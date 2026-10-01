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
from functools import lru_cache
from itertools import accumulate
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from exp_task_verification_strict import CANDIDATE_TASKS, make_discriminating_contexts  # noqa: E402
from folding_evolution.alphabet import ALPHABET, random_genotype  # noqa: E402
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


@lru_cache(maxsize=32)
def _char_weights(k_weight: float) -> tuple[float, ...]:
    if not math.isfinite(k_weight) or k_weight <= 0:
        raise ValueError("k_weight must be finite and positive")
    return tuple(accumulate(k_weight if c == "k" else 1.0 for c in ALPHABET))


def draw_char(rng: random.Random, k_weight: float) -> str:
    return rng.choices(ALPHABET, cum_weights=_char_weights(k_weight), k=1)[0]


def rand_genotype(length: int, rng: random.Random, k_weight: float) -> str:
    if k_weight == 1.0:
        return random_genotype(length, rng)
    return "".join(rng.choices(ALPHABET, cum_weights=_char_weights(k_weight), k=length))


def mutate_w(g: str, rng: random.Random, k_weight: float) -> str:
    if k_weight == 1.0:
        return mutate(g, rng)
    op = rng.choice(("point", "insertion", "deletion"))
    if op == "deletion" and len(g) > 1:
        pos = rng.randrange(len(g))
        return g[:pos] + g[pos + 1:]
    if op == "insertion":
        pos = rng.randrange(len(g) + 1)
        return g[:pos] + draw_char(rng, k_weight) + g[pos:]
    if not g:
        return g
    pos = rng.randrange(len(g))
    return g[:pos] + draw_char(rng, k_weight) + g[pos + 1:]


def select_survivors(pop, sc, kids, ksc, tie, rng):
    if tie == "offspring":
        allg, alls = kids + pop, ksc + sc
    else:
        allg, alls = pop + kids, sc + ksc
    if tie == "random":
        noise = [rng.random() for _ in allg]
        order = sorted(range(len(allg)), key=lambda i: (-alls[i][0], noise[i]))[:len(pop)]
    else:
        order = sorted(range(len(allg)), key=lambda i: -alls[i][0])[:len(pop)]
    return [allg[i] for i in order], [alls[i] for i in order]


def run_key(r):
    return (r["task"], r["map"], r["pop"], r["gens"], r["L0"], r["seed"],
            r["search"], r.get("tie", "parents"), float(r.get("k_weight", 1.0)))


def _budgets(text):
    result = [tuple(int(x) for x in b.split("x")) for b in text.split(",") if b]
    if any(len(b) != 2 or b[0] < 3 or b[1] < 0 for b in result):
        raise ValueError("budgets must be POPxGENS with POP >= 3 and GENS >= 0")
    return list(dict.fromkeys(result))


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
    m, L, seed, n, k_weight = payload
    rng = random.Random(seed)
    gs = [rand_genotype(L, rng, k_weight) for _ in range(n)]
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
    _char_weights(args.k_weight)
    if args.n <= 0 or args.workers <= 0 or any(L <= 0 for L in lengths):
        raise ValueError("sample counts, lengths and workers must be positive")
    (out / "SAMPLE_DONE").unlink(missing_ok=True)
    jobs = [(m, L, s, min(CHUNK, args.n - s * CHUNK), args.k_weight)
            for m in MAPS for L in lengths for s in range(math.ceil(args.n / CHUNK))]
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
        suffix = f"_k{args.k_weight:g}" if args.k_weight != 1.0 else ""
        (out / f"sample_{m}_L{L}{suffix}.json").write_text(json.dumps(
            {"map": m, "length": L, "k_weight": args.k_weight, "n": n, "n_source_sample": sum(src.values()),
             "behaviours": rows, "sources_top": src.most_common(200), "n_sources": len(src)}))
        print(f"{m} L{L}: {n:,} genotypes, {len(c):,} behaviours, {len(src):,} sources in the first "
              f"{sum(src.values()):,}", flush=True)
    (out / "SAMPLE_DONE").write_text("ok\n")


# ---------------- Phase B ----------------

