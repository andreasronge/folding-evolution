"""1019: fixed prior law, paired inference and production admission boundaries."""

import copy
import json
from types import SimpleNamespace

import pytest

from experiments.chem_tape import tree_hand_run as run
from experiments.chem_tape import tree_hand_report as report
from experiments.chem_tape import tree_uniform_run as prior
from experiments.chem_tape import restart_gp_run as restart
from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.tree_gp_search import Tree, search


def test_prior_mass_semantics_and_archive():
    from collections import Counter

    entries = run.hand_prior("v2_x4")
    counts = Counter(tuple(e["prefix"]) for e in entries)
    assert len(entries) == 192 and len(counts) == 44
    assert set(counts.values()) == {3, 8}
    assert sum(e["donor_class"] == "P" for e in entries) == 96
    assert sum(e["donor_class"] == "K" for e in entries) == 96
    assert {(i, j) for op, i, j in counts if i < 4 and j < 4} == {
        (i, j) for i in range(4) for j in range(4) if i != j
    }
    assert all((op, j, i) in counts for op, i, j in counts)
    assert all(e["nodes"] == 3 and e["prefix"][0] == 9 for e in entries)
    with pytest.raises(ValueError):
        run.hand_prior("other")
    saved, _ = load_saved()
    saved["banks.json"]["GS"] = prior.prior_run.snapshot("bank.json")
    libs, evidence = run.reconstruct(saved)
    assert evidence["passed"] and evidence["source_jobs"] == 768 and len(libs) == 24
    run.reviewed_methods()


def test_schedule_seeds_and_tamper():
    saved, targets = load_saved()
    gs = prior.prior_run.snapshot("bank.json")
    schedules = run.schedules(gs)
    assert {k: len(v) for k, v in schedules.items()} == dict(
        score=5184, stage=72, smoke=72
    )
    assert run.seed_audit(schedules, saved, targets, gs)["admitted"]
    bad = copy.deepcopy(schedules)
    bad["score"][0]["seeds"][0] += 1
    assert not run.seed_audit(bad, saved, targets, gs)["admitted"]


def test_observer_has_no_search_effect_and_class_totals():
    gs = prior.prior_run.snapshot("bank.json")
    c = next(c for c in gs["screen"]["cells"] if c["id"] == prior.score_cells(gs)[0])
    job = (c, run.seed("test"), 2048, 256, gs["inputs"], 0.5)
    donors = [Tree(tuple(e["prefix"])) for e in run.hand_prior("v2_x4")]
    plain = search(job, force_cap=True, donor_library=donors)
    counts = dict(draws=0, insertions=0, oversize=0)

    def observe(donor, rejected):
        counts["draws"] += 1
        counts["insertions"] += int(not rejected)
        counts["oversize"] += int(rejected)

    observed = search(job, force_cap=True, donor_library=donors, donor_observer=observe)
    assert restart.deterministic(plain) == restart.deterministic(observed)
    assert counts["draws"] == plain["operator"]["library_draws"]
    assert counts["insertions"] == plain["operator"]["library_insertions"]
    assert counts["oversize"] == plain["operator"]["rejected_library"]


@pytest.mark.parametrize(
    "primary,baseline,guard,expected",
    [
        ([0.9, 1.24], [0.4, 0.79], [0, 0], "retained"),
        ([1.26, 1.5], [0.4, 0.7], [0, 0], "learned_increment"),
        ([1, 1.25], [0.4, 0.7], [0, 0], "unresolved"),
        ([0.9, 1.2], [0.4, 0.80], [0, 0], "unresolved"),
        ([0.9, 1.2], [0.4, 0.7], [-0.03, 0], "unresolved"),
        ([1.2, 1.3], [0.4, 0.7], [0, 0], "unresolved"),
    ],
)
def test_registered_decision(primary, baseline, guard, expected):
    assert report.classify(primary, baseline, guard) == expected


def test_smoke_never_authorizes_score(tmp_path):
    p = dict(admitted=True, smoke=True)
    (tmp_path / "preparation.json").write_text(json.dumps(p))
    runner = object.__new__(run.Runner)
    runner.args = SimpleNamespace(preparation=str(tmp_path))
    with pytest.raises(ValueError, match="production preparation"):
        runner.score()


def synthetic():
    gs = prior.prior_run.snapshot("bank.json")
    cells = prior.score_cells(gs)
    rows = []
    for c in cells:
        for b in range(24):
            for r in range(6):
                for a, f in zip(run.ARMS, (1, 0.5, 0.5)):
                    cost = (b + 1) * 256 * f
                    rows.append(
                        dict(
                            family="GS",
                            cell=c,
                            build=b,
                            repeat=r,
                            arm=a,
                            seeds=[b, r],
                            evaluations=cost,
                            worker_seconds=cost / 256,
                            solved=True,
                            attempt_count=1,
                            attempts=[
                                dict(
                                    evaluations=cost,
                                    operator=dict(mutation=1),
                                    curve=[[cost, 64, 1, 10]],
                                    phenotype_diversity_curve=[[cost, 1]],
                                )
                            ],
                        )
                    )
    libs = dict(
        hand=run.hand_prior("v2_x4"),
        TS=[
            dict(
                build=b,
                entries=[],
                acquisition_evaluations=10000,
                acquisition_worker_seconds=100,
                extraction_seconds=1,
                verification_seconds=3,
            )
            for b in range(24)
        ],
    )
    return rows, libs, gs


def test_paired_report_economics_and_plots(tmp_path):
    rows, libs, gs = synthetic()
    report.report(tmp_path, rows, libs, gs, dict(hand_overhead={}), {})
    r = json.loads((tmp_path / "result.json").read_text())
    assert r["decision"] == "retained"
    assert r["comparisons"]["evaluations"]["R-hand/R-TS"]["interval95"] == [1, 1]
    assert r["comparisons"]["evaluations"]["R-hand/R-tree"]["interval95"] == [0.5, 0.5]
    e = r["economics"]["evaluations"]["R-TS/R-hand"]
    assert (
        e["searches_to_repay"] is None and e["bootstrap_positive_saving_fraction"] == 0
    )
    assert e["horizons"]["1"]["total_difference"]["point"] == 10000
    assert (
        r["economics"]["worker_seconds"]["R-TS/R-hand"]["acquisition"]["point"] == 104
    )
    for name in ("dynamics.png", "economics.png", "report.md"):
        assert (tmp_path / name).stat().st_size > 0
    with pytest.raises(ValueError, match="5,184"):
        report.summarize(rows[:-1], libs, gs, dict(hand_overhead={}))


def test_timing_only_admission_and_stop():
    rows, _, _ = synthetic()
    stage = [r for r in rows if r["build"] < 2 and r["repeat"] == 0]
    for r in stage:
        r["solved"] = False
    batch = dict(
        worker_seconds=sum(r["worker_seconds"] for r in stage),
        wall_seconds=sum(r["worker_seconds"] for r in stage) / 10,
    )
    assert run.stage_gate(stage, batch, 100)["admitted"]
    slow = copy.deepcopy(stage)
    for r in slow:
        r["worker_seconds"] = 1000
    assert not run.stage_gate(slow, batch, 100)["admitted"]
    assert not run.stage_gate(stage, batch, 1800)["admitted"]
