"""0145 independent-build inference, historical pairing and measured economics."""

import math

import numpy as np

from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.fragment_run import CORPORA
from experiments.chem_tape.small_source_report import contrast
from experiments.chem_tape.sparse_feedback_report import HORIZONS
from experiments.chem_tape.two_sum_report import bootstrap, describe


def interval_draws(point, draws):
    return dict(
        cost_ratio=float(point), interval_95=np.quantile(draws, [0.025, 0.975]).tolist()
    )


def acquisition(build, units):
    a = build["acquisition"]
    if units == "evaluations":
        return a["evaluations"]
    return sum(
        a.get(k, 0)
        for k in (
            "source_worker_seconds",
            "verification_seconds",
            "fit_seconds",
            "extraction_seconds",
            "external_verification_seconds",
            "intermediate_overhead_seconds",
        )
    )


def economics(rows, methods, builds, calibration):
    result = {}
    for units in ("evaluations", "worker_seconds"):
        fit, draws, idx, base, baseline = bootstrap(rows, methods, units)
        # Historical G4 times require current-machine calibration. New builds,
        # fits and target times were directly measured, not calibrated.
        if units == "worker_seconds":
            base *= calibration
            baseline *= calibration
        curves, prices, searches, breaks = {}, {}, {}, {}
        for m in methods:
            price = np.array(
                [acquisition(builds[f"{tid}|{m}"], units) for tid in CORPORA]
            )
            pdraws = price[idx].mean(1)
            saving = baseline - draws[m]
            roots = np.full(len(saving), np.inf)
            np.divide(pdraws, saving, out=roots, where=saving > 0)
            mean_saving = base - fit[m].mean()
            # Including infinity preserves never-repay outcomes in interval endpoints.
            ordered = np.sort(roots)
            qs = [float(ordered[int(q * (len(ordered) - 1))]) for q in (0.025, 0.975)]
            breaks[m] = dict(
                point_N=float(price.mean() / mean_saving) if mean_saving > 0 else None,
                interval_95_N=[q if math.isfinite(q) else None for q in qs],
                never_repay_fraction=float(np.mean(saving <= 0)),
                null_endpoint_means="infinite/no repayment",
                conditional_finite_interval_95_N=np.quantile(
                    roots[np.isfinite(roots)], [0.025, 0.975]
                ).tolist()
                if np.isfinite(roots).any()
                else None,
            )
            prices[m], searches[m] = float(price.mean()), float(fit[m].mean())
            curves[m] = [
                dict(
                    N=n,
                    cost=float(price.mean() + n * fit[m].mean()),
                    interval_95=np.quantile(
                        pdraws + n * draws[m], [0.025, 0.975]
                    ).tolist(),
                )
                for n in HORIZONS
            ]
        prices["G4"], searches["G4"] = 0.0, base
        curves["G4"] = [
            dict(
                N=n,
                cost=float(n * base),
                interval_95=np.quantile(n * baseline, [0.025, 0.975]).tolist(),
            )
            for n in HORIZONS
        ]
        result[units] = dict(
            acquisition_mean=prices,
            arithmetic_search_mean=searches,
            curves=curves,
            break_even_vs_G4=breaks,
            qualification="actual capped arithmetic expenditure; fresh acquisition includes failures, intermediate A8 fitting and both verification passes; G4 historical worker time calibrated by two replay rows; not uncapped expected solve time",
        )
    return result


