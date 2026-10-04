"""scripts/research.py: budgets, night window, and a full cycle with fake agents."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location("research", SCRIPTS / "research.py")
research = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(research)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip())
    return path


def question(path: Path, experiments: int | None, used: int = 0, status: str = "open") -> None:
    budget = f"budget: {{experiments: {experiments}, used: {used}}}\n" if experiments else ""
    write(path / "question.md", f"---\nstatus: {status}\ntags: [x]\n{budget}---\n# {path.name}?\n")
    write(path / "log.md", "# log\n")


# -- budgets ---------------------------------------------------------------


def executed_run(research_dir: Path, task: str, node: str) -> None:
    write(research_dir / "runs" / task / "proposal.md", f"---\nnode: {node}\n---\n")
    write(research_dir / "runs" / task / "execution.md", "# Execution\n")


def test_children_draw_from_ancestor_budget(tmp_path):
    q = tmp_path / "questions"
    question(q / "01-root", experiments=3, used=1)  # one recorded by hand
    question(q / "01-root" / "02-a", experiments=5)
    question(q / "01-root" / "03-b", experiments=5)
    executed_run(tmp_path, "t1", "questions/01-root/02-a")
    assert research.remaining_budget(tmp_path, q / "01-root" / "03-b") == 1  # root: 3 - 2
    executed_run(tmp_path, "t2", "questions/01-root/02-a")
    assert research.remaining_budget(tmp_path, q / "01-root" / "03-b") == 0
    assert research.remaining_budget(tmp_path, q / "01-root" / "02-a") == 0
    write(tmp_path / "runs" / "t3" / "proposal.md", "---\nnode: questions/01-root/03-b\n---\n")
    assert research.remaining_budget(tmp_path, q / "01-root") == 0  # proposals don't count


def test_no_budget_means_unlimited(tmp_path):
    q = tmp_path / "questions" / "01-free"
    question(q, experiments=None)
    executed_run(tmp_path, "t1", "questions/01-free")
    assert research.remaining_budget(tmp_path, q) is None


# -- night window ----------------------------------------------------------


def make_research(tmp_path: Path, **cfg) -> Path:
    r = tmp_path / "research"
    conf = {"night_start": "22:00", "night_end": "07:00", "launcher": "local",
            "max_repairs": 1, "max_agent_calls": 8, "base_branch": "main",
            "research_branch": "research/main", "worktree_root": "../wt",
            "worktree_setup": [], "commit_research": False, **cfg}
    lines = []
    for k, v in conf.items():
        lines.append(f"{k} = {json.dumps(v)}")
    write(r / "config.toml", "\n".join(lines) + "\n")
    write(r / "agents.toml", '[fake]\ncmd = ["fake", "{prompt}"]\n')
    for role in ("steward", "researcher", "reviewer"):
        write(r / "roles" / f"{role}.md", f"---\nagent: fake\nmodel: m-{role}\n---\nBe {role}.\n")
    question(r / "questions" / "01-root", experiments=2)
    (r / "briefs").mkdir()
    (r / "runs").mkdir()
    return r


def test_night_window_wraps_midnight(tmp_path):
    d = research.Driver(research=make_research(tmp_path), repo=tmp_path, launcher=object())
    day = dt.date(2026, 10, 4)
    at = lambda h, m=0: dt.datetime.combine(day, dt.time(h, m))  # noqa: E731
    assert d.in_night(at(23)) and d.in_night(at(3)) and not d.in_night(at(12))
    assert d.night_end_after(at(23)) == dt.datetime.combine(day + dt.timedelta(days=1), dt.time(7))
    assert d.night_end_after(at(3)) == at(7)


# -- full cycle with fake agents --------------------------------------------


class FakeLauncher:
    """Stands in for agents and the queue runner: writes what each phase must
    produce. `review_verdicts` scripts the reviewer's code-review answers."""

    name = "fake"

    def __init__(self, review_verdicts=("pass",)):
        self.driver = None
        self.calls: list[str] = []
        self.verdicts = list(review_verdicts)

    def run(self, label, argv, cwd, log_dir, timeout_s, env=None):
        d = self.driver
        td = d.task_dir()
        phase = label.rsplit("-", 1)[0]
        self.calls.append(phase)
        if phase == "propose":
            write(td / "proposal.md", "---\nnode: questions/01-root\ntitle: First\n---\nWhy.\n")
        elif phase == "prepare":
            with (Path(cwd) / "exp.py").open("a") as f:  # each repair changes the code
                f.write("print('hi')\n")
            subprocess.run(["git", "add", "-A"], cwd=cwd, check=True)
            subprocess.run(["git", "commit", "-qm", "exp"], cwd=cwd, check=True)
            write(td / "plan.md", "If A then X.\n")
            write(td / "queue.yaml", f"runs:\n  - id: {d.state['task']}-a\n    cmd: echo hi\n")
        elif phase == "review_code":
            write(td / "code_review.md", f"---\nverdict: {self.verdicts.pop(0)}\n---\nok\n")
        elif phase == "queue":
            status = {f"{d.state['task']}-a": {"status": "done", "wall_seconds": 1.0,
                                               "run_dir": "experiments/output/x"}}
            (td / "queue.status.json").write_text(json.dumps(status))
        elif phase == "analyse":
            write(td / "analysis.md", "All seeds present.\n")
        elif phase == "decide":
            write(td / "decision.md", "Continue.\n")
            nxt = d.research / "runs" / d.state["next_task"]
            write(nxt / "proposal.md", "---\nnode: questions/01-root\ntitle: Second\n---\nNext.\n")
            brief = next(a for a in argv if "brief" in a).split("owner's brief to ")[1].split(",")[0]
            write(Path(brief), "Brief.\n")
        return 0


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-qb", "main"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                    "--allow-empty", "-m", "init"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
    return root


