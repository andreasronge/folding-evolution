"""Analysis of the §13 queue (map-bias notebook §14): attribution controls and
the evolvable combiner, compared with the overnight runs of §12.

Usage: uv run python experiments/chem_tape/s13_analysis.py experiments/output/<s13 date> experiments/output/2026-09-26
"""

from __future__ import annotations

import collections
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import fisher_exact

import overnight_analysis as oa
from folding_evolution.chem_tape import tagged


def label(c: dict) -> str:
    if c["arm"] != "TAG":
        return f"baseline {c['alphabet']} tape{c['tape_length']} mu{c['mutation_rate']}"
    parts = [c["alphabet"], f"mu{c['mutation_rate']}"]
    if c.get("run_duplication_rate"):
        parts.append("dup")
    if c.get("crossover_rate", 0.7) == 0:
        parts.append("no-crossover")
    if c.get("tag_combine", "max") != "max":
        parts.append(c["tag_combine"])
    return "TAG " + " ".join(parts)


def fixed_rows(sweep: Path, pool) -> dict[str, list[dict]]:
    items = oa.load(sweep)
    rows = pool.map(oa.analyze_fixed, items)
    out = collections.defaultdict(list)
    for (run_dir, c), r in zip(items, rows):
        r["label"], r["run_dir"] = label(c), run_dir
        out[r["label"]].append(r)
    return out


def markers_in_output(run_dir: str) -> str:
    import csv
    rows = list(csv.DictReader(open(Path(run_dir) / "history.csv")))
    g = np.frombuffer(bytes.fromhex(rows[-1]["best_genotype_hex"]), dtype=np.uint8)
    out = [b for t, b in tagged.parse_runs(g) if t == tagged.OUTPUT_TAG]
    joins = [tagged._marker(b) for b in out[1:]]
    names = {None: "max", tagged.C_MIN: "min", tagged.C_ADD: "add", tagged.C_GATE: "gate"}
    return f"{len(out)} output runs, joins: {', '.join(names[j] for j in joins) or '-'}"


def main(s13: str, day1: str) -> None:
    s13, day1 = Path(s13), Path(day1)
    lines = ["# §13 results", ""]
    with Pool(10) as pool:
        ref_or = fixed_rows(day1 / "mapbias_or_race", pool)
        ref_and = fixed_rows(day1 / "mapbias_and_fixed", pool)
        comparisons = [("mapbias_or_nox", ref_or), ("mapbias_or_leftmost", ref_or), ("mapbias_or_basectrl", ref_or),
                       ("mapbias_comb_or", ref_or), ("mapbias_comb_and", ref_and)]
        for name, ref in comparisons:
            sweep = s13 / name
            if not (sweep / "sweep_index.json").exists():
                lines += [f"## {name}", "", "not run", ""]
                continue
            new = fixed_rows(sweep, pool)
            lines += [f"## {name}{'' if (sweep / 'SWEEP_COMPLETE').exists() else ' (INCOMPLETE)'}", "",
                      "| setup | exact | median first exact gen | multi-run tagged solvers |", "|---|---|---|---|"]
            show = {**new, **{f"(ref) {k}": v for k, v in ref.items()}}
            for k, rs in show.items():
                ex = sum(r["final_exact"] for r in rs)
                firsts = [r["first_exact_gen"] for r in rs if r["first_exact_gen"] is not None]
                st = [r["structure"] for r in rs if "structure" in r]
                multi = sum(s["output_runs"] > 1 or s["live_recv"] > 0 for s in st)
                lines.append(f"| {k} | {ex}/{len(rs)} | {np.median(firsts) if firsts else float('nan'):.0f} | "
                             f"{f'{multi}/{len(st)}' if st else '-'} |")
            lines.append("")
            for k, rs in new.items():
                a = sum(r["final_exact"] for r in rs)
                for rk, rrs in ref.items():
                    b = sum(r["final_exact"] for r in rrs)
                    p = fisher_exact([[a, len(rs) - a], [b, len(rrs) - b]])[1]
                    lines.append(f"- {k} {a}/{len(rs)} vs (ref) {rk} {b}/{len(rrs)}: p = {p:.4f}")
            if name.startswith("mapbias_comb"):
                lines += ["", "Exact combiner solvers, output group:"]
                for k, rs in new.items():
                    for r in rs:
                        if r["final_exact"]:
                            lines.append(f"- seed {r['seed']}: {markers_in_output(r['run_dir'])}")
            lines.append("")
        mvg = s13 / "mapbias_mvg_matched"
        if (mvg / "sweep_index.json").exists():
            rows = pool.map(oa.analyze_mvg, oa.load(mvg))
            ref = json.loads((day1 / "mapbias_mvg_p20" / "analysis.json").read_text())
            lines += [f"## mapbias_mvg_matched{'' if (mvg / 'SWEEP_COMPLETE').exists() else ' (INCOMPLETE)'}", "",
                      "| setup | runs with exact AND at a late phase end | ever | early max>5 / sum>10 phases reaching 1.0 |",
                      "|---|---|---|---|"]

            def summarise(rs, name):
                k = len(rs[0]["phases"])
                late = sum(any(p["goal"] == "mbs_and" and p["end_exact"] for p in r["phases"][2 * k // 3:]) for r in rs)
                ever = sum(any(p["goal"] == "mbs_and" and p["end_exact"] for p in r["phases"]) for r in rs)
                early = [p for r in rs for p in r["phases"][:k // 3]]
                pm = np.mean([p["reached_1"] for p in early if p["goal"] == "mbs_max_gt_5"])
                ps = np.mean([p["reached_1"] for p in early if p["goal"] == "mbs_sum_gt_10"])
                lines.append(f"| {name} | {late}/{len(rs)} | {ever}/{len(rs)} | {100 * pm:.0f}% / {100 * ps:.0f}% |")
            for arm in ("tagged", "tagged+dup"):
                summarise([r for r in rows if r["arm"] == arm], f"{arm} (matched rate)")
            for arm in ("baseline", "tagged", "tagged+dup"):
                summarise([r for r in ref if r["arm"] == arm], f"(ref mvg_p20) {arm}")
            lines.append("")
    (s13 / "s13_summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
