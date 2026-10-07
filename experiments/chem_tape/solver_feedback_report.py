"""1924 lineage-level inference; incomplete admitted rosters never support claims."""

import math

import numpy as np
from scipy.stats import t

from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.crossed_learning_run import TRAINING, HOLDOUTS
from experiments.chem_tape.solver_corpus_fit import R
from experiments.chem_tape.solver_corpus_report import cost, one_sample, pooled


def holdout_label(estimate):
    bounds = estimate.get("interval_95") if estimate else None
    if not bounds:
        return "unresolved"
    lower, upper = bounds
    if lower > 1:
        return "transfers"
    if upper < 1:
        return "harms withheld cells"
    if lower <= 1 <= upper < 1.10:
        return "no transfer above 10%"
    return "unresolved"


def outcome(parent, source, feasible):
    if not feasible:
        return dict(
            row=0, meaning="infeasible or incomplete primary; no comparison claim"
        )
    bounds = parent.get("interval_95")
    if not bounds:
        return dict(row=5, meaning="unresolved")
    if bounds[0] > 1:
        if source and source.get("interval_95") and source["interval_95"][0] > 1:
            return dict(
                row=1,
                meaning="further training gain attributable to the source-decoder procedure",
            )
        return dict(row=2, meaning="parent improvement; source attribution unresolved")
    if bounds[1] < 1:
        return dict(
            row=4, meaning="feedback slows training search at this one-step scope"
        )
    if bounds[0] <= 1 <= bounds[1] < 1.10:
        return dict(
            row=3, meaning="this refit's mean training increment is bounded below 10%"
        )
    return dict(row=5, meaning="unresolved; additional independent lineages needed")


def contrast(rows, corpora, roster, phase, a, b, fresh_n):
    """Reject missing, duplicated or unpaired rows rather than shrink the roster."""
    groups = {f: [] for f in TRAINING}
    grouped = {}
    for row in rows:
        if row["phase"] == phase and row["corpus"] in roster and row["arm"] in (a, b):
            grouped.setdefault((row["corpus"], row["cell"], row["arm"]), []).append(row)
    lineage = {}
    for tid in roster:
        family = corpora[tid]["family"]
        cells = TRAINING[family] if phase == "training" else sum(HOLDOUTS.values(), [])
        differences = []
        for cid in cells:
            paired = []
            for arm in (a, b):
                rs = grouped.get((tid, cid, arm), [])
                if len(rs) != fresh_n or len({r["seed"] for r in rs}) != fresh_n:
                    raise ValueError("incomplete/duplicate inferential roster")
                paired.append({r["seed"]: r for r in rs})
            if paired[0].keys() != paired[1].keys() or any(
                paired[0][s]["training_indices"] != paired[1][s]["training_indices"]
                for s in paired[0]
            ):
                raise ValueError("unpaired inferential roster")
            differences.append(
                float(
                    np.mean([np.log2(cost(r)) for r in paired[0].values()])
                    - np.mean([np.log2(cost(r)) for r in paired[1].values()])
                )
            )
        delta = float(np.mean(differences))
        groups[family].append(delta)
        lineage[tid] = delta
    result = (
        pooled(groups)
        if phase == "training"
        else one_sample(groups["BE"] + groups["PA"])
    )
    result.update(roster=roster, lineage_contrasts_log2=lineage)
    estimate = result["pooled"] if phase == "training" else result
    result["required_n"] = required_n(groups, estimate["delta_log2"], phase)
    return result


