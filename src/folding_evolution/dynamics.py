"""Regime-shift dynamics: compare folding vs direct encoding adaptation."""

from __future__ import annotations

import random
from typing import Any, Callable

from .alphabet import random_genotype
from .config import EvolutionConfig
from .direct import develop_direct
from .individual import Individual
from .operators import crossover, mutate
from .phenotype import Program, develop
from .selection import select_next_generation, tournament_select
from .stats import StatsCollector


def partial_credit(actual: Any, expected: Any) -> float:
    """Partial credit for near-misses, ported from Elixir dynamics.ex."""
    if actual == expected:
        return 1.0
    if actual is None:
        return 0.0
    # Numeric near-miss
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        if expected == 0:
            return 0.1 if actual != 0 else 1.0
        ratio = abs(actual - expected) / max(abs(expected), 1)
        return max(0.1, min(0.9, 1.0 - ratio))
    # List length near-miss
    if isinstance(actual, list) and isinstance(expected, list):
        if not expected:
            return 0.1 if actual else 1.0
        len_score = 1.0 - min(abs(len(actual) - len(expected)) / len(expected), 1.0)
        return 0.1 + 0.8 * len_score
    # Dict partial
    if isinstance(actual, dict) and isinstance(expected, dict):
        if not expected:
            return 1.0 if not actual else 0.1
        return 0.1
    # Wrong type entirely
    return 0.05


def evaluate_multi_target(
    individual: Individual,
    targets: list[Callable[[dict], Any]],
    contexts: list[dict],
) -> float:
    """Evaluate fitness as average partial credit across all targets x contexts.

    Data-dependence gate: if program output is identical on all contexts, fitness is 0.
    """
    if individual.program is None:
        return 0.0

    # Data-dependence gate: check outputs vary across contexts
    gate_outputs = []
    for ctx in contexts:
        gate_outputs.append(repr(individual.program.evaluate(ctx)))
    if len(set(gate_outputs)) <= 1:
        return 0.0

    scores = []
    for target_fn in targets:
        for ctx in contexts:
            output = individual.program.evaluate(ctx)
            expected = target_fn(ctx)
            scores.append(partial_credit(output, expected))
    return sum(scores) / len(scores) if scores else 0.0


def _evolve_phase(
    population: list[Individual],
    targets: list[Callable[[dict], Any]],
    contexts: list[dict],
    develop_fn: Callable[[str], Program],
    config: EvolutionConfig,
    generations: int,
    rng: random.Random,
    stats: StatsCollector,
    gen_offset: int,
) -> list[Individual]:
    """Run evolution for a number of generations, mutating stats in place."""
    for gen in range(generations):
        for ind in population:
            ind.program = develop_fn(ind.genotype)
            ind.fitness = evaluate_multi_target(ind, targets, contexts)

        stats.record(gen_offset + gen, population)

        # Produce children: crossover OR mutation (not both), matching Elixir
        children: list[Individual] = []
        for _ in range(config.population_size):
            if rng.random() < config.crossover_rate:
                a = tournament_select(population, config.tournament_size, rng)
                b = tournament_select(population, config.tournament_size, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                parent = tournament_select(population, config.tournament_size, rng)
                child_geno = mutate(parent.genotype, rng)
            children.append(Individual(genotype=child_geno))

        # (mu+lambda) selection: evaluate children, combine with parents, keep best
        for ind in children:
            ind.program = develop_fn(ind.genotype)
            ind.fitness = evaluate_multi_target(ind, targets, contexts)

        combined = population + children
        combined.sort(key=lambda ind: ind.fitness, reverse=True)
        population = [Individual(genotype=ind.genotype) for ind in combined[:config.population_size]]

    # Final evaluation
    for ind in population:
        if ind.program is None:
            ind.program = develop_fn(ind.genotype)
            ind.fitness = evaluate_multi_target(ind, targets, contexts)

    return population


def run_regime_shift(
    config: EvolutionConfig,
    targets_a: list[Callable[[dict], Any]],
    targets_b: list[Callable[[dict], Any]],
    regime_a_gens: int,
    regime_b_gens: int,
    contexts: list[dict],
    develop_fn: Callable[[str], Program],
    rng: random.Random | None = None,
    initial_genotypes: list[str] | None = None,
) -> dict:
    """Single encoding, single seed regime shift.

    Returns dict with:
      - history: list of GenerationStats
      - shift_gen: generation where target changed
      - fitness_jumps: count of >0.1 best_fitness improvement in one gen
    """
    if rng is None:
        rng = random.Random(config.seed)

    develop.cache_clear()
    develop_direct.cache_clear()

    stats = StatsCollector()

    if initial_genotypes is not None:
        population = [Individual(genotype=g) for g in initial_genotypes]
    else:
        population = [
            Individual(genotype=random_genotype(config.genotype_length, rng))
            for _ in range(config.population_size)
        ]

    # Phase A
    population = _evolve_phase(
        population, targets_a, contexts, develop_fn, config,
        regime_a_gens, rng, stats, gen_offset=0,
    )

    shift_gen = regime_a_gens

    # Phase B -- same population, new targets
    _evolve_phase(
        population, targets_b, contexts, develop_fn, config,
        regime_b_gens, rng, stats, gen_offset=regime_a_gens,
    )

    # Count fitness jumps (>0.1 improvement in best_fitness)
    jumps = 0
    for i in range(1, len(stats.history)):
        delta = stats.history[i].best_fitness - stats.history[i - 1].best_fitness
        if delta > 0.1:
            jumps += 1

    return {
        "history": stats.history,
        "shift_gen": shift_gen,
        "fitness_jumps": jumps,
    }


def run_regime_shift_comparison(
    config: EvolutionConfig,
    targets_a: list[Callable[[dict], Any]],
    targets_b: list[Callable[[dict], Any]],
    regime_a_gens: int,
    regime_b_gens: int,
    contexts: list[dict],
    n_seeds: int = 5,
) -> dict:
    """Compare folding vs direct across multiple seeds.

    Uses the same initial genotypes for both encodings per seed.
    """
    folding_runs = []
    direct_runs = []

    for seed in range(n_seeds):
        seed_rng = random.Random(seed)
        genotypes = [
            random_genotype(config.genotype_length, seed_rng)
            for _ in range(config.population_size)
        ]

        folding_rng = random.Random(seed)
        folding_result = run_regime_shift(
            config, targets_a, targets_b,
            regime_a_gens, regime_b_gens, contexts,
            develop_fn=develop,
            rng=folding_rng,
            initial_genotypes=list(genotypes),
        )
        folding_runs.append(folding_result)

        direct_rng = random.Random(seed)
        direct_result = run_regime_shift(
            config, targets_a, targets_b,
            regime_a_gens, regime_b_gens, contexts,
            develop_fn=develop_direct,
            rng=direct_rng,
            initial_genotypes=list(genotypes),
        )
        direct_runs.append(direct_result)

        print(f"Seed {seed}: folding best={folding_result['history'][-1].best_fitness:.3f}, "
              f"direct best={direct_result['history'][-1].best_fitness:.3f}")

    return {
        "folding_runs": folding_runs,
        "direct_runs": direct_runs,
        "shift_gen": regime_a_gens,
        "n_seeds": n_seeds,
    }
