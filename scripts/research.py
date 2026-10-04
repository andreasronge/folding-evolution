"""Autonomous research loop driver.

Design: Plans/research-tree.md. Agent-facing conventions: research/README.md.

One experiment cycle runs through fixed phases:

    propose → (owner approves) → prepare → review_code → execute → analyse → decide
    steward                      researcher  reviewer    run_queue  reviewer   steward

`decide` also writes the next proposal and the morning brief, so the loop
always ends waiting for the owner's approval. The driver holds budgets,
timeouts and phase order; agents hold judgment. All state is in files
(research/state.json plus the task folder), so any command can be re-run
after a crash and resumes where it stopped.

Usage:
    uv run python scripts/research.py status
    uv run python scripts/research.py propose          # steward proposes now
    uv run python scripts/research.py approve [--note "..."]
    uv run python scripts/research.py reject "reason"
    uv run python scripts/research.py run              # waits for the night window
    uv run python scripts/research.py run --now        # daytime run, starts at once

Nightly: `caffeinate -s uv run python scripts/research.py run` in the
evening (or from cron/launchd). With nothing approved it only writes a
proposal for the morning.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path
from typing import Any, Callable

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from queue_lib import LockError, acquire_lock, load_queue, release_lock  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
RESEARCH = REPO / "research"
STATE_PATH = RESEARCH / "state.json"
POLL_SECONDS = 5
KILL_GRACE_SECONDS = 10
# The queue runner needs longer: it gives its entries 10 s, then SIGKILLs them.
QUEUE_KILL_GRACE_SECONDS = 45
QUEUE_LOCKED_EXIT = 3  # run_queue.py: another runner holds the lock

IDLE = "idle"
AWAITING = "awaiting_approval"
ACCEPT = "accept"  # next proposal written by `decide`, not yet validated
PHASE_ORDER = ["propose", ACCEPT, AWAITING, "prepare", "review_code", "execute", "analyse",
               "decide"]


class Stop(Exception):
    """Stop the loop for now; state is saved and the next run resumes."""


# --------------------------------------------------------------------------
# Files


def load_config(research: Path) -> dict[str, Any]:
    with (research / "config.toml").open("rb") as f:
        return tomllib.load(f)


def read_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def load_state(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text())
    return {"phase": IDLE, "task": None}


def save_state(path: Path, state: dict[str, Any]) -> None:
    atomic_write(path, json.dumps(state, indent=2, sort_keys=True) + "\n")


def load_role(research: Path, role: str) -> dict[str, Any]:
    meta, _ = read_frontmatter(research / "roles" / f"{role}.md")
    for key in ("agent", "model"):
        if key not in meta:
            raise SystemExit(f"roles/{role}.md: frontmatter needs '{key}'")
    return meta


def agent_argv(research: Path, role_meta: dict[str, Any], prompt: str) -> list[str]:
    with (research / "agents.toml").open("rb") as f:
        agents = tomllib.load(f)
    kind = role_meta["agent"]
    if kind not in agents:
        raise SystemExit(f"agents.toml has no [{kind}] entry")
    values = {
        "prompt": prompt,
        "model": str(role_meta["model"]),
        "effort": str(role_meta.get("effort", "high")),
        "research_dir": str(research),
    }
    return [part.format(**values) for part in agents[kind]["cmd"]]


# --------------------------------------------------------------------------
# Budgets


def question_nodes(research: Path, node: Path) -> list[Path]:
    """`node` and its ancestors that are question folders, innermost first."""
    questions = (research / "questions").resolve()
    out, cur = [], node.resolve()
    while cur != questions and questions in cur.parents:
        if (cur / "question.md").exists():
            out.append(cur)
        cur = cur.parent
    return out


def _budget(path: Path) -> dict[str, int]:
    meta, _ = read_frontmatter(path)
    return meta.get("budget") or {}


def executed_nodes(research: Path) -> list[Path]:
    """Question folder of every experiment the loop has started running.
    A run counts once `execution.md` exists in its task folder, so charging
    is idempotent: resuming a run never charges it again."""
    out = []
    for td in (research / "runs").glob("*/"):
        if (td / "execution.md").exists() and (td / "proposal.md").exists():
            node = str(read_frontmatter(td / "proposal.md")[0].get("node", "")).strip("/")
            if node:
                out.append((research / node).resolve())
    return out


def remaining_budget(research: Path, node: Path) -> int | None:
    """Experiments still allowed at `node`: the minimum over every ancestor of
    (its budget − experiments used anywhere in its subtree). Used = runs the
    loop executed there + any `used` recorded by hand. None = unlimited."""
    remaining, runs = None, executed_nodes(research)
    for q in question_nodes(research, node):
        b = _budget(q / "question.md")
        if "experiments" not in b:
            continue
        used = sum(_budget(p).get("used", 0) for p in q.rglob("question.md"))
        used += sum(1 for r in runs if r == q or q in r.parents)
        left = int(b["experiments"]) - used
        remaining = left if remaining is None else min(remaining, left)
    return remaining


# --------------------------------------------------------------------------
# Launching processes (agents, worktree setup, the queue)


def _write_script(log_dir: Path, label: str, argv: list[str] | str, cwd: Path,
                  env: dict[str, str]) -> Path:
    cmd = argv if isinstance(argv, str) else shlex.join(argv)
    exports = "".join(f"export {k}={shlex.quote(v)}\n" for k, v in env.items())
    script = log_dir / f"{label}.sh"
    script.write_text(
        "#!/bin/bash\n"
        f"cd {shlex.quote(str(cwd))} || exit 97\n"
        f"echo $$ > {shlex.quote(str(log_dir / (label + '.pid')))}\n"
        f"{exports}"
        f"{{ {cmd}\n}} 2>&1 | tee {shlex.quote(str(log_dir / (label + '.log')))}\n"
        f"echo ${{PIPESTATUS[0]}} > {shlex.quote(str(log_dir / (label + '.exit')))}\n"
    )
    return script


def _group_alive(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except (ProcessLookupError, PermissionError):  # EPERM: only zombies left
        return False


def _kill_group(pid_file: Path, grace: float | None = None) -> None:
    """SIGTERM the process group, wait up to `grace` for it to exit, then SIGKILL."""
    try:
        pid = int(pid_file.read_text().strip())
    except (OSError, ValueError):
        return
    try:
        os.killpg(pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return
    end = time.monotonic() + (KILL_GRACE_SECONDS if grace is None else grace)
    while time.monotonic() < end and _group_alive(pid):
        time.sleep(0.2)
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def stop_launch(log_dir: Path, label: str, grace: float | None = None) -> None:
    """Stop whatever a launch left running: its process group and its herdr tab.
    A launch that wrote its exit code is finished and is not signalled (its
    PID may have been reused since)."""
    if not (log_dir / f"{label}.exit").exists():
        _kill_group(log_dir / f"{label}.pid", grace)
    tab_file = log_dir / f"{label}.tab"
    if tab_file.exists():
        subprocess.run(["herdr", "tab", "close", tab_file.read_text().strip()],
                       capture_output=True, timeout=30)
        tab_file.unlink(missing_ok=True)


def _wait_exit(exit_file: Path, timeout_s: float, alive: Callable[[], bool]) -> int | None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if exit_file.exists() and exit_file.read_text().strip():
            return int(exit_file.read_text().strip())
        if not alive():
            # Process gone without writing an exit code: killed or crashed.
            time.sleep(1)
            return int(exit_file.read_text().strip()) if exit_file.exists() else None
        time.sleep(POLL_SECONDS)
    return None


class LocalLauncher:
    name = "local"

    def run(self, label: str, argv: list[str] | str, cwd: Path, log_dir: Path,
            timeout_s: float, env: dict[str, str] | None = None,
            kill_grace: float | None = None) -> int | None:
        """Run to completion; return exit code, or None on timeout/kill."""
        log_dir.mkdir(parents=True, exist_ok=True)
        for suffix in (".exit", ".pid", ".tab"):
            (log_dir / f"{label}{suffix}").unlink(missing_ok=True)
        script = _write_script(log_dir, label, argv, cwd, env or {})
        proc = subprocess.Popen(["bash", str(script)], start_new_session=True,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # The script writes the same PID; writing it here too closes the gap
        # before the script starts.
        (log_dir / f"{label}.pid").write_text(f"{proc.pid}\n")
        try:
            code = _wait_exit(log_dir / f"{label}.exit", timeout_s, lambda: proc.poll() is None)
        except BaseException:  # driver interrupted: never leave the agent running
            stop_launch(log_dir, label, kill_grace)
            raise
        if code is None:
            stop_launch(log_dir, label, kill_grace)
            proc.wait()
        return code


class HerdrLauncher:
    """Runs each command in its own herdr tab so the owner can watch or attach.
    Completion is read from the exit file the script writes, never from the
    terminal or herdr's agent-state detection."""

    name = "herdr"

    def __init__(self, workspace_label: str) -> None:
        self.workspace = self._workspace(workspace_label)

    @staticmethod
    def _herdr(*args: str) -> dict[str, Any]:
        out = subprocess.run(["herdr", *args], capture_output=True, text=True, timeout=30)
        if out.returncode != 0:
            raise RuntimeError(f"herdr {' '.join(args)}: {out.stderr.strip() or out.stdout.strip()}")
        return json.loads(out.stdout).get("result", {}) if out.stdout.strip() else {}

    def _workspace(self, label: str) -> str:
        for ws in self._herdr("workspace", "list").get("workspaces", []):
            if ws.get("label") == label:
                return ws["workspace_id"]
        created = self._herdr("workspace", "create", "--label", label, "--cwd", str(REPO),
                              "--no-focus")
        found = _find_key(created, "workspace_id")
        if not found:
            raise RuntimeError(f"herdr workspace create returned no id: {created}")
        return found

    def run(self, label: str, argv: list[str] | str, cwd: Path, log_dir: Path,
            timeout_s: float, env: dict[str, str] | None = None,
            kill_grace: float | None = None) -> int | None:
        log_dir.mkdir(parents=True, exist_ok=True)
        for suffix in (".exit", ".pid", ".tab"):
            (log_dir / f"{label}{suffix}").unlink(missing_ok=True)
        script = _write_script(log_dir, label, argv, cwd, env or {})
        tab = self._herdr("tab", "create", "--workspace", self.workspace, "--label",
                          f"{log_dir.parent.name}:{label}", "--cwd", str(cwd), "--no-focus")
        tab_id, pane_id = tab["tab"]["tab_id"], tab["root_pane"]["pane_id"]
        # Recorded first, so an interrupted start can still be cleaned up.
        (log_dir / f"{label}.tab").write_text(tab_id + "\n")
        try:
            self._herdr("pane", "run", pane_id, f"bash {shlex.quote(str(script))}")
        except BaseException:
            stop_launch(log_dir, label, kill_grace)
            raise
        pid_file = log_dir / f"{label}.pid"

        def alive() -> bool:
            if not pid_file.exists():
                return True  # not started yet
            try:
                os.kill(int(pid_file.read_text().strip()), 0)
                return True
            except (ProcessLookupError, ValueError):
                return False
            except PermissionError:
                return True

        try:
            code = _wait_exit(log_dir / f"{label}.exit", timeout_s, alive)
        except BaseException:  # driver interrupted: never leave the agent running
            stop_launch(log_dir, label, kill_grace)
            raise
        if code == 0 or code is None:
            stop_launch(log_dir, label, kill_grace)  # just closes the tab if it finished
        else:
            # Keep failed tabs open for inspection; the log is saved either way.
            (log_dir / f"{label}.tab").unlink(missing_ok=True)
        return code


