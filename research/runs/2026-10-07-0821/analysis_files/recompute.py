"""Independent recomputation for 0821 analysis. Reads only raw run outputs."""
import json, sys, collections
import numpy as np
from scipy import stats
from pathlib import Path

OUT = Path("/Users/andreas/developer/folding-evolution/experiments/output/2026-10-07/2026-10-07-0821-rank-one-continuation")
TASK = Path("/Users/andreas/developer/folding-evolution/research/runs/2026-10-07-0821")
TRAIN = {"BE": ["BE:F?S:(M+m)","BE:F?m:(S+M)","BE:S?F:(M+m)","BE:S?M:(m+F)"],
         "PA": ["PA:(F?S:m)+M","PA:(F?m:M)+S","PA:(F?m:S)+M","PA:(S?M:F)+m","PA:(S?m:F)+M","PA:(S?m:M)+F"]}
cfg = json.load(open(OUT/"config.json"))

def lc(r, cap):
    return np.log2(r["evaluations"] if r["solved"] and r["evaluations"] <= cap else 2*cap)

print("=== 1. search.jsonl completeness")
phase_counts = collections.Counter(); keys = set(); dups = 0
learn_rows = collections.defaultdict(list)   # (pair, arm) -> list of (gen, seed, cell, lc)
sel_rows = collections.defaultdict(list)
cal_rows = []; fresh_rows = []
seed_cells_by_phase = collections.defaultdict(dict)
caps = collections.Counter()
with open(OUT/"search.jsonl") as f:
    for line in f:
        r = json.loads(line)
        k = (r["arm"], r["cell"], r["seed"])
        if k in keys: dups += 1
        keys.add(k)
        ph = r["phase"].split(":")[0]
        phase_counts[ph] += 1
        caps[(ph, r["cap"])] += 1
        small = dict(arm=r["arm"], cell=r["cell"], seed=r["seed"], solved=r["solved"], ev=r["evaluations"], sec=r["seconds"], cap=r["cap"], lc=lc(r, r["cap"]), th=r["table_hash"])
        if ph == "learn":
            tid, arm, g, i = r["arm"].split(":")
            learn_rows[(tid, arm)].append((int(g[1:]), int(i), r["seed"], r["cell"], small["lc"], r["solved"], r["seconds"]))
        elif ph == "selection":
            tid, arm, _, i = r["arm"].split(":")
            sel_rows[(tid, arm)].append((int(i), r["seed"], r["cell"], small["lc"], r["solved"], r["seconds"]))
        elif ph == "calibration":
            cal_rows.append(small)
        elif ph == "fresh":
            fresh_rows.append(small)
print("rows per phase:", dict(phase_counts), "total", sum(phase_counts.values()), "duplicate keys:", dups)
print("caps per phase:", dict(caps))
# per trajectory budget
bad = []
for (tid, arm), rows in sorted(learn_rows.items()):
    n_learn = len(rows); n_sel = len(sel_rows[(tid, arm)])
    gens = sorted(set(g for g, *_ in rows))
    if n_learn != 3840 or n_sel != 200 or gens != list(range(20)): bad.append((tid, arm, n_learn, n_sel, len(gens)))
print("trajectories:", len(learn_rows), "with wrong budgets:", bad)
# shared seeds between T and C in learning: for each pair, gen, cand index -> seeds set identical
mismatch = 0
for tid in sorted({t for t, _ in learn_rows}):
    for arm_rows in [learn_rows[(tid, "T")], learn_rows[(tid, "C")]]:
        pass
    sT = {(g, r[2], r[3]) for r in learn_rows[(tid, "T")] for g in [r[0]]}
    sC = {(g, r[2], r[3]) for r in learn_rows[(tid, "C")] for g in [r[0]]}
    if sT != sC: mismatch += 1
print("pairs with T/C seed-cell mismatch in learning:", mismatch)
# Seeds disjoint across phases?
# (quick check: seed ranges)
print("fresh rows", len(fresh_rows), "cal rows", len(cal_rows))

print("\n=== 2. fresh scoring recompute")
cap = cfg["fresh_cap"]; seeds = cfg["fresh_seeds"]
look = {(r["arm"], r["cell"], r["seed"]): r for r in fresh_rows}
assert len(look) == len(fresh_rows)
pairs = [f"{f}{k}" for k in range(1, 9) for f in ("BE", "PA")]
exp = {("G4", c, s) for c in sum(TRAIN.values(), []) for s in seeds}
for tid in pairs:
    exp |= {(f"{tid}:{m}", c, s) for m in ("S","T","C","C0") for c in TRAIN[tid[:2]] for s in seeds}
