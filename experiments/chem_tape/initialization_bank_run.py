"""0315: frozen initialization factorial on ten 1723 training cells."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing as mp
import time
from pathlib import Path

from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.crossed_learning_run import (
    TRAINING,
    HOLDOUTS,
    DEFAULT_BANK,
    load_bank,
)
from experiments.chem_tape.initialization_run import (
    Runner as BaseRunner,
    SOURCE,
    initialized_search,
    encoding_checks,
)
from experiments.chem_tape.initialization_bank_report import (
    make_report,
    save_report,
    prior_descriptive,
    DESCRIPTIVE_SHA,
)

MAIN_SEEDS = list(range(3150000, 3150200))
DIAGNOSTIC_SEEDS = [3150900, 3150901]
REFERENCE = (
    Path(__file__).with_name("data") / "initialization_0315" / "reference_2331.jsonl.gz"
)
REFERENCE_SHA = "930a8c4ad1f803d20eb9753bb1ff71fc67cdf981b7c6e9ef6390f96edfad8b8c"
REFERENCE_COMMIT = "8f42f3805b19e1737fd3d2d12a23ad886aa38fab"


class Runner(BaseRunner):
    """Reuse the unchanged search payload and per-block validation from 2331."""

    def __init__(self, args):
        super().__init__(args)
        bank, _ = load_bank(args.bank)
        self.bank_cells = {
            c["id"]: {"id": c["id"], "labels": c["labels"]} for c in bank["cells"]
        }
        self.cells = {cid: self.bank_cells[cid] for cid in sum(TRAINING.values(), [])}
        self.seeds = DIAGNOSTIC_SEEDS if args.smoke or args.probe else MAIN_SEEDS
        self.work_deadline = self.deadline - 360
        self.validation.pop("search_law")
        self.validation["search_law_omitted"] = (
            "MMr omitted as approved; previous non-rejection is not equivalence."
        )
        prior_descriptive()
        self.validation["prior_descriptive_hash_verified"] = True
        self.config.update(
            task="2026-10-07-0315",
            cells=list(self.cells),
            seeds=self.seeds,
            law_seeds=[],
            probe_seeds=DIAGNOSTIC_SEEDS,
            reencoded_arms=["MG", "GM"],
            reference_commit=REFERENCE_COMMIT,
            reference_sha256=REFERENCE_SHA,
            prior_descriptive_sha256=DESCRIPTIVE_SHA,
            expected_main_searches=122000,
            expected_search_law_searches=0,
            expected_reproduction_searches=786,
            expected_probe_searches=1220,
            minimum_complete_seeds=120,
            reporting_reserve_seconds=360,
            scheduling="Two consecutive seed blocks dispatched together; checked complete prefix retained",
            weighting="Equal cell families/cells within family, equal map families/maps within family",
            historical_1723_seeds=[1723300, 1723301],
            historical_2331_seeds=[2331000, 2331001],
        )
        write_json(self.out, "config.json", self.config)
        self.persist_validation()

    def block_jobs(self, seed):
        return [self.job("G4", "GG", cid, seed) for cid in self.cells] + [
            self.job(tid, arm, cid, seed)
            for tid in self.map_ids
            for cid in self.cells
            for arm in ("MM", "MG", "GM")
        ]

    def reference_rows(self):
        raw = gzip.decompress(REFERENCE.read_bytes())
        if hashlib.sha256(raw).hexdigest() != REFERENCE_SHA:
            raise ValueError("2331 reference SHA256 mismatch")
        rows2331 = [json.loads(line) for line in raw.splitlines()]
        expected = {
            ("G4" if arm == "GG" else tid, arm, cid, seed)
            for tid in self.map_ids
            for arm in ("GG", "MM", "MG", "GM")
            for cid in sum(HOLDOUTS.values(), [])
            for seed in (2331000, 2331001)
        }
        actual = {(r["map"], r["arm"], r["cell"], r["seed"]) for r in rows2331}
        if len(rows2331) != 366 or actual != expected:
            raise ValueError("Wrong 2331 reproduction roster")
        raw1723 = gzip.decompress(
            (Path(self.args.source) / "fresh_scores.json.gz").read_bytes()
        )
        # frozen_source in BaseRunner independently pins the complete artifact.
        rows1723 = [r for r in json.loads(raw1723) if r["seed"] in (1723300, 1723301)]
        expected1723 = {
            (tid, cid, seed)
            for tid in self.maps
            for cid in self.cells
            for seed in (1723300, 1723301)
        }
        if (
            len(rows1723) != 420
            or {(r["arm"], r["cell"], r["seed"]) for r in rows1723} != expected1723
        ):
            raise ValueError("Wrong 1723 reproduction roster")
        refs = []
        for r in rows1723:
            # All substantive original fields, except historical phase annotation.
            ref = {
                k: v
                for k, v in r.items()
                if k not in ("seconds", "budget_seconds", "decode_seconds", "phase")
            }
            refs.append(("1723", ref, r["arm"], r["arm"], False))
        for ref in rows2331:
            tid, arm = ref["map"], ref["arm"]
            dst = "G4" if arm in ("GG", "MG") else tid
            src = "G4" if arm in ("GG", "GM") else tid
            refs.append(("2331", ref, dst, src, arm in ("MG", "GM")))
        if self.args.smoke:
            refs = [r for r in refs if r[1]["seed"] in (1723300, 2331000)]
        return refs

    def reproduction(self, pool):
        refs = self.reference_rows()
        jobs, expected = [], {}
        for origin, ref, dst, src, reencode in refs:
            tid = ref["map"] if origin == "2331" else ref["arm"]
            payload = (
                self.bank_cells[ref["cell"]],
                ref["arm"],
                self.maps[dst],
                ref["seed"],
                524288,
                256,
                self.inputs,
                self.config["alphabet"],
                dict(source_table=self.maps[src], reencode=reencode),
            )
            jobs.append((payload, tid, tid[:2] if tid != "G4" else "G"))
            key = (ref["arm"], ref["cell"], ref["seed"], tid)
            if key in expected:
                raise ValueError("Duplicate historical key")
            expected[key] = origin, ref
        checked, errors = [], []
        started = time.monotonic()
        with (self.out / "reproduction.jsonl").open("a", buffering=1) as stream:

            def record(row):
                origin, ref = expected.pop(
                    (row["arm"], row["cell"], row["seed"], row["map"])
                )
                changed = [k for k, v in ref.items() if row.get(k) != v]
                if changed:
                    errors.append(
                        dict(
                            origin=origin,
                            map=row["map"],
                            arm=row["arm"],
                            cell=row["cell"],
                            seed=row["seed"],
                            fields=changed,
                        )
                    )
                stream.write(
                    json.dumps(
                        dict(row, reference_origin=origin, mismatched_fields=changed),
                        allow_nan=False,
                    )
                    + "\n"
                )
                checked.append(row)

            complete = run_jobs(
                pool, initialized_search, jobs, self.work_deadline, record
            )
        self.validation["reproduction"] = dict(
            passed=complete and not errors and not expected,
            rows=len(checked),
            expected=len(jobs),
            errors=errors,
            seconds=sum(r["seconds"] for r in checked),
            wall_seconds=time.monotonic() - started,
            reference_2331_sha256=REFERENCE_SHA,
            roster_1723=420,
            roster_2331=366,
            smoke_reduced_roster=self.args.smoke,
        )
        self.persist_validation()
        if not self.validation["reproduction"]["passed"]:
            raise ValueError("Historical reproduction failed or timed out")

    def timing(self, rows, wall_seconds):
        groups = {}
        for arm in ("GG", "MM", "MG", "GM"):
            groups[arm] = {}
            for cid in self.cells:
                rs = [r for r in rows if r["arm"] == arm and r["cell"] == cid]
                groups[arm][cid] = dict(
                    n=len(rs),
                    seconds=sum(r["seconds"] for r in rs),
                    at_cap=sum(r["evaluations"] == self.cap for r in rs),
                    unsolved=sum(not r["solved"] for r in rs),
                )
        n = len({r["seed"] for r in rows})
        return dict(
            rows=len(rows),
            seeds=n,
            wall_seconds=wall_seconds,
            sum_search_seconds=sum(r["seconds"] for r in rows),
            effective_workers=sum(r["seconds"] for r in rows) / wall_seconds
            if wall_seconds
            else None,
            projected_200_seed_seconds=wall_seconds * 200 / n if n else None,
            projected_120_seed_seconds=wall_seconds * 120 / n if n else None,
            groups=groups,
            cap=self.cap,
            note="Observed complete blocks, no cell/map selection; short diagnostic projection has small-n uncertainty.",
        )

    def grid(self, pool):
        with (self.out / "search.jsonl").open("a", buffering=1) as stream:
            for start in range(0, len(self.seeds), 2):
                seeds = self.seeds[start : start + 2]
                blocks = {s: [] for s in seeds}
                jobs_by_seed = [self.block_jobs(s) for s in seeds]
                expected_counts = {s: len(js) for s, js in zip(seeds, jobs_by_seed)}
                # Alternation keeps both blocks in flight rather than a tail barrier.
                jobs = (
                    [job for pair in zip(*jobs_by_seed) for job in pair]
                    if len(seeds) == 2
                    else jobs_by_seed[0]
                )
                validated = set()

                def record(row):
                    seed = row["seed"]
                    blocks[seed].append(row)
                    self.rows.append(row)
                    stream.write(json.dumps(row, allow_nan=False) + "\n")
                    if len(blocks[seed]) == expected_counts[seed]:
                        self.check_block(blocks[seed], seed)
                        validated.add(seed)

                started = time.monotonic()
                complete = run_jobs(
                    pool, initialized_search, jobs, self.work_deadline, record
                )
                for seed in seeds:
                    if seed not in validated:
                        break
                    self.complete_seeds.append(seed)
                    self.validation["pairing_blocks"] += 1
                if start == 0 and len(validated) == len(seeds):
                    self.first_blocks_timing = self.timing(
                        [r for s in seeds for r in blocks[s]],
                        time.monotonic() - started,
                    )
                    write_json(self.out, "timing.json", self.first_blocks_timing)
                self.persist_validation()
                print(
                    json.dumps(
                        dict(
                            stage="grid",
                            complete_seeds=len(self.complete_seeds),
                            rows=len(self.rows),
                            elapsed_seconds=time.monotonic() - self.started,
                        )
                    ),
                    flush=True,
                )
                if not complete:
                    self.stop_reason = "internal deadline; checked complete seed prefix retained, partial/later seeds excluded"
                    break

    def run(self):
        pool = mp.get_context("spawn").Pool(self.args.workers)
        diagnostic = self.args.smoke or self.args.probe or self.args.validate_only
        self.first_blocks_timing = None
        try:
            self.validation["encoding"] = encoding_checks(self.maps, law_count=0)
            self.persist_validation()
            if not self.validation["encoding"]["passed"]:
                raise ValueError("Round-trip validation failed")
            self.reproduction(pool)
            if not self.args.validate_only:
                self.grid(pool)
            self.validation["passed"] = bool(
                self.validation["encoding"]["passed"]
                and self.validation["reproduction"]["passed"]
            )
        except Exception as error:
            self.stop_reason = f"{type(error).__name__}: {error}"
            self.validation["passed"] = False
        finally:
            pool.terminate()
            pool.join()
        self.persist_validation()
        retained = [r for r in self.rows if r["seed"] in self.complete_seeds]
        report = make_report(
            retained,
            self.map_ids,
            list(self.cells),
            self.complete_seeds,
            self.validation,
            diagnostic,
            replicates=1000 if diagnostic else 20000,
        )
        report.update(
            stop_reason=self.stop_reason,
            first_blocks_timing=self.first_blocks_timing,
            runtime=dict(
                wall_seconds_before_reporting=time.monotonic() - self.started,
                rows=len(self.rows),
                included_rows=len(retained),
                excluded_partial_rows=len(self.rows) - len(retained),
                sum_search_seconds=sum(r["seconds"] for r in self.rows),
            ),
        )
        write_json(self.out, "result.json", report)
        if self.first_blocks_timing is None:
            write_json(
                self.out, "timing.json", dict(reason="No complete initial batch")
            )
        save_report(self.out, report, retained, list(self.cells))
        report["runtime"]["wall_seconds"] = time.monotonic() - self.started
        write_json(self.out, "result.json", report)
        print(
            json.dumps(
                dict(
                    outcome=report["outcome"],
                    n_seeds=len(self.complete_seeds),
                    validation_passed=self.validation["passed"],
                    stop_reason=self.stop_reason,
                )
            ),
            flush=True,
        )
        return (
            1
            if self.stop_reason and not self.stop_reason.startswith("internal deadline")
            else 0
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(SOURCE))
    parser.add_argument("--bank", default=str(DEFAULT_BANK))
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=25200)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--smoke", action="store_true")
    modes.add_argument("--probe", action="store_true")
    modes.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 360:
        parser.error(
            "Positive workers and deadline exceeding reporting reserve required"
        )
    raise SystemExit(Runner(args).run())


if __name__ == "__main__":
    main()
