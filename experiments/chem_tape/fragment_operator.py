"""Literal fragment block edits, conditional-uniform inverse encoding, and stack audits."""

from collections import Counter

import numpy as np

from experiments.chem_tape.composition_bank import TA
from experiments.chem_tape.composition_search import Decoder
from folding_evolution.chem_tape import executor as vm

ARMS = ('C', 'F', 'B', 'W')
RATE = .2


def trace(tokens, inputs):
    """Actual preserve-on-mismatch execution; include DUP/SWAP's inline defaults.

    Stack effects are empirical from an empty stack, not a context-free type signature.
    No scoring code uses this monkeypatch; each worker is a single Python thread.
    """
    saved = vm.safe_pop
    saved_mode = vm._SAFE_POP_CONSUME
    vm._SAFE_POP_CONSUME = False
    records = []
    totals = Counter()
    try:
        for inp in inputs:
            stack, positions = [], []
            current = Counter()

            def counted(stack, expected):
                current['pop_calls'] += 1
                if not stack:
                    current['underflow'] += 1
                elif expected != 'any' and stack[-1][0] != expected:
                    current['wrong_type'] += 1
                return saved(stack, expected)

            vm.safe_pop = counted
            for token in tokens:
                current = Counter()
                op = vm.resolve_op(int(token), TA, 'v2_rmin_first')
                if op is vm._op_dup and not stack:
                    current['underflow'] += 1
                elif op is vm._op_swap:
                    current['underflow'] += max(0, 2 - len(stack))
                before = len(stack)
                op(stack, list(inp), 'intlist', TA)
                current['stack_delta'] = len(stack) - before
                current['default_use'] = current['underflow'] + current['wrong_type']
                positions.append(dict(current))
                totals.update({k: v for k, v in current.items() if k != 'stack_delta'})
            result = int(stack[-1][1]) if stack and stack[-1][0] == 'int' else 0
            records.append(dict(positions=positions, final_stack_types=[x[0] for x in stack],
                                stack_delta=len(stack), output=result))
    finally:
        vm.safe_pop = saved
        vm._SAFE_POP_CONSUME = saved_mode
    return dict(inputs=len(inputs), totals=dict(totals), executions=records)