def required_n(groups, delta, phase):
    """Conditional sizing at observed effect/SD; independent NEW lineage replication."""
    sds = {
        f: float(np.std(v, ddof=1)) if len(v) > 1 else None for f, v in groups.items()
    }
    if any(v is None for v in sds.values()):
        return dict(note="insufficient replication for sizing")
    if phase == "training":

        def width(n):
            return float(
                t.ppf(0.975, n - 1)
                * 0.5
                * np.sqrt(sum(s * s for s in sds.values()) / n)
            )

        unit = "lineages per family"
    else:
        sd = float(np.std(groups["BE"] + groups["PA"], ddof=1))

        def width(n):
            return float(t.ppf(0.975, n - 1) * sd / np.sqrt(n))

        unit = "total lineages (balanced families)"

    def needed(distance):
        if distance <= 0:
            return None
        lo, hi = 2, 100000
        if width(hi) >= distance:
            return ">100000"
        while lo < hi:
            mid = (lo + hi) // 2
            if width(mid) < distance:
                hi = mid
            else:
                lo = mid + 1
        return lo if phase == "training" else lo + (lo % 2)

    return dict(
        unit=unit,
        n_for_gain_lower_above_1=needed(-delta),
        n_for_upper_below_1_10=needed(delta + math.log2(1.10)),
        note="conditional on observed mean and SD; does not guarantee future precision",
    )


def table_metrics(table):
    p = np.diff(np.asarray(table), prepend=0, axis=1) / R
    entropy = -(p * np.log2(p)).sum(1)
    # Distribution over previous tokens in the 31 body positions of a length-32 tape.
    prev = p[24].copy()
    occupancy = np.zeros(24)
    for _ in range(31):
        occupancy += prev
        prev = prev @ p[:24]
    joint = occupancy[:, None] / 31 * p[:24]
    marginal = joint.sum(0)
    mi = float((joint * np.log2(p[:24] / marginal)).sum())
    return dict(
        mean_body_row_entropy_bits=float(entropy[:24].mean()),
        start_row_entropy_bits=float(entropy[24]),
        start_row_top_token_share=float(p[24].max()),
        previous_token_mutual_information_bits=mi,
        MI_definition="finite-tape body-position weighted decoder distribution, positions 2–32",
    )


def amortization(rows, corpora, roster, phase):
    result = {}
    for tid in roster:
        tr = corpora[tid]
        cells = (
            TRAINING[tr["family"]]
            if phase == "training"
            else sum(HOLDOUTS.values(), [])
        )

        def mean(arm, field):
            return float(
                np.mean(
                    [
                        np.mean(
                            [
                                cost(r) if field == "evaluations" else r["seconds"]
                                for r in rows
                                if r["phase"] == phase
                                and r["corpus"] == tid
                                and r["arm"] == arm
                                and r["cell"] == cid
                            ]
                        )
                        for cid in cells
                    ]
                )
            )

        evaluations = mean("C", "evaluations") - mean("C2", "evaluations")
        seconds = mean("C", "seconds") - mean("C2", "seconds")
        collection = tr["C2"]
        result[tid] = dict(
            mean_penalized_evaluations_saved=evaluations,
            mean_worker_seconds_saved=seconds,
            collection_evaluations=collection["collection_evaluations"],
            collection_worker_seconds=collection["collection_seconds"],
            break_even_searches_evaluations=math.ceil(
                collection["collection_evaluations"] / evaluations
            )
            if evaluations > 0
            else None,
            break_even_searches_worker_seconds=math.ceil(
                (collection["collection_seconds"] + collection["fit_seconds"]) / seconds
            )
            if seconds > 0
            else None,
            seconds_include_fit=True,
        )
    return result


