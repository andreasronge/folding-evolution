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
    t = tapes_mx.astype(mx.int32)
    return (t >= 1) & (t <= 13)


def _non_separator_mask_mx(tapes_mx: mx.array) -> mx.array:
    """(B, L) uint8 → (B, L) bool, True iff token id ∉ {14, 15}. Arm BP rule."""
    t = tapes_mx.astype(mx.int32)
    return t < 14


def compute_active_mask(tapes: np.ndarray) -> np.ndarray:
    assert tapes.dtype == np.uint8
    mask = _active_mask_mx(mx.array(tapes))
    mx.eval(mask)
    return np.array(mask, dtype=bool)


def compute_non_separator_mask(tapes: np.ndarray) -> np.ndarray:
    assert tapes.dtype == np.uint8
    mask = _non_separator_mask_mx(mx.array(tapes))
    mx.eval(mask)
    return np.array(mask, dtype=bool)


def _longest_run_mask_mx(eligible: mx.array) -> mx.array:
    """MLX port of the spec §Layer 6 longest-run algorithm over an eligibility mask."""
    B, L = eligible.shape

    zeros_col = mx.zeros((B, 1), dtype=mx.bool_)
    shifted = mx.concatenate([zeros_col, eligible[:, :-1]], axis=1)
    run_start = eligible & ~shifted

    run_id = mx.cumsum(run_start.astype(mx.int32), axis=1) * eligible.astype(mx.int32)

    bins = mx.arange(L + 1, dtype=mx.int32)
    onehot = (run_id[:, :, None] == bins[None, None, :]).astype(mx.int32)
    lengths = onehot.sum(axis=1)

    best_run = mx.argmax(lengths[:, 1:], axis=1) + 1
    any_eligible = eligible.any(axis=1)
    best_run = mx.where(any_eligible, best_run, mx.zeros_like(best_run))

    return (run_id == best_run[:, None]) & eligible


def compute_longest_run_mask(tapes: np.ndarray) -> np.ndarray:
    """Arm B (strict): longest run of active cells."""
    assert tapes.dtype == np.uint8
    is_active = _active_mask_mx(mx.array(tapes))
    mask = _longest_run_mask_mx(is_active)
    mx.eval(mask)
    return np.array(mask, dtype=bool)


def compute_longest_runnable_mask(tapes: np.ndarray) -> np.ndarray:
    """Arm BP (permeable): longest run of non-separator cells (NOP passes through)."""
    assert tapes.dtype == np.uint8
    is_runnable = _non_separator_mask_mx(mx.array(tapes))
    mask = _longest_run_mask_mx(is_runnable)
    mx.eval(mask)
    return np.array(mask, dtype=bool)


def extract_programs(
    tapes: np.ndarray, longest_mask: np.ndarray
) -> list[list[int]]:
    """Backend-agnostic: given (B, L) tapes and (B, L) mask, gather per row."""
    assert tapes.shape == longest_mask.shape
    programs: list[list[int]] = []
    for b in range(tapes.shape[0]):
        programs.append(tapes[b][longest_mask[b]].astype(np.int64).tolist())
    return programs
