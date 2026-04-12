"""
Experiment 1.15b: Matched-Starting-Fitness Transfer.

Follow-up to 1.15. The AUC reanalysis showed that Pareto populations
inherit elevated starting fitness on novel targets via partial-credit
scoring of preserved scaffolds. To disambiguate "inherited scaffold
inventory" from "starting-position advantage," this experiment
constructs subpopulations with matched *novel-target* starting
fitness across the three conditions, then runs the same assay.

Design:
  1. Re-run Phase 1 of 1.15 with the same seeds to recover gen 300
     snapshot genotypes (deterministic under seed).
  2. For each condition, pool all genotypes across seeds.
  3. Score each pooled genotype on the novel target (T_far) in its
     *unadapted* state (gen-0 fitness).
  4. Select a fitness band [f_low, f_high] that is populated in all
     three conditions.
  5. From each condition, sample matched subpopulations (size =
     pop_size) whose members all lie in the fitness band.
  6. Run the assay from each matched subpop for N_ASSAY_GENS gens
     with continuous selection only, no motif insertion. Multiple
     independent assay seeds per condition.
  7. Report ceiling access (≥0.8 hit rate), endpoint distributions,
     and AUC per condition.

Interpretation:
  - If Pareto matched subpops still show ≥0.8 ceiling hits and
    continuous-selection matched subpops do not: the structural
    content of preserved scaffolds contributes to transfer beyond
    the baseline advantage.
  - If ceiling-access rates equalize after matching: the 1.15
    transfer effect is dominated by inherited starting fitness,
    and preservation should be framed as a baseline-advantage
    mechanism rather than a latent-capacity mechanism.
"""

import json
import random
import time
import statistics
from collections import Counter
from pathlib import Path

from folding_evolution.individual import Individual
from folding_evolution.operators import crossover, mutate
from folding_evolution.phenotype import develop, develop_batch
from folding_evolution.dynamics import _develop_and_score_vm, _develop_population
from folding_evolution.selection import tournament_select

try:
    from _folding_rust import (
        RustContexts as _RustContexts,
        RustTargetOutputs as _RustTargetOutputs,
    )
    _USE_RUST_VM = True
except ImportError:
    _USE_RUST_VM = False

from exp_archive_reinjection import scaffold_stage, make_contexts
from exp_endogenous_scaffold import (
    structural_pattern_score, PRICE_MOTIFS,
)
from exp_cryptic_variation import (
    train_with_snapshots, PRICE_200_TARGETS, T_FAR_TARGETS, T_NEAR_TARGETS,
)


# ---------------------------------------------------------------------------
# Scoring a set of genotypes against a target, no adaptation
# ---------------------------------------------------------------------------

def score_genotypes(genotypes, contexts, targets):
    """Return a list of fitness scores (one per genotype) on the given
    target in the unadapted state."""
    pop = [Individual(genotype=g) for g in genotypes]
    if _USE_RUST_VM:
        rust_ctx = _RustContexts(contexts)
        target_outputs = [[t(ctx) for ctx in contexts] for t in targets]
        rust_targets = _RustTargetOutputs(target_outputs)
        _develop_and_score_vm(pop, rust_ctx, rust_targets)
    else:
        _develop_population(pop, develop, use_batch=True)
    return [ind.fitness for ind in pop]


# ---------------------------------------------------------------------------
# Assay — same as 1.15, parameterized
# ---------------------------------------------------------------------------

