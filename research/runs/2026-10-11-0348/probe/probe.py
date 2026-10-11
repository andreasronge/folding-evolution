import json, sys, time
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.tree_gp_search import search, Tree, interpret

CAP = 524288
AUD = '/Users/andreas/developer/folding-evolution/research/runs/2026-10-11-0348/semantic-planning-audit.json'
LIB = '/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-0150-prepare/libraries.json'
INPUTS = inputs_for("D625")
XS = np.asarray(INPUTS)
roles = json.load(open(AUD))['greedy_roles'][:2]
libs = json.load(open(LIB))

def cell(r):
    A,B,C,D,E,F,G = r
    lab = np.where(XS[:,A]+XS[:,B] > XS[:,C]+XS[:,D], XS[:,E]+XS[:,F], XS[:,G]).astype(np.int64)
    return dict(id=f"(X{A}+X{B})>(X{C}+X{D})?X{E}+X{F}:X{G}", labels=lab.tolist())

# sanity: canonical tree interpret == labels
for r in roles:
    A,B,C,D,E,F,G = r
    t = Tree((11, G, 9, E, F, 10, 9, A, B, 9, C, D))
    c = cell(r)
    assert all(interpret(t, x) == y for x, y in zip(INPUTS, c['labels'])), r
    print(c['id'], 'canonical compiled length', len(t.program), flush=True)

def run(args):
    ci, arm, b, k = args
    c = cell(roles[ci])
    donors = None if arm == 'R-tree' else [Tree(tuple(e['prefix'])) for e in libs[b]['entries']]
    seed = 934_900_000 + ci*100000 + b*100 + k
    t = time.monotonic()
    r = search((c, seed, CAP, 256, INPUTS, 0.5), donor_library=donors)
    return dict(cell=c['id'], arm=arm, build=b, k=k, solved=r['solved'], evaluations=r['evaluations'],
                seconds=time.monotonic()-t, op=r["operator"], best=[x[:2] for x in r["curve"]], perfect=r["training_perfect_individuals"], short=r["unique_shortcuts"])

if __name__ == '__main__':
    n = int(sys.argv[1])
    jobs = [(ci, arm, b, k) for k in range(n) for b in range(24) for ci in range(2) for arm in ('R-tree','R-lib')]
    with ProcessPoolExecutor(10) as ex, open('/tmp/probe0348/out/rows_long.jsonl','w') as f:
        for row in ex.map(run, jobs):
            f.write(json.dumps(row)+'\n'); f.flush()
