"""Safeguards for changed source membership and independent acquisition units."""

from collections import Counter
import time

import numpy as np
import pytest

from experiments.chem_tape.comparison_gate_bank import (
    TRAINING,
    load_training,
    load_replacement_sources,
)
from experiments.chem_tape.fragment_library import extract_windows
from experiments.chem_tape.fragment_run import CORPORA
from experiments.chem_tape.small_source_run import build_source
from experiments.chem_tape.solver_corpus_fit import small_source_counts, fit_context
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.source_replication_run import (
    ARMS,
    CAP,
    Runner,
    admission,
    collection_roster,
    timing_roster,
    references,
)
from experiments.chem_tape.source_replication_report import report
from experiments.chem_tape.two_sum_bank import load
from experiments.chem_tape.two_sum_run import fitted_roster, methods


def test_explicit_loader_preserves_original_contract_and_complete_complement():
    bank, old = load_training()
    replacement, cells = load_replacement_sources()
    assert bank == replacement
    assert set(old) == set(sum(TRAINING.values(), []))
    assert set(cells) == set(sum(bank["split"]["holdouts"].values(), []))
    assert not set(old) & set(cells)
    assert all(set(c) == {"id", "labels"} for c in cells.values())


def test_rosters_independent_sources_and_exact_historical_scoring_keys():
    bank, _ = load_replacement_sources()
    roster = bank["split"]["holdouts"]
    full = collection_roster(roster)
    smoke = collection_roster(roster, True)
    assert len(full) == 768 and len(smoke) == 96
    assert len({r["seed"] for r in full}) == 768
    assert not {r["seed"] for r in full} & {r["seed"] for r in smoke}
    assert set(
        Counter((r["corpus"], r["phase"], r["cell"]) for r in full).values()
    ) == {4}
    assert Counter(r["arm"] for r in full) == {"G4": 512, "F": 256}
    payload, _ = references()
    assert not {r["seed"] for r in full} & set(payload["historical_source_seeds"])
    target, _ = load()
    timing = timing_roster(target["timing_ids"])
    assert len(timing) == 32 and {r["corpus"] for r in timing} == set(CORPORA[:4])
    score = fitted_roster(target["selected_ids"], 4, ARMS)
    assert len(score) == 2048
    historical = {Runner.key(r): r for r in payload["target_rows"] if r["arm"] == "A8"}
    for r in score:
        if r["arm"] == "A8":
            assert historical[Runner.key(r)]["block"] == r["seed_ordinal"] == r["block"]
    assert not {r["seed"] for r in timing} & {r["seed"] for r in score}


def test_legacy_default_is_bit_exact_for_saved_2033_build():
    payload, _ = references()
    bank, cells = load_training()
    rows = payload["legacy_build_rows"]
    rows = rows[:16] + sorted(rows[16:], key=Runner.key)
    indices = np.random.default_rng(0).choice(1331, 96, replace=False).tolist()
    implicit = build_source(("BE1", 0, rows, bank["inputs"], cells, indices))
    explicit = build_source(
        ("BE1", 0, rows, bank["inputs"], cells, indices, TRAINING["BE"])
    )
    old = methods()[0]["builds.json"]["BE1|0|A8"]
    for field in (
        "table",
        "table_hash",
        "library",
        "attempt_keys",
        "attempts_hash",
        "yields",
        "empty_cells",
    ):
        assert implicit[field] == explicit[field] == old[field]


def test_replacement_fallback_and_membership_rejections():
    bank, cells = load_replacement_sources()
    roster = bank["split"]["holdouts"]["BE"]
    counts, yields = small_source_counts([], roster)
    assert not any(yields.values())
    assert np.array_equal(fit_context(counts), tables()["G4"])
    indices = np.random.default_rng(0).choice(1331, 96, replace=False).tolist()
    b = build_source(("BE1", 0, [], bank["inputs"], cells, indices, roster))
    assert set(b["empty_cells"]) == set(roster) and not b["library"]["fragments"]
    wrong = dict(
        corpus="BE1",
        cell=TRAINING["BE"][0],
        seed=1,
        solved=False,
        solver=None,
        evaluations=CAP,
        seconds=1,
    )
    with pytest.raises(ValueError, match="non-training"):
        build_source(("BE1", 0, [wrong], bank["inputs"], cells, indices, roster))
    with pytest.raises(ValueError, match="non-training"):
        extract_windows(
            "BE1",
            [dict(cell=wrong["cell"], tape=[0] * 32, seed=1)],
            bank["inputs"],
            cells,
            indices,
            source_cells=roster,
        )


