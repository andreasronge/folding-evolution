"""Censor-aware assembly summaries and explicitly conditional cost scenarios."""

from __future__ import annotations

import math

import numpy as np

from experiments.chem_tape.composition_report import CAP, BUDGETS, median, summaries


def finite_interval(x):
    if not len(x):
        return [None, None]
    ordered = np.sort(x)
    return [
        float(ordered[int(0.025 * (len(x) - 1))]),
        float(ordered[math.ceil(0.975 * (len(x) - 1))]),
    ]


def shape_contrast(
    rows, cells, numerator, denominator, seed=260605000, replicates=2000
):
    """One joint seed resample across cells and arms; undefined KM stays undefined."""
    groups = {
        (cid, arm): {r["seed"]: r for r in rows if r["cell"] == cid and r["arm"] == arm}
        for cid in cells
        for arm in (numerator, denominator)
    }
    seeds = (
        sorted(set.intersection(*(set(g) for g in groups.values()))) if groups else []
    )
    result = dict(
        n_paired_seeds=len(seeds),
        numerator=numerator,
        denominator=denominator,
        cells=cells,
        median_ratio=None,
        interval_95=[None, None],
        defined_bootstrap_fraction=0.0,
        capped_time_ratio=None,
        resolved=False,
    )
    if not seeds:
        return result

    def ratio(indices, capped=False):
        ratios = []
        for cid in cells:
            ms = []
            for arm in (numerator, denominator):
                rs = [groups[(cid, arm)][seeds[i]] for i in indices]
                ms.append(
                    float(np.median([r["evaluations"] for r in rs]))
                    if capped
                    else median(rs)
                )
            if None in ms:
                return None
            ratios.append(ms[0] / ms[1])
        return float(np.exp(np.mean(np.log(ratios))))

    indices = np.arange(len(seeds))
    result["median_ratio"] = ratio(indices)
    result["capped_time_ratio"] = ratio(indices, True)
    rng = np.random.default_rng(seed)
    draws = [
        ratio(rng.integers(len(seeds), size=len(seeds))) for _ in range(replicates)
    ]
    defined = [x for x in draws if x is not None]
    result["defined_bootstrap_fraction"] = len(defined) / replicates
    # A finite conditional-on-solves interval would omit the censoring tail.
    # Use the KM gate only when every replicate and the point estimate exists.
    if len(defined) == replicates and result["median_ratio"] is not None:
        result["interval_95"] = finite_interval(defined)
        result["resolved"] = True
    return result


def capped_ratios(rows):
    groups = {}
    for r in rows:
        groups.setdefault(r["cell"], {}).setdefault(r["arm"], {})[r["seed"]] = r
    result = {}
    rng = np.random.default_rng(260605001)
    for cid, arms in sorted(groups.items()):
        for numerator, denominator in (("G", "U"), ("F", "U"), ("G", "G-marg")):
            ns, ds = arms.get(numerator, {}), arms.get(denominator, {})
            seeds = sorted(ns.keys() & ds.keys())
            if not seeds:
                continue
            x = np.log2([ns[s]["evaluations"] / ds[s]["evaluations"] for s in seeds])
            draws = np.median(x[rng.integers(len(x), size=(2000, len(x)))], axis=1)
            result[cid + "|" + numerator + "/" + denominator] = dict(
                n=len(seeds),
                ratio=float(2 ** np.median(x)),
                interval_95=finite_interval(2**draws),
                scope="paired capped-time ratio; not uncensored KM",
            )
    return result


