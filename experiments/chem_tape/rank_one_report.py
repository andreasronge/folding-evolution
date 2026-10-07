"""0821 family-balanced paired training intervals and bounded interpretations."""

from collections import Counter

import numpy as np
from scipy.stats import spearmanr, t

from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.crossed_learning_report import interval
from experiments.chem_tape.crossed_learning_run import TRAINING
from experiments.chem_tape.map_learning import log_cost


def balanced(values):
    if any(not values[f] for f in TRAINING):
        return dict(log2_mean=None, ratio=None, interval_95=None, df=None)
    x, y = (np.asarray(values[f]) for f in TRAINING)
    mean = float((x.mean() + y.mean()) / 2)
    result = dict(log2_mean=mean, ratio=2**mean, interval_95=None, df=None)
    if min(len(x), len(y)) < 2:
        return result
    se = float(0.5 * np.sqrt(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y)))
    df = len(x) + len(y) - 2
    width = float(t.ppf(0.975, df) * se)
    result.update(
        interval_95=[2 ** (mean - width), 2 ** (mean + width)],
        standard_error_log2=se,
        df=df,
        half_width_log2=width,
    )
    return result


def outcome(primary, token, context, residual, valid, counts):
    if not valid or min(counts.values()) < 6:
        return dict(
            row="U",
            meaning="Invalid/incomplete data or fewer than six complete pairs per family.",
            next="strategy",
        )
    lo, hi = primary["interval_95"]
    if lo > 1:
        attributed = residual["interval_95"][0] > 1
        return dict(
            row="1",
            meaning="Mixed token+context continuation improves fresh training cost.",
            residual_removal_resolved=attributed,
            attribution="Residual removal is resolved, including emitted marginal changes."
            if attributed
            else "Benefit of the mixed procedure; residual attribution unresolved.",
            next="frozen transfer" if primary["ratio"] >= 1.1 else "strategy",
        )
    if hi < 1.15:
        if token["interval_95"][0] > 1:
            return dict(
                row="2",
                meaning="Context increment bounded below 1.15x while token continuation improved.",
                mechanism="Consult initial b-step diagnostics; B versus C remains tentative; D untested.",
                next="close 18; strategy",
            )
        return dict(
            row="3",
            meaning="Context increment bounded below 1.15x; token learning unresolved. Depth versus ineffective context remains unresolved.",
            neither_arm_resolved_learning=context["interval_95"][0] <= 1,
            next="park 18; strategy",
        )
    return dict(
        row="4",
        meaning="Unresolved primary increment.",
        next="size possible extra pairs from observed spread; strategy if unaffordable",
    )


def validate_fresh(config, pairs, rows, finals, maps):
    expected = {
        ("G4", c, s) for c in sum(TRAINING.values(), []) for s in config["fresh_seeds"]
    }
    for tid in pairs:
        expected.update(
            (tid + ":" + arm, c, s)
            for arm in ("S", "T", "C", "C0")
            for c in TRAINING[tid[:2]]
            for s in config["fresh_seeds"]
        )
    seen, cases, errors = set(), {}, []
    if len(set(pairs)) != len(pairs):
        errors.append("duplicate pairs")
    order = [f"{f}{k}" for k in range(1, 9) for f in ("BE", "PA")]
    if pairs != order[: len(pairs)]:
        errors.append("non-prefix alternating admission")
    for row in rows:
        key = row["arm"], row["cell"], row["seed"]
        if key in seen or key not in expected:
            errors.append("duplicate/unexpected fresh row")
        seen.add(key)
        if (
            row["cap"] != config["fresh_cap"]
            or row["pop_size"] != 256
            or row["phase"] != "fresh"
            or row["arm"] not in maps
            or row["table_hash"] != maps.get(row["arm"], {}).get("table_hash")
        ):
            errors.append("fresh cap/population/phase/map mismatch")
        seed = row["seed"]
        if seed in cases and cases[seed] != row["training_indices"]:
            errors.append("fresh shared-seed cases mismatch")
        cases[seed] = row["training_indices"]
    if seen != expected:
        errors.append("missing/unexpected fresh observations")
    budget = config["searches_per_trajectory"]
    if not config["smoke_only"] and budget != 4040:
        errors.append("incorrect full trajectory budget")
    for tid in pairs:
        for arm in ("T", "C"):
            rec = finals.get(tid + ":" + arm)
            if rec is None or rec["search_costs"]["searches"] != budget:
                errors.append("missing/incorrect trajectory budget")
    return dict(
        passed=not errors,
        errors=sorted(set(errors)),
        expected_rows=len(expected),
        observed_rows=len(rows),
    )


