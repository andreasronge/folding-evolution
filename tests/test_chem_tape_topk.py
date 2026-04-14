"""Top-K permeable decode (Arm BP_TOPK). experiments.md §8.

Contract:
  - K=1 reduces to Arm BP (leftmost-longest non-separator run).
  - K ≥ number_of_runs equals the full non-separator mask (every bonded
    cell executes; separators 14/15 still gate).
  - Top-K tie-break: leftmost wins (stable argsort on -length).
  - NumPy and MLX backends return identical masks (MLX delegates).
"""

import numpy as np
import pytest

from folding_evolution.chem_tape import engine, engine_mlx, engine_numpy
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import _programs_for_arm


# ---------- K=1 reduces to BP ----------


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
def test_topk_k1_matches_longest_runnable(seed):
    rng = np.random.default_rng(seed)
    tapes = rng.integers(0, 16, size=(64, 32), dtype=np.uint8)
    bp = engine_numpy.compute_longest_runnable_mask(tapes)
    topk1 = engine_numpy.compute_topk_runnable_mask(tapes, k=1)
    assert np.array_equal(bp, topk1)


# ---------- K large equals full non-separator mask ----------


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
def test_topk_kbig_equals_non_separator_mask(seed):
    rng = np.random.default_rng(seed)
    tapes = rng.integers(0, 16, size=(64, 32), dtype=np.uint8)
    non_sep = engine_numpy.compute_non_separator_mask(tapes)
    topk_big = engine_numpy.compute_topk_runnable_mask(tapes, k=999)
    assert np.array_equal(non_sep, topk_big)


# ---------- Tape-level structural cases ----------


def test_topk_k2_picks_two_longest_runs():
    """Tape with three distinct run lengths — K=2 must pick the two longest."""
    # Runs: [1,2] (len 2) | sep 14 | [3,4,5,6] (len 4) | sep 15 | [7,8,9] (len 3) | pad.
    tape = np.array([[
        1, 2, 14, 3, 4, 5, 6, 15, 7, 8, 9, 14, 14, 14, 14, 14,
    ]], dtype=np.uint8)
    m = engine_numpy.compute_topk_runnable_mask(tape, k=2)
    expected = np.zeros(16, dtype=bool)
    expected[3:7] = True    # run of 4
    expected[8:11] = True   # run of 3
    assert np.array_equal(m[0], expected)


def test_topk_tiebreak_leftmost():
    """Two runs of equal length — K=1 picks leftmost."""
    tape = np.array([[
        1, 2, 3, 14, 4, 5, 6, 14, 14, 14, 14, 14, 14, 14, 14, 14,
    ]], dtype=np.uint8)
    m = engine_numpy.compute_topk_runnable_mask(tape, k=1)
    expected = np.zeros(16, dtype=bool)
    expected[0:3] = True
    assert np.array_equal(m[0], expected)


def test_topk_tape_order_preserved_in_extraction():
    """Tokens are extracted in tape position order regardless of run length ordering."""
    # Shorter run [9,10] comes first in tape; longer run [1,2,3,4] comes second.
    tape = np.array([[
        9, 10, 14, 1, 2, 3, 4, 14, 14, 14, 14, 14, 14, 14, 14, 14,
    ]], dtype=np.uint8)
    m = engine_numpy.compute_topk_runnable_mask(tape, k=2)
    programs = engine_numpy.extract_programs(tape, m)
    # Tape order: shorter run's tokens first, longer run's tokens after.
    assert programs[0] == [9, 10, 1, 2, 3, 4]


def test_topk_k_larger_than_run_count():
    """K > number of runs ⇒ all runs included, mask == non-separator."""
    tape = np.array([[
        1, 2, 14, 3, 4, 15, 5, 14, 14, 14, 14, 14, 14, 14, 14, 14,
    ]], dtype=np.uint8)
    m = engine_numpy.compute_topk_runnable_mask(tape, k=999)
    expected = engine_numpy.compute_non_separator_mask(tape)
    assert np.array_equal(m, expected)


