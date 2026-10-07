"""2331 paired costs with crossed map/whole-seed uncertainty."""

from __future__ import annotations

import numpy as np
from scipy.stats import t

METRIC_DEFINITIONS = {
    "cost": "Evaluations to first full D1331 exact solve, or the cap if unsolved.",
    "P1": "Mean paired log2(T_MG/T_MM), equal cells and equal BE/PA families.",
    "P2": "Mean paired log2(T_GM/T_MM), equal cells and equal BE/PA families.",
    "D": "Mean paired log2(T_GG/T_MM), equal cells and equal BE/PA families.",
    "I_G": "Mean paired log2(T_GG/T_MG), equal cells and equal BE/PA families.",
    "O_G": "Mean paired log2(T_GG/T_GM), equal cells and equal BE/PA families.",
    "interaction": "P1 minus O_G in paired log2 cost units.",
    "MMr/MM": "Mean paired log2(T_MMr/T_MM), equal cells and equal BE/PA families.",
}
BOOTSTRAP_SEED = 2331400
BOOTSTRAP_REPLICATES = 20000
DELTA = 0.25


def resampling(n_seeds, n_maps, replicates=BOOTSTRAP_REPLICATES):
    """Shared multinomial weights represent crossed whole-block resampling."""
    if n_seeds < 1 or n_maps not in (10, 20):
        raise ValueError("need seeds and ten maps per family")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    seeds = rng.multinomial(n_seeds, np.full(n_seeds, 1 / n_seeds), replicates)
    maps = np.concatenate(
        [
            rng.multinomial(10, np.full(10, 0.1), replicates)
            for _ in range(n_maps // 10)
        ],
        axis=1,
    )
    return maps / n_maps, seeds / n_seeds


def estimate(values, weights, confidence=0.95, gg_seed=None):
    """values is map × seed; every contrast reuses the same crossed weights."""
    values = np.asarray(values, dtype=float)
    mw, sw = weights
    if values.shape != (mw.shape[1], sw.shape[1]):
        raise ValueError("bootstrap shape mismatch")
    samples = np.einsum("bi,bi->b", sw @ values.T, mw)
    tail = (1 - confidence) / 2
    bounds = np.quantile(samples, [tail, 1 - tail])
    mean = float(values.mean())
    per_map = values.mean(axis=1)
    variance = float(np.var(per_map, ddof=1) / len(per_map))
    if gg_seed is not None and len(gg_seed) > 1:
        variance += float(np.var(gg_seed, ddof=1) / len(gg_seed))
    half = float(t.ppf(1 - tail, len(per_map) - 1) * np.sqrt(variance))
    label = "N" if bounds[1] < DELTA else "P" if bounds[0] > 0 else "X"
    return dict(
        log2_mean=mean,
        ratio=float(2**mean),
        confidence=confidence,
        interval_log2=bounds.tolist(),
        interval_ratio=(2**bounds).tolist(),
        width_log2=float(bounds[1] - bounds[0]),
        label=label,
        resolved_negative=bool(bounds[1] < 0),
        map_spread_log2=float(np.std(per_map, ddof=1)),
        t_sensitivity_log2=[mean - half, mean + half],
        t_sensitivity_note="Map-level t; additive shared GG variance where applicable; covariance approximation, not primary.",
    )


def cost_matrices(rows, maps, cells, seeds, arms=("GG", "MM", "MG", "GM")):
    lookup = {(r["map"], r["arm"], r["cell"], r["seed"]): r for r in rows}
    if len(lookup) != len(rows):
        raise ValueError("duplicate analysis row")
    logs = {}
    for arm in arms:
        logs[arm] = np.array(
            [
                [
                    [
                        np.log2(
                            lookup[("G4" if arm == "GG" else tid, arm, cid, seed)][
                                "evaluations"
                            ]
                        )
                        for seed in seeds
                    ]
                    for cid in cells
                ]
                for tid in maps
            ]
        )
    return logs


def law_report(rows, maps, cells, seeds, replicates=BOOTSTRAP_REPLICATES):
    logs = cost_matrices(rows, maps, cells, seeds, ("MM", "MMr"))
    values = (logs["MMr"] - logs["MM"]).mean(axis=1)
    result = estimate(values, resampling(len(seeds), len(maps), replicates), 0.99)
    lo, hi = result["interval_log2"]
    result.update(
        passed=bool(lo <= 0 <= hi), seeds=len(seeds), equivalence_demonstrated=False
    )
    return result


def classify(primary, valid):
    if not valid:
        return dict(
            row="U",
            meaning="Diagnostic mode, failed validation, insufficient coverage or failed diagonal reproduction; no mechanism attribution.",
        )
    labels = tuple(primary[k]["label"] for k in ("P1", "P2"))
    row, meaning = {
        ("P", "N"): (
            "1",
            "Ongoing M suffices at the margin; the learned start adds <1.19x conditional on ongoing M.",
        ),
        ("N", "P"): (
            "2",
            "Learned start suffices at the margin; ongoing M adds <1.19x conditional on learned start.",
        ),
        ("P", "P"): (
            "3",
            "Both conditional increments are resolved positive; size and combination depend on the intervals and interaction.",
        ),
        ("N", "N"): (
            "4",
            "Conditional redundancy at this margin; check resolved negative increments for antagonism.",
        ),
    }.get(
        labels,
        ("5", "Attribution unresolved for at least one component; return to strategy."),
    )
    negative = [k for k in ("P1", "P2") if primary[k]["resolved_negative"]]
    if negative:
        meaning += (
            " Antagonism: "
            + ", ".join(negative)
            + " resolves negative (a mixed arm is faster than MM)."
        )
    return dict(row=row, meaning=meaning, antagonism=negative)


def make_report(
    rows,
    maps,
    cells,
    seeds,
    validation,
    diagnostic=False,
    replicates=BOOTSTRAP_REPLICATES,
    cell_weights=None,
    minimum_seeds=200,
    gg_minimum=0.85,
):
    main = [r for r in rows if r["seed"] in seeds and r["arm"] != "MMr"]
    report = dict(
        complete_seeds=seeds,
        n_seeds=len(seeds),
        n_maps=len(maps),
        validation=validation,
        diagnostic_only=diagnostic,
        metric_definitions=METRIC_DEFINITIONS,
        bootstrap=dict(
            seed=BOOTSTRAP_SEED,
            replicates=replicates,
            method="Crossed map-within-family / shared whole-seed percentile intervals",
            weighting="Equal cells, equal BE/PA families, equal maps within family",
        ),
        outcome=classify({}, False),
    )
    if not seeds:
        return report
    logs = cost_matrices(main, maps, cells, seeds)
    contrasts = {
        "P1": logs["MG"] - logs["MM"],
        "P2": logs["GM"] - logs["MM"],
        "D": logs["GG"] - logs["MM"],
        "I_G": logs["GG"] - logs["MG"],
        "O_G": logs["GG"] - logs["GM"],
    }
    contrasts["interaction"] = contrasts["P1"] - contrasts["O_G"]
    weights = resampling(len(seeds), len(maps), replicates)

    def summaries(cs, ws, gg):
        return {
            k: estimate(
                v, ws, gg_seed=gg if k in ("D", "I_G", "O_G", "interaction") else None
            )
            for k, v in cs.items()
        }

    cw = (
        np.full(len(cells), 1 / len(cells))
        if cell_weights is None
        else np.asarray(cell_weights)
    )
    average = {k: np.einsum("mcs,c->ms", v, cw) for k, v in contrasts.items()}
    gg_average = np.einsum("cs,c->s", logs["GG"][0], cw)
    report["contrasts"] = summaries(average, weights, gg_average)
    report["per_cell"] = {
        cid: summaries(
            {k: v[:, j, :] for k, v in contrasts.items()}, weights, logs["GG"][0, j]
        )
        for j, cid in enumerate(cells)
    }
    report["per_family"] = {
        family: summaries(
            {k: v[start : start + 10] for k, v in average.items()},
            resampling(len(seeds), 10, replicates),
            gg_average,
        )
        for family, start in (("BE", 0), ("PA", 10))
    }
    report["per_map"] = {
        tid: dict(
            family=tid[:2],
            contrasts={k: float(v[i].mean()) for k, v in average.items()},
            per_cell={
                cid: {k: float(v[i, j].mean()) for k, v in contrasts.items()}
                for j, cid in enumerate(cells)
            },
        )
        for i, tid in enumerate(maps)
    }
    d = report["contrasts"]["D"]["log2_mean"]
    report["descriptive_shares"] = {
        k + "/D": report["contrasts"][k]["log2_mean"] / d if d else None
        for k in ("I_G", "O_G")
    }
    report["solve_fractions"] = {
        tid: {
            arm: {
                cid: dict(
                    n=len(rs),
                    solved=sum(r["solved"] for r in rs),
                    fraction=float(np.mean([r["solved"] for r in rs])),
                )
                for cid in cells
                if (
                    rs := [
                        r
                        for r in main
                        if r["map"] == tid and r["arm"] == arm and r["cell"] == cid
                    ]
                )
            }
            for arm in (("GG",) if tid == "G4" else ("MM", "MG", "GM"))
        }
        for tid in ("G4", *maps)
    }
    gg_gate = all(
        v["fraction"] >= gg_minimum
        for v in report["solve_fractions"]["G4"]["GG"].values()
    )
    d_gate = bool(report["contrasts"]["D"]["interval_log2"][0] > np.log2(1.25))
    report["gates"] = dict(
        gg_solve=gg_gate, diagonal=d_gate, minimum_seeds=len(seeds) >= minimum_seeds
    )
    report["outcome"] = classify(
        report["contrasts"],
        validation["passed"]
        and not diagnostic
        and gg_gate
        and d_gate
        and len(seeds) >= minimum_seeds,
    )
    return report


def save_report(out, report, rows, cells):
    lines = [
        "# Frozen starting-program / ongoing-decoder intervention",
        "",
        f"Outcome {report['outcome']['row']}: {report['outcome']['meaning']}",
        f"Complete shared seeds: {report['n_seeds']}; maps: {report['n_maps']}.",
        f"Scope: 20 frozen maps, {len(cells)} reused screened cells, G4 context, D1331, approved operators/budget.",
        "Ongoing use bundles inherited alleles, mutation, crossover and continued program supply.",
        "",
    ]
    for name, r in report.get("contrasts", {}).items():
        lines.append(
            f"{name}: {r['ratio']:.4f}x, 95% CI {r['interval_ratio']}; log2 {r['log2_mean']:.4f}, width {r['width_log2']:.4f}; {r['label']}."
        )
    lines += [
        "",
        "N bounds an extra conditional increment; P need not establish a practically large increment.",
        "Law-check non-rejection does not establish equivalence. See result.json for cell/family results and sensitivity.",
        f"Stop reason: {report.get('stop_reason')}",
        f"Validation: {report['validation']}",
    ]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4))
    for i, (name, r) in enumerate(report.get("contrasts", {}).items()):
        lo, hi = r["interval_log2"]
        ax.plot([lo, hi], [i, i], color="C0")
        ax.plot(r["log2_mean"], i, "o", color="C0")
    ax.set(
        yticks=range(len(report.get("contrasts", {}))),
        yticklabels=list(report.get("contrasts", {})),
        xlabel="Paired log2 cost ratio, 95% crossed interval",
    )
    ax.axvline(0, color="grey")
    ax.axvline(DELTA, color="grey", linestyle="--")
    fig.tight_layout()
    fig.savefig(out / "contrasts.png", dpi=150)
    plt.close(fig)
    fig, axes = plt.subplots(3, len(cells), figsize=(5 * len(cells), 10), squeeze=False)
    for j, cid in enumerate(cells):
        for arm in ("GG", "MM", "MG", "GM"):
            rs = [r for r in rows if r["cell"] == cid and r["arm"] == arm]
            if not rs:
                continue
            budgets = np.geomspace(256, rs[0]["cap"], 100)
            axes[0, j].plot(
                budgets,
                [
                    np.mean([r["solved"] and r["evaluations"] <= b for r in rs])
                    for b in budgets
                ],
                label=arm,
            )
            points = {}
            for row in rs:
                for evaluation, score, diversity in row["curve"]:
                    points.setdefault(evaluation, []).append((score / 64, diversity))
            xs = sorted(points)
            for k in (0, 1):
                axes[k + 1, j].plot(
                    xs, [np.mean([p[k] for p in points[x]]) for x in xs], label=arm
                )
        for k, label in enumerate(
            (
                "Fraction exactly solved",
                "Best accuracy (active searches)",
                "Diversity (active searches)",
            )
        ):
            axes[k, j].set(title=cid, xlabel="Evaluations", ylabel=label, xscale="log")
            if axes[k, j].lines:
                axes[k, j].legend()
    fig.tight_layout()
    fig.savefig(out / "search_curves.png", dpi=150)
    plt.close(fig)
