"""Deterministic semantic preflight only; no evolutionary searches or fitted maps.

Uses an isolated export of research/main. The current checkout's Rust extension
does not implement FIRST, so validation here uses the exported Python executor.
Any admitted experiment must additionally validate the matching Rust build.
"""
import hashlib
import io
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time

OUT = Path(__file__).resolve().parent
DOUBLE = "--double-predicate" in sys.argv
DOMAIN = "D1331" if DOUBLE else "D2401"
STEM = "double-predicate-audit" if DOUBLE else "predicate-domain-audit"
REV = subprocess.check_output(["git", "rev-parse", "research/main"], text=True).strip()
with tempfile.TemporaryDirectory(prefix="strategy-semantic-") as directory:
    archive = subprocess.check_output(
        ["git", "archive", REV, "src", "experiments"]
    )
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(directory, filter="data")
    sys.path[:0] = [directory, str(Path(directory) / "src")]
    import numpy as np
    from folding_evolution.chem_tape import alphabet as a
    from folding_evolution.chem_tape.executor import execute_program
    from experiments.chem_tape import assembly_bank as ab
    from experiments.chem_tape.composition_bank import TA
    from experiments.chem_tape.four_reducer_bank import ALPHABET, EXECUTABLE, FirstMachine, REDUCERS

    def python_outputs(programs, inputs, alphabet):
        return np.asarray([[execute_program(p, TA, x, "intlist", alphabet) for x in inputs] for p in programs])

    ab.outputs = python_outputs
    xs = np.asarray(ab.inputs_for(DOMAIN))
    values = dict(S=xs.sum(1), M=xs.max(1), m=xs.min(1), F=xs[:, 0])
    cells = {}
    for repeated in "SMmF":
        for A, B, C, D, E in sorted(set(itertools.permutations("SMmF" + repeated))):
            if A > B:
                continue
            gate = values[A] + values[B] > values[C]
            labels = np.where(gate, values[D], values[E]).astype("<i8")
            if gate.all() or not gate.any() or np.array_equal(labels, values[D]) or np.array_equal(labels, values[E]):
                continue
            key = hashlib.sha256(labels.tobytes()).hexdigest()
            push = lambda r: [a.INPUT, REDUCERS[r]]
            cell = dict(id=f"GA:({A}+{B})>{C}?{D}:{E}", shape="GA", roles=dict(zip("ABCDE", (A,B,C,D,E))),
                        labels=labels.tolist(), label_hash=key,
                        canonical=push(E)+push(D)+push(A)+push(B)+[a.ADD]+push(C)+[a.GT,a.IF_GT])
            if key not in cells or cell["id"] < cells[key]["id"]:
                cells[key] = cell
    roster = sorted(cells.values(), key=lambda c: c["id"])
    if DOUBLE:
        cells = {}
        for A, B, C, D, E, F in itertools.product("FMSm", repeat=6):
            if A > B or C > D or set((A,B,C,D,E,F)) != set("FMSm"):
                continue
            gate = values[A] + values[B] > values[C] + values[D]
            labels = np.where(gate, values[E], values[F]).astype("<i8")
            if gate.all() or not gate.any() or np.array_equal(labels, values[E]) or np.array_equal(labels, values[F]):
                continue
            key = hashlib.sha256(labels.tobytes()).hexdigest()
            cell = dict(id=f"DG:({A}+{B})>({C}+{D})?{E}:{F}", shape="DG",
                        roles=dict(zip("ABCDEF",(A,B,C,D,E,F))), labels=labels.tolist(), label_hash=key,
                        canonical=push(F)+push(E)+push(A)+push(B)+[a.ADD]+push(C)+push(D)+[a.ADD,a.GT,a.IF_GT])
            if key not in cells or cell["id"] < cells[key]["id"]:
                cells[key] = cell
        roster = sorted(cells.values(), key=lambda c:c["id"])
    result = ab.screen_domain(DOMAIN, 9, deadline=time.monotonic()+300,
                             cells=roster, tokens=EXECUTABLE, machine_type=FirstMachine, alphabet=ALPHABET)
    retained = [c for c in roster if c["retained"]]
    if DOUBLE:
        reference = []
        for name in ("comparison_gate_1246_bank.json", "then_addition_1548_bank.json", "two_sum_2303_bank.json"):
            bank = json.loads((Path(directory)/"experiments/chem_tape/data"/name).read_text())
            reference.extend(c["labels"] for c in bank["cells"])
        reference = np.asarray(reference)
        for c in retained:
            c["old_roster_agreement"] = float(np.count_nonzero(reference == c["labels"],axis=1).max()/len(xs))
        retained = [c for c in retained if c["old_roster_agreement"] < .8]
    separated = []
    for c in sorted(retained, key=lambda c: hashlib.sha256(("predicate-d2401:"+c["id"]).encode()).hexdigest()):
        if all(5*np.count_nonzero(np.asarray(c["labels"]) == d["labels"]) < 4*len(xs) for d in separated):
            separated.append(c)
    result.update(scope="Semantic preflight, no search; Python validation only; greedy separated set is not a maximum certificate",
                  code=REV, distinct_active=len(roster), retained_count=len(retained),
                  retained_ids=[c["id"] for c in retained], separated_ids=[c["id"] for c in separated])
    (OUT/(STEM+".json")).write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("code","distinct_active","retained_count","retained_ids","separated_ids","wall_seconds")}))
