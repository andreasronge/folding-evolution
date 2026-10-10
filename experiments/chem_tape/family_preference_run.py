"""1717 unchanged A8 acquisition, independently fitted DG/TS crossed scoring."""

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape.branch_sum_bank import build as build_bank, validate_bank
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.independent_input_bank import ALPHABET, validate
from experiments.chem_tape.independent_input_run import (
    Runner as BaseRunner,
    load_frozen,
    method_hashes,
    schedules as dg_schedules,
    validate_source_rows,
    source_summary,
    CAP,
)
from experiments.chem_tape.small_source_run import build_source
from experiments.chem_tape.solver_corpus_fit import validate_table

DATA = Path(__file__).with_name("data") / "family_preference_1717"
TS_SHA = "fdd025c3f3d8f052b7048c610e0597d0c2cae72bc1a76b4c55344d79df6d3dc9"


def load_ts():
    raw = gzip.decompress((DATA / "ts_bank.json.gz").read_bytes())
    if hashlib.sha256(raw).hexdigest() != TS_SHA:
        raise ValueError("frozen TS semantic bank changed")
    bank = json.loads(raw)
    validate_bank(bank)
    return bank


def semantic_bank(bank):
    return {
        k: bank[k]
        for k in (
            "name",
            "alphabet",
            "inputs",
            "maximum_separated",
            "clique_ids",
            "split",
        )
    } | dict(cells=bank["screen"]["cells"])


def load_dg():
    provenance = json.loads((DATA / "provenance.json").read_text())
    saved = {}
    for name, sha in provenance["hashes"].items():
        raw = gzip.decompress((DATA / (name + ".gz")).read_bytes())
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError("DG frozen raw hash changed: " + name)
        saved[name] = (
            [json.loads(line) for line in raw.splitlines()]
            if name.endswith(".jsonl")
            else json.loads(raw)
        )
    bank, _ = load_frozen()
    p = saved["preparation.json"]
    if p["preparation_hash"] != digest(
        {k: v for k, v in p.items() if k != "preparation_hash"}
    ):
        raise ValueError("DG admission hash changed")
    if saved["config.json"]["git_commit"] != provenance["commit"] or not p["admitted"]:
        raise ValueError("DG production provenance changed")
    for n, key in [
        ("builds.json", "builds_hash"),
        ("seed_builds.json", "seed_builds_hash"),
        ("validation.json", "validation_hash"),
    ]:
        if digest(saved[n]) != p[key]:
            raise ValueError("DG frozen digest changed: " + n)
    schedule, prior_score = dg_schedules(bank, protected=True)
    if (
        saved["source_schedule.json"] != schedule
        or saved["schedule.json"] != prior_score
    ):
        raise ValueError("DG source/score schedule changed")
    rows = saved["first.jsonl"] + saved["adaptive.jsonl"]
    validate_source_rows(rows, schedule, CAP)
    by = {(r["cell"], r["seed"]): r for r in rows}
    current = method_hashes()
    for name, sha in saved["method_freeze.json"]["method_hashes"].items():
        if current.get(name) != sha:
            raise ValueError("unchanged A8 production method changed: " + name)
    for records in (saved["builds.json"], saved["seed_builds.json"]):
        if set(records) != {str(b) for b in range(24)}:
            raise ValueError("incomplete DG cohort")
        for b, rec in records.items():
            if (
                validate_table(rec["table"]) != rec["table_hash"]
                or digest(rec["library"]["fragments"]) != rec["library"]["hash"]
            ):
                raise ValueError("DG fit/library hash mismatch")
            keys = rec["attempt_keys"]
            fitting_rows = [
                by[r["cell"], r["seed"]] | dict(corpus="DG" + b)
                for r in schedule
                if r["build"] == int(b)
                and (records is saved["builds.json"] or r["phase"] == "first_G4")
            ]
            if (
                keys != [[r["corpus"], r["cell"], r["seed"]] for r in fitting_rows]
                or digest(fitting_rows) != rec["attempts_hash"]
            ):
                raise ValueError("DG pooled fit membership changed")
            if any(
                cid not in bank["split"]["source"] or by[cid, seed]["build"] != int(b)
                for _, cid, seed in keys
            ):
                raise ValueError("DG fit source contamination")
    used = set(sum(bank["split"].values(), []))
    target = [cid for cid in bank["clique_ids"] if cid not in used]
    if len(target) != 8 or any(r["cell"] in target for r in schedule + prior_score):
        raise ValueError("DG spare targets exposed")
    return bank, saved, target, provenance


