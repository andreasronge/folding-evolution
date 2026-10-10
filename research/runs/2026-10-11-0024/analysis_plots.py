import gzip, json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT="/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/"
REPO="/Users/andreas/developer/folding-evolution-research/2026-10-11-0024/"
TASK="/Users/andreas/developer/folding-evolution/research/runs/2026-10-11-0024/"
COL={"R-tree":"#2a78d6","R-A8":"#eb6834","F-A8":"#1baf7a"}
HIST={"tree":"#2a78d6","A8":"#eb6834"}
plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.color":"#e6e6e3","grid.linewidth":0.6})
def load(fam): return [json.loads(l) for l in open(OUT+f"2026-10-11-0024-{fam.lower()}/search.jsonl")]
def hist(fam): return [json.loads(l) for l in gzip.open(REPO+f"experiments/chem_tape/data/restart_gp_0024/{fam}.jsonl.gz","rt")]
xs=np.logspace(np.log10(256),np.log10(524288),400)
fig,axes=plt.subplots(1,2,figsize=(11,4.2))
for ax,fam in zip(axes,("DG","TS")):
    rows=load(fam); old=hist(fam)
    for arm in ("R-tree","R-A8","F-A8"):
        ev=np.array([r["evaluations"] for r in rows if r["arm"]==arm and r["solved"]]); n=sum(1 for r in rows if r["arm"]==arm)
        ax.plot(xs,[(ev<=x).sum()/n for x in xs],color=COL[arm],lw=2,label=f"{arm} (n={n})")
    for arm in ("tree","A8"):
        ev=np.array([r["evaluations"] for r in old if r["arm"]==arm and r["solved"]]); n=sum(1 for r in old if r["arm"]==arm)
        ax.plot(xs,[(ev<=x).sum()/n for x in xs],color=HIST[arm],lw=1.2,ls="--",label=f"2254 full-cap {arm} (n={n})")
    for k in range(1,9): ax.axvline(65536*k,color="#c3c2b7",lw=0.6,ls=":")
    ax.set_xscale("log"); ax.set_xlabel("evaluations spent by the job"); ax.set_ylabel("fraction of jobs solved"); ax.set_title(f"{fam}: D625-exact solves by expenditure"); ax.set_ylim(0,1.02); ax.legend(fontsize=8,loc="upper left")
fig.tight_layout(); fig.savefig(TASK+"analysis_solve_curves.png",dpi=130)

rows=load("DG"); old=hist("DG")
fig,axes=plt.subplots(1,2,figsize=(11,4.4))
ax=axes[0]
rt=[np.mean([r["evaluations"] for r in rows if r["arm"]=="R-tree" and r["build"]==b]) for b in range(24)]
ra=[np.mean([r["evaluations"] for r in rows if r["arm"]=="R-A8" and r["build"]==b]) for b in range(24)]
ax.scatter(ra,rt,s=40,color="#2a78d6",edgecolor="#fcfcfb",zorder=3)
for b in range(24):
    if b in (16,7,23,3): ax.annotate(f"build {b}",(ra[b],rt[b]),textcoords="offset points",xytext=(5,3),fontsize=8,color="#52514e")
m=max(max(ra),max(rt))*1.05; ax.plot([0,m],[0,m],color="#c3c2b7",lw=1); ax.set_xlim(0,m); ax.set_ylim(0,m)
ax.set_xlabel("R-A8 mean evaluations per job (32 jobs per build)"); ax.set_ylabel("R-tree mean evaluations per job (same seeds)"); ax.set_title("DG: paired per-build means; below the line = tree cheaper")
ax=axes[1]
order=sorted({r["cell"] for r in rows},key=lambda c: next(r["seeds"][0] for r in rows if r["cell"]==c and r["arm"]=="R-tree" and r["build"]==0 and r["repeat"]==0))
for i,arm in enumerate(("R-tree","R-A8","F-A8")):
    for j,c in enumerate(order):
        v=[np.mean([r["evaluations"] for r in rows if r["arm"]==arm and r["cell"]==c and r["build"]==b]) for b in range(24)]
        ax.scatter(np.full(24,j+(i-1)*0.25)+np.random.default_rng(j).uniform(-0.06,0.06,24),v,s=9,color=COL[arm],alpha=0.45)
        ax.plot([j+(i-1)*0.25-0.1,j+(i-1)*0.25+0.1],[np.mean(v)]*2,color=COL[arm],lw=2.5)
    ax.scatter([],[],color=COL[arm],label=arm)
ax.set_xticks(range(8)); ax.set_xticklabels([c.split(":")[1] for c in order],rotation=35,ha="right",fontsize=7)
ax.set_ylabel("mean evaluations per job (dots: builds, bar: cell mean)"); ax.set_title("DG: per-cell cost by arm"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(TASK+"analysis_builds_cells.png",dpi=130)
print("ok")
