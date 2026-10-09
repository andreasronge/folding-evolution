"""Complete-roster W/R primary and descriptive development-bank contrasts."""

import math

import numpy as np

from experiments.chem_tape.comparison_gate_report import describe, balanced_target_n
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.fragment_report import comparison, row_key, plots

SCOPE = ('Matched boundary-policy test and its downstream effects in externally fitted C on development banks. '
         'Identical block proposals hold on identical inputs, not along divergent trajectories. '
         'No sole-cause attribution, acquisition, inheritance, modules, C/T, or fresh-bank transfer claim. '
         'All outcomes return to strategy; no automatic top-up.')


def route(stat):
    lo, hi = stat['interval_95']
    if hi < 1:
        return 'ripple_helps_drop_repair'
    if lo > 1 and stat['speed_ratio'] >= 1.10:
        return 'preservation_needed_keep_repair'
    if hi < 1.10:
        return 'not_needed_at_this_resolution'
    return 'unresolved_keep_incumbent_repair'


def diagnostics(rows, arms):
    result = {}
    for arm in arms:
        rs = [r for r in rows if r['arm'] == arm]
        stats = {}
        for key in rs[0]['operator']:
            if key.endswith('histogram'):
                size = max(len(r['operator'][key]) for r in rs)
                stats[key] = [sum(r['operator'][key][j] if j < len(r['operator'][key]) else 0 for r in rs) for j in range(size)]
            else:
                stats[key] = sum(r['operator'][key] for r in rs)
        # Historical W changed counts are entirely inside its preserved block.
        if 'inside_changed_tokens' not in stats:
            stats.update(inside_changed_tokens=stats['changed_tokens'], suffix_changed_tokens=0,
                         inside_changed_histogram=stats['changed_histogram'].copy(), suffix_changed_histogram=[stats['edited_children']] + [0] * 32)
        stats.update(realized_child_fraction=stats['edited_children'] / max(1, stats['eligible_children']),
                     tokens_changed_per_edit=stats['changed_tokens'] / max(1, stats['edited_children']),
                     inside_tokens_changed_per_edit=stats['inside_changed_tokens'] / max(1, stats['edited_children']),
                     suffix_tokens_changed_per_edit=stats['suffix_changed_tokens'] / max(1, stats['edited_children']),
                     suffix_ripple_fraction=(1 - stats['suffix_changed_histogram'][0] / stats['edited_children']) if stats['edited_children'] else 0)
        result[arm] = stats
    return result


