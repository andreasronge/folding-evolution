"""0150: frozen source-subtree libraries, paired restarted DG searches."""

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

from experiments.chem_tape import restart_gp_run as restart
from experiments.chem_tape import tree_gp_run as ordinary
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.independent_input_run import method_hashes
from experiments.chem_tape.tree_gp_search import Tree, search
from experiments.chem_tape.tree_library import extract, controls, verify_entries

TASK = "2026-10-11-0150"
ARMS = ("R-tree", "R-lib", "R-size")
DATA = Path(__file__).with_name("data") / "tree_library_0150"


def schedules(bank, targets):
    source, stage_source, score, stage = [], [], [], []

    def meta(cell, arm, b, r, base, ci, stride):
        return dict(
            family="DG",
            cell=cell,
            arm=arm,
            build=b,
            repeat=r,
            seeds=[base + stride * ci + 8 * (8 * b + r) + k for k in range(8)],
        )

    for ci, cell in enumerate(bank["split"]["source"]):
        for b in range(24):
            for r in range(8):
                source.append(meta(cell, "R-tree", b, r, 31500000, ci, 2000))
        for b in range(2):
            for r in range(8):
                stage_source.append(meta(cell, "R-tree", b, r, 31700000, ci, 1000))
    for ci, cell in enumerate(targets):
        for b in range(24):
            for r in range(8):
                for arm in ARMS:
                    score.append(meta(cell, arm, b, r, 31600000, ci, 2000))
    for ci, cell in enumerate(bank["split"]["source"] + bank["split"]["development"]):
        for r in range(4):
            for arm in ARMS:
                stage.append(
                    dict(
                        family="DG",
                        cell=cell,
                        arm=arm,
                        build=r % 2,
                        repeat=r,
                        seeds=[31800000 + 1000 * ci + 8 * r + k for k in range(8)],
                    )
                )
    return dict(source=source, stage_source=stage_source, score=score, stage=stage)


def seed_audit(schedule):
    raw = gzip.decompress((DATA / "historical_seeds.json.gz").read_bytes())
    provenance = json.loads((DATA / "provenance.json").read_text())
    if hashlib.sha256(raw).hexdigest() != provenance["historical_sha256"]:
        raise ValueError("historical seed snapshot changed")
    historic = set(json.loads(raw))
    # Explicit old schedules cover even unexecuted attempt/obsolete seed formulas.
    saved, targets = load_saved()
    for base in (22150000, 22180000):
        for metas in ordinary.schedules(
            saved["banks.json"], targets, scoring_base=base
        ):
            historic.update(m["seed"] for m in metas)
    for metas in restart.schedules(saved["banks.json"], targets):
        historic.update(s for m in metas for s in m["seeds"])
    historic |= (
        ordinary.SMOKE_SEEDS | ordinary.TAIL_SEEDS | ordinary.historical_seeds(saved)
    )
    sets, paired = {}, True
    for name, metas in schedule.items():
        uses = {}
        if len({restart.key(m) for m in metas}) != len(metas):
            paired = False
        for m in metas:
            for k, s in enumerate(m["seeds"]):
                uses.setdefault(s, []).append((m, k))
        for entries in uses.values():
            expected = set(ARMS) if name in ("score", "stage") else {"R-tree"}
            paired &= (
                len(entries) == len(expected)
                and {m["arm"] for m, k in entries} == expected
            )
            paired &= (
                len({(m["cell"], m["build"], m["repeat"], k) for m, k in entries}) == 1
            )
        sets[name] = set(uses)
    sets["control"] = set(range(31900000, 31900024)) | {31900100, 31900101}
    sets["smoke"] = set(range(32000000, 32000032)) | {32000100, 32000200}
    overlap = {a + "_historic": sorted(v & historic) for a, v in sets.items()}
    for i, a in enumerate(sets):
        for b in list(sets)[i + 1 :]:
            overlap[a + "_" + b] = sorted(sets[a] & sets[b])
    complete = {k: len(v) for k, v in schedule.items()} == dict(
        source=768, stage_source=64, score=4608, stage=96
    )
    return dict(
        admitted=bool(paired and complete and not any(overlap.values())),
        complete=complete,
        intended_pairing_valid=bool(paired),
        overlaps=overlap,
        published_seed_sets={k: sorted(v) for k, v in sets.items()},
        historical_seeds=sorted(historic),
        historical_snapshot=provenance,
        replay_exception="eight original saved 0024 jobs, validation only",
    )


