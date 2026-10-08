"""Corpus-level paired endpoints, fixed-prefix routing and measured run pricing."""

import math
from collections import Counter, defaultdict

import numpy as np

from experiments.chem_tape.comparison_gate_bank import TRAINING
from experiments.chem_tape.comparison_gate_report import (
    balanced_target_n,
    describe,
    interval,
    selected_prefix,
)
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.solver_corpus_report import cost

ARMS = ("C_S", "T_S", "C_P", "C_exact", "G4")
CONTRASTS = (
    ("C_S", "T_S"),
    ("C_S", "G4"),
    ("C_S", "C_P"),
    ("C_S", "C_exact"),
    ("T_S", "G4"),
)


def route(ct, cg, eligible):
    if not eligible:
        return dict(
            label="incomplete",
            meaning="too few complete balanced corpora or execution error; no efficacy decision",
        )
    if ct["interval_95"][1] < 1.20:
        return dict(
            label="bounded_gain",
            meaning="worthwhile gain bounded for this collector; do not fund feedback on it",
        )
    if ct["interval_95"][0] > 1:
        if cg["interval_95"][0] > 1:
            return dict(
                label="useful",
                meaning="resolved relative and G4 improvements; worthwhile gain still plausible; strategy consider feedback",
            )
        return dict(
            label="relative_only",
            meaning="resolved C/T advantage; useful acquisition against G4 remains unestablished",
        )
    return dict(
        label="unresolved", meaning="C/T unresolved; price further independent corpora"
    )


def contrasts(grouped, prefix, penalty=2, both_solved=False):
    result = {}
    for left, right in CONTRASTS:
        values = {}
        pairs = {}
        for tid in prefix:
            cell_means = []
            counts = 0
            for cid in TRAINING[tid[:2]]:
                left_rows, right_rows = (
                    grouped[tid, cid, left],
                    grouped[tid, cid, right],
                )
                selected = [
                    s
                    for s in left_rows
                    if not both_solved
                    or (left_rows[s]["solved"] and right_rows[s]["solved"])
                ]
                counts += len(selected)
                if selected:
                    cell_means.append(
                        np.mean(
                            [
                                math.log(cost(right_rows[s], penalty))
                                - math.log(cost(left_rows[s], penalty))
                                for s in selected
                            ]
                        )
                    )
            if cell_means:
                values[tid] = float(np.mean(cell_means))
            pairs[tid] = counts
        stat = interval(list(values.values()))
        stat.update(
            corpus_scores_log=values,
            paired_searches=pairs,
            families={
                f: interval([v for tid, v in values.items() if tid.startswith(f)])
                for f in TRAINING
            },
            conditional_on_both_solved=both_solved,
            note="both-solved sensitivity conditions on success and may omit cells/corpora"
            if both_solved
            else "equal cells and paired seeds within each independent corpus",
        )
        result[f"{left}/{right}"] = stat
    return result


