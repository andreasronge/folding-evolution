"""2033 equal-block, corpus-clustered contrasts and fully charged acquisition curves."""

import math

import numpy as np

from experiments.chem_tape.comparison_gate_report import describe, balanced_target_n
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.fragment_report import plots, row_key
from experiments.chem_tape.small_source_report import contrast

METHODS = ("A8", "S8", "C4F4", "full_F", "G4")
HORIZONS = (0, 1, 4, 16, 64, 256, 1024, 4096)


def contrasts(rows, **kwargs):
    return {
        name: contrast(rows, a, b, **kwargs)
        for name, a, b in (
            ("sigma", "S8", "A8"),
            ("A8_over_seed_speed", "C4F4", "A8"),
            ("S8_over_seed_speed", "C4F4", "S8"),
            ("rho_A8", "full_F", "A8"),
            ("rho_S8", "full_F", "S8"),
            ("A8_over_full_C_speed", "full_C", "A8"),
            ("S8_over_full_C_speed", "full_C", "S8"),
        )
    }


def acquisition_price(a, units, calibration, *, adaptive=False, intermediate=False):
    if units == "evaluations":
        return a["evaluations"]
    if adaptive:
        source = (
            a["historical_source_seconds"] * calibration["G4"]
            + a["current_source_seconds"]
        )
    else:
        source = a["source_worker_seconds"] * calibration["G4"]
    return (
        source
        + sum(
            a.get(k, 0)
            for k in (
                "verification_seconds",
                "fit_seconds",
                "extraction_seconds",
                "continuation_verification_seconds",
            )
        )
        + (a["intermediate_overhead_seconds"] if intermediate else 0)
    )


def economics(rows, builds, p, g4):
    tids = sorted({r["corpus"] for r in rows})
    cal = p["validation"]["historical_replay"]["calibration"]
    result = {}
    for units in ("evaluations", "worker_seconds"):
        A = {m: [] for m in METHODS}
        S = {m: [] for m in METHODS}
        solves = {m: [] for m in METHODS}
        for tid in tids:
            for m in METHODS:
                if m in ("A8", "S8"):
                    prices = [
                        acquisition_price(
                            builds[f"{tid}|{b}|{m}"]["acquisition"],
                            units,
                            cal,
                            adaptive=True,
                            intermediate=True,
                        )
                        for b in range(4)
                    ]
                elif m == "C4F4":
                    prices = [
                        acquisition_price(
                            p["seed_acquisition"][f"{tid}|{b}"], units, cal
                        )
                        for b in range(4)
                    ]
                elif m == "full_F":
                    prices = [acquisition_price(p["full_acquisition"][tid], units, cal)]
                else:
                    prices = [0.0]
                A[m].append(np.mean(prices))
                rs = (
                    g4
                    if m == "G4"
                    else [r for r in rows if r["corpus"] == tid and r["method"] == m]
                )
                factor = (
                    cal[{"C4F4": "seed", "full_F": "full", "G4": "G4"}.get(m, "G4")]
                    if m in ("C4F4", "full_F", "G4")
                    else 1.0
                )
                S[m].append(
                    np.mean(
                        [
                            r["evaluations"]
                            if units == "evaluations"
                            else (
                                r["seconds"] + r.get("external_verification_seconds", 0)
                            )
                            * factor
                            for r in rs
                        ]
                    )
                )
                solves[m].append(np.mean([r["solved"] for r in rs]))
        A = {m: np.array(v) for m, v in A.items()}
        S = {m: np.array(v) for m, v in S.items()}
        rng = np.random.default_rng(2033)
        idx = np.column_stack(
            [
                rng.choice(
                    [i for i, t in enumerate(tids) if t.startswith(f)], size=(4096, 8)
                )
                for f in ("BE", "PA")
            ]
        )
        Ab = {m: v[idx].mean(1) for m, v in A.items()}
        Sb = {m: v[idx].mean(1) for m, v in S.items()}
        gv = np.array(
            [
                r["evaluations"] if units == "evaluations" else r["seconds"] * cal["G4"]
                for r in g4
            ]
        )
        Sb["G4"] = gv[rng.integers(len(g4), size=(4096, len(g4)))].mean(1)
        curves = {
            m: [
                dict(
                    N=n,
                    cost=float(A[m].mean() + n * S[m].mean()),
                    interval_95=np.quantile(Ab[m] + n * Sb[m], [0.025, 0.975]).tolist(),
                )
                for n in HORIZONS
            ]
            for m in METHODS
        }
        comparisons = {}
        for x, y in [
            ("A8", "S8"),
            ("A8", "C4F4"),
            ("S8", "C4F4"),
            ("A8", "full_F"),
            ("S8", "full_F"),
            ("A8", "G4"),
            ("S8", "G4"),
        ]:
            dA = float(A[x].mean() - A[y].mean())
            saving = float(S[y].mean() - S[x].mean())
            root = dA / saving if saving and dA / saving > 0 else None
            dbA = Ab[x] - Ab[y]
            dbS = Sb[x] - Sb[y]
            roots = np.divide(-dbA, dbS, out=np.full(4096, np.nan), where=dbS != 0)
            positive = np.isfinite(roots) & (roots > 0)
            comparisons[x + "_vs_" + y] = dict(
                initial_acquisition_difference=dA,
                arithmetic_search_saving=saving,
                crossover_N=root,
                crossover_direction=("wins_after" if saving > 0 else "loses_after")
                if root
                else None,
                initially_cheaper=dA < 0,
                eventually_cheaper=saving > 0,
                positive_crossover_bootstrap_fraction=float(positive.mean()),
                wins_after_bootstrap_fraction=float((positive & (dbS < 0)).mean()),
                loses_after_bootstrap_fraction=float((positive & (dbS > 0)).mean()),
                no_positive_crossover_fraction=float((~positive).mean()),
                positive_crossover_interval_95=np.quantile(
                    roots[positive], [0.025, 0.975]
                ).tolist()
                if positive.any()
                else None,
                total_cost_differences=[
                    dict(
                        N=n,
                        difference=float(dA - n * saving),
                        interval_95=np.quantile(dbA + n * dbS, [0.025, 0.975]).tolist(),
                        cheaper_bootstrap_fraction=float((dbA + n * dbS < 0).mean()),
                    )
                    for n in HORIZONS
                ],
            )
        result[units] = dict(
            arithmetic_means={
                m: dict(
                    A=float(A[m].mean()),
                    S=float(S[m].mean()),
                    solve_probability=float(np.mean(solves[m])),
                )
                for m in METHODS
            },
            corpus_acquisition_search={
                m: dict(A=A[m].tolist(), S=S[m].tolist()) for m in METHODS
            },
            curves=curves,
            comparisons=comparisons,
        )
    result.update(
        bootstrap_seed=2033,
        bootstrap_replicates=4096,
        accounting="One deployed build; equal four-block weighting within16 corpora. First batch plus intermediate verification/fit/extraction, continuation including failures, final verification/fit/extraction. Historical G4 source seconds calibrated; adaptive collection seconds current. Corpus resampling within family preserves acquisition/search dependence; unpaired G4 resampled separately.",
        caveat="Arithmetic capped effort, not uncapped expected time to solve. Evaluation units exclude fitting/extraction overhead. Historical search seconds calibrated by selected replays only; original full fit/extraction qualified. No economic verdict without a stated reuse horizon and difference interval.",
    )
    return result


