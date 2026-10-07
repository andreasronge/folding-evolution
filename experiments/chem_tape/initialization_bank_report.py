"""0315 training-bank attribution and across-cell family balance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import t

from experiments.chem_tape.initialization_report import (
    BOOTSTRAP_REPLICATES,
    DELTA,
    cost_matrices,
    make_report as base_report,
    resampling,
    save_report as base_save,
)

DESCRIPTIVE_REFERENCE = (
    Path(__file__).with_name("data") / "initialization_0315" / "descriptive_2331.json"
)
DESCRIPTIVE_SHA = "604ad43252c61c770752e436a825b6905483a8d903123d54e3d6114ff45fb9e5"


def prior_descriptive():
    raw = DESCRIPTIVE_REFERENCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != DESCRIPTIVE_SHA:
        raise ValueError("Prior descriptive result SHA256 mismatch")
    return json.loads(raw)


def cell_weights(cells):
    return np.array(
        [0.5 / sum(c.startswith(cid[:2] + ":") for c in cells) for cid in cells]
    )


def family_interval(per_cell):
    groups = {
        f: np.array([v for c, v in per_cell.items() if c.startswith(f + ":")], float)
        for f in ("BE", "PA")
    }
    if any(
        len(v) != n or not np.all(np.isfinite(v))
        for v, n in zip(groups.values(), (4, 6))
    ):
        return dict(label="X", reason="Missing cell coverage", per_cell=per_cell)
    be, pa = groups.values()
    a, b = np.var(be, ddof=1) / 4, np.var(pa, ddof=1) / 6
    se = np.sqrt(a + b)
    df = (a + b) ** 2 / (a * a / 3 + b * b / 5) if a + b else None
    mean = float(be.mean() - pa.mean())
    half = float(t.ppf(0.975, df) * se) if df else 0.0
    lo, hi = mean - half, mean + half
    inside = bool(lo > -DELTA and hi < DELTA)
    # Direction takes precedence on the negative side, matching plan.md.
    label = "B" if hi < 0 else "E" if inside else "R" if lo > 0 else "X"
    return dict(
        log2_mean=mean,
        interval_log2=[lo, hi],
        width_log2=2 * half,
        confidence=0.95,
        label=label,
        label_precedence=["B", "E", "R", "X"],
        direction="negative" if hi < 0 else "positive" if lo > 0 else "unresolved",
        inside_margin=inside,
        degrees_freedom=df,
        standard_error=float(se),
        family_means={f: float(v.mean()) for f, v in groups.items()},
        family_sd={f: float(v.std(ddof=1)) for f, v in groups.items()},
        s_w=float(np.sqrt((3 * np.var(be, ddof=1) + 5 * np.var(pa, ddof=1)) / 8)),
        per_cell=per_cell,
        scope="Working Welch summary across four BE and six PA screened training cells; frozen maps.",
    )


def classify(primary, family, valid):
    if not valid:
        return dict(
            row="U",
            meaning="Validation, coverage or diagonal gain gate failed; no mechanism attribution.",
        )
    p1, p2 = (primary[k]["label"] for k in ("P1", "P2"))
    if (p1, p2) == ("P", "P"):
        row, meaning = {
            "B": (
                "1",
                "Both components help; BE is relatively more start-dependent than PA on this training bank. C alone does not establish a sign flip.",
            ),
            "E": (
                "2",
                "Both components help; training-bank family difference is bounded within the planned margin.",
            ),
            "R": (
                "3",
                "Both components help; relative family balance is reversed on this training bank.",
            ),
            "X": ("4", "Both components help; family dependence remains unresolved."),
        }[family["label"]]
    elif (p1, p2) in (("P", "N"), ("N", "P")):
        row, meaning = (
            "5",
            "One conditional increment is bounded below the practical threshold, while the other is resolved positive; N does not mean no contribution.",
        )
    else:
        row, meaning = (
            "6",
            "Attribution unresolved, or conditionally redundant at the margin if both increments are N.",
        )
    negative = [k for k in ("P1", "P2") if primary[k]["resolved_negative"]]
    if negative:
        meaning += " Antagonism: " + ", ".join(negative) + " resolves negative."
    return dict(row=row, meaning=meaning, antagonism=negative)


def contrasts(logs):
    cs = {
        name: logs[a] - logs[b]
        for name, a, b in (
            ("P1", "MG", "MM"),
            ("P2", "GM", "MM"),
            ("D", "GG", "MM"),
            ("I_G", "GG", "MG"),
            ("O_G", "GG", "GM"),
        )
    }
    cs["interaction"] = cs["P1"] - cs["O_G"]
    return cs


def masked_summary(values, mask, weights, cw):
    """Recompute available paired means within each cell/map-family per draw.

    Entire seed indices remain shared. Empty resampled strata make the interval
    unavailable, rather than manufacturing a cost or silently changing weights.
    """
    mw, sw = weights
    values, mask = np.asarray(values), np.asarray(mask)
    point, samples = 0.0, np.zeros(len(mw))
    counts = []
    for j, weight in enumerate(cw):
        for start in (0, 10):
            v, m = values[start : start + 10, j], mask[start : start + 10, j]
            count = int(m.sum())
            counts.append(count)
            map_counts = m.sum(axis=1)
            if np.any(map_counts == 0):
                return dict(label="X", reason="Empty cell/map stratum", counts=counts)
            point += weight * 0.5 * float(np.mean(np.sum(v * m, axis=1) / map_counts))
            num = sw @ (v * m).T
            den = sw @ m.astype(float).T
            map_draws = mw[:, start : start + 10]
            if np.any((den == 0) & (map_draws > 0)):
                return dict(
                    label="X",
                    reason="Empty bootstrap cell/map stratum",
                    counts=counts,
                )
            samples += weight * np.einsum(
                "bi,bi->b", num / np.where(den > 0, den, 1), map_draws
            )
    lo, hi = np.quantile(samples, [0.025, 0.975])
    return dict(
        log2_mean=point,
        ratio=float(2**point),
        interval_log2=[float(lo), float(hi)],
        interval_ratio=[float(2**lo), float(2**hi)],
        width_log2=float(hi - lo),
        label="N" if hi < DELTA else "P" if lo > 0 else "X",
        resolved_negative=bool(hi < 0),
        counts=counts,
    )


def masked_cell_means(values, mask, cells):
    result = {}
    for j, cid in enumerate(cells):
        means = []
        for start in (0, 10):
            v, m = values[start : start + 10, j], mask[start : start + 10, j]
            if np.any(m.sum(axis=1) == 0):
                result[cid] = None
                break
            means.append(float(np.mean(np.sum(v * m, axis=1) / m.sum(axis=1))))
        else:
            result[cid] = float(np.mean(means))
    return result


def make_report(
    rows,
    maps,
    cells,
    seeds,
    validation,
    diagnostic=False,
    replicates=BOOTSTRAP_REPLICATES,
):
    cw = cell_weights(cells)
    report = base_report(
        rows,
        maps,
        cells,
        seeds,
        validation,
        diagnostic,
        replicates,
        cell_weights=cw,
        minimum_seeds=120,
        gg_minimum=0.75,
    )
    report["bootstrap"]["weighting"] = (
        "Equal cell families, equal cells within cell family, equal map families and maps within family"
    )
    report["metric_definitions"] = dict(
        report["metric_definitions"],
        S="Per-cell mean log2(T_MG/T_GM) over maps and seeds.",
        C="Mean S over four BE cells minus mean S over six PA cells; Welch 95% t over cells.",
    )
    report["metric_definitions"].pop("MMr/MM")
    report["metric_definitions"] = {
        k: v.replace(
            "equal cells and equal BE/PA families",
            "equal cell families/cells within family and equal map families/maps within family",
        )
        for k, v in report["metric_definitions"].items()
    }
    report["metric_definitions"]["pooled_weighting"] = report["bootstrap"]["weighting"]
    report["outcome"] = classify({}, {}, False)
    if not seeds:
        return report
    logs = cost_matrices(rows, maps, cells, seeds)
    cs = contrasts(logs)
    report["family_balance"] = family_interval(
        {cid: float((cs["P1"] - cs["P2"])[:, j].mean()) for j, cid in enumerate(cells)}
    )
    for cid in cells:
        report["per_cell"][cid]["S"] = report["family_balance"]["per_cell"][cid]
    prior = prior_descriptive()
    report["descriptive_13_cells"] = dict(
        descriptive_only=True,
        note="Different seed cohorts and training status; this view does not change inference or routing.",
        previous_source=prior,
        per_cell={
            **{
                cid: dict(
                    values, cohort="2331 reused withheld", n_seeds=prior["n_seeds"]
                )
                for cid, values in prior["per_cell"].items()
            },
            **{
                cid: dict(
                    P1=v["P1"]["log2_mean"],
                    P2=v["P2"]["log2_mean"],
                    S=v["S"],
                    cohort="0315 training",
                    n_seeds=len(seeds),
                )
                for cid, v in report["per_cell"].items()
            },
        },
    )
    report["map_family_by_cell_family"] = {
        mf: {
            cf: {
                k: float(
                    np.mean(
                        v[
                            start : start + 10,
                            [j for j, c in enumerate(cells) if c.startswith(cf + ":")],
                        ]
                    )
                )
                for k, v in dict(cs, S=cs["P1"] - cs["P2"]).items()
            }
            for cf in ("BE", "PA")
        }
        for mf, start in (("BE", 0), ("PA", 10))
    }
    for tid in report["solve_fractions"]:
        for arm in report["solve_fractions"][tid]:
            for cid, group in report["solve_fractions"][tid][arm].items():
                rs = [
                    r
                    for r in rows
                    if (r["map"], r["arm"], r["cell"]) == (tid, arm, cid)
                ]
                group["unsolved"] = group["n"] - group["solved"]
                group["at_cap"] = sum(
                    r["evaluations"] == r.get("cap", 524288) for r in rs
                )
    valid = bool(
        validation["passed"] and not diagnostic and all(report["gates"].values())
    )
    report["outcome"] = classify(report["contrasts"], report["family_balance"], valid)
    weights = resampling(len(seeds), len(maps), replicates)
    report["sensitivities"] = {}
    for name in ("winsorized_65536", "uncapped_triplets"):
        modified = (
            {k: np.minimum(v, np.log2(65536)) for k, v in logs.items()}
            if name.startswith("winsor")
            else logs
        )
        scs = contrasts(modified)
        masks = {k: np.ones_like(v, dtype=bool) for k, v in scs.items()}
        triplet = np.logical_and.reduce(
            [logs[k] < np.log2(524288) for k in ("GG", "MM", "MG", "GM")]
        )
        if name == "uncapped_triplets":
            masks = {
                k: triplet
                if k in ("P1", "P2")
                else triplet & (logs["GG"] < np.log2(524288))
                for k in scs
            }
        primary = {k: masked_summary(v, masks[k], weights, cw) for k, v in scs.items()}
        sb = family_interval(
            masked_cell_means(scs["P1"] - scs["P2"], masks["P1"], cells)
        )
        complete = (
            all("interval_log2" in v for v in primary.values())
            and "interval_log2" in sb
        )
        outcome = classify(primary, sb, valid and complete)
        report["sensitivities"][name] = dict(
            contrasts=primary,
            family_balance=sb,
            outcome=outcome,
            outcome_changed=outcome["row"] != report["outcome"]["row"],
            label_changes={
                k: primary[k]["label"] != report["contrasts"][k]["label"]
                for k in primary
            },
            family_label_changed=sb["label"] != report["family_balance"]["label"],
            retained_triplets=int(masks["P1"].sum()),
            total_triplets=int(triplet.size),
            retained_by_cell={
                c: int(masks["P1"][:, j].sum()) for j, c in enumerate(cells)
            },
            note="Drop triplets with any of four arms at cap, as in 2331. Available seeds within each map/cell, equal maps and family/cell weights; shared crossed draws. C uses available per-cell S.",
        )
    return report


def save_report(out, report, rows, cells):
    base_save(out, report, rows, cells)
    lines = ["\nTraining-bank family balance (screened cells; frozen maps):"]
    b = report.get("family_balance", {})
    lines.append(str(b))
    lines.append(
        "Map-family × cell-family (same family is in-sample): "
        + str(report.get("map_family_by_cell_family", {}))
    )
    for name, sensitivity in report.get("sensitivities", {}).items():
        lines.append(
            f"{name}: row {sensitivity['outcome']['row']}; label changes {sensitivity['label_changes']}; family label changed {sensitivity['family_label_changed']}."
        )
    lines.append(
        "C does not establish a sign flip. Prior withheld-cell typicality is not identified. A negative interaction is sub-additivity, not an identified shared resource."
    )
    lines.append(
        "Prior three-cell results: research/runs/2026-10-06-2331/analysis.md; any 13-cell view is descriptive because seeds differ."
    )
    with (out / "summary.md").open("a") as stream:
        stream.write("\n".join(lines) + "\n")
    if "interval_log2" in b:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 6))
        for i, (cid, value) in enumerate(b["per_cell"].items()):
            ax.plot(value, i, "o", color="C0" if cid.startswith("BE:") else "C1")
        ax.set(
            yticks=range(len(cells)),
            yticklabels=cells,
            xlabel="S = log2(T_MG/T_GM), mean over frozen maps and seeds",
        )
        ax.axvline(0, color="grey")
        lo, hi = b["interval_log2"]
        prefix = "Diagnostic only; " if report["diagnostic_only"] else ""
        ax.set_title(
            f"{prefix}C={b['log2_mean']:.3f}; Welch 95% [{lo:.3f}, {hi:.3f}]; label {b['label']}"
        )
        fig.tight_layout()
        fig.savefig(out / "family_balance.png", dpi=150)
        plt.close(fig)
