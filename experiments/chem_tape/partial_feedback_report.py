"""2116: complete-lineage endpoints, acquisition diagnostics and smoke pricing."""

import math
from collections import defaultdict

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

CONTRASTS = (
    ("F", "O"),
    ("F", "R"),
    ("O", "R"),
    ("F", "TF"),
    ("TF", "G4"),
    ("F", "G4"),
    ("F", "C_exact"),
)


def route(stat, eligible):
    if not eligible:
        return dict(
            label="incomplete", meaning="all16 lineages required; no efficacy decision"
        )
    lo, hi = stat["interval_95"]
    if hi < 1:
        return dict(label="degradation", meaning="feedback degrades; cause unisolated")
    if hi < 1.15:
        return dict(
            label="small_gain", meaning="worthwhile gain excluded; prefer one-shot"
        )
    if lo > 1:
        if stat["speed_ratio"] >= 1.15:
            return dict(
                label="adopt_feedback",
                worthwhile_established=lo > 1.15,
                meaning="resolved improvement; point>=1.15; adopt feedback provisionally unless worthwhile gain established",
            )
        return dict(
            label="resolved_small_estimate",
            meaning="resolved improvement but point<1.15; prefer one-shot at estimate, practical magnitude unresolved",
        )
    return dict(
        label="unresolved",
        meaning="acquisition route unresolved; price resolution; no automatic follow-up",
    )


def contrasts(grouped, prefix, arms, penalty=2, both_solved=False):
    result = {}
    for left, right in CONTRASTS:
        if right not in arms:
            continue
        values, cells, pairs = {}, defaultdict(dict), {}
        for tid in prefix:
            means = []
            counts = 0
            for cid in TRAINING[tid[:2]]:
                left_rows, right_rows = (
                    grouped[tid, cid, left],
                    grouped[tid, cid, right],
                )
                seeds = [
                    s
                    for s in left_rows
                    if not both_solved
                    or (left_rows[s]["solved"] and right_rows[s]["solved"])
                ]
                counts += len(seeds)
                if seeds:
                    value = float(
                        np.mean(
                            [
                                math.log(cost(right_rows[s], penalty))
                                - math.log(cost(left_rows[s], penalty))
                                for s in seeds
                            ]
                        )
                    )
                    means.append(value)
                    cells[cid][tid] = value
            if means:
                values[tid] = float(np.mean(means))
            pairs[tid] = counts
        stat = interval(list(values.values()))
        stat.update(
            lineage_scores_log=values,
            paired_searches=pairs,
            families={
                f: interval([v for tid, v in values.items() if tid.startswith(f)])
                for f in TRAINING
            },
            cells={c: interval(list(v.values())) for c, v in cells.items()},
            conditional_on_both_solved=both_solved,
            note="success-conditioned; may omit cells/lineages"
            if both_solved
            else "equal cells and paired seeds within lineage",
        )
        result[f"{left}/{right}"] = stat
    return result


