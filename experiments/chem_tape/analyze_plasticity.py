"""Plasticity-aware analysis for §v2.5-plasticity-1a.

Reads the per-individual plastic metrics persisted into
``final_population.npz`` by ``evolve.py`` (delta_final,
test_fitness_frozen, test_fitness_plastic, train_fitness_frozen,
train_fitness_plastic, has_gt) alongside the genotype array, and
computes the prereg's outcome-grid metrics: R_fit_frozen_999,
R_fit_plastic_999, Baldwin_gap binned by Hamming-to-canonical,
Baldwin_slope + bootstrap 95% CI, and GT_bypass_fraction.

The genotype → active-view → canonical distance pipeline is shared
with ``analyze_retention`` — we import rather than duplicate.

CLI mirrors ``analyze_retention.main``:
    uv run python experiments/chem_tape/analyze_plasticity.py <sweep_name>

Emits ``plasticity.csv`` (per-run rows) and ``plasticity_summary.json``
(per-cell aggregates) in the sweep output dir.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml

# Re-use canonical/active-view/levenshtein helpers from the retention
# module so the distance definition is consistent across sibling
# analyses (principle 23).
from analyze_retention import (  # type: ignore[import-not-found]
    CANONICAL_AND_BODY_HEX,
    OUTPUT_ROOT,
    extract_active,
    hex_to_tape,
    levenshtein,
)


# --- METRIC_DEFINITIONS (principle 27) ---
#
# Verbatim citations: every entry's value matches the wording the
# §v2.5-plasticity-1a prereg quotes under "METRIC_DEFINITIONS
# additions". Preregs and chronicles should copy/paste from here.
METRIC_DEFINITIONS: dict[str, str] = {
    "F_AND_test": (
        "Fraction of the 20 seeded runs that achieve best-of-run "
        "fitness >= threshold on the held-out test examples (separate "
        "from training examples). Unit: count/20. Binary per-run "
        "measure — used for F-recovery claim only, not for Baldwin "
        "slope regression."
    ),
    "F_AND_train": (
        "Fraction of the 20 seeded runs that achieve best-of-run "
        "fitness >= threshold on training examples. Sanity check — "
        "should remain near 20/20 under seeded init."
    ),
    "test_fitness_frozen": (
        "Per-individual fraction of held-out test examples correctly "
        "classified with delta=0 (frozen, no adaptation). Continuous "
        "scalar in [0, 1]; 16-valued given 75/25 split over 64 "
        "examples (16 test examples). This is the continuous "
        "test-fitness used in the Baldwin slope regression — not the "
        "binary F_AND_test. Emitted per-individual in "
        "final_population.npz."
    ),
    "test_fitness_plastic": (
        "Per-individual fraction of held-out test examples correctly "
        "classified with delta trained on the 48 train examples and "
        "then frozen. Continuous scalar in [0, 1]. Emitted "
        "per-individual in final_population.npz."
    ),
    "delta_convergence": (
        "Per-individual final value of delta after train-phase "
        "adaptation, stored alongside frozen/plastic fitnesses in "
        "final_population.npz. Used to diagnose universal-adapter "
        "signature: if std(delta_final) is small relative to "
        "mean(delta_final) across diverse genotypes, delta converges "
        "to the same value regardless of genotype → universal-adapter "
        "flag independent of F recovery."
    ),
    "GT_bypass_fraction": (
        "Fraction of final-population individuals whose decoded "
        "program contains no GT token. These individuals have "
        "test_fitness_plastic - test_fitness_frozen = 0 trivially "
        "(plasticity cannot act on a program with no GT operation) "
        "and must be excluded from the Baldwin slope regression and "
        "reported separately. Computed by scanning the decoded token "
        "sequence for the GT opcode before any fitness evaluation. "
        "Emitted as a per-cell scalar in the analysis CSV."
    ),
    "R_fit_frozen_999": (
        "Fraction of the final population whose training fitness >= "
        "0.999 under frozen evaluation (plasticity state disabled at "
        "test time). This is the analogue of R_fit_999 under frozen "
        "semantics."
    ),
    "R_fit_plastic_999": (
        "Fraction of the final population whose training fitness >= "
        "0.999 under plastic evaluation (train-phase adaptation, then "
        "test). Captures the within-lifetime adaptation uplift."
    ),
    "Baldwin_gap": (
        "For each non-GT-bypass individual in the final population, "
        "compute test_fitness_plastic - test_fitness_frozen on "
        "held-out test examples. Aggregate as mean of that gap "
        "binned by Hamming-to-canonical-active-view distance (bins "
        "0, 1, 2, 3, >=4). Positive gap means plasticity helps; zero "
        "gap means plasticity does nothing; negative gap means "
        "plasticity hurts. GT-bypass individuals excluded; reported "
        "separately via GT_bypass_fraction."
    ),
    "Baldwin_slope": (
        "Linear regression slope of per-individual "
        "(test_fitness_plastic - test_fitness_frozen) on "
        "hamming_to_canonical, computed on non-GT-bypass individuals "
        "only. If slope is negative (closer genotypes get more "
        "plastic uplift) → Baldwin signature. If slope is zero "
        "(uniform uplift regardless of distance) → universal adapter. "
        "Bootstrap 95% CI on slope using 10 000 resamples."
    ),
    "bootstrap_ci_spec": (
        "Nonparametric bootstrap over per-seed values: 10 000 "
        "resamples with replacement via "
        "numpy.random.default_rng(seed=42); 95% CI is the [2.5%, "
        "97.5%] empirical quantile of the resampled means."
    ),
}


HAMMING_BINS = [0, 1, 2, 3]  # final bin is implicit "≥4"


def hamming_bin_label(d: int) -> str:
    return str(d) if d < 4 else ">=4"


def linreg_slope(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Return (slope, intercept) of the OLS fit of y on x.

    Uses numpy.polyfit to avoid the scipy dependency; equivalent to
    scipy.stats.linregress up to numerical precision on real-valued
    inputs. Returns (nan, nan) when the input has < 2 points or when
    x has zero variance (degenerate regression — no slope is defined).
    """
    if len(x) < 2:
        return float("nan"), float("nan")
    if np.var(x) == 0:
        return float("nan"), float("nan")
    slope, intercept = np.polyfit(x.astype(np.float64), y.astype(np.float64), 1)
    return float(slope), float(intercept)


