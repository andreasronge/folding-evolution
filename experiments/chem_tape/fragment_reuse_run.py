"""1036 frozen whole-corpus fragment reuse; complete primary and reference rosters."""

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import BANK_SHA, TRAINING, digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder, outputs
from experiments.chem_tape.fragment_library import extract_corpus
from experiments.chem_tape.fragment_operator import validate_edits
from experiments.chem_tape.fragment_run import (
    Runner as BaseRunner,
    CORPORA,
    REPLAY_FIELDS,
    substantive,
)
from experiments.chem_tape.fragment_report import row_key
from experiments.chem_tape.fragment_reuse_report import report
from experiments.chem_tape.then_addition_bank import load, BANK_SHA as TA_SHA
from experiments.chem_tape.then_addition_run import PROVENANCE_SHA

ARMS = ("C", "F", "W")
BASE = 204610091036  # separate billion-sized namespace from 0843's seeds
PREP_TIMEOUT = 1800
SCORE_TIMEOUT = 12300
ADMISSION_SECONDS = 195 * 60
DATA = Path(__file__).with_name("data") / "fragment_reuse_1036"
HISTORY_SHA = "9eee744dbb5728df9da6702bf646f502fdd1eb934cd63f9025c801c3337da0b1"
WHOLE_SHA = "5d199a2e1bac974837333bfa92202a24da3a4f6aa5561f8bac11e3ddd1b4b4f7"


def pinned_history():
    raw = (DATA / "history.json").read_bytes()
    whole = gzip.decompress((DATA / "whole_libraries.json.gz").read_bytes())
    if (
        hashlib.sha256(raw).hexdigest() != HISTORY_SHA
        or hashlib.sha256(whole).hexdigest() != WHOLE_SHA
    ):
        raise ValueError("historical fixture SHA mismatch")
    return json.loads(raw), json.loads(whole)


def target_ids(bank, ta_bank):
    return dict(
        then_addition=ta_bank["selected_ids"],
        holdout=[cid for f in TRAINING for cid in bank["split"]["holdouts"][f]],
    )


def seed(phase, tid, ci, si):
    return (
        BASE
        + phase * 1000000
        + (tid[:2] == "PA") * 100000
        + (int(tid[2:]) - 1) * 10000
        + ci * 200
        + si
    )


def schedule(ids, n):
    return [
        dict(
            phase=phase,
            family=tid[:2],
            corpus=tid,
            cell=cid,
            arm=arm,
            seed=seed(pi, tid, ci, si),
        )
        for pi, phase in enumerate(("then_addition", "holdout"))
        for tid in CORPORA
        for ci, cid in enumerate(ids[phase])
        for si in range(n if pi == 0 else 8)
        for arm in ARMS
    ]


