"""1350 SHA-pinned archive interface; never disguise partial tapes as solvers."""

import hashlib
import json
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.comparison_gate_bank import BANK_SHA, TRAINING, digest
from experiments.chem_tape.composition_search import outputs
from experiments.chem_tape.fragment_library import extract_windows
from experiments.chem_tape.solver_corpus_fit import seed_for

PROVENANCE = Path(__file__).with_name('data') / 'pre_solve_1350' / 'provenance.json'
CHECKPOINTS = (64, 128, 256)


def load_sources():
    raw = PROVENANCE.read_bytes()
    provenance = json.loads(raw)
    saved = {}
    for kind, record in provenance.items():
        saved[kind] = {}
        for name, sha in record['sha256'].items():
            data = (Path(record['path']) / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != sha:
                raise ValueError(f'{kind} source SHA mismatch: {name}')
            saved[kind][name] = ([json.loads(line) for line in data.splitlines()]
                                 if name == 'search.jsonl' else json.loads(data))
    partial = saved['partial']
    config, freeze = partial['config.json'], partial['freeze.json']
    if (not freeze['complete'] or freeze['smoke_only'] or config['smoke_only']
            or freeze['bank_sha256'] != BANK_SHA
            or freeze['schedule_hash'] != digest(partial['schedule.json'])
            or freeze['method_hash'] != digest(config['method'])):
        raise ValueError('partial collection freeze changed')
    expected = {(f'{f}{k + 1}', cid, seed_for(0, f, k, ci, si, 202610081831))
                for f in TRAINING for k in range(8) for ci, cid in enumerate(TRAINING[f])
                for si in range(32)}
    collection = [r for r in partial['search.jsonl'] if r['phase'] == 'collection']
    if (len(collection) != len(expected)
            or {(r['corpus'], r['cell'], r['seed']) for r in collection} != expected
            or any(r['arm'] != 'G4' or r['family'] != r['corpus'][:2]
                   or r['cap'] != 65536 or r['pop_size'] != 256 for r in collection)):
        raise ValueError('partial collection attempts missing/duplicated/changed')
    return collection, saved['historical'], provenance, hashlib.sha256(raw).hexdigest()


def select_sources(rows):
    """Stable minimum-slot selection, without inspecting accuracy/eventual solve."""
    selected, attempts = [], []
    for r in sorted(rows, key=lambda r: (r['cell'], r['seed'])):
        first = r['generations'] if r['solved'] else None
        if r['evaluations'] != r['generations'] * 256:
            raise ValueError('source first-solve/evaluation inconsistency')
        archive = r['archive']
        for a in archive:
            cp = a['checkpoint']
            if (cp not in CHECKPOINTS or a['evaluations'] != cp * 256
                    or cp > r['generations'] or first is not None and cp >= first
                    or a['exact'] is not False or a['cell'] != r['cell']
                    or a['source_seed'] != r['seed']
                    or a['source_later_solved'] != r['solved']
                    or len(a['tape']) != 32 or any(not 0 <= t < 24 for t in a['tape'])
                    or a['kind'] not in ('S', 'P')):
                raise ValueError('archive temporal/non-exactness metadata invalid')
        kept = []
        for cp in CHECKPOINTS:
            candidates = [a for a in archive if a['kind'] == 'S' and a['checkpoint'] == cp]
            if not candidates:
                continue
            # Stable tie: the archive's first row at the lowest slot, as in the probe.
            a = min(candidates, key=lambda a: a['slot'])
            row = dict(cell=r['cell'], seed=r['seed'], checkpoint=cp, slot=a['slot'],
                       population_index=a['population_index'], tape=a['tape'],
                       saved_d1331_correct=a['d1331_correct'], first_solve_generation=first)
            selected.append(row)
            kept.append(cp)
        attempts.append(dict(cell=r['cell'], seed=r['seed'], later_solved=r['solved'],
                             first_solve_generation=first, generations=r['generations'],
                             evaluations=r['evaluations'], archive_rows=len(archive),
                             selected_checkpoints=kept,
                             missing_checkpoints=[cp for cp in CHECKPOINTS if cp not in kept],
                             worker_seconds=r['worker_seconds'],
                             archive_verification_seconds=r['archive_verification_seconds']))
    return selected, attempts


def extract_partial(envelope):
    tid, rows, inputs, cells, indices = envelope
    started = time.monotonic()
    selected, attempts = select_sources(rows)
    # Re-evaluate selected source tapes on the full domain, independently of archive labels.
    values = outputs([r['tape'] for r in selected], inputs, 'v2_rmin_first') if selected else []
    for r, value in zip(selected, values):
        correct = int(np.sum(value == cells[r['cell']]['labels']))
        if correct == len(inputs) or correct != r['saved_d1331_correct']:
            raise ValueError('selected partial tape exact or archive accuracy/backend changed')
    built = extract_windows(tid, selected, inputs, cells, indices, partial=True)
    lib = built['whole_corpus']
    built['manifest'] = dict(corpus=tid, attempts=attempts, selected_tapes=selected,
                            selected_tapes_hash=digest(selected), tapes=len(selected),
                            distinct_tapes=len({tuple(r['tape']) for r in selected}),
                            empty_attempts=sum(not r['selected_checkpoints'] for r in attempts),
                            source_searches=len(attempts),
                            ranking='-distinct_cells,-raw_occurrences,-length,tokens',
                            duplicates='positions and checkpoints counted separately',
                            library_size=len(lib['fragments']),
                            selected_full_domain_nonexact_checked=len(selected))
    built['seconds'] = time.monotonic() - started
    return built
