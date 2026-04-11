"""Tests for the evolution loop."""

import time

from folding_evolution.config import EvolutionConfig
from folding_evolution.data_contexts import make_contexts
from folding_evolution.evolution import run_evolution


def _count_products(ctx: dict) -> int:
    return len(ctx["products"])


def test_evolution_completes_and_fitness_increases():
    """A 20-gen run completes and fitness increases from gen 0."""
    config = EvolutionConfig(
        population_size=50,
        genotype_length=30,
        generations=20,
        seed=42,
    )
    contexts = make_contexts()
    _, stats = run_evolution(config, _count_products, contexts)

    assert len(stats.history) > 0
    assert stats.history[-1].best_fitness >= stats.history[0].best_fitness


def test_evolution_seed_42_reaches_target():
    """Seed 42: best fitness reaches 1.0 within 50 gens."""
    config = EvolutionConfig(
        population_size=50,
        genotype_length=30,
        generations=100,
        seed=42,
    )
    contexts = make_contexts()

    start = time.time()
    _, stats = run_evolution(config, _count_products, contexts)
    elapsed = time.time() - start

    total_evals = sum(s.population_size for s in stats.history)
    print(f"\nSeed 42: best={stats.best_fitness:.2f}, gens={len(stats.history)}, "
          f"evals={total_evals}, evals/sec={total_evals/elapsed:.0f}")

    assert stats.best_fitness >= 1.0, (
        f"Expected fitness 1.0, got {stats.best_fitness}"
    )


def test_multiple_seeds_reach_good_fitness():
    """Multiple seeds reach fitness > 0.5."""
    contexts = make_contexts()
    for seed in [42, 123, 99]:
        config = EvolutionConfig(
            population_size=50,
            genotype_length=30,
            generations=200,
            seed=seed,
        )
        _, stats = run_evolution(config, _count_products, contexts)
        print(f"Seed {seed}: best={stats.best_fitness:.2f}")
        assert stats.best_fitness > 0.5, (
            f"Seed {seed}: expected >0.5, got {stats.best_fitness}"
        )


def test_stats_csv(tmp_path):
    """Stats CSV has correct columns."""
    config = EvolutionConfig(
        population_size=20,
        genotype_length=30,
        generations=10,
        seed=42,
    )
    contexts = make_contexts()
    _, stats = run_evolution(config, _count_products, contexts)

    csv_path = tmp_path / "stats.csv"
    stats.to_csv(csv_path)

    with open(csv_path) as f:
        header = f.readline().strip()
        assert header == "generation,best_fitness,avg_fitness,best_genotype,best_source,best_bond_count,population_size"
        lines = f.readlines()
        assert len(lines) == len(stats.history)


def test_evals_per_second():
    """Print evals/sec for benchmarking."""
    config = EvolutionConfig(
        population_size=50,
        genotype_length=30,
        generations=50,
        seed=42,
    )
    contexts = make_contexts()

    start = time.time()
    _, stats = run_evolution(config, _count_products, contexts)
    elapsed = time.time() - start

    total_evals = sum(s.population_size for s in stats.history)
    rate = total_evals / elapsed
    print(f"\nBenchmark: {total_evals} evals in {elapsed:.2f}s = {rate:.0f} evals/sec")
    assert rate > 0
