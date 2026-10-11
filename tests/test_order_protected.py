"""Protected roster, balanced timeout inference and seed-paired build uncertainty."""
import copy
import json
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.chem_tape import order_protected_run as run
from experiments.chem_tape.tree_gp_search import Tree


@pytest.fixture(scope='module')
def fixture():
    bank = run.saved.load_bank()
    cells = {c['id']: c for c in bank['screen']['cells']}
    rows = []
    for m in run.schedules(bank):
        tree = Tree(tuple(cells[m['cell']]['canonical_tree']))
        cost = (256 if m['build'] < 12 else 2560) if m['arm'] == 'R-tree' else 512
        rows.append(m | dict(solved=True, evaluations=cost, worker_seconds=cost/1000,
                             cap=run.CAP, cutoff=65536, pop_size=256,
                             attempts=[dict(seed=m['seeds'][0], evaluations=cost, solved=True,
                                            solver_tree=list(tree.prefix), solver=list(tree.program), operator={})]))
    libs = [dict(semantic_all=[], source_jobs=48, source_solves=48,
                 acquisition_evaluations=10000, acquisition_worker_seconds=1,
                 all_helper_diagnostics={}, **{k: 0.01 for k in run.saved.TIMINGS}) for _ in range(24)]
    return bank, rows, libs


def test_roster_pairing_and_reporting_does_not_choose_donors(fixture):
    bank, rows, libs = fixture
    metas = run.schedules(bank)
    assert len(metas) == 3456
    assert len(run.schedules(bank, True)) == 36
    assert set(m['cell'] for m in metas) == set(bank['split']['protected'])
    assert all(m['repeat'] == 0 for m in metas[:1728])
    assert all(m['repeat'] == 1 for m in metas[1728:])
    for offset in range(0, len(metas), 3):
        assert len({tuple(m['seeds']) for m in metas[offset:offset+3]}) == 1
    assert len({tuple(m['seeds']) for m in metas}) == 1152
    frozen = dict(order=[[0]], cutoff=65536)
    jobs = run.envelopes(metas[:3], bank, libs, frozen)
    assert set(jobs[0][1]) == {'id', 'labels'}
    changed = copy.deepcopy(bank)
    for c in changed['screen']['cells']:
        c['helpers'] = ['irrelevant']
        c['disjoint'] = not c.get('disjoint', False)
    assert jobs == run.envelopes(metas[:3], changed, libs, frozen)
    with pytest.raises(ValueError, match='unapproved'):
        run.envelopes([metas[0] | dict(cell=bank['split']['development'][0])], bank, libs, frozen)
    with pytest.raises(ValueError, match='unapproved'):
        run.envelopes(metas[:1], bank, libs, frozen, smoke=True)


def test_bootstrap_pooled_builds_and_balanced_fallback(fixture):
    bank, rows, libs = fixture
    result = run.summarize(rows, libs, bank)
    den = np.array([256]*12 + [2560]*12)
    selected = np.random.default_rng(run.BOOTSTRAP_SEED).integers(24, size=(run.DRAWS, 24))
    estimate = result['contrasts']['R-all/R-tree']['evaluations']
    assert estimate['point'] == pytest.approx(512/den.mean())
    assert estimate['interval95'] == pytest.approx(np.quantile(512/den[selected].mean(1), [.025, .975]))
    assert estimate['point'] != pytest.approx(np.mean(512/den))
    assert result['reliability']['allowance'] == 12
    assert result['strata_descriptive']['disjoint']['paired_units'] == 192
    assert result['strata_descriptive']['overlapping']['paired_units'] == 960
    first_plus_partial = rows[:1730]
    fallback = run.summarize(first_plus_partial, libs, bank)
    assert fallback['analyzed_repeats'] == 1 and not fallback['complete']
    assert fallback['ignored_partial_jobs'] == 2 and fallback['paired_units'] == 576
    assert fallback['reliability']['allowance'] == 6
    assert fallback['contrasts'] == result['contrasts']  # identical synthetic repeats
    incomplete = run.summarize(rows[:1727], libs, bank)
    assert incomplete['decision'] == 'incomplete_no_efficacy_verdict'
    assert 'contrasts' not in incomplete


def test_partial_rows_cannot_hide_errors(fixture):
    bank, rows, _ = fixture
    for bad in (rows[:1] * 2, [rows[0] | dict(cell='unknown')],
                [rows[0] | dict(seeds=[1]*8)], [rows[0] | dict(cap=100)],
                [rows[0] | dict(worker_seconds=float('nan'))]):
        with pytest.raises(ValueError):
            run.balanced_rows(bad, bank)
    bad = copy.deepcopy(rows[0])
    bad.update(solved=False, evaluations=2048)
    bad['attempts'] = [dict(seed=s, evaluations=256, solved=False) for s in bad['seeds']]
    with pytest.raises(ValueError, match='capped'):
        run.balanced_rows([bad], bank)
    with pytest.raises(ValueError, match='repeat one'):
        run.balanced_rows([rows[1728]], bank)


@pytest.mark.parametrize('interval, extra, units, prefix', [
    ([.70, .78], 0, 1152, 'end_expansion'),
    ([.50, .79], 12, 1152, 'useful'), ([.50, .79], 13, 1152, 'unresolved'),
    ([.50, .79], 6, 576, 'useful'), ([.50, .79], 7, 576, 'unresolved'),
    ([.60, .85], 0, 1152, 'unresolved'), ([.67, .80], 0, 1152, 'unresolved'),
])
def test_decision_precedence_and_reliability(interval, extra, units, prefix):
    assert run.classify(interval, extra, units).startswith(prefix)


def test_repeat_barrier_durable_rows_and_timeout(fixture, monkeypatch, tmp_path):
    bank, rows, libs = fixture
    called, fsynced = [], []
    by = {(r['build'], r['cell'], r['repeat'], r['arm']): r for r in rows}
    class Pool:
        def close(self):
            pass
        def terminate(self):
            pass
        def join(self):
            pass
    monkeypatch.setattr(run.mp, 'get_context', lambda _: SimpleNamespace(Pool=lambda workers: Pool()))
    monkeypatch.setattr(run.os, 'fsync', lambda fd: fsynced.append(fd))
    def fake_jobs(pool, execute, jobs, deadline, callback):
        repeat = jobs[0][0]['repeat']
        assert all(j[0]['repeat'] == repeat for j in jobs)
        if repeat == 1:
            marker = json.loads((tmp_path / 'score_completion.json').read_text())
            assert marker['completed_repeats'] == [0] and marker['rows'] == 1728
            assert len(fsynced) == 1728
        called.append(repeat)
        for m, *_ in jobs[:(2 if repeat else len(jobs))]:
            callback(by[m['build'], m['cell'], m['repeat'], m['arm']])
        return repeat == 0
    monkeypatch.setattr(run, 'run_jobs', fake_jobs)
    actual, completed, _ = run.run_blocks(tmp_path, 'score.jsonl', bank, libs,
                                          dict(order=[[0]], cutoff=65536), 10, float('inf'))
    assert called == [0, 1] and completed == [0] and len(actual) == 1730
    assert len(fsynced) == len(actual)
    assert len((tmp_path / 'score.jsonl').read_text().splitlines()) == len(actual)
    chosen, repeats = run.balanced_rows(actual, bank)
    assert repeats == 1 and len(chosen) == 1728
