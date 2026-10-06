"""Frozen FIRST bank, exact semantic screen, split obstacles and validation."""

from collections import Counter
import hashlib
import itertools
import time

import numpy as np

from experiments.chem_tape.assembly_bank import inputs_for, screen_domain
from experiments.chem_tape.composition_bank import TOKENS, TA, SemanticMachine
from experiments.chem_tape.composition_search import outputs
from folding_evolution.chem_tape import alphabet as a
from folding_evolution.chem_tape.executor import execute_program, resolve_op

ALPHABET = "v2_rmin_first"
REDUCERS = {"S": a.SUM, "M": a.REDUCE_MAX, "m": a.REDUCE_MIN, "F": a.FIRST}
EXECUTABLE = (*TOKENS, a.FIRST)


class FirstMachine(SemanticMachine):
    def __init__(self, inputs):
        super().__init__(inputs)
        self.reduced[a.FIRST] = self.intern(np.asarray(inputs, dtype=np.int64)[:, 0])


def roster(domain):
    xs = np.asarray(inputs_for(domain))
    reduced = dict(S=xs.sum(1), M=xs.max(1), m=xs.min(1), F=xs[:, 0])
    cells = []

    def push(r):
        return [a.INPUT, REDUCERS[r]]

    def emit(cid, family, roles, labels, program):
        cells.append(
            dict(
                id=cid,
                shape=family,
                roles=roles,
                labels=labels.tolist(),
                canonical=program,
                token_counts=dict(Counter(map(str, program))),
                label_hash=hashlib.sha256(labels.astype("<i8").tobytes()).hexdigest(),
            )
        )

    for cond, then in itertools.permutations(REDUCERS, 2):
        left, right = [r for r in REDUCERS if r not in (cond, then)]
        emit(
            f"BE:{cond}?{then}:({left}+{right})",
            "BE",
            dict(cond=cond, then=then, sum_left=left, sum_right=right),
            np.where(reduced[cond] > 0, reduced[then], reduced[left] + reduced[right]),
            push(left) + push(right) + [a.ADD] + push(then) + push(cond) + [a.IF_GT],
        )
    for cond, then, other in itertools.permutations(REDUCERS, 3):
        summand = next(r for r in REDUCERS if r not in (cond, then, other))
        emit(
            f"PA:({cond}?{then}:{other})+{summand}",
            "PA",
            dict(cond=cond, then=then, other=other, summand=summand),
            np.where(reduced[cond] > 0, reduced[then], reduced[other])
            + reduced[summand],
            push(other) + push(then) + push(cond) + [a.IF_GT] + push(summand) + [a.ADD],
        )
    return sorted(cells, key=lambda c: c["id"])


def role_set(cells):
    # Both BE summands belong to one unordered role.
    return {
        ("sum" if role.startswith("sum_") else role, r)
        for c in cells
        for role, r in c["roles"].items()
    }


def split(cells):
    cells = sorted(cells, key=lambda c: c["id"])
    if len(cells) < 4:
        return None
    for hold in itertools.combinations(cells, 2):
        train = [c for c in cells if c not in hold]
        if role_set(hold) <= role_set(train) and not {c["label_hash"] for c in hold} & {
            c["label_hash"] for c in train
        }:
            return dict(
                holdouts=[c["id"] for c in hold], training=[c["id"] for c in train]
            )
    return None


def obstacles(screen):
    result = {}
    for family in ("BE", "PA"):
        cells = [c for c in screen["cells"] if c["retained"] and c["shape"] == family]
        coverage = {
            f"{role}:{r}": [c["id"] for c in cells if (role, r) in role_set([c])]
            for role, r in sorted(role_set(cells))
        }
        result[family] = dict(
            retained=[c["id"] for c in cells],
            split=split(cells),
            role_coverage=coverage,
            single_covered_holdouts=[
                c["id"]
                for c in cells
                if role_set([c]) <= role_set([x for x in cells if x != c])
            ],
            pair_obstacles=[
                dict(
                    holdouts=[c["id"] for c in hold],
                    missing_roles=sorted(
                        role_set(hold) - role_set([c for c in cells if c not in hold])
                    ),
                )
                for hold in itertools.combinations(cells, 2)
            ],
        )
    return result


def screen_job(job):
    domain, depth, deadline = job
    result = screen_domain(
        domain,
        depth,
        deadline,
        cells=roster(domain),
        tokens=EXECUTABLE,
        machine_type=FirstMachine,
        alphabet=ALPHABET,
    )
    result["obstacles"] = obstacles(result)
    return result


def validate(random_count=100000, depth=4):
    started = time.monotonic()
    # A representative domain spanning signs/ties; complete typed stacks are
    # compared for every raw program, with no state pruning in the reference.
    inputs = [[-5, 2, 0], [3, -1, 5], [0, 0, 0], [-2, -2, -2], [1, 1, 1]]
    machine = FirstMachine(inputs)
    raw_states, raw_outputs = set(), set()
    count = 0
    for d in range(depth + 1):
        for program in itertools.product(EXECUTABLE, repeat=d):
            state = ()
            for t in program:
                state = machine.apply(state, t)
            raw_states.add(state)
            raw_outputs.add(machine.values[machine.output_id(state)].tobytes())
            for j, inp in enumerate(inputs):
                stack = []
                for t in program:
                    resolve_op(t, TA, ALPHABET)(stack, inp, "intlist", TA)
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
                assert stack == expected, (program, inp, state, stack)
            count += 1
    seen, frontier = {()}, {()}
    dedup_outputs = {machine.values[machine.zero].tobytes()}
    for _ in range(depth):
        frontier = {machine.apply(s, t) for s in frontier for t in EXECUTABLE} - seen
        seen |= frontier
        dedup_outputs |= {
            machine.values[machine.output_id(s)].tobytes() for s in frontier
        }
    assert seen == raw_states and raw_outputs == dedup_outputs
    rng = np.random.default_rng(1603001)
    # Every random program checked at all representative inputs plus empty
    # input: 100k programs, not 100k program/input pairs.
    inputs += [[]]
    for offset in range(0, random_count, 1000):
        programs = rng.integers(
            24, size=(min(1000, random_count - offset), 32)
        ).tolist()
        observed = outputs(programs, inputs, ALPHABET)
        expected = [
            [execute_program(p, TA, x, "intlist", ALPHABET) for x in inputs]
            for p in programs
        ]
        assert np.array_equal(observed, expected), "Python/Rust random disagreement"
    for domain in ("D625", "D1331", "D2401"):
        cells = roster(domain)
        assert np.array_equal(
            outputs(
                [[0] * 22 + c["canonical"] for c in cells], inputs_for(domain), ALPHABET
            ),
            [c["labels"] for c in cells],
        )
    return dict(
        complete=depth == 4 and random_count == 100000,
        passed=True,
        brute_depth=depth,
        raw_programs=count,
        typed_states=len(seen),
        random_programs=random_count,
        random_seed=1603001,
        canonical_cells_per_domain=36,
        seconds=time.monotonic() - started,
    )
