"""0024: equally weighted fixed cells, paired acquisition-build bootstrap.

Attempts are accounting records. Only whole scheduled jobs enter inference.
"""

import time

import numpy as np
from scipy.stats import norm

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.component_transfer_report import acquisition
from experiments.chem_tape.composition_run import write_json

DRAWS = 8192
BOOT_SEED = 2230024
ARMS = ("R-tree", "R-A8", "F-A8")
METRIC_DEFINITIONS = dict(
    R="ratio of arithmetic mean actual evaluations R-tree / R-A8; eight cells equally weighted, failures spend actual total cap",
    reliability="solve-fraction difference R-tree minus R-A8; lower paired-build 95% bound > -0.03 establishes noninferiority within three percentage points",
    bootstrap="8192 paired resamples of 24 acquisition-build blocks; all fixed cells and repeats retained within block",
    geometric="exp(mean(log(actual solved evaluations or two times total cap for failures))); descriptive sensitivity",
    savings="mean(actual R-tree effort minus actual A8 effort), evaluations and worker seconds separately",
    repayment="historical mean acquisition / contemporaneous mean search saving; interval unbounded when savings admit zero or negative values",
    phenotype_diversity="distinct output vectors on 64 fixed training cases; lower bound on D625 phenotype diversity",
    primitive_case_work="compiled token count times 64 cases, execution-length proxy excluding exact checks and internal primitive costs",
)


def ci(v):
    if not np.all(np.isfinite(v)):
        raise ValueError("nonfinite bootstrap draws")
    return np.quantile(v, [0.025, 0.975]).tolist()


def estimate(point, draws):
    return dict(point=float(point), interval95=ci(draws))


def grid(rows, family, cells, metric):
    rs = [r for r in rows if r["family"] == family]
    by = {(r["cell"], r["arm"], r["build"], r["repeat"]): r for r in rs}
    expected = {
        (c, a, b, s)
        for c in cells
        for a in ARMS
        for b in range(24)
        for s in range(2 if a == "F-A8" else 4)
    }
    if len(cells) != 8 or len(rs) != 1920 or len(by) != len(rs) or set(by) != expected:
        raise ValueError("requires complete 24-build eight-cell 768/768/384 job grid")
    for c in cells:
        for b in range(24):
            for s in range(4):
                if by[c, "R-tree", b, s]["seeds"] != by[c, "R-A8", b, s]["seeds"]:
                    raise ValueError("restart pairing changed")

    def value(r):
        if metric == "geometric":
            return np.log(r["evaluations"] if r["solved"] else 2 * r["cap"])
        return float(r[metric])

    values = {
        a: np.array(
            [
                [
                    [value(by[c, a, b, s]) for s in range(2 if a == "F-A8" else 4)]
                    for c in cells
                ]
                for b in range(24)
            ]
        )
        for a in ARMS
    }
    if any(
        not np.all(np.isfinite(v)) or (metric != "solved" and np.any(v <= 0))
        for v in values.values()
    ):
        raise ValueError("nonpositive/nonfinite measured costs")
    return values


def classify(ratio, difference):
    holds = difference[0] > -0.03
    if ratio[1] < 1:
        verdict = (
            "tree_evaluation_win_with_noninferiority"
            if holds
            else "cheaper_tree_reliability_not_established"
        )
    elif ratio[0] > 1:
        verdict = "A8_evaluation_saving"
    else:
        verdict = "unresolved_cost"
    return dict(
        verdict=verdict,
        reliability_noninferiority=holds,
        reliability_status="within_three_percentage_points"
        if holds
        else (
            "demonstrated_inferiority_beyond_margin"
            if difference[1] < -0.03
            else "unresolved"
        ),
    )


