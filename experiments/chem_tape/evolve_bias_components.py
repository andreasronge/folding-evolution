"""Frozen 2x2 component-sufficiency study, one look (2026-10-05-1814)."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time

import numpy as np
from _folding_rust import rust_tag_screen

from experiments.chem_tape import evolve_bias as eb
from folding_evolution.chem_tape import tagged

MASTER = 202610051814
TASKS = eb.TASKS
ARMS = ("U", "IG", "R", "X")
PAIRS = (("U", "X"), ("U", "IG"), ("U", "R"), ("IG", "X"), ("R", "X"))
ALPHA = 0.05 / 10
POP, CAP, BOOT = 1024, 262144, 100000
PRIOR = Path(__file__).with_name("evolve_bias_components_prior.json")
DESIGN = Path(__file__).with_name("evolve_bias_components_design.json")


def vectors(spec, task):
    x = np.array(spec["vectors"]["max" if task == "sum2" else "sum"])
    u = np.full(22, 1 / 22)
    rest = np.ones(22, dtype=bool)
    rest[[1, 8]] = False
    ig = np.full(22, x[rest].sum() / 20)
    ig[[1, 8]] = x[[1, 8]]
    r = u.copy()
    r[rest] = x[rest] / x[rest].sum() * (20 / 22)
    return {a: p.tolist() for a, p in zip(ARMS, (u, ig, r, x))}


def validate_vectors(spec):
    eb.validate_spec(spec)
    for task in TASKS:
        v = {a: np.asarray(p) for a, p in vectors(spec, task).items()}
        for p in v.values():
            if (
                p.shape != (22,)
                or not np.isfinite(p).all()
                or (p <= 0).any()
                or not np.isclose(p.sum(), 1)
            ):
                raise ValueError("invalid component probabilities")
        assert np.array_equal(v["IG"][[1, 8]], v["X"][[1, 8]])
        assert np.array_equal(v["R"][[1, 8]], v["U"][[1, 8]])
        rest = [i for i in range(22) if i not in (1, 8)]
        assert np.ptp(v["IG"][rest]) == 0
        assert np.allclose(v["R"][rest] / v["X"][rest], (20 / 22) / v["X"][rest].sum())


def reliable(c):
    return (
        c.get("ratio") is not None
        and c.get("lower") is not None
        and c.get("upper") is not None
        and c.get("finite_fraction", 0) >= 0.99
    )


def labels_for_task(comps, task):
    replicate = comps[f"{task}/U/X"]
    replicated = reliable(replicate) and replicate["lower"] > 1
    arms = {}
    for arm in ("IG", "R"):
        cx, uc = comps[f"{task}/{arm}/X"], comps[f"{task}/U/{arm}"]
        sufficiency = "open"
        if reliable(cx):
            if cx["upper"] < 1.5:
                sufficiency = "within"
            elif cx["lower"] > 1.5:
                sufficiency = "short"
        faster = reliable(uc) and uc["lower"] > 1
        label = "not applicable: X not replicated"
        if replicated:
            label = (
                "carries"
                if sufficiency == "within" and faster
                else "falls short"
                if sufficiency == "short"
                else "unresolved"
            )
        arms[arm] = dict(
            label=label, vs_X=sufficiency, vs_U="faster" if faster else "not resolved"
        )
    return dict(X_replicated=bool(replicated), arms=arms)


def closure(task_labels, incomplete=False):
    if incomplete or not all(task_labels[t]["X_replicated"] for t in TASKS):
        return "park"
    carrying = [
        {a for a in ("IG", "R") if task_labels[t]["arms"][a]["label"] == "carries"}
        for t in TASKS
    ]
    if carrying[0] and carrying[0] == carrying[1]:
        return "close: " + "+".join(sorted(carrying[0]))
    return "park"


def comparisons(rows, boot=BOOT):
    result = {}
    for ti, task in enumerate(TASKS):
        for pi, (a, b) in enumerate(PAIRS):
            aa = [r for r in rows if r["task"] == task and r["arm"] == a]
            bb = [r for r in rows if r["task"] == task and r["arm"] == b]
            c = eb.compare(aa, bb, MASTER + 300000 + 100 * ti + pi, boot, alpha=ALPHA)
            # The old F/E/R labels are for another study; use only estimates.
            c.pop("verdict")
            result[f"{task}/{a}/{b}"] = {
                **c,
                "task": task,
                "numerator": a,
                "denominator": b,
                "look": 1,
            }
    return result


def precision(prior, out, trials=200, boot=BOOT, sizes=(250, 300, 350)):
    """Old data only. Independent synthetic arms, paired index resampling."""
    results = dict(
        master=MASTER,
        trials=trials,
        bootstrap_draws=boot,
        alpha=ALPHA,
        sizes={},
        source_sha256=hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
        note="Per-comparison precision, not joint-verdict or intermediate-effect power.",
    )
    for n in sizes:
        by_task = {}
        for ti, task in enumerate(TASKS):
            old = [
                r
                for r in prior["runs"]
                if r["task"] == task and r["arm"] == "mismatched"
            ]
            assert old and all(r["complete"] and r["cap"] == CAP for r in old)
            rng = np.random.default_rng(eb.stream_seed(f"precision/{task}/{n}", MASTER))
            within = short = 0
            uppers = []
            for k in range(trials):
                a, b = [
                    [
                        {**old[j], "seed": i}
                        for i, j in enumerate(rng.integers(len(old), size=n))
                    ]
                    for _ in range(2)
                ]
                seed = MASTER + 500000 + ti * 100000 + n * 200 + k
                c = eb.compare(a, b, seed, boot, alpha=ALPHA)
                within += bool(reliable(c) and c["upper"] < 1.5)
                if c["upper"] is not None:
                    uppers.append(c["upper"])
                scaled = [
                    {
                        **r,
                        "event": r["event"] and r["time"] * 2.25 <= CAP,
                        "time": min(CAP, r["time"] * 2.25),
                    }
                    for r in a
                ]
                # Scaling without censoring leaves bootstrap medians proportional.
                if all(r["event"] for r in a) and all(r["event"] for r in scaled):
                    short += bool(reliable(c) and c["lower"] * 2.25 > 1.5)
                else:
                    d = eb.compare(scaled, b, seed, boot, alpha=ALPHA)
                    short += bool(reliable(d) and d["lower"] > 1.5)
                if (k + 1) % 25 == 0:
                    print(f"precision n={n} {task}: {k + 1}/{trials}", flush=True)
            by_task[task] = dict(
                within_probability=within / trials,
                short_probability=short / trials,
                within_mc_interval=eb.binomial(within, trials),
                short_mc_interval=eb.binomial(short, trials),
                median_upper=float(np.median(uppers)) if uppers else None,
            )
        results["sizes"][str(n)] = by_task
        passed = all(
            min(c["within_probability"], c["short_probability"]) >= 0.8
            for c in by_task.values()
        )
        results.update(n=n, precision_passed=passed)
        eb.write_json(out / "precision.json", results)
        if passed:
            break
    return results


def jobs_for(spec, out, n, deadline, smoke=False):
    pop, cap = (64, 16384) if smoke else (POP, CAP)
    phase = "smoke" if smoke else "main"
    offset = 20000 if smoke else 100000
    return [
        dict(
            phase=phase,
            task=t,
            arm=a,
            replicate=i,
            seed=MASTER + offset + i,
            master=MASTER,
            pop=pop,
            cap=cap,
            probs=vectors(spec, t)[a],
            component_diagnostics=True,
            deadline=deadline,
            out=str(out / "runs" / phase / t / a / f"{MASTER + offset + i}.json"),
        )
        for i in range(n)
        for t in TASKS
        for a in ARMS
    ]


def sampler_audit():
    result = {}
    for task in TASKS:
        idx = eb.training_indices(task, MASTER + 100000, MASTER)
        y = eb.labels(task, eb.DOMAIN[idx])
        other = "max2" if task == "sum2" else "sum2"
        assert len(y) == 64 and y.sum() == 32
        result[task] = dict(
            seed=MASTER + 100000,
            master=MASTER,
            indices=idx.tolist(),
            positives=int(y.sum()),
            n=64,
            balance=float(y.mean()),
            both_labels=True,
            constant_accuracy=0.5,
            proxy=other,
            proxy_train_accuracy=float((eb.labels(other, eb.DOMAIN[idx]) == y).mean()),
            proxy_domain_accuracy=float(
                (eb.labels(other, eb.DOMAIN) == eb.labels(task, eb.DOMAIN)).mean()
            ),
        )
    return result


def sample_components(spec, out, n, deadline):
    data = {}
    for task in TASKS:
        data[task] = {}
        for arm in ("IG", "R"):
            q = vectors(spec, task)[arm]
            stream = f"sampling/components/{task}/{arm}"
            rng = np.random.default_rng(eb.stream_seed(stream, MASTER))
            idx = eb.training_indices(task, MASTER + 40000, MASTER)
            screen = eb.DOMAIN[idx].tolist()
            screen_y = [eb.labels(task, eb.DOMAIN[idx]).tolist()]
            full_y = [eb.labels(task, eb.DOMAIN).tolist()]
            done = hits = 0
            start = time.monotonic()
            while done < n:
                if time.monotonic() >= deadline:
                    raise eb.Deadline("component sampling incomplete")
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
                        rust_tag_screen(selected.tobytes(), 64, eb.DOMAIN_LIST, full_y)
                    )
                done += count
                data[task][arm] = {
                    **eb.binomial(hits, done),
                    "requested": n,
                    "complete": done == n,
                    "seconds": time.monotonic() - start,
                    "stream": stream,
                    "master": MASTER,
                    "probs": q,
                    "screen_indices": idx.tolist(),
                    "provenance": "fresh component sampling",
                }
                if done % 1000000 == 0 or done == n:
                    eb.write_json(out / "sampling.json", data)
            print(f"sampled {task}/{arm}: {hits}/{n}", flush=True)
    return data


def sampling_for(spec, sampling, task, arm):
    if arm in ("IG", "R"):
        return sampling.get(task, {}).get(arm)
    source = "uniform" if arm == "U" else "max" if task == "sum2" else "sum"
    s = spec["sampling"][source]
    return {
        **eb.binomial(s["counts"][task], s["n"]),
        "provenance": "historical 1558, frozen by 1705",
        "source": source,
        "source_commit": spec["source_commit"],
        "source_sha256": spec["source_sha256"],
    }


def summarize_cells(rows, sampling, spec):
    cells = {}
    interactions = {}
    for task in TASKS:
        for arm in ARMS:
            rr = [r for r in rows if r["task"] == task and r["arm"] == arm]
            med = eb.km_curve(rr)[2]
            s = sampling_for(spec, sampling, task, arm)
            p = s["p"] if s else None
            random_median = math.log(0.5) / math.log1p(-p) if p and p < 1 else None
            cells[f"{task}/{arm}"] = dict(
                n=len(rr),
                complete=sum(r["complete"] for r in rr),
                solves=sum(r["complete"] and r["event"] for r in rr),
                solve_rate=sum(r["event"] for r in rr) / len(rr)
                if rr and all(r["complete"] for r in rr)
                else None,
                km_median=med,
                sampling=s,
                cap=rr[0]["cap"] if rr else CAP,
                random_search_median=random_median,
                evolution_over_random=random_median / med
                if random_median and med
                else None,
                speed_over_U=None,
                sampling_lift=None,
                sampling_lift_interval=None,
                pass_through=None,
                share_log_gain=None,
                saved_shortcuts=sum(len(r.get("shortcuts", [])) for r in rr),
                runs_with_saved_shortcuts=sum(bool(r.get("shortcuts")) for r in rr),
                training_thresholds={
                    name: {
                        "reached": sum(r.get(name) is not None for r in rr),
                        "first_generations": [
                            r.get(name) for r in sorted(rr, key=lambda r: r["seed"])
                        ],
                        "note": "Trajectories stop at the first exact solve or cap; null means not reached before stopping.",
                    }
                    for name in ("first_training_075", "first_training_100")
                },
            )
        u, x = [cells[f"{task}/{a}"] for a in ("U", "X")]
        for arm in ARMS:
            c = cells[f"{task}/{arm}"]
            if c["sampling"]:
                cs, us = c["sampling"], u["sampling"]
                c["sampling_lift"] = cs["p"] / us["p"]
                c["sampling_lift_interval"] = [
                    cs["lower"] / us["upper"],
                    cs["upper"] / us["lower"],
                ]
            if u["km_median"] and c["km_median"]:
                c["speed_over_U"] = u["km_median"] / c["km_median"]
                if c["sampling_lift"]:
                    c["pass_through"] = c["speed_over_U"] / c["sampling_lift"]
                if x["km_median"] and u["km_median"] != x["km_median"]:
                    c["share_log_gain"] = math.log(c["speed_over_U"]) / math.log(
                        u["km_median"] / x["km_median"]
                    )
        m = [cells[f"{task}/{a}"]["km_median"] for a in ARMS]
        interactions[task] = m[1] * m[2] / (m[0] * m[3]) if all(m) else None
    return cells, interactions


def decode(genome):
    """Typed structural output dependency slice; conservative, not necessity.

    Mirrors preserve-mode stack types and TAG recursion/depth. IF_GT includes
    all three operands; max includes all same-tag outputs. No value-based gate.
    """
    g = np.frombuffer(bytes.fromhex(genome), dtype=np.uint8)
    if len(g) != 128:
        raise ValueError("decoder requires L64 genome")
    ops, tags = tagged.split(g)
    runs, cur = [], None
    for i, (op, tg) in enumerate(zip(ops.tolist(), tags.tolist())):
        if op == 20:
            cur = dict(tag=tg, sep=i, body=[])
            runs.append(cur)
        elif cur is not None:
            cur["body"].append((op, tg, i))
    by_tag = {}
    for k, run in enumerate(runs):
        by_tag.setdefault(run["tag"], []).append(k)
    executed = set()

    def tag_deps(tag, depth, visiting):
        return set().union(*(run_deps(k, depth, visiting) for k in by_tag.get(tag, [])))

    def run_deps(k, depth, visiting):
        if k in visiting or depth > tagged.MAX_DEPTH:
            return set()
        executed.add(k)
        stack = []

        def pop(typ):
            if stack and stack[-1][0] == typ:
                return stack.pop()[1]
            return set()

        for op, tg, i in runs[k]["body"]:
            if op in (0, 12, 13):
                continue
            if op == 1:
                stack.append(("list", {i}))
            elif op in (2, 3, 15, 16, 19):
                stack.append(("int", {i}))
            elif op == 4:
                pop("str")
                stack.append(("chars", {i}))
            elif op == 14:
                stack.append(("list", pop("chars") | {i}))
            elif op in (5, 6, 11, 18):
                stack.append(("int", pop("list") | {i}))
            elif op in (7, 8):
                b, a = pop("int"), pop("int")
                stack.append(("int", a | b | {i}))
            elif op == 9:
                if stack:
                    typ, deps = stack[-1]
                    stack.append((typ, deps | {i}))
                else:
                    stack.extend([("int", {i}), ("int", {i})])
            elif op == 10:
                b = stack.pop() if stack else ("int", set())
                a = stack.pop() if stack else ("int", set())
                stack.extend([(b[0], b[1] | {i}), (a[0], a[1] | {i})])
            elif op == 17:
                if len(stack) < 3:
                    for _ in range(3):
                        pop("int")
                    stack.append(("int", {i}))
                else:
                    cond, then, other = pop("int"), pop("int"), pop("int")
                    stack.append(("int", cond | then | other | {i}))
            elif op == 21:
                stack.append(("int", tag_deps(tg, depth + 1, visiting | {k}) | {i}))
        return stack[-1][1] if stack and stack[-1][0] == "int" else set()

    deps = sorted(tag_deps(0, 0, frozenset()))
    return dict(
        tape_INPUT=bool(np.any(ops == 1)),
        tape_GT=bool(np.any(ops == 8)),
        output_dependency_INPUT=any(ops[i] == 1 for i in deps),
        output_dependency_GT=any(ops[i] == 8 for i in deps),
        dependency_positions=deps,
        dependency_ops=[int(ops[i]) for i in deps],
        output_connected_runs=sorted(executed),
        runs=[
            dict(tag=r["tag"], sep=r["sep"], body=[list(c) for c in r["body"]])
            for r in runs
        ],
        qualification="Conservative structural output-value dependencies; IF_GT includes all operands and same-tag max includes all branches. Presence here does not prove necessity or ancestry.",
    )


def decode_all(rows, prior, out):
    records = []
    cache = {}
    for source, rr in (("1705", prior["runs"]), ("1814", rows)):
        for r in rr:
            gs = [("solver", r.get("solver"))] + [
                ("shortcut", s["genome"]) for s in r.get("shortcuts", [])
            ]
            for kind, genome in gs:
                if genome is None:
                    continue
                if genome not in cache:
                    g = np.frombuffer(bytes.fromhex(genome), dtype=np.uint8)
                    pred = eb.predictions([g], eb.DOMAIN_LIST)[0]
                    cache[genome] = {
                        **decode(genome),
                        "agreement": {
                            t: float((pred == eb.labels(t, eb.DOMAIN)).mean())
                            for t in TASKS
                        },
                    }
                agreement = cache[genome]["agreement"][r["task"]]
                if (kind == "solver" and agreement != 1.0) or (
                    kind == "shortcut" and agreement == 1.0
                ):
                    raise ValueError(
                        "saved genome classification failed independent full-domain re-verification"
                    )
                records.append(
                    dict(
                        source=source,
                        task=r["task"],
                        arm=r["arm"],
                        seed=r["seed"],
                        kind=kind,
                        genome=genome,
                        **cache[genome],
                    )
                )
    eb.write_json(
        out / "decoded.json", dict(prior_source=prior["source"], records=records)
    )


def plot_results(out, rows, cells):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = dict(zip(ARMS, ("#555555", "#1f77b4", "#e07b22", "#25974b")))
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    structure, s_axes = plt.subplots(2, 2, figsize=(13, 8))
    for ti, task in enumerate(TASKS):
        ax, hist = axes[ti]
        for arm in ARMS:
            rr = [r for r in rows if r["task"] == task and r["arm"] == arm]
            if not rr:
                continue
            x, y, _ = eb.km_curve(rr)
            ax.step(
                x, y, where="post", color=colors[arm], label=f"{arm} KM n={len(rr)}"
            )
            s = cells[f"{task}/{arm}"]["sampling"]
            if s:
                grid = np.geomspace(1, rr[0]["cap"], 300)
                ax.plot(
                    grid,
                    eb.random_cdf(grid, s["p"]),
                    "--",
                    color=colors[arm],
                    alpha=0.65,
                )
                ax.fill_between(
                    grid,
                    eb.random_cdf(grid, s["lower"]),
                    eb.random_cdf(grid, s["upper"]),
                    color=colors[arm],
                    alpha=0.1,
                )
            for r in rr:
                h = r["training_history"]
                hist.plot(
                    [v["gen"] for v in h],
                    [v["best"] for v in h],
                    color=colors[arm],
                    alpha=0.1,
                )
                sparse = r["history"]
                s_axes[ti, 0].plot(
                    [v["evaluations"] for v in sparse],
                    [v["distinct"] / r["pop"] for v in sparse],
                    color=colors[arm],
                    alpha=0.12,
                )
                s_axes[ti, 1].plot(
                    [v["evaluations"] for v in sparse],
                    [v["run_census"]["runs"] for v in sparse],
                    color=colors[arm],
                    alpha=0.12,
                )
        ax.set(
            xscale="symlog",
            xlabel="Candidate evaluations",
            ylabel="P(exact solve)",
            ylim=(0, 1),
            title=f"{task}: KM; dashed random search (historical U/X)",
        )
        ax.legend(fontsize=8)
        hist.set(
            xlabel="Generation (stops at event)",
            ylabel="Best training accuracy",
            ylim=(0, 1.02),
            title=task,
        )
        for j, name in enumerate(("Distinct / population", "Mean runs / genome")):
            s_axes[ti, j].set(
                xscale="log", xlabel="Candidate evaluations", ylabel=name, title=task
            )
    fig.tight_layout()
    structure.tight_layout()
    fig.savefig(out / "diagnostics.png", dpi=150)
    structure.savefig(out / "structure.png", dpi=150)
    plt.close(fig)
    plt.close(structure)


def finish(out, result, rows, sampling, spec, prior, boot=BOOT):
    comps = comparisons(rows, boot)
    result["comparisons"] = comps
    result["task_labels"] = {t: labels_for_task(comps, t) for t in TASKS}
    result["cells"], result["interaction"] = summarize_cells(rows, sampling, spec)
    # Engineering smoke must never return a scientific verdict.
    result["decision"] = (
        "smoke only"
        if result["smoke_only"]
        else closure(result["task_labels"], result["incomplete"])
    )
    eb.write_json(out / "comparisons.json", comps)
    eb.write_json(out / "result.json", result)
    decode_all(rows, prior, out)
    plot_results(out, rows, result["cells"])
    lines = [
        "# Component sufficiency",
        f"Decision: **{result['decision']}**. n={result['n']}. Incomplete={result['incomplete']}.",
        "Labels concern coupled initialization/mutation vector interventions within 1.5× of X, not mechanisms or most of the gain.",
        "Sampling lifts and intervals are descriptive; U/X sampling is historical. Lift intervals use the envelope of two exact-binomial 95% intervals, not a confirmatory equivalence test.",
        "| task | X replicated | IG label / vs X / vs U | R label / vs X / vs U |",
        "|---|---|---|---|",
    ]
    for t, v in result["task_labels"].items():
        parts = [
            f"{a['label']} / {a['vs_X']} / {a['vs_U']}" for a in v["arms"].values()
        ]
        lines.append(f"| {t} | {v['X_replicated']} | {' | '.join(parts)} |")
    lines += [
        "",
        "| contrast | n | ratio | 99.5% interval | finite fraction |",
        "|---|---|---|---|---|",
    ]
    for key, c in comps.items():
        lines.append(
            f"| {key} | {c['n']} | {c['ratio']} | {c['lower']}, {c['upper']} | {c['finite_fraction']} |"
        )
    lines += [
        "",
        "| cell | KM median | sampling lift (interval envelope) | pass-through | share of log gain |",
        "|---|---|---|---|---|",
    ]
    for key, c in result["cells"].items():
        lines.append(
            f"| {key} | {c['km_median']} | {c['sampling_lift']} ({c['sampling_lift_interval']}) | {c['pass_through']} | {c['share_log_gain']} |"
        )
    lines += [
        "",
        f"Descriptive multiplicative interaction (m_IG*m_R)/(m_U*m_X): {result['interaction']}",
        "Decoding in decoded.json is a conservative structural dependency slice, not causal necessity or shortcut ancestry.",
        "Unresolved means insufficient evidence at this n, not no gain. Nonreplication means not replicated here, not that 1705 was noise.",
    ]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    if not result["incomplete"]:
        (out / "COMPLETE").write_text("smoke" if result["smoke_only"] else "finished\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seconds", type=int, default=9900)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--precision",
        action="store_true",
        help="Old-data precision only; no new tapes or evolution.",
    )
    args = parser.parse_args()
    if args.workers < 1 or args.seconds <= (0 if args.smoke or args.precision else 900):
        parser.error("positive workers and a sufficient seconds budget required")
    os.environ["RAYON_NUM_THREADS"] = "1"
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    if (
        (out / "COMPLETE").exists()
        or (out / "result.json").exists()
        or (out / "runs").exists()
        or (out / "sampling.json").exists()
    ):
        raise ValueError(
            "RUN_DIR contains prior experiment outputs; use a fresh directory"
        )
    prior = json.loads(PRIOR.read_text())
    if args.precision:
        precision(prior, out)
        return 0
    spec = json.loads(eb.SPEC_PATH.read_text())
    validate_vectors(spec)
    design = json.loads(DESIGN.read_text())
    if (
        design["n"] not in (250, 300, 350)
        or design["master"] != MASTER
        or design["bootstrap_draws"] != BOOT
        or design["alpha"] != ALPHA
        or design["prior_sha256"] != hashlib.sha256(PRIOR.read_bytes()).hexdigest()
        or design["vectors_sha256"]
        != hashlib.sha256(eb.SPEC_PATH.read_bytes()).hexdigest()
    ):
        raise ValueError("invalid frozen design")
    n = 1 if args.smoke else design["n"]
    jobs = jobs_for(spec, out, n, time.monotonic() + args.seconds, args.smoke)
    eb.write_json(
        out / "vectors.json",
        dict(
            source=spec["source"],
            source_sha256=hashlib.sha256(eb.SPEC_PATH.read_bytes()).hexdigest(),
            vectors={t: vectors(spec, t) for t in TASKS},
        ),
    )
    eb.write_json(
        out / "design.json",
        {
            **design,
            "smoke_only": args.smoke,
            "actual_n": n,
            "pop": jobs[0]["pop"],
            "cap": jobs[0]["cap"],
            "workers": args.workers,
            "seconds": args.seconds,
        },
    )
    eb.write_json(out / "sampler_audit.json", sampler_audit())
    result = dict(
        n=n,
        smoke_only=args.smoke,
        incomplete=False,
        master_seed=MASTER,
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"])
        .decode()
        .strip(),
        git_dirty=bool(
            subprocess.check_output(["git", "status", "--porcelain"]).strip()
        ),
        prior_sha256=hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
        design=design,
    )
    rows, sampling = [], {}
    compute_deadline = time.monotonic() + args.seconds - (0 if args.smoke else 900)
    for j in jobs:
        j["deadline"] = compute_deadline
    try:
        sampling = sample_components(
            spec, out, 10000 if args.smoke else 125000000, compute_deadline
        )
        rows = eb.run_jobs(jobs, args.workers, out)
        result["incomplete"] = len(rows) != 8 * n or any(
            not r["complete"] for r in rows
        )
    except eb.Deadline as exc:
        result.update(incomplete=True, error=str(exc))
        if (out / "sampling.json").exists():
            sampling = json.loads((out / "sampling.json").read_text())
    finish(out, result, rows, sampling, spec, prior, boot=2000 if args.smoke else BOOT)
    return int(result["incomplete"])


if __name__ == "__main__":
    raise SystemExit(main())