def bootstrap_slope_ci(
    x: np.ndarray,
    y: np.ndarray,
    n_boot: int = 10_000,
    rng_seed: int = 42,
) -> tuple[float, float, float]:
    """Return (slope_mean, slope_ci_lo, slope_ci_hi) with n_boot bootstrap
    resamples (with replacement over pairs), 95% CI as [2.5%, 97.5%].

    Matches bootstrap_ci_spec — same rng seed and n_boot as
    analyze_retention so cross-analysis CIs are comparable. Returns
    (nan, nan, nan) when degenerate (< 2 points or zero x-variance).
    """
    if len(x) < 2:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(rng_seed)
    n = len(x)
    slopes = np.empty(n_boot, dtype=np.float64)
    x_f = x.astype(np.float64)
    y_f = y.astype(np.float64)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        xs = x_f[idx]
        ys = y_f[idx]
        if np.var(xs) == 0:
            slopes[i] = float("nan")
            continue
        s, _ = np.polyfit(xs, ys, 1)
        slopes[i] = s
    valid = slopes[~np.isnan(slopes)]
    if len(valid) == 0:
        return float("nan"), float("nan"), float("nan")
    return (
        float(np.mean(valid)),
        float(np.quantile(valid, 0.025)),
        float(np.quantile(valid, 0.975)),
    )


