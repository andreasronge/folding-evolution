"""0821 training-only calibration and paired rank-one continuation.

Full runs, smoke runs and fixed throughput probes write exclusively to RUN_DIR.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder, search
from experiments.chem_tape.crossed_learning_run import (
    BANK_SHA,
    DEFAULT_BANK,
    G4_HASH,
    TRAINING,
)
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.map_learning import log_cost, table_for
from experiments.chem_tape.rank_one_learning import (
    SEEDS,
    calibration_estimate,
    choose_effort,
    diagnostics,
    reservation,
    start_vector,
    step,
    table,
)

SOURCE = Path(__file__).with_name("data") / "crossed_1723"
SOURCE_HASHES = {
    "config.json": "f345d3e277569cd3e380b98dbd1cfd362b9796bd3e850f1cc135209f258156b5",
    "trajectories.json": "94138e35c6aa36b583704a69e83cab8437f11a5c55f7e3c1696fe03fc5a481b3",
}


def load_sources():
    raw = DEFAULT_BANK.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BANK_SHA:
        raise ValueError("1603 bank SHA mismatch")
    bank = json.loads(raw)
    if bank["domain"] != "D1331" or bank["smoke_only"]:
        raise ValueError("invalid bank")
    all_cells = {c["id"]: c for c in bank["cells"]}
    cells = {}
    for cid in sum(TRAINING.values(), []):
        c = all_cells[cid]
        if not c["retained"] or not c["canonical_verified"] or len(c["labels"]) != 1331:
            raise ValueError("unverified training cell")
        cells[cid] = dict(id=cid, labels=c["labels"])
    data = {}
    for name, sha in SOURCE_HASHES.items():
        raw = (SOURCE / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError(f"1723 SHA mismatch: {name}")
        data[name] = json.loads(raw)
    config, sources = data["config.json"], data["trajectories.json"]
    if (
        config["task"] != "2026-10-06-1723"
        or config["smoke_only"]
        or config["probe_only"]
        or config["training"] != TRAINING
        or config["bank_sha256"] != BANK_SHA
        or config["g4_hash"] != G4_HASH
        or config["alphabet"] != ALPHABET
        or config["domain"] != "D1331"
    ):
        raise ValueError("invalid source configuration")
    g4 = tables()["G4"]
    if Decoder(g4).hash() != G4_HASH:
        raise ValueError("G4 hash mismatch")
    expected = {f"{f}{k}" for f in TRAINING for k in range(1, 11)}
    if set(sources) != expected:
        raise ValueError("invalid source roster")
    starts = {}
    for tid, r in sources.items():
        m = np.array(r["vector"], dtype=float)
        if (
            r["trajectory"] != tid
            or r["family"] != tid[:2]
            or m.shape != (24,)
            or not np.all(np.isfinite(m))
        ):
            raise ValueError("invalid saved map")
        rebuilt = table_for("M", m, {"G": g4})
        if (
            not np.array_equal(rebuilt, r["table"])
            or Decoder(rebuilt).hash() != r["table_hash"]
        ):
            raise ValueError("saved token map does not reconstruct")
        starts[tid] = dict(
            vector=m.tolist(), table=rebuilt.tolist(), table_hash=r["table_hash"]
        )
    return cells, starts, g4


class Runner:
    def __init__(self, args):
        self.args = args
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists() or (self.out / "search.jsonl").exists():
            raise ValueError("use a fresh RUN_DIR")
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds
        self.work_deadline = self.deadline - 180
        self.cells, self.starts, self.g4 = load_sources()
        self.inputs = inputs_for("D1331")
        self.offset = 10_000_000 if args.smoke else 20_000_000 if args.probe else 0
        self.pool = None
        self.pairs, self.pair_times, self.schedule = [], [], []
        self.finals, self.fresh, self.costs, self.units = {}, [], {}, []
        self.slow_a, self.slow_b = 0.0, 0.0
        self.inner_cap = 4096 if args.smoke else 65536
        self.fresh_cap = 8192 if args.smoke else 524288
        self.fresh_n = 2 if args.smoke else 50
        self.final_n = 12 if args.smoke else 100
        self.effective_workers = 0.95 * args.workers
        self.config = dict(
            task="2026-10-07-0821",
            arguments=vars(args),
            smoke_only=args.smoke,
            probe_only=args.probe,
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            bank_sha256=BANK_SHA,
            source_hashes=SOURCE_HASHES,
            g4_hash=G4_HASH,
            training=TRAINING,
            seeds=SEEDS,
            seed_offset=self.offset,
            calibration_seed_rule="base+start_index*100000+candidate_index*1000+block*500+j",
            learning_seed_rule="base+pair_index*10000+generation*100+j",
            selection_seed_rule="base+pair_index*1000+j",
            fresh_seeds=list(
                range(self.seed("fresh"), self.seed("fresh") + self.fresh_n)
            ),
            population=256,
            length=32,
            allele_range=24000,
            training_cases=64,
            crossover=0.7,
            mutation=0.03,
            alphabet=ALPHABET,
            domain="D1331",
            outer_mu=2,
            outer_lambda=6,
            inner_cap=self.inner_cap,
            fresh_cap=self.fresh_cap,
            final_searches_per_parent=self.final_n,
            objective="mean log2 evaluations; unsolved=2*cap at every stage",
            calibration_stops_learning=False,
            selection_uses_training_only=True,
            representation="m[24], centred unit-RMS a[25], centred b[24]; a*b clipped at +/-ln16",
        )
        write_json(self.out, "config.json", self.config)
        write_json(self.out, "starts.json", self.starts)
        write_json(self.out, "training_cells.json", self.cells)
        write_json(
            self.out,
            "validation.json",
            dict(
                passed=True,
                pinned_hashes=True,
                reconstructed_maps=20,
                search_payload_fields=["id", "labels"],
                no_historical_scores_loaded=True,
                training_only=True,
            ),
        )

    def seed(self, phase, delta=0):
        return SEEDS[phase] + self.offset + delta

    def job(self, name, t, cid, seed, cap):
        if cid not in self.cells:
            raise ValueError("non-training search rejected")
        return self.cells[cid], name, t, int(seed), cap, 256, self.inputs, ALPHABET

    def block(self, name, t, family, seed, n, cap, rotation=0):
        cells = TRAINING[family]
        return [
            self.job(name, t, cells[(j + rotation) % len(cells)], seed + j, cap)
            for j in range(n)
        ]

    def jobs(self, jobs, phase):
        expected = {
            (j[1], j[0]["id"], j[3]): hashlib.sha256(
                np.asarray(j[2], dtype="<i8").tobytes()
            ).hexdigest()
            for j in jobs
        }
        if len(expected) != len(jobs):
            raise ValueError("duplicate jobs")
        for j in jobs:
            if j[0]["id"] not in self.cells or set(j[0]) != {"id", "labels"}:
                raise ValueError("invalid search payload")
        rows, seen, seed_cases = [], set(), {}
        tick = time.monotonic()

        def save(row):
            key = row["arm"], row["cell"], row["seed"]
            if key not in expected or key in seen or row["table_hash"] != expected[key]:
                raise ValueError("wrong, duplicate or mismatched search result")
            cases = row["training_indices"]
            if row["seed"] in seed_cases and cases != seed_cases[row["seed"]]:
                raise ValueError("shared seeds do not pair training cases")
            seed_cases[row["seed"]] = cases
            seen.add(key)
            row["phase"] = phase
            rows.append(row)
            with (self.out / "search.jsonl").open("a") as f:
                f.write(json.dumps(row, allow_nan=False) + "\n")
            category = phase.split(":")[0]
            c = self.costs.setdefault(
                category, dict(searches=0, solves=0, evaluations=0, worker_seconds=0.0)
            )
            c["searches"] += 1
            c["solves"] += int(row["solved"])
            c["evaluations"] += row["evaluations"]
            c["worker_seconds"] += row["seconds"]

        if not run_jobs(self.pool, search, jobs, self.work_deadline, save):
            raise TimeoutError("search deadline; partial rows retained")
        if seen != set(expected):
            raise ValueError("missing search rows")
        rows.sort(key=lambda r: (r["arm"], r["seed"], r["cell"]))
        return rows, time.monotonic() - tick

    def record(self, file, value):
        with (self.out / file).open("a") as f:
            f.write(json.dumps(value, allow_nan=False) + "\n")

    def timing(self, rows, wall):
        groups = {}
        overhead = max(
            1.0, wall * self.effective_workers / sum(r["seconds"] for r in rows)
        )
        for r in rows:
            key = r["operator"] + ":" + r["family"]
            groups.setdefault(key, []).append(r)
        return {
            k: dict(
                n=len(rs),
                solves=sum(r["solved"] for r in rs),
                solve_fraction=float(np.mean([r["solved"] for r in rs])),
                seconds_per_search=float(np.mean([r["seconds"] for r in rs])),
                reserve_seconds_per_search=float(
                    np.mean([r["seconds"] for r in rs]) * overhead
                ),
            )
            for k, rs in groups.items()
        }

    def calibration(self):
        n = 12 if self.args.smoke else 48
        pn = 24 if self.args.smoke else 192
        mutants = 4 if self.args.smoke else 24
        collected, wall_total = [], 0.0
        for si, tid in enumerate(("BE9", "BE10", "PA9", "PA10")):
            family = tid[:2]
            origin = start_vector(
                self.starts[tid]["vector"],
                np.random.default_rng(self.seed("direction", si)),
            )
            if not np.array_equal(table(origin, self.g4), self.starts[tid]["table"]):
                raise ValueError("zero residual changed saved start")
            parents = []
            for block in range(2):
                rs, wall = self.jobs(
                    self.block(
                        f"{tid}:parent:{block}",
                        table(origin, self.g4),
                        family,
                        self.seed("calibration", si * 100000 + block * 500),
                        pn,
                        self.inner_cap,
                    ),
                    "calibration:parent",
                )
                wall_total += wall
                parents.append(
                    float(np.mean([log_cost(r, self.inner_cap) for r in rs]))
                )
            for ui, operator in enumerate(("context", "context", "token")):
                rng = np.random.default_rng(self.seed("mutation", 1000 + si * 10 + ui))
                v0 = start_vector(
                    self.starts[tid]["vector"],
                    np.random.default_rng(self.seed("direction", 100 + si * 10 + ui)),
                )
                uid = f"{tid}:{operator}:{ui}"
                effects, variances, records, jobs = [], [], [], []
                for j in range(mutants):
                    v, mutation = step(
                        v0,
                        rng,
                        self.g4,
                        force="b" if operator == "context" else "token",
                    )
                    name = f"{uid}:mutant{j}"
                    t = table(v, self.g4)
                    records.append(
                        dict(
                            id=name,
                            vector=v.tolist(),
                            mutation=mutation,
                            table_hash=Decoder(t).hash(),
                            diagnostics=diagnostics(
                                v, self.g4, np.array(self.starts[tid]["table"])
                            ),
                        )
                    )
                    ci = 1 + ui * mutants + j
                    for block in range(2):
                        jobs.extend(
                            self.block(
                                name + f":{block}",
                                t,
                                family,
                                self.seed(
                                    "calibration", si * 100000 + ci * 1000 + block * 500
                                ),
                                n,
                                self.inner_cap,
                            )
                        )
                rs, wall = self.jobs(jobs, f"calibration:{uid}")
                wall_total += wall
                for r in rs:
                    r.update(operator=operator, family=family)
                collected.extend(rs)
                for record in records:
                    blocks = [
                        np.array(
                            [
                                log_cost(r, self.inner_cap)
                                for r in rs
                                if r["arm"] == record["id"] + f":{b}"
                            ]
                        )
                        for b in range(2)
                    ]
                    effects.append(
                        [
                            blocks[0].mean() - parents[0],
                            blocks[1].mean() - parents[1],
                            blocks[0][: n // 2].mean() - parents[0],
                        ]
                    )
                    variances.append([x.var(ddof=1) for x in blocks])
                unit = dict(
                    id=uid,
                    start=tid,
                    family=family,
                    operator=operator,
                    parent_block_means=parents,
                    effects=np.asarray(effects).tolist(),
                    variances=np.asarray(variances).tolist(),
                    mutants=records,
                )
                self.units.append(unit)
                write_json(self.out, "calibration_units.json", self.units)
        replicates = 100 if self.args.smoke else 2000
        rng = np.random.default_rng(self.seed("bootstrap"))
        estimates = {}
        for operator in ("context", "token"):
            us = [u for u in self.units if u["operator"] == operator]
            estimates[operator] = dict(
                pooled=calibration_estimate(us, rng, replicates),
                families={
                    f: calibration_estimate(
                        [u for u in us if u["family"] == f], rng, replicates
                    )
                    for f in TRAINING
                },
                units={u["id"]: calibration_estimate([u], rng, replicates) for u in us},
            )
        # Parent timings do not set operator rates; use only mutant observations.
        rates = self.timing(collected, wall_total)
        self.slow_a = max(r["reserve_seconds_per_search"] for r in rates.values())
        effort = choose_effort(estimates["context"]["pooled"])
        self.n = 12 if self.args.smoke else effort["n"]
        self.generations = 2 if self.args.smoke else 3840 // (8 * self.n)
        self.config.update(
            scoring_effort=self.n,
            generations=self.generations,
            searches_per_trajectory=8 * self.n * self.generations + 2 * self.final_n,
        )
        write_json(self.out, "config.json", self.config)
        self.calibration_result = dict(
            estimates=estimates,
            effort=effort,
            rates=rates,
            searches=self.costs["calibration"]["searches"],
            bootstrap_replicates=replicates,
            stage_b_always_runs=True,
            seconds=time.monotonic() - self.started,
        )
        write_json(self.out, "calibration.json", self.calibration_result)
        print(
            f"Stage A complete: n={self.n}, slowest={self.slow_a:.3f}s/search",
            flush=True,
        )

    def evolve_pair(self, tid, pi):
        tick = time.monotonic()
        family = tid[:2]
        start = np.asarray(self.starts[tid]["table"])
        origins, parents, rngs = {}, {}, {}
        mix = {
            a: {
                op: dict(proposed=0, survived=0, clipped_elements=0, redraws=0)
                for op in ("token", "b", "a")
            }
            for a in ("T", "C")
        }
        for ai, arm in enumerate(("T", "C")):
            origins[arm] = start_vector(
                self.starts[tid]["vector"],
                np.random.default_rng(self.seed("direction", 1000 + pi * 10 + ai)),
            )
            parents[arm] = [origins[arm].copy(), origins[arm].copy()]
            rngs[arm] = np.random.default_rng(self.seed("mutation", pi * 10 + ai))
        all_rows = []
        for gen in range(self.generations):
            candidates, mutations, names, jobs = {}, {}, {}, []
            for arm in ("T", "C"):
                candidates[arm] = list(parents[arm])
                mutations[arm] = []
                for _ in range(6):
                    parent = int(rngs[arm].integers(2))
                    child, mutation = step(
                        parents[arm][parent], rngs[arm], self.g4, arm
                    )
                    candidates[arm].append(child)
                    mutations[arm].append(dict(parent=parent, **mutation))
                    c = mix[arm][mutation["operator"]]
                    c["proposed"] += 1
                    c["clipped_elements"] += (
                        mutation["clipped_elements"]
                        + mutation["redrawn_clipped_elements"]
                    )
                    c["redraws"] += mutation["redraws"]
                names[arm] = [f"{tid}:{arm}:g{gen}:{i}" for i in range(8)]
                for name, vector in zip(names[arm], candidates[arm]):
                    jobs.extend(
                        self.block(
                            name,
                            table(vector, self.g4),
                            family,
                            self.seed("learning", pi * 10000 + gen * 100),
                            self.n,
                            self.inner_cap,
                            gen,
                        )
                    )
            rs, _ = self.jobs(jobs, f"learn:{tid}:{gen}")
            all_rows.extend(rs)
            for arm in ("T", "C"):
                scores = [
                    float(
                        np.mean(
                            [
                                log_cost(r, self.inner_cap)
                                for r in rs
                                if r["arm"] == name
                            ]
                        )
                    )
                    for name in names[arm]
                ]
                chosen = np.argsort(scores, kind="stable")[:2].tolist()
                for i in chosen:
                    if i >= 2:
                        mix[arm][mutations[arm][i - 2]["operator"]]["survived"] += 1
                self.record(
                    "generations.jsonl",
                    dict(
                        start=tid,
                        arm=arm,
                        generation=gen,
                        candidates=[
                            dict(
                                id=name,
                                vector=v.tolist(),
                                table_hash=Decoder(table(v, self.g4)).hash(),
                            )
                            for name, v in zip(names[arm], candidates[arm])
                        ],
                        scores=scores,
                        selected_indices=chosen,
                        mutations=mutations[arm],
                    ),
                )
                parents[arm] = [candidates[arm][i] for i in chosen]
        jobs = []
        for arm in ("T", "C"):
            for i, v in enumerate(parents[arm]):
                jobs.extend(
                    self.block(
                        f"{tid}:{arm}:final:{i}",
                        table(v, self.g4),
                        family,
                        self.seed("selection", pi * 1000),
                        self.final_n,
                        self.inner_cap,
                    )
                )
        rs, _ = self.jobs(jobs, f"selection:{tid}")
        all_rows.extend(rs)
        for arm in ("T", "C"):
            scores = [
                float(
                    np.mean(
                        [
                            log_cost(r, self.inner_cap)
                            for r in rs
                            if r["arm"] == f"{tid}:{arm}:final:{i}"
                        ]
                    )
                )
                for i in range(2)
            ]
            i = int(np.argmin(scores))
            v = parents[arm][i]
            ts = table(v, self.g4)
            self.finals[f"{tid}:{arm}"] = dict(
                start=tid,
                arm=arm,
                vector=v.tolist(),
                table=ts.tolist(),
                table_hash=Decoder(ts).hash(),
                selection_scores=scores,
                selected_parent=i,
                selected_score=scores[i],
                step_mix=mix[arm],
                diagnostics=diagnostics(v, self.g4, start),
            )
            arm_rows = [r for r in all_rows if f":{arm}:" in r["arm"]]
            self.finals[f"{tid}:{arm}"]["search_costs"] = dict(
                searches=len(arm_rows),
                solves=sum(r["solved"] for r in arm_rows),
                evaluations=sum(r["evaluations"] for r in arm_rows),
                worker_seconds=sum(r["seconds"] for r in arm_rows),
            )
        measured = []
        for arm in ("T", "C"):
            # Compare the same operator/family grain used in Stage A, rather
            # than comparing its family mean with B's single slowest cell.
            subset = [r["seconds"] for r in all_rows if f":{arm}:" in r["arm"]]
            measured.append(float(np.mean(subset)))
        wall = time.monotonic() - tick
        overhead = max(
            1.0, wall * self.effective_workers / sum(r["seconds"] for r in all_rows)
        )
        self.slow_b = max(self.slow_b, max(measured) * overhead)
        self.pair_times.append(wall)
        self.pairs.append(tid)
        write_json(self.out, "trajectories.json", self.finals)
        self.checkpoint("learning")
        print(f"Completed {tid} in {wall:.1f}s; pairs={len(self.pairs)}", flush=True)

    def checkpoint(self, state, **extra):
        write_json(
            self.out,
            "status.json",
            dict(
                state=state,
                pairs=self.pairs,
                elapsed_seconds=time.monotonic() - self.started,
                pair_seconds=self.pair_times,
                slow_a=self.slow_a,
                slow_b=self.slow_b,
                costs=self.costs,
                **extra,
            ),
        )

    def continuation(self):
        target = 1 if self.args.smoke else 8
        for k in range(1, target + 1):
            for family in ("BE", "PA"):
                tid = f"{family}{k}"
                reserve = reservation(
                    self.pairs,
                    tid,
                    self.pair_times,
                    self.slow_a,
                    self.slow_b,
                    self.effective_workers,
                    self.fresh_n,
                    self.config["searches_per_trajectory"],
                )
                remaining = self.deadline - time.monotonic()
                admitted = (
                    sum(
                        reserve[x]
                        for x in ("pair_seconds", "fresh_seconds", "reporting_seconds")
                    )
                    <= remaining
                )
                self.schedule.append(
                    dict(
                        prospective=tid,
                        admitted=admitted,
                        remaining_seconds=remaining,
                        **reserve,
                    )
                )
                write_json(self.out, "admission.json", self.schedule)
                if not admitted:
                    return
                self.evolve_pair(tid, len(self.pairs))

    def fresh_scoring(self):
        maps = {"G4": self.g4}
        for tid in self.pairs:
            maps[tid + ":S"] = np.array(self.starts[tid]["table"])
            for arm in ("T", "C"):
                maps[tid + ":" + arm] = np.array(self.finals[tid + ":" + arm]["table"])
            v = np.array(self.finals[tid + ":C"]["vector"])
            v[49:] = 0
            maps[tid + ":C0"] = table(v, self.g4)
        frozen = {
            name: dict(table=t.tolist(), table_hash=Decoder(t).hash())
            for name, t in maps.items()
        }
        write_json(self.out, "fresh_maps.json", frozen)
        jobs = []
        for name, t in maps.items():
            cells = sum(TRAINING.values(), []) if name == "G4" else TRAINING[name[:2]]
            for cid in cells:
                for j in range(self.fresh_n):
                    jobs.append(
                        self.job(name, t, cid, self.seed("fresh", j), self.fresh_cap)
                    )
        self.fresh, _ = self.jobs(jobs, "fresh")
        write_json(self.out, "fresh_scores.json", self.fresh)

    def probe(self):
        jobs, metadata = [], {}
        for si, tid in enumerate(("BE9", "BE10", "PA9", "PA10")):
            rng = np.random.default_rng(self.seed("mutation", si))
            origin = start_vector(
                self.starts[tid]["vector"],
                np.random.default_rng(self.seed("direction", si)),
            )
            for operator in ("token", "context"):
                v, mutation = step(
                    origin, rng, self.g4, force="token" if operator == "token" else "b"
                )
                name = f"probe:{tid}:{operator}"
                metadata[name] = dict(
                    operator=operator, family=tid[:2], mutation=mutation
                )
                for cap, n in ((65536, 48), (524288, 24)):
                    namecap = name + f":{cap}"
                    metadata[namecap] = metadata[name]
                    jobs.extend(
                        self.block(
                            namecap,
                            table(v, self.g4),
                            tid[:2],
                            self.seed(
                                "calibration",
                                si * 100000
                                + (1000 if operator == "context" else 0)
                                + (500 if cap == 524288 else 0),
                            ),
                            n,
                            cap,
                        )
                    )
        # Separate sufficiently occupied cap batches: a tiny mixed-cap batch
        # confounds steady throughput with process startup and a long idle tail.
        rows, walls = [], {}
        for cap in (65536, 524288):
            rs, wall = self.jobs([j for j in jobs if j[4] == cap], f"probe:{cap}")
            rows.extend(rs)
            walls[str(cap)] = wall
        for row in rows:
            row.update(
                operator=metadata[row["arm"]]["operator"],
                family=metadata[row["arm"]]["family"],
            )
        rates = {
            str(cap): self.timing(
                [r for r in rows if r["cap"] == cap],
                walls[str(cap)],
            )
            for cap in (65536, 524288)
        }
        slow = max(r["reserve_seconds_per_search"] for r in rates["65536"].values())
        result = dict(
            searches=len(rows),
            wall_seconds=sum(walls.values()),
            cap_batch_wall_seconds=walls,
            rates=rates,
            estimated_stage_a_seconds=29184 * slow / self.effective_workers,
            estimated_16_pair_seconds=16 * 8080 * slow / self.effective_workers,
            estimated_12_pair_seconds=12 * 8080 * slow / self.effective_workers,
            namespace_offset=self.offset,
            fixed_probe_never_selects_full_run_parameters=True,
        )
        write_json(self.out, "probe.json", result)
        self.checkpoint("probe_complete")
        print(json.dumps(result, indent=2), flush=True)

    def run(self):
        ctx = mp.get_context("spawn")
        self.pool = ctx.Pool(self.args.workers)
        try:
            if self.args.probe:
                self.probe()
                return
            self.calibration()
            self.continuation()
            self.fresh_scoring()
            from experiments.chem_tape.rank_one_report import make_report, save_report

            result = make_report(
                self.config,
                self.pairs,
                self.fresh,
                self.finals,
                json.loads((self.out / "fresh_maps.json").read_text()),
            )
            result.update(
                calibration=self.calibration_result,
                runtime=self.costs,
                admission=self.schedule,
                elapsed_seconds=time.monotonic() - self.started,
            )
            save_report(self.out, result, self.finals)
            self.checkpoint("complete", outcome=result["outcome"])
        except Exception as exc:
            self.checkpoint("failed", error=f"{type(exc).__name__}: {exc}")
            raise
        finally:
            self.pool.terminate()
            self.pool.join()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workers", type=int, default=10)
    p.add_argument("--deadline-seconds", type=float, default=13680)
    group = p.add_mutually_exclusive_group()
    group.add_argument("--smoke", action="store_true")
    group.add_argument("--probe", action="store_true")
    args = p.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 180:
        p.error("positive worker count and >180 seconds required")
    Runner(args).run()


if __name__ == "__main__":
    main()
