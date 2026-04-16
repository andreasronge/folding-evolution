"""Tests for §v2.4-proxy-4 seeded-initialization infrastructure."""

from __future__ import annotations

import pytest
import random

import numpy as np

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import (
    _parse_seed_tapes,
    build_initial_population,
    run_evolution,
)


# 12-token canonical AND body for §v2.4 task:
#   CONST_0 INPUT REDUCE_MAX CONST_5 GT  INPUT SUM CONST_5 CONST_5 ADD GT  IF_GT
# Token ids: 2, 1, 18, 16, 8, 1, 5, 16, 16, 7, 8, 17.
CANONICAL_AND_12TOK_HEX = "020112100801051010070811"


def test_empty_seed_tapes_returns_empty_list():
    cfg = ChemTapeConfig(alphabet="v2_probe", tape_length=32)
    assert _parse_seed_tapes(cfg) == []


def test_parse_single_seed_tape():
    cfg = ChemTapeConfig(
        alphabet="v2_probe",
        tape_length=32,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
    )
    seeds = _parse_seed_tapes(cfg)
    assert len(seeds) == 1
    seed = seeds[0]
    assert seed.shape == (32,)
    assert seed.dtype == np.uint8
    # First 12 bytes match the canonical body; remainder are NOP (0).
    expected_prefix = [2, 1, 18, 16, 8, 1, 5, 16, 16, 7, 8, 17]
    assert list(seed[:12]) == expected_prefix
    assert list(seed[12:]) == [0] * 20


def test_parse_multiple_seed_tapes():
    two = f"{CANONICAL_AND_12TOK_HEX},{CANONICAL_AND_12TOK_HEX}"
    cfg = ChemTapeConfig(
        alphabet="v2_probe",
        tape_length=32,
        seed_tapes=two,
    )
    seeds = _parse_seed_tapes(cfg)
    assert len(seeds) == 2


def test_seed_tape_too_long_raises():
    # Tape length 8, but hex has 12 bytes.
    cfg = ChemTapeConfig(
        alphabet="v2_probe",
        tape_length=8,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
    )
    with pytest.raises(ValueError, match="longer seeds"):
        _parse_seed_tapes(cfg)


def test_seed_tape_invalid_hex_raises():
    cfg = ChemTapeConfig(
        alphabet="v2_probe",
        tape_length=32,
        seed_tapes="not-hex",
    )
    with pytest.raises(ValueError, match="valid hex"):
        _parse_seed_tapes(cfg)


def test_seed_token_out_of_alphabet_raises():
    # v1 alphabet caps at id 15; token id 18 (REDUCE_MAX) is a v2-only id.
    cfg = ChemTapeConfig(
        alphabet="v1",
        tape_length=32,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
    )
    with pytest.raises(ValueError, match="token_max"):
        _parse_seed_tapes(cfg)


def test_build_initial_population_without_seeds():
    cfg = ChemTapeConfig(alphabet="v2_probe", tape_length=32, pop_size=16)
    rng = random.Random(42)
    pop = build_initial_population(cfg, rng, cfg.pop_size)
    assert len(pop) == 16
    assert all(g.shape == (32,) for g in pop)
    # Uniform-random should produce variety.
    uniq = {tuple(int(b) for b in g) for g in pop}
    assert len(uniq) == 16


def test_build_initial_population_seed_fraction_1():
    # seed_fraction=1.0 → every individual is a copy of a seed.
    cfg = ChemTapeConfig(
        alphabet="v2_probe",
        tape_length=32,
        pop_size=16,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
        seed_fraction=1.0,
    )
    rng = random.Random(42)
    pop = build_initial_population(cfg, rng, cfg.pop_size)
    assert len(pop) == 16
    for g in pop:
        assert list(g[:12]) == [2, 1, 18, 16, 8, 1, 5, 16, 16, 7, 8, 17]
        assert list(g[12:]) == [0] * 20


def test_build_initial_population_seed_fraction_half():
    cfg = ChemTapeConfig(
        alphabet="v2_probe",
        tape_length=32,
        pop_size=100,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
        seed_fraction=0.5,
    )
    rng = random.Random(42)
    pop = build_initial_population(cfg, rng, cfg.pop_size)
    assert len(pop) == 100
    expected = np.array([2, 1, 18, 16, 8, 1, 5, 16, 16, 7, 8, 17], dtype=np.uint8)
    n_seeded = sum(1 for g in pop if np.array_equal(g[:12], expected) and (g[12:] == 0).all())
    # Exactly round(0.5 * 100) = 50 should be seeded.
    assert n_seeded == 50


