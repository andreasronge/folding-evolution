"""2303 paired corpus inference and shared, cell-stratified G4 uncertainty."""

from collections import defaultdict
import math

import numpy as np

from experiments.chem_tape.comparison_gate_report import (
    describe as base_describe,
    balanced_target_n,
)
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.fragment_run import CORPORA
from experiments.chem_tape.small_source_report import contrast
from experiments.chem_tape.solver_corpus_report import cost
from experiments.chem_tape.sparse_feedback_report import HORIZONS

REPLICATES = 8192


def describe(rows):
    result = base_describe(rows)
    if rows:
        result["worker_seconds"] = sum(
            r["seconds"] + r.get("external_verification_seconds", 0) for r in rows
        )
    return result


def corpus_values(rows, method, units="log_cost"):
    grouped = defaultdict(list)
    for r in rows:
        if r["arm"] == method:
            value = (
                np.log(cost(r))
                if units == "log_cost"
                else r["evaluations"]
                if units == "evaluations"
                else r["seconds"] + r.get("external_verification_seconds", 0)
            )
            grouped[r["corpus"], r["block"]].append(value)
    return np.array(
        [np.mean([np.mean(grouped[tid, b]) for b in range(4)]) for tid in CORPORA]
    )


def bootstrap(rows, methods, units):
    """Fixed target roster; corpus clusters + independent G4 seeds in each cell.

    Each replicate draws one G4 baseline shared across every fitted corpus and
    method. No independent pseudo-G4 corpus observations are manufactured.
    """
    rng = np.random.default_rng(206610092303)
    idx = np.column_stack(
        [
            rng.choice(
                [i for i, t in enumerate(CORPORA) if t.startswith(f)],
                size=(REPLICATES, 8),
            )
            for f in ("BE", "PA")
        ]
    )
    fit = {m: corpus_values(rows, m, units) for m in methods}
    draws = {m: v[idx].mean(1) for m, v in fit.items()}
    g4 = defaultdict(list)
    for r in rows:
        if r["arm"] == "G4":
            g4[r["cell"]].append(
                np.log(cost(r))
                if units == "log_cost"
                else r["evaluations"]
                if units == "evaluations"
                else r["seconds"] + r.get("external_verification_seconds", 0)
            )
    if len(g4) != 16 or any(len(v) != 16 for v in g4.values()):
        raise ValueError("G4 roster incomplete")
    baseline = np.zeros(REPLICATES)
    for cid in sorted(g4):
        values = np.asarray(g4[cid])
        baseline += values[rng.integers(16, size=(REPLICATES, 16))].mean(1) / 16
    return fit, draws, idx, float(np.mean([np.mean(v) for v in g4.values()])), baseline


def acquisition_cost(a, units, accounting, method):
    if units == "evaluations":
        return a["evaluations"]
    # Source G4 seconds are historical; convert using its current historical
    # replay. A8 continuation and fitting overhead were measured in 2033 and
    # use the current matched cheap-arm replay factor. Report this as calibration.
    cal = accounting["current_calibration"]
    if method == "full_F":
        source = a["source_worker_seconds"] * cal["G4"]
        overhead_factor = cal["full_F"]
    else:
        source = (
            a["historical_source_seconds"] * cal["G4"]
            + a["current_source_seconds"] * cal[method]
        )
        overhead_factor = cal[method]
    overhead = sum(
        a.get(k, 0)
        for k in (
            "verification_seconds",
            "fit_seconds",
            "extraction_seconds",
            "continuation_verification_seconds",
            "intermediate_overhead_seconds",
        )
    )
    return source + overhead * overhead_factor


