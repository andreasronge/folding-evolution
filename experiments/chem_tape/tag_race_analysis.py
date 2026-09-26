"""Analyze the tagged-runs AND race (map-bias notebook §10).

- Solve rate on the 64 training cases and exact AND on all 10,000 lists,
  against the baseline lexicase runs (lexicase_lineage sweep, §5).
- For each exact tagged solver: re-run with lineage tracking (checked to
  reproduce) and find the first generation where some run in some genome
  computes max>5 / sum>10 exactly, where both exist in the population, and
  where both sit in one genome — the same waiting times as §7a (baseline
  numbers from crossover_spectrum2/results.json).
- How each exact solver is built: load-bearing runs (knockout) and whether
  the output reaches other runs through RECV.

Usage: uv run python experiments/chem_tape/tag_race_analysis.py \
    experiments/output/2026-09-26/tag_race experiments/output/2026-09-26
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from dataclasses import fields, replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import yaml

from folding_evolution.chem_tape import tagged
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evolve import run_evolution
from folding_evolution.chem_tape.tasks import build_task

ALL = [tuple(int(v) for v in x) for x in itertools.product(range(10), repeat=4)]
MAX5 = np.array([int(max(x) > 5) for x in ALL])
SUM10 = np.array([int(sum(x) > 10) for x in ALL])
AND = MAX5 & SUM10
_rng = np.random.default_rng(0)
SCREEN = np.concatenate([_rng.choice(np.flatnonzero((MAX5 == m) & (SUM10 == t)), 8, replace=False)
                         for m in (0, 1) for t in (0, 1)])


def cfg_of(c: dict) -> ChemTapeConfig:
    names = {f.name for f in fields(ChemTapeConfig)}
    return ChemTapeConfig(**{k: v for k, v in c.items() if k in names})


def all_task(cfg, idx=None):
    t = build_task(cfg, cfg.seed)
    ins = ALL if idx is None else [ALL[i] for i in idx]
    labs = AND if idx is None else AND[idx]
    return replace(t, inputs=ins, labels=labs)


def exact_and(g: np.ndarray, cfg) -> bool:
    return bool((tagged.evaluate_tagged([g], all_task(cfg))[1][0] == AND).all())


def structure(g: np.ndarray, cfg) -> dict:
    t = all_task(cfg)
    runs = tagged.parse_runs(g)
    base = tagged.evaluate_tagged([g], t)[1][0]
    kos = [tagged.build([], runs[:k] + runs[k + 1:], max(1, sum(1 + len(b) for _, b in runs[:k] + runs[k + 1:])),
                        random.Random(0)) for k in range(len(runs))]
    changed = (tagged.evaluate_tagged(kos, t)[1] != base).any(axis=1) if kos else np.array([])
    out_recv = sorted({tg for tag, body in runs if tag == tagged.OUTPUT_TAG
                       for op, tg in body if op == tagged.RECV})
    vals = tagged.run_values(g, t)
    roles = ["max>5" if (v == MAX5).all() else "sum>10" if (v == SUM10).all() else "AND" if (v == AND).all()
             else "" for v in vals]
    return {"runs": len(runs), "load_bearing": int(changed.sum()), "output_recv_tags": out_recv,
            "run_roles": [r for r in roles if r]}


def waits(item) -> dict:
    run_dir, c, expected = item
    cfg = replace(cfg_of(c), track_lineage=True)
    res = run_evolution(cfg)
    assert res.best_genotype.tobytes().hex() == expected, "re-run did not reproduce"
    pops = res.generations["pops"]
    t_screen, t_all = all_task(cfg, SCREEN), all_task(cfg)
    confirmed: dict[bytes, tuple[bool, bool]] = {}

    def genome_flags(g) -> tuple[bool, bool]:
        key = g.tobytes()
        if key not in confirmed:
            vs = tagged.run_values(g, t_screen)
            m = any((v == MAX5[SCREEN]).all() for v in vs)
            s = any((v == SUM10[SCREEN]).all() for v in vs)
            if m or s:
                va = tagged.run_values(g, t_all)
                m = m and any((v == MAX5).all() for v in va)
                s = s and any((v == SUM10).all() for v in va)
            confirmed[key] = (m, s)
        return confirmed[key]

    def flags(gen: int) -> tuple[bool, bool, bool]:
        fl = [genome_flags(g) for g in np.unique(pops[gen], axis=0)]
        return any(m for m, _ in fl), any(s for _, s in fl), any(m and s for m, s in fl)

    G = len(pops) - 1
    names = ("max>5 anywhere", "sum>10 anywhere", "both in one genome")
    first = {n: None for n in names}
    seen = {}
    for gen in list(range(0, G + 1, 5)) + ([G] if G % 5 else []):
        seen[gen] = flags(gen)
        for n, v in zip(names, seen[gen]):
            if v and first[n] is None:
                first[n] = gen
        if all(v is not None for v in first.values()):
            break
    for k, n in enumerate(names):
        if first[n]:
            for gen in range(max(0, first[n] - 4), first[n]):
                f = seen.get(gen) or flags(gen)
                if f[k]:
                    first[n] = gen
                    break
    both = None if None in (first["max>5 anywhere"], first["sum>10 anywhere"]) else \
        max(first["max>5 anywhere"], first["sum>10 anywhere"])
    return {"seed": cfg.seed, **first, "both in population": both, "solve": G}


def main(race_dir: str, day_dir: str) -> None:
    race, day = Path(race_dir), Path(day_dir)
    rows = []
    for r in json.loads((race / "sweep_index.json").read_text()):
        c = yaml.safe_load(open(Path(r["run_dir"]) / "config.yaml"))
        g = np.frombuffer(bytes.fromhex(r["best_genotype_hex"]), dtype=np.uint8)
        cfg = cfg_of(c)
        solved = r["best_fitness"] >= 0.999
        rows.append({"seed": c["seed"], "run_dir": r["run_dir"], "config": c, "hex": r["best_genotype_hex"],
                     "solved": solved, "gens": r["generations_run"], "holdout": r["holdout_fitness"],
                     "exact": solved and exact_and(g, cfg),
                     "structure": structure(g, cfg) if solved else None})
    lin = json.loads((day / "lexicase_lineage" / "lineage_runs.json").read_text())["lexicase"]
    base_solved = sum(x["solved"] for x in lin)
    base_exact = sum(1 for x in lin if x["solved"] and x["full_domain"] >= 0.9999)
    base_waits = json.loads((day / "crossover_spectrum2" / "results.json").read_text())
    exact = [x for x in rows if x["exact"]]
    with Pool(min(10, max(1, len(exact)))) as pool:
        tag_waits = sorted(pool.map(waits, [(x["run_dir"], x["config"], x["hex"]) for x in exact]),
                           key=lambda w: w["seed"]) if exact else []

    lines = ["# Tagged-runs AND race", "",
             "| chemistry | solved (64 cases) | exact AND (all 10k lists) | median solve gen (exact) |",
             "|---|---|---|---|",
             f"| baseline (BP_TOPK, lexicase) | {base_solved}/30 | {base_exact}/30 | "
             f"{np.median([w['waits']['solve'] for w in base_waits]):.0f} |",
             f"| tagged runs (lexicase) | {sum(x['solved'] for x in rows)}/{len(rows)} | {len(exact)}/{len(rows)} | "
             f"{np.median([x['gens'] for x in exact]) if exact else float('nan'):.0f} |", "",
             "## Waiting times (generation of first occurrence), exact solvers", "",
             "| chemistry | seed | both blocks in population | both in one genome | solve | one genome → solve |",
             "|---|---|---|---|---|---|"]
    for w in base_waits:
        ww = w["waits"]
        gap = "-" if ww["both in one genome"] is None else ww["solve"] - ww["both in one genome"]
        lines.append(f"| baseline | {w['seed']} | {ww['both in population']} | {ww['both in one genome']} | "
                     f"{ww['solve']} | {gap} |")
    for w in tag_waits:
        gap = "-" if w["both in one genome"] is None else w["solve"] - w["both in one genome"]
        lines.append(f"| tagged | {w['seed']} | {w['both in population']} | {w['both in one genome']} | "
                     f"{w['solve']} | {gap} |")
    lines += ["", "## How the tagged solvers are built", "",
              "| seed | exact AND | runs | load-bearing runs | output RECVs tags | runs computing a predicate |",
              "|---|---|---|---|---|---|"]
    for x in sorted(rows, key=lambda r: r["seed"]):
        if x["solved"]:
            s = x["structure"]
            lines.append(f"| {x['seed']} | {x['exact']} | {s['runs']} | {s['load_bearing']} | "
                         f"{s['output_recv_tags'] or '-'} | {', '.join(s['run_roles']) or '-'} |")
    (race / "summary.md").write_text("\n".join(lines) + "\n")
    (race / "analysis.json").write_text(json.dumps(
        {"rows": [{k: v for k, v in x.items() if k not in ("config",)} for x in rows], "waits": tag_waits},
        indent=1, default=str))
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
