"""Exhaustive 1- and 2-point mutation neighbourhoods of stuck AND-task genomes."""
import sys, itertools, json, os, numpy as np
from multiprocessing import Pool
sys.path.insert(0, "experiments/chem_tape")
from arrival_frequent import collect_runs, _make_cfg

def setup():
    out = []
    for key, runs in collect_runs().items():
        if key[0] == "sum_gt_10_AND_max_gt_5" and key[5] == "preserve":
            out += [(r["config"], r["genotype_hex"], r["seed"]) for r in runs if r["pop_size"] == 1024]
    return out

def work(item):
    c, hx, seed = item
    from folding_evolution.chem_tape.evaluate import evaluate_population
    from folding_evolution.chem_tape.evolve import _token_max
    from folding_evolution.chem_tape.tasks import build_task
    cfg = _make_cfg(c); task = build_task(cfg, 0); hi = _token_max(cfg) + 1
    g = np.frombuffer(bytes.fromhex(hx), dtype=np.uint8).copy(); L = len(g)
    f0, p0 = evaluate_population([g], task, cfg); f0 = float(f0[0])
    mx = np.array([max(x) > 5 for x in task.inputs]); sm = np.array([sum(x) > 10 for x in task.inputs])
    kind = "max>5" if (p0[0] == mx).all() else "sum>10" if (p0[0] == sm).all() else "other"
    # single mutants, indexed [pos, token]
    f1 = np.full((L, hi), f0)
    m1, idx = [], []
    for i in range(L):
        for t in range(hi):
            if t != g[i]:
                h = g.copy(); h[i] = t; m1.append(h); idx.append((i, t))
    ff, _ = evaluate_population(m1, task, cfg)
    for (i, t), v in zip(idx, ff): f1[i, t] = v
    # double mutants
    n2 = tot2 = 0; best2 = 0.0; solvers = []
    for i, j in itertools.combinations(range(L), 2):
        B, bi = [], []
        for a in range(hi):
            if a == g[i]: continue
            for b in range(hi):
                if b == g[j]: continue
                h = g.copy(); h[i] = a; h[j] = b; B.append(h); bi.append((a, b))
        f, _ = evaluate_population(B, task, cfg)
        tot2 += len(B); best2 = max(best2, float(f.max()))
        for (a, b), v in zip(bi, f):
            if v >= 0.999:
                n2 += 1
                solvers.append((i, a, j, b, float(f1[i, a]), float(f1[j, b])))
    # valley: are both single steps toward a 2-step solver worse than the parent?
    valley = sum(1 for s in solvers if max(s[4], s[5]) < f0 - 1e-9)
    neutral_path = sum(1 for s in solvers if max(s[4], s[5]) >= f0 - 1e-9)
    return dict(seed=seed, arm=cfg.arm, f0=f0, kind=kind,
                n1=int((ff >= 0.999).sum()), tot1=len(m1), best1=float(ff.max()),
                share1_worse=float((ff < f0 - 1e-9).mean()), share1_neutral=float((abs(ff - f0) < 1e-9).mean()),
                n2=n2, tot2=tot2, best2=best2, valley=valley, neutral_path=neutral_path, solvers=solvers[:50])

if __name__ == "__main__":
    os.environ["RAYON_NUM_THREADS"] = "1"
    with Pool(10) as pool: res = pool.map(work, setup())
    json.dump(res, open(sys.argv[1], "w"))
    for r in sorted(res, key=lambda r: (r["arm"], r["seed"])):
        print(f"{r['arm']:7s} seed {r['seed']:2d} {r['kind']:6s} f0={r['f0']:.3f} | 1-mut: solvers {r['n1']}/{r['tot1']} best {r['best1']:.3f} "
              f"worse {r['share1_worse']:.0%} neutral {r['share1_neutral']:.0%} | 2-mut: solvers {r['n2']}/{r['tot2']} best {r['best2']:.3f} "
              f"(valley {r['valley']}, neutral-first-step {r['neutral_path']})", flush=True)
