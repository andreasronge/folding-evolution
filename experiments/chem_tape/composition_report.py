"""Pre-stated censored summaries, split rules, and experiment-two projections."""

from __future__ import annotations

import itertools
import math

import numpy as np
from scipy.stats import beta

from experiments.chem_tape.composition_bank import PAIRS
from experiments.chem_tape.composition_search import ARMS

CAP = 524288
BUDGETS = (32768, 65536, 131072)


def median(rows):
    if not rows:
        return None
    solved = sorted(r["evaluations"] for r in rows if r["solved"])
    position = math.ceil(len(rows) / 2) - 1
    return solved[position] if len(solved) > position else None


def bootstrap_medians(rows, rng, n=2000):
    if not rows:
        return np.full(n, np.inf)
    times = np.array([r["evaluations"] if r["solved"] else np.inf for r in rows])
    samples = times[rng.integers(len(rows), size=(n, len(rows)))]
    return np.sort(samples, axis=1)[:, math.ceil(len(rows) / 2) - 1]


def interval(values):
    # Order statistics avoid interpolating finite and infinite censoring tails.
    ordered = np.sort(values)
    limits = ordered[
        [int(0.025 * (len(ordered) - 1)), math.ceil(0.975 * (len(ordered) - 1))]
    ]
    return [float(v) if np.isfinite(v) else None for v in limits]


def count_interval(hits, n):
    return (
        [
            0.0 if hits == 0 else float(beta.ppf(0.025, hits, n - hits + 1)),
            1.0 if hits == n else float(beta.ppf(0.975, hits + 1, n - hits)),
        ]
        if n
        else [None, None]
    )


def summarize(rows, rng):
    n = len(rows)
    hits = sum(r["solved"] for r in rows)
    m = median(rows)
    ci = interval(bootstrap_medians(rows, rng))
    budgets = {}
    for b in (*BUDGETS, 262144, CAP):
        budget_hits = sum(r["solved"] and r["evaluations"] <= b for r in rows)
        x = np.log2([min(r["evaluations"], b) for r in rows])
        sd = float(np.std(x, ddof=1)) if n > 1 else None
        times = [
            r["budget_seconds"][str(b)] for r in rows if str(b) in r["budget_seconds"]
        ]
        budgets[str(b)] = dict(
            n=n,
            solves=budget_hits,
            solve_fraction=budget_hits / n if n else None,
            solve_fraction_95_interval=count_interval(budget_hits, n),
            objective_sd=sd,
            k=max(1, math.ceil((2 * sd) ** 2)) if sd is not None else None,
            mean_seconds=float(np.mean(times)) if len(times) == n and n else None,
            runtime_n=len(times),
        )
    return dict(
        n=n,
        solves=hits,
        solve_fraction=hits / n if n else None,
        solve_fraction_95_interval=count_interval(hits, n),
        km_median=m,
        km_median_label=(str(m) if m is not None else "> 524288")
        if n
        else "unmeasured",
        km_median_95_interval=ci,
        bootstrap_censored=ci[1] is None,
        ranking_value=m if m is not None else CAP,
        mean_seconds=float(np.mean([r["seconds"] for r in rows])) if n else None,
        shortcuts=sum(r["shortcuts"] for r in rows),
        unique_shortcuts=sum(r.get("unique_shortcuts", 0) for r in rows),
        unique_shortcuts_scope="sum of distinct programs within each seed; not deduplicated across seeds",
        budgets=budgets,
        decode_seconds_per_generation=sum(r["decode_seconds"] for r in rows)
        / sum(r["generations"] for r in rows)
        if n
        else None,
    )


def group(rows):
    result = {}
    for r in rows:
        result.setdefault((r["cell"], r["arm"]), []).append(r)
    return result


def summaries(rows):
    rng = np.random.default_rng(22474000)
    return {
        cid + "|" + arm: summarize(rs, rng)
        for (cid, arm), rs in sorted(group(rows).items())
    }


def tractable(summary):
    return summary["n"] >= 50 and summary["solves"] >= (
        105 if summary["n"] == 150 else 35
    )


