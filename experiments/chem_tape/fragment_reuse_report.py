"""1036 ordered primary decision; fixed-cell corpus intervals and arithmetic repayment."""

import math

import numpy as np

from experiments.chem_tape.comparison_gate_report import describe, balanced_target_n
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.fragment_report import (
    comparison,
    row_key,
    plots,
    METRIC_DEFINITIONS,
)

ARMS = ("C", "F", "W")
PAIRS = [("F", "W"), ("F", "C"), ("W", "C")]


def route(stats):
    fw, fc = stats["F/W"], stats["F/C"]
    if fw["interval_95"][1] < 1 or fc["interval_95"][1] < 1:
        return "harm_ends_cross_shape_expansion"
    if (
        fw["interval_95"][0] > 1
        and fw["speed_ratio"] >= 1.10
        and fc["interval_95"][0] > 1
    ):
        return "repertoire_earns_acquisition_review"
    if fw["interval_95"][1] < 1.10:
        return "no_worthwhile_library_increment"
    return "unresolved"


def contrasts(rows, **kwargs):
    return {f"{x}/{y}": comparison(rows, x, y, **kwargs) for x, y in PAIRS}


def diagnostics(rows, libraries):
    result = {}
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        stats = {
            k: (
                [sum(r["operator"][k][j] for r in rs) for j in range(7)]
                if k.endswith("histogram")
                else sum(r["operator"][k] for r in rs)
            )
            for k in rs[0]["operator"]
        }
        stats["realized_child_fraction"] = stats["edited_children"] / max(
            1, stats["eligible_children"]
        )
        stats["tokens_changed_per_edit"] = stats["changed_tokens"] / max(
            1, stats["edited_children"]
        )
        occurrences = []
        for r in rs:
            if r["solved"]:
                occurrences.append(
                    sum(
                        r["solver"][s : s + len(f["tokens"])] == f["tokens"]
                        for f in libraries[r["corpus"]]["fragments"]
                        for s in range(33 - len(f["tokens"]))
                    )
                )
        stats.update(
            solvers_with_library_window=sum(v > 0 for v in occurrences),
            solver_library_share=sum(v > 0 for v in occurrences) / len(occurrences)
            if occurrences
            else None,
            solver_library_occurrences=sum(occurrences),
            seconds_per_evaluation=sum(r["seconds"] for r in rs)
            / sum(r["evaluations"] for r in rs),
        )
        result[arm] = stats
    return result


def repayment(rows, preparation):
    means = {
        arm: dict(
            evaluations=float(
                np.mean([r["evaluations"] for r in rows if r["arm"] == arm])
            ),
            worker_seconds=float(
                np.mean([r["seconds"] for r in rows if r["arm"] == arm])
            ),
        )
        for arm in ARMS
    }
    extraction = preparation["extraction_cost"]["worker_seconds"]
    comparisons = {}
    for arm in ("C", "W"):
        saved = means[arm]["worker_seconds"] - means["F"]["worker_seconds"]
        comparisons["F/" + arm] = dict(
            mean_actual_evaluations_saved=means[arm]["evaluations"]
            - means["F"]["evaluations"],
            mean_worker_seconds_saved=saved,
            searches_to_repay_all16_libraries=extraction / saved if saved > 0 else None,
            demonstrated_positive_wall_saving=saved > 0,
        )
    return dict(
        arithmetic_means=means,
        comparisons=comparisons,
        extraction_cost=preparation["extraction_cost"],
        shared_corpus_collection=preparation["shared_corpus_collection"],
        units="Repayment divides measured extraction worker-seconds for all16 libraries by arithmetic worker-seconds saved per search; consumed evaluations reported separately, never mixed with seconds or penalized endpoint costs.",
        caveat="Descriptive workload-conditioned accounting; no positive saving means no demonstrated break-even; shared corpus collection excluded from incremental extraction but reported separately.",
    )


