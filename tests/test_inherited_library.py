"""Mechanistic validation of modifier alignment, law recovery and frozen schedules."""
import importlib.util
import subprocess
import sys

import numpy as np
import pytest

from experiments.chem_tape import inherited_library_run as run
from experiments.chem_tape.tree_gp_search import Tree, search


@pytest.fixture
def job():
    bank = run.saved.load_bank()
    c = next(c for c in bank['screen']['cells'] if c['id'] == bank['split']['development'][0])
    # Impossible label keeps replay independent of first-hit stopping semantics.
    return (dict(id=c['id'], labels=[123456]*len(bank['inputs'])), 14270001, 4096, 256, bank['inputs'], 0.5)


def comparable(row):
    return {k: v for k, v in row.items() if not ('seconds' in k or k in
            ('modifier_bits', 'modifier_trace', 'first_solve_evaluations', 'library_probability'))}


def test_default_replays_committed_engine(job, tmp_path):
    path = tmp_path / 'original.py'
    path.write_bytes(subprocess.check_output(['git', 'show', '60ab76697cc1e5592474b4819f4bb3761c5bbbcd:experiments/chem_tape/tree_gp_search.py']))
    spec = importlib.util.spec_from_file_location('tree_gp_original_1427', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    for prefixes in (None, [(10, 0, 1), (11, 0, 1, 10, 0, 1)]):
        old_donors = None if prefixes is None else [module.Tree(p) for p in prefixes]
        new_donors = None if prefixes is None else [Tree(p) for p in prefixes]
        assert comparable(search(job, donor_library=new_donors)) == comparable(module.search(job, donor_library=old_donors))


def test_fixed_laws_and_neutral_stream_independence(job):
    donors = [Tree((10, 0, 1)), Tree((11, 0, 1, 10, 0, 1))]
    ordinary = search(job)
    fixed = search(job, donor_library=donors)
    off = search(job, donor_library=donors, modifier_bits=[0]*256)
    on = search(job, donor_library=donors, modifier_bits=[1]*256)
    for k in ('curve', 'phenotype_diversity_curve', 'initial_tokens_hash', 'training_indices', 'compiled_length_histogram'):
        assert off[k] == ordinary[k]
        assert on[k] == fixed[k]
    assert off['operator']['library_draws'] == 0
    assert on['operator'] == fixed['operator']
    for shuffle in (False, True):
        neutral = search(job, modifier_bits=[1]*64+[0]*192, modifier_seed=123, shuffle_modifiers=shuffle)
        assert comparable(neutral) == comparable(ordinary)
    assert comparable(search(job, donor_library=donors, library_probability=0))['curve'] == ordinary['curve']


def test_recipient_elite_and_fallback_alignment(job):
    bits = np.array([1]*64+[0]*192)
    events = []
    def observe(event):
        nonlocal bits
        if 'elites' in event:
            assert event['old_bits'] == bits.tolist()
            assert event['next_bits'] == [int(bits[i]) for i in event['elites']] + [e['state'] for e in events]
            bits = np.array(event['next_bits'])
            events.clear()
        else:
            assert event['state'] == bits[event['recipient']]
            if event['rejected']:
                assert event['child'] is event['parent']
            events.append(event)
    result = search(job, donor_library=[Tree((11, 0, 1, 10, 0, 1))], modifier_bits=bits, lineage_observer=observe)
    assert result['modifier_bits'] == bits.tolist()
    assert result['operator']['rejected_mutation'] + result['operator']['rejected_crossover'] > 0
    assert all(t['counters'][0]['library_draws'] == 0 for t in result['modifier_trace'] if t['counters'])


def test_first_exact_hit_is_preserved_and_continues(job, monkeypatch):
    from experiments.chem_tape import tree_gp_search as tree
    labels = [0]*len(job[4])
    zero = Tree((5,))
    monkeypatch.setattr(tree, 'initialize', lambda rng, n: ([zero]*n, {}))
    altered = (dict(id='zero', labels=labels), *job[1:])
    stop = search(altered, modifier_bits=[0]*256)
    continued = search(altered, modifier_bits=[0]*256, continue_after_solve=True)
    assert stop['evaluations'] == continued['first_solve_evaluations'] == 256
    assert continued['evaluations'] == job[2] and continued['solved']
    assert continued['solver_tree'] == [5] and continued['exact_checks'] == 1
    assert len(continued['modifier_trace']) == job[2]//256
    assert all(t['phase'] == 'post' for t in continued['modifier_trace'])


def test_grid_rotation_pairing_and_aggregate_extraction():
    bank = run.saved.load_bank()
    sc = run.schedules(bank)
    assert len(sc['exposure']) == 336 and len(sc['readout']) == 1440
    for a, count in [('L', 96), ('S', 96), ('Z', 96), ('N', 48)]:
        rows = [r for r in sc['exposure'] if r['arm'] == a]
        assert len(rows) == count
        for c in bank['split']['development']:
            assert sum(r['cells'][0] == c for r in rows) == count//6
            assert all(r['cells'].count(c) == 2 for r in rows)
    for r in sc['readout']:
        assert len([m for m in sc['readout'] if m['seeds'] == r['seeds']]) == 5
    rows = [dict(build=0, arm=a, final_f=f) for a in ('L', 'S') for f in (0, 0.25, 0.5, 1)]
    probs = run.probabilities(rows, 1)[0]
    assert probs['L-final'] == probs['S-final'] == 0.21875


def test_seed_audit_and_size_null_builds():
    bank, libs, artifacts = run.load_saved(run.DEFAULT_SAVED)
    assert run.audit_seeds(bank, artifacts)['admitted']
    for b, lib in enumerate(libs):
        entries, _ = run.controls(lib['semantic_all'], run.seed('null', b))
        assert [(e['nodes'], e['compiled_length']) for e in entries] == [(e['nodes'], e['compiled_length']) for e in lib['semantic_all']]


def test_invalid_bits_rejected_before_conversion(job):
    with pytest.raises(ValueError, match='modifier bits'):
        search(job, modifier_bits=[0.5]*256)


def test_shuffled_alignment_includes_elites(job):
    children = []
    generations = []
    def observe(event):
        if 'elites' in event:
            old = event['old_bits']
            assert all(c['state'] == old[c['recipient']] for c in children)
            assert event['next_bits'] == [old[i] for i in event['elites']] + [c['state'] for c in children]
            generations.append(event)
            children.clear()
        else:
            children.append(event)
    result = search(job, modifier_bits=[1]*64+[0]*192, modifier_seed=991,
                    shuffle_modifiers=True, lineage_observer=observe)
    assert len(generations) == len(result['modifier_trace'])-1
    for g, event in enumerate(generations):
        assert np.mean(event['old_bits']) == result['modifier_trace'][g]['census_f']
        assert np.mean(event['next_bits']) == result['modifier_trace'][g]['next_f']