def report(out, rows, schedule, preparation, historical):
    expected = {row_key(r): r for r in schedule}
    if (len(expected) != len(schedule) or len(rows) != len(schedule) or len({row_key(r) for r in rows}) != len(rows)
            or any(row_key(r) not in expected or any(r[k] != v for k, v in expected[row_key(r)].items()) for r in rows)):
        raise ValueError('incomplete/duplicate/changed roster; no efficacy report')
    paired = preparation['historical_paired']
    if not paired and historical:
        raise ValueError('fallback cannot use historical paired contrasts')
    arms = ('W', 'R', 'C') if paired else ('W', 'R')
    if paired:
        expected_refs = {(*row_key(r)[:3], a) for r in schedule for a in ('W', 'C')}
        if len(historical) != len(expected_refs) or {row_key(r) for r in historical} != expected_refs:
            raise ValueError('incomplete historical references')
        indexed = {row_key(r): r for r in rows}
        for r in historical:
            mate = indexed[(*row_key(r)[:3], 'R')]
            if r['phase'] != mate['phase'] or r['family'] != mate['family']:
                raise ValueError('historical bank/family mismatch')
    combined = rows + historical
    pairs = [('W', 'R'), ('R', 'C')] if paired else [('W', 'R')]

    def contrasts(rs, **kwargs):
        return {f'{x}/{y}': comparison(rs, x, y, **kwargs) for x, y in pairs}

    banks = {}
    for phase in (('then_addition', 'holdout') if paired else ('then_addition',)):
        rs = [r for r in combined if r['phase'] == phase]
        bank = dict(comparisons=contrasts(rs), summaries={a: describe([r for r in rs if r['arm'] == a]) for a in arms},
                    sensitivity=dict(cap_penalty_1=contrasts(rs, penalty=1), both_solved=contrasts(rs, both=True),
                                     families={f: contrasts(rs, family=f) for f in ('BE', 'PA')}),
                    per_cell={cid: dict(comparisons=contrasts([r for r in rs if r['cell'] == cid]),
                        summaries={a: describe([r for r in rs if r['cell'] == cid and r['arm'] == a]) for a in arms})
                              for cid in sorted({r['cell'] for r in rs})},
                    diagnostics=diagnostics(rs, arms))
        for summary in bank['summaries'].values():
            summary['mean_evaluations'] = summary['actual_evaluations'] / summary['n']
            summary['mean_worker_seconds'] = summary['worker_seconds'] / summary['n']
        banks[phase] = bank
        plots(out, rs, bank, arms=arms)
        (out / 'diagnostics.png').replace(out / (phase + '_diagnostics.png'))
        suffix_plot(out, phase, bank, arms)
    primary = banks['then_addition']['comparisons']['W/R']
    decision = route(primary)
    n = balanced_target_n(primary['sd_log'], math.log(1.05), 16)
    extra = max(0, n - 16)
    means = {a: banks['then_addition']['summaries'][a]['actual_evaluations'] / banks['then_addition']['summaries'][a]['n'] for a in arms}
    scoring_seconds = 1.15 * extra * 256 * sum(np.mean([r['seconds'] for r in combined if r['phase'] == 'then_addition' and r['arm'] == a]) for a in ('W', 'R')) / 10
    pricing = preparation['resolution_cost']
    source_seconds = 1.15 * extra / 10 * sum(pricing[k] for k in (
        'source_collection_worker_seconds_per_corpus', 'library_worker_seconds_per_corpus',
        'historical_C_fit_worker_seconds_per_corpus'))
    result = dict(complete=True, historical_paired=paired, primary_bank='then_addition', primary_seeds=16,
                  holdout_seeds=8 if paired else 0, decision=decision, banks=banks,
                  chain_proposals_help_without_containment=(paired and decision == 'not_needed_at_this_resolution'
                      and banks['then_addition']['comparisons']['R/C']['interval_95'][0] > 1),
                  resolution_price=dict(target_half_width_factor=1.05, scenario_corpora=n, new_balanced_corpora=extra,
                      additional_scoring_queue_seconds=scoring_seconds, additional_preparation_queue_seconds=source_seconds,
                      reporting_queue_seconds=pricing['reporting_queue_seconds'], agent_hours=pricing['agent_hours'],
                      complete_expected_hours=(scoring_seconds + source_seconds + pricing['reporting_queue_seconds']) / 3600 + pricing['agent_hours'],
                      caveat='Conditional observed corpus-SD scenario, including fresh W/R on new corpora and historical source collection/fitting/library costs. Seed-only top-up may not remove heterogeneity. No work authorized.'),
                  arithmetic_mean_evaluations=means,
                  metric_definitions=dict(speed_ratio='exp(equal-corpus mean paired log(cost_Y)-log(cost_X)); unsolved2cap;95%t15df',
                      changed_tokens='actual decoded Hamming distance after ordinary variation; inside and suffix counted separately; suffix includes boundary',
                      worker_seconds='historical timings descriptive; current hardware/operator instrumentation differ'), scope=SCOPE)
    write_json(out, 'result.json', result)
    lines = [f"Decision: **{decision}** (then-addition only; approved precedence).", '', SCOPE, '']
    for phase, bank in banks.items():
        lines += [phase + (' (primary)' if phase == 'then_addition' else ' (descriptive)'), '',
                  '| ratio | estimate | 95% interval |', '|---|---:|---|']
        for key, s in bank['comparisons'].items():
            lines.append(f"| {key} | {s['speed_ratio']:.3f} | {s['interval_95'][0]:.3f}–{s['interval_95'][1]:.3f} |")
        lines.append('')
    lines += ['Rule2 supports retaining repair under the chosen decision rule, not proof of true benefit above1.10 or literal necessity. Rule3 is a resolution statement, not equality. Unresolved retains incumbent repair.',
              'Result.json includes cell/family/sensitivity, solve/cost/edit diagnostics and a conditional×1.05 resolution price. Return to strategy.']
    (out / 'report.md').write_text('\n'.join(lines) + '\n')
    return result


def suffix_plot(out, phase, bank, arms):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for arm in arms:
        stats = bank['diagnostics'][arm]
        for ax, name in zip(axes, ('inside', 'suffix')):
            vals = stats[name + '_changed_histogram']
            ax.plot(range(len(vals)), vals, label=arm)
            ax.set(title=name + ' actual token changes', xlabel='Hamming distance', ylabel='edited children', yscale='symlog')
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(out / (phase + '_ripple.png'), dpi=150)
    plt.close(fig)
