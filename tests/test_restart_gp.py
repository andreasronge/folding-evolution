"""Restart stopping/accounting, seed isolation and paired scientific inference."""

import copy
import json
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.chem_tape import restart_gp_run as run
from experiments.chem_tape import restart_gp_report as report


@pytest.fixture(scope="module")
def saved():
    return run.load_saved()


def test_seed_sets_and_grid_counts(saved):
    data, targets = saved
    old, _ = run.historical(data, targets)
    score, stage, validation = run.schedules(data["banks.json"], targets)
    audit = run.audit(score, stage, validation, data, old, targets)
    assert audit["admitted"]
    assert all(not v for v in audit["overlaps"].values())
    for f in ("DG", "TS"):
        assert [
            sum(m["family"] == f and m["arm"] == a for m in score) for a in run.ARMS
        ] == [768, 768, 384]
    broken = copy.deepcopy(score)
    broken[0]["seeds"][0] = validation[0]["seeds"][0]
    assert not run.audit(broken, stage, validation, data, old, targets)["admitted"]
    broken = copy.deepcopy(score)
    broken[0]["seeds"][0] += 1
    assert not run.audit(broken, stage, validation, data, old, targets)["admitted"]


@pytest.mark.parametrize("solve_on,expected", [(0, 1), (3, 4), (None, 8)])
def test_attempt_stopping_and_accounting(saved, monkeypatch, solve_on, expected):
    data, targets = saved
    _, _, validation = run.schedules(data["banks.json"], targets)
    m = validation[0]
    seen = []

    def execute(e):
        seen.append(e["meta"]["seed"])
        solved = len(seen) - 1 == solve_on
        return dict(
            solved=solved,
            solver=[2] if solved else None,
            evaluations=256 if solved else 65536,
            worker_seconds=0.0,
        )

    monkeypatch.setattr(run.ordinary, "execute", execute)
    result = run.execute(run.envelope(m, data))
    assert seen == m["seeds"][:expected]
    assert result["attempt_count"] == expected
    assert result["evaluations"] == (
        524288 if solve_on is None else solve_on * 65536 + 256
    )
    assert result["solved"] == (solve_on is not None)
    assert result["evaluations"] <= result["cap"]


def test_real_both_engine_first_attempt_and_schedule_replay(saved):
    data, targets = saved
    _, _, validation = run.schedules(data["banks.json"], targets)
    for m in validation[:2]:
        e = run.envelope(m, data, cutoff=512)
        a = run.execute(e)
        direct = run.ordinary.execute(e["first"])
        assert run.deterministic(a["attempts"][0]) == run.deterministic(direct)
        assert run.deterministic(a) == run.deterministic(run.execute(e))
        run.validate_rows([a], [m], data, cutoff=512)
        broken = copy.deepcopy(a)
        broken["evaluations"] -= 256
        with pytest.raises(ValueError, match="accounting"):
            run.validate_rows([broken], [m], data, cutoff=512)
        broken = copy.deepcopy(a)
        broken["attempts"][0]["training_indices"] = [0] * 64
        with pytest.raises(ValueError, match="RNG"):
            run.validate_rows([broken], [m], data, cutoff=512)


def test_determinism_scope_excludes_only_timing():
    assert run.deterministic(
        dict(
            seconds=2,
            worker_seconds=3,
            budget_seconds={"1": 2},
            compile_seconds_scope="cached",
            attempts=[dict(seed=8, seconds=4)],
        )
    ) == dict(compile_seconds_scope="cached", attempts=[dict(seed=8)])


def fake_grid():
    rows = []
    for c in range(8):
        for b in range(24):
            for a in run.ARMS:
                for s in range(2 if a == "F-A8" else 4):
                    rows.append(
                        dict(
                            family="DG",
                            cell=str(c),
                            build=b,
                            repeat=s,
                            arm=a,
                            seeds=[1000 * c + 8 * (4 * b + s) + k for k in range(8)],
                            evaluations=256 * (b + 1) * (1 if a == "R-tree" else 2),
                            solved=True,
                            cap=524288,
                            worker_seconds=1,
                        )
                    )
    return rows


