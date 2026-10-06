# Steward probe 0811: true-effect spread of one-step children at the six saved M maps.
# Run from a detached worktree at 02cf76f: .venv/bin/python <this file>
import json, sys, time, multiprocessing as mp
import numpy as np
from experiments.chem_tape.map_learning_run import load_bank
from experiments.chem_tape.map_learning import table_for, normalize, initial, BOUND, log_cost
from experiments.chem_tape.assembly_maps import frozen_controls
from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_search import search

O = '/Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-0132-post-addition-map-learning'
CAP = 65536

def row_move(table, sigma, rng):
    w = np.diff(table, prepend=0, axis=1).astype(float)
    r = int(rng.integers(24))
    w[r] = np.exp(np.log(w[r]) + rng.normal(0, sigma, 23))
    return normalize(w), r

def m_move(vec, rng):
    v = vec.copy(); c = rng.choice(23, 3, replace=False); v[c] += rng.normal(0, 0.5, 3)
    return np.clip(v, -BOUND, BOUND)

if __name__ == '__main__':
    bank = load_bank(); inputs = inputs_for('D1331'); ctr = frozen_controls()
    cells = {c['id']: dict(id=c['id'], labels=c['labels']) for c in bank['cells']}
    train = bank['split']['training']
    fm = json.load(open(O + '/final_maps.json'))
    rng = np.random.default_rng(811001)
    maps, meta = {}, {}
    for k in range(6):
        vec = np.array(fm[f'M{k+1}']['vector']); tab = table_for('M', vec, ctr)
        assert np.array_equal(tab, np.array(fm[f'M{k+1}']['table']))
        maps[f'M{k+1}:parent'] = tab; meta[f'M{k+1}:parent'] = (k, 'parent')
        for j in range(10):
            maps[f'M{k+1}:mcoord:{j}'] = table_for('M', m_move(vec, rng), ctr); meta[f'M{k+1}:mcoord:{j}'] = (k, 'mcoord')
            for s in (0.5, 1.0):
                t, r = row_move(tab, s, rng); n = f'M{k+1}:row{s}:{j}:r{r}'
                maps[n] = t; meta[n] = (k, f'row{s}')
    jobs = []
    for n, t in maps.items():
        k = meta[n][0]
        for c in train:
            for s in range(4):
                jobs.append((cells[c], n, t, 811100000 + k * 100 + s, CAP, 256, inputs))
    tick = time.monotonic()
    with mp.get_context('spawn').Pool(10) as p:
        rows = p.map(search, jobs, chunksize=2)
    wall = time.monotonic() - tick
    sc = {(r['arm'], r['cell'], r['seed']): log_cost(r, CAP) for r in rows}
    secs = {}
    for r in rows: secs.setdefault(meta[r['arm']][1], []).append(r['seconds'])
    print(f'runs {len(rows)} wall {wall:.0f}s  runs/s {len(rows)/wall:.1f}')
    for op, v in secs.items(): print(op, 'mean s/run %.3f' % np.mean(v))
    res = {}
    for n, (k, op) in meta.items():
        if op == 'parent': continue
        keys = [(c, 811100000 + k * 100 + s) for c in train for s in range(4)]
        d = np.array([sc[(n,) + key] - sc[(f'M{k+1}:parent',) + key] for key in keys])
        res.setdefault(op, []).append((d.mean(), d.var(ddof=1) / len(d)))
    par = [np.mean([sc[(f'M{k+1}:parent', c, 811100000 + k*100 + s)] for c in train for s in range(4)]) for k in range(6)]
    print('parent means', np.round(par, 2))
    out = {}
    for op, v in res.items():
        m = np.array([a for a, b in v]); noise = np.mean([b for a, b in v])
        tv = max(m.var(ddof=1) - noise, 0)
        out[op] = dict(n=len(m), mean=float(m.mean()), obs_sd=float(m.std(ddof=1)), noise_sd=float(noise**.5), true_sd=float(tv**.5),
                       frac_better_05=float(np.mean(m < -0.5)))
        print(op, {a: round(b, 3) for a, b in out[op].items()})
    json.dump(dict(summary=out, wall=wall, runs=len(rows), parent_means=par), open('/tmp/probe0811_result.json', 'w'), indent=1)
