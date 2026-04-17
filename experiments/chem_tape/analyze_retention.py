#!/usr/bin/env python3
"""§v2.4-proxy-4d retention post-processor.

Reads `final_population.npz` (genotypes, fitnesses) from every run under
a sweep directory, computes edit-distance-k retention R_k against a
canonical target tape, and emits a per-run CSV + per-arm summary JSON.

Three edit-distance views:

- **active** (permeable-all) — token-level Levenshtein on the sequence of
  non-NOP, non-separator tokens in tape order. This is a **superset** of
  the BP_TOPK decode, so active-view distance and BP_TOPK-decode-view
  distance can disagree in either direction (not a strict bound). Under
  Arm A the VM runs the raw tape, so active drift approximates
  execution-trace drift up to NOP/separator no-op reorderings.
- **raw** — Levenshtein on the full 32-token tape.
- **decoded** (BP_TOPK-decode-consistent) — Levenshtein on the tokens
  that the BP_TOPK(k=topk) decoder actually passes to the VM: top-K
  longest non-separator runs concatenated in tape order. Mirrors
  `evaluate._programs_for_arm`'s BP_TOPK path exactly. For BP_TOPK
  runs this is the execution-semantic view. For Arm A runs the VM
  executes the raw tape, so the decoded column is informational
  ("what would this tape decode to if passed through BP_TOPK(k)?")
  rather than execution-semantic.

Usage:
    python experiments/chem_tape/analyze_retention.py <sweep_name>
        --canonical-hex <hex>
        [--out <dir>]

The sweep name is the subdirectory under experiments/chem_tape/output/.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from folding_evolution.chem_tape import alphabet as alph  # noqa: E402
from folding_evolution.chem_tape import engine  # noqa: E402

OUTPUT_ROOT = REPO_ROOT / "experiments" / "chem_tape" / "output"

CANONICAL_AND_BODY_HEX = "0201121008010510100708110000000000000000000000000000000000000000"

# --- METRIC_DEFINITIONS (principle 27) ---
#
# One-line specifications of what THIS module computes. Prereg metric
# declarations and chronicle metric-definition blocks cite these entries
# verbatim (copy/paste, not paraphrase). Keeping the definitions in code
# lets prereg-time and chronicle-time gates both verify that the metric
# named in prose matches the metric the code actually produces. See
# docs/methodology.md §27.
METRIC_DEFINITIONS: dict[str, str] = {
    "R0_active": (
        "Fraction of final-population tapes whose permeable-all active view "
        "(non-NOP, non-separator tokens in tape order, alphabet-aware separators) "
        "is byte-for-byte identical to canonical's 12-token active program."
    ),
    "R2_active": (
        "Fraction of final-population tapes whose permeable-all active view "
        "(non-NOP, non-separator tokens in tape order) is within Levenshtein "
        "edit distance 2 of canonical's 12-token active program. This view "
        "is a SUPERSET of the BP_TOPK(k) decode; active-view and decoded-view "
        "distances can disagree in either direction (Levenshtein is not "
        "monotone under the top-K-longest-run subsequence restriction)."
    ),
    "R2_raw": (
        "Fraction of final-population tapes whose full 32-token tape is "
        "within Levenshtein edit distance 2 of canonical's full 32-token tape "
        "(canonical 12-token AND body + 20-NOP tail)."
    ),
    "R2_decoded": (
        "Fraction of final-population tapes whose BP_TOPK(k=topk) decoded "
        "view — the exact token sequence passed to the VM under arm=BP_TOPK, "
        "computed as the top-K longest non-separator runs concatenated in "
        "tape order via engine.compute_topk_runnable_mask — is within "
        "Levenshtein edit distance 2 of canonical's decoded view. For "
        "arm=A runs this view is informational (the VM executes the raw "
        "tape), not execution-semantic."
    ),
    "R_fit_999": (
        "Fraction of final-population individuals whose training-task "
        "fitness is >= 0.999 (near-canonical fitness proxy, independent "
        "of structural distance from canonical)."
    ),
    "unique_genotypes": (
        "Count of distinct 32-token tapes in the final population, by "
        "raw byte equality. Upper-bounds full-population exact-match "
        "retention: R_exact <= (pop_size - unique_genotypes) / pop_size."
    ),
    "bootstrap_ci_spec": (
        "Nonparametric bootstrap over per-seed values: 10 000 resamples "
        "with replacement via numpy.random.default_rng(seed=42); 95% CI "
        "is the [2.5%, 97.5%] empirical quantile of the resampled means."
    ),
}


def hex_to_tape(hex_str: str) -> np.ndarray:
    raw = bytes.fromhex(hex_str)
    return np.frombuffer(raw, dtype=np.uint8).copy()


def extract_active(tape: np.ndarray, alphabet: str) -> tuple[int, ...]:
    """Return the active-program view: non-NOP, non-separator tokens in tape
    order. Mirrors decode_winner.extract_bp_topk_program (which uses the
    permeable-all approximation) but is alphabet-aware for separator ids.
    """
    masks = alph.masks_for(alphabet)
    sep = masks["separator"]
    out: list[int] = []
    for t in tape.tolist():
        ti = int(t)
        if ti == 0:
            continue  # NOP
        if sep[ti]:
            continue  # separator
        out.append(ti)
    return tuple(out)


def extract_decoded(tape: np.ndarray, topk: int) -> tuple[int, ...]:
    """Return the BP_TOPK(k=topk) decode-consistent view: tokens under the
    top-K longest non-separator runs, concatenated in tape order. Mirrors
    `evaluate._programs_for_arm`'s BP_TOPK path — the exact sequence of
    tokens the VM executes for arm=BP_TOPK.

    For an Arm A run this is informational only: the VM executes the raw
    tape, so the decoded view answers "what would this tape decode to
    under BP_TOPK(k)?" rather than reporting what actually ran.
    """
    tapes = tape.reshape(1, -1)
    mask = engine.compute_topk_runnable_mask(tapes, topk, backend="numpy")
    return tuple(int(t) for t in tape[mask[0]].tolist())


def levenshtein(a: tuple[int, ...], b: tuple[int, ...], cap: int | None = None) -> int:
    """Classic iterative Levenshtein with optional early-exit cap.

    If `cap` is given and the distance exceeds `cap`, returns cap+1 (callers
    only need to know whether d ≤ cap).
    """
    la, lb = len(a), len(b)
    if abs(la - lb) > (cap if cap is not None else max(la, lb)):
        return (cap or max(la, lb)) + 1
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        row_min = cur[0]
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(
                prev[j] + 1,        # deletion
                cur[j - 1] + 1,     # insertion
                prev[j - 1] + cost, # substitution
            )
            if cur[j] < row_min:
                row_min = cur[j]
        if cap is not None and row_min > cap:
            return cap + 1
        prev = cur
    return prev[lb]


def analyze_run(
    run_dir: Path, canonical_tape: np.ndarray, alphabet: str
) -> dict | None:
    fp = run_dir / "final_population.npz"
    if not fp.exists():
        return None
    result_path = run_dir / "result.json"
    cfg_path = run_dir / "config.yaml"
    if not result_path.exists() or not cfg_path.exists():
        return None
    result = json.loads(result_path.read_text())
    cfg = yaml.safe_load(cfg_path.read_text()) or {}

    data = np.load(fp)
    genotypes = data["genotypes"]         # (P, L) uint8
    fitnesses = data["fitnesses"]          # (P,) float32
    P, L = genotypes.shape
    unique_genotypes = len({bytes(g) for g in genotypes})

    # Decode-consistent K: read from cfg; 4d sweeps use K=3 per base.
    # For Arm A runs, topk defaults to 1 in ChemTapeConfig but is
    # informational here (not execution semantics) — see extract_decoded.
    topk_val = int(cfg.get("topk", 3))
    arm_val = str(cfg.get("arm", result.get("arm", "")))

    can_active = extract_active(canonical_tape, alphabet)
    can_raw = tuple(int(t) for t in canonical_tape.tolist())
    can_decoded = extract_decoded(canonical_tape, topk_val)

    # Cap edit-distance computation at 4 (we care about R_0..R_3 buckets only).
    dist_active = np.empty(P, dtype=np.int16)
    dist_raw = np.empty(P, dtype=np.int16)
    dist_decoded = np.empty(P, dtype=np.int16)
    for i in range(P):
        tape = genotypes[i]
        act = extract_active(tape, alphabet)
        dist_active[i] = levenshtein(act, can_active, cap=4)
        raw = tuple(int(t) for t in tape.tolist())
        dist_raw[i] = levenshtein(raw, can_raw, cap=4)
        dec = extract_decoded(tape, topk_val)
        dist_decoded[i] = levenshtein(dec, can_decoded, cap=4)

    def frac_le(arr: np.ndarray, k: int) -> float:
        return float(np.mean(arr <= k))

    R_active = {k: frac_le(dist_active, k) for k in range(4)}
    R_raw = {k: frac_le(dist_raw, k) for k in range(4)}
    R_decoded = {k: frac_le(dist_decoded, k) for k in range(4)}

    # R_fit: fraction with fitness ≥ 0.999 (near-canonical fitness proxy).
    R_fit = float(np.mean(fitnesses >= 0.999))

    # Histogram of active edit distance 0..12+ (capped) for bimodality check.
    # Use bins 0,1,2,3,>=4.
    hist_active = [int(np.sum(dist_active == k)) for k in range(4)] + [
        int(np.sum(dist_active >= 4))
    ]

    return {
        "config_hash": result.get("config_hash", run_dir.name),
        "seed": int(cfg.get("seed", result.get("seed", -1))),
        "arm": arm_val,
        "topk": topk_val,
        "seed_fraction": float(cfg.get("seed_fraction", 0.0)),
        "safe_pop_mode": str(cfg.get("safe_pop_mode", "preserve")),
        "pop_size": P,
        "tape_length": L,
        "unique_genotypes": unique_genotypes,
        "best_fitness": float(result.get("best_fitness", -1.0)),
        "final_generation_mean": float(result.get("final_generation_mean", -1.0)),
        "R0_active": R_active[0],
        "R1_active": R_active[1],
        "R2_active": R_active[2],
        "R3_active": R_active[3],
        "R0_raw": R_raw[0],
        "R1_raw": R_raw[1],
        "R2_raw": R_raw[2],
        "R3_raw": R_raw[3],
        "R0_decoded": R_decoded[0],
        "R1_decoded": R_decoded[1],
        "R2_decoded": R_decoded[2],
        "R3_decoded": R_decoded[3],
        "R_fit_999": R_fit,
        "hist_active_0_1_2_3_ge4": hist_active,
    }


def bootstrap_ci(
    xs: np.ndarray, n_boot: int = 10_000, alpha: float = 0.05, seed: int = 42
) -> tuple[float, float]:
    """Nonparametric bootstrap 95% CI on the mean. Fixed seed for
    reproducibility; recorded in the summary for audit."""
    rng = np.random.default_rng(seed)
    boots = rng.choice(xs, size=(n_boot, len(xs)), replace=True).mean(axis=1)
    return float(np.quantile(boots, alpha / 2)), float(np.quantile(boots, 1 - alpha / 2))


def summarize_arm(rows: list[dict]) -> dict:
    """Aggregate per-arm (keyed by seed_fraction, safe_pop_mode, arm)."""
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        key = (r["arm"], r["safe_pop_mode"], r["seed_fraction"])
        groups[key].append(r)
    summary: list[dict] = []
    for key, grp in sorted(groups.items()):
        arm, spm, sf = key
        r2a = np.array([r["R2_active"] for r in grp])
        r2r = np.array([r["R2_raw"] for r in grp])
        r2d = np.array([r["R2_decoded"] for r in grp])
        r0a = np.array([r["R0_active"] for r in grp])
        r0d = np.array([r["R0_decoded"] for r in grp])
        rfit = np.array([r["R_fit_999"] for r in grp])
        uniq = np.array([r["unique_genotypes"] for r in grp])
        fmean = np.array([r["final_generation_mean"] for r in grp])
        bfit = np.array([r["best_fitness"] for r in grp])
        solve = int(np.sum(bfit >= 0.999))
        r2a_lo, r2a_hi = bootstrap_ci(r2a)
        r2d_lo, r2d_hi = bootstrap_ci(r2d)
        summary.append({
            "arm": arm,
            "safe_pop_mode": spm,
            "seed_fraction": sf,
            "n_seeds": len(grp),
            "R2_active_mean": float(r2a.mean()),
            "R2_active_ci95_lo": r2a_lo,
            "R2_active_ci95_hi": r2a_hi,
            "R2_active_median": float(np.median(r2a)),
            "R2_active_min": float(r2a.min()),
            "R2_active_max": float(r2a.max()),
            "R2_raw_mean": float(r2r.mean()),
            "R2_decoded_mean": float(r2d.mean()),
            "R2_decoded_ci95_lo": r2d_lo,
            "R2_decoded_ci95_hi": r2d_hi,
            "R2_decoded_median": float(np.median(r2d)),
            "R2_decoded_min": float(r2d.min()),
            "R2_decoded_max": float(r2d.max()),
            "R0_active_mean": float(r0a.mean()),
            "R0_decoded_mean": float(r0d.mean()),
            "R_fit_999_mean": float(rfit.mean()),
            "unique_genotypes_mean": float(uniq.mean()),
            "final_mean_fitness_mean": float(fmean.mean()),
            "solve_count": solve,
        })
    return {
        "per_cell": summary,
        "bootstrap_spec": {"n_boot": 10_000, "alpha": 0.05, "rng_seed": 42},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep", help="sweep name under experiments/chem_tape/output/")
    ap.add_argument("--canonical-hex", default=CANONICAL_AND_BODY_HEX)
    ap.add_argument("--alphabet", default="v2_probe")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    sw_dir = OUTPUT_ROOT / args.sweep
    if not sw_dir.exists():
        print(f"sweep dir missing: {sw_dir}", file=sys.stderr)
        return 2

    canonical = hex_to_tape(args.canonical_hex)
    rows: list[dict] = []
    missing = 0
    for d in sorted(sw_dir.iterdir()):
        if not d.is_dir():
            continue
        r = analyze_run(d, canonical, args.alphabet)
        if r is None:
            missing += 1
            continue
        rows.append(r)

    print(f"analyzed {len(rows)} run(s); {missing} had no final_population.npz")

    out_dir = args.out or sw_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "retention.csv"
    summary_path = out_dir / "retention_summary.json"

    if rows:
        keys = list(rows[0].keys())
        with csv_path.open("w") as f:
            f.write(",".join(keys) + "\n")
            for r in rows:
                f.write(",".join(str(r[k]) for k in keys) + "\n")
    summary = summarize_arm(rows)
    summary_path.write_text(json.dumps(summary, indent=2))

    print(f"  per-run CSV: {csv_path}")
    print(f"  summary JSON: {summary_path}")
    print()
    for cell in summary.get("per_cell", []):
        print(
            f"  arm={cell['arm']:<8s} spm={cell['safe_pop_mode']:<8s} "
            f"sf={cell['seed_fraction']:.3f}  n={cell['n_seeds']:>2}  "
            f"R2_active={cell['R2_active_mean']:.4f} "
            f"CI95=[{cell['R2_active_ci95_lo']:.4f},{cell['R2_active_ci95_hi']:.4f}]  "
            f"R2_decoded={cell['R2_decoded_mean']:.4f} "
            f"CI95=[{cell['R2_decoded_ci95_lo']:.4f},{cell['R2_decoded_ci95_hi']:.4f}]  "
            f"R_fit={cell['R_fit_999_mean']:.3f}  "
            f"uniq={cell['unique_genotypes_mean']:.1f}  "
            f"final_mean={cell['final_mean_fitness_mean']:.3f}  "
            f"solve={cell['solve_count']}/{cell['n_seeds']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
