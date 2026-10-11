"""1019: fixed source-free sum donors versus frozen TS donors on B/C."""

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

from experiments.chem_tape import tree_source_run as source
from experiments.chem_tape import tree_library_run as base
from experiments.chem_tape import tree_uniform_run as prior
from experiments.chem_tape import gate_sum_run as dg
from experiments.chem_tape import restart_gp_run as restart
from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.independent_input_run import method_hashes
from experiments.chem_tape.tree_gp_search import Tree, search
from experiments.chem_tape.tree_gp_validate import python_output
from experiments.chem_tape.tree_library import verify_entries

TASK = "2026-10-11-1019"
ARMS = ("R-tree", "R-TS", "R-hand")
DATA = Path(__file__).with_name("data") / "tree_hand_1019"


def snapshot(name):
    p = json.loads((DATA / "provenance.json").read_text())
    raw = gzip.decompress((DATA / (name + ".gz")).read_bytes())
    if hashlib.sha256(raw).hexdigest() != p["artifacts"][name]:
        raise ValueError("0833 archive changed: " + name)
    return (
        [json.loads(x) for x in raw.splitlines()]
        if name.endswith("jsonl")
        else json.loads(raw)
    )


def seed(domain, *parts):
    raw = json.dumps([TASK, domain, *parts], separators=(",", ":"), sort_keys=True)
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], "big") & (
        (1 << 63) - 1
    )


def hand_prior(alphabet):
    """Alphabet-only construction; multiplicity is the frozen draw law."""
    if alphabet != "v2_x4":
        raise ValueError("prior requires v2_x4")
    entries = []
    for group, prefixes, copies in (
        ("P", [(9, i, j) for i in range(4) for j in range(4) if i != j], 8),
        (
            "K",
            [p for i in range(4) for c in range(5, 9) for p in ((9, i, c), (9, c, i))],
            3,
        ),
    ):
        for prefix in prefixes:
            tree = Tree(prefix)
            entries.extend(
                [
                    dict(
                        prefix=list(prefix),
                        nodes=3,
                        compiled_length=len(tree.program),
                        donor_class=group,
                    )
                ]
                * copies
            )
    return entries


def schedules(gs):
    return {
        phase: [
            dict(
                family="GS",
                cell=c,
                arm=a,
                build=b,
                repeat=r,
                seeds=[seed(phase, c, b, r, k) for k in range(8)],
            )
            for c in prior.score_cells(gs)
            for b in range(builds)
            for r in range(repeats)
            for a in ARMS
        ]
        for phase, builds, repeats in (
            ("score", 24, 6),
            ("stage", 2, 1),
            ("smoke", 2, 1),
        )
    }


def seed_audit(schedule, saved, targets, gs):
    old = source.seed_audit(
        source.schedules(saved["banks.json"]["TS"], gs, targets["TS"]),
        saved,
        targets,
        gs,
    )
    historic = set()
    for audit in (old, snapshot("schedule_audit.json")):
        historic.update(audit.get("historical_seeds", []))
        historic.update(audit.get("reserved_probe_seeds", []))
        for ss in audit["published_seed_sets"].values():
            historic.update(ss)
    # source.seed_audit's union is summarized, not embedded: recover the complete
    # older union directly through the existing 0150 audit as well.
    a = base.seed_audit(base.schedules(saved["banks.json"]["DG"], targets["DG"]))
    historic.update(a["historical_seeds"])
    for audit in (
        dg.snapshot("schedule_audit.json"),
        prior.prior_run.snapshot("schedule_audit.json"),
        prior.snapshot("schedule_audit.json"),
        prior.seed_audit(prior.schedules(gs)),
    ):
        historic.update(audit.get("historical_seeds", []))
        historic.update(audit.get("reserved_probe_seeds", []))
        for ss in audit["published_seed_sets"].values():
            historic.update(ss)
    sets, paired = {}, True
    for phase, metas in schedule.items():
        uses = {}
        paired &= len({restart.key(m) for m in metas}) == len(metas)
        for m in metas:
            for k, s in enumerate(m["seeds"]):
                uses.setdefault(s, []).append((m, k))
        for records in uses.values():
            paired &= len(records) == 3 and {m["arm"] for m, _ in records} == set(ARMS)
            paired &= (
                len({(m["cell"], m["build"], m["repeat"], k) for m, k in records}) == 1
            )
        sets[phase] = set(uses)
    sets["bootstrap"] = {seed("bootstrap")}
    overlaps = {a + "_historic": sorted(ss & historic) for a, ss in sets.items()}
    for i, a in enumerate(sets):
        for b in list(sets)[i + 1 :]:
            overlaps[a + "_" + b] = sorted(sets[a] & sets[b])
    complete = schedule == schedules(gs)
    return dict(
        admitted=bool(complete and paired and not any(overlaps.values())),
        complete=complete,
        intended_pairing_valid=bool(paired),
        overlaps=overlaps,
        published_seed_sets={k: sorted(v) for k, v in sets.items()},
        historical_count=len(historic),
        historical_hash=digest(sorted(historic)),
        replay_exception="eight original 0024 jobs; validation only",
    )


