"""Deadline-bounded approved 0001 assembly-family experiment.

Run as a module from the worktree; every artifact is written under RUN_DIR.
A serial spawn pool releases the large screen between domains. Search/sampling
workers use spawn and one Rayon thread, and checkpoints survive deadlines.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
from pathlib import Path
import time

import numpy as np
from scipy.stats import beta

from experiments.chem_tape.assembly_bank import (
    DOMAINS,
    SHAPES,
    choose_pair,
    inputs_for,
    roster,
    screen_domain,
    stage_b_domain,
)
from experiments.chem_tape.assembly_maps import frozen_controls, freeze_diagnostics
from experiments.chem_tape.assembly_report import report
from experiments.chem_tape.composition_run import plots, run_jobs, write_json
from experiments.chem_tape.composition_search import ARMS, R, Decoder, outputs, search


def screen_job(job):
    return screen_domain(*job)


def sample(job):
    arm, table, seed, count, bank, inputs = job
    rng = np.random.default_rng(seed)
    decoder = Decoder(table)
    indices = np.random.default_rng(260604999).choice(len(inputs), 48, replace=False)
    subset = [inputs[i] for i in indices]
    labels = np.asarray([c["labels"] for c in bank])
    hits = {c["id"]: 0 for c in bank}
    start = time.monotonic()
    for offset in range(0, count, 1000):
        n = min(1000, count - offset)
        tapes = decoder.decode(rng.integers(R, size=(n, 32), dtype=np.int32))
        observed = outputs(tapes, subset)
        for c, label in zip(bank, labels):
            candidates = np.flatnonzero(np.all(observed == label[indices], axis=1))
            if len(candidates):
                exact = outputs(tapes[candidates], inputs)
                hits[c["id"]] += int(np.count_nonzero(np.all(exact == label, axis=1)))
    return dict(
        arm=arm,
        seed=seed,
        genotypes=count,
        hits=hits,
        seconds=time.monotonic() - start,
        table_hash=decoder.hash(),
    )


def sampling_summary(chunks, bank):
    result = {}
    for arm in ARMS:
        rows = [r for r in chunks if r["arm"] == arm]
        n = sum(r["genotypes"] for r in rows)
        seconds = sum(r["seconds"] for r in rows)
        result[arm] = dict(
            genotypes=n,
            cpu_seconds=seconds,
            genotypes_per_second=n / seconds if seconds else None,
            cells={},
        )
        for c in bank:
            hits = sum(r["hits"][c["id"]] for r in rows)
            low = float(beta.ppf(0.025, hits, n - hits + 1)) if hits else 0.0
            high = (
                float(beta.ppf(0.975, hits + 1, n - hits))
                if n and hits < n
                else (1.0 if n else None)
            )
            result[arm]["cells"][c["id"]] = dict(
                hits=hits,
                rate=hits / n if n else None,
                interval_95=[low if n else None, high],
                zero_hit_upper_95=float(-np.expm1(np.log(0.05) / n))
                if n and not hits
                else None,
            )
    return result


def run(args):
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    os.environ["RAYON_NUM_THREADS"] = "1"
    started = time.monotonic()
    deadline = started + args.deadline_seconds
    work_deadline = deadline - args.reserve_seconds
    # Save all candidates and complete tables before any outcome inspection.
    write_json(out, "roster.json", {d: roster(d) for d in DOMAINS})
    controls = frozen_controls()
    diagnostics, measurements = freeze_diagnostics(work_deadline)
    tables = {**controls, **diagnostics}
    write_json(
        out,
        "maps.json",
        dict(
            tables={k: v.tolist() for k, v in tables.items()},
            hashes={k: Decoder(v).hash() for k, v in tables.items()},
            marginal_measurements=measurements,
            frozen_before_screen=True,
            control_source="composition_2247_maps.json",
        ),
    )
    write_json(
        out,
        "config.json",
        dict(
            task="2026-10-06-0001",
            arguments=vars(args),
            domains=DOMAINS,
            base_seed=260601000,
            topup_seed=260602000,
            diagnostic_seed=260601000,
            sampling_seed=260604000,
            bootstrap_seed=260605000,
            population=256,
            cap=args.cap,
            training_cases=64,
            token_support=list(range(23)),
            mutation=0.03,
            crossover=0.7,
            allele_range=R,
            allele_length=32,
        ),
    )
    screens, rows, chunks, blocks = {}, [], [], []
    stage_b_complete = stage_c_complete = topups_complete = False
    pairing = dict(selected=None, eligible=[], failures=[])
    bank = []
    ctx = mp.get_context("spawn")
    # New process per domain: RSS from one domain never accumulates with another.
    for domain in DOMAINS:
        pool = ctx.Pool(1)

        def save_screen(row):
            screens[row["domain"]] = row
            write_json(out, "stage_a.json", screens)

        try:
            complete = run_jobs(
                pool,
                screen_job,
                [(domain, args.screen_depth, work_deadline)],
                work_deadline,
                save_screen,
            )
        except TimeoutError:
            complete = False
        finally:
            pool.terminate()
            pool.join()
        if not complete:
            break
    if len(screens) == 3:
        pairing = choose_pair(screens)
        write_json(out, "pairing.json", pairing)
        domain = stage_b_domain(screens, pairing["selected"])
        inputs = inputs_for(domain)
        bank = [c for c in screens[domain]["cells"] if c["retained"]]
        write_json(out, "bank.json", dict(domain=domain, cells=bank))
        # A smoke with a shallow screen is not an outcome analysis. Its broad
        # roster exercises condition and linear targets, which shallow aliases
        # have not excluded yet.
        if args.smoke:
            bank = [
                next(c for c in roster(domain) if c["shape"] == shape)
                for shape in SHAPES
            ]
            write_json(
                out, "bank.json", dict(domain=domain, cells=bank, smoke_only=True)
            )
        pool = ctx.Pool(args.workers)

        def save_search(row):
            rows.append(row)
            # Append each completed run immediately; final sorted JSON is separate.
            with (out / "search.jsonl").open("a") as f:
                f.write(json.dumps(row, allow_nan=False) + "\n")

        try:
            stage_b_complete = True
            for offset in range(0, args.seeds, 10):
                before = len(rows)
                tick = time.monotonic()
                seed_start = 260609000 if args.smoke else 260601000
                jobs = [
                    (c, arm, tables[arm], seed_start + i, args.cap, 256, inputs)
                    for i in range(offset, min(offset + 10, args.seeds))
                    for c in bank
                    for arm in ARMS
                ]
                stage_b_complete = run_jobs(
                    pool, search, jobs, work_deadline, save_search
                )
                elapsed = time.monotonic() - tick
                completed = len(rows) - before
                pair = pairing["selected"]
                pair_cells = [c for c in bank if pair and c["shape"] in pair["shapes"]]
                # Explicit allowance: worst case F top-up on every retained cell;
                # conditional C has four arms for 50 seeds on both shapes.
                per_run_wall = elapsed / completed if completed else None
                block = dict(
                    offset=offset,
                    requested=len(jobs),
                    completed=completed,
                    wall_seconds=elapsed,
                    mean_run_seconds=float(
                        np.mean([r["seconds"] for r in rows[before:]])
                    )
                    if completed
                    else None,
                    projected_baseline_remaining_seconds=(
                        args.seeds - min(offset + 10, args.seeds)
                    )
                    * len(bank)
                    * 4
                    * per_run_wall
                    if completed
                    else None,
                    projected_worst_f_topup_seconds=100 * len(bank) * per_run_wall
                    if completed
                    else None,
                    projected_conditional_c_seconds=50
                    * 4
                    * len(pair_cells)
                    * per_run_wall
                    if completed
                    else None,
                )
                blocks.append(block)
                write_json(out, "calibration_blocks.json", blocks)
                print("balanced block", block, flush=True)
                if not stage_b_complete:
                    break
            topups_complete = stage_b_complete
            if stage_b_complete and not args.smoke:
                requested = [
                    c
                    for c in bank
                    if 30
                    <= sum(
                        r["solved"]
                        for r in rows
                        if r["cell"] == c["id"] and r["arm"] == "F"
                    )
                    <= 39
                ]
                write_json(out, "topup_requests.json", [c["id"] for c in requested])
                for offset in range(0, 100, 10):
                    jobs = [
                        (c, "F", tables["F"], 260602000 + i, args.cap, 256, inputs)
                        for i in range(offset, offset + 10)
                        for c in requested
                    ]
                    topups_complete = run_jobs(
                        pool, search, jobs, work_deadline, save_search
                    )
                    if not topups_complete:
                        break
            pair = pairing["selected"]
            stage_c_complete = pair is None or args.smoke
            if stage_b_complete and topups_complete and pair and not args.smoke:
                pair_cells = [c for c in bank if c["shape"] in pair["shapes"]]
                arms = [s + suffix for s in pair["shapes"] for suffix in ("", "-marg")]
                stage_c_complete = True
                for offset in range(0, 50, 10):
                    jobs = [
                        (c, arm, tables[arm], 260601000 + i, args.cap, 256, inputs)
                        for i in range(offset, offset + 10)
                        for c in pair_cells
                        for arm in arms
                    ]
                    stage_c_complete = run_jobs(
                        pool, search, jobs, work_deadline, save_search
                    )
                    if not stage_c_complete:
                        break
            # Sampling is secondary, with bounded chunks and balanced arm blocks.
            # Deadline may cut an in-flight block: only completed chunks count.
            if stage_b_complete and topups_complete and stage_c_complete:

                def save_chunk(row):
                    chunks.append(row)
                    with (out / "sampling.jsonl").open("a") as f:
                        f.write(json.dumps(row) + "\n")

                sample_count = 10000 if args.smoke else args.sampling_genotypes
                for offset in range(0, sample_count, args.sampling_chunk):
                    n = min(args.sampling_chunk, sample_count - offset)
                    index = offset // args.sampling_chunk
                    jobs = [
                        (
                            arm,
                            tables[arm],
                            260604000 + j * 10000 + index,
                            n,
                            bank,
                            inputs,
                        )
                        for j, arm in enumerate(ARMS)
                    ]
                    if not run_jobs(pool, sample, jobs, work_deadline, save_chunk):
                        break
        finally:
            pool.terminate()
            pool.join()
    write_json(
        out, "search.json", sorted(rows, key=lambda r: (r["cell"], r["arm"], r["seed"]))
    )
    sampling = sampling_summary(chunks, bank)
    write_json(out, "sampling.json", sampling)
    marginal_seconds = max(
        v["seconds"] + v["check_seconds"] for v in measurements.values()
    )
    result = report(
        screens,
        pairing,
        rows,
        stage_b_complete and not args.smoke,
        stage_c_complete,
        topups_complete,
        marginal_seconds,
    )
    result.update(
        wall_seconds=time.monotonic() - started,
        smoke_only=args.smoke,
        sampling=sampling,
        calibration_blocks=blocks,
    )
    if args.smoke:
        result["outcome"] = "smoke_only"
    write_json(out, "result.json", result)
    plots(out, rows)
    (out / "summary.md").write_text(
        f"Outcome: {result['outcome']}\n\nSemantic verdict: {result['semantic_verdict']}\n\n"
        f"{result['semantic_scope']}\n\n"
        f"A complete: {result['stage_a_complete']}; B: {stage_b_complete}; "
        f"top-ups: {topups_complete}; C: {stage_c_complete}.\n\n"
        "See result.json for censoring, paired contrasts and conditional cost scenarios; "
        "stage_a.json for canonical verification, alias witnesses and duplicates; "
        "pairing.json for split coverage and primitive balance. No transfer was measured.\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--cap", type=int, default=524288)
    parser.add_argument("--seeds", type=int, default=50)
    parser.add_argument("--screen-depth", type=int, default=9)
    parser.add_argument("--deadline-seconds", type=int, default=7800)
    parser.add_argument("--reserve-seconds", type=int, default=180)
    parser.add_argument("--sampling-genotypes", type=int, default=100000000)
    parser.add_argument("--sampling-chunk", type=int, default=100000)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if (
        not 1 <= args.screen_depth <= 9
        or args.cap < 256
        or args.cap % 256
        or args.workers < 1
    ):
        parser.error("invalid depth, workers or population-aligned cap")
    if not args.smoke and (
        args.seeds != 50 or args.cap != 524288 or args.screen_depth != 9
    ):
        parser.error("full run must use approved depth 9, 50 seeds, cap 524288")
    run(args)


if __name__ == "__main__":
    main()
