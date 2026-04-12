"""Unit tests for decision-tree rule encoding and step kernel."""

import random

import numpy as np
import pytest

from folding_evolution.ca import engine_numpy
from folding_evolution.ca import rule_decision_tree as dt


K = 4


def test_genotype_length():
    assert dt.GENOTYPE_LEN == 94  # 31 pos + 31 val + 32 leaves


def test_random_genotype_deterministic():
    g1 = dt.random_genotype(K, random.Random(42))
    g2 = dt.random_genotype(K, random.Random(42))
    assert np.array_equal(g1, g2)


def test_decode_shapes_and_ranges():
    g = dt.random_genotype(K, random.Random(0))
    decoded = dt.decode_one(g, K)
    assert decoded.pos.shape == (31,)
    assert decoded.val.shape == (31,)
    assert decoded.leaves.shape == (32,)
    assert decoded.pos.max() <= 8 and decoded.pos.min() >= 0
    assert decoded.val.max() < K and decoded.val.min() >= 0
    assert decoded.leaves.max() < K and decoded.leaves.min() >= 0


def test_decode_batch_stacks():
    genos = [dt.random_genotype(K, random.Random(i)) for i in range(3)]
    batch = dt.decode_batch(genos, K)
    assert batch.pos.shape == (3, 31)
    assert batch.val.shape == (3, 31)
    assert batch.leaves.shape == (3, 32)


def test_mutate_deterministic():
    g = dt.random_genotype(K, random.Random(0))
    m1 = dt.mutate(g, K, 0.1, random.Random(99))
    m2 = dt.mutate(g, K, 0.1, random.Random(99))
    assert np.array_equal(m1, m2)


def test_crossover_length_preserved():
    a = dt.random_genotype(K, random.Random(1))
    b = dt.random_genotype(K, random.Random(2))
    c = dt.crossover(a, b, random.Random(3))
    assert c.size == a.size


def _constant_output_tree(k_out: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Tree where every leaf emits state `k_out`. All tests trivially go left."""
    pos = np.zeros((1, 31), dtype=np.uint8)
    val = np.zeros((1, 31), dtype=np.uint8)
    leaves = np.full((1, 32), k_out, dtype=np.uint8)
    return pos, val, leaves


def test_constant_tree_writes_one_state():
    pos, val, leaves = _constant_output_tree(k_out=2)
    grid = np.zeros((1, 8, 8), dtype=np.uint8)
    clamp = np.zeros((1, 8), dtype=np.uint8)
    out = engine_numpy.step_dt(grid, pos, val, leaves, clamp)
    # Everywhere should be 2 except row 0 (clamped to 0).
    assert (out[0, 0, :] == 0).all()
    assert (out[0, 1:, :] == 2).all()


def test_tree_routes_left_right_correctly():
    """Root tests window[position=4]==1 (center cell).

    - Left subtree (center==1): all leaves output 3
    - Right subtree (center!=1): all leaves output 0
    Use a single-level decision conceptually — fill depths 1..4 with inert
    no-op internals whose output is still determined by root's split via
    which leaf subtree each side leads to.
    """
    pos = np.zeros((1, 31), dtype=np.uint8)
    val = np.zeros((1, 31), dtype=np.uint8)
    pos[0, 0] = 4  # root tests center cell
    val[0, 0] = 1  # center == 1 → go left
    # All non-root internals have arbitrary test; their children in this
    # tree shape both drop into one of two leaf halves. The left subtree
    # covers leaves [0..15], the right covers [16..31].
    leaves = np.zeros((1, 32), dtype=np.uint8)
    leaves[0, 0:16] = 3   # outputs for left half
    leaves[0, 16:32] = 0  # outputs for right half

    grid = np.zeros((1, 4, 4), dtype=np.uint8)
    grid[0, 2, 2] = 1   # center-ish live cell
    clamp = np.zeros((1, 4), dtype=np.uint8)

    out = engine_numpy.step_dt(grid, pos, val, leaves, clamp)
    # Cell (2,2): its own center value is 1 → left subtree → leaves[0..15] → 3.
    assert out[0, 2, 2] == 3
    # Cell (3,3): its center is 0 → right subtree → 0.
    assert out[0, 3, 3] == 0


def test_run_dt_iterates_steps():
    pos, val, leaves = _constant_output_tree(k_out=1)
    grid = np.zeros((1, 6, 6), dtype=np.uint8)
    clamp = np.array([[2, 2, 2, 2, 2, 2]], dtype=np.uint8)
    out = engine_numpy.run_dt(grid, pos, val, leaves, clamp, steps=4)
    assert (out[0, 0, :] == 2).all()      # clamp pinned
    assert (out[0, 1:, :] == 1).all()     # rest constant from tree


def test_decode_rejects_wrong_length():
    with pytest.raises(ValueError):
        dt.decode_one(np.zeros(50, dtype=np.uint8), K)