def reviewed_methods():
    """Allow only the optional, RNG-free accounting observer in the old engine."""
    methods = method_hashes()
    path = "experiments/chem_tape/tree_gp_search.py"
    original = gzip.decompress(
        (DATA / "original_tree_gp_search.py.gz").read_bytes()
    ).decode()
    expected = original.replace(
        "donor_library=None):", "donor_library=None, donor_observer=None):"
    )
    expected = expected.replace(
        'stats["ordinary_donors"] += int(not library_draw)',
        'if library_draw and donor_observer is not None:\n                        donor_observer(donor, rejected)\n                    stats["ordinary_donors"] += int(not library_draw)',
    )
    if Path(path).read_text() != expected:
        raise ValueError("engine differs beyond reviewed accounting observer")
    old_hash = hashlib.sha256(original.encode()).hexdigest()
    if snapshot("method_freeze.json")["methods"][path] != old_hash:
        raise ValueError("observer's original engine is not the acquired engine")
    return methods, methods | {path: old_hash}


def reconstruct(saved):
    p, libs = snapshot("preparation.json"), snapshot("libraries.json")
    bank = saved["banks.json"]["TS"]
    schedule = snapshot("schedules.json")
    rows = source.validate_rows(
        snapshot("acquisition.jsonl"), schedule["source"], saved
    )
    if (
        not p["admitted"]
        or p["smoke"]
        or p["preparation_hash"]
        != digest({k: v for k, v in p.items() if k != "preparation_hash"})
        or digest(rows) != p["source_rows_hash"]
        or digest(libs) != p["libraries_hash"]
        or schedule
        != source.schedules(bank, saved["banks.json"]["GS"], load_saved()[1]["TS"])
        or snapshot("banks.json")["TS"] != bank
        or snapshot("banks.json")["GS"] != saved["banks.json"]["GS"]
    ):
        raise ValueError("0833 archived admission/provenance changed")
    rebuilt = source.build_libraries(rows, 24, bank)
    if restart.deterministic(rebuilt) != restart.deterministic(libs["TS"]):
        raise ValueError("0833 TS reconstruction mismatch")
    for old, new in zip(libs["TS"], rebuilt):
        for field in (
            "acquisition_evaluations",
            "acquisition_worker_seconds",
            "source_by_cell",
            "source_solves",
        ):
            if old[field] != new[field]:
                raise ValueError("0833 acquisition costs changed")
    return libs["TS"], dict(
        passed=True,
        builds=24,
        source_jobs=len(rows),
        failed_source_jobs=sum(not r["solved"] for r in rows),
        original_preparation_hash=p["preparation_hash"],
        libraries_hash=digest(libs["TS"]),
    )


def envelope(meta, saved, libs, cutoff=65536):
    if meta["arm"] not in ARMS and meta["arm"] != "R-tree":
        raise ValueError("unknown donor arm")
    e = restart.envelope(meta | dict(arm="R-tree"), saved, cutoff)
    e["meta"] = meta
    entries = (
        None
        if meta["arm"] == "R-tree"
        else (
            libs["hand"]
            if meta["arm"] == "R-hand"
            else libs["TS"][meta["build"]]["entries"]
        )
    )
    e["donors"] = (
        None if entries is None else [Tree(tuple(x["prefix"])) for x in entries]
    )
    return e


