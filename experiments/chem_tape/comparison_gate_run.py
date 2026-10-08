"""1246 training-only corpus fits; fixed balanced prefix, protected holdout freeze."""

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
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.crossed_learning_run import G4_HASH
from experiments.chem_tape.solver_corpus_fit import (
    seed_for,
    transition_counts,
    fit,
    validate_table,
)
from experiments.chem_tape.solver_corpus_run import observed_search

BASE = 202610081246
CAP = 524288


def roster(bank, base=BASE, nc=8, collect_n=48, fresh_n=16, g4_n=32):
    """Metadata only: all seeds, including the unexecuted stage-2 roster."""
    rows = []
    for family, cells in TRAINING.items():
        for k in range(nc):
            tid = f"{family}{k + 1}"
            for phase, phase_id, ids, count, arms in (
                ("collection", 0, cells, collect_n, ("G4",)),
                ("training", 1, cells, fresh_n, ("C", "T")),
                (
                    "holdout",
                    2,
                    sum(bank["split"]["holdouts"].values(), []),
                    16,
                    ("C", "T"),
                ),
            ):
                for c, cid in enumerate(ids):
                    for s in range(count):
                        for arm in arms:
                            rows.append(
                                dict(
                                    phase=phase,
                                    family=family,
                                    corpus=tid,
                                    cell=cid,
                                    arm=arm,
                                    seed=seed_for(phase_id, family, k, c, s, base),
                                )
                            )
        for phase, phase_id, ids, count in (
            ("training", 3, cells, g4_n),
            ("holdout", 5, bank["split"]["holdouts"][family], 32),
        ):
            for c, cid in enumerate(ids):
                for s in range(count):
                    rows.append(
                        dict(
                            phase=phase,
                            family=family,
                            corpus="G4",
                            cell=cid,
                            arm="G4",
                            seed=seed_for(phase_id, family, 0, c, s, base),
                        )
                    )
    # Only the predeclared C/T pair may share a seed. This checks all phases too.
    by_seed = {}
    for row in rows:
        group = by_seed.setdefault(row["seed"], [])
        group.append(row)
    for group in by_seed.values():
        if len(group) == 1:
            if group[0]["arm"] != "G4":
                raise ValueError("unpaired fitted-arm seed")
        elif (
            len(group) != 2
            or {r["arm"] for r in group} != {"C", "T"}
            or any(
                {k: v for k, v in r.items() if k != "arm"}
                != {k: v for k, v in group[0].items() if k != "arm"}
                for r in group
            )
        ):
            raise ValueError("seed collision outside paired C/T")
    return rows


