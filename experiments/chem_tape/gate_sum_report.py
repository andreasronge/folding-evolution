"""0348 protected-cell search transfer, jointly charged frozen acquisition."""

import numpy as np

from experiments.chem_tape import tree_library_report as base
from experiments.chem_tape.gate_sum_bank import pairing
from experiments.chem_tape.gate_sum_run import BOOTSTRAP_SEED
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json

HORIZONS = (1, 10, 50, 100, 500, 1000)


def classify(ratio, control, guard):
    if ratio[0] > 1:
        return "harm_end_route_expansion"
    if ratio[1] < 0.90:
        if guard[0] > -0.03:
            return "search_cost_transfers_return_to_strategy"
        return (
            "reliability_inferior"
            if guard[1] < -0.03
            else "reliability_unresolved_price_resolution"
        )
    if ratio[0] > 0.85:
        return "small_or_none_end_route_expansion"
    return "unresolved_price_resolution_return_to_strategy"


def summarize(rows, libraries, bank, targets):
    by = {c["id"]: c for c in bank["screen"]["cells"]}
    learned = ((0, 1), (2, 3))
    flags = {c: pairing(by[c]) == learned for c in targets}
    groups = {
        str(p): [i for i, c in enumerate(targets) if pairing(by[c]) == p]
        for p in sorted({pairing(by[c]) for c in targets})
    }
    result = base.summarize(
        rows,
        libraries,
        bank,
        targets,
        repeats=4,
        expected_cells=18,
        seed=BOOTSTRAP_SEED,
        horizons=HORIZONS,
        coverage_flags=flags,
        groups=groups,
        decision_fn=classify,
    )
    result["solve_counts"] = {
        a: sum(r["solved"] for r in rows if r["arm"] == a) for a in base.ARMS
    }
    # Separate attempt-of-solve from attempts spent on an unsolved capped job.
    for a in base.ARMS:
        rs = [r for r in rows if r["arm"] == a]
        result["diagnostics"][a]["attempt_of_solve"] = {
            str(k): sum(r["solved"] and r["attempt_count"] == k for r in rs)
            for k in range(1, 9)
        }
        result["diagnostics"][a]["failed_jobs"] = sum(not r["solved"] for r in rs)
    for group, value in result["pair_split"].items():
        cells = value["cells"]
        value["learned_predicate_split"] = all(flags[c] for c in cells)
        value["solve_counts"] = {
            a: sum(r["solved"] for r in rows if r["arm"] == a and r["cell"] in cells)
            for a in base.ARMS
        }
    # Price guard resolution as well as ratio resolution: a speed gain with an
    # unresolved reliability guard is not called useful transfer.
    solved = base.grid(rows, targets, "solved", repeats=4, expected_cells=18)
    d = (solved["R-lib"] - solved["R-tree"]).mean(axis=(1, 2))
    gap = d.mean() + 0.03
    needed = (
        None
        if gap <= 0
        else int(np.ceil(1.959963984540054**2 * np.var(d, ddof=1) / gap**2))
    )
    extra = None if needed is None else max(0, needed - 24)
    cost = np.array(
        [
            sum(r["worker_seconds"] for r in rows if r["build"] == b)
            + libraries[b]["acquisition_worker_seconds"]
            + libraries[b]["extraction_seconds"]
            + libraries[b]["verification_seconds"]
            + libraries[b]["control_seconds"]
            for b in range(24)
        ]
    )
    result["resolution_price"]["reliability_guard"] = dict(
        conditional_total_acquisitions=needed,
        additional_acquisitions=extra,
        additional_jobs=None if extra is None else extra * (32 + 18 * 4 * 3),
        additional_worker_seconds=None if extra is None else float(extra * cost.mean()),
        caveat="normal approximation at observed build variance/effect; full acquisition and grid charged; no automatic top-up or guaranteed resolution",
    )
    return result


def report(out, rows, libraries, bank, targets, preparation, timing):
    result = summarize(rows, libraries, bank, targets)
    result.update(
        rows_hash=digest(rows),
        preparation_hash=preparation["preparation_hash"],
        timing=timing,
        bootstrap=dict(
            draws=base.DRAWS,
            seed=BOOTSTRAP_SEED,
            unit="24 acquisitions jointly resampled with original costs; paired arms; 18 fixed cells equally weighted, four repeats",
        ),
        scope="Protected-cell confirmation within a deliberately selected new gate-sum shape made of familiar parts. Two cells probed before freeze, excluded from protection. Frozen external fitting, no inherited adaptation, broad task transfer or identified modularity.",
        economics_scope="Original per-build acquisition including failed attempts, extraction and validation; R-size additionally charged original random-control construction. Reconstruction is validation of sunk artifacts, not new acquisition. Capped costs and load-dependent worker seconds, not unlimited time-to-solution.",
    )
    write_json(out, "result.json", result)
    lines = [
        "# Frozen tree libraries on fresh gate-sum (0348)",
        "",
        result["scope"],
        "",
        "Search-cost decision: " + result["decision"],
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
        "Exact solves (1,728 jobs per arm): " + str(result["solve_counts"]),
        "",
        "Secondary content contrast: " + result["content_contrast_status"],
        "",
        "Decision precedence: harm, then <0.90 upper with reliability guard, then >0.85 lower, otherwise unresolved. Useful-speed interval with unresolved/failed guard does not establish useful transfer.",
        "",
        result["economics_scope"],
        "",
    ]
    for metric, arms in result["economics"].items():
        for a, value in arms.items():
            lines.append(
                f"{metric} {a}: acquisition {value['acquisition']}; saving {value['savings']}; repayment {value['repayment_searches']}, 95% {value['repayment_interval95']} (unbounded={value['repayment_unbounded']})."
            )
    lines += [
        "",
        "Acquisition-plus-search horizons 1, 10, 50, 100, 500, 1,000; joint bootstrap, each cell and all three pair splits, attempt-of-solve, insertion/rejection/fallback counts, shortcuts and conditional resolution prices are in result.json. No automatic top-up. DG ratio 0.39 is a different bank and is descriptive only. R-lib beating R-size does not identify structure beyond input/ADD frequency. Return to strategy.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    base.plot(out, rows, result)
