"""GA loop for chem-tape evolution.

Mirrors `ca/evolve.py`. Genotype = length-L uint8 tape with values in {0..15};
per-byte mutation with fresh uniform resample; single-point crossover.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np

from .config import ChemTapeConfig
from .evaluate import evaluate_population, evaluate_on_inputs
from .metrics import ChemTapeStatsCollector
from .tasks import build_task


@dataclass
class EvolutionResult:
    best_genotype: np.ndarray
    best_fitness: float
    stats: ChemTapeStatsCollector
    generations_run: int
    holdout_fitness: float | None


def random_genotype(cfg: ChemTapeConfig, rng: random.Random) -> np.ndarray:
    """Uniform {0..15} per cell (spec §Layer 7). Three ids execute as NOP."""
    return np.array(
        [rng.randint(0, 15) for _ in range(cfg.tape_length)],
        dtype=np.uint8,
    )


def mutate(tape: np.ndarray, cfg: ChemTapeConfig, rng: random.Random) -> np.ndarray:
    """Per-byte fresh uniform resample at rate `mutation_rate`."""
    out = tape.copy()
    for i in range(out.shape[0]):
        if rng.random() < cfg.mutation_rate:
            out[i] = rng.randint(0, 15)
    return out


def crossover(
    a: np.ndarray, b: np.ndarray, cfg: ChemTapeConfig, rng: random.Random
) -> np.ndarray:
    """Single-point splice along the tape."""
    L = a.shape[0]
    cut = rng.randint(1, L - 1) if L > 1 else 0
    child = np.empty_like(a)
    child[:cut] = a[:cut]
    child[cut:] = b[cut:]
    return child


def _tournament_select(
    indices: list[int],
    fitnesses: np.ndarray,
    tournament_size: int,
    rng: random.Random,
) -> int:
    competitors = rng.sample(indices, min(tournament_size, len(indices)))
    return max(competitors, key=lambda i: fitnesses[i])


def run_evolution(cfg: ChemTapeConfig) -> EvolutionResult:
    """Evolve chem-tape genotypes for `cfg.generations` generations."""
    rng = random.Random(cfg.seed)
    task = build_task(cfg, seed=cfg.seed)

    population = [random_genotype(cfg, rng) for _ in range(cfg.pop_size)]
    fitnesses, _ = evaluate_population(population, task, cfg)

    stats = ChemTapeStatsCollector()
    stats.record(0, fitnesses, population, arm=cfg.arm)

    gen = 0
    for gen in range(1, cfg.generations + 1):
        order = np.argsort(-fitnesses)
        elites = [population[i].copy() for i in order[: cfg.elite_count]]
        new_pop: list[np.ndarray] = list(elites)

        pop_idx = list(range(cfg.pop_size))
        while len(new_pop) < cfg.pop_size:
            if rng.random() < cfg.crossover_rate:
                i = _tournament_select(pop_idx, fitnesses, cfg.tournament_size, rng)
                j = _tournament_select(pop_idx, fitnesses, cfg.tournament_size, rng)
                child = crossover(population[i], population[j], cfg, rng)
            else:
                i = _tournament_select(pop_idx, fitnesses, cfg.tournament_size, rng)
                child = population[i].copy()
            child = mutate(child, cfg, rng)
            new_pop.append(child)

        population = new_pop
        fitnesses, _ = evaluate_population(population, task, cfg)
        stats.record(gen, fitnesses, population, arm=cfg.arm)

        if fitnesses.max() >= 1.0:
            break

    best_idx = int(np.argmax(fitnesses))
    best = population[best_idx].copy()

    holdout_fitness: float | None = None
    if task.holdout_inputs is not None and task.holdout_labels is not None:
        holdout_fitness = evaluate_on_inputs(
            best, task.holdout_inputs, task.holdout_labels, task, cfg
        )

    return EvolutionResult(
        best_genotype=best,
        best_fitness=float(fitnesses[best_idx]),
        stats=stats,
        generations_run=gen,
        holdout_fitness=holdout_fitness,
    )
