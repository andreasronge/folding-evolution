"""
Experiment 1.9: Consolidation — Drift + Screened Motifs at Scale.

Confirms the 1.8 drift result is robust at larger scale: 50 seeds,
pop=200, 500 gens, best drift schedule (10/20). Measures whether the
correct filter program appears and what fitness it achieves.

Two conditions (same motifs, same seeds):
  A. Continuous selection (baseline)
  B. Drift 10/20 (the 1.8 winner)

Key readout: does the exact target program
  count(filter(fn x (> (get x :price) VALUE)) data/products)
appear? At what rate? What fitness?

Scaffold detection every 5 gens to reduce overhead.
"""

import random
import time
from collections import Counter

from folding_evolution.alphabet import random_genotype
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, develop_batch
from folding_evolution.dynamics import (
    _develop_and_score_vm, _develop_population, evaluate_multi_target,
)
from folding_evolution.selection import tournament_select

try:
    from _folding_rust import (
        RustContexts as _RustContexts,
        RustTargetOutputs as _RustTargetOutputs,
    )
    _USE_RUST_VM = True
except ImportError:
    _USE_RUST_VM = False

from exp_archive_reinjection import scaffold_stage, make_contexts, TARGETS


# Screened motifs (from 1.5b)
SCREENED_MOTIFS = [
    'DaL', 'KaD', 'aDM', 'jDa', '3aD', 'DaB', 'caD', 'aJD',
    'aDT', 'QaD', 'iDa', 'raD', 'aDl', 'aDi', 'aDG', 'aDP',
    'aD', 'Da', 'KS', 'A7',
]


def mutate_with_motif(genotype: str, rng: random.Random) -> str:
    if rng.random() < 0.75:
        motif = rng.choice(SCREENED_MOTIFS)
        if len(motif) > len(genotype):
            return mutate(genotype, rng)
        pos = rng.randint(0, len(genotype) - len(motif))
        return genotype[:pos] + motif + genotype[pos + len(motif):]
    return mutate(genotype, rng)


