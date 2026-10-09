"""1350 complete-roster procedure comparison; historical replay controls pairing."""

import math

import numpy as np

from experiments.chem_tape.comparison_gate_report import describe, balanced_target_n
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.fragment_report import comparison, plots, row_key, METRIC_DEFINITIONS

ARMS = ('E', 'W_E')
SCOPE = ('Externally extracted pre-solve literal windows on then-addition development cells, '
         'conditional on exact-solver C. No solver-free system, inheritance, fresh transfer, '
         'join mechanism, semantic modularity or joint-content versus token-supply conclusion. '
         'E/F compares complete source/content/length procedures; unresolved is not equality. '
         'Solver-window occurrence does not measure ancestry. Return to strategy for every outcome.')


def route(stat):
    lower, upper = stat['interval_95']
    if upper < 1:
        return 'harm_ends_source'
    if lower > 1 and stat['speed_ratio'] >= 1.10:
        return 'useful_early_source_earns_strategy_review'
    if upper < 1.10:
        return 'no_worthwhile_increment_ends_source'
    return 'unresolved_price_resolution'


def diagnostics(rows, libraries):
    result = {}
    for arm in ARMS:
        rs = [r for r in rows if r['arm'] == arm]
        stats = {k: ([sum(r['operator'][k][j] for r in rs) for j in range(7)]
                     if k.endswith('histogram') else sum(r['operator'][k] for r in rs))
                 for k in rs[0]['operator']}
        occurrences = [sum(r['solver'][s:s + len(f['tokens'])] == f['tokens']
                           for f in libraries[r['corpus']]['fragments']
                           for s in range(33 - len(f['tokens']))) for r in rs if r['solved']]
        stats.update(realized_child_fraction=stats['edited_children'] / max(1, stats['eligible_children']),
                     tokens_changed_per_edit=stats['changed_tokens'] / max(1, stats['edited_children']),
                     solvers_with_library_window=sum(v > 0 for v in occurrences),
                     solver_library_share=sum(v > 0 for v in occurrences) / len(occurrences) if occurrences else None,
                     solver_library_occurrences=sum(occurrences),
                     fallback_searches=sum(r.get('fallback', False) for r in rs))
        result[arm] = stats
    return result


