"""Guard identity, corpus weighting, censoring and fixed-size routing."""

from copy import deepcopy

import pytest

from experiments.chem_tape.frequency_matched_run import (
    deterministic, frozen_source, historical_source, schedules,
)
from experiments.chem_tape import then_addition_bank
from experiments.chem_tape.frequency_matched_report import make_report, route


@pytest.fixture(scope='module')
def source():
    bank, _ = then_addition_bank.load()
    saved, _ = frozen_source()
    history, _, _ = historical_source(saved['corpora.json'], saved['freeze.json'], bank)
    roster, replay, timing = schedules(history['schedule.json'], bank['selected_ids'])
    return history, roster, replay, timing


def test_exact_roster_and_replay_selection(source):
    history, roster, replay, timing = source
    assert len(roster) == 2048 and len({r['seed'] for r in roster}) == 2048
    assert len(replay) == 32 and {r['corpus'] for r in replay} == {'BE1', 'PA1'}
    assert len(timing) == 16 and len({r['corpus'] for r in timing}) == 16
    assert roster == [dict(r, arm='K') for r in history['schedule.json'] if r['arm'] == 'C']


def test_replay_ignores_only_clocks(source):
    ref = source[0]['search.jsonl'][0]
    changed = deepcopy(ref)
    for name in ('seconds', 'decode_seconds', 'budget_seconds'):
        changed[name] = None
    assert deterministic(ref) == deterministic(changed)
    changed['curve'][0][1] += 1
    assert deterministic(ref) != deterministic(changed)


def test_complete_corpus_weighting_and_ratio_direction(source):
    history, roster, _, _ = source
    rows = [dict(r, arm='K') for r in history['search.jsonl'] if r['arm'] == 'C']
    config = dict(scope='test fixture')
    result = make_report(rows, history['search.jsonl'], roster, config)
    for val in result['sensitivities'].values():
        assert val['C_K']['speed_ratio'] == 1
        assert val['C_K']['interval_95'] == [1, 1]
        assert val['C_K']['df'] == 15
        assert val['K_T']['speed_ratio'] == val['C_T']['speed_ratio']
        assert val['descriptive_log_K_T_over_log_C_T'] == 1
    assert result['outcome']['label'] == 'replacement_adequate'
    assert result['sensitivities']['unsolved_2cap']['arms']['C']['solved'] == 1771
    assert result['sensitivities']['unsolved_2cap']['arms']['T']['solved'] == 1547
    assert result['sensitivities']['unsolved_2cap']['arms']['G4']['solved'] == 162
    # Analytical constant ratio with no censoring, all 16 corpus intervals equal.
    references = [dict(r, solved=True, evaluations=256) for r in history['search.jsonl']]
    rows = [dict(r, arm='K', solved=True, evaluations=512) for r in references if r['arm'] == 'C']
    result = make_report(rows, references, roster, config)
    p = result['sensitivities']['unsolved_2cap']
    assert p['C_K']['speed_ratio'] == pytest.approx(2)
    assert p['K_T']['speed_ratio'] == pytest.approx(.5)
    assert result['outcome']['label'] == 'replacement_insufficient'


def test_incomplete_error_and_duplicate_never_route(source):
    history, roster, _, _ = source
    rows = [dict(r, arm='K') for r in history['search.jsonl'] if r['arm'] == 'C']
    for subset, error in ((rows[:-1], None), (rows, 'failed replay')):
        assert make_report(subset, history['search.jsonl'], roster, dict(scope='test'), error)['outcome']['label'] == 'incomplete'
    with pytest.raises(ValueError, match='duplicate'):
        make_report(rows + rows[:1], history['search.jsonl'], roster, dict(scope='test'))


def test_capped_sensitivity_and_empty_both_solved(source):
    history, roster, _, _ = source
    rows = [dict(r, arm='K', solved=False, evaluations=r['cap']) for r in history['search.jsonl'] if r['arm'] == 'C']
    refs = [dict(r, solved=True, evaluations=256) for r in history['search.jsonl']]
    result = make_report(rows, refs, roster, dict(scope='test'))
    r2 = result['sensitivities']['unsolved_2cap']['C_K']['speed_ratio']
    r1 = result['sensitivities']['unsolved_1cap']['C_K']['speed_ratio']
    assert r2 / r1 == pytest.approx(2)
    assert result['both_solved']['C_K']['n'] == 0
    assert result['both_solved']['C_K']['speed_ratio'] is None
    assert all(n == 0 for per in result['both_solved']['C_K']['occupancy'].values() for n in per.values())


def test_decision_bounds():
    assert route({'interval_95': [1.2, 1.3]}, True)['label'] == 'replacement_insufficient'
    assert route({'interval_95': [1.0, 1.2]}, True)['label'] == 'replacement_adequate'
    assert route({'interval_95': [1.1, 1.3]}, True)['label'] == 'unresolved'
