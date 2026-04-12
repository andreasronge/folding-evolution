#!/usr/bin/env python3
"""Langton's λ reanalysis over every completed sweep (§13).

For each evolved best-genotype, compute λ = fraction of rule-table entries
mapping to a non-quiescent state (i.e. non-zero). Compare the evolved-λ
distribution to a same-shape random-rule baseline. Correlate λ with best-
fitness within each sweep cell.

Outputs:
  - analysis/lambda_summary.csv  : one row per evolved run (sweep, cell, λ, fit)
  - analysis/lambda_random.csv   : random-baseline λ distribution per (K, family)
  - analysis/lambda_{sweep}.png  : per-sweep evolved-vs-random histogram + fit vs λ scatter
  - analysis/lambda_all.png      : consolidated overview

Usage:
    python experiments/ca/analyze_lambda.py experiments/ca/output
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml


# ---------- λ computation ----------

def lambda_outer_totalistic(genotype_bytes: bytes, n_states: int) -> float:
    """λ = fraction of rule-table entries that map to a non-zero (non-quiescent) state.

    Classical Langton λ for outer-totalistic rules: count non-quiescent next-state
    entries divided by total entries. Each entry is one byte in the genotype.
    """
    arr = np.frombuffer(genotype_bytes, dtype=np.uint8)
    decoded = arr % n_states
    return float((decoded != 0).mean())


def lambda_decision_tree(genotype_bytes: bytes, n_states: int) -> float:
    """For a decision-tree rule, λ = fraction of *leaves* mapping to non-quiescent state.

    Matches the spirit of Langton's λ: fraction of terminal rule outputs that are
    non-zero. Structure bytes (pos, val for internal nodes) are excluded.
    """
    arr = np.frombuffer(genotype_bytes, dtype=np.uint8)
    # DT layout from rule_decision_tree.py: 31 pos + 31 val + 32 leaves.
    from folding_evolution.ca.rule_decision_tree import N_LEAVES, N_INTERNAL
    leaves = arr[2 * N_INTERNAL : 2 * N_INTERNAL + N_LEAVES] % n_states
    return float((leaves != 0).mean())


def lambda_from_run(config: dict, genotype_bytes: bytes) -> float | None:
    K = config["n_states"]
    fam = config.get("rule_family", "outer_totalistic")
    if fam == "outer_totalistic":
        return lambda_outer_totalistic(genotype_bytes, K)
    if fam == "decision_tree":
        return lambda_decision_tree(genotype_bytes, K)
    return None


# ---------- random baselines ----------

def random_lambda_distribution(
    rule_family: str,
    n_states: int,
    n_samples: int = 10_000,
    seed: int = 0,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if rule_family == "outer_totalistic":
        n_entries = n_states * (8 * (n_states - 1) + 1)
        samples = rng.integers(0, n_states, size=(n_samples, n_entries), dtype=np.uint8)
        return (samples != 0).mean(axis=1)
    if rule_family == "decision_tree":
        from folding_evolution.ca.rule_decision_tree import N_LEAVES
        samples = rng.integers(0, n_states, size=(n_samples, N_LEAVES), dtype=np.uint8)
        return (samples != 0).mean(axis=1)
    raise ValueError(f"Unknown rule_family {rule_family!r}")


# ---------- data collection ----------

def collect(output_root: Path) -> list[dict]:
    rows = []
    for result_path in output_root.glob("*/*/result.json"):
        run_dir = result_path.parent
        sweep = run_dir.parent.name
        cfg_path = run_dir / "config.yaml"
        if not cfg_path.exists():
            continue
        cfg = yaml.safe_load(cfg_path.read_text())
        res = json.loads(result_path.read_text())
        hex_str = res.get("best_genotype_hex")
        if not hex_str:
            continue
        genotype = bytes.fromhex(hex_str)
        lam = lambda_from_run(cfg, genotype)
        if lam is None:
            continue
        rows.append({
            "sweep": sweep,
            "hash": run_dir.name,
            "rule_family": cfg.get("rule_family", "outer_totalistic"),
            "n_states": cfg["n_states"],
            "n_bits": cfg.get("n_bits"),
            "task": cfg.get("task"),
            "grid_n": cfg.get("grid_n"),
            "steps": cfg.get("steps"),
            "seed": cfg.get("seed"),
            "best_fitness": float(res["best_fitness"]),
            "lambda": lam,
        })
    return rows


# ---------- plotting ----------

def per_sweep_plot(rows: list[dict], sweep: str, out_dir: Path) -> None:
    data = [r for r in rows if r["sweep"] == sweep]
    if not data:
        return
    # Group by (rule_family, n_states) for random-baseline comparison
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    groups = defaultdict(list)
    for r in data:
        groups[(r["rule_family"], r["n_states"])].append(r)

    colors = plt.cm.tab10(np.linspace(0, 1, max(10, len(groups))))

    # Histogram of evolved λ vs random baseline per group.
    ax = axes[0]
    for i, ((fam, K), rs) in enumerate(sorted(groups.items())):
        evolved = np.array([r["lambda"] for r in rs])
        rand = random_lambda_distribution(fam, K, n_samples=10_000, seed=0)
        ax.hist(rand, bins=30, alpha=0.3, density=True, color=colors[i], linestyle="--",
                label=f"{fam} K={K} random")
        if len(evolved) > 0:
            ax.hist(evolved, bins=min(15, max(3, len(evolved) // 2)),
                    alpha=0.7, density=True, color=colors[i],
                    label=f"{fam} K={K} evolved (n={len(evolved)})")
    ax.set_xlabel("Langton λ")
    ax.set_ylabel("density")
    ax.set_title(f"λ distributions — sweep: {sweep}")
    ax.legend(fontsize=8)
    ax.set_xlim(0, 1)

    # Fitness vs λ scatter.
    ax = axes[1]
    for i, ((fam, K), rs) in enumerate(sorted(groups.items())):
        x = [r["lambda"] for r in rs]
        y = [r["best_fitness"] for r in rs]
        ax.scatter(x, y, alpha=0.7, color=colors[i], label=f"{fam} K={K}")
    ax.set_xlabel("Langton λ")
    ax.set_ylabel("best fitness")
    ax.set_title(f"fitness vs λ — {sweep}")
    ax.axhline(0.5, color="grey", lw=0.8, linestyle=":")
    ax.legend(fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0.45, 1.05)

    plt.tight_layout()
    out = out_dir / f"lambda_{sweep}.png"
    plt.savefig(out, dpi=140)
    plt.close(fig)
    print(f"Wrote {out}")


def overview_plot(rows: list[dict], out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # Panel A: evolved λ aggregated by (rule_family, K), with random baseline reference lines.
    ax = axes[0]
    groups = defaultdict(list)
    for r in rows:
        groups[(r["rule_family"], r["n_states"])].append(r["lambda"])
    sorted_keys = sorted(groups.keys())
    positions = range(len(sorted_keys))
    box_data = [np.array(groups[k]) for k in sorted_keys]
    ax.boxplot(box_data, positions=list(positions), widths=0.5,
               tick_labels=[f"{f}\nK={k}" for f, k in sorted_keys])

    # Reference: random λ expected values.
    for i, (fam, K) in enumerate(sorted_keys):
        rand = random_lambda_distribution(fam, K, n_samples=5000, seed=0)
        ax.plot([i - 0.25, i + 0.25], [rand.mean(), rand.mean()],
                color="red", lw=2, alpha=0.7,
                label="random mean" if i == 0 else None)
    ax.set_ylabel("evolved λ")
    ax.set_title("Evolved λ by (family, K)")
    ax.set_ylim(0, 1)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)

    # Panel B: fitness vs λ colored by K; separated into solvable-task-cells vs stuck (K=2 is stuck).
    ax = axes[1]
    Ks = sorted({r["n_states"] for r in rows})
    colors = plt.cm.viridis(np.linspace(0, 1, len(Ks)))
    for K, col in zip(Ks, colors):
        sub = [r for r in rows if r["n_states"] == K]
        x = [r["lambda"] for r in sub]
        y = [r["best_fitness"] for r in sub]
        ax.scatter(x, y, alpha=0.5, color=col, s=20, label=f"K={K} (n={len(sub)})")
    ax.set_xlabel("Langton λ")
    ax.set_ylabel("best fitness")
    ax.set_title(f"All evolved rules (n={len(rows)})")
    ax.axhline(0.5, color="grey", lw=0.8, linestyle=":")
    ax.set_xlim(0, 1)
    ax.set_ylim(0.45, 1.05)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    out = out_dir / "lambda_all.png"
    plt.savefig(out, dpi=140)
    plt.close(fig)
    print(f"Wrote {out}")


# ---------- summary tables ----------

def print_summary(rows: list[dict]) -> None:
    print(f"\n=== λ summary over {len(rows)} evolved rules ===\n")
    # By (rule_family, K, task, n_bits): λ median + fitness median
    groups = defaultdict(list)
    for r in rows:
        key = (r["rule_family"], r["n_states"], r["task"], r["n_bits"])
        groups[key].append(r)
    header = f"{'family':>18}  {'K':>2}  {'task':>8}  {'bits':>4}  " \
             f"{'n':>3}  {'λ med':>6}  {'λ mean':>7}  {'rand λ':>6}  {'fit med':>7}"
    print(header)
    print("-" * len(header))
    for key in sorted(groups.keys()):
        fam, K, task, n_bits = key
        subset = groups[key]
        lams = np.array([r["lambda"] for r in subset])
        fits = np.array([r["best_fitness"] for r in subset])
        rand = random_lambda_distribution(fam, K, n_samples=5000, seed=0)
        print(f"{fam:>18}  {K:>2}  {str(task):>8}  {str(n_bits):>4}  "
              f"{len(subset):>3}  {np.median(lams):>6.3f}  {lams.mean():>7.3f}  "
              f"{rand.mean():>6.3f}  {np.median(fits):>7.3f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("output_root", type=Path, nargs="?",
                    default=Path("experiments/ca/output"))
    ap.add_argument("--out-dir", type=Path,
                    default=Path("experiments/ca/output/analysis"))
    args = ap.parse_args()

    rows = collect(args.output_root)
    if not rows:
        raise SystemExit(f"No runs found under {args.output_root}")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # CSV dump of all evolved λs.
    with open(args.out_dir / "lambda_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {args.out_dir / 'lambda_summary.csv'} ({len(rows)} rows)")

    print_summary(rows)

    # Per-sweep plots.
    sweeps = sorted({r["sweep"] for r in rows})
    for sweep in sweeps:
        per_sweep_plot(rows, sweep, args.out_dir)

    overview_plot(rows, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
