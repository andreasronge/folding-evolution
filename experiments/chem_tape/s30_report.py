#!/usr/bin/env python3
"""Map-bias §30 report (Plans/establishment-s30.md): establishment of a rare shared form.

    uv run python experiments/chem_tape/s30_report.py --roots DIR [DIR ...] --out DIR [--figdir DIR]

Each root is a sweep output root (a queue entry's $RUN_DIR). Runs are recognised from
their seed tapes: the shared form plus k-1 copies of a competitor (arms A, B), or a single
duplicated form with random latent tags (arm C). Runs whose final census has no fully
exact individual are reported as such and never counted as any form.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import shared_helper as sh  # noqa: E402

SEEDS = list(range(30))
SHARE_COLORS = {Fraction(1, 32): "#1baf7a", Fraction(1, 10): "#2a78d6", Fraction(1, 4): "#eda100",
                Fraction(1, 2): "#eb6834"}


def identify(cfg: dict) -> dict:
    L = cfg["tape_length"]
    hexes = [h for h in cfg["seed_tapes"].split(",") if h]
    known = {}
    for latent in ("zero", "random"):
        for n in sh.FORMS:
            g = sh.form_genome(n, L, latent)
            if g is not None:
                known[g.tobytes().hex()] = (n, latent)
    forms = [known.get(h, ("?", "?")) for h in hexes]
    names = [f[0] for f in forms]
    if len(hexes) == 1 and forms[0] == ("duplicated", "random"):
        return {"arm": "C", "competitor": "duplicated", "share": None}
    if names.count("shared") == 1 and len(set(names) - {"shared"}) == 1 and all(f[1] == "zero" for f in forms):
        comp = (set(names) - {"shared"}).pop()
        return {"arm": "A" if comp == "duplicated" else "B", "competitor": comp,
                "share": Fraction(1, len(hexes))}
    return {"arm": "?", "competitor": "?", "share": None}


def load(roots: list[Path]) -> tuple[list[dict], list[dict]]:
    runs, metas = [], []
    for root in roots:
        if (root / "metadata.json").exists():
            metas.append(json.loads((root / "metadata.json").read_text()))
        for d in sorted(p for p in root.iterdir() if p.is_dir()):
            if not (d / "result.json").exists():
                continue
            cfg = yaml.safe_load((d / "config.yaml").read_text())
            res = json.loads((d / "result.json").read_text())
            runs.append({"dir": d, "cfg": cfg, "res": res, "L": cfg["tape_length"], "seed": cfg["seed"],
                         "xo": cfg["crossover_rate"], **identify(cfg)})
    return runs, metas


EXPECTED = ([("A", s, xo, L) for s in (Fraction(1, 32), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
             for xo in (0.7, 0.0) for L in (64, 128)]
            + [("B", s, xo, L) for s in (Fraction(1, 32), Fraction(1, 10), Fraction(1, 2))
               for xo in (0.7, 0.0) for L in (32, 64, 128)]
            + [("C", None, 0.7, L) for L in (64, 128)])


def cell(runs, arm, share, xo, L):
    return sorted((r for r in runs if r["arm"] == arm and r["share"] == share and r["xo"] == xo
                   and r["L"] == L), key=lambda r: r["seed"])


def validate(runs, metas) -> list[str]:
    out = [f"- runs found: {len(runs)}; unrecognised: {sum(r['arm'] == '?' for r in runs)}"]
    keys = defaultdict(int)
    for r in runs:
        keys[(r["arm"], r["share"], r["xo"], r["L"], r["seed"])] += 1
    out.append(f"- duplicate run keys: {sum(v > 1 for v in keys.values())}")
    partial = []
    for arm, s, xo, L in EXPECTED:
        rs = cell(runs, arm, s, xo, L)
        have = {r["seed"] for r in rs}
        short = [r["seed"] for r in rs if r["res"]["generations_run"] != r["cfg"]["generations"]]
        if len(have) != len(SEEDS) or short:
            partial.append(f"{arm} {s} xo={xo} L={L}: {len(have)}/30 seeds"
                           + (f", stopped early {short}" if short else ""))
    out.append(f"- cells: {len(EXPECTED)}; PARTIAL or missing: {len(partial)}")
    out += [f"  - PARTIAL {p}" for p in partial]
    for m in metas:
        out.append(f"- entry {m.get('id')}: status {m.get('status')}, exit {m.get('exit_code')}, "
                   f"commit {str(m.get('git_commit'))[:7]}, dirty {m.get('git_dirty')}, wall {m.get('wall_seconds')} s")
    return out


def summarise(rs: list[dict]) -> dict:
    fin = [r["res"]["shared_stats"][-1] for r in rs]
    none = [f["n_fully_exact"] == 0 for f in fin]
    sh_ = [f["shared"] for f in fin if f["n_fully_exact"] > 0]
    gone_gen = []
    for r in rs:
        st = r["res"]["shared_stats"]
        z = next((s["gen"] for s in st[1:] if s["n_fully_exact"] > 0 and s["shared"] == 0), None)
        if z is not None:
            gone_gen.append(z)
    return {"n": len(rs), "none": int(sum(none)), "with": len(sh_),
            "win": int(sum(v > 0.9 for v in sh_)), "gone": int(sum(v == 0 for v in sh_)),
            "between": int(sum(0 < v <= 0.9 for v in sh_)),
            "mean_shared": float(np.mean(sh_)) if sh_ else None,
            "median_gone_gen": float(np.median(gone_gen)) if gone_gen else None,
            "partly": float(np.mean([f["partly"] for f in fin if f["n_fully_exact"] > 0])) if sh_ else None,
            "duplicated": float(np.mean([f["duplicated"] for f in fin if f["n_fully_exact"] > 0])) if sh_ else None}


def fmt(x, d=2):
    return "–" if x is None else f"{x:.{d}f}"


def readouts(runs) -> tuple[list[str], dict]:
    out, data = [], {}
    for arm, comp in (("A", "duplicated"), ("B", "partly shared")):
        out += [f"### Arm {arm}: shared vs {comp} (300 generations)", "",
                "| L | crossover | start share | seeds | > 90% shared at end | shared gone at end | in between | "
                "no fully exact at end | mean final shared share | final partly / duplicated (mean) | "
                "median generation shared first hits 0 |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
        for (a, s, xo, L) in EXPECTED:
            if a != arm:
                continue
            rs = cell(runs, a, s, xo, L)
            if not rs:
                out.append(f"| {L} | {xo} | {s} | 0 | | | | | | | |")
                continue
            m = summarise(rs)
            data[f"{a}_{s}_{xo}_{L}"] = m
            w = m["with"]
            out.append(f"| {L} | {xo} | {s} | {m['n']} | {m['win']}/{w} | {m['gone']}/{w} | {m['between']}/{w} | "
                       f"{m['none']}/{m['n']} | {fmt(m['mean_shared'])} | {fmt(m['partly'])} / {fmt(m['duplicated'])} | "
                       f"{fmt(m['median_gone_gen'], 0)} |")
        out.append("")
        out += [f"Lowest start share from which shared ends > 90% in a majority of all seeds (arm {arm}):", ""]
        Ls = sorted({L for (a, _, _, L) in EXPECTED if a == arm})
        for xo in (0.7, 0.0):
            for L in Ls:
                shares = sorted({s for (a, s, x, l) in EXPECTED if a == arm and x == xo and l == L})
                # majority of all seeds: a seed with no fully exact individual counts as not won
                ok = [s for s in shares if (m := data.get(f"{arm}_{s}_{xo}_{L}")) and m["win"] > m["n"] / 2]
                out.append(f"- crossover {xo}, L={L}: {min(ok) if ok else 'none of ' + ', '.join(map(str, shares))}")
        out.append("")
    out += ["### Arm C: seed-dup with random latent tags (1000 generations, crossover 0.7)", "",
            "| L | seeds | partly > 50% at some log point | median generation partly first > 50% | "
            "any shared individual | no fully exact at end | final partly / duplicated (mean) |",
            "|---|---|---|---|---|---|---|"]
    for L in (64, 128):
        rs = cell(runs, "C", None, 0.7, L)
        if not rs:
            out.append(f"| {L} | 0 | | | | | |")
            continue
        cross = [next((s["gen"] for s in r["res"]["shared_stats"] if (s["partly"] or 0) > 0.5), None) for r in rs]
        c = [x for x in cross if x is not None]
        anysh = sum(any((s["shared"] or 0) > 0 for s in r["res"]["shared_stats"]) for r in rs)
        m = summarise(rs)
        data[f"C_{L}"] = {**m, "crossed": len(c), "median_cross": float(np.median(c)) if c else None}
        out.append(f"| {L} | {len(rs)} | {len(c)}/{len(rs)} | {fmt(float(np.median(c)) if c else None, 0)} | "
                   f"{anysh}/{len(rs)} | {m['none']}/{len(rs)} | {fmt(m['partly'])} / {fmt(m['duplicated'])} |")
    return out, data


def plot(runs, arm, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    Ls = sorted({L for (a, _, _, L) in EXPECTED if a == arm})
    shares = sorted({s for (a, s, _, _) in EXPECTED if a == arm})
    fig, axes = plt.subplots(2, len(Ls), figsize=(3.6 * len(Ls), 5.4), dpi=150, sharex=True, sharey=True,
                             squeeze=False)
    for i, xo in enumerate((0.7, 0.0)):
        for j, L in enumerate(Ls):
            ax = axes[i][j]
            for s in shares:
                rs = cell(runs, arm, s, xo, L)
                if not rs:
                    continue
                vals = []
                for r in rs:
                    st = r["res"]["shared_stats"]
                    g = np.array([x["gen"] for x in st])
                    v = np.array([np.nan if x["shared"] is None else x["shared"] for x in st])
                    ax.plot(g, v, color=SHARE_COLORS[s], lw=0.5, alpha=0.2)
                    vals.append(v)
                ax.plot(g, np.nanmean(np.array(vals), axis=0), color=SHARE_COLORS[s], lw=2,
                        label=f"start {s}")
            ax.set_title(f"L = {L}, crossover {xo}", fontsize=8, loc="left")
            ax.set_ylim(-0.02, 1.02)
            ax.grid(axis="y", color="#e6e5e1", lw=0.6)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            if j == 0:
                ax.set_ylabel("shared share of\nfully exact", fontsize=8)
            if i == 1:
                ax.set_xlabel("generation", fontsize=8)
    comp = "duplicated" if arm == "A" else "partly shared"
    axes[0][0].legend(frameon=False, fontsize=7, loc="center right")
    fig.suptitle(f"§30 arm {arm}: shared vs {comp} from a small start share (thin: per seed, bold: mean)",
                 fontsize=9, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--figdir", type=Path, default=None)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    runs, metas = load([r for r in args.roots if r.exists()])
    ro, data = readouts(runs)
    md = ["## Validation", ""] + validate(runs, metas) + ["", "## Readouts", ""] + ro
    (args.out / "s30_report.md").write_text("\n".join(md) + "\n")
    (args.out / "s30_report.json").write_text(json.dumps(data, indent=2, default=str))
    if args.figdir:
        args.figdir.mkdir(parents=True, exist_ok=True)
        plot(runs, "A", args.figdir / "s30_establishment_dup.png")
        plot(runs, "B", args.figdir / "s30_establishment_partly.png")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
