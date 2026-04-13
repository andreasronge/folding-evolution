"""Backend dispatcher for the chem-tape engine."""

from __future__ import annotations

import numpy as np

from . import engine_mlx, engine_numpy


def compute_longest_run_mask(tapes: np.ndarray, backend: str = "mlx") -> np.ndarray:
    if backend == "numpy":
        return engine_numpy.compute_longest_run_mask(tapes)
    if backend == "mlx":
        return engine_mlx.compute_longest_run_mask(tapes)
    raise ValueError(f"Unknown backend {backend!r}; use 'numpy' or 'mlx'")


def extract_programs(
    tapes: np.ndarray, longest_mask: np.ndarray
) -> list[list[int]]:
    # Pure NumPy; backend-independent.
    return engine_numpy.extract_programs(tapes, longest_mask)
