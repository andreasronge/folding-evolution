"""Guaranteed-supply merge test (map-bias notebook §7).

Can recombination put a max>5 block and a sum>10 block together into an exact
AND without crashing? Static test, no AND evolution:

1. Donor pools. For each chemistry, evolve populations on `mb_max_gt_5` and on
   `mb_sum_gt_10` (same slot/threshold bindings as the AND task) and keep the
   genomes that compute their predicate exactly on all 10,000 lists.
2. Crosses between a max>5 donor and a sum>10 donor, in both orders:
   - baseline single-point: current chem decoder (BP_TOPK), child = X[:c] + Y[c:]
   - v3 single-point: same splice on v3 tapes (what v3 evolution used)
   - v3 transplant: one whole domain of Y inserted at each domain boundary of X,
     with each of the 6 linker types (tapes may grow beyond 32)
3. Every child is scored on all 10,000 lists against the AND labels:
   exact AND, crash (balanced accuracy below the *weaker* parent - 0.05, i.e.
   clearly worse than both), same behaviour as one parent, and
   whether both predicates survive as pieces (a substring for baseline, a whole
   domain for v3).

Usage: uv run python experiments/chem_tape/merge_test.py experiments/output/2026-09-26/merge_test
"""

from __future__ import annotations

import collections
import itertools
import json
import os
import sys
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np

os.environ.setdefault("RAYON_NUM_THREADS", "4")

from folding_evolution.chem_tape.config import ChemTapeConfig  # noqa: E402
from folding_evolution.chem_tape.domains import LINKERS, domain_values, split_domains  # noqa: E402
from folding_evolution.chem_tape.evaluate import _programs_for_arm, evaluate_population  # noqa: E402
from folding_evolution.chem_tape.evolve import run_evolution  # noqa: E402
from folding_evolution.chem_tape.tasks import build_task  # noqa: E402

ALL_LISTS = [tuple(int(v) for v in x) for x in itertools.product(range(10), repeat=4)]
MAX_GT_5 = np.array([int(max(x) > 5) for x in ALL_LISTS], dtype=np.int64)
SUM_GT_10 = np.array([int(sum(x) > 10) for x in ALL_LISTS], dtype=np.int64)
AND = MAX_GT_5 & SUM_GT_10
POS = AND == 1
PRED = {"max>5": MAX_GT_5, "sum>10": SUM_GT_10}
CRASH = 0.05
POOL = 25          # donors kept per (chemistry, predicate)
SEEDS = range(8)

CHEMS = {
    "baseline": dict(arm="BP_TOPK", alphabet="v2_probe", topk=3, bond_protection_ratio=0.5),
    "v3": dict(arm="V3", alphabet="v3_domains"),
}


def cfg_for(chem: str, task: str, seed: int) -> ChemTapeConfig:
    return ChemTapeConfig(task=task, seed=seed, pop_size=1024, generations=400, backend="numpy",
                          n_examples=64, holdout_size=0, disable_early_termination=True,
                          dump_final_population=True, **CHEMS[chem])


def full_task(cfg: ChemTapeConfig, labels: np.ndarray):
    return replace(build_task(cfg, 0), inputs=ALL_LISTS, labels=labels)


def bacc_and(preds: np.ndarray) -> np.ndarray:
    ok = preds == AND
    return 0.5 * (ok[:, POS].mean(axis=1) + ok[:, ~POS].mean(axis=1))


def evolve_donors(item) -> tuple[str, str, list[bytes]]:
    chem, pred, seed = item
    task_name = "mb_max_gt_5" if pred == "max>5" else "mb_sum_gt_10"
    cfg = cfg_for(chem, task_name, seed)
    res = run_evolution(cfg)
    uniq = np.unique(res.final_population, axis=0)
    _, preds = evaluate_population(list(uniq), full_task(cfg, PRED[pred]), cfg)
    exact = uniq[(preds == PRED[pred]).all(axis=1)]
    return chem, pred, [g.tobytes() for g in exact[:POOL]]


