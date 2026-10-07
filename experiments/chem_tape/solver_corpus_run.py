"""1707 independent solver corpora, frozen fits, training and time-gated transfer."""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import search, outputs
from experiments.chem_tape.crossed_learning_run import (
    TRAINING,
    HOLDOUTS,
    DEFAULT_BANK,
    BANK_SHA,
    G4_HASH,
    load_bank,
)
from experiments.chem_tape.crossed_holdout_run import (
    SOURCE,
    SOURCE_HASHES,
    SOURCE_COMMIT,
    frozen_source,
)
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.solver_corpus_fit import (
    BASE,
    seed_for,
    validate_table,
    transition_counts,
    fit,
    admit_holdouts,
)

DATA = Path(__file__).with_name("data") / "solver_corpus_1707"
REPLAY_SHA = "eb569085b6400afa95edfbd53d8e1a269e32f3d9cc489b7b2ab5516b572f9eeb"
# Pin the timing projection as well as the replay input, not just its self-reported hash.
PROVENANCE_SHA = "6081e83d70047b4439495ef1882302f4beafa1daa3e1ca7b0982103a545834b7"
REPLAY_EXCLUDED = {
    "seconds",
    "decode_seconds",
    "budget_seconds",
    "map",
    "family",
    "phase",
}


def scientific_fields(row):
    return {k: v for k, v in row.items() if k not in REPLAY_EXCLUDED and k != "solver"}


def observed_search(envelope):
    job, meta, save_solver = envelope
    row = search(job, return_solver=save_solver)
    if save_solver:
        if row["solved"]:
            tick = time.monotonic()
            exact = outputs([row["solver"]], job[6], job[7])[0]
            if not np.array_equal(exact, job[0]["labels"]):
                raise ValueError("saved solver failed independent D1331 verification")
            row["verification_seconds"] = time.monotonic() - tick
        elif row["solver"] is not None:
            raise ValueError("unsolved search returned solver")
    row.update(meta)
    return row