def report(out, rows, schedule, libraries, preparation):
    # Compare all metadata, not just keys; phase decides which bank enters efficacy.
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
        raise ValueError("changed roster metadata; no efficacy decision")
    banks = {}
    for phase in ("then_addition", "holdout"):
        rs = [r for r in rows if r["phase"] == phase]
        summaries = {a: describe([r for r in rs if r["arm"] == a]) for a in ARMS}
        banks[phase] = dict(
            comparisons=contrasts(rs),
            summaries=summaries,
            sensitivity=dict(
                cap_penalty_1=contrasts(rs, penalty=1),
                both_solved=contrasts(rs, both=True),
                families={f: contrasts(rs, family=f) for f in ("BE", "PA")},
            ),
            per_cell={
                cid: dict(
                    comparisons=contrasts([r for r in rs if r["cell"] == cid]),
                    summaries={
                        a: describe(
                            [r for r in rs if r["cell"] == cid and r["arm"] == a]
                        )
                        for a in ARMS
                    },
                )
                for cid in sorted({r["cell"] for r in rs})
            },
            diagnostics=diagnostics(rs, libraries),
            repayment=repayment(rs, preparation),
        )
        plots(out, rs, banks[phase], arms=ARMS)
        (out / "diagnostics.png").replace(out / (phase + "_diagnostics.png"))
    primary = banks["then_addition"]["comparisons"]
    pricing = preparation["resolution_cost"]
    n = balanced_target_n(primary["F/W"]["sd_log"], math.log(1.05), 16)
    extra = n - 16
    score = preparation["admission"]["projected_seconds"] * extra / 16
    build = (
        1.15
        * extra
        / pricing["workers"]
        * sum(
            pricing[k]
            for k in (
                "source_collection_worker_seconds_per_corpus",
                "library_worker_seconds_per_corpus",
                "historical_C_fit_worker_seconds_per_corpus",
            )
        )
    )
    price = dict(
        target_half_width_factor=1.05,
        scenario_corpora=n,
        new_balanced_corpora=extra,
        additional_scoring_queue_seconds=score,
        additional_preparation_queue_seconds=build,
        reporting_queue_seconds=pricing["reporting_queue_seconds"],
        agent_hours=pricing["agent_hours"],
        complete_expected_hours=(score + build + pricing["reporting_queue_seconds"])
        / 3600
        + pricing["agent_hours"],
        caveat="Observed corpus SD assumed unchanged; new balanced corpora repeat collection, C fitting, library extraction and complete scoring. This conditional price does not authorize new work or guarantee seed-only precision.",
    )
    result = dict(
        complete=True,
        primary_bank="then_addition",
        reference_bank="holdout",
        primary_seeds=preparation["admission"]["selected_seeds"],
        holdout_seeds=8,
        decision=route(primary),
        W_cheaper_candidate=(
            route(primary) == "no_worthwhile_library_increment"
            and primary["W/C"]["interval_95"][0] > 1
        ),
        banks=banks,
        resolution_price=price,
        metric_definitions=METRIC_DEFINITIONS,
        scope="Frozen externally extracted literal blocks on two development banks; corpus intervals condition on fixed cells. No acquisition, modularity, fresh-bank transfer or dependency-versus-supply claim. Whole libraries have four source cells versus three in0843, preventing clean shape attenuation estimates. W retains a library-derived length schedule, though no token repertoire.",
    )
    write_json(out, "result.json", result)
    lines = [
        f"Decision: **{result['decision']}** (then-addition only; approved order).",
        "",
        result["scope"],
        "",
    ]
    for phase, bank in banks.items():
        lines.extend(
            [
                phase + " (primary)"
                if phase == "then_addition"
                else phase + " (descriptive reference)",
                "",
                "| ratio | estimate | 95% interval |",
                "|---|---:|---|",
            ]
        )
        for key, s in bank["comparisons"].items():
            lines.append(
                f"| {key} | {s['speed_ratio']:.3f} | {s['interval_95'][0]:.3f}–{s['interval_95'][1]:.3f} |"
            )
        lines.append("")
    lines.extend(
        [
            "Rule2 earns review, not proof of true increment>1.10 or acquisition. Reference-bank results cannot resolve the primary decision. Broad F/W uncertainty is not evidence for block mechanics.",
            "Arithmetic repayment versus both C and W, descriptive cell/family/solve/edit results, and conditional×1.05 resolution pricing are in result.json. Return to strategy; no automatic top-up.",
        ]
    )
    (out / "report.md").write_text("\n".join(lines) + "\n")
    return result
