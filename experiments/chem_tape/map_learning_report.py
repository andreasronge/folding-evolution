"""Paired trajectory/seed inference for the approved PA refinement study."""

from __future__ import annotations

import math

import numpy as np

from experiments.chem_tape.map_learning import log_cost


def classify(interval):
    low, high = interval
    return "faster" if low > 1 else "no practical gain" if high < 1.5 else "unresolved"


def contrast(rows, ids_a, ids_b, cells, cap=524288, replicates=10000):
    """Joint block/seed bootstrap; frozen observations enter only once.

    Reinitializing the fixed bootstrap stream for each contrast shares draws
    across reported comparisons. Use the union of test seeds, retaining the
    drawn members observed on the selected cells (50 training / 100 holdout).
    Each matched trajectory draw is shared by both learned arms, including
    a C table's own C-marg. A frozen control has no trajectory dimension.
    """
    groups = {}
    for row in rows:
        groups.setdefault((row["arm"], row["cell"]), {})[row["seed"]] = row
    keys = [(a, c) for a in ids_a + ids_b for c in cells]
    if any(key not in groups for key in keys):
        raise ValueError("missing contrast observations")
    seeds = sorted(set.intersection(*(set(groups[key]) for key in keys)))
    if any(len(groups[key]) != len(seeds) for key in keys):
        raise ValueError("unpaired or incomplete contrast observations")
    universe = sorted({r["seed"] for r in rows})
    locations = np.array([universe.index(s) for s in seeds])

    def matrix(ids):
        return np.asarray(
            [
                [[log_cost(groups[(a, c)][s], cap) for s in seeds] for c in cells]
                for a in ids
            ]
        )

    a, b = matrix(ids_a), matrix(ids_b)
    n = max(len(a), len(b))
    if len(a) not in (1, n) or len(b) not in (1, n):
        raise ValueError("trajectory pairing requires matched lengths")
    point = float(b.mean() - a.mean())
    block_rng = np.random.default_rng([132700000, 0])
    seed_rng = np.random.default_rng([132700000, 1])
    boot = np.empty(replicates)
    for i in range(replicates):
        # Consume the same number of trajectory uniforms even for the four-T
        # fallback; seed draws stay joint across every contrast regardless of n.
        blocks = (block_rng.random(max(6, n))[:n] * n).astype(int)
        weights = np.bincount(
            seed_rng.integers(len(universe), size=len(universe)),
            minlength=len(universe),
        )[locations]
        if not weights.sum():
            weights = np.ones(len(seeds))

        def mean(x):
            selected = x if len(x) == 1 else x[blocks]
            return float(
                np.sum(selected * weights)
                / (selected.shape[0] * len(cells) * weights.sum())
            )

        boot[i] = mean(b) - mean(a)
    interval = (2 ** np.quantile(boot, [0.025, 0.975])).tolist()
    differences = b.mean((1, 2)) - a.mean((1, 2))
    sd = float(np.std(differences, ddof=1)) if n > 1 else None
    # Planning heuristic, not a power guarantee: enough blocks for half-width
    # log2(1.5)/2 at the measured trajectory spread, with seed noise held fixed.
    needed = (
        max(n, math.ceil((1.96 * sd / (np.log2(1.5) / 2)) ** 2))
        if sd is not None
        else None
    )
    return dict(
        ratio=float(2**point),
        mean_log2_difference=point,
        interval_95=interval,
        classification=classify(interval),
        trajectories=n,
        paired_seeds=len(seeds),
        cells=cells,
        cap=cap,
        between_trajectory_sd=sd,
        approximate_trajectories_for_resolution=needed,
        resolution_estimate_scope="heuristic from trajectory spread; seed noise not removed",
        bootstrap_replicates=replicates,
    )


def outcome(contrasts):
    training = contrasts["training524:C/G"]["classification"]
    if training == "unresolved":
        return dict(row=5, meaning="Training gain unresolved; transfer not decided")
    if training == "no practical gain":
        return dict(
            row=1,
            meaning="No practical fresh-training gain at the 524k test cap; inspect the 65k objective before diagnosing failure to learn",
        )
    g = [contrasts[f"holdout{i}:C/G"]["classification"] for i in range(2)]
    m = [contrasts[f"holdout{i}:C/M"]["classification"] for i in range(2)]
    if g == ["no practical gain"] * 2:
        return dict(
            row=2, meaning="No >=1.5x holdout gain supported within interval resolution"
        )
    if g == ["faster"] * 2 and m == ["faster"] * 2:
        return dict(
            row=3,
            meaning="Learned contextual preferences transfer within the screened PA family beyond G token retuning",
        )
    if g == ["faster"] * 2 and m == ["no practical gain"] * 2:
        return dict(
            row=4,
            meaning="Transfer with bounded incremental C advantage over M; inspect M/G before claiming M transfer",
        )
    return dict(row=5, meaning="Transfer contrasts unresolved or mixed")


