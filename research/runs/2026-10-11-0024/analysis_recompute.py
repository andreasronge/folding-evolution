"""Independent recomputation for 0024 analysis.md (reviewer)."""
import gzip, json, sys
from collections import Counter, defaultdict
import numpy as np

OUT = "/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/"
REPO = "/Users/andreas/developer/folding-evolution-research/2026-10-11-0024/"
CAP = 524288; CUT = 65536

def load(fam):
    return [json.loads(l) for l in open(OUT + f"2026-10-11-0024-{fam.lower()}/search.jsonl")]
def hist(fam):
    return [json.loads(l) for l in gzip.open(REPO + f"experiments/chem_tape/data/restart_gp_0024/{fam}.jsonl.gz", "rt")]

for fi, fam in enumerate(("DG", "TS")):
    rows = load(fam); old = hist(fam)
    print(f"\n######## {fam}: {len(rows)} rows")
    keys = [(r["cell"], r["arm"], r["build"], r["repeat"]) for r in rows]
    print("duplicates:", len(keys) - len(set(keys)))
    cells = sorted({r["cell"] for r in rows}); print("cells:", len(cells))
    cnt = Counter(r["arm"] for r in rows); print("rows per arm:", dict(cnt))
    expected = {(c, a, b, s) for c in cells for a in ("R-tree", "R-A8", "F-A8") for b in range(24) for s in range(2 if a == "F-A8" else 4)}
    print("grid matches expected:", set(keys) == expected)
    # accounting
    bad = []
    for r in rows:
        tot = sum(a["evaluations"] for a in r["attempts"])
        if tot != r["evaluations"] or r["evaluations"] > CAP or (not r["solved"] and r["evaluations"] != (CAP)):
            bad.append((r["arm"], r["cell"], r["build"], r["repeat"], r["evaluations"], tot, r["solved"]))
        if r["arm"] == "F-A8" and (len(r["attempts"]) != 1 or r["cap"] != CAP or r["attempts"][0]["cap"] != CAP):
            bad.append(("F-A8 cap", r["cell"], r["build"], r["repeat"]))
        if r["arm"] != "F-A8" and (r["cutoff"] != CUT or any(a["cap"] != CUT for a in r["attempts"]) or len(r["attempts"]) > 8):
            bad.append(("cutoff", r["cell"], r["build"], r["repeat"]))
        if r["solved"] != r["attempts"][-1]["solved"] or any(a["solved"] for a in r["attempts"][:-1]):
            bad.append(("stop rule", r["cell"], r["build"], r["repeat"]))
        if any(a.get("shortcuts", 0) for a in r["attempts"]) or any(a.get("force_cap") for a in r["attempts"]):
            bad.append(("shortcut/force_cap", r["arm"], r["cell"], r["build"], r["repeat"]))
    print("accounting violations:", len(bad), bad[:5])
    # seeds
    by = {k: r for k, r in zip(keys, rows)}
    ci = {c: i for i, c in enumerate(cells)}
    seedbad = 0; shared = 0
    for c in cells:
        for b in range(24):
            for s in range(4):
                exp = [22300000 + 1000 * (8 * fi + ci[c]) + 8 * (4 * b + s) + k for k in range(8)]
                t, a = by[c, "R-tree", b, s], by[c, "R-A8", b, s]
                if t["seeds"] != exp or a["seeds"] != exp: seedbad += 1
                if t["seeds"] == a["seeds"]: shared += 1
                for k, at in enumerate(t["attempts"] + a["attempts"]):
                    pass
            for s in range(2):
                f = by[c, "F-A8", b, s]
                if f["seeds"] != [22320000 + 1000 * (8 * fi + ci[c]) + 2 * b + s]: seedbad += 1
    print("seed formula violations:", seedbad, "| paired restarted jobs sharing seeds:", shared, "/", 8 * 24 * 4)
    # attempt-level seed check
    att_seed_bad = sum(1 for r in rows if r["arm"] != "F-A8" for k, a in enumerate(r["attempts"]) if a["seed"] != r["seeds"][k])
    print("attempt seed mismatches:", att_seed_bad)
    # all seeds unique across all attempts (except intended sharing)
    allseeds = Counter(a["seed"] for r in rows for a in r["attempts"])
    print("max seed multiplicity (2 expected for shared restarted):", max(allseeds.values()), "| seeds used once:", sum(1 for v in allseeds.values() if v == 1))
    oldseeds = {r["seed"] for r in old}
    print("overlap with 2254 rows' seeds:", len(set(allseeds) & oldseeds))

    # key numbers
    print("\n-- arm summaries")
    arms = ("R-tree", "R-A8", "F-A8")
    A = {}
    for a in arms:
        rs = [r for r in rows if r["arm"] == a]
        ev = np.array([r["evaluations"] for r in rs]); sv = np.array([r["solved"] for r in rs]); ws = np.array([r["worker_seconds"] for r in rs])
        A[a] = (ev, sv, ws)
        print(f"{a}: jobs {len(rs)} solved {sv.sum()}/{len(rs)} = {sv.mean():.4f}; mean evals {ev.mean():.0f} (median {np.median(ev):.0f}, q90 {np.quantile(ev,.9):.0f}); mean worker s {ws.mean():.2f}; us/eval {1e6*ws.sum()/ev.sum():.1f}")
    # attempts distribution
    print("\n-- attempts per job (restarted arms): index of solving attempt, F = failed all 8")
    for a in ("R-tree", "R-A8"):
        rs = [r for r in rows if r["arm"] == a]
        c = Counter(len(r["attempts"]) if r["solved"] else "F" for r in rs)
        print(a, dict(sorted(c.items(), key=lambda kv: (isinstance(kv[0], str), kv[0]))))
        # conditional per-attempt success rate
        cond = []
        for k in range(8):
            reached = [r for r in rs if len(r["attempts"]) > k]
            succ = sum(1 for r in reached if r["attempts"][k]["solved"])
            cond.append((k + 1, succ, len(reached), round(succ / len(reached), 3) if reached else None))
        print("  attempt k: solved/reached:", cond)
        p1 = cond[0][1] / cond[0][2]
        print(f"  first-attempt rate {p1:.3f}; independence projection 1-(1-p1)^8 = {1-(1-p1)**8:.4f}; observed job solve {A[a][1].mean():.4f}")
    # 2254 historical rates
    for arm, lab in (("tree", "R-tree"), ("A8", "R-A8/F-A8")):
        rs = [r for r in old if r["arm"] == arm]
        e65 = sum(1 for r in rs if r["solved"] and r["evaluations"] <= CUT)
        print(f"2254 {arm}: {len(rs)} jobs, solved {sum(r['solved'] for r in rs)}, solved by 65536: {e65} ({e65/len(rs):.3f}); mean evals {np.mean([r['evaluations'] for r in rs]):.0f}; us/eval {1e6*sum(r['worker_seconds'] for r in rs)/sum(r['evaluations'] for r in rs):.1f}")
    # first attempt in this run vs historical by-65536 rate (same engines; different seeds)
    # per-build heterogeneity for A8
    print("\n-- per-build A8 (R-A8 solves/32, F-A8 solves/16, 2254 A8 solves/16, R-A8 mean evals)")
    rb = []
    for b in range(24):
        ra = [r for r in rows if r["arm"] == "R-A8" and r["build"] == b]
        fa = [r for r in rows if r["arm"] == "F-A8" and r["build"] == b]
        ho = [r for r in old if r["arm"] == "A8" and r["build"] == b]
        rt = [r for r in rows if r["arm"] == "R-tree" and r["build"] == b]
        rb.append((b, sum(r["solved"] for r in ra), sum(r["solved"] for r in fa), sum(r["solved"] for r in ho), round(np.mean([r["evaluations"] for r in ra])), round(np.mean([r["evaluations"] for r in rt]))))
    for x in rb: print("  ", x)
    ra_s = np.array([x[1] for x in rb]); fa_s = np.array([x[2] for x in rb]); ho_s = np.array([x[3] for x in rb]); ra_e = np.array([x[4] for x in rb]); rt_e = np.array([x[5] for x in rb])
    print("corr(R-A8 solves, 2254 A8 solves) =", round(np.corrcoef(ra_s, ho_s)[0, 1], 3), "| corr(F-A8, 2254 A8) =", round(np.corrcoef(fa_s, ho_s)[0, 1], 3), "| corr(R-A8 mean evals, 2254 solves) =", round(np.corrcoef(ra_e, ho_s)[0, 1], 3))
    print("builds where R-tree mean evals < R-A8 mean evals:", int((rt_e < ra_e).sum()), "/24")

    # paired build bootstrap replicate
    print("\n-- paired build bootstrap (independent replicate, 8192 draws)")
    def mat(a, metric):
        return np.array([[[by[c, a, b, s][metric] for s in range(2 if a == "F-A8" else 4)] for c in cells] for b in range(24)], dtype=float)
    rng = np.random.default_rng(777)
    idx = rng.integers(0, 24, size=(8192, 24))
    def boot(num, den, f=lambda x, y: x / y):
        pn = num.mean(); pd = den.mean()
        d = np.array([f(num[i].mean(), den[i].mean()) for i in idx])
        return f(pn, pd), np.quantile(d, [0.025, 0.975])
    for metric in ("evaluations", "worker_seconds"):
        M = {a: mat(a, metric) for a in arms}
        for n, d in (("R-tree", "R-A8"), ("R-tree", "F-A8"), ("R-A8", "F-A8")):
            p, q = boot(M[n], M[d])
            print(f"  {metric} {n}/{d}: {p:.3f} [{q[0]:.3f}, {q[1]:.3f}]")
    S = {a: mat(a, "solved") for a in arms}
    for n, d in (("R-tree", "R-A8"), ("R-tree", "F-A8")):
        p, q = boot(S[n], S[d], lambda x, y: x - y)
        print(f"  solve diff {n}-{d}: {p:.4f} [{q[0]:.4f}, {q[1]:.4f}]")
    # alternative: bootstrap over cells (8) to show cell-level uncertainty
    idc = rng.integers(0, 8, size=(8192, 8))
    M = {a: mat(a, "evaluations") for a in arms}
    d = np.array([M["R-tree"][:, i].mean() / M["R-A8"][:, i].mean() for i in idc])
    print(f"  cell-resampled (8 cells, descriptive) R-tree/R-A8 evaluations: [{np.quantile(d,.025):.3f}, {np.quantile(d,.975):.3f}]")
    # per-cell ratios
    print("\n-- per-cell R-tree/R-A8 evaluation ratio and solve counts")
    for i, c in enumerate(cells):
        print(f"  {c}: ratio {M['R-tree'][:, i].mean()/M['R-A8'][:, i].mean():.3f}; R-tree {int(S['R-tree'][:, i].sum())}/96 R-A8 {int(S['R-A8'][:, i].sum())}/96 F-A8 {int(S['F-A8'][:, i].sum())}/48")
    # geometric 2x cap
    def geo(a):
        rs = [r for r in rows if r["arm"] == a]
        return np.exp(np.mean([np.log(r["evaluations"] if r["solved"] else 2 * CAP) for r in rs]))
    print("\n-- geometric (failures at 2x cap):", {a: round(geo(a)) for a in arms}, "ratio R-tree/R-A8:", round(geo("R-tree") / geo("R-A8"), 3))
    # restart overhead: us/eval for attempts of restarted arms vs F-A8/2254
    print("-- us/eval by arm, this run:", {a: round(1e6 * A[a][2].sum() / A[a][0].sum(), 1) for a in arms})
    # F-A8 vs 2254 A8 full-cap contemporaneous
    ho = [r for r in old if r["arm"] == "A8"]
    print(f"-- F-A8 {int(A['F-A8'][1].sum())}/384 solved, mean {A['F-A8'][0].mean():.0f} evals vs 2254 A8 {sum(r['solved'] for r in ho)}/384, mean {np.mean([r['evaluations'] for r in ho]):.0f}")
    np.save(f"/tmp/0024_{fam}_cells.npy", np.array(cells))
