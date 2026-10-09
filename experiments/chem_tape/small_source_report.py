"""1743 corpus-clustered retention and explicitly priced capped search policies."""

from collections import defaultdict
import math

import numpy as np

from experiments.chem_tape.comparison_gate_report import (
    interval,
    describe,
    balanced_target_n,
)
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.fragment_report import row_key, plots
from experiments.chem_tape.solver_corpus_report import cost


def contrast(rows, numerator, denominator, penalty=2, both=False, blocks=(0, 1, 2, 3)):
    """Cost ratio numerator/denominator; average cells/seeds then equal blocks."""
    indexed = {(r["corpus"], r["cell"], r["seed"], r["method"]): r for r in rows}
    groups = defaultdict(list)
    for r in rows:
        if r["method"] != denominator:
            continue
        mate = indexed[r["corpus"], r["cell"], r["seed"], numerator]
        if both and not (mate["solved"] and r["solved"]):
            continue
        groups[r["corpus"], r["block"]].append(
            np.log(cost(mate, penalty)) - np.log(cost(r, penalty))
        )
    by = defaultdict(dict)
    for (tid, b), vals in groups.items():
        by[tid][b] = float(np.mean(vals))
    # Empty both-solved blocks are missing, never imputed as no difference.
    all_corpora = {r["corpus"] for r in rows}
    for tid in all_corpora:
        by.setdefault(tid, {})
    complete = {tid: bs for tid, bs in by.items() if len(bs) == len(blocks)}
    result = interval(
        [np.mean(list(complete[tid].values())) for tid in sorted(complete)]
    )
    result.update(
        cost_ratio=result.pop("speed_ratio"),
        numerator=numerator,
        denominator=denominator,
        corpora=sorted(complete),
        corpus_block_log_means=dict(by),
        eligible_pairs=sum(map(len, groups.values())),
        missing_blocks={
            tid: [b for b in blocks if b not in bs]
            for tid, bs in by.items()
            if len(bs) < len(blocks)
        },
        interpretation="equal-block cost ratio; >1 numerator costs more; both-solved may omit corpora with empty blocks",
    )
    return result


def all_contrasts(rows, **kwargs):
    return {
        name: contrast(rows, a, b, **kwargs)
        for name, a, b in (
            ("rho", "full_F", "cheap_F"),
            ("F4_speed_over_W4", "cheap_W", "cheap_F"),
            ("W4_cost_over_full_W", "cheap_W", "full_W"),
        )
    }


