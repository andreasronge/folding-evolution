#!/usr/bin/env python3
"""Persistent regression benchmark for the folding-evolution pipeline.

Records four metrics to benchmarks/results.csv:
  1. develops/sec — raw pipeline throughput (fold + chemistry + best selection)
  2. fitness_calls/sec — evaluate_multi_target() throughput including LRU cache
  3. cache_hit_rate — fraction of develop() calls served from LRU cache
  4. backend_equivalence — fraction of random genotypes where Rust == Python

Run before/after any change to detect regressions.

Usage:
    python benchmarks/regression.py           # run and append to CSV
    python benchmarks/regression.py --show    # show history
"""

import sys
import os
import csv
import time
import random
import subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from folding_evolution.phenotype import develop, _USE_RUST
import folding_evolution.phenotype as phenotype_mod
from folding_evolution.dynamics import evaluate_multi_target
from folding_evolution.individual import Individual
from folding_evolution.data_contexts import make_contexts
from folding_evolution.alphabet import random_genotype
from folding_evolution.config import EvolutionConfig
from folding_evolution.operators import crossover, mutate
from folding_evolution.selection import tournament_select


RESULTS_PATH = Path(__file__).resolve().parent / "results.csv"
CORPUS_SEED = 42
CORPUS_SIZE_SHORT = 1000  # length 30
CORPUS_SIZE_LONG = 1000   # length 50
DEVELOP_BENCH_SIZE = 5000
FITNESS_BENCH_GENS = 50
FITNESS_POP_SIZE = 50


def get_git_hash():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=Path(__file__).resolve().parent.parent,
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return "unknown"


def get_backend():
    return "rust" if phenotype_mod._USE_RUST else "python"


def bench_develops_per_sec():
    """Raw develop() throughput, no cache."""
    develop.cache_clear()
    rng = random.Random(99)
    genotypes = [
        "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(50))
        for _ in range(DEVELOP_BENCH_SIZE)
    ]

    t0 = time.perf_counter()
    for g in genotypes:
        develop(g)
    elapsed = time.perf_counter() - t0
    develop.cache_clear()
    return DEVELOP_BENCH_SIZE / elapsed


