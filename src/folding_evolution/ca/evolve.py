"""GA loop for CA-rule evolution."""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np

from . import rule as ca_rule
from .config import CAConfig
from .evaluate import evaluate_population
from .metrics import CAStatsCollector
from .tasks import build_task


@dataclass
class EvolutionResult:
    best_genotype: np.ndarray
    best_fitness: float
    stats: CAStatsCollector
    generations_run: int


def _tournament_select(
    indices: list[int],
    fitnesses: np.ndarray,
    tournament_size: int,
    rng: random.Random,
) -> int:
    competitors = rng.sample(indices, min(tournament_size, len(indices)))
    return max(competitors, key=lambda i: fitnesses[i])


def run_evolution(cfg: CAConfig) -> EvolutionResult:
    """Evolve CA rules for `cfg.generations` generations."""
    rng = random.Random(cfg.seed)
    task = build_task(cfg, seed=cfg.seed)

    # Initial population — P random rule genotypes (family-dispatched).
    population = [ca_rule.random_genotype_for(cfg, rng) for _ in range(cfg.pop_size)]
    fitnesses, _ = evaluate_population(population, task, cfg)

    stats = CAStatsCollector()
    stats.record(0, fitnesses, population)

    for gen in range(1, cfg.generations + 1):
        # Build next population: elitism + tournament-selected parents.
        order = np.argsort(-fitnesses)
        elites = [population[i].copy() for i in order[: cfg.elite_count]]
        new_pop: list[np.ndarray] = list(elites)

        pop_idx = list(range(cfg.pop_size))
        while len(new_pop) < cfg.pop_size:
            if rng.random() < cfg.crossover_rate:
                i = _tournament_select(pop_idx, fitnesses, cfg.tournament_size, rng)
                j = _tournament_select(pop_idx, fitnesses, cfg.tournament_size, rng)
                child = ca_rule.crossover_for(population[i], population[j], cfg, rng)
            else:
                i = _tournament_select(pop_idx, fitnesses, cfg.tournament_size, rng)
                child = population[i].copy()
            child = ca_rule.mutate_for(child, cfg, rng)
            new_pop.append(child)

        population = new_pop
        fitnesses, _ = evaluate_population(population, task, cfg)
        stats.record(gen, fitnesses, population)

    best_idx = int(np.argmax(fitnesses))
    return EvolutionResult(
        best_genotype=population[best_idx].copy(),
        best_fitness=float(fitnesses[best_idx]),
        stats=stats,
        generations_run=cfg.generations,
    )
