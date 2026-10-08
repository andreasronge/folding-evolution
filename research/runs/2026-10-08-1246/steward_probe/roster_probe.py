import itertools, hashlib, json, time, sys
from collections import Counter, defaultdict
import numpy as np
sys.path[:0] = ["/tmp/rmain", "/tmp/rmain/src"]
from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape import four_reducer_bank as frb
from experiments.chem_tape.four_reducer_bank import FirstMachine, EXECUTABLE, REDUCERS
from folding_evolution.chem_tape import alphabet as a
from folding_evolution.chem_tape.executor import execute_program
from experiments.chem_tape.composition_bank import TA

D = "D1331"
xs = np.asarray(inputs_for(D)); n = len(xs)
r = dict(S=xs.sum(1), M=xs.max(1), m=xs.min(1), F=xs[:, 0])
push = lambda k: [a.INPUT, REDUCERS[k]]
cells = []
for rep in "SMmF":
    ms = sorted(set(itertools.permutations(list("SMmF") + [rep], 5)))
    for A, B, C, Dd, E in ms:
        g = r[A] > r[B]
        if g.all() or not g.any():
            continue  # constant gate
        be = np.where(g, r[C], r[Dd] + r[E])
        pa = np.where(g, r[C], r[Dd]) + r[E]
        cells.append(("BE", f"BE:{A}>{B}?{C}:{Dd}+{E}", be, push(Dd)+push(E)+[a.ADD]+push(C)+push(A)+push(B)+[a.GT, a.IF_GT]))
        cells.append(("PA", f"PA:({A}>{B}?{C}:{Dd})+{E}", pa, push(Dd)+push(C)+push(A)+push(B)+[a.GT, a.IF_GT]+push(E)+[a.ADD]))
# verify a sample of canonicals with python executor
for fam, cid, lab, prog in cells[:40]:
    out = [execute_program([0]*19+prog, TA, list(x), "intlist", "v2_rmin_first") for x in xs[:200]]
    assert np.array_equal(out, lab[:200]), cid
byhash = defaultdict(list)
for c in cells: byhash[c[2].tobytes()].append(c)
uniq = {}
for h, cs in byhash.items():
    fams = {c[0] for c in cs}
    uniq[h] = cs
print("raw (non-constant gate)", Counter(c[0] for c in cells))
print("distinct behaviours", len(uniq), "cross-family dups", sum(len({c[0] for c in cs})>1 for cs in uniq.values()))
# old bank behaviours
oldh = {np.asarray(c["labels"], dtype=np.int64).tobytes() for c in frb.roster(D)}
# Inactive branch / dominated: label equals a single branch everywhere is covered by alias screen.
labels = np.array([np.frombuffer(h, dtype=np.int64) for h in uniq])
fam_of = [ "+".join(sorted({c[0] for c in uniq[h]})) for h in uniq]
print("equal to old-bank behaviour", sum(h in oldh for h in uniq))
# exact <=9 screen
t0 = time.monotonic()
m = FirstMachine(inputs_for(D))
best = np.full(len(labels), -1); checked=set()
def check(state):
    oid = m.output_id(state)
    if oid in checked: return
    checked.add(oid)
    mt = np.count_nonzero(labels == m.values[oid], axis=1)
    np.maximum(best, mt, out=best)
seen={()}; frontier={()}; check(())
DEPTH=int(sys.argv[1]) if len(sys.argv)>1 else 9
for d in range(1, DEPTH+1):
    last = d == DEPTH
    nxt=set()
    for s in frontier:
        for t in EXECUTABLE:
            ch = m.apply(s,t)
            if last: check(ch)
            elif ch not in seen:
                seen.add(ch); nxt.add(ch); check(ch)
    print("depth", d, len(nxt), len(checked), round(time.monotonic()-t0,1), flush=True)
    frontier = nxt
agree = best / n
exact = agree == 1; near = (agree >= .8) & ~exact
keep = ~exact & ~near
for fam in ("BE","PA","BE+PA"):
    idx = [i for i,f in enumerate(fam_of) if f==fam]
    print(fam, "distinct", len(idx), "exact", int(exact[idx].sum()), "near", int(near[idx].sum()), "retained", int(keep[idx].sum()))
res = []
for i,h in enumerate(uniq):
    res.append(dict(ids=[c[1] for c in uniq[h]], fam=fam_of[i], agree=float(agree[i]), retained=bool(keep[i]), old=h in oldh))
json.dump(res, open("/tmp/probe/roster_screen.json","w"), indent=1)