def cost_projection(pair, summary, rows, marginal_seconds=0.0):
    if pair is None:
        return dict(
            split_specific=None,
            reason="no eligible split",
            per_cell_cost_curves={
                key: {str(b): val["budgets"][str(b)] for b in BUDGETS}
                for key, val in summary.items()
                if key.endswith("|U") or key.endswith("|G")
            },
        )
    groups = {}
    for r in rows:
        groups.setdefault((r["cell"], r["arm"]), []).append(r)
    scenarios = {}
    holdouts = [cid for s in pair["shapes"] for cid in pair["split"][s]["holdouts"]]
    # 24 learned maps, each tied control, 4 fixed controls; 4 holdouts x 50 seeds.
    transfer_seconds = (
        52
        * 50
        * sum(
            max(
                summary[cid + "|" + a]["mean_seconds"]
                for a in ("U", "F", "G", "G-marg")
            )
            for cid in holdouts
        )
    )
    transfer_capped = (
        52
        * 50
        * sum(
            max(
                r["seconds"] / r["evaluations"]
                for a in ("U", "F", "G", "G-marg")
                for r in groups[(cid, a)]
            )
            * CAP
            for cid in holdouts
        )
    )
    for start in ("U", "G"):
        scenarios[start] = {}
        for b in BUDGETS:
            training_seconds, capped_seconds, detail = 0.0, 0.0, {}
            feasible = True
            for shape in pair["shapes"]:
                train = pair["split"][shape]["training"]
                vals = [summary[cid + "|" + start]["budgets"][str(b)] for cid in train]
                sd2 = sum(v["objective_sd"] ** 2 for v in vals) / len(vals)
                k = max(2, math.ceil(4 * sd2 / len(train)))
                feasible &= all(v["solve_fraction"] >= 0.5 for v in vals)
                base = sum(v["mean_seconds"] for v in vals) * k
                capped = (
                    sum(
                        max(
                            r["seconds"] / r["evaluations"]
                            for r in groups[(cid, start)]
                        )
                        * b
                        for cid in train
                    )
                    * k
                )
                # 12 trajectories/shape, 16 individuals, initial + 30 generations.
                training_seconds += 12 * 16 * 31 * base
                capped_seconds += 12 * 16 * 31 * capped
                detail[shape] = dict(
                    n_train=len(train),
                    pooled_within_cell_sd=sd2**0.5,
                    k=k,
                    searches=12 * 16 * 31 * k * len(train),
                    mean_inner_seconds=base,
                    training_cells=train,
                )
            # Both contextual and token-only maps get a measured marginal control.
            marginal_cost = 24 * marginal_seconds
            total = training_seconds + transfer_seconds + marginal_cost
            capped_total = capped_seconds + transfer_capped + marginal_cost
            scenarios[start][str(b)] = dict(
                feasible=bool(feasible),
                shapes=detail,
                adaptation_cpu_hours=training_seconds / 3600,
                transfer_cpu_hours=transfer_seconds / 3600,
                marginal_cpu_hours=marginal_cost / 3600,
                total_cpu_hours=total / 3600,
                wall_hours_8_workers=total / (8 * 3600),
                capped_cpu_hours=capped_total / 3600,
                capped_wall_hours_8_workers=capped_total / (8 * 3600),
            )
    return dict(
        split_specific=scenarios,
        transfer_searches=52 * 4 * 50,
        trajectories=24,
        scope="starting U/G runtime scenarios; decoder adaptation unmeasured; capped scenario uses slowest observed seconds/evaluation",
        marginal_scope="24 estimates plus validation, timed from diagnostic maps; token-only marginal cost conservatively included",
        precision_target="SE <=0.5 log2 units for mean training objective under independent inner runs",
        queue_scope="future queues reviewed separately, each <=8h",
    )


