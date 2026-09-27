"""Follow-up checks on the overnight queue (map-bias notebook §12): Fisher tests,
per-run exact AND under varying goals vs the fixed control, and how the tagged OR
solvers' second output run arrived (lineage). Run after overnight_analysis.py."""

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import yaml
from scipy.stats import fisher_exact

from folding_evolution.chem_tape import tagged

D = Path(sys.argv[1] if len(sys.argv) > 1 else 'experiments/output/2026-09-26')
# 1. Fisher tests on OR / AND
for sw in ('mapbias_or_race', 'mapbias_and_fixed'):
    rows = json.load(open(D / sw / 'analysis.json'))
    n = {a: sum(r['final_exact'] for r in rows if r['arm'] == a) for a in ('baseline', 'tagged', 'tagged+dup')}
    for a, b in (('baseline', 'tagged'), ('baseline', 'tagged+dup'), ('tagged', 'tagged+dup')):
        p = fisher_exact([[n[a], 30 - n[a]], [n[b], 30 - n[b]]])[1]
        print(sw, f'{a} {n[a]}/30 vs {b} {n[b]}/30  p={p:.4f}')
# 2. MVG: runs with an exact AND phase-end anywhere in the last third, vs fixed AND
fixed = json.load(open(D / 'mapbias_and_fixed' / 'analysis.json'))
for sw in ('mapbias_mvg_p20', 'mapbias_mvg_period'):
    rows = json.load(open(D / sw / 'analysis.json'))
    for per in sorted({r['period'] for r in rows}):
        for a in ('baseline', 'tagged', 'tagged+dup'):
            rs = [r for r in rows if r['arm'] == a and r['period'] == per]
            if not rs:
                continue
            k = len(rs[0]['phases'])
            hit = sum(any(p['goal'] == 'mbs_and' and p['end_exact'] for p in r['phases'][2 * k // 3:]) for r in rs)
            anyhit = sum(any(p['goal'] == 'mbs_and' and p['end_exact'] for p in r['phases']) for r in rs)
            print(f'{sw} p{per} {a}: runs with exact AND at a late phase end {hit}/30, ever {anyhit}/30'
                  f' | fixed AND exact at end {sum(x["final_exact"] for x in fixed if x["arm"] == a)}/30')
# 3. OR solvers: how did the second output run arrive?
def out_bodies(g):
    return [tagged._strip_trailing_nops(b) for t, b in tagged.parse_runs(g) if t == tagged.OUTPUT_TAG]
rows = json.load(open(D / 'mapbias_or_race' / 'analysis.json'))
idx = {r['run_dir']: r for r in json.load(open(D / 'mapbias_or_race' / 'sweep_index.json'))}
for arm in ('tagged', 'tagged+dup'):
    events = Counter()
    for rd, r in idx.items():
        c = yaml.safe_load(open(Path(rd) / 'config.yaml'))
        a = 'tagged+dup' if c.get('run_duplication_rate') else ('tagged' if c['arm'] == 'TAG' else 'baseline')
        if a != arm:
            continue
        row = next(x for x in rows if x['seed'] == c['seed'] and x['arm'] == arm)
        if not row['final_exact']:
            continue
        L = np.load(Path(rd) / 'lineage.npz')
        gs, kind, mut, other = L['genome'], L['kind'], L['mutated'], L['other_genome']
        # last step at which the champion line went from < 2 to >= 2 output runs
        cnt = [len(out_bodies(g)) for g in gs]
        ks = [k for k in range(1, len(cnt)) if cnt[k] >= 2 and cnt[k - 1] < 2]
        if not ks:
            events['never 2 output runs on main line'] += 1
            continue
        k = ks[-1]
        prev, child = set(out_bodies(gs[k - 1])), out_bodies(gs[k])
        new = [b for b in child if b not in prev]
        if kind[k] == 1:
            oth = set(out_bodies(other[k]))
            src = 'crossover: new output run came from the other parent' if any(b in oth for b in new) else \
                  'crossover: new output run not an exact copy of either parent'
        elif kind[k] == 2:
            src = 'mutation step: copy of an existing output run (duplication)' if any(b in prev for b in child if child.count(b) > 1) or not new else 'mutation step: new output run (tag mutation / other)'
        else:
            src = 'elite'
        events[src] += 1
    print(arm, dict(events))
