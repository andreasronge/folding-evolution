"""1831: balanced pre-solution acquisition, frozen fitting and paired training search."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import (
    BANK_SHA,
    TRAINING,
    digest,
    load_training,
)
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import search
from experiments.chem_tape.crossed_learning_run import G4_HASH
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.partial_program_collect import CHECKPOINTS, collect_search
from experiments.chem_tape.solver_corpus_fit import (
    fit,
    partial_transition_counts,
    seed_for,
    validate_table,
)
from experiments.chem_tape.then_addition_run import frozen_source

BASE = 202610081831
CAP = 524288
COLLECT_CAP = 65536
ARMS = ("C_S", "T_S", "C_P", "C_exact", "G4")


def roster(base=BASE, nc=8, collect_n=32, fresh_n=16):
    rows = []
    for k in range(nc):
        for family, cells in TRAINING.items():
            for phase, count, arms in (
                ("collection", collect_n, ("G4",)),
                ("training", fresh_n, ARMS),
            ):
                for c, cid in enumerate(cells):
                    for s in range(count):
                        for arm in arms:
                            rows.append(
                                dict(
                                    phase=phase,
                                    family=family,
                                    corpus=f"{family}{k + 1}",
                                    cell=cid,
                                    arm=arm,
                                    seed=seed_for(
                                        int(phase == "training"), family, k, c, s, base
                                    ),
                                )
                            )
    by_seed = {}
    for row in rows:
        by_seed.setdefault(row["seed"], []).append(row)
    for group in by_seed.values():
        expected = ("G4",) if group[0]["phase"] == "collection" else ARMS
        if set(r["arm"] for r in group) != set(expected) or len(group) != len(expected):
            raise ValueError("seed collision / incomplete arm pairing")
        if any(
            {k: v for k, v in r.items() if k != "arm"}
            != {k: v for k, v in group[0].items() if k != "arm"}
            for r in group
        ):
            raise ValueError("seed collision outside paired search")
    return rows


def score_search(envelope):
    job, meta = envelope
    result = search(job)
    result.update(meta, worker_seconds=result["seconds"])
    return result


def archive_diagnostics(rows, kind):
    result = {}
    for cid in sorted({r["cell"] for r in rows}):
        sources = [r for r in rows if r["cell"] == cid]
        archive = [a for r in sources for a in r["archive"] if a["kind"] == kind]
        contributing = sum(
            any(a["kind"] == kind for a in r["archive"]) for r in sources
        )
        tapes = len({tuple(a["tape"]) for a in archive})
        result[cid] = dict(
            attempts=len(sources),
            contributing_sources=contributing,
            effective_sources=contributing,
            archive_rows=len(archive),
            distinct_tapes=tapes,
            duplicate_rate=1 - tapes / len(archive) if archive else None,
            later_solved_share=np.mean(
                [a["source_later_solved"] for a in archive]
            ).item()
            if archive
            else None,
            training_perfect_share=np.mean(
                [a["training_correct"] == 64 for a in archive]
            ).item()
            if archive
            else None,
            mean_d1331_accuracy=np.mean(
                [a["d1331_correct"] / 1331 for a in archive]
            ).item()
            if archive
            else None,
        )
    return result


class Runner:
    def __init__(self, args):
        self.args = args
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("use a fresh RUN_DIR")
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 120
        self.bank, self.cells = load_training()
        self.inputs = self.bank["inputs"]
        self.g4 = tables()["G4"]
        if validate_table(self.g4) != G4_HASH:
            raise ValueError("G4 hash mismatch")
        self.saved, self.provenance = frozen_source()
        self.nc, self.collect_n, self.fresh_n = (1, 4, 2) if args.smoke else (8, 32, 16)
        self.base = BASE + (100000000 if args.smoke else 0)
        self.schedule = roster(self.base, self.nc, self.collect_n, self.fresh_n)
        self.rows, self.corpora, self.timings = [], {}, {}
        self.completed_pairs = 0
        self.stop_kind = self.stop_reason = None
        hashes = {}
        for name in (
            "partial_program_run.py",
            "partial_program_collect.py",
            "partial_program_report.py",
            "composition_search.py",
            "solver_corpus_fit.py",
            "comparison_gate_bank.py",
            "composition_run.py",
            "four_reducer_maps.py",
            "map_learning.py",
            "then_addition_run.py",
            "assembly_bank.py",
            "four_reducer_bank.py",
        ):
            hashes[name] = hashlib.sha256(
                Path(__file__).with_name(name).read_bytes()
            ).hexdigest()
        for name in (
            "_folding_rust._folding_rust",
            "folding_evolution.chem_tape.evolve",
            "folding_evolution.chem_tape.executor",
            "folding_evolution.chem_tape.alphabet",
        ):
            hashes[name] = hashlib.sha256(
                Path(importlib.import_module(name).__file__).read_bytes()
            ).hexdigest()
        method = dict(
            bank_sha256=BANK_SHA,
            split_hash=self.bank["split_hash"],
            inputs_hash=self.bank["inputs_hash"],
            code_hashes=hashes,
            g4_hash=G4_HASH,
            exact_source=self.provenance,
            alphabet=ALPHABET,
            cap=CAP,
            collection_cap=COLLECT_CAP,
            population=256,
            tape_length=32,
            training_cases=64,
            crossover=0.7,
            mutation=0.03,
            elite=2,
            checkpoints=list(CHECKPOINTS),
            samples_per_checkpoint_kind=8,
            replacement=True,
            terminal_parents="508 lexicase slots from copied selection state, same evaluated population",
            archive_seed_rule="default_rng([source_seed,1831])",
            weighting="equal archive rows within source; equal contributing sources within cell; cell total1600",
            alpha=50,
            minimum_count=250,
            allele_range=24000,
            T_multiplier_bounds=[1 / 16, 16],
            arms=list(ARMS),
            K_scored=False,
            source_empty_cell="error; no replacement",
            endpoint="exp(mean_corpus(mean_cell_seed(log(cost_T_S)-log(cost_C_S))))",
            interval="95% t across independent corpora, equal BE/PA weight",
            unsolved_primary="2*cap",
            worthwhile_margin=1.20,
            decision_precedence=[
                "UB_C/T<1.20: bounded gain",
                "LB_C/T>1 and LB_C/G4>1: useful",
                "LB_C/T>1: relative advantage, absolute usefulness unresolved",
                "otherwise unresolved",
            ],
            prefix="fixed BE_i/PA_i blocks; >=6 complete pairs; errors ineligible",
            scope="training reuse, development bank, fitting procedure; no isolated order or transfer",
        )
        self.config = dict(
            task="2026-10-08-1831",
            arguments=vars(args),
            smoke_only=args.smoke,
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            method=method,
            method_hash=digest(method),
            seed_base=self.base,
            seed_rule="base+phase*1000000+(family==PA)*100000+corpus*2000+cell*200+index",
            nc=self.nc,
            collect_n=self.collect_n,
            fresh_n=self.fresh_n,
            workers=args.workers,
            pair_order=[[f"BE{k + 1}", f"PA{k + 1}"] for k in range(self.nc)],
        )
        self.validation = dict(
            passed=False, archive_verifications=0, pairing_checks=0, holdout_searches=0
        )
        for name, data in (
            ("config.json", self.config),
            ("bank.json", self.bank),
            ("schedule.json", self.schedule),
        ):
            write_json(self.out, name, data)
        self.save_state()

    def envelope(self, row):
        if (
            row["phase"] not in ("collection", "training")
            or row["cell"] not in TRAINING[row["family"]]
        ):
            raise ValueError("training-only payload required")
        cell = self.cells[row["cell"]]
        if set(cell) != {"id", "labels"}:
            raise ValueError("program leaked to search")
        table = (
            self.g4
            if row["arm"] == "G4"
            else self.corpora[row["corpus"]]["tables"][row["arm"]]
        )
        cap = COLLECT_CAP if row["phase"] == "collection" else CAP
        return (
            (cell, row["arm"], table, row["seed"], cap, 256, self.inputs, ALPHABET),
            {k: row[k] for k in ("phase", "family", "corpus")},
        )

    def jobs(self, roster_rows, name):
        envelopes = [self.envelope(r) for r in roster_rows]
        expected = {
            tuple(
                r[k] for k in ("phase", "family", "corpus", "cell", "arm", "seed")
            ): validate_table(job[2])
            for r, (job, _) in zip(roster_rows, envelopes)
        }
        if len(expected) != len(envelopes):
            raise ValueError("duplicate roster")
        rows, pairing = [], {}
        tick = time.monotonic()
        serialization_seconds = 0
        with (self.out / "search.jsonl").open("a", buffering=1) as stream:

            def save(row):
                nonlocal serialization_seconds
                key = tuple(
                    row[k] for k in ("phase", "family", "corpus", "cell", "arm", "seed")
                )
                if expected.pop(key) != row["table_hash"]:
                    raise ValueError("wrong table")
                cap = COLLECT_CAP if row["phase"] == "collection" else CAP
                if (
                    row["cap"] != cap
                    or row["pop_size"] != 256
                    or not 0 < row["evaluations"] <= cap
                    or row["evaluations"] % 256
                    or (not row["solved"] and row["evaluations"] != cap)
                ):
                    raise ValueError("invalid budget")
                indices = (
                    np.random.default_rng([row["seed"], 0])
                    .choice(1331, 64, replace=False)
                    .tolist()
                )
                if row["training_indices"] != indices:
                    raise ValueError("case seed mismatch")
                pkey = key[:4] + (row["seed"],)
                if pkey in pairing:
                    if pairing[pkey] != indices:
                        raise ValueError("unpaired cases")
                    self.validation["pairing_checks"] += 1
                pairing[pkey] = indices
                self.validation["archive_verifications"] += len(row.get("archive", []))
                rows.append(row)
                self.rows.append(row)
                serial_tick = time.monotonic()
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                serialization_seconds += time.monotonic() - serial_tick

            try:
                complete = run_jobs(
                    self.pool,
                    collect_search
                    if roster_rows[0]["phase"] == "collection"
                    else score_search,
                    envelopes,
                    self.deadline,
                    save,
                )
            finally:
                self.timings[name] = dict(
                    wall_seconds=time.monotonic() - tick,
                    worker_seconds=sum(r["worker_seconds"] for r in rows),
                    serialization_seconds=serialization_seconds,
                    rows=len(rows),
                    expected_rows=len(envelopes),
                    complete=not expected,
                )
                write_json(self.out, "timing.json", self.timings)
        if not complete or expected:
            raise TimeoutError(f"{name} incomplete at internal deadline")
        return rows

    def collect(self, tid):
        family = tid[:2]
        rows = self.jobs(
            [
                r
                for r in self.schedule
                if r["phase"] == "collection" and r["corpus"] == tid
            ],
            f"collection:{tid}",
        )
        record = dict(
            family=family,
            index=int(tid[2:]) - 1,
            diagnostics={kind: archive_diagnostics(rows, kind) for kind in ("S", "P")},
            collection_evaluations=sum(r["evaluations"] for r in rows),
            collection_worker_seconds=sum(r["worker_seconds"] for r in rows),
            verification_seconds=sum(r["archive_verification_seconds"] for r in rows),
        )
        self.corpora[tid] = record
        self.save_state()
        tick = time.monotonic()
        fits, diagnostics, counts = {}, {}, {}
        for kind in ("S", "P"):
            n, yields = partial_transition_counts(rows, TRAINING[family], kind)
            fitted, diagnostic = fit(n)
            counts[kind] = n.tolist()
            diagnostics[kind] = dict(**diagnostic, contributing_sources=yields)
            fits[f"C_{kind}"] = fitted["C"].tolist()
            if kind == "S":
                fits["T_S"] = fitted["T"].tolist()
        fits["C_exact"] = self.saved["corpora.json"][tid]["tables"]["C"]
        p = {
            arm: np.diff(table, prepend=0, axis=1) / 24000
            for arm, table in fits.items()
        }
        record.update(
            counts=counts,
            tables=fits,
            fit=diagnostics,
            table_hashes={arm: validate_table(table) for arm, table in fits.items()},
            row_entropy={
                arm: (-np.sum(q * np.log(q), axis=1)).tolist() for arm, q in p.items()
            },
            fit_seconds=time.monotonic() - tick,
        )
        self.save_state()
        print(
            json.dumps(
                dict(stage="fit", corpus=tid, elapsed=time.monotonic() - self.started)
            ),
            flush=True,
        )

    def save_state(self):
        write_json(self.out, "corpora.json", self.corpora)
        write_json(
            self.out,
            "freeze.json",
            dict(
                method_hash=self.config["method_hash"],
                bank_sha256=BANK_SHA,
                schedule_hash=digest(self.schedule),
                fitted_table_hashes={
                    t: c["table_hashes"]
                    for t, c in self.corpora.items()
                    if "table_hashes" in c
                },
                smoke_only=self.args.smoke,
                complete=not self.args.smoke and self.completed_pairs == 8,
            ),
        )
        write_json(
            self.out,
            "progress.json",
            dict(
                completed_pairs=self.completed_pairs,
                stop_kind=self.stop_kind,
                stop_reason=self.stop_reason,
            ),
        )
        write_json(self.out, "validation.json", self.validation)

    def run(self):
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        try:
            for pair in self.config["pair_order"]:
                for tid in pair:
                    self.collect(tid)
                self.jobs(
                    [
                        r
                        for r in self.schedule
                        if r["phase"] == "training" and r["corpus"] in pair
                    ],
                    f"training:{pair[0]}+{pair[1]}",
                )
                self.completed_pairs += 1
                self.save_state()
                print(
                    json.dumps(
                        dict(
                            stage="pair_complete",
                            pair=pair,
                            elapsed=time.monotonic() - self.started,
                        )
                    ),
                    flush=True,
                )
        except TimeoutError as error:
            self.stop_kind, self.stop_reason = "timeout", str(error)
        except Exception as error:
            self.stop_kind, self.stop_reason = (
                "error",
                f"{type(error).__name__}: {error}",
            )
        finally:
            self.pool.terminate()
            self.pool.join()
        self.validation.update(
            passed=self.stop_kind != "error",
            completed_pairs=self.completed_pairs,
            full_roster_complete=self.completed_pairs == self.nc,
        )
        self.save_state()
        from experiments.chem_tape.partial_program_report import (
            make_report,
            save_report,
        )

        tick = time.monotonic()
        report = make_report(
            self.rows,
            self.corpora,
            self.config,
            self.completed_pairs,
            self.stop_kind,
            self.stop_reason,
            self.timings,
        )
        save_report(self.out, report, self.rows)
        self.timings["reporting"] = dict(wall_seconds=time.monotonic() - tick)
        self.timings["total"] = dict(wall_seconds=time.monotonic() - self.started)
        write_json(self.out, "timing.json", self.timings)
        return int(self.stop_kind == "error")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--deadline-seconds", type=int, default=14220)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 120:
        ap.error("positive workers and deadline above120 required")
    return Runner(args).run()


if __name__ == "__main__":
    raise SystemExit(main())
