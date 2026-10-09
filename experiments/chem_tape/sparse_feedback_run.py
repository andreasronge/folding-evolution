"""2033 one frozen sparse-source feedback batch versus equal G4 attempts.

Preparation writes all acquisition keys before collection. --smoke-collection uses
only 128 diagnostic attempts and cannot supply a scoring handoff.
"""

import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import TRAINING, digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.fragment_operator import BlockOperator, validate_edits
from experiments.chem_tape.fragment_report import row_key
from experiments.chem_tape.small_source_run import (
    Runner as SmallRunner,
    CORPORA,
    SCIENTIFIC_FIELDS,
    build_source,
    execute as small_execute,
    roster as old_roster,
    smoke_roster as old_smoke_roster,
    REPLAY_FIELDS,
)
from experiments.chem_tape.sparse_feedback_report import report

DATA = Path(__file__).with_name("data") / "sparse_feedback_2033"
REFERENCE_SHA = "772766f5362ea6a06afd0c216b0262b8d8164895aa0fa26873c0d0a5531fb517"
ARMS = ("A8", "S8")
BASE = 206610092033


def execute(envelope):
    tick = time.monotonic()
    row = small_execute(envelope)
    row["external_verification_seconds"] = max(
        0.0, time.monotonic() - tick - row["seconds"]
    )
    return row


def audit_empty_fallback():
    decoder = Decoder(tables()["G4"])
    original = np.random.default_rng(2033).integers(
        decoder.allele_range, size=(1024, 32), dtype=np.int32
    )
    results = []
    for arm in ("F", "W"):
        op = BlockOperator(arm, [], 2033, empty_fallback=True)
        changed, info = op.edit(original.copy(), decoder, force=True, boundary=True)
        actual = decoder.decode(changed)
        if not np.array_equal(actual, info["desired"]) or set(info["lengths"]) != {
            3,
            4,
            5,
            6,
        }:
            raise ValueError("empty fallback decode/span failed")
        for i, (start, length) in enumerate(zip(info["starts"], info["lengths"])):
            outside = np.ones(32, dtype=bool)
            outside[start : start + length] = False
            if not np.array_equal(actual[i, outside], info["before"][i, outside]):
                raise ValueError("empty fallback suffix changed")
        results.append(changed)
    if not np.array_equal(*results):
        raise ValueError("empty F/W fallback paths differ")
    return dict(passed=True, forced_edits=2048, identical_F_W=True)


