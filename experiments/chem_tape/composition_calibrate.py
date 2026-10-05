"""Stage-0 calibration, also used as the researcher small-scale smoke test."""

from __future__ import annotations

import argparse
import multiprocessing as mp
import json
import resource
import sys
import os
import time
from pathlib import Path

import numpy as np
from scipy.stats import chisquare

from experiments.chem_tape.composition_bank import (
    INPUTS,
    TOKENS,
    SemanticMachine,
    cells,
    screen,
)
from experiments.chem_tape.composition_search import (
    ARMS,
    R,
    Decoder,
    base_tables,
    cumulative,
    outputs,
    search,
)


def check_deadline(deadline):
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError("stage-0 deadline reached")


def token_counts(decoder, seed, genotypes, deadline=None):
    rng = np.random.default_rng(seed)
    count = np.zeros(23, dtype=np.int64)
    start = time.monotonic()
    for n in range(0, genotypes, 10000):
        check_deadline(deadline)
        alleles = rng.integers(R, size=(min(10000, genotypes - n), 32), dtype=np.int32)
        count += np.bincount(decoder.decode(alleles).ravel(), minlength=23)
    return count, time.monotonic() - start


def freeze_maps(out, deadline=None):
    tables = base_tables()
    d = Decoder(tables["G"])
    counts, seconds = token_counts(d, 224701, 312500, deadline)
    tables["G-marg"] = np.tile(cumulative(counts), (24, 1))
    measured, check_seconds = token_counts(
        Decoder(tables["G-marg"]), 224702, 312500, deadline
    )
    p, q = counts / counts.sum(), measured / measured.sum()
    tolerance = np.maximum(0.02 * p, 0.0005)
    assert np.all(np.abs(p - q) <= tolerance)
    uniform, uniform_seconds = token_counts(
        Decoder(tables["U"]), 224700, 31250, deadline
    )
    chi = chisquare(uniform)
    assert chi.pvalue > 1e-6, "uniform decoder diagnostic failed"
    record = dict(
        tables={k: v.tolist() for k, v in tables.items()},
        hashes={k: Decoder(v).hash() for k, v in tables.items()},
        marginal_counts=counts.tolist(),
        marginal_check_counts=measured.tolist(),
        marginal_measurement_genotypes=312500,
        marginal_seconds=seconds,
        marginal_check_seconds=check_seconds,
        uniform_chi_square=float(chi.statistic),
        uniform_pvalue=float(chi.pvalue),
        uniform_seconds=uniform_seconds,
        freeze_precedes_search=True,
    )
    (out / "maps.json").write_text(json.dumps(record, indent=2) + "\n")
    return tables, record


def select_bank(alias):
    all_cells = cells()
    chosen = []
    for cid in dict.fromkeys(c["id"] for c in all_cells):
        rows = [row for row in alias["oriented_cells"] if row["id"] == cid]
        best = min(
            rows,
            key=lambda row: (
                row["best_shorter_matches"],
                ("S", "M", "m").index(row["x"]),
            ),
        )
        cell = next(c for c in all_cells if c["id"] == cid and c["x"] == best["x"])
        chosen.append({**cell, "rejects": best["rejects"], "screen": best})
    # Duplicate label vectors reject every affected cell.
    for c in chosen:
        c["duplicate_ids"] = [
            other["id"]
            for other in chosen
            if other["id"] != c["id"] and np.array_equal(c["labels"], other["labels"])
        ]
        c["rejects"] |= bool(c["duplicate_ids"])
    return chosen


def sample_speed(job):
    arm, table, seed, count = job
    d = Decoder(table)
    rng = np.random.default_rng(seed)
    idx = np.random.default_rng(224704).choice(625, 48, replace=False)
    inputs = [INPUTS[i] for i in idx]
    labels = np.array([c["labels"][idx] for c in cells()])
    start = time.monotonic()
    for offset in range(0, count, 1000):
        tapes = d.decode(
            rng.integers(R, size=(min(1000, count - offset), 32), dtype=np.int32)
        )
        result = outputs(tapes, inputs)
        # Include screening and exact checks in the sampling calibration.
        for target in labels:
            candidates = np.flatnonzero(np.all(result == target, axis=1))
            if len(candidates):
                outputs(tapes[candidates], INPUTS)
    seconds = time.monotonic() - start
    return dict(
        arm=arm, genotypes=count, seconds=seconds, genotypes_per_second=count / seconds
    )


