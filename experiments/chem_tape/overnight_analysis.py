"""Morning analysis of the map-bias overnight queue (notebook §11).

Reads sweep outputs (sweep_index.json + per-run history.csv / result.json /
config.yaml) and reports, per arm (baseline BP_TOPK, tagged, tagged+dup):

Fixed tasks (or_race, and_fixed):
  - exact solves: final best genome exact on all 10,000 lists
  - generation of first exact best genome (checked every 10 generations)
  - tagged solvers' structure: output (tag-0) runs, load-bearing runs,
    live / dead RECVs (a RECV is live if some run carries its tag)

Varying goals (mvg_p20, mvg_period):
  - per phase: the new goal's starting best (flip_events.at_flip_best_new_task),
    whether training fitness reaches 1.0 within the phase and after how many
    generations, and whether the phase-end best genome is exact on all 10k
    lists for that goal; early (first third) vs late (last third) of the run
  - tagged phase-end structure as above

Usage: uv run python experiments/chem_tape/overnight_analysis.py experiments/output/<date>
"""

from __future__ import annotations

import collections
import csv
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
from folding_evolution.chem_tape.evaluate import evaluate_population
from folding_evolution.chem_tape.tasks import build_task

ALL = [tuple(int(v) for v in x) for x in itertools.product(range(10), repeat=4)]
LABELS = {
    "mbs_max_gt_5": np.array([int(max(x) > 5) for x in ALL]),
    "mbs_sum_gt_10": np.array([int(sum(x) > 10) for x in ALL]),
    "mbs_and": np.array([int(max(x) > 5 and sum(x) > 10) for x in ALL]),
    "mbs_or": np.array([int(max(x) > 5 or sum(x) > 10) for x in ALL]),
}
STEP = 10


def arm_name(c: dict) -> str:
    if c["arm"] != "TAG":
        return "baseline"
    return "tagged+dup" if c.get("run_duplication_rate", 0) else "tagged"


def cfg_of(c: dict) -> ChemTapeConfig:
    names = {f.name for f in fields(ChemTapeConfig)}
    return ChemTapeConfig(**{k: v for k, v in c.items() if k in names})


def exact_many(genomes: list[np.ndarray], cfg: ChemTapeConfig, task_name: str) -> np.ndarray:
    t = replace(build_task(replace(cfg, task=task_name), cfg.seed), inputs=ALL, labels=LABELS[task_name])
    _, preds = evaluate_population(genomes, t, replace(cfg, task=task_name))
    return (preds == LABELS[task_name]).all(axis=1)


def structure(g: np.ndarray, cfg: ChemTapeConfig, task_name: str) -> dict:
    runs = tagged.parse_runs(g)
    t = replace(build_task(replace(cfg, task=task_name), cfg.seed), inputs=ALL, labels=LABELS[task_name])
    base = tagged.evaluate_tagged([g], t)[1][0]
    rng = random.Random(0)
    kos = []
    for k in range(len(runs)):
        rest = runs[:k] + runs[k + 1:]
        kos.append(tagged.build([], rest, max(1, sum(1 + len(b) for _, b in rest)), rng))
    load = int((tagged.evaluate_tagged(kos, t)[1] != base).any(axis=1).sum()) if kos else 0
    owned = {tag for tag, _ in runs}
    recv = [tg for _, body in runs for op, tg in body if op == tagged.RECV]
    return {"runs": len(runs), "output_runs": sum(tag == tagged.OUTPUT_TAG for tag, _ in runs),
            "load_bearing": load, "live_recv": sum(tg in owned for tg in recv),
            "dead_recv": sum(tg not in owned for tg in recv)}


def history(run_dir: Path) -> tuple[list[float], list[np.ndarray]]:
    rows = list(csv.DictReader(open(run_dir / "history.csv")))
    return ([float(r["best_fitness"]) for r in rows],
            [np.frombuffer(bytes.fromhex(r["best_genotype_hex"]), dtype=np.uint8) for r in rows])


def analyze_fixed(item) -> dict:
    run_dir, c = item
    cfg = cfg_of(c)
    fits, genomes = history(Path(run_dir))
    gens = list(range(0, len(genomes), STEP)) + [len(genomes) - 1]
    ex = exact_many([genomes[g] for g in gens], cfg, cfg.task)
    first = next((g for g, e in zip(gens, ex) if e), None)
    final_exact = bool(ex[-1])
    out = {"arm": arm_name(c), "seed": c["seed"], "final_exact": final_exact, "first_exact_gen": first,
           "final_train": fits[-1]}
    if c["arm"] == "TAG" and final_exact:
        out["structure"] = structure(genomes[-1], cfg, cfg.task)
    return out


