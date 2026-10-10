"""0311 development probe or 1536 protected confirmation of the same A8 recipe."""

import argparse
import gzip
import hashlib
import importlib
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
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.fragment_operator import BlockOperator
from experiments.chem_tape.independent_input_bank import (
    ALPHABET,
    BANK,
    pairing,
    validate,
)
from experiments.chem_tape.small_source_run import build_source
from experiments.chem_tape.solver_corpus_fit import validate_table
from experiments.chem_tape.independent_input_report import report

DATA = Path(__file__).with_name("data") / "independent_input_0311"
CAP = 524288
WORKERS = 10
# Raw-byte hashes are frozen after the performance-blind screen, before search.
BANK_SHA = "d577cd82af204678463ddd2a1e90e498303f7b9be75d0222ffed213731011e7a"
OLD_SHA = "1f28f569ac01b9592c70dfc0fce4fc8dcebdab4e79562e23630541f5b7810fd6"


def load_frozen():
    saved = []
    for name, expected in [("bank.json", BANK_SHA), ("old_builds.json", OLD_SHA)]:
        raw = gzip.decompress((DATA / (name + ".gz")).read_bytes())
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("frozen artifact changed: " + name)
        saved.append(json.loads(raw))
    bank, old = saved
    validate_bank(bank)
    if len(old["builds"]) != 8 or [b["identity"] for b in old["builds"]] != [
        f"{f}{i}|A8" for f in ("BE", "PA") for i in range(1, 5)
    ]:
        raise ValueError("wrong frozen O identities")
    for b in old["builds"]:
        if (
            validate_table(b["table"]) != b["table_hash"]
            or digest(b["library"]["fragments"]) != b["library"]["hash"]
        ):
            raise ValueError("old artifact decoder/library mismatch")
    return bank, old


def validate_bank(bank):
    screen = bank["screen"]
    by = {c["id"]: c for c in screen["cells"]}
    parts = bank["split"]
    ids = sum((parts[k] for k in ("source", "development", "protected")), [])
    cells = [by[c] for c in ids]
    if (
        bank["name"] != BANK
        or bank["alphabet"] != ALPHABET
        or not screen["complete"]
        or screen["max_depth"] != 9
        or [len(parts[k]) for k in ("source", "development", "protected")] != [4, 4, 8]
        or len(set(ids)) != 16
        or bank["maximum_separated"] < 16
        or not all(c["retained"] and c["proper"] for c in cells)
    ):
        raise ValueError("incomplete real-token bank/split")
    labels = np.asarray([c["labels"] for c in cells])
    matches = (labels[:, None, :] == labels[None, :, :]).sum(2)
    if np.any(5 * matches[np.triu_indices(16, 1)] >= 4 * len(bank["inputs"])):
        raise ValueError("split not pairwise separated")
    source = [by[c] for c in parts["source"]]
    if (
        {c["roles"][r] for c in source for r in "EF"} != set(range(4))
        or len({pairing(c) for c in source}) < 2
        or len({pairing(by[c]) for c in parts["protected"]}) != 3
    ):
        raise ValueError("coverage failure")
    for c in screen["cells"]:
        if (
            hashlib.sha256(np.asarray(c["labels"], dtype="<i8").tobytes()).hexdigest()
            != c["label_hash"]
        ):
            raise ValueError("label hash changed")


