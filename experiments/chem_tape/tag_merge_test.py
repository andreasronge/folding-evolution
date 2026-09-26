"""Tagged-runs merge test (map-bias notebook §8-9).

Donors: genomes evolved under tagged runs that compute max>5 or sum>10 exactly
on all 10,000 lists (lexicase, pop 1024 x 400 gens, 8 seeds per predicate).
Three measures (fifth Fable review):

1. Smear: remove each run of a donor; a run is load-bearing if the donor's
   output changes. Kill if donors typically need >= 3 load-bearing runs.
2. Inertness: append each run of donor B to donor A. Inert = A's output
   unchanged. Kill if < 80% of non-output transplants are inert (hijacking).
3. Paths to AND: import B's whole module silently (all of B's runs appended,
   B's output run retagged to a tag unused in A, so nothing references it).
   Exhaustive 1-mutation neighbourhood and a random sample of 2-mutation
   neighbours: count exact AND, better than both parents, and "wired in"
   (output changed and some expressed RECV reaches the imported module).
   Confirm if some 2-step path to AND exists (baseline: 0 in 38,750).

Usage: uv run python experiments/chem_tape/tag_merge_test.py experiments/output/2026-09-26/tag_merge_test
"""

from __future__ import annotations

import collections
import itertools
import json
import random
import sys
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from folding_evolution.chem_tape import tagged
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution
from folding_evolution.chem_tape.tasks import build_task

ALL = [tuple(int(v) for v in x) for x in itertools.product(range(10), repeat=4)]
MAX5 = np.array([int(max(x) > 5) for x in ALL])
SUM10 = np.array([int(sum(x) > 10) for x in ALL])
AND = MAX5 & SUM10
POS = AND == 1
TASKS = {"max>5": ("mb_max_gt_5", MAX5), "sum>10": ("mb_sum_gt_10", SUM10)}
SEEDS = range(8)
POOL = 20
CRASH = 0.05
N_PATH_CHILDREN = 40
N_DOUBLE = 3000


def cfg_for(task: str, seed: int) -> ChemTapeConfig:
    return ChemTapeConfig(task=task, arm="TAG", alphabet="tagged", tape_length=64, pop_size=1024,
                          generations=400, mutation_rate=0.015, selection_mode="lexicase", backend="numpy",
                          holdout_size=0, seed=seed, disable_early_termination=True, dump_final_population=True)


def task_on(labels: np.ndarray):
    return replace(build_task(cfg_for("mb_max_gt_5", 0), 0), inputs=ALL, labels=labels)


def outputs(genomes, task) -> np.ndarray:
    return tagged.evaluate_tagged(list(genomes), task)[1]


def bacc(preds: np.ndarray) -> np.ndarray:
    ok = preds == AND
    return 0.5 * (ok[:, POS].mean(axis=1) + ok[:, ~POS].mean(axis=1))


def evolve(item):
    pred, seed = item
    task_name, labels = TASKS[pred]
    res = run_evolution(cfg_for(task_name, seed))
    uniq = np.unique(res.final_population, axis=0)
    exact = uniq[(outputs(uniq, task_on(labels)) == labels).all(axis=1)]
    return pred, seed, [g.tobytes() for g in exact]


def runs_to_genome(runs, rng) -> np.ndarray:
    L = sum(1 + len(b) for _, b in runs)
    return tagged.build([], runs, max(L, 1), rng)


def expressed_tags(g: np.ndarray) -> set[int]:
    """Tags reachable from the output tag through RECV."""
    runs = tagged.parse_runs(g)
    by_tag = collections.defaultdict(list)
    for tag, body in runs:
        by_tag[tag].append(body)
    seen, todo = set(), [tagged.OUTPUT_TAG]
    while todo:
        t = todo.pop()
        if t in seen:
            continue
        seen.add(t)
        for body in by_tag.get(t, []):
            todo += [tg for op, tg in body if op == tagged.RECV]
    return seen


