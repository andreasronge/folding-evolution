#!/usr/bin/env python3
"""Reviewer's independent re-analysis of task 2026-10-04-1839 (run from the worktree).

Re-derives every verdict from final_population.npz (not from readouts.json), re-classifies
the historical crossover-off / selected-mate runs of the same cells with the same rule,
pairs them by seed, and plots per-seed trajectories.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import yaml
from scipy.stats import fisher_exact

WT = Path('/Users/andreas/developer/folding-evolution-research/2026-10-04-1839')
sys.path.insert(0, str(WT / 'experiments/chem_tape'))
import shared_helper as sh  # noqa: E402

OUT = Path('/Users/andreas/developer/folding-evolution/experiments/output')
TASK = Path(__file__).resolve().parent
NEW = OUT / '2026-10-04/2026-10-04-1839-self-mate-contest/evolution'
OLD = [OUT / '2026-10-03' / n for n in ('mapbias_s30_est_dup', 'mapbias_s30_est_partly', 'mapbias_s31_dose')]
KNOWN = {sh.form_genome(n, 64).tobytes().hex(): n for n in sh.FORMS}
M, EX, CACHE = sh.machine(), sh.Exactness(), {}


def load(d: Path):
    cfg = yaml.safe_load((d / 'config.yaml').read_text())
    if cfg.get('tape_length') != 64 or not cfg.get('seed_tapes') or cfg.get('seed_counts'):
        return None
    tapes = cfg['seed_tapes'].split(',')
    if any(t not in KNOWN for t in tapes):
        return None
    names = [KNOWN[t] for t in tapes]
    if names.count('shared') != 1 or len(tapes) not in (10, 32):
        return None
    comp = next(n for n in names if n != 'shared')
    if cfg['crossover_rate'] not in (0.0, 0.3, 0.7):
        return None
    res = json.loads((d / 'result.json').read_text())
    pop = np.load(d / 'final_population.npz')['genotypes']
    forms = Counter()
    for g in pop[cfg['elite_count']:]:
        if EX(g).all():
            k = sh.semantic_key(g)
            if k not in CACHE:
                CACHE[k] = sh.classify(g, M)['form']
            forms[CACHE[k]] += 1
    n = sum(forms.values())
    share = forms.get('shared', 0) / n if n else None
    out = 'no_solution' if n < 20 else 'won' if share > 0.9 else 'gone' if share == 0 else 'between'
    return {'dir': d.name, 'comp': comp, 'start': f'1/{len(tapes)}', 'rate': cfg['crossover_rate'],
            'mate': cfg.get('crossover_mate', 'selected'), 'seed': cfg['seed'], 'gens': cfg['generations'],
            'pop': cfg['pop_size'], 'mu': cfg['mutation_rate'], 'sel': cfg['selection_mode'],
            'n_exact': n, 'forms': dict(forms), 'share': share, 'outcome': out,
            'elite0': sh.classify(pop[0], M)['form'], 'stats': res['shared_stats']}


runs = []
for root in [NEW, *OLD]:
    for d in sorted(root.iterdir()):
        if d.is_dir() and (d / 'result.json').exists():
            r = load(d)
            if r:
                r['root'] = root.name
                runs.append(r)

new = [r for r in runs if r['root'] == 'evolution']
print('new runs', len(new), 'mates', Counter(r['mate'] for r in new),
      'settings', Counter((r['gens'], r['pop'], r['mu'], r['sel']) for r in runs))
cells = defaultdict(list)
for r in runs:
    arm = 'off' if r['rate'] == 0 else f"{r['mate']}@{r['rate']}"
    cells[(r['comp'], r['start'], arm)].append(r)
for k, rs in cells.items():
    seeds = sorted(r['seed'] for r in rs)
    assert seeds == list(range(30)), (k, len(seeds))

# cross-check against the researcher's readouts
rd = {x['hash']: x for x in json.loads((NEW.parent / 'readouts/readouts.json').read_text())['runs']}
mism = [r['dir'] for r in new if rd[r['dir']]['outcome'] != r['outcome'] or rd[r['dir']]['n_exact_nonelite'] != r['n_exact']]
print('verdict mismatches vs readouts.json:', len(mism), 'of', len(new))

ARMS = ['off', 'self@0.3', 'self@0.7', 'selected@0.3', 'selected@0.7']
print('\n| contest | start | arm | N | won | gone | between | no solution | median exact non-elites (of 1022) | slot-0 elite shared: won/all | Fisher p vs off (won) |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for comp in ('duplicated', 'partly'):
    for start in ('1/32', '1/10'):
        off = sum(r['outcome'] == 'won' for r in cells[(comp, start, 'off')])
        for arm in ARMS:
            rs = cells[(comp, start, arm)]
            o = Counter(r['outcome'] for r in rs)
            e0 = [r for r in rs if r['elite0'] == 'shared']
            p = fisher_exact([[o['won'], 30 - o['won']], [off, 30 - off]])[1] if arm != 'off' else float('nan')
            print(f"| {comp} | {start} | {arm} | {len(rs)} | {o['won']} | {o['gone']} | {o['between']} | {o['no_solution']} | "
                  f"{np.median([r['n_exact'] for r in rs]):.0f} | {sum(r['outcome'] == 'won' for r in e0)}/{len(e0)} | {p:.3f} |")

print('\nPooled self-mate (0.3+0.7) vs off, wins:')
for comp in ('duplicated', 'partly'):
    for start in ('1/32', '1/10'):
        s = sum(r['outcome'] == 'won' for a in ('self@0.3', 'self@0.7') for r in cells[(comp, start, a)])
        off = sum(r['outcome'] == 'won' for r in cells[(comp, start, 'off')])
        print(comp, start, f'self {s}/60 off {off}/30 p={fisher_exact([[s, 60 - s], [off, 30 - off]])[1]:.3f}')

print('\nSeed pairing (same seed = same shuffled start): self won & off won / self only / off only / neither')
for comp in ('duplicated', 'partly'):
    for start in ('1/32', '1/10'):
        off = {r['seed']: r['outcome'] == 'won' for r in cells[(comp, start, 'off')]}
        for arm in ('self@0.3', 'self@0.7'):
            s = {r['seed']: r['outcome'] == 'won' for r in cells[(comp, start, arm)]}
            c = Counter((s[i], off[i]) for i in range(30))
            print(comp, start, arm, c[(True, True)], c[(True, False)], c[(False, True)], c[(False, False)])
        a, b = ({r['seed']: r['outcome'] == 'won' for r in cells[(comp, start, x)]} for x in ('self@0.3', 'self@0.7'))
        c = Counter((a[i], b[i]) for i in range(30))
        print(comp, start, 'self0.3 vs self0.7', c[(True, True)], c[(True, False)], c[(False, True)], c[(False, False)])

print('\nNon-won / non-gone self-mate runs:')
for r in new:
    if r['outcome'] in ('between', 'no_solution'):
        tail = [(s['gen'], s['n_fully_exact'], None if s['shared'] is None else round(s['shared'], 2)) for s in r['stats'][-6:]]
        print(r['comp'], r['start'], r['rate'], 'seed', r['seed'], r['outcome'], r['n_exact'], r['forms'], 'elite0', r['elite0'], tail)

print('\nPer-generation means (census n=256, elites included): shared among exact | fully exact fraction')
for comp in ('duplicated', 'partly'):
    for start in ('1/32', '1/10'):
        for arm in ARMS:
            rs = cells[(comp, start, arm)]
            row = []
            for g in (0, 5, 10, 20, 50, 100, 300):
                ss = [next(s for s in r['stats'] if s['gen'] == g) for r in rs]
                sh_ = [s['shared'] for s in ss if s['shared'] is not None]
                row.append(f"{g}: {np.mean(sh_):.3f} | {np.mean([s['fully_exact'] for s in ss]):.2f}")
            print(comp, start, arm, ' ; '.join(row))

print('\nGeneration when sampled shared-among-exact first > 0.9 (winning runs): median [min, max]')
for comp in ('duplicated', 'partly'):
    for start in ('1/32', '1/10'):
        for arm in ('off', 'self@0.3', 'self@0.7'):
            t = [next((s['gen'] for s in r['stats'] if (s['shared'] or 0) > 0.9), None)
                 for r in cells[(comp, start, arm)] if r['outcome'] == 'won']
            t = [x for x in t if x is not None]
            print(comp, start, arm, len(t), np.median(t), min(t), max(t))

import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

fig, axes = plt.subplots(3, 4, figsize=(15, 9), sharex=True, sharey=True)
for col, (comp, start) in enumerate((c, s) for c in ('duplicated', 'partly') for s in ('1/32', '1/10')):
    for row, arm in enumerate(('off', 'self@0.3', 'self@0.7')):
        ax = axes[row, col]
        rs = cells[(comp, start, arm)]
        for r in rs:
            y = [np.nan if s['shared'] is None else s['shared'] for s in r['stats']]
            ax.plot([s['gen'] for s in r['stats']], y, lw=0.7, alpha=0.6,
                    color={'won': 'tab:blue', 'gone': 'tab:gray', 'between': 'tab:orange', 'no_solution': 'tab:red'}[r['outcome']])
        w = sum(r['outcome'] == 'won' for r in rs)
        ax.set_title(f"vs {comp}, start {start}, {'crossover off (§30)' if arm == 'off' else arm.replace('@', ' mate, crossover ')}: won {w}/30", fontsize=8)
        ax.grid(alpha=0.25)
for ax in axes[-1]:
    ax.set_xlabel('Generation')
for ax in axes[:, 0]:
    ax.set_ylabel('Shared share among fully exact\n(census of 256, elites included)', fontsize=8)
fig.suptitle('Per-seed trajectories; blue = won, grey = shared gone, orange = in between, red = lost the solution (final non-elite verdict)', fontsize=9)
fig.tight_layout()
fig.savefig(TASK / 'analysis_trajectories.png', dpi=130)

fig, axes = plt.subplots(1, 4, figsize=(14, 3.4), sharey=True)
for ax, (comp, start) in zip(axes, ((c, s) for c in ('duplicated', 'partly') for s in ('1/32', '1/10'))):
    w = [sum(r['outcome'] == 'won' for r in cells[(comp, start, a)]) for a in ARMS]
    ax.bar(range(5), w, color=['tab:gray', 'tab:blue', 'tab:blue', 'tab:red', 'tab:red'])
    for i, v in enumerate(w):
        ax.text(i, v + 0.4, str(v), ha='center', fontsize=8)
    ax.set_xticks(range(5), ['off', 'self\n0.3', 'self\n0.7', 'selected\n0.3', 'selected\n0.7'], fontsize=8)
    ax.set_title(f'vs {comp}, start {start}', fontsize=9)
    ax.set_ylim(0, 33)
axes[0].set_ylabel('Seeds where shared won (of 30)')
fig.tight_layout()
fig.savefig(TASK / 'analysis_wins.png', dpi=130)
