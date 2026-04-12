"""Tests for neighborhood radius > 1 in outer-totalistic kernel."""

import random

import numpy as np
import pytest

from folding_evolution.ca import engine_mlx, engine_numpy
from folding_evolution.ca import rule as ca_rule


K = 4


@pytest.mark.parametrize("radius,expected_nbrs,expected_max_sum", [
    (1, 8, 24),
    (2, 24, 72),
    (3, 48, 144),
])
def test_neighbor_counts_and_rule_shape(radius, expected_nbrs, expected_max_sum):
    assert ca_rule.neighbor_count(radius) == expected_nbrs
    shape = ca_rule.rule_shape(K, radius=radius)
    assert shape == (K, expected_max_sum + 1)
    # K=4 sizes: r=1 → 100, r=2 → 292, r=3 → 580
    expected_len = {1: 100, 2: 292, 3: 580}[radius]
    assert ca_rule.rule_len(K, radius=radius) == expected_len


def test_radius1_matches_legacy_step():
    """Default radius=1 must produce the same output as before the refactor."""
    rng = random.Random(42)
    np_rng = np.random.default_rng(42)
    B, N = 4, 8
    genos = [ca_rule.random_genotype(K, rng) for _ in range(B)]
    tables = np.stack([ca_rule.decode(g, K) for g in genos], axis=0)
    grid = np_rng.integers(0, K, size=(B, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(B, N), dtype=np.uint8)
    out_default = engine_numpy.step(grid, tables, clamp)
    out_r1 = engine_numpy.step(grid, tables, clamp, radius=1)
    assert np.array_equal(out_default, out_r1)


@pytest.mark.parametrize("radius", [1, 2, 3])
def test_numpy_step_shape_at_radius(radius):
    rng = random.Random(7)
    np_rng = np.random.default_rng(7)
    B, N = 3, 16
    genos = [ca_rule.random_genotype(K, rng, radius=radius) for _ in range(B)]
    tables = np.stack([ca_rule.decode(g, K, radius=radius) for g in genos], axis=0)
    grid = np_rng.integers(0, K, size=(B, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(B, N), dtype=np.uint8)
    out = engine_numpy.step(grid, tables, clamp, radius=radius)
    assert out.shape == (B, N, N)
    assert out.dtype == np.uint8


@pytest.mark.parametrize("radius", [1, 2, 3])
def test_numpy_mlx_parity_at_radius(radius):
    rng = random.Random(99)
    np_rng = np.random.default_rng(99)
    B, N = 3, 16
    genos = [ca_rule.random_genotype(K, rng, radius=radius) for _ in range(B)]
    tables = np.stack([ca_rule.decode(g, K, radius=radius) for g in genos], axis=0)
    grid = np_rng.integers(0, K, size=(B, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(B, N), dtype=np.uint8)
    out_np = engine_numpy.step(grid, tables, clamp, radius=radius)

    import mlx.core as mx
    out_mx = engine_mlx.step(mx.array(grid), mx.array(tables), mx.array(clamp), radius=radius)
    assert np.array_equal(out_np, np.array(out_mx, dtype=np.uint8))


def test_radius2_at_boundary_uses_zero_padding():
    """A lone live cell at the top-left corner contributes to all r=2 neighborhoods
    inside its (2r+1)x(2r+1) reach, but cells outside the grid are zero."""
    B, N = 1, 8
    grid = np.zeros((B, N, N), dtype=np.uint8)
    grid[0, 0, 0] = 1
    table = np.zeros((B, K, 73), dtype=np.uint8)
    # Identity rule (next = self, regardless of sum) — ensures the boundary
    # doesn't alter interior behaviour.
    for s in range(K):
        table[0, s, :] = s
    clamp = np.zeros((B, N), dtype=np.uint8)
    out = engine_numpy.step(grid, table, clamp, radius=2)
    # Identity rule leaves (1,1) alone too; only row 0 gets clamped.
    assert out[0, 1, 1] == 0


def test_radius_genotype_length_for_config():
    from folding_evolution.ca.config import CAConfig
    from folding_evolution.ca import rule as rule_mod
    for r, expected in [(1, 100), (2, 292), (3, 580)]:
        cfg = CAConfig(n_states=4, neighborhood_radius=r)
        assert rule_mod.genotype_len(cfg) == expected
