"""Unit tests for task registry."""

import numpy as np

from folding_evolution.ca.config import CAConfig
from folding_evolution.ca.tasks import build_task


def test_parity_labels_correct():
    cfg = CAConfig(n_bits=3, n_examples=8, task="parity")
    task = build_task(cfg, seed=0)
    for i in range(task.inputs.shape[0]):
        bits = task.inputs[i]
        expected = int(bits.sum()) % 2
        assert int(task.labels[i]) == expected


def test_majority_labels_correct():
    cfg = CAConfig(n_bits=4, n_examples=16, task="majority")
    task = build_task(cfg, seed=0)
    for i in range(task.inputs.shape[0]):
        bits = task.inputs[i]
        count = int(bits.sum())
        expected = 1 if count * 2 > cfg.n_bits else 0
        assert int(task.labels[i]) == expected, f"input={bits} count={count}"


def test_majority_label_balance_4bit():
    """4-bit majority with ties→0 should be unbalanced: only 5/16 inputs have majority 1."""
    cfg = CAConfig(n_bits=4, n_examples=16, task="majority")
    task = build_task(cfg, seed=0)
    # Count inputs with >2 ones out of 4 bits: C(4,3)+C(4,4) = 4+1 = 5.
    assert int(task.labels.sum()) == 5


def test_unknown_task_raises():
    import pytest
    cfg = CAConfig(task="does_not_exist")
    with pytest.raises(KeyError):
        build_task(cfg, seed=0)
