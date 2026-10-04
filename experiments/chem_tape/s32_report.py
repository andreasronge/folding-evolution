#!/usr/bin/env python3
"""Map-bias §32 report (Plans/s32-mate-latent-cases.md): arms K (latent helper), J (crossover
mate), L (256 training cases) and G2 (more seeds of §31 G at L 64 / 0.3), with §31 arm G's
matching cells as the reference.

    uv run python experiments/chem_tape/s32_report.py --roots DIR [DIR ...] --g-root S31_STAGE4_DIR \
        --out DIR [--workers 10]

Seeded verdicts as §31 (non-elite final population, >= 20 fully exact). Random-start runs
(Fable, twentieth review):
- training-solved at the end: >= 10% of the final census training-perfect;
- first established form: first census with >= 20 of 256 fully exact and > 90% one form;
- helper content of shared verdicts: the pure helper's value on all 10,000 lists is a function
  of the sum only (B-type), of the max only (A-type), or neither (mixed).
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import s31_report as r31  # noqa: E402
import shared_helper as sh  # noqa: E402
from folding_evolution.chem_tape import tagged  # noqa: E402
from s32_make_sweeps import partly_plus_b  # noqa: E402

FORMS = ("shared", "partly", "duplicated")
SUM, MAX = sh.X_ALL.sum(axis=1), sh.X_ALL.max(axis=1)


def function_of(v: np.ndarray, key: np.ndarray) -> bool:
    for k in np.unique(key):
        if len(np.unique(v[key == k])) > 1:
            return False
    return True


def helper_content(pop: np.ndarray, ne: int, m, limit: int = 20) -> str:
    """Majority content of the pure helpers in up to `limit` non-elite shared genomes."""
    ex, kinds = sh.Exactness(), Counter()
    for g in pop[ne:]:
        if sum(kinds.values()) >= limit:
            break
        if not ex(g).all():
            continue
        c = sh.classify(g, m)
        if c["form"] != "shared":
            continue
        vals = tagged.genome_outputs(g, m, combine="leftmost", all_runs=True)
        for k in c["pure_helpers"]:
            v = vals[k]
            fs, fm = function_of(v, SUM), function_of(v, MAX)
            kinds["B" if fs and not fm else "A" if fm and not fs else "const" if fs else "mixed"] += 1
    return kinds.most_common(1)[0][0] if kinds else "–"


def identify32(cfg: dict, comp_hex: dict) -> dict:
    L, xo = cfg["tape_length"], cfg["crossover_rate"]
    tapes = [h for h in (cfg.get("seed_tapes") or "").split(",") if h]
    if tapes:
        n_comp = sum(h == comp_hex.get(L) for h in tapes)
        if n_comp == len(tapes):
            return {"arm": "K", "cell": ("alone", xo)}
        if cfg.get("seed_counts"):
            return {"arm": "K", "cell": (f"{cfg['seed_counts'].split(',')[0]} copy", xo)}
        return {"arm": "K", "cell": (f"1/{len(tapes)}", xo)}
    mate = cfg.get("crossover_mate", "selected")
    # G2 (seeds 50-99) is kept apart from the §31 G reference (seeds 0-49): codex review 1
    arm = "L" if cfg["n_examples"] != 64 else "J" if mate != "selected" else "G2" if cfg["seed"] >= 50 else "G"
    return {"arm": arm, "cell": (L, xo, mate, cfg["n_examples"])}


COMP_HEX = {L: partly_plus_b(L).tobytes().hex() for L in (32, 64, 128)}


def classify32(path: str) -> dict:
    r = r31.classify_run(path)
    r.update(identify32(r["cfg"], COMP_HEX))
    pop = np.load(Path(path) / "final_population.npz")["genotypes"]
    ne = r["cfg"]["elite_count"]
    if r["arm"] == "K":
        r["b_intact"] = float(np.mean([sh.helper_intact(g) for g in pop[ne:]]))
    else:
        st = r["stats"]
        est = next((s for s in st if s["n_fully_exact"] >= r31.MIN_EXACT and
                    max((s[k] or 0) for k in FORMS) > 0.9), None)
        r["est_gen"] = est["gen"] if est else None
        r["est_form"] = max(FORMS, key=lambda k: est[k] or 0) if est else None
        r["train_solved"] = st[-1]["train_perfect"] >= 0.1
        if r["n_exact"] >= r31.MIN_EXACT:
            shares = {k: r["forms"].get(k, 0) / r["n_exact"] for k in FORMS}
            top = max(shares, key=shares.get)
            r["verdict"] = top if shares[top] > 0.9 else "mixed"
        else:
            r["verdict"] = None
        r["helper"] = helper_content(pop, ne, sh.machine()) if r["verdict"] == "shared" else None
    return r


def k_table(runs) -> list[str]:
    out = ["### Arm K: shared vs partly shared plus an unread B run (L 64, 300 generations)", "",
           "| start | crossover | seeds | won (> 90% shared) | shared gone | in between | lost the solution | "
           "slot-0 elite shared: won / all | genomes with the B run intact (mean, non-elite) |",
           "|---|---|---|---|---|---|---|---|---|"]
    cells = [(s, xo) for s in ("1/32", "1/10") for xo in (0.1, 0.3, 0.7)] + \
            [("1 copy", 0.0), ("1 copy", 0.3), ("alone", 0.3)]
    for c in cells:
        rs = [r for r in runs if r["arm"] == "K" and r["cell"] == c]
        if not rs:
            continue
        o = Counter(r31.outcome(r) for r in rs)
        se = [r for r in rs if r["elites"][0] == "shared"]
        out.append(f"| {c[0]} | {c[1]} | {len(rs)} | {o['won']} | {o['gone']} | {o['between']} | {o['no_solution']} | "
                   f"{sum(r31.outcome(r) == 'won' for r in se)} / {len(se)} | "
                   f"{np.mean([r['b_intact'] for r in rs]):.2f} |")
    return out + ["", "\"alone\": the competitor only; there is no shared form, so the won/gone columns do "
                  "not apply (they read 0 / all). Its last column is the decay of an unread B run.", ""]


def random_table(runs) -> list[str]:
    out = ["### Random starts: §32 arms J, L, G2 and §31 arm G reference (3000 generations)", "",
           "| arm | L | crossover | mate | cases | seeds | training-solved at end | exact population at end "
           "(≥ 20) | first established form: shared / partly / dup | final verdict: shared / partly / dup / mixed | "
           "shared verdicts: B-type / A-type / other | median s per run |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    cells = sorted({(r["arm"], r["cell"]) for r in runs if r["arm"] in ("G", "G2", "J", "L")}, key=str)
    for arm, c in cells:
        rs = [r for r in runs if r["arm"] == arm and r["cell"] == c]
        seeds = sorted(r["cfg"]["seed"] for r in rs)
        est = Counter(r["est_form"] for r in rs if r["est_form"])
        ver = Counter(r["verdict"] for r in rs if r["verdict"])
        hel = Counter(r["helper"] for r in rs if r["helper"])
        L, xo, mate, cases = c
        label = "G (§31)" if arm == "G" else arm
        out.append(f"| {label} | {L} | {xo} | {mate} | {cases} | {len(rs)} ({seeds[0]}–{seeds[-1]}) | "
                   f"{sum(r['train_solved'] for r in rs)} | {sum(r['n_exact'] >= r31.MIN_EXACT for r in rs)} | "
                   f"{est['shared']} / {est['partly']} / {est['duplicated']} | "
                   f"{ver['shared']} / {ver['partly']} / {ver['duplicated']} / {ver['mixed']} | "
                   f"{hel['B']} / {hel['A']} / {sum(hel.values()) - hel['B'] - hel['A']} | "
                   f"{np.median([r['elapsed'] for r in rs]):.0f} |")
    return out + [""]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", type=Path, nargs="+", required=True)
    ap.add_argument("--g-root", type=Path, default=None, help="§31 arm G sweep root (reference cells)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    dirs, metas = [], []
    for root in args.roots:
        if not root.exists():
            continue
        if (root / "metadata.json").exists():
            metas.append(json.loads((root / "metadata.json").read_text()))
        dirs += [str(p) for p in sorted(root.iterdir()) if (p / "result.json").exists()]
    ref = []
    if args.g_root and args.g_root.exists():
        for p in sorted(args.g_root.iterdir()):
            if (p / "result.json").exists():
                cfg = yaml.safe_load((p / "config.yaml").read_text())
                if (cfg["tape_length"], cfg["crossover_rate"]) in ((64, 0.3), (64, 0.7), (128, 0.3), (64, 0.0)):
                    ref.append(str(p))
    with mp.get_context("spawn").Pool(args.workers) as pool:
        runs = pool.map(classify32, dirs + ref, chunksize=2)
    keys = Counter((r["arm"], r["cell"], r["cfg"]["seed"]) for r in runs)
    short = [r["dir"] for r in runs if r["stats"][-1]["gen"] != r["cfg"]["generations"]]
    md = ["## Validation", "",
          f"- runs: {len(runs)} ({len(ref)} §31 reference); duplicate run keys: "
          f"{sum(v > 1 for v in keys.values())}; stopped early: {len(short)}"]
    for m in metas:
        md.append(f"- entry {m.get('id')}: status {m.get('status')}, exit {m.get('exit_code')}, "
                  f"commit {str(m.get('git_commit'))[:7]}, dirty {m.get('git_dirty')}, wall {m.get('wall_seconds')} s")
    md += ["", "## Readouts", ""] + k_table(runs) + random_table(runs)
    (args.out / "s32_report.md").write_text("\n".join(md) + "\n")
    slim = [{k: (list(v) if isinstance(v, tuple) else v) for k, v in r.items() if k not in ("cfg", "stats")}
            for r in runs]
    (args.out / "s32_runs.json").write_text(json.dumps(slim, indent=1, default=str))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
