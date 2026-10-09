"""0239 complete-roster corpus intervals and joint Q/P interpretation."""

from collections import defaultdict
import math

import numpy as np

from experiments.chem_tape.comparison_gate_report import interval, describe, balanced_target_n
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.solver_corpus_report import cost

PAIRS = dict(C_Q=('C', 'Q'), C_P=('C', 'P'), Q_K=('Q', 'K'), Q_P=('Q', 'P'),
             C_K=('C', 'K'), C_T=('C', 'T'))
ARMS = ('C', 'T', 'K', 'Q', 'P', 'G4')


def route(result, eligible):
    if not eligible:
        return dict(label='incomplete', meaning='fixed roster incomplete or error; no efficacy decision')
    low, high = result['interval_95']
    if low >= 1.20:
        return dict(label='replacement_insufficient', meaning='this frozen positional replacement is insufficient within 20% under these operators')
    if high <= 1.20:
        return dict(label='replacement_adequate', meaning='this frozen positional replacement is sufficient within the stated 20% bound')
    return dict(label='unresolved', meaning='interval crosses 1.20; positional sufficiency unresolved')


def joint_interpretation(q, p):
    labels = q['label'], p['label']
    adequate, insufficient = 'replacement_adequate', 'replacement_insufficient'
    if labels == (insufficient, adequate):
        return 'G4-based Q failed; independent positional P remains a viable acquisition target.'
    if labels == (adequate, insufficient):
        return 'Q suffices while P fails; supplied G4 grammar remains useful in this replacement test.'
    if labels == (adequate, adequate):
        return 'Both projections suffice; independent positional supply is a viable target, without demonstrated learnability.'
    if labels == (insufficient, insufficient):
        return 'Both frozen replacements fail under the fixed operators; investigate dependencies without ruling out all positional learners.'
    return 'One or both controls remain inconclusive; retain both intervals and the unresolved representation choice.'


def make_report(rows, references, schedule, config, error=None):
    def k(r):
        return tuple(r[x] for x in ('corpus', 'cell', 'seed'))
    expected = {(k(r), r['arm']) for r in schedule}
    observed = {(k(r), r['arm']): r for r in rows}
    if len(observed) != len(rows) or not set(observed) <= expected or any(r['arm'] not in ('Q', 'P') for r in rows):
        raise ValueError('unexpected or duplicate Q/P observation')
    eligible = not error and len(rows) == 4096 and set(observed) == expected
    report = dict(efficacy_eligible=eligible, full_roster_complete=eligible, searches=len(rows),
                  error=error, scope=config['scope'], sensitivities={},
                  uncertainty_unit='corpus; fixed bank/cells/seeds; n=16, df=15',
                  censoring_caution='capped geometric costs; zero solves is not absence',
                  limits='External frozen projections; development bank; success does not show learnability; supply and variation are not separated.')
    if not eligible:
        report['outcome'] = route({}, False)
        report['partial_counts'] = {a: describe([r for r in rows if r['arm'] == a]) for a in ('Q', 'P')}
        return report
    grouped = defaultdict(dict)
    for r in references + rows:
        if r['arm'] != 'G4':
            if r['arm'] in grouped[k(r)]:
                raise ValueError('duplicate paired reference')
            grouped[k(r)][r['arm']] = r
    if any(set(grouped[x]) != {'C', 'T', 'K', 'Q', 'P'} for x, _ in expected):
        raise ValueError('C/T/K/Q/P pairing incomplete')
    corpora = sorted({r['corpus'] for r in schedule})
    cells = sorted({r['cell'] for r in schedule})

    def contrast(a, b, penalty=2, only_cells=None, both=False):
        scores, occupancy = {}, {}
        for tid in corpora:
            per_cell = []
            occupancy[tid] = {}
            for cid in only_cells or cells:
                pairs = [p for (t, c, _), p in grouped.items() if t == tid and c == cid]
                if both:
                    pairs = [p for p in pairs if p[a]['solved'] and p[b]['solved']]
                occupancy[tid][cid] = len(pairs)
                if pairs:
                    per_cell.append(np.mean([np.log(cost(p[b], penalty)) - np.log(cost(p[a], penalty)) for p in pairs]))
            if per_cell:
                scores[tid] = float(np.mean(per_cell))
        result = interval(list(scores.values()))
        result.update(corpus_scores_log=scores, occupancy=occupancy,
                      per_source_family={f: interval([v for t, v in scores.items() if t.startswith(f)]) for f in ('BE', 'PA')})
        return result

    for penalty in (2, 1):
        contrasts = {name: contrast(a, b, penalty) for name, (a, b) in PAIRS.items()}
        logcq = math.log(contrasts['C_Q']['speed_ratio'])
        logck = math.log(contrasts['C_K']['speed_ratio'])
        report['sensitivities'][f'unsolved_{penalty}cap'] = dict(
            **contrasts, descriptive_log_C_Q_over_log_C_K=logcq / logck if abs(logck) > 1e-12 else None,
            share_interpretation='descriptive arithmetic, not a causal fraction',
            arms={a: describe([r for r in references + rows if r['arm'] == a], penalty) for a in ARMS},
            per_cell={cid: dict(contrasts={name: contrast(a, b, penalty, [cid]) for name, (a, b) in PAIRS.items()},
                                arms={a: describe([r for r in references + rows if r['cell'] == cid and r['arm'] == a], penalty) for a in ARMS}) for cid in cells},
        )
    report['both_solved'] = {name: contrast(a, b, both=True) for name, (a, b) in PAIRS.items()}
    report['both_solved_interpretation'] = 'selection-conditioned; occupied cells equally weighted within corpus; omitted cells and occupancy reported'
    primary = report['sensitivities']['unsolved_2cap']
    report['outcome'] = route(primary['C_Q'], True)
    report['P_interpretation_band'] = route(primary['C_P'], True)
    report['joint_interpretation'] = joint_interpretation(report['outcome'], report['P_interpretation_band'])
    report['sizing'] = {arm: dict(
        approximate_only=True, assumption='new independent corpora with same observed spread; precision estimate, not a boundary-resolution guarantee; no top-up',
        corpora_for_10_percent_half_width=balanced_target_n(primary[f'C_{arm}']['sd_log'], math.log(1.10), 16),
        current_half_width_log=primary[f'C_{arm}']['half_width_log']) for arm in ('Q', 'P')}
    return report


