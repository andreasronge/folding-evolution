import json, math, sys, collections
import numpy as np
OUT='/Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-0132-post-addition-map-learning'
TR=["PA:(S?M:m)+M","PA:(S?M:m)+S","PA:(S?m:M)+S","PA:(S?m:M)+m","PA:(S?m:S)+M","PA:(S?m:S)+m"]
HO=["PA:(S?M:S)+M","PA:(S?M:S)+m"]
rows=[]
with open(OUT+'/search.jsonl') as f:
    for line in f:
        r=json.loads(line)
        rows.append((r['phase'],r['arm'],r['cell'],r['seed'],r['cap'],r['solved'],r['evaluations'],r['shortcuts'],r['unique_shortcuts'],r['seconds']))
print("total rows",len(rows))
# phase counts
pc=collections.Counter(p.split(':')[0] for p,*_ in rows)
print("phase counts",dict(pc))
# duplicates
keys=collections.Counter((p,a,c,s) for p,a,c,s,*_ in rows)
dups=[k for k,v in keys.items() if v>1]
print("duplicate (phase,arm,cell,seed):",len(dups))
# learn seeds
learn=collections.defaultdict(set)
for p,a,c,s,*_ in rows:
    if p.startswith('learn:'):
        tid,g=p.split(':')[1],p.split(':')[2]
        learn[(tid,g)].add(s)
# shared across C/M/T same k,g; disjoint across (k,g)
ok_shared=all(learn[('C%d'%k,g)]==learn[('M%d'%k,g)]==learn[('T%d'%k,g)] for k in range(1,7) for g in ['g%d'%i for i in range(1,26)])
sets=[frozenset(learn[('C%d'%k,'g%d'%g)]) for k in range(1,7) for g in range(1,26)]
alls=set().union(*sets); print("learn seeds shared across learners:",ok_shared,"; disjoint across k,gen:",len(alls)==sum(len(s) for s in sets), "; n sets",len(sets), "sizes", set(len(s) for s in sets))
# learn rows per (tid,gen)
lc=collections.Counter((p.split(':')[1],p.split(':')[2]) for p,*_ in rows if p.startswith('learn:'))
print("learn rows per traj-gen: ",set(lc.values()), "n traj-gen", len(lc))
sc=collections.Counter(p.split(':')[1] for p,*_ in rows if p.startswith('selection:'))
print("selection rows per traj:",dict(sc))
# test
test=[r for r in rows if r[0].startswith('test:')]
tarms=sorted(set(r[1] for r in test))
print("test arms",len(tarms),tarms)
tseeds={}
for p,a,c,s,*_ in test: tseeds.setdefault((a,c),set()).add(s)
tr_seeds=set(range(132300000,132300050)); ho_seeds=set(range(132300000,132300100))
bad=[(a,c) for (a,c),ss in tseeds.items() if ss!=(tr_seeds if c in TR else ho_seeds)]
print("test (arm,cell) with wrong seed set:",bad)
print("test cells per arm:",{a:len([c for (aa,c) in tseeds if aa==a]) for a in tarms})
# per map per cell costs
def lc_(solved,ev,cap): return math.log2(ev) if solved and ev<=cap else math.log2(2*cap)
by=collections.defaultdict(list)
for p,a,c,s,cap,solved,ev,sh,ush,sec in test: by[(a,c)].append((s,solved,ev,sh,ush,sec))
percell={}
for (a,c),lst in by.items():
    lst.sort()
    ev=np.array([e if so else np.inf for s,so,e,*_ in lst])
    n=len(lst)
    med=float(np.median(ev)) if np.isfinite(np.median(ev)) else None
    percell[f"{a}|{c}"]=dict(n=n,solved524=int(sum(1 for s,so,e,*_ in lst if so and e<=524288)),solved65=int(sum(1 for s,so,e,*_ in lst if so and e<=65536)),
        cost524=float(np.mean([lc_(so,e,524288) for s,so,e,*_ in lst])),cost65=float(np.mean([lc_(so,e,65536) for s,so,e,*_ in lst])),
        km_median=med, shortcuts_mean=float(np.mean([sh for *_,sh,ush,sec in lst])), unique_shortcuts_mean=float(np.mean([ush for *_,sh,ush,sec in lst])), seconds_mean=float(np.mean([sec for *_,sec in lst])))
