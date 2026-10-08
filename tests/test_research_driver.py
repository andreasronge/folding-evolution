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
        self.fail_critique = False
        self.critiques = ["approve"]
        self.strategy_next = "stop"
        self.infeasible = False
        self.on_queue = None  # called when the queue "runs"
        self.plan_minutes = None  # plan.md's estimated_minutes
        self.allocate_next = "strategy"
        self.proposal_front = ""  # extra proposal frontmatter, e.g. "kind: probe\n"

    def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
        d = self.driver
        td = d.task_dir()
        phase = label.rsplit("-", 1)[0]
        self.calls.append(phase)
        if phase == "propose":
            write(td / "proposal.md", "---\nnode: questions/01-root\ntitle: First\n"
                  f"{self.proposal_front}---\nWhy.\n")
        elif phase == "prepare" and self.infeasible:
            write(td / "infeasible.md", "0 hits in 1M tapes.\n")
        elif phase == "prepare":
            with (Path(cwd) / "exp.py").open("a") as f:  # each repair changes the code
                f.write("print('hi')\n")
            subprocess.run(["git", "add", "-A"], cwd=cwd, check=True)
            subprocess.run(["git", "commit", "-qm", "exp"], cwd=cwd, check=True)
            est = (f"---\nestimated_minutes: {self.plan_minutes}\n---\n"
                   if self.plan_minutes else "")
            write(td / "plan.md", est + "If A then X.\n")
            write(td / "queue.yaml", f"runs:\n  - id: {d.state['task']}-a\n    cmd: echo hi\n")
        elif phase == "critique":
            if self.fail_critique:
                return 1 if self.fail_critique == "exit" else 0
            rec = self.critiques.pop(0) if len(self.critiques) > 1 else self.critiques[0]
            write(td / "critique.md", f"---\nrecommend: {rec}\n---\nFine.\n")
        elif phase == "allocate":
            write(td / "allocation.md", f"---\nnext: {self.allocate_next}\n---\nWhy.\n")
        elif phase == "condense":
            write(d.research / "digest.md", "Short.\n")
        elif phase == "strategy":
            write(td / "strategy.md", f"---\nnext: {self.strategy_next}\n---\nGo on.\n")
        elif phase == "summary":
            prompt = argv[1]
            write(Path(prompt.split("Write ")[1].split(" for the owner")[0]), "Summary.\n")
        elif phase == "review_code":
            write(td / "code_review.md", f"---\nverdict: {self.verdicts.pop(0)}\n---\nok\n")
        elif phase == "queue":
            status = {f"{d.state['task']}-a": {"status": "done", "wall_seconds": 1.0,
                                               "run_dir": "experiments/output/x"}}
            (td / "queue.status.json").write_text(json.dumps(status))
            if self.on_queue:
                self.on_queue()
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

        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            if label.startswith("analyse") and self.fail_once:
                self.fail_once = False
                return None  # timed out
            return super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)

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

        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            if label == "queue" and not self.crashed:
                self.crashed = True
                raise KeyboardInterrupt  # driver killed mid-queue
            return super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)

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
    assert "cleanup" in d.state and d.state["phase"] == research.ACCEPT
    d.run_cleanup = original
    wt = Path(d.state["cleanup"]["worktree"])
    assert wt.exists()
    calls = len(fake.calls)
    d.run(now_mode=True)
    assert not wt.exists() and "cleanup" not in d.state
    assert d.state["phase"] == research.AWAITING
    assert len(fake.calls) == calls  # the written proposal is accepted, not re-asked


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


def test_call_cap_while_proposing_stops_cleanly(repo):
    fake = FakeLauncher()
    d = make_driver(repo, fake, max_agent_calls=0)
    assert d.run(now_mode=True) == 1
    assert d.state["phase"] == "propose" and fake.calls == []
    d.cfg["max_agent_calls"] = 8
    assert d.propose() == 0 and d.state["phase"] == research.AWAITING


