"""Independent re-analysis of 2026-10-11-2353 from score.jsonl (reviewer)."""
import json, sys
from collections import Counter, defaultdict
import numpy as np
OUT = "/Users/andreas/developer/folding-evolution/experiments/output/2026-10-12/"
rows = [json.loads(l) for l in open(OUT + "2026-10-11-2353-score/score.jsonl")]
smoke = [json.loads(l) for l in open("/Users/andreas/developer/folding-evolution/research/runs/2026-10-11-2353/smoke/score.jsonl")]
res = {}
# ---- completeness
res["n_rows"] = len(rows)
res["per_arm"] = dict(Counter(r["arm"] for r in rows))
keys = [(r["build"], r["cell"], r["repeat"], r["arm"]) for r in rows]
res["duplicate_keys"] = len(keys) - len(set(keys))
cells = sorted({r["cell"] for r in rows}); builds = sorted({r["build"] for r in rows})
res["n_cells"], res["n_builds"] = len(cells), len(builds)
exp = set()
for c in cells:
    for b in range(24):
        for rep in range(6):
            for a in ("R-all", "R-bind"): exp.add((b, c, rep, a))
        for a in ("R-tree", "R-gate"): exp.add((b, c, 0, a))
res["missing_keys"] = len(exp - set(keys)); res["extra_keys"] = len(set(keys) - exp)
# seeds
unit_seeds = defaultdict(set)
for r in rows: unit_seeds[(r["build"], r["cell"], r["repeat"])].add(tuple(r["seeds"]))
res["units_with_more_than_one_seed_tuple"] = sum(len(v) > 1 for v in unit_seeds.values())
all_seeds = [s for r in rows for s in r["seeds"]]
units_seed_sets = [tuple(sorted(next(iter(v)))) for v in unit_seeds.values()]
flat = [s for t in units_seed_sets for s in t]
res["seed_count_unique_vs_expected"] = (len(set(flat)), 24 * 24 * 6 * 8)
res["seed_range"] = (min(flat), max(flat))
smoke_seeds = {s for r in smoke for s in r["seeds"]}
res["overlap_with_smoke_seeds"] = len(smoke_seeds & set(flat))
# attempts structure
bad = 0
for r in rows:
    ev = sum(a["evaluations"] for a in r["attempts"])
    if ev != r["evaluations"] or r["evaluations"] > r["cap"] or r["evaluations"] % 256 or (not r["solved"] and r["evaluations"] != r["cap"]) or (r["solved"] != (r["solver"] is not None)) or len(r["attempts"]) > 8:
        bad += 1
res["rows_with_inconsistent_accounting"] = bad
res["failed_rows"] = sum(1 for r in rows if r.get("error"))
# ---- arrays
by = {(r["build"], r["cell"], r["repeat"], r["arm"]): r for r in rows}
def arr(arm, metric, reps):
    return np.array([[[by[b, c, k, arm][metric] for k in range(reps)] for c in cells] for b in range(24)], float)
E = {a: arr(a, "evaluations", 6) for a in ("R-all", "R-bind")}
E0 = {a: arr(a, "evaluations", 1) for a in ("R-tree", "R-gate")}
S = {a: arr(a, "solved", 6) for a in ("R-all", "R-bind")}
# arm summaries
summ = {}
for a in ("R-tree", "R-all", "R-bind", "R-gate"):
    rr = [r for r in rows if r["arm"] == a]
    ev = np.array([r["evaluations"] for r in rr])
    summ[a] = dict(jobs=len(rr), solves=sum(r["solved"] for r in rr), capped=sum(r["evaluations"] == r["cap"] for r in rr),
                   first_attempt=sum(len(r["attempts"]) == 1 and r["solved"] for r in rr),
                   mean_eval=float(ev.mean()), median_eval=float(np.median(ev)), p95=float(np.quantile(ev, .95)),
                   worker_s=float(np.mean([r["worker_seconds"] for r in rr])))
res["arms"] = summ
# ---- primary: pooled capped mean ratio with crossed bootstrap (own seed)
rng = np.random.default_rng(7)
D = 20000
bi = rng.integers(24, size=(D, 24)); ci = rng.integers(24, size=(D, 24))
def boot(a):
    m = a.mean(2)
    return m[bi[:, :, None], ci[:, None, :]].mean((1, 2))
def contrast(a, b):
    pt = a.mean() / b.mean(); s = boot(a) / boot(b)
    return dict(point=float(pt), ci=np.quantile(s, [.025, .975]).tolist(), log_halfwidth=float(np.diff(np.log(np.quantile(s, [.025, .975])))[0] / 2))
res["primary_R-bind/R-all"] = contrast(E["R-bind"], E["R-all"])
res["R-bind/R-all_repeat0_only"] = contrast(E["R-bind"][:, :, :1], E["R-all"][:, :, :1])
res["R-bind/R-tree_r0"] = contrast(E["R-bind"][:, :, :1], E0["R-tree"])
res["R-all/R-tree_r0"] = contrast(E["R-all"][:, :, :1], E0["R-tree"])
res["R-gate/R-bind_r0"] = contrast(E0["R-gate"], E["R-bind"][:, :, :1])
res["R-gate/R-all_r0"] = contrast(E0["R-gate"], E["R-all"][:, :, :1])
res["R-bind/R-all_all6_vs_Rtree_r0"] = contrast(E["R-bind"], E0["R-tree"])
# geometric / median versions (not pre-registered)
lr = np.log(E["R-bind"].mean(2)) - np.log(E["R-all"].mean(2))   # unit-level log ratio of means
res["unit_log_ratio"] = dict(mean=float(lr.mean()), median=float(np.median(lr)), sd=float(lr.std(ddof=1)),
                             units_bind_cheaper=int((lr < 0).sum()), units=lr.size)
