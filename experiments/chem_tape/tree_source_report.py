"""0833 inference: fixed destination rosters, TS blocks, independent DG cohort."""

from collections import Counter
import math

import numpy as np

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.tree_library_report import estimate
from experiments.chem_tape.tree_source_run import ARMS, NATIVE_ARMS, seed

DRAWS = 8192
HORIZONS = (1, 5, 10, 25, 50, 100, 500, 1000)


def classify(ratio, guard):
    if guard[0] <= -0.03:
        return "reliability_inferior" if guard[1] < -0.03 else "reliability_unresolved"
    if ratio[1] < 0.80:
        return "worthwhile_saving_supported"
    if ratio[0] > 0.80:
        return "saving_at_least_20pct_excluded"
    return "usefulness_unresolved"


def grid(rows, cells, repeats, arms, metric):
    by = {(r["build"], r["cell"], r["repeat"], r["arm"]): r for r in rows}
    expected = {
        (b, c, r, a)
        for b in range(24)
        for c in cells
        for r in range(repeats)
        for a in arms
    }
    if len(by) != len(rows) or set(by) != expected:
        raise ValueError("requires complete fixed-size destination grid")
    for b, c, r, _ in expected:
        if len({tuple(by[b, c, r, a]["seeds"]) for a in arms}) != 1:
            raise ValueError("attempt seed pairing failed")
    return {
        a: np.array(
            [
                [[float(by[b, c, r, a][metric]) for r in range(repeats)] for c in cells]
                for b in range(24)
            ]
        )
        for a in arms
    }


def acquisition(libs, owner, metric, control=False):
    if metric == "evaluations":
        return np.array(
            [x["acquisition_evaluations"] for x in libs[owner]], dtype=float
        )
    fields = [
        "acquisition_worker_seconds",
        "extraction_seconds",
        "verification_seconds",
    ]
    if control:
        fields.append("control_seconds")
    return np.array([sum(x[k] for k in fields) for x in libs[owner]])


def price(variance, gap, rows, libs):
    needed = (
        None
        if gap <= 0
        else max(24, int(math.ceil(1.959963984540054**2 * variance / gap**2)))
    )
    extra = None if needed is None else max(0, needed - 24)
    worker = sum(r["worker_seconds"] for r in rows) / 24
    worker += sum(
        acquisition(libs, f, "worker_seconds", f == "TS").mean() for f in ("TS", "DG")
    )
    return dict(
        conditional_total_builds=needed,
        additional_builds=extra,
        additional_jobs=None if extra is None else extra * (64 + 384),
        additional_worker_seconds=None if extra is None else extra * float(worker),
        additional_wall_seconds_at_10x=None
        if extra is None
        else extra * float(worker) / 10,
        caveat="Observed effect/variance normal approximation; complete two-source acquisition and 384-job scoring grid per extra slot; no automatic top-up or guaranteed resolution",
    )


