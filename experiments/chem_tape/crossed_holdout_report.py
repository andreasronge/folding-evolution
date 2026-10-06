"""2229 frozen holdout inference; independent trajectories remain the unit."""

from __future__ import annotations

import itertools
import json

import numpy as np
from scipy.stats import norm, t

from experiments.chem_tape.crossed_learning_report import flags, interval


def gain_matrix(rows, trajectories, cells, seeds, cap, g4_hash, phase):
    """Validate every row before averaging, including seed-derived case pairing."""
    expected = set(itertools.product(["G4", *trajectories], cells, seeds))
    lookup, errors = {}, []
    cases = {
        seed: np.random.default_rng([seed, 0]).choice(1331, 64, replace=False).tolist()
        for seed in seeds
    }
    for row in rows:
        key = row["arm"], row["cell"], row["seed"]
        if key in lookup:
            errors.append(f"duplicate row {key}")
        lookup[key] = row
        wanted_hash = (
            g4_hash
            if row["arm"] == "G4"
            else trajectories.get(row["arm"], {}).get("table_hash")
        )
        if row["table_hash"] != wanted_hash:
            errors.append(f"map hash mismatch {key}")
        if row["cap"] != cap or row["phase"] != phase or row["pop_size"] != 256:
            errors.append(f"search settings/phase mismatch {key}")
        if (
            not isinstance(row["solved"], bool)
            or not 0 < row["evaluations"] <= cap
            or row["evaluations"] % 256
            or (not row["solved"] and row["evaluations"] != cap)
        ):
            errors.append(f"invalid solve/evaluation accounting {key}")
        if row["training_indices"] != cases.get(row["seed"]):
            errors.append(f"unpaired or incorrect training cases {key}")
    missing, extra = sorted(expected - lookup.keys()), sorted(lookup.keys() - expected)
    validation = dict(
        passed=not (errors or missing or extra),
        expected_rows=len(expected),
        actual_rows=len(rows),
        errors=errors,
        missing_rows=missing,
        extra_rows=extra,
    )
    if not validation["passed"]:
        return {}, validation

    def cost(row):
        return np.log2(row["evaluations"] if row["solved"] else cap)

    gains = {
        tid: {
            cid: float(
                np.mean(
                    [
                        cost(lookup[("G4", cid, seed)]) - cost(lookup[(tid, cid, seed)])
                        for seed in seeds
                    ]
                )
            )
            for cid in cells
        }
        for tid in trajectories
    }
    return gains, validation


def gain_status(result):
    ci = result["interval_95"]
    return (
        "improved"
        if ci and ci[0] > 1
        else "harmed"
        if ci and ci[1] < 1
        else "unresolved"
    )


def estimate(values, other=None, crossed=False):
    result = interval(values, other)
    result.update(flags(result, crossed=crossed))
    result["gain_status"] = gain_status(result)
    if crossed:
        result["reversed_preference"] = bool(
            result["interval_95"] and result["interval_95"][1] < 1
        )
    return result


def outcome(crossed, generic, interaction, valid):
    if not valid:
        return dict(
            row="U",
            meaning="Frozen holdout evaluation unresolved: validation, completeness, diagnostic mode or G4 solve gate.",
        )
    wins = sum(r["label"] == "W" for r in crossed.values())
    if wins == 2:
        return dict(
            row="1",
            meaning="Matched family advantage resolved in both directions on these three cells; consult matched G4 gains and damage checks for useful specialization.",
        )
    if wins == 1:
        return dict(
            row="2",
            meaning="Matched family advantage resolved in one direction; the other remains bounded or unresolved.",
        )
    if not any(r["resolved_gain"] for arm in generic.values() for r in arm.values()):
        return dict(
            row="3",
            meaning="Holdout improvement unresolved; upper bounds do not by themselves establish transfer loss.",
        )
    if all(r["upper_below_1_25"] for r in crossed.values()):
        return dict(
            row="4",
            meaning="Matched advantage bounded below 1.25x in both directions; report signed/reversed preferences. This does not establish equality.",
        )
    return dict(
        row="5",
        subreading="5a" if interaction["resolved_gain"] else "5b",
        meaning="Directional family dependence unresolved with some resolved holdout improvement. "
        + (
            "The secondary interaction resolves aggregate family information."
            if interaction["resolved_gain"]
            else "Family-dependent versus generic adaptation remains unresolved."
        ),
    )


