"""2229: frozen holdout mode of crossed learning; no adaptation is permitted."""

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

from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder, search
from experiments.chem_tape.crossed_learning_run import (
    BANK_SHA,
    DEFAULT_BANK,
    G4_HASH,
    HOLDOUTS,
    TRAINING,
    load_bank,
)
from experiments.chem_tape.crossed_holdout_report import (
    gain_matrix,
    make_report,
    save_report,
)
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.map_learning import table_for

SOURCE = Path(__file__).with_name("data") / "crossed_1723"
SOURCE_HASHES = {
    "config.json": "f345d3e277569cd3e380b98dbd1cfd362b9796bd3e850f1cc135209f258156b5",
    "trajectories.json": "94138e35c6aa36b583704a69e83cab8437f11a5c55f7e3c1696fe03fc5a481b3",
    "fresh_scores.json": "bbca73201e88acb5620d171841dfe779a735f0408d4d7663bdb102e972e1aa96",
}
SOURCE_COMMIT = "db96645f54b72e890f55d9236dbeec85c41df256"


def frozen_source(source):
    """Check the original bytes before any evaluation, including compressed rows."""
    data = {}
    for name, sha in SOURCE_HASHES.items():
        path = Path(source) / (name + ".gz" if name == "fresh_scores.json" else name)
        raw = (
            gzip.decompress(path.read_bytes())
            if path.suffix == ".gz"
            else path.read_bytes()
        )
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError(f"stage-1 source SHA256 mismatch: {name}")
        data[name] = json.loads(raw)
    config, trajectories = data["config.json"], data["trajectories.json"]
    if (
        config["git_commit"] != SOURCE_COMMIT
        or config["task"] != "2026-10-06-1723"
        or config["smoke_only"]
        or config["probe_only"]
        or config["training"] != TRAINING
        or config["excluded_holdouts"] != HOLDOUTS
        or config["bank_sha256"] != BANK_SHA
        or config["g4_hash"] != G4_HASH
        or config["alphabet"] != ALPHABET
        or config["domain"] != "D1331"
        or config["fresh_cap"] != 524288
        or config["fresh_seeds"] != list(range(1723300, 1723350))
    ):
        raise ValueError("wrong stage-1 configuration")
    expected = [f"{f}{k + 1}" for f in ("BE", "PA") for k in range(10)]
    if set(trajectories) != set(expected):
        raise ValueError("all and only 20 frozen trajectories required")
    g4 = tables()["G4"]
    if Decoder(g4).hash() != G4_HASH:
        raise ValueError("G4 hash mismatch")
    for tid in expected:
        tr = trajectories[tid]
        family, k = tid[:2], int(tid[2:]) - 1
        if (
            tr["trajectory"] != tid
            or tr["family"] != family
            or tr["seed"] != 1723200 + 2 * k + (family == "PA")
        ):
            raise ValueError(f"trajectory identity mismatch: {tid}")
        table = np.asarray(tr["table"])
        if table.shape != (25, 24) or table.dtype.kind not in "iu":
            raise ValueError(f"invalid saved integer table: {tid}")
        vector = np.asarray(tr["vector"], dtype=float)
        if vector.shape != (24,) or not np.all(np.isfinite(vector)):
            raise ValueError(f"invalid frozen vector: {tid}")
        # Reconstruction is deterministic validation, never an outer learning call.
        if not np.array_equal(table_for("M", vector, {"G": g4}), table):
            raise ValueError(f"vector/table mismatch: {tid}")
        if Decoder(table).hash() != tr["table_hash"]:
            raise ValueError(f"saved map hash mismatch: {tid}")
    trajectories = {tid: trajectories[tid] for tid in expected}
    gains, validation = gain_matrix(
        data["fresh_scores.json"],
        trajectories,
        sum(TRAINING.values(), []),
        config["fresh_seeds"],
        config["fresh_cap"],
        G4_HASH,
        "fresh_training",
    )
    if not validation["passed"]:
        raise ValueError(f"stage-1 fresh rows invalid: {validation}")
    own_training = {
        tid: float(np.mean([gains[tid][cid] for cid in TRAINING[tr["family"]]]))
        for tid, tr in trajectories.items()
    }
    return trajectories, g4, own_training, validation


