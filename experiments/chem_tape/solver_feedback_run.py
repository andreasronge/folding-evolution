"""1924: one fixed-rule solver-corpus feedback refit, with a timed source control."""

from __future__ import annotations

import argparse
import datetime as dt
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
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.crossed_learning_run import (
    TRAINING,
    HOLDOUTS,
    DEFAULT_BANK,
    BANK_SHA,
    G4_HASH,
    load_bank,
)
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.solver_corpus_fit import (
    BASE,
    fit,
    seed_for,
    transition_counts,
    validate_table,
)
from experiments.chem_tape.solver_corpus_run import (
    Runner as CorpusRunner,
    scientific_fields,
)

DATA = Path(__file__).with_name("data") / "solver_feedback_1924"
PROVENANCE_SHA = "e7f9d6494643172ec4615628c1a940997d325531da724d9c908a4ab1694ab113"
OWNER_WORK_CUTOFF = (
    "2026-10-07T20:05:00+00:00"  # 22:05 Stockholm, 20 min analysis reserve
)


def frozen_parents():
    raw = (DATA / "provenance.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != PROVENANCE_SHA:
        raise ValueError("1924 provenance SHA mismatch")
    provenance = json.loads(raw)
    artifacts = {}
    for name, digest in provenance["artifact_hashes"].items():
        raw = (DATA / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError(f"{name} SHA mismatch")
        artifacts[name] = json.loads(raw)
    parents = artifacts["parents.json"]
    expected = {f"{f}{k + 1}" for f in TRAINING for k in range(16)}
    if set(parents) != expected:
        raise ValueError("parent roster mismatch")
    for tid, tr in parents.items():
        if (
            tid != f"{tr['family']}{tr['index'] + 1}"
            or validate_table(tr["table"]) != tr["table_hash"]
        ):
            raise ValueError("parent lineage/hash mismatch")
    return parents, artifacts["replay.json"], artifacts["solvers.json"], provenance


def admit_control(remaining, full_projection):
    """Fixed full/half/none roster; no scientific results enter this gate."""
    if remaining > 1.25 * full_projection:
        return 16
    if remaining > 1.25 * full_projection / 2:
        return 8
    return 0


class Runner(CorpusRunner):
    # Reuse the reviewed payload-leakage, search-budget/hash/case checks and
    # streaming runner. No change to search or the frozen fitter.
    def __init__(self, args):
        self.args = args
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("use a fresh RUN_DIR")
        self.started = time.monotonic()
        now = dt.datetime.now(dt.timezone.utc)
        available = (dt.datetime.fromisoformat(args.work_cutoff) - now).total_seconds()
        self.work_deadline = self.started + min(args.deadline_seconds, available)
        self.bank, self.cells = load_bank(DEFAULT_BANK)
        self.hold_cells = {
            c["id"]: {"id": c["id"], "labels": c["labels"]}
            for c in self.bank["cells"]
            if c["id"] in sum(HOLDOUTS.values(), [])
        }
        self.inputs = inputs_for("D1331")
        self.g4 = tables()["G4"]
        if validate_table(self.g4) != G4_HASH:
            raise ValueError("G4 hash mismatch")
        self.parents, self.replay, self.old_solvers, self.provenance = frozen_parents()
        self.base = BASE + (300000000 if args.smoke else 0)
        self.nc = 1 if args.smoke else 16
        self.collect_n = 8 if args.smoke else 48
        self.fresh_n = 2 if args.smoke else 32
        self.cap = 524288
        self.roster = [f"{f}{k + 1}" for f in TRAINING for k in range(self.nc)]
        self.rows, self.corpora, self.timings = [], {}, {}
        self.validation = dict(
            passed=False,
            bank_sha256=BANK_SHA,
            g4_hash=G4_HASH,
            parent_table_checks=32,
            table_checks=32,
            solver_verifications=0,
            old_solver_verifications=0,
            pairing_checks=0,
        )
        self.complete = dict(
            A=False,
            B=False,
            C=False,
            D_collection=False,
            D_training=False,
            D_holdout=False,
        )
        self.admission = dict(roster=[], admitted=False, reason="A–C not yet complete")
        self.stop_reason = None
        self.control_failure = None
        self.control_valid = True
        self.config = dict(
            task="2026-10-07-1924",
            arguments=vars(args),
            smoke_only=args.smoke,
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            submitted_at=now.isoformat(),
            owner_work_cutoff=args.work_cutoff,
            available_work_seconds=max(0, self.work_deadline - self.started),
            owner_analysis_reserve_seconds=1200,
            bank_sha256=BANK_SHA,
            g4_hash=G4_HASH,
            parent_provenance_sha256=PROVENANCE_SHA,
            parent_source=self.provenance,
            training=TRAINING,
            holdouts=HOLDOUTS,
            roster=self.roster,
            seed_base=self.base,
            phases=dict(C_collection=10, training=11, holdout=12, G4_collection=13),
            seed_rule="seed_for(phase, family, lineage_index, cell_index, seed_index, base)",
            n_corpora_per_family=self.nc,
            collect_n=self.collect_n,
            fresh_n=self.fresh_n,
            collection_yield_floor=4 if args.smoke else 24,
            cap=self.cap,
            population=256,
            length=32,
            training_cases=64,
            domain="D1331",
            alphabet=ALPHABET,
            allele_range=24000,
            minimum_count=250,
            alpha=50,
            cell_transition_weight=1600,
            token_multiplier_bound=16,
            K_steps=400,
            K_step=0.7,
            K_tolerance=0.001,
            unsolved_primary="2*cap",
            workers=args.workers,
            source_scope="decoder procedure, including yield and tape diversity",
            expected_parent_solve_counts=dict(
                training=[5077, 5120], holdout=[3034, 3072]
            ),
        )
        write_json(self.out, "config.json", self.config)
        write_json(self.out, "validation.json", self.validation)

    def checkpoint(self):
        write_json(self.out, "corpora.json", self.corpora)
        write_json(self.out, "validation.json", self.validation)
        write_json(self.out, "stages.json", self.complete)

    def validate_sources(self):
        # Batched independent replay of ALL saved solver tapes, not canonical witnesses.
        tick = time.monotonic()
        for tid, tr in self.parents.items():
            for cid in TRAINING[tr["family"]]:
                tapes = [
                    r["solver"]
                    for r in self.old_solvers
                    if r["corpus"] == tid and r["cell"] == cid
                ]
                if not tapes:
                    raise ValueError("missing saved solver cell")
                if any(
                    len(p) != 32
                    or any(type(t) is not int or not 0 <= t < 24 for t in p)
                    for p in tapes
                ):
                    raise ValueError("invalid saved tape")
                for offset in range(0, len(tapes), 64):
                    batch = tapes[offset : offset + 64]
                    if not np.all(
                        outputs(batch, self.inputs, ALPHABET)
                        == np.asarray(self.cells[cid]["labels"])
                    ):
                        raise ValueError(
                            "1707 saved tape failed independent D1331 verification"
                        )
                    self.validation["old_solver_verifications"] += len(batch)
        if (
            self.validation["old_solver_verifications"]
            != self.provenance["solver_count"]
        ):
            raise ValueError("saved solver roster/leakage mismatch")
        self.timings["old_solver_validation"] = dict(
            wall_seconds=time.monotonic() - tick
        )
        # There are 20 GG seeds per replay cell (40 rows total); retain them all.
        jobs = [
            self.envelope(
                "replay",
                r["family"],
                "replay",
                r["cell"],
                "GG",
                self.g4,
                r["seed"],
                True,
            )
            for r in self.replay
        ]
        rows = self.jobs(jobs, "replay")
        by = {(r["cell"], r["seed"]): r for r in rows}
        errors = []
        for ref in self.replay:
            row = by[ref["cell"], ref["seed"]]
            changed = [
                k
                for k, v in scientific_fields(ref).items()
                if k not in {"corpus", "verification_seconds"} and row.get(k) != v
            ]
            if row.get("solver") != ref.get("solver"):
                changed.append("solver")
            if changed:
                errors.append(dict(cell=ref["cell"], seed=ref["seed"], fields=changed))
        self.validation["replay"] = dict(
            rows=len(rows), passed=not errors, errors=errors
        )
        if errors:
            raise ValueError("1707 GG bit-identical replay failed")
        self.validation["sources_passed"] = True
        self.checkpoint()

    def collect(self, source, roster):
        stage = "A" if source == "C" else "D_collection"
        phase = "collection_C" if source == "C" else "collection_G4"
        for tid in roster:
            parent = self.parents[tid]
            family, k = parent["family"], parent["index"]
            cells = TRAINING[family]
            table = parent["table"] if source == "C" else self.g4
            jobs = [
                self.envelope(
                    phase,
                    family,
                    tid,
                    cid,
                    source,
                    table,
                    seed_for(10 if source == "C" else 13, family, k, c, s, self.base),
                    True,
                )
                for c, cid in enumerate(cells)
                for s in range(self.collect_n)
            ]
            rows = self.jobs(jobs, f"{stage}:{tid}")
            record = dict(
                family=family,
                index=k,
                attempts=len(rows),
                yields={
                    cid: sum(r["solved"] for r in rows if r["cell"] == cid)
                    for cid in cells
                },
                distinct_tapes=len({tuple(r["solver"]) for r in rows if r["solved"]}),
                distinct_per_cell={
                    cid: len(
                        {
                            tuple(r["solver"])
                            for r in rows
                            if r["cell"] == cid and r["solved"]
                        }
                    )
                    for cid in cells
                },
                collection_evaluations=sum(r["evaluations"] for r in rows),
                collection_seconds=sum(
                    r["seconds"] + r.get("verification_seconds", 0) for r in rows
                ),
                collection_wall_seconds=self.timings[f"{stage}:{tid}"]["wall_seconds"],
            )
            self.corpora.setdefault(
                tid, dict(family=family, index=k, C=parent["table"])
            )["C2" if source == "C" else "Cprime"] = record
            self.checkpoint()
            if min(record["yields"].values()) < self.config["collection_yield_floor"]:
                raise ValueError(
                    f"{stage}:{tid} collection below yield floor: {record['yields']}"
                )
            counts, yields = transition_counts(rows, cells)
            tick = time.monotonic()
            fitted, diagnostic = fit(counts)
            record.update(
                counts=counts.tolist(),
                tables={a: t.tolist() for a, t in fitted.items()},
                fit=diagnostic,
                fit_seconds=time.monotonic() - tick,
            )
            self.validation["table_checks"] += 3
            self.checkpoint()
            print(
                json.dumps(
                    dict(
                        stage=stage,
                        lineage=tid,
                        yields=yields,
                        elapsed=time.monotonic() - self.started,
                    )
                ),
                flush=True,
            )
        self.complete[stage] = True
        self.checkpoint()

    def evaluation_jobs(self, holdout=False, control=False):
        jobs = []
        roster = self.admission["roster"] if control else self.roster
        phase = "holdout" if holdout else "training"
        for tid in roster:
            tr = self.corpora[tid]
            cells = sum(HOLDOUTS.values(), []) if holdout else TRAINING[tr["family"]]
            arms = ["Cprime"] if control else ["C2", "C"]
            for c, cid in enumerate(cells):
                for s in range(self.fresh_n):
                    seed = seed_for(
                        12 if holdout else 11,
                        tr["family"],
                        tr["index"],
                        c,
                        s,
                        self.base,
                    )
                    for arm in arms:
                        table = tr["C"] if arm == "C" else tr[arm]["tables"]["C"]
                        jobs.append(
                            self.envelope(
                                phase, tr["family"], tid, cid, arm, table, seed
                            )
                        )
        return jobs

    def control_projection(self):
        timings = [
            v
            for k, v in self.timings.items()
            if k == "B" or k == "C" or k.startswith("A:")
        ]
        effective = min(
            self.args.workers,
            sum(v["worker_seconds"] for v in timings)
            / sum(v["wall_seconds"] for v in timings),
        )
        effective = max(effective, 0.01)
        historical = self.provenance["historical_C_worker_seconds"]
        ncollection = self.nc * sum(map(len, TRAINING.values())) * self.collect_n
        ntraining = self.nc * sum(map(len, TRAINING.values())) * self.fresh_n
        nhold = len(self.roster) * 3 * self.fresh_n
        worker = (
            ncollection * self.provenance["G4_collection_worker_seconds"]
            + ntraining * historical["training"]
            + nhold * historical["holdout"]
        )
        fits = sum(tr["C2"]["fit_seconds"] for tr in self.corpora.values())
        projection = worker / effective + fits
        remaining = self.work_deadline - time.monotonic()
        n = (
            self.nc
            if self.args.smoke and remaining > 1.25 * projection
            else (0 if self.args.smoke else admit_control(remaining, projection))
        )
        roster = [f"{f}{k + 1}" for f in TRAINING for k in range(n)]
        return dict(
            admitted=bool(roster),
            roster=roster,
            n_per_family=n,
            projected_full_seconds=projection,
            projected_admitted_seconds=projection * n / self.nc,
            remaining_seconds=remaining,
            effective_workers=effective,
            multiplier=1.25,
            historical_costs=self.provenance,
            reason="timing gate only",
        )

    def run(self):
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        try:
            self.validate_sources()
            self.collect("C", self.roster)
            self.jobs(self.evaluation_jobs(), "B")
            self.complete["B"] = True
            self.validation["passed"] = True
            self.checkpoint()
            self.jobs(self.evaluation_jobs(holdout=True), "C")
            self.complete["C"] = True
            self.checkpoint()
            self.admission = self.control_projection()
            write_json(self.out, "admission.json", self.admission)
            if self.admission["admitted"]:
                try:
                    self.collect("G4", self.admission["roster"])
                    self.jobs(self.evaluation_jobs(control=True), "D_training")
                    self.complete["D_training"] = True
                    self.checkpoint()
                    self.jobs(
                        self.evaluation_jobs(holdout=True, control=True), "D_holdout"
                    )
                    self.complete["D_holdout"] = True
                except Exception as error:
                    self.control_failure = f"{type(error).__name__}: {error}"
                    # Timeout leaves complete training contrast usable; scientific
                    # control failure invalidates the control procedure as a whole.
                    if not isinstance(error, TimeoutError):
                        self.control_valid = False
            else:
                self.control_failure = "D skipped: insufficient projected time"
        except Exception as error:
            self.stop_reason = f"{type(error).__name__}: {error}"
            if not self.complete["B"] or not isinstance(error, TimeoutError):
                self.validation["passed"] = False
        finally:
            self.pool.terminate()
            self.pool.join()
        self.checkpoint()
        write_json(self.out, "admission.json", self.admission)
        from experiments.chem_tape.solver_feedback_report import (
            make_report,
            save_report,
        )

        report = make_report(
            self.rows,
            self.corpora,
            self.config,
            self.complete,
            self.validation,
            self.admission,
            self.control_valid,
            self.stop_reason,
            self.control_failure,
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
                    control_failure=self.control_failure,
                )
            ),
            flush=True,
        )
        return 0 if self.complete["B"] and self.validation["passed"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=6000)
    parser.add_argument("--work-cutoff", default=OWNER_WORK_CUTOFF)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.workers < 1 or not 0 < args.deadline_seconds <= 6000:
        parser.error("positive workers and 0<deadline<=6000 required")
    cutoff = dt.datetime.fromisoformat(args.work_cutoff)
    if cutoff.tzinfo is None or (
        not args.smoke and args.work_cutoff != OWNER_WORK_CUTOFF
    ):
        parser.error("full runs require the approved absolute work cutoff")
    raise SystemExit(Runner(args).run())


if __name__ == "__main__":
    main()
