"""
Experiment 1.11: Scaffold Protection Without Full Drift.

Tests whether explicit scaffold protection (Pareto selection on
fitness × scaffold stage) can recover the drift benefit without
turning off selection entirely.

Three conditions (same motifs, same seeds):
  A. Continuous selection (baseline — ceiling blocked)
  B. Drift 10/20 (positive control — ceiling broken)
  C. Pareto(fitness, scaffold_stage): non-dominated sorting keeps
     scaffold carriers alive alongside fit individuals

If Pareto works: the mechanism is specifically about preserving
scaffold carriers, not drift's broader effects.

If Pareto fails: drift provides something beyond preservation —
random exploration or diversification that Pareto can't replicate.

Uses develop_batch and Rust VM scoring for performance.
Scaffold detection every 5 gens.
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


# ---------------------------------------------------------------------------
# Pareto selection on (fitness, scaffold_stage)
# ---------------------------------------------------------------------------

def pareto_select(population: list[Individual], pop_size: int) -> list[Individual]:
    """Non-dominated sorting on (fitness, scaffold_stage).

    An individual A dominates B if A.fitness >= B.fitness AND
    scaffold_stage(A) >= scaffold_stage(B), with at least one strict.

    Fills the next generation front-by-front. Within the last front
    that doesn't fully fit, prefer higher scaffold stage (the rarer
    objective) to break ties.
    """
    # Score each individual on both objectives
    scored = []
    for ind in population:
        stage = scaffold_stage(ind.program) if ind.program else 0
        scored.append((ind, ind.fitness, stage))

    # Non-dominated sorting
    fronts = []
    remaining = list(range(len(scored)))

    while remaining and len(fronts) < pop_size:
        front = []
        for i in remaining:
            dominated = False
            for j in remaining:
                if i == j:
                    continue
                _, fi, si = scored[i]
                _, fj, sj = scored[j]
                # j dominates i if j >= i on both and strictly > on at least one
                if fj >= fi and sj >= si and (fj > fi or sj > si):
                    dominated = True
                    break
            if not dominated:
                front.append(i)
        fronts.append(front)
        remaining = [i for i in remaining if i not in front]

    # Fill population front by front
    selected = []
    for front in fronts:
        if len(selected) + len(front) <= pop_size:
            selected.extend(front)
        else:
            # Partial front: prefer higher scaffold stage
            front_scored = [(i, scored[i][2]) for i in front]
            front_scored.sort(key=lambda x: x[1], reverse=True)
            for i, _ in front_scored:
                if len(selected) >= pop_size:
                    break
                selected.append(i)
            break

    return [Individual(genotype=scored[i][0].genotype) for i in selected]


# ---------------------------------------------------------------------------
# Evolution engine
# ---------------------------------------------------------------------------

def run_seed(
    pop_size, genotype_length, total_gens, contexts, targets, seed,
    mode,  # "select", "drift", or "pareto"
    drift_interval=20, drift_duration=10,
    scaffold_every=5,
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
    filter_programs = []
    stage_trace = []

    # Carrier lifetime tracking
    s1_run = 0
    s2_run = 0
    s1_runs = []
    s2_runs = []
    s1_cooccur = 0
    s2_cooccur = 0

    for gen in range(total_gens):
        # Determine drift phase (only for "drift" mode)
        if mode == "drift":
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

        # Scaffold detection
        if gen % scaffold_every == 0 or gen == total_gens - 1:
            genotypes = [ind.genotype for ind in population]
            programs = develop_batch(genotypes)
            for ind, prog in zip(population, programs):
                ind.program = prog

            sc = Counter()
            for ind in population:
                stage = scaffold_stage(ind.program)
                sc[stage] += 1
                if stage >= 4 and ind.program.source and "filter" in ind.program.source and "get x :price" in ind.program.source:
                    filter_programs.append((gen, ind.program.source, ind.fitness))

            s1p = sum(c for s, c in sc.items() if s >= 1)
            s2p = sum(c for s, c in sc.items() if s >= 2)
            s3p = sum(c for s, c in sc.items() if s >= 3)
            s4p = sum(c for s, c in sc.items() if s >= 4)
            s5p = sum(c for s, c in sc.items() if s >= 5)
            stage_trace.append((gen, phase, s1p, s2p, s3p, s4p, s5p))

            for s in sc:
                if s > max_stage_ever:
                    max_stage_ever = s
            if s3p > 0 and first_s3 is None: first_s3 = gen
            if s4p > 0 and first_s4 is None: first_s4 = gen
            if s5p > 0 and first_s5 is None: first_s5 = gen

            # Carrier lifetime
            if s1p > 0:
                s1_run += scaffold_every
            else:
                if s1_run > 0: s1_runs.append(s1_run)
                s1_run = 0
            if s2p > 0:
                s2_run += scaffold_every
            else:
                if s2_run > 0: s2_runs.append(s2_run)
                s2_run = 0
            if s1p >= 2: s1_cooccur += 1
            if s2p >= 2: s2_cooccur += 1

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
            # Pure drift
            rng.shuffle(combined)
            population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]
        elif mode == "pareto":
            # Pareto: need programs for scaffold_stage
            genotypes = [ind.genotype for ind in combined]
            programs = develop_batch(genotypes)
            for ind, prog in zip(combined, programs):
                ind.program = prog
            population = pareto_select(combined, pop_size)
        else:
            # Standard fitness selection
            combined.sort(key=lambda ind: ind.fitness, reverse=True)
            population = [Individual(genotype=ind.genotype)
                          for ind in combined[:pop_size]]

    # Close open runs
    if s1_run > 0: s1_runs.append(s1_run)
    if s2_run > 0: s2_runs.append(s2_run)

    avg = lambda lst: sum(lst) / len(lst) if lst else 0.0

    return {
        "best_fitness": best_fitness_ever,
        "best_source": best_source_ever,
        "max_stage": max_stage_ever,
        "first_s3": first_s3,
        "first_s4": first_s4,
        "first_s5": first_s5,
        "filter_programs": filter_programs,
        "stage_trace": stage_trace,
        "s1_avg_lifetime": avg(s1_runs),
        "s2_avg_lifetime": avg(s2_runs),
        "s1_cooccur": s1_cooccur,
        "s2_cooccur": s2_cooccur,
    }


def main():
    pop_size = 100
    genotype_length = 100
    total_gens = 300
    n_seeds = 20
    contexts = make_contexts()
    targets = [tfn for _, tfn in TARGETS]

    conditions = [
        ("A. Continuous selection", "select"),
        ("B. Drift 10/20 (control)", "drift"),
        ("C. Pareto(fitness, scaffold)", "pareto"),
    ]

    print("=" * 70)
    print("Experiment 1.11: Scaffold Protection Without Full Drift")
    print("=" * 70)
    print(f"Pop: {pop_size}, Length: {genotype_length}, Gens: {total_gens}, "
          f"Seeds: {n_seeds}")
    print(f"Rust VM: {'YES' if _USE_RUST_VM else 'NO'}")
    print()

    all_results = {}

    for cond_name, mode in conditions:
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
                seed, mode,
            )
            cond_results.append(result)

            if result["first_s3"] is not None: s3_count += 1
            if result["first_s4"] is not None: s4_count += 1
            if result["first_s5"] is not None: s5_count += 1
            if result["filter_programs"]: filter_count += 1

            f_s3 = f"gen {result['first_s3']}" if result["first_s3"] is not None else "NEVER"
            f_s4 = f"gen {result['first_s4']}" if result["first_s4"] is not None else "NEVER"
            f_s5 = f"gen {result['first_s5']}" if result["first_s5"] is not None else "NEVER"
            s1l = f"{result['s1_avg_lifetime']:.0f}"
            s2l = f"{result['s2_avg_lifetime']:.0f}"

            print(f"  Seed {seed:2d}: fit={result['best_fitness']:.3f} "
                  f"S3={f_s3:>8s} S4={f_s4:>8s} S5={f_s5:>8s} "
                  f"s1_life={s1l:>4s} s2_life={s2l:>4s} "
                  f"src={result['best_source']}")

        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.1f}s ({elapsed/n_seeds:.1f}s/seed)")
        print(f"  S3: {s3_count}/{n_seeds}, S4: {s4_count}/{n_seeds}, "
              f"S5: {s5_count}/{n_seeds}, Filter: {filter_count}/{n_seeds}\n")
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
        avg_s1_life = sum(r["s1_avg_lifetime"] for r in results) / len(results)
        avg_s2_life = sum(r["s2_avg_lifetime"] for r in results) / len(results)
        avg_s1_cooccur = sum(r["s1_cooccur"] for r in results) / len(results)
        avg_s2_cooccur = sum(r["s2_cooccur"] for r in results) / len(results)

        print(f"\n  {cond_name}:")
        print(f"    Avg fitness: {avg_fit:.3f}")
        print(f"    S3: {s3_seeds}/{n_seeds}, S4: {s4_seeds}/{n_seeds}, "
              f"S5: {s5_seeds}/{n_seeds}, Filter: {filter_seeds}/{n_seeds}")
        print(f"    Carrier lifetimes: S1={avg_s1_life:.1f}, S2={avg_s2_life:.1f}")
        print(f"    Co-occurrence (sampled gens with 2+): "
              f"S1={avg_s1_cooccur:.1f}, S2={avg_s2_cooccur:.1f}")

    # Stage trace
    print("\n--- Stage occupancy over time (avg across seeds) ---")
    for cond_name, results in all_results.items():
        print(f"\n  {cond_name}:")
        all_gens = sorted(set(g for r in results for g, *_ in r["stage_trace"]))
        for gen in all_gens:
            if gen > 0 and gen % 25 != 0 and gen != all_gens[-1]:
                continue
            vals = {"s1": [], "s2": [], "s3": [], "s4": [], "s5": []}
            phase = "?"
            for r in results:
                for g, p, s1, s2, s3, s4, s5 in r["stage_trace"]:
                    if g == gen:
                        vals["s1"].append(s1)
                        vals["s2"].append(s2)
                        vals["s3"].append(s3)
                        vals["s4"].append(s4)
                        vals["s5"].append(s5)
                        phase = p
                        break
            if vals["s1"]:
                avg = lambda v: sum(v) / len(v)
                print(f"    Gen {gen:3d} [{phase:6s}]: "
                      f"S1+={avg(vals['s1']):5.1f} S2+={avg(vals['s2']):5.1f} "
                      f"S3+={avg(vals['s3']):5.1f} S4+={avg(vals['s4']):5.1f} "
                      f"S5+={avg(vals['s5']):5.1f}")


if __name__ == "__main__":
    main()