class Runner:
    def __init__(self, args):
        self.args = args
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if any(self.out.iterdir()):
            # Queue runner installs its logs before launch; only our artifacts matter.
            if any(
                (self.out / name).exists()
                for name in ("config.json", "search.jsonl", "result.json")
            ):
                raise ValueError("Use a fresh RUN_DIR")
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds
        self.work_deadline = self.deadline - 180
        self.trajectories, g4, self.training_gains, source_validation = frozen_source(
            args.source
        )
        bank, _ = load_bank(args.bank)
        raw_cells = {c["id"]: c for c in bank["cells"]}
        self.cells = {
            cid: {"id": cid, "labels": raw_cells[cid]["labels"]}
            for cid in sum(HOLDOUTS.values(), [])
        }
        self.inputs = inputs_for("D1331")
        self.maps = {
            "G4": g4,
            **{tid: np.asarray(tr["table"]) for tid, tr in self.trajectories.items()},
        }
        self.cap = 8192 if args.smoke else 524288
        seeds = (
            list(range(2229500, 2229505))
            if args.probe
            else list(range(2229400, 2229402))
            if args.smoke
            else list(range(2229000, 2229400))
        )
        self.config = dict(
            task="2026-10-06-2229",
            mode="frozen_holdout",
            arguments=vars(args),
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            source_commit=SOURCE_COMMIT,
            source_sha256=SOURCE_HASHES,
            bank_sha256=BANK_SHA,
            g4_hash=G4_HASH,
            alphabet=ALPHABET,
            domain="D1331",
            holdouts=HOLDOUTS,
            excluded_training=TRAINING,
            map_hashes={arm: Decoder(table).hash() for arm, table in self.maps.items()},
            trajectories_per_family=10,
            learning_permitted=False,
            learning_calls=0,
            fresh_cap=self.cap,
            fresh_seeds=seeds,
            population=256,
            length=32,
            crossover=0.7,
            mutation=0.03,
            training_cases=64,
            exact_cases=1331,
            allele_range=24000,
            unsolved_cost="cap",
            workers=args.workers,
            internal_deadline_seconds=args.deadline_seconds,
            reporting_reserve_seconds=180,
            expected_searches=len(self.maps) * len(self.cells) * len(seeds),
            smoke_only=args.smoke,
            probe_only=args.probe,
            preparation_diagnostics=dict(
                initial_smoke=dict(
                    seeds=[2229000, 2229001],
                    cap=8192,
                    note="Initial infrastructure smoke exposed two evaluation seeds at reduced cap; no adaptation/selection or data reuse. Subsequent smoke uses a separate block.",
                ),
                final_smoke=dict(seeds=[2229400, 2229401], cap=8192),
                feasibility_probe=dict(seeds=list(range(2229500, 2229505)), cap=524288),
            ),
        )
        write_json(self.out, "config.json", self.config)
        write_json(self.out, "bank.json", bank)
        write_json(self.out, "trajectories.json", self.trajectories)
        write_json(self.out, "training_gains.json", self.training_gains)
        self.validation = dict(
            source_hashes_verified=True,
            map_hashes_verified=True,
            vector_tables_verified=True,
            bank_labels_verified=True,
            training_holdout_disjoint=True,
            no_learning=True,
            search_payload_fields=["id", "labels"],
            source_training_rows=source_validation,
        )
        write_json(self.out, "validation.json", self.validation)
        self.rows, self.stop_reason = [], None

    def job(self, cid, arm, seed):
        if (
            cid not in self.cells
            or arm not in self.maps
            or seed not in self.config["fresh_seeds"]
        ):
            raise ValueError("non-holdout or unfrozen job rejected")
        if set(self.cells[cid]) != {"id", "labels"}:
            raise ValueError("solver information in search payload")
        return (
            self.cells[cid],
            arm,
            self.maps[arm],
            seed,
            self.cap,
            256,
            self.inputs,
            ALPHABET,
        )

    def run(self):
        jobs = [
            self.job(cid, arm, seed)
            for arm in self.maps
            for cid in self.cells
            for seed in self.config["fresh_seeds"]
        ]
        pool = mp.get_context("spawn").Pool(self.args.workers)
        try:
            with (self.out / "search.jsonl").open("a", buffering=1) as stream:

                def save(row):
                    row["phase"] = "fresh_holdout"
                    self.rows.append(row)
                    stream.write(json.dumps(row, allow_nan=False) + "\n")

                if not run_jobs(pool, search, jobs, self.work_deadline, save):
                    self.stop_reason = (
                        "internal deadline; partial rows preserved, no subset inference"
                    )
        except Exception as error:
            self.stop_reason = f"search failed: {type(error).__name__}: {error}"
        finally:
            pool.terminate()
            pool.join()
        write_json(self.out, "fresh_scores.json", self.rows)
        report = make_report(
            self.rows,
            self.trajectories,
            self.config,
            self.training_gains,
            self.stop_reason,
        )
        seconds = [r["seconds"] for r in self.rows]
        report["runtime"] = dict(
            wall_seconds_before_reporting=time.monotonic() - self.started,
            sum_search_seconds=sum(seconds),
            mean_search_seconds=float(np.mean(seconds)) if seconds else None,
            projected_full_queue_minutes_at_observed_rate=(
                25200 * np.mean(seconds) / self.args.workers / 60 + 3
            )
            if seconds
            else None,
        )
        self.validation.update(
            job_rows=report["validation"],
            g4_solve_gate=report["g4_solve_gate"],
            passed=report["complete"]
            and all(v["passed"] for v in report["g4_solve_gate"].values())
            and not self.stop_reason,
        )
        write_json(self.out, "validation.json", self.validation)
        write_json(self.out, "result.json", report)
        save_report(self.out, report, self.rows, HOLDOUTS)
        report["runtime"]["wall_seconds"] = time.monotonic() - self.started
        write_json(self.out, "result.json", report)
        print(
            json.dumps(
                dict(
                    rows=len(self.rows),
                    outcome=report["outcome"],
                    runtime=report["runtime"],
                )
            )
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", default=str(DEFAULT_BANK))
    parser.add_argument("--source", default=str(SOURCE))
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=6300)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--smoke", action="store_true")
    group.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 180:
        parser.error(
            "workers must be positive and deadline must exceed reporting reserve"
        )
    Runner(args).run()


if __name__ == "__main__":
    main()
