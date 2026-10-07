"""2129 paired interaction inference; fixed complete rosters are mandatory."""

import math

import numpy as np
from scipy.stats import t

from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.crossed_learning_run import TRAINING, HOLDOUTS
from experiments.chem_tape.solver_corpus_report import cost, pooled, one_sample
from experiments.chem_tape.solver_feedback_report import required_n

CONTRASTS = {
    "interaction": {"C2": 1, "T2": -1, "C1": -1, "T1": 1},
    "T2/T1": {"T2": 1, "T1": -1},
    "C2/T2": {"C2": 1, "T2": -1},
    "C1/T1": {"C1": 1, "T1": -1},
    "C2/C1": {"C2": 1, "C1": -1},
}


def outcome(estimate, valid=True):
    if not valid:
        return dict(
            row=0, meaning="validation failure or incomplete stage; no comparison claim"
        )
    bounds = estimate.get("interval_95")
    if not bounds:
        return dict(row=4, meaning="unresolved")
    lower, upper = bounds
    if lower > 1:
        return dict(
            row=1,
            meaning="feedback increased the advantage of additionally fitted context",
        )
    if upper < 1:
        return dict(
            row=2,
            meaning="the restricted token fit gained relatively more from feedback",
        )
    if 1 / 1.10 < lower <= 1 <= upper < 1.10:
        return dict(
            row=3,
            meaning="relative increment bounded within ±10% for these two fitting procedures",
        )
    return dict(
        row=4,
        meaning="unresolved; principal explanations remain compatible with the interval",
    )


def conditional_sizing(groups, estimate, phase):
    result = required_n(groups, estimate["delta_log2"], phase)
    mean = estimate["delta_log2"]
    margin = math.log2(1.10)
    sds = {f: float(np.std(v, ddof=1)) for f, v in groups.items()}
    if phase == "training":

        def width(n):
            return float(
                t.ppf(0.975, n - 1)
                * 0.5
                * np.sqrt(sum(s * s for s in sds.values()) / n)
            )
    else:
        sd = float(np.std(sum(groups.values(), []), ddof=1))

        def width(n):
            return float(t.ppf(0.975, n - 1) * sd / np.sqrt(n))

    distance = margin - abs(mean)
    needed = None
    if distance > 0:
        if width(100000) >= distance:
            needed = ">100000"
        else:
            lo, hi = 2, 100000
            while lo < hi:
                mid = (lo + hi) // 2
                if width(mid) < distance:
                    hi = mid
                else:
                    lo = mid + 1
            needed = lo if phase == "training" else lo + lo % 2
    result.update(
        n_for_two_sided_10pct_bound=needed,
        observed_family_sd_log2=sds,
        note="Conditional on observed mean/SD. Seed noise and lineage variation are separately estimated; more seeds may reduce seed noise. No guarantee for new lineages.",
    )
    return result


def phase_report(rows, corpora, config, phase):
    from experiments.chem_tape.context_increment_run import validate_rows

    roster, n = config["roster"], config["fresh_n"]
    by = validate_rows(rows, corpora, roster, phase, ("C1", "C2", "T1", "T2"), n)
    grouped = {name: {f: [] for f in TRAINING} for name in CONTRASTS}
    lineage = {name: {} for name in CONTRASTS}
    noise = {f: [] for f in TRAINING}
    for tid in roster:
        tr = corpora[tid]
        family = tr["family"]
        cells = TRAINING[family] if phase == "training" else sum(HOLDOUTS.values(), [])
        cell_means = {name: [] for name in CONTRASTS}
        cell_variances = []
        for cid in cells:
            arms = {}
            for arm in ("C1", "C2", "T1", "T2"):
                rs = sorted(
                    [r for key, r in by.items() if key[2:5] == (tid, cid, arm)],
                    key=lambda r: r["seed"],
                )
                arms[arm] = np.array([np.log2(cost(r)) for r in rs])
            for name, coefficients in CONTRASTS.items():
                paired = sum(
                    coefficient * arms[arm] for arm, coefficient in coefficients.items()
                )
                cell_means[name].append(float(paired.mean()))
                if name == "interaction":
                    cell_variances.append(float(np.var(paired, ddof=1) / n))
            # validate_rows regenerates each expected seed's training indices,
            # thereby requiring identical cases in all four arms.
        for name in CONTRASTS:
            value = float(np.mean(cell_means[name]))
            grouped[name][family].append(value)
            lineage[name][tid] = value
        noise[family].append(sum(cell_variances) / len(cells) ** 2)
    results = {}
    for name, groups in grouped.items():
        estimate = (
            pooled(groups)
            if phase == "training"
            else one_sample(sum(groups.values(), []))
        )
        estimate["lineage_contrasts_log2"] = lineage[name]
        if phase == "holdout":
            estimate["families"] = {f: one_sample(x) for f, x in groups.items()}
        results[name] = estimate
    primary = (
        results["interaction"]["pooled"]
        if phase == "training"
        else results["interaction"]
    )
    results["outcome"] = outcome(primary)
    results["conditional_sizing"] = (
        conditional_sizing(grouped["interaction"], primary, phase)
        if not config["smoke_only"]
        else None
    )
    results["noise_diagnostics"] = {
        f: dict(
            observed_lineage_variance_log2=float(
                np.var(grouped["interaction"][f], ddof=1)
            )
            if len(noise[f]) > 1
            else None,
            mean_estimated_seed_variance_log2=float(np.mean(noise[f])),
            note="Paired within-cell seed variance/n summed across independently seeded cells; decomposition is descriptive and noisy.",
        )
        for f in TRAINING
    }
    results["solve_counts"] = {
        arm: dict(
            solved=sum(r["solved"] for r in by.values() if r["arm"] == arm),
            total=sum(r["arm"] == arm for r in by.values()),
        )
        for arm in ("C1", "C2", "T1", "T2")
    }
    return results


