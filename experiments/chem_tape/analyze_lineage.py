"""Analyze lineages of AND-task runs (map-bias notebook §4, step 2).

For every run with lineage.npz:
  - Is the final best an exact AND, or an approximation that happens to fit the
    64 training cases? Scored on all 10,000 length-4 lists over [0, 9].
  - Every innovation along the best genome's ancestry (main line = fitter
    parent at each crossover): a child that beats *both* its parents, labelled
    as crossover or clone+mutation, with the gain over the better parent.
  - For crossover steps: does the child's *executed* program (decode mask)
    contain material that only parent 1 had AND material that only parent 2 had?
    That is the "combine two building blocks" event the jump question is about.

Usage: uv run python experiments/chem_tape/analyze_lineage.py experiments/output/2026-09-26/lexicase_lineage
"""

from __future__ import annotations

import collections
import itertools
import json
import sys
from dataclasses import fields
from pathlib import Path

import numpy as np
import yaml

from folding_evolution.chem_tape import engine_numpy
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import evaluate_population
from folding_evolution.chem_tape.tasks import build_task

ALL_LISTS = [tuple(int(v) for v in x) for x in itertools.product(range(10), repeat=4)]
ALL_LABELS = np.array([int(sum(x) > 10 and max(x) > 5) for x in ALL_LISTS], dtype=np.int64)
BIG_JUMP = 0.05  # >= 4 of 64 training cases in one step


def setup_name(c: dict) -> str:
    name = c.get("selection_mode", "tournament")
    return name + (" + alphabet_separators" if c.get("alphabet_separators") else "")


def full_domain_accuracy(genome: np.ndarray, cfg: ChemTapeConfig) -> float:
    task = build_task(cfg, cfg.seed)
    from dataclasses import replace
    everything = replace(task, inputs=ALL_LISTS, labels=ALL_LABELS)
    fits, _ = evaluate_population([genome], everything, cfg)
    return float(fits[0])


def origins(child: np.ndarray, p1: np.ndarray, p2: np.ndarray, cfg: ChemTapeConfig) -> tuple[int, int]:
    """Executed cells of the child that match only parent 1 / only parent 2."""
    mask = engine_numpy.compute_topk_runnable_mask(child[None, :], cfg.topk, cfg.decode_separators())[0]
    only1 = mask & (child == p1) & (child != p2)
    only2 = mask & (child == p2) & (child != p1)
    return int(only1.sum()), int(only2.sum())


def analyze_run(run_dir: Path, c: dict) -> dict:
    names = {f.name for f in fields(ChemTapeConfig)}
    cfg = ChemTapeConfig(**{k: v for k, v in c.items() if k in names})
    lin = np.load(run_dir / "lineage.npz")
    fit, kind, mut = lin["fitness"], lin["kind"], lin["mutated"]
    steps = []
    for k in range(1, len(fit)):
        best_parent = float(fit[k - 1])  # main line = the fitter parent
        gain = float(fit[k]) - best_parent
        if gain <= 1e-9:
            continue
        step = {"gen": int(lin["generation"][k]), "gain": gain, "to": float(fit[k]),
                "kind": {0: "elite", 1: "crossover", 2: "mutation"}[int(kind[k])],
                "mutated": bool(mut[k])}
        if kind[k] == 1:
            p1, p2 = lin["genome"][k - 1], lin["other_genome"][k]
            o1, o2 = origins(lin["genome"][k], p1, p2, cfg)
            step.update(p2_fitness=float(lin["other_fitness"][k]), only_p1=o1, only_p2=o2,
                        merges=o1 >= 2 and o2 >= 2)
        steps.append(step)
    solved = fit[-1] >= 0.999
    return {"seed": c["seed"], "solved": bool(solved), "final": float(fit[-1]),
            "full_domain": full_domain_accuracy(lin["genome"][-1], cfg) if solved else None,
            "steps": steps}


def main(out_dir: str) -> None:
    out = Path(out_dir)
    index = json.loads((out / "sweep_index.json").read_text())
    by_setup: dict[str, list] = collections.defaultdict(list)
    for r in index:
        rd = Path(r["run_dir"])
        c = yaml.safe_load(open(rd / "config.yaml"))
        by_setup[setup_name(c)].append(analyze_run(rd, c))

    lines = ["# Lexicase lineage analysis", "",
             "| setup | solved | exact AND (all 10k lists) | median full-domain acc of solvers |",
             "|---|---|---|---|"]
    for name, runs in sorted(by_setup.items()):
        sol = [r for r in runs if r["solved"]]
        fd = [r["full_domain"] for r in sol]
        lines.append(f"| {name} | {len(sol)}/{len(runs)} | {sum(x >= 0.9999 for x in fd)}/{len(sol)} | "
                     f"{np.median(fd) if fd else float('nan'):.4f} |")

    lines += ["", "## Innovations (child beats both parents) along solver main lines", "",
              "| setup | innovations | by crossover | by mutation only | crossovers merging both parents | "
              "big jumps (>= 0.05) by crossover / mutation |", "|---|---|---|---|---|---|"]
    for name, runs in sorted(by_setup.items()):
        st = [s for r in runs if r["solved"] for s in r["steps"]]
        xo = [s for s in st if s["kind"] == "crossover"]
        mu = [s for s in st if s["kind"] == "mutation"]
        big_x = sum(s["gain"] >= BIG_JUMP for s in xo)
        big_m = sum(s["gain"] >= BIG_JUMP for s in mu)
        lines.append(f"| {name} | {len(st)} | {len(xo)} | {len(mu)} | "
                     f"{sum(s['merges'] for s in xo)}/{len(xo)} | {big_x} / {big_m} |")

    lines += ["", "## The final step to 1.0 in each solver", "",
              "| setup | seed | gen | fitter parent | kind | mutated | other parent | executed cells only-fitter / only-other | full-domain acc |",
              "|---|---|---|---|---|---|---|---|---|"]
    for name, runs in sorted(by_setup.items()):
        for r in sorted((r for r in runs if r["solved"]), key=lambda r: r["seed"]):
            s = r["steps"][-1]
            p2 = f"{s['p2_fitness']:.3f}" if "p2_fitness" in s else "-"
            orig = f"{s['only_p1']} / {s['only_p2']}" if "only_p1" in s else "-"
            lines.append(f"| {name} | {r['seed']} | {s['gen']} | {s['to'] - s['gain']:.3f} | {s['kind']} | "
                         f"{s['mutated']} | {p2} | {orig} | {r['full_domain']:.4f} |")

    (out / "lineage_summary.md").write_text("\n".join(lines) + "\n")
    (out / "lineage_runs.json").write_text(json.dumps(by_setup, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
