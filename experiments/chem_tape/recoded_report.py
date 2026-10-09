"""Explicit cost ratios and corpus intervals for the fixed recoding experiment."""

from collections import defaultdict
import math

import numpy as np

from experiments.chem_tape.comparison_gate_report import interval, describe, balanced_target_n
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.solver_corpus_report import cost

CONTRASTS = dict(G=('Q', 'R30'), H=('R30', 'C'), G100=('Q', 'R100'),
                 R100_over_R30=('R30', 'R100'), Q_over_C=('Q', 'C'))
ARMS = ('Q', 'C', 'R30', 'R100')


def route(effect, eligible=True):
    if not eligible:
        return 'incomplete'
    low, high = effect['interval_95']
    if low >= 1.20:
        return 'useful_gain_at_fixed_uniform_prior_supply'
    if high <= 1.20:
        return 'no_useful_gain_for_this_recoding'
    return 'unresolved'


def make_report(rows, references, schedule, config, preparation, error=None):
    triple = lambda r: tuple(r[k] for k in ('corpus', 'cell', 'seed'))
    expected = {(triple(r), r['arm']) for r in schedule}
    observed = {(triple(r), r['arm']): r for r in rows}
    if len(observed) != len(rows) or not set(observed) <= expected:
        raise ValueError('unexpected/duplicate recoding observations')
    eligible = not error and len(rows) == 4096 and set(observed) == expected
    report = dict(efficacy_eligible=eligible, searches=len(rows), error=error,
                  outcome='incomplete', sensitivities={}, scope=config['scope'],
                  ratio_definitions={n: f'geometric cost_{a}/cost_{b}' for n, (a, b) in CONTRASTS.items()},
                  uncertainty_unit='corpus; n=16, df=15; equal cells/seeds within corpus; realizations nested',
                  limits='No causal partition of C advantage, transfer or acquisition; failure bounds these frozen recodings, not all wider mutation. Finite non-hits are not absence. Gap share is arithmetic closure, not mediation.')
    if not eligible:
        report['partial_counts'] = {a: describe([r for r in rows if r['arm'] == a]) for a in ('R30', 'R100')}
        return report
    paired = defaultdict(dict)
    for r in references + rows:
        if r['arm'] in paired[triple(r)]:
            raise ValueError('duplicate paired reference')
        paired[triple(r)][r['arm']] = r
    if len(paired) != 2048 or any(set(p) != set(ARMS) for p in paired.values()):
        raise ValueError('Q/C/R30/R100 pairing incomplete')
    corpora = sorted({r['corpus'] for r in schedule})
    cells = sorted({r['cell'] for r in schedule})

    def contrast(a, b, penalty=2, selected_cells=None, both=False, realization=None):
        scores, occupancy = {}, {}
        for tid in corpora:
            values = []
            occupancy[tid] = {}
            for cid in selected_cells or cells:
                ps = [p for (t, c, _), p in paired.items() if t == tid and c == cid]
                if realization is not None:
                    ps = [p for p in ps if p['R30']['realization'] == realization]
                if both:
                    ps = [p for p in ps if p[a]['solved'] and p[b]['solved']]
                occupancy[tid][cid] = len(ps)
                if ps:
                    values.append(np.mean([np.log(cost(p[a], penalty)) - np.log(cost(p[b], penalty)) for p in ps]))
            if values:
                scores[tid] = float(np.mean(values))
        r = interval(list(scores.values()))
        r.update(corpus_scores_log=scores, occupancy=occupancy,
                 families={f: interval([v for t, v in scores.items() if t.startswith(f)]) for f in ('BE', 'PA')})
        return r

    for penalty in (2, 1):
        effects = {name: contrast(a, b, penalty) for name, (a, b) in CONTRASTS.items()}
        denominator = math.log(effects['Q_over_C']['speed_ratio'])
        report['sensitivities'][f'unsolved_{penalty}cap'] = dict(
            **effects, descriptive_gap_share=math.log(effects['G']['speed_ratio']) / denominator if abs(denominator) > 1e-12 else None,
            arms={a: describe([r for r in references + rows if r['arm'] == a], penalty) for a in ARMS},
            per_cell={cid: {name: contrast(a, b, penalty, [cid]) for name, (a, b) in CONTRASTS.items()} for cid in cells},
            per_realization={str(k): {name: contrast(a, b, penalty, realization=k) for name, (a, b) in CONTRASTS.items()} for k in (0, 1)})
    report['both_solved'] = {name: contrast(a, b, both=True) for name, (a, b) in CONTRASTS.items()}
    report['both_solved_note'] = 'selection conditioned; occupied cells equally weighted; omitted occupancy recorded'
    primary = report['sensitivities']['unsolved_2cap']
    report['outcome'] = route(primary['G'])
    report['R100_descriptive_band'] = route(primary['G100'])
    h_low, h_high = primary['H']['interval_95']
    report['approaches_C'] = 'yes' if h_high <= 1.5 else ('bounded_outside_1.5' if h_low > 1.5 else 'unresolved')
    report['no_useful_gain_at_either_dose'] = all(primary[n]['interval_95'][1] <= 1.20 for n in ('G', 'G100'))
    report['next'] = 'strategy'
    report['resolution_price'] = {}
    for name in ('G', 'G100'):
        effect = primary[name]
        distance = abs(math.log(effect['speed_ratio']) - math.log(1.2))
        target = balanced_target_n(effect['sd_log'], distance, 16) if distance > 0 else None
        extra = max(0, target - 16) if target is not None else None
        # Only score cost can be priced from these observations; new corpora need acquisition/fitting separately.
        score_per_corpus = sum(v['mean_worker_seconds'] for v in preparation['arms'].values()) * 128 / config['workers']
        report['resolution_price'][name] = dict(total_balanced_corpora_to_boundary_half_width=target,
            extra_corpora=extra, additional_recoded_scoring_seconds=extra * score_per_corpus if extra is not None else None,
            total_corpora_for_10_percent_half_width=balanced_target_n(effect['sd_log'], math.log(1.1), 16),
            assumption='same observed spread/effect and fresh independent corpora; approximate precision, not a resolution guarantee; acquisition/fitting/Q/C references need separate pricing; no automatic top-up')
    return report


