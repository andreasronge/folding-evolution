"""Fixed inherited-token acquisition study, approved run 2026-10-07-2243.

All outputs belong to RUN_DIR. Stage zero is a cost gate only. No calibration,
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

MASTER = 202610072243
FAMILIES = ("sum", "max")
ARMS = ("inherited", "broken")
TARGETS = ("sum1", "sum5", "max1", "max5")
POP = 1024
EPISODES = 48
GENERATIONS = 128  # reproduction generations; includes a generation-zero census
CAP = 262144
WORKERS = 10
QUEUE_SECONDS = 12600


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
    rng = make_rng(cfg)
    modifier = Modifier(cfg.pop_size, np.random.default_rng(seed("modifier/" + name + "/" + arm)))
    row = dict(job, master=MASTER, program_seed=cfg.seed,
               modifier_stream="modifier/" + name + "/" + arm, config=asdict(cfg),
               complete=False, episodes=[], trajectories=[], price=[],
               evaluations=0, evaluation_seconds=0.0, verifier_seconds=0.0,
               reproduction_seconds=0.0, reset_seconds=0.0, generations=0)
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
                      verifier_seconds=0.0, shuffles=0)
            row["episodes"].append(ep)
            for gen in range(job.get("generations", GENERATIONS) + 1):
                if time.monotonic() >= deadline:
                    raise eb.Deadline("acquisition timing deadline; not censoring")
                stamp = time.monotonic()
                pred = eb.predictions(population, t.inputs)
                row["evaluation_seconds"] += time.monotonic() - stamp
                row["evaluations"] += cfg.pop_size
                cases = pred == t.labels[None, :]
                fits = cases.mean(axis=1)
                stamp = time.monotonic()
                pos, checked, shortcuts = eb.first_exact(population, cases, target, cache)
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
                    break
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
                depth_mean=float(modifier.depth.mean()), depth_max=int(modifier.depth.max())))
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


def acquisition_jobs(out, phase, n=16, **options):
    return [dict(family=f, arm=a, replicate=i, phase=phase,
                 out=str(out / "acquisition" / phase / f / a / f"{i}.json"), **options)
            for i in range(n) for f in FAMILIES for a in ARMS]


def projection(acquisitions, searches, workers=WORKERS):
    # Four timing runs are not a tail distribution. Double the slower family
    # arm's cost and charge the incomplete final worker batch in full. For
    # scoring use the worst measured search for each target, rather than its
    # mean; charge 704 searches/target (512 learned + 192 references).
    acquisition_batches = sum(
        np.ceil(32 / workers) * 2 * max(r["seconds"] for r in acquisitions if r["family"] == f)
        for f in FAMILIES
    )
    scoring_batches = sum(
        np.ceil(704 / workers) * 2 * max(r["seconds"] for r in searches if r["task"] == t)
        for t in TARGETS
    )
    stage0 = (sum(r["seconds"] for r in acquisitions)
              + sum(r["seconds"] for r in searches))  # serial is conservative
    total = float(stage0 + acquisition_batches + scoring_batches + 300)
    return dict(acquisition_seconds=float(acquisition_batches),
                scoring_seconds=float(scoring_batches), stage0_seconds=float(stage0),
                overhead_seconds=300, total_seconds=total,
                queue_timeout_seconds=QUEUE_SECONDS,
                feasible=all(r["complete"] for r in acquisitions + searches) and total < QUEUE_SECONDS - 600,
                policy="2x slower-family acquisition, 2x target-max scoring, rounded batches; cost only")


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
    out.mkdir(parents=True, exist_ok=True)
    eb.write_json(out / "validation.json", validate())
    acquisitions = parallel(acquire, acquisition_jobs(out, "timing", n=1), workers)
    spec = json.loads(eb.SPEC_PATH.read_text())
    jobs = []
    for t in TARGETS:
        family = t[:-1]
        for name, p in (("uniform", spec["vectors"]["uniform"]),
                        ("hand", spec["vectors"]["hand_" + family]),
                        ("fit", spec["vectors"][family])):
            for i in range(4):
                j = frozen_job(t, name, p, 900000 + i, "timing")
                j["out"] = str(out / "timing_searches" / t / name / f"{i}.json")
                jobs.append(j)
        # Include both heterogeneous-acquisition extractions in the timing probe.
        for a in ARMS:
            p = next(r["probs"] for r in acquisitions if r["family"] == family and r["arm"] == a)
            for i in range(4):
                j = frozen_job(t, "timing_" + a, p, 900000 + i, "timing")
                j["out"] = str(out / "timing_searches" / t / a / f"{i}.json")
                jobs.append(j)
    searches = parallel(score, jobs, workers)
    summary = dict(projection=projection(acquisitions, searches, workers),
                   acquisition=[{k: r[k] for k in ("family", "arm", "complete", "seconds", "solves",
                                                   "generations", "evaluations", "verifier_seconds",
                                                   "evaluation_seconds", "reproduction_seconds")}
                                | {"depth_mean": float(np.mean(r["depth"])), "depth_max": max(r["depth"])}
                                for r in acquisitions],
                   frozen={t: dict(n=sum(r["task"] == t for r in searches),
                                   solves=sum(r["task"] == t and r["event"] for r in searches),
                                   incomplete=sum(r["task"] == t and not r["complete"] for r in searches),
                                   max_seconds=max(r["seconds"] for r in searches if r["task"] == t),
                                   verifier_seconds=sum(r["verifier_seconds"] for r in searches if r["task"] == t))
                           for t in TARGETS})
    eb.write_json(out / "stage0.json", summary)
    return summary


def manifest():
    spec = json.loads(eb.SPEC_PATH.read_text())
    return dict(master=MASTER, families=FAMILIES, arms=ARMS, targets=TARGETS,
                pop=POP, tape_length=64, episodes=EPISODES, generations=GENERATIONS,
                sigma=0.03, theta_bounds=[-3, 3], floor=0.1 / 22,
                selection="lexicase", elites=2, crossover="v2", crossover_rate=0.7,
                crossover_mate="selected", mutation_rate=0.015,
                acquisition_replicates=list(range(16)), shared_scoring_indices=list(range(16)),
                reference_scoring_indices=list(range(64)), cap=CAP,
                reference_spec_sha256=hashlib.sha256(eb.SPEC_PATH.read_bytes()).hexdigest(),
                references=spec, rng="SHA256 named SeedSequence, separate program/modifier",
                ordering="reset/evaluate/exact check/one broken permutation/check stop/select recipient/inherit/mutate",
                extraction="final population mean probabilities, no subsequent reset",
                lineage_depth="nonelite recipient-copy generations with modifier mutation; elites retain depth",
                frozen_search_count=2816,
                queue_timeout_seconds=QUEUE_SECONDS)


def crossed_effect(a, b, rng, draws=10000, paired_runs=False):
    """a/b: [family, acquisition run, target, shared search seed] log costs.

    Paired acquisition runs use the same sampled indices across arms. References
    have one fixed vector (no acquisition variance). Shared search seeds resample
    within target and are reused for both arms and every vector.
    """
    a, b = np.asarray(a), np.asarray(b)
    if paired_runs and a.shape[1] != b.shape[1]:
        raise ValueError("paired acquisitions need the same number of runs")
    samples = np.empty((draws, 2))
    for i in range(draws):
        for f in range(2):
            ai = rng.integers(a.shape[1], size=a.shape[1])
            bi = ai if paired_runs else rng.integers(b.shape[1], size=b.shape[1])
            delta = []
            for t in range(2):
                si = rng.integers(a.shape[3], size=a.shape[3])
                delta.append(a[f, ai, t][:, si].mean() - b[f, bi, t][:, si].mean())
            samples[i, f] = np.mean(delta)
    def result(point, boot):
        lo, hi = np.quantile(np.exp(boot), [0.025, 0.975])
        return dict(ratio=float(np.exp(point)), lower=float(lo), upper=float(hi))
    point = a.mean(axis=(1, 2, 3)) - b.mean(axis=(1, 2, 3))
    return dict(pooled=result(point.mean(), samples.mean(axis=1)),
                families={f: result(point[i], samples[:, i]) for i, f in enumerate(FAMILIES)},
                draws=draws, method="crossed percentile bootstrap: family/arm runs and shared target seeds")


def analyze(out, acquisitions, searches):
    if not all(r["complete"] for r in acquisitions + searches):
        raise RuntimeError("infrastructure missingness cannot be counted as censoring")
    cells = {(r["task"], r["arm"], r["replicate"]): r for r in searches}
    def tensor(arm):
        return np.array([[[[np.log(cells[(f + t, f"{arm}/{i}", s)]["time"])
                            for s in range(16)] for t in ("1", "5")]
                          for i in range(16)] for f in FAMILIES])
    inherited, broken = tensor("inherited"), tensor("broken")
    primary = crossed_effect(broken, inherited, np.random.default_rng(seed("bootstrap/primary")),
                             paired_runs=True)
    refs = {}
    for name in ("uniform", "hand", "fit"):
        # Conditional on the paired 16-seed block for contrasts with learned maps;
        # extra 48 reference seeds contribute only to descriptive reference summaries.
        ref = np.array([[[[np.log(cells[(f + t, name, s)]["time"])
                         for s in range(16)] for t in ("1", "5")]] for f in FAMILIES])
        refs[name] = crossed_effect(inherited, ref,
                                   np.random.default_rng(seed("bootstrap/" + name)))
    solves = {}
    for target in TARGETS:
        solves[target] = {}
        for arm in ARMS + ("uniform", "hand", "fit"):
            rs = [r for r in searches if r["task"] == target and
                  (r["arm"].startswith(arm + "/") if arm in ARMS else r["arm"] == arm)]
            solves[target][arm] = dict(n=len(rs), solves=sum(r["event"] for r in rs),
                                       capped_geometric_cost=float(np.exp(np.mean([np.log(r["time"]) for r in rs]))),
                                       arithmetic_evaluations=float(np.mean([r["time"] for r in rs])),
                                       mean_seconds=float(np.mean([r["seconds"] for r in rs])))
    c = primary["pooled"]
    endpoint_rule = ("linkage advantage" if c["lower"] > 1 and c["ratio"] >= 1.5 else
                     "limited procedure" if c["upper"] < 1.5 else "unresolved")
    break_even = {}
    for f in FAMILIES:
        acq = np.mean([r["seconds"] for r in acquisitions if r["family"] == f and r["arm"] == "inherited"])
        break_even[f] = {}
        for ref in ("uniform", "hand", "fit"):
            saving = np.mean([solves[f + t][ref]["mean_seconds"] - solves[f + t]["inherited"]["mean_seconds"]
                              for t in ("1", "5")])
            break_even[f][ref] = dict(acquisition_seconds=float(acq), seconds_saved_per_search=float(saving),
                                     searches=float(acq / saving) if saving > 0 else None)
    result = dict(endpoint="capped geometric search cost; censored at 262144 evaluations",
                  primary=primary, inherited_over_reference=refs, solves=solves,
                  endpoint_rule=endpoint_rule,
                  useful_direction=refs["uniform"]["pooled"]["ratio"] < 1,
                  useful_interval=refs["uniform"]["pooled"]["upper"] < 1,
                  break_even=break_even,
                  run_scores=[dict(family=f, arm=arm, replicate=i,
                                   capped_geometric_cost=float(np.exp(values[fi, i].mean())),
                                   solves=sum(cells[(f + t, f"{arm}/{i}", s)]["event"]
                                              for t in ("1", "5") for s in range(16)))
                              for fi, f in enumerate(FAMILIES)
                              for arm, values in (("inherited", inherited), ("broken", broken))
                              for i in range(16)],
                  exposure=[dict(family=r["family"], arm=r["arm"], replicate=r["replicate"],
                                 generations=r["generations"], depth_mean=float(np.mean(r["depth"])),
                                 solves=r["solves"]) for r in acquisitions],
                  interpretation="Rule is on capped costs. Heavy censoring/negligible exposure can leave mechanism unresolved; see plan.md.")
    eb.write_json(out / "result.json", result)
    plot(out, acquisitions)
    (out / "report.md").write_text(
        f"Capped cost broken/inherited: {c['ratio']:.4g} [{c['lower']:.4g}, {c['upper']:.4g}].\n\n"
        f"Endpoint rule: {endpoint_rule}. Useful direction vs uniform: {result['useful_direction']}; "
        f"interval below uniform: {result['useful_interval']}.\n\n"
        "Training targets only on a development bank. Per-family results, solve counts, "
        "exposure and break-even costs are in result.json; modifiers and Price covariances "
        "are in individual acquisition files. Similar arm gains do not identify their cause.\n")
    (out / "COMPLETE").write_text("ok\n")
    return result


def plot(out, rows):
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
                             (3, "CONST_1"), (16, "CONST_5"), (5 if family == "sum" else 18, "aggregator")):
                ax.plot(np.arange(1, p.shape[1] + 1), p.mean(axis=0)[:, op], label=name)
            ax.set(title=family + "/" + arm, xlabel="episode", ylabel="mean probability")
            ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "trajectories.png", dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.environ.get("RUN_DIR"))
    ap.add_argument("--mode", choices=("validate", "smoke", "stage0", "full"), default="full")
    ap.add_argument("--workers", type=int, default=WORKERS)
    args = ap.parse_args()
    if not args.out:
        ap.error("set RUN_DIR or --out")
    if args.workers <= 0:
        ap.error("workers must be positive")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    design = manifest()
    design["git_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    design["git_dirty"] = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
    sources = (Path(__file__), Path(eb.__file__), Path(tagged.__file__))
    from folding_evolution.chem_tape import evolve
    design["source_sha256"] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (*sources, Path(evolve.__file__))}
    eb.write_json(out / "manifest.json", design)
    if args.mode == "validate":
        eb.write_json(out / "validation.json", validate())
        return 0
    if args.mode == "smoke":
        eb.write_json(out / "validation.json", validate())
        rows = parallel(acquire, acquisition_jobs(out, "smoke", n=1, pop=32, episodes=2, generations=3), args.workers)
        eb.write_json(out / "smoke.json", rows)
        return 0 if all(r["complete"] for r in rows) else 1
    stage = stage_zero(out, args.workers)
    if args.mode == "stage0":
        return 0 if stage["projection"]["feasible"] else 2
    if not stage["projection"]["feasible"]:
        (out / "INFEASIBLE").write_text("stage-zero conservative cost projection exceeds budget or incomplete timing\n")
        return 2
    acquisitions = parallel(acquire, acquisition_jobs(out, "main"), args.workers)
    if not all(r["complete"] for r in acquisitions):
        raise RuntimeError("incomplete acquisition; do not score partial modifier vectors")
    jobs = []
    for r in acquisitions:
        for threshold in ("1", "5"):
            for index in range(16):
                j = frozen_job(r["family"] + threshold, f"{r['arm']}/{r['replicate']}", r["probs"], index)
                j["out"] = str(out / "searches" / j["task"] / j["arm"] / f"{index}.json")
                jobs.append(j)
    spec = design["references"]
    for t in TARGETS:
        f = t[:-1]
        for name, p in (("uniform", spec["vectors"]["uniform"]), ("hand", spec["vectors"]["hand_" + f]),
                        ("fit", spec["vectors"][f])):
            for index in range(64):
                j = frozen_job(t, name, p, index)
                j["out"] = str(out / "searches" / t / name / f"{index}.json")
                jobs.append(j)
    searches = parallel(score, jobs, args.workers)
    analyze(out, acquisitions, searches)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