def report(out, rows, schedule, libraries, preparation, historical):
    expected = {row_key(r): r for r in schedule}
    if (len(expected) != len(schedule) or len(rows) != len(schedule)
            or len({row_key(r) for r in rows}) != len(rows)):
        raise ValueError('incomplete/duplicate roster; no efficacy report')
    if any(row_key(r) not in expected or any(r[k] != v for k, v in expected[row_key(r)].items()) for r in rows):
        raise ValueError('changed roster metadata; no efficacy report')
    paired = preparation['historical_paired']
    reference_status = 'paired after48 bit-exact replays' if paired else 'ALL C/F/W historical unpaired references only'
    pairs = [('E', 'W_E')]
    pooled = rows
    if paired:
        expected_historical = {(*key[:3], arm) for key in expected for arm in ('C', 'F', 'W')}
        if len(historical) != len(expected_historical) or {row_key(r) for r in historical} != expected_historical:
            raise ValueError('incomplete historical reference roster')
        indexed = {row_key(r): r for r in historical}
        for r in rows:
            mate = indexed[(*row_key(r)[:3], 'C')]
            if any(r[k] != mate[k] for k in ('initial_tokens_hash', 'training_indices', 'table_hash', 'cap', 'pop_size')):
                raise ValueError('historical pairing metadata changed despite replay')
        pooled = rows + historical
        pairs += [('E', 'F'), ('E', 'C'), ('W_E', 'W')]

    def contrasts(rs, **kwargs):
        return {f'{x}/{y}': comparison(rs, x, y, **kwargs) for x, y in pairs}

    stats = contrasts(pooled)
    summaries = {a: describe([r for r in rows if r['arm'] == a]) for a in ARMS}
    diag = diagnostics(rows, libraries)
    sensitivity = dict(cap_penalty_1=contrasts(pooled, penalty=1), both_solved=contrasts(pooled, both=True),
                       families={f: contrasts(pooled, family=f) for f in ('BE', 'PA')})
    per_cell = {cid: dict(comparisons=contrasts([r for r in pooled if r['cell'] == cid]),
                         summaries={a: describe([r for r in rows if r['cell'] == cid and r['arm'] == a]) for a in ARMS})
                for cid in sorted({r['cell'] for r in rows})}
    means = {a: dict(actual_evaluations=float(np.mean([r['evaluations'] for r in rows if r['arm'] == a])),
                     worker_seconds=float(np.mean([r['seconds'] for r in rows if r['arm'] == a]))) for a in ARMS}
    seconds_saved = means['W_E']['worker_seconds'] - means['E']['worker_seconds']
    extraction = preparation['extraction_cost']['worker_seconds']
    partial = preparation['partial_collection_cost']['worker_seconds']
    arithmetic = dict(means=means, mean_worker_seconds_saved=seconds_saved,
                      mean_actual_evaluations_saved=means['W_E']['actual_evaluations'] - means['E']['actual_evaluations'],
                      extraction_only_break_even_searches=extraction / seconds_saved if seconds_saved > 0 else None,
                      partial_plus_extraction_cost_scenario_break_even_searches=(partial + extraction) / seconds_saved if seconds_saved > 0 else None,
                      caveat='Worker-seconds only; descriptive E/W_E workload savings. Both arms share exact C and partial-derived length laws. Charging partial acquisition to E alone is a conservative scenario, not a matched end-to-end repayment or a geometric cost-ratio conversion.')
    pricing = preparation['resolution_cost']
    target_n = balanced_target_n(stats['E/W_E']['sd_log'], math.log(1.05), 16)
    extra = target_n - 16
    scoring = extra / 16 * preparation['admission']['projected_seconds']
    build = 1.15 * extra / pricing['workers'] * sum(pricing[k] for k in (
        'source_worker_seconds_per_corpus', 'exact_source_worker_seconds_per_corpus',
        'library_worker_seconds_per_corpus', 'fit_worker_seconds_per_corpus'))
    price = dict(target_half_width_factor=1.05, scenario_corpora=target_n, new_balanced_corpora=extra,
                 additional_scoring_queue_seconds=scoring, additional_preparation_queue_seconds=build,
                 reporting_queue_seconds=pricing['reporting_queue_seconds'], agent_hours=pricing['agent_hours'],
                 complete_expected_hours=(scoring + build + pricing['reporting_queue_seconds']) / 3600 + pricing['agent_hours'],
                 caveat='Observed corpus SD assumed unchanged. Repeat balanced partial collection, exact C acquisition/fitting and extraction/scoring. More seeds may not remove corpus heterogeneity. Price is conditional, no automatic continuation.')
    result = dict(complete=True, primary_bank='then-addition-v1', primary_seeds=preparation['admission']['selected_seeds'],
                  corpus_n=16, decision=route(stats['E/W_E']), comparisons=stats,
                  sensitivity=sensitivity, per_cell=per_cell, summaries=summaries, diagnostics=diag,
                  historical_status=reference_status,
                  historical_summaries={a: describe([r for r in historical if r['arm'] == a]) for a in ('F', 'W', 'C')},
                  costs=dict(arithmetic=arithmetic, extraction=preparation['extraction_cost'],
                             partial_collection=preparation['partial_collection_cost'],
                             shared_exact_collection=preparation['shared_exact_collection_cost'],
                             historical_replay=preparation['historical_replay_cost']),
                  resolution_price=price,
                  complete_early_stage_price=dict(allocated=False, scenario_total_hours=[6, 9],
                     caveat='Proposal planning scenario; partial-decoder then-addition search rate unmeasured. Requires strategy review, E/C and W_E/W inspection and a new allocation.'),
                  metric_definitions=dict(METRIC_DEFINITIONS, speed_direction='E/W_E>1 favors E; exp(mean paired log(cost_W_E/cost_E)); unsolved2cap,95% t15df'),
                  scope=SCOPE)
    write_json(out, 'result.json', result)
    plots(out, rows, result, arms=ARMS)
    (out / 'diagnostics.png').replace(out / 'then_addition_diagnostics.png')
    lines = [f"Decision: **{result['decision']}** (ordered primary rule).", '', SCOPE, '',
             reference_status + '.', '', '| ratio | estimate | 95% interval |', '|---|---:|---|']
    for key, s in stats.items():
        lines.append(f"| {key} | {s['speed_ratio']:.3f} | {s['interval_95'][0]:.3f}–{s['interval_95'][1]:.3f} |")
    lines += ['', 'Primary speed ratio >1 favors E. Secondary intervals are descriptive. A win earns strategy review, not proof of a >10% true effect or a complete early-data system.',
              'Inspect E/C and W_E/W before stage two; if pairing failed these comparisons are unavailable. Arithmetic savings, separately charged partial/exact acquisition, sensitivities, cell results and conditional x1.05 resolution pricing are in result.json.']
    (out / 'report.md').write_text('\n'.join(lines) + '\n')
    return result
