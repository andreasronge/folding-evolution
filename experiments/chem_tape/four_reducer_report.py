"""Fixed-cell paired bootstrap, censored medians and narrow feasibility routing."""

from collections import defaultdict
import numpy as np
from experiments.chem_tape.composition_report import median, bootstrap_medians, interval
from experiments.chem_tape.four_reducer_maps import ARMS


def summaries(rows, draws=2000):
    groups = defaultdict(list)
    for r in rows:
        groups[r["cell"] + "|" + r["arm"]].append(r)
    rng = np.random.default_rng(1603002)
    result = {}
    for key, rs in sorted(groups.items()):
        cap = rs[0]["cap"]
        med = median(rs)
        ci = interval(bootstrap_medians(rs, rng, draws))
        result[key] = dict(
            n=len(rs),
            solves=sum(r["solved"] for r in rs),
            cap=cap,
            km_median=med,
            km_median_label=str(med) if med is not None else f"> {cap}",
            km_median_interval_95=ci,
            km_median_interval_labels=[
                str(v) if v is not None else f"> {cap}" for v in ci
            ],
            mean_seconds=float(np.mean([r["seconds"] for r in rs])),
            capped_fraction=float(np.mean([not r["solved"] for r in rs])),
            solve_curve={
                str(b): sum(r["solved"] and r["evaluations"] <= b for r in rs) / len(rs)
                for b in (4096, 32768, 131072, 524288)
            },
        )
    return result


def contrast(rows, cells, coefficients, draws=2000):
    """Positive coefficient means slower reference; negative means tested map.

    Each fixed cell independently resamples its seed indices, jointly across
    every arm in the linear contrast. Neither cells nor arms are resampled.
    """
    rng = np.random.default_rng(1603002)
    log_point, log_draws = [], np.zeros(draws)
    ns = {}
    for cid in cells:
        groups = {
            a: {r["seed"]: r for r in rows if r["cell"] == cid and r["arm"] == a}
            for a in coefficients
        }
        seeds = sorted(set.intersection(*(set(g) for g in groups.values())))
        ns[cid] = len(seeds)
        if not seeds:
            return dict(
                ratio=None, interval_95=[None, None], paired_seeds=ns, complete=False
            )
        x = sum(
            weight
            * np.log2(
                [min(groups[a][s]["evaluations"], groups[a][s]["cap"]) for s in seeds]
            )
            for a, weight in coefficients.items()
        )
        log_point.append(float(np.mean(x)))
        idx = rng.integers(len(seeds), size=(draws, len(seeds)))
        log_draws += np.mean(x[idx], axis=1) / len(cells)
    return dict(
        ratio=float(2 ** np.mean(log_point)),
        interval_95=interval(2**log_draws),
        paired_seeds=ns,
        coefficients=coefficients,
        scope="geometric mean of paired capped-time speed ratios; cells fixed",
        complete=True,
    )


def witness(rows, cells, matched, swapped):
    c = contrast(rows, cells, {swapped: 1, matched: -1})
    arms = [r for r in rows if r["cell"] in cells and r["arm"] in (matched, swapped)]
    capped = {
        a: float(np.mean([not r["solved"] for r in arms if r["arm"] == a]))
        if any(r["arm"] == a for r in arms)
        else None
        for a in (matched, swapped)
    }
    low, high = c["interval_95"]
    c.update(
        capped_fractions=capped,
        reading="W"
        if low is not None and low > 1
        else "C"
        if any(v is not None and v > 0.25 for v in capped.values())
        else "B"
        if high is not None and high < 1.25
        else "X",
    )
    c["large"] = c["reading"] == "W" and c["ratio"] >= 1.5
    return c


def gates(bank, splits, summary):
    if not all(splits.values()):
        return dict(split=False, headroom=None, tractability=None)
    holds = [c for s in splits.values() for c in s["holdouts"]]
    counts = {
        a: sum(
            summary[c + "|" + a]["km_median"] is None
            or summary[c + "|" + a]["km_median"] >= 4096
            for c in holds
        )
        for a in ("F4", "G4", "G4-marg")
    }
    train = [c for s in splits.values() for c in s["training"]]
    tractable = all(
        summary[c + "|G4"]["solves"] >= 35
        and summary[c + "|G4"]["km_median"] is not None
        and summary[c + "|G4"]["km_median"] <= 65536
        for c in train
    )
    return dict(
        split=True,
        headroom=all(n >= 3 for n in counts.values()),
        holdouts_passing_4096=counts,
        tractability=tractable,
    )


