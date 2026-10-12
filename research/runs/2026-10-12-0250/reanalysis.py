"""Reviewer re-analysis of 2026-10-12-0250 from the raw rows (independent of report.json).
Run from the worktree root: PYTHONPATH=. .venv/bin/python research/runs/2026-10-12-0250/reanalysis.py
"""
import json, collections, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = Path('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-12')
T = Path('/Users/andreas/developer/folding-evolution/research/runs/2026-10-12-0250')
FIG = T/'figs'
FAMS = ('order', 'gate'); LAWS = ('L-matched', 'L-swapped', 'S', 'N', 'M'); PURE = ('O', 'G')
B, P = 24, 8

# ---------------- score rows ----------------
rows = []
with open(R/'2026-10-12-0250-readout'/'score.jsonl') as f:
    for line in f:
        d = json.loads(line)
        rows.append(dict(family=d['family'], build=d['build'], population=d['population'], cell=d['cell'],
                         repeat=d['repeat'], arm=d['arm'], f=d['gate_fraction'], solved=d['solved'],
                         ev=d['evaluations'], ws=d['worker_seconds'], attempts=len(d['attempts'])))
print('score rows', len(rows))
print('unsolved by family/arm:', collections.Counter((r['family'], r['arm']) for r in rows if not r['solved']))
print('attempts distribution (restarts used):', collections.Counter(r['attempts'] for r in rows))

def arrays(metric):
    out = {}
    for fam in FAMS:
        for law in LAWS+PURE:
            by = collections.defaultdict(list)
            for r in rows:
                if r['family'] == fam and r['arm'] == law:
                    by[r['build'], r['population']].append(r[metric])
            out[fam, law] = np.array([[np.mean(by[b, None if law in PURE else p]) for p in range(P)] for b in range(B)])
    return out
cost = arrays('ev')

def boot(arrs, draws=8192, seed=20261012):
    rng = np.random.default_rng(seed)
    bi = rng.integers(0, B, size=(draws, B))
    pi = rng.integers(0, P, size=(draws, B, P))
    out = {}
    for k, a in arrs.items():
        # a[b, p]; sample builds then populations within each build
        samp = a[bi[:, :, None], pi]          # draws x B x P
        out[k] = samp.mean(axis=(1, 2))
    return out
S = boot(cost)
def est(point, draws):
    lo, hi = np.percentile(draws, [2.5, 97.5]); return point, lo, hi
def ratio(fam, n, d):
    return est(cost[fam, n].mean()/cost[fam, d].mean(), S[fam, n]/S[fam, d])

print('\n== capped mean evaluations per law (mean over builds and populations)')
for fam in FAMS:
    print(fam, {law: round(cost[fam, law].mean()) for law in LAWS+PURE})
print('\n== ratios (my bootstrap, seed 20261012)')
contr = [('L-matched', 'M'), ('L-matched', 'L-swapped'), ('L-swapped', 'M'), ('S', 'M'), ('N', 'M'), ('L-matched', 'S'), ('L-matched', 'N'), ('O', 'M'), ('G', 'M')]
rat = {}
for fam in FAMS:
    for n, d in contr:
        p, lo, hi = ratio(fam, n, d); rat[fam, n, d] = (p, lo, hi)
        print(f'{fam:5s} {n}/{d:12s} {p:.3f} [{lo:.3f}, {hi:.3f}]')
pr = np.sqrt(np.prod([cost[f, 'L-matched'].mean()/cost[f, 'M'].mean() for f in FAMS]))
pd = np.sqrt(np.prod([S[f, 'L-matched']/S[f, 'M'] for f in FAMS], axis=0))
print(f'PRIMARY R (geo mean L-matched/M): {pr:.3f} [{np.percentile(pd,2.5):.3f}, {np.percentile(pd,97.5):.3f}]')
hr = np.sqrt((cost['order','O'].mean()/cost['order','M'].mean())*(cost['gate','G'].mean()/cost['gate','M'].mean()))
hd = np.sqrt((S['order','O']/S['order','M'])*(S['gate','G']/S['gate','M']))
print(f'HEADROOM own-pure/M pooled: {hr:.3f} [{np.percentile(hd,2.5):.3f}, {np.percentile(hd,97.5):.3f}]')
# swapped-pure as a bound: what would the mixture-wrong-way cost
ws = arrays('ws'); 
for fam in FAMS:
    print(f'{fam} worker-s L-matched/M point {ws[fam,"L-matched"].mean()/ws[fam,"M"].mean():.3f}')