def _evolve_one(payload) -> dict:
    """search "evolve": the exp_2x2.run_stable loop. search "random": the same budget of
    fresh random genotypes at L0 each generation, keeping the best pop_size (a baseline
    for how far each map's own bias alone carries the endpoint)."""
    task, m, pop_size, gens, L0, seed, search, tie, k_weight = payload
    if search == "random":
        tie = "parents"  # Fixed night-1 baseline; tie intervention is evolutionary.
    rng = random.Random(f"{task}|{pop_size}|{gens}|{seed}")    # same start for both maps
    pop = [rand_genotype(L0, rng, k_weight) for _ in range(pop_size)]

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
                kids.append(rand_genotype(L0, rng, k_weight))
            elif rng.random() < 0.7:
                child = crossover(pick(), pick(), rng)
            else:
                child = mutate_w(pick(), rng, k_weight)
            if search != "random":
                kids.append(child[:MAX_LEN])
        ksc = score(kids)
        if first_exact is None and any(e for _, e, _ in ksc):
            first_exact = gen
        pop, sc = select_survivors(pop, sc, kids, ksc, tie, rng)
    best = max(range(pop_size), key=lambda i: (sc[i][0], sc[i][1]))
    final_beh = collections.Counter(b for _, _, b in sc)
    return {"task": task, "map": m, "pop": pop_size, "gens": gens, "L0": L0, "seed": seed,
            "search": search, "tie": tie, "k_weight": k_weight, **gen0, "best_len": len(pop[best]),
            "best_fitness": sc[best][0], "best_exact": sc[best][1], "best_behaviour": sc[best][2],
            "best_genotype": pop[best], "first_exact_gen": first_exact,
            "final_exact_members": sum(e for _, e, _ in sc),
            "final_behaviours": final_beh.most_common(20), "n_final_behaviours": len(final_beh),
            "final_top_share": final_beh.most_common(1)[0][1] / pop_size,
            "mean_len": sum(map(len, pop)) / pop_size}


def cmd_evolve(args) -> None:
    out = _out(args)
    out.mkdir(parents=True, exist_ok=True)
    budgets = _budgets(args.budgets)
    weights = list(dict.fromkeys(float(x) for x in args.k_weights.split(",")))
    for w in weights:
        _char_weights(w)
    tasks = args.tasks.split(";") if args.tasks else list(TASKS)
    if any(t not in TASKS for t in tasks) or args.seeds <= 0 or args.workers <= 0 or args.length <= 0:
        raise ValueError("unknown task or non-positive seeds/workers/length")
    done = set()
    res_path = out / "evolve.jsonl"
    if res_path.exists():
        for line in res_path.read_text().splitlines():
            r = json.loads(line)
            done.add(run_key(r))
    rbudgets = _budgets(args.random_budgets)
    (out / "EVOLVE_DONE").unlink(missing_ok=True)
    jobs = [(t, m, p, g, args.length, s, mode, tie, w)
            for mode, bs in (("evolve", budgets), ("random", rbudgets)) for (p, g) in bs
            for tie in (args.tie if mode == "evolve" else "parents",)
            for t in tasks for s in range(args.seeds) for m in MAPS for w in weights
            if (t, m, p, g, args.length, s, mode, tie, w) not in done]
    if not budgets and not rbudgets:
        raise ValueError("at least one evolution or random-search budget is required")
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


def _binom_two_sided(k: int, n: int) -> float:
    from scipy.stats import binomtest
    return float(binomtest(k, n, 0.5).pvalue) if n else 1.0


def _solved(r):
    return r["first_exact_gen"] is not None


def _diversity(r):
    # Night 1 stores only the top 20, so larger counts cannot be recovered.
    top = r["final_behaviours"]
    count = r.get("n_final_behaviours")
    if count is None and len(top) < 20:
        count = len(top)
    return count, r.get("final_top_share", top[0][1] / r["pop"] if top else None)


def _trend(groups):
    """Descriptive pooled Cochran-Armitage score test, scored by measured P(exact).

    Reused seeds are paired across weights; the pooled reference distribution does
    not model that dependence. Also report the paired low/high comparison below.
    """
    from scipy.stats import norm
    total = sum(n for _, s, n in groups)
    p = sum(s for _, s, n in groups) / total
    mean = sum(x * n for x, s, n in groups) / total
    variance = p * (1 - p) * sum(n * (x - mean) ** 2 for x, s, n in groups)
    if variance <= 0:
        return None, None
    z = sum((x - mean) * (s - n * p) for x, s, n in groups) / math.sqrt(variance)
    return z, float(2 * norm.sf(abs(z)))