def report(screens, bank, rows, b_complete, c_started, c_complete, pilot, cost):
    # Completeness is checked on unique seed IDs, not merely a scheduling flag.
    b_complete = b_complete and all(
        len([r for r in rows if r["cell"] == c["id"] and r["arm"] == a]) == 50
        and {r["seed"] for r in rows if r["cell"] == c["id"] and r["arm"] == a}
        == set(range(1603100, 1603150))
        for c in bank
        for a in ARMS
    )
    summary = summaries(rows)
    splits = {
        f: screens.get("D1331", {}).get("obstacles", {}).get(f, {}).get("split")
        for f in ("BE", "PA")
    }
    gs = gates(bank, splits, summary) if b_complete else dict(split=None)
    families = {}
    for f in ("BE", "PA"):
        cs = [c["id"] for c in bank if c["shape"] == f]
        if not cs:
            continue
        matched = "G4-" + f
        swapped = "G4-" + ("PA" if f == "BE" else "BE")
        families[f] = dict(
            grammar=witness(rows, cs, matched, swapped),
            marginal=witness(rows, cs, matched + "-marg", swapped + "-marg"),
            context_over_marginal=contrast(
                rows,
                cs,
                {swapped: 1, matched: -1, swapped + "-marg": -1, matched + "-marg": 1},
            ),
            matched_over_G4=contrast(rows, cs, {"G4": 1, matched: -1}),
            controls={
                x + "/" + y: contrast(rows, cs, {y: 1, x: -1})
                for x, y in (("G4", "U"), ("F4", "U"), ("G4", "G4-marg"))
            },
            censoring={
                a: float(
                    np.mean(
                        [
                            not r["solved"]
                            for r in rows
                            if r["cell"] in cs and r["arm"] == a
                        ]
                    )
                )
                if any(r["cell"] in cs and r["arm"] == a for r in rows)
                else None
                for a in ARMS
            },
        )
    outcome = "U"
    if (
        all(s.get("complete") for s in screens.values())
        and len(screens) == 3
        and b_complete
    ):
        if c_started and not c_complete:
            outcome = "U"
        elif not gs["split"]:
            outcome = "1"
        elif not gs["headroom"]:
            outcome = "2"
        elif not gs["tractability"] or not cost.get("fits", False):
            outcome = "3"
        elif c_complete:
            outcome = (
                "4"
                if all(
                    any(
                        v["gain"]["interval_95"][0] > 1
                        for v in pilot.values()
                        if v["family"] == f
                    )
                    for f in ("BE", "PA")
                )
                else "5"
            )
    return dict(
        outcome=outcome,
        per_cell_arm=summary,
        families=families,
        gates=gs,
        splits=splits,
        cost=cost,
        pilot=pilot,
        per_cell_control_ratios={
            c["id"]: {
                x + "/" + y: contrast(rows, [c["id"]], {y: 1, x: -1})
                for x, y in (("G4", "U"), ("F4", "U"), ("G4", "G4-marg"))
            }
            for c in bank
        },
        interpretation="Split failure rejects only this candidate. Headroom failure means "
        "failure of the frozen 4096 rule. No negative capacity inference. A W reading "
        "in one family is a matched-prior advantage there; crossed preference requires "
        "W in both. Context attribution requires the directly paired contrast. "
        "All intervals are descriptive; incomplete search remains unresolved.",
    )


def plots(out, bank, result):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for f, ax in zip(("BE", "PA"), axes):
        for a in ARMS:
            curves = [
                result["per_cell_arm"][c["id"] + "|" + a]["solve_curve"]
                for c in bank
                if c["shape"] == f and c["id"] + "|" + a in result["per_cell_arm"]
            ]
            if curves:
                ax.plot(
                    [4096, 32768, 131072, 524288],
                    np.mean(
                        [
                            [v[str(b)] for b in (4096, 32768, 131072, 524288)]
                            for v in curves
                        ],
                        axis=0,
                    ),
                    label=a,
                )
        ax.set(
            xscale="log",
            ylim=(0, 1),
            title=f,
            xlabel="Evaluations",
            ylabel="Solved fraction",
        )
    if axes[0].lines:
        axes[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "curves.png")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4))
    i = 0
    for f, v in result["families"].items():
        for name in ("grammar", "marginal", "context_over_marginal", "matched_over_G4"):
            c = v[name]
            lo, hi = c["interval_95"]
            if lo is not None:
                ax.errorbar(
                    c["ratio"], i, xerr=[[c["ratio"] - lo], [hi - c["ratio"]]], fmt="o"
                )
                ax.text(hi * 1.01, i, f + " " + name, fontsize=8)
                i += 1
    ax.axvline(1, color="gray")
    ax.set(xscale="log", xlabel="Paired capped-time ratio", yticks=[])
    fig.tight_layout()
    fig.savefig(out / "contrasts.png")
    plt.close(fig)
