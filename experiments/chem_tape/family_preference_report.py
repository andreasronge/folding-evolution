"""Fixed-cell interaction with independent acquisition cohorts and shared seeds."""

import json
import numpy as np
from scipy.stats import t

from experiments.chem_tape.composition_run import write_json

ARMS = ("G4", "D", "T")


def arrays(rows, B, penalty=2):
    cells = {
        f: sorted({r["cell"] for r in rows if r["family"] == f}) for f in ("DG", "TS")
    }
    by = {(r["family"], r["cell"], r["arm"], r["ordinal"]): r for r in rows}
    expected = {
        (f, c, a, i)
        for f in cells
        for c in cells[f]
        for a in ARMS
        for i in range(2 * B)
    }
    if len(by) != len(rows) or set(by) != expected:
        raise ValueError("incomplete/duplicate crossed roster")
    for (f, c, a, i), r in by.items():
        if r["build"] != i // 2 or any(
            by[f, c, other, i]["seed"] != r["seed"] for other in ARMS
        ):
            raise ValueError("build/ordinal/common seed assignment changed")
    values = {
        f: {
            a: np.array(
                [
                    [
                        np.log(r["evaluations"] if r["solved"] else penalty * r["cap"])
                        for i in range(2 * B)
                        for r in [by[f, c, a, i]]
                    ]
                    for c in cells[f]
                ]
            )
            for a in ARMS
        }
        for f in cells
    }
    return cells, values


def classify(ratios):
    pd, pt, interaction = [ratios[k]["interval95"] for k in ("P_DG", "P_TS", "I")]
    label = (
        "material geometric family interaction"
        if interaction[0] > 1.5
        else (
            "geometric interaction below1.5 margin"
            if interaction[1] < 1.5
            else "unresolved interaction"
        )
    )
    reciprocal = pd[0] > 1 and pt[0] > 1
    dominates = (
        "D" if pd[0] > 1 and pt[1] < 1 else ("T" if pd[1] < 1 and pt[0] > 1 else None)
    )
    directions = {
        k: (
            "matched preference"
            if ratios[k]["interval95"][0] > 1
            else "mismatched preference"
            if ratios[k]["interval95"][1] < 1
            else "unresolved direction"
        )
        for k in ("P_DG", "P_TS")
    }
    useful = (
        ratios["G4/D_DG"]["interval95"][0] > 1
        and ratios["G4/T_TS"]["interval95"][0] > 1
    )
    shared = all(
        ratios[f"G4/{a}_{f}"]["interval95"][0] > 1.5
        for a in ("D", "T")
        for f in ("DG", "TS")
    )
    return dict(
        interaction=label,
        directions=directions,
        reciprocal=reciprocal,
        dominant_bias=dominates,
        dominant_bias_with_interaction=dominates is not None and interaction[0] > 1.5,
        own_family_useful=useful,
        family_specific_acquisition_candidate=reciprocal
        and useful
        and interaction[0] > 1.5,
        shared_bias_candidate=shared and interaction[1] < 1.5,
        next="strategy",
    )


