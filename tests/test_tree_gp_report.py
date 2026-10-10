"""Scientific pairing, failure penalties, admission gates and repayment bounds."""

import copy
import numpy as np
import pytest

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.tree_gp_report import (
    classify,
    grid,
    summarize,
    horizon_summary,
    samples,
    report,
)
from experiments.chem_tape.tree_gp_run import choose_mix, project, require_admission


def fake_rows():
    rows = []
    for f in ("DG", "TS"):
        for ci in range(8):
            for b in range(24):
                for s in range(2):
                    for a in ("A8", "tree"):
                        ev = 256 * (1 + (b + ci + s) % 7) * (2 if a == "tree" else 1)
                        rows.append(
                            dict(
                                family=f,
                                cell=f + str(ci),
                                arm=a,
                                build=b,
                                repeat=s,
                                seed=10000 * (f == "TS") + 1000 * ci + 2 * b + s,
                                solved=True,
                                evaluations=ev,
                                cap=524288,
                                worker_seconds=ev / 256,
                            )
                        )
            for s in range(16):
                rows.append(
                    dict(
                        family=f,
                        cell=f + str(ci),
                        arm="G4",
                        build=None,
                        repeat=s,
                        seed=10000 * (f == "TS") + 1000 * ci + 100 + s,
                        solved=True,
                        evaluations=4096,
                        cap=524288,
                        worker_seconds=16,
                    )
                )
    return rows


TARGETS = {f: [f + str(i) for i in range(8)] for f in ("DG", "TS")}


def test_paired_bootstrap_fixed_cells_and_builds():
    rows = fake_rows()
    summary = summarize(rows, TARGETS)
    for f in ("DG", "TS"):
        q = summary["families"][f]["Q"]
        assert q["point"] == pytest.approx(2)
        assert q["interval95"] == pytest.approx([2, 2])
    assert summary["decision"] == "worthwhile_A8_advantage"
    assert summarize(list(reversed(rows)), TARGETS) == summary
    with pytest.raises(ValueError, match="complete"):
        summarize(rows[:-1], TARGETS)
    broken = copy.deepcopy(rows)
    broken[0]["seed"] += 1
    with pytest.raises(ValueError, match="pairing"):
        summarize(broken, TARGETS)
    assert classify([0.2, 0.6]) == "worthwhile_tree_advantage"
    assert classify([0.67, 1.5]) == "within_margin"
    assert classify([1.4, 1.6]) == "unresolved"


def test_failure_penalty_is_excluded_from_actual_economics():
    rows = fake_rows()
    tree = next(r for r in rows if r["arm"] == "tree")
    tree.update(solved=False, evaluations=tree["cap"])
    log_v, _ = grid(rows, "DG", TARGETS["DG"], penalty=2)
    actual, _ = grid(rows, "DG", TARGETS["DG"], metric="evaluations")
    assert np.exp(log_v["tree"][0, 0, 0]) == pytest.approx(2 * tree["cap"])
    assert actual["tree"][0, 0, 0] == tree["cap"]
    log_one, _ = grid(rows, "DG", TARGETS["DG"], penalty=1)
    assert np.exp(log_one["tree"][0, 0, 0]) == pytest.approx(tree["cap"])


def test_repayment_unbounded_and_joint_positive_savings():
    selected, repeats, _ = samples()
    acq = np.full(24, 100.0)
    positive = horizon_summary(acq, np.full((24, 8, 2), 10.0), selected, repeats)
    assert positive["repayment_searches"] == pytest.approx(10)
    assert positive["repayment_interval95"] == pytest.approx([10, 10])
    assert not positive["repayment_unbounded"]
    zero = horizon_summary(acq, np.zeros((24, 8, 2)), selected, repeats)
    assert zero["repayment_unbounded"] and zero["repayment_searches"] is None
    assert zero["repayment_interval95"] == [None, None]
    uncertain = np.full((24, 8, 2), 10.0)
    uncertain[:12] = -9
    uncertain = horizon_summary(acq, uncertain, selected, repeats)
    assert uncertain["mean_savings_per_search"] > 0
    assert uncertain["savings_interval95"][0] < 0
    assert (
        uncertain["repayment_unbounded"]
        and uncertain["repayment_interval95"][1] is None
    )


