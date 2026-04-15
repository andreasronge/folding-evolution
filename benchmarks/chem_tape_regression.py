#!/usr/bin/env python3
"""Chem-tape micro-benchmark for performance regression tracking.

Measures per-generation hot-path costs at a v2-shaped config (pop=1024,
arm=BP_TOPK, alphabet=v2_probe, bond_protection_ratio=0.5). Reduced to 50
generations — we're measuring per-gen throughput, not an evolutionary outcome.

Measurement discipline:
  - Same seed (cfg.seed) used for every rep — median-of-N measures implementation
    noise on a fixed workload, not seed variance.
  - RNG state is snapshot before each measured block and restored after, so
    mutate/reproduce don't pollute the RNG stream seen by other timed blocks.
  - pyo3_crossings_per_gen is counted on the timed gen_total path (covers the
    evaluate call that happens inside one generation).

Columns (median of N_REPS runs each):
  phase                 — label for the row (e.g. baseline, phase1, phase2, phase3)
  git_hash              — short commit hash
  pop_eval_sec          — evaluate_population(pop, task, cfg) wall time
  mutate_sec            — full-population mutation wall time (pop_size calls to mutate)
  gen_total_sec         — one full generation: _reproduce_one_island + evaluate_population
  pyo3_crossings_per_gen  — count of Rust-executor calls inside one generation's gen_total
  pop_size, generations_run, task, arm, alphabet
  timestamp

Usage:
  uv run python benchmarks/chem_tape_regression.py [--phase baseline] [--reps 5]
  uv run python benchmarks/chem_tape_regression.py --show
"""

from __future__ import annotations

import argparse
import csv
import random
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from folding_evolution.chem_tape import evaluate as _chem_evaluate
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import evaluate_population
from folding_evolution.chem_tape.evolve import (
    _reproduce_one_island,
    mutate,
    random_genotype,
)
from folding_evolution.chem_tape.tasks import build_task


RESULTS_CSV = Path(__file__).resolve().parent / "chem_tape_results.csv"
COLS = [
    "timestamp",
    "git_hash",
    "phase",
    "pop_size",
    "generations_run",
    "task",
    "arm",
    "alphabet",
    "pop_eval_sec",
    "mutate_sec",
    "gen_total_sec",
    "pyo3_crossings_per_gen",
    "notes",
]


def _git_hash() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=Path(__file__).resolve().parent.parent
        )
        return out.decode().strip()
    except Exception:
        return "unknown"


def _bench_config() -> ChemTapeConfig:
    return ChemTapeConfig(
        tape_length=32,
        arm="BP_TOPK",
        topk=3,
        bond_protection_ratio=0.5,
        task="sum_gt_10_v2",
        n_examples=64,
        holdout_size=0,
        pop_size=1024,
        generations=50,
        tournament_size=3,
        elite_count=2,
        mutation_rate=0.03,
        crossover_rate=0.7,
        alphabet="v2_probe",
        seed=0,
        backend="mlx",
        log_every=1000,  # disable
    )


@dataclass
class _CrossingCounter:
    """Counts invocations of either `_rust_exec_batch` (per-individual path)
    or `_rust_exec_pop_batch` (new pop-batch path) while active. Both are
    wrapped simultaneously so the counter reports total Rust-executor calls
    regardless of which dispatch branch evaluate_population takes."""
    count: int = 0

    def __enter__(self):
        self._orig = getattr(_chem_evaluate, "_rust_exec_batch", None)
        self._orig_pop = getattr(_chem_evaluate, "_rust_exec_pop_batch", None)
        if self._orig is not None:
            def wrapped(*a, **kw):
                self.count += 1
                return self._orig(*a, **kw)
            _chem_evaluate._rust_exec_batch = wrapped  # type: ignore[attr-defined]
        if self._orig_pop is not None:
            def wrapped_pop(*a, **kw):
                self.count += 1
                return self._orig_pop(*a, **kw)
            _chem_evaluate._rust_exec_pop_batch = wrapped_pop  # type: ignore[attr-defined]
        return self

    def __exit__(self, *exc):
        if self._orig is not None:
            _chem_evaluate._rust_exec_batch = self._orig  # type: ignore[attr-defined]
        if self._orig_pop is not None:
            _chem_evaluate._rust_exec_pop_batch = self._orig_pop  # type: ignore[attr-defined]


def _build_population(cfg: ChemTapeConfig, rng: random.Random) -> list[np.ndarray]:
    return [random_genotype(cfg, rng) for _ in range(cfg.pop_size)]