print("expected fresh keys", len(exp), "observed", len(look), "missing", len(exp - set(look)), "extra", len(set(look) - exp))
# shared seeds -> same training cases? we checked in run; check table hashes unique per map
fm = json.load(open(OUT/"fresh_maps.json"))
hash_ok = all(look[k]["th"] == fm[k[0]]["table_hash"] for k in look)
print("fresh table hashes match fresh_maps.json:", hash_ok)
# identical maps? (e.g. C==C0 if residual zero, T==S)
hs = {k: v["table_hash"] for k, v in fm.items()}
same = [(a, b) for a in hs for b in hs if a < b and hs[a] == hs[b]]
print("identical fresh maps:", same)

def arm_cost(name, cells):
    return np.array([[look[(name, c, s)]["lc"] for s in seeds] for c in cells])  # cells x seeds
def solve_frac(name, cells):
    return np.mean([[look[(name, c, s)]["solved"] for s in seeds] for c in cells])

contr = {"C/T": ("T","C"), "T/S": ("S","T"), "C/S": ("S","C"), "C/C0": ("C0","C"), "C0/T": ("T","C0")}
pv = {k: {} for k in contr}
percell = {k: {} for k in contr}
for tid in pairs:
    cells = TRAIN[tid[:2]]
    for k, (num, den) in contr.items():
        d = arm_cost(f"{tid}:{num}", cells) - arm_cost(f"{tid}:{den}", cells)
        pv[k][tid] = d.mean()
        for ci, c in enumerate(cells):
            percell[k].setdefault(c, []).append(d[ci].mean())

def balanced(vals):
    x = np.array([vals[t] for t in pairs if t.startswith("BE")]); y = np.array([vals[t] for t in pairs if t.startswith("PA")])
    m = (x.mean() + y.mean())/2
    se = 0.5*np.sqrt(x.var(ddof=1)/len(x) + y.var(ddof=1)/len(y)); df = len(x)+len(y)-2
    w = stats.t.ppf(0.975, df)*se
    return m, se, w, 2**m, 2**(m-w), 2**(m+w), x, y

print("\ncontrast | ratio [95%] | log2 mean ± half | BE ratio [CI] | PA ratio [CI] | pooled sd | sign + / n | Wilcoxon p")
for k in contr:
    m, se, w, r, lo, hi, x, y = balanced(pv[k])
    def fam(z):
        mm = z.mean(); ww = stats.t.ppf(0.975, len(z)-1)*z.std(ddof=1)/np.sqrt(len(z)); return f"{2**mm:.3f} [{2**(mm-ww):.3f}, {2**(mm+ww):.3f}]"
    allv = np.r_[x, y]
    wp = stats.wilcoxon(allv).pvalue
    print(f"{k:5s} | {r:.3f} [{lo:.3f}, {hi:.3f}] | {m:+.3f} ± {w:.3f} | {fam(x)} | {fam(y)} | sd {allv.std(ddof=1):.3f} | {(allv>0).sum()}/{len(allv)} | {wp:.3f}")

print("\nper-pair log2 contrasts:")
print("pair  " + "  ".join(f"{k:>7s}" for k in contr))
for tid in pairs:
    print(f"{tid:5s} " + "  ".join(f"{pv[k][tid]:+7.3f}" for k in contr))

print("\nper-cell mean log2 contrast (over 8 pairs of family), C/T and T/S, C/S:")
for c in sum(TRAIN.values(), []):
    print(f"{c:16s} C/T {np.mean(percell['C/T'][c]):+.3f} (sd {np.std(percell['C/T'][c], ddof=1):.3f})  T/S {np.mean(percell['T/S'][c]):+.3f}  C/S {np.mean(percell['C/S'][c]):+.3f}  C/C0 {np.mean(percell['C/C0'][c]):+.3f}")

