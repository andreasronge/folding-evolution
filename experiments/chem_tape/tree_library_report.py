"""0150: acquisition-block inference and measured library acquisition economics."""

import numpy as np
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json

ARMS = ("R-tree", "R-lib", "R-size")
DRAWS = 8192
SEED = 32000200


def estimate(point, samples):
    if not np.all(np.isfinite(samples)):
        raise ValueError("nonfinite bootstrap")
    return dict(
        point=float(point), interval95=np.quantile(samples, [0.025, 0.975]).tolist()
    )


def classify(b, c, d):
    if d[0] <= -0.03:
        return "reliability_inferior" if d[1] < -0.03 else "reliability_unresolved"
    if b[1] < 0.90 and c[1] < 1:
        return "useful_search_content_increment_consider_fresh_bank"
    if c[0] > 1:
        return (
            "baseline_gain_random_control_better"
            if b[1] < 0.90
            else "learned_content_loses_to_size_control"
        )
    if b[1] < 0.90:
        return "baseline_gain_content_increment_unresolved"
    if b[0] > 0.85:
        return "end_saving_above_15pct_excluded"
    return "unresolved_return_to_strategy"


def grid(rows, cells, metric, repeats=8, expected_cells=8):
    by = {(r["build"], r["cell"], r["repeat"], r["arm"]): r for r in rows}
    expected = {
        (b, c, r, a)
        for b in range(24)
        for c in cells
        for r in range(repeats)
        for a in ARMS
    }
    if len(cells) != expected_cells or len(by) != len(rows) or set(by) != expected:
        raise ValueError(
            f"requires complete 24-acquisition x {expected_cells}-cell x {repeats}-repeat x 3-arm grid"
        )
    for b in range(24):
        for c in cells:
            for r in range(repeats):
                if len({tuple(by[b, c, r, a]["seeds"]) for a in ARMS}) != 1:
                    raise ValueError("attempt seed pairing mismatch")
    return {
        a: np.array(
            [
                [[float(by[b, c, r, a][metric]) for r in range(repeats)] for c in cells]
                for b in range(24)
            ]
        )
        for a in ARMS
    }


def coverage(bank, targets):
    by = {c["id"]: c for c in bank["screen"]["cells"]}

    def pair(c):
        return tuple(sorted(tuple(sorted(p)) for p in by[c]["pairing"]))

    covered = {pair(c) for c in bank["split"]["source"]}
    return {c: pair(c) in covered for c in targets}


