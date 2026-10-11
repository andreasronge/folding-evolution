"""Reviewer's independent re-analysis of 1427 (exposure + readout). Writes figs/ and prints numbers."""
import json, sys, math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11')
EXP = OUT / '2026-10-11-1427-exposure'
RD = OUT / '2026-10-11-1427-readout'
FIG = Path('/Users/andreas/developer/folding-evolution/research/runs/2026-10-11-1427/figs')
ARMS = ('L', 'S', 'Z', 'N')
LAWS = ('R-tree', 'initial', 'L-final', 'S-final', 'R-all')

rows = [json.loads(l) for l in (EXP / 'exposure.jsonl').read_text().splitlines()]
scores = [json.loads(l) for l in (RD / 'score.jsonl').read_text().splitlines()]
manifest = json.loads((EXP / 'exposure_manifest.json').read_text())
schedule = json.loads((EXP / 'schedules.json').read_text())

print('## Completeness')
print('exposure rows', len(rows), 'expected', len(schedule['exposure']))
keys = Counter((r['build'], r['arm'], r['repeat']) for r in rows)
print('duplicate exposure keys', sum(v > 1 for v in keys.values()))
print('per arm', Counter(r['arm'] for r in rows))
print('episodes per row', Counter(len(r['episodes']) for r in rows))
print('gens per episode', Counter(e['generations'] for r in rows for e in r['episodes']))
print('score rows', len(scores), 'expected', len(schedule['readout']))
skeys = Counter((s['build'], s['cell'], s['repeat'], s['arm']) for s in scores)
print('duplicate score keys', sum(v > 1 for v in skeys.values()))
print('score per arm', Counter(s['arm'] for s in scores))
print('score per cell x arm all 48:', set(Counter((s['cell'], s['arm']) for s in scores).values()))
bad = [s for s in scores if s['probability'] != manifest['probabilities'][s['build']][s['arm']]]
print('probability mismatches', len(bad))
print('unsolved score rows', sum(not s['solved'] for s in scores), 'all at cap 524288:', all(s['evaluations'] == 524288 for s in scores if not s['solved']))
print('failure.json present:', (EXP/'failure.json').exists(), (RD/'failure.json').exists())

# lead-cell balance
lead = Counter((r['arm'], r['cells'][0]) for r in rows)
print('lead-cell counts per arm', {a: sorted(Counter(c for (aa, c), n in lead.items() if aa == a for _ in range(n)).values()) for a in ARMS})

print('\n## Final frequency')
fin = {a: [r['final_f'] for r in rows if r['arm'] == a] for a in ARMS}
for a in ARMS:
    v = fin[a]
    print(a, 'n', len(v), 'fixed', sum(x == 1 for x in v), 'lost', sum(x == 0 for x in v), 'polymorphic', sum(0 < x < 1 for x in v), 'mean f', round(np.mean(v), 4))

def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h
for a in ARMS:
    k, n = sum(x == 1 for x in fin[a]), len(fin[a])
    print(a, 'trajectory-level fixation', k, '/', n, '=', round(k/n, 3), 'Wilson95', [round(x, 3) for x in wilson(k, n)])

# library-level bootstrap replicate
rng = np.random.default_rng(202610111427)
B = 24
final = {a: np.array([np.mean([r['final_f'] for r in rows if r['build'] == b and r['arm'] == a]) for b in range(B)]) for a in ARMS}
sel = rng.integers(B, size=(8192, B))
for a in ('S', 'Z', 'N'):
    d = final['L'] - final[a]
    print('L -', a, 'point', round(d.mean(), 4), 'boot95', np.round(np.quantile(d[sel].mean(1), [0.025, 0.975]), 4).tolist(),
          'builds L>', a, int((d > 0).sum()), 'L=', int((d == 0).sum()), 'L<', int((d < 0).sum()))
for a in ARMS:
    print(a, 'mean final f', round(final[a].mean(), 4), 'boot95', np.round(np.quantile(final[a][sel].mean(1), [0.025, 0.975]), 4).tolist())
# S vs Z vs N contrast
for x, y in (('S', 'Z'), ('S', 'N'), ('Z', 'N')):
    d = final[x] - final[y]
    print(x, '-', y, 'point', round(d.mean(), 4), 'boot95', np.round(np.quantile(d[sel].mean(1), [0.025, 0.975]), 4).tolist())

