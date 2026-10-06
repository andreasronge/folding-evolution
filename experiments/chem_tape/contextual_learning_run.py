"""Deadline-bounded 0811 M-start matched contextual continuation study.

Run as a module. All observations/checkpoints are confined to RUN_DIR.
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

from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.assembly_maps import frozen_controls
from experiments.chem_tape.assembly_run import sample
from experiments.chem_tape.composition_report import count_interval
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder, outputs, search
from experiments.chem_tape.contextual_learning import (
    diagnostics,
    projection,
    start_vector,
    step,
    table,
)
from experiments.chem_tape.contextual_report import map_changes, report
from experiments.chem_tape.map_learning import log_cost
from experiments.chem_tape.map_learning_report import plots
from experiments.chem_tape.map_learning_run import BANK, load_bank

SOURCES = Path(__file__).with_name("data") / "contextual_0811_sources.json"
SEEDS = dict(
    harness=811200000,
    calibration=811300000,
    timing=811400000,
    learning=812000000,
    selection=813000000,
    test=814000000,
    off_family=815000000,
    sampling=816000000,
    mutation=817000000,
    calibration_mutation=817100000,
    bootstrap=818000000,
)


def variation(effects, noise, starts, replicates=2000):
    """Approximate variance subtraction with start/child uncertainty.

    Noise is estimated within the six fixed cell strata; shared parent errors
    are retained in the signed raw effects, not claimed to be fully removed.
    """
    means, noise, starts = np.array(effects), np.array(noise), np.array(starts)
    true_sd = float(np.sqrt(max(0, means.var(ddof=1) - noise.mean())))
    rng = np.random.default_rng(SEEDS["bootstrap"])
    unique = sorted(set(starts.tolist()))
    boots = []
    for _ in range(replicates):
        indices = []
        for k in rng.choice(unique, len(unique)):
            choices = np.flatnonzero(starts == k)
            indices.extend(rng.choice(choices, len(choices)).tolist())
        boots.append(
            np.sqrt(max(0, means[indices].var(ddof=1) - noise[indices].mean()))
        )
    return dict(
        n=len(means),
        signed_child_minus_parent=means.tolist(),
        mean_effect=float(means.mean()),
        observed_sd=float(means.std(ddof=1)),
        estimated_noise_sd=float(np.sqrt(noise.mean())),
        true_effect_sd=true_sd,
        approximate_true_sd_interval_95=np.quantile(boots, [0.025, 0.975]).tolist(),
        fraction_beneficial=float(np.mean(means < 0)),
        fraction_better_05=float(np.mean(means < -0.5)),
        uncertainty_scope="approximate variance subtraction; fixed cell strata and shared-parent noise; spread is not beneficial signal",
    )


class Runner:
    def __init__(self, args):
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.args = args
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("RUN_DIR already contains a study; use a fresh directory")
        self.started = time.monotonic()
        self.work_deadline = self.started + args.deadline_seconds - 180
        self.offset = (
            10000000
            if args.smoke
            else 20000000
            if getattr(args, "calibration_only", False)
            else 0
        )
        self.bank = load_bank()
        self.sources = json.loads(SOURCES.read_text())
        self.controls = frozen_controls()
        self.inputs = inputs_for("D1331")
        self.off = self.sources["off_family"]["cells"]
        assert len(self.off) == 8 and sum(c["shape"] == "BE" for c in self.off) == 2
        for c in self.off:
            assert c["retained"] and c["shape"] != "PA"
            assert (
                hashlib.sha256(np.array(c["labels"], dtype="<i8").tobytes()).hexdigest()
                == c["label_hash"]
            )
            assert np.array_equal(
                outputs([c["canonical"]], self.inputs)[0], c["labels"]
            )
        self.cells = {
            c["id"]: dict(id=c["id"], labels=c["labels"])
            for c in self.bank["cells"] + self.off
        }
        self.inherited = {
            a: np.array(r["table"]) for a, r in self.sources["starts"].items()
        }
        for a, r in self.sources["starts"].items():
            for arm in ("M+", "R"):
                assert np.array_equal(
                    table(start_vector(r["vector"], arm), self.controls),
                    self.inherited[a],
                )
            assert Decoder(self.inherited[a]).hash() == r["table_hash"]
        self.tests, self.generations, self.finals, self.completed_pairs = [], [], {}, []
        self.evaluations = 0
        self.phase_costs = {}
        self.phase, self.schedule, self.stage0 = "initial", None, None
        self.pool = None
        write_json(self.out, "bank.json", self.bank)
        write_json(self.out, "sources.json", self.sources)
        write_json(
            self.out,
            "config.json",
            dict(
                task="2026-10-06-0811",
                arguments=vars(args),
                bank_sha256=hashlib.sha256(BANK.read_bytes()).hexdigest(),
                sources_sha256=hashlib.sha256(SOURCES.read_bytes()).hexdigest(),
                seeds=SEEDS,
                verification_seed_offset=self.offset,
                population=256,
                allele_length=32,
                allele_range=23000,
                domain="D1331",
                executor="v2_rmin",
                training_cases=64,
                crossover=0.7,
                allele_mutation=0.03,
                training_cap=65536,
                test_cap=524288,
                outer_mu=4,
                outer_lambda=12,
                pair_order=[
                    dict(start=k, rep=rep) for rep in ("a", "b") for k in range(1, 7)
                ],
                controls={
                    "G": dict(
                        table=self.controls["G"].tolist(),
                        hash=Decoder(self.controls["G"]).hash(),
                    )
                },
                bounds="each multiplier and residual coordinate independently +/- log16",
                normalization="250-count support; proportional water filling; stable largest remainder",
                test_values_never_select=True,
                timing_only_schedule=True,
                calibration_role="descriptive only; spread never gates learning (code-review amendment)",
            ),
        )

    def seed(self, phase, delta=0):
        return SEEDS[phase] + delta + self.offset

    def checkpoint(self, state, **extra):
        write_json(
            self.out,
            "status.json",
            dict(
                state=state,
                phase=self.phase,
                elapsed_seconds=time.monotonic() - self.started,
                cumulative_inner_evaluations=self.evaluations,
                finished_map_ids=list(self.finals),
                completed_pairs=self.completed_pairs,
                schedule=self.schedule,
                **extra,
            ),
        )

    def searches(self, tables, cells, seeds, cap, phase):
        self.phase = phase
        jobs = [
            (self.cells[c], a, t, s, cap, 256, self.inputs)
            for a, t in tables.items()
            for c in cells
            for s in seeds
        ]
        rows = []

        def save(row):
            row["phase"] = phase
            rows.append(row)
            self.evaluations += row["evaluations"]
            category = phase.split(":")[0]
            cost = self.phase_costs.setdefault(
                category, dict(searches=0, evaluations=0, worker_seconds=0.0)
            )
            cost["searches"] += 1
            cost["evaluations"] += row["evaluations"]
            cost["worker_seconds"] += row["seconds"]
            with (self.out / "search.jsonl").open("a") as f:
                f.write(json.dumps(row, allow_nan=False) + "\n")
            if phase.startswith("test:"):
                self.tests.append(row)

        tick = time.monotonic()
        if not run_jobs(self.pool, search, jobs, self.work_deadline, save):
            raise TimeoutError("Search deadline; partial observations retained")
        rows.sort(key=lambda r: (r["arm"], r["cell"], r["seed"]))
        return rows, time.monotonic() - tick

    def evaluate(self, tables, off=False):
        if off:
            groups = [
                (
                    list(c["id"] for c in self.off),
                    2 if self.args.smoke else 50,
                    "off_family",
                )
            ]
        else:
            groups = [
                (self.bank["split"]["training"], 2 if self.args.smoke else 50, "test"),
                (self.bank["split"]["holdouts"], 2 if self.args.smoke else 200, "test"),
            ]
        for cells, n, namespace in groups:
            base = self.seed(namespace)
            self.searches(
                tables,
                cells,
                range(base, base + n),
                524288,
                "test:" + ("off:" if off else "PA:") + ",".join(tables),
            )

    def calibration(self):
        train = self.bank["split"]["training"]
        n = 2 if self.args.smoke else 20
        base = self.seed("harness")
        rows, _ = self.searches(
            {"G": self.controls["G"]}, train, range(base, base + n), 65536, "harness"
        )
        cost = float(np.mean([log_cost(r, 65536) for r in rows]))
        mismatch = not self.args.smoke and abs(cost - 13.84) > 0.6
        record = dict(
            harness=dict(
                mean_log2_cost=cost,
                reference=13.84,
                tolerance=0.6,
                n=len(rows),
                solves=sum(r["solved"] for r in rows),
            ),
            harness_mismatch=mismatch,
            smoke_only=self.args.smoke,
            zero_residuals_reproduce_all_saved_tables=True,
        )
        if mismatch:
            write_json(self.out, "stage0.json", record)
            return record
        effects = {a: [] for a in ("M+", "R")}
        noises = {a: [] for a in effects}
        starts = {a: [] for a in effects}
        cal_rows, cal_wall = [], {a: 0 for a in effects}
        timing_vectors = None
        child_records = []
        for k in range(1, 2 if self.args.smoke else 7):
            multiplier = self.sources["starts"][f"M{k}"]["vector"]
            rng = np.random.default_rng(self.seed("calibration_mutation", k))
            seeds = range(
                self.seed("calibration", k * 100),
                self.seed("calibration", k * 100) + (2 if self.args.smoke else 4),
            )
            parent_rows, _ = self.searches(
                {"parent": self.inherited[f"M{k}"]},
                train,
                seeds,
                65536,
                f"calibration:M{k}:parent",
            )
            parent = {(r["cell"], r["seed"]): log_cost(r, 65536) for r in parent_rows}
            for arm in effects:
                origin = start_vector(multiplier, arm)
                vectors, tables = {}, {}
                for j in range(2 if self.args.smoke else 16):
                    v, mutation = step(origin, rng, row_only=(arm == "R"))
                    name = f"{arm}:M{k}:child{j}"
                    vectors[name], tables[name] = v, table(v, self.controls)
                    child_records.append(
                        dict(
                            id=name,
                            start=k,
                            vector=v.tolist(),
                            mutation=mutation,
                            table_hash=Decoder(tables[name]).hash(),
                        )
                    )
                rs, wall = self.searches(
                    tables, train, seeds, 65536, f"calibration:M{k}:{arm}"
                )
                cal_rows.extend(rs)
                cal_wall[arm] += wall
                for name in tables:
                    d = np.array(
                        [
                            [
                                log_cost(r, 65536) - parent[r["cell"], r["seed"]]
                                for r in rs
                                if r["arm"] == name and r["cell"] == c
                            ]
                            for c in train
                        ]
                    )
                    effects[arm].append(float(d.mean()))
                    # Variance of the mean across fixed cells, preserving
                    # cross-cell covariance of the shared seed index.
                    noises[arm].append(float(d.mean(0).var(ddof=1) / d.shape[1]))
                    starts[arm].append(k)
                if k == 1 and arm == "R":
                    # Representative mixed R and co-adapted ablation; no
                    # score picks this table (the first child is fixed).
                    rvec = next(iter(vectors.values())).copy()
                    rvec[:23], _ = step(np.array(multiplier), rng)
                    timing_vectors = dict(
                        R=rvec, R_abl=rvec[:23], **{"M+": np.array(multiplier)}
                    )
        spread = {
            a: variation(
                effects[a], noises[a], starts[a], 100 if self.args.smoke else 2000
            )
            for a in effects
        }
        rates = {}
        for arm in effects:
            rs = [r for r in cal_rows if r["arm"].startswith(arm + ":")]
            effective = max(
                np.mean([r["seconds"] for r in rs]),
                cal_wall[arm] * self.args.workers / len(rs),
            )
            rates[arm] = dict(train=float(effective))
        # Stage-0 timings use training cells only: no withheld/off-family
        # observation enters schedule selection or any adaptation decision.
        timing_tables = {
            "G": self.controls["G"],
            **{a: table(v, self.controls) for a, v in timing_vectors.items()},
        }
        base = self.seed("timing")
        bench, wall = self.searches(
            timing_tables,
            train,
            range(base, base + (2 if self.args.smoke else 6)),
            524288,
            "timing:training524",
        )
        overhead = max(1.0, wall * self.args.workers / sum(r["seconds"] for r in bench))
        mean_times = {
            a: float(np.mean([r["seconds"] for r in bench if r["arm"] == a]) * overhead)
            for a in timing_tables
        }
        gtime = mean_times["G"]
        for a in ("M+", "R", "R_abl"):
            # Proposal's ~13/s test and 1.14 worker-seconds off-family
            # anchors are retained; scale upwards for slower representative
            # maps. Learned R and its ablation may be slower than starts.
            rates.setdefault(a, {})["test"] = max(
                mean_times[a], self.args.workers / 12.0
            )
            rates[a]["off"] = max(mean_times[a], 1.14 * max(1.0, mean_times[a] / gtime))
        rates["reference"] = dict(
            test=max(mean_times["M+"], mean_times["G"], self.args.workers / 12.0),
            off=max(mean_times["M+"], mean_times["G"], 1.14),
        )
        chunks = []
        count = 10000 if self.args.smoke else 100000
        jobs = [
            (
                f"timing{i}",
                self.inherited[f"M{1 + i % 6}"],
                self.seed("timing", 100 + i),
                count,
                list(self.cells.values()),
                self.inputs,
            )
            for i in range(self.args.workers)
        ]
        tick = time.monotonic()
        if not run_jobs(self.pool, sample, jobs, self.work_deadline, chunks.append):
            raise TimeoutError("sampling timing deadline")
        sample_seconds = (
            (time.monotonic() - tick) * 100000000 / (count * self.args.workers)
        )
        decision = projection(
            rates,
            self.args.workers,
            time.monotonic() - self.started,
            sample_seconds,
        )
        record.update(
            variation=spread,
            calibration_children=child_records,
            calibration_role="descriptive only; spread never gates learning (code-review amendment)",
            calibration_solves={
                a: dict(
                    n=sum(r["arm"].startswith(a + ":") for r in cal_rows),
                    solves=sum(
                        r["solved"] for r in cal_rows if r["arm"].startswith(a + ":")
                    ),
                )
                for a in effects
            },
            rates=rates,
            timing_tables={
                a: dict(
                    table=t.tolist(), hash=Decoder(t).hash(), mean_seconds=mean_times[a]
                )
                for a, t in timing_tables.items()
            },
            timing_training_solve_counts={
                a: dict(
                    n=sum(r["arm"] == a for r in bench),
                    solves=sum(r["solved"] for r in bench if r["arm"] == a),
                )
                for a in timing_tables
            },
            sample_seconds_per_1e8_per_map=sample_seconds,
            sampling_timing_chunks=chunks,
            projection=decision,
            decision_inputs="training-only timings; calibration spread descriptive; no holdout/off-family scores",
        )
        write_json(self.out, "stage0.json", record)
        return record

    def evolve(self, arm, k, rep, pair_index):
        tid = f"{arm}{k}{rep}"
        origin = start_vector(self.sources["starts"][f"M{k}"]["vector"], arm)
        rng = np.random.default_rng(
            self.seed("mutation", pair_index * 100 + (arm == "R"))
        )
        parents = [origin.copy() for _ in range(4)]
        tick, evaluations = time.monotonic(), 0
        for gen in range(self.schedule["generations"]):
            vectors = list(parents)
            mutations = []
            for _ in range(12):
                p = int(rng.integers(4))
                v, details = step(parents[p], rng)
                vectors.append(v)
                mutations.append(dict(parent_index=p, **details))
            names = [f"{tid}:g{gen + 1}:candidate{i}" for i in range(16)]
            tables = [table(v, self.controls) for v in vectors]
            base = self.seed("learning", pair_index * 10000 + gen * 100)
            rows, wall = self.searches(
                dict(zip(names, tables)),
                self.bank["split"]["training"],
                range(base, base + (1 if self.args.smoke else 4)),
                65536,
                f"learn:{tid}:g{gen + 1}",
            )
            scores = [
                float(np.mean([log_cost(r, 65536) for r in rows if r["arm"] == n]))
                for n in names
            ]
            chosen = np.argsort(scores, kind="stable")[:4].tolist()
            evaluations += sum(r["evaluations"] for r in rows)
            record = dict(
                trajectory=tid,
                start=k,
                rep=rep,
                learner=arm,
                generation=gen + 1,
                seed_base=base,
                scores=scores,
                selected_indices=chosen,
                mutations=mutations,
                generation_seconds=wall,
                cumulative_inner_evaluations=evaluations,
                cumulative_seconds=time.monotonic() - tick,
                candidates=[
                    dict(
                        id=n,
                        vector=v.tolist(),
                        table_hash=Decoder(t).hash(),
                        **diagnostics(v, origin, self.controls),
                    )
                    for n, v, t in zip(names, vectors, tables)
                ],
            )
            with (self.out / "generations.jsonl").open("a") as f:
                f.write(json.dumps(record, allow_nan=False) + "\n")
            self.generations.append(record)
            parents = [vectors[i] for i in chosen]
            self.checkpoint("running")
        names = [f"{tid}:selection{i}" for i in range(4)]
        tables = [table(v, self.controls) for v in parents]
        base = self.seed("selection", pair_index * 1000)
        rows, _ = self.searches(
            dict(zip(names, tables)),
            self.bank["split"]["training"],
            range(base, base + (2 if self.args.smoke else 20)),
            65536,
            f"selection:{tid}",
        )
        scores = [
            float(np.mean([log_cost(r, 65536) for r in rows if r["arm"] == n]))
            for n in names
        ]
        best = int(np.argmin(scores))
        self.finals[tid] = dict(
            trajectory=tid,
            learner=arm,
            start=k,
            rep=rep,
            vector=parents[best].tolist(),
            table=tables[best].tolist(),
            table_hash=Decoder(tables[best]).hash(),
            selection_scores=scores,
            selected_parent_index=best,
            adaptation_evaluations=evaluations + sum(r["evaluations"] for r in rows),
            adaptation_seconds=time.monotonic() - tick,
            **diagnostics(parents[best], origin, self.controls),
        )
        if arm == "R":
            ablation = table(parents[best][:23], self.controls)
            self.finals[f"R_abl{k}{rep}"] = dict(
                learner="R_abl",
                start=k,
                rep=rep,
                source=tid,
                vector=parents[best][:23].tolist(),
                table=ablation.tolist(),
                table_hash=Decoder(ablation).hash(),
                adaptation_evaluations=0,
                adaptation_seconds=0,
            )
        write_json(self.out, "final_maps.json", self.finals)

    def sampling(self, names):
        self.phase = "sampling"
        count, size = (10000, 10000) if self.args.smoke else (100000000, 1000000)
        chunks, jobs = [], []
        for i, name in enumerate(names):
            tab = (
                self.inherited[name]
                if name in self.inherited
                else np.array(self.finals[name]["table"])
            )
            for j in range(count // size):
                jobs.append(
                    (
                        name,
                        tab,
                        self.seed("sampling", i * 1000 + j),
                        size,
                        list(self.cells.values()),
                        self.inputs,
                    )
                )

        def save(row):
            chunks.append(row)
            with (self.out / "sampling.jsonl").open("a") as f:
                f.write(json.dumps(row) + "\n")

        done = run_jobs(self.pool, sample, jobs, self.work_deadline, save)
        summary = {}
        for name in names:
            rs = [r for r in chunks if r["arm"] == name]
            n = sum(r["genotypes"] for r in rs)
            summary[name] = dict(
                genotypes=n,
                complete=n == count,
                cpu_seconds=sum(r["seconds"] for r in rs),
                cells={},
            )
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
                complete=done,
                maps=summary,
                reused_G=self.sources["reused_sampling"]["G"],
                scope="descriptive; sparse/zero counts are bounds, not absence; supply and variation change together",
            ),
        )
        return done

    def run(self):
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        complete, sampling_complete, reason = False, None, None
        off_family_complete = None
        mismatch = False
        interrupted = None

        def stop(signum, _frame):
            nonlocal interrupted
            interrupted = signal.Signals(signum).name
            self.work_deadline = time.monotonic()

        handlers = {
            sig: signal.signal(sig, stop) for sig in (signal.SIGINT, signal.SIGTERM)
        }
        try:
            self.checkpoint("calibrating")
            self.stage0 = self.calibration()
            mismatch = self.stage0["harness_mismatch"]
            if mismatch:
                reason = "G harness mismatch; no interpretation or further stages"
                return
            self.schedule = self.stage0["projection"]["selected"]
            if self.args.smoke:
                # Tiny smoke batches have startup/tail costs unsuitable for
                # projecting 334k searches; exercise the pipeline regardless.
                self.schedule = dict(
                    generations=1,
                    sampling=True,
                    off_family=True,
                    pair_seconds=0,
                    projected_total_seconds=None,
                    smoke_only=True,
                )
            if getattr(self.args, "calibration_only", False):
                reason = "Calibration-only feasibility check; no reference tests or learning executed"
                return
            if self.schedule is None:
                reason = "All approved timing-only schedules exceed seven hours"
                (self.out / "infeasible.md").write_text(
                    "# Infeasible timing projection\n\n"
                    + reason
                    + ".\n\nSee stage0.json for measured rates and all projections. A steward-approved staged or smaller design is needed.\n"
                )
                return
            self.schedule = dict(self.schedule)
            if self.args.smoke:
                self.schedule.update(generations=1, sampling=True, off_family=True)
            write_json(self.out, "schedule.json", self.schedule)
            write_json(
                self.out,
                "result.json",
                dict(complete=False, outcome=None, reason="Run in progress"),
            )
            write_json(self.out, "final_maps.json", {})
            refs = {"G": self.controls["G"], **self.inherited}
            self.evaluate(refs)
            self.evaluate(refs, off=True)
            pairs = [(k, rep) for rep in ("a", "b") for k in range(1, 7)]
            if self.args.smoke:
                pairs = [(1, "a")]
            for i, (k, rep) in enumerate(pairs):
                # Admit only a whole pair with its immediate PA tests.
                # Rates may increase; previous learning/test timings can
                # only strengthen the reservation, never change design.
                measured = [p["seconds"] for p in self.completed_pairs]
                pair_reserve = max(
                    [1.1 * self.schedule["pair_seconds"]] + [1.1 * s for s in measured]
                )
                if (
                    not self.args.smoke
                    and time.monotonic() + pair_reserve > self.work_deadline
                ):
                    raise TimeoutError(
                        "Insufficient reserved time for next whole pair and immediate tests"
                    )
                tick = time.monotonic()
                for arm in ("M+", "R"):
                    self.evolve(arm, k, rep, i)
                names = [f"{a}{k}{rep}" for a in ("M+", "R", "R_abl")]
                self.evaluate({n: np.array(self.finals[n]["table"]) for n in names})
                self.completed_pairs.append(
                    dict(start=k, rep=rep, seconds=time.monotonic() - tick)
                )
                self.checkpoint("running")
            complete = True
            if self.schedule["off_family"]:
                names = [
                    f"{a}{k}a"
                    for k in range(1, 2 if self.args.smoke else 7)
                    for a in ("M+", "R")
                ]
                self.evaluate(
                    {n: np.array(self.finals[n]["table"]) for n in names}, off=True
                )
                off_family_complete = True
            if self.schedule["sampling"]:
                names = list(self.inherited)
                names += [
                    f"{a}{k}a"
                    for k in range(1, 2 if self.args.smoke else 7)
                    for a in ("M+", "R")
                ]
                sampling_complete = self.sampling(names)
        except TimeoutError as error:
            reason = f"Interrupted by {interrupted}" if interrupted else str(error)
        except Exception as error:
            reason = f"{type(error).__name__}: {error}"
            raise
        finally:
            self.pool.terminate()
            self.pool.join()
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
            result = report(
                self.tests,
                self.bank["split"],
                self.off,
                self.completed_pairs,
                1 if self.args.smoke else 12,
                complete,
                mismatch,
                200 if self.args.smoke else 10000,
                self.seed("bootstrap"),
                (2, 2, 2) if self.args.smoke else (50, 200, 50),
            )
            result.update(
                smoke_only=self.args.smoke,
                sampling_complete=sampling_complete,
                learned_off_family_complete=off_family_complete,
                stop_reason=reason,
                elapsed_seconds=time.monotonic() - self.started,
                adaptation=self.finals,
                cumulative_inner_evaluations=self.evaluations,
                schedule=self.schedule,
                map_changes=map_changes(self.finals),
                phase_costs=self.phase_costs,
            )
            if self.args.smoke:
                result["outcome"] = None
            write_json(self.out, "result.json", result)
            if self.tests or self.generations:
                plots(
                    self.out,
                    self.generations,
                    self.tests,
                    self.bank["split"]["holdouts"],
                )
            (self.out / "summary.md").write_text(
                f"# M-start contextual continuation\n\nComplete: {complete}; smoke: {self.args.smoke}; completed pairs: {len(self.completed_pairs)}.\n\nOutcome: {result['outcome']}. Stop reason: {reason}.\n\nSee stage0.json for calibration and timing, schedule.json for the frozen design, result.json for clustered contrasts, coverage and cost, and curves.png for learning/drift/solve curves.\n"
            )
            self.checkpoint(
                "complete" if result["complete"] else "stopped", stop_reason=reason
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=27600)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--calibration-only",
        action="store_true",
        help="Measure the approved Stage 0 without executing later stages",
    )
    args = parser.parse_args()
    if args.workers < 1 or args.deadline_seconds < 240 or args.deadline_seconds > 27600:
        parser.error(
            "workers must be positive and deadline between 240 and 27600 seconds"
        )
    Runner(args).run()


if __name__ == "__main__":
    main()
