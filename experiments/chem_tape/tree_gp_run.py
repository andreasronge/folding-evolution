"""2254: frozen A8 versus closure GP, with preparation-gated target scoring."""

import argparse
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.component_transfer_run import (
    load_saved,
    envelope as native_envelope,
    execute as native_execute,
)
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape import composition_search as tape_search
from experiments.chem_tape.composition_search import Decoder, outputs
from experiments.chem_tape.family_preference_run import load_dg
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.independent_input_bank import ALPHABET
from experiments.chem_tape.independent_input_run import CAP, method_hashes
from experiments.chem_tape.tree_gp_search import GRAMMAR, MIXES, Tree, interpret, search
from experiments.chem_tape.tree_gp_validate import validate

TASK = "2026-10-10-2254"
SCORING_BASE = 22180000
LIMITS = dict(DG=7200, TS=5400)
HISTORICAL = dict(DG=dict(A8=11.7, G4=29.0), TS=dict(A8=3.6, G4=14.0))
SMOKE_SEEDS = {22160000, 22161000}
TAIL_SEEDS = {22160000 + 1000 * fi + 200 + i for fi in range(2) for i in range(10)}


def schedules(banks, targets, scoring_base=SCORING_BASE):
    calibration, scoring = [], []
    for fi, family in enumerate(("DG", "TS")):
        cells = banks[family]["split"]["source"] + banks[family]["split"]["development"]
        if (
            len(cells) != 8
            or len(targets[family]) != 8
            or set(cells) & set(targets[family])
        ):
            raise ValueError("calibration/target split changed")
        for ci, cid in enumerate(cells):
            for repeat in range(8):
                for mix in MIXES:
                    calibration.append(
                        dict(
                            family=family,
                            cell=cid,
                            arm="tree",
                            repeat=repeat,
                            crossover=mix,
                            phase="calibration",
                            seed=22140000 + 1000 * (8 * fi + ci) + repeat,
                        )
                    )
        for ci, cid in enumerate(targets[family]):
            for build in range(24):
                for repeat in range(2):
                    for arm in ("A8", "tree"):
                        scoring.append(
                            dict(
                                family=family,
                                cell=cid,
                                arm=arm,
                                build=build,
                                repeat=repeat,
                                phase="target",
                                seed=scoring_base
                                + 1000 * (8 * fi + ci)
                                + 2 * build
                                + repeat,
                            )
                        )
            for repeat in range(16):
                scoring.append(
                    dict(
                        family=family,
                        cell=cid,
                        arm="G4",
                        build=None,
                        repeat=repeat,
                        phase="target",
                        seed=scoring_base + 1000 * (8 * fi + ci) + 100 + repeat,
                    )
                )
    return calibration, scoring


def historical_seeds(saved):
    _, old, _, _ = load_dg()
    rows = saved["first.jsonl"] + saved["adaptive.jsonl"] + saved["replay.json"]
    rows += old["first.jsonl"] + old["adaptive.jsonl"]
    return {r["seed"] for r in rows}