def make_report(rows, corpora, config, complete, validation, admission, stop_reason):
    report = dict(
        config=config,
        stages=complete,
        validation=validation,
        admission=admission,
        stop_reason=stop_reason,
        training={},
        holdout={},
        outcome=outcome({}, False),
        transfer="unresolved",
        smoke_only=config["smoke_only"],
    )
    valid = validation["passed"] and complete["training"]
    if valid:
        report["training"] = phase_report(rows, corpora, config, "training")
        if not config["smoke_only"]:
            report["outcome"] = report["training"]["outcome"]
        if complete["holdout"]:
            report["holdout"] = phase_report(rows, corpora, config, "holdout")
            if not config["smoke_only"]:
                report["transfer"] = report["holdout"]["outcome"]["meaning"]
    return report


def save_report(out, report):
    write_json(out, "result.json", report)
    lines = [
        "# Feedback context increment",
        "",
        f"Outcome: {report['outcome']}",
        f"Transfer: {report['transfer']}",
        f"Stop: {report['stop_reason']}",
        "",
        "Extension of 1924 on shared seeds; not independent confirmation. T retains fixed G4 context.",
        "Speed ratios above one favor the numerator procedure. Interaction >1 means a larger contextual advantage after feedback.",
        "All contrasts except the training interaction are descriptive. No shared-mechanism or decoder-context-removal claim.",
        "",
    ]
    for phase in ("training", "holdout"):
        section = report[phase]
        if not section:
            continue
        lines += [
            f"## {phase}",
            "",
            "| Contrast | Ratio | 95% interval |",
            "|---|---:|---|",
        ]
        for name in CONTRASTS:
            estimate = section[name].get("pooled", section[name])
            bounds = estimate["interval_95"]
            lines.append(f"| {name} | {estimate['speed_ratio']:.3f} | {bounds} |")
        token = section["T2/T1"].get("pooled", section["T2/T1"])
        lines += [
            "",
            "Token improvement supported."
            if token["interval_95"] and token["interval_95"][0] > 1
            else "Token increment unresolved or negative; its interval does not justify a mostly-contextual claim.",
            f"Noise diagnostics: {section['noise_diagnostics']}",
            f"Conditional sizing: {section['conditional_sizing']}",
            "",
        ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4))
    for phase, color in [("training", "tab:blue"), ("holdout", "tab:orange")]:
        if report[phase]:
            values = report[phase]["interaction"]["lineage_contrasts_log2"]
            ax.scatter(
                range(len(values)),
                [2 ** (-v) for v in values.values()],
                label=phase,
                color=color,
            )
    ax.axhline(1, color="black", linewidth=0.7)
    ax.set(
        xlabel="Lineage (BE then PA)",
        ylabel="Interaction speed ratio I",
        title="Paired lineage interactions (smoke has no inference)"
        if report["smoke_only"]
        else "Paired lineage interactions",
    )
    if ax.collections:
        ax.legend()
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    plt.close(fig)
