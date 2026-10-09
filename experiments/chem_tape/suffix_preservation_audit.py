"""Matched W/R forced edits, including constructed neutral and endpoint edits."""

from collections import Counter

import numpy as np

from experiments.chem_tape.composition_search import Decoder
from experiments.chem_tape.fragment_operator import BlockOperator


def audit(corpora, libraries, n=10000):
    histogram = Counter()
    inside_histogram = Counter()
    coverage = Counter()
    for ci, tid in enumerate(sorted(corpora)):
        decoder = Decoder(corpora[tid]['tables']['C'])
        fragments = libraries[tid]['fragments']
        count = n // len(corpora) + (ci < n % len(corpora))
        original = np.random.default_rng([1606, ci]).integers(decoder.allele_range, size=(count, 32), dtype=np.int32)
        seed = 1606 + ci
        # First draw constructs deliberate no-op and same-final-token children.
        preview, info = BlockOperator('W', fragments, seed).edit(original.copy(), decoder, force=True, boundary=True)
        tokens = decoder.decode(original)
        for i, (s, length) in enumerate(zip(info['starts'], info['lengths'])):
            if i % 5 == 0:
                original[i, s:s + length] = preview[i, s:s + length]
            elif i % 5 == 1:
                tokens[i, s + length - 1] = info['desired'][i, s + length - 1]
                original[i] = decoder.encode(tokens[i:i + 1], np.random.default_rng([1606, ci, i]))[0]
        w, r = [BlockOperator(arm, fragments, seed) for arm in ('W', 'R')]
        preserved, wi = w.edit(original.copy(), decoder, force=True, boundary=True)
        rippled, ri = r.edit(original.copy(), decoder, force=True, boundary=True)
        if w.rng.bit_generator.state != r.rng.bit_generator.state:
            raise AssertionError('W/R RNG state mismatch on identical input')
        if not np.array_equal(wi['starts'], ri['starts']) or not np.array_equal(wi['lengths'], ri['lengths']):
            raise AssertionError('proposal draw mismatch')
        unrepaired = preserved.copy()
        for i, (s, length) in enumerate(zip(wi['starts'], wi['lengths'])):
            end = s + length
            if end < 32:
                unrepaired[i, end] = original[i, end]
        before, wd, rd, ud = [decoder.decode(a) for a in (original, preserved, rippled, unrepaired)]
        if not np.array_equal(rd, ud) or not np.array_equal(rd, ri['desired']):
            raise AssertionError('R does not decode to actual unrepaired output')
        measured_inside = 0
        measured_suffix = 0
        for i, (s, length) in enumerate(zip(wi['starts'], wi['lengths'])):
            end = s + length
            if not np.array_equal(wd[i, :end], rd[i, :end]) or not np.array_equal(preserved[i, s:end], rippled[i, s:end]):
                raise AssertionError('prefix or block changed between matched arms')
            if not np.array_equal(rd[i, :s], before[i, :s]):
                raise AssertionError('prefix ripple')
            if not np.array_equal(wd[i, end:], before[i, end:]):
                raise AssertionError('W repair changed')
            if not np.array_equal(rippled[i, end + 1:], original[i, end + 1:]):
                raise AssertionError('allele beyond boundary changed')
            if end < 32:
                token, previous = rd[i, end], rd[i, end - 1]
                low = 0 if token == 0 else decoder.table[previous, token - 1]
                if not low <= rippled[i, end] < decoder.table[previous, token]:
                    raise AssertionError('R boundary outside preimage')
            inside = int(np.count_nonzero(rd[i, s:end] != before[i, s:end]))
            suffix = int(np.count_nonzero(rd[i, end:] != before[i, end:]))
            measured_inside += inside
            measured_suffix += suffix
            inside_histogram[inside] += 1
            histogram[suffix] += 1
            coverage['edits'] += 1
            coverage['tape_start'] += int(s == 0)
            coverage['tape_end'] += int(end == 32)
            coverage['no_op_block'] += int(inside == 0)
            coverage['unchanged_final_block_token'] += int(rd[i, end - 1] == before[i, end - 1])
            if i % 5 == 0 and (inside or suffix):
                raise AssertionError('constructed no-op rippled')
            if i % 5 == 1 and rd[i, end - 1] != before[i, end - 1]:
                raise AssertionError('constructed final-token control failed')
        if r.stats['inside_changed_tokens'] != measured_inside or r.stats['suffix_changed_tokens'] != measured_suffix:
            raise AssertionError('diagnostics do not count actual block/suffix changes')
        actual_changes = int(np.count_nonzero(rd != before))
        if r.stats['changed_tokens'] != actual_changes or r.stats['inside_changed_tokens'] + r.stats['suffix_changed_tokens'] != actual_changes:
            raise AssertionError('diagnostics do not count actual suffix changes')
    if coverage['edits'] != n or any(coverage[k] == 0 for k in ('tape_start', 'tape_end', 'no_op_block', 'unchanged_final_block_token')):
        raise AssertionError('audit coverage missing')
    return dict(passed=True, seed=1606, coverage=dict(coverage), inside_histogram=dict(sorted(inside_histogram.items())),
                suffix_histogram=dict(sorted(histogram.items())), suffix_ripple_fraction=1 - histogram[0] / n,
                note='Constructed neutral controls included; histogram is an invariant audit, not the natural edit-rate estimate. Scoring logs natural R edits.')
