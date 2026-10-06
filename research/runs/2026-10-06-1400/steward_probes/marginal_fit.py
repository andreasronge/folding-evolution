"""Steward probe: can G-based token multipliers match each saved R map's emitted
token frequencies (exact 32-position Markov propagation, no sampling)?"""
import json, numpy as np
O = "experiments/output/2026-10-06/2026-10-06-0811-contextual-continuation"
maps = json.load(open(O + "/final_maps.json"))
R, L, BOUND, MINC = 23000, 32, np.log(16.0), 250
u = np.tile(np.arange(1, 24) * 1000, (24, 1)); g = u.copy()
s = np.full(23, 500); s[1] = 12000; g[23] = np.cumsum(s)
a = np.full(23, 500); a[[5, 11]] = 2250; a[[18, 22]] = 4500; g[1] = np.cumsum(a)
b = np.full(23, 500); b[[1, 7, 9, 17]] = 3375
for t in (2, 3, 5, 6, 7, 8, 11, 15, 16, 17, 18, 19, 22): g[t] = np.cumsum(b)
Gw = np.diff(g, prepend=0, axis=1).astype(float)

def probs(counts):
    return counts / counts.sum(1, keepdims=True)

def emitted(P):
    d = P[23].copy(); tot = d.copy()
    for _ in range(L - 1):
        d = d @ P[:23]; tot += d
    return tot / L

def floor_norm(w):  # float version of normalize(): 250 floor, proportional fill
    out = []
    for row in w:
        fixed = np.zeros(23, bool)
        while True:
            sh = row * (R - MINC * fixed.sum()) / row[~fixed].sum(); sh[fixed] = MINC
            nf = (~fixed) & (sh < MINC)
            if not nf.any(): break
            fixed |= nf
        out.append(sh)
    return np.array(out)

def fit(target):
    m = np.zeros(23)
    for _ in range(3000):
        f = emitted(probs(floor_norm(Gw * np.exp(m)[None, :])))
        m = np.clip(m + 0.5 * np.log(target / f), -BOUND, BOUND)
    f = emitted(probs(floor_norm(Gw * np.exp(m)[None, :])))
    return m, f

rows = []
for k, v in maps.items():
    if not k.startswith("R") or k.startswith("R_abl"): continue
    t = emitted(probs(np.diff(np.array(v["table"]), prepend=0, axis=1).astype(float)))
    pair = k[1:]
    tp = emitted(probs(np.diff(np.array(maps["M+" + pair]["table"]), prepend=0, axis=1).astype(float)))
    ta = emitted(probs(np.diff(np.array(maps["R_abl" + pair]["table"]), prepend=0, axis=1).astype(float)))
    m, f = fit(t)
    tv = lambda x, y: 0.5 * np.abs(x - y).sum()
    rows.append(dict(map=k, tv_fit=tv(f, t), max_rel=float(np.max(np.abs(f / t - 1))),
                     at_bound=int(np.sum(np.abs(m) > BOUND - 1e-6)),
                     tv_R_vs_Mplus=tv(t, tp), tv_R_vs_Rabl=tv(t, ta),
                     ifgt_R=float(t[9]) if False else None))
    print(f"{k:6s} TV(fit,R)={tv(f,t):.4f} maxrel={np.max(np.abs(f/t-1)):.3f} "
          f"at_bound={int(np.sum(np.abs(m)>BOUND-1e-6))}  TV(R,M+)={tv(t,tp):.3f} TV(R,R_abl)={tv(t,ta):.3f}")
