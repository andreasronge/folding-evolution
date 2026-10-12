"""Paired summary of rows.jsonl; build-level bootstrap (cells within builds) for ratios."""
import json, collections
import numpy as np
rows = [json.loads(l) for l in open(__file__.replace('analyse.py', 'rows.jsonl'))]
rng = np.random.default_rng(250)
out = {}
for fam in ('order', 'gate'):
    E = {law: np.zeros((24, 6)) for law in 'OGM'}
    cells = sorted({r['cell'] for r in rows if r['family'] == fam})
    W = collections.defaultdict(list)
    for r in rows:
        if r['family'] == fam:
            E[r['law']][r['build'], cells.index(r['cell'])] = r['evaluations']
            W[r['law']].append(r['worker_seconds'])
    print(fam, {l: (round(E[l].mean()), round(float(np.mean(W[l])), 2), int(sum(r['solved'] for r in rows if r['family']==fam and r['law']==l)),
                     int(sum(r['attempts']>1 for r in rows if r['family']==fam and r['law']==l))) for l in 'OGM'})
    for a, b in (('O', 'M'), ('G', 'M'), ('O', 'G')):
        bs = []
        for _ in range(4000):
            i = rng.integers(24, size=24); j = rng.integers(6, size=(24, 6))
            bs.append(E[a][i[:, None], j].mean() / E[b][i[:, None], j].mean())
        print(f'  {a}/{b} {E[a].mean()/E[b].mean():.3f} [{np.quantile(bs,.025):.3f}, {np.quantile(bs,.975):.3f}]')
    print('  per-cell O/M', np.round(E['O'].mean(0)/E['M'].mean(0), 2), 'G/M', np.round(E['G'].mean(0)/E['M'].mean(0), 2))
