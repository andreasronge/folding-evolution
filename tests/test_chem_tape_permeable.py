"""Permeable bond rule (Arm BP): id 0 (NOP) passes through bonded runs,
ids 14 and 15 remain hard separators.
"""

import numpy as np
import pytest

from folding_evolution.chem_tape import alphabet as alph
from folding_evolution.chem_tape import engine_numpy, engine_mlx, engine
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import _programs_for_arm


# ---------- Predicate masks ----------


def test_non_separator_mask_covers_ids_0_to_13():
    tape = np.arange(16, dtype=np.uint8)[None, :]
    mask = engine_numpy.compute_non_separator_mask(tape)
    expected = np.zeros(16, dtype=bool)
    expected[0:14] = True       # 0..13 are non-separator
    assert np.array_equal(mask[0], expected)


def test_strict_active_mask_excludes_nop():
    """Sanity: v1 strict mask excludes id 0 (NOP), which permeable includes."""
    tape = np.arange(16, dtype=np.uint8)[None, :]
    strict = engine_numpy.compute_active_mask(tape)
    perm = engine_numpy.compute_non_separator_mask(tape)
    # Strict and permeable differ on id 0 (NOP): strict False, perm True.
    assert not strict[0, 0] and perm[0, 0]
    # On ids 1..13: both masks True.
    assert strict[0, 1:14].all() and perm[0, 1:14].all()
    # On ids 14, 15: both masks False.
    assert not strict[0, 14:].any() and not perm[0, 14:].any()


# ---------- Longest-runnable mask semantics ----------


def test_permeable_bridges_single_nop():
    """Strict rule: [1, 2, 0, 3, 4] splits into two runs. Permeable: one run of 5.

    Trailing cells padded with id 15 (separator) so the post-separator region is empty
    and only the designed runs compete for "longest".
    """
    tape = np.array([[1, 2, 0, 3, 4, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]], dtype=np.uint8)
    strict = engine_numpy.compute_longest_run_mask(tape)
    perm = engine_numpy.compute_longest_runnable_mask(tape)

    # Strict: two runs of length 2 ([1,2] and [3,4]); leftmost wins.
    expected_strict = np.zeros(16, dtype=bool)
    expected_strict[0:2] = True
    assert np.array_equal(strict[0], expected_strict)

    # Permeable: cells 0..4 (length 5, including NOP at cell 2) — the only runnable segment.
    expected_perm = np.zeros(16, dtype=bool)
    expected_perm[0:5] = True
    assert np.array_equal(perm[0], expected_perm)


def test_permeable_breaks_at_separator():
    """Id 14 is a hard boundary even under the permeable rule."""
    tape = np.array([[1, 2, 3, 14, 4, 5, 6, 7, 15, 15, 15, 15, 15, 15, 15, 15]], dtype=np.uint8)
    perm = engine_numpy.compute_longest_runnable_mask(tape)
    expected = np.zeros(16, dtype=bool)
    expected[4:8] = True   # 4..7 (length 4) vs 0..2 (length 3) → rightmost wins by length
    assert np.array_equal(perm[0], expected)


def test_permeable_excludes_all_separator_tape():
    tape = np.array([[14, 15, 14, 15, 14, 15, 14, 15, 14, 15, 14, 15, 14, 15, 14, 15]], dtype=np.uint8)
    perm = engine_numpy.compute_longest_runnable_mask(tape)
    assert not perm.any()


def test_permeable_all_nop_tape_is_one_run():
    """An all-NOP tape has one big runnable segment (all 16 cells), all executing as NOP."""
    tape = np.zeros((1, 16), dtype=np.uint8)
    perm = engine_numpy.compute_longest_runnable_mask(tape)
    assert perm[0].all()


def test_permeable_tape_without_separators_equals_full_tape():
    """A tape with no ids 14 or 15 → the whole tape is one runnable segment → Arm BP ≈ Arm A."""
    tape = np.array([[1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 7, 8, 9, 10, 11]], dtype=np.uint8)
    perm = engine_numpy.compute_longest_runnable_mask(tape)
    assert perm[0].all()


