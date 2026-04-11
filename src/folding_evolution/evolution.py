"""Main evolution loop."""

from __future__ import annotations

import random
from typing import Any, Callable

from .alphabet import random_genotype
from .config import EvolutionConfig
from .fitness import evaluate_fitness
from .individual import Individual
from .operators import crossover, mutate
from .phenotype import Program, develop, develop_batch
from .selection import select_next_generation
from .stats import StatsCollector


def run_evolution(
    config: EvolutionConfig,
    target_fn: Callable[[dict], Any],
    contexts: list[dict],
    develop_fn: Callable[[str], Program] | None = None,
) -> tuple[list[Individual], StatsCollector]:
    """Run the full evolution loop.

    Returns (final_population, stats_collector).
    """
    if develop_fn is None:
        develop_fn = develop

    use_batch = develop_fn is develop

    # Clear LRU cache to avoid cross-contamination between runs
    develop.cache_clear()

    rng = random.Random(config.seed)
    stats = StatsCollector()

    # Initialize random population
    population = [
        Individual(genotype=random_genotype(config.genotype_length, rng))
        for _ in range(config.population_size)
    ]

    for gen in range(config.generations):
        # Develop and evaluate
        if use_batch:
            genotypes = [ind.genotype for ind in population]
            programs = develop_batch(genotypes)
            for ind, prog in zip(population, programs):
                ind.program = prog
        else:
            for ind in population:
                ind.program = develop_fn(ind.genotype)
        for ind in population:
            ind.fitness = evaluate_fitness(ind, target_fn, contexts)

        # Record stats
        stats.record(gen, population)

        # Early termination if perfect fitness found
        if any(ind.fitness >= 1.0 for ind in population):
            break

        # Select next generation
        selected = select_next_generation(
            population, config.elite_count, config.tournament_size, rng
        )

        # Create offspring via crossover and mutation
        next_pop: list[Individual] = []
        for i in range(config.population_size):
            if i < config.elite_count:
                # Elites pass through unchanged
                next_pop.append(Individual(genotype=selected[i].genotype))
            else:
                parent = selected[i]
                if rng.random() < config.crossover_rate:
                    partner = selected[rng.randrange(len(selected))]
                    child_geno = crossover(parent.genotype, partner.genotype, rng)
                else:
                    child_geno = parent.genotype

                if rng.random() < config.mutation_rate:
                    child_geno = mutate(child_geno, rng)

                next_pop.append(Individual(genotype=child_geno))

        population = next_pop

    # Final evaluation of last generation
    for ind in population:
        if ind.program is None:
            ind.program = develop_fn(ind.genotype)
            ind.fitness = evaluate_fitness(ind, target_fn, contexts)

    return population, stats