def calibration_rows():
    return [
        dict(
            family=f,
            crossover=m,
            repeat=s,
            cap=524288,
            evaluations=524288,
            solved=(s < 4),
            worker_seconds=50.0,
            exact_check_seconds=0.01,
            exact_check_max_seconds=0.002,
            curve=[[524288, 63, 10]],
            operator=dict(
                crossover=100, mutation=20, rejected_crossover=5, rejected_mutation=2
            ),
            initialization=dict(rejected=10, attempts=266),
        )
        for f in ("DG", "TS")
        for m in (0.9, 0.5)
        for c in range(8)
        for s in range(8)
    ]


def test_mix_ties_admission_projection_and_low_solve_block():
    rows = calibration_rows()
    mix, _ = choose_mix(rows)
    assert mix == 0.9
    batches = {f: dict(worker_seconds=6400.0, wall_seconds=700.0) for f in ("DG", "TS")}
    replays = [
        dict(family=f, worker_seconds=2.0) for f in ("DG", "TS") for i in range(8)
    ]
    p = project(rows, batches, replays, [], {}, mix)
    assert all(x["admitted"] for x in p.values())
    assert p["DG"]["effective_workers"] == pytest.approx(6400 / 700)
    assert p["DG"]["rates"]["A8"] == 11.7  # never faster than historical anchor
    assert p["DG"]["full_cap_searches"] == 64
    slow = project(
        rows,
        {f: dict(worker_seconds=6400.0, wall_seconds=2000.0) for f in ("DG", "TS")},
        replays,
        [],
        {},
        mix,
    )
    assert not all(x["admitted"] for x in slow.values())
    prep = dict(
        validation=dict(admitted=True),
        seed_audit=dict(admitted=True),
        replay=dict(passed=True),
        projection=p,
        prepare_seconds=1000,
        admitted=True,
        smoke=False,
    )
    prep["preparation_hash"] = digest(prep)
    require_admission(prep)
    bad = copy.deepcopy(prep)
    bad["projection"]["DG"]["chosen_solve_fraction"] = 0.24
    bad.pop("preparation_hash")
    bad["preparation_hash"] = digest(bad)
    with pytest.raises(ValueError, match="gate failed"):
        require_admission(bad)
    bad = copy.deepcopy(prep)
    bad["smoke"] = True
    bad.pop("preparation_hash")
    bad["preparation_hash"] = digest(bad)
    with pytest.raises(ValueError, match="gate failed"):
        require_admission(bad)


def test_report_artifacts_use_complete_synthetic_grid(tmp_path):
    from experiments.chem_tape.component_transfer_run import load_saved

    saved, _ = load_saved()
    rows = fake_rows()
    for r in rows:
        r.update(
            seconds=r["worker_seconds"],
            mean_compiled_length=32.0,
            max_compiled_length=32,
            compiled_length_histogram=[0] * 32 + [r["evaluations"]],
            primitive_case_work=r["evaluations"] * 32 * 64,
            exact_check_seconds=0.001,
            training_perfect_individuals=1,
            unique_shortcuts=0,
            curve=[[256, 62, 10], [r["evaluations"], 64, 8]],
            phenotype_diversity_curve=[[256, 15], [r["evaluations"], 12]],
        )
        if r["arm"] == "tree":
            r.update(
                initialization=dict(attempts=266, rejected=10),
                operator=dict(
                    crossover=100,
                    mutation=10,
                    rejected_crossover=5,
                    rejected_mutation=1,
                ),
                compile_seconds=0.01,
                variation_seconds=0.05,
            )
    prep = dict(
        freeze=dict(targets=TARGETS),
        batches={f: dict(worker_seconds=1.0) for f in ("DG", "TS")},
        calibration_actual_evaluations=10000,
    )
    report(tmp_path, rows, saved, prep, {})
    import json

    result = json.loads((tmp_path / "result.json").read_text())
    assert result["status"] == "complete"
    assert result["development_cost"]["actual_calibration_evaluations"] == 10000
    assert (
        result["economics"]["families"]["DG"]["evaluations"]["mean_savings_per_search"]
        > 0
    )
    assert (tmp_path / "dynamics.png").stat().st_size > 1000
    assert "historical" in (tmp_path / "report.md").read_text()