print('\n## Absorption timing (episode index 0-11 at whose end the trajectory was first at 0 or 1 and stayed)')
def absorb_episode(r):
    for e in r['episodes']:
        if e['final_f'] in (0.0, 1.0):
            return e['episode']
    return None
for a in ARMS:
    eps = [absorb_episode(r) for r in rows if r['arm'] == a]
    c = Counter(eps)
    print(a, dict(sorted(c.items(), key=lambda kv: (kv[0] is None, kv[0]))))
    # within the first episode: absorbing generation
    gens = []
    for r in rows:
        if r['arm'] != a: continue
        for e in r['episodes']:
            tr = e['modifier_trace']
            g = next((t['generation'] for t in tr if t['next_f'] in (0.0, 1.0)), None)
            if g is not None:
                gens.append(g + 1 + 64 * e['episode']); break
    print('   absorbing generation (global): median', np.median(gens), 'IQR', np.quantile(gens, [0.25, 0.75]).tolist(), 'max', max(gens))

print('\n## Mean f at episode ends')
for a in ARMS:
    m = [np.mean([r['episodes'][e]['final_f'] for r in rows if r['arm'] == a]) for e in range(12)]
    print(a, [round(x, 3) for x in m])

print('\n## Selection differential per polymorphic generation: recipient_f - census_f (before elites) and next_f - census_f')
diffs = {a: {'pre': [], 'post': []} for a in ARMS}
step = {a: {'pre': [], 'post': []} for a in ARMS}
for r in rows:
    for e in r['episodes']:
        for t in e['modifier_trace']:
            if 0 < t['census_f'] < 1 and t['recipient_f'] is not None:
                diffs[r['arm']][t['phase']].append(t['recipient_f'] - t['census_f'])
                step[r['arm']][t['phase']].append(t['next_f'] - t['census_f'])
for a in ARMS:
    for ph in ('pre', 'post'):
        d = np.array(diffs[a][ph]); s = np.array(step[a][ph])
        se = d.std(ddof=1) / math.sqrt(len(d))
        print(a, ph, 'n polymorphic gens', len(d), 'mean recipient-census', round(d.mean(), 5), '+/-', round(1.96*se, 5),
              '| mean next-census', round(s.mean(), 5))
# Per-trajectory (independent units) version: mean recipient-census per trajectory, then library-level
print('per-library mean of per-generation (recipient_f - census_f), bootstrap over libraries:')
for a in ARMS:
    per_build = []
    for b in range(B):
        vals = [t['recipient_f'] - t['census_f'] for r in rows if r['arm'] == a and r['build'] == b
                for e in r['episodes'] for t in e['modifier_trace'] if 0 < t['census_f'] < 1 and t['recipient_f'] is not None]
        per_build.append(np.mean(vals))
    pb = np.array(per_build)
    print(a, 'point', round(pb.mean(), 5), 'boot95', np.round(np.quantile(pb[sel].mean(1), [0.025, 0.975]), 5).tolist())

print('\n## Relative selection differential: (recipient_f - census_f) / (census_f (1-census_f)) [approx selection coefficient]')
for a in ARMS:
    for ph in ('pre', 'post'):
        vals = [(t['recipient_f'] - t['census_f']) / (t['census_f'] * (1 - t['census_f']))
                for r in rows if r['arm'] == a for e in r['episodes'] for t in e['modifier_trace'] if 0 < t['census_f'] < 1 and t['recipient_f'] is not None and t['phase'] == ph]
        v = np.array(vals)
        print(a, ph, 'n', len(v), 'mean s', round(v.mean(), 4), '+/-', round(1.96*v.std(ddof=1)/math.sqrt(len(v)), 4))