def audit_seeds(calibration, score, historical=()):
    cal = {r["seed"] for r in calibration}
    target = {r["seed"] for r in score}
    historical = set(historical)
    overlaps = dict(
        calibration_scoring_overlap=sorted(cal & target),
        smoke_scoring_overlap=sorted(SMOKE_SEEDS & target),
        smoke_calibration_overlap=sorted(SMOKE_SEEDS & cal),
        historical_calibration_overlap=sorted(historical & cal),
        historical_scoring_overlap=sorted(historical & target),
        historical_smoke_overlap=sorted(historical & SMOKE_SEEDS),
        diagnostic_overlap=sorted(
            TAIL_SEEDS & (cal | target | historical | SMOKE_SEEDS)
        ),
    )
    implicated = [r for r in calibration if r["seed"] in cal & target]
    scored = [r for r in score if r["seed"] in cal & target]
    cal_keys = [
        (r["family"], r["cell"], r["repeat"], r["crossover"]) for r in calibration
    ]
    score_keys = [
        (r["family"], r["cell"], r["arm"], r["build"], r["repeat"]) for r in score
    ]
    cal_pairs = {}
    for r in calibration:
        cal_pairs.setdefault((r["family"], r["cell"], r["repeat"]), {})[
            r["crossover"]
        ] = r["seed"]
    cal_paired = len(cal_pairs) == 128 and all(
        set(v) == set(MIXES) and len(set(v.values())) == 1 for v in cal_pairs.values()
    )
    pairs = {}
    for r in score:
        if r["arm"] in ("A8", "tree"):
            pairs.setdefault((r["family"], r["cell"], r["build"], r["repeat"]), {})[
                r["arm"]
            ] = r["seed"]
    paired = all(
        set(v) == {"A8", "tree"} and len(set(v.values())) == 1 for v in pairs.values()
    )
    complete = (
        len(calibration) == 256
        and len(score) == 1792
        and len(set(cal_keys)) == 256
        and len(set(score_keys)) == 1792
        and len(cal) == 128
        and len(target) == 1024
        and len(pairs) == 768
        and paired
        and cal_paired
    )
    return dict(
        task=TASK,
        admitted=complete and not any(overlaps.values()),
        **overlaps,
        complete=complete,
        intended_pairing_valid=paired,
        calibration_pairing_valid=cal_paired,
        historical_source_replay_seed_count=len(historical),
        calibration_searches=len(calibration),
        target_searches=len(score),
        calibration_unique_seeds=len(cal),
        target_unique_seeds=len(target),
        implicated_calibration_rows=len(implicated),
        implicated_scoring_rows=len(scored),
        calibration_examples=implicated[:4],
        scoring_examples=scored[:4],
        targets_scored=False,
    )


def envelope(meta, saved, cap, crossover=None, force_cap=False):
    bank = saved["banks.json"][meta["family"]]
    cell = next(c for c in bank["screen"]["cells"] if c["id"] == meta["cell"])
    if meta["arm"] == "tree":
        mix = meta.get("crossover", crossover)
        return dict(
            kind="tree",
            meta=meta | dict(crossover=mix),
            force_cap=force_cap,
            job=(cell, meta["seed"], cap, 256, bank["inputs"], mix),
        )
    owner = "D" if meta["family"] == "DG" else "T"
    if meta["arm"] == "A8":
        m = meta | dict(
            table_owner=owner,
            table_build=meta["build"],
            library_owner=owner,
            library_build=meta["build"],
            operator_mode="literal",
        )
        native = native_envelope(m, saved, cap)
    elif meta["arm"] == "G4":
        m = meta | dict(operator_mode="off")
        native = (
            (
                cell,
                "G4",
                tables()["G4"].tolist(),
                meta["seed"],
                cap,
                256,
                bank["inputs"],
                ALPHABET,
            ),
            m,
            [],
            [],
        )
    else:
        raise ValueError("unknown arm")
    return dict(kind="native", meta=m, job=native)


def execute(e):
    tick = time.monotonic()
    if e["kind"] == "tree":
        row = search(e["job"], force_cap=e["force_cap"]) | e["meta"]
    else:
        original_outputs = tape_search.outputs
        phenotype_curve, last, generations = [], None, 0

        def observe(programs, inputs, alphabet="v2_rmin"):
            nonlocal last, generations
            result = original_outputs(programs, inputs, alphabet)
            if len(programs) == 256 and len(inputs) == 64:
                generations += 1
                if (generations - 1) % 32 == 0:
                    last = [generations * 256, len(np.unique(result, axis=0))]
                    phenotype_curve.append(last)
                else:
                    last = (generations * 256, result)
            return result

        tape_search.outputs = observe
        try:
            row = native_execute(e["job"])
        finally:
            tape_search.outputs = original_outputs
        if phenotype_curve[-1][0] != row["evaluations"]:
            phenotype_curve.append([last[0], len(np.unique(last[1], axis=0))])
        row.update(
            phenotype_diversity_curve=phenotype_curve,
            phenotype_diversity_scope="distinct output vectors on 64 fixed training cases; lower bound on D625 phenotype diversity",
        )
        # Production tapes are exactly 32 tokens at every evaluated generation.
        row.update(
            mean_compiled_length=32.0,
            max_compiled_length=32,
            compiled_tokens_evaluated=32 * row["evaluations"],
            primitive_case_work=32 * 64 * row["evaluations"],
            compiled_length_histogram=[0] * 32 + [row["evaluations"]],
        )
    row["worker_seconds"] = time.monotonic() - tick
    return row


