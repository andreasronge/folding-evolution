"""Fixed-cell paired build bootstrap and actual-effort economics for run 2254."""

import numpy as np
from scipy.stats import t

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.component_transfer_report import acquisition
from experiments.chem_tape.composition_run import write_json

DRAWS = 8192
BOOT_SEED = 2214000
METRIC_DEFINITIONS = {
    "phenotype_diversity": "distinct output vectors on 64 fixed training cases; lower bound on D625 phenotype diversity",
    "compile_seconds": "cached program collection; construction compilation included in variation_seconds",
    "Q": "exp(mean(log(capped tree cost) - log(capped native A8 cost))); fixed eight cells, 24 build blocks, two paired repeats; failures at two caps",
    "savings": "mean(actual tree effort - actual A8 effort); failures spend actual cap; evaluations and worker seconds separately",
    "repayment": "mean(actual native acquisition effort) / mean(actual tree effort - actual A8 effort); unbounded when savings admit zero or negative values",
    "primitive_case_work": "sum(compiled token count over evaluated individuals) times 64 training cases; execution-length proxy, excludes exact checks and internal primitive costs",
}


def classify(interval):
    lo, hi = interval
    if lo > 1.5:
        return "worthwhile_A8_advantage"
    if hi < 0.67:
        return "worthwhile_tree_advantage"
    if lo >= 0.67 and hi <= 1.5:
        return "within_margin"
    return "unresolved"


def grid(rows, family, cells, penalty=2, metric=None):
    rs = [r for r in rows if r["family"] == family]
    by = {(r["cell"], r["arm"], r["build"], r["repeat"]): r for r in rs}
    expected = {
        (c, a, b, s)
        for c in cells
        for a in ("A8", "tree")
        for b in range(24)
        for s in range(2)
    }
    expected |= {(c, "G4", None, s) for c in cells for s in range(16)}
    if len(cells) != 8 or len(by) != len(rs) or set(by) != expected:
        raise ValueError(
            "bootstrap requires complete 24-build, eight-cell, two-repeat paired grid and G4 reference"
        )
    for c in cells:
        for b in range(24):
            for s in range(2):
                if by[c, "A8", b, s]["seed"] != by[c, "tree", b, s]["seed"]:
                    raise ValueError("broken pairing")

    def cost(r):
        v = (
            r[metric]
            if metric
            else np.log(r["evaluations"] if r["solved"] else penalty * r["cap"])
        )
        if not np.isfinite(v) or (metric and v <= 0):
            raise ValueError("nonpositive/nonfinite costs")
        return v

    v = {
        a: np.array(
            [
                [[cost(by[c, a, b, s]) for s in range(2)] for c in cells]
                for b in range(24)
            ]
        )
        for a in ("A8", "tree")
    }
    g4 = np.array([[cost(by[c, "G4", None, s]) for s in range(16)] for c in cells])
    return v, g4


def samples(seed=BOOT_SEED, draws=DRAWS):
    rng = np.random.default_rng(seed)
    selected = rng.integers(24, size=(draws, 24))
    repeats = rng.integers(2, size=(draws, 24, 8, 2))
    g4_seeds = rng.integers(16, size=(draws, 8, 16))
    return selected, repeats, g4_seeds


def bootstrap(values, selected, repeats, per_cell=False):
    chosen = np.take_along_axis(values[selected], repeats, axis=3)
    return chosen.mean(axis=(1, 3) if per_cell else (1, 2, 3))


def interval(values):
    if len(values) != DRAWS or not np.all(np.isfinite(values)):
        raise ValueError("all 8192 bootstrap draws must be finite")
    return np.quantile(values, [0.025, 0.975]).tolist()


