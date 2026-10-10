"""0145 complementary-source replication of the unchanged four-plus-four recipe."""

import argparse
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

from experiments.chem_tape.comparison_gate_bank import (
    BANK_SHA as SOURCE_SHA,
    digest,
    load_training,
    load_replacement_sources,
)
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.fragment_run import CORPORA, implementation_hashes
from experiments.chem_tape.fragment_operator import validate_edits
from experiments.chem_tape.small_source_run import build_source, REPLAY_FIELDS
from experiments.chem_tape.sparse_feedback_run import audit_empty_fallback
from experiments.chem_tape.solver_corpus_fit import validate_table
from experiments.chem_tape.two_sum_bank import load, BANK_SHA
from experiments.chem_tape.two_sum_run import (
    Runner as TargetRunner,
    fitted_roster,
    g4_roster,
    methods,
    CAP,
    worker_seconds,
)
from experiments.chem_tape.source_replication_report import report

BASE = 206610100145
DEADLINE = "2026-10-10T07:12:10+02:00"
DATA = Path(__file__).with_name("data") / "source_replication_0145"
REFERENCE_SHA = "f9c139de1b4e1ca623a3fcf9a5d363c483545c7067144df9532149129d43b861"
ARMS = ("A8", "S8")  # prime denoted by recipe/source provenance, not search operator


def references():
    raw = gzip.decompress((DATA / "references.json.gz").read_bytes())
    provenance = json.loads((DATA / "provenance.json").read_text())
    if (
        hashlib.sha256(raw).hexdigest() != REFERENCE_SHA
        or provenance["payload_sha256"] != REFERENCE_SHA
    ):
        raise ValueError("historical reference changed")
    payload = json.loads(raw)
    bank, _ = load()
    expected = fitted_roster(bank["selected_ids"], 4, ("A8",)) + g4_roster(
        bank["selected_ids"]
    )
    rows = payload["target_rows"]
    by = {TargetRunner.key(r): r for r in rows}
    if (
        len(rows) != len(expected)
        or len(by) != len(rows)
        or set(by) != {TargetRunner.key(r) for r in expected}
    ):
        raise ValueError("historical target roster incomplete")
    for meta in expected:
        if any(by[TargetRunner.key(meta)][k] != v for k, v in meta.items()):
            raise ValueError("historical target metadata changed")
    return payload, provenance


def collection_roster(roster, smoke=False):
    return [
        dict(
            phase=phase,
            family=tid[:2],
            corpus=tid,
            block=0,
            cell=cid,
            arm="F" if p == 2 else "G4",
            attempt=a,
            seed=BASE
            + (10000000 if smoke else 0)
            + p * 1000000
            + ci * 10000
            + ti * 100
            + a,
        )
        for ci, tid in enumerate(CORPORA)
        if not smoke or tid in ("BE1", "PA1")
        for p, phase in enumerate(("first_G4", "static_G4", "adaptive"))
        for ti, cid in enumerate(roster[tid[:2]])
        for a in range(4)
    ]


def timing_roster(ids):
    return [
        dict(
            phase="timing",
            family=tid[:2],
            corpus=tid,
            block=0,
            seed_ordinal=0,
            cell=cid,
            arm=arm,
            seed=BASE + 3000000 + CORPORA.index(tid) * 10000 + ci * 100,
        )
        for tid in CORPORA[:4]
        for ci, cid in enumerate(ids)
        for arm in ARMS
    ]


def admission(rows, wall, elapsed, workers, finish_by, now=None):
    now = time.time() if now is None else now
    means = {
        a: float(np.mean([worker_seconds(r) for r in rows if r["arm"] == a]))
        for a in ARMS
    }
    effective = min(workers, sum(map(worker_seconds, rows)) / wall)
    replay = 1.15 * sum(map(worker_seconds, rows)) / effective
    candidates = []
    for arms in (ARMS, ("A8",)):
        projection = 1.15 * 1024 * sum(means[a] for a in arms) / effective
        reserve = projection + replay + 240
        candidates.append(
            dict(
                arms=list(arms),
                seeds=4,
                searches=1024 * len(arms),
                projected_seconds=projection,
                with_reserve_seconds=reserve,
                fits=reserve <= 7080 and reserve <= finish_by - now,
            )
        )
    selected = next((c for c in candidates if c["fits"]), None)
    return dict(
        admitted=selected is not None and elapsed <= 2280,
        selected=selected,
        candidates=candidates,
        effective_workers=effective,
        workers=workers,
        prepare_seconds=elapsed,
        timing_wall_seconds=wall,
        mean_worker_seconds=means,
        replay_reserve_seconds=replay,
        report_reserve_seconds=240,
        remaining_seconds=finish_by - now,
        finish_by=DEADLINE,
        timing_only=True,
    )


