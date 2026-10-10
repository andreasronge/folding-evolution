"""Steward feasibility probe (read-only): semantic coverage of (A+B)>(C+D)?E:F
over independent readouts X0-X3 on D625. No search, no fitted maps.

Reinterprets the four reducer slots SUM/MAX/MIN/FIRST as X0..X3 inside the
semantic machine only (no executor change). Canonical check uses the same
machine, so this validates nothing about Rust/Python executors.
Variant "keep": REDUCE_ADD/ANY stay in the token set (conservative screen).
Variant "drop": they are removed.
"""
import hashlib, io, itertools, json, subprocess, sys, tarfile, tempfile, time
from pathlib import Path

OUT = Path(__file__).resolve().parent
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "keep"
REV = subprocess.check_output(["git", "rev-parse", "research/main"], text=True).strip()
with tempfile.TemporaryDirectory(prefix="steward-probe-") as d:
    arch = subprocess.check_output(["git", "archive", REV, "src", "experiments"])
    with tarfile.open(fileobj=io.BytesIO(arch)) as t:
        t.extractall(d, filter="data")
    sys.path[:0] = [d, str(Path(d) / "src")]
    import numpy as np
    from folding_evolution.chem_tape import alphabet as a
    from experiments.chem_tape import assembly_bank as ab
    from experiments.chem_tape.four_reducer_bank import EXECUTABLE, FirstMachine

    SLOT = (a.SUM, a.REDUCE_MAX, a.REDUCE_MIN, a.FIRST)
    xs = np.asarray(ab.inputs_for("D625"))

    class XMachine(FirstMachine):
        def __init__(self, inputs):
            super().__init__(inputs)
            v = np.asarray(inputs, dtype=np.int64)
            for i, tok in enumerate(SLOT):
                self.reduced[tok] = self.intern(v[:, i])

    def outputs(programs, inputs, alphabet):
        m = XMachine(inputs)
        res = []
        for p in programs:
            s = ()
            for tok in p:
                if tok:
                    s = m.apply(s, tok)
            res.append(m.values[m.output_id(s)])
        return np.asarray(res)

    ab.outputs = outputs
    tokens = tuple(t for t in EXECUTABLE if VARIANT == "keep" or t not in (a.REDUCE_ADD, a.ANY))
    push = lambda i: [a.INPUT, SLOT[i]]
    cells = {}
    for A, B, C, D, E, F in itertools.product(range(4), repeat=6):
        if A > B or C > D:
            continue
        gate = xs[:, A] + xs[:, B] > xs[:, C] + xs[:, D]
        lab = np.where(gate, xs[:, E], xs[:, F]).astype("<i8")
        if gate.all() or not gate.any() or (lab == xs[:, E]).all() or (lab == xs[:, F]).all():
            continue
        key = hashlib.sha256(lab.tobytes()).hexdigest()
        cid = f"DG:(X{A}+X{B})>(X{C}+X{D})?X{E}:X{F}"
        cell = dict(id=cid, shape="DG", roles=dict(zip("ABCDEF", map(int, (A, B, C, D, E, F)))),
                    proper=len({A, B, C, D}) == 4, labels=lab.tolist(), label_hash=key,
                    canonical=push(F) + push(E) + push(A) + push(B) + [a.ADD] + push(C) + push(D) + [a.ADD, a.GT, a.IF_GT])
        if key not in cells or (cell["proper"], -len(cid), cid) > (cells[key]["proper"], -len(cells[key]["id"]), cells[key]["id"]):
            cells[key] = cell
    roster = sorted(cells.values(), key=lambda c: c["id"])
    res = ab.screen_domain("D625", 9, deadline=time.monotonic() + 600, cells=roster,
                           tokens=tokens, machine_type=XMachine, alphabet="probe")
    ret = [c for c in roster if c["retained"]]
    L = np.asarray([c["labels"] for c in ret])
    agree = (L[:, None, :] == L[None, :, :]).mean(2) if len(ret) else np.zeros((0, 0))
    ok = agree < 0.8
    # Exact maximum clique of the separation graph (Bron-Kerbosch with pivot).
    best = []
    def bk(R, P, X):
        global best
        if not P and not X:
            if len(R) > len(best):
                best = R
            return
        if len(R) + len(P) <= len(best):
            return
        u = max(P | X, key=lambda v: len(P & nb[v]))
        for v in list(P - nb[u]):
            bk(R + [v], P & nb[v], X & nb[v])
            P = P - {v}; X = X | {v}
    nb = {i: {j for j in range(len(ret)) if j != i and ok[i, j]} for i in range(len(ret))}
    sys.setrecursionlimit(10000)
    bk([], set(range(len(ret))), set())
    summ = dict(variant=VARIANT, code=REV, distinct_active=len(roster),
                proper_active=sum(c["proper"] for c in roster),
                retained=len(ret), retained_proper=sum(c["proper"] for c in ret),
                max_separated=len(best), max_separated_ids=[ret[i]["id"] for i in best],
                retained_ids=[c["id"] for c in ret],
                alias_witness_lengths=sorted({len(c["witness"] or []) for c in roster if not c["retained"]}),
                screen_seconds=res["wall_seconds"])
    (OUT / f"independent-input-probe-{VARIANT}.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(json.dumps({k: v for k, v in summ.items() if k != "retained_ids"}, indent=1))
