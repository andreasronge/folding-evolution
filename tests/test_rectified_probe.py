"""Rectifier semantics, reporting isolation, fixed grids and provenance gates."""

import copy
import json

import numpy as np
import pytest

from experiments.chem_tape import rectified_bank as bank, rectified_run as run, order_library
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.tree_gp_search import Tree
from tests.test_order_probe import source_row


def test_bank_and_seed_paired_fixed_allocation():
    b = run.load_bank()
    assert len(b['screen']['cells']) == 54
    assert all(c['retained'] for c in b['screen']['cells'])
    assert [len(b['split'][k]) for k in ('source', 'development', 'protected')] == [24, 6, 24]
    assert b['split']['development'][:4] == list(bank.SEEN)
    assert b['split']['development'][4:] == ['O:pos12+neg13', 'O:pos03+neg13']
    schedule = run.schedules(b)
    assert [len(schedule[p]) for p in ('source', 'score')] == [384, 384]
    assert run.seed_audit(b)['admitted']
    for offset in range(0, 384, 4):
        assert len({tuple(m['seeds']) for m in schedule['score'][offset:offset+4]}) == 1
    assert not set(m['cell'] for m in schedule['score']) & set(b['split']['protected'])


def test_reporting_vectors_never_change_emitted_pool():
    b = run.load_bank()
    h = bank.helper('pos', 0, 1).prefix
    rows = [source_row('a', (9,) + h + (2,)), source_row('b', (9,) + h + (3,))]
    ordinary = order_library.build(rows, ['a', 'b'], b['inputs'], cap=None)
    reported = order_library.build(rows, ['a', 'b'], b['inputs'], cap=None, diagnostic_vectors=run.helper_vectors(b['inputs']))
    blind = order_library.build(rows, ['a', 'b'], b['inputs'], cap=None, diagnostic_vectors={})
    assert ordinary['semantic'] == reported['semantic'] == blind['semantic']
    assert ordinary['literal'] == reported['literal'] == blind['literal']
    d = reported['helper_diagnostics']['pos01']['semantic']
    assert d['recurrent'] and d['included'] and d['nodes'] == 8
    assert reported['census'][0]['helpers']['pos01'] == [8]


def test_workers_have_only_labels_and_frozen_donors():
    b = run.load_bank()
    frozen = run.freeze(b)
    libs = [dict(semantic=[]) for _ in range(8)]
    metas = run.schedules(b)['score'][:4]
    jobs = run.envelopes(metas, b, libs, frozen)
    assert all(set(j[1]) == {'id', 'labels'} for j in jobs)
    assert jobs[0][-1] is None and jobs[1][-1] == frozen['rect']
    assert jobs[2][-1] == []
    assert jobs[3][-1] == [e['prefix'] for e in run.transport()['libraries.json'][0]['semantic_all']]
    changed = copy.deepcopy(b)
    for c in changed['screen']['cells']:
        c['helpers'] = ['dummy reporting annotation']
        c['canonical_tree'] = []
    assert run.envelopes(metas, changed, libs, frozen) == jobs
    for a in run.ARMS:
        with pytest.raises(ValueError, match='protected'):
            run.envelopes([metas[0] | dict(arm=a, cell=b['split']['protected'][0])], b, libs, frozen)


def test_advisory_rule_complete_and_arithmetic_thresholds():
    assert all(run.investment(24, .1, .9, .5, .67, True)['gates'].values())
    r = run.investment(23, .1, .8, .6, .9, False)
    assert 'low observed acquisition under this source effort' in r['reasons']
    assert 'supplied-prior performance below the investment threshold' in r['reasons']
    assert 'coverage shortfall, cause unresolved' in run.investment(23, .25, 1, .4, .6, True)['reasons']
    assert run.investment(24, .5, 1, .4, .68, True)['reasons'] == ['helpers available but insufficient observed saving']
    assert run.investment(0, .0, .8, .6, .6, False)['mechanism_lead']


def canonical_rows(b, metas):
    by = {c['id']: c for c in b['screen']['cells']}
    rows = []
    for m in metas:
        t = Tree(tuple(by[m['cell']]['canonical_tree']))
        # Build-dependent budgets test pooling, rather than averaging per-build ratios.
        cost = (256 if m['build'] < 4 else 2560) if m['arm'] == 'R-tree' else 512
        rows.append(m | dict(solved=True, evaluations=cost, worker_seconds=cost/1000,
                             attempts=[dict(seed=m['seeds'][0], solved=True, evaluations=cost,
                                            solver_tree=list(t.prefix), solver=list(t.program))]))
    return rows


def test_report_complete_grid_and_pooled_build_bootstrap():
    b = run.load_bank()
    rows = canonical_rows(b, run.schedules(b)['score'])
    libs = [dict(source_jobs=48, source_solves=48, acquisition_evaluations=10000,
                 acquisition_worker_seconds=1, extraction_census_seconds=.1, validation_census_seconds=.1,
                 semantic=[], helper_diagnostics={}, census=[]) for _ in range(8)]
    r = run.summarize(rows, libs, b)
    denominator = np.asarray([256]*4 + [2560]*4)
    selected = np.random.default_rng(run.BOOTSTRAP_SEED).integers(8, size=(run.DRAWS, 8))
    result = r['contrasts']['R-all/R-tree']['evaluations']
    assert result['point'] == pytest.approx(512/denominator.mean())
    assert result['interval95'] == pytest.approx(np.quantile(512/denominator[selected].mean(1), [.025, .975]))
    with pytest.raises(ValueError, match='incomplete'):
        run.summarize(rows[:-1], libs, b)
    altered = copy.deepcopy(rows)
    altered[0]['seeds'][0] += 1
    with pytest.raises(ValueError, match='schedule'):
        run.summarize(altered, libs, b)


def test_source_replay_and_tampered_transport_fail_closed(tmp_path, monkeypatch):
    b = run.load_bank()
    frozen, schedule, audit = run.freeze(b), run.schedules(b, True), run.seed_audit(b)
    rows = run.base.validate_rows(canonical_rows(b, schedule['source']), schedule['source'], b)
    libs = run.libraries_from(rows, b, 1)
    assert sum(bool(c['own_helper_sizes']) for c in libs[0]['census']) == 48
    assert len(libs[0]['helper_diagnostics']) == 12
    p = dict(admitted=True, smoke=True)
    for name, value in [('source_rows', rows), ('libraries', libs), ('bank', b), ('freeze', frozen), ('schedule', schedule), ('audit', audit)]:
        p[name + '_hash'] = digest(value)
    p['preparation_hash'] = digest(p)
    for name, value in [('bank', b), ('method_freeze', frozen), ('libraries', libs), ('schedules', schedule), ('seed_audit', audit), ('preparation', p)]:
        write_json(tmp_path, name + '.json', value)
    (tmp_path / 'acquisition.jsonl').write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
    assert run.load_prepared(tmp_path, True)[2] == libs
    changed = copy.deepcopy(libs)
    changed[0]['semantic'].pop()
    write_json(tmp_path, 'libraries.json', changed)
    with pytest.raises(ValueError, match='provenance'):
        run.load_prepared(tmp_path, True)
    monkeypatch.setattr(run, 'TRANSPORT_SHA', '0'*64)
    with pytest.raises(ValueError, match='artifact changed'):
        run.transport()
