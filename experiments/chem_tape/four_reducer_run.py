"""Approved 1603 staged screen/calibration/pilot; only writes RUN_DIR."""

import argparse
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np
from scipy.stats import spearmanr
from experiments.chem_tape.assembly_bank import DOMAINS, inputs_for
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder, search
from experiments.chem_tape.four_reducer_bank import (
    ALPHABET,
    roster,
    screen_job,
    validate,
)
from experiments.chem_tape.four_reducer_maps import ARMS, R, tables
from experiments.chem_tape.four_reducer_report import (
    contrast,
    gates,
    plots,
    report,
    summaries,
)
from experiments.chem_tape.map_learning import initial, log_cost, mutate, table_for


def projection(rows, bank, splits, workers, block_wall=None, b_remaining=0):
    g4 = [r for r in rows if r["arm"] == "G4"]
    # Full-run checkpoint timings have the actual 65k passage (or earlier
    # exact solve); no solve-rate substitution or omission of capped searches.
    inner = max([r["budget_seconds"].get("65536", r["seconds"]) for r in g4], default=0)
    # Use per-cell mean at the inner cap, worst training cell, plus 2x map
    # slowdown. This is more conservative than a pooled successful-run rate.
    inner = max(
        [
            np.mean(
                [
                    r["budget_seconds"].get("65536", r["seconds"])
                    for r in g4
                    if r["cell"] == c["id"]
                ]
            )
            for c in bank
        ],
        default=inner,
    )
    final = max(
        [np.mean([r["seconds"] for r in g4 if r["cell"] == c["id"]]) for c in bank],
        default=0,
    )
    known = all(splits.values())
    train_n = (
        sum(len(s["training"]) for s in splits.values())
        if known
        else max(0, len(bank) - 4)
    )
    hold_n = 4
    inner_count = 4 * (4 + 25 * 16) * 24
    # 0132 selects its final parent on 20 fresh seeds per training cell.
    selection_count = 2 * train_n * 4 * 20
    final_count = 5 * (train_n * 50 + hold_n * 100)
    pilot = (
        1.25
        * (2 * inner * (inner_count + selection_count) + 2 * final * final_count)
        / workers
        + 180
    )
    per_job_wall = block_wall / len(rows) if block_wall is not None and rows else None
    return dict(
        inner_searches=inner_count,
        final_parent_selection_searches=selection_count,
        final_scoring_searches=final_count,
        g4_inner_mean_seconds_worst_cell=float(inner),
        g4_final_mean_seconds_worst_cell=float(final),
        candidate_slowdown_allowance=2,
        worker_overhead_factor=1.25,
        workers=workers,
        projected_c_seconds=float(pilot),
        c_conditional_on_splits=not known,
        projected_b_remaining_seconds=b_remaining * per_job_wall
        if per_job_wall
        else None,
    )


