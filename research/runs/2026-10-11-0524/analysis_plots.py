import json, re
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
T = "/Users/andreas/developer/folding-evolution/research/runs/2026-10-11-0524"
S = "/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0524-score"
res = json.load(open(f"{S}/result.json")); rc = json.load(open(f"{T}/analysis_recompute.json"))
COL = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a"}  # validated categorical slots 1-3
INK, MUTED, GRID = "#222222", "#6b6b6b", "#e4e4e4"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
fig, axes = plt.subplots(1, 3, figsize=(14, 5.2), gridspec_kw=dict(width_ratios=[1.3, 1, 1]))

# Panel 1: per-cell R-perm/R-lib with 95% intervals, grouped by split
ax = axes[0]
cells = sorted(rc["percell"], key=lambda x: (x[0], x[1]))
ys = []
for i, (sp, c, th, m, s) in enumerate(cells):
    pc = res["per_cell"][c]["contrasts"]["R-perm/R-lib"]["evaluations"]
    lo, hi = pc["interval95"]; ax.plot([lo, hi], [i, i], color=COL[sp], lw=2, solid_capstyle="round")
    ax.plot(pc["point"], i, "o", color=COL[sp], ms=6, mec="white", mew=1)
    ys.append(c.replace("GS:", ""))
ax.set_yticks(range(len(ys))); ax.set_yticklabels(ys, fontsize=7.5); ax.invert_yaxis()
ax.set_xscale("log"); ax.set_xticks([0.5, 1, 1.25, 2, 4, 8]); ax.set_xticklabels(["0.5", "1", "1.25", "2", "4", "8"])
ax.axvline(1, color=MUTED, lw=1); ax.axvline(1.25, color=MUTED, lw=1, ls=":")
ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.set_xlabel("R-perm / R-lib, mean capped evaluations (95% paired bootstrap)")
ax.set_title("Per cell (144 jobs per arm): A = positive control, B/C = primary", loc="left", fontsize=9.5)
for sp in "ABC": ax.plot([], [], "o-", color=COL[sp], label=f"split {sp}")
ax.legend(frameon=False, loc="lower right", fontsize=8)
for s in ("top", "right"): ax.spines[s].set_visible(False)

# Panel 2: per-build B/C ratio, 24 builds, sorted; plus per-realization pooled ratio
ax = axes[1]
pb = np.array(rc["perbuild_bc"]["R-perm/R-lib"]); pa = np.array(rc["perbuild_A"]["R-perm/R-lib"])
order = np.argsort(pb)
ax.scatter(np.arange(24), pb[order], color=COL["B"], s=28, zorder=3, label="B/C (12 cells × 6 repeats)")
ax.scatter(np.arange(24), pa[order], color=COL["A"], s=28, zorder=3, marker="s", label="A (6 cells × 6 repeats)")
ax.axhline(1, color=MUTED, lw=1); ax.axhline(1.25, color=MUTED, lw=1, ls=":")
ax.set_yscale("log"); ax.set_yticks([0.5, 1, 1.25, 2, 4, 8, 16]); ax.set_yticklabels(["0.5", "1", "1.25", "2", "4", "8", "16"])
ax.set_xticks([]); ax.set_xlabel("24 builds, ordered by B/C ratio")
ax.set_ylabel("R-perm / R-lib per build")
ax.set_title(f"Per build: B/C below 1 in {(pb<1).sum()}/24; A above 1 in {(pa>1).sum()}/24", loc="left", fontsize=9.5)
ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True); ax.legend(frameon=False, fontsize=8, loc="upper left")
for s in ("top", "right"): ax.spines[s].set_visible(False)

# Panel 3: group means per arm with intervals (B/C and A)
ax = axes[2]
arms = ["R-tree", "R-lib", "R-perm"]; x = np.arange(3)
for j, (g, sp, off) in enumerate([("B/C", "B", -0.18), ("((0, 1), (2, 3))", "A", 0.18)]):
    m = res["groups"][g]["means"]["evaluations"]
    pts = [m[a]["point"] for a in arms]; lo = [m[a]["interval95"][0] for a in arms]; hi = [m[a]["interval95"][1] for a in arms]
    ax.bar(x + off, pts, width=0.34, color=COL[sp], label=("B/C (1,728 jobs/arm)" if sp == "B" else "A (864 jobs/arm)"))
    ax.errorbar(x + off, pts, yerr=[np.subtract(pts, lo), np.subtract(hi, pts)], fmt="none", ecolor=INK, elinewidth=1, capsize=2)
    for xi, p in zip(x + off, pts): ax.text(xi, p + 1500, f"{p/1000:.1f}k", ha="center", va="bottom", fontsize=7.5, color=INK)
ax.set_xticks(x); ax.set_xticklabels(arms); ax.set_ylabel("mean capped evaluations per job")
ax.set_title("Arm means (95% paired bootstrap)", loc="left", fontsize=9.5)
ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True); ax.legend(frameon=False, fontsize=8)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.suptitle("0524: label-rearranged (R-perm) vs intact (R-lib) tree libraries vs restarted tree GP (R-tree), gate-sum bank", x=0.01, ha="left", fontsize=10.5)
fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{T}/analysis_ratios.png", dpi=150)
print("saved")