def future_sizing(x, y):
    """Expected CI width and approximate detection are distinct planning numbers."""
    variances = [float(np.var(v, ddof=1)) for v in (x, y)]
    sizes = np.arange(2, 10001)
    se = np.sqrt(sum(variances) / sizes)
    denom = sum(v**2 for v in variances)
    dfs = (sum(variances) ** 2 / denom * (sizes - 1)) if denom else 2 * sizes - 2
    critical = t.ppf(0.975, dfs)
    target = np.log2(1.1)
    width = critical * se
    # Normal detection approximation with finite-sample t critical value.
    noncentrality = np.divide(target, se, out=np.full_like(se, np.inf), where=se > 0)
    detection = norm.sf(critical - noncentrality) + norm.cdf(-critical - noncentrality)

    def first(mask):
        return int(sizes[mask][0]) if mask.any() else None

    width_n, detect_n = first(width < target), first(detection >= 0.8)

    def cost(n):
        if n is None:
            return None
        additional = max(0, 2 * (n - 10))
        return dict(
            additional_trajectories=additional,
            additional_learning_hours=[additional * 10 / 60, additional * 14 / 60],
            holdout_evaluation_minutes_at_1_1_s_search=(2 * n + 1)
            * 3
            * 400
            * 1.1
            / 10
            / 60,
        )

    return dict(
        within_arm_variance_log2=variances,
        target_ratio=1.1,
        n_per_family_expected_half_width_below_effect=width_n,
        n_per_family_approx_80_percent_detection=detect_n,
        width_cost=cost(width_n),
        detection_cost=cost(detect_n),
        caveat="Observed trajectory spread; fixed three tasks. Expected CI width is not detection probability. Detection uses a normal approximation with Welch t critical values; costs exclude training fresh scoring and overhead. No trajectories added here.",
    )