def schedules(banks, dg_targets, smoke=False):
    B = 2 if smoke else 24
    base = 1300000 if smoke else 900000
    source = [
        dict(
            alphabet=ALPHABET,
            phase=phase,
            family="TS",
            build=b,
            cell=cid,
            arm="G4" if p == 0 else "T",
            attempt=a,
            seed=base + 100000 * p + 1000 * b + 10 * ci + a,
        )
        for p, phase in enumerate(("first_G4", "adaptive"))
        for b in range(B)
        for ci, cid in enumerate(banks["TS"]["split"]["source"])
        for a in range(4)
    ]

    def target(part, base, count):
        rows = []
        for fi, family in enumerate(("DG", "TS")):
            cells = (
                (dg_targets if family == "DG" else banks["TS"]["split"]["protected"])
                if part == "target"
                else banks[family]["split"]["development"]
            )
            for ci, cid in enumerate(cells):
                for ordinal in range(count):
                    for arm in ("G4", "D", "T"):
                        rows.append(
                            dict(
                                alphabet=ALPHABET,
                                phase=part,
                                family=family,
                                cell=cid,
                                arm=arm,
                                build=ordinal // 2,
                                ordinal=ordinal,
                                seed=base + 1000 * (8 * fi + ci) + ordinal,
                            )
                        )
        return rows

    calibration = target("development", 1500000 if smoke else 1100000, 4)
    if not smoke:
        # Spread the development-only price check across the complete cohorts.
        for row in calibration:
            fi = ("DG", "TS").index(row["family"])
            ci = banks[row["family"]]["split"]["development"].index(row["cell"])
            row["build"] = (4 * (4 * fi + ci) + row["ordinal"]) % B
    score = target(
        "development" if smoke else "target", 1600000 if smoke else 1200000, 2 * B
    )
    if len({r["seed"] for r in source}) != len(source) or {
        r["seed"] for r in source
    } & {r["seed"] for r in calibration + score}:
        raise ValueError("source/target seed overlap")
    return source, calibration, score


def cross_alias_check(banks, targets, source_rows):
    sources = [
        c
        for f, b in banks.items()
        for c in b["screen"]["cells"]
        if c["id"] in b["split"]["source"]
    ]
    cells = [
        c for b in banks.values() for c in b["screen"]["cells"] if c["id"] in targets
    ]
    labels = np.asarray([c["labels"] for c in cells])
    if any(np.any(np.all(labels == c["labels"], axis=1)) for c in sources):
        raise ValueError("target solved by a source behaviour")
    solved = [r["solver"] for r in source_rows if r["solved"]]
    if solved:
        values = outputs(solved, banks["DG"]["inputs"], ALPHABET)
        if any(np.any(np.all(labels == v, axis=1)) for v in values):
            raise ValueError("target solved by an acquired source solver")


