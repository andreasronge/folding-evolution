"""0833: unchanged tree-library acquisition from TS, B/C and native scoring."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import gate_sum_run as dg
from experiments.chem_tape import tree_library_run as base
from experiments.chem_tape import tree_uniform_run as prior
from experiments.chem_tape import restart_gp_run as restart
from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.independent_input_bank import ALPHABET
from experiments.chem_tape.independent_input_run import method_hashes
from experiments.chem_tape.tree_gp_search import Tree, from_postfix, interpret
from experiments.chem_tape.tree_gp_validate import python_output
from experiments.chem_tape.tree_library import extract, controls, verify_entries

TASK = "2026-10-11-0833"
ARMS = ("R-tree", "R-TS", "R-DG", "R-sizeTS")
NATIVE_ARMS = ARMS[:3]


def seed(domain, *parts):
    raw = json.dumps([TASK, domain, *parts], separators=(",", ":"), sort_keys=True)
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], "big") & (
        (1 << 63) - 1
    )


def schedules(ts, gs, targets):
    result = {}
    for phase, family, cells, builds, repeats, arms in (
        ("source", "TS", ts["split"]["source"], 24, 8, ("R-tree",)),
        ("stage_source", "TS", ts["split"]["source"], 2, 8, ("R-tree",)),
        ("gate", "GS", prior.score_cells(gs), 24, 6, ARMS),
        ("native", "TS", targets, 24, 4, NATIVE_ARMS),
        ("stage_gate", "GS", prior.score_cells(gs), 2, 1, ARMS),
        ("stage_native", "TS", targets, 2, 1, NATIVE_ARMS),
    ):
        result[phase] = [
            dict(
                family=family,
                cell=c,
                arm=a,
                build=b,
                repeat=r,
                seeds=[seed(phase, c, b, r, k) for k in range(8)],
            )
            for c in cells
            for b in range(builds)
            for r in range(repeats)
            for a in arms
        ]
    return result


def seed_audit(schedule, saved, targets, gs):
    audits = [
        base.seed_audit(base.schedules(saved["banks.json"]["DG"], targets["DG"])),
        dg.snapshot("schedule_audit.json"),
        prior.prior_run.snapshot("schedule_audit.json"),
        prior.snapshot("schedule_audit.json"),
        prior.seed_audit(prior.schedules(gs)),
    ]
    historic = set()
    for a in audits:
        historic.update(a.get("historical_seeds", []))
        historic.update(a.get("reserved_probe_seeds", []))
        for values in a["published_seed_sets"].values():
            historic.update(values)
    sets, paired = {}, True
    for phase, metas in schedule.items():
        uses = {}
        paired &= len({restart.key(m) for m in metas}) == len(metas)
        for m in metas:
            for k, s in enumerate(m["seeds"]):
                uses.setdefault(s, []).append((m, k))
        expected = set(
            ARMS
            if phase in ("gate", "stage_gate")
            else NATIVE_ARMS
            if phase in ("native", "stage_native")
            else ("R-tree",)
        )
        for records in uses.values():
            paired &= (
                len(records) == len(expected)
                and {m["arm"] for m, _ in records} == expected
                and len(
                    {
                        (m["family"], m["cell"], m["build"], m["repeat"], k)
                        for m, k in records
                    }
                )
                == 1
            )
        sets[phase] = set(uses)
    sets["control"] = {seed("control", b) for b in range(24)}
    sets["stage_control"] = {seed("stage_control", b) for b in range(2)}
    sets["bootstrap"] = {seed("bootstrap")}
    overlaps = {a + "_historic": sorted(v & historic) for a, v in sets.items()}
    for i, a in enumerate(sets):
        for b in list(sets)[i + 1 :]:
            overlaps[a + "_" + b] = sorted(sets[a] & sets[b])
    complete = schedule == schedules(saved["banks.json"]["TS"], gs, targets["TS"])
    return dict(
        admitted=bool(paired and complete and not any(overlaps.values())),
        complete=complete,
        intended_pairing_valid=bool(paired),
        overlaps=overlaps,
        published_seed_sets={k: sorted(v) for k, v in sets.items()},
        historical_count=len(historic),
        historical_hash=digest(sorted(historic)),
        replay_exception="eight saved 0150 off-path fixtures, validation only",
        control_exception="archived DG controls reconstructed on original seeds",
        rule="SHA256 canonical JSON [task, domain, parts]; first eight bytes, 63-bit mask",
    )


def verify_banks(saved, targets, gs):
    old = [saved["banks.json"][f] for f in ("DG", "TS")]
    dg.bank_module.validate_bank(gs, old, dg.snapshot("planning.json"))
    evidence = dg.bank_module.verify(gs)
    ts = saved["banks.json"]["TS"]
    source, native = ts["split"]["source"], targets["TS"]
    if len(source) != 4 or len(native) != 8 or set(source) & set(native):
        raise ValueError("TS source/native roster changed or overlaps")
    by = {c["id"]: c for c in ts["screen"]["cells"]}
    checked = []
    for cid in source + native:
        c = by[cid]
        t = from_postfix(c["canonical"])
        if (
            list(t.program) != c["canonical"]
            or len(t.program) > 32
            or [interpret(t, x) for x in ts["inputs"]] != c["labels"]
            or [python_output(t, x) for x in ts["inputs"]] != c["labels"]
            or outputs([t.program], ts["inputs"], ALPHABET)[0].tolist() != c["labels"]
        ):
            raise ValueError("canonical TS interpreter/Python/VM mismatch")
        checked.append(cid)
    source_labels = {digest(by[c]["labels"]) for c in source}
    destination_labels = {digest(by[c]["labels"]) for c in native}
    destination_labels |= {
        digest(c["labels"])
        for c in gs["screen"]["cells"]
        if c["id"] in prior.score_cells(gs)
    }
    if source_labels & destination_labels:
        raise ValueError("source/target semantic overlap")
    return dict(
        passed=True,
        TS_canonical_cells=checked,
        GS=evidence,
        source_target_separation=True,
    )


def build_libraries(rows, count, bank, stage=False):
    result = []
    for b in range(count):
        cohort = [r for r in rows if r["build"] == b]
        if len(cohort) != 32 or any(r["family"] != "TS" for r in cohort):
            raise ValueError("requires exactly 32 TS-source jobs per build")
        entries, seconds = extract(cohort, bank["split"]["source"])
        control_seed = seed("stage_control" if stage else "control", b)
        control, control_seconds = controls(entries, control_seed)
        tick = time.monotonic()
        verified = verify_entries(entries + control, bank["inputs"])
        result.append(
            dict(
                build=b,
                entries=entries,
                controls=control,
                control_seed=control_seed,
                source_rows_hash=digest(cohort),
                source_solves=sum(r["solved"] for r in cohort),
                source_by_cell={
                    c: dict(
                        jobs=len(rs),
                        solves=sum(r["solved"] for r in rs),
                        evaluations=sum(r["evaluations"] for r in rs),
                        worker_seconds=sum(r["worker_seconds"] for r in rs),
                    )
                    for c in bank["split"]["source"]
                    for rs in [[r for r in cohort if r["cell"] == c]]
                },
                acquisition_evaluations=sum(r["evaluations"] for r in cohort),
                acquisition_worker_seconds=sum(r["worker_seconds"] for r in cohort),
                extraction_seconds=seconds,
                control_seconds=control_seconds,
                verification_seconds=time.monotonic() - tick,
                verified_entries=verified,
            )
        )
    return result


def envelope(meta, saved, libraries, cutoff=65536):
    if meta["arm"] not in ARMS:
        raise ValueError("unknown donor arm")
    e = restart.envelope(meta | dict(arm="R-tree"), saved, cutoff)
    e["meta"] = meta
    entries = None
    if meta["arm"] != "R-tree":
        owner = "DG" if meta["arm"] == "R-DG" else "TS"
        field = "controls" if meta["arm"] == "R-sizeTS" else "entries"
        entries = libraries[owner][meta["build"]][field]
    e["donors"] = (
        None if entries is None else [Tree(tuple(x["prefix"])) for x in entries]
    )
    return e


def validate_rows(rows, metas, saved, cutoff=65536):
    rows = base.validate_rows(rows, metas, saved, cutoff)
    pairs = {}
    for r in rows:
        for a in r["attempts"]:
            key = r["family"], r["cell"], r["build"], r["repeat"], a["seed"]
            value = a["initial_tokens_hash"], a["training_indices"]
            if key in pairs and pairs[key] != value:
                raise ValueError("paired initialization/cases changed")
            pairs[key] = value
    return rows


def stage_gate(source, stages, batches, libraries, elapsed):
    source_eff = min(
        10.0,
        batches["stage_source"]["worker_seconds"]
        / batches["stage_source"]["wall_seconds"],
    )
    source_mean = float(np.mean([r["worker_seconds"] for r in source]))
    overhead = np.mean(
        [
            sum(
                lib[k]
                for k in (
                    "extraction_seconds",
                    "control_seconds",
                    "verification_seconds",
                )
            )
            for lib in libraries["TS"]
        ]
    )
    prep = (
        elapsed + 90 + 1.3 * (768 * max(0.49, source_mean) / source_eff + 24 * overhead)
    )
    scoring, arms, concurrency = 90.0, {}, {}
    for phase, n in (("stage_gate", 1728), ("stage_native", 768)):
        batch = batches[phase]
        eff = min(10.0, batch["worker_seconds"] / batch["wall_seconds"])
        concurrency[phase] = eff
        arms[phase] = {}
        for a in ARMS if phase == "stage_gate" else NATIVE_ARMS:
            rs = [r for r in stages[phase] if r["arm"] == a]
            mean = float(np.mean([r["worker_seconds"] for r in rs]))
            floor = (2.37 if a == "R-DG" else 6.48) if phase == "stage_gate" else 0.49
            arms[phase][a] = dict(
                jobs=len(rs),
                solves=sum(r["solved"] for r in rs),
                measured_mean_worker_seconds=mean,
                projected_mean_worker_seconds=max(floor, mean),
                mean_evaluations=float(np.mean([r["evaluations"] for r in rs])),
            )
            scoring += 1.3 * n * max(floor, mean) / eff
    return dict(
        admitted=bool(prep <= 2700 and scoring <= 9000),
        preparation_projected_seconds=float(prep),
        scoring_projected_seconds=float(scoring),
        preparation_limit_seconds=2700,
        scoring_limit_seconds=9000,
        source_mean_worker_seconds=source_mean,
        source_effective_concurrency=source_eff,
        source_by_cell={
            c: dict(
                jobs=len(rs),
                solves=sum(r["solved"] for r in rs),
                mean_evaluations=float(np.mean([r["evaluations"] for r in rs])),
                mean_worker_seconds=float(np.mean([r["worker_seconds"] for r in rs])),
            )
            for c in sorted({r["cell"] for r in source})
            for rs in [[r for r in source if r["cell"] == c]]
        },
        stage_elapsed_seconds=elapsed,
        arms=arms,
        effective_concurrency=concurrency,
        library_yields=[len(x["entries"]) for x in libraries["TS"]],
        projection="actual source and destination calibration; historical timing floors; 30% reserve +90s; fixed full grid, timing only",
    )


class Runner(base.Runner):
    def __init__(self, args):
        self.args = args
        self.started = time.monotonic()
        self.deadline = self.started + args.deadline_seconds - 30
        self.out = Path(os.environ["RUN_DIR"])
        self.out.mkdir(parents=True, exist_ok=True)
        restart.require_fresh(self.out)
        self.saved, self.targets = load_saved()
        self.gs = prior.prior_run.snapshot("bank.json")
        self.bank = self.saved["banks.json"]["TS"]
        self.schedule = schedules(self.bank, self.gs, self.targets["TS"])
        self.audit = seed_audit(self.schedule, self.saved, self.targets, self.gs)
        self.freeze = dg.freeze(self.gs, self.schedule, method_hashes()) | dict(
            task=TASK,
            TS_bank_hash=digest(self.bank),
            TS_sources=self.bank["split"]["source"],
            targets=dict(GS=prior.score_cells(self.gs), TS=self.targets["TS"]),
            disclosure="two development destinations, no fresh-bank transfer claim",
        )
        self.saved["banks.json"]["GS"] = self.gs
        self.batches = {}
        for name, v in (
            (
                "config.json",
                dict(
                    arguments=vars(args),
                    git_commit=subprocess.check_output(
                        ["git", "rev-parse", "HEAD"], text=True
                    ).strip(),
                ),
            ),
            ("banks.json", {"TS": self.bank, "GS": self.gs}),
            ("method_freeze.json", self.freeze),
            ("schedule_audit.json", self.audit),
            ("schedules.json", self.schedule),
        ):
            write_json(self.out, name, v)
        if not self.audit["admitted"]:
            raise ValueError("seed audit failed")

    def jobs(self, metas, name, libraries=None, cutoff=65536):
        rows, tick = [], time.monotonic()
        with (self.out / (name + ".jsonl")).open("w", buffering=1) as stream:

            def save(row):
                rows.append(row)
                stream.write(json.dumps(row, allow_nan=False) + "\n")
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
            wall_seconds=time.monotonic() - tick,
            worker_seconds=sum(r["worker_seconds"] for r in rows),
        )
        write_json(self.out, "timing.json", self.batches)
        return validate_rows(rows, metas, self.saved, cutoff)

    def prepare(self):
        verification = verify_banks(self.saved, self.targets, self.gs)
        write_json(self.out, "verification.json", verification)
        dlibs, reconstruction = dg.reconstruct(self.saved)
        write_json(self.out, "reconstruction.json", reconstruction)
        replay = self.replay()
        write_json(self.out, "replay.json", replay)
        source = self.jobs(self.schedule["stage_source"], "stage_source")
        libs = dict(TS=build_libraries(source, 2, self.bank, True), DG=dlibs)
        write_json(self.out, "stage_libraries.json", libs)
        stages = {
            p: self.jobs(self.schedule[p], p, libs)
            for p in ("stage_gate", "stage_native")
        }
        elapsed = time.monotonic() - self.started
        gate = stage_gate(source, stages, self.batches, libs, elapsed)
        write_json(self.out, "stage_gate.json", gate)
        print(json.dumps(gate), flush=True)
        p = dict(
            admitted=False,
            smoke=self.args.smoke,
            freeze=self.freeze,
            seed_audit=self.audit,
            verification=verification,
            reconstruction=reconstruction,
            replay=replay,
            stage_gate=gate,
            stage_elapsed_seconds=elapsed,
            stage_timing=dict(self.batches),
            stage_libraries_hash=digest(libs),
            stage_hashes={"stage_source": digest(source)}
            | {k: digest(v) for k, v in stages.items()},
        )
        if gate["admitted"] and not self.args.smoke:
            rows = self.jobs(self.schedule["source"], "acquisition")
            libs["TS"] = build_libraries(rows, 24, self.bank)
            p |= dict(
                admitted=True,
                libraries_hash=digest(libs),
                source_rows_hash=digest(rows),
            )
            write_json(self.out, "libraries.json", libs)
        p["preparation_hash"] = digest(p)
        write_json(self.out, "preparation.json", p)
        if not gate["admitted"]:
            raise ValueError("approved timing envelope failed: " + json.dumps(gate))

    def score(self):
        path = Path(self.args.preparation)
        p = json.loads((path / "preparation.json").read_text())
        if (
            not p.get("admitted")
            or p.get("smoke")
            or p.get("freeze") != self.freeze
            or p.get("seed_audit") != self.audit
            or p.get("preparation_hash")
            != digest({k: v for k, v in p.items() if k != "preparation_hash"})
            or not all(
                p[k]["passed"] for k in ("verification", "reconstruction", "replay")
            )
            or not p["stage_gate"]["admitted"]
        ):
            raise ValueError("requires unchanged admitted production preparation")
        libs = json.loads((path / "libraries.json").read_text())
        source = validate_rows(
            restart.jsonlines(path / "acquisition.jsonl"),
            self.schedule["source"],
            self.saved,
        )
        rebuilt = build_libraries(source, 24, self.bank)
        dlibs, _ = dg.reconstruct(self.saved)
        if (
            digest(source) != p["source_rows_hash"]
            or digest(libs) != p["libraries_hash"]
            or restart.deterministic(libs)
            != restart.deterministic(dict(TS=rebuilt, DG=dlibs))
        ):
            raise ValueError("frozen source-only library reconstruction failed")
        if libs["DG"] != dlibs or any(
            libs["TS"][b]["acquisition_worker_seconds"]
            != rebuilt[b]["acquisition_worker_seconds"]
            or libs["TS"][b]["source_by_cell"] != rebuilt[b]["source_by_cell"]
            for b in range(24)
        ):
            raise ValueError("recorded acquisition costs changed")
        verify_banks(self.saved, self.targets, self.gs)
        src = validate_rows(
            restart.jsonlines(path / "stage_source.jsonl"),
            self.schedule["stage_source"],
            self.saved,
        )
        stages = {
            k: validate_rows(
                restart.jsonlines(path / (k + ".jsonl")), self.schedule[k], self.saved
            )
            for k in ("stage_gate", "stage_native")
        }
        slibs = json.loads((path / "stage_libraries.json").read_text())
        stage_rebuilt = dict(TS=build_libraries(src, 2, self.bank, True), DG=dlibs)
        if (
            p["stage_hashes"]
            != {"stage_source": digest(src)} | {k: digest(v) for k, v in stages.items()}
            or digest(slibs) != p["stage_libraries_hash"]
            or restart.deterministic(slibs) != restart.deterministic(stage_rebuilt)
            or stage_gate(
                src, stages, p["stage_timing"], slibs, p["stage_elapsed_seconds"]
            )
            != p["stage_gate"]
        ):
            raise ValueError("calibration evidence changed")
        # The 0150 replay fixture lives in base.DATA, not the DG acquisition archive.
        import gzip

        raw = gzip.decompress((base.DATA / "replay.jsonl.gz").read_bytes())
        if hashlib.sha256(raw).hexdigest() != self.freeze["reference"]["replay_sha256"]:
            raise ValueError("off-path replay fixture changed")
        original = [json.loads(line) for line in raw.splitlines()]
        replay_metas = [
            {
                k: r[k]
                for k in ("family", "cell", "arm", "build", "repeat", "phase", "seeds")
            }
            for r in original
        ]
        replay_rows = validate_rows(
            restart.jsonlines(path / "replay.jsonl"), replay_metas, self.saved
        )
        expected = {restart.key(r): r for r in original}
        if digest(replay_rows) != p["replay"]["rows_hash"] or any(
            restart.deterministic(r) != restart.deterministic(expected[restart.key(r)])
            for r in replay_rows
        ):
            raise ValueError("off-path replay evidence changed")
        for name, v in (("preparation.json", p), ("libraries.json", libs)):
            write_json(self.out, name, v)
        rows = self.jobs(
            self.schedule["gate"] + self.schedule["native"], "search", libs
        )
        from experiments.chem_tape.tree_source_report import report

        report(self.out, rows, libs, self.freeze["targets"], p, self.batches)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=2700)
    args = parser.parse_args()
    if (
        args.workers != 10
        or os.environ.get("RAYON_NUM_THREADS") != "1"
        or not 30 < args.deadline_seconds <= (2700 if args.prepare else 9000)
        or (args.smoke and not args.prepare)
        or (not args.prepare and not args.preparation)
    ):
        parser.error(
            "requires Rayon=1, ten workers and bounded preparation or preparation-gated scoring"
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