def test_queue_edited_after_review_is_refused(repo):
    class EditQueue(FakeLauncher):
        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            code = super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)
            if label.startswith("review_code"):
                with (self.driver.task_dir() / "queue.yaml").open("a") as f:
                    f.write("  - id: sneaky\n    cmd: echo\n")
            return code

    fake = EditQueue()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    d.approve(None)
    assert d.run(now_mode=True) == 1
    assert d.state["phase"] == "execute" and "queue" not in fake.calls


def test_resume_reruns_interrupted_queue_entries(repo):
    class InterruptedOnce(FakeLauncher):
        seen_before: list = []

        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            if label == "queue":
                path = self.driver.task_dir() / "queue.status.json"
                self.seen_before.append(json.loads(path.read_text()) if path.exists() else None)
                if len(self.seen_before) == 1:  # first attempt: killed mid-entry
                    path.write_text(json.dumps({f"{self.driver.state['task']}-a":
                                                {"status": "interrupted"}}))
                    self.calls.append("queue")
                    return None
            return super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)

    fake = InterruptedOnce()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    d.approve(None)
    assert d.run(now_mode=True) == 1 and d.state["phase"] == "execute"
    assert d.run(now_mode=True) == 0
    assert fake.seen_before[1] == {}  # the interrupted entry was cleared for re-running
    task_runs = sorted((d.research / "runs").glob("*/execution.md"))
    assert "| done |" in task_runs[0].read_text()


@pytest.mark.parametrize("outcome", ["exit2", "missing"])
def test_queue_failure_does_not_advance(repo, outcome):
    class BrokenQueue(FakeLauncher):
        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            if label == "queue":
                self.calls.append("queue")
                return 2 if outcome == "exit2" else 0  # "missing": no status written
            return super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)

    fake = BrokenQueue()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    d.approve(None)
    assert d.run(now_mode=True) == 1
    assert d.state["phase"] == "execute" and "analyse" not in fake.calls
    assert not research.git_ok("rev-parse", "--verify", "research/main^{commit}", cwd=repo) or \
        research.git("rev-parse", "research/main", cwd=repo) != d.state["commit"]


def test_critic_reviews_every_proposal_and_is_optional(repo):
    fake = FakeLauncher()
    d = make_driver(repo, fake)
    write(d.research / "roles" / "critic.md", "---\nagent: fake\nmodel: m-critic\n---\nCritic.\n")
    assert d.run(now_mode=True) == 0
    assert fake.calls == ["propose", "critique"] and d.state["phase"] == research.AWAITING
    assert (d.task_dir() / "critique.md").exists()
    assert d.approve(None) == 0
    fake.fail_critique = True  # no critique.md: the proposal still reaches the owner
    assert d.run(now_mode=True) == 0
    assert fake.calls[-2:] == ["decide", "critique"] and d.state["phase"] == research.AWAITING
    assert not (d.task_dir() / "critique.md").exists()


def test_cycle_commits_and_pushes_notes_and_code(repo, tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=repo, check=True)
    fake = FakeLauncher()
    d = make_driver(repo, fake, commit_research=True, push=True)
    assert d.run(now_mode=True) == 0
    first = d.state["task"]
    assert d.approve(None) == 0
    assert d.run(now_mode=True) == 0
    pushed = research.git("ls-remote", "--heads", str(remote), cwd=repo)
    for ref in ("refs/heads/main", "refs/heads/research/main", f"refs/heads/research/{first}"):
        assert ref in pushed
    notes = research.git("ls-tree", "-r", "--name-only", "main", cwd=repo)
    assert f"research/runs/{first}/execution.md" in notes
    assert f"research/runs/{first}/logs/" not in notes
    assert "Rerun:" in (d.research / "runs" / first / "execution.md").read_text()


# -- autonomous mode -------------------------------------------------------


def auto_driver(repo, fake, **cfg):
    d = make_driver(repo, fake, **cfg)
    write(d.research / "roles" / "critic.md", "---\nagent: fake\nmodel: m\n---\nCritic.\n")
    write(d.research / "roles" / "strategist.md", "---\nagent: fake\nmodel: m\n---\nStrat.\n")
    d.sleep = lambda s: None
    return d


