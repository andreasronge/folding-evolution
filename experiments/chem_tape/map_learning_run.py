"""Approved 0132 outer-map refinement with a timing-only stage-0 gate.

Run as a module. All experiment artifacts, checkpoints and raw observations
are written to RUN_DIR; no test scores enter adaptation or scheduling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import signal
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for, split_shape
from experiments.chem_tape.assembly_maps import frozen_controls
from experiments.chem_tape.assembly_run import sample
from experiments.chem_tape.composition_calibrate import token_counts
from experiments.chem_tape.composition_report import count_interval
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import (
    Decoder,
    cumulative,
    outputs,
    search,
)
from experiments.chem_tape.map_learning import (
    LEARNERS,
    drift,
    initial,
    log_cost,
    mutate,
    schedule_projection,
    table_for,
)
from experiments.chem_tape.map_learning_report import make_report, plots

BANK = Path(__file__).with_name("data") / "post_addition_0132_bank.json"
REUSED_SAMPLING = BANK.with_name("post_addition_0132_sampling.json")


def load_bank():
    bank = json.loads(BANK.read_text())
    assert bank["domain"] == "D1331" and len(bank["cells"]) == 8
    assert bank["split"] == split_shape(bank["cells"])
    assert bank["split"]["holdouts"] == ["PA:(S?M:S)+M", "PA:(S?M:S)+m"]
    inputs = inputs_for(bank["domain"])
    for cell in bank["cells"]:
        assert cell["retained"] and cell["shape"] == "PA"
        assert (
            hashlib.sha256(
                np.asarray(cell["labels"], dtype="<i8").tobytes()
            ).hexdigest()
            == cell["label_hash"]
        )
        assert np.array_equal(outputs([cell["canonical"]], inputs)[0], cell["labels"])
    return bank


class Runner:
    def __init__(self, args):
        # Set before canonical checks initialize Rust's global Rayon pool.
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.args = args
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        # Never append a second experiment to old observations.
        if (self.out / "search.jsonl").exists():
            raise ValueError(
                "RUN_DIR already contains search observations; use a fresh directory"
            )
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds
        self.work_deadline = self.deadline - 180
        self.bank = load_bank()
        self.inputs = inputs_for("D1331")
        self.cells = {
            c["id"]: dict(id=c["id"], labels=c["labels"]) for c in self.bank["cells"]
        }
        self.controls = frozen_controls()
        self.tests = []
        self.generations = []
        self.finals = {}
        self.total_evaluations = 0
        self.phase = "initial"
        self.pool = None
        self.schedule = None
        self.train_cap = 65536
        self.test_cap = 524288
        self.seed_offset = 1000000 if args.smoke else 0
        self.infeasible = None
        write_json(self.out, "bank.json", self.bank)
        write_json(
            self.out, "reused_sampling.json", json.loads(REUSED_SAMPLING.read_text())
        )
        write_json(
            self.out,
            "config.json",
            dict(
                task="2026-10-06-0132",
                arguments=vars(args),
                bank_sha256=hashlib.sha256(BANK.read_bytes()).hexdigest(),
                controls={
                    a: dict(hash=Decoder(t).hash(), table=t.tolist())
                    for a, t in self.controls.items()
                },
                train_cap=self.train_cap,
                test_cap=self.test_cap,
                population=256,
                executor="v2_rmin",
                allele_length=32,
                allele_range=23000,
                training_cases=64,
                crossover=0.7,
                allele_mutation=0.03,
                outer_mu=4,
                outer_lambda=12,
                mutation_coordinates=3,
                mutation_sigma=0.5,
                normalization="proportional lower-bound water filling, stable largest remainder",
                seed_namespaces=dict(
                    calibration=132000000,
                    learning=132100000,
                    selection=132200000,
                    test=132300000,
                    marginal=132400000,
                    sampling=132500000,
                    mutation=132600000,
                    bootstrap=132700000,
                ),
                smoke_seed_offset=self.seed_offset,
                test_values_never_select=True,
            ),
        )

    def checkpoint(self, state, **kwargs):
        write_json(
            self.out,
            "status.json",
            dict(
                state=state,
                phase=self.phase,
                elapsed_seconds=time.monotonic() - self.started,
                cumulative_inner_evaluations=self.total_evaluations,
                finished_map_ids=list(self.finals),
                schedule=self.schedule,
                **kwargs,
            ),
        )

    def searches(self, tables, cell_ids, seeds, cap, phase):
        self.phase = phase
        rows = []
        jobs = [
            (self.cells[c], a, t, seed + self.seed_offset, cap, 256, self.inputs)
            for a, t in tables.items()
            for c in cell_ids
            for seed in seeds
        ]

        def save(row):
            row["phase"] = phase
            rows.append(row)
            self.total_evaluations += row["evaluations"]
            with (self.out / "search.jsonl").open("a") as f:
                f.write(json.dumps(row, allow_nan=False) + "\n")
            if phase.startswith("test:"):
                self.tests.append(row)

        tick = time.monotonic()
        if not run_jobs(self.pool, search, jobs, self.work_deadline, save):
            raise TimeoutError(
                "search deadline; unfinished observations retained in search.jsonl"
            )
        rows.sort(key=lambda r: (r["arm"], r["cell"], r["seed"]))
        return rows, time.monotonic() - tick

    def evolve(
        self, learner, k, generations, per_cell=4, selection_seeds=20, calibration=False
    ):
        tid = f"{learner}{k + 1}"
        start = initial(learner, self.controls)
        start_table = table_for(learner, start, self.controls)
        rng = np.random.default_rng(
            132600000
            + LEARNERS.index(learner) * 100
            + k
            + (10000 if calibration else 0)
            + self.seed_offset
        )
        parents = [start.copy() for _ in range(4)]
        parent_ids = [f"{tid}:initial:{i}" for i in range(4)]
        total_rows, durations = [], []
        tick = time.monotonic()
        adaptation_evaluations = 0
        changed, differences = [], []
        for gen in range(generations):
            vectors = list(parents)
            origin, mutations = [], []
            for _ in range(12):
                parent_index = int(rng.integers(4))
                child, mutation = mutate(parents[parent_index], start, rng)
                vectors.append(child)
                origin.append(parent_index)
                mutations.append(mutation)
            tables = [table_for(learner, v, self.controls) for v in vectors]
            names = [f"{tid}:g{gen + 1}:candidate{i}" for i in range(16)]
            seed_base = (
                132001000 + gen * 100
                if calibration
                else 132100000 + k * 10000 + gen * 100
            )
            rows, seconds = self.searches(
                dict(zip(names, tables)),
                self.bank["split"]["training"],
                range(seed_base, seed_base + per_cell),
                self.train_cap,
                f"{'calibration' if calibration else 'learn'}:{tid}:g{gen + 1}",
            )
            by = {name: [r for r in rows if r["arm"] == name] for name in names}
            scores = [
                float(np.mean([log_cost(r, self.train_cap) for r in by[name]]))
                for name in names
            ]
            chosen = np.argsort(scores, kind="stable")[:4].tolist()
            diagnostics = []
            for i, parent_index in enumerate(origin):
                child_index = i + 4
                is_changed = not np.array_equal(
                    tables[child_index], tables[parent_index]
                )
                paired = np.asarray(
                    [log_cost(r, self.train_cap) for r in by[names[child_index]]]
                ) - np.asarray(
                    [log_cost(r, self.train_cap) for r in by[names[parent_index]]]
                )
                changed.append(is_changed)
                differences.extend(paired.tolist())
                diagnostics.append(
                    dict(
                        parent_index=parent_index,
                        table_changed=is_changed,
                        paired_difference_mean=float(paired.mean()),
                        paired_difference_sd=float(paired.std(ddof=1)),
                        **mutations[i],
                    )
                )
            adaptation_evaluations += sum(r["evaluations"] for r in rows)
            record = dict(
                trajectory=tid,
                calibration=calibration,
                generation=gen + 1,
                parent_ids=parent_ids,
                selected_indices=chosen,
                scores=scores,
                seed_base=seed_base + self.seed_offset,
                seeds_per_cell=per_cell,
                candidates=[
                    dict(
                        id=name,
                        vector=v.tolist(),
                        table=t.tolist(),
                        table_hash=Decoder(t).hash(),
                        l1_drift=drift(t, start_table),
                    )
                    for name, v, t in zip(names, vectors, tables)
                ],
                mutations=diagnostics,
                generation_seconds=seconds,
                cumulative_inner_evaluations=adaptation_evaluations,
                cumulative_seconds=time.monotonic() - tick,
            )
            with (self.out / "generations.jsonl").open("a") as f:
                f.write(json.dumps(record, allow_nan=False) + "\n")
            if not calibration:
                self.generations.append(record)
            parents = [vectors[i] for i in chosen]
            parent_ids = [names[i] for i in chosen]
            total_rows.extend(rows)
            durations.append(seconds)
            self.checkpoint("running")
        diagnostic = dict(
            train_rows=len(total_rows),
            train_seconds_per_run=max(
                float(np.mean([r["seconds"] for r in total_rows])),
                sum(durations) * self.args.workers / len(total_rows),
            ),
            generation_seconds=durations,
            mutation_table_change_fraction=float(np.mean(changed)),
            paired_mutation_score_mean=float(np.mean(differences)),
            paired_mutation_score_sd=float(np.std(differences, ddof=1)),
        )
        if calibration:
            return diagnostic
        tables = {
            f"{tid}:selection{i}": table_for(learner, v, self.controls)
            for i, v in enumerate(parents)
        }
        seed_base = 132200000 + k * 1000
        rows, seconds = self.searches(
            tables,
            self.bank["split"]["training"],
            range(seed_base, seed_base + selection_seeds),
            self.train_cap,
            f"selection:{tid}",
        )
        scores = [
            float(np.mean([log_cost(r, self.train_cap) for r in rows if r["arm"] == a]))
            for a in tables
        ]
        best = int(np.argmin(scores))
        table = list(tables.values())[best]
        record = dict(
            trajectory=tid,
            learner=learner,
            trajectory_index=k,
            vector=parents[best].tolist(),
            table=table.tolist(),
            table_hash=Decoder(table).hash(),
            l1_drift=drift(table, start_table),
            selection_scores=scores,
            selected_parent_index=best,
            selected_parent_id=parent_ids[best],
            adaptation_evaluations=adaptation_evaluations
            + sum(r["evaluations"] for r in rows),
            adaptation_seconds=time.monotonic() - tick,
            diagnostics=diagnostic,
        )
        self.finals[tid] = record
        write_json(self.out, "final_maps.json", self.finals)
        return table

    def marginal(self, name, table, k):
        seed = 132400000 + k * 10 + self.seed_offset
        tick = time.monotonic()
        counts, seconds = token_counts(Decoder(table), seed, 312500, self.work_deadline)
        tied = np.tile(cumulative(counts), (24, 1))
        checked, check_seconds = token_counts(
            Decoder(tied), seed + 1, 312500, self.work_deadline
        )
        p, q = counts / counts.sum(), checked / checked.sum()
        valid = bool(np.all(np.abs(p - q) <= np.maximum(0.02 * p, 0.0005)))
        record = dict(
            source=name,
            table=tied.tolist(),
            table_hash=Decoder(tied).hash(),
            seed=seed,
            check_seed=seed + 1,
            counts=counts.tolist(),
            check_counts=checked.tolist(),
            genotypes=312500,
            check_genotypes=312500,
            seconds=seconds,
            check_seconds=check_seconds,
            agreement_passed=valid,
        )
        write_json(self.out, f"{name}_marginal.json", record)
        if not valid:
            raise RuntimeError("learned marginal agreement gate failed")
        return tied, time.monotonic() - tick

    def evaluate(self, name, table):
        split = self.bank["split"]
        for cells, n in [
            (split["training"], 2 if self.args.smoke else 50),
            (split["holdouts"], 2 if self.args.smoke else 100),
        ]:
            self.searches(
                {name: table},
                cells,
                range(132300000, 132300000 + n),
                self.test_cap,
                "test:" + name,
            )

    def calibration(self):
        diagnostics = {}
        for a in LEARNERS:
            diagnostics[a] = self.evolve(
                a,
                0,
                1 if self.args.smoke else 2,
                per_cell=1 if self.args.smoke else 4,
                calibration=True,
            )
        repeat = []
        for i in range(2):
            rows, _ = self.searches(
                {"G": self.controls["G"]},
                self.bank["split"]["training"],
                range(
                    132005000 + i * 100,
                    132005000 + i * 100 + (2 if self.args.smoke else 20),
                ),
                self.train_cap,
                f"repeatability:{i}",
            )
            costs = np.array([log_cost(r, self.train_cap) for r in rows])
            repeat.append(
                dict(
                    n=len(rows),
                    cost=float(costs.mean()),
                    se=float(costs.std(ddof=1) / np.sqrt(len(rows))),
                    solve_fraction=float(np.mean([r["solved"] for r in rows])),
                )
            )
        rates = {
            a: dict(train=diagnostics[a]["train_seconds_per_run"]) for a in LEARNERS
        }
        bench = {}
        for a in LEARNERS + ("G-marg", "U", "F"):
            table = (
                table_for(a, initial(a, self.controls), self.controls)
                if a in LEARNERS
                else self.controls[a]
            )
            cells = (
                self.bank["split"]["holdouts"] if a in ("U", "F") else list(self.cells)
            )
            rows, wall = self.searches(
                {a: table},
                cells,
                range(132006000, 132006000 + (2 if self.args.smoke else 4)),
                self.test_cap,
                "timing:" + a,
            )
            # Saturation overhead is already measured by the learning batches.
            train_times = [
                r["seconds"]
                for r in rows
                if r["cell"] in self.bank["split"]["training"]
            ]
            hold_times = [
                r["seconds"]
                for r in rows
                if r["cell"] in self.bank["split"]["holdouts"]
            ]
            rates.setdefault(a, {})["holdout200"] = 200 * float(np.mean(hold_times))
            if train_times:
                rates[a]["test500"] = (
                    300 * float(np.mean(train_times)) + rates[a]["holdout200"]
                )
            bench[a] = dict(
                rows=len(rows),
                wall_seconds=wall,
                rates=rates[a],
                per_cell_seconds={
                    c: float(np.mean([r["seconds"] for r in rows if r["cell"] == c]))
                    for c in cells
                },
            )
        _, marginal_seconds = self.marginal("calibration_G", self.controls["G"], 100)
        chunks = []
        sampling_jobs = [
            (
                a,
                self.controls["G"],
                132007000 + i + self.seed_offset,
                100000,
                list(self.cells.values()),
                self.inputs,
            )
            for i, a in enumerate(("C", "M"))
        ]
        if not run_jobs(
            self.pool, sample, sampling_jobs, self.work_deadline, chunks.append
        ):
            raise TimeoutError("sampling calibration deadline")
        sample_seconds = max(r["seconds"] for r in chunks) * 1000
        projection = schedule_projection(
            rates,
            workers=self.args.workers,
            elapsed=time.monotonic() - self.started,
            marginal_seconds=marginal_seconds,
            sample_seconds=sample_seconds,
        )
        mismatch = abs(repeat[0]["cost"] - repeat[1]["cost"]) > 0.6
        if mismatch and not self.args.smoke:
            projection["feasible"] = False
            projection["selected"] = None
        record = dict(
            diagnostics=diagnostics,
            repeatability=repeat,
            harness_mismatch=mismatch,
            stage2_benchmarks=bench,
            marginal_seconds=marginal_seconds,
            sampling_seconds_per_1e8=sample_seconds,
            sampling_timing_chunks=chunks,
            projection=projection,
            decision_inputs="timings and training-only G repeatability; no holdout scores",
            smoke_only=self.args.smoke,
        )
        write_json(self.out, "stage0.json", record)
        return record

    def sampling(self):
        chunks = []
        jobs = []
        # Small chunks retain partial counts under a deadline; unique chunk
        # seeds across maps. No chunks are reused between C and M.
        chunk_size = 10000 if self.args.smoke else 1000000
        count = 10000 if self.args.smoke else 100000000
        for i, (name, record) in enumerate(self.finals.items()):
            if record["learner"] not in ("C", "M"):
                continue
            for j in range(count // chunk_size):
                jobs.append(
                    (
                        name,
                        np.asarray(record["table"]),
                        132500000 + i * 1000 + j + self.seed_offset,
                        chunk_size,
                        list(self.cells.values()),
                        self.inputs,
                    )
                )

        def save(row):
            chunks.append(row)
            with (self.out / "sampling.jsonl").open("a") as f:
                f.write(json.dumps(row) + "\n")

        complete = run_jobs(self.pool, sample, jobs, self.work_deadline, save)
        summary = {}
        for name in sorted({j[0] for j in jobs}):
            rs = [r for r in chunks if r["arm"] == name]
            n = sum(r["genotypes"] for r in rs)
            summary[name] = dict(genotypes=n, complete=n == count, cells={})
            for cid in self.cells:
                hits = sum(r["hits"][cid] for r in rs)
                summary[name]["cells"][cid] = dict(
                    hits=hits,
                    rate=hits / n if n else None,
                    interval_95=count_interval(hits, n),
                    zero_hit_upper_95=float(-np.expm1(np.log(0.05) / n))
                    if n and not hits
                    else None,
                )
        write_json(
            self.out,
            "sampling.json",
            dict(
                complete=complete,
                maps=summary,
                frozen_rates_source="0001 sampling.json; G and G-marg unchanged",
            ),
        )
        return complete

    def run(self):
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        complete = False
        sampling_complete = None
        reason = None
        interrupted = None

        def stop(signum, _frame):
            nonlocal interrupted
            interrupted = signal.Signals(signum).name
            self.work_deadline = time.monotonic()

        previous_handlers = {
            sig: signal.signal(sig, stop) for sig in (signal.SIGINT, signal.SIGTERM)
        }
        try:
            self.checkpoint("calibrating")
            calibration = self.calibration()
            self.schedule = calibration["projection"]["selected"]
            if self.args.smoke:
                self.schedule = dict(
                    trajectories=dict(C=1, M=1, T=1),
                    generations=1,
                    sampling=True,
                    remaining_seconds=3600,
                )
                self.schedule["expected_test_counts"] = {
                    a: 16 for a in ("C1", "M1", "T1", "C-marg1", "G", "G-marg")
                }
                self.schedule["expected_test_counts"].update(U=4, F=4)
            if self.schedule is None:
                self.infeasible = (
                    "G repeatability mismatch"
                    if calibration["harness_mismatch"]
                    else "All approved schedules exceed the seven-hour gate"
                )
                notes = f"# Stage-0 infeasible\n\n{self.infeasible}.\n\n"
                notes += (
                    "Measured training seconds/search: "
                    + ", ".join(
                        f"{a}={calibration['diagnostics'][a]['train_seconds_per_run']:.3f}"
                        for a in LEARNERS
                    )
                    + ".\n\n"
                )
                notes += (
                    "G repeatability costs: "
                    + ", ".join(
                        f"{r['cost']:.3f} (n={r['n']}, SE={r['se']:.3f})"
                        for r in calibration["repeatability"]
                    )
                    + ".\n\n"
                )
                notes += "Projected wall minutes (all approved schedules):\n\n"
                for p in calibration["projection"]["attempts"]:
                    notes += f"- {p['trajectories']}, {p['generations']} generations, sampling={p['sampling']}: {p['projected_total_seconds'] / 60:.1f} min\n"
                notes += "\nSee stage0.json for PA test timings, marginal/sampling cost and projection components. "
                notes += (
                    "Resolve the repeatability mismatch before adaptation."
                    if calibration["harness_mismatch"]
                    else "A steward-approved smaller learning budget or staged study is needed; no further reduction was executed."
                )
                (self.out / "infeasible.md").write_text(notes + "\n")
                reason = self.infeasible
                return
            write_json(self.out, "schedule.json", self.schedule)
            # A hard kill also leaves an explicit incomplete-study marker.
            write_json(
                self.out,
                "result.json",
                make_report([], self.bank["split"], self.schedule, False),
            )
            # Frozen controls evaluated first, within the measured reservation.
            for name in ("G", "G-marg"):
                self.evaluate(name, self.controls[name])
            for name in ("U", "F"):
                self.searches(
                    {name: self.controls[name]},
                    self.bank["split"]["holdouts"],
                    range(132300000, 132300000 + (2 if self.args.smoke else 100)),
                    self.test_cap,
                    "test:" + name,
                )
            for k in range(max(self.schedule["trajectories"].values())):
                for a in LEARNERS:
                    if k >= self.schedule["trajectories"][a]:
                        continue
                    if not self.args.smoke:
                        # Reserve the remaining fixed core schedule, not just
                        # the fast next trajectory. Optional sampling drops first.
                        remaining_learning = 0.0
                        for kk in range(k, 6):
                            for aa in LEARNERS:
                                if (
                                    kk >= self.schedule["trajectories"][aa]
                                    or f"{aa}{kk + 1}" in self.finals
                                ):
                                    continue
                                n = self.schedule["trajectories"][aa]
                                remaining_learning += (
                                    self.schedule["learning_seconds"][aa]
                                    + self.schedule["test_seconds"][aa]
                                ) / n
                                if aa == "C":
                                    remaining_learning += (
                                        self.schedule["test_seconds"]["C-marg"] / 6
                                        + calibration["marginal_seconds"]
                                    )
                        if (
                            time.monotonic() + 1.15 * remaining_learning
                            > self.work_deadline
                        ):
                            raise TimeoutError(
                                "Insufficient reserved time for the remaining fixed learning/evaluation schedule"
                            )
                    tid = f"{a}{k + 1}"
                    table = self.evolve(
                        a,
                        k,
                        self.schedule["generations"],
                        per_cell=1 if self.args.smoke else 4,
                        selection_seeds=1 if self.args.smoke else 20,
                    )
                    self.evaluate(tid, table)
                    if a == "C":
                        marginal, _ = self.marginal(tid, table, k)
                        self.evaluate(f"C-marg{k + 1}", marginal)
                    self.checkpoint("running")
            complete = True
            if self.schedule["sampling"]:
                self.phase = "sampling"
                sampling_complete = self.sampling()
        except TimeoutError as error:
            reason = f"Interrupted by {interrupted}" if interrupted else str(error)
        finally:
            self.pool.terminate()
            self.pool.join()
            for sig, handler in previous_handlers.items():
                signal.signal(sig, handler)
            if self.schedule:
                result = make_report(
                    self.tests,
                    self.bank["split"],
                    self.schedule,
                    complete,
                    replicates=200 if self.args.smoke else 10000,
                )
                result.update(
                    smoke_only=self.args.smoke,
                    sampling_complete=sampling_complete,
                    stop_reason=reason,
                    adaptation=self.finals,
                    elapsed_seconds=time.monotonic() - self.started,
                )
                if self.args.smoke:
                    result["outcome"] = None
                write_json(self.out, "result.json", result)
                plots(
                    self.out,
                    self.generations,
                    self.tests,
                    self.bank["split"]["holdouts"],
                )
                summary = f"# PA map refinement\n\nComplete fixed schedule: {result['complete']}. Smoke only: {self.args.smoke}.\n\n"
                if result["outcome"]:
                    summary += f"{result['outcome']}\n\n"
                summary += f"Missing maps: {result['missing_map_ids']}. Stop reason: {reason}.\n\nDetailed contrasts, costs and scope: result.json. Calibration and frozen schedule: stage0.json, schedule.json.\n"
                (self.out / "summary.md").write_text(summary)
            else:
                write_json(
                    self.out,
                    "result.json",
                    dict(
                        complete=False, infeasible=self.infeasible, stop_reason=reason
                    ),
                )
                (self.out / "summary.md").write_text(
                    f"# Stage-0 stopped\n\n{reason}. See stage0.json and infeasible.md.\n"
                )
            self.checkpoint(
                "complete"
                if complete
                else "infeasible"
                if self.infeasible
                else "incomplete",
                stop_reason=reason,
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=27600)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 180:
        parser.error(
            "positive workers and a deadline longer than the 180s reporting reserve are required"
        )
    Runner(args).run()


if __name__ == "__main__":
    main()