def economics(values, saved, owner, selected):
    result = {}
    for metric, v in values.items():
        acq = np.array([acquisition(saved, owner, b)[metric] for b in range(24)])
        result[metric] = {}
        tree = v["R-tree"].mean(axis=(1, 2))
        for a in ("R-A8", "F-A8"):
            native = v[a].mean(axis=(1, 2))
            savings = tree - native
            saving_boot = savings[selected].mean(axis=1)
            acquisition_boot = acq[selected].mean(axis=1)
            unbounded = ci(saving_boot)[0] <= 0
            positive = saving_boot > 0
            repayment = acquisition_boot[positive] / saving_boot[positive]
            # A finite upper endpoint cannot be reported when saving uncertainty admits <=0.
            horizon = (
                [None, None]
                if not np.any(positive)
                else [
                    float(np.quantile(repayment, 0.025)),
                    None if unbounded else float(np.quantile(repayment, 0.975)),
                ]
            )
            result[metric][a] = dict(
                acquisition=estimate(acq.mean(), acquisition_boot),
                savings=estimate(savings.mean(), saving_boot),
                repayment_searches=None
                if savings.mean() <= 0
                else float(acq.mean() / savings.mean()),
                repayment_interval95=horizon,
                repayment_unbounded=unbounded,
                per_build={
                    str(b): dict(
                        acquisition=float(acq[b]),
                        saving=float(savings[b]),
                        repayment_searches=None
                        if savings[b] <= 0
                        else float(acq[b] / savings[b]),
                    )
                    for b in range(24)
                },
                horizons={
                    str(n): dict(
                        A8=estimate(
                            (acq + n * native).mean(),
                            (acq[selected] + n * native[selected]).mean(axis=1),
                        ),
                        tree=estimate(
                            (n * tree).mean(), (n * tree[selected]).mean(axis=1)
                        ),
                        A8_minus_tree=estimate(
                            (acq - n * savings).mean(),
                            (acq[selected] - n * savings[selected]).mean(axis=1),
                        ),
                    )
                    for n in (1, 16, 256, 1024, 4096)
                },
            )
    return result