print("\nabsolute fresh mean log2 cost per map (own cells) and solve fraction; G4 anchor by family")
g4 = {f: arm_cost("G4", TRAIN[f]).mean() for f in TRAIN}
g4sf = {f: solve_frac("G4", TRAIN[f]) for f in TRAIN}
print("G4:", {f: f"{g4[f]:.3f} (solve {g4sf[f]:.3f})" for f in TRAIN})
rows = []
for tid in pairs:
    cells = TRAIN[tid[:2]]
    vals = {m: arm_cost(f"{tid}:{m}", cells).mean() for m in ("S","T","C","C0")}
    sfs = {m: solve_frac(f"{tid}:{m}", cells) for m in ("S","T","C","C0")}
    rows.append((tid, vals, sfs))
    print(f"{tid:5s} " + " ".join(f"{m} {vals[m]:.3f}({sfs[m]:.3f})" for m in vals) + f"  S/G4 {2**(g4[tid[:2]]-vals['S']):.2f}x")
for f in TRAIN:
    fr = [r for r in rows if r[0].startswith(f)]
    for m in ("S","T","C","C0"):
        print(f"  {f} {m}: mean log2 {np.mean([r[1][m] for r in fr]):.3f}, vs G4 {2**(g4[f]-np.mean([r[1][m] for r in fr])):.2f}x, solve {np.mean([r[2][m] for r in fr]):.4f}")
unsolved = sum(1 for r in fresh_rows if not r["solved"]); print("fresh unsolved total:", unsolved, "/", len(fresh_rows))
by_map_unsolved = collections.Counter(r["arm"].split(":")[-1] for r in fresh_rows if not r["solved"]); print("fresh unsolved by map type:", dict(by_map_unsolved))

print("\n=== 3. in-loop final-selection comparison (shared seeds, 65k cap; 2 parents x 100 per arm)")
traj = json.load(open(OUT/"trajectories.json"))
inl = {}
for tid in pairs:
    best = {}
    for arm in ("T","C"):
        rs = sel_rows[(tid, arm)]
        i = traj[f"{tid}:{arm}"]["selected_parent"]
        d = {(s, c): l for ii, s, c, l, *_ in rs if ii == i}
        best[arm] = d
    ks = sorted(best["T"]); dd = np.array([best["T"][k] - best["C"][k] for k in ks])
    inl[tid] = dd.mean()
m, se, w, r, lo, hi, x, y = balanced(inl)
print(f"in-loop selected-parent C/T (paired seeds, selection-biased): ratio {r:.3f} [{lo:.3f}, {hi:.3f}]; per pair:", {t: round(v, 3) for t, v in inl.items()})
# selected_score fresh agreement
for arm in ("T","C"):
    xs = [traj[f"{t}:{arm}"]["selected_score"] for t in pairs]
    ys = [arm_cost(f"{t}:{arm}", TRAIN[t[:2]]).mean() for t in pairs]
    print(f"  {arm}: in-loop selected score vs fresh cost: spearman {stats.spearmanr(xs, ys).statistic:.3f}; mean in-loop {np.mean(xs):.3f} vs fresh {np.mean(ys):.3f} (in-loop optimistic by {np.mean(ys)-np.mean(xs):+.3f} log2)")

print("\n=== 4. in-loop learning curves (parents' mean score per generation; includes rescoring)")
gens = [json.loads(l) for l in open(OUT/"generations.jsonl")]
print("generation records:", len(gens), "(expect 16*2*20 =", 16*2*20, ")")
curve = {}
for g in gens:
    sc = np.array(g["scores"]); par = sc[:2].mean(); best = sc.min(); childbest = sc[2:].min()
    curve[(g["start"], g["arm"], g["generation"])] = (par, best, childbest, sc[:2].min())
for f in TRAIN:
    for arm in ("T","C"):
        line = [np.mean([curve[(t, arm, gg)][0] for t in pairs if t.startswith(f)]) for gg in range(20)]
        print(f"{f} {arm} parents-mean by gen: " + " ".join(f"{v:.2f}" for v in line))
# child acceptance: fraction of generations where best child beats both parents
acc = collections.Counter(); tot = collections.Counter()
for g in gens:
    sc = np.array(g["scores"]); tot[g["arm"]] += 1
    if sc[2:].min() < sc[:2].min(): acc[g["arm"]] += 1
