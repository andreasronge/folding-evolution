#!/usr/bin/env python3
"""Generic sweep runner for CA-GP.

Reads a sweep YAML with the form:

    sweep_name: mvp
    backend: mlx             # default if not in grid
    base:
        grid_n: 16
        steps: 16
        n_states: 4
        pop_size: 256
        generations: 200
        n_bits: 4
        n_examples: 16
    grid:
        seed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Expands the `grid` dict into the Cartesian product of CAConfig overrides, merges
with `base`, and runs each config. Outputs to experiments/ca/output/{sweep_name}/{hash}/.

Resumable: if a config hash directory already has result.json, it is skipped.

Parallelism:
  --workers N  use a multiprocessing pool of N workers (default 1 for MLX to
               avoid Metal contention; raise for numpy backend).
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from folding_evolution.ca.config import CAConfig

# Import late inside worker to keep pool-start cheap.


def expand_grid(spec: dict[str, Any]) -> list[CAConfig]:
    """Expand a sweep spec into a list of CAConfigs.

    Supports two axis kinds:
      - `grid`: dict[str, list] — Cartesian product across keys.
      - `paired`: list[dict]    — items iterated in parallel (zipped),
                                  crossed with `grid`.

    Base fields in `base` apply to every config; `grid`/`paired` override.
    """
    base = dict(spec.get("base", {}))
    grid = spec.get("grid", {}) or {}
    paired = spec.get("paired", []) or []

    # Normalize paired: list of override-dicts. An empty paired means one
    # no-op "paired item" so the Cartesian works uniformly.
    paired_items: list[dict] = list(paired) if paired else [{}]

    if not grid:
        configs = [CAConfig(**{**base, **p}) for p in paired_items]
        return configs

    grid_keys = sorted(grid.keys())
    grid_values = [grid[k] for k in grid_keys]

    configs: list[CAConfig] = []
    for combo in itertools.product(*grid_values):
        grid_overrides = dict(zip(grid_keys, combo))
        for p in paired_items:
            configs.append(CAConfig(**{**base, **p, **grid_overrides}))
    return configs


def _worker(payload: tuple[dict, str]) -> dict:
    cfg_dict, output_root_str = payload
    # Import inside worker so parent process stays light; MLX also isolates cleanly.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run import execute  # type: ignore
    cfg = CAConfig(**cfg_dict)
    output_root = Path(output_root_str)
    run_dir = execute(cfg, output_root)
    summary = json.loads((run_dir / "result.json").read_text())
    return {"hash": cfg.hash(), "run_dir": str(run_dir), **summary}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep", type=Path, help="sweep YAML")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--output-root", type=Path, default=None)
    ap.add_argument("--force", action="store_true", help="ignore existing results")
    args = ap.parse_args()

    spec = yaml.safe_load(args.sweep.read_text())
    sweep_name = spec.get("sweep_name", args.sweep.stem)
    output_root = args.output_root or Path("experiments/ca/output") / sweep_name
    output_root.mkdir(parents=True, exist_ok=True)

    configs = expand_grid(spec)
    print(f"Sweep '{sweep_name}': {len(configs)} config(s) → {output_root}")

    # Filter already-done.
    to_run: list[CAConfig] = []
    skipped: list[CAConfig] = []
    for cfg in configs:
        if (output_root / cfg.hash() / "result.json").exists() and not args.force:
            skipped.append(cfg)
        else:
            to_run.append(cfg)
    print(f"  to run: {len(to_run)}    already done: {len(skipped)}")

    t0 = time.time()
    results: list[dict] = []
    if args.workers > 1 and to_run:
        payloads = [(asdict(c), str(output_root)) for c in to_run]
        with mp.get_context("spawn").Pool(args.workers) as pool:
            for r in pool.imap_unordered(_worker, payloads):
                print(f"  done: {r['config_hash']} best={r['best_fitness']:.3f}")
                results.append(r)
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from run import execute  # type: ignore
        for cfg in to_run:
            rd = execute(cfg, output_root)
            summary = json.loads((rd / "result.json").read_text())
            print(
                f"  done: {summary['config_hash']} "
                f"best={summary['best_fitness']:.3f} "
                f"elapsed={summary['elapsed_sec']:.1f}s"
            )
            results.append({"hash": cfg.hash(), "run_dir": str(rd), **summary})

    elapsed = time.time() - t0
    print(f"Sweep done: {len(results)} new run(s) in {elapsed:.1f}s")

    # Sweep-level index.
    index_path = output_root / "sweep_index.json"
    existing: list[dict] = []
    if index_path.exists():
        existing = json.loads(index_path.read_text())
    by_hash = {e["hash"]: e for e in existing}
    for r in results:
        by_hash[r["hash"]] = r
    index_path.write_text(json.dumps(sorted(by_hash.values(), key=lambda x: x["hash"]), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
