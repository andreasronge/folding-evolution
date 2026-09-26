"""Crossover spectrum on the exact-AND lexicase solvers (map-bias notebook §6).

Re-runs each solver seed with lineage tracking (deterministic, checked against
the saved run) and, on sampled generations, classifies every child against its
parent(s) using all 10,000 length-4 lists over [0, 9]:

  score     balanced accuracy on the 10k lists (84% of lists are positive, so
            plain accuracy would reward "always 1")
  better    child > fitter parent + EPS
  neutral   within EPS of the fitter parent
  degrade   below the fitter parent but >= weaker parent - CRASH
  crash     below weaker parent - CRASH

For crossover children also:
  combination   child passes every list either parent passed, and each parent
                passed >= K lists the other did not (the parents' pass sets are
                not nested, so a single-threshold walk can't fake it)
and for combination events a substring test: does the child's executed
program contain one contiguous piece whose outputs equal parent 1's on all 10k
lists, and another equal to parent 2's? Both found = the blocks survived as
pieces of the child; the tokens around them are the glue.

Usage:
  uv run python experiments/chem_tape/crossover_spectrum.py \
      experiments/output/2026-09-26/lexicase_lineage experiments/output/2026-09-26/crossover_spectrum
"""

from __future__ import annotations

import collections
import itertools
import json
import os
import sys
from dataclasses import fields, replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import yaml

EPS = 1e-3
CRASH = 0.05
K = 3
MAX_EVENTS = 60  # unique combination events per seed that get the substring test

ALL_LISTS = [tuple(int(v) for v in x) for x in itertools.product(range(10), repeat=4)]
ALL_LABELS = np.array([int(sum(x) > 10 and max(x) > 5) for x in ALL_LISTS], dtype=np.int64)
POS = ALL_LABELS == 1
MAX_GT_5 = np.array([int(max(x) > 5) for x in ALL_LISTS], dtype=np.int64)
SUM_GT_10 = np.array([int(sum(x) > 10) for x in ALL_LISTS], dtype=np.int64)


def bacc(passed: np.ndarray) -> np.ndarray:
    """Balanced accuracy from a (N, 10k) pass matrix."""
    return 0.5 * (passed[:, POS].mean(axis=1) + passed[:, ~POS].mean(axis=1))


def sample_generations(G: int) -> list[int]:
    return sorted(set(range(10, G + 1, 10)) | set(range(max(1, G - 9), G + 1)))


def token_names() -> dict[int, str]:
    from folding_evolution.chem_tape import alphabet as A
    names = {v: k for k, v in vars(A).items()
             if isinstance(v, int) and k.isupper() and not k.startswith(("N_", "RESERVED", "SLOT", "SEP", "SUM_", "MIN"))}
    names.update({12: "SLOT12", 13: "SLOT13", 20: "|", 21: "|"})
    return names


def classify(child: float, parents: list[float]) -> str:
    hi, lo = max(parents), min(parents)
    if child > hi + EPS:
        return "better"
    if child >= hi - EPS:
        return "neutral"
    if child >= lo - CRASH:
        return "degrade"
    return "crash"


