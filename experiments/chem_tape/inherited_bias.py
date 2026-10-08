"""Fixed inherited-token acquisition study, approved run 2026-10-08-0918.

All outputs belong to RUN_DIR. Preparation timing is a cost gate only. No calibration,
checkpoint selection, threshold-2 exposure, or outcomes change the fixed roster.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import evolve_bias as eb
from folding_evolution.chem_tape import tagged
from folding_evolution.chem_tape.evolve import _reproduce_one_island, make_rng

MASTER = 202610080843
FAMILIES = ("sum", "max")
ARMS = ("inherited", "broken")
TARGETS = ("sum1", "sum5", "max1", "max5")
POP = 1024
EPISODES = 48
GENERATIONS = 128  # reproduction generations; includes a generation-zero census
CAP = 262144
WORKERS = 10
QUEUE_SECONDS = 10800
ACQUISITIONS = 20
SHARED_SEEDS = 16
REFERENCES = ("uniform", "hand", "fit")


def reference_arms(include_fit=True):
    return REFERENCES if include_fit else REFERENCES[:2]


def seed(name):
    return eb.stream_seed(name, MASTER)


def probabilities(theta):
    theta = np.asarray(theta, dtype=float)
    if theta.shape[-1] != 22 or not np.isfinite(theta).all():
        raise ValueError("theta must have 22 finite log weights")
    w = np.exp(theta - theta.max(axis=-1, keepdims=True))
    return 0.9 * w / w.sum(axis=-1, keepdims=True) + 0.1 / 22


class Modifier:
    """Rows are attached to current individuals; recipient is the sole donor."""
    def __init__(self, pop, rng, sigma=0.03, theta=None):
        self.theta = np.zeros((pop, 22)) if theta is None else np.array(theta, copy=True)
        self.depth = np.zeros(pop, dtype=np.int64)
        self.rng, self.sigma = rng, sigma
        self.last_covariance = np.zeros(22)

    def shuffle(self):
        order = self.rng.permutation(len(self.theta))
        self.theta = self.theta[order]
        self.depth = self.depth[order]
        return order

    def __call__(self, recipients, elites):
        counts = np.bincount(recipients, minlength=len(self.theta))
        self.last_covariance = (
            (self.theta - self.theta.mean(axis=0)) * (counts - counts.mean())[:, None]
        ).mean(axis=0)
        child = self.theta[recipients].copy()
        depth = self.depth[recipients].copy()
        if self.sigma:
            child[elites:] += self.rng.normal(0, self.sigma, child[elites:].shape)
        child[elites:] = np.clip(child[elites:], -3, 3)
        depth[elites:] += 1
        self.theta, self.depth = child, depth
        return probabilities(child[elites:])


def reset_population(modifier, rng):
    # Preserve Python initialization draws of the legacy harness, row by row.
    return [tagged.random_genotype(64, rng, op_p=p) for p in probabilities(modifier.theta)]


def acquire(job):
    start = time.monotonic()
    family, arm, replicate = (job[k] for k in ("family", "arm", "replicate"))
    name = f"{job['phase']}/{family}/{replicate}"
    program_seed = int(seed("program/" + name).generate_state(1)[0])
    cfg = eb.config(family + "1", arm, program_seed, job.get("pop", POP), CAP,
                    [1 / 22] * 22, master=MASTER)
    cfg = replace(cfg, generations=job.get("generations", GENERATIONS))
    rng = make_rng(cfg)
    modifier = Modifier(cfg.pop_size, np.random.default_rng(seed("modifier/" + name + "/" + arm)))
    row = dict(job, master=MASTER, program_seed=cfg.seed,
               modifier_stream="modifier/" + name + "/" + arm, config=asdict(cfg),
               complete=False, episodes=[], trajectories=[], price=[],
               evaluations=0, evaluation_seconds=0.0, verifier_seconds=0.0,
               reproduction_seconds=0.0, reset_seconds=0.0, generations=0, censuses=0)
    deadline = start + job.get("seconds", 1200)
    try:
        for episode in range(job.get("episodes", EPISODES)):
            target = family + ("1" if episode % 2 == 0 else "5")
            cfg = replace(cfg, task=target)
            training_seed = int(seed(f"cases/{name}/{episode}").generate_state(1)[0])
            t = eb.make_task(target, training_seed, master=MASTER)
            stamp = time.monotonic()
            population = reset_population(modifier, rng)
            row["reset_seconds"] += time.monotonic() - stamp
            ep_start = time.monotonic()
            cache = {}
            ep = dict(episode=episode, target=target, training_seed=training_seed,
                      training_indices=eb.training_indices(target, training_seed, MASTER).tolist(),
                      solved=False, generations=0, verifications=0, shortcuts=0,
                      verifier_seconds=0.0, shuffles=0, censuses=0, evaluations=0)
            row["episodes"].append(ep)
            for gen in range(job.get("generations", GENERATIONS) + 1):
                if time.monotonic() >= deadline:
                    raise eb.Deadline("acquisition timing deadline; not censoring")
                stamp = time.monotonic()
                pred = eb.predictions(population, t.inputs)
                row["evaluation_seconds"] += time.monotonic() - stamp
                row["evaluations"] += cfg.pop_size
                row["censuses"] += 1
                ep["censuses"] += 1
                ep["evaluations"] += cfg.pop_size
                cases = pred == t.labels[None, :]
                fits = cases.mean(axis=1)
                stamp = time.monotonic()
                pos, checked, shortcuts = (None, 0, 0) if ep["solved"] else eb.first_exact(population, cases, target, cache)
                elapsed = time.monotonic() - stamp
                row["verifier_seconds"] += elapsed
                ep["verifier_seconds"] += elapsed
                ep["verifications"] += checked
                ep["shortcuts"] += shortcuts
                # One post-evaluation permutation, including gen0, final censuses,
                # and immediate solves. Elites are assigned only after this step.
                if arm == "broken":
                    modifier.shuffle()
                    ep["shuffles"] += 1
                if pos is not None:
                    ep.update(solved=True, first_gen=gen, position=pos,
                              evaluations_to_exact=gen * cfg.pop_size + pos + 1,
                              solver=population[pos].tobytes().hex())
                if gen < job.get("generations", GENERATIONS):
                    stamp = time.monotonic()
                    population = _reproduce_one_island(population, fits, cfg, rng,
                                                       cases=cases, modifier=modifier)
                    row["reproduction_seconds"] += time.monotonic() - stamp
                    row["generations"] += 1
                    ep["generations"] += 1
                    row["price"].append(dict(episode=episode, gen=gen,
                                             covariance=modifier.last_covariance.tolist()))
            ep["seconds"] = time.monotonic() - ep_start
            row["trajectories"].append(dict(
                episode=episode, mean_theta=modifier.theta.mean(axis=0).tolist(),
                sd_theta=modifier.theta.std(axis=0).tolist(),
                mean_p=probabilities(modifier.theta).mean(axis=0).tolist(),
                depth_mean=float(modifier.depth.mean()), depth_max=int(modifier.depth.max()),
                uniform_l1=float(np.abs(probabilities(modifier.theta).mean(axis=0) - 1 / 22).sum())))
        row["complete"] = True
    except eb.Deadline as exc:
        row["error"] = str(exc)
    row.update(seconds=time.monotonic() - start,
               solves=sum(e["solved"] for e in row["episodes"]),
               theta=modifier.theta.tolist(), depth=modifier.depth.tolist(),
               probs=probabilities(modifier.theta).mean(axis=0).tolist())
    if job.get("out"):
        eb.write_json(job["out"], row)
    return row


def frozen_job(target, vector, probs, index, phase="main"):
    return dict(task=target, arm=vector, probs=list(probs), seed=MASTER + 100000 + index,
                replicate=index, phase=phase, master=MASTER, pop=POP, cap=CAP)


def score(job):
    return eb.run_one(dict(job, deadline=time.monotonic() + job.get("seconds", 600)))


def parallel(function, jobs, workers=WORKERS):
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(function, job) for job in jobs]
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print(json.dumps({k: row[k] for k in (
                ("family", "arm", "replicate", "complete", "solves", "seconds")
                if function is acquire else ("task", "arm", "replicate", "complete", "event", "seconds")
            )}), flush=True)
    return rows


def acquisition_jobs(out, phase, n=ACQUISITIONS, **options):
    return [dict(family=f, arm=a, replicate=i, phase=phase,
                 out=str(out / "acquisition" / phase / f / a / f"{i}.json"), **options)
            for i in range(n) for f in FAMILIES for a in ARMS]


def projection(acquisitions, searches, workers=WORKERS, reference_seeds=SHARED_SEEDS,
               include_fit=True):
    """Roster-weighted means, final-worker overhead, then 2x + 15 min.

    Old frozen timings price only their own vector kind; no new frozen
    performance is inspected during preparation. Four acquisitions are not a
    tail estimate, and this allowance is not a runtime guarantee.
    """
    acquisition = sum(r["seconds"] * ACQUISITIONS for r in acquisitions) / workers
    acquisition += (workers - 1) / workers * max(r["seconds"] for r in acquisitions)
    scoring = {}
    for family in FAMILIES:
        work, means = 0.0, []
        for threshold in ("1", "5"):
            for arm in ARMS + reference_arms(include_fit):
                rs = [r for r in searches if r["task"] == family + threshold and
                      r["arm"] in (arm, "timing_" + arm)]
                if not rs:
                    raise ValueError(f"missing timing cell {family + threshold}/{arm}")
                mean = float(np.mean([r["seconds"] for r in rs]))
                means.append(mean)
                count = ACQUISITIONS * SHARED_SEEDS if arm in ARMS else reference_seeds
                work += mean * count
        scoring[family] = work / workers + (workers - 1) / workers * max(means)
    timeouts = dict(acquisition=int(np.ceil(2 * acquisition + 300)),
                    sum=int(np.ceil(2 * scoring["sum"] + 150)),
                    max=int(np.ceil(2 * scoring["max"] + 150)), analysis=300)
    total = sum(timeouts.values())
    return dict(acquisition_seconds=acquisition, scoring_seconds=scoring,
                expected_minutes=(acquisition + sum(scoring.values())) / 60,
                timeout_seconds=timeouts, total_seconds=total,
                reference_seeds=reference_seeds, workers=workers,
                reference_arms=reference_arms(include_fit),
                feasible=all(r["complete"] for r in acquisitions + searches) and total <= QUEUE_SECONDS,
                policy="roster-weighted cell means + 0.9 slowest-cell final-worker allowance; 2x + 900 seconds")


def planted(target):
    # CONST_1=3, CONST_5=16; SUM=5, MAX=18, GT=8, INPUT=1, SEP=20.
    ops = [20, 1, 5 if target.startswith("sum") else 18,
           3 if target.endswith("1") else 16, 8]
    return np.array(ops + [0] * (64 - len(ops)) + [0] * 64, dtype=np.uint8)


def validate():
    """Operational stage-zero checks; deterministic and excluded from inference."""
    audits = {}
    for target in TARGETS:
        t = eb.make_task(target, MASTER, master=MASTER)
        want = np.array([int((sum(x) if target.startswith("sum") else max(x)) > int(target[-1]))
                         for x in eb.DOMAIN.tolist()])
        assert np.array_equal(want, eb.labels(target, eb.DOMAIN))
        assert np.array_equal(eb.predictions([planted(target)], eb.DOMAIN_LIST)[0], want)
        assert all(t.label_fn(x) == y for x, y in zip(t.inputs, t.labels))
        cases = eb.predictions([planted(target)], t.inputs) == t.labels
        assert eb.first_exact([planted(target)], cases, target, {})[0] == 0
        assert int(t.labels.sum()) == 32
        audits[target] = dict(positives=int(want.sum()), training_positives=32, exact_solver=True)
    extreme = np.random.default_rng(1).uniform(-3, 3, (100, 22))
    p = probabilities(extreme)
    assert np.allclose(p.sum(axis=1), 1) and np.all(p >= 0.1 / 22)
    before = eb.predictions([planted("sum1")], eb.DOMAIN_LIST)
    probabilities(extreme)  # no resident tape is reinterpreted by theta
    assert np.array_equal(before, eb.predictions([planted("sum1")], eb.DOMAIN_LIST))
    # Distinct rows catch recipient/mate confusion and elite mutation.
    m = Modifier(8, np.random.default_rng(4), sigma=0,
                 theta=np.arange(8 * 22).reshape(8, 22) / 100)
    theta, depth = m.theta.copy(), np.arange(8)
    m.depth = depth.copy()
    order = m.shuffle()
    assert np.array_equal(m.theta, theta[order]) and np.array_equal(m.depth, depth[order])
    recipients = np.array([7, 6, 1, 1, 3, 0, 2, 5])
    source, source_depth = m.theta.copy(), m.depth.copy()
    m(recipients, 2)
    assert np.array_equal(m.theta, source[recipients])
    assert np.array_equal(m.depth[:2], source_depth[recipients[:2]])
    assert np.array_equal(m.depth[2:], source_depth[recipients[2:]] + 1)
    replay = []
    for i in range(20):
        target = TARGETS[i % 4]
        cfg = eb.config(target, "uniform", i, 16, 64, [1 / 22] * 22, master=MASTER)
        a_rng, b_rng = make_rng(cfg), make_rng(cfg)
        a = eb.build_initial_population(cfg, a_rng, 16)
        mod = Modifier(16, np.random.default_rng(seed(f"validation/{i}")), sigma=0)
        b = reset_population(mod, b_rng)
        t = eb.make_task(target, i, master=MASTER)
        for _ in range(3):
            assert np.array_equal(a, b), f"initial/reproduction mismatch seed {i}"
            cases = eb.predictions(a, t.inputs) == t.labels
            a = _reproduce_one_island(a, cases.mean(axis=1), cfg, a_rng, cases=cases)
            b = _reproduce_one_island(b, cases.mean(axis=1), cfg, b_rng, cases=cases, modifier=mod)
        assert np.array_equal(a, b)
        replay.append(i)
    return dict(targets=audits, sigma_zero_legacy_replay_seeds=replay,
                support_floor=0.1 / 22, distinct_row_bookkeeping=True,
                theta_does_not_reinterpret=True)


def stage_zero(out, workers=WORKERS):
    """Only re-time acquisitions; frozen timing is taken from approved prior evidence."""
    start = time.monotonic()
    eb.write_json(out / "validation.json", validate())
    acquisitions = parallel(acquire, acquisition_jobs(out, "timing", n=1), workers)
    eb.write_json(out / "timing.json", dict(wall_seconds=time.monotonic() - start,
                 worker_seconds=sum(r["seconds"] for r in acquisitions),
                 acquisition=acquisitions))
    return acquisitions


def manifest(reference_seeds=SHARED_SEEDS, include_fit=True):
    spec = json.loads(eb.SPEC_PATH.read_text())
    return dict(master=MASTER, families=FAMILIES, arms=ARMS, targets=TARGETS,
                pop=POP, tape_length=64, episodes=EPISODES, generations=GENERATIONS,
                sigma=0.03, theta_bounds=[-3, 3], floor=0.1 / 22,
                selection="lexicase", elites=2, crossover="v2", crossover_rate=0.7,
                crossover_mate="selected", mutation_rate=0.015,
                acquisition_replicates=list(range(ACQUISITIONS)), shared_scoring_indices=list(range(SHARED_SEEDS)),
                reference_scoring_indices=list(range(reference_seeds)), cap=CAP,
                reference_arms=list(reference_arms(include_fit)),
                reference_spec_sha256=hashlib.sha256(eb.SPEC_PATH.read_bytes()).hexdigest(),
                references=spec, rng="SHA256 named SeedSequence, separate program/modifier",
                ordering="reset/evaluate/exact check/one broken permutation/continue through final census/select recipient/inherit/mutate",
                extraction="final population mean probabilities, no subsequent reset",
                lineage_depth="nonelite recipient-copy generations with modifier mutation; elites retain depth",
                frozen_search_count=ACQUISITIONS * 4 * 2 * SHARED_SEEDS + 4 * len(reference_arms(include_fit)) * reference_seeds,
                queue_timeout_seconds=QUEUE_SECONDS)


def classify(effect):
    return ("acquired" if effect["lower"] > 1 and effect["ratio"] >= 1.5 else
            "bounded" if effect["upper"] < 1.5 else "unresolved")


def crossed_effects(tensors, draws=10000):
    """One shared seed resample across all vectors/contrasts; paired run indices.

    Tensors are [acquisition, target, scoring seed] log evaluation costs for
    one family. Fixed reference vectors have one acquisition row.
    """
    contrasts = dict(uniform_over_inherited=("uniform", "inherited"),
                     broken_over_inherited=("broken", "inherited"),
                     broken_over_uniform=("broken", "uniform"),
                     inherited_over_scaffold=("inherited", "hand"))
    if "fit" in tensors:
        contrasts["fit_over_inherited"] = ("fit", "inherited")
    rng = np.random.default_rng(seed("bootstrap/" + tensors.pop("family")))
    samples = {name: np.empty(draws) for name in contrasts}
    n = tensors["inherited"].shape[0]
    for draw in range(draws):
        runs = rng.integers(n, size=n)
        indices = [rng.integers(SHARED_SEEDS, size=SHARED_SEEDS) for _ in range(2)]
        means = {}
        for arm, values in tensors.items():
            ri = runs if arm in ARMS else np.array([0])
            means[arm] = np.mean([values[ri, t][:, indices[t]].mean() for t in range(2)])
        for name, (a, b) in contrasts.items():
            samples[name][draw] = means[a] - means[b]
    result = {}
    for name, (a, b) in contrasts.items():
        lo, hi = np.quantile(np.exp(samples[name]), [0.025, 0.975])
        result[name] = dict(ratio=float(np.exp(tensors[a].mean() - tensors[b].mean())),
                            lower=float(lo), upper=float(hi))
    return result


def check_acquisitions(rows):
    expected = {(f, a, i) for f in FAMILIES for a in ARMS for i in range(ACQUISITIONS)}
    if len(rows) != len(expected) or {(r["family"], r["arm"], r["replicate"]) for r in rows} != expected:
        raise RuntimeError("acquisition roster missing or duplicate")
    for r in rows:
        if (not r["complete"] or r["master"] != MASTER or r["phase"] != "main" or
                r["generations"] != EPISODES * GENERATIONS or
                r["censuses"] != EPISODES * (GENERATIONS + 1) or
                r["evaluations"] != EPISODES * (GENERATIONS + 1) * POP or
                len(r["episodes"]) != EPISODES or
                len(r["trajectories"]) != EPISODES or len(r["price"]) != EPISODES * GENERATIONS):
            raise RuntimeError("incomplete or wrong-schedule acquisition; cannot extract a partial vector")
        for e, ep in enumerate(r["episodes"]):
            if (ep["target"] != r["family"] + ("1" if e % 2 == 0 else "5") or
                    ep["generations"] != GENERATIONS or ep["censuses"] != GENERATIONS + 1 or
                    ep["evaluations"] != (GENERATIONS + 1) * POP or
                    ep["shuffles"] != (GENERATIONS + 1 if r["arm"] == "broken" else 0)):
                raise RuntimeError("wrong episode schedule")
        p = np.asarray(r["probs"])
        if not np.allclose(p, probabilities(r["theta"]).mean(axis=0)):
            raise RuntimeError("wrong final extraction")


def scoring_jobs(out, acquisitions, family, reference_seeds=SHARED_SEEDS, include_fit=True):
    jobs = []
    for r in acquisitions:
        if r["family"] != family:
            continue
        for threshold in ("1", "5"):
            for index in range(SHARED_SEEDS):
                jobs.append(frozen_job(family + threshold, f"{r['arm']}/{r['replicate']}", r["probs"], index))
    spec = json.loads(eb.SPEC_PATH.read_text())
    for threshold in ("1", "5"):
        for name in reference_arms(include_fit):
            key = "hand_" + family if name == "hand" else family if name == "fit" else name
            for index in range(reference_seeds):
                jobs.append(frozen_job(family + threshold, name, spec["vectors"][key], index))
    for j in jobs:
        j["out"] = str(out / "searches" / j["task"] / j["arm"] / f"{j['replicate']}.json")
    return jobs


def analyze(out, acquisitions, searches, reference_seeds=SHARED_SEEDS, draws=10000,
            include_fit=True):
    check_acquisitions(acquisitions)
    if not all(r["complete"] for r in searches):
        raise RuntimeError("infrastructure missingness cannot be counted as censoring")
    cells = {(r["task"], r["arm"], r["replicate"]): r for r in searches}
    references = reference_arms(include_fit)
    expected_jobs = [j for f in FAMILIES for j in scoring_jobs(out, acquisitions, f, reference_seeds, include_fit)]
    expected = {(j["task"], j["arm"], j["replicate"]) for j in expected_jobs}
    if len(cells) != len(searches) or set(cells) != expected:
        raise RuntimeError("frozen roster missing or duplicate")
    for j in expected_jobs:
        r = cells[(j["task"], j["arm"], j["replicate"])]
        if (r["master"] != MASTER or r["seed"] != j["seed"] or r["pop"] != POP or
                r["cap"] != CAP or not np.array_equal(r["probs"], j["probs"]) or
                not 0 < r["time"] <= CAP or (not r["event"] and r["time"] != CAP)):
            raise RuntimeError("wrong frozen parameters or capped cost")
    summaries = {}
    for target in TARGETS:
        summaries[target] = {}
        for arm in ARMS + references:
            rs = [r for r in searches if r["task"] == target and
                  (r["arm"].startswith(arm + "/") if arm in ARMS else r["arm"] == arm)]
            summaries[target][arm] = dict(n=len(rs), solves=sum(r["event"] for r in rs),
                capped_geometric_cost=float(np.exp(np.mean([np.log(r["time"]) for r in rs]))),
                arithmetic_evaluations=float(np.mean([r["time"] for r in rs])),
                mean_seconds=float(np.mean([r["seconds"] for r in rs])))
    families, run_scores = {}, []
    for f in FAMILIES:
        tensors = {}
        for arm in ARMS + references:
            names = [f"{arm}/{i}" for i in range(ACQUISITIONS)] if arm in ARMS else [arm]
            tensors[arm] = np.array([[[np.log(cells[(f + t, name, s)]["time"])
                                      for s in range(SHARED_SEEDS)] for t in ("1", "5")] for name in names])
        effects = crossed_effects(dict(tensors, family=f), draws=draws)
        verdict = classify(effects["uniform_over_inherited"])
        linkage, sc = effects["broken_over_inherited"], effects["inherited_over_scaffold"]
        continuation = ("propose transfer for strategy review" if verdict == "acquired" and
                        linkage["lower"] > 1 and sc["lower"] < 2 else "return to strategy")
        spread = {}
        for arm in ARMS:
            costs = tensors[arm].mean(axis=(1, 2))
            spread[arm] = float(costs.std(ddof=1))
            for i, cost in enumerate(costs):
                run_scores.append(dict(family=f, arm=arm, replicate=i,
                    capped_geometric_cost=float(np.exp(cost)),
                    solves=sum(cells[(f + t, f"{arm}/{i}", s)]["event"] for t in ("1", "5") for s in range(SHARED_SEEDS))))
        acq = float(np.mean([r["seconds"] for r in acquisitions if r["family"] == f and r["arm"] == "inherited"]))
        break_even = {}
        # Compare the matched shared-seed blocks for savings.
        for ref in references:
            savings = {}
            for metric in ("seconds", "time"):
                learned_mean = np.mean([cells[(f + t, f"inherited/{i}", s)][metric]
                    for t in ("1", "5") for i in range(ACQUISITIONS) for s in range(SHARED_SEEDS)])
                reference_mean = np.mean([cells[(f + t, ref, s)][metric]
                    for t in ("1", "5") for s in range(SHARED_SEEDS)])
                savings[metric] = float(reference_mean - learned_mean)
            acq_evals = EPISODES * (GENERATIONS + 1) * POP
            break_even[ref] = dict(acquisition_seconds=acq, acquisition_evaluations=acq_evals,
                seconds_saved_per_search=savings["seconds"], evaluations_saved_per_search=savings["time"],
                searches_by_seconds=acq / savings["seconds"] if savings["seconds"] > 0 else None,
                searches_by_evaluations=acq_evals / savings["time"] if savings["time"] > 0 else None)
        families[f] = dict(primary=effects["uniform_over_inherited"], effects=effects,
            verdict=verdict, next_action=continuation, between_run_log_sd=spread,
            inherited_within_twofold_scaffold=sc["upper"] < 2,
            scaffold_twofold_disadvantage_not_established=sc["lower"] < 2,
            linkage_unidentified_by_both_censored=all(summaries[f + t][a]["solves"] == 0 for t in ("1", "5") for a in ARMS),
            break_even=break_even)
    result = dict(endpoint="geometric evaluation cost, censored at cap; equal target weights",
        primary="uniform/inherited, per family only", families=families, solves=summaries,
        bootstrap=dict(draws=draws, method="crossed percentile, paired acquisitions and shared target seed indices across every vector/contrast"),
        reference_arms=references, reference_extras="none" if reference_seeds == SHARED_SEEDS else "descriptive only",
        run_scores=run_scores,
        exposure=[{k: r[k] for k in ("family", "arm", "replicate", "generations", "censuses", "evaluations", "solves", "seconds", "verifier_seconds")}
                  | dict(depth_mean=float(np.mean(r["depth"])), depth_max=max(r["depth"])) for r in acquisitions],
        scope="fixed-duration discovery plus maintenance; development bank training targets; equal schedule does not equalize lineage depth or selection intensity")
    eb.write_json(out / "result.json", result)
    plot(out, acquisitions, searches, references)
    lines = []
    for f, r in families.items():
        c = r["primary"]
        lines.append(f"{f}: uniform/inherited {c['ratio']:.4g} [{c['lower']:.4g}, {c['upper']:.4g}], {r['verdict']}. {r['next_action']}.")
    (out / "report.md").write_text("\n\n".join(lines) + "\n\n" + result["scope"] +
        ". S=inherited/scaffold; lower<2 is uncertainty, upper<2 supports within-twofold. Similar gains do not identify cause.\n")
    (out / "COMPLETE").write_text("ok\n")
    return result


def plot(out, rows, searches=(), references=REFERENCES):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for fi, family in enumerate(FAMILIES):
        for ai, arm in enumerate(ARMS):
            rs = [r for r in rows if r["family"] == family and r["arm"] == arm]
            p = np.array([[ep["mean_p"] for ep in r["trajectories"]] for r in rs])
            ax = axes[fi, ai]
            for op, name in ((1, "INPUT"), (8, "GT"), (15, "CONST_2"),
                             (3, "CONST_1"), (16, "CONST_5"), (20, "SEP_A"),
                             (12, "SLOT_12"), (13, "SLOT_13"), (5 if family == "sum" else 18, "aggregator")):
                ax.plot(np.arange(1, p.shape[1] + 1), p.mean(axis=0)[:, op], label=name)
            ax.set(title=family + "/" + arm, xlabel="episode", ylabel="mean probability")
            ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "trajectories.png", dpi=150)
    plt.close(fig)

    # Predetermined seed/run zero, never select examples by successful outcome.
    # Search histories stop on solving; these panels are illustrative trajectories.
    if searches:
        fig, axes = plt.subplots(2, 4, figsize=(15, 7))
        for ti, target in enumerate(TARGETS):
            for arm in ("inherited/0", "broken/0") + tuple(references):
                row = next(r for r in searches if r["task"] == target and r["arm"] == arm and r["replicate"] == 0)
                history = row["history"]
                axes[0, ti].plot([h["gen"] for h in history], [h["best"] for h in history], label=arm)
                axes[1, ti].plot([h["gen"] for h in history], [h["distinct"] for h in history], label=arm)
            axes[0, ti].set(title=target, ylabel="best training fitness, seed/run 0")
            axes[1, ti].set(xlabel="generation (ends at solve/cap)", ylabel="distinct tapes, seed/run 0")
            axes[0, ti].legend(fontsize=6)
        fig.tight_layout()
        fig.savefig(out / "search_trajectories.png", dpi=150)
        plt.close(fig)


def price_artifacts(out, timing, frozen_timings, workers=WORKERS):
    records = json.loads((timing / "timing.json").read_text())
    acquisitions = records["acquisition"]
    searches = [json.loads(p.read_text()) for p in sorted(frozen_timings.rglob("*.json"))]
    full = projection(acquisitions, searches, workers)
    without_fit = projection(acquisitions, searches, workers, include_fit=False)
    chosen = full if full["feasible"] else without_fit
    summary = dict(full=full, without_fit=without_fit, chosen=chosen,
        timing_wall_seconds=records["wall_seconds"],
        timing_workers=min(workers, 4),
        timing_utilization=records["worker_seconds"] / (4 * records["wall_seconds"]),
        acquisition=[{k: r[k] for k in ("family", "arm", "complete", "seconds", "solves", "generations", "censuses", "evaluations", "verifier_seconds", "evaluation_seconds", "reproduction_seconds")}
                     for r in acquisitions],
        source_timing_directory=str(frozen_timings.resolve()),
        timing_source_sha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(frozen_timings.rglob("*.json"))})
    eb.write_json(out / "projection.json", summary)
    return summary


def load_acquisitions(root):
    rows = [json.loads(p.read_text()) for p in sorted((root / "acquisition" / "main").glob("*/*/*.json"))]
    check_acquisitions(rows)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.environ.get("RUN_DIR"))
    ap.add_argument("--mode", choices=("validate", "smoke", "stage0", "price", "acquire", "score", "analyze"), required=True)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--family", choices=FAMILIES)
    ap.add_argument("--timing", type=Path)
    ap.add_argument("--frozen-timings", type=Path)
    ap.add_argument("--acquisitions", type=Path)
    ap.add_argument("--sum-scores", type=Path)
    ap.add_argument("--max-scores", type=Path)
    ap.add_argument("--reference-seeds", type=int, choices=(SHARED_SEEDS,), default=SHARED_SEEDS)
    ap.add_argument("--omit-fit", action="store_true",
                    help="approved cost fallback only; must match across all stages")
    args = ap.parse_args()
    if not args.out or args.workers <= 0:
        ap.error("set RUN_DIR or --out and positive workers")
    if args.mode in ("score", "analyze") and args.acquisitions is None:
        ap.error("--acquisitions required")
    if args.mode == "score" and args.family is None:
        ap.error("--family required")
    if args.mode == "analyze" and (args.sum_scores is None or args.max_scores is None):
        ap.error("both scoring directories required")
    if args.mode == "price" and (args.timing is None or args.frozen_timings is None):
        ap.error("--timing and --frozen-timings required")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    design = manifest(args.reference_seeds, include_fit=not args.omit_fit)
    design.update(mode=args.mode, workers=args.workers,
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        git_dirty=bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()))
    from folding_evolution.chem_tape import evolve
    sources = [Path(__file__), Path(eb.__file__), Path(tagged.__file__), Path(evolve.__file__)]
    design["source_sha256"] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    for name in ("acquisitions", "sum_scores", "max_scores"):
        root = getattr(args, name)
        if root:
            source = root / "manifest.json"
            prior = json.loads(source.read_text())
            if any(prior[k] != design[k] for k in (
                    "master", "source_sha256", "reference_scoring_indices", "reference_arms",
                    "reference_spec_sha256", "frozen_search_count")):
                raise RuntimeError("input manifest differs from frozen design")
            design[name] = dict(directory=str(root.resolve()), manifest_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    eb.write_json(out / "manifest.json", design)
    if args.mode == "validate":
        eb.write_json(out / "validation.json", validate())
    elif args.mode == "smoke":
        eb.write_json(out / "validation.json", validate())
        rows = parallel(acquire, acquisition_jobs(out, "smoke", n=1, pop=32, episodes=2, generations=3), args.workers)
        eb.write_json(out / "smoke.json", rows)
        if not all(r["complete"] and r["generations"] == 6 and r["censuses"] == 8 and r["evaluations"] == 256 for r in rows):
            return 1
    elif args.mode == "stage0":
        rows = stage_zero(out, args.workers)
        return 0 if all(r["complete"] for r in rows) else 2
    elif args.mode == "price":
        summary = price_artifacts(out, args.timing, args.frozen_timings, args.workers)
        print(json.dumps(summary["chosen"]), flush=True)
        return 0 if summary["chosen"]["feasible"] else 2
    elif args.mode == "acquire":
        eb.write_json(out / "validation.json", validate())
        rows = parallel(acquire, acquisition_jobs(out, "main"), args.workers)
        check_acquisitions(rows)
        (out / "ACQUISITIONS_COMPLETE").write_text("ok\n")
    elif args.mode == "score":
        rows = load_acquisitions(args.acquisitions)
        jobs = scoring_jobs(out, rows, args.family, args.reference_seeds, include_fit=not args.omit_fit)
        searches = parallel(score, jobs, args.workers)
        if not all(r["complete"] for r in searches):
            raise RuntimeError("infrastructure missingness, scoring stage incomplete")
        (out / "SCORING_COMPLETE").write_text("ok\n")
    elif args.mode == "analyze":
        rows = load_acquisitions(args.acquisitions)
        searches = [json.loads(p.read_text()) for root in (args.sum_scores, args.max_scores)
                    for p in sorted((root / "searches").rglob("*.json"))]
        analyze(out, rows, searches, args.reference_seeds, include_fit=not args.omit_fit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