def envelope(meta, saved, libraries, cutoff=65536):
    converted = meta | dict(arm="R-tree")
    e = restart.envelope(converted, saved, cutoff)
    e["meta"] = meta
    e["donors"] = (
        None
        if meta["arm"] == "R-tree"
        else [
            Tree(tuple(x["prefix"]))
            for x in libraries[meta["build"]][
                "entries" if meta["arm"] == "R-lib" else "controls"
            ]
        ]
    )
    return e


def execute(e):
    start, attempts = time.monotonic(), []
    for k, seed in enumerate(e["meta"]["seeds"]):
        a = restart.with_seed(e["first"], seed)
        tick = time.monotonic()
        row = search(a["job"], donor_library=e["donors"]) | a["meta"]
        row["worker_seconds"] = time.monotonic() - tick
        attempts.append(row)
        if row["solved"]:
            break
    elapsed = time.monotonic() - start
    return e["meta"] | dict(
        cap=8 * e["cutoff"],
        cutoff=e["cutoff"],
        pop_size=256,
        solved=attempts[-1]["solved"],
        solver=attempts[-1]["solver"],
        evaluations=sum(a["evaluations"] for a in attempts),
        worker_seconds=elapsed,
        attempts=attempts,
        attempt_count=len(attempts),
        scheduling_seconds=max(
            0.0, elapsed - sum(a["worker_seconds"] for a in attempts)
        ),
    )


def validate_rows(rows, metas, saved, cutoff=65536):
    # The existing independent verifier checks every attempt's RNG/budget/solver.
    # Separately enforce the original three-arm grid before normalizing arm names.
    by = {restart.key(r): r for r in rows}
    if len(by) != len(rows) or set(by) != {restart.key(m) for m in metas}:
        raise ValueError("missing/duplicate/unexpected library jobs")
    for m in metas:
        r = by[restart.key(m)]
        if any(r.get(k) != v for k, v in m.items()):
            raise ValueError("library job provenance changed")
        restart.validate_rows(
            [r | dict(arm="R-tree")], [m | dict(arm="R-tree")], saved, cutoff
        )
        if r["arm"] != "R-tree":
            for a in r["attempts"]:
                s = a["operator"]
                if (
                    s["library_draws"] + s["ordinary_donors"] != s["mutation"]
                    or s["library_insertions"] + s["rejected_library"]
                    != s["library_draws"]
                ):
                    raise ValueError("donor accounting mismatch")
    return sorted(rows, key=lambda r: str(restart.key(r)))


def build_libraries(rows, count, bank, stage=False):
    result = []
    for b in range(count):
        cohort = [r for r in rows if r["build"] == b]
        if len(cohort) != 32:
            raise ValueError("incomplete acquisition cohort")
        entries, seconds = extract(cohort, bank["split"]["source"])
        control, control_seconds = controls(
            entries, 31900100 + b if stage else 31900000 + b
        )
        tick = time.monotonic()
        verified = verify_entries(entries + control, bank["inputs"])
        verification_seconds = time.monotonic() - tick
        result.append(
            dict(
                build=b,
                entries=entries,
                controls=control,
                source_rows_hash=digest(cohort),
                source_solves=sum(r["solved"] for r in cohort),
                source_by_cell={
                    cell: dict(
                        jobs=len(jobs),
                        solves=sum(r["solved"] for r in jobs),
                        evaluations=sum(r["evaluations"] for r in jobs),
                        worker_seconds=sum(r["worker_seconds"] for r in jobs),
                    )
                    for cell in bank["split"]["source"]
                    for jobs in [[r for r in cohort if r["cell"] == cell]]
                },
                acquisition_evaluations=sum(r["evaluations"] for r in cohort),
                acquisition_worker_seconds=sum(r["worker_seconds"] for r in cohort),
                extraction_seconds=seconds,
                control_seconds=control_seconds,
                verification_seconds=verification_seconds,
                control_seed=31900100 + b if stage else 31900000 + b,
                verified_entries=verified,
            )
        )
    return result


