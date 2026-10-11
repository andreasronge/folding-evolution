"""Independent reviewer recomputation for 0524 (reads raw search.jsonl only)."""
import json, sys, re
from collections import Counter, defaultdict
import numpy as np

S = "/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0524-score"
P = "/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0524-prepare"
ARMS = ("R-tree", "R-lib", "R-perm")
rows = [json.loads(l) for l in open(f"{S}/search.jsonl")]
print("rows", len(rows))
keys = Counter((r["build"], r["cell"], r["repeat"], r["arm"]) for r in rows)
print("unique keys", len(keys), "max multiplicity", max(keys.values()))
cells = sorted({r["cell"] for r in rows}); print("cells", len(cells))
print("builds", sorted({r["build"] for r in rows}) == list(range(24)), "repeats", sorted({r["repeat"] for r in rows}))
print("per arm", Counter(r["arm"] for r in rows))
by = {(r["build"], r["cell"], r["repeat"], r["arm"]): r for r in rows}
bad_seed = bad_real = 0
for (b, c, rp, a), r in by.items():
    if a == "R-tree":
        others = [by[b, c, rp, x] for x in ARMS]
        if len({tuple(o["seeds"]) for o in others}) != 1: bad_seed += 1
        if any(o["realization"] != rp % 3 for o in others): bad_real += 1
print("triples with mismatched seeds", bad_seed, "mismatched realization", bad_real)
allseeds = [s for r in rows if r["arm"] == "R-tree" for s in r["seeds"]]
print("distinct attempt seeds among R-tree rows", len(set(allseeds)), "of", len(allseeds))
print("caps", Counter(r["cap"] for r in rows), "cutoff", Counter(r["cutoff"] for r in rows))
print("evaluations > cap", sum(r["evaluations"] > r["cap"] for r in rows))
print("unsolved rows", Counter((r["arm"], r["evaluations"] == r["cap"], r["attempt_count"]) for r in rows if not r["solved"]))
print("solved but attempts/evals odd", sum(1 for r in rows if r["solved"] and r["evaluations"] > r["cap"]))

def split(cell):
    m = re.match(r"GS:\(X(\d)\+X(\d)\)>\(X(\d)\+X(\d)\)\?\(X(\d)\+X(\d)\):X(\d)", cell)
    a, b, c, d, e, f, g = map(int, m.groups())
    s = tuple(sorted([tuple(sorted((a, b))), tuple(sorted((c, d)))]))
    return {((0,1),(2,3)): "A", ((0,2),(1,3)): "B", ((0,3),(1,2)): "C"}[s], tuple(sorted((e, f)))
SPLIT = {c: split(c)[0] for c in cells}; THEN = {c: split(c)[1] for c in cells}
print("cells per split", Counter(SPLIT.values()))
learned_then = [c for c in cells if SPLIT[c] in "BC" and THEN[c] in ((0,1),(2,3))]
print("B/C learned then-pair cells", len(learned_then))

def arr(metric, cset):
    cset = list(cset)
    return {a: np.array([[[float(by[b, c, rp, a][metric]) for rp in range(6)] for c in cset] for b in range(24)]) for a in ARMS}

rng = np.random.default_rng(12345)
DR = 8192
builds = rng.integers(24, size=(DR, 24)); cons = rng.integers(3, size=(DR, 24, 3))
def blocks(v):  # (24, cells, 6) -> (24, 3) construction-block means over cells and both repeats
    return np.stack([v[:, :, r::3].mean(axis=(1, 2)) for r in range(3)], axis=1)
def boot(v):
    return v[builds[:, :, None], cons].mean(axis=(1, 2))
def ci(x): return np.percentile(x, [2.5, 97.5])

def report(name, cset):
    ev = arr("evaluations", cset); sv = arr("solved", cset); ws = arr("worker_seconds", cset)
    n = 24 * len(cset) * 6
    print(f"\n== {name}: {len(cset)} cells, {n} jobs/arm")
    for a in ARMS:
        print(f"  {a:7s} mean evals {ev[a].mean():9.0f}  solves {int(sv[a].sum())}/{n}  worker s {ws[a].sum():8.0f}  mean {ws[a].mean():.2f}")
    out = {}
    for a, b in [("R-perm", "R-lib"), ("R-perm", "R-tree"), ("R-lib", "R-tree")]:
        ba, bb = blocks(ev[a]), blocks(ev[b])
        ratio = ba.mean() / bb.mean(); bs = boot(ba) / boot(bb)
        # simpler: build-only bootstrap and per-build log-ratio t-interval
        pb = ev[a].mean(axis=(1, 2)) / ev[b].mean(axis=(1, 2))
        bo = ev[a].mean(axis=(1, 2))[builds].mean(1) / ev[b].mean(axis=(1, 2))[builds].mean(1)
        lr = np.log(pb); t = lr.mean() + np.array([-1, 1]) * 2.069 * lr.std(ddof=1) / np.sqrt(24)
        d = (sv[a] - sv[b]); dm = d.mean(); dci = ci(boot(blocks(d)))
        print(f"  {a}/{b}: ratio {ratio:.3f} nested-boot [{ci(bs)[0]:.3f}, {ci(bs)[1]:.3f}]  build-only boot [{ci(bo)[0]:.3f}, {ci(bo)[1]:.3f}]  geo-mean per-build {np.exp(lr.mean()):.3f} t-CI [{np.exp(t[0]):.3f}, {np.exp(t[1]):.3f}]  builds with ratio<1: {(pb<1).sum()}/24  solve diff {dm:+.4f} [{dci[0]:+.4f}, {dci[1]:+.4f}]")
        out[(a, b)] = (ratio, ci(bs), pb)
    return out