print('\n## Shortcuts / force_cap / distinct recipients')
print('exposure episodes with shortcuts>0:', sum(e['shortcuts'] > 0 for r in rows for e in r['episodes']), 'force_cap True:', sum(e['force_cap'] for r in rows for e in r['episodes']))
print('score attempts with shortcuts>0:', sum(a['shortcuts'] > 0 for s_ in scores for a in s_['attempts']), 'of', sum(len(s_['attempts']) for s_ in scores))
print('unsolved score rows:', [(s_['arm'], s_['cell'], s_['build'], s_['probability']) for s_ in scores if not s_['solved']])
dr = [t.get('distinct_recipients') for r in rows for e in r['episodes'] for t in e['modifier_trace'] if t.get('distinct_recipients') is not None]
print('distinct recipients per generation: mean', round(np.mean(dr),1), 'median', np.median(dr), 'q10/q90', np.quantile(dr,[0.1,0.9]).tolist())
dr0 = [t.get('distinct_recipients') for r in rows for e in r['episodes'] for t in e['modifier_trace'][:20] if t.get('distinct_recipients') is not None and e['episode']==0]
print('distinct recipients, first 20 generations of episode 0: mean', round(np.mean(dr0),1))
print('\n## Episode-level pre/post solve delta (split by solved), per-generation rate')
for a in ARMS:
    pre_rate, post_rate, unsolved_rate = [], [], []
    for r in rows:
        if r['arm'] != a: continue
        for e in r['episodes']:
            if e['initial_f'] in (0.0, 1.0):
                continue  # absorbed already; nothing can move
            if e['solved']:
                g = e['first_solve_evaluations'] // 256 - 1
                if g > 0: pre_rate.append(e['pre_solve_delta'] / g)
                if 63 - g > 0: post_rate.append(e['post_solve_delta'] / (63 - g))
            else:
                unsolved_rate.append(e['pre_solve_delta'] / 63)
    print(a, 'solved eps (polymorphic start)', len(pre_rate), 'pre rate/gen', round(np.mean(pre_rate), 5), 'post rate/gen', round(np.mean(post_rate), 5),
          '| unsolved eps', len(unsolved_rate), 'rate/gen', round(np.mean(unsolved_rate), 5) if unsolved_rate else None)

print('\n## Solving during exposure (episodes), by arm, and by carrier frequency at episode start')
for a in ARMS:
    eps = [e for r in rows if r['arm'] == a for e in r['episodes']]
    solved = sum(e['solved'] for e in eps)
    fs = [e['first_solve_evaluations'] for e in eps if e['solved']]
    print(a, 'episodes', len(eps), 'solved within 64 gens', solved, round(solved/len(eps), 3), 'median first-solve evals (solved only)', np.median(fs))
print('by initial f bucket (all arms):')
for a in ARMS:
    buck = defaultdict(list)
    for r in rows:
        if r['arm'] != a: continue
        for e in r['episodes']:
            f0 = e['initial_f']
            b = '0' if f0 == 0 else ('1' if f0 == 1 else 'poly')
            buck[b].append((e['solved'], e['first_solve_evaluations'] if e['solved'] else 16384))
    for b in ('0', 'poly', '1'):
        v = buck[b]
        if v:
            print('  ', a, 'f0=', b, 'episodes', len(v), 'solved', sum(s for s, _ in v), 'capped mean evals', round(np.mean([x for _, x in v])))

# paired comparison L vs others on episode first-solve (same program seeds), only episodes where both are polymorphic at start? Use all.
print('paired episode capped evals (16384 cap), L vs S/Z/N on same (build, repeat<2 for N, episode):')
idx = {(r['build'], r['arm'], r['repeat']): r for r in rows}
for a in ('S', 'Z', 'N'):
    d = []
    for (b, arm, rep), r in idx.items():
        if arm != 'L' or (b, a, rep) not in idx: continue
        o = idx[(b, a, rep)]
        for e1, e2 in zip(r['episodes'], o['episodes']):
            x1 = e1['first_solve_evaluations'] if e1['solved'] else 16384
            x2 = e2['first_solve_evaluations'] if e2['solved'] else 16384
            d.append(x1 - x2)
    print('  L -', a, 'n episodes', len(d), 'mean diff evals', round(np.mean(d)), '+/-', round(1.96*np.std(d, ddof=1)/math.sqrt(len(d))))

print('\n## Readout: per law')
for a in LAWS:
    rr = [s for s in scores if s['arm'] == a]
    print(a, 'jobs', len(rr), 'solved', sum(s['solved'] for s in rr), 'capped mean evals', round(np.mean([s['evaluations'] for s in rr])),
          'median', np.median([s['evaluations'] for s in rr]), 'mean worker s', round(np.mean([s['worker_seconds'] for s in rr]), 2))
print('\n## Readout dose-response: pooled by probability value (all laws)')
byp = defaultdict(list)
for s in scores:
    byp[s['probability']].append(s)
for p in sorted(byp):
    rr = byp[p]
    builds = sorted({s['build'] for s in rr})
    print('p=', p, 'jobs', len(rr), 'builds', len(builds), 'solved', sum(s['solved'] for s in rr), 'capped mean', round(np.mean([s['evaluations'] for s in rr])),
          'laws', Counter(s['arm'] for s in rr))