def test_exclusion_and_leave_one_out_use_explicit_source_cells():
    from experiments.chem_tape.composition_search import outputs

    bank, _ = load_training()
    indices = np.random.default_rng(0).choice(1331, 96, replace=False).tolist()
    tape = [1, 5, 1, 18, 7] + [0] * 27  # sum + max, five active tokens
    cells = {
        "replacement-a": dict(labels=[0] * 1331),
        "replacement-b": dict(
            labels=outputs([tape], bank["inputs"], "v2_rmin_first")[0].tolist()
        ),
    }
    result = extract_windows(
        "BE1",
        [dict(cell=c, seed=i, tape=tape) for i, c in enumerate(cells)],
        bank["inputs"],
        cells,
        indices,
        source_cells=list(cells),
    )
    assert set(result["libraries"]) == {"BE1|replacement-a", "BE1|replacement-b"}
    assert all(not library["fragments"] for library in result["libraries"].values())
    dropped = result["whole_corpus"]["dropped_padded_solvers"]
    assert {tuple(r["tokens"]): r["solves"] for r in dropped} == {
        (1, 5, 1, 18, 7): ["replacement-b"],
        (1, 5, 1): ["replacement-a"],
    }
    assert all(
        set(f["source_cells"]) == set(cells)
        for f in result["whole_corpus"]["fragments"]
    )


@pytest.mark.parametrize(
    "seconds,expected", [(20, ["A8", "S8"]), (40, ["A8"]), (80, None)]
)
def test_timing_only_fallback_preserves_all_builds_and_actual_deadline(
    seconds, expected
):
    bank, _ = load()
    rows = [dict(r, seconds=seconds) for r in timing_roster(bank["timing_ids"])]
    now = time.time()
    a = admission(rows, 32 * seconds / 10, 300, 10, now + 20000, now)
    assert (a["selected"]["arms"] if a["selected"] else None) == expected
    assert not admission(rows, 32 * seconds / 10, 300, 10, now - 1, now)["admitted"]
    assert not admission(rows, 32 * seconds / 10, 2300, 10, now + 20000, now)[
        "admitted"
    ]


def test_complete_report_propagates_shared_G4_and_single_build_costs(tmp_path):
    payload, _ = references()
    bank, _ = load()
    schedule = fitted_roster(bank["selected_ids"], 4, ARMS)
    old = {Runner.key(r): r for r in payload["target_rows"] if r["arm"] == "A8"}
    rows = [dict(old[(r["corpus"], r["cell"], r["seed"], "A8")], **r) for r in schedule]
    builds = {
        f"{tid}|{m}": dict(
            yields={},
            empty_cells=[],
            library=dict(fragments=[]),
            table_hash="test",
            acquisition=dict(
                evaluations=100,
                source_worker_seconds=1,
                intermediate_overhead_seconds=2 if m == "A8" else 0,
            ),
        )
        for tid in CORPORA
        for m in ARMS
    }
    prep = dict(
        admission=dict(selected=dict(arms=list(ARMS))),
        validation=dict(G4_time_calibration=1),
    )
    result = report(tmp_path, rows, schedule, builds, prep, payload["target_rows"])
    assert result["delta"]["cost_ratio"] == pytest.approx(1)
    assert result["delta"]["df"] == 15
    assert result["sigma"]["cost_ratio"] == pytest.approx(1)
    assert result["primary"]["interval_95"][0] < result["primary"]["interval_95"][1]
    assert result["economics"]["worker_seconds"]["acquisition_mean"]["A8"] == 3
    assert result["economics"]["worker_seconds"]["acquisition_mean"]["S8"] == 1
    assert (tmp_path / "cost_curves.png").exists()
    with pytest.raises(ValueError, match="incomplete"):
        report(tmp_path, rows[:-1], schedule, builds, prep, payload["target_rows"])
