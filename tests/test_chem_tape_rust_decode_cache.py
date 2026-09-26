"""Parity for the native top-K hot path and optional prediction cache."""

import numpy as np
import pytest

from folding_evolution.chem_tape import evaluate, evolve
from folding_evolution.chem_tape.config import ChemTapeConfig


@pytest.mark.skipif(evaluate._rust_decode_topk is None, reason="native decoder unavailable")
@pytest.mark.parametrize("evolve_k", [False, True])
@pytest.mark.parametrize("k", [1, 3, 999])
def test_native_topk_matches_numpy(monkeypatch, evolve_k, k):
    cfg = ChemTapeConfig(arm="BP_TOPK", topk=k, evolve_k=evolve_k, backend="numpy")
    tapes = np.random.default_rng(17).integers(0, 22, (80, 32), dtype=np.uint8)
    tapes[0] = 14  # no eligible run
    tapes[1] = [1, 2, 14, 3, 4, 15, 5, 6] * 4  # repeated ties
    native = evaluate._programs_for_arm(cfg, tapes)
    monkeypatch.setattr(evaluate, "_rust_decode_topk", None)
    reference = evaluate._programs_for_arm(cfg, tapes)
    assert native == reference


@pytest.mark.skipif(evolve._rust_topk_mask is None, reason="native mask unavailable")
@pytest.mark.parametrize("k", [1, 3, 999])
def test_native_mutation_mask_preserves_rng_and_tape(monkeypatch, k):
    import random

    cfg = ChemTapeConfig(
        arm="BP_TOPK", topk=k, bond_protection_ratio=0.5,
        mutation_rate=0.2, backend="numpy",
    )
    tape = np.random.default_rng(9).integers(0, 22, 32, dtype=np.uint8)
    native_rng = random.Random(41)
    native = evolve.mutate(tape, cfg, native_rng)
    native_state = native_rng.getstate()
    monkeypatch.setattr(evolve, "_rust_topk_mask", None)
    reference_rng = random.Random(41)
    reference = evolve.mutate(tape, cfg, reference_rng)
    assert np.array_equal(native, reference)
    assert native_state == reference_rng.getstate()


@pytest.mark.skipif(not evaluate._HAS_POP_BATCH, reason="native executor unavailable")
def test_prediction_cache_preserves_alternating_task_trajectory():
    cfg = ChemTapeConfig(
        arm="BP_TOPK", topk=3, bond_protection_ratio=0.5,
        task="sum_gt_10_v2", alphabet="v2_probe", backend="numpy",
        task_alternating_period=2,
        task_alternating_values="sum_gt_10_v2,sum_gt_5_slot",
        pop_size=40, generations=12, n_examples=16, holdout_size=0,
        disable_early_termination=True, dump_final_population=True, seed=15,
    )
    uncached = evolve.run_evolution(cfg, prediction_cache_size=0)
    cached = evolve.run_evolution(cfg, prediction_cache_size=128)
    assert np.array_equal(uncached.final_population, cached.final_population)
    assert np.array_equal(uncached.final_population_fitness, cached.final_population_fitness)
    assert [s.best_fitness for s in uncached.stats.history] == [s.best_fitness for s in cached.stats.history]


@pytest.mark.skipif(evaluate._rust_decode_topk is None, reason="native decoder unavailable")
def test_native_topk_preserves_evolution_trajectory(monkeypatch):
    cfg = ChemTapeConfig(
        arm="BP_TOPK", topk=3, bond_protection_ratio=0.5,
        task="sum_gt_10_v2", alphabet="v2_probe", backend="numpy",
        pop_size=40, generations=12, n_examples=16, holdout_size=0,
        disable_early_termination=True, dump_final_population=True, seed=19,
    )
    native = evolve.run_evolution(cfg)
    monkeypatch.setattr(evaluate, "_rust_decode_topk", None)
    monkeypatch.setattr(evolve, "_rust_topk_mask", None)
    reference = evolve.run_evolution(cfg)
    assert np.array_equal(native.final_population, reference.final_population)
    assert np.array_equal(native.final_population_fitness, reference.final_population_fitness)
    assert [s.best_fitness for s in native.stats.history] == [s.best_fitness for s in reference.stats.history]