def work(item) -> dict:
    run_dir, c, expected_hex = item
    os.environ.setdefault("RAYON_NUM_THREADS", "2")
    from _folding_rust import rust_chem_execute_pop_batch
    from folding_evolution.chem_tape.config import ChemTapeConfig
    from folding_evolution.chem_tape.evaluate import _programs_for_arm, evaluate_population
    from folding_evolution.chem_tape.evolve import run_evolution
    from folding_evolution.chem_tape.tasks import build_task

    names = {f.name for f in fields(ChemTapeConfig)}
    cfg = ChemTapeConfig(**{**{k: v for k, v in c.items() if k in names}, "track_lineage": True})
    res = run_evolution(cfg)
    assert res.best_genotype.tobytes().hex() == expected_hex, "re-run did not reproduce the saved run"
    pops, parents = res.generations["pops"], res.generations["parents"]
    task = replace(build_task(cfg, cfg.seed), inputs=ALL_LISTS, labels=ALL_LABELS)

    def outputs(genomes: np.ndarray) -> np.ndarray:
        _, preds = evaluate_population(list(genomes), task, cfg)
        return preds

    counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    combos: dict[tuple, dict] = {}
    G = len(pops) - 1
    for g in sample_generations(G):
        prev_u, prev_inv = np.unique(pops[g - 1], axis=0, return_inverse=True)
        cur_u, cur_inv = np.unique(pops[g], axis=0, return_inverse=True)
        prev_out, cur_out = outputs(prev_u), outputs(cur_u)
        prev_pass, cur_pass = prev_out == ALL_LABELS, cur_out == ALL_LABELS
        prev_score, cur_score = bacc(prev_pass), bacc(cur_pass)
        prev_inv, cur_inv = prev_inv.ravel(), cur_inv.ravel()
        for ci, (p1, p2, kind, mutated) in enumerate(parents[g]):
            if kind == 0 or (kind == 2 and not mutated):
                continue  # elites and unmutated clones are exact copies
            cu = cur_inv[ci]
            if kind == 2:
                counts["mutation only"][classify(cur_score[cu], [prev_score[prev_inv[p1]]])] += 1
                continue
            a, b = prev_inv[p1], prev_inv[p2]
            label = "crossover + mutation" if mutated else "crossover, no mutation"
            outcome = classify(cur_score[cu], [prev_score[a], prev_score[b]])
            counts[label][outcome] += 1
            s1, s2, sc = prev_pass[a], prev_pass[b], cur_pass[cu]
            if (s1 & ~s2).sum() >= K and (s2 & ~s1).sum() >= K and not ((s1 | s2) & ~sc).any():
                counts[label]["combination"] += 1
                key = (pops[g][ci].tobytes(), prev_u[a].tobytes(), prev_u[b].tobytes())
                if key not in combos and len(combos) < MAX_EVENTS:
                    combos[key] = {"gen": g, "label": label, "outcome": outcome,
                                   "child": pops[g][ci], "p1": prev_u[a], "p2": prev_u[b],
                                   "p1_out": prev_out[a], "p2_out": prev_out[b],
                                   "scores": [float(prev_score[a]), float(prev_score[b]), float(cur_score[cu])]}

    # Substring test on unique combination events.
    tn = token_names()

    def piece_outputs(prog: list[int]):
        spans = [(i, j) for i in range(len(prog)) for j in range(i + 1, len(prog) + 1)]
        flat = rust_chem_execute_pop_batch(
            [prog[i:j] for i, j in spans], task.alphabet.slot_12, task.alphabet.slot_13,
            ALL_LISTS, task.input_type, alphabet_name=cfg.alphabet,
            threshold=int(task.alphabet.threshold), safe_pop_consume=cfg.safe_pop_mode == "consume",
        )
        return spans, np.asarray(flat, dtype=np.int64).reshape(len(spans), len(ALL_LISTS))

    def has_predicates(prog: list[int]) -> dict:
        """Does some contiguous piece compute max>5 / sum>10 exactly?"""
        _, out = piece_outputs(prog)
        return {"max>5": bool((out == MAX_GT_5).all(axis=1).any()),
                "sum>10": bool((out == SUM_GT_10).all(axis=1).any())}

    events = []
    for ev in combos.values():
        prog = _programs_for_arm(cfg, ev["child"].reshape(1, -1))[0]
        spans, out = piece_outputs(prog)
        m1 = [spans[k] for k in np.flatnonzero((out == ev["p1_out"]).all(axis=1))]
        m2 = [spans[k] for k in np.flatnonzero((out == ev["p2_out"]).all(axis=1))]
        # Shortest disjoint pair of pieces, one per parent.
        pair = min(((x, y) for x in m1 for y in m2 if x[1] <= y[0] or y[1] <= x[0]),
                   key=lambda xy: (xy[0][1] - xy[0][0]) + (xy[1][1] - xy[1][0]), default=None)
        shown = " ".join(tn.get(t, str(t)) for t in prog)
        if pair:
            (i1, j1), (i2, j2) = pair
            marks = ["[" + " ".join(tn.get(t, str(t)) for t in prog[i:j]) + "]" for i, j in sorted([(i1, j1), (i2, j2)])]
            inside = set(range(i1, j1)) | set(range(i2, j2))
            glue = " ".join(tn.get(prog[k], str(prog[k])) for k in range(len(prog)) if k not in inside)
            shown = f"pieces {marks[0]} {marks[1]} | outside: {glue}"
        p1_prog = _programs_for_arm(cfg, ev["p1"].reshape(1, -1))[0]
        p2_prog = _programs_for_arm(cfg, ev["p2"].reshape(1, -1))[0]
        events.append({"gen": ev["gen"], "label": ev["label"], "outcome": ev["outcome"],
                       "scores": ev["scores"], "p1_piece": bool(m1), "p2_piece": bool(m2),
                       "both_disjoint": pair is not None, "program": shown,
                       "predicates": {"child": has_predicates(prog), "p1": has_predicates(p1_prog),
                                      "p2": has_predicates(p2_prog)},
                       "p1_program": " ".join(tn.get(t, str(t)) for t in p1_prog),
                       "p2_program": " ".join(tn.get(t, str(t)) for t in p2_prog)})
    return {"seed": cfg.seed, "solve_gen": G, "counts": {k: dict(v) for k, v in counts.items()},
            "events": events, "unique_combinations_tested": len(combos)}