print("generations where a child beat both parents (in-loop, noisy):", {a: f"{acc[a]}/{tot[a]}" for a in tot})
# gen-0 parents are identical: check T and C gen0 parent scores equal
g0 = [(g["start"], g["arm"], g["scores"][:2]) for g in gens if g["generation"] == 0]
d0 = {}
for s, a, sc in g0: d0.setdefault(s, {})[a] = sc
print("gen0 T==C parent scores for all pairs:", all(np.allclose(v["T"], v["C"]) for v in d0.values()))
# per-step surviving operators from mutations: survived counts by operator in C
mix = collections.Counter(); surv = collections.Counter()
for g in gens:
    for i, mu in enumerate(g["mutations"]):
        mix[(g["arm"], mu["operator"])] += 1
        if (i + 2) in g["selected_indices"]: surv[(g["arm"], mu["operator"])] += 1
print("proposed/survived by arm,operator:", {f"{k[0]}:{k[1]}": f"{surv[k]}/{mix[k]} = {surv[k]/mix[k]:.3f}" for k in sorted(mix)})

print("\n=== 5. final map diagnostics (C arm)")
for tid in pairs:
    d = traj[f"{tid}:C"]["diagnostics"]; dt = traj[f"{tid}:T"]["diagnostics"]
    print(f"{tid:5s} C: residual_rms {d['residual_rms']:.3f} resid_table_l1 {d['residual_table_l1']:.4f} total_l1 {d['total_table_l1']:.3f} clips {d['clipped_elements']} | T total_l1 {dt['total_table_l1']:.3f} | C vec b-norm {np.linalg.norm(np.array(traj[f'{tid}:C']['vector'])[49:]):.3f}")
print("mean |post-clipping column means| across C finals:", np.mean([np.mean(np.abs(traj[f'{t}:C']['diagnostics']['post_clipping_column_means'])) for t in pairs]))

print("\n=== 6. calibration recompute")
units = json.load(open(OUT/"calibration_units.json"))
print("units:", len(units), [u["id"] for u in units])
print("mutants per unit:", sorted(set(len(u["effects"]) for u in units)))
cal_n = collections.Counter(r["arm"].rsplit(":", 1)[0] for r in cal_rows)
print("calibration rows per mutant/parent-block: counts of counts:", collections.Counter(cal_n.values()))
def point(us):
    cov = np.mean([np.cov(np.array(u["effects"])[:, :2], rowvar=False, ddof=1)[0, 1] for u in us])
    mu = np.mean([np.mean(np.array(u["effects"])[:, :2]) for u in us])
    v = np.mean([np.mean(u["variances"]) for u in us])
    return cov, mu, v
def gamma(cov, mu, v):
    var = max(0, cov); out = {}
    for n in (24, 48):
        den = np.sqrt(var + 2*v/n); out[n] = max(0, 1.27*var/den - mu)/n
    return out
rng = np.random.default_rng(7)
for op in ("context", "token"):
    us = [u for u in units if u["operator"] == op]
    cov, mu, v = point(us); print(f"{op}: cov {cov:.4f} mu {mu:.4f} v {v:.3f} gamma {gamma(cov, mu, v)}")
    # correlation A vs B of deltas within unit
    allA = np.concatenate([np.array(u["effects"])[:, 0] - np.mean(np.array(u["effects"])[:, 0]) for u in us])
    allB = np.concatenate([np.array(u["effects"])[:, 1] - np.mean(np.array(u["effects"])[:, 1]) for u in us])
    print(f"   within-unit-centred corr(ΔA, ΔB) = {np.corrcoef(allA, allB)[0,1]:.3f}, n mutants {len(allA)}; sd ΔA {allA.std():.3f}; expected noise sd of a 48-search block mean = {np.sqrt(v/48):.3f}")
    # reliability: true variance / observed variance
    print(f"   true-effect variance share of observed Δ variance: {cov/ allA.var():.2f}")
    # fraction of mutants with Δ<0 on both blocks
    E = np.concatenate([np.array(u["effects"])[:, :2] for u in us])
    print(f"   mutants with mean(ΔA,ΔB) < 0: {(E.mean(1) < 0).sum()}/{len(E)}; < -0.1: {(E.mean(1) < -0.1).sum()}; quantiles of mean Δ: {np.round(np.quantile(E.mean(1), [0.1, 0.25, 0.5, 0.75, 0.9]), 3)}")
    if op == "context":
        # bootstrap stability of n choice
        choose48 = 0; B = 2000
        for _ in range(B):
            rs = []
            for u in us:
                e = np.array(u["effects"]); vv = np.array(u["variances"]); idx = rng.integers(len(e), size=len(e))
                rs.append(dict(effects=e[idx].tolist(), variances=vv[idx].tolist()))
            c2, m2, v2 = point(rs); g = gamma(c2, m2, v2)
            choose48 += g[48] > g[24]
        print(f"   bootstrap: fraction of replicates choosing n=48: {choose48/B:.3f}")