def execute(e):
    if e["meta"]["arm"] != "R-hand":
        return base.execute(e)
    # Identical restart wrapper; only the optional observer collects P/K counts.
    start, attempts = time.monotonic(), []
    for s in e["meta"]["seeds"]:
        a = restart.with_seed(e["first"], s)
        counts = {g: dict(draws=0, insertions=0, oversize=0) for g in ("P", "K")}

        def observe(donor, rejected):
            g = "P" if all(x < 4 for x in donor.prefix[1:]) else "K"
            counts[g]["draws"] += 1
            counts[g]["insertions"] += int(not rejected)
            counts[g]["oversize"] += int(rejected)

        tick = time.monotonic()
        row = (
            search(a["job"], donor_library=e["donors"], donor_observer=observe)
            | a["meta"]
        )
        row["worker_seconds"] = time.monotonic() - tick
        row["donor_classes"] = counts
        attempts.append(row)
        if row["solved"]:
            break
    elapsed = time.monotonic() - start
    return e["meta"] | dict(
        cap=8 * e["cutoff"],
        cutoff=e["cutoff"],
        pop_size=256,
        solved=attempts[-1]["solved"],
        solver=attempts[-1]["solver"],
        evaluations=sum(a["evaluations"] for a in attempts),
        worker_seconds=elapsed,
        attempts=attempts,
        attempt_count=len(attempts),
        scheduling_seconds=max(
            0.0, elapsed - sum(a["worker_seconds"] for a in attempts)
        ),
    )


def validate_rows(rows, metas, saved, cutoff=65536):
    rows = source.validate_rows(rows, metas, saved, cutoff)
    for row in rows:
        if row["arm"] != "R-hand":
            continue
        for attempt in row["attempts"]:
            counts = attempt["donor_classes"]
            for group in ("P", "K"):
                if (
                    counts[group]["draws"]
                    != counts[group]["insertions"] + counts[group]["oversize"]
                ):
                    raise ValueError("donor class accounting mismatch")
            for field, key in (
                ("draws", "library_draws"),
                ("insertions", "library_insertions"),
                ("oversize", "rejected_library"),
            ):
                if sum(c[field] for c in counts.values()) != attempt["operator"][key]:
                    raise ValueError("donor class totals mismatch")
    return rows


