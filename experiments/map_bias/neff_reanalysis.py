"""Seventeenth review reanalysis (notebook §28): evolution solve rates as a ratio to
blind sampling, from recorded first_exact_gen and Phase A P(exact). No new runs.
Ratio = -ln(1 - solved/n) / P(exact) / evaluations; 1 means equal to random sampling.
Run from the repo root: uv run python experiments/map_bias/neff_reanalysis.py"""
import json, math, glob, collections
rows=[]
for f in glob.glob('experiments/output/2026-10-01/pivot2_*/**/evolve.jsonl',recursive=True)+['experiments/output/2026-09-30/pivot_phase_b_L50/evolve.jsonl']:
    for l in open(f):
        r=json.loads(l); r.setdefault('tie','parents'); r.setdefault('k_weight',1.0); rows.append(r)
print(len(rows))
P={}
def load(m,suffix,k):
    for f in glob.glob(f'experiments/output/*/pivot*/sample_{m}_L50{suffix}.json'):
        d=json.load(open(f)); P[(m,k)]=({b['behaviour']:b['count'] for b in d['behaviours']},d['n'])
for m in('fold','direct'):
    load(m,'',1.0);load(m,'_k0.2',0.2);load(m,'_k5',5.0)
import sys
sys.path.insert(0,'experiments/map_bias'); sys.path.insert(0,'.')
import fold_direct as fd
def pex(task,m,k):
    c,n=P[(m,k)]
    tgt=fd.behaviour(fd.EXPECTED[task])
    return c.get(tgt,0)/n
cells=collections.defaultdict(list)
for r in rows:
    if r['L0']!=50: continue
    cells[(r['task'],r['map'],r['pop'],r['gens'],r['search'],r['tie'],r['k_weight'])].append(r)
tasks=[t for t in fd.EXPECTED if 'rest' in t or t=='count(products)' or t=='count(employees)']
print("task map pop tie k | P | solved/50 at gens G: evo(Neff/N) | random-pred")
for key in sorted(cells):
    task,m,pop,gens,search,tie,k=key
    if task not in tasks or search!='evolve': continue
    p=pex(task,m,k)
    if p==0: continue
    out=[]
    for G in (30,100,300,1000,2000):
        if G>gens: continue
        rs=cells[key]; s=sum(1 for r in rs if r['first_exact_gen'] is not None and r['first_exact_gen']<=G)
        N=pop*(G+1); n=len(rs)
        pred=1-math.exp(-N*p)
        if 0<s<n: ne=-math.log(1-s/n)/p/N; nes=f"{ne:.2f}"
        else: nes='-'
        out.append(f"G{G}:{s}/{n} x{nes} (rnd {pred*n:.0f})")
    print(task,m,pop,tie,k,f"P={p:.2e}",' | '.join(out))
