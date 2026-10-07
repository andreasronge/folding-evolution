"""1137 token continuation, fixed F1 gate, and paired context on independent F2.

Reuse 0821's search payload checks, production engine, operators and pinned starts.
All generated artifacts are written beneath RUN_DIR.
"""

import argparse
from datetime import datetime
import json
import multiprocessing as mp
import time
from zoneinfo import ZoneInfo

import numpy as np

from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.continuation96_report import (
    F1_SEEDS,
    REFERENCE_SHA,
    ROSTER,
    baseline_check,
    contrasts,
    gate,
    load_reference,
    outcome,
    selected_diagnostic,
    validate_rows,
)
from experiments.chem_tape.crossed_learning_run import TRAINING
from experiments.chem_tape.map_learning import log_cost
from experiments.chem_tape.rank_one_learning import (
    diagnostics,
    start_vector,
    step,
    table,
)
from experiments.chem_tape.rank_one_run import Runner

SEEDS = dict(
    learning=1_861_000_000,
    selection=1_862_000_000,
    fresh=1_824_000_000,
    f2=1_863_000_000,
    mutation=1_864_000_000,
    direction=1_865_000_000,
    calibration=1_866_000_000,
)


def internal_seconds(seconds, now=None):
    now = now or datetime.now(ZoneInfo("Europe/Stockholm"))
    close = now.replace(hour=22, minute=0, second=0, microsecond=0)
    return min(seconds, 5.5 * 3600, (close - now).total_seconds())


def reserve(
    starts, admitted, prospective, trajectory_times, fresh_rate, workers, fresh_n=50
):
    context = [*admitted, *([prospective] if prospective else [])]
    # S/T on ALL token starts, C/C0 on admitted + prospective starts, G4 always.
    searches = fresh_n * (
        10
        + 2 * sum(len(TRAINING[t[:2]]) for t in starts)
        + 2 * sum(len(TRAINING[t[:2]]) for t in context)
    )
    return dict(
        trajectory_seconds=1.3 * max(trajectory_times) if prospective else 0,
        fresh_searches=searches,
        fresh_seconds=1.3 * searches * fresh_rate / workers,
        reporting_seconds=180,
    )


