"""Performance-blind double-gate bank under the explicitly named v2_x4 language."""

import hashlib
import itertools
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for, screen_domain
from experiments.chem_tape.composition_bank import SemanticMachine, TA
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.four_reducer_bank import EXECUTABLE
from folding_evolution.chem_tape import executor as vm

ALPHABET = "v2_x4"
BANK = "x4-double-gate-v1"
SLOTS = (5, 18, 22, 23)


class XMachine(SemanticMachine):
    def __init__(self, inputs):
        # Base initialization needs a rectangular nonempty domain. Its integer
        # constants/ANY are valid for all supported intlist inputs; ragged input
        # lists are padded only for initialization and then replaced below.
        padded = [
            list(x) + [0] * (max(1, max(map(len, inputs))) - len(x)) for x in inputs
        ]
        super().__init__(padded)
        for index, token in enumerate(SLOTS):
            self.reduced[token] = self.intern(
                np.asarray(
                    [x[index] if len(x) > index else 0 for x in inputs], dtype=np.int64
                )
            )
        self.reduced[11] = self.reduced[5]
        self.reduced[6] = self.intern(
            np.asarray([int(any(x)) for x in inputs], dtype=np.int64)
        )


def semantic_outputs(programs, inputs):
    m = XMachine(inputs)
    rows = []
    for program in programs:
        state = ()
        for token in program[:256]:
            if token in EXECUTABLE:
                state = m.apply(state, token)
        rows.append(m.values[m.output_id(state)])
    return np.asarray(rows)


def roster():
    xs = np.asarray(inputs_for("D625"))
    unique = {}
    for A, B, C, D, E, F in itertools.product(range(4), repeat=6):
        if A > B or C > D:
            continue
        gate = xs[:, A] + xs[:, B] > xs[:, C] + xs[:, D]
        lab = np.where(gate, xs[:, E], xs[:, F]).astype("<i8")
        if (
            gate.all()
            or not gate.any()
            or np.array_equal(lab, xs[:, E])
            or np.array_equal(lab, xs[:, F])
        ):
            continue
        sha = hashlib.sha256(lab.tobytes()).hexdigest()
        cid = f"DG:(X{A}+X{B})>(X{C}+X{D})?X{E}:X{F}"
        proper = len({A, B, C, D}) == 4
        push = lambda i: [1, SLOTS[i]]
        canonical = (
            push(F) + push(E) + push(A) + push(B) + [7] + push(C) + push(D) + [7, 8, 17]
        )
        cell = dict(
            id=cid,
            shape="DG",
            roles=dict(zip("ABCDEF", (A, B, C, D, E, F))),
            proper=proper,
            labels=lab.tolist(),
            label_hash=sha,
            canonical=canonical,
            pairing=sorted([sorted((A, B)), sorted((C, D))]),
        )
        # Same explicit duplicate representative rule as the steward's probe.
        if sha not in unique or (proper, -len(cid), cid) > (
            unique[sha]["proper"],
            -len(unique[sha]["id"]),
            unique[sha]["id"],
        ):
            unique[sha] = cell
    return sorted(unique.values(), key=lambda c: (c["label_hash"], c["id"]))


def maximum_clique(cells):
    """Exact Bron-Kerbosch, deterministic hash-order vertices/pivot/ties."""
    labels = np.asarray([c["labels"] for c in cells])
    matches = (labels[:, None, :] == labels[None, :, :]).sum(2)
    nb = {
        i: {
            j
            for j in range(len(cells))
            if i != j and 5 * matches[i, j] < 4 * labels.shape[1]
        }
        for i in range(len(cells))
    }
    best = []

    def visit(R, P, X):
        nonlocal best
        if not P and not X:
            if len(R) > len(best):
                best = sorted(R)
            return
        if len(R) + len(P) <= len(best):
            return
        pivot = min(P | X, key=lambda u: (-len(P & nb[u]), u))
        for v in sorted(P - nb[pivot]):
            visit(R + [v], P & nb[v], X & nb[v])
            P.remove(v)
            X.add(v)

    visit([], set(nb), set())
    return [cells[i] for i in best]


def pairing(cell):
    return tuple(map(tuple, cell["pairing"]))