class BlockOperator:
    def __init__(self, arm, library, seed, diagnostic_inputs=()):
        if arm not in ARMS:
            raise ValueError('unknown block arm')
        self.arm = arm
        self.rng = np.random.default_rng([seed, 4])
        self.fragments = np.asarray([r['tokens'] + [0] * (6 - len(r['tokens'])) for r in library], dtype=np.uint8)
        self.lengths = np.array([len(r['tokens']) for r in library])
        if arm != 'C' and not len(library):
            raise ValueError('empty block library')
        self.by_length = {L: self.fragments[self.lengths == L, :L] for L in sorted(set(self.lengths))}
        self.inputs = diagnostic_inputs
        self.stats = dict(eligible_children=0, edited_children=0, span_tokens=0, changed_tokens=0,
                          changed_histogram=[0] * 7, span_histogram=[0] * 7,
                          sampled_offspring=0, sampled_inputs=0, offspring_underflow=0,
                          offspring_wrong_type=0, offspring_default_use=0)

    def edit(self, child, decoder, *, force=False, boundary=False):
        self.stats['eligible_children'] += len(child)
        if self.arm == 'C':
            return child, None
        ix = np.arange(len(child)) if force else np.flatnonzero(self.rng.random(len(child)) < RATE)
        if not len(ix):
            return child, None
        before = decoder.decode(child[ix])
        desired = before.copy()
        draw = self.rng.integers(len(self.fragments), size=len(ix))
        lengths = self.lengths[draw]
        starts = self.rng.integers(0, 33 - lengths)
        if boundary:
            starts[::4] = 0
            starts[1::4] = 32 - lengths[1::4]
        for L in self.by_length:
            rows = np.flatnonzero(lengths == L)
            if not len(rows):
                continue
            positions = starts[rows, None] + np.arange(L)
            if self.arm == 'F':
                block = self.fragments[draw[rows], :L]
            elif self.arm == 'B':
                source = self.by_length[L]
                sampled = self.rng.integers(len(source), size=(len(rows), L))
                block = source[sampled, np.arange(L)]
            else:
                block = np.empty((len(rows), L), dtype=np.uint8)
                previous = np.where(starts[rows] == 0, decoder.n_tokens,
                                    before[rows, np.maximum(starts[rows] - 1, 0)])
                for j in range(L):
                    block[:, j] = decoder.lookup[previous, self.rng.integers(decoder.allele_range, size=len(rows))]
                    previous = block[:, j]
            desired[rows[:, None], positions] = block
        # Repair next allele under the final new token, retaining its old decoded token.
        lower = np.concatenate((np.zeros((decoder.n_tokens + 1, 1), dtype=np.int64), decoder.table[:, :-1]), axis=1)
        for j in range(7):
            rows = np.flatnonzero((j <= lengths) & (starts + j < 32))
            if not len(rows):
                continue
            pos = starts[rows] + j
            token = desired[rows, pos]
            previous = np.where(pos == 0, decoder.n_tokens, desired[rows, np.maximum(pos - 1, 0)])
            child[ix[rows], pos] = self.rng.integers(lower[previous, token], decoder.table[previous, token], dtype=np.int32)
        changes = np.sum(before != desired, axis=1)
        self.stats['edited_children'] += len(ix)
        self.stats['span_tokens'] += int(lengths.sum())
        self.stats['changed_tokens'] += int(changes.sum())
        for key, vals in (('changed_histogram', changes), ('span_histogram', lengths)):
            self.stats[key] = (np.array(self.stats[key]) + np.bincount(vals, minlength=7)).tolist()
        return child, dict(indices=ix, before=before, desired=desired, lengths=lengths, starts=starts)

    def __call__(self, child, decoder, generation):
        child, _ = self.edit(child, decoder)
        # Deterministic sparse diagnostic sample; consumes no search/operator draws.
        if self.inputs and generation % 32 == 0:
            sample = decoder.decode(child[:1])[0]
            measured = trace(sample, self.inputs)
            self.stats['sampled_offspring'] += 1
            self.stats['sampled_inputs'] += len(self.inputs)
            for key in ('underflow', 'wrong_type', 'default_use'):
                self.stats['offspring_' + key] += measured['totals'].get(key, 0)
        return child


def validate_edits(corpora, libraries, n=10000):
    """End-to-end invariants across all 64 libraries; 10k forced edits per arm."""
    result = {}
    keys = sorted(libraries)
    for arm in ARMS[1:]:
        done, starts_count, ends_count = 0, 0, 0
        for i, key in enumerate(keys):
            count = n // len(keys) + (i < n % len(keys))
            decoder = Decoder(corpora[key.split('|')[0]]['tables']['C'])
            original = np.random.default_rng([202610090845, i]).integers(decoder.allele_range, size=(count, 32), dtype=np.int32)
            op = BlockOperator(arm, libraries[key]['fragments'], 202610090845 + i)
            changed, info = op.edit(original.copy(), decoder, force=True, boundary=True)
            actual = decoder.decode(changed)
            before = decoder.decode(original)
            if not np.array_equal(actual, info['desired']):
                raise AssertionError('inverse encoding did not preserve desired tape')
            for k, (start, L) in enumerate(zip(info['starts'], info['lengths'])):
                outside = np.ones(32, dtype=bool)
                outside[start:start + L] = False
                if not np.array_equal(actual[k, outside], before[k, outside]):
                    raise AssertionError('outside-window tokens changed (including end)')
                untouched = outside.copy()
                if start + L < 32:
                    untouched[start + L] = False
                if not np.array_equal(changed[k, untouched], original[k, untouched]):
                    raise AssertionError('outside alleles beyond repair changed')
                for pos in range(start, min(32, start + L + 1)):
                    previous = 24 if pos == 0 else actual[k, pos - 1]
                    token = actual[k, pos]
                    lo = 0 if token == 0 else decoder.table[previous, token - 1]
                    if not lo <= changed[k, pos] < decoder.table[previous, token]:
                        raise AssertionError('allele escaped conditional preimage')
            starts_count += int(np.count_nonzero(info['starts'] == 0))
            ends_count += int(np.count_nonzero(info['starts'] + info['lengths'] == 32))
            done += count
        if done != n:
            raise AssertionError('edit audit count')
        result[arm] = dict(passed=True, edits=done, tape_start=starts_count, tape_end=ends_count)
    return result
