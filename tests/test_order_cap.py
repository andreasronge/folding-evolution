"""Cap intervention, provenance and acquisition-unit inference boundaries."""

import copy

import numpy as np
import pytest

from experiments.chem_tape import order_cap_run as run, order_library
from experiments.chem_tape.order_bank import helper
from tests.test_order_probe import INPUTS, source_row


def corpus():
    prefixes = [(9,) + helper(kind, a, b).prefix + (3,)
                for kind in ('lo', 'hi') for a in range(4) for b in range(a + 1, 4)]
    prefixes += [(9, 9, a, b, 2) for a in range(4) for b in range(a, 4)]
    return [source_row(c, p, repeat=i) for c in ('a', 'b') for i, p in enumerate(prefixes)]


def test_complete_pool_exact_prefix_and_census_cannot_fit(monkeypatch):
    rows = corpus()
    capped = order_library.build(rows, ['a', 'b'], INPUTS)
    uncapped = order_library.build(rows, ['a', 'b'], INPUTS, cap=None)
    assert len(capped['semantic']) == 16 < len(uncapped['semantic'])
    assert len(uncapped['semantic']) == uncapped['eligible_semantic_classes']
    assert uncapped['semantic'][:16] == capped['semantic']
    monkeypatch.setattr(order_library, 'helpers', lambda inputs: {})
    blind = order_library.build(rows, ['a', 'b'], INPUTS, cap=None)
    assert blind['semantic'] == uncapped['semantic']
    assert not blind['helper_diagnostics']
    with pytest.raises(ValueError):
        order_library.build(rows, ['a', 'b'], INPUTS, cap=17)


def test_source_only_and_empty_acquisition_stays_charged():
    row = source_row('a', (), solved=False)
    bank = dict(split=dict(source=['a']), inputs=INPUTS)
    lib = run.libraries_from([row], bank, 1)[0]
    assert lib['semantic'] == lib['semantic_all'] == []
    assert lib['source_solves'] == 0 and lib['source_jobs'] == 1
    assert lib['acquisition_evaluations'] == 256
    with pytest.raises(ValueError, match='source R-tree'):
        order_library.build([row | dict(arm='R-all')], ['a'], INPUTS, cap=None)


def test_frozen_bank_schedules_seed_audit_and_protected_guard():
    bank = run.load_bank()
    schedule = run.schedules(bank)
    assert len(schedule['source']) == 1152 and len(schedule['score']) == 2304
    assert run.seed_audit(bank)['admitted']
    frozen = run.freeze(bank)
    for m in schedule['score'][:4]:
        assert m['seeds'] == schedule['score'][0]['seeds']
    libs = [dict(semantic=[], semantic_all=[]) for _ in range(24)]
    for arm in run.ARMS:
        meta = schedule['score'][0] | dict(arm=arm, cell=bank['split']['protected'][0])
        with pytest.raises(ValueError, match='protected'):
            run.envelopes([meta], bank, libs, frozen)
    altered = copy.deepcopy(bank)
    for cell in altered['screen']['cells']:
        cell['helpers'] = ['changed reporting identity']
    assert run.envelopes(schedule['score'][:4], bank, libs, frozen) == run.envelopes(schedule['score'][:4], altered, libs, frozen)


def report_fixture():
    bank = run.load_bank()
    rows = []
    for m in run.schedules(bank)['score']:
        # Builds have opposing ratios; pooled ratio is far from mean(build ratios).
        tree = 256 if m['build'] < 12 else 2560
        cost = tree if m['arm'] == 'R-tree' else 512
        rows.append(m | dict(evaluations=cost, worker_seconds=cost/1000, solved=True,
                             attempts=[dict(operator={})]))
    libs = [dict(semantic=[], semantic_all=[], source_jobs=48, source_solves=48,
                 acquisition_evaluations=10000, acquisition_worker_seconds=1,
                 all_helper_diagnostics={}, **{k: 0.01 for k in run.TIMINGS}) for _ in range(24)]
    return rows, libs, bank


def test_pooled_ratio_bootstrap_resamples_paired_whole_builds():
    rows, libs, bank = report_fixture()
    result = run.summarize(rows, libs, bank)
    ratio = result['contrasts']['R-all/R-tree']['evaluations']
    den = np.array([256]*12 + [2560]*12)
    selected = np.random.default_rng(run.BOOTSTRAP_SEED).integers(24, size=(run.DRAWS, 24))
    assert ratio['point'] == pytest.approx(512/den.mean())
    assert ratio['interval95'] == pytest.approx(np.quantile(512/den[selected].mean(1), [0.025, 0.975]))
    assert ratio['point'] != pytest.approx(np.mean(512/den))
    assert result['contrasts']['R-all/R-S']['evaluations']['interval95'] == [1, 1]
    with pytest.raises(ValueError, match='complete'):
        run.summarize(rows[:-1], libs, bank)
    bad = copy.deepcopy(rows)
    bad[0]['solved'] = False
    with pytest.raises(ValueError, match='full cap'):
        run.summarize(bad, libs, bank)


@pytest.mark.parametrize('interval, expected', [
    ([0.70, 0.78], 'end_recipe'), ([0.50, 0.79], 'useful_acquisition'),
    ([0.60, 0.85], 'unresolved'), ([0.67, 0.80], 'unresolved'),
])
def test_decision_precedence(interval, expected):
    assert run.classify(interval).startswith(expected)


def test_preparation_roundtrip_and_tampering_fail_closed(tmp_path):
    import json
    from experiments.chem_tape.comparison_gate_bank import digest
    from experiments.chem_tape.composition_run import write_json
    from experiments.chem_tape.tree_gp_search import Tree

    bank = run.load_bank()
    frozen, schedule, audit = run.freeze(bank), run.schedules(bank, True), run.seed_audit(bank)
    cells = {c['id']: c for c in bank['screen']['cells']}
    rows = []
    for meta in schedule['source']:
        tree = Tree(tuple(cells[meta['cell']]['canonical_tree']))
        rows.append(meta | dict(solved=True, evaluations=256, worker_seconds=0.1,
                                attempts=[dict(seed=meta['seeds'][0], evaluations=256, solved=True,
                                               solver_tree=list(tree.prefix), solver=list(tree.program))]))
    rows = run.base.validate_rows(rows, schedule['source'], bank)
    libs = run.libraries_from(rows, bank, 1)
    preparation = dict(admitted=True, smoke=True)
    for name, value in [('source_rows', rows), ('libraries', libs), ('bank', bank),
                        ('freeze', frozen), ('schedule', schedule), ('audit', audit)]:
        preparation[name + '_hash'] = digest(value)
    preparation['preparation_hash'] = digest(preparation)
    for name, value in [('bank', bank), ('method_freeze', frozen), ('libraries', libs),
                        ('schedules', schedule), ('seed_audit', audit), ('preparation', preparation)]:
        write_json(tmp_path, name + '.json', value)
    (tmp_path / 'acquisition.jsonl').write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    loaded = run.load_prepared(tmp_path, True)
    assert loaded[2] == libs
    changed = copy.deepcopy(libs)
    changed[0]['semantic_all'].pop()
    write_json(tmp_path, 'libraries.json', changed)
    with pytest.raises(ValueError, match='provenance'):
        run.load_prepared(tmp_path, True)
    write_json(tmp_path, 'failure.json', dict(admitted=False))
    with pytest.raises(ValueError, match='recorded failure'):
        run.load_prepared(tmp_path, True)
