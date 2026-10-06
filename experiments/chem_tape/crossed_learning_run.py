"""1723: independent token learning on frozen BE/PA training cells only."""

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
from scipy.stats import spearmanr

from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import Decoder, search
from experiments.chem_tape.four_reducer_bank import ALPHABET, roster, role_set
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.map_learning import initial, log_cost, mutate, table_for
from experiments.chem_tape.crossed_learning_report import make_report, save_report

TRAINING = {
    "BE": ["BE:F?S:(M+m)", "BE:F?m:(S+M)", "BE:S?F:(M+m)", "BE:S?M:(m+F)"],
    "PA": [
        "PA:(F?S:m)+M",
        "PA:(F?m:M)+S",
        "PA:(F?m:S)+M",
        "PA:(S?M:F)+m",
        "PA:(S?m:F)+M",
        "PA:(S?m:M)+F",
    ],
}
HOLDOUTS = {"BE": ["BE:S?m:(M+F)"], "PA": ["PA:(F?S:M)+m", "PA:(S?M:m)+F"]}
BANK_SHA = "b2b856cb6d051e65599b22409cf49f654ba8d87539f073d2e9b7d061079aceb9"
G4_HASH = "8a7b3091f411e659f553981b8680dc5db4bd5f3f34b6eca9c8ab3ee3e728dc10"
DEFAULT_BANK = Path(__file__).with_name("data") / "four_reducer_1603_bank.json"