def summarize_family(
    rows, cells, repeats, arms, libs, selected, independent, price_rows
):
    values = {
        m: grid(rows, cells, repeats, arms, m)
        for m in ("evaluations", "worker_seconds", "solved")
    }
    blocks = {
        m: {a: x.mean(axis=(1, 2)) for a, x in arrays.items()}
        for m, arrays in values.items()
    }
    contrasts, prices = {}, {}
    for denom in arms:
        if denom == "R-TS":
            continue
        index = independent if denom == "R-DG" else selected
        name = "R-TS/" + denom
        v = {}
        for metric in ("evaluations", "worker_seconds"):
            a, b = blocks[metric]["R-TS"], blocks[metric][denom]
            v[metric] = estimate(
                a.mean() / b.mean(), a[selected].mean(axis=1) / b[index].mean(axis=1)
            )
        a, b = blocks["solved"]["R-TS"], blocks["solved"][denom]
        v["solve_fraction_difference"] = estimate(
            (a - b).mean(), a[selected].mean(axis=1) - b[index].mean(axis=1)
        )
        contrasts[name] = v
        a, b = blocks["evaluations"]["R-TS"], blocks["evaluations"][denom]
        ratio = a.mean() / b.mean()
        threshold = 0.8 if denom == "R-tree" else 1.0
        variance = (
            np.var(a / a.mean(), ddof=1) + np.var(b / b.mean(), ddof=1)
            if denom == "R-DG"
            else np.var(a / a.mean() - b / b.mean(), ddof=1)
        )
        prices[name] = dict(
            log_ratio=price(
                float(variance), abs(math.log(ratio / threshold)), price_rows, libs
            ),
            reliability=price(
                float(
                    np.var(blocks["solved"]["R-TS"], ddof=1)
                    + np.var(blocks["solved"][denom], ddof=1)
                    if denom == "R-DG"
                    else np.var(
                        blocks["solved"]["R-TS"] - blocks["solved"][denom], ddof=1
                    )
                ),
                float(
                    (blocks["solved"]["R-TS"] - blocks["solved"][denom]).mean() + 0.03
                ),
                price_rows,
                libs,
            ),
        )
    economics = {}
    for metric in ("evaluations", "worker_seconds"):
        econ = {}
        for arm in arms:
            if arm == "R-tree":
                continue
            owner = "DG" if arm == "R-DG" else "TS"
            ix = independent if owner == "DG" else selected
            acq = acquisition(libs, owner, metric, arm == "R-sizeTS")
            search = blocks[metric][arm]
            baseline = blocks[metric]["R-tree"]
            saving = baseline - search
            savings = saving[ix].mean(axis=1)
            amortized = acq[ix].mean(axis=1)
            finite = savings > 0
            repay = amortized[finite] / savings[finite]
            econ[arm] = dict(
                acquisition=estimate(acq.mean(), amortized),
                saving_per_search=estimate(saving.mean(), savings),
                repayment_searches=None
                if saving.mean() <= 0
                else float(acq.mean() / saving.mean()),
                repayment_interval95=None
                if not finite.all()
                else np.quantile(repay, [0.025, 0.975]).tolist(),
                repayment_unbounded_fraction=float((~finite).mean()),
                horizons={
                    str(n): dict(
                        acquired=estimate(
                            acq.mean() + n * search.mean(),
                            amortized + n * search[ix].mean(axis=1),
                        ),
                        baseline=estimate(
                            n * baseline.mean(), n * baseline[ix].mean(axis=1)
                        ),
                        ratio=estimate(
                            (acq.mean() + n * search.mean()) / (n * baseline.mean()),
                            (amortized + n * search[ix].mean(axis=1))
                            / (n * baseline[ix].mean(axis=1)),
                        ),
                    )
                    for n in HORIZONS
                },
            )
        economics[metric] = econ
    diagnostics = {}
    for a in arms:
        rs = [r for r in rows if r["arm"] == a]
        attempts = [x for r in rs for x in r["attempts"]]
        op = {
            k: sum(x["operator"].get(k, 0) for x in attempts)
            for k in sorted({k for x in attempts for k in x["operator"]})
        }
        draws = op.get("library_draws", 0)
        diagnostics[a] = dict(
            operator=op,
            insertion_fraction=None
            if not draws
            else op.get("library_insertions", 0) / draws,
            oversize_fraction=None
            if not draws
            else op.get("rejected_library", 0) / draws,
            mean_attempts=float(np.mean([r["attempt_count"] for r in rs])),
            attempt_histogram={
                str(k): sum(r["attempt_count"] == k for r in rs) for k in range(1, 9)
            },
            failed_jobs=sum(not r["solved"] for r in rs),
            evaluation_quantiles=np.quantile(
                [r["evaluations"] for r in rs], [0, 0.5, 0.9, 0.95, 1]
            ).tolist(),
        )
    per_cell = {}
    for ci, c in enumerate(cells):
        v = {a: values["evaluations"][a][:, ci, :].mean(axis=1) for a in arms}
        per_cell[c] = dict(
            arms={
                a: dict(
                    mean_evaluations=float(v[a].mean()),
                    solve_fraction=float(values["solved"][a][:, ci, :].mean()),
                )
                for a in arms
            },
            ratios={
                "R-TS/" + a: estimate(
                    v["R-TS"].mean() / v[a].mean(),
                    v["R-TS"][selected].mean(axis=1)
                    / v[a][independent if a == "R-DG" else selected].mean(axis=1),
                )
                for a in arms
                if a != "R-TS"
            },
        )
    sensitivity = {}
    for denom in arms:
        if denom == "R-TS":
            continue
        num, den = values["evaluations"]["R-TS"], values["evaluations"][denom]
        sn, sd = (
            values["solved"]["R-TS"].astype(bool),
            values["solved"][denom].astype(bool),
        )
        common = sn & sd
        sensitivity[denom] = dict(
            common_solved_jobs=int(common.sum()),
            common_solved_ratio=None
            if not common.any()
            else float(num[common].mean() / den[common].mean()),
            alternative_failure_charge_ratios={
                str(f): float(
                    np.where(sn, num, f * 524288).mean()
                    / np.where(sd, den, f * 524288).mean()
                )
                for f in (0.5, 1, 2)
            },
            scope="conditional common-solve costs and hypothetical failure charges; primary keeps actual fixed cap",
        )
    primary = contrasts["R-TS/R-tree"]
    return dict(
        means={
            m: {a: float(v.mean()) for a, v in arrays.items()}
            for m, arrays in blocks.items()
        },
        solve_counts={a: sum(r["solved"] for r in rows if r["arm"] == a) for a in arms},
        contrasts=contrasts,
        decision=classify(
            primary["evaluations"]["interval95"],
            primary["solve_fraction_difference"]["interval95"],
        ),
        content_contrast_status=(
            "not_scored"
            if "R-sizeTS" not in arms
            else "content_increment_supported"
            if contrasts["R-TS/R-sizeTS"]["evaluations"]["interval95"][1] < 1
            else "content_disadvantage_supported"
            if contrasts["R-TS/R-sizeTS"]["evaluations"]["interval95"][0] > 1
            else "content_increment_unresolved"
        ),
        economics=economics,
        resolution_price=prices,
        diagnostics=diagnostics,
        per_cell=per_cell,
        per_build=[
            dict(
                build=b,
                arms={a: {m: float(blocks[m][a][b]) for m in blocks} for a in arms},
                ratios={
                    "R-TS/" + a: float(
                        blocks["evaluations"]["R-TS"][b] / blocks["evaluations"][a][b]
                    )
                    for a in arms
                    if a != "R-TS"
                },
            )
            for b in range(24)
        ],
        failure_sensitivity=sensitivity,
    )


