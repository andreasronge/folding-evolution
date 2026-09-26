#!/usr/bin/env python3
"""Profile actual chem-tape generations without changing the RNG stream.

Example: uv run python benchmarks/chem_tape_profile.py --generations 100
The summary separates reproduction, decoding, Rust execution, and statistics.
It also counts distinct decoded programs in each generation.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from folding_evolution.chem_tape import evaluate, evolve
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.metrics import ChemTapeStatsCollector


def profile(cfg: ChemTapeConfig, cache_size: int = 0) -> dict:
    elapsed: dict[str, list[float]] = {key: [] for key in ("reproduce", "evaluate", "decode", "execute", "stats")}
    unique: list[int] = []
    sizes: list[int] = []
    previously_seen: list[int] = []
    seen_programs: set[tuple[int, ...]] = set()
    original_reproduce = evolve._reproduce_one_island
    original_evaluate = evolve.evaluate_population
    original_decode = evaluate._programs_for_arm
    original_execute = getattr(evaluate, "_rust_exec_pop_batch", None)
    original_record = ChemTapeStatsCollector.record

    def timed(name, fn):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = fn(*args, **kwargs)
            elapsed[name].append(time.perf_counter() - start)
            return result
        return wrapper

    def decode(*args, **kwargs):
        start = time.perf_counter()
        programs = original_decode(*args, **kwargs)
        elapsed["decode"].append(time.perf_counter() - start)
        program_keys = [tuple(p) for p in programs]
        unique.append(len(set(program_keys)))
        sizes.append(len(programs))
        previously_seen.append(sum(key in seen_programs for key in program_keys))
        seen_programs.update(program_keys)
        return programs

    evolve._reproduce_one_island = timed("reproduce", original_reproduce)
    evolve.evaluate_population = timed("evaluate", original_evaluate)
    evaluate._programs_for_arm = decode
    if original_execute is not None:
        evaluate._rust_exec_pop_batch = timed("execute", original_execute)
    ChemTapeStatsCollector.record = timed("stats", original_record)
    wall_start = time.perf_counter()
    try:
        result = evolve.run_evolution(cfg, prediction_cache_size=cache_size)
    finally:
        evolve._reproduce_one_island = original_reproduce
        evolve.evaluate_population = original_evaluate
        evaluate._programs_for_arm = original_decode
        if original_execute is not None:
            evaluate._rust_exec_pop_batch = original_execute
        ChemTapeStatsCollector.record = original_record
    wall_seconds = time.perf_counter() - wall_start

    return {
        "config": {"arm": cfg.arm, "backend": cfg.backend, "seed": cfg.seed,
                   "population": cfg.pop_size, "generations": result.generations_run,
                   "cache_size": cache_size},
        "median_ms": {name: round(1000 * statistics.median(samples), 3) if samples else None
                      for name, samples in elapsed.items()},
        "decoded_unique_fraction": {
            "initial": round(unique[0] / sizes[0], 4),
            "middle": round(unique[len(unique) // 2] / sizes[len(sizes) // 2], 4),
            "final": round(unique[-1] / sizes[-1], 4),
        },
        "previously_seen_fraction": {
            "middle": round(previously_seen[len(unique) // 2] / sizes[len(sizes) // 2], 4),
            "final": round(previously_seen[-1] / sizes[-1], 4),
        },
        "best_fitness": result.best_fitness,
        "wall_seconds": round(wall_seconds, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generations", type=int, default=100)
    parser.add_argument("--population", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--arm", choices=("A", "BP_TOPK"), default="BP_TOPK")
    parser.add_argument("--backend", choices=("numpy", "mlx"), default="mlx")
    parser.add_argument("--cache-size", type=int, default=0)
    args = parser.parse_args()
    cfg = ChemTapeConfig(
        arm=args.arm, topk=3, bond_protection_ratio=0.5,
        task="sum_gt_10_v2", alphabet="v2_probe", backend=args.backend,
        pop_size=args.population, generations=args.generations, seed=args.seed,
        disable_early_termination=True, holdout_size=0,
    )
    print(json.dumps(profile(cfg, args.cache_size), indent=2))


if __name__ == "__main__":
    main()
