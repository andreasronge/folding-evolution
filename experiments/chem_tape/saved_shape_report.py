"""Six-start t intervals and first-match outcome rules for saved-map shifts."""

import numpy as np
from scipy.stats import t

CONTRASTS = {'R/M+': ('R', 'M+'), 'R/R_fm': ('R', 'R_fm'),
             'R/R_abl': ('R', 'R_abl'), 'R_fm/M+': ('R_fm', 'M+')}


def interval(values):
    if len(values) != 6:
        return dict(state='unresolved', reason='requires all six starts', n=len(values))
    v = np.asarray(values)
    mean = float(v.mean())
    half = float(t.ppf(0.975, 5) * v.std(ddof=1) / np.sqrt(6))
    return dict(state='complete', n=6, df=5, per_start_log2=v.tolist(),
                log2_mean=mean, ratio=2**mean,
                interval_95=[2**(mean-half), 2**(mean+half)])


def primary(contrasts, eligible):
    r = contrasts['R/M+']
    if not eligible or any(v['state'] != 'complete' for v in r.values()):
        return dict(row=0, meaning='No verdict: gate or six complete b starts missing.')
    be, lin, shift = (r[k]['interval_95'] for k in ('BE', 'LIN', 'shift'))
    if be[0] > 1 and shift[0] > 1:
        return dict(row=1, meaning='Conditional BE gain and shift replicate on the same M starts.')
    if shift[0] > 1:
        return dict(row=2, meaning='Relative shift replicates without resolved BE gain.',
                    linear_loss=lin[1] < 1)
    if shift[1] < 1.41 and be[1] < 1.25:
        return dict(row=3, meaning='No replication at prior size: shift bounded below 1.41x and BE gain below 1.25x; not zero effects.')
    return dict(row=4, meaning='Unresolved; report intervals, not equality.')


def dependency(contrasts):
    residual, fm = contrasts['R/R_fm'], contrasts['R_fm/M+']
    if any(v['state'] != 'complete' for r in (residual, fm) for v in r.values()):
        return dict(row='D-c', meaning='Dependency unresolved: incomplete layer.')
    shift = residual['shift']['interval_95']
    if shift[0] > 1:
        helps = residual['BE']['interval_95'][0] > 1
        return dict(row='D-a', residual_branch_help=helps,
                    meaning='Residuals contribute shift beyond matched pooled uniform-allele frequencies; ' +
                    ('residuals help branch search.' if helps else 'trade-off only, no resolved useful branch gain.'))
    if shift[1] < 1.25 and fm['shift']['interval_95'][0] > 1:
        return dict(row='D-b', meaning='Pooled emitted frequencies reproduce shift; residual increment bounded below 1.25x.')
    return dict(row='D-c', meaning='Dependency unresolved.')


def report(rows, maps, cells, seeds, prior_costs, gate_passed, smoke=False):
    by_key = {}
    for r in rows:
        by_key.setdefault((r['arm'], r['cell']), []).append(r)
    stats, complete = {}, set()
    for name, m in maps.items():
        stats[name] = {}
        valid = True
        for c in cells:
            rs = by_key.get((name, c['id']), [])
            ok = (len(rs) == len(seeds) and {r['seed'] for r in rs} == set(seeds)
                  and all(r['table_hash'] == m['table_hash'] for r in rs))
            valid &= ok
            stats[name][c['id']] = dict(n=len(rs), expected=len(seeds), complete=ok,
                solved=sum(r['solved'] for r in rs),
                cost=float(np.mean([r['log2_cost'] for r in rs])) if rs else None)
        if valid:
            complete.add(name)
    groups = {group: [c['id'] for c in cells if (c['shape'] == 'BE') == (group == 'BE')]
              for group in ('BE', 'LIN')}
    costs = {name: {g: float(np.mean([stats[name][c]['cost'] for c in cs]))
                    for g, cs in groups.items()} for name in complete}
    pairs = {}
    for rep in ('b', 'a'):
        for k in range(1, 7):
            pair = f'{k}{rep}'
            pairs[pair] = {}
            for label, (x, y) in CONTRASTS.items():
                xn, yn = x+pair, y+pair
                if xn not in complete or yn not in complete:
                    pairs[pair][label] = None
                    continue
                be, lin = (costs[yn][g] - costs[xn][g] for g in ('BE', 'LIN'))
                pairs[pair][label] = dict(log2=dict(BE=be, LIN=lin, shift=be-lin),
                                         ratios=dict(BE=2**be, LIN=2**lin, shift=2**(be-lin)))
            if f'R{pair}' in maps and f'M+{pair}' in maps:
                pairs[pair]['IF_GT_difference_R_minus_Mplus'] = (
                    maps[f'R{pair}']['emitted_frequencies'][17] -
                    maps[f'M+{pair}']['emitted_frequencies'][17])
    layers = {}
    for layer, reps in [('b_only', ('b',)), ('pooled', ('a', 'b'))]:
        contrasts = {}
        for label in CONTRASTS:
            metrics = {}
            for metric in ('BE', 'LIN', 'shift'):
                values = []
                for k in range(1, 7):
                    records = [pairs[f'{k}{rep}'][label] for rep in reps]
                    if all(r is not None for r in records):
                        values.append(float(np.mean([r['log2'][metric] for r in records])))
                metrics[metric] = interval(values)
            contrasts[label] = metrics
        layers[layer] = dict(contrasts=contrasts, dependency=dependency(contrasts))
        if smoke:
            layers[layer]['dependency'] = dict(row='D-c', meaning='Smoke infrastructure check; no dependency verdict.')
    b_complete = [k for k in range(1, 7)
                  if all(f'{a}{k}b' in complete for a in ('M+', 'R', 'R_abl'))]
    outcome = primary(layers['b_only']['contrasts'], gate_passed and len(b_complete) == 6 and not smoke)
    if smoke:
        outcome = dict(row=0, meaning='Smoke infrastructure check; no scientific verdict.')
    d = layers['pooled']['dependency']
    row = outcome['row']
    if row == 1 and d['row'] == 'D-a' and d['residual_branch_help']:
        action = 'Full contextual arm in four-reducer study.'
    elif row == 1 and d['row'] == 'D-c':
        action = 'Context secondary with R_fm control; source unresolved.'
    elif row in (1, 2):
        action = 'Prioritize token learner; context at most secondary.'
    elif row == 3:
        action = 'Drop lead at stated bounds; token adaptation remains demonstrated gain.'
    elif row == 4:
        action = 'Record intervals and move on; no precision loop.'
    else:
        action = 'No scientific verdict; incomplete or failed gate (smoke is infrastructure only).'
    references = {}
    if 'G' in complete:
        for k in range(1, 7):
            name = f'M{k}'
            references[name] = {c['id']: 2**(stats['G'][c['id']]['cost'] - stats[name][c['id']]['cost'])
                                for c in cells} if name in complete else None
    return dict(cell_stats=stats, group_costs=costs, per_pair=pairs, layers=layers,
                complete_maps=sorted(complete), complete_b_starts=b_complete,
                prior_G_cell_costs=prior_costs, M_over_G_per_cell=references,
                IF_GT_frequencies={n: m['emitted_frequencies'][17] for n,m in maps.items()},
                outcome=outcome, downstream=action,
                scope='Conditional same-start replication. Pooled includes selected a continuations. No family-specificity, solver-supply or positional/selected-population frequency attribution.')
