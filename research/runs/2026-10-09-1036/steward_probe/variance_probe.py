# Read-only: variance components of paired log-cost contrasts in 0843 rows, projected to reuse designs.
import json, math, sys, collections, random
import numpy as np
from scipy import stats
rows=[json.loads(l) for l in open(sys.argv[1])]
rows=[r for r in rows if r.get('phase')=='training']
k=[x for x in rows[0] if 'corpus' in x or 'family' in x]; print('keys',k)
cost=lambda r: r['evaluations'] if r['solved'] else 2*r['cap']
d=collections.defaultdict(dict)
for r in rows: d[(r['corpus'] if 'corpus' in r else r['corpus_id'],r['cell'],r['seed_index'] if 'seed_index' in r else r['seed'])][r['arm']]=cost(r)
for a,b in [('F','W'),('F','C'),('W','C')]:
    per=collections.defaultdict(list)
    for (c,cell,s),v in d.items(): per[c].append(math.log(v[b])-math.log(v[a]))
    m=np.array([np.mean(x) for x in per.values()]); n=np.array([len(x) for x in per.values()])
    pair_sd=np.sqrt(np.mean([np.var(x,ddof=1) for x in per.values()]))
    within=pair_sd**2/n.mean(); obs=m.var(ddof=1); between=max(obs-within,0)
    print(f'{a}/{b}: est {math.exp(m.mean()):.3f} corpusSD {m.std(ddof=1):.3f} pairSD {pair_sd:.2f} between_var {between:.4f} (sd {math.sqrt(between):.3f})')
    for pairs in (64,128,192,256):
        sd=math.sqrt(between+pair_sd**2/pairs); hw=math.exp(stats.t.ppf(.975,15)*sd/4)
        print(f'   pairs/corpus {pairs}: proj corpusSD {sd:.3f} half-width x{hw:.3f}')
