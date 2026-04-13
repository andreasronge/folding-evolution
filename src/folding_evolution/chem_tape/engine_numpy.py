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

from .alphabet import ACTIVE_MASK, NON_SEPARATOR_MASK


def compute_active_mask(tapes: np.ndarray) -> np.ndarray:
    """(B, L) uint8 in [0, 16) → (B, L) bool. True iff token id ∈ {1..13}."""
    assert tapes.dtype == np.uint8
    return ACTIVE_MASK[tapes]


def compute_non_separator_mask(tapes: np.ndarray) -> np.ndarray:
    """(B, L) uint8 → (B, L) bool. True iff token id ∉ {14, 15} (permeable rule)."""
    assert tapes.dtype == np.uint8
    return NON_SEPARATOR_MASK[tapes]


def _shift_right_pad0(m: np.ndarray) -> np.ndarray:
    """Shift along axis=1 by 1, with zero-pad on the left. (B, L) bool → (B, L) bool."""
    out = np.zeros_like(m)
    out[:, 1:] = m[:, :-1]
    return out


def _longest_run_under_mask(eligible: np.ndarray) -> np.ndarray:
    """Return the (B, L) bool mask picking the leftmost-longest run of True cells.

    Shared spec §Layer 6 algorithm; parameterized by which cells are eligible
    to be part of a run. Arm B uses is_active; Arm BP uses is_non_separator.
    """
    B, L = eligible.shape

    run_start = eligible & ~_shift_right_pad0(eligible)          # (B, L) bool
    run_id = np.cumsum(run_start.astype(np.int32), axis=1) * eligible.astype(np.int32)

    lengths = np.zeros((B, L + 1), dtype=np.int32)
    for b in range(B):
        lengths[b] = np.bincount(run_id[b], minlength=L + 1)

    best_run = np.argmax(lengths[:, 1:], axis=1) + 1             # (B,)
    any_eligible = eligible.any(axis=1)
    best_run = np.where(any_eligible, best_run, 0)

    return (run_id == best_run[:, None]) & eligible              # (B, L) bool


def compute_longest_run_mask(tapes: np.ndarray) -> np.ndarray:
    """Arm B (strict): longest contiguous run of *active* cells (ids 1..13)."""
    return _longest_run_under_mask(compute_active_mask(tapes))


def compute_longest_runnable_mask(tapes: np.ndarray) -> np.ndarray:
    """Arm BP (permeable): longest contiguous run of *non-separator* cells
    (ids 0..13). Id 0 (NOP) passes through bonded runs as a no-op; ids 14
    and 15 remain hard boundaries.
    """
    return _longest_run_under_mask(compute_non_separator_mask(tapes))


def extract_programs(
    tapes: np.ndarray, longest_mask: np.ndarray
) -> list[list[int]]:
    """Pick out the tokens inside the longest-run mask for each row, in tape order."""
    assert tapes.shape == longest_mask.shape
    programs: list[list[int]] = []
    for b in range(tapes.shape[0]):
        programs.append(tapes[b][longest_mask[b]].astype(np.int64).tolist())
    return programs
