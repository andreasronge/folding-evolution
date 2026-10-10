"""1743 complete four-attempt pipeline; prepare gates precede frozen scoring."""

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
from experiments.chem_tape.composition_search import Decoder, outputs, search
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.fragment_library import extract_windows
from experiments.chem_tape.fragment_operator import BlockOperator, validate_edits
from experiments.chem_tape.fragment_run import (
    Runner as BaseRunner,
    CORPORA,
    REPLAY_FIELDS,
    substantive,
)
from experiments.chem_tape.fragment_report import row_key
from experiments.chem_tape.fragment_reuse_run import (
    pinned_history,
    schedule as historical_schedule,
)
from experiments.chem_tape.small_source_report import report
from experiments.chem_tape.solver_corpus_fit import (
    small_source_counts,
    transition_counts,
    fit_context,
    validate_table,
)
from experiments.chem_tape.then_addition_bank import load, BANK_SHA as TA_SHA

DATA = Path(__file__).with_name("data") / "small_source_1743"
REFERENCE_SHA = "9529407ceae86e197b715aecbf6fd8c9d185ed070c18a5dbb90f257b85552199"
G4_DATA = Path(__file__).with_name("data") / "then_addition_1548_frozen"
G4_SHA = "792282393b1d03cef558f0b3d2fbc1689217b05482154b52851368f80a84d312"
ARMS = ("F", "W")
SCIENTIFIC_FIELDS = REPLAY_FIELDS + ("solver", "operator")