def report(out, rows, schedule, builds, preparation, historical):
    def key(r):
        return r["corpus"], r["cell"], r["seed"], r["arm"]

    if (
        len(rows) != len(schedule)
        or len({key(r) for r in rows}) != len(rows)
        or {key(r) for r in rows} != {key(r) for r in schedule}
    ):
        raise ValueError("incomplete/duplicate confirmation roster")
    methods = tuple(preparation["admission"]["selected"]["arms"])
    old = {key(r): r for r in historical if r["arm"] == "A8"}
    g4 = [r for r in historical if r["arm"] == "G4"]
    if len(old) != 1024 or len(g4) != 256:
        raise ValueError("historical roster incomplete")
    combined = rows + g4
    fit, draws, idx, base, baseline = bootstrap(combined, methods, "log_cost")
    primary = interval_draws(
        np.exp(base - fit["A8"].mean()), np.exp(baseline - draws["A8"])
    )
    lo, hi = primary["interval_95"]
    decision = (
        "useful_replication"
        if lo > 1.5
        else "below_usefulness_bar"
        if hi < 1.5
        else "unresolved"
    )
    paired = []
    for r in rows:
        if r["arm"] != "A8":
            continue
        h = old[key(r)]
        if (
            r["block"] != h["block"]
            or r["seed_ordinal"] != h["seed_ordinal"]
            or r["training_indices"] != h["training_indices"]
        ):
            raise ValueError("historical block/key/case pairing changed")
        paired.extend((dict(r, method="A8"), dict(h, method="historical_A8")))
    delta = contrast(paired, "A8", "historical_A8")
    if delta["n"] != 16 or delta["df"] != 15 or delta["missing_blocks"]:
        raise ValueError("historical comparison incomplete")
    delta["qualification"] = (
        "historical roster comparison: new single build vs four old block-specific artifacts per corpus; identical target keys, not shared source ancestry or equal per-build reliability"
    )
    sigma = (
        contrast([dict(r, method=r["arm"]) for r in rows], "S8", "A8")
        if "S8" in methods
        else None
    )
    onecap = [dict(r, cap=r["cap"] / 2) if not r["solved"] else r for r in combined]
    f1, d1, _, b1, bd1 = bootstrap(onecap, methods, "log_cost")
    sensitivity = interval_draws(np.exp(b1 - f1["A8"].mean()), np.exp(bd1 - d1["A8"]))
    families = {}
    for family in ("BE", "PA"):
        indices = [i for i, t in enumerate(CORPORA) if t.startswith(family)]
        family_draws = fit["A8"][idx[:, :8] if family == "BE" else idx[:, 8:]].mean(1)
        families[family] = dict(
            u=interval_draws(
                np.exp(base - fit["A8"][indices].mean()),
                np.exp(baseline - family_draws),
            ),
            arms={
                m: describe(
                    [r for r in rows if r["family"] == family and r["arm"] == m]
                )
                for m in methods
            },
            build_log_sd=float(np.std(fit["A8"][indices], ddof=1)),
        )
    cells = {}
    for cid in sorted({r["cell"] for r in rows}):
        rs = [r for r in combined if r["cell"] == cid]
        cells[cid] = {
            m: describe([r for r in rs if r["arm"] == m]) for m in (*methods, "G4")
        }
    # Scenario precision: independent builds can reduce their variance, but
    # they cannot eliminate uncertainty in the reused shared baseline.
    pooled_var = float(
        np.mean(
            [
                np.var(
                    fit["A8"][[i for i, t in enumerate(CORPORA) if t.startswith(f)]],
                    ddof=1,
                )
                for f in ("BE", "PA")
            ]
        )
    )
    baseline_var = float(np.var(baseline, ddof=1))
    distance = abs(base - fit["A8"].mean() - math.log(1.5))
    denominator = (distance / 1.96) ** 2 - baseline_var
    required = (
        max(16, int(math.ceil(pooled_var / denominator / 2) * 2))
        if denominator > 0
        else None
    )
    eco = economics(
        combined, methods, builds, preparation["validation"]["G4_time_calibration"]
    )
    result = dict(
        decision=decision,
        primary=primary,
        margin=1.5,
        delta=delta,
        sigma=sigma,
        sigma_contextual_reference=1.17,
        one_cap_sensitivity=sensitivity,
        interval_units="16 independent new builds resampled within source family; shared G4 seeds resampled within each fixed cell; 8192 draws; fixed development target roster",
        arms={
            m: describe([r for r in combined if r["arm"] == m])
            for m in (*methods, "G4")
        },
        per_family=families,
        per_cell=cells,
        source_builds={
            k: dict(
                yields=b["yields"],
                empty_cells=b["empty_cells"],
                library_size=len(b["library"]["fragments"]),
                table_hash=b["table_hash"],
                acquisition=b["acquisition"],
            )
            for k, b in builds.items()
        },
        between_build_log_means={
            m: dict(zip(CORPORA, v.tolist())) for m, v in fit.items()
        },
        resolution_price=dict(
            estimated_total_builds=required,
            additional_builds=required - 16 if required is not None else None,
            within_family_log_variance=pooled_var,
            shared_G4_log_variance=baseline_var,
            qualification="normal precision scenario at observed effect; null total means fixed G4 uncertainty floor prevents resolution by build top-up alone; no automatic top-up",
        ),
        economics=eco,
        admission=preparation["admission"],
        scope="one complementary development source roster in BE/PA; two-sum-v1 development targets; externally fitted bundled decoder/library; no new-family or inherited-evolution claim",
    )
    write_json(out, "result.json", result)
    summary = f"u=G4/A8′ {primary['cost_ratio']:.3f} [{lo:.3f}, {hi:.3f}]; margin 1.5; {decision}."
    text = "# Complementary-source replication\n\n" + summary + "\n\n"
    text += f"Historical roster comparison delta=A8′/historical A8: {delta['cost_ratio']:.3f}, 95% t interval {delta['interval_95']}, df=15. Target pairing does not pair source ancestry.\n\n"
    if sigma:
        text += f"Secondary S8′/A8′: {sigma['cost_ratio']:.3f}, interval {sigma['interval_95']}; contextual reference 1.17.\n\n"
    else:
        text += "S8′ omitted by timing admission; no adaptive-versus-static attribution.\n\n"
    text += "The usefulness bar and repayment use different estimators. Arithmetic measured acquisition plus capped search costs and bootstrap break-even, including never-repay draws, are in result.json. Below-bar usefulness alone does not establish deterioration relative to historical A8. Unresolved intervals establish neither equality nor source dependence.\n\n"
    text += (
        "All outcomes return to strategy. Per-family/cell solves, source yields/fallbacks/library sizes, cap sensitivity, build spread, resolution price and economics are in result.json.\n\n"
        + result["scope"]
        + "\n"
    )
    (out / "report.md").write_text(text)
    plots(out, rows, result)
    return result


