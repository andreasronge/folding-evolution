"""Fixed paired-block inference and acquisition economics for 1019."""

from collections import Counter
import math

import numpy as np

from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.tree_library_report import estimate
from experiments.chem_tape.tree_source_report import grid, acquisition
from experiments.chem_tape.tree_hand_run import ARMS, seed
from experiments.chem_tape.tree_uniform_run import score_cells
from experiments.chem_tape import gate_sum_bank

DRAWS = 8192
CONTRASTS = (("R-hand", "R-TS"), ("R-hand", "R-tree"), ("R-TS", "R-tree"))


def classify(primary, baseline, guard):
    if primary[1] < 1.25 and baseline[1] < 0.80 and guard[0] > -0.03:
        return "retained"
    if primary[0] > 1.25:
        return "learned_increment"
    return "unresolved"


def contrasts(values, selected):
    out = {}
    for a, b in CONTRASTS:
        av, bv = values[a], values[b]
        out[a + "/" + b] = estimate(
            av.mean() / bv.mean(), av[selected].mean(1) / bv[selected].mean(1)
        )
    return out


def library_audit(libs):
    def audit(entries):
        counts = Counter(tuple(e["prefix"]) for e in entries)
        return dict(
            entries=len(entries),
            distinct=len(counts),
            forms=[
                dict(prefix=list(p), copies=n, draw_mass=n / len(entries), nodes=len(p))
                for p, n in sorted(counts.items())
            ],
            root_counts=dict(Counter(str(e["prefix"][0]) for e in entries)),
            size_counts=dict(Counter(str(e["nodes"]) for e in entries)),
            pair_draw_mass=sum(
                n
                for p, n in counts.items()
                if len(p) == 3 and p[0] == 9 and all(x < 4 for x in p[1:])
            )
            / len(entries)
            if entries
            else 0,
        )

    return dict(
        hand=audit(libs["hand"]),
        TS=[
            dict(
                build=lib["build"],
                audit=audit(lib["entries"]),
                common_distinct_with_hand=len(
                    set(tuple(e["prefix"]) for e in lib["entries"])
                    & set(tuple(e["prefix"]) for e in libs["hand"])
                ),
            )
            for lib in libs["TS"]
        ],
    )