def summarize(
    rows,
    libraries,
    bank,
    targets,
    *,
    repeats=8,
    expected_cells=8,
    seed=SEED,
    horizons=(1, 16, 64, 160, 320, 1024, 4096),
    coverage_flags=None,
    groups=None,
    decision_fn=classify,
):
    selected = np.random.default_rng(seed).integers(24, size=(DRAWS, 24))
    costs = {
        m: grid(rows, targets, m, repeats, expected_cells)
        for m in ("evaluations", "worker_seconds")
    }
    solves = grid(rows, targets, "solved", repeats, expected_cells)
    blocks = {
        m: {a: v.mean(axis=(1, 2)) for a, v in arrays.items()}
        for m, arrays in costs.items()
    }
    solve_blocks = {a: v.mean(axis=(1, 2)) for a, v in solves.items()}
    contrasts = {}
    prices = {}
    total_per_build = sum(v.sum(axis=(1, 2)) for v in costs["worker_seconds"].values())
    acquisition_seconds = np.array(
        [
            library["acquisition_worker_seconds"]
            + library["extraction_seconds"]
            + library["control_seconds"]
            + library["verification_seconds"]
            for library in libraries
        ]
    )
    for denominator, threshold in [("R-tree", 0.90), ("R-size", 1.0)]:
        name = "R-lib/" + denominator
        contrasts[name] = {}
        for m, v in blocks.items():
            contrasts[name][m] = estimate(
                v["R-lib"].mean() / v[denominator].mean(),
                v["R-lib"][selected].mean(axis=1)
                / v[denominator][selected].mean(axis=1),
            )
        d = solve_blocks["R-lib"] - solve_blocks[denominator]
        contrasts[name]["solve_fraction_difference"] = estimate(
            d.mean(), d[selected].mean(axis=1)
        )
        a, b = blocks["evaluations"]["R-lib"], blocks["evaluations"][denominator]
        ratio = a.mean() / b.mean()
        influence = (a - ratio * b) / b.mean()
        gap = abs(ratio - threshold)
        needed = (
            None
            if gap == 0
            else int(np.ceil(1.959963984540054**2 * np.var(influence, ddof=1) / gap**2))
        )
        extra = None if needed is None else max(0, needed - 24)
        prices[name] = dict(
            routing_threshold=threshold,
            conditional_total_acquisitions=needed,
            additional_acquisitions=extra,
            additional_jobs=None
            if extra is None
            else extra * (32 + len(targets) * repeats * 3),
            additional_worker_seconds=None
            if extra is None
            else float(extra * (total_per_build + acquisition_seconds).mean()),
            realised_relative_interval_half_width=(
                contrasts[name]["evaluations"]["interval95"][1]
                - contrasts[name]["evaluations"]["interval95"][0]
            )
            / (2 * ratio),
            caveat="normal approximation at observed acquisition variance and effect; all three arms and acquisition charged; no guaranteed precision or automatic top-up",
        )
    economics = {}
    for metric, v in blocks.items():
        economics[metric] = {}
        for a in ("R-lib", "R-size"):
            acq = np.array(
                [
                    library["acquisition_evaluations"]
                    if metric == "evaluations"
                    else library["acquisition_worker_seconds"]
                    + library["extraction_seconds"]
                    + library["verification_seconds"]
                    + (library["control_seconds"] if a == "R-size" else 0)
                    for library in libraries
                ]
            )
            saving = v["R-tree"] - v[a]
            acq_boot = acq[selected].mean(axis=1)
            saving_boot = saving[selected].mean(axis=1)
            rate = saving_boot / acq_boot
            low, high = np.quantile(rate, [0.025, 0.975])
            economics[metric][a] = dict(
                acquisition=estimate(acq.mean(), acq_boot),
                savings=estimate(saving.mean(), saving_boot),
                repayment_searches=None
                if saving.mean() <= 0
                else float(acq.mean() / saving.mean()),
                repayment_interval95=[
                    None if high <= 0 else float(1 / high),
                    None if low <= 0 else float(1 / low),
                ],
                repayment_unbounded=bool(low <= 0),
                per_build=[
                    dict(
                        build=b,
                        acquisition=float(acq[b]),
                        saving=float(saving[b]),
                        repayment_searches=None
                        if saving[b] <= 0
                        else float(acq[b] / saving[b]),
                    )
                    for b in range(24)
                ],
                horizons={
                    str(n): {
                        arm: estimate(values.mean(), values[selected].mean(axis=1))
                        for arm, values in [
                            ("R-tree", n * v["R-tree"]),
                            (a, acq + n * v[a]),
                        ]
                    }
                    for n in horizons
                },
            )
    flags = coverage(bank, targets) if coverage_flags is None else coverage_flags
    per_cell = {}
    for ci, cell in enumerate(targets):
        per_cell[cell] = dict(source_pair_split_covered=flags[cell], arms={}, ratios={})
        for a in ARMS:
            rs = [r for r in rows if r["cell"] == cell and r["arm"] == a]
            per_cell[cell]["arms"][a] = dict(
                jobs=len(rs),
                solves=sum(r["solved"] for r in rs),
                evaluations=float(costs["evaluations"][a][:, ci, :].mean()),
                worker_seconds=float(costs["worker_seconds"][a][:, ci, :].mean()),
            )
        for denom in ("R-tree", "R-size"):
            num = costs["evaluations"]["R-lib"][:, ci, :].mean(axis=1)
            den = costs["evaluations"][denom][:, ci, :].mean(axis=1)
            per_cell[cell]["ratios"]["R-lib/" + denom] = estimate(
                num.mean() / den.mean(),
                num[selected].mean(axis=1) / den[selected].mean(axis=1),
            )
    split = {}
    if groups is None:
        groups = {
            "covered" if covered else "uncovered": [
                i for i, c in enumerate(targets) if flags[c] == covered
            ]
            for covered in (True, False)
        }
    for group, indices in groups.items():
        split[group] = dict(cells=[targets[i] for i in indices], ratios={})
        for denom in ("R-tree", "R-size"):
            num = costs["evaluations"]["R-lib"][:, indices, :].mean(axis=(1, 2))
            den = costs["evaluations"][denom][:, indices, :].mean(axis=(1, 2))
            split[group]["ratios"]["R-lib/" + denom] = estimate(
                num.mean() / den.mean(),
                num[selected].mean(axis=1) / den[selected].mean(axis=1),
            )
    diagnostics = {}
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]
        attempts = [p for r in rs for p in r["attempts"]]
        operators = {
            k: sum(p["operator"].get(k, 0) for p in attempts)
            for k in sorted({k for p in attempts for k in p["operator"]})
        }
        shortcuts = sum(p["shortcuts"] for p in attempts)
        perfect = sum(p["training_perfect_individuals"] for p in attempts)
        diagnostics[a] = dict(
            operator=operators,
            training_perfect_not_exact_evaluation_share=shortcuts
            / sum(r["evaluations"] for r in rs),
            training_perfect_not_exact_among_perfect=None
            if not perfect
            else shortcuts / perfect,
            mean_attempts=float(np.mean([r["attempt_count"] for r in rs])),
            attempt_histogram={
                str(k): sum(r["attempt_count"] == k for r in rs) for k in range(1, 9)
            },
        )
    b = contrasts["R-lib/R-tree"]
    c = contrasts["R-lib/R-size"]
    return dict(
        means={
            m: {a: float(v.mean()) for a, v in arms.items()}
            for m, arms in blocks.items()
        },
        solve_fractions={a: float(v.mean()) for a, v in solve_blocks.items()},
        contrasts=contrasts,
        decision=decision_fn(
            b["evaluations"]["interval95"],
            c["evaluations"]["interval95"],
            b["solve_fraction_difference"]["interval95"],
        ),
        content_contrast_status=(
            "resolved_loss_to_size_control"
            if c["evaluations"]["interval95"][0] > 1
            else "resolved_increment_over_size_control"
            if c["evaluations"]["interval95"][1] < 1
            else "unresolved_content_increment"
        ),
        resolution_price=prices,
        economics=economics,
        per_cell=per_cell,
        pair_split=split,
        diagnostics=diagnostics,
        acquisition_spread=[
            {
                k: library[k]
                for k in (
                    "build",
                    "source_solves",
                    "acquisition_evaluations",
                    "acquisition_worker_seconds",
                    "extraction_seconds",
                    "control_seconds",
                    "verification_seconds",
                )
            }
            | dict(
                library_size=len(library["entries"]),
                entry_size_pairs=[
                    [e["nodes"], e["compiled_length"]] for e in library["entries"]
                ],
                control_draws=[e["draws"] for e in library["controls"]],
            )
            for library in libraries
        ],
    )