def summarize(rows, saved, targets, old):
    selected = np.random.default_rng(BOOT_SEED).integers(24, size=(DRAWS, 24))
    result = {}
    for f in sorted({r["family"] for r in rows}):
        costs = {
            metric: grid(rows, f, targets[f], metric)
            for metric in ("evaluations", "worker_seconds")
        }
        solves = grid(rows, f, targets[f], "solved")
        geometric = grid(rows, f, targets[f], "geometric")
        means = {
            metric: {a: v.mean(axis=(1, 2)) for a, v in values.items()}
            for metric, values in costs.items()
        }
        solve_blocks = {a: v.mean(axis=(1, 2)) for a, v in solves.items()}
        contrasts = {}
        for numerator, denominator in (
            ("R-tree", "R-A8"),
            ("R-tree", "F-A8"),
            ("R-A8", "F-A8"),
        ):
            contrast = {}
            for metric, blocks in means.items():
                boot = {a: v[selected].mean(axis=1) for a, v in blocks.items()}
                contrast[metric] = estimate(
                    blocks[numerator].mean() / blocks[denominator].mean(),
                    boot[numerator] / boot[denominator],
                )
            difference = solve_blocks[numerator] - solve_blocks[denominator]
            contrast["solve_fraction_difference"] = estimate(
                difference.mean(), difference[selected].mean(axis=1)
            )
            g = geometric[numerator].mean(axis=(1, 2)) - geometric[denominator].mean(
                axis=(1, 2)
            )
            contrast["geometric_2cap_ratio"] = estimate(
                np.exp(g.mean()), np.exp(g[selected].mean(axis=1))
            )
            contrasts[numerator + "/" + denominator] = contrast
        primary = contrasts["R-tree/R-A8"]
        cells = {}
        for i, c in enumerate(targets[f]):
            cells[c] = {}
            for a in ARMS:
                rs = [
                    r
                    for r in rows
                    if r["family"] == f and r["cell"] == c and r["arm"] == a
                ]
                attempts = [p for r in rs for p in r["attempts"]]
                blocks = costs["evaluations"][a][:, i, :].mean(axis=1)
                solved = solves[a][:, i, :].mean(axis=1)
                cells[c][a] = dict(
                    jobs=len(rs),
                    solves=sum(r["solved"] for r in rs),
                    evaluations=estimate(blocks.mean(), blocks[selected].mean(axis=1)),
                    solve_fraction=estimate(
                        solved.mean(), solved[selected].mean(axis=1)
                    ),
                    worker_seconds=float(np.mean([r["worker_seconds"] for r in rs])),
                    mean_attempts=float(np.mean([r["attempt_count"] for r in rs])),
                    total_exact_check_seconds=sum(
                        p["exact_check_seconds"] for p in attempts
                    ),
                    total_scheduling_seconds=sum(r["scheduling_seconds"] for r in rs),
                    compiled_tokens_evaluated=sum(
                        p["compiled_tokens_evaluated"] for p in attempts
                    ),
                    primitive_case_work=sum(p["primitive_case_work"] for p in attempts),
                    initialization_rejections=sum(
                        p.get("initialization", {}).get("rejected", 0) for p in attempts
                    ),
                    rejected_subtree_children=sum(
                        p["operator"].get("rejected_crossover", 0)
                        + p["operator"].get("rejected_mutation", 0)
                        for p in attempts
                    ),
                    final_training_output_diversity=float(
                        np.mean(
                            [p["phenotype_diversity_curve"][-1][1] for p in attempts]
                        )
                    ),
                    attempt_histogram={
                        str(k): sum(r["attempt_count"] == k for r in rs)
                        for k in range(1, 9)
                    },
                    solve_cost_curve={
                        str(x): sum(r["solved"] and r["evaluations"] <= x for r in rs)
                        / len(rs)
                        for x in (4096, 16384, 65536, 131072, 262144, 524288)
                    },
                )
        history = [r for r in old[f + ".jsonl"] if r["arm"] == "tree"]
        result[f] = dict(
            contrasts=contrasts,
            decision=classify(
                primary["evaluations"]["interval95"],
                primary["solve_fraction_difference"]["interval95"],
            ),
            means={
                metric: {a: float(v.mean()) for a, v in blocks.items()}
                for metric, blocks in means.items()
            },
            solve_fractions={a: float(v.mean()) for a, v in solve_blocks.items()},
            per_cell=cells,
            economics=economics(costs, saved, "D" if f == "DG" else "T", selected),
            historical_full_cap_tree=dict(
                label="2254 historical unpaired reference, development data",
                jobs=len(history),
                solves=sum(r["solved"] for r in history),
                mean_evaluations=float(np.mean([r["evaluations"] for r in history])),
                mean_worker_seconds=float(
                    np.mean([r["worker_seconds"] for r in history])
                ),
                restarted_to_historical_evaluation_ratio=float(
                    means["evaluations"]["R-tree"].mean()
                    / np.mean([r["evaluations"] for r in history])
                ),
            ),
        )
        if f == "DG":
            # Linearized ratio and solve difference variances at observed points.
            a, b = means["evaluations"]["R-tree"], means["evaluations"]["R-A8"]
            ratio = a.mean() / b.mean()
            influence = (a - ratio * b) / b.mean()
            difference = solve_blocks["R-tree"] - solve_blocks["R-A8"]
            prices = {}
            for name, blocks, gap in (
                ("evaluation_ratio", influence, abs(ratio - 1)),
                ("reliability_margin", difference, abs(difference.mean() + 0.03)),
            ):
                needed = (
                    None
                    if gap == 0
                    else int(
                        np.ceil(norm.ppf(0.975) ** 2 * np.var(blocks, ddof=1) / gap**2)
                    )
                )
                extra = None if needed is None else max(0, needed - 24)
                search_seconds = (
                    sum(
                        r["worker_seconds"]
                        for r in rows
                        if r["family"] == "DG" and r["arm"] != "F-A8"
                    )
                    / 24
                )
                acquisition_seconds = np.mean(
                    [acquisition(saved, "D", j)["worker_seconds"] for j in range(24)]
                )
                prices[name] = dict(
                    conditional_total_builds=needed,
                    additional_builds=extra,
                    additional_worker_seconds=None
                    if extra is None
                    else float(extra * (search_seconds + acquisition_seconds)),
                    caveat="normal approximation at observed point/variance; DG-only search + historical fresh acquisition price; no guarantee, no automatic top-up",
                )
            result[f]["resolution_price"] = prices
    return result


