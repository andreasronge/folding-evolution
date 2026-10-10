"""2001: frozen table/library crossing, explicit block mode, gated scoring."""

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

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder, outputs, search
from experiments.chem_tape.family_preference_run import (
    load_dg,
    load_ts,
    semantic_bank,
    schedules as old_schedules,
    cross_alias_check,
)
from experiments.chem_tape.fragment_operator import BlockOperator
from experiments.chem_tape.independent_input_bank import ALPHABET, validate
from experiments.chem_tape.independent_input_run import (
    CAP,
    method_hashes,
    validate_source_rows,
)
from experiments.chem_tape.solver_corpus_fit import validate_table

DATA = Path(__file__).with_name("data") / "component_transfer_2001"
ARMS = ("D/D", "T/T", "T/D", "D/T", "D/none", "T/none")
PERMUTATION_SEED = 2001
LIMITS = dict(DG=9000, TS=3600)


def load_saved():
    provenance = json.loads((DATA / "provenance.json").read_text())
    saved = {}
    for name, sha in provenance["hashes"].items():
        raw = gzip.decompress((DATA / (name + ".gz")).read_bytes())
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError("saved artifact hash changed: " + name)
        saved[name] = (
            [json.loads(x) for x in raw.splitlines()]
            if name.endswith(".jsonl")
            else json.loads(raw)
        )
    dg, old, targets, _ = load_dg()
    banks, builds = saved["banks.json"], saved["builds.json"]
    p = saved["preparation.json"]
    if p["preparation_hash"] != digest(
        {k: v for k, v in p.items() if k != "preparation_hash"}
    ):
        raise ValueError("1717 admission changed")
    if not p["admitted"] or p["smoke"] or not p["validation"]["passed"]:
        raise ValueError("not a complete admitted production preparation")
    if banks["DG"] != dg or semantic_bank(banks["TS"]) != semantic_bank(load_ts()):
        raise ValueError("saved semantic banks changed")
    if builds["D"] != old["builds.json"]:
        raise ValueError("D cohort differs from audited original")
    source, _, target = old_schedules(banks, targets)
    if saved["source_schedule.json"] != source:
        raise ValueError("TS acquisition schedule changed")
    rows = saved["first.jsonl"] + saved["adaptive.jsonl"]
    validate_source_rows(rows, source, CAP)
    for name, key in [
        ("first.jsonl", "first_hash"),
        ("adaptive.jsonl", "adaptive_hash"),
    ]:
        ordered = sorted(
            saved[name], key=lambda r: (r["build"], r["cell"], r["seed"], r["arm"])
        )
        if digest(ordered) != p[key]:
            raise ValueError("TS source rows changed")
    if (
        digest(builds) != p["freeze"]["builds_hash"]
        or digest(saved["seed_builds.json"]) != p["freeze"]["seed_builds_hash"]
    ):
        raise ValueError("1717 cohort digest changed")
    current = method_hashes()
    for name, sha in p["freeze"]["method_hashes"].items():
        if current.get(name) != sha:
            raise ValueError("1717 production method changed: " + name)
    by = {(r["cell"], r["seed"]): r for r in rows}
    for cohort in (builds, saved["seed_builds.json"]):
        for owner in ("D", "T"):
            if set(cohort[owner]) != {str(i) for i in range(24)}:
                raise ValueError("incomplete cohort")
            for b, rec in cohort[owner].items():
                if (
                    validate_table(rec["table"]) != rec["table_hash"]
                    or digest(rec["library"]["fragments"]) != rec["library"]["hash"]
                ):
                    raise ValueError("table/library identity changed")
                if owner == "T":
                    fitting = [
                        by[r["cell"], r["seed"]] | dict(corpus="TS" + b)
                        for r in source
                        if r["build"] == int(b)
                        and (cohort is builds or r["phase"] == "first_G4")
                    ]
                    if (
                        rec["attempt_keys"]
                        != [[r["corpus"], r["cell"], r["seed"]] for r in fitting]
                        or digest(fitting) != rec["attempts_hash"]
                    ):
                        raise ValueError("TS fit source membership changed")
    target_meta = {(r["family"], r["cell"], r["arm"], r["seed"]): r for r in target}
    replay = saved["replay.json"]
    if (
        len(replay) != 16
        or len({(r["cell"], r["arm"], r["seed"]) for r in replay}) != 16
    ):
        raise ValueError("incomplete native replay set")
    for r in replay:
        meta = target_meta[(r["family"], r["cell"], r["arm"], r["seed"])]
        if r["arm"] not in ("D", "T") or any(r[k] != v for k, v in meta.items()):
            raise ValueError("historical native replay provenance changed")
    cross_alias_check(
        banks,
        targets + banks["TS"]["split"]["protected"],
        rows + old["first.jsonl"] + old["adaptive.jsonl"],
    )
    return saved, dict(DG=targets, TS=banks["TS"]["split"]["protected"])


