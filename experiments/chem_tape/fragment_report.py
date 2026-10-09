"""Complete-roster corpus contrasts and approved practical decision rules."""

import math
from collections import defaultdict

import numpy as np

from experiments.chem_tape.comparison_gate_report import interval, describe, balanced_target_n
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.fragment_operator import ARMS
from experiments.chem_tape.solver_corpus_report import cost

METRIC_DEFINITIONS = dict(
    speed_ratio='exp(mean_corpus(mean_paired_cell_seed(log(cost_Y)-log(cost_X)))); unsolved cost=2*cap; 95% t interval over 16 corpus contrasts',
    library_share='fraction of full-domain solver tapes containing at least one exact contiguous library window; occurrence, not causal operator ancestry',
    offspring_defaults='underflow plus wrong-type events in first non-elite offspring, every 32 generations, on four fixed diagnostic inputs; descriptive sparse sample',
    tokens_changed='decoded Hamming distance between child after ordinary variation and after block edit; repaired next position is unchanged in decoded space',
)
PAIRS = [('F', 'C'), ('F', 'B'), ('F', 'W'), ('W', 'C'), ('B', 'C')]


def row_key(r):
    return (r['corpus'], r['cell'], r['seed'], r['arm'])


def comparison(rows, X, Y, penalty=2, both=False, family=None):
    grouped = defaultdict(list)
    indexed = {row_key(r): r for r in rows}
    for r in rows:
        if r['arm'] != X or (family and r['family'] != family):
            continue
        mate = indexed[(r['corpus'], r['cell'], r['seed'], Y)]
        if both and not (r['solved'] and mate['solved']):
            continue
        grouped[r['corpus']].append(np.log(cost(mate, penalty)) - np.log(cost(r, penalty)))
    corpora = sorted(grouped)
    result = interval([np.mean(grouped[c]) for c in corpora])
    result.update(corpora=corpora, paired_searches=sum(map(len, grouped.values())),
                  pairs_per_corpus={c: len(grouped[c]) for c in corpora})
    return result


def route(comparisons):
    fc, fb, fw = [comparisons[k] for k in ('F/C', 'F/B', 'F/W')]
    lc, uc = fc['interval_95']
    lb, ub = fb['interval_95']
    lw, uw = fw['interval_95']
    if fc['speed_ratio'] >= 1.15 and min(lc, lb, lw) > 1:
        return 'earns_review_of_reuse'
    if uc < 1.10:
        return 'ends_extractor_operator'
    if lc > 1 and uw < 1.10:
        return 'no_worthwhile_fragment_increment_over_W'
    if lc > 1 and ((lw <= 1 and uw >= 1.10) or (lb <= 1 and ub >= 1.10)):
        return 'joint_content_unresolved'
    return 'otherwise_unresolved'