def corpus_diagnostics(rows, cells):
    return {
        cid: dict(
            attempts=sum(r["cell"] == cid for r in rows),
            solved=sum(r["cell"] == cid and r["solved"] for r in rows),
            distinct_tapes=len(
                {tuple(r["solver"]) for r in rows if r["cell"] == cid and r["solved"]}
            ),
        )
        for cid in cells
    }


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
        self.nc = 1 if args.smoke else 8
        self.collect_n = 8 if args.smoke else 48
        self.fresh_n = 2 if args.smoke else 16
        self.g4_n = 2 if args.smoke else 32
        self.base = BASE + (100000000 if args.smoke else 0)
        self.schedule = roster(
            self.bank, self.base, self.nc, self.collect_n, self.fresh_n, self.g4_n
        )
        self.rows, self.corpora, self.timings = [], {}, {}
        self.completed_pairs = 0
        self.g4_complete = False
        self.stop_reason, self.stop_kind = None, None
        self.validation = dict(
            passed=False,
            bank_sha256=BANK_SHA,
            g4_hash=G4_HASH,
            solver_verifications=0,
            pairing_checks=0,
            holdout_searches=0,
        )
        sources = [
            "comparison_gate_bank.py",
            "comparison_gate_run.py",
            "comparison_gate_report.py",
            "solver_corpus_fit.py",
            "solver_corpus_run.py",
            "composition_search.py",
            "composition_run.py",
            "composition_bank.py",
            "assembly_bank.py",
            "four_reducer_bank.py",
            "four_reducer_maps.py",
            "map_learning.py",
        ]
        code_hashes = {
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_bytes()
            ).hexdigest()
            for name in sources
        }
        for name in (
            "_folding_rust._folding_rust",
            "folding_evolution.chem_tape.evolve",
            "folding_evolution.chem_tape.executor",
            "folding_evolution.chem_tape.alphabet",
        ):
            code_hashes[name] = hashlib.sha256(
                Path(importlib.import_module(name).__file__).read_bytes()
            ).hexdigest()
        method = dict(
            bank_sha256=BANK_SHA,
            split_hash=self.bank["split_hash"],
            inputs_hash=self.bank["inputs_hash"],
            code_hashes=code_hashes,
            g4_hash=G4_HASH,
            cap=CAP,
            population=256,
            tape_length=32,
            training_cases=64,
            alphabet=ALPHABET,
            crossover=0.7,
            mutation=0.03,
            elite=2,
            initialization="fresh random allele population",
            alpha=50,
            cell_transition_weight=1600,
            T_multipliers=24,
            multiplier_bounds=[1 / 16, 16],
            minimum_count=250,
            allele_range=24000,
            K_steps=400,
            K_step=0.7,
            K_tolerance=0.001,
            K_scored=False,
            cell_yield_floor=1,
            continuation_pooled_yield_floor=0.4,
            endpoint="exp(mean_corpus(mean_cell_seed(log(cost_T)-log(cost_C))))",
            interval="two-sided 95% t across independent corpus contrasts; equal family weights",
            unsolved_primary="2*cap",
            unsolved_sensitivity="1*cap",
            decision_precedence=[
                "LB>1 and pooled_yield>=0.4: recommend stage 2",
                "LB>1 and pooled_yield<0.4: acquisition obstacle, strategy",
                "UB<1.10: gain bounded below 10%, no stage 2 for C/T",
                "otherwise: unresolved, price additional corpora",
            ],
            scope="C versus restricted T fitting procedure; changed emitted frequencies not controlled",
            timeout_prefix="BE1/PA1 through BE8/PA8; >=6 complete initial pairs; no error fallback",
            stage2=dict(
                corpora_per_family=8,
                holdouts=self.bank["split"]["holdouts"],
                seeds_per_cell_table=16,
                G4_seeds_per_holdout=32,
                searches=4352,
                K_scored=False,
                endpoint="same corpus statistic over all eight holdouts",
                interval="95% t across 16 corpus contrasts",
                unsolved_primary="2*cap",
                sensitivity="1*cap and per-training-family",
                allocation="not authorised in this stage",
            ),
        )
        self.config = dict(
            task="2026-10-08-1246",
            arguments=vars(args),
            smoke_only=args.smoke,
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            method=method,
            method_hash=digest(method),
            training=TRAINING,
            seed_base=self.base,
            seed_rule="base+phase*1000000+(family==PA)*100000+corpus_index*2000+cell_index*200+seed_index",
            nc=self.nc,
            collect_n=self.collect_n,
            fresh_n=self.fresh_n,
            g4_n=self.g4_n,
            workers=args.workers,
            pair_order=[[f"BE{k + 1}", f"PA{k + 1}"] for k in range(self.nc)],
        )
        write_json(self.out, "config.json", self.config)
        write_json(self.out, "bank.json", self.bank)
        write_json(self.out, "schedule.json", self.schedule)
        self.save_state()

    def envelope(self, row):
        if (
            row["phase"] not in ("collection", "training")
            or row["cell"] not in TRAINING[row["family"]]
        ):
            raise ValueError("holdout leakage / invalid training phase")
        cell = self.cells[row["cell"]]
        if set(cell) != {"id", "labels"}:
            raise ValueError("program in search payload")
        table = (
            self.g4
            if row["arm"] == "G4"
            else self.corpora[row["corpus"]]["tables"][row["arm"]]
        )
        return (
            (cell, row["arm"], table, row["seed"], CAP, 256, self.inputs, ALPHABET),
            {k: row[k] for k in ("phase", "family", "corpus")},
            row["phase"] == "collection",
        )

    def jobs(self, roster_rows, name):
        envelopes = [self.envelope(r) for r in roster_rows]
        expected = {
            (
                r["phase"],
                r["family"],
                r["corpus"],
                r["cell"],
                r["arm"],
                r["seed"],
            ): hashlib.sha256(np.asarray(j[2], dtype="<i8").tobytes()).hexdigest()
            for r, (j, _, _) in zip(roster_rows, envelopes)
        }
        if len(expected) != len(envelopes):
            raise ValueError("duplicate jobs")
        rows, pairing = [], {}
        tick = time.monotonic()
        with (self.out / "search.jsonl").open("a", buffering=1) as stream:

            def save(row):
                key = tuple(
                    row[k] for k in ("phase", "family", "corpus", "cell", "arm", "seed")
                )
                if expected.pop(key) != row["table_hash"]:
                    raise ValueError("table hash mismatch")
                if (
                    row["cap"] != CAP
                    or row["pop_size"] != 256
                    or not 0 < row["evaluations"] <= CAP
                    or row["evaluations"] % 256
                    or (not row["solved"] and row["evaluations"] != CAP)
                ):
                    raise ValueError("invalid evaluation budget")
                indices = (
                    np.random.default_rng([row["seed"], 0])
                    .choice(1331, 64, replace=False)
                    .tolist()
                )
                if indices != row["training_indices"]:
                    raise ValueError("case seed mismatch")
                pkey = key[:4] + (row["seed"],)
                if pkey in pairing:
                    if row["training_indices"] != pairing[pkey]:
                        raise ValueError("case pairing mismatch")
                    self.validation["pairing_checks"] += 1
                pairing[pkey] = row["training_indices"]
                self.validation["solver_verifications"] += int(
                    row["phase"] == "collection" and row["solved"]
                )
                rows.append(row)
                self.rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")

            try:
                complete = run_jobs(
                    self.pool, observed_search, envelopes, self.deadline, save
                )
            finally:
                self.timings[name] = dict(
                    wall_seconds=time.monotonic() - tick,
                    worker_seconds=sum(
                        r["seconds"] + r.get("verification_seconds", 0) for r in rows
                    ),
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
        diagnostics = corpus_diagnostics(rows, TRAINING[family])
        record = dict(
            family=family,
            index=int(tid[2:]) - 1,
            cells=diagnostics,
            yields={c: d["solved"] for c, d in diagnostics.items()},
            collection_evaluations=sum(r["evaluations"] for r in rows),
            collection_worker_seconds=sum(
                r["seconds"] + r.get("verification_seconds", 0) for r in rows
            ),
            verification_seconds=sum(r.get("verification_seconds", 0) for r in rows),
        )
        self.corpora[tid] = record
        self.save_state()
        # The frozen estimator refuses empty cells; do not resample or omit them.
        counts, yields = transition_counts(rows, TRAINING[family])
        tick = time.monotonic()
        fitted, diagnostic = fit(counts)
        record.update(
            counts=counts.tolist(),
            tables={a: t.tolist() for a, t in fitted.items()},
            fit=diagnostic,
            fit_seconds=time.monotonic() - tick,
        )
        self.save_state()
        print(
            json.dumps(
                dict(
                    stage="fit",
                    corpus=tid,
                    yields=yields,
                    distinct_tapes={
                        c: d["distinct_tapes"] for c, d in diagnostics.items()
                    },
                    elapsed=time.monotonic() - self.started,
                )
            ),
            flush=True,
        )

    def save_state(self):
        write_json(self.out, "corpora.json", self.corpora)
        fitted = {
            tid: tr["fit"]["hashes"] for tid, tr in self.corpora.items() if "fit" in tr
        }
        write_json(
            self.out,
            "freeze.json",
            dict(
                method_hash=self.config["method_hash"],
                bank_sha256=BANK_SHA,
                split_hash=self.bank["split_hash"],
                schedule_hash=digest(self.schedule),
                stage2_searches_executed=0,
                fitted_table_hashes=fitted,
                complete=not self.args.smoke and len(fitted) == 16,
                smoke_only=self.args.smoke,
            ),
        )
        write_json(
            self.out,
            "progress.json",
            dict(
                completed_pairs=self.completed_pairs,
                g4_complete=self.g4_complete,
                stop_kind=self.stop_kind,
                stop_reason=self.stop_reason,
            ),
        )
        write_json(self.out, "validation.json", self.validation)

    def run(self):
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        try:
            self.jobs(
                [
                    r
                    for r in self.schedule
                    if r["phase"] == "training" and r["arm"] == "G4"
                ],
                "G4_training",
            )
            self.g4_complete = True
            self.save_state()
            for pair in self.config["pair_order"]:
                for tid in pair:
                    self.collect(tid)
                # Both maps frozen before paired scoring; no performance-based ordering.
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
            g4_complete=self.g4_complete,
            completed_pairs=self.completed_pairs,
            full_roster_complete=self.completed_pairs == self.nc,
        )
        self.save_state()
        from experiments.chem_tape.comparison_gate_report import (
            make_report,
            save_report,
        )

        tick = time.monotonic()
        report = make_report(
            self.rows,
            self.corpora,
            self.config,
            self.completed_pairs,
            self.g4_complete,
            self.stop_kind,
            self.stop_reason,
            self.timings,
        )
        save_report(self.out, report, self.rows)
        self.timings["reporting"] = dict(wall_seconds=time.monotonic() - tick)
        self.timings["total"] = dict(wall_seconds=time.monotonic() - self.started)
        write_json(self.out, "timing.json", self.timings)
        return 1 if self.stop_kind == "error" else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--deadline-seconds", type=int, default=10680)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 120:
        ap.error("positive workers and a deadline above reporting reserve required")
    return Runner(args).run()


if __name__ == "__main__":
    raise SystemExit(main())