print('\n== per build / per population counts, L-matched vs M (same seeds)')
for fam in FAMS:
    bl = (cost[fam, 'L-matched'].mean(axis=1) < cost[fam, 'M'].mean(axis=1)).sum()
    pl = (cost[fam, 'L-matched'] < cost[fam, 'M']).sum()
    bs = (cost[fam, 'L-matched'].mean(axis=1) < cost[fam, 'L-swapped'].mean(axis=1)).sum()
    ps = (cost[fam, 'L-matched'] < cost[fam, 'L-swapped']).sum()
    print(f'{fam}: L-matched < M in {bl}/24 builds, {pl}/192 populations; L-matched < L-swapped in {bs}/24 builds, {ps}/192 populations')
    rb = cost[fam, 'L-matched'].mean(axis=1)/cost[fam, 'M'].mean(axis=1)
    print(f'   per-build L-matched/M ratios: min {rb.min():.2f} median {np.median(rb):.2f} max {rb.max():.2f}')

print('\n== per cell L-matched/M and O/M, G/M (point, all rows)')
for fam in FAMS:
    cells = sorted(set(r['cell'] for r in rows if r['family'] == fam))
    for c in cells:
        m = {law: np.mean([r['ev'] for r in rows if r['family']==fam and r['cell']==c and r['arm']==law]) for law in LAWS+PURE}
        print(f'{fam} {c}: L-matched/M {m["L-matched"]/m["M"]:.2f}  L-swapped/M {m["L-swapped"]/m["M"]:.2f}  S/M {m["S"]/m["M"]:.2f}  N/M {m["N"]/m["M"]:.2f}  O/M {m["O"]/m["M"]:.2f}  G/M {m["G"]/m["M"]:.2f}')

print('\n== robustness: drop capped (unsolved) rows')
for fam in FAMS:
    def mean_law(law, drop):
        return np.mean([r['ev'] for r in rows if r['family']==fam and r['arm']==law and (r['solved'] or not drop)])
    print(f'{fam} L-matched/M all rows {mean_law("L-matched",False)/mean_law("M",False):.3f}; solved only {mean_law("L-matched",True)/mean_law("M",True):.3f}')

# ---------------- dose curve from readout: cost vs f per population-law ----------------
print('\n== dose curve: readout cost against deployed gate fraction f (population laws pooled; same cells/seeds)')
fpts = {fam: [] for fam in FAMS}
fmap = {}
for r in rows:
    if r['population'] is not None:
        fmap[(r['family'], r['arm'], r['build'], r['population'])] = r['f']
for fam in FAMS:
    for law in LAWS[:4]:
        for b in range(B):
            for p in range(P):
                fpts[fam].append((fmap[fam, law, b, p], cost[fam, law][b, p], law))
edges = [0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0001]
dose = {}
for fam in FAMS:
    arr = np.array([(f, c) for f, c, _ in fpts[fam]])
    M = cost[fam, 'M'].mean()
    rho = np.corrcoef(np.argsort(np.argsort(arr[:,0])), np.argsort(np.argsort(arr[:,1])))[0,1]
    print(f'{fam}: {len(arr)} population-laws, Spearman(f, cost) = {rho:.3f}; M (f=0.5) = {M:.0f}; O (f=0) = {cost[fam,"O"].mean():.0f}; G (f=1) = {cost[fam,"G"].mean():.0f}')
    dose[fam] = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = arr[(arr[:,0] >= lo) & (arr[:,0] < hi)]
        if len(sel):
            dose[fam].append((lo, hi, len(sel), sel[:,1].mean(), sel[:,1].mean()/M))
            print(f'   f in [{lo:.1f},{hi:.1f}): n={len(sel):3d} mean cost {sel[:,1].mean():8.0f}  /M = {sel[:,1].mean()/M:.2f}')
    # quadratic fit through population-law points plus pure endpoints (weighted equally per point)
    X = np.concatenate([arr[:,0], np.zeros(B), np.ones(B)]); Y = np.concatenate([arr[:,1], cost[fam,'O'][:,0], cost[fam,'G'][:,0]])
    coef = np.polyfit(X, np.log(Y), 2)
    pred = lambda f: np.exp(np.polyval(coef, f))
    print(f'   log-quadratic fit: cost(f)/M at f=0.25 {pred(0.25)/M:.2f}, 0.38 {pred(0.38)/M:.2f}, 0.5 {pred(0.5)/M:.2f}, 0.62 {pred(0.62)/M:.2f}, 0.75 {pred(0.75)/M:.2f}')
    dose[fam+'_fit'] = (coef, M, arr)