def make_report(rows, split, schedule, complete, replicates=10000):
    planned = [
        f"{a}{k + 1}"
        for k in range(6)
        for a in ("C", "M", "T")
        if k < schedule["trajectories"][a]
    ]
    expected = {
        a: 500
        for a in planned
        + [f"C-marg{k + 1}" for k in range(schedule["trajectories"]["C"])]
        + ["G", "G-marg"]
    }
    expected.update(U=200, F=200)
    # Smoke uses different counts; caller supplies its explicit expectation.
    if "expected_test_counts" in schedule:
        expected = schedule["expected_test_counts"]
    counts = {a: sum(r["arm"] == a for r in rows) for a in expected}
    missing = [a for a in expected if counts[a] != expected[a]]
    result = dict(
        complete=complete and not missing,
        planned_trajectory_ids=planned,
        missing_map_ids=missing,
        expected_test_counts=expected,
        actual_test_counts=counts,
        outcome=None,
        contrasts={},
        map_costs={},
    )
    for a in sorted({r["arm"] for r in rows}):
        result["map_costs"][a] = {}
        for name, cells in [
            ("training", split["training"]),
            ("holdouts", split["holdouts"]),
        ]:
            rs = [r for r in rows if r["arm"] == a and r["cell"] in cells]
            if rs:
                result["map_costs"][a][name] = {
                    str(cap): dict(
                        n=len(rs),
                        mean_log2_cost=float(np.mean([log_cost(r, cap) for r in rs])),
                        solves=sum(r["solved"] and r["evaluations"] <= cap for r in rs),
                    )
                    for cap in (65536, 524288)
                }
        costs = result["map_costs"][a]
        if "training" in costs and "holdouts" in costs:
            costs["holdout_minus_training_log2_gap"] = (
                costs["holdouts"]["524288"]["mean_log2_cost"]
                - costs["training"]["524288"]["mean_log2_cost"]
            )
    if not result["complete"]:
        result["incomplete_rule"] = "No planned-study outcome from a truncated schedule"
        return result
    ids = {
        a: [f"{a}{k + 1}" for k in range(schedule["trajectories"][a])]
        for a in ("C", "M", "T")
    }
    ids["C-marg"] = [f"C-marg{k + 1}" for k in range(schedule["trajectories"]["C"])]
    for label, cells, cap in [
        ("training65", split["training"], 65536),
        ("training524", split["training"], 524288),
    ] + [(f"holdout{i}", [c], 524288) for i, c in enumerate(split["holdouts"])]:
        comparisons = [("C", "G"), ("M", "G"), ("T", "G-marg"), ("T", "G")]
        if label.startswith("holdout"):
            comparisons += [("C", "M"), ("C", "C-marg")]
        for a, b in comparisons:
            result["contrasts"][f"{label}:{a}/{b}"] = contrast(
                rows, ids.get(a, [a]), ids.get(b, [b]), cells, cap, replicates
            )
    result["outcome"] = outcome(result["contrasts"])
    result["scope"] = (
        "G refinement on a reused screened PA bank; no mechanism or family-specificity claim"
    )
    return result


def plots(out, generations, rows, holdouts):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for tid in sorted({r["trajectory"] for r in generations}):
        rs = [r for r in generations if r["trajectory"] == tid]
        axes[0].plot(
            [r["generation"] for r in rs],
            [min(r["scores"]) for r in rs],
            label=tid,
            marker=".",
            markersize=3,
        )
        axes[1].plot(
            [r["generation"] for r in rs],
            [
                np.mean([r["candidates"][i]["l1_drift"] for i in r["selected_indices"]])
                for r in rs
            ],
            marker=".",
            markersize=3,
        )
    axes[0].set(xlabel="Outer generation", ylabel="Best training mean log2 cost")
    axes[1].set(xlabel="Outer generation", ylabel="Mean selected probability L1 drift")
    for arm in sorted({r["arm"].rstrip("0123456789") for r in rows}):
        rs = [
            r
            for r in rows
            if r["arm"].rstrip("0123456789") == arm and r["cell"] in holdouts
        ]
        if not rs:
            continue
        budgets = np.geomspace(256, 524288, 128)
        axes[2].plot(
            budgets,
            [
                np.mean([r["solved"] and r["evaluations"] <= b for r in rs])
                for b in budgets
            ],
            label=arm,
        )
    axes[2].set(
        xscale="log", xlabel="Holdout test evaluations", ylabel="Exact solve fraction"
    )
    axes[0].legend(fontsize=6, ncol=3)
    axes[2].legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(out / "curves.png", dpi=150)
    plt.close(fig)