def summarize(rows, libs, gs, preparation):
    cells = score_cells(gs)
    if len(rows) != 5184 or {r["family"] for r in rows} != {"GS"}:
        raise ValueError("requires all 5,184 GS scoring jobs")
    rng = np.random.default_rng(seed("bootstrap"))
    selected = rng.integers(24, size=(DRAWS, 24))
    arrays = {
        m: grid(rows, cells, 6, ARMS, m)
        for m in ("evaluations", "worker_seconds", "solved")
    }
    blocks = {
        m: {a: x.mean((1, 2)) for a, x in vals.items()} for m, vals in arrays.items()
    }
    comparisons = {
        m: contrasts(vals, selected) for m, vals in blocks.items() if m != "solved"
    }
    solve_diffs = {
        a + "-" + b: estimate(
            (blocks["solved"][a] - blocks["solved"][b]).mean(),
            (blocks["solved"][a] - blocks["solved"][b])[selected].mean(1),
        )
        for a, b in CONTRASTS
    }
    decision = classify(
        comparisons["evaluations"]["R-hand/R-TS"]["interval95"],
        comparisons["evaluations"]["R-hand/R-tree"]["interval95"],
        solve_diffs["R-hand-R-tree"]["interval95"],
    )
    diagnostics = {}
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]
        attempts = [p for r in rs for p in r["attempts"]]
        op = Counter()
        for p in attempts:
            op.update(p["operator"])
        class_counts = {
            g: {
                k: sum(
                    p.get("donor_classes", {}).get(g, {}).get(k, 0) for p in attempts
                )
                for k in ("draws", "insertions", "oversize")
            }
            for g in ("P", "K")
        }
        for v in class_counts.values():
            v.update(
                insertion_rate=v["insertions"] / v["draws"] if v["draws"] else None,
                oversize_rate=v["oversize"] / v["draws"] if v["draws"] else None,
            )
        diagnostics[a] = dict(
            jobs=len(rs),
            solves=sum(r["solved"] for r in rs),
            first_attempt_solves=sum(
                r["solved"] and r["attempt_count"] == 1 for r in rs
            ),
            capped_failures=sum(not r["solved"] for r in rs),
            operator=dict(op),
            donor_classes=class_counts,
            insertion_rate=op["library_insertions"] / op["library_draws"]
            if op["library_draws"]
            else None,
            oversize_rate=op["rejected_library"] / op["library_draws"]
            if op["library_draws"]
            else None,
            attempt_histogram=dict(Counter(str(r["attempt_count"]) for r in rs)),
            mean_evaluations=float(blocks["evaluations"][a].mean()),
            mean_worker_seconds=float(blocks["worker_seconds"][a].mean()),
        )
    subsets = {c: [i] for i, c in enumerate(cells)}
    by = {c["id"]: c for c in gs["screen"]["cells"]}
    # Fixed bank pairing groups B/C, without choosing groups from observed scores.
    for group in sorted({str(gate_sum_bank.pairing(by[c])) for c in cells}):
        subsets["split:" + group] = [
            i for i, c in enumerate(cells) if str(gate_sum_bank.pairing(by[c])) == group
        ]
    subset_results = {
        name: dict(
            evaluations=contrasts(
                {a: arrays["evaluations"][a][:, ix, :].mean((1, 2)) for a in ARMS},
                selected,
            ),
            worker_seconds=contrasts(
                {a: arrays["worker_seconds"][a][:, ix, :].mean((1, 2)) for a in ARMS},
                selected,
            ),
        )
        for name, ix in subsets.items()
    }
    per_build = []
    for b in range(24):
        picks = rng.integers(6, size=(DRAWS, len(cells), 6))
        ts, hand = arrays["evaluations"]["R-TS"][b], arrays["evaluations"]["R-hand"][b]
        ts_samples = ts[np.arange(len(cells))[None, :, None], picks].mean((1, 2))
        hand_samples = hand[np.arange(len(cells))[None, :, None], picks].mean((1, 2))
        per_build.append(
            dict(
                build=b,
                TS_over_hand=estimate(
                    ts.mean() / hand.mean(), ts_samples / hand_samples
                ),
                learned_beats_hand=bool(ts.mean() < hand.mean()),
                interval_scope="Paired repeat resampling within each fixed cell; conditional on this build, six repeats.",
            )
        )
    sensitivity = {}
    for a, b in CONTRASTS:
        mask = arrays["solved"][a].astype(bool) & arrays["solved"][b].astype(bool)
        sensitivity[a + "/" + b] = dict(
            both_solved_jobs=int(mask.sum()),
            both_solved_ratio=float(
                arrays["evaluations"][a][mask].mean()
                / arrays["evaluations"][b][mask].mean()
            )
            if mask.any()
            else None,
            caveat="Both-solved subset conditions on outcomes; descriptive only.",
            failure_charge_ratios={
                str(cap): contrasts(
                    {
                        arm: np.where(
                            arrays["solved"][arm], arrays["evaluations"][arm], cap
                        ).mean((1, 2))
                        for arm in ARMS
                    },
                    selected,
                )[a + "/" + b]
                for cap in (262144, 524288, 1048576)
            },
        )
    economics = {}
    for metric in ("evaluations", "worker_seconds"):
        acq = acquisition({"TS": libs["TS"]}, "TS", metric)
        econ = {}
        for comparator in ("R-tree", "R-hand"):
            learned, baseline = blocks[metric]["R-TS"], blocks[metric][comparator]
            acqs = acq[selected].mean(1)
            ls, bs = learned[selected].mean(1), baseline[selected].mean(1)
            saving = bs - ls
            finite = saving > 0
            point_saving = baseline.mean() - learned.mean()
            econ["R-TS/" + comparator] = dict(
                acquisition=estimate(acq.mean(), acqs),
                searches_to_repay=float(acq.mean() / point_saving)
                if point_saving > 0
                else None,
                bootstrap_positive_saving_fraction=float(finite.mean()),
                conditional_repayment_interval95=np.quantile(
                    acqs[finite] / saving[finite], [0.025, 0.975]
                ).tolist()
                if finite.any()
                else None,
                horizons={
                    str(n): dict(
                        total_ratio=estimate(
                            (acq.mean() + n * learned.mean()) / (n * baseline.mean()),
                            (acqs + n * ls) / (n * bs),
                        ),
                        total_difference=estimate(
                            acq.mean() + n * (learned.mean() - baseline.mean()),
                            acqs + n * (ls - bs),
                        ),
                    )
                    for n in range(1, 201)
                },
            )
        econ["R-hand/R-tree"] = {
            "horizons": {
                str(n): dict(total_ratio=comparisons[metric]["R-hand/R-tree"])
                for n in range(1, 201)
            }
        }
        economics[metric] = econ
    prices = {}
    for a, b, threshold in (("R-hand", "R-TS", 1.25), ("R-hand", "R-tree", 0.80)):
        av, bv = blocks["evaluations"][a], blocks["evaluations"][b]
        gap = abs(math.log(av.mean() / bv.mean() / threshold))
        variance = float(np.var(av / av.mean() - bv / bv.mean(), ddof=1))
        n = None if gap == 0 else max(24, math.ceil(1.959964**2 * variance / gap**2))
        extra = None if n is None else max(0, n - 24)
        prices[a + "/" + b] = dict(
            conditional_total_slots=n,
            additional_slots=extra,
            additional_jobs=None if extra is None else extra * 12 * 6 * 3,
            additional_worker_seconds=None
            if extra is None
            else extra * sum(r["worker_seconds"] for r in rows) / 24,
            additional_TS_acquisition_worker_seconds=None
            if extra is None
            else extra
            * float(acquisition({"TS": libs["TS"]}, "TS", "worker_seconds").mean()),
            additional_TS_acquisition_evaluations=None
            if extra is None
            else extra
            * float(acquisition({"TS": libs["TS"]}, "TS", "evaluations").mean()),
            caveat="Observed-effect paired variance approximation; no guarantee or automatic extension. Extra complete slots require TS acquisitions; worker-time cost uses historical acquisition rates.",
        )
    difference = blocks["solved"]["R-hand"] - blocks["solved"]["R-tree"]
    gap = float(difference.mean() + 0.03)
    variance = float(np.var(difference, ddof=1))
    needed = None if gap <= 0 else max(24, math.ceil(1.959964**2 * variance / gap**2))
    prices["reliability_guard"] = dict(
        conditional_total_slots=needed,
        additional_slots=None if needed is None else max(0, needed - 24),
        caveat="Observed Bernoulli block variance; all-success zero variance is not guaranteed future reliability; gap <=0 has no finite projected price under this effect.",
    )
    return dict(
        decision=decision,
        comparisons=comparisons,
        solve_differences=solve_diffs,
        diagnostics=diagnostics,
        subsets=subset_results,
        per_build=per_build,
        failure_sensitivity=sensitivity,
        economics=economics,
        resolution_prices=prices,
        library_audit=library_audit(libs),
        bootstrap=dict(
            draws=DRAWS,
            seed=seed("bootstrap"),
            unit="24 paired build/seed slots; fixed cells and six repeats; TS acquisition jointly resampled",
        ),
        scope="Fixed development-informed sum prior, source-free at execution; substitution on B/C only. Outcomes do not isolate donor ingredients or generalize to a fresh bank.",
        hand_overhead=preparation["hand_overhead"],
        economics_scope="TS includes measured historical acquisition failures, extraction and verification; hand has zero acquisition evaluations. Hand constructor/validation overhead reported separately, not repeated per search. Worker-time acquisition was measured on the historical host/load.",
    )


