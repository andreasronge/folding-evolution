"""Acquisition order, paired reference grouping and accounting regressions for2033."""

from collections import Counter

import numpy as np
import pytest

from experiments.chem_tape.sparse_feedback_run import (
    collection_roster,
    source_allocations,
    roster,
    smoke_roster,
    retained,
    CORPORA,
)
from experiments.chem_tape.sparse_feedback_report import acquisition_price, report
from experiments.chem_tape.then_addition_run import frozen_source
from experiments.chem_tape.then_addition_bank import load
from experiments.chem_tape.small_source_run import references
from experiments.chem_tape.fragment_report import row_key


def test_static_continuation_uses_schedule_order_and_disjoint_keys():
    saved, _ = frozen_source()
    first, static, manifest = source_allocations(saved)
    assert len(first) == len(static) == 64
    assert manifest["disjoint"]
    assert not set(map(tuple, manifest["first"])) & set(map(tuple, manifest["static"]))
    ordered = [
        r["seed"]
        for r in saved["schedule.json"]
        if r["phase"] == "collection"
        and r["corpus"] == "BE1"
        and r["cell"] == first["BE1|0"][0]["cell"]
    ]
    assert [r["seed"] for r in first["BE1|0"][:4]] == ordered[:4]
    assert [r["seed"] for r in static["BE1|0"][:4]] == ordered[16:20]
    assert [r["seed"] for r in static["BE1|3"][:4]] == ordered[28:32]
    damaged = dict(saved)
    first_collection = next(
        i for i, r in enumerate(saved["search.jsonl"]) if r["phase"] == "collection"
    )
    damaged["search.jsonl"] = (
        saved["search.jsonl"][:first_collection]
        + saved["search.jsonl"][first_collection + 1 :]
    )
    with pytest.raises(ValueError):
        source_allocations(damaged)


def test_roster_and_collection_have_approved_grain_and_disjoint_seeds():
    ids = load()[0]["selected_ids"]
    c = collection_roster()
    assert len(c) == 1024 and len({r["seed"] for r in c}) == 1024
    assert set(Counter((r["corpus"], r["block"], r["cell"]) for r in c).values()) == {4}
    for n, total in ((16, 8192), (12, 6144)):
        rs = roster(ids, n)
        assert len(rs) == total
        assert set(
            Counter((r["corpus"], r["block"], r["cell"], r["arm"]) for r in rs).values()
        ) == {n // 4}
        assert all(r["block"] == r["seed_ordinal"] % 4 for r in rs)
        assert not {r["seed"] for r in c} & {r["seed"] for r in rs}
    smoke = smoke_roster(ids)
    assert len(smoke) == 128 and {r["cell"] for r in smoke} == set(ids)


def test_calibration_does_not_scale_current_adaptive_collection_or_double_charge_first():
    a = dict(
        evaluations=100,
        source_worker_seconds=50,
        historical_source_seconds=30,
        current_source_seconds=20,
        verification_seconds=2,
        fit_seconds=3,
        extraction_seconds=4,
        intermediate_overhead_seconds=5,
        continuation_verification_seconds=6,
    )
    assert (
        acquisition_price(a, "evaluations", {"G4": 2}, adaptive=True, intermediate=True)
        == 100
    )
    assert (
        acquisition_price(
            a, "worker_seconds", {"G4": 2}, adaptive=True, intermediate=True
        )
        == 100
    )
    assert acquisition_price(a, "worker_seconds", {"G4": 2}) == 115


def test_full_report_sigma_reference_matching_economics_and_incomplete_rejection(
    tmp_path,
):
    full, g4, _, _ = references()
    frozen, _ = retained()
    idx = {row_key(r): r for r in full}
    schedule = roster(load()[0]["selected_ids"], 12)
    rows = []
    for meta in schedule:
        r = dict(idx[meta["corpus"], meta["cell"], meta["seed"], "F"], **meta)
        r.update(solved=True, evaluations=256 if meta["arm"] == "A8" else 512)
        rows.append(r)
    acquisition = dict(
        evaluations=100,
        source_worker_seconds=10,
        historical_source_seconds=6,
        current_source_seconds=4,
        intermediate_overhead_seconds=2,
    )
    builds = {
        f"{tid}|{b}|{a}": dict(
            acquisition=acquisition,
            yields={},
            empty_cells=[],
            library=dict(fragments=[]),
        )
        for tid in CORPORA
        for b in range(4)
        for a in ("A8", "S8")
    }
    p = dict(
        seed_acquisition={f"{t}|{b}": acquisition for t in CORPORA for b in range(4)},
        full_acquisition={t: acquisition for t in CORPORA},
        admission=dict(
            selected_seeds=12, projected_seconds=100, collection_wall_seconds=10
        ),
        validation=dict(historical_replay=dict(calibration=dict(seed=1, full=1, G4=1))),
    )
    result = report(
        tmp_path, rows, schedule, builds, p, frozen["primary.jsonl"], full, g4
    )
    assert result["primary"]["sigma"]["cost_ratio"] == pytest.approx(2)
    assert result["primary"]["sigma"]["df"] == 15
    assert result["decision"] == "worthwhile_search_increment"
    assert (tmp_path / "cost_curves.png").exists() and (
        tmp_path / "diagnostics.png"
    ).exists()
    econ = result["economics"]["evaluations"]["comparisons"]["A8_vs_S8"]
    assert econ["initial_acquisition_difference"] == 0
    assert econ["arithmetic_search_saving"] == 256
    assert econ["crossover_N"] is None
    assert econ["total_cost_differences"][0]["difference"] == 0
    assert econ["total_cost_differences"][-1]["interval_95"][1] < 0
    for b in range(4):
        assert result["per_block"][str(b)]["sigma"]["cost_ratio"] == pytest.approx(2)
    with pytest.raises(ValueError, match="incomplete"):
        report(
            tmp_path, rows[:-1], schedule, builds, p, frozen["primary.jsonl"], full, g4
        )
    assert np.isfinite(result["primary"]["A8_over_seed_speed"]["cost_ratio"])