def schedules(banks, targets, smoke=False):
    permutation = np.random.default_rng(PERMUTATION_SEED).permutation(24).tolist()

    def make(calibration):
        rows = []
        for fi, family in enumerate(("DG", "TS")):
            cells = (
                banks[family]["split"]["development"]
                if calibration or smoke
                else targets[family]
            )
            if smoke:
                cells = cells[:1]
            for ci, cell in enumerate(cells):
                for pair in [0, 12] if calibration or smoke else range(24):
                    for repeat in range(1 if calibration else 2):
                        seed = (
                            (
                                2200000
                                if calibration
                                else (2300000 if smoke else 2100000)
                            )
                            + 1000 * (8 * fi + ci)
                            + (pair if calibration else 2 * pair + repeat)
                        )
                        for arm in ARMS:
                            table, library = arm.split("/")
                            rows.append(
                                dict(
                                    family=family,
                                    cell=cell,
                                    arm=arm,
                                    pair=pair,
                                    repeat=repeat,
                                    seed=seed,
                                    phase="calibration"
                                    if calibration
                                    else "smoke"
                                    if smoke
                                    else "target",
                                    table_owner=table,
                                    table_build=pair
                                    if table == "D"
                                    else permutation[pair],
                                    library_owner=library,
                                    library_build=None
                                    if library == "none"
                                    else pair
                                    if library == "D"
                                    else permutation[pair],
                                    operator_mode="off"
                                    if library == "none"
                                    else "literal",
                                )
                            )
        return rows

    return permutation, make(True), make(False)


def envelope(meta, saved, cap):
    rec = saved["builds.json"][meta["table_owner"]][str(meta["table_build"])]
    library = (
        []
        if meta["library_owner"] == "none"
        else saved["builds.json"][meta["library_owner"]][str(meta["library_build"])][
            "library"
        ]["fragments"]
    )
    bank = saved["banks.json"][meta["family"]]
    cell = next(c for c in bank["screen"]["cells"] if c["id"] == meta["cell"])
    ix = np.random.default_rng(0).choice(625, 96, replace=False)
    diagnostic = [bank["inputs"][i] for i in ix[:4]]
    job = (
        cell,
        meta["arm"],
        rec["table"],
        meta["seed"],
        cap,
        256,
        bank["inputs"],
        ALPHABET,
    )
    return job, meta, library, diagnostic


def execute(e):
    job, meta, library, diagnostic = e
    mode = meta["operator_mode"]
    if mode not in ("off", "literal") or (mode == "off" and library):
        raise ValueError("invalid explicit operator mode")
    operator = (
        None
        if mode == "off"
        else BlockOperator(
            "F",
            library,
            meta["seed"],
            diagnostic,
            empty_fallback=True,
            alphabet=ALPHABET,
        )
    )
    row = search(job, return_solver=True, child_transform=operator, measure_exact=True)
    if row["solved"] and not np.array_equal(
        outputs([row["solver"]], job[6], ALPHABET)[0], job[0]["labels"]
    ):
        raise ValueError("solver D625 verification failed")
    row.update(meta)
    row.update(
        alphabet=ALPHABET,
        library_hash=digest(library),
        empty_library_fallback=mode == "literal" and not library,
        block_events=0 if operator is None else operator.stats["edited_children"],
        operator=None if operator is None else operator.stats,
    )
    return row