def test_build_initial_population_incompatible_evolve_k_raises():
    cfg = ChemTapeConfig(
        alphabet="v2_probe",
        tape_length=32,
        pop_size=16,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
        seed_fraction=0.1,
        evolve_k=True,
    )
    rng = random.Random(0)
    with pytest.raises(ValueError, match="incompatible with evolve_k"):
        build_initial_population(cfg, rng, cfg.pop_size)


def test_seed_fraction_out_of_range_raises():
    cfg = ChemTapeConfig(
        alphabet="v2_probe",
        tape_length=32,
        pop_size=16,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
        seed_fraction=1.5,
    )
    rng = random.Random(0)
    with pytest.raises(ValueError, match="must be in"):
        build_initial_population(cfg, rng, cfg.pop_size)


def test_hash_stable_when_seeding_disabled():
    # Pre-feature configs must produce identical hashes with the new fields at defaults.
    a = ChemTapeConfig(alphabet="v2_probe", tape_length=32)
    b = ChemTapeConfig(alphabet="v2_probe", tape_length=32, seed_tapes="", seed_fraction=0.0)
    assert a.hash() == b.hash()


def test_hash_changes_when_seeding_enabled():
    a = ChemTapeConfig(alphabet="v2_probe", tape_length=32)
    b = ChemTapeConfig(
        alphabet="v2_probe",
        tape_length=32,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
        seed_fraction=0.01,
    )
    assert a.hash() != b.hash()


def test_seeded_run_evolution_smoke():
    # End-to-end: a short run with seeded initialization completes and returns results.
    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16,
        holdout_size=0,
        alphabet="v2_probe",
        tape_length=32,
        pop_size=16,
        generations=4,
        backend="numpy",
        arm="B",
        seed=0,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
        seed_fraction=0.5,
    )
    result = run_evolution(cfg)
    assert result.generations_run == 4
    assert len(result.stats.history) == 5  # gen 0 + 4 evolved


def test_disable_early_termination_default_behavior():
    # §v2.4-proxy-4b: with seeded canonical body and default disable_early_termination=False,
    # the GA terminates at gen 1 (current §v2.4-proxy-4 signature).
    cfg = ChemTapeConfig(
        task="sum_gt_10_AND_max_gt_5",
        n_examples=16,
        holdout_size=0,
        alphabet="v2_probe",
        tape_length=32,
        pop_size=16,
        generations=10,
        backend="numpy",
        arm="BP_TOPK",
        topk=3,
        bond_protection_ratio=0.5,
        seed=0,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
        seed_fraction=1.0,  # every individual is the canonical body
    )
    result = run_evolution(cfg)
    # Early-term triggers at gen 1 with default disable_early_termination=False
    assert result.generations_run == 1, f"expected early-term at gen 1, got {result.generations_run}"


def test_disable_early_termination_runs_full_horizon():
    # §v2.4-proxy-4b: with disable_early_termination=True, GA runs all `generations`
    # even when fitness hits 1.0 at gen 0.
    cfg = ChemTapeConfig(
        task="sum_gt_10_AND_max_gt_5",
        n_examples=16,
        holdout_size=0,
        alphabet="v2_probe",
        tape_length=32,
        pop_size=16,
        generations=10,
        backend="numpy",
        arm="BP_TOPK",
        topk=3,
        bond_protection_ratio=0.5,
        seed=0,
        seed_tapes=CANONICAL_AND_12TOK_HEX,
        seed_fraction=1.0,
        disable_early_termination=True,
    )
    result = run_evolution(cfg)
    assert result.generations_run == 10, f"expected full 10 gens, got {result.generations_run}"
    # History should have gen 0 + 10 evolved gens
    assert len(result.stats.history) == 11


def test_hash_stable_when_disable_early_term_off():
    # Regression: pre-v2.4-proxy-4b configs must produce identical hashes with the
    # new field at default.
    a = ChemTapeConfig(alphabet="v2_probe", tape_length=32)
    b = ChemTapeConfig(alphabet="v2_probe", tape_length=32, disable_early_termination=False)
    assert a.hash() == b.hash()


def test_hash_changes_when_disable_early_term_on():
    a = ChemTapeConfig(alphabet="v2_probe", tape_length=32)
    b = ChemTapeConfig(alphabet="v2_probe", tape_length=32, disable_early_termination=True)
    assert a.hash() != b.hash()
