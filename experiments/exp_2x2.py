#!/usr/bin/env python3
"""2x2 Experiment: Representation x Selection Regime.

Design:
              Stable target    Shifting target
Folding       (F+S)            (F+Sh)
Direct        (B+S)            (B+Sh)

Tests Altenberg's prediction: canalized maps favor stability,
developmental maps favor adaptation under environmental change.

Shift frequency sweep: N = 5, 10, 20, 50 gens between target changes.
"""

import sys
import time
import random
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from folding_evolution.config import EvolutionConfig
from folding_evolution.data_contexts import make_contexts
from folding_evolution.dynamics import evaluate_multi_target
from folding_evolution.individual import Individual
from folding_evolution.alphabet import random_genotype
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop
from folding_evolution.direct import develop_direct
from folding_evolution.selection import tournament_select
from folding_evolution.stats import StatsCollector


# === Task pool: structurally related count targets ===
# Calibrated from Phase 1 — direct encoding can solve these given enough time.

TASK_POOL = [
    ("count(products)", [lambda ctx: len(ctx["products"])]),
    ("count(employees)", [lambda ctx: len(ctx["employees"])]),
    ("count(orders)", [lambda ctx: len(ctx["orders"])]),
    ("count(expenses)", [lambda ctx: len(ctx["expenses"])]),
]


def run_stable(config, targets, contexts, develop_fn, seed, generations):
    """Run evolution with a fixed target for all generations."""
    rng = random.Random(seed)
    develop.cache_clear()
    develop_direct.cache_clear()

    population = [
        Individual(genotype=random_genotype(config.genotype_length, rng))
        for _ in range(config.population_size)
    ]

    stats = StatsCollector()

    for gen in range(generations):
        for ind in population:
            ind.program = develop_fn(ind.genotype)
            ind.fitness = evaluate_multi_target(ind, targets, contexts)

        stats.record(gen, population)

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

    return {
        "history": stats.history,
        "final_fitness": stats.history[-1].best_fitness if stats.history else 0.0,
    }


