"""Run counts under variation alone, no selection (map-bias notebook §25).

A random tagged population (tape 64) reproduces with uniform parent choice: crossover
at rate 0.7 (v1, v2, or off), then mutate_batch at mu 0.015 — the §19/§24 operators.
Every `every`-th generation (default 10) records the leftmost run census and, for that
generation's reproduction step only (not averaged over the interval; the last row has
none), the mean change in run count each operator causes:
- crossover: runs(child) - runs(parent A) for the cut and homologous events together;
- paired assembly: on each crossover the same proposal (same cloned random state) is
  also assembled by v1 and by v2, so runs(v2 child) - runs(v1 child) is the assembly
  difference alone. The populations of the two variants still diverge (v2 draws extra
  random numbers when it deletes runs), so only this column is paired;
- mutation: runs(after) - runs(before).
Also the share of genomes with no run and the share of children of a run-free first
parent that have a run after mutation (recovery).

Usage: uv run python experiments/chem_tape/crossover_drift.py [--gens 300] [--seeds 3]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

from folding_evolution.chem_tape import tagged


def nruns(g) -> int:
    return len(tagged.parse_runs(g))


def drift(variant: str, seed: int, gens: int, P: int = 1024, L: int = 64, mu: float = 0.015,
          px: float = 0.7, every: int = 10) -> list[dict]:
    rng = random.Random(seed)
    gen = np.random.default_rng(seed)
    pop = [tagged.random_genotype(L, rng) for _ in range(P)]
    rows = []
    for g in range(gens + 1):
        record = g % every == 0 or g == gens
        if record:
            c = np.array([tagged.run_census(x, "leftmost") for x in pop], dtype=float)
            row = {"variant": variant, "seed": seed, "gen": g, "runs": c[:, 0].mean(),
                   "no_runs": (c[:, 0] == 0).mean(), "output_runs": c[:, 1].mean(),
                   "unread": (c[:, 0] - c[:, 2]).mean(), "tail_nops": c[:, 4].mean(),
                   "runs_hist": np.bincount(c[:, 0].astype(int), minlength=12)[:12].tolist()}
        if g == gens:
            rows.append(row)
            break
        children, a_runs, dx, dpair = [], [], [], []
        for _ in range(P):
            a = pop[rng.randrange(P)]
            ra = nruns(a)
            if variant != "off" and rng.random() < px:
                b = pop[rng.randrange(P)]
                state = rng.getstate()
                paired = []
                for v in ("v1", "v2"):
                    r2 = random.Random()
                    r2.setstate(state)
                    paired.append(nruns(tagged.crossover(a, b, r2, v)))
                dpair.append(paired[1] - paired[0])
                ch = tagged.crossover(a, b, rng, variant)
                dx.append(nruns(ch) - ra)
            else:
                ch = a.copy()
            children.append(ch)
            a_runs.append(ra)
        before = np.array([nruns(x) for x in children])
        pop = list(tagged.mutate_batch(np.stack(children), mu, gen))
        after = np.array([nruns(x) for x in pop])
        if record:
            a_runs = np.array(a_runs)
            free = a_runs == 0
            row.update({"d_crossover": float(np.mean(dx)) if dx else 0.0,
                        "d_v2_minus_v1": float(np.mean(dpair)) if dpair else 0.0,
                        "d_mutation": float((after - before).mean()),
                        "recovery": float((after[free] > 0).mean()) if free.any() else None})
            rows.append(row)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=300)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    rows = [r for v in ("v1", "v2", "off") for s in range(args.seeds) for r in drift(v, s, args.gens)]
    if args.out:
        args.out.write_text(json.dumps(rows))
    print("| variant | gen | runs | no runs | output runs | unread | tail NOPs | Δruns crossover | v2−v1 same proposal | Δruns mutation | recovery |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for v in ("v1", "v2", "off"):
        for g in sorted({r["gen"] for r in rows}):
            rs = [r for r in rows if r["variant"] == v and r["gen"] == g]
            if g not in (0, 10, 20, 50, 100, 200, args.gens):
                continue
            m = lambda k: np.mean([r[k] for r in rs if r.get(k) is not None]) if any(r.get(k) is not None for r in rs) else float("nan")  # noqa: E731
            print(f"| {v} | {g} | {m('runs'):.2f} | {m('no_runs'):.2f} | {m('output_runs'):.2f} | {m('unread'):.2f} | "
                  f"{m('tail_nops'):.1f} | {m('d_crossover'):+.3f} | {m('d_v2_minus_v1'):+.3f} | {m('d_mutation'):+.3f} | {m('recovery'):.2f} |")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
