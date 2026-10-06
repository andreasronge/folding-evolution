# Steward probe 1 (run 2026-10-06-0132), run from a detached worktree of research/main (a65ded0)
# at /tmp/probe0132 with 10 spawn workers. Capped (65 536) G / PA-grammar / U / globally perturbed G
# searches on the six PA training cells, 20 fresh seeds each. Output in results.md.
import json, time, sys, numpy as np, multiprocessing as mp
sys.path.insert(0, '/tmp/probe0132')
from experiments.chem_tape.composition_search import search, Decoder, cumulative, R
from experiments.chem_tape.assembly_maps import frozen_controls, grammar
from experiments.chem_tape.assembly_bank import inputs_for
B = json.load(open('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-0001-assembly-family/bank.json'))
TRAIN = ['PA:(S?M:m)+M','PA:(S?M:m)+S','PA:(S?m:M)+S','PA:(S?m:M)+m','PA:(S?m:S)+M','PA:(S?m:S)+m']
cells = {c['id']: dict(id=c['id'], labels=c['labels']) for c in B['cells'] if c['id'] in TRAIN}
INP = inputs_for('D1331')
def perturb(table, sigma, rng):
    out = table.copy()
    for r in range(24):
        w = np.diff(table[r], prepend=0).astype(float)
        w = np.exp(np.log(w) + rng.normal(0, sigma, 23)); w = np.maximum(w, w.sum()*250/R*1.05)
        out[r] = cumulative(w)
    Decoder(out); return out
def job(a):
    name, table, cid, seed, cap = a
    r = search((cells[cid], name, table, seed, cap, 256, INP))
    return name, cid, seed, r['solved'], r['evaluations'], r['seconds']
if __name__ == '__main__':
    t = frozen_controls(); G = t['G']
    maps = {'G': G, 'PAgram': grammar('PA'), 'U': t['U']}
    rng = np.random.default_rng(13201)
    for i in range(4): maps[f'Gp{i}'] = perturb(G, 0.5, rng)
    cap = 65536; seeds = range(91320000, 91320000+20)
    jobs = [(n, m, c, s, cap) for n, m in maps.items() for c in TRAIN for s in seeds]
    t0 = time.time()
    with mp.get_context('spawn').Pool(10) as p: res = p.map(job, jobs, chunksize=4)
    print('runs', len(res), 'wall', round(time.time()-t0,1))
    import collections
    by = collections.defaultdict(list)
    for r in res: by[r[0]].append(r)
    for n, rs in by.items():
        sc = np.array([np.log2(e if s else 2*cap) for _,_,_,s,e,_ in rs])
        print(n, np.mean([r[3] for r in rs]), sc.mean(), sc.std(ddof=1)/np.sqrt(len(sc)), np.mean([r[5] for r in rs]))
