#!/usr/bin/env python3
"""Map-bias §29 stage 3 report: validate, analyse, inspect and plot the shared-helper queue.

    uv run python experiments/chem_tape/s29_report.py --roots DIR [DIR ...] --out DIR \
        [--stage2 PRESERVE_JSON] [--figdir docs/map-bias/figures]

Each root is a queue entry's $RUN_DIR (a sweep output root with metadata.json beside it,
when run by scripts/run_queue.py). Arms are recognised from each run's seed tapes.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import shared_helper as sh  # noqa: E402
from folding_evolution.chem_tape import tagged  # noqa: E402

EXPECTED = {"mixed": (64, 128), "shared": (32, 64, 128), "dup": (64, 128)}
SEEDS = list(range(30))
OP_NAMES = {0: "NOP", 1: "INPUT", 2: "C0", 3: "C1", 4: "CHARS", 5: "SUM", 6: "ANY", 7: "ADD", 8: "GT",
            9: "DUP", 10: "SWAP", 11: "RADD", 12: "NOP12", 13: "NOP13", 14: "MAP_EQ_E", 15: "C2",
            16: "C5", 17: "IF_GT", 18: "RMAX", 19: "THR", 20: "SEP", 21: "RECV"}
COLORS = {32: "#1baf7a", 64: "#2a78d6", 128: "#eb6834"}
FORM_COLORS = {"shared": "#2a78d6", "duplicated": "#eb6834"}


def arm_of(cfg: dict) -> str:
    L = cfg["tape_length"]
    hexes = [h for h in cfg["seed_tapes"].split(",") if h]
    names = {sh.form_genome(n, L).tobytes().hex(): n for n in sh.FORMS if sh.form_genome(n, L) is not None}
    forms = sorted(names.get(h, "?") for h in hexes)
    return {("duplicated", "shared"): "mixed", ("shared",): "shared", ("duplicated",): "dup"}.get(tuple(forms), "?")


def load(roots: list[Path]) -> tuple[list[dict], list[dict]]:
    runs, metas = [], []
    for root in roots:
        meta = root / "metadata.json"
        if meta.exists():
            metas.append({"root": str(root), **json.loads(meta.read_text())})
        for d in sorted(p for p in root.iterdir() if p.is_dir()):
            if not (d / "result.json").exists():
                continue
            cfg = yaml.safe_load((d / "config.yaml").read_text())
            res = json.loads((d / "result.json").read_text())
            runs.append({"dir": d, "arm": arm_of(cfg), "L": cfg["tape_length"], "seed": cfg["seed"],
                         "cfg": cfg, "res": res, "hash": d.name})
    return runs, metas


def validate(runs: list[dict], metas: list[dict]) -> tuple[list[str], dict]:
    lines, cover = [], {}
    keys = defaultdict(list)
    for r in runs:
        keys[(r["arm"], r["L"], r["seed"])].append(r["hash"])
    dups = {k: v for k, v in keys.items() if len(v) > 1}
    lines.append(f"- runs found: {len(runs)}; duplicate (arm, L, seed) keys: {len(dups)}")
    for arm, Ls in EXPECTED.items():
        for L in Ls:
            have = sorted(s for (a, l, s) in keys if a == arm and l == L)
            missing = [s for s in SEEDS if s not in have]
            short = [r["seed"] for r in runs if r["arm"] == arm and r["L"] == L
                     and r["res"]["generations_run"] != r["cfg"]["generations"]]
            cover[(arm, L)] = len(have)
            status = "complete" if not missing else "PARTIAL" if have else "MISSING"
            lines.append(f"- seed-{arm} L={L}: {len(have)}/30 seeds ({status})"
                         + (f", missing {missing}" if missing and have else "")
                         + (f", stopped early: {short}" if short else ""))
    unknown = [r["hash"] for r in runs if r["arm"] == "?"]
    if unknown:
        lines.append(f"- runs with unrecognised seed tapes: {unknown}")
    for m in metas:
        lines.append(f"- entry {m.get('id')}: status {m.get('status')}, exit {m.get('exit_code')}, "
                     f"commit {str(m.get('git_commit'))[:7]}, dirty {m.get('git_dirty')}, "
                     f"wall {m.get('wall_seconds')} s")
    return lines, cover


def series(r: dict, key: str) -> tuple[np.ndarray, np.ndarray]:
    st = r["res"]["shared_stats"]
    g = np.array([s["gen"] for s in st])
    v = np.array([np.nan if s[key] is None else s[key] for s in st], dtype=float)
    return g, v


def group(runs, arm, L):
    return sorted((r for r in runs if r["arm"] == arm and r["L"] == L), key=lambda r: r["seed"])


def fmt(x, d=2):
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def readouts(runs: list[dict]) -> tuple[list[str], dict]:
    out, data = [], {}
    # 1. seed-mixed
    out += ["### Readout 1: seed-mixed (shared share among fully exact individuals)", "",
            "| L | seeds | final shared share: mean (min–max) | > 90% shared | > 90% duplicated | in between | "
            "no fully exact at end | final fully exact (mean) |", "|---|---|---|---|---|---|---|---|"]
    for L in EXPECTED["mixed"]:
        rs = group(runs, "mixed", L)
        if not rs:
            out.append(f"| {L} | 0 | | | | | | |")
            continue
        fin = [r["res"]["shared_stats"][-1] for r in rs]
        sh_ = np.array([np.nan if f["shared"] is None else f["shared"] for f in fin])
        du_ = np.array([np.nan if f["duplicated"] is None else f["duplicated"] for f in fin])
        ok = ~np.isnan(sh_)
        hi_s, hi_d = int((sh_[ok] > 0.9).sum()), int((du_[ok] > 0.9).sum())
        out.append(f"| {L} | {len(rs)} | {fmt(np.nanmean(sh_))} ({fmt(np.nanmin(sh_))}–{fmt(np.nanmax(sh_))}) | "
                   f"{hi_s}/{ok.sum()} | {hi_d}/{ok.sum()} | {int(ok.sum()) - hi_s - hi_d}/{ok.sum()} | "
                   f"{int((~ok).sum())}/{len(rs)} | {fmt(np.mean([f['fully_exact'] for f in fin]))} |")
        data[("mixed", L)] = {"final_shared": sh_.tolist(), "final_dup": du_.tolist()}
    # 2. seed-shared
    out += ["", "### Readout 2: seed-shared (does the shared form persist?)", "",
            "| L | seeds | final fully exact (mean, min) | seeds with fully exact at every log point | "
            "final among fully exact: shared / partly / duplicated (means) | seeds ending < 50% shared |",
            "|---|---|---|---|---|---|"]
    for L in EXPECTED["shared"]:
        rs = group(runs, "shared", L)
        if not rs:
            out.append(f"| {L} | 0 | | | | |")
            continue
        fin = [r["res"]["shared_stats"][-1] for r in rs]
        fe = np.array([f["fully_exact"] for f in fin])
        always = sum(all(s["fully_exact"] > 0 for s in r["res"]["shared_stats"]) for r in rs)
        m = {k: np.nanmean([np.nan if f[k] is None else f[k] for f in fin]) for k in ("shared", "partly", "duplicated")}
        low = sum(1 for f in fin if f["shared"] is None or f["shared"] < 0.5)   # None = no fully exact
        out.append(f"| {L} | {len(rs)} | {fmt(fe.mean())}, {fmt(fe.min())} | {always}/{len(rs)} | "
                   f"{fmt(m['shared'])} / {fmt(m['partly'])} / {fmt(m['duplicated'])} | {low}/{len(rs)} |")
    # 3. seed-dup
    out += ["", "### Readout 3: seed-dup (does sharing arise from a duplicated start?)", "",
            "| L | seeds | seeds with any shared individual (any log point) | max shared share | "
            "seeds with any partly shared | final fully exact (mean) | no fully exact at end | "
            "final partly / duplicated share (mean over seeds with fully exact) |",
            "|---|---|---|---|---|---|---|---|"]
    for L in EXPECTED["dup"]:
        rs = group(runs, "dup", L)
        if not rs:
            out.append(f"| {L} | 0 | | | | | | |")
            continue
        anysh = sum(any((s["shared"] or 0) > 0 for s in r["res"]["shared_stats"]) for r in rs)
        mx = max(max((s["shared"] or 0) for s in r["res"]["shared_stats"]) for r in rs)
        anyp = sum(any((s["partly"] or 0) > 0 for s in r["res"]["shared_stats"]) for r in rs)
        fin = [r["res"]["shared_stats"][-1] for r in rs]
        none = sum(f["n_fully_exact"] == 0 for f in fin)
        pa = [f["partly"] for f in fin if f["partly"] is not None]
        du = [f["duplicated"] for f in fin if f["duplicated"] is not None]
        out.append(f"| {L} | {len(rs)} | {anysh}/{len(rs)} | {fmt(mx)} | {anyp}/{len(rs)} | "
                   f"{fmt(np.mean([f['fully_exact'] for f in fin]))} | {none}/{len(rs)} | "
                   f"{fmt(np.mean(pa)) if pa else '–'} / {fmt(np.mean(du)) if du else '–'} (n={len(pa)}) |")
    # 4. run census
    out += ["", "### Readout 4: run census (population means, generation 0 → final; reading from tags 0–2)", "",
            "| arm | L | runs | read | unread | helpers (read, not an output run) | with a helper |",
            "|---|---|---|---|---|---|---|"]
    for arm, Ls in EXPECTED.items():
        for L in Ls:
            rs = group(runs, arm, L)
            if not rs:
                continue

            def m(k, i):
                return np.mean([r["res"]["run_stats"][i][k] for r in rs])
            out.append(f"| seed-{arm} | {L} | {m('runs', 0):.2f} → {m('runs', -1):.2f} | "
                       f"{m('read', 0):.2f} → {m('read', -1):.2f} | {m('unread', 0):.2f} → {m('unread', -1):.2f} | "
                       f"{m('helpers', 0):.2f} → {m('helpers', -1):.2f} | "
                       f"{m('with_helper', 0):.2f} → {m('with_helper', -1):.2f} |")
    # other_output_helper, shown so a non-plan form is not hidden
    out += ["", "Fully exact individuals whose tag-1 or tag-2 output run feeds another output "
            "(other_output_helper; counted inside the three forms above), final generation, mean share:", ""]
    for arm, Ls in EXPECTED.items():
        for L in Ls:
            rs = group(runs, arm, L)
            if rs:
                v = [r["res"]["shared_stats"][-1]["other_output_helper"] for r in rs]
                out.append(f"- seed-{arm} L={L}: {fmt(np.nanmean([np.nan if x is None else x for x in v]), 3)}")
    return out, data


def decode(g: np.ndarray) -> str:
    parts = []
    for t, body in tagged.parse_runs(g):
        ops = [OP_NAMES[op] + (f"{tg}" if op == tagged.RECV else "") for op, tg in tagged._strip_trailing_nops(body)]
        parts.append(f"[{t}] " + " ".join(ops))
    return " | ".join(parts)


def inspect(runs: list[dict], per_arm: int = 5) -> list[str]:
    """Per arm: the form tally of every fully exact individual in each final population, and
    one decoded non-elite fully exact genome (random, fixed rng) from each of the first
    `per_arm` seeds. Slots 0..elite_count-1 hold the elites, which elitism freezes (often
    the original seed genome), so they are reported separately and never sampled."""
    out = ["### Final populations: form tallies and decoded genomes", "",
           "Tally = forms of all fully exact individuals in the final population (elites excluded); "
           "elites = forms of the elite slots.", ""]
    m = sh.machine()
    rng = np.random.default_rng(29)
    for arm, Ls in EXPECTED.items():
        for L in Ls:
            rs = group(runs, arm, L)
            out.append(f"**seed-{arm}, L={L}**")
            out.append("")
            for r in rs[:per_arm]:
                f = r["dir"] / "final_population.npz"
                if not f.exists():
                    out.append(f"- seed {r['seed']}: no final_population.npz")
                    continue
                pop = np.load(f)["genotypes"]
                ne = r["cfg"]["elite_count"]
                ex = sh.Exactness()
                idx = [i for i in range(ne, len(pop)) if ex(pop[i]).all()]
                elites = [sh.classify(pop[i], m)["form"] for i in range(ne)]
                if not idx:
                    out.append(f"- seed {r['seed']}: no fully exact non-elite individual; elites {elites}")
                    continue
                tally = defaultdict(int)
                for i in idx:
                    tally[sh.classify(pop[i], m)["form"]] += 1
                g = pop[int(rng.choice(idx))]
                c = sh.classify(g, m)
                cc = ",".join(f"{t}:{n}" for t, n in zip(c["tags"], c["consumer_counts"]))
                out.append(f"- seed {r['seed']}: {len(idx)}/{len(pop) - ne} fully exact, tally "
                           f"{dict(tally)}, elites {elites}. Sampled: **{c['form']}**"
                           f"{' +other-output-helper' if c['other_output_helper'] else ''}; "
                           f"consumers {cc}  \n  `{decode(g)}`")
            out.append("")
    return out


def plot_mixed(runs: list[dict], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=150)
    for L in EXPECTED["mixed"]:
        rs = group(runs, "mixed", L)
        if not rs:
            continue
        vals = []
        for r in rs:
            g, v = series(r, "shared")
            ax.plot(g, v, color=COLORS[L], lw=0.6, alpha=0.25)
            vals.append(v)
        mean = np.nanmean(np.array(vals), axis=0)
        ax.plot(g, mean, color=COLORS[L], lw=2, label=f"{L} cells (mean of {len(rs)} seeds)")
    ax.axhline(0.5, color="#8a8984", lw=0.8, ls=":")
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("generation")
    ax.set_ylabel("shared share of fully exact individuals")
    ax.set_title("Seed-mixed: shared share of fully exact individuals (sample of 256, every 20 generations;"
                 " thin: per seed)", fontsize=8.5, loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#e6e5e1", lw=0.6)
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_stage2(preserve: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = preserve["rows"]
    ops = [("mutation", None)] + [(v, p) for v in sh.VARIANTS for p in sh.PAIRINGS]
    labels = ["mutation"] + [f"{v}\n{ {'form_A': 'form=A', 'form_B': 'form=B', 'other': 'vs other'}[p]}"
                             for v, p in ops[1:]]
    fig, axes = plt.subplots(2, 1, figsize=(9, 5.6), dpi=150, sharey=True)
    for ax, L in zip(axes, (64, 128)):
        x = np.arange(len(ops))
        for j, form in enumerate(("shared", "duplicated")):
            ys = []
            for op, p in ops:
                r = [r for r in rows if r["form"] == form and r["L"] == L and r["op"] == op and r["pairing"] == p]
                ys.append(r[0]["fully_exact"] if r else np.nan)
            ax.bar(x + (j - 0.5) * 0.38, ys, width=0.36, color=FORM_COLORS[form], label=form,
                   edgecolor="white", linewidth=1)
        ax.set_xticks(x, labels, fontsize=7)
        ax.set_ylabel(f"L = {L}\nchildren fully exact", fontsize=8)
        ax.set_ylim(0, 1)
        ax.grid(axis="y", color="#e6e5e1", lw=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].legend(frameon=False, fontsize=8, ncol=2, loc="upper left")
    axes[0].set_title("Stage 2: fraction of children fully exact, 10,000 per bar (no selection)",
                      fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--stage2", type=Path, default=None)
    ap.add_argument("--figdir", type=Path, default=None)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    runs, metas = load([r for r in args.roots if r.exists()])
    val, _ = validate(runs, metas)
    ro, data = readouts(runs)
    ins = inspect(runs)
    md = ["## Validation", ""] + val + [""] + ["## Readouts", ""] + ro + [""] + ins
    (args.out / "s29_report.md").write_text("\n".join(md) + "\n")
    (args.out / "s29_report.json").write_text(json.dumps(
        {f"{k[0]}_{k[1]}": v for k, v in data.items()}, indent=2))
    if args.figdir:
        args.figdir.mkdir(parents=True, exist_ok=True)
        plot_mixed(runs, args.figdir / "s29_mixed_shared_fraction.png")
        if args.stage2:
            plot_stage2(json.loads(args.stage2.read_text()), args.figdir / "s29_stage2_survival.png")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
