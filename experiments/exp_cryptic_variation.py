"""
Experiment 1.15: Cryptic Variation Assay.

Tests whether Pareto-preserved populations adapt faster to novel but
related targets than continuous-selection populations — the direct
stored-evolvability claim.

Phase 1: Evolve three conditions on filter-price-200 for 300 gens,
snapshot the full population at gens 200 and 300.

  A. Continuous selection
  B. Pareto(scaffold_stage) — task-specific preservation (1.11 winner)
  C. Pareto(structural_pattern) — semigeneric preservation (1.13 winner)

Phase 2: For each snapshot, switch target to novel but related and
resume CONTINUOUS SELECTION ONLY (no Pareto, no motif insertion) for
N_ASSAY gens. Motif insertion is disabled in the assay so the only
variable is the variation carried by the starting population.

Two novel targets, chosen to probe two levels of novelty:
  T_near:  count(filter(fn x (> (get x :price) 600)) data/products)
           — same structure, different threshold. Tests scaffold
           reuse with a parameter shift.
  T_far:   count(filter(fn x (> (get x :amount) 300)) data/orders)
           — different field, different data source. Tests whether
           structural scaffolds transfer across target families.
           This is the strong evolvability claim.

Interpretation:
  If Pareto populations adapt faster to T_near AND T_far:
    Preservation accumulates reusable variation (stored evolvability).
  If Pareto populations match continuous selection on both:
    Preservation rescues current-task scaffolds but not cryptic variation.
  If Pareto populations adapt faster on T_near but not T_far:
    Preservation produces parameter-reusable scaffolds but not
    family-transferable ones. Still useful, more narrowly scoped.

If Pareto(structural_pattern) preserves BETTER than Pareto(scaffold_stage)
on the T_far transfer, that's a second independent defense of the
generic-preservation claim from 1.13.
"""

import json
import random
import time
from collections import Counter
from pathlib import Path

