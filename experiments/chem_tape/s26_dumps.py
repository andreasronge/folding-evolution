"""Map-bias notebook §26: structure of final populations and solved-by-generation curves.

For each sweep directory (tagged arms with dump_final_population and track_exact_any):
- solved by generation g: share of runs whose population held an exact individual by g
  (result.json exact_any.first_gen), g = 500 … 3000 — not conditional on solving;
- final-population structure, split by whether the run was solved (population level):
  output-run body length (first output run, trailing NOPs stripped), leader cells, runs,
  share of genomes with an extra (silent under leftmost) output run;
- exact individuals (training-perfect members checked on all 10,000 lists): share that
  use a helper (tagged.run_census), share whose output run is the last run.

Usage: uv run python experiments/chem_tape/s26_dumps.py SWEEP_DIR [...]
"""

from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import overnight_analysis as oa  # noqa: E402
from folding_evolution.chem_tape import tagged  # noqa: E402

GENS = (500, 1000, 1500, 2000, 2500, 3000)


def per_run(item) -> dict:
    rd, c = item
    cfg = oa.cfg_of(c)
    res = json.loads((Path(rd) / "result.json").read_text())
    z = np.load(Path(rd) / "final_population.npz")
    pop, fit = z["genotypes"], z["fitnesses"]
    rows = []
    for g in pop:
        runs = tagged.parse_runs(g)
        out = [k for k, (t, _) in enumerate(runs) if t == tagged.OUTPUT_TAG]
        body = len(tagged._strip_trailing_nops(runs[out[0]][1])) if out else None
        rows.append((len(runs), len(tagged.leader_cells(g)), body, len(out) > 1))
    perfect = [i for i in range(len(pop)) if fit[i] >= 1.0]
    uniq = {pop[i].tobytes(): i for i in perfect}
    ex = oa.exact_many([pop[i] for i in uniq.values()], cfg, cfg.task) if uniq else []
    exact_keys = {k for k, e in zip(uniq, ex) if e}
    exact = [i for i in perfect if pop[i].tobytes() in exact_keys]
    helper = [tagged.run_census(pop[i], cfg.tag_combine)[3] > 0 for i in exact]
    last = []
    for i in exact:
        runs = tagged.parse_runs(pop[i])
        out = [k for k, (t, _) in enumerate(runs) if t == tagged.OUTPUT_TAG]
        last.append(bool(out) and out[0] == len(runs) - 1)
    bodies = [r[2] for r in rows if r[2] is not None]
    return {"arm": oa.arm_name(c), "first_gen": (res.get("exact_any") or {}).get("first_gen"),
            "runs": np.mean([r[0] for r in rows]), "leader": np.mean([r[1] for r in rows]),
            "body": np.mean(bodies) if bodies else np.nan, "extra_out": np.mean([r[3] for r in rows]),
            "n_exact": len(exact), "helper": helper, "last": last}


def main(dirs: list[str]) -> None:
    items = [it for d in dirs for it in oa.load(Path(d))]
    with Pool(4) as pool:
        rows = pool.map(per_run, items)
    arms = list(dict.fromkeys(r["arm"] for r in rows))
    print("Solved (population has an exact individual) by generation:\n")
    print("| arm | n | " + " | ".join(str(g) for g in GENS) + " |")
    print("|---|---|" + "---|" * len(GENS))
    for a in arms:
        rs = [r for r in rows if r["arm"] == a]
        print(f"| {a} | {len(rs)} | " + " | ".join(
            str(sum(r["first_gen"] is not None and r["first_gen"] <= g for r in rs)) for g in GENS) + " |")
    print("\nFinal populations (means over runs of per-genome means):\n")
    print("| arm | runs solved? | n | runs | leader | output body | extra output run | "
          "exact individuals with a helper | output run is last (exact) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for a in arms:
        for solved in (True, False):
            rs = [r for r in rows if r["arm"] == a and (r["first_gen"] is not None) == solved]
            if not rs:
                continue
            h = [x for r in rs for x in r["helper"]]
            la = [x for r in rs for x in r["last"]]
            pct = lambda x: f"{100 * np.mean(x):.0f}% of {len(x)}" if x else "-"  # noqa: E731
            print(f"| {a} | {'solved' if solved else 'unsolved'} | {len(rs)} | {np.mean([r['runs'] for r in rs]):.2f} | "
                  f"{np.mean([r['leader'] for r in rs]):.1f} | {np.nanmean([r['body'] for r in rs]):.1f} | "
                  f"{100 * np.mean([r['extra_out'] for r in rs]):.0f}% | {pct(h)} | {pct(la)} |")


if __name__ == "__main__":
    main(sys.argv[1:])