def sensitivity(rows, cells):
    """Empirical independent-attempt scenarios, explicitly retaining fixed builds."""
    start = time.monotonic()
    rng = np.random.default_rng(2230025)
    base = {}
    for a in ("tree", "A8"):
        by = {(r["build"], r["cell"], r["repeat"]): r for r in rows if r["arm"] == a}
        base[a] = np.array(
            [
                [
                    [
                        [
                            min(by[b, c, s]["evaluations"], 65536),
                            by[b, c, s]["solved"]
                            and by[b, c, s]["evaluations"] <= 65536,
                        ]
                        for s in range(2)
                    ]
                    for c in cells
                ]
                for b in range(24)
            ]
        )
    result = {}
    for mode in ("cell_pool", "build_pool", "cell_build"):
        scenarios, analytic = {}, {}
        for a, v in base.items():
            if mode == "cell_pool":
                pool = v.transpose(1, 0, 2, 3).reshape(8, 48, 2)
                p = pool[:, :, 1].mean(axis=1)
                e = pool[:, :, 0].mean(axis=1)
            elif mode == "build_pool":
                pool = v.reshape(24, 16, 2)
                p = pool[:, :, 1].mean(axis=1)
                e = pool[:, :, 0].mean(axis=1)
            else:
                pool = v
                p = v[:, :, :, 1].mean(axis=2)
                e = v[:, :, :, 0].mean(axis=2)
            analytic[a] = dict(
                evaluations=float(np.mean(e * sum((1 - p) ** k for k in range(8)))),
                solve_fraction=float(np.mean(1 - (1 - p) ** 8)),
            )
            scenarios[a] = pool
        resolved = reliable = joint = 0
        ratios = []
        for _ in range(256):
            blocks = {}
            # Historic arms share seeds; sample their matched rows together.
            indices = rng.integers(
                next(iter(scenarios.values())).shape[-2], size=(24, 8, 4, 8)
            )
            for a, pool in scenarios.items():
                if mode == "cell_pool":
                    samples = pool[np.arange(8)[None, :, None, None], indices]
                elif mode == "build_pool":
                    samples = pool[np.arange(24)[:, None, None, None], indices]
                else:
                    samples = pool[
                        np.arange(24)[:, None, None, None],
                        np.arange(8)[None, :, None, None],
                        indices,
                    ]
                hits = samples[..., 1].astype(bool)
                any_hit = hits.any(axis=3)
                first = np.where(any_hit, hits.argmax(axis=3), 7)
                cost = (samples[..., 0] * (np.arange(8) <= first[..., None])).sum(
                    axis=3
                )
                blocks[a] = (cost.mean(axis=(1, 2)), any_hit.mean(axis=(1, 2)))
            selected = rng.integers(24, size=(512, 24))
            r = blocks["tree"][0][selected].mean(axis=1) / blocks["A8"][0][
                selected
            ].mean(axis=1)
            d = (blocks["tree"][1] - blocks["A8"][1])[selected].mean(axis=1)
            win = ci(r)[1] < 1
            guard = ci(d)[0] > -0.03
            resolved += win
            reliable += guard
            joint += win and guard
            ratios.append(blocks["tree"][0].mean() / blocks["A8"][0].mean())
        result[mode] = dict(
            analytic=analytic,
            simulation_datasets=256,
            bootstrap_draws_per_dataset=512,
            evaluation_win_frequency=resolved / 256,
            reliability_guard_frequency=reliable / 256,
            joint_frequency=joint / 256,
            simulated_ratio_range95=ci(ratios),
        )
    return dict(
        scenarios=result,
        worker_seconds=time.monotonic() - start,
        assumptions="paired historical rows across arms; independent empirical attempts within fixed build per job; only two observations per cell/build; sensitivity, not validated power or dependence test",
    )


