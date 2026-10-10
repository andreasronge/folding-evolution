"""Semantics, isolation and uncertainty tests for the crossed comparison."""

from collections import Counter
import copy
import itertools
import time

import numpy as np
import pytest

from experiments.chem_tape.branch_sum_bank import roster, maximum_clique, validate_bank
from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import (
    semantic_outputs,
    roster as dg_roster,
)
from experiments.chem_tape.family_preference_run import (
    load_dg,
    load_ts,
    schedules,
    cross_alias_check,
)
from experiments.chem_tape.family_preference_report import summarize, economics


def test_ts_canonical_reference_production_and_gross_operation_counts():
    cells = roster()
    assert len(cells) == 216
    xs = inputs_for("D625")
    programs = [c["canonical"] for c in cells]
    assert np.array_equal(outputs(programs, xs, "v2_x4"), [c["labels"] for c in cells])
    assert np.array_equal(semantic_outputs(programs, xs), [c["labels"] for c in cells])
    assert all(
        len(p) == 16
        and Counter(p)[1] == 6
        and Counter(p)[7] == 2
        and Counter(p)[8] == 1
        and Counter(p)[17] == 1
        for p in programs
    )
    assert Counter(programs[0])[1] == Counter(dg_roster()[0]["canonical"])[1]


def test_exact_clique_against_brute_force_and_deadline():
    rng = np.random.default_rng(1717)
    for _ in range(10):
        cells = [
            dict(id=str(i), labels=rng.integers(2, size=10).tolist()) for i in range(10)
        ]
        best = 0
        for n in range(1, 11):
            for subset in itertools.combinations(cells, n):
                if all(
                    5 * sum(x == y for x, y in zip(a["labels"], b["labels"])) < 40
                    for a, b in itertools.combinations(subset, 2)
                ):
                    best = n
                    break
        chosen = maximum_clique(cells)
        assert len(chosen) == best
        assert chosen == maximum_clique(cells)
    with pytest.raises(TimeoutError):
        maximum_clique(cells, time.monotonic() - 1)


def test_frozen_bank_screen_coverage_and_reject_alias_overlap():
    ts = load_ts()
    validate_bank(ts)
    assert ts["maximum_separated"] == 108
    assert sum(c["retained"] for c in ts["screen"]["cells"]) == 192
    for kind in ("overlap", "shortscreen", "alias"):
        bank = copy.deepcopy(ts)
        if kind == "overlap":
            bank["split"]["protected"][0] = bank["split"]["source"][0]
        if kind == "shortscreen":
            bank["screen"]["max_depth"] = 8
        if kind == "alias":
            next(
                c for c in bank["screen"]["cells"] if c["id"] == bank["clique_ids"][0]
            )["best_matches"] = 500
        with pytest.raises(ValueError):
            validate_bank(bank)


def test_complete_dg_cohort_fresh_seeds_rosters_and_no_source_aliases():
    dg, saved, targets, _ = load_dg()
    ts = load_ts()
    banks = dict(DG=dg, TS=ts)
    assert len(saved["builds.json"]) == 24 and len(targets) == 8
    source, calibration, target = schedules(banks, targets)
    assert len(source) == 768 and len(calibration) == 96 and len(target) == 2304
    for arm in ("D", "T"):
        assert {r["build"] for r in calibration if r["arm"] == arm} == set(range(24))
    assert not {r["cell"] for r in source} & {r["cell"] for r in target}
    ss, sc, st = schedules(banks, targets, smoke=True)
    assert not {r["cell"] for r in ss + sc + st} & {r["cell"] for r in target}
    assert not {r["seed"] for r in ss + sc + st} & {
        r["seed"] for r in source + calibration + target
    }
    old = dg["split"]["source"]
    assert not {r["cell"] for r in target} & set(old)
    for cid in targets + ts["split"]["protected"]:
        rs = [r for r in target if r["cell"] == cid]
        assert all(
            {r["seed"] for r in rs if r["arm"] == a}
            == {r["seed"] for r in rs if r["arm"] == "G4"}
            for a in ("D", "T")
        )
    cross_alias_check(
        banks,
        targets + ts["split"]["protected"],
        saved["first.jsonl"] + saved["adaptive.jsonl"],
    )
    with pytest.raises(ValueError):
        cross_alias_check(banks, [old[0]], [])


