"""Start-cluster and jointly shared-seed inference for 0811."""

import math
import numpy as np

from experiments.chem_tape.map_learning import log_cost


def classify(interval):
    low, high = interval
    return "faster" if low > 1 else "no practical gain" if high < 1.25 else "unresolved"


def contrast(
    rows, groups_a, groups_b, cells, cap=524288, replicates=10000, seed=818000000
):
    """One group per inherited start; retain all continuations within a group.

    Average continuations inside each start before resampling starts. A seed
    draw is shared by every map and every fixed cell stratum, preserving the
    experiment's shared case/initialization/variation streams. Frozen G is
    replicated in groups for pairing, never treated as independent G runs.
    """
    index = {(r["arm"], r["cell"], r["seed"]): r for r in rows}
    keys = {(a, c) for g in groups_a + groups_b for a in g for c in cells}
    seed_sets = [{s for arm, cell, s in index if (arm, cell) == key} for key in keys]
    seeds = sorted(set.intersection(*seed_sets))
    if not seeds or any(s != set(seeds) for s in seed_sets):
        raise ValueError("missing or unpaired contrast observations")
    if len(groups_a) != len(groups_b):
        raise ValueError("unmatched start clusters")

    def matrix(groups):
        return np.array(
            [
                np.mean(
                    [
                        [[log_cost(index[a, c, s], cap) for s in seeds] for c in cells]
                        for a in g
                    ],
                    axis=0,
                )
                for g in groups
            ]
        )

    d = matrix(groups_b) - matrix(groups_a)
    n, _, ns = d.shape
    point = float(d.mean())
    rng_cluster = np.random.default_rng([seed, 0])
    rng_seed = np.random.default_rng([seed, 1])
    boot = np.empty(replicates)
    # Chunked vectorization avoids allocating replicate × map × cell × seed.
    fixed_cells = d.mean(1)
    for offset in range(0, replicates, 100):
        count = min(100, replicates - offset)
        clusters = rng_cluster.integers(n, size=(count, n))
        sampled_seeds = rng_seed.integers(ns, size=(count, ns))
        for j in range(count):
            boot[offset + j] = fixed_cells[clusters[j]][:, sampled_seeds[j]].mean()
    ci = (2 ** np.quantile(boot, [0.025, 0.975])).tolist()
    cluster_sd = float(d.mean((1, 2)).std(ddof=1)) if n > 1 else None
    seed_se = float(d.mean((0, 1)).std(ddof=1) / np.sqrt(ns)) if ns > 1 else None
    # Normal approximation keeps shared-seed uncertainty instead of treating
    # added continuations as new independent inherited starts.
    target_se = np.log2(1.25) / 1.96
    needed = None
    if cluster_sd is not None and seed_se is not None and seed_se < target_se:
        needed = max(n, math.ceil(cluster_sd**2 / (target_se**2 - seed_se**2)))

    def starts_needed(distance):
        se = distance / 1.96
        if cluster_sd is None or seed_se is None or se <= seed_se:
            return None
        return max(n, math.ceil(cluster_sd**2 / (se**2 - seed_se**2)))

    faster_n = starts_needed(point) if point > 0 else None
    bounded_n = starts_needed(np.log2(1.25) - point) if point < np.log2(1.25) else None
    return dict(
        ratio=float(2**point),
        mean_log2_difference=point,
        interval_95=ci,
        classification=classify(ci),
        point_reaches_1_25=bool(2**point >= 1.25),
        lower_bound_exceeds_1_25=bool(ci[0] > 1.25),
        start_clusters=n,
        continuations_per_start=[len(g) for g in groups_a],
        paired_seeds=ns,
        cells=cells,
        cap=cap,
        between_start_sd=cluster_sd,
        shared_seed_se=seed_se,
        approximate_starts_for_null_bound_1_25=needed,
        approximate_starts_for_resolved_observed_gain=faster_n,
        approximate_starts_for_observed_bound_1_25=bounded_n,
        approximate_pairs_at_two_continuations=dict(
            faster=2 * faster_n if faster_n else None,
            no_practical_gain=2 * bounded_n if bounded_n else None,
        ),
        sizing_scope="normal sensitivity; added continuations are not added starts; null if retained seed term alone exceeds precision target",
        bootstrap_replicates=replicates,
    )