bc = [c for c in cells if SPLIT[c] in "BC"]
res = {}
res["B/C"] = report("B/C (primary)", bc)
res["A"] = report("A (positive control)", [c for c in cells if SPLIT[c] == "A"])
res["B"] = report("B", [c for c in cells if SPLIT[c] == "B"])
res["C"] = report("C", [c for c in cells if SPLIT[c] == "C"])
res["all"] = report("all 18", cells)
res["then"] = report("B/C learned then-pair (4)", learned_then)
res["other"] = report("B/C other then-pair (8)", [c for c in bc if c not in learned_then])

# per realization, B/C
print("\n== B/C per realization (R-perm/R-lib), 576 jobs per arm per realization")
ev = arr("evaluations", bc)
for k in range(3):
    pa = ev["R-perm"][:, :, k::3]; la = ev["R-lib"][:, :, k::3]; ta = ev["R-tree"][:, :, k::3]
    pb = pa.mean(axis=(1,2)) / la.mean(axis=(1,2))
    bo = pa.mean(axis=(1,2))[builds].mean(1) / la.mean(axis=(1,2))[builds].mean(1)
    print(f"  realization {k}: R-perm {pa.mean():8.0f}  R-lib {la.mean():8.0f}  R-tree {ta.mean():8.0f}  ratio {pa.mean()/la.mean():.3f} build-boot [{ci(bo)[0]:.3f}, {ci(bo)[1]:.3f}]  builds<1 {(pb<1).sum()}/24")
# per repeat (same realization pairs)
print("  per repeat R-perm/R-lib:", [round(ev["R-perm"][:, :, r].mean()/ev["R-lib"][:, :, r].mean(), 3) for r in range(6)])

# per cell
print("\n== per cell (144 jobs/arm): split, then-pair, mean evals per arm, R-perm/R-lib, R-lib/R-tree, solves")
percell = []
for c in cells:
    e = {a: np.array([by[b, c, rp, a]["evaluations"] for b in range(24) for rp in range(6)], float) for a in ARMS}
    s = {a: sum(by[b, c, rp, a]["solved"] for b in range(24) for rp in range(6)) for a in ARMS}
    percell.append((SPLIT[c], c, THEN[c], e, s))
for sp, c, th, e, s in sorted(percell):
    print(f"  {sp} {c:34s} then={th} tree {e['R-tree'].mean():7.0f} lib {e['R-lib'].mean():7.0f} perm {e['R-perm'].mean():7.0f}  perm/lib {e['R-perm'].mean()/e['R-lib'].mean():.2f}  lib/tree {e['R-lib'].mean()/e['R-tree'].mean():.3f}  solves {s['R-tree']}/{s['R-lib']}/{s['R-perm']}")

# attempt-of-solve on B/C
print("\n== B/C attempt of solve (solved jobs) and first-attempt share")
for a in ARMS:
    rs = [r for r in rows if r["arm"] == a and SPLIT[r["cell"]] in "BC"]
    cnt = Counter(r["attempt_count"] for r in rs if r["solved"])
    print(f"  {a}: {dict(sorted(cnt.items()))}  first-attempt {cnt[1]}/{len(rs)} = {cnt[1]/len(rs):.3f}  unsolved {sum(not r['solved'] for r in rs)}")
print("== A attempt of solve")
for a in ARMS:
    rs = [r for r in rows if r["arm"] == a and SPLIT[r["cell"]] == "A"]
    cnt = Counter(r["attempt_count"] for r in rs if r["solved"])
    print(f"  {a}: {dict(sorted(cnt.items()))}  first-attempt {cnt[1]}/{len(rs)} = {cnt[1]/len(rs):.3f}  unsolved {sum(not r['solved'] for r in rs)}")

# median / distribution of evaluations on B/C
print("\n== B/C evaluations distribution per arm (median, p25, p75, p90, max)")
for a in ARMS:
    x = np.array([r["evaluations"] for r in rows if r["arm"] == a and SPLIT[r["cell"]] in "BC"])
    print(f"  {a}: median {np.median(x):.0f} p25 {np.percentile(x,25):.0f} p75 {np.percentile(x,75):.0f} p90 {np.percentile(x,90):.0f} max {x.max()}  share at 1st-attempt-cap or more (>65536) {(x>65536).mean():.3f}")

# library operator stats per arm (B/C)
print("\n== operator totals on B/C per arm")
for a in ARMS:
    tot = Counter()
    for r in rows:
        if r["arm"] == a and SPLIT[r["cell"]] in "BC":
            for at in r["attempts"]:
                for k, v in (at.get("operators") or {}).items():
                    if isinstance(v, (int, float)): tot[k] += v
    print(" ", a, dict(tot))

# timing
t = json.load(open(f"{S}/timing.json"))["search"]
print("\n== timing: jobs", t["jobs"], "wall", round(t["wall_seconds"]), "worker", round(t["worker_seconds"]), "concurrency", round(t["worker_seconds"]/t["wall_seconds"], 2))
print("per-arm worker seconds:", {a: round(sum(r["worker_seconds"] for r in rows if r["arm"] == a)) for a in ARMS})
json.dump({"percell": [(sp, c, str(th), {a: float(e[a].mean()) for a in ARMS}, s) for sp, c, th, e, s in percell],
           "perbuild_bc": {f"{a}/{b}": v[2].tolist() for (a, b), v in res["B/C"].items()},
           "perbuild_A": {f"{a}/{b}": v[2].tolist() for (a, b), v in res["A"].items()}},
          open("/Users/andreas/developer/folding-evolution/research/runs/2026-10-11-0524/analysis_recompute.json", "w"), indent=1)
