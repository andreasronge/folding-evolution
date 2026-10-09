"""Distribution, initialization, source recovery and contrast-direction guards."""

from collections import Counter

import numpy as np
import pytest

from experiments.chem_tape.composition_search import search
from experiments.chem_tape.frequency_matched_run import deterministic
from experiments.chem_tape.recoded import RecodedDecoder, R
from experiments.chem_tape.recoded_smoke import q_source
from experiments.chem_tape.recoded_run import schedules, runtime_admission, stable, recoded_search
from experiments.chem_tape.recoded_report import make_report, route
from experiments.chem_tape import then_addition_bank


@pytest.fixture(scope='module')
def source():
    return q_source()


@pytest.fixture(scope='module')
def decoder(source):
    return RecodedDecoder(dict(table=source['projected_tables.json']['BE1']['Q'], corpus='BE1', dose=30, k=0))


def test_full_row_counts_bijection_and_fixed_start(decoder):
    assert R == 24000
    assert decoder.validate()['rows'] == 800
    assert np.array_equal(decoder.lookup[0], decoder.q_lookup[0])
    assert not np.array_equal(decoder.lookup[1, 0], decoder.q_lookup[1, 0])
    assert not np.array_equal(decoder.inverse[1, 0], decoder.inverse[1, 1])
    assert decoder.hash() != decoder.source_hash


def test_initial_bijection_and_unsigned_conditional_encoder(decoder):
    rng = np.random.default_rng(537)
    a = rng.integers(R, size=(512, 32), dtype=np.int32)
    tokens = decoder.q_decode(a)
    recoded = decoder.recode(a)
    assert np.array_equal(decoder.decode(recoded), tokens)
    previous = np.full(len(a), 24)
    for j in range(32):
        # Mapping is invertible even as previous-token contexts change.
        assert np.array_equal(decoder.inverse[j, previous, a[:, j]], recoded[:, j])
        previous = tokens[:, j]
    encoded = decoder.encode(tokens.astype(np.uint8), rng)
    assert np.array_equal(decoder.decode(encoded), tokens)
    # Conditional aliases vary rather than all choosing a fixed representative.
    duplicates = np.repeat(tokens[:1], 400, axis=0)
    b = decoder.encode(duplicates, rng)
    assert len(np.unique(b[:, 1])) > 100
    with pytest.raises(ValueError):
        decoder.encode(tokens.astype(float), rng)


def test_identity_initial_hook_keeps_search_streams(source):
    from experiments.chem_tape.position_matched import PositionalDecoder
    table = source['projected_tables.json']['BE1']['Q']
    b, cells = then_addition_bank.load()
    cell = cells[b['selected_ids'][0]]
    job = (cell, 'Q', table, 537, 1024, 32, b['inputs'], b['alphabet'])
    a = search(job, decoder_factory=PositionalDecoder)
    z = search(job, decoder_factory=PositionalDecoder, initial_transform=lambda pop, _: pop.copy())
    assert deterministic(a) == deterministic(z)
    # Recovery instrumentation adds only fields excluded from scientific replay.
    assert stable(dict(a, solver=[1], verification_seconds=2)) == stable(a)


def test_realization_assignment_and_replay_roster(source):
    b, _ = then_addition_bank.load()
    full, replay, timing = schedules(source['schedule.json'], b['selected_ids'])
    assert len(full) == 4096 and len(replay) == 32 and len(timing) == 64
    assert Counter(r['arm'] for r in replay) == {'Q': 16, 'C': 16}
    counts = Counter((r['corpus'], r['cell'], r['arm'], r['realization']) for r in full)
    assert set(counts.values()) == {4}
    assert len({(r['corpus'], r['arm'], r['realization']) for r in timing}) == 64
    for r in full:
        seeds = sorted(x['seed'] for x in full if (x['corpus'], x['cell'], x['arm']) == (r['corpus'], r['cell'], r['arm']))
        assert r['realization'] == seeds.index(r['seed']) // 4


def test_report_ratio_direction_and_incomplete_refusal(source):
    b, _ = then_addition_bank.load()
    full, _, _ = schedules(source['schedule.json'], b['selected_ids'])
    base = [r for r in source['schedule.json'] if r['arm'] == 'Q']
    refs = [dict(r, arm=arm, solved=True, evaluations=e, seconds=0, cap=524288)
            for r in base for arm, e in (('Q', 1024), ('C', 256))]
    rows = [dict(r, solved=True, evaluations=512 if r['arm']=='R30' else 2048, seconds=0, cap=524288) for r in full]
    prep = dict(arms={a: dict(mean_worker_seconds=1) for a in ('R30', 'R100')})
    config = dict(scope='test', workers=10)
    report = make_report(rows, refs, full, config, prep)
    v = report['sensitivities']['unsolved_2cap']
    assert v['G']['speed_ratio'] == pytest.approx(2)
    assert v['H']['speed_ratio'] == pytest.approx(2)
    assert v['G100']['speed_ratio'] == pytest.approx(.5)
    assert v['descriptive_gap_share'] == pytest.approx(.5)
    assert v['G']['df'] == 15
    assert report['approaches_C'] == 'bounded_outside_1.5'
    assert report['outcome'] == 'useful_gain_at_fixed_uniform_prior_supply'
    assert not make_report(rows[:-1], refs, full, config, prep)['efficacy_eligible']
    assert route(dict(interval_95=[1.1, 1.3])) == 'unresolved'
    assert not report['no_useful_gain_at_either_dose']


def test_runtime_gate_includes_preparation_setup_and_tail():
    assert runtime_admission(4000, 5000, 10000, 100, 1799)['admitted']
    assert not runtime_admission(4000, 5000, 10000, 100, 1801)['admitted']
    assert not runtime_admission(4000, 5000, 11540, 100, 1)['admitted']
    assert not runtime_admission(11000, 5000, 10000, 100, 1)['admitted']


def test_identity_recoded_runner_replays_original_fields(source):
    from experiments.chem_tape.position_matched import PositionalDecoder
    b, cells = then_addition_bank.load()
    table = source['projected_tables.json']['BE1']['Q']
    cell = cells[b['selected_ids'][0]]
    job = (cell, 'Q', table, 537, 1024, 32, b['inputs'], b['alphabet'])
    meta = dict(phase='fresh', corpus='BE1', family='BE')
    original = search(job, decoder_factory=PositionalDecoder)
    original.update(meta)
    payload = dict(table=table, corpus='BE1', dose=0, k=0)
    recoded = recoded_search(((cell, 'Q', payload, 537, 1024, 32, b['inputs'], b['alphabet']), meta))
    assert stable(original) == stable(recoded)