def make_driver(repo, launcher, **cfg):
    r = make_research(repo, **cfg)
    clock = iter(dt.datetime(2026, 10, 4, 23, 0) + dt.timedelta(minutes=i) for i in range(10_000))
    d = research.Driver(research=r, repo=repo, launcher=launcher, now=lambda: next(clock))
    launcher.driver = d
    return d


def test_full_cycle_ends_awaiting_next_approval(repo):
    fake = FakeLauncher()
    d = make_driver(repo, fake)
    assert d.run(now_mode=True) == 0
    assert d.state["phase"] == research.AWAITING and fake.calls == ["propose"]
    first = d.state["task"]

    assert d.approve("small run please") == 0
    assert d.run(now_mode=True) == 0
    assert fake.calls == ["propose", "prepare", "review_code", "queue", "analyse", "decide"]
    assert d.state["phase"] == research.AWAITING and d.state["task"] != first

    runs = d.research / "runs" / first
    assert "| done |" in (runs / "execution.md").read_text()
    assert (runs / "approval.md").read_text().startswith("small run")
    assert research.remaining_budget(d.research, d.research / "questions" / "01-root") == 1
    # Code builds on the previous experiment; the finished worktree is removed.
    assert research.git("rev-parse", "research/main", cwd=repo) == research.git(
        "rev-parse", f"research/{first}", cwd=repo)
    assert not (repo / "../wt" / first).resolve().exists()
    assert list((d.research / "briefs").glob("*.md"))


def test_failed_review_gets_one_repair_then_blocks(repo):
    fake = FakeLauncher(review_verdicts=["fail", "fail"])
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    d.approve(None)
    d.run(now_mode=True)
    assert fake.calls == ["propose", "prepare", "review_code", "prepare", "review_code", "decide"]
    assert research.remaining_budget(d.research, d.research / "questions" / "01-root") == 2


def test_exhausted_budget_blocks_execution(repo):
    fake = FakeLauncher()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    question(d.research / "questions" / "01-root", experiments=2, used=2)
    d.approve(None)
    d.run(now_mode=True)
    assert "queue" not in fake.calls and fake.calls[-1] == "decide"


def test_agent_failure_stops_and_resumes(repo):
    class Flaky(FakeLauncher):
        fail_once = True

        def run(self, label, argv, cwd, log_dir, timeout_s, env=None):
            if label.startswith("analyse") and self.fail_once:
                self.fail_once = False
                return None  # timed out
            return super().run(label, argv, cwd, log_dir, timeout_s, env)

    fake = Flaky()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    d.approve(None)
    assert d.run(now_mode=True) == 1
    assert d.state["phase"] == "analyse"
    # A fresh driver (e.g. after a crash) resumes from state.json.
    d2 = research.Driver(research=d.research, repo=repo, launcher=fake, now=d.now)
    fake.driver = d2
    assert d2.run(now_mode=True) == 0
    assert d2.state["phase"] == research.AWAITING


