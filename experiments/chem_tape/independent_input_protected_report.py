"""1536 fixed-cell confirmation: build uncertainty, cap sensitivity, full cost."""

import json

import numpy as np
from scipy.stats import spearmanr, t

from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.independent_input_bank import pairing
from experiments.chem_tape.independent_input_report import ARMS, plot

USEFUL = (
    "useful protected-cell replication on x4-double-gate-v1, relative to G4 at this cap"
)


def decision(interval):
    if interval[0] > 1.5:
        return USEFUL
    if interval[1] < 1.5:
        return "not worthwhile at this margin"
    return "unresolved"


def arrays(rows, nbuild, penalty=2):
    cells = sorted({r["cell"] for r in rows})
    counts = dict(G4=2 * nbuild, A8=2 * nbuild, O=2 * min(nbuild, 8))
    by = {(r["arm"], r["cell"], r["ordinal"]): r for r in rows}
    expected = {(a, c, i) for c in cells for a, n in counts.items() for i in range(n)}
    if len(by) != len(rows) or set(by) != expected:
        raise ValueError("incomplete/duplicate protected scoring roster")
    for (a, c, i), r in by.items():
        if r["build"] != i // 2:
            raise ValueError("target build/ordinal assignment changed")
    values = {
        a: np.array(
            [
                [
                    np.log(r["evaluations"] if r["solved"] else penalty * r["cap"])
                    for i in range(n)
                    for r in [by[a, c, i]]
                ]
                for c in cells
            ]
        )
        for a, n in counts.items()
    }
    return cells, values


def wilson(solved, attempts):
    z = 1.959963984540054
    p = solved / attempts
    den = 1 + z * z / attempts
    mid = (p + z * z / (2 * attempts)) / den
    half = z * np.sqrt(p * (1 - p) / attempts + z * z / (4 * attempts**2)) / den
    return [float(max(0, mid - half)), float(min(1, mid + half))]


def summarize(rows, nbuild, penalty=2, draws=8192):
    cells, values = arrays(rows, nbuild, penalty)
    rng = np.random.default_rng(730000)
    boot = np.empty((draws, 3))
    for k in range(draws):
        # G4 is sampled once per cell/draw and shared across both contrasts.
        gi = rng.integers(2 * nbuild, size=(len(cells), 2 * nbuild))
        g = np.take_along_axis(values["G4"], gi, axis=1).mean()
        means = {}
        for arm in ("A8", "O"):
            B = values[arm].shape[1] // 2
            selected = (
                np.concatenate((rng.integers(4, size=4), 4 + rng.integers(4, size=4)))
                if arm == "O" and B == 8
                else rng.integers(B, size=B)
            )
            ix = 2 * selected[None, :, None] + rng.integers(2, size=(len(cells), B, 2))
            means[arm] = np.take_along_axis(
                values[arm], ix.reshape(len(cells), -1), axis=1
            ).mean()
        boot[k] = [g - means["A8"], g - means["O"], means["O"] - means["A8"]]
    ratios = {}
    for j, (name, num, den) in enumerate(
        (("G4/A8", "G4", "A8"), ("G4/O", "G4", "O"), ("O/A8", "O", "A8"))
    ):
        ratios[name] = dict(
            point=float(np.exp(values[num].mean() - values[den].mean())),
            interval95=np.exp(np.quantile(boot[:, j], [0.025, 0.975])).tolist(),
        )
    build_logs = {
        a: values[a].reshape(len(cells), -1, 2).mean(axis=(0, 2)) for a in ("A8", "O")
    }
    counts = {}
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]
        s = sum(r["solved"] for r in rs)
        counts[a] = dict(
            solved=s,
            attempts=len(rs),
            fraction=s / len(rs),
            descriptive_Wilson95=wilson(s, len(rs)),
        )
    return dict(
        ratios=ratios,
        decision=decision(ratios["G4/A8"]["interval95"]),
        margin=1.5,
        failure_penalty=penalty,
        bootstrap=dict(
            draws=draws,
            seed=730000,
            unit="fresh acquisition build / old artifact",
            G4="one shared cell-stratified baseline seed draw per replicate",
            O="four BE plus four PA artifacts resampled within strata",
            targets="fixed cells/source roster/family; two seeds resampled within selected build and cell",
        ),
        solve_counts=counts,
        solve_interval_scope="descriptive Wilson intervals; shared fitted builds are not independent acquisition replicates",
        build_log_sd={a: float(v.std(ddof=1)) for a, v in build_logs.items()},
        build_mean_log_costs={a: v.tolist() for a, v in build_logs.items()},
        per_cell={
            c: {
                a: dict(
                    solved=sum(
                        r["solved"] for r in rows if r["cell"] == c and r["arm"] == a
                    ),
                    attempts=values[a].shape[1],
                    geometric_cost=float(np.exp(values[a][i].mean())),
                )
                for a in ARMS
            }
            for i, c in enumerate(cells)
        },
    )


