"""MLX (Metal) CA step kernel — same contract as engine_numpy.

Key differences from NumPy:
- MLX arrays are immutable; in-place row clamping becomes a concatenate.
- mx.take_along_axis replaces NumPy's fancy indexing for the rule-table gather.
- Prefer uint8 throughout to keep data small; cast to int32 only for indexing.
"""

from __future__ import annotations

import mlx.core as mx
import numpy as np


def _to_mx(a: np.ndarray) -> mx.array:
    return mx.array(a)


def _neighbor_sum(grid: mx.array) -> mx.array:
    """8-connected Moore neighbor sum with zero padding.

    grid: (B, N, N) uint8. Returns (B, N, N) int32.
    """
    B, N, _ = grid.shape
    padded = mx.pad(grid.astype(mx.int32), [(0, 0), (1, 1), (1, 1)])
    return (
        padded[:, :-2, :-2]
        + padded[:, :-2, 1:-1]
        + padded[:, :-2, 2:]
        + padded[:, 1:-1, :-2]
        + padded[:, 1:-1, 2:]
        + padded[:, 2:, :-2]
        + padded[:, 2:, 1:-1]
        + padded[:, 2:, 2:]
    )


def step(
    grid: mx.array,
    rule_table: mx.array,
    input_clamp: mx.array,
) -> mx.array:
    """One CA step, same semantics as engine_numpy.step.

    Args:
        grid: (B, N, N) uint8
        rule_table: (B, K, max_sum+1) uint8
        input_clamp: (B, N) uint8
    Returns:
        new_grid: (B, N, N) uint8
    """
    B, N, _ = grid.shape
    K, max_sum_plus_1 = rule_table.shape[1], rule_table.shape[2]

    nbr_sum = _neighbor_sum(grid)                 # (B, N, N) int32
    self_idx = grid.astype(mx.int32)              # (B, N, N)

    # Linear index into flattened rule table per batch: self * (max_sum+1) + sum.
    flat_idx = self_idx * max_sum_plus_1 + nbr_sum
    flat_table = rule_table.reshape(B, K * max_sum_plus_1)

    # Gather: mx.take_along_axis over axis=1 of flat_table using flat_idx flattened per batch.
    flat_idx_2d = flat_idx.reshape(B, N * N)
    gathered = mx.take_along_axis(flat_table.astype(mx.int32), flat_idx_2d, axis=1)
    new_grid = gathered.reshape(B, N, N).astype(mx.uint8)

    # Clamp row 0 via slice-concat (MLX arrays are immutable).
    clamped_row0 = input_clamp.reshape(B, 1, N)
    new_grid = mx.concatenate([clamped_row0, new_grid[:, 1:, :]], axis=1)
    return new_grid


def run(
    initial_grid: np.ndarray,
    rule_table: np.ndarray,
    input_clamp: np.ndarray,
    steps: int,
) -> np.ndarray:
    """Run `steps` iterations on MLX, return the final grid as a NumPy uint8 array."""
    grid = _to_mx(initial_grid)
    table = _to_mx(rule_table)
    clamp = _to_mx(input_clamp)

    # Apply initial clamp on row 0 for consistency with engine_numpy.run.
    B, N, _ = initial_grid.shape
    clamped_row0 = clamp.reshape(B, 1, N)
    grid = mx.concatenate([clamped_row0, grid[:, 1:, :]], axis=1)

    for _ in range(steps):
        grid = step(grid, table, clamp)
    mx.eval(grid)
    return np.array(grid, dtype=np.uint8)