def run_seed(
    pop_size, genotype_length, total_gens, contexts, targets, seed,
    drift_interval, drift_duration, scaffold_every=5,
):
    rng = random.Random(seed)
    develop.cache_clear()

    population = [
        Individual(genotype=random_genotype(genotype_length, rng))
        for _ in range(pop_size)
    ]

    use_vm = _USE_RUST_VM
    rust_ctx = None
    rust_targets = None
    if use_vm:
        rust_ctx = _RustContexts(contexts)
        target_outputs = [[t(ctx) for ctx in contexts] for t in targets]
        rust_targets = _RustTargetOutputs(target_outputs)

    # Tracking
    best_fitness_ever = 0.0
    best_source_ever = None
    max_stage_ever = 0
    first_s3 = None
    first_s4 = None
    first_s5 = None
    filter_programs_found = []  # (gen, source, fitness)
    stage_trace = []  # (gen, phase, s1+, s2+, s3+, s4+, s5+)

    for gen in range(total_gens):
        if drift_interval is not None and drift_duration > 0:
            cycle_pos = gen % drift_interval
            in_drift = cycle_pos >= (drift_interval - drift_duration)
        else:
            in_drift = False

        phase = "drift" if in_drift else "select"

        # Develop and score
        if use_vm:
            _develop_and_score_vm(population, rust_ctx, rust_targets)
        else:
            _develop_population(population, develop, use_batch=True)
            for ind in population:
                ind.fitness = evaluate_multi_target(ind, targets, contexts)

        # Track best fitness
        best = max(population, key=lambda i: i.fitness)
        if best.fitness > best_fitness_ever:
            best_fitness_ever = best.fitness
            best_source_ever = best.program.source if best.program else None

        # Scaffold detection (every N gens to save time)
        if gen % scaffold_every == 0 or gen == total_gens - 1:
            genotypes = [ind.genotype for ind in population]
            programs = develop_batch(genotypes)
            for ind, prog in zip(population, programs):
                ind.program = prog

            sc = Counter()
            for ind in population:
                stage = scaffold_stage(ind.program)
                sc[stage] += 1

                # Check for filter programs
                if stage >= 4 and ind.program.source:
                    src = ind.program.source
                    if "filter" in src and "get x :price" in src:
                        filter_programs_found.append((gen, src, ind.fitness))

            s1p = sum(c for s, c in sc.items() if s >= 1)
            s2p = sum(c for s, c in sc.items() if s >= 2)
            s3p = sum(c for s, c in sc.items() if s >= 3)
            s4p = sum(c for s, c in sc.items() if s >= 4)
            s5p = sum(c for s, c in sc.items() if s >= 5)
            stage_trace.append((gen, phase, s1p, s2p, s3p, s4p, s5p))

            for s in sc:
                if s > max_stage_ever:
                    max_stage_ever = s
            if s3p > 0 and first_s3 is None:
                first_s3 = gen
            if s4p > 0 and first_s4 is None:
                first_s4 = gen
            if s5p > 0 and first_s5 is None:
                first_s5 = gen

        # Reproduce
        children = []
        for _ in range(pop_size):
            if rng.random() < 0.7:
                a = tournament_select(population, 3, rng)
                b = tournament_select(population, 3, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                parent = tournament_select(population, 3, rng)
                child_geno = mutate_with_motif(parent.genotype, rng)
            children.append(Individual(genotype=child_geno))

        # Evaluate children
        if use_vm:
            _develop_and_score_vm(children, rust_ctx, rust_targets)
        else:
            _develop_population(children, develop, use_batch=True)
            for ind in children:
                ind.fitness = evaluate_multi_target(ind, targets, contexts)

        # Selection
        combined = population + children
        if in_drift:
            rng.shuffle(combined)
            population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]
        else:
            combined.sort(key=lambda ind: ind.fitness, reverse=True)
            population = [Individual(genotype=ind.genotype)
                          for ind in combined[:pop_size]]

    return {
        "best_fitness": best_fitness_ever,
        "best_source": best_source_ever,
        "max_stage": max_stage_ever,
        "first_s3": first_s3,
        "first_s4": first_s4,
        "first_s5": first_s5,
        "filter_programs": filter_programs_found,
        "stage_trace": stage_trace,
    }