def row_key(r):
    return (
        r["family"],
        r["cell"],
        r["arm"],
        r.get("build"),
        r["repeat"],
        r.get("crossover"),
    )


def validate_rows(rows, schedule, saved, cap, crossover=None, force_cap=False):
    expected = [envelope(m, saved, cap, crossover, force_cap)["meta"] for m in schedule]
    by = {row_key(r): r for r in rows}
    if len(by) != len(rows) or set(by) != {row_key(m) for m in expected}:
        raise ValueError("missing/duplicate/unexpected search rows")
    for m in expected:
        r = by[row_key(m)]
        e = envelope(m, saved, cap, crossover, force_cap)
        if any(r.get(k) != v for k, v in m.items()):
            raise ValueError("search provenance mismatch")
        if (
            r["cap"] != cap
            or r["pop_size"] != 256
            or not 0 < r["evaluations"] <= cap
            or r["evaluations"] % 256
            or r["generations"] * 256 != r["evaluations"]
            or (not r["solved"] and r["evaluations"] != cap)
            or (r["solver"] is not None) != r["solved"]
        ):
            raise ValueError("invalid budget/solver accounting")
        indices = (
            np.random.default_rng([r["seed"], 0])
            .choice(625, 64, replace=False)
            .tolist()
        )
        if r["training_indices"] != indices:
            raise ValueError("training RNG mismatch")
        job = e["job"] if e["kind"] == "tree" else e["job"][0]
        cell, inputs = job[0], job[4] if e["kind"] == "tree" else job[6]
        if r["solved"] and not np.array_equal(
            outputs([r["solver"]], inputs, ALPHABET)[0], cell["labels"]
        ):
            raise ValueError("D625 verification failed")
        if r["arm"] == "tree":
            if r["max_compiled_length"] > 32 or r["initialization"]["rejected"] < 0:
                raise ValueError("tree size accounting")
            s = r["operator"]
            if s["crossover"] + s["mutation"] != (r["generations"] - 1) * 254:
                raise ValueError("tree operator accounting")
            if r["solved"]:
                tree = Tree(tuple(r["solver_tree"]))
                if (
                    list(tree.program) != r["solver"]
                    or [interpret(tree, x) for x in inputs] != cell["labels"]
                ):
                    raise ValueError("independent tree solver verification failed")
        else:
            if r["table_hash"] != Decoder(job[2]).hash() or r["library_hash"] != digest(
                e["job"][2]
            ):
                raise ValueError("table/library mismatch")
            if r["arm"] == "G4":
                if r["operator"] is not None or r["block_events"] != 0:
                    raise ValueError("G4 used acquired blocks")
            elif r["operator"]["eligible_children"] != (r["generations"] - 1) * 254:
                raise ValueError("native operator boundary")
    return sorted(rows, key=lambda r: str(row_key(r)))


def choose_mix(rows):
    costs = {
        m: float(
            np.mean(
                [
                    np.log(r["evaluations"] if r["solved"] else 2 * r["cap"])
                    for r in rows
                    if r["crossover"] == m
                ]
            )
        )
        for m in MIXES
    }
    return min(MIXES, key=lambda m: costs[m]), {str(m): v for m, v in costs.items()}


