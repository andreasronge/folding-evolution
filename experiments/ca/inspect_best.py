#!/usr/bin/env python3
"""Inspect the best-evolved rule from a single run.

Replays the CA on all task examples and prints each (input → intermediate → output).
Useful for understanding what computation evolution actually found.

Usage:
    python experiments/ca/inspect_best.py experiments/ca/output/mvp/d189db16a76e
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from folding_evolution.ca.config import CAConfig
from folding_evolution.ca import rule as ca_rule
from folding_evolution.ca import engine
from folding_evolution.ca.tasks import build_task


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--examples", type=int, default=8, help="how many examples to print")
    ap.add_argument("--show-grid", action="store_true", help="print the full final grid")
    args = ap.parse_args()

    cfg = CAConfig(**yaml.safe_load((args.run_dir / "config.yaml").read_text()))
    result = json.loads((args.run_dir / "result.json").read_text())
    geno = np.frombuffer(bytes.fromhex(result["best_genotype_hex"]), dtype=np.uint8).copy()

    print(f"Config: grid={cfg.grid_n} steps={cfg.steps} K={cfg.n_states} "
          f"task={cfg.task} n_bits={cfg.n_bits}")
    print(f"Best fitness: {result['best_fitness']:.3f}\n")

    table = ca_rule.decode(geno, cfg.n_states)
    print("Rule table (rows = self_state, cols = neighbor_sum):")
    print(table)
    print()

    task = build_task(cfg, seed=cfg.seed)
    n_show = min(args.examples, task.inputs.shape[0])

    clamp = task.encode(task.inputs[:n_show], cfg)
    initial = np.zeros((n_show, cfg.grid_n, cfg.grid_n), dtype=np.uint8)
    tables = np.broadcast_to(table[None, ...], (n_show, *table.shape))
    tables = np.ascontiguousarray(tables)

    final = engine.run(initial, tables, clamp, steps=cfg.steps, backend="numpy")
    out_row = cfg.resolved_output_row()
    out_col = cfg.resolved_output_col()
    out_states = final[:, out_row, out_col]
    preds = task.decode(out_states, cfg)

    print(f"{'input bits':>20}  label  out_state  pred  correct")
    for i in range(n_show):
        bits = "".join(str(b) for b in task.inputs[i])
        print(f"{bits:>20}    {task.labels[i]}        {out_states[i]}      {preds[i]}    "
              f"{'yes' if preds[i] == task.labels[i] else 'NO'}")

    if args.show_grid:
        print("\nFinal grids:")
        for i in range(n_show):
            print(f"\n--- example {i}: input={task.inputs[i].tolist()} label={task.labels[i]} "
                  f"pred={preds[i]} ---")
            print(final[i])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
