"""Task registry: labels, balance, holdout disjointness."""

import numpy as np

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.tasks import (
    build_task,
    _count_r_label,
    _has_upper_label,
    _sum_gt_10_label,
)


def test_count_r_labels_match_label_fn():
    cfg = ChemTapeConfig(task="count_r", n_examples=32, holdout_size=64, seed=0)
    task = build_task(cfg, seed=cfg.seed)
    for s, lbl in zip(task.inputs, task.labels):
        assert int(lbl) == _count_r_label(s)


def test_has_upper_balanced():
    cfg = ChemTapeConfig(task="has_upper", n_examples=32, holdout_size=0, seed=0)
    task = build_task(cfg, seed=cfg.seed)
    pos = int(task.labels.sum())
    assert 14 <= pos <= 18  # ~half of 32, allow ±2 slack from odd-n rounding


def test_sum_gt_10_labels_match():
    cfg = ChemTapeConfig(task="sum_gt_10", n_examples=32, holdout_size=64, seed=0)
    task = build_task(cfg, seed=cfg.seed)
    for xs, lbl in zip(task.inputs, task.labels):
        assert int(lbl) == _sum_gt_10_label(xs)


def test_holdout_disjoint_from_training():
    cfg = ChemTapeConfig(task="sum_gt_10", n_examples=16, holdout_size=64, seed=0)
    task = build_task(cfg, seed=cfg.seed)
    train_set = {repr(x) for x in task.inputs}
    hold_set = {repr(x) for x in task.holdout_inputs}
    assert train_set.isdisjoint(hold_set)


def test_holdout_size_zero_returns_none():
    cfg = ChemTapeConfig(task="count_r", n_examples=16, holdout_size=0, seed=0)
    task = build_task(cfg, seed=cfg.seed)
    assert task.holdout_inputs is None
    assert task.holdout_labels is None


def test_task_reproducible_by_seed():
    cfg = ChemTapeConfig(task="count_r", n_examples=16, holdout_size=0, seed=42)
    t1 = build_task(cfg, seed=42)
    t2 = build_task(cfg, seed=42)
    assert t1.inputs == t2.inputs
    assert np.array_equal(t1.labels, t2.labels)