def report(
    screens,
    pairing,
    rows,
    complete_b,
    complete_c,
    complete_topups,
    marginal_seconds=0.0,
):
    summary = summaries(rows)
    pair = pairing["selected"]
    result = dict(
        stage_a_complete=len(screens) == 3
        and all(s["complete"] for s in screens.values()),
        stage_b_complete=complete_b,
        stage_c_complete=complete_c,
        topups_complete=complete_topups,
        selected_pair=pair,
        summaries=summary,
        paired_capped_ratios=capped_ratios(rows),
        contrasts={},
        semantic_verdict="no eligible enumerated pair"
        if pair is None
        else "eligible enumerated pair",
        semantic_scope="162 frozen candidates on three finite domains under >=80% alias, duplicate and role-coverage rules",
    )
    result["semantic_table"] = {
        domain: {
            shape: dict(
                candidates=sum(c["shape"] == shape for c in screen["cells"]),
                retained=sum(
                    c["shape"] == shape and c["retained"] for c in screen["cells"]
                ),
                exact_identities=sum(
                    c["shape"] == shape and c["alias_kind"] == "exact_identity"
                    for c in screen["cells"]
                ),
                near_aliases=sum(
                    c["shape"] == shape and c["alias_kind"] == "domain_near_alias"
                    for c in screen["cells"]
                ),
                duplicates=sum(
                    c["shape"] == shape and bool(c["duplicate_ids"])
                    for c in screen["cells"]
                ),
            )
            for shape in ("GA", "BT", "BE", "PA", "D1", "D2")
        }
        for domain, screen in screens.items()
    }
    result["costs"] = (
        cost_projection(pair, summary, rows, marginal_seconds)
        if complete_b
        else dict(split_specific=None, reason="calibration incomplete")
    )
    if not result["stage_a_complete"]:
        result["semantic_verdict"] = "unresolved incomplete screen"
    if (
        not result["stage_a_complete"]
        or not complete_b
        or not complete_c
        or not complete_topups
    ):
        result.update(outcome="U", reason="incomplete required stage/block/top-up")
        return result
    if pair is None:
        result.update(
            outcome="1", reason="no enumerated pair passes frozen semantic/split rules"
        )
        return result
    contrast_status, g_status = [], []
    for i, shape in enumerate(pair["shapes"]):
        swapped = pair["shapes"][1 - i]
        cells = [
            c["id"]
            for c in screens[pair["domain"]]["cells"]
            if c["retained"] and c["shape"] == shape
        ]
        context = shape_contrast(rows, cells, swapped, shape)
        marginal = shape_contrast(rows, cells, swapped + "-marg", shape + "-marg")
        g = shape_contrast(rows, cells, "G", shape)
        result["contrasts"][shape] = dict(
            context=context, tied_marginals=marginal, g_over_matched=g
        )
        for contrast, statuses, threshold in (
            (context, contrast_status, 1.5),
            (g, g_status, 1.0),
        ):
            low, high = contrast["interval_95"]
            if not contrast["resolved"] or low <= 1 <= high:
                statuses.append("unresolved")
            elif low > 1 and contrast["median_ratio"] >= threshold:
                statuses.append("pass")
            else:
                statuses.append("fail")
    if "unresolved" in contrast_status:
        result.update(outcome="U", reason="censored or imprecise diagnostic contrast")
    elif "fail" in contrast_status:
        result.update(
            outcome="2",
            reason="these hand-set diagnostic grammars did not establish usable contrast in both shapes",
        )
    elif "unresolved" in g_status:
        result.update(outcome="U", reason="censored or imprecise improvement over G")
    elif "fail" in g_status:
        result.update(
            outcome="3", reason="improvement over G not established in both shapes"
        )
    else:
        fast = sum(
            any(
                summary[cid + "|" + arm]["km_median"] is not None
                and summary[cid + "|" + arm]["km_median"] < 4096
                for arm in ("F", "G", "G-marg")
            )
            for s in pair["shapes"]
            for cid in pair["split"][s]["holdouts"]
        )
        g_scenarios = result["costs"]["split_specific"]["G"]
        affordable = any(
            c["feasible"] and c["wall_hours_8_workers"] <= 16
            for c in g_scenarios.values()
        )
        if fast >= 2:
            result.update(
                outcome="3",
                reason="at least two holdouts fail the 4096 operational headroom rule",
            )
        else:
            result.update(
                outcome="5" if affordable else "4",
                reason="conditional cost/tractability gate",
            )
    return result
