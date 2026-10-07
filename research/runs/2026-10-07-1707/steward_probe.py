"""Throwaway steward probe 1707: corpus yield, fit, short fresh comparison."""
import inspect, json, sys, time, multiprocessing as mp
import numpy as np
from scipy.optimize import minimize
import experiments.chem_tape.composition_search as cs
from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.four_reducer_maps import tables, marginal
from experiments.chem_tape.map_learning import normalize
from experiments.chem_tape.crossed_learning_run import load_bank, TRAINING, DEFAULT_BANK

src = inspect.getsource(cs.search)
src = src.replace("def search(job)", "def search_tape(job)")
src = src.replace("solved_at = evaluations\n                break",
                  "solved_at = evaluations\n                solver = programs[i].tolist()\n                break")
src = src.replace("    shortcuts = 0\n", "    shortcuts = 0\n    solver = None\n", 1)
src = src.replace("        initial_reencoded=reencoded,\n    )", "        initial_reencoded=reencoded,\n        solver=solver,\n    )")
ns = dict(vars(cs)); exec(src, ns); search_tape = ns["search_tape"]; search_tape.__module__ = "__main__"
assert "solver=solver" in src and "solver = programs" in src

G4 = tables()["G4"]; R = 24000
_, CELLS = load_bank(DEFAULT_BANK); INPUTS = inputs_for("D1331")

def job(cid, arm, table, seed, cap=524288):
    return (CELLS[cid], arm, table, seed, cap, 256, INPUTS, ALPHABET)

def counts_of(rows, cells):
    n = np.zeros((25, 24)); per = {c: np.zeros((25, 24)) for c in cells}
    for r in rows:
        if r["solver"] is None: continue
        prev = 24
        for t in r["solver"]:
            per[r["cell"]][prev, t] += 1; prev = t
    for c in cells:  # equal task weight
        tot = per[c].sum(); n += per[c] / tot * 32 * 50 if tot else 0
    return n

def fit_T(n):
    g = np.diff(G4, prepend=0, axis=1) / R
    def f(lw):
        w = np.exp(lw); q = g * w; q /= q.sum(1, keepdims=True)
        ll = (n * np.log(q)).sum()
        grad = n.sum(0) - (n.sum(1, keepdims=True) * q).sum(0)
        return -ll, -grad
    res = minimize(f, np.zeros(24), jac=True, method="L-BFGS-B", bounds=[(-np.log(16), np.log(16))] * 24)
    return normalize(g * np.exp(res.x)[None, :], R), res.x

def fit_C(n, alpha):
    g = np.diff(G4, prepend=0, axis=1) / R
    p = (n + alpha * g) / (n.sum(1, keepdims=True) + alpha)
    return normalize(p, R)

def emitted(table):
    p = np.diff(table, prepend=0, axis=1) / R
    pos = p[24].copy(); tot = pos.copy()
    for _ in range(31):
        pos = pos @ p[:24]; tot += pos
    return tot / 32

def fit_K(target):
    g = np.diff(G4, prepend=0, axis=1) / R; lw = np.zeros(24)
    for _ in range(400):
        t = normalize(g * np.exp(lw)[None, :], R)
        lw += 0.7 * (np.log(target) - np.log(emitted(t)))
    t = normalize(g * np.exp(lw)[None, :], R)
    return t, np.abs(emitted(t) - target).max()

if __name__ == "__main__":
    import os; os.environ["RAYON_NUM_THREADS"] = "1"
    ncoll, nev = int(sys.argv[1]), int(sys.argv[2])
    pool = mp.Pool(10); out = {}
    for fam, cells in TRAINING.items():
        t0 = time.time()
        rows = pool.map(search_tape, [job(c, "G4", G4, 17070000 + 1000 * k + s) for k, c in enumerate(cells) for s in range(ncoll)], chunksize=1)
        tc = time.time() - t0
        n = counts_of(rows, cells)
        T, lwT = fit_T(n)
        C = fit_C(n, 50.0); C2 = fit_C(n, 400.0)
        K, kerr = fit_K(emitted(C))
        print(fam, "collect", len(rows), "solved", sum(r["solved"] for r in rows), "wall %.0fs" % tc, "Kerr %.4f" % kerr, flush=True)
        print("  T multipliers", np.round(np.exp(lwT), 2).tolist())
        print("  emitted G4/T/C top", [(int(i), round(float(emitted(m)[i]), 3)) for m in (G4, T, C) for i in np.argsort(-emitted(m))[:4]])
        g = np.diff(G4, prepend=0, axis=1) / R
        for name, tab in (("T", T), ("C", C)):
            p = np.diff(tab, prepend=0, axis=1) / R
            # held-in log-lik per transition vs G4
            print("  ll/trans", name, round(float((n * (np.log(p) - np.log(g))).sum() / n.sum()), 3))
        arms = {"G4": G4, "T": T, "C": C, "C400": C2, "K": K}
        t0 = time.time()
        ev = pool.map(cs.search, [job(c, a, arms[a], 17170000 + 1000 * k + s) for k, c in enumerate(cells) for s in range(nev) for a in arms], chunksize=1)
        print("  eval wall %.0fs" % (time.time() - t0))
        for a in arms:
            r = [x for x in ev if x["arm"] == a]
            le = np.array([np.log2(x["evaluations"] if x["solved"] else 2 * 524288) for x in r])
            print("  ", a, "solved %d/%d" % (sum(x["solved"] for x in r), len(r)), "mean log2 %.2f" % le.mean(), "mean s %.2f" % np.mean([x["seconds"] for x in r]))
        out[fam] = dict(n=n.tolist(), ev=[{k: x[k] for k in ("cell", "arm", "seed", "solved", "evaluations", "seconds")} for x in ev])
    json.dump(out, open("/tmp/probefull/out.json", "w"))