def load_bank(path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != BANK_SHA:
        raise ValueError("frozen 1603 bank SHA256 mismatch")
    data = json.loads(raw)
    if data["domain"] != "D1331" or data["smoke_only"]:
        raise ValueError("wrong frozen bank domain or smoke artifact")
    source = {c["id"]: c for c in data["cells"]}
    expected = {c["id"]: c for c in roster("D1331")}
    for ids in (*TRAINING.values(), *HOLDOUTS.values()):
        for cid in ids:
            c = source[cid]
            if not c["retained"] or not c["canonical_verified"]:
                raise ValueError(f"unverified bank cell {cid}")
            if c["labels"] != expected[cid]["labels"]:
                raise ValueError(f"label mismatch {cid}")
    train_ids = sum(TRAINING.values(), [])
    hold_ids = sum(HOLDOUTS.values(), [])
    if set(train_ids) & set(hold_ids):
        raise ValueError("holdout ID leakage")
    for tr in train_ids:
        for ho in hold_ids:
            if source[tr]["labels"] == source[ho]["labels"]:
                raise ValueError("holdout label leakage")
    for family in TRAINING:
        if not role_set([source[c] for c in HOLDOUTS[family]]) <= role_set(
            [source[c] for c in TRAINING[family]]
        ):
            raise ValueError("holdout role not covered")
    # Canonical and screened witness programs never enter a search job.
    cells = {cid: {"id": cid, "labels": source[cid]["labels"]} for cid in train_ids}
    return data, cells


def reservation(pair_seconds, per_search_seconds, maps, workers):
    """Include the prospective pair and G4; selection is in pair_seconds."""
    return dict(
        pair_seconds=1.3 * pair_seconds,
        fresh_seconds=1.3 * (maps + 2 + 1) * 10 * 50 * per_search_seconds / workers,
        reporting_seconds=180,
    )


def early_stop(trajectories):
    return len(trajectories) == 4 and all(
        t["selection_gain_log2"] < np.log2(1.1) for t in trajectories.values()
    )


class Runner:
    def __init__(self, args):
        self.args = args
        os.environ["RAYON_NUM_THREADS"] = "1"
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("Use a fresh RUN_DIR")
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds
        self.work_deadline = self.deadline - 180
        bank, self.cells = load_bank(args.bank)
        self.controls = {"G": tables()["G4"]}
        if Decoder(self.controls["G"]).hash() != G4_HASH:
            raise ValueError("G4 hash mismatch")
        self.inputs = inputs_for("D1331")
        self.pool = None
        self.trajectories = {}
        self.fresh = []
        self.schedule = []
        self.pair_times = []
        self.costs = {}
        self.gate_stopped = False
        self.stop_reason = None
        self.inner_cap = 4096 if args.smoke else 65536
        self.final_cap = 8192 if args.smoke else 524288
        self.generations = 1 if args.smoke else 25
        self.selection_n = 12 if args.smoke else 120
        self.fresh_n = 2 if args.smoke else 50
        self.target = 2 if args.smoke else 10
        self.config = dict(
            task="2026-10-06-1723",
            arguments=vars(args),
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            bank_sha256=BANK_SHA,
            bank_source="experiments/output/2026-10-06/2026-10-06-1603-four-reducer-family/bank.json",
            g4_hash=G4_HASH,
            alphabet=ALPHABET,
            domain="D1331",
            training=TRAINING,
            excluded_holdouts=HOLDOUTS,
            population=256,
            length=32,
            allele_range=24000,
            training_cases=64,
            crossover=0.7,
            mutation=0.03,
            outer_mu=4,
            outer_lambda=12,
            dimensions=24,
            multiplier_bounds=[1 / 16, 16],
            minimum_count=250,
            mutation_coordinates=3,
            mutation_sigma=0.5,
            objective="mean log2 evaluations; unsolved=2*inner_cap",
            inner_searches=24,
            inner_cap=self.inner_cap,
            generations=self.generations,
            selection_searches_per_candidate=self.selection_n,
            fresh_cap=self.final_cap,
            fresh_seeds=list(range(1723300, 1723300 + self.fresh_n)),
            trajectories_per_family=self.target,
            workers=args.workers,
            outer_seeds={
                f: [1723200 + 2 * k + (f == "PA") for k in range(self.target)]
                for f in TRAINING
            },
            selection_seed_rule="outer_seed*10000+5000+j",
            inner_seed_rule="outer_seed*10000+generation*100+j",
            permutation_seed=1723500,
            smoke_only=args.smoke,
            probe_only=args.probe,
        )
        write_json(self.out, "config.json", self.config)
        write_json(self.out, "bank.json", bank)
        write_json(
            self.out,
            "validation.json",
            dict(
                passed=True,
                frozen_hash_verified=True,
                labels_verified=True,
                training_holdout_labels_disjoint=True,
                holdout_roles_covered=True,
                search_payload_fields=["id", "labels"],
                g4_hash=G4_HASH,
            ),
        )

    def job(self, cid, arm, table, seed, cap):
        if cid not in self.cells:
            raise ValueError(f"non-training job rejected: {cid}")
        return self.cells[cid], arm, table, int(seed), cap, 256, self.inputs, ALPHABET

    def jobs(self, jobs, phase):
        for job in jobs:
            if job[0]["id"] not in self.cells or set(job[0]) != {"id", "labels"}:
                raise ValueError("holdout/solver search payload rejected")
        rows = []

        def save(row):
            row["phase"] = phase
            rows.append(row)
            with (self.out / "search.jsonl").open("a") as f:
                f.write(json.dumps(row, allow_nan=False) + "\n")
            # Solves stop at the same budget; capped runs reserve a full-cap
            # extrapolation. Aggregate within cell, then weight all cells equally.
            projected = row["seconds"] * (
                1 if row["solved"] else self.final_cap / row["cap"]
            )
            values = self.costs.setdefault(row["cell"], [0.0, 0])
            values[0] += projected
            values[1] += 1

        if not run_jobs(self.pool, search, jobs, self.work_deadline, save):
            raise TimeoutError("search deadline; partial rows preserved")
        return rows

    def evolve(self, family, k):
        tid = f"{family}{k + 1}"
        seed = 1723200 + 2 * k + (family == "PA")
        rng = np.random.default_rng(seed)
        start = initial("M", self.controls)
        parents = [start.copy() for _ in range(4)]
        train = TRAINING[family]
        tick = time.monotonic()
        evaluations = 0
        initial_scores = None
        previous = None
        ranks = []
        for gen in range(self.generations + 1):
            vectors = list(parents)
            mutations = []
            if gen:
                for _ in range(12):
                    p = int(rng.integers(4))
                    child, record = mutate(parents[p], start, rng)
                    vectors.append(child)
                    mutations.append(dict(parent=p, **record))
            names = [f"{tid}:generation:{gen}:{i}" for i in range(len(vectors))]
            ts = [table_for("M", v, self.controls) for v in vectors]
            rows = self.jobs(
                [
                    self.job(
                        train[(j + gen) % len(train)],
                        name,
                        t,
                        seed * 10000 + gen * 100 + j,
                        self.inner_cap,
                    )
                    for name, t in zip(names, ts)
                    for j in range(24)
                ],
                f"learn:{tid}:{gen}",
            )
            scores = [
                float(
                    np.mean(
                        [log_cost(r, self.inner_cap) for r in rows if r["arm"] == name]
                    )
                )
                for name in names
            ]
            evaluations += sum(r["evaluations"] for r in rows)
            rank = None
            if (
                previous is not None
                and min(len(set(previous)), len(set(scores[:4]))) >= 2
            ):
                rank = float(spearmanr(previous, scores[:4]).statistic)
            if gen:
                ranks.append(rank)
            else:
                initial_scores = scores
            chosen = np.argsort(scores, kind="stable")[:4].tolist()
            record = dict(
                trajectory=tid,
                family=family,
                seed=int(seed),
                generation=gen,
                candidates=[
                    dict(
                        id=n,
                        vector=v.tolist(),
                        table=t.tolist(),
                        hash=Decoder(t).hash(),
                    )
                    for n, v, t in zip(names, vectors, ts)
                ],
                scores=scores,
                selected_indices=chosen,
                mutations=mutations,
                previous_selected_parent_scores=previous,
                rescored_parent_scores=scores[:4],
                within_generation_spearman=rank,
                rank_undefined_reason="initial generation or fewer than two distinct scores"
                if rank is None
                else None,
            )
            with (self.out / "generations.jsonl").open("a") as f:
                f.write(json.dumps(record, allow_nan=False) + "\n")
            parents = [vectors[i] for i in chosen]
            previous = [scores[i] for i in chosen]
        names = [f"{tid}:selection:{i}" for i in range(4)] + [f"{tid}:selection:G4"]
        ts = [table_for("M", v, self.controls) for v in parents] + [self.controls["G"]]
        rows = self.jobs(
            [
                self.job(
                    train[j % len(train)],
                    name,
                    t,
                    seed * 10000 + 5000 + j,
                    self.inner_cap,
                )
                for name, t in zip(names, ts)
                for j in range(self.selection_n)
            ],
            f"selection:{tid}",
        )
        scores = [
            float(
                np.mean([log_cost(r, self.inner_cap) for r in rows if r["arm"] == name])
            )
            for name in names
        ]
        best = int(np.argmin(scores[:4]))
        self.trajectories[tid] = dict(
            trajectory=tid,
            family=family,
            seed=int(seed),
            vector=parents[best].tolist(),
            table=ts[best].tolist(),
            table_hash=Decoder(ts[best]).hash(),
            initial_scores=initial_scores,
            final_in_loop_scores=previous,
            selection_scores=scores[:4],
            selection_g4_score=scores[4],
            selection_gain_log2=scores[4] - scores[best],
            selected_parent=best,
            final_in_loop_selected_score=previous[best],
            seconds=time.monotonic() - tick,
            evaluations=evaluations + sum(r["evaluations"] for r in rows),
            within_generation_spearman=ranks,
        )
        write_json(self.out, "trajectories.json", self.trajectories)

    def admit(self):
        seconds = max(self.pair_times, default=31 * 60 * 10 / self.args.workers)
        # G4 calibration is a floor; candidate/cell timings update the reserve.
        rate = (
            max(1.88, float(np.mean([total / n for total, n in self.costs.values()])))
            if self.costs
            else 1.88
        )
        r = reservation(seconds, rate, len(self.trajectories), self.args.workers)
        if self.args.smoke:
            r = dict(
                pair_seconds=seconds if self.pair_times else 60,
                fresh_seconds=60,
                reporting_seconds=180,
            )
        remaining = self.deadline - time.monotonic()
        allowed = sum(r.values()) <= remaining
        self.schedule.append(
            dict(
                completed_pairs=len(self.pair_times),
                remaining_seconds=remaining,
                fresh_per_search_seconds=rate,
                reserve=r,
                admitted=allowed,
            )
        )
        write_json(self.out, "schedule.json", self.schedule)
        return allowed

    def probe(self):
        start = initial("M", self.controls)
        rng = np.random.default_rng(1723600)
        vector, mutation = mutate(start, start, rng)
        ts = {
            "G4": self.controls["G"],
            "perturbation": table_for("M", vector, self.controls),
        }
        tick = time.monotonic()
        rows = self.jobs(
            [
                self.job(cid, arm, t, seed, 65536)
                for arm, t in ts.items()
                for cid in self.cells
                for seed in range(1723601, 1723601 + self.args.probe_seeds)
            ],
            "probe",
        )
        wall = time.monotonic() - tick
        result = dict(
            smoke_only=True,
            wall_seconds=wall,
            mutation=mutation,
            perturbation_vector=vector.tolist(),
            rows=len(rows),
            cells={},
        )
        for family, ids in TRAINING.items():
            for arm in ts:
                rs = [r for r in rows if r["arm"] == arm and r["cell"] in ids]
                result["cells"][f"{family}:{arm}"] = dict(
                    searches=len(rs),
                    mean_seconds=float(np.mean([r["seconds"] for r in rs])),
                    solve_fraction=float(np.mean([r["solved"] for r in rs])),
                    evaluations=sum(r["evaluations"] for r in rs),
                )
        write_json(self.out, "probe.json", result)

    def run(self):
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        try:
            if self.args.probe:
                self.probe()
                return
            for k in range(self.target):
                if not self.admit():
                    self.stop_reason = "runtime reservation refused next balanced pair"
                    break
                tick = time.monotonic()
                for family in TRAINING:
                    self.evolve(family, k)
                self.pair_times.append(time.monotonic() - tick)
                if k == 1 and early_stop(self.trajectories):
                    self.gate_stopped = True
                    self.stop_reason = (
                        "early low-yield stop; learning remains unresolved"
                    )
                    break
            maps = {
                "G4": self.controls["G"],
                **{tid: np.asarray(t["table"]) for tid, t in self.trajectories.items()},
            }
            # Score one map per block so partially completed raw rows survive.
            for arm, table in maps.items():
                self.fresh.extend(
                    self.jobs(
                        [
                            self.job(cid, arm, table, seed, self.final_cap)
                            for cid in self.cells
                            for seed in self.config["fresh_seeds"]
                        ],
                        "fresh_training",
                    )
                )
                write_json(self.out, "fresh_scores.json", self.fresh)
        except TimeoutError as e:
            self.stop_reason = str(e)
        finally:
            self.pool.terminate()
            self.pool.join()
        report = make_report(
            self.fresh, self.trajectories, self.config, self.gate_stopped
        )
        report.update(
            stop_reason=self.stop_reason,
            wall_seconds=time.monotonic() - self.started,
            pair_seconds=self.pair_times,
            schedule=self.schedule,
        )
        write_json(self.out, "result.json", report)
        save_report(self.out, report, self.trajectories, self.fresh)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bank", type=str, default=str(DEFAULT_BANK))
    p.add_argument("--workers", type=int, default=10)
    p.add_argument("--deadline-seconds", type=int, default=27000)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--probe", action="store_true")
    p.add_argument("--probe-seeds", type=int, default=5)
    args = p.parse_args()
    if (
        args.workers < 1
        or args.probe_seeds < 1
        or args.deadline_seconds <= 180
        or (args.smoke and args.probe)
    ):
        p.error("invalid workers/deadline or mutually exclusive smoke/probe")
    Runner(args).run()


if __name__ == "__main__":
    main()