def splits(bank, summary, ignore_tractability=False):
    retained = {c["id"]: c for c in bank if not c["rejects"]}
    result = []
    for permutation in itertools.permutations(("ADD", "DADD", "SEL")):
        holdouts = [
            "".join(pair) + "-" + comb for pair, comb in zip(PAIRS, permutation)
        ]
        holds = [retained[cid] for cid in holdouts if cid in retained]
        hold_tractable = all(
            tractable(summary.get(cid + "|U", {"n": 0, "solves": 0}))
            for cid in holdouts
        )
        training = [
            c
            for cid, c in retained.items()
            if cid not in holdouts
            and (
                ignore_tractability
                or tractable(summary.get(cid + "|U", {"n": 0, "solves": 0}))
            )
        ]
        train_combiners = {c["id"].split("-")[1] for c in training}
        train_reducers = {r for c in training for r in (c["x"], c["y"])}
        coverage = all(
            any(t["id"].split("-")[0] == h["id"].split("-")[0] for t in training)
            and h["id"].split("-")[1] in train_combiners
            for h in holds
        )
        structural = (
            len(holds) == 3
            and len(training) >= 4
            and len(train_combiners) == 3
            and len(train_reducers) == 3
            and coverage
        )
        eligible = structural and (ignore_tractability or hold_tractable)
        arm_medians = {
            arm: [summary.get(cid + "|" + arm, {}).get("km_median") for cid in holdouts]
            for arm in ("F", "G")
        }
        lacks = any(
            sum(m is not None and m < 4096 for m in ms) >= 2
            for ms in arm_medians.values()
        )
        ranking = math.exp(
            np.mean(
                [
                    math.log(summary.get(cid + "|U", {}).get("ranking_value", CAP))
                    for cid in holdouts
                ]
            )
        )
        result.append(
            dict(
                holdouts=holdouts,
                training=sorted(c["id"] for c in training),
                eligible=eligible,
                structural_eligible=structural,
                holdout_medians=arm_medians,
                headroom=not lacks,
                ranking=ranking,
            )
        )
    return result


def paired_ratios(rows):
    gs = group(rows)
    rng = np.random.default_rng(22474001)
    result = []
    for cid in sorted({r["cell"] for r in rows}):
        for bias, control in (("F", "U"), ("G", "U"), ("G", "G-marg")):
            left = {r["seed"]: r for r in gs.get((cid, control), [])}
            right = {r["seed"]: r for r in gs.get((cid, bias), [])}
            seeds = sorted(left.keys() & right.keys())
            a, b = [left[s] for s in seeds], [right[s] for s in seeds]
            ma, mb = median(a), median(b)
            ratio = ma / mb if ma is not None and mb is not None else None
            indices = rng.integers(len(seeds), size=(2000, len(seeds))) if seeds else []
            ratios = []
            unresolved = 0
            for ix in indices:
                x, y = median([a[i] for i in ix]), median([b[i] for i in ix])
                if x is None or y is None:
                    unresolved += 1
                else:
                    ratios.append(x / y)
            result.append(
                dict(
                    cell=cid,
                    bias=bias,
                    control=control,
                    paired_n=len(seeds),
                    speed_ratio=ratio,
                    paired_bootstrap_95_interval=interval(ratios)
                    if ratios and unresolved == 0
                    else [None, None],
                    unresolved_bootstraps=unresolved,
                )
            )
    return result


def topup_requests(bank, summary):
    """One request per cell/arm, sharing the original stage-C seed block."""
    training = {
        cid
        for split in splits(bank, summary, True)
        if split["eligible"]
        for cid in split["training"]
    }
    requests = []
    for cell in bank:
        if cell["rejects"]:
            continue
        cid = cell["id"]
        for arm in ("U", "F", "G"):
            s = summary[cid + "|" + arm]
            if s["n"] != 50:
                continue
            reasons = []
            if arm == "U":
                if 30 <= s["solves"] <= 39:
                    reasons.append("tractability")
                if cid in training:
                    reasons.extend(
                        "inner_budget_" + str(b)
                        for b in BUDGETS
                        if 20 <= s["budgets"][str(b)]["solves"] <= 30
                    )
            else:
                low, high = s["km_median_95_interval"]
                if low is not None and low <= 4096 and (high is None or high >= 4096):
                    reasons.append("headroom")
            if reasons:
                requests.append(dict(cell=cid, arm=arm, reasons=reasons))
    return requests


