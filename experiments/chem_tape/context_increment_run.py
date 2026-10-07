"""2129: token fits on the exact saved 1924 crossing, with replay and timing gates."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.crossed_learning_run import (
    TRAINING,
    HOLDOUTS,
    DEFAULT_BANK,
    BANK_SHA,
    load_bank,
)
from experiments.chem_tape.solver_corpus_fit import BASE, seed_for, validate_table
from experiments.chem_tape.solver_corpus_run import (
    Runner as CorpusRunner,
    scientific_fields,
)

DATA = Path(__file__).with_name("data") / "context_increment_2129"
PROVENANCE_SHA = "ff532999ff43f0b7d6cdbb1cdd1482ce20e860b08430abd36ee96594ec9695c6"
WORK_CUTOFF = "2026-10-07T20:20:38+00:00"
HISTORICAL_T1 = {"training": 1.042, "holdout": 0.946}


def row_key(row):
    return tuple(row[k] for k in ("phase", "family", "corpus", "cell", "arm", "seed"))


def expected_rows(corpora, roster, phase, arms, n):
    for tid in roster:
        tr = corpora[tid]
        cells = (
            TRAINING[tr["family"]]
            if phase == "training"
            else sum(HOLDOUTS.values(), [])
        )
        for c, cid in enumerate(cells):
            for s in range(n):
                seed = seed_for(
                    11 if phase == "training" else 12,
                    tr["family"],
                    tr["index"],
                    c,
                    s,
                    BASE,
                )
                for arm in arms:
                    yield (phase, tr["family"], tid, cid, arm, seed)


def validate_rows(rows, corpora, roster, phase, arms, n):
    expected = set(expected_rows(corpora, roster, phase, arms, n))
    selected = [
        r
        for r in rows
        if r["phase"] == phase and r["corpus"] in roster and r["arm"] in arms
    ]
    by = {row_key(r): r for r in selected}
    if len(by) != len(selected) or set(by) != expected:
        raise ValueError("incomplete/duplicate/incorrect fixed row roster")
    for key, row in by.items():
        indices = (
            np.random.default_rng([row["seed"], 0])
            .choice(1331, 64, replace=False)
            .tolist()
        )
        if (
            row["training_indices"] != indices
            or row["cap"] != 524288
            or row["pop_size"] != 256
            or row["table_hash"] != corpora[row["corpus"]]["hashes"][row["arm"]]
            or row["initial_source_hash"] != row["table_hash"]
            or row["initial_reencoded"]
            or (not row["solved"] and row["evaluations"] != 524288)
        ):
            raise ValueError("row seed/index/hash/budget mismatch")
    return by


def frozen_sources():
    raw = (DATA / "provenance.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != PROVENANCE_SHA:
        raise ValueError("provenance SHA mismatch")
    provenance = json.loads(raw)
    artifacts = {}
    for name, digest in provenance["artifact_hashes"].items():
        raw = (DATA / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError(f"{name} SHA mismatch")
        artifacts[name] = raw
    corpora = json.loads(artifacts["tables.json"])
    roster = [f"{f}{k + 1}" for f in TRAINING for k in range(16)]
    if set(corpora) != set(roster):
        raise ValueError("lineage roster mismatch")
    for tid, tr in corpora.items():
        if tid != f"{tr['family']}{tr['index'] + 1}" or set(tr["tables"]) != {
            "T1",
            "T2",
            "C1",
            "C2",
        }:
            raise ValueError("lineage identity mismatch")
        for arm, table in tr["tables"].items():
            if validate_table(table) != tr["hashes"][arm]:
                raise ValueError("table hash mismatch")
    for label, config in provenance["source_configs"].items():
        if (
            config["bank_sha256"] != BANK_SHA
            or config["training"] != TRAINING
            or config["holdouts"] != HOLDOUTS
            or config["seed_base"] != BASE
            or config["fresh_n"] != 32
            or config["cap"] != 524288
            or config["population"] != 256
            or config["length"] != 32
            or config["training_cases"] != 64
            or config["smoke_only"]
        ):
            raise ValueError(f"{label} source configuration mismatch")
    rows = [
        json.loads(line)
        for line in gzip.decompress(artifacts["context_rows.jsonl.gz"]).splitlines()
    ]
    if len(rows) != 16384 or len(rows) != provenance["context_row_count"]:
        raise ValueError("saved row count mismatch")
    for phase in ("training", "holdout"):
        validate_rows(rows, corpora, roster, phase, ("C1", "C2"), 32)
    return corpora, rows, provenance


def timing_admission(remaining, projection):
    return remaining > 1.25 * projection


class Runner(CorpusRunner):
    def __init__(self, args):
        self.args = args
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("use a fresh RUN_DIR")
        self.started = time.monotonic()
        now = dt.datetime.now(dt.timezone.utc)
        available = (
            args.deadline_seconds - 120
            if args.smoke
            else min(
                args.deadline_seconds - 120,
                (dt.datetime.fromisoformat(WORK_CUTOFF) - now).total_seconds(),
            )
        )
        self.work_deadline = self.started + max(0, available)
        self.bank, self.cells = load_bank(DEFAULT_BANK)
        self.hold_cells = {
            c["id"]: {"id": c["id"], "labels": c["labels"]}
            for c in self.bank["cells"]
            if c["id"] in sum(HOLDOUTS.values(), [])
        }
        self.inputs = inputs_for("D1331")
        self.corpora, self.saved_rows, provenance = frozen_sources()
        self.roster = [
            f"{f}{k + 1}" for f in TRAINING for k in range(1 if args.smoke else 16)
        ]
        self.fresh_n = 2 if args.smoke else 32
        if args.smoke:
            keys = set(
                expected_rows(
                    self.corpora, self.roster, "training", ("C1", "C2"), self.fresh_n
                )
            )
            keys.update(
                expected_rows(
                    self.corpora, self.roster, "holdout", ("C1", "C2"), self.fresh_n
                )
            )
            self.saved_rows = [r for r in self.saved_rows if row_key(r) in keys]
        self.cap = 524288
        self.rows, self.timings = [], {}
        self.validation = dict(
            passed=False,
            table_checks=128,
            saved_roster_checks=16384,
            pairing_checks=0,
            solver_verifications=0,
        )
        self.complete = dict(replay=False, timing=False, training=False, holdout=False)
        self.admission = {}
        self.stop_reason = None
        self.config = dict(
            task="2026-10-07-2129",
            arguments=vars(args),
            smoke_only=args.smoke,
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            submitted_at=now.isoformat(),
            work_cutoff=WORK_CUTOFF,
            reporting_reserve_seconds=120,
            autonomous_deadline="2026-10-07T20:25:38+00:00",
            available_work_seconds=max(0, available),
            provenance_sha256=PROVENANCE_SHA,
            source=provenance,
            bank_sha256=BANK_SHA,
            cap=self.cap,
            population=256,
            length=32,
            training_cases=64,
            seed_base=BASE,
            phases=dict(training=11, holdout=12),
            training=TRAINING,
            holdouts=HOLDOUTS,
            roster=self.roster,
            fresh_n=self.fresh_n,
            timing_seeds=[0],
            timing_cells="all own training cells",
            workers=args.workers,
            unsolved_cost="2*cap",
            safety_multiplier=1.25,
        )
        write_json(self.out, "config.json", self.config)
        write_json(self.out, "tables.json", self.corpora)

    def evaluation_jobs(self, phase="training", timing=False):
        jobs = []
        for key in expected_rows(
            self.corpora, self.roster, phase, ("T1", "T2"), self.fresh_n
        ):
            _, family, tid, cid, arm, seed = key
            tr = self.corpora[tid]
            timing_key = (
                phase == "training"
                and arm == "T2"
                and seed
                == seed_for(
                    11, family, tr["index"], TRAINING[family].index(cid), 0, BASE
                )
            )
            if phase == "training" and timing_key != timing:
                continue
            jobs.append(
                self.envelope(phase, family, tid, cid, arm, tr["tables"][arm], seed)
            )
        return jobs

    def replay_sources(self):
        refs = [
            r
            for r in self.saved_rows
            if r["corpus"] in self.roster
            and r["phase"] == "training"
            and r["cell"] == TRAINING[r["family"]][0]
            and r["seed"]
            == seed_for(11, r["family"], self.corpora[r["corpus"]]["index"], 0, 0, BASE)
        ]
        jobs = [
            self.envelope(
                "training",
                r["family"],
                r["corpus"],
                r["cell"],
                r["arm"],
                self.corpora[r["corpus"]]["tables"][r["arm"]],
                r["seed"],
            )
            for r in refs
        ]
        rows = self.jobs(jobs, "replay")
        by = {row_key(r): r for r in rows}
        errors = []
        for ref in refs:
            observed = scientific_fields(by[row_key(ref)])
            expected = scientific_fields(ref)
            if observed != expected:
                errors.append(
                    dict(
                        key=row_key(ref),
                        fields=sorted(
                            k
                            for k in set(observed) | set(expected)
                            if observed.get(k) != expected.get(k)
                        ),
                    )
                )
        self.validation["replay"] = dict(
            rows=len(rows), passed=not errors, errors=errors
        )
        if errors or len(rows) != len(self.roster) * 2:
            raise ValueError("C1/C2 scientific replay mismatch")
        # Replays are QA only; use frozen rows once in inference.
        self.rows = []
        (self.out / "search.jsonl").rename(self.out / "replay.jsonl")
        self.complete["replay"] = True
        write_json(
            self.out,
            "reused_context.jsonl_metadata.json",
            dict(rows=len(self.saved_rows), source_sha=PROVENANCE_SHA),
        )

    def projection(self, phase):
        timing = (
            self.timings["timing"] if phase == "training" else self.timings["training"]
        )
        effective = max(
            0.01,
            min(
                self.args.workers,
                timing["worker_seconds"] / max(timing["wall_seconds"], 0.001),
            ),
        )
        costs = {}
        for f in TRAINING:
            rs = [
                r
                for r in self.rows
                if r["arm"] == "T2" and r["family"] == f and r["phase"] == "training"
            ]
            costs[f] = float(np.mean([r["seconds"] for r in rs]))
        worker = 0
        existing = {row_key(r) for r in self.rows}
        for key in expected_rows(
            self.corpora, self.roster, phase, ("T1", "T2"), self.fresh_n
        ):
            if key in existing:
                continue
            _, f, _, _, arm, _ = key
            worker += (
                HISTORICAL_T1[phase]
                if arm == "T1"
                else costs[f] * max(1, HISTORICAL_T1[phase] / HISTORICAL_T1["training"])
            )
        projected = worker / effective
        remaining = self.work_deadline - time.monotonic()
        return dict(
            admitted=timing_admission(remaining, projected),
            projected_seconds=projected,
            remaining_seconds=remaining,
            effective_workers=effective,
            T2_family_worker_seconds=costs,
            multiplier=1.25,
            rule="timing only; full roster or none",
        )

    def checkpoint(self):
        for name, value in [
            ("validation.json", self.validation),
            ("stages.json", self.complete),
            ("admission.json", self.admission),
            ("timing.json", self.timings),
        ]:
            write_json(self.out, name, value)

    def run(self):
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        try:
            if time.monotonic() >= self.work_deadline:
                raise TimeoutError(
                    "absolute work deadline passed; no searches authorized"
                )
            self.replay_sources()
            self.jobs(self.evaluation_jobs(timing=True), "timing")
            self.complete["timing"] = True
            self.admission["training"] = self.projection("training")
            self.checkpoint()
            if not self.args.preflight:
                if not self.admission["training"]["admitted"]:
                    raise TimeoutError(
                        "full primary roster exceeds timing projection allowance"
                    )
                self.jobs(self.evaluation_jobs(), "training")
                validate_rows(
                    self.saved_rows + self.rows,
                    self.corpora,
                    self.roster,
                    "training",
                    ("T1", "T2", "C1", "C2"),
                    self.fresh_n,
                )
                self.complete["training"] = self.validation["passed"] = True
                self.admission["holdout"] = self.projection("holdout")
                self.checkpoint()
                if self.admission["holdout"]["admitted"]:
                    self.jobs(self.evaluation_jobs("holdout"), "holdout")
                    validate_rows(
                        self.saved_rows + self.rows,
                        self.corpora,
                        self.roster,
                        "holdout",
                        ("T1", "T2", "C1", "C2"),
                        self.fresh_n,
                    )
                    self.complete["holdout"] = True
        except Exception as error:
            self.stop_reason = f"{type(error).__name__}: {error}"
            if not isinstance(error, TimeoutError):
                self.validation["passed"] = False
        finally:
            self.pool.terminate()
            self.pool.join()
        self.checkpoint()
        from experiments.chem_tape.context_increment_report import (
            make_report,
            save_report,
        )

        report = make_report(
            self.saved_rows + self.rows,
            self.corpora,
            self.config,
            self.complete,
            self.validation,
            self.admission,
            self.stop_reason,
        )
        report.update(
            timings=self.timings, wall_seconds=time.monotonic() - self.started
        )
        save_report(self.out, report)
        print(
            json.dumps(
                dict(
                    outcome=report["outcome"],
                    wall_seconds=report["wall_seconds"],
                    stop_reason=self.stop_reason,
                )
            ),
            flush=True,
        )
        return (
            0
            if (self.args.preflight and self.complete["timing"])
            or (self.complete["training"] and self.validation["passed"])
            else 1
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=2520)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--smoke", action="store_true")
    modes.add_argument(
        "--preflight",
        action="store_true",
        help="full replay and fixed timing block only; no inference",
    )
    args = parser.parse_args()
    if args.workers < 1 or not 120 < args.deadline_seconds <= 2520:
        parser.error("positive workers and 120<deadline<=2520 required")
    raise SystemExit(Runner(args).run())


if __name__ == "__main__":
    main()
