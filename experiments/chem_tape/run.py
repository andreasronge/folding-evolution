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
    npz_data = dict(
        generation=np.array([s.generation for s in history]),
        best_fitness=np.array([s.best_fitness for s in history]),
        mean_fitness=np.array([s.mean_fitness for s in history]),
        std_fitness=np.array([s.std_fitness for s in history]),
        unique_genotypes=np.array([s.unique_genotypes for s in history]),
        unique_programs=np.array([s.unique_programs for s in history]),
        mean_longest_run=np.array([s.mean_longest_run for s in history]),
        max_longest_run=np.array([s.max_longest_run for s in history]),
        best_longest_run=np.array([s.best_longest_run for s in history]),
    )
    if history and history[0].per_island_best is not None:
        # Shape: (n_generations_logged, n_islands)
        npz_data["per_island_best"] = np.stack([s.per_island_best for s in history])
        npz_data["per_island_mean"] = np.stack([s.per_island_mean for s in history])
    if history and history[0].k_distribution is not None:
        # Shape: (n_generations_logged, n_k_values)
        npz_data["k_distribution"] = np.stack([s.k_distribution for s in history])
    # §v2.5-plasticity-2a: gen-0 canonical-count scalar (principle 23/25
    # infrastructure-fidelity check). At cfg.seed_tapes == "" (all sf=0.0
    # runs) the count is 0; any nonzero value flags a build_initial_population
    # bug. Stored as a 0-d int64 array for npz round-trip.
    npz_data["initial_population_canonical_count"] = np.asarray(
        result.initial_population_canonical_count, dtype=np.int64
    )
    np.savez(run_dir / "history.npz", **npz_data)

    # §v2.4-proxy-4d: dump final-gen population when the flag is set.
    # final_population shape: (pop_size, tape_length) uint8.
    # final_population_fitness shape: (pop_size,) float32.
    # §v2.5-plasticity-1a: when plasticity is enabled, also dump per-
    # individual plastic metrics (delta_final, test_fitness_frozen/plastic,
    # train_fitness_frozen/plastic, has_gt) into the same NPZ so
    # analyze_plasticity.py can consume a single artifact per run.
    if result.final_population is not None:
        npz_fp: dict = {
            "genotypes": result.final_population,
            "fitnesses": result.final_population_fitness,
        }
        if result.final_delta_final is not None:
            npz_fp["delta_final"] = result.final_delta_final
            npz_fp["test_fitness_frozen"] = result.final_test_fitness_frozen
            npz_fp["test_fitness_plastic"] = result.final_test_fitness_plastic
            npz_fp["train_fitness_frozen"] = result.final_train_fitness_frozen
            npz_fp["train_fitness_plastic"] = result.final_train_fitness_plastic
            npz_fp["has_gt"] = result.final_has_gt
        np.savez(run_dir / "final_population.npz", **npz_fp)

    holdout = result.holdout_fitness
    gap = None if holdout is None else float(result.best_fitness) - float(holdout)
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
        "holdout_fitness": holdout,
        "train_holdout_gap": gap,
    }
    if result.flip_events is not None:
        summary["flip_events"] = result.flip_events
    if result.cross_task_fitness is not None:
        summary["cross_task_fitness"] = result.cross_task_fitness
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
