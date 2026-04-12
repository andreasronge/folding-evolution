"""Backend dispatcher for CA engines.

Routes on (rule_family, backend). `run_population` is the high-level entry
used by `evaluate.py`; it decodes a list of genotypes for the given family
and executes the appropriate kernel.
"""

from __future__ import annotations

import numpy as np

from . import engine_mlx, engine_numpy
from . import rule as rule_mod
from . import rule_decision_tree as _dt
from . import rule_banded as _banded
from .config import CAConfig


def _run_outer_totalistic(
    cfg: CAConfig,
    genotypes: list[np.ndarray],
    initial_grid: np.ndarray,
    input_clamp: np.ndarray,
) -> np.ndarray:
    B = initial_grid.shape[0]
    P = len(genotypes)
    E = B // P
    # Stack per-rule tables, broadcast across examples.
    tables = np.stack([rule_mod.decode(g, cfg.n_states) for g in genotypes], axis=0)
    tables_be = np.broadcast_to(tables[:, None, :, :], (P, E, *tables.shape[1:]))
    tables_be = np.ascontiguousarray(tables_be).reshape(P * E, *tables.shape[1:])

    if cfg.backend == "numpy":
        return engine_numpy.run(initial_grid, tables_be, input_clamp, cfg.steps)
    if cfg.backend == "mlx":
        return engine_mlx.run(initial_grid, tables_be, input_clamp, cfg.steps)
    raise ValueError(f"Unknown backend {cfg.backend!r}")


def _run_decision_tree(
    cfg: CAConfig,
    genotypes: list[np.ndarray],
    initial_grid: np.ndarray,
    input_clamp: np.ndarray,
) -> np.ndarray:
    B = initial_grid.shape[0]
    P = len(genotypes)
    E = B // P
    batch = _dt.decode_batch(genotypes, cfg.n_states)    # pos/val/leaves per rule

    def _broadcast(a: np.ndarray) -> np.ndarray:
        out = np.broadcast_to(a[:, None, ...], (P, E, *a.shape[1:]))
        return np.ascontiguousarray(out).reshape(P * E, *a.shape[1:])

    pos = _broadcast(batch.pos)
    val = _broadcast(batch.val)
    leaves = _broadcast(batch.leaves)

    if cfg.backend == "numpy":
        return engine_numpy.run_dt(
            initial_grid, pos, val, leaves, input_clamp, steps=cfg.steps
        )
    if cfg.backend == "mlx":
        return engine_mlx.run_dt(
            initial_grid, pos, val, leaves, input_clamp, steps=cfg.steps
        )
    raise ValueError(f"Unknown backend {cfg.backend!r}")


def _run_banded(
    cfg: CAConfig,
    genotypes: list[np.ndarray],
    initial_grid: np.ndarray,
    input_clamp: np.ndarray,
) -> np.ndarray:
    B = initial_grid.shape[0]
    P = len(genotypes)
    E = B // P
    batch = _banded.decode_batch(genotypes, cfg.n_states, cfg.n_bands)
    tables = batch.tables                                    # (P, n_bands, K, max_sum+1)
    tables_be = np.broadcast_to(
        tables[:, None, ...], (P, E, *tables.shape[1:])
    )
    tables_be = np.ascontiguousarray(tables_be).reshape(P * E, *tables.shape[1:])

    row_band = _banded.row_to_band(cfg.grid_n, cfg.n_bands)

    if cfg.backend == "numpy":
        return engine_numpy.run_banded(initial_grid, tables_be, row_band, input_clamp, cfg.steps)
    if cfg.backend == "mlx":
        return engine_mlx.run_banded(initial_grid, tables_be, row_band, input_clamp, cfg.steps)
    raise ValueError(f"Unknown backend {cfg.backend!r}")


def run_population(
    cfg: CAConfig,
    genotypes: list[np.ndarray],
    initial_grid: np.ndarray,
    input_clamp: np.ndarray,
) -> np.ndarray:
    """Execute the CA for a whole batch (population × examples) under cfg's family + backend."""
    fam = cfg.rule_family
    if fam == "outer_totalistic":
        return _run_outer_totalistic(cfg, genotypes, initial_grid, input_clamp)
    if fam == "decision_tree":
        return _run_decision_tree(cfg, genotypes, initial_grid, input_clamp)
    if fam == "banded_ot":
        return _run_banded(cfg, genotypes, initial_grid, input_clamp)
    raise ValueError(f"Unknown rule_family {fam!r}")


# Preserve the original single-rule entry for any external callers / tests.
def run(
    initial_grid: np.ndarray,
    rule_table: np.ndarray,
    input_clamp: np.ndarray,
    steps: int,
    backend: str = "mlx",
) -> np.ndarray:
    """Legacy entry for outer-totalistic rule_table + backend."""
    if backend == "numpy":
        return engine_numpy.run(initial_grid, rule_table, input_clamp, steps)
    if backend == "mlx":
        return engine_mlx.run(initial_grid, rule_table, input_clamp, steps)
    raise ValueError(f"Unknown backend {backend!r}; use 'numpy' or 'mlx'")
