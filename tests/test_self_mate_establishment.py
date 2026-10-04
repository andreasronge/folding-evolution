"""Guard the approved contest grid, census semantics, and §31 verdict boundaries."""
import random
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments/chem_tape'))
import self_mate_establishment as sm
from folding_evolution.chem_tape import evolve, tagged


def test_approved_grid_preserves_historical_parameters_and_tapes():
    old = yaml.safe_load((sm.HERE / 'sweeps/mapbias/s31_dose.yaml').read_text())
    spec = sm.make_spec()
    assert spec['base'] == {**old['base'], 'crossover_mate': 'self'}
    configs = sm.expand_grid(spec)
    assert len(configs) == len({cfg.hash() for cfg in configs}) == 240
    keys = set()
    for cfg in configs:
        comp, length, rate, start = sm.r31.identify(asdict(cfg))['cell']
        assert length == 64
        keys.add((comp, start, rate, cfg.seed))
        assert any(p['tape_length'] == 64 and p['crossover_rate'] == 0.3 and
                   p['seed_tapes'] == cfg.seed_tapes for p in old['paired'])
        pop = evolve.build_initial_population(cfg, evolve.make_rng(cfg), cfg.pop_size)
        n_shared = sum(np.array_equal(g, sm.sh.form_genome('shared', 64)) for g in pop)
        assert n_shared == (32 if start == '1/32' else 103)
    assert keys == {(comp, start, rate, seed) for comp in ('partly', 'duplicated')
                    for start in ('1/10', '1/32') for rate in (0.3, 0.7) for seed in range(30)}


def test_census_conserves_counts_and_matches_direct_operator():
    spec = sm.make_spec()
    result = sm.census(spec, 100, 0)
    assert result == sm.census(spec, 100, 0)
    for row in result['rows']:
        parent = sm.parents(spec)[row['parent']]
        rng = random.Random(0)
        direct = [tagged.crossover(parent, parent, rng, 'v2') for _ in range(100)]
        classified = [sm.sh.classify(g)['form'] or 'broken' for g in direct]
        assert sum(row['counts'].values()) == row['events'] == row['children'] == 100
        assert row['byte_clones'] == sum(np.array_equal(g, parent) for g in direct)
        assert row['counts'] == {k: classified.count(k) for k in row['counts']}
        assert 0 < row['counts']['broken'] < 100
        assert 0 < row['byte_clones'] < 100


@pytest.mark.parametrize('n,shared,expected', [(19, 19, 'no_solution'), (20, 18, 'between'),
                                             (20, 19, 'won'), (20, 0, 'gone')])
def test_historical_verdict(n, shared, expected):
    assert sm.r31.outcome({'n_exact': n, 'forms': {'shared': shared}}) == expected


def test_missing_results_are_rejected(tmp_path):
    cfg = sm.expand_grid(sm.make_spec())[0]
    with pytest.raises(ValueError, match='Missing'):
        sm.validate_run(tmp_path, cfg)


def test_undefined_mean_stays_null():
    assert sm.mean_defined([None, None]) is None
    assert sm.mean_defined([None, 0.0, 1.0]) == 0.5
