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
    uv run python scripts/research.py run --auto --hours 48   # no approvals (research-auto.md)
                                                    # up to auto_max_experiments experiments

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
# Entry outcomes that are results (failures included) rather than "not done yet".
FINISHED_ENTRY_STATUSES = {"done", "failed", "timeout", "suspicious"}

IDLE = "idle"
AWAITING = "awaiting_approval"
ACCEPT = "accept"  # next proposal written by `decide`, not yet validated
PHASE_ORDER = ["propose", ACCEPT, AWAITING, "prepare", "review_code", "execute", "analyse",
               "decide"]


class Stop(Exception):
    """Stop the loop for now; state is saved and the next run resumes."""


class OwnerNeeded(Stop):
    """Autonomous mode cannot continue without the owner (not retried)."""


class AgentFailed(Stop):
    """An agent exited badly, timed out or wrote nothing: worth a retry."""


class RunComplete(Stop):
    """The autonomous run used all the experiments it was allowed (a normal end)."""


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


def git_ok(*args: str, cwd: Path, timeout: float = 600) -> bool:
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                              timeout=timeout).returncode == 0
    except subprocess.TimeoutExpired:
        return False


# --------------------------------------------------------------------------
# Prompts. Role guidance lives in research/roles/*.md; these lines only say
# what this phase must produce.

COMMON = (
    "You are the {role} in this repository's autonomous research loop. First read "
    "{research}/README.md and {research}/roles/{role}.md. Your task folder is {task_dir}. "
)

PROMPTS = {
    "propose": (
        "Choose the next experiment. Read {research}/digest.md (current beliefs), then the root "
        "question you work in and the folders it links; open other logs only for a named "
        "uncertainty. {strategy}{feedback}{banks}"
        "You may create a new sub-question folder if the right question does not exist yet. "
        "Write {task_dir}/proposal.md in the proposal format from the README (at most 800 words), "
        "with its feasibility numbers and the closest known technique; when the mechanism is new "
        "to this tree, search the literature first and cite only papers you found, with links. "
        "Do not write experiment code; short read-only probes with existing code (≤ 10 min) are "
        "fine."
    ),
    "critique": (
        "Give a second opinion on the steward's proposal {task_dir}/proposal.md before it is "
        "approved. Read it, then {research}/digest.md and the questions it touches. {previous}"
        "{banks}Write {task_dir}/critique.md: is it feasible (hit rates, solve counts and runtime "
        "stated and plausible)? Is it worth running: would it change a belief that matters for the "
        "core question, more than the best alternative use of the run? Is the closest known "
        "technique named right, and what does this add beyond it (name prior work it missed if you "
        "know it)? Is a cheaper or more decisive design available? Which outcome would leave us no "
        "wiser? A `kind: probe` proposal is descriptive: judge only its cost and correctness. "
        "Mention a parked question only if its reopen condition is newly met. Number your points "
        "and mark each `blocking` or `note`. Start the file with frontmatter `recommend:` "
        "`approve`, `approve_with_notes` (notes the researcher must address in plan.md), `revise` "
        "(a blocking point: the experiment would give a wrong or uninterpretable answer, a clearly "
        "cheaper or more decisive design exists, or its value is low next to an alternative you "
        "name) or `reject` (no identifiable contribution to the core question), then one sentence "
        "why. {audit}Do not edit any other file."
    ),
    "prepare": (
        "Implement the approved proposal {task_dir}/proposal.md. Also read, if present, "
        "approval.md (owner notes), critique.md (second opinion on the proposal; address its points "
        "or say in plan.md why not), code_review.md (review to address) and driver_feedback.md "
        "(failed checks to fix) in the task folder. The current directory is your git worktree on "
        "branch {branch}; the task folder is in the main checkout, so write task files there and "
        "commit no research/ files on {branch}. 1) Before running anything, write {task_dir}/plan.md, starting with "
        "frontmatter `estimated_minutes:` (expected queue wall-clock): conditions, seeds, "
        "measurements, and what each outcome would mean for the competing explanations. "
        "2) Implement and smoke-test at small scale. If you find the approved design cannot work "
        "as proposed (targets unreachable, rates or runtime far from the proposal's assumptions, "
        "a gate it cannot pass), stop there: write {task_dir}/infeasible.md with the measured "
        "numbers and what would work instead, commit, and end; the steward re-plans. "
        "3) Write {task_dir}/queue.yaml in "
        "scripts/run_queue.py format for the full run: commands run with this worktree as cwd, "
        "write outputs under $RUN_DIR, and every entry id starts with '{task}-'. "
        "4) Commit all changes on {branch} so `git status` is clean."
    ),
    "review_code": (
        "Review this experiment before it runs: the code (`git diff {base}..{commit}` in the "
        "current directory, the experiment's worktree; it may be empty when only the queue "
        "changed), and {task_dir}/proposal.md, plan.md and queue.yaml (arms, seeds, parameters, "
        "timeouts). If {task_dir}/critique.md exists, check that its points are addressed or that "
        "plan.md says why not; an unanswered substantive point is a blocking issue. Gates, power "
        "checks and stop rules that decide whether the main stage runs are part of the review: "
        "check them for unjustified assumptions and the risk of stopping for the wrong reason "
        "(resample a pilot only when that could change whether the main stage runs); such a risk "
        "is a blocking issue. Write "
        "{task_dir}/code_review.md starting with frontmatter `verdict: pass` or `verdict: fail`, "
        "then numbered blocking issues and brief minor notes."
    ),
    "analyse": (
        "Analyse the results. Inputs: {task_dir}/proposal.md, queue.yaml, execution.md (run status "
        "and output folders) and the code in the current directory. Do not open plan.md until your "
        "analysis is written. Write {task_dir}/analysis.md: data completeness first, then the key "
        "numbers with denominators, plots if they help (save them in the task folder), and what "
        "the data does and does not show. Then read plan.md and append '## Against the predictions'. "
        "Finally put frontmatter `outcome:` at the top of analysis.md: the plan's outcome label the "
        "data matches, or `unresolved`, `pilot_only`, or `observations` for a probe."
    ),
    "decide": (
        "This experiment cycle is over.{blocked} Read the task folder (proposal, critique, plan, "
        "infeasible, code review, execution, analysis — whichever exist). 1) Update the question at "
        "{research}/{node}: append to log.md (experiment → result → `Decision: … because …`), "
        "update question.md (status, summary, Related, Reopen if), and update {research}/digest.md "
        "if beliefs changed. For each changed belief give the observed contrast, its uncertainty "
        "and the tested scope; an unresolved or finite-sample result is not equality or absence, "
        "and a heading must not claim more than the text below it. A probe's results are "
        "observations: log them, but keep them out of the digest's beliefs until a later "
        "experiment confirms them. Fix any problems listed under "
        "'## Digest check' in critique.md. Re-check "
        "parked questions whose reopen condition may now be met. 2) Write {task_dir}/decision.md: "
        "continue, park, close or new question, and why. If this step was interrupted before, "
        "check what is already written and do not add a log entry twice. 3) {next_step} "
        "4) Write the owner's brief to {brief}, under one "
        "page: what was tested and why · what happened (key numbers) · what we learned (1–3 "
        "sentences) · how the tree changed · the next proposal and why · failures and uncertainty."
    ),
    "strategy": (
        "Review the whole research program. Read the core question in {repo}/README.md, "
        "{research}/digest.md, the question tree, the plans and owner notes in {research}/plans, "
        "the latest decisions and the recent briefs in {research}/briefs. Write {task_dir}/strategy.md: what the program has learned so far · "
        "which root questions matter most for the core question now, and why · the current line "
        "against at least one mechanistically different candidate (from owner notes, the "
        "literature, or results nobody has explained; search the literature for it and cite only "
        "papers you found, with links) · what the steward should work on next (a question and "
        "why, not a full design) · what to stop. For every owner note (`owner-*.md`) that is new "
        "or changed since an earlier strategy.md answered it, say pursued, deferred or declined, "
        "why, and when to reconsider. {run_note} "
        "{roots_note} Start strategy.md with frontmatter `next: proposal`, or `next: stop` (the run "
        "then ends and waits for the owner). Stop when no candidate justifies its full cost in the "
        "time left; feasibility alone does not justify running. A promising direction that lacks a "
        "plan is a reason to write one in {research}/plans/, not to stop."
    ),
    "summary": (
        "The autonomous run that started at {started} has ended: {reason}. Write {summary} for the "
        "owner, who will review the run and may change how the loop works: each cycle of the run in "
        "one or two lines (the driver's table {ledger} lists them; see the briefs and research/runs/ "
        "folders since then) · how the question "
        "tree and digest changed (`git log -p --since=\"{started}\" -- research/` helps) · what you "
        "would do next · where the agents were least sure · what the owner should check first, "
        "including decisions you disagree with. Under two pages. {audit}Edit no other file."
    ),
    "allocate": (
        "The steward's next proposal {proposal} is for a question with no experiment budget left "
        "(there or at an ancestor). Read it, the latest strategy.md in {research}/runs and the "
        "question's log. Either grant its root a block of experiments that lasts through the next "
        "strategy review (normally {block}, fewer if time is short; raise only the `experiments` "
        "field of the root's budget), or send it to a full strategy review. Write "
        "{task_dir}/allocation.md starting with frontmatter `next: proposal` (you granted) or "
        "`next: strategy`, then at most 150 words: why, and the block's exit condition. {run_note}"
    ),
    "condense": (
        "{research}/digest.md is {words} words, over its {cap}-word limit. Rewrite it as current "
        "beliefs: one short section per root question, each claim with its contrast, uncertainty, "
        "scope and a link to its evidence. Move history and superseded numbers into the questions' "
        "log.md files (append; do not rewrite logs). Compress; do not change what is believed. "
        "Edit no other file."
    ),
}