def main():
    pop_size = 200
    genotype_length = 100
    total_gens = 500
    n_seeds = 50
    contexts = make_contexts()
    targets = [tfn for _, tfn in TARGETS]

    conditions = [
        ("A. Continuous selection", None, 0),
        ("B. Drift 10/20", 20, 10),
    ]

    print("=" * 70)
    print("Experiment 1.9: Consolidation — Drift at Scale")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {total_gens}, "
          f"Seeds: {n_seeds}")
    print(f"Rust VM: {'YES' if _USE_RUST_VM else 'NO'}")
    print()

    all_results = {}

    for cond_name, drift_interval, drift_duration in conditions:
        print(f"--- {cond_name} ---")
        cond_results = []
        t0 = time.time()

        s3_count = 0
        s4_count = 0
        s5_count = 0
        filter_count = 0

        for seed in range(n_seeds):
            result = run_seed(
                pop_size, genotype_length, total_gens, contexts, targets,
                seed, drift_interval, drift_duration,
            )
            cond_results.append(result)

            if result["first_s3"] is not None: s3_count += 1
            if result["first_s4"] is not None: s4_count += 1
            if result["first_s5"] is not None: s5_count += 1
            if result["filter_programs"]: filter_count += 1

            f_s3 = f"gen {result['first_s3']}" if result["first_s3"] is not None else "NEVER"
            f_s4 = f"gen {result['first_s4']}" if result["first_s4"] is not None else "NEVER"
            f_s5 = f"gen {result['first_s5']}" if result["first_s5"] is not None else "NEVER"
            filt = f"{len(result['filter_programs'])} found" if result["filter_programs"] else ""

            print(f"  Seed {seed:2d}: fit={result['best_fitness']:.3f} "
                  f"S3={f_s3:>8s} S4={f_s4:>8s} S5={f_s5:>8s} "
                  f"max={result['max_stage']} {filt}")

        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.1f}s ({elapsed/n_seeds:.1f}s/seed)")
        print(f"  S3: {s3_count}/{n_seeds}, S4: {s4_count}/{n_seeds}, "
              f"S5: {s5_count}/{n_seeds}")
        print(f"  Seeds with filter(get x :price) programs: {filter_count}/{n_seeds}\n")
        all_results[cond_name] = cond_results

    # ======================================================================
    # SUMMARY
    # ======================================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for cond_name, results in all_results.items():
        s3_seeds = sum(1 for r in results if r["first_s3"] is not None)
        s4_seeds = sum(1 for r in results if r["first_s4"] is not None)
        s5_seeds = sum(1 for r in results if r["first_s5"] is not None)
        filter_seeds = sum(1 for r in results if r["filter_programs"])

        avg_fit = sum(r["best_fitness"] for r in results) / len(results)

        # Avg first appearance (among seeds where it appeared)
        s3_gens = [r["first_s3"] for r in results if r["first_s3"] is not None]
        s4_gens = [r["first_s4"] for r in results if r["first_s4"] is not None]
        s5_gens = [r["first_s5"] for r in results if r["first_s5"] is not None]
        avg_s3_gen = sum(s3_gens) / len(s3_gens) if s3_gens else float('inf')
        avg_s4_gen = sum(s4_gens) / len(s4_gens) if s4_gens else float('inf')
        avg_s5_gen = sum(s5_gens) / len(s5_gens) if s5_gens else float('inf')

        print(f"\n  {cond_name}:")
        print(f"    Avg best fitness: {avg_fit:.3f}")
        print(f"    S3: {s3_seeds}/{n_seeds} (avg gen {avg_s3_gen:.0f})")
        print(f"    S4: {s4_seeds}/{n_seeds} (avg gen {avg_s4_gen:.0f})")
        print(f"    S5: {s5_seeds}/{n_seeds} (avg gen {avg_s5_gen:.0f})")
        print(f"    Filter programs found: {filter_seeds}/{n_seeds} seeds")

        # List all unique filter programs found
        all_filters = []
        for r in results:
            for gen, src, fit in r["filter_programs"]:
                all_filters.append((src, fit, gen))
        if all_filters:
            unique_filters = {}
            for src, fit, gen in all_filters:
                if src not in unique_filters or fit > unique_filters[src][0]:
                    unique_filters[src] = (fit, gen)
            print(f"    Unique filter programs:")
            for src, (fit, gen) in sorted(unique_filters.items(),
                                           key=lambda x: x[1][0], reverse=True)[:10]:
                print(f"      fit={fit:.3f} gen={gen:3d}: {src}")

    # Stage trace comparison
    print("\n--- Stage occupancy over time (avg across seeds) ---")
    for cond_name, results in all_results.items():
        print(f"\n  {cond_name}:")
        # Collect all trace gens
        all_gens = sorted(set(g for r in results for g, *_ in r["stage_trace"]))
        for gen in all_gens:
            if gen > 0 and gen % 25 != 0 and gen != all_gens[-1]:
                continue
            s1_vals = []
            s2_vals = []
            s3_vals = []
            s4_vals = []
            s5_vals = []
            phase = "?"
            for r in results:
                for g, p, s1, s2, s3, s4, s5 in r["stage_trace"]:
                    if g == gen:
                        s1_vals.append(s1)
                        s2_vals.append(s2)
                        s3_vals.append(s3)
                        s4_vals.append(s4)
                        s5_vals.append(s5)
                        phase = p
                        break
            if s1_vals:
                avg = lambda v: sum(v) / len(v)
                print(f"    Gen {gen:3d} [{phase:6s}]: "
                      f"S1+={avg(s1_vals):5.1f} S2+={avg(s2_vals):5.1f} "
                      f"S3+={avg(s3_vals):5.1f} S4+={avg(s4_vals):5.1f} "
                      f"S5+={avg(s5_vals):5.1f}")


if __name__ == "__main__":
    main()
