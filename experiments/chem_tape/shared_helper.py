#!/usr/bin/env python3
"""Shared helpers, stages 1-2 (Plans/shared-helper-reuse.md; map-bias notebook §29).

Three rewarded outputs read from output tags 0, 1, 2 (leftmost-wins, alphabet "tagged"):
    tag 0: A = max > 5      tag 1: A and B      tag 2: A or B      (B = sum > 10)

Stage 1 (express): three hand-built forms, checked on all 10,000 length-4 lists over [0, 9]:
    shared      A (tag 0), B (tag 3), tags 1 and 2 read both by RECV
    partly      tags 1 and 2 read A by RECV and recompute B
    duplicated  tags 1 and 2 recompute A and B in their own body
Knockout: replace one run's body with NOPs and re-evaluate the three outputs on all lists;
the run's consumer count is the number of outputs that change.

Stage 2 (preserve): variation only, no selection. For each form and tape length, 10,000
children per operator cell: mutation at the §25 rate, and crossover v1 / v2 / v1c with
the form as parent A (random parent B), as parent B (random parent A), and against the
other form.

Usage:
    uv run python experiments/chem_tape/shared_helper.py express --out "$RUN_DIR"
    uv run python experiments/chem_tape/shared_helper.py preserve --out "$RUN_DIR" --workers 8
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import random
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from folding_evolution.chem_tape import tagged  # noqa: E402
from folding_evolution.chem_tape.alphabet import (  # noqa: E402
    ADD, CONST_0, CONST_1, CONST_5, GT, INPUT, REDUCE_MAX, SUM,
)
from folding_evolution.chem_tape.tagged import RECV, SEP  # noqa: E402

OUTPUT_TAGS = (0, 1, 2)
HELPER_TAG = 3
LENGTHS = (32, 64, 128)
MUTATION_RATE = 0.015                    # §25 (xover_v2_xor_leftmost.yaml)
VARIANTS = ("v1", "v2", "v1c")
PAIRINGS = ("form_A", "form_B", "other")

X_ALL = np.array(list(itertools.product(range(10), repeat=4)), dtype=np.int64)
PRED_A = (X_ALL.max(axis=1) > 5).astype(np.int64)
PRED_B = (X_ALL.sum(axis=1) > 10).astype(np.int64)
LABELS = np.stack([PRED_A, PRED_A & PRED_B, PRED_A | PRED_B])      # (3, 10000)
SUBSET = slice(None, None, 20)            # prefilter: every 20th list (500), as _ExactTracker

A_BODY = [INPUT, REDUCE_MAX, CONST_5, GT]
B_BODY = [INPUT, SUM, CONST_5, CONST_5, ADD, GT]
AND_TAIL = [ADD, CONST_1, GT]            # a + b > 1 on 0/1 values
OR_TAIL = [ADD, CONST_0, GT]             # a + b > 0


def _cells(ops):
    return [op if isinstance(op, tuple) else (op, 0) for op in ops]


def _recv(t):
    return (RECV, t)


FORMS = {
    "shared": [(0, A_BODY), (HELPER_TAG, B_BODY),
               (1, [_recv(0), _recv(HELPER_TAG)] + AND_TAIL),
               (2, [_recv(0), _recv(HELPER_TAG)] + OR_TAIL)],
    "partly": [(0, A_BODY), (1, [_recv(0)] + B_BODY + AND_TAIL), (2, [_recv(0)] + B_BODY + OR_TAIL)],
    "duplicated": [(0, A_BODY), (1, A_BODY + B_BODY + AND_TAIL), (2, A_BODY + B_BODY + OR_TAIL)],
}
OTHER = {"shared": "duplicated", "duplicated": "shared", "partly": "shared"}


def form_cells(name: str) -> int:
    return sum(1 + len(body) for _, body in FORMS[name])


def form_genome(name: str, L: int) -> np.ndarray | None:
    """The hand-built form on an L-cell tape (NOP padding with fixed random tags), or None
    if it does not fit."""
    if form_cells(name) > L:
        return None
    runs = [(tag, tuple(_cells(body))) for tag, body in FORMS[name]]
    return tagged.build([], runs, L, random.Random(L))


# ---------------- multi-output evaluation ----------------

def machine(inputs: np.ndarray = X_ALL):
    """Interpreter over `inputs`; mbs_* tasks bind THRESHOLD_SLOT to 0."""
    return tagged._Machine(inputs, 0)


def outputs(g: np.ndarray, m, body_cache: dict | None = None) -> np.ndarray:
    """(3, E): the value of output tags 0, 1, 2 under leftmost-wins (first run of the tag;
    0 if the tag has no run). A run's value with RECVs resolved is the same at the top
    level as when read as an output, so this is genome_outputs per output tag."""
    runs = tagged.parse_runs(g)
    first: dict[int, int] = {}
    for k, (t, _) in enumerate(runs):
        first.setdefault(t, k)
    out = np.zeros((len(OUTPUT_TAGS), m.E), dtype=np.int64)
    if not any(t in first for t in OUTPUT_TAGS):
        return out
    vals = tagged.genome_outputs(g, m, body_cache, all_runs=True, combine="leftmost")
    for o, t in enumerate(OUTPUT_TAGS):
        if t in first:
            out[o] = vals[first[t]]
    return out


def run_spans(g: np.ndarray) -> list[tuple[int, int, int]]:
    """(tag, first body cell, end) per run, in tape order (cells as in tagged.parse_runs)."""
    ops, tags = tagged.split(g)
    spans, cur = [], None
    for i, op in enumerate(ops.tolist()):
        if op == SEP:
            if cur is not None:
                spans.append((cur[0], cur[1], i))
            cur = (int(tags[i]), i + 1)
    if cur is not None:
        spans.append((cur[0], cur[1], len(ops)))
    return spans


def knockout(g: np.ndarray, k: int) -> np.ndarray:
    """g with run k's body replaced by NOPs (its SEP, tag and every other cell kept)."""
    _, lo, hi = run_spans(g)[k]
    out = g.copy()
    out[lo:hi] = 0
    return out