def library_audit(libs):
    from experiments.chem_tape.tree_gp_search import TERMINALS, FUNCTIONS
    from experiments.chem_tape.gate_sum_bank import pairing
    from experiments.chem_tape import tree_uniform_run as prior

    bank = prior.prior_run.snapshot("bank.json")
    splits = sorted(
        {
            pairing(c)
            for c in bank["screen"]["cells"]
            if c["id"] in prior.score_cells(bank)
        }
    )
    result = {}
    for owner, libraries in libs.items():
        records = []
        for lib in libraries:
            labels = Counter(op for e in lib["entries"] for op in e["prefix"])
            sums = [
                e["canonical"][1:]
                for e in lib["entries"]
                if e["canonical"][0] == 9
                and e["nodes"] == 3
                and all(op < 4 for op in e["canonical"][1:])
            ]
            records.append(
                dict(
                    build=lib["build"],
                    entries=len(lib["entries"]),
                    entry_nodes=[e["nodes"] for e in lib["entries"]],
                    compiled_lengths=[e["compiled_length"] for e in lib["entries"]],
                    labels={
                        name: labels[i] for i, name in enumerate(TERMINALS + FUNCTIONS)
                    },
                    pair_sums=sums,
                    pair_sums_by_destination_split={
                        str(p): sum(tuple(sorted(s)) in p for s in sums) for p in splits
                    },
                    predicate_roots=sum(e["prefix"][0] == 10 for e in lib["entries"]),
                    seven_node_predicates=sum(
                        e["prefix"][0] == 10 and e["nodes"] == 7 for e in lib["entries"]
                    ),
                    source_solves=lib["source_solves"],
                    source_by_cell=lib["source_by_cell"],
                    acquisition_evaluations=lib["acquisition_evaluations"],
                    acquisition_worker_seconds=lib["acquisition_worker_seconds"],
                    extraction_seconds=lib["extraction_seconds"],
                    verification_seconds=lib["verification_seconds"],
                    control_seconds=lib["control_seconds"],
                    control_draws=[e["draws"] for e in lib["controls"]],
                )
            )
        result[owner] = records
    return result


def summarize(rows, libs, targets):
    if len(rows) != 9216 or {r["family"] for r in rows} != {"GS", "TS"}:
        raise ValueError("requires all 9,216 scoring jobs")
    rng = np.random.default_rng(seed("bootstrap"))
    selected = rng.integers(24, size=(DRAWS, 24))
    independent = rng.integers(24, size=(DRAWS, 24))
    destinations = {
        f: summarize_family(
            [r for r in rows if r["family"] == f],
            targets[f],
            6 if f == "GS" else 4,
            ARMS if f == "GS" else NATIVE_ARMS,
            libs,
            selected,
            independent,
            rows,
        )
        for f in ("GS", "TS")
    }
    gs, ts = destinations["GS"]["decision"], destinations["TS"]["decision"]
    route = (
        "portable_complete_procedure_return_to_strategy"
        if gs == "worthwhile_saving_supported"
        else "native_only_reuse_return_to_strategy"
        if gs == "saving_at_least_20pct_excluded"
        and ts == "worthwhile_saving_supported"
        else "specified_saving_excluded_both_rosters"
        if gs == ts == "saving_at_least_20pct_excluded"
        else "routing_unsettled_price_resolution"
    )
    return dict(
        destinations=destinations,
        routing=route,
        library_audit=library_audit(libs),
        bootstrap=dict(
            draws=DRAWS,
            seed=seed("bootstrap"),
            unit="24 TS build slots; fixed cells/repeats retained, paired TS/baseline/size; independent DG source-cohort resampling for TS/DG; acquisition jointly resampled with owner build",
        ),
        scope="Development rosters only; externally frozen acquisition, no inheritance or fresh-bank transfer claim. Complete-procedure usefulness does not identify content mechanism.",
        economics_scope="Both sources charged actual acquisition including failures, extraction and entry verification; random-control construction additionally charged only to R-sizeTS. Historical DG worker costs measured on historical host/load; current scoring worker costs at ten-worker load. Shared semantic validation/replay and reconstruction are reported in timing, not repeated per acquired library.",
    )