def structured_rows(dg_D=1024, dg_T=4096, ts_D=4096, ts_T=1024, variable=False):
    rows = []
    for f in ("DG", "TS"):
        for c in range(8):
            for i in range(48):
                for a in ("G4", "D", "T"):
                    ev = (
                        32768
                        if a == "G4"
                        else {
                            "DG": {"D": dg_D, "T": dg_T},
                            "TS": {"D": ts_D, "T": ts_T},
                        }[f][a]
                    )
                    if variable and a == "D" and f == "DG":
                        ev = 256 * 2 ** (i // 2 % 10)
                    rows.append(
                        dict(
                            family=f,
                            cell=f + str(c),
                            ordinal=i,
                            build=i // 2,
                            arm=a,
                            seed=1200000 + (c + 8 * (f == "TS")) * 1000 + i,
                            solved=True,
                            evaluations=ev,
                            cap=524288,
                            seconds=1,
                        )
                    )
    return rows


def test_interaction_direction_usefulness_and_constant_advantage():
    s = summarize(structured_rows(), 24, draws=64)
    assert np.isclose(s["ratios"]["I"]["point"], 4)
    assert s["decision"]["family_specific_acquisition_candidate"]
    dominant = summarize(structured_rows(ts_D=1024, ts_T=1280), 24, draws=64)
    assert dominant["ratios"]["I"]["point"] > 1.5
    assert dominant["decision"]["dominant_bias"] == "D"
    assert dominant["decision"]["dominant_bias_with_interaction"]
    constant = summarize(structured_rows(ts_D=1024, ts_T=4096), 24, draws=64)
    assert np.isclose(constant["ratios"]["I"]["point"], 1)
    harmful = summarize(
        structured_rows(dg_D=65536, dg_T=262144, ts_D=262144, ts_T=65536), 24, draws=64
    )
    assert (
        harmful["decision"]["reciprocal"]
        and not harmful["decision"]["own_family_useful"]
    )
    assert not harmful["decision"]["family_specific_acquisition_candidate"]


def test_between_build_uncertainty_not_pseudoreplicated_across_cells():
    s = summarize(structured_rows(variable=True), 24, draws=1024)
    lo, hi = s["ratios"]["I"]["interval95"]
    assert hi / lo > 1.4
    with pytest.raises(ValueError):
        summarize(structured_rows()[:-1], 24, draws=4)
    rows = structured_rows()
    rows[0]["seed"] += 1
    with pytest.raises(ValueError):
        summarize(rows, 24, draws=4)
    capped = structured_rows()
    for r in capped:
        r.update(solved=False, evaluations=524288)
    s = summarize(capped, 24, draws=8)
    assert np.isclose(s["ratios"]["I"]["point"], 1)
    assert not s["decision"]["shared_bias_candidate"]


def test_arithmetic_acquisition_once_per_deployment_and_no_savings():
    builds = {
        a: {
            str(b): dict(
                acquisition=dict(
                    evaluations=1000,
                    source_worker_seconds=10,
                    verification_seconds=1,
                    fit_seconds=2,
                    extraction_seconds=3,
                )
            )
            for b in range(24)
        }
        for a in ("D", "T")
    }
    intermediate = copy.deepcopy(builds)
    cost = economics(structured_rows(), builds, intermediate)
    b = cost["per_deployed_build"]["D"]["0"]
    assert b["acquisition"]["worker_seconds"] == 22
    assert (
        b["rosters"]["both"]["acquisition_plus_search_evaluations"]
        == 1000 + 16 * 1024 + 16 * 4096
    )
    assert b["rosters"]["DG"]["repayment_searches"] == 1000 / (32768 - 1024)
    rows = structured_rows(dg_D=32768, ts_D=32768)
    cost = economics(rows, builds, intermediate)
    assert (
        cost["per_deployed_build"]["D"]["0"]["rosters"]["both"]["repayment_searches"]
        is None
    )
