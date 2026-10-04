"""Research invariants: arrival denominators, natural weighting and ancestry."""
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'experiments'/'chem_tape'))
import shared_arrival as sa
import shared_helper as sh
from folding_evolution.chem_tape import evolve
from folding_evolution.chem_tape.config import ChemTapeConfig
from folding_evolution.chem_tape.evaluate import evaluate_population


def cfg(**kw):
    base = dict(arm='TAG', alphabet='tagged', task='mbs_three', tag_combine='leftmost',
                tape_length=64, pop_size=32, elite_count=2, fast_rng=True, n_examples=64,
                selection_mode='lexicase', fitness_metric='balanced', tagged_crossover='v2',
                crossover_mate='self', crossover_rate=.3, mutation_rate=.015, seed=3)
    return ChemTapeConfig(**{**base, **kw})


@pytest.mark.parametrize('fast', [False, True])
def test_self_parent_rows_are_actual_and_recording_preserves_rng(fast):
    c = cfg(fast_rng=fast, crossover_rate=1)
    rng = evolve.make_rng(c)
    pop = evolve.build_initial_population(c, rng, c.pop_size)
    m = sa.Measurements(c)
    fits, cases = m.training(pop)
    rows = []
    a_rng, b_rng = evolve.make_rng(c), evolve.make_rng(c)
    a = evolve._reproduce_one_island(pop, fits, c, a_rng, cases=cases, lineage=rows)
    b = evolve._reproduce_one_island(pop, fits, c, b_rng, cases=cases)
    assert np.array_equal(a, b)
    assert a_rng.getstate() == b_rng.getstate()
    if fast:
        assert a_rng.np.bit_generator.state == b_rng.np.bit_generator.state
    assert all(p == q for p, q, kind, _ in rows if kind == 1)
    assert rows[:2] == [(int(i), -1, 0, 0) for i in np.argsort(-fits)[:2]]


def test_descendants_include_elites_both_parents_and_no_negative_index():
    flags = np.array([False, True, False])
    rows = [(1, -1, 0, 0), (0, 1, 1, 0), (0, -1, 2, 0), (2, 2, 1, 0)]
    assert sa.propagate(flags, rows).tolist() == [True, True, False, False]


def test_training_cache_matches_engine_and_full_form_classifier():
    c = cfg()
    rng = evolve.make_rng(c)
    pop = [sh.form_genome(n, 64) for n in ('shared', 'partly', 'duplicated')]
    pop += [evolve.random_genotype(c, rng) for _ in range(20)]
    pop += [pop[0].copy()]*4
    m = sa.Measurements(c)
    fits, cases = m.training(pop)
    actual, preds = evaluate_population(pop, m.task, c)
    assert np.array_equal(fits, actual)
    assert np.array_equal(cases, preds == m.task.labels)
    assert np.array_equal(m.training(pop)[0], actual)
    for g in pop[:3]:
        assert m.classify(g)[0] == sh.classify(g)['form']


def test_minimum_occupancy_and_descendant_share_denominator():
    c = cfg(pop_size=24)
    m = sa.Measurements(c)
    shared, partly = sh.form_genome('shared', 64), sh.form_genome('partly', 64)
    # Elite descendant included in survival, excluded from exact non-elite share.
    pop = [shared]*2+[shared]*10+[partly]*10
    flags = np.array([True, False]+[True]*10+[False]*10)
    row = m.population(pop, flags)
    assert row['exact_nonelite'] == 20
    assert row['descendant_established'] and row['descendant_shared_full'] == 11
    assert row['descendant_exact_shared_share'] == .5
    assert not m.population(pop[:21], flags[:21])['descendant_established']
    flags[:] = False
    row = m.population(pop, flags)
    assert row['total_established'] and not row['descendant_established']


def test_zero_bound_and_interval_censoring():
    assert .009 < sa.binomial_interval(0, 300)[1] < .013
    assert sa.binomial_interval(5, 100)[1] < .12
    tr = [dict(generation=1, alive=True), dict(generation=10, alive=True), dict(generation=20, alive=False)]
    assert sa.loss_interval(tr, 'alive') == dict(lower=10, upper=20, right_censored=False)
    assert sa.loss_interval(tr[:2], 'alive')['right_censored']


def test_historical_duration_preserves_first_form_and_bounds():
    c = cfg(generations=60, log_every=20)
    stats = [dict(gen=g, n_fully_exact=n, shared=s, partly=p, duplicated=0)
             for g, n, s, p in [(0, 0, None, None), (20, 30, 0, 1),
                               (40, 30, .47, .53), (60, 30, .98, .02)]]
    h = sa.historical_exposure(stats, c)
    assert h['first_form'] == 'partly' and h['duration'] == 40
    assert h['replacement_interval'] == [40, 60]
    assert h['duration_bounds'][0] <= 40 <= h['duration_bounds'][1]


