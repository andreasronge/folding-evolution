#!/usr/bin/env python3
"""§v2.4-proxy-5a-followup-bp-inspection: zero-compute population inspection.

Pre-registration: Plans/prereg_v2-4-proxy-5a-followup-bp-inspection.md

Reads the final_population.npz files from the §v2.4-proxy-5a sweep directory
for bp=0.9 × sf=0.01 (20 runs) and bp=0.5 × sf=0.01 (20 runs, baseline),
then answers the primary inspection question:

    Is the bp=0.9 R_fit collapse due to:
    (a) convergence to a single alternative attractor,
    (b) fragmentation across multiple attractors, or
    (c) dispersed proxy-basin noise?

METRIC_DEFINITIONS (principle 27):
    "best_of_run_hex": "Hex string of the best-of-run genotype from
        result.json:best_genotype_hex. Used to confirm canonical retention
        at the best-of-run layer per §v2.4-proxy-5a check_canonical.py."
    "fitness_dist_stats": "Per-seed statistics of the 1024-individual fitness
        array from final_population.npz:fitnesses (float32): mean, std, and
        fraction ≥ threshold at thresholds {0.999, 0.9, 0.5}."
    "modal_noncanonicalhex_fit09": "For each seed, the most common genotype
        hex (bytes.hex()) in the population slice filtered to fitness ≥ 0.9,
        excluding canonical. Used for attractor-category classification."
    "unique_hex_count_fit09": "Count of distinct genotype hexes in the
        fitness ≥ 0.9 slice of each seed's final population, excluding
        canonical. Pooled across all seeds to determine SINGLE/MULTI/DISPERSED."
    "active_token_histogram": "Count of each token ID across all genotypes
        in the condition, computed from the active-program view (non-NOP,
        non-separator tokens in tape order via analyze_retention.extract_active,
        alphabet=v2_probe)."
    "rawtape_hamming_hist": "Histogram of per-individual Hamming distances
        (XOR sum on uint8 raw tape, compared to canonical 32-token tape) at
        levels d ∈ {0,1,2,3,4,5,>=6}, reported as fraction of total population."
    "activetape_levenshtein_hist": "Histogram of per-individual Levenshtein
        distances on the active-program token sequence (via
        analyze_retention.levenshtein, capped at 8) compared to canonical's
        active-program sequence, at levels d ∈ {0,1,2,3,4,5,6,7,>=8}."

Usage:
    python experiments/chem_tape/inspect_bp9_population.py <sweep-dir>

    <sweep-dir> is the absolute path to the v2_4_proxy5a_bp_sweep directory,
    e.g. experiments/output/2026-04-17/v2_4_proxy5a_bp_sweep

Outputs:
    - JSON report to stdout (machine-readable full report)
    - Summary to stderr (human-readable attractor classification + verdict)
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "experiments" / "chem_tape"))

from analyze_retention import (  # noqa: E402
    CANONICAL_AND_BODY_HEX,
    extract_active,
    levenshtein,
    hex_to_tape,
)

CANONICAL_TAPE = hex_to_tape(CANONICAL_AND_BODY_HEX)
CANONICAL_ACTIVE = extract_active(CANONICAL_TAPE, "v2_probe")
ALPHABET = "v2_probe"
HAMMING_LEVELS = [0, 1, 2, 3, 4, 5]  # ">=6" is the catch-all
LEVENSHTEIN_LEVELS = [0, 1, 2, 3, 4, 5, 6, 7]  # ">=8" is the catch-all
LEVENSHTEIN_CAP = 8


def raw_hamming(tape: np.ndarray, canonical: np.ndarray) -> int:
    """Hamming distance on raw uint8 tape (XOR → count nonzero)."""
    return int(np.count_nonzero(tape != canonical))


def hamming_hist(tapes: np.ndarray, canonical: np.ndarray) -> dict[str, float]:
    """Fraction-of-population histogram of raw-tape Hamming distances."""
    n = len(tapes)
    dists = np.count_nonzero(tapes != canonical[np.newaxis, :], axis=1)
    counts: dict[str, int] = {str(d): 0 for d in HAMMING_LEVELS}
    counts[">=6"] = 0
    for d in dists.tolist():
        key = str(d) if d <= 5 else ">=6"
        counts[key] = counts.get(key, 0) + 1
    return {k: v / n for k, v in counts.items()}


def levenshtein_hist(tapes: np.ndarray, canonical_active: tuple[int, ...]) -> dict[str, float]:
    """Fraction-of-population histogram of active-view Levenshtein distances."""
    n = len(tapes)
    counts: dict[str, int] = {str(d): 0 for d in LEVENSHTEIN_LEVELS}
    counts[f">={LEVENSHTEIN_CAP}"] = 0
    for tape in tapes:
        active = extract_active(tape, ALPHABET)
        d = levenshtein(active, canonical_active, cap=LEVENSHTEIN_CAP)
        if d >= LEVENSHTEIN_CAP:
            counts[f">={LEVENSHTEIN_CAP}"] += 1
        else:
            counts[str(d)] = counts.get(str(d), 0) + 1
    return {k: v / n for k, v in counts.items()}


def token_histogram(tapes: np.ndarray) -> dict[str, int]:
    """Aggregate active-view token counts across all tapes."""
    counts: Counter[int] = Counter()
    for tape in tapes:
        active = extract_active(tape, ALPHABET)
        counts.update(active)
    return {str(k): v for k, v in sorted(counts.items())}


def load_condition(
    sweep_dir: Path, bp_target: float, sf_target: float
) -> list[dict]:
    """Load all run dicts matching (bp, sf) from sweep_dir.

    Returns a list of dicts, one per run, with keys:
        seed, bp, sf, best_of_run_hex, genotypes (ndarray), fitnesses (ndarray)
    """
    runs = []
    for d in sorted(sweep_dir.iterdir()):
        if not d.is_dir():
            continue
        cfg_path = d / "config.yaml"
        res_path = d / "result.json"
        npz_path = d / "final_population.npz"
        if not (cfg_path.exists() and res_path.exists() and npz_path.exists()):
            continue
        cfg = yaml.safe_load(cfg_path.read_text())
        bp = float(cfg.get("bond_protection_ratio", 0.5))
        sf = float(cfg.get("seed_fraction", 0.0))
        if abs(bp - bp_target) > 0.01 or abs(sf - sf_target) > 0.001:
            continue
        res = json.loads(res_path.read_text())
        pop = np.load(str(npz_path))
        runs.append(
            {
                "run_hash": d.name,
                "seed": int(cfg.get("seed", -1)),
                "bp": bp,
                "sf": sf,
                "best_of_run_hex": res.get("best_genotype_hex", ""),
                "genotypes": pop["genotypes"],  # (1024, 32) uint8
                "fitnesses": pop["fitnesses"].astype(float),  # (1024,)
            }
        )
    runs.sort(key=lambda r: r["seed"])
    return runs


def classify_attractor(
    runs: list[dict],
    canonical_hex: str = CANONICAL_AND_BODY_HEX,
    fit_threshold: float = 0.9,
    single_attractor_min_frac: float = 0.80,
    min_occurrences_multi: int = 2,
    max_hexes_single: int = 2,
) -> dict:
    """Classify attractor regime from the final-population high-fitness slice.

    For each run, find the modal non-canonical genotype hex among individuals
    with fitness >= fit_threshold. Then pool those modal hexes across all runs
    to determine the attractor-category outcome.

    Returns a dict with:
        modal_hexes: list of (seed, modal_hex, count_in_slice, slice_size)
        hex_counter: {hex: n_seeds} across all modal hexes
        unique_hex_count: total distinct modal hexes across seeds
        dominant_hex: hex with most seed occurrences (or None)
        dominant_frac: fraction of seeds where dominant_hex is modal
        verdict_axis_A: SINGLE | MULTI | DISPERSED
    """
    modal_hexes = []
    hex_counter: Counter[str] = Counter()

    for run in runs:
        genos = run["genotypes"]
        fits = run["fitnesses"]
        mask = fits >= fit_threshold
        slice_genos = genos[mask]
        slice_size = int(mask.sum())
        if slice_size == 0:
            modal_hexes.append(
                {
                    "seed": run["seed"],
                    "modal_hex": None,
                    "count_in_slice": 0,
                    "slice_size": 0,
                }
            )
            continue
        # Count non-canonical hexes in the slice
        hex_counts: Counter[str] = Counter()
        for tape in slice_genos:
            h = tape.tobytes().hex()
            if h != canonical_hex:
                hex_counts[h] += 1
        if not hex_counts:
            # Entire fitness-≥0.9 slice is canonical
            modal_hex = None
            modal_count = 0
        else:
            modal_hex, modal_count = hex_counts.most_common(1)[0]
        modal_hexes.append(
            {
                "seed": run["seed"],
                "modal_hex": modal_hex,
                "count_in_slice": modal_count,
                "slice_size": slice_size,
            }
        )
        if modal_hex is not None:
            hex_counter[modal_hex] += 1

    n_runs = len(runs)
    unique_hex_count = len(hex_counter)
    if hex_counter:
        dominant_hex, dominant_count = hex_counter.most_common(1)[0]
        dominant_frac = dominant_count / n_runs
    else:
        dominant_hex = None
        dominant_count = 0
        dominant_frac = 0.0

    # Determine Axis A verdict
    multi_threshold = [h for h, c in hex_counter.items() if c >= min_occurrences_multi]
    if dominant_frac >= single_attractor_min_frac and unique_hex_count <= max_hexes_single:
        verdict_a = "SINGLE-ATTRACTOR"
    elif len(multi_threshold) >= 3 or (3 <= unique_hex_count <= 10):
        verdict_a = "MULTI-ATTRACTOR"
    else:
        verdict_a = "DISPERSED"

    return {
        "modal_hexes": modal_hexes,
        "hex_counter": dict(hex_counter.most_common(20)),
        "unique_hex_count": unique_hex_count,
        "dominant_hex": dominant_hex,
        "dominant_count": dominant_count,
        "dominant_frac": dominant_frac,
        "verdict_axis_A": verdict_a,
    }


def fitness_stats(runs: list[dict]) -> list[dict]:
    """Per-seed fitness distribution statistics."""
    stats = []
    for run in runs:
        fits = run["fitnesses"]
        stats.append(
            {
                "seed": run["seed"],
                "mean": float(fits.mean()),
                "std": float(fits.std()),
                "frac_ge_999": float((fits >= 0.999).mean()),
                "frac_ge_90": float((fits >= 0.9).mean()),
                "frac_ge_50": float((fits >= 0.5).mean()),
                "n": len(fits),
            }
        )
    return stats


def aggregate_fitness_stats(per_seed: list[dict]) -> dict:
    """Mean across seeds of the per-seed fitness stats."""
    keys = ["mean", "std", "frac_ge_999", "frac_ge_90", "frac_ge_50"]
    out = {}
    for k in keys:
        vals = [r[k] for r in per_seed]
        out[f"mean_{k}"] = float(np.mean(vals))
        out[f"std_{k}"] = float(np.std(vals))
    return out


def pool_genotypes(runs: list[dict]) -> np.ndarray:
    """Stack all final populations into a single (N, 32) array."""
    return np.vstack([r["genotypes"] for r in runs])


def classify_hamming_shoulder(
    hist_bp9: dict[str, float],
    hist_bp5: dict[str, float],
    shoulder_threshold: float = 1.5,
) -> dict:
    """Determine Axis B verdict: is there a Hamming ≤ 2 shoulder at bp=0.9?

    shoulder_threshold: bp=0.9 fraction must exceed bp=0.5 fraction × this
    multiplier to count as a shoulder.
    """
    frac_le2_bp9 = sum(hist_bp9.get(str(d), 0.0) for d in [0, 1, 2])
    frac_le2_bp5 = sum(hist_bp5.get(str(d), 0.0) for d in [0, 1, 2])
    ratio = frac_le2_bp9 / frac_le2_bp5 if frac_le2_bp5 > 1e-9 else 0.0
    shoulder_present = ratio > shoulder_threshold
    return {
        "frac_le2_bp9": frac_le2_bp9,
        "frac_le2_bp5": frac_le2_bp5,
        "ratio": ratio,
        "threshold": shoulder_threshold,
        "shoulder_present": shoulder_present,
        "verdict_axis_B": "SHOULDER" if shoulder_present else "NO-SHOULDER",
    }


def final_verdict(verdict_a: str, shoulder_present: bool) -> str:
    """Map (Axis A, Axis B) to prereg outcome row."""
    if verdict_a == "SINGLE-ATTRACTOR" and not shoulder_present:
        return "SINGLE-ATTRACTOR"
    if verdict_a == "SINGLE-ATTRACTOR" and shoulder_present:
        return "SINGLE-ATTRACTOR + CLIFF-PARTIAL"
    if verdict_a == "MULTI-ATTRACTOR":
        return "MULTI-ATTRACTOR"
    if verdict_a == "DISPERSED" and not shoulder_present:
        return "DISPERSED"
    if verdict_a == "DISPERSED" and shoulder_present:
        return "CLIFF-PARTIAL-ONLY"
    return "INCONCLUSIVE"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: inspect_bp9_population.py <sweep-dir>", file=sys.stderr)
        return 2

    sweep_dir = Path(sys.argv[1])
    if not sweep_dir.exists():
        print(f"sweep dir missing: {sweep_dir}", file=sys.stderr)
        return 2

    print(f"Loading bp=0.9 × sf=0.01 runs …", file=sys.stderr)
    runs_bp9 = load_condition(sweep_dir, bp_target=0.9, sf_target=0.01)
    print(f"Loading bp=0.5 × sf=0.01 runs (baseline) …", file=sys.stderr)
    runs_bp5 = load_condition(sweep_dir, bp_target=0.5, sf_target=0.01)

    if not runs_bp9:
        print("ERROR: no bp=0.9 sf=0.01 runs found", file=sys.stderr)
        return 1
    if not runs_bp5:
        print("ERROR: no bp=0.5 sf=0.01 runs found (baseline)", file=sys.stderr)
        return 1

    print(f"  bp=0.9: {len(runs_bp9)} runs | bp=0.5: {len(runs_bp5)} runs", file=sys.stderr)

    # --- 1. Best-of-run hex check ---
    bor_check_bp9 = [
        {
            "seed": r["seed"],
            "best_of_run_hex": r["best_of_run_hex"],
            "is_canonical": r["best_of_run_hex"] == CANONICAL_AND_BODY_HEX,
        }
        for r in runs_bp9
    ]
    n_canonical_bor = sum(1 for x in bor_check_bp9 if x["is_canonical"])
    print(
        f"Best-of-run canonical: {n_canonical_bor}/{len(runs_bp9)} at bp=0.9",
        file=sys.stderr,
    )

    # --- 2. Fitness distribution ---
    fit_stats_bp9 = fitness_stats(runs_bp9)
    fit_agg_bp9 = aggregate_fitness_stats(fit_stats_bp9)

    # --- 3. Attractor classification (Axis A) ---
    print("Classifying attractor regime …", file=sys.stderr)
    attractor = classify_attractor(runs_bp9)
    print(
        f"  Axis A verdict: {attractor['verdict_axis_A']} "
        f"(dominant={attractor['dominant_hex']}, "
        f"frac={attractor['dominant_frac']:.2f}, "
        f"unique_hexes={attractor['unique_hex_count']})",
        file=sys.stderr,
    )

    # --- 4. Active-view token histogram ---
    print("Computing active-view token histograms …", file=sys.stderr)
    all_genos_bp9 = pool_genotypes(runs_bp9)
    all_genos_bp5 = pool_genotypes(runs_bp5)
    tok_hist_bp9 = token_histogram(all_genos_bp9)
    tok_hist_bp5 = token_histogram(all_genos_bp5)

    # Delta: bp9 - bp5 normalised counts
    all_tokens = sorted(set(tok_hist_bp9) | set(tok_hist_bp5), key=lambda x: int(x))
    n9 = len(all_genos_bp9)
    n5 = len(all_genos_bp5)
    tok_delta = {
        t: tok_hist_bp9.get(t, 0) / n9 - tok_hist_bp5.get(t, 0) / n5
        for t in all_tokens
    }

    # --- 5. Raw-tape Hamming distance distribution (Axis B) ---
    print("Computing raw-tape Hamming distributions …", file=sys.stderr)
    hamming_bp9 = hamming_hist(all_genos_bp9, CANONICAL_TAPE)
    hamming_bp5 = hamming_hist(all_genos_bp5, CANONICAL_TAPE)
    axis_b = classify_hamming_shoulder(hamming_bp9, hamming_bp5)
    print(
        f"  Axis B verdict: {axis_b['verdict_axis_B']} "
        f"(Hamming≤2 bp9={axis_b['frac_le2_bp9']:.5f}, "
        f"bp5={axis_b['frac_le2_bp5']:.5f}, "
        f"ratio={axis_b['ratio']:.2f}x)",
        file=sys.stderr,
    )

    # --- 6. Active-view Levenshtein distribution ---
    print("Computing active-view Levenshtein distributions …", file=sys.stderr)
    lev_bp9 = levenshtein_hist(all_genos_bp9, CANONICAL_ACTIVE)
    lev_bp5 = levenshtein_hist(all_genos_bp5, CANONICAL_ACTIVE)

    # --- 7. Final outcome verdict ---
    verdict = final_verdict(attractor["verdict_axis_A"], axis_b["shoulder_present"])
    print(f"\n=== OUTCOME VERDICT: {verdict} ===", file=sys.stderr)
    print(
        f"  Attractor coherence (Axis A): {attractor['verdict_axis_A']}\n"
        f"  Hamming shoulder   (Axis B):  {axis_b['verdict_axis_B']}\n"
        f"  → Combined prereg row:        {verdict}",
        file=sys.stderr,
    )

    # --- Assemble full JSON report ---
    report = {
        "experiment": "v2.4-proxy-5a-followup-bp-inspection",
        "sweep_dir": str(sweep_dir),
        "n_runs_bp9": len(runs_bp9),
        "n_runs_bp5": len(runs_bp5),
        "best_of_run_check": {
            "bp9_canonical_count": n_canonical_bor,
            "bp9_total": len(runs_bp9),
            "per_seed": bor_check_bp9,
        },
        "fitness_distribution": {
            "per_seed": fit_stats_bp9,
            "aggregate": fit_agg_bp9,
        },
        "attractor_classification": attractor,
        "token_histogram": {
            "bp9": tok_hist_bp9,
            "bp5": tok_hist_bp5,
            "delta_normalised": tok_delta,
        },
        "rawtape_hamming": {
            "bp9": hamming_bp9,
            "bp5": hamming_bp5,
            "axis_B": axis_b,
        },
        "activetape_levenshtein": {
            "bp9": lev_bp9,
            "bp5": lev_bp5,
        },
        "verdict": {
            "axis_A": attractor["verdict_axis_A"],
            "axis_B": axis_b["verdict_axis_B"],
            "combined": verdict,
        },
    }

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
