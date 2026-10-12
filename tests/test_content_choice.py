"""Content-choice laws, RNG isolation, inheritance and inference pairing."""
import importlib.util
import subprocess
import sys

import numpy as np
import pytest

from experiments.chem_tape import content_choice_run as run
from experiments.chem_tape.tree_gp_search import Tree, search
from tests.test_inherited_library import comparable


@pytest.fixture
def job():
    bank = run.old.saved.load_bank()
    return (dict(id=bank['split']['development'][0], labels=[10**12]*len(bank['inputs'])),
            run.seed('validation', 0), 16384, 256, bank['inputs'], 0.5)


def plain(row):
    result = comparable(row)
    result.pop('content_choice_gate_fraction', None)
    result['operator'] = {k: v for k, v in result['operator'].items() if k not in ('order_draws', 'gate_draws')}
    return result


def test_legacy_replay(job, tmp_path):
    path = tmp_path/'original.py'
    path.write_bytes(subprocess.check_output(['git', 'show', 'HEAD:experiments/chem_tape/tree_gp_search.py']))
    spec = importlib.util.spec_from_file_location('original_content_choice', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    prefixes = [(10, 0, 1), (11, 0, 1, 10, 0, 1)]
    for linked in (False, True):
        kwargs = dict(modifier_bits=[0]*128+[1]*128, modifier_seed=run.seed('validation', 1),
            shuffle_modifiers=True, modifier_mutation_probability=1/32,
            modifier_redraw_probability=0.5, continue_after_solve=True) if linked else {}
        a = search(job, donor_library=[Tree(p) for p in prefixes], **kwargs)
        b = module.search(job, donor_library=[module.Tree(p) for p in prefixes], **kwargs)
        assert comparable(a) == comparable(b)
        if linked:
            assert a['modifier_trace'] == b['modifier_trace'] and a['modifier_bits'] == b['modifier_bits']


@pytest.mark.parametrize('f', [0, 1, 0.5])
def test_identical_and_pure_limits(job, f):
    a, b = [Tree((10, 0, 1))], [Tree((11, 0, 1, 10, 0, 1))]
    libraries = (a, a) if f == 0.5 else (a, b)
    selected = a if f in (0, 0.5) else b
    assert plain(search(job, donor_libraries=libraries, gate_fraction=f)) == comparable(search(job, donor_library=selected))
    for state in (0, 1):
        row = search(job, donor_libraries=(a, b), modifier_bits=[state]*256)
        ref = search(job, donor_library=(a, b)[state])
        assert plain(row) == comparable(ref)


def test_normalization_and_per_state_rates(job):
    # Unequal list sizes must not change the source mixture mass.
    order = [Tree((0,))]
    gate = [Tree((i,)) for i in (1, 2, 3, 5, 6)]
    hits = {p.prefix: 0 for p in order+gate}
    row = search((job[0], job[1], 65536, *job[3:]), donor_libraries=(order, gate),
                 gate_fraction=0.3, donor_observer=lambda t, rejected: hits.__setitem__(t.prefix, hits[t.prefix]+1))
    op = row['operator']
    for count, n, p in [(op['library_draws'], op['mutation'], 0.5),
                         (op['gate_draws'], op['library_draws'], 0.3)]:
        assert abs(count-n*p) < 6*np.sqrt(n*p*(1-p))
    for t in gate:
        assert abs(hits[t.prefix]-op['gate_draws']/5) < 6*np.sqrt(op['gate_draws']*0.2*0.8)
    row = search(job, donor_libraries=(order, gate), modifier_bits=[0]*128+[1]*128,
        modifier_seed=run.seed('validation', 2), modifier_mutation_probability=1/32,
        modifier_redraw_probability=0.5, continue_after_solve=True)
    for state in (0, 1):
        cc = [t['counters'][state] for t in row['modifier_trace'] if t['counters'] is not None]
        n, count = sum(c['mutation'] for c in cc), sum(c['library_draws'] for c in cc)
        assert abs(count-n*0.5) < 6*np.sqrt(n*0.25)
        assert sum(c['gate_draws' if state == 0 else 'order_draws'] for c in cc) == 0


@pytest.mark.parametrize('shuffle', [False, True])
def test_neutral_stream_and_unbiased_redraw(job, shuffle):
    libraries = ([Tree((10, 0, 1))], [Tree((11, 0, 1, 10, 0, 1))])
    reference = search(job, donor_libraries=libraries, gate_fraction=0.5, continue_after_solve=True)
    row = search(job, donor_libraries=libraries, gate_fraction=0.5, modifier_bits=[0]*128+[1]*128,
        modifier_seed=run.seed('validation', 3), modifier_mutation_probability=1/32,
        modifier_redraw_probability=0.5, shuffle_modifiers=shuffle, continue_after_solve=True)
    assert comparable(row) == comparable(reference)
    transitions = np.sum([t['modifier_transitions'] for t in row['modifier_trace'] if t['counters'] is not None], axis=0)
    for s in (0, 1):
        n, count = transitions[s].sum(), transitions[s, 1-s]
        assert abs(count-n/64) < 6*np.sqrt(n*(1/64)*(63/64))


def test_bit_tree_alignment_with_rejected_children(job):
    children, generations = [], []
    def observe(event):
        if 'elites' in event:
            old = event['old_bits']
            assert all(c['inherited_state'] == old[c['recipient']] for c in children)
            assert event['next_bits'] == [old[i] for i in event['elites']]+[c['state'] for c in children]
            generations.extend(children); children.clear()
        else:
            if event['rejected']:
                assert event['child'] is event['parent']
            if event['donor_source'] is not None:
                assert event['donor_source'] == event['state']
            children.append(event)
    search(job, donor_libraries=([Tree((11, 0, 1, 10, 0, 1))], [Tree((11, 2, 3, 10, 2, 3))]),
        modifier_bits=[0]*128+[1]*128, modifier_seed=run.seed('validation', 4),
        modifier_mutation_probability=1, modifier_redraw_probability=0.5,
        shuffle_modifiers=True, lineage_observer=observe, continue_after_solve=True)
    assert any(c['rejected'] for c in generations)
    assert any(c['rejected'] and c['state'] != c['inherited_state'] for c in generations)


def test_schedules_seeds_and_reciprocal_endpoints():
    banks, _, history = run.load_saved()
    sc = run.schedules(banks)
    assert len(sc['exposure']) == 1152 and len(sc['readout']) == 36288
    assert sum(m['family'] == 'order' for m in sc['readout']) == 12096
    assert sum(m['family'] == 'gate' for m in sc['readout']) == 24192
    assert run.audit_seeds(banks, history)['admitted']
    for m in sc['exposure']:
        assert all(m['cells'].count(c) == 2 for c in banks[m['family']]['split']['development'])
    endpoints = {(fam, 0, a, p): dict(final_f=f) for fam, f in [('order', 0.1), ('gate', 0.9)] for a in run.ARMS for p in range(2)}
    for family, matched in [('order', 0.1), ('gate', 0.9)]:
        m = dict(family=family, build=0, population=0)
        assert run.fraction(m | dict(arm='L-matched'), endpoints) == matched
        assert run.fraction(m | dict(arm='L-swapped'), endpoints) == (0.9 if family == 'order' else 0.1)


def test_paired_bootstrap_keeps_shared_pure_references():
    ref = np.arange(1, 193).reshape(24, 8)
    values = {'order/M': ref, 'order/L-matched': ref*0.8, 'gate/M': ref*2,
              'gate/L-matched': ref*1.8, 'order/O': np.repeat(np.arange(1, 25)[:, None], 8, axis=1)}
    boot = run.recurrent.paired_draws(values, np.random.default_rng(4))
    assert np.allclose(boot['order/L-matched']/boot['order/M'], 0.8)
    assert np.allclose(boot['gate/M']/boot['order/M'], 2)
    whole = run.recurrent.paired_draws(values, np.random.default_rng(4), nested=False)
    assert np.array_equal(boot['order/O'], whole['order/O'])


def test_outcome_precedence():
    def classify(ci, directions):
        ratios = {f+'/'+k: dict(interval95=[0.7, 0.99 if f in directions else 1.1]) for f in run.FAMILIES for k in ('L-matched/M', 'L-matched/L-swapped')}
        return run.classify(dict(interval95=ci), ratios)
    r = classify([0.82, 0.88], run.FAMILIES)
    assert r['outcome'] == 'useful_reciprocal' and r['twenty_percent_pooled_saving_excluded']
    assert classify([0.7, 0.88], ['order'])['outcome'] == 'useful_one_direction'
    assert classify([0.7, 0.88], [])['outcome'] == 'pooled_improvement_directional_dependence_unresolved'
    assert classify([0.81, 1.1], [])['outcome'] == '20_percent_pooled_saving_excluded'
    assert classify([0.7, 1.1], [])['outcome'] == 'unresolved'


@pytest.mark.parametrize('kwargs', [dict(donor_libraries=([], []), gate_fraction=0.5),
    dict(donor_libraries=([Tree((0,))],), gate_fraction=0.5), dict(gate_fraction=0.5),
    dict(donor_libraries=([Tree((0,))], [Tree((1,))]), gate_fraction=1.1),
    dict(donor_libraries=([Tree((0,))], [Tree((1,))]))])
def test_invalid_laws_fail_closed(job, kwargs):
    with pytest.raises(ValueError):
        search(job, **kwargs)


def test_first_hit_preserved_through_fixed_exposure(job):
    cell = dict(id=job[0]['id'], labels=[x[0] for x in job[4]])
    easy = (cell, job[1], 16384, *job[3:])
    kwargs = dict(donor_libraries=([Tree((0,))], [Tree((1,))]),
        modifier_bits=[0]*128+[1]*128, modifier_seed=run.seed('validation', 5),
        modifier_mutation_probability=1/32, modifier_redraw_probability=0.5)
    stopped = search(easy, **kwargs)
    continued = search(easy, continue_after_solve=True, **kwargs)
    assert stopped['solved'] and continued['solved']
    assert continued['first_solve_evaluations'] == stopped['evaluations']
    assert continued['solver'] == stopped['solver']
    assert continued['evaluations'] == 16384 and len(continued['modifier_trace']) == 64
    assert continued['first_solve_evaluations'] < continued['evaluations']
