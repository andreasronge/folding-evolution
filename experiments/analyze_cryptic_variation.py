"""
Post-hoc analysis of 1.15 cryptic variation assay.

Reads experiments/output/cryptic_full/cryptic_variation_raw.json and
reports sharper metrics than the original summary, without rerunning:

  - Fitness at checkpoints 10, 20, 40, 80 gens
  - AUC of the best-fitness trajectory per assay (captures sustained
    vs plateau-from-start dynamics)
  - Recovery slope over the first 20 gens (early-adaptation speed)
  - Endpoint fitness distributions (full per-seed list)
  - Hit counts at multiple fitness thresholds

Rationale: the original summary reported only final_best and
time-to-first-threshold. The per-seed trajectories in the JSON
let us read the *shape* of adaptation, which is where the real
Pareto signal is most apparent.
"""

import json
import statistics
from pathlib import Path


def load_results(path):
    with open(path) as f:
        return json.load(f)


def trajectory_metrics(traj, checkpoints=(10, 20, 40, 80)):
    """Compute metrics from a best-fitness-so-far trajectory."""
    n = len(traj)
    checkpoint_fits = {c: traj[min(c, n - 1)] for c in checkpoints}

    # AUC: average of best_so_far over all gens (trapezoidal, simple mean)
    auc = sum(traj) / n

    # Recovery slope: linear fit over first 20 gens (or all if shorter)
    early_n = min(20, n)
    xs = list(range(early_n))
    ys = traj[:early_n]
    mean_x = sum(xs) / early_n
    mean_y = sum(ys) / early_n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den = sum((x - mean_x) ** 2 for x in xs)
    slope = num / den if den > 0 else 0.0

    return {
        "checkpoint_fits": checkpoint_fits,
        "auc": auc,
        "early_slope": slope,
        "final": traj[-1],
    }


def summarize_condition(seed_dict, snap_gen, task_name, checkpoints):
    """Aggregate per-seed trajectory metrics for one (condition, snap, task)."""
    metrics = []
    finals = []
    start_s5 = []
    start_g5 = []
    for seed, sr in seed_dict.items():
        assay = sr["assays"][str(snap_gen)][task_name]
        m = trajectory_metrics(assay["best_trajectory"], checkpoints)
        metrics.append(m)
        finals.append(assay["final_best_fitness"])
        start_s5.append(assay["starting_pop_stats"]["S5+"])
        start_g5.append(assay["starting_pop_stats"]["G5+"])

    n = len(metrics)
    agg = {"n": n, "finals": finals, "start_s5": start_s5, "start_g5": start_g5}
    agg["mean_auc"] = sum(m["auc"] for m in metrics) / n
    agg["median_auc"] = statistics.median(m["auc"] for m in metrics)
    agg["mean_early_slope"] = sum(m["early_slope"] for m in metrics) / n
    for c in checkpoints:
        vals = [m["checkpoint_fits"][c] for m in metrics]
        agg[f"mean_at_{c}"] = sum(vals) / n
        agg[f"median_at_{c}"] = statistics.median(vals)
    return agg


def hit_counts(finals, thresholds):
    return {t: sum(1 for f in finals if f >= t) for t in thresholds}


def main():
    raw_path = Path(__file__).parent / "output" / "cryptic_full" / "cryptic_variation_raw.json"
    if not raw_path.exists():
        print(f"ERROR: no raw file at {raw_path}")
        return

    results = load_results(raw_path)
    checkpoints = (10, 20, 40, 80)
    thresholds = (0.4, 0.6, 0.7, 0.8, 0.9)

    snapshots = [200, 300]
    tasks = ["T_near_price600", "T_far_amount300"]
    conditions = ["A_continuous", "B_scaffold", "C_structural"]

    print("=" * 80)
    print("1.15 CRYPTIC VARIATION — Post-hoc trajectory analysis")
    print("=" * 80)

    for task in tasks:
        print(f"\n{'=' * 80}")
        print(f"Task: {task}")
        print(f"{'=' * 80}")
        for snap in snapshots:
            print(f"\n--- Snapshot gen = {snap} ---")
            header = f"  {'Cond':<14}"
            header += f"{'AUC':<9}{'slope×20':<10}"
            for c in checkpoints:
                header += f"{'@'+str(c):<8}"
            for t in thresholds:
                header += f"{'≥'+str(t):<7}"
            print(header)

            for cond in conditions:
                agg = summarize_condition(results[cond], snap, task, checkpoints)
                hits = hit_counts(agg["finals"], thresholds)
                row = f"  {cond:<14}"
                row += f"{agg['mean_auc']:.3f}    "
                row += f"{agg['mean_early_slope']*20:.3f}     "
                for c in checkpoints:
                    row += f"{agg['mean_at_'+str(c)]:.3f}   "
                for t in thresholds:
                    row += f"{hits[t]:>2}/{agg['n']:<3}"
                print(row)

            # Per-seed final distributions
            print(f"\n  Endpoint distributions (sorted):")
            for cond in conditions:
                agg = summarize_condition(results[cond], snap, task, checkpoints)
                sorted_finals = sorted(agg["finals"])
                vals_str = " ".join(f"{f:.3f}" for f in sorted_finals)
                print(f"    {cond:<14} [{vals_str}]")

    # ==================================================================
    # Cross-comparison: Pareto advantage over continuous at each checkpoint
    # ==================================================================
    print("\n" + "=" * 80)
    print("PARETO ADVANTAGE (B or C mean at checkpoint) − (A mean at checkpoint)")
    print("=" * 80)
    print(f"\n{'Task':<20}{'Snap':<6}{'Cond':<14}" +
          "".join(f"{'Δ@'+str(c):<10}" for c in checkpoints) +
          f"{'ΔAUC':<10}{'Δslope':<10}")
    for task in tasks:
        for snap in snapshots:
            a = summarize_condition(results["A_continuous"], snap, task, checkpoints)
            for cond in ["B_scaffold", "C_structural"]:
                x = summarize_condition(results[cond], snap, task, checkpoints)
                row = f"{task:<20}{snap:<6}{cond:<14}"
                for c in checkpoints:
                    delta = x[f"mean_at_{c}"] - a[f"mean_at_{c}"]
                    row += f"{delta:+.3f}    "
                row += f"{x['mean_auc']-a['mean_auc']:+.3f}    "
                row += f"{(x['mean_early_slope']-a['mean_early_slope'])*20:+.3f}"
                print(row)

    # ==================================================================
    # Ceiling access (≥0.8 hit-rate) as primary endpoint
    # ==================================================================
    print("\n" + "=" * 80)
    print("CEILING ACCESS (fraction of seeds reaching final ≥0.8)")
    print("=" * 80)
    print(f"\n{'Task':<20}{'Snap':<6}" +
          "".join(f"{c:<18}" for c in conditions))
    for task in tasks:
        for snap in snapshots:
            row = f"{task:<20}{snap:<6}"
            for cond in conditions:
                agg = summarize_condition(results[cond], snap, task, checkpoints)
                h = hit_counts(agg["finals"], (0.8,))[0.8]
                row += f"{h}/{agg['n']} ({h/agg['n']*100:.1f}%)   "
            print(row)


if __name__ == "__main__":
    main()
