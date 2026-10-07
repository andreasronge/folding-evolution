"""Throwaway steward probe 1924: collect under saved 1707 C, refit C2, short C2 vs C."""
import json, sys, time, math, multiprocessing as mp, os
import numpy as np
from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.composition_search import search
from experiments.chem_tape.crossed_learning_run import TRAINING, DEFAULT_BANK, load_bank
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.solver_corpus_fit import transition_counts, fit, R
from experiments.chem_tape.composition_search import Decoder

_, CELLS = load_bank(DEFAULT_BANK); INPUTS = inputs_for("D1331")
CORP = json.load(open(sys.argv[1]))
def job(cid, arm, table, seed): return (CELLS[cid], arm, table, seed, 524288, 256, INPUTS, ALPHABET)
def run_tape(j): return search(j, return_solver=True)
def run(j): return search(j)
def cost(r): return math.log2(r["evaluations"] if r["solved"] else 2 * r["cap"])
def ent(t):
    p = np.diff(np.asarray(t), prepend=0, axis=1) / R
    return float(-(p[:24] * np.log2(p[:24])).sum(1).mean())

if __name__ == "__main__":
    os.environ["RAYON_NUM_THREADS"] = "1"
    names = sys.argv[2].split(","); ncoll, nev = int(sys.argv[3]), int(sys.argv[4])
    pool = mp.Pool(10)
    for name in names:
        c = CORP[name]; fam = c["family"]; cells = TRAINING[fam]
        C = np.asarray(c["tables"]["C"])
        t0 = time.time()
        rows = pool.map(run_tape, [job(cid, "C", C, 19240000 + 1000 * k + s) for k, cid in enumerate(cells) for s in range(ncoll)], chunksize=1)
        tc = time.time() - t0
        n, yields = transition_counts(rows, cells)
        fitted, diag = fit(n)
        C2 = fitted["C"]
        distinct = len({tuple(r["solver"]) for r in rows if r["solved"]})
        ws = sum(r["seconds"] for r in rows)
        print(name, "collect", len(rows), "yields", yields, "distinct", distinct, "wall %.0fs worker %.0fs" % (tc, ws),
              "row entropy G4/C/C2 %.2f/%.2f/%.2f" % (ent(__import__("experiments.chem_tape.four_reducer_maps",fromlist=["x"]).tables()["G4"]), ent(C), ent(C2)), flush=True)
        t0 = time.time()
        jobs = [(cid, s) for k, cid in enumerate(cells) for s in range(19340000 + 1000 * k, 19340000 + 1000 * k + nev)]
        rc = pool.map(run, [job(cid, "C", C, s) for cid, s in jobs], chunksize=1)
        r2 = pool.map(run, [job(cid, "C2", C2, s) for cid, s in jobs], chunksize=1)
        d = [cost(a) - cost(b) for a, b in zip(r2, rc)]
        m = np.mean(d); se = np.std(d, ddof=1) / math.sqrt(len(d))
        print(name, "eval %d pairs wall %.0fs" % (len(d), time.time() - t0),
              "C %.2f C2 %.2f  C2-C %.3f se %.3f  solved C %d C2 %d  sec/search C %.2f C2 %.2f" % (
              np.mean([cost(r) for r in rc]), np.mean([cost(r) for r in r2]), m, se,
              sum(r["solved"] for r in rc), sum(r["solved"] for r in r2),
              np.mean([r["seconds"] for r in rc]), np.mean([r["seconds"] for r in r2])), flush=True)