def test_reject_asks_for_new_proposal(repo):
    fake = FakeLauncher()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    old = d.state["task"]
    assert d.reject("too big") == 0
    assert (d.research / "runs" / old / "rejected.md").exists()
    assert d.state["phase"] == "propose" and d.state["rejected"].endswith("proposal.md")
    assert d.propose() == 0 and d.state["phase"] == research.AWAITING


def test_local_launcher_times_out_and_kills_group(tmp_path, monkeypatch):
    monkeypatch.setattr(research, "KILL_GRACE_SECONDS", 1)
    monkeypatch.setattr(research, "POLL_SECONDS", 0.2)
    launcher = research.LocalLauncher()
    marker = tmp_path / "child_alive"
    # The background child ignores SIGTERM; only the group SIGKILL stops it.
    cmd = f"(trap '' TERM; sleep 3; touch {marker}) & sleep 30"
    assert launcher.run("slow", cmd, tmp_path, tmp_path / "logs", timeout_s=1) is None
    time.sleep(3.5)
    assert not marker.exists(), "background child survived the timeout"
    assert launcher.run("quick", "true && exit 4", tmp_path, tmp_path / "logs", timeout_s=10) == 4
    assert launcher.run("echo", "echo a; echo b", tmp_path, tmp_path / "logs", timeout_s=10) == 0
    assert (tmp_path / "logs" / "echo.log").read_text() == "a\nb\n"


def test_resumed_execution_is_charged_once(repo):
    class CrashAfterQueue(FakeLauncher):
        crashed = False

        def run(self, label, argv, cwd, log_dir, timeout_s, env=None):
            if label == "queue" and not self.crashed:
                self.crashed = True
                raise KeyboardInterrupt  # driver killed mid-queue
            return super().run(label, argv, cwd, log_dir, timeout_s, env)

    fake = CrashAfterQueue()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    d.approve(None)
    with pytest.raises(KeyboardInterrupt):
        d.run(now_mode=True)
    root = d.research / "questions" / "01-root"
    assert research.remaining_budget(d.research, root) == 1
    d2 = research.Driver(research=d.research, repo=repo, launcher=fake, now=d.now)
    fake.driver = d2
    assert d2.run(now_mode=True) == 0
    assert research.remaining_budget(d.research, root) == 1  # not charged twice


def test_leftover_launch_is_killed_on_resume(repo):
    fake = FakeLauncher()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    log_dir = d.task_dir() / "logs"
    log_dir.mkdir()
    orphan = subprocess.Popen(["sleep", "60"], start_new_session=True)
    (log_dir / "prepare-9.pid").write_text(str(orphan.pid))
    d.state["launch"] = {"label": "prepare-9", "log_dir": str(log_dir)}
    d.save()
    d.reconcile()
    assert orphan.wait(timeout=15) != 0
    assert "launch" not in d.state


def test_crash_during_cleanup_resumes_cleanup(repo):
    fake = FakeLauncher()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    d.approve(None)
    original = d.run_cleanup

    def crash(_cleanup):
        raise KeyboardInterrupt

    d.run_cleanup = crash
    with pytest.raises(KeyboardInterrupt):
        d.run(now_mode=True)
    assert "cleanup" in d.state and d.state["phase"] == "propose"
    d.run_cleanup = original
    wt = Path(d.state["cleanup"]["worktree"])
    assert wt.exists()
    d.run(now_mode=True)
    assert not wt.exists() and "cleanup" not in d.state
    assert d.state["phase"] == research.AWAITING


def test_queue_not_started_after_deadline(repo):
    fake = FakeLauncher()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    d.approve(None)
    d.state.update(phase="execute", worktree=str(repo),
                   commit=research.git("rev-parse", "HEAD", cwd=repo))
    d.deadline = d.now() - dt.timedelta(minutes=1)
    with pytest.raises(research.Stop):
        d.phase_execute()
    assert "queue" not in fake.calls
