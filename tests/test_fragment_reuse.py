from copy import deepcopy

import pytest

from experiments.chem_tape.comparison_gate_bank import load_training
from experiments.chem_tape.fragment_operator import BlockOperator
from experiments.chem_tape.fragment_reuse_run import (
    ARMS,
    CORPORA,
    target_ids,
    pinned_history,
    schedule,
    smoke_schedule,
    check_seeds,
    admit,
)
from experiments.chem_tape.fragment_reuse_report import route, report
from experiments.chem_tape.then_addition_bank import load


def fixtures():
    bank, _ = load_training()
    ta, _ = load()
    return target_ids(bank, ta), pinned_history()[0]


def test_frozen_schedules_coverage_pairing_and_seed_exclusion():
    ids, history = fixtures()
    full, fallback, smoke = (
        schedule(ids, 16),
        schedule(ids, 12),
        smoke_schedule(history),
    )
    assert len(full) == 15360 and len(fallback) == 12288 and len(smoke) == 96
    assert {r["corpus"] for r in smoke} == set(CORPORA)
    assert {r["arm"] for r in full} == set(ARMS)
    for phase, n in [("then_addition", 4096), ("holdout", 1024)]:
        assert len([r for r in full if r["phase"] == phase and r["arm"] == "C"]) == n
    assert {tuple(r.items()) for r in fallback} <= {tuple(r.items()) for r in full}
    check_seeds(full, smoke, history["historical_seeds"])
    with pytest.raises(ValueError, match="overlap"):
        check_seeds(full, smoke, [full[0]["seed"]])
    bad = deepcopy(full)
    bad[0]["cell"] = "wrong"
    with pytest.raises(ValueError, match="collision"):
        check_seeds(bad, smoke, [])


def test_admission_only_timing_changes_seed_count():
    _, history = fixtures()
    rows = [
        dict(r, seconds=6, solved=False, evaluations=524288)
        for r in smoke_schedule(history)
    ]
    a = admit(rows, 120, 10)
    assert a["selected_seeds"] == 16
    for r in rows:
        r["solved"] = True
    assert admit(rows, 120, 10)["selected_seeds"] == 16
    for r in rows:
        r["seconds"] = 7.2
    assert admit(rows, 120, 10)["selected_seeds"] == 12
    for r in rows:
        r["seconds"] = 8.5
    assert not admit(rows, 120, 10)["admitted"]
    assert not admit([dict(r, seconds=1) for r in rows], 1801, 10)["admitted"]
    with pytest.raises(ValueError, match="incomplete"):
        admit(rows[:-1], 120, 10)


def stat(point, lo, hi):
    return dict(speed_ratio=point, interval_95=[lo, hi])


@pytest.mark.parametrize(
    "fw,fc,want",
    [
        (stat(1.2, 1.1, 1.3), stat(0.9, 0.8, 0.99), "harm_ends_cross_shape_expansion"),
        (stat(0.9, 0.8, 0.99), stat(1.5, 1.3, 1.7), "harm_ends_cross_shape_expansion"),
        (
            stat(1.10, 1.01, 1.21),
            stat(1.3, 1.1, 1.5),
            "repertoire_earns_acquisition_review",
        ),
        (stat(1.08, 1.01, 1.16), stat(1.3, 1.1, 1.5), "unresolved"),
        (
            stat(1.01, 0.94, 1.09),
            stat(1.3, 1.1, 1.5),
            "no_worthwhile_library_increment",
        ),
        (stat(1.1, 1, 1.21), stat(1.3, 1.1, 1.5), "unresolved"),
        (stat(1.12, 1.01, 1.24), stat(1.1, 0.95, 1.27), "unresolved"),
    ],
)
def test_approved_rule_order(fw, fc, want):
    assert route({"F/W": fw, "F/C": fc}) == want


def test_report_banks_separate_complete_roster_and_arithmetic_repayment(tmp_path):
    ids, _ = fixtures()
    roster = schedule(ids, 12)
    operator = BlockOperator("C", [], 0).stats
    rows = []
    for r in roster:
        # Primary F equals W; reference F large gain must not change decision.
        value = 256 if r["phase"] == "holdout" and r["arm"] == "F" else 512
        rows.append(
            dict(
                r,
                solved=True,
                evaluations=value,
                cap=524288,
                seconds=value / 256,
                operator=deepcopy(operator),
                solver=[0] * 32,
                curve=[[256, 32, 8]],
            )
        )
    libs = {tid: dict(fragments=[dict(tokens=[1, 2, 3])]) for tid in CORPORA}
    p = dict(
        admission=dict(selected_seeds=12, projected_seconds=600),
        extraction_cost=dict(worker_seconds=100, wall_seconds=10),
        shared_corpus_collection=dict(worker_seconds=1000),
        resolution_cost=dict(
            workers=10,
            reporting_queue_seconds=600,
            agent_hours=3,
            source_collection_worker_seconds_per_corpus=100,
            library_worker_seconds_per_corpus=5,
            historical_C_fit_worker_seconds_per_corpus=1,
        ),
    )
    result = report(tmp_path, rows, roster, libs, p)
    assert result["decision"] == "no_worthwhile_library_increment"
    assert result["banks"]["then_addition"]["comparisons"]["F/W"]["df"] == 15
    assert result["banks"]["holdout"]["comparisons"]["F/W"][
        "speed_ratio"
    ] == pytest.approx(2)
    assert (
        result["banks"]["then_addition"]["repayment"]["comparisons"]["F/W"][
            "searches_to_repay_all16_libraries"
        ]
        is None
    )
    assert (
        result["banks"]["holdout"]["repayment"]["comparisons"]["F/W"][
            "searches_to_repay_all16_libraries"
        ]
        == 100
    )
    assert (tmp_path / "then_addition_diagnostics.png").stat().st_size > 1000
    assert (tmp_path / "holdout_diagnostics.png").stat().st_size > 1000
    with pytest.raises(ValueError, match="incomplete"):
        report(tmp_path, rows[:-1], roster, libs, p)
    altered = deepcopy(rows)
    altered[0]["phase"] = "holdout"
    with pytest.raises(ValueError, match="metadata"):
        report(tmp_path, altered, roster, libs, p)


def test_fixture_whole_library_and_replay_rosters():
    history, libraries = pinned_history()
    assert set(libraries) == set(CORPORA)
    assert all(
        len(lib["fragments"]) == 32 and lib["held_out_cell"] is None
        for lib in libraries.values()
    )
    replays = [r for p in history["history"].values() for r in p["replays"]]
    assert len(replays) == 16 and {r["corpus"] for r in replays} == set(CORPORA)
