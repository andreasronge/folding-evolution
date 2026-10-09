"""Protect temporal exclusion, historical demotion and frozen paired inference."""

from copy import deepcopy

import pytest

from experiments.chem_tape.comparison_gate_bank import load_training
from experiments.chem_tape.fragment_library import extract_corpus
from experiments.chem_tape.fragment_operator import BlockOperator
from experiments.chem_tape.fragment_reuse_run import pinned_history
from experiments.chem_tape.fragment_run import CORPORA
from experiments.chem_tape.pre_solve_sources import select_sources
from experiments.chem_tape.pre_solve_run import schedule, smoke_schedule, admit, execute
from experiments.chem_tape.pre_solve_report import route, report
from experiments.chem_tape.then_addition_bank import load
from experiments.chem_tape.then_addition_run import frozen_source


def source_row():
    archive = [dict(kind='S', checkpoint=64, evaluations=16384, slot=slot,
                    cell='cell', source_seed=7, source_later_solved=True, exact=False,
                    tape=[slot] * 32, population_index=3, d1331_correct=slot)
               for slot in (9, 1, 1)]
    return dict(cell='cell', seed=7, solved=True, generations=128, evaluations=32768,
                archive=archive, worker_seconds=2, archive_verification_seconds=.1)


def test_temporal_exclusion_and_performance_blind_minimum_slot():
    r = source_row()
    selected, attempts = select_sources([r])
    assert selected[0]['tape'] == [1] * 32
    assert selected[0]['slot'] == 1
    assert attempts[0]['missing_checkpoints'] == [128, 256]
    # Swapping eventual success while retaining a legal observation must not select differently.
    later = deepcopy(r)
    later.update(solved=False, generations=256, evaluations=65536)
    for a in later['archive']:
        a['source_later_solved'] = False
    assert select_sources([later])[0][0]['tape'] == selected[0]['tape']
    for field, value in [('checkpoint', 128), ('exact', True), ('source_seed', 8)]:
        broken = deepcopy(r)
        broken['archive'][0][field] = value
        with pytest.raises(ValueError, match='archive'):
            select_sources([broken])
    empty = dict(later, archive=[])
    assert select_sources([empty])[1][0]['missing_checkpoints'] == [64, 128, 256]


def test_roster_reuses_historical_seeds_and_smoke_covers_all_cells_families():
    bank, _ = load()
    ids = bank['selected_ids']
    full, small, smoke = schedule(ids, 16), schedule(ids, 12), smoke_schedule(ids)
    assert len(full) == 8192 and len(small) == 6144 and len(smoke) == 64
    assert {tuple(r.items()) for r in small} <= {tuple(r.items()) for r in full}
    assert {r['corpus'] for r in smoke} == set(CORPORA)
    assert {(r['cell'], r['family']) for r in smoke} == {(c, f) for c in ids for f in ('BE', 'PA')}
    assert not {r['seed'] for r in full} & {r['seed'] for r in smoke}


def test_timing_fallback_never_depends_on_solve_rate():
    ids = [str(i) for i in range(16)]
    rows = [dict(r, seconds=8, solved=False) for r in smoke_schedule(ids)]
    p = admit(rows, 51.2, 120)
    assert p['selected_seeds'] == 16
    assert admit([dict(r, solved=True) for r in rows], 51.2, 120)['selected_seeds'] == 16
    rows = [dict(r, seconds=9) for r in rows]
    assert admit(rows, 57.6, 120)['selected_seeds'] == 12
    assert not admit([dict(r, seconds=12) for r in rows], 76.8, 120)['admitted']
    assert not admit(rows, 57.6, 1801)['admitted']


@pytest.mark.parametrize('point,lo,hi,label', [
    (.9, .8, .99, 'harm_ends_source'),
    (1.1, 1.01, 1.2, 'useful_early_source_earns_strategy_review'),
    (1.01, .95, 1.09, 'no_worthwhile_increment_ends_source'),
    (1.05, .97, 1.13, 'unresolved_price_resolution'),
    (1.1, 1, 1.2, 'unresolved_price_resolution'),
])
def test_primary_rule_boundaries(point, lo, hi, label):
    assert route(dict(speed_ratio=point, interval_95=[lo, hi])) == label