def plot(out, rows, families):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(
        len(families), 4, figsize=(18, 4 * len(families)), squeeze=False
    )
    for i, f in enumerate(families):
        for a in ARMS:
            rs = [r for r in rows if r["family"] == f and r["arm"] == a]
            xs = np.array((256, 4096, 16384, 65536, 131072, 262144, 524288))
            axes[i, 0].plot(
                xs,
                [
                    np.mean([r["solved"] and r["evaluations"] <= x for r in rs])
                    for x in xs
                ],
                label=a,
            )
            for panel, field in ((1, "curve"), (2, "phenotype_diversity_curve")):
                ys = []
                for x in xs:
                    values = []
                    for r in rs:
                        timeline, offset = [], 0
                        for p in r["attempts"]:
                            timeline.extend(
                                (offset + point[0], point[1]) for point in p[field]
                            )
                            offset += p["evaluations"]
                        values.append(
                            ([p[1] for p in timeline if p[0] <= x] or [timeline[0][1]])[
                                -1
                            ]
                        )
                    ys.append(np.mean(values))
                axes[i, panel].plot(xs, ys, label=a)
            axes[i, 3].plot(
                range(1, 9),
                [
                    sum(r["attempt_count"] == k for r in rs) / len(rs)
                    for k in range(1, 9)
                ],
                label=a,
            )
        for j, title in enumerate(
            (
                "D625 solves by expenditure",
                "Training best score (reset at restart)",
                "Training output diversity (held after stop)",
                "Attempts per scheduled job",
            )
        ):
            axes[i, j].set_title(f + ": " + title)
            axes[i, j].legend()
            if j < 3:
                axes[i, j].set_xscale("log")
    fig.tight_layout()
    fig.savefig(out / "dynamics.png", dpi=130)
    plt.close(fig)
    fig, axes = plt.subplots(
        len(families), 2, figsize=(12, 4 * len(families)), squeeze=False
    )
    for i, (family, summary) in enumerate(families.items()):
        for j, metric in enumerate(("evaluations", "worker_seconds")):
            panel = axes[i, j]
            curves = summary["economics"][metric]
            tree = next(iter(curves.values()))["horizons"]
            for arm, horizons, field in [("R-tree", tree, "tree")] + [
                (arm, curve["horizons"], "A8") for arm, curve in curves.items()
            ]:
                ns = sorted(int(n) for n in horizons)
                measured = [horizons[str(n)][field] for n in ns]
                panel.plot(ns, [v["point"] for v in measured], label=arm)
                panel.fill_between(
                    ns,
                    [v["interval95"][0] for v in measured],
                    [v["interval95"][1] for v in measured],
                    alpha=0.15,
                )
            panel.set_xscale("log")
            panel.set_yscale("log")
            panel.set_title(family + ": acquisition + N × search (" + metric + ")")
            panel.set_xlabel("Searches per deployed build")
            panel.legend()
    fig.text(
        0.5,
        0.01,
        "Point estimates and paired-build 95% intervals; acquisition timing is historical, search timing contemporary.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(out / "economics.png", dpi=130)
    plt.close(fig)


def report(out, rows, saved, targets, old, preparation, timing):
    from experiments.chem_tape.restart_gp_run import key

    rows = sorted(rows, key=lambda r: str(key(r)))
    families = summarize(rows, saved, targets, old)
    result = dict(
        families=families,
        metric_definitions=METRIC_DEFINITIONS,
        rows_hash=digest(rows),
        preparation_hash=preparation["preparation_hash"],
        timing=timing,
        primary="DG R-tree/R-A8 arithmetic evaluations with paired reliability guard",
        scope="fixed DG/TS development rosters; no transfer or optimal-policy claim",
        acquisition_timing="historical acquisition worker seconds plus contemporary search seconds; hardware/load limits; point-estimates are not resolved repayment",
        bootstrap=dict(draws=DRAWS, seed=BOOT_SEED, unit="paired acquisition build"),
    )
    write_json(out, "result.json", result)
    lines = [
        "# Restarted tree versus A8 (0024)",
        "",
        result["scope"],
        "",
        result["acquisition_timing"],
        "",
    ]
    for f, v in families.items():
        lines += [
            f"## {f} ({'primary' if f == 'DG' else 'descriptive; never pooled'})",
            "",
            str(v["decision"]),
            "",
            "| Contrast | Evaluation ratio (95%) | Worker-time ratio (95%) | Solve difference (95%) |",
            "|---|---|---|---|",
        ]
        for name, c in v["contrasts"].items():
            cells = [
                f"{c[m]['point']:.4g} {c[m]['interval95']}"
                for m in ("evaluations", "worker_seconds", "solve_fraction_difference")
            ]
            lines.append("| " + " | ".join([name] + cells) + " |")
        lines += [
            "",
            "Means and solve fractions: `"
            + str(v["means"])
            + "`; `"
            + str(v["solve_fractions"])
            + "`.",
            "",
            "Historical tree reference: `" + str(v["historical_full_cap_tree"]) + "`.",
            "",
            "Full per-cell metrics, attempts, geometric sensitivity, acquisition-plus-search curves in both units, repayment bounds and resolution prices are in result.json.",
            "",
        ]
        for metric, e in v["economics"].items():
            for a, c in e.items():
                lines.append(
                    f"{metric}, {a}: saving {c['savings']}; repayment {c['repayment_searches']}, 95% {c['repayment_interval95']}, unbounded={c['repayment_unbounded']}."
                )
        lines += [""]
        lines += [
            "| Cell | Arm | Solves / jobs | Mean evaluations | Mean worker seconds |",
            "|---|---|---|---|---|",
        ]
        for cell, arms in v["per_cell"].items():
            for arm, metrics in arms.items():
                lines.append(
                    f"| {cell} | {arm} | {metrics['solves']}/{metrics['jobs']} | {metrics['evaluations']['point']:.1f} | {metrics['worker_seconds']:.3f} |"
                )
        lines += [""]
    lines += [
        "Noninferiority is within three percentage points, not equal reliability. An unresolved guard does not establish inferiority. Lower capped expenditure does not imply unlimited time-to-solution or practical superiority. Return to strategy; no automatic top-up."
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    plot(out, rows, families)