def summarize(rows, targets, penalty=2):
    selected, repeats, g4_seeds = samples()
    families = {}
    for f in sorted({r["family"] for r in rows}):
        cells = targets[f]
        v, g4 = grid(rows, f, cells, penalty)
        delta = v["tree"] - v["A8"]
        log_boot = bootstrap(delta, selected, repeats)
        q = dict(
            point=float(np.exp(delta.mean())),
            interval95=np.exp(interval(log_boot)).tolist(),
        )
        q["interval_multiplicative_width"] = q["interval95"][1] / q["interval95"][0]
        blocks = delta.mean(axis=(1, 2))
        cell_boot = bootstrap(delta, selected, repeats, per_cell=True)
        tree_boot = bootstrap(v["tree"], selected, repeats)
        g4_boot = np.take_along_axis(
            np.broadcast_to(g4, (DRAWS, 8, 16)), g4_seeds, axis=2
        ).mean(axis=(1, 2))
        families[f] = dict(
            Q=q,
            block_log_ratio_sd=float(np.std(blocks, ddof=1)),
            per_cell_Q={
                c: dict(
                    point=float(np.exp(delta[:, i].mean())),
                    interval95=np.exp(
                        np.quantile(cell_boot[:, i], [0.025, 0.975])
                    ).tolist(),
                )
                for i, c in enumerate(cells)
            },
            per_build_Q={str(b): float(np.exp(blocks[b])) for b in range(24)},
            tree_over_G4=dict(
                point=float(np.exp(v["tree"].mean() - g4.mean())),
                interval95=np.exp(interval(tree_boot - g4_boot)).tolist(),
                scope="descriptive, independent G4 seeds within fixed cells",
            ),
            costs={
                a: dict(
                    geometric_cost=float(np.exp(v[a].mean()))
                    if a != "G4"
                    else float(np.exp(g4.mean())),
                    solved=sum(
                        r["solved"] for r in rows if r["family"] == f and r["arm"] == a
                    ),
                    attempts=sum(r["family"] == f and r["arm"] == a for r in rows),
                )
                for a in ("A8", "tree", "G4")
            },
        )
    return dict(
        families=families,
        decision=classify(families["DG"]["Q"]["interval95"]),
        failure_penalty=penalty,
        reliable=True,
        bootstrap=dict(
            draws=DRAWS,
            seed=BOOT_SEED,
            blocks=24,
            cells="fixed",
            unit="build blocks; tree build labels identify independent searches, not acquired tree replicates",
            repeats="two repeats resampled jointly within each selected block x cell",
        ),
    )


def horizon_summary(acqs, saving, selected, repeats):
    point_s = float(saving.mean())
    boot_s = bootstrap(saving, selected, repeats)
    boot_a = acqs[selected].mean(axis=1)
    ci = interval(boot_s)
    ratios = np.full(DRAWS, np.inf)
    positive = boot_s > 0
    ratios[positive] = boot_a[positive] / boot_s[positive]
    # Empirical order statistics keep unbounded draws explicit without JSON Infinity.
    ordered = np.sort(ratios)
    bounds = [ordered[int(p * (DRAWS - 1))] for p in (0.025, 0.975)]
    return dict(
        mean_acquisition=float(acqs.mean()),
        mean_savings_per_search=point_s,
        savings_interval95=ci,
        repayment_searches=None if point_s <= 0 else float(acqs.mean() / point_s),
        repayment_interval95=[
            float(bounds[0]) if np.isfinite(bounds[0]) else None,
            float(bounds[1]) if ci[0] > 0 and np.isfinite(bounds[1]) else None,
        ],
        repayment_unbounded=ci[0] <= 0,
        nonpositive_savings_bootstrap_fraction=float(np.mean(~positive)),
        unbounded_endpoint_encoding="null means no finite repayment horizon",
    )


def economics(rows, saved, targets):
    selected, repeats, _ = samples()
    result = {}
    for f in sorted({r["family"] for r in rows}):
        owner = "D" if f == "DG" else "T"
        acq = [acquisition(saved, owner, b) for b in range(24)]
        result[f] = {}
        for metric, acq_key in (
            ("evaluations", "evaluations"),
            ("worker_seconds", "worker_seconds"),
        ):
            v, _ = grid(rows, f, targets[f], metric=metric)
            acquisition_values = np.array([a[acq_key] for a in acq])
            saving = v["tree"] - v["A8"]
            s = horizon_summary(acquisition_values, saving, selected, repeats)
            s["per_build"] = {
                str(b): dict(
                    acquisition=float(acquisition_values[b]),
                    native_search_mean=float(v["A8"][b].mean()),
                    tree_search_mean=float(v["tree"][b].mean()),
                    repayment_searches=None
                    if saving[b].mean() <= 0
                    else float(acquisition_values[b] / saving[b].mean()),
                    actual_native_total=float(acquisition_values[b] + v["A8"][b].sum()),
                    actual_tree_total=float(v["tree"][b].sum()),
                    horizons={
                        str(n): dict(
                            A8=float(acquisition_values[b] + n * v["A8"][b].mean()),
                            tree=float(n * v["tree"][b].mean()),
                        )
                        for n in (1, 16, 256, 4096)
                    },
                )
                for b in range(24)
            }
            s["mean_horizon_costs"] = {
                str(n): dict(
                    A8=float(acquisition_values.mean() + n * v["A8"].mean()),
                    tree=float(n * v["tree"].mean()),
                )
                for n in (1, 16, 256, 4096)
            }
            result[f][metric] = s
    return dict(
        families=result,
        scope="arithmetic actual expenditures; failures at actual cap; native pays its saved acquisition once per deployed build; GP calibration is separate development cost",
        timing_caveat="acquisition worker times are historical and search worker times contemporary; hardware/load comparability limits apply; neither is queue wall time",
    )