# token vs context: selected quarter on B after selecting on A, pooled over units (recompute)
for op in ("context", "token"):
    us = [u for u in units if u["operator"] == op]
    gains = []; abs_ = []
    for u in us:
        e = np.array(u["effects"]); k = len(e)//4; ch = np.argsort(e[:, 0], kind="stable")[:k]
        abs_.append(e[ch, 1].mean()); gains.append(e[ch, 1].mean() - e[:, 1].mean())
    print(f"{op}: selected-quarter (by ΔA, 48) mean ΔB = {np.mean(abs_):+.4f}; selected-minus-all = {np.mean(gains):+.4f}; per unit: {np.round(abs_, 3)}")

print("\n=== 7. timing/solve by phase")
st = json.load(open(OUT/"status.json"))
for ph, c in st["costs"].items():
    print(f"{ph}: searches {c['searches']}, solves {c['solves']} ({c['solves']/c['searches']:.3f}), s/search {c['worker_seconds']/c['searches']:.3f}")
print("pair wall seconds: mean", np.mean(st["pair_seconds"]), "max", max(st["pair_seconds"]), "sum", sum(st["pair_seconds"]))
# unsolved by arm in learning
for arm in ("T","C"):
    rs = [r for k, v in learn_rows.items() if k[1] == arm for r in v]
    print(f"learn {arm}: solve fraction {np.mean([r[5] for r in rs]):.4f} of {len(rs)}; s/search {np.mean([r[6] for r in rs]):.3f}")

json.dump(dict(pair_values={k: {t: float(v) for t, v in d.items()} for k, d in pv.items()}, inloop_ct={t: float(v) for t, v in inl.items()}), open(TASK/"analysis_files"/"recomputed.json", "w"), indent=1)

# ---------- plots
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
ax = axes[0]
for f, ls in (("BE", "-"), ("PA", "--")):
    for arm, col in (("T", "#1f77b4"), ("C", "#d62728")):
        line = [np.mean([curve[(t, arm, gg)][0] for t in pairs if t.startswith(f)]) for gg in range(20)]
        ax.plot(range(1, 21), line, ls, color=col, label=f"{f} {arm}")
ax.set(xlabel="generation", ylabel="mean of 2 parents' in-loop log2 cost (24 searches, 65k cap)", title="In-loop parent score (mean of 8 starts)")
ax.legend(fontsize=8)
ax = axes[1]
labels = list(contr); xs = np.arange(len(labels))
for i, k in enumerate(labels):
    m, se, w, r, lo, hi, x, y = balanced(pv[k])
    ax.errorbar(i, m, yerr=w, fmt="o", color="black", capsize=4)
    ax.scatter(np.full(len(x), i - 0.15), x, color="#1f77b4", s=14, alpha=0.7, label="BE pair" if i == 0 else None)
    ax.scatter(np.full(len(y), i + 0.15), y, color="#ff7f0e", s=14, alpha=0.7, label="PA pair" if i == 0 else None)
ax.axhline(0, color="grey", lw=0.8); ax.axhline(np.log2(1.15), color="grey", lw=0.8, ls=":")
ax.set_xticks(xs); ax.set_xticklabels(labels); ax.set(ylabel="log2 improvement (positive = numerator cheaper)", title="Fresh contrasts (mean, 95% t CI, per-pair dots)")
ax.legend(fontsize=8)
ax = axes[2]
for op, col in (("context", "#d62728"), ("token", "#1f77b4")):
    us = [u for u in units if u["operator"] == op]
    E = np.concatenate([np.array(u["effects"])[:, :2] for u in us])
    ax.scatter(E[:, 0], E[:, 1], s=12, alpha=0.6, color=col, label=f"{op} mutants (n={len(E)})")
lim = [-1.0, 1.2]; ax.plot(lim, lim, color="grey", lw=0.8); ax.axhline(0, color="grey", lw=0.5); ax.axvline(0, color="grey", lw=0.5)
ax.set(xlabel="Δ_A (mutant − parent, block A, 48 searches)", ylabel="Δ_B (independent block B)", title="Stage A single-step effects, blocks A vs B"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(TASK/"analysis_files"/"contrasts.png", dpi=130)
print("saved plot")