def cmd_analyze(args) -> None:
    import numpy as np

    warnings = []
    samples = {}
    for directory in args.sample:
        sd = Path(directory)
        if not (sd / "SAMPLE_DONE").exists():
            warnings.append(f"Missing SAMPLE_DONE: {sd}")
        files = sorted(sd.glob("sample_*_L*.json"))
        if not files:
            warnings.append(f"No sample files: {sd}")
        for path in files:
            d = json.loads(path.read_text())
            key = (d["map"], d["length"], float(d.get("k_weight", 1.0)))
            if key in samples:
                raise ValueError(f"duplicate sample arm {key}: {path}")
            if d["n"] <= 0 or sum(r["count"] for r in d["behaviours"]) != d["n"]:
                raise ValueError(f"invalid sample counts: {path}")
            samples[key] = d

    # Recover exactness from actual program outputs, never from the lossy repr alone.
    exact_probability = {}
    for (m, length, weight), d in samples.items():
        counts = {task: 0 for task in TASKS}
        for row in d["behaviours"]:
            outs = outputs(develop_many([row["example"]], m)[0])
            if behaviour(outs) != row["behaviour"]:
                raise ValueError("sample behaviour does not replay under this code")
            for task in TASKS:
                if exact(outs, task):
                    counts[task] += row["count"]
        for task, count in counts.items():
            exact_probability[(task, m, length, weight)] = count / d["n"]

    runs = {}
    for directory in args.evolve:
        ed = Path(directory)
        if not (ed / "EVOLVE_DONE").exists():
            warnings.append(f"Missing EVOLVE_DONE: {ed}")
        path = ed / "evolve.jsonl"
        if not path.exists():
            warnings.append(f"Missing evolve.jsonl: {ed}")
            continue
        for line in path.read_text().splitlines():
            r = json.loads(line)
            r.setdefault("tie", "parents")
            r.setdefault("k_weight", 1.0)
            key = run_key(r)
            if key in runs:
                raise ValueError(f"duplicate run arm {key}: {path}")
            runs[key] = r
    rows = list(runs.values())
    cells = collections.defaultdict(dict)
    for r in rows:
        key = (r["task"], r["map"], r["pop"], r["gens"], r["L0"],
               r["search"], r["tie"], r["k_weight"])
        cells[key][r["seed"]] = r
    for key, cell in cells.items():
        if set(cell) != set(range(args.expected_seeds)):
            warnings.append(f"Seed coverage {key}: {len(cell)}/{args.expected_seeds}")

    def cell(task, m, pop, gens, length, mode, tie="parents", weight=1.0):
        return cells.get((task, m, pop, gens, length, mode, tie, weight), {})

    def rate(rs):
        return f"{sum(_solved(r) for r in rs.values())}/{len(rs)}" if rs else "not run"

    def probability(task, m, length, weight):
        value = exact_probability.get((task, m, length, weight))
        if value is None:
            warnings.append(f"Missing P(exact): {task}, {m}, L{length}, k={weight:g}")
        return value

    lines = ["# Map-bias pivot night 2", "",
             "Solved = at least one individual exact on all eight contexts at any generation. "
             "All rates show actual denominators. Paired contrasts use the intersection of seed IDs. "
             "Legacy rows mean parents-first, k=1. Random search keeps the night-1 parents-first "
             "selection rule and samples fixed-length genotypes.", "",
             "P-values are exploratory, uncorrected across tasks/budgets. Count tasks share a "
             "program family. The k intervention changes initialization and mutation proposals "
             "together; it does not isolate starting frequency from mutational accessibility.", "",
             "## Phase A: exact random-genotype frequencies", "",
             "| task | L | k weight | fold P(exact) | direct P(exact) | sample n fold / direct |",
             "|---|---|---|---|---|---|"]
    for length, weight in sorted({(L, w) for m, L, w in samples}):
        for task in TASKS:
            values = [probability(task, m, length, weight) for m in MAPS]
            sizes = [samples.get((m, length, weight), {}).get("n", 0) for m in MAPS]
            rendered = [f"{v:.6g}" if v is not None else "missing" for v in values]
            lines.append(f"| {task} | {length} | {weight:g} | {rendered[0]} | {rendered[1]} | {sizes[0]} / {sizes[1]} |")

    lines += ["", "## T1: drift check (unsolved runs, k=1)", "",
              "Pooled across tasks within each arm. Legacy top-20 lists recover the exact distinct "
              "count only when fewer than 20 entries were stored; other counts are unavailable.", "",
              "| L0 | tie | map | budget | unsolved n | median distinct behaviours (available n) | median top share | median best length |",
              "|---|---|---|---|---|---|---|---|"]
    drift = collections.defaultdict(list)
    for r in rows:
        if r["search"] == "evolve" and r["k_weight"] == 1.0 and not _solved(r):
            drift[(r["L0"], r["tie"], r["map"], r["pop"], r["gens"])].append(r)
    for (length, tie, m, pop, gens), rs in sorted(drift.items()):
        counts = [n for n, share in map(_diversity, rs) if n is not None]
        shares = [share for n, share in map(_diversity, rs) if share is not None]
        ntext = f"{np.median(counts):.3g} ({len(counts)})" if counts else "unavailable (0)"
        sharetext = f"{np.median(shares):.3f}" if shares else "unavailable"
        lines.append(f"| {length} | {tie} | {m} | {pop}×{gens} | {len(rs)} | {ntext} | {sharetext} | {np.median([r['best_len'] for r in rs]):.3g} |")

    lines += ["", "## T2: solve rates and seed-paired comparisons (k=1)", "",
              "| task | L0 | budget | search / tie | fold solved | direct solved | paired n | only fold / only direct | McNemar p |",
              "|---|---|---|---|---|---|---|---|---|"]
    arms = sorted({(r["task"], r["L0"], r["pop"], r["gens"], r["search"], r["tie"])
                   for r in rows if r["k_weight"] == 1.0})
    for task, length, pop, gens, mode, tie in arms:
        f = cell(task, "fold", pop, gens, length, mode, tie)
        d = cell(task, "direct", pop, gens, length, mode, tie)
        paired = sorted(f.keys() & d.keys())
        of = sum(_solved(f[s]) and not _solved(d[s]) for s in paired)
        od = sum(_solved(d[s]) and not _solved(f[s]) for s in paired)
        p = f"{_binom_two_sided(of, of + od):.4g}" if paired else "not paired"
        lines.append(f"| {task} | {length} | {pop}×{gens} | {mode} / {tie} | {rate(f)} | {rate(d)} | {len(paired)} | {of} / {od} | {p} |")
    lines += ["", "### Evolution minus random search, paired by seed", "",
              "Difference is in percentage points on paired seeds, including all solve outcomes.", "",
              "| task | L0 | budget | tie | map | evolution / random solved | paired n | difference pp | evolution only / random only | McNemar p |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for task, length, pop, gens, mode, tie in arms:
        if mode != "evolve":
            continue
        for m in MAPS:
            e = cell(task, m, pop, gens, length, "evolve", tie)
            b = cell(task, m, pop, gens, length, "random")
            if not b:
                warnings.append(f"Missing random-search baseline: {task}, {m}, L{length}, {pop}x{gens}")
            paired = sorted(e.keys() & b.keys())
            eo = sum(_solved(e[s]) and not _solved(b[s]) for s in paired)
            bo = sum(_solved(b[s]) and not _solved(e[s]) for s in paired)
            delta = f"{100 * (eo - bo) / len(paired):+.1f}" if paired else "not paired"
            p = f"{_binom_two_sided(eo, eo + bo):.4g}" if paired else "not paired"
            lines.append(f"| {task} | {length} | {pop}×{gens} | {tie} | {m} | {rate(e)} / {rate(b)} | {len(paired)} | {delta} | {eo} / {bo} | {p} |")

    lines += ["", "## T3: frequency knob (random tie rule)", "",
              "The k=1 reference is the random-tie drift arm. Monotonicity is ordered by measured "
              "P(exact), not by assumed k ordering. Cochran-Armitage is a descriptive pooled test: "
              "it treats weights as independent despite reused seeds. The low/high contrast "
              "also reports an exact seed-paired McNemar test. Constant outcomes have no trend "
              "variance and are reported as uninformative. count(products) is the control.", "",
              "| task | map | L0 | budget | k=0.2 P(exact), solves | k=1 P(exact), solves | k=5 P(exact), solves | monotone with P(exact) | pooled z, p | paired low/high n, pp, p |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    knob_arms = sorted({(r["task"], r["map"], r["L0"], r["pop"], r["gens"])
                        for r in rows if r["search"] == "evolve" and r["tie"] == "random" and r["k_weight"] != 1.0})
    for task, m, length, pop, gens in knob_arms:
        parts, groups, complete = [], [], True
        for weight in (0.2, 1.0, 5.0):
            rs = cell(task, m, pop, gens, length, "evolve", "random", weight)
            pe = probability(task, m, length, weight)
            parts.append(f"{pe:.6g}, {rate(rs)}" if pe is not None else f"missing, {rate(rs)}")
            if rs and pe is not None:
                groups.append((pe, sum(_solved(r) for r in rs.values()), len(rs)))
            else:
                complete = False
                warnings.append(f"Missing knob arm: {task}, {m}, L{length}, {pop}x{gens}, k={weight:g}")
        monotone = trend = contrast = "incomplete"
        if complete:
            ordered = sorted(groups)
            rates = [s / n for pe, s, n in ordered]
            monotone = "flat" if len(set(rates)) == 1 else "yes" if all(a <= b for a, b in zip(rates, rates[1:])) else "no"
            if len({pe for pe, s, n in groups}) < 3:
                monotone = "frequency ties; not identifiable"
            z, p = _trend(groups)
            trend = f"{z:+.3g}, {p:.4g}" if z is not None else "uninformative"
            low = cell(task, m, pop, gens, length, "evolve", "random", 0.2)
            high = cell(task, m, pop, gens, length, "evolve", "random", 5.0)
            paired = sorted(low.keys() & high.keys())
            ho = sum(_solved(high[s]) and not _solved(low[s]) for s in paired)
            lo = sum(_solved(low[s]) and not _solved(high[s]) for s in paired)
            contrast = f"{len(paired)}, {100 * (ho - lo) / len(paired):+.1f}, {_binom_two_sided(ho, ho + lo):.4g}" if paired else "not paired"
        lines.append(f"| {task} | {m} | {length} | {pop}×{gens} | " + " | ".join(parts) + f" | {monotone} | {trend} | {contrast} |")
    if not knob_arms:
        lines.append("No weighted evolution runs supplied; the knob is not yet tested.")
    if warnings:
        lines[1:1] = ["", "**PARTIAL: inputs or seed coverage are incomplete.**", ""]
        lines += ["", "## Incomplete inputs", ""] + [f"- {w}" for w in dict.fromkeys(warnings)]
    report = Path(args.report) if args.report else _out(args) / "report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n")
    print(f"Report: {report}; {len(rows)} runs; {'PARTIAL' if warnings else 'complete supplied inputs'}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--n", type=int, default=20_000_000, help="genotypes per (map, length)")
    s.add_argument("--lengths", default="30,50,80")
    s.add_argument("--workers", type=int, default=10)
    s.add_argument("--out", default=None)
    s.add_argument("--k-weight", type=float, default=1.0)
    e = sub.add_parser("evolve")
    e.add_argument("--seeds", type=int, default=50)
    e.add_argument("--budgets", default="200x1000", help="comma list of POPxGENS")
    e.add_argument("--length", type=int, default=50, help="initial genotype length")
    e.add_argument("--random-budgets", default="", help="POPxGENS budgets for the random-search baseline")
    e.add_argument("--tasks", default="", help="';'-separated task names (default: all)")
    e.add_argument("--workers", type=int, default=10)
    e.add_argument("--out", default=None)
    e.add_argument("--tie", choices=("parents", "random", "offspring"), default="parents",
                   help="evolution tie rule; random-search baselines always use parents")
    e.add_argument("--k-weights", default="1", help="comma-separated positive rest-character weights")
    a = sub.add_parser("analyze")
    a.add_argument("--sample", required=True, nargs="+")
    a.add_argument("--evolve", default=[], nargs="+")
    a.add_argument("--expected-seeds", type=int, default=50)
    a.add_argument("--report", default=None)
    a.add_argument("--out", default=None)
    args = ap.parse_args()
    {"sample": cmd_sample, "evolve": cmd_evolve, "analyze": cmd_analyze}[args.cmd](args)


if __name__ == "__main__":
    main()
