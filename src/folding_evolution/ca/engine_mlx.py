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


# ---------------- Decision-tree rule family (MLX) ----------------

def _window_stack_mx(grid: mx.array) -> mx.array:
    """Build a (B, N, N, 9) window stack on MLX. Same position order as NumPy.
    Position order: 0=NW 1=N 2=NE 3=W 4=C 5=E 6=SW 7=S 8=SE.
    """
    B, N, _ = grid.shape
    padded = mx.pad(grid, [(0, 0), (1, 1), (1, 1)])
    # stack 9 shifted views along a new last axis
    return mx.stack([
        padded[:, 0:-2, 0:-2],
        padded[:, 0:-2, 1:-1],
        padded[:, 0:-2, 2:],
        padded[:, 1:-1, 0:-2],
        padded[:, 1:-1, 1:-1],
        padded[:, 1:-1, 2:],
        padded[:, 2:,   0:-2],
        padded[:, 2:,   1:-1],
        padded[:, 2:,   2:],
    ], axis=-1)


def step_dt(
    grid: mx.array,
    pos: mx.array,
    val: mx.array,
    leaves: mx.array,
    input_clamp: mx.array,
    depth: int = 5,
) -> mx.array:
    """Decision-tree CA step on MLX. Same contract as engine_numpy.step_dt."""
    B, N, _ = grid.shape
    n_internal = (1 << depth) - 1

    window = _window_stack_mx(grid)                              # (B, N, N, 9) uint8

    # Work in int32 for indices/comparisons; cast back to uint8 at the end.
    current = mx.zeros((B, N, N), dtype=mx.int32)

    # Flatten the per-rule arrays once for take_along_axis gathers per step.
    # pos/val are (B, n_internal); we want pos[b, current[b,y,x]] per (b,y,x).
    pos_flat = pos.astype(mx.int32)                              # (B, n_internal)
    val_flat = val.astype(mx.int32)

    # For window gather: flatten window to (B, N*N, 9) so we can take at the
    # cell's (y,x) position using mx.take_along_axis over axis=2.
    window_flat = window.astype(mx.int32).reshape(B, N * N, 9)

    for _ in range(depth):
        # Gather pos and val at current node per (b, y, x).
        cur_flat = current.reshape(B, N * N)                     # (B, N*N)
        pos_here = mx.take_along_axis(pos_flat, cur_flat, axis=1)  # (B, N*N)
        val_here = mx.take_along_axis(val_flat, cur_flat, axis=1)

        # Gather the window cell at `pos_here` along the last axis of window_flat.
        pos_idx = pos_here.reshape(B, N * N, 1)
        window_val = mx.take_along_axis(window_flat, pos_idx, axis=2).reshape(B, N * N)

        goes_left = (window_val == val_here).astype(mx.int32)
        step_vec = 2 - goes_left                                 # 1 if left else 2
        cur_flat = 2 * cur_flat + step_vec
        current = cur_flat.reshape(B, N, N)

    leaf_idx = current - n_internal                              # (B, N, N) int32
    leaf_idx_flat = leaf_idx.reshape(B, N * N)
    new_flat = mx.take_along_axis(
        leaves.astype(mx.int32), leaf_idx_flat, axis=1
    )
    new_grid = new_flat.reshape(B, N, N).astype(mx.uint8)

    clamped_row0 = input_clamp.reshape(B, 1, N)
    new_grid = mx.concatenate([clamped_row0, new_grid[:, 1:, :]], axis=1)
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
    grid = _to_mx(initial_grid)
    pos_mx = _to_mx(pos)
    val_mx = _to_mx(val)
    leaves_mx = _to_mx(leaves)
    clamp_mx = _to_mx(input_clamp)

    B, N, _ = initial_grid.shape
    clamped_row0 = clamp_mx.reshape(B, 1, N)
    grid = mx.concatenate([clamped_row0, grid[:, 1:, :]], axis=1)

    for _ in range(steps):
        grid = step_dt(grid, pos_mx, val_mx, leaves_mx, clamp_mx, depth=depth)
    mx.eval(grid)
    return np.array(grid, dtype=np.uint8)
