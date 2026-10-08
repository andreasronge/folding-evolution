import sys, os, json, time
os.environ["RAYON_NUM_THREADS"] = "1"
sys.path[:0] = ["/tmp/probe", "/tmp/rmain", "/tmp/rmain/src"]
import numpy as np, itertools
from multiprocessing import Pool
def build():
    from experiments.chem_tape.assembly_bank import inputs_for
    from experiments.chem_tape.four_reducer_bank import REDUCERS
    xs = np.asarray(inputs_for("D1331"))
    r = dict(S=xs.sum(1), M=xs.max(1), m=xs.min(1), F=xs[:, 0])
    scr = json.load(open("/tmp/probe/roster_screen.json"))
    out = {}
    for fam in ("BE", "PA"):
        ret = sorted([c for c in scr if c["fam"] == fam and c["retained"]], key=lambda c: sorted(c["ids"])[0])
        pick = ret[:: len(ret) // 6][:6]
        for c in pick:
            cid = sorted(c["ids"])[0]
            body = cid[3:]
            if fam == "BE":
                A, B = body[0], body[2]; C = body[4]; D, E = body[6], body[8]
                lab = np.where(r[A] > r[B], r[C], r[D] + r[E])
            else:
                A, B = body[1], body[3]; C = body[5]; D = body[7]; E = body[10]
                lab = np.where(r[A] > r[B], r[C], r[D]) + r[E]
            out[cid] = dict(id=cid, labels=lab.tolist(), agree=c["agree"])
    return out, inputs_for("D1331")
def run(job):
    from experiments.chem_tape.composition_search import search
    row = search(job)
    return job[0]["id"], row["solved"], row["evaluations"], row["seconds"], row["shortcuts"]
if __name__ == "__main__":
    from experiments.chem_tape.four_reducer_maps import tables
    import folding_evolution; print(folding_evolution.__file__)
    cells, inputs = build()
    g4 = tables()["G4"]
    jobs = [(c, "G4", g4, 12460000 + i * 100 + s, 524288, 256, inputs, "v2_rmin_first") for i, c in enumerate(cells.values()) for s in range(int(sys.argv[1]))]
    t0 = time.monotonic()
    with Pool(10) as p:
        res = p.map(run, jobs, chunksize=1)
    print("wall", round(time.monotonic() - t0, 1), "searches", len(jobs))
    json.dump([list(r) for r in res], open("/tmp/probe/search_res.json", "w"))
    by = {}
    for cid, solved, ev, sec, sc in res:
        by.setdefault(cid, []).append((solved, ev, sec, sc))
    for cid, rs in by.items():
        ev = [e if s else 2*524288 for s, e, _, _ in rs]
        print(f"{cid:22s} agree {cells[cid]['agree']:.3f} solved {sum(s for s,_,_,_ in rs)}/{len(rs)} median {int(np.median(ev))} sec {np.mean([x for _,_,x,_ in rs]):.1f} shortcuts {sum(x for *_,x in rs)}")