def resolution_price(rows, summary, saved):
    q = summary["families"]["DG"]["Q"]["point"]
    logs = np.log(list(summary["families"]["DG"]["per_build_Q"].values()))
    variance = float(np.var(logs, ddof=1))
    boundary = min((0.67, 1.5), key=lambda b: abs(np.log(q / b)))
    gap = abs(np.log(q / boundary))
    needed = next(
        (
            n
            for n in range(24, 1025)
            if gap > 0 and t.ppf(0.975, n - 1) * np.sqrt(variance / n) < gap
        ),
        None,
    )
    rs = [r for r in rows if r["arm"] in ("tree", "A8")]
    # Two seeds x eight cells per paired arm on each available roster plus fresh acquisitions.
    search_per_build = sum(r["worker_seconds"] for r in rs) / 24
    acq_per_build = np.mean(
        [
            sum(acquisition(saved, o, b)["worker_seconds"] for o in ("D", "T"))
            for b in range(24)
        ]
    )
    extra = None if needed is None else max(0, needed - 24)
    return dict(
        observed_block_variance=variance,
        nearest_boundary=boundary,
        conditional_total_blocks=needed,
        additional_blocks=extra,
        additional_worker_seconds=None
        if extra is None
        else float(extra * (search_per_build + acq_per_build)),
        projected_minutes_at10_with30percent_reserve=None
        if extra is None
        else float(1.3 * extra * (search_per_build + acq_per_build) / 600),
        caveat="conditional normal/t approximation at observed point and variance; full both-roster price provisional until TS completes; reference G4 excluded; no guarantee or automatic top-up",
    )


def diagnostics(rows):
    result = {}
    for f in sorted({r["family"] for r in rows}):
        result[f] = {}
        for a in ("A8", "tree", "G4"):
            rs = [r for r in rows if r["family"] == f and r["arm"] == a]
            d = dict(
                mean_seconds=float(np.mean([r["seconds"] for r in rs])),
                mean_worker_seconds=float(np.mean([r["worker_seconds"] for r in rs])),
                max_worker_seconds=max(r["worker_seconds"] for r in rs),
                mean_compiled_length=float(
                    np.mean([r["mean_compiled_length"] for r in rs])
                ),
                max_compiled_length=max(r["max_compiled_length"] for r in rs),
                compiled_length_histogram=np.sum(
                    [r["compiled_length_histogram"] for r in rs], axis=0
                ).tolist(),
                primitive_case_work=sum(r["primitive_case_work"] for r in rs),
                exact_check_seconds=sum(r["exact_check_seconds"] for r in rs),
                training_perfect_individuals=sum(
                    r["training_perfect_individuals"] for r in rs
                ),
                unique_shortcuts=sum(r["unique_shortcuts"] for r in rs),
                final_mean_correctness_pattern_diversity=float(
                    np.mean([r["curve"][-1][2] for r in rs])
                ),
                final_mean_output_phenotype_diversity=float(
                    np.mean([r["phenotype_diversity_curve"][-1][1] for r in rs])
                ),
            )
            if a == "tree":
                d.update(
                    initialization_attempts=sum(
                        r["initialization"]["attempts"] for r in rs
                    ),
                    initialization_rejections=sum(
                        r["initialization"]["rejected"] for r in rs
                    ),
                    operator={
                        k: sum(r["operator"][k] for r in rs) for k in rs[0]["operator"]
                    },
                    compile_seconds=sum(r["compile_seconds"] for r in rs),
                    variation_seconds=sum(r["variation_seconds"] for r in rs),
                )
            if a == "tree":
                d["operator_rejection_fractions"] = {
                    k: None
                    if d["operator"][k] == 0
                    else d["operator"]["rejected_" + k] / d["operator"][k]
                    for k in ("crossover", "mutation")
                }
            result[f][a] = d
        result[f]["per_cell"] = {
            c: {
                a: dict(
                    mean_worker_seconds=float(
                        np.mean(
                            [
                                r["worker_seconds"]
                                for r in rows
                                if r["family"] == f and r["cell"] == c and r["arm"] == a
                            ]
                        )
                    ),
                    mean_compiled_length=float(
                        np.mean(
                            [
                                r["mean_compiled_length"]
                                for r in rows
                                if r["family"] == f and r["cell"] == c and r["arm"] == a
                            ]
                        )
                    ),
                    final_mean_output_phenotype_diversity=float(
                        np.mean(
                            [
                                r["phenotype_diversity_curve"][-1][1]
                                for r in rows
                                if r["family"] == f and r["cell"] == c and r["arm"] == a
                            ]
                        )
                    ),
                )
                for a in ("A8", "tree", "G4")
            }
            for c in sorted({r["cell"] for r in rows if r["family"] == f})
        }
    return result


