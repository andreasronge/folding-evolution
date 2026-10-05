"""Approved constant-threshold sampling experiment, run 2026-10-05-1558.

No evolution. RUN_DIR owns all raw data, stage logs, gate decisions and plots.
Decision bounds are simultaneous across scheduled looks and dependent tasks.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import subprocess
import time
from pathlib import Path

import numpy as np
from scipy.stats import chi2
from _folding_rust import rust_tag_screen

MASTER = 202610051558
TRAINING_SEED = MASTER + 1
BENCHMARK_SEED = MASTER + 2
UNIFORM = np.full(22, 1 / 22)
FLOOR = 0.05 / 22
FITS = {"sum": ["sum1", "sum5"], "max": ["max1", "max5"]}
HOLDOUTS = {"sum": ["sum2"], "max": ["max2"]}
DESCRIPTIVE = ["sum6", "sum7", "max3", "max6"]
CALIBRATION_N = 200_000_000
FIT_ITERATION_N = 10_000_000
VALIDATION_N = 5_000_000
TRANSFER_STEP_N = 125_000_000
DIAGNOSTIC_N = 10_000_000
DECISIVE_RESERVE = 4 * 4 * TRANSFER_STEP_N
DESIGN_RESERVE = (
    CALIBRATION_N + 3 * (18 * FIT_ITERATION_N + 3 * VALIDATION_N) + DECISIVE_RESERVE
)
TASKS = list(
    dict.fromkeys(
        [t for groups in (FITS, HOLDOUTS) for ts in groups.values() for t in ts]
        + DESCRIPTIVE
    )
)
DOMAIN = np.array(list(itertools.product(range(10), repeat=4)), dtype=np.int64)


def labels(task, inputs):
    family = "sum" if task.startswith("sum") else "max"
    threshold = int(task[len(family) :])
    return (getattr(inputs, family)(axis=1) > threshold).astype(np.int64)


def constrained(p):
    """Project to the probability simplex with a strict uniform-relative floor."""
    p = np.asarray(p, dtype=float)
    if not np.isfinite(p).all() or (p < 0).any() or p.sum() <= 0:
        raise ValueError("invalid weights")
    p = p / p.sum()
    # Water filling retains relative mass among weights above the floor.
    fixed = np.zeros(22, dtype=bool)
    while True:
        q = p * ((1 - FLOOR * fixed.sum()) / p[~fixed].sum())
        q[fixed] = FLOOR
        new = (q < FLOOR) & ~fixed
        if not new.any():
            return q
        fixed |= new


def swap(p):
    q = np.array(p, copy=True)
    a, b = q[[5, 11]].sum(), q[18]
    q[[5, 11]] *= b / a
    q[18] = a
    return q  # diagnostic mass exchange, other weights literally unchanged


def executed_counts(g):
    """Distinct cells in runs actually visited from output tag, including SEP.

    Type defaults never skip ops; IF_GT eagerly evaluates operands. Cycles and
    depth limits skip entire run invocations. Counts include visited NOPs.
    """
    ops, tags = g[:64], g[64:]
    starts = np.flatnonzero(ops == 20).tolist()
    runs = [
        (int(tags[i]), i, starts[k + 1] if k + 1 < len(starts) else 64)
        for k, i in enumerate(starts)
    ]
    seen = set()
    memo = set()

    def visit(tag, depth, visiting):
        for k, (t, a, b) in enumerate(runs):
            if t != tag or k in memo or k in visiting or depth > 8:
                continue
            seen.update(range(a, b))
            for i in range(a + 1, b):
                if ops[i] == 21:
                    visit(int(tags[i]), depth + 1, visiting | {k})
            if not visiting:
                memo.add(k)

    visit(0, 0, set())
    return np.bincount(ops[sorted(seen)], minlength=22)


def knockout(g, removed):
    """Delete body cells (not replace with NOP); retain all remaining tags."""
    keep = ~np.isin(g[:64], list(removed))
    ops, tags = g[:64][keep], g[64:][keep]
    n = 64 - len(ops)
    return np.concatenate([np.pad(ops, (0, n)), np.pad(tags, (0, n))]).astype(np.uint8)


def poisson_bounds(k, n, alpha):
    if n <= 0:
        return 0.0, math.inf
    lo = 0.0 if k == 0 else float(chi2.ppf(alpha / 2, 2 * k) / 2 / n)
    hi = float(chi2.ppf(1 - alpha / 2, 2 * (k + 1)) / 2 / n)
    return lo, hi


def ratio_record(a, b, members, alpha):
    rows = {}
    for task in members:
        ka, kb = a["counts"][task], b["counts"][task]
        na, nb = a["n"], b["n"]
        la, ua = poisson_bounds(ka, na, alpha)
        lb, ub = poisson_bounds(kb, nb, alpha)
        point = ka / na / (kb / nb) if na and nb and kb else (math.inf if ka else None)
        rows[task] = {
            "numerator_hits": ka,
            "denominator_hits": kb,
            "ratio": point,
            "lower": la / ub if ub else 0.0,
            "upper": ua / lb if lb else math.inf,
        }
    points = [r["ratio"] for r in rows.values()]
    point = None if any(p is None for p in points) else geometric(points)
    lo = geometric([r["lower"] for r in rows.values()])
    hi = geometric([r["upper"] for r in rows.values()])
    kind = (
        "G" if point is not None and point >= 3 and lo > 1 else "N" if hi < 3 else "U"
    )
    return {
        "ratio": point,
        "lower": lo,
        "upper": hi,
        "class": kind,
        "members": rows,
        "one_holdout": len(members) == 1,
        "member_reversal": any(
            r["ratio"] is not None and r["ratio"] < 1 for r in rows.values()
        ),
        "interval_method": "geometric mean of simultaneous exact Poisson rate bounds",
        "marginal_alpha": alpha,
    }


def geometric(values):
    if any(v == 0 for v in values):
        return 0.0
    return math.exp(sum(math.log(v) for v in values) / len(values))


def verdict(comparisons, validated=True):
    if not validated:
        return "inconclusive"
    s = [comparisons[f]["specificity"]["class"] for f in FITS]
    g = [comparisons[f]["gain"]["class"] for f in FITS]
    if "U" in s + g:
        return "inconclusive"
    useful = [s[i] == g[i] == "G" for i in range(2)]
    if all(useful):
        return "A"
    if any(useful):
        return "partial A"
    if s == ["N", "N"] and "G" in g:
        return "C"
    if g == ["N", "N"]:
        return "D"
    return "mixed/unresolved"


def mean_log_rate(p, tasks):
    if any(p["counts"][t] == 0 for t in tasks):
        return -math.inf
    return float(np.mean([math.log(p["counts"][t] / p["n"]) for t in tasks]))


def clean_json(value):
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [clean_json(v) for v in value]
    if isinstance(value, (float, np.floating)):
        return (
            float(value)
            if math.isfinite(value)
            else ("Infinity" if value > 0 else "-Infinity")
        )
    if isinstance(value, np.integer):
        return int(value)
    return value


class Deadline(Exception):
    pass


class Experiment:
    def __init__(self, out, smoke=False, seconds=10500, seed=MASTER):
        self.out = Path(out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.seed, self.smoke = seed, smoke
        self.end = time.monotonic() + seconds
        self.stage = "setup"
        self.batch = 2000 if smoke else 50000
        self.worst_rate = math.inf
        self.results = {
            "seed": seed,
            "smoke_only": smoke,
            "tasks": TASKS,
            "parameters": {
                "internal_deadline_seconds": seconds,
                "L": 64,
                "n_ops": 22,
                "tags": 64,
                "threshold": 0,
                "slots": "NOP",
                "alpha_smoothing": 0.5,
                "floor": FLOOR,
                "starts": 3,
                "iterations": 6,
                "elites_min": 10,
                "fit_initialization": "start 0 iteration 0 uses retained-task uniform calibration elites when supported",
                "training_seed": TRAINING_SEED,
                "benchmark_seed": BENCHMARK_SEED,
                "fitting_tasks": FITS,
                "holdouts": HOLDOUTS,
                "descriptive_tasks": DESCRIPTIVE,
                "calibration_n": CALIBRATION_N,
                "fit_iteration_cap": FIT_ITERATION_N,
                "validation_per_start_cap": VALIDATION_N,
                "transfer_per_arm_cap": 4 * TRANSFER_STEP_N,
                "diagnostic_pool_cap": DIAGNOSTIC_N,
            },
            "streams": [],
            "pools": {},
            "gates": [],
        }
        self.domain = DOMAIN.tolist()
        self.full_y = [labels(t, DOMAIN).tolist() for t in TASKS]
        rng = np.random.default_rng(TRAINING_SEED)
        idx = set()
        self.training = {}
        for t in TASKS:
            y = labels(t, DOMAIN)
            # Low max thresholds have fewer than 32 distinct negatives. Sampling
            # with replacement still supplies 32 of each label, as specified.
            chosen = np.concatenate(
                [rng.choice(np.flatnonzero(y == v), 32, replace=True) for v in (0, 1)]
            )
            self.training[t] = chosen.tolist()
            idx.update(chosen.tolist())
        screen_idx = np.array(sorted(idx))
        rng.shuffle(screen_idx)
        self.screen = DOMAIN[screen_idx].tolist()
        self.screen_y = [labels(t, DOMAIN[screen_idx]).tolist() for t in TASKS]
        self.results["training_indices"] = self.training
        self.results["screen_indices"] = screen_idx.tolist()
        try:
            self.results["commit"] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip()
        except subprocess.CalledProcessError:
            self.results["commit"] = None
        self.results["git_dirty"] = bool(
            subprocess.check_output(["git", "status", "--porcelain"], text=True)
        )
        self.save()

    def save(self):
        tmp = self.out / "result.json.tmp"
        tmp.write_text(json.dumps(clean_json(self.results), indent=2) + "\n")
        tmp.replace(self.out / "result.json")

    def log(self, event, **kw):
        row = {"stage": self.stage, "event": event, **kw}
        with (self.out / "progress.jsonl").open("a") as f:
            f.write(json.dumps(clean_json(row)) + "\n")
        print(json.dumps(clean_json(row)), flush=True)

    def gate(self, name, **kw):
        row = {"name": name, **kw}
        self.results["gates"].append(row)
        self.save()
        self.log("gate", **row)

    def rng(self, stream):
        # Stable across Python hash randomization; unique named streams.
        digest = hashlib.sha256(stream.encode()).digest()
        base_seed = BENCHMARK_SEED if stream.startswith("benchmark/") else self.seed
        entropy = [base_seed, *np.frombuffer(digest[:16], dtype="<u4").tolist()]
        self.results["streams"].append({"name": stream, "entropy": entropy})
        return np.random.default_rng(np.random.SeedSequence(entropy))

    def draw(self, rng, n, weights):
        ops = rng.choice(22, size=(n, 64), p=weights).astype(np.uint8)
        tags = rng.integers(0, 64, size=(n, 64), dtype=np.uint8)
        return np.concatenate([ops, tags], axis=1)

    def evaluate(self, tapes):
        t0 = time.monotonic()
        candidates = rust_tag_screen(tapes.tobytes(), 64, self.screen, self.screen_y)
        screen_seconds = time.monotonic() - t0
        t1 = time.monotonic()
        exact = []
        if candidates:
            indices = [i for i, _ in candidates]
            survivors = rust_tag_screen(
                tapes[indices].tobytes(), 64, self.domain, self.full_y
            )
            exact = [(indices[i], mask) for i, mask in survivors]
        return exact, {
            "screen_seconds": screen_seconds,
            "exact_seconds": time.monotonic() - t1,
            "candidates": len(candidates),
        }

    def pool(self, name, n, weights, collect=False, previous=None):
        rng = self.rng(name)
        stream_record = self.results["streams"][-1]
        stream_record.update(requested=n, completed=0, weights=weights.tolist())
        p = (
            {**previous, "counts": dict(previous["counts"])}
            if previous is not None
            else {
                "n": 0,
                "counts": dict.fromkeys(TASKS, 0),
                "seconds": 0.0,
                "screen_seconds": 0.0,
                "exact_seconds": 0.0,
                "candidates": 0,
            }
        )
        elites = {t: [] for t in TASKS}
        self.results["pools"][name] = p
        self.log("pool_start", name=name, target=n, weights=weights.tolist())
        done = 0
        while done < n:
            if time.monotonic() > self.end - 60:
                p["budget_truncated"] = True
                self.save()
                raise Deadline(name)
            count = min(self.batch, n - done)
            t0 = time.monotonic()
            tapes = self.draw(rng, count, weights)
            exact, costs = self.evaluate(tapes)
            for i, mask in exact:
                for j, t in enumerate(TASKS):
                    if mask & (1 << j):
                        p["counts"][t] += 1
                        if collect:
                            elites[t].append(tapes[i].copy())
            p["n"] += count
            done += count
            stream_record["completed"] = done
            p["seconds"] += time.monotonic() - t0
            for k, v in costs.items():
                p[k] += v
            if done % (10 * self.batch) == 0:
                self.save()
        if p["seconds"] > 0:
            self.worst_rate = min(self.worst_rate, p["n"] / p["seconds"])
        self.save()
        self.log("pool_end", name=name, **p)
        return p, elites

    def exact_task(self, tapes, task):
        if not len(tapes):
            return set()
        if time.monotonic() > self.end - 60:
            raise Deadline("knockout")
        y = [self.full_y[TASKS.index(task)]]
        return {
            i
            for i, _ in rust_tag_screen(np.asarray(tapes).tobytes(), 64, self.domain, y)
        }

    def benchmark(self, vectors):
        self.stage = "benchmark"
        for name, w in vectors.items():
            n = 2000 if self.smoke else 100000
            p, _ = self.pool("benchmark/" + name, n, w)
            # Effective throughput includes actual enriched exhaustive candidates.
            # Planted solvers additionally time successful full-domain checks.
            planted = []
            for task in ("sum5", "max5"):
                ops = [20, 1, 5 if task.startswith("sum") else 18, 16, 8]
                planted.append(
                    np.array(ops + [0] * (64 - len(ops)) + [0] * 64, dtype=np.uint8)
                )
            start = time.monotonic()
            self.exact_task([planted[0]] * 20, "sum5")
            self.exact_task([planted[1]] * 20, "max5")
            exact_cost = (time.monotonic() - start) / 40
            self.results.setdefault("benchmarks", {})[name] = {
                "effective_tapes_per_second": p["n"] / p["seconds"],
                "exhaustive_seconds_per_planted_check": exact_cost,
                "exhaustive_candidate_seconds": p["exact_seconds"],
                "screen_candidates": p["candidates"],
            }
        self.save()

    def calibrate(self, scale):
        self.stage = "calibration"
        target = 20000 if self.smoke else CALIBRATION_N
        self.gate(
            "calibration_budget", initial=target, cap=target, looks=1, scaled=False
        )
        cal, elites = self.pool("calibration/initial", target, UNIFORM, True)
        self.results["calibration"] = cal
        for t in TASKS:
            data = np.asarray(elites[t], dtype=np.uint8).reshape(-1, 128)
            np.save(self.out / ("calibration_" + t + ".npy"), data)
        eligible = {
            t: cal["counts"][t] >= 10 and cal["counts"][t] / cal["n"] <= 1e-3
            for t in sum(FITS.values(), []) + sum(HOLDOUTS.values(), [])
        }
        fits = {f: list(ts) for f, ts in FITS.items()}
        hold = {f: list(ts) for f, ts in HOLDOUTS.items()}
        self.results["frozen_tasks"] = {
            "fits": fits,
            "holdouts": hold,
            "eligible": eligible,
            "substitutions": [],
            "descriptive": DESCRIPTIVE,
        }
        valid = all(eligible.values())
        self.gate("task_eligibility", passed=valid, **self.results["frozen_tasks"])
        return valid, cal, elites, fits, hold

    def prune(self, elites, fits):
        self.stage = "pruning"
        tasks = sum(fits.values(), [])
        report = {
            t: {
                "solvers": len(elites[t]),
                "present": [0] * 22,
                "executed": [0] * 22,
                "broken": [0] * 22,
            }
            for t in tasks
        }
        for t in tasks:
            data = np.asarray(elites[t], dtype=np.uint8)
            ec = np.array([executed_counts(g) for g in data])
            report[t]["present"] = [
                int(np.any(data[:, :64] == o, axis=1).sum()) for o in range(22)
            ]
            report[t]["executed"] = (ec > 0).sum(axis=0).astype(int).tolist()
            for o in range(20):
                ko = np.array([knockout(g, {o}) for g in data])
                report[t]["broken"][o] = len(data) - len(self.exact_task(ko, t))
        support = np.sum([r["executed"] for r in report.values()], axis=0)
        candidates = {
            o
            for o in range(20)
            if support[o] >= 5 and all(r["broken"][o] == 0 for r in report.values())
        }
        original = sorted(candidates)
        removed = []
        while candidates:
            broken = {
                t: len(elites[t])
                - len(self.exact_task([knockout(g, candidates) for g in elites[t]], t))
                for t in tasks
            }
            self.log("joint_knockout", candidates=sorted(candidates), broken=broken)
            if not any(broken.values()):
                break
            o = min(candidates, key=lambda o: (support[o], o))
            candidates.remove(o)
            removed.append(o)
        # Relative raw weights: exactly .05 vs 1 before normalization.
        weights = np.ones(22)
        weights[list(candidates)] = 0.05
        weights /= weights.sum()
        self.results["pruning"] = {
            "per_task": report,
            "candidates": original,
            "joint_removed": removed,
            "floored": sorted(candidates),
            "low_support_kept": [o for o in range(20) if support[o] < 5],
            "under_supported": any(len(elites[t]) < 20 for t in tasks),
            "weights": weights.tolist(),
            "raw_weight_floor": 0.05,
            "normalized_floored_probability": float(
                0.05 / (22 - 0.95 * len(candidates))
            ),
            "executed_definition": "distinct visited cells including SEP and NOP",
        }
        self.gate("pruning_frozen", **self.results["pruning"])
        return weights

    def fit(self, name, tasks, scale, remaining_fits=1, calibration_elites=None):
        self.stage = "fitting/" + name
        iterations = []
        starts = []
        unit = 2000 if self.smoke else FIT_ITERATION_N
        if not self.smoke:
            # Leave independent validation and decisive transfer ahead of diagnostics.
            reserve = (
                remaining_fits * (18 * FIT_ITERATION_N + 3 * VALIDATION_N)
                + DECISIVE_RESERVE
            )
            scale = min(
                scale,
                max(
                    0.0,
                    (self.end - time.monotonic() - 120)
                    * self.worst_rate
                    * 0.8
                    / reserve,
                ),
            )
        n = max(1, int(unit * scale))
        cal = self.results.get("calibration")
        if calibration_elites is not None and cal is None:
            raise ValueError("bootstrap elites require their uniform calibration pool")
        self.gate(
            "fit_budget",
            fit=name,
            per_iteration=n,
            total_cap=18 * n,
            expected_elites_from_uniform={
                t: n * cal["counts"][t] / cal["n"] for t in tasks
            }
            if cal
            else None,
        )
        bootstrap = {
            "start": 0,
            "iteration": 0,
            "source": "uniform calibration",
            "updated_tasks": [],
            "counts": {t: len((calibration_elites or {}).get(t, [])) for t in tasks},
        }
        start_updates = []
        for start in range(3):
            weights = (
                UNIFORM.copy()
                if start == 0
                else constrained(
                    self.rng(f"fit/{name}/{start}/initial").dirichlet(np.ones(22) * 10)
                )
            )
            contributions = {t: weights.copy() for t in tasks}
            updated_tasks = set()
            fresh_updated_tasks = set()
            # A uniform pool legitimately seeds the uniform start. Never use
            # its elites as observations from either Dirichlet distribution,
            # and never allow held-out tasks into this update.
            if start == 0:
                bootstrap["updated_tasks"] = sorted(
                    t for t in tasks if bootstrap["counts"][t] >= 10
                )
            for iteration in range(6):
                use_calibration = start == iteration == 0 and bool(
                    bootstrap["updated_tasks"]
                )
                if use_calibration:
                    p, elites = cal, calibration_elites
                else:
                    p, elites = self.pool(
                        f"fit/{name}/{start}/{iteration}", n, weights, True
                    )
                objective = mean_log_rate(p, tasks)
                for t in tasks:
                    if len(elites[t]) >= 10:
                        freq = np.sum([executed_counts(g) for g in elites[t]], axis=0)
                        contributions[t] = freq / freq.sum()
                        updated_tasks.add(t)
                        if not use_calibration:
                            fresh_updated_tasks.add(t)
                update = np.mean(list(contributions.values()), axis=0)
                weights = constrained(0.5 * weights + 0.5 * update)
                if start == iteration == 0:
                    bootstrap["used"] = use_calibration
                    bootstrap["next_weights"] = weights.tolist()
                    self.gate("fit_bootstrap", fit=name, **bootstrap)
                iterations.append(
                    {
                        "start": start,
                        "iteration": iteration,
                        "source": "uniform calibration"
                        if use_calibration
                        else "fresh fitting pool",
                        "objective": objective,
                        "counts": {t: p["counts"][t] for t in tasks},
                        "updated_tasks": [t for t in tasks if len(elites[t]) >= 10],
                        "next_weights": weights.tolist(),
                    }
                )
            # Final update is itself a candidate; use it as the fitted vector.
            starts.append(weights)
            start_updates.append(
                {
                    "start": start,
                    "updated_tasks": sorted(updated_tasks),
                    "fresh_updated_tasks": sorted(fresh_updated_tasks),
                    "status": "updated" if updated_tasks else "no task updated",
                }
            )
        self.results.setdefault("fitting", {})[name] = {
            "iterations": iterations,
            "starts": [w.tolist() for w in starts],
            "objective": "mean log P(exact)",
            "bootstrap": bootstrap,
            "start_updates": start_updates,
            "status": "updated"
            if any(r["updated_tasks"] for r in start_updates)
            else "no task updated",
        }
        self.gate(
            "fit_updates",
            fit=name,
            passed=self.results["fitting"][name]["status"] == "updated",
            starts=start_updates,
        )
        return starts

    def validate(self, name, tasks, starts, cal, scale, remaining_fits=1):
        self.stage = "validation/" + name
        if not self.smoke:
            reserve = (
                remaining_fits * 3 * VALIDATION_N
                + (remaining_fits - 1) * 18 * FIT_ITERATION_N
                + DECISIVE_RESERVE
            )
            scale = min(
                scale,
                max(
                    0.0,
                    (self.end - time.monotonic() - 120)
                    * self.worst_rate
                    * 0.8
                    / reserve,
                ),
            )
        n = max(1, int((3000 if self.smoke else VALIDATION_N) * scale))
        self.gate("validation_budget", fit=name, per_start=n)
        rows, validated = [], []
        for i, w in enumerate(starts):
            p, _ = self.pool(f"validation/{name}/{i}", n, w)
            ratios = {t: ratio_record(p, cal, [t], 0.05 / 4) for t in tasks}
            passed = all(
                r["ratio"] is not None and r["ratio"] >= 3 and r["lower"] > 1
                for r in ratios.values()
            )
            objective = mean_log_rate(p, tasks) - mean_log_rate(cal, tasks)
            rows.append(
                {
                    "start": i,
                    "ratios": ratios,
                    "passed": passed,
                    "objective": objective,
                    "weights": w.tolist(),
                    "fold_change": (w / UNIFORM).tolist(),
                }
            )
            if passed:
                validated.append((objective, i))
        selected = max(validated)[1] if validated else None
        self.results.setdefault("validation", {})[name] = {
            "starts": rows,
            "selected": selected,
            "objective_spread": [r["objective"] for r in rows],
            "selected_start_status": (
                self.results["fitting"][name]["start_updates"][selected]["status"]
                if selected is not None
                else None
            ),
        }
        self.gate(
            "fit_validation", fit=name, passed=selected is not None, selected=selected
        )
        return starts[selected] if selected is not None else None

    def comparisons(self, pools, hold):
        result = {}
        # 4 looks * 4 decisive comparisons * 2 members * 2 rate bounds.
        # Union bound handles dependence and optional stopping without normal
        # approximations, including zero-count cells.
        decisive_alpha = 0.05 / (4 * 4 * 2 * 2)
        side_alpha = 0.05 / (4 * 2 * 2 * 2)
        for f, other in (("sum", "max"), ("max", "sum")):
            result[f] = {}
            for axis, reference in (
                ("specificity", other),
                ("gain", "uniform"),
                ("beyond_pruning", "prune"),
            ):
                alpha = side_alpha if axis == "beyond_pruning" else decisive_alpha
                result[f][axis] = ratio_record(
                    pools[f], pools[reference], hold[f], alpha
                )
                if axis != "beyond_pruning" and self.results.get(
                    "transfer_budget_cut", False
                ):
                    result[f][axis]["statistical_class"] = result[f][axis]["class"]
                    result[f][axis]["class"] = "U"
                    result[f][axis]["runtime_cut"] = True
                result[f][axis]["descriptive_fixed_95"] = ratio_record(
                    pools[f], pools[reference], hold[f], 0.05 / 4
                )
                result[f][axis]["descriptive_fixed_95"]["interval_method"] = (
                    "conservative fixed-look 95% simultaneous Poisson bounds over "
                    "at most two members and two rates; not a stopping gate"
                )
        return result

    def transfer(self, vectors, hold, scale):
        self.stage = "transfer"
        self.benchmark({k: v for k, v in vectors.items() if k in ("sum", "max")})
        self.stage = "transfer"
        measured = min(
            v["effective_tapes_per_second"] for v in self.results["benchmarks"].values()
        )
        remaining = self.end - time.monotonic() - 120
        unit = 4000 if self.smoke else TRANSFER_STEP_N
        # Preserve decisive pools before allocating descriptive ones. Scale is
        # frozen before first transfer sample, and limited to the proposal cap.
        transfer_scale = min(scale, max(0.0, remaining * measured / (16 * unit) * 0.8))
        step = max(1, int(unit * transfer_scale))
        self.results["transfer_budget_cut"] = not self.smoke and step < TRANSFER_STEP_N
        self.gate(
            "transfer_budget_frozen",
            step=step,
            looks=4,
            cap_per_decision_pool=4 * step,
            remaining_seconds=remaining,
            scale=transfer_scale,
            descriptive_priority="both/swaps then prune extension cut first",
        )
        pools = {}
        for k in ("uniform", "sum", "max", "prune"):
            pools[k], _ = self.pool(f"transfer/{k}/look1", step, vectors[k])
        looks = []
        for look in range(1, 5):
            c = self.comparisons(pools, hold)
            looks.append(
                {
                    "look": look,
                    "comparisons": c,
                    "samples": {k: p["n"] for k, p in pools.items()},
                }
            )
            self.results["transfer"] = {
                "pools": pools,
                "looks": looks,
                "comparisons": c,
                "outcome": verdict(c),
                "holdouts": hold,
            }
            self.gate("transfer_look", look=look, outcome=verdict(c), comparisons=c)
            active = set()
            for f, other in (("sum", "max"), ("max", "sum")):
                if c[f]["specificity"]["class"] == "U":
                    active.update((f, other))
                if c[f]["gain"]["class"] == "U":
                    active.update((f, "uniform"))
            if not active or look == 4:
                break
            # An arm that sat out earlier looks never exceeds its frozen cap.
            for k in sorted(active):
                pools[k], _ = self.pool(
                    f"transfer/{k}/look{look + 1}", step, vectors[k], previous=pools[k]
                )
        # The primary result is fixed before optional diagnostics start. A
        # diagnostic timeout cannot erase a completed decisive comparison.
        self.results["transfer"]["decisive_complete"] = True
        self.results["outcome"] = self.results["transfer"]["outcome"]
        self.results["fitting_recheck"] = {
            f: {
                t: ratio_record(pools[f], pools["uniform"], [t], 0.05 / 2)
                for t in self.results["frozen_tasks"]["fits"][f]
            }
            for f in FITS
        }
        self.save()
        # Beyond-pruning unresolved does not block the primary verdict. Extend
        # prune only after decisive comparisons have reached their final look.
        for look in range(2, 5):
            c = self.comparisons(pools, hold)
            if all(c[f]["beyond_pruning"]["class"] != "U" for f in FITS):
                break
            rate = self.results["benchmarks"]["enriched"]["effective_tapes_per_second"]
            if (self.end - time.monotonic() - 120) * rate < step * 1.5:
                self.log("descriptive_cut", vector="prune", reason="runtime reserve")
                break
            pools["prune"], _ = self.pool(
                f"transfer/prune/side{look}",
                step,
                vectors["prune"],
                previous=pools["prune"],
            )
        self.results["transfer"]["comparisons"] = self.comparisons(pools, hold)
        self.results["transfer"]["outcome"] = verdict(
            self.results["transfer"]["comparisons"]
        )
        for k in ("both", "sum_swap", "max_swap"):
            if k not in vectors:
                self.log("descriptive_cut", vector=k, reason="no validated both-fit")
                continue
            rate = min(
                v["effective_tapes_per_second"]
                for v in self.results["benchmarks"].values()
            )
            diagnostic_n = 4000 if self.smoke else DIAGNOSTIC_N
            if (self.end - time.monotonic() - 120) * rate < diagnostic_n * 1.5:
                self.log("descriptive_cut", vector=k, reason="runtime reserve")
                continue
            pools[k], _ = self.pool(
                f"transfer/{k}/descriptive", diagnostic_n, vectors[k]
            )
        self.results["transfer"]["pools"] = pools
        self.results["outcome"] = self.results["transfer"]["outcome"]
        self.results["descriptive_comparisons"] = {
            k: {f: ratio_record(p, pools["uniform"], hold[f], 0.05 / 4) for f in FITS}
            for k, p in pools.items()
        }
        self.save()

    def run(self):
        enriched = np.ones(22)
        enriched[[1, 5, 11, 18, 2, 3, 15, 16, 19, 8, 20]] *= 3
        enriched /= enriched.sum()
        self.benchmark({"uniform": UNIFORM, "enriched": enriched})
        rate = min(
            v["effective_tapes_per_second"] for v in self.results["benchmarks"].values()
        )
        remaining = self.end - time.monotonic() - 120
        # Reserve calibration, three fits/validations and all four transfer arms,
        # 20% margin for knockouts and richer fit costs; remeasure before transfer.
        scale = 1.0 if self.smoke else min(1.0, remaining * rate * 0.8 / DESIGN_RESERVE)
        self.results["runtime_scale"] = scale
        self.gate("runtime_budget", scale=scale, rate=rate, remaining_seconds=remaining)
        valid, cal, elites, fits, hold = self.calibrate(scale)
        if not valid:
            self.results["outcome"] = "infeasible task set"
            self.results["diagnostics_status"] = (
                "prune/both/swaps not estimated: calibration gate failed"
            )
            return
        prune = self.prune(elites, fits)
        selected = {}
        for index, (f, ts) in enumerate(
            [*fits.items(), ("both", sum(fits.values(), []))]
        ):
            starts = self.fit(
                f, ts, scale, remaining_fits=3 - index, calibration_elites=elites
            )
            selected[f] = self.validate(
                f, ts, starts, cal, scale, remaining_fits=3 - index
            )
        if selected["sum"] is None or selected["max"] is None:
            self.results["outcome"] = "inconclusive"
            no_updates = [
                f
                for f in FITS
                if self.results["fitting"][f]["status"] == "no task updated"
            ]
            self.results["reason"] = (
                "no fitting task updated in "
                + ", ".join(no_updates)
                + "; no validated family fit; transfer not run"
                if no_updates
                else "adapted family fit not validated; transfer not run"
            )
            self.results["diagnostics_status"] = (
                "transfer/prune-vs-uniform/swaps not estimated: validation gate failed"
            )
            return
        vectors = {
            "uniform": UNIFORM,
            "prune": prune,
            "sum": selected["sum"],
            "max": selected["max"],
            "sum_swap": swap(selected["sum"]),
            "max_swap": swap(selected["max"]),
        }
        if selected["both"] is not None:
            vectors["both"] = selected["both"]
        self.results["vectors"] = {k: v.tolist() for k, v in vectors.items()}
        self.results["swap_diagnostics"] = {
            k: {
                "below_fit_floor_ops": np.flatnonzero(v < FLOOR).tolist(),
                "mass_exchange": "SUM+REDUCE_ADD exchanged with REDUCE_MAX; other ops unchanged",
            }
            for k, v in vectors.items()
            if k.endswith("_swap")
        }
        self.transfer(vectors, hold, scale)

    def handle_deadline(self, error):
        transfer = self.results.get("transfer", {})
        decisive_complete = transfer.get("decisive_complete", False)
        self.results["outcome"] = (
            transfer["outcome"] if decisive_complete else "inconclusive"
        )
        reason = "internal deadline at " + str(error)
        if decisive_complete:
            # Only completed side pools enter comparisons. Partial counts in
            # results["pools"] remain available as interrupted raw diagnostics.
            transfer["comparisons"] = self.comparisons(
                transfer["pools"], transfer["holdouts"]
            )
            self.results["diagnostics_status"] = (
                reason + "; remaining diagnostics incomplete"
            )
        else:
            self.results["reason"] = reason
        self.gate(
            "deadline",
            passed=False,
            interrupted_stage=self.stage,
            decisive_complete=decisive_complete,
        )

    def finish(self):
        self.save()
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 4))
        pools = self.results.get("transfer", {}).get(
            "pools",
            {"calibration": self.results["calibration"]}
            if "calibration" in self.results
            else self.results["pools"],
        )
        for name, p in pools.items():
            if p.get("n"):
                ax.plot(
                    TASKS, [p["counts"][t] / p["n"] for t in TASKS], "o-", label=name
                )
        ax.set_yscale("symlog", linthresh=1e-8)
        max_rate = max(
            (
                p["counts"][t] / p["n"]
                for p in pools.values()
                if p.get("n")
                for t in TASKS
            ),
            default=0.0,
        )
        ax.set_ylim(0, min(1.0, max(1e-7, max_rate * 1.2)))
        ax.set_ylabel("P(exact) on all 10,000 inputs")
        ax.tick_params(axis="x", rotation=45)
        ax.set_title(("SMOKE — " if self.smoke else "") + self.results["outcome"])
        if ax.lines:
            ax.legend()
        fig.tight_layout()
        fig.savefig(self.out / "diagnostics.png")
        plt.close(fig)
        lines = [
            "# Sum/max frequency fitting",
            "",
            f"Outcome: {self.results['outcome']}",
            f"Smoke only: {self.smoke}",
            "",
            "Decision bounds are adjusted across four scheduled looks and decisive comparisons.",
            "Family estimates describe the retained thresholds; evolution remains untested.",
            "See result.json for frozen tasks, all rates/intervals, seed streams, weights and gate decisions.",
        ]
        if "reason" in self.results:
            lines.extend(["", "Reason: " + self.results["reason"]])
        if "diagnostics_status" in self.results:
            lines.extend(["", self.results["diagnostics_status"]])
        frozen = self.results.get("frozen_tasks", {})
        if frozen:
            lines.extend(
                [
                    "",
                    "Retained fitting tasks: " + str(frozen["fits"]),
                    "Retained holdouts: " + str(frozen["holdouts"]),
                    "",
                    "| Task | Calibration exact hits | P(exact) | Eligible |",
                    "|---|---:|---:|---|",
                ]
            )
            cal = self.results["calibration"]
            for t in TASKS:
                lines.append(
                    f"| {t} | {cal['counts'][t]} | {cal['counts'][t] / cal['n']:.4g} | {frozen['eligible'].get(t, 'descriptive only')} |"
                )
        if "pruning" in self.results:
            lines.extend(
                [
                    "",
                    "Pruning under-supported: "
                    + str(self.results["pruning"]["under_supported"]),
                ]
            )
        for name, fit in self.results.get("fitting", {}).items():
            lines.extend(
                [
                    "",
                    f"{name} fitting status: {fit['status']}",
                    "Calibration bootstrap tasks: "
                    + str(fit["bootstrap"]["updated_tasks"]),
                    "Start update support: " + str(fit["start_updates"]),
                ]
            )
        comparisons = self.results.get("transfer", {}).get("comparisons", {})
        if comparisons:
            member_notes = []
            lines.extend(
                [
                    "",
                    "| Family | Axis | Ratio | Adjusted lower | Adjusted upper | Class |",
                    "|---|---|---:|---:|---:|---|",
                ]
            )
            for f, axes in comparisons.items():
                for axis, r in axes.items():
                    point = "unknown" if r["ratio"] is None else f"{r['ratio']:.4g}"
                    lines.append(
                        f"| {f} | {axis} | {point} | {r['lower']:.4g} | {r['upper']:.4g} | {r['class']} |"
                    )
                    if r["one_holdout"] or r["member_reversal"]:
                        member_notes.append(
                            f"\n{f}/{axis}: one_holdout={r['one_holdout']}, member_reversal={r['member_reversal']}; inspect member intervals in result.json.\n"
                        )
            lines.extend(member_notes)
        lines.extend(
            [
                "",
                "Each family has one held-out member: sum>2 or max>2.",
                "C excludes worthwhile (3×) specificity on this split, not all family information.",
                "D can reflect CONST_2 suppression; this is a possible explanation, not an identified cause.",
                "Neither verdict establishes that frequency adaptation generally fails or that decoder changes are necessary.",
                "",
                "| Fit | Selected start | CONST_2 probability | Fold vs uniform |",
                "|---|---:|---:|---:|",
            ]
        )
        for name, validation in self.results.get("validation", {}).items():
            selected = validation["selected"]
            if selected is None:
                lines.append(f"| {name} | none | unavailable | unavailable |")
            else:
                p2 = validation["starts"][selected]["weights"][15]
                lines.append(
                    f"| {name} | {selected} | {p2:.6g} | {p2 / UNIFORM[15]:.4g} |"
                )
        lines.extend(
            [
                "",
                "Recorded cumulative pool counts (sum6/sum7/max3/max6 are descriptive only):",
                "",
                "| Pool | Task | N tapes | Exact hits | P(exact) | Status |",
                "|---|---|---:|---:|---:|---|",
            ]
        )
        for name, p in self.results["pools"].items():
            if p["n"]:
                for task in TASKS:
                    lines.append(
                        f"| {name} | {task} | {p['n']} | {p['counts'][task]} | {p['counts'][task] / p['n']:.6g} | {'interrupted' if p.get('budget_truncated') else 'complete'} |"
                    )
        lines.extend(
            [
                "",
                "Aggregator swaps (descriptive only; other op weights unchanged):",
                "",
                "| Vector | Holdout | Ratio vs uniform | Lower | Upper |",
                "|---|---|---:|---:|---:|",
            ]
        )
        diagnostics = self.results.get("descriptive_comparisons", {})
        transfer = self.results.get("transfer", {})
        for name in ("sum_swap", "max_swap"):
            if name not in diagnostics and name in transfer.get("pools", {}):
                diagnostics[name] = {
                    f: ratio_record(
                        transfer["pools"][name],
                        transfer["pools"]["uniform"],
                        HOLDOUTS[f],
                        0.05 / 4,
                    )
                    for f in FITS
                }
            if name not in diagnostics:
                lines.append(
                    f"| {name} | unavailable | unavailable | unavailable | unavailable |"
                )
                continue
            for family, r in diagnostics[name].items():
                point = "unknown" if r["ratio"] is None else f"{r['ratio']:.4g}"
                lines.append(
                    f"| {name} | {HOLDOUTS[family][0]} | {point} | {r['lower']:.4g} | {r['upper']:.4g} |"
                )
        (self.out / "report.md").write_text("\n".join(lines) + "\n")
        (self.out / "COMPLETE").write_text("ok\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.environ.get("RUN_DIR"))
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument(
        "--probe",
        action="store_true",
        help="5M uniform reconnaissance only; excluded from experiment pools",
    )
    ap.add_argument("--seconds", type=float, default=10500)
    ap.add_argument("--seed", type=int, default=MASTER)
    args = ap.parse_args()
    if not args.out:
        ap.error("set RUN_DIR or --out")
    if args.probe and args.smoke:
        ap.error("--probe and --smoke are separate modes")
    experiment = Experiment(args.out, args.smoke, args.seconds, args.seed)
    try:
        if args.probe:
            experiment.stage = "reconnaissance"
            p, _ = experiment.pool("reconnaissance/uniform", 5_000_000, UNIFORM)
            experiment.results["reconnaissance"] = p
            experiment.results["outcome"] = (
                "reconnaissance only; no eligibility or inference"
            )
        else:
            experiment.run()
    except Deadline as e:
        experiment.handle_deadline(e)
    experiment.finish()


if __name__ == "__main__":
    main()