def assay(starting_genotypes, assay_gens, contexts, novel_targets, seed):
    rng = random.Random(seed)
    pop_size = len(starting_genotypes)
    population = [Individual(genotype=g) for g in starting_genotypes]

    rust_ctx = None
    rust_targets = None
    if _USE_RUST_VM:
        rust_ctx = _RustContexts(contexts)
        target_outputs = [[t(ctx) for ctx in contexts] for t in novel_targets]
        rust_targets = _RustTargetOutputs(target_outputs)

    best_so_far = 0.0
    traj = []
    for gen in range(assay_gens + 1):
        if _USE_RUST_VM:
            _develop_and_score_vm(population, rust_ctx, rust_targets)
        else:
            _develop_population(population, develop, use_batch=True)
        best = max(ind.fitness for ind in population)
        if best > best_so_far:
            best_so_far = best
        traj.append(best_so_far)

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
                child_geno = mutate(parent.genotype, rng)
            children.append(Individual(genotype=child_geno))

        if _USE_RUST_VM:
            _develop_and_score_vm(children, rust_ctx, rust_targets)
        else:
            _develop_population(children, develop, use_batch=True)

        combined = population + children
        combined.sort(key=lambda ind: ind.fitness, reverse=True)
        population = [Individual(genotype=i.genotype) for i in combined[:pop_size]]

    return {
        "final_best": best_so_far,
        "best_trajectory": traj,
    }


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def phase1_recover_snapshots(n_seeds, pop_size, genotype_length,
                              train_gens, snapshot_gen):
    """Re-run training to recover snapshot genotypes (deterministic on seed).
    Returns: dict condition -> list of genotypes (pooled across seeds)."""
    contexts = make_contexts()
    price_targets = [tfn for _, tfn in PRICE_200_TARGETS]
    conditions = [
        ("A_continuous", "select"),
        ("B_scaffold", "scaffold"),
        ("C_structural", "structural"),
    ]

    pooled = {cond: [] for cond, _ in conditions}
    for cond, objective in conditions:
        print(f"  Phase 1 recover: {cond}")
        for seed in range(n_seeds):
            t0 = time.time()
            snapshots, _ = train_with_snapshots(
                pop_size, genotype_length, train_gens, [snapshot_gen],
                contexts, price_targets, seed, objective, PRICE_MOTIFS,
            )
            pooled[cond].extend(snapshots[snapshot_gen])
            print(f"    seed {seed}: {time.time()-t0:.1f}s, pool size {len(pooled[cond])}")

    return pooled


def build_matched_subpop(pooled_genos, fitness_scores, band, target_size, rng):
    """Select up to target_size genotypes from the pool whose fitness lies
    in the band [f_low, f_high]. If fewer available, sample with replacement."""
    f_low, f_high = band
    in_band = [g for g, f in zip(pooled_genos, fitness_scores)
               if f_low <= f <= f_high]
    if not in_band:
        return None
    if len(in_band) >= target_size:
        return rng.sample(in_band, target_size)
    return rng.choices(in_band, k=target_size)


def summarize_assays(assay_results, thresholds=(0.5, 0.6, 0.7, 0.8, 0.9)):
    """Given a list of assay results for one condition, compute summary stats."""
    finals = [r["final_best"] for r in assay_results]
    n = len(finals)
    out = {
        "n_runs": n,
        "mean_final": sum(finals) / n,
        "median_final": statistics.median(finals),
        "hits": {t: sum(1 for f in finals if f >= t) for t in thresholds},
        "finals": sorted(finals),
    }
    if assay_results:
        traj_len = len(assay_results[0]["best_trajectory"])
        auc_vals = [sum(r["best_trajectory"]) / traj_len for r in assay_results]
        out["mean_auc"] = sum(auc_vals) / n
    return out