def test_fixed_block_bootstrap_and_failure_charging():
    rows = fake_grid()
    cells = list(map(str, range(8)))
    values = report.grid(rows, "DG", cells, "evaluations")
    blocks = {a: v.mean(axis=(1, 2)) for a, v in values.items()}
    selected = np.random.default_rng(report.BOOT_SEED).integers(
        24, size=(report.DRAWS, 24)
    )
    ratio = blocks["R-tree"][selected].mean(axis=1) / blocks["R-A8"][selected].mean(
        axis=1
    )
    assert report.ci(ratio) == [0.5, 0.5]
    assert np.array_equal(
        values["R-tree"],
        report.grid(list(reversed(rows)), "DG", cells, "evaluations")["R-tree"],
    )
    rows[0].update(solved=False, evaluations=524288)
    assert report.grid(rows, "DG", cells, "evaluations")["R-tree"][0, 0, 0] == 524288
    assert np.exp(
        report.grid(rows, "DG", cells, "geometric")["R-tree"][0, 0, 0]
    ) == pytest.approx(1048576)
    with pytest.raises(ValueError, match="complete"):
        report.grid(rows[:-1], "DG", cells, "evaluations")
    rows[0]["seeds"][0] += 1
    with pytest.raises(ValueError, match="pairing"):
        report.grid(rows, "DG", cells, "evaluations")


def test_queue_owned_metadata_is_allowed_but_prior_experiment_is_refused(tmp_path):
    for name in ("metadata.json", "stdout.log", "stderr.log"):
        (tmp_path / name).write_text("")
    run.require_fresh(tmp_path)
    (tmp_path / "config.json").write_text("{}")
    with pytest.raises(ValueError, match="fresh RUN_DIR"):
        run.require_fresh(tmp_path)


def test_reliability_and_ratio_boundaries():
    assert (
        report.classify([0.6, 0.9], [-0.02, 0.01])["verdict"]
        == "tree_evaluation_win_with_noninferiority"
    )
    assert (
        report.classify([0.6, 0.9], [-0.03, 0.01])["reliability_status"] == "unresolved"
    )
    assert (
        report.classify([0.6, 0.9], [-0.05, -0.04])["reliability_status"]
        == "demonstrated_inferiority_beyond_margin"
    )
    assert report.classify([1, 1.2], [0, 0.1])["verdict"] == "unresolved_cost"
    assert report.classify([1.01, 1.2], [-0.1, 0])["verdict"] == "A8_evaluation_saving"


def test_actual_acquisition_economics_and_unbounded_repayment(monkeypatch):
    monkeypatch.setattr(
        report, "acquisition", lambda *_: dict(evaluations=100, worker_seconds=10)
    )
    selected = np.tile(np.arange(24), (8192, 1))
    values = {
        "evaluations": {
            a: np.full((24, 8, 2 if a == "F-A8" else 4), 30 if a == "R-tree" else 20)
            for a in run.ARMS
        }
    }
    e = report.economics(values, {}, "D", selected)["evaluations"]["R-A8"]
    assert e["repayment_interval95"] == [10, 10]
    assert e["horizons"]["16"]["A8_minus_tree"]["point"] == -60
    values["evaluations"]["R-tree"][:] = 10
    e = report.economics(values, {}, "D", selected)["evaluations"]["R-A8"]
    assert e["repayment_searches"] is None and e["repayment_unbounded"]
    assert e["repayment_interval95"] == [None, None]


