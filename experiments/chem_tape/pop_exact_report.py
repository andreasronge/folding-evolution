"""Population-level vs champion exactness for replayed sweeps (map-bias notebook §24).

Each argument is REPLAY_DIR=ORIGINAL_DIR. Replay runs have track_exact_any (result.json
"exact_any"); original runs have analysis.json from overnight_analysis (champion-based).
Runs are matched by arm label and seed; configs must be equal apart from the tracking
flags. The replay's final champion must equal the original's (history.csv, last row),
or the run is excluded — a check that the replay really is the same run.

Usage: uv run python experiments/chem_tape/pop_exact_report.py REPLAY=ORIG [...] > report.md
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

_STRIP = ("track_exact_any", "track_lineage", "dump_final_population")


def key(c: dict) -> tuple:
    return (oa.arm_name(c), c["seed"])


def last_champion(run_dir) -> str:
    rows = list(csv.DictReader(open(Path(run_dir) / "history.csv")))
    return rows[-1]["best_genotype_hex"]


def main() -> None:
    print("| sweep | arm | champion exact | population exact | +hidden | median first exact (champion / population) | replay matches |")
    print("|---|---|---|---|---|---|---|")
    for pair in sys.argv[1:]:
        rep, orig = map(Path, pair.split("="))
        o_items = {key(c): rd for rd, c in oa.load(orig)}
        o_rows = {(r["arm"], r["seed"]): r for r in json.loads((orig / "analysis.json").read_text())}
        o_cfg = {key(c): c for _, c in oa.load(orig)}
        by_arm: dict[str, list] = {}
        bad = []
        for rd, c in oa.load(rep):
            k = key(c)
            norm = lambda d: {f: v for f, v in d.items() if f not in _STRIP}
            if norm(c) != norm(o_cfg[k]):
                raise SystemExit(f"{rep.name} {k}: config differs from the original beyond {_STRIP}")
            res = json.loads((Path(rd) / "result.json").read_text())["exact_any"]
            o = o_rows[k]
            same = last_champion(rd) == last_champion(o_items[k])
            if not same:
                bad.append(k)
                continue                    # not the same run: excluded from the counts
            by_arm.setdefault(k[0], []).append((o, res, same))
        if bad:
            print(f"<!-- {rep.name}: replay differs from the original, excluded: {bad} -->")
        for arm, rs in by_arm.items():
            champ = sum(o["final_exact"] for o, _, _ in rs)
            pop = sum(r["first_gen"] is not None for _, r, _ in rs)
            fc = [o["first_exact_gen"] for o, _, _ in rs if o["first_exact_gen"] is not None]
            fp = [r["first_gen"] for _, r, _ in rs if r["first_gen"] is not None]
            med = lambda x: f"{np.median(x):.0f}" if x else "-"
            print(f"| {rep.name} | {arm} | {champ}/{len(rs)} | {pop}/{len(rs)} | {pop - champ} | "
                  f"{med(fc)} / {med(fp)} | {sum(s for *_, s in rs)}/{len(rs)} |")


if __name__ == "__main__":
    main()