def report(out, rows, schedule, builds, p, seed_refs, full_refs, g4):
    expected = {row_key(r): r for r in schedule}
    if (
        len(expected) != len(schedule)
        or len(rows) != len(schedule)
        or len({row_key(r) for r in rows}) != len(rows)
        or any(
            row_key(r) not in expected
            or any(r[k] != v for k, v in expected[row_key(r)].items())
            for r in rows
        )
    ):
        raise ValueError("incomplete/duplicate/changed roster; no efficacy decision")
    seed = {row_key(r): r for r in seed_refs}
    full = {row_key(r): r for r in full_refs}
    combined = []
    for r in rows:
        combined.append(dict(r, method=r["arm"]))
        if r["arm"] == "A8":
            for method, old in [
                ("C4F4", seed[r["corpus"], r["cell"], r["seed"], "F"]),
                ("full_F", full[r["corpus"], r["cell"], r["seed"], "F"]),
                ("full_C", full[r["corpus"], r["cell"], r["seed"], "C"]),
            ]:
                if old["training_indices"] != r["training_indices"] or (
                    "block" in old and old["block"] != r["block"]
                ):
                    raise ValueError("historical case/block pairing changed")
                combined.append(
                    dict(
                        old,
                        block=r["block"],
                        seed_ordinal=r["seed_ordinal"],
                        method=method,
                    )
                )
    primary = contrasts(combined)
    if primary["sigma"]["n"] != 16:
        raise ValueError("primary corpus roster incomplete")
    lo, hi = primary["sigma"]["interval_95"]
    decision = (
        "worthwhile_search_increment"
        if lo > 1.10
        else ("no_worthwhile_search_increment" if hi < 1.10 else "unresolved")
    )
    diagnostics = {}
    for arm in ("A8", "S8"):
        rs = [r for r in rows if r["arm"] == arm]
        stats = {
            k: (
                [
                    sum(r["operator"][k][j] for r in rs)
                    for j in range(len(rs[0]["operator"][k]))
                ]
                if isinstance(rs[0]["operator"][k], list)
                else sum(r["operator"][k] for r in rs)
            )
            for k in rs[0]["operator"]
        }
        stats["tokens_changed_per_edit"] = stats["changed_tokens"] / max(
            1, stats["edited_children"]
        )
        stats["realized_child_fraction"] = stats["edited_children"] / max(
            1, stats["eligible_children"]
        )
        diagnostics[arm] = stats
    n = balanced_target_n(primary["sigma"]["sd_log"], math.log(1.05), 16)
    extra = n - 16
    result = dict(
        complete=True,
        decision=decision,
        next="strategy",
        primary=primary,
        primary_seeds=p["admission"]["selected_seeds"],
        summaries={
            a: describe([r for r in rows if r["arm"] == a]) for a in ("A8", "S8")
        },
        diagnostics=diagnostics,
        reference_summaries={
            m: describe([r for r in combined if r["method"] == m])
            for m in ("C4F4", "full_F", "full_C")
        },
        sensitivity=dict(
            cap_penalty_1=contrasts(combined, penalty=1),
            both_solved=contrasts(combined, both=True),
            families={
                f: contrasts([r for r in combined if r["family"] == f])
                for f in ("BE", "PA")
            },
        ),
        per_block={
            str(b): contrasts([r for r in combined if r["block"] == b], blocks=(b,))
            for b in range(4)
        },
        per_cell={
            c: contrasts([r for r in combined if r["cell"] == c])
            for c in sorted({r["cell"] for r in rows})
        },
        acquisition_diagnostics={
            key: dict(
                yields=b["yields"],
                empty_cells=b["empty_cells"],
                library_size=len(b["library"]["fragments"]),
                gt_fragments=sum(
                    any("gt" in name for name in f["names"])
                    for f in b["library"]["fragments"]
                ),
                acquisition=b["acquisition"],
            )
            for key, b in builds.items()
        },
        economics=economics(combined, builds, p, g4),
        resolution_price=dict(
            target_half_width_factor=1.05,
            scenario_corpora=n,
            additional_independent_corpora=extra,
            additional_independent_acquisitions=4 * extra,
            scoring_queue_seconds=p["admission"]["projected_seconds"] * extra / 16,
            adaptive_collection_queue_seconds=p["admission"]["collection_wall_seconds"]
            * extra
            / 16,
            historical_source_and_full_reference_evaluations=extra
            / 16
            * sum(a["evaluations"] for a in p["full_acquisition"].values()),
            seed_only_caveat="No seed-only resolution guarantee. Independent-corpus scenario assumes observed SD unchanged and needs new static source/full reference acquisition AND scoring; historical source effort is a lower bound on its price.",
            agent_hours=3,
            automatic_extension=False,
        ),
        metric="sigma=exp(mean_corpus(mean_equal_blocks(log(cost_S8)-log(cost_A8)))); failures2cap;95% t df15;worthwhile threshold1.10",
        scope="One externally fitted feedback update on reused development sources/tasks. Decoder/library and yield/content are bundled. Unresolved sigma is not equivalence; search increment and total-cost usefulness are separate. Return to strategy under all outcomes.",
    )
    write_json(out, "result.json", result)
    plots(out, rows, result, arms=("A8", "S8"))
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, units in zip(axes, ("evaluations", "worker_seconds")):
        for method, curve in result["economics"][units]["curves"].items():
            xs = [v["N"] for v in curve]
            ax.plot(xs, [v["cost"] for v in curve], label=method)
            ax.fill_between(
                xs,
                [v["interval_95"][0] for v in curve],
                [v["interval_95"][1] for v in curve],
                alpha=0.10,
            )
        ax.set(
            xscale="symlog",
            yscale="log",
            xlabel="Number of capped fresh searches",
            ylabel=units,
            title="Acquisition + search"
            + (" (qualified)" if units == "worker_seconds" else ""),
        )
        ax.legend()
    fig.tight_layout()
    fig.savefig(out / "cost_curves.png", dpi=150)
    plt.close(fig)
    (out / "report.md").write_text(
        f"Decision: **{decision}**; return to strategy.\n\n"
        + result["metric"]
        + f"\n\nsigma={primary['sigma']['cost_ratio']:.3f},95% [{lo:.3f},{hi:.3f}].\n\n"
        + result["scope"]
        + "\n\nAll seed/full reference contrasts, cap/family/block sensitivities, acquisition yields, fully charged arithmetic curves, paired total-cost difference intervals at stated horizons, crossover directions and resolution scenarios are in result.json.\n"
    )
    return result
