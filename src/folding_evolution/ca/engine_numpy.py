"""Reference CA step kernel using NumPy.

The kernel is batched over a leading axis B which typically flattens
(population, examples). All arrays are uint8 in [0, K).

Neighborhood: 8-connected Moore, zero-padded boundary.
Rule family: outer-totalistic — next = table[self, sum(neighbors)].
Input convention: row 0 is clamped to input_clamp each step.
"""

from __future__ import annotations

import numpy as np


def step(
    grid: np.ndarray,
    rule_table: np.ndarray,
    input_clamp: np.ndarray,
) -> np.ndarray:
    """Apply one CA step.

    Args:
        grid: (B, N, N) uint8
        rule_table: (B, K, max_sum+1) uint8
        input_clamp: (B, N) uint8 — values to pin on row 0 AFTER the step

    Returns:
        new_grid: (B, N, N) uint8
    """
    assert grid.dtype == np.uint8
    assert rule_table.dtype == np.uint8
    assert input_clamp.dtype == np.uint8
    B, N, _ = grid.shape
    K = rule_table.shape[1]

    # Zero-padded neighborhood sum. Shift in all 8 directions.
    padded = np.zeros((B, N + 2, N + 2), dtype=np.int16)
    padded[:, 1:-1, 1:-1] = grid.astype(np.int16)

    nbr_sum = (
        padded[:, :-2, :-2]   # NW
        + padded[:, :-2, 1:-1]  # N
        + padded[:, :-2, 2:]   # NE
        + padded[:, 1:-1, :-2]  # W
        + padded[:, 1:-1, 2:]   # E
        + padded[:, 2:, :-2]    # SW
        + padded[:, 2:, 1:-1]   # S
        + padded[:, 2:, 2:]     # SE
    ).astype(np.int16)

    self_idx = grid.astype(np.int64)                              # (B, N, N)
    sum_idx = nbr_sum.astype(np.int64)                            # (B, N, N)

    # Gather: new[b, y, x] = rule_table[b, self_idx[b,y,x], sum_idx[b,y,x]]
    b_idx = np.arange(B).reshape(B, 1, 1)                         # broadcast
    new_grid = rule_table[b_idx, self_idx, sum_idx].astype(np.uint8)

    # Clamp input row.
    new_grid[:, 0, :] = input_clamp
    return new_grid


def run(
    initial_grid: np.ndarray,
    rule_table: np.ndarray,
    input_clamp: np.ndarray,
    steps: int,
) -> np.ndarray:
    """Run `steps` iterations of the CA, returning the final grid."""
    grid = initial_grid.copy()
    # Clamp row 0 on the initial grid too, so step 0 starts consistent.
    grid[:, 0, :] = input_clamp
    for _ in range(steps):
        grid = step(grid, rule_table, input_clamp)
    return grid
