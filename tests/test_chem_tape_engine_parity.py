"""NumPy ↔ MLX engine equivalence on fixed seeds."""

import numpy as np
import pytest

from folding_evolution.chem_tape import engine_mlx, engine_numpy


B = 64
L = 32


def _random_tapes(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 16, size=(B, L), dtype=np.uint8)


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
def test_active_mask_numpy_mlx_identical(seed):
    tapes = _random_tapes(seed)
    m_np = engine_numpy.compute_active_mask(tapes)
    m_mx = engine_mlx.compute_active_mask(tapes)
    assert np.array_equal(m_np, m_mx), f"active mask diverges at seed={seed}"


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
def test_longest_run_mask_numpy_mlx_identical(seed):
    tapes = _random_tapes(seed)
    m_np = engine_numpy.compute_longest_run_mask(tapes)
    m_mx = engine_mlx.compute_longest_run_mask(tapes)
    assert np.array_equal(m_np, m_mx), (
        f"longest-run mask diverges at seed={seed}: "
        f"rows differing = {np.where(~(m_np == m_mx).all(axis=1))[0].tolist()[:5]}"
    )


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 1729])
def test_extracted_programs_identical(seed):
    tapes = _random_tapes(seed)
    m_np = engine_numpy.compute_longest_run_mask(tapes)
    m_mx = engine_mlx.compute_longest_run_mask(tapes)
    assert engine_numpy.extract_programs(tapes, m_np) == engine_mlx.extract_programs(tapes, m_mx)
