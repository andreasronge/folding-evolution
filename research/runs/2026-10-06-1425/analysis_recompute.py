"""Independent recomputation for the 1425 analysis (reviewer)."""
import json, collections, math, sys
import numpy as np
from scipy.stats import t as tdist
O='/Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-1425-saved-map-shape-shift'
P='/Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-0811-contextual-continuation'
rows=[json.loads(l) for l in open(O+'/search.jsonl')]
print('rows',len(rows))
keys=collections.Counter((r['arm'],r['cell'],r['seed']) for r in rows)
print('unique keys',len(keys),'dups',sum(1 for k,v in keys.items() if v>1))
arms=sorted({r['arm'] for r in rows}); cells=sorted({r['cell'] for r in rows})
print('arms',len(arms),'cells',len(cells))
seeds=sorted({r['seed'] for r in rows}); print('seeds',len(seeds),min(seeds),max(seeds))
cnt=collections.Counter((r['arm'],r['cell']) for r in rows)
bad=[(k,v) for k,v in cnt.items() if v!=200]; print('cells not 200:',bad)
print('caps',collections.Counter(r['cap'] for r in rows),'pop',collections.Counter(r['pop_size'] for r in rows))
# cost check
mism=sum(1 for r in rows if abs(r['log2_cost']-(math.log2(r['evaluations']) if r['solved'] else 20.0))>1e-9)
print('cost mismatches',mism)
print('shortcut rows',sum(1 for r in rows if r['shortcuts']),'max shortcuts',max(r['shortcuts'] for r in rows))
BE=[c for c in cells if c.startswith('BE')]; LIN=[c for c in cells if not c.startswith('BE')]
print('BE',BE); print('LIN',LIN)
# per arm-cell cost and solved
cost={}; solved={}
by=collections.defaultdict(list)
for r in rows: by[(r['arm'],r['cell'])].append(r)
for k,v in by.items():
    cost[k]=np.mean([x['log2_cost'] for x in v]); solved[k]=sum(x['solved'] for x in v)
def fam(a):
    for f in ('R_fm','R_abl','M+','R'):
        if a.startswith(f): return f
    return a if a=='G' else 'M'
famsolve=collections.defaultdict(lambda:[0,0])
for k,v in by.items():
    f=fam(k[0]); famsolve[(f,k[1])][0]+=solved[k]; famsolve[(f,k[1])][1]+=len(v)
print('\nSolved by family x cell:')
for f in ('G','M','M+','R','R_abl','R_fm'):
    print(f, {c.split(':')[1]:f"{famsolve[(f,c)][0]}/{famsolve[(f,c)][1]}" for c in cells})
unsolved_maps=collections.Counter()
for k,v in by.items():
    if solved[k]<200: unsolved_maps[k]=200-solved[k]
print('unsolved by (map,cell):',sorted(unsolved_maps.items(), key=lambda x:-x[1])[:20])
grp={a:dict(BE=np.mean([cost[(a,c)] for c in BE]),LIN=np.mean([cost[(a,c)] for c in LIN])) for a in arms}
res=json.load(open(O+'/result.json'))
md=max(abs(grp[a][g]-res['group_costs'][a][g]) for a in arms for g in ('BE','LIN'))
print('max group cost diff vs result.json',md)
# contrasts
def contrast(x,y,g): return grp[y][g]-grp[x][g]  # positive => x faster
pairs=[f'{i}{s}' for i in range(1,7) for s in 'ab']
C={}
for p in pairs:
    for lab,(x,y) in {'R/M+':('R','M+'),'R/R_fm':('R','R_fm'),'R/R_abl':('R','R_abl'),'R_fm/M+':('R_fm','M+')}.items():
        be=contrast(x+p,y+p,'BE'); lin=contrast(x+p,y+p,'LIN'); C[(p,lab)]=dict(BE=be,LIN=lin,shift=be-lin)
def ival(v):
    v=np.array(v); m=v.mean(); h=tdist.ppf(0.975,5)*v.std(ddof=1)/math.sqrt(6)
    return m,2**m,2**(m-h),2**(m+h)
print('\nLayer tables (ratio [95% t df5])')
for layer in ('b','a','pooled'):
    for lab in ('R/M+','R/R_fm','R/R_abl','R_fm/M+'):
        out=[]
        for g in ('BE','LIN','shift'):
            if layer=='pooled': v=[(C[(f'{i}a',lab)][g]+C[(f'{i}b',lab)][g])/2 for i in range(1,7)]
            else: v=[C[(f'{i}{layer}',lab)][g] for i in range(1,7)]
            m,r,lo,hi=ival(v); out.append(f"{g} {r:.3f} [{lo:.3f},{hi:.3f}] n>0={sum(x>0 for x in v)}/6")
        print(layer,lab,' | '.join(out))
