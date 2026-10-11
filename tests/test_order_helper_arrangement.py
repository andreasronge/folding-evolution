"""Entry-local matching, support failure, complete-grid inference and pairing."""

import copy
import hashlib
import itertools

import numpy as np
import pytest

from experiments.chem_tape import order_helper_arrangement as construction
from experiments.chem_tape import order_helper_run as run
from experiments.chem_tape.tree_gp_search import Tree
from experiments.chem_tape.tree_permutation import signature


@pytest.fixture(scope='module')
def semantics():
    return construction.Semantics(list(itertools.product(range(-2, 3), repeat=4)))


def entry(prefix, semantics):
    t = Tree(tuple(prefix))
    return dict(prefix=list(prefix), nodes=len(prefix), compiled_length=len(t.program),
                semantic_hash=hashlib.sha256(semantics.vector(prefix)).hexdigest(),
                sentinel_metadata={'preserved': True})


def test_entry_material_slots_nonhelpers_and_replay(semantics):
    lo = entry([11, 0, 1, 10, 0, 1], semantics)
    plain = entry([9, 2, 3], semantics)
    original = [dict(semantic_all=[lo, plain, lo])]
    libs, audit = construction.build(original, semantics.inputs)
    assert audit['helpers_per_build'] == [2]
    assert len(libs[0]['constructions']) == 4
    for form in libs[0]['constructions']:
        entries = form['entries']
        assert len(entries) == 3 and entries[1] == plain
        for before, after in zip(original[0]['semantic_all'], entries):
            assert signature([before]) == signature([after])
            assert not semantics.census(after['prefix'])
        # Same slot's replay is fixed; two original duplicates keep two draws.
        for slot in (0, 2):
            s = construction.seed('construction', 0, form['realization'], slot)
            assert entries[slot] == construction.replace(lo, s, semantics)[0]
    assert libs == construction.build(original, semantics.inputs)[0]
    assert original[0]['semantic_all'] == [lo, plain, lo]


def test_support_and_embedded_helpers_fail_closed(semantics, monkeypatch):
    lo = entry([11, 0, 1, 10, 0, 1], semantics)
    with pytest.raises(ValueError, match='exhausted'):
        construction.replace(lo, 1, semantics, max_draws=0)
    calls = []
    class Unsupported:
        def census(self, prefix):
            calls.append(prefix)
            return [{'helper': 'always'}]
    with pytest.raises(ValueError, match='exhausted 3 draws'):
        construction.replace(lo, 1, Unsupported(), max_draws=3)
    assert len(calls) == 3
    embedded = entry([9, 11, 0, 1, 10, 0, 1, 6], semantics)
    with pytest.raises(ValueError, match='embedded helper'):
        construction.build([dict(semantic_all=[embedded])], semantics.inputs)
    changed = copy.deepcopy(lo)
    changed['semantic_hash'] = 'changed'
    with pytest.raises(ValueError, match='semantic hash'):
        construction.build([dict(semantic_all=[changed])], semantics.inputs)


@pytest.fixture(scope='module')
def fixture():
    bank = run.saved.load_bank()
    by = {c['id']: c for c in bank['screen']['cells']}
    rows = []
    for m in run.schedules(bank):
        t = Tree(tuple(by[m['cell']]['canonical_tree']))
        cost = ((256 if m['build'] < 12 else 2560) if m['arm'] == 'R-all'
                else 512 if m['arm'] == 'R-hx' else 5120)
        rows.append(m | dict(solved=True, evaluations=cost, worker_seconds=cost/1000,
                             cap=run.CAP, cutoff=65536, pop_size=256,
                             attempts=[dict(seed=m['seeds'][0], evaluations=cost, solved=True,
                                            cap=65536, pop_size=256, crossover=0.5,
                                            initial_tokens_hash='paired', training_indices=[0],
                                            solver_tree=list(t.prefix), solver=list(t.program))]))
    values = dict(bank=bank, coverage=[dict(build=b, cell=c, needed_helpers_present=b % 3)
                                      for b in range(24) for c in bank['split']['development']],
                  method_freeze=dict(bootstrap=dict(seed=construction.seed('bootstrap'), draws=run.DRAWS)))
    return rows, values