def test_auto_runs_cycles_until_the_strategist_stops(repo):
    fake = FakeLauncher(review_verdicts=("pass", "pass"))
    d = auto_driver(repo, fake, strategy_every=2)
    fake.critiques = ["approve"]
    assert d.run_auto(hours=48) == 1  # the strategist said stop: owner needed
    cycle = ["prepare", "review_code", "queue", "analyse", "decide"]
    assert fake.calls == (["propose", "critique"] + cycle + ["critique"] + cycle
                          + ["strategy", "summary"])
    assert (d.task_dir() / "steward_proposal.md").exists()  # kept for the strategist
    info = json.loads(d.run_path.read_text())
    assert info["finished"] and info["cycles"] == 2 and "strategist" in info["reason"]
    assert (d.research / "briefs" / f"{info['id']}-auto-summary.md").exists()


def test_auto_revise_twice_then_strategy_redesigns(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake, strategy_every=9)
    fake.critiques = ["revise", "revise", "revise", "approve"]
    fake.strategy_next = "proposal"
    d.run_auto(hours=48)
    assert fake.calls[:10] == (["propose", "critique"] * 3 + ["strategy", "propose", "critique",
                                                             "prepare"])
    approved = sorted((d.research / "runs").glob("*/approval.md"))
    assert "Approved by the critic" in approved[0].read_text()
    assert len(list((d.research / "runs").glob("*/rejected.md"))) == 3
    ledger = next((d.research / "briefs").glob("*-ledger.md")).read_text()
    assert ledger.count("| sent back |") == 2 and "| to strategy |" in ledger


def test_auto_five_rejections_need_the_owner(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake)
    fake.critiques = ["reject"]
    fake.strategy_next = "proposal"
    assert d.run_auto(hours=48) == 1
    assert fake.calls == (["propose", "critique"] * 3 + ["strategy"] + ["propose", "critique"] * 2
                          + ["summary"])
    assert "owner is needed" in json.loads(d.run_path.read_text())["reason"]


def test_auto_approve_with_notes_runs_and_passes_the_notes_on(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake, strategy_every=1)
    fake.critiques = ["approve_with_notes"]
    d.run_auto(hours=48)
    assert fake.calls[:3] == ["propose", "critique", "prepare"]
    approval = next((d.research / "runs").glob("*/approval.md")).read_text()
    assert "notes" in approval


def test_auto_allows_two_new_roots(repo):
    class RootMaker(FakeLauncher):
        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            if label.startswith("propose"):
                for name in ("02-new", "03-other", "04-third"):
                    question(self.driver.research / "questions" / name, experiments=1)
            return super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)

    fake = RootMaker()
    d = auto_driver(repo, fake)
    assert d.run_auto(hours=48) == 1
    assert fake.calls == ["propose", "summary"]
    assert "3 new root questions" in json.loads(d.run_path.read_text())["reason"]


def test_auto_steward_may_not_raise_a_root_budget(repo):
    class Raiser(FakeLauncher):
        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            if label.startswith("propose"):
                question(self.driver.research / "questions" / "01-root", experiments=9)
            return super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)

    fake = Raiser()
    d = auto_driver(repo, fake)
    assert d.run_auto(hours=48) == 1
    assert "raised outside strategy" in json.loads(d.run_path.read_text())["reason"]


def test_auto_strategist_may_raise_a_root_budget(repo):
    class Granter(FakeLauncher):
        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            if label.startswith("strategy"):
                assert "used 1 of its 40 experiments" in argv[1]
                question(self.driver.research / "questions" / "01-root", experiments=5)
            return super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)

    fake = Granter(review_verdicts=("pass", "pass"))
    d = auto_driver(repo, fake, strategy_every=9)
    question(d.research / "questions" / "01-root", experiments=1)
    fake.strategy_next = "proposal"
    fake.on_queue = lambda: None
    d.run_auto(hours=48)
    # Budget used up → a short allocation, which sends it on to a full review that grants more.
    i = fake.calls.index("strategy")
    assert fake.calls[i - 2:i] == ["decide", "allocate"]
    assert fake.calls[i + 1:i + 4] == ["propose", "critique", "prepare"]
    assert list((d.research / "runs").glob("*/steward_proposal.md"))