def economics(rows, builds, intermediate, summary):
    # Final acquisition includes both search batches; add only intermediate fit overhead.
    acquisition = {}
    for b, record in builds.items():
        final, inter = record["acquisition"], intermediate[b]["acquisition"]
        acquisition[b] = dict(
            evaluations=final["evaluations"],
            worker_seconds=final["source_worker_seconds"]
            + sum(
                final[k] + inter[k]
                for k in ("verification_seconds", "fit_seconds", "extraction_seconds")
            ),
        )
    mean_evals = {
        a: float(np.mean([r["evaluations"] for r in rows if r["arm"] == a]))
        for a in ARMS
    }
    acq = float(np.mean([v["evaluations"] for v in acquisition.values()]))
    deployed = {}
    for b in builds:
        rs = [r for r in rows if r["arm"] == "A8" and str(r["build"]) == b]
        keys = {(r["cell"], r["seed"]) for r in rs}
        baseline = [
            r for r in rows if r["arm"] == "G4" and (r["cell"], r["seed"]) in keys
        ]
        savings = float(
            np.mean([r["evaluations"] for r in baseline])
            - np.mean([r["evaluations"] for r in rs])
        )
        deployed[b] = dict(
            acquisition=acquisition[b],
            target_searches=len(rs),
            A8_acquisition_plus_search_evaluations=acquisition[b]["evaluations"]
            + sum(r["evaluations"] for r in rs),
            matched_G4_search_evaluations=sum(r["evaluations"] for r in baseline),
            mean_evaluation_saving_per_search=savings,
            repayment_searches=acquisition[b]["evaluations"] / savings
            if savings > 0
            else None,
        )
    saving = mean_evals["G4"] - mean_evals["A8"]
    yield_values = [sum(intermediate[b]["yields"].values()) for b in builds]
    empty = [not intermediate[b]["library"]["fragments"] for b in builds]
    logs = summary["build_mean_log_costs"]["A8"]
    # Match build order explicitly (JSON sorts string keys lexicographically).
    logs = [logs[int(b)] for b in builds]
    rho = None
    if len(set(yield_values)) > 1 and len(set(logs)) > 1:
        rho = float(spearmanr(yield_values, logs).statistic)
    return dict(
        acquisition=acquisition,
        per_build=deployed,
        acquisition_mean_evaluations=acq,
        acquisition_total_evaluations=sum(
            v["evaluations"] for v in acquisition.values()
        ),
        acquisition_mean_worker_seconds=float(
            np.mean([v["worker_seconds"] for v in acquisition.values()])
        ),
        mean_search_evaluations=mean_evals,
        mean_search_worker_seconds={
            a: float(np.mean([r["seconds"] for r in rows if r["arm"] == a]))
            for a in ARMS
        },
        scoring_total_evaluations=sum(r["evaluations"] for r in rows),
        arithmetic_saving_per_search=saving,
        repayment_searches=acq / saving if saving > 0 else None,
        repayment_scope="arithmetic evaluations actually spent, failures charged cap; acquisition once per deployed build; no finite repayment if savings<=0; no wall-time claim",
        first_yield_target_log_cost_spearman=rho,
        empty_intermediate_target_geometric_cost={
            str(flag): float(
                np.exp(np.mean([v for v, e in zip(logs, empty) if e == flag]))
            )
            for flag in (False, True)
            if flag in empty
        },
        association_scope="descriptive build-level acquisition yield/fallback association, not causal attribution",
    )


def resolution_price(rows, summary, costs, ncell):
    _, values = arrays(rows, len(summary["build_mean_log_costs"]["A8"]))
    var_a = summary["build_log_sd"]["A8"] ** 2
    var_g = float(np.var(values["G4"], axis=1, ddof=1).mean())
    distance = abs(np.log(summary["ratios"]["G4/A8"]["point"] / 1.5))
    scenarios = []
    for mode in ("baseline_grows_with_builds", "baseline_fixed48_per_cell"):
        found = None
        for B in range(24, 513):
            ng = 2 * B if mode == "baseline_grows_with_builds" else 48
            half = float(
                t.ppf(0.975, B - 1) * np.sqrt(var_a / B + var_g / (ncell * ng))
            )
            # Expected interval clearing the margin at the observed point, conditional only.
            if distance > 0 and half < distance:
                jobs = dict(acquisition=32 * B, A8=2 * B * ncell, G4=ng * ncell)
                found = dict(
                    fresh_builds=B,
                    baseline_seeds_per_cell=ng,
                    jobs=jobs,
                    half_width_factor=float(np.exp(half)),
                    total_evaluations=B * costs["acquisition_mean_evaluations"]
                    + sum(
                        jobs[a] * costs["mean_search_evaluations"][a]
                        for a in ("G4", "A8")
                    ),
                    total_worker_seconds=B * costs["acquisition_mean_worker_seconds"]
                    + sum(
                        jobs[a] * costs["mean_search_worker_seconds"][a]
                        for a in ("G4", "A8")
                    ),
                )
                break
        scenarios.append(
            dict(
                mode=mode, achievable_within512_builds=found is not None, scenario=found
            )
        )
    return dict(
        needed=summary["decision"] == "unresolved",
        scenarios=scenarios,
        observed_build_variance=var_a,
        observed_G4_seed_variance=var_g,
        baseline_fixed48_floor_factor=float(
            np.exp(1.96 * np.sqrt(var_g / (ncell * 48)))
        ),
        scope="conditional resolution at observed point and capped-cost variances; independent new run would need approval; no power guarantee; all-capped or mostly-capped data cannot price uncapped difficulty",
    )


