"""2303 frozen sparse acquisition transfer; prepare gates precede full scoring.

All search execution reuses sparse_feedback_run.execute (unchanged F operator).
--smoke uses a diagnostic cap and cannot create an admitted scoring handoff.
"""

import argparse
from collections import defaultdict
from datetime import datetime
import gzip
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import digest, load_training
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.fragment_operator import validate_edits
from experiments.chem_tape.fragment_reuse_run import pinned_history
from experiments.chem_tape.fragment_run import CORPORA, implementation_hashes
from experiments.chem_tape.small_source_run import (
    references,
    SCIENTIFIC_FIELDS,
    REPLAY_FIELDS,
)
from experiments.chem_tape.sparse_feedback_run import (
    execute as sparse_execute,
    audit_empty_fallback,
)
from experiments.chem_tape.solver_corpus_fit import validate_table
from experiments.chem_tape.then_addition_run import frozen_source
from experiments.chem_tape.then_addition_bank import load as load_ta
from experiments.chem_tape.two_sum_bank import load, BANK_SHA
from experiments.chem_tape.two_sum_report import report

DATA = Path(__file__).with_name("data") / "two_sum_2303_methods"
METHOD_SHA = "c4b49eb3e6256bda5c064bb2532227f7b544e3e1d0cbd26bfdcca4a25e71d697"
BASE = 206610092303
CAP = 524288
ARMS = ("A8", "S8", "full_F")
DEADLINE = "2026-10-10T07:12:10+02:00"