def costs(split, summary, rows):
    result = dict(holdouts=split["holdouts"], training=split["training"], budgets={})
    groups = group(rows)
    for b in (*BUDGETS, 262144, CAP):
        train = {
            cid: summary[cid + "|U"]["budgets"][str(b)] for cid in split["training"]
        }
        pending = [
            cid
            for cid, x in train.items()
            if b in BUDGETS and x["n"] == 50 and 20 <= x["solves"] <= 30
        ]
        feasible = not pending and all(
            x["solve_fraction"] >= 0.5 for x in train.values()
        )
        base_inner = sum(x["k"] * x["mean_seconds"] for x in train.values())
        # Capped-runtime upper projection uses per-evaluation time from each
        # observed run (including decoder and reproduction); no assumed solves.
        max_rates = {
            cid: max(r["seconds"] / r["evaluations"] for r in groups[(cid, "U")])
            for cid in train
        }
        capped_inner = sum(x["k"] * max_rates[cid] * b for cid, x in train.items())
        # 16 transfer arms; use the slowest measured fixed arm per holdout as
        # the baseline projection for future, unmeasured learned decoders.
        transfer = (
            16
            * 50
            * sum(
                max(summary[cid + "|" + arm]["mean_seconds"] for arm in ARMS)
                for cid in split["holdouts"]
            )
        )
        capped_transfer = (
            16
            * 50
            * sum(
                max(
                    r["seconds"] / r["evaluations"]
                    for arm in ARMS
                    for r in groups[(cid, arm)]
                )
                * CAP
                for cid in split["holdouts"]
            )
        )
        trajectories = {}
        for n in (8, 6):
            # The mismatched-family adaptation is allocated an equal complete
            # training run. It is included in both totals, not deferred away.
            adaptation = n * 16 * 40 * base_inner
            capped_adaptation = n * 16 * 40 * capped_inner
            total = 2 * adaptation + transfer
            capped_total = 2 * capped_adaptation + capped_transfer
            trajectories[str(n)] = dict(
                adaptation_cpu_hours=adaptation / 3600,
                mismatched_adaptation_cpu_hours=adaptation / 3600,
                transfer_cpu_hours=transfer / 3600,
                total_cpu_hours=total / 3600,
                total_wall_hours_8_workers=total / (8 * 3600),
                largest_single_queue_wall_hours=max(adaptation, transfer) / (8 * 3600),
                capped_total_cpu_hours=capped_total / 3600,
                capped_total_wall_hours_8_workers=capped_total / (8 * 3600),
            )
        result["budgets"][str(b)] = dict(
            feasible=feasible,
            pending_topup_cells=pending,
            per_cell=train,
            trajectories=trajectories if feasible or b not in BUDGETS else None,
        )
    result["inner_budget"] = next(
        (b for b in BUDGETS if result["budgets"][str(b)]["feasible"]), None
    )
    result["projection_scope"] = (
        "U baseline runtimes; learned and mismatched decoders unmeasured; equal mismatched adaptation allocation; transfer uses slowest fixed-arm runtime per cell"
    )
    return result


def decision(bank, rows, complete, topups_complete=True):
    summary = summaries(rows)
    candidates = splits(bank, summary)
    structural = splits(bank, summary, True)
    result = dict(
        summaries=summary,
        transversals=candidates,
        structural_transversals=structural,
        deciding_cap=CAP,
        tractability_scope="operational threshold at 524288 evaluations; larger caps untested",
        structural_headroom_complete=complete and topups_complete,
        all_structural_candidates_lack_headroom=all(
            not s["headroom"] for s in structural if s["eligible"]
        )
        if any(s["eligible"] for s in structural)
        else None,
        complete=complete,
        topups_complete=topups_complete,
        selected_split=None,
        all_split_costs=[],
    )
    if not complete or not topups_complete:
        result["outcome"] = "U"
        return result
    if sum(not c["rejects"] for c in bank) < 7 or not any(
        s["eligible"] for s in structural
    ):
        result["outcome"] = "1"
        return result
    eligible = [s for s in candidates if s["eligible"]]
    if not eligible:
        result["outcome"] = "2"
        return result
    eligible = [s for s in eligible if s["headroom"]]
    if not eligible:
        result["outcome"] = "3"
        return result
    eligible.sort(
        key=lambda s: (-s["ranking"], -len(s["training"]), sorted(s["holdouts"]))
    )
    selected = eligible[0]
    projected = [costs(s, summary, rows) for s in eligible]
    result["selected_split"] = selected
    result["all_split_costs"] = projected
    result["another_split_has_inner_budget"] = any(
        c["inner_budget"] is not None for c in projected[1:]
    )
    chosen = projected[0]
    b = chosen["inner_budget"]
    # An unresolved smaller budget prevents choosing a larger one as the
    # smallest feasible budget, even if the latter has a stable pass count.
    pending = [
        budget
        for budget in BUDGETS
        if (b is None or budget <= b)
        and chosen["budgets"][str(budget)]["pending_topup_cells"]
    ]
    if pending:
        result["outcome"] = "U"
        result["reason"] = "required borderline inner-budget top-up missing"
        result["pending_inner_budgets"] = pending
    elif b is None:
        result["outcome"] = "4a"
    else:
        cost = chosen["budgets"][str(b)]["trajectories"]
        result["outcome"] = "5" if cost["6"]["total_wall_hours_8_workers"] <= 8 else "4"
        result["recommended_trajectories"] = (
            8 if cost["8"]["total_wall_hours_8_workers"] <= 8 else 6
        )
    return result