def test_auto_allocation_grants_a_block_without_a_full_review(repo):
    class Allocator(FakeLauncher):
        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            if label.startswith("allocate"):
                assert "normally 9" in argv[1]
                question(self.driver.research / "questions" / "01-root", experiments=5)
            return super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)

    fake = Allocator(review_verdicts=("pass", "pass"))
    d = auto_driver(repo, fake, strategy_every=9, auto_max_experiments=2)
    question(d.research / "questions" / "01-root", experiments=1)
    fake.allocate_next = "proposal"
    d.run_auto(hours=48)
    i = fake.calls.index("allocate")
    assert fake.calls[i + 1:i + 3] == ["critique", "prepare"] and "strategy" not in fake.calls
    ledger = next((d.research / "briefs").glob("*-ledger.md")).read_text()
    assert "allocation: granted" in ledger


def test_auto_run_ends_after_its_experiment_limit(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake, strategy_every=9, auto_max_experiments=1)
    assert d.run_auto(hours=48) == 0
    cycle = ["prepare", "review_code", "queue", "analyse", "decide"]
    assert fake.calls == ["propose", "critique"] + cycle + ["summary"]
    info = json.loads(d.run_path.read_text())
    assert info["executed"] and "1 of its experiments" in info["reason"]
    ledger = (d.research / "briefs" / f"{info['id']}-ledger.md").read_text()
    assert "| yes |" in ledger and "Continue." in ledger


def test_infeasible_design_goes_to_decide_uncharged(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake, strategy_every=9, auto_max_experiments=1)
    fake.infeasible = True
    d.run_auto(hours=48)
    assert fake.calls[:4] == ["propose", "critique", "prepare", "decide"]
    assert not list((d.research / "runs").glob("*/execution.md"))
    assert "infeasible" in next((d.research / "briefs").glob("*-ledger.md")).read_text()


def test_auto_finished_queue_is_analysed_after_the_deadline(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake, strategy_every=9)
    fake.on_queue = lambda: setattr(d, "deadline", dt.datetime(2000, 1, 1))
    d.run_auto(hours=48)
    assert fake.calls[-4:] == ["queue", "analyse", "decide", "summary"]
    assert json.loads(d.run_path.read_text())["reason"] == "its time was used up"


def test_auto_retries_a_failed_agent(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake, strategy_every=1)
    fake.fail_critique = "exit"
    sleeps = []
    d.sleep = lambda s: (sleeps.append(s), setattr(fake, "fail_critique", False))
    d.run_auto(hours=48)
    # One failed critique at proposal time, one on the auto-approval retry, then a sleep.
    assert sleeps == [600]
    assert fake.calls[:5] == ["propose", "critique", "critique", "critique", "prepare"]


def test_auto_run_resumes_with_its_deadline(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake)
    (d.research / "STOP").write_text("")
    d.run_auto(hours=1)
    assert json.loads(d.run_path.read_text())["finished"]
    info = {"id": "x", "started": "2026-10-04T23:00:00", "deadline": "2026-10-04T23:00:00",
            "roots_at_start": ["01-root"], "cycles": 3}
    d.run_path.write_text(json.dumps(info))
    (d.research / "STOP").unlink()
    d.run_auto(hours=48)  # resumes run x, whose deadline has passed
    assert json.loads(d.run_path.read_text())["reason"] == "its time was used up"


def test_queue_over_the_cap_goes_back_to_the_researcher(repo):
    fake = FakeLauncher()
    d = make_driver(repo, fake, max_queue_hours=1)  # the fake's entry has the 4 h default
    d.run(now_mode=True)
    task = d.state["task"]
    d.approve(None)
    d.run(now_mode=True)
    assert fake.calls == ["propose", "prepare", "prepare", "decide"]  # one repair, then blocked
    assert "1 h cap" in (d.research / "runs" / task / "driver_feedback.md").read_text()


def test_failed_critic_verdict_is_discarded(repo):
    class HalfCritic(FakeLauncher):
        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            code = super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)
            return 1 if label.startswith("critique") else code  # wrote a verdict, then failed

    fake = HalfCritic()
    d = auto_driver(repo, fake)
    d.run_auto(hours=48)
    assert "approve" not in fake.calls and "prepare" not in fake.calls
    assert not (d.task_dir() / "critique.md").exists()