def smoke_schedule(history):
    rows = []
    for pi, (phase, ranks) in enumerate(
        (("then_addition", [0, 5, 10, 15]), ("holdout", [0, 2, 5, 7]))
    ):
        for j, rank in enumerate(ranks):
            ci = pi * 4 + j
            cid = history["history"][phase]["difficulty"][rank]["cell"]
            for si in range(4):
                tid = ("BE" if si % 2 == 0 else "PA") + str((ci * 2 + si // 2) % 8 + 1)
                for arm in ARMS:
                    rows.append(
                        dict(
                            phase="smoke_" + phase,
                            family=tid[:2],
                            corpus=tid,
                            cell=cid,
                            arm=arm,
                            seed=seed(2, tid, ci, si),
                        )
                    )
    if len(rows) != 96 or {r["corpus"] for r in rows} != set(CORPORA):
        raise ValueError("smoke coverage changed")
    return rows


def check_seeds(full, smoke, historical):
    seen = {}
    for r in full + smoke:
        identity = (r["phase"], r["corpus"], r["cell"])
        if r["seed"] in seen and seen[r["seed"]] != identity:
            raise ValueError("seed collision between distinct search pairs")
        seen[r["seed"]] = identity
    if set(seen) & set(historical):
        raise ValueError("fresh seeds overlap historical searches")


def admit(rows, elapsed, workers):
    timings = {}
    for phase in ("then_addition", "holdout"):
        timings[phase] = {}
        for arm in ARMS:
            rs = [r for r in rows if r["phase"] == "smoke_" + phase and r["arm"] == arm]
            if len(rs) != 16:
                raise ValueError("timing roster incomplete")
            timings[phase][arm] = dict(
                n=16,
                solved=sum(r["solved"] for r in rs),
                mean_seconds=float(np.mean([r["seconds"] for r in rs])),
                max_seconds=max(r["seconds"] for r in rs),
                worker_seconds=sum(r["seconds"] for r in rs),
                seconds_per_evaluation=sum(r["seconds"] for r in rs)
                / sum(r["evaluations"] for r in rs),
            )
    candidates = []
    for n in (16, 12):
        projected = (
            1.15
            / workers
            * sum(
                16 * (16 * n if phase == "then_addition" else 8 * 8) * s["mean_seconds"]
                for phase, arms in timings.items()
                for s in arms.values()
            )
        )
        candidates.append(
            dict(
                seeds=n,
                searches_per_arm=256 * n + 1024,
                projected_seconds=projected,
                fits=projected <= ADMISSION_SECONDS,
            )
        )
    selected = next((c for c in candidates if c["fits"]), None)
    return dict(
        admitted=selected is not None and elapsed <= PREP_TIMEOUT,
        selected_seeds=selected["seeds"] if selected else None,
        projected_seconds=selected["projected_seconds"] if selected else None,
        prepare_wall_seconds=elapsed,
        workers=workers,
        timings=timings,
        candidates=candidates,
        smoke_replay_projected_seconds=1.15 / workers * sum(r["seconds"] for r in rows),
        prepare_timeout_seconds=PREP_TIMEOUT,
        scoring_timeout_seconds=SCORE_TIMEOUT,
        rule="timing alone: full projection *1.15/10 <=195min at16 then12 primary seeds; all8 holdout seeds fixed; preparation<=30min",
        rate_caveat="16 timing searches/bank/arm across fixed historical difficulty ranks; not an efficacy sample or precise target-rate forecast",
    )


class Runner(BaseRunner):
    arms = ARMS

    def __init__(self, args):
        super().__init__(args)
        self.ta_bank, ta_cells = load()
        if self.ta_bank["inputs"] != self.bank["inputs"]:
            raise ValueError("bank domains differ")
        self.ids = target_ids(self.bank, self.ta_bank)
        if len(self.ids["then_addition"]) != 16 or len(self.ids["holdout"]) != 8:
            raise ValueError("target roster changed")
        # Only labels/IDs reach search; no canonical or witness.
        self.cells.update(ta_cells)
        self.cells.update(
            {
                c["id"]: dict(id=c["id"], labels=c["labels"])
                for c in self.bank["cells"]
                if c["id"] in self.ids["holdout"]
            }
        )
        self.history, self.reference_libraries = pinned_history()
        self.hashes["fragment_reuse_run.py"] = hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest()
        self.config.update(
            task="2026-10-09-1036",
            arms=ARMS,
            seed_base=BASE,
            implementation_hashes=self.hashes,
            then_addition_sha256=TA_SHA,
            history_sha256=HISTORY_SHA,
            reference_whole_libraries_sha256=WHOLE_SHA,
            method="unchanged C and0843 whole libraries; F/W rate.2 and same library-derived span/start/suffix law; no target filtering",
            scope="then-addition primary; comparison-gate holdouts descriptive reference; both development banks",
        )
        write_json(self.out, "config.json", self.config)
        write_json(
            self.out,
            "target_banks.json",
            dict(then_addition=self.ta_bank, comparison_gate=self.bank),
        )
        write_json(self.out, "historical_provenance.json", self.history["provenance"])
        self.rosters = {str(n): schedule(self.ids, n) for n in (16, 12)}
        self.smoke = smoke_schedule(self.history)
        check_seeds(
            self.rosters["16"],
            self.smoke,
            self.history["historical_seeds"]
            + [r["seed"] for r in self.saved["schedule.json"]],
        )
        write_json(self.out, "candidate_schedules.json", self.rosters)
        write_json(
            self.out,
            "preparation_schedules.json",
            dict(smoke=self.smoke, replay=self.replay_schedule()),
        )

    def replay_schedule(self):
        return [
            dict(
                phase="replay",
                family=r["family"],
                corpus=r["corpus"],
                cell=r["cell"],
                arm="C",
                seed=r["seed"],
            )
            for p in self.history["history"].values()
            for r in p["replays"]
        ]

    def envelope(self, r, off=False):
        fragments = [] if off else self.libraries[r["corpus"]]["fragments"]
        job = (
            self.cells[r["cell"]],
            r["arm"],
            self.corpora[r["corpus"]]["tables"]["C"],
            r["seed"],
            self.config["cap"],
            256,
            self.bank["inputs"],
            "v2_rmin_first",
        )
        return job, r, fragments, self.diagnostic_inputs, off

    def prepare(self):
        collection = [
            r for r in self.saved["search.jsonl"] if r["phase"] == "collection"
        ]
        if len(collection) != 3072 or any(r["arm"] != "G4" for r in collection):
            raise ValueError("source collection roster changed")
        envelopes = [
            (
                tid,
                [r for r in collection if r["corpus"] == tid],
                self.bank["inputs"],
                self.cells,
                self.indices,
            )
            for tid in CORPORA
        ]
        built = []
        extraction_started = time.monotonic()

        def save(record):
            tid, lib = record["corpus"], record["whole_corpus"]
            if (
                lib != self.reference_libraries[tid]
                or digest(lib["fragments"]) != lib["hash"]
            ):
                raise ValueError("0843 library reconstruction mismatch")
            self.libraries[tid] = lib
            built.append(record)
            write_json(self.out, "libraries.json", self.libraries)

        if not run_jobs(self.pool, extract_corpus, envelopes, self.deadline, save):
            raise TimeoutError("library reconstruction incomplete")
        extraction_wall = time.monotonic() - extraction_started
        if set(self.libraries) != set(CORPORA) or any(
            len(lib["fragments"]) != 32 for lib in self.libraries.values()
        ):
            raise ValueError("whole library roster changed")
        write_json(
            self.out, "activity.json", {r["corpus"]: r["activity"] for r in built}
        )
        laws = {}
        padded = {}
        for tid, lib in self.libraries.items():
            counts = Counter(len(f["tokens"]) for f in lib["fragments"])
            laws[tid] = dict(
                length_counts=dict(counts),
                length_probabilities={k: v / 32 for k, v in counts.items()},
                start="uniform integers0..32-length",
                rate=0.2,
                suffix="conditional uniform window+next preimage; decoded suffix retained",
                caveat="W stores no token repertoire; its length schedule is library-derived",
            )
            programs = [
                f["tokens"] + [0] * (32 - len(f["tokens"])) for f in lib["fragments"]
            ]
            values = outputs(programs, self.bank["inputs"], "v2_rmin_first")
            padded[tid] = {
                phase: [
                    dict(
                        fragment_index=i, tokens=lib["fragments"][i]["tokens"], cell=cid
                    )
                    for i, value in enumerate(values)
                    for cid in ids
                    if np.array_equal(value, self.cells[cid]["labels"])
                ]
                for phase, ids in self.ids.items()
            }
        write_json(self.out, "operator_laws.json", laws)
        write_json(
            self.out,
            "padded_solutions.json",
            dict(tests=16 * 32 * 24, hits=padded, filtered=False),
        )
        audit_libraries = {tid + "|whole": lib for tid, lib in self.libraries.items()}
        self.validation["edits"] = validate_edits(
            self.corpora, audit_libraries, arms=("F", "W")
        )
        replayed = self.jobs(self.replay_schedule(), off=True)
        reference = {
            row_key(r): r
            for p in self.history["history"].values()
            for r in p["replays"]
        }
        if len(replayed) != 16 or any(
            substantive(r) != substantive(reference[row_key(r)]) for r in replayed
        ):
            raise ValueError("1548 C operator-off replay changed")
        self.validation["C_replay"] = dict(passed=True, rows=16, fields=REPLAY_FIELDS)
        smoke = self.jobs(self.smoke)
        admission = admit(smoke, time.monotonic() - self.started, self.args.workers)
        self.validation.update(
            passed=True,
            libraries_match_0843=True,
            paired_initial_tokens=True,
            elite_exclusion=True,
            smoke_rows=96,
            library_sizes={k: 32 for k in CORPORA},
        )
        write_json(self.out, "validation.json", self.validation)
        freeze = dict(
            frozen_before_scoring=True,
            implementation_hashes=self.hashes,
            bank_sha256=BANK_SHA,
            then_addition_sha256=TA_SHA,
            source_provenance_sha256=PROVENANCE_SHA,
            history_sha256=HISTORY_SHA,
            libraries_hash=digest(self.libraries),
            operator_laws_hash=digest(laws),
            table_hashes={
                tid: Decoder(r["tables"]["C"]).hash() for tid, r in self.corpora.items()
            },
            candidate_schedule_hashes={n: digest(rs) for n, rs in self.rosters.items()},
            smoke_schedule_hash=digest(self.smoke),
        )
        write_json(self.out, "freeze.json", freeze)
        p = dict(
            admitted=admission["admitted"],
            workers=self.args.workers,
            implementation_hashes=self.hashes,
            freeze=freeze,
            admission=admission,
            validation=self.validation,
            timing_rows=smoke,
            extraction_cost=dict(
                worker_seconds=sum(r["seconds"] for r in built),
                wall_seconds=extraction_wall,
                scope="conservative full reconstruction including activity and legacy LOO libraries; no new source collection",
            ),
            resolution_cost=dict(
                source_collection_worker_seconds_per_corpus=sum(
                    r["seconds"] for r in collection
                )
                / 16,
                library_worker_seconds_per_corpus=sum(r["seconds"] for r in built) / 16,
                historical_C_fit_worker_seconds_per_corpus=sum(
                    r["fit_seconds"] for r in self.corpora.values()
                )
                / 16,
                workers=self.args.workers,
                reporting_queue_seconds=600,
                agent_hours=3,
            ),
            shared_corpus_collection=dict(
                worker_seconds=sum(r["seconds"] for r in collection),
                evaluations=sum(r["evaluations"] for r in collection),
                sunk_for_this_run=True,
            ),
        )
        write_json(self.out, "preparation.json", p)
        print(json.dumps(admission, indent=2), flush=True)
        if not p["admitted"]:
            raise ValueError("runtime admission failed; feasibility stop")
        write_json(
            self.out, "schedule.json", self.rosters[str(admission["selected_seeds"])]
        )

    def score(self):
        if not self.args.preparation:
            raise ValueError("scoring requires admitted preparation")
        path = Path(self.args.preparation)
        raw = path.read_bytes()
        p = json.loads(raw)
        self.libraries = json.loads((path.parent / "libraries.json").read_bytes())
        laws = json.loads((path.parent / "operator_laws.json").read_bytes())
        freeze = p["freeze"]
        n = p["admission"]["selected_seeds"]
        if (
            not p["admitted"]
            or not p["validation"]["passed"]
            or p["workers"] != self.args.workers
            or n not in (16, 12)
            or p["implementation_hashes"] != self.hashes
        ):
            raise ValueError("preparation admission/implementation changed")
        if (
            not freeze["frozen_before_scoring"]
            or freeze["bank_sha256"] != BANK_SHA
            or freeze["then_addition_sha256"] != TA_SHA
            or freeze["source_provenance_sha256"] != PROVENANCE_SHA
            or freeze["history_sha256"] != HISTORY_SHA
            or freeze["libraries_hash"] != digest(self.libraries)
            or self.libraries != self.reference_libraries
            or freeze["operator_laws_hash"] != digest(laws)
            or freeze["candidate_schedule_hashes"]
            != {s: digest(rs) for s, rs in self.rosters.items()}
            or freeze["smoke_schedule_hash"] != digest(self.smoke)
            or freeze["table_hashes"]
            != {
                tid: Decoder(r["tables"]["C"]).hash() for tid, r in self.corpora.items()
            }
        ):
            raise ValueError("frozen source/library/bank/table/roster changed")
        self.config["preparation_sha256"] = hashlib.sha256(raw).hexdigest()
        write_json(self.out, "config.json", self.config)
        for name, value in (
            ("libraries.json", self.libraries),
            ("operator_laws.json", laws),
            ("freeze.json", freeze),
            ("schedule.json", self.rosters[str(n)]),
            ("preparation.json", p),
        ):
            write_json(self.out, name, value)
        smoke = self.jobs(self.smoke)
        refs = {row_key(r): r for r in p["timing_rows"]}
        fields = REPLAY_FIELDS + ("solver", "operator")
        if (
            len(refs) != 96
            or {row_key(r) for r in smoke} != set(refs)
            or any(
                {k: r[k] for k in fields} != {k: refs[row_key(r)][k] for k in fields}
                for r in smoke
            )
        ):
            raise ValueError("smoke handoff replay changed scientific payload")
        write_json(
            self.out,
            "validation.json",
            dict(passed=True, smoke_replay_rows=96, fields=fields),
        )
        if self.args.validate_preparation:
            print(
                "All96 handoff smoke payloads matched; no efficacy searches.",
                flush=True,
            )
            return
        rows = self.jobs(self.rosters[str(n)])
        report(self.out, rows, self.rosters[str(n)], self.libraries, p)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--validate-preparation", action="store_true")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=1680)
    args = parser.parse_args()
    if args.workers != 10:
        parser.error("approved timing admission requires10 workers")
    Runner(args).run()


if __name__ == "__main__":
    main()
