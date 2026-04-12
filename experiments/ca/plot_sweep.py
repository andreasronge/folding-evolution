#!/usr/bin/env python3
"""Plot fitness curves from a completed sweep directory.

Usage:
    python experiments/ca/plot_sweep.py experiments/ca/output/mvp
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep_dir", type=Path)
    ap.add_argument("--out", type=Path, default=None, help="PNG output path")
    args = ap.parse_args()

    runs = sorted(args.sweep_dir.glob("*/history.npz"))
    if not runs:
        raise SystemExit(f"No history.npz files found under {args.sweep_dir}")

    fig, (ax_best, ax_mean) = plt.subplots(1, 2, figsize=(11, 4), sharex=True)
    for p in runs:
        h = np.load(p)
        gens = h["generation"]
        ax_best.plot(gens, h["best_fitness"], alpha=0.5, lw=1)
        ax_mean.plot(gens, h["mean_fitness"], alpha=0.5, lw=1)

    # Median curves.
    stacks_best, stacks_mean = [], []
    for p in runs:
        h = np.load(p)
        stacks_best.append(h["best_fitness"])
        stacks_mean.append(h["mean_fitness"])
    best_median = np.median(np.stack(stacks_best), axis=0)
    mean_median = np.median(np.stack(stacks_mean), axis=0)
    gens = np.load(runs[0])["generation"]
    ax_best.plot(gens, best_median, color="black", lw=2.5, label="median")
    ax_mean.plot(gens, mean_median, color="black", lw=2.5, label="median")

    for ax, title in ((ax_best, "Best fitness per generation"),
                      (ax_mean, "Mean fitness per generation")):
        ax.set_title(title)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Fitness (fraction correct)")
        ax.axhline(0.5, color="grey", lw=0.8, linestyle=":", label="random baseline")
        ax.legend(loc="lower right", fontsize=9)
        ax.grid(alpha=0.3)
        ax.set_ylim(0.0, 1.05)

    out = args.out or (args.sweep_dir / "fitness_curves.png")
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
