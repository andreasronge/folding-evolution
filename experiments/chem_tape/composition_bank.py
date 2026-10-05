"""Exact composition-bank alias probe; no syntactic validity pruning.

The semantic machine interns complete, typed per-domain values. Prefix states
are tuples of these values, including every stack entry, never just outputs.
Negative IDs denote the only list values reachable on this integer-list domain.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import resource
import time
from pathlib import Path

import numpy as np

from folding_evolution.chem_tape import alphabet as a
from folding_evolution.chem_tape.executor import execute_program

TOKENS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 22)
INPUTS = list(map(list, itertools.product(range(-2, 3), repeat=4)))
PAIRS = (("S", "M"), ("S", "m"), ("M", "m"))
REDUCERS = {"S": a.SUM, "M": a.REDUCE_MAX, "m": a.REDUCE_MIN}
TA = a.TaskAlphabet(threshold=0)


def cells():
    xs = np.array(INPUTS)
    r = {"S": xs.sum(1), "M": xs.max(1), "m": xs.min(1)}
    result = []
    for pair in PAIRS:
        for comb in ("ADD", "DADD", "SEL"):
            for x, y in [pair] if comb == "ADD" else (pair, pair[::-1]):
                if comb == "ADD":
                    label = r[x] + r[y]
                    program = [a.INPUT, REDUCERS[x], a.INPUT, REDUCERS[y], a.ADD]
                elif comb == "DADD":
                    label = 2 * r[x] + r[y]
                    program = [
                        a.INPUT,
                        REDUCERS[x],
                        a.DUP,
                        a.ADD,
                        a.INPUT,
                        REDUCERS[y],
                        a.ADD,
                    ]
                else:
                    label = np.where(r["S"] > 0, r[x], r[y])
                    program = [
                        a.INPUT,
                        REDUCERS[y],
                        a.INPUT,
                        REDUCERS[x],
                        a.INPUT,
                        a.SUM,
                        a.IF_GT,
                    ]
                result.append(
                    dict(
                        id="".join(pair) + "-" + comb,
                        x=x,
                        y=y,
                        labels=label,
                        canonical=program,
                    )
                )
    return result


class SemanticMachine:
    # -1=input intlist, -2=empty intlist, -3=empty charlist. No string
    # input/producer exists. Integer vector IDs are >=0.
    def __init__(self):
        self.values = []
        self.ids = {}
        self.zero = self.intern(np.zeros(625, dtype=np.int64))
        self.constants = {
            k: self.intern(np.full(625, k, dtype=np.int64)) for k in (0, 1, 2, 5)
        }
        xs = np.array(INPUTS)
        self.reduced = {
            a.SUM: self.intern(xs.sum(1)),
            a.REDUCE_ADD: self.intern(xs.sum(1)),
            a.ANY: self.intern(np.any(xs != 0, axis=1).astype(np.int64)),
            a.REDUCE_MAX: self.intern(xs.max(1)),
            a.REDUCE_MIN: self.intern(xs.min(1)),
        }
        self.cache = {}

    def intern(self, v):
        key = v.tobytes()
        if key not in self.ids:
            self.ids[key] = len(self.values)
            self.values.append(v)
        return self.ids[key]

    def apply(self, state, token):
        stack = list(state)

        def pop_int():
            return stack.pop() if stack and stack[-1] >= 0 else self.zero

        def pop_list(kind):
            if stack and stack[-1] in kind:
                return stack.pop()
            return -2 if -2 in kind else -3

        if token == a.INPUT:
            stack.append(-1)
        elif token in (a.CONST_0, a.CONST_1, a.CONST_2, a.CONST_5, a.THRESHOLD_SLOT):
            stack.append(self.constants[{2: 0, 3: 1, 15: 2, 16: 5, 19: 0}[token]])
        elif token == a.DUP:
            if not stack:
                stack.extend((self.zero, self.zero))
            else:
                stack.append(stack[-1])
        elif token == a.SWAP:
            b = stack.pop() if stack else self.zero
            x = stack.pop() if stack else self.zero
            stack.extend((b, x))
        elif token in self.reduced:
            v = pop_list((-1, -2))
            stack.append(self.reduced[token] if v == -1 else self.zero)
        elif token == a.CHARS:
            # No string value is reachable: wrong type is preserved.
            stack.append(-3)
        elif token == a.MAP_EQ_E:
            pop_list((-3,))
            stack.append(-2)
        elif token in (a.ADD, a.GT):
            b, x = pop_int(), pop_int()
            key = (token, x, b)
            if key not in self.cache:
                v = (
                    self.values[x] + self.values[b]
                    if token == a.ADD
                    else (self.values[x] > self.values[b]).astype(np.int64)
                )
                self.cache[key] = self.intern(v)
            stack.append(self.cache[key])
        elif token == a.IF_GT:
            short = len(stack) < 3
            cond, then, other = pop_int(), pop_int(), pop_int()
            if short:
                stack.append(self.zero)
            else:
                key = (token, cond, then, other)
                if key not in self.cache:
                    self.cache[key] = self.intern(
                        np.where(
                            self.values[cond] > 0, self.values[then], self.values[other]
                        )
                    )
                stack.append(self.cache[key])
        else:
            raise ValueError(token)
        return tuple(stack)

    def output_id(self, state):
        return state[-1] if state and state[-1] >= 0 else self.zero


def rust_outputs(programs):
    from _folding_rust import rust_chem_execute_pop_batch

    return np.asarray(
        rust_chem_execute_pop_batch(
            programs, "NOP", "NOP", INPUTS, "intlist", "v2_rmin", 0
        ),
        dtype=np.int64,
    ).reshape(len(programs), 625)


def screen(max_depth=6, stop_on_impossible=False):
    start = time.monotonic()
    machine = SemanticMachine()
    targets = cells()
    best = [dict(matches=-1, program=[]) for _ in targets]
    seen = {(): ()}
    frontier = {(): ()}
    checked = set()
    counts = []
    for depth in range(max_depth + 1):
        # An output first reached at d can only screen canonicals longer than d.
        for state, program in frontier.items():
            out_id = machine.output_id(state)
            if out_id in checked:
                continue
            checked.add(out_id)
            out = machine.values[out_id]
            for i, cell in enumerate(targets):
                if depth < len(cell["canonical"]):
                    matches = int(np.count_nonzero(out == cell["labels"]))
                    if matches > best[i]["matches"]:
                        best[i] = dict(matches=matches, program=list(program))
        grouped = {}
        for c, b in zip(targets, best):
            grouped.setdefault(c["id"], []).append(b["matches"] >= 500)
        failed = [cid for cid, fs in grouped.items() if all(fs)]
        counts.append(
            dict(
                depth=depth,
                states=len(frontier),
                total_states=len(seen),
                distinct_outputs=len(checked),
                values=len(machine.values),
                seconds=time.monotonic() - start,
                proven_failed=failed,
                peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                / (1024 * 1024 if __import__("sys").platform == "darwin" else 1024),
            )
        )
        print(json.dumps(counts[-1]), flush=True)
        if stop_on_impossible and len(failed) >= 3:
            break
        if depth == max_depth:
            break
        nxt = {}
        for state, program in frontier.items():
            for token in TOKENS:
                child = machine.apply(state, token)
                if child not in seen:
                    rep = program + (token,)
                    seen[child] = rep
                    nxt[child] = rep
        frontier = nxt
    rows = []
    for cell, b in zip(targets, best):
        witness = b["program"]
        exact = rust_outputs([witness])[0]
        reference = np.array(
            [execute_program(witness, TA, inp, "intlist", "v2_rmin") for inp in INPUTS]
        )
        assert np.array_equal(exact, reference)
        assert int(np.count_nonzero(exact == cell["labels"])) == b["matches"]
        canonical = rust_outputs(
            [[a.NOP] * (32 - len(cell["canonical"])) + cell["canonical"]]
        )[0]
        assert np.array_equal(canonical, cell["labels"])
        rows.append(
            dict(
                id=cell["id"],
                x=cell["x"],
                y=cell["y"],
                canonical=cell["canonical"],
                best_shorter_matches=b["matches"],
                agreement=b["matches"] / 625,
                witness=witness,
                rejects=b["matches"] >= 500,
            )
        )
    return dict(
        domain_size=625,
        threshold_matches=500,
        token_ids=list(TOKENS),
        alphabet="v2_rmin",
        threshold_slot=0,
        stage_a_complete=depth == 6,
        depth_completed=depth,
        counts=counts,
        oriented_cells=rows,
        proven_failed=failed,
        maximum_possible_survivors=9 - len(failed),
        wall_seconds=time.monotonic() - start,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--stop-on-impossible", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = screen(args.max_depth, args.stop_on_impossible)
    out = args.output or Path(os.environ["RUN_DIR"]) / "alias_probe.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