def plot(out, rows, result):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xs = np.array([256, 4096, 16384, 65536, 131072, 262144, 524288])
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for fi, f in enumerate(("GS", "TS")):
        for a in ARMS if f == "GS" else NATIVE_ARMS:
            rs = [r for r in rows if r["family"] == f and r["arm"] == a]
            axes[fi, 0].plot(
                xs,
                [
                    np.mean([r["solved"] and r["evaluations"] <= x for r in rs])
                    for x in xs
                ],
                label=a,
            )
            for panel, field in ((1, "curve"), (2, "phenotype_diversity_curve")):
                lines = []
                for r in rs:
                    line, offset = [], 0
                    for p in r["attempts"]:
                        line.extend((offset + v[0], v[1]) for v in p[field])
                        offset += p["evaluations"]
                    lines.append(line)
                axes[fi, panel].plot(
                    xs,
                    [
                        np.mean(
                            [
                                ([v for t, v in line if t <= x] or [line[0][1]])[-1]
                                for line in lines
                            ]
                        )
                        for x in xs
                    ],
                    label=a,
                )
        for ax, title in zip(
            axes[fi],
            (
                "D625 solve fraction",
                "Training best (restart resets)",
                "Output diversity",
            ),
        ):
            ax.set_title(f + ": " + title)
            ax.set_xscale("log")
            ax.set_xlabel("Evaluations")
            ax.legend()
    fig.tight_layout()
    fig.savefig(out / "dynamics.png", dpi=130)
    plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for fi, f in enumerate(("GS", "TS")):
        for mi, m in enumerate(("evaluations", "worker_seconds")):
            ax = axes[fi, mi]
            for a, e in result["destinations"][f]["economics"][m].items():
                vals = [e["horizons"][str(n)]["ratio"] for n in HORIZONS]
                ax.plot(HORIZONS, [v["point"] for v in vals], label=a + " / R-tree")
                ax.fill_between(
                    HORIZONS,
                    [v["interval95"][0] for v in vals],
                    [v["interval95"][1] for v in vals],
                    alpha=0.15,
                )
            ax.axhline(1, color="black", linewidth=0.7)
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_title(f + ": acquisition + searches, " + m)
            ax.set_xlabel("Searches per library")
            ax.legend()
    fig.tight_layout()
    fig.savefig(out / "economics.png", dpi=130)
    plt.close(fig)


def report(out, rows, libs, targets, preparation, timing):
    result = summarize(rows, libs, targets)
    result |= dict(
        rows_hash=digest(rows),
        preparation_hash=preparation["preparation_hash"],
        timing=timing,
    )
    write_json(out, "result.json", result)
    lines = [
        "# Tree libraries acquired from branch-sum sources (0833)",
        "",
        result["scope"],
        "",
        result["routing"],
        "",
    ]
    for f, d in result["destinations"].items():
        lines += [
            f + ": " + d["decision"],
            "",
            "| Contrast | Evaluation ratio (95%) | Worker ratio (95%) | Solve difference (95%) |",
            "|---|---|---|---|",
        ]
        for name, c in d["contrasts"].items():
            lines.append(
                "| "
                + " | ".join(
                    [name]
                    + [
                        f"{c[m]['point']:.4g} {c[m]['interval95']}"
                        for m in (
                            "evaluations",
                            "worker_seconds",
                            "solve_fraction_difference",
                        )
                    ]
                )
                + " |"
            )
        lines += [
            "",
            "Exact solves: " + str(d["solve_counts"]),
            "",
            "Content contrast: " + d["content_contrast_status"],
            "",
        ]
    lines += [
        result["economics_scope"],
        "",
        "See result.json for per-cell/per-build contrasts, donor content by split, insertion and oversize rates, failure sensitivity, charged acquisition curves and conditional resolution prices. No automatic extension.",
        "",
        "A ratio straddling 0.80 or an unresolved reliability guard leaves usefulness unresolved. Excluding a 20% saving does not exclude smaller benefits. A source-cohort difference cannot identify DG skeletons or pair-sum supply as the cause. Return to strategy.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    plot(out, rows, result)