def schedules(bank, smoke=False, protected=False):
    nbuild = 2 if smoke else (24 if protected else 8)
    base = (
        (800000 if protected else 390000)
        if smoke
        else (500000 if protected else 310000)
    )
    adaptive_gap = 100000 if protected and not smoke else 10000
    sources = [
        dict(
            alphabet=ALPHABET,
            phase=phase,
            build=b,
            cell=cid,
            arm="G4" if p == 0 else "A8",
            attempt=a,
            seed=base + adaptive_gap * p + 1000 * b + 10 * ci + a,
        )
        for p, phase in enumerate(("first_G4", "adaptive"))
        for b in range(nbuild)
        for ci, cid in enumerate(bank["split"]["source"])
        for a in range(4)
    ]
    target_part = "protected" if protected and not smoke else "development"
    score_base = (
        (820000 if protected else 420000)
        if smoke
        else (700000 if protected else 330000)
    )
    target = [
        dict(
            alphabet=ALPHABET,
            phase=target_part,
            cell=cid,
            arm=arm,
            build=ordinal // 2,
            ordinal=ordinal,
            seed=score_base + 1000 * ci + ordinal,
        )
        for ci, cid in enumerate(bank["split"][target_part])
        for ordinal in range(2 * nbuild)
        for arm in ("G4", "A8", "O")
        if arm != "O" or ordinal < 2 * min(nbuild, 8)
    ]
    if len({r["seed"] for r in sources}) != len(sources) or {
        r["seed"] for r in sources
    } & {r["seed"] for r in target}:
        raise ValueError("seed overlap")
    if any(r["cell"] in bank["split"]["protected"] for r in sources):
        raise ValueError("protected source exposure")
    if target_part != "protected" and any(
        r["cell"] in bank["split"]["protected"] for r in target
    ):
        raise ValueError("protected smoke/development exposure")
    return sources, target


def runtime_limits(protected=False):
    return (2970, 4170) if protected else (1470, 1770)


def score_projection(schedule, mean_g4, mean_a8, mean_o, effective):
    means = dict(G4=mean_g4, A8=mean_a8, O=mean_o)
    return 1.3 * sum(means[r["arm"]] for r in schedule) / effective + 90


def method_hashes():
    root = Path(__file__).resolve().parents[2]
    paths = sorted((root / "src/folding_evolution").rglob("*.py"))
    paths += sorted((root / "experiments/chem_tape").glob("*.py"))
    paths += sorted((root / "rust/src").rglob("*.rs"))
    hashes = {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths
    }
    backend = importlib.import_module("_folding_rust._folding_rust")
    hashes["rust_extension"] = hashlib.sha256(
        Path(backend.__file__).read_bytes()
    ).hexdigest()
    return hashes


