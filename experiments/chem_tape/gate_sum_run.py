"""0348: unchanged 0150 tree libraries on a frozen fresh gate-sum bank."""

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

from experiments.chem_tape import gate_sum_bank as bank_module
from experiments.chem_tape import tree_library_run as base
from experiments.chem_tape import restart_gp_run as restart
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.independent_input_run import method_hashes
from experiments.chem_tape.tree_library import extract, controls, verify_entries

TASK = "2026-10-11-0348"
DATA = Path(__file__).with_name("data") / "gate_sum_0348"
ARMS = base.ARMS
BOOTSTRAP_SEED = 34100200
SMOKE_SEEDS = set(range(34100000, 34100008))


def snapshot(name):
    provenance = json.loads((DATA / "provenance.json").read_text())
    raw = gzip.decompress((DATA / (name + ".gz")).read_bytes())
    if hashlib.sha256(raw).hexdigest() != provenance["artifacts"][name]:
        raise ValueError("frozen 0150/planning artifact changed: " + name)
    return (
        [json.loads(line) for line in raw.splitlines()]
        if name.endswith("jsonl")
        else json.loads(raw)
    )


def schedules(bank):
    result = {}
    for phase, cells, repeats, seed_base in [
        ("stage", bank["split"]["development"], 1, 34000000),
        ("score", bank["split"]["protected"], 4, 34200000),
    ]:
        result[phase] = [
            dict(
                family="GS",
                cell=c,
                arm=a,
                build=b,
                repeat=r,
                seeds=[seed_base + ci * 1000 + b * 32 + r * 8 + k for k in range(8)],
            )
            for ci, c in enumerate(cells)
            for b in range(24)
            for r in range(repeats)
            for a in ARMS
        ]
    return result


def seed_audit(schedule):
    old = snapshot("schedule_audit.json")
    historic = set(old["historical_seeds"])
    for seeds in old["published_seed_sets"].values():
        historic.update(seeds)
    # Include both discarded probe namespaces, including allocated but unfinished
    # long jobs; these used the same seeds and never count as confirmation.
    probe = snapshot("probe_rows.json")
    max_k = max(r["k"] for r in probe["rows"])
    probe_seeds = {
        base_seed + ci * 100000 + b * 100 + k
        for base_seed in (934800000, 934900000)
        for ci in range(2)
        for b in range(24)
        for k in range(max_k + 1)
    }
    historic |= probe_seeds
    sets, paired = {}, True
    for phase, metas in schedule.items():
        uses = {}
        if len({restart.key(m) for m in metas}) != len(metas):
            paired = False
        for m in metas:
            for k, s in enumerate(m["seeds"]):
                uses.setdefault(s, []).append((m, k))
        for entries in uses.values():
            paired &= (
                len(entries) == 3
                and {m["arm"] for m, _ in entries} == set(ARMS)
                and len({(m["cell"], m["build"], m["repeat"], k) for m, k in entries})
                == 1
            )
        sets[phase] = set(uses)
    sets.update(smoke=SMOKE_SEEDS, bootstrap={BOOTSTRAP_SEED})
    overlaps = {a + "_historic": sorted(s & historic) for a, s in sets.items()}
    for i, a in enumerate(sets):
        for b in list(sets)[i + 1 :]:
            overlaps[a + "_" + b] = sorted(sets[a] & sets[b])
    complete = {k: len(v) for k, v in schedule.items()} == dict(stage=288, score=5184)
    return dict(
        admitted=bool(paired and complete and not any(overlaps.values())),
        complete=complete,
        intended_pairing_valid=bool(paired),
        overlaps=overlaps,
        published_seed_sets={k: sorted(v) for k, v in sets.items()},
        historical_count=len(historic),
        historical_hash=digest(sorted(historic)),
        source_audit_hash=digest(old),
        probe_artifact_hash=digest(probe),
        reserved_probe_seeds=sorted(probe_seeds),
        replay_exception="eight saved 0024 jobs validation only",
        control_exception="rebuild the original 0150 R-size donors from their original seeds",
    )


