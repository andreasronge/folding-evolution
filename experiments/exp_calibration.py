#!/usr/bin/env python3
"""Phase 1 Calibration: Can direct encoding solve tasks under stable conditions?

Sweeps task complexity levels for both encodings under a fixed target.
Determines whether direct encoding is a valid baseline for the 2x2 experiment,
or if we need an alternative (stack-based assembly or DEAP tree GP).

Task complexity levels:
  1-bond: count(data/products) — trivial, just "BS" in direct encoding
  2-bond: count(rest(data/products)) — requires count + rest + data
  3-bond: first(rest(data/products)) — requires first + rest + data
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from folding_evolution.config import EvolutionConfig
from folding_evolution.data_contexts import make_contexts
from folding_evolution.dynamics import evaluate_multi_target, partial_credit
from folding_evolution.individual import Individual
from folding_evolution.alphabet import random_genotype
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop
from folding_evolution.direct import develop_direct
from folding_evolution.selection import tournament_select
from folding_evolution.stats import StatsCollector

import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run_stable_evolution(config, targets, contexts, develop_fn, seed):
    """Run evolution with a fixed target for all generations."""
    rng = random.Random(seed)
    develop.cache_clear()
    develop_direct.cache_clear()

    population = [
        Individual(genotype=random_genotype(config.genotype_length, rng))
        for _ in range(config.population_size)
    ]

    best_history = []

    for gen in range(config.generations):
        for ind in population:
            ind.program = develop_fn(ind.genotype)
            ind.fitness = evaluate_multi_target(ind, targets, contexts)

        best = max(population, key=lambda ind: ind.fitness)
        best_history.append(best.fitness)

        # (mu+lambda) with crossover OR mutation
        children = []
        for _ in range(config.population_size):
            if rng.random() < config.crossover_rate:
                a = tournament_select(population, config.tournament_size, rng)
                b = tournament_select(population, config.tournament_size, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                parent = tournament_select(population, config.tournament_size, rng)
                child_geno = mutate(parent.genotype, rng)
            children.append(Individual(genotype=child_geno))

        for ind in children:
            ind.program = develop_fn(ind.genotype)
            ind.fitness = evaluate_multi_target(ind, targets, contexts)

        combined = population + children
        combined.sort(key=lambda ind: ind.fitness, reverse=True)
        population = [Individual(genotype=ind.genotype) for ind in combined[:config.population_size]]

    # Final eval
    for ind in population:
        if ind.program is None:
            ind.program = develop_fn(ind.genotype)
            ind.fitness = evaluate_multi_target(ind, targets, contexts)

    best = max(population, key=lambda ind: ind.fitness)
    return {
        "best_history": best_history,
        "final_fitness": best.fitness,
        "best_source": best.program.source if best.program else None,
        "best_bond_count": best.program.bond_count if best.program else 0,
    }


def main():
    config = EvolutionConfig(
        population_size=40,
        genotype_length=50,
        generations=200,  # long enough to show convergence
        tournament_size=3,
        elite_count=3,
        crossover_rate=0.3,
        mutation_rate=1.0,
        seed=42,
    )

    contexts = make_contexts()
    n_seeds = 10

    # Task complexity levels
    task_levels = {
        "1-bond: count(products)": [
            lambda ctx: len(ctx["products"]),
        ],
        "2-bond: count+first": [
            lambda ctx: len(ctx["products"]),
            lambda ctx: ctx["products"][0],
        ],
        "3-target: count+first+rest": [
            lambda ctx: len(ctx["products"]),
            lambda ctx: ctx["products"][0],
            lambda ctx: len(ctx["products"][1:]),
        ],
    }

    print("=" * 70)
    print("CALIBRATION EXPERIMENT")
    print("=" * 70)
    print(f"Population: {config.population_size}, Length: {config.genotype_length}")
    print(f"Generations: {config.generations}, Seeds: {n_seeds}")
    print()

    all_results = {}

    for task_name, targets in task_levels.items():
        print(f"\n{'='*70}")
        print(f"Task: {task_name}")
        print(f"{'='*70}")

        for encoding, develop_fn, label in [
            ("folding", develop, "Folding"),
            ("direct", develop_direct, "Direct"),
        ]:
            results = []
            t0 = time.time()
            for seed in range(n_seeds):
                result = run_stable_evolution(config, targets, contexts, develop_fn, seed)
                results.append(result)
            elapsed = time.time() - t0

            finals = [r["final_fitness"] for r in results]
            avg_final = sum(finals) / len(finals)
            max_final = max(finals)
            min_final = min(finals)
            success_rate = sum(1 for f in finals if f > 0.5) / len(finals)

            # Find gen of first >0.3 fitness across seeds
            first_discovery = []
            for r in results:
                for gen, f in enumerate(r["best_history"]):
                    if f > 0.3:
                        first_discovery.append(gen)
                        break

            avg_first = sum(first_discovery) / len(first_discovery) if first_discovery else -1

            print(f"\n  {label}:")
            print(f"    Avg final fitness: {avg_final:.3f} (min={min_final:.3f}, max={max_final:.3f})")
            print(f"    Success rate (>0.5): {success_rate:.0%}")
            print(f"    Avg gen of first discovery (>0.3): {avg_first:.0f}" if avg_first >= 0 else "    Never discovered >0.3")
            print(f"    Time: {elapsed:.1f}s ({elapsed/n_seeds:.1f}s/run)")
            print(f"    Best programs: {set(r['best_source'] for r in results)}")

            key = f"{task_name}|{encoding}"
            all_results[key] = {
                "results": results,
                "avg_final": avg_final,
                "success_rate": success_rate,
            }

    # Decision gate
    print("\n" + "=" * 70)
    print("CALIBRATION DECISION")
    print("=" * 70)

    # Check if direct encoding succeeds on any task level
    direct_success = False
    for task_name in task_levels:
        key = f"{task_name}|direct"
        if all_results[key]["success_rate"] > 0.5:
            direct_success = True
            print(f"\n  Direct encoding succeeds on: {task_name}")
            print(f"    Success rate: {all_results[key]['success_rate']:.0%}")
            print(f"    -> Use this task level for the 2x2 experiment")

    if not direct_success:
        print("\n  Direct encoding NEVER reliably succeeds (success rate <= 50%)")
        print("  -> Direct encoding is a strawman for the 2x2 experiment")
        print("  -> Options:")
        print("     A) Use DEAP tree GP as the canalized baseline")
        print("     B) Build stack-based assembly as Option B")
        print("     C) Accept that direct encoding is inherently weak and")
        print("        frame the paper as 'folding enables what direct cannot'")

    # Plot convergence curves
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    fig, axes = plt.subplots(1, len(task_levels), figsize=(5 * len(task_levels), 4), sharey=True)
    if len(task_levels) == 1:
        axes = [axes]

    for ax, (task_name, targets) in zip(axes, task_levels.items()):
        for encoding, color, label in [("folding", "blue", "Folding"), ("direct", "red", "Direct")]:
            key = f"{task_name}|{encoding}"
            histories = [r["best_history"] for r in all_results[key]["results"]]

            # Average across seeds
            max_len = max(len(h) for h in histories)
            avg_hist = []
            for gen in range(max_len):
                vals = [h[gen] for h in histories if gen < len(h)]
                avg_hist.append(sum(vals) / len(vals))

            ax.plot(avg_hist, color=color, label=label, linewidth=1.5)

        ax.set_title(task_name, fontsize=9)
        ax.set_xlabel("Generation")
        ax.axhline(y=0.5, color="gray", linestyle=":", alpha=0.5)
        ax.legend(fontsize=8)

    axes[0].set_ylabel("Best Fitness (avg)")
    fig.suptitle("Calibration: Stable Target Convergence", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / "calibration.png", dpi=150)
    print(f"\nPlot saved to {output_dir / 'calibration.png'}")


if __name__ == "__main__":
    main()
