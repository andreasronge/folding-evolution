"""Descriptive build/seed uncertainty and conditional confirmation pricing."""

import json

import numpy as np
from scipy.stats import t

from experiments.chem_tape.composition_run import write_json

ARMS = ("G4", "A8", "O")


def cost(row):
    return row["evaluations"] if row["solved"] else 2 * row["cap"]


def arrays(rows, nbuild):
    cells = sorted({r["cell"] for r in rows})
    maps = {(r["arm"], r["cell"], r["ordinal"]): r for r in rows}
    if len(maps) != len(rows) or len(rows) != len(cells) * nbuild * 2 * 3:
        raise ValueError("incomplete/duplicate descriptive scoring roster")
    values = {
        a: np.array(
            [[np.log(cost(maps[a, c, i])) for i in range(nbuild * 2)] for c in cells]
        )
        for a in ARMS
    }
    return cells, values


def summarize(rows, nbuild, draws=8192):
    cells, values = arrays(rows, nbuild)
    rng = np.random.default_rng(340000)
    boot = np.empty((draws, 3))
    for k in range(draws):
        # One contemporaneous G4 baseline draw shared across both fitted contrasts.
        gi = rng.integers(2 * nbuild, size=(len(cells), 2 * nbuild))
        g = np.take_along_axis(values["G4"], gi, axis=1).mean()
        means = {}
        for arm in ("A8", "O"):
            if arm == "O" and nbuild == 8:
                # The declared O mixture has four BE and four PA artifacts.
                selected = np.concatenate(
                    (rng.integers(4, size=4), 4 + rng.integers(4, size=4))
                )
            else:
                selected = rng.integers(nbuild, size=nbuild)
            # Artifact/build is the outer uncertainty unit. Resample target
            # seeds within each selected build and fixed development cell.
            ix = 2 * selected[None, :, None] + rng.integers(
                2, size=(len(cells), nbuild, 2)
            )
            means[arm] = np.take_along_axis(
                values[arm], ix.reshape(len(cells), -1), axis=1
            ).mean()
        boot[k] = [g - means["A8"], g - means["O"], means["O"] - means["A8"]]
    ratios = {}
    for j, (name, numerator, denominator) in enumerate(
        [("G4/A8", "G4", "A8"), ("G4/O", "G4", "O"), ("O/A8", "O", "A8")]
    ):
        ratios[name] = dict(
            point=float(np.exp(values[numerator].mean() - values[denominator].mean())),
            interval95=np.exp(np.quantile(boot[:, j], [0.025, 0.975])).tolist(),
        )
    build_logs = {
        a: values[a].reshape(len(cells), nbuild, 2).mean(axis=(0, 2))
        for a in ("A8", "O")
    }
    return dict(
        ratios=ratios,
        bootstrap=dict(
            draws=draws,
            seed=340000,
            unit="independent acquisition build / old artifact",
            G4="one shared cell-stratified baseline seed resample per draw",
            targets="fixed development cells; seeds resampled inside fitted build/cell; A8 and O builds independently resampled",
        ),
        build_log_sd={a: float(v.std(ddof=1)) for a, v in build_logs.items()},
        build_mean_log_costs={a: v.tolist() for a, v in build_logs.items()},
        solve_counts={
            a: dict(
                solved=sum(r["solved"] for r in rows if r["arm"] == a),
                attempts=sum(r["arm"] == a for r in rows),
            )
            for a in ARMS
        },
        per_cell={
            c: {
                a: dict(
                    solved=sum(
                        r["solved"] for r in rows if r["cell"] == c and r["arm"] == a
                    ),
                    attempts=sum(r["cell"] == c and r["arm"] == a for r in rows),
                    geometric_cost=float(np.exp(values[a][i].mean())),
                )
                for a in ARMS
            }
            for i, c in enumerate(cells)
        },
        failure_penalty="2cap; unsolved rows are capped search failures, not observed solution times",
    )