def _find_key(obj: Any, key: str) -> str | None:
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        obj = list(obj.values())
    if isinstance(obj, list):
        for v in obj:
            if (found := _find_key(v, key)) is not None:
                return found
    return None


def make_launcher(cfg: dict[str, Any]) -> LocalLauncher | HerdrLauncher:
    if cfg.get("launcher", "herdr") == "herdr":
        try:
            return HerdrLauncher(cfg.get("herdr_workspace", "research"))
        except (RuntimeError, OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            print(f"[research] herdr unavailable ({e}); running agents locally", file=sys.stderr)
    return LocalLauncher()


# --------------------------------------------------------------------------
# Git


def git(*args: str, cwd: Path) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout.strip()


def git_ok(*args: str, cwd: Path) -> bool:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True).returncode == 0


# --------------------------------------------------------------------------
# Prompts. Role guidance lives in research/roles/*.md; these lines only say
# what this phase must produce.

COMMON = (
    "You are the {role} in this repository's autonomous research loop. First read "
    "{research}/README.md and {research}/roles/{role}.md. Your task folder is {task_dir}. "
)

PROMPTS = {
    "propose": (
        "Choose the next experiment. Read {research}/digest.md and explore {research}/questions "
        "(statuses, budgets, logs, parked questions' reopen conditions). {feedback}"
        "You may create a new question folder if the right question does not exist yet. "
        "Write {task_dir}/proposal.md in the proposal format from the README. Do not write code."
    ),
    "prepare": (
        "Implement the approved proposal {task_dir}/proposal.md. Also read, if present, "
        "approval.md (owner notes), code_review.md (review to address) and driver_feedback.md "
        "(failed checks to fix) in the task folder. The current directory is your git worktree on "
        "branch {branch}. 1) Before running anything, write {task_dir}/plan.md: conditions, seeds, "
        "measurements, and what each outcome would mean for the competing explanations. "
        "2) Implement and smoke-test at small scale. 3) Write {task_dir}/queue.yaml in "
        "scripts/run_queue.py format for the full run: commands run with this worktree as cwd, "
        "write outputs under $RUN_DIR, and every entry id starts with '{task}-'. "
        "4) Commit all changes on {branch} so `git status` is clean."
    ),
    "review_code": (
        "Review the code written for this experiment: run `git diff {base}..{commit}` in the "
        "current directory (the experiment's worktree). Read {task_dir}/proposal.md, plan.md and "
        "queue.yaml. Write {task_dir}/code_review.md starting with frontmatter `verdict: pass` or "
        "`verdict: fail`, then numbered blocking issues and brief minor notes."
    ),
    "analyse": (
        "Analyse the results. Inputs: {task_dir}/proposal.md, queue.yaml, execution.md (run status "
        "and output folders) and the code in the current directory. Do not open plan.md until your "
        "analysis is written. Write {task_dir}/analysis.md: data completeness first, then the key "
        "numbers with denominators, plots if they help (save them in the task folder), and what "
        "the data does and does not show. Then read plan.md and append '## Against the predictions'."
    ),
    "decide": (
        "This experiment cycle is over.{blocked} Read the task folder (proposal, plan, code review, "
        "execution, analysis — whichever exist). 1) Update the question at {research}/{node}: append "
        "to log.md (experiment → result → `Decision: … because …`), update question.md (status, "
        "summary, Related, Reopen if), and update {research}/digest.md if beliefs changed. Re-check "
        "parked questions whose reopen condition may now be met. 2) Write {task_dir}/decision.md: "
        "continue, park, close or new question, and why. 3) Write the next proposal to "
        "{next_dir}/proposal.md (README format). 4) Write the owner's brief to {brief}, under one "
        "page: what was tested and why · what happened (key numbers) · what we learned (1–3 "
        "sentences) · how the tree changed · the next proposal and why · failures and uncertainty."
    ),
}