def analyze_run(
    run_dir: Path,
    canonical_tape: np.ndarray,
    alphabet: str,
) -> dict | None:
    """Compute per-run plasticity metrics. Returns None when the run
    either lacks final_population.npz or was a frozen-only run (no
    plasticity columns present — nothing to analyze here).
    """
    fp = run_dir / "final_population.npz"
    cfg_path = run_dir / "config.yaml"
    result_path = run_dir / "result.json"
    if not fp.exists() or not cfg_path.exists() or not result_path.exists():
        return None

    data = np.load(fp)
    if "delta_final" not in data.files:
        # Frozen-only run (plasticity_enabled=False); skip — this
        # analysis is only meaningful when plasticity columns exist.
        return None

    cfg = yaml.safe_load(cfg_path.read_text()) or {}
    result = json.loads(result_path.read_text())

    genotypes = data["genotypes"]            # (P, L) uint8
    train_fit_frozen = data["train_fitness_frozen"]   # (P,) float32
    train_fit_plastic = data["train_fitness_plastic"] # (P,) float32
    test_fit_frozen = data["test_fitness_frozen"]     # (P,) float32
    test_fit_plastic = data["test_fitness_plastic"]   # (P,) float32
    delta_final = data["delta_final"]                 # (P,) float32
    has_gt = data["has_gt"].astype(bool)              # (P,) bool

    P = genotypes.shape[0]
    can_active = extract_active(canonical_tape, alphabet)

    # Hamming-to-canonical as active-view Levenshtein (capped at 4 —
    # matches the prereg's {0,1,2,3,≥4} bin structure and avoids
    # computing large edit distances on drifted tapes).
    dist = np.empty(P, dtype=np.int16)
    for i in range(P):
        act = extract_active(genotypes[i], alphabet)
        dist[i] = levenshtein(act, can_active, cap=4)

    delta_fit = test_fit_plastic - test_fit_frozen  # per-individual

    # --- Cell-level scalars ---
    R_fit_frozen_999 = float(np.mean(train_fit_frozen >= 0.999))
    R_fit_plastic_999 = float(np.mean(train_fit_plastic >= 0.999))
    GT_bypass_fraction = float(1.0 - np.mean(has_gt))

    # Restrict Baldwin regression to non-GT-bypass individuals
    # (principle-correct per prereg; GT-bypass is trivially delta_fit=0
    # and would pull the slope toward zero).
    non_bypass = has_gt
    n_non_bypass = int(non_bypass.sum())

    if n_non_bypass >= 2:
        x = dist[non_bypass].astype(np.float64)
        y = delta_fit[non_bypass].astype(np.float64)
        slope, intercept = linreg_slope(x, y)
        slope_boot, slope_ci_lo, slope_ci_hi = bootstrap_slope_ci(x, y)
    else:
        slope = intercept = float("nan")
        slope_boot = slope_ci_lo = slope_ci_hi = float("nan")

    # Baldwin gap binned by Hamming (non-bypass only).
    gap_bins: dict[str, float | None] = {}
    gap_counts: dict[str, int] = {}
    for b in HAMMING_BINS:
        mask = non_bypass & (dist == b)
        gap_bins[f"Baldwin_gap_h{b}"] = (
            float(delta_fit[mask].mean()) if mask.any() else None
        )
        gap_counts[f"count_h{b}"] = int(mask.sum())
    mask_ge4 = non_bypass & (dist >= 4)
    gap_bins["Baldwin_gap_h_ge4"] = (
        float(delta_fit[mask_ge4].mean()) if mask_ge4.any() else None
    )
    gap_counts["count_h_ge4"] = int(mask_ge4.sum())

    # delta_convergence summary per Hamming bin — universal-adapter
    # diagnostic (principle 4 degenerate-success guard).
    delta_stats: dict[str, float | None] = {}
    for b in HAMMING_BINS:
        mask = non_bypass & (dist == b)
        if mask.any():
            delta_stats[f"delta_mean_h{b}"] = float(delta_final[mask].mean())
            delta_stats[f"delta_std_h{b}"] = float(delta_final[mask].std())
        else:
            delta_stats[f"delta_mean_h{b}"] = None
            delta_stats[f"delta_std_h{b}"] = None

    return {
        "run_dir": run_dir.name,
        "arm": cfg.get("arm", result.get("arm", "")),
        "seed": int(cfg.get("seed", 0)),
        "seed_fraction": float(cfg.get("seed_fraction", 0.0)),
        "plasticity_budget": int(cfg.get("plasticity_budget", 0)),
        "plasticity_delta": float(cfg.get("plasticity_delta", 0.0)),
        "plasticity_enabled": bool(cfg.get("plasticity_enabled", False)),
        "best_fitness": float(result.get("best_fitness", float("nan"))),
        "best_fitness_train_frozen": float(train_fit_frozen.max()),
        "best_fitness_test_frozen": float(test_fit_frozen.max()),
        "best_fitness_train_plastic": float(train_fit_plastic.max()),
        "best_fitness_test_plastic": float(test_fit_plastic.max()),
        "R_fit_frozen_999": R_fit_frozen_999,
        "R_fit_plastic_999": R_fit_plastic_999,
        "R_fit_delta_999": R_fit_plastic_999 - R_fit_frozen_999,
        "GT_bypass_fraction": GT_bypass_fraction,
        "n_non_bypass": n_non_bypass,
        "Baldwin_slope": slope,
        "Baldwin_slope_bootstrap_mean": slope_boot,
        "Baldwin_slope_ci95_lo": slope_ci_lo,
        "Baldwin_slope_ci95_hi": slope_ci_hi,
        "delta_final_mean": float(delta_final.mean()),
        "delta_final_std": float(delta_final.std()),
        **gap_bins,
        **gap_counts,
        **delta_stats,
    }


def _cell_key(row: dict) -> tuple:
    return (
        row["arm"],
        row["plasticity_enabled"],
        row["plasticity_budget"],
        row["seed_fraction"],
    )