# ---------------- exposure rows ----------------
print('\n== exposure (streamed)')
traj = []
ep_keys_printed = False
with open(R/'2026-10-12-0250-exposure'/'exposure.jsonl') as f:
    for line in f:
        d = json.loads(line)
        if not ep_keys_printed:
            ep = d['episodes'][0]; tr = ep['modifier_trace'][0]
            print('episode keys:', sorted(k for k in ep if k != 'modifier_trace'))
            print('trace keys:', sorted(tr))
            ep_keys_printed = True
        eps = []
        census = []; phase = []; seldiff = []
        for ep in d['episodes']:
            tr = ep['modifier_trace']
            cf = [t['census_f'] for t in tr]
            census.extend(cf); phase.extend(t['phase'] for t in tr)
            seldiff.extend((t['recipient_f']-t['census_f']) if t['counters'] is not None else np.nan for t in tr)
            first = ep['first_solve_evaluations']
            f_at_solve = None if first is None else tr[first//256-1]['census_f']
            eps.append(dict(solved=ep['solved'], first=first, initial=ep['initial_f'], final=ep['final_f'],
                            min_f=min(cf), f_at_solve=f_at_solve, pre=ep['pre_solve_delta'], post=ep['post_solve_delta'],
                            gens_pre=sum(1 for t in tr if t['phase']=='pre')))
        traj.append(dict(family=d['family'], build=d['build'], arm=d['arm'], repeat=d['repeat'], final_f=d['final_f'],
                         eps=eps, census=np.array(census), phase=np.array(phase), seldiff=np.array(seldiff, dtype=float),
                         ws=d['worker_seconds']))
print('trajectories', len(traj), collections.Counter((t['family'], t['arm']) for t in traj))

for fam in FAMS:
    for arm in ('L', 'S', 'N'):
        tt = [t for t in traj if t['family']==fam and t['arm']==arm]
        ff = np.array([t['final_f'] for t in tt])
        solves = sum(e['solved'] for t in tt for e in t['eps'])
        pre = np.array([e['pre'] for t in tt for e in t['eps']]); post = np.array([e['post'] for t in tt for e in t['eps'] if e['post'] is not None])
        gens_pre = np.array([e['gens_pre'] for t in tt for e in t['eps'] if e['solved']])
        sd_pre = np.nanmean(np.concatenate([t['seldiff'][t['phase']=='pre'] for t in tt]))
        sd_post = np.nanmean(np.concatenate([t['seldiff'][t['phase']=='post'] for t in tt]))
        # final episode: f at first solve vs end
        last = [t['eps'][-1] for t in tt]
        fs = [e['f_at_solve'] for e in last if e['f_at_solve'] is not None]
        print(f'{fam}/{arm}: n={len(tt)} final f mean {ff.mean():.3f} sd {ff.std():.3f} min {ff.min():.2f} max {ff.max():.2f}; '
              f'<0.25: {(ff<0.25).sum()}, <0.5: {(ff<0.5).sum()}, >0.5: {(ff>0.5).sum()}, >0.75: {(ff>0.75).sum()}; '
              f'episodes solved {solves}/{12*len(tt)}; median pre-solve gens (solved eps) {np.median(gens_pre):.0f}; '
              f'mean pre-solve delta {pre.mean():+.3f}, maintenance delta {post.mean():+.3f} (n={len(post)}); '
              f'sel diff per gen pre {sd_pre:+.4f} post {sd_post:+.4f}; last-episode f at first solve mean {np.mean(fs):.3f} (n={len(fs)}) vs final {ff.mean():.3f}')
# episode-by-episode mean start/end for L arms
print('\n== per-episode mean f (L arms): start -> at first solve (solved eps) -> end')
for fam in FAMS:
    tt = [t for t in traj if t['family']==fam and t['arm']=='L']
    line = []
    for e in range(12):
        st = np.mean([t['eps'][e]['initial'] for t in tt]); en = np.mean([t['eps'][e]['final'] for t in tt])
        fs = [t['eps'][e]['f_at_solve'] for t in tt if t['eps'][e]['f_at_solve'] is not None]
        line.append(f'{st:.2f}->{np.mean(fs):.2f}->{en:.2f}')
    print(fam, ' | '.join(line))
# L minus S/N final f with build-level paired bootstrap (populations nested)
print('\n== frequency contrasts (my bootstrap)')
fin = {}
for fam in FAMS:
    for arm in ('L','S','N'):
        a = np.zeros((B,P))
        for t in traj:
            if t['family']==fam and t['arm']==arm: a[t['build'], t['repeat']] = t['final_f']
        fin[fam, arm] = a
FS = boot(fin)
for fam in FAMS:
    for arm in ('S','N'):
        d = fin[fam,'L'].mean()-fin[fam,arm].mean(); dd = FS[fam,'L']-FS[fam,arm]
        print(f'{fam} L-{arm}: {d:+.3f} [{np.percentile(dd,2.5):+.3f}, {np.percentile(dd,97.5):+.3f}]; L lower than {arm} in {(fin[fam,"L"].mean(axis=1)<fin[fam,arm].mean(axis=1)).sum()}/24 builds')

# correlation: within order/L, does the endpoint f predict readout cost? (L-matched pops)
print('\n== within L-matched: endpoint f vs own readout cost')
for fam in FAMS:
    fs = np.array([fin[fam,'L'][b,p] for b in range(B) for p in range(P)])
    cs = np.array([cost[fam,'L-matched'][b,p]/cost[fam,'M'][b,p] for b in range(B) for p in range(P)])
    rho = np.corrcoef(np.argsort(np.argsort(fs)), np.argsort(np.argsort(cs)))[0,1]
    lo = cs[fs < np.median(fs)].mean(); hi = cs[fs >= np.median(fs)].mean()
    print(f'{fam}: Spearman(f, L-matched/M per population) = {rho:.3f}; mean per-pop ratio below-median f {lo:.3f}, above-median f {hi:.3f} (median f {np.median(fs):.3f})')

# ---------------- figures ----------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
for ax, fam in zip(axes, FAMS):
    coef, M, arr = dose[fam+'_fit']
    for law, c in zip(LAWS[:4], ['tab:blue','tab:orange','tab:green','tab:gray']):
        pts = [(f, cc) for f, cc, l in fpts[fam] if l == law]
        ax.scatter([p[0] for p in pts], [p[1]/M for p in pts], s=8, alpha=0.5, color=c, label=law)
    ax.scatter([0]*B, cost[fam,'O'][:,0]/M, s=14, color='black', marker='v', label='O (f=0)')
    ax.scatter([1]*B, cost[fam,'G'][:,0]/M, s=14, color='black', marker='^', label='G (f=1)')
    xs = np.linspace(0, 1, 101); ax.plot(xs, np.exp(np.polyval(coef, xs))/M, color='red', label='log-quadratic fit')
    ax.axhline(1, color='black', linestyle='--', linewidth=0.8)
    ax.set(xlabel='deployed gate fraction f', ylabel='capped mean evaluations / M (f=0.5)', title=f'{fam} family readout', ylim=(0, 3.5 if fam=='order' else 2.5))
    ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(FIG/'dose_curve.png', dpi=130); plt.close(fig)

fig, axes = plt.subplots(2, 3, figsize=(13, 6), sharex=True)
for i, fam in enumerate(FAMS):
    for j, arm in enumerate(('L','S','N')):
        ff = fin[fam,arm].ravel()
        axes[i,j].hist(ff, bins=np.linspace(0,1,21), color='tab:blue', alpha=0.8)
        axes[i,j].axvline(0.5, color='black', linestyle='--'); axes[i,j].axvline(ff.mean(), color='red')
        axes[i,j].set(title=f'{fam}/{arm}: mean {ff.mean():.3f}', xlabel='final gate fraction f', ylabel='populations (of 192)')
fig.tight_layout(); fig.savefig(FIG/'final_f_hist.png', dpi=130); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, fam in zip(axes, FAMS):
    for arm, c in zip(('L','S','N'), ['tab:blue','tab:orange','tab:green']):
        tt = [t for t in traj if t['family']==fam and t['arm']==arm]
        m = np.mean([t['census'] for t in tt], axis=0)
        ax.plot(m, color=c, label=arm, linewidth=1)
    tt = [t for t in traj if t['family']==fam and t['arm']=='L']
    frac_pre = np.mean([(t['phase']=='pre') for t in tt], axis=0)
    ax2 = ax.twinx(); ax2.plot(frac_pre, color='gray', alpha=0.4, linewidth=0.8); ax2.set_ylabel('share of L trajectories still pre-solve', color='gray'); ax2.set_ylim(0,1)
    ax.axhline(0.5, color='black', linestyle='--', linewidth=0.8)
    for e in range(1,12): ax.axvline(64*e, color='lightgray', linewidth=0.5)
    ax.set(xlabel='generation (12 episodes x 64)', ylabel='mean census gate fraction', title=f'{fam} exposure'); ax.legend(loc='lower left')
fig.tight_layout(); fig.savefig(FIG/'episode_sawtooth.png', dpi=130); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, fam in zip(axes, FAMS):
    lm = cost[fam,'L-matched'].mean(axis=1); m = cost[fam,'M'].mean(axis=1); ls = cost[fam,'L-swapped'].mean(axis=1)
    ax.scatter(m, lm, s=20, label='L-matched'); ax.scatter(m, ls, s=20, marker='x', label='L-swapped')
    lim = [0, max(m.max(), lm.max(), ls.max())*1.05]; ax.plot(lim, lim, color='black', linewidth=0.8)
    ax.set(xlabel='M cost per build (capped mean evals)', ylabel='endpoint-law cost per build', title=f'{fam}: 24 paired builds'); ax.legend()
fig.tight_layout(); fig.savefig(FIG/'paired_builds.png', dpi=130); plt.close(fig)
print('figures written to', FIG)
