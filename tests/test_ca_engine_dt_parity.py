"""NumPy ↔ MLX bitwise-identical DT step."""

import random

import numpy as np
import pytest

from folding_evolution.ca import engine_mlx, engine_numpy
from folding_evolution.ca import rule_decision_tree as dt


K = 4
N = 16
B = 4


def _random_dt_inputs(seed: int):
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    genos = [dt.random_genotype(K, rng) for _ in range(B)]
    decoded = dt.decode_batch(genos, K)
    grid = np_rng.integers(0, K, size=(B, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(B, N), dtype=np.uint8)
    return grid, decoded.pos, decoded.val, decoded.leaves, clamp


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
def test_numpy_mlx_single_step_dt_identical(seed):
    grid, pos, val, leaves, clamp = _random_dt_inputs(seed)
    out_np = engine_numpy.step_dt(grid, pos, val, leaves, clamp)

    import mlx.core as mx
    out_mx = engine_mlx.step_dt(
        mx.array(grid), mx.array(pos), mx.array(val),
        mx.array(leaves), mx.array(clamp),
    )
    out_mx_np = np.array(out_mx, dtype=np.uint8)
    assert np.array_equal(out_np, out_mx_np)


@pytest.mark.parametrize("seed", [0, 3, 99])
def test_numpy_mlx_full_run_dt_identical(seed):
    grid, pos, val, leaves, clamp = _random_dt_inputs(seed)
    out_np = engine_numpy.run_dt(grid, pos, val, leaves, clamp, steps=16)
    out_mx = engine_mlx.run_dt(grid, pos, val, leaves, clamp, steps=16)
    assert np.array_equal(out_np, out_mx)