def make_report(
    rows,
    corpora,
    config,
    complete,
    validation,
    admission,
    control_valid,
    stop_reason,
    control_failure,
):
    report = dict(
        config=config,
        stages=complete,
        validation=validation,
        admission=admission,
        control_valid=control_valid,
        stop_reason=stop_reason,
        control_failure=control_failure,
        contrasts={},
        holdout={},
        collection={},
        tables={},
        solve_rates={},
        amortization={},
        next="strategy",
        smoke_only=config["smoke_only"],
    )
    roster, n = config["roster"], config["fresh_n"]
    feasible = complete["A"] and complete["B"] and validation["passed"]
    for phase, done in [
        ("training", feasible),
        ("holdout", feasible and complete["C"]),
    ]:
        if not done:
            continue
        report["contrasts"][phase] = {
            "C2/C": contrast(rows, corpora, roster, phase, "C2", "C", n)
        }
        source_done = (
            complete["D_training" if phase == "training" else "D_holdout"]
            and control_valid
        )
        if source_done:
            for a, b in [("C2", "Cprime"), ("Cprime", "C")]:
                report["contrasts"][phase][a + "/" + b] = contrast(
                    rows, corpora, admission["roster"], phase, a, b, n
                )
        report["amortization"][phase] = amortization(rows, corpora, roster, phase)
    training = report["contrasts"].get("training", {})
    parent = training.get("C2/C", {}).get("pooled", {})
    source = training.get("C2/Cprime", {}).get("pooled")
    report["outcome"] = outcome(parent, source, feasible and not config["smoke_only"])
    if config["smoke_only"]:
        report["outcome"]["meaning"] = "smoke only; no scientific comparison claim"
    for key in ("C2/C", "C2/Cprime"):
        report["holdout"][key] = holdout_label(
            report["contrasts"].get("holdout", {}).get(key)
        )
    report["source_attributed_transfer"] = (
        not config["smoke_only"]
        and report["outcome"]["row"] == 1
        and all(v == "transfers" for v in report["holdout"].values())
    )
    for tid, tr in corpora.items():
        report["tables"][tid] = {"C": table_metrics(tr["C"])}
        report["collection"][tid] = {}
        for arm in ("C2", "Cprime"):
            if arm in tr:
                record = tr[arm]
                report["collection"][tid][arm] = {
                    k: v
                    for k, v in record.items()
                    if k not in {"tables", "counts", "fit"}
                }
                if "tables" in record:
                    report["tables"][tid][arm] = table_metrics(record["tables"]["C"])
    for phase in ("collection_C", "collection_G4", "training", "holdout"):
        arms = sorted({r["arm"] for r in rows if r["phase"] == phase})
        report["solve_rates"][phase] = {
            a: dict(
                solved=sum(
                    r["solved"] for r in rows if r["phase"] == phase and r["arm"] == a
                ),
                attempted=sum(r["phase"] == phase and r["arm"] == a for r in rows),
            )
            for a in arms
        }
    report["limitations"] = [
        "One external refit with frozen rule; no indefinite or evolutionary-learning claim.",
        "Source-decoder procedure includes differences in solver yield and diversity.",
        "Three repeatedly inspected holdouts; no family-specificity or carrying-mechanism inference.",
        "Start-row contribution and extent of overfitting are not isolated.",
        "Incomplete control rosters are descriptive only; unresolved intervals are not equality.",
    ]
    return report


def save_report(out, report):
    write_json(out, "result.json", report)
    lines = [
        "# One solver-corpus feedback step",
        "",
        report["outcome"]["meaning"],
        "",
        "| Phase | Contrast | Speed ratio | 95% interval |",
        "|---|---|---|---|",
    ]
    for phase, contrasts in report["contrasts"].items():
        for name, result in contrasts.items():
            estimate = result["pooled"] if phase == "training" else result
            lines.append(
                f"| {phase} | {name} | {estimate['speed_ratio']:.3f} | {estimate['interval_95']} |"
            )
    lines += [
        "",
        "Holdout labels: " + str(report["holdout"]),
        "",
        "Partial control data, if present, do not support source attribution.",
        "",
        "Full yields, costs, diagnostics, precision, conditional sizing and break-even are in result.json.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for arm in ("C", "C2", "Cprime"):
        values = [
            metrics[arm]["mean_body_row_entropy_bits"]
            for metrics in report["tables"].values()
            if arm in metrics
        ]
        if values:
            axes[0].plot(range(1, len(values) + 1), values, "o", label=arm)
    axes[0].set(xlabel="Lineage", ylabel="Mean body-row entropy (bits)")
    if report["tables"]:
        axes[0].legend()
    train = report["contrasts"].get("training", {}).get("C2/C")
    if train:
        for family in TRAINING:
            axes[1].plot(train["families"][family]["contrasts_log2"], "o", label=family)
        axes[1].legend()
    axes[1].axhline(0, color="gray", linewidth=1)
    axes[1].set(xlabel="Within-family lineage", ylabel="C2 − C mean log2 evaluations")
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=140)
    plt.close(fig)
