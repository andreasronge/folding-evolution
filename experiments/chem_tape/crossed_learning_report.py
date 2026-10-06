"""Training-only inference with independent adapted maps as the sampling unit."""

from __future__ import annotations

import itertools
import json

import numpy as np
from scipy.stats import spearmanr, t


def interval(values, other=None):
    """Log2 mean and 95% t/Welch interval; never pair BE and PA trajectories."""
    x = np.asarray(values, dtype=float)
    mean = float(x.mean())
    if other is not None:
        mean -= float(np.mean(other))
    if len(x) < 2 or (other is not None and len(other) < 2):
        return dict(log2_mean=mean, ratio=2**mean, interval_95=None, df=None)
    vx = float(x.var(ddof=1) / len(x))
    df = len(x) - 1
    if other is not None:
        y = np.asarray(other, dtype=float)
        vy = float(y.var(ddof=1) / len(y))
        df = (
            ((vx + vy) ** 2 / (vx**2 / (len(x) - 1) + vy**2 / (len(y) - 1)))
            if vx + vy
            else len(x) + len(y) - 2
        )
        vx += vy
    width = float(t.ppf(0.975, df) * np.sqrt(vx))
    return dict(
        log2_mean=mean,
        ratio=2**mean,
        interval_95=[2 ** (mean - width), 2 ** (mean + width)],
        df=float(df),
        half_width_log2=width,
    )


def flags(result, crossed=False):
    ci = result["interval_95"]
    resolved = ci is not None and ci[0] > 1
    bounded = ci is not None and ci[1] < 1.25
    return dict(
        resolved_gain=resolved,
        upper_below_1_25=bounded,
        label=("W" if crossed else "L")
        if resolved
        else ("B" if crossed else "N")
        if bounded
        else "X",
    )


def outcome(own, crossed, valid, n, gate_stopped):
    if not valid or n < 6 and not gate_stopped:
        return dict(
            row="U",
            meaning="Unresolved: incomplete/invalid data or fewer than six maps per family.",
        )
    if gate_stopped:
        return dict(
            row="1",
            meaning="Early low-yield stop; learning remains unresolved. Consult fresh intervals.",
        )
    a, b = (own[f]["label"] for f in ("BE", "PA"))
    if a == b == "N":
        return dict(
            row="2",
            meaning="Gains of 1.25x or more are excluded at the stated own-training intervals.",
        )
    if a == b == "L":
        if all(crossed[f]["label"] == "B" for f in ("BE", "PA")):
            return dict(
                row="3",
                meaning="Both families improve; both crossed training advantages are bounded below 1.25x. Holdout specificity remains untested.",
            )
        return dict(
            row="4",
            meaning="Both families improve; training-family information is possible or resolved. Holdout transfer remains untested.",
        )
    if (a == "L") != (b == "L"):
        return dict(
            row="5",
            meaning="Improvement demonstrated in one family only; the other is bounded or unresolved, not established absent.",
        )
    return dict(
        row="6",
        meaning="Own-training learning gain remains unresolved against trajectory variation.",
    )


def correlation(x, y):
    if len(x) < 3 or min(len(set(x)), len(set(y))) < 2:
        return dict(spearman=None, reason="fewer than three maps or constant scores")
    return dict(spearman=float(spearmanr(x, y).statistic))


def own_precision(values):
    """Descriptive n for an expected interval to clear 1 at a true 1.25x gain."""
    sd = float(np.std(values, ddof=1))
    sizes = np.arange(2, 10001)
    half_widths = t.ppf(0.975, sizes - 1) * sd / np.sqrt(sizes)
    meets = sizes[half_widths < np.log2(1.25)]
    return dict(
        between_trajectory_sd_log2=sd,
        estimated_n_for_half_width_below_log2_1_25=int(meets[0])
        if len(meets)
        else None,
        caveat="Uses observed SD; expected precision at true 1.25x gain, not a power guarantee.",
    )