def save_report(out, report, rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    write_json(out, 'result.json', report)
    lines = ['# Fixed-prior Q recoding', '', f"Outcome: {report['outcome']}", '', report['scope'], '',
             f"New searches: {report['searches']}/4096. Error: {report['error']}", '',
             '| Cost convention | G = Q/R30 | H = R30/C | Q/R100 |', '|---|---|---|---|']
    for name, x in report['sensitivities'].items():
        lines.append('| ' + name + ' | ' + ' | '.join(f"{x[n]['speed_ratio']:.3f} {x[n]['interval_95']}" for n in ('G', 'H', 'G100')) + ' |')
    if report['efficacy_eligible']:
        lines += ['', f"Approaches C: {report['approaches_C']}. R100: {report['R100_descriptive_band']}.",
                  f"No useful gain at either dose: {report['no_useful_gain_at_either_dose']}.",
                  'Corpus/cell/realization spread, gap share, solves, sensitivities and resolution price are in result.json. Selected-state audit is in variation.json.']
    lines += ['', report['limits']]
    (out / 'report.md').write_text('\n'.join(lines) + '\n')
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for arm in ARMS:
        rs = [r for r in rows if r['arm'] == arm]
        if not rs:
            continue
        budgets = np.geomspace(256, 524288, 100)
        axes[0].plot(budgets, [np.mean([r['solved'] and r['evaluations'] <= b for r in rs]) for b in budgets], label=arm)
        pts = defaultdict(list)
        for r in rs:
            for ev, accuracy, diversity in r['curve']:
                pts[ev].append((accuracy, diversity))
        xs = sorted(pts)
        for ax, j in ((axes[1], 0), (axes[2], 1)):
            ax.plot(xs, [np.median([v[j] for v in pts[x]]) for x in xs], label=arm)
    for ax, label in zip(axes, ('Fraction D1331-exact', 'Best training cases (active runs)', 'Behavioural diversity (active runs)')):
        ax.set(xscale='log', xlabel='Evaluations', ylabel=label)
        if ax.lines:
            ax.legend()
    fig.tight_layout()
    fig.savefig(out / 'diagnostics.png', dpi=150)
    plt.close(fig)
    # Exact descriptive count/span distributions, averaged within corpus/realization.
    variation = json.loads((out / 'variation.json').read_text())
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for i, prior in enumerate(('uniform', 'C_solvers')):
        for j, metric in enumerate(('count_histogram', 'span_histogram')):
            for arm in ARMS:
                hist = []
                for corpus in variation['corpora'].values():
                    by_k = []
                    for name, v in corpus.items():
                        if name.startswith(arm + '-'):
                            h = np.asarray(v[prior]['full_offspring'][metric], dtype=float)
                            by_k.append(h / h.sum())
                    hist.append(np.mean(by_k, axis=0))
                axes[i, j].plot(range(33), np.mean(hist, axis=0), label=arm)
            axes[i, j].set(title=f'{prior}: full offspring', xlabel=metric, ylabel='Probability')
            axes[i, j].legend()
    fig.tight_layout()
    fig.savefig(out / 'variation.png', dpi=150)
    plt.close(fig)