def validate_rows(rows, schedule, saved, cap):
    def key(r):
        return r["family"], r["cell"], r["arm"], r["seed"]

    by = {key(r): r for r in rows}
    if len(by) != len(rows) or set(by) != {key(r) for r in schedule}:
        raise ValueError("missing/duplicate search rows")
    initial = {}
    for meta in schedule:
        r = by[key(meta)]
        e = envelope(meta, saved, cap)
        if (
            any(r[k] != v for k, v in meta.items())
            or r["table_hash"] != Decoder(e[0][2]).hash()
            or r["library_hash"] != digest(e[2])
        ):
            raise ValueError("component provenance mismatch")
        if (
            r["cap"] != cap
            or r["pop_size"] != 256
            or not 0 < r["evaluations"] <= cap
            or r["evaluations"] % 256
            or (not r["solved"] and r["evaluations"] != cap)
            or (r["solver"] is not None) != r["solved"]
        ):
            raise ValueError("invalid search budget")
        if (
            r["training_indices"]
            != np.random.default_rng([r["seed"], 0])
            .choice(625, 64, replace=False)
            .tolist()
        ):
            raise ValueError("training RNG changed")
        if meta["operator_mode"] == "off":
            if r["operator"] is not None or r["block_events"] != 0:
                raise ValueError("bare table used blocks")
        elif r["operator"]["eligible_children"] != (r["generations"] - 1) * 254:
            raise ValueError("operator boundary changed")
        k = (meta["table_owner"], meta["table_build"], meta["seed"])
        if initial.setdefault(k, r["initial_tokens_hash"]) != r["initial_tokens_hash"]:
            raise ValueError("same table/seed initialization differs")
    return sorted(rows, key=key)


def project(rows, batches, score, workers):
    result = {}
    for family in ("DG", "TS"):
        rs = [r for r in rows if r["family"] == family]
        rates = {
            a: float(np.mean([r["seconds"] for r in rs if r["arm"] == a])) for a in ARMS
        }
        effective = min(
            workers, sum(r["seconds"] for r in rs) / batches[family]["wall_seconds"]
        )
        total = sum(r["family"] == family for r in score)
        worker_projection = (
            sum(rates[r["arm"]] for r in score if r["family"] == family) / effective
        )
        wall_projection = batches[family]["wall_seconds"] * total / len(rs)
        projected = 1.3 * max(worker_projection, wall_projection) + 120
        result[family] = dict(
            rates=rates,
            effective_workers=effective,
            projected_seconds=projected,
            limit_seconds=LIMITS[family] - 30,
            admitted=projected <= LIMITS[family] - 30,
            solved={a: sum(r["solved"] for r in rs if r["arm"] == a) for a in ARMS},
            max_search_seconds=max(r["seconds"] for r in rs),
            max_exact_check_seconds=max(r["exact_check_max_seconds"] for r in rs),
        )
    return result


