#!/usr/bin/env python3
"""Regime-shift experiment: folding vs direct encoding.

Regime A: products-focused (count, first, count-of-rest)
Regime B: employees-focused (count, first, count-of-rest)

The hypothesis is that folding can restructure programs after the shift,
while direct encoding is locked into its initial structure.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from folding_evolution.config import EvolutionConfig
from folding_evolution.data_contexts import make_contexts
from folding_evolution.dynamics import run_regime_shift_comparison
from folding_evolution.visualization import plot_regime_shift, plot_regime_shift_comparison


def main():
    config = EvolutionConfig(
        population_size=50,
        genotype_length=30,
        generations=40,
        tournament_size=3,
        elite_count=2,
        mutation_rate=0.3,
        crossover_rate=0.7,
        seed=42,
    )

    contexts = make_contexts()

    # Multi-target regimes (harder than single count)
    targets_a = [
        lambda ctx: len(ctx["products"]),        # count products
        lambda ctx: ctx["products"][0],           # first product (dict)
        lambda ctx: len(ctx["products"][1:]),     # count of rest(products)
    ]

    targets_b = [
        lambda ctx: len(ctx["employees"]),        # count employees
        lambda ctx: ctx["employees"][0],           # first employee (dict)
        lambda ctx: len(ctx["employees"][1:]),     # count of rest(employees)
    ]

    regime_a_gens = 20
    regime_b_gens = 20
    n_seeds = 5

    print("=" * 60)
    print("REGIME SHIFT EXPERIMENT (multi-target)")
    print("=" * 60)
    print(f"Regime A: products-focused ({regime_a_gens} gens)")
    print(f"  - count(products), first(products), count(rest(products))")
    print(f"Regime B: employees-focused ({regime_b_gens} gens)")
    print(f"  - count(employees), first(employees), count(rest(employees))")
    print(f"Population: {config.population_size}, Length: {config.genotype_length}")
    print(f"Seeds: {n_seeds}")
    print()

    result = run_regime_shift_comparison(
        config, targets_a, targets_b,
        regime_a_gens, regime_b_gens, contexts,
        n_seeds=n_seeds,
    )

    # Print summary
    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    for label, runs in [("Folding", result["folding_runs"]), ("Direct", result["direct_runs"])]:
        print(f"\n--- {label} ---")
        for i, run in enumerate(runs):
            h = run["history"]
            pre_shift = h[regime_a_gens - 1].best_fitness if len(h) > regime_a_gens - 1 else 0
            post_shift = h[regime_a_gens].best_fitness if len(h) > regime_a_gens else 0
            final = h[-1].best_fitness if h else 0
            print(f"  Seed {i}: pre-shift={pre_shift:.3f}, post-shift={post_shift:.3f}, "
                  f"final={final:.3f}, jumps={run['fitness_jumps']}")

    # Averages
    print("\n--- Averages ---")
    for label, runs in [("Folding", result["folding_runs"]), ("Direct", result["direct_runs"])]:
        pre = sum(r["history"][regime_a_gens - 1].best_fitness for r in runs) / n_seeds
        final = sum(r["history"][-1].best_fitness for r in runs) / n_seeds
        jumps = sum(r["fitness_jumps"] for r in runs) / n_seeds
        print(f"  {label}: pre-shift best={pre:.3f}, final best={final:.3f}, "
              f"avg jumps={jumps:.1f}")

    # Save plots
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    plot_regime_shift_comparison(result, save_path=output_dir / "regime_shift_comparison.png")

    plot_regime_shift(
        result["folding_runs"][0]["history"],
        result["direct_runs"][0]["history"],
        shift_gen=regime_a_gens,
        save_path=output_dir / "regime_shift_seed0.png",
    )

    print(f"\nPlots saved to {output_dir}/")


if __name__ == "__main__":
    main()
