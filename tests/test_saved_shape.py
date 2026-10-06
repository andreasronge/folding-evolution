"""Scientific gates and clustering invariants for the approved 1425 design."""

import numpy as np
import pytest
from scipy.stats import t

from experiments.chem_tape.composition_search import base_tables
from experiments.chem_tape.saved_shape_maps import emitted, fit_frequency
from experiments.chem_tape.saved_shape_report import dependency, interval, primary, report


def metrics(be, lin, shift):
    return {key: dict(state='complete', interval_95=value)
            for key, value in zip(('BE', 'LIN', 'shift'), (be, lin, shift))}


def test_first_match_and_tradeoff_language():
    c = {'R/M+': metrics([1.1, 1.5], [0.5, 0.9], [1.4, 2])}
    assert primary(c, True)['row'] == 1
    assert primary(c, False)['row'] == 0
    c['R/M+']['BE']['interval_95'] = [0.9, 1.3]
    assert primary(c, True) == dict(row=2, meaning='Relative shift replicates without resolved BE gain.', linear_loss=True)
    c['R/M+']['LIN']['interval_95'][1] = 1
    assert not primary(c, True)['linear_loss']
    c['R/M+'] = metrics([0.8, 1.24], [0.8, 1.2], [0.8, 1.40])
    assert primary(c, True)['row'] == 3
    c['R/M+']['shift']['interval_95'][1] = 1.41
    assert primary(c, True)['row'] == 4
    c = {'R/R_fm': metrics([0.8, 1.1], [0.4, 0.7], [1.01, 1.2]),
         'R_fm/M+': metrics([1, 2], [0.8, 1], [1.1, 2])}
    d = dependency(c)
    assert d['row'] == 'D-a' and not d['residual_branch_help']
    # D-a takes precedence even when D-b would also match.
    c['R/R_fm']['shift']['interval_95'][0] = 1
    assert dependency(c)['row'] == 'D-b'


def test_exact_emission_and_production_normalized_fit():
    counts = np.arange(1, 24)
    tied = np.tile(np.cumsum(counts * (23000 // counts.sum())), (24, 1))
    np.testing.assert_allclose(emitted(tied), counts/counts.sum(), atol=1e-15)
    g = base_tables()['G']
    fitted = fit_frequency(emitted(g), g)
    assert fitted['accepted'] and fitted['tv'] < 1e-10
    np.testing.assert_array_equal(fitted['table'], g)


def test_cluster_means_missing_fit_and_duplicate_searches():
    cells = [dict(id='be', shape='BE'), dict(id='lin', shape='LIN')]
    maps, rows = {}, []
    for k in range(1, 7):
        for rep in ('a', 'b'):
            for family, delta in [('M+', 0), ('R', 0.2*k), ('R_abl', 0), ('R_fm', 0)]:
                name = f'{family}{k}{rep}'
                maps[name] = dict(table_hash=name, emitted_frequencies=[1/23]*23)
                for cell in ('be', 'lin'):
                    rows.append(dict(arm=name, cell=cell, seed=1, table_hash=name,
                                     solved=True, log2_cost=10 - (delta if cell == 'be' else 0)))
    r = report(rows, maps, cells, [1], {}, True)
    pooled = r['layers']['pooled']['contrasts']['R/M+']['BE']
    values = np.arange(1, 7)*0.2
    assert pooled['n'] == 6 and pooled['df'] == 5
    expected = 2**(values.mean() - t.ppf(.975, 5)*values.std(ddof=1)/np.sqrt(6))
    assert pooled['interval_95'][0] == pytest.approx(expected)
    np.testing.assert_allclose(pooled['per_start_log2'], values)
    assert r['outcome']['row'] == 1
    assert interval([1]*5)['state'] == 'unresolved'
    # A failed fit affects the dependency layer, not the available replication.
    no_fit = {n: m for n,m in maps.items() if n != 'R_fm3b'}
    r = report([r for r in rows if r['arm'] in no_fit], no_fit, cells, [1], {}, True)
    assert r['outcome']['row'] == 1
    assert r['layers']['pooled']['dependency']['row'] == 'D-c'
    # Duplicate or missing observations cannot silently become a complete start.
    r = report(rows + [next(r for r in rows if r['arm']=='R3b')], maps, cells, [1], {}, True)
    assert r['outcome']['row'] == 0
    assert r['layers']['b_only']['contrasts']['R/M+']['shift']['state'] == 'unresolved'
