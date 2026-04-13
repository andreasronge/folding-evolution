#!/usr/bin/env python3
"""Single-config chem-tape runner.

Usage:
    python experiments/chem_tape/run.py <config.yaml>
    python experiments/chem_tape/run.py <config.yaml> --seed 7
    python experiments/chem_tape/run.py <config.yaml> --output-root experiments/chem_tape/output/mvp

Writes:
    {output_root}/{config_hash}/config.yaml
    {output_root}/{config_hash}/result.json
    {output_root}/{config_hash}/history.npz
    {output_root}/{config_hash}/history.csv
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution


def load_config(path: Path, overrides: dict) -> ChemTapeConfig:
    raw = yaml.safe_load(path.read_text()) or {}
    if "config" in raw and len(raw) <= 2:
        raw = raw["config"]
    elif "base" in raw:
        raw = dict(raw["base"])
    for k in ("sweep_name", "grid", "base", "paired"):
        raw.pop(k, None)
    merged = {**raw, **overrides}
    return ChemTapeConfig(**merged)


def execute(cfg: ChemTapeConfig, output_root: Path) -> Path:
    run_dir = output_root / cfg.hash()
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "config.yaml").write_text(yaml.safe_dump(asdict(cfg)))

    t0 = time.time()
    result = run_evolution(cfg)
    elapsed = time.time() - t0

    result.stats.to_csv(run_dir / "history.csv")

    history = result.stats.history
    np.savez(
        run_dir / "history.npz",
        generation=np.array([s.generation for s in history]),
        best_fitness=np.array([s.best_fitness for s in history]),
        mean_fitness=np.array([s.mean_fitness for s in history]),
        std_fitness=np.array([s.std_fitness for s in history]),
        unique_genotypes=np.array([s.unique_genotypes for s in history]),
        mean_longest_run=np.array([s.mean_longest_run for s in history]),
        max_longest_run=np.array([s.max_longest_run for s in history]),
        best_longest_run=np.array([s.best_longest_run for s in history]),
    )

    summary = {
        "config_hash": cfg.hash(),
        "seed": cfg.seed,
        "arm": cfg.arm,
        "task": cfg.task,
        "best_fitness": result.best_fitness,
        "best_genotype_hex": result.best_genotype.tobytes().hex(),
        "generations_run": result.generations_run,
        "elapsed_sec": elapsed,
        "final_generation_best": history[-1].best_fitness,
        "final_generation_mean": history[-1].mean_fitness,
        "holdout_fitness": result.holdout_fitness,
    }
    (run_dir / "result.json").write_text(json.dumps(summary, indent=2))
    return run_dir


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config", type=Path, help="YAML config file")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--backend", type=str, default=None, choices=["numpy", "mlx"])
    ap.add_argument("--arm", type=str, default=None, choices=["A", "B"])
    ap.add_argument(
        "--output-root",
        type=Path,
        default=Path("experiments/chem_tape/output/adhoc"),
        help="Root directory for run outputs",
    )
    args = ap.parse_args()

    overrides: dict = {}
    if args.seed is not None:
        overrides["seed"] = args.seed
    if args.backend is not None:
        overrides["backend"] = args.backend
    if args.arm is not None:
        overrides["arm"] = args.arm

    cfg = load_config(args.config, overrides)
    run_dir = execute(cfg, args.output_root)
    print(f"Run complete: {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
