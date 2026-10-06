import sys, time, itertools, json, resource
sys.path.insert(0, "/tmp/fr4"); sys.path.insert(0, "/tmp/fr4/src")
import numpy as np
from experiments.chem_tape.composition_bank import TOKENS, SemanticMachine
from folding_evolution.chem_tape import alphabet as a
FIRST = 23
TOK = tuple(TOKENS) + (FIRST,)
DOM = sys.argv[1] if len(sys.argv) > 1 else "D1331"
L, lo, hi = {"D625": (4, -2, 2), "D1331": (3, -5, 5), "D2401": (4, -3, 3)}[DOM]
MAXD = int(sys.argv[2]) if len(sys.argv) > 2 else 8
inputs = list(map(list, itertools.product(range(lo, hi + 1), repeat=L)))
xs = np.array(inputs)
R = {"S": xs.sum(1), "M": xs.max(1), "m": xs.min(1), "F": xs[:, 0]}
RT = {"S": a.SUM, "M": a.REDUCE_MAX, "m": a.REDUCE_MIN, "F": FIRST}
class M4(SemanticMachine):
    def __init__(self, inputs):
        super().__init__(inputs)
        self.reduced[FIRST] = self.intern(np.asarray(inputs)[:, 0])
m = M4(inputs)
def push(x): return [a.INPUT, RT[x]]
cells = []
for A, B in itertools.permutations("SMmF", 2):
    rest = [r for r in "SMmF" if r not in (A, B)]
    C, D = rest
    cells.append((f"BE:{A}?{B}:({C}+{D})", "BE", np.where(R[A] > 0, R[B], R[C] + R[D]), push(C)+push(D)+[a.ADD]+push(B)+push(A)+[a.IF_GT]))
for A, B, C in itertools.permutations("SMmF", 3):
    D = [r for r in "SMmF" if r not in (A, B, C)][0]
    cells.append((f"PA:({A}?{B}:{C})+{D}", "PA", np.where(R[A] > 0, R[B], R[C]) + R[D], push(C)+push(B)+push(A)+[a.IF_GT]+push(D)+[a.ADD]))
labels = np.array([c[2] for c in cells])
# verify canonicals on the semantic machine
for c in cells:
    st = ()
    for t in c[3]: st = m.apply(st, t)
    assert np.array_equal(m.values[m.output_id(st)], c[2]), c[0]
n = len(inputs)
best = np.full(len(cells), -1); wit = [None]*len(cells); checked = set()
def check(state, prog):
    oid = m.output_id(state)
    if oid in checked: return
    checked.add(oid)
    mt = np.count_nonzero(labels == m.values[oid], axis=1)
    for i in np.flatnonzero(mt > best):
        best[i] = mt[i]; wit[i] = bytes(prog)
def report(depth):
    surv = [cells[i][0] for i in range(len(cells)) if 5*best[i] < 4*n]
    print(json.dumps(dict(depth=depth, t=round(time.monotonic()-t0,1), rss_gb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024**3,2), states=len(frontier), survivors=len(surv))), flush=True)
t0 = time.monotonic()
seen = {()}; frontier = {(): b""}; check((), b"")
OO = len(sys.argv) > 3
for depth in range(1, MAXD + 1):
    nxt = {}
    last = OO and depth == MAXD
    if last: del seen
    for state, prog in frontier.items():
        for t in TOK:
            ch = m.apply(state, t)
            if last:
                check(ch, prog + bytes([t])); continue
            if ch not in seen:
                seen.add(ch); rep = prog + bytes([t]); nxt[ch] = rep; check(ch, rep)
    frontier = nxt
    report(depth)
    if last: break
# label duplicates
dup = {}
for i, c in enumerate(cells): dup.setdefault(c[2].tobytes(), []).append(c[0])
out = []
for i, c in enumerate(cells):
    out.append(dict(id=c[0], agree=round(best[i]/n, 3), witness=list(wit[i]), dups=[d for d in dup[c[2].tobytes()] if d != c[0]], survive=bool(5*best[i] < 4*n)))
json.dump(dict(domain=DOM, depth=MAXD, cells=out), open(f"/tmp/fr4probe/screen_{DOM}_{MAXD}.json", "w"), indent=1)
for r in sorted(out, key=lambda r: r["agree"]): print(r["id"], r["agree"], r["survive"], r["dups"], r["witness"])
