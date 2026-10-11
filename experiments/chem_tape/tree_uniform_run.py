"""0652: uniform labels versus empirical permutation on frozen donor shapes."""

import argparse
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import gate_sum_run as previous
from experiments.chem_tape import gate_sum_bank as bank_module
from experiments.chem_tape import tree_library_run as base
from experiments.chem_tape import restart_gp_run as restart
from experiments.chem_tape import tree_permutation as permutation
from experiments.chem_tape import tree_uniform as uniform
from experiments.chem_tape import tree_permutation_run as prior_run
from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.independent_input_run import method_hashes
from experiments.chem_tape.tree_gp_search import Tree

TASK = uniform.TASK
ARMS = ("R-tree", "R-lib", "R-perm", "R-unif", "R-size")
DATA = Path(__file__).with_name("data") / "tree_uniform_0652"
BOOTSTRAP_SEED = uniform.seed("bootstrap")


def snapshot(name):
    provenance = json.loads((DATA / "provenance.json").read_text())
    raw = gzip.decompress((DATA / (name + ".gz")).read_bytes())
    if hashlib.sha256(raw).hexdigest() != provenance["artifacts"][name]:
        raise ValueError("archived 0524 artifact changed: " + name)
    return (
        [json.loads(line) for line in raw.splitlines()]
        if name.endswith("jsonl")
        else json.loads(raw)
    )


def score_cells(bank):
    by = {c["id"]: c for c in bank["screen"]["cells"]}
    cells = [
        c
        for c in bank["split"]["protected"]
        if bank_module.pairing(by[c]) in permutation.PAIRS[1:]
    ]
    if len(cells) != 12:
        raise ValueError("approved twelve B/C cells changed")
    return cells


def schedules(bank, repeats=6, arms=ARMS):
    if (repeats, tuple(arms)) not in ((6, ARMS), (6, ARMS[:-1]), (4, ARMS[:-1])):
        raise ValueError("unapproved runtime fallback")

    def metas(phase, cells, count, active):
        return [
            dict(
                family="GS",
                cell=c,
                arm=a,
                build=b,
                repeat=r,
                realization=r % 3,
                seeds=[uniform.seed(phase, c, b, r, k) for k in range(8)],
            )
            for c in cells
            for b in range(24)
            for r in range(count)
            for a in active
        ]

    return dict(
        stage=metas("stage", bank["split"]["development"], 3, ("R-unif",)),
        score=metas("score", score_cells(bank), repeats, arms),
    )


def seed_audit(schedule):
    old = snapshot("schedule_audit.json")
    historic = set()
    for audit in (
        old,
        prior_run.snapshot("schedule_audit.json"),
        previous.snapshot("schedule_audit.json"),
    ):
        historic.update(audit.get("historical_seeds", []))
        historic.update(audit.get("reserved_probe_seeds", []))
        for values in audit["published_seed_sets"].values():
            historic.update(values)
    sets, paired = {}, True
    for phase, metas in schedule.items():
        uses = {}
        paired &= len({restart.key(m) for m in metas}) == len(metas)
        for m in metas:
            paired &= m["realization"] == m["repeat"] % 3
            for k, s in enumerate(m["seeds"]):
                uses.setdefault(s, []).append((m, k))
        expected = set(ARMS) if phase == "score" else {"R-unif"}
        for records in uses.values():
            paired &= (
                len(records) == len(expected)
                and {m["arm"] for m, _ in records} == expected
                and len({(m["cell"], m["build"], m["repeat"], k) for m, k in records})
                == 1
            )
        sets[phase] = set(uses)
    sets["construction"] = {
        uniform.seed("construction", b, r) for b in range(24) for r in range(3)
    }
    sets["bootstrap"] = {BOOTSTRAP_SEED}
    bank = prior_run.snapshot("bank.json")
    sets["smoke"] = {
        uniform.seed("smoke", c, b, r, k)
        for c in bank["split"]["development"]
        for b in range(24)
        for r in range(3)
        for k in range(8)
    }
    overlaps = {a + "_historic": sorted(v & historic) for a, v in sets.items()}
    for i, a in enumerate(sets):
        for b in list(sets)[i + 1 :]:
            overlaps[a + "_" + b] = sorted(sets[a] & sets[b])
    complete = schedule == schedules(bank)
    return dict(
        admitted=bool(paired and complete and not any(overlaps.values())),
        intended_pairing_valid=bool(paired),
        complete=complete,
        overlaps=overlaps,
        published_seed_sets={k: sorted(v) for k, v in sets.items()},
        historical_count=len(historic),
        historical_hash=digest(sorted(historic)),
        rule="SHA256 canonical JSON [task, domain, parts], first eight bytes big-endian masked to 63 bits",
        replay_exception="six saved 0524 R-perm jobs, validation only",
        control_exception="exact 0150 R-size and 0524 R-perm construction seeds",
    )


