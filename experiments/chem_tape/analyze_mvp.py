#!/usr/bin/env python3
"""Analyze the MVP sweep under the differential-outcome framing (arch §Layer 9).

For each (task, arm), reports:
  - solve count (runs reaching best_fitness == 1.0 on training set)
  - generations-to-solve (first gen hitting 1.0) — median, mean, range, IQR
  - holdout fitness — median, min, max
  - final-gen mean_longest_run (diagnostic: did the population's active runs
    lengthen over training? expected to diverge more for Arm B on sum-gt-10)

Prints a formatted table keyed by task, plus the Arm A↔B differential per task.
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def gens_to_solve(history_csv: Path) -> int | None:
    with open(history_csv) as f:
        for row in csv.DictReader(f):
            if float(row["best_fitness"]) >= 1.0:
                return int(row["generation"])
    return None


def final_diagnostics(history_csv: Path) -> tuple[float | None, int | None]:
    """Return (mean_longest_run_final, max_longest_run_final) from the last
    generation row, or (None, None) if the column is missing (old runs)."""
    last = None
    with open(history_csv) as f:
        for row in csv.DictReader(f):
            last = row
    if last is None or "mean_longest_run" not in last:
        return None, None
    return float(last["mean_longest_run"]), int(last["max_longest_run"])


def gather(root: Path) -> list[dict]:
    rows = []
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        r_path = d / "result.json"
        h_path = d / "history.csv"
        if not r_path.exists() or not h_path.exists():
            continue
        r = json.loads(r_path.read_text())
        gts = gens_to_solve(h_path)
        mlr_final, max_final = final_diagnostics(h_path)
        rows.append({
            "task": r["task"],
            "arm": r["arm"],
            "seed": r["seed"],
            "train": r["best_fitness"],
            "hold": r.get("holdout_fitness"),
            "gens_to_solve": gts,
            "final_mean_run": mlr_final,
            "final_max_run": max_final,
            "elapsed": r["elapsed_sec"],
        })
    return rows


def _fmt_gens(vs: list[int]) -> str:
    if not vs:
        return "(none solved)"
    med = statistics.median(vs)
    mn = min(vs)
    mx = max(vs)
    return f"median={med:>5.1f}  min={mn:>3d}  max={mx:>3d}"


def summarize(rows: list[dict]) -> None:
    by_task: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_task[r["task"]][r["arm"]].append(r)

    tasks = ["count_r", "has_upper", "sum_gt_10"]
    print("\n================ PER-TASK RESULTS ================\n")
    for t in tasks:
        if t not in by_task:
            continue
        print(f"▶ {t}")
        for arm in ("A", "B"):
            sub = by_task[t][arm]
            n = len(sub)
            solved = [r for r in sub if r["gens_to_solve"] is not None]
            gens = [r["gens_to_solve"] for r in solved]
            holds = [r["hold"] for r in sub if r["hold"] is not None]
            runs = [r["final_mean_run"] for r in sub if r["final_mean_run"] is not None]
            best_runs = [r["final_max_run"] for r in sub if r["final_max_run"] is not None]
            print(f"  Arm {arm} (n={n}): solved {len(solved)}/{n}  {_fmt_gens(gens)}")
            if holds:
                print(
                    f"         holdout: median={statistics.median(holds):.3f}"
                    f"  min={min(holds):.3f}  max={max(holds):.3f}"
                )
            if runs:
                print(
                    f"         final mean longest-run: "
                    f"median-across-seeds={statistics.median(runs):.2f}"
                    f"  (max-across-pop median={statistics.median(best_runs):.1f})"
                )
        # Differential: B - A on gens-to-solve.
        a_solved = [
            r["gens_to_solve"] for r in by_task[t]["A"] if r["gens_to_solve"] is not None
        ]
        b_solved = [
            r["gens_to_solve"] for r in by_task[t]["B"] if r["gens_to_solve"] is not None
        ]
        if a_solved and b_solved:
            diff = statistics.median(b_solved) - statistics.median(a_solved)
            sign = "B faster" if diff < 0 else "B slower" if diff > 0 else "tie"
            print(f"  Δ(median gens, B−A) = {diff:+.1f} → {sign}")
        elif a_solved and not b_solved:
            print("  Δ: B never solved; A did")
        elif b_solved and not a_solved:
            print("  Δ: A never solved; B did")
        print()

    print("================ DIFFERENTIAL PATTERN (arch §Layer 9) ================\n")
    print("  Expected positive signal: B < A on count_r, has_upper; B > A on sum_gt_10.\n")
    for t in tasks:
        if t not in by_task:
            continue
        a = by_task[t]["A"]
        b = by_task[t]["B"]
        a_solve = len([r for r in a if r["gens_to_solve"] is not None])
        b_solve = len([r for r in b if r["gens_to_solve"] is not None])
        # Prefer gens-to-solve comparison; fall back to best_fitness median.
        a_g = [r["gens_to_solve"] for r in a if r["gens_to_solve"] is not None]
        b_g = [r["gens_to_solve"] for r in b if r["gens_to_solve"] is not None]
        if a_g and b_g:
            a_m = statistics.median(a_g)
            b_m = statistics.median(b_g)
            verdict = (
                "B > A (faster)" if b_m < a_m * 0.9
                else "B < A (slower)" if b_m > a_m * 1.1
                else "B ≈ A"
            )
            print(
                f"  {t:10s}  solved A={a_solve}/10 B={b_solve}/10   "
                f"median gens A={a_m:.1f} B={b_m:.1f}   →   {verdict}"
            )
        else:
            a_f = statistics.median([r["train"] for r in a])
            b_f = statistics.median([r["train"] for r in b])
            verdict = (
                "B > A" if b_f > a_f + 0.02
                else "B < A" if b_f < a_f - 0.02
                else "B ≈ A"
            )
            print(
                f"  {t:10s}  solved A={a_solve}/10 B={b_solve}/10   "
                f"median best-fitness A={a_f:.3f} B={b_f:.3f}   →   {verdict}"
            )


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("experiments/chem_tape/output/mvp")
    rows = gather(root)
    print(f"Loaded {len(rows)} runs from {root}")
    summarize(rows)