def _time(fn, *args, **kwargs) -> tuple[float, object]:
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    return time.perf_counter() - t0, out


def measure(cfg: ChemTapeConfig, reps: int) -> dict:
    """Repeat each measurement `reps` times on a FIXED workload (cfg.seed).
    RNG state is snapshot before each measured block and restored after so
    the three blocks don't pollute each other's RNG streams.

    Returns medians + crossing count sampled from the gen_total path.
    """
    eval_samples: list[float] = []
    mutate_samples: list[float] = []
    gen_samples: list[float] = []
    crossings_samples: list[int] = []

    # Build once — same task, same initial pop across all reps.
    base_rng = random.Random(cfg.seed)
    task = build_task(cfg, cfg.seed)
    pop = _build_population(cfg, base_rng)

    # Warm once (MLX kernel compile, Rayon thread-pool spin-up, import JIT).
    _ = evaluate_population(pop, task, cfg)

    # Precompute a reference fitness vector used by _gen's reproduce step.
    ref_fits, _ = evaluate_population(pop, task, cfg)

    # Snapshot the RNG state AFTER setup so every rep starts from the same
    # RNG position — implementation comparisons stay on equal footing.
    rng_state_after_setup = base_rng.getstate()

    for rep in range(reps):
        # --- 1) evaluate_population alone ---
        t_eval, _ = _time(evaluate_population, pop, task, cfg)
        eval_samples.append(t_eval)

        # --- 2) mutate_sec — full-pop mutation on a scratch RNG ---
        rng_mut = random.Random()
        rng_mut.setstate(rng_state_after_setup)

        def _full_mutate():
            out = []
            for g in pop:
                out.append(mutate(g, cfg, rng_mut))
            return out

        t_mut, _ = _time(_full_mutate)
        mutate_samples.append(t_mut)

        # --- 3) gen_total_sec — one full generation on a scratch RNG ---
        rng_gen = random.Random()
        rng_gen.setstate(rng_state_after_setup)

        def _gen():
            new_pop = _reproduce_one_island(pop, ref_fits, cfg, rng_gen)
            new_fits, _ = evaluate_population(new_pop, task, cfg)
            return new_fits

        if rep == 0:
            # Sample crossing count on the same gen_total path that's being timed.
            with _CrossingCounter() as cc:
                t_gen, _ = _time(_gen)
            crossings_samples.append(cc.count)
        else:
            t_gen, _ = _time(_gen)
        gen_samples.append(t_gen)

    return {
        "pop_eval_sec": statistics.median(eval_samples),
        "mutate_sec": statistics.median(mutate_samples),
        "gen_total_sec": statistics.median(gen_samples),
        "pyo3_crossings_per_gen": crossings_samples[0] if crossings_samples else -1,
    }


def append_row(phase: str, cfg: ChemTapeConfig, m: dict, notes: str = "") -> None:
    row = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "git_hash": _git_hash(),
        "phase": phase,
        "pop_size": cfg.pop_size,
        "generations_run": cfg.generations,
        "task": cfg.task,
        "arm": cfg.arm,
        "alphabet": cfg.alphabet,
        "pop_eval_sec": f"{m['pop_eval_sec']:.4f}",
        "mutate_sec": f"{m['mutate_sec']:.4f}",
        "gen_total_sec": f"{m['gen_total_sec']:.4f}",
        "pyo3_crossings_per_gen": m["pyo3_crossings_per_gen"],
        "notes": notes,
    }
    need_header = not RESULTS_CSV.exists()
    with RESULTS_CSV.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if need_header:
            w.writeheader()
        w.writerow(row)


def show() -> None:
    if not RESULTS_CSV.exists():
        print("no results yet")
        return
    with RESULTS_CSV.open() as f:
        for line in f:
            print(line.rstrip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="baseline", help="row label")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--notes", default="")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    if args.show:
        show()
        return 0

    cfg = _bench_config()
    print(f"bench: phase={args.phase} pop={cfg.pop_size} task={cfg.task} "
          f"arm={cfg.arm} alphabet={cfg.alphabet} reps={args.reps}")
    m = measure(cfg, args.reps)
    print(f"  pop_eval_sec:          {m['pop_eval_sec']:.4f}")
    print(f"  mutate_sec:            {m['mutate_sec']:.4f}")
    print(f"  gen_total_sec:         {m['gen_total_sec']:.4f}")
    print(f"  pyo3_crossings_per_gen:{m['pyo3_crossings_per_gen']}")
    append_row(args.phase, cfg, m, notes=args.notes)
    print(f"  → appended to {RESULTS_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