# ---------- NumPy ↔ MLX parity ----------


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
def test_permeable_numpy_mlx_identical(seed):
    rng = np.random.default_rng(seed)
    tapes = rng.integers(0, 16, size=(32, 32), dtype=np.uint8)
    m_np = engine_numpy.compute_longest_runnable_mask(tapes)
    m_mx = engine_mlx.compute_longest_runnable_mask(tapes)
    assert np.array_equal(m_np, m_mx), (
        f"permeable mask diverges at seed={seed}: "
        f"rows differing = {np.where(~(m_np == m_mx).all(axis=1))[0].tolist()[:5]}"
    )


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
def test_non_separator_mask_numpy_mlx_identical(seed):
    rng = np.random.default_rng(seed)
    tapes = rng.integers(0, 16, size=(32, 32), dtype=np.uint8)
    m_np = engine_numpy.compute_non_separator_mask(tapes)
    m_mx = engine_mlx.compute_non_separator_mask(tapes)
    assert np.array_equal(m_np, m_mx)


# ---------- Arm-level equivalences ----------


def test_bp_on_separator_free_tape_equals_arm_a():
    """Spec §Layer 9 analog: on a tape with no separators, Arm BP = Arm A."""
    tape = np.array([[1, 2, 3, 4, 5, 0, 6, 7, 0, 8, 9, 10, 11, 12, 13, 0]], dtype=np.uint8)

    cfg_a = ChemTapeConfig(tape_length=16, arm="A", backend="numpy")
    cfg_bp = ChemTapeConfig(tape_length=16, arm="BP", backend="numpy")

    prog_a = _programs_for_arm(cfg_a, tape)
    prog_bp = _programs_for_arm(cfg_bp, tape)

    assert prog_a == prog_bp
    assert prog_bp[0] == tape[0].tolist()


def test_bp_differs_from_b_when_nop_internal():
    """Arm B strict prunes NOP cells; Arm BP includes them as pass-through."""
    # Pad post-separator region with id-15 separators so only cells 0..4 qualify.
    tape = np.array([[1, 2, 0, 3, 4, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]], dtype=np.uint8)

    cfg_b = ChemTapeConfig(tape_length=16, arm="B", backend="numpy")
    cfg_bp = ChemTapeConfig(tape_length=16, arm="BP", backend="numpy")

    prog_b = _programs_for_arm(cfg_b, tape)[0]
    prog_bp = _programs_for_arm(cfg_bp, tape)[0]

    # Strict picks a length-2 run (leftmost tie); permeable picks cells 0..4 (length 5 incl NOP).
    assert prog_b == [1, 2]
    assert prog_bp == [1, 2, 0, 3, 4]


def test_bp_engine_dispatcher_routes_to_mlx():
    """Dispatcher correctness for backend='mlx'."""
    rng = np.random.default_rng(0)
    tapes = rng.integers(0, 16, size=(4, 32), dtype=np.uint8)
    mask_np = engine.compute_longest_runnable_mask(tapes, backend="numpy")
    mask_mx = engine.compute_longest_runnable_mask(tapes, backend="mlx")
    assert np.array_equal(mask_np, mask_mx)


# ---------- Smoke test: evolution under Arm BP runs ----------


def test_arm_bp_smoke_numpy():
    """Arm BP runs to completion on count_r without error."""
    from folding_evolution.chem_tape.evolve import run_evolution

    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16,
        holdout_size=0,
        tape_length=16,
        pop_size=16,
        generations=4,
        backend="numpy",
        arm="BP",
        seed=0,
    )
    result = run_evolution(cfg)
    assert 0.0 <= result.best_fitness <= 1.0
    # Arm BP programs should contain NOP (id 0) more often than Arm B programs.
    # Not guaranteed every run, but the *possibility* exists — structural check only.