NEXT_PROPOSAL = "Write the next proposal to {next_dir}/proposal.md (README format)."
NEXT_PROPOSAL_AUTO = (
    "Write the next proposal to {next_dir}/proposal.md (README format) — or, if no open question "
    "deserves another experiment, write none and start decision.md with frontmatter "
    "`next: strategy`; the strategist then reviews the program first.")
NEXT_STRATEGY = ("Write no next proposal: the strategist reviews the whole program before the "
                 "next one.")
PREVIOUS = ("This revises the proposal in {prev}: if it is the same experiment, first check that "
            "the points in {prev}/critique.md are fixed, then look for new defects. ")
AUDIT = ("Also check the belief updates since the last check (`git log -p {range} -- "
         "research/digest.md research/questions`) against the analysis.md files they rest on "
         "(latest: {research}/runs/{after}): list any statement that claims more than the evidence "
         "(a finite sample read as absence, an unresolved result read as equality, a widened "
         "scope, a heading stronger than its text) under '## Digest check' in critique.md, "
         "briefly. These do not affect your recommendation. ")
FINAL_AUDIT = ("Then add '## Claim check': belief updates since the last check (`git log -p "
               "{range} -- research/digest.md research/questions`) that claim more than their "
               "analysis.md shows. ")


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
        self.auto = False  # `run --auto`: the critic approves, the strategist steers
        self.run_path = research / "auto_run.json"  # survives task changes and restarts
        self.run_info: dict[str, Any] = {}
        self.sleep = time.sleep

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
        if phase not in ("analyse", "decide", "condense", "summary"):  # finish a finished queue
            self.check_deadline()
        calls = self.state.get("agent_calls", 0)
        if calls >= self.cfg.get("max_agent_calls", 8) and phase not in ("decide", "condense",
                                                                           "summary"):
            if phase in ("propose", "critique", "strategy") or "node" not in self.state:
                raise Stop(f"agent call cap ({calls}) reached while proposing; "
                           "`research.py propose` starts over")
            self.block(f"agent call cap ({calls}) reached")
            raise _Blocked()
        self.state["agent_calls"] = calls + 1
        self.save()
        meta = load_role(self.research, role)
        values = {"role": role, "research": str(self.research), "repo": str(self.repo),
                  "task_dir": str(self.task_dir()),
                  "task": self.state["task"], **fmt}
        prompt = (COMMON + PROMPTS[phase]).format(**values)
        argv = agent_argv(self.research, meta, prompt)
        timeout = float(meta.get("timeout_min", 60)) * 60
        label = f"{phase}-{self.state['agent_calls']}"
        self.log(f"{role} ({meta['agent']}/{meta['model']}) → {phase} [{self.launcher.name}]")
        t0 = time.monotonic()
        code = self.launch(label, argv, cwd, timeout)
        self.state["agent_seconds"] = self.state.get("agent_seconds", 0) + time.monotonic() - t0
        self.save()
        if code != 0:
            raise AgentFailed(f"{role} agent for {phase} "
                              f"{'timed out' if code is None else f'exited {code}'}"
                       f"; see {self.task_dir() / 'logs' / (label + '.log')}")

    def block(self, reason: str) -> None:
        """Abandon the experiment; the steward records why in `decide`."""
        self.state["blocked"] = reason
        self.log(f"blocked: {reason}")
        self.set_phase("decide")

    def expect(self, name: str) -> Path:
        path = self.task_dir() / name
        if not path.exists():
            raise AgentFailed(f"agent finished but did not write {path}")
        return path

    # -- phases ---------------------------------------------------------
    def phase_propose(self) -> None:
        feedback = strategy = ""
        if rejected := self.state.get("rejected"):
            feedback = (f"The previous proposal ({rejected}) was set aside; read it and the "
                        "rejected.md and critique.md beside it (whichever exist), and propose "
                        "something that answers the objections. ")
        if (self.task_dir() / "strategy.md").exists():
            strategy = (f"First read {self.task_dir() / 'strategy.md'}, the strategist's direction "
                        "for the program; follow it or say in the proposal why not. ")
        if self.auto and self.deadline:
            hours = (self.deadline - self.now()).total_seconds() / 3600
            strategy += (f"This autonomous run has about {max(hours, 0):.1f} h left; size the "
                         "experiment so its preparation and queue finish within it. ")
        self.call_agent("steward", "propose", self.repo, feedback=feedback, strategy=strategy,
                        banks=self.bank_note())
        self.expect("proposal.md")  # missing → retry the steward, not the acceptance
        self.set_phase(ACCEPT)
        self.accept_proposal()

    def accept_proposal(self) -> None:
        meta, _ = read_frontmatter(self.expect("proposal.md"))
        node = str(meta.get("node", "")).strip().strip("/")
        if not node.startswith("questions/") or not (self.research / node / "question.md").exists():
            raise Stop(f"proposal.md node {node!r} is not a question folder under research/questions")
        self.check_roots()
        self.state["node"] = node
        self.state.pop("rejected", None)
        self.critique()
        self.set_phase(AWAITING)
        left = remaining_budget(self.research, self.research / node)
        self.log(f"proposal: {meta.get('title', '?')} [{node}] — budget left: "
                 f"{'unlimited' if left is None else left}. Approve with `research.py approve`.")

    def critique(self) -> None:
        """Second opinion on the proposal, if a critic role exists. Optional:
        without it (failure, deadline, call cap) the owner still decides."""
        crit = self.task_dir() / "critique.md"
        if crit.exists() and self.state.get("critique_done"):
            return
        crit.unlink(missing_ok=True)  # output of a failed or interrupted critic
        if not (self.research / "roles" / "critic.md").exists():
            return
        prev, after = self.state.get("previous"), self.state.get("after")
        head = git("rev-parse", "HEAD", cwd=self.repo)
        try:
            self.call_agent("critic", "critique", self.repo,
                            previous=PREVIOUS.format(prev=prev) if prev else "",
                            banks=self.bank_note(),
                            audit=AUDIT.format(research=self.research, after=after,
                                               range=self.audit_range()) if after else "")
            self.expect("critique.md")
            self.state["critique_done"] = True
            if after:
                self.state["audited"] = head
            self.save()
        except Stop as e:
            crit.unlink(missing_ok=True)  # never trust a verdict from a failed run
            self.log(f"no critique: {e}")

    def is_probe(self, proposal: Path | None = None) -> bool:
        proposal = proposal or self.task_dir() / "proposal.md"
        return proposal.exists() and str(
            read_frontmatter(proposal)[0].get("kind", "")).strip().lower() == "probe"

    def probe_allowed(self) -> bool:
        """One probe per run, plus one per four full experiments it has run."""
        probes = self.run_info.get("probes", [])
        full = len(self.run_info.get("executed", [])) - len(probes)
        return len(probes) < 1 + full // 4

    def audit_range(self) -> str:
        """Commits whose belief updates no critic has checked yet."""
        since = self.state.get("audited")
        if since and git_ok("merge-base", "--is-ancestor", since, "HEAD", cwd=self.repo):
            return f"{since}..HEAD"
        return "-1"

    def bank_exposure(self) -> dict[str, int]:
        """Executed experiments per task bank (proposal frontmatter `bank:`)."""
        out: dict[str, int] = {}
        for ex in (self.research / "runs").glob("*/execution.md"):
            prop = ex.parent / "proposal.md"
            bank = (str(read_frontmatter(prop)[0].get("bank", "")).strip()
                    if prop.exists() else "")
            if bank and bank.lower() != "none":
                out[bank] = out.get(bank, 0) + 1
        return out

    def bank_note(self) -> str:
        used = self.bank_exposure()
        if not used:
            return ""
        return ("Task banks already used by experiments: " + ", ".join(
            f"{b} ({n})" for b, n in sorted(used.items())) + ". These are development banks: a "
            "transfer claim needs a fresh bank, frozen with the method before it is scored. ")

    def phase_prepare(self) -> None:
        if not self.state.get("worktree_ready"):
            self.create_worktree()
        wt = self.worktree()
        self.call_agent("researcher", "prepare", wt, branch=self.state["branch"])
        if (self.task_dir() / "infeasible.md").exists():
            self.block("the researcher found the approved design infeasible; see infeasible.md")
            return
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
            if not git_ok("merge", "--no-edit", base, cwd=wt) and not self.resolve_notes(wt):
                git_ok("merge", "--abort", cwd=wt)
                self.block(f"merging {base} into {rb} conflicts; resolve by hand")
                raise _Blocked()
            self.state["base"] = git("rev-parse", "HEAD", cwd=wt)
            self.save()
        self.run_setup(wt, "setup")
        self.state["worktree_ready"] = True
        self.save()

    def resolve_notes(self, wt: Path) -> bool:
        """Finish a conflicted merge of the base branch whose conflicts are all
        under research/: the notes on the base branch are the record (code
        branches only carry copies, e.g. a first-pass code_review.md)."""
        paths = git("diff", "--name-only", "--diff-filter=U", cwd=wt).splitlines()
        if not paths or not all(p.startswith("research/") for p in paths):
            return False
        for p in paths:
            if git_ok("checkout", "--theirs", "--", p, cwd=wt):
                git_ok("add", "--", p, cwd=wt)
            else:  # deleted on the base branch
                git_ok("rm", "-q", "--", p, cwd=wt)
        if not git_ok("commit", "--no-edit", cwd=wt):
            return False
        self.log(f"merge conflicts in research/ notes resolved to {self.cfg['base_branch']}'s "
                 f"version: {', '.join(paths)}")
        return True

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
                if any(e.timeout_seconds <= 0 for e in entries):
                    problems.append("every queue entry needs a positive `timeout_seconds`")
                cap = float(self.cfg.get("max_queue_hours", 8))
                total = sum(e.timeout_seconds for e in entries) / 3600
                probe_cap = float(self.cfg.get("probe_max_queue_minutes", 60))
                if self.is_probe() and total * 60 > probe_cap:
                    problems.append(
                        f"this is a probe: queue entry timeouts sum to {total * 60:.0f} min, over "
                        f"the {probe_cap:g} min probe cap; trim it or ask for a full experiment")
                if total > cap:
                    problems.append(
                        f"queue entry timeouts sum to {total:.1f} h, over the {cap:g} h cap on "
                        "running without review: set realistic `timeout_seconds` per entry (the "
                        "default is 4 h), or run a first stage now and the rest in a later cycle")
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
        # Queue time without review is capped across retries too. After a crash
        # the attempt is charged conservatively: everything since it started.
        used = self.state.get("queue_seconds", 0.0)
        if started := self.state.pop("queue_started", None):  # the driver died mid-queue
            used += max(0.0, time.time() - started)
            self.state["queue_seconds"] = used
            self.save()
        if not (td / "execution.md").exists():  # a new campaign, not a resumed one
            if self.auto:
                self.admit_queue()
            left = remaining_budget(self.research, self.node_path())
            if left is not None and left <= 0:
                self.block(f"no experiment budget left at {self.state['node']} or an ancestor "
                           "(owner raises `experiments` in question.md)")
                return
            self.charge_run()
            # Writing execution.md charges the budget (see executed_nodes).
            atomic_write(td / "execution.md", "# Execution\n\nStarted; results pending.\n")
        elif status_path.exists():
            # Resuming after a crash: run_queue never retries entries it marks
            # interrupted, so clear those; finished entries are kept.
            status = json.loads(status_path.read_text())
            retry = [k for k, v in status.items() if v.get("status") in ("interrupted", "running")]
            if retry:
                self.log(f"re-running interrupted queue entries: {retry}")
                atomic_write(status_path, json.dumps(
                    {k: v for k, v in status.items() if k not in retry}, indent=2) + "\n")
        cap = float(self.cfg.get("max_queue_hours", 8)) * 3600
        timeout = min(sum(e.timeout_seconds for e in entries) + 900, cap - used)
        if timeout <= 0:
            self.block(f"the queue used its {cap / 3600:g} h of unreviewed running time")
            return
        argv = ["uv", "run", "python", "scripts/run_queue.py", "--queue", str(queue),
                "--status", str(status_path), "--lock", str(self.repo / "queue.lock"),
                "--output-root", str(self.repo / "experiments" / "output")]
        self.log(f"running queue ({len(entries)} entries)")
        self.state.update(queue_seconds=used, queue_started=time.time())
        self.save()
        code = self.launch("queue", argv, wt, timeout, kill_grace=QUEUE_KILL_GRACE_SECONDS)
        self.state["queue_seconds"] = used + time.time() - self.state.pop("queue_started")
        self.save()
        if code == QUEUE_LOCKED_EXIT:
            raise Stop("another queue runner holds queue.lock; resume when it is done")
        if code is None:
            raise Stop("queue runner timed out or was killed; resume re-runs unfinished entries")
        if code != 0:
            raise Stop(f"queue runner failed (exit {code}); see {td / 'logs' / 'queue.log'}")
        status = json.loads(status_path.read_text()) if status_path.exists() else {}
        unfinished = [e.id for e in entries
                      if status.get(e.id, {}).get("status") not in FINISHED_ENTRY_STATUSES]
        if unfinished:
            raise Stop(f"queue entries did not finish: {unfinished}; resume re-runs them")
        rows = [f"| {e.id} | {status.get(e.id, {}).get('status', 'not run')} | "
                f"{status.get(e.id, {}).get('wall_seconds', '')} | "
                f"{status.get(e.id, {}).get('run_dir', '')} |" for e in entries]
        atomic_write(td / "execution.md", (
            f"# Execution\n\nCode: commit `{self.state['commit']}` on `{self.state['branch']}`. "
            f"Queue runner exit: {code}.\n\nRerun: check out that commit (`git worktree add <dir> "
            f"{self.state['commit']}`), run the `worktree_setup` commands from research/config.toml "
            f"in it, then `uv run python scripts/run_queue.py --queue <this folder>/queue.yaml` from "
            "it. Seeds are fixed, so the runs repeat.\n\n"
            "| id | status | wall s | output (repo-relative) |\n"
            "|---|---|---|---|\n" + "\n".join(rows) + "\n"))
        # Later experiments build on this code.
        git("branch", "-f", self.cfg["research_branch"], self.state["commit"], cwd=self.repo)
        self.set_phase("analyse")

    def admit_queue(self) -> None:
        """End the run, leaving the cycle at execute for the next run, rather than
        start a queue whose plan expects it to finish well after the deadline."""
        if not self.deadline:
            return
        try:
            est = float(read_frontmatter(self.task_dir() / "plan.md")[0].get("estimated_minutes"))
        except (TypeError, ValueError, OSError):
            return
        left = (self.deadline - self.now()).total_seconds() / 60
        if est > left + float(self.cfg.get("deadline_grace_minutes", 30)):
            raise RunComplete(f"the next queue needs about {est:.0f} min and the run has "
                              f"{max(left, 0):.0f} min left; the next run starts it")

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
        cycles = self.run_info.get("cycles_since_strategy", 0) + 1
        strategy_due = self.auto and cycles >= self.cfg.get("strategy_every", 4)
        next_dir = self.research / "runs" / nxt
        next_step = (NEXT_STRATEGY if strategy_due else
                     NEXT_PROPOSAL_AUTO if self.auto else NEXT_PROPOSAL).format(next_dir=next_dir)
        self.call_agent("steward", "decide", cwd, node=self.state["node"], next_step=next_step,
                        brief=str(brief), blocked=blocked)
        self.expect("decision.md")
        if not brief.exists():
            raise Stop(f"steward did not write the brief {brief}")
        self.condense_digest(cwd)
        proposal = next_dir / "proposal.md"
        to_strategy = to_allocate = False
        if self.auto:
            wants = str(read_frontmatter(self.task_dir() / "decision.md")[0].get("next", ""))
            to_strategy = (strategy_due or wants.strip().lower() == "strategy"
                           or self.changes_root(proposal))
            # A proposal that only lacks budget gets a short allocation decision.
            to_allocate = not to_strategy and self.over_budget(proposal)
            if not to_strategy and not proposal.exists():
                raise AgentFailed("steward wrote neither a next proposal nor `next: strategy`")
            if to_strategy and proposal.exists():  # the strategist sees it as a suggestion
                proposal.rename(next_dir / "steward_proposal.md")
            self.run_info["cycles"] = self.run_info.get("cycles", 0) + 1
            self.run_info["cycles_since_strategy"] = cycles
            self.save_run()
            self.ledger_cycle()
        # Hand over to the next proposal (written by the steward above) before
        # cleaning up, so a crash here never loses the finished cycle.
        cleanup = {"task": self.state["task"], "worktree": self.state.get("worktree"),
                   "brief": str(brief)}
        nxt_phase = "strategy" if to_strategy else "allocate" if to_allocate else ACCEPT
        audited = self.state.get("audited")
        self.state = {"phase": nxt_phase, "task": nxt, "cleanup": cleanup,
                      "after": cleanup["task"]}
        if audited:
            self.state["audited"] = audited
        self.save()
        self.run_cleanup(cleanup)
        if self.auto and len(self.run_info.get("executed", [])) >= self.max_experiments():
            raise RunComplete(f"the run used all {self.max_experiments()} of its experiments")
        if nxt_phase == ACCEPT:
            self.accept_proposal()

    def condense_digest(self, cwd: Path) -> None:
        """The digest is loaded by every agent: keep it to current beliefs."""
        cap = int(self.cfg.get("digest_max_words", 3000))
        digest = self.research / "digest.md"
        words = len(digest.read_text().split()) if digest.exists() else 0
        if words <= cap:
            return
        self.call_agent("steward", "condense", cwd, words=str(words), cap=str(cap))
        after = len(digest.read_text().split())
        self.log(f"digest condensed: {words} → {after} words"
                 + (f" (still over {cap})" if after > cap else ""))

    def phase_allocate(self) -> None:
        proposal = self.expect("proposal.md")
        self.check_roots()
        self.call_agent("strategist", "allocate", self.repo, proposal=str(proposal),
                        block=str(self.cfg.get("strategy_every", 4)), run_note=self.run_note())
        meta, _ = read_frontmatter(self.expect("allocation.md"))
        nxt = str(meta.get("next", "")).strip().lower()
        if self.auto:
            self.run_info["root_budgets"] = self.root_budgets()  # the strategist may raise them
            self.save_run()
        self.check_roots()
        granted = nxt == "proposal" and not self.over_budget(proposal)
        if self.auto:
            self.ledger([f"{self.state['task']} (allocation)", "", "", "", "", "", "",
                         f"allocation: {'granted' if granted else 'to strategy'}", ""])
        if not granted:
            proposal.rename(self.task_dir() / "steward_proposal.md")
            self.set_phase("strategy")
            return
        self.set_phase(ACCEPT)
        self.accept_proposal()

    def run_note(self) -> str:
        if not self.auto:
            return ""
        used, cap = len(self.run_info.get("executed", [])), self.max_experiments()
        hours = (self.deadline - self.now()).total_seconds() / 3600 if self.deadline else 0
        return (f"This autonomous run has used {used} of its {cap} experiments and has about "
                f"{max(hours, 0):.0f} h left. Question budgets are allocations: you may raise "
                "`experiments` in a root question's budget (only that frontmatter field) by a "
                "block that lasts through the next strategy review, naming its exit condition "
                "and expected total time; `research.py status` shows what is left.")

    def phase_strategy(self) -> None:
        left = self.cfg.get("max_new_roots", 2) - len(self.new_roots())
        roots_note = ("This run may not open more root questions; work with the existing roots."
                      if left <= 0 else
                      f"You may open {left} more root question(s) with a plan (see your role file).")
        if (self.task_dir() / "steward_proposal.md").exists():
            roots_note += (f" The steward suggested {self.task_dir() / 'steward_proposal.md'}; "
                           "weigh it.")
        if rejected := self.state.get("rejected"):
            roots_note += (f" The last proposal, {rejected}, was set aside; read the rejected.md "
                           "and critique.md beside it.")
        run_note = self.run_note()
        self.check_roots()  # raises made before strategy (e.g. in decide) are not the strategist's
        self.call_agent("strategist", "strategy", self.repo, roots_note=roots_note,
                        run_note=run_note)
        meta, _ = read_frontmatter(self.expect("strategy.md"))
        nxt = str(meta.get("next", "")).strip().lower()
        if self.auto:
            self.run_info["cycles_since_strategy"] = 0
            self.run_info["root_budgets"] = self.root_budgets()  # the strategist may raise them
            self.save_run()
        self.check_roots()
        if self.auto:
            self.ledger([f"{self.state['task']} (strategy)", "", "", "", "", "", "",
                         f"strategy: next {nxt or '?'}", ""])
        if nxt == "stop":
            raise OwnerNeeded(f"the strategist recommends stopping; see {self.task_dir()}/strategy.md")
        self.set_phase("propose")

    def changes_root(self, proposal: Path) -> bool:
        """Does this proposal move to a different root question than the cycle that wrote it?"""
        if not proposal.exists() or "node" not in self.state:
            return False
        node = str(read_frontmatter(proposal)[0].get("node", "")).strip().strip("/")
        return node.split("/")[:2] != self.state["node"].split("/")[:2]

    def over_budget(self, proposal: Path) -> bool:
        """Is the proposal for a question with no experiment budget left?"""
        if not proposal.exists():
            return False
        node = str(read_frontmatter(proposal)[0].get("node", "")).strip().strip("/")
        if not (self.research / node / "question.md").exists():
            return False
        left = remaining_budget(self.research, self.research / node)
        return left is not None and left <= 0

    def root_budgets(self) -> dict[str, int | None]:
        out = {}
        for name in sorted(self.top_level_questions()):
            b = _budget(self.research / "questions" / name / "question.md")
            out[name] = int(b["experiments"]) if "experiments" in b else None
        return out

    def max_experiments(self) -> int:
        return int(self.run_info.get("max_experiments", self.cfg.get("auto_max_experiments", 40)))

    def charge_run(self) -> None:
        """Count an experiment against the autonomous run's limit, once per task."""
        if not self.auto:
            return
        executed = self.run_info.setdefault("executed", [])
        if self.state["task"] in executed:
            return
        if len(executed) >= self.max_experiments():
            raise RunComplete(f"the run used all {len(executed)} of its experiments")
        executed.append(self.state["task"])
        if self.is_probe():
            self.run_info.setdefault("probes", []).append(self.state["task"])
        self.save_run()

    def new_roots(self) -> set[str]:
        return self.top_level_questions() - set(self.run_info.get("roots_at_start", []))

    def check_roots(self) -> None:
        """At most `max_new_roots` new root questions per autonomous run."""
        if not self.auto:
            return
        new, allowed = self.new_roots(), self.cfg.get("max_new_roots", 2)
        if len(new) > allowed:
            raise OwnerNeeded(f"the run has opened {len(new)} new root questions "
                              f"({', '.join(sorted(new))}); at most {allowed} allowed")
        # Only the strategist raises root budgets; its raises are recorded after each strategy.
        known = self.run_info.get("root_budgets", {})
        for name, now in self.root_budgets().items():
            before = known.get(name)
            raised = (now is None or now > before) if before is not None else False
            if name in known and raised:
                raise OwnerNeeded(f"root question {name}'s budget was raised outside strategy "
                                  f"({before} → {now})")

    def top_level_questions(self) -> set[str]:
        return {q.name for q in (self.research / "questions").iterdir()
                if (q / "question.md").exists()}

    def run_cleanup(self, cleanup: dict[str, Any]) -> None:
        wt = cleanup.get("worktree")
        if wt and Path(wt).exists() and not git("status", "--porcelain", cwd=Path(wt)):
            git_ok("worktree", "remove", wt, cwd=self.repo)
        self.publish(f"Research: {cleanup['task']}", f"research/{cleanup['task']}")
        self.state.pop("cleanup", None)
        self.save()
        self.log(f"cycle {cleanup['task']} done; brief: {cleanup['brief']}")

    def publish(self, message: str, code_branch: str | None = None) -> None:
        """Commit research/ and push it with the code that produced it."""
        if self.cfg.get("commit_research"):
            git_ok("add", "research", cwd=self.repo)
            git_ok("commit", "-m", message, "--", "research", cwd=self.repo)
        if self.cfg.get("push"):
            refs = ["HEAD", self.cfg["research_branch"]] + ([code_branch] if code_branch else [])
            refs = [r for r in refs if git_ok("rev-parse", "--verify", r, cwd=self.repo)]
            if git_ok("push", "origin", *refs, cwd=self.repo):
                return
            # Usually the owner pushed to the base branch meanwhile: merge it and retry.
            base = self.cfg["base_branch"]
            if (git_ok("fetch", "origin", base, cwd=self.repo)
                    and git_ok("merge", "--no-edit", f"origin/{base}", cwd=self.repo)):
                if git_ok("push", "origin", *refs, cwd=self.repo):
                    self.log(f"merged origin/{base} (pushed by the owner meanwhile) and pushed")
                    return
            else:
                git_ok("merge", "--abort", cwd=self.repo)
            self.log(f"push of {' '.join(refs)} failed; push by hand")

    # -- control --------------------------------------------------------
    def advance(self) -> None:
        """Run phases until the loop needs the owner, a deadline, or a fix."""
        self.reconcile()
        handlers = {"propose": self.phase_propose, ACCEPT: self.accept_proposal,
                    "strategy": self.phase_strategy, "allocate": self.phase_allocate,
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
                if not self.auto:
                    return
                self.auto_approve()
                continue
            if (self.research / "STOP").exists():
                raise Stop("research/STOP exists; remove it to continue")
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

    # -- autonomous mode ------------------------------------------------
    def save_run(self) -> None:
        atomic_write(self.run_path, json.dumps(self.run_info, indent=2) + "\n")

    def auto_approve(self) -> None:
        """The critic's verdict stands in for the owner's (Plans/research-auto.md)."""
        self.check_deadline()  # no new experiment after the deadline
        self.check_roots()
        td, rounds = self.task_dir(), self.state.get("rounds", 0)
        self.critique()  # no-op when a complete critique exists
        crit = td / "critique.md"
        rec = (str(read_frontmatter(crit)[0].get("recommend", "")).strip().lower()
               if crit.exists() else "")
        if rec not in ("approve", "approve_with_notes", "revise", "reject"):
            raise AgentFailed("no critique with `recommend: approve|approve_with_notes|revise|reject`")
        left = remaining_budget(self.research, self.node_path())
        if left is not None and left <= 0:
            # Budgets are allocations; the strategist may grant more or redirect.
            self.set_aside(f"No experiment budget left at {self.state['node']} or an ancestor.",
                           rec, to_strategy=True)
            return
        if rec in ("approve", "approve_with_notes") and self.is_probe() and not self.probe_allowed():
            self.set_aside("The run has used its probe allowance (one, plus one per four full "
                           "experiments); propose a full experiment.", rec, to_strategy=False)
            return
        if rec in ("approve", "approve_with_notes"):
            if len(self.run_info.get("executed", [])) >= self.max_experiments():
                raise RunComplete(f"the run used all {self.max_experiments()} of its experiments")
            note = ("Approved by the critic in autonomous mode." if rec == "approve" else
                    "Approved with notes by the critic in autonomous mode: address the notes in "
                    "critique.md or say in plan.md why not. The code reviewer checks this.")
            atomic_write(td / "approval.md", note + "\n")
            self.state.update(approved=True, approved_at=self.now().isoformat())
            self.log(f"auto-approved (critic: {rec}, revisions: {rounds})")
            self.set_phase("prepare")
            return
        why = f"The critic recommends `{rec}`; see critique.md beside the proposal."
        if rounds >= 4:
            raise OwnerNeeded(f"five proposals in a row were turned down (last: {td}); {why}")
        # After two revisions the strategist redesigns or redirects, rather than
        # running a proposal the critic still objects to.
        self.set_aside(why, rec, to_strategy=rounds == 2)

    def set_aside(self, why: str, rec: str, to_strategy: bool) -> None:
        td, rounds = self.task_dir(), self.state.get("rounds", 0)
        atomic_write(td / "rejected.md", why + "\n")
        self.ledger([td.name, self.state.get("node", ""), rec, "", "",
                     f"{self.state.get('agent_seconds', 0) / 60:.0f}", "",
                     "to strategy" if to_strategy else "sent back", why])
        keep = {k: self.state[k] for k in ("after", "audited") if k in self.state}
        self.state = {"phase": "strategy" if to_strategy else "propose",
                      "task": self.new_task_id(), "rejected": str(td / "proposal.md"),
                      "previous": str(td), "rounds": rounds + 1, **keep}
        self.task_dir().mkdir(parents=True, exist_ok=True)
        self.save()
        self.log(f"proposal {'sent to the strategist' if to_strategy else 'sent back to the steward'}"
                 f" ({why})")

    # -- the run ledger: one row per cycle, for the owner's review ---------
    LEDGER_HEAD = ("| task | node | critic | code review | queue min (est) | agent min | charged | "
                   "outcome | decision |\n|---|---|---|---|---|---|---|---|---|\n")

    def ledger(self, cells: list[str]) -> None:
        if not self.auto or not self.run_info.get("id"):
            return
        path = self.research / "briefs" / f"{self.run_info['id']}-ledger.md"
        text = path.read_text() if path.exists() else (
            f"# Autonomous run {self.run_info['id']}: ledger\n\nWritten by the driver. "
            "Proposals that did not run are listed as sent back.\n\n" + self.LEDGER_HEAD)
        row = "| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in cells) + " |\n"
        key = f"| {cells[0]} |"
        lines = [ln for ln in text.splitlines(keepends=True) if not ln.startswith(key)]
        atomic_write(path, "".join(lines) + row)  # a retried phase replaces its row

    def ledger_cycle(self) -> None:
        td = self.task_dir()

        def front(name: str, key: str) -> str:
            return (str(read_frontmatter(td / name)[0].get(key, "")) if (td / name).exists()
                    else "")

        queue_min = f"{self.state.get('queue_seconds', 0) / 60:.0f}" if (
            td / "execution.md").exists() else ""
        if est := front("plan.md", "estimated_minutes"):
            queue_min += f" ({est})"
        decision = ""
        if (td / "decision.md").exists():
            _, body = read_frontmatter(td / "decision.md")
            decision = next((ln.lstrip("# ").strip() for ln in body.splitlines() if ln.strip()), "")
        outcome = (f"blocked: {self.state['blocked']}" if self.state.get("blocked")
                   else front("analysis.md", "outcome"))
        review = front("code_review.md", "verdict")
        if self.state.get("repairs"):
            review += f" after {self.state['repairs']} repair(s)"
        node = self.state.get("node", "")
        if bank := front("proposal.md", "bank"):
            node += f" (bank: {bank})"
        if self.is_probe():
            node += " (probe)"
        self.ledger([td.name, node, front("critique.md", "recommend"),
                     review, queue_min, f"{self.state.get('agent_seconds', 0) / 60:.0f}",
                     "yes" if td.name in self.run_info.get("executed", []) else "no",
                     outcome, decision[:160]])

    def run_auto(self, hours: float) -> int:
        """Cycle without the owner until the time is up, research/STOP appears,
        or the owner is needed; then the strategist summarises the run."""
        self.auto = True
        info = json.loads(self.run_path.read_text()) if self.run_path.exists() else {}
        if info and not info.get("finished"):
            print(f"[research] resuming autonomous run {info['id']} (deadline {info['deadline']}; "
                  f"--hours ignored). Delete {self.run_path} to start a new run instead.")
        else:
            now = self.now()
            info = {"id": f"{now:%Y-%m-%d-%H%M}", "started": now.isoformat(timespec="seconds"),
                    "deadline": (now + dt.timedelta(hours=hours)).isoformat(timespec="seconds"),
                    "roots_at_start": sorted(self.top_level_questions()), "cycles": 0,
                    "cycles_since_strategy": 0,
                    "max_experiments": int(self.cfg.get("auto_max_experiments", 40)),
                    "executed": []}
        self.run_info = info
        info.setdefault("root_budgets", self.root_budgets())
        self.save_run()
        self.deadline = dt.datetime.fromisoformat(info["deadline"])
        try:
            self.reconcile()  # stop leftovers of a crashed run before anything else
        except Exception as e:  # noqa: BLE001
            self.finish_auto(f"cleaning up after the previous run failed: {e!r}")
            return 1
        reason, code, last, fails = None, 0, None, 0
        while reason is None:
            if (self.research / "STOP").exists():
                reason = "the research/STOP file was found"
            elif self.now() >= self.deadline and self.state.get("phase") not in ("analyse",
                                                                                  "decide"):
                reason = "its time was used up"  # a finished queue is still analysed first
            if reason:
                break
            phase = self.state.get("phase")
            try:
                self.advance()
            except OwnerNeeded as e:
                reason, code = f"the owner is needed: {e}", 1
            except RunComplete as e:
                reason = str(e)
            except AgentFailed as e:
                key = (self.state.get("task"), self.state.get("phase"))
                fails, last = (fails + 1 if key == last else 1), key
                self.log(f"agent failure {fails} in {key[1]}: {e}")
                if fails >= self.cfg.get("auto_max_retries", 3):
                    reason, code = f"{fails} agent failures in a row in {key[1]}: {e}", 1
                else:
                    self.sleep(self.cfg.get("auto_retry_minutes", 10) * 60)
            except Stop as e:
                if self.now() >= self.deadline:
                    reason = "its time was used up"
                else:
                    reason, code = f"it stopped in {self.state.get('phase', phase)}: {e}", 1
            except Exception as e:  # noqa: BLE001 - end the run with a summary, not a traceback
                reason, code = f"an unexpected error in {self.state.get('phase', phase)}: {e!r}", 1
        self.finish_auto(reason)
        return code

    def finish_auto(self, reason: str) -> None:
        info = self.run_info
        summary = self.research / "briefs" / f"{info['id']}-auto-summary.md"
        self.log(f"autonomous run {info['id']} ends: {reason}")
        try:
            self.reconcile()
        except Exception as e:  # noqa: BLE001 - still write the summary
            self.log(f"reconcile before the summary failed: {e!r}")
        if self.state.get("task") and not summary.exists():
            self.task_dir().mkdir(parents=True, exist_ok=True)
            try:
                self.call_agent("strategist", "summary", self.repo, started=info["started"],
                                audit=FINAL_AUDIT.format(range=self.audit_range()),
                                reason=reason, summary=str(summary),
                                ledger=str(summary.with_name(f"{info['id']}-ledger.md")))
            except Exception as e:  # noqa: BLE001 - fall back to a plain summary
                self.log(f"summary agent failed: {e}")
        if not summary.exists():
            started = dt.datetime.fromisoformat(info["started"]).timestamp()
            briefs = sorted(b for b in (self.research / "briefs").glob("*.md")
                            if b.stat().st_mtime >= started and b != summary)
            atomic_write(summary, (
                f"# Autonomous run {info['id']}\n\nStarted {info['started']}; ended: {reason}. "
                f"Cycles: {info.get('cycles', 0)}. The strategist's summary failed; see "
                f"{info['id']}-ledger.md and the briefs "
                "of this run:\n\n" + "".join(f"- {b.name}\n" for b in briefs)))
        info.update(finished=self.now().isoformat(timespec="seconds"), reason=reason)
        self.save_run()
        self.publish(f"Research: autonomous run {info['id']} ({reason})")
        print(f"[research] summary: {summary}")

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
        if self.run_path.exists():
            info = json.loads(self.run_path.read_text())
            state = (f"ended {info['finished']}: {info.get('reason')}" if info.get("finished")
                     else f"active until {info['deadline']}")
            print(f"autonomous run {info['id']}: {info.get('cycles', 0)} cycles, "
                  f"{len(info.get('executed', []))}/{info.get('max_experiments', '?')} "
                  f"experiments, {state}")
        if s.get("task") and (self.task_dir() / "proposal.md").exists():
            meta, _ = read_frontmatter(self.task_dir() / "proposal.md")
            print(f"proposal: {meta.get('title', '?')}  ({self.task_dir() / 'proposal.md'})")
            if (crit := self.task_dir() / "critique.md").exists():
                print(f"critique: {read_frontmatter(crit)[0].get('recommend', '?')}  ({crit})")
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
    p_run.add_argument("--auto", action="store_true",
                       help="autonomous: cycle without approvals (Plans/research-auto.md)")
    p_run.add_argument("--hours", type=float, default=48, help="length of an --auto run")
    args = ap.parse_args(argv)

    # SIGTERM (e.g. from launchd) unwinds like Ctrl-C so running agents are stopped.
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    driver = Driver()
    if args.cmd == "status":
        return driver.status()
    if args.cmd == "run" and not (args.now or args.auto):
        driver.wait_for_night()
    actions = {
        "propose": driver.propose,
        "approve": lambda: driver.approve(args.note),
        "reject": lambda: driver.reject(args.reason),
        "run": lambda: (driver.run_auto(args.hours) if args.auto
                        else driver.run(now_mode=args.now)),
    }

    def fresh() -> int:  # re-read state under the lock
        driver.state = load_state(driver.state_path)
        return actions[args.cmd]()

    return locked(driver.research, fresh)


if __name__ == "__main__":
    sys.exit(main())
