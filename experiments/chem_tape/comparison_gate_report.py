"""1246 corpus-level training endpoint; descriptive G4 headroom and run pricing."""

from __future__ import annotations

import math
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import t

from experiments.chem_tape.comparison_gate_bank import TRAINING
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.solver_corpus_report import cost


def interval(values):
    x = np.asarray(values, dtype=float)
    result = dict(
        n=len(x),
        contrasts_log=x.tolist(),
        speed_ratio=None,
        interval_95=None,
        sd_log=None,
        half_width_log=None,
    )
    if not len(x):
        return result
    result["speed_ratio"] = float(np.exp(x.mean()))
    if len(x) > 1:
        sd = float(x.std(ddof=1))
        width = float(t.ppf(0.975, len(x) - 1) * sd / np.sqrt(len(x)))
        result.update(
            sd_log=sd,
            half_width_log=width,
            df=len(x) - 1,
            interval_95=[
                float(np.exp(x.mean() - width)),
                float(np.exp(x.mean() + width)),
            ],
        )
    return result


def route(ct, collection_yield, eligible):
    if not eligible:
        return dict(
            label="incomplete",
            meaning="execution obstacle or too few complete prefix corpora; no efficacy decision",
        )
    bounds = ct.get("interval_95")
    if bounds and bounds[0] > 1:
        if collection_yield >= 0.4:
            return dict(
                label="recommend_stage2",
                meaning="relative C/T training gain; recommend strategy consider frozen transfer",
            )
        return dict(
            label="acquisition_obstacle",
            meaning="resolved C/T training gain with pooled yield below 40%; strategy review",
        )
    if bounds and bounds[1] < 1.10:
        return dict(
            label="bounded_small_gain",
            meaning="C/T gain bounded below 10%; stage 2 unattractive for C/T; absence not established",
        )
    return dict(
        label="unresolved",
        meaning="C/T unresolved; price additional independent balanced corpora",
    )


def selected_prefix(completed_pairs):
    return [f"{f}{k + 1}" for k in range(completed_pairs) for f in TRAINING]


def describe(rows, penalty=2):
    if not rows:
        return dict(n=0)
    return dict(
        n=len(rows),
        solved=sum(r["solved"] for r in rows),
        solve_rate=float(np.mean([r["solved"] for r in rows])),
        geometric_cost=float(np.exp(np.mean([np.log(cost(r, penalty)) for r in rows]))),
        actual_evaluations=sum(r["evaluations"] for r in rows),
        worker_seconds=sum(
            r["seconds"] + r.get("verification_seconds", 0) for r in rows
        ),
    )


def balanced_target_n(sd, target, minimum):
    """Approximate same-spread fresh-corpus precision target with t critical value."""
    if sd is None or target <= 0:
        return None
    n = max(4, int(2 * math.ceil((1.96 * sd / target) ** 2 / 2)))
    while t.ppf(0.975, n - 1) * sd / np.sqrt(n) > target:
        n += 2
    return max(minimum, n)