def projection(rows, corpora, config, timings):
    throughput = {}
    for phase, arms in (("collection", ("G4",)), ("training", ARMS)):
        for arm in arms:
            selected = [r for r in rows if r["phase"] == phase and r["arm"] == arm]
            throughput[f"{phase}:{arm}"] = dict(
                n=len(selected),
                solved=sum(r["solved"] for r in selected),
                mean_worker_seconds=float(
                    np.mean([r["worker_seconds"] for r in selected])
                )
                if selected
                else None,
                unsolved_mean_worker_seconds=float(
                    np.mean([r["worker_seconds"] for r in selected if not r["solved"]])
                )
                if any(not r["solved"] for r in selected)
                else None,
            )
    efficiencies = {}
    for phase in ("collection", "training"):
        blocks = [
            v for k, v in timings.items() if k.startswith(phase + ":") and v["complete"]
        ]
        efficiencies[phase] = (
            min(
                config["workers"],
                sum(v["worker_seconds"] for v in blocks)
                / max(1e-9, sum(v["wall_seconds"] for v in blocks)),
            )
            if blocks
            else None
        )
    projected = {}
    if all(v["n"] for v in throughput.values()) and all(efficiencies.values()):
        collection = (
            2048
            * throughput["collection:G4"]["mean_worker_seconds"]
            / efficiencies["collection"]
        )
        scoring = (
            1024
            * sum(throughput[f"training:{a}"]["mean_worker_seconds"] for a in ARMS)
            / efficiencies["training"]
        )
        fit_seconds = (
            float(
                np.mean(
                    [r["fit_seconds"] for r in corpora.values() if "fit_seconds" in r]
                )
            )
            * 16
        )
        # Serialization and dispatch are included in measured worker/wall efficiencies.
        overhead = 120
        partial_capped = []
        for arm in ("C_S", "T_S", "C_P"):
            rs = [r for r in rows if r["phase"] == "training" and r["arm"] == arm]
            caps = [r["worker_seconds"] for r in rs if not r["solved"]]
            partial_capped.append(
                float(np.mean(caps))
                if caps
                else max(r["worker_seconds"] * r["cap"] / r["evaluations"] for r in rs)
            )
        capped_scoring = (
            1024
            * (
                sum(partial_capped)
                + sum(
                    throughput[f"training:{a}"]["mean_worker_seconds"]
                    for a in ("C_exact", "G4")
                )
            )
            / efficiencies["training"]
        )
        total = collection + scoring + fit_seconds + overhead
        projected = dict(
            full_collection_seconds=collection,
            full_scoring_seconds=scoring,
            full_fit_seconds=fit_seconds,
            reporting_and_startup_reserve_seconds=overhead,
            full_total_seconds=total,
            full_total_minutes=total / 60,
            all_partial_capped_total_minutes=(
                collection + capped_scoring + fit_seconds + overhead
            )
            / 60,
            exceeds_210_minute_gate=total > 12600,
            extra_independent_corpus_seconds=(collection + scoring + fit_seconds) / 16,
            effective_workers=efficiencies,
            archive_verification_included=True,
            serialization_included=True,
            note="small-smoke mean projection; capped scenario is sensitivity, not a measured efficacy result",
        )
    return throughput, projected


def continuation_sizing(primary, n, projected):
    """Price precision at the observed contrasts, including unresolved G4 usefulness."""
    targets = {}
    for name, boundary in (("C_S/T_S", math.log(1.20)), ("C_S/G4", 0.0)):
        stat = primary[name]
        estimate = math.log(stat["speed_ratio"]) if stat["speed_ratio"] else None
        distances = {"exclude_no_gain": abs(estimate) if estimate is not None else None}
        if boundary:
            distances["exclude_worthwhile_margin"] = (
                boundary - estimate if estimate is not None else None
            )
        targets[name] = {}
        for label, distance in distances.items():
            target = (
                balanced_target_n(stat["sd_log"], distance, max(12, n))
                if distance and distance > 1e-12
                else None
            )
            extra = max(0, target - n) if target is not None else None
            targets[name][label] = dict(
                total_corpora=target,
                extra_balanced_corpora=extra,
                extra_queue_minutes=extra
                * projected["extra_independent_corpus_seconds"]
                / 60
                if extra is not None and projected
                else None,
            )
    return targets