def test_new_report_demotes_all_history_and_enforces_complete_metadata(tmp_path):
    ids = load()[0]['selected_ids']
    roster = schedule(ids, 12)
    op = BlockOperator('C', [], 0).stats
    rows = [dict(r, solved=False, evaluations=524288, cap=524288, seconds=1,
                 operator=deepcopy(op), solver=None, curve=[[256, 32, 8]], fallback=False) for r in roster]
    libraries = {tid: dict(fragments=[]) for tid in CORPORA}
    p = dict(historical_paired=False, admission=dict(selected_seeds=12, projected_seconds=600),
             extraction_cost=dict(worker_seconds=100), partial_collection_cost=dict(worker_seconds=5000),
             shared_exact_collection_cost=dict(worker_seconds=48000), historical_replay_cost={},
             resolution_cost=dict(source_worker_seconds_per_corpus=300, exact_source_worker_seconds_per_corpus=3000,
                                  library_worker_seconds_per_corpus=10, fit_worker_seconds_per_corpus=1,
                                  workers=10, reporting_queue_seconds=600, agent_hours=3))
    result = report(tmp_path, rows, roster, libraries, p, [])
    assert list(result['comparisons']) == ['E/W_E']
    assert 'ALL C/F/W' in result['historical_status']
    assert result['comparisons']['E/W_E']['df'] == 15
    assert result['decision'] == 'no_worthwhile_increment_ends_source'
    assert result['costs']['arithmetic']['extraction_only_break_even_searches'] is None
    assert (tmp_path / 'then_addition_diagnostics.png').stat().st_size > 1000
    with pytest.raises(ValueError, match='incomplete'):
        report(tmp_path, rows[:-1], roster, libraries, p, [])
    broken = deepcopy(rows)
    broken[0]['phase'] = 'smoke'
    with pytest.raises(ValueError, match='metadata'):
        report(tmp_path, broken, roster, libraries, p, [])


def test_legacy_extractor_still_reconstructs_saved_whole_library():
    import numpy as np
    saved, _ = frozen_source()
    bank, cells = load_training()
    rows = [r for r in saved['search.jsonl'] if r['phase'] == 'collection' and r['corpus'] == 'BE1']
    indices = np.random.default_rng(0).choice(len(bank['inputs']), 96, replace=False).tolist()
    built = extract_corpus(('BE1', rows, bank['inputs'], cells, indices))
    assert built['whole_corpus'] == pinned_history()[1]['BE1']


def test_empty_library_adapter_makes_E_and_WE_identical_chain_searches():
    from experiments.chem_tape.four_reducer_maps import tables
    inputs = [[i, i, i] for i in range(80)]
    lib = [dict(tokens=[1, 2, 3]), dict(tokens=[1, 2, 3, 4, 5, 6])]
    results = []
    for arm in ('E', 'W_E'):
        meta = dict(arm=arm, seed=7, fallback=True)
        job = (dict(id='unreachable', labels=[99999] * 80), arm, tables()['G4'], 7,
               768, 256, inputs, 'v2_rmin_first')
        results.append(execute((job, meta, lib, inputs[:4], False)))
    ignored = {'arm', 'seconds', 'decode_seconds', 'budget_seconds'}
    assert {k: v for k, v in results[0].items() if k not in ignored} == {k: v for k, v in results[1].items() if k not in ignored}


def test_replayed_history_is_paired_and_speed_direction_is_cost_control_over_E(tmp_path):
    ids = load()[0]['selected_ids']
    roster = schedule(ids, 12)
    op = BlockOperator('C', [], 0).stats
    rows = [dict(r, solved=True, evaluations=256 if r['arm'] == 'E' else 512,
                 cap=524288, seconds=1, operator=deepcopy(op), solver=[0] * 32,
                 curve=[[256, 32, 8]], fallback=False, initial_tokens_hash='shared',
                 training_indices=[1, 2], table_hash=r['corpus'], pop_size=256) for r in roster]
    historical = [dict(r, arm=a, evaluations=v) for r in rows if r['arm'] == 'E'
                  for a, v in [('F', 768), ('C', 1536), ('W', 1024)]]
    p = dict(historical_paired=True, admission=dict(selected_seeds=12, projected_seconds=600),
             extraction_cost=dict(worker_seconds=100), partial_collection_cost=dict(worker_seconds=5000),
             shared_exact_collection_cost=dict(worker_seconds=48000), historical_replay_cost={},
             resolution_cost=dict(source_worker_seconds_per_corpus=300, exact_source_worker_seconds_per_corpus=3000,
                                  library_worker_seconds_per_corpus=10, fit_worker_seconds_per_corpus=1,
                                  workers=10, reporting_queue_seconds=600, agent_hours=3))
    libraries = {tid: dict(fragments=[]) for tid in CORPORA}
    result = report(tmp_path, rows, roster, libraries, p, historical)
    for ratio, value in [('E/W_E', 2), ('E/F', 3), ('E/C', 6), ('W_E/W', 2)]:
        assert result['comparisons'][ratio]['speed_ratio'] == pytest.approx(value)
    assert result['decision'] == 'useful_early_source_earns_strategy_review'
    assert result['comparisons']['E/W_E']['paired_searches'] == 3072
    with pytest.raises(ValueError, match='historical reference'):
        report(tmp_path, rows, roster, libraries, p, historical[:-1])
    bad = deepcopy(historical)
    bad[1]['initial_tokens_hash'] = 'changed'
    with pytest.raises(ValueError, match='pairing'):
        report(tmp_path, rows, roster, libraries, p, bad)