def reconstruct(saved):
    """Failures and original measured acquisition costs survive reconstruction."""
    source = snapshot("acquisition.jsonl")
    libraries = snapshot("libraries.json")
    original_schedule = snapshot("schedules.json")
    p = snapshot("preparation.json")
    source = base.validate_rows(source, original_schedule["source"], saved)
    if (
        not p["admitted"]
        or p["smoke"]
        or digest(source) != p["source_rows_hash"]
        or digest(libraries) != p["libraries_hash"]
        or p["preparation_hash"]
        != digest({k: v for k, v in p.items() if k != "preparation_hash"})
        or len(libraries) != 24
        or [x["build"] for x in libraries] != list(range(24))
    ):
        raise ValueError("incomplete or changed 0150 acquisition")
    bank = saved["banks.json"]["DG"]
    evidence = []
    for b, lib in enumerate(libraries):
        cohort = [r for r in source if r["build"] == b]
        entries, seconds = extract(cohort, bank["split"]["source"])
        donors, control_seconds = controls(entries, lib["control_seed"])
        if (
            entries != lib["entries"]
            or donors != lib["controls"]
            or digest(cohort) != lib["source_rows_hash"]
            or len(cohort) != 32
            or lib["acquisition_evaluations"] != sum(r["evaluations"] for r in cohort)
            or lib["acquisition_worker_seconds"]
            != sum(r["worker_seconds"] for r in cohort)
            or lib["source_solves"] != sum(r["solved"] for r in cohort)
        ):
            raise ValueError(
                "source extraction or recorded donor reconstruction mismatch"
            )
        verified = verify_entries(entries + donors, bank["inputs"])
        evidence.append(
            dict(
                build=b,
                entries_hash=digest(entries),
                controls_hash=digest(donors),
                source_hash=digest(cohort),
                source_solves=lib["source_solves"],
                verification_count=verified,
                reconstruction_seconds=seconds,
                control_reconstruction_seconds=control_seconds,
            )
        )
    return libraries, dict(
        passed=True,
        builds=24,
        source_jobs=len(source),
        failed_source_jobs=sum(not r["solved"] for r in source),
        original_preparation_hash=p["preparation_hash"],
        libraries_hash=digest(libraries),
        per_build=evidence,
    )


def freeze(bank, schedule, methods):
    original = json.loads((DATA / "provenance.json").read_text())
    # Operator/search and source extraction implementations must remain the
    # reviewed 0150 method, including the release extension used to acquire it.
    core = [
        p
        for p in original["method_hashes"]
        if p.startswith(("src/folding_evolution/", "rust/src/"))
    ]
    core += [
        "experiments/chem_tape/tree_gp_search.py",
        "experiments/chem_tape/tree_library.py",
        "experiments/chem_tape/tree_library_run.py",
        "experiments/chem_tape/restart_gp_run.py",
        "experiments/chem_tape/tree_gp_run.py",
        "experiments/chem_tape/composition_search.py",
    ]
    for path in core:
        if methods[path] != original["method_hashes"][path]:
            raise ValueError("0150 method implementation changed: " + path)
    return dict(
        task=TASK,
        bank_hash=digest(restart.deterministic(bank)),
        targets=bank["split"]["protected"],
        methods=methods,
        schedule_hash=digest(schedule),
        artifacts=original["artifacts"],
        reference=json.loads((base.DATA / "provenance.json").read_text()),
        original_methods=original["method_hashes"],
        cutoff=65536,
        cap=524288,
        workers=10,
        rayon_threads=1,
        library_probability=0.5,
        disclosure="Two cells probed before freeze; development only. Deliberately selected new shape composed of familiar parts; no broad task-transfer or modularity inference.",
    )


def stage_gate(rows, batch):
    effective = min(10.0, batch["worker_seconds"] / batch["wall_seconds"])
    arms = {}
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]
        arms[a] = dict(
            jobs=len(rs),
            solves=sum(r["solved"] for r in rs),
            mean_evaluations=float(np.mean([r["evaluations"] for r in rs])),
            mean_worker_seconds=float(np.mean([r["worker_seconds"] for r in rs])),
            projected_protected_solves=1728 * sum(r["solved"] for r in rs) / len(rs),
        )
    projection = (
        90
        + 1.3 * 1728 * sum(v["mean_worker_seconds"] for v in arms.values()) / effective
    )
    return dict(
        admitted=projection <= 5400,
        arms=arms,
        effective_concurrency=effective,
        sustained_wall_seconds=batch["wall_seconds"],
        scoring_projected_seconds=projection,
        scoring_limit_seconds=5400,
        projection="actual restarted jobs at ten workers, all 24 libraries and four development cells; 30% reserve +90s; protected heterogeneity remains unmeasured",
    )


