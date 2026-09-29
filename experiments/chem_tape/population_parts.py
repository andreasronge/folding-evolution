"""Do final populations hold complementary parts? (map-bias notebook §21-22)

For each run with a final_population.npz, every distinct genome is evaluated on all
10,000 lists. The four quadrants of (max>5, sum>10) split the inputs; a genome "covers" a
quadrant if it is right on >= COVER of that quadrant's lists. For XOR the target is 1 on the
two mixed quadrants and 0 on the others, so the partial solutions seen so far cover three
quadrants (e.g. one XOR half, OR, NAND).

Per run: how many individuals are exact on all lists (and whether the recorded champion is
one); the distinct quadrant-cover sets present; whether the union of covers present reaches
all four quadrants ("complementary parts present") while no individual covers all four; the
number of individuals in the largest cover class.

Usage: uv run python experiments/chem_tape/population_parts.py <sweep dir> [<sweep dir> ...]
"""

from __future__ import annotations

import collections
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import overnight_analysis as oa  # noqa: E402

from folding_evolution.chem_tape.evaluate import evaluate_population  # noqa: E402
from folding_evolution.chem_tape.tasks import build_task  # noqa: E402
from dataclasses import replace  # noqa: E402

COVER = 0.95
ALL = np.array(oa.ALL)
QUAD = (ALL.max(axis=1) > 5).astype(int) * 2 + (ALL.sum(axis=1) > 10).astype(int)   # 0..3 = (m, s)
QNAME = {0: "--", 1: "-S", 2: "M-", 3: "MS"}


def analyze(item) -> dict:
    run_dir, c = item
    cfg = oa.cfg_of(c)
    f = Path(run_dir) / "final_population.npz"
    if not f.exists():
        return {"run_dir": run_dir, "missing": True}
    pop = np.load(f)["genotypes"]
    keys = [g.tobytes() for g in pop]
    uniq = list(dict.fromkeys(keys))
    t = replace(build_task(cfg, cfg.seed), inputs=oa.ALL, labels=oa.LABELS[cfg.task])
    _, preds = evaluate_population([np.frombuffer(k, dtype=np.uint8) for k in uniq], t, cfg)
    ok = preds == oa.LABELS[cfg.task][None, :]
    qacc = np.stack([ok[:, QUAD == q].mean(axis=1) for q in range(4)], axis=1)
    covers = [frozenset(q for q in range(4) if qacc[i, q] >= COVER) for i in range(len(uniq))]
    exact = ok.all(axis=1)
    count = collections.Counter(keys)
    n_by = collections.Counter()
    for k, cv in zip(uniq, covers):
        n_by[cv] += count[k]
    union = frozenset().union(*covers)
    champ = Path(run_dir) / "result.json"
    champ_hex = json.loads(champ.read_text()).get("best_genotype_hex") if champ.exists() else None
    champ_exact = None
    if champ_hex:
        ci = uniq.index(bytes.fromhex(champ_hex)) if bytes.fromhex(champ_hex) in uniq else None
        champ_exact = bool(exact[ci]) if ci is not None else None
    top = n_by.most_common(1)[0]
    return {"run_dir": run_dir, "arm": oa.arm_name(c), "seed": c["seed"], "n_unique": len(uniq),
            "n_exact": int(sum(count[k] for k, e in zip(uniq, exact) if e)), "champion_exact": champ_exact,
            "any_full_cover": bool(any(len(cv) == 4 for cv in covers)),
            "union_all_four": len(union) == 4,
            "cover_classes": {"".join(QNAME[q] + " " for q in sorted(cv)).strip() or "none": n
                              for cv, n in n_by.most_common(6)},
            "largest_class": ("".join(QNAME[q] + " " for q in sorted(top[0])).strip() or "none", top[1])}


def main() -> None:
    items = []
    for sweep in sys.argv[1:]:
        items += oa.load(Path(sweep))
    with Pool(10) as pool:
        rows = pool.map(analyze, items)
    rows = [r for r in rows if not r.get("missing")]
    for sweep in sys.argv[1:]:
        Path(sweep, "population_parts.json").write_text(
            json.dumps([r for r in rows if Path(r["run_dir"]).resolve().is_relative_to(Path(sweep).resolve())],
                       indent=1))
    for key in dict.fromkeys((Path(r["run_dir"]).parent.name, r["arm"]) for r in rows):
        rs = [r for r in rows if (Path(r["run_dir"]).parent.name, r["arm"]) == key]
        arm = f"{key[0]} — {key[1]}"
        solved = [r for r in rs if r["n_exact"] > 0]
        uns = [r for r in rs if r["n_exact"] == 0]
        print(f"\n## {arm} ({len(rs)} runs)")
        print(f"populations with >= 1 exact individual: {len(solved)}; champion exact in "
              f"{sum(bool(r['champion_exact']) for r in rs)}; exact individual present but champion not: "
              f"{sum(r['n_exact'] > 0 and r['champion_exact'] is False for r in rs)}")
        print(f"unsolved populations whose quadrant covers together reach all four: "
              f"{sum(r['union_all_four'] for r in uns)}/{len(uns)}")
        lc = collections.Counter(r["largest_class"][0] for r in uns)
        print(f"unsolved: largest cover class: {dict(lc)}")


if __name__ == "__main__":
    main()