def plot(out, rows, result):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 4, figsize=(18, 4))
    xs = np.array([256, 4096, 16384, 65536, 131072, 262144, 524288])
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]
        axes[0].plot(
            xs,
            [np.mean([r["solved"] and r["evaluations"] <= x for r in rs]) for x in xs],
            label=a,
        )
        for panel, field in [(1, "curve"), (2, "phenotype_diversity_curve")]:
            timelines = []
            for r in rs:
                line = []
                offset = 0
                for p in r["attempts"]:
                    line.extend((offset + point[0], point[1]) for point in p[field])
                    offset += p["evaluations"]
                timelines.append(line)
            axes[panel].plot(
                xs,
                [
                    np.mean(
                        [
                            ([v for t, v in line if t <= x] or [line[0][1]])[-1]
                            for line in timelines
                        ]
                    )
                    for x in xs
                ],
                label=a,
            )
        axes[3].plot(
            range(1, 9),
            [sum(r["attempt_count"] == k for r in rs) / len(rs) for k in range(1, 9)],
            label=a,
        )
    for i, title in enumerate(
        [
            "D625 solves by expenditure",
            "Training best score (restart resets)",
            "Training output diversity",
            "Attempts per job",
        ]
    ):
        axes[i].set_title(title)
        axes[i].legend()
        if i < 3:
            axes[i].set_xscale("log")
            axes[i].set_xlabel("Evaluations")
    fig.tight_layout()
    fig.savefig(out / "dynamics.png", dpi=130)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for panel, metric in zip(axes, ("evaluations", "worker_seconds")):
        econ = result["economics"][metric]
        for a in ARMS:
            horizons = econ["R-lib" if a == "R-tree" else a]["horizons"]
            ns = sorted(map(int, horizons))
            vals = [horizons[str(n)][a] for n in ns]
            panel.plot(ns, [v["point"] for v in vals], label=a)
            panel.fill_between(
                ns,
                [v["interval95"][0] for v in vals],
                [v["interval95"][1] for v in vals],
                alpha=0.15,
            )
        panel.set_xscale("log")
        panel.set_yscale("log")
        panel.set_title("Acquisition + N searches: " + metric)
        panel.set_xlabel("Searches per library")
        panel.legend()
    fig.tight_layout()
    fig.savefig(out / "economics.png", dpi=130)
    plt.close(fig)


