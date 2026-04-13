"""Chem-tape engine: active mask + longest-run extraction on hand-built tapes."""

import numpy as np

from folding_evolution.chem_tape import alphabet as alph
from folding_evolution.chem_tape import engine_numpy


def _tape(ids, L=16, pad_id=0):
    arr = np.full(L, pad_id, dtype=np.uint8)
    arr[: len(ids)] = ids
    return arr


def test_active_mask_marks_1_through_13_active():
    tape = np.arange(16, dtype=np.uint8)[None, :]
    mask = engine_numpy.compute_active_mask(tape)
    expected = np.zeros(16, dtype=bool)
    expected[1:14] = True
    assert np.array_equal(mask[0], expected)


def test_longest_run_empty_tape():
    tape = np.zeros((1, 16), dtype=np.uint8)
    mask = engine_numpy.compute_longest_run_mask(tape)
    assert not mask.any()


def test_longest_run_single_active_run():
    # [0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    tape = np.zeros((1, 16), dtype=np.uint8)
    tape[0, 1:4] = [1, 2, 3]
    mask = engine_numpy.compute_longest_run_mask(tape)
    expected = np.zeros(16, dtype=bool)
    expected[1:4] = True
    assert np.array_equal(mask[0], expected)


def test_longest_run_picks_the_longest_of_several():
    """Worked example from spec §Layer 5 (with slot 12 = MAP_EQ_R)."""
    # idx:   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
    # token: 1  4 12  5  0  0  1  4 12  6  8  0  2  7  0  0
    tape = np.array(
        [[1, 4, 12, 5, 0, 0, 1, 4, 12, 6, 8, 0, 2, 7, 0, 0]],
        dtype=np.uint8,
    )
    mask = engine_numpy.compute_longest_run_mask(tape)
    # Runs:
    #   0–3 (length 4)
    #   6–10 (length 5) ← longest
    #   12–13 (length 2)
    expected = np.zeros(16, dtype=bool)
    expected[6:11] = True
    assert np.array_equal(mask[0], expected)

    programs = engine_numpy.extract_programs(tape, mask)
    assert programs[0] == [1, 4, 12, 6, 8]
    # Spec names: [INPUT, CHARS, MAP_EQ_R, ANY, GT]


def test_longest_run_ties_take_leftmost():
    # Two runs of length 3: 1-3 and 5-7. Leftmost wins.
    tape = np.array(
        [[0, 1, 2, 3, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0]],
        dtype=np.uint8,
    )
    mask = engine_numpy.compute_longest_run_mask(tape)
    expected = np.zeros(16, dtype=bool)
    expected[1:4] = True
    assert np.array_equal(mask[0], expected)


def test_reserved_ids_are_inactive():
    # Ids 14 and 15 must NOT bond — they count as inactive.
    tape = np.array(
        [[1, 14, 2, 15, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
        dtype=np.uint8,
    )
    mask = engine_numpy.compute_longest_run_mask(tape)
    # Three runs of length 1 each; leftmost wins.
    expected = np.zeros(16, dtype=bool)
    expected[0] = True
    assert np.array_equal(mask[0], expected)


def test_multi_row_independent():
    tape = np.array(
        [
            [1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 4, 5, 6, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        dtype=np.uint8,
    )
    mask = engine_numpy.compute_longest_run_mask(tape)
    expected = np.zeros((2, 16), dtype=bool)
    expected[0, 0:3] = True
    expected[1, 3:7] = True
    assert np.array_equal(mask, expected)