def run_shifting(config, task_pool, contexts, develop_fn, seed, generations, shift_every):
    """Run evolution with cycling targets every shift_every generations."""
    rng = random.Random(seed)
    develop.cache_clear()
    develop_direct.cache_clear()

    population = [
        Individual(genotype=random_genotype(config.genotype_length, rng))
        for _ in range(config.population_size)
    ]

    stats = StatsCollector()
    shift_gens = []
    n_tasks = len(task_pool)

    for gen in range(generations):
        task_idx = (gen // shift_every) % n_tasks
        _, targets = task_pool[task_idx]

        # Record shift points
        if gen > 0 and gen % shift_every == 0:
            shift_gens.append(gen)

        for ind in population:
            ind.program = develop_fn(ind.genotype)
            ind.fitness = evaluate_multi_target(ind, targets, contexts)

        stats.record(gen, population)

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

    # Count fitness jumps
    jumps = 0
    for i in range(1, len(stats.history)):
        delta = stats.history[i].best_fitness - stats.history[i - 1].best_fitness
        if delta > 0.1:
            jumps += 1

    # Recovery speed: avg gens to recover >0.3 fitness after each shift
    recovery_gens = []
    for sg in shift_gens:
        for g in range(sg, min(sg + shift_every, generations)):
            if g < len(stats.history) and stats.history[g].best_fitness > 0.3:
                recovery_gens.append(g - sg)
                break

    return {
        "history": stats.history,
        "final_fitness": stats.history[-1].best_fitness if stats.history else 0.0,
        "shift_gens": shift_gens,
        "fitness_jumps": jumps,
        "recovery_gens": recovery_gens,
    }


def main():
    config = EvolutionConfig(
        population_size=50,
        genotype_length=50,
        generations=200,
        tournament_size=3,
        elite_count=3,
        crossover_rate=0.3,
        mutation_rate=1.0,
        seed=42,
    )

    contexts = make_contexts()
    n_seeds = 30
    shift_frequencies = [5, 10, 20, 50]
    generations = 200

    # Use the first task for stable condition
    stable_task_name, stable_targets = TASK_POOL[0]

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("2x2 EXPERIMENT: Representation x Selection Regime")
    print("=" * 70)
    print(f"Population: {config.population_size}, Length: {config.genotype_length}")
    print(f"Generations: {generations}, Seeds: {n_seeds}")
    print(f"Stable task: {stable_task_name}")
    print(f"Shifting task pool: {[t[0] for t in TASK_POOL]}")
    print(f"Shift frequencies: {shift_frequencies}")
    print()

    # ============================================================
    # 1. STABLE CONDITION (F+S and B+S)
    # ============================================================
    print("=" * 70)
    print("PHASE 1: Stable target")
    print("=" * 70)

    stable_results = {}
    for encoding, develop_fn, label in [
        ("folding", develop, "Folding"),
        ("direct", develop_direct, "Direct"),
    ]:
        t0 = time.time()
        runs = []
        for seed in range(n_seeds):
            result = run_stable(config, stable_targets, contexts, develop_fn, seed, generations)
            runs.append(result)
            if (seed + 1) % 10 == 0:
                print(f"  {label}: {seed + 1}/{n_seeds} seeds done")
        elapsed = time.time() - t0

        finals = [r["final_fitness"] for r in runs]
        print(f"\n  {label} stable: avg={np.mean(finals):.3f}, "
              f"std={np.std(finals):.3f}, time={elapsed:.1f}s")

        stable_results[encoding] = runs

    # ============================================================
    # 2. SHIFTING CONDITION — sweep shift frequencies
    # ============================================================
    shift_results = {}  # {shift_freq: {encoding: [runs]}}

    for shift_every in shift_frequencies:
        print(f"\n{'=' * 70}")
        print(f"PHASE 2: Shifting target (every {shift_every} gens)")
        print("=" * 70)

        shift_results[shift_every] = {}

        for encoding, develop_fn, label in [
            ("folding", develop, "Folding"),
            ("direct", develop_direct, "Direct"),
        ]:
            t0 = time.time()
            runs = []
            for seed in range(n_seeds):
                result = run_shifting(
                    config, TASK_POOL, contexts, develop_fn,
                    seed, generations, shift_every,
                )
                runs.append(result)
                if (seed + 1) % 10 == 0:
                    print(f"  {label}: {seed + 1}/{n_seeds} seeds done")
            elapsed = time.time() - t0

            finals = [r["final_fitness"] for r in runs]
            jumps = [r["fitness_jumps"] for r in runs]
            print(f"\n  {label} shift={shift_every}: avg_final={np.mean(finals):.3f}, "
                  f"std={np.std(finals):.3f}, avg_jumps={np.mean(jumps):.1f}, "
                  f"time={elapsed:.1f}s")

            shift_results[shift_every][encoding] = runs

    # ============================================================
    # 3. ANALYSIS
    # ============================================================
    print(f"\n{'=' * 70}")
    print("RESULTS SUMMARY")
    print("=" * 70)

    from scipy import stats as sp_stats

    # --- Summary table ---
    print(f"\n{'Condition':<30} {'Folding':<25} {'Direct':<25} {'p-value':<10}")
    print("-" * 90)

    # Stable
    f_stable = [r["final_fitness"] for r in stable_results["folding"]]
    d_stable = [r["final_fitness"] for r in stable_results["direct"]]
    _, p_stable = sp_stats.mannwhitneyu(f_stable, d_stable, alternative="two-sided")
    print(f"{'Stable':<30} {np.mean(f_stable):.3f} +/- {np.std(f_stable):.3f}      "
          f"{np.mean(d_stable):.3f} +/- {np.std(d_stable):.3f}      {p_stable:.4f}")

    for shift_every in shift_frequencies:
        f_shift = [r["final_fitness"] for r in shift_results[shift_every]["folding"]]
        d_shift = [r["final_fitness"] for r in shift_results[shift_every]["direct"]]
        _, p_shift = sp_stats.mannwhitneyu(f_shift, d_shift, alternative="two-sided")
        label = f"Shifting (N={shift_every})"
        print(f"{label:<30} {np.mean(f_shift):.3f} +/- {np.std(f_shift):.3f}      "
              f"{np.mean(d_shift):.3f} +/- {np.std(d_shift):.3f}      {p_shift:.4f}")

    # --- Two-way ANOVA for each shift frequency ---
    print(f"\n{'=' * 70}")
    print("INTERACTION TESTS (Two-way ANOVA: Representation x Regime)")
    print("=" * 70)

    for shift_every in shift_frequencies:
        f_shift = [r["final_fitness"] for r in shift_results[shift_every]["folding"]]
        d_shift = [r["final_fitness"] for r in shift_results[shift_every]["direct"]]

        # Manual 2x2 ANOVA via F-test on interaction term
        # Groups: F+S, F+Sh, D+S, D+Sh
        all_data = f_stable + f_shift + d_stable + d_shift
        n = n_seeds
        grand_mean = np.mean(all_data)

        # Factor means
        folding_mean = np.mean(f_stable + f_shift)
        direct_mean = np.mean(d_stable + d_shift)
        stable_mean = np.mean(f_stable + d_stable)
        shift_mean = np.mean(f_shift + d_shift)

        # Cell means
        fs_mean = np.mean(f_stable)
        fsh_mean = np.mean(f_shift)
        ds_mean = np.mean(d_stable)
        dsh_mean = np.mean(d_shift)

        # SS interaction
        ss_interaction = n * sum([
            (fs_mean - folding_mean - stable_mean + grand_mean) ** 2,
            (fsh_mean - folding_mean - shift_mean + grand_mean) ** 2,
            (ds_mean - direct_mean - stable_mean + grand_mean) ** 2,
            (dsh_mean - direct_mean - shift_mean + grand_mean) ** 2,
        ])

        # SS within (error)
        ss_within = (
            sum((x - fs_mean) ** 2 for x in f_stable) +
            sum((x - fsh_mean) ** 2 for x in f_shift) +
            sum((x - ds_mean) ** 2 for x in d_stable) +
            sum((x - dsh_mean) ** 2 for x in d_shift)
        )

        df_interaction = 1
        df_within = 4 * n - 4
        ms_interaction = ss_interaction / df_interaction
        ms_within = ss_within / df_within

        f_stat = ms_interaction / ms_within if ms_within > 0 else 0
        p_interaction = 1 - sp_stats.f.cdf(f_stat, df_interaction, df_within)

        # Effect size (partial eta-squared)
        eta_sq = ss_interaction / (ss_interaction + ss_within)

        print(f"\n  Shift every {shift_every} gens:")
        print(f"    F+S={fs_mean:.3f}  F+Sh={fsh_mean:.3f}  D+S={ds_mean:.3f}  D+Sh={dsh_mean:.3f}")
        print(f"    Interaction: F({df_interaction},{df_within})={f_stat:.2f}, p={p_interaction:.4f}")
        print(f"    Effect size (partial eta^2): {eta_sq:.3f}")
        sig = "***" if p_interaction < 0.001 else "**" if p_interaction < 0.01 else "*" if p_interaction < 0.05 else "ns"
        print(f"    Significance: {sig}")

    # --- Recovery speed ---
    print(f"\n{'=' * 70}")
    print("RECOVERY SPEED (avg gens to reach >0.3 after shift)")
    print("=" * 70)

    for shift_every in shift_frequencies:
        for encoding, label in [("folding", "Folding"), ("direct", "Direct")]:
            all_recovery = []
            for r in shift_results[shift_every][encoding]:
                all_recovery.extend(r["recovery_gens"])
            if all_recovery:
                print(f"  {label} (N={shift_every}): {np.mean(all_recovery):.1f} gens "
                      f"(median={np.median(all_recovery):.0f})")
            else:
                print(f"  {label} (N={shift_every}): never recovered")

    # ============================================================
    # 4. PLOTS
    # ============================================================

    # --- Main 4-curve figure for each shift frequency ---
    for shift_every in shift_frequencies:
        fig, ax = plt.subplots(figsize=(10, 6))

        for runs, color, linestyle, label in [
            (stable_results["folding"], "blue", "-", "Folding + Stable"),
            (shift_results[shift_every]["folding"], "blue", "--", "Folding + Shifting"),
            (stable_results["direct"], "red", "-", "Direct + Stable"),
            (shift_results[shift_every]["direct"], "red", "--", "Direct + Shifting"),
        ]:
            n_gens = min(len(r["history"]) for r in runs)
            mean_best = []
            for g in range(n_gens):
                vals = [r["history"][g].best_fitness for r in runs]
                mean_best.append(np.mean(vals))

            ax.plot(range(n_gens), mean_best, color=color, linestyle=linestyle,
                    linewidth=2, label=label)

        # Mark shift points
        if shift_every < generations:
            for sg in range(shift_every, generations, shift_every):
                ax.axvline(x=sg, color="gray", linestyle=":", alpha=0.3)

        ax.set_xlabel("Generation")
        ax.set_ylabel("Best Fitness (mean over seeds)")
        ax.set_title(f"2x2: Representation x Regime (shift every {shift_every} gens, {n_seeds} seeds)")
        ax.legend(loc="lower right")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        fig.savefig(output_dir / f"2x2_shift{shift_every}.png", dpi=150)
        print(f"Plot saved to {output_dir / f'2x2_shift{shift_every}.png'}")
        plt.close(fig)

    # --- Folding advantage vs shift frequency curve ---
    fig, ax = plt.subplots(figsize=(8, 5))

    freq_labels = ["Stable"] + [str(n) for n in shift_frequencies]
    folding_means = [np.mean(f_stable)]
    direct_means = [np.mean(d_stable)]
    advantages = [np.mean(f_stable) - np.mean(d_stable)]

    for sf in shift_frequencies:
        fm = np.mean([r["final_fitness"] for r in shift_results[sf]["folding"]])
        dm = np.mean([r["final_fitness"] for r in shift_results[sf]["direct"]])
        folding_means.append(fm)
        direct_means.append(dm)
        advantages.append(fm - dm)

    x = range(len(freq_labels))
    ax.bar(x, advantages, color=["gray"] + ["steelblue"] * len(shift_frequencies), alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(freq_labels)
    ax.set_xlabel("Shift Frequency (gens between shifts)")
    ax.set_ylabel("Folding Advantage (mean final fitness difference)")
    ax.set_title("Folding Advantage vs Shift Frequency")
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    fig.savefig(output_dir / "2x2_advantage_curve.png", dpi=150)
    print(f"Plot saved to {output_dir / '2x2_advantage_curve.png'}")
    plt.close(fig)

    # --- Save raw data as CSV ---
    csv_path = output_dir / "2x2_results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["encoding", "condition", "shift_freq", "seed", "final_fitness", "fitness_jumps"])

        for seed in range(n_seeds):
            writer.writerow(["folding", "stable", "NA", seed,
                             stable_results["folding"][seed]["final_fitness"], "NA"])
            writer.writerow(["direct", "stable", "NA", seed,
                             stable_results["direct"][seed]["final_fitness"], "NA"])

        for sf in shift_frequencies:
            for seed in range(n_seeds):
                for encoding in ["folding", "direct"]:
                    r = shift_results[sf][encoding][seed]
                    writer.writerow([encoding, "shifting", sf, seed,
                                     r["final_fitness"], r["fitness_jumps"]])

    print(f"Raw data saved to {csv_path}")
    print(f"\nTotal runs: {2 * n_seeds + 2 * n_seeds * len(shift_frequencies)} "
          f"({n_seeds} seeds x 2 encodings x {1 + len(shift_frequencies)} conditions)")


if __name__ == "__main__":
    main()