def main(sweep_dir: str, out_dir: str) -> None:
    sweep, out = Path(sweep_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    lin = json.loads((sweep / "lineage_runs.json").read_text())["lexicase"]
    exact = {r["seed"] for r in lin if r["solved"] and r["full_domain"] >= 0.9999}
    items = []
    for r in json.loads((sweep / "sweep_index.json").read_text()):
        c = yaml.safe_load(open(Path(r["run_dir"]) / "config.yaml"))
        if c["selection_mode"] == "lexicase" and not c.get("alphabet_separators") and c["seed"] in exact:
            items.append((r["run_dir"], c, r["best_genotype_hex"]))
    with Pool(len(items)) as pool:
        results = sorted(pool.map(work, items), key=lambda r: r["seed"])
    (out / "results.json").write_text(json.dumps(results, indent=1))

    total: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in results:
        for k, v in r["counts"].items():
            total[k].update(v)
    lines = ["# Crossover spectrum — exact-AND lexicase solvers", "",
             f"Seeds {', '.join(str(r['seed']) for r in results)}; sampled generations (every 10th + "
             "last 10 before the solve); all children except elites and unmutated clones; scored on "
             "all 10,000 lists (balanced accuracy).", "",
             "| operator | children | better | neutral | small degradation | crash | combination |",
             "|---|---|---|---|---|---|---|"]
    for k in ("crossover, no mutation", "crossover + mutation", "mutation only"):
        v = total[k]
        n = sum(v[o] for o in ("better", "neutral", "degrade", "crash"))
        pct = lambda o: f"{100 * v[o] / n:.2f}%" if n else "-"  # noqa: E731
        lines.append(f"| {k} | {n} | {pct('better')} | {pct('neutral')} | {pct('degrade')} | "
                     f"{pct('crash')} | {v['combination']} ({pct('combination')}) |")
    ev = [e for r in results for e in r["events"]]
    lines += ["", f"## Substring test on {len(ev)} unique combination events", "",
              f"- a piece behaving exactly like parent 1: {sum(e['p1_piece'] for e in ev)}",
              f"- a piece behaving exactly like parent 2: {sum(e['p2_piece'] for e in ev)}",
              f"- both, as disjoint pieces (blocks survived intact): {sum(e['both_disjoint'] for e in ev)}", "",
              "Parents at these moments are approximations, so a piece equal to a *whole parent* is a "
              "strict test. Second test: which programs contain a piece computing `max>5` or `sum>10` "
              "exactly (child / parent 1 / parent 2):", "",
              "| seed | gen | child | parent 1 | parent 2 |", "|---|---|---|---|---|"]
    fmt = lambda d: ", ".join(k for k, v in d.items() if v) or "none"  # noqa: E731
    lines += [f"| {r['seed']} | {e['gen']} | {fmt(e['predicates']['child'])} | {fmt(e['predicates']['p1'])} | "
              f"{fmt(e['predicates']['p2'])} |" for r in results for e in r["events"]]
    lines += ["",
              "| seed | gen | operator | outcome | parent 1 / parent 2 / child | child program |", "|---|---|---|---|---|---|"]
    for r in results:
        for e in r["events"]:
            s = " / ".join(f"{x:.3f}" for x in e["scores"])
            lines.append(f"| {r['seed']} | {e['gen']} | {e['label']} | {e['outcome']} | {s} | `{e['program']}` |")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
