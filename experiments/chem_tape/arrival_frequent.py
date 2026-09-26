"""Arrival of the frequent: does the genotype->behaviour bias predict what evolution finds?

Hobby probe (see README "Core question"). For every chem-tape decoder setup that
has past fixed-task runs on disk:

  1. Sample N uniform random tapes, decode + execute them on the task's seed-0
     training inputs, and count how often each behaviour (prediction vector)
     appears. That is the map's bias, before any selection.
  2. Re-evaluate every past run's best genotype on the same inputs and look up
     how common its behaviour was among random tapes.

Question: are solutions that random tapes hit often the ones evolution finds,
and are evolved dead-ends (proxy basins) simply the most frequent behaviour
at their fitness level?

Usage:
  uv run python experiments/chem_tape/arrival_frequent.py sample --n 50000000 --workers 10
  uv run python experiments/chem_tape/arrival_frequent.py analyze
Outputs go to $RUN_DIR (queue runner) or --out (default experiments/chem_tape/output/arrival_frequent).
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import time
from dataclasses import fields
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import yaml

DECODE_KEYS = ("task", "arm", "topk", "alphabet", "tape_length", "safe_pop_mode")
CHUNK = 200_000


def _default_out() -> Path:
    return Path(os.environ.get("RUN_DIR", "experiments/chem_tape/output/arrival_frequent"))


def collect_runs() -> dict[tuple, list[dict]]:
    """Past fixed-task, single-population, unseeded runs grouped by decode setup."""
    idx_paths = (
        glob.glob("experiments/chem_tape/output/*/sweep_index.json")
        + glob.glob("experiments/output/*/*/sweep_index.json")
        + glob.glob("experiments/output/*/*/*/sweep_index.json")
    )
    groups: dict[tuple, list[dict]] = collections.defaultdict(list)
    seen: set[str] = set()
    for idx in idx_paths:
        for r in json.loads(Path(idx).read_text()):
            run_dir = r["run_dir"]
            if run_dir in seen:
                continue
            try:
                c = yaml.safe_load(Path(run_dir, "config.yaml").read_text())
            except OSError:
                continue
            if c.get("task_alternating_period") and c.get("task_alternating_values"):
                continue
            if (c.get("k_alternating_period") or c.get("evolve_k") or c.get("plasticity_enabled")
                    or c.get("seed_tapes") or c.get("n_islands", 1) > 1):
                continue
            seen.add(run_dir)
            c.setdefault("safe_pop_mode", "preserve")
            key = tuple(c.get(k) for k in DECODE_KEYS)
            groups[key].append({
                "config": c,
                "seed": r["seed"],
                "best_fitness": r["best_fitness"],
                "genotype_hex": r["best_genotype_hex"],
                "pop_size": c.get("pop_size"),
                "generations": c.get("generations"),
            })
    return groups


def _make_cfg(c: dict):
    from folding_evolution.chem_tape.config import ChemTapeConfig
    names = {f.name for f in fields(ChemTapeConfig)}
    kw = {k: v for k, v in c.items() if k in names}
    kw.update(seed=0, backend="numpy")
    return ChemTapeConfig(**kw)


def _behaviour_keys(preds: np.ndarray) -> np.ndarray:
    rows = np.ascontiguousarray(preds.astype(np.int16))
    return rows.view(np.dtype((np.void, rows.shape[1] * 2))).ravel()


def sample_group(payload) -> dict:
    key, runs, n, out = payload
    from folding_evolution.chem_tape.evaluate import evaluate_population
    from folding_evolution.chem_tape.evolve import _token_max
    from folding_evolution.chem_tape.tasks import build_task

    cfg = _make_cfg(runs[0]["config"])
    task = build_task(cfg, 0)
    hi = _token_max(cfg) + 1
    rng = np.random.default_rng(12345)
    counts: collections.Counter = collections.Counter()
    fit_of: dict[bytes, float] = {}
    t0 = time.time()
    done = 0
    while done < n:
        m = min(CHUNK, n - done)
        tapes = rng.integers(0, hi, size=(m, cfg.tape_length), dtype=np.uint8)
        fits, preds = evaluate_population(list(tapes), task, cfg)
        keys = _behaviour_keys(preds)
        uniq, first, cnt = np.unique(keys, return_index=True, return_counts=True)
        for u, i, k in zip(uniq, first, cnt):
            b = u.tobytes()
            counts[b] += int(k)
            if b not in fit_of:
                fit_of[b] = float(fits[i])
        done += m

    # Evolved best genotypes, re-scored on the seed-0 inputs.
    geno = [np.frombuffer(bytes.fromhex(r["genotype_hex"]), dtype=np.uint8) for r in runs]
    efits, epreds = evaluate_population(geno, task, cfg)
    ekeys = _behaviour_keys(epreds)
    beh_list = sorted(counts, key=counts.get, reverse=True)
    evolved = []
    for r, ef, ek in zip(runs, efits, ekeys):
        b = ek.tobytes()
        at_or_above = [x for x in beh_list if fit_of[x] >= ef - 1e-9]
        rank = at_or_above.index(b) + 1 if b in counts else None
        evolved.append({
            "seed": r["seed"], "pop_size": r["pop_size"], "generations": r["generations"],
            "best_fitness": r["best_fitness"], "fitness_seed0": float(ef),
            "freq": counts.get(b, 0) / n, "rank_at_or_above_fitness": rank,
            "n_behaviours_at_or_above": len(at_or_above),
        })

    solve_count = sum(c for b, c in counts.items() if fit_of[b] >= 0.999)
    name = "__".join(str(k) for k in key)
    freq = np.array([counts[b] for b in beh_list], dtype=np.int64)
    fit = np.array([fit_of[b] for b in beh_list])
    np.savez_compressed(Path(out, "groups", name + ".npz"), counts=freq, fitness=fit)
    res = {
        "key": dict(zip(DECODE_KEYS, key)), "name": name, "n_samples": n,
        "n_behaviours": len(counts), "top1_share": float(freq[0] / n),
        "p_solve": solve_count / n,
        "p_fit_ge": {t: float(freq[fit >= t].sum() / n) for t in (0.75, 0.9, 0.95)},
        "top_behaviours": [{"share": float(c / n), "fitness": float(f)}
                           for c, f in zip(freq[:15], fit[:15])],
        "evolved": evolved, "seconds": time.time() - t0,
    }
    Path(out, "groups", name + ".json").write_text(json.dumps(res, indent=1))
    with open(Path(out, "progress.jsonl"), "a") as fh:
        fh.write(json.dumps({"group": name, "p_solve": res["p_solve"],
                             "n_behaviours": res["n_behaviours"], "seconds": round(res["seconds"])}) + "\n")
    return res


def cmd_sample(args) -> None:
    out = Path(args.out)
    (out / "groups").mkdir(parents=True, exist_ok=True)
    groups = collect_runs()
    done = {p.stem for p in (out / "groups").glob("*.json")}
    todo = [(k, v, args.n, str(out)) for k, v in groups.items()
            if "__".join(str(x) for x in k) not in done]
    # Slow decoders first so the tail of the run is the fast Arm A groups.
    todo.sort(key=lambda p: p[0][1] == "A")
    print(f"{len(groups)} decode groups, {sum(len(v) for v in groups.values())} runs, "
          f"{len(todo)} to sample at n={args.n:,}", flush=True)
    os.environ["RAYON_NUM_THREADS"] = "1"
    with Pool(args.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(sample_group, todo), 1):
            print(f"[{i}/{len(todo)}] {r['name']}: p_solve={r['p_solve']:.2e} "
                  f"behaviours={r['n_behaviours']} ({r['seconds']:.0f}s)", flush=True)
    (out / "DONE").write_text("ok\n")


def cmd_analyze(args) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.stats import spearmanr

    out = Path(args.out)
    res = [json.loads(p.read_text()) for p in sorted((out / "groups").glob("*.json"))]
    lines = ["# Arrival of the frequent — results", ""]

    # 1. Does random-tape solve frequency predict evolved solve rate? One point per
    #    (decode setup, budget).
    pts = []
    for r in res:
        by_budget = collections.defaultdict(list)
        for e in r["evolved"]:
            by_budget[(e["pop_size"], e["generations"])].append(e["best_fitness"] >= 0.999)
        for (pop, gens), solved in by_budget.items():
            if len(solved) < 10:
                continue
            floor = 0.5 / r["n_samples"]
            pts.append({"name": r["name"], "arm": r["key"]["arm"], "pop": pop, "gens": gens,
                        "n": len(solved), "solve_rate": float(np.mean(solved)),
                        "p_solve": r["p_solve"], "log_p": float(np.log10(max(r["p_solve"], floor))),
                        "unseen": r["p_solve"] == 0})
    rho, p = spearmanr([q["log_p"] for q in pts], [q["solve_rate"] for q in pts])
    lines += [f"## 1. Random-tape solve frequency vs evolved solve rate",
              f"{len(pts)} (setup, budget) points. Spearman rho = {rho:.2f} (p = {p:.1e}).", "",
              "| setup | pop×gens | runs | evolved solve rate | P(random tape solves) |",
              "|---|---|---|---|---|"]
    for q in sorted(pts, key=lambda q: q["log_p"]):
        ps = "unseen" if q["unseen"] else f"{q['p_solve']:.1e}"
        lines.append(f"| {q['name']} | {q['pop']}×{q['gens']} | {q['n']} | {q['solve_rate']:.2f} | {ps} |")

    fig, ax = plt.subplots(figsize=(7, 5))
    for arm, color in (("A", "tab:orange"), ("BP_TOPK", "tab:blue"), ("B", "tab:green"), ("BP", "tab:purple")):
        sel = [q for q in pts if q["arm"] == arm]
        if sel:
            ax.scatter([q["log_p"] for q in sel], [q["solve_rate"] for q in sel],
                       c=color, label=arm, alpha=0.75,
                       marker="o", edgecolors=["k" if q["unseen"] else "none" for q in sel])
    ax.set_xlabel("log10 P(random tape solves the task)   (outlined = never seen, plotted at floor)")
    ax.set_ylabel("evolved solve rate")
    ax.set_title(f"Arrival of the frequent: rho = {rho:.2f}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "solve_rate_vs_frequency.png", dpi=130)

    # 1b. Same task, different decoder: fairer than 1, since task difficulty cancels.
    by_task = collections.defaultdict(list)
    for q in pts:
        if q["pop"] == 1024 and q["gens"] == 1500:
            by_task[q["name"].split("__")[0]].append(q)
    agree = total = 0
    lines += ["", "## 1b. Same task, different decoder (pop 1024 × 1500 gens)", "",
              "| task | decoder with more random solvers | its solve rate | other decoder | its solve rate |",
              "|---|---|---|---|---|"]
    for task, qs in sorted(by_task.items()):
        for i, a in enumerate(qs):
            for b in qs[i + 1:]:
                if a["log_p"] == b["log_p"] or a["solve_rate"] == b["solve_rate"]:
                    continue
                hi, lo = (a, b) if a["log_p"] > b["log_p"] else (b, a)
                total += 1
                agree += hi["solve_rate"] > lo["solve_rate"]
                short = lambda q: "__".join(q["name"].split("__")[1:])
                lines.append(f"| {task} | {short(hi)} | {hi['solve_rate']:.2f} | {short(lo)} | {lo['solve_rate']:.2f} |")
    lines += ["", f"Frequency ordering predicts solve-rate ordering in {agree}/{total} decoder pairs."]

    # 2. Are evolved outcomes the most frequent behaviour at their fitness level?
    #    Only runs with >= 2 sampled alternatives at that fitness say anything; the
    #    baseline is the rank-1 rate if evolution picked uniformly among them.
    ev = [e for r in res for e in r["evolved"]]
    ranks = [e["rank_at_or_above_fitness"] for e in ev]
    contested = [e for e in ev if e["rank_at_or_above_fitness"] is not None and e["n_behaviours_at_or_above"] >= 2]
    rank1 = sum(e["rank_at_or_above_fitness"] == 1 for e in contested)
    uniform = sum(1 / e["n_behaviours_at_or_above"] for e in contested)
    lines += ["", "## 2. Where evolved best behaviours sit in the random-tape ranking",
              f"{len(ranks)} evolved runs. Behaviour never seen among random tapes: {ranks.count(None)}. "
              f"Runs with >= 2 sampled behaviours at or above their fitness: {len(contested)}. "
              f"Of those, the evolved behaviour is the most frequent one in {rank1} "
              f"(uniform-choice baseline: {uniform:.0f}).", "",
              "| setup | runs | unseen | rank 1 | median rank | median freq of evolved behaviour |",
              "|---|---|---|---|---|---|"]
    for r in res:
        rk = [e["rank_at_or_above_fitness"] for e in r["evolved"]]
        s = [x for x in rk if x is not None]
        fq = [e["freq"] for e in r["evolved"]]
        lines.append(f"| {r['name']} | {len(rk)} | {rk.count(None)} | {sum(x == 1 for x in s)} | "
                     f"{np.median(s) if s else '-'} | {np.median(fq):.1e} |")

    # 3. How biased is each map? Rank-frequency curves.
    fig, ax = plt.subplots(figsize=(7, 5))
    for r in res:
        d = np.load(out / "groups" / (r["name"] + ".npz"))
        c = d["counts"] / r["n_samples"]
        ax.loglog(np.arange(1, len(c) + 1), c, alpha=0.5,
                  color="tab:orange" if r["key"]["arm"] == "A" else "tab:blue", lw=1)
    ax.set_xlabel("behaviour rank")
    ax.set_ylabel("share of random tapes")
    ax.set_title("Rank-frequency of behaviours (orange = Arm A direct, blue = chem decoders)")
    fig.tight_layout()
    fig.savefig(out / "rank_frequency.png", dpi=130)
    lines += ["", "## 3. Bias of each map", "",
              "| setup | distinct behaviours | top-1 share | P(fit>=0.9) | P(solve) |", "|---|---|---|---|---|"]
    for r in res:
        lines.append(f"| {r['name']} | {r['n_behaviours']} | {r['top1_share']:.2f} | "
                     f"{r['p_fit_ge']['0.9']:.1e} | {r['p_solve']:.1e} |")

    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--n", type=int, default=50_000_000)
    s.add_argument("--workers", type=int, default=10)
    s.add_argument("--out", default=str(_default_out()))
    a = sub.add_parser("analyze")
    a.add_argument("--out", default=str(_default_out()))
    args = ap.parse_args()
    cmd_sample(args) if args.cmd == "sample" else cmd_analyze(args)


if __name__ == "__main__":
    main()
