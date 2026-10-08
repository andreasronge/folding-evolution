"""Corpus-level intervals, matched D shrinkage, censoring-aware interpretation."""

from collections import Counter, defaultdict
import math

import numpy as np
from scipy.stats import t

from experiments.chem_tape.comparison_gate_bank import TRAINING
from experiments.chem_tape.comparison_gate_report import (
    interval,
    describe,
    balanced_target_n,
    selected_prefix,
)
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.solver_corpus_report import cost


def difference_interval(values):
    """Arithmetic interval for a difference on the log-ratio scale."""
    r = interval(values)
    return dict(
        n=r["n"],
        difference_log=float(np.mean(values)) if len(values) else None,
        interval_95_log=[math.log(v) for v in r["interval_95"]]
        if r["interval_95"]
        else None,
        ratio_of_ratios=r["speed_ratio"],
        interval_95_ratio=r["interval_95"],
    )


def family_difference(scores):
    """Independent source-family contrast, Welch interval (BE minus PA)."""
    x, y = [
        np.asarray([v for tid, v in scores.items() if tid.startswith(f)], dtype=float)
        for f in TRAINING
    ]
    if len(x) < 2 or len(y) < 2:
        return dict(n_BE=len(x), n_PA=len(y), difference_log=None, interval_95_log=None)
    vx, vy = x.var(ddof=1) / len(x), y.var(ddof=1) / len(y)
    se = np.sqrt(vx + vy)
    df = (
        (vx + vy) ** 2 / (vx**2 / (len(x) - 1) + vy**2 / (len(y) - 1))
        if se
        else len(x) + len(y) - 2
    )
    width = t.ppf(0.975, df) * se
    delta = float(x.mean() - y.mean())
    return dict(
        n_BE=len(x),
        n_PA=len(y),
        difference_log=delta,
        interval_95_log=[float(delta - width), float(delta + width)],
        df=float(df),
    )


def route(ct, eligible, shared_censoring, row):
    if not eligible:
        return dict(
            label="incomplete",
            meaning="too few complete balanced pairs or execution error; no efficacy decision",
        )
    bounds = ct["interval_95"]
    if bounds[0] > 1:
        label = (
            "resolved_gain_below_10_percent"
            if bounds[1] < 1.10
            else "resolved_relative_gain"
        )
        meaning = "C advantage over restricted T on this frozen bank at this cap"
    elif bounds[1] < 1.10:
        label = "bounded_small_gain"
        meaning = "gain bounded below 10% at this cap; consistent with shape specificity, cause not identified"
    else:
        label, meaning = (
            "unresolved",
            "interval spans no gain and a potentially useful gain",
        )
    if shared_censoring:
        return dict(
            label="capped_endpoint",
            numeric_label=label,
            meaning="both arms solve fewer than 25%; numerical ratio describes capped costs, useful uncapped transfer unresolved",
        )
    if row == "D":
        meaning += (
            "; within-shape generalization on a development bank, no transfer claim"
        )
    else:
        meaning += "; scope is the deliberately selected then-addition bank"
    return dict(label=label, meaning=meaning)


def key(row):
    return tuple(row[k] for k in ("phase", "family", "corpus", "cell", "arm", "seed"))


