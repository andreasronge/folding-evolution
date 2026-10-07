"""1707 corpus-level intervals and descriptive arithmetic amortization."""

import math
import numpy as np
from scipy.stats import t

from experiments.chem_tape.crossed_learning_run import TRAINING, HOLDOUTS
from experiments.chem_tape.composition_run import write_json


def cost(row, penalty=2):
    return row["evaluations"] if row["solved"] else penalty * row["cap"]


def interval(mean, se, df):
    if not np.isfinite(mean):
        return dict(
            delta_log2=None, speed_ratio=None, interval_95=None, se_log2=None, df=None
        )
    if df <= 0 or not np.isfinite(se):
        return dict(
            delta_log2=float(mean),
            speed_ratio=float(2 ** (-mean)),
            interval_95=None,
            se_log2=None,
            df=None,
        )
    width = float(t.ppf(0.975, df) * se)
    return dict(
        delta_log2=float(mean),
        speed_ratio=float(2 ** (-mean)),
        interval_95=[float(2 ** (-mean - width)), float(2 ** (-mean + width))],
        se_log2=float(se),
        half_width_log2=width,
        df=float(df),
    )


def moments(x):
    x = np.asarray(x, dtype=float)
    if not len(x):
        return float("nan"), float("nan"), -1
    return (
        float(x.mean()),
        float(x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 else float("nan"),
        len(x) - 1,
    )


def one_sample(x):
    out = interval(*moments(x))
    out.update(
        n=len(x),
        sd_log2=float(np.std(x, ddof=1)) if len(x) > 1 else None,
        contrasts_log2=[float(v) for v in x],
    )
    return out


def pooled(groups):
    fam = {f: one_sample(x) for f, x in groups.items()}
    m = [moments(groups[f]) for f in ("BE", "PA")]
    estimate = interval(
        (m[0][0] + m[1][0]) / 2,
        np.sqrt(m[0][1] ** 2 + m[1][1] ** 2) / 2,
        min(m[0][2], m[1][2]),
    )
    return dict(pooled=estimate, families=fam, equal_family_weight=True)


def welch(x, y):
    mx, sx, dx = moments(x)
    my, sy, dy = moments(y)
    se = np.sqrt(sx * sx + sy * sy)
    if dx <= 0 or dy <= 0:
        return interval(mx - my, se, 0)
    denom = sx**4 / dx + sy**4 / dy
    df = (sx * sx + sy * sy) ** 2 / denom if denom else min(dx, dy)
    return interval(mx - my, se, df)


def gain(r):
    return r.get("interval_95") is not None and r["interval_95"][0] > 1


def label(r):
    bounds = r.get("interval_95")
    if not bounds:
        return "unresolved"
    if bounds[0] > 1:
        return "transfer"
    if bounds[1] < 1.10:
        return "no transfer above 10%"
    return "unresolved"


def outcome(ct, subset_ct, ck, feasible):
    if not feasible:
        return dict(
            row=0, meaning="infeasible or incomplete stage 1; no comparison claim"
        )
    if gain(ct):
        if gain(subset_ct) and gain(ck):
            return dict(
                row=1,
                meaning="procedure improvement; increment beyond pooled emitted frequencies on K-valid corpora",
            )
        return dict(
            row=2,
            meaning="procedure improvement; frequency versus additional context unresolved",
        )
    if ct.get("interval_95") and ct["interval_95"][1] < 1.10:
        return dict(
            row=3, meaning="this full-tape fit adds no gain above 10% over token fit"
        )
    return dict(row=4, meaning="unresolved; further independent corpora needed")


def corpus_scores(rows, corpora, phase, penalty):
    grouped = {}
    for r in rows:
        if r["phase"] == phase:
            grouped.setdefault((r["corpus"], r["arm"], r["cell"]), []).append(r)
    scores = {}
    for tid, tr in corpora.items():
        cells = (
            TRAINING[tr["family"]]
            if phase == "training"
            else sum(HOLDOUTS.values(), [])
        )
        scores[tid] = {}
        for arm in ("T", "C", "K"):
            if arm == "K" and not tr["fit"]["K_valid"]:
                continue
            scores[tid][arm] = {
                c: float(
                    np.mean([np.log2(cost(r, penalty)) for r in grouped[tid, arm, c]])
                )
                for c in cells
            }
    return scores, grouped


def contrast(scores, corpora, a, b, subset=False, holdout=False):
    groups = {f: [] for f in TRAINING}
    for tid, s in scores.items():
        if (subset or b == "K") and not corpora[tid]["fit"]["K_valid"]:
            continue
        groups[corpora[tid]["family"]].append(
            float(np.mean([s[a][c] - s[b][c] for c in s[a]]))
        )
    if holdout:
        return one_sample(groups["BE"] + groups["PA"])
    return pooled(groups)


def reference(grouped, family, phase, penalty):
    cells = TRAINING[family] if phase == "training" else sum(HOLDOUTS.values(), [])
    rs = [grouped["G4", "G4", c] for c in cells]
    ms = [moments([np.log2(cost(r, penalty)) for r in cell]) for cell in rs]
    return (
        float(np.mean([v[0] for v in ms])),
        float(np.sqrt(sum(v[1] ** 2 for v in ms)) / len(cells)),
        min(v[2] for v in ms),
    )


def versus_g4(scores, grouped, corpora, phase, penalty):
    out = {}
    for arm in ("T", "C"):
        fs = {}
        parts = []
        fitted_variances = []
        for family in TRAINING:
            x = [
                np.mean(list(s[arm].values()))
                for tid, s in scores.items()
                if corpora[tid]["family"] == family
            ]
            mx, sx, dx = moments(x)
            my, sy, dy = reference(grouped, family, phase, penalty)
            se = np.sqrt(sx * sx + sy * sy)
            denom = sx**4 / dx + sy**4 / dy if dx > 0 and dy > 0 else 0
            df = (sx * sx + sy * sy) ** 2 / denom if denom else min(dx, dy)
            fs[family] = interval(mx - my, se, df)
            parts.append((mx - my, se, df))
            fitted_variances.append(sx * sx)
        pooled_se = np.sqrt(sum(p[1] ** 2 for p in parts)) / 2
        if phase == "holdout":
            # Both corpus families share this single G4 reference. Its variance
            # remains whole when the two fitted-family means are averaged.
            pooled_se = np.sqrt(sum(fitted_variances) / 4 + sy * sy)
        p = interval(
            np.mean([p[0] for p in parts]),
            pooled_se,
            min(p[2] for p in parts),
        )
        out[arm + "/G4"] = dict(pooled=p, families=fs)
    return out


def amortization(rows, corpora, phase, penalty):
    out = {}
    for tid, tr in corpora.items():
        family = tr["family"]
        cells = TRAINING[family] if phase == "training" else sum(HOLDOUTS.values(), [])

        def mean(arm, field, corpus):
            return float(
                np.mean(
                    [
                        np.mean(
                            [
                                cost(r, penalty)
                                if field == "evaluations"
                                else r["seconds"]
                                for r in rows
                                if r["phase"] == phase
                                and r["corpus"] == corpus
                                and r["arm"] == arm
                                and r["cell"] == c
                            ]
                        )
                        for c in cells
                    ]
                )
            )

        out[tid] = {}
        for arm in ("T", "C"):
            ev = mean("G4", "evaluations", "G4") - mean(arm, "evaluations", tid)
            sec = mean("G4", "seconds", "G4") - mean(arm, "seconds", tid)
            out[tid][arm] = dict(
                mean_capped_evaluations_saved=ev,
                mean_seconds_saved=sec,
                break_even_searches_evaluations=math.ceil(
                    tr["collection_evaluations"] / ev
                )
                if ev > 0
                else None,
                break_even_searches_seconds=math.ceil(
                    (tr["collection_seconds"] + tr["fit_seconds"]) / sec
                )
                if sec > 0
                else None,
                collection_evaluations=tr["collection_evaluations"],
                collection_plus_all_fitting_seconds=tr["collection_seconds"]
                + tr["fit_seconds"],
                note="None means no finite break-even at this cap; all fitting charged conservatively",
            )
    return out


def make_report(rows, corpora, config, stage1, stage2, validation, reason):
    report = dict(
        config=config,
        validation=validation,
        stop_reason=reason,
        stage1_complete=stage1,
        stage2_complete=stage2,
        scope="External full-tape fitting, not evolutionary discovery; K matches uniform-latent position-pooled frequencies.",
        K_exclusions={
            f: [
                tid
                for tid, tr in corpora.items()
                if tr["family"] == f and not tr.get("fit", {}).get("K_valid", False)
            ]
            for f in TRAINING
        },
        outcome=outcome({}, {}, {}, False),
        sensitivities={},
    )
    feasible = (
        stage1
        and validation["passed"]
        and not (config["smoke_only"] or config["probe_only"])
    )
    if not stage1:
        return report
    for penalty in (2, 1):
        scores, grouped = corpus_scores(rows, corpora, "training", penalty)
        ct = contrast(scores, corpora, "C", "T")
        subset_ct = contrast(scores, corpora, "C", "T", subset=True)
        ck = contrast(scores, corpora, "C", "K")
        readout = dict(
            C_T=ct,
            K_valid_C_T=subset_ct,
            C_K=ck,
            reference=versus_g4(scores, grouped, corpora, "training", penalty),
            amortization=amortization(rows, corpora, "training", penalty),
            corpus_scores=scores,
        )
        # Independent procedures, with equal cells within each own-family map.
        readout["T_M"] = {}
        for family in TRAINING:
            x = [
                np.mean(list(s["T"].values()))
                for tid, s in scores.items()
                if corpora[tid]["family"] == family
            ]
            mids = sorted(
                {
                    r["corpus"]
                    for r in rows
                    if r["phase"] == "training"
                    and r["arm"] == "M"
                    and r["family"] == family
                }
            )
            y = [
                np.mean(
                    [
                        np.mean(
                            [np.log2(cost(r, penalty)) for r in grouped[mid, "M", c]]
                        )
                        for c in TRAINING[family]
                    ]
                )
                for mid in mids
            ]
            readout["T_M"][family] = welch(x, y)
        if penalty == 2:
            report["outcome"] = outcome(
                ct["pooled"], subset_ct["pooled"], ck["pooled"], feasible
            )
            # Approximate balanced-corpus sizing; no equality inferred at small effects.
            spreads = [ct["families"][f]["sd_log2"] for f in TRAINING]
            delta = abs(ct["pooled"]["delta_log2"])
            variance = (
                sum(s * s for s in spreads) / 4
                if all(s is not None for s in spreads)
                else None
            )
            readout["sizing"] = dict(
                n_per_family_for_half_width_log2_1_10=math.ceil(
                    1.96**2 * variance / np.log2(1.10) ** 2
                )
                if variance is not None
                else None,
                n_per_family_approx_80percent_detect_observed_effect=math.ceil(
                    (1.96 + 0.84) ** 2 * variance / delta**2
                )
                if variance is not None and delta > 0
                else None,
                note="Normal approximation based on observed spreads; fresh independent corpora, not additional seeds alone.",
            )
        if stage2:
            hs, hg = corpus_scores(rows, corpora, "holdout", penalty)
            hct = contrast(hs, corpora, "C", "T", holdout=True)
            hsubset = contrast(hs, corpora, "C", "T", subset=True, holdout=True)
            hck = contrast(hs, corpora, "C", "K", holdout=True)
            transfer = dict(
                C_T=hct,
                K_valid_C_T=hsubset,
                C_K=hck,
                interpreted=feasible and report["outcome"]["row"] in (1, 2),
                C_T_label=label(hct),
                C_K_label=label(hck),
                contextual_increment=gain(hsubset) and gain(hck),
                reference=versus_g4(hs, hg, corpora, "holdout", penalty),
                amortization=amortization(rows, corpora, "holdout", penalty),
                families={},
            )
            for cid in sum(HOLDOUTS.values(), []):
                own = cid[:2]
                other = "PA" if own == "BE" else "BE"
                x = [
                    s["C"][cid]
                    for tid, s in hs.items()
                    if corpora[tid]["family"] == own
                ]
                y = [
                    s["C"][cid]
                    for tid, s in hs.items()
                    if corpora[tid]["family"] == other
                ]
                z = [np.log2(cost(r, penalty)) for r in hg["G4", "G4", cid]]
                matched = welch(x, y)
                g4 = welch(x, z)
                transfer["families"][cid] = dict(
                    matched_mismatched=matched,
                    matched_G4=g4,
                    useful_family_adaptation=gain(matched) and gain(g4),
                    task_scope="single holdout cell",
                )
            readout["holdout"] = transfer
        report["sensitivities"][f"unsolved_{penalty}x_cap"] = readout
    report["search_summary"] = {}
    for phase in ("collection", "training", "holdout"):
        report["search_summary"][phase] = {}
        for arm in sorted({r["arm"] for r in rows if r["phase"] == phase}):
            rs = [r for r in rows if r["phase"] == phase and r["arm"] == arm]
            report["search_summary"][phase][arm] = dict(
                n=len(rs),
                solved=sum(r["solved"] for r in rs),
                actual_evaluations=sum(r["evaluations"] for r in rs),
                seconds=sum(r["seconds"] for r in rs),
            )
    if config["smoke_only"] or config["probe_only"]:
        report["outcome"] = dict(
            row="diagnostic", meaning="smoke/probe only; no research inference"
        )
    return report


def save_report(out, report, rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    selected = [r for r in rows if r["phase"] == "training"]
    arms = [
        a for a in ("G4", "T", "C", "K", "M") if any(r["arm"] == a for r in selected)
    ]
    if arms:
        axes[0].boxplot(
            [[np.log2(cost(r)) for r in selected if r["arm"] == a] for a in arms],
            tick_labels=arms,
        )
    axes[0].set_ylabel("log2 evaluations (unsolved=2×cap)")
    main = report.get("sensitivities", {}).get("unsolved_2x_cap", {})
    if "C_T" in main:
        for i, family in enumerate(TRAINING):
            xs = main["C_T"]["families"][family]["contrasts_log2"]
            axes[1].scatter([i] * len(xs), xs, label=family)
        axes[1].set_xticks([0, 1], ["BE", "PA"])
        axes[1].axhline(0, color="gray")
        axes[1].set_ylabel("Corpus C−T log2 cost")
    # Median best fitness and behavioral diversity among runs observed at each checkpoint.
    for arm in arms[:4]:
        points = {}
        for r in selected:
            if r["arm"] == arm:
                for ev, score, div in r["curve"]:
                    points.setdefault(ev, []).append((score, div))
        x = sorted(points)
        if x:
            axes[2].plot(
                x, [np.median([v[0] for v in points[e]]) for e in x], label=arm
            )
    axes[2].set_xscale("log", base=2)
    axes[2].set_ylabel("Median best correct cases (surviving runs)")
    axes[2].set_xlabel("Evaluations")
    axes[2].legend()
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4))
    for arm in arms[:4]:
        points = {}
        for r in selected:
            if r["arm"] == arm:
                for ev, score, div in r["curve"]:
                    points.setdefault(ev, []).append(div)
        x = sorted(points)
        if x:
            ax.plot(x, [np.median(points[e]) for e in x], label=arm)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Evaluations")
    ax.set_ylabel("Median behavioral diversity (surviving runs)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "diversity.png", dpi=150)
    plt.close(fig)
    lines = [
        "# Solver-corpus fitting 1707",
        "",
        f"Outcome: {report['outcome']['row']} — {report['outcome']['meaning']}",
        "",
        report["scope"],
        "",
        f"Stage 1 complete: {report['stage1_complete']}; stage 2 complete: {report['stage2_complete']}.",
        f"K exclusions: {report['K_exclusions']}",
        "",
    ]
    if main:
        lines += ["| Training contrast | Speed | 95% interval |", "|---|---:|---:|"]
        for name in ("C_T", "K_valid_C_T", "C_K"):
            r = main[name]["pooled"]
            ratio = (
                f"{r['speed_ratio']:.3f}"
                if r["speed_ratio"] is not None
                else "unavailable"
            )
            lines.append(f"| {name} | {ratio} | {r['interval_95']} |")
        for name, r in main["reference"].items():
            p = r["pooled"]
            lines.append(f"| {name} | {p['speed_ratio']:.3f} | {p['interval_95']} |")
        lines += [
            "",
            "All details, per-family estimates, 1×cap sensitivity and arithmetic break-even are in result.json.",
            "A relative improvement alone does not establish practical benefit over G4.",
        ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    write_json(out, "result.json", report)