def make_report(
    rows, corpora, config, completed_pairs, g4_complete, stop_kind, stop_reason, timings
):
    prefix = selected_prefix(completed_pairs)
    grouped = defaultdict(list)
    for r in rows:
        if r["phase"] == "training" and (r["corpus"] in prefix or r["arm"] == "G4"):
            grouped[r["corpus"], r["cell"], r["arm"]].append(r)
    # Never infer completion from the fastest individual results.
    for tid in prefix:
        for cid in TRAINING[tid[:2]]:
            for arm in ("C", "T"):
                rs = grouped[tid, cid, arm]
                if len(rs) != config["fresh_n"] or len({r["seed"] for r in rs}) != len(
                    rs
                ):
                    raise ValueError("completed prefix is missing a scored corpus cell")
            if {r["seed"] for r in grouped[tid, cid, "C"]} != {
                r["seed"] for r in grouped[tid, cid, "T"]
            }:
                raise ValueError("unpaired endpoint")
    if g4_complete:
        for cid in sum(TRAINING.values(), []):
            if len(grouped["G4", cid, "G4"]) != config["g4_n"]:
                raise ValueError("G4 grid incomplete")
    acquisition = {}
    for family in TRAINING:
        rs = [
            r
            for r in rows
            if r["phase"] == "collection"
            and r["corpus"] in prefix
            and r["family"] == family
        ]
        acquisition[family] = describe(rs)
    acquired = [r for r in rows if r["phase"] == "collection" and r["corpus"] in prefix]
    yield_pooled = float(np.mean([r["solved"] for r in acquired])) if acquired else 0.0
    observed_corpora = {r["corpus"] for r in rows if r["corpus"] != "G4"} | set(corpora)
    trailing = sorted(observed_corpora - set(prefix))
    trailing_summary = {}
    for tid in trailing:
        selected = [r for r in rows if r["corpus"] == tid]
        trailing_summary[tid] = {
            key: describe([r for r in selected if r["phase"] + ":" + r["arm"] == key])
            for key in sorted({r["phase"] + ":" + r["arm"] for r in selected})
        }
    # Include incomplete acquisition cells as observations, without admitting
    # their faster completed searches into the primary endpoint or yield gate.
    tape_diagnostics = {}
    for tid in sorted(observed_corpora):
        selected = [
            r for r in rows if r["phase"] == "collection" and r["corpus"] == tid
        ]
        tape_diagnostics[tid] = {
            cid: dict(
                attempts=sum(r["cell"] == cid for r in selected),
                solved=sum(r["cell"] == cid and r["solved"] for r in selected),
                distinct_tapes=len(
                    {
                        tuple(r["solver"])
                        for r in selected
                        if r["cell"] == cid and r["solved"] and "solver" in r
                    }
                ),
            )
            for cid in TRAINING[tid[:2]]
        }
    eligible = (
        g4_complete
        and completed_pairs >= 6
        and not config["smoke_only"]
        and (
            stop_kind == "timeout"
            or (stop_kind is None and completed_pairs == config["nc"])
        )
    )
    report = dict(
        scope="training C versus restricted token-likelihood fit; no transfer or isolated token-order inference",
        smoke_only=config["smoke_only"],
        completed_pairs=completed_pairs,
        analysed_corpora=prefix,
        stage1_complete=completed_pairs == config["nc"]
        and g4_complete
        and stop_kind is None,
        efficacy_eligible=eligible,
        stop_kind=stop_kind,
        stop_reason=stop_reason,
        unanalysed_trailing_corpora=trailing,
        unanalysed_trailing_search_summary=trailing_summary,
        total_searches=len(rows),
        observed_counts=dict(Counter(r["phase"] + ":" + r["arm"] for r in rows)),
        holdout_searches=sum(r["phase"] == "holdout" for r in rows),
        collection_yield_pooled=yield_pooled,
        collection_per_family=acquisition,
        distinct_tapes=tape_diagnostics,
        sensitivities={},
        method_hash=config["method_hash"],
    )
    if report["holdout_searches"]:
        raise ValueError("protected holdout was searched")
    for penalty in (2, 1):
        by_family, corpus_scores = {f: [] for f in TRAINING}, {}
        for tid in prefix:
            values = []
            for cid in TRAINING[tid[:2]]:
                by_seed = {
                    arm: {r["seed"]: r for r in grouped[tid, cid, arm]}
                    for arm in ("C", "T")
                }
                values += [
                    np.log(cost(by_seed["T"][s], penalty))
                    - np.log(cost(by_seed["C"][s], penalty))
                    for s in by_seed["C"]
                ]
            score = float(np.mean(values))
            corpus_scores[tid] = score
            by_family[tid[:2]].append(score)
        ct = interval(list(corpus_scores.values()))
        ct.update(
            families={f: interval(x) for f, x in by_family.items()},
            equal_family_weight=True,
            corpus_scores_log=corpus_scores,
        )
        cells, families, amortization = {}, {}, {}
        for family, cids in TRAINING.items():
            families[family] = {}
            for cid in cids:
                cells[cid] = {}
                for arm in ("C", "T", "G4"):
                    rs = (
                        grouped["G4", cid, "G4"]
                        if arm == "G4"
                        else sum(
                            [
                                grouped[tid, cid, arm]
                                for tid in prefix
                                if tid.startswith(family)
                            ],
                            [],
                        )
                    )
                    cells[cid][arm] = describe(rs, penalty)
            for arm in ("C", "T", "G4"):
                # Equal cell weights, each with the same number of searches.
                rs = [
                    r
                    for r in rows
                    if r["phase"] == "training"
                    and r["family"] == family
                    and r["arm"] == arm
                    and (arm == "G4" or r["corpus"] in prefix)
                ]
                families[family][arm] = describe(rs, penalty)
            for arm in ("C", "T"):
                ref, fitted = families[family]["G4"], families[family][arm]
                families[family][arm + "/G4"] = (
                    ref["geometric_cost"] / fitted["geometric_cost"]
                    if ref["n"] and fitted["n"]
                    else None
                )
        reference = {}
        for arm in ("C", "T"):
            ratios = [families[f][arm + "/G4"] for f in TRAINING]
            reference[arm + "/G4"] = (
                float(np.exp(np.mean(np.log(ratios))))
                if all(r is not None for r in ratios)
                else None
            )
        for tid in prefix:
            tr = corpora[tid]
            g4_rows = sum([grouped["G4", c, "G4"] for c in TRAINING[tid[:2]]], [])
            amortization[tid] = {}
            for arm in ("C", "T"):
                rs = sum([grouped[tid, c, arm] for c in TRAINING[tid[:2]]], [])
                if not g4_rows or not rs:
                    continue
                eval_saved = float(
                    np.mean([cost(r, penalty) for r in g4_rows])
                    - np.mean([cost(r, penalty) for r in rs])
                )
                time_saved = float(
                    np.mean([r["seconds"] for r in g4_rows])
                    - np.mean([r["seconds"] for r in rs])
                )
                amortization[tid][arm] = dict(
                    mean_capped_evaluations_saved_per_search=eval_saved,
                    break_even_searches_evaluations=math.ceil(
                        tr["collection_evaluations"] / eval_saved
                    )
                    if eval_saved > 0
                    else None,
                    break_even_searches_worker_seconds=math.ceil(
                        (tr["collection_worker_seconds"] + tr["fit_seconds"])
                        / time_saved
                    )
                    if time_saved > 0
                    else None,
                )
        report["sensitivities"][f"unsolved_{penalty}x_cap"] = dict(
            C_T=ct,
            per_cell=cells,
            per_family=families,
            descriptive_reference=reference,
            amortization=amortization,
            reference_uncertainty="descriptive point ratios only; G4 seeds independent, shared baseline not replicated per corpus",
        )
    primary = report["sensitivities"]["unsolved_2x_cap"]["C_T"]
    report["outcome"] = route(primary, yield_pooled, eligible)
    if config["smoke_only"]:
        report["outcome"] = dict(
            label="smoke",
            meaning="development-only execution/throughput check; no efficacy inference",
        )
    baseline = report["sensitivities"]["unsolved_2x_cap"]["descriptive_reference"]
    report["useful_adaptation_caution"] = (
        baseline["C/G4"] is not None
        and baseline["T/G4"] is not None
        and baseline["C/G4"] <= 1
        and baseline["T/G4"] <= 1
    )
    n = len(prefix)
    sd = primary["sd_log"]
    target = balanced_target_n(sd, math.log(1.10), n)
    effect = abs(float(np.mean(primary["contrasts_log"]))) if n else 0
    power_target = (
        max(n, 4, int(2 * math.ceil(((1.96 + 0.84) * sd / effect) ** 2 / 2)))
        if sd is not None and effect > 0
        else None
    )
    report["sizing"] = dict(
        total_corpora_for_half_width_log_1_10=target,
        extra_balanced_corpora=max(0, target - n) if target is not None else None,
        total_corpora_for_approx_80percent_detect_observed_effect=power_target,
        note="same observed spread, approximate fixed-design planning only; fresh corpora, not more score seeds",
    )
    projected = {}
    throughput = {}
    for phase, arm in (
        ("collection", "G4"),
        ("training", "C"),
        ("training", "T"),
        ("training", "G4"),
    ):
        rs = [r for r in rows if r["phase"] == phase and r["arm"] == arm]
        throughput[phase + ":" + arm] = describe(rs)
    collections = [
        v for k, v in timings.items() if k.startswith("collection:") and v["complete"]
    ]
    scoring = [
        v for k, v in timings.items() if k.startswith("training:") and v["complete"]
    ]
    cg = throughput["collection:G4"]
    ca, ta, ga = [throughput["training:" + a] for a in ("C", "T", "G4")]
    fit_seconds = sum(tr.get("fit_seconds", 0) for tr in corpora.values()) / max(
        1, len(corpora)
    )
    if all(x["n"] for x in (cg, ca, ta, ga)):
        effective = (
            min(
                config["workers"],
                sum(v["worker_seconds"] for v in scoring)
                / max(1e-9, sum(v["wall_seconds"] for v in scoring)),
            )
            if scoring
            else 1
        )
        collect_effective = (
            min(
                config["workers"],
                sum(v["worker_seconds"] for v in collections)
                / max(1e-9, sum(v["wall_seconds"] for v in collections)),
            )
            if collections
            else 1
        )
        collection_mean, c_mean, t_mean, g_mean = [
            x["worker_seconds"] / x["n"] for x in (cg, ca, ta, ga)
        ]
        projected = dict(
            full_collection_seconds=3072 * collection_mean / max(1, collect_effective),
            full_CT_training_seconds=1024 * (c_mean + t_mean) / max(1, effective),
            full_G4_training_seconds=256 * g_mean / config["workers"],
            full_fitting_seconds=16 * fit_seconds,
            effective_scoring_workers=effective,
            effective_collection_workers=collect_effective,
            stage2_seconds_same_difficulty=(2048 * (c_mean + t_mean) + 256 * g_mean)
            / max(1, effective),
            stage2_caveat="no holdouts timed; extrapolation from training, allow harder protected targets",
            extra_corpus_seconds=192 * collection_mean / max(1, collect_effective)
            + 64 * (c_mean + t_mean) / max(1, effective)
            + fit_seconds,
        )
        projected["full_stage1_seconds"] = sum(
            projected[k]
            for k in (
                "full_collection_seconds",
                "full_CT_training_seconds",
                "full_G4_training_seconds",
                "full_fitting_seconds",
            )
        )
        extra = report["sizing"]["extra_balanced_corpora"]
        projected["precision_topup_seconds"] = (
            extra * projected["extra_corpus_seconds"] if extra is not None else None
        )
    report["throughput"], report["projection"] = throughput, projected
    return report