def execute(envelope):
    job, meta, fragments, diagnostic = envelope
    off = meta["arm"] == "G4"
    operator = (
        None
        if off
        else BlockOperator(
            "F",
            fragments,
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
        raise ValueError("solver exact validation failed")
    row.update(meta)
    row["alphabet"] = ALPHABET
    row["library_hash"] = digest(fragments) if not off else None
    row["empty_library_fallback"] = not off and not fragments
    if operator is not None:
        row["operator"] = operator.stats
    return row


class Runner:
    def __init__(self, args):
        self.args = args
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 30
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("fresh empty RUN_DIR required")
        self.bank, self.old = load_frozen()
        self.cells = {c["id"]: c for c in self.bank["screen"]["cells"]}
        self.indices = np.random.default_rng(0).choice(625, 96, replace=False).tolist()
        self.diagnostic = [self.bank["inputs"][i] for i in self.indices[:4]]
        self.protected = getattr(args, "protected", False)
        self.nbuild = 2 if args.smoke else (24 if self.protected else 8)
        self.source_schedule, self.score_schedule = schedules(
            self.bank, args.smoke, self.protected
        )
        self.cap = 8192 if args.smoke else CAP
        self.hashes = method_hashes()
        self.config = dict(
            task="2026-10-10-1536" if self.protected else "2026-10-10-0311",
            alphabet=ALPHABET,
            bank=BANK,
            smoke=args.smoke,
            arguments=vars(args),
            cap=self.cap,
            population=256,
            lexicase_cases=64,
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            recipe="unchanged G4; 4+4/cell; alpha50 C; active recurrent3..6 windows, max32; F rate0.2 suffix preserved",
            method=dict(tape_length=32, crossover=0.7, mutation=0.03, elites=2),
            reinterpretation="O token ids unchanged; reducers explicitly reinterpreted as X0..X3",
            protected_performance_scored=False,
            target_partition="protected"
            if self.protected and not args.smoke
            else "development",
        )
        self.freeze = dict(
            alphabet=ALPHABET,
            bank_sha256=BANK_SHA,
            old_sha256=OLD_SHA,
            source_schedule_hash=digest(self.source_schedule),
            score_schedule_hash=digest(self.score_schedule),
            method_hashes=self.hashes,
            smoke=args.smoke,
            workers=args.workers,
            frozen_before_search=True,
            protected_mode=self.protected,
            fragment_indices=self.indices,
        )
        self.builds, self.seed_builds, self.batches = {}, {}, {}
        for name, value in [
            ("config.json", self.config),
            ("bank.json", self.bank),
            ("old_builds.json", self.old),
            ("source_schedule.json", self.source_schedule),
            ("schedule.json", self.score_schedule),
            ("method_freeze.json", self.freeze),
        ]:
            write_json(self.out, name, value)

    def envelope(self, meta):
        if meta["arm"] == "G4":
            table, fragments = tables()["G4"].tolist(), []
        else:
            if meta["arm"] == "O":
                build = self.old["builds"][meta["build"]]
            else:
                build = (
                    self.seed_builds if meta["phase"] == "adaptive" else self.builds
                )[str(meta["build"])]
            table, fragments = build["table"], build["library"]["fragments"]
        job = (
            self.cells[meta["cell"]],
            meta["arm"],
            table,
            meta["seed"],
            self.cap,
            256,
            self.bank["inputs"],
            ALPHABET,
        )
        return job, meta, fragments, self.diagnostic

    def jobs(self, schedule, filename, phase):
        tick = time.monotonic()
        envelopes = [self.envelope(r) for r in schedule]
        expected = {(r["cell"], r["arm"], r["seed"]): r for r in schedule}
        if len(expected) != len(schedule):
            raise ValueError("duplicate search keys")
        rows = []
        hashes = {
            (e[1]["cell"], e[1]["arm"], e[1]["seed"]): (
                Decoder(e[0][2]).hash(),
                digest(e[2]),
            )
            for e in envelopes
        }
        with (self.out / filename).open("w", buffering=1) as stream:

            def save(row):
                key = row["cell"], row["arm"], row["seed"]
                meta = expected.pop(key)
                tab, lib = hashes[key]
                if (
                    any(row[k] != v for k, v in meta.items())
                    or row["table_hash"] != tab
                    or (row["arm"] != "G4" and row["library_hash"] != lib)
                    or row["cap"] != self.cap
                    or row["pop_size"] != 256
                    or not 0 < row["evaluations"] <= self.cap
                    or row["evaluations"] % 256
                    or (not row["solved"] and row["evaluations"] != self.cap)
                    or (row["solver"] is not None) != row["solved"]
                    or row["training_indices"]
                    != np.random.default_rng([row["seed"], 0])
                    .choice(625, 64, replace=False)
                    .tolist()
                ):
                    raise ValueError("search provenance/budget/seed mismatch")
                if (
                    row["arm"] != "G4"
                    and row["operator"]["eligible_children"]
                    != (row["generations"] - 1) * 254
                ):
                    raise ValueError("elite/operator boundary changed")
                rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                write_json(
                    self.out,
                    "progress.json",
                    dict(
                        alphabet=ALPHABET,
                        phase=phase,
                        complete=len(rows),
                        total=len(schedule),
                    ),
                )

            if (
                not run_jobs(self.pool, execute, envelopes, self.deadline, save)
                or expected
            ):
                raise TimeoutError("incomplete batch: " + phase)
        wall = time.monotonic() - tick
        worker = sum(r["seconds"] for r in rows)
        self.batches[phase] = dict(
            jobs=len(rows),
            wall_seconds=wall,
            worker_seconds=worker,
            effective_workers=worker / wall,
            exact_check_seconds=sum(r["exact_check_seconds"] for r in rows),
            max_exact_check_seconds=max(r["exact_check_max_seconds"] for r in rows),
        )
        write_json(
            self.out, "timing.json", dict(alphabet=ALPHABET, batches=self.batches)
        )
        return sorted(rows, key=lambda r: (r["build"], r["cell"], r["seed"], r["arm"]))

    def rebuild(self, rows, phase):
        tick = time.monotonic()
        nbuild = self.nbuild
        sources = self.bank["split"]["source"]
        # Stable schedule order, independent of worker completion order.
        index = {(r["cell"], r["seed"]): r for r in rows}
        scheduled = [r for r in self.source_schedule if (r["cell"], r["seed"]) in index]
        grouped = {
            str(b): [
                index[r["cell"], r["seed"]] | dict(corpus="DG" + str(b))
                for r in scheduled
                if r["build"] == b
            ]
            for b in range(nbuild)
        }
        jobs = [
            (
                "DG" + b,
                b,
                rs,
                self.bank["inputs"],
                self.cells,
                self.indices,
                sources,
                ALPHABET,
            )
            for b, rs in grouped.items()
        ]
        builds = {}

        def save(record):
            b = record["block"]
            validate_table(record["table"])
            if record["attempt_keys"] != [
                [r["corpus"], r["cell"], r["seed"]] for r in grouped[b]
            ]:
                raise ValueError("fit membership changed")
            record["alphabet"] = ALPHABET
            builds[b] = record

        if (
            not run_jobs(self.pool, build_source, jobs, self.deadline, save)
            or len(builds) != nbuild
        ):
            raise TimeoutError("incomplete source fitting")
        self.batches[phase] = dict(
            wall_seconds=time.monotonic() - tick,
            jobs=nbuild,
            worker_seconds=sum(
                sum(
                    r["acquisition"][k]
                    for k in (
                        "verification_seconds",
                        "fit_seconds",
                        "extraction_seconds",
                    )
                )
                for r in builds.values()
            ),
        )
        write_json(
            self.out, "timing.json", dict(alphabet=ALPHABET, batches=self.batches)
        )
        return builds

    def prepare(self):
        tick = time.monotonic()
        validation = validate(
            self.bank["screen"]["cells"], random_count=100 if self.args.smoke else 10000
        )
        # Existing empty fit/library rules are asserted by dedicated tests and
        # audited at preparation with the same production fitting path.
        empty = build_source(
            (
                "DG-empty",
                0,
                [],
                self.bank["inputs"],
                self.cells,
                self.indices,
                self.bank["split"]["source"],
                ALPHABET,
            )
        )
        if (
            empty["table"] != tables()["G4"].tolist()
            or empty["library"]["fragments"]
            or len(empty["empty_cells"]) != 4
        ):
            raise ValueError("empty fit/library fallback changed")
        validation["alphabet"] = ALPHABET
        validation["empty_corpus_G4"] = True
        validation["seconds_including_empty_audit"] = time.monotonic() - tick
        write_json(self.out, "validation.json", validation)
        first = self.jobs(
            [r for r in self.source_schedule if r["phase"] == "first_G4"],
            "first.jsonl",
            "first_G4",
        )
        self.seed_builds = self.rebuild(first, "intermediate_fit")
        write_json(self.out, "seed_builds.json", self.seed_builds)
        adaptive = self.jobs(
            [r for r in self.source_schedule if r["phase"] == "adaptive"],
            "adaptive.jsonl",
            "adaptive",
        )
        self.builds = self.rebuild(first + adaptive, "final_fit")
        write_json(self.out, "builds.json", self.builds)
        yields = {
            b: sum(r["solved"] for r in first if str(r["build"]) == b)
            for b in self.builds
        }
        median = float(np.median(list(yields.values())))
        effective = min(
            self.args.workers,
            self.batches["first_G4"]["effective_workers"],
            self.batches["adaptive"]["effective_workers"],
        )
        mean_g4 = self.batches["first_G4"]["worker_seconds"] / len(first)
        mean_a8 = self.batches["adaptive"]["worker_seconds"] / len(adaptive)
        # O is unmeasured before scoring; conservatively reserve at least G4's
        # measured unsolved-equivalent full-cap time rather than claiming O is timed.
        fullcap_g4 = float(
            np.mean([r["seconds"] * self.cap / r["evaluations"] for r in first])
        )
        mean_o_proxy = max(mean_g4, mean_a8, fullcap_g4)
        projected = score_projection(
            self.score_schedule, mean_g4, mean_a8, mean_o_proxy, effective
        )
        prepare_limit, score_limit = runtime_limits(self.protected)
        prepare_seconds = time.monotonic() - self.started
        admitted = projected <= score_limit and prepare_seconds <= prepare_limit
        reasons = []
        if median < 4:
            reasons.append(
                "discovery obstacle: median first-batch yield below4/16; continue scoring with unchanged fallbacks and no attempt increase"
            )
        if projected > score_limit:
            reasons.append(
                f"measured source-load price cannot admit{len(self.score_schedule)} searches in{score_limit + 30}s"
            )
        if prepare_seconds > prepare_limit:
            reasons.append(f"preparation exceeds{prepare_limit + 30}s allowance")
        p = dict(
            alphabet=ALPHABET,
            admitted=admitted,
            smoke=self.args.smoke,
            reasons=reasons,
            first_yields=yields,
            median_first_yield=median,
            batches=self.batches,
            effective_workers=effective,
            score_projected_seconds=projected,
            timing_caveat="O is not yet measured; source-load projection includes conservative fullcap proxy and30%reserve",
            freeze=self.freeze,
            builds_hash=digest(self.builds),
            seed_builds_hash=digest(self.seed_builds),
            validation_hash=digest(validation),
            validation=validation,
            first_hash=digest(first),
            adaptive_hash=digest(adaptive),
            prepare_seconds=prepare_seconds,
        )
        p["preparation_hash"] = digest(p)
        for name, value in [
            (
                "source_summary.json",
                source_summary(first, adaptive, self.seed_builds, self.builds),
            ),
            ("preparation.json", p),
        ]:
            write_json(self.out, name, value)
        print(
            json.dumps(
                dict(
                    admitted=admitted,
                    median_first_yield=median,
                    projected_score_seconds=projected,
                    smoke=self.args.smoke,
                )
            ),
            flush=True,
        )

    def score(self):
        if not self.args.preparation:
            raise ValueError("--preparation required")
        path = Path(self.args.preparation)
        p = json.loads(path.read_text())
        if p.get("preparation_hash") != digest(
            {k: v for k, v in p.items() if k != "preparation_hash"}
        ):
            raise ValueError("preparation admission/timing record changed")
        if (
            p["smoke"] != self.args.smoke
            or p["freeze"] != self.freeze
            or digest(p["validation"]) != p["validation_hash"]
            or not p["validation"]["passed"]
        ):
            raise ValueError(
                "preparation/method/seed freeze changed or smoke/full mismatch"
            )
        self.builds = json.loads((path.parent / "builds.json").read_text())
        self.seed_builds = json.loads((path.parent / "seed_builds.json").read_text())
        if (
            digest(self.builds) != p["builds_hash"]
            or digest(self.seed_builds) != p["seed_builds_hash"]
        ):
            raise ValueError("source artifacts changed")
        first = sorted(
            [
                json.loads(x)
                for x in (path.parent / "first.jsonl").read_text().splitlines()
            ],
            key=lambda r: (r["build"], r["cell"], r["seed"], r["arm"]),
        )
        adaptive = sorted(
            [
                json.loads(x)
                for x in (path.parent / "adaptive.jsonl").read_text().splitlines()
            ],
            key=lambda r: (r["build"], r["cell"], r["seed"], r["arm"]),
        )
        if digest(first) != p["first_hash"] or digest(adaptive) != p["adaptive_hash"]:
            raise ValueError("source rows changed")
        validate_source_rows(first + adaptive, self.source_schedule, self.cap)
        measured_median = float(
            np.median(
                [
                    sum(r["solved"] for r in first if r["build"] == b)
                    for b in range(
                        2
                        if self.args.smoke
                        else (24 if getattr(self.args, "protected", False) else 8)
                    )
                ]
            )
        )
        prepare_limit, score_limit = runtime_limits(
            getattr(self.args, "protected", False)
        )
        if measured_median != p["median_first_yield"] or p["admitted"] != (
            p["score_projected_seconds"] <= score_limit
            and p["prepare_seconds"] <= prepare_limit
        ):
            raise ValueError(
                "preparation admission disagrees with recorded data/limits"
            )
        for name, value in [
            ("preparation.json", p),
            ("builds.json", self.builds),
            ("seed_builds.json", self.seed_builds),
            (
                "source_summary.json",
                source_summary(first, adaptive, self.seed_builds, self.builds),
            ),
            ("validation.json", p["validation"]),
        ]:
            write_json(self.out, name, value)
        if not p["admitted"] and not self.args.smoke:
            result = dict(
                alphabet=ALPHABET,
                status="feasibility_stop",
                reasons=p["reasons"],
                protected_performance_scored=False,
                preparation=p,
                scope="runtime obstacle; protected confirmation unanswered",
            )
            write_json(self.out, "result.json", result)
            (self.out / "report.md").write_text(
                "Feasibility stop before target scoring.\n\n"
                + "\n".join(p["reasons"])
                + "\n\nProtected cells remain unscored. Return to strategy.\n"
            )
            return
        phase = (
            "protected"
            if getattr(self.args, "protected", False) and not self.args.smoke
            else "development"
        )
        rows = self.jobs(self.score_schedule, "search.jsonl", phase)
        if phase == "protected":
            self.config["protected_performance_scored"] = True
            write_json(self.out, "config.json", self.config)
        reporter = report
        if getattr(self.args, "protected", False):
            from experiments.chem_tape.independent_input_protected_report import (
                report as reporter,
            )
        reporter(
            self.out,
            rows,
            self.builds,
            self.old,
            p,
            self.batches[phase],
            self.args.smoke,
        )

    def run(self):
        # Spawn workers only after the performance-blind manifest is written.
        with mp.get_context("spawn").Pool(self.args.workers) as pool:
            self.pool = pool
            if self.args.prepare:
                self.prepare()
            else:
                self.score()


def validate_source_rows(rows, schedule, cap):
    by = {(r["cell"], r["seed"]): r for r in rows}
    if len(by) != len(rows) or len(rows) != len(schedule):
        raise ValueError("incomplete/duplicate frozen source schedule")
    for meta in schedule:
        row = by.get((meta["cell"], meta["seed"]))
        if row is None or any(row[k] != v for k, v in meta.items()):
            raise ValueError("source seed/phase/build/cell metadata changed")
        if (
            row["cap"] != cap
            or row["pop_size"] != 256
            or (row["solver"] is not None) != row["solved"]
        ):
            raise ValueError("source cap/population/solver mismatch")


def source_summary(first, adaptive, seed_builds, builds):
    median_first_yield = float(
        np.median(
            [sum(r["solved"] for r in first if str(r["build"]) == b) for b in builds]
        )
    )
    return dict(
        alphabet=ALPHABET,
        median_first_yield=median_first_yield,
        discovery_obstacle=median_first_yield < 4,
        phases={
            phase: {
                cid: dict(attempts=len(rs), solved=sum(r["solved"] for r in rs))
                for cid in sorted({r["cell"] for r in rows})
                for rs in [[r for r in rows if r["cell"] == cid]]
            }
            for phase, rows in [("first_G4", first), ("adaptive", adaptive)]
        },
        builds={
            b: dict(
                first_yield=sum(r["solved"] for r in first if str(r["build"]) == b),
                adaptive_yield=sum(
                    r["solved"] for r in adaptive if str(r["build"]) == b
                ),
                intermediate_empty_cells=seed_builds[b]["empty_cells"],
                final_empty_cells=record["empty_cells"],
                intermediate_empty_corpus=not any(seed_builds[b]["yields"].values()),
                final_empty_corpus=not any(record["yields"].values()),
                intermediate_empty_library=not seed_builds[b]["library"]["fragments"],
                final_empty_library=not record["library"]["fragments"],
                library_size=len(record["library"]["fragments"]),
                acquisition=record["acquisition"],
                intermediate_fitting=seed_builds[b]["acquisition"],
            )
            for b, record in builds.items()
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--protected",
        action="store_true",
        help="1536 confirmation; smoke still searches only development cells",
    )
    parser.add_argument("--workers", type=int, default=WORKERS)
    parser.add_argument("--deadline-seconds", type=int, default=1500)
    args = parser.parse_args()
    if args.workers != WORKERS or args.deadline_seconds <= 30:
        parser.error("approved sustained load requires10 workers and deadline>30s")
    Runner(args).run()


if __name__ == "__main__":
    main()
