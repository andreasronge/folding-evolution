#!/usr/bin/env python3
"""Aggregate analysis of a completed CA-GP sweep.

Reads per-run config.yaml + result.json from a sweep directory, builds a tidy
dataframe-ish list, and produces:

  1. A 1-D summary: median final best_fitness per unique group of axes, printed.
  2. Boxplot per axis value (if axis has ≥2 unique values and ≥2 seeds each).
  3. Heatmap for every pair of categorical axes.

Usage:
    python experiments/ca/analyze_sweep.py experiments/ca/output/capacity
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml


AXES_OF_INTEREST = [
    "n_bits", "grid_n", "steps", "n_states", "pop_size",
    "generations", "mutation_rate", "rule_family", "task",
]


def _gens_to_threshold(history_path: Path, threshold: float = 1.0) -> int | None:
    """First generation whose best_fitness reached `threshold`, or None if never."""
    if not history_path.exists():
        return None
    h = np.load(history_path)
    hit = np.where(h["best_fitness"] >= threshold)[0]
    if len(hit) == 0:
        return None
    return int(h["generation"][hit[0]])


def collect(sweep_dir: Path) -> list[dict]:
    rows = []
    for result_path in sweep_dir.glob("*/result.json"):
        run_dir = result_path.parent
        config = yaml.safe_load((run_dir / "config.yaml").read_text())
        result = json.loads(result_path.read_text())
        row = {**config, **result}
        row["gens_to_solve"] = _gens_to_threshold(run_dir / "history.npz", 1.0)
        rows.append(row)
    return rows


def _varying_axes(rows: list[dict]) -> list[str]:
    """Axes that take ≥2 distinct values across rows."""
    varying = []
    for ax in AXES_OF_INTEREST:
        values = {r.get(ax) for r in rows if ax in r}
        if len(values) >= 2:
            varying.append(ax)
    return varying


def summary_table(rows: list[dict], axes: list[str]) -> None:
    print(f"\n=== Summary — {len(rows)} runs, axes varied: {axes} ===\n")
    groups: dict[tuple, list[tuple[float, int | None]]] = defaultdict(list)
    for r in rows:
        key = tuple(r[a] for a in axes)
        groups[key].append((r["best_fitness"], r.get("gens_to_solve")))
    header = (
        "  ".join(f"{a:>8}" for a in axes)
        + "   n   median    min    max    mean   solved  med_gens"
    )
    print(header)
    print("-" * len(header))
    for key in sorted(groups.keys()):
        fits = np.array([g[0] for g in groups[key]])
        solves = [g[1] for g in groups[key] if g[1] is not None]
        vals = "  ".join(f"{v!s:>8}" for v in key)
        solved_str = f"{len(solves)}/{len(fits)}"
        med_gens = f"{int(np.median(solves)):>6}" if solves else "     —"
        print(
            f"{vals}  {len(fits):>2}   {np.median(fits):.3f}  "
            f"{fits.min():.3f}  {fits.max():.3f}  {fits.mean():.3f}  "
            f"{solved_str:>6}  {med_gens}"
        )


def boxplot_per_axis(rows: list[dict], axes: list[str], out_dir: Path) -> None:
    for ax in axes:
        values = sorted({r[ax] for r in rows})
        data = [[r["best_fitness"] for r in rows if r[ax] == v] for v in values]
        if any(len(d) < 2 for d in data):
            continue
        fig, plot_ax = plt.subplots(figsize=(max(4, len(values) * 0.8), 4))
        plot_ax.boxplot(data, tick_labels=[str(v) for v in values])
        plot_ax.set_xlabel(ax)
        plot_ax.set_ylabel("Best fitness (final)")
        plot_ax.set_title(f"Best fitness vs {ax}")
        plot_ax.axhline(0.5, color="grey", lw=0.8, linestyle=":")
        plot_ax.set_ylim(0.45, 1.05)
        plot_ax.grid(alpha=0.3)
        out = out_dir / f"box_{ax}.png"
        plt.tight_layout()
        plt.savefig(out, dpi=150)
        plt.close(fig)
        print(f"Wrote {out}")


def heatmap_pairwise(rows: list[dict], axes: list[str], out_dir: Path) -> None:
    if len(axes) < 2:
        return
    for a, b in combinations(axes, 2):
        a_vals = sorted({r[a] for r in rows})
        b_vals = sorted({r[b] for r in rows})
        grid = np.full((len(a_vals), len(b_vals)), np.nan)
        for i, av in enumerate(a_vals):
            for j, bv in enumerate(b_vals):
                fits = [r["best_fitness"] for r in rows if r[a] == av and r[b] == bv]
                if fits:
                    grid[i, j] = float(np.median(fits))
        fig, ax_ = plt.subplots(figsize=(max(4, len(b_vals) * 0.7 + 2), max(3, len(a_vals) * 0.7 + 1.5)))
        im = ax_.imshow(grid, origin="lower", cmap="viridis", vmin=0.5, vmax=1.0, aspect="auto")
        ax_.set_xticks(range(len(b_vals)))
        ax_.set_xticklabels([str(v) for v in b_vals])
        ax_.set_yticks(range(len(a_vals)))
        ax_.set_yticklabels([str(v) for v in a_vals])
        ax_.set_xlabel(b)
        ax_.set_ylabel(a)
        ax_.set_title(f"Median best fitness: {a} vs {b}")
        for i in range(len(a_vals)):
            for j in range(len(b_vals)):
                if not np.isnan(grid[i, j]):
                    ax_.text(j, i, f"{grid[i,j]:.2f}", ha="center", va="center",
                             color="white" if grid[i,j] < 0.75 else "black", fontsize=9)
        plt.colorbar(im, ax=ax_, label="median best fitness")
        out = out_dir / f"heatmap_{a}_vs_{b}.png"
        plt.tight_layout()
        plt.savefig(out, dpi=150)
        plt.close(fig)
        print(f"Wrote {out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep_dir", type=Path)
    args = ap.parse_args()

    rows = collect(args.sweep_dir)
    if not rows:
        raise SystemExit(f"No runs found in {args.sweep_dir}")

    axes = _varying_axes(rows)
    # Treat 'seed' as replicates, not an axis to vary over.
    summary_table(rows, [a for a in axes if a != "seed"])
    boxplot_per_axis(rows, axes, args.sweep_dir)
    heatmap_pairwise(rows, [a for a in axes if a != "seed"], args.sweep_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
