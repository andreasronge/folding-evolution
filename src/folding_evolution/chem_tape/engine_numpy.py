"""Reference chem-tape v1 engine (NumPy).

Batch axis B typically flattens (population). Input tapes are (B, L) uint8 with
token ids in {0..15}. The engine produces, for each row, the boolean mask of
cells in the *longest* active run (spec §Layer 5).

Algorithm (spec §Layer 6):
  1. is_active    = ACTIVE_MASK[token]                       (B, L) bool
  2. run_start    = is_active & ~shift_right_pad0(is_active) (B, L) bool
  3. run_id       = cumsum(run_start, axis=1) * is_active    (B, L) int
  4. lengths[b,k] = count of cells with run_id == k          (B, L+1) int
  5. best_run     = argmax(lengths[:, 1:], axis=1) + 1       (B,)  (ties → leftmost)
  6. active_best  = (run_id == best_run[:, None]) & is_active (B, L) bool
"""

from __future__ import annotations

import numpy as np

from .alphabet import ACTIVE_MASK


def compute_active_mask(tapes: np.ndarray) -> np.ndarray:
    """(B, L) uint8 in [0, 16) → (B, L) bool. True iff token id ∈ {1..13}."""
    assert tapes.dtype == np.uint8
    return ACTIVE_MASK[tapes]


def _shift_right_pad0(m: np.ndarray) -> np.ndarray:
    """Shift along axis=1 by 1, with zero-pad on the left. (B, L) bool → (B, L) bool."""
    out = np.zeros_like(m)
    out[:, 1:] = m[:, :-1]
    return out


def compute_longest_run_mask(tapes: np.ndarray) -> np.ndarray:
    """Return a (B, L) bool mask picking out the leftmost-longest active run per row."""
    is_active = compute_active_mask(tapes)                      # (B, L) bool
    B, L = is_active.shape

    run_start = is_active & ~_shift_right_pad0(is_active)        # (B, L) bool
    run_id = np.cumsum(run_start.astype(np.int32), axis=1) * is_active.astype(np.int32)

    # lengths[b, k] = cells with run_id == k (run_id=0 means "inactive").
    lengths = np.zeros((B, L + 1), dtype=np.int32)
    for b in range(B):
        # np.bincount is ~2x faster than a scatter-add loop and keeps this readable.
        lengths[b] = np.bincount(run_id[b], minlength=L + 1)

    # Best run id per row; ties → leftmost (argmax returns first occurrence).
    best_run = np.argmax(lengths[:, 1:], axis=1) + 1             # (B,)

    # If lengths[:, 1:] is all-zero (no active cells), argmax returns 0 → best_run=1,
    # but run_id never equals 1 in that row, so the mask is all-False. Explicitly
    # zero such rows so downstream behaviour is unambiguous.
    any_active = is_active.any(axis=1)                           # (B,)
    best_run = np.where(any_active, best_run, 0)                 # 0 → mask all-False

    active_best = (run_id == best_run[:, None]) & is_active       # (B, L) bool
    return active_best


def extract_programs(
    tapes: np.ndarray, longest_mask: np.ndarray
) -> list[list[int]]:
    """Pick out the tokens inside the longest-run mask for each row, in tape order."""
    assert tapes.shape == longest_mask.shape
    programs: list[list[int]] = []
    for b in range(tapes.shape[0]):
        programs.append(tapes[b][longest_mask[b]].astype(np.int64).tolist())
    return programs
