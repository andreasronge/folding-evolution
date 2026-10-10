"""Validity checks for the bounded tree implementation and preparation stop."""

import numpy as np
import pytest

from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET
from experiments.chem_tape.tree_gp_search import (
    Tree,
    initialize,
    interpret,
    from_postfix,
    random_tree,
)
from experiments.chem_tape.tree_gp_validate import (
    full_acceptance_probability,
    python_output,
)


def test_order_closure_missing_readouts_and_wrapping():
    conditional = Tree((11, 8, 7, 10, 0, 1))  # else5, then2, X0>X1
    for x in ([], [3], [2, 3], [3, 2], [3, 3]):
        expected = 2 if (x[0] if x else 0) > (x[1] if len(x) > 1 else 0) else 5
        assert interpret(conditional, x) == python_output(conditional, x) == expected
        assert outputs([conditional.program], [x], ALPHABET)[0, 0] == expected
    add = Tree((9, 0, 1))
    x = [2**63 - 1, 1]
    assert interpret(add, x) == outputs([add.program], [x], ALPHABET)[0, 0] == -(2**63)
    assert from_postfix(conditional.program) == conditional
    assert len(Tree((0,)).program) == 2
    for prefix in ((), (9, 0), (0, 1), (12,)):
        with pytest.raises(ValueError):
            Tree(prefix)


def test_subtree_exchange_and_oversize_revert():
    parent = Tree((9, 0, 1))
    donor = Tree((11, 5, 6, 10, 2, 3))
    child, rejected = parent.insert(1, donor, 3)
    assert not rejected and child.prefix == (9, 10, 2, 3, 1)
    oversized = Tree((9,) * 20 + (8,) * 21)  # valid but 41 primitive tokens
    child, rejected = parent.insert(0, oversized)
    assert rejected and child is parent
    rng = np.random.default_rng(22160009)
    for _ in range(100):
        a, b = random_tree(rng, 2), random_tree(rng, 3)
        child, rejected = a.insert(
            int(rng.integers(len(a.prefix))), b, int(rng.integers(len(b.prefix)))
        )
        assert len(child.program) <= 32
        for x in ([0, 1, 2, 3], [4, 3, 2, 1], []):
            assert interpret(child, x) == python_output(child, x)


def test_corrected_initializer_and_mutation_root():
    pop, stats = initialize(np.random.default_rng([22160000, 1]), 256)
    assert all(t.prefix[0] >= 9 and len(t.program) <= 32 for t in pop)
    assert set(stats["bins"]) == {f"{d}/{f}" for d in (1, 2, 3) for f in (True, False)}
    counts = [v["accepted"] for v in stats["bins"].values()]
    assert sum(counts) == 256 and max(counts) - min(counts) == 1
    rng = np.random.default_rng(22160001)
    roots = [random_tree(rng, 3).prefix[0] for _ in range(1000)]
    assert 400 < sum(x < 9 for x in roots) < 600
    assert all(
        random_tree(rng, 3, function_root=True).prefix[0] >= 9 for _ in range(1000)
    )
    assert full_acceptance_probability(2) == pytest.approx(1)
    assert full_acceptance_probability(3) > 0.7
    # All-binary 31-node constant trees; length32 also admits one readout
    # or one deepest-level IF_GT (one extra constant leaf).
    exact = (2 / 3) ** 15 * (4 / 9) ** 16 * (1 + 16 * 5 / 4 + 8 * 0.5 * 4 / 9)
    assert full_acceptance_probability(4) == pytest.approx(exact)


