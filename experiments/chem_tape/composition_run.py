"""Deadline-gated composition-bank feasibility study; writes only RUN_DIR."""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import time
from pathlib import Path

import numpy as np
from scipy.stats import chi2

from experiments.chem_tape.composition_bank import INPUTS
from experiments.chem_tape.composition_calibrate import calibrate
from experiments.chem_tape.composition_report import (
    decision,
    paired_ratios,
    splits,
    summaries,
)
from experiments.chem_tape.composition_search import ARMS, R, Decoder, outputs, search


def write_json(out, name, data):
    temporary = out / (name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    temporary.replace(out / name)


def run_jobs(pool, fn, jobs, deadline, callback):
    it = pool.imap_unordered(fn, jobs, chunksize=1)
    done = 0
    while done < len(jobs):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        try:
            row = it.next(timeout=min(1, remaining))
        except mp.TimeoutError:
            continue
        callback(row)
        done += 1
    return True


def sample(job):
    arm, table, seed, count, bank = job
    d = Decoder(table)
    rng = np.random.default_rng(seed)
    idx = np.random.default_rng(22473000).choice(625, 48, replace=False)
    inputs = [INPUTS[i] for i in idx]
    labels = np.array([c["labels"][idx] for c in bank])
    hits = {c["id"]: 0 for c in bank}
    start = time.monotonic()
    for offset in range(0, count, 1000):
        programs = d.decode(
            rng.integers(R, size=(min(count - offset, 1000), 32), dtype=np.int32)
        )
        observed = outputs(programs, inputs)
        for c, label in zip(bank, labels):
            candidates = np.flatnonzero(np.all(observed == label, axis=1))
            if len(candidates):
                exact = outputs(programs[candidates], INPUTS)
                hits[c["id"]] += int(
                    np.count_nonzero(np.all(exact == c["labels"], axis=1))
                )
    return dict(
        arm=arm, seed=seed, genotypes=count, hits=hits, seconds=time.monotonic() - start
    )


def mutation_cascades(tables):
    rng = np.random.default_rng(22475000)
    alleles = rng.integers(R, size=(10000, 32), dtype=np.int32)
    changed = alleles.copy()
    positions = rng.integers(32, size=10000)
    changed[np.arange(10000), positions] = rng.integers(R, size=10000)
    result = {}
    for arm in ARMS:
        d = Decoder(tables[arm])
        cascade = np.sum(d.decode(alleles) != d.decode(changed), axis=1)
        result[arm] = dict(
            single_allele_resample=True,
            n=10000,
            mean_emitted_changes=float(cascade.mean()),
            histogram=np.bincount(cascade, minlength=33).tolist(),
        )
    return result


def overlap(bank):
    result = {}
    for c in bank:
        own = list(zip(c["canonical"], c["canonical"][1:]))
        other = {
            bigram
            for x in bank
            if x["id"] != c["id"]
            for bigram in zip(x["canonical"], x["canonical"][1:])
        }
        result[c["id"]] = dict(
            shared=sum(b in other for b in own),
            total=len(own),
            fraction=sum(b in other for b in own) / len(own),
        )
    return result


def plots(out, rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        if not rs:
            continue
        budgets = np.unique(
            np.geomspace(256, max(r["cap"] for r in rs), 256).astype(int)
        )
        axes[0].plot(
            budgets,
            [
                sum(r["solved"] and r["evaluations"] <= b for r in rs) / len(rs)
                for b in budgets
            ],
            label=arm,
        )
        # Curves explicitly aggregate a varying number of surviving runs.
        points = {}
        for r in rs:
            for evaluation, fit, diversity in r["curve"]:
                points.setdefault(evaluation, []).append((fit, diversity))
        axes[1].plot(
            sorted(points),
            [np.mean([v[0] / 64 for v in points[x]]) for x in sorted(points)],
            label=arm,
        )
        axes[2].plot(
            sorted(points),
            [np.mean([v[1] for v in points[x]]) for x in sorted(points)],
            label=arm,
        )
    axes[0].set(xlabel="Evaluations", ylabel="Fraction exactly solved", xscale="log")
    axes[1].set(
        xlabel="Evaluations", ylabel="Mean best accuracy (active runs)", xscale="log"
    )
    axes[2].set(
        xlabel="Evaluations", ylabel="Mean diversity (active runs)", xscale="log"
    )
    if rows:
        for axis in axes:
            axis.legend()
    fig.tight_layout()
    fig.savefig(out / "curves.png", dpi=150)
    plt.close(fig)


def run(args):
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    deadline = start + args.deadline_seconds
    work_deadline = deadline - args.reserve_seconds
    rows, sampling = [], []
    try:
        tables, bank, calibration = calibrate(
            out,
            args.workers,
            args.cap,
            args.validation_count,
            args.slice_count,
            min(work_deadline, start + 900),
        )
    except TimeoutError as e:
        write_json(
            out,
            "result.json",
            dict(
                outcome="U",
                reason=str(e),
                stage="0",
                wall_seconds=time.monotonic() - start,
            ),
        )
        (out / "summary.md").write_text("Outcome U: unresolved. " + str(e) + "\n")
        plots(out, [])
        return
    retained = [c for c in bank if not c["rejects"]]
    write_json(out, "bank.json", [{**c, "labels": c["labels"].tolist()} for c in bank])
    write_json(
        out,
        "config.json",
        dict(
            task="2026-10-05-2247",
            workers=args.workers,
            cap=args.cap,
            population=256,
            alleles=32,
            allele_range=R,
            mutation=0.03,
            crossover=0.7,
            training_cases=64,
            domain_size=625,
            seeds=args.seeds,
            stage_b_seed_start=22471000,
            stage_c_seed_start=22472000,
            bootstrap_seed=22474000,
            deadline_seconds=args.deadline_seconds,
            reserve_seconds=args.reserve_seconds,
            smoke=args.smoke,
        ),
    )
    result = None
    topups_complete = True
    complete = True
    projection = {}
    partial_block_results = []
    # Alias failure is an approved early stop; it needs no stage-B seeds.
    if len(retained) < 7 or not any(s["eligible"] for s in splits(bank, {}, True)):
        result = decision(bank, rows, True)
    elif calibration["stage_0_seconds"] > 900 and not args.smoke:
        result = dict(outcome="U", reason="stage 0 exceeded its 15-minute allowance")
    else:
        # G is context-dependent; inflate U timing to cover its measured decode
        # overhead conservatively, and use a capped upper search forecast too.
        max_calibration = max(r["seconds"] for r in calibration["searches"])
        mean = calibration["mean_censored_inclusive_seconds"]
        search_seconds = len(retained) * 4 * args.seeds * mean / args.workers * 1.5
        worst_search = (
            len(retained) * 4 * args.seeds * max_calibration / args.workers * 1.5
        )
        topup_seconds = min(
            1800, max(0, (work_deadline - time.monotonic()) - search_seconds)
        )
        total_throughput = (
            sum(s["genotypes"] for s in calibration["sampling_speeds"])
            / calibration["sampling_parallel_wall_seconds"]
        )
        desired = args.sample_count
        for count in (desired, min(desired, 50000000), 0):
            sampling_seconds = count * 4 / total_throughput
            if (
                time.monotonic() + search_seconds + topup_seconds + sampling_seconds
                <= work_deadline
                or count == 0
            ):
                desired = count
                break
        projection = dict(
            stage_b_seconds=search_seconds,
            capped_stage_b_seconds=worst_search,
            topup_reserve_seconds=topup_seconds,
            capped_all_possible_topups_seconds=len(retained)
            * 3
            * 100
            * max_calibration
            / args.workers
            * 1.5,
            sampling_per_arm=desired,
            sampling_seconds=desired * 4 / total_throughput,
            measured_sampling_genotypes_per_second_8_workers=total_throughput,
        )
        write_json(out, "projection.json", projection)
        if time.monotonic() + search_seconds > work_deadline and not args.smoke:
            result = dict(
                outcome="U",
                reason="stage-0 projection cannot complete approved stage B by deadline",
                implementation_infeasible=True,
            )
        else:
            pool = mp.Pool(args.workers)
            try:

                def record(row):
                    rows.append(row)
                    # Persist each completed seed before starting another block.
                    with (out / "searches.jsonl").open("a") as f:
                        f.write(json.dumps(row) + "\n")

                for block in range(0, args.seeds, 10):
                    jobs = [
                        (c, arm, tables[arm], 22471000 + seed, args.cap, 256)
                        for seed in range(block, min(block + 10, args.seeds))
                        for c in retained
                        for arm in ARMS
                    ]
                    before_block = len(rows)
                    if not run_jobs(pool, search, jobs, work_deadline, record):
                        partial_block_results = rows[before_block:]
                        rows = rows[:before_block]
                        complete = False
                        break
                    print(
                        json.dumps(
                            dict(
                                stage="B",
                                seed_block=block,
                                completed=len(rows),
                                elapsed_seconds=time.monotonic() - start,
                            )
                        ),
                        flush=True,
                    )
                if complete and not args.smoke:
                    summary = summaries(rows)
                    jobs = []
                    for c in retained:
                        for arm in ("U", "F", "G"):
                            s = summary[c["id"] + "|" + arm]
                            low, high = s["km_median_95_interval"]
                            triggered = (
                                (30 <= s["solves"] <= 39)
                                if arm == "U"
                                else (
                                    low is not None
                                    and low <= 4096
                                    and (high is None or high >= 4096)
                                )
                            )
                            if triggered:
                                jobs.extend(
                                    (
                                        c,
                                        arm,
                                        tables[arm],
                                        22472000 + seed,
                                        args.cap,
                                        256,
                                    )
                                    for seed in range(100)
                                )
                    write_json(
                        out,
                        "topup_plan.json",
                        [dict(cell=j[0]["id"], arm=j[1], seed=j[3]) for j in jobs],
                    )
                    topup_deadline = min(work_deadline, time.monotonic() + 1800)
                    topups_complete = run_jobs(
                        pool, search, jobs, topup_deadline, record
                    )
                if complete and topups_complete and desired:
                    jobs = [
                        (
                            arm,
                            tables[arm],
                            22473000 + i * 100000 + chunk,
                            min(args.sample_chunk, desired - chunk * args.sample_chunk),
                            retained,
                        )
                        for i, arm in enumerate(ARMS)
                        for chunk in range(math.ceil(desired / args.sample_chunk))
                    ]

                    def record_sample(row):
                        sampling.append(row)
                        with (out / "sampling.jsonl").open("a") as f:
                            f.write(json.dumps(row) + "\n")

                    sampling_complete = run_jobs(
                        pool, sample, jobs, work_deadline, record_sample
                    )
                else:
                    sampling_complete = not desired
            finally:
                pool.terminate()
                pool.join()
            complete &= args.seeds == 50 and args.cap == 524288
            result = decision(bank, rows, complete, topups_complete)
            result["sampling_complete"] = sampling_complete
    sample_summary = {}
    for arm in ARMS:
        rs = [r for r in sampling if r["arm"] == arm]
        n = sum(r["genotypes"] for r in rs)
        sample_summary[arm] = {}
        for c in retained:
            hits = sum(r["hits"][c["id"]] for r in rs)
            sample_summary[arm][c["id"]] = dict(
                n=n,
                hits=hits,
                rate=hits / n if n else None,
                zero_hit_95_upper_bound=-math.expm1(math.log(0.05) / n)
                if n and hits == 0
                else None,
                poisson_95_interval=[
                    float(chi2.ppf(0.025, 2 * hits) / (2 * n)) if hits else 0,
                    float(chi2.ppf(0.975, 2 * (hits + 1)) / (2 * n)),
                ]
                if n
                else [None, None],
            )
    ratios = paired_ratios(rows)
    for ratio in ratios:
        cid = ratio["cell"]
        left = sample_summary[ratio["bias"]][cid]["rate"]
        right = sample_summary[ratio["control"]][cid]["rate"]
        ratio["sampling_rate_ratio"] = (
            left / right if left is not None and right else None
        )
    result.update(
        sampling=sample_summary,
        partial_block_results=partial_block_results,
        descriptive_ratios=ratios,
        mutation_cascades=mutation_cascades(tables),
        canonical_bigram_overlap=overlap(bank),
        projection=projection,
        wall_seconds=time.monotonic() - start,
    )
    write_json(out, "result.json", result)
    plots(out, rows)
    meanings = {
        "U": "Unresolved: missing complete search or top-up data.",
        "1": "Bank fails the alias screens.",
        "2": "No eligible tractable split.",
        "3": "Every eligible split lacks fixed-control headroom.",
        "4a": "Selected split has no feasible tested inner budget.",
        "4": "Feasible split, but experiment two needs a staged allocation.",
        "5": "Go: freeze the selected split and controls; use fresh seeds next.",
    }
    (out / "summary.md").write_text(
        "# Composition-bank feasibility\n\nOutcome "
        + result["outcome"]
        + ": "
        + meanings[result["outcome"]]
        + "\n\n"
        "Raw per-seed data: searches.jsonl. Full metrics and selection: result.json.\n"
        "This feasibility study does not test learned transfer.\n"
    )
    print(
        json.dumps(dict(outcome=result["outcome"], seconds=time.monotonic() - start)),
        flush=True,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--deadline-seconds", type=int, default=9600)
    ap.add_argument("--reserve-seconds", type=int, default=300)
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--cap", type=int, default=524288)
    ap.add_argument("--sample-count", type=int, default=200000000)
    ap.add_argument("--sample-chunk", type=int, default=100000)
    ap.add_argument("--validation-count", type=int, default=100000)
    ap.add_argument("--slice-count", type=int, default=1000000)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if not args.smoke and (
        args.seeds != 50
        or args.cap != 524288
        or args.validation_count != 100000
        or args.slice_count != 1000000
    ):
        ap.error("full runs must use approved search and validation sizes")
    run(args)


if __name__ == "__main__":
    main()