class PieceCheck:
    """Does some contiguous piece of a baseline program compute a predicate exactly?"""

    def __init__(self, cfg: ChemTapeConfig):
        from _folding_rust import rust_chem_execute_pop_batch
        self.exec, self.cfg = rust_chem_execute_pop_batch, cfg
        self.task = build_task(cfg, 0)
        rng = np.random.default_rng(0)
        self.screen_idx = np.concatenate([
            rng.choice(np.flatnonzero((MAX_GT_5 == m) & (SUM_GT_10 == t)), 8, replace=False)
            for m in (0, 1) for t in (0, 1)])
        self.cache: dict[tuple, tuple[bool, bool]] = {}      # exact on all 10k lists
        self.screened: dict[tuple, tuple[bool, bool]] = {}   # passes the 32-list screen

    def _run(self, progs, idx):
        inputs = [ALL_LISTS[i] for i in idx]
        flat = self.exec(progs, self.task.alphabet.slot_12, self.task.alphabet.slot_13, inputs,
                         "intlist", alphabet_name=self.cfg.alphabet, threshold=int(self.task.alphabet.threshold))
        return np.asarray(flat, dtype=np.int64).reshape(len(progs), len(idx))

    def _screen(self, subs: set) -> None:
        new = [x for x in subs if x not in self.screened]
        for x in new:  # must read the input and aggregate it to compute either predicate
            if 1 not in x or not {5, 11, 18} & set(x):
                self.screened[x] = (False, False)
        new = [x for x in new if x not in self.screened]
        if new:
            out = self._run([list(x) for x in new], self.screen_idx)
            for x, o in zip(new, out):
                self.screened[x] = (bool((o == MAX_GT_5[self.screen_idx]).all()),
                                    bool((o == SUM_GT_10[self.screen_idx]).all()))

    def both(self, progs: list[list[int]]) -> np.ndarray:
        """Per program: some piece computes max>5 exactly AND some piece computes
        sum>10 exactly. Screen-passing candidates are confirmed shortest-first."""
        per = [sorted({tuple(p[i:j]) for i in range(len(p)) for j in range(i + 1, len(p) + 1)}, key=len)
               for p in progs]
        self._screen({x for subs in per for x in subs})
        result = []
        for k in (0, 1):
            cands = [[x for x in subs if self.screened[x][k]] for subs in per]
            pos, answer = [0] * len(per), [None] * len(per)
            while True:
                need = set()
                for n, cs in enumerate(cands):
                    while answer[n] is None:
                        if pos[n] >= len(cs):
                            answer[n] = False
                        elif cs[pos[n]] in self.cache:
                            if self.cache[cs[pos[n]]][k]:
                                answer[n] = True
                            else:
                                pos[n] += 1
                        else:
                            need.add(cs[pos[n]])
                            break
                if not need:
                    break
                need = list(need)
                full = self._run([list(x) for x in need], range(len(ALL_LISTS)))
                for x, o in zip(need, full):
                    self.cache[x] = (bool((o == MAX_GT_5).all()), bool((o == SUM_GT_10).all()))
            result.append(answer)
        return np.array([a and b for a, b in zip(*result)], dtype=bool)


def v3_both(children: list[np.ndarray], task) -> np.ndarray:
    """Both predicates present as whole domains (expressed or silent)."""
    doms = [split_domains(c) for c in children]
    uniq = list({d for ds in doms for _, d in ds})
    if not uniq:
        return np.zeros(len(children), dtype=bool)
    vals = dict(zip(uniq, domain_values(uniq, task)))
    out = []
    for ds in doms:
        roles = [("max" if (vals[d] == MAX_GT_5).all() else "sum" if (vals[d] == SUM_GT_10).all() else "")
                 for _, d in ds]
        out.append("max" in roles and "sum" in roles)
    return np.array(out, dtype=bool)


def children_single_point(x: np.ndarray, y: np.ndarray):
    for c in range(1, len(x)):
        yield {"cut": c}, np.concatenate([x[:c], y[c:]])


def children_transplant(x: np.ndarray, y: np.ndarray):
    """Insert each whole domain of y at each domain boundary of x, with each linker."""
    y_doms = [d for _, d in split_domains(y)]
    bounds = [0] + [i for i, t in enumerate(x) if t in LINKERS] + [len(x)]
    for d in y_doms:
        for b in sorted(set(bounds)):
            for link in LINKERS:
                if b == 0:
                    ins = list(d) + [link]           # new first domain; x's first gets `link`
                else:
                    ins = [link] + list(d)
                yield {"linker": int(link)}, np.array(list(x[:b]) + ins + list(x[b:]), dtype=np.uint8)