def make_report(config, pairs, rows, finals, maps):
    validation = validate_fresh(config, pairs, rows, finals, maps)
    counts = {f: sum(tid.startswith(f) for tid in pairs) for f in TRAINING}
    lookup = {(r["arm"], r["cell"], r["seed"]): r for r in rows}
    comparisons = {
        "C/T": ("T", "C"),
        "T/S": ("S", "T"),
        "C/S": ("S", "C"),
        "C/C0": ("C0", "C"),
        "C0/T": ("T", "C0"),
    }
    contrasts, pair_values = {}, {}
    if validation["passed"]:
        for label, (num, den) in comparisons.items():
            values = {f: [] for f in TRAINING}
            pair_values[label] = {}
            for tid in pairs:
                costs = [
                    log_cost(lookup[tid + ":" + num, c, s], config["fresh_cap"])
                    - log_cost(lookup[tid + ":" + den, c, s], config["fresh_cap"])
                    for c in TRAINING[tid[:2]]
                    for s in config["fresh_seeds"]
                ]
                value = float(np.mean(costs))
                pair_values[label][tid] = value
                values[tid[:2]].append(value)
            contrasts[label] = dict(
                pooled=balanced(values),
                families={f: interval(v) if v else None for f, v in values.items()},
            )
    complete = (
        validation["passed"]
        and not config["smoke_only"]
        and not config["probe_only"]
        and min(counts.values()) >= 6
    )
    decision = (
        outcome(
            *(contrasts[k]["pooled"] for k in ("C/T", "T/S", "C/S", "C/C0")),
            True,
            counts,
        )
        if complete
        else dict(
            row="U",
            meaning="Invalid/incomplete data, smoke/probe, or fewer than six complete pairs per family.",
            next="strategy",
        )
    )
    fresh_stats = {}
    for r in rows:
        key = r["arm"] + "|" + r["cell"]
        item = fresh_stats.setdefault(
            key,
            dict(n=0, solves=0, evaluations=0, worker_seconds=0.0, log2_cost_sum=0.0),
        )
        item["n"] += 1
        item["solves"] += int(r["solved"])
        item["evaluations"] += r["evaluations"]
        item["worker_seconds"] += r["seconds"]
        item["log2_cost_sum"] += log_cost(r, config["fresh_cap"])
    for item in fresh_stats.values():
        item.update(
            solve_fraction=item["solves"] / item["n"],
            mean_log2_cost=item["log2_cost_sum"] / item["n"],
            seconds_per_search=item["worker_seconds"] / item["n"],
        )
    agreement = {}
    for arm in ("T", "C") if validation["passed"] else ():
        x = [finals[tid + ":" + arm]["selected_score"] for tid in pairs]
        y = [
            float(
                np.mean(
                    [
                        fresh_stats[tid + ":" + arm + "|" + c]["mean_log2_cost"]
                        for c in TRAINING[tid[:2]]
                    ]
                )
            )
            for tid in pairs
        ]
        rho = (
            float(spearmanr(x, y).statistic)
            if len(x) > 2 and len(set(x)) > 1 and len(set(y)) > 1
            else None
        )
        agreement[arm] = dict(
            selected_in_loop=x, fresh_cost=y, descriptive_spearman=rho
        )
    # Hand-set grammars are consulted only after selection and fresh scoring.
    from experiments.chem_tape.four_reducer_maps import tables

    grammar = tables()
    contrast = np.log(np.diff(grammar["G4-BE"], prepend=0, axis=1)) - np.log(
        np.diff(grammar["G4-PA"], prepend=0, axis=1)
    )
    alignment = {}
    for tid in pairs:
        rec = finals.get(tid + ":C")
        if rec is None:
            continue
        r = np.asarray(rec["diagnostics"]["residual_log_weights"])
        denom = np.linalg.norm(r) * np.linalg.norm(contrast)
        alignment[tid] = float(np.sum(r * contrast) / denom) if denom else None
    mix = {
        arm: {
            op: dict(
                Counter(
                    {
                        metric: sum(
                            rec["step_mix"][op][metric]
                            for name, rec in finals.items()
                            if name.endswith(":" + arm)
                        )
                        for metric in (
                            "proposed",
                            "survived",
                            "clipped_elements",
                            "redraws",
                        )
                    }
                )
            )
            for op in ("token", "b", "a")
        }
        for arm in ("T", "C")
    }
    return dict(
        validation=validation,
        family_counts=counts,
        pairs=pairs,
        outcome=decision,
        metric="Improvement A/B = mean log2(cost_B/cost_A), unsolved=2*cap; equal cells and equal family weights; t df=n_BE+n_PA-2.",
        contrasts=contrasts,
        pair_effects=pair_values,
        fresh_stats=fresh_stats,
        in_loop_fresh_agreement=agreement,
        grammar_alignment_cosine=alignment,
        step_mix=mix,
        map_diagnostics={name: rec["diagnostics"] for name, rec in finals.items()},
        continuation_costs={name: rec["search_costs"] for name, rec in finals.items()},
        scope="Short continuation on reused training bank; no holdout/transfer evaluation. Calibration conditional on starts/directions; clipping and residual removal alter marginals.",
    )


