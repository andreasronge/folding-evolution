"""Deterministic active-window extraction from pinned G4 collection solvers."""

from collections import Counter, defaultdict
from functools import lru_cache
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import TRAINING, digest
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.fragment_operator import trace
from folding_evolution.chem_tape.executor import resolve_op
from experiments.chem_tape.composition_bank import TA


def extract_corpus(envelope):
    tid, rows, inputs, cells, indices = envelope
    started = time.monotonic()
    sampled = [inputs[i] for i in indices]
    diagnostic_inputs = sampled[:4]
    candidates = defaultdict(list)
    activity = []
    for row in rows:
        tape = row['solver']
        if not row['solved']:
            continue
        mutants = np.tile(tape, (33, 1))
        mutants[np.arange(32) + 1, np.arange(32)] = 0
        observed = outputs(mutants, sampled, 'v2_rmin_first')
        active = np.any(observed[1:] != observed[0], axis=1)
        if not np.array_equal(outputs([tape], inputs, 'v2_rmin_first')[0], cells[row['cell']]['labels']):
            raise ValueError('source solver fails full-domain validation')
        activity.append(dict(cell=row['cell'], seed=row['seed'], active=active.tolist()))
        context = trace(tape, diagnostic_inputs)
        if [r['output'] for r in context['executions']] != observed[0, :4].tolist():
            raise ValueError('Python/Rust trace mismatch on source')
        for L in range(3, 7):
            for start in range(33 - L):
                if not active[start:start + L].all():
                    continue
                f = tuple(tape[start:start + L])
                metrics = Counter()
                deltas = []
                for execution in context['executions']:
                    positions = execution['positions'][start:start + L]
                    deltas.append(sum(p['stack_delta'] for p in positions))
                    for p in positions:
                        metrics.update({k: v for k, v in p.items() if k != 'stack_delta'})
                candidates[f].append(dict(cell=row['cell'], seed=row['seed'], start=start,
                                          context_inputs=4, context_stack_deltas=deltas,
                                          context_totals=dict(metrics)))

    @lru_cache(maxsize=None)
    def padded_solves(f):
        values = outputs([list(f) + [0] * (32 - len(f))], inputs, 'v2_rmin_first')[0]
        return [c for c in TRAINING[tid[:2]] if np.array_equal(values, cells[c]['labels'])]

    @lru_cache(maxsize=None)
    def standalone(f):
        result = trace(f, sampled)
        if [r['output'] for r in result['executions']] != outputs([list(f)], sampled, 'v2_rmin_first')[0].tolist():
            raise ValueError('Python/Rust trace mismatch on fragment')
        return dict(inputs=96, totals=result['totals'],
                    stack_effects=dict(Counter(str(r['stack_delta']) for r in result['executions'])),
                    final_stack_types=dict(Counter(','.join(r['final_stack_types']) for r in result['executions'])))

    def library(held):
        eligible = []
        for f, provenance in candidates.items():
            sources = [p for p in provenance if p['cell'] != held]
            source_cells = sorted({p['cell'] for p in sources})
            if len(source_cells) >= 2:
                eligible.append((f, sources, source_cells))
        eligible.sort(key=lambda x: (-len(x[2]), -len(x[1]), -len(x[0]), x[0]))
        retained, dropped = [], []
        for f, sources, source_cells in eligible:
            solves = padded_solves(f)
            if solves:
                dropped.append(dict(tokens=list(f), solves=solves))
                continue
            totals = Counter()
            for p in sources:
                totals.update(p['context_totals'])
            retained.append(dict(tokens=list(f), names=[resolve_op(t, TA, 'v2_rmin_first').__name__ for t in f],
                                 length=len(f), source_cells=source_cells, count=len(sources),
                                 provenance=sources, standalone=standalone(f),
                                 source_context_totals=dict(totals), padded_solves=solves))
            if len(retained) == 32:
                break
        return dict(held_out_cell=held, recurring_candidates=len(eligible), fragments=retained,
                    dropped_padded_solvers=dropped, hash=digest(retained),
                    activity_scope='NOP knockout contribution in the original source program on 96 inputs',
                    stack_scope='standalone empty-stack effect on 96 inputs; source-context use on first four of those inputs')

    libraries = {tid + '|' + held: library(held) for held in TRAINING[tid[:2]]}
    whole_started = time.monotonic()
    whole = library(None)
    return dict(corpus=tid, libraries=libraries, whole_corpus=whole, activity=activity,
                seconds=time.monotonic() - started, whole_build_seconds=time.monotonic() - whole_started)