def test_frozen_schedule_size_pairing_and_seed_collision_gate():
    from experiments.chem_tape.component_transfer_run import load_saved
    from experiments.chem_tape.tree_gp_run import schedules

    saved, targets = load_saved()
    calibration, score = schedules(saved["banks.json"], targets, scoring_base=22150000)
    assert len(calibration) == 256 and len(score) == 1792
    overlap = {r["seed"] for r in calibration} & {r["seed"] for r in score}
    assert len(overlap) == 48
    assert min(overlap) == 22150000 and max(overlap) == 22155007
    assert {22160000, 22161000} <= {r["seed"] for r in score}
    from experiments.chem_tape.tree_gp_run import audit_seeds

    audit = audit_seeds(calibration, score)
    assert not audit["admitted"] and not audit["targets_scored"]
    assert audit["calibration_scoring_overlap"] == sorted(overlap)
    assert audit["smoke_scoring_overlap"] == [22160000, 22161000]
    assert (
        audit["implicated_calibration_rows"] == audit["implicated_scoring_rows"] == 96
    )
    for f in ("DG", "TS"):
        assert sum(r["family"] == f for r in calibration) == 128
        for a, n in (("A8", 384), ("tree", 384), ("G4", 128)):
            assert sum(r["family"] == f and r["arm"] == a for r in score) == n
        assert not {r["cell"] for r in calibration if r["family"] == f} & set(
            targets[f]
        )
        tree = {
            (r["cell"], r["build"], r["repeat"]): r["seed"]
            for r in score
            if r["family"] == f and r["arm"] == "tree"
        }
        native = {
            (r["cell"], r["build"], r["repeat"]): r["seed"]
            for r in score
            if r["family"] == f and r["arm"] == "A8"
        }
        assert tree == native and len(set(tree.values())) == 384


def test_corrected_seed_schedule_and_historical_audit():
    from experiments.chem_tape.tree_gp_run import (
        schedules,
        audit_seeds,
        historical_seeds,
    )
    from experiments.chem_tape.component_transfer_run import load_saved

    saved, targets = load_saved()
    cal, score = schedules(saved["banks.json"], targets)
    old = historical_seeds(saved)
    audit = audit_seeds(cal, score, old)
    assert audit["admitted"] and audit["intended_pairing_valid"]
    assert len(old) == 1544
    assert min(r["seed"] for r in score) == 22180000
    assert max(r["seed"] for r in score) == 22195115
    assert not audit_seeds(cal, score, old | {22180000})["admitted"]
    assert not audit_seeds(cal, score[:-1], old)["admitted"]
    broken = [r.copy() for r in score]
    broken[0]["seed"] += 200
    assert not audit_seeds(cal, broken, old)["admitted"]


def test_small_development_envelopes_pairing_and_verification():
    from experiments.chem_tape.tree_gp_run import envelope, execute, validate_rows
    from experiments.chem_tape.component_transfer_run import load_saved

    saved, _ = load_saved()
    metas = [
        dict(
            family="DG",
            cell=saved["banks.json"]["DG"]["split"]["development"][0],
            arm=a,
            build=0 if a != "G4" else None,
            repeat=0,
            phase="smoke",
            seed=22160000,
        )
        for a in ("A8", "tree", "G4")
    ]
    rows = [execute(envelope(m, saved, 512, 0.9)) for m in metas]
    validate_rows(rows, metas, saved, 512, 0.9)
    assert len({tuple(r["training_indices"]) for r in rows}) == 1
    assert rows[2]["operator"] is None
    assert rows[0]["operator"]["eligible_children"] == 254
    from experiments.chem_tape.component_transfer_run import execute as original_execute

    original = original_execute(envelope(metas[0], saved, 512, 0.9)["job"])
    for k in (
        "solver",
        "evaluations",
        "curve",
        "training_indices",
        "initial_tokens_hash",
        "operator",
    ):
        assert rows[0][k] == original[k]
    for r in rows:
        phenotypes = dict(r["phenotype_diversity_curve"])
        for point in r["curve"]:
            assert point[2] <= phenotypes[point[0]]
    bad = [r.copy() for r in rows]
    bad[1]["training_indices"] = list(range(64))
    with pytest.raises(ValueError, match="training RNG"):
        validate_rows(bad, metas, saved, 512, 0.9)
    bad = [r.copy() for r in rows]
    bad[1]["evaluations"] += 256
    with pytest.raises(ValueError, match="accounting"):
        validate_rows(bad, metas, saved, 512, 0.9)