class Runner:
    def __init__(self, args):
        self.args = args
        self.deadline = time.monotonic() + args.deadline_seconds - 30
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        restart.require_fresh(self.out)
        self.saved, self.targets = load_saved()
        self.bank = self.saved["banks.json"]["DG"]
        self.schedule = schedules(self.bank, self.targets["DG"])
        self.audit = seed_audit(self.schedule)
        self.freeze = dict(
            task=TASK,
            bank_hash=digest(self.bank),
            targets=self.targets["DG"],
            methods=method_hashes(),
            schedule_hash=digest(self.schedule),
            reference=json.loads((DATA / "provenance.json").read_text()),
            cutoff=65536,
            cap=524288,
            workers=10,
            rayon_threads=1,
            library_probability=0.5,
        )
        self.batches = {}
        for name, value in [
            (
                "config.json",
                dict(
                    arguments=vars(args),
                    git_commit=subprocess.check_output(
                        ["git", "rev-parse", "HEAD"], text=True
                    ).strip(),
                ),
            ),
            ("method_freeze.json", self.freeze),
            ("schedule_audit.json", self.audit),
            ("schedules.json", self.schedule),
        ]:
            write_json(self.out, name, value)
        if not self.audit["admitted"]:
            raise ValueError("seed audit failed")

    def jobs(self, metas, name, libraries=(), cutoff=65536, reference=False):
        rows = []
        start = time.monotonic()
        with (self.out / (name + ".jsonl")).open("w", buffering=1) as stream:

            def save(r):
                rows.append(r)
                stream.write(json.dumps(r, allow_nan=False) + "\n")
                write_json(
                    self.out,
                    "progress.json",
                    dict(phase=name, completed=len(rows), total=len(metas)),
                )

            jobs = (
                [restart.envelope(m, self.saved, cutoff) for m in metas]
                if reference
                else [envelope(m, self.saved, libraries, cutoff) for m in metas]
            )
            if not run_jobs(
                self.pool,
                restart.execute if reference else execute,
                jobs,
                self.deadline,
                save,
            ):
                raise TimeoutError("incomplete batch " + name)
        self.batches[name] = dict(
            jobs=len(rows),
            wall_seconds=time.monotonic() - start,
            worker_seconds=sum(r["worker_seconds"] for r in rows),
        )
        write_json(self.out, "timing.json", self.batches)
        return validate_rows(rows, metas, self.saved, cutoff)

    def replay(self):
        raw = gzip.decompress((DATA / "replay.jsonl.gz").read_bytes())
        if hashlib.sha256(raw).hexdigest() != self.freeze["reference"]["replay_sha256"]:
            raise ValueError("saved replay changed")
        original = [json.loads(line) for line in raw.splitlines()]
        metas = [
            {
                k: r[k]
                for k in ("family", "cell", "arm", "build", "repeat", "phase", "seeds")
            }
            for r in original
        ]
        replay = self.jobs(metas, "replay")
        expected = {restart.key(r): r for r in original}
        if any(
            restart.deterministic(r) != restart.deterministic(expected[restart.key(r)])
            for r in replay
        ):
            raise ValueError("off-path saved 0024 replay failed")
        return dict(
            passed=True,
            jobs=8,
            fields="all deterministic fields",
            rows_hash=digest(replay),
        )

    def prepare(self):
        replay = self.replay()
        write_json(self.out, "replay.json", replay)
        cutoff = 2048 if self.args.smoke else 65536
        src = self.jobs(self.schedule["stage_source"], "stage_source", cutoff=cutoff)
        libraries = build_libraries(src, 2, self.bank, stage=True)
        write_json(self.out, "stage_libraries.json", libraries)
        stage = self.jobs(self.schedule["stage"], "stage0", libraries, cutoff)
        means = {
            a: float(np.mean([r["worker_seconds"] for r in stage if r["arm"] == a]))
            for a in ARMS
        }
        batch = self.batches["stage0"]
        eff = min(10.0, batch["worker_seconds"] / batch["wall_seconds"])
        src_batch = self.batches["stage_source"]
        src_eff = min(10.0, src_batch["worker_seconds"] / src_batch["wall_seconds"])
        overhead = (
            sum(
                library["extraction_seconds"]
                + library["control_seconds"]
                + library["verification_seconds"]
                for library in libraries
            )
            / 2
        )
        score_projection = (
            1.3 * 1536 * sum(max(8.9, v) for v in means.values()) / eff + 90
        )
        prepare_projection = (
            sum(b["wall_seconds"] for b in self.batches.values())
            + 1.3
            * (
                768
                * max(8.9, float(np.mean([r["worker_seconds"] for r in src])))
                / src_eff
                + 24 * overhead
            )
            + 90
        )
        timing = dict(
            means=means,
            effective_concurrency=eff,
            source_effective_concurrency=src_eff,
            scoring_projected_seconds=score_projection,
            preparation_projected_seconds=prepare_projection,
            source_by_cell={
                c: dict(
                    jobs=len(rs),
                    solves=sum(r["solved"] for r in rs),
                    mean_evaluations=float(np.mean([r["evaluations"] for r in rs])),
                    mean_worker_seconds=float(
                        np.mean([r["worker_seconds"] for r in rs])
                    ),
                )
                for c in self.bank["split"]["source"]
                for rs in [[r for r in src if r["cell"] == c]]
            },
            library_yields=[len(library["entries"]) for library in libraries],
            control_draws=[
                [e["draws"] for e in library["controls"]] for library in libraries
            ],
            control_seconds=[library["control_seconds"] for library in libraries],
            projection="ten-worker sustained source/development; historical 8.9s/job floor; 30% reserve+90s",
        )
        write_json(self.out, "stage_gate.json", timing)
        if not self.args.smoke and (
            score_projection > 9000 or prepare_projection > 2700
        ):
            raise ValueError("approved timing gate failed: " + json.dumps(timing))
        if self.args.stage_only or self.args.smoke:
            write_json(
                self.out,
                "preparation.json",
                dict(
                    admitted=False,
                    smoke=self.args.smoke,
                    stage_only=True,
                    stage_gate=timing,
                ),
            )
            return
        rows = self.jobs(self.schedule["source"], "acquisition")
        libraries = build_libraries(rows, 24, self.bank)
        write_json(self.out, "libraries.json", libraries)
        p = dict(
            admitted=True,
            smoke=False,
            freeze=self.freeze,
            seed_audit=self.audit,
            replay=replay,
            stage_gate=timing,
            libraries_hash=digest(libraries),
            source_rows_hash=digest(rows),
            stage_source_hash=digest(src),
            stage_rows_hash=digest(stage),
            verified_entries=sum(library["verified_entries"] for library in libraries),
        )
        p["preparation_hash"] = digest(p)
        write_json(self.out, "preparation.json", p)

    def score(self):
        directory = Path(self.args.preparation)
        p = json.loads((directory / "preparation.json").read_text())
        if (
            not p.get("admitted")
            or p.get("smoke")
            or p.get("stage_only")
            or not p.get("replay", {}).get("passed")
            or p.get("stage_gate", {}).get("scoring_projected_seconds", float("inf"))
            > 9000
            or p.get("stage_gate", {}).get(
                "preparation_projected_seconds", float("inf")
            )
            > 2700
            or p.get("freeze") != self.freeze
            or p.get("seed_audit") != self.audit
            or p.get("preparation_hash")
            != digest({k: v for k, v in p.items() if k != "preparation_hash"})
        ):
            raise ValueError("requires admitted unchanged full preparation")
        libraries = json.loads((directory / "libraries.json").read_text())
        source = validate_rows(
            restart.jsonlines(directory / "acquisition.jsonl"),
            self.schedule["source"],
            self.saved,
        )
        stage_src = validate_rows(
            restart.jsonlines(directory / "stage_source.jsonl"),
            self.schedule["stage_source"],
            self.saved,
        )
        stage = validate_rows(
            restart.jsonlines(directory / "stage0.jsonl"),
            self.schedule["stage"],
            self.saved,
        )
        if (
            digest(libraries) != p["libraries_hash"]
            or digest(source) != p["source_rows_hash"]
            or digest(stage_src) != p["stage_source_hash"]
            or digest(stage) != p["stage_rows_hash"]
        ):
            raise ValueError("preparation evidence changed")
        if len(libraries) != 24 or [library["build"] for library in libraries] != list(
            range(24)
        ):
            raise ValueError("incomplete frozen libraries")
        for b, library in enumerate(libraries):
            rebuilt, _ = extract(
                [r for r in source if r["build"] == b], self.bank["split"]["source"]
            )
            if rebuilt != library["entries"]:
                raise ValueError("source-only extraction mismatch")
            rebuilt_control, _ = controls(library["entries"], library["control_seed"])
            if rebuilt_control != library["controls"]:
                raise ValueError("size-control replay mismatch")
            verify_entries(
                library["entries"] + library["controls"], self.bank["inputs"]
            )
        for name, v in [("preparation.json", p), ("libraries.json", libraries)]:
            write_json(self.out, name, v)
        # Source trees remain only in audit artifacts, never resident search donors.
        del source, stage_src, stage
        rows = self.jobs(self.schedule["score"], "search", libraries)
        from experiments.chem_tape.tree_library_report import report

        report(
            self.out, rows, libraries, self.bank, self.targets["DG"], p, self.batches
        )

    def run(self):
        self.pool = mp.get_context("spawn").Pool(10)
        try:
            self.prepare() if self.args.prepare else self.score()
        finally:
            self.pool.terminate()
            self.pool.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--stage-only", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=2700)
    args = parser.parse_args()
    if (
        args.workers != 10
        or os.environ.get("RAYON_NUM_THREADS") != "1"
        or not 30 < args.deadline_seconds <= (2700 if args.prepare else 9000)
        or ((args.smoke or args.stage_only) and not args.prepare)
        or (not args.prepare and not args.preparation)
    ):
        parser.error(
            "RAYON_NUM_THREADS=1, ten workers, bounded preparation or preparation-gated scoring required"
        )
    Runner(args).run()


if __name__ == "__main__":
    main()