def test_missing_proposal_reruns_the_steward(repo):
    class Forgetful(FakeLauncher):
        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            if label == "propose-1":
                self.calls.append("propose")
                return 0  # exits cleanly without writing proposal.md
            return super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)

    fake = Forgetful()
    d = auto_driver(repo, fake, strategy_every=1)
    d.run_auto(hours=48)
    assert fake.calls[:3] == ["propose", "propose", "critique"]


def test_critique_from_an_interrupted_critic_is_redone(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake, strategy_every=1)
    d.run(now_mode=True)  # manual: proposal + critique, awaiting approval
    d.state.pop("critique_done")  # as if the critic was killed after writing a verdict
    d.save()
    fake.critiques = ["reject"]
    d.run_auto(hours=48)
    assert fake.calls[:3] == ["propose", "critique", "critique"]  # verdict not reused


def test_auto_pool_ends_the_run_before_more_strategy(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake, strategy_every=1, auto_max_experiments=1)
    assert d.run_auto(hours=48) == 0
    assert "strategy" not in fake.calls


def test_ledger_replaces_a_retried_row(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake)
    d.run_info = {"id": "r"}
    d.auto = True
    d.ledger(["t1", "n", "approve", "pass", "1", "yes", "A", "first"])
    d.ledger(["t1", "n", "approve", "pass", "1", "yes", "A", "second"])
    text = (d.research / "briefs" / "r-ledger.md").read_text()
    assert text.count("| t1 |") == 1 and "second" in text


