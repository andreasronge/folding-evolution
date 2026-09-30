"""Map-bias pivot: arrival of the frequent on the folding map vs direct encoding.

Plan: Plans/map-bias-pivot.md. Both maps use the same 62-char alphabet, operators and
evaluator (direct.py); only genotype -> program differs. A behaviour is a program's
output vector (repr) on the 8 discriminating contexts of exp_task_verification_strict.

  sample   Phase A: behaviour (and program-source) frequencies of uniform random
           genotypes, per map and genotype length. No evolution.
  evolve   Phase B: evolution per (task, map, budget, seed); records the endpoint
           behaviour, first generation any individual is exact, and final-population
           behaviours.
  analyze  Tables for both phases (reads the sample and evolve outputs).

Usage (outputs under --out, default $RUN_DIR):
  uv run python experiments/map_bias/fold_direct.py sample --n 20000000 --lengths 30,50,80
  uv run python experiments/map_bias/fold_direct.py evolve --seeds 50 --budgets 200x1000,500x2000
  uv run python experiments/map_bias/fold_direct.py analyze --sample DIR --evolve DIR
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import os
import random
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from exp_task_verification_strict import CANDIDATE_TASKS, make_discriminating_contexts  # noqa: E402
from folding_evolution.alphabet import random_genotype  # noqa: E402
from folding_evolution.direct import develop_direct  # noqa: E402
from folding_evolution.dynamics import partial_credit  # noqa: E402
from folding_evolution.operators import crossover, mutate  # noqa: E402
from folding_evolution.phenotype import develop_batch  # noqa: E402

CONTEXTS = make_discriminating_contexts()
TASKS = {name: fn for name, _, fn, _ in CANDIDATE_TASKS}
TASKS["count(expenses)"] = lambda ctx: len(ctx["expenses"])
EXPECTED = {name: [fn(c) for c in CONTEXTS] for name, fn in TASKS.items()}
MAPS = ("fold", "direct")
CHUNK = 20_000
SOURCE_SAMPLE = 500_000         # program-source counts use the first 500k genotypes only
MAX_LEN = 200                   # evolved genotypes are cut to this length (bloat guard)


def _out(args) -> Path:
    return Path(args.out or os.environ.get("RUN_DIR", "experiments/map_bias/output"))


def develop_many(genotypes: list[str], m: str):
    if m == "fold":
        return develop_batch(genotypes)
    return [develop_direct.__wrapped__(g) for g in genotypes]


def outputs(program) -> list:
    return [program.evaluate(c) for c in CONTEXTS]


_ADDR = re.compile(r" at 0x[0-9a-f]+")


def canon(o) -> str:
    """Process-independent repr: functions (direct encoding can return closures) become
    '<fn>', containers are canonicalised recursively, stray addresses are stripped."""
    if callable(o):
        return "<fn>"
    if isinstance(o, list):
        return "[" + ", ".join(canon(x) for x in o) + "]"
    if isinstance(o, tuple):
        return "(" + ", ".join(canon(x) for x in o) + ")"
    if isinstance(o, dict):
        return "{" + ", ".join(f"{canon(k)}: {canon(v)}" for k, v in sorted(o.items(), key=lambda kv: repr(kv[0]))) + "}"
    return _ADDR.sub("", repr(o))


def behaviour(outs: list) -> str:
    return "|".join(canon(o) for o in outs)


def fitness(outs: list, task: str) -> float:
    """dynamics.evaluate_multi_target on one target: mean partial credit over the
    contexts, 0 if the output is identical on every context (data-dependence gate)."""
    if len({canon(o) for o in outs}) <= 1:
        return 0.0
    return sum(partial_credit(o, e) for o, e in zip(outs, EXPECTED[task])) / len(CONTEXTS)


def exact(outs: list, task: str) -> bool:
    return all(o == e and type(o) is type(e) for o, e in zip(outs, EXPECTED[task]))


# ---------------- Phase A ----------------

def _sample_chunk(payload):
    m, L, seed, n = payload
    rng = random.Random(seed)
    gs = [random_genotype(L, rng) for _ in range(n)]
    counts: collections.Counter = collections.Counter()
    example: dict[str, str] = {}
    sources: collections.Counter = collections.Counter()
    for g, p in zip(gs, develop_many(gs, m)):
        b = behaviour(outputs(p))
        counts[b] += 1
        example.setdefault(b, g)
        if seed < SOURCE_SAMPLE // CHUNK:
            sources[p.source] += 1
    return m, L, counts, example, sources


def cmd_sample(args) -> None:
    out = _out(args)
    out.mkdir(parents=True, exist_ok=True)
    lengths = [int(x) for x in args.lengths.split(",")]
    jobs = [(m, L, s, CHUNK) for m in MAPS for L in lengths for s in range(args.n // CHUNK)]
    agg = {(m, L): [collections.Counter(), {}, collections.Counter()] for m in MAPS for L in lengths}
    t0 = time.time()
    os.environ["RAYON_NUM_THREADS"] = "1"
    with Pool(args.workers) as pool:
        for i, (m, L, c, ex, src) in enumerate(pool.imap_unordered(_sample_chunk, jobs, chunksize=4), 1):
            a = agg[(m, L)]
            a[0].update(c)
            for k, g in ex.items():
                a[1].setdefault(k, g)
            a[2].update(src)
            if i % 500 == 0:
                print(f"{i}/{len(jobs)} chunks, {time.time() - t0:.0f}s", flush=True)
    for (m, L), (c, ex, src) in agg.items():
        n = sum(c.values())
        rows = [{"behaviour": b, "count": k, "example": ex[b]} for b, k in c.most_common()]
        (out / f"sample_{m}_L{L}.json").write_text(json.dumps(
            {"map": m, "length": L, "n": n, "n_source_sample": sum(src.values()),
             "behaviours": rows, "sources_top": src.most_common(200), "n_sources": len(src)}))
        print(f"{m} L{L}: {n:,} genotypes, {len(c):,} behaviours, {len(src):,} sources in the first "
              f"{sum(src.values()):,}", flush=True)
    (out / "SAMPLE_DONE").write_text("ok\n")


# ---------------- Phase B ----------------

def _evolve_one(payload) -> dict:
    """search "evolve": the exp_2x2.run_stable loop. search "random": the same budget of
    fresh random genotypes at L0 each generation, keeping the best pop_size (a baseline
    for how far each map's own bias alone carries the endpoint)."""
    task, m, pop_size, gens, L0, seed, search = payload
    rng = random.Random(f"{task}|{pop_size}|{gens}|{seed}")    # same start for both maps
    pop = [random_genotype(L0, rng) for _ in range(pop_size)]

    def score(gs):
        res = []
        for g, p in zip(gs, develop_many(gs, m)):
            o = outputs(p)
            res.append((fitness(o, task), exact(o, task), behaviour(o)))
        return res

    sc = score(pop)
    first_exact = 0 if any(e for _, e, _ in sc) else None
    g0 = max(range(pop_size), key=lambda i: (sc[i][0], sc[i][1]))
    gen0 = {"gen0_fitness": sc[g0][0], "gen0_behaviour": sc[g0][2]}
    tsize = 3
    for gen in range(1, gens + 1):
        def pick():
            best = max(rng.sample(range(pop_size), tsize), key=lambda i: sc[i][0])
            return pop[best]
        kids = []
        for _ in range(pop_size):
            if search == "random":
                kids.append(random_genotype(L0, rng))
            elif rng.random() < 0.7:
                child = crossover(pick(), pick(), rng)
            else:
                child = mutate(pick(), rng)
            if search != "random":
                kids.append(child[:MAX_LEN])
        ksc = score(kids)
        if first_exact is None and any(e for _, e, _ in ksc):
            first_exact = gen
        # (mu + lambda) truncation, as exp_2x2.run_stable: parents first on ties.
        allg, alls = pop + kids, sc + ksc
        order = sorted(range(2 * pop_size), key=lambda i: -alls[i][0])[:pop_size]
        pop, sc = [allg[i] for i in order], [alls[i] for i in order]
    best = max(range(pop_size), key=lambda i: (sc[i][0], sc[i][1]))
    final_beh = collections.Counter(b for _, _, b in sc)
    return {"task": task, "map": m, "pop": pop_size, "gens": gens, "L0": L0, "seed": seed,
            "search": search, **gen0, "best_len": len(pop[best]),
            "best_fitness": sc[best][0], "best_exact": sc[best][1], "best_behaviour": sc[best][2],
            "best_genotype": pop[best], "first_exact_gen": first_exact,
            "final_exact_members": sum(e for _, e, _ in sc),
            "final_behaviours": final_beh.most_common(20), "mean_len": sum(map(len, pop)) / pop_size}


def cmd_evolve(args) -> None:
    out = _out(args)
    out.mkdir(parents=True, exist_ok=True)
    budgets = [tuple(int(x) for x in b.split("x")) for b in args.budgets.split(",")]
    tasks = args.tasks.split(";") if args.tasks else list(TASKS)
    done = set()
    res_path = out / "evolve.jsonl"
    if res_path.exists():
        for line in res_path.read_text().splitlines():
            r = json.loads(line)
            done.add((r["task"], r["map"], r["pop"], r["gens"], r["L0"], r["seed"], r["search"]))
    rbudgets = [tuple(int(x) for x in b.split("x")) for b in args.random_budgets.split(",") if b]
    jobs = [(t, m, p, g, args.length, s, mode)
            for mode, bs in (("evolve", budgets), ("random", rbudgets)) for (p, g) in bs
            for t in tasks for s in range(args.seeds) for m in MAPS
            if (t, m, p, g, args.length, s, mode) not in done]
    jobs.sort(key=lambda j: -j[2] * j[3])                      # long jobs first
    print(f"{len(jobs)} runs to do ({len(done)} already done)", flush=True)
    t0 = time.time()
    os.environ["RAYON_NUM_THREADS"] = "1"
    with Pool(args.workers) as pool, open(res_path, "a") as fh:
        for i, r in enumerate(pool.imap_unordered(_evolve_one, jobs), 1):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            if i % 50 == 0:
                print(f"{i}/{len(jobs)} runs, {time.time() - t0:.0f}s", flush=True)
    (out / "EVOLVE_DONE").write_text("ok\n")


# ---------------- analysis ----------------

def _spearman(x, y) -> float:
    from scipy.stats import spearmanr
    return float(spearmanr(x, y)[0])


def cmd_analyze(args) -> None:
    import numpy as np

    sd = Path(args.sample)
    samples = {}
    for p in sorted(sd.glob("sample_*_L*.json")):
        d = json.loads(p.read_text())
        samples[(d["map"], d["length"])] = d
    lengths = sorted({L for _, L in samples})
    lines = ["# Map-bias pivot: folding vs direct encoding", ""]

    # Fitness and exactness of every sampled behaviour, from its example genotype.
    beh_outs: dict[str, list] = {}
    for (m, L), d in samples.items():
        for r in d["behaviours"]:
            if r["behaviour"] not in beh_outs:
                beh_outs[r["behaviour"]] = outputs(develop_many([r["example"]], m)[0])

    def freq(m, L):
        d = samples[(m, L)]
        return {r["behaviour"]: r["count"] / d["n"] for r in d["behaviours"]}, d["n"]

    lines += ["## Phase A: behaviour bias of random genotypes", "",
              "| length | map | n | distinct behaviours | top-1 share (behaviour) | no output (None) | "
              "constant output | distinct sources (first 500k) |", "|---|---|---|---|---|---|---|---|"]
    for L in lengths:
        for m in MAPS:
            f, n = freq(m, L)
            top = max(f, key=f.get)
            const = sum(v for b, v in f.items() if len(set(b.split("|"))) == 1)
            lines.append(f"| {L} | {m} | {n:,} | {len(f):,} | {f[top]:.3f} `{top[:40]}` | "
                         f"{f.get('|'.join(['None'] * 8), 0):.3f} | {const:.3f} | {samples[(m, L)]['n_sources']:,} |")
    lines += ["", "Cross-map agreement (log10 frequency, unseen floored at 0.5/n):", "",
              "| length | behaviours (union) | well sampled (≥ 100 in either map) | Spearman rho, well sampled | "
              "rho, well sampled and data-dependent | top-20 overlap | "
              "P(fold) / P(direct) of the 20 most common fold behaviours (median) |",
              "|---|---|---|---|---|---|---|"]
    for L in lengths:
        ff, nf = freq("fold", L)
        fd, nd = freq("direct", L)
        union = sorted(set(ff) | set(fd))
        # Rare behaviours seen in one map only would sit on the floor and dominate rho.
        well = [b for b in union if max(ff.get(b, 0) * nf, fd.get(b, 0) * nd) >= 100]
        lf = [math.log10(ff.get(b, 0.5 / nf)) for b in well]
        ld = [math.log10(fd.get(b, 0.5 / nd)) for b in well]
        dep = [i for i, b in enumerate(well) if len(set(b.split("|"))) > 1]
        top_f = sorted(ff, key=ff.get, reverse=True)[:20]
        top_d = sorted(fd, key=fd.get, reverse=True)[:20]
        ratio = np.median([ff[b] / fd.get(b, 0.5 / nd) for b in top_f])
        lines.append(f"| {L} | {len(union):,} | {len(well):,} | {_spearman(lf, ld):.2f} | "
                     f"{_spearman([lf[i] for i in dep], [ld[i] for i in dep]):.2f} | "
                     f"{len(set(top_f) & set(top_d))}/20 | {ratio:.2f} |")
    lines += ["", "P(random genotype is exact) and P(fitness ≥ 0.75), per task:", "",
              "| task | length | P(exact) fold | P(exact) direct | ratio | P(≥0.75) fold | P(≥0.75) direct |",
              "|---|---|---|---|---|---|---|"]
    p_exact = {}
    for t in TASKS:
        for L in lengths:
            row = []
            for m in MAPS:
                f, n = freq(m, L)
                pe = sum(v for b, v in f.items() if exact(beh_outs[b], t))
                p75 = sum(v for b, v in f.items() if fitness(beh_outs[b], t) >= 0.75)
                p_exact[(t, m, L)] = pe
                row += [pe, p75]
            ratio = (row[0] / row[2]) if row[2] else float("inf") if row[0] else float("nan")
            lines.append(f"| {t} | {L} | {row[0]:.1e} | {row[2]:.1e} | {ratio:.2g} | {row[1]:.1e} | {row[3]:.1e} |")

    if not (sd / "SAMPLE_DONE").exists():
        lines.insert(1, "**PARTIAL: Phase A did not finish (no SAMPLE_DONE).**\n")
    if args.evolve:
        ev_path = Path(args.evolve) / "evolve.jsonl"
        if not ev_path.exists():
            lines += ["", f"**Phase B missing: no {ev_path}.**"]
        else:
            if not (Path(args.evolve) / "EVOLVE_DONE").exists():
                lines.insert(1, "**PARTIAL: Phase B did not finish (no EVOLVE_DONE); counts below "
                                "cover the runs that completed.**\n")
            lines += phase_b(ev_path, samples, lengths, freq, beh_outs, p_exact)
    text = "\n".join(lines) + "\n"
    (Path(args.report) if args.report else _out(args) / "report.md").write_text(text)
    print(text)


def _binom_two_sided(k: int, n: int) -> float:
    from scipy.stats import binomtest
    return float(binomtest(k, n, 0.5).pvalue) if n else 1.0


def phase_b(ev_path, samples, lengths, freq, beh_outs, p_exact) -> list[str]:
    """Phase B tables. Arms are paired: within a (task, budget, seed) both maps start from
    the same genotypes, so solves are compared by McNemar (exact binomial on discordant
    pairs) and endpoint frequencies by a signed-rank test on the seed pairs."""
    import numpy as np
    from scipy.stats import wilcoxon

    runs = [json.loads(x) for x in ev_path.read_text().splitlines()]
    L0 = runs[0]["L0"]
    if L0 not in lengths:
        raise SystemExit(f"no Phase A sample at the evolution start length {L0}")
    fr = {(m, L): freq(m, L) for m in MAPS for L in lengths}

    def near(L):
        return min(lengths, key=lambda x: abs(x - L))

    def dval(b, L):
        """log10 P_fold(b) - log10 P_direct(b), both at the sampled length nearest L
        (evolved genotypes drift in length); unseen floored at 0.5/n."""
        (ff, nf), (fd, nd) = fr[("fold", near(L))], fr[("direct", near(L))]
        return math.log10(ff.get(b, 0.5 / nf)) - math.log10(fd.get(b, 0.5 / nd))

    ev = [r for r in runs if r["search"] == "evolve"]
    budgets = sorted({(r["pop"], r["gens"]) for r in ev})
    key = lambda r: (r["task"], r["pop"], r["gens"], r["seed"])  # noqa: E731
    pairs = collections.defaultdict(dict)
    for r in runs:
        pairs[(r["search"],) + key(r)][r["map"]] = r
    lines = ["", f"## Phase B: evolution (start length {L0})", "",
             "Solved = some individual exact on all 8 contexts at any generation. Pairs share the "
             "start population; p = McNemar exact test on seeds where only one map solved.", "",
             "| task | budget | fold solved | direct solved | only fold / only direct | p | "
             "P(exact) fold / direct at L0 |", "|---|---|---|---|---|---|---|"]
    agree = total = 0
    for (pop, gens) in budgets:
        for t in TASKS:
            ps = [v for k, v in pairs.items() if k[0] == "evolve" and k[1:4] == (t, pop, gens) and len(v) == 2]
            if not ps:
                continue
            sf = [v["fold"]["first_exact_gen"] is not None for v in ps]
            sd = [v["direct"]["first_exact_gen"] is not None for v in ps]
            of = sum(a and not b for a, b in zip(sf, sd))
            od = sum(b and not a for a, b in zip(sf, sd))
            pf, pd = p_exact[(t, "fold", L0)], p_exact[(t, "direct", L0)]
            if pf != pd and of != od:
                total += 1
                agree += (pf > pd) == (of > od)
            lines.append(f"| {t} | {pop}×{gens} | {sum(sf)}/{len(ps)} | {sum(sd)}/{len(ps)} | {of} / {od} | "
                         f"{_binom_two_sided(of, of + od):.2g} | {pf:.1e} / {pd:.1e} |")
    lines += ["", f"The map with more random exact solvers also solves more often in {agree}/{total} "
              "(task, budget) cells where both differ."]

    lines += ["", "### Do endpoints sit on their own map's frequent behaviours?", "",
              "d = log10 P_fold(b) − log10 P_direct(b) of a run's best behaviour b, with frequencies "
              "taken at the Phase A length nearest the genotype's length (unseen floored at 0.5/n). "
              "Own-map steering predicts d(fold) > d(direct). Seed pairs where neither map ever "
              "solved; one-sided Wilcoxon signed-rank on d(fold) − d(direct). Baselines: the same pairs' "
              "generation-0 best behaviours (start bias), and random search with the same budget at "
              "L0 (how far each map's bias alone carries the endpoint).", "",
              "| task | budget | pairs | median d(fold) − d(direct): evolved | p | gen 0 | "
              "random search: matched pairs, median evolved − random, p | "
              "endpoints unseen in own map's sample (fold / direct) |",
              "|---|---|---|---|---|---|---|---|"]
    for (pop, gens) in budgets:
        for t in TASKS:
            ps = [v for k, v in pairs.items() if k[0] == "evolve" and k[1:4] == (t, pop, gens) and len(v) == 2
                  and v["fold"]["first_exact_gen"] is None and v["direct"]["first_exact_gen"] is None]
            if len(ps) < 5:
                continue
            diff = [dval(v["fold"]["best_behaviour"], v["fold"]["best_len"])
                    - dval(v["direct"]["best_behaviour"], v["direct"]["best_len"]) for v in ps]
            g0 = [dval(v["fold"]["gen0_behaviour"], L0) - dval(v["direct"]["gen0_behaviour"], L0) for v in ps]
            nz = [x for x in diff if x != 0]
            p = wilcoxon(nz, alternative="greater").pvalue if len(nz) >= 5 else float("nan")
            # Random search on the same seeds: eligible when neither map solved under
            # evolution nor under random search; paired evolved-minus-random difference.
            matched = []
            for v, dv in zip(ps, diff):
                rv = pairs.get(("random", t, pop, gens, v["fold"]["seed"]), {})
                if len(rv) == 2 and all(rv[m]["first_exact_gen"] is None for m in MAPS):
                    rd = dval(rv["fold"]["best_behaviour"], L0) - dval(rv["direct"]["best_behaviour"], L0)
                    matched.append(dv - rd)
            mz = [x for x in matched if x != 0]
            rp = wilcoxon(mz, alternative="greater").pvalue if len(mz) >= 5 else float("nan")
            rtxt = f"{len(matched)}, {np.median(matched):.2f}, {rp:.2g}" if matched else "-"
            unseen = [sum(v[m]["best_behaviour"] not in fr[(m, near(v[m]["best_len"]))][0] for v in ps) for m in MAPS]
            lines.append(f"| {t} | {pop}×{gens} | {len(ps)} | {np.median(diff):.2f} | {p:.2g} | "
                         f"{np.median(g0):.2f} | {rtxt} | {unseen[0]} / {unseen[1]} |")

    lines += ["", "### Endpoint rank among own-map behaviours at or above its fitness", "",
              "Frequencies at the Phase A length nearest the endpoint genotype's length.", "",
              "| map | budget | endpoints | unseen | rank 1 | uniform-choice expectation | median rank |",
              "|---|---|---|---|---|---|---|"]
    fit_cache: dict = {}
    for m in MAPS:
        for (pop, gens) in budgets:
            rs = [r for r in ev if r["map"] == m and r["pop"] == pop and r["gens"] == gens]
            ranks, unif, unseen = [], 0.0, 0
            for r in rs:
                L = near(r["best_len"])
                f, _ = fr[(m, L)]
                if r["best_behaviour"] not in f:
                    unseen += 1
                    continue
                ck = (m, L, r["task"])
                if ck not in fit_cache:
                    fit_cache[ck] = (sorted(f, key=f.get, reverse=True),
                                     {b: fitness(beh_outs[b], r["task"]) for b in f})
                order, fit_b = fit_cache[ck]
                above = [b for b in order if fit_b[b] >= r["best_fitness"] - 1e-9]
                if len(above) < 2:
                    continue
                ranks.append(above.index(r["best_behaviour"]) + 1)
                unif += 1 / len(above)
            lines.append(f"| {m} | {pop}×{gens} | {len(rs)} | {unseen} | {sum(x == 1 for x in ranks)} of "
                         f"{len(ranks)} | {unif:.1f} | {np.median(ranks) if ranks else '-'} |")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--n", type=int, default=20_000_000, help="genotypes per (map, length)")
    s.add_argument("--lengths", default="30,50,80")
    s.add_argument("--workers", type=int, default=10)
    s.add_argument("--out", default=None)
    e = sub.add_parser("evolve")
    e.add_argument("--seeds", type=int, default=50)
    e.add_argument("--budgets", default="200x1000", help="comma list of POPxGENS")
    e.add_argument("--length", type=int, default=50, help="initial genotype length")
    e.add_argument("--random-budgets", default="", help="POPxGENS budgets for the random-search baseline")
    e.add_argument("--tasks", default="", help="';'-separated task names (default: all)")
    e.add_argument("--workers", type=int, default=10)
    e.add_argument("--out", default=None)
    a = sub.add_parser("analyze")
    a.add_argument("--sample", required=True)
    a.add_argument("--evolve", default=None)
    a.add_argument("--report", default=None)
    a.add_argument("--out", default=None)
    args = ap.parse_args()
    {"sample": cmd_sample, "evolve": cmd_evolve, "analyze": cmd_analyze}[args.cmd](args)


if __name__ == "__main__":
    main()
