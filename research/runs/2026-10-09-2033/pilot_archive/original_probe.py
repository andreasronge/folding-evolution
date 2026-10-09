import json, time, multiprocessing as mp, numpy as np, sys
sys.path.insert(0, '/tmp/ssf_probe')
from experiments.chem_tape.comparison_gate_bank import TRAINING, load_training
from experiments.chem_tape.comparison_gate_run import CAP
from experiments.chem_tape.composition_search import search
from experiments.chem_tape.fragment_operator import BlockOperator
B = json.load(open('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1743-small-source-prepare/builds.json'))
bank, cells = load_training()
idx = np.random.default_rng(0).choice(len(bank['inputs']), 96, replace=False).tolist()
diag = [bank['inputs'][i] for i in idx[:4]]
def run(a):
    key, cid, seed = a
    rec = B[key]
    op = BlockOperator('F', rec['library']['fragments'], seed, diag, empty_fallback=True)
    t = time.monotonic()
    r = search((cells[cid], 'F', rec['table'], seed, CAP, 256, bank['inputs'], 'v2_rmin_first'), return_solver=True, child_transform=op)
    return dict(key=key, cell=cid, solved=r['solved'], ev=r['evaluations'], s=time.monotonic()-t, empty=cid in rec['empty_cells'])
if __name__ == '__main__':
    jobs = []
    for key, rec in B.items():
        if rec['block'] != int(sys.argv[1]): continue
        for i, cid in enumerate(TRAINING[rec['corpus'][:2]]):
            jobs.append((key, cid, 990020331 + hash(key) % 1000 * 10 + i))
    t = time.time()
    with mp.Pool(10) as p: out = p.map(run, jobs)
    w = time.time() - t
    sol = [o for o in out if o['solved']]
    print(len(out), 'searches', len(sol), 'solved; wall', round(w), 's; worker-s mean', round(np.mean([o['s'] for o in out]),2), 'evals mean', int(np.mean([o['ev'] for o in out])))
    e = [o for o in out if o['empty']]; print('in source-empty cells', len(e), 'solved', sum(o['solved'] for o in e))
    print(sorted((o['cell'], o['solved']) for o in out if not o['solved']))
