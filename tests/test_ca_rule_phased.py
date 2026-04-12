"""Unit tests for phase-scheduled outer-totalistic rule family."""

import random

import numpy as np
import pytest

from folding_evolution.ca import engine_mlx, engine_numpy
from folding_evolution.ca import rule_phased as rp


K = 4


def test_genotype_length():
    # P=1: 100 + 16 = 116
    assert rp.genotype_len(4, 1, 16) == 116
    # P=2: 200 + 16 = 216
    assert rp.genotype_len(4, 2, 16) == 216
    # P=3: 300 + 16 = 316
    assert rp.genotype_len(4, 3, 16) == 316


def test_random_genotype_in_range():
    rng = random.Random(42)
    g = rp.random_genotype(4, 3, 16, rng)
    assert g.size == 316
    assert g.min() >= 0 and g.max() < 4


def test_random_genotype_deterministic():
    g1 = rp.random_genotype(4, 3, 16, random.Random(99))
    g2 = rp.random_genotype(4, 3, 16, random.Random(99))
    assert np.array_equal(g1, g2)


def test_decode_shapes_and_ranges():
    g = rp.random_genotype(4, 3, 16, random.Random(0))
    tables, schedule = rp.decode_one(g, 4, 3, 16)
    assert tables.shape == (3, 4, 25)
    assert schedule.shape == (16,)
    assert schedule.min() >= 0 and schedule.max() < 3
    assert tables.max() < 4 and tables.min() >= 0


def test_decode_length_mismatch_raises():
    with pytest.raises(ValueError):
        rp.decode_one(np.zeros(50, dtype=np.uint8), 4, 3, 16)


def test_p1_matches_uniform_ot():
    """With n_phases=1, the phased engine must produce identical output to
    the plain outer-totalistic engine for any rule (schedule is always 0)."""
    from folding_evolution.ca import rule as ot_rule
    rng = random.Random(5)
    np_rng = np.random.default_rng(5)
    B, N = 3, 16
    # Build OT genotype and evaluate via uniform engine.
    ot_genos = [ot_rule.random_genotype(K, rng) for _ in range(B)]
    ot_tables = np.stack([ot_rule.decode(g, K) for g in ot_genos], axis=0)
    grid = np_rng.integers(0, K, size=(B, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(B, N), dtype=np.uint8)
    out_ot = engine_numpy.run(grid, ot_tables, clamp, steps=8)

    # Build phased genotype with n_phases=1 using the same tables + zeros schedule.
    tables_p = ot_tables.reshape(B, 1, K, 25)
    schedule = np.zeros((B, 8), dtype=np.int8)
    out_ph = engine_numpy.run_phased(grid, tables_p, schedule, clamp, steps=8)
    assert np.array_equal(out_ot, out_ph)


@pytest.mark.parametrize("seed", [0, 1, 42, 1729])
def test_numpy_mlx_phased_identical(seed):
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    B, N, P, T = 3, 16, 3, 8
    genos = [rp.random_genotype(K, P, T, rng) for _ in range(B)]
    decoded = [rp.decode_one(g, K, P, T) for g in genos]
    tables = np.stack([d[0] for d in decoded], axis=0)      # (B, P, K, 25)
    schedule = np.stack([d[1] for d in decoded], axis=0)    # (B, T)
    grid = np_rng.integers(0, K, size=(B, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(B, N), dtype=np.uint8)

    out_np = engine_numpy.run_phased(grid, tables, schedule, clamp, steps=T)
    out_mx = engine_mlx.run_phased(grid, tables, schedule, clamp, steps=T)
    assert np.array_equal(out_np, out_mx)


def test_mutate_deterministic():
    g = rp.random_genotype(4, 3, 16, random.Random(0))
    m1 = rp.mutate(g, 4, 0.1, random.Random(7))
    m2 = rp.mutate(g, 4, 0.1, random.Random(7))
    assert np.array_equal(m1, m2)


def test_crossover_length_preserved():
    a = rp.random_genotype(4, 3, 16, random.Random(1))
    b = rp.random_genotype(4, 3, 16, random.Random(2))
    c = rp.crossover(a, b, random.Random(3))
    assert c.size == a.size


def test_config_driven_genotype_len():
    from folding_evolution.ca.config import CAConfig
    from folding_evolution.ca import rule as rule_mod
    cfg = CAConfig(rule_family="phased_ot", n_states=4, n_phases=3, steps=16)
    assert rule_mod.genotype_len(cfg) == 316
