"""Steward probe (read-only, not efficacy): fit C4 and extract F4 from the first four 1246
collection attempts per corpus x training cell (audit rule), then time a small then-addition
look at C4 bare and C4+F4. Run from a research/main build at /tmp/rmain (see 1350 probe header):
  cd /tmp/rmain && RAYON_NUM_THREADS=1 PYTHONPATH=/tmp/rmain .venv/bin/python <this file>
Empty cells use G4's expected length-32 transition counts scaled to the cell mass (plan's fallback)."""
import json, sys, time, os, pickle, multiprocessing as mp
from collections import defaultdict
import numpy as np
from experiments.chem_tape.comparison_gate_bank import TRAINING, load_training
from experiments.chem_tape.composition_search import Decoder, outputs
from experiments.chem_tape.four_reducer_maps import R, tables
from experiments.chem_tape.map_learning import normalize
from experiments.chem_tape.solver_corpus_fit import transition_counts
from experiments.chem_tape.fragment_library import extract_windows
from experiments.chem_tape.fragment_run import execute, CORPORA
from experiments.chem_tape.then_addition_run import frozen_source
from experiments.chem_tape.then_addition_bank import load

def main():
    OUT = sys.argv[1] if len(sys.argv) > 1 else 'small_source_probe.json'
    bank, cells = load_training()
    saved, _ = frozen_source()
    corp = saved['corpora.json']
    rows = {(r['corpus'], r['cell'], r['seed']): r for r in saved['search.jsonl'] if r['phase'] == 'collection'}
    order = defaultdict(list)
    for s in saved['schedule.json']:
        if s['phase'] == 'collection':
            order[s['corpus'], s['cell']].append(s['seed'])
    g = np.diff(tables()['G4'], prepend=0, axis=1) / R
    # expected G4 transition counts over a 32-token tape (start row 24)
    exp = np.zeros((25, 24)); p = np.zeros(25); p[24] = 1
    for _ in range(32):
        exp += p[:, None] * g
        q = p @ g; p = np.zeros(25); p[:24] = q
    def fit_c(rs, cs):
        per = {}
        for c in cs:
            sub = [r for r in rs if r['cell'] == c]
            if any(r['solved'] for r in sub):
                n, _ = transition_counts(sub, [c]); per[c] = n
            else:
                per[c] = exp / exp.sum() * 1600
        n = sum(per.values())
        return normalize((n + 50 * g) / (n.sum(1, keepdims=True) + 50), R)
    indices = np.random.default_rng(0).choice(len(bank['inputs']), 96, replace=False).tolist()
    info, tabs, libs = {}, {}, {}
    t0 = time.time()
    CACHE = '/tmp/small_source_probe_cache.pkl'
    if os.path.exists(CACHE):
        info, tabs, libs, fit_s = pickle.load(open(CACHE, 'rb'))
    for tid in ([] if info else CORPORA):
        cs = TRAINING[tid[:2]]
        allr = [r for r in rows.values() if r['corpus'] == tid]
        pre = [rows[tid, c, s] for c in cs for s in order[tid, c][:4]]
        full_check = Decoder(fit_c(allr, cs)).hash() == Decoder(corp[tid]['tables']['C']).hash()
        C4 = fit_c(pre, cs); tabs[tid] = C4
        src = [dict(cell=r['cell'], seed=r['seed'], tape=r['solver']) for r in pre if r['solved']]
        lib = extract_windows(tid, src, bank['inputs'], cells, indices)['whole_corpus'] if len({s['cell'] for s in src}) >= 2 else dict(fragments=[])
        libs[tid] = lib['fragments']
        full = np.diff(np.asarray(corp[tid]['tables']['C']), prepend=0, axis=1) / R
        c4 = np.diff(C4, prepend=0, axis=1) / R
        H = lambda P: float(np.mean(-(P * np.log2(P)).sum(1)))
        info[tid] = dict(full_C_reproduced=full_check, solvers=len(src),
                         per_cell={c: sum(r['solved'] for r in pre if r['cell'] == c) for c in cs},
                         library_size=len(lib['fragments']),
                         library_lengths=[len(f['tokens']) for f in lib['fragments']],
                         row_entropy_bits=dict(C4=H(c4), C=H(full), G4=H(g)),
                         tv_C4_C=float(np.mean(0.5 * np.abs(c4 - full).sum(1))))
    if not os.path.exists(CACHE):
        fit_s = time.time() - t0
        pickle.dump((info, tabs, libs, fit_s), open(CACHE, 'wb'))
    print('fit/extract seconds', fit_s, flush=True)
    ta, ta_cells = load()
    ids = ta['selected_ids']
    diag = [bank['inputs'][i] for i in indices[:4]]
    jobs = []
    for ci, tid in enumerate(CORPORA):
        for k in range(4):
            cid = ids[(4 * k + ci) % 16]  # each corpus sees 4 cells; every cell seen 4 times
            sd = 917000000000 + ci * 1000 + k
            for arm, frag in (('C', []), ('F', libs[tid])):
                if arm == 'F' and not frag:
                    continue
                job = (ta_cells[cid], arm, tabs[tid].tolist(), sd, 524288, 256, bank['inputs'], 'v2_rmin_first')
                jobs.append((job, dict(corpus=tid, cell=cid, seed=sd, arm4=arm, arm=arm, phase='probe', family=tid[:2]), frag, diag, arm == 'C'))
    t1 = time.time()
    with mp.get_context('spawn').Pool(10) as pool:
        res = pool.map(execute, jobs, chunksize=1)
    wall = time.time() - t1
    summ = {}
    for arm in ('C', 'F'):
        rs = [r for r in res if r['arm4'] == arm]
        cost = [r['evaluations'] if r['solved'] else 2 * 524288 for r in rs]
        summ['C4' if arm == 'C' else 'C4+F4'] = dict(n=len(rs), solved=sum(r['solved'] for r in rs),
            geo_cost=float(np.exp(np.mean(np.log(cost)))), mean_worker_s=float(np.mean([r['seconds'] for r in rs])))
    json.dump(dict(info=info, fit_extract_seconds=fit_s, probe=summ, wall=wall,
                   rows=[{k: r[k] for k in ('corpus', 'cell', 'seed', 'arm4', 'solved', 'evaluations', 'seconds')} for r in res]),
              open(OUT, 'w'), indent=1)
    print(json.dumps(dict(summ=summ, wall=wall, fit_s=fit_s), indent=1))
    for t, v in info.items():
        print(t, v['full_C_reproduced'], v['solvers'], v['per_cell'].values(), v['library_size'], round(v['row_entropy_bits']['C4'], 2), round(v['row_entropy_bits']['C'], 2), round(v['tv_C4_C'], 2))


if __name__ == '__main__':
    main()
