"""Causal intervention, pairing, censoring, power and stopping-rule fidelity."""
from dataclasses import replace
import json
import time

import numpy as np
import pytest

from experiments.chem_tape import evolve_bias as eb
from experiments.chem_tape import evolve_shortcut_veto as sv
from folding_evolution.chem_tape.evolve import _reproduce_one_island, make_rng
from tests.test_evolve_bias import genome, planted


def spec():
    return json.loads(eb.SPEC_PATH.read_text())


def job(tmp_path, pop=4, cap=16):
    j = sv.jobs_for(spec(), tmp_path, "smoke", 1, time.monotonic() + 30)[0]
    return {**j, "pop": pop, "cap": cap}


def record(seed=0, times=(100, 100, 60, 60), exposed=(True, True)):
    cells = {}
    for i, cell in enumerate(sv.CELLS):
        cells[cell] = dict(seed=seed, cell=cell, cap=sv.CAP, time=times[i],
            event=True, complete=True, max_before_solve=exposed[i // 2], reproductive_exposure=exposed[i // 2],
            seconds=1., processed_candidates=sv.CAP, fully_vetoed=False,
            peak_veto_fraction=.1, first_training_100=2, history=[], solver_parents=None)
    return dict(seed=seed, cells=cells, identity=[dict(passed=True)] * 2)


def estimate(lo, hi, finite=1.):
    return dict(ratio=(lo + hi) / 2, lower=lo, upper=hi, finite_fraction=finite)


def test_sampler_and_frozen_vectors():
    audit = sv.sampler_audit()
    assert all(a["balance"] == .5 and a["proxy_train_accuracy"] == 1 for a in audit)
    j = sv.jobs_for(spec(), __import__('pathlib').Path('/tmp'), 'pilot', 50, 999.)
    assert len(j) == 50
    assert {k["master"] for k in j} == {sv.PILOT_MASTER}
    assert sv.PILOT_MASTER != sv.MASTER != sv.SMOKE_MASTER
    assert sv.training_indices(j[0]["seed"], j[0]["master"]).tolist() != sv.training_indices(j[0]["seed"]).tolist()
    assert all(k['pop'] == 1024 and k['cap'] == 262144 for k in j)
    assert sv.training_indices(j[0]['seed']).tolist() != sv.training_indices(j[1]['seed']).tolist()
    for arm in ('U', 'R'):
        cfg = eb.config('sum2', arm, j[0]['seed'], sv.POP, sv.CAP, j[0]['vectors'][arm], sv.MASTER)
        assert cfg.crossover_mate == 'selected' and cfg.generations == 255
        assert cfg.mutation_rate == .015 and cfg.tagged_crossover == 'v2'


def test_full_classification_cache_solver_priority_and_other_counts():
    population = [planted('max2'), planted('sum2'), planted('max2'), genome([20, 3])]
    cases = np.ones((4, 64), bool)
    cache, examples = {}, {}
    classes, pos, checks = sv.classify(population, cases, cache, examples)
    assert classes.tolist() == [2, 1, 2, 0] and pos == 1 and checks == 3
    assert len(examples) == 1 and next(iter(examples.values()))['max_agreement'] < 1
    assert sv.classify(population, cases, cache, examples)[2] == 0


@pytest.mark.parametrize('fast', [True, False])
@pytest.mark.parametrize('mode', ['lexicase', 'tournament', 'ranking', 'truncation'])
@pytest.mark.parametrize('eligible', [[False, True, False, False], [False, True, True, False]])
def test_explicit_eligibility_both_parents_elites_and_all_fail(mode, fast, eligible):
    cfg = eb.config('sum2', 'U', 12, 4, 8, [1 / 22] * 22, sv.MASTER)
    cfg = replace(cfg, fast_rng=fast, selection_mode=mode)
    population = [planted('max2'), genome([0]), genome([20, 3]), planted('max2')]
    cases = np.zeros((4, 64), bool)
    cases[[0, 3]] = True  # vetoed rows dominate raw fitness; eligible rows all fail
    fits = cases.mean(axis=1)
    lineage = []
    children = _reproduce_one_island(population, fits, cfg, make_rng(cfg), cases=cases,
                                    lineage=lineage, eligible=np.array(eligible))
    assert len(children) == len(lineage) == 4
    assert all(eligible[i] and (j < 0 or eligible[j]) for i, j, _, _ in lineage)
    assert sum(kind == 0 for _, _, kind, _ in lineage) == min(2, sum(eligible))


@pytest.mark.parametrize('fast', [True, False])
def test_all_true_mask_exactly_preserves_rng_and_no_mask_path(fast):
    cfg = eb.config('sum2', 'U', 11, 4, 8, [1 / 22] * 22, sv.MASTER)
    cfg = replace(cfg, fast_rng=fast)
    population = [genome([0]), genome([20, 3]), planted('sum2'), planted('max2')]
    cases = np.array([[False] * 64, [True] * 32 + [False] * 32, [True] * 64, [True] * 64])
    fits = cases.mean(axis=1)
    a_rng, b_rng = make_rng(cfg), make_rng(cfg)
    a_line, b_line = [], []
    a = _reproduce_one_island(population, fits, cfg, a_rng, cases=cases, lineage=a_line)
    b = _reproduce_one_island(population, fits, cfg, b_rng, cases=cases, lineage=b_line,
                              eligible=np.ones(4, bool))
    assert np.array_equal(a, b) and a_line == b_line
    assert a_rng.random() == b_rng.random()
    with pytest.raises(ValueError, match='no eligible'):
        _reproduce_one_island(population, fits, cfg, a_rng, cases=cases, eligible=np.zeros(4, bool))


def test_all_vetoed_and_solver_never_vetoed(tmp_path):
    j = job(tmp_path)
    r = sv.run_one(j, 'R-veto', [planted('max2')] * 4)
    assert r['complete'] and not r['event'] and r['time'] == 16 and r['fully_vetoed']
    assert r['first_max_gen'] == 0 and r['max_before_solve']
    r = sv.run_one(j, 'R-veto', [planted('max2'), planted('sum2'), planted('max2'), planted('max2')])
    assert r['event'] and r['time'] == 2 and r['solver_parents'] is None
    assert not r['fully_vetoed']
    assert r['max_before_solve'] and not r['reproductive_exposure']


def test_immediate_parent_diagnostic_uses_previous_classes(tmp_path, monkeypatch):
    j = job(tmp_path)
    def reproduce(*args, lineage, **kwargs):
        lineage.extend([(0, 1, 1, 1)] * 4)
        return [planted('sum2')] * 4
    monkeypatch.setattr(sv, '_reproduce_one_island', reproduce)
    r = sv.run_one(j, 'R-ord', [planted('max2'), genome([0]), genome([0]), genome([0])])
    assert r['time'] == 5 and r['solver_parents']['exact_max'] == [True, False]


def test_identity_until_exposure_and_no_exposure_endpoints(tmp_path):
    j = job(tmp_path)
    a = sv.run_one(j, 'U-ord', [genome([0])] * 4)
    b = sv.run_one(j, 'U-veto', [genome([0])] * 4)
    assert sv.check_identity(a, b)['passed']
    b['population_digests'][0] = 'broken'
    with pytest.raises(RuntimeError, match='identity failure'):
        sv.check_identity(a, b)
    a['first_max_gen'] = 0
    b['population_digests'][0] = a['population_digests'][0]
    assert sv.check_identity(a, b)['verified_generations'] == 1


def test_incomplete_is_missingness_not_censoring(tmp_path):
    j = job(tmp_path)
    j['deadline'] = time.monotonic() - 1
    r = sv.run_one(j, 'U-veto')
    assert not r['complete'] and r['time'] is None and not r['event']
    rows = [record()]
    rows[0]['cells']['U-veto']['complete'] = False
    with pytest.raises(ValueError, match='incomplete'):
        sv.comparisons(rows, 100)


def test_whole_seed_interaction_and_censored_envelope():
    # Perfect correlation between all cells makes interaction exactly 2,
    # independent of bootstrap index draws, which must be shared by all cells.
    rows = [record(i, (100 + i, 200 + 2*i, 50 + i/2, 200 + 2*i)) for i in range(40)]
    c = sv.comparisons(rows, 1000)
    assert c['I']['ratio'] == c['I']['lower'] == c['I']['upper'] == 2
    assert c['P_U']['ratio'] == 2 and c['P_R']['ratio'] == 4
    for row in rows[:21]:
        row['cells']['R-veto'].update(event=False, time=sv.CAP)
    c = sv.comparisons(rows, 1000)
    assert c['P_R']['ratio'] is None and c['I']['upper'] is None
    assert c['P_R']['finite_fraction'] < .99
    rows[0]['cells']['U-ord']['cap'] -= 1
    with pytest.raises(ValueError, match='different administrative'):
        sv.comparisons(rows, 100)


def test_exclusive_outcomes_and_strict_boundaries():
    c = dict(C1=estimate(1.2, 2), P_R=estimate(.5, .99), P_U=estimate(1, 1), I=estimate(1.2, 2))
    assert sv.outcome(c) == 'exact shortcut trap'
    c['P_R'] = estimate(1.01, 1.249)
    assert 'detectable but small' in sv.outcome(c)
    c['P_R'] = estimate(1.01, 1.25)
    assert sv.outcome(c) == 'route supported'
    c['I'] = estimate(1, 2)
    assert 'R advantage unresolved' in sv.outcome(c)
    c['P_R'] = estimate(.9, 1.25)
    assert sv.outcome(c) == 'unresolved'
    c['C1'] = estimate(1, 2)
    assert sv.outcome(c).startswith('gate failed')
    c['C1'] = estimate(1.2, 2, .98)
    assert sv.outcome(c).startswith('gate failed')


def test_injection_preserves_unexposed_and_censors_events():
    rows = [record(i, (100 + i, 130 + i, 60 + i, 80 + i), (i < 40, i < 40)) for i in range(50)]
    # Empirical unexposed pairs must actually be identical.
    for r in rows[40:]:
        r['cells']['U-veto']['time'] = r['cells']['U-ord']['time']
        r['cells']['R-veto']['time'] = r['cells']['R-ord']['time']
    v, mask = sv.values(rows), sv.exposure_mask(rows)
    injected, info = sv.inject(v, mask, 1.6)
    assert injected is not None
    assert info['achieved']['P_R'] == pytest.approx(1.6)
    assert np.array_equal(injected[40:], v[40:])
    assert np.array_equal(injected[:, [0, 2]], v[:, [0, 2]])
    assert sv.inject(v, np.zeros((50, 2), bool), 1.6)[0] is None
    v[0, 3] = np.inf
    injected, _ = sv.inject(v, mask, 1.6)
    assert np.isinf(injected[0, 3])


def test_runtime_gate_and_no_downsizing():
    rows = [record(i) for i in range(50)]
    powered = dict(n=800, feasible=True, reason=None)
    assert sv.runtime_design(rows, powered, 3000, 4)['feasible']
    d = sv.runtime_design(rows, powered, 1, 4)
    assert not d['feasible'] and d['n'] == 800
    assert not sv.runtime_design(rows, dict(n=None, feasible=False), 100000, 4)['feasible']


@pytest.mark.parametrize('feasible,incomplete', [(True, False), (False, False), (True, True)])
def test_orchestration_separate_pilot_and_main_one_look(tmp_path, monkeypatch, feasible, incomplete):
    monkeypatch.setenv('RUN_DIR', str(tmp_path))
    monkeypatch.setattr('sys.argv', ['veto', '--seconds', '10500'])
    calls = []
    def fake_jobs(jobs, workers, out):
        calls.append(jobs)
        rows = [record(j['seed']) for j in jobs]
        if incomplete and jobs[0]['phase'] == 'main':
            rows[0]['cells']['U-veto']['complete'] = False
        return rows
    monkeypatch.setattr(sv, 'run_jobs', fake_jobs)
    monkeypatch.setattr(sv, 'power', lambda *a: dict(n=600 if feasible else None, feasible=feasible))
    monkeypatch.setattr(sv, 'plot_results', lambda *a: None)
    monkeypatch.setattr(sv, 'comparisons', lambda rows: {k: {**estimate(1, 1), 'n': len(rows)} for k in ('C1', 'P_R', 'P_U', 'I')})
    assert sv.main() == int(incomplete)
    assert len(calls[0]) == 50 and calls[0][0]['phase'] == 'pilot'
    if feasible:
        assert len(calls[1]) == 600 and calls[1][0]['phase'] == 'main'
        assert {j['seed'] for j in calls[0]}.isdisjoint(j['seed'] for j in calls[1])
    else:
        assert len(calls) == 1
    result = json.loads((tmp_path / 'result.json').read_text())
    assert (tmp_path / 'COMPLETE').exists() == (not incomplete)
    assert bool(result['comparisons']) == (feasible and not incomplete)


def test_power_gate_reports_joint_and_uses_smallest_passing_size(tmp_path, monkeypatch):
    rows = [record(i) for i in range(50)]
    def fake_bootstrap(v, seed, boot):
        alt = sv.ratios(sv.median_values(v))[1] > 1.3
        return dict(C1=estimate(1.1, 2), P_R=estimate(1.1, 2) if alt else estimate(.9, 1.1),
                    I=estimate(1.1, 2), P_U=estimate(.9, 1.1))
    monkeypatch.setattr(sv, 'bootstrap', fake_bootstrap)
    result = sv.power(rows, tmp_path, time.monotonic() + 30, trials=3, boot=10)
    assert result['feasible'] and result['n'] == 600
    assert result['sizes']['600']['complete_route']['p'] == 1
    assert set(result['sizes']) == {'600'}


def test_exposed_real_pair_excludes_shortcut_from_reproduction(tmp_path):
    j = job(tmp_path, pop=64, cap=1024)
    initial = [planted('max2')] + [genome([0])] * 63
    a = sv.run_one(j, 'R-ord', initial)
    b = sv.run_one(j, 'R-veto', initial)
    assert a['complete'] and b['complete'] and a['first_max_gen'] == b['first_max_gen'] == 0
    assert sv.check_identity(a, b)['verified_generations'] == 1
    # In the absence of max2 parents, generation-one perfect max phenotypes
    # can arise only through variation of the eligible constant population.
    assert b['history'][1]['exact_max'] == 0
    assert a['population_digests'][1] != b['population_digests'][1]


def test_identity_failure_cancels_queued_seed_jobs(tmp_path, monkeypatch):
    from concurrent.futures import Future
    broken, pending = Future(), Future()
    broken.set_exception(RuntimeError('identity failure'))
    class Pool:
        def __init__(self, **kwargs):
            self.futures = iter([broken, pending])
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def submit(self, *args):
            return next(self.futures)
    monkeypatch.setattr(sv, 'ProcessPoolExecutor', Pool)
    monkeypatch.setattr(sv, 'as_completed', lambda futures: iter(futures))
    with pytest.raises(RuntimeError, match='identity failure'):
        sv.run_jobs([{}, {}], 1, tmp_path)
    assert pending.cancelled()
