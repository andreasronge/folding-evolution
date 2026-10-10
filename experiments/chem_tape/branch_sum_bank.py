"""Performance-blind TS bank; the DG real-token screen is reused unchanged."""

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.assembly_bank import (
    inputs_for,
    screen_domain,
    deadline_check,
)
from experiments.chem_tape.four_reducer_bank import EXECUTABLE
from experiments.chem_tape.independent_input_bank import ALPHABET, SLOTS, XMachine

BANK = "x4-branch-sum-v1"


def roster():
    xs = np.asarray(inputs_for("D625"))
    unique = {}
    for A, B in itertools.permutations(range(4), 2):
        for C, D in itertools.combinations(range(4), 2):
            for E, F in itertools.combinations(range(4), 2):
                if len({A, B, C, D, E, F}) != 4:
                    continue
                gate = xs[:, A] > xs[:, B]
                then, other = xs[:, C] + xs[:, D], xs[:, E] + xs[:, F]
                lab = np.where(gate, then, other).astype("<i8")
                if np.array_equal(lab, then) or np.array_equal(lab, other):
                    continue
                sha = hashlib.sha256(lab.tobytes()).hexdigest()
                cid = f"TS:X{A}>X{B}?(X{C}+X{D}):(X{E}+X{F})"

                def push(i):
                    return [1, SLOTS[i]]

                canonical = (
                    push(E)
                    + push(F)
                    + [7]
                    + push(C)
                    + push(D)
                    + [7]
                    + push(A)
                    + push(B)
                    + [8, 17]
                )
                cell = dict(
                    id=cid,
                    shape="TS",
                    roles=dict(zip("ABCDEF", (A, B, C, D, E, F))),
                    proper=True,
                    labels=lab.tolist(),
                    label_hash=sha,
                    canonical=canonical,
                    pairing=[min(A, B), max(A, B)],
                )
                if sha not in unique or cid > unique[sha]["id"]:
                    unique[sha] = cell
    return sorted(unique.values(), key=lambda c: (c["label_hash"], c["id"]))


def maximum_clique(cells, deadline=None):
    """Exact bitset branch-and-bound with greedy-color upper bounds.

    Deterministic vertex/color order; a completed search certifies maximal size.
    Equal-size ties retain the first found maximum, without expensive tie search.
    """
    labels = np.asarray([c["labels"] for c in cells])
    nb = []
    for i in range(len(cells)):
        matches = (labels == labels[i]).sum(1)
        nb.append(
            sum(
                1 << j
                for j in range(len(cells))
                if j != i and 5 * matches[j] < 4 * labels.shape[1]
            )
        )
    best = []
    visits = 0

    def color(P):
        order, bounds = [], []
        level = 0
        while P:
            level += 1
            Q = P
            while Q:
                bit = Q & -Q
                v = bit.bit_length() - 1
                order.append(v)
                bounds.append(level)
                P &= ~bit
                Q &= ~bit
                Q &= ~nb[v]
        return order, bounds

    def expand(R, P):
        nonlocal best, visits
        visits += 1
        if visits % 256 == 1:
            deadline_check(deadline)
        order, bounds = color(P)
        for k in range(len(order) - 1, -1, -1):
            if len(R) + bounds[k] <= len(best):
                return
            v = order[k]
            Q = P & nb[v]
            if Q:
                expand(R + [v], Q)
            elif len(R) + 1 > len(best):
                best = R + [v]
            P &= ~(1 << v)

    expand([], (1 << len(cells)) - 1)
    return [cells[i] for i in sorted(best)]