def sizing(spreads, n):
    if not spreads or n < 2:
        return None
    proxy = float(np.median([s["contrast_proxy"] for s in spreads.values()]))
    candidates = []
    for size in sorted(set([n, 14, 18])):
        half = float(t.ppf(0.975, 2 * size - 2) * proxy * np.sqrt(2 / size))
        candidates.append(
            dict(n_per_family=size, half_width_log2=half, reaches_target=half <= 0.5)
        )
    selected = next((c["n_per_family"] for c in candidates if c["reaches_target"]), n)
    achieved_half = float(t.ppf(0.975, 2 * n - 2) * proxy * np.sqrt(2 / n))
    return dict(
        s_off=proxy,
        definition="median over ten cells of sqrt((s_BE^2+s_PA^2)/2)",
        family_cell_medians={
            f: float(
                np.median(
                    [
                        s["contrast_proxy"]
                        for cid, s in spreads.items()
                        if cid.startswith(f + ":")
                    ]
                )
            )
            for f in ("BE", "PA")
        },
        candidates=candidates,
        selected_n_per_family=selected,
        no_candidate_reaches_target=not any(c["reaches_target"] for c in candidates),
        achieved_half_width_log2=achieved_half,
        ratio_whose_point_estimate_would_clear_one=2**achieved_half,
        caveat="Training-only precision proxy; neither power nor conservative coverage is guaranteed for any holdout.",
    )


