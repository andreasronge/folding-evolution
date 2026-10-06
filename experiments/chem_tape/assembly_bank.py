"""Frozen six-shape roster and exhaustive <=9-token semantic screen.

Only executable tokens are enumerated: the five NOP synonyms cannot create a
shorter behaviour. Every complete typed stack is retained through depth 8;
last-level children are evaluated without allocating a depth-9 state frontier.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import resource
import sys
import time

import numpy as np

from experiments.chem_tape.composition_bank import TOKENS, REDUCERS, SemanticMachine
from experiments.chem_tape.composition_search import outputs
from folding_evolution.chem_tape import alphabet as a

DOMAINS = {"D625": (4, -2, 2), "D1331": (3, -5, 5), "D2401": (4, -3, 3)}
SHAPES = ("GA", "BT", "BE", "PA", "D1", "D2")


def inputs_for(domain):
    length, lo, hi = DOMAINS[domain]
    return list(map(list, itertools.product(range(lo, hi + 1), repeat=length)))


def roster(domain):
    xs = np.asarray(inputs_for(domain))
    r = {"S": xs.sum(1), "M": xs.max(1), "m": xs.min(1)}
    cells = []

    def emit(cid, shape, roles, labels, program):
        assert len(program) == 10
        cells.append(
            dict(
                id=cid,
                shape=shape,
                roles=roles,
                canonical=program,
                canonical_hash=hashlib.sha256(bytes(program)).hexdigest(),
                labels=labels.tolist(),
                label_hash=hashlib.sha256(labels.astype("<i8").tobytes()).hexdigest(),
                token_counts={str(t): n for t, n in sorted(Counter(program).items())},
            )
        )

    def push(x):
        return [a.INPUT, REDUCERS[x]]

    for x, y in itertools.combinations("SMm", 2):
        for t, e in itertools.permutations("SMm", 2):
            emit(
                f"GA:({x}+{y})?{t}:{e}",
                "GA",
                dict(gate_x=x, gate_y=y, then=t, other=e),
                np.where(r[x] + r[y] > 0, r[t], r[e]),
                push(e) + push(t) + push(x) + push(y) + [a.ADD, a.IF_GT],
            )
    for k in "SMm":
        for x, y in itertools.combinations("SMm", 2):
            for z in "SMm":
                emit(
                    f"BT:{k}?({x}+{y}):{z}",
                    "BT",
                    dict(condition=k, sum_x=x, sum_y=y, other=z),
                    np.where(r[k] > 0, r[x] + r[y], r[z]),
                    push(z) + push(x) + push(y) + [a.ADD] + push(k) + [a.IF_GT],
                )
                emit(
                    f"BE:{k}?{z}:({x}+{y})",
                    "BE",
                    dict(condition=k, sum_x=x, sum_y=y, then=z),
                    np.where(r[k] > 0, r[z], r[x] + r[y]),
                    push(x) + push(y) + [a.ADD] + push(z) + push(k) + [a.IF_GT],
                )
        for x, y in itertools.permutations("SMm", 2):
            for z in "SMm":
                emit(
                    f"PA:({k}?{x}:{y})+{z}",
                    "PA",
                    dict(condition=k, then=x, other=y, summand=z),
                    np.where(r[k] > 0, r[x], r[y]) + r[z],
                    push(y) + push(x) + push(k) + [a.IF_GT] + push(z) + [a.ADD],
                )
    for x, y in itertools.combinations_with_replacement("SMm", 2):
        for z in "SMm":
            emit(
                f"D2:2({x}+{y})+{z}",
                "D2",
                dict(sum_x=x, sum_y=y, summand=z),
                2 * (r[x] + r[y]) + r[z],
                push(x) + push(y) + [a.ADD, a.DUP, a.ADD] + push(z) + [a.ADD],
            )
    for x in "SMm":
        for y, z in itertools.combinations_with_replacement("SMm", 2):
            emit(
                f"D1:2{x}+{y}+{z}",
                "D1",
                dict(doubled=x, summand_y=y, summand_z=z),
                2 * r[x] + r[y] + r[z],
                push(x) + [a.DUP, a.ADD] + push(y) + [a.ADD] + push(z) + [a.ADD],
            )
    return sorted(cells, key=lambda c: c["id"])


def deadline_check(deadline):
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError("assembly screen deadline reached")


def screen_domain(
    domain,
    max_depth=9,
    deadline=None,
    *,
    cells=None,
    tokens=TOKENS,
    machine_type=SemanticMachine,
    alphabet="v2_rmin",
):
    started = time.monotonic()
    inputs = inputs_for(domain)
    cells = roster(domain) if cells is None else cells
    labels = np.asarray([c["labels"] for c in cells])
    canonical = outputs([[0] * 22 + c["canonical"] for c in cells], inputs, alphabet)
    assert np.array_equal(canonical, labels), "canonical executor disagreement"
    m = machine_type(inputs)
    best = np.full(len(cells), -1)
    witnesses = [None] * len(cells)
    checked = set()

    def check(state, program):
        oid = m.output_id(state)
        if oid in checked:
            return
        checked.add(oid)
        matches = np.count_nonzero(labels == m.values[oid], axis=1)
        for i in np.flatnonzero(matches > best):
            best[i] = matches[i]
            witnesses[i] = list(program)

    seen = {()}
    frontier = {(): b""}
    check((), b"")
    counts = []
    for depth in range(1, max_depth + 1):
        nxt = {} if depth < max_depth else None
        if depth == max_depth:
            # A repeated child needs no state dedup at the output-only level.
            # All earlier outputs have already been checked.
            del seen
        for i, (state, program) in enumerate(frontier.items()):
            if i % 10000 == 0:
                deadline_check(deadline)
            for token in tokens:
                child = m.apply(state, token)
                if nxt is None:
                    check(child, program + bytes([token]))
                elif child not in seen:
                    seen.add(child)
                    rep = program + bytes([token])
                    nxt[child] = rep
                    check(child, rep)
        counts.append(
            dict(
                depth=depth,
                states=None if nxt is None else len(nxt),
                output_only=nxt is None,
                distinct_outputs=len(checked),
                seconds=time.monotonic() - started,
                peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                / (1024**2 if sys.platform == "darwin" else 1024),
            )
        )
        print(domain, counts[-1], flush=True)
        if nxt is not None:
            frontier = nxt
    observed = outputs(witnesses, inputs, alphabet)
    duplicate_groups = {}
    for c in cells:
        duplicate_groups.setdefault(c["label_hash"], []).append(c["id"])
    for i, c in enumerate(cells):
        assert int(np.count_nonzero(observed[i] == labels[i])) == int(best[i])
        c["best_matches"] = int(best[i])
        c["agreement"] = float(best[i] / len(inputs))
        c["witness"] = witnesses[i]
        c["duplicate_ids"] = [
            k for k in duplicate_groups[c["label_hash"]] if k != c["id"]
        ]
        c["alias_kind"] = (
            "exact_identity"
            if best[i] == len(inputs)
            else ("domain_near_alias" if 5 * best[i] >= 4 * len(inputs) else None)
        )
        c["retained"] = c["alias_kind"] is None and not c["duplicate_ids"]
        c["canonical_verified"] = True
    return dict(
        domain=domain,
        domain_size=len(inputs),
        max_depth=max_depth,
        complete=max_depth == 9,
        cells=cells,
        counts=counts,
        wall_seconds=time.monotonic() - started,
        token_ids=list(tokens),
    )


def role_set(cells):
    return {(role, reducer) for c in cells for role, reducer in c["roles"].items()}


def split_shape(cells):
    cells = sorted(cells, key=lambda c: c["id"])
    if len(cells) < 4:
        return None
    for hold in itertools.combinations(cells, 2):
        train = [c for c in cells if c not in hold]
        if role_set(hold) <= role_set(train):

            def primitive_counts(rows):
                counts = Counter()
                for c in rows:
                    counts.update(c["token_counts"])
                return dict(sorted(counts.items()))

            return dict(
                holdouts=[c["id"] for c in hold],
                training=[c["id"] for c in train],
                primitive_counts_training=primitive_counts(train),
                primitive_counts_holdout=primitive_counts(hold),
            )
    return None


def choose_pair(screens):
    eligible, failures = [], []
    for domain, screen in screens.items():
        by_shape = {
            s: [c for c in screen["cells"] if c["shape"] == s and c["retained"]]
            for s in SHAPES
        }
        for left, right in itertools.combinations(sorted(SHAPES), 2):
            ls, rs = split_shape(by_shape[left]), split_shape(by_shape[right])
            multisets = [
                {tuple(c["token_counts"].items()) for c in by_shape[s]}
                for s in (left, right)
            ]
            overlap = sorted(multisets[0] & multisets[1])
            row = dict(
                domain=domain,
                shapes=[left, right],
                retained_counts=[len(by_shape[left]), len(by_shape[right])],
                split={left: ls, right: rs},
                shared_token_multisets=overlap,
            )
            if ls and rs and overlap:
                eligible.append(row)
            else:
                row["reasons"] = [
                    s
                    + (
                        ": fewer than four cells"
                        if len(by_shape[s]) < 4
                        else ": insufficient role coverage"
                    )
                    for s, split in ((left, ls), (right, rs))
                    if not split
                ]
                if not overlap:
                    row["reasons"].append("no shared retained canonical token multiset")
                failures.append(row)
    eligible.sort(
        key=lambda p: (
            -sum(p["retained_counts"]),
            len(inputs_for(p["domain"])),
            p["shapes"],
        )
    )
    return dict(
        selected=eligible[0] if eligible else None, eligible=eligible, failures=failures
    )


def stage_b_domain(screens, pair):
    if pair:
        return pair["domain"]
    return min(
        screens,
        key=lambda d: (
            -sum(c["retained"] and c["shape"] == "PA" for c in screens[d]["cells"]),
            len(inputs_for(d)),
        ),
    )