class Runner:
    def __init__(self, args):
        self.args = args
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 30
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("fresh RUN_DIR required")
        self.saved, targets = load_saved()
        permutation, self.calibration, self.schedule = schedules(
            self.saved["banks.json"], targets, args.smoke
        )
        self.cap = 8192 if args.smoke else CAP
        self.freeze = dict(
            task="2026-10-10-2001",
            smoke=args.smoke,
            cap=self.cap,
            permutation=permutation,
            permutation_seed=PERMUTATION_SEED,
            targets=targets,
            workers=args.workers,
            builds_hash=digest(self.saved["builds.json"]),
            banks_hash=digest(self.saved["banks.json"]),
            calibration_hash=digest(self.calibration),
            schedule_hash=digest(self.schedule),
            method_hashes=method_hashes(),
            artifact_provenance=json.loads((DATA / "provenance.json").read_text()),
        )
        self.batches = {}
        write_json(
            self.out,
            "config.json",
            dict(
                arguments=vars(args),
                git_commit=subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], text=True
                ).strip(),
                cap=self.cap,
                population=256,
                exact_inputs=625,
            ),
        )
        write_json(self.out, "method_freeze.json", self.freeze)
        write_json(self.out, "schedule.json", self.schedule)
        write_json(self.out, "calibration_schedule.json", self.calibration)

    def jobs(self, schedule, filename, phase, worker=execute, envelopes=None):
        tick = time.monotonic()
        rows = []
        with (self.out / filename).open("w", buffering=1) as stream:

            def save(row):
                rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                write_json(
                    self.out,
                    "progress.json",
                    dict(phase=phase, completed=len(rows), total=len(schedule)),
                )

            if not run_jobs(
                self.pool,
                worker,
                envelopes or [envelope(m, self.saved, self.cap) for m in schedule],
                self.deadline,
                save,
            ):
                raise TimeoutError("incomplete batch: " + phase)
        wall = time.monotonic() - tick
        self.batches[phase] = dict(
            wall_seconds=wall,
            jobs=len(rows),
            worker_seconds=sum(r["seconds"] for r in rows),
            exact_check_seconds=sum(r["exact_check_seconds"] for r in rows),
            max_exact_check_seconds=max(r["exact_check_max_seconds"] for r in rows),
        )
        write_json(self.out, "timing.json", self.batches)
        return rows

    def replay(self):
        expected = self.saved["replay.json"]
        metas = []
        for r in expected:
            m = {
                k: r[k]
                for k in (
                    "family",
                    "cell",
                    "arm",
                    "seed",
                    "build",
                    "ordinal",
                    "phase",
                    "alphabet",
                )
            }
            m.update(
                table_owner=r["arm"],
                table_build=r["build"],
                library_owner=r["arm"],
                library_build=r["build"],
                operator_mode="literal",
            )
            metas.append(m)
        actual = self.jobs(
            metas,
            "replay.jsonl",
            "replay",
            envelopes=[envelope(m, self.saved, CAP) for m in metas],
        )
        by = {(r["cell"], r["arm"], r["seed"]): r for r in actual}
        ignored = {
            "seconds",
            "budget_seconds",
            "decode_seconds",
            "exact_check_seconds",
            "exact_check_max_seconds",
        }
        for old in expected:
            new = by[old["cell"], old["arm"], old["seed"]]
            changed = [k for k in old if k not in ignored and old[k] != new[k]]
            if changed:
                raise ValueError("native replay mismatch: " + str(changed))
        return dict(rows=16, passed=True, excluded_timing_fields=sorted(ignored))

    def prepare(self):
        replay = self.replay()
        validation = validate(
            [
                c
                for b in self.saved["banks.json"].values()
                for c in b["screen"]["cells"]
            ],
            random_count=100 if self.args.smoke else 10000,
        )
        rows = []
        for family in ("DG", "TS"):
            subset = [r for r in self.calibration if r["family"] == family]
            rows += self.jobs(subset, "calibration_" + family + ".jsonl", family)
        rows = validate_rows(rows, self.calibration, self.saved, self.cap)
        projection = project(rows, self.batches, self.schedule, self.args.workers)
        elapsed = time.monotonic() - self.started
        p = dict(
            freeze=self.freeze,
            validation=validation,
            replay=replay,
            projection=projection,
            calibration_rows_hash=digest(rows),
            batches=self.batches,
            prepare_seconds=elapsed,
            admitted=all(v["admitted"] for v in projection.values())
            and elapsed <= self.args.deadline_seconds - 30,
            targets_scored=False,
        )
        p["preparation_hash"] = digest(p)
        write_json(self.out, "preparation.json", p)
        print(
            json.dumps(
                dict(admitted=p["admitted"], projection=projection, elapsed=elapsed)
            ),
            flush=True,
        )
        if not p["admitted"]:
            (self.out / "infeasible.md").write_text(
                "Measured complete design exceeds funded timeouts; return to strategy.\n"
                + json.dumps(projection, indent=2)
                + "\n"
            )

    def score(self):
        parent = Path(self.args.preparation).parent
        p = json.loads(Path(self.args.preparation).read_text())
        if (
            p["preparation_hash"]
            != digest({k: v for k, v in p.items() if k != "preparation_hash"})
            or p["freeze"] != self.freeze
        ):
            raise ValueError("preparation freeze changed")
        rows = []
        for f in ("DG", "TS"):
            rows += [
                json.loads(x)
                for x in (parent / ("calibration_" + f + ".jsonl"))
                .read_text()
                .splitlines()
            ]
        rows = validate_rows(rows, self.calibration, self.saved, self.cap)
        if (
            digest(rows) != p["calibration_rows_hash"]
            or project(rows, p["batches"], self.schedule, self.args.workers)
            != p["projection"]
        ):
            raise ValueError("calibration/admission changed")
        admitted = (
            all(v["admitted"] for v in p["projection"].values())
            and p["prepare_seconds"] <= 1770
        )
        if (
            p["admitted"] != admitted
            or not p["validation"]["passed"]
            or not p["replay"]["passed"]
        ):
            raise ValueError("invalid admission record")
        if not admitted:
            write_json(
                self.out,
                "result.json",
                dict(
                    status="feasibility_stop",
                    targets_scored=False,
                    projection=p["projection"],
                ),
            )
            (self.out / "report.md").write_text(
                "Admission failed; no target scoring. Return to strategy.\n"
            )
            return
        family = self.args.family
        selected = [r for r in self.schedule if r["family"] == family]
        rows = validate_rows(
            self.jobs(selected, "search.jsonl", "score"), selected, self.saved, self.cap
        )
        write_json(self.out, "preparation.json", p)
        if family == "TS":
            dg_parent = Path(self.args.dg_score)
            if (
                json.loads((dg_parent / "method_freeze.json").read_text())
                != self.freeze
                or json.loads((dg_parent / "preparation.json").read_text()) != p
            ):
                raise ValueError("DG score provenance differs")
            dg_rows = [
                json.loads(x)
                for x in (dg_parent / "search.jsonl").read_text().splitlines()
            ]
            dg_schedule = [r for r in self.schedule if r["family"] == "DG"]
            dg_rows = validate_rows(dg_rows, dg_schedule, self.saved, self.cap)
            if (
                digest(dg_rows)
                != json.loads((dg_parent / "result.json").read_text())[
                    "search_rows_hash"
                ]
            ):
                raise ValueError("DG score rows changed")
            rows += dg_rows
            rows = validate_rows(rows, self.schedule, self.saved, self.cap)
        from experiments.chem_tape.component_transfer_report import report

        report(self.out, rows, self.saved, p, self.batches, self.args.smoke)

    def run(self):
        pool = mp.get_context("spawn").Pool(self.args.workers)
        self.pool = pool
        try:
            self.prepare() if self.args.prepare else self.score()
        except BaseException:
            pool.terminate()
            pool.join()
            raise
        else:
            pool.close()
            pool.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--family", choices=("DG", "TS"))
    parser.add_argument("--dg-score")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=1800)
    args = parser.parse_args()
    if (
        args.workers != 10
        or args.deadline_seconds <= 30
        or (
            not args.prepare
            and (
                not args.preparation
                or not args.family
                or (args.family == "TS" and not args.dg_score)
            )
        )
    ):
        parser.error(
            "requires 10 workers and prepare or prepared family scoring; TS requires DG score"
        )
    Runner(args).run()


if __name__ == "__main__":
    main()