def test_arrival_occurrences_weighted_by_source_exposure_not_layout(tmp_path):
    records, sources = [], []
    for sid, count, exposure, draws in [('a', 2, 100, 10), ('b', 1, 100, 20)]:
        path = tmp_path/'sources'/sid
        path.mkdir(parents=True)
        # Duplicate child layouts retain two independent occurrence rows.
        (path/'arrivals.jsonl').write_text(''.join(json.dumps(dict(source=sid, child_hex='same'))+'\n' for _ in range(count)))
        records.append(dict(source=sid, insertion_eligible=True, arrivals=count,
                            children=draws, historical_offspring_exposure=exposure))
        sources.append(dict(id=sid))
    candidates, weights = sa.insertion_candidates(records, sources, tmp_path)
    assert len(candidates) == 3
    assert weights.tolist() == [.4, .4, .2]


def test_continuation_task_seed_and_matched_control(tmp_path, monkeypatch):
    c = cfg(crossover_rate=0, mutation_rate=0)
    source = tmp_path/'source'
    source.mkdir()
    (tmp_path/'trials').mkdir()
    partly, shared = sh.form_genome('partly', 64), sh.form_genome('shared', 64)
    np.savez(source/'final_population.npz', genotypes=np.stack([partly]*c.pop_size))
    event = dict(child_hex=shared.tobytes().hex(), helper='A-only')
    original_training = sa.Measurements.training
    seeds = []
    def training(self, pop):
        seeds.append(self.task.name+':'+str(self.cfg.seed))
        return original_training(self, pop)
    monkeypatch.setattr(sa.Measurements, 'training', training)
    result = sa.continuation((dict(id='test', path=str(source), config=asdict(c)), event, 999, 20, str(tmp_path), 0))
    assert result['task_seed'] == 3 and result['continuation_seed'] == 999
    assert set(seeds) == {'mbs_three:3'}
    inserted = result['arms']['insert']['trajectory'][1]
    assert inserted['descendants_full'] == inserted['descendant_shared_full'] == 1
    assert all(row['total_shared_full'] == 0 for row in result['arms']['control']['trajectory'])
    assert json.loads((tmp_path/'trials'/'000.json').read_text()) == result


def test_replay_checks_census_history_and_final_population(tmp_path):
    c = cfg(generations=4, log_every=2, track_shared=True, track_runs=True,
            dump_final_population=True, disable_early_termination=True)
    r = evolve.run_evolution(c)
    source = tmp_path/'original'
    source.mkdir()
    (tmp_path/'sources'/'replay').mkdir(parents=True)
    r.stats.to_csv(source/'history.csv')
    np.savez(source/'final_population.npz', genotypes=r.final_population)
    (source/'result.json').write_text(json.dumps(dict(shared_stats=r.shared_stats, run_stats=r.run_stats)))
    desc = dict(id='replay', path=str(source), config=asdict(c), historical=dict(midpoint=2))
    check, mid = sa.replay(desc, 10, tmp_path)
    assert check['verified'] and mid.shape == (32, 128)
    # Same best genotype is insufficient: a census-only difference must reject.
    saved = json.loads((source/'result.json').read_text())
    saved['shared_stats'][0]['train_perfect'] += .1
    (source/'result.json').write_text(json.dumps(saved))
    check, mid = sa.replay(desc, 10, tmp_path)
    assert not check['verified'] and mid is None and check['reason'] == 'shared census mismatch'


def test_frozen_census_counts_all_children_and_excludes_shared_clones(tmp_path):
    c = cfg(crossover_rate=0, mutation_rate=0)
    source = tmp_path/'s'
    source.mkdir()
    h = dict(first_form='shared', duration=0, duration_known=True, duration_bounds=[0, 0])
    desc = dict(id='s', path=str(source), config=asdict(c), historical=h)
    np.savez(source/'final_population.npz', genotypes=np.stack([sh.form_genome('shared', 64)]*c.pop_size))
    f = sa.Frozen(desc, 42, 'final')
    events, rows = f.draw()
    assert events == [] and f.record['arrivals'] == 0
    assert f.record['children'] == c.pop_size-c.elite_count
    assert f.record['parent_strata']['shared']['children'] == 30
    assert sum(f.record['selected_parent_counts']) == 30
    assert all(x == 0 for x in rows[2])
    r = sa.finish_record(f.record, c)
    assert r['arrival_rate_all_offspring'] == 0
    assert sum(s['children'] for s in r['parent_strata'].values()) == 30


def test_missing_exposure_is_not_a_zero_arrival_estimate():
    r = dict(target=True, source='unknown', children=1000, arrivals=1,
             expected_arrivals=None, historical_offspring_exposure=0,
             insertion_eligible=True,
             historical=dict(duration_known=False, duration=0, duration_bounds=[0, 3000], replacement_interval=None))
    s = sa.exposure_summary([r])
    assert s['target_sources'] == 1
    assert s['expected_arrivals_per_run'] is None
    assert s['historical_exposure_unmeasured_sources'] == ['unknown']
    assert s['joint_rate_duration_envelope_per_run'][1] > 0
