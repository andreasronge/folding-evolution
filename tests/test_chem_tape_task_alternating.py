"""Task-alternating schedule (§v1.5): task-axis analogue of §10 K-alternation.

Active task cycles through `task_alternating_values` every `task_alternating_period`
generations. cross_task_fitness records best-of-run performance under each task
in the schedule.
"""

from __future__ import annotations

import numpy as np
import pytest

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution, _is_task_alternating


# ---------- Config helpers ----------


def test_current_task_inactive_returns_cfg_task():
    cfg = ChemTapeConfig(task="count_r")
    assert cfg.current_task(0) == "count_r"
    assert cfg.current_task(999) == "count_r"


def test_current_task_cycles_under_schedule():
    cfg = ChemTapeConfig(
        task="count_r",
        task_alternating_period=100,
        task_alternating_values="sum_gt_10,count_r,has_upper",
    )
    assert cfg.current_task(0) == "sum_gt_10"
    assert cfg.current_task(99) == "sum_gt_10"
    assert cfg.current_task(100) == "count_r"
    assert cfg.current_task(199) == "count_r"
    assert cfg.current_task(200) == "has_upper"
    assert cfg.current_task(300) == "sum_gt_10"   # wrap


def test_task_alternating_value_list_parses():
    cfg = ChemTapeConfig(task_alternating_values=" sum_gt_10 ,count_r ,has_upper")
    assert cfg.task_alternating_value_list() == ["sum_gt_10", "count_r", "has_upper"]


def test_is_task_alternating_predicate():
    c_off = ChemTapeConfig(task="count_r")
    c_on = ChemTapeConfig(task="count_r",
                          task_alternating_period=100,
                          task_alternating_values="sum_gt_10,count_r")
    assert not _is_task_alternating(c_off)
    assert _is_task_alternating(c_on)


# ---------- Hash stability ----------


def test_hash_unchanged_when_task_alt_inactive():
    c1 = ChemTapeConfig(task="count_r")
    c2 = ChemTapeConfig(task="count_r",
                        task_alternating_period=0, task_alternating_values="")
    assert c1.hash() == c2.hash()


def test_hash_differs_when_task_alt_active():
    c1 = ChemTapeConfig(task="count_r")
    c2 = ChemTapeConfig(task="count_r",
                        task_alternating_period=100,
                        task_alternating_values="sum_gt_10,count_r")
    assert c1.hash() != c2.hash()


# ---------- Smoke: task-alternation runs ----------


def test_task_alternating_smoke_runs_and_flips_recorded():
    cfg = ChemTapeConfig(
        task="count_r",  # fallback; overridden by schedule
        n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=9,
        backend="numpy", arm="BP_TOPK", topk=3,
        task_alternating_period=3,
        task_alternating_values="count_r,has_upper,sum_gt_10",
        seed=0,
    )
    result = run_evolution(cfg)
    # Schedule: gens 0..2 count_r; 3..5 has_upper; 6..8 sum_gt_10.
    # Loop runs gens 1..9 → flips at 3, 6, 9.
    assert result.flip_events is not None
    # At least 2 task flips: gen 3 (count_r→has_upper), gen 6 (has_upper→sum_gt_10).
    task_flips = [ev for ev in result.flip_events if ev.get("flip_type") == "task"]
    assert len(task_flips) >= 2
    # Each task-flip has old_task/new_task.
    for ev in task_flips:
        assert "old_task" in ev and "new_task" in ev
        assert ev["old_task"] != ev["new_task"]


def test_cross_task_fitness_populated():
    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=6,
        backend="numpy", arm="BP_TOPK", topk=3,
        task_alternating_period=2,
        task_alternating_values="count_r,has_upper",
        seed=0,
    )
    result = run_evolution(cfg)
    assert result.cross_task_fitness is not None
    assert set(result.cross_task_fitness.keys()) == {"count_r", "has_upper"}
    for task_name, record in result.cross_task_fitness.items():
        assert "fitness" in record and 0.0 <= record["fitness"] <= 1.0


def test_cross_task_fitness_none_when_alt_off():
    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=4,
        backend="numpy", arm="BP_TOPK", topk=3,
        seed=0,
    )
    result = run_evolution(cfg)
    assert result.cross_task_fitness is None


# ---------- Reproducibility ----------


def test_task_alternating_is_reproducible():
    cfg = ChemTapeConfig(
        task="count_r",
        n_examples=16, holdout_size=0,
        tape_length=16, pop_size=16, generations=6,
        backend="numpy", arm="BP_TOPK", topk=3,
        task_alternating_period=3,
        task_alternating_values="count_r,has_upper",
        seed=42,
    )
    r1 = run_evolution(cfg)
    r2 = run_evolution(cfg)
    assert np.array_equal(r1.best_genotype, r2.best_genotype)
    assert r1.best_fitness == r2.best_fitness
    assert r1.cross_task_fitness == r2.cross_task_fitness