def split(clique):
    if len(clique) < 16:
        return None
    # Source first, then protected coverage, then earliest four remaining devs.
    for source in itertools.combinations(clique, 4):
        if len({pairing(c) for c in source}) < 2 or {
            c["roles"][r] for c in source for r in "EF"
        } != set(range(4)):
            continue
        left = [c for c in clique if c not in source]
        for protected in itertools.combinations(left, 8):
            if len({pairing(c) for c in protected}) != 3:
                continue
            dev = [c for c in left if c not in protected][:4]
            return dict(
                source=[c["id"] for c in source],
                development=[c["id"] for c in dev],
                protected=[c["id"] for c in protected],
            )
    return None


def build(deadline=None):
    started = time.monotonic()
    screen = screen_domain(
        "D625",
        9,
        deadline,
        cells=roster(),
        tokens=EXECUTABLE,
        machine_type=XMachine,
        alphabet=ALPHABET,
    )
    retained = [c for c in screen["cells"] if c["retained"]]
    clique = maximum_clique(retained)
    selected = split(clique)
    bank = dict(
        name=BANK,
        alphabet=ALPHABET,
        inputs=inputs_for("D625"),
        screen=screen,
        maximum_separated=len(clique),
        clique_ids=[c["id"] for c in clique],
        split=selected,
        tie_break="label SHA256 then id; deterministic first maximum clique; source/protected/development enumeration",
        seconds=time.monotonic() - started,
    )
    if selected is None:
        raise ValueError(
            f"bank admission failed: {len(retained)} retained, maximum separated {len(clique)}, no covered 16-cell split"
        )
    return bank


def validate(cells=(), random_count=10000, depth=3):
    started = time.monotonic()
    inputs = [[], [9], [9, -7], [9, -7, 4], [9, -7, 4, -3]]
    machine = XMachine(inputs)
    raw_states, raw_outputs = set(), set()
    count = 0
    vm._SAFE_POP_CONSUME = False
    for d in range(depth + 1):
        for program in itertools.product(EXECUTABLE, repeat=d):
            state = ()
            for token in program:
                state = machine.apply(state, token)
            raw_states.add(state)
            raw_outputs.add(machine.values[machine.output_id(state)].tobytes())
            for j, inp in enumerate(inputs):
                stack = []
                for token in program:
                    vm.resolve_op(token, TA, ALPHABET)(stack, inp, "intlist", TA)
                expected = [
                    ("int", int(machine.values[v][j]))
                    if v >= 0
                    else ("intlist", tuple(inp))
                    if v == -1
                    else ("intlist", ())
                    if v == -2
                    else ("charlist", ())
                    for v in state
                ]
                assert stack == expected, (program, inp, stack, expected)
            count += 1
    seen, frontier = {()}, {()}
    dedup_outputs = {machine.values[machine.zero].tobytes()}
    for _ in range(depth):
        frontier = {machine.apply(s, t) for s in frontier for t in EXECUTABLE} - seen
        seen |= frontier
        dedup_outputs |= {
            machine.values[machine.output_id(s)].tobytes() for s in frontier
        }
    assert seen == raw_states and dedup_outputs == raw_outputs
    rng = np.random.default_rng(390001)
    programs = rng.integers(24, size=(random_count, 32)).tolist()
    observed = outputs(programs, inputs, ALPHABET)
    assert np.array_equal(observed, semantic_outputs(programs, inputs))
    expected = [
        [vm.execute_program(p, TA, x, "intlist", ALPHABET) for x in inputs]
        for p in programs
    ]
    assert np.array_equal(observed, expected)
    if cells:
        domain = inputs_for("D625")
        for field in ("canonical", "witness"):
            programs = [c[field] for c in cells]
            observed = outputs(programs, domain, ALPHABET)
            assert np.array_equal(observed, semantic_outputs(programs, domain))
            expected = [
                [vm.execute_program(p, TA, x, "intlist", ALPHABET) for x in domain]
                for p in programs
            ]
            assert np.array_equal(observed, expected)
            if field == "canonical":
                assert np.array_equal(observed, [c["labels"] for c in cells])
    return dict(
        passed=True,
        raw_programs=count,
        depth=depth,
        random_programs=random_count,
        typed_state_dedup=True,
        canonical_and_witness_cells=len(cells),
        seconds=time.monotonic() - started,
    )
