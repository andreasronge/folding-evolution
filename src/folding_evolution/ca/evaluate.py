"""Batched population evaluation.

Given a population of rule genotypes and a task, evaluate each rule's fitness
by running the CA on every task example and comparing predictions to labels.

Batching strategy: the batch axis B flattens (population P, examples E) so one
kernel call processes P*E grids in parallel. Routing to the correct rule
family + backend is delegated to `engine.run_population`.
"""

from __future__ import annotations

import numpy as np

from . import engine
from .config import CAConfig
from .tasks import Task


def evaluate_population(
    genotypes: list[np.ndarray],
    task: Task,
    cfg: CAConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate every rule in `genotypes` on `task.inputs`.

    Returns:
        fitnesses: (P,) float in [0, 1] — fraction correct per rule.
        predictions: (P, E) int8 — per-example predictions.
    """
    P = len(genotypes)
    E = task.inputs.shape[0]
    N = cfg.grid_n

    clamp_e = task.encode(task.inputs, cfg).astype(np.uint8)            # (E, N)
    clamp_pe = np.broadcast_to(clamp_e[None, :, :], (P, E, N))
    clamp_pe = np.ascontiguousarray(clamp_pe).reshape(P * E, N)

    initial_grid = np.zeros((P * E, N, N), dtype=np.uint8)

    final = engine.run_population(
        cfg=cfg,
        genotypes=genotypes,
        initial_grid=initial_grid,
        input_clamp=clamp_pe,
    )                                                                     # (P*E, N, N)

    predictions = _read_predictions(final, cfg, task, P, E)              # (P, E) int8
    labels = task.labels
    fitnesses = (predictions == labels[None, :]).mean(axis=1).astype(np.float64)
    return fitnesses, predictions


def _read_predictions(
    final: np.ndarray,
    cfg: CAConfig,
    task: Task,
    P: int,
    E: int,
) -> np.ndarray:
    """Apply cfg.output_mode to a (P*E, N, N) final grid and return (P, E) int8 labels.

    For multi-cell modes, decode each cell to a bit via task.decode and
    majority-vote across bits. Keeps task-specific decode logic intact.
    """
    N = cfg.grid_n
    out_row = cfg.resolved_output_row()
    out_col = cfg.resolved_output_col()
    mode = cfg.output_mode

    if mode == "center_cell":
        out_states = final[:, out_row, out_col].reshape(P, E)            # (P, E)
        return np.stack(
            [task.decode(out_states[p], cfg) for p in range(P)], axis=0
        )

    if mode == "horizontal_3":
        lo = max(0, out_col - 1)
        hi = min(N, out_col + 2)
        cells = final[:, out_row, lo:hi].reshape(P, E, hi - lo)          # (P, E, k)
    elif mode == "row_full":
        cells = final[:, out_row, :].reshape(P, E, N)                    # (P, E, N)
    else:
        raise ValueError(f"Unknown output_mode {mode!r}")

    k = cells.shape[-1]
    bits = np.stack(
        [task.decode(cells[p].reshape(-1), cfg).reshape(E, k) for p in range(P)],
        axis=0,
    ).astype(np.int8)                                                     # (P, E, k)
    votes = bits.sum(axis=-1)                                             # (P, E)
    return (votes * 2 > k).astype(np.int8)
