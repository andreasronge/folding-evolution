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

try:
    from _folding_rust import rust_chem_execute_batch as _rust_exec_batch  # type: ignore
    _HAS_RUST_EXECUTOR = True
except ImportError:
    _HAS_RUST_EXECUTOR = False

try:
    from _folding_rust import rust_chem_execute_pop_batch as _rust_exec_pop_batch  # type: ignore
    _HAS_POP_BATCH = True
except ImportError:
    _HAS_POP_BATCH = False


def _tapes_from_population(population: list[np.ndarray]) -> np.ndarray:
    """Stack P individual tapes into a (P, L) uint8 array."""
    return np.stack(population, axis=0).astype(np.uint8)


def _programs_for_arm(
    cfg: ChemTapeConfig, tapes: np.ndarray, topk_override: int | None = None
) -> list[list[int]]:
    """Arm A: full tape as program. Arm B: strict longest-active-run. Arm BP:
    permeable longest-run (NOP passes through; ids 14/15 are hard separators).
    Arm BP_TOPK: top-K permeable runs concatenated in tape order (§8).

    §12 evolve-K mode (cfg.evolve_k=True, BP_TOPK only): cell 0 of each tape
    is the K-header. K = evolve_k_values[tape[0] % len(values)]. Decode
    operates on tape[1:] (body) only; cell 0 is never part of the program.

    `topk_override` lets the evolve loop supply a per-generation K under the
    K-alternating schedule (§10); ignored when evolve_k=True (each individual
    uses its own header-derived K instead)."""
    if cfg.arm == "A":
        return [tapes[b].astype(np.int64).tolist() for b in range(tapes.shape[0])]
    if cfg.arm == "B":
        mask = engine.compute_longest_run_mask(tapes, backend=cfg.backend)
        return engine.extract_programs(tapes, mask)
    if cfg.arm == "BP":
        mask = engine.compute_longest_runnable_mask(tapes, backend=cfg.backend)
        return engine.extract_programs(tapes, mask)
    if cfg.arm == "BP_TOPK":
        if cfg.evolve_k:
            # Per-individual K from header cell 0; decode over body cells 1..L-1.
            bodies = tapes[:, 1:]
            progs: list[list[int]] = []
            # Per-individual K means per-row decode; NumPy engine handles a single-row tape.
            for b in range(tapes.shape[0]):
                k_b = cfg.individual_k(tapes[b])
                body_b = bodies[b:b+1]
                mask_b = engine.compute_topk_runnable_mask(body_b, k_b, backend=cfg.backend)
                progs.append(body_b[0][mask_b[0]].astype(np.int64).tolist())
            return progs
        k = topk_override if topk_override is not None else cfg.topk
        mask = engine.compute_topk_runnable_mask(tapes, k, backend=cfg.backend)
        return engine.extract_programs(tapes, mask)
    raise ValueError(f"Unknown arm {cfg.arm!r}; use 'A', 'B', 'BP', or 'BP_TOPK'")


def evaluate_population(
    population: list[np.ndarray],
    task: Task,
    cfg: ChemTapeConfig,
    topk_override: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate every tape in `population` on `task.inputs`.

    `topk_override` — for the §10 K-alternating schedule, evolve.py supplies
    the K to use this generation. Ignored unless arm == "BP_TOPK".

    Returns:
        fitnesses: (P,) float in [0, 1] — fraction correct.
        predictions: (P, E) int64 — per-example predictions.

    §v2.5-plasticity-1a: when ``cfg.plasticity_enabled`` is True the
    routing dispatches to the plastic evaluator (pure-Python); the fast
    Rust path is preserved when plasticity is off (default), so existing
    sweeps are byte-identical to pre-5c.
    """
    P = len(population)
    E = len(task.inputs)
    tapes = _tapes_from_population(population)                   # (P, L) uint8
    programs = _programs_for_arm(cfg, tapes, topk_override=topk_override)

    if cfg.plasticity_enabled:
        # Plastic path: train δ per-individual on the train split, score on
        # the train split as the selection signal. Predictions array is left
        # as an empty placeholder since the GA does not consume per-example
        # preds when plasticity is on (frozen metrics are captured in the
        # final-population dump via evolve.py).
        from . import plasticity as _plast
        plastic_out = _plast.evaluate_population_plastic(programs, task, cfg)
        fitnesses = plastic_out["selection_fitness"].astype(np.float64)
        predictions = np.zeros((P, E), dtype=np.int64)  # unused; placeholder
        return fitnesses, predictions

    consume = cfg.safe_pop_mode == "consume"
    if _HAS_POP_BATCH:
        s12 = task.alphabet.slot_12
        s13 = task.alphabet.slot_13
        threshold = int(task.alphabet.threshold)
        flat = _rust_exec_pop_batch(
            programs, s12, s13, task.inputs, task.input_type,
            alphabet_name=cfg.alphabet, threshold=threshold,
            safe_pop_consume=consume,
        )
        predictions = np.asarray(flat, dtype=np.int64).reshape(P, E)
    elif _HAS_RUST_EXECUTOR:
        predictions = np.zeros((P, E), dtype=np.int64)
        s12 = task.alphabet.slot_12
        s13 = task.alphabet.slot_13
        threshold = int(task.alphabet.threshold)
        for p in range(P):
            predictions[p] = _rust_exec_batch(
                programs[p], s12, s13, task.inputs, task.input_type,
                alphabet_name=cfg.alphabet, threshold=threshold,
                safe_pop_consume=consume,
            )
    else:
        predictions = np.zeros((P, E), dtype=np.int64)
        for p in range(P):
            prog = programs[p]
            for e in range(E):
                predictions[p, e] = executor.execute_program(
                    prog, task.alphabet, task.inputs[e], task.input_type,
                    alphabet_name=cfg.alphabet,
                    safe_pop_consume=consume,
                )

    fitnesses = (predictions == task.labels[None, :]).mean(axis=1).astype(np.float64)
    return fitnesses, predictions


def evaluate_on_inputs(
    genotype: np.ndarray,
    inputs: list,
    labels: np.ndarray,
    task: Task,
    cfg: ChemTapeConfig,
    topk_override: int | None = None,
) -> float:
    """Score a single genotype on an arbitrary input set (used for holdout).
    `topk_override` (§10): decode under this K instead of `cfg.topk`."""
    tape = genotype.astype(np.uint8).reshape(1, -1)
    programs = _programs_for_arm(cfg, tape, topk_override=topk_override)
    prog = programs[0]
    consume = cfg.safe_pop_mode == "consume"
    correct = 0
    for e, x in enumerate(inputs):
        pred = executor.execute_program(
            prog, task.alphabet, x, task.input_type, alphabet_name=cfg.alphabet,
            safe_pop_consume=consume,
        )
        if pred == int(labels[e]):
            correct += 1
    return correct / max(len(inputs), 1)