def methods():
    raw = (DATA / "provenance.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != METHOD_SHA:
        raise ValueError("2033 method provenance changed")
    provenance = json.loads(raw)
    saved = {}
    for name, sha in provenance["sha256"].items():
        raw = gzip.decompress((DATA / (name + ".gz")).read_bytes())
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError("2033 artifact changed: " + name)
        saved[name] = json.loads(raw)
    b, p, f = (saved[n] for n in ("builds.json", "preparation.json", "freeze.json"))
    if (
        saved["metadata.json"]["status"] != "done"
        or not p["admitted"]
        or not saved["validation.json"]["passed"]
        or digest(b) != f["builds_hash"]
        or p["freeze"] != f
        or digest(p["admission"]) != f["admission_hash"]
        or set(b)
        != {
            f"{tid}|{block}|{arm}"
            for tid in CORPORA
            for block in range(4)
            for arm in ("A8", "S8")
        }
    ):
        raise ValueError("2033 incomplete method")
    for key, build in b.items():
        if (
            validate_table(build["table"]) != build["table_hash"]
            or key != f"{build['corpus']}|{build['block']}|{build['arm']}"
        ):
            raise ValueError("2033 decoder identity changed")
    return saved, provenance


def fitted_roster(ids, n, arms=ARMS, timing=False):
    return [
        dict(
            phase="timing" if timing else "two_sum",
            family=tid[:2],
            corpus=tid,
            cell=cid,
            block=si % 4,
            seed_ordinal=si,
            arm=arm,
            seed=BASE
            + (1000000 if timing else 0)
            + CORPORA.index(tid) * 10000
            + ci * 100
            + si,
        )
        for tid in (CORPORA[:2] if timing else CORPORA)
        for ci, cid in enumerate(ids)
        for si in range(n)
        for arm in arms
    ]


def g4_roster(ids, timing=False):
    return [
        dict(
            phase="timing" if timing else "two_sum",
            family="G4",
            corpus="G4",
            cell=cid,
            block=si % 4,
            seed_ordinal=si,
            arm="G4",
            seed=BASE + (2000000 if timing else 3000000) + ci * 100 + si,
        )
        for ci, cid in enumerate(ids)
        for si in range(4 if timing else 16)
    ]


def execute(envelope):
    job, meta, *rest = envelope
    row = sparse_execute((job, dict(meta, arm=job[1]), *rest))
    row["arm"] = meta["arm"]
    return row


def worker_seconds(row):
    return row["seconds"] + row.get("external_verification_seconds", 0)


def admission(rows, wall, elapsed, workers, finish_by):
    means = {
        a: float(np.mean([worker_seconds(r) for r in rows if r["arm"] == a]))
        for a in (*ARMS, "G4")
    }
    effective = min(workers, sum(map(worker_seconds, rows)) / wall)
    replay = sum(map(worker_seconds, rows)) * 1.15 / effective
    candidates = []
    remaining = finish_by - time.time()
    for n, arms in ((8, ARMS), (4, ARMS), (4, ("A8", "full_F"))):
        total = 16 * 16 * n * sum(means[a] for a in arms) + 256 * means["G4"]
        projected = 1.15 * total / effective
        with_reserve = projected + replay + 240
        candidates.append(
            dict(
                seeds=n,
                arms=list(arms),
                searches=16 * 16 * n * len(arms) + 256,
                projected_seconds=projected,
                with_reserve_seconds=with_reserve,
                fits=projected <= 9000
                and with_reserve <= 10680
                and with_reserve <= remaining,
            )
        )
    selected = next((c for c in candidates if c["fits"]), None)
    return dict(
        admitted=selected is not None and elapsed <= 2580,
        selected=selected,
        candidates=candidates,
        workers=workers,
        effective_workers=effective,
        mean_worker_seconds=means,
        timing_wall_seconds=wall,
        prepare_seconds=elapsed,
        replay_reserve_seconds=replay,
        report_reserve_seconds=240,
        finish_by=DEADLINE,
        remaining_seconds=remaining,
        rule="first 8/all,4/all,4/no-S8 with 1.15*projection<=150min; replay+240s<=score budget and actual deadline; prepare<=2580s",
        caveat="timing cells only; limited throughput precision; no efficacy selection",
    )


class Runner:
    def __init__(self, args):
        self.args = args
        self.started = time.monotonic()
        self.finish_by = datetime.fromisoformat(DEADLINE).timestamp()
        self.deadline = min(
            self.started + args.deadline_seconds - 120,
            self.started + self.finish_by - time.time(),
        )
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("fresh RUN_DIR required")
        self.bank, self.cells = load()
        self.saved, self.provenance = methods()
        source, source_provenance = frozen_source()
        self.corpora = source["corpora.json"]
        self.full_rows, self.old_g4, self.old, full_provenance = references()
        _, self.full_libraries = pinned_history()
        if self.old["libraries.json"] != self.full_libraries or self.old["freeze.json"][
            "table_hashes"
        ] != {tid: Decoder(self.corpora[tid]["tables"]["C"]).hash() for tid in CORPORA}:
            raise ValueError("full F library mismatch")
        self.builds = self.saved["builds.json"]
        self.accounting = dict(
            full=self.saved["preparation.json"]["full_acquisition"],
            cheap={k: v["acquisition"] for k, v in self.builds.items()},
            historical_calibration=self.saved["preparation.json"]["validation"][
                "historical_replay"
            ]["calibration"],
            qualification="historical acquisition seconds in 2033 calibration units; search worker-seconds directly measured on this bank; historical prices not remeasured",
        )
        self.old_bank, self.old_cells = load_training()
        _, ta_cells = load_ta()
        self.old_cells.update(ta_cells)
        self.indices = np.random.default_rng(0).choice(1331, 96, replace=False).tolist()
        self.diagnostic = [self.bank["inputs"][i] for i in self.indices[:4]]
        self.timing = fitted_roster(
            self.bank["timing_ids"], 4, timing=True
        ) + g4_roster(self.bank["timing_ids"], True)
        self.schedules = {
            f"{n}-{'all' if len(arms) == 3 else 'no-S8'}": fitted_roster(
                self.bank["selected_ids"], n, arms
            )
            + g4_roster(self.bank["selected_ids"])
            for n, arms in ((8, ARMS), (4, ARMS), (4, ("A8", "full_F")))
        }
        self.replay = self.replay_roster()
        confirmation_seeds = {r["seed"] for r in self.schedules["8-all"]}
        timing_seeds = {r["seed"] for r in self.timing}
        if confirmation_seeds & timing_seeds or (confirmation_seeds | timing_seeds) & {
            r["seed"] for r in self.replay
        }:
            raise ValueError("seed overlap")
        for schedule in self.schedules.values():
            if len({self.key(r) for r in schedule}) != len(schedule):
                raise ValueError("duplicate schedule key")
        hashes = implementation_hashes()
        hashes["two_sum_run.py"] = hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest()
        self.freeze = dict(
            bank_sha256=BANK_SHA,
            method_sha256=METHOD_SHA,
            implementation_hashes=hashes,
            builds_hash=digest(self.builds),
            full_tables_hash=digest(self.corpora),
            full_libraries_hash=digest(self.full_libraries),
            accounting_hash=digest(self.accounting),
            source_provenance=source_provenance,
            full_provenance=full_provenance,
            timing_schedule_hash=digest(self.timing),
            schedule_hashes={k: digest(s) for k, s in self.schedules.items()},
            replay_hash=digest(self.replay),
            frozen_before_timing=True,
        )
        for name, val in (
            (
                "config.json",
                dict(
                    task="2026-10-09-2303",
                    arguments=vars(args),
                    seed_base=BASE,
                    cap=CAP,
                    population=256,
                    arms=ARMS,
                    method=dict(
                        selection="lexicase",
                        crossover=0.7,
                        mutation=0.03,
                        elites=2,
                        fragment_rate=0.2,
                        operator="F",
                        empty_fallback="uniform C-chain lengths3..6",
                        suffix="preserved",
                    ),
                    git_commit=subprocess.check_output(
                        ["git", "rev-parse", "HEAD"], text=True
                    ).strip(),
                ),
            ),
            ("bank.json", self.bank),
            ("builds.json", self.builds),
            ("accounting.json", self.accounting),
            ("method_freeze.json", self.freeze),
            ("candidate_schedules.json", self.schedules),
            ("timing_schedule.json", self.timing),
            ("replay_schedule.json", self.replay),
        ):
            write_json(self.out, name, val)

    @staticmethod
    def key(r):
        return r["corpus"], r["cell"], r["seed"], r["arm"]

    def replay_roster(self):
        rows = [dict(r, phase="replay") for r in self.saved["replay.json"]]
        for tid in CORPORA:
            rows.append(
                dict(
                    next(
                        r
                        for r in self.full_rows
                        if r["corpus"] == tid and r["arm"] == "F"
                    ),
                    arm="full_F",
                    phase="replay",
                )
            )
        for ci in (0, 15):
            rows.append(
                dict(
                    next(
                        r
                        for r in self.old_g4
                        if r["cell"] == load_ta()[0]["selected_ids"][ci]
                    ),
                    phase="replay",
                    corpus="G4",
                    family="G4",
                    arm="G4",
                )
            )
        # Keep reference payload alongside each immutable replay key, but do not pass it to search.
        return rows

    def envelope(self, meta, cap=CAP):
        if meta["arm"] in ("A8", "S8"):
            b = self.builds[f"{meta['corpus']}|{meta['block']}|{meta['arm']}"]
            table, fragments = b["table"], b["library"]["fragments"]
        elif meta["arm"] == "full_F":
            table = self.corpora[meta["corpus"]]["tables"]["C"]
            fragments = self.full_libraries[meta["corpus"]]["fragments"]
        else:
            table, fragments = tables()["G4"].tolist(), []
        cell = (self.old_cells if meta["phase"] == "replay" else self.cells)[
            meta["cell"]
        ]
        off = meta["arm"] == "G4"
        job = (
            cell,
            "G4" if off else "F",
            table,
            meta["seed"],
            cap,
            256,
            self.bank["inputs"],
            "v2_rmin_first",
        )
        metadata = {
            k: meta[k]
            for k in (
                "phase",
                "family",
                "corpus",
                "cell",
                "arm",
                "seed",
                "block",
                "seed_ordinal",
            )
            if k in meta
        }
        return job, metadata, fragments, self.diagnostic, off

    def jobs(self, schedule, filename, cap=CAP):
        pending = {self.key(r): r for r in schedule}
        if len(pending) != len(schedule):
            raise ValueError("duplicate keys")
        envelopes = [self.envelope(r, cap) for r in schedule]
        hashes = {self.key(e[1]): Decoder(e[0][2]).hash() for e in envelopes}
        rows = []
        with (self.out / filename).open("w", buffering=1) as stream:

            def save(r):
                meta = pending.pop(self.key(r))
                keys = (
                    "phase",
                    "family",
                    "corpus",
                    "cell",
                    "arm",
                    "seed",
                    "block",
                    "seed_ordinal",
                )
                if (
                    any(r[k] != meta[k] for k in keys if k in meta)
                    or r["table_hash"] != hashes[self.key(r)]
                    or r["cap"] != cap
                    or r["pop_size"] != 256
                    or not 0 < r["evaluations"] <= cap
                    or r["evaluations"] % 256
                    or (not r["solved"] and r["evaluations"] != cap)
                    or (r["solver"] is not None) != r["solved"]
                    or r["training_indices"]
                    != np.random.default_rng([r["seed"], 0])
                    .choice(1331, 64, replace=False)
                    .tolist()
                ):
                    raise ValueError("search provenance/cases/budget changed")
                if (
                    r["arm"] != "G4"
                    and r["operator"]["eligible_children"]
                    != (r["generations"] - 1) * 254
                ):
                    raise ValueError("elite edited")
                rows.append(r)
                stream.write(json.dumps(r, allow_nan=False) + "\n")
                write_json(
                    self.out,
                    "progress.json",
                    dict(completed=len(rows), total=len(schedule), phase=r["phase"]),
                )

            if (
                not run_jobs(self.pool, execute, envelopes, self.deadline, save)
                or pending
            ):
                raise TimeoutError("incomplete roster; no efficacy report")
        groups = defaultdict(list)
        for r in rows:
            if r["arm"] != "G4":
                groups[r["corpus"], r["cell"], r["seed"]].append(r)
        for rs in groups.values():
            if len({tuple(r["training_indices"]) for r in rs}) != 1:
                raise ValueError("paired cases changed")
        return sorted(rows, key=self.key)

    def gates(self):
        aliases, libraries = {}, {}
        for key, b in self.builds.items():
            if b["library"]["fragments"]:
                aliases[key] = dict(tables=dict(C=b["table"]))
                libraries[key] = b["library"]
        for tid in CORPORA:
            aliases[tid] = self.corpora[tid]
            libraries[tid] = self.full_libraries[tid]
        # validate_edits identifies decoders by key before '|': use exact synthetic keys.
        edit_corpora = {k.split("|")[0]: v for k, v in aliases.items() if "|" not in k}
        renamed_libs = {}
        for i, (key, library) in enumerate(libraries.items()):
            synthetic = f"build{i}"
            edit_corpora[synthetic] = aliases[key]
            renamed_libs[synthetic] = library
        validation = dict(
            empty_fallback=audit_empty_fallback(),
            suffix_edits=validate_edits(
                edit_corpora, renamed_libs, n=10000, arms=("F",)
            ),
        )
        schedule = self.replay
        rows = self.jobs(schedule, "historical_replay.jsonl")
        old = {self.key(r): r for r in schedule}
        for r in rows:
            fields = REPLAY_FIELDS if r["arm"] == "G4" else SCIENTIFIC_FIELDS
            if any(r[k] != old[self.key(r)][k] for k in fields if k != "arm"):
                raise ValueError("historical scientific replay mismatch")
        calibration = {}
        for arm in (*ARMS, "G4"):
            rs = [r for r in rows if r["arm"] == arm]
            calibration[arm] = sum(map(worker_seconds, rs)) / sum(
                old[self.key(r)]["seconds"] for r in rs
            )
        validation.update(
            passed=True,
            historical_rows=len(rows),
            historical_worker_seconds=sum(map(worker_seconds, rows)),
            calibration=calibration,
        )
        write_json(self.out, "validation.json", validation)
        return validation

    def prepare(self):
        validation = self.gates()
        schedule = (
            [r for r in self.timing if r["cell"] == self.bank["timing_ids"][0]]
            if self.args.smoke
            else self.timing
        )
        write_json(
            self.out,
            "smoke_schedule.json" if self.args.smoke else "timing_schedule.json",
            schedule,
        )
        tick = time.monotonic()
        rows = self.jobs(schedule, "timing.jsonl", cap=8192 if self.args.smoke else CAP)
        wall = time.monotonic() - tick
        if self.args.smoke:
            full_schedule = [
                r
                for r in self.timing
                if r["cell"] == self.bank["timing_ids"][1]
                and (
                    r["seed_ordinal"] == 0
                    or (r["corpus"] == "PA1" and r["seed_ordinal"] == 3)
                )
            ]
            full = self.jobs(full_schedule, "smoke_full_cap.jsonl")
            write_json(
                self.out,
                "smoke.json",
                dict(
                    passed=True,
                    admitted=False,
                    rows=len(rows),
                    cap=8192,
                    validation=validation,
                    full_cap_rows=len(full),
                    full_cap_mean_seconds={
                        a: float(
                            np.mean([worker_seconds(r) for r in full if r["arm"] == a])
                        )
                        for a in (*ARMS, "G4")
                    },
                ),
            )
            return
        a = admission(
            rows,
            wall,
            time.monotonic() - self.started,
            self.args.workers,
            self.finish_by,
        )
        p = dict(
            admitted=a["admitted"],
            admission=a,
            validation=validation,
            method_freeze=self.freeze,
            admission_hash=digest(a),
            timing_rows=rows,
            timing_payload_hash=digest(self.scientific(rows)),
        )
        if a["admitted"]:
            chosen = a["selected"]
            key = f"{chosen['seeds']}-{'all' if len(chosen['arms']) == 3 else 'no-S8'}"
            p["schedule_key"] = key
            write_json(self.out, "schedule.json", self.schedules[key])
        write_json(self.out, "preparation.json", p)
        print(json.dumps(a, indent=2), flush=True)
        if not a["admitted"]:
            raise ValueError("runtime obstacle; return to strategy")

    @staticmethod
    def scientific(rows):
        return [{k: r[k] for k in SCIENTIFIC_FIELDS if k in r} for r in rows]

    def score(self):
        p = json.loads(Path(self.args.preparation).read_text())
        if (
            not p["admitted"]
            or p["method_freeze"] != self.freeze
            or not p["validation"]["passed"]
            or p["admission_hash"] != digest(p["admission"])
            or p["admission"]["workers"] != self.args.workers
            or p["timing_payload_hash"] != digest(self.scientific(p["timing_rows"]))
        ):
            raise ValueError("invalid or changed scoring handoff")
        chosen = p["admission"]["selected"]
        if chosen["with_reserve_seconds"] > self.finish_by - time.time():
            raise ValueError(
                "insufficient time before analysis deadline; return to strategy"
            )
        key = f"{chosen['seeds']}-{'all' if len(chosen['arms']) == 3 else 'no-S8'}"
        if key != p["schedule_key"] or p["method_freeze"]["schedule_hashes"][
            key
        ] != digest(self.schedules[key]):
            raise ValueError("scoring schedule changed")
        replay = self.jobs(self.timing, "timing_replay.jsonl")
        if self.scientific(replay) != self.scientific(p["timing_rows"]):
            raise ValueError("timing scientific replay mismatch")
        write_json(self.out, "preparation.json", p)
        write_json(
            self.out,
            "validation.json",
            dict(passed=True, timing_replay=len(replay), historical=p["validation"]),
        )
        schedule = self.schedules[key]
        write_json(self.out, "schedule.json", schedule)
        rows = self.jobs(schedule, "search.jsonl")
        report(self.out, rows, schedule, self.accounting, p)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--smoke", action="store_true")
    modes.add_argument("--preparation")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=2580)
    args = parser.parse_args()
    if args.workers != 10:
        parser.error("approved timing/scoring requires 10 workers")
    os.environ["RAYON_NUM_THREADS"] = "1"
    runner = Runner(args)
    with mp.get_context("spawn").Pool(args.workers) as pool:
        runner.pool = pool
        runner.score() if args.preparation else runner.prepare()


if __name__ == "__main__":
    main()
