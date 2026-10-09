import numpy as np
import pytest

from experiments.chem_tape.composition_search import Decoder, search
from experiments.chem_tape.fragment_operator import BlockOperator, trace
from experiments.chem_tape.fragment_report import route
from experiments.chem_tape.fragment_run import admit, schedule, smoke_schedule
from experiments.chem_tape.four_reducer_maps import tables


@pytest.mark.parametrize('arm', ['F', 'B', 'W'])
def test_block_preserves_suffix_and_end(arm):
    decoder = Decoder(tables()['G4'])
    library = [{'tokens': [1, 18, 3]}, {'tokens': [1, 22, 7, 1, 18, 9]}]
    op = BlockOperator(arm, library, 843)
    original = np.random.default_rng(0).integers(24000, size=(256, 32), dtype=np.int32)
    changed, info = op.edit(original.copy(), decoder, force=True, boundary=True)
    decoded = decoder.decode(changed)
    assert np.array_equal(decoded, info['desired'])
    before = decoder.decode(original)
    for i, (s, L) in enumerate(zip(info['starts'], info['lengths'])):
        assert np.array_equal(decoded[i, :s], before[i, :s])
        assert np.array_equal(decoded[i, s + L:], before[i, s + L:])
        if s + L < 32:
            assert decoded[i, -1] == before[i, -1]
        assert np.array_equal(changed[i, s + L + 1:], original[i, s + L + 1:])
    assert op.stats['edited_children'] == 256


def test_B_breaks_joint_content_and_retains_marginals():
    decoder = Decoder(tables()['G4'])
    library = [{'tokens': [1, 2, 3]}, {'tokens': [4, 5, 6]}]
    op = BlockOperator('B', library, 843)
    original = np.zeros((10000, 32), dtype=np.int32)
    _, info = op.edit(original, decoder, force=True)
    windows = np.array([row[s:s + 3] for row, s in zip(info['desired'], info['starts'])])
    assert np.all(np.abs((windows == [1, 2, 3]).mean(axis=0) - .5) < .025)
    assert len(np.unique(windows, axis=0)) == 8


def test_operator_off_hook_preserves_scientific_search():
    inputs = [[i, i, i] for i in range(80)]
    job = ({'id': 'unreachable', 'labels': [99999] * 80}, 'C', tables()['G4'], 843, 768, 256, inputs, 'v2_rmin_first')
    baseline = search(job, return_solver=True)
    operator = BlockOperator('C', [], 843, inputs[:4])
    hooked = search(job, return_solver=True, child_transform=operator)
    for key in baseline:
        if key not in ('seconds', 'decode_seconds', 'budget_seconds'):
            assert baseline[key] == hooked[key]
    assert operator.stats['eligible_children'] == 2 * 254
    assert operator.stats['edited_children'] == 0


def test_trace_counts_inline_and_wrong_type_defaults():
    # DUP underflow creates two ints; INPUT leaves list on top, ADD defaults twice.
    from folding_evolution.chem_tape import executor as vm
    from experiments.chem_tape.composition_bank import TA
    dup_id = next(t for t in range(24) if vm.resolve_op(t, TA, 'v2_rmin_first') is vm._op_dup)
    add_id = next(t for t in range(24) if vm.resolve_op(t, TA, 'v2_rmin_first') is vm._op_add)
    result = trace([dup_id, 1, add_id], [[1, 2, 3]])
    assert result['totals']['underflow'] == 1
    assert result['totals']['wrong_type'] == 2
    assert result['totals']['default_use'] == 3


def test_roster_and_admission_fallback():
    full, smoke = schedule(32), smoke_schedule()
    assert len(full) == 8192 and len(smoke) == 128
    assert not {r['seed'] for r in full} & {r['seed'] for r in smoke}
    assert len({r['corpus'] for r in smoke}) == 16
    rows = [dict(arm=r['arm'], solved=True, seconds=15, evaluations=10000) for r in smoke]
    assert admit(rows, 120, 10)['selected_seeds'] == 24
    for r in rows:
        r['seconds'] = 30
    assert not admit(rows, 120, 10)['admitted']


def test_rule_precedence_and_unresolved_content():
    def stat(point, lo, hi):
        return dict(speed_ratio=point, interval_95=[lo, hi])
    comparisons = {'F/C': stat(1.2, 1.05, 1.4), 'F/B': stat(1.1, .95, 1.25), 'F/W': stat(1.1, .95, 1.25)}
    assert route(comparisons) == 'joint_content_unresolved'
    comparisons['F/W'] = stat(1.02, .96, 1.09)
    assert route(comparisons) == 'no_worthwhile_fragment_increment_over_W'
    comparisons['F/C'] = stat(1.01, .95, 1.09)
    assert route(comparisons) == 'ends_extractor_operator'


def test_complete_report_and_plotting(tmp_path):
    from experiments.chem_tape.fragment_report import report
    from experiments.chem_tape.fragment_run import CORPORA
    from experiments.chem_tape.comparison_gate_bank import TRAINING
    roster = schedule(16)
    stats = BlockOperator('C', [], 843).stats
    rows = [dict(r, solved=False, evaluations=524288, cap=524288, seconds=1,
                 solver=None, operator=stats.copy(), curve=[[256, 32, 8]]) for r in roster]
    libraries = {tid + '|' + cid: {'fragments': [{'tokens': [1, 2, 3]}]}
                 for tid in CORPORA for cid in TRAINING[tid[:2]]}
    preparation = {'admission': {'selected_seeds': 16, 'projected_seconds': 100}, 'reuse_price': {},
                   'resolution_cost': dict(source_collection_worker_seconds_per_corpus=10,
                                           fit_worker_seconds_per_corpus=1, library_worker_seconds_per_corpus=1,
                                           workers=10, reporting_queue_seconds=600, agent_hours=2.5)}
    result = report(tmp_path, rows, roster, libraries, preparation)
    assert result['comparisons']['F/C']['df'] == 15
    assert result['decision'] == 'ends_extractor_operator'
    assert (tmp_path / 'diagnostics.png').stat().st_size > 1000
    with pytest.raises(ValueError, match='incomplete'):
        report(tmp_path, rows[:-1], roster, libraries, preparation)