def precision_price(rows, builds, preparation, score_timing, summary):
    nbuild = len(builds)
    cells, values = arrays(rows, nbuild)
    var_a = summary["build_log_sd"]["A8"] ** 2
    # Fixed cells, independent target seeds. This is not an estimate of
    # between-protected-cell variation: stage2 remains conditional on dev data.
    var_g = float(np.mean(np.var(values["G4"], axis=1, ddof=1)))
    baseline_floor = float(np.exp(1.96 * np.sqrt(var_g / (8 * 16))))
    effective = min(
        preparation["effective_workers"], score_timing["effective_workers"], 10
    )
    mean_worker = {
        a: float(np.mean([r["seconds"] for r in rows if r["arm"] == a])) for a in ARMS
    }
    mean_eval = {
        a: float(np.mean([r["evaluations"] for r in rows if r["arm"] == a]))
        for a in ARMS
    }
    acquisition = []
    for b in builds:
        final = builds[b]["acquisition"]
        inter = preparation["source_build_costs"][b]
        acquisition.append(
            dict(
                evaluations=final["evaluations"],
                worker_seconds=final["source_worker_seconds"]
                + sum(
                    final[k] + inter[k]
                    for k in (
                        "verification_seconds",
                        "fit_seconds",
                        "extraction_seconds",
                    )
                ),
            )
        )
    acq_worker = float(np.mean([a["worker_seconds"] for a in acquisition]))
    acq_eval = float(np.mean([a["evaluations"] for a in acquisition]))
    all_capped = all(not r["solved"] for r in rows)
    g4_fraction = sum(r["solved"] for r in rows if r["arm"] == "G4") / sum(
        r["arm"] == "G4" for r in rows
    )
    scenarios_informative = not all_capped and 0.1 <= g4_fraction <= 0.8
    scenarios = []
    for mode in ("baseline_grows_with_builds", "baseline_fixed16_per_cell"):
        candidates = []
        for B in range(8, 257):
            ng = 2 * B if mode == "baseline_grows_with_builds" else 16
            half = float(
                np.exp(t.ppf(0.975, B - 1) * np.sqrt(var_a / B + var_g / (8 * ng)))
            )
            if half <= 1.25:
                candidates.append((B, ng, half))
                break
        if not candidates:
            scenarios.append(
                dict(
                    mode=mode,
                    achievable_within256_builds=False,
                    baseline_floor_factor=baseline_floor,
                )
            )
            continue
        B, ng, half = candidates[0]
        jobs = dict(acquisition=B * 32, G4=8 * ng, A8=B * 8 * 2, O=B * 8 * 2)
        worker = (
            B * acq_worker
            + jobs["G4"] * mean_worker["G4"]
            + jobs["A8"] * mean_worker["A8"]
        )
        evaluations = (
            B * acq_eval + jobs["G4"] * mean_eval["G4"] + jobs["A8"] * mean_eval["A8"]
        )
        scenarios.append(
            dict(
                mode=mode,
                fresh_builds=B,
                protected_cells=8,
                fitted_target_seeds_per_build_cell=2,
                G4_seeds_per_protected_cell=ng,
                half_width_factor=half,
                jobs=jobs,
                acquisition_plus_G4_A8_evaluations=evaluations,
                acquisition_plus_G4_A8_worker_seconds=worker,
                projected_compute_wall_seconds=worker / effective,
                optional_O_additional_worker_seconds=jobs["O"] * mean_worker["O"],
                optional_O_additional_evaluations=jobs["O"] * mean_eval["O"],
                caveat="conditional scenario; development build variance held constant, not divided by number of protected cells; O artifact supply/confirmation design requires separate approval",
            )
        )
    return dict(
        precision_scenarios_informative=scenarios_informative,
        precision_warning="all-capped/low-headroom estimates describe the censored cost distribution and cannot price latent solve ability"
        if not scenarios_informative
        else "conditional development-variance extrapolation only",
        goal_half_width_factor=1.25,
        baseline_fixed16_floor_factor=baseline_floor,
        observed_build_variance=var_a,
        observed_G4_within_cell_seed_variance=var_g,
        effective_workers=effective,
        acquisition_mean_worker_seconds=acq_worker,
        acquisition_mean_evaluations=acq_eval,
        mean_score_worker_seconds=mean_worker,
        mean_score_evaluations=mean_eval,
        scenarios=scenarios,
        scope="planning scenario conditional on four development cells/eight pilot builds; fresh independent confirmation builds required; protected performance untouched",
        costing="measured worker costs include failed searches, intermediate/final fitting/extraction and exact verification; wall estimate uses sustained measured concurrency, excludes future agent time and scheduling overhead",
    )