def make_report(rows, trajectories, config, gate_stopped):
    training = config["training"]
    cells = sum(training.values(), [])
    seeds = config["fresh_seeds"]
    maps = ["G4", *trajectories]
    expected = set(itertools.product(maps, cells, seeds))
    lookup = {}
    errors = []
    for row in rows:
        key = row["arm"], row["cell"], row["seed"]
        if key in lookup:
            errors.append(f"duplicate fresh row {key}")
        lookup[key] = row
        if row["cell"] not in cells or row["phase"] != "fresh_training":
            errors.append(f"non-training fresh row {key}")
        if row["cap"] != config["fresh_cap"]:
            errors.append(f"fresh cap mismatch {key}")
        if not 0 < row["evaluations"] <= row["cap"]:
            errors.append(f"fresh evaluation count outside cap {key}")
        wanted_hash = (
            config["g4_hash"]
            if row["arm"] == "G4"
            else trajectories.get(row["arm"], {}).get("table_hash")
        )
        if row["table_hash"] != wanted_hash:
            errors.append(f"fresh map hash mismatch {key}")
    missing = sorted(expected - set(lookup))
    extra = sorted(set(lookup) - expected)
    ids = {
        f: [tid for tid, tr in trajectories.items() if tr["family"] == f]
        for f in training
    }
    n = min(map(len, ids.values()))
    if len(ids["BE"]) != len(ids["PA"]):
        errors.append("unbalanced completed trajectories")
    valid = not (errors or missing or extra)
    result = dict(
        complete=valid,
        smoke_only=config["smoke_only"],
        gate_stopped=gate_stopped,
        n_per_family={f: len(v) for f, v in ids.items()},
        errors=errors,
        missing_fresh_rows=missing,
        extra_fresh_rows=extra,
        outcome=None,
        metric_definition="Per map/cell: mean over shared seeds of log2(T_G4/T_map), T=evaluations to solve or cap if unsolved. Cell means have equal weight; trajectory units for t/Welch intervals.",
        trajectory_gains={},
        own={},
        off={},
        crossed={},
        per_cell={},
        scope="Fresh training cells only; no held-out transfer is measured.",
    )
    if not valid or n < 2:
        result["outcome"] = outcome({}, {}, False, n, gate_stopped)
        return result

    def cost(row):
        return np.log2(row["evaluations"] if row["solved"] else config["fresh_cap"])

    gains = {}
    for tid in trajectories:
        gains[tid] = {}
        for cid in cells:
            for seed in seeds:
                if (
                    lookup[("G4", cid, seed)]["training_indices"]
                    != lookup[(tid, cid, seed)]["training_indices"]
                ):
                    errors.append(f"unpaired cases {tid} {cid} {seed}")
            gains[tid][cid] = float(
                np.mean(
                    [
                        cost(lookup[("G4", cid, seed)]) - cost(lookup[(tid, cid, seed)])
                        for seed in seeds
                    ]
                )
            )
    if errors:
        result["complete"] = False
        result["outcome"] = outcome({}, {}, False, n, gate_stopped)
        return result
    by_set = {
        tid: {
            f: float(np.mean([gains[tid][c] for c in cs])) for f, cs in training.items()
        }
        for tid in trajectories
    }
    result["trajectory_gains"] = by_set
    result["per_cell"] = gains
    for family in training:
        other = "PA" if family == "BE" else "BE"
        own = interval([by_set[tid][family] for tid in ids[family]])
        own.update(flags(own))
        own.update(own_precision([by_set[tid][family] for tid in ids[family]]))
        crossed = interval(
            [by_set[tid][family] for tid in ids[family]],
            [by_set[tid][family] for tid in ids[other]],
        )
        crossed.update(flags(crossed, crossed=True))
        result["own"][family] = own
        result["off"][family] = interval([by_set[tid][other] for tid in ids[family]])
        result["crossed"][family] = crossed
    spreads = {}
    for cid in cells:
        sd = {
            f: float(np.std([gains[tid][cid] for tid in ids[f]], ddof=1))
            for f in training
        }
        spreads[cid] = dict(
            within_arm_sd_log2=sd,
            contrast_proxy=float(np.sqrt((sd["BE"] ** 2 + sd["PA"] ** 2) / 2)),
        )
    result["spreads"] = spreads
    result["stage2_sizing"] = sizing(spreads, n)
    result["outcome"] = outcome(
        result["own"], result["crossed"], valid, n, gate_stopped
    )
    # Row 3/5 explicitly do not extend, even if the generic size proxy says so.
    if result["outcome"]["row"] in ("3", "5"):
        result["stage2_sizing"]["selected_n_per_family"] = n
        result["stage2_sizing"]["routing_override"] = (
            "proposal row 3/5: achieved n, no extension"
        )
    result["repeatability"] = {}
    for f in training:
        trs = [trajectories[tid] for tid in ids[f]]
        loop = [tr["final_in_loop_selected_score"] for tr in trs]
        selection = [min(tr["selection_scores"]) for tr in trs]
        fresh = [by_set[tid][f] for tid in ids[f]]
        ranks = [
            v for tr in trs for v in tr["within_generation_spearman"] if v is not None
        ]
        result["repeatability"][f] = dict(
            within_generation_median_spearman=float(np.median(ranks))
            if ranks
            else None,
            defined_rank_count=len(ranks),
            loop_vs_selection=correlation(loop, selection),
            loop_vs_fresh_gain=correlation(loop, fresh),
            selection_vs_fresh_gain=correlation(selection, fresh),
        )
    vectors = {
        f: np.asarray([trajectories[tid]["vector"] for tid in ids[f]]) for f in training
    }
    mean = {f: v.mean(axis=0) for f, v in vectors.items()}
    distance = float(np.linalg.norm(mean["BE"] - mean["PA"]))
    spread = {
        f: float(np.sqrt(np.mean(np.sum((v - mean[f]) ** 2, axis=1))))
        for f, v in vectors.items()
    }
    combined = np.concatenate(list(vectors.values()))
    rng = np.random.default_rng(1723500)
    exceed = 0
    for _ in range(10000):
        shuffled = rng.permutation(combined)
        d = np.linalg.norm(shuffled[:n].mean(axis=0) - shuffled[n:].mean(axis=0))
        exceed += d >= distance
    rms = float(np.sqrt(np.mean(np.square(list(spread.values())))))
    result["parameter_divergence"] = dict(
        distance_between_family_means=distance,
        within_family_rms_spread=spread,
        distance_over_within_rms=distance / rms if rms else None,
        descriptive_permutation_p=(1 + exceed) / 10001,
        permutations=10000,
        seed=1723500,
        test_classification="exploratory; no claim or routing gate",
        token_mean_log_multiplier_difference_BE_minus_PA=(
            mean["BE"] - mean["PA"]
        ).tolist(),
        token_differences_sorted=[
            dict(
                token_id=int(i),
                mean_BE=float(mean["BE"][i]),
                mean_PA=float(mean["PA"][i]),
                difference_BE_minus_PA=float(mean["BE"][i] - mean["PA"][i]),
            )
            for i in np.argsort(-np.abs(mean["BE"] - mean["PA"]), kind="stable")
        ],
    )
    result["cost"] = {
        tid: {k: tr[k] for k in ("seconds", "evaluations")}
        for tid, tr in trajectories.items()
    }
    return result


