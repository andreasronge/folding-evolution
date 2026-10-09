import copy

import pytest

from experiments.chem_tape.fragment_operator import BlockOperator
from experiments.chem_tape.fragment_reuse_run import pinned_history, target_ids
from experiments.chem_tape.fragment_run import CORPORA
from experiments.chem_tape.then_addition_run import frozen_source
from experiments.chem_tape.then_addition_bank import load
from experiments.chem_tape.comparison_gate_bank import load_training
from experiments.chem_tape.suffix_preservation_audit import audit
from experiments.chem_tape.suffix_preservation_run import roster, timing_roster, admit
from experiments.chem_tape.suffix_preservation_report import report, route


def test_matched_actual_suffix_and_neutral_controls():
    saved, _ = frozen_source()
    _, libraries = pinned_history()
    result = audit(saved['corpora.json'], libraries, n=10000)
    assert result['coverage']['edits'] == 10000
    assert result['coverage']['no_op_block'] >= 2000
    assert result['coverage']['unchanged_final_block_token'] >= 4000
    assert result['suffix_histogram'][0] < 10000


def ids():
    bank, _ = load_training()
    ta, _ = load()
    return target_ids(bank, ta)


def test_fixed_rosters_and_runtime_stop():
    banks = ids()
    paired, fallback = roster(banks, True), roster(banks, False)
    assert len(paired) == 5120 and len(fallback) == 8192
    assert not {r['seed'] for r in paired} & {r['seed'] for r in fallback}
    for historical_paired in (True, False):
        smoke = timing_roster(banks, historical_paired)
        assert len(smoke) == 32
        assert {r['corpus'] for r in smoke} == set(CORPORA)
        rows = [dict(r, solved=True, seconds=6, evaluations=100000) for r in smoke]
        assert admit(rows, 20, 60, historical_paired)['admitted']
        for r in rows:
            r['seconds'] = 60
        assert not admit(rows, 200, 240, historical_paired)['admitted']


@pytest.mark.parametrize('point,lo,hi,decision', [
    (.96, .93, .99, 'ripple_helps_drop_repair'),
    (1.10, 1.01, 1.20, 'preservation_needed_keep_repair'),
    (1.02, .97, 1.09, 'not_needed_at_this_resolution'),
    (1.05, .981, 1.124, 'unresolved_keep_incumbent_repair'),
])
def test_ordered_rules(point, lo, hi, decision):
    assert route(dict(speed_ratio=point, interval_95=[lo, hi])) == decision


@pytest.mark.parametrize('paired', [True, False])
def test_complete_report_and_metadata_gate(tmp_path, paired):
    schedule = roster(ids(), paired)
    def row(meta):
        stats = BlockOperator(meta['arm'], [{'tokens': [1, 2, 3]}], 1606).stats
        return dict(meta, solved=False, evaluations=524288, cap=524288, seconds=1,
                    solver=None, operator=copy.deepcopy(stats), curve=[[256, 32, 8]])
    rows = [row(r) for r in schedule]
    historical = [row(dict(r, arm=arm)) for r in schedule for arm in ('W', 'C')] if paired else []
    preparation = dict(historical_paired=paired, admission={'projected_seconds': 100},
                       resolution_cost=dict(source_collection_worker_seconds_per_corpus=10,
                           library_worker_seconds_per_corpus=1, historical_C_fit_worker_seconds_per_corpus=1,
                           reporting_queue_seconds=600, agent_hours=3))
    result = report(tmp_path, rows, schedule, preparation, historical)
    assert result['banks']['then_addition']['comparisons']['W/R']['df'] == 15
    assert result['decision'] == 'not_needed_at_this_resolution'
    if paired:
        assert result['banks']['then_addition']['diagnostics']['C']['suffix_ripple_fraction'] == 0
    assert (tmp_path / 'then_addition_ripple.png').stat().st_size > 1000
    with pytest.raises(ValueError, match='incomplete'):
        report(tmp_path, rows[:-1], schedule, preparation, historical)
    changed = copy.deepcopy(rows)
    changed[0]['phase'] = 'holdout' if changed[0]['phase'] == 'then_addition' else 'then_addition'
    with pytest.raises(ValueError, match='changed'):
        report(tmp_path, changed, schedule, preparation, historical)


def test_every_queued_target_has_search_payload(tmp_path, monkeypatch):
    from argparse import Namespace
    from experiments.chem_tape.suffix_preservation_run import Runner
    monkeypatch.setenv('RUN_DIR', str(tmp_path))
    args = Namespace(prepare=True, preparation=None, validate_preparation=False,
                     workers=10, deadline_seconds=1680)
    runner = Runner(args)
    for paired in (True, False):
        for meta in runner.rosters[str(paired)]:
            job, returned, _, _, _ = runner.envelope(meta)
            assert job[0]['id'] == meta['cell'] and returned == meta
            assert set(job[0]) == {'id', 'labels'}
            assert len(job[0]['labels']) == len(job[6])
