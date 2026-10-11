"""Signed-gate admission, paired inference, search isolation and provenance gates."""

import copy
import json

import numpy as np
import pytest

from experiments.chem_tape import signed_gate_bank as bank, signed_gate_run as run, order_library
from experiments.chem_tape.comparison_gate_bank import digest
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.tree_gp_search import Tree


def raw_bank():
    return json.loads((run.DATA / 'manifest.json').read_text())


def canonical_rows(b, metas):
    by = {c['id']: c for c in b['screen']['cells']}
    rows = []
    for m in metas:
        tree = Tree(tuple(by[m['cell']]['canonical_tree']))
        index = b['split']['protected'].index(m['cell']) if m['cell'] in b['split']['protected'] else 0
        cost = 256 * (1 + m['build'] + index) if m['arm'] == 'R-tree' else 512
        rows.append(m | dict(solved=True, evaluations=cost, worker_seconds=cost/1000,
                             cap=524288, cutoff=65536, pop_size=256,
                             attempts=[dict(seed=m['seeds'][0], solved=True, evaluations=cost,
                                            solver_tree=list(tree.prefix), solver=list(tree.program))]))
    return rows


def empty_libraries(n):
    return [dict(source_jobs=96, source_solves=96, acquisition_evaluations=200000,
                 acquisition_worker_seconds=10, extraction_census_seconds=.2, validation_census_seconds=.1,
                 semantic=[], helper_diagnostics={}, census=[]) for _ in range(n)]


def test_frozen_bank_complete_split_and_fresh_paired_grid():
    b = run.load_bank()
    assert digest(b) == run.BANK_HASH
    assert [len(b['split'][k]) for k in ('source','development','protected')] == [48,6,18]
    assert b['split']['development'][:4] == list(bank.SEEN)
    assert b['split']['development'][4:] == ['O:p21+n03', 'O:p03+n12']
    assert all(c['retained'] and c['best_matches'] < 625 and c['best_old_matches'] < 500 for c in b['screen']['cells'])
    grid = run.schedules(b)
    assert [len(grid[p]) for p in ('source','development','protected')] == [2304,1152,6912]
    audit = run.seed_audit(b)
    assert audit['admitted']
    for p in ('development','protected'):
        for i in range(0,len(grid[p]),4):
            assert len({tuple(m['seeds']) for m in grid[p][i:i+4]}) == 1
    assert 'protected' not in run.schedules(b, True)
    assert bank.executor_check()['passed']


def test_diagnostic_vectors_cannot_change_extractor_or_worker_inputs():
    b = raw_bank()
    rows = canonical_rows(b, run.schedules(b,True)['source'])
    ordinary = order_library.build(rows,b['split']['source'],b['inputs'],cap=None,diagnostic_vectors={})
    reported = order_library.build(rows,b['split']['source'],b['inputs'],cap=None,diagnostic_vectors=run.helper_vectors(b['inputs']))
    assert ordinary['semantic'] == reported['semantic']
    assert sum(d['semantic']['included'] for d in reported['helper_diagnostics'].values()) == 24
    frozen = run.freeze(b)
    libs = empty_libraries(1)
    metas = run.schedules(b,True)['development'][:4]
    jobs = run.envelopes(metas,b,libs,frozen,'development',True)
    assert all(set(j[1]) == {'id','labels'} for j in jobs)
    assert jobs[0][-1] is None and jobs[1][-1] == [] and jobs[3][-1] == frozen['gates']
    assert jobs[2][-1] == [e['prefix'] for e in run.transport()['libraries.json'][0]['semantic_all']]
    changed = copy.deepcopy(b)
    for c in changed['screen']['cells']:
        c['helpers'],c['canonical_tree'] = ['ignored'],[]
    assert run.envelopes(metas,changed,libs,frozen,'development',True) == jobs
    with pytest.raises(ValueError,match='protected smoke'):
        run.envelopes(run.schedules(b)['protected'][:4],b,libs,frozen,'protected',True)
    with pytest.raises(ValueError,match='unapproved'):
        run.envelopes([metas[0] | dict(cell=b['split']['protected'][0])],b,libs,frozen,'development',True)


def test_two_way_pooled_arithmetic_bootstrap_and_boundary_rules():
    b = raw_bank()
    rows = canonical_rows(b,run.schedules(b)['protected'])
    result = run.summarize(rows,empty_libraries(24),b)
    denominator = 256 * (1 + np.arange(24)[:,None] + np.arange(18)[None,:])
    bi,ci = run.bootstrap_indices(24,18)
    draws = 512 / denominator[bi[:,:,None],ci[:,None,:]].mean((1,2))
    primary = result['contrasts']['R-all/R-tree']['evaluations']
    assert primary['point'] == pytest.approx(512/denominator.mean())
    assert primary['interval95'] == pytest.approx(np.quantile(draws,[.025,.975]))
    assert 'material_saving_recipe' in run.classify([.5,.7999])
    assert 'unresolved' in run.classify([.5,.80])
    assert 'material_saving_excluded' in run.classify([.80,.9])
    assert 'pooled_harm' in run.classify([1.01,1.2])
    assert 'material_saving_excluded' in run.classify([1,1.2])
    assert result['economics']['evaluations']['comparisons']['R-order_owned']['repayment_unbounded']
    with pytest.raises(ValueError,match='incomplete'):
        run.summarize(rows[:-1],empty_libraries(24),b)
    altered=copy.deepcopy(rows)
    altered[0]['seeds'][0] += 1
    with pytest.raises(ValueError,match='schedule'):
        run.summarize(altered,empty_libraries(24),b)


def test_source_replay_and_tampering_fail_closed(tmp_path):
    b=run.load_bank()
    frozen,schedule,audit=run.freeze(b),run.schedules(b,True),run.seed_audit(b)
    rows=run.validate_rows(canonical_rows(b,schedule['source']),schedule['source'],b)
    libs=run.libraries_from(rows,b,1)
    p=dict(admitted=True,smoke=True)
    for name,value in [('source_rows',rows),('libraries',libs),('bank',b),('freeze',frozen),('schedule',schedule),('audit',audit)]:
        p[name+'_hash']=digest(value)
    p['preparation_hash']=digest(p)
    for name,value in [('bank',b),('method_freeze',frozen),('libraries',libs),('schedules',schedule),('seed_audit',audit),('preparation',p)]:
        write_json(tmp_path,name+'.json',value)
    (tmp_path/'acquisition.jsonl').write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
    assert run.load_prepared(tmp_path,True)[2] == libs
    changed=copy.deepcopy(libs)
    changed[0]['semantic'].pop()
    write_json(tmp_path,'libraries.json',changed)
    with pytest.raises(ValueError,match='provenance'):
        run.load_prepared(tmp_path,True)
    (tmp_path/'failure.json').write_text('{}')
    with pytest.raises(ValueError,match='recorded failure'):
        run.load_prepared(tmp_path,True)
