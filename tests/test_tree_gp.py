"""Validity checks for the bounded tree implementation and preparation stop."""

import numpy as np
import pytest

from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET
from experiments.chem_tape.tree_gp_search import (
    Tree, initialize, interpret, from_postfix, random_tree,
)
from experiments.chem_tape.tree_gp_validate import full_acceptance_probability, python_output


def test_order_closure_missing_readouts_and_wrapping():
    conditional = Tree((11, 8, 7, 10, 0, 1))  # else5, then2, X0>X1
    for x in ([], [3], [2, 3], [3, 2], [3, 3]):
        expected = 2 if (x[0] if x else 0) > (x[1] if len(x) > 1 else 0) else 5
        assert interpret(conditional, x) == python_output(conditional, x) == expected
        assert outputs([conditional.program], [x], ALPHABET)[0, 0] == expected
    add = Tree((9, 0, 1))
    x = [2**63 - 1, 1]
    assert interpret(add, x) == outputs([add.program], [x], ALPHABET)[0, 0] == -2**63
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
        child, rejected = a.insert(int(rng.integers(len(a.prefix))), b, int(rng.integers(len(b.prefix))))
        assert len(child.program) <= 32
        for x in ([0, 1, 2, 3], [4, 3, 2, 1], []):
            assert interpret(child, x) == python_output(child, x)


def test_frozen_initializer_fails_in_full_depth4_bin():
    with pytest.raises(ValueError, match="depth=4, full=True, draws=10000"):
        initialize(np.random.default_rng([22160000, 1]), 256)
    assert full_acceptance_probability(2) == pytest.approx(1)
    assert full_acceptance_probability(3) > 0.7
    # All-binary 31-node constant trees; length32 also admits one readout
    # or one deepest-level IF_GT (one extra constant leaf).
    exact = (2 / 3)**15 * (4 / 9)**16 * (1 + 16 * 5 / 4 + 8 * 0.5 * 4 / 9)
    assert full_acceptance_probability(4) == pytest.approx(exact)