def references():
    raw = (DATA / "provenance.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != REFERENCE_SHA:
        raise ValueError("1036 reference provenance changed")
    provenance = json.loads(raw)
    saved = {}
    for name, sha in provenance["sha256"].items():
        if name == "search.jsonl":
            continue
        raw = gzip.decompress((DATA / (name + ".gz")).read_bytes())
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError("1036 reference SHA mismatch: " + name)
        saved[name] = json.loads(raw)
    raw = gzip.decompress((DATA / "primary.jsonl.gz").read_bytes())
    if hashlib.sha256(raw).hexdigest() != provenance["primary_rows_sha256"]:
        raise ValueError("1036 primary reference changed")
    rows = [json.loads(line) for line in raw.splitlines()]
    old_roster = historical_schedule(
        dict(then_addition=load()[0]["selected_ids"], holdout=[]), 16
    )
    expected = {row_key(r): r for r in old_roster}
    if (
        len(rows) != len(expected)
        or {row_key(r) for r in rows} != set(expected)
        or not saved["validation.json"]["passed"]
        or saved["metadata.json"]["status"] != "done"
        or saved["freeze.json"]["then_addition_sha256"] != TA_SHA
    ):
        raise ValueError("1036 reference incomplete")
    for r in rows:
        if any(r[k] != v for k, v in expected[row_key(r)].items()):
            raise ValueError("1036 roster changed")
    raw = gzip.decompress((G4_DATA / "search.jsonl.gz").read_bytes())
    if hashlib.sha256(raw).hexdigest() != G4_SHA:
        raise ValueError("1548 G4 reference changed")
    g4 = [
        json.loads(line) for line in raw.splitlines() if json.loads(line)["arm"] == "G4"
    ]
    if len(g4) != 256 or len({(r["cell"], r["seed"]) for r in g4}) != 256:
        raise ValueError("1548 G4 reference incomplete")
    return rows, g4, saved, provenance


def roster(ids, n):
    old = historical_schedule(dict(then_addition=ids, holdout=[]), n)
    # Historical schedule orders ordinal si inside corpus/cell, then arms.
    ordinals = defaultdict(dict)
    result = []
    for r in old:
        if r["arm"] not in ARMS:
            continue
        seeds = ordinals[r["corpus"], r["cell"]]
        if r["seed"] not in seeds:
            seeds[r["seed"]] = len(seeds)
        si = seeds[r["seed"]]
        result.append(dict(r, block=si % 4, seed_ordinal=si))
    return result


def smoke_roster(ids):
    # Every corpus x block, a Latin rotation across all sixteen target cells.
    return [
        dict(
            phase="smoke",
            family=tid[:2],
            corpus=tid,
            cell=ids[(ci // 2 + 4 * b + (ci % 2) * 8) % 16],
            block=b,
            seed_ordinal=b,
            arm=arm,
            seed=205610091743 + ci * 100 + b,
        )
        for ci, tid in enumerate(CORPORA)
        for b in range(4)
        for arm in ARMS
    ]


def build_source(envelope):
    tid, block, rows, inputs, cells, indices, *extra = envelope
    source_cells = extra[0] if extra else TRAINING[tid[:2]]
    alphabet = extra[1] if len(extra) > 1 else "v2_rmin_first"
    if len(extra) > 2 or len(source_cells) != len(set(source_cells)):
        raise ValueError("invalid source roster")
    if any(r["cell"] not in source_cells for r in rows):
        raise ValueError("non-training source")
    tick = time.monotonic()
    solved = [r for r in rows if r["solved"]]
    if solved:
        observed = outputs([r["solver"] for r in solved], inputs, alphabet)
        if any(
            not np.array_equal(value, cells[r["cell"]]["labels"])
            for value, r in zip(observed, solved)
        ):
            raise ValueError("source exact solver mismatch")
    verification_seconds = time.monotonic() - tick
    tick = time.monotonic()
    counts, yields = small_source_counts(rows, source_cells)
    table = fit_context(counts)
    sha = validate_table(table)
    fit_seconds = time.monotonic() - tick
    tick = time.monotonic()
    sources = [dict(cell=r["cell"], seed=r["seed"], tape=r["solver"]) for r in solved]
    extracted = extract_windows(
        tid, sources, inputs, cells, indices, source_cells=source_cells, alphabet=alphabet
    )
    extraction_seconds = time.monotonic() - tick
    return dict(
        corpus=tid,
        block=block,
        table=table.tolist(),
        table_hash=sha,
        library=extracted["whole_corpus"],
        activity=extracted["activity"],
        yields=yields,
        empty_cells=[c for c, n in yields.items() if not n],
        attempt_keys=[[r["corpus"], r["cell"], r["seed"]] for r in rows],
        attempts_hash=digest(rows),
        acquisition=dict(
            evaluations=sum(r["evaluations"] for r in rows),
            source_worker_seconds=sum(r["seconds"] for r in rows),
            verification_seconds=verification_seconds,
            fit_seconds=fit_seconds,
            extraction_seconds=extraction_seconds,
        ),
    )


def execute(envelope):
    job, meta, fragments, diagnostic, off = envelope
    operator = (
        None
        if off
        else BlockOperator(
            meta["arm"], fragments, meta["seed"], diagnostic, empty_fallback=True
        )
    )
    row = search(job, return_solver=True, child_transform=operator)
    if row["solved"] and not np.array_equal(
        outputs([row["solver"]], job[6], job[7])[0], job[0]["labels"]
    ):
        raise ValueError("search exact solver mismatch")
    row.update(meta)
    if operator is not None:
        row["operator"] = operator.stats
    return row


class Runner(BaseRunner):
    arms = ARMS

    def __init__(self, args):
        super().__init__(args)
        self.ta, ta_cells = load()
        self.cells.update(ta_cells)
        self.ids = self.ta["selected_ids"]
        self.reference, self.g4, self.old, self.reference_provenance = references()
        _, self.full_libraries = pinned_history()
        if self.old["freeze.json"]["source_provenance_sha256"] != self.config[
            "source_provenance_sha256"
        ] or self.old["freeze.json"]["table_hashes"] != {
            tid: Decoder(self.corpora[tid]["tables"]["C"]).hash() for tid in CORPORA
        }:
            raise ValueError("1036 reference source/decoder mismatch")
        if self.full_libraries != self.old["libraries.json"]:
            raise ValueError("1036 full libraries differ from frozen0843 libraries")
        self.hashes["small_source_run.py"] = hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest()
        self.config.update(
            task="2026-10-09-1743",
            arms=ARMS,
            implementation_hashes=self.hashes,
            then_addition_sha256=TA_SHA,
            reference_sha256=REFERENCE_SHA,
            G4_rows_sha256=G4_SHA,
            method="four disjoint4-attempt acquisitions; alpha50 C; recurrent active windows; suffix kept; empty library uniform3..6 C chains",
            scope="development sources/tasks; externally fitted pipeline; W uses library-derived lengths",
        )
        write_json(self.out, "config.json", self.config)
        write_json(self.out, "target_bank.json", self.ta)
        write_json(self.out, "historical_provenance.json", self.reference_provenance)
        self.builds = {}
        self.smoke = smoke_roster(self.ids)
        self.rosters = {str(n): roster(self.ids, n) for n in (16, 12)}
        if {r["seed"] for r in self.smoke} & (
            {r["seed"] for r in self.reference}
            | {r["seed"] for r in self.saved["schedule.json"]}
        ):
            raise ValueError("diagnostic seed overlap")
        write_json(self.out, "candidate_schedules.json", self.rosters)

    def envelope(self, r, off=False):
        if r["phase"] == "replay":
            tab = self.corpora[r["corpus"]]["tables"]["C"]
            fragments = self.full_libraries[r["corpus"]]["fragments"]
        elif r["phase"] == "replay_G4":
            tab, fragments = tables()["G4"].tolist(), []
        else:
            record = self.builds[r["corpus"] + "|" + str(r["block"])]
            tab, fragments = record["table"], record["library"]["fragments"]
        job = (
            self.cells[r["cell"]],
            r["arm"],
            tab,
            r["seed"],
            self.config["cap"],
            256,
            self.bank["inputs"],
            "v2_rmin_first",
        )
        return job, r, fragments, self.diagnostic_inputs, off

    def jobs(self, schedule, off=False):
        expected = {row_key(r): r for r in schedule}
        if len(expected) != len(schedule):
            raise ValueError("duplicate schedule")
        envelopes = [self.envelope(r, off) for r in schedule]
        table_hashes = {row_key(e[1]): Decoder(e[0][2]).hash() for e in envelopes}
        rows = []
        with (self.out / "search.jsonl").open("a", buffering=1) as stream:

            def save(r):
                key = row_key(r)
                meta = expected.pop(key)
                if (
                    any(r[k] != v for k, v in meta.items())
                    or r["table_hash"] != table_hashes[key]
                ):
                    raise ValueError("search metadata/table mismatch")
                if (
                    r["cap"] != self.config["cap"]
                    or r["pop_size"] != 256
                    or not 0 < r["evaluations"] <= r["cap"]
                    or r["evaluations"] % 256
                    or (not r["solved"] and r["evaluations"] != r["cap"])
                    or r["training_indices"]
                    != np.random.default_rng([r["seed"], 0])
                    .choice(len(self.bank["inputs"]), 64, replace=False)
                    .tolist()
                ):
                    raise ValueError("budget/case draw changed")
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
        if not off:
            groups = defaultdict(list)
            for r in rows:
                groups[r["corpus"], r["cell"], r["seed"]].append(r)
                if r["operator"]["eligible_children"] != (r["generations"] - 1) * 254:
                    raise ValueError("elite edited")
            for rs in groups.values():
                if (
                    len(rs) != 2
                    or {r["arm"] for r in rs} != set(ARMS)
                    or len({r["initial_tokens_hash"] for r in rs}) != 1
                    or len({tuple(r["training_indices"]) for r in rs}) != 1
                ):
                    raise ValueError("paired initial programs/cases changed")
        return sorted(rows, key=row_key)

    def prepare(self):
        collection = [
            r for r in self.saved["search.jsonl"] if r["phase"] == "collection"
        ]
        index = {(r["corpus"], r["cell"], r["seed"]): r for r in collection}
        ordered = defaultdict(list)
        scheduled = [
            r for r in self.saved["schedule.json"] if r["phase"] == "collection"
        ]
        keys = [(r["corpus"], r["cell"], r["seed"]) for r in scheduled]
        if (
            len(index) != 3072
            or len(collection) != 3072
            or len(set(keys)) != 3072
            or set(keys) != set(index)
        ):
            raise ValueError("source attempt keys incomplete/duplicate")
        g4_table_hash = Decoder(tables()["G4"]).hash()
        for r, key in zip(scheduled, keys):
            actual = index[key]
            if any(actual[k] != v for k, v in r.items()) or actual["arm"] != "G4":
                raise ValueError("source schedule provenance mismatch")
            if (
                actual["table_hash"] != g4_table_hash
                or (actual["solver"] is not None) != actual["solved"]
                or actual["cap"] != self.config["cap"]
                or actual["pop_size"] != 256
                or not 0 < actual["evaluations"] <= actual["cap"]
                or (not actual["solved"] and actual["evaluations"] != actual["cap"])
            ):
                raise ValueError("invalid G4 source record")
            ordered[r["corpus"], r["cell"]].append(actual)
        if len(ordered) != 64 or any(len(rs) != 48 for rs in ordered.values()):
            raise ValueError("source allocation changed")
        for tid in CORPORA:
            rs = [r for r in collection if r["corpus"] == tid]
            counts, _ = small_source_counts(rs, TRAINING[tid[:2]])
            legacy, _ = transition_counts(rs, TRAINING[tid[:2]])
            if (
                not np.allclose(counts, legacy, rtol=0, atol=1e-12)
                or Decoder(fit_context(counts)).hash()
                != Decoder(self.corpora[tid]["tables"]["C"]).hash()
            ):
                raise ValueError("legacy full C not reproduced")
        empty, _ = small_source_counts([], TRAINING["BE"])
        if not np.array_equal(fit_context(empty), tables()["G4"]):
            raise ValueError("all-empty estimator did not recover G4")
        self.validation["estimator"] = dict(full_C_hashes=16, all_empty_G4=True)
        envelopes = [
            (
                tid,
                b,
                [
                    r
                    for cid in TRAINING[tid[:2]]
                    for r in ordered[tid, cid][4 * b : 4 * b + 4]
                ],
                self.bank["inputs"],
                self.cells,
                self.indices,
            )
            for tid in CORPORA
            for b in range(4)
        ]

        def save(record):
            self.builds[record["corpus"] + "|" + str(record["block"])] = record
            write_json(self.out, "builds.json", self.builds)

        if (
            not run_jobs(self.pool, build_source, envelopes, self.deadline, save)
            or len(self.builds) != 64
        ):
            raise TimeoutError("source rebuild incomplete")
        audit_corpora = {
            key: dict(tables=dict(C=r["table"])) for key, r in self.builds.items()
        }
        audit_libs = {key + "|whole": r["library"] for key, r in self.builds.items()}
        # validate_edits uses the part before | as corpus ID; assign audit aliases.
        audit_corpora = {
            key.replace("|", "_"): value for key, value in audit_corpora.items()
        }
        audit_libs = {
            key.replace("|", "_") + "|whole": r["library"]
            for key, r in self.builds.items()
            if r["library"]["fragments"]
        }
        self.validation["edits"] = (
            validate_edits(audit_corpora, audit_libs, arms=ARMS) if audit_libs else {}
        )
        # Synthetic empty fallback has identical F/W edits and a uniform length law.
        decoder = Decoder(tables()["G4"])
        original = np.random.default_rng(1743).integers(
            decoder.allele_range, size=(1024, 32), dtype=np.int32
        )
        records = []
        for arm in ARMS:
            op = BlockOperator(arm, [], 1743, empty_fallback=True)
            changed, info = op.edit(original.copy(), decoder, force=True, boundary=True)
            if not np.array_equal(decoder.decode(changed), info["desired"]) or set(
                info["lengths"]
            ) != {3, 4, 5, 6}:
                raise ValueError("empty fallback decode/span failed")
            for i, (start, length) in enumerate(zip(info["starts"], info["lengths"])):
                outside = np.ones(32, dtype=bool)
                outside[start : start + length] = False
                if not np.array_equal(
                    decoder.decode(changed)[i, outside], info["before"][i, outside]
                ):
                    raise ValueError("empty fallback suffix changed")
            records.append(changed)
        if not np.array_equal(*records):
            raise ValueError("empty F/W paths differ")
        self.validation["empty_library_fallback"] = dict(
            passed=True, forced_edits=2048, identical_F_W=True
        )
        replay_refs = []
        for tid in CORPORA:
            first = next(
                r for r in self.reference if r["corpus"] == tid and r["arm"] == "F"
            )
            replay_refs.extend(
                r
                for r in self.reference
                if r["corpus"] == tid
                and r["cell"] == first["cell"]
                and r["seed"] == first["seed"]
                and r["arm"] in ARMS
            )
        replay_schedule = [
            {k: r[k] for k in ("family", "corpus", "cell", "arm", "seed")}
            | dict(phase="replay")
            for r in replay_refs
        ]
        replayed = self.jobs(replay_schedule)
        refs = {row_key(r): r for r in replay_refs}
        if len(replayed) != 32 or any(
            {k: r[k] for k in SCIENTIFIC_FIELDS}
            != {k: refs[row_key(r)][k] for k in SCIENTIFIC_FIELDS}
            for r in replayed
        ):
            raise ValueError("1036 F/W scientific replay failed; stop")
        grefs = [next(r for r in self.g4 if r["cell"] == self.ids[i]) for i in (0, 15)]
        gs = [
            dict(
                phase="replay_G4",
                family="G4",
                corpus="G4",
                cell=r["cell"],
                arm="G4",
                seed=r["seed"],
            )
            for r in grefs
        ]
        greplay = self.jobs(gs, off=True)
        gm = {(r["cell"], r["seed"]): r for r in grefs}
        if any(
            substantive(r) != substantive(gm[r["cell"], r["seed"]]) for r in greplay
        ):
            raise ValueError("1548 G4 scientific replay failed")
        self.validation["historical_replay"] = dict(
            passed=True,
            F=16,
            W=16,
            G4=2,
            fields=SCIENTIFIC_FIELDS,
            calibration={
                a: sum(r["seconds"] for r in replayed + greplay if r["arm"] == a)
                / sum(r["seconds"] for r in replay_refs + grefs if r["arm"] == a)
                for a in ("F", "W", "G4")
            },
            calibration_caveat="same-hardware replay of selected rows; workload-dependent timing ratio, not a universal correction",
        )
        write_json(
            self.out,
            "preparation_schedules.json",
            dict(replay=replay_schedule, G4_replay=gs, smoke=self.smoke),
        )
        smoke_started = time.monotonic()
        smoke = self.jobs(self.smoke)
        smoke_wall = time.monotonic() - smoke_started
        effective_workers = min(
            self.args.workers, sum(r["seconds"] for r in smoke) / smoke_wall
        )
        means = {
            arm: float(np.mean([r["seconds"] for r in smoke if r["arm"] == arm]))
            for arm in ARMS
        }
        candidates = [
            dict(
                seeds=n,
                projected_seconds=1.15
                * 256
                * n
                * sum(means.values())
                / effective_workers,
            )
            for n in (16, 12)
        ]
        selected = next(
            (c for c in candidates if c["projected_seconds"] <= 150 * 60), None
        )
        admission = dict(
            admitted=selected is not None and time.monotonic() - self.started <= 1800,
            selected_seeds=selected["seeds"] if selected else None,
            candidates=candidates,
            projected_seconds=selected["projected_seconds"] if selected else None,
            prepare_seconds=time.monotonic() - self.started,
            workers=self.args.workers,
            mean_worker_seconds=means,
            smoke_wall_seconds=smoke_wall,
            effective_smoke_workers=effective_workers,
            timing_groups={
                f"{arm}|{family}|{b}": dict(
                    n=len(rs), worker_seconds=sum(r["seconds"] for r in rs)
                )
                for arm in ARMS
                for family in TRAINING
                for b in range(4)
                for rs in [
                    [
                        r
                        for r in smoke
                        if r["arm"] == arm and r["family"] == family and r["block"] == b
                    ]
                ]
            },
        )
        self.validation.update(
            passed=True,
            source_attempts=3072,
            selected_attempts=1024,
            paired_initial_programs=True,
        )
        freeze = dict(
            frozen_before_scoring=True,
            implementation_hashes=self.hashes,
            builds_hash=digest(self.builds),
            config_source=self.source,
            reference_sha256=REFERENCE_SHA,
            target_sha256=TA_SHA,
            schedule_hashes={n: digest(rs) for n, rs in self.rosters.items()},
            smoke_hash=digest(self.smoke),
        )
        p = dict(
            admitted=admission["admitted"],
            workers=self.args.workers,
            freeze=freeze,
            validation=self.validation,
            admission=admission,
            timing_rows=smoke,
            full_acquisition={
                tid: dict(
                    evaluations=sum(
                        r["evaluations"] for r in collection if r["corpus"] == tid
                    ),
                    source_worker_seconds=sum(
                        r["seconds"] for r in collection if r["corpus"] == tid
                    ),
                    fit_seconds=self.corpora[tid]["fit_seconds"],
                    extraction_seconds=self.old["preparation.json"]["extraction_cost"][
                        "worker_seconds"
                    ]
                    / 16,
                    verification_seconds=0,
                    verification_caveat="historical extraction includes solver verification; not separately timed",
                )
                for tid in CORPORA
            },
        )
        for name, val in [
            ("validation.json", self.validation),
            ("freeze.json", freeze),
            ("preparation.json", p),
        ]:
            write_json(self.out, name, val)
        print(json.dumps(admission, indent=2), flush=True)
        if not p["admitted"]:
            raise ValueError("runtime admission failed; feasibility stop")
        write_json(self.out, "schedule.json", self.rosters[str(selected["seeds"])])

    def score(self):
        if not self.args.preparation:
            raise ValueError("preparation required")
        path = Path(self.args.preparation)
        p = json.loads(path.read_bytes())
        self.builds = json.loads((path.parent / "builds.json").read_bytes())
        n = p["admission"]["selected_seeds"]
        f = p["freeze"]
        if (
            not p["admitted"]
            or not p["validation"]["passed"]
            or p["workers"] != self.args.workers
            or n not in (16, 12)
            or f["implementation_hashes"] != self.hashes
            or f["builds_hash"] != digest(self.builds)
            or f["config_source"] != self.source
            or f["target_sha256"] != TA_SHA
            or f["reference_sha256"] != REFERENCE_SHA
            or not f["frozen_before_scoring"]
            or f["schedule_hashes"] != {k: digest(rs) for k, rs in self.rosters.items()}
            or f["smoke_hash"] != digest(self.smoke)
        ):
            raise ValueError("frozen preparation changed")
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
            {k: r[k] for k in SCIENTIFIC_FIELDS}
            != {k: refs[row_key(r)][k] for k in SCIENTIFIC_FIELDS}
            for r in smoke
        ):
            raise ValueError("smoke scientific replay changed")
        write_json(
            self.out, "validation.json", dict(passed=True, smoke_replay_rows=len(smoke))
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
            self.reference,
            self.g4,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--validate-preparation", action="store_true")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=1680)
    args = parser.parse_args()
    if args.workers != 10:
        parser.error("approved timing requires10 workers")
    Runner(args).run()


if __name__ == "__main__":
    main()
