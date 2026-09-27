"""Effective mutation rate per arm (map-bias notebook §13, item 4).

For champions from the mvg_p20 runs (best genome every 100 generations, 10
seeds per arm), apply the arm's mutation operator many times and count how
often the child's predictions on the current goal's training inputs differ
from the parent's. Tagged runs are also measured at higher mutation rates to
find the rate matching the baseline.

Usage: uv run python experiments/chem_tape/effective_mutation_rate.py experiments/output/2026-09-26/mapbias_mvg_p20
"""

from __future__ import annotations

import csv
import json
import random
import sys
from dataclasses import fields, replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import yaml

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import evaluate_population
from folding_evolution.chem_tape.evolve import mutate
from folding_evolution.chem_tape.tasks import build_task

N_CHILDREN = 100
TAG_RATES = (0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.045)


def cfg_of(c: dict) -> ChemTapeConfig:
    names = {f.name for f in fields(ChemTapeConfig)}
    return ChemTapeConfig(**{k: v for k, v in c.items() if k in names})


def measure(item) -> dict:
    run_dir, c = item
    cfg = cfg_of(c)
    rows = list(csv.DictReader(open(Path(run_dir) / "history.csv")))
    goals = cfg.task_alternating_value_list()
    # Tagged arms: a range of rates plus the run's own (its realised rate).
    rates = tuple(sorted(set(TAG_RATES) | {cfg.mutation_rate})) if cfg.arm == "TAG" else (cfg.mutation_rate,)
    out = {}
    for mu in rates:
        m_cfg = replace(cfg, mutation_rate=mu)
        rng = random.Random(0)
        changed = total = 0
        for gen in range(100, len(rows), 100):
            g = np.frombuffer(bytes.fromhex(rows[gen]["best_genotype_hex"]), dtype=np.uint8)
            task = build_task(replace(cfg, task=goals[(gen // cfg.task_alternating_period) % len(goals)]), cfg.seed)
            kids = [mutate(g, m_cfg, rng) for _ in range(N_CHILDREN)]
            _, preds = evaluate_population([g] + kids, task, m_cfg)
            changed += int((preds[1:] != preds[0]).any(axis=1).sum())
            total += N_CHILDREN
        out[mu] = changed / total
    arm = "baseline" if cfg.arm != "TAG" else ("tagged+dup" if cfg.run_duplication_rate else "tagged")
    return {"arm": arm, "seed": cfg.seed, "rates": out}


def main(sweep_dir: str) -> None:
    sweep = Path(sweep_dir)
    items = []
    for r in json.loads((sweep / "sweep_index.json").read_text()):
        c = yaml.safe_load(open(Path(r["run_dir"]) / "config.yaml"))
        if c["seed"] < 10:
            items.append((r["run_dir"], c))
    with Pool(10) as pool:
        res = pool.map(measure, items)
    print("fraction of mutated children whose behaviour changes (champions every 100 gens, 10 seeds):")
    for arm in ("baseline", "tagged", "tagged+dup"):
        rs = [r for r in res if r["arm"] == arm]
        if not rs:
            continue
        for mu in sorted(rs[0]["rates"]):
            v = [r["rates"][mu] for r in rs]
            print(f"  {arm:11s} mutation_rate {mu:<6} -> {np.mean(v):.3f} (seed range {min(v):.3f}-{max(v):.3f})")
    (sweep / "effective_mutation_rate.json").write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1])