class Runner:
    def __init__(self, args):
        self.args = args
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("use a fresh RUN_DIR")
        self.started = time.monotonic()
        self.work_deadline = self.started + args.deadline_seconds - 120
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
        self.saved, _, _, _ = frozen_source(SOURCE)
        for tr in self.saved.values():
            validate_table(tr["table"])
        raw = (DATA / "replay.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != REPLAY_SHA:
            raise ValueError("0315 replay SHA mismatch")
        self.replay = json.loads(raw)
        prov = (DATA / "provenance.json").read_bytes()
        if hashlib.sha256(prov).hexdigest() != PROVENANCE_SHA:
            raise ValueError("replay/timing provenance SHA mismatch")
        self.provenance = json.loads(prov)
        self.smoke = args.smoke
        self.base = BASE + (100000000 if args.smoke else 200000000 if args.probe else 0)
        self.nc = 2 if args.smoke else (1 if args.probe else 16)
        self.collect_n = 8 if args.smoke else 48
        self.fresh_n = 2 if args.smoke or args.probe else 32
        self.g4_n = 2 if args.smoke or args.probe else 96
        self.map_n = 1 if args.smoke or args.probe else 16
        self.hold_g4_n = 2 if args.smoke else 128
        # Smoke still collects at the scientific cap: reduced caps often give no tapes.
        self.cap = 524288
        self.rows = []
        self.corpora = {}
        self.stage1_complete = False
        self.stage2_complete = False
        self.stop_reason = None
        self.validation = dict(
            passed=False,
            bank_sha256=BANK_SHA,
            g4_hash=G4_HASH,
            replay_sha256=REPLAY_SHA,
            solver_verifications=0,
            table_checks=0,
            pairing_checks=0,
        )
        self.timings = {}
        self.admission = None
        self.config = dict(
            task="2026-10-07-1707",
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            smoke_only=args.smoke,
            probe_only=args.probe,
            arguments=vars(args),
            training=TRAINING,
            holdouts=HOLDOUTS,
            bank_sha256=BANK_SHA,
            g4_hash=G4_HASH,
            replay_sha256=REPLAY_SHA,
            seed_base=self.base,
            reference_source_commit=SOURCE_COMMIT,
            reference_source_hashes=SOURCE_HASHES,
            seed_rule="base+phase*1000000+family_index*100000+corpus_index*2000+cell_index*200+seed_index",
            phases=dict(
                collection=0,
                training=1,
                holdout=2,
                G4_training=3,
                M_training=4,
                G4_holdout=5,
            ),
            n_corpora_per_family=self.nc,
            collect_n=self.collect_n,
            fresh_n=self.fresh_n,
            g4_training_n=self.g4_n,
            M_training_n=self.map_n,
            g4_holdout_n=self.hold_g4_n,
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
            collection_yield_floor=4 if args.smoke else 24,
            maximum_K_failures_per_family=4,
            workers=args.workers,
            unsolved_primary="2*cap",
            unsolved_sensitivity="1*cap",
        )
        write_json(self.out, "config.json", self.config)
        write_json(self.out, "reference_maps.json", self.saved)
        write_json(self.out, "validation.json", self.validation)

    def envelope(self, phase, family, corpus, cid, arm, table, seed, solver=False):
        allowed = self.hold_cells if phase == "holdout" else self.cells
        if cid not in allowed:
            raise ValueError("holdout leakage / invalid phase cell")
        if set(allowed[cid]) != {"id", "labels"}:
            raise ValueError("solver/canonical program in payload")
        meta = dict(phase=phase, family=family, corpus=corpus)
        return (
            (allowed[cid], arm, table, seed, self.cap, 256, self.inputs, ALPHABET),
            meta,
            solver,
        )

    def jobs(self, jobs, phase):
        expected = {
            (
                m["phase"],
                m["family"],
                m["corpus"],
                j[0]["id"],
                j[1],
                j[3],
            ): hashlib.sha256(np.asarray(j[2], dtype="<i8").tobytes()).hexdigest()
            for j, m, _ in jobs
        }
        if len(expected) != len(jobs):
            raise ValueError("duplicate search roster")
        rows = []
        pairing = {}
        tick = time.monotonic()
        with (self.out / "search.jsonl").open("a", buffering=1) as stream:

            def save(row):
                key = tuple(
                    row[k] for k in ("phase", "family", "corpus", "cell", "arm", "seed")
                )
                if expected.pop(key) != row["table_hash"]:
                    raise ValueError("search table hash mismatch")
                if (
                    row["cap"] != self.cap
                    or row["pop_size"] != 256
                    or (not row["solved"] and row["evaluations"] != self.cap)
                ):
                    raise ValueError("search budget validation failed")
                indices = (
                    np.random.default_rng([row["seed"], 0])
                    .choice(1331, 64, replace=False)
                    .tolist()
                )
                if row["training_indices"] != indices:
                    raise ValueError("case seed validation failed")
                pkey = key[:4] + (row["seed"],)
                if pkey in pairing and pairing[pkey] != row["training_indices"]:
                    raise ValueError("arm case pairing failed")
                if pkey in pairing:
                    self.validation["pairing_checks"] += 1
                pairing[pkey] = row["training_indices"]
                self.validation["solver_verifications"] += int(
                    "solver" in row and row["solved"]
                )
                rows.append(row)
                self.rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")

            complete = run_jobs(
                self.pool, observed_search, jobs, self.work_deadline, save
            )
        self.timings[phase] = dict(
            wall_seconds=time.monotonic() - tick,
            worker_seconds=sum(
                r["seconds"] + r.get("verification_seconds", 0) for r in rows
            ),
            rows=len(rows),
            expected_rows=len(jobs),
            complete=complete,
        )
        write_json(self.out, "timing.json", self.timings)
        if not complete or expected:
            raise TimeoutError(f"{phase} incomplete at internal deadline")
        return rows

    def validate_replay(self):
        refs = self.replay[:1] + self.replay[20:21] if self.smoke else self.replay
        jobs = [
            self.envelope(
                "replay",
                r["cell"][:2],
                "replay",
                r["cell"],
                "GG",
                self.g4,
                r["seed"],
                True,
            )
            for r in refs
        ]
        rows = self.jobs(jobs, "replay")
        by = {(r["cell"], r["seed"]): r for r in rows}
        errors = []
        for ref in refs:
            row = by[ref["cell"], ref["seed"]]
            changed = [k for k, v in scientific_fields(ref).items() if row.get(k) != v]
            if changed:
                errors.append(dict(cell=ref["cell"], seed=ref["seed"], fields=changed))
        self.validation["replay"] = dict(
            passed=not errors,
            rows=len(rows),
            errors=errors,
            excluded_fields=sorted(REPLAY_EXCLUDED),
        )
        if errors:
            raise ValueError("deterministic 0315 replay failed")

    def collect(self):
        for family, cells in TRAINING.items():
            for k in range(self.nc):
                tid = f"{family}{k + 1}"
                jobs = [
                    self.envelope(
                        "collection",
                        family,
                        tid,
                        cid,
                        "G4",
                        self.g4,
                        seed_for(0, family, k, c, s, self.base),
                        True,
                    )
                    for c, cid in enumerate(cells)
                    for s in range(self.collect_n)
                ]
                rows = self.jobs(jobs, f"collection:{tid}")
                counts, yields = transition_counts(rows, cells)
                record = dict(
                    family=family,
                    index=k,
                    yields=yields,
                    counts=counts.tolist(),
                    collection_evaluations=sum(r["evaluations"] for r in rows),
                    collection_seconds=sum(
                        r["seconds"] + r.get("verification_seconds", 0) for r in rows
                    ),
                    collection_wall_seconds=self.timings[f"collection:{tid}"][
                        "wall_seconds"
                    ],
                )
                self.corpora[tid] = record
                write_json(self.out, "corpora.json", self.corpora)
                if min(yields.values()) < self.config["collection_yield_floor"]:
                    raise ValueError(
                        f"{tid} collection cell below yield floor: {yields}"
                    )
                tick = time.monotonic()
                fitted, diagnostic = fit(counts)
                record.update(
                    tables={a: t.tolist() for a, t in fitted.items()},
                    fit=diagnostic,
                    fit_seconds=time.monotonic() - tick,
                )
                self.validation["table_checks"] += 3
                write_json(self.out, "corpora.json", self.corpora)
                print(
                    json.dumps(
                        dict(
                            stage="collection_fit",
                            corpus=tid,
                            yields=yields,
                            K_error=diagnostic["K_max_error"],
                            elapsed=time.monotonic() - self.started,
                        )
                    ),
                    flush=True,
                )
            failures = sum(
                not tr["fit"]["K_valid"]
                for tr in self.corpora.values()
                if tr["family"] == family
            )
            if failures > 4:
                raise ValueError(f"{family}: {failures} failed K fits (>4)")

    def evaluation_jobs(self, holdout=False):
        jobs = []
        phase = "holdout" if holdout else "training"
        for tid, tr in self.corpora.items():
            cells = sum(HOLDOUTS.values(), []) if holdout else TRAINING[tr["family"]]
            for c, cid in enumerate(cells):
                for s in range(self.fresh_n):
                    seed = seed_for(
                        2 if holdout else 1, tr["family"], tr["index"], c, s, self.base
                    )
                    for arm in ("T", "C", "K"):
                        if arm == "K" and not tr["fit"]["K_valid"]:
                            continue
                        jobs.append(
                            self.envelope(
                                phase,
                                tr["family"],
                                tid,
                                cid,
                                arm,
                                tr["tables"][arm],
                                seed,
                            )
                        )
        for family, cells in (HOLDOUTS if holdout else TRAINING).items():
            for c, cid in enumerate(cells):
                for s in range(self.hold_g4_n if holdout else self.g4_n):
                    jobs.append(
                        self.envelope(
                            phase,
                            family,
                            "G4",
                            cid,
                            "G4",
                            self.g4,
                            seed_for(5 if holdout else 3, family, 0, c, s, self.base),
                        )
                    )
        if not holdout:
            for tid, tr in self.saved.items():
                family = tr["family"]
                for c, cid in enumerate(TRAINING[family]):
                    for s in range(self.map_n):
                        jobs.append(
                            self.envelope(
                                phase,
                                family,
                                f"M:{tid}",
                                cid,
                                "M",
                                tr["table"],
                                seed_for(4, family, int(tid[2:]) - 1, c, s, self.base),
                            )
                        )
        return jobs

    def holdout_projection(self, jobs):
        training = [r for r in self.rows if r["phase"] == "training"]
        g4 = [r for r in training if r["arm"] == "G4"]
        # Historical holdout/train G4 ratio compensates for task difficulty; never a result gate.
        historical = self.provenance["holdout_G4_mean_seconds"]
        train_g4 = np.mean([r["seconds"] for r in g4])
        factor = max(1.0, max(historical.values()) / train_g4)
        costs = {
            a: np.mean([r["seconds"] for r in training if r["arm"] == a])
            for a in ("T", "C", "K", "G4")
            if any(r["arm"] == a for r in training)
        }
        observed = self.timings["training"]
        effective = min(
            self.args.workers, observed["worker_seconds"] / observed["wall_seconds"]
        )
        projection = sum(costs[j[1]] for j, _, _ in jobs) * factor / max(effective, 1)
        remaining = self.work_deadline - time.monotonic()
        return dict(
            projected_seconds=projection,
            remaining_seconds=remaining,
            difficulty_factor=factor,
            effective_workers=effective,
            training_costs=costs,
            historical_holdout_G4_seconds=historical,
            admitted=admit_holdouts(remaining, projection),
            multiplier=1.5,
        )

    def run(self):
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        try:
            self.validate_replay()
            self.collect()
            self.jobs(self.evaluation_jobs(), "training")
            self.stage1_complete = True
            self.validation["passed"] = True
            if not self.args.probe:
                jobs = self.evaluation_jobs(True)
                self.admission = self.holdout_projection(jobs)
                write_json(self.out, "admission.json", self.admission)
                if self.admission["admitted"]:
                    self.jobs(jobs, "holdout")
                    self.stage2_complete = True
                else:
                    self.stop_reason = "stage 2 skipped: insufficient projected time"
        except Exception as error:
            self.stop_reason = f"{type(error).__name__}: {error}"
            if not self.stage1_complete:
                self.validation["passed"] = False
        finally:
            self.pool.terminate()
            self.pool.join()
        write_json(self.out, "validation.json", self.validation)
        write_json(
            self.out,
            "admission.json",
            self.admission
            or dict(admitted=False, reason="probe or stage 1 incomplete"),
        )
        from experiments.chem_tape.solver_corpus_report import make_report, save_report

        report = make_report(
            self.rows,
            self.corpora,
            self.config,
            self.stage1_complete,
            self.stage2_complete,
            self.validation,
            self.stop_reason,
        )
        report.update(timings=self.timings, admission=self.admission)
        save_report(self.out, report, self.rows)
        report["wall_seconds"] = time.monotonic() - self.started
        write_json(self.out, "result.json", report)
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
        return 0 if self.stage1_complete else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=7920)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--smoke", action="store_true")
    modes.add_argument(
        "--probe",
        action="store_true",
        help="one 48/cell corpus/family and small fresh check; no holdouts",
    )
    args = parser.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 120:
        parser.error("positive workers and deadline >120 required")
    raise SystemExit(Runner(args).run())


if __name__ == "__main__":
    main()