class Runner(TargetRunner):
    def __init__(self, args):
        self.args = args
        self.started = time.monotonic()
        self.finish_by = datetime.fromisoformat(DEADLINE).timestamp()
        self.deadline = min(
            self.started + args.deadline_seconds - 120,
            self.started + self.finish_by - time.time() - 240,
        )
        if self.deadline <= self.started:
            raise ValueError("analysis deadline passed")
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("fresh RUN_DIR required")
        self.source_bank, self.source_cells = load_replacement_sources()
        self.roster = self.source_bank["split"]["holdouts"]
        self.bank, self.cells = load()
        if self.source_bank["inputs"] != self.bank["inputs"]:
            raise ValueError("source/target domain mismatch")
        self.indices = np.random.default_rng(0).choice(1331, 96, replace=False).tolist()
        self.diagnostic = [self.bank["inputs"][i] for i in self.indices[:4]]
        self.refs, self.provenance = references()
        self.saved, _ = methods()
        self.sources = collection_roster(self.roster, args.smoke)
        self.timing = timing_roster(self.bank["timing_ids"])
        self.schedules = {
            k: fitted_roster(self.bank["selected_ids"], 4, arms)
            for k, arms in (("all", ARMS), ("A8", ("A8",)))
        }
        source_seeds = {r["seed"] for r in self.sources}
        if len(source_seeds) != len(self.sources) or source_seeds & set(
            self.refs["historical_source_seeds"]
        ):
            raise ValueError("source seed overlap")
        if source_seeds & {r["seed"] for r in self.timing + self.schedules["all"]} or {
            r["seed"] for r in self.timing
        } & {r["seed"] for r in self.schedules["all"]}:
            raise ValueError("timing/confirmation overlap")
        self.hashes = implementation_hashes()
        self.freeze = dict(
            source_bank_sha256=SOURCE_SHA,
            target_bank_sha256=BANK_SHA,
            references_sha256=REFERENCE_SHA,
            historical_artifacts_hash=digest(self.saved["builds.json"]),
            implementation_hashes=self.hashes,
            source_schedule_hash=digest(self.sources),
            roster_hash=digest(self.roster),
            schedule_hashes={k: digest(v) for k, v in self.schedules.items()},
            timing_hash=digest(self.timing),
            smoke=args.smoke,
        )
        self.builds, self.seed_builds = {}, {}
        for name, value in (
            (
                "config.json",
                dict(
                    task="2026-10-10-0145",
                    arguments=vars(args),
                    seed_base=BASE,
                    cap=CAP,
                    population=256,
                    git_commit=subprocess.check_output(
                        ["git", "rev-parse", "HEAD"], text=True
                    ).strip(),
                    recipe="unchanged C alpha50/F, 4+4 per cell; complementary development sources",
                    method=dict(
                        selection="lexicase",
                        crossover=0.7,
                        mutation=0.03,
                        elites=2,
                        fragment_rate=0.2,
                        suffix="preserved",
                    ),
                ),
            ),
            ("bank.json", self.bank),
            ("source_roster.json", self.roster),
            ("source_schedule.json", self.sources),
            ("timing_schedule.json", self.timing),
            ("candidate_schedules.json", self.schedules),
            ("method_freeze.json", self.freeze),
            ("historical_provenance.json", self.provenance),
        ):
            write_json(self.out, name, value)

    def envelope(self, meta, cap=CAP):
        source = meta["phase"] in ("first_G4", "static_G4", "adaptive")
        off = meta["arm"] in ("first_G4", "static_G4", "G4")
        if off:
            table, fragments = tables()["G4"].tolist(), []
        else:
            build = (
                self.seed_builds[meta["corpus"]]
                if source
                else self.builds[f"{meta['corpus']}|{meta['arm']}"]
            )
            table, fragments = build["table"], build["library"]["fragments"]
        cell = (self.source_cells if source else self.cells)[meta["cell"]]
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
        return job, meta, fragments, self.diagnostic, off

    def rebuild(self, sources):
        result = {}
        jobs = [
            (
                tid.split("|")[0],
                tid,
                rows,
                self.bank["inputs"],
                self.source_cells,
                self.indices,
                self.roster[tid[:2]],
            )
            for tid, rows in sources.items()
        ]

        def save(build):
            result[build["block"]] = build

        if not run_jobs(self.pool, build_source, jobs, self.deadline, save) or len(
            result
        ) != len(sources):
            raise TimeoutError("incomplete fitting")
        for key, build in result.items():
            if build["attempt_keys"] != [
                [r["corpus"], r["cell"], r["seed"]] for r in sources[key]
            ]:
                raise ValueError("source membership/order changed")
            build["acquisition_id"] = key
            build["block"] = 0  # one independent acquisition, no nested blocks
            validate_table(build["table"])
        return result

    def gates(self):
        bank, cells = load_training()
        # The retained historical build pools first batch in schedule order and
        # adaptive rows in the reviewed runner's sorted key order.
        rs = self.refs["legacy_build_rows"]
        rs = rs[:16] + sorted(rs[16:], key=self.key)
        actual = build_source(("BE1", 0, rs, bank["inputs"], cells, self.indices))
        old = self.saved["builds.json"]["BE1|0|A8"]
        if (
            actual["table"] != old["table"]
            or actual["library"] != old["library"]
            or actual["attempt_keys"] != old["attempt_keys"]
            or actual["attempts_hash"] != old["attempts_hash"]
        ):
            raise ValueError("2033 old-default build replay mismatch")
        g4 = [r for r in self.refs["target_rows"] if r["arm"] == "G4"]
        sample = [
            next(r for r in g4 if r["cell"] == self.bank["selected_ids"][ci])
            for ci in (0, 15)
        ]
        metas = [
            {
                k: r[k]
                for k in (
                    "phase",
                    "family",
                    "corpus",
                    "cell",
                    "block",
                    "seed_ordinal",
                    "arm",
                    "seed",
                )
            }
            for r in sample
        ]
        replay = self.jobs(metas, "historical_replay.jsonl")
        indexed = {self.key(r): r for r in sample}
        if any(
            any(r[k] != indexed[self.key(r)][k] for k in REPLAY_FIELDS) for r in replay
        ):
            raise ValueError("2303 G4 replay mismatch")
        return dict(
            passed=True,
            legacy_build="BE1|0|A8",
            legacy_table_hash=actual["table_hash"],
            legacy_library_hash=digest(actual["library"]),
            empty_fallback=audit_empty_fallback(),
            historical_replay_rows=2,
            G4_time_calibration=sum(map(worker_seconds, replay))
            / sum(map(worker_seconds, sample)),
        )

    def prepare(self):
        validation = self.gates()
        first_schedule = [r for r in self.sources if r["phase"] == "first_G4"]
        tick = time.monotonic()
        first = self.jobs(first_schedule, "first.jsonl")
        self.seed_builds = self.rebuild(
            {
                tid: [r for r in first if r["corpus"] == tid]
                for tid in dict.fromkeys(r["corpus"] for r in first)
            }
        )
        write_json(self.out, "seed_builds.json", self.seed_builds)
        rest = self.jobs(
            [r for r in self.sources if r["phase"] != "first_G4"], "continuation.jsonl"
        )
        sources = {
            f"{tid}|{arm}": [r for r in first if r["corpus"] == tid]
            + [r for r in rest if r["corpus"] == tid and r["phase"] == phase]
            for tid in self.seed_builds
            for arm, phase in (("A8", "adaptive"), ("S8", "static_G4"))
        }
        self.builds = self.rebuild(sources)
        for key, build in self.builds.items():
            tid, arm = key.split("|")
            if len(build["attempt_keys"]) != 32 or any(
                sum(k[1] == c for k in build["attempt_keys"]) != 8
                for c in self.roster[tid[:2]]
            ):
                raise ValueError("not eight attempts per cell")
            a = build["acquisition"]
            a["external_verification_seconds"] = sum(
                r.get("external_verification_seconds", 0) for r in sources[key]
            )
            a["intermediate_overhead_seconds"] = (
                sum(
                    self.seed_builds[tid]["acquisition"][k]
                    for k in (
                        "verification_seconds",
                        "fit_seconds",
                        "extraction_seconds",
                    )
                )
                if arm == "A8"
                else 0
            )
            build["arm"] = arm
        collection_wall = time.monotonic() - tick
        write_json(self.out, "builds.json", self.builds)
        aliases = {
            key.replace("|", "_"): dict(tables=dict(C=b["table"]))
            for key, b in self.builds.items()
        }
        libs = {
            key.replace("|", "_") + "|whole": b["library"]
            for key, b in self.builds.items()
            if b["library"]["fragments"]
        }
        validation["edits"] = (
            validate_edits(aliases, libs, n=10000, arms=("F",))
            if libs
            else dict(empty=True)
        )
        if self.args.smoke:
            timing = [r for r in self.timing if r["corpus"] in self.seed_builds]
        else:
            timing = self.timing
        tick = time.monotonic()
        rows = self.jobs(timing, "timing.jsonl")
        wall = time.monotonic() - tick
        self.freeze.update(
            builds_hash=digest(self.builds),
            seed_builds_hash=digest(self.seed_builds),
            validation_hash=digest(validation),
            frozen_before_confirmation=True,
        )
        write_json(self.out, "method_freeze.json", self.freeze)
        a = admission(
            rows,
            wall,
            time.monotonic() - self.started,
            self.args.workers,
            self.finish_by,
        )
        p = dict(
            admitted=a["admitted"] and not self.args.smoke,
            admission=a,
            validation=validation,
            method_freeze=self.freeze,
            admission_hash=digest(a),
            timing_rows=rows,
            timing_payload_hash=digest(self.scientific(rows)),
            collection_wall_seconds=collection_wall,
            collection_worker_seconds=sum(map(worker_seconds, first + rest)),
        )
        write_json(self.out, "preparation.json", p)
        write_json(self.out, "validation.json", validation)
        if self.args.smoke:
            write_json(
                self.out,
                "smoke.json",
                dict(
                    passed=True,
                    admitted=False,
                    collection_rows=len(first + rest),
                    builds=len(self.builds),
                    seconds=time.monotonic() - self.started,
                    source_mean_worker_seconds={
                        phase: float(
                            np.mean(
                                [
                                    worker_seconds(r)
                                    for r in first + rest
                                    if r["phase"] == phase
                                ]
                            )
                        )
                        for phase in ("first_G4", "static_G4", "adaptive")
                    },
                    timing=a,
                ),
            )
            return
        if not p["admitted"]:
            write_json(
                self.out,
                "infeasible.json",
                dict(reason="timing/deadline admission obstacle", admission=a),
            )
            raise ValueError("cost obstacle; return to strategy")
        key = "all" if len(a["selected"]["arms"]) == 2 else "A8"
        write_json(self.out, "schedule.json", self.schedules[key])

    def score(self):
        path = Path(self.args.preparation)
        p = json.loads(path.read_text())
        self.builds = json.loads((path.parent / "builds.json").read_text())
        seed_builds = json.loads((path.parent / "seed_builds.json").read_text())
        expected = dict(
            self.freeze,
            builds_hash=digest(self.builds),
            seed_builds_hash=digest(seed_builds),
            validation_hash=digest(p["validation"]),
            frozen_before_confirmation=True,
        )
        if (
            not p["admitted"]
            or not p["validation"]["passed"]
            or p["method_freeze"] != expected
            or p["admission_hash"] != digest(p["admission"])
            or p["timing_payload_hash"] != digest(self.scientific(p["timing_rows"]))
            or p["admission"]["workers"] != self.args.workers
        ):
            raise ValueError("changed/smoke/incomplete handoff")
        chosen = p["admission"]["selected"]
        if chosen["arms"] not in (list(ARMS), ["A8"]) or chosen["seeds"] != 4:
            raise ValueError("unapproved score roster")
        if chosen["with_reserve_seconds"] > min(
            self.finish_by - time.time(), self.deadline - time.monotonic() + 120
        ):
            raise ValueError("insufficient score deadline; return to strategy")
        self.freeze = expected
        for name, value in (
            ("builds.json", self.builds),
            ("seed_builds.json", seed_builds),
            ("preparation.json", p),
            ("method_freeze.json", expected),
        ):
            write_json(self.out, name, value)
        replay = self.jobs(self.timing, "timing_replay.jsonl")
        if self.scientific(replay) != self.scientific(p["timing_rows"]):
            raise ValueError("scientific timing handoff replay mismatch")
        write_json(
            self.out,
            "validation.json",
            dict(passed=True, timing_replay_rows=len(replay)),
        )
        key = "all" if len(chosen["arms"]) == 2 else "A8"
        schedule = self.schedules[key]
        write_json(self.out, "schedule.json", schedule)
        # Explicit historical artifact/key mapping: one new build vs four old blocks.
        pairing = [
            dict(
                new_build=r["corpus"] + "|A8",
                historical_build=f"{r['corpus']}|{r['block']}|A8",
                new_table_hash=self.builds[r["corpus"] + "|A8"]["table_hash"],
                historical_table_hash=self.saved["builds.json"][
                    f"{r['corpus']}|{r['block']}|A8"
                ]["table_hash"],
                historical_library_hash=digest(
                    self.saved["builds.json"][f"{r['corpus']}|{r['block']}|A8"][
                        "library"
                    ]
                ),
                cell=r["cell"],
                seed=r["seed"],
                seed_ordinal=r["seed_ordinal"],
                block=r["block"],
            )
            for r in schedule
            if r["arm"] == "A8"
        ]
        write_json(self.out, "historical_pairing.json", pairing)
        rows = self.jobs(schedule, "search.jsonl")
        report(self.out, rows, schedule, self.builds, p, self.refs["target_rows"])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    modes = ap.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--smoke", action="store_true")
    modes.add_argument("--preparation")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--deadline-seconds", type=int, default=2400)
    args = ap.parse_args()
    if args.workers != 10:
        ap.error("approved concurrency requires ten workers")
    os.environ["RAYON_NUM_THREADS"] = "1"
    runner = Runner(args)
    with mp.get_context("spawn").Pool(args.workers) as pool:
        runner.pool = pool
        runner.score() if args.preparation else runner.prepare()


if __name__ == "__main__":
    main()