def analyze_mvg(item) -> dict:
    run_dir, c = item
    cfg = cfg_of(c)
    fits, genomes = history(Path(run_dir))
    result = json.loads((Path(run_dir) / "result.json").read_text())
    at_flip = {e["flip_gen"]: e.get("at_flip_best_new_task") for e in result.get("flip_events") or []}
    period, goals = cfg.task_alternating_period, cfg.task_alternating_value_list()
    phases = []
    for start in range(0, len(fits) - 1, period):
        end = min(start + period, len(fits)) - 1
        goal = goals[(start // period) % len(goals)]
        seg = fits[start + (1 if start else 0): end + 1]
        hit = next((i for i, f in enumerate(seg) if f >= 0.999), None)
        phases.append({"start": start, "goal": goal, "at_flip": at_flip.get(start),
                       "reached_1": hit is not None, "gens_to_1": hit, "end_genome": genomes[end]})
    by_goal = collections.defaultdict(list)
    for p in phases:
        by_goal[p["goal"]].append(p)
    for goal, ps in by_goal.items():
        ex = exact_many([p["end_genome"] for p in ps], cfg, goal)
        for p, e in zip(ps, ex):
            p["end_exact"] = bool(e)
    tag_struct = []
    if c["arm"] == "TAG":
        for p in phases[-len(goals) * 3:]:          # last three cycles
            if p.get("end_exact"):
                tag_struct.append({"goal": p["goal"], **structure(p["end_genome"], cfg, p["goal"])})
    for p in phases:
        del p["end_genome"]
    return {"arm": arm_name(c), "seed": c["seed"], "period": period, "phases": phases, "structure": tag_struct}


def load(sweep: Path):
    idx = json.loads((sweep / "sweep_index.json").read_text())
    return [(r["run_dir"], yaml.safe_load(open(Path(r["run_dir"]) / "config.yaml"))) for r in idx]


def fixed_report(name: str, rows: list[dict]) -> list[str]:
    lines = [f"## {name}", "", "| arm | runs | final exact (all 10k) | median first exact gen | "
             "tagged solvers: output runs / load-bearing / live RECV / dead RECV (medians) |", "|---|---|---|---|---|"]
    for arm in ("baseline", "tagged", "tagged+dup"):
        rs = [r for r in rows if r["arm"] == arm]
        if not rs:
            continue
        firsts = [r["first_exact_gen"] for r in rs if r["first_exact_gen"] is not None]
        st = [r["structure"] for r in rs if "structure" in r]
        stxt = " / ".join(f"{np.median([s[k] for s in st]):.0f}" for k in
                          ("output_runs", "load_bearing", "live_recv", "dead_recv")) if st else "-"
        lines.append(f"| {arm} | {len(rs)} | {sum(r['final_exact'] for r in rs)} | "
                     f"{np.median(firsts) if firsts else float('nan'):.0f} ({len(firsts)} ever exact) | {stxt} |")
    if any("structure" in r for r in rows):
        multi = collections.Counter((r["arm"], r["structure"]["output_runs"] > 1 or r["structure"]["live_recv"] > 0)
                                    for r in rows if "structure" in r)
        lines += ["", "Tagged exact solvers using more than one run (≥ 2 output runs or a live RECV): " +
                  ", ".join(f"{a}: {multi[(a, True)]}/{multi[(a, True)] + multi[(a, False)]}"
                            for a in ("tagged", "tagged+dup") if multi[(a, True)] + multi[(a, False)])]
    return lines + [""]


def mvg_report(name: str, rows: list[dict]) -> list[str]:
    lines = [f"## {name}", ""]
    for period in sorted({r["period"] for r in rows}):
        lines += [f"### period {period}", "",
                  "| arm | goal | third | phases | new-goal start (median best) | reached 1.0 | median gens to 1.0 | "
                  "phase-end exact (all 10k) |", "|---|---|---|---|---|---|---|---|"]
        for arm in ("baseline", "tagged", "tagged+dup"):
            rs = [r for r in rows if r["arm"] == arm and r["period"] == period]
            if not rs:
                continue
            n_ph = len(rs[0]["phases"])
            for goal in ("mbs_max_gt_5", "mbs_sum_gt_10", "mbs_and"):
                for label, lo, hi in (("early", 0, n_ph // 3), ("late", 2 * n_ph // 3, n_ph)):
                    ps = [p for r in rs for p in r["phases"][lo:hi] if p["goal"] == goal]
                    if not ps:
                        continue
                    starts = [p["at_flip"] for p in ps if p["at_flip"] is not None]
                    g1 = [p["gens_to_1"] for p in ps if p["reached_1"]]
                    lines.append(f"| {arm} | {goal} | {label} | {len(ps)} | "
                                 f"{np.median(starts) if starts else float('nan'):.3f} | "
                                 f"{100 * sum(p['reached_1'] for p in ps) / len(ps):.0f}% | "
                                 f"{np.median(g1) if g1 else float('nan'):.0f} | "
                                 f"{100 * sum(p['end_exact'] for p in ps) / len(ps):.0f}% |")
        st = [(r["arm"], s) for r in rows if r["period"] == period for s in r["structure"]]
        if st:
            lines += ["", "Tagged phase-end exact solvers (last three cycles), medians of output runs / "
                      "load-bearing / live RECV:"]
            for arm in ("tagged", "tagged+dup"):
                for goal in ("mbs_max_gt_5", "mbs_sum_gt_10", "mbs_and"):
                    ss = [s for a, s in st if a == arm and s["goal"] == goal]
                    if ss:
                        lines.append(f"- {arm} {goal}: n={len(ss)}, " + " / ".join(
                            f"{np.median([s[k] for s in ss]):.0f}" for k in ("output_runs", "load_bearing", "live_recv")))
        lines.append("")
    return lines


def main(day_dir: str) -> None:
    day = Path(day_dir)
    lines = ["# Map-bias overnight results", ""]
    with Pool(10) as pool:
        for name, kind in (("mapbias_or_race", "fixed"), ("mapbias_and_fixed", "fixed"),
                           ("mapbias_mvg_p20", "mvg"), ("mapbias_mvg_period", "mvg")):
            sweep = day / name
            if not (sweep / "sweep_index.json").exists():
                lines += [f"## {name}", "", "not run / no index", ""]
                continue
            complete = (sweep / "SWEEP_COMPLETE").exists()
            items = load(sweep)
            rows = pool.map(analyze_fixed if kind == "fixed" else analyze_mvg, items)
            (sweep / "analysis.json").write_text(json.dumps(rows, indent=1, default=str))
            head = f"{name}{'' if complete else ' (INCOMPLETE)'}"
            lines += fixed_report(head, rows) if kind == "fixed" else mvg_report(head, rows)
    (day / "overnight_summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
