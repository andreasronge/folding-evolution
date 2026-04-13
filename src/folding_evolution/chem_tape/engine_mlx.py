"""MLX (Metal) chem-tape v1 engine — same contract as engine_numpy.

Produces a (B, L) bool longest-active-run mask. Since the downstream Python
executor needs NumPy arrays anyway, the MLX entry points evaluate and convert
back to NumPy; parity with the NumPy engine is then a bitwise mask comparison.
"""

from __future__ import annotations

import mlx.core as mx
import numpy as np

from .alphabet import ACTIVE_MASK


def _active_mask_mx(tapes_mx: mx.array) -> mx.array:
    """(B, L) uint8 → (B, L) bool, True iff token id ∈ {1..13}."""
    # MLX lacks a direct fancy-index-from-lookup, so compose the predicate.
    t = tapes_mx.astype(mx.int32)
    return (t >= 1) & (t <= 13)


def compute_active_mask(tapes: np.ndarray) -> np.ndarray:
    assert tapes.dtype == np.uint8
    tapes_mx = mx.array(tapes)
    mask = _active_mask_mx(tapes_mx)
    mx.eval(mask)
    return np.array(mask, dtype=bool)


def compute_longest_run_mask(tapes: np.ndarray) -> np.ndarray:
    """MLX port of the spec §Layer 6 algorithm; returns NumPy bool (B, L)."""
    assert tapes.dtype == np.uint8
    B, L = tapes.shape

    tapes_mx = mx.array(tapes)
    is_active = _active_mask_mx(tapes_mx)                         # (B, L) bool

    # shift_right_pad0 via slice+concat (MLX arrays are immutable).
    zeros_col = mx.zeros((B, 1), dtype=mx.bool_)
    shifted = mx.concatenate([zeros_col, is_active[:, :-1]], axis=1)
    run_start = is_active & ~shifted                               # (B, L) bool

    run_id = mx.cumsum(run_start.astype(mx.int32), axis=1) * is_active.astype(mx.int32)
    # (B, L) int32, values in [0, max_runs].

    # One-hot + sum gives per-row run-length counts. For v1 sizes (B≤1K, L=32)
    # the (B, L, L+1) intermediate is tiny (~1M ints) and keeps us off MLX
    # APIs that differ by version.
    bins = mx.arange(L + 1, dtype=mx.int32)                        # (L+1,)
    onehot = (run_id[:, :, None] == bins[None, None, :]).astype(mx.int32)
    lengths = onehot.sum(axis=1)                                   # (B, L+1) int32

    # argmax over lengths[:, 1:] with ties → leftmost (mx.argmax returns first).
    best_run = mx.argmax(lengths[:, 1:], axis=1) + 1               # (B,) int32

    any_active = is_active.any(axis=1)                             # (B,) bool
    best_run = mx.where(any_active, best_run, mx.zeros_like(best_run))

    active_best = (run_id == best_run[:, None]) & is_active         # (B, L) bool
    mx.eval(active_best)
    return np.array(active_best, dtype=bool)


def extract_programs(
    tapes: np.ndarray, longest_mask: np.ndarray
) -> list[list[int]]:
    """Backend-agnostic: given (B, L) tapes and (B, L) mask, gather per row."""
    assert tapes.shape == longest_mask.shape
    programs: list[list[int]] = []
    for b in range(tapes.shape[0]):
        programs.append(tapes[b][longest_mask[b]].astype(np.int64).tolist())
    return programs