def point_mutants(g: np.ndarray):
    ops, tags = tagged.split(g)
    L = len(ops)
    for i in range(L):
        for v in range(tagged.N_OPS):
            if v != ops[i]:
                h = g.copy()
                h[i] = v
                yield h
        for v in range(tagged.N_TAGS):
            if v != tags[i]:
                h = g.copy()
                h[L + i] = v
                yield h


def main(out: str) -> None:
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(0)
    pool_file = out_dir / "donor_pools.json"
    if pool_file.exists():
        pools = {k: [bytes.fromhex(h) for h in v] for k, v in json.loads(pool_file.read_text()).items()}
    else:
        with Pool(10) as pool:
            got = pool.map(evolve, [(p, s) for p in TASKS for s in SEEDS])
        by_seed = collections.defaultdict(list)
        for pred, seed, gs in got:
            by_seed[pred].append(gs)
        pools = {}
        for pred, lists in by_seed.items():   # round-robin across seeds for diversity
            picked = []
            for row in itertools.zip_longest(*lists):
                picked += [g for g in row if g is not None and g not in picked]
            pools[pred] = picked[:POOL]
        pool_file.write_text(json.dumps({k: [g.hex() for g in v] for k, v in pools.items()}))
    donors = {k: [np.frombuffer(g, dtype=np.uint8) for g in v] for k, v in pools.items()}
    t_and = task_on(AND)
    lines = ["# Tagged-runs merge test", "",
             f"Donors (exact on all 10k lists): max>5 {len(donors['max>5'])}, sum>10 {len(donors['sum>10'])}"]

    # 1. Smear -------------------------------------------------------------
    smear = collections.defaultdict(list)
    for pred, gs in donors.items():
        t = task_on(TASKS[pred][1])
        for g in gs:
            runs = tagged.parse_runs(g)
            base = outputs([g], t)[0]
            kos = [runs_to_genome(runs[:k] + runs[k + 1:], rng) for k in range(len(runs))]
            changed = (outputs(kos, t) != base).any(axis=1) if kos else np.array([])
            smear[pred].append({"runs": len(runs), "load_bearing": int(changed.sum()),
                                "expressed_runs": sum(1 for tag, _ in runs if tag in expressed_tags(g))})
    lines += ["", "## 1. Smear: load-bearing runs per donor", "",
              "| donor | donors | runs (median) | load-bearing runs: median | distribution |", "|---|---|---|---|---|"]
    for pred, rows in smear.items():
        lb = [r["load_bearing"] for r in rows]
        lines.append(f"| {pred} | {len(rows)} | {np.median([r['runs'] for r in rows]):.0f} | {np.median(lb):.1f} | "
                     f"{dict(sorted(collections.Counter(lb).items()))} |")

    # 2. Inertness ---------------------------------------------------------
    tally = collections.Counter()
    score = {g.tobytes(): float(bacc(outputs([g], t_and))[0]) for gs in donors.values() for g in gs}
    for a_pred, b_pred in (("max>5", "sum>10"), ("sum>10", "max>5")):
        for a in donors[a_pred]:
            ra, out_a = tagged.parse_runs(a), outputs([a], t_and)[0]
            for b in donors[b_pred]:
                weaker = min(score[a.tobytes()], score[b.tobytes()])
                kids, kinds = [], []
                for tag, body in tagged.parse_runs(b):
                    kids.append(runs_to_genome(ra + [(tag, body)], rng))
                    kinds.append("output run" if tag == tagged.OUTPUT_TAG else
                                 "tag already in recipient" if any(tag == t for t, _ in ra) else "new tag")
                if not kids:
                    continue
                preds = outputs(kids, t_and)
                sc = bacc(preds)
                for k, kind in enumerate(kinds):
                    tally[(kind, "n")] += 1
                    tally[(kind, "inert")] += bool((preds[k] == out_a).all())
                    tally[(kind, "crash")] += bool(sc[k] < weaker - CRASH)
    lines += ["", "## 2. Inertness: one run of donor B appended to donor A", "",
              "| transplanted run | children | inert (A unchanged) | crash |", "|---|---|---|---|"]
    for kind in ("new tag", "tag already in recipient", "output run"):
        n = tally[(kind, "n")]
        if n:
            lines.append(f"| {kind} | {n} | {100 * tally[(kind, 'inert')] / n:.1f}% | "
                         f"{100 * tally[(kind, 'crash')] / n:.1f}% |")
    non_out = sum(tally[(k, "n")] for k in ("new tag", "tag already in recipient"))
    non_out_inert = sum(tally[(k, "inert")] for k in ("new tag", "tag already in recipient"))
    lines.append(f"\nNon-output transplants inert: {100 * non_out_inert / max(non_out, 1):.1f}% (kill below 80%)")

    # 3. Paths to AND --------------------------------------------------------
    pairs = [(a, b) for a in donors["max>5"] for b in donors["sum>10"]]
    pairs += [(b, a) for a, b in pairs]
    rng.shuffle(pairs)
    res = collections.Counter()
    examples = []
    for a, b in pairs[:N_PATH_CHILDREN]:
        ra, rb = tagged.parse_runs(a), tagged.parse_runs(b)
        used = {t for t, _ in ra} | {t for t, _ in rb}
        free = next(t for t in range(1, tagged.N_TAGS) if t not in used)
        imported = [(free if t == tagged.OUTPUT_TAG else t, body) for t, body in rb]
        child = runs_to_genome(ra + imported, rng)
        parents_best = max(score[a.tobytes()], score[b.tobytes()])
        out_child = outputs([child], t_and)[0]
        res["children"] += 1
        res["import inert"] += bool((out_child == outputs([a], t_and)[0]).all())
        module_tags = {t for t, _ in imported}
        for step, mutants in (("1 mutation", list(point_mutants(child))),
                              ("2 mutations", None)):
            if mutants is None:
                singles = list(point_mutants(child))
                mutants = []
                for _ in range(N_DOUBLE):
                    h = singles[rng.randrange(len(singles))]
                    ops, tags = tagged.split(h)
                    i = rng.randrange(len(ops))
                    h = h.copy()
                    if rng.random() < 0.5:
                        h[i] = rng.randrange(tagged.N_OPS)
                    else:
                        h[len(ops) + i] = rng.randrange(tagged.N_TAGS)
                    mutants.append(h)
            preds = outputs(mutants, t_and)
            sc = bacc(preds)
            exact = (preds == AND).all(axis=1)
            changed = (preds != out_child).any(axis=1)
            res[(step, "n")] += len(mutants)
            res[(step, "exact AND")] += int(exact.sum())
            res[(step, "better than both parents")] += int((sc > parents_best + 1e-3).sum())
            for k in np.flatnonzero(changed):
                if expressed_tags(mutants[k]) & module_tags:
                    res[(step, "wired in")] += 1
            for k in np.flatnonzero(exact)[:3]:
                examples.append((step, mutants[k]))
    lines += ["", f"## 3. Paths to AND from {res['children']} silent module imports", "",
              f"Import itself inert (A unchanged): {res['import inert']}/{res['children']}", "",
              "| neighbourhood | mutants | exact AND | better than both parents | wired in |", "|---|---|---|---|---|"]
    for step in ("1 mutation", "2 mutations"):
        n = res[(step, "n")]
        lines.append(f"| {step}{' (sampled)' if step.startswith('2') else ' (exhaustive)'} | {n} | "
                     f"{res[(step, 'exact AND')]} | {res[(step, 'better than both parents')]} | "
                     f"{res[(step, 'wired in')]} |")
    if examples:
        lines += ["", "Example exact-AND mutants (runs as tag: body ops):", ""]
        for step, g in examples[:5]:
            shown = "; ".join(f"{t}: {' '.join(f'RECV{tg}' if op == tagged.RECV else str(op) for op, tg in body)}"
                              for t, body in tagged.parse_runs(g))
            lines.append(f"- {step}: `{shown}`")

    (out_dir / "summary.md").write_text("\n".join(lines) + "\n")
    (out_dir / "results.json").write_text(json.dumps(
        {"smear": smear, "inert": {f"{k[0]}|{k[1]}": v for k, v in tally.items()},
         "paths": {str(k): v for k, v in res.items()}}, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