def outcome(contrasts):
    h = [contrasts[f"holdout{i}:R/M+"]["classification"] for i in range(2)]
    t = contrasts["training524:R/M+"]["classification"]
    if h == ["faster"] * 2:
        return dict(
            row=1,
            meaning="Allowing contextual moves improves transfer in this screened PA family; inspect residual ablation and practical scale.",
        )
    if t == "faster" and h == ["no practical gain"] * 2:
        return dict(
            row=2,
            meaning="Training improves; each holdout gain is bounded below 1.25x, not proven absent.",
        )
    if t == "no practical gain" and h == ["no practical gain"] * 2:
        a = contrasts["training524:R/R_abl"]["classification"]
        return dict(
            row=3,
            meaning="No practical incremental gain at this budget/operator.",
            residual_reading="Resolved residual dependency despite displaced token steps"
            if a == "faster"
            else f"No resolved residual benefit; ablation {a}.",
        )
    return dict(
        row=4,
        meaning="Unresolved: inspect all intervals, start/seed spread and actual pair coverage.",
    )


def report(
    rows,
    split,
    off_cells,
    completed_pairs,
    planned_pairs,
    complete,
    gate_failed,
    harness_mismatch=False,
    replicates=10000,
    seed=818000000,
    test_seed_counts=(50, 200, 50),
):
    result = dict(
        complete=complete,
        completed_pairs=completed_pairs,
        planned_pairs=planned_pairs,
        outcome=None,
        contrasts={},
        map_costs={},
        between_pair_differences={},
        scope="Learned procedures on a screened PA bank; residual ablation is a dependency check, not unique contextual causation. No mechanism/family-specificity claim.",
    )
    if harness_mismatch:
        result["outcome"] = dict(
            row=0, meaning="Harness mismatch: interpretation stopped."
        )
        return result
    expected_maps = ["G"] + [f"M{k}" for k in range(1, 7)]
    expected_maps += [
        f"{a}{p['start']}{p['rep']}"
        for p in completed_pairs
        for a in ("M+", "R", "R_abl")
    ]
    counts = {}
    for a in expected_maps:
        for label, cells, n in [
            ("training", split["training"], test_seed_counts[0]),
            ("holdouts", split["holdouts"], test_seed_counts[1]),
        ]:
            for c in cells:
                rs = [r for r in rows if r["arm"] == a and r["cell"] == c]
                counts[f"{a}:{c}"] = dict(
                    expected=n,
                    actual=len(rs),
                    unique_seeds=len({r["seed"] for r in rs}),
                    set=label,
                )
    result["test_counts"] = counts
    pair_coverage = (
        len({(p["start"], p["rep"]) for p in completed_pairs}) == planned_pairs
    )
    result["complete"] = (
        complete
        and (gate_failed or pair_coverage)
        and all(
            v["actual"] == v["expected"] == v["unique_seeds"] for v in counts.values()
        )
    )
    sets = [
        ("training65", split["training"], 65536),
        ("training524", split["training"], 524288),
    ]
    sets += [(f"holdout{i}", [c], 524288) for i, c in enumerate(split["holdouts"])]
    sets += [
        (shape, [c["id"] for c in off_cells if c["shape"] == shape], 524288)
        for shape in ("BE", "D1", "D2")
    ]
    linear = [c["id"] for c in off_cells if c["shape"] != "BE"]
    sets = [(name, cells, cap) for name, cells, cap in sets if cells]
    if linear:
        sets.append(("linear", linear, 524288))
    names = sorted({r["arm"] for r in rows})
    for a in names:
        result["map_costs"][a] = {}
        for label, cells, cap in sets:
            rs = [r for r in rows if r["arm"] == a and r["cell"] in cells]
            if rs:
                result["map_costs"][a][label] = dict(
                    n=len(rs),
                    solves=sum(r["solved"] and r["evaluations"] <= cap for r in rs),
                    mean_log2_cost=float(np.mean([log_cost(r, cap) for r in rs])),
                )
    starts = sorted({p["start"] for p in completed_pairs})
    for label, cells, cap in sets:
        if all(a in names for a in ["G"] + [f"M{k}" for k in range(1, 7)]):
            # The frozen check is independent of completed learning coverage.
            try:
                result["contrasts"][f"{label}:M/G"] = contrast(
                    rows,
                    [[f"M{k}"] for k in range(1, 7)],
                    [["G"]] * 6,
                    cells,
                    cap,
                    replicates,
                    seed,
                )
            except ValueError:
                pass
        if label in ("BE", "linear", "D1", "D2"):
            off_starts = sorted(
                {p["start"] for p in completed_pairs if p["rep"] == "a"}
            )
            for a, b in [("R", "M+"), ("R", "M"), ("M+", "M")]:
                if not off_starts:
                    continue
                ga = [[f"{a}{k}a"] for k in off_starts]
                gb = [[f"M{k}"] if b == "M" else [f"{b}{k}a"] for k in off_starts]
                try:
                    result["contrasts"][f"{label}:{a}/{b}"] = contrast(
                        rows, ga, gb, cells, cap, replicates, seed
                    )
                except ValueError:
                    pass
            continue
        if not completed_pairs:
            continue
        for a, b in [("R", "M+"), ("R", "R_abl"), ("M+", "M"), ("R", "M")]:
            ga = [
                [
                    f"{a}{p['start']}{p['rep']}"
                    for p in completed_pairs
                    if p["start"] == k
                ]
                for k in starts
            ]
            gb = [
                [f"M{k}"]
                if b == "M"
                else [
                    f"{b}{p['start']}{p['rep']}"
                    for p in completed_pairs
                    if p["start"] == k
                ]
                for k in starts
            ]
            result["contrasts"][f"{label}:{a}/{b}"] = contrast(
                rows, ga, gb, cells, cap, replicates, seed
            )
        diffs = []
        for p in completed_pairs:
            r = result["map_costs"][f"R{p['start']}{p['rep']}"][label]["mean_log2_cost"]
            m = result["map_costs"][f"M+{p['start']}{p['rep']}"][label][
                "mean_log2_cost"
            ]
            diffs.append(m - r)
        result["between_pair_differences"][label] = dict(
            values=diffs, sd=float(np.std(diffs, ddof=1)) if len(diffs) > 1 else None
        )
    result["coverage_by_start"] = {
        str(k): [p["rep"] for p in completed_pairs if p["start"] == k]
        for k in range(1, 7)
    }
    result["log_gain_shrinkage"] = {}
    for arm in ("M+", "R"):
        train = result["contrasts"].get(f"training524:{arm}/M")
        if not train:
            continue
        g = train["mean_log2_difference"]
        result["log_gain_shrinkage"][arm] = {
            f"holdout{i}": dict(
                lost_log2_gain=g
                - result["contrasts"][f"holdout{i}:{arm}/M"]["mean_log2_difference"],
                fraction_lost=(
                    g
                    - result["contrasts"][f"holdout{i}:{arm}/M"]["mean_log2_difference"]
                )
                / g
                if g > 0
                else None,
            )
            for i in range(2)
        }
    if gate_failed:
        result["outcome"] = dict(
            row=0,
            meaning="Calibration did not establish usable row variation; frozen checks descriptive only.",
        )
    elif result["complete"] and len(completed_pairs) == planned_pairs:
        result["outcome"] = outcome(result["contrasts"])
    else:
        result["incomplete_rule"] = (
            "Report observed contrasts/coverage, without a planned-study outcome or full-run power claim."
        )
    return result


