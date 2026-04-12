#!/usr/bin/env python3
"""Exhaustive error-pattern analysis of a single evolved rule.

Reloads the best genotype from a run directory, evaluates it on all 2^n_bits
possible inputs (ignoring the training subset), and characterizes the error
structure:

  - error rate per bit-count group (0, 1, 2, ..., n_bits ones)
  - error rate per bit-position (which columns are predictive?)
  - train/holdout accuracy split
  - visual: 256-cell grid colored by prediction vs truth

Distinguishes three hypotheses for the observed 8-bit-parity ceiling:
  H1 parity-of-subset: errors cluster at certain bit-count regions
  H2 positional-bias:  errors cluster at inputs where specific positions differ
  H3 random:           errors uniformly spread, ~20% everywhere

Usage:
    python experiments/ca/inspect_errors.py experiments/ca/output/popsize_8bit/7ea2b8d7974c
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from folding_evolution.ca.config import CAConfig
from folding_evolution.ca import engine
from folding_evolution.ca.tasks import build_task


def exhaustive_inputs(n_bits: int) -> np.ndarray:
    """All 2^n_bits bit-pattern inputs, shape (2^n_bits, n_bits) int8."""
    total = 1 << n_bits
    return np.array(
        [[(i >> k) & 1 for k in range(n_bits)] for i in range(total)],
        dtype=np.int8,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    args = ap.parse_args()

    cfg_yaml = yaml.safe_load((args.run_dir / "config.yaml").read_text())
    cfg = CAConfig(**cfg_yaml)
    result = json.loads((args.run_dir / "result.json").read_text())
    geno = np.frombuffer(bytes.fromhex(result["best_genotype_hex"]), dtype=np.uint8).copy()

    n_bits = cfg.n_bits
    total = 1 << n_bits

    print(f"Run: {args.run_dir.name}")
    print(f"Task: {cfg.task} n_bits={n_bits}  (full input space = {total})")
    print(f"Rule family: {cfg.rule_family}  K={cfg.n_states}  N={cfg.grid_n}  T={cfg.steps}")
    print(f"Training fitness: {result['best_fitness']:.4f} on {cfg.n_examples} examples")

    # Training subset (same seed → same subset as build_task would draw).
    trained_task = build_task(cfg, seed=cfg.seed)
    trained_inputs = trained_task.inputs
    trained_indices = set(
        int(sum((int(b) << k) for k, b in enumerate(row))) for row in trained_inputs
    )

    # Run evaluation on ALL 2^n_bits inputs under this single rule.
    all_inputs = exhaustive_inputs(n_bits)
    if cfg.task == "parity":
        all_labels = all_inputs.sum(axis=1).astype(np.int8) % 2
    elif cfg.task == "majority":
        all_labels = (all_inputs.sum(axis=1) * 2 > n_bits).astype(np.int8)
    else:
        raise RuntimeError(f"Task {cfg.task} not supported for exhaustive analysis")

    cfg_eval = CAConfig(**{**cfg_yaml, "n_examples": total, "backend": "numpy"})
    eval_task = build_task(cfg_eval, seed=cfg.seed)
    # build_task may have subsampled for n_examples < total; bypass by supplying
    # exhaustive inputs directly.
    eval_task.inputs = all_inputs
    eval_task.labels = all_labels

    from folding_evolution.ca.evaluate import evaluate_population
    fitnesses, predictions = evaluate_population([geno], eval_task, cfg_eval)
    preds = predictions[0]

    correct = (preds == all_labels)
    total_acc = correct.mean()
    train_mask = np.array([
        int(sum((int(b) << k) for k, b in enumerate(row))) in trained_indices
        for row in all_inputs
    ])
    train_acc = correct[train_mask].mean() if train_mask.any() else float("nan")
    holdout_acc = correct[~train_mask].mean() if (~train_mask).any() else float("nan")

    print("\n=== Overall ===")
    print(f"Full-space accuracy: {total_acc:.4f} ({int(correct.sum())}/{total})")
    print(f"On training subset:  {train_acc:.4f} ({int(correct[train_mask].sum())}/{int(train_mask.sum())})")
    print(f"On holdout subset:   {holdout_acc:.4f} ({int(correct[~train_mask].sum())}/{int((~train_mask).sum())})")

    print("\n=== H1: error rate vs bit-count (number of 1s in input) ===")
    bitcounts = all_inputs.sum(axis=1)
    print(f"{'bit_count':>10}  {'n':>4}  {'correct':>8}  {'err_rate':>8}")
    for bc in range(n_bits + 1):
        mask = bitcounts == bc
        if mask.any():
            n = int(mask.sum())
            c = int(correct[mask].sum())
            print(f"{bc:>10}  {n:>4}  {c:>8}  {1 - c/n:>8.3f}")

    print("\n=== H2: per-bit-position influence (error rate conditional on bit set/unset) ===")
    print(f"{'position':>8}  {'err|bit=0':>10}  {'err|bit=1':>10}  {'diff':>8}")
    for pos in range(n_bits):
        bit = all_inputs[:, pos] == 1
        e0 = 1 - correct[~bit].mean() if (~bit).any() else float("nan")
        e1 = 1 - correct[bit].mean() if bit.any() else float("nan")
        print(f"{pos:>8}  {e0:>10.3f}  {e1:>10.3f}  {e1 - e0:>+8.3f}")

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    # (a) error rate by bit-count
    ax = axes[0]
    err_by_bc = []
    for bc in range(n_bits + 1):
        mask = bitcounts == bc
        err_by_bc.append(1 - correct[mask].mean() if mask.any() else 0)
    ax.bar(range(n_bits + 1), err_by_bc)
    ax.set_xlabel("number of 1s in input")
    ax.set_ylabel("error rate")
    ax.set_title("H1: errors by bit-count")
    ax.axhline(1 - total_acc, color="grey", linestyle=":", label="overall err")
    ax.legend()
    ax.set_ylim(0, max(1.05 * max(err_by_bc, default=0.1), 0.4))

    # (b) per-position error diff
    ax = axes[1]
    e0_arr, e1_arr = [], []
    for pos in range(n_bits):
        bit = all_inputs[:, pos] == 1
        e0_arr.append(1 - correct[~bit].mean() if (~bit).any() else 0)
        e1_arr.append(1 - correct[bit].mean() if bit.any() else 0)
    width = 0.4
    x = np.arange(n_bits)
    ax.bar(x - width/2, e0_arr, width, label="bit=0")
    ax.bar(x + width/2, e1_arr, width, label="bit=1")
    ax.set_xlabel("input bit position")
    ax.set_ylabel("error rate")
    ax.set_title("H2: errors by per-position bit value")
    ax.legend()
    ax.set_xticks(x)

    # (c) full 256-cell correctness map
    ax = axes[2]
    if total == 256:
        mat = correct.reshape(16, 16).astype(int)
        ax.imshow(mat, cmap="RdYlGn", vmin=0, vmax=1)
        ax.set_title(f"Correct=green, wrong=red  ({int(correct.sum())}/{total})")
        ax.set_xlabel("low 4 bits of input")
        ax.set_ylabel("high 4 bits of input")
    else:
        ax.text(0.5, 0.5, f"n_bits={n_bits}: {int(correct.sum())}/{total} correct",
                ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()

    out = args.run_dir / "error_analysis.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