def score(chem: str, op: str, pools: dict, out_dir: Path) -> dict:
    cfg = cfg_for(chem, "sum_gt_10_AND_max_gt_5", 0)
    task = full_task(cfg, AND)
    maxes = [np.frombuffer(g, dtype=np.uint8) for g in pools[(chem, "max>5")]]
    sums = [np.frombuffer(g, dtype=np.uint8) for g in pools[(chem, "sum>10")]]
    parent_score, parent_out = {}, {}
    for g in maxes + sums:
        _, p = evaluate_population([g], task, cfg)
        parent_score[g.tobytes()] = float(bacc_and(p)[0])
        parent_out[g.tobytes()] = p[0]
    make = children_transplant if op == "transplant" else children_single_point
    pieces = PieceCheck(cfg) if chem == "baseline" else None
    rng = np.random.default_rng(1)
    tally = collections.Counter()
    by_linker: dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    batch, meta = [], []

    def flush():
        _, preds = evaluate_population(batch, task, cfg)
        exact = (preds == AND).all(axis=1)
        sc = bacc_and(preds)
        # Piece checks are costly for baseline: run them on a 10% sample.
        check = rng.random(len(batch)) < (0.1 if pieces else 1.0)
        if pieces:
            idx = np.flatnonzero(check)
            progs = _programs_for_arm(cfg, np.stack([batch[i] for i in idx])) if len(idx) else []
            both = np.zeros(len(batch), dtype=bool)
            both[idx] = pieces.both(progs) if len(idx) else []
        else:
            both = v3_both(batch, task)
        for k, (m, (xk, yk)) in enumerate(meta):
            fitter = max(parent_score[xk], parent_score[yk])
            weaker = min(parent_score[xk], parent_score[yk])
            crash = bool(sc[k] < weaker - CRASH)
            tally["children"] += 1
            tally["exact AND"] += bool(exact[k])
            tally["crash"] += crash
            tally["same as a parent"] += bool((preds[k] == parent_out[xk]).all() or (preds[k] == parent_out[yk]).all())
            tally["better than fitter parent"] += bool(sc[k] > fitter + 1e-3)
            if check[k]:
                tally["checked for pieces"] += 1
                tally["both pieces"] += bool(both[k])
            if "linker" in m:
                by_linker[m["linker"]]["children"] += 1
                by_linker[m["linker"]]["exact AND"] += bool(exact[k])
                by_linker[m["linker"]]["crash"] += crash
        batch.clear()
        meta.clear()

    for a, b in itertools.product(maxes, sums):
        for x, y in ((a, b), (b, a)):
            for m, child in make(x, y):
                batch.append(child)
                meta.append((m, (x.tobytes(), y.tobytes())))
                if len(batch) >= 4000:
                    flush()
    if batch:
        flush()
    return {"chemistry": chem, "operator": op, "donors": [len(maxes), len(sums)], "tally": dict(tally),
            "by_linker": {int(k): dict(v) for k, v in by_linker.items()},
            "parent_scores": sorted(set(round(v, 4) for v in parent_score.values()))}


def main(out: str) -> None:
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    pools: dict[tuple, list[bytes]] = collections.defaultdict(list)
    pool_file = out_dir / "donor_pools.json"
    if pool_file.exists():  # donor evolution is the slow part; reuse it
        for k, v in json.loads(pool_file.read_text()).items():
            chem, pred = k.split("|")
            pools[(chem, pred)] = [bytes.fromhex(h) for h in v]
    else:
        items = [(c, p, s) for c in CHEMS for p in PRED for s in SEEDS]
        with Pool(10) as pool:
            got = pool.map(evolve_donors, items)
        for chem, pred, gs in got:
            for g in gs:
                if g not in pools[(chem, pred)] and len(pools[(chem, pred)]) < POOL:
                    pools[(chem, pred)].append(g)
        pool_file.write_text(json.dumps({f"{c}|{p}": [g.hex() for g in v] for (c, p), v in pools.items()}))
    print({k: len(v) for k, v in pools.items()}, flush=True)
    results = [score(c, op, pools, out_dir) for c, op in
               (("baseline", "single-point"), ("v3", "single-point"), ("v3", "transplant"))
               if pools[(c, "max>5")] and pools[(c, "sum>10")]]
    (out_dir / "results.json").write_text(json.dumps(results, indent=1))

    names = {20: "SILENT", 21: "ADD", 22: "GT", 23: "MIN", 24: "MAX", 25: "GATE"}
    lines = ["# Guaranteed-supply merge test", "",
             "Donor pools (max>5 / sum>10 genomes exact on all 10k lists): "
             + ", ".join(f"{c} {len(pools[(c, 'max>5')])}/{len(pools[(c, 'sum>10')])}" for c in CHEMS), "",
             "| chemistry | operator | children | exact AND | both blocks kept | better than fitter parent | "
             "same as a parent | crash (worse than both) |",
             "|---|---|---|---|---|---|---|---|"]
    for c in CHEMS:
        if not (pools[(c, "max>5")] and pools[(c, "sum>10")]):
            lines.append(f"| {c} | - | no exact donors for one predicate | | | | |")
    for r in results:
        t = r["tally"]
        n = t["children"]
        pct = lambda k, d=n: f"{100 * t.get(k, 0) / d:.2f}%" if d else "-"  # noqa: E731
        lines.append(f"| {r['chemistry']} | {r['operator']} | {n} | {pct('exact AND')} | "
                     f"{pct('both pieces', t.get('checked for pieces', 0))} | {pct('better than fitter parent')} | "
                     f"{pct('same as a parent')} | {pct('crash')} |")
    tr = results[-1]["by_linker"] if results and results[-1]["operator"] == "transplant" else {}
    lines += ["", "## v3 transplant by linker at the join", "", "| linker | children | exact AND | crash |",
              "|---|---|---|---|"]
    for k in sorted(tr):
        v = tr[k]
        lines.append(f"| {names[k]} | {v['children']} | {100 * v.get('exact AND', 0) / v['children']:.2f}% | "
                     f"{100 * v.get('crash', 0) / v['children']:.2f}% |")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