def projection(rows, corpora, config, timings):
    throughput = {}
    for phase, round_, arms in (
        ("collection", 1, ("G4",)),
        ("collection", 2, ("F", "TF", "O")),
        ("collection", 3, ("F", "TF", "O")),
        ("training", 4, config["arms"]),
    ):
        for arm in arms:
            rs = [
                r
                for r in rows
                if r["phase"] == phase and r["round"] == round_ and r["arm"] == arm
            ]
            throughput[f"r{round_}:{arm}"] = dict(
                n=len(rs),
                solved=sum(r["solved"] for r in rs),
                actual_evaluations=sum(r["evaluations"] for r in rs),
                contributing_sources=sum(
                    any(a["kind"] == "S" for a in r.get("archive", [])) for r in rs
                )
                if phase == "collection"
                else None,
                mean_worker_seconds=float(np.mean([r["worker_seconds"] for r in rs]))
                if rs
                else None,
            )
    efficiency = {}
    for phase in ("collection", "training"):
        blocks = [
            v for k, v in timings.items() if k.startswith(phase + ":") and v["complete"]
        ]
        efficiency[phase] = (
            min(
                config["workers"],
                sum(v["worker_seconds"] for v in blocks)
                / max(1e-9, sum(v["wall_seconds"] for v in blocks)),
            )
            if blocks
            else None
        )
    if not all(v["n"] for v in throughput.values()) or not all(efficiency.values()):
        return throughput, {}
    replay = (
        2048 * throughput["r1:G4"]["mean_worker_seconds"] / efficiency["collection"]
    )
    acquisition = (
        2048
        * sum(
            throughput[f"r{r}:{a}"]["mean_worker_seconds"]
            for r in (2, 3)
            for a in ("F", "TF", "O")
        )
        / efficiency["collection"]
    )
    scores = {
        a: 1024 * throughput[f"r4:{a}"]["mean_worker_seconds"] / efficiency["training"]
        for a in config["arms"]
    }
    fit_times = [
        sum(
            e["fit_seconds"] for round_ in c["rounds"].values() for e in round_.values()
        )
        for c in corpora.values()
        if len(c.get("rounds", {})) == 3
    ]
    fitting = 16 * float(np.mean(fit_times)) if fit_times else 0
    # Checkpoint writes occur outside jobs/fit timers. Project their measured cost
    # per lineage together with orchestration; reserve a minimum two minutes.
    measured = sum(v["wall_seconds"] for v in timings.values() if "rows" in v) + sum(
        fit_times
    )
    elapsed = sum(
        v["wall_seconds"] for k, v in timings.items() if k == "orchestration_elapsed"
    )
    overhead = max(120, max(0, elapsed - measured) * 16 / max(1, len(fit_times)) + 120)
    total = replay + acquisition + sum(scores.values()) + fitting + overhead
    without_exact = total - scores.get("C_exact", 0)
    return throughput, dict(
        full_replay_seconds=replay,
        full_new_collection_seconds=acquisition,
        full_scoring_seconds=scores,
        full_fit_seconds=fitting,
        orchestration_and_reporting_reserve_seconds=overhead,
        full_total_seconds=total,
        full_total_minutes=total / 60,
        without_exact_total_minutes=without_exact / 60,
        exceeds_240_minute_gate=total > 14400,
        effective_workers=efficiency,
        archive_verification_included=True,
        serialization_included=True,
        extra_independent_lineage_seconds=total / 16,
        note="small-smoke mean projection; not efficacy evidence",
    )


