"""Map-bias notebook §25: crossover v2 vs v1 — discovery, retention, champion, run census.

Per sweep and arm: champion exact (analysis.json from overnight_analysis), population-level
discovery (result.json exact_any.first_gen), retention (exact_any.final_count > 0 and its
median), and the run census (result.json run_stats) averaged over generations >= 1000
(>= 500 for 1500-generation sweeps). Fisher tests pair each v2 arm with the v1 arm that
has the same name minus " xv2". v1 replays: the final champion must equal the original
run's (seed-matched), as a check that tracking changed nothing.

Usage: uv run python experiments/chem_tape/s25_report.py experiments/output/2026-09-29 > report.md
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import fisher_exact

sys.path.insert(0, str(Path(__file__).parent))
import overnight_analysis as oa  # noqa: E402

SWEEPS = ["mapbias_xover_v2_xor_leftmost", "mapbias_xover_v2_xor_max", "mapbias_xover_v2_or_leftmost",
          "mapbias_xover_v2_or_tournament", "mapbias_or_tournament_ctrl"]
# v1 arms that replay an earlier sweep (sweep dir, arm name there).
REPLAYS = {
    ("mapbias_xover_v2_xor_leftmost", "tagged leftmost"): [
        ("experiments/output/2026-09-29/mapbias_xor_leftmost_pop", "tagged leftmost"),
        ("experiments/output/2026-09-28/mapbias_xor_leftmost_more", "tagged leftmost")],
    ("mapbias_xover_v2_xor_max", "tagged"): [("experiments/output/2026-09-29/mapbias_xor_race_pop", "tagged")],
}
CENSUS = ("runs", "output_runs", "unread", "helpers", "with_helper", "no_runs", "no_output", "tail_nops")


def last_champion(run_dir) -> str:
    return list(csv.DictReader(open(Path(run_dir) / "history.csv")))[-1]["best_genotype_hex"]


def main(day: str) -> None:
    day = Path(day)
    print("| sweep | arm | n | champion exact | population exact | retained at end | median exact members at end (retained runs) | median first exact gen (pop) |")
    print("|---|---|---|---|---|---|---|---|")
    census_lines, tests, replay_lines = [], [], []
    for sw in SWEEPS:
        d = day / sw
        items = oa.load(d)
        champ = {(r["arm"], r["seed"]): r for r in json.loads((d / "analysis.json").read_text())}
        by_arm: dict[str, list] = {}
        for rd, c in items:
            res = json.loads((Path(rd) / "result.json").read_text())
            arm = oa.arm_name(c)
            by_arm.setdefault(arm, []).append((rd, c, res, champ[(arm, c["seed"])]))
        counts = {}
        for arm, rs in by_arm.items():
            n = len(rs)
            ch = sum(r[3]["final_exact"] for r in rs)
            ex = [r[2].get("exact_any") or {} for r in rs]
            pop = sum(e.get("first_gen") is not None for e in ex)
            ret = [e["final_count"] for e in ex if e.get("final_count")]
            fg = [e["first_gen"] for e in ex if e.get("first_gen") is not None]
            counts[arm] = (pop, n, ch)
            med = lambda x: f"{np.median(x):.0f}" if x else "-"  # noqa: E731
            print(f"| {sw.removeprefix('mapbias_')} | {arm} | {n} | {ch} | {pop} | {len(ret)} | {med(ret)} | {med(fg)} |")
            stats = [r[2].get("run_stats") for r in rs]
            if all(stats):
                g0 = 1000 if rs[0][1]["generations"] >= 3000 else 500
                vals = {k: np.mean([np.mean([s[k] for s in st if s["gen"] >= g0]) for st in stats]) for k in CENSUS}
                census_lines.append(f"| {sw.removeprefix('mapbias_')} | {arm} | g ≥ {g0} | " +
                                    " | ".join(f"{vals[k]:.2f}" for k in CENSUS) + " |")
            for (rsw, rarm), origs in REPLAYS.items():
                if rsw != sw or rarm != arm:
                    continue
                orig = {}
                for od, oarm in origs:
                    for ord_, oc in oa.load(Path(od)):
                        if oa.arm_name(oc) == oarm:
                            orig[oc["seed"]] = ord_
                same = sum(last_champion(r[0]) == last_champion(orig[r[1]["seed"]]) for r in rs if r[1]["seed"] in orig)
                replay_lines.append(f"- {sw.removeprefix('mapbias_')} / {arm}: {same}/{sum(r[1]['seed'] in orig for r in rs)} "
                                    "final champions equal the original run's")
        for arm, (pop, n, ch) in counts.items():
            if arm.endswith(" xv2") and arm[:-4] in counts:
                p1, n1, c1 = counts[arm[:-4]]
                pp = fisher_exact([[pop, n - pop], [p1, n1 - p1]])[1]
                pc = fisher_exact([[ch, n - ch], [c1, n1 - c1]])[1]
                tests.append(f"- {sw.removeprefix('mapbias_')}: v2 vs v1 ({arm[:-4]}): population {pop}/{n} vs {p1}/{n1} "
                             f"(Fisher p = {pp:.3g}); champion {ch}/{n} vs {c1}/{n1} (p = {pc:.3g})")
    print("\nv2 vs v1 (two-sided Fisher):\n" + "\n".join(tests))
    print("\nReplay check:\n" + "\n".join(replay_lines))
    print("\nRun census, population means averaged over generations (then over seeds):\n")
    print("| sweep | arm | gens | " + " | ".join(CENSUS) + " |")
    print("|---|---|---|" + "---|" * len(CENSUS))
    print("\n".join(census_lines))


if __name__ == "__main__":
    main(sys.argv[1])