# matrices for contrasts: arm -> cell -> seed-ordered cost array
def mat(arm,cells,cap):
    return np.array([[lc_(so,e,cap) for s,so,e,*_ in sorted(by[(arm,c)])] for c in cells])
fam={'C':[f'C{k}' for k in range(1,7)],'M':[f'M{k}' for k in range(1,7)],'T':[f'T{k}' for k in range(1,7)],'C-marg':[f'C-marg{k}' for k in range(1,7)],'G':['G'],'G-marg':['G-marg'],'U':['U'],'F':['F']}
rng=np.random.default_rng(7)
def contrast(A,B,cells,cap,reps=4000):
    a=np.stack([mat(x,cells,cap) for x in fam[A]]); b=np.stack([mat(x,cells,cap) for x in fam[B]])
    point=b.mean()-a.mean()
    per_traj=(b.mean((1,2)) if len(b)>1 else np.repeat(b.mean(),len(a))) - a.mean((1,2))
    boot=[]
    n=max(len(a),len(b)); nseed=a.shape[2]
    for _ in range(reps):
        bl=rng.integers(n,size=n)
        aa=a[bl] if len(a)>1 else a; bb=b[bl] if len(b)>1 else b
        idx=rng.integers(nseed,size=nseed)  # same seeds for all cells (joint)
        boot.append(bb[:,:,idx].mean()-aa[:,:,idx].mean())
    lo,hi=np.quantile(boot,[0.025,0.975])
    return dict(ratio=float(2**point),lo=float(2**lo),hi=float(2**hi),per_traj_ratio=[float(2**d) for d in per_traj],per_traj_sd_log2=float(np.std(per_traj,ddof=1)) if len(per_traj)>1 else None)
contrasts={}
for lab,cells in [('training',TR),('holdout0',[HO[0]]),('holdout1',[HO[1]])]:
    for cap in ([65536,524288] if lab=='training' else [524288]):
        for A,B in [('C','G'),('M','G'),('T','G-marg'),('T','G'),('C','M'),('C','C-marg'),('M','C-marg'),('C-marg','G-marg'),('G','G-marg'),('G','U'),('G','F')]:
            if (A in ('U','F') or B in ('U','F')) and lab=='training': continue
            contrasts[f"{lab}{cap//1000}:{A}/{B}"]=contrast(A,B,cells,cap)
# pooled holdout solve fraction curve per family
budgets=[2**i for i in range(8,20)]
curves={}
for Fm,arms in fam.items():
    evs=[e if so else np.inf for arm in arms for c in HO for s,so,e,*_ in by.get((arm,c),[])]
    if evs: curves[Fm]=[float(np.mean([e<=b for e in evs])) for b in budgets]
# calibration/repeatability/benchmark counts
rep={p:len([1 for r in rows if r[0]==p]) for p in set(r[0] for r in rows if r[0].startswith('repeatability'))}
calib=collections.Counter(r[0] for r in rows if r[0].startswith('calibration'))
bench=collections.Counter(r[0] for r in rows if r[0].startswith('bench') or r[0].startswith('stage') or r[0].startswith('timing'))
other=collections.Counter(r[0].split(':')[0] for r in rows if not any(r[0].startswith(x) for x in ('learn:','test:','selection:','repeatability','calibration')))
print("repeatability",rep,"calibration n",sum(calib.values()),"other phases",dict(other))
# total evaluations
print("total inner evaluations",sum(r[6] for r in rows))
json.dump(dict(percell=percell,contrasts=contrasts,curves=curves,budgets=budgets,phase_counts=dict(pc),n_rows=len(rows),dups=len(dups)),open('/Users/andreas/developer/folding-evolution/research/runs/2026-10-06-0132/analysis_tmp/scan.json','w'),indent=1)
print("done")