def bench_fitness_calls_per_sec():
    """Evolution-style fitness throughput including cache effects.

    Returns (fitness_calls_per_sec, cache_hit_rate).
    fitness_calls_per_sec = number of evaluate_multi_target() calls per second.
    cache_hit_rate = fraction of develop() calls that hit the LRU cache.
    """
    develop.cache_clear()
    contexts = make_contexts()
    targets = [lambda ctx: len(ctx["products"])]
    rng = random.Random(42)

    population = [
        Individual(genotype=random_genotype(50, rng))
        for _ in range(FITNESS_POP_SIZE)
    ]

    total_fitness_calls = 0
    total_develop_calls = 0

    t0 = time.perf_counter()
    for gen in range(FITNESS_BENCH_GENS):
        for ind in population:
            ind.program = develop(ind.genotype)
            total_develop_calls += 1
            ind.fitness = evaluate_multi_target(ind, targets, contexts)
            total_fitness_calls += 1

        children = []
        for _ in range(FITNESS_POP_SIZE):
            if rng.random() < 0.3:
                a = tournament_select(population, 3, rng)
                b = tournament_select(population, 3, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                parent = tournament_select(population, 3, rng)
                child_geno = mutate(parent.genotype, rng)
            children.append(Individual(genotype=child_geno))

        for ind in children:
            ind.program = develop(ind.genotype)
            total_develop_calls += 1
            ind.fitness = evaluate_multi_target(ind, targets, contexts)
            total_fitness_calls += 1

        combined = population + children
        combined.sort(key=lambda ind: ind.fitness, reverse=True)
        population = [Individual(genotype=ind.genotype) for ind in combined[:FITNESS_POP_SIZE]]

    elapsed = time.perf_counter() - t0

    cache_info = develop.cache_info()
    cache_hit_rate = cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0.0
    develop.cache_clear()

    return total_fitness_calls / elapsed, cache_hit_rate


def bench_backend_equivalence():
    """Fraction of random genotypes where Rust and Python produce identical results.

    Returns (match_rate, total_tested, fn_closures_skipped).
    """
    if not phenotype_mod._USE_RUST:
        return 1.0, 0, 0  # can't test without Rust

    rng = random.Random(CORPUS_SEED)
    total = 0
    matches = 0
    fn_skipped = 0

    ctx = {
        "products": [
            {"price": 600, "name": "Widget", "status": "active"},
            {"price": 400, "name": "Gadget", "status": "inactive"},
        ],
        "employees": [{"name": "Alice", "department": "eng"}],
        "orders": [{"id": 1, "amount": 100}],
        "expenses": [{"amount": 200, "category": "travel"}],
    }

    for length in [30, 50]:
        size = CORPUS_SIZE_SHORT if length == 30 else CORPUS_SIZE_LONG
        for _ in range(size):
            genotype = "".join(
                rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(length)
            )

            # Python
            phenotype_mod._USE_RUST = False
            develop.cache_clear()
            py = develop(genotype)

            # Rust
            phenotype_mod._USE_RUST = True
            develop.cache_clear()
            rs = develop(genotype)

            total += 1
            if py.source == rs.source and py.bond_count == rs.bond_count:
                # Also check eval equivalence (skip fn closures)
                py_result = py.evaluate(ctx)
                rs_result = rs.evaluate(ctx)
                if callable(py_result) or callable(rs_result):
                    fn_skipped += 1
                    matches += 1  # source matches, can't compare closures
                elif repr(py_result) == repr(rs_result):
                    matches += 1

    phenotype_mod._USE_RUST = True
    develop.cache_clear()
    return matches / total if total > 0 else 0.0, total, fn_skipped


def run():
    backend = get_backend()
    git_hash = get_git_hash()
    timestamp = datetime.now().isoformat(timespec="seconds")

    print(f"Regression benchmark | backend={backend} | commit={git_hash}")
    print("=" * 60)

    # 1. develops/sec
    develops_sec = bench_develops_per_sec()
    print(f"  develops/sec:          {develops_sec:,.0f}")

    # 2. fitness_calls/sec + cache hit rate
    fitness_sec, cache_rate = bench_fitness_calls_per_sec()
    print(f"  fitness_calls/sec:     {fitness_sec:,.0f}")
    print(f"  cache_hit_rate:        {cache_rate:.1%}")

    # 3. backend equivalence
    equiv_rate, equiv_total, fn_skipped = bench_backend_equivalence()
    print(f"  backend_equivalence:   {equiv_rate:.4f} ({equiv_total} tested, {fn_skipped} fn closures skipped)")

    # Append to CSV
    write_header = not RESULTS_PATH.exists()
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "timestamp", "git_hash", "backend",
                "develops_sec", "fitness_calls_sec", "cache_hit_rate",
                "equiv_rate", "equiv_total", "fn_closures_skipped",
            ])
        writer.writerow([
            timestamp, git_hash, backend,
            f"{develops_sec:.0f}", f"{fitness_sec:.0f}", f"{cache_rate:.4f}",
            f"{equiv_rate:.4f}", equiv_total, fn_skipped,
        ])

    print(f"\nResults appended to {RESULTS_PATH}")


def show():
    if not RESULTS_PATH.exists():
        print("No results yet. Run: python benchmarks/regression.py")
        return

    with open(RESULTS_PATH) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"{'Timestamp':<22} {'Hash':<10} {'Backend':<8} {'dev/s':>8} {'fit/s':>8} {'cache':>7} {'equiv':>7}")
    print("-" * 80)
    for r in rows:
        print(f"{r['timestamp']:<22} {r['git_hash']:<10} {r['backend']:<8} "
              f"{r['develops_sec']:>8} {r['fitness_calls_sec']:>8} "
              f"{r['cache_hit_rate']:>7} {r['equiv_rate']:>7}")


if __name__ == "__main__":
    if "--show" in sys.argv:
        show()
    else:
        run()
