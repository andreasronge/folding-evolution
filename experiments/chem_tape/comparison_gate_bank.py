"""Comparison-gate-v1: bounded semantic screen and performance-blind 4+4 split.

Canonicals and screen witnesses are bank validation data only. Searches receive
only training ids and labels, via load_training().
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import os
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for, screen_domain
from experiments.chem_tape.composition_bank import TA
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.four_reducer_bank import (
    ALPHABET,
    EXECUTABLE,
    FirstMachine,
    REDUCERS,
    roster as old_roster,
)
from folding_evolution.chem_tape import alphabet as a
from folding_evolution.chem_tape.executor import execute_program

TRAINING = {
    "BE": ["BE:F>S?F:M+m", "BE:F>m?S:F+M", "BE:S>F?M:F+m", "BE:S>F?m:M+S"],
    "PA": ["PA:(F>S?F:m)+M", "PA:(F>S?m:M)+F", "PA:(M>F?m:S)+S", "PA:(S>F?M:m)+m"],
}
# Protect entire previously probed behaviours, not only these spellings.
PROBED = [
    "BE:F>S?F:M+m",
    "BE:F>S?m:M+M",
    "BE:F>m?S:F+M",
    "BE:M>F?S:F+m",
    "BE:S>F?M:F+m",
    "BE:S>F?m:M+S",
    "PA:(F>S?F:m)+M",
    "PA:(F>S?m:M)+F",
    "PA:(F>m?M:S)+m",
    "PA:(M>F?F:m)+S",
    "PA:(M>F?m:S)+S",
    "PA:(S>F?M:m)+m",
]
DATA = Path(__file__).with_name("data") / "comparison_gate_1246_bank.json"
# Filled after the in-repo semantic build, pinned independently of bank metadata.
BANK_SHA = "df3476d0823cff5eaed57fccf19f01e6a2699442be3139b5f05cb56e5f7aa15d"


def digest(data):
    return hashlib.sha256(
        json.dumps(
            data, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def roster():
    xs = np.asarray(inputs_for("D1331"))
    reduced = dict(S=xs.sum(1), M=xs.max(1), m=xs.min(1), F=xs[:, 0])
    cells = []

    def push(r):
        return [a.INPUT, REDUCERS[r]]

    for repeated in "SMmF":
        for A, B, C, D, E in sorted(set(itertools.permutations("SMmF" + repeated))):
            gate = reduced[A] > reduced[B]
            for family in ("BE", "PA"):
                then = reduced[C] if family == "BE" else reduced[C] + reduced[E]
                other = reduced[D] + reduced[E]
                labels = np.where(gate, then, other).astype(np.int64)
                if family == "BE":
                    cid = f"BE:{A}>{B}?{C}:{D}+{E}"
                    program = (
                        push(D)
                        + push(E)
                        + [a.ADD]
                        + push(C)
                        + push(A)
                        + push(B)
                        + [a.GT, a.IF_GT]
                    )
                else:
                    cid = f"PA:({A}>{B}?{C}:{D})+{E}"
                    program = (
                        push(D)
                        + push(C)
                        + push(A)
                        + push(B)
                        + [a.GT, a.IF_GT]
                        + push(E)
                        + [a.ADD]
                    )
                cells.append(
                    dict(
                        id=cid,
                        shape=family,
                        roles=dict(A=A, B=B, C=C, D=D, E=E),
                        repeated=repeated,
                        labels=labels.tolist(),
                        canonical=program,
                        canonical_hash=hashlib.sha256(bytes(program)).hexdigest(),
                        token_counts={
                            str(t): n for t, n in sorted(Counter(program).items())
                        },
                        label_hash=hashlib.sha256(
                            labels.astype("<i8").tobytes()
                        ).hexdigest(),
                        gate_true=int(gate.sum()),
                        constant_gate=bool(gate.all() or not gate.any()),
                        inactive_branch=bool(
                            np.array_equal(labels, then)
                            or np.array_equal(labels, other)
                        ),
                    )
                )
    return sorted(cells, key=lambda c: c["id"])


def roles(cell):
    return {
        ("sum" if cell["shape"] == "BE" and role in ("D", "E") else role, r)
        for role, r in cell["roles"].items()
    }


def token_totals(cells):
    total = Counter()
    for cell in cells:
        total.update(cell["token_counts"])
    return dict(sorted(total.items()))


def choose_split(cells):
    by = {c["id"]: c for c in cells}
    train_hashes = {by[c]["label_hash"] for c in sum(TRAINING.values(), [])}
    probed = {c["label_hash"] for c in cells if set(c["alias_ids"]) & set(PROBED)}
    if len(probed) != 12:
        raise ValueError("the twelve development behaviours were not recovered")
    holdouts, candidates = {}, {}
    for family in TRAINING:
        training = [by[c] for c in TRAINING[family]]
        if not all(c["retained"] for c in training):
            raise ValueError("approved training cells did not survive")
        coverage = set().union(*(roles(c) for c in training))
        holdouts[family], candidates[family] = [], {}
        for reducer in "SMmF":
            eligible = [
                c
                for c in cells
                if c["retained"]
                and c["shape"] == family
                and c["repeated"] == reducer
                and c["label_hash"] not in probed
                and roles(c) <= coverage
            ]
            eligible.sort(
                key=lambda c: hashlib.sha256((c["id"] + "1246").encode()).hexdigest()
            )
            candidates[family][reducer] = [
                dict(
                    id=c["id"],
                    selection_hash=hashlib.sha256(
                        (c["id"] + "1246").encode()
                    ).hexdigest(),
                )
                for c in eligible
            ]
            if not eligible:
                raise ValueError(
                    f"no untouched role-covered {family}/{reducer} holdout"
                )
            holdouts[family].append(eligible[0]["id"])
    held = [by[c] for c in sum(holdouts.values(), [])]
    if len({c["label_hash"] for c in held}) != 8 or train_hashes & {
        c["label_hash"] for c in held
    }:
        raise ValueError("split behavioural leakage")
    totals = {f: token_totals([by[c] for c in holdouts[f]]) for f in TRAINING}
    if totals["BE"] != totals["PA"]:
        raise ValueError("holdout token totals differ")
    return dict(
        training=TRAINING,
        holdouts=holdouts,
        candidates=candidates,
        development_ids=PROBED,
        development_label_hashes=sorted(probed),
        rule='lowest sha256(id+"1246") per family/repeated reducer, unprobed and role-covered',
        holdout_token_totals=totals,
        training_token_totals={
            f: token_totals([by[c] for c in TRAINING[f]]) for f in TRAINING
        },
    )


def build(out):
    started = time.monotonic()
    inputs = inputs_for("D1331")
    raw = roster()
    # Every canonical, including excluded ones, checked on every D1331 input.
    programs = [[a.NOP] * (32 - len(c["canonical"])) + c["canonical"] for c in raw]
    expected = np.asarray([c["labels"] for c in raw])
    if not np.array_equal(outputs(programs, inputs, ALPHABET), expected):
        raise ValueError("Rust canonical mismatch")
    python = [
        [execute_program(p, TA, x, "intlist", ALPHABET) for x in inputs]
        for p in programs
    ]
    if not np.array_equal(python, expected):
        raise ValueError("Python canonical mismatch")
    canonical_seconds = time.monotonic() - started
    groups = defaultdict(list)
    for c in raw:
        if not c["constant_gate"]:
            groups[c["label_hash"]].append(c)
    old = {c["label_hash"] for c in old_roster("D1331")}
    cells = []
    for group in groups.values():
        rep = dict(min(group, key=lambda c: c["id"]))
        rep["alias_ids"] = sorted(c["id"] for c in group)
        rep["cross_family"] = len({c["shape"] for c in group}) > 1
        rep["old_bank_alias"] = rep["label_hash"] in old
        cells.append(rep)
    cells.sort(key=lambda c: c["id"])
    screen = screen_domain(
        "D1331",
        9,
        cells=cells,
        tokens=EXECUTABLE,
        machine_type=FirstMachine,
        alphabet=ALPHABET,
    )
    for c in cells:
        c["retained"] &= not (
            c["cross_family"] or c["old_bank_alias"] or c["inactive_branch"]
        )
    retained = dict(Counter(c["shape"] for c in cells if c["retained"]))
    if retained != {"BE": 37, "PA": 56}:
        raise ValueError(f"semantic counts disagree with approved probe: {retained}")
    split = choose_split(cells)
    bank = dict(
        name="comparison-gate-v1",
        domain="D1331",
        alphabet=ALPHABET,
        inputs=inputs,
        inputs_hash=digest(inputs),
        cells=cells,
        split=split,
        split_hash=digest(split),
        screen_depth=9,
        screen_complete=True,
        minimality="exhaustive through 9 tokens only; 13-token minimality unproved",
        screen_tokens=list(EXECUTABLE),
        agreement_rejection=0.8,
        raw_counts=dict(Counter(c["shape"] for c in raw)),
        nonconstant_counts=dict(
            Counter(c["shape"] for c in raw if not c["constant_gate"])
        ),
        distinct_nonconstant=len(cells),
        retained_counts=retained,
        canonical_validation=dict(
            programs=len(raw), inputs_per_program=len(inputs), Python=True, Rust=True
        ),
        screen_validation="best witnesses independently verified by Rust; FirstMachine reused from 1603",
    )
    write_json(out, "bank.json", bank)
    write_json(
        out,
        "screen_timing.json",
        dict(
            canonical_seconds=canonical_seconds,
            counts=screen["counts"],
            screen_seconds=screen["wall_seconds"],
            total_seconds=time.monotonic() - started,
        ),
    )
    return bank


def load_training(path=DATA):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != BANK_SHA:
        raise ValueError("comparison-gate bank hash mismatch")
    bank = json.loads(raw)
    if (
        not bank["screen_complete"]
        or bank["screen_depth"] != 9
        or bank["inputs"] != inputs_for("D1331")
        or digest(bank["inputs"]) != bank["inputs_hash"]
        or choose_split(bank["cells"]) != bank["split"]
        or digest(bank["split"]) != bank["split_hash"]
    ):
        raise ValueError("bank manifest/split mismatch")
    by = {c["id"]: c for c in bank["cells"]}
    # Deliberately no holdout labels or programs in the returned search payload.
    return bank, {
        cid: dict(id=cid, labels=by[cid]["labels"])
        for cid in sum(TRAINING.values(), [])
    }


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    build(out)


if __name__ == "__main__":
    main()
