"""Pair-block uncertainty and arithmetic economics for the 2001 crossing."""

import json
import numpy as np
from scipy.stats import t
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.comparison_gate_bank import digest

ARMS = ("D/D", "T/T", "T/D", "D/T", "D/none", "T/none")
CONTRASTS = {
    "R_replacement": ("T/T", "T/D"),
    "G_residual": ("T/D", "D/D"),
    "B_bare_table": ("T/none", "D/none"),
    "D_library_gain": ("D/none", "D/D"),
    "T_portable_gain": ("T/none", "T/D"),
    "D_library_identity": ("D/T", "D/D"),
    "native_gap": ("T/T", "D/D"),
    "reverse_gain": ("D/none", "D/T"),
    "T_native_library_gain": ("T/none", "T/T"),
    "TS_retention": ("T/D", "T/T"),
}


def classify(ratios):
    r, g = [ratios[k]["interval95"] for k in ("R_replacement", "G_residual")]
    if r[0] > 1.5:
        primary = "worthwhile portable replacement increment"
        sufficiency = (
            "within 1.5x replacement tolerance"
            if g[1] < 1.5
            else "portable but partial"
            if g[0] > 1.5
            else "sufficiency unresolved"
        )
    elif r[1] < 1.5:
        primary = "no worthwhile replacement increment"
        sufficiency = None
    else:
        primary = "replacement increment unresolved"
        sufficiency = None
    return dict(
        primary=primary,
        sufficiency=sufficiency,
        table_contribution=ratios["B_bare_table"]["interval95"][0] > 1.5,
        portable_activity=ratios["T_portable_gain"]["interval95"][0] > 1.5,
        native_D_identity_advantage=ratios["D_library_identity"]["interval95"][0] > 1.5,
        fresh_native_gap_resolved=ratios["native_gap"]["interval95"][0] > 1.5,
        caveat="contributions nonexclusive; unresolved is not absence; native identity advantage is conditional compatibility, not evolutionary coadaptation",
    )


def arrays(rows, penalty):
    families = sorted({r["family"] for r in rows})
    pairs = sorted({r["pair"] for r in rows})
    by = {(r["family"], r["cell"], r["pair"], r["repeat"], r["arm"]): r for r in rows}
    cells = {f: sorted({r["cell"] for r in rows if r["family"] == f}) for f in families}
    expected = {
        (f, c, b, s, a)
        for f in families
        for c in cells[f]
        for b in pairs
        for s in range(2)
        for a in ARMS
    }
    if len(by) != len(rows) or set(by) != expected:
        raise ValueError("incomplete or duplicate component grid")
    for f, c, b, s, a in expected:
        if by[f, c, b, s, a]["seed"] != by[f, c, b, s, "D/D"]["seed"]:
            raise ValueError("common seeds differ")
    values = {
        f: np.array(
            [
                [
                    [
                        [
                            np.log(
                                r["evaluations"] if r["solved"] else penalty * r["cap"]
                            )
                            for s in range(2)
                            for r in [by[f, c, b, s, a]]
                        ]
                        for b in pairs
                    ]
                    for c in cells[f]
                ]
                for a in ARMS
            ]
        )
        for f in families
    }
    return pairs, cells, values


def summarize(rows, penalty=2, draws=8192):
    pairs, cells, values = arrays(rows, penalty)
    B = len(pairs)
    rng = np.random.default_rng(2001000)
    boot = {f: np.empty((draws, len(ARMS))) for f in values}
    for i in range(draws):
        selected = rng.integers(B, size=B)
        for f, v in values.items():
            # Seeds jointly across arms; duplicate sampled pairs are independent
            # bootstrap draws, while all appearances retain their donor identities.
            seeds = rng.integers(2, size=(len(cells[f]), B, 2))
            chosen = v[:, :, selected, :]
            boot[f][i] = np.take_along_axis(chosen, seeds[None, :, :, :], axis=3).mean(
                axis=(1, 2, 3)
            )
    result = {}
    for f, v in values.items():
        means = v.mean(axis=(1, 2, 3))
        ratios = {}
        for key, (num, den) in CONTRASTS.items():
            n, d = ARMS.index(num), ARMS.index(den)
            ratios[key] = dict(
                point=float(np.exp(means[n] - means[d])),
                interval95=np.exp(
                    np.quantile(boot[f][:, n] - boot[f][:, d], [0.025, 0.975])
                ).tolist(),
                numerator=num,
                denominator=den,
            )
        result[f] = dict(
            ratios=ratios,
            costs={
                a: dict(
                    geometric_cost=float(np.exp(means[i])),
                    interval95=np.exp(
                        np.quantile(boot[f][:, i], [0.025, 0.975])
                    ).tolist(),
                    solved=sum(
                        r["solved"] for r in rows if r["family"] == f and r["arm"] == a
                    ),
                    attempts=len(cells[f]) * B * 2,
                )
                for i, a in enumerate(ARMS)
            },
            per_cell={
                c: {a: float(np.exp(v[i, j].mean())) for i, a in enumerate(ARMS)}
                for j, c in enumerate(cells[f])
            },
            per_pair={
                str(b): {
                    a: float(np.exp(v[i, :, j].mean())) for i, a in enumerate(ARMS)
                }
                for j, b in enumerate(pairs)
            },
        )
    return dict(
        families=result,
        decision=classify(result["DG"]["ratios"]),
        failure_penalty=penalty,
        bootstrap=dict(
            draws=draws,
            seed=2001000,
            unit="24 frozen donor pairs, kept jointly across both rosters and all arms",
            seeds="two repeats resampled jointly across arms within pair x cell",
            cells="fixed",
            donor_assignment="conditional on permutation seed 2001",
        ),
    )