def validate_execution(tables, out, count=100000, deadline=None):
    from _folding_rust import rust_chem_execute_alleles

    start = time.monotonic()
    rng = np.random.default_rng(224700)
    tested = 0
    for arm in ARMS:
        d = Decoder(tables[arm])
        for offset in range(0, count // 4, 500):
            check_deadline(deadline)
            n = min(500, count // 4 - offset)
            alleles = rng.integers(R, size=(n, 32), dtype=np.int32)
            tapes = d.decode(alleles)
            assert np.array_equal(tapes, d.decode(alleles.copy()))
            direct = outputs(tapes, INPUTS)
            latent = np.array(
                rust_chem_execute_alleles(
                    alleles.tolist(), tables[arm].tolist(), INPUTS
                )
            ).reshape(n, 625)
            assert np.array_equal(direct, latent)
            tested += n
    result = dict(
        genotypes=tested,
        input_executions=tested * 625,
        all_arms=list(ARMS),
        seconds=time.monotonic() - start,
        identical=True,
    )
    (out / "decoder_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def enumerate_slice(count=1000000, deadline=None):
    start = time.monotonic()
    rng = np.random.default_rng(224703)
    programs = rng.choice(TOKENS, size=(count, 6))
    m = SemanticMachine()
    states = set()
    for i, tape in enumerate(programs):
        if i % 10000 == 0:
            check_deadline(deadline)
        state = ()
        for token in tape:
            state = m.apply(state, int(token))
        states.add(state)
    return dict(
        raw_programs=count,
        depth=6,
        uniform_rank_slice=True,
        distinct_full_typed_states=len(states),
        distinct_value_vectors=len(m.values),
        seconds=time.monotonic() - start,
        peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        / (1024 * 1024 if sys.platform == "darwin" else 1024),
    )


def calibrate(
    out,
    workers=8,
    cap=524288,
    validation_count=100000,
    slice_count=1000000,
    deadline=None,
):
    started = time.monotonic()
    deadline = min(started + 900, deadline) if deadline is not None else started + 900
    tables, maps = freeze_maps(out, deadline)
    validation = validate_execution(tables, out, validation_count, deadline)
    enumeration = enumerate_slice(slice_count, deadline)
    alias = screen(6)
    (out / "stage_a.json").write_text(json.dumps(alias, indent=2) + "\n")
    bank = select_bank(alias)
    jobs = [
        (c, "U", tables["U"], 224705 + i * 2 + j, cap, 256)
        for i, c in enumerate(bank)
        for j in range(2)
    ]
    results = []
    pool = mp.Pool(workers)
    try:
        iterator = pool.imap_unordered(search, jobs, chunksize=1)
        while len(results) < len(jobs):
            check_deadline(deadline)
            try:
                result = iterator.next(timeout=min(1, deadline - time.monotonic()))
            except mp.TimeoutError:
                continue
            results.append(result)
            print(
                json.dumps(
                    {
                        k: result[k]
                        for k in ("cell", "seed", "solved", "evaluations", "seconds")
                    }
                ),
                flush=True,
            )
            (out / "calibration_search.json").write_text(
                json.dumps(results, indent=2) + "\n"
            )
        sampling_start = time.monotonic()
        future = pool.map_async(
            sample_speed,
            [
                (arm, tables[arm], 224704 + i * 2 + j, 10000)
                for i, arm in enumerate(ARMS)
                for j in range(2)
            ],
        )
        check_deadline(deadline)
        try:
            speeds = future.get(timeout=deadline - time.monotonic())
        except mp.TimeoutError as e:
            raise TimeoutError("stage-0 sampling deadline reached") from e
        sampling_seconds = time.monotonic() - sampling_start
    finally:
        pool.terminate()
        pool.join()
    # Contention-aware CPU-to-wall throughput from the whole block rather
    # than a serial speed divided blindly by worker count.
    elapsed = time.monotonic() - started
    mean = float(np.mean([r["seconds"] for r in results]))
    retained = sum(not c["rejects"] for c in bank)
    search_projection = retained * 4 * 50 * mean / workers
    record = dict(
        workers=workers,
        cap=cap,
        retained=retained,
        decoder_validation=validation,
        enumeration_slice=enumeration,
        mean_censored_inclusive_seconds=mean,
        stage_b_projected_seconds=search_projection,
        sampling_speeds=speeds,
        sampling_parallel_wall_seconds=sampling_seconds,
        stage_0_seconds=elapsed,
        searches=results,
    )
    (out / "calibration.json").write_text(json.dumps(record, indent=2) + "\n")
    return tables, bank, record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cap", type=int, default=524288)
    ap.add_argument("--validation-count", type=int, default=100000)
    ap.add_argument("--slice-count", type=int, default=1000000)
    args = ap.parse_args()
    out = args.output or Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    calibrate(out, args.workers, args.cap, args.validation_count, args.slice_count)


if __name__ == "__main__":
    main()