def stage_gate(rows, batch, replay):
    eff = min(10.0, batch["worker_seconds"] / batch["wall_seconds"])
    scale = max(
        1.0,
        sum(r["worker_seconds"] for r in replay)
        / sum(r["worker_seconds"] for r in snapshot("replay.jsonl")),
    )
    rates = snapshot("reference_rates.json")
    arms = {
        a: dict(mean_worker_seconds=rates[a]["mean_worker_seconds"] * scale)
        for a in ARMS
        if a != "R-unif"
    }
    mean = float(np.mean([r["worker_seconds"] for r in rows]))
    arms["R-unif"] = dict(
        jobs=len(rows),
        solves=sum(r["solved"] for r in rows),
        eight_attempt_jobs=sum(r["attempt_count"] == 8 for r in rows),
        capped_jobs=sum(r["evaluations"] == r["cap"] for r in rows),
        measured_mean_worker_seconds=mean,
        mean_worker_seconds=max(mean, arms["R-tree"]["mean_worker_seconds"]),
        quantiles={
            m: np.quantile([r[m] for r in rows], [0, 0.5, 0.9, 0.95, 1]).tolist()
            for m in ("evaluations", "worker_seconds", "attempt_count")
        },
    )
    candidates = [(6, ARMS), (6, ARMS[:-1]), (4, ARMS[:-1])]
    projections = [
        dict(
            repeats=n,
            arms=list(active),
            seconds=90
            + 1.3
            * 24
            * 12
            * n
            * sum(arms[a]["mean_worker_seconds"] for a in active)
            / eff,
        )
        for n, active in candidates
    ]
    chosen = next((x for x in projections if x["seconds"] <= 6000), projections[-1])
    return dict(
        admitted=chosen["seconds"] <= 6000,
        repeats=chosen["repeats"],
        active_arms=chosen["arms"],
        realizations=3,
        realization_rule="repeat modulo three; equal weight after averaging repeats within realization",
        arms=arms,
        effective_concurrency=eff,
        replay_host_scale=scale,
        sustained_wall_seconds=batch["wall_seconds"],
        projections=projections,
        scoring_projected_seconds=chosen["seconds"],
        scoring_limit_seconds=6000,
        per_construction=[
            dict(
                build=b,
                realization=r,
                jobs=len(rs),
                solves=sum(x["solved"] for x in rs),
                mean_evaluations=float(np.mean([x["evaluations"] for x in rs])),
                mean_worker_seconds=float(np.mean([x["worker_seconds"] for x in rs])),
            )
            for b, r in sorted({(x["build"], x["realization"]) for x in rows})
            for rs in [[x for x in rows if (x["build"], x["realization"]) == (b, r)]]
        ],
        projection="archived B/C baseline rates, upward replay host scale; measured uniform with R-tree floor; sustained concurrency; 30% reserve +90s; development-to-B/C heterogeneity unmeasured",
    )


def construct(saved, inputs):
    libraries, rebuilt = previous.reconstruct(saved)
    libraries, perm_audit = permutation.build(libraries, inputs)
    archived = snapshot("libraries.json")
    p = snapshot("preparation.json")
    if (
        not p["admitted"]
        or p["smoke"]
        or digest(archived) != p["libraries_hash"]
        or p["preparation_hash"]
        != digest({k: v for k, v in p.items() if k != "preparation_hash"})
    ):
        raise ValueError("archived 0524 library admission changed")
    if restart.deterministic(libraries) != restart.deterministic(archived):
        raise ValueError("0524 frozen construction hashes changed")
    libraries, audit = uniform.build(libraries, inputs)
    audit["permutation_audit"] = perm_audit
    audit["frozen_0524_hashes"] = [digest(restart.deterministic(x)) for x in archived]
    return libraries, rebuilt, audit


def validate_rows(rows, metas, saved, cutoff=65536):
    rows = base.validate_rows(rows, metas, saved, cutoff)
    paired = {}
    for row in rows:
        for attempt in row["attempts"]:
            k = row["cell"], row["build"], row["repeat"], attempt["seed"]
            fields = attempt["initial_tokens_hash"], attempt["training_indices"]
            if k in paired and paired[k] != fields:
                raise ValueError("initial population or case pairing failed")
            paired[k] = fields
    return rows


def envelope(meta, saved, libraries, cutoff):
    if meta["arm"] not in ARMS:
        raise ValueError("unknown donor arm")
    e = restart.envelope(meta | dict(arm="R-tree"), saved, cutoff)
    e["meta"] = meta
    lib = libraries[meta["build"]] if libraries is not None else None
    entries = (
        None
        if meta["arm"] == "R-tree"
        else (
            lib["entries"]
            if meta["arm"] == "R-lib"
            else lib["controls"]
            if meta["arm"] == "R-size"
            else lib[
                "uniform_constructions" if meta["arm"] == "R-unif" else "constructions"
            ][meta["realization"]]["entries"]
        )
    )
    e["donors"] = (
        None if entries is None else [Tree(tuple(x["prefix"])) for x in entries]
    )
    return e