def summarize(rows, B, penalty=2, draws=8192):
    cells, values = arrays(rows, B, penalty)
    keys = ["P_DG", "P_TS", "I"] + [
        f"G4/{a}_{f}" for f in ("DG", "TS") for a in ("D", "T")
    ]

    def contrasts(means):
        d = means["DG"]["T"] - means["DG"]["D"]
        s = means["TS"]["D"] - means["TS"]["T"]
        return [d, s, (d + s) / 2] + [
            means[f]["G4"] - means[f][a] for f in ("DG", "TS") for a in ("D", "T")
        ]

    point = contrasts(
        {f: {a: v.mean() for a, v in arms.items()} for f, arms in values.items()}
    )
    rng = np.random.default_rng(1717000)
    boot = np.empty((draws, len(keys)))
    for k in range(draws):
        selected = {a: rng.integers(B, size=B) for a in ("D", "T")}
        means = {}
        for f, arms in values.items():
            n = len(cells[f])
            means[f] = {}
            gi = rng.integers(2 * B, size=(n, 2 * B))
            means[f]["G4"] = np.take_along_axis(arms["G4"], gi, axis=1).mean()
            # One two-seed draw per original build x cell shared by D/T; independent
            # acquisition resamples select these rows, retaining both rosters.
            offsets = rng.integers(2, size=(n, B, 2))
            for a in ("D", "T"):
                ix = 2 * selected[a][None, :, None] + offsets[:, selected[a], :]
                means[f][a] = np.take_along_axis(
                    arms[a], ix.reshape(n, -1), axis=1
                ).mean()
        boot[k] = contrasts(means)
    ratios = {
        key: dict(
            point=float(np.exp(point[i])),
            interval95=np.exp(np.quantile(boot[:, i], [0.025, 0.975])).tolist(),
        )
        for i, key in enumerate(keys)
    }
    build_contrasts = {
        a: (
            values["DG"][a].reshape(len(cells["DG"]), B, 2).mean(axis=(0, 2))
            - values["TS"][a].reshape(len(cells["TS"]), B, 2).mean(axis=(0, 2))
        ).tolist()
        for a in ("D", "T")
    }
    return dict(
        ratios=ratios,
        decision=classify(ratios),
        failure_penalty=penalty,
        bootstrap=dict(
            draws=draws,
            seed=1717000,
            unit="independent acquisition builds within D and T; selected builds keep both rosters",
            cells="fixed",
            seeds="two common ordinal offsets resampled jointly within original build x cell",
            G4="one shared cell-stratified baseline resample per draw; never duplicate baseline rows",
        ),
        build_cross_roster_log_costs=build_contrasts,
        per_cell={
            f: {
                c: {
                    a: dict(
                        geometric_cost=float(np.exp(values[f][a][i].mean())),
                        solved=sum(
                            r["solved"]
                            for r in rows
                            if r["cell"] == c and r["arm"] == a
                        ),
                        attempts=2 * B,
                    )
                    for a in ARMS
                }
                for i, c in enumerate(cs)
            }
            for f, cs in cells.items()
        },
        per_build={
            a: {
                str(b): {
                    f: float(np.exp(values[f][a][:, 2 * b : 2 * b + 2].mean()))
                    for f in cells
                }
                for b in range(B)
            }
            for a in ("D", "T")
        },
        solves={
            f: {
                a: dict(
                    solved=sum(
                        r["solved"] for r in rows if r["family"] == f and r["arm"] == a
                    ),
                    attempts=sum(r["family"] == f and r["arm"] == a for r in rows),
                )
                for a in ARMS
            }
            for f in cells
        },
    )