def save_report(out, report, rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    write_json(out, "result.json", report)
    lines = [
        "# Comparison-gate training stage 1246",
        "",
        f"Outcome: {report['outcome']['label']} — {report['outcome']['meaning']}",
        "",
        report["scope"],
        "",
        f"Analysed prefix: {report['analysed_corpora']}; holdout searches: {report['holdout_searches']}.",
        f"Pooled collection yield: {report['collection_yield_pooled']:.3f}.",
        "",
        "| Unsolved cost | C/T speed | 95% corpus interval |",
        "|---|---:|---|",
    ]
    for key, val in report["sensitivities"].items():
        ct = val["C_T"]
        lines.append(f"| {key} | {ct['speed_ratio']} | {ct['interval_95']} |")
    lines += [
        "",
        "G4 ratios are descriptive; see result.json for per-cell/family solve rates, acquisition diversity, amortization and sizing.",
        f"Stop: {report['stop_kind']}: {report['stop_reason']}",
        "Protected stage 2 is frozen and remains unexecuted.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for arm in ("C", "T", "G4"):
        selected = [
            r
            for r in rows
            if r["phase"] == "training"
            and r["arm"] == arm
            and (arm == "G4" or r["corpus"] in report["analysed_corpora"])
        ]
        if not selected:
            continue
        budgets = np.geomspace(256, 524288, 100)
        axes[0].plot(
            budgets,
            [
                np.mean([r["solved"] and r["evaluations"] <= b for r in selected])
                for b in budgets
            ],
            label=arm,
        )
        points = defaultdict(list)
        for r in selected:
            for ev, accuracy, diversity in r["curve"]:
                points[ev].append((accuracy, diversity))
        x = sorted(points)
        for axis, index in ((axes[1], 0), (axes[2], 1)):
            axis.plot(
                x, [np.median([v[index] for v in points[ev]]) for ev in x], label=arm
            )
    for axis, label in zip(
        axes,
        (
            "Fraction D1331-exact",
            "Median best correct cases (active runs)",
            "Median behavioural diversity (active runs)",
        ),
    ):
        axis.set(xlabel="Evaluations", ylabel=label, xscale="log")
        if axis.lines:
            axis.legend()
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    plt.close(fig)