def make_report(
    rows, corpora, config, completed_pairs, stop_kind, stop_reason, timings
):
    prefix = selected_prefix(completed_pairs)
    grouped = defaultdict(dict)
    for r in rows:
        if r["phase"] == "training" and r["corpus"] in prefix:
            key = (r["corpus"], r["cell"], r["arm"])
            if r["seed"] in grouped[key]:
                raise ValueError("duplicate scored seed")
            grouped[key][r["seed"]] = r
    for tid in prefix:
        for cid in TRAINING[tid[:2]]:
            seeds = None
            for arm in ARMS:
                group = grouped[tid, cid, arm]
                if len(group) != config["fresh_n"]:
                    raise ValueError("completed prefix missing scored cell")
                if seeds is not None and set(group) != seeds:
                    raise ValueError("unpaired endpoint")
                seeds = set(group)
    if any(
        r["phase"] not in ("collection", "training")
        or r["cell"] not in TRAINING[r["family"]]
        for r in rows
    ):
        raise ValueError("training-only scope violated")
    eligible = (
        not config["smoke_only"]
        and completed_pairs >= 6
        and (
            stop_kind == "timeout"
            or (stop_kind is None and completed_pairs == config["nc"])
        )
    )
    scored = [r for r in rows if r["phase"] == "training" and r["corpus"] in prefix]
    sensitivities = {
        f"unsolved_{penalty}x_cap": contrasts(grouped, prefix, penalty)
        for penalty in (2, 1)
    }
    sensitivities["both_solved"] = contrasts(grouped, prefix, both_solved=True)
    primary = sensitivities["unsolved_2x_cap"]
    outcome = route(primary["C_S/T_S"], primary["C_S/G4"], eligible)
    if config["smoke_only"]:
        outcome = dict(
            label="smoke", meaning="execution/throughput only; no efficacy inference"
        )
    throughput, projected = projection(rows, corpora, config, timings)
    target = balanced_target_n(
        primary["C_S/T_S"]["sd_log"], math.log(1.20), max(12, len(prefix))
    )
    extra = max(0, target - len(prefix)) if target is not None else None
    return dict(
        scope=config["method"]["scope"],
        method_hash=config["method_hash"],
        analysed_corpora=prefix,
        completed_pairs=completed_pairs,
        efficacy_eligible=eligible,
        stop_kind=stop_kind,
        stop_reason=stop_reason,
        outcome=outcome,
        total_searches=len(rows),
        observed_counts=dict(Counter(r["phase"] + ":" + r["arm"] for r in rows)),
        unanalysed_trailing_corpora=sorted(
            set(r["corpus"] for r in rows) - set(prefix)
        ),
        sensitivities=sensitivities,
        solves={arm: describe([r for r in scored if r["arm"] == arm]) for arm in ARMS},
        per_family={
            f: {
                a: describe([r for r in scored if r["family"] == f and r["arm"] == a])
                for a in ARMS
            }
            for f in TRAINING
        },
        almost_all_primary_capped=bool(scored)
        and all(
            np.mean([not r["solved"] for r in scored if r["arm"] == a]) >= 0.95
            for a in ("C_S", "T_S")
        ),
        cap_caution="near-universal caps make penalized equality uninformative about relative search behaviour",
        corpus_diagnostics={
            tid: tr.get("diagnostics", {}) for tid, tr in corpora.items()
        },
        throughput=throughput,
        projection=projected,
        sizing=dict(
            total_corpora_for_halfwidth_log_1_20=target,
            extra_balanced_corpora=extra,
            extra_queue_minutes=extra
            * projected["extra_independent_corpus_seconds"]
            / 60
            if extra is not None and projected
            else None,
            observed_effect_targets=continuation_sizing(
                primary, len(prefix), projected
            ),
            note="conditional on observed SD; new independent corpora, not additional scoring seeds",
        ),
    )


def save_report(out, report, rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    write_json(out, "result.json", report)
    lines = [
        "# Partial-program context training",
        "",
        f"Outcome: {report['outcome']['label']} — {report['outcome']['meaning']}",
        "",
        report["scope"],
        "",
        f"Analysed balanced prefix: {report['analysed_corpora']}",
        "",
        "| Comparison | Speed ratio | 95% corpus interval |",
        "|---|---:|---|",
    ]
    for name, stat in report["sensitivities"]["unsolved_2x_cap"].items():
        lines.append(f"| {name} | {stat['speed_ratio']} | {stat['interval_95']} |")
    lines += [
        "",
        report["cap_caution"],
        "C_S/C_P tests extra parent enrichment; populations already experienced evolution.",
        "C_exact has a different acquisition budget. No isolated-order, inheritance or fresh-transfer claim.",
        f"Stop: {report['stop_kind']}: {report['stop_reason']}",
        f"Measured full-run projection: {report['projection']}",
        "Solve rates, sensitivities, archive diagnostics and additional-corpus price: result.json.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for arm in ARMS:
        selected = [
            r
            for r in rows
            if r["phase"] == "training"
            and r["arm"] == arm
            and r["corpus"] in report["analysed_corpora"]
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
            "D1331-exact fraction",
            "Best correct training cases (active runs)",
            "Behavioural diversity (active runs)",
        ),
    ):
        axis.set(xlabel="Evaluations", ylabel=label, xscale="log")
        if axis.lines:
            axis.legend()
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    plt.close(fig)