def test_grid_pairing_realizations_and_protected_exclusion(fixture):
    _, values = fixture
    metas = run.schedules(values['bank'])
    assert len(metas) == 3456
    assert len(run.schedules(values['bank'], True)) == 72
    assert len({tuple(m['seeds']) for m in metas}) == 1152
    assert not set(m['cell'] for m in metas) & set(values['bank']['split']['protected'])
    for start in range(0, len(metas), 3):
        assert len({tuple(m['seeds']) for m in metas[start:start+3]}) == 1
    assert all(m['realization'] == m['repeat'] % 4 for m in metas)
    libs = [dict(entries=[dict(prefix=[0])], constructions=[dict(entries=[dict(prefix=[1])])]*4)]*24
    v = values | dict(libraries=libs)
    jobs = run.envelopes(metas[:3], v)
    assert jobs[0][-1] is None and jobs[1][-1] == [[0]] and jobs[2][-1] == [[1]]
    assert set(jobs[0][1]) == {'id', 'labels'}
    for field, val in [('cell', values['bank']['split']['protected'][0]), ('realization', 9), ('seeds', [1]*8)]:
        with pytest.raises(ValueError, match='unapproved'):
            run.envelopes([metas[0] | {field: val}], v)


def test_pooled_whole_build_bootstrap_and_no_partial_verdict(fixture):
    rows, values = fixture
    result = run.summarize(rows, values)
    den = np.array([256]*12 + [2560]*12)
    selected = np.random.default_rng(construction.seed('bootstrap')).integers(24, size=(run.DRAWS, 24))
    estimate = result['contrasts']['R-hx/R-all']
    assert estimate['point'] == pytest.approx(512/den.mean())
    assert estimate['interval95'] == pytest.approx(np.quantile(512/den[selected].mean(1), [.025, .975]))
    assert estimate['point'] != pytest.approx(np.mean(512/den))
    assert result['rediscovery']['fraction'] == 1
    for partial in (rows[:-1], rows[:432], rows[::3]):
        report = run.summarize(partial, values)
        assert report['decision'] == 'incomplete_no_efficacy_verdict'
        assert 'contrasts' not in report
    for bad in (rows[:1]*2, [rows[0] | dict(realization=9)]):
        with pytest.raises(ValueError):
            run.summarize(bad, values)
    bad = copy.deepcopy(rows[:3])
    bad[1]['attempts'][0]['initial_tokens_hash'] = 'unpaired'
    with pytest.raises(ValueError, match='pairing'):
        run.summarize(bad, values)


def test_method_freeze_detects_late_artifact_changes(tmp_path, monkeypatch):
    # The expensive semantic reconstruction is covered by the CLI smoke.
    # Exercise the loader's hash gates without another acquisition replay.
    rows, values = [], {name: {'frozen': name} for name in run.ARTIFACTS}
    values['bank'] = {'split': {'development': []}}
    from experiments.chem_tape.composition_run import write_json
    from experiments.chem_tape.comparison_gate_bank import digest
    monkeypatch.setattr(run, 'load_source', lambda _: (values['bank'], None, None, None))
    monkeypatch.setattr(run, 'make_values', lambda *args: values)
    monkeypatch.setattr(run, 'validate_partial', lambda *args: rows)
    p = dict(admitted=True, task=run.TASK, source_preparation_hash=run.SOURCE_PREPARATION_HASH,
             artifact_hashes={k: digest(v) for k, v in values.items()}, smoke_rows_hash=digest(rows))
    p['preparation_hash'] = digest(p)
    write_json(tmp_path, 'preparation.json', p)
    for k, v in values.items():
        write_json(tmp_path, k + '.json', v)
    (tmp_path / 'smoke.jsonl').write_text('')
    assert run.load_prepared(tmp_path)[0] == values
    write_json(tmp_path, 'libraries.json', {'tampered': True})
    with pytest.raises(ValueError, match='frozen artifact changed: libraries'):
        run.load_prepared(tmp_path)


@pytest.mark.parametrize('q, tree, outcome', [
    ([1.26, 1.8], [.5, .9], 'material_loss'),
    ([1.0, 1.24], [.5, .79], 'useful_retention'),
    ([1.0, 1.25], [.5, .79], 'unresolved'),
    ([1.25, 1.8], [.5, .9], 'unresolved'),
    ([1.0, 1.24], [.5, .80], 'unresolved'),
])
def test_registered_outcomes(q, tree, outcome):
    assert run.classify(q, tree).startswith(outcome)
