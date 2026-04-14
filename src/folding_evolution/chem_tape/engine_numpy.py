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


def _topk_runs_under_mask(eligible: np.ndarray, k: int) -> np.ndarray:
    """Return the (B, L) bool mask selecting cells in the K longest runs of
    True cells in `eligible`. Runs are emitted in tape order (a cell is True in
    the output iff its run is among the top K by length, with leftmost
    tiebreak on equal lengths). K=1 reduces to `_longest_run_under_mask`;
    K ≥ (number of runs) selects all non-empty runs (equals `eligible` itself).

    Experiments.md §8.
    """
    assert k >= 1
    B, L = eligible.shape

    run_start = eligible & ~_shift_right_pad0(eligible)
    run_id = np.cumsum(run_start.astype(np.int32), axis=1) * eligible.astype(np.int32)

    out = np.zeros_like(eligible)
    run_ids_all = np.arange(1, L + 1, dtype=np.int32)
    for b in range(B):
        lengths = np.bincount(run_id[b], minlength=L + 1)[1:]   # lengths of runs 1..L
        valid = lengths > 0
        if not valid.any():
            continue
        valid_ids = run_ids_all[valid]                          # ascending = leftmost first
        valid_lengths = lengths[valid]
        # Stable sort on -length preserves ascending run_id among ties → leftmost tiebreak.
        order = np.argsort(-valid_lengths, kind="stable")
        chosen_ids = valid_ids[order[: min(k, valid_ids.size)]]
        out[b] = np.isin(run_id[b], chosen_ids) & eligible[b]
    return out


def compute_topk_runnable_mask(tapes: np.ndarray, k: int) -> np.ndarray:
    """Arm BP_TOPK: K longest non-separator runs, concatenated in tape order
    on extraction. At K=1 identical to `compute_longest_runnable_mask` (Arm BP).
    At K ≥ number-of-runs, mask equals the non-separator mask (every bonded
    cell executes). Separator cells (ids 14, 15) never participate.
    """
    return _topk_runs_under_mask(compute_non_separator_mask(tapes), k)


def extract_programs(
    tapes: np.ndarray, longest_mask: np.ndarray
) -> list[list[int]]:
    """Pick out the tokens inside the longest-run mask for each row, in tape order."""
    assert tapes.shape == longest_mask.shape
    programs: list[list[int]] = []
    for b in range(tapes.shape[0]):
        programs.append(tapes[b][longest_mask[b]].astype(np.int64).tolist())
    return programs