def economics(rows, builds, preparation, g4):
    tids = sorted({r["corpus"] for r in rows})
    methods = ("cheap_F", "cheap_W", "full_F", "G4")
    calibration = preparation["validation"]["historical_replay"]["calibration"]
    price = {}
    for units in ("evaluations", "worker_seconds"):
        acquisitions = {m: [] for m in methods}
        searches = {m: [] for m in methods}
        reliability = {m: [] for m in methods}
        for tid in tids:
            blocks = [builds[f"{tid}|{b}"]["acquisition"] for b in range(4)]
            full = preparation["full_acquisition"][tid]

            def acquisition(a):
                if units == "evaluations":
                    return a["evaluations"]
                return a["source_worker_seconds"] * calibration["G4"] + sum(
                    a.get(k, 0)
                    for k in (
                        "verification_seconds",
                        "fit_seconds",
                        "extraction_seconds",
                    )
                )

            cheap = float(np.mean([acquisition(a) for a in blocks]))
            acquisitions["cheap_F"].append(cheap)
            acquisitions["cheap_W"].append(
                cheap
            )  # W4 pays extraction of its length law.
            acquisitions["full_F"].append(acquisition(full))
            acquisitions["G4"].append(0.0)
            for method in methods:
                rs = (
                    g4
                    if method == "G4"
                    else [
                        r for r in rows if r["corpus"] == tid and r["method"] == method
                    ]
                )
                factor = (
                    calibration["G4" if method == "G4" else "F"]
                    if method in ("full_F", "G4")
                    else 1.0
                )

                def value(r):
                    return (
                        r["evaluations"]
                        if units == "evaluations"
                        else r["seconds"] * factor
                    )

                searches[method].append(float(np.mean([value(r) for r in rs])))
                reliability[method].append(float(np.mean([r["solved"] for r in rs])))
        A = {m: np.asarray(v) for m, v in acquisitions.items()}
        S = {m: np.asarray(v) for m, v in searches.items()}
        rng = np.random.default_rng(1743)
        # Resample whole corpus records; retain acquisition/search dependence.
        indices = np.column_stack(
            [
                rng.choice(
                    [i for i, t in enumerate(tids) if t.startswith(f)], size=(4096, 8)
                )
                for f in ("BE", "PA")
            ]
        )
        Ab = {m: A[m][indices].mean(1) for m in methods}
        Sb = {m: S[m][indices].mean(1) for m in methods}
        gvalues = np.array(
            [
                r["evaluations"]
                if units == "evaluations"
                else r["seconds"] * calibration["G4"]
                for r in g4
            ]
        )
        Sb["G4"] = gvalues[rng.integers(len(g4), size=(4096, len(g4)))].mean(1)
        horizons = [0, 1, 4, 16, 64, 256, 1024, 4096]
        curves = {
            m: [
                dict(
                    N=n,
                    cost=float(A[m].mean() + n * S[m].mean()),
                    interval_95=np.quantile(Ab[m] + n * Sb[m], [0.025, 0.975]).tolist(),
                )
                for n in horizons
            ]
            for m in methods
        }
        comparisons = {}
        for x, y in (
            ("cheap_F", "full_F"),
            ("cheap_F", "G4"),
            ("cheap_W", "full_F"),
            ("cheap_W", "G4"),
        ):
            dA = A[x].mean() - A[y].mean()
            saving = S[y].mean() - S[x].mean()
            root = float(dA / saving) if saving and dA / saving > 0 else None
            bsaving = Sb[y] - Sb[x]
            broot = np.divide(
                Ab[x] - Ab[y], bsaving, out=np.full(4096, np.nan), where=bsaving != 0
            )
            good = broot[np.isfinite(broot) & (broot > 0)]
            comparisons[x + "_vs_" + y] = dict(
                initial_acquisition_difference=float(dA),
                arithmetic_search_saving=float(saving),
                positive_long_run_saving=bool(saving > 0),
                crossover_N=root,
                crossover_direction=(
                    "cheap_wins_after" if saving > 0 else "cheap_loses_after"
                )
                if root
                else None,
                positive_crossover_bootstrap_fraction=len(good) / 4096,
                positive_crossover_interval_95=np.quantile(
                    good, [0.025, 0.975]
                ).tolist()
                if len(good)
                else None,
                no_positive_crossover_fraction=1 - len(good) / 4096,
                initially_cheaper=bool(dA < 0),
                eventually_cheaper=bool(saving > 0),
            )
        price[units] = dict(
            arithmetic_means={
                m: dict(
                    A=float(A[m].mean()),
                    S=float(S[m].mean()),
                    solve_probability=float(np.mean(reliability[m])),
                )
                for m in methods
            },
            corpus_acquisition_search={
                m: dict(A=A[m].tolist(), S=S[m].tolist()) for m in methods
            },
            curves=curves,
            comparisons=comparisons,
        )
    price.update(
        bootstrap_seed=1743,
        bootstrap_replicates=4096,
        accounting="One acquisition per deployed method; equal average over4 disjoint replicate builds per corpus. W4 pays verification/fit/extraction. Corpus bootstrap preserves shared acquisition/search dependence; unpaired G4 additionally resampled.",
        seconds_caveat="Historical source and G4 search times scaled by same-hardware G4 replay; full F search by F replay. Calibration uses selected workloads and cannot guarantee hardware-invariant comparisons. Historical full fit/extraction retained at recorded worker times, qualified, not separately calibrated. Full extraction is a pooled overhead allocated equally to corpora; its corpus variability is unavailable.",
        evaluations_caveat="Evaluation curves count source/search evaluations only; fit/extraction have no evaluation-unit equivalent. Full economic accounting including verification/fit/extraction is in worker_seconds. Capped effort is not uncapped expected time to solve.",
    )
    return price


