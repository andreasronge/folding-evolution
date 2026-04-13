"""Batched population evaluation for chem-tape.

Arm B (chem-tape v1): compute the longest-active-run mask in one batched engine
call over (P, L), extract per-row programs, then loop P×E in Python to execute
each program on each example (spec §Layer 6 — per-example Python loop is fine
for ≤16K evaluations × ≤32 tokens × ≤256 op cap).

Arm A (direct stack-GP null): skip the engine entirely — each individual's
program IS the full tape. NOPs act as no-ops but not as separators
(spec §Layer 9).
"""

from __future__ import annotations

import numpy as np

from . import engine, executor
from .config import ChemTapeConfig
from .tasks import Task


def _tapes_from_population(population: list[np.ndarray]) -> np.ndarray:
    """Stack P individual tapes into a (P, L) uint8 array."""
    return np.stack(population, axis=0).astype(np.uint8)


def _programs_for_arm(
    cfg: ChemTapeConfig, tapes: np.ndarray
) -> list[list[int]]:
    """Arm A: full tape as program. Arm B: longest-run extraction via engine."""
    if cfg.arm == "A":
        return [tapes[b].astype(np.int64).tolist() for b in range(tapes.shape[0])]
    if cfg.arm == "B":
        mask = engine.compute_longest_run_mask(tapes, backend=cfg.backend)
        return engine.extract_programs(tapes, mask)
    raise ValueError(f"Unknown arm {cfg.arm!r}; use 'A' or 'B'")


def evaluate_population(
    population: list[np.ndarray],
    task: Task,
    cfg: ChemTapeConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate every tape in `population` on `task.inputs`.

    Returns:
        fitnesses: (P,) float in [0, 1] — fraction correct.
        predictions: (P, E) int64 — per-example predictions.
    """
    P = len(population)
    E = len(task.inputs)
    tapes = _tapes_from_population(population)                   # (P, L) uint8
    programs = _programs_for_arm(cfg, tapes)                     # len P, list[int]

    predictions = np.zeros((P, E), dtype=np.int64)
    for p in range(P):
        prog = programs[p]
        for e in range(E):
            predictions[p, e] = executor.execute_program(
                prog, task.alphabet, task.inputs[e], task.input_type
            )

    fitnesses = (predictions == task.labels[None, :]).mean(axis=1).astype(np.float64)
    return fitnesses, predictions


def evaluate_on_inputs(
    genotype: np.ndarray,
    inputs: list,
    labels: np.ndarray,
    task: Task,
    cfg: ChemTapeConfig,
) -> float:
    """Score a single genotype on an arbitrary input set (used for holdout)."""
    tape = genotype.astype(np.uint8).reshape(1, -1)
    programs = _programs_for_arm(cfg, tape)
    prog = programs[0]
    correct = 0
    for e, x in enumerate(inputs):
        pred = executor.execute_program(prog, task.alphabet, x, task.input_type)
        if pred == int(labels[e]):
            correct += 1
    return correct / max(len(inputs), 1)
