"""0524 paired build/construction inference and acquisition-inclusive costs."""

import numpy as np

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.gate_sum_bank import pairing
from experiments.chem_tape.tree_library_report import estimate
from experiments.chem_tape.tree_permutation import PAIRS, motifs
from experiments.chem_tape.tree_permutation_run import ARMS, BOOTSTRAP_SEED

DRAWS = 8192
HORIZONS = (1, 10, 50, 100, 500, 1000)


def grid(rows, cells, metric, repeats):
    by = {(r["build"], r["cell"], r["repeat"], r["arm"]): r for r in rows}
    expected = {
        (b, c, r, a)
        for b in range(24)
        for c in cells
        for r in range(repeats)
        for a in ARMS
    }
    if len(cells) != 18 or len(by) != len(rows) or set(by) != expected:
        raise ValueError(
            "requires complete approved 24-build x18-cell xrepeat x3-arm grid"
        )
    for b, c, r in {(b, c, r) for b, c, r, a in expected}:
        rs = [by[b, c, r, a] for a in ARMS]
        if len({tuple(v["seeds"]) for v in rs}) != 1 or any(
            v["realization"] != r % (repeats // 2) for v in rs
        ):
            raise ValueError("paired seeds or construction assignment changed")
    return {
        a: np.array(
            [
                [[float(by[b, c, r, a][metric]) for r in range(repeats)] for c in cells]
                for b in range(24)
            ]
        )
        for a in ARMS
    }


def classify(primary, replication, baseline, reliability, positive):
    if replication["interval95"][1] >= 0.60:
        return "replication_failed_acquisition_choice_unresolved"
    if reliability["interval95"][0] <= -0.03:
        return "reliability_guard_failed_acquisition_choice_unresolved"
    if primary["interval95"][1] < 1.25 and baseline["interval95"][1] < 0.80:
        if positive["interval95"][0] <= 1.5:
            return "search_cost_retained_control_too_weak_acquisition_choice_unresolved"
        return (
            "rearranged_procedure_gain_arrangement_unnecessary_at_this_resolution"
            if primary["interval95"][1] < 1
            else "arrangement_unnecessary_at_this_resolution"
        )
    if primary["interval95"][0] > 1.10 and primary["point"] >= 1.25:
        return "intact_information_beyond_matched_properties_return_to_strategy"
    return "unresolved_price_resolution_return_to_strategy"


def summarize(rows, libraries, bank, preparation):
    cells = bank["split"]["protected"]
    n = preparation["stage_gate"]["realizations"]
    repeats = 2 * n
    metrics = {
        m: grid(rows, cells, m, repeats)
        for m in ("evaluations", "worker_seconds", "solved")
    }
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    builds = rng.integers(24, size=(DRAWS, 24))
    constructions = rng.integers(n, size=(DRAWS, 24, n))
    by = {c["id"]: c for c in bank["screen"]["cells"]}
    indices = {
        str(p): [i for i, c in enumerate(cells) if pairing(by[c]) == p] for p in PAIRS
    }
    bc = indices[str(PAIRS[1])] + indices[str(PAIRS[2])]
    then = [
        i
        for i in bc
        if tuple(sorted((by[cells[i]]["roles"]["E"], by[cells[i]]["roles"]["F"])))
        in PAIRS[0]
    ]
    if len(bc) != 12 or len(then) != 4:
        raise ValueError("registered B/C or learned-then-pair subgroup changed")

    def blocks(values, ix):
        # Both search repeats of a construction stay together; all corresponding
        # reference rows follow precisely the same sampled construction indices.
        return np.stack(
            [values[:, ix, r::n].mean(axis=(1, 2)) for r in range(n)], axis=1
        )

    def sample(v):
        return v[builds[:, :, None], constructions].mean(axis=(1, 2))

    def group(ix):
        values = {
            m: {a: blocks(v, ix) for a, v in arrays.items()}
            for m, arrays in metrics.items()
        }
        means = {
            m: {a: estimate(v.mean(), sample(v)) for a, v in arrays.items()}
            for m, arrays in values.items()
        }
        contrasts = {}
        for a, b in [("R-perm", "R-lib"), ("R-perm", "R-tree"), ("R-lib", "R-tree")]:
            contrasts[a + "/" + b] = {
                m: estimate(
                    values[m][a].mean() / values[m][b].mean(),
                    sample(values[m][a]) / sample(values[m][b]),
                )
                for m in ("evaluations", "worker_seconds")
            }
            d = values["solved"][a] - values["solved"][b]
            contrasts[a + "/" + b]["solve_fraction_difference"] = estimate(
                d.mean(), sample(d)
            )
        return dict(
            cells=[cells[i] for i in ix],
            jobs_per_arm=24 * len(ix) * repeats,
            means=means,
            contrasts=contrasts,
            solve_counts={a: int(metrics["solved"][a][:, ix, :].sum()) for a in ARMS},
        )

    groups = {
        name: group(ix)
        for name, ix in [
            ("B/C", bc),
            ("all", list(range(18))),
            ("B/C learned then-pair", then),
            ("B/C other then-pair", [i for i in bc if i not in then]),
        ]
        + list(indices.items())
    }
    primary = groups["B/C"]["contrasts"]["R-perm/R-lib"]["evaluations"]
    replication = groups["B/C"]["contrasts"]["R-lib/R-tree"]["evaluations"]
    baseline = groups["B/C"]["contrasts"]["R-perm/R-tree"]["evaluations"]
    reliability = groups["B/C"]["contrasts"]["R-perm/R-lib"][
        "solve_fraction_difference"
    ]
    positive = groups[str(PAIRS[0])]["contrasts"]["R-perm/R-lib"]["evaluations"]
    decision = classify(primary, replication, baseline, reliability, positive)
    per_cell = {c: group([i]) for i, c in enumerate(cells)}

    economics = {}
    for name in ("B/C", "all", *map(str, PAIRS)):
        ix = (
            bc if name == "B/C" else list(range(18)) if name == "all" else indices[name]
        )
        economics[name] = {}
        for metric in ("evaluations", "worker_seconds"):
            values = {a: blocks(v, ix) for a, v in metrics[metric].items()}
            economics[name][metric] = {}
            for a in ("R-lib", "R-perm"):
                acq = np.array(
                    [
                        lib["acquisition_evaluations"]
                        if metric == "evaluations"
                        else lib["acquisition_worker_seconds"]
                        + lib["extraction_seconds"]
                        + lib["verification_seconds"]
                        for lib in libraries
                    ]
                )
                overhead = np.zeros((24, n))
                if a == "R-perm" and metric == "worker_seconds":
                    overhead = np.array(
                        [
                            [
                                c["construction_seconds"]
                                for c in lib["constructions"][:n]
                            ]
                            for lib in libraries
                        ]
                    )
                acquire = acq[:, None] + overhead
                saving = values["R-tree"] - values[a]
                saving_boot = sample(saving)
                acq_boot = sample(acquire)
                rate = saving_boot / acq_boot
                low, high = np.quantile(rate, [0.025, 0.975])
                economics[name][metric][a] = dict(
                    acquisition=estimate(acquire.mean(), acq_boot),
                    savings=estimate(saving.mean(), saving_boot),
                    repayment_searches=None
                    if saving.mean() <= 0
                    else float(acquire.mean() / saving.mean()),
                    repayment_interval95=[
                        None if high <= 0 else float(1 / high),
                        None if low <= 0 else float(1 / low),
                    ],
                    repayment_unbounded=bool(low <= 0),
                    horizons={
                        str(h): {
                            arm: estimate(v.mean(), sample(v))
                            for arm, v in [
                                ("R-tree", h * values["R-tree"]),
                                (a, acquire + h * values[a]),
                            ]
                        }
                        for h in HORIZONS
                    },
                )

    diagnostics = {}
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]
        operators = [t["operator"] for r in rs for t in r["attempts"]]
        diagnostics[a] = dict(
            jobs=len(rs),
            solves=sum(r["solved"] for r in rs),
            failed_jobs=sum(not r["solved"] for r in rs),
            attempt_of_solve={
                str(k): sum(r["solved"] and r["attempt_count"] == k for r in rs)
                for k in range(1, 9)
            },
            operator_totals={
                key: sum(op.get(key, 0) for op in operators)
                for key in sorted(set().union(*(op.keys() for op in operators)))
            },
            worker_seconds=sum(r["worker_seconds"] for r in rs),
        )
    per_construction = []
    for lib in libraries:
        for realization in range(n):
            donor = motifs(lib["constructions"][realization]["entries"])
            for name, ix in [("B/C", bc)] + list(indices.items()):
                rs = [
                    r
                    for r in rows
                    if r["build"] == lib["build"]
                    and r["realization"] == realization
                    and r["cell"] in {cells[i] for i in ix}
                ]
                per_construction.append(
                    dict(
                        build=lib["build"],
                        realization=realization,
                        group=name,
                        motifs=donor,
                        means={
                            a: {
                                m: float(np.mean([r[m] for r in rs if r["arm"] == a]))
                                for m in ("evaluations", "worker_seconds", "solved")
                            }
                            for a in ARMS
                        },
                    )
                )

    def price(stat, threshold):
        # Conditional scaling of achieved hierarchical interval with acquisition
        # count, holding the construction/repeat design fixed. Not guaranteed power.
        half = (stat["interval95"][1] - stat["interval95"][0]) / 2
        gap = abs(stat["point"] - threshold)
        total = None if gap == 0 else max(24, int(np.ceil(24 * (half / gap) ** 2)))
        extra = None if total is None else total - 24
        worker_per_build = np.mean(
            [
                sum(r["worker_seconds"] for r in rows if r["build"] == b)
                + libraries[b]["acquisition_worker_seconds"]
                + libraries[b]["extraction_seconds"]
                + libraries[b]["verification_seconds"]
                for b in range(24)
            ]
        )
        return dict(
            threshold=threshold,
            conditional_total_acquisitions=total,
            additional_acquisitions=extra,
            additional_jobs=None if extra is None else extra * (32 + 18 * repeats * 3),
            additional_worker_seconds=None
            if extra is None
            else float(extra * worker_per_build),
            achieved_relative_interval_half_width=None
            if stat["point"] == 0
            else half / abs(stat["point"]),
            caveat="conditional inverse-square scaling of observed hierarchical interval at fixed effect/construction design; no guaranteed resolution or automatic top-up",
        )

    return dict(
        decision=decision,
        primary_group="B/C",
        primary=primary,
        replication_guard=replication,
        reliability_guard=reliability,
        positive_control=positive,
        baseline_guard=baseline,
        groups=groups,
        per_cell=per_cell,
        per_construction=per_construction,
        diagnostics=diagnostics,
        economics=economics,
        resolution_price=dict(
            retention=price(primary, 1.25),
            intact_advantage_lower=price(primary, 1.10),
            replication=price(replication, 0.60),
            reliability=price(reliability, -0.03),
            positive_control=price(positive, 1.5),
        ),
        bootstrap=dict(
            draws=DRAWS,
            seed=BOOTSTRAP_SEED,
            builds=24,
            constructions_per_build=n,
            unit="paired hierarchical resampling of builds, then construction blocks within each sampled build; both repeats, corresponding reference rows and all fixed cells retained together",
        ),
        scope="Development-bank replacement of externally fitted frozen libraries. Retention concerns this shape/count-conditioned procedure, not token-only sufficiency, cheaper acquisition or causal decomposition. A gain from rearrangement is consistent with redistributed pairs, but also changes operator placement, repeated-input expressions and other joint content. Intact advantage is information beyond matched properties. A sensitivity check is on a different split and does not identify selective destruction on B/C.",
        economics_scope="Both donor arms charged all original source jobs including failures, extraction and original verification; R-perm additionally charged each construction. Reconstruction and full experimental validation are separately logged execution overhead, not fresh acquisition. Evaluation costs and load-dependent worker seconds are separate; finite capped search and fixed horizons, no assumed reuse horizon.",
        finite_sample_note="Zero observed failures does not establish absence of population reliability loss; decision requires the registered three-point noninferiority guard.",
    )


