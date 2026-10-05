"""One-look exact max>2 reproductive-access experiment (2026-10-05-1957).

The approved plan lives in research/runs/2026-10-05-1957/plan.md. Run as a
module with RUN_DIR set. Pilot data select n only; never enter final contrasts.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import evolve_bias as eb
from experiments.chem_tape import evolve_bias_components as ec
from folding_evolution.chem_tape.evolve import (
    _reproduce_one_island, build_initial_population, make_rng,
)

MASTER = 202610051957
CELLS = ("U-ord", "U-veto", "R-ord", "R-veto")
POP, CAP, BOOT = 1024, 262144, 100000
ALPHA, TAU = .05 / 4, 1.25
SUM_Y, MAX_Y = eb.labels("sum2", eb.DOMAIN), eb.labels("max2", eb.DOMAIN)
METRIC_DEFINITIONS = {
    "time": "Candidate evaluations to the earliest exact sum>2 program in population order, verified on all 10000 lists; unsolved complete runs are administratively censored at cap.",
    "exact_max": "Number of individuals whose output equals max>2 on all 10000 lists, after checking exact sum>2 first.",
    "other_perfect": "Number of training-perfect individuals that are neither exhaustive exact sum>2 nor exhaustive exact max>2, counting duplicate genomes.",
    "solver_parents": "Exact-max>2 flags of the immediate previous-generation parents of the earliest solver, using engine lineage indices; null for generation-zero solvers.",
    "C1": "U-ord KM median evaluations divided by R-ord KM median evaluations.",
    "P_R": "R-veto KM median evaluations divided by R-ord KM median evaluations.",
    "P_U": "U-veto KM median evaluations divided by U-ord KM median evaluations.",
    "I": "P_R divided by P_U, calculated from four cell KM medians with whole-seed paired bootstrap resampling.",
}


def training_indices(seed):
    rng = np.random.default_rng(eb.stream_seed(f"training/sum2/{seed}", MASTER))
    idx = np.concatenate([
        rng.choice(np.flatnonzero(SUM_Y == 0), 32, replace=True),
        rng.choice(np.flatnonzero((SUM_Y == 1) & (MAX_Y == 1)), 32, replace=True),
    ])
    return idx[rng.permutation(64)]


def sampler_audit():
    assert int((SUM_Y != MAX_Y).sum()) == 66
    assert int(((SUM_Y == 1) & (MAX_Y == 1)).sum()) == 9919
    audits = []
    for seed in (MASTER + 10000, MASTER + 100000):
        idx = training_indices(seed)
        y, proxy = SUM_Y[idx], MAX_Y[idx]
        assert y.sum() == 32 and np.array_equal(y, proxy)
        audits.append(dict(seed=seed, indices=idx.tolist(), positives=int(y.sum()),
                           n=len(y), balance=float(y.mean()), both_labels=True,
                           constant_accuracy=.5, proxy="max>2",
                           proxy_train_accuracy=float((proxy == y).mean()),
                           proxy_domain_accuracy=float((SUM_Y == MAX_Y).mean()),
                           admitted_positives=9919, domain_disagreements=66))
    return audits


def classify(population, cases, cache, examples):
    """All training-perfect candidates, with byte-keyed exhaustive verification.

    A guarantees every exact max2 program is training perfect. Class values:
    0=other, 1=exact sum2, 2=exact max2. No semantic hash approximation.
    """
    classes = np.zeros(len(population), dtype=np.uint8)
    checked = 0
    for i in np.flatnonzero(cases.all(axis=1)):
        key = population[i].tobytes()
        if key not in cache:
            if len(cache) >= 65536:
                cache.clear()
            pred = eb.predictions([population[i]], eb.DOMAIN_LIST)[0]
            kind = 1 if np.array_equal(pred, SUM_Y) else 2 if np.array_equal(pred, MAX_Y) else 0
            cache[key] = (kind, float((pred == SUM_Y).mean()), float((pred == MAX_Y).mean()))
            checked += 1
        kind, target, proxy = cache[key]
        classes[i] = kind
        if kind == 0 and len(examples) < 20:
            examples.setdefault(key.hex(), dict(genome=key.hex(), target_agreement=target,
                                                max_agreement=proxy))
    exact = np.flatnonzero(classes == 1)
    return classes, int(exact[0]) if len(exact) else None, checked


def run_one(job, cell, initial=None):
    start = time.monotonic()
    seed, pop, cap = (job[k] for k in ("seed", "pop", "cap"))
    arm, mode = cell.split("-")
    cfg = eb.config("sum2", arm, seed, pop, cap, job["vectors"][arm], MASTER)
    idx = training_indices(seed)
    inputs, y = eb.DOMAIN[idx].tolist(), SUM_Y[idx]
    rng = make_rng(cfg)
    row = dict(cell=cell, arm=arm, veto=mode == "veto", phase=job["phase"],
               seed=seed, replicate=job["replicate"], master=MASTER, pop=pop, cap=cap,
               config=asdict(cfg), probs=job["vectors"][arm], training_indices=idx.tolist(),
               training_sha256=hashlib.sha256(eb.DOMAIN[idx].astype("<i8").tobytes()
                                             + y.astype("<i8").tobytes()).hexdigest(),
               complete=False, event=False, time=None, first_gen=None, position=None,
               solver=None, solver_parents=None, verifications=0, processed_candidates=0,
               first_training_100=None, first_max_gen=None, first_max_position=None,
               max_before_solve=False, fully_vetoed=False, peak_veto_fraction=0.,
               history=[], population_digests=[], other_examples=[])
    cache, examples = {}, {}
    parents, previous_classes = None, None
    try:
        if time.monotonic() >= job["deadline"]:
            raise eb.Deadline("deadline before initialization; infrastructure missingness")
        population = build_initial_population(cfg, rng, pop) if initial is None else [g.copy() for g in initial]
        if len(population) != pop:
            raise ValueError("incorrect initial population size")
        for gen in range(cfg.generations + 1):
            if time.monotonic() >= job["deadline"]:
                raise eb.Deadline("deadline during run; infrastructure missingness")
            row["population_digests"].append(hashlib.sha256(np.stack(population).tobytes()).hexdigest())
            cases = eb.predictions(population, inputs) == y[None, :]
            fits = cases.mean(axis=1)
            row["processed_candidates"] += pop
            classes, pos, checked = classify(population, cases, cache, examples)
            row["verifications"] += checked
            max_idx = np.flatnonzero(classes == 2)
            if len(max_idx) and row["first_max_gen"] is None:
                row.update(first_max_gen=gen, first_max_position=int(max_idx[0]))
            if row["first_training_100"] is None and cases.all(axis=1).any():
                row["first_training_100"] = gen
            count = len(max_idx)
            row["peak_veto_fraction"] = max(row["peak_veto_fraction"], count / pop)
            row["history"].append(dict(gen=gen, evaluations=(gen + 1) * pop,
                best=float(fits.max()), mean=float(fits.mean()),
                distinct=len({g.tobytes() for g in population}),
                training_perfect=int(cases.all(axis=1).sum()), exact_max=count,
                other_perfect=int((cases.all(axis=1) & (classes == 0)).sum())))
            if pos is not None:
                row.update(event=True, time=gen * pop + pos + 1, first_gen=gen,
                           position=pos, solver=population[pos].tobytes().hex())
                if parents is not None:
                    i, j, kind, mutated = parents[pos]
                    row["solver_parents"] = dict(indices=[i, j], kind=kind, mutated=mutated,
                        exact_max=[bool(previous_classes[i] == 2),
                                   bool(previous_classes[j] == 2) if j >= 0 else None])
                break
            eligible = classes != 2 if mode == "veto" else None
            if eligible is not None and not eligible.any():
                row["fully_vetoed"] = True
                break
            if gen < cfg.generations:
                parents = []
                population = _reproduce_one_island(population, fits, cfg, rng,
                    cases=cases, lineage=parents, eligible=eligible)
                if eligible is not None:
                    assert all(eligible[i] and (j < 0 or eligible[j]) for i, j, _, _ in parents), "vetoed reproductive parent"
                previous_classes = classes
        row.update(complete=True, time=row["time"] if row["event"] else cap)
        if row["first_max_gen"] is not None:
            row["max_before_solve"] = not row["event"] or (
                (row["first_max_gen"], row["first_max_position"]) <
                (row["first_gen"], row["position"]))
    except eb.Deadline as exc:
        row["error"] = str(exc)
    row["other_examples"] = list(examples.values())
    row["seconds"] = time.monotonic() - start
    return row


def check_identity(ordinary, veto):
    """Hashes cover substantive ordered population bytes, never wall time."""
    first = ordinary["first_max_gen"]
    prefix = len(ordinary["population_digests"]) if first is None else first + 1
    a, b = ordinary["population_digests"], veto["population_digests"]
    if a[:prefix] != b[:prefix] or len(b) < prefix:
        raise RuntimeError(f"identity failure before exposure: {ordinary['arm']}/{ordinary['seed']}")
    if first is None and ordinary["complete"] and veto["complete"]:
        for field in ("time", "event", "solver", "population_digests", "first_max_gen"):
            if ordinary[field] != veto[field]:
                raise RuntimeError(f"unexposed pair diverged in {field}")
    return dict(arm=ordinary["arm"], seed=ordinary["seed"], verified_generations=prefix,
                first_exposure_gen=first, passed=True)


def run_seed(job):
    record = dict(seed=job["seed"], replicate=job["replicate"], phase=job["phase"], cells={}, identity=[])
    for arm in ("U", "R"):
        for mode in ("ord", "veto"):
            cell = f"{arm}-{mode}"
            record["cells"][cell] = run_one(job, cell)
            eb.write_json(job["out"], record)
        a, b = (record["cells"][f"{arm}-{m}"] for m in ("ord", "veto"))
        # A truncated pair is infrastructure missingness; do not demand a
        # prefix it never had time to generate, and do not treat it as passed.
        if a["complete"] and b["complete"]:
            try:
                record["identity"].append(check_identity(a, b))
            except RuntimeError as exc:
                record["identity_error"] = str(exc)
                eb.write_json(job["out"], record)
                raise
    eb.write_json(job["out"], record)
    return record


def jobs_for(spec, out, phase, n, deadline, smoke=False):
    offset = dict(pilot=10000, smoke=20000, main=100000)[phase]
    vectors = {a: ec.vectors(spec, "sum2")[a] for a in ("U", "R")}
    return [dict(seed=MASTER + offset + i, replicate=i, phase=phase,
                 pop=64 if smoke else POP, cap=16384 if smoke else CAP,
                 vectors=vectors, deadline=deadline,
                 out=str(out / "runs" / phase / f"{MASTER + offset + i}.json")) for i in range(n)]


def run_jobs(jobs, workers, out):
    records = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_seed, job) for job in jobs]
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            with (out / "progress.jsonl").open("a") as log:
                log.write(json.dumps(dict(seed=record["seed"], phase=record["phase"],
                    cells={c: {k: r[k] for k in ("time", "event", "complete", "seconds")}
                           for c, r in record["cells"].items()})) + "\n")
            print(f"{record['phase']} seed {record['seed']}: " +
                  ", ".join(f"{c}={r['time']}" for c, r in record["cells"].items()), flush=True)
    return sorted(records, key=lambda r: r["seed"])


def complete(records):
    return bool(records) and all(set(r["cells"]) == set(CELLS) and
        all(v["complete"] for v in r["cells"].values()) and
        len(r["identity"]) == 2 and all(i["passed"] for i in r["identity"]) for r in records)


def values(records):
    """Administrative censoring represented by infinity, never cap imputation."""
    if not complete(records):
        raise ValueError("incomplete four-cell seed records")
    seeds = [r["seed"] for r in records]
    if len(set(seeds)) != len(seeds):
        raise ValueError("duplicate seeds")
    caps = {v["cap"] for r in records for v in r["cells"].values()}
    if len(caps) != 1:
        raise ValueError("different administrative caps")
    for r in records:
        for cell in CELLS:
            v = r["cells"][cell]
            if v["seed"] != r["seed"] or (not v["event"] and v["time"] != v["cap"]):
                raise ValueError("unpaired or nonadministrative censoring")
    return np.array([[r["cells"][c]["time"] if r["cells"][c]["event"] else np.inf
                      for c in CELLS] for r in records], dtype=float)


def median_values(v):
    return np.partition(v, math.ceil(len(v) / 2) - 1, axis=0)[math.ceil(len(v) / 2) - 1]


def ratios(m):
    with np.errstate(invalid="ignore", divide="ignore"):
        c1, pr, pu = m[..., 0] / m[..., 2], m[..., 3] / m[..., 2], m[..., 1] / m[..., 0]
        return np.stack([c1, pr, pu, pr / pu], axis=-1)


def bootstrap(v, seed, boot=BOOT):
    """Resample entire seed rows for all four ratios, retaining nonfinite draws."""
    n, rng = len(v), np.random.default_rng(seed)
    point = ratios(median_values(v))
    samples, estimable = [], []
    k = math.ceil(n / 2) - 1
    for lo in range(0, boot, 250):
        draws = rng.integers(0, n, (min(250, boot - lo), n))
        med = np.partition(v[draws], k, axis=1)[:, k, :]
        r = ratios(med)
        ok_med = np.isfinite(med)
        ok = np.stack([ok_med[:, 0] & ok_med[:, 2], ok_med[:, 3] & ok_med[:, 2],
                       ok_med[:, 1] & ok_med[:, 0], ok_med.all(axis=1)], axis=1)
        samples.append(r)
        estimable.append(ok & np.isfinite(r))
    samples, ok = np.concatenate(samples), np.concatenate(estimable)
    lower = np.quantile(np.where(ok, samples, 0.), ALPHA / 2, axis=0, method="inverted_cdf")
    upper = np.quantile(np.where(ok, samples, np.inf), 1 - ALPHA / 2, axis=0, method="inverted_cdf")
    return {key: dict(ratio=float(point[i]) if np.isfinite(point[i]) else None,
                     lower=float(lower[i]), upper=float(upper[i]) if np.isfinite(upper[i]) else None,
                     finite_fraction=float(ok[:, i].mean()), n=n, alpha=ALPHA,
                     bootstrap_draws=boot, seed=seed, look=1)
            for i, key in enumerate(("C1", "P_R", "P_U", "I"))}


def comparisons(records, boot=BOOT):
    return bootstrap(values(records), MASTER + 400000, boot)


def outcome(c):
    if not c or not ec.reliable(c["C1"]) or c["C1"]["lower"] <= 1:
        return "gate failed: R gain on A not reproduced"
    pr, interaction = c["P_R"], c["I"]
    if ec.reliable(pr):
        if pr["upper"] < 1:
            return "exact shortcut trap"
        if pr["upper"] < TAU:
            return "no practically meaningful contribution" + ("; detectable but small" if pr["lower"] > 1 else "")
        if pr["lower"] > 1:
            if ec.reliable(interaction) and interaction["lower"] > 1:
                return "route supported"
            return "stepping stone real; R advantage unresolved"
    return "unresolved"


def exposure_mask(records):
    # First occurrence strictly before solve (or before the cap for failures).
    return np.array([[r["cells"][f"{a}-ord"]["max_before_solve"] for a in ("U", "R")]
                     for r in records], dtype=bool)


def inject(v, exposed, target_pr):
    """Center actual paired residuals and inject only exposed veto event times.

    Originally censored observations remain infinity. Newly pushed-over-cap
    events censor at cap. No unexposed row can acquire a treatment effect.
    """
    result = v.copy()
    achieved, factors = {}, {}
    for ai, (ordinary, veto, target) in enumerate(((0, 1, 1.), (2, 3, target_pr))):
        base = median_values(v)[ordinary]
        if not np.isfinite(base):
            return None, dict(reason="ordinary pilot median not estimable")
        eligible = exposed[:, ai] & np.isfinite(v[:, veto])
        def transform(log_factor):
            w = v[:, veto].copy()
            w[eligible] *= math.exp(log_factor)
            w[w > CAP] = np.inf
            w = np.maximum(w, 1.)
            return w
        lo, hi = -12., 12.
        wanted = base * target
        for _ in range(70):
            mid = (lo + hi) / 2
            m = median_values(transform(mid)[:, None])[0]
            if m < wanted:
                lo = mid
            else:
                hi = mid
        candidates = [((lo + hi) / 2), lo, hi, -12., 12.]
        log_factor = min(candidates, key=lambda f: abs(median_values(transform(f)[:, None])[0] / wanted - 1))
        transformed = transform(log_factor)
        med = median_values(transformed[:, None])[0]
        if not np.isfinite(med) or abs(med / wanted - 1) > 1e-6:
            return None, dict(reason="target unattainable without changing unexposed pairs", arm=("U", "R")[ai], target=target)
        result[:, veto] = transformed
        achieved[("P_U", "P_R")[ai]] = float(med / base)
        factors[("U", "R")[ai]] = math.exp(log_factor)
    return result, dict(achieved=achieved, factors=factors,
                        I=achieved["P_R"] / achieved["P_U"])


def power(records, out, deadline, trials=300, boot=2000, sizes=(600, 800)):
    v = values(records)
    exposed = exposure_mask(records)
    null, null_info = inject(v, exposed, 1.)
    alt, alt_info = inject(v, exposed, 1.6)
    result = dict(trials=trials, inner_bootstrap_draws=boot, alpha=ALPHA,
                  exposure_counts=exposed.sum(axis=0).tolist(), injection_null=null_info,
                  injection_alternative=alt_info, sizes={}, n=None, feasible=False,
                  reason=None, paired_log_time_correlations={}, pilot_censoring={})
    for ai, arm in enumerate(("U", "R")):
        # Observed cap times for this descriptive correlation only, clearly
        # labelled; inference still uses censored KM medians.
        x = np.log([r["cells"][f"{arm}-ord"]["time"] for r in records])
        y = np.log([r["cells"][f"{arm}-veto"]["time"] for r in records])
        corr = np.corrcoef(x, y)[0, 1] if x.std() and y.std() else np.nan
        result["paired_log_time_correlations"][arm] = float(corr) if np.isfinite(corr) else None
    result["correlation_note"] = "Descriptive observed log times, administrative failures placed at cap; not a power assumption."
    for c in CELLS:
        result["pilot_censoring"][c] = sum(not r["cells"][c]["event"] for r in records)
    if null is None or alt is None:
        result["reason"] = "injection infeasible"
        eb.write_json(out / "power.json", result)
        return result
    for n in sizes:
        hits = dict(interaction=0, R_penalty=0, null_small=0, complete_route=0)
        rng = np.random.default_rng(eb.stream_seed(f"power/{n}", MASTER + 300000))
        for trial in range(trials):
            if time.monotonic() >= deadline:
                raise eb.Deadline("deadline in power simulation; infrastructure missingness")
            # Identical whole-record resample for alternative and null.
            draws = rng.integers(0, len(v), n)
            seed = int(rng.integers(0, 2**63))
            ca, cn = bootstrap(alt[draws], seed, boot), bootstrap(null[draws], seed, boot)
            positive = {k: ec.reliable(ca[k]) and ca[k]["lower"] > 1 for k in ("C1", "P_R", "I")}
            hits["interaction"] += bool(positive["I"])
            hits["R_penalty"] += bool(positive["P_R"])
            hits["complete_route"] += bool(all(positive.values()))
            hits["null_small"] += bool(ec.reliable(cn["P_R"]) and cn["P_R"]["upper"] < TAU)
            if (trial + 1) % 25 == 0:
                print(f"power n={n}: {trial + 1}/{trials}", flush=True)
        result["sizes"][str(n)] = {k: eb.binomial(count, trials) for k, count in hits.items()}
        passed = all(hits[k] / trials >= .8 for k in ("interaction", "R_penalty", "null_small"))
        if passed:
            result.update(n=n, feasible=True)
        eb.write_json(out / "power.json", result)
        if passed:
            break
    if not result["feasible"]:
        result["reason"] = "specified marginal powers below .80 at affordable sizes"
        eb.write_json(out / "power.json", result)
    return result


def runtime_design(pilot, powered, seconds_left, workers):
    design = dict(feasible=False, n=powered.get("n"), power_passed=powered["feasible"],
                  seconds_remaining=seconds_left, reason=powered.get("reason"))
    if not complete(pilot):
        design["reason"] = "incomplete pilot"
        return design
    costs = {c: 1.5 * max(r["cells"][c]["seconds"] / r["cells"][c]["processed_candidates"]
                         for r in pilot) * CAP for c in CELLS}
    design["conservative_cap_seconds_by_cell"] = costs
    if powered["feasible"]:
        estimate = powered["n"] * sum(costs.values()) / workers + max(costs.values()) + 600
        design.update(estimated_seconds=estimate, feasible=estimate <= seconds_left,
                      reason=None if estimate <= seconds_left else "main exceeds remaining deadline")
    return design


def cell_summary(records):
    result = {}
    for cell in CELLS:
        rows = [r["cells"][cell] for r in records]
        result[cell] = dict(n=len(rows), complete=sum(r["complete"] for r in rows),
            solves=sum(r["complete"] and r["event"] for r in rows),
            km_median=eb.km_curve(rows)[2],
            exposed_before_solve=sum(r["max_before_solve"] for r in rows),
            fully_vetoed=sum(r["fully_vetoed"] for r in rows),
            peak_exact_max_fraction=[r["peak_veto_fraction"] for r in rows],
            first_training_100=[r["first_training_100"] for r in rows],
            remaining_other_perfect=sum(h["other_perfect"] for r in rows for h in r["history"]),
            immediate_max_parent=sum(bool(r["solver_parents"]) and any(v is True for v in r["solver_parents"]["exact_max"]) for r in rows))
    return result


def plot_results(out, records, stage):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for cell, color in zip(CELLS, ("#555555", "#999999", "#1f77b4", "#e07b22")):
        rows = [r["cells"][cell] for r in records]
        if not rows:
            continue
        x, y, _ = eb.km_curve(rows)
        axes[0, 0].step(x, y, where="post", color=color, label=cell)
        for r in rows:
            h = r["history"]
            x = [v["evaluations"] for v in h]
            axes[0, 1].plot(x, [v["mean"] for v in h], color=color, alpha=.1)
            axes[1, 0].plot(x, [v["distinct"] / r["pop"] for v in h], color=color, alpha=.1)
            axes[1, 1].plot(x, [v["exact_max"] / r["pop"] for v in h], color=color, alpha=.1)
    for ax, label in zip(axes.flat, ("P(exact solve), KM", "Mean training fitness", "Distinct / population", "Exact max2 / population")):
        ax.set(xscale="symlog", xlabel="Candidate evaluations (trajectories: batch end)", ylabel=label, ylim=(0, 1))
    if records:
        axes[0, 0].legend()
    fig.suptitle(stage + ": individual trajectories stop at solve/cap; pilot excluded from confirmation")
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    plt.close(fig)


def finish(out, result, records, pilot):
    result["cells"] = cell_summary(records) if records else {}
    if records and complete(records) and result["stage"] == "finished":
        result["comparisons"] = comparisons(records)
        result["outcome"] = outcome(result["comparisons"])
        c = result["comparisons"]
        if ec.reliable(c["C1"]) and ec.reliable(c["I"]) and c["C1"]["ratio"] != 1:
            result["descriptive_share_log_gain"] = math.log(c["I"]["ratio"]) / math.log(c["C1"]["ratio"])
    else:
        result["comparisons"] = {}
        result["outcome"] = "smoke only" if result["smoke_only"] else "infrastructure incomplete" if result["incomplete"] else "pilot-only feasibility stop"
    eb.write_json(out / "result.json", result)
    plot_results(out, records or pilot, result["stage"])
    lines = ["# Exact shortcut reproductive-access experiment", f"Stage: {result['stage']}. Outcome: **{result['outcome']}**.",
             "Scope: sum2, frozen R, TAG L64 P1024 lexicase, balanced shortcut-admitting sets, exact max2 only.",
             "Pilot data are excluded from final contrasts. Net removal cost allows compensation by other routes. Reproductive access may operate through population composition or mating; immediate-parent counts do not exclude earlier ancestry.",
             f"Design: {json.dumps(result.get('design', {}))}"]
    if result["comparisons"]:
        lines += ["| Contrast | Ratio | 98.75% CI | Finite fraction |", "|---|---|---|---|"]
        for name, c in result["comparisons"].items():
            lines.append(f"| {name} | {c['ratio']} | {c['lower']}, {c['upper']} | {c['finite_fraction']} |")
    (out / "report.md").write_text("\n\n".join(lines[:5]) + "\n\n" + "\n".join(lines[5:]) + "\n")
    if not result["incomplete"]:
        (out / "COMPLETE").write_text(result["stage"] + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seconds", type=float, default=10500)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    if args.workers < 1 or args.seconds <= 0:
        ap.error("positive workers and seconds required")
    out = Path(os.environ["RUN_DIR"]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "result.json").exists() or (out / "runs").exists():
        raise RuntimeError("RUN_DIR contains an earlier run; use a fresh directory")
    os.environ["RAYON_NUM_THREADS"] = "1"
    deadline = time.monotonic() + args.seconds
    spec = json.loads(eb.SPEC_PATH.read_text())
    ec.validate_vectors(spec)
    eb.write_json(out / "vectors.json", {a: ec.vectors(spec, "sum2")[a] for a in ("U", "R")})
    eb.write_json(out / "sampler_audit.json", sampler_audit())
    result = dict(stage="initializing", smoke_only=args.smoke, incomplete=False,
        master_seed=MASTER, workers=args.workers, internal_seconds=args.seconds,
        comparisons={}, metric_definitions=METRIC_DEFINITIONS, next="stop",
        vector_source_sha256=hashlib.sha256(eb.SPEC_PATH.read_bytes()).hexdigest(),
        statistics=dict(family="2026-10-05-1957 exact-shortcut reproductive-access",
                        tests=4, looks=1, alpha=ALPHA, bootstrap_draws=BOOT, min_finite_fraction=.99),
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        git_dirty=bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()))
    records, pilot = [], []
    try:
        eb.write_json(out / "result.json", result)
        if args.smoke:
            result["stage"] = "smoke"
            records = run_jobs(jobs_for(spec, out, "smoke", 2, deadline - 10, smoke=True), args.workers, out)
            result["incomplete"] = not complete(records)
        else:
            result["stage"] = "pilot"
            pilot = run_jobs(jobs_for(spec, out, "pilot", 50, deadline - 600), args.workers, out)
            eb.write_json(out / "pilot.json", pilot)
            result["pilot_cells"] = cell_summary(pilot)
            if not complete(pilot):
                result.update(stage="pilot_incomplete", incomplete=True)
            else:
                result["stage"] = "power"
                eb.write_json(out / "result.json", result)
                powered = power(pilot, out, deadline - 600)
                design = runtime_design(pilot, powered, deadline - time.monotonic(), args.workers)
                result["design"] = design
                eb.write_json(out / "design.json", design)
                if not design["feasible"]:
                    result["stage"] = "pilot_only"
                else:
                    result["stage"] = "main"
                    eb.write_json(out / "result.json", result)
                    records = run_jobs(jobs_for(spec, out, "main", design["n"], deadline - 600), args.workers, out)
                    result.update(stage="finished" if complete(records) else "main_incomplete", incomplete=not complete(records))
        finish(out, result, records, pilot)
        return int(result["incomplete"])
    except (eb.Deadline, RuntimeError) as exc:
        result.update(stage="infrastructure_error", incomplete=True, error=str(exc))
        finish(out, result, records, pilot)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
