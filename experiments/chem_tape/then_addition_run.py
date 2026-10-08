"""1548 frozen C/T scoring: fresh then-addition F and development holdout D."""

import argparse
from collections import defaultdict
import gzip
import hashlib
import importlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

from experiments.chem_tape.comparison_gate_bank import (
    BANK_SHA as V1_SHA,
    TRAINING,
    digest,
    load_training,
)
from experiments.chem_tape.comparison_gate_run import Runner as TrainingRunner, CAP
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.crossed_learning_run import G4_HASH
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.solver_corpus_fit import validate_table
from experiments.chem_tape import then_addition_bank as fresh

BASE = 202610081548
SOURCE = Path(__file__).with_name("data") / "comparison_gate_1246_frozen"
PROVENANCE_SHA = "a8402465d255a33d45df122e8154de0619a999406471b7a8cb07557c3205b4a5"


def frozen_source(path=SOURCE):
    raw = (path / "provenance.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != PROVENANCE_SHA:
        raise ValueError("source provenance SHA mismatch")
    provenance = json.loads(raw)
    saved = {}
    for name, sha in provenance["sha256"].items():
        data = (
            gzip.decompress((path / (name + ".gz")).read_bytes())
            if name == "search.jsonl"
            else (path / name).read_bytes()
        )
        if hashlib.sha256(data).hexdigest() != sha:
            raise ValueError(f"frozen source SHA mismatch: {name}")
        saved[name] = (
            [json.loads(line) for line in data.splitlines()]
            if name == "search.jsonl"
            else json.loads(data)
        )
    config, freeze = saved["config.json"], saved["freeze.json"]
    v1, _ = load_training()
    corpora = saved["corpora.json"]
    ids = {f"{f}{k + 1}" for f in TRAINING for k in range(8)}
    if (
        not freeze["complete"]
        or freeze["smoke_only"]
        or config["smoke_only"]
        or freeze["bank_sha256"] != V1_SHA
        or set(corpora) != ids
        or freeze["split_hash"] != v1["split_hash"]
        or digest(saved["schedule.json"]) != freeze["schedule_hash"]
        or digest(config["method"]) != freeze["method_hash"]
        or config["method_hash"] != freeze["method_hash"]
    ):
        raise ValueError("source freeze incomplete or inconsistent")
    for tid, record in corpora.items():
        if record["family"] != tid[:2] or record["index"] != int(tid[2:]) - 1:
            raise ValueError("source corpus identity mismatch")
        for arm in ("C", "T", "K"):
            sha = validate_table(record["tables"][arm])
            if (
                sha != freeze["fitted_table_hashes"][tid][arm]
                or sha != record["fit"]["hashes"][arm]
            ):
                raise ValueError("frozen fitted table mismatch")
    if any(r["phase"] == "holdout" for r in saved["search.jsonl"]):
        raise ValueError("source holdout already scored")
    return saved, provenance


def check_seeds(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["seed"]].append(row)
    for group in groups.values():
        if len(group) == 1 and group[0]["arm"] == "G4":
            continue
        if (
            len(group) != 2
            or {r["arm"] for r in group} != {"C", "T"}
            or {k: v for k, v in group[0].items() if k != "arm"}
            != {k: v for k, v in group[1].items() if k != "arm"}
        ):
            raise ValueError("seed collision outside C/T pair")


def fresh_schedule(ids, base=BASE):
    # 16 cells need a larger corpus stride than 1246's eight-cell roster.
    rows = []
    for family in TRAINING:
        for k in range(8):
            for c, cid in enumerate(ids):
                for s in range(8):
                    seed = (
                        base
                        + 6000000
                        + (family == "PA") * 100000
                        + k * 10000
                        + c * 200
                        + s
                    )
                    for arm in ("C", "T"):
                        rows.append(
                            dict(
                                phase="fresh",
                                family=family,
                                corpus=f"{family}{k + 1}",
                                cell=cid,
                                arm=arm,
                                seed=seed,
                            )
                        )
    for c, cid in enumerate(ids):
        for s in range(16):
            rows.append(
                dict(
                    phase="fresh",
                    family="TA",
                    corpus="G4",
                    cell=cid,
                    arm="G4",
                    seed=base + 7000000 + c * 200 + s,
                )
            )
    check_seeds(rows)
    return rows


def smoke_schedule():
    rows = []
    base = BASE + 100000000
    for family, ids in TRAINING.items():
        for c, cid in enumerate(ids):
            for s in range(2):
                for arm in ("C", "T", "G4"):
                    seed = (
                        base
                        + (7000000 if arm == "G4" else 6000000)
                        + (family == "PA") * 100000
                        + c * 200
                        + s
                    )
                    rows.append(
                        dict(
                            phase="smoke",
                            family=family,
                            corpus="G4" if arm == "G4" else family + "1",
                            cell=cid,
                            arm=arm,
                            seed=seed,
                        )
                    )
    check_seeds(rows)
    return rows


class Runner(TrainingRunner):
    # Reuse the existing validated batching/checkpoint search path; never collect/refit.
    def __init__(self, args):
        self.args = args
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("use a fresh RUN_DIR")
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 120
        self.bank, training = load_training()
        self.fresh_bank, fresh_cells = fresh.load()
        self.saved, self.provenance = frozen_source()
        self.corpora = self.saved["corpora.json"]
        self.inputs = self.bank["inputs"]
        self.g4 = tables()["G4"]
        if validate_table(self.g4) != G4_HASH:
            raise ValueError("G4 hash mismatch")
        f = fresh_schedule(self.fresh_bank["selected_ids"])
        d = [r for r in self.saved["schedule.json"] if r["phase"] == "holdout"]
        if len(d) != 4352:
            raise ValueError("source D roster count mismatch")
        check_seeds(d + f)
        if {r["seed"] for r in f + d} & {r["seed"] for r in self.saved["search.jsonl"]}:
            raise ValueError("target seeds overlap source searches")
        schedules = dict(F=f, D=d)
        self.schedule = smoke_schedule() if args.smoke else schedules[args.row]
        by = {c["id"]: dict(id=c["id"], labels=c["labels"]) for c in self.bank["cells"]}
        self.cells = (
            training
            if args.smoke
            else fresh_cells
            if args.row == "F"
            else {
                cid: by[cid] for cid in sum(self.bank["split"]["holdouts"].values(), [])
            }
        )
        self.rows, self.timings = [], {}
        self.completed_pairs = 0
        self.g4_complete = False
        self.stop_reason, self.stop_kind = None, None
        self.nc = 1 if args.smoke else 8
        self.validation = dict(
            passed=False,
            solver_verifications=0,
            pairing_checks=0,
            source_tables_checked=48,
            source_sha256=self.provenance["sha256"],
            target_searches=0,
            training_only_smoke=args.smoke,
        )
        sources = [
            "then_addition_bank.py",
            "then_addition_run.py",
            "then_addition_report.py",
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
        hashes = {
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
            hashes[name] = hashlib.sha256(
                Path(importlib.import_module(name).__file__).read_bytes()
            ).hexdigest()
        method = dict(
            source_provenance_sha256=PROVENANCE_SHA,
            fresh_bank_sha256=fresh.BANK_SHA,
            v1_bank_sha256=V1_SHA,
            source_table_hashes=self.saved["freeze.json"]["fitted_table_hashes"],
            code_hashes=hashes,
            source_method=self.saved["config.json"]["method"],
            cap=CAP,
            population=256,
            tape_length=32,
            cases=64,
            K_scored=False,
            F_seed_base=BASE,
            F_seed_rule="base+phase*1000000+(family==PA)*100000+corpus_index*10000+cell_index*200+seed_index; phases 6/7",
            D_seed_rule="exact source holdout roster, unchanged",
            schedule_hashes={r: digest(s) for r, s in schedules.items()},
            endpoint="exp(mean_corpus(mean_cell_seed(log(cost_T)-log(cost_C))))",
            unsolved_primary="2*cap",
            sensitivity="1*cap",
            interval="95% t over independent balanced corpora",
            decision_precedence=[
                "incomplete or error: no decision",
                "both solve rates<0.25: capped endpoint interpretation",
                "LB>1: resolved relative gain; UB<1.10 also means below 10%",
                "UB<1.10: boundary on selected bank, consistent with shape specificity",
                "otherwise unresolved",
            ],
            prefix="fixed BE1/PA1..BE8/PA8, minimum 6 pairs; no fallback after error",
            scope="selected then-addition bank; C vs restricted token-fit procedure, no isolated token-order inference",
        )
        self.config = dict(
            task="2026-10-08-1548",
            row=args.row,
            smoke_only=args.smoke,
            arguments=vars(args),
            method=method,
            method_hash=digest(method),
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            nc=self.nc,
            workers=args.workers,
            pair_order=[[f"BE{k + 1}", f"PA{k + 1}"] for k in range(self.nc)],
        )
        write_json(self.out, "config.json", self.config)
        write_json(
            self.out,
            "bank.json",
            self.fresh_bank if args.row == "F" and not args.smoke else self.bank,
        )
        write_json(self.out, "schedule.json", self.schedule)
        write_json(self.out, "target_schedules.json", schedules)
        write_json(self.out, "source_provenance.json", self.provenance)
        (self.out / "search.jsonl").touch()
        self.save_state()

    def envelope(self, row):
        if row not in self.schedule or row["cell"] not in self.cells:
            raise ValueError("search outside frozen roster")
        cell = self.cells[row["cell"]]
        if set(cell) != {"id", "labels"}:
            raise ValueError("program in search payload")
        table = (
            self.g4
            if row["arm"] == "G4"
            else self.corpora[row["corpus"]]["tables"][row["arm"]]
        )
        return (
            (
                cell,
                row["arm"],
                table,
                row["seed"],
                CAP,
                256,
                self.inputs,
                self.bank["alphabet"],
            ),
            {k: row[k] for k in ("phase", "family", "corpus")},
            False,
        )

    def save_state(self):
        write_json(
            self.out,
            "freeze.json",
            dict(
                method_hash=self.config["method_hash"],
                schedule_hash=digest(self.schedule),
                target_schedule_hashes=self.config["method"]["schedule_hashes"],
                fresh_bank_sha256=fresh.BANK_SHA,
                source_sha256=self.provenance["sha256"],
                fitted_table_hashes=self.saved["freeze.json"]["fitted_table_hashes"],
                complete=True,
                frozen_before_scoring=True,
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
            self.jobs([r for r in self.schedule if r["arm"] == "G4"], "G4")
            self.g4_complete = True
            self.save_state()
            for pair in self.config["pair_order"]:
                self.jobs(
                    [r for r in self.schedule if r["corpus"] in pair], "+".join(pair)
                )
                self.completed_pairs += 1
                self.save_state()
                print(
                    json.dumps(
                        dict(
                            pair=pair,
                            completed_pairs=self.completed_pairs,
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
            target_searches=0 if self.args.smoke else len(self.rows),
        )
        self.save_state()
        from experiments.chem_tape.then_addition_report import make_report, save_report

        tick = time.monotonic()
        report = make_report(
            self.rows,
            self.schedule,
            self.saved["search.jsonl"],
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
        return int(self.stop_kind == "error")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--row", choices=("F", "D"), required=True)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--deadline-seconds", type=int, default=14160)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 120:
        ap.error("positive workers and deadline above reporting reserve required")
    return Runner(args).run()


if __name__ == "__main__":
    raise SystemExit(main())
