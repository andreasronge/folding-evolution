"""
Experiment 1.15c: Within-family robustness check.

Cheap sanity check after the cross-family reachability test failed.
Tests whether the 1.15 / 1.15b structural-generalization claim holds
on two additional within-family transfer targets, not just the
threshold-shift (T_near) and field+data-shift (T_far) pair.

Within-family variations tested:
  - T_comp: comparator swap (> → <)
       `(count (filter (fn x (< (get x :price) 500)) data/products))`
  - T_wrap: wrapper swap (count → first)
       `(first (filter (fn x (> (get x :price) 300)) data/products))`

Design mirrors 1.15 / 1.15b exactly so results are directly comparable:
  - Train 300 gens on filter-price-200
  - Snapshot at gen 300 only
  - 10 seeds per condition (cheap; we already have 15-seed data for
    the same Phase 1 in 1.15 — this is a robustness probe, not a
    primary result)
  - 40-gen assay, continuous selection only, no motif insertion
  - Single-target novel assays (same as 1.15b)

Primary readouts (same as 1.15b, primary to secondary):
  - Starting-fitness distribution per condition (non-overlap test)
  - Endpoint ceiling access hit rates
  - Endpoint phenotype diversity (distinct program sources)

No claim of faster adaptation. No cryptic variation language.
"""

import json
import random
import statistics
import time
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

from exp_archive_reinjection import make_contexts
from exp_endogenous_scaffold import PRICE_MOTIFS
from exp_cryptic_variation import train_with_snapshots, PRICE_200_TARGETS
from exp_matched_fitness import assay, score_genotypes


T_COMP_TARGETS = [
    ("count(filter(price<500, products))",
     lambda ctx: len([p for p in ctx["products"] if p["price"] < 500])),
]

T_WRAP_TARGETS = [
    ("first(filter(price>300, products))",
     lambda ctx: next((p for p in ctx["products"] if p["price"] > 300), None)),
]