def map_changes(finals):
    """Descriptive directions across all available R continuations."""
    residuals = [
        np.array(r["residuals"]) for r in finals.values() if r["learner"] == "R"
    ]
    result = dict(R_maps=len(residuals), rows=[], multiplier_directions={})
    for arm in ("M+", "R"):
        deltas = [r["multiplier_delta"] for r in finals.values() if r["learner"] == arm]
        if deltas:
            d = np.array(deltas)
            result["multiplier_directions"][arm] = dict(
                n=len(d),
                mean_delta=d.mean(0).tolist(),
                positive_counts=(d > 0).sum(0).tolist(),
                negative_counts=(d < 0).sum(0).tolist(),
            )
    if residuals:
        d = np.array(residuals)
        drifts = np.array(
            [r["residual_row_table_l1"] for r in finals.values() if r["learner"] == "R"]
        )
        for row in range(24):
            result["rows"].append(
                dict(
                    row=row,
                    changed_maps=int(np.count_nonzero(drifts[:, row])),
                    mean_table_l1=float(drifts[:, row].mean()),
                    mean_log_residual=d[:, row].mean(0).tolist(),
                    positive_counts=(d[:, row] > 0).sum(0).tolist(),
                    negative_counts=(d[:, row] < 0).sum(0).tolist(),
                )
            )
    return result