# --------------------------------------------------------------------------
# The loop


class Driver:
    def __init__(self, research: Path = RESEARCH, repo: Path = REPO,
                 launcher: Any = None, now: Callable[[], dt.datetime] = dt.datetime.now):
        self.research, self.repo, self.now = research, repo, now
        self.cfg = load_config(research)
        self.state_path = research / "state.json"
        self.state = load_state(self.state_path)
        self._launcher = launcher
        self.deadline: dt.datetime | None = None

    # -- helpers --------------------------------------------------------
    @property
    def launcher(self) -> Any:
        if self._launcher is None:
            self._launcher = make_launcher(self.cfg)
        return self._launcher

    def save(self) -> None:
        save_state(self.state_path, self.state)

    def task_dir(self, task: str | None = None) -> Path:
        return self.research / "runs" / (task or self.state["task"])

    def log(self, msg: str) -> None:
        line = f"{self.now():%Y-%m-%d %H:%M:%S} {msg}"
        print(f"[research] {msg}")
        if self.state.get("task"):
            with (self.task_dir() / "driver.log").open("a") as f:
                f.write(line + "\n")

    def new_task_id(self) -> str:
        base = f"{self.now():%Y-%m-%d-%H%M}"
        task, n = base, 2
        while (self.research / "runs" / task).exists():
            task, n = f"{base}-{n}", n + 1
        return task

    def set_phase(self, phase: str) -> None:
        self.state["phase"] = phase
        self.save()
        self.log(f"phase → {phase}")

    def node_path(self) -> Path:
        return self.research / self.state["node"]

    def worktree(self) -> Path:
        return Path(self.state["worktree"])

    def check_deadline(self) -> None:
        if self.deadline and self.now() >= self.deadline:
            raise Stop(f"past the run deadline ({self.deadline:%H:%M}); resume next run")

    def launch(self, label: str, argv: list[str] | str, cwd: Path, timeout_s: float,
               env: dict[str, str] | None = None, kill_grace: float | None = None) -> int | None:
        """Run via the launcher, recording what runs so a crashed driver's
        leftover process is found and stopped on the next start. The record
        is cleared only after a normal return (the launcher stopped it)."""
        log_dir = self.task_dir() / "logs"
        self.state["launch"] = {"label": label, "log_dir": str(log_dir), "grace": kill_grace}
        self.save()
        code = self.launcher.run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)
        self.state.pop("launch", None)
        self.save()
        return code

    def reconcile(self) -> None:
        """Finish what a crashed driver left half-done before doing anything new."""
        if launch := self.state.get("launch"):
            self.log(f"stopping leftover process from an interrupted run: {launch['label']}")
            stop_launch(Path(launch["log_dir"]), launch["label"], launch.get("grace"))
            self.state.pop("launch")
            self.save()
        if cleanup := self.state.get("cleanup"):
            self.run_cleanup(cleanup)

    def call_agent(self, role: str, phase: str, cwd: Path, **fmt: str) -> None:
        """Launch the role's agent for `phase`; raise Stop if past the deadline,
        over the call cap, or the agent did not finish cleanly."""
        if phase != "decide":
            self.check_deadline()
        calls = self.state.get("agent_calls", 0)
        if calls >= self.cfg.get("max_agent_calls", 8) and phase != "decide":
            if phase == "propose" or "node" not in self.state:
                raise Stop(f"agent call cap ({calls}) reached while proposing; "
                           "`research.py propose` starts over")
            self.block(f"agent call cap ({calls}) reached")
            raise _Blocked()
        self.state["agent_calls"] = calls + 1
        self.save()
        meta = load_role(self.research, role)
        values = {"role": role, "research": str(self.research), "task_dir": str(self.task_dir()),
                  "task": self.state["task"], **fmt}
        prompt = (COMMON + PROMPTS[phase]).format(**values)
        argv = agent_argv(self.research, meta, prompt)
        timeout = float(meta.get("timeout_min", 60)) * 60
        label = f"{phase}-{self.state['agent_calls']}"
        self.log(f"{role} ({meta['agent']}/{meta['model']}) → {phase} [{self.launcher.name}]")
        code = self.launch(label, argv, cwd, timeout)
        if code != 0:
            raise Stop(f"{role} agent for {phase} {'timed out' if code is None else f'exited {code}'}"
                       f"; see {self.task_dir() / 'logs' / (label + '.log')}")

    def block(self, reason: str) -> None:
        """Abandon the experiment; the steward records why in `decide`."""
        self.state["blocked"] = reason
        self.log(f"blocked: {reason}")
        self.set_phase("decide")

    def expect(self, name: str) -> Path:
        path = self.task_dir() / name
        if not path.exists():
            raise Stop(f"agent finished but did not write {path}")
        return path

    # -- phases ---------------------------------------------------------
    def phase_propose(self) -> None:
        feedback = ""
        if rejected := self.state.get("rejected"):
            feedback = (f"The owner set aside the previous proposal ({rejected}); read it and any "
                        "rejected.md beside it, and propose something that answers the objection. ")
        self.call_agent("steward", "propose", self.repo, feedback=feedback)
        self.accept_proposal()

    def accept_proposal(self) -> None:
        meta, _ = read_frontmatter(self.expect("proposal.md"))
        node = str(meta.get("node", "")).strip().strip("/")
        if not node.startswith("questions/") or not (self.research / node / "question.md").exists():
            raise Stop(f"proposal.md node {node!r} is not a question folder under research/questions")
        self.state["node"] = node
        self.state.pop("rejected", None)
        self.set_phase(AWAITING)
        left = remaining_budget(self.research, self.research / node)
        self.log(f"proposal: {meta.get('title', '?')} [{node}] — budget left: "
                 f"{'unlimited' if left is None else left}. Approve with `research.py approve`.")

    def phase_prepare(self) -> None:
        if not self.state.get("worktree_ready"):
            self.create_worktree()
        wt = self.worktree()
        self.call_agent("researcher", "prepare", wt, branch=self.state["branch"])
        # Rebuild from the final source, so the extension matches the reviewed commit.
        self.run_setup(wt, "build")
        problems = self.check_prepared(wt)
        if problems:
            self.repair("driver_feedback.md", "Preparation checks failed:\n\n" +
                        "\n".join(f"- {p}" for p in problems))
            return
        (self.task_dir() / "driver_feedback.md").unlink(missing_ok=True)
        self.state["commit"] = git("rev-parse", "HEAD", cwd=wt)
        self.state["queue_sha"] = file_sha(self.task_dir() / "queue.yaml")
        self.set_phase("review_code")

    def create_worktree(self) -> None:
        task, rb = self.state["task"], self.cfg["research_branch"]
        base = self.cfg["base_branch"]
        if not git_ok("rev-parse", "--verify", rb, cwd=self.repo):
            git("branch", rb, base, cwd=self.repo)
        wt = (self.repo / self.cfg["worktree_root"] / task).resolve()
        branch = f"research/{task}"
        # Idempotent: a crash may have left the branch or worktree behind.
        if not wt.exists():
            git_ok("worktree", "prune", cwd=self.repo)
            if git_ok("rev-parse", "--verify", branch, cwd=self.repo):
                git("worktree", "add", str(wt), branch, cwd=self.repo)
            else:
                git("worktree", "add", "-b", branch, str(wt), rb, cwd=self.repo)
        if "base" not in self.state:
            self.state["base"] = git("rev-parse", "HEAD", cwd=wt)
        self.state.update(worktree=str(wt), branch=branch)
        self.save()
        # Pick up the owner's latest work on the base branch.
        if not git_ok("merge-base", "--is-ancestor", base, "HEAD", cwd=wt):
            if not git_ok("merge", "--no-edit", base, cwd=wt):
                git_ok("merge", "--abort", cwd=wt)
                self.block(f"merging {base} into {rb} conflicts; resolve by hand")
                raise _Blocked()
            self.state["base"] = git("rev-parse", "HEAD", cwd=wt)
            self.save()
        self.run_setup(wt, "setup")
        self.state["worktree_ready"] = True
        self.save()

    def run_setup(self, wt: Path, label: str) -> None:
        env = {k: str(self.repo / v) for k, v in self.cfg.get("setup_env", {}).items()}
        for i, cmd in enumerate(self.cfg.get("worktree_setup", [])):
            code = self.launch(f"{label}-{i}", cmd, wt, 3600, env)
            if code != 0:
                raise Stop(f"worktree {label} failed: {cmd} (exit {code})")

    def check_prepared(self, wt: Path) -> list[str]:
        problems = []
        if git("status", "--porcelain", cwd=wt):
            problems.append("worktree has uncommitted changes; commit everything")
        for name in ("plan.md", "queue.yaml"):
            if not (self.task_dir() / name).exists():
                problems.append(f"{name} missing from the task folder")
        queue = self.task_dir() / "queue.yaml"
        if queue.exists():
            try:
                entries = load_queue(queue)
                if not entries:
                    problems.append("queue.yaml has no entries")
                for e in entries:
                    if not e.id.startswith(f"{self.state['task']}-"):
                        problems.append(f"queue id {e.id!r} must start with '{self.state['task']}-'")
            except Exception as e:  # noqa: BLE001 - any parse error is feedback
                problems.append(f"queue.yaml does not load: {e}")
        for module in self.cfg.get("import_check", []):
            out = subprocess.run(
                ["uv", "run", "python", "-c", f"import {module}; print({module}.__file__)"],
                cwd=wt, capture_output=True, text=True)
            where = out.stdout.strip()
            if out.returncode != 0:
                problems.append(f"`import {module}` fails in the worktree: "
                                f"{out.stderr.strip().splitlines()[-1:]}")
            elif not Path(where).resolve().is_relative_to(wt.resolve()):
                problems.append(f"{module} loads from {where}, not from this worktree")
        return problems

    def repair(self, feedback_name: str, feedback: str | None = None) -> None:
        if feedback is not None:
            atomic_write(self.task_dir() / feedback_name, feedback + "\n")
        repairs = self.state.get("repairs", 0)
        if repairs >= self.cfg.get("max_repairs", 1):
            self.block(f"still failing after {repairs} repair(s); see {feedback_name}")
            return
        self.state["repairs"] = repairs + 1
        self.set_phase("prepare")

    def phase_review_code(self) -> None:
        wt = self.worktree()
        if not git("diff", "--stat", f"{self.state['base']}..{self.state['commit']}", cwd=wt):
            self.log("no code changes; skipping code review")
            self.set_phase("execute")
            return
        self.call_agent("reviewer", "review_code", wt, base=self.state["base"],
                        commit=self.state["commit"])
        meta, _ = read_frontmatter(self.expect("code_review.md"))
        verdict = str(meta.get("verdict", "")).lower()
        if verdict == "pass":
            self.set_phase("execute")
        elif verdict == "fail":
            self.repair("code_review.md")
        else:
            raise Stop("code_review.md has no 'verdict: pass|fail' frontmatter")

    def phase_execute(self) -> None:
        self.check_deadline()  # never start a long queue after the night ends
        wt, td = self.worktree(), self.task_dir()
        if git("rev-parse", "HEAD", cwd=wt) != self.state["commit"] or git(
                "status", "--porcelain", cwd=wt):
            raise Stop("worktree changed after review (HEAD moved or uncommitted edits); "
                       "refusing to run unreviewed code")
        queue = td / "queue.yaml"
        if file_sha(queue) != self.state.get("queue_sha"):
            raise Stop("queue.yaml changed after review; refusing to run an unreviewed queue")
        entries = load_queue(queue)
        status_path = td / "queue.status.json"
        if not (td / "execution.md").exists():  # a new campaign, not a resumed one
            left = remaining_budget(self.research, self.node_path())
            if left is not None and left <= 0:
                self.block(f"no experiment budget left at {self.state['node']} or an ancestor "
                           "(owner raises `experiments` in question.md)")
                return
            # Writing execution.md charges the budget (see executed_nodes).
            atomic_write(td / "execution.md", "# Execution\n\nStarted; results pending.\n")
        timeout = sum(e.timeout_seconds for e in entries) + 900
        argv = ["uv", "run", "python", "scripts/run_queue.py", "--queue", str(queue),
                "--status", str(status_path), "--lock", str(self.repo / "queue.lock"),
                "--output-root", str(self.repo / "experiments" / "output")]
        self.log(f"running queue ({len(entries)} entries)")
        code = self.launch("queue", argv, wt, timeout, kill_grace=QUEUE_KILL_GRACE_SECONDS)
        if code == QUEUE_LOCKED_EXIT:
            raise Stop("another queue runner holds queue.lock; resume when it is done")
        if code is None:
            raise Stop("queue runner timed out or was killed; resume continues unfinished entries")
        status = json.loads(status_path.read_text()) if status_path.exists() else {}
        rows = [f"| {e.id} | {status.get(e.id, {}).get('status', 'not run')} | "
                f"{status.get(e.id, {}).get('wall_seconds', '')} | "
                f"{status.get(e.id, {}).get('run_dir', '')} |" for e in entries]
        atomic_write(td / "execution.md", (
            f"# Execution\n\nCode: commit `{self.state['commit']}` on `{self.state['branch']}`. "
            f"Queue runner exit: {code}.\n\n| id | status | wall s | output (repo-relative) |\n"
            "|---|---|---|---|\n" + "\n".join(rows) + "\n"))
        # Later experiments build on this code.
        git("branch", "-f", self.cfg["research_branch"], self.state["commit"], cwd=self.repo)
        self.set_phase("analyse")

    def phase_analyse(self) -> None:
        self.call_agent("reviewer", "analyse", self.worktree())
        self.expect("analysis.md")
        self.set_phase("decide")

    def phase_decide(self) -> None:
        nxt = self.state.get("next_task") or self.new_task_id()
        self.state["next_task"] = nxt
        self.save()
        (self.research / "runs" / nxt).mkdir(parents=True, exist_ok=True)
        brief = self.research / "briefs" / f"{self.now():%Y-%m-%d}-{self.state['task']}.md"
        blocked = (f" It was stopped before completion: {self.state['blocked']}."
                   if self.state.get("blocked") else "")
        cwd = Path(self.state["worktree"]) if self.state.get("worktree") else self.repo
        self.call_agent("steward", "decide", cwd, node=self.state["node"],
                        next_dir=str(self.research / "runs" / nxt), brief=str(brief),
                        blocked=blocked)
        self.expect("decision.md")
        if not brief.exists():
            raise Stop(f"steward did not write the brief {brief}")
        # Hand over to the next proposal (written by the steward above) before
        # cleaning up, so a crash here never loses the finished cycle.
        cleanup = {"task": self.state["task"], "worktree": self.state.get("worktree"),
                   "brief": str(brief)}
        self.state = {"phase": ACCEPT, "task": nxt, "cleanup": cleanup}
        self.save()
        self.run_cleanup(cleanup)
        self.accept_proposal()

    def run_cleanup(self, cleanup: dict[str, Any]) -> None:
        wt = cleanup.get("worktree")
        if wt and Path(wt).exists() and not git("status", "--porcelain", cwd=Path(wt)):
            git_ok("worktree", "remove", wt, cwd=self.repo)
        if self.cfg.get("commit_research"):
            git_ok("add", "research", cwd=self.repo)
            git_ok("commit", "-m", f"Research: {cleanup['task']}", "--", "research",
                   cwd=self.repo)
        self.state.pop("cleanup", None)
        self.save()
        self.log(f"cycle {cleanup['task']} done; brief: {cleanup['brief']}")

    # -- control --------------------------------------------------------
    def advance(self) -> None:
        """Run phases until the loop needs the owner, a deadline, or a fix."""
        self.reconcile()
        handlers = {"propose": self.phase_propose, ACCEPT: self.accept_proposal,
                    "prepare": self.phase_prepare,
                    "review_code": self.phase_review_code, "execute": self.phase_execute,
                    "analyse": self.phase_analyse, "decide": self.phase_decide}
        while True:
            phase = self.state["phase"]
            if phase == IDLE:
                self.state = {"phase": "propose", "task": self.new_task_id()}
                self.task_dir().mkdir(parents=True, exist_ok=True)
                self.save()
                continue
            if phase == AWAITING:
                return
            try:
                handlers[phase]()
            except _Blocked:
                continue

    def run(self, now_mode: bool) -> int:
        if not now_mode:
            self.wait_for_night()
            # The owner may have approved or rejected while we waited.
            self.state = load_state(self.state_path)
        start = self.now()
        self.deadline = (start + dt.timedelta(hours=self.cfg.get("day_max_hours", 8))
                         if now_mode else self.night_end_after(start))
        if self.state["phase"] == AWAITING:
            print(f"[research] proposal {self.task_dir() / 'proposal.md'} awaits approval; nothing to run")
            return 0
        return self._advance_reporting()

    def _advance_reporting(self) -> int:
        try:
            self.advance()
        except Stop as e:
            self.log(f"stopped in {self.state['phase']}: {e}")
            return 1
        return 0

    def _clock(self, key: str) -> dt.time:
        return dt.time.fromisoformat(self.cfg.get(key, {"night_start": "22:00",
                                                       "night_end": "07:00"}[key]))

    def in_night(self, t: dt.datetime) -> bool:
        s, e = self._clock("night_start"), self._clock("night_end")
        return (s <= t.time() or t.time() < e) if s > e else (s <= t.time() < e)

    def night_end_after(self, t: dt.datetime) -> dt.datetime:
        end = dt.datetime.combine(t.date(), self._clock("night_end"))
        return end if end > t else end + dt.timedelta(days=1)

    def wait_for_night(self) -> None:
        if self.in_night(self.now()):
            return
        start = dt.datetime.combine(self.now().date(), self._clock("night_start"))
        if start <= self.now():
            start += dt.timedelta(days=1)
        print(f"[research] waiting for the night window (starts {start:%H:%M}); use --now to run now")
        while self.now() < start:
            time.sleep(min(60, max(1, (start - self.now()).total_seconds())))
            self.cfg = load_config(self.research)

    def approve(self, note: str | None) -> int:
        if self.state["phase"] != AWAITING:
            print(f"[research] nothing awaiting approval (phase: {self.state['phase']})")
            return 1
        if note:
            atomic_write(self.task_dir() / "approval.md", note + "\n")
        self.state.update(approved=True, approved_at=self.now().isoformat())
        self.set_phase("prepare")
        print("[research] approved; it runs tonight, or now with `research.py run --now`")
        return 0

    def reject(self, reason: str) -> int:
        if self.state["phase"] != AWAITING:
            print(f"[research] nothing awaiting approval (phase: {self.state['phase']})")
            return 1
        atomic_write(self.task_dir() / "rejected.md", reason + "\n")
        old = self.task_dir() / "proposal.md"
        self.state = {"phase": "propose", "task": self.new_task_id(), "rejected": str(old)}
        self.task_dir().mkdir(parents=True, exist_ok=True)
        self.save()
        print("[research] rejected; run `research.py propose` for a new proposal")
        return 0

    def propose(self) -> int:
        if self.state["phase"] not in (IDLE, AWAITING, "propose", ACCEPT):
            print(f"[research] an experiment is in progress (phase {self.state['phase']}); "
                  "finish it with `run` first")
            return 1
        if self.state["phase"] == AWAITING:
            self.state = {"phase": "propose", "task": self.new_task_id(),
                          "rejected": str(self.task_dir() / "proposal.md")}
            self.task_dir().mkdir(parents=True, exist_ok=True)
            self.save()
        self.deadline = None
        try:
            self.reconcile()
            if self.state["phase"] == IDLE:
                self.state = {"phase": "propose", "task": self.new_task_id()}
                self.task_dir().mkdir(parents=True, exist_ok=True)
            self.state["phase"] = "propose"
            self.state["agent_calls"] = 0  # the owner asked: a fresh call budget
            self.save()
            self.phase_propose()
        except Stop as e:
            self.log(f"stopped in propose: {e}")
            return 1
        return 0

    def status(self) -> int:
        s = self.state
        print(f"phase: {s['phase']}   task: {s.get('task')}   node: {s.get('node', '-')}")
        if s.get("blocked"):
            print(f"blocked: {s['blocked']}")
        if s.get("task") and (self.task_dir() / "proposal.md").exists():
            meta, _ = read_frontmatter(self.task_dir() / "proposal.md")
            print(f"proposal: {meta.get('title', '?')}  ({self.task_dir() / 'proposal.md'})")
        print("\nquestions:")
        for q in sorted((self.research / "questions").rglob("question.md")):
            meta, body = read_frontmatter(q)
            title = next((ln[2:] for ln in body.splitlines() if ln.startswith("# ")), "")
            depth = len(q.relative_to(self.research / "questions").parts) - 2
            left = remaining_budget(self.research, q.parent)
            print(f"  {'  ' * depth}{q.parent.name:<34} {meta.get('status', '?'):<7} "
                  f"left={'∞' if left is None else left:<3} {title[:70]}")
        briefs = sorted((self.research / "briefs").glob("*.md"))
        if briefs:
            print(f"\nlatest brief: {briefs[-1]}")
        return 0