def plots(out, rows, result):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    methods = list(result["between_build_log_means"])
    fig, grid = plt.subplots(2, 2, figsize=(11, 7))
    axes = grid.ravel()
    for m in methods:
        axes[0].plot(
            np.arange(16),
            list(result["between_build_log_means"][m].values()),
            "o-",
            label=m + "′",
        )
        rs = [r for r in rows if r["arm"] == m]
        budget = np.arange(256, 524289, 8192)
        fitness = [
            np.mean(
                [
                    next(
                        (p[1] / 64 for p in reversed(r["curve"]) if p[0] <= b),
                        r["curve"][0][1] / 64,
                    )
                    for r in rs
                ]
            )
            for b in budget
        ]
        diversity = [
            np.mean(
                [
                    next(
                        (p[2] for p in reversed(r["curve"]) if p[0] <= b),
                        r["curve"][0][2],
                    )
                    for r in rs
                ]
            )
            for b in budget
        ]
        axes[1].plot(budget, fitness, label=m + "′")
        axes[3].plot(budget, diversity, label=m + "′")
        axes[2].plot(
            np.arange(16),
            [
                len(result["source_builds"][f"{tid}|{m}"]["empty_cells"])
                for tid in CORPORA
            ],
            "o-",
            label=m + "′",
        )
    axes[0].set(xlabel="Build index", ylabel="Mean log penalized cost")
    axes[1].set(
        xlabel="Evaluations", ylabel="Training fitness (last observation carried)"
    )
    axes[2].set(xlabel="Build index", ylabel="Empty source cells")
    axes[3].set(
        xlabel="Evaluations",
        ylabel="Distinct fitness-case masks (last observation carried)",
    )
    for ax in axes:
        ax.legend()
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, units in zip(axes, ("evaluations", "worker_seconds")):
        for m, curve in result["economics"][units]["curves"].items():
            x = [p["N"] for p in curve]
            y = [p["cost"] for p in curve]
            ax.plot(x, y, label=m)
            ax.fill_between(
                x,
                [p["interval_95"][0] for p in curve],
                [p["interval_95"][1] for p in curve],
                alpha=0.12,
            )
        ax.set(xscale="symlog", yscale="symlog", xlabel="Searches N", ylabel=units)
        ax.legend()
    fig.tight_layout()
    fig.savefig(out / "cost_curves.png")
    plt.close(fig)
