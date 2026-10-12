"""Decompose per-generation change in gate fraction: selection, redraw, elites; project pre-solve f on the dose curve."""
import json, collections
from pathlib import Path
import numpy as np
R = Path('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-12')
FAMS = ('order', 'gate'); B, P = 24, 8
acc = collections.defaultdict(lambda: collections.defaultdict(list))
first_solve_f = collections.defaultdict(list)   # (fam, arm) -> f at first solve, every solved episode
pre_len = collections.defaultdict(list)
with open(R/'2026-10-12-0250-exposure'/'exposure.jsonl') as f:
    for line in f:
        d = json.loads(line); k = (d['family'], d['arm'])
        for ep in d['episodes']:
            tr = ep['modifier_trace']
            for t in tr:
                if t['counters'] is None: continue
                ph = t['phase']
                acc[k][ph+'_sel'].append(t['recipient_f']-t['census_f'])
                acc[k][ph+'_redraw'].append(t['post_mutation_f']-t['pre_mutation_f'])
                acc[k][ph+'_elite'].append(t['next_f']-t['post_mutation_f'])
                acc[k][ph+'_total'].append(t['next_f']-t['census_f'])
                acc[k][ph+'_pull'].append((0.5-t['pre_mutation_f'])/32)
                acc[k][ph+'_f'].append(t['census_f'])
            if ep['solved']:
                first = ep['first_solve_evaluations']
                first_solve_f[k].append(tr[first//256-1]['census_f']); pre_len[k].append(first//256)
print('Per-generation decomposition of delta f (mean over generations; "pull" = expected redraw (0.5-f)/32):')
print(f'{"fam/arm":10s} {"phase":5s} {"gens":>8s} {"mean f":>7s} {"selection":>10s} {"redraw":>8s} {"pull":>8s} {"elite":>8s} {"total":>8s}')
for k in sorted(acc):
    for ph in ('pre', 'post'):
        a = acc[k]
        print(f'{k[0]+"/"+k[1]:10s} {ph:5s} {len(a[ph+"_sel"]):8d} {np.mean(a[ph+"_f"]):7.3f} {np.mean(a[ph+"_sel"]):+10.4f} {np.mean(a[ph+"_redraw"]):+8.4f} {np.mean(a[ph+"_pull"]):+8.4f} {np.mean(a[ph+"_elite"]):+8.4f} {np.mean(a[ph+"_total"]):+8.4f}')
print('\nf at first solve (all solved episodes) and pre-solve generations:')
for k in sorted(first_solve_f):
    v = np.array(first_solve_f[k]); g = np.array(pre_len[k])
    print(f'{k}: n={len(v)} mean f at first solve {v.mean():.3f}; median pre-solve generations {np.median(g):.0f}, mean {g.mean():.1f}; share of 64 gens pre-solve (solved eps) {g.mean()/64:.2f}')

# ---- dose-curve projection from readout rows, excluding L-matched (predict L-matched from other laws' f) ----
rows = []
with open(R/'2026-10-12-0250-readout'/'score.jsonl') as f:
    for line in f:
        d = json.loads(line)
        if d['population'] is None: continue
        rows.append((d['family'], d['arm'], d['build'], d['population'], d['gate_fraction'], d['evaluations']))
cost = collections.defaultdict(list)
for fam, arm, b, p, fr, ev in rows: cost[fam, arm, b, p].append(ev)
pts = {fam: [] for fam in FAMS}
for (fam, arm, b, p), v in cost.items():
    pts[fam].append((arm, rows and next(fr for f2, a2, b2, p2, fr, ev in rows if (f2, a2, b2, p2) == (fam, arm, b, p)), np.mean(v)))
edges = np.array([0, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 1.0001])
for fam in FAMS:
    arr = np.array([(fr, c) for a, fr, c in pts[fam] if a != 'L-matched'])
    M = np.mean([c for a, fr, c in pts[fam] if a == 'M'])
    binmean = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = arr[(arr[:,0] >= lo) & (arr[:,0] < hi)]
        binmean.append(sel[:,1].mean() if len(sel) else np.nan)
    binmean = np.array(binmean)
    def predict(fs):
        idx = np.clip(np.searchsorted(edges, fs, side='right')-1, 0, len(binmean)-1)
        return np.nanmean(binmean[idx])
    fL = np.array([fr for a, fr, c in pts[fam] if a == 'L-matched'])
    actual = np.mean([c for a, fr, c in pts[fam] if a == 'L-matched'])
    print(f'\n{fam}: dose bins (S, N, L-swapped populations only; cost/M): ' + ' '.join(f'[{lo:.2f},{hi:.2f}):{bm/M:.2f}' for lo, hi, bm in zip(edges[:-1], edges[1:], binmean)))
    print(f'  L-matched: mean f {fL.mean():.3f}, sd {fL.std():.3f}; actual cost/M {actual/M:.3f}; predicted from own f distribution {predict(fL)/M:.3f}; predicted at a single f = mean {predict(np.array([fL.mean()]))/M:.3f}')
    fs = np.array(first_solve_f[fam, 'L'])
    print(f'  projection (not measured): deploying f at first solve (mean {fs.mean():.3f}, sd {fs.std():.3f}) would cost about {predict(fs)/M:.2f} of M on this dose curve')
    print(f'  reference: own pure library cost/M = {np.mean([c for a,fr,c in pts[fam] if a=="M"])*0+ (0.725 if fam=="order" else 0.778):.3f}')