def make_report(
    rows,
    schedule,
    training_rows,
    config,
    completed_pairs,
    g4_complete,
    stop_kind,
    stop_reason,
    timings,
):
    prefix = selected_prefix(completed_pairs)
    expected = {
        key(r)
        for r in schedule
        if r["corpus"] in prefix or (g4_complete and r["arm"] == "G4")
    }
    selected = [
        r for r in rows if r["corpus"] in prefix or (g4_complete and r["arm"] == "G4")
    ]
    if len(selected) != len(expected) or {key(r) for r in selected} != expected:
        raise ValueError("completed prefix roster missing/duplicate/extra rows")
    grouped = defaultdict(list)
    for r in selected:
        grouped[r["corpus"], r["cell"], r["arm"]].append(r)
    cells = sorted({r["cell"] for r in schedule})
    corpus_cells = {
        tid: sorted({r["cell"] for r in schedule if r["corpus"] == tid})
        for tid in prefix
    }
    training = defaultdict(list)
    for r in training_rows:
        if r["phase"] == "training" and r["arm"] in ("C", "T"):
            if r["cell"] not in TRAINING[r["family"]]:
                raise ValueError("source training family mismatch")
            training[r["corpus"], r["cell"], r["arm"]].append(r)

    def contrast(groups, tid, cids, penalty):
        values = []
        for cid in cids:
            pair = {a: {r["seed"]: r for r in groups[tid, cid, a]} for a in ("C", "T")}
            if not pair["C"] or pair["C"].keys() != pair["T"].keys():
                raise ValueError("unpaired or empty corpus-cell endpoint")
            values.append(
                float(
                    np.mean(
                        [
                            np.log(cost(pair["T"][s], penalty))
                            - np.log(cost(pair["C"][s], penalty))
                            for s in pair["C"]
                        ]
                    )
                )
            )
        return float(np.mean(values))

    eligible = (
        not config["smoke_only"]
        and g4_complete
        and completed_pairs >= 6
        and (
            stop_kind == "timeout"
            or (stop_kind is None and completed_pairs == config["nc"])
        )
    )
    observed_corpora = {r["corpus"] for r in rows if r["arm"] != "G4"}
    trailing = [r for r in rows if r["corpus"] not in prefix and r["arm"] != "G4"]
    report = dict(
        row=config["row"],
        smoke_only=config["smoke_only"],
        analysed_corpora=prefix,
        completed_pairs=completed_pairs,
        completed_corpora=len(prefix),
        g4_complete=g4_complete,
        full_row_complete=completed_pairs == config["nc"]
        and g4_complete
        and stop_kind is None,
        efficacy_eligible=eligible,
        stop_kind=stop_kind,
        stop_reason=stop_reason,
        total_searches=len(rows),
        observed_counts=dict(Counter(r["arm"] for r in rows)),
        trailing_corpora=sorted(observed_corpora - set(prefix)),
        trailing_search_summary=describe(trailing),
        scope="C versus restricted T; bank-conditional corpus uncertainty; no isolated token-order effect",
        method_hash=config["method_hash"],
        sensitivities={},
    )
    for penalty in (2, 1):
        scores = {
            tid: contrast(grouped, tid, corpus_cells[tid], penalty) for tid in prefix
        }
        ct = interval(list(scores.values()))
        ct.update(
            corpus_scores_log=scores,
            equal_family_weight=True,
            families={
                f: interval([v for tid, v in scores.items() if tid.startswith(f)])
                for f in TRAINING
            },
        )
        per_cell = {}
        for cid in cells:
            tids = [tid for tid in prefix if cid in corpus_cells[tid]]
            per_cell[cid] = dict(
                C_T=interval([contrast(grouped, tid, [cid], penalty) for tid in tids]),
                arms={
                    a: describe(
                        [r for r in selected if r["cell"] == cid and r["arm"] == a],
                        penalty,
                    )
                    for a in ("C", "T", "G4")
                },
            )
        arms = {
            a: describe([r for r in selected if r["arm"] == a], penalty)
            for a in ("C", "T", "G4")
        }
        ratios_g4 = {}
        for a in ("C", "T"):
            vals = []
            for tid in prefix:
                values = []
                for cid in corpus_cells[tid]:
                    g = grouped["G4", cid, "G4"]
                    if not g:
                        continue
                    values.append(
                        np.mean([np.log(cost(r, penalty)) for r in g])
                        - np.mean(
                            [np.log(cost(r, penalty)) for r in grouped[tid, cid, a]]
                        )
                    )
                if values:
                    vals.append(float(np.mean(values)))
            ratios_g4[a + "_G4"] = interval(vals)
        train_scores = {
            tid: contrast(training, tid, TRAINING[tid[:2]], penalty) for tid in prefix
        }
        secondary = dict(
            source_family_BE_minus_PA=family_difference(scores),
            target_minus_own_family_training=difference_interval(
                [scores[tid] - train_scores[tid] for tid in prefix]
            ),
            own_family_training_C_T=interval(list(train_scores.values())),
        )
        if config["row"] == "D" and not config["smoke_only"]:
            matched, mismatched = {}, {}
            for tid in prefix:
                matched[tid] = contrast(
                    grouped,
                    tid,
                    [c for c in corpus_cells[tid] if c.startswith(tid[:2] + ":")],
                    penalty,
                )
                mismatched[tid] = contrast(
                    grouped,
                    tid,
                    [c for c in corpus_cells[tid] if not c.startswith(tid[:2] + ":")],
                    penalty,
                )
            secondary.update(
                matched_C_T=interval(list(matched.values())),
                mismatched_C_T=interval(list(mismatched.values())),
                matched_minus_mismatched=difference_interval(
                    [matched[tid] - mismatched[tid] for tid in prefix]
                ),
                own_family_holdout_minus_training=difference_interval(
                    [matched[tid] - train_scores[tid] for tid in prefix]
                ),
                matched_corpus_scores_log=matched,
                mismatched_corpus_scores_log=mismatched,
                per_source_family={
                    f: dict(
                        matched_C_T=interval(
                            [matched[tid] for tid in prefix if tid.startswith(f)]
                        ),
                        mismatched_C_T=interval(
                            [mismatched[tid] for tid in prefix if tid.startswith(f)]
                        ),
                        matched_minus_mismatched=difference_interval(
                            [
                                matched[tid] - mismatched[tid]
                                for tid in prefix
                                if tid.startswith(f)
                            ]
                        ),
                        own_family_holdout_minus_training=difference_interval(
                            [
                                matched[tid] - train_scores[tid]
                                for tid in prefix
                                if tid.startswith(f)
                            ]
                        ),
                    )
                    for f in TRAINING
                },
            )
        loo = {}
        for cid in cells:
            if prefix and all(len(corpus_cells[tid]) > 1 for tid in prefix):
                loo[cid] = interval(
                    [
                        contrast(
                            grouped,
                            tid,
                            [c for c in corpus_cells[tid] if c != cid],
                            penalty,
                        )
                        for tid in prefix
                    ]
                )
        report["sensitivities"][f"unsolved_{penalty}cap"] = dict(
            C_T=ct,
            arms=arms,
            per_cell=per_cell,
            cells_with_C_T_above_one=sum(
                v["C_T"]["speed_ratio"] is not None and v["C_T"]["speed_ratio"] > 1
                for v in per_cell.values()
            ),
            leave_one_cell_out=loo,
            leave_one_cell_out_range=[
                min(v["speed_ratio"] for v in loo.values()),
                max(v["speed_ratio"] for v in loo.values()),
            ]
            if loo
            else None,
            descriptive_unpaired_baselines=ratios_g4,
            baseline_interval_limitation="corpus variation only; independent G4 sampling uncertainty omitted",
            secondaries=secondary,
        )
    primary = report["sensitivities"]["unsolved_2cap"]
    shared = all(primary["arms"][a].get("solve_rate", 0) < 0.25 for a in ("C", "T"))
    report["shared_low_solve_guard"] = shared
    report["censoring_caution"] = (
        "25% is an interpretive flag; higher solve rates do not eliminate capped-endpoint distortion"
    )
    report["outcome"] = route(primary["C_T"], eligible, shared, config["row"])
    baselines = primary["descriptive_unpaired_baselines"]
    report["both_fits_costlier_than_G4"] = all(
        baselines[a + "_G4"]["speed_ratio"] is not None
        and baselines[a + "_G4"]["speed_ratio"] < 1
        for a in ("C", "T")
    )
    report["G4_interpretation"] = (
        "Both fits have higher capped geometric cost than G4; C/T superiority alone does not establish useful adaptation against G4"
        if report["both_fits_costlier_than_G4"]
        else "See per-arm and per-cell solve counts and descriptive unpaired G4 cost contrasts"
    )
    if config["smoke_only"]:
        report["outcome"] = dict(
            label="smoke_only",
            meaning="training-only infrastructure check; no target efficacy decision",
        )
    ct = primary["C_T"]
    n = len(prefix)
    effect = math.log(ct["speed_ratio"]) if ct["speed_ratio"] else 0
    targets = dict(
        precision_1_10=balanced_target_n(ct["sd_log"], math.log(1.10), n),
        observed_effect=balanced_target_n(ct["sd_log"], abs(effect), n),
    )
    worker_seconds = sum(r["seconds"] for r in rows)
    wall = sum(v["wall_seconds"] for v in timings.values())
    effective = worker_seconds / wall if wall else None
    scoring = worker_seconds / len(rows) if rows else None
    per_corpus_searches = sum(r["corpus"] == "BE1" for r in schedule)
    price = (
        423 + scoring * per_corpus_searches / max(effective, 1)
        if effective and scoring
        else None
    )
    report["sizing"] = dict(
        total_corpora_needed=targets,
        extra_balanced_corpora={
            k: max(0, v - n) if v is not None else None for k, v in targets.items()
        },
        approximate_only=True,
        acquisition_seconds_per_corpus=423,
        measured_scoring_seconds_per_corpus=price - 423 if price else None,
        total_seconds_per_extra_corpus=price,
        effective_workers=effective,
    )
    return report