def plot(out, rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    families = sorted({r["family"] for r in rows})
    fig, axes = plt.subplots(
        len(families), 4, figsize=(19, 4 * len(families)), squeeze=False
    )
    for i, f in enumerate(families):
        for a in ("A8", "tree", "G4"):
            rs = [r for r in rows if r["family"] == f and r["arm"] == a]
            xs = sorted({p[0] for r in rs for p in r["curve"]} | {rs[0]["cap"]})
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
                    for x in xs
                ]
                axes[i, k - 1].plot(xs, ys, label=a)
                axes[i, k - 1].set_xscale("log")
            hist = np.sum([r["compiled_length_histogram"] for r in rs], axis=0)
            px = sorted({p[0] for r in rs for p in r["phenotype_diversity_curve"]})
            py = [
                np.mean(
                    [
                        (
                            [p for p in r["phenotype_diversity_curve"] if p[0] <= x]
                            or r["phenotype_diversity_curve"][:1]
                        )[-1][1]
                        for r in rs
                    ]
                )
                for x in px
            ]
            axes[i, 2].plot(px, py, label=a)
            axes[i, 2].set_xscale("log")
            axes[i, 3].plot(np.arange(33), hist / hist.sum(), label=a)
        for j, title in enumerate(
            (
                "best correct training cases",
                "distinct correctness patterns",
                "distinct training output vectors",
                "compiled token lengths",
            )
        ):
            axes[i, j].set_title(f + ": " + title)
            axes[i, j].set_xlabel("evaluations" if j < 3 else "tokens")
            axes[i, j].legend()
    fig.tight_layout()
    fig.savefig(out / "dynamics.png", dpi=130)
    plt.close(fig)


def report(out, rows, saved, prep, timing):
    rows = sorted(
        rows,
        key=lambda r: str(
            (
                r["family"],
                r["cell"],
                r["arm"],
                r.get("build"),
                r["repeat"],
                r.get("crossover"),
            )
        ),
    )
    targets = prep["freeze"]["targets"]
    two, one = summarize(rows, targets), summarize(rows, targets, penalty=1)
    result = dict(
        status="complete"
        if {r["family"] for r in rows} == {"DG", "TS"}
        else "DG_complete_TS_pending",
        summary=two,
        one_cap=one,
        penalty_sensitive=two["decision"] != one["decision"],
        economics=economics(rows, saved, targets),
        resolution_price=resolution_price(rows, two, saved),
        diagnostics=diagnostics(rows),
        timing=timing,
        preparation=prep,
        development_cost=dict(
            actual_calibration_evaluations=prep["calibration_actual_evaluations"],
            actual_calibration_worker_seconds=sum(
                prep["batches"][f]["worker_seconds"] for f in ("DG", "TS")
            ),
        ),
        search_rows_hash=digest(rows),
        metric_definitions=METRIC_DEFINITIONS,
        next="strategy",
        scope="fixed DG/TS development rosters, v2_x4, 32 tokens, P256, cap524288; complete procedures; no causal learning, strong-typing or fresh-bank transfer claim",
    )
    write_json(out, "result.json", result)
    lines = [
        "# Frozen A8 versus subtree GP",
        "",
        result["status"],
        "",
        "DG decision: " + two["decision"] + ". Return to strategy.",
        "",
        "|Family|Tree / native A8 Q|95% paired block interval|A8 solves|Tree solves|G4 solves|",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for f, s in two["families"].items():
        q, c = s["Q"], s["costs"]
        lines.append(
            f"|{f}|{q['point']:.3f}|[{q['interval95'][0]:.3f}, {q['interval95'][1]:.3f}]|"
            + "|".join(
                f"{c[a]['solved']}/{c[a]['attempts']}" for a in ("A8", "tree", "G4")
            )
            + "|"
        )
    lines += [
        "",
        result["scope"],
        "",
        "Search-cost verdict and arithmetic repayment are independent. Within-margin intervals do not establish equality. "
        "Null repayment endpoints mean unbounded horizons; historical acquisition seconds have hardware/load limits.",
        "",
        "Inspect per-cell/per-seed solvers, shortcuts, paired cases, expression lengths, rejection and diversity diagnostics "
        "before interpreting too-clean solving or an advantage over a weak tree arm. No outcome-driven tuning or top-up.",
        "",
        "Per-cell Q, 1-cap sensitivity, tree/G4, block variance, repayment, development cost and conditional resolution price: result.json.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    plot(out, rows)