def report(out, rows, builds, old, preparation, timing, smoke=False):
    summary = summarize(rows, len(builds), draws=512 if smoke else 8192)
    preparation = dict(
        preparation,
        source_build_costs={
            b: r["acquisition"]
            for b, r in json.loads((out / "seed_builds.json").read_text()).items()
        },
    )
    price = precision_price(rows, builds, preparation, timing, summary)
    frac = (
        summary["solve_counts"]["G4"]["solved"]
        / summary["solve_counts"]["G4"]["attempts"]
    )
    readings = []
    if 0.1 <= frac <= 0.8:
        readings.append("G4 development headroom lies in the pre-stated10–80% range.")
    else:
        readings.append(
            "G4 development headroom is outside10–80%; pilot contrast may be uninformative."
        )
    if all(v["solved"] / v["attempts"] < 0.1 for v in summary["solve_counts"].values()):
        readings.append(
            "All arms mostly fail at the cap; ratios near1 provide little evidence about relative ability."
        )
    oa = summary["ratios"]["O/A8"]
    if oa["interval95"][0] <= 1 <= oa["interval95"][1]:
        readings.append(
            "O/A8 is unresolved; this does not establish equality or that old syntax carries useful help."
        )
    elif oa["interval95"][0] > 1:
        readings.append(
            "A8 costs less than these eight reinterpreted O artifacts on development cells; fresh acquisition necessity in general is untested."
        )
    else:
        readings.append(
            "These eight reinterpreted O artifacts cost less on development cells; protected confirmation remains untested."
        )
    result = dict(
        status="smoke" if smoke else "descriptive_probe_complete",
        alphabet="v2_x4",
        summary=summary,
        score_timing=timing,
        stage2_price=price,
        readings=readings,
        old_identities=[b["identity"] for b in old["builds"]],
        protected_performance_scored=False,
        scope="external fitting plus literal fragments; alphabet/domain changed; development only; no confirmatory claims, inherited evolution or isolated predicate-placement inference",
    )
    write_json(out, "result.json", result)
    text = [
        "# Independent-input pilot (descriptive)",
        "",
        "SMOKE ONLY; no scientific admission."
        if smoke
        else "Protected cells remain unscored. Return to strategy; stage2 requires its own allocation.",
        "",
        "|Contrast (capped cost)|Point|95% build/seed interval|",
        "|---|---:|---:|",
    ]
    for name, r in summary["ratios"].items():
        text.append(
            f"|{name}|{r['point']:.3f}|[{r['interval95'][0]:.3f}, {r['interval95'][1]:.3f}]|"
        )
    text += [
        "",
        "Failures contribute2cap. A finite no-hit sample is a bound, not impossibility. Shared G4 seed uncertainty is propagated.",
        "",
        "|Arm|Solved/attempts|",
        "|---|---:|",
    ]
    for a, v in summary["solve_counts"].items():
        text.append(f"|{a}|{v['solved']}/{v['attempts']}|")
    text += [
        "",
        *readings,
        "",
        f"Between-build log-SD: {summary['build_log_sd']}. O identities: {result['old_identities']}.",
        "",
        "The stage2 price is a conditional scenario based on four development cells and pilot variance. Independent fresh builds are required. Both build and baseline-seed uncertainty enter the half-width calculation; increasing builds alone cannot eliminate a fixed baseline floor.",
        "",
        f"Precision scenario usable for a transfer comparison: {price['precision_scenarios_informative']}; {price['precision_warning']}.",
        "",
        f"Fixed16-seed/cell baseline floor factor: {price['baseline_fixed16_floor_factor']:.3f}.",
        f"Measured effective workers used for pricing: {price['effective_workers']:.2f}.",
        "",
    ]
    for s in price["scenarios"]:
        text.append(str(s))
    text += [
        "",
        "Source/fallback incidence and full acquisition costs are in source_summary.json; exact-check tails and fitting/batch load are in timing.json and preparation.json. Per-cell solves and bootstrap details are in result.json.",
        "",
        "PIPE is the external-fitting precedent; DreamCoder connects library learning and search policy. This literal-window recipe does not test a new learning principle. No pilot observation is promoted to the digest.",
    ]
    (out / "report.md").write_text("\n".join(text) + "\n")
    plot(out, rows)


def plot(out, rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]
        # Common evaluation grid; carry last observed value after a solve.
        cap = max(r["cap"] for r in rs)
        grid = np.array(
            sorted(
                {b for b in (4096, 32768, 131072, 262144, 524288) if b <= cap} | {cap}
            )
        )
        for ax, column, label in [
            (axes[0], 1, "Best correct lexicase cases"),
            (axes[1], 2, "Distinct correctness patterns"),
        ]:
            vals = []
            for budget in grid:
                v = []
                for r in rs:
                    eligible = [point for point in r["curve"] if point[0] <= budget]
                    v.append((eligible[-1] if eligible else r["curve"][0])[column])
                vals.append(np.mean(v))
            ax.plot(grid, vals, marker="o", label=a)
            ax.set_xlabel("Evaluations")
            ax.set_ylabel(label)
            ax.set_xscale("log")
        axes[2].plot(
            [r["evaluations"] for r in rs],
            [r["exact_check_seconds"] for r in rs],
            ".",
            label=a,
            alpha=0.6,
        )
    axes[2].set_xlabel("Evaluations")
    axes[2].set_ylabel("Exact-check seconds per search")
    for ax in axes:
        ax.legend()
        ax.grid(alpha=0.2)
    fig.suptitle("v2_x4 · development only (correctness-pattern diversity)")
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=140)
    plt.close(fig)
