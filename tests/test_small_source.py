"""Scientific invariants for sparse acquisition, weighting and pricing."""

from collections import Counter

import numpy as np
import pytest

from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.fragment_operator import BlockOperator
from experiments.chem_tape.solver_corpus_fit import (
    small_source_counts,
    transition_counts,
    fit_context,
)
from experiments.chem_tape.small_source_run import roster, smoke_roster, CORPORA
from experiments.chem_tape.then_addition_bank import load
from experiments.chem_tape.small_source_report import contrast, economics, report


def test_fallback_mass_and_legacy_counts():
    rows = [
        dict(cell="a", solved=True, solver=[1] * 32),
        dict(cell="b", solved=True, solver=[2] * 32),
    ]
    actual, yields = small_source_counts(rows, ["a", "b"])
    legacy, _ = transition_counts(rows, ["a", "b"])
    assert np.array_equal(actual, legacy) and yields == {"a": 1, "b": 1}
    empty, yields = small_source_counts([], ["a", "b"])
    assert empty.sum() == pytest.approx(3200)
    assert np.array_equal(fit_context(empty), tables()["G4"])
    partial, yields = small_source_counts(rows[:1], ["a", "b"])
    assert partial.sum() == pytest.approx(3200) and yields == {"a": 1, "b": 0}
    with pytest.raises(ValueError, match="mismatch"):
        small_source_counts([dict(cell="a", solved=False, solver=[1] * 32)], ["a"])


def test_empty_library_is_opt_in_and_f_matches_w():
    with pytest.raises(ValueError, match="empty"):
        BlockOperator("F", [], 1)
    f = BlockOperator("F", [], 1, empty_fallback=True)
    w = BlockOperator("W", [], 1, empty_fallback=True)
    assert f.arm == w.arm == "W"
    assert f.lengths.tolist() == [3, 4, 5, 6]


def test_block_ordinals_and_timing_coverage():
    ids = load()[0]["selected_ids"]
    for n in (16, 12):
        rows = roster(ids, n)
        assert len(rows) == 16 * 16 * n * 2
        counts = Counter((r["corpus"], r["cell"], r["arm"], r["block"]) for r in rows)
        assert set(counts.values()) == {n // 4}
        assert all(r["block"] == r["seed_ordinal"] % 4 for r in rows)
    smoke = smoke_roster(ids)
    assert len(smoke) == 128
    assert len({(r["corpus"], r["block"], r["arm"]) for r in smoke}) == 128
    assert {r["cell"] for r in smoke} == set(ids)


def test_retention_orientation_and_equal_block_weight():
    rows = []
    for tid in CORPORA:
        for b in range(4):
            # Deliberately unequal counts: block weight, not pooled row weight.
            for s in range(b + 1):
                for method, evaluations in [
                    ("full_F", 100),
                    ("cheap_F", 120 if b < 2 else 80),
                ]:
                    rows.append(
                        dict(
                            corpus=tid,
                            cell="x",
                            seed=b * 10 + s,
                            block=b,
                            method=method,
                            evaluations=evaluations,
                            cap=1000,
                            solved=True,
                        )
                    )
    result = contrast(rows, "full_F", "cheap_F")
    assert result["cost_ratio"] == pytest.approx(np.sqrt((100 / 120) * (100 / 80)))
    assert result["df"] == 15
    for r in rows:
        if r["method"] == "cheap_F":
            r["evaluations"] = 120
    assert contrast(rows, "full_F", "cheap_F")["cost_ratio"] == pytest.approx(100 / 120)


def test_crossover_can_be_initial_win_then_long_run_loss():
    rows = []
    builds = {}
    full = {}
    for tid in CORPORA:
        full[tid] = dict(evaluations=1000, source_worker_seconds=1000)
        for b in range(4):
            builds[f"{tid}|{b}"] = dict(
                acquisition=dict(evaluations=100, source_worker_seconds=100)
            )
            for method, ev in [("cheap_F", 20), ("cheap_W", 25), ("full_F", 10)]:
                rows.append(
                    dict(
                        corpus=tid,
                        block=b,
                        method=method,
                        evaluations=ev,
                        seconds=ev,
                        solved=True,
                    )
                )
    p = dict(
        full_acquisition=full,
        validation=dict(historical_replay=dict(calibration={"F": 1, "W": 1, "G4": 1})),
    )
    g4 = [dict(evaluations=30, seconds=30, solved=True)] * 4
    result = economics(rows, builds, p, g4)
    for unit in ("evaluations", "worker_seconds"):
        comp = result[unit]["comparisons"]["cheap_F_vs_full_F"]
        assert comp["crossover_N"] == pytest.approx(90)
        assert comp["crossover_direction"] == "cheap_loses_after"
        assert comp["initially_cheaper"] and not comp["eventually_cheaper"]
        assert result[unit]["arithmetic_means"]["cheap_W"]["A"] == 100
    with pytest.raises(ValueError, match="incomplete"):
        report(None, [], [dict(corpus="BE1", cell="x", seed=1, arm="F")], {}, p, [], g4)


def test_complete_reporting_recovers_identical_data_retention(tmp_path):
    # Exercise all report/grouping/plot paths using frozen recorded data, no searches.
    from experiments.chem_tape.small_source_run import references
    from experiments.chem_tape.fragment_report import row_key

    refs, g4, _, _ = references()
    indexed = {row_key(r): r for r in refs}
    schedule = roster(load()[0]["selected_ids"], 16)
    rows = [dict(indexed[row_key(meta)], **meta) for meta in schedule]
    acquisition = dict(evaluations=100, source_worker_seconds=100)
    builds = {
        f"{tid}|{b}": dict(
            acquisition=acquisition,
            yields={},
            empty_cells=[],
            library=dict(fragments=[]),
        )
        for tid in CORPORA
        for b in range(4)
    }
    prep = dict(
        full_acquisition={tid: acquisition for tid in CORPORA},
        validation=dict(historical_replay=dict(calibration={"F": 1, "W": 1, "G4": 1})),
        admission=dict(selected_seeds=16, projected_seconds=100),
    )
    result = report(tmp_path, rows, schedule, builds, prep, refs, g4)
    assert result["primary"]["rho"]["cost_ratio"] == pytest.approx(1)
    assert result["primary"]["rho"]["df"] == 15
    assert result["decision"] == "retained"
    assert (tmp_path / "diagnostics.png").exists()
    assert (tmp_path / "cost_curves.png").exists()
    assert all(
        result["per_block"][str(b)]["comparisons"]["rho"]["cost_ratio"]
        == pytest.approx(1)
        for b in range(4)
    )