class _Blocked(Exception):
    """Internal: the phase was redirected to `decide`; continue the loop."""


def locked(research: Path, fn: Callable[[], int]) -> int:
    """One driver command at a time (a waiting nightly run holds no lock)."""
    lock = research / "driver.lock"
    try:
        acquire_lock(lock)
    except LockError:
        print("[research] another research.py command is running; try again later",
              file=sys.stderr)
        return 3
    try:
        return fn()
    finally:
        release_lock(lock)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Autonomous research loop (Plans/research-tree.md)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="show the current phase, proposal and question tree")
    sub.add_parser("propose", help="ask the steward for a proposal now")
    p_approve = sub.add_parser("approve", help="approve the pending proposal")
    p_approve.add_argument("--note", help="notes for the researcher (saved as approval.md)")
    p_reject = sub.add_parser("reject", help="reject the pending proposal")
    p_reject.add_argument("reason")
    p_run = sub.add_parser("run", help="run the approved experiment (waits for night by default)")
    p_run.add_argument("--now", action="store_true", help="daytime run: start immediately")
    args = ap.parse_args(argv)

    # SIGTERM (e.g. from launchd) unwinds like Ctrl-C so running agents are stopped.
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    driver = Driver()
    if args.cmd == "status":
        return driver.status()
    if args.cmd == "run" and not args.now:
        driver.wait_for_night()
    actions = {
        "propose": driver.propose,
        "approve": lambda: driver.approve(args.note),
        "reject": lambda: driver.reject(args.reason),
        "run": lambda: driver.run(now_mode=args.now),
    }

    def fresh() -> int:  # re-read state under the lock
        driver.state = load_state(driver.state_path)
        return actions[args.cmd]()

    return locked(driver.research, fresh)


if __name__ == "__main__":
    sys.exit(main())