def make_report(
    rows, corpora, config, completed_pairs, stop_kind, stop_reason, timings
):
    prefix = selected_prefix(completed_pairs)
    grouped = defaultdict(dict)
    for r in rows:
        if r["cell"] not in TRAINING[r["family"]] or r["phase"] not in (
            "collection",
            "training",
        ):
            raise ValueError("training-only scope violated")
        if r["phase"] == "training" and r["corpus"] in prefix:
            key = (r["corpus"], r["cell"], r["arm"])
            if r["seed"] in grouped[key]:
                raise ValueError("duplicate scored seed")
            grouped[key][r["seed"]] = r
    for tid in prefix:
        for cid in TRAINING[tid[:2]]:
            sets = [set(grouped[tid, cid, a]) for a in config["arms"]]
            if any(len(s) != config["fresh_n"] or s != sets[0] for s in sets):
                raise ValueError("missing/unpaired scored cell")
    sensitivity = {
        f"unsolved_{p}x_cap": contrasts(grouped, prefix, config["arms"], p)
        for p in (2, 1)
    }
    sensitivity["both_solved"] = contrasts(
        grouped, prefix, config["arms"], both_solved=True
    )
    stat = sensitivity["unsolved_2x_cap"]["F/O"]
    eligible = not config["smoke_only"] and completed_pairs == 8 and stop_kind is None
    outcome = route(stat, eligible)
    if config["smoke_only"]:
        outcome = dict(
            label="smoke", meaning="validation/throughput only; no efficacy inference"
        )
    scored = [r for r in rows if r["phase"] == "training" and r["corpus"] in prefix]
    throughput, projected = projection(rows, corpora, config, timings)
    targets = {}
    for boundary in (1.0, 1.15):
        distance = (
            abs(math.log(stat["speed_ratio"] / boundary))
            if stat["speed_ratio"]
            else None
        )
        target = (
            balanced_target_n(stat["sd_log"], distance, max(16, len(prefix)))
            if distance
            else None
        )
        extra = max(0, target - len(prefix)) if target else None
        targets[str(boundary)] = dict(
            total_lineages=target,
            additional_lineages=extra,
            extra_queue_minutes=extra
            * projected["extra_independent_lineage_seconds"]
            / 60
            if extra is not None and projected
            else None,
        )
    payback = {}
    for arm in ("F", "O", "TF"):
        extra = sum(
            e[arm]["collection_evaluations"]
            for c in corpora.values()
            for r, e in c.get("rounds", {}).items()
            if r in ("2", "3")
        )
        savings = [
            cost(grouped[t, c, "R"][s], 2) - cost(row, 2)
            for (t, c, a), values in grouped.items()
            if a == arm
            for s, row in values.items()
        ]
        saving = float(np.mean(savings)) if savings else None
        payback[arm] = dict(
            extra_acquisition_evaluations=extra,
            mean_penalized_saving_vs_R=saving,
            future_searches_to_repay=extra / saving if saving and saving > 0 else None,
            note="penalized-cost accounting (2*cap for failures), not actual evaluation savings",
        )
    return dict(
        scope=config["method"]["scope"],
        method_hash=config["method_hash"],
        analysed_lineages=prefix,
        efficacy_eligible=eligible,
        outcome=outcome,
        stop_kind=stop_kind,
        stop_reason=stop_reason,
        total_searches=len(rows),
        sensitivities=sensitivity,
        solves={
            a: describe([r for r in scored if r["arm"] == a]) for a in config["arms"]
        },
        per_family={
            f: {
                a: describe([r for r in scored if r["family"] == f and r["arm"] == a])
                for a in config["arms"]
            }
            for f in TRAINING
        },
        per_cell={
            c: {
                a: describe([r for r in scored if r["cell"] == c and r["arm"] == a])
                for a in config["arms"]
            }
            for cells in TRAINING.values()
            for c in cells
        },
        almost_all_primary_capped=bool(scored)
        and all(
            np.mean([not r["solved"] for r in scored if r["arm"] == a]) >= 0.95
            for a in ("F", "O")
        ),
        cap_caution="near-universal caps are uninformative about relative search behavior; unresolved is not equality",
        throughput=throughput,
        projection=projected,
        sizing=targets,
        payback=payback,
    )


def save_report(out, report, rows):
    # Reuse legacy plotting; its fixed arm list is adapted through explicit config.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    write_json(out, "result.json", report)
    lines = [
        "# Partial-program feedback training",
        "",
        str(report["outcome"]),
        "",
        report["scope"],
        "",
        "| Comparison | Cost ratio | 95% lineage interval |",
        "|---|---:|---|",
    ]
    for name, stat in report["sensitivities"]["unsolved_2x_cap"].items():
        lines.append(f"| {name} | {stat['speed_ratio']} | {stat['interval_95']} |")
    lines.extend(
        [
            "",
            report["cap_caution"],
            "",
            "F/O bundles source yield and tape contents. C_exact has unmatched acquisition cost. No order, transfer or inheritance claim.",
            "",
            f"Runtime projection: {report['projection']}",
            "",
            f"Stop: {report['stop_kind']}: {report['stop_reason']}",
            "",
            "Per-round diagnostics/counts/entropy: corpora.json; solves, sensitivities and payback: result.json.",
        ]
    )
    (out / "report.md").write_text("\n".join(lines) + "\n")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for arm in report["solves"]:
        selected = [
            r
            for r in rows
            if r["phase"] == "training"
            and r["arm"] == arm
            and r["corpus"] in report["analysed_lineages"]
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
        for ax, idx in ((axes[1], 0), (axes[2], 1)):
            ax.plot(x, [np.median([v[idx] for v in points[ev]]) for ev in x], label=arm)
    for ax, label in zip(
        axes,
        (
            "D1331-exact fraction",
            "Best training correct (active)",
            "Behavior diversity (active)",
        ),
    ):
        ax.set(xlabel="Evaluations", ylabel=label, xscale="log")
        if ax.lines:
            ax.legend()
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    plt.close(fig)