res["geometric_mean_ratio_unit_means"] = float(np.exp(lr.mean()))
res["median_eval_ratio"] = float(np.median(E["R-bind"]) / np.median(E["R-all"]))
# solve rates
res["solve_rate"] = {a: (int(S[a].sum()), int(S[a].size)) for a in S}
# per build / per cell ratios
res["per_build_ratio"] = {int(b): float(E["R-bind"][b].mean() / E["R-all"][b].mean()) for b in range(24)}
res["per_cell_ratio"] = {c: float(E["R-bind"][:, i].mean() / E["R-all"][:, i].mean()) for i, c in enumerate(cells)}
# variance decomposition on log ratio: within-unit (seed) vs between-unit
# per unit, per repeat log(bind/all) using shared seeds
lr_rep = np.log(E["R-bind"]) - np.log(E["R-all"])  # (24,24,6)
within = lr_rep.var(2, ddof=1).mean()
between_units = lr_rep.mean(2).var(ddof=1)
res["log_ratio_variance"] = dict(within_unit_seed_var=float(within), var_of_unit_means=float(between_units),
                                 persistent_unit_var_est=float(between_units - within / 6),
                                 implied_sd_of_grand_mean_r6=float(np.sqrt(between_units / 576)),
                                 implied_sd_of_grand_mean_rinf=float(np.sqrt(max(between_units - within / 6, 0) / 576)))
# two-way: build and cell main effects of unit mean log ratio
u = lr_rep.mean(2)
gb = u.mean(1); gc = u.mean(0)
res["build_effect_sd"] = float(gb.std(ddof=1)); res["cell_effect_sd"] = float(gc.std(ddof=1))
resid = u - gb[:, None] - gc[None, :] + u.mean()
res["resid_sd"] = float(resid.std(ddof=1))
# strata by R-all needed helpers present
hd = json.load(open(OUT + "2026-10-11-2353-score/helper_draws.json"))
cov = {(h["build"], h["cell"]): h["arms"]["R-all"]["needed_helpers_present"] for h in hd}
covb = {(h["build"], h["cell"]): h["arms"]["R-bind"]["needed_helpers_present"] for h in hd}
res["R-bind_needed_present_dist"] = dict(Counter(covb.values()))
strata = {}
for n in range(4):
    idx = [(b, i) for b in range(24) for i, c in enumerate(cells) if cov[(b, c)] == n]
    if not idx: continue
    A = np.array([E["R-all"][b, i] for b, i in idx]); B = np.array([E["R-bind"][b, i] for b, i in idx])
    # unit bootstrap (units resampled; descriptive)
    rs = []
    for _ in range(4000):
        j = rng.integers(len(idx), size=len(idx)); rs.append(B[j].mean() / A[j].mean())
    strata[n] = dict(units=len(idx), ratio=float(B.mean() / A.mean()), unit_boot_ci=np.quantile(rs, [.025, .975]).tolist(),
                     R_all_mean=float(A.mean()), R_bind_mean=float(B.mean()),
                     R_all_solve=(int(S["R-all"][[b for b,_ in idx],[i for _,i in idx]].sum()), A.size),
                     R_bind_solve=(int(S["R-bind"][[b for b,_ in idx],[i for _,i in idx]].sum()), B.size))
res["strata_by_R_all_needed_helpers"] = strata
# needed-helper draw prob per arm (mean over units)
for a in ("R-all", "R-bind", "R-gate"):
    res["mean_needed_helper_draw_prob_" + a] = float(np.mean([h["arms"][a]["needed_helper_draw_probability"] for h in hd]))
# R-bind vs R-all per build: distinct behaviours and ratio
rv = json.load(open(OUT + "2026-10-11-2353-score/rebinding_validation.json"))
pb = {d["build"]: d for d in rv["per_build"]}
res["build_table"] = [dict(build=b, slots=pb[b]["arms"]["R-all"]["slots"], helper_slots=pb[b]["arms"]["R-all"]["helper_slots"],
                           distinct_bind=pb[b]["arms"]["R-bind"]["distinct_behaviours"], ratio=res["per_build_ratio"][b],
                           R_all_mean=float(E["R-all"][b].mean()), R_bind_mean=float(E["R-bind"][b].mean())) for b in range(24)]
hs = np.array([t["helper_slots"] / t["slots"] for t in res["build_table"]]); br = np.array([t["ratio"] for t in res["build_table"]])
res["corr_build_ratio_vs_helper_share"] = float(np.corrcoef(hs, np.log(br))[0, 1])
res["rebinding_validation_top"] = {k: v for k, v in rv.items() if k != "per_build" and len(json.dumps(v)) < 400}
json.dump(res, open("/Users/andreas/developer/folding-evolution/research/runs/2026-10-11-2353/reanalysis.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if k not in ("build_table", "per_cell_ratio", "per_build_ratio")}, indent=1, default=str))
print("per build:", {k: round(v, 3) for k, v in res["per_build_ratio"].items()})
print("per cell:", {k: round(v, 3) for k, v in res["per_cell_ratio"].items()})