def economics(rows, methods, accounting):
    result = {}
    for units in ("evaluations", "worker_seconds"):
        fit, draws, idx, g4, gdraws = bootstrap(rows, methods, units)
        prices = {}
        curves = {}
        for m in (*methods, "G4"):
            if m == "G4":
                price = np.zeros(16)
                search = np.full(16, g4)
                sd = gdraws
            else:
                price = np.array(
                    [
                        acquisition_cost(accounting["full"][tid], units, accounting, m)
                        if m == "full_F"
                        else np.mean(
                            [
                                acquisition_cost(
                                    accounting["cheap"][f"{tid}|{b}|{m}"],
                                    units,
                                    accounting,
                                    m,
                                )
                                for b in range(4)
                            ]
                        )
                        for tid in CORPORA
                    ]
                )
                search, sd = fit[m], draws[m]
            prices[m] = dict(
                acquisition=price,
                search=search,
                acquisition_draws=price[idx].mean(1),
                search_draws=sd,
            )
            curves[m] = [
                dict(
                    N=n,
                    cost=float(price.mean() + n * search.mean()),
                    interval_95=np.quantile(
                        prices[m]["acquisition_draws"] + n * sd, [0.025, 0.975]
                    ).tolist(),
                )
                for n in HORIZONS
            ]
        comparisons = {}
        pairs = [("A8", "full_F"), ("A8", "G4"), ("full_F", "G4")]
        if "S8" in methods:
            pairs.append(("A8", "S8"))
        for x, y in pairs:
            dx = prices[x]["acquisition_draws"] - prices[y]["acquisition_draws"]
            ds = prices[x]["search_draws"] - prices[y]["search_draws"]
            da = float(
                prices[x]["acquisition"].mean() - prices[y]["acquisition"].mean()
            )
            delta = float(prices[x]["search"].mean() - prices[y]["search"].mean())
            root = -da / delta if delta and -da / delta > 0 else None
            comparisons[f"{x}-{y}"] = dict(
                positive_point_crossover_N=root,
                at_horizons=[
                    dict(
                        N=n,
                        difference=float(da + n * delta),
                        interval_95=np.quantile(dx + n * ds, [0.025, 0.975]).tolist(),
                    )
                    for n in HORIZONS
                ],
            )
        result[units] = dict(
            curves=curves,
            comparisons=comparisons,
            acquisition_mean={
                m: float(v["acquisition"].mean()) for m, v in prices.items()
            },
            arithmetic_search_mean={
                m: float(v["search"].mean()) for m, v in prices.items()
            },
            acquisition_qualification=accounting["qualification"],
            estimator="actual arithmetic search expenditure; failures charged their actual cap, distinct from primary 2cap log estimator",
        )
    return result


