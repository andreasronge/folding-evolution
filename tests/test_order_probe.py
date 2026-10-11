"""Semantic pooling boundaries that can change the 1129 interpretation."""

import pytest

from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.order_bank import helper, roster, split, verify
from experiments.chem_tape.order_library import build
from experiments.chem_tape.order_run import schedules, seed_audit, summarize, envelopes
from experiments.chem_tape.tree_library import extract

INPUTS = inputs_for('D625')


def source_row(cell, prefix, repeat=0, solved=True):
    return dict(cell=cell, arm='R-tree', solved=solved, build=0, repeat=repeat,
                evaluations=256, worker_seconds=0.1,
                attempts=[dict(solver_tree=list(prefix))])


def test_manifest_semantics_and_protected_split():
    cells = roster()
    assert len(cells) == 54 and len({c['label_hash'] for c in cells}) == 54
    assert verify(cells)['passed']
    selected = split(cells)
    assert len(selected['source']) == 24
    assert len(selected['development']) == 6
    assert len(selected['protected']) == 24
    assert not set(selected['development']) & set(selected['protected'])
    assert sum(c.get('disjoint', False) for c in cells if c['id'] in selected['protected']) == 4
    bank = dict(split=selected, screen=dict(cells=cells), inputs=INPUTS)
    audit = seed_audit(bank)
    assert audit['admitted']
    schedule = schedules(bank)
    assert len(schedule['source']) == 384 and len(schedule['score']) == 480
    for m in schedule['score']:
        paired = [r for r in schedule['score'] if (r['cell'], r['build'], r['repeat']) == (m['cell'], m['build'], m['repeat'])]
        assert len(paired) == 5 and all(r['seeds'] == m['seeds'] for r in paired)
    protected = schedule['score'][0] | dict(cell=selected['protected'][0])
    with pytest.raises(ValueError, match='protected'):
        envelopes([protected], bank, [], dict(order=[], sum=[], cutoff=65536))


def test_solver_dedup_and_literal_extractor_unchanged():
    h = helper('lo', 0, 1).prefix
    # The same class occurs twice per solver, but counts once per solver.
    tree = (9,) + h + h
    rows = [source_row('a', tree), source_row('b', tree), source_row('a', tree, 1)]
    lib = build(rows, ['a', 'b'], INPUTS)
    assert lib['literal'] == extract(rows, ['a', 'b'])[0]
    d = lib['helper_diagnostics']['lo01']['semantic']
    assert d['solver_count'] == 3 and d['source_cells'] == ['a', 'b']
    assert d['included'] and d['smallest_prefix'] == list(h)
    # One-node input classes enter pooling, but cannot consume the emission cap.
    assert all(3 <= e['nodes'] <= 9 for e in lib['semantic'])


def test_emission_size_limit_does_not_synthesize_helper():
    # Equal to lo01, but a ten-node observed selector; no descendant is lo01.
    large = (11, 0, 1, 10, 9, 0, 5, 9, 1, 5)
    assert len(large) == 10
    rows = [source_row('a', (9,) + large + (2,)), source_row('b', (9,) + large + (3,))]
    lib = build(rows, ['a', 'b'], INPUTS)
    d = lib['helper_diagnostics']['lo01']['semantic']
    assert d['recurrent'] and d['nodes'] == 10
    assert not d['admissible'] and not d['included'] and d['uncapped_rank'] is None
    assert d['smallest_prefix'] == list(large)
    assert not lib['helper_diagnostics']['lo01']['literal']


def test_distinct_cell_recurrence_and_failures_charged():
    h = helper('hi', 2, 3).prefix
    rows = [source_row('a', (9,) + h + (0,)), source_row('a', (9,) + h + (1,), 1),
            source_row('b', (), solved=False)]
    lib = build(rows, ['a', 'b'], INPUTS)
    d = lib['helper_diagnostics']['hi23']['semantic']
    assert d['solver_count'] == 2 and not d['recurrent'] and not d['included']
    assert lib['source_solves'] == 2 and lib['source_jobs'] == 3
    assert lib['acquisition_evaluations'] == 768


def test_gap_undefined_without_positive_order_gap():
    cells = roster()
    bank = dict(split=split(cells), screen=dict(cells=cells))
    rows = [dict(arm=arm, build=0, evaluations=1024, solved=True, worker_seconds=0.1,
                 attempts=[dict(solved=True)]) for arm in ('R-tree', 'R-sum', 'R-order', 'R-L', 'R-S')]
    report = summarize(rows, [], bank)
    assert all(s['log_gap_recovered'] is None for s in report['arms'].values())
    assert not report['qualifying_arms']