from folding_evolution.alphabet import random_genotype
from folding_evolution.ast_nodes import ListExpr, Symbol, Keyword, NsSymbol
from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, develop_batch
from folding_evolution.dynamics import (
    _develop_and_score_vm, _develop_population,
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
from exp_endogenous_scaffold import (
    structural_pattern_score,
    motif_presence_score,
    mutate_with_motif,
    _pareto_sort,
    PRICE_MOTIFS,
)


# ---------------------------------------------------------------------------
# Target families
# ---------------------------------------------------------------------------

PRICE_200_TARGETS = TARGETS  # training target (filter-price-200 + count(products))

# Novel tasks are intentionally SINGLE-TARGET to avoid confound where the
# training population already scores high on a shared secondary target.
# Under single-target novel assays, fitness cleanly reflects adaptation
# to the actually novel thing.
T_NEAR_TARGETS = [
    ("count(filter(price>600, products))",
     lambda ctx: len([p for p in ctx["products"] if p["price"] > 600])),
]

T_FAR_TARGETS = [
    ("count(filter(amount>300, orders))",
     lambda ctx: len([o for o in ctx["orders"] if o["amount"] > 300])),
]


# ---------------------------------------------------------------------------
# Phase 1: Train with snapshots
# ---------------------------------------------------------------------------

def train_with_snapshots(
    pop_size, genotype_length, total_gens, snapshot_gens,
    contexts, targets, seed, objective, motifs,
):
    """Evolve a population with one of three objectives, snapshotting at
    specified generations. Returns dict {gen: [genotypes]} plus a trace.
    """
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

    snapshots: dict[int, list[str]] = {}
    trace = []

    for gen in range(total_gens + 1):
        # Score
        if use_vm:
            _develop_and_score_vm(population, rust_ctx, rust_targets)
        else:
            _develop_population(population, develop, use_batch=True)

        if gen in snapshot_gens:
            snapshots[gen] = [ind.genotype for ind in population]

            # Snapshot scaffold / pattern stats for the report
            genotypes = [ind.genotype for ind in population]
            progs = develop_batch(genotypes)
            for ind, prog in zip(population, progs):
                ind.program = prog
            s3p = sum(1 for i in population if scaffold_stage(i.program) >= 3)
            s4p = sum(1 for i in population if scaffold_stage(i.program) >= 4)
            s5p = sum(1 for i in population if scaffold_stage(i.program) >= 5)
            g3p = sum(1 for i in population if structural_pattern_score(i.program) >= 3)
            g4p = sum(1 for i in population if structural_pattern_score(i.program) >= 4)
            g5p = sum(1 for i in population if structural_pattern_score(i.program) >= 5)
            avg_fit = sum(i.fitness for i in population) / pop_size
            trace.append({
                "gen": gen, "avg_fit": avg_fit,
                "s3": s3p, "s4": s4p, "s5": s5p,
                "g3": g3p, "g4": g4p, "g5": g5p,
            })

        if gen == total_gens:
            break

        # Reproduce
        children = []
        for _ in range(pop_size):
            if rng.random() < 0.7:
                a = tournament_select(population, 3, rng)
                b = tournament_select(population, 3, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                parent = tournament_select(population, 3, rng)
                child_geno = mutate_with_motif(parent.genotype, rng, motifs)
            children.append(Individual(genotype=child_geno))

        if use_vm:
            _develop_and_score_vm(children, rust_ctx, rust_targets)
        else:
            _develop_population(children, develop, use_batch=True)

        combined = population + children

        if objective == "select":
            combined.sort(key=lambda ind: ind.fitness, reverse=True)
            population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]
        else:
            genotypes = [ind.genotype for ind in combined]
            progs = develop_batch(genotypes)
            for ind, prog in zip(combined, progs):
                ind.program = prog

            if objective == "scaffold":
                scored = [(i, i.fitness, scaffold_stage(i.program)) for i in combined]
            elif objective == "structural":
                scored = [(i, i.fitness, structural_pattern_score(i.program))
                          for i in combined]
            population = _pareto_sort(scored, pop_size)

    return snapshots, trace


# ---------------------------------------------------------------------------
# Phase 2: Assay — continuous selection on novel target, no motif insertion
# ---------------------------------------------------------------------------

def assay(starting_genotypes, assay_gens, contexts, novel_targets, seed,
          fitness_thresholds=(0.2, 0.4, 0.6, 0.8)):
    """Resume continuous selection on a novel target from a given starting
    population. No Pareto, no motif insertion — standard mutation + crossover
    + tournament only. Measures how fast variation in the starting population
    becomes useful on the new target.

    Returns a dict with:
      - first_gen_at[threshold]: first gen where best fitness >= threshold
      - best_fitness_trajectory: list of best fitness per gen
      - final_best_fitness
      - inherited_scaffold_frac: fraction of final population that inherited
        a scaffold substring from the starting population
      - starting_pop_stats: S/G scaffold carrier counts at gen 0
      - final_pop_stats: same at final gen
    """
    rng = random.Random(seed)
    pop_size = len(starting_genotypes)

    population = [Individual(genotype=g) for g in starting_genotypes]

    use_vm = _USE_RUST_VM
    rust_ctx = None
    rust_targets = None
    if use_vm:
        rust_ctx = _RustContexts(contexts)
        target_outputs = [[t(ctx) for ctx in contexts] for t in novel_targets]
        rust_targets = _RustTargetOutputs(target_outputs)

    # Starting pop structural stats
    progs = develop_batch(starting_genotypes)
    start_s = Counter()
    start_g = Counter()
    for g_, prog in zip(starting_genotypes, progs):
        start_s[scaffold_stage(prog)] += 1
        start_g[structural_pattern_score(prog)] += 1

    first_gen_at = {t: None for t in fitness_thresholds}
    best_trajectory = []
    best_so_far = 0.0

    for gen in range(assay_gens + 1):
        if use_vm:
            _develop_and_score_vm(population, rust_ctx, rust_targets)
        else:
            _develop_population(population, develop, use_batch=True)

        best = max(ind.fitness for ind in population)
        if best > best_so_far:
            best_so_far = best
        best_trajectory.append(best_so_far)

        for t in fitness_thresholds:
            if first_gen_at[t] is None and best_so_far >= t:
                first_gen_at[t] = gen

        if gen == assay_gens:
            break

        children = []
        for _ in range(pop_size):
            if rng.random() < 0.7:
                a = tournament_select(population, 3, rng)
                b = tournament_select(population, 3, rng)
                child_geno = crossover(a.genotype, b.genotype, rng)
            else:
                parent = tournament_select(population, 3, rng)
                child_geno = mutate(parent.genotype, rng)  # plain mutation, no motifs
            children.append(Individual(genotype=child_geno))

        if use_vm:
            _develop_and_score_vm(children, rust_ctx, rust_targets)
        else:
            _develop_population(children, develop, use_batch=True)

        combined = population + children
        combined.sort(key=lambda ind: ind.fitness, reverse=True)
        population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]

    # Final pop structural stats
    final_genos = [ind.genotype for ind in population]
    progs = develop_batch(final_genos)
    final_s = Counter()
    final_g = Counter()
    for ind, prog in zip(population, progs):
        ind.program = prog
        final_s[scaffold_stage(prog)] += 1
        final_g[structural_pattern_score(prog)] += 1

    return {
        "first_gen_at": first_gen_at,
        "best_trajectory": best_trajectory,
        "final_best_fitness": best_so_far,
        "starting_pop_stats": {
            "S3+": sum(c for s, c in start_s.items() if s >= 3),
            "S4+": sum(c for s, c in start_s.items() if s >= 4),
            "S5+": sum(c for s, c in start_s.items() if s >= 5),
            "G3+": sum(c for g, c in start_g.items() if g >= 3),
            "G4+": sum(c for g, c in start_g.items() if g >= 4),
            "G5+": sum(c for g, c in start_g.items() if g >= 5),
        },
        "final_pop_stats": {
            "S3+": sum(c for s, c in final_s.items() if s >= 3),
            "S4+": sum(c for s, c in final_s.items() if s >= 4),
            "S5+": sum(c for s, c in final_s.items() if s >= 5),
            "G3+": sum(c for g, c in final_g.items() if g >= 3),
            "G4+": sum(c for g, c in final_g.items() if g >= 4),
            "G5+": sum(c for g, c in final_g.items() if g >= 5),
        },
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run_all(n_seeds, pop_size, genotype_length, train_gens, snapshot_gens,
            assay_gens, out_dir):
    contexts = make_contexts()
    price_targets = [tfn for _, tfn in PRICE_200_TARGETS]

    conditions = [
        ("A_continuous", "select"),
        ("B_scaffold", "scaffold"),
        ("C_structural", "structural"),
    ]

    novel_tasks = [
        ("T_near_price600", [tfn for _, tfn in T_NEAR_TARGETS]),
        ("T_far_amount300", [tfn for _, tfn in T_FAR_TARGETS]),
    ]

    results = {}  # condition -> seed -> {gen -> {novel_task -> assay_result}}

    for cond_name, objective in conditions:
        results[cond_name] = {}
        print(f"\n{'=' * 75}")
        print(f"Phase 1 — Training under {cond_name}")
        print(f"{'=' * 75}")
        for seed in range(n_seeds):
            t0 = time.time()
            snapshots, trace = train_with_snapshots(
                pop_size, genotype_length, train_gens, snapshot_gens,
                contexts, price_targets, seed, objective, PRICE_MOTIFS,
            )
            train_time = time.time() - t0
            print(f"  seed {seed}: train {train_time:.1f}s  "
                  f"final avg_fit={trace[-1]['avg_fit']:.3f}  "
                  f"S5+={trace[-1]['s5']}  G5+={trace[-1]['g5']}")

            seed_results = {"trace": trace, "assays": {}}
            for snap_gen in snapshot_gens:
                seed_results["assays"][snap_gen] = {}
                for task_name, task_targets in novel_tasks:
                    assay_seed = seed * 1000 + snap_gen  # deterministic per (seed, snap)
                    r = assay(snapshots[snap_gen], assay_gens, contexts,
                              task_targets, assay_seed)
                    seed_results["assays"][snap_gen][task_name] = r
            results[cond_name][seed] = seed_results

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "cryptic_variation_raw.json", "w") as f:
        json.dump(results, f, default=str, indent=2)

    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def summarize(results, snapshot_gens, novel_task_names, fitness_thresholds):
    print("\n" + "=" * 75)
    print("SUMMARY — Cryptic Variation Assay")
    print("=" * 75)

    for task in novel_task_names:
        print(f"\n--- Novel task: {task} ---")
        for snap_gen in snapshot_gens:
            print(f"\n  Snapshot gen = {snap_gen}")
            header = f"    {'Condition':<20} {'final_best':<12}"
            for t in fitness_thresholds:
                header += f"{'first>=%.1f' % t:<14}"
            header += f"{'start S5+':<10}{'start G5+':<10}"
            print(header)

            for cond_name, seed_results in results.items():
                finals = []
                first_gens = {t: [] for t in fitness_thresholds}
                start_s5 = []
                start_g5 = []
                for seed, sr in seed_results.items():
                    assay_r = sr["assays"][snap_gen][task]
                    finals.append(assay_r["final_best_fitness"])
                    for t in fitness_thresholds:
                        fg = assay_r["first_gen_at"][t]
                        if fg is not None:
                            first_gens[t].append(fg)
                    start_s5.append(assay_r["starting_pop_stats"]["S5+"])
                    start_g5.append(assay_r["starting_pop_stats"]["G5+"])

                n = len(finals)
                mean_final = sum(finals) / n if n else 0
                row = f"    {cond_name:<20} {mean_final:.3f}       "
                for t in fitness_thresholds:
                    fg = first_gens[t]
                    if fg:
                        row += f"{sum(fg)/len(fg):.1f} ({len(fg)}/{n}) "
                    else:
                        row += f"--  (0/{n})    "
                row += f"{sum(start_s5)/n:.1f}       {sum(start_g5)/n:.1f}"
                print(row)


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def main_quick():
    """Small sanity-check run. Verifies the pipeline end-to-end."""
    out = Path(__file__).parent / "output" / "cryptic_quick"
    print("Experiment 1.15 — QUICK mode (3 seeds, short gens)")
    print(f"Output: {out}")
    results = run_all(
        n_seeds=3, pop_size=60, genotype_length=100,
        train_gens=100, snapshot_gens=[50, 100],
        assay_gens=30, out_dir=out,
    )
    summarize(results, [50, 100],
              ["T_near_price600", "T_far_amount300"],
              [0.2, 0.4, 0.6, 0.8])


def main_full():
    """Full run. 15 seeds, 300-gen training, 80-gen assays, both snapshots."""
    out = Path(__file__).parent / "output" / "cryptic_full"
    print("Experiment 1.15 — FULL mode")
    print(f"Output: {out}")
    results = run_all(
        n_seeds=15, pop_size=100, genotype_length=100,
        train_gens=300, snapshot_gens=[200, 300],
        assay_gens=80, out_dir=out,
    )
    summarize(results, [200, 300],
              ["T_near_price600", "T_far_amount300"],
              [0.2, 0.4, 0.6, 0.8])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "full":
        main_full()
    else:
        main_quick()