def economics(rows, builds, intermediate):
    result = {}
    for a, cohort in builds.items():
        deployed = {}
        for b, record in cohort.items():
            final = record["acquisition"]
            inter = intermediate[a][b]["acquisition"]
            acq = dict(
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
            # Smoke may deploy only first2 DG builds, but the frozen cohort remains24.
            if not any(r["arm"] == a and r["build"] == int(b) for r in rows):
                continue
            rosters = {}
            for f in ("DG", "TS", "both"):
                rs = [
                    r
                    for r in rows
                    if r["arm"] == a
                    and r["build"] == int(b)
                    and (f == "both" or r["family"] == f)
                ]
                keys = {(r["cell"], r["seed"]) for r in rs}
                g = [
                    r
                    for r in rows
                    if r["arm"] == "G4" and (r["cell"], r["seed"]) in keys
                ]
                savings = np.mean([r["evaluations"] for r in g]) - np.mean(
                    [r["evaluations"] for r in rs]
                )
                time_saving = np.mean([r["seconds"] for r in g]) - np.mean(
                    [r["seconds"] for r in rs]
                )
                rosters[f] = dict(
                    searches=len(rs),
                    acquisition_plus_search_evaluations=acq["evaluations"]
                    + sum(r["evaluations"] for r in rs),
                    G4_evaluations=sum(r["evaluations"] for r in g),
                    mean_saving_evaluations=float(savings),
                    repayment_searches=float(acq["evaluations"] / savings)
                    if savings > 0
                    else None,
                    acquisition_plus_search_worker_seconds=acq["worker_seconds"]
                    + sum(r["seconds"] for r in rs),
                    G4_worker_seconds=sum(r["seconds"] for r in g),
                    mean_worker_seconds_saving=float(time_saving),
                )
            deployed[b] = dict(acquisition=acq, rosters=rosters)
        result[a] = deployed
    return dict(
        per_deployed_build=result,
        scope="arithmetic actual effort; acquisition once/build per deployment scenario; failures actual cap, not penalty; DG sunk for execution, charged for deployment; measured worker times are not wall-time speedups",
    )


def resolution_price(rows, summary, builds, intermediate, timing):
    B = len(summary["build_cross_roster_log_costs"]["D"])
    variance = (
        sum(
            np.var(summary["build_cross_roster_log_costs"][a], ddof=1)
            for a in ("D", "T")
        )
        / 4
    )
    gap = abs(np.log(summary["ratios"]["I"]["point"] / 1.5))
    needed = None
    for n in range(B, 513):
        if gap > 0 and t.ppf(0.975, n - 1) * np.sqrt(variance / n) < gap:
            needed = n
            break
    acq = {
        a: np.mean(
            [
                r["acquisition"]["source_worker_seconds"]
                + sum(
                    r["acquisition"][k] + intermediate[a][b]["acquisition"][k]
                    for k in (
                        "verification_seconds",
                        "fit_seconds",
                        "extraction_seconds",
                    )
                )
                for b, r in cohort.items()
            ]
        )
        for a, cohort in builds.items()
    }
    means = {a: np.mean([r["seconds"] for r in rows if r["arm"] == a]) for a in ARMS}
    total = (
        None
        if needed is None
        else needed * sum(acq.values()) + 32 * needed * sum(means.values())
    )
    return dict(
        conditional_total_builds_per_cohort=needed,
        builds_examined_to=512,
        worker_seconds=None if total is None else float(total),
        projected_minutes_with30percent_reserve=None
        if total is None
        else float(1.3 * total / timing["effective_workers"] / 60),
        caveat="planning approximation from observed between-build cross-roster variance; inner-seed uncertainty not separately priced, not guaranteed resolution or authorized enlargement",
    )


def plot(out, rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for fi, f in enumerate(("DG", "TS")):
        for a in ARMS:
            rs = [r for r in rows if r["family"] == f and r["arm"] == a]
            cap = max(r["cap"] for r in rs)
            grid = sorted({p[0] for r in rs for p in r["curve"]} | {cap})
            for column, title in (
                (1, "best correct cases"),
                (2, "distinct correctness patterns"),
            ):
                means = []
                for budget in grid:
                    points = [
                        ([p for p in r["curve"] if p[0] <= budget] or r["curve"][:1])[
                            -1
                        ][column]
                        for r in rs
                    ]
                    means.append(np.mean(points))
                ax = axes[fi, column - 1]
                ax.plot(grid, means, label=a)
                ax.set_title(f"{f}: {title}")
                ax.set_xlabel("evaluations")
                ax.set_xscale("log")
                ax.legend()
            axes[fi, 2].scatter(
                [r["evaluations"] for r in rs],
                [r["exact_check_seconds"] for r in rs],
                label=a,
                alpha=0.4,
                s=8,
            )
        axes[fi, 2].set_title(f"{f}: exact verification")
        axes[fi, 2].set_xlabel("evaluations")
        axes[fi, 2].set_ylabel("seconds")
        axes[fi, 2].legend()
    fig.tight_layout()
    fig.savefig(out / "dynamics.png", dpi=130)
    plt.close(fig)


def report(out, rows, builds, intermediate, prep, timing, smoke=False):
    B = 2 if smoke else 24
    two = summarize(rows, B)
    one = summarize(rows, B, penalty=1)
    result = dict(
        status="smoke" if smoke else "crossed_comparison_complete",
        summary=two,
        one_cap=one,
        penalty_sensitive=two["decision"] != one["decision"],
        economics=economics(rows, builds, intermediate),
        resolution_price=resolution_price(rows, two, builds, intermediate, timing),
        timing=timing,
        preparation=prep,
        target_performance_scored=not smoke,
        scope="external fitting and literal fragments on fixed same-alphabet rosters; DG development bank; no inheritance, competitive-baseline, pure ADD-placement or broad fresh-bank claim",
    )
    write_json(out, "result.json", result)
    lines = [
        "# Same-alphabet crossed family preference",
        "",
        "SMOKE ONLY: development cells."
        if smoke
        else "Fixed DG spare and TS target rosters; return to strategy.",
        "",
        "|Capped-cost contrast|Point|95% build/seed interval|",
        "|---|---:|---:|",
    ]
    for key, r in two["ratios"].items():
        lines.append(
            f"|{key}|{r['point']:.3f}|[{r['interval95'][0]:.3f}, {r['interval95'][1]:.3f}]|"
        )
    lines += [
        "",
        json.dumps(two["decision"], indent=2),
        "",
        f"Penalty-sensitive: {result['penalty_sensitive']}.",
        "",
        "Only a constant multiplicative advantage cancels from I. Unresolved directions remain unresolved; exclude only interaction above the1.5 margin. Own-family usefulness and directions accompany the interaction.",
        "",
        f"Solves: {two['solves']}",
        "",
        result["scope"],
        "",
        "Per-cell/build costs, retained fallbacks, acquisition economics and a conditional resolution price are in result.json/builds.json/preparation.json. No arithmetic saving means no demonstrated break-even.",
        "",
        "Closest precedents: [PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/) and [Wild & Porter (2022)](https://eprints.lancs.ac.uk/id/eprint/174982/?template=browse).",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    plot(out, rows)