def retained():
    raw = (DATA / "provenance.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != REFERENCE_SHA:
        raise ValueError("1743 provenance changed")
    p = json.loads(raw)
    saved = {}
    for name, sha in p["sha256"].items():
        raw = gzip.decompress((DATA / (name + ".gz")).read_bytes())
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError("1743 reference changed: " + name)
        saved[name] = (
            [json.loads(s) for s in raw.splitlines()]
            if name.endswith(".jsonl")
            else json.loads(raw)
        )
    rows = saved["primary.jsonl"]
    if (
        len(rows) != 4096
        or len({row_key(r) for r in rows}) != 4096
        or not saved["validation.json"]["passed"]
        or not saved["preparation.json"]["admitted"]
        or any(
            saved[n]["status"] != "done"
            for n in ("metadata.json", "score_metadata.json")
        )
        or digest(saved["builds.json"]) != saved["freeze.json"]["builds_hash"]
    ):
        raise ValueError("1743 incomplete reference")
    return saved, p


def roster(ids, n):
    return [dict(r, arm=ARMS[("F", "W").index(r["arm"])]) for r in old_roster(ids, n)]


def smoke_roster(ids):
    return [
        dict(
            r,
            arm=ARMS[("F", "W").index(r["arm"])],
            seed=BASE + 1000000 + CORPORA.index(r["corpus"]) * 100 + r["block"],
        )
        for r in old_smoke_roster(ids)
    ]


def collection_roster():
    return [
        dict(
            phase="collection",
            family=tid[:2],
            corpus=tid,
            block=b,
            cell=cid,
            arm="F",
            attempt=a,
            seed=BASE + ci * 10000 + b * 1000 + ti * 100 + a,
        )
        for ci, tid in enumerate(CORPORA)
        for b in range(4)
        for ti, cid in enumerate(TRAINING[tid[:2]])
        for a in range(4)
    ]


def source_allocations(saved):
    """Select by pinned schedule order; never sort numeric seeds or drop failures."""
    rows = [r for r in saved["search.jsonl"] if r["phase"] == "collection"]
    index = {(r["corpus"], r["cell"], r["seed"]): r for r in rows}
    schedule = [r for r in saved["schedule.json"] if r["phase"] == "collection"]
    ordered = defaultdict(list)
    ghash = Decoder(tables()["G4"]).hash()
    if len(rows) != 3072 or len(index) != 3072 or len(schedule) != 3072:
        raise ValueError("source incomplete/duplicate")
    seen = set()
    for meta in schedule:
        key = (meta["corpus"], meta["cell"], meta["seed"])
        if key in seen or key not in index:
            raise ValueError("source schedule keys changed")
        seen.add(key)
        r = index[key]
        if (
            any(r[k] != v for k, v in meta.items())
            or r["arm"] != "G4"
            or r["table_hash"] != ghash
            or r["cap"] != 524288
            or r["pop_size"] != 256
            or bool(r["solver"] is not None) != r["solved"]
            or not 0 < r["evaluations"] <= r["cap"]
            or r["evaluations"] % 256
            or (not r["solved"] and r["evaluations"] != r["cap"])
        ):
            raise ValueError("invalid source row")
        ordered[r["corpus"], r["cell"]].append(r)
    if len(ordered) != 64 or any(len(rs) != 48 for rs in ordered.values()):
        raise ValueError("source cell allocation changed")

    def select(offset):
        return {
            f"{tid}|{b}": [
                r
                for cid in TRAINING[tid[:2]]
                for r in ordered[tid, cid][offset + 4 * b : offset + 4 * b + 4]
            ]
            for tid in CORPORA
            for b in range(4)
        }

    first, static = select(0), select(16)

    def keys(mapping):
        return [
            (r["corpus"], r["cell"], r["seed"]) for rs in mapping.values() for r in rs
        ]

    fk, sk = keys(first), keys(static)
    if len(set(fk)) != 1024 or len(set(sk)) != 1024 or set(fk) & set(sk):
        raise ValueError("first/static attempt overlap")
    return (
        first,
        static,
        dict(
            first=fk,
            static=sk,
            first_sha256=digest(fk),
            static_sha256=digest(sk),
            disjoint=True,
        ),
    )


def scientific(row):
    # Arm labels are policy bookkeeping; execute always uses the unchanged F operator.
    return {k: row[k] for k in SCIENTIFIC_FIELDS if k != "arm"}


class Runner(SmallRunner):
    arms = ARMS

    def __init__(self, args):
        super().__init__(args)
        self.retained, self.retained_provenance = retained()
        self.seed_builds = self.retained["builds.json"]
        self.seed_reference = self.retained["primary.jsonl"]
        expected = {row_key(r) for r in old_roster(self.ids, 16) if r["arm"] == "F"}
        if {row_key(r) for r in self.seed_reference} != expected:
            raise ValueError("retained scoring roster changed")
        self.first, self.static, self.source_manifest = source_allocations(self.saved)
        self.collection = collection_roster()
        self.smoke = smoke_roster(self.ids)
        self.rosters = {str(n): roster(self.ids, n) for n in (16, 12)}
        source_seeds = {r["seed"] for r in self.saved["schedule.json"]}
        score_seeds = {r["seed"] for rs in self.rosters.values() for r in rs}
        new_seeds = {r["seed"] for r in self.collection}
        smoke_seeds = {r["seed"] for r in self.smoke}
        if (
            len(new_seeds) != 1024
            or new_seeds & (source_seeds | score_seeds | smoke_seeds)
            or smoke_seeds & (source_seeds | score_seeds)
        ):
            raise ValueError("fresh seed collision")
        self.hashes["sparse_feedback_run.py"] = hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest()
        self.config.update(
            task="2026-10-09-2033",
            arms=ARMS,
            seed_base=BASE,
            retained_sha256=REFERENCE_SHA,
            method="one C4F4 batch vs four continued G4 attempts; unchanged pooling/fitter/extractor/operator",
            scope="one external update; reused development sources/tasks; decoder/library and yield/content not isolated",
        )
        self.validation = {}
        for name, val in [
            ("config.json", self.config),
            ("candidate_schedules.json", self.rosters),
            ("retained_provenance.json", self.retained_provenance),
            (
                "source_schedules.json",
                dict(
                    self.source_manifest,
                    adaptive=self.collection,
                    adaptive_sha256=digest(self.collection),
                    smoke=self.smoke,
                ),
            ),
        ]:
            write_json(self.out, name, val)

    def envelope(self, r, off=False):
        phase = r["phase"]
        if phase == "replay":
            tab = self.corpora[r["corpus"]]["tables"]["C"]
            fragments = self.full_libraries[r["corpus"]]["fragments"]
        elif phase == "replay_G4":
            tab, fragments = tables()["G4"].tolist(), []
        else:
            mapping = (
                self.seed_builds
                if phase in ("collection", "replay_seed")
                else self.builds
            )
            key = f"{r['corpus']}|{r['block']}"
            if mapping is self.builds:
                key += "|" + r["arm"]
            build = mapping[key]
            tab, fragments = build["table"], build["library"]["fragments"]
        operator_arm = "G4" if off else "F"
        job = (
            self.cells[r["cell"]],
            operator_arm,
            tab,
            r["seed"],
            self.config["cap"],
            256,
            self.bank["inputs"],
            "v2_rmin_first",
        )
        return job, dict(r, arm=operator_arm), fragments, self.diagnostic_inputs, off

    def jobs(self, schedule, off=False, filename="search.jsonl"):
        expected = {row_key(r): r for r in schedule}
        if len(expected) != len(schedule):
            raise ValueError("duplicate schedule")
        envelopes = []
        table_hashes = {}
        for meta in schedule:
            e = self.envelope(meta, off)
            # execute receives policy arm as metadata but uses F for the operator.
            e = (e[0], dict(e[1], policy_arm=meta["arm"]), *e[2:])
            envelopes.append(e)
            table_hashes[row_key(meta)] = Decoder(e[0][2]).hash()
        rows = []
        with (self.out / filename).open("a", buffering=1) as stream:

            def save(r):
                r["arm"] = r.pop("policy_arm")
                key = row_key(r)
                meta = expected.pop(key)
                if (
                    any(r[k] != v for k, v in meta.items())
                    or r["table_hash"] != table_hashes[key]
                    or r["cap"] != self.config["cap"]
                    or r["pop_size"] != 256
                    or not 0 < r["evaluations"] <= r["cap"]
                    or r["evaluations"] % 256
                    or (not r["solved"] and r["evaluations"] != r["cap"])
                    or (r["solver"] is not None) != r["solved"]
                    or r["training_indices"]
                    != np.random.default_rng([r["seed"], 0])
                    .choice(len(self.bank["inputs"]), 64, replace=False)
                    .tolist()
                ):
                    raise ValueError("search provenance/budget changed")
                if (
                    not off
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
                or expected
            ):
                raise TimeoutError("incomplete roster; no efficacy decision")
        if schedule and schedule[0]["phase"] in ("smoke", "then_addition"):
            groups = defaultdict(list)
            for r in rows:
                groups[r["corpus"], r["cell"], r["seed"]].append(r)
            for pair in groups.values():
                if (
                    len(pair) != 2
                    or {r["arm"] for r in pair} != set(ARMS)
                    or len({tuple(r["training_indices"]) for r in pair}) != 1
                ):
                    raise ValueError("case/seed pairing changed")
                # Different decoder tables intentionally change decoded initial tapes.
        return sorted(rows, key=row_key)

    def rebuild(self, sources):
        def save(record):
            self.builds[f"{record['corpus']}|{record['block']}"] = record

        jobs = [
            (
                key.split("|")[0],
                "|".join(key.split("|")[1:]),
                rows,
                self.bank["inputs"],
                self.cells,
                self.indices,
            )
            for key, rows in sources.items()
        ]
        self.builds = {}
        if not run_jobs(self.pool, build_source, jobs, self.deadline, save) or len(
            self.builds
        ) != len(sources):
            raise TimeoutError("source rebuild incomplete")
        return self.builds

    def historical_gates(self):
        rebuilt = self.rebuild(self.first)
        for key, actual in rebuilt.items():
            old = self.seed_builds[key]
            if (
                actual["table_hash"] != old["table_hash"]
                or actual["table"] != old["table"]
                or digest(actual["library"]) != digest(old["library"])
                or actual["attempt_keys"] != old["attempt_keys"]
                or actual["attempts_hash"] != old["attempts_hash"]
            ):
                raise ValueError("1743 first-batch table/library not bit-exact")
        self.validation["empty_library_fallback"] = audit_empty_fallback()
        self.validation["first_batch"] = dict(
            passed=True, decoder_hashes=64, library_hashes=64
        )
        # Preserve measured current intermediate verification/fitting/extraction overhead.
        self.intermediate = rebuilt
        schedules = {"seed": [], "full": [], "G4": []}
        references = {"seed": [], "full": [], "G4": []}
        for ci, tid in enumerate(CORPORA):
            seed = next(
                r
                for r in self.seed_reference
                if r["corpus"] == tid and r["block"] == ci % 4
            )
            full = next(
                r for r in self.reference if r["corpus"] == tid and r["arm"] == "F"
            )
            for name, row, phase in [
                ("seed", seed, "replay_seed"),
                ("full", full, "replay"),
            ]:
                meta = {k: row[k] for k in ("family", "corpus", "cell", "arm", "seed")}
                meta["phase"] = phase
                if name == "seed":
                    meta["block"] = row["block"]
                schedules[name].append(meta)
                references[name].append(row)
        for i in (0, 15):
            r = next(r for r in self.g4 if r["cell"] == self.ids[i])
            references["G4"].append(r)
            schedules["G4"].append(
                dict(
                    phase="replay_G4",
                    family="G4",
                    corpus="G4",
                    cell=r["cell"],
                    arm="G4",
                    seed=r["seed"],
                )
            )
        calibration = {}
        for name in schedules:
            rows = self.jobs(schedules[name], off=name == "G4")
            for r, old in zip(rows, sorted(references[name], key=row_key)):
                fields = SCIENTIFIC_FIELDS if name != "G4" else REPLAY_FIELDS
                if any(r[k] != old[k] for k in fields):
                    raise ValueError(name + " historical replay failed")
            calibration[name] = sum(r["seconds"] for r in rows) / sum(
                r["seconds"] for r in references[name]
            )
        self.validation["historical_replay"] = dict(
            passed=True, seed=16, full=16, G4=2, calibration=calibration
        )
        write_json(self.out, "replay_schedules.json", schedules)

    def prepare(self):
        self.historical_gates()
        collection = (
            [r for r in self.collection if r["block"] in (0, 2) and r["attempt"] == 0]
            if self.args.smoke_collection
            else self.collection
        )
        # Diagnostic collection has its own disjoint keys; never reuses full acquisition draws.
        if self.args.smoke_collection:
            collection = [dict(r, seed=r["seed"] + 2000000) for r in collection]
        write_json(self.out, "collection_schedule.json", collection)
        tick = time.monotonic()
        collected = self.jobs(collection, filename="collection.jsonl")
        collection_wall = time.monotonic() - tick
        by = defaultdict(list)
        for r in collected:
            by[f"{r['corpus']}|{r['block']}"].append(r)
        sources = {
            key + "|" + arm: first + (by[key] if arm == "A8" else self.static[key])
            for key, first in self.first.items()
            for arm in ARMS
        }
        builds = self.rebuild(sources)
        for key, b in builds.items():
            b["block"] = int(key.split("|")[1])
            b["arm"] = key.split("|")[2]
            seed = self.intermediate["|".join(key.split("|")[:2])]["acquisition"]
            # build_source prices pooled rows; first/static rows are historical,
            # adaptive rows current. Separate them for qualified time calibration.
            old_rows = self.first["|".join(key.split("|")[:2])]
            if b["arm"] == "S8":
                old_rows = old_rows + self.static["|".join(key.split("|")[:2])]
            b["acquisition"]["historical_source_seconds"] = sum(
                r["seconds"] for r in old_rows
            )
            b["acquisition"]["current_source_seconds"] = (
                b["acquisition"]["source_worker_seconds"]
                - b["acquisition"]["historical_source_seconds"]
            )
            b["acquisition"]["continuation_verification_seconds"] = (
                sum(
                    r.get("external_verification_seconds", 0)
                    for r in by["|".join(key.split("|")[:2])]
                )
                if b["arm"] == "A8"
                else 0.0
            )
            b["acquisition"]["intermediate_overhead_seconds"] = sum(
                seed[k]
                for k in ("verification_seconds", "fit_seconds", "extraction_seconds")
            )
            if not self.args.smoke_collection and (
                len(b["attempt_keys"]) != 32
                or any(
                    sum(k[1] == cid for k in b["attempt_keys"]) != 8
                    for cid in TRAINING[b["corpus"][:2]]
                )
            ):
                raise ValueError("not eight attempts per cell")
        write_json(self.out, "builds.json", builds)
        write_json(self.out, "seed_builds.json", self.intermediate)
        aliases = {
            key.replace("|", "_"): dict(tables=dict(C=b["table"]))
            for key, b in builds.items()
        }
        libs = {
            key.replace("|", "_") + "|whole": b["library"]
            for key, b in builds.items()
            if b["library"]["fragments"]
        }
        self.validation["edits"] = (
            validate_edits(aliases, libs, arms=("F",)) if libs else {}
        )
        tick = time.monotonic()
        smoke = self.jobs(self.smoke)
        wall = time.monotonic() - tick
        effective = min(self.args.workers, sum(r["seconds"] for r in smoke) / wall)
        means = {
            a: float(np.mean([r["seconds"] for r in smoke if r["arm"] == a]))
            for a in ARMS
        }
        replay_seconds = 1.15 * sum(r["seconds"] for r in smoke) / effective
        candidates = []
        for n in (16, 12):
            seconds = 1.15 * 256 * n * sum(means.values()) / effective
            candidates.append(
                dict(
                    seeds=n,
                    projected_seconds=seconds,
                    with_reserve_seconds=seconds + replay_seconds + 240,
                    fits=seconds + replay_seconds + 240 <= 10800,
                )
            )
        selected = next((c for c in candidates if c["fits"]), None)
        admission = dict(
            admitted=selected is not None and time.monotonic() - self.started <= 2700,
            selected_seeds=selected["seeds"] if selected else None,
            candidates=candidates,
            workers=self.args.workers,
            projected_seconds=selected["projected_seconds"] if selected else None,
            effective_workers=effective,
            timing_wall_seconds=wall,
            mean_worker_seconds=means,
            collection_wall_seconds=collection_wall,
            collection_worker_seconds=sum(r["seconds"] for r in collected),
            prepare_seconds=time.monotonic() - self.started,
            timing_only=True,
            implementation_smoke=self.args.smoke_collection,
        )
        self.validation.update(
            passed=True,
            attempt_keys_disjoint=self.source_manifest["disjoint"],
            collection_rows=len(collected),
            final_builds=len(builds),
        )
        freeze = dict(
            admission_hash=digest(admission),
            implementation_hashes=self.hashes,
            builds_hash=digest(builds),
            source=self.source,
            retained_sha256=REFERENCE_SHA,
            target_sha256=self.config["then_addition_sha256"],
            source_schedules_hash=digest(
                dict(self.source_manifest, adaptive=self.collection)
            ),
            accounting_hash=digest(
                dict(
                    full=self.retained["preparation.json"]["full_acquisition"],
                    seed={
                        key: b["acquisition"] for key, b in self.intermediate.items()
                    },
                    replay=self.validation["historical_replay"],
                )
            ),
            timing_payload_hash=digest([scientific(r) for r in smoke]),
            schedule_hashes={k: digest(v) for k, v in self.rosters.items()},
            smoke_hash=digest(self.smoke),
            frozen_before_scoring=True,
        )
        p = dict(
            admitted=admission["admitted"] and not self.args.smoke_collection,
            admission=admission,
            freeze=freeze,
            validation=self.validation,
            timing_rows=smoke,
            full_acquisition=self.retained["preparation.json"]["full_acquisition"],
            seed_acquisition={
                key: b["acquisition"] for key, b in self.intermediate.items()
            },
        )
        for name, val in [
            ("preparation.json", p),
            ("validation.json", self.validation),
            ("freeze.json", freeze),
        ]:
            write_json(self.out, name, val)
        if selected:
            write_json(self.out, "schedule.json", self.rosters[str(selected["seeds"])])
        print(json.dumps(admission, indent=2), flush=True)
        if not admission["admitted"]:
            raise ValueError("runtime admission failed; stop")

    def score(self):
        if not self.args.preparation:
            raise ValueError("preparation required")
        path = Path(self.args.preparation)
        p = json.loads(path.read_bytes())
        self.builds = json.loads((path.parent / "builds.json").read_bytes())
        f = p["freeze"]
        n = p["admission"]["selected_seeds"]
        if (
            (
                not p["admitted"]
                and not (
                    self.args.validate_preparation
                    and p["admission"]["implementation_smoke"]
                )
            )
            or (
                p["admission"]["implementation_smoke"]
                and not self.args.validate_preparation
            )
            or f["admission_hash"] != digest(p["admission"])
            or not p["validation"]["passed"]
            or p["admission"]["workers"] != self.args.workers
            or n not in (16, 12)
            or f["implementation_hashes"] != self.hashes
            or f["builds_hash"] != digest(self.builds)
            or f["source"] != self.source
            or f["retained_sha256"] != REFERENCE_SHA
            or not f["frozen_before_scoring"]
            or f["target_sha256"] != self.config["then_addition_sha256"]
            or f["source_schedules_hash"]
            != digest(dict(self.source_manifest, adaptive=self.collection))
            or f["schedule_hashes"] != {k: digest(v) for k, v in self.rosters.items()}
            or f["smoke_hash"] != digest(self.smoke)
            or f["timing_payload_hash"]
            != digest([scientific(r) for r in p["timing_rows"]])
            or f["accounting_hash"]
            != digest(
                dict(
                    full=p["full_acquisition"],
                    seed=p["seed_acquisition"],
                    replay=p["validation"]["historical_replay"],
                )
            )
        ):
            raise ValueError("frozen preparation changed/incomplete")
        for name, val in [
            ("preparation.json", p),
            ("builds.json", self.builds),
            ("freeze.json", f),
            ("schedule.json", self.rosters[str(n)]),
        ]:
            write_json(self.out, name, val)
        smoke = self.jobs(self.smoke)
        refs = {row_key(r): r for r in p["timing_rows"]}
        if len(refs) != 128 or any(
            scientific(r) != scientific(refs[row_key(r)]) for r in smoke
        ):
            raise ValueError("scientific handoff replay failed")
        write_json(
            self.out, "validation.json", dict(passed=True, smoke_replay_rows=128)
        )
        if self.args.validate_preparation:
            return
        rows = self.jobs(self.rosters[str(n)])
        report(
            self.out,
            rows,
            self.rosters[str(n)],
            self.builds,
            p,
            self.seed_reference,
            self.reference,
            self.g4,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--smoke-collection", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--validate-preparation", action="store_true")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=2580)
    args = parser.parse_args()
    if args.workers != 10:
        parser.error("approved timing requires10 workers")
    if args.smoke_collection and not args.prepare:
        parser.error("smoke collection is preparation only")
    Runner(args).run()


if __name__ == "__main__":
    main()