def make_report(rows, trajectories, config, training_gains, stop_reason=None):
    holdouts = config["holdouts"]
    cells = sum(holdouts.values(), [])
    gains, validation = gain_matrix(
        rows,
        trajectories,
        cells,
        config["fresh_seeds"],
        config["fresh_cap"],
        config["g4_hash"],
        "fresh_holdout",
    )
    wanted_ids = {f"{f}{k}" for f in ("BE", "PA") for k in range(1, 11)}
    if set(trajectories) != wanted_ids or any(
        tr["family"] != tid[:2] for tid, tr in trajectories.items()
    ):
        validation["errors"].append("requires all ten frozen trajectories per family")
    if config.get("learning_permitted", False) or config.get("learning_calls", 0):
        validation["errors"].append("learning forbidden in frozen holdout evaluation")
    validation["passed"] = validation["passed"] and not validation["errors"]
    result = dict(
        complete=validation["passed"],
        validation=validation,
        smoke_only=config["smoke_only"],
        probe_only=config["probe_only"],
        stop_reason=stop_reason,
        outcome=outcome({}, {}, {}, False),
        scope="Frozen maps on three screened D1331 holdouts, including only one BE task; token-only learning with hand-supplied context.",
        metric_definition="Seed-mean log2(T_G4/T_map); unsolved T=cap. Equal cell weight in PA aggregate; trajectory-unit 95% t/Welch intervals.",
        generic={},
        aggregate_gains={},
        crossed={},
        pa_cell_crossed={},
        interaction=None,
        damage={},
        per_map={},
        transfer_loss={},
        future_sizing={},
        n_per_family={
            f: sum(tr["family"] == f for tr in trajectories.values())
            for f in ("BE", "PA")
        },
        counts={},
        timing={},
    )
    for arm in ["G4", *trajectories]:
        result["counts"][arm], result["timing"][arm] = {}, {}
        for cid in cells:
            rs = [r for r in rows if r["arm"] == arm and r["cell"] == cid]
            result["counts"][arm][cid] = dict(
                searches=len(rs),
                solved=sum(r["solved"] for r in rs),
                shortcuts=sum(r["shortcuts"] for r in rs),
                searches_with_shortcuts=sum(r["shortcuts"] > 0 for r in rs),
                unique_shortcuts=sum(r["unique_shortcuts"] for r in rs),
            )
            result["timing"][arm][cid] = dict(
                total_seconds=sum(r["seconds"] for r in rs),
                mean_seconds=float(np.mean([r["seconds"] for r in rs])) if rs else None,
            )
    result["g4_solve_gate"] = {
        cid: dict(
            fraction=(v["solved"] / v["searches"] if v["searches"] else None),
            passed=bool(v["searches"] and v["solved"] / v["searches"] >= 0.85),
        )
        for cid, v in result["counts"]["G4"].items()
    }
    # Infrastructure smoke/probe never produces a scientific inference.
    if (
        not result["complete"]
        or config["smoke_only"]
        or config["probe_only"]
        or stop_reason
    ):
        return result
    ids = {
        f: [tid for tid in trajectories if trajectories[tid]["family"] == f]
        for f in holdouts
    }
    grouped = {
        tid: {
            f: float(np.mean([gains[tid][c] for c in cs])) for f, cs in holdouts.items()
        }
        for tid in trajectories
    }
    result["per_map"] = {
        tid: dict(
            family=trajectories[tid]["family"],
            per_cell_log2=gains[tid],
            aggregate_log2=grouped[tid],
            own_training_log2=training_gains[tid],
            transfer_loss_log2=training_gains[tid]
            - grouped[tid][trajectories[tid]["family"]],
        )
        for tid in trajectories
    }
    for arm, tids in ids.items():
        result["generic"][arm] = {
            cid: estimate([gains[tid][cid] for tid in tids]) for cid in cells
        }
        result["aggregate_gains"][arm] = {
            f: estimate([grouped[tid][f] for tid in tids]) for f in holdouts
        }
        result["transfer_loss"][arm] = interval(
            [result["per_map"][tid]["transfer_loss_log2"] for tid in tids]
        )
    for f in holdouts:
        other = "PA" if f == "BE" else "BE"
        x, y = ([grouped[tid][f] for tid in ids[arm]] for arm in (f, other))
        result["crossed"][f] = estimate(x, y, crossed=True)
        result["future_sizing"][f] = future_sizing(x, y)
        result["damage"][f] = dict(
            applies=result["crossed"][f]["label"] == "W",
            matched=result["aggregate_gains"][f][f],
            mismatched=result["aggregate_gains"][other][f],
            useful_improvement=result["aggregate_gains"][f][f]["gain_status"]
            == "improved",
            via_mismatched_harm=result["aggregate_gains"][other][f]["gain_status"]
            == "harmed",
        )
    result["pa_cell_crossed"] = {
        cid: estimate(
            [gains[tid][cid] for tid in ids["PA"]],
            [gains[tid][cid] for tid in ids["BE"]],
            crossed=True,
        )
        for cid in holdouts["PA"]
    }
    d = {tid: grouped[tid]["BE"] - grouped[tid]["PA"] for tid in trajectories}
    x, y = ([d[tid] for tid in ids[arm]] for arm in ("BE", "PA"))
    result["interaction"] = estimate(x, y, crossed=True)
    assert np.isclose(
        result["interaction"]["log2_mean"],
        sum(r["log2_mean"] for r in result["crossed"].values()),
    )
    result["future_sizing"]["interaction"] = future_sizing(x, y)
    valid = all(v["passed"] for v in result["g4_solve_gate"].values())
    result["outcome"] = outcome(
        result["crossed"], result["generic"], result["interaction"], valid
    )
    return result


