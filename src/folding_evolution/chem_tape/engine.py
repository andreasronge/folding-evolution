"""Backend dispatcher for the chem-tape engine."""

from __future__ import annotations

import numpy as np

from . import engine_numpy

# MLX is an optional backend: import lazily so that the module loads on
# platforms without a working libmlx (e.g., Linux sandboxes where the
# mlx wheel ships without the native lib). `backend="mlx"` paths raise
# ImportError at call time, not at module-import time.
try:
    from . import engine_mlx  # type: ignore
    _HAS_MLX = True
except Exception:
    engine_mlx = None  # type: ignore
    _HAS_MLX = False


def _require_mlx() -> None:
    if not _HAS_MLX:
        raise ImportError(
            "mlx backend is unavailable on this platform (libmlx.so not found). "
            "Use backend='numpy' instead."
        )


def compute_longest_run_mask(tapes: np.ndarray, backend: str = "mlx") -> np.ndarray:
    """Arm B (strict): longest contiguous run of active cells (ids 1..13)."""
    if backend == "numpy":
        return engine_numpy.compute_longest_run_mask(tapes)
    if backend == "mlx":
        _require_mlx()
        return engine_mlx.compute_longest_run_mask(tapes)
    raise ValueError(f"Unknown backend {backend!r}; use 'numpy' or 'mlx'")


def compute_longest_runnable_mask(tapes: np.ndarray, backend: str = "mlx") -> np.ndarray:
    """Arm BP (permeable): longest contiguous run of non-separator cells.

    Under the permeable rule, id 0 (NOP) does not break bonded runs; only
    ids 14 and 15 are hard separators. Cells in the resulting mask execute
    as their token dispatches — NOP cells as no-ops, everything else as
    normal ops.
    """
    if backend == "numpy":
        return engine_numpy.compute_longest_runnable_mask(tapes)
    if backend == "mlx":
        _require_mlx()
        return engine_mlx.compute_longest_runnable_mask(tapes)
    raise ValueError(f"Unknown backend {backend!r}; use 'numpy' or 'mlx'")


def compute_topk_runnable_mask(
    tapes: np.ndarray, k: int, backend: str = "mlx"
) -> np.ndarray:
    """Arm BP_TOPK: K longest non-separator runs. K=1 = Arm BP. K=∞ ⇒
    every non-separator cell executes (distinct from Arm A only in that
    ids 14/15 still gate)."""
    if backend == "numpy":
        return engine_numpy.compute_topk_runnable_mask(tapes, k)
    if backend == "mlx":
        _require_mlx()
        return engine_mlx.compute_topk_runnable_mask(tapes, k)
    raise ValueError(f"Unknown backend {backend!r}; use 'numpy' or 'mlx'")


def extract_programs(
    tapes: np.ndarray, longest_mask: np.ndarray
) -> list[list[int]]:
    # Pure NumPy; backend-independent.
    return engine_numpy.extract_programs(tapes, longest_mask)