def save_report(out, report, rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for arm in ("C", "T", "G4"):
        selected = [
            r
            for r in rows
            if r["arm"] == arm
            and (
                r["corpus"] in report["analysed_corpora"]
                or (arm == "G4" and report["g4_complete"])
            )
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
        for ax, i in ((axes[1], 0), (axes[2], 1)):
            ax.plot(x, [np.median([v[i] for v in points[ev]]) for ev in x], label=arm)
    for ax, label in zip(
        axes,
        (
            "Fraction D1331-exact",
            "Median best correct cases (active runs)",
            "Median behavioural diversity (active runs)",
        ),
    ):
        ax.set(xlabel="Evaluations", ylabel=label, xscale="log")
        if ax.lines:
            ax.legend()
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    plt.close(fig)
    write_json(out, "result.json", report)
    lines = [
        f"# Frozen-map row {report['row']}",
        "",
        f"Outcome: {report['outcome']['label']} — {report['outcome']['meaning']}",
        "",
        report["scope"],
        "",
        f"Complete pairs/corpora: {report['completed_pairs']}/{report['completed_corpora']}; analysed: {report['analysed_corpora']}.",
        f"Stop: {report['stop_kind']}: {report['stop_reason']}",
        "",
        "| Unsolved cost | C/T capped cost ratio | 95% corpus interval | C solves | T solves | G4 solves |",
        "|---|---:|---|---|---|---|",
    ]
    for name, val in report["sensitivities"].items():
        a = val["arms"]
        lines.append(
            f"| {name} | {val['C_T']['speed_ratio']} | {val['C_T']['interval_95']} | {a['C'].get('solved', 0)}/{a['C']['n']} | {a['T'].get('solved', 0)}/{a['T']['n']} | {a['G4'].get('solved', 0)}/{a['G4']['n']} |"
        )
    lines += [
        "",
        f"Shared low-solve guard: {report['shared_low_solve_guard']}. {report['censoring_caution']}",
        report["G4_interpretation"],
        "",
        "K is unscored. G4 contrasts are descriptive and unpaired; the corpus interval omits G4 sampling uncertainty.",
        "Per-cell solve counts, leave-one-cell-out range, source-family and matched-family shrinkage intervals, and extra-corpus pricing are in result.json.",
        "A bounded gain limits this selected bank at this cap; branch placement is not isolated from gate/behaviour selection.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
