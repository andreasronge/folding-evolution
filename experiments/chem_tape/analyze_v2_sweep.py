#!/usr/bin/env python3
"""Post-hoc analyzer for §v2.4-alt / §v2.4-proxy / §v2.6 sweeps.

Each `result.json` already contains `cross_task_fitness` with
per-task train + holdout scores for the best-of-run genotype (written by
evolve.py for task-alternating runs). This script:

  * Tabulates per-seed BOTH-solve for alternation sweeps (BOTH = both
    cross-task fitnesses ≥ 0.999). For single-task sweeps (`v2_4_proxy`)
    it just tabulates solve and holdout gap.
  * Summarises flip-event cost histograms (pre_flip_best vs post_flip_best).
  * Writes a `summary.json` next to the sweep's output directory and prints
    a human-readable table.
  * Optional `--plot`: produces `fitness_trajectories.png` overlaying all 20
    seeds' best-fitness curves from `history.csv`, with flip markers.

Usage:
    python experiments/chem_tape/analyze_v2_sweep.py <sweep_name> [--plot]
    python experiments/chem_tape/analyze_v2_sweep.py --all
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_ROOT = REPO_ROOT / "experiments" / "chem_tape" / "output"
SOLVE_EPS = 0.999

V2_SWEEPS = [
    "v2_4_alt",
    "v2_4_proxy",
    "v2_6_pair1",
    "v2_6_pair2",
    "v2_6_pair3",
]


@dataclass
class SeedRow:
    seed: int
    task: str
    best_fitness: float
    holdout_fitness: float | None
    gap: float | None
    per_task: dict[str, dict[str, float | None]] | None
    flip_events: list[dict]


def load_seed_rows(sweep: str) -> list[SeedRow]:
    sweep_dir = OUTPUT_ROOT / sweep
    rows: list[SeedRow] = []
    for d in sorted(sweep_dir.iterdir()):
        rp = d / "result.json"
        if not rp.exists():
            continue
        r = json.loads(rp.read_text())
        rows.append(
            SeedRow(
                seed=r["seed"],
                task=r["task"],
                best_fitness=float(r["best_fitness"]),
                holdout_fitness=r.get("holdout_fitness"),
                gap=r.get("train_holdout_gap"),
                per_task=r.get("cross_task_fitness"),
                flip_events=r.get("flip_events") or [],
            )
        )
    rows.sort(key=lambda x: x.seed)
    return rows


def analyse_sweep(sweep: str) -> dict:
    rows = load_seed_rows(sweep)
    n = len(rows)
    is_alt = bool(rows and rows[0].per_task)
    out: dict = {"sweep": sweep, "n": n, "alternation": is_alt}

    if is_alt:
        task_names = sorted(next((r.per_task for r in rows if r.per_task), {}).keys())
        per_task_solve: dict[str, int] = {t: 0 for t in task_names}
        per_task_train: dict[str, list[float]] = {t: [] for t in task_names}
        per_task_hold: dict[str, list[float]] = {t: [] for t in task_names}
        per_task_gap: dict[str, list[float]] = {t: [] for t in task_names}
        both_solve = 0
        for r in rows:
            if r.per_task is None:
                continue
            all_solve = True
            for t in task_names:
                tr = r.per_task[t]["fitness"]
                hd = r.per_task[t]["holdout_fitness"]
                gp = r.per_task[t]["gap"]
                per_task_train[t].append(tr)
                if hd is not None:
                    per_task_hold[t].append(hd)
                if gp is not None:
                    per_task_gap[t].append(gp)
                if tr >= SOLVE_EPS:
                    per_task_solve[t] += 1
                else:
                    all_solve = False
            if all_solve:
                both_solve += 1
        fmin = min(per_task_solve.values()) if per_task_solve else 0
        out["task_names"] = task_names
        out["per_task_solve"] = per_task_solve
        out["Fmin"] = fmin
        out["BOTH_solve"] = both_solve
        out["per_task_mean_train"] = {t: statistics.mean(v) if v else None for t, v in per_task_train.items()}
        out["per_task_mean_hold"] = {t: statistics.mean(v) if v else None for t, v in per_task_hold.items()}
        out["per_task_max_abs_gap"] = {t: max((abs(x) for x in v), default=0.0) for t, v in per_task_gap.items()}
    else:
        solved = sum(1 for r in rows if r.best_fitness >= SOLVE_EPS)
        out["solve"] = solved
        out["mean_train"] = statistics.mean(r.best_fitness for r in rows) if rows else None
        out["mean_hold"] = (
            statistics.mean(r.holdout_fitness for r in rows if r.holdout_fitness is not None)
            if rows else None
        )
        out["max_abs_gap"] = max((abs(r.gap) for r in rows if r.gap is not None), default=0.0)

    # Flip-event analysis (alternation only).
    if is_alt:
        zero_cost = 0
        total_flips = 0
        recoveries: list[int] = []
        costs: list[float] = []
        for r in rows:
            for fe in r.flip_events:
                total_flips += 1
                pre = fe["pre_flip_best"]
                post = fe["post_flip_best"]
                if pre >= SOLVE_EPS and post >= SOLVE_EPS:
                    zero_cost += 1
                costs.append(pre - post)
                if fe.get("recovery_gen", -1) > 0 and fe["flip_gen"] >= 0:
                    recoveries.append(fe["recovery_gen"] - fe["flip_gen"])
        out["flip_events"] = {
            "total": total_flips,
            "zero_cost": zero_cost,
            "mean_cost": statistics.mean(costs) if costs else None,
            "max_cost": max(costs, default=0.0),
            "median_recovery_gens": statistics.median(recoveries) if recoveries else None,
        }

    out["per_seed"] = [
        {
            "seed": r.seed,
            "best": r.best_fitness,
            "hold": r.holdout_fitness,
            "gap": r.gap,
            "per_task": r.per_task,
        }
        for r in rows
    ]
    return out


def print_summary(s: dict) -> None:
    sweep = s["sweep"]
    print(f"\n=== {sweep}  n={s['n']}  alternation={s['alternation']} ===")
    if s["alternation"]:
        for t in s["task_names"]:
            hit = s["per_task_solve"][t]
            mt = s["per_task_mean_train"][t]
            mh = s["per_task_mean_hold"][t]
            gp = s["per_task_max_abs_gap"][t]
            print(f"  {t:48s} solve={hit:>2}/{s['n']}  mean train={mt:.3f}  hold={mh:.3f}  max|gap|={gp:.4f}")
        print(f"  BOTH solve = {s['BOTH_solve']}/{s['n']}    Fmin = {s['Fmin']}")
        fe = s["flip_events"]
        print(f"  flips: {fe['total']} total, {fe['zero_cost']} zero-cost, mean cost={fe['mean_cost']:.3f}, max cost={fe['max_cost']:.3f}")
    else:
        print(f"  solve={s['solve']}/{s['n']}  mean train={s['mean_train']:.3f}  mean hold={s['mean_hold']:.3f}  max|gap|={s['max_abs_gap']:.4f}")


def plot_trajectories(sweep: str, out_path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sweep_dir = OUTPUT_ROOT / sweep
    fig, ax = plt.subplots(figsize=(11, 6))
    for d in sorted(sweep_dir.iterdir()):
        hc = d / "history.csv"
        rp = d / "result.json"
        if not hc.exists() or not rp.exists():
            continue
        seed = json.loads(rp.read_text())["seed"]
        gens: list[int] = []
        best: list[float] = []
        with open(hc) as f:
            for row in csv.DictReader(f):
                gens.append(int(row["generation"]))
                best.append(float(row["best_fitness"]))
        ax.plot(gens, best, alpha=0.35, linewidth=0.9, label=f"s{seed}")
    # Task-alternating boundaries at period=300 (standard across these sweeps).
    for x in range(300, 1501, 300):
        ax.axvline(x, color="gray", alpha=0.25, linewidth=0.7, linestyle=":")
    ax.set_xlabel("generation")
    ax.set_ylabel("best fitness")
    ax.set_title(f"{sweep} — per-seed best-fitness trajectories (flips at gens 300/600/900/1200/1500)")
    ax.set_ylim(0.4, 1.02)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    print(f"  plot → {out_path}")
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep", nargs="?", help="sweep name (omit with --all)")
    ap.add_argument("--all", action="store_true", help="analyse all v2 sweeps")
    ap.add_argument("--plot", action="store_true", help="write fitness_trajectories.png")
    ap.add_argument("--write-json", action="store_true", help="write summary.json into sweep dir")
    args = ap.parse_args()

    targets = V2_SWEEPS if args.all else ([args.sweep] if args.sweep else [])
    if not targets:
        ap.error("provide a sweep name or --all")

    for sw in targets:
        sw_dir = OUTPUT_ROOT / sw
        if not sw_dir.exists():
            print(f"  skip: {sw} (no output dir)")
            continue
        s = analyse_sweep(sw)
        print_summary(s)
        if args.write_json:
            (sw_dir / "summary.json").write_text(json.dumps(s, indent=2))
        if args.plot:
            plot_trajectories(sw, sw_dir / "fitness_trajectories.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
