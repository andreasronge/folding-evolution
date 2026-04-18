#!/usr/bin/env python3
"""§v2.4-proxy-5a-followup-mid-bp: plateau-edge population inspection.

Pre-registration: Plans/prereg_v2-4-proxy-5a-followup-mid-bp.md
Decision rule (PLATEAU-MID row): "Inspect plateau-edge populations
genotype-by-genotype (zero-compute per principle 3) to identify mechanism
shift. Draft a narrowed follow-up prereg based on inspection findings."

Two candidate mechanisms compete in the bond_protection_ratio axis:
    (1) cloud-destabilisation — rising bp erodes the wide BP_TOPK solver
        neutral network, scattering the population into proxy-basin noise;
    (2) cliff-flattening — rising bp suppresses mutation in bonded cells,
        clustering the population near canonical (Hamming ≤ 2 shoulder).

Under PLATEAU-MID the R_fit_999 profile is non-monotone: 0.60→0.65→0.70
falls then 0.70→0.75 recovers then 0.75→0.85 collapses. Two-mechanism
reading: one mechanism dominates low-bp, the other dominates high-bp,
and bp=0.75 sits near the crossover with a transient recovery.

This script compares three bp pairs across two sweep directories:
    A. bp=0.60 (mid-bp, gentle decay)     vs bp=0.70 (5a, local minimum)
    B. bp=0.70 (5a, dip)                   vs bp=0.75 (mid-bp, recovery)  ← key
    C. bp=0.85 (mid-bp, collapse)         vs bp=0.90 (5a, floor)

For each pair, computes attractor coherence (Axis A, reused from
inspect_bp9_population) and Hamming-shoulder presence (Axis B, also
reused), then classifies the pair as showing cloud-destabilisation,
cliff-flattening, both, or neither. The three-pair profile answers the
mechanism-crossover question.

METRIC_DEFINITIONS (principle 27; metrics reused from
analyze_retention.py and inspect_bp9_population.py are cited by their
existing names — this module adds one new derived metric):
    "pair_attractor_coherence": "For each bp cell in a pair, compute
        attractor-category verdict (SINGLE / MULTI / DISPERSED) via
        inspect_bp9_population.classify_attractor on the population
        pooled across all seeds with final-individual fitness >= 0.9.
        The pair's coherence shift is (cell_A_verdict, cell_B_verdict)."
    "pair_hamming_shoulder_shift": "For each bp cell in a pair, compute
        the fraction of final-population tapes within raw-tape Hamming
        distance <= 2 of canonical. The pair's shoulder shift is the
        ratio cell_B_frac / cell_A_frac. Ratio > 1.5 = shoulder
        emerges (cliff-flattening); ratio < 1/1.5 = shoulder dissolves
        (cloud-destabilisation); ratio in [1/1.5, 1.5] = stable."
    "pair_mechanism_verdict": "Composite label derived from the pair's
        attractor shift and shoulder shift, per the code's classification
        table (see summarise_pair). Values and their explicit criteria:
        CLIFF-FLATTENING = shoulder EMERGES AND attractor shift ∈ {TIGHTENS,
        SAME}; CLOUD-DESTABILISATION = shoulder DISSOLVES AND attractor
        shift ∈ {LOOSENS, SAME} (the SAME branch accepts the case where
        both cells are already DISPERSED and the shoulder dissolves
        further — cloud stretches in raw-tape Hamming without an attractor-
        category transition); STABLE = shoulder STABLE AND attractor
        SAME; MIXED = any other combination. Readers cross-checking
        against §v2.4-proxy-5a-followup-mid-bp's Pair B verdict should
        note: Pair B has attractor SAME (both DISPERSED) AND shoulder
        DISSOLVES, so it classifies as CLOUD-DESTABILISATION via the
        SAME-branch extension, not via the LOOSENS branch. The narrower
        reading (require LOOSENS strictly) would classify Pair B as
        MIXED instead — the code commits to the broader reading for
        cloud-stretch-within-DISPERSED cases, and the chronicle cites
        this definition verbatim."

Usage:
    python experiments/chem_tape/inspect_plateau_edge.py \\
        --sweep-5a experiments/output/2026-04-17/v2_4_proxy5a_bp_sweep \\
        --sweep-mid experiments/output/2026-04-18/v2_4_proxy5a_mid_bp

Outputs:
    - JSON report to stdout (full machine-readable report)
    - Human-readable verdict summary to stderr
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "experiments" / "chem_tape"))

from analyze_retention import CANONICAL_AND_BODY_HEX, hex_to_tape  # noqa: E402
from inspect_bp9_population import (  # noqa: E402
    classify_attractor,
    fitness_stats,
    hamming_hist,
    levenshtein_hist,
    load_condition,
    pool_genotypes,
    CANONICAL_ACTIVE,
)

CANONICAL_TAPE = hex_to_tape(CANONICAL_AND_BODY_HEX)

# Plateau-edge pairs pre-committed in the decision rule.
# Each pair: (cell_A_bp, cell_A_sweep_key, cell_B_bp, cell_B_sweep_key).
PAIRS = [
    ("A", 0.60, "mid", 0.70, "5a", "low-bp gentle decay vs 5a dip"),
    ("B", 0.70, "5a", 0.75, "mid", "5a dip vs mid-bp recovery (KEY)"),
    ("C", 0.85, "mid", 0.90, "5a", "mid-bp collapse vs 5a floor"),
]

SHOULDER_THRESHOLD = 1.5  # ratio multiplier for shoulder emergence
SHOULDER_DISSOLVE_THRESHOLD = 1.0 / 1.5  # < this = shoulder dissolves


def summarise_pair(
    pair_id: str,
    label: str,
    runs_a: list[dict],
    runs_b: list[dict],
    bp_a: float,
    bp_b: float,
) -> dict:
    """Compute the mechanism-verdict summary for one bp pair."""
    if not runs_a or not runs_b:
        return {
            "pair_id": pair_id,
            "label": label,
            "bp_a": bp_a,
            "bp_b": bp_b,
            "error": "missing runs",
            "n_a": len(runs_a),
            "n_b": len(runs_b),
        }

    # --- Attractor classification per cell ---
    attr_a = classify_attractor(runs_a)
    attr_b = classify_attractor(runs_b)

    # --- Hamming-shoulder per cell (raw-tape distance to canonical) ---
    genos_a = pool_genotypes(runs_a)
    genos_b = pool_genotypes(runs_b)
    hamm_a = hamming_hist(genos_a, CANONICAL_TAPE)
    hamm_b = hamming_hist(genos_b, CANONICAL_TAPE)
    lev_a = levenshtein_hist(genos_a, CANONICAL_ACTIVE)
    lev_b = levenshtein_hist(genos_b, CANONICAL_ACTIVE)

    frac_le2_a = sum(hamm_a.get(str(d), 0.0) for d in [0, 1, 2])
    frac_le2_b = sum(hamm_b.get(str(d), 0.0) for d in [0, 1, 2])
    ratio = frac_le2_b / frac_le2_a if frac_le2_a > 1e-9 else 0.0

    if ratio > SHOULDER_THRESHOLD:
        shoulder_shift = "EMERGES"  # cliff-flattening candidate
    elif ratio < SHOULDER_DISSOLVE_THRESHOLD and frac_le2_a > 1e-9:
        shoulder_shift = "DISSOLVES"  # cloud-destabilisation candidate
    else:
        shoulder_shift = "STABLE"

    # --- Attractor shift: SINGLE → DISPERSED is destabilisation etc. ---
    attractor_levels = {"SINGLE-ATTRACTOR": 3, "MULTI-ATTRACTOR": 2, "DISPERSED": 1}
    va = attractor_levels.get(attr_a["verdict_axis_A"], 0)
    vb = attractor_levels.get(attr_b["verdict_axis_A"], 0)
    if vb > va:
        attractor_shift = "TIGHTENS"  # cliff-flattening candidate
    elif vb < va:
        attractor_shift = "LOOSENS"  # cloud-destabilisation candidate
    else:
        attractor_shift = "SAME"

    # --- Composite mechanism verdict for the pair ---
    if shoulder_shift == "EMERGES" and attractor_shift in ("TIGHTENS", "SAME"):
        verdict = "CLIFF-FLATTENING"
    elif shoulder_shift == "DISSOLVES" and attractor_shift in ("LOOSENS", "SAME"):
        verdict = "CLOUD-DESTABILISATION"
    elif shoulder_shift == "STABLE" and attractor_shift == "SAME":
        verdict = "STABLE"
    else:
        verdict = "MIXED"

    # --- Fitness-distribution aggregates for caveat tracking ---
    fit_a = fitness_stats(runs_a)
    fit_b = fitness_stats(runs_b)
    mean_frac_999_a = float(np.mean([r["frac_ge_999"] for r in fit_a]))
    mean_frac_999_b = float(np.mean([r["frac_ge_999"] for r in fit_b]))

    return {
        "pair_id": pair_id,
        "label": label,
        "bp_a": bp_a,
        "bp_b": bp_b,
        "n_a": len(runs_a),
        "n_b": len(runs_b),
        "attractor_a": {
            "verdict": attr_a["verdict_axis_A"],
            "dominant_hex": attr_a["dominant_hex"],
            "dominant_frac": attr_a["dominant_frac"],
            "unique_hex_count": attr_a["unique_hex_count"],
        },
        "attractor_b": {
            "verdict": attr_b["verdict_axis_A"],
            "dominant_hex": attr_b["dominant_hex"],
            "dominant_frac": attr_b["dominant_frac"],
            "unique_hex_count": attr_b["unique_hex_count"],
        },
        "attractor_shift": attractor_shift,
        "hamming_a": hamm_a,
        "hamming_b": hamm_b,
        "frac_le2_a": frac_le2_a,
        "frac_le2_b": frac_le2_b,
        "shoulder_ratio": ratio,
        "shoulder_shift": shoulder_shift,
        "levenshtein_a": lev_a,
        "levenshtein_b": lev_b,
        "r_fit_999_a": mean_frac_999_a,
        "r_fit_999_b": mean_frac_999_b,
        "pair_mechanism_verdict": verdict,
    }


def cross_pair_profile(pair_results: list[dict]) -> dict:
    """Combine the three pair verdicts into a crossover-profile classification."""
    verdicts = {p["pair_id"]: p.get("pair_mechanism_verdict", "ERROR")
                for p in pair_results}
    # Expected signatures per decision rule:
    #   A=CLOUD-DEST, B=CLIFF-FLAT, C=CLIFF-FLAT  → clean crossover at bp=0.75
    #   A=CLOUD-DEST, B=MIXED,      C=CLOUD-DEST   → single-mechanism gradient
    #   all same                                    → no crossover; R_fit non-monotonicity is noise
    a, b, c = verdicts.get("A"), verdicts.get("B"), verdicts.get("C")

    if (a in ("CLOUD-DESTABILISATION", "MIXED") and
            b == "CLIFF-FLATTENING" and
            c in ("CLIFF-FLATTENING", "MIXED")):
        profile = "MECHANISM-CROSSOVER-AT-0.75"
    elif a == b == c:
        profile = f"UNIFORM-{a}"
    elif c == "CLOUD-DESTABILISATION" and a in (
        "CLOUD-DESTABILISATION",
        "STABLE",
    ):
        profile = "MONOTONE-CLOUD-DESTABILISATION-WITH-NOISE-AT-B"
    else:
        profile = "HETEROGENEOUS"
    return {"verdicts": verdicts, "crossover_profile": profile}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sweep-5a", required=True, type=Path,
                        help="Path to v2_4_proxy5a_bp_sweep (bp∈{0.5,0.7,0.9})")
    parser.add_argument("--sweep-mid", required=True, type=Path,
                        help="Path to v2_4_proxy5a_mid_bp (bp∈{0.60,0.65,0.75,0.85})")
    args = parser.parse_args()

    if not args.sweep_5a.exists():
        print(f"ERROR: sweep-5a missing: {args.sweep_5a}", file=sys.stderr)
        return 2
    if not args.sweep_mid.exists():
        print(f"ERROR: sweep-mid missing: {args.sweep_mid}", file=sys.stderr)
        return 2

    sweeps = {"5a": args.sweep_5a, "mid": args.sweep_mid}

    def load(bp: float, key: str) -> list[dict]:
        return load_condition(sweeps[key], bp_target=bp, sf_target=0.01)

    # Load every bp cell we'll need; cache.
    needed = {(0.60, "mid"), (0.65, "mid"), (0.70, "5a"), (0.75, "mid"),
              (0.85, "mid"), (0.90, "5a"), (0.50, "5a")}
    cache: dict[tuple[float, str], list[dict]] = {}
    for bp, key in sorted(needed):
        print(f"Loading bp={bp} sf=0.01 from {key} sweep…", file=sys.stderr)
        runs = load(bp, key)
        cache[(bp, key)] = runs
        if not runs:
            print(f"  WARNING: no runs found for bp={bp} in {key} sweep",
                  file=sys.stderr)

    # Compute each pair.
    pair_results: list[dict] = []
    for pid, bp_a, key_a, bp_b, key_b, label in PAIRS:
        print(
            f"\nPair {pid}: bp={bp_a}({key_a}) vs bp={bp_b}({key_b}) — {label}",
            file=sys.stderr,
        )
        result = summarise_pair(
            pid, label,
            cache[(bp_a, key_a)], cache[(bp_b, key_b)],
            bp_a, bp_b,
        )
        pair_results.append(result)
        if "error" in result:
            print(f"  ERROR: {result['error']}", file=sys.stderr)
            continue
        print(
            f"  R_fit_999: {result['r_fit_999_a']:.3f} → {result['r_fit_999_b']:.3f}\n"
            f"  Attractor: {result['attractor_a']['verdict']} "
            f"→ {result['attractor_b']['verdict']} "
            f"({result['attractor_shift']})\n"
            f"  Hamming≤2: {result['frac_le2_a']:.4f} → "
            f"{result['frac_le2_b']:.4f} "
            f"(ratio={result['shoulder_ratio']:.2f}x, "
            f"{result['shoulder_shift']})\n"
            f"  → PAIR VERDICT: {result['pair_mechanism_verdict']}",
            file=sys.stderr,
        )

    # Cross-pair profile.
    profile = cross_pair_profile(pair_results)
    print(f"\n=== CROSSOVER PROFILE: {profile['crossover_profile']} ===",
          file=sys.stderr)
    for pid, v in profile["verdicts"].items():
        print(f"  Pair {pid}: {v}", file=sys.stderr)

    report = {
        "experiment": "v2.4-proxy-5a-followup-mid-bp.plateau-edge-inspection",
        "sweep_5a": str(args.sweep_5a),
        "sweep_mid": str(args.sweep_mid),
        "pairs": pair_results,
        "crossover_profile": profile,
    }
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
