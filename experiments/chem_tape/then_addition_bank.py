"""Performance-blind then-addition-v1 semantic audit (1548); no search."""

from collections import Counter, defaultdict
import hashlib
import itertools
import json
import os
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for, screen_domain
from experiments.chem_tape.comparison_gate_bank import (
    digest,
    load_training,
    BANK_SHA as V1_SHA,
)
from experiments.chem_tape.composition_bank import TA
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.crossed_learning_run import load_bank, DEFAULT_BANK
from experiments.chem_tape.four_reducer_bank import (
    ALPHABET,
    EXECUTABLE,
    FirstMachine,
    REDUCERS,
)
from folding_evolution.chem_tape import alphabet as a
from folding_evolution.chem_tape.executor import execute_program

DATA = Path(__file__).with_name("data") / "then_addition_1548_bank.json"
BANK_SHA = "26be2d562275ff908b9874667b80ac88795984fb74c2ce3d8dc2738f726e5748"


def roster():
    xs = np.asarray(inputs_for("D1331"))
    r = dict(S=xs.sum(1), M=xs.max(1), m=xs.min(1), F=xs[:, 0])
    cells = []

    def push(key):
        return [a.INPUT, REDUCERS[key]]

    for repeated in "SMmF":
        for A, B, C, D, E in sorted(set(itertools.permutations("SMmF" + repeated))):
            gate = r[A] > r[B]
            labels = np.where(gate, r[C] + r[D], r[E]).astype(np.int64)
            program = (
                push(E)
                + push(C)
                + push(D)
                + [a.ADD]
                + push(A)
                + push(B)
                + [a.GT, a.IF_GT]
            )
            cells.append(
                dict(
                    id=f"TA:{A}>{B}?{C}+{D}:{E}",
                    shape="TA",
                    repeated=repeated,
                    roles=dict(A=A, B=B, C=C, D=D, E=E),
                    labels=labels.tolist(),
                    canonical=program,
                    canonical_hash=hashlib.sha256(bytes(program)).hexdigest(),
                    label_hash=hashlib.sha256(
                        labels.astype("<i8").tobytes()
                    ).hexdigest(),
                    token_counts={
                        str(t): n for t, n in sorted(Counter(program).items())
                    },
                    gate_true=int(gate.sum()),
                    constant_gate=bool(gate.all() or not gate.any()),
                )
            )
    return sorted(cells, key=lambda c: c["id"])


def build(out):
    tick = time.monotonic()
    v1, _ = load_training()
    old, _ = load_bank(DEFAULT_BANK)
    raw = roster()
    inputs = v1["inputs"]
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
    groups = defaultdict(list)
    for cell in raw:
        if not cell["constant_gate"]:
            groups[cell["label_hash"]].append(cell)
    cells = []
    for group in groups.values():
        cell = dict(min(group, key=lambda c: c["id"]))
        cell["alias_ids"] = sorted(c["id"] for c in group)
        cell["alias_repeated_reducers"] = sorted({c["repeated"] for c in group})
        # The steward's probe deduplicated in S/M/m/F enumeration order;
        # aliases can span repeated-reducer inventories on this domain.
        cell["probe_repeated_reducer"] = min(
            group, key=lambda c: ("SMmF".index(c["repeated"]), c["id"])
        )["repeated"]
        cells.append(cell)
    cells.sort(key=lambda c: c["id"])
    validation_seconds = time.monotonic() - tick
    screen = screen_domain(
        "D1331",
        9,
        cells=cells,
        tokens=EXECUTABLE,
        machine_type=FirstMachine,
        alphabet=ALPHABET,
    )
    old_hashes = {c["label_hash"] for c in old["cells"]}
    reference = np.asarray([c["labels"] for c in v1["cells"]])
    survivors = sum(c["retained"] for c in cells)
    fresh_count = 0
    for cell in cells:
        matches = np.count_nonzero(reference == cell["labels"], axis=1)
        best = int(matches.max())
        cell["v1_best_matches"] = best
        cell["v1_max_agreement"] = best / len(inputs)
        cell["v1_closest_ids"] = [
            v1["cells"][i]["id"] for i in np.flatnonzero(matches == best)
        ]
        reasons = []
        if not cell["retained"]:
            reasons.append("nine_token_" + cell["alias_kind"])
        if 5 * best >= 4 * len(inputs):
            reasons.append("v1_agreement_ge_80_percent")
        fresh_count += int(not reasons)
        if cell["label_hash"] in old_hashes:
            reasons.append("exact_1603_bank_alias")
        cell["exclusion_reasons"] = reasons
        cell["retained"] = not reasons
    counts = dict(
        raw=len(raw),
        nonconstant=sum(not c["constant_gate"] for c in raw),
        distinct=len(cells),
        nine_token_survivors=survivors,
        fresh_before_old_exclusion=fresh_count,
        final=sum(c["retained"] for c in cells),
    )
    probe_repeats = dict(
        Counter(c["probe_repeated_reducer"] for c in cells if c["retained"])
    )
    bank = dict(
        name="then-addition-v1",
        domain="D1331",
        inputs=inputs,
        inputs_hash=digest(inputs),
        alphabet=ALPHABET,
        cells=cells,
        raw_assignments=[
            dict(
                id=c["id"],
                label_hash=c["label_hash"],
                constant_gate=c["constant_gate"],
                exclusion_reasons=["constant_gate"] if c["constant_gate"] else [],
            )
            for c in raw
        ],
        selected_ids=[c["id"] for c in cells if c["retained"]],
        counts=counts,
        representative_reducer_counts=dict(
            Counter(c["repeated"] for c in cells if c["retained"])
        ),
        probe_order_reducer_counts=probe_repeats,
        reference_v1_sha256=V1_SHA,
        reference_v1_ids=[c["id"] for c in v1["cells"]],
        reference_old_sha256=hashlib.sha256(DEFAULT_BANK.read_bytes()).hexdigest(),
        screen_depth=9,
        screen_tokens=list(EXECUTABLE),
        screen_complete=True,
        agreement_rejection=0.8,
        minimality="screen through nine only; 13-token minimality unproved",
        canonical_validation=dict(
            programs=240, inputs_per_program=1331, Python=True, Rust=True
        ),
    )
    write_json(out, "bank.json", bank)
    write_json(
        out,
        "screen_timing.json",
        dict(
            canonical_seconds=validation_seconds,
            screen_seconds=screen["wall_seconds"],
            levels=screen["counts"],
            total_seconds=time.monotonic() - tick,
        ),
    )
    if [
        counts[k]
        for k in (
            "raw",
            "nonconstant",
            "distinct",
            "nine_token_survivors",
            "fresh_before_old_exclusion",
        )
    ] != [240, 162, 86, 37, 16]:
        raise ValueError(f"approved semantic probe mismatch: {counts}")
    if not counts["final"]:
        raise ValueError("empty fresh bank after approved old-bank exclusion")
    if counts["final"] == 16 and probe_repeats != dict(S=3, M=5, m=4, F=4):
        raise ValueError(
            f"probe-order repeated reducer counts mismatch: {probe_repeats}"
        )
    return bank


def load():
    raw = DATA.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BANK_SHA:
        raise ValueError("then-addition bank SHA mismatch")
    bank = json.loads(raw)
    if (
        bank["inputs"] != inputs_for("D1331")
        or digest(bank["inputs"]) != bank["inputs_hash"]
    ):
        raise ValueError("input manifest mismatch")
    return bank, {
        c["id"]: dict(id=c["id"], labels=c["labels"])
        for c in bank["cells"]
        if c["retained"]
    }


if __name__ == "__main__":
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    build(out)