def summarize(rows: list[dict]) -> dict:
    cells: dict[tuple, list[dict]] = {}
    for r in rows:
        cells.setdefault(_cell_key(r), []).append(r)

    summary = []
    for key, members in sorted(cells.items()):
        arm, pl_enabled, pl_budget, sf = key
        # Per-cell means of scalar run-level metrics.
        def _mean(colname: str) -> float | None:
            vals = [m[colname] for m in members if m.get(colname) is not None
                    and not (isinstance(m[colname], float) and np.isnan(m[colname]))]
            return float(np.mean(vals)) if vals else None

        summary.append({
            "arm": arm,
            "plasticity_enabled": pl_enabled,
            "plasticity_budget": pl_budget,
            "seed_fraction": sf,
            "n_seeds": len(members),
            "R_fit_frozen_999_mean": _mean("R_fit_frozen_999"),
            "R_fit_plastic_999_mean": _mean("R_fit_plastic_999"),
            "R_fit_delta_999_mean": _mean("R_fit_delta_999"),
            "GT_bypass_fraction_mean": _mean("GT_bypass_fraction"),
            "Baldwin_slope_mean": _mean("Baldwin_slope"),
            "Baldwin_slope_ci95_lo_mean": _mean("Baldwin_slope_ci95_lo"),
            "Baldwin_slope_ci95_hi_mean": _mean("Baldwin_slope_ci95_hi"),
            "delta_final_mean_mean": _mean("delta_final_mean"),
            "delta_final_std_mean": _mean("delta_final_std"),
            "Baldwin_gap_h0_mean": _mean("Baldwin_gap_h0"),
            "Baldwin_gap_h1_mean": _mean("Baldwin_gap_h1"),
            "Baldwin_gap_h2_mean": _mean("Baldwin_gap_h2"),
            "Baldwin_gap_h3_mean": _mean("Baldwin_gap_h3"),
            "Baldwin_gap_h_ge4_mean": _mean("Baldwin_gap_h_ge4"),
        })
    return {
        "per_cell": summary,
        "bootstrap_spec": {"n_boot": 10_000, "alpha": 0.05, "rng_seed": 42},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep", help="sweep name under experiments/chem_tape/output/ "
                                   "(or an absolute path)")
    ap.add_argument("--canonical-hex", default=CANONICAL_AND_BODY_HEX)
    ap.add_argument("--alphabet", default="v2_probe")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    sweep_arg = Path(args.sweep)
    sw_dir = sweep_arg if sweep_arg.is_absolute() else OUTPUT_ROOT / args.sweep
    if not sw_dir.exists():
        print(f"sweep dir missing: {sw_dir}", file=sys.stderr)
        return 2

    canonical = hex_to_tape(args.canonical_hex)
    rows: list[dict] = []
    missing = skipped_frozen = 0
    for d in sorted(sw_dir.iterdir()):
        if not d.is_dir():
            continue
        r = analyze_run(d, canonical, args.alphabet)
        if r is None:
            # Distinguish "no final_population.npz" from "frozen-only run"
            fp = d / "final_population.npz"
            if not fp.exists():
                missing += 1
            else:
                skipped_frozen += 1
            continue
        rows.append(r)

    print(f"analyzed {len(rows)} run(s); "
          f"{missing} missing final_population.npz; "
          f"{skipped_frozen} frozen-only (no plasticity columns)")

    out_dir = args.out or sw_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "plasticity.csv"
    summary_path = out_dir / "plasticity_summary.json"

    if rows:
        csv_keys = [k for k in rows[0].keys() if not isinstance(rows[0][k], (dict, list))]
        with csv_path.open("w") as f:
            f.write(",".join(csv_keys) + "\n")
            for r in rows:
                f.write(",".join(
                    "" if r.get(k) is None else str(r[k])
                    for k in csv_keys
                ) + "\n")
    summary = summarize(rows)
    summary_path.write_text(json.dumps(summary, indent=2))

    print(f"  per-run CSV: {csv_path}")
    print(f"  summary JSON: {summary_path}")
    print()
    for cell in summary.get("per_cell", []):
        rf = cell.get("R_fit_frozen_999_mean")
        rp = cell.get("R_fit_plastic_999_mean")
        bs = cell.get("Baldwin_slope_mean")
        bs_lo = cell.get("Baldwin_slope_ci95_lo_mean")
        bs_hi = cell.get("Baldwin_slope_ci95_hi_mean")
        gt_fr = cell.get("GT_bypass_fraction_mean")
        rf_s = f"{rf:.3f}" if rf is not None else "-"
        rp_s = f"{rp:.3f}" if rp is not None else "-"
        bs_s = f"{bs:+.4f}" if bs is not None else "-"
        ci_s = (f"[{bs_lo:+.4f},{bs_hi:+.4f}]"
                if bs_lo is not None and bs_hi is not None else "[-, -]")
        gt_s = f"{gt_fr:.2f}" if gt_fr is not None else "-"
        print(
            f"  arm={cell['arm']:<8s} pl={int(cell['plasticity_enabled'])} "
            f"budget={cell['plasticity_budget']} "
            f"sf={cell['seed_fraction']:.3f}  n={cell['n_seeds']:>2}  "
            f"R_fit_frozen={rf_s}  R_fit_plastic={rp_s}  "
            f"Baldwin_slope={bs_s} CI95={ci_s}  "
            f"GT_bypass={gt_s}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