def test_smoke_cannot_admit_target_scoring(tmp_path):
    p = dict(admitted=False, smoke=True)
    p["preparation_hash"] = run.digest(p)
    (tmp_path / "preparation.json").write_text(json.dumps(p))
    runner = object.__new__(run.Runner)
    runner.args = SimpleNamespace(preparation=str(tmp_path))
    runner.freeze = {}
    runner.seed_audit = {}
    with pytest.raises(ValueError, match="admitted"):
        runner.load_preparation()


def test_complete_report_artifacts_and_order_invariance(saved, tmp_path):
    data, _ = saved
    rows = fake_grid()
    for row in rows:
        row.update(
            attempt_count=1,
            scheduling_seconds=0,
            attempts=[
                dict(
                    evaluations=row["evaluations"],
                    exact_check_seconds=0,
                    compiled_tokens_evaluated=row["evaluations"] * 10,
                    primitive_case_work=row["evaluations"] * 640,
                    operator={},
                    curve=[[256, 32, 3, 10], [row["evaluations"], 64, 4, 10]],
                    phenotype_diversity_curve=[[256, 5], [row["evaluations"], 2]],
                )
            ],
        )
    cells = list(map(str, range(8)))
    old = {
        "DG.jsonl": [dict(arm="tree", solved=True, evaluations=1024, worker_seconds=1)]
    }
    report.report(
        tmp_path,
        rows,
        data,
        dict(DG=cells),
        old,
        dict(preparation_hash="synthetic"),
        {},
    )
    result = json.loads((tmp_path / "result.json").read_text())
    summary = result["families"]["DG"]
    assert summary["contrasts"]["R-tree/R-A8"]["evaluations"]["interval95"] == [
        0.5,
        0.5,
    ]
    assert summary["decision"]["reliability_noninferiority"]
    assert summary["per_cell"]["0"]["R-tree"]["jobs"] == 96
    assert (
        report.summarize(list(reversed(rows)), data, dict(DG=cells), old)["DG"]
        == summary
    )
    assert (tmp_path / "dynamics.png").stat().st_size > 1000
    assert (tmp_path / "economics.png").stat().st_size > 1000
    assert "historical acquisition" in (tmp_path / "report.md").read_text()


def test_admitted_preparation_reloads_completion_order_and_blocks_tampering(
    tmp_path, monkeypatch
):
    runner = object.__new__(run.Runner)
    runner.args = SimpleNamespace(preparation=str(tmp_path), family="DG")
    runner.freeze = dict(method="synthetic")
    runner.seed_audit = dict(admitted=True)
    runner.stage = []
    runner.score = []
    runner.saved = {}
    runner.out = tmp_path / "score"
    runner.out.mkdir()
    rows = [
        dict(family="DG", cell="c", arm="R-tree", build=i, repeat=0) for i in range(128)
    ]
    normalized = sorted(rows, key=lambda r: str(run.key(r)))
    # Actual attempt semantic/accounting checks have separate real-engine coverage.
    monkeypatch.setattr(
        run, "validate_rows", lambda rs, *_: sorted(rs, key=lambda r: str(run.key(r)))
    )
    (tmp_path / "stage0.jsonl").write_text(
        "\n".join(json.dumps(r) for r in reversed(rows)) + "\n"
    )
    p = dict(
        admitted=True,
        smoke=False,
        freeze=runner.freeze,
        seed_audit=runner.seed_audit,
        validation=dict(passed=True),
        replay=dict(passed=True),
        stage_rows=128,
        DG_projected_seconds=100,
        stage_hash=run.digest(normalized),
    )
    p["preparation_hash"] = run.digest(p)
    (tmp_path / "preparation.json").write_text(json.dumps(p))
    assert runner.load_preparation() == p

    def entered(*_):
        raise RuntimeError("entered score after admission")

    runner.jobs = entered
    with pytest.raises(RuntimeError, match="entered score"):
        runner.score_family()
    rows[0]["build"] = 999
    (tmp_path / "stage0.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n"
    )
    with pytest.raises(ValueError, match="evidence changed"):
        runner.score_family()