def project(rows, batches, replays, tails, tail_batches, crossover, workers=10):
    result = {}
    for family in ("DG", "TS"):
        all_rows = [r for r in rows if r["family"] == family]
        rs = [r for r in all_rows if r["crossover"] == crossover]
        full = [r for r in rs if r["evaluations"] == CAP]
        forced = [r for r in tails if r["family"] == family]
        if not full and not forced:
            raise ValueError("missing full-cap tail measurement")
        batch = batches[family]
        effective = min(workers, batch["worker_seconds"] / batch["wall_seconds"])
        if family in tail_batches:
            t = tail_batches[family]
            effective = min(effective, t["worker_seconds"] / t["wall_seconds"])
        if effective <= 0:
            raise ValueError("invalid effective concurrency")
        rates = dict(
            tree=float(np.mean([r["worker_seconds"] for r in rs])),
            A8=max(
                HISTORICAL[family]["A8"],
                float(
                    np.mean(
                        [r["worker_seconds"] for r in replays if r["family"] == family]
                    )
                ),
            ),
            G4=HISTORICAL[family]["G4"],
        )
        worker = (384 * (rates["tree"] + rates["A8"]) + 128 * rates["G4"]) / effective
        average = np.mean([r["worker_seconds"] for r in all_rows])
        tree_wall = (
            batch["wall_seconds"]
            * 384
            / len(all_rows)
            * max(1, rates["tree"] / average)
        )
        wall = tree_wall + (384 * rates["A8"] + 128 * rates["G4"]) / effective
        projected = 1.3 * max(worker, wall) + 120
        logs = np.array(
            [
                np.mean(
                    [
                        np.log(r["evaluations"] if r["solved"] else 2 * CAP)
                        for r in rs
                        if r["repeat"] == i
                    ]
                )
                for i in range(8)
            ]
        )
        sd = float(np.std(logs, ddof=1))
        width = float(np.exp(2 * 1.96 * sd / np.sqrt(24)))
        tail_rows = full + forced
        result[family] = dict(
            admitted=projected <= 0.8 * LIMITS[family],
            rates=rates,
            projected_seconds=projected,
            limit_seconds=0.8 * LIMITS[family],
            effective_workers=effective,
            chosen_solved=sum(r["solved"] for r in rs),
            chosen_attempts=len(rs),
            chosen_solve_fraction=float(np.mean([r["solved"] for r in rs])),
            full_cap_searches=len(tail_rows),
            full_cap_mean_seconds=float(
                np.mean([r["worker_seconds"] for r in tail_rows])
            ),
            full_cap_max_seconds=max(r["worker_seconds"] for r in tail_rows),
            exact_check_seconds=sum(r["exact_check_seconds"] for r in all_rows),
            max_exact_check_seconds=max(r["exact_check_max_seconds"] for r in all_rows),
            precision=dict(
                tree_seed_block_log_cost_sd=sd,
                tree_only_interval_multiplicative_width_at24=width,
                label="tree-only planning proxy; paired A8/tree uncertainty unmeasured; near-margin Q may remain unresolved",
            ),
            operator={k: sum(r["operator"][k] for r in rs) for k in rs[0]["operator"]},
            initial_rejected=sum(r["initialization"]["rejected"] for r in rs),
            initial_attempts=sum(r["initialization"]["attempts"] for r in rs),
            final_mean_diversity=float(np.mean([r["curve"][-1][2] for r in rs])),
        )
    return result


def require_admission(p):
    if p["preparation_hash"] != digest(
        {k: v for k, v in p.items() if k != "preparation_hash"}
    ):
        raise ValueError("preparation hash mismatch")
    admitted = (
        p["validation"]["admitted"]
        and p["seed_audit"]["admitted"]
        and p["replay"]["passed"]
        and all(v["admitted"] for v in p["projection"].values())
        and p["projection"]["DG"]["chosen_solve_fraction"] >= 0.25
        and p["prepare_seconds"] <= 1770
    )
    if p["admitted"] != admitted or not admitted or p["smoke"]:
        raise ValueError(
            "Preparation gate failed; no targets. Return to strategy; DG <25% requires reviewer diagnostic."
        )