def split(clique, deadline=None):
    if len(clique) < 16:
        return None
    # Prefer aggregate readout balance by a semantic-only squared-count score.
    candidates = []
    for i, source in enumerate(itertools.combinations(clique, 4)):
        if i % 10000 == 0:
            deadline_check(deadline)
        if len({tuple(c["pairing"]) for c in source}) < 2:
            continue
        counts = np.bincount(
            [v for c in source for v in c["roles"].values()], minlength=4
        )
        if np.any(counts == 0):
            continue
        candidates.append(
            (int(np.sum((counts - 6) ** 2)), tuple(c["id"] for c in source), source)
        )
    for _, _, source in sorted(candidates):
        left = [c for c in clique if c not in source]
        # Earliest eight targets covering >=3 pairings, then earliest four devs.
        for i, target in enumerate(itertools.combinations(left, 8)):
            if i % 10000 == 0:
                deadline_check(deadline)
            if len({tuple(c["pairing"]) for c in target}) >= 3:
                dev = [c for c in left if c not in target][:4]
                return dict(
                    source=[c["id"] for c in source],
                    development=[c["id"] for c in dev],
                    protected=[c["id"] for c in target],
                )
    return None


def build(deadline):
    tick = time.monotonic()
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
    clique = maximum_clique(retained, deadline)
    chosen = split(clique, deadline)
    if chosen is None:
        raise ValueError(
            f"TS bank admission failed: {len(retained)} retained, maximum {len(clique)}, no covered split"
        )
    return dict(
        name=BANK,
        alphabet=ALPHABET,
        inputs=inputs_for("D625"),
        screen=screen,
        maximum_separated=len(clique),
        clique_ids=[c["id"] for c in clique],
        split=chosen,
        tie_break="hash/id vertices, deterministic bitset color-bound first maximum; source readout balance then ids; target/dev enumeration",
        seconds=time.monotonic() - tick,
    )


def validate_bank(bank):
    parts = bank["split"]
    by = {c["id"]: c for c in bank["screen"]["cells"]}
    ids = sum((parts[k] for k in ("source", "development", "protected")), [])
    if (
        bank["name"] != BANK
        or bank["alphabet"] != ALPHABET
        or bank["inputs"] != inputs_for("D625")
        or not bank["screen"]["complete"]
        or bank["screen"]["max_depth"] != 9
        or bank["screen"]["token_ids"] != list(EXECUTABLE)
        or [len(parts[k]) for k in ("source", "development", "protected")] != [4, 4, 8]
        or len(set(ids)) != 16
        or len(bank["clique_ids"]) != bank["maximum_separated"]
        or bank["maximum_separated"] < 16
        or not set(ids) <= set(bank["clique_ids"])
    ):
        raise ValueError("incomplete TS bank/split/screen")
    for c in by.values():
        if (
            hashlib.sha256(np.asarray(c["labels"], dtype="<i8").tobytes()).hexdigest()
            != c["label_hash"]
        ):
            raise ValueError("TS label hash changed")
    clique = [by[cid] for cid in bank["clique_ids"]]
    if not all(
        c["retained"] and c["proper"] and 5 * c["best_matches"] < 4 * 625
        for c in clique
    ):
        raise ValueError("TS short alias admitted")
    labs = np.asarray([c["labels"] for c in clique])
    if any(
        np.any(5 * (labs[i + 1 :] == lab).sum(1) >= 4 * 625)
        for i, lab in enumerate(labs)
    ):
        raise ValueError("TS clique not separated")
    if (
        len({tuple(by[c]["pairing"]) for c in parts["source"]}) < 2
        or len({tuple(by[c]["pairing"]) for c in parts["protected"]}) < 3
        or {v for c in parts["source"] for v in by[c]["roles"].values()}
        != set(range(4))
    ):
        raise ValueError("TS split coverage failure")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deadline-seconds", type=float, default=1200)
    args = parser.parse_args()
    out = Path(os.environ["RUN_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    tick = time.monotonic()
    try:
        bank = build(tick + args.deadline_seconds)
        (out / "bank.json").write_text(json.dumps(bank, allow_nan=False))
    except (TimeoutError, ValueError) as error:
        (out / "infeasible.json").write_text(
            json.dumps(dict(reason=str(error), seconds=time.monotonic() - tick))
        )
        raise


if __name__ == "__main__":
    main()
