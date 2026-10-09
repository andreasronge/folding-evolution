"""2303 performance-blind two-sum-v1 enumeration, audit and frozen split."""

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
    BANK_SHA as OLD_SHA,
)
from experiments.chem_tape.composition_bank import TA
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.four_reducer_bank import (
    ALPHABET,
    EXECUTABLE,
    FirstMachine,
    REDUCERS,
)
from experiments.chem_tape.then_addition_bank import load as load_ta, BANK_SHA as TA_SHA
from folding_evolution.chem_tape import alphabet as a
from folding_evolution.chem_tape.executor import execute_program

DATA = Path(__file__).with_name("data") / "two_sum_2303_bank.json"
BANK_SHA = "d2fc77e957f71ad71e8d7f9e720f8fb24824510e9670d025cd8271d3113ea451"


def roster():
    xs = np.asarray(inputs_for("D1331"))
    values = dict(F=xs[:, 0], M=xs.max(1), S=xs.sum(1), m=xs.min(1))
    result = []

    def push(r):
        return [a.INPUT, REDUCERS[r]]

    for A, B, C, D, E, F in itertools.product("FMSm", repeat=6):
        if A == B or C > D or E > F or set((A, B, C, D, E, F)) != set("FMSm"):
            continue
        gate = values[A] > values[B]
        labels = np.where(gate, values[C] + values[D], values[E] + values[F]).astype(
            "<i8"
        )
        program = (
            push(E)
            + push(F)
            + [a.ADD]
            + push(C)
            + push(D)
            + [a.ADD]
            + push(A)
            + push(B)
            + [a.GT, a.IF_GT]
        )
        result.append(
            dict(
                id=f"TB:{A}>{B}?{C}+{D}:{E}+{F}",
                shape="TB",
                roles=dict(zip("ABCDEF", (A, B, C, D, E, F))),
                gate_pair="".join(sorted((A, B))),
                labels=labels.tolist(),
                canonical=program,
                canonical_hash=hashlib.sha256(bytes(program)).hexdigest(),
                label_hash=hashlib.sha256(labels.tobytes()).hexdigest(),
                token_counts={str(t): n for t, n in sorted(Counter(program).items())},
                gate_true=int(gate.sum()),
                constant_gate=bool(gate.all() or not gate.any()),
            )
        )
    return sorted(result, key=lambda c: c["id"])


def choose(cells):
    chosen, counts = [], Counter()
    for cell in sorted(
        (c for c in cells if c["retained"]),
        key=lambda c: hashlib.sha256(("two-sum-v1:" + c["id"]).encode()).hexdigest(),
    ):
        if counts[cell["gate_pair"]] >= 4:
            continue
        if any(
            5 * np.count_nonzero(np.asarray(cell["labels"]) == other["labels"])
            >= 4 * 1331
            for other in chosen
        ):
            continue
        chosen.append(cell)
        counts[cell["gate_pair"]] += 1
        if len(chosen) == 20:
            break
    return [c["id"] for c in chosen[:16]], [c["id"] for c in chosen[16:]]


def build(out):
    tick = time.monotonic()
    old, _ = load_training()
    ta, _ = load_ta()
    inputs = inputs_for("D1331")
    raw = roster()
    programs = [[a.NOP] * (32 - len(c["canonical"])) + c["canonical"] for c in raw]
    expected = np.asarray([c["labels"] for c in raw])
    rust = outputs(programs, inputs, ALPHABET)
    rust_bad = np.argwhere(rust != expected)
    python = np.asarray(
        [
            [execute_program(p, TA, x, "intlist", ALPHABET) for x in inputs]
            for p in programs
        ]
    )
    python_bad = np.argwhere(python != expected)
    validation = dict(
        programs=len(raw),
        inputs_per_program=len(inputs),
        Python=not len(python_bad),
        Rust=not len(rust_bad),
        python_mismatches=len(python_bad),
        rust_mismatches=len(rust_bad),
        seconds=time.monotonic() - tick,
    )
    write_json(out, "canonical_validation.json", validation)
    if len(rust_bad) or len(python_bad):
        raise ValueError(f"canonical mismatch: {validation}")
    groups = defaultdict(list)
    for c in raw:
        if not c["constant_gate"]:
            groups[c["label_hash"]].append(c)
    cells = []
    for group in groups.values():
        cell = dict(min(group, key=lambda c: c["id"]))
        cell["alias_ids"] = sorted(c["id"] for c in group)
        cells.append(cell)
    cells.sort(key=lambda c: c["id"])
    screen = screen_domain(
        "D1331",
        9,
        cells=cells,
        tokens=EXECUTABLE,
        machine_type=FirstMachine,
        alphabet=ALPHABET,
    )
    reference = np.asarray([c["labels"] for c in old["cells"] + ta["cells"]])
    for cell in cells:
        best = int(np.count_nonzero(reference == cell["labels"], axis=1).max())
        reasons = [] if cell["retained"] else ["nine_token_" + cell["alias_kind"]]
        if 5 * best >= 4 * len(inputs):
            reasons.append("old_roster_agreement_ge_80_percent")
        cell.update(
            old_best_matches=best,
            old_max_agreement=best / len(inputs),
            exclusion_reasons=reasons,
            retained=not reasons,
        )
    confirmation, timing = choose(cells)
    counts = dict(
        raw=len(raw),
        nonconstant=sum(not c["constant_gate"] for c in raw),
        distinct=len(cells),
        eligible=sum(c["retained"] for c in cells),
        confirmation=len(confirmation),
        timing=len(timing),
    )
    bank = dict(
        name="two-sum-v1",
        domain="D1331",
        inputs=inputs,
        inputs_hash=digest(inputs),
        alphabet=ALPHABET,
        cells=cells,
        selected_ids=confirmation,
        timing_ids=timing,
        counts=counts,
        raw_assignments=[
            dict(
                id=c["id"], label_hash=c["label_hash"], constant_gate=c["constant_gate"]
            )
            for c in raw
        ],
        canonical_validation={k: v for k, v in validation.items() if k != "seconds"},
        screen_depth=9,
        screen_complete=True,
        screen_tokens=list(EXECUTABLE),
        reference_sha256=dict(comparison_gate=OLD_SHA, then_addition=TA_SHA),
        reference_behaviours=len(reference),
        selection_rule='lexical representative; sha256("two-sum-v1:"+id); <=4 per unordered gate pair across confirmation+timing; mutual agreement <80%',
        minimality="<=9-token screen only; 10-15-token solutions not excluded",
    )
    write_json(out, "bank.json", bank)
    write_json(
        out,
        "screen_timing.json",
        dict(
            levels=screen["counts"],
            screen_seconds=screen["wall_seconds"],
            total_seconds=time.monotonic() - tick,
        ),
    )
    if (
        counts["nonconstant"] != 333
        or counts["distinct"] != 289
        or counts["eligible"] != 76
        or len(confirmation) != 16
        or len(timing) != 4
    ):
        raise ValueError(f"approved bank feasibility gate failed: {counts}")
    return bank


def load():
    raw = DATA.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BANK_SHA:
        raise ValueError("two-sum bank SHA mismatch")
    bank = json.loads(raw)
    if (
        bank["inputs"] != inputs_for("D1331")
        or digest(bank["inputs"]) != bank["inputs_hash"]
    ):
        raise ValueError("two-sum input manifest mismatch")
    return bank, {
        c["id"]: dict(id=c["id"], labels=c["labels"])
        for c in bank["cells"]
        if c["id"] in bank["selected_ids"] + bank["timing_ids"]
    }


if __name__ == "__main__":
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    build(out)