def consumer_counts(g: np.ndarray, m=None, body_cache: dict | None = None,
                    base: np.ndarray | None = None) -> list[int]:
    """Per run (tape order): how many of the three outputs change on any input when the
    run's body is knocked out."""
    m = m or machine()
    base = outputs(g, m, body_cache) if base is None else base
    return [int((outputs(knockout(g, k), m, body_cache) != base).any(axis=1).sum())
            for k in range(len(run_spans(g)))]


def classify(g: np.ndarray, m=None, body_cache: dict | None = None) -> dict:
    """Exactness per output on all lists, consumer counts and the form of the genome.

    output-as-helper: the first tag-0 run with consumer count >= 2. pure helper: a run
    that is not the first run of tags 0-2, with consumer count >= 2. Form (fully exact
    genomes only): shared (has a pure helper), partly (output-as-helper only), duplicated
    (neither). `other_output_helper`: the first run of tag 1 or 2 has consumer count >= 2
    (not in the plan's three labels; reported so it is not silently called duplicated)."""
    m = m or machine()
    base = outputs(g, m, body_cache)
    exact = [bool(v) for v in (base == LABELS).all(axis=1)]
    counts = consumer_counts(g, m, body_cache, base)
    tags = [t for t, _, _ in run_spans(g)]
    first = {}
    for k, t in enumerate(tags):
        first.setdefault(t, k)
    out_runs = {first[t] for t in OUTPUT_TAGS if t in first}
    oah = 0 in first and counts[first[0]] >= 2
    pure = [k for k, c in enumerate(counts) if c >= 2 and k not in out_runs]
    other = any(t in first and counts[first[t]] >= 2 for t in (1, 2))
    full = all(exact)
    form = None
    if full:
        form = "shared" if pure else "partly" if oah else "duplicated"
    return {"exact": exact, "fully_exact": full, "consumer_counts": counts, "tags": tags,
            "output_as_helper": bool(oah), "pure_helpers": pure,
            "other_output_helper": bool(other), "form": form}


def semantic_key(g: np.ndarray) -> tuple:
    """What a genome computes: its runs with RECV tags, trailing NOPs stripped (as
    evolve._ExactTracker._semantic_keys)."""
    return tuple((t, tuple((op, tg if op == RECV else 0) for op, tg in tagged._strip_trailing_nops(body)))
                 for t, body in tagged.parse_runs(g))


class Exactness:
    """Per-output exactness on all 10,000 lists, cached by semantic key; genomes wrong on
    the 500-list subset for every output skip the full evaluation."""

    def __init__(self) -> None:
        self.m_sub, self.m_full = machine(X_ALL[SUBSET]), machine(X_ALL)
        self.c_sub, self.c_full = {}, {}
        self.cache: dict[tuple, np.ndarray] = {}

    def __call__(self, g: np.ndarray) -> np.ndarray:
        key = semantic_key(g)
        hit = self.cache.get(key)
        if hit is None:
            ok = (outputs(g, self.m_sub, self.c_sub) == LABELS[:, SUBSET]).all(axis=1)
            if ok.any():
                ok = ok & (outputs(g, self.m_full, self.c_full) == LABELS).all(axis=1)
            hit = self.cache[key] = ok
            if len(self.cache) > 200_000:
                self.cache.clear()
        return hit


# ---------------- stage 1 ----------------

def express() -> dict:
    m, cache = machine(), {}
    rows = []
    for name in FORMS:
        for L in LENGTHS:
            g = form_genome(name, L)
            row = {"form": name, "cells": form_cells(name), "L": L, "fits": g is not None}
            if g is not None:
                c = classify(g, m, cache)
                row.update({k: c[k] for k in ("exact", "fully_exact", "consumer_counts", "tags",
                                               "output_as_helper", "pure_helpers", "form")})
                row["classified_as"] = row.pop("form")
                row["form"] = name
                row["genome_hex"] = g.tobytes().hex()
            rows.append(row)
    return {"forms": {n: [(t, [list(c) if isinstance(c, tuple) else c for c in b]) for t, b in FORMS[n]]
                      for n in FORMS},
            "rows": rows}


