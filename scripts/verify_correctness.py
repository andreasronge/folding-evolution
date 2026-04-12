"""Correctness fingerprint — run evaluate_population at fixed seed on both
shapes, SHA the fitness and predictions, and print a stable digest.

Used as a bit-identical gate for perf-opt phases: run before a change, run
after, diff the output.
"""

from __future__ import annotations

import argparse
import hashlib
import random
import sys

import numpy as np

from folding_evolution.ca import rule as ca_rule
from folding_evolution.ca.config import CAConfig
from folding_evolution.ca.evaluate import evaluate_population
from folding_evolution.ca.tasks import build_task


SHAPES: dict[str, CAConfig] = {
    "small": CAConfig(
        grid_n=16, steps=16, n_states=4,
        pop_size=256, n_examples=64,
        task="parity", n_bits=8,
        backend="mlx", seed=0,
    ),
    "heavy": CAConfig(
        grid_n=32, steps=64, n_states=4,
        pop_size=256, n_examples=256,
        task="parity", n_bits=8,
        backend="mlx", seed=0,
    ),
}


def fingerprint(cfg: CAConfig) -> tuple[str, str]:
    rng = random.Random(cfg.seed)
    pop = [ca_rule.random_genotype_for(cfg, rng) for _ in range(cfg.pop_size)]
    task = build_task(cfg, seed=cfg.seed)
    fitnesses, predictions = evaluate_population(pop, task, cfg)

    fit_hash = hashlib.sha256(np.ascontiguousarray(fitnesses).tobytes()).hexdigest()
    pred_hash = hashlib.sha256(np.ascontiguousarray(predictions).tobytes()).hexdigest()
    return fit_hash, pred_hash


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shapes", nargs="+", choices=list(SHAPES) + ["all"], default=["all"])
    args = parser.parse_args()

    shapes = list(SHAPES) if args.shapes == ["all"] else args.shapes
    exit_code = 0
    for name in shapes:
        cfg = SHAPES[name]
        fit_h, pred_h = fingerprint(cfg)
        # Also print the first 5 fitness values as a quick human-readable sanity.
        rng = random.Random(cfg.seed)
        pop = [ca_rule.random_genotype_for(cfg, rng) for _ in range(cfg.pop_size)]
        task = build_task(cfg, seed=cfg.seed)
        fitnesses, _ = evaluate_population(pop, task, cfg)
        head = ", ".join(f"{f:.6f}" for f in fitnesses[:5])
        print(f"{name:6s}  fit_sha={fit_h[:16]}  pred_sha={pred_h[:16]}  fitness[:5]=[{head}]")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
