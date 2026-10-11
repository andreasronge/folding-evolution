"""0652 paired, equally weighted realization inference on B/C replacement."""

import numpy as np

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.gate_sum_bank import pairing
from experiments.chem_tape.tree_library_report import estimate
from experiments.chem_tape.tree_permutation import PAIRS, motifs
from experiments.chem_tape.tree_uniform_run import BOOTSTRAP_SEED, score_cells

DRAWS = 8192
HORIZONS = (1, 10, 50, 100, 500, 1000)


def grid(rows, cells, metric, repeats, arms):
    by = {(r["build"], r["cell"], r["repeat"], r["arm"]): r for r in rows}
    expected = {
        (b, c, r, a)
        for b in range(24)
        for c in cells
        for r in range(repeats)
        for a in arms
    }
    if len(cells) != 12 or len(by) != len(rows) or set(by) != expected:
        raise ValueError(
            "requires complete approved 24-build x12-cell xrepeat xactive-arm grid"
        )
    for b, c, r in {(b, c, r) for b, c, r, a in expected}:
        rs = [by[b, c, r, a] for a in arms]
        if len({tuple(v["seeds"]) for v in rs}) != 1 or any(
            v["realization"] != r % 3 for v in rs
        ):
            raise ValueError("paired seeds or construction assignment changed")
    return {
        a: np.array(
            [
                [[float(by[b, c, r, a][metric]) for r in range(repeats)] for c in cells]
                for b in range(24)
            ]
        )
        for a in arms
    }


def classify(primary, intact, baseline, reliability, guards):
    if any(s["interval95"][1] >= 0.60 for s in guards.values()):
        return "validity_failed_acquisition_choice_unresolved"
    if primary["interval95"][0] > 1.10 and primary["point"] >= 1.25:
        return "worthwhile_uniform_replacement_loss_return_to_strategy"
    if (
        primary["interval95"][1] < 1.25
        and baseline["interval95"][1] < 0.80
        and reliability["interval95"][0] > -0.03
    ):
        if intact["interval95"][1] < 1.25:
            return "uniform_replacement_retains_acquired_benefit_at_this_resolution"
        return "matches_R_perm_relation_to_intact_unresolved"
    return "unresolved_price_resolution_return_to_strategy"


