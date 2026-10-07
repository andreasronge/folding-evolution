"""2331 frozen 2×2 initialization intervention, validation-gated and seed-major."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np
from scipy.stats import chisquare

from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder, search
from experiments.chem_tape.crossed_holdout_run import (
    SOURCE,
    SOURCE_COMMIT,
    SOURCE_HASHES,
    frozen_source,
)
from experiments.chem_tape.crossed_learning_run import (
    BANK_SHA,
    DEFAULT_BANK,
    G4_HASH,
    HOLDOUTS,
    load_bank,
)
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.initialization_report import (
    law_report,
    make_report,
    save_report,
)

REFERENCE = (
    Path(__file__).with_name("data") / "initialization_2331" / "reference_2229.jsonl.gz"
)
REFERENCE_SHA = "44bafebde6f4ae1da140711fab406ce3de6a98de246e277715c887747c08de24"
REFERENCE_COMMIT = "33fcee2291d6fb2d6d8dbae43e927a141273f161"
MAIN_SEEDS = list(range(2331000, 2331400))
LAW_SEEDS = MAIN_SEEDS[:100]
PROBE_SEEDS = list(range(9000000, 9000025))
ARMS = ("MM", "MG", "GM")


def initialized_search(job):
    payload, tid, family = job
    row = search(payload)
    row.update(map=tid, family=family)
    return row


def encoding_checks(maps, count=10000, law_count=1000000):
    """Source tapes come from uniform alleles, never uniform tokens."""
    rng = np.random.default_rng(2331500)
    decoders = {tid: Decoder(table) for tid, table in maps.items()}
    for tid, d in decoders.items():
        if (d.allele_range, d.n_tokens) != (24000, 24) or np.min(
            np.diff(d.table, prepend=0, axis=1)
        ) < 250:
            raise ValueError(f"unexpected interval size/range: {tid}")
    round_trips = []
    for tid in maps:
        if tid == "G4":
            continue
        for src, dst in (("G4", tid), (tid, "G4")):
            tapes = decoders[src].decode(
                rng.integers(24000, size=(count, 32), dtype=np.int32)
            )
            encoded = decoders[dst].encode(tapes, rng)
            passed = bool(np.array_equal(decoders[dst].decode(encoded), tapes))
            round_trips.append(
                dict(source=src, destination=dst, tapes=count, passed=passed)
            )
    laws = []
    for tid in (("G4", "BE1", "PA1") if law_count else ()):
        d = decoders[tid]
        n_tapes = (law_count + 31) // 32
        tapes = d.decode(rng.integers(24000, size=(n_tapes, 32), dtype=np.int32))
        encoded = d.encode(tapes, rng)
        if not np.array_equal(d.decode(encoded), tapes):
            raise AssertionError("self round trip failed")
        histogram = np.bincount(encoded.ravel()[:law_count] // 100, minlength=240)
        statistic, p = chisquare(histogram)
        laws.append(
            dict(
                table=tid,
                alleles=law_count,
                bins=240,
                histogram=histogram.tolist(),
                chi_square=float(statistic),
                p=float(p),
                failure_threshold=0.05 / 3,
                passed=bool(p >= 0.05 / 3),
            )
        )
    return dict(
        passed=all(r["passed"] for r in round_trips + laws),
        round_trips=round_trips,
        marginal_law=laws,
        conditional_interval_bounds_checked=True,
        conditional_law="Self-decoded tape probabilities times inverse interval probabilities cancel to the independent uniform allele prior.",
    )


class Runner:
    def __init__(self, args):
        self.args = args
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds
        self.work_deadline = self.deadline - 180
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if any(
            (self.out / n).exists()
            for n in ("config.json", "search.jsonl", "result.json")
        ):
            raise ValueError("Use a fresh RUN_DIR")
        trajectories, g4, _, validation = frozen_source(args.source)
        self.maps = {
            "G4": g4,
            **{tid: np.asarray(tr["table"]) for tid, tr in trajectories.items()},
        }
        self.map_ids = list(trajectories)
        bank, _ = load_bank(args.bank)
        by_id = {c["id"]: c for c in bank["cells"]}
        self.cells = {
            cid: {"id": cid, "labels": by_id[cid]["labels"]}
            for cid in sum(HOLDOUTS.values(), [])
        }
        self.inputs = inputs_for("D1331")
        self.cap = 8192 if args.smoke else 524288
        self.seeds = (
            PROBE_SEEDS
            if args.probe
            else PROBE_SEEDS[-2:]
            if args.smoke
            else MAIN_SEEDS
        )
        self.rows, self.complete_seeds = [], []
        self.validation = dict(
            passed=False,
            source_hashes_verified=True,
            map_hashes_verified=True,
            bank_labels_verified=True,
            no_learning=True,
            source_training_rows=validation,
            reproduction=None,
            encoding=None,
            pairing_blocks=0,
            search_law=None,
        )
        self.stop_reason = None
        self.config = dict(
            task="2026-10-06-2331",
            arguments=vars(args),
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            source_commit=SOURCE_COMMIT,
            source_sha256=SOURCE_HASHES,
            reference_commit=REFERENCE_COMMIT,
            reference_sha256=REFERENCE_SHA,
            bank_sha256=BANK_SHA,
            g4_hash=G4_HASH,
            maps=self.map_ids,
            map_hashes={tid: Decoder(table).hash() for tid, table in self.maps.items()},
            cells=list(self.cells),
            alphabet=ALPHABET,
            domain="D1331",
            population=256,
            length=32,
            mutation=0.03,
            crossover=0.7,
            cap=self.cap,
            training_cases=64,
            exact_cases=1331,
            allele_range=24000,
            seeds=self.seeds,
            law_seeds=LAW_SEEDS,
            probe_seeds=PROBE_SEEDS,
            smoke_only=args.smoke,
            probe_only=args.probe,
            validation_only=args.validate_only,
            learning_permitted=False,
            original_arms=["GG", "MM"],
            reencoded_arms=["MG", "GM", "MMr"],
            streams=dict(
                cases="[seed,0]",
                initial="[seed,1]",
                variation="[seed,2]",
                reencoding="[seed,3]",
                selection="seed+100000000",
            ),
            expected_main_searches=73200,
            expected_search_law_searches=6000,
            expected_reproduction_searches=630,
            expected_probe_searches=900,
            minimum_complete_seeds=200,
            scheduling="One complete seed across all cells/maps/arms before the next seed",
            weighting="Equal cells, equal BE/PA families; equal maps within family",
        )
        write_json(self.out, "config.json", self.config)
        write_json(self.out, "trajectories.json", trajectories)
        write_json(self.out, "bank.json", bank)
        (self.out / "search.jsonl").touch()
        (self.out / "reproduction.jsonl").touch()
        self.persist_validation()

    def persist_validation(self):
        write_json(self.out, "validation.json", self.validation)

    def job(self, tid, arm, cid, seed, cap=None):
        if set(self.cells[cid]) != {"id", "labels"}:
            raise ValueError("solver information in search payload")
        src = "G4" if arm in ("GG", "GM") else tid
        dst = "G4" if arm in ("GG", "MG") else tid
        payload = (
            self.cells[cid],
            arm,
            self.maps[dst],
            seed,
            self.cap if cap is None else cap,
            256,
            self.inputs,
            ALPHABET,
            dict(source_table=self.maps[src], reencode=arm in ("MG", "GM", "MMr")),
        )
        return payload, tid, tid[:2] if tid != "G4" else "G"

    def block_jobs(self, seed):
        return [self.job("G4", "GG", cid, seed) for cid in self.cells] + [
            self.job(tid, arm, cid, seed)
            for tid in self.map_ids
            for cid in self.cells
            for arm in (*ARMS, "MMr")
            if arm != "MMr" or seed in LAW_SEEDS or self.args.smoke
        ]

    def check_block(self, rows, seed):
        jobs = self.block_jobs(seed)
        expected = {
            (tid, payload[1], payload[0]["id"], seed) for payload, tid, _ in jobs
        }
        lookup = {(r["map"], r["arm"], r["cell"], r["seed"]): r for r in rows}
        if len(lookup) != len(rows) or lookup.keys() != expected:
            raise ValueError("incomplete/duplicate/unexpected seed block")
        cases = (
            np.random.default_rng([seed, 0]).choice(1331, 64, replace=False).tolist()
        )
        initial = np.random.default_rng([seed, 1]).integers(
            24000, size=(256, 32), dtype=np.int32
        )
        token_hashes = {
            tid: hashlib.sha256(Decoder(table).decode(initial).tobytes()).hexdigest()
            for tid, table in self.maps.items()
        }
        for row in rows:
            tid, arm, cid = row["map"], row["arm"], row["cell"]
            src = "G4" if arm in ("GG", "GM") else tid
            dst = "G4" if arm in ("GG", "MG") else tid
            if (
                row["table_hash"] != self.config["map_hashes"][dst]
                or row["initial_source_hash"] != self.config["map_hashes"][src]
                or row["initial_tokens_hash"] != token_hashes[src]
                or row["initial_reencoded"] != (arm in ("MG", "GM", "MMr"))
                or row["training_indices"] != cases
                or row["cap"] != self.cap
                or row["pop_size"] != 256
                or row["family"] != (tid[:2] if tid != "G4" else "G")
                or not isinstance(row["solved"], bool)
                or not isinstance(row["evaluations"], int)
                or not 0 < row["evaluations"] <= self.cap
                or row["evaluations"] % 256
                or (not row["solved"] and row["evaluations"] != self.cap)
            ):
                raise ValueError(f"invalid paired search row {tid}/{arm}/{cid}/{seed}")
        for tid in self.map_ids:
            for cid in self.cells:
                if (
                    lookup[(tid, "MG", cid, seed)]["initial_tokens_hash"]
                    != lookup[(tid, "MM", cid, seed)]["initial_tokens_hash"]
                ):
                    raise AssertionError("MG != MM initial programs")
                if (
                    lookup[(tid, "GM", cid, seed)]["initial_tokens_hash"]
                    != lookup[("G4", "GG", cid, seed)]["initial_tokens_hash"]
                ):
                    raise AssertionError("GM != GG initial programs")

    def reproduction(self, pool):
        raw = gzip.decompress(REFERENCE.read_bytes())
        if hashlib.sha256(raw).hexdigest() != REFERENCE_SHA:
            raise ValueError("historical reference SHA256 mismatch")
        references = [json.loads(line) for line in raw.splitlines()]
        if self.args.smoke:
            references = [r for r in references if r["seed"] == 2229002]
        expected = {(r["arm"], r["cell"], r["seed"]): r for r in references}
        jobs = []
        for ref in references:
            payload = (
                self.cells[ref["cell"]],
                ref["arm"],
                self.maps[ref["arm"]],
                ref["seed"],
                524288,
                256,
                self.inputs,
                ALPHABET,
                dict(source_table=self.maps[ref["arm"]], reencode=False),
            )
            jobs.append(payload)
        checked, errors = [], []
        with (self.out / "reproduction.jsonl").open("a", buffering=1) as stream:

            def record(row):
                ref = expected[(row["arm"], row["cell"], row["seed"])]
                changed = [key for key, value in ref.items() if row[key] != value]
                if changed:
                    errors.append(
                        dict(
                            arm=row["arm"],
                            cell=row["cell"],
                            seed=row["seed"],
                            fields=changed,
                        )
                    )
                checked.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")

            complete = run_jobs(pool, search, jobs, self.work_deadline, record)
        result = dict(
            passed=complete and not errors,
            rows=len(checked),
            expected=len(jobs),
            errors=errors,
            reference_sha256=REFERENCE_SHA,
            fields=list(references[0]),
            seconds=sum(r["seconds"] for r in checked),
        )
        self.validation["reproduction"] = result
        self.persist_validation()
        if not result["passed"]:
            raise ValueError("historical reproduction failed or timed out")

    def run_probe(self, pool):
        """Repeat the proposal's runtime calibration without choosing maps or effects."""
        jobs = [
            self.job(tid, arm, cid, seed, 524288)
            for tid in ("BE1", "PA4", "PA9")
            for seed in PROBE_SEEDS
            for cid in self.cells
            for arm in ("GG", "MM", "MG", "GM")
        ]
        rows = []
        start = time.monotonic()
        with (self.out / "probe.jsonl").open("w", buffering=1) as stream:

            def record(row):
                rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")

            complete = run_jobs(
                pool, initialized_search, jobs, self.work_deadline, record
            )
        timing = dict(
            complete=complete,
            rows=len(rows),
            wall_seconds=time.monotonic() - start,
            sum_search_seconds=sum(r["seconds"] for r in rows),
            groups={},
        )
        for tid in ("BE1", "PA4", "PA9"):
            timing["groups"][tid] = {}
            for arm in ("GG", "MM", "MG", "GM"):
                rs = [r for r in rows if r["map"] == tid and r["arm"] == arm]
                timing["groups"][tid][arm] = dict(
                    n=len(rs),
                    solved=sum(r["solved"] for r in rs),
                    mean_seconds=float(np.mean([r["seconds"] for r in rs]))
                    if rs
                    else None,
                )
        write_json(self.out, "probe.json", timing)
        print(json.dumps(timing), flush=True)
        return timing

    def run(self):
        pool = mp.get_context("spawn").Pool(self.args.workers)
        diagnostic = self.args.smoke or self.args.probe or self.args.validate_only
        probe = None
        try:
            if self.args.probe:
                probe = self.run_probe(pool)
            else:
                self.validation["encoding"] = encoding_checks(self.maps)
                self.persist_validation()
                if not self.validation["encoding"]["passed"]:
                    raise ValueError("round-trip/allele-law validation failed")
                self.reproduction(pool)
                if self.args.validate_only:
                    self.validation["passed"] = True
                else:
                    with (self.out / "search.jsonl").open("a", buffering=1) as stream:
                        for seed in self.seeds:
                            block = []

                            def record(row):
                                block.append(row)
                                self.rows.append(row)
                                stream.write(json.dumps(row, allow_nan=False) + "\n")

                            complete = run_jobs(
                                pool,
                                initialized_search,
                                self.block_jobs(seed),
                                self.work_deadline,
                                record,
                            )
                            if not complete:
                                self.stop_reason = "internal deadline; partial seed excluded, complete seed blocks retained"
                                break
                            self.check_block(block, seed)
                            self.complete_seeds.append(seed)
                            self.validation["pairing_blocks"] += 1
                            if seed == LAW_SEEDS[-1]:
                                self.validation["search_law"] = law_report(
                                    self.rows, self.map_ids, list(self.cells), LAW_SEEDS
                                )
                                self.persist_validation()
                                if not self.validation["search_law"]["passed"]:
                                    raise ValueError(
                                        "MMr/MM 99% search-law interval excludes 1"
                                    )
                            print(
                                json.dumps(
                                    dict(
                                        stage="main",
                                        complete_seeds=len(self.complete_seeds),
                                        rows=len(self.rows),
                                        elapsed_seconds=time.monotonic() - self.started,
                                    )
                                ),
                                flush=True,
                            )
                    if self.args.smoke:
                        self.validation["search_law"] = dict(
                            passed=False,
                            deferred=True,
                            reason="Smoke has two excluded seeds; full 100-seed check remains queued",
                        )
                        self.validation["smoke_pairing_passed"] = len(
                            self.complete_seeds
                        ) == len(self.seeds)
                    self.validation["passed"] = bool(
                        self.validation["encoding"]["passed"]
                        and self.validation["reproduction"]["passed"]
                        and self.validation["search_law"]
                        and self.validation["search_law"]["passed"]
                    )
        except Exception as error:
            self.stop_reason = f"{type(error).__name__}: {error}"
            self.validation["passed"] = False
        finally:
            pool.terminate()
            pool.join()
        self.persist_validation()
        retained = [r for r in self.rows if r["seed"] in self.complete_seeds]
        report = make_report(
            retained,
            self.map_ids,
            list(self.cells),
            self.complete_seeds,
            self.validation,
            diagnostic,
            replicates=1000 if diagnostic else 20000,
        )
        report.update(
            stop_reason=self.stop_reason,
            runtime=dict(
                wall_seconds=time.monotonic() - self.started,
                rows=len(self.rows),
                included_rows=len(retained),
                excluded_partial_rows=len(self.rows) - len(retained),
                sum_search_seconds=sum(r["seconds"] for r in self.rows),
            ),
            probe=probe,
        )
        write_json(self.out, "result.json", report)
        save_report(self.out, report, retained, list(self.cells))
        print(
            json.dumps(
                dict(
                    outcome=report["outcome"],
                    n_seeds=len(self.complete_seeds),
                    validation_passed=self.validation["passed"],
                    stop_reason=self.stop_reason,
                )
            ),
            flush=True,
        )
        return (
            1
            if self.stop_reason and not self.stop_reason.startswith("internal deadline")
            else 0
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(SOURCE))
    parser.add_argument("--bank", default=str(DEFAULT_BANK))
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=16200)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--smoke", action="store_true")
    modes.add_argument("--probe", action="store_true")
    modes.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 180:
        parser.error(
            "workers must be positive and deadline must exceed the reporting reserve"
        )
    raise SystemExit(Runner(args).run())


if __name__ == "__main__":
    main()