def test_topk_empty_tape():
    """All-separator tape ⇒ empty mask at any K."""
    tape = np.full((1, 16), 14, dtype=np.uint8)
    m = engine_numpy.compute_topk_runnable_mask(tape, k=5)
    assert not m.any()


# ---------- NumPy ↔ MLX parity (MLX delegates) ----------


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
@pytest.mark.parametrize("k", [1, 2, 3, 4, 8, 999])
def test_topk_numpy_mlx_identical(seed, k):
    rng = np.random.default_rng(seed)
    tapes = rng.integers(0, 16, size=(32, 32), dtype=np.uint8)
    m_np = engine_numpy.compute_topk_runnable_mask(tapes, k=k)
    m_mx = engine_mlx.compute_topk_runnable_mask(tapes, k=k)
    assert np.array_equal(m_np, m_mx)


def test_topk_dispatcher_routes():
    rng = np.random.default_rng(0)
    tapes = rng.integers(0, 16, size=(4, 32), dtype=np.uint8)
    m_np = engine.compute_topk_runnable_mask(tapes, k=3, backend="numpy")
    m_mx = engine.compute_topk_runnable_mask(tapes, k=3, backend="mlx")
    assert np.array_equal(m_np, m_mx)


# ---------- Arm-level equivalence ----------


def test_arm_bp_topk_k1_equals_arm_bp():
    """Arm BP_TOPK with K=1 produces identical programs to Arm BP."""
    rng = np.random.default_rng(0)
    tapes = rng.integers(0, 16, size=(16, 32), dtype=np.uint8)

    cfg_bp = ChemTapeConfig(arm="BP", backend="numpy")
    cfg_topk1 = ChemTapeConfig(arm="BP_TOPK", topk=1, backend="numpy")

    progs_bp = _programs_for_arm(cfg_bp, tapes)
    progs_topk1 = _programs_for_arm(cfg_topk1, tapes)
    assert progs_bp == progs_topk1


def test_arm_bp_topk_kbig_includes_all_bonded_cells():
    """At large K, BP_TOPK's programs contain every non-separator token in tape order."""
    tape = np.array([[
        1, 2, 0, 3, 14, 4, 5, 6, 15, 7, 0, 8, 14, 14, 14, 14,
    ]], dtype=np.uint8)
    cfg = ChemTapeConfig(arm="BP_TOPK", topk=999, backend="numpy")
    prog = _programs_for_arm(cfg, tape)[0]
    # Tape order over non-separator cells: 1,2,0,3,4,5,6,7,0,8
    assert prog == [1, 2, 0, 3, 4, 5, 6, 7, 0, 8]


# ---------- Smoke test: evolution under BP_TOPK runs ----------


@pytest.mark.parametrize("k", [1, 2, 4])
def test_bp_topk_smoke_numpy(k):
    from folding_evolution.chem_tape.evolve import run_evolution

    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16,
        holdout_size=0,
        tape_length=16,
        pop_size=16,
        generations=4,
        backend="numpy",
        arm="BP_TOPK",
        topk=k,
        seed=0,
    )
    result = run_evolution(cfg)
    assert 0.0 <= result.best_fitness <= 1.0


# ---------- Config hash: BP_TOPK distinct by K, non-TOPK unaffected ----------


def test_hash_bp_topk_differs_by_k():
    c1 = ChemTapeConfig(arm="BP_TOPK", topk=1)
    c2 = ChemTapeConfig(arm="BP_TOPK", topk=2)
    assert c1.hash() != c2.hash()


def test_hash_non_topk_unaffected_by_topk_field():
    """Existing A/B/BP hashes must not change after adding `topk` to the config."""
    c_base = ChemTapeConfig(arm="BP", topk=1)
    c_other = ChemTapeConfig(arm="BP", topk=99)
    assert c_base.hash() == c_other.hash()
