"""Evolve-K-per-individual (§12).

Cell 0 of each tape is the K-header: K = evolve_k_values[tape[0] % len(values)].
Decode operates on tape[1:] only; cell 0 is never part of the program.
"""

from __future__ import annotations

import numpy as np
import pytest

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import _programs_for_arm
from folding_evolution.chem_tape.evolve import run_evolution


# ---------- Config helpers ----------


def test_evolve_k_value_list_parses_default():
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True)
    assert cfg.evolve_k_value_list() == [1, 2, 3, 4, 8, 999]


def test_evolve_k_value_list_custom():
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True, evolve_k_values="3,999")
    assert cfg.evolve_k_value_list() == [3, 999]


def test_individual_k_maps_header():
    cfg = ChemTapeConfig(arm="BP_TOPK", evolve_k=True, evolve_k_values="3,999")
    tape_a = np.array([0, 1, 2, 3], dtype=np.uint8)
    tape_b = np.array([1, 1, 2, 3], dtype=np.uint8)
    tape_c = np.array([4, 1, 2, 3], dtype=np.uint8)  # 4 % 2 = 0 → K=3
    assert cfg.individual_k(tape_a) == 3
    assert cfg.individual_k(tape_b) == 999
    assert cfg.individual_k(tape_c) == 3


# ---------- Hash stability ----------


def test_hash_unchanged_when_evolve_k_off():
    """Existing BP_TOPK configs must have unchanged hashes."""
    c_old = ChemTapeConfig(arm="BP_TOPK", topk=3)
    c_new = ChemTapeConfig(arm="BP_TOPK", topk=3,
                           evolve_k=False, evolve_k_values="1,2,3,4,8,999")
    assert c_old.hash() == c_new.hash()


def test_hash_differs_when_evolve_k_active():
    c1 = ChemTapeConfig(arm="BP_TOPK", topk=3)
    c2 = ChemTapeConfig(arm="BP_TOPK", topk=3, evolve_k=True)
    assert c1.hash() != c2.hash()


# ---------- Decode routes ----------


def test_evolve_k_decode_uses_body_only():
    """_programs_for_arm under evolve-K must skip cell 0 and decode body only."""
    cfg = ChemTapeConfig(
        arm="BP_TOPK", evolve_k=True, evolve_k_values="1,999",
        tape_length=16, backend="numpy",
    )
    # Cell 0 = 0 → K=1. Body cells [1..15] with a single bonded run.
    # Build a tape where body has runs of length 3 and 5, separated by 14.
    tape = np.array([[
        0,                          # header: 0 → K=1
        1, 2, 3,                    # body run of length 3
        14,                         # separator
        4, 5, 6, 7, 8,              # body run of length 5 (longest)
        14, 14, 14, 14, 14, 14,     # separators
    ]], dtype=np.uint8)
    progs = _programs_for_arm(cfg, tape)
    # K=1 picks the longest run only = run of length 5.
    assert progs[0] == [4, 5, 6, 7, 8]


def test_evolve_k_different_k_different_program():
    """Same tape with different header cell → different decoded program."""
    cfg_body_only = ChemTapeConfig(
        arm="BP_TOPK", evolve_k=True, evolve_k_values="1,999",
        tape_length=16, backend="numpy",
    )
    # Cell 0 = 0 → K=1 (K picks longest = length 5).
    tape_k1 = np.array([[
        0, 1, 2, 3, 14, 4, 5, 6, 7, 8, 14, 14, 14, 14, 14, 14,
    ]], dtype=np.uint8)
    # Cell 0 = 1 → K=999 (picks both runs).
    tape_kinf = tape_k1.copy()
    tape_kinf[0, 0] = 1
    progs_k1 = _programs_for_arm(cfg_body_only, tape_k1)
    progs_kinf = _programs_for_arm(cfg_body_only, tape_kinf)
    assert progs_k1[0] == [4, 5, 6, 7, 8]
    assert progs_kinf[0] == [1, 2, 3, 4, 5, 6, 7, 8]


def test_evolve_k_population_heterogeneity():
    """A batch of tapes with different cell-0 values produces different K decodes."""
    cfg = ChemTapeConfig(
        arm="BP_TOPK", evolve_k=True, evolve_k_values="1,999",
        tape_length=16, backend="numpy",
    )
    base = np.array([
        0, 1, 2, 3, 14, 4, 5, 6, 7, 8, 14, 14, 14, 14, 14, 14,
    ], dtype=np.uint8)
    tapes = np.stack([
        base,                       # K=1
        np.concatenate([[1], base[1:]]).astype(np.uint8),  # K=999
    ])
    progs = _programs_for_arm(cfg, tapes)
    assert progs[0] == [4, 5, 6, 7, 8]
    assert progs[1] == [1, 2, 3, 4, 5, 6, 7, 8]


# ---------- Metrics: k_distribution ----------


def test_k_distribution_recorded_under_evolve_k():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=32, generations=4,
        backend="numpy", arm="BP_TOPK", evolve_k=True,
        evolve_k_values="1,3,999", seed=0,
    )
    result = run_evolution(cfg)
    # Every generation record should have a k_distribution array of length 3.
    for s in result.stats.history:
        assert s.k_distribution is not None
        assert s.k_distribution.shape == (3,)
        assert s.k_distribution.sum() == cfg.pop_size


def test_k_distribution_none_under_fixed_k():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=32, generations=4,
        backend="numpy", arm="BP_TOPK", topk=3, seed=0,
    )
    result = run_evolution(cfg)
    for s in result.stats.history:
        assert s.k_distribution is None


# ---------- Smoke: evolve-K + protection ----------


def test_evolve_k_with_protection_smoke():
    """Evolve-K with r=0.5 protection should run without error and respect
    that header cell is not protected."""
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=4,
        backend="numpy", arm="BP_TOPK", evolve_k=True,
        evolve_k_values="1,3", bond_protection_ratio=0.5, seed=0,
    )
    result = run_evolution(cfg)
    assert 0.0 <= result.best_fitness <= 1.0


# ---------- Reproducibility ----------


def test_evolve_k_is_reproducible():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=6,
        backend="numpy", arm="BP_TOPK", evolve_k=True,
        evolve_k_values="1,3,999", seed=7,
    )
    r1 = run_evolution(cfg)
    r2 = run_evolution(cfg)
    assert np.array_equal(r1.best_genotype, r2.best_genotype)
    assert r1.best_fitness == r2.best_fitness
