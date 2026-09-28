"""Mutation neighbourhoods of leftmost-XOR plateau specialists and non-solvers (notebook §20).

Eleventh review: solvers of tagged leftmost XOR (§19) sit as exact three-quadrant
specialists at 0.75 for hundreds of generations before a 1-2 cell step. Is there an
exact-XOR or a case-gaining move next to those plateau genomes, and next to the final
champions of runs that never solved? Empty neighbourhoods on non-solvers would be a valley
under lexicase; plenty of moves would mean they are on the same plateau and just haven't
drawn the step.

Genomes scanned per run (from history.csv, the best genome of each generation):
  solvers      the champion 100 generations before the first exact generation ("plateau")
  non-solvers  the final champion (generation 3000)

Single mutants = the tagged mutation operator's moves that can change behaviour:
  - op change at any cell (every other op);
  - tag change on SEP and RECV cells (tags on other cells are inert);
  - deletion of any cell (the genome is NOP-padded at the end);
  - insertion after any cell of every non-RECV op (one tag: inert), or RECV with every tag.
Double mutants: a random sample: one single mutant, then one random op / tag / deletion /
insertion move on it.

Per genome: training balanced fitness; how many single / sampled double mutants are exact
on all 10,000 lists; how many dominate the parent on training cases (gain one, lose none);
how many trade cases (gain some, lose others: lexicase may still pick these, depending on
the rest of the population); how many raise balanced fitness; how many are neutral.

Usage: uv run python experiments/chem_tape/xor_neighbourhood.py <sweep dir> <out.json> [--pairs N]
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import random
import sys
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import overnight_analysis as oa  # noqa: E402

from folding_evolution.chem_tape import tagged  # noqa: E402
from folding_evolution.chem_tape.tasks import build_task  # noqa: E402

PLATEAU_OFFSET = 100


def singles(g: np.ndarray, n_ops: int) -> list[np.ndarray]:
    L = len(g) // 2
    ops, tags = g[:L], g[L:]
    out = []
    for i in range(L):
        for o in range(n_ops):
            if o != ops[i]:
                h = g.copy(); h[i] = o; out.append(h)
        if ops[i] in (tagged.SEP, tagged.RECV):
            for t in range(tagged.N_TAGS):
                if t != tags[i]:
                    h = g.copy(); h[L + i] = t; out.append(h)
        # deletion: shift left, pad with NOP
        o2 = np.concatenate([np.delete(ops, i), [0]]); t2 = np.concatenate([np.delete(tags, i), [0]])
        out.append(np.concatenate([o2, t2]).astype(np.uint8))
    # Insertion as in tagged.mutate_batch: a new cell right after a kept cell, so at
    # positions 1..L-1 (never at the front); truncate to L. Tags matter on SEP (run tag) and
    # RECV (read tag), so those get every tag; other ops one (inert) tag.
    news = [(o, 0) for o in range(n_ops) if o not in (tagged.RECV, tagged.SEP)] + \
        [(o, t) for o in (tagged.SEP, tagged.RECV) for t in range(tagged.N_TAGS)]
    for i in range(1, L):
        for o, t in news:
            o2 = np.insert(ops, i, o)[:L]; t2 = np.insert(tags, i, t)[:L]
            out.append(np.concatenate([o2, t2]).astype(np.uint8))
    return out


def evaluate(genomes, task, combine, labels):
    _, preds = tagged.evaluate_tagged(genomes, task, combine=combine)
    ok = preds == labels[None, :]
    pos = labels == 1
    bal = 0.5 * (ok[:, pos].mean(axis=1) + ok[:, ~pos].mean(axis=1))
    return ok, bal


def scan(item) -> dict:
    run_dir, c, role, gen, pairs = item
    cfg = oa.cfg_of(c)
    rows = list(csv.DictReader(open(Path(run_dir) / "history.csv")))
    g = np.frombuffer(bytes.fromhex(rows[gen]["best_genotype_hex"]), dtype=np.uint8).copy()
    task = build_task(cfg, cfg.seed)
    full = replace(task, inputs=oa.ALL, labels=oa.LABELS[cfg.task])
    comb = cfg.tag_combine
    n_ops = tagged.n_ops_for(cfg.alphabet)
    ok0, bal0 = evaluate([g], task, comb, task.labels)
    ok0, bal0 = ok0[0], float(bal0[0])

    def summarise(ms):
        ok, bal = evaluate(ms, task, comb, task.labels)
        gains = (ok & ~ok0[None, :]).any(axis=1)
        losses = (~ok & ok0[None, :]).any(axis=1)
        gain = gains & ~losses            # dominates the parent on training cases
        train_exact = ok.all(axis=1)
        n_exact = 0
        if train_exact.any():
            cand = [m for m, e in zip(ms, train_exact) if e]
            fok, _ = evaluate(cand, full, comb, full.labels)
            n_exact = int(fok.all(axis=1).sum())
        return {"n": len(ms), "exact": n_exact, "train_exact": int(train_exact.sum()),
                "case_gain": int(gain.sum()), "case_trade": int((gains & losses).sum()),
                "fitter": int((bal > bal0 + 1e-9).sum()),
                "neutral": int((np.abs(bal - bal0) < 1e-9).sum()), "best": float(bal.max())}

    s1 = singles(g, n_ops)
    one = summarise(s1)
    rng = random.Random(int(c["seed"]) * 1000 + gen)
    L = len(g) // 2
    doubles = []
    for _ in range(pairs):
        h = s1[rng.randrange(len(s1))]
        # second move: a random single mutant of h (cheap: one random op/tag/indel move)
        k = rng.randrange(4)
        h = h.copy()
        i = rng.randrange(1, L) if k == 2 else rng.randrange(L)
        if k == 0:
            h[i] = rng.randrange(n_ops)
        elif k == 1:
            h[L + i] = rng.randrange(tagged.N_TAGS)
        elif k == 3:
            h = np.concatenate([np.append(np.delete(h[:L], i), 0), np.append(np.delete(h[L:], i), 0)]).astype(np.uint8)
        else:                        # k == 2: insertion after cell i-1
            o = rng.randrange(n_ops); t = rng.randrange(tagged.N_TAGS)
            h = np.concatenate([np.insert(h[:L], i, o)[:L], np.insert(h[L:], i, t)[:L]]).astype(np.uint8)
        doubles.append(h)
    two = summarise(doubles) if pairs else None
    fok0, _ = evaluate([g], full, comb, full.labels)
    runs = tagged.parse_runs(g)
    return {"seed": c["seed"], "role": role, "gen": gen, "train_bal": bal0,
            "full_acc": float(fok0[0].mean()), "n_runs": len(runs), "single": one, "double": two}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep")
    ap.add_argument("out")
    ap.add_argument("--pairs", type=int, default=20000)
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    sweep = Path(a.sweep)
    loaded = oa.load(sweep)
    rows = json.loads((sweep / "analysis.json").read_text())
    assert len(loaded) == len(rows)
    items = []
    for (run_dir, c), r in zip(loaded, rows):
        assert r["seed"] == c["seed"]
        if r["first_exact_gen"] is not None:
            items.append((run_dir, c, "solver_plateau", max(0, r["first_exact_gen"] - PLATEAU_OFFSET), a.pairs))
        else:
            n = sum(1 for _ in open(Path(run_dir) / "history.csv")) - 2
            items.append((run_dir, c, "non_solver_final", n, a.pairs))
    with Pool(a.workers) as pool:
        res = pool.map(scan, items)
    Path(a.out).write_text(json.dumps(res, indent=1))
    for role in ("solver_plateau", "non_solver_final"):
        rs = [r for r in res if r["role"] == role]
        print(f"\n{role} ({len(rs)})")
        print("seed gen train_bal full_acc | single: n exact dominate trade fitter neutral | "
              "double: n exact dominate trade fitter")
        for r in sorted(rs, key=lambda r: r["seed"]):
            s, d = r["single"], r["double"] or {}
            print(f"{r['seed']:>3} {r['gen']:>5} {r['train_bal']:.3f} {r['full_acc']:.3f} | "
                  f"{s['n']:>5} {s['exact']:>3} {s['case_gain']:>4} {s['case_trade']:>5} {s['fitter']:>4} "
                  f"{s['neutral']:>5} | {d.get('n', 0):>6} {d.get('exact', 0):>3} {d.get('case_gain', 0):>5} "
                  f"{d.get('case_trade', 0):>6} {d.get('fitter', 0):>5}")


if __name__ == "__main__":
    main()
