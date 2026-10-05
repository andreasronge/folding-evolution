"""Frozen held-out family-bias evolution study (2026-10-05-1705).

Run as a module. All artifacts live under RUN_DIR. The queue performs pilot,
descriptive sampling, design freeze, and up to two confirmatory looks.
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
from scipy.stats import beta
from _folding_rust import rust_tag_outputs, rust_tag_screen

from folding_evolution.chem_tape.alphabet import TaskAlphabet
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import (
    _reproduce_one_island,
    _run_stats,
    build_initial_population,
    make_rng,
)
from folding_evolution.chem_tape.tasks import Task
from experiments.chem_tape.family_bias import DOMAIN, labels

MASTER = 202610051705
TASKS = ("sum2", "max2")
ARMS = ("uniform", "matched", "mismatched", "hand")
PAIRS = (("uniform", "matched"), ("mismatched", "matched"), ("matched", "hand"))
ALPHA = 0.05 / 12
CAPS = (262144, 1048576, 4194304)
SIZES = (256, 1024)
SPEC_PATH = Path(__file__).with_name("evolve_bias_vectors.json")
DOMAIN_LIST = DOMAIN.tolist()


class Deadline(RuntimeError):
    pass


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def stream_seed(name, master=None):
    words = np.frombuffer(hashlib.sha256(name.encode()).digest()[:16], dtype="<u4")
    return np.random.SeedSequence(
        [MASTER if master is None else master, *words.tolist()]
    )


def vectors(spec, task):
    family = task[:-1]
    other = "max" if family == "sum" else "sum"
    return dict(
        zip(
            ARMS,
            [spec["vectors"][k] for k in ("uniform", family, other, "hand_" + family)],
        )
    )


def validate_spec(spec):
    for name, q in spec["vectors"].items():
        p = np.asarray(q)
        if (
            p.shape != (22,)
            or not np.isfinite(p).all()
            or (p <= 0).any()
            or not np.isclose(p.sum(), 1)
        ):
            raise ValueError(f"invalid vector {name}")
    for family, scaffold in (("sum", [1, 8, 5, 11]), ("max", [1, 8, 18])):
        q = np.asarray(spec["vectors"]["hand_" + family])
        assert np.array_equal(
            q[scaffold], np.asarray(spec["vectors"][family])[scaffold]
        )
        assert np.array_equal(q[[2, 3, 15, 16]], np.full(4, 1 / 22))
        other = [i for i in range(22) if i not in scaffold + [2, 3, 15, 16]]
        assert np.ptp(q[other]) == 0


def training_indices(task, seed, master=None):
    rng = np.random.default_rng(stream_seed(f"training/{task}/{seed}", master))
    y = labels(task, DOMAIN)
    idx = np.concatenate(
        [rng.choice(np.flatnonzero(y == v), 32, replace=True) for v in (0, 1)]
    )
    return idx[rng.permutation(64)]


def make_task(task, seed, master=None):
    idx = training_indices(task, seed, master)
    # All slots inert, threshold 0: literal constants must be encoded in tapes.
    return Task(
        task,
        "intlist",
        DOMAIN[idx].tolist(),
        labels(task, DOMAIN[idx]),
        TaskAlphabet(),
        lambda x: int((sum(x) if task.startswith("sum") else max(x)) > 2),
    )


def config(task, arm, seed, pop, cap, probs, master=None):
    if cap % pop or cap < pop or pop <= 2:
        raise ValueError("cap must be a positive whole number of populations")
    # Evolution gets an independent substream; paired cells share its seed.
    evo_seed = int(stream_seed(f"evolution/{task}/{seed}", master).generate_state(1)[0])
    return ChemTapeConfig(
        task=task,
        arm="TAG",
        alphabet="tagged",
        tape_length=64,
        n_examples=64,
        holdout_size=0,
        pop_size=pop,
        generations=cap // pop - 1,
        seed=evo_seed,
        elite_count=2,
        selection_mode="lexicase",
        tagged_crossover="v2",
        crossover_rate=0.7,
        crossover_mate="selected",
        mutation_rate=0.015,
        disable_early_termination=True,
        fast_rng=True,
        backend="numpy",
        op_weights=",".join(f"{i}:{p:.17g}" for i, p in enumerate(probs)),
    )


def predictions(population, inputs):
    tapes = np.stack(population).astype(np.uint8, copy=False)
    return np.asarray(rust_tag_outputs(tapes.tobytes(), 64, inputs), dtype=np.int64)


def first_exact(population, cases, task, cache, saved=None, gen=None):
    """Return the earliest exact candidate, not a training champion.

    Full genome byte keys preserve order and avoid semantic-hash collisions.
    A cache hit is the same exhaustive verification, not a sampled proxy.
    """
    full_y = labels(task, DOMAIN)
    other_y = labels("max2" if task == "sum2" else "sum2", DOMAIN)
    checked = shortcuts = 0
    for i in np.flatnonzero(cases.all(axis=1)):
        genome = population[i]
        key = genome.tobytes()
        if key not in cache:
            # Bounded cache; eviction may cause re-verification but no aliasing.
            if len(cache) >= 65536:
                cache.clear()
            full_pred = predictions([genome], DOMAIN_LIST)[0]
            cache[key] = bool(np.array_equal(full_pred, full_y))
            if saved is not None and not cache[key] and len(saved) < 20:
                saved.setdefault(
                    key.hex(),
                    dict(
                        genome=key.hex(),
                        first_gen=gen,
                        target_agreement=float((full_pred == full_y).mean()),
                        other_family_agreement=float((full_pred == other_y).mean()),
                    ),
                )
            checked += 1
        if cache[key]:
            return int(i), checked, shortcuts
        shortcuts += 1
    return None, checked, shortcuts


def run_one(job, initial=None):
    start = time.monotonic()
    task, arm, seed, pop, cap = (job[k] for k in ("task", "arm", "seed", "pop", "cap"))
    master_kw = {"master": job["master"]} if "master" in job else {}
    cfg = config(task, arm, seed, pop, cap, job["probs"], **master_kw)
    t = make_task(task, seed, **master_kw)
    rng = make_rng(cfg)
    row = {k: v for k, v in job.items() if k not in ("deadline", "out")}
    row.update(
        config=asdict(cfg),
        training_indices=training_indices(task, seed, **master_kw).tolist(),
        complete=False,
        event=False,
        time=None,
        first_gen=None,
        position=None,
        solver=None,
        verifications=0,
        shortcut_candidates=0,
        history=[],
        processed_candidates=0,
    )
    row["training_sha256"] = hashlib.sha256(
        np.asarray(t.inputs, dtype="<i8").tobytes()
        + np.asarray(t.labels, dtype="<i8").tobytes()
    ).hexdigest()
    population = initial
    cache = {}
    saved = {} if job.get("component_diagnostics") else None
    if saved is not None:
        row.update(
            training_history=[], first_training_075=None, first_training_100=None
        )
    try:
        if time.monotonic() >= job["deadline"]:
            raise Deadline("deadline before initialization")
        if population is None:
            population = build_initial_population(cfg, rng, pop)
        if len(population) != pop:
            raise ValueError("incorrect initial population size")
        for gen in range(cfg.generations + 1):
            if time.monotonic() >= job["deadline"]:
                raise Deadline("deadline during run; infrastructure missingness")
            pred = predictions(population, t.inputs)
            row["processed_candidates"] += pop
            cases = pred == t.labels[None, :]
            fits = cases.mean(axis=1)
            pos, checked, shortcuts = first_exact(
                population, cases, task, cache, saved, gen
            )
            if saved is not None:
                best = float(fits.max())
                row["training_history"].append(dict(gen=gen, best=best))
                for threshold, name in (
                    (0.75, "first_training_075"),
                    (1.0, "first_training_100"),
                ):
                    if row[name] is None and best >= threshold:
                        row[name] = gen
            row["verifications"] += checked
            row["shortcut_candidates"] += shortcuts
            last = pos is not None or gen == cfg.generations
            if gen % 25 == 0 or last:
                row["history"].append(
                    dict(
                        gen=gen,
                        evaluations=(gen + 1) * pop,
                        seconds=time.monotonic() - start,
                        best=float(fits.max()),
                        mean=float(fits.mean()),
                        distinct=len({g.tobytes() for g in population}),
                        training_perfect=int(cases.all(axis=1).sum()),
                        run_census=_run_stats(gen, population, cfg),
                    )
                )
            if pos is not None:
                row.update(
                    event=True,
                    time=gen * pop + pos + 1,
                    first_gen=gen,
                    position=pos,
                    solver=population[pos].tobytes().hex(),
                )
                break
            if gen < cfg.generations:
                population = _reproduce_one_island(
                    population, fits, cfg, rng, cases=cases
                )
        row.update(complete=True, time=row["time"] if row["event"] else cap)
    except Deadline as exc:
        row["error"] = str(exc)
    if saved is not None:
        row["shortcuts"] = list(saved.values())
    row["seconds"] = time.monotonic() - start
    if job.get("out"):
        write_json(job["out"], row)
    return row


def km_curve(rows):
    if not rows or any(not r["complete"] for r in rows):
        return [], [], None
    times = sorted({r["time"] for r in rows})
    at_risk = len(rows)
    survival = 1.0
    x, cdf, median = [0], [0.0], None
    for t in times:
        events = sum(r["time"] == t and r["event"] for r in rows)
        censors = sum(r["time"] == t and not r["event"] for r in rows)
        survival *= 1 - events / at_risk
        x.append(t)
        cdf.append(1 - survival)
        if median is None and survival <= 0.5 + 1e-12:
            median = t
        at_risk -= events + censors
    return x, cdf, median


def bootstrap_medians(rows, draws):
    # All censoring is administrative at one common cap, so KM reaches 0.5
    # at the ceil(n/2)-th event order statistic (or never). An infinity slot
    # represents a censored candidate, not an imputed solve at the cap.
    if len({r["cap"] for r in rows}) != 1:
        raise ValueError("bootstrap requires shared administrative censoring cap")
    if any(
        not r["complete"] or (not r["event"] and r["time"] != r["cap"]) for r in rows
    ):
        raise ValueError("incomplete or non-administrative censoring")
    v = np.array([r["time"] if r["event"] else np.inf for r in rows])
    k = math.ceil(len(rows) / 2) - 1
    return np.partition(v[draws], k, axis=1)[:, k]


def compare(a, b, seed, boot=100000, alpha=ALPHA):
    out = dict(
        n=len(a),
        seed=seed,
        alpha=alpha,
        bootstrap_draws=boot,
        method="paired KM median ratio percentile bootstrap",
        verdict="U",
        ratio=None,
        lower=None,
        upper=None,
        finite_fraction=None,
    )
    if not a or len(a) != len(b) or any(not r["complete"] for r in a + b):
        return out
    a, b = sorted(a, key=lambda r: r["seed"]), sorted(b, key=lambda r: r["seed"])
    if [r["seed"] for r in a] != [r["seed"] for r in b]:
        raise ValueError("unpaired seeds")
    ma, mb = km_curve(a)[2], km_curve(b)[2]
    if ma is None or mb is None:
        return out
    out["ratio"] = ma / mb
    rng = np.random.default_rng(seed)
    ratio_chunks = []
    finite = 0
    for lo in range(0, boot, 2000):
        draws = rng.integers(0, len(a), (min(2000, boot - lo), len(a)))
        aa, bb = bootstrap_medians(a, draws), bootstrap_medians(b, draws)
        ok = np.isfinite(aa) & np.isfinite(bb)
        finite += int(ok.sum())
        # Nonestimable resamples form an unbounded envelope, never dropped.
        with np.errstate(invalid="ignore"):
            r = aa / bb
        ratio_chunks.append((np.where(ok, r, 0.0), np.where(ok, r, np.inf)))
    lower = np.quantile(
        np.concatenate([v[0] for v in ratio_chunks]), alpha / 2, method="inverted_cdf"
    )
    upper = np.quantile(
        np.concatenate([v[1] for v in ratio_chunks]),
        1 - alpha / 2,
        method="inverted_cdf",
    )
    out.update(
        lower=float(lower),
        upper=float(upper) if np.isfinite(upper) else None,
        finite_fraction=finite / boot,
    )
    if finite / boot < 0.99 or not np.isfinite(upper):
        return out
    if lower > 1 and out["ratio"] >= 2:
        out["verdict"] = "F"
    elif lower > 0.5 and upper < 2:
        out["verdict"] = "E"
    elif upper < 1 and out["ratio"] <= 0.5:
        out["verdict"] = "R"
    return out


def overall(comparisons, incomplete=False, screen=False):
    if incomplete or len(comparisons) != 6:
        return "Unresolved"

    def v(task, a, b):
        return comparisons[f"{task}/{a}/{b}"]["verdict"]

    if all(v(t, a, b) == "F" for t in TASKS for a, b in PAIRS[:2]):
        return (
            "A'" if all(v(t, "matched", "hand") in ("F", "E") for t in TASKS) else "A"
        )
    if all(v(t, "uniform", "matched") == "E" for t in TASKS):
        # The approved screen routes no-large-effect results to strategy.
        return "Unresolved" if screen else "B"
    # A resolved one-family gain or reverse establishes Partial, even when
    # other cells remain U. A specificity-only result with unknown baseline
    # cannot establish evolutionary benefit.
    if any(v(t, "uniform", "matched") in ("F", "R") for t in TASKS):
        return "Partial"
    return "Unresolved"


def next_cells(comparisons):
    return {
        (t, arm)
        for key, c in comparisons.items()
        if c["verdict"] == "U"
        for t, a, b in [key.split("/")]
        for arm in (a, b)
    }


def binomial(k, n):
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return dict(hits=k, n=n, p=k / n, lower=lo, upper=hi)


def random_cdf(n, p):
    return -np.expm1(np.asarray(n) * np.log1p(-p))


def sampler_audit():
    audit = {}
    for t in TASKS:
        idx = training_indices(t, MASTER + 100000)
        y = labels(t, DOMAIN[idx])
        proxy = labels("max2" if t == "sum2" else "sum2", DOMAIN[idx])
        assert len(y) == 64 and y.sum() == 32
        audit[t] = dict(
            seed=MASTER + 100000,
            indices=idx.tolist(),
            positives=int(y.sum()),
            n=len(y),
            balance=float(y.mean()),
            constant_accuracy=0.5,
            proxy="max>2" if t == "sum2" else "sum>2",
            proxy_train_accuracy=float((proxy == y).mean()),
            proxy_domain_accuracy=float(
                (
                    labels("max2" if t == "sum2" else "sum2", DOMAIN)
                    == labels(t, DOMAIN)
                ).mean()
            ),
            distinct_cases=len(set(idx.tolist())),
            both_labels=True,
        )
    return audit


def sample_hand(spec, out, n, deadline):
    data = {}
    for t in TASKS:
        q = vectors(spec, t)["hand"]
        rng = np.random.default_rng(stream_seed("sampling/hand/" + t))
        idx = training_indices(t, MASTER + 40000)
        screen = DOMAIN[idx].tolist()
        screen_y = [labels(t, DOMAIN[idx]).tolist()]
        full_y = [labels(t, DOMAIN).tolist()]
        done = hits = 0
        start = time.monotonic()
        while done < n:
            if time.monotonic() >= deadline:
                raise Deadline("hand sampling incomplete")
            count = min(100000, n - done)
            tapes = np.concatenate(
                [
                    rng.choice(22, (count, 64), p=q).astype(np.uint8),
                    rng.integers(0, 64, (count, 64), dtype=np.uint8),
                ],
                axis=1,
            )
            candidates = rust_tag_screen(tapes.tobytes(), 64, screen, screen_y)
            if candidates:
                selected = tapes[[i for i, _ in candidates]]
                hits += len(
                    rust_tag_screen(selected.tobytes(), 64, DOMAIN_LIST, full_y)
                )
            done += count
            data[t] = {
                **binomial(hits, done),
                "seconds": time.monotonic() - start,
                "requested": n,
                "complete": done == n,
                "stream": f"sampling/hand/{t}",
                "probs": q,
                "screen_indices": idx.tolist(),
            }
            if done % 1000000 == 0 or done == n:
                write_json(out / "sampling.json", data)
    return data


def jobs_for(spec, out, phase, cells, indices, design, deadline):
    offset = {"pilot": 10000, "smoke": 20000, "main": 100000}[phase]
    jobs = []
    for t, arm, pop in sorted(cells):
        cap = design[t]["cap"]
        for i in indices:
            seed = MASTER + offset + i
            jobs.append(
                dict(
                    phase=phase,
                    task=t,
                    arm=arm,
                    seed=seed,
                    replicate=i,
                    pop=pop,
                    cap=cap,
                    probs=vectors(spec, t)[arm],
                    deadline=deadline,
                    out=str(out / "runs" / phase / t / arm / f"{pop}-{seed}.json"),
                )
            )
    # Interleave cells so runtime calibration isn't skewed to the first arm.
    return sorted(jobs, key=lambda j: (j["replicate"], j["task"], j["arm"], j["pop"]))


def run_jobs(jobs, workers, out):
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_one, j) for j in jobs]
        for f in as_completed(futures):
            row = f.result()
            rows.append(row)
            with (out / "progress.jsonl").open("a") as log:
                log.write(
                    json.dumps(
                        {
                            k: row[k]
                            for k in (
                                "phase",
                                "task",
                                "arm",
                                "seed",
                                "pop",
                                "cap",
                                "complete",
                                "event",
                                "time",
                                "seconds",
                            )
                        }
                    )
                    + "\n"
                )
            print(
                f"{row['phase']} {row['task']}/{row['arm']} P={row['pop']} seed={row['seed']}: {row['time']}, complete={row['complete']}",
                flush=True,
            )
    return rows


def select_design(pilot, seconds_left, workers, caps=CAPS, sizes=SIZES):
    if any(not r["complete"] for r in pilot):
        return {"feasible": False, "reason": "incomplete pilot"}
    chosen, costs, details = {}, {}, []
    for t in TASKS:
        candidates = []
        for pop in sizes:
            u = [
                r
                for r in pilot
                if r["task"] == t and r["arm"] == "uniform" and r["pop"] == pop
            ]
            h = [
                r
                for r in pilot
                if r["task"] == t and r["arm"] == "hand" and r["pop"] == pop
            ]
            if len(u) != 10 or len(h) != 10:
                return {"feasible": False, "reason": "missing pilot cells"}
            costs[t, pop] = max(r["seconds"] / r["processed_candidates"] for r in u + h)
            for cap in caps:
                passes = sum(r["event"] and r["time"] <= cap for r in u) >= 8
                truncated_h = [
                    {
                        **r,
                        "cap": cap,
                        "event": r["event"] and r["time"] <= cap,
                        "time": min(r["time"], cap),
                    }
                    for r in h
                ]
                m = km_curve(truncated_h)[2]
                details.append(
                    dict(
                        task=t,
                        pop=pop,
                        cap=cap,
                        uniform_solves=sum(r["event"] and r["time"] <= cap for r in u),
                        hand_median=m,
                        passes=passes,
                    )
                )
                if passes:
                    candidates.append((math.inf if m is None else m, -pop, cap, pop))
                    break
        if candidates:
            _, _, cap, pop = max(candidates)
            chosen[t] = dict(pop=pop, cap=cap, pilot_passed=True)
        else:
            # Allocate half available cap-runtime to this family's 200 runs.
            affordable = [
                (p, c)
                for p in sizes
                for c in caps
                if 1.5 * costs[t, p] * c * (200 / workers + 1) <= seconds_left / 2
            ]
            if not affordable:
                return {
                    "feasible": False,
                    "reason": f"no affordable pilot fallback for {t}",
                    "pilot_details": details,
                }
            pop, cap = max(affordable)
            chosen[t] = dict(pop=pop, cap=cap, pilot_passed=False)
    estimates = {t: 1.5 * costs[t, v["pop"]] * v["cap"] for t, v in chosen.items()}

    def budget(n):
        return n * 4 * sum(estimates.values()) / workers + max(estimates.values())

    return dict(
        feasible=budget(50) <= seconds_left,
        tasks=chosen,
        pilot_details=details,
        estimated_cap_seconds=estimates,
        look1_seconds=budget(50),
        two_look_seconds=budget(100),
        seconds_available=seconds_left,
        max_look=2 if budget(100) <= seconds_left else 1,
        large_effect_screen=budget(100) > seconds_left,
        reason=None if budget(50) <= seconds_left else "look 1 exceeds budget",
    )


def summarize_cells(rows, sampling, spec):
    cells = {}
    for t in TASKS:
        for arm in ARMS:
            rr = sorted(
                [r for r in rows if r["task"] == t and r["arm"] == arm],
                key=lambda r: r["seed"],
            )
            if not rr:
                continue
            _, _, median = km_curve(rr)
            family, other = t[:-1], "max" if t.startswith("sum") else "sum"
            source = dict(zip(ARMS, ("uniform", family, other, "hand")))[arm]
            baseline = (
                sampling.get(t)
                if arm == "hand"
                else binomial(
                    spec["sampling"][source]["counts"][t], spec["sampling"][source]["n"]
                )
            )
            p = baseline["p"] if baseline else None
            random_median = math.log(0.5) / math.log1p(-p) if p and p < 1 else None
            cells[f"{t}/{arm}"] = dict(
                n=len(rr),
                complete=sum(r["complete"] for r in rr),
                solves=sum(r["event"] and r["complete"] for r in rr),
                solve_rate=sum(r["event"] for r in rr) / len(rr)
                if all(r["complete"] for r in rr)
                else None,
                cap=rr[0]["cap"],
                pop=rr[0]["pop"],
                km_median=median,
                sampling=baseline,
                random_search_median=random_median,
                evolution_over_random=random_median / median
                if random_median and median
                else None,
                pass_through=None,
                replicate_indices=[r["replicate"] for r in rr],
            )
    for t in TASKS:
        u = cells.get(f"{t}/uniform")
        for arm in ARMS:
            c = cells.get(f"{t}/{arm}")
            if (
                c
                and u
                and c["km_median"]
                and u["km_median"]
                and c["sampling"]
                and u["sampling"]
            ):
                c["pass_through"] = (
                    (u["km_median"] / c["km_median"])
                    / (c["sampling"]["p"] / u["sampling"]["p"])
                    if c["sampling"]["p"]
                    else None
                )
    return cells


def look(rows, comparisons, number, boot):
    # Resolved entries are immutable, even if a shared cell gains observations.
    for ti, t in enumerate(TASKS):
        for pi, (a, b) in enumerate(PAIRS):
            key = f"{t}/{a}/{b}"
            if key in comparisons and comparisons[key]["verdict"] != "U":
                continue
            aa = [r for r in rows if r["task"] == t and r["arm"] == a]
            bb = [r for r in rows if r["task"] == t and r["arm"] == b]
            seed = MASTER + 300000 + ti * 100 + pi * 10 + number
            comparisons[key] = {
                **compare(aa, bb, seed, boot),
                "look": number,
                "numerator": a,
                "denominator": b,
                "task": t,
            }
    return comparisons


def plot_results(out, rows, cells):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    colors = dict(zip(ARMS, ("#555555", "#1f77b4", "#e07b22", "#25974b")))
    for ti, t in enumerate(TASKS):
        ax = axes[ti, 0]
        hist_ax = axes[ti, 1]
        for arm in ARMS:
            rr = [r for r in rows if r["task"] == t and r["arm"] == arm]
            if not rr:
                continue
            x, y, _ = km_curve(rr)
            ax.step(
                x, y, where="post", color=colors[arm], label=f"{arm} KM (n={len(rr)})"
            )
            c = cells[f"{t}/{arm}"]
            if c["sampling"]:
                s = c["sampling"]
                n = np.geomspace(1, c["cap"], 300)
                ax.plot(n, random_cdf(n, s["p"]), "--", color=colors[arm], alpha=0.75)
                ax.fill_between(
                    n,
                    random_cdf(n, s["lower"]),
                    random_cdf(n, s["upper"]),
                    color=colors[arm],
                    alpha=0.1,
                )
            # Histories stop at each event; show individual trajectories,
            # avoiding a survivor-only mean masquerading as a population curve.
            for r in rr:
                h = r["history"]
                hist_ax.plot(
                    [v["evaluations"] for v in h],
                    [v["mean"] for v in h],
                    color=colors[arm],
                    alpha=0.12,
                )
        ax.set(
            xscale="symlog",
            xlim=(0, max(r["cap"] for r in rows if r["task"] == t)),
            ylim=(0, 1),
            xlabel="Candidate evaluations",
            ylabel="P(exact solve)",
            title=f"{t}: KM; dashed = random search, 95% p bands",
        )
        ax.legend(fontsize=8)
        hist_ax.set(
            xscale="log",
            ylim=(0, 1),
            xlabel="Candidate evaluations (batch end)",
            ylabel="Mean training fitness",
            title=f"{t}: per-seed fitness (stops at event)",
        )
    fig.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    for ti, t in enumerate(TASKS):
        for arm in ARMS:
            for r in rows:
                if r["task"] != t or r["arm"] != arm:
                    continue
                h = r["history"]
                x = [v["evaluations"] for v in h]
                axes[ti, 0].plot(
                    x,
                    [v["distinct"] / r["pop"] for v in h],
                    color=colors[arm],
                    alpha=0.15,
                )
                axes[ti, 1].plot(
                    x,
                    [v["run_census"]["runs"] for v in h],
                    color=colors[arm],
                    alpha=0.15,
                )
        axes[ti, 0].set(
            xscale="log",
            title=f"{t}: genotype diversity",
            ylabel="Distinct / population",
            xlabel="Evaluations",
        )
        axes[ti, 1].set(
            xscale="log",
            title=f"{t}: run census",
            ylabel="Mean runs / genome",
            xlabel="Evaluations",
        )
    fig.tight_layout()
    fig.savefig(out / "structure.png", dpi=150)
    plt.close(fig)


def finish(out, result, rows, sampling, spec):
    result["cells"] = summarize_cells(rows, sampling, spec)
    result["outcome"] = overall(
        result["comparisons"],
        result.get("incomplete", False),
        screen=result.get("design", {}).get("large_effect_screen", False),
    )
    write_json(out / "result.json", result)
    if rows:
        plot_results(out, rows, result["cells"])
    else:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.axis("off")
        ax.text(
            0.5,
            0.5,
            f"No confirmatory observations\n{result['stage']} — Unresolved",
            ha="center",
            va="center",
        )
        for name in ("diagnostics.png", "structure.png"):
            fig.savefig(out / name, dpi=150)
        plt.close(fig)
    lines = [
        "# Held-out family bias evolution",
        f"Outcome: **{result['outcome']}**.",
        f"Smoke only: {result['smoke_only']}. Stage: {result['stage']}.",
        f"Design: {json.dumps(result.get('design', {}))}",
        "Median-speed comparisons are frozen at their stopping look; secondary cells may contain more seeds.",
        "B supports only no worthwhile median-speed gain on these two holdouts. Sampling and pass-through are descriptive; no search-mechanism claim.",
    ]
    table = [
        "| comparison | look | n | ratio | CI | verdict |",
        "|---|---|---|---|---|---|",
    ]
    for k, c in result["comparisons"].items():
        table.append(
            f"| {k} | {c['look']} | {c['n']} | {c['ratio']} | {c['lower']}, {c['upper']} | {c['verdict']} |"
        )
    (out / "report.md").write_text(
        "\n\n".join(lines) + "\n\n" + "\n".join(table) + "\n"
    )
    # Distinguish finished infeasibility from an interrupted execution.
    if not result.get("incomplete"):
        (out / "COMPLETE").write_text(result["stage"] + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seconds", type=float, default=27900)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    if args.workers < 1 or args.seconds <= 0:
        ap.error("positive workers and seconds required")
    out = Path(os.environ["RUN_DIR"]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "result.json").exists():
        raise RuntimeError(
            "RUN_DIR already contains result.json; use a fresh directory"
        )
    os.environ["RAYON_NUM_THREADS"] = "1"
    start = time.monotonic()
    deadline = start + args.seconds
    spec = json.loads(SPEC_PATH.read_text())
    validate_spec(spec)
    write_json(out / "vectors.json", spec)
    write_json(out / "sampler_audit.json", sampler_audit())
    result = dict(
        smoke_only=args.smoke,
        master_seed=MASTER,
        stage="initializing",
        comparisons={},
        incomplete=False,
        workers=args.workers,
        internal_seconds=args.seconds,
        spec_sha256=hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest(),
        source=spec["source"],
        source_sha256=spec["source_sha256"],
        statistics=dict(
            family="2026-10-05-1705 held-out median-speed",
            comparisons=6,
            planned_looks=2,
            alpha=ALPHA,
            bootstrap_draws=100000,
            bootstrap_min_finite_fraction=0.99,
            seed_pairing=True,
        ),
        product_model_predictions={
            t: float(
                (
                    lambda q, agg: (
                        q[1] * 22 * q[8] * 22 * np.mean(np.asarray(q)[agg]) * 22
                    )
                )(vectors(spec, t)["hand"], [5, 11] if t == "sum2" else [18])
            )
            for t in TASKS
        },
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        git_dirty=bool(
            subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        ),
    )
    rows, sampling = [], {}
    try:
        if args.smoke:
            result["stage"] = "smoke"
            # One run at every task × arm; several hundred generations to
            # measure sustained reproduction overhead without pilot inference.
            design = {t: dict(pop=64, cap=16384) for t in TASKS}
            jobs = jobs_for(
                spec,
                out,
                "smoke",
                {(t, a, 64) for t in TASKS for a in ARMS},
                range(1),
                design,
                deadline,
            )
            rows = run_jobs(jobs, args.workers, out)
            sampling = sample_hand(spec, out, 10000, deadline)
            result["incomplete"] = any(not r["complete"] for r in rows)
            result["design"] = dict(smoke=True, tasks=design)
        else:
            result["stage"] = "pilot"
            write_json(out / "result.json", result)
            jobs = jobs_for(
                spec,
                out,
                "pilot",
                {(t, a, p) for t in TASKS for a in ("uniform", "hand") for p in SIZES},
                range(10),
                {t: dict(cap=CAPS[-1]) for t in TASKS},
                min(deadline, start + 9000),
            )
            pilot = run_jobs(jobs, args.workers, out)
            write_json(out / "pilot.json", pilot)
            if any(not r["complete"] for r in pilot):
                result.update(stage="pilot_incomplete", incomplete=True)
                finish(out, result, rows, sampling, spec)
                return 1
            result["stage"] = "hand_sampling"
            write_json(out / "result.json", result)
            sampling = sample_hand(spec, out, 125000000, deadline - 900)
            design = select_design(
                pilot, deadline - time.monotonic() - 900, args.workers
            )
            result["design"] = design
            write_json(out / "design.json", design)
            if not design["feasible"]:
                result["stage"] = "runtime_infeasible"
                finish(out, result, rows, sampling, spec)
                return 0
            result["stage"] = "look1"
            write_json(out / "result.json", result)
            tasks = design["tasks"]
            cells = {(t, a, tasks[t]["pop"]) for t in TASKS for a in ARMS}
            jobs = jobs_for(spec, out, "main", cells, range(50), tasks, deadline - 900)
            rows = run_jobs(jobs, args.workers, out)
            if any(not r["complete"] for r in rows):
                result.update(stage="look1_incomplete", incomplete=True)
            else:
                look(rows, result["comparisons"], 1, 100000)
                write_json(out / "look1.json", result["comparisons"])
                pending = next_cells(result["comparisons"])
                if pending and design["max_look"] == 2:
                    result["stage"] = "look2"
                    write_json(out / "result.json", result)
                    jobs = jobs_for(
                        spec,
                        out,
                        "main",
                        {(t, a, tasks[t]["pop"]) for t, a in pending},
                        range(50, 100),
                        tasks,
                        deadline - 900,
                    )
                    rows += run_jobs(jobs, args.workers, out)
                    if any(not r["complete"] for r in rows):
                        result.update(stage="look2_incomplete", incomplete=True)
                    else:
                        look(rows, result["comparisons"], 2, 100000)
                        write_json(out / "look2.json", result["comparisons"])
                if not result["incomplete"]:
                    result["stage"] = "finished"
        finish(out, result, rows, sampling, spec)
        return int(result["incomplete"])
    except Deadline as exc:
        result.update(stage="deadline", incomplete=True, error=str(exc))
        finish(out, result, rows, sampling, spec)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