def report(out, rows, schedule, accounting, preparation):
    def key(r):
        return r["corpus"], r["cell"], r["seed"], r["arm"]

    if (
        len(rows) != len(schedule)
        or len({key(r) for r in rows}) != len(rows)
        or {key(r) for r in rows} != {key(r) for r in schedule}
    ):
        raise ValueError("incomplete/duplicate roster; no efficacy report")
    methods = tuple(preparation["admission"]["selected"]["arms"])
    accounting = dict(
        accounting,
        current_calibration=preparation["validation"]["calibration"],
        qualification="Historical source seconds calibrated by sampled current G4 replay; adaptive continuation and overhead calibrated by matched cheap-arm replay; full fitting overhead by full-F replay. Calibration is approximate, not a remeasurement of acquisition. Current-bank search seconds include external verification.",
    )
    write_json(out, "accounting.json", accounting)
    fitted = [dict(r, method=r["arm"]) for r in rows if r["arm"] != "G4"]
    primary = contrast(fitted, "A8", "full_F")
    if primary["n"] != 16 or primary["df"] != 15 or primary["missing_blocks"]:
        raise ValueError("primary corpus/block roster incomplete")
    fit, draws, _, base, bdraws = bootstrap(rows, methods, "log_cost")
    usefulness = {
        m: dict(
            cost_ratio=float(np.exp(base - fit[m].mean())),
            interval_95=np.quantile(np.exp(bdraws - draws[m]), [0.025, 0.975]).tolist(),
            numerator="G4",
            denominator=m,
            replicates=REPLICATES,
            estimator="shared G4 resample stratified within fixed cell + fitted corpus resampling within source family",
        )
        for m in methods
    }
    summaries = {
        m: describe([r for r in rows if r["arm"] == m]) for m in (*methods, "G4")
    }
    lo, hi = primary["interval_95"]
    useful = usefulness["A8"]["interval_95"][0] > 1
    guard = summaries["full_F"]["solve_rate"] >= 0.25
    relative = (
        "material_relative_loss"
        if lo > 1.20
        else "resolved_loss_unknown_materiality"
        if lo > 1 and hi >= 1.20
        else "bounded_retention"
        if hi < 1.20
        else "unresolved"
    )
    retention = hi < 1.20 and useful and guard
    sensitivities = dict(
        cap_penalty_1=contrast(fitted, "A8", "full_F", penalty=1),
        both_solved=contrast(fitted, "A8", "full_F", both=True),
        source_families={
            f: contrast([r for r in fitted if r["family"] == f], "A8", "full_F")
            for f in ("BE", "PA")
        },
    )
    per_cell = {
        cid: dict(
            rho=contrast([r for r in fitted if r["cell"] == cid], "A8", "full_F"),
            summaries={
                m: describe([r for r in rows if r["arm"] == m and r["cell"] == cid])
                for m in (*methods, "G4")
            },
        )
        for cid in sorted({r["cell"] for r in rows})
    }
    n = balanced_target_n(primary["sd_log"], math.log(1.20) - math.log(1.05), 16)
    resolution = dict(
        scenario_corpora=n,
        extra_corpora=n - 16,
        additional_scoring_seconds=(n - 16)
        / 16
        * preparation["admission"]["selected"]["projected_seconds"],
        assumption="same independent-corpus log SD; target 95% half-width < log(1.20/1.05); extra acquisition/agent time required, no automatic top-up",
        current_sd=primary["sd_log"],
    )
    per_corpus_bounds = {}
    for units in ("evaluations", "worker_seconds"):
        # A complete new corpus must at least pay for its most expensive
        # single policy acquisition. Policies share source attempts, so this
        # max is an explicit lower bound rather than a double-charged sum.
        prices = [
            np.mean(
                [
                    acquisition_cost(
                        accounting["full"][tid], units, accounting, "full_F"
                    )
                    for tid in CORPORA
                ]
            )
        ]
        for m in methods:
            if m != "full_F":
                prices.append(
                    4
                    * np.mean(
                        [
                            acquisition_cost(
                                accounting["cheap"][f"{tid}|{b}|{m}"],
                                units,
                                accounting,
                                m,
                            )
                            for tid in CORPORA
                            for b in range(4)
                        ]
                    )
                )
        per_corpus_bounds[units] = float(max(prices))
    resolution.update(
        additional_acquisition_evaluations_lower_bound=(n - 16)
        * per_corpus_bounds["evaluations"],
        additional_acquisition_worker_seconds_lower_bound=(n - 16)
        * per_corpus_bounds["worker_seconds"],
        acquisition_bound="maximum of complete full-F and four-block cheap policy prices; shared historical source attempts prevent summing policies; approximate worker calibration",
        agent_hours_scenario=3 if n > 16 else 0,
    )
    if "effective_workers" in preparation["admission"]:
        resolution["complete_hours_lower_bound_scenario"] = (
            resolution["additional_scoring_seconds"]
            + resolution["additional_acquisition_worker_seconds_lower_bound"]
            / preparation["admission"]["effective_workers"]
        ) / 3600 + resolution["agent_hours_scenario"]
    diagnostics = {}
    for m in methods:
        rs = [r for r in rows if r["arm"] == m]
        diagnostics[m] = dict(
            edited_children=sum(r["operator"]["edited_children"] for r in rs),
            eligible_children=sum(r["operator"]["eligible_children"] for r in rs),
            changed_tokens=sum(r["operator"]["changed_tokens"] for r in rs),
        )
    result = dict(
        complete=True,
        primary=primary,
        usefulness=usefulness,
        summaries=summaries,
        decision="useful_retention" if retention else relative,
        relative_result=relative,
        A8_useful_against_G4=useful,
        full_F_solve_guard=guard,
        sigma=contrast(fitted, "S8", "A8") if "S8" in methods else None,
        sensitivity=sensitivities,
        per_cell=per_cell,
        diagnostics=diagnostics,
        economics=economics(rows, methods, accounting),
        resolution_price=resolution,
        scope="Fixed two-sum-v1 target roster on D1331; intervals conditional on selected targets; frozen externally fitted literal-window reuse. No inherited adaptation or general transfer claim.",
    )
    write_json(out, "result.json", result)
    lines = [
        f"Decision: **{result['decision']}**; return to strategy.",
        "",
        result["scope"],
        "",
        f"Primary capped evaluation ratio A8/full_F: {primary['cost_ratio']:.3f}, 95% t interval [{lo:.3f}, {hi:.3f}], 16 corpus units (15 df).",
        f"A8 usefulness against G4: {useful}; full_F solve guard >=25%: {guard}.",
        "",
        "| method | solves | fraction | G4/method cost ratio (95% interval) |",
        "|---|---:|---:|---|",
    ]
    for m in methods:
        s, u = summaries[m], usefulness[m]
        lines.append(
            f"| {m} | {s['solved']}/{s['n']} | {s['solve_rate']:.3f} | {u['cost_ratio']:.3f} [{u['interval_95'][0]:.3f}, {u['interval_95'][1]:.3f}] |"
        )
    lines += [
        "",
        "G4 uncertainty is resampled within each cell and shared across all fitted corpus comparisons.",
        "Bounded retention, usefulness and relative loss are separate results. Selecting full acquisition also needs usefulness against G4 and a stated horizon on the acquisition+search curves.",
        "Worker-time acquisition calibration and complete resolution scenarios are in result.json. No post-score target filtering or further bank.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    plots(out, rows, result)
    return result


def plots(out, rows, result):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    methods = sorted({r["arm"] for r in rows})
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for method in methods:
        rs = [r for r in rows if r["arm"] == method]
        budgets = np.unique(np.geomspace(256, rs[0]["cap"], 128).astype(int))
        axes[0].plot(
            budgets,
            [
                np.mean([r["solved"] and r["evaluations"] <= b for r in rs])
                for b in budgets
            ],
            label=method,
        )
        curves = defaultdict(list)
        for r in rs:
            for ev, fitness, diversity in r["curve"]:
                curves[ev].append((fitness, diversity))
        x = sorted(curves)
        axes[1].plot(
            x, [np.mean([v[0] / 64 for v in curves[e]]) for e in x], label=method
        )
        axes[2].plot(x, [np.mean([v[1] for v in curves[e]]) for e in x], label=method)
    axes[0].set(xscale="log", xlabel="Evaluations", ylabel="Exact solve fraction")
    axes[1].set(xlabel="Evaluations (surviving runs)", ylabel="Mean fitness")
    axes[2].set(xlabel="Evaluations (surviving runs)", ylabel="Mean diversity")
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, (units, e) in zip(axes, result["economics"].items()):
        for method, curve in e["curves"].items():
            x = [r["N"] for r in curve]
            ax.plot(x, [r["cost"] for r in curve], label=method)
            ax.fill_between(
                x,
                [r["interval_95"][0] for r in curve],
                [r["interval_95"][1] for r in curve],
                alpha=0.12,
            )
        ax.set(xscale="symlog", yscale="log", xlabel="Reuse horizon N", ylabel=units)
        ax.legend()
    fig.tight_layout()
    fig.savefig(out / "cost_curves.png", dpi=150)
    plt.close(fig)