# per-build L-final vs S-final laws & costs
print('\n## Per build: probabilities and capped means')
print('build  pL   pS   cost(R-tree) cost(init) cost(L) cost(S) cost(R-all)')
for b in range(B):
    pr = manifest['probabilities'][b]
    c = {a: np.mean([s['evaluations'] for s in scores if s['build'] == b and s['arm'] == a]) for a in LAWS}
    print(f"{b:>5} {pr['L-final']:.3f} {pr['S-final']:.3f} {c['R-tree']:>10.0f} {c['initial']:>9.0f} {c['L-final']:>8.0f} {c['S-final']:>8.0f} {c['R-all']:>9.0f}")

# Jensen check: predicted mean cost of a mixture of per-build laws using the pooled dose-response curve
curve = {p: np.mean([s['evaluations'] for s in byp[p]]) for p in byp}
for law in ('L-final', 'S-final'):
    pred = np.mean([curve[manifest['probabilities'][b][law]] for b in range(B)])
    act = np.mean([s['evaluations'] for s in scores if s['arm'] == law])
    print(law, 'mean probability', round(np.mean([manifest['probabilities'][b][law] for b in range(B)]), 4), 'dose-curve predicted cost', round(pred), 'actual', round(act))

# ratios replicate
costs = {a: np.array([np.mean([s['evaluations'] for s in scores if s['build'] == b and s['arm'] == a]) for b in range(B)]) for a in LAWS}
def ratio(n, d):
    return round(costs[n].mean()/costs[d].mean(), 3), np.round(np.quantile(costs[n][sel].mean(1)/costs[d][sel].mean(1), [0.025, 0.975]), 3).tolist()
for n, d in [('initial', 'R-all'), ('L-final', 'initial'), ('L-final', 'S-final'), ('L-final', 'R-all'), ('S-final', 'initial'), ('initial', 'R-tree'), ('R-all', 'R-tree')]:
    print('ratio', n, '/', d, ratio(n, d))

# ---------- plots ----------
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
col = {'L': '#1f77b4', 'S': '#ff7f0e', 'Z': '#2ca02c', 'N': '#7f7f7f'}
for a in ARMS:
    rr = [r for r in rows if r['arm'] == a]
    paths = np.array([[t['census_f'] for e in r['episodes'] for t in e['modifier_trace']] for r in rr])
    axes[0].plot(paths.mean(0), color=col[a], label=f'{a} (n={len(rr)})')
    fixed = np.array([[float(t['census_f'] == 1.0) for e in r['episodes'] for t in e['modifier_trace']] for r in rr])
    axes[1].plot(fixed.mean(0), color=col[a], label=a)
for ax in axes:
    for k in range(1, 12):
        ax.axvline(64*k, color='#dddddd', lw=0.5)
    ax.set_xlabel('generation (12 episodes x 64)')
    ax.legend()
axes[0].axhline(0.25, color='k', ls=':', lw=0.8)
axes[0].set_ylabel('mean carrier frequency f'); axes[0].set_title('Mean carrier frequency')
axes[1].set_ylabel('fraction of trajectories fixed (f=1)'); axes[1].set_title('Fixation over time')
fig.tight_layout(); fig.savefig(FIG / 'frequency_trajectories.png', dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
ps = sorted(byp)
means = [np.mean([s['evaluations'] for s in byp[p]]) for p in ps]
ns = [len(byp[p]) for p in ps]
ax.plot(ps, means, 'o-', color='#1f77b4')
for p, m, n in zip(ps, means, ns):
    ax.annotate(f'n={n}', (p, m), textcoords='offset points', xytext=(4, 6), fontsize=8)
ax.set_xlabel('library draw probability (global law)'); ax.set_ylabel('capped mean evaluations to solve')
ax.set_title('Frozen readout dose-response (pooled over laws, 6 cells x 2 repeats)')
fig.tight_layout(); fig.savefig(FIG / 'readout_dose_response.png', dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 3.5))
x = np.arange(B); w = 0.2
for i, a in enumerate(ARMS):
    ax.bar(x + (i-1.5)*w, final[a], w, color=col[a], label=a)
ax.set_xlabel('library build'); ax.set_ylabel('mean final f (over 4 or 2 trajectories)'); ax.legend(ncol=4)
ax.axhline(0.25, color='k', ls=':', lw=0.8)
fig.tight_layout(); fig.savefig(FIG / 'final_f_by_build.png', dpi=130); plt.close(fig)
print('\nplots written')