def save_report(out, result, finals):
    write_json(out, "report.json", result)
    lines = [
        "# Rank-one continuation on training cells",
        "",
        result["scope"],
        "",
        f"Outcome {result['outcome']['row']}: {result['outcome']['meaning']}",
        "",
        "| Contrast (improvement) | Ratio | 95% interval |",
        "|---|---:|---|",
    ]
    for label, estimates in result["contrasts"].items():
        p = estimates["pooled"]
        lines.append(f"| {label} | {p['ratio']} | {p['interval_95']} |")
    lines.extend(
        [
            "",
            "Calibration cannot stop continuation or decide an outcome. Selected-minus-all gain is distinct from beneficial change relative to the parent.",
            "",
            "See report.json for per-unit/family paired bootstrap diagnostics, solve fractions, timing, clipping, and attribution qualifications.",
        ]
    )
    (out / "report.md").write_text("\n".join(lines) + "\n")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    # Raw generation records retain parent rescoring and operator histories.
    import json

    path = out / "generations.jsonl"
    if path.exists():
        generations = [json.loads(line) for line in path.read_text().splitlines()]
        for name in finals:
            tid, arm = name.split(":")
            rs = [r for r in generations if r["start"] == tid and r["arm"] == arm]
            axes[0].plot(
                [r["generation"] + 1 for r in rs],
                [min(r["scores"]) for r in rs],
                color="C0" if arm == "T" else "C1",
                alpha=0.4,
            )
    axes[0].set(
        xlabel="Generation",
        ylabel="Minimum in-loop log2 cost",
        title="T blue; C orange (selection-biased)",
    )
    effects = result["pair_effects"].get("C/T", {})
    axes[1].bar(
        range(len(effects)),
        list(effects.values()),
        color=["C0" if k.startswith("BE") else "C1" for k in effects],
    )
    axes[1].axhline(0, color="black", linewidth=0.7)
    axes[1].set(
        xlabel="Alternating paired starts",
        ylabel="Fresh log2(T/C) improvement",
        title="BE blue; PA orange",
    )
    fig.tight_layout()
    fig.savefig(out / "learning.png", dpi=140)
    plt.close(fig)