def express_table(res: dict) -> str:
    lines = ["| form | cells | L | fits | fully exact | classified as | consumer counts (tags) |",
             "|---|---|---|---|---|---|---|"]
    for r in res["rows"]:
        if r["fits"]:
            cc = ", ".join(f"{t}:{c}" for t, c in zip(r["tags"], r["consumer_counts"]))
            lines.append(f"| {r['form']} | {r['cells']} | {r['L']} | yes | {r['fully_exact']} | "
                         f"{r['classified_as']} | {cc} |")
        else:
            lines.append(f"| {r['form']} | {r['cells']} | {r['L']} | no | | | |")
    return "\n".join(lines)


# ---------------- stage 2 ----------------

def helper_intact(g: np.ndarray) -> bool:
    """The first run tagged HELPER_TAG still has B's body (trailing NOPs ignored)."""
    for t, body in tagged.parse_runs(g):
        if t == HELPER_TAG:
            return [op for op, _ in tagged._strip_trailing_nops(body)] == B_BODY
    return False


def children(form: str, L: int, op: str, pairing: str | None, n: int, seed: int) -> list[np.ndarray]:
    """n children of one operator cell. Mutation: tagged.mutate_batch (the fast_rng path
    the §25 sweeps use) at MUTATION_RATE. Crossover: tagged.crossover(variant)."""
    parent = form_genome(form, L)
    if op == "mutation":
        gen = np.random.default_rng(seed)
        return list(tagged.mutate_batch(np.repeat(parent[None, :], n, axis=0), MUTATION_RATE, gen))
    rng = random.Random(seed)
    other = form_genome(OTHER[form], L) if pairing == "other" else None
    out = []
    for _ in range(n):
        if pairing == "form_A":
            a, b = parent, tagged.random_genotype(L, rng)
        elif pairing == "form_B":
            a, b = tagged.random_genotype(L, rng), parent
        else:
            a, b = parent, other
        out.append(tagged.crossover(a, b, rng, op))
    return out


def preserve_cell(args: tuple) -> dict:
    form, L, op, pairing, n, seed = args
    t0 = time.time()
    ex = Exactness()
    kids = children(form, L, op, pairing, n, seed)
    E = np.array([ex(g) for g in kids])                      # (n, 3)
    row = {"form": form, "L": L, "op": op, "pairing": pairing, "n": n, "seed": seed,
           "fully_exact": float(E.all(axis=1).mean()),
           "keep": [float(v) for v in E.mean(axis=0)],
           "mean_lost": float((3 - E.sum(axis=1)).mean()),
           "identical": float(np.mean([np.array_equal(k, form_genome(form, L)) for k in kids])),
           "secs": 0.0}
    if form == "shared":
        row["helper_intact"] = float(np.mean([helper_intact(k) for k in kids]))
    row["secs"] = round(time.time() - t0, 1)
    return row


def preserve_cells(n: int) -> list[tuple]:
    cells = []
    seed = 0
    for form in FORMS:
        for L in LENGTHS:
            if form_genome(form, L) is None:
                continue
            cells.append((form, L, "mutation", None, n, seed))
            seed += 1
            for v in VARIANTS:
                for p in PAIRINGS:
                    if p == "other" and form_genome(OTHER[form], L) is None:
                        continue
                    cells.append((form, L, v, p, n, seed))
                    seed += 1
    return cells


def preserve_table(rows: list[dict]) -> str:
    lines = ["| L | op | pairing | form | fully exact | keep tag 0 / 1 / 2 | mean outputs lost | helper intact |",
             "|---|---|---|---|---|---|---|---|"]
    def key(r):
        return (r["L"], (("mutation",) + VARIANTS).index(r["op"]),
                PAIRINGS.index(r["pairing"]) if r["pairing"] else -1, list(FORMS).index(r["form"]))

    for r in sorted(rows, key=key):
        keep = " / ".join(f"{k:.3f}" for k in r["keep"])
        hi = f"{r['helper_intact']:.3f}" if "helper_intact" in r else ""
        lines.append(f"| {r['L']} | {r['op']} | {r['pairing'] or ''} | {r['form']} | {r['fully_exact']:.3f} | "
                     f"{keep} | {r['mean_lost']:.3f} | {hi} |")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["express", "preserve"])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n", type=int, default=10_000)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.stage == "express":
        res = express()
        (args.out / "express.json").write_text(json.dumps(res, indent=2))
        (args.out / "express.md").write_text(express_table(res) + "\n")
        print(express_table(res))
        return 0
    cells = preserve_cells(args.n)
    print(f"{len(cells)} cells x {args.n} trials, {args.workers} workers", flush=True)
    rows = []
    with mp.get_context("spawn").Pool(args.workers) as pool:
        for r in pool.imap_unordered(preserve_cell, cells):
            rows.append(r)
            print(f"  {r['form']} L={r['L']} {r['op']} {r['pairing']}: fully exact {r['fully_exact']:.3f} "
                  f"({r['secs']}s)", flush=True)
            (args.out / "preserve.json").write_text(json.dumps({"n": args.n, "rows": rows}, indent=2))
    (args.out / "preserve.md").write_text(preserve_table(rows) + "\n")
    print(preserve_table(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