def main(n_seeds=15, snapshot_gen=300, assay_gens=60, n_assay_runs=30,
         bands_to_try=None, out_name="matched_fitness"):
    contexts = make_contexts()

    print("=" * 78)
    print("Experiment 1.15b: Matched-Starting-Fitness Transfer")
    print(f"n_seeds={n_seeds}, snap_gen={snapshot_gen}, "
          f"assay_gens={assay_gens}, n_assay_runs={n_assay_runs}")
    print("=" * 78)

    # Phase 1: recover snapshot genotypes
    print("\nPhase 1 — recover snapshot genotypes via deterministic re-run\n")
    pooled = phase1_recover_snapshots(
        n_seeds, pop_size=100, genotype_length=100,
        train_gens=snapshot_gen, snapshot_gen=snapshot_gen,
    )

    # Score on T_far (primary novel target for matched analysis — it's where
    # 1.15 showed the cleanest ceiling-access signal)
    print("\nPhase 1b — scoring snapshot genotypes on T_far in unadapted state\n")
    t_far_targets = [tfn for _, tfn in T_FAR_TARGETS]
    t_far_fitness = {}
    for cond, genos in pooled.items():
        t_far_fitness[cond] = score_genotypes(genos, contexts, t_far_targets)
        fits = t_far_fitness[cond]
        nonzero = [f for f in fits if f > 0]
        print(f"  {cond}: n={len(fits)}, "
              f"nonzero={len(nonzero)}, "
              f"mean={sum(nonzero)/len(nonzero) if nonzero else 0:.3f}, "
              f"max={max(fits):.3f}, "
              f"quantiles = "
              f"25%={sorted(fits)[len(fits)//4]:.3f} "
              f"50%={sorted(fits)[len(fits)//2]:.3f} "
              f"75%={sorted(fits)[3*len(fits)//4]:.3f}")

    # Report distribution overlap — which bands have all three conditions
    print("\n  Fitness band populations:")
    band_edges = [0.0, 0.2, 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
    header = "    band".ljust(14)
    for cond in ["A_continuous", "B_scaffold", "C_structural"]:
        header += f"{cond:<15}"
    print(header)
    for lo, hi in zip(band_edges, band_edges[1:]):
        row = f"    [{lo:.2f}, {hi:.2f})".ljust(14)
        for cond in ["A_continuous", "B_scaffold", "C_structural"]:
            n_in = sum(1 for f in t_far_fitness[cond] if lo <= f < hi)
            row += f"{n_in:<15}"
        print(row)

    # Phase 2: matched-fitness assays
    if bands_to_try is None:
        # Pick bands where all three conditions have >= 20 individuals
        bands_to_try = [(0.50, 0.60), (0.45, 0.55), (0.55, 0.65)]

    print(f"\n{'=' * 78}")
    print(f"Phase 2 — matched-fitness transfer assays")
    print(f"Target novel task: T_far (filter-amount-300), assay_gens={assay_gens}")
    print(f"{'=' * 78}")

    all_results = {}
    rng = random.Random(42)
    for band in bands_to_try:
        band_key = f"band_{band[0]:.2f}_{band[1]:.2f}"
        print(f"\n--- Band {band} ---")
        band_results = {}
        viable = True
        for cond in ["A_continuous", "B_scaffold", "C_structural"]:
            available = sum(1 for f in t_far_fitness[cond]
                           if band[0] <= f <= band[1])
            print(f"  {cond}: {available} individuals in band")
            if available < 20:
                print(f"  SKIP band (too few individuals in {cond})")
                viable = False
                break
        if not viable:
            continue

        for cond in ["A_continuous", "B_scaffold", "C_structural"]:
            results = []
            t0 = time.time()
            for assay_seed in range(n_assay_runs):
                subpop = build_matched_subpop(
                    pooled[cond], t_far_fitness[cond], band, 100, rng)
                r = assay(subpop, assay_gens, contexts, t_far_targets,
                          assay_seed + 1000)
                results.append(r)
            elapsed = time.time() - t0
            summary = summarize_assays(results)
            band_results[cond] = summary
            print(f"  {cond} ({elapsed:.1f}s): "
                  f"mean={summary['mean_final']:.3f}, "
                  f"median={summary['median_final']:.3f}, "
                  f"≥0.6={summary['hits'][0.6]}/{n_assay_runs}, "
                  f"≥0.7={summary['hits'][0.7]}/{n_assay_runs}, "
                  f"≥0.8={summary['hits'][0.8]}/{n_assay_runs}")
            print(f"    endpoints: {summary['finals']}")
        all_results[band_key] = band_results

    # Save
    out_dir = Path(__file__).parent / "output" / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "matched_fitness_results.json", "w") as f:
        json.dump({
            "params": {
                "n_seeds": n_seeds, "snapshot_gen": snapshot_gen,
                "assay_gens": assay_gens, "n_assay_runs": n_assay_runs,
                "bands_to_try": bands_to_try,
            },
            "fitness_distributions": {
                cond: sorted(t_far_fitness[cond])
                for cond in t_far_fitness
            },
            "results": all_results,
        }, f, indent=2)

    print(f"\nResults saved to {out_dir}")
    return all_results


if __name__ == "__main__":
    main()