class Runner(base.Runner):
    def __init__(self, args):
        self.args = args
        self.deadline = time.monotonic() + args.deadline_seconds - 30
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        restart.require_fresh(self.out)
        self.saved, _ = load_saved()
        self.bank = prior_run.snapshot("bank.json")
        bank_module.validate_bank(
            self.bank,
            list(self.saved["banks.json"].values()),
            previous.snapshot("planning.json"),
        )
        prior = prior_run.snapshot("preparation.json")
        if (
            not prior["admitted"]
            or prior["bank_hash"] != digest(self.bank)
            or prior["preparation_hash"]
            != digest({k: v for k, v in prior.items() if k != "preparation_hash"})
        ):
            raise ValueError("0348 bank admission evidence changed")
        self.saved["banks.json"]["GS"] = self.bank
        self.schedule = schedules(self.bank)
        self.audit = seed_audit(self.schedule)
        self.freeze = previous.freeze(self.bank, self.schedule, method_hashes()) | dict(
            task=TASK,
            artifacts_0524=json.loads((DATA / "provenance.json").read_text()),
            scope="development-bank uniform-label replacement conditional on acquired skeletons, widths, sizes and multiplicities",
        )
        old_methods = self.freeze["artifacts_0524"]["method_hashes"]
        for path in (
            "experiments/chem_tape/tree_permutation.py",
            "experiments/chem_tape/tree_permutation_run.py",
        ):
            if self.freeze["methods"][path] != old_methods[path]:
                raise ValueError("0524 construction/search method changed: " + path)
        self.freeze["targets"] = score_cells(self.bank)
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
            ("bank.json", self.bank),
            ("method_freeze.json", self.freeze),
            ("schedule_audit.json", self.audit),
            ("schedules.json", self.schedule),
        ]:
            write_json(self.out, name, value)
        if not self.audit["admitted"]:
            raise ValueError("seed audit failed")

    def jobs(self, metas, name, libraries=None, cutoff=65536):
        start = time.monotonic()
        rows = []
        with (self.out / (name + ".jsonl")).open("w", buffering=1) as stream:

            def save(r):
                rows.append(r)
                stream.write(json.dumps(r, allow_nan=False) + "\n")
                write_json(
                    self.out,
                    "progress.json",
                    dict(phase=name, completed=len(rows), total=len(metas)),
                )

            if not run_jobs(
                self.pool,
                base.execute,
                [envelope(m, self.saved, libraries, cutoff) for m in metas],
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

    def replay(self, libraries):
        original = snapshot("replay.jsonl")
        metas = [
            {
                k: r[k]
                for k in (
                    "family",
                    "cell",
                    "arm",
                    "build",
                    "repeat",
                    "realization",
                    "seeds",
                )
            }
            for r in original
        ]
        rows = self.jobs(metas, "replay", libraries)
        by = {restart.key(r): r for r in original}
        if any(
            restart.deterministic(r) != restart.deterministic(by[restart.key(r)])
            for r in rows
        ):
            raise ValueError("saved 0524 R-perm determinism replay failed")
        return rows, dict(
            passed=True,
            jobs=len(rows),
            fields="all deterministic fields",
            rows_hash=digest(rows),
        )

    def prepare(self):
        verification = bank_module.verify(self.bank)
        libraries, rebuilt, audit = construct(self.saved, self.bank["inputs"])
        for name, value in [
            ("verification.json", verification),
            ("reconstruction.json", rebuilt),
            ("libraries.json", libraries),
            ("construction_audit.json", audit),
        ]:
            write_json(self.out, name, value)
        replay, replay_evidence = self.replay(libraries)
        write_json(self.out, "replay.json", replay_evidence)
        metas = self.schedule["stage"]
        if self.args.smoke:
            # Full-budget small-scale calibration on all four development cells,
            # all three constructions and three fixed builds. Never admission.
            metas = [
                m
                | dict(
                    seeds=[
                        uniform.seed(
                            "smoke",
                            m["cell"],
                            m["build"],
                            m["repeat"],
                            k,
                        )
                        for k in range(8)
                    ]
                )
                for m in metas
                if m["build"] in (0, 11, 23)
            ]
        stage = self.jobs(metas, "stage0", libraries)
        gate = stage_gate(stage, self.batches["stage0"], replay)
        write_json(self.out, "stage_gate.json", gate)
        self.schedule["score"] = schedules(
            self.bank, gate["repeats"], tuple(gate["active_arms"])
        )["score"]
        write_json(self.out, "schedules.json", self.schedule)
        p = dict(
            admitted=not self.args.smoke and gate["admitted"],
            smoke=self.args.smoke,
            freeze=self.freeze,
            seed_audit=self.audit,
            verification=verification,
            reconstruction=rebuilt,
            construction_audit=audit,
            replay=replay_evidence,
            stage_gate=gate,
            bank_hash=digest(self.bank),
            libraries_hash=digest(libraries),
            stage_rows_hash=digest(stage),
            stage_timing=self.batches["stage0"],
            selected_schedule_hash=digest(self.schedule),
        )
        p["preparation_hash"] = digest(p)
        write_json(self.out, "preparation.json", p)
        print(json.dumps(gate), flush=True)
        if not self.args.smoke and not gate["admitted"]:
            raise ValueError(
                "four-arm four-repeat scoring projection exceeds approved 100-minute allowance"
            )

    def score(self):
        directory = Path(self.args.preparation)
        p = json.loads((directory / "preparation.json").read_text())
        if (
            not p.get("admitted")
            or p.get("smoke")
            or p["freeze"] != self.freeze
            or p["seed_audit"] != self.audit
            or p["preparation_hash"]
            != digest({k: v for k, v in p.items() if k != "preparation_hash"})
            or p["bank_hash"] != digest(self.bank)
            or not all(
                p[k]["passed"]
                for k in (
                    "verification",
                    "reconstruction",
                    "construction_audit",
                    "replay",
                )
            )
        ):
            raise ValueError("requires unchanged admitted production preparation")
        libraries = json.loads((directory / "libraries.json").read_text())
        if digest(libraries) != p["libraries_hash"]:
            raise ValueError("libraries changed")
        regenerated, rebuilt, audit = construct(self.saved, self.bank["inputs"])

        # Construction timings are measurements, not deterministic content.
        content = restart.deterministic

        if (
            content(regenerated) != content(libraries)
            or audit != p["construction_audit"]
            or not rebuilt["passed"]
        ):
            raise ValueError("frozen construction replay failed")
        metas = [
            {
                k: r[k]
                for k in (
                    "family",
                    "cell",
                    "arm",
                    "build",
                    "repeat",
                    "realization",
                    "seeds",
                )
            }
            for r in snapshot("replay.jsonl")
        ]
        replay = validate_rows(
            restart.jsonlines(directory / "replay.jsonl"), metas, self.saved
        )
        expected = {restart.key(r): r for r in snapshot("replay.jsonl")}
        if digest(replay) != p["replay"]["rows_hash"] or any(
            restart.deterministic(r) != restart.deterministic(expected[restart.key(r)])
            for r in replay
        ):
            raise ValueError("replay evidence changed")
        stage = validate_rows(
            restart.jsonlines(directory / "stage0.jsonl"),
            self.schedule["stage"],
            self.saved,
        )
        if (
            digest(stage) != p["stage_rows_hash"]
            or not math.isclose(
                sum(r["worker_seconds"] for r in stage),
                p["stage_timing"]["worker_seconds"],
                rel_tol=1e-12,
            )
            or stage_gate(stage, p["stage_timing"], replay) != p["stage_gate"]
            or not p["stage_gate"]["admitted"]
        ):
            raise ValueError("stage evidence changed")
        self.schedule["score"] = schedules(
            self.bank, p["stage_gate"]["repeats"], tuple(p["stage_gate"]["active_arms"])
        )["score"]
        if (
            digest(self.schedule) != p["selected_schedule_hash"]
            or json.loads((directory / "schedules.json").read_text()) != self.schedule
        ):
            raise ValueError("selected schedule changed")
        for name, value in [
            ("schedules.json", self.schedule),
            ("preparation.json", p),
            ("libraries.json", libraries),
            ("construction_audit.json", audit),
        ]:
            write_json(self.out, name, value)
        rows = self.jobs(self.schedule["score"], "search", libraries)
        from experiments.chem_tape.tree_uniform_report import report

        report(self.out, rows, libraries, self.bank, p, self.batches)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=2400)
    args = parser.parse_args()
    if (
        args.workers != 10
        or os.environ.get("RAYON_NUM_THREADS") != "1"
        or not 30 < args.deadline_seconds <= (2400 if args.prepare else 7200)
        or (args.smoke and not args.prepare)
        or (not args.prepare and not args.preparation)
    ):
        parser.error(
            "ten workers, RAYON_NUM_THREADS=1, bounded preparation or preparation-gated scoring required"
        )
    try:
        Runner(args).run()
    except (ValueError, TimeoutError) as error:
        out = Path(os.environ["RUN_DIR"])
        out.mkdir(parents=True, exist_ok=True)
        write_json(out, "infeasible.json", dict(task=TASK, reason=str(error)))
        raise


if __name__ == "__main__":
    main()