def report(out, rows, schedule, libraries, preparation):
    if len(rows) != len(schedule) or len({row_key(r) for r in rows}) != len(rows) or {row_key(r) for r in rows} != {row_key(r) for r in schedule}:
        raise ValueError('incomplete/duplicate roster; no efficacy report')
    comparisons = {f'{X}/{Y}': comparison(rows, X, Y) for X, Y in PAIRS}
    sensitivities = {
        'cap_penalty_1': {f'{X}/{Y}': comparison(rows, X, Y, penalty=1) for X, Y in PAIRS},
        'both_solved': {f'{X}/{Y}': comparison(rows, X, Y, both=True) for X, Y in PAIRS},
        'families': {f: {f'{X}/{Y}': comparison(rows, X, Y, family=f) for X, Y in PAIRS} for f in ('BE', 'PA')},
    }
    summaries = {a: describe([r for r in rows if r['arm'] == a]) for a in ARMS}
    diagnostics = {}
    for arm in ARMS:
        rs = [r for r in rows if r['arm'] == arm]
        keys = rs[0]['operator'].keys()
        stats = {k: ([sum(r['operator'][k][j] for r in rs) for j in range(7)] if k.endswith('histogram')
                     else sum(r['operator'][k] for r in rs)) for k in keys}
        stats['realized_child_fraction'] = stats['edited_children'] / max(1, stats['eligible_children'])
        stats['tokens_changed_per_edit'] = stats['changed_tokens'] / max(1, stats['edited_children'])
        solved = [r for r in rs if r['solved']]
        occurrences = []
        for r in solved:
            fs = libraries[r['corpus'] + '|' + r['cell']]['fragments']
            tape = r['solver']
            occurrences.append(sum(tape[s:s + len(f['tokens'])] == f['tokens']
                                   for f in fs for s in range(33 - len(f['tokens']))))
        stats['solvers_with_library_window'] = sum(n > 0 for n in occurrences)
        stats['solver_library_share'] = stats['solvers_with_library_window'] / len(solved) if solved else None
        stats['solver_library_occurrences'] = sum(occurrences)
        stats['seconds_per_evaluation'] = sum(r['seconds'] for r in rs) / sum(r['evaluations'] for r in rs)
        diagnostics[arm] = stats
    prices = {}
    pricing = preparation['resolution_cost']
    for key in ('F/C', 'F/B', 'F/W'):
        n = balanced_target_n(comparisons[key]['sd_log'], math.log(1.07), 16)
        extra = max(0, n - 16)
        scoring = extra / 16 * preparation['admission']['projected_seconds']
        preparation_seconds = 1.15 * extra * sum(pricing[k] for k in (
            'source_collection_worker_seconds_per_corpus', 'fit_worker_seconds_per_corpus',
            'library_worker_seconds_per_corpus')) / pricing['workers']
        prices[key] = dict(target_half_width_factor=1.07, scenario_corpora=n,
                          new_corpora=extra, scenario='observed corpus SD stays fixed; more seeds may not remove effect heterogeneity; new balanced corpora repeat source collection and fitting',
                          additional_scoring_queue_seconds=scoring,
                          additional_preparation_queue_seconds=preparation_seconds,
                          reporting_queue_seconds=pricing['reporting_queue_seconds'], agent_hours=pricing['agent_hours'],
                          complete_expected_hours=(scoring + preparation_seconds + pricing['reporting_queue_seconds']) / 3600 + pricing['agent_hours'])
    result = dict(complete=True, seeds=preparation['admission']['selected_seeds'], comparisons=comparisons,
                  decision=route(comparisons), sensitivity=sensitivities, summaries=summaries,
                  diagnostics=diagnostics, resolution_price=prices, reuse_price=preparation['reuse_price'],
                  metric_definitions=METRIC_DEFINITIONS,
                  scope='Externally fitted literal-block procedure and matched controls on comparison-gate-v1 development cells; no modularity, acquisition, or fresh-bank transfer claim.')
    write_json(out, 'result.json', result)
    lines = [f"Decision: **{result['decision']}** (approved precedence).", '', result['scope'], '',
             '| ratio | estimate | 95% interval |', '|---|---:|---|']
    for key, stat in comparisons.items():
        lines.append(f"| {key} | {stat['speed_ratio']:.3f} | {stat['interval_95'][0]:.3f}–{stat['interval_95'][1]:.3f} |")
    lines += ['', 'Rule 3 is a practical stopping decision. W/C must independently support a gain before using “block editing suffices”.',
              'A broad interval remains unresolved. Resolution/reuse prices and descriptive diagnostics are in result.json.']
    (out / 'report.md').write_text('\n'.join(lines) + '\n')
    plots(out, rows, result)
    return result


def plots(out, rows, result, arms=ARMS):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for arm in arms:
        rs = [r for r in rows if r['arm'] == arm]
        axes[0, 0].plot(sorted([cost(r) for r in rs]), label=arm)
        points = defaultdict(list)
        for r in rs:
            for ev, fitness, diversity in r['curve']:
                points[ev].append((fitness, diversity))
        xs = sorted(points)
        axes[0, 1].plot(xs, [np.mean([p[0] for p in points[x]]) for x in xs], label=arm)
        axes[0, 2].plot(xs, [np.mean([p[1] for p in points[x]]) for x in xs], label=arm)
        axes[1, 0].plot(range(7), result['diagnostics'][arm]['changed_histogram'], label=arm)
    for ax in axes.flat[:4]:
        ax.legend()
    axes[0, 0].set(title='Search cost distribution', yscale='log', xlabel='sorted searches')
    axes[0, 1].set(title='Observed fitness (surviving searches)', xlabel='evaluations', ylabel='correct / 64')
    axes[0, 2].set(title='Behavior diversity (surviving searches)', xlabel='evaluations', ylabel='unique correctness vectors')
    axes[1, 0].set(title='Realized changed tokens per block', xlabel='token Hamming distance')
    axes[1, 1].bar(arms, [result['summaries'][a]['solve_rate'] for a in arms])
    axes[1, 1].set(title='Solve fraction', ylim=(0, 1))
    axes[1, 2].bar(arms, [result['diagnostics'][a]['tokens_changed_per_edit'] for a in arms])
    axes[1, 2].set(title='Mean realized edits per attempted block')
    fig.tight_layout()
    fig.savefig(out / 'diagnostics.png', dpi=150)
    plt.close(fig)
