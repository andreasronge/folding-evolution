"""0024: fixed-cutoff scheduling of unchanged 2254 tree and native A8 searches.

Preparation alone can admit target scoring; smoke can never admit it.
"""

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

from experiments.chem_tape import tree_gp_run as ordinary
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.independent_input_run import CAP, method_hashes

TASK = "2026-10-11-0024"
CUTOFF = 65536
ARMS = ("R-tree", "R-A8", "F-A8")
DATA = Path(__file__).with_name("data") / "restart_gp_0024"
LIMITS = dict(DG=5400, TS=1800)


def historical(saved, targets):
    provenance = json.loads((DATA / "provenance.json").read_text())
    root = Path(__file__).resolve().parents[2]
    for name, sha in provenance["frozen_search_hashes"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != sha:
            raise ValueError("2254 frozen search changed: " + name)
    result = {}
    for name, rec in provenance["files"].items():
        raw = (
            (DATA / name).read_bytes()
            if name.endswith(".json")
            else gzip.decompress((DATA / (name + ".gz")).read_bytes())
        )
        if hashlib.sha256(raw).hexdigest() != rec["sha256"]:
            raise ValueError("historical artifact changed: " + name)
        result[name] = (
            json.loads(raw)
            if name.endswith(".json")
            else [json.loads(line) for line in raw.splitlines()]
        )
    _, schedule = ordinary.schedules(saved["banks.json"], targets)
    for family in ("DG", "TS"):
        ordinary.validate_rows(
            result[family + ".jsonl"],
            [m for m in schedule if m["family"] == family],
            saved,
            CAP,
            0.5,
        )
    return result, provenance


def schedules(banks, targets):
    score, stage, validation = [], [], []
    for fi, f in enumerate(("DG", "TS")):
        development = banks[f]["split"]["source"] + banks[f]["split"]["development"]
        if (
            len(development) != 8
            or len(targets[f]) != 8
            or set(development) & set(targets[f])
        ):
            raise ValueError("fixed roster changed")
        for ci, cell in enumerate(targets[f]):
            for b in range(24):
                for r in range(4):
                    for a in ARMS[:2]:
                        score.append(
                            dict(
                                family=f,
                                cell=cell,
                                arm=a,
                                build=b,
                                repeat=r,
                                phase="target",
                                seeds=[
                                    22300000
                                    + 1000 * (8 * fi + ci)
                                    + 8 * (4 * b + r)
                                    + k
                                    for k in range(8)
                                ],
                            )
                        )
                for r in range(2):
                    score.append(
                        dict(
                            family=f,
                            cell=cell,
                            arm="F-A8",
                            build=b,
                            repeat=r,
                            phase="target",
                            seeds=[22320000 + 1000 * (8 * fi + ci) + 2 * b + r],
                        )
                    )
        for r in range(2):
            for a in ARMS[:2]:
                validation.append(
                    dict(
                        family=f,
                        cell=development[0],
                        arm=a,
                        build=r,
                        repeat=r,
                        phase="validation",
                        seeds=[22350000 + 1000 * fi + 8 * r + k for k in range(8)],
                    )
                )
        if f == "DG":
            for ci, cell in enumerate(development):
                for b in range(8):
                    for a in ARMS[:2]:
                        stage.append(
                            dict(
                                family=f,
                                cell=cell,
                                arm=a,
                                build=b,
                                repeat=0,
                                phase="stage0",
                                seeds=[
                                    22340000 + 1000 * ci + 8 * b + k for k in range(8)
                                ],
                            )
                        )
    return score, stage, validation


def key(m):
    return m["family"], m["cell"], m["arm"], m["build"], m["repeat"]


def audit(score, stage, validation, saved, old, targets):
    groups = {}
    pairing = True
    for name, schedule in (
        ("restarted", [m for m in score if m["arm"] != "F-A8"]),
        ("full", [m for m in score if m["arm"] == "F-A8"]),
        ("stage0", stage),
        ("validation", validation),
    ):
        uses = {}
        for m in schedule:
            for k, seed in enumerate(m["seeds"]):
                uses.setdefault(seed, []).append((key(m), k))
        for entries in uses.values():
            if name == "full":
                pairing &= len(entries) == 1
            else:
                pairing &= len(entries) == 2 and {e[0][2] for e in entries} == set(
                    ARMS[:2]
                )
                pairing &= len({(e[0][:2], e[0][3:], e[1]) for e in entries}) == 1
        groups[name] = set(uses)
    groups["semantic_validation"] = {22352000}
    historical_seeds = ordinary.historical_seeds(saved) | set(
        old["observed_seeds.json"]
    )
    for base in (22150000, 22180000):
        cal, previous = ordinary.schedules(
            saved["banks.json"], targets, scoring_base=base
        )
        historical_seeds |= {m["seed"] for m in cal + previous}
    historical_seeds |= ordinary.SMOKE_SEEDS | ordinary.TAIL_SEEDS
    overlaps = {}
    names = list(groups)
    for i, name in enumerate(names):
        overlaps[name + "_historical"] = sorted(groups[name] & historical_seeds)
        for other in names[i + 1 :]:
            overlaps[name + "_" + other] = sorted(groups[name] & groups[other])
    complete = (
        len(score) == 3840
        and len(stage) == 128
        and len(validation) == 8
        and len({key(m) for m in score}) == 3840
        and len(groups["restarted"]) == 12288
        and len(groups["full"]) == 768
        and len(groups["stage0"]) == 512
        and len(groups["validation"]) == 32
    )
    return dict(
        task=TASK,
        admitted=bool(complete and pairing and not any(overlaps.values())),
        complete=complete,
        intended_pairing_valid=bool(pairing),
        overlaps=overlaps,
        published_seed_sets={k: sorted(v) for k, v in groups.items()},
        historical_seeds=sorted(historical_seeds),
        historical_replays=[r["seed"] for r in saved["replay.json"]],
        replay_exception="rerun original sixteen saved native searches; not fresh scoring",
        targets_scored=False,
    )


def attempt_meta(meta, k):
    return {n: v for n, v in meta.items() if n != "seeds"} | dict(
        arm="tree" if meta["arm"] == "R-tree" else "A8", seed=meta["seeds"][k]
    )


def envelope(meta, saved, cutoff=CUTOFF):
    if meta["arm"] not in ARMS or len(meta["seeds"]) != (
        1 if meta["arm"] == "F-A8" else 8
    ):
        raise ValueError("invalid restart schedule")
    return dict(
        meta=meta,
        cutoff=cutoff,
        first=ordinary.envelope(
            attempt_meta(meta, 0), saved, CAP if meta["arm"] == "F-A8" else cutoff, 0.5
        ),
    )


def with_seed(e, seed):
    e = dict(e)
    e["meta"] = e["meta"] | dict(seed=seed)
    if e["kind"] == "tree":
        job = list(e["job"])
        job[1] = seed
        e["job"] = tuple(job)
    else:
        job, meta, fragments, diagnostic = e["job"]
        job = list(job)
        job[3] = seed
        e["job"] = (tuple(job), meta | dict(seed=seed), fragments, diagnostic)
    return e


def execute(e):
    start = time.monotonic()
    attempts = []
    for seed in e["meta"]["seeds"]:
        # Every call starts the unchanged engine with fresh local RNG/cache/population.
        row = ordinary.execute(with_seed(e["first"], seed))
        attempts.append(row)
        if row["solved"]:
            break
    elapsed = time.monotonic() - start
    return e["meta"] | dict(
        cap=CAP if e["meta"]["arm"] == "F-A8" else 8 * e["cutoff"],
        cutoff=CAP if e["meta"]["arm"] == "F-A8" else e["cutoff"],
        pop_size=256,
        solved=attempts[-1]["solved"],
        solver=attempts[-1]["solver"],
        evaluations=sum(r["evaluations"] for r in attempts),
        worker_seconds=elapsed,
        attempts=attempts,
        attempt_count=len(attempts),
        scheduling_seconds=max(
            0.0, elapsed - sum(r["worker_seconds"] for r in attempts)
        ),
    )


def deterministic(value):
    """Remove measured timing fields recursively; retain every other field."""
    if isinstance(value, dict):
        return {
            k: deterministic(v)
            for k, v in value.items()
            if k != "seconds" and not k.endswith("_seconds")
        }
    if isinstance(value, list):
        return [deterministic(v) for v in value]
    return value


def validate_rows(rows, schedule, saved, cutoff=CUTOFF):
    by = {key(r): r for r in rows}
    if len(rows) != len(by) or set(by) != {key(m) for m in schedule}:
        raise ValueError("missing/duplicate/unexpected scheduled jobs")
    for m in schedule:
        r = by[key(m)]
        if any(r.get(k) != v for k, v in m.items()):
            raise ValueError("job provenance changed")
        cap = CAP if m["arm"] == "F-A8" else cutoff
        attempts = r["attempts"]
        if not attempts or len(attempts) > len(m["seeds"]):
            raise ValueError("invalid attempt count")
        for k, a in enumerate(attempts):
            ordinary.validate_rows([a], [attempt_meta(m, k)], saved, cap, 0.5)
            if k < len(attempts) - 1 and a["solved"]:
                raise ValueError("continued after first exact solve")
        total = cap * len(m["seeds"])
        if (
            r["cap"] != total
            or r["cutoff"] != cap
            or r["pop_size"] != 256
            or r["evaluations"] != sum(a["evaluations"] for a in attempts)
            or not 0 < r["evaluations"] <= total
            or r["solved"] != attempts[-1]["solved"]
            or r["solver"] != attempts[-1]["solver"]
            or r["attempt_count"] != len(attempts)
            or (
                not r["solved"]
                and (len(attempts) != len(m["seeds"]) or r["evaluations"] != total)
            )
            or not np.isfinite(r["worker_seconds"])
            or r["worker_seconds"] <= 0
            or not np.isfinite(r["scheduling_seconds"])
            or r["scheduling_seconds"] < 0
            or r["worker_seconds"] + 1e-6 < sum(a["worker_seconds"] for a in attempts)
        ):
            raise ValueError("invalid aggregate accounting")
    return sorted(rows, key=lambda r: str(key(r)))


def jsonlines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def require_fresh(out):
    # run_queue.py creates these files before launching the experiment.
    owned = {"metadata.json", "stdout.log", "stderr.log"}
    if any(p.name not in owned for p in out.iterdir()):
        raise ValueError("fresh RUN_DIR required (runner metadata/logs allowed)")


class Runner:
    def __init__(self, args):
        self.args = args
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 30
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        require_fresh(self.out)
        self.saved, self.targets = load_saved()
        self.old, provenance = historical(self.saved, self.targets)
        self.score, self.stage, self.validation = schedules(
            self.saved["banks.json"], self.targets
        )
        self.seed_audit = audit(
            self.score, self.stage, self.validation, self.saved, self.old, self.targets
        )
        self.cutoff = 2048 if args.smoke else CUTOFF
        self.freeze = dict(
            task=TASK,
            targets=self.targets,
            banks=digest(self.saved["banks.json"]),
            builds=digest(self.saved["builds.json"]),
            methods=method_hashes(),
            schedule=digest(self.score),
            stage=digest(self.stage),
            validation=digest(self.validation),
            history=provenance,
            crossover=0.5,
            cutoff=CUTOFF,
            cap=CAP,
            workers=10,
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
            ),
        )
        for name, value in (
            ("method_freeze.json", self.freeze),
            ("target_schedule.json", self.score),
            ("stage0_schedule.json", self.stage),
            ("validation_schedule.json", self.validation),
            ("schedule_audit.json", self.seed_audit),
        ):
            write_json(self.out, name, value)
        if not self.seed_audit["admitted"]:
            raise ValueError("seed audit failed before search")

    def jobs(self, metas, name, fn=execute, jobs=None):
        rows, start = [], time.monotonic()
        with (self.out / (name + ".jsonl")).open("w", buffering=1) as stream:

            def save(row):
                rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                write_json(
                    self.out,
                    "progress.json",
                    dict(phase=name, completed=len(rows), total=len(metas)),
                )

            if not run_jobs(
                self.pool,
                fn,
                jobs
                if jobs is not None
                else [envelope(m, self.saved, self.cutoff) for m in metas],
                self.deadline,
                save,
            ):
                raise TimeoutError("incomplete batch: " + name)
        self.batches[name] = dict(
            wall_seconds=time.monotonic() - start,
            jobs=len(rows),
            worker_seconds=sum(r["worker_seconds"] for r in rows),
        )
        write_json(self.out, "timing.json", self.batches)
        return rows

    def replay(self):
        # Reuse the exact original native replay implementation, not a reconstruction.
        proxy = object.__new__(ordinary.Runner)
        proxy.saved = self.saved

        def jobs(metas, name, phase, envelopes=None):
            return self.jobs(metas, "replay", ordinary.execute, envelopes)

        proxy.jobs = jobs
        return proxy.replay()[1]

    def validate(self):
        from experiments.chem_tape import tree_gp_validate as semantics

        original = semantics.SEED
        semantics.SEED = 22352000
        try:
            semantic = semantics.validate()
        finally:
            semantics.SEED = original
        if not semantic["admitted"]:
            raise ValueError("semantic validation failed")
        rows = self.jobs(self.validation, "validation_search")
        validate_rows(rows, self.validation, self.saved, self.cutoff)
        for row in rows:
            e = envelope(
                next(m for m in self.validation if key(m) == key(row)),
                self.saved,
                self.cutoff,
            )
            direct = ordinary.execute(e["first"])
            if deterministic(row["attempts"][0]) != deterministic(direct):
                raise ValueError("first attempt differs from ordinary capped search")
            repeat = execute(e)
            if deterministic(row) != deterministic(repeat):
                raise ValueError("scheduled job deterministic replay failed")
        return dict(
            passed=True,
            semantic=semantic,
            first_attempt_equivalence=len(rows),
            deterministic_replays=len(rows),
            targets_scored=False,
        )

    def prepare(self):
        from experiments.chem_tape.restart_gp_report import sensitivity

        validation = self.validate()
        replay = self.replay()
        write_json(self.out, "validation.json", validation)
        write_json(self.out, "replay.json", replay)
        sensitivity_result = sensitivity(self.old["DG.jsonl"], self.targets["DG"])
        write_json(self.out, "historical_sensitivity.json", sensitivity_result)
        stage = self.stage[:4] if self.args.smoke else self.stage
        rows = self.jobs(stage, "stage0")
        rows = validate_rows(rows, stage, self.saved, self.cutoff)
        timing = self.batches["stage0"]
        effective = min(10.0, timing["worker_seconds"] / timing["wall_seconds"])
        means = {
            a: float(np.mean([r["worker_seconds"] for r in rows if r["arm"] == a]))
            for a in ARMS[:2]
        }
        full = float(
            np.mean(
                [r["worker_seconds"] for r in self.old["DG.jsonl"] if r["arm"] == "A8"]
            )
        )
        projection = 90 + 1.3 * (768 * sum(means.values()) + 384 * full) / max(
            0.1, effective
        )
        p = dict(
            task=TASK,
            smoke=self.args.smoke,
            freeze=self.freeze,
            seed_audit=self.seed_audit,
            validation=validation,
            replay=replay,
            stage_hash=digest(rows),
            stage_rows=len(rows),
            timing=timing,
            means=means,
            effective_concurrency=effective,
            historical_F_A8_mean_worker_seconds=full,
            DG_projected_seconds=projection,
            admitted=not self.args.smoke and len(rows) == 128 and projection <= 4500,
            projection_caveat="source/development restart means; historical F-A8 worker time; 30% reserve +90s; targets may differ",
        )
        p["preparation_hash"] = digest(p)
        write_json(self.out, "preparation.json", p)
        if not p["admitted"] and not self.args.smoke:
            raise ValueError("DG timing admission failed: " + str(projection))
        print(
            json.dumps(
                {
                    k: p[k]
                    for k in (
                        "admitted",
                        "smoke",
                        "DG_projected_seconds",
                        "means",
                        "effective_concurrency",
                    )
                }
            ),
            flush=True,
        )

    def load_preparation(self):
        directory = Path(self.args.preparation)
        p = json.loads((directory / "preparation.json").read_text())
        if (
            p.get("preparation_hash")
            != digest({k: v for k, v in p.items() if k != "preparation_hash"})
            or not p.get("admitted")
            or p.get("smoke")
            or p.get("freeze") != self.freeze
            or p.get("seed_audit") != self.seed_audit
            or not p["validation"]["passed"]
            or not p["replay"]["passed"]
            or p["stage_rows"] != 128
            or p["DG_projected_seconds"] > 4500
        ):
            raise ValueError("requires admitted unchanged production preparation")
        rows = validate_rows(
            jsonlines(directory / "stage0.jsonl"), self.stage, self.saved
        )
        if digest(rows) != p["stage_hash"]:
            raise ValueError("preparation evidence changed")
        write_json(self.out, "preparation.json", p)
        return p

    def score_family(self):
        from experiments.chem_tape.restart_gp_report import report

        p = self.load_preparation()
        previous = []
        if self.args.family == "TS":
            path = Path(self.args.dg_score)
            previous = validate_rows(
                jsonlines(path / "search.jsonl"),
                [m for m in self.score if m["family"] == "DG"],
                self.saved,
            )
            result = json.loads((path / "result.json").read_text())
            if (
                result["rows_hash"] != digest(previous)
                or result["preparation_hash"] != p["preparation_hash"]
            ):
                raise ValueError("DG result or preparation changed")
        metas = [m for m in self.score if m["family"] == self.args.family]
        rows = validate_rows(self.jobs(metas, "search"), metas, self.saved)
        report(
            self.out,
            previous + rows,
            self.saved,
            self.targets,
            self.old,
            p,
            self.batches,
        )

    def run(self):
        # Terminate workers on a failed gate/deadline; do not wait for an abandoned batch.
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        try:
            self.prepare() if self.args.prepare else self.score_family()
        finally:
            self.pool.terminate()
            self.pool.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--family", choices=("DG", "TS"))
    parser.add_argument("--dg-score")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=1800)
    args = parser.parse_args()
    if (
        args.workers != 10
        or args.deadline_seconds <= 30
        or args.deadline_seconds
        > (1800 if args.prepare else LIMITS.get(args.family, 0))
        or (args.smoke and not args.prepare)
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
            "requires ten workers and bounded preparation or preparation-gated family scoring"
        )
    Runner(args).run()


if __name__ == "__main__":
    main()