def save_report(out, report, trajectories, rows):
    lines = [
        "# Crossed learning: training only",
        "",
        report["scope"],
        "",
        f"Outcome: {report['outcome']['row']} — {report['outcome']['meaning']}",
        f"Maps per family: {report['n_per_family']}. Smoke: {report['smoke_only']}.",
        "",
    ]
    for kind in ("own", "off", "crossed"):
        for family, r in report[kind].items():
            lines.append(
                f"{kind} {family}: {r['ratio']:.3f}x, 95% interval {r['interval_95']}; {r.get('label', 'descriptive')}."
            )
    lines += [
        "",
        "L/W takes precedence over N/B; retain both flags. N/B bounds gains below 1.25x, not absence of improvement.",
        "Crossed estimates use independent trajectory Welch intervals; shared search seeds are paired within map/cell only.",
        "No result from this stage establishes held-out family specificity.",
        "",
        "Sizing (training-only proxy): " + json.dumps(report.get("stage2_sizing")),
        "",
        "Stop reason: " + str(report.get("stop_reason")),
    ]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for family in ("BE", "PA"):
        for tid, tr in trajectories.items():
            if tr["family"] != family:
                continue
            ranks = tr["within_generation_spearman"]
            axes[0].plot(
                range(1, len(ranks) + 1),
                [np.nan if x is None else x for x in ranks],
                alpha=0.4,
            )
            g = report["trajectory_gains"].get(tid)
            if g:
                axes[1].scatter(g["BE"], g["PA"], label=tid)
        rs = [
            r
            for r in rows
            if r["arm"] in trajectories and trajectories[r["arm"]]["family"] == family
        ]
        if rs:
            budgets = np.geomspace(256, rs[0]["cap"], 100)
            axes[2].plot(
                budgets,
                [
                    np.mean([r["solved"] and r["evaluations"] <= b for r in rs])
                    for b in budgets
                ],
                label=family,
            )
    axes[0].set(xlabel="Generation", ylabel="Prior vs rescored parent Spearman")
    axes[1].set(xlabel="Log2 gain on BE training", ylabel="Log2 gain on PA training")
    axes[1].axhline(0, color="grey")
    axes[1].axvline(0, color="grey")
    axes[2].set(
        xlabel="Evaluations",
        ylabel="Fraction solved (all training cells)",
        xscale="log",
    )
    if rows:
        axes[2].legend()
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for arm in ["G4", "BE", "PA"]:
        rs = [
            r
            for r in rows
            if r["arm"] == arm or (arm != "G4" and r["arm"].startswith(arm))
        ]
        points = {}
        for r in rs:
            for evaluation, fit, diversity in r["curve"]:
                points.setdefault(evaluation, []).append((fit, diversity))
        if points:
            xs = sorted(points)
            for i, axis in enumerate(axes):
                axis.plot(
                    xs, [np.mean([v[i] for v in points[x]]) for x in xs], label=arm
                )
    for axis, label in zip(
        axes,
        [
            "Mean best matches / 64 (active searches)",
            "Mean phenotype diversity (active searches)",
        ],
    ):
        axis.set(xlabel="Evaluations", ylabel=label, xscale="log")
        if rows:
            axis.legend()
    fig.tight_layout()
    fig.savefig(out / "search_curves.png", dpi=150)
    plt.close(fig)
