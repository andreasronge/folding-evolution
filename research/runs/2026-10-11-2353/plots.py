import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
T="/Users/andreas/developer/folding-evolution/research/runs/2026-10-11-2353/"
res=json.load(open(T+"reanalysis.json"))
BLUE,ORANGE,AQUA,TXT,MUT="#2a78d6","#eb6834","#1baf7a","#0b0b0b","#52514e"
plt.rcParams.update({"font.size":10,"axes.edgecolor":"#c9c8c3","axes.spines.top":False,"axes.spines.right":False,"text.color":TXT,"axes.labelcolor":TXT,"xtick.color":MUT,"ytick.color":MUT})
fig,axes=plt.subplots(1,3,figsize=(14,4.4),gridspec_kw=dict(width_ratios=[1,1.2,1.2]))
# (a) strata
ax=axes[0]; st=res["strata_by_R_all_needed_helpers"]
ns=sorted(int(k) for k in st); y=[st[str(n)]["ratio"] for n in ns]; lo=[st[str(n)]["unit_boot_ci"][0] for n in ns]; hi=[st[str(n)]["unit_boot_ci"][1] for n in ns]
ax.axhline(1,color="#c9c8c3",lw=1,zorder=0); ax.axhspan(0.85,0.90,color="#f0efec",zorder=0)
ax.errorbar(ns,y,yerr=[np.subtract(y,lo),np.subtract(hi,y)],fmt="o",color=BLUE,ms=7,capsize=3,lw=2)
p=res["primary_R-bind/R-all"]; ax.axhline(p["point"],color=ORANGE,lw=1.5,ls="--"); ax.text(3.05,p["point"]+0.015,"pooled 0.85",color=ORANGE,fontsize=9,ha="right")
for n,v in zip(ns,y): ax.text(n,hi[ns.index(n)]+0.03,f"{st[str(n)]['units']} units",ha="center",fontsize=8,color=MUT)
ax.set_xticks(ns); ax.set_xlabel("needed helpers present in R-all library (per build x cell)"); ax.set_ylabel("R-bind / R-all capped mean evaluations")
ax.set_title("(a) Saving by R-all coverage stratum\n(descriptive; unit bootstrap 95%)",fontsize=10,loc="left"); ax.set_ylim(0.5,1.75)
# (b) per build
ax=axes[1]; pb=res["per_build_ratio"]; b=sorted(int(k) for k in pb); v=[pb[str(k)] for k in b]
ax.axhline(1,color="#c9c8c3",lw=1); ax.axhspan(0.85,0.90,color="#f0efec",zorder=0)
ax.bar(b,v,color=BLUE,width=0.7); ax.axhline(p["point"],color=ORANGE,lw=1.5,ls="--")
ax.set_xlabel("library build (24 cells x 6 repeats each)"); ax.set_ylabel("R-bind / R-all"); ax.set_ylim(0.5,1.1); ax.set_xticks(b[::2])
ax.set_title("(b) Ratio per build",fontsize=10,loc="left")
# (c) per cell
ax=axes[2]; pc=res["per_cell_ratio"]; cells=sorted(pc,key=lambda c:pc[c]); v=[pc[c] for c in cells]
ax.axvline(1,color="#c9c8c3",lw=1); ax.axvspan(0.85,0.90,color="#f0efec",zorder=0)
ax.barh(range(len(cells)),v,color=AQUA,height=0.7); ax.axvline(p["point"],color=ORANGE,lw=1.5,ls="--")
ax.set_yticks(range(len(cells))); ax.set_yticklabels([c[2:] for c in cells],fontsize=7); ax.set_xlim(0.5,1.3)
ax.set_xlabel("R-bind / R-all (24 builds x 6 repeats each)"); ax.set_title("(c) Ratio per cell",fontsize=10,loc="left")
fig.suptitle("2026-10-11-2353: R-bind vs R-all, pooled 0.853 [0.785, 0.927]; grey band = 0.85-0.90 decision gap",fontsize=10,x=0.01,ha="left")
fig.tight_layout(); fig.savefig(T+"ratios.png",dpi=130)
