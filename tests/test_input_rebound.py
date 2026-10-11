"""Rebinding weights, semantic symmetry, complete schedules and paired estimands."""

import copy
import time

import pytest

from experiments.chem_tape import input_rebound_run as run, rebound_library as lib
from experiments.chem_tape import signed_chain_run as chain
from experiments.chem_tape.tree_gp_search import Tree


@pytest.fixture(scope="module")
def saved():
    return chain.saved_libraries()


def test_consistent_renaming_preserves_duplicate_mass():
    entries = [
        dict(prefix=[9, 0, 0], nodes=3, compiled_length=5),
        dict(prefix=[9, 4, 5], nodes=3, compiled_length=4),
    ]
    expanded = lib.expand(entries)
    assert len(expanded) == 48
    assert sum(e["prefix"] == [9, 0, 0] for e in expanded[:24]) == 6
    assert all(e["prefix"][1] == e["prefix"][2] for e in expanded[:24])
    assert all(e["prefix"] == [9, 4, 5] for e in expanded[24:])
    assert [e["prefix"] for e in expanded if e["permutation"] == [0, 1, 2, 3]] == [
        e["prefix"] for e in entries
    ]
    with pytest.raises(ValueError, match="bijection"):
        lib.rename([0], [0, 0, 1, 2])


def test_full_reference_seed_grid_and_historical_disjointness(saved):
    bank = chain.load_bank()
    full = run.schedules(bank)
    assert len(full) == 8064 and len(run.schedules(bank, 5)) == 6912
    assert {m["cell"] for m in full} == set(run.roster(bank))
    for arm, count in (
        ("R-tree", 576),
        ("R-gate", 576),
        ("R-all", 3456),
        ("R-bind", 3456),
    ):
        assert sum(m["arm"] == arm for m in full) == count
    reference = [tuple(m["seeds"]) for m in full if m["arm"] == "R-tree"]
    assert len(set(reference)) == 576
    assert {s for m in full for s in m["seeds"]} == set(range(20481000, 20508648))
    assert {tuple(m["seeds"]) for m in run.schedules(bank, 5)} <= {
        tuple(m["seeds"]) for m in full
    }
    audit = run.seed_audit(bank, saved[2], saved[3])
    assert audit["admitted"] and len(audit["published_seed_sets"]["smoke"]) == 32
    sets = list(map(set, audit["published_seed_sets"].values()))
    assert all(not a & b for i, a in enumerate(sets) for b in sets[i + 1 :])


def test_saved_production_semantics_multiplicities_and_roster_mass(saved):
    bank = chain.load_bank()
    libraries = saved[0]
    expanded = [lib.expand(library["semantic"]) for library in libraries]
    validation = lib.validate(
        libraries, expanded, bank["inputs"], time.monotonic() + 300
    )
    assert validation["complete"] and validation["slots"] == 24 * sum(
        len(library["semantic"]) for library in libraries
    )
    draws = run.helper_draws(bank, validation)
    for build in range(24):
        rows = [r for r in draws if r["build"] == build]
        assert len(rows) == 24
        assert sum(
            r["arms"]["R-all"]["needed_helper_draw_probability"] for r in rows
        ) == pytest.approx(
            sum(r["arms"]["R-bind"]["needed_helper_draw_probability"] for r in rows)
        )
        supported = validation["per_build"][build]["arms"]["R-bind"]["helper_counts"]
        assert len(supported) == (12 if build == 5 else 24)
    bad = copy.deepcopy(expanded)
    bad[0].pop()
    with pytest.raises(ValueError, match="multiplicity"):
        lib.validate(libraries, bad, bank["inputs"], time.monotonic() + 300)


