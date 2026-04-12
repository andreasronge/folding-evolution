"""Unit tests for ca.engine_numpy — hand-picked rules with known behavior."""

import numpy as np
import pytest

from folding_evolution.ca import engine_numpy as eng
from folding_evolution.ca import rule as ca_rule


K = 4
N = 8


def _identity_table() -> np.ndarray:
    """Rule table where next_state = self, regardless of neighbor sum."""
    shape = ca_rule.rule_shape(K)
    table = np.zeros(shape, dtype=np.uint8)
    for s in range(K):
        table[s, :] = s
    return table


def _zero_table() -> np.ndarray:
    """Rule table that always writes 0 (except row 0 which gets clamped)."""
    return np.zeros(ca_rule.rule_shape(K), dtype=np.uint8)


def test_identity_rule_preserves_interior():
    table = _identity_table()[None, ...]  # (1, K, max_sum+1)
    grid = np.zeros((1, N, N), dtype=np.uint8)
    grid[0, 3, 3] = 2
    grid[0, 5, 4] = 1
    clamp = np.zeros((1, N), dtype=np.uint8)
    out = eng.step(grid, table, clamp)
    assert out[0, 3, 3] == 2
    assert out[0, 5, 4] == 1


def test_zero_rule_clears_grid_except_clamped_row():
    table = _zero_table()[None, ...]
    grid = np.full((1, N, N), 3, dtype=np.uint8)
    clamp = np.array([[1, 0, 1, 0, 1, 0, 1, 0]], dtype=np.uint8)
    out = eng.step(grid, table, clamp)
    # Everything should be zero except row 0, which is clamped.
    assert np.array_equal(out[0, 0, :], clamp[0])
    assert (out[0, 1:, :] == 0).all()


def test_run_steps_are_iterated():
    # Build a rule that propagates state 1 downward via neighbor sum.
    # Identity rule, but where sum>=1 bumps a 0 up to 1.
    table = _identity_table()
    table[0, 1:] = 1  # dead cell with any live neighbor becomes alive
    table_b = table[None, ...]

    grid = np.zeros((1, N, N), dtype=np.uint8)
    clamp = np.zeros((1, N), dtype=np.uint8)
    clamp[0, N // 2] = 1  # a single live cell on row 0

    out = eng.run(grid.copy(), table_b, clamp, steps=N - 1)
    # By the time we've run N-1 steps, the signal should have reached row N-1
    # at the column of the clamp (or adjacent).
    assert out[0, N - 1, :].sum() > 0


def test_batch_independence():
    """Two batch entries with different rules should evolve independently."""
    table_zero = _zero_table()
    table_id = _identity_table()
    table = np.stack([table_zero, table_id], axis=0)  # (2, K, max_sum+1)

    grid = np.full((2, N, N), 2, dtype=np.uint8)
    clamp = np.zeros((2, N), dtype=np.uint8)
    out = eng.step(grid, table, clamp)
    # Batch 0 uses zero rule: interior becomes 0.
    assert (out[0, 1:, :] == 0).all()
    # Batch 1 uses identity: interior preserved.
    assert (out[1, 1:, :] == 2).all()


def test_input_clamp_overrides_previous_row_zero():
    """Row 0 after step == input_clamp regardless of what rule would write."""
    # Identity rule would keep row-0 cells as-is; we pass a different clamp.
    table_b = _identity_table()[None, ...]
    grid = np.full((1, N, N), 2, dtype=np.uint8)
    clamp = np.array([[3, 3, 3, 3, 3, 3, 3, 3]], dtype=np.uint8)
    out = eng.step(grid, table_b, clamp)
    assert np.array_equal(out[0, 0, :], clamp[0])


def test_step_dtype_asserts():
    table_b = _identity_table()[None, ...]
    grid_bad = np.zeros((1, N, N), dtype=np.int64)
    clamp = np.zeros((1, N), dtype=np.uint8)
    with pytest.raises(AssertionError):
        eng.step(grid_bad, table_b, clamp)
