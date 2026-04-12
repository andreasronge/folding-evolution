"""Unit tests for banded+phased combined rule family."""

import random

import numpy as np
import pytest

from folding_evolution.ca import engine_mlx, engine_numpy
from folding_evolution.ca import rule_banded_phased as rbp


K = 4


def test_genotype_length():
    # K=4, n_phases=2, n_bands=3, steps=16: 2*3*100 + 16 = 616
    assert rbp.genotype_len(4, 2, 3, 16) == 616
    # n_phases=3 → 3*3*100 + 16 = 916
    assert rbp.genotype_len(4, 3, 3, 16) == 916


def test_random_genotype_in_range():
    rng = random.Random(42)
    g = rbp.random_genotype(4, 2, 3, 16, rng)
    assert g.size == 616
    assert g.min() >= 0 and g.max() < 4


def test_decode_shapes():
    g = rbp.random_genotype(4, 2, 3, 16, random.Random(0))
    tables, schedule = rbp.decode_one(g, 4, 2, 3, 16)
    assert tables.shape == (2, 3, 4, 25)
    assert schedule.shape == (16,)
    assert schedule.min() >= 0 and schedule.max() < 2


def test_decode_length_mismatch():
    with pytest.raises(ValueError):
        rbp.decode_one(np.zeros(100, dtype=np.uint8), 4, 2, 3, 16)


def test_mutate_deterministic():
    g = rbp.random_genotype(4, 2, 3, 16, random.Random(0))
    m1 = rbp.mutate(g, 4, 0.1, random.Random(7))
    m2 = rbp.mutate(g, 4, 0.1, random.Random(7))
    assert np.array_equal(m1, m2)


def _random_bp_inputs(seed: int, P: int = 2, Bn: int = 3, T: int = 8):
    from folding_evolution.ca import rule_banded as rb
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    BATCH, N = 3, 16
    genos = [rbp.random_genotype(K, P, Bn, T, rng) for _ in range(BATCH)]
    decoded = [rbp.decode_one(g, K, P, Bn, T) for g in genos]
    tables = np.stack([d[0] for d in decoded], axis=0)
    schedule = np.stack([d[1] for d in decoded], axis=0)
    row_band = rb.row_to_band(N, Bn)
    grid = np_rng.integers(0, K, size=(BATCH, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(BATCH, N), dtype=np.uint8)
    return grid, tables, schedule, row_band, clamp


@pytest.mark.parametrize("seed", [0, 1, 7, 42])
def test_numpy_mlx_banded_phased_identical(seed):
    grid, tables, schedule, row_band, clamp = _random_bp_inputs(seed)
    out_np = engine_numpy.run_banded_phased(
        grid, tables, schedule, row_band, clamp, steps=8
    )
    out_mx = engine_mlx.run_banded_phased(
        grid, tables, schedule, row_band, clamp, steps=8
    )
    assert np.array_equal(out_np, out_mx)


def test_p1_reduces_to_banded():
    """With n_phases=1, banded_phased must match banded_ot for any genotype."""
    from folding_evolution.ca import rule_banded as rb
    rng = random.Random(5)
    np_rng = np.random.default_rng(5)
    Bn, BATCH, N, T = 3, 3, 16, 8
    # Build the 3-band rule-table stack as if from banded_ot.
    banded_genos = [rb.random_genotype(K, Bn, rng) for _ in range(BATCH)]
    banded_tables = np.stack([rb.decode_one(g, K, Bn) for g in banded_genos], axis=0)  # (BATCH, Bn, K, 25)
    row_band = rb.row_to_band(N, Bn)
    grid = np_rng.integers(0, K, size=(BATCH, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(BATCH, N), dtype=np.uint8)
    out_banded = engine_numpy.run_banded(grid, banded_tables, row_band, clamp, steps=T)

    # Wrap banded_tables into phase=1 form: (BATCH, 1, Bn, K, 25), zero schedule.
    bp_tables = banded_tables.reshape(BATCH, 1, Bn, K, 25)
    schedule = np.zeros((BATCH, T), dtype=np.int8)
    out_bp = engine_numpy.run_banded_phased(
        grid, bp_tables, schedule, row_band, clamp, steps=T
    )
    assert np.array_equal(out_banded, out_bp)


def test_config_driven_len():
    from folding_evolution.ca.config import CAConfig
    from folding_evolution.ca import rule as rule_mod
    cfg = CAConfig(rule_family="banded_phased", n_states=4, n_phases=2, n_bands=3, steps=16)
    assert rule_mod.genotype_len(cfg) == 616