def main(n_seeds=10, pop_size=100, genotype_length=100,
         train_gens=300, assay_gens=40):
    contexts = make_contexts()
    price_train_targets = [tfn for _, tfn in PRICE_200_TARGETS]
    conditions = [
        ("A_continuous", "select"),
        ("B_scaffold", "scaffold"),
        ("C_structural", "structural"),
    ]

    novel_targets = {
        "T_comp_priceLT500": [tfn for _, tfn in T_COMP_TARGETS],
        "T_wrap_firstGT300": [tfn for _, tfn in T_WRAP_TARGETS],
    }

    print("=" * 78)
    print("Experiment 1.15c: Within-family robustness check")
    print(f"n_seeds={n_seeds}, train_gens={train_gens}, assay_gens={assay_gens}")
    print("=" * 78)

    snapshot_gen = train_gens
    pooled = {cond: [] for cond, _ in conditions}

    print("\nPhase 1 — training\n")
    for cond, objective in conditions:
        print(f"  {cond}")
        for seed in range(n_seeds):
            t0 = time.time()
            snaps, _ = train_with_snapshots(
                pop_size, genotype_length, train_gens, [snapshot_gen],
                contexts, price_train_targets, seed, objective, PRICE_MOTIFS,
            )
            pooled[cond].extend(snaps[snapshot_gen])
            print(f"    seed {seed}: {time.time()-t0:.1f}s")

    # Starting-fitness distributions on each novel target
    print("\nPhase 1b — scoring on novel targets (gen-0)\n")
    start_fits = {}
    for target_name, targets in novel_targets.items():
        start_fits[target_name] = {}
        print(f"  Target: {target_name}")
        for cond in ["A_continuous", "B_scaffold", "C_structural"]:
            fits = score_genotypes(pooled[cond], contexts, targets)
            start_fits[target_name][cond] = fits
            unique = sorted(set(fits))
            print(f"    {cond}: n={len(fits)}, "
                  f"unique vals={len(unique)}, "
                  f"min={min(fits):.3f}, max={max(fits):.3f}, "
                  f"mean={sum(fits)/len(fits):.3f}")
            if len(unique) <= 5:
                print(f"      (values = {[f'{v:.3f}' for v in unique]})")

        # Histogram
        print(f"    Starting-fitness histogram:")
        band_edges = [0.0, 0.2, 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.9]
        header = "      band".ljust(16)
        for cond in ["A_continuous", "B_scaffold", "C_structural"]:
            header += f"{cond:<14}"
        print(header)
        for lo, hi in zip(band_edges, band_edges[1:]):
            row = f"      [{lo:.2f},{hi:.2f})".ljust(16)
            for cond in ["A_continuous", "B_scaffold", "C_structural"]:
                n_in = sum(1 for f in start_fits[target_name][cond] if lo <= f < hi)
                row += f"{n_in:<14}"
            print(row)

    # Phase 2: standard per-seed assays (not matched-fitness; just
    # the 1.15-style "how does the natural starting population fare")
    print("\n" + "=" * 78)
    print("Phase 2 — per-seed transfer assays (each seed's own snapshot)")
    print("=" * 78)

    results = {cond: {} for cond, _ in conditions}
    # Rebuild per-seed snapshots from the pool index
    for cond_idx, (cond, _) in enumerate(conditions):
        per_seed_snaps = [pooled[cond][i*pop_size:(i+1)*pop_size]
                          for i in range(n_seeds)]
        for target_name, targets in novel_targets.items():
            print(f"\n  {cond} on {target_name}")
            seed_results = []
            t0 = time.time()
            for seed in range(n_seeds):
                r = assay(per_seed_snaps[seed], assay_gens, contexts,
                          targets, seed + 7000)
                seed_results.append(r)
            elapsed = time.time() - t0
            finals = [r["final_best"] for r in seed_results]
            hits_06 = sum(1 for f in finals if f >= 0.6)
            hits_07 = sum(1 for f in finals if f >= 0.7)
            hits_08 = sum(1 for f in finals if f >= 0.8)
            print(f"    ({elapsed:.1f}s) finals={sorted(finals)}, "
                  f"≥0.6={hits_06}/{n_seeds}, ≥0.7={hits_07}/{n_seeds}, "
                  f"≥0.8={hits_08}/{n_seeds}")
            results[cond][target_name] = {
                "finals": sorted(finals),
                "hits_0.6": hits_06,
                "hits_0.7": hits_07,
                "hits_0.8": hits_08,
                "mean_final": sum(finals) / n_seeds,
                "median_final": statistics.median(finals),
            }

    # Summary table
    print("\n" + "=" * 78)
    print("SUMMARY — Within-family robustness")
    print("=" * 78)
    for target_name in novel_targets:
        print(f"\n{target_name}:")
        print(f"  {'Cond':<16}{'median_final':<14}{'mean_final':<14}"
              f"{'≥0.6':<8}{'≥0.7':<8}{'≥0.8':<8}")
        for cond in ["A_continuous", "B_scaffold", "C_structural"]:
            r = results[cond][target_name]
            print(f"  {cond:<16}{r['median_final']:<14.3f}{r['mean_final']:<14.3f}"
                  f"{r['hits_0.6']}/{n_seeds}    "
                  f"{r['hits_0.7']}/{n_seeds}    "
                  f"{r['hits_0.8']}/{n_seeds}")

    # Save
    out_dir = Path(__file__).parent / "output" / "within_family_check"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_data = {
        "params": {
            "n_seeds": n_seeds, "train_gens": train_gens,
            "assay_gens": assay_gens, "pop_size": pop_size,
        },
        "starting_fitness_distributions": {
            target: {cond: sorted(fits)
                     for cond, fits in cond_dict.items()}
            for target, cond_dict in start_fits.items()
        },
        "assay_results": results,
    }
    with open(out_dir / "within_family_results.json", "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\nResults saved to {out_dir}")


if __name__ == "__main__":
    main()