class Runner(BaseRunner):
    def __init__(self, args):
        self.args = args
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 30
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("fresh RUN_DIR required")
        dg, self.dg_saved, self.dg_targets, self.dg_provenance = load_dg()
        self.builds = self.dg_saved["builds.json"]
        self.dg_builds = self.builds
        self.batches = {}
        self.nbuild = 2 if args.smoke or args.pilot else 24
        self.cap = 8192 if args.smoke else CAP
        self.hashes = method_hashes()
        self.indices = np.random.default_rng(0).choice(625, 96, replace=False).tolist()
        self.diagnostic = [dg["inputs"][i] for i in self.indices[:4]]
        if args.prepare:
            if args.bank:
                # Researcher smoke may reuse the independently completed semantic screen.
                if not (args.smoke or args.pilot):
                    raise ValueError("--bank reuse is smoke only")
                ts = json.loads(Path(args.bank).read_text())
            else:
                ts = build_bank(min(self.deadline, self.started + 1200))
        else:
            ts = json.loads((Path(args.preparation).parent / "banks.json").read_text())[
                "TS"
            ]
        validate_bank(ts)
        if semantic_bank(ts) != semantic_bank(load_ts()):
            raise ValueError(
                "regenerated TS bank differs from performance-blind roster"
            )
        self.banks = dict(DG=dg, TS=ts)
        self.bank = dg
        self.cells = {
            c["id"]: c for b in self.banks.values() for c in b["screen"]["cells"]
        }
        self.source_schedule, self.calibration, self.score_schedule = schedules(
            self.banks, self.dg_targets, args.smoke or args.pilot
        )
        self.ts_builds = {}
        self.seed_builds = {}
        self.freeze = dict(
            task="2026-10-10-1717",
            smoke=args.smoke,
            pilot=args.pilot,
            cap=self.cap,
            banks_hash=digest(self.banks),
            dg_provenance=self.dg_provenance,
            targets=dict(DG=self.dg_targets, TS=ts["split"]["protected"]),
            sources_hash=digest(self.source_schedule),
            calibration_hash=digest(self.calibration),
            score_hash=digest(self.score_schedule),
            method_hashes=self.hashes,
            fragment_indices=self.indices,
            workers=args.workers,
        )
        self.config = dict(
            task="2026-10-10-1717",
            smoke=args.smoke,
            arguments=vars(args),
            cap=self.cap,
            alphabet=ALPHABET,
            population=256,
            lexicase_cases=64,
            exact_inputs=625,
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            recipe="unchanged 7244fa1 A8 external fit + literal fragments",
            target_performance_scored=False,
        )
        for name, value in [
            ("config.json", self.config),
            ("banks.json", self.banks),
            ("method_freeze.json", self.freeze),
            ("source_schedule.json", self.source_schedule),
            ("calibration_schedule.json", self.calibration),
            ("schedule.json", self.score_schedule),
        ]:
            write_json(self.out, name, value)

    def envelope(self, meta):
        if meta["arm"] == "G4":
            table, fragments = tables()["G4"].tolist(), []
        else:
            cohort = (
                self.dg_builds
                if meta["arm"] == "D"
                else (
                    self.seed_builds if meta["phase"] == "adaptive" else self.ts_builds
                )
            )
            rec = cohort[str(meta["build"])]
            table, fragments = rec["table"], rec["library"]["fragments"]
        return (
            (
                self.cells[meta["cell"]],
                meta["arm"],
                table,
                meta["seed"],
                self.cap,
                256,
                self.bank["inputs"],
                ALPHABET,
            ),
            meta,
            fragments,
            self.diagnostic,
        )

    def rebuild(self, rows, phase):
        tick = time.monotonic()
        index = {(r["cell"], r["seed"]): r for r in rows}
        scheduled = [r for r in self.source_schedule if (r["cell"], r["seed"]) in index]
        groups = {
            str(b): [
                index[r["cell"], r["seed"]] | dict(corpus="TS" + str(b))
                for r in scheduled
                if r["build"] == b
            ]
            for b in range(self.nbuild)
        }
        jobs = [
            (
                "TS" + b,
                b,
                rs,
                self.bank["inputs"],
                self.cells,
                self.indices,
                self.banks["TS"]["split"]["source"],
                ALPHABET,
            )
            for b, rs in groups.items()
        ]
        records = {}

        def save(rec):
            b = rec["block"]
            if rec["attempt_keys"] != [
                [r["corpus"], r["cell"], r["seed"]] for r in groups[b]
            ]:
                raise ValueError("TS fit membership changed")
            validate_table(rec["table"])
            records[b] = rec

        if (
            not run_jobs(self.pool, build_source, jobs, self.deadline, save)
            or len(records) != self.nbuild
        ):
            raise TimeoutError("incomplete TS fitting")
        self.batches[phase] = dict(
            jobs=self.nbuild,
            wall_seconds=time.monotonic() - tick,
            worker_seconds=sum(
                sum(
                    r["acquisition"][k]
                    for k in (
                        "verification_seconds",
                        "fit_seconds",
                        "extraction_seconds",
                    )
                )
                for r in records.values()
            ),
        )
        return records

    def prepare(self):
        cells = [c for b in self.banks.values() for c in b["screen"]["cells"]]
        validation = validate(cells, random_count=100 if self.args.smoke else 10000)
        empty = build_source(
            (
                "TS-empty",
                0,
                [],
                self.bank["inputs"],
                self.cells,
                self.indices,
                self.banks["TS"]["split"]["source"],
                ALPHABET,
            )
        )
        if (
            empty["table"] != tables()["G4"].tolist()
            or empty["library"]["fragments"]
            or len(empty["empty_cells"]) != 4
        ):
            raise ValueError("TS empty corpus fallback changed")
        cross_alias_check(
            self.banks,
            self.dg_targets + self.banks["TS"]["split"]["protected"],
            self.dg_saved["first.jsonl"] + self.dg_saved["adaptive.jsonl"],
        )
        write_json(self.out, "validation.json", validation)
        first = self.jobs(
            [r for r in self.source_schedule if r["phase"] == "first_G4"],
            "first.jsonl",
            "first_G4",
        )
        self.seed_builds = self.rebuild(first, "intermediate_fit")
        adaptive = self.jobs(
            [r for r in self.source_schedule if r["phase"] == "adaptive"],
            "adaptive.jsonl",
            "adaptive",
        )
        self.ts_builds = self.rebuild(first + adaptive, "final_fit")
        cross_alias_check(
            self.banks,
            self.dg_targets + self.banks["TS"]["split"]["protected"],
            first + adaptive,
        )
        write_json(self.out, "builds.json", dict(D=self.dg_builds, T=self.ts_builds))
        write_json(
            self.out,
            "seed_builds.json",
            dict(D=self.dg_saved["seed_builds.json"], T=self.seed_builds),
        )
        write_json(
            self.out,
            "source_summary.json",
            dict(
                D=source_summary(
                    self.dg_saved["first.jsonl"],
                    self.dg_saved["adaptive.jsonl"],
                    self.dg_saved["seed_builds.json"],
                    self.dg_builds,
                ),
                T=source_summary(first, adaptive, self.seed_builds, self.ts_builds),
            ),
        )
        calibration = self.jobs(self.calibration, "calibration.jsonl", "calibration")
        rates = {
            f: {
                a: float(
                    np.mean(
                        [
                            r["seconds"]
                            for r in calibration
                            if r["family"] == f and r["arm"] == a
                        ]
                    )
                )
                for a in ("G4", "D", "T")
            }
            for f in ("DG", "TS")
        }
        effective = min(
            self.args.workers, self.batches["calibration"]["effective_workers"]
        )
        projected = (
            1.3
            * sum(rates[r["family"]][r["arm"]] for r in self.score_schedule)
            / effective
            + 90
        )
        elapsed = time.monotonic() - self.started
        admitted = projected <= 8370 and elapsed <= 4770
        reasons = []
        if projected > 8370:
            reasons.append("projected scoring exceeds140minute timeout")
        if elapsed > 4770:
            reasons.append("preparation exceeds80minute timeout")
        self.freeze["builds_hash"] = digest(dict(D=self.dg_builds, T=self.ts_builds))
        self.freeze["seed_builds_hash"] = digest(
            dict(D=self.dg_saved["seed_builds.json"], T=self.seed_builds)
        )
        write_json(self.out, "method_freeze.json", self.freeze)
        p = dict(
            admitted=admitted,
            reasons=reasons,
            smoke=self.args.smoke,
            freeze=self.freeze,
            validation=validation,
            calibration_hash=digest(calibration),
            first_hash=digest(first),
            adaptive_hash=digest(adaptive),
            rates=rates,
            effective_workers=effective,
            score_projected_seconds=projected,
            prepare_seconds=elapsed,
            batches=self.batches,
            limits=dict(preparation=4770, score=8370),
            targets_scored=False,
        )
        p["preparation_hash"] = digest(p)
        write_json(self.out, "preparation.json", p)
        print(
            json.dumps(
                dict(
                    admitted=admitted,
                    rates=rates,
                    projected_seconds=projected,
                    prepare_seconds=elapsed,
                )
            ),
            flush=True,
        )

    def score(self):
        parent = Path(self.args.preparation).parent
        p = json.loads(Path(self.args.preparation).read_text())
        if p["preparation_hash"] != digest(
            {k: v for k, v in p.items() if k != "preparation_hash"}
        ):
            raise ValueError("admission record changed")
        cohort = json.loads((parent / "builds.json").read_text())
        intermediate = json.loads((parent / "seed_builds.json").read_text())
        self.freeze["builds_hash"] = digest(cohort)
        self.freeze["seed_builds_hash"] = digest(intermediate)
        if (
            self.freeze != p["freeze"]
            or not p["validation"]["passed"]
            or p["smoke"] != self.args.smoke
        ):
            raise ValueError("method/build/bank/seed freeze changed")
        preparation_rows = {}
        for filename, key in [
            ("first.jsonl", "first_hash"),
            ("adaptive.jsonl", "adaptive_hash"),
            ("calibration.jsonl", "calibration_hash"),
        ]:
            rows = sorted(
                [
                    json.loads(line)
                    for line in (parent / filename).read_text().splitlines()
                ],
                key=lambda r: (r["build"], r["cell"], r["seed"], r["arm"]),
            )
            if digest(rows) != p[key]:
                raise ValueError("preparation search rows changed")
            preparation_rows[filename] = rows
        validate_source_rows(
            preparation_rows["first.jsonl"] + preparation_rows["adaptive.jsonl"],
            self.source_schedule,
            self.cap,
        )
        calibration = preparation_rows["calibration.jsonl"]
        expected = {(r["cell"], r["arm"], r["seed"]): r for r in self.calibration}
        if len(calibration) != len(expected) or any(
            any(
                r[k] != v for k, v in expected[(r["cell"], r["arm"], r["seed"])].items()
            )
            for r in calibration
        ):
            raise ValueError("calibration schedule changed")
        rates = {
            f: {
                a: float(
                    np.mean(
                        [
                            r["seconds"]
                            for r in calibration
                            if r["family"] == f and r["arm"] == a
                        ]
                    )
                )
                for a in ("G4", "D", "T")
            }
            for f in ("DG", "TS")
        }
        effective = min(
            self.args.workers,
            sum(r["seconds"] for r in calibration)
            / p["batches"]["calibration"]["wall_seconds"],
        )
        projected = (
            1.3
            * sum(rates[r["family"]][r["arm"]] for r in self.score_schedule)
            / effective
            + 90
        )
        if (
            rates != p["rates"]
            or not np.isclose(effective, p["effective_workers"])
            or not np.isclose(projected, p["score_projected_seconds"])
            or p["admitted"] != (projected <= 8370 and p["prepare_seconds"] <= 4770)
        ):
            raise ValueError("recorded admission disagrees with measured cost")
        write_json(self.out, "method_freeze.json", self.freeze)
        if not p["admitted"]:
            write_json(
                self.out,
                "result.json",
                dict(
                    status="feasibility_stop",
                    reasons=p["reasons"],
                    targets_scored=False,
                ),
            )
            (self.out / "report.md").write_text(
                "Admission failed; no target search. Return to strategy.\n"
                + "\n".join(p["reasons"])
            )
            return
        self.dg_builds, self.ts_builds = cohort["D"], cohort["T"]
        rows = self.jobs(self.score_schedule, "search.jsonl", "score")
        self.config["target_performance_scored"] = not (
            self.args.smoke or self.args.pilot
        )
        write_json(self.out, "config.json", self.config)
        write_json(self.out, "preparation.json", p)
        write_json(self.out, "builds.json", cohort)
        write_json(self.out, "seed_builds.json", intermediate)
        from experiments.chem_tape.family_preference_report import report

        report(
            self.out,
            rows,
            cohort,
            intermediate,
            p,
            self.batches["score"],
            self.args.smoke or self.args.pilot,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--bank")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--pilot",
        action="store_true",
        help="separate2-build full-cap development calibration; never targets",
    )
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=4800)
    args = parser.parse_args()
    if (
        args.workers != 10
        or args.deadline_seconds <= 30
        or (not args.prepare and not args.preparation)
    ):
        parser.error("requires10workers, deadline>30 and --prepare or --preparation")
    Runner(args).run()


if __name__ == "__main__":
    main()
