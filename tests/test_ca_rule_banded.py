"""Unit tests for banded outer-totalistic rule family."""

import random

import numpy as np
import pytest

from folding_evolution.ca import engine_mlx, engine_numpy
from folding_evolution.ca import rule_banded as rb


K = 4
N = 16
B = 3  # n_bands
BATCH = 4


def test_genotype_length():
    # K=4, n_bands=3 → 3 bands × 100 per band = 300
    assert rb.genotype_len(4, 3) == 300
    # K=2, n_bands=3 → 3 × 18 = 54
    assert rb.genotype_len(2, 3) == 54


def test_band_boundaries_n16_b3():
    bounds = rb.band_boundaries(16, 3)
    # rounding: 0, round(16/3)=5, round(32/3)=11, 16
    assert list(bounds) == [0, 5, 11, 16]


def test_row_to_band_assignments():
    r2b = rb.row_to_band(16, 3)
    expected = [0]*5 + [1]*6 + [2]*5
    assert list(r2b) == expected


def test_random_genotype_in_range():
    rng = random.Random(42)
    g = rb.random_genotype(4, 3, rng)
    assert g.size == 300
    assert g.min() >= 0 and g.max() < 4


def test_random_genotype_deterministic():
    g1 = rb.random_genotype(4, 3, random.Random(99))
    g2 = rb.random_genotype(4, 3, random.Random(99))
    assert np.array_equal(g1, g2)


def test_decode_shape_and_ranges():
    g = rb.random_genotype(4, 3, random.Random(0))
    table = rb.decode_one(g, 4, 3)
    assert table.shape == (3, 4, 25)
    assert table.max() < 4 and table.min() >= 0


def test_mutate_deterministic():
    g = rb.random_genotype(4, 3, random.Random(0))
    m1 = rb.mutate(g, 4, 0.1, random.Random(7))
    m2 = rb.mutate(g, 4, 0.1, random.Random(7))
    assert np.array_equal(m1, m2)


def _random_banded_inputs(seed: int):
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    genos = [rb.random_genotype(K, B, rng) for _ in range(BATCH)]
    tables = np.stack([rb.decode_one(g, K, B) for g in genos], axis=0)  # (BATCH, B, K, 25)
    row_band = rb.row_to_band(N, B)
    grid = np_rng.integers(0, K, size=(BATCH, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(BATCH, N), dtype=np.uint8)
    return grid, tables, row_band, clamp


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
def test_numpy_mlx_single_step_banded_identical(seed):
    grid, tables, row_band, clamp = _random_banded_inputs(seed)
    out_np = engine_numpy.step_banded(grid, tables, row_band, clamp)

    import mlx.core as mx
    out_mx = engine_mlx.step_banded(
        mx.array(grid), mx.array(tables), mx.array(row_band.astype(np.int32)),
        mx.array(clamp),
    )
    out_mx_np = np.array(out_mx, dtype=np.uint8)
    assert np.array_equal(out_np, out_mx_np)


@pytest.mark.parametrize("seed", [0, 3, 99])
def test_numpy_mlx_full_run_banded_identical(seed):
    grid, tables, row_band, clamp = _random_banded_inputs(seed)
    out_np = engine_numpy.run_banded(grid, tables, row_band, clamp, steps=16)
    out_mx = engine_mlx.run_banded(grid, tables, row_band, clamp, steps=16)
    assert np.array_equal(out_np, out_mx)


def test_banded_identical_bands_matches_uniform_ot():
    """If every band carries the same rule table, banded output must match the
    plain outer-totalistic engine with that rule."""
    rng = random.Random(5)
    np_rng = np.random.default_rng(5)
    # Shared single-band rule.
    single = np.array([rng.randrange(K) for _ in range(4 * 25)], dtype=np.uint8)
    single_table = single.reshape(4, 25)
    # Replicate across 3 bands.
    tables = np.broadcast_to(single_table[None, None, ...], (BATCH, 3, 4, 25))
    tables = np.ascontiguousarray(tables)
    grid = np_rng.integers(0, K, size=(BATCH, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(BATCH, N), dtype=np.uint8)
    row_band = rb.row_to_band(N, 3)

    out_banded = engine_numpy.step_banded(grid, tables, row_band, clamp)
    # Plain OT step using the same (replicated) rule table.
    ot_tables = np.broadcast_to(single_table[None, ...], (BATCH, 4, 25))
    ot_tables = np.ascontiguousarray(ot_tables)
    out_plain = engine_numpy.step(grid, ot_tables, clamp)
    assert np.array_equal(out_banded, out_plain)