class Runner:
    def __init__(self, args):
        self.args = args
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 30
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        if (self.out / "config.json").exists():
            raise ValueError("fresh RUN_DIR required")
        self.saved, self.targets = load_saved()
        self.calibration, self.schedule = schedules(
            self.saved["banks.json"], self.targets
        )
        self.cap = 8192 if args.smoke else CAP
        self.freeze = dict(
            task=TASK,
            scoring_base=SCORING_BASE,
            grammar=GRAMMAR,
            banks_hash=digest(self.saved["banks.json"]),
            builds_hash=digest(self.saved["builds.json"]),
            calibration_hash=digest(self.calibration),
            schedule_hash=digest(self.schedule),
            method_hashes=method_hashes(),
            targets=self.targets,
            cap=self.cap,
            population=256,
            workers=args.workers,
            smoke=args.smoke,
        )
        self.freeze = json.loads(json.dumps(self.freeze))
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
        write_json(self.out, "method_freeze.json", self.freeze)
        write_json(self.out, "calibration_schedule.json", self.calibration)
        write_json(self.out, "target_schedule.json", self.schedule)

    def jobs(self, metas, name, phase, crossover=None, force_cap=False, envelopes=None):
        tick, rows = time.monotonic(), []
        with (self.out / name).open("w", buffering=1) as stream:

            def save(row):
                rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                write_json(
                    self.out,
                    "progress.json",
                    dict(phase=phase, completed=len(rows), total=len(metas)),
                )

            if not run_jobs(
                self.pool,
                execute,
                envelopes
                or [
                    envelope(m, self.saved, self.cap, crossover, force_cap)
                    for m in metas
                ],
                self.deadline,
                save,
            ):
                raise TimeoutError("incomplete batch: " + phase)
        self.batches[phase] = dict(
            wall_seconds=time.monotonic() - tick,
            jobs=len(rows),
            worker_seconds=sum(r["worker_seconds"] for r in rows),
        )
        write_json(self.out, "timing.json", self.batches)
        return rows

    def replay(self):
        expected, metas, jobs = self.saved["replay.json"], [], []
        for r in expected:
            m = {
                k: r[k]
                for k in (
                    "family",
                    "cell",
                    "arm",
                    "seed",
                    "build",
                    "ordinal",
                    "phase",
                    "alphabet",
                )
            }
            m.update(
                table_owner=r["arm"],
                table_build=r["build"],
                library_owner=r["arm"],
                library_build=r["build"],
                operator_mode="literal",
            )
            metas.append(m)
            jobs.append(
                dict(kind="native", meta=m, job=native_envelope(m, self.saved, CAP))
            )
        actual = self.jobs(metas, "replay.jsonl", "replay", envelopes=jobs)
        by = {(r["cell"], r["arm"], r["seed"]): r for r in actual}
        ignored = {
            "seconds",
            "budget_seconds",
            "decode_seconds",
            "exact_check_seconds",
            "exact_check_max_seconds",
        }
        for old in expected:
            new = by[old["cell"], old["arm"], old["seed"]]
            changed = [k for k in old if k not in ignored and old[k] != new[k]]
            if changed:
                raise ValueError("native replay mismatch: " + str(changed))
        return actual, dict(
            rows=16, passed=True, excluded_timing_fields=sorted(ignored)
        )

    def prepare(self):
        audit = audit_seeds(
            self.calibration, self.schedule, historical_seeds(self.saved)
        )
        write_json(self.out, "schedule_audit.json", audit)
        if not audit["admitted"]:
            raise ValueError("seed audit failed before calibration")
        validation = validate()
        write_json(self.out, "validation.json", validation)
        if not validation["admitted"]:
            raise ValueError("validity/initialization gate failed")
        replays, replay = self.replay()
        calibration = self.calibration
        if self.args.smoke:
            calibration = [
                m | dict(seed=22160000 + 1000 * (m["family"] == "TS"), phase="smoke")
                for m in calibration
                if m["repeat"] == 0
                and m["cell"]
                == self.saved["banks.json"][m["family"]]["split"]["development"][0]
            ]
        rows = []
        for family in ("DG", "TS"):
            subset = [m for m in calibration if m["family"] == family]
            rows += self.jobs(subset, "calibration_" + family + ".jsonl", family)
        rows = validate_rows(rows, calibration, self.saved, self.cap)
        mix, costs = choose_mix(rows)
        tails, tail_batches = [], {}
        if not self.args.smoke:
            for fi, family in enumerate(("DG", "TS")):
                if any(
                    r["evaluations"] == CAP
                    and r["crossover"] == mix
                    and r["family"] == family
                    for r in rows
                ):
                    continue
                metas = [
                    dict(
                        family=family,
                        cell=self.saved["banks.json"][family]["split"]["development"][
                            i % 4
                        ],
                        arm="tree",
                        phase="tail",
                        seed=22160000 + 1000 * fi + 200 + i,
                        repeat=i,
                        crossover=mix,
                    )
                    for i in range(10)
                ]
                actual = self.jobs(
                    metas,
                    "tails_" + family + ".jsonl",
                    "tail_" + family,
                    force_cap=True,
                )
                tails += validate_rows(actual, metas, self.saved, CAP, force_cap=True)
                tail_batches[family] = self.batches["tail_" + family]
        projection = (
            {}
            if self.args.smoke
            else project(rows, self.batches, replays, tails, tail_batches, mix)
        )
        elapsed = time.monotonic() - self.started
        admitted = (
            not self.args.smoke
            and all(v["admitted"] for v in projection.values())
            and projection["DG"]["chosen_solve_fraction"] >= 0.25
            and elapsed <= 1770
        )
        p = dict(
            freeze=self.freeze,
            smoke=self.args.smoke,
            seed_audit=audit,
            validation=validation,
            replay=replay,
            chosen_crossover=mix,
            calibration_log_costs=costs,
            calibration_actual_evaluations=sum(r["evaluations"] for r in rows),
            calibration_rows_hash=digest(rows),
            replay_rows_hash=digest(replays),
            tails_hash=digest(tails),
            projection=projection,
            batches=self.batches,
            prepare_seconds=elapsed,
            admitted=admitted,
            targets_scored=False,
        )
        p["preparation_hash"] = digest(p)
        write_json(self.out, "preparation.json", p)
        print(
            json.dumps(
                dict(
                    admitted=admitted,
                    chosen_crossover=mix,
                    projection=projection,
                    seconds=elapsed,
                )
            ),
            flush=True,
        )
        if not self.args.smoke:
            require_admission(p)

    def load_preparation(self):
        parent = Path(self.args.preparation)
        p = json.loads((parent / "preparation.json").read_text())
        require_admission(p)
        if (
            p["freeze"] != self.freeze
            or json.loads((parent / "method_freeze.json").read_text()) != self.freeze
        ):
            raise ValueError("preparation/current method freeze mismatch")
        rows = []
        for f in ("DG", "TS"):
            rows += [
                json.loads(x)
                for x in (parent / ("calibration_" + f + ".jsonl"))
                .read_text()
                .splitlines()
            ]
        rows = validate_rows(rows, self.calibration, self.saved, CAP)
        if (
            digest(rows) != p["calibration_rows_hash"]
            or choose_mix(rows)[0] != p["chosen_crossover"]
        ):
            raise ValueError("calibration rows/frozen mix changed")
        # Bind every preparation evidence file consumed by the timing/admission gates.
        replays = [
            json.loads(x) for x in (parent / "replay.jsonl").read_text().splitlines()
        ]
        tails = []
        for f in ("DG", "TS"):
            path = parent / ("tails_" + f + ".jsonl")
            if path.exists():
                tails += [json.loads(x) for x in path.read_text().splitlines()]
        if (
            digest(replays) != p["replay_rows_hash"]
            or digest(sorted(tails, key=lambda r: str(row_key(r)))) != p["tails_hash"]
        ):
            raise ValueError("replay/tail evidence changed")
        if (
            audit_seeds(self.calibration, self.schedule, historical_seeds(self.saved))
            != p["seed_audit"]
        ):
            raise ValueError("seed audit changed")
        tail_batches = {
            f: p["batches"]["tail_" + f]
            for f in ("DG", "TS")
            if "tail_" + f in p["batches"]
        }
        if (
            project(
                rows, p["batches"], replays, tails, tail_batches, p["chosen_crossover"]
            )
            != p["projection"]
        ):
            raise ValueError("timing/solve gate changed")
        return p

    def score(self):
        p = self.load_preparation()
        family, mix = self.args.family, p["chosen_crossover"]
        previous = []
        # Validate DG dependencies before spending on any TS target.
        if family == "TS":
            parent = Path(self.args.dg_score)
            if (
                json.loads((parent / "method_freeze.json").read_text()) != self.freeze
                or json.loads((parent / "preparation.json").read_text()) != p
            ):
                raise ValueError("DG dependency freeze mismatch")
            previous = [
                json.loads(x)
                for x in (parent / "search.jsonl").read_text().splitlines()
            ]
            previous = validate_rows(
                previous,
                [m for m in self.schedule if m["family"] == "DG"],
                self.saved,
                CAP,
                mix,
            )
            if (
                digest(previous)
                != json.loads((parent / "result.json").read_text())["search_rows_hash"]
            ):
                raise ValueError("DG result hash mismatch")
        selected = [m for m in self.schedule if m["family"] == family]
        rows = validate_rows(
            self.jobs(selected, "search.jsonl", "score", mix),
            selected,
            self.saved,
            CAP,
            mix,
        )
        write_json(self.out, "preparation.json", p)
        from experiments.chem_tape.tree_gp_report import report

        report(self.out, rows + previous, self.saved, p, self.batches)

    def run(self):
        pool = mp.get_context("spawn").Pool(self.args.workers)
        self.pool = pool
        try:
            self.prepare() if self.args.prepare else self.score()
        except BaseException as exc:
            pool.terminate()
            pool.join()
            write_json(
                self.out,
                "failure.json",
                dict(
                    error=str(exc),
                    phase="prepare" if self.args.prepare else "score",
                    targets_scored=(self.out / "search.jsonl").exists(),
                    next="strategy",
                ),
            )
            raise
        else:
            pool.close()
            pool.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--family", choices=("DG", "TS"))
    parser.add_argument("--dg-score")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=1800)
    args = parser.parse_args()
    if args.audit_only:
        saved, targets = load_saved()
        cal, score = schedules(saved["banks.json"], targets)
        out = Path(os.environ["RUN_DIR"])
        out.mkdir(parents=True, exist_ok=True)
        audit = audit_seeds(cal, score, historical_seeds(saved))
        for name, value in [
            ("schedule_audit.json", audit),
            ("calibration_schedule.json", cal),
            ("target_schedule.json", score),
        ]:
            write_json(out, name, value)
        print(json.dumps(audit), flush=True)
        if not audit["admitted"]:
            raise SystemExit("seed gate failed")
        return
    if (
        args.workers != 10
        or args.deadline_seconds <= 30
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
            "requires ten workers, prepare or gated family scoring; smoke is development preparation only"
        )
    if args.deadline_seconds > (1800 if args.prepare else LIMITS[args.family]):
        parser.error("deadline exceeds approved timeout")
    Runner(args).run()


if __name__ == "__main__":
    main()
