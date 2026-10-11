"""1736: recurrent modifier bookkeeping and paired individual deployment."""
import importlib.util
import subprocess
import sys

import numpy as np
import pytest

from experiments.chem_tape import recurrent_library_run as run
from experiments.chem_tape.tree_gp_search import Tree, search
from tests.test_inherited_library import comparable


@pytest.fixture
def job():
    bank = run.old.saved.load_bank()
    c = bank['split']['development'][0]
    return (dict(id=c, labels=[123456]*len(bank['inputs'])), 17360001, 8192, 256, bank['inputs'], 0.5)


def test_zero_mutation_replays_1427_exactly(job, tmp_path):
    path = tmp_path/'original.py'
    path.write_bytes(subprocess.check_output(['git', 'show', 'f8f4246:experiments/chem_tape/tree_gp_search.py']))
    spec = importlib.util.spec_from_file_location('original_recurrent_test', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    for arm in ('L', 'S', 'N'):
        kwargs = dict(modifier_bits=[1]*64+[0]*192, modifier_seed=777, shuffle_modifiers=arm == 'S', continue_after_solve=True)
        donors = None if arm == 'N' else [Tree((11, 0, 1, 10, 0, 1))]
        old_donors = None if donors is None else [module.Tree(t.prefix) for t in donors]
        a = search(job, donor_library=donors, modifier_mutation_probability=0, **kwargs)
        b = module.search(job, donor_library=old_donors, **kwargs)
        assert comparable(a) == comparable(b)
        assert a['modifier_bits'] == b['modifier_bits']
        assert a['modifier_trace'] == b['modifier_trace']


@pytest.mark.parametrize('shuffle', [False, True])
@pytest.mark.parametrize('redraw_state', [0, 1])
def test_mutated_child_alignment_including_elites_and_rejection(job, shuffle, redraw_state):
    children, generations = [], []
    def observe(event):
        if 'elites' in event:
            old = event['old_bits']
            assert all(c['inherited_state'] == old[c['recipient']] for c in children)
            assert all(c['modifier_redrawn'] and c['state'] == redraw_state for c in children)
            assert event['next_bits'] == [old[i] for i in event['elites']] + [c['state'] for c in children]
            assert any(c['inherited_state'] != redraw_state and c['state'] == redraw_state for c in children) or len(generations) > 0
            generations.append((event, list(children)))
            children.clear()
        else:
            if event['rejected']:
                assert event['child'] is event['parent']
            children.append(event)
    result = search(job, donor_library=[Tree((11, 0, 1, 10, 0, 1))],
                    modifier_bits=[1]*16+[0]*240, modifier_seed=321,
                    modifier_mutation_probability=1, modifier_redraw_probability=redraw_state,
                    shuffle_modifiers=shuffle, lineage_observer=observe, continue_after_solve=True)
    assert len(generations) == 31
    assert any(c['rejected'] for _, cc in generations for c in cc)
    for t, (event, cc) in zip(result['modifier_trace'], generations):
        assert t['pre_mutation_f'] == np.mean([c['inherited_state'] for c in cc])
        assert t['post_mutation_f'] == redraw_state
        assert t['elite_bits'] == [event['old_bits'][i] for i in event['elites']]
        assert t['modifier_transitions'][1-redraw_state][redraw_state] == sum(c['inherited_state'] != redraw_state for c in cc)
        assert t['counters'][1-redraw_state]['recipients'] == 0
        assert (t['counters'][1]['library_draws'] > 0) == bool(redraw_state)
    assert result['modifier_bits'] == generations[-1][0]['next_bits']


def test_neutral_transition_rates_and_independent_program_stream(job):
    longer = (job[0], job[1], 65536, *job[3:])
    ordinary = search(longer, continue_after_solve=True)
    for shuffle in (False, True):
        neutral = search(longer, modifier_bits=[1]*16+[0]*240, modifier_seed=997,
            shuffle_modifiers=shuffle, modifier_mutation_probability=run.MUTATION,
            modifier_redraw_probability=run.INITIAL_F, continue_after_solve=True)
        assert comparable(neutral) == comparable(ordinary)
        transitions = np.sum([t['modifier_transitions'] for t in neutral['modifier_trace'] if t['counters'] is not None], axis=0)
        for state, expected in ((0, 1/512), (1, 15/512)):
            n = transitions[state].sum()
            assert n > 500
            count = transitions[state, 1-state]
            assert abs(count-n*expected) < 6*np.sqrt(n*expected*(1-expected))
        assert sum(t['modifier_redraws'] for t in neutral['modifier_trace'] if t['counters'] is not None) > 0


def test_schedules_seeds_and_unpooled_endpoint_laws():
    bank, _, artifacts = run.old.load_saved(run.old.DEFAULT_SAVED)
    sc = run.schedules(bank)
    assert len(sc['exposure']) == 432 and len(sc['readout']) == 8640
    assert run.audit_seeds(bank, artifacts)['admitted']
    for a in run.EXPOSURE_ARMS:
        rows = [r for r in sc['exposure'] if r['arm'] == a]
        assert len(rows) == 144
        assert all(sum(r['cells'][0] == c for r in rows) == 24 for c in bank['split']['development'])
        assert all(all(r['cells'].count(c) == 2 for c in bank['split']['development']) for r in rows)
    groups = {}
    for r in sc['readout']:
        groups.setdefault((r['build'], r['cell'], r['population'], r['scoring_repeat']), []).append(r)
    assert len(groups) == 1728
    assert all(len(rows) == 5 and len({tuple(r['seeds']) for r in rows}) == 1 for rows in groups.values())
    assert sum(r['arm'] in ('initial', 'R-all') for r in sc['readout']) == 3456
    rows = [dict(build=0, repeat=p, arm=a, final_f=f) for a in run.EXPOSURE_ARMS for p, f in enumerate((0, 1))]
    laws = run.probabilities(rows)
    assert laws['0:0']['L-final'] == 0 and laws['0:1']['L-final'] == 0.5
    assert all(q['initial'] == 1/32 for q in laws.values())


def test_bootstrap_attaches_reference_blocks_and_resamples_populations():
    ref = np.arange(1, 145).reshape(24, 6)
    values = dict(initial=ref, endpoint=0.95*ref)
    boot = run.paired_draws(values, np.random.default_rng(91))
    assert np.allclose(boot['endpoint']/boot['initial'], 0.95)
    identical_libraries = np.tile(np.arange(1, 7), (24, 1))
    nested = run.paired_draws(dict(x=identical_libraries), np.random.default_rng(91))['x']
    whole = run.paired_draws(dict(x=identical_libraries), np.random.default_rng(91), nested=False)['x']
    assert nested.std() > 0
    assert whole.std() == 0


def test_frozen_decision_branches():
    def ratios(primary, n=(0.7, 0.99), s=(0.7, 0.99)):
        return {k: {'evaluations': {'interval95': v}} for k, v in
                [('L-final/initial', primary), ('L-final/N-final', n), ('L-final/S-final', s)]}
    assert run.classify(ratios((0.7, 0.89))) == 'useful_with_inheritance_controls'
    assert run.classify(ratios((0.7, 0.89), n=(0.8, 1.01))) == 'saving_inheritance_unresolved'
    assert run.classify(ratios((0.81, 1.1))) == '20_percent_saving_excluded_for_this_procedure'
    assert run.classify(ratios((0.7, 1.1))) == 'unresolved'


@pytest.mark.parametrize('kwargs', [dict(modifier_mutation_probability=-0.1),
                                  dict(modifier_redraw_probability=1.1),
                                  dict(modifier_mutation_probability=1/32),
                                  dict(modifier_bits=[0]*256, modifier_mutation_probability=1/32)])
def test_invalid_mutation_settings_fail_before_search(job, kwargs):
    with pytest.raises(ValueError, match='modifier mutation'):
        search(job, **kwargs)