print('\nPer-start R/M+ log2 (BE, LIN, shift):')
for p in pairs: c=C[(p,'R/M+')]; print(p, f"{c['BE']:+.3f} {c['LIN']:+.3f} {c['shift']:+.3f}")
print('\nPer-start R/R_fm log2 (BE, LIN, shift):')
for p in pairs: c=C[(p,'R/R_fm')]; print(p, f"{c['BE']:+.3f} {c['LIN']:+.3f} {c['shift']:+.3f}")
print('\nPer-start R/R_abl log2 (BE, LIN, shift):')
for p in pairs: c=C[(p,'R/R_abl')]; print(p, f"{c['BE']:+.3f} {c['LIN']:+.3f} {c['shift']:+.3f}")
# per cell R/M+ for b and a
print('\nPer-cell mean log2 R/M+ across 6 starts (b | a):')
for c in cells:
    vb=[cost[('M+'+f'{i}b',c)]-cost[('R'+f'{i}b',c)] for i in range(1,7)]
    va=[cost[('M+'+f'{i}a',c)]-cost[('R'+f'{i}a',c)] for i in range(1,7)]
    print(c, f"b {np.mean(vb):+.3f} (n>0 {sum(x>0 for x in vb)}/6) | a {np.mean(va):+.3f} (n>0 {sum(x>0 for x in va)}/6)")
# G and M/G
print('\nG per cell cost/solved:',{c:(round(cost[('G',c)],3),solved[('G',c)]) for c in cells})
print('G BE/LIN',grp['G'])
print('M1-6 BE/LIN:',{a:(round(grp[a]['BE'],3),round(grp[a]['LIN'],3)) for a in ['M%d'%i for i in range(1,7)]})
print('M+ b BE/LIN:',{a:(round(grp[a]['BE'],3),round(grp[a]['LIN'],3)) for a in ['M+%db'%i for i in range(1,7)]})
print('R b BE/LIN:',{a:(round(grp[a]['BE'],3),round(grp[a]['LIN'],3)) for a in ['R%db'%i for i in range(1,7)]})
# a maps: 0811 vs fresh seeds comparison
prow=[json.loads(l) for l in open(P+'/search.jsonl')]
pcells=set(cells)
pby=collections.defaultdict(list)
for r in prow:
    if r['cell'] in pcells: pby[(r['arm'],r['cell'])].append(r['log2_cost'] if 'log2_cost' in r else (math.log2(r['evaluations']) if r['solved'] else 20.0))
print('\n0811 arms on these cells:',sorted({k[0] for k in pby}), 'n per arm-cell', collections.Counter(len(v) for v in pby.values()))
pc={k:np.mean(v) for k,v in pby.items()}
def pgrp(a): return dict(BE=np.mean([pc[(a,c)] for c in BE]),LIN=np.mean([pc[(a,c)] for c in LIN]))
print('0811 per-start a R/M+ log2 (BE,LIN,shift) vs fresh-seed a:')
old=[];new=[]
for i in range(1,7):
    p=f'{i}a'
    try:
        gR=pgrp('R'+p); gM=pgrp('M+'+p)
        be=gM['BE']-gR['BE']; lin=gM['LIN']-gR['LIN']; old.append((be,lin,be-lin))
    except KeyError as e:
        print('missing',e); continue
    c=C[(p,'R/M+')]; new.append((c['BE'],c['LIN'],c['shift']))
    print(p, f"0811: {be:+.3f} {lin:+.3f} {be-lin:+.3f}   fresh: {c['BE']:+.3f} {c['LIN']:+.3f} {c['shift']:+.3f}")
if old:
    for j,g in enumerate(('BE','LIN','shift')):
        m,r,lo,hi=ival([o[j] for o in old]); m2,r2,lo2,hi2=ival([n[j] for n in new])
        print(g,'a on 0811 seeds',f"{r:.3f} [{lo:.3f},{hi:.3f}]",' a on fresh seeds',f"{r2:.3f} [{lo2:.3f},{hi2:.3f}]")
# seed-level SE of a per-map group cost
print('\nseed-level SE of map BE/LIN cost (sd of per-seed cell mean / sqrt(200)), example R1b:')
for a in ('R1b','M+1b','G'):
    for g,cs in (('BE',BE),('LIN',LIN)):
        per_seed=collections.defaultdict(list)
        for c in cs:
            for r in by[(a,c)]: per_seed[r['seed']].append(r['log2_cost'])
        v=np.array([np.mean(x) for x in per_seed.values()]); print(a,g,'sd',round(v.std(ddof=1),3),'se',round(v.std(ddof=1)/math.sqrt(200),3))
# censoring sensitivity: median-based group costs for R/M+ b
print('\nCensoring sensitivity, b-only R/M+ BE using medians of evaluations:')
def medcost(a,c): return np.median([r['log2_cost'] for r in by[(a,c)]])
vb=[np.mean([medcost('M+'+f'{i}b',c)-medcost('R'+f'{i}b',c) for c in BE]) for i in range(1,7)]
m,r,lo,hi=ival(vb); print('median BE R/M+ b',f"{r:.3f} [{lo:.3f},{hi:.3f}]")
vl=[np.mean([medcost('M+'+f'{i}b',c)-medcost('R'+f'{i}b',c) for c in LIN]) for i in range(1,7)]
m,r,lo,hi=ival(vl); print('median LIN R/M+ b',f"{r:.3f} [{lo:.3f},{hi:.3f}]")
json.dump(dict(C={f'{k[0]}|{k[1]}':v for k,v in C.items()}, grp=grp, old_a=old), open(sys.argv[1],'w')) if len(sys.argv)>1 else None