def plot(out, rows, result):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xs = np.array([256, 4096, 16384, 65536, 131072, 262144, 524288])
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]
        axes[0].plot(
            xs,
            [np.mean([r["solved"] and r["evaluations"] <= x for r in rs]) for x in xs],
            label=a,
        )
        for ax, field in zip(axes[1:], ("curve", "phenotype_diversity_curve")):
            lines = []
            for r in rs:
                line, offset = [], 0
                for p in r["attempts"]:
                    line.extend((offset + v[0], v[1]) for v in p[field])
                    offset += p["evaluations"]
                lines.append(line)
            ax.plot(
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
        axes,
        ("Exact solve fraction", "Training best (restarts reset)", "Output diversity"),
    ):
        ax.set_title(title)
        ax.set_xscale("log")
        ax.set_xlabel("Evaluations")
        ax.legend()
    fig.tight_layout()
    fig.savefig(out / "dynamics.png", dpi=130)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, metric in zip(axes, ("evaluations", "worker_seconds")):
        for name, e in result["economics"][metric].items():
            vals = [e["horizons"][str(n)]["total_ratio"] for n in range(1, 201)]
            ax.plot(range(1, 201), [v["point"] for v in vals], label=name)
            ax.fill_between(
                range(1, 201),
                [v["interval95"][0] for v in vals],
                [v["interval95"][1] for v in vals],
                alpha=0.15,
            )
        ax.axhline(1, color="black", linewidth=0.7)
        ax.set_title(metric)
        ax.set_xlabel("Searches")
        ax.set_ylabel("Acquisition + search / comparator")
        ax.legend()
    fig.tight_layout()
    fig.savefig(out / "economics.png", dpi=130)
    plt.close(fig)


def report(out, rows, libs, gs, preparation, batches):
    result = summarize(rows, libs, gs, preparation)
    write_json(out, "result.json", result)
    plot(out, rows, result)
    lines = [
        "# Fixed sum-donor prior versus TS libraries",
        "",
        "Decision: **" + result["decision"] + "**; return to strategy.",
        "",
        result["scope"],
        "",
        "| Contrast | Evaluations ratio (95% interval) | Worker-seconds ratio (95% interval) |",
        "|---|---|---|",
    ]

    def fmt(v):
        return f"{v['point']:.4f} [{v['interval95'][0]:.4f}, {v['interval95'][1]:.4f}]"

    for name in result["comparisons"]["evaluations"]:
        lines.append(
            f"| {name} | {fmt(result['comparisons']['evaluations'][name])} | {fmt(result['comparisons']['worker_seconds'][name])} |"
        )
    lines.extend(
        [
            "",
            "Solve differences: " + json_text(result["solve_differences"]),
            "",
            result["economics_scope"],
            "",
            "Full per-cell/split/build intervals, diagnostics, prior audit, failure sensitivity, resolution prices and 1–200 search cost curves: `result.json`. Raw search curves: `search.jsonl`. Hand overhead: "
            + json_text(result["hand_overhead"]),
            "",
            "Retention is substitution within the 1.25 margin; it permits a smaller learned advantage at longer horizons. A loss rejects this prior only; ingredient explanations remain hypotheses. Unresolved results do not imply equality or authorize more seeds.",
        ]
    )
    (out / "report.md").write_text("\n".join(lines) + "\n")


def json_text(value):
    import json

    return json.dumps(value, sort_keys=True)