def save_report(out, report, rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for arm in ARMS:
        selected = [r for r in rows if r['arm'] == arm]
        if not selected:
            continue
        budgets = np.geomspace(256, 524288, 100)
        axes[0].plot(budgets, [np.mean([r['solved'] and r['evaluations'] <= b for r in selected]) for b in budgets], label=arm)
        points = defaultdict(list)
        for r in selected:
            for ev, accuracy, diversity in r['curve']:
                points[ev].append((accuracy, diversity))
        x = sorted(points)
        for ax, i in ((axes[1], 0), (axes[2], 1)):
            ax.plot(x, [np.median([v[i] for v in points[ev]]) for ev in x], label=arm)
    for ax, label in zip(axes, ('Fraction D1331-exact', 'Median correct training cases (active runs)', 'Median behavioural diversity (active runs)')):
        ax.set(xlabel='Evaluations', ylabel=label, xscale='log')
        if ax.lines:
            ax.legend()
    fig.tight_layout()
    fig.savefig(out / 'diagnostics.png', dpi=150)
    plt.close(fig)
    write_json(out, 'result.json', report)
    lines = ['# Frozen positional replacements Q and P', '',
             f"Primary outcome: {report['outcome']['label']} — {report['outcome']['meaning']}", '',
             report['scope'], '', f"Q/P observations: {report['searches']}/4096. Error: {report['error']}", '',
             '| Unsolved cost | C/Q (95% corpus interval) | C/P (95% corpus interval) | Q/K | Q/P |',
             '|---|---|---|---|---|']
    for name, val in report['sensitivities'].items():
        lines.append(f"| {name} | {val['C_Q']['speed_ratio']} {val['C_Q']['interval_95']} | {val['C_P']['speed_ratio']} {val['C_P']['interval_95']} | {val['Q_K']['speed_ratio']} | {val['Q_P']['speed_ratio']} |")
    if report['efficacy_eligible']:
        arms = report['sensitivities']['unsolved_2cap']['arms']
        lines += ['', report['joint_interpretation'], '', 'Solve counts: ' + '; '.join(f"{a} {r['solved']}/{r['n']}" for a, r in arms.items()), '',
                  'Both-solved sensitivities, occupancy, per-cell and family results, descriptive log-gap share and conditional precision prices are in result.json.']
    lines += ['', report['limits'], report['censoring_caution']]
    (out / 'report.md').write_text('\n'.join(lines) + '\n')