def test_search_envelopes_ignore_reporting_helper_labels(saved):
    bank = chain.load_bank()
    libraries, identities = saved[:2]
    expanded = [lib.expand(library["semantic"]) for library in libraries]
    frozen = run.freeze(bank, libraries, identities, 6)
    metas = run.schedules(bank, smoke=True)
    jobs = run.envelopes(metas, bank, libraries, expanded, frozen, True)
    assert jobs[0][-1] is None and len(jobs[2][-1]) == 24 * len(jobs[1][-1])
    changed = copy.deepcopy(bank)
    for c in changed["screen"]["cells"]:
        c["helpers"], c["canonical_tree"] = [], []
    assert run.envelopes(metas, changed, libraries, expanded, frozen, True) == jobs
    assert all(set(j[1]) == {"id", "labels"} for j in jobs)
    with pytest.raises(ValueError, match="unapproved"):
        run.envelopes(
            [metas[0] | dict(seeds=[1] * 8)], bank, libraries, expanded, frozen, True
        )


def test_decision_precedence_strict_boundaries_and_timing_rule():
    assert run.classify([0.86, 0.89]) == "material_gain"
    assert run.classify([0.86, 0.9]) == "small_none_or_harm"
    assert run.classify([0.85, 1.1]) == "unresolved"
    assert run.classify([1.01, 1.2]) == "harm"
    assert run.classify([0.7, 0.9]) == "unresolved"
    arms = {
        "R-all": {"worker_seconds": {"mean": 10}},
        "R-bind": {"worker_seconds": {"mean": 13}},
    }
    assert run.timing_selection(arms)["selected_repeats"] == 6
    arms["R-bind"]["worker_seconds"]["mean"] = 13.01
    assert run.timing_selection(arms)["selected_repeats"] == 5


def test_unequal_repeats_primary_reference_pairing_and_economics(saved):
    bank = chain.load_bank()
    libraries, identities = saved[:2]
    frozen = run.freeze(bank, libraries, identities, 5)
    by = {c["id"]: c for c in bank["screen"]["cells"]}
    rows = []
    for m in run.schedules(bank, 5):
        tree = Tree(tuple(by[m["cell"]]["canonical_tree"]))
        # All-repeat bind/all = .5; reference-zero bind/tree = .2.
        multiplier = {
            "R-tree": 20,
            "R-gate": 2,
            "R-all": 16,
            "R-bind": 4 + 2 * m["repeat"],
        }[m["arm"]]
        cost = 256 * multiplier
        rows.append(
            m
            | dict(
                solved=True,
                cap=524288,
                cutoff=65536,
                pop_size=256,
                evaluations=cost,
                worker_seconds=cost / 1000,
                attempts=[
                    dict(
                        seed=m["seeds"][0],
                        solved=True,
                        evaluations=cost,
                        solver_tree=list(tree.prefix),
                        solver=list(tree.program),
                    )
                ],
            )
        )
    draws = [
        dict(build=b, cell=c, arms={"R-all": dict(needed_helpers_present=0)})
        for b in range(24)
        for c in run.roster(bank)
    ]
    data = dict(
        bank=bank,
        libraries=libraries,
        method_freeze=frozen,
        helper_draws=draws,
        rebinding_validation=dict(per_build=[]),
    )
    report = run.summarize(rows, data, 100, 8)
    assert report["contrasts"]["R-bind/R-all"]["evaluations"]["point"] == pytest.approx(
        0.5
    )
    assert report["contrasts"]["R-bind/R-tree"]["evaluations"][
        "point"
    ] == pytest.approx(0.2)
    assert report["contrasts"]["R-gate/R-bind"]["evaluations"][
        "point"
    ] == pytest.approx(0.5)
    assert report["decision"] == "material_gain"
    assert report["R_all_coverage_strata"][0]["units"] == 576
    curve = next(
        c
        for c in report["economics"]
        if c["searches"] == 10 and c["contrast"] == "R-bind/R-all"
    )
    acquisition = sum(library["acquisition_evaluations"] for library in libraries) / 24
    assert curve["numerator_total"] == acquisition + 10 * 256 * 8
    assert curve["denominator_total"] == acquisition + 10 * 256 * 16
    assert not report["validity_checks"]["hard_tier_supported"]
    with pytest.raises(ValueError, match="incomplete"):
        run.summarize(rows[:-1], data, 100, 8)
