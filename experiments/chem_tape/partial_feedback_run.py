"""2116: accumulated partial-program feedback versus equal source allocation."""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import TRAINING, digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.partial_program_run import (
    Runner as PartialRunner,
    BASE as REPLAY_BASE,
    archive_diagnostics,
)
from experiments.chem_tape.solver_corpus_fit import (
    fit,
    partial_transition_counts,
    seed_for,
    validate_table,
)

BASE = 202610082116
ARMS = ("F", "O", "TF", "R", "G4", "C_exact")
DATA = Path(__file__).with_name("data") / "partial_feedback_2116"
REPLAY_SHA = "b935b2894cb0d7e14353fd8b60344aa39a64b46e44f666fd6cb2874bd87e263b"


def source_fingerprint(row):
    """All scientific search fields and both archives, excluding timing/metadata."""
    excluded = {
        "seconds",
        "decode_seconds",
        "budget_seconds",
        "worker_seconds",
        "archive_verification_seconds",
        "phase",
        "family",
        "corpus",
        "round",
    }
    return digest({k: v for k, v in row.items() if k not in excluded})


def replay_source():
    raw = (DATA / "replay.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != REPLAY_SHA:
        raise ValueError("1831 replay manifest hash mismatch")
    return json.loads(raw)


def check_replay(rows, counts, fitted, expected):
    fingerprints = {str(r["seed"]): source_fingerprint(r) for r in rows}
    if fingerprints != expected["sources"]:
        raise ValueError("round-one source/archive replay mismatch")
    hashes = {a: validate_table(fitted[a]) for a in ("C", "T")}
    if (
        digest(counts.tolist()) != expected["counts_hash"]
        or hashes != expected["tables"]
    ):
        raise ValueError("round-one count/table replay mismatch")
    return dict(
        passed=True, sources=len(rows), source_hash=digest(fingerprints), tables=hashes
    )


def roster(base=BASE, nc=8, collect_n=32, fresh_n=16, arms=ARMS):
    rows = []
    for k in range(nc):
        for family, cells in TRAINING.items():
            for round_, count, acquisition_arms in (
                (1, 32, ("G4",)),
                (2, collect_n, ("F", "TF", "O")),
                (3, collect_n, ("F", "TF", "O")),
                (4, fresh_n, arms),
            ):
                for c, cid in enumerate(cells):
                    for s in range(count):
                        for arm in acquisition_arms:
                            rows.append(
                                dict(
                                    phase="training" if round_ == 4 else "collection",
                                    round=round_,
                                    family=family,
                                    corpus=f"{family}{k + 1}",
                                    cell=cid,
                                    arm=arm,
                                    seed=seed_for(
                                        0 if round_ == 1 else round_,
                                        family,
                                        k,
                                        c,
                                        s,
                                        REPLAY_BASE if round_ == 1 else base,
                                    ),
                                )
                            )
    groups = {}
    for row in rows:
        groups.setdefault(row["seed"], []).append(row)
    for group in groups.values():
        r = group[0]
        expected = (
            ("G4",)
            if r["round"] == 1
            else arms
            if r["round"] == 4
            else ("F", "TF", "O")
        )
        if len(group) != len(expected) or {x["arm"] for x in group} != set(expected):
            raise ValueError("seed collision/incomplete pairing")
        if any(
            {k: v for k, v in x.items() if k != "arm"}
            != {k: v for k, v in r.items() if k != "arm"}
            for x in group
        ):
            raise ValueError("seed collision outside paired arm")
    return rows


class Runner(PartialRunner):
    # Reuse the reviewed streaming search-budget, table-hash and paired-case checks.
    def __init__(self, args):
        super().__init__(args)
        self.arms = ARMS[:-1] if args.omit_exact else ARMS
        self.nc, self.collect_n, self.fresh_n = (1, 4, 4) if args.smoke else (8, 32, 16)
        self.base = BASE + (100000000 if args.smoke else 0)
        self.schedule = roster(
            self.base, self.nc, self.collect_n, self.fresh_n, self.arms
        )
        self.replay_manifest = replay_source()
        self.replay_checks = {}
        if (
            self.replay_manifest["bank_sha256"] != self.config["method"]["bank_sha256"]
            or self.replay_manifest["g4_hash"] != self.config["method"]["g4_hash"]
        ):
            raise ValueError("round-one bank/G4 mismatch")
        self.config.update(
            task="2026-10-08-2116",
            seed_base=self.base,
            nc=self.nc,
            collect_n=self.collect_n,
            fresh_n=self.fresh_n,
            arms=list(self.arms),
            replay_manifest_sha256=REPLAY_SHA,
        )
        method = self.config["method"]
        method.update(
            arms=list(self.arms),
            source_empty_cell="round1 error; later round adds zero, retain earlier sources",
            weighting="pool equally weighted contributing sources across rounds; rescale cell to1600",
            endpoint="exp(mean_lineage(mean_cell_seed(log(cost_O)-log(cost_F))))",
            worthwhile_margin=1.15,
            prefix="all16 independent lineages required; no partial-prefix decision",
            decision_precedence=[
                "UB<1: degradation",
                "UB<1.15: small gain/prefer O",
                "LB>1 and point>=1.15: provisional adoption F",
                "LB>1 and point<1.15: resolved gain/prefer O at estimate",
                "otherwise unresolved",
            ],
            replay_seed_base=REPLAY_BASE,
            fresh_phases=[2, 3, 4],
            acquisition="3 rounds,32 sources/cell/round; F uses C1,C2; TF uses T1,T2; O uses G4",
        )
        for name in ("partial_feedback_run.py", "partial_feedback_report.py"):
            method["code_hashes"][name] = hashlib.sha256(
                Path(__file__).with_name(name).read_bytes()
            ).hexdigest()
        self.config["method_hash"] = digest(method)
        for name, data in (
            ("config.json", self.config),
            ("schedule.json", self.schedule),
        ):
            write_json(self.out, name, data)
        self.save_state()

    def envelope(self, row):
        job, meta = super().envelope(row)
        meta["round"] = row["round"]
        if row["phase"] == "collection" and row["arm"] != "G4":
            record = self.corpora[row["corpus"]]
            table = (
                self.g4
                if row["arm"] == "O"
                else record["rounds"][str(row["round"] - 1)][row["arm"]]["table"]
            )
            job = job[:2] + (table,) + job[3:]
        return job, meta

    def collect(self, tid):
        record = dict(family=tid[:2], index=int(tid[2:]) - 1, rounds={}, tables={})
        self.corpora[tid] = record
        pooled = {}
        for round_ in (1, 2, 3):
            rows = self.jobs(
                [
                    r
                    for r in self.schedule
                    if r["phase"] == "collection"
                    and r["corpus"] == tid
                    and r["round"] == round_
                ],
                f"collection:{tid}:r{round_}",
            )
            # Preserve legacy summation order for bit-exact round-one counts.
            # New rounds use seed order, so worker scheduling cannot change fits.
            if round_ == 1:
                by_seed = {str(r["seed"]): r for r in rows}
                rows = [
                    by_seed[s] for s in self.replay_manifest["corpora"][tid]["sources"]
                ]
            else:
                rows.sort(key=lambda r: (r["seed"], r["arm"]))
            record["rounds"][str(round_)] = {}
            for arm in ("F", "TF", "O"):
                new = rows if round_ == 1 else [r for r in rows if r["arm"] == arm]
                if round_ == 1:
                    pooled[arm] = list(new)
                else:
                    pooled[arm].extend(new)
                tick = time.monotonic()
                counts, yields = partial_transition_counts(
                    pooled[arm], TRAINING[tid[:2]], "S"
                )
                # O is fitted only after its final batch; first round supplies common C1/T1.
                fitted, fit_diag = (
                    fit(counts) if arm != "O" or round_ in (1, 3) else (None, None)
                )
                diagnostics = archive_diagnostics(new, "S")
                for cid, d in diagnostics.items():
                    cell_rows = [r for r in new if r["cell"] == cid]
                    d.update(
                        solved_sources=sum(r["solved"] for r in cell_rows),
                        actual_evaluations=sum(r["evaluations"] for r in cell_rows),
                        allocated_evaluations=len(cell_rows) * 65536,
                    )
                entry = dict(
                    diagnostics=diagnostics,
                    contributing_sources_pooled=yields,
                    counts=counts.tolist(),
                    counts_hash=digest(counts.tolist()),
                    fit=fit_diag,
                    fit_seconds=time.monotonic() - tick,
                    collection_evaluations=sum(r["evaluations"] for r in new),
                    verification_seconds=sum(
                        r["archive_verification_seconds"] for r in new
                    ),
                )
                if fitted is not None:
                    table = fitted["T" if arm == "TF" else "C"]
                    q = np.diff(table, prepend=0, axis=1) / 24000
                    entry.update(
                        table=table.tolist(),
                        table_hash=validate_table(table),
                        row_entropy=(-np.sum(q * np.log(q), axis=1)).tolist(),
                    )
                    record["tables"][arm] = entry["table"]
                if round_ == 1 and arm == "F":
                    self.replay_checks[tid] = check_replay(
                        new, counts, fitted, self.replay_manifest["corpora"][tid]
                    )
                    record["tables"]["R"] = entry["table"]
                    record["tables"]["C_exact"] = self.saved["corpora.json"][tid][
                        "tables"
                    ]["C"]
                record["rounds"][str(round_)][arm] = entry
            record["table_hashes"] = {
                a: validate_table(t) for a, t in record["tables"].items()
            }
            self.save_state()
            print(
                json.dumps(
                    dict(
                        stage="round_complete",
                        corpus=tid,
                        round=round_,
                        elapsed=time.monotonic() - self.started,
                    )
                ),
                flush=True,
            )

    def save_state(self):
        super().save_state()
        if hasattr(self, "replay_checks"):
            write_json(self.out, "replay.json", self.replay_checks)

    def run(self):
        self.pool = mp.get_context("spawn").Pool(self.args.workers)
        try:
            for pair in self.config["pair_order"]:
                for tid in pair:
                    self.collect(tid)
                self.jobs(
                    [
                        r
                        for r in self.schedule
                        if r["phase"] == "training" and r["corpus"] in pair
                    ],
                    f"training:{pair[0]}+{pair[1]}",
                )
                self.completed_pairs += 1
                self.save_state()
        except TimeoutError as error:
            self.stop_kind, self.stop_reason = "timeout", str(error)
        except Exception as error:
            self.stop_kind, self.stop_reason = (
                "error",
                f"{type(error).__name__}: {error}",
            )
        finally:
            self.pool.terminate()
            self.pool.join()
        self.validation.update(
            passed=self.stop_kind is None,
            completed_pairs=self.completed_pairs,
            full_roster_complete=self.completed_pairs == self.nc,
            replay_lineages=len(self.replay_checks),
        )
        self.save_state()
        from experiments.chem_tape.partial_feedback_report import (
            make_report,
            save_report,
        )

        self.timings["orchestration_elapsed"] = dict(
            wall_seconds=time.monotonic() - self.started
        )
        tick = time.monotonic()
        report = make_report(
            self.rows,
            self.corpora,
            self.config,
            self.completed_pairs,
            self.stop_kind,
            self.stop_reason,
            self.timings,
        )
        save_report(self.out, report, self.rows)
        self.timings["reporting"] = dict(wall_seconds=time.monotonic() - tick)
        self.timings["total"] = dict(wall_seconds=time.monotonic() - self.started)
        write_json(self.out, "timing.json", self.timings)
        return int(self.stop_kind is not None)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--deadline-seconds", type=int, default=17880)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--omit-exact", action="store_true")
    args = ap.parse_args()
    if args.workers < 1 or args.deadline_seconds <= 120:
        ap.error("positive workers and deadline above120 required")
    return Runner(args).run()


if __name__ == "__main__":
    raise SystemExit(main())
