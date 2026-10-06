# Steward probe 2: G vs single-row log-normal perturbations (sigma 0.7) of G, paired seeds.
import time, sys, numpy as np, multiprocessing as mp
sys.path.insert(0, '/tmp/probe0132'); sys.path.insert(0, '/tmp/probe0132/p')
from probe import job, TRAIN, cumulative, R, Decoder, frozen_controls
def row_perturb(table, row, sigma, rng):
    out = table.copy(); w = np.diff(table[row], prepend=0).astype(float)
    w = np.exp(np.log(w) + rng.normal(0, sigma, 23)); w = np.maximum(w, w.sum()*250/R*1.05)
    out[row] = cumulative(w); Decoder(out); return out
if __name__ == '__main__':
    G = frozen_controls()['G']; rng = np.random.default_rng(13202)
    rows = [23, 1, 5, 11, 18, 22, 7, 9, 17, 2, 3, 15]
    maps = {'G': G}
    for r in rows: maps[f'row{r}'] = row_perturb(G, r, 0.7, rng)
    cap = 65536; seeds = range(91330000, 91330000+20)
    jobs = [(n, m, c, s, cap) for n, m in maps.items() for c in TRAIN for s in seeds]
    with mp.get_context('spawn').Pool(10) as p: res = p.map(job, jobs, chunksize=4)
    sc = {(r[0], r[1], r[2]): np.log2(r[4] if r[3] else 2*cap) for r in res}
    keys = [(c, s) for c in TRAIN for s in seeds]
    g = np.array([sc[('G',)+k] for k in keys])
    for n in maps:
        if n == 'G': continue
        x = np.array([sc[(n,)+k] for k in keys]); d = x - g
        print(n, x.mean(), d.mean(), d.std(ddof=1)/np.sqrt(len(d)), np.corrcoef(x, g)[0, 1])