def save_report(out, report, rows, holdouts):
    lines = [
        "# Frozen crossed holdout evaluation",
        "",
        report["scope"],
        "",
        f"Outcome {report['outcome']['row']}: {report['outcome']['meaning']}",
        f"Complete: {report['complete']}; smoke: {report['smoke_only']}; probe: {report['probe_only']}.",
        f"Independent trajectories per family: {report['n_per_family']}.",
        "",
    ]

    def show(label, r):
        lines.append(
            f"{label}: {r['ratio']:.3f}x, 95% CI {r['interval_95']}; {r.get('label', 'descriptive')}, {r.get('gain_status', '')}. "
            f"Resolved gain: {r.get('resolved_gain')}; upper below 1.25: {r.get('upper_below_1_25')}."
        )

    for arm, estimates in report["generic"].items():
        for cid, r in estimates.items():
            show(f"Gain {arm} on {cid}", r)
    for arm, estimates in report["aggregate_gains"].items():
        for f, r in estimates.items():
            show(f"Aggregate gain {arm} on {f}", r)
    for f, r in report["crossed"].items():
        show(f"Crossed {f}", r)
        if r["reversed_preference"]:
            lines.append(f"{f}: resolved reversed preference (mismatched maps faster).")
        lines.append("Damage/usefulness: " + json.dumps(report["damage"][f]))
    for cid, r in report["pa_cell_crossed"].items():
        show(f"Descriptive PA contrast {cid}", r)
    if report["interaction"]:
        show("Secondary interaction", report["interaction"])
    for f, r in report["transfer_loss"].items():
        show(f"Descriptive own-training minus holdout gain {f}", r)
    lines += [
        "",
        "B bounds matched advantage only; it does not establish equality. Unresolved gain/harm is not absence.",
        "Future sizing (no extension): " + json.dumps(report["future_sizing"]),
        "G4 solve gate: " + json.dumps(report["g4_solve_gate"]),
        "Validation: "
        + json.dumps(
            {
                "passed": report["validation"]["passed"],
                "expected_rows": report["validation"]["expected_rows"],
                "actual_rows": report["validation"]["actual_rows"],
                "errors": len(report["validation"]["errors"]),
                "missing_rows": len(report["validation"]["missing_rows"]),
                "extra_rows": len(report["validation"]["extra_rows"]),
            }
        )
        + "; details in result.json.",
        "Stop reason: " + str(report["stop_reason"]),
    ]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, cid in zip(axes, sum(holdouts.values(), [])):
        for arm in ("G4", "BE", "PA"):
            rs = [
                r
                for r in rows
                if r["cell"] == cid
                and (r["arm"] == arm or r["arm"].startswith(arm) and arm != "G4")
            ]
            if rs:
                budgets = np.geomspace(256, rs[0]["cap"], 100)
                ax.plot(
                    budgets,
                    [
                        np.mean([r["solved"] and r["evaluations"] <= b for r in rs])
                        for b in budgets
                    ],
                    label=arm,
                )
        ax.set(
            title=cid,
            xlabel="Evaluations",
            ylabel="Fraction exactly solved",
            xscale="log",
            ylim=(0, 1),
        )
        if rows:
            ax.legend()
    fig.tight_layout()
    fig.savefig(out / "holdout_solves.png", dpi=150)
    plt.close(fig)
    fig, axes = plt.subplots(2, 3, figsize=(15, 7))
    for column, cid in enumerate(sum(holdouts.values(), [])):
        for arm in ("G4", "BE", "PA"):
            points = {}
            for row in rows:
                if row["cell"] == cid and (
                    row["arm"] == arm or arm != "G4" and row["arm"].startswith(arm)
                ):
                    for evaluation, fit, diversity in row["curve"]:
                        points.setdefault(evaluation, []).append((fit / 64, diversity))
            if points:
                xs = sorted(points)
                for i in (0, 1):
                    axes[i, column].plot(
                        xs, [np.mean([v[i] for v in points[x]]) for x in xs], label=arm
                    )
        for i, ylabel in enumerate(
            ("Mean best accuracy (active searches)", "Mean diversity (active searches)")
        ):
            axes[i, column].set(
                title=cid, xlabel="Evaluations", ylabel=ylabel, xscale="log"
            )
            if rows:
                axes[i, column].legend()
    fig.tight_layout()
    fig.savefig(out / "search_curves.png", dpi=150)
    plt.close(fig)
