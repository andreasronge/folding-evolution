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


# ---------------- Decision-tree rule family ----------------

def _window_stack(grid: np.ndarray) -> np.ndarray:
    """Build the 3x3 neighborhood window as a (B, N, N, 9) uint8 array.

    Position order: 0=NW 1=N 2=NE 3=W 4=C 5=E 6=SW 7=S 8=SE.
    Zero-padded at the grid boundary.
    """
    B, N, _ = grid.shape
    padded = np.zeros((B, N + 2, N + 2), dtype=np.uint8)
    padded[:, 1:-1, 1:-1] = grid
    return np.stack([
        padded[:, 0:-2, 0:-2],  # NW
        padded[:, 0:-2, 1:-1],  # N
        padded[:, 0:-2, 2:],    # NE
        padded[:, 1:-1, 0:-2],  # W
        padded[:, 1:-1, 1:-1],  # C
        padded[:, 1:-1, 2:],    # E
        padded[:, 2:,   0:-2],  # SW
        padded[:, 2:,   1:-1],  # S
        padded[:, 2:,   2:],    # SE
    ], axis=-1)


def step_dt(
    grid: np.ndarray,
    pos: np.ndarray,
    val: np.ndarray,
    leaves: np.ndarray,
    input_clamp: np.ndarray,
    depth: int = 5,
) -> np.ndarray:
    """One CA step under decision-tree rules.

    Args:
        grid: (B, N, N) uint8
        pos: (B, 2^depth - 1) uint8 — position index (0..8) at each internal node
        val: (B, 2^depth - 1) uint8 — test value at each internal node
        leaves: (B, 2^depth) uint8 — output state at each leaf
        input_clamp: (B, N) uint8 — values pinned to row 0 after the step
    """
    assert grid.dtype == np.uint8
    assert pos.dtype == np.uint8 and val.dtype == np.uint8
    assert leaves.dtype == np.uint8
    B, N, _ = grid.shape
    n_internal = (1 << depth) - 1

    window = _window_stack(grid)  # (B, N, N, 9)

    # Track the current internal-node index for each cell as we descend.
    current = np.zeros((B, N, N), dtype=np.int64)

    b_idx = np.arange(B).reshape(B, 1, 1)
    y_idx = np.arange(N).reshape(1, N, 1)
    x_idx = np.arange(N).reshape(1, 1, N)

    for _ in range(depth):
        # At each cell, gather (pos, val) for its current node.
        pos_here = pos[b_idx, current]                          # (B, N, N)
        val_here = val[b_idx, current]                          # (B, N, N)
        # Gather the window cell at `pos_here`.
        window_val = window[
            b_idx, y_idx, x_idx, pos_here.astype(np.int64)
        ]                                                        # (B, N, N)
        goes_left = (window_val == val_here)
        # Left child = 2i+1, right child = 2i+2.
        current = 2 * current + np.where(goes_left, 1, 2)

    # `current` is now a tree-array index in [n_internal, 2*n_internal].
    leaf_idx = (current - n_internal).astype(np.int64)
    new_grid = leaves[b_idx, leaf_idx].astype(np.uint8)

    # Clamp row 0.
    new_grid[:, 0, :] = input_clamp
    return new_grid


def run_dt(
    initial_grid: np.ndarray,
    pos: np.ndarray,
    val: np.ndarray,
    leaves: np.ndarray,
    input_clamp: np.ndarray,
    steps: int,
    depth: int = 5,
) -> np.ndarray:
    grid = initial_grid.copy()
    grid[:, 0, :] = input_clamp
    for _ in range(steps):
        grid = step_dt(grid, pos, val, leaves, input_clamp, depth=depth)
    return grid