def report(out, rows, libraries, bank, targets, preparation, timing):
    result = summarize(rows, libraries, bank, targets)
    result.update(
        rows_hash=digest(rows),
        preparation_hash=preparation["preparation_hash"],
        timing=timing,
        bootstrap=dict(
            draws=DRAWS,
            seed=SEED,
            unit="24 independent acquisitions; paired across arms, fixed cells/repeats retained",
        ),
        scope="DG development bank, frozen extractor/rate/restart policy; no fresh-bank transfer or causal separation of token frequencies/dependencies",
        economics_scope="measured acquisition, extraction and shared semantic-validation gate; size-control construction charged to R-size; wall timings depend on sustained ten-worker load",
    )
    write_json(out, "result.json", result)
    lines = [
        "# Frozen source-subtree donors (0150)",
        "",
        result["scope"],
        "",
        result["decision"],
        "",
        "| Contrast | Evaluation ratio (95%) | Worker-second ratio (95%) | Solve difference (95%) |",
        "|---|---|---|---|",
    ]
    for name, v in result["contrasts"].items():
        lines.append(
            "| "
            + " | ".join(
                [name]
                + [
                    f"{v[m]['point']:.4g} {v[m]['interval95']}"
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
        "Means: " + str(result["means"]),
        "",
        "Solve fractions: " + str(result["solve_fractions"]),
        "",
        "Acquisition spread, resolution prices for both contrasts, operator/fallback counts, shortcuts, per-cell and coverage intervals are in result.json. No automatic top-up.",
        "",
        "Frozen metadata yields "
        + str(sum(coverage(bank, targets).values()))
        + " covered cells; remaining cells are uncovered (proposal 5/3 was a roster counting error).",
        "",
    ]
    for metric, arms in result["economics"].items():
        for a, v in arms.items():
            lines.append(
                f"{metric} {a}: acquisition {v['acquisition']}; saving {v['savings']}; repayment {v['repayment_searches']}, 95% {v['repayment_interval95']} (unbounded={v['repayment_unbounded']})."
            )
    lines += [
        "",
        "A search-only useful result recommends consideration of transfer; economic usefulness needs positive savings and enough reuse. Noninferiority is one-sided, not equivalence. An unresolved control contrast does not establish a size explanation. Return to strategy.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    plot(out, rows, result)