class ContinuationRunner(Runner):
    def __init__(self, args):
        super().__init__(args)
        self.reference = load_reference()
        if any(
            self.reference["config"][key] != self.config[key]
            for key in (
                "bank_sha256",
                "source_hashes",
                "g4_hash",
                "alphabet",
                "domain",
                "population",
                "length",
                "allele_range",
                "training_cases",
                "crossover",
                "mutation",
            )
        ):
            raise ValueError("0821 reference disagrees with pinned search setup")
        self.roster = ROSTER[:2] if args.smoke else ROSTER.copy()
        seconds = (
            args.deadline_seconds
            if args.smoke or args.probe
            else internal_seconds(args.deadline_seconds)
        )
        if seconds <= 180:
            raise ValueError("internal local deadline has passed")
        self.deadline = self.started + seconds
        self.work_deadline = self.deadline - 180
        self.n = 12 if args.smoke else 96
        self.generations = 6 if args.smoke else 12
        self.final_n = 12 if args.smoke else 192
        self.midpoints, self.token_times, self.context_starts = {}, [], []
        self.fresh_rate = 0.867
        self.config.update(
            task="2026-10-07-1137",
            seeds=SEEDS,
            roster=self.roster,
            reference_sha256=REFERENCE_SHA,
            historical_source_sha256=self.reference["source_files_sha256"],
            scoring_effort=self.n,
            generations=self.generations,
            searches_per_trajectory=8 * self.n * self.generations + 2 * self.final_n,
            final_searches_per_parent=self.final_n,
            midpoint_generation=self.generations // 2,
            fresh_seeds=[self.seed("fresh", j) for j in range(self.fresh_n)],
            f2_seeds=[self.seed("f2", j) for j in range(self.fresh_n)],
            internal_deadline_seconds=seconds,
            timezone="Europe/Stockholm",
            gate_ratio=1.10,
            no_calibration=True,
            selected_change_scope="actual child/source-parent pairs both retained; no additional searches",
            seed_offset=self.offset,
            selection_seed_rule="base+start_index*1000+j",
            learning_seed_rule="base+start_index*10000+generation*100+j",
            calibration_stops_learning=None,
        )
        self.config.pop("calibration_seed_rule", None)
        write_json(self.out, "config.json", self.config)
        validation = json.loads((self.out / "validation.json").read_text())
        validation.pop("no_historical_scores_loaded", None)
        validation.update(
            historical_reference_pinned=True,
            historical_scores_used_for_selection=False,
            reference_sha256=REFERENCE_SHA,
        )
        write_json(self.out, "validation.json", validation)
        write_json(self.out, "admission.json", [])
        (self.out / "selected_changes.jsonl").touch()

    def seed(self, phase, delta=0):
        return SEEDS[phase] + self.offset + delta

    def evolve_arm(self, tid, arm):
        tick = time.monotonic()
        pi, ai = ROSTER.index(tid), int(arm == "C")
        origin = start_vector(
            self.starts[tid]["vector"],
            np.random.default_rng(self.seed("direction", pi * 10 + ai)),
        )
        if not np.array_equal(table(origin, self.g4), self.starts[tid]["table"]):
            raise ValueError("zero residual changed saved start")
        parents = [origin.copy(), origin.copy()]
        rng = np.random.default_rng(self.seed("mutation", pi * 10 + ai))
        mix = {
            op: dict(proposed=0, survived=0, clipped_elements=0, redraws=0)
            for op in ("token", "b", "a")
        }
        costs = dict(searches=0, solves=0, evaluations=0, worker_seconds=0.0)
        previous = None

        def account(rows):
            costs["searches"] += len(rows)
            costs["solves"] += sum(r["solved"] for r in rows)
            costs["evaluations"] += sum(r["evaluations"] for r in rows)
            costs["worker_seconds"] += sum(r["seconds"] for r in rows)

        def score(rows, names):
            grouped = {name: [] for name in names}
            for r in rows:
                grouped[r["arm"]].append(log_cost(r, self.inner_cap))
            return [float(np.mean(grouped[name])) for name in names]

        for gen in range(self.generations):
            candidates, mutations = list(parents), []
            for _ in range(6):
                parent = int(rng.integers(2))
                child, mutation = step(parents[parent], rng, self.g4, arm)
                candidates.append(child)
                mutations.append(dict(parent=parent, **mutation))
                m = mix[mutation["operator"]]
                m["proposed"] += 1
                m["clipped_elements"] += (
                    mutation["clipped_elements"] + mutation["redrawn_clipped_elements"]
                )
                m["redraws"] += mutation["redraws"]
            names = [f"{tid}:{arm}:g{gen}:{i}" for i in range(8)]
            tables = [table(v, self.g4) for v in candidates]
            jobs = [
                j
                for name, ts in zip(names, tables)
                for j in self.block(
                    name,
                    ts,
                    tid[:2],
                    self.seed("learning", pi * 10000 + gen * 100),
                    self.n,
                    self.inner_cap,
                    gen,
                )
            ]
            rows, _ = self.jobs(jobs, f"learn:{arm}:{tid}:{gen}")
            account(rows)
            scores = score(rows, names)
            chosen = np.argsort(scores, kind="stable")[:2].tolist()
            if previous is not None:
                diagnostic = selected_diagnostic(previous, scores[:2])
                self.record(
                    "selected_changes.jsonl",
                    dict(
                        start=tid,
                        arm=arm,
                        acceptance_generation=gen - 1,
                        rescore_generation=gen,
                        **diagnostic,
                    ),
                )
            for i in chosen:
                if i >= 2:
                    mix[mutations[i - 2]["operator"]]["survived"] += 1
            previous = dict(
                start=tid,
                arm=arm,
                generation=gen,
                candidates=[
                    dict(id=name, vector=v.tolist(), table_hash=Decoder(ts).hash())
                    for name, v, ts in zip(names, candidates, tables)
                ],
                scores=scores,
                selected_indices=chosen,
                mutations=mutations,
                retained_parent_mean=float(np.mean(scores[:2])),
            )
            self.record("generations.jsonl", previous)
            parents = [candidates[i] for i in chosen]
            if gen + 1 == self.generations // 2 and arm == "T":
                v = candidates[chosen[0]]
                ts = tables[chosen[0]]
                self.midpoints[tid] = dict(
                    vector=v.tolist(),
                    table=ts.tolist(),
                    table_hash=Decoder(ts).hash(),
                    score=scores[chosen[0]],
                )
                write_json(self.out, "midpoints.json", self.midpoints)
        self.record(
            "selected_changes.jsonl",
            dict(
                start=tid,
                arm=arm,
                acceptance_generation=self.generations - 1,
                final_generation_without_next_block=sum(
                    i >= 2 for i in previous["selected_indices"]
                ),
            ),
        )
        names = [f"{tid}:{arm}:final:{i}" for i in range(2)]
        rows, _ = self.jobs(
            [
                j
                for name, v in zip(names, parents)
                for j in self.block(
                    name,
                    table(v, self.g4),
                    tid[:2],
                    self.seed("selection", pi * 1000),
                    self.final_n,
                    self.inner_cap,
                )
            ],
            f"selection:{arm}:{tid}",
        )
        account(rows)
        scores = score(rows, names)
        i = int(np.argmin(scores))
        v, ts = parents[i], table(parents[i], self.g4)
        self.finals[f"{tid}:{arm}"] = dict(
            start=tid,
            arm=arm,
            vector=v.tolist(),
            table=ts.tolist(),
            table_hash=Decoder(ts).hash(),
            selection_scores=scores,
            selected_parent=i,
            selected_score=scores[i],
            step_mix=mix,
            diagnostics=diagnostics(v, self.g4, np.asarray(self.starts[tid]["table"])),
            search_costs=costs,
        )
        if costs["searches"] != self.config["searches_per_trajectory"]:
            raise ValueError("incorrect trajectory search budget")
        wall = time.monotonic() - tick
        self.slow_b = max(
            self.slow_b, wall * self.effective_workers / costs["searches"]
        )
        if arm == "T":
            self.token_times.append(wall)
            self.pairs.append(tid)
        else:
            self.context_starts.append(tid)
        write_json(self.out, "trajectories.json", self.finals)
        self.checkpoint("learning", context_starts=self.context_starts)
        print(f"Completed {tid}:{arm} in {wall:.1f}s", flush=True)

    def score_fresh(self, phase):
        maps = {}
        for tid in self.roster:
            maps[tid + ":S"] = np.asarray(self.starts[tid]["table"])
            maps[tid + ":T"] = np.asarray(self.finals[tid + ":T"]["table"])
            if phase == "F1":
                maps[tid + ":T_mid"] = np.asarray(self.midpoints[tid]["table"])
        if phase == "F2":
            maps["G4"] = self.g4
            for tid in self.context_starts:
                maps[tid + ":C"] = np.asarray(self.finals[tid + ":C"]["table"])
                v = np.asarray(self.finals[tid + ":C"]["vector"])
                v[49:] = 0
                maps[tid + ":C0"] = table(v, self.g4)
        frozen = {
            name: dict(table=ts.tolist(), table_hash=Decoder(ts).hash())
            for name, ts in maps.items()
        }
        write_json(self.out, phase.lower() + "_maps.json", frozen)
        seeds = self.config["fresh_seeds" if phase == "F1" else "f2_seeds"]
        jobs = [
            self.job(name, ts, cid, seed, self.fresh_cap)
            for name, ts in maps.items()
            for cid in (
                sum(TRAINING.values(), []) if name == "G4" else TRAINING[name[:2]]
            )
            for seed in seeds
        ]
        rows, wall = self.jobs(jobs, phase)
        write_json(self.out, phase.lower() + "_scores.json", rows)
        validation = validate_rows(rows, frozen, seeds, self.fresh_cap, phase)
        if not validation["passed"]:
            raise ValueError(str(validation))
        self.fresh_rate = max(
            self.fresh_rate, wall * self.effective_workers / len(rows)
        )
        return rows, frozen, validation

    def context_stage(self):
        for tid in self.roster:
            # Scale the measured fresh rate if later context maps slow learning.
            learn_rate = (
                max(self.token_times)
                * self.effective_workers
                / self.config["searches_per_trajectory"]
            )
            rate = self.fresh_rate * max(1.0, self.slow_b / learn_rate)
            res = reserve(
                self.roster,
                self.context_starts,
                tid,
                self.token_times,
                rate,
                self.effective_workers,
                self.fresh_n,
            )
            remaining = self.deadline - time.monotonic()
            admitted = (
                sum(
                    res[k]
                    for k in (
                        "trajectory_seconds",
                        "fresh_seconds",
                        "reporting_seconds",
                    )
                )
                <= remaining
            )
            self.schedule.append(
                dict(
                    prospective=tid,
                    admitted=admitted,
                    remaining_seconds=remaining,
                    **res,
                )
            )
            write_json(self.out, "admission.json", self.schedule)
            if not admitted:
                break
            self.evolve_arm(tid, "C")

    def baseline_probe(self):
        seeds = F1_SEEDS[:1]
        tids = ["BE1", "PA1"]
        rows, wall = self.jobs(
            [
                self.job(tid + ":S", self.starts[tid]["table"], c, s, 524288)
                for tid in tids
                for c in TRAINING[tid[:2]]
                for s in seeds
            ],
            "baseline_probe",
        )
        result = baseline_check(rows, self.reference, tids, seeds)
        result["wall_seconds"] = wall
        write_json(self.out, "baseline_probe.json", result)
        if not result["passed"]:
            raise ValueError("historical baseline smoke mismatch")

    def representative_probe(self):
        """One unselected full generation on BE1/PA1, then fixed fresh maps.

        Match full candidate occupancy instead of forecasting from calibration
        units. No probe score selects a map or alters full-run parameters.
        """
        jobs, fresh_jobs, metadata = [], [], {}
        for pi, tid in enumerate(("BE1", "PA1")):
            for ai, arm in enumerate(("T", "C")):
                origin = start_vector(
                    self.starts[tid]["vector"],
                    np.random.default_rng(self.seed("direction", pi * 10 + ai)),
                )
                rng = np.random.default_rng(self.seed("mutation", pi * 10 + ai))
                candidates = [origin.copy(), origin.copy()]
                for _ in range(6):
                    parent = int(rng.integers(2))
                    child, _ = step(candidates[parent], rng, self.g4, arm)
                    candidates.append(child)
                for i, v in enumerate(candidates):
                    name = f"probe:{tid}:{arm}:{i}"
                    metadata[name] = dict(family=tid[:2], arm=arm)
                    jobs.extend(
                        self.block(
                            name,
                            table(v, self.g4),
                            tid[:2],
                            self.seed("calibration", pi * 10000),
                            96,
                            65536,
                        )
                    )
                # Predetermined first child and saved S; no probe selection.
                fresh_jobs.extend(
                    self.job(
                        tid + ":" + arm,
                        table(candidates[2], self.g4),
                        c,
                        self.seed("calibration", 500000 + j),
                        524288,
                    )
                    for c in TRAINING[tid[:2]]
                    for j in range(10)
                )
            fresh_jobs.extend(
                self.job(
                    tid + ":S",
                    self.starts[tid]["table"],
                    c,
                    self.seed("calibration", 500000 + j),
                    524288,
                )
                for c in TRAINING[tid[:2]]
                for j in range(10)
            )
        learn, learn_wall = self.jobs(jobs, "probe:65536")
        fresh, fresh_wall = self.jobs(fresh_jobs, "probe:524288")

        def statistics(rows):
            return dict(
                searches=len(rows),
                solves=sum(r["solved"] for r in rows),
                solve_fraction=float(np.mean([r["solved"] for r in rows])),
                evaluations=sum(r["evaluations"] for r in rows),
                mean_worker_seconds=float(np.mean([r["seconds"] for r in rows])),
            )

        learn_rate, fresh_rate = learn_wall / len(learn), fresh_wall / len(fresh)
        per_arm = {
            f + ":" + a: statistics(
                [r for r in learn if metadata[r["arm"]] == dict(family=f, arm=a)]
            )
            for f in TRAINING
            for a in ("T", "C")
        }
        result = dict(
            task="2026-10-07-1137",
            learning=statistics(learn),
            fresh=statistics(fresh),
            learning_by_family_arm=per_arm,
            cap_batch_wall_seconds={"65536": learn_wall, "524288": fresh_wall},
            projected_stage1_seconds=153600 * learn_rate + 12000 * fresh_rate,
            projected_full_seconds=307200 * learn_rate + 28500 * fresh_rate,
            projected_minimum_context_seconds=(153600 + 12 * 9600) * learn_rate
            + (12000 + 14500) * fresh_rate,
            namespace_offset=self.offset,
            fixed_probe_never_selects_full_run_parameters=True,
            projection_scope="one full unselected candidate generation at BE1/PA1; learned-map runtime may differ",
        )
        write_json(self.out, "probe.json", result)
        self.checkpoint("probe_complete")
        print(json.dumps(result, indent=2), flush=True)

    def run(self):
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        try:
            if self.args.probe:
                self.baseline_probe()
                self.representative_probe()
                return
            for tid in self.roster:
                self.evolve_arm(tid, "T")
            f1, _, v1 = self.score_fresh("F1")
            baseline = (
                dict(passed=True, smoke_not_historical=True)
                if self.args.smoke
                else baseline_check(
                    f1, self.reference, self.roster, self.config["fresh_seeds"]
                )
            )
            write_json(self.out, "baseline_validation.json", baseline)
            if not baseline["passed"]:
                raise ValueError("F1 S scientific fields differ from 0821")
            c1, effects1 = contrasts(
                f1,
                self.roster,
                self.config["fresh_seeds"],
                self.fresh_cap,
                {
                    "T/S(F1)": ("S", "T"),
                    "T_mid/S(F1)": ("S", "T_mid"),
                    "T/T_mid(F1)": ("T_mid", "T"),
                },
            )
            gate_pass = gate(c1["T/S(F1)"]["pooled"])
            write_json(
                self.out,
                "gate.json",
                dict(
                    passed=gate_pass,
                    threshold=1.10,
                    estimate=c1["T/S(F1)"],
                    baseline_validation=baseline,
                    smoke_only=self.args.smoke,
                ),
            )
            # Smoke always exercises stage 2; its outcome is forced to U.
            f2, v2, c2, effects2 = [], dict(passed=True, not_run=True), {}, {}
            if gate_pass or self.args.smoke:
                self.context_stage()
                f2, _, v2 = self.score_fresh("F2")
                c2, effects2 = contrasts(
                    f2,
                    self.roster,
                    self.config["f2_seeds"],
                    self.fresh_cap,
                    {"T/S(F2,all)": ("S", "T")},
                )
                if self.context_starts:
                    matched, matched_effects = contrasts(
                        f2,
                        self.context_starts,
                        self.config["f2_seeds"],
                        self.fresh_cap,
                        {
                            "T/S(F2)": ("S", "T"),
                            "C/T": ("T", "C"),
                            "C/S": ("S", "C"),
                            "C/C0": ("C0", "C"),
                        },
                    )
                    c2.update(matched)
                    effects2.update(matched_effects)
                else:
                    c2["T/S(F2)"] = c2["T/S(F2,all)"]
            else:
                # Explicit artifacts distinguish a skipped stage from missing data.
                write_json(self.out, "f2_maps.json", {})
                write_json(self.out, "f2_scores.json", [])
            estimates = {**c1, **c2}
            token_counts = {
                f: sum(t.startswith(f) for t in self.pairs) for f in TRAINING
            }
            context_counts = {
                f: sum(t.startswith(f) for t in self.context_starts) for f in TRAINING
            }
            decision = outcome(
                c1["T/S(F1)"]["pooled"],
                c2.get("T/S(F2)", {}).get("pooled"),
                c2.get("C/T", {}).get("pooled"),
                c2.get("C/S", {}).get("pooled"),
                c2.get("C/C0", {}).get("pooled"),
                v1["passed"]
                and v2["passed"]
                and baseline["passed"]
                and not self.args.smoke,
                token_counts,
                context_counts,
            )
            # Historical rows are accessed for comparisons only after learning.
            old = [
                dict(r, arm=r["start"] + ":" + r["arm"])
                for r in self.reference["records"]
                if r["arm"] == "T24"
            ]
            if not self.args.smoke:
                historical, he = contrasts(
                    [*f1, *old],
                    self.roster,
                    F1_SEEDS,
                    self.fresh_cap,
                    {"T96/T24(F1)": ("T24", "T")},
                )
                estimates.update(historical)
                effects1.update(he)
            result = dict(
                outcome=decision,
                gate_passed=gate_pass,
                contrasts=estimates,
                pair_effects={**effects1, **effects2},
                token_counts=token_counts,
                context_counts=context_counts,
                context_starts=self.context_starts,
                validation=dict(
                    passed=v1["passed"] and v2["passed"] and baseline["passed"],
                    F1=v1,
                    F2=v2,
                    baseline=baseline,
                ),
                runtime=self.costs,
                admission=self.schedule,
                elapsed_seconds=time.monotonic() - self.started,
                scope="Fixed continuation on saved maps and training cells. F2 confirms scoring of the same learned maps, not independent learning replication. No transfer evaluation.",
                metric="A/B improvement = mean log2(cost_B)-log2(cost_A), equal own cells/seeds then equal family weights; unsolved=2*cap; t df=n_BE+n_PA-2.",
            )
            fresh_stats = {}
            for phase, rows in (("F1", f1), ("F2", f2)):
                for row in rows:
                    key = phase + "|" + row["arm"] + "|" + row["cell"]
                    stats = fresh_stats.setdefault(
                        key,
                        dict(
                            searches=0,
                            solves=0,
                            evaluations=0,
                            worker_seconds=0.0,
                            log2_cost_sum=0.0,
                        ),
                    )
                    stats["searches"] += 1
                    stats["solves"] += int(row["solved"])
                    stats["evaluations"] += row["evaluations"]
                    stats["worker_seconds"] += row["seconds"]
                    stats["log2_cost_sum"] += log_cost(row, self.fresh_cap)
            for stats in fresh_stats.values():
                stats.update(
                    solve_fraction=stats["solves"] / stats["searches"],
                    mean_log2_cost=stats["log2_cost_sum"] / stats["searches"],
                )
            result["fresh_stats"] = fresh_stats
            result["gain_vs_start"] = {
                tid: dict(
                    starting_mean_log2_cost=float(
                        np.mean(
                            [
                                fresh_stats["F1|" + tid + ":S|" + c]["mean_log2_cost"]
                                for c in TRAINING[tid[:2]]
                            ]
                        )
                    ),
                    token_gain_log2=effects1["T/S(F1)"][tid],
                )
                for tid in self.roster
            }
            self.save_report(result)
            self.checkpoint(
                "complete", outcome=decision, context_starts=self.context_starts
            )
        except Exception as exc:
            failure = dict(
                row="U",
                meaning=f"Infrastructure failure: {type(exc).__name__}: {exc}",
                next="strategy",
            )
            write_json(
                self.out, "report.json", dict(outcome=failure, runtime=self.costs)
            )
            (self.out / "report.md").write_text(f"Outcome U: {failure['meaning']}\n")
            self.checkpoint("failed", error=failure["meaning"])
            raise
        finally:
            self.pool.terminate()
            self.pool.join()

    def save_report(self, result):
        generations = [
            json.loads(line)
            for line in (self.out / "generations.jsonl").read_text().splitlines()
        ]
        selected = [
            json.loads(line)
            for line in (self.out / "selected_changes.jsonl").read_text().splitlines()
        ]
        curves = {}
        for name, rec in self.finals.items():
            tid, arm = name.split(":")
            rs = [r for r in generations if r["start"] == tid and r["arm"] == arm]
            ys = [r["retained_parent_mean"] for r in rs]
            curves[name] = dict(
                parent_mean_log2=ys,
                slope_log2_per_generation=float(np.polyfit(range(len(ys)), ys, 1)[0]),
                search_costs=rec["search_costs"],
                step_mix=rec["step_mix"],
                diagnostics=rec["diagnostics"],
                selected_change_coverage={
                    k: sum(
                        r.get(k, 0)
                        for r in selected
                        if r["start"] == tid and r["arm"] == arm
                    )
                    for k in (
                        "accepted_children",
                        "missing_source_parent",
                        "covered_pairs",
                        "final_generation_without_next_block",
                    )
                },
            )
            coverage = curves[name]["selected_change_coverage"]
            coverage["accepted_children_total"] = (
                coverage["accepted_children"]
                + coverage["final_generation_without_next_block"]
            )
        from experiments.chem_tape.four_reducer_maps import tables

        grammars = tables()
        direction = np.log(np.diff(grammars["G4-BE"], prepend=0, axis=1)) - np.log(
            np.diff(grammars["G4-PA"], prepend=0, axis=1)
        )
        alignment = {}
        for tid in self.context_starts:
            r = np.asarray(
                self.finals[tid + ":C"]["diagnostics"]["residual_log_weights"]
            )
            denom = np.linalg.norm(r) * np.linalg.norm(direction)
            alignment[tid] = float(np.sum(r * direction) / denom) if denom else None
        result.update(learning_diagnostics=curves, grammar_alignment_cosine=alignment)
        write_json(self.out, "report.json", result)
        lines = [
            "# Selection-calibrated continuation",
            "",
            result["scope"],
            "",
            f"Outcome {result['outcome']['row']}: {result['outcome']['meaning']}",
            "",
            "| Improvement | Ratio | 95% interval |",
            "|---|---:|---|",
        ]
        for name, e in result["contrasts"].items():
            p = e["pooled"]
            lines.append(f"| {name} | {p['ratio']} | {p['interval_95']} |")
        lines.extend(
            [
                "",
                "Selected-change readouts cover only accepted child/source-parent pairs both retained; coverage is in report.json and raw differences in selected_changes.jsonl.",
                "T96/T24 compares procedures with different total effort and depth. F1 controls admission; F2 supplies the stage-2 contrasts.",
            ]
        )
        (self.out / "report.md").write_text("\n".join(lines) + "\n")
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        for name, curve in curves.items():
            ys = curve["parent_mean_log2"]
            axes[0].plot(
                range(1, len(ys) + 1),
                ys,
                color="C0" if name.endswith(":T") else "C1",
                alpha=0.4,
            )
        axes[0].set(
            xlabel="Generation",
            ylabel="Rescored parent mean log2 cost",
            title="T blue; C orange",
        )
        for label in ("T/S(F1)", "T_mid/S(F1)", "T/S(F2)", "C/T"):
            if label in result["contrasts"]:
                p = result["contrasts"][label]["pooled"]
                if p["ratio"] is not None:
                    bounds = p["interval_95"]
                    error = (
                        [[p["ratio"] - bounds[0]], [bounds[1] - p["ratio"]]]
                        if bounds
                        else None
                    )
                    axes[1].errorbar([label], [p["ratio"]], yerr=error, fmt="o")
        axes[1].axhline(1, color="black", linewidth=0.7)
        axes[1].set(ylabel="Improvement ratio", title="Fresh paired estimates (95% t)")
        axes[1].tick_params(axis="x", labelrotation=25)
        fig.tight_layout()
        fig.savefig(self.out / "learning.png", dpi=140)
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=float, default=19800)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--smoke", action="store_true")
    group.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 180:
        parser.error("positive workers and >180 seconds required")
    ContinuationRunner(args).run()


if __name__ == "__main__":
    main()
