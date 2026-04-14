"""K-alternating schedule (§10 plasticity test).

When `k_alternating_period > 0` and `k_alternating_values` is non-empty, the
BP_TOPK decode K cycles through values every `period` generations.
"""

from __future__ import annotations

import numpy as np
import pytest

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution, _is_k_alternating


# ---------- Config.current_k cycles correctly ----------


def test_current_k_returns_topk_when_inactive():
    cfg = ChemTapeConfig(arm="BP_TOPK", topk=3)
    assert cfg.current_k(0) == 3
    assert cfg.current_k(100) == 3
    assert cfg.current_k(999) == 3


def test_current_k_cycles_under_schedule():
    cfg = ChemTapeConfig(
        arm="BP_TOPK",
        topk=3,  # ignored under alternating
        k_alternating_period=100,
        k_alternating_values="3,999",
    )
    # Gens 0-99: K=3. Gens 100-199: K=999. Gens 200-299: K=3. ...
    assert cfg.current_k(0) == 3
    assert cfg.current_k(99) == 3
    assert cfg.current_k(100) == 999
    assert cfg.current_k(199) == 999
    assert cfg.current_k(200) == 3
    assert cfg.current_k(299) == 3
    assert cfg.current_k(300) == 999


def test_current_k_three_values():
    cfg = ChemTapeConfig(
        arm="BP_TOPK",
        k_alternating_period=50,
        k_alternating_values="1,3,999",
    )
    assert cfg.current_k(0) == 1
    assert cfg.current_k(49) == 1
    assert cfg.current_k(50) == 3
    assert cfg.current_k(100) == 999
    assert cfg.current_k(150) == 1  # wrap


def test_is_k_alternating_predicate():
    cfg_off = ChemTapeConfig(arm="BP_TOPK", topk=3)
    cfg_on  = ChemTapeConfig(arm="BP_TOPK", k_alternating_period=50, k_alternating_values="3,999")
    assert not _is_k_alternating(cfg_off)
    assert _is_k_alternating(cfg_on)


# ---------- Hash stability ----------


def test_hash_unchanged_when_k_alternating_inactive():
    """Adding k_alternating fields with defaults must not change hashes of
    existing BP_TOPK configs."""
    c1 = ChemTapeConfig(arm="BP_TOPK", topk=3)
    c2 = ChemTapeConfig(arm="BP_TOPK", topk=3,
                        k_alternating_period=0, k_alternating_values="")
    assert c1.hash() == c2.hash()


def test_hash_differs_when_k_alternating_active():
    c1 = ChemTapeConfig(arm="BP_TOPK", topk=3)
    c2 = ChemTapeConfig(arm="BP_TOPK", topk=3,
                        k_alternating_period=100, k_alternating_values="3,999")
    assert c1.hash() != c2.hash()


def test_hash_differs_by_period():
    c1 = ChemTapeConfig(arm="BP_TOPK", k_alternating_period=100, k_alternating_values="3,999")
    c2 = ChemTapeConfig(arm="BP_TOPK", k_alternating_period=300, k_alternating_values="3,999")
    assert c1.hash() != c2.hash()


# ---------- Flip events are recorded ----------


def test_flip_events_recorded_and_structured():
    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=12,
        backend="numpy", arm="BP_TOPK",
        k_alternating_period=3, k_alternating_values="3,999",
        seed=0,
    )
    result = run_evolution(cfg)
    assert result.flip_events is not None
    # Schedule under period=3: [0..2] K=3, [3..5] K=999, [6..8] K=3, [9..11] K=999,
    # [12] K=3 (gen 12 is evaluated as the first gen under new period).
    # Loop runs gens 1..12 inclusive, so flips happen at gens 3, 6, 9, 12 → 4 events.
    assert len(result.flip_events) == 4
    for ev in result.flip_events:
        assert set(ev.keys()) == {
            "flip_gen", "old_k", "new_k", "pre_flip_best", "post_flip_best", "recovery_gen",
        }
        assert ev["old_k"] != ev["new_k"]
    assert [(e["flip_gen"], e["old_k"], e["new_k"]) for e in result.flip_events] == [
        (3, 3, 999), (6, 999, 3), (9, 3, 999), (12, 999, 3),
    ]


def test_flip_events_none_when_inactive():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=6,
        backend="numpy", arm="BP_TOPK", topk=3,
        seed=0,
    )
    result = run_evolution(cfg)
    assert result.flip_events is None


# ---------- Reproducibility under alternation ----------


def test_k_alternating_is_reproducible():
    cfg = ChemTapeConfig(
        task="count_r", n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=9,
        backend="numpy", arm="BP_TOPK",
        k_alternating_period=3, k_alternating_values="3,999",
        seed=42,
    )
    r1 = run_evolution(cfg)
    r2 = run_evolution(cfg)
    assert np.array_equal(r1.best_genotype, r2.best_genotype)
    assert r1.best_fitness == r2.best_fitness
    assert r1.flip_events == r2.flip_events