def report(out, rows, builds, old, preparation, timing, smoke=False):
    draws = 512 if smoke else 8192
    summary = summarize(rows, len(builds), draws=draws)
    sensitivity = summarize(rows, len(builds), penalty=1, draws=draws)
    bank = json.loads((out / "bank.json").read_text())
    by = {c["id"]: c for c in bank["screen"]["cells"]}
    source_pairs = {pairing(by[c]) for c in bank["split"]["source"]}
    unseen = {r["cell"] for r in rows if pairing(by[r["cell"]]) not in source_pairs}
    subgroups = {}
    for name, cells in (
        ("unseen_pairing", unseen),
        ("source_seen_pairing", {r["cell"] for r in rows} - unseen),
    ):
        if cells:
            subset = summarize(
                [r for r in rows if r["cell"] in cells], len(builds), draws=draws
            )
            subgroups[name] = dict(
                cells=sorted(cells),
                ratios=subset["ratios"],
                solve_counts=subset["solve_counts"],
                scope="descriptive; no subgroup decision",
            )
    intermediate = json.loads((out / "seed_builds.json").read_text())
    costs = economics(rows, builds, intermediate, summary)
    readings = []
    if all(v["fraction"] < 0.1 for v in summary["solve_counts"].values()):
        readings.append(
            "All arms mostly cap; a ratio near one says little about uncapped difficulty or why acquisition failed."
        )
    sensitive = summary["decision"] != sensitivity["decision"]
    if sensitive:
        readings.append(
            "Decision changes at 1cap: penalty-sensitive capped-cost usefulness, not an ordinary time-to-solution speed-up."
        )
    if summary["decision"] == "unresolved":
        readings.append(
            "The interval spans 1.5; usefulness remains unresolved, not equality. Resolution price is conditional."
        )
    result = dict(
        status="smoke" if smoke else "protected_confirmation_complete",
        protected_performance_scored=not smoke,
        bank="x4-double-gate-v1",
        alphabet="v2_x4",
        summary=summary,
        sensitivity_1cap=sensitivity,
        penalty_sensitive=sensitive,
        subgroups=subgroups,
        economics=costs,
        resolution_price=resolution_price(
            rows, summary, costs, len(summary["per_cell"])
        ),
        preparation_seconds=preparation["prepare_seconds"],
        score_timing=timing,
        old_identities=[b["identity"] for b in old["builds"]],
        readings=readings,
        scope="protected within-development-bank confirmation relative to supplied G4 at this cap; fixed family/cells/roster; no fresh-bank transfer, general portability, inheritance, predicate-placement isolation, or context/fragment/supply attribution; O token reinterpretation prevents family-specificity inference",
    )
    write_json(out, "result.json", result)
    text = [
        "# Independent-input protected-cell confirmation",
        "",
        "SMOKE ONLY: development targets; no scientific admission."
        if smoke
        else summary["decision"],
        "",
        "|Capped-cost contrast|Point|95% build/seed interval|",
        "|---|---:|---:|",
    ]
    for name, r in summary["ratios"].items():
        text.append(
            f"|{name}|{r['point']:.3f}|[{r['interval95'][0]:.3f}, {r['interval95'][1]:.3f}]|"
        )
    text += [
        "",
        f"Failure charge: 2cap. At 1cap: {sensitivity['decision']}; penalty-sensitive: {sensitive}.",
        "",
        "|Arm|Solved/attempts|Descriptive Wilson 95%|",
        "|---|---:|---:|",
    ]
    for a, v in summary["solve_counts"].items():
        text.append(f"|{a}|{v['solved']}/{v['attempts']}|{v['descriptive_Wilson95']}|")
    text += [
        "",
        summary["solve_interval_scope"],
        "",
        *readings,
        "",
        result["scope"],
        "",
        "Unseen-pairing and other-cell results are descriptive in result.json; an aggregate benefit leaves new-pairing assembly unresolved if those three cells fail.",
        "",
        f"Arithmetic acquisition repayment: {costs['repayment_searches']} searches per build (None means no finite repayment). {costs['repayment_scope']}",
        "",
        "Per-cell costs, acquisition-yield/fallback associations, complete acquisition-plus-search evaluations and conditional resolution scenarios are in result.json. Source failures/fallbacks remain in source_summary.json; batch and exact-check tails are in timing.json/preparation.json. O uses the frozen BE1..4/PA1..4 A8-prime artifacts with token ids reinterpreted.",
        "",
        "A finite no-hit sample is a bound, not impossibility. Return to strategy; no automatic expansion.",
    ]
    (out / "report.md").write_text("\n".join(text) + "\n")
    plot(
        out,
        rows,
        title="v2_x4 · protected confirmation"
        if not smoke
        else "v2_x4 · development smoke",
    )