def report(out, rows, libraries, bank, preparation, timing):
    result = summarize(rows, libraries, bank, preparation)
    result.update(
        rows_hash=digest(rows),
        preparation_hash=preparation["preparation_hash"],
        timing=timing,
    )
    write_json(out, "result.json", result)
    lines = [
        "# Shape/count-conditioned tree-library replacement (0524)",
        "",
        result["scope"],
        "",
        "Decision: " + result["decision"],
        "",
        "| Group | Contrast | Evaluation ratio (95%) | Solve difference (95%) |",
        "|---|---|---|---|",
    ]
    for name, group in result["groups"].items():
        for contrast, value in group["contrasts"].items():
            ratio = value["evaluations"]
            solves = value["solve_fraction_difference"]
            lines.append(
                f"| {name} | {contrast} | {ratio['point']:.4g} {ratio['interval95']} | {solves['point']:.4g} {solves['interval95']} |"
            )
    lines += [
        "",
        "Exact B/C solves: " + str(result["groups"]["B/C"]["solve_counts"]),
        "",
        result["finite_sample_note"],
        "",
        result["economics_scope"],
        "",
        "Replication and reliability guards take precedence. Cost retention with split A lower bound <=1.5 is control too weak; acquisition choice remains unresolved. Intact advantage requires lower >1.10 and point >=1.25; all other patterns remain unresolved. No additional seeds follow automatically. Per-cell, per-construction pair/predicate supply, operator counts, worker costs, acquisition-inclusive curves and conditional resolution prices are in result.json. Return to strategy.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    plot(out, rows, result)


def plot(out, rows, result):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    cells = set(result["groups"]["B/C"]["cells"])
    for a in ARMS:
        costs = np.sort(
            [r["evaluations"] for r in rows if r["arm"] == a and r["cell"] in cells]
        )
        axes[0].step(costs, np.arange(1, len(costs) + 1) / len(costs), label=a)
    axes[0].set(
        xscale="log", xlabel="B/C capped evaluations", ylabel="Fraction of jobs"
    )
    axes[0].legend()
    for i, name in enumerate(map(str, PAIRS)):
        stat = result["groups"][name]["contrasts"]["R-perm/R-lib"]["evaluations"]
        axes[1].errorbar(
            i,
            stat["point"],
            yerr=np.array(
                [
                    [stat["point"] - stat["interval95"][0]],
                    [stat["interval95"][1] - stat["point"]],
                ]
            ),
            fmt="o",
        )
    axes[1].set(
        xticks=range(3),
        xticklabels=["A", "B", "C"],
        ylabel="R-perm / R-lib capped cost (95%)",
    )
    axes[1].axhline(1.25, ls="--", color="gray")
    fig.tight_layout()
    fig.savefig(out / "dynamics.png")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, metric in zip(axes, ("evaluations", "worker_seconds")):
        for a in ("R-lib", "R-perm"):
            horizons = result["economics"]["B/C"][metric][a]["horizons"]
            for arm in (a, "R-tree") if a == "R-lib" else (a,):
                ax.plot(
                    HORIZONS,
                    [horizons[str(n)][arm]["point"] for n in HORIZONS],
                    marker="o",
                    label=arm,
                )
        ax.set(
            xscale="log",
            yscale="log",
            xlabel="B/C searches per acquisition",
            ylabel="Acquisition + search " + metric,
        )
        ax.legend()
    fig.tight_layout()
    fig.savefig(out / "economics.png")
    plt.close(fig)