def summarize(rows, libraries, bank, preparation):
    cells = score_cells(bank)
    n = 3
    repeats = preparation["stage_gate"]["repeats"]
    arms = tuple(preparation["stage_gate"]["active_arms"])
    metrics = {
        m: grid(rows, cells, m, repeats, arms)
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
        # Average repeats within each realization first (also 2/1/1 fallback);
        # give three realizations equal weight. All corresponding
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
        for a, b in [
            ("R-unif", "R-perm"),
            ("R-unif", "R-lib"),
            ("R-unif", "R-tree"),
            ("R-perm", "R-tree"),
            ("R-lib", "R-tree"),
        ] + ([("R-size", "R-unif")] if "R-size" in arms else []):
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
            solve_counts={a: int(metrics["solved"][a][:, ix, :].sum()) for a in arms},
        )

    groups = {
        name: group(ix)
        for name, ix in [
            ("B/C", bc),
            ("B/C learned then-pair", then),
            ("B/C other then-pair", [i for i in bc if i not in then]),
            ("B", indices[str(PAIRS[1])]),
            ("C", indices[str(PAIRS[2])]),
        ]
    }
    contrasts = groups["B/C"]["contrasts"]
    primary = contrasts["R-unif/R-perm"]["evaluations"]
    intact = contrasts["R-unif/R-lib"]["evaluations"]
    baseline = contrasts["R-unif/R-tree"]["evaluations"]
    reliability = contrasts["R-unif/R-perm"]["solve_fraction_difference"]
    intact_reliability = contrasts["R-unif/R-lib"]["solve_fraction_difference"]
    guards = {a: contrasts[a + "/R-tree"]["evaluations"] for a in ("R-lib", "R-perm")}
    decision = classify(primary, intact, baseline, reliability, guards)
    per_cell = {c: group([i]) for i, c in enumerate(cells)}

    economics = {}
    for name, ix in [
        ("B/C", bc),
        ("B", indices[str(PAIRS[1])]),
        ("C", indices[str(PAIRS[2])]),
    ]:
        economics[name] = {}
        for metric in ("evaluations", "worker_seconds"):
            values = {a: blocks(v, ix) for a, v in metrics[metric].items()}
            economics[name][metric] = {}
            for a in ("R-lib", "R-perm", "R-unif"):
                acq = np.array(
                    [
                        (2_880_000 if a == "R-unif" else lib["acquisition_evaluations"])
                        if metric == "evaluations"
                        else lib["acquisition_worker_seconds"]
                        + lib["extraction_seconds"]
                        + lib["verification_seconds"]
                        for lib in libraries
                    ]
                )
                overhead = np.zeros((24, n))
                if a in ("R-perm", "R-unif") and metric == "worker_seconds":
                    overhead = np.array(
                        [
                            [
                                c["construction_seconds"]
                                for c in lib[
                                    "uniform_constructions"
                                    if a == "R-unif"
                                    else "constructions"
                                ][:n]
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
    for a in arms:
        rs = [r for r in rows if r["arm"] == a]
        operators = [t["operator"] for r in rs for t in r["attempts"]]
        totals = {
            key: sum(op.get(key, 0) for op in operators)
            for key in sorted(set().union(*(op.keys() for op in operators)))
        }
        draws = totals.get("library_draws", 0)
        diagnostics[a] = dict(
            jobs=len(rs),
            solves=sum(r["solved"] for r in rs),
            failed_jobs=sum(not r["solved"] for r in rs),
            attempt_of_solve={
                str(k): sum(r["solved"] and r["attempt_count"] == k for r in rs)
                for k in range(1, 9)
            },
            operator_totals=totals,
            insertion_fraction_of_library_draws=None
            if not draws
            else totals.get("library_insertions", 0) / draws,
            rejection_fraction_of_library_draws=None
            if not draws
            else totals.get("rejected_library", 0) / draws,
            library_fraction_of_mutations=None
            if not totals.get("mutation")
            else draws / totals["mutation"],
            worker_seconds=sum(r["worker_seconds"] for r in rs),
        )
    per_construction = []
    for lib in libraries:
        for realization in range(n):
            donor = motifs(lib["constructions"][realization]["entries"])
            for name, ix in [
                ("B/C", bc),
                ("B", indices[str(PAIRS[1])]),
                ("C", indices[str(PAIRS[2])]),
            ]:
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
                        motifs=dict(
                            R_perm=donor,
                            R_unif=motifs(
                                lib["uniform_constructions"][realization]["entries"]
                            ),
                        ),
                        means={
                            a: {
                                m: float(np.mean([r[m] for r in rs if r["arm"] == a]))
                                for m in ("evaluations", "worker_seconds", "solved")
                            }
                            for a in arms
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
            additional_jobs=None
            if extra is None
            else extra * (32 + 12 * repeats * len(arms)),
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
        validity_guards=guards,
        intact_comparison=intact,
        intact_reliability=intact_reliability,
        reliability_guard=reliability,
        baseline_guard=baseline,
        groups=groups,
        per_cell=per_cell,
        per_construction=per_construction,
        diagnostics=diagnostics,
        economics=economics,
        resolution_price=dict(
            retention=price(primary, 1.25),
            worthwhile_loss=price(primary, 1.10),
            intact_retention=price(intact, 1.25),
            uniform_baseline=price(baseline, 0.80),
            reliability=price(reliability, -0.03),
            **{a + "_validity": price(s, 0.60) for a, s in guards.items()},
        ),
        content_audit=preparation["construction_audit"],
        active_arms=list(arms),
        repeats=repeats,
        bootstrap=dict(
            draws=DRAWS,
            seed=BOOTSTRAP_SEED,
            builds=24,
            constructions_per_build=n,
            unit="paired hierarchical resampling of builds, then construction blocks within each sampled build; all repeats within realization averaged first, three realizations equally weighted; corresponding reference rows and all fixed cells retained together",
        ),
        scope="Development-bank donor replacement informing a later probabilistic generator. Uniform sufficiency is conditional on acquired skeletons, widths, sizes and multiplicities. Loss supports retaining this empirical construction; it does not separate ADD dilution, ANY supply, constants, joint labels or finite-library dependency changes. Retention does not establish a causal skeleton advantage, no-learning sufficiency or fresh transfer. PIPE is prospective; no learning loop is implemented.",
        economics_scope="R-unif is charged the approved 2.88M-evaluation acquisition budget per build (actual archived source usage is separately retained in libraries.json), original source worker time including failures, extraction and original verification, plus uniform construction worker time. R-lib/R-perm retain their actual original acquisition costs. Rebuilding and whole-experiment validation are separately logged overhead. No cheaper acquisition is established.",
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
        "# Uniform compatible donor labels (0652)",
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
        "Validity guards take precedence. Worthwhile replacement loss requires lower >1.10 and point >=1.25. Uniform retention requires primary upper <1.25, R-unif/R-tree upper <0.80 and solve-difference lower >-0.03 against R-perm. Intact benefit additionally requires R-unif/R-lib upper <1.25; intact reliability is reported separately. Other outcomes leave acquisition choice unresolved. Return to strategy without automatic top-up.",
        "Per-cell and realization costs, content and operator audits, acquisition-inclusive curves and conditional precision prices are in result.json. Raw solve counts differ from the equally weighted estimand under four repeats.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    plot(out, rows, result)


def plot(out, rows, result):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    arms = result["active_arms"]
    cells = set(result["groups"]["B/C"]["cells"])
    for a in arms:
        rs = sorted(
            [r for r in rows if r["arm"] == a and r["cell"] in cells],
            key=lambda r: r["evaluations"],
        )
        weights = np.array(
            [
                1 / sum(k % 3 == r["realization"] for k in range(result["repeats"]))
                for r in rs
            ]
        )
        axes[0].step(
            [r["evaluations"] for r in rs], np.cumsum(weights) / weights.sum(), label=a
        )
    axes[0].set(
        xscale="log", xlabel="B/C capped evaluations", ylabel="Fraction of jobs"
    )
    axes[0].legend()
    for i, name in enumerate(("B", "C")):
        stat = result["groups"][name]["contrasts"]["R-unif/R-perm"]["evaluations"]
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
        xticks=range(2),
        xticklabels=["B", "C"],
        ylabel="R-unif / R-perm capped cost (95%)",
    )
    axes[1].axhline(1.25, ls="--", color="gray")
    fig.tight_layout()
    fig.savefig(out / "dynamics.png")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, metric in zip(axes, ("evaluations", "worker_seconds")):
        for a in ("R-lib", "R-perm", "R-unif"):
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
