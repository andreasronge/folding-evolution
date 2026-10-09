"""Projection/decoder intervention and complete-roster inference guards."""

import numpy as np
import pytest

from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.frequency_matched_run import frozen_source, historical_source
from experiments.chem_tape.four_reducer_maps import R, tables
from experiments.chem_tape.position_matched import (
    PositionalDecoder, marginals, project, reference_decode, table_hash,
)
from experiments.chem_tape.position_matched_run import runtime_admission, schedules
from experiments.chem_tape.position_matched_report import make_report, route, joint_interpretation
from experiments.chem_tape import then_addition_bank


def test_runtime_admission_tolerates_measured_timing_drift():
    # Review's measured projections, including a 6% slowdown that would flip
    # the old conservative-price predicate despite ample roster headroom.
    for drift in (1, 1.019, 1.06):
        sample, batch, capped, fit = np.array([6502.15, 7812.38, 9485.97, 50.09]) * drift
        result = runtime_admission(sample, batch, capped, fit, 198.86 * drift)
        assert result['admitted']
        assert result['expected_scoring_with_safety_seconds'] < 11700
        assert result['all_capped_scoring_bound_seconds'] < 11700
        assert result['admission_rule']['version'] == 'expected_safety_and_capped_bound_v1'
        if drift == 1.06:
            assert 1.15 * max(sample, batch, capped) + fit + 120 > 11700


@pytest.mark.parametrize('sample,batch,capped,elapsed,admitted', [
    (0, 0, 11579, 1800, True),     # Preparation limit is inclusive.
    (0, 0, 11579, 1800.01, False),
    (0, 0, 11580, 1, False),       # All-capped timeout is a strict hard bound.
    (0, 10000, 11579, 1, True),
    (0, 10100, 11579, 1, False),   # Expected work can independently refuse.
    (10100, 0, 11579, 1, False),   # Both expected projections matter.
    (0, 11580 / 1.15, 0, 1, False),  # Expected timeout is also strict.
])
def test_runtime_admission_budget_guards(sample, batch, capped, elapsed, admitted):
    assert runtime_admission(sample, batch, capped, 0, elapsed)['admitted'] == admitted


def test_changing_positions_lookup_and_repeated_legacy_identity():
    g = tables()['G4']
    repeated = np.tile(g, (32, 1, 1))
    rng = np.random.default_rng(239)
    a = rng.integers(R, size=(256, 32), dtype=np.int32)
    d = PositionalDecoder(repeated)
    assert d.hash() == Decoder(g).hash() == table_hash(g)
    assert np.array_equal(d.decode(a), Decoder(g).decode(a))
    # Shift columns separately at every position, preserving support and range.
    counts = np.diff(repeated, prepend=0, axis=2)
    changed = np.array([np.cumsum(np.roll(c, j, axis=1), axis=1) for j, c in enumerate(counts)])
    assert np.array_equal(PositionalDecoder(changed).decode(a), reference_decode(changed, a))
    assert not np.array_equal(d.decode(a), PositionalDecoder(changed).decode(a))
    with pytest.raises(ValueError):
        PositionalDecoder(changed).decode(a.astype(float))
    with pytest.raises(ValueError):
        PositionalDecoder(changed).decode(a[:, :31])


@pytest.fixture(scope='module')
def source():
    b, _ = then_addition_bank.load()
    saved, _ = frozen_source()
    history, _, _ = historical_source(saved['corpora.json'], saved['freeze.json'], b)
    return saved, history, schedules(history['schedule.json'], b['selected_ids'])


def test_quantized_projection_support_start_and_propagation(source):
    c = np.asarray(source[0]['corpora.json']['BE1']['tables']['C'])
    controls, diagnostics = project(c)
    assert np.array_equal(controls['Q'][0, 24], c[24])
    for arm, t in controls.items():
        assert np.min(np.diff(t, prepend=0, axis=2)) >= 250
        assert diagnostics['checks'][arm]['maximum_token_error'] <= .001
        assert diagnostics['checks'][arm]['maximum_total_variation'] <= .005
        assert np.max(np.abs(marginals(t) - marginals(c))) <= .001
    assert np.all(controls['P'] == controls['P'][:, :1])
    assert not np.all(controls['Q'][1] == controls['Q'][1, :1])


def test_complete_roster_and_joint_controls(source):
    _, history, (roster, ct, kr, timing) = source
    assert len(roster) == 4096 and len(ct) == 32 and len(kr) == 16 and len(timing) == 32
    assert {r['cell'] for r in timing} == {r['cell'] for r in roster}
    assert len({r['corpus'] for r in timing}) == 16
    # Known cost ratios independent of actual searches; balanced 16-corpus result.
    refs = [dict(r, solved=True, evaluations=256) for r in history['search.jsonl']]
    refs += [dict(r, arm='K') for r in refs if r['arm'] == 'C']
    rows = [dict(r, arm=a, evaluations=512 if a == 'Q' else 256) for r in refs if r['arm'] == 'C' for a in ('Q', 'P')]
    report = make_report(rows, refs, roster, dict(scope='fixture'))
    primary = report['sensitivities']['unsolved_2cap']
    assert primary['C_Q']['speed_ratio'] == pytest.approx(2)
    assert primary['C_P']['speed_ratio'] == 1
    assert primary['Q_K']['speed_ratio'] == pytest.approx(.5)
    assert primary['Q_P']['speed_ratio'] == pytest.approx(.5)
    assert primary['C_Q']['df'] == 15
    assert report['outcome']['label'] == 'replacement_insufficient'
    assert report['P_interpretation_band']['label'] == 'replacement_adequate'
    assert 'independent positional P remains' in report['joint_interpretation']
    assert make_report(rows[:-1], refs, roster, dict(scope='fixture'))['outcome']['label'] == 'incomplete'
    assert make_report(rows, refs, roster, dict(scope='fixture'), 'failed gate')['outcome']['label'] == 'incomplete'
    with pytest.raises(ValueError, match='duplicate'):
        make_report(rows + rows[:1], refs, roster, dict(scope='fixture'))
    unsolved = [dict(r, solved=False, evaluations=r['cap']) for r in rows]
    empty = make_report(unsolved, refs, roster, dict(scope='fixture'))
    assert empty['both_solved']['C_Q']['n'] == 0
    assert empty['both_solved']['C_Q']['speed_ratio'] is None


def test_boundary_routing_and_unresolved_interpretation():
    adequate = route(dict(interval_95=[1, 1.2]), True)
    insufficient = route(dict(interval_95=[1.2, 1.3]), True)
    unresolved = route(dict(interval_95=[1.1, 1.3]), True)
    assert adequate['label'] == 'replacement_adequate'
    assert insufficient['label'] == 'replacement_insufficient'
    assert unresolved['label'] == 'unresolved'
    assert 'supplied G4 grammar remains useful' in joint_interpretation(adequate, insufficient)
    assert 'without ruling out all' in joint_interpretation(insufficient, insufficient)