class Runner(base.Runner):
    def __init__(self, args):
        self.args = args
        self.deadline = time.monotonic() + args.deadline_seconds - 30
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        restart.require_fresh(self.out)
        self.saved, _ = load_saved()
        old_banks = list(self.saved["banks.json"].values())
        planning = snapshot("planning.json")
        if args.prepare:
            self.bank = bank_module.build(old_banks, planning, self.deadline)
        else:
            self.bank = json.loads((Path(args.preparation) / "bank.json").read_text())
            bank_module.validate_bank(self.bank, old_banks, planning)
        self.saved["banks.json"]["GS"] = self.bank
        self.targets = {"GS": self.bank["split"]["protected"]}
        self.schedule = schedules(self.bank)
        self.audit = seed_audit(self.schedule)
        self.freeze = freeze(self.bank, self.schedule, method_hashes())
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

    def prepare(self):
        verification = bank_module.verify(self.bank)
        write_json(self.out, "verification.json", verification)
        libraries, rebuilt = reconstruct(self.saved)
        write_json(self.out, "libraries.json", libraries)
        write_json(self.out, "reconstruction.json", rebuilt)
        replay = self.replay()
        write_json(self.out, "replay.json", replay)
        cutoff = 2048 if self.args.smoke else 65536
        stage = self.jobs(self.schedule["stage"], "stage0", libraries, cutoff)
        gate = stage_gate(stage, self.batches["stage0"])
        write_json(self.out, "stage_gate.json", gate)
        p = dict(
            admitted=not self.args.smoke and gate["admitted"],
            smoke=self.args.smoke,
            freeze=self.freeze,
            seed_audit=self.audit,
            verification=verification,
            reconstruction=rebuilt,
            replay=replay,
            stage_gate=gate,
            bank_hash=digest(self.bank),
            libraries_hash=digest(libraries),
            stage_rows_hash=digest(stage),
            stage_timing=self.batches["stage0"],
        )
        p["preparation_hash"] = digest(p)
        write_json(self.out, "preparation.json", p)
        print(json.dumps(gate), flush=True)
        if not self.args.smoke and not gate["admitted"]:
            raise ValueError("approved 90-minute scoring gate failed")

    def score(self):
        directory = Path(self.args.preparation)
        p = json.loads((directory / "preparation.json").read_text())
        if (
            not p.get("admitted")
            or p.get("smoke")
            or p.get("freeze") != self.freeze
            or p.get("seed_audit") != self.audit
            or not p["verification"]["passed"]
            or not p["replay"]["passed"]
            or not p["reconstruction"]["passed"]
            or not p["stage_gate"]["admitted"]
            or p["stage_gate"]["scoring_projected_seconds"] > 5400
            or p["preparation_hash"]
            != digest({k: v for k, v in p.items() if k != "preparation_hash"})
            or p["bank_hash"] != digest(self.bank)
        ):
            raise ValueError(
                "requires unchanged, fully admitted production preparation"
            )
        libraries = json.loads((directory / "libraries.json").read_text())
        original = snapshot("libraries.json")
        stage = base.validate_rows(
            restart.jsonlines(directory / "stage0.jsonl"),
            self.schedule["stage"],
            self.saved,
        )
        if (
            libraries != original
            or digest(libraries) != p["libraries_hash"]
            or digest(stage) != p["stage_rows_hash"]
            or not math.isclose(
                p["stage_timing"]["worker_seconds"],
                sum(r["worker_seconds"] for r in stage),
                rel_tol=1e-12,
            )
            or stage_gate(stage, p["stage_timing"]) != p["stage_gate"]
        ):
            raise ValueError("preparation/library/stage evidence changed")
        # Re-check the existing frozen source evidence; never use target outcomes
        # or target trees to reconstruct donors.
        reconstruct(self.saved)
        write_json(self.out, "preparation.json", p)
        write_json(self.out, "libraries.json", libraries)
        del stage
        rows = self.jobs(self.schedule["score"], "search", libraries)
        from experiments.chem_tape.gate_sum_report import report

        report(
            self.out, rows, libraries, self.bank, self.targets["GS"], p, self.batches
        )


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
        or not 30 < args.deadline_seconds <= (2400 if args.prepare else 5400)
        or (args.smoke and not args.prepare)
        or (not args.prepare and not args.preparation)
    ):
        parser.error(
            "RAYON_NUM_THREADS=1, ten workers, bounded preparation or preparation-gated scoring required"
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