def acquisition(saved, owner, build):
    final = saved["builds.json"][owner][str(build)]["acquisition"]
    inter = saved["seed_builds.json"][owner][str(build)]["acquisition"]
    return dict(
        evaluations=final["evaluations"],
        worker_seconds=final["source_worker_seconds"]
        + sum(
            final[k] + inter[k]
            for k in ("verification_seconds", "fit_seconds", "extraction_seconds")
        ),
    )


def economics(rows, saved):
    result = {}
    for f in sorted({r["family"] for r in rows}):
        result[f] = {}
        for a in ARMS:
            per_pair = {}
            for b in sorted({r["pair"] for r in rows}):
                rs = [
                    r
                    for r in rows
                    if r["family"] == f and r["arm"] == a and r["pair"] == b
                ]
                m = rs[0]
                owners = {(m["table_owner"], m["table_build"])}
                if m["library_owner"] != "none":
                    owners.add((m["library_owner"], m["library_build"]))
                acqs = [acquisition(saved, o, i) for o, i in owners]
                acq = {
                    k: sum(x[k] for x in acqs)
                    for k in ("evaluations", "worker_seconds")
                }
                ev = float(np.mean([r["evaluations"] for r in rs]))
                sec = float(np.mean([r["seconds"] for r in rs]))
                per_pair[str(b)] = dict(
                    acquisition=acq,
                    searches=len(rs),
                    actual_total_evaluations=acq["evaluations"]
                    + sum(r["evaluations"] for r in rs),
                    actual_total_worker_seconds=acq["worker_seconds"]
                    + sum(r["seconds"] for r in rs),
                    horizons={
                        str(n): dict(
                            evaluations=acq["evaluations"] + n * ev,
                            worker_seconds=acq["worker_seconds"] + n * sec,
                        )
                        for n in (1, 16, 256, 4096)
                    },
                )
            result[f][a] = dict(
                per_pair=per_pair,
                mean_horizon_costs={
                    str(n): {
                        k: float(
                            np.mean(
                                [p["horizons"][str(n)][k] for p in per_pair.values()]
                            )
                        )
                        for k in ("evaluations", "worker_seconds")
                    }
                    for n in (1, 16, 256, 4096)
                },
            )
    return dict(
        costs=result,
        scope="arithmetic actual effort, failures actual cap; hybrids pay both acquisitions, native and bare pay one; hypothetical explicit horizons, not repayment from geometric ratios; measured worker time, not queue wall time",
    )


def resolution_price(rows, summary, saved):
    pair_costs = summary["families"]["DG"]["per_pair"]
    logs = np.array([np.log(v["T/T"] / v["T/D"]) for v in pair_costs.values()])
    B = len(logs)
    variance = float(np.var(logs, ddof=1))
    gap = abs(
        np.log(summary["families"]["DG"]["ratios"]["R_replacement"]["point"] / 1.5)
    )
    needed = next(
        (
            n
            for n in range(max(B, 3), 1025)
            if gap > 0 and t.ppf(0.975, n - 1) * np.sqrt(variance / n) < gap
        ),
        None,
    )
    acq = []
    for b in pair_costs:
        m = next(r for r in rows if r["pair"] == int(b) and r["arm"] == "T/T")
        acq.append(
            acquisition(saved, "D", int(b))["worker_seconds"]
            + acquisition(saved, "T", m["table_build"])["worker_seconds"]
        )
    means = {
        a: float(np.mean([r["seconds"] for r in rows if r["arm"] == a])) for a in ARMS
    }
    # Full sixteen-cell design: two repeats per arm and pair.
    worker_per_pair = float(np.mean(acq)) + 32 * sum(means.values())
    additional = None if needed is None else max(0, needed - B)
    return dict(
        observed_pair_log_ratio_variance=variance,
        conditional_total_pairs=needed,
        additional_independent_pairs=additional,
        additional_worker_seconds=None
        if additional is None
        else additional * worker_per_pair,
        projected_minutes_at_10_workers_with30percent_reserve=None
        if additional is None
        else 1.3 * additional * worker_per_pair / 10 / 60,
        caveat="observed pair variance and point fixed; normal/t approximation, inner seed noise included in observed variance; new independent acquisitions assumed similar cost; no guaranteed resolution or automatic top-up; all results exit to strategy",
    )