class Runner:
    def __init__(self, args):
        self.args = args
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("Use a fresh RUN_DIR; refusing to mix experiments")
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 180
        self.tables = tables()
        self.inputs = inputs_for("D1331")
        self.ctx = mp.get_context("spawn")
        self.pool = None
        self.rows = []
        self.test_rows = []
        self.screens = {}
        self.bank = []
        self.splits = {}
        self.pilot = {}
        self.blocks = []
        self.cost = {}
        self.c_started = False
        self.c_complete = False
        self.c_cost_blocked = False
        write_json(
            self.out,
            "config.json",
            dict(
                task="2026-10-06-1603",
                arguments=vars(args),
                git_commit=subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], text=True
                ).strip(),
                alphabet=ALPHABET,
                allele_range=R,
                length=32,
                population=256,
                training_cases=64,
                crossover=0.7,
                mutation=0.03,
                pilot_parameters=dict(
                    trajectories_per_family=2,
                    outer_mu=4,
                    outer_lambda=12,
                    generations=25,
                    dimensions=24,
                    inner_searches_per_candidate=24,
                    inner_cap=65536,
                    multiplier_bounds=[1 / 16, 16],
                    mutation_coordinates=3,
                    mutation_sigma=0.5,
                    minimum_token_count=250,
                    objective="mean log2 evaluations; unsolved assigned 2*inner_cap",
                    final_parent_selection_seeds_per_training_cell=20,
                    normalization="proportional lower-bound water filling; stable largest remainder",
                ),
                seed_blocks=dict(
                    validation=1603001,
                    bootstrap=1603002,
                    calibration=[1603100, 1603149],
                    learning=[1603200, 1603203],
                    fresh_training=[1603300, 1603349],
                    fresh_holdout=[1603400, 1603499],
                ),
            ),
        )
        write_json(
            self.out,
            "maps.json",
            dict(
                tables={a: t.tolist() for a, t in self.tables.items()},
                hashes={a: Decoder(t).hash() for a, t in self.tables.items()},
                marginal_method="Exact expected token counts over 32 iid uniform-allele positions; "
                "start row included; stable largest remainder to 24000 alleles",
                frozen_before_screen=True,
            ),
        )
        write_json(self.out, "roster.json", {d: roster(d) for d in DOMAINS})

    def jobs(self, jobs, phase):
        rows = []

        def save(row):
            row["phase"] = phase
            rows.append(row)
            with (self.out / "search.jsonl").open("a") as f:
                f.write(json.dumps(row, allow_nan=False) + "\n")

        if not run_jobs(self.pool, search, jobs, self.deadline, save):
            raise TimeoutError("search deadline; partial raw rows preserved")
        return sorted(rows, key=lambda r: (r["arm"], r["cell"], r["seed"]))

    def job(self, c, a, t, s, cap):
        return (c, a, t, s, cap, 256, self.inputs, ALPHABET)

    def evolve(self, family, k):
        tid = f"{family}{k + 1}"
        controls = {"G": self.tables["G4"], "G-marg": self.tables["G4-marg"]}
        start = initial("M", controls)
        seed = 1603200 + (0 if family == "BE" else 2) + k
        rng = np.random.default_rng(seed)
        train = [c for c in self.bank if c["id"] in self.splits[family]["training"]]
        parents = [start.copy() for _ in range(4)]
        previous_scores = None
        ranks = []
        all_evals = 0
        tick = time.monotonic()
        generations = 1 if self.args.smoke else 25
        inner_cap = min(self.args.cap, 65536)

        def score(vectors, gen, phase):
            names = [f"{tid}:{phase}:{gen}:{i}" for i in range(len(vectors))]
            ts = [table_for("M", v, controls) for v in vectors]
            base = seed * 10000 + gen * 100
            assignments = [(train[(j + gen) % len(train)], base + j) for j in range(24)]
            rows = self.jobs(
                [
                    self.job(c, a, t, s, inner_cap)
                    for a, t in zip(names, ts)
                    for c, s in assignments
                ],
                f"learn:{tid}:{phase}:{gen}",
            )
            values = [
                float(np.mean([log_cost(r, inner_cap) for r in rows if r["arm"] == a]))
                for a in names
            ]
            return values, rows, names, ts

        previous_scores, init_rows, _, _ = score(parents, 0, "initial")
        all_evals += sum(r["evaluations"] for r in init_rows)
        for gen in range(1, generations + 1):
            vectors = list(parents)
            mutations = []
            for _ in range(12):
                parent = int(rng.integers(4))
                child, record = mutate(parents[parent], start, rng)
                vectors.append(child)
                mutations.append(dict(parent=parent, **record))
            scores, rows, names, ts = score(vectors, gen, "generation")
            distinct = min(len(set(previous_scores)), len(set(scores[:4])))
            rank = (
                float(spearmanr(previous_scores, scores[:4]).statistic)
                if distinct >= 2
                else None
            )
            ranks.append(rank)
            chosen = np.argsort(scores, kind="stable")[:4].tolist()
            all_evals += sum(r["evaluations"] for r in rows)
            record = dict(
                trajectory=tid,
                family=family,
                generation=gen,
                seed=seed,
                candidates=[
                    dict(
                        id=a,
                        vector=v.tolist(),
                        table=t.tolist(),
                        hash=Decoder(t).hash(),
                    )
                    for a, v, t in zip(names, vectors, ts)
                ],
                scores=scores,
                selected_indices=chosen,
                mutations=mutations,
                previous_selected_parent_scores=previous_scores,
                rescored_parent_scores=scores[:4],
                within_generation_spearman=rank,
                rank_undefined_reason="fewer than two distinct scores"
                if rank is None
                else None,
            )
            with (self.out / "generations.jsonl").open("a") as f:
                f.write(json.dumps(record, allow_nan=False) + "\n")
            parents = [vectors[i] for i in chosen]
            previous_scores = [scores[i] for i in chosen]
        # Final parent selection is fresh training data, never holdout scores.
        names = [f"{tid}:selection:{i}" for i in range(4)]
        ts = [table_for("M", v, controls) for v in parents]
        n = 2 if self.args.smoke else 20
        rows = self.jobs(
            [
                self.job(c, a, t, seed * 10000 + 5000 + j, inner_cap)
                for a, t in zip(names, ts)
                for c in train
                for j in range(n)
            ],
            f"selection:{tid}",
        )
        scores = [
            float(np.mean([log_cost(r, inner_cap) for r in rows if r["arm"] == a]))
            for a in names
        ]
        best = int(np.argmin(scores))
        all_evals += sum(r["evaluations"] for r in rows)
        record = dict(
            family=family,
            trajectory=tid,
            seed=seed,
            table=ts[best].tolist(),
            vector=parents[best].tolist(),
            table_hash=Decoder(ts[best]).hash(),
            selection_scores=scores,
            seconds=time.monotonic() - tick,
            evaluations=all_evals,
            within_generation_spearman=ranks,
            median_spearman=float(np.median([r for r in ranks if r is not None]))
            if any(r is not None for r in ranks)
            else None,
        )
        self.pilot[tid] = record
        write_json(self.out, "pilot.json", self.pilot)
        return ts[best]

    def run(self):
        b_complete = False
        validation = {}
        try:
            validation = validate(
                1000 if self.args.smoke else 100000, 2 if self.args.smoke else 4
            )
            write_json(self.out, "validation.json", validation)
            for domain in DOMAINS:
                self.pool = self.ctx.Pool(1)
                try:

                    def save_screen(row):
                        self.screens[domain] = row
                        write_json(self.out, "stage_a.json", self.screens)

                    if not run_jobs(
                        self.pool,
                        screen_job,
                        [(domain, self.args.screen_depth, self.deadline)],
                        self.deadline,
                        save_screen,
                    ):
                        raise TimeoutError("screen deadline")
                finally:
                    self.pool.terminate()
                    self.pool.join()
                    self.pool = None
            self.bank = [c for c in self.screens["D1331"]["cells"] if c["retained"]]
            self.splits = {
                f: self.screens["D1331"]["obstacles"][f]["split"] for f in ("BE", "PA")
            }
            if self.args.smoke:
                # Explicitly smoke only: exercise both families at a bounded size.
                self.bank = [
                    next(c for c in roster("D1331") if c["shape"] == f)
                    for f in ("BE", "PA")
                ]
            write_json(
                self.out,
                "bank.json",
                dict(
                    domain="D1331",
                    cells=self.bank,
                    splits=self.splits,
                    smoke_only=self.args.smoke,
                ),
            )
            self.pool = self.ctx.Pool(self.args.workers)
            for offset in range(0, self.args.seeds, 10):
                jobs = [
                    self.job(c, a, self.tables[a], 1603100 + j, self.args.cap)
                    for j in range(offset, min(offset + 10, self.args.seeds))
                    for c in self.bank
                    for a in ARMS
                ]
                tick = time.monotonic()
                rs = self.jobs(jobs, "calibration")
                self.rows.extend(rs)
                wall = time.monotonic() - tick
                remaining = (
                    (self.args.seeds - min(offset + 10, self.args.seeds))
                    * len(self.bank)
                    * len(ARMS)
                )
                cost = projection(
                    rs, self.bank, self.splits, self.args.workers, wall, remaining
                )
                block = dict(
                    offset=offset,
                    completed=len(rs),
                    requested=len(jobs),
                    wall_seconds=wall,
                    mean_seconds=float(np.mean([r["seconds"] for r in rs]))
                    if rs
                    else None,
                    solves=summaries(rs),
                    projection=cost,
                    projected_total_seconds=time.monotonic()
                    - self.started
                    + (cost["projected_b_remaining_seconds"] or 0)
                    + cost["projected_c_seconds"],
                )
                self.blocks.append(block)
                write_json(self.out, "blocks.json", self.blocks)
                if offset == 0:
                    self.c_cost_blocked = (
                        block["projected_total_seconds"]
                        > self.args.deadline_seconds - 180
                    )
                    block["c_skipped_if_projection_overruns"] = self.c_cost_blocked
                    write_json(self.out, "checkpoint_b1.json", block)
                print("balanced block", offset, "wall", round(wall, 2), flush=True)
            b_complete = True
            gs = (
                dict(split=False, headroom=None, tractability=None)
                if self.args.smoke
                else gates(self.bank, self.splits, summaries(self.rows))
            )
            self.cost = projection(self.rows, self.bank, self.splits, self.args.workers)
            self.cost["remaining_work_seconds"] = self.deadline - time.monotonic()
            self.cost["first_block_cost_blocked"] = self.c_cost_blocked
            self.cost["fits"] = (
                not self.c_cost_blocked
                and self.cost["projected_c_seconds"]
                <= self.cost["remaining_work_seconds"]
            )
            write_json(self.out, "gates.json", dict(**gs, cost=self.cost))
            if (
                not self.args.smoke
                and all(gs.get(g) for g in ("split", "headroom", "tractability"))
                and self.cost["fits"]
            ):
                self.c_started = True
                learned = {
                    f"{f}{k + 1}": self.evolve(f, k)
                    for f in ("BE", "PA")
                    for k in range(2)
                }
                for a, t in {"G4": self.tables["G4"], **learned}.items():
                    for f in ("BE", "PA"):
                        for kind, n, base in (
                            ("training", 50, 1603300),
                            ("holdouts", 100, 1603400),
                        ):
                            cells = [
                                c for c in self.bank if c["id"] in self.splits[f][kind]
                            ]
                            self.test_rows.extend(
                                self.jobs(
                                    [
                                        self.job(c, a, t, base + j, self.args.cap)
                                        for c in cells
                                        for j in range(n)
                                    ],
                                    f"test:{f}:{kind}",
                                )
                            )
                for tid, p in self.pilot.items():
                    train = self.splits[p["family"]]["training"]
                    p["gain"] = contrast(self.test_rows, train, {"G4": 1, tid: -1})
                    p["holdout_scores"] = {
                        f: {
                            kind: contrast(self.test_rows, s[kind], {"G4": 1, tid: -1})
                            for kind in ("training", "holdouts")
                        }
                        for f, s in self.splits.items()
                    }
                self.c_complete = True
                write_json(self.out, "pilot.json", self.pilot)
        except (TimeoutError, AssertionError) as exc:
            write_json(
                self.out,
                "interruption.json",
                dict(reason=str(exc), phase="C" if self.c_started else "A/B"),
            )
            if isinstance(exc, AssertionError):
                validation.update(complete=False, passed=False, failure=str(exc))
                write_json(self.out, "validation.json", validation)
            # Partial completed observations survive even if a block is cut off.
            if (self.out / "search.jsonl").exists():
                raw = [
                    json.loads(line)
                    for line in (self.out / "search.jsonl").read_text().splitlines()
                ]
                self.rows = [r for r in raw if r["phase"] == "calibration"]
                self.test_rows = [r for r in raw if r["phase"].startswith("test:")]
        finally:
            if self.pool:
                self.pool.terminate()
                self.pool.join()
        write_json(self.out, "calibration.json", self.rows)
        write_json(self.out, "fresh_scores.json", self.test_rows)
        result = report(
            self.screens,
            self.bank,
            self.rows,
            b_complete and not self.args.smoke,
            self.c_started,
            self.c_complete,
            self.pilot,
            self.cost,
        )
        if not validation.get("complete") or self.args.smoke:
            result["outcome"] = "smoke_only" if self.args.smoke else "U"
        result.update(
            fresh_per_cell_arm=summaries(self.test_rows),
            wall_seconds=time.monotonic() - self.started,
            b_complete=b_complete,
            c_started=self.c_started,
            c_complete=self.c_complete,
            smoke_only=self.args.smoke,
        )
        write_json(self.out, "summary.json", result)
        plots(self.out, self.bank, result)
        (self.out / "summary.md").write_text(
            f"Outcome: {result['outcome']}\n\n"
            + result["interpretation"]
            + "\n\nSee summary.json for cell/arm medians (unobserved medians "
            "are bounds beyond cap), paired ratios and pilot costs; stage_a.json for role coverage "
            "and Rust-checked alias witnesses. No transfer-specificity test was performed.\n"
        )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=10)
    p.add_argument("--deadline-seconds", type=int, default=12600)
    p.add_argument("--seeds", type=int, default=50)
    p.add_argument("--cap", type=int, default=524288)
    p.add_argument("--screen-depth", type=int, default=9)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    if (
        args.deadline_seconds <= 180
        or args.workers < 1
        or args.seeds < 1
        or args.cap < 256
        or args.cap % 256
        or not 1 <= args.screen_depth <= 9
    ):
        p.error("invalid population-aligned cap, depth, seeds or workers")
    if not args.smoke and (
        args.cap != 524288 or args.seeds != 50 or args.screen_depth != 9
    ):
        p.error("full run requires approved cap 524288, 50 seeds, depth 9")
    Runner(args).run()


if __name__ == "__main__":
    main()