def stage_gate(rows, batch, elapsed):
    eff = min(10.0, batch["worker_seconds"] / batch["wall_seconds"])
    arms = {}
    for a, floor in zip(ARMS, (6.63, 2.40, 6.63)):
        rs = [r for r in rows if r["arm"] == a]
        mean = float(np.mean([r["worker_seconds"] for r in rs]))
        arms[a] = dict(
            jobs=len(rs),
            solves=sum(r["solved"] for r in rs),
            measured_mean_worker_seconds=mean,
            projected_mean_worker_seconds=max(floor, mean),
        )
    projected = (
        90
        + 1.3
        * 1728
        * sum(v["projected_mean_worker_seconds"] for v in arms.values())
        / eff
    )
    return dict(
        admitted=bool(projected <= 7200 and elapsed + 90 <= 1800),
        scoring_projected_seconds=projected,
        scoring_limit_seconds=7200,
        preparation_projected_seconds=elapsed + 90,
        preparation_limit_seconds=1800,
        effective_concurrency=eff,
        arms=arms,
        reserve=1.30,
        overhead_seconds=90,
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
        self.saved["banks.json"]["GS"] = self.gs
        self.schedule = schedules(self.gs)
        self.audit = seed_audit(self.schedule, self.saved, self.targets, self.gs)
        methods, pristine = reviewed_methods()
        self.freeze = dg.freeze(self.gs, self.schedule, pristine) | dict(
            task=TASK,
            methods=methods,
            archived_engine_hash=pristine["experiments/chem_tape/tree_gp_search.py"],
            targets=prior.score_cells(self.gs),
            arms=list(ARMS),
            repeats=6,
            prior_hash=digest(hand_prior("v2_x4")),
            archive=json.loads((DATA / "provenance.json").read_text()),
            disclosure="fixed development-informed sum prior; source-free at execution; B/C substitution only",
        )
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
            ("banks.json", {"TS": self.saved["banks.json"]["TS"], "GS": self.gs}),
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
                execute,
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

    def construct(self):
        verification = source.verify_banks(self.saved, self.targets, self.gs)
        ts, reconstruction = reconstruct(self.saved)
        tick = time.monotonic()
        hand = hand_prior("v2_x4")
        construction_seconds = time.monotonic() - tick
        tick = time.monotonic()
        verify_entries(hand, self.gs["inputs"])
        if any(
            [python_output(Tree(tuple(e["prefix"])), x) for x in self.gs["inputs"]]
            != [
                source.interpret(Tree(tuple(e["prefix"])), x) for x in self.gs["inputs"]
            ]
            for e in hand
        ):
            raise ValueError("hand Python evaluator mismatch")
        verification |= dict(
            hand_entries=192,
            hand_distinct=44,
            hand_class_counts={
                g: sum(e["donor_class"] == g for e in hand) for g in ("P", "K")
            },
        )
        for name, v in (
            ("verification.json", verification),
            ("reconstruction.json", reconstruction),
        ):
            write_json(self.out, name, v)
        return dict(TS=ts, hand=hand), dict(
            construction_seconds=construction_seconds,
            verification_seconds=time.monotonic() - tick,
        )

    def prepare(self):
        libs, overhead = self.construct()
        write_json(self.out, "libraries.json", libs)
        replay = self.replay()
        write_json(self.out, "replay.json", replay)
        phase = "smoke" if self.args.smoke else "stage"
        rows = self.jobs(
            self.schedule[phase], "stage0", libs, 2048 if self.args.smoke else 65536
        )
        elapsed = time.monotonic() - self.started
        gate = stage_gate(rows, self.batches["stage0"], elapsed)
        p = dict(
            admitted=bool(gate["admitted"] and not self.args.smoke),
            smoke=self.args.smoke,
            freeze=self.freeze,
            seed_audit=self.audit,
            replay=replay,
            stage_gate=gate,
            libraries_hash=digest(libs),
            stage_rows_hash=digest(rows),
            stage_elapsed_seconds=elapsed,
            stage_timing=self.batches["stage0"],
            hand_overhead=overhead,
        )
        p["preparation_hash"] = digest(p)
        write_json(self.out, "stage_gate.json", gate)
        write_json(self.out, "preparation.json", p)
        print(json.dumps(gate), flush=True)
        if not self.args.smoke and not gate["admitted"]:
            raise ValueError("approved timing envelope failed: " + json.dumps(gate))

    def validate_preparation(self):
        path = Path(self.args.preparation)
        p = json.loads((path / "preparation.json").read_text())
        if (
            not p.get("admitted")
            or p.get("smoke")
            or p["freeze"] != self.freeze
            or p["seed_audit"] != self.audit
            or p["preparation_hash"]
            != digest({k: v for k, v in p.items() if k != "preparation_hash"})
        ):
            raise ValueError("requires unchanged admitted production preparation")
        libs, _ = self.construct()
        archived = json.loads((path / "libraries.json").read_text())
        rows = validate_rows(
            restart.jsonlines(path / "stage0.jsonl"), self.schedule["stage"], self.saved
        )
        replay_rows = restart.jsonlines(path / "replay.jsonl")
        original = [
            json.loads(x)
            for x in gzip.decompress(
                (base.DATA / "replay.jsonl.gz").read_bytes()
            ).splitlines()
        ]
        metas = [
            {
                k: r[k]
                for k in ("family", "cell", "arm", "build", "repeat", "phase", "seeds")
            }
            for r in original
        ]
        replay_rows = source.validate_rows(replay_rows, metas, self.saved)
        by = {restart.key(r): r for r in original}
        if (
            libs != archived
            or digest(libs) != p["libraries_hash"]
            or digest(rows) != p["stage_rows_hash"]
            or stage_gate(rows, p["stage_timing"], p["stage_elapsed_seconds"])
            != p["stage_gate"]
            or not p["stage_gate"]["admitted"]
            or not p["replay"]["passed"]
            or digest(replay_rows) != p["replay"]["rows_hash"]
            or any(
                restart.deterministic(r) != restart.deterministic(by[restart.key(r)])
                for r in replay_rows
            )
        ):
            raise ValueError("production preparation evidence changed")
        return libs, p

    def score(self):
        libs, p = self.validate_preparation()
        for name, v in (("preparation.json", p), ("libraries.json", libs)):
            write_json(self.out, name, v)
        rows = self.jobs(self.schedule["score"], "search", libs)
        from experiments.chem_tape.tree_hand_report import report

        report(self.out, rows, libs, self.gs, p, self.batches)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--preparation")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--deadline-seconds", type=int, default=1800)
    args = parser.parse_args()
    if (
        args.workers != 10
        or os.environ.get("RAYON_NUM_THREADS") != "1"
        or not 30 < args.deadline_seconds <= (1800 if args.prepare else 7200)
        or (args.smoke and not args.prepare)
        or (not args.prepare and not args.preparation)
    ):
        parser.error(
            "requires Rayon=1, ten workers, bounded preparation or preparation-gated scoring"
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
