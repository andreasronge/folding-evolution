"""NumPy ↔ MLX engine equivalence on fixed seeds."""

import random

import numpy as np
import pytest

from folding_evolution.ca import engine_mlx, engine_numpy
from folding_evolution.ca import rule as ca_rule


K = 4
N = 16
B = 4


def _random_inputs(seed: int):
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    rule_bytes = [ca_rule.random_genotype(K, rng) for _ in range(B)]
    rule_table = np.stack([ca_rule.decode(g, K) for g in rule_bytes], axis=0)

    grid = np_rng.integers(0, K, size=(B, N, N), dtype=np.uint8)
    clamp = np_rng.integers(0, K, size=(B, N), dtype=np.uint8)
    return grid, rule_table, clamp


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
def test_numpy_mlx_single_step_identical(seed):
    grid, rule_table, clamp = _random_inputs(seed)
    out_np = engine_numpy.step(grid, rule_table, clamp)

    import mlx.core as mx
    out_mx = engine_mlx.step(mx.array(grid), mx.array(rule_table), mx.array(clamp))
    out_mx_np = np.array(out_mx, dtype=np.uint8)

    assert out_np.shape == out_mx_np.shape
    assert np.array_equal(out_np, out_mx_np), (
        f"Mismatch at seed={seed}: "
        f"numpy_sum={int(out_np.sum())} mlx_sum={int(out_mx_np.sum())}"
    )


@pytest.mark.parametrize("seed", [0, 3, 99])
def test_numpy_mlx_full_run_identical(seed):
    grid, rule_table, clamp = _random_inputs(seed)
    steps = 16
    out_np = engine_numpy.run(grid, rule_table, clamp, steps=steps)
    out_mx = engine_mlx.run(grid, rule_table, clamp, steps=steps)
    assert np.array_equal(out_np, out_mx)
