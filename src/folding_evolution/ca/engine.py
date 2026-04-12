"""Backend dispatcher for CA engines."""

from __future__ import annotations

import numpy as np

from . import engine_mlx, engine_numpy


def run(
    initial_grid: np.ndarray,
    rule_table: np.ndarray,
    input_clamp: np.ndarray,
    steps: int,
    backend: str = "mlx",
) -> np.ndarray:
    """Run a batched CA for `steps` steps using the selected backend.

    Args:
        initial_grid: (B, N, N) uint8
        rule_table: (B, K, max_sum+1) uint8
        input_clamp: (B, N) uint8
        steps: number of iterations
        backend: "numpy" | "mlx"
    Returns:
        final_grid: (B, N, N) uint8 — always a NumPy array for downstream use.
    """
    if backend == "numpy":
        return engine_numpy.run(initial_grid, rule_table, input_clamp, steps)
    if backend == "mlx":
        return engine_mlx.run(initial_grid, rule_table, input_clamp, steps)
    raise ValueError(f"Unknown backend {backend!r}; use 'numpy' or 'mlx'")
