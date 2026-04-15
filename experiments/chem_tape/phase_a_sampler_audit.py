"""Phase A sampler-audit measurement (no GP).

Used by §v2.8 (prereg_v2_8_integer_6token.md) and §v2.6'-Pair2
(prereg_v2_6_pair2_redesigned.md). Computes per-seed class balance,
proxy accuracies, and label viability on candidate task pairs.
Reports PASS/FAIL per the audit criteria in each prereg.

Per principle 20: report on representative seeds (default {0, 1, 2}),
not seed-0 alone. Each task is tested independently.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path

from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.tasks import build_task


# Proxies per prereg. Each callable takes an input (intlist) and returns 0/1.
PROXY_DEFINITIONS: dict[str, Callable[[tuple[int, ...]], int]] = {
    "constant_0": lambda xs: 0,
    "constant_1": lambda xs: 1,
    "sum_gt_5": lambda xs: 1 if sum(xs) > 5 else 0,
    "sum_gt_10": lambda xs: 1 if sum(xs) > 10 else 0,
    "sum_gt_15": lambda xs: 1 if sum(xs) > 15 else 0,
    "sum_gt_20": lambda xs: 1 if sum(xs) > 20 else 0,
    "sum_gt_25": lambda xs: 1 if sum(xs) > 25 else 0,
    "sum_gt_30": lambda xs: 1 if sum(xs) > 30 else 0,
    "max_gt_5": lambda xs: 1 if max(xs, default=0) > 5 else 0,
    "max_gt_7": lambda xs: 1 if max(xs, default=0) > 7 else 0,
    "max_gt_9": lambda xs: 1 if max(xs, default=0) > 9 else 0,
    "max_gt_11": lambda xs: 1 if max(xs, default=0) > 11 else 0,
    "any_cell_gt_5": lambda xs: 1 if any(x > 5 for x in xs) else 0,
    "any_cell_gt_7": lambda xs: 1 if any(x > 7 for x in xs) else 0,
    "any_cell_gt_9": lambda xs: 1 if any(x > 9 for x in xs) else 0,
    "any_cell_gt_11": lambda xs: 1 if any(x > 11 for x in xs) else 0,
}


def audit_task(task_name: str, seed: int, n_examples: int = 64) -> dict:
    cfg = ChemTapeConfig(
        alphabet="v2_probe",
        task=task_name,
        n_examples=n_examples,
        holdout_size=256,
        pop_size=8,
        generations=2,
        seed=seed,
    )
    task = build_task(cfg, seed)
    inputs = task.inputs
    labels = list(task.labels)
    n = len(labels)
    positives = sum(labels)
    balance = positives / n

    proxy_accuracies = {}
    for name, fn in PROXY_DEFINITIONS.items():
        preds = [fn(tuple(inp) if not isinstance(inp, tuple) else inp) for inp in inputs]
        correct = sum(1 for p, ell in zip(preds, labels) if p == ell)
        proxy_accuracies[name] = correct / n

    max_proxy = max(proxy_accuracies.items(), key=lambda kv: kv[1])
    return {
        "task": task_name,
        "seed": seed,
        "n_examples": n,
        "positives": positives,
        "balance": balance,
        "max_proxy_name": max_proxy[0],
        "max_proxy_accuracy": max_proxy[1],
        "proxy_accuracies": proxy_accuracies,
    }


def evaluate_audit(per_seed_results: list[dict], max_proxy_threshold: float = 0.90) -> dict:
    """Apply the audit pass criteria from the §v2.8 / §v2.6'-Pair2 preregs."""
    failures = []
    for r in per_seed_results:
        if not (0.40 <= r["balance"] <= 0.60):
            failures.append(
                f"seed={r['seed']}: class balance {r['balance']:.3f} outside [0.40, 0.60]"
            )
        if r["max_proxy_accuracy"] >= max_proxy_threshold:
            failures.append(
                f"seed={r['seed']}: max proxy '{r['max_proxy_name']}' "
                f"= {r['max_proxy_accuracy']:.3f} >= {max_proxy_threshold:.2f} threshold"
            )
        if r["positives"] < 5:
            failures.append(
                f"seed={r['seed']}: positives {r['positives']} < 5 (label viability)"
            )
    return {"verdict": "PASS" if not failures else "FAIL", "failures": failures}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True, help="Comma-separated task names.")
    ap.add_argument("--seeds", default="0,1,2", help="Comma-separated seed list.")
    ap.add_argument("--max-proxy-threshold", type=float, default=0.90)
    ap.add_argument("--output", type=Path, default=Path("phase_a_audit.json"))
    args = ap.parse_args()

    tasks = args.tasks.split(",")
    seeds = [int(s) for s in args.seeds.split(",")]
    all_results = {}
    overall_pass = True
    for task_name in tasks:
        per_seed = [audit_task(task_name.strip(), s) for s in seeds]
        verdict = evaluate_audit(per_seed, max_proxy_threshold=args.max_proxy_threshold)
        all_results[task_name] = {"per_seed": per_seed, "verdict": verdict}
        if verdict["verdict"] != "PASS":
            overall_pass = False
        print(f"\n=== {task_name} ===")
        for r in per_seed:
            print(
                f"  seed={r['seed']}: balance={r['balance']:.3f}  "
                f"max_proxy={r['max_proxy_name']}={r['max_proxy_accuracy']:.3f}  "
                f"positives={r['positives']}"
            )
        print(f"  VERDICT: {verdict['verdict']}")
        for f in verdict["failures"]:
            print(f"    - {f}")

    args.output.write_text(json.dumps(all_results, indent=2, default=lambda o: int(o) if hasattr(o, "__index__") else float(o)))
    print(f"\nWritten: {args.output}")
    print(f"OVERALL: {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
