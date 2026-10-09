"""Steward probe (read-only): would the 0843/1036 extractor, applied to pre-solve S tapes
from 1831, fill 32-fragment libraries, and how much do they overlap the exact-solver whole
libraries? One S tape per (source search, checkpoint): lowest archive slot (performance-blind).
Needs research/main's Rust (v2_rmin_first): `git archive research/main | tar -x -C /tmp/rmain`,
`uv pip install -e .` and `maturin develop --release` there, then run from /tmp/rmain with
PYTHONPATH=/tmp/rmain. main's prebuilt .venv module gives wrong outputs for this alphabet."""
import gzip, json, sys, time
from collections import Counter, defaultdict
from functools import lru_cache
import numpy as np
from experiments.chem_tape.comparison_gate_bank import TRAINING, load_training
from experiments.chem_tape.composition_search import outputs

ARCH = "/Users/andreas/developer/folding-evolution/experiments/output/2026-10-08/2026-10-08-1831-partial-program-context/search.jsonl"
EXACT = '/tmp/rmain/experiments/chem_tape/data/fragment_reuse_1036/whole_libraries.json.gz'
bank, cells = load_training()
inputs = bank['inputs']
indices = np.random.default_rng(0).choice(len(inputs), 96, replace=False).tolist()
sampled = [inputs[i] for i in indices]
exact = json.load(gzip.open(EXACT))
rows = [json.loads(l) for l in open(ARCH)]
rows = [r for r in rows if r['phase'] == 'collection']
by = defaultdict(list)
for r in rows:
    by[r['corpus']].append(r)
out = {}
t0 = time.time()
for tid in sorted(by):
    cand = defaultdict(list)
    ntapes = 0
    for r in by[tid]:
        for cp in (64, 128, 256):
            S = sorted((a for a in r['archive'] if a['kind'] == 'S' and a['checkpoint'] == cp), key=lambda a: a['slot'])
            if not S:
                continue
            tape = S[0]['tape']; ntapes += 1
            m = np.tile(tape, (33, 1)); m[np.arange(32) + 1, np.arange(32)] = 0
            o = outputs(m, sampled, 'v2_rmin_first')
            act = np.any(o[1:] != o[0], axis=1)
            for L in range(3, 7):
                for s in range(33 - L):
                    if act[s:s + L].all():
                        cand[tuple(tape[s:s + L])].append((r['cell'], r['seed'], cp))
    @lru_cache(None)
    def solves(f):
        v = outputs([list(f) + [0] * (32 - len(f))], inputs, 'v2_rmin_first')[0]
        return any(np.array_equal(v, cells[c]['labels']) for c in TRAINING[tid[:2]])
    el = []
    for f, p in cand.items():
        sc = {x[0] for x in p}
        srcs = {(x[0], x[1]) for x in p}
        if len(sc) >= 2:
            el.append((f, len(sc), len(p), len(srcs)))
    el.sort(key=lambda x: (-x[1], -x[2], -len(x[0]), x[0]))
    lib = []
    for f, nc, cnt, ns in el:
        if solves(f):
            continue
        lib.append((f, nc, cnt, ns))
        if len(lib) == 32:
            break
    ex = {tuple(x['tokens']) for x in exact[tid]['fragments']}
    pf = {x[0] for x in lib}
    out[tid] = dict(tapes=ntapes, eligible=len(el), size=len(lib), overlap=len(pf & ex),
                    lengths=dict(Counter(len(f) for f in pf)), exact_lengths=dict(Counter(len(f) for f in ex)),
                    min_sources=min((x[3] for x in lib), default=0), all4=sum(x[1] == 4 for x in lib))
    print(tid, out[tid], flush=True)
print('seconds', time.time() - t0)
allp = set(); alle = set()
json.dump(out, open("/Users/andreas/developer/folding-evolution/research/runs/2026-10-09-1350/steward_probe/partial_library_probe.json", 'w'), indent=1)

# Which fragments differ (names), pooled over corpora.
from folding_evolution.chem_tape.executor import resolve_op
from experiments.chem_tape.composition_bank import TA
name = lambda f: ' '.join(resolve_op(t, TA, 'v2_rmin_first').__name__ for t in f)
