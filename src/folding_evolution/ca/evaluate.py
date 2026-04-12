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

    out_row = cfg.resolved_output_row()
    out_col = cfg.resolved_output_col()
    out_states = final[:, out_row, out_col].reshape(P, E)                # (P, E)

    predictions = np.stack(
        [task.decode(out_states[p], cfg) for p in range(P)], axis=0
    )
    labels = task.labels
    fitnesses = (predictions == labels[None, :]).mean(axis=1).astype(np.float64)
    return fitnesses, predictions