def git_t(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def test_note_conflicts_on_the_code_branch_resolve_to_main(repo, tmp_path):
    # A code branch carried a first-pass review; main holds the second pass.
    git_t("branch", "research/main", cwd=repo)
    side = tmp_path / "side"
    git_t("worktree", "add", str(side), "research/main", cwd=repo)
    write(side / "research/notes/code_review.md", "verdict: fail\n")
    git_t("add", "-A", cwd=side)
    git_t("commit", "-qm", "first pass", cwd=side)
    git_t("worktree", "remove", str(side), cwd=repo)
    write(repo / "research/notes/code_review.md", "verdict: pass\n")
    git_t("add", "research/notes/code_review.md", cwd=repo)
    git_t("commit", "-qm", "second pass", cwd=repo)
    fake = FakeLauncher()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    first = d.state["task"]
    d.approve(None)
    d.run(now_mode=True)
    assert "queue" in fake.calls
    kept = research.git("show", f"research/{first}:research/notes/code_review.md", cwd=repo)
    assert kept == "verdict: pass"


def test_code_conflicts_still_block(repo, tmp_path):
    git_t("branch", "research/main", cwd=repo)
    side = tmp_path / "side"
    git_t("worktree", "add", str(side), "research/main", cwd=repo)
    write(side / "src.py", "a = 1\n")
    git_t("add", "-A", cwd=side)
    git_t("commit", "-qm", "code", cwd=side)
    git_t("worktree", "remove", str(side), cwd=repo)
    write(repo / "src.py", "a = 2\n")
    git_t("add", "src.py", cwd=repo)
    git_t("commit", "-qm", "owner code", cwd=repo)
    fake = FakeLauncher()
    d = make_driver(repo, fake)
    d.run(now_mode=True)
    d.approve(None)
    d.run(now_mode=True)
    assert "queue" not in fake.calls
    logs = "".join(f.read_text() for f in (d.research / "runs").glob("*/driver.log"))
    assert "conflicts; resolve by hand" in logs


def test_push_merges_what_the_owner_pushed_meanwhile(repo, tmp_path):
    remote = tmp_path / "remote.git"
    git_t("init", "-q", "--bare", str(remote), cwd=tmp_path)
    git_t("remote", "add", "origin", str(remote), cwd=repo)
    git_t("push", "-q", "origin", "main", cwd=repo)
    other = tmp_path / "laptop"
    git_t("clone", "-q", str(remote), str(other), cwd=tmp_path)
    write(other / "owner.md", "note\n")
    git_t("add", "-A", cwd=other)
    git_t("-c", "user.name=o", "-c", "user.email=o@o", "commit", "-qm", "owner", cwd=other)
    git_t("push", "-q", "origin", "main", cwd=other)
    fake = FakeLauncher()
    d = make_driver(repo, fake, commit_research=True, push=True)
    d.run(now_mode=True)
    d.approve(None)
    d.run(now_mode=True)
    remote_main = research.git("rev-parse", "main", cwd=remote)
    assert remote_main == research.git("rev-parse", "HEAD", cwd=repo)
    assert (repo / "owner.md").exists()


def test_auto_queue_that_would_overrun_the_deadline_waits(repo):
    fake = FakeLauncher()
    fake.plan_minutes = 600
    d = auto_driver(repo, fake, strategy_every=9)
    assert d.run_auto(hours=2) == 0
    assert "queue" not in fake.calls and fake.calls[-1] == "summary"
    info = json.loads(d.run_path.read_text())
    assert "the next run starts it" in info["reason"] and not info["executed"]
    assert d.state["phase"] == "execute"


def test_long_digest_is_condensed_after_decide(repo):
    fake = FakeLauncher()
    d = auto_driver(repo, fake, strategy_every=9, auto_max_experiments=1, digest_max_words=5)
    write(d.research / "digest.md", "one two three four five six\n")
    d.run_auto(hours=48)
    assert fake.calls[fake.calls.index("decide") + 1] == "condense"
    assert (d.research / "digest.md").read_text() == "Short.\n"


def test_probe_allowance_and_queue_cap(repo):
    fake = FakeLauncher()
    fake.proposal_front = "kind: probe\n"
    d = auto_driver(repo, fake, strategy_every=9)
    d.run_info = {"executed": ["a"], "probes": ["a"]}
    assert not d.probe_allowed()
    d.run_info = {"executed": ["a", "b", "c", "d", "e"], "probes": ["a"]}
    assert d.probe_allowed()  # one more after four full experiments
    d.run_info = {"executed": ["a", "b", "c"], "probes": ["a"]}
    assert not d.probe_allowed()


def test_probe_queue_over_its_cap_goes_back(repo):
    fake = FakeLauncher()
    fake.proposal_front = "kind: probe\n"
    d = auto_driver(repo, fake, strategy_every=9, auto_max_experiments=1,
                    probe_max_queue_minutes=30)
    d.run_auto(hours=48)  # the fake queue entry has the default 4 h timeout
    feedback = list((d.research / "runs").glob("*/driver_feedback.md"))
    assert feedback and "probe cap" in feedback[0].read_text()
    assert "queue" not in fake.calls[:fake.calls.index("decide")]


def test_task_bank_exposure_is_told_to_proposer_and_critic(repo):
    fake = FakeLauncher()
    d = make_driver(repo, fake)
    write(d.research / "runs" / "t1" / "proposal.md", "---\nnode: questions/01-root\nbank: b1\n---\n")
    write(d.research / "runs" / "t1" / "execution.md", "# Execution\n")
    write(d.research / "runs" / "t2" / "proposal.md", "---\nnode: questions/01-root\nbank: b1\n---\n")
    assert d.bank_exposure() == {"b1": 1}
    d.run(now_mode=True)
    assert "b1 (1)" in d.bank_note()


def test_digest_check_covers_every_update_since_the_last_check(repo):
    prompts = []

    class Recorder(FakeLauncher):
        def run(self, label, argv, cwd, log_dir, timeout_s, env=None, kill_grace=None):
            prompts.append((label, argv[1]))
            return super().run(label, argv, cwd, log_dir, timeout_s, env, kill_grace)

    fake = Recorder(review_verdicts=("pass", "pass"))
    d = auto_driver(repo, fake, strategy_every=9, auto_max_experiments=2, commit_research=True)
    d.run_auto(hours=48)
    crits = [p for label, p in prompts if label.startswith("critique")]
    assert "Digest check" not in crits[0] and "git log -p -1 " in crits[1]
    summary = next(p for label, p in prompts if label.startswith("summary"))
    assert "## Claim check" in summary and "..HEAD -- research/digest.md" in summary
