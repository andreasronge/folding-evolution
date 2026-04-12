"""Unit tests for ca.rule — genotype/rule encoding, mutate, crossover."""

import random

import numpy as np
import pytest

from folding_evolution.ca import rule


def test_rule_shape_k4():
    assert rule.rule_shape(4) == (4, 25)
    assert rule.rule_len(4) == 100


def test_rule_shape_k2():
    assert rule.rule_shape(2) == (2, 9)
    assert rule.rule_len(2) == 18


def test_random_genotype_in_range():
    rng = random.Random(42)
    g = rule.random_genotype(4, rng)
    assert g.shape == (100,)
    assert g.dtype == np.uint8
    assert g.min() >= 0
    assert g.max() < 4


def test_random_genotype_deterministic():
    g1 = rule.random_genotype(4, random.Random(99))
    g2 = rule.random_genotype(4, random.Random(99))
    assert np.array_equal(g1, g2)


def test_decode_shape():
    rng = random.Random(0)
    g = rule.random_genotype(4, rng)
    table = rule.decode(g, 4)
    assert table.shape == (4, 25)
    assert table.dtype == np.uint8


def test_decode_length_mismatch():
    with pytest.raises(ValueError):
        rule.decode(np.zeros(50, dtype=np.uint8), 4)


def test_mutate_deterministic():
    rng_seed = 123
    g = rule.random_genotype(4, random.Random(0))
    m1 = rule.mutate(g, 4, 0.1, random.Random(rng_seed))
    m2 = rule.mutate(g, 4, 0.1, random.Random(rng_seed))
    assert np.array_equal(m1, m2)


def test_mutate_preserves_range():
    g = rule.random_genotype(4, random.Random(0))
    m = rule.mutate(g, 4, 0.5, random.Random(1))
    assert m.min() >= 0 and m.max() < 4


def test_mutate_rate_zero_is_identity():
    g = rule.random_genotype(4, random.Random(0))
    m = rule.mutate(g, 4, 0.0, random.Random(1))
    assert np.array_equal(g, m)


def test_mutate_rate_one_changes_most_bytes():
    g = rule.random_genotype(4, random.Random(0))
    m = rule.mutate(g, 4, 1.0, random.Random(42))
    # With p=1 each byte is resampled; for K=4 we'd expect ~25% to match by chance.
    same = int((g == m).sum())
    assert same < g.size  # at least one changed
    assert same / g.size < 0.5


def test_crossover_length_preserved():
    rng = random.Random(0)
    a = rule.random_genotype(4, rng)
    b = rule.random_genotype(4, rng)
    c = rule.crossover(a, b, random.Random(7))
    assert c.size == a.size


def test_crossover_uses_both_parents():
    a = np.zeros(100, dtype=np.uint8)
    b = np.ones(100, dtype=np.uint8)
    c = rule.crossover(a, b, random.Random(3))
    # Child should contain some zeros (from a) and some ones (from b).
    assert (c == 0).any()
    assert (c == 1).any()


def test_crossover_deterministic():
    a = rule.random_genotype(4, random.Random(1))
    b = rule.random_genotype(4, random.Random(2))
    c1 = rule.crossover(a, b, random.Random(11))
    c2 = rule.crossover(a, b, random.Random(11))
    assert np.array_equal(c1, c2)
