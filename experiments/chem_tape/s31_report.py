#!/usr/bin/env python3
"""Map-bias §31 report (Plans/s31-dose-reciprocal-stage4.md): arms D (crossover dose),
E (reciprocal), F (few copies, crossover off) and G (stage 4, random starts).

    uv run python experiments/chem_tape/s31_report.py --roots DIR [DIR ...] --out DIR \
        [--s30-roots DIR ...] [--figdir DIR] [--workers 10]

--s30-roots: the §30 arm A/B sweep roots. Their crossover 0 and 0.7 runs in arm D's cells are
re-classified with the same final-population criterion and plotted as the dose endpoints
(codex review 1: never mix §30's census-based wins with these).

Final outcomes come from each run's final population without the elite slots (0 ..
elite_count-1), classified by knockout. A form verdict needs >= MIN_EXACT fully exact
non-elite individuals; a run below that is "lost the solution" (seeded arms) or "unsolved
at the end" (G), never a form outcome. Elite forms are listed separately.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import shared_helper as sh  # noqa: E402

MIN_EXACT = 20
FORMS = ("shared", "partly", "duplicated")


def identify(cfg: dict) -> dict:
    """Arm and cell of a §31 run from its config."""
    L, xo = cfg["tape_length"], cfg["crossover_rate"]
    if not cfg.get("seed_tapes"):
        return {"arm": "G", "cell": (L, xo)}
    known = {sh.form_genome(n, L).tobytes().hex(): n for n in sh.FORMS if sh.form_genome(n, L) is not None}
    names = [known.get(h, "?") for h in cfg["seed_tapes"].split(",") if h]
    comp = next((n for n in names if n != "shared"), "?")
    if cfg.get("seed_counts"):
        n_shared = int(cfg["seed_counts"].split(",")[0])
        arm = "E" if n_shared >= 512 else "F"
        return {"arm": arm, "cell": (comp, L, xo, n_shared)}
    return {"arm": "D", "cell": (comp, L, xo, f"1/{len(names)}")}


def classify_run(path: str) -> dict:
    d = Path(path)
    cfg = yaml.safe_load((d / "config.yaml").read_text())
    res = json.loads((d / "result.json").read_text())
    pop = np.load(d / "final_population.npz")["genotypes"]
    ne = cfg["elite_count"]
    m, ex, cache = sh.machine(), sh.Exactness(), {}
    forms: Counter = Counter()
    for g in pop[ne:]:
        if ex(g).all():
            k = sh.semantic_key(g)
            if k not in cache:
                cache[k] = sh.classify(g, m)["form"]
            forms[cache[k]] += 1
    elites = [sh.classify(pop[i], m)["form"] for i in range(ne)]
    return {"dir": path, "cfg": cfg, "stats": res["shared_stats"], "run_stats": res["run_stats"][-1],
            "forms": dict(forms), "n_exact": sum(forms.values()), "elites": elites,
            "elapsed": res["elapsed_sec"], **identify(cfg)}


def outcome(r: dict) -> str:
    n = r["n_exact"]
    if n < MIN_EXACT:
        return "no_solution"
    sh_ = r["forms"].get("shared", 0) / n
    return "won" if sh_ > 0.9 else "gone" if sh_ == 0 else "between"


def seeded_table(runs, arm, title, cells, extra=None) -> list[str]:
    out = [f"### {title}", "",
           "| contest | L | crossover | shared at start | seeds | won (> 90% shared) | shared gone | in between | "
           "lost the solution (< 20 exact) | slot-0 elite shared: won / all | mean shared share (verdict runs) |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in cells:
        rs = [r for r in runs if r["arm"] == arm and r["cell"] == c]
        o = Counter(outcome(r) for r in rs)
        se = [r for r in rs if r["elites"][0] == "shared"]         # slot 0 keeps its generation-0 genome
        won_se = sum(outcome(r) == "won" for r in se)
        sh_ = [r["forms"].get("shared", 0) / r["n_exact"] for r in rs if r["n_exact"] >= MIN_EXACT]
        comp, L, xo, start = c
        out.append(f"| {comp} | {L} | {xo} | {start} | {len(rs)} | {o['won']} | {o['gone']} | {o['between']} | "
                   f"{o['no_solution']} | {won_se} / {len(se)} | {np.mean(sh_):.2f} |" if sh_ else
                   f"| {comp} | {L} | {xo} | {start} | {len(rs)} | {o['won']} | {o['gone']} | {o['between']} | "
                   f"{o['no_solution']} | {won_se} / {len(se)} | – |")
        if extra:
            extra(c, rs, o)
    return out + [""]


def stage4(runs) -> list[str]:
    out = ["### Arm G: stage 4, random starts (3000 generations, 50 seeds)", "",
           "| L | crossover | seeds | fully exact ever (census) | median first generation | form at first "
           "census with fully exact: shared / partly / duplicated / other | end (final population, non-elite "
           "fully exact): ≥ 20 / 1–19 / 0 | final verdict (≥ 20): shared / partly / duplicated / mixed | "
           "final training-perfect share (mean) | any shared individual (census) | lost (census once ≥ 20 "
           "of 256 fully exact, end < 20) | median s per run |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for L in (32, 64, 128):
        for xo in (0.7, 0.3, 0.0):
            rs = [r for r in runs if r["arm"] == "G" and r["cell"] == (L, xo)]
            if not rs:
                continue
            firsts, first_forms = [], Counter()
            anysh = lost = 0
            for r in rs:
                st = r["stats"]
                f = next((s for s in st if s["n_fully_exact"] > 0), None)
                if f is not None:
                    firsts.append(f["gen"])
                    shares = {k: f[k] or 0 for k in FORMS}
                    top = max(shares, key=shares.get)
                    first_forms[top if shares[top] > 0.5 else "other"] += 1
                    if r["n_exact"] < MIN_EXACT and any(s["n_fully_exact"] >= MIN_EXACT for s in st):
                        lost += 1
                anysh += any((s["shared"] or 0) > 0 for s in st)
            solved = [r for r in rs if r["n_exact"] >= MIN_EXACT]
            rare = sum(0 < r["n_exact"] < MIN_EXACT for r in rs)
            none = sum(r["n_exact"] == 0 for r in rs)
            tp = np.mean([r["stats"][-1]["train_perfect"] for r in rs])
            verdict = Counter()
            for r in solved:
                shares = {k: r["forms"].get(k, 0) / r["n_exact"] for k in FORMS}
                top = max(shares, key=shares.get)
                verdict[top if shares[top] > 0.9 else "mixed"] += 1
            med = f"{np.median(firsts):.0f}" if firsts else "–"
            out.append(f"| {L} | {xo} | {len(rs)} | {len(firsts)} | {med} | "
                       f"{first_forms['shared']} / {first_forms['partly']} / {first_forms['duplicated']} / "
                       f"{first_forms['other']} | {len(solved)} / {rare} / {none} | {verdict['shared']} / {verdict['partly']} / "
                       f"{verdict['duplicated']} / {verdict['mixed']} | {tp:.2f} | {anysh} | {lost} | "
                       f"{np.median([r['elapsed'] for r in rs]):.0f} |")
    return out + [""]


def plot_dose(runs, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    contexts = [("duplicated", 64), ("partly", 64), ("partly", 32)]
    colors = {"1/32": "#1baf7a", "1/10": "#2a78d6"}
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.4), dpi=150, sharey=True)
    for ax, (comp, L) in zip(axes, contexts):
        for start in ("1/32", "1/10"):
            xs, ys = [], []
            for xo in (0.0, 0.1, 0.3, 0.5, 0.7):
                rs = [r for r in runs if r["arm"] == "D" and r["cell"] == (comp, L, xo, start)]
                if rs:
                    xs.append(xo)
                    ys.append(sum(outcome(r) == "won" for r in rs) / len(rs))
            ax.plot(xs, ys, marker="o", ms=4, lw=2, color=colors[start], label=f"start {start}")
        ax.set_title(f"shared vs {comp}, L = {L}", fontsize=8, loc="left")
        ax.set_xlabel("crossover rate", fontsize=8)
        ax.set_ylim(-0.02, 1.02)
        ax.grid(axis="y", color="#e6e5e1", lw=0.6)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].set_ylabel("seeds where shared wins", fontsize=8)
    axes[0].legend(frameon=False, fontsize=7)
    fig.suptitle("§31 arm D: rare shared form wins vs crossover rate (0 and 0.7: §30 runs, same criterion; 30 seeds)",
                 fontsize=9, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_stage4(runs, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {0.7: "#eb6834", 0.3: "#eda100", 0.0: "#2a78d6"}
    fig, axes = plt.subplots(2, 3, figsize=(10, 5.4), dpi=150, sharex=True, sharey="row")
    for j, L in enumerate((32, 64, 128)):
        for xo in (0.7, 0.3, 0.0):
            rs = [r for r in runs if r["arm"] == "G" and r["cell"] == (L, xo)]
            if not rs:
                continue
            g = np.array([s["gen"] for s in rs[0]["stats"]])
            solved = np.array([[s["n_fully_exact"] > 0 for s in r["stats"]] for r in rs]).mean(axis=0)
            shared = np.array([[(s["shared"] or 0) > 0 for s in r["stats"]] for r in rs]).mean(axis=0)
            axes[0][j].plot(g, solved, color=colors[xo], lw=2, label=f"crossover {xo}")
            axes[1][j].plot(g, shared, color=colors[xo], lw=2, label=f"crossover {xo}")
        axes[0][j].set_title(f"L = {L}", fontsize=8, loc="left")
        axes[1][j].set_xlabel("generation", fontsize=8)
        for i in range(2):
            axes[i][j].grid(axis="y", color="#e6e5e1", lw=0.6)
            for sp in ("top", "right"):
                axes[i][j].spines[sp].set_visible(False)
    axes[0][0].set_ylabel("seeds with a fully exact\nindividual in the sample", fontsize=8)
    axes[1][0].set_ylabel("seeds with a shared\nindividual in the sample", fontsize=8)
    axes[0][0].legend(frameon=False, fontsize=7)
    fig.suptitle("§31 arm G: stage 4 from random starts (census of 256 every 20 generations; 50 seeds)",
                 fontsize=9, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--s30-roots", type=Path, nargs="*", default=[],
                    help="§30 arm A/B sweep roots: crossover 0 and 0.7 endpoints for arm D's cells")
    ap.add_argument("--figdir", type=Path, default=None)
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
    dose_cells = {(c, L, xo, s) for c, L in (("duplicated", 64), ("partly", 64), ("partly", 32))
                  for s in ("1/32", "1/10") for xo in (0.0, 0.7)}
    s30_dirs = []
    for root in args.s30_roots:
        for p in sorted(root.iterdir()) if root.exists() else []:
            if (p / "result.json").exists():
                cfg = yaml.safe_load((p / "config.yaml").read_text())
                if identify(cfg)["cell"] in dose_cells:
                    s30_dirs.append(str(p))
    with mp.get_context("spawn").Pool(args.workers) as pool:
        runs = pool.map(classify_run, dirs, chunksize=4)
        s30_runs = pool.map(classify_run, s30_dirs, chunksize=4)
    keys = Counter((r["arm"], r["cell"], r["cfg"]["seed"]) for r in runs)
    short = [r["dir"] for r in runs if r["stats"][-1]["gen"] != r["cfg"]["generations"]]
    by_cell = defaultdict(int)
    for (arm, cell, _), _n in keys.items():
        by_cell[(arm, cell)] += 1
    md = ["## Validation", "",
          f"- runs: {len(runs)}; duplicate run keys: {sum(v > 1 for v in keys.values())}; "
          f"stopped early: {len(short)}",
          f"- seeds per cell: " + ", ".join(f"{a} {c}: {n}" for (a, c), n in sorted(by_cell.items(), key=str))]
    for m in metas:
        md.append(f"- entry {m.get('id')}: status {m.get('status')}, exit {m.get('exit_code')}, "
                  f"commit {str(m.get('git_commit'))[:7]}, dirty {m.get('git_dirty')}, wall {m.get('wall_seconds')} s")
    md += ["", "## Readouts", "", f"Verdicts need ≥ {MIN_EXACT} fully exact non-elite individuals in the final "
           "population.", ""]
    md += seeded_table(runs, "D", "Arm D: crossover dose (shared from 1/32 and 1/10)",
                       [(c, L, xo, s) for c, L in (("duplicated", 64), ("partly", 64), ("partly", 32))
                        for s in ("1/32", "1/10") for xo in (0.1, 0.3, 0.5)])
    if s30_runs:
        md += seeded_table(s30_runs, "D", "§30 endpoints for arm D's cells (crossover 0 and 0.7), same criterion",
                           [(c, L, xo, s) for c, L in (("duplicated", 64), ("partly", 64), ("partly", 32))
                            for s in ("1/32", "1/10") for xo in (0.0, 0.7)])
    md += seeded_table(runs, "E", "Arm E: reciprocal (shared in the majority, crossover 0.7)",
                       [(c, L, 0.7, n) for c, L in (("duplicated", 64), ("partly", 64), ("partly", 128))
                        for n in (768, 922, 992)])
    # independence prediction from §30 (crossover off, 32 copies, L 64): per-copy failure q
    pred = {"duplicated": 11 / 30, "partly": 22 / 30}
    md += seeded_table(runs, "F", "Arm F: few shared copies, crossover off, L 64 (100 seeds)",
                       [(c, 64, 0.0, n) for c in ("duplicated", "partly") for n in (1, 8)])
    md += ["Independence prediction from §30 (32 copies lost in 11/30 vs duplicated, 22/30 vs partly; "
           "P(win from n) ≈ 1 − (lost fraction)^(n/32)): " +
           ", ".join(f"{c} n={n}: {100 * (1 - pred[c] ** (n / 32)):.0f}/100" for c in pred for n in (1, 8)), ""]
    md += stage4(runs)
    (args.out / "s31_report.md").write_text("\n".join(md) + "\n")
    slim = [{k: (list(v) if isinstance(v, tuple) else v) for k, v in r.items() if k not in ("cfg", "stats")}
            for r in runs]
    (args.out / "s31_runs.json").write_text(json.dumps(slim, indent=1, default=str))
    if args.figdir:
        args.figdir.mkdir(parents=True, exist_ok=True)
        if any(r["arm"] == "D" for r in runs):
            plot_dose(runs + s30_runs, args.figdir / "s31_dose.png")
        if any(r["arm"] == "G" for r in runs):
            plot_stage4(runs, args.figdir / "s31_stage4.png")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