def report(out, rows, schedule, builds, preparation, reference, g4):
    expected = {row_key(r): r for r in schedule}
    if (
        len(expected) != len(schedule)
        or len(rows) != len(schedule)
        or len({row_key(r) for r in rows}) != len(rows)
    ):
        raise ValueError("incomplete/duplicate roster; no efficacy decision")
    if any(
        row_key(r) not in expected
        or any(r[k] != v for k, v in expected[row_key(r)].items())
        for r in rows
    ):
        raise ValueError("roster metadata changed")
    original = {row_key(r): r for r in reference}
    combined = []
    for r in rows:
        combined.append(dict(r, method="cheap_" + r["arm"]))
        if r["arm"] == "F":
            for arm in ("F", "W", "C"):
                old = original[r["corpus"], r["cell"], r["seed"], arm]
                if old["training_indices"] != r["training_indices"]:
                    raise ValueError("historical cases no longer paired")
                combined.append(
                    dict(
                        old,
                        block=r["block"],
                        seed_ordinal=r["seed_ordinal"],
                        method="full_" + arm,
                    )
                )
    primary = all_contrasts(combined)
    if primary["rho"]["n"] != 16:
        raise ValueError("primary corpus roster incomplete")
    lo, hi = primary["rho"]["interval_95"]
    decision = (
        "retained" if lo > 0.833 else ("tight_loss" if hi < 0.833 else "unresolved")
    )
    diagnostics = {}
    for arm in ("F", "W"):
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
        occurrences = []
        for r in rs:
            if r["solved"]:
                fragments = builds[f"{r['corpus']}|{r['block']}"]["library"][
                    "fragments"
                ]
                occurrences.append(
                    sum(
                        r["solver"][s : s + len(f["tokens"])] == f["tokens"]
                        for f in fragments
                        for s in range(33 - len(f["tokens"]))
                    )
                )
        stats["solver_library_share"] = (
            sum(n > 0 for n in occurrences) / len(occurrences) if occurrences else None
        )
        diagnostics[arm] = stats
    summaries = {
        arm: describe([r for r in rows if r["arm"] == arm]) for arm in ("F", "W")
    }

    def unpaired(rs):
        by = defaultdict(list)
        for r in rs:
            if r["method"] == "cheap_F":
                by[r["corpus"]].append(np.log(cost(r)))
        base = float(np.mean([np.log(cost(r)) for r in g4]))
        rng = np.random.default_rng(1743)
        means = np.array([np.mean(by[tid]) for tid in sorted(by)])
        base_values = np.array([np.log(cost(r)) for r in g4])
        samples = np.exp(
            means[rng.integers(len(means), size=(4096, len(means)))].mean(1)
            - base_values[rng.integers(len(g4), size=(4096, len(g4)))].mean(1)
        )
        return dict(
            cost_ratio_cheap_F_over_G4=float(
                np.exp(np.mean([np.mean(v) for v in by.values()]) - base)
            ),
            G4=describe(g4),
            paired=False,
            interval_95=np.quantile(samples, [0.025, 0.975]).tolist(),
            caveat="corpus bootstrap plus independent resampling of unpaired256-search G4; fixed cells",
        )

    per_block = {str(b): {} for b in range(4)}
    for b in range(4):
        # A block-specific interval clusters its paired log costs by corpus.
        rs = [r for r in combined if r["block"] == b]
        idx = {(r["corpus"], r["cell"], r["seed"], r["method"]): r for r in rs}
        by = defaultdict(list)
        for r in rs:
            if r["method"] == "cheap_F":
                mate = idx[r["corpus"], r["cell"], r["seed"], "full_F"]
                by[r["corpus"]].append(np.log(cost(mate)) - np.log(cost(r)))
        per_block[str(b)] = dict(
            comparisons=all_contrasts(rs, blocks=(b,)),
            retention=interval([np.mean(by[t]) for t in sorted(by)]),
            summaries={
                m: describe([r for r in rs if r["method"] == m])
                for m in ("cheap_F", "cheap_W", "full_F")
            },
        )
    n = balanced_target_n(primary["rho"]["sd_log"], math.log(1.05), 16)
    extra = n - 16
    result = dict(
        complete=True,
        decision=decision,
        next="strategy",
        primary_seeds=preparation["admission"]["selected_seeds"],
        primary=primary,
        summaries=summaries,
        diagnostics=diagnostics,
        reference_summaries={
            m: describe([r for r in combined if r["method"] == m])
            for m in ("full_F", "full_W", "full_C")
        },
        sensitivity=dict(
            cap_penalty_1=all_contrasts(combined, penalty=1),
            both_solved=all_contrasts(combined, both=True),
            families={
                f: all_contrasts([r for r in combined if r["family"] == f])
                for f in ("BE", "PA")
            },
        ),
        per_block=per_block,
        per_cell={
            cid: all_contrasts([r for r in combined if r["cell"] == cid])
            for cid in sorted({r["cell"] for r in combined})
        },
        G4_comparison=unpaired(combined),
        acquisition_diagnostics={
            key: dict(
                yields=r["yields"],
                empty_cells=r["empty_cells"],
                library_size=len(r["library"]["fragments"]),
                library_fallback=not bool(r["library"]["fragments"]),
                gt_fragments=sum(
                    any("gt" in name for name in f["names"])
                    for f in r["library"]["fragments"]
                ),
                gt_joins=sum(
                    sum("gt" in name for name in f["names"])
                    for f in r["library"]["fragments"]
                ),
                acquisition=r["acquisition"],
            )
            for key, r in builds.items()
        },
        economics=economics(combined, builds, preparation, g4),
        resolution_price=dict(
            target_half_width_factor=1.05,
            scenario_corpora=n,
            additional_independent_corpora=extra,
            additional_independent_acquisitions=4 * extra,
            scoring_queue_seconds=preparation["admission"]["projected_seconds"]
            * extra
            / 16,
            acquisition_queue_seconds=1.15
            * extra
            / 10
            * sum(
                sum(
                    builds[f"{tid}|{b}"]["acquisition"].get(k, 0)
                    for k in (
                        "source_worker_seconds",
                        "verification_seconds",
                        "fit_seconds",
                        "extraction_seconds",
                    )
                )
                for tid in sorted({r["corpus"] for r in rows})
                for b in range(4)
            )
            / 16,
            seed_only_caveat="No seed-only resolution guarantee: scoring seeds cannot remove between-acquisition/corpus variability. New corpus scenario assumes observed SD unchanged; repeat full reference acquisition and scoring would add cost.",
            agent_hours=3,
            automatic_extension=False,
        ),
        metric="rho=exp(mean_corpus(mean_equal_blocks(log(cost_full_F)-log(cost_cheap_F)))); 95% t interval df15; failures2cap; threshold0.833",
        scope="Reused development sources/tasks, external fitting. Aggregate retention does not guarantee individual acquisitions. W4 still acquires library-derived lengths. No bare-C4 rescue, inherited map evolution or fresh-bank transfer claim.",
    )
    write_json(out, "result.json", result)
    plots(out, rows, result, arms=("F", "W"))
    (out / "report.md").write_text(
        f"Decision: **{decision}**; return to strategy.\n\n"
        + result["metric"]
        + f"\n\nrho={primary['rho']['cost_ratio']:.3f}, 95% interval [{lo:.3f}, {hi:.3f}].\n\n"
        + result["scope"]
        + "\n\nArithmetic A+N*S curves and paired corpus-bootstrap crossover ranges (including initial wins followed by long-run losses), capped reliability, block/cell/family diagnostics and resolution scenarios are in result.json. Worker-time comparisons are calibrated on selected replay workloads and remain qualified; evaluation curves exclude non-evaluation overhead. W4 pays library extraction.\n"
    )
    # Standalone economic curves, in the fully charged but qualified worker-time units.
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    for method, curve in result["economics"]["worker_seconds"]["curves"].items():
        xs = [r["N"] for r in curve]
        ys = [r["cost"] for r in curve]
        ax.plot(xs, ys, label=method)
        ax.fill_between(
            xs,
            [r["interval_95"][0] for r in curve],
            [r["interval_95"][1] for r in curve],
            alpha=0.12,
        )
    ax.set(
        xscale="symlog",
        yscale="log",
        xlabel="Number of capped fresh searches",
        ylabel="Acquisition + search worker seconds (qualified)",
        title="One acquisition per deployed pipeline",
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "cost_curves.png", dpi=150)
    plt.close(fig)
    return result