def plot(out, rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    families = sorted({r["family"] for r in rows})
    fig, axes = plt.subplots(
        len(families), 3, figsize=(15, 4 * len(families)), squeeze=False
    )
    for fi, f in enumerate(families):
        for a in ARMS:
            rs = [r for r in rows if r["family"] == f and r["arm"] == a]
            grid = sorted({p[0] for r in rs for p in r["curve"]} | {rs[0]["cap"]})
            for k in (1, 2):
                ys = [
                    np.mean(
                        [
                            ([p for p in r["curve"] if p[0] <= x] or r["curve"][:1])[
                                -1
                            ][k]
                            for r in rs
                        ]
                    )
                    for x in grid
                ]
                axes[fi, k - 1].plot(grid, ys, label=a)
                axes[fi, k - 1].set_xscale("log")
            axes[fi, 2].scatter(
                [r["evaluations"] for r in rs],
                [r["exact_check_seconds"] for r in rs],
                s=5,
                alpha=0.3,
                label=a,
            )
        for j, title in enumerate(
            (
                "best correct training cases",
                "distinct correctness patterns",
                "exact verification seconds",
            )
        ):
            axes[fi, j].set_title(f + ": " + title)
            axes[fi, j].set_xlabel("evaluations")
            axes[fi, j].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "dynamics.png", dpi=130)
    plt.close(fig)


def report(out, rows, saved, prep, timing, smoke=False):
    two = summarize(rows)
    one = summarize(rows, penalty=1)
    complete = {r["family"] for r in rows} == {"DG", "TS"}
    result = dict(
        status="smoke"
        if smoke
        else "component_comparison_complete"
        if complete
        else "DG_complete_TS_pending",
        summary=two,
        one_cap=one,
        penalty_sensitive=two["decision"] != one["decision"],
        economics=economics(rows, saved),
        resolution_price=resolution_price(rows, two, saved),
        timing=timing,
        preparation=prep,
        target_performance_scored=not smoke,
        complete=complete,
        search_rows_hash=digest(rows),
        scope="fixed development banks and frozen decoder assignment; external fitting, no adapter fitting, inheritance, pure motif, or fresh-bank transfer claim",
    )
    if "TS" in two["families"]:
        lo, hi = two["families"]["TS"]["ratios"]["TS_retention"]["interval95"]
        result["TS_retention_guidance"] = (
            "cost loss above 1.5x favors family-aware or joint acquisition"
            if lo > 1.5
            else "cost loss below 1.5x tolerance"
            if hi < 1.5
            else "retention choice unresolved"
        )
    write_json(out, "result.json", result)
    lines = [
        "# Frozen table/library component transfer",
        "",
        "SMOKE ONLY; development cells."
        if smoke
        else "Return to strategy after both rosters; development data.",
        "",
        json.dumps(two["decision"], indent=2),
        "",
        f"One-cap label sensitive: {result['penalty_sensitive']}",
        "",
        "|Family|Contrast|Point|95% pair/seed interval|",
        "|---|---|---:|---:|",
    ]
    for f, s in two["families"].items():
        for k, r in s["ratios"].items():
            lines.append(
                f"|{f}|{k}|{r['point']:.3f}|[{r['interval95'][0]:.3f}, {r['interval95'][1]:.3f}]|"
            )
    lines += [
        "",
        "|Family|Table|Library|Geometric cost|Solves|",
        "|---|---|---|---:|---:|",
    ]
    for f, s in two["families"].items():
        for a, c in s["costs"].items():
            table, library = a.split("/")
            lines.append(
                f"|{f}|{table}|{library}|{c['geometric_cost']:.1f}|{c['solved']}/{c['attempts']}|"
            )
    lines += [
        "",
        result["scope"],
        "",
        "R tests replacement increment, not every meaning of portability. Bare-table and library contributions can coexist. Library sufficiency means within the 1.5x replacement tolerance. Native identity effects are conditional compatibility; bare tables were acquired with intermediate libraries. Unresolved cost is not equality or absence. A failure to resolve the fresh native gap leaves attribution conditional on these new references.",
        "",
        result.get("TS_retention_guidance", "TS pending."),
        "",
        "Per-cell/pair costs, 1-cap sensitivity, arithmetic acquisition costs and conditional resolution price are in result.json. No automatic enlargement.",
        "",
        "Precedents: common-subtree transfer (O’Neill et al. 2017), [Run Transferable Libraries (Keijzer et al. 2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf), [PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/), and model stitching (Lenc & Vedaldi); this crossing fits no adapter.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    plot(out, rows)
