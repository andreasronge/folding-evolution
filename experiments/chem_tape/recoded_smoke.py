"""0537 small recoding smoke and read-only audit of promised solver availability.

This is not a full-run scorer. The full preparation recovers missing C tapes via bit-exact historical replay.
Output goes exclusively under RUN_DIR.
"""

import gzip
import hashlib
import json
import os
from pathlib import Path
import time

import numpy as np

from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.composition_search import search
from experiments.chem_tape.four_reducer_maps import R
from experiments.chem_tape.frequency_matched_run import deterministic, historical_source, key
from experiments.chem_tape.position_matched import decoder_for
from experiments.chem_tape.then_addition_run import frozen_source
from experiments.chem_tape import then_addition_bank as bank_module
from experiments.chem_tape.recoded import METHOD, RecodedDecoder, audit

DATA = Path(__file__).with_name('data') / 'recoded_0537'
Q_PROVENANCE_SHA = 'c84b8375c483cabed8bfdaa06e5f32b64f8a3b7eb9a49223b667615604a5b8ce'


def q_source():
    raw = (DATA / 'provenance.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != Q_PROVENANCE_SHA:
        raise ValueError('Q provenance mismatch')
    provenance = json.loads(raw)
    saved = {}
    for name, sha in provenance['sha256'].items():
        path = DATA / name
        raw = path.read_bytes() if path.exists() else gzip.decompress((DATA / (name + '.gz')).read_bytes())
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError('Q source SHA mismatch: ' + name)
        saved[name] = [json.loads(r) for r in raw.splitlines()] if name == 'search.jsonl' else json.loads(raw)
    if (saved['metadata.json']['git_dirty'] or saved['metadata.json']['status'] != 'done'
        or saved['config.json']['git_commit'] != provenance['commit']
        or saved['metadata.json']['git_commit'] != provenance['commit']
        or not saved['validation.json']['passed']):
        raise ValueError('Q source not clean/completed/validated')
    return saved


def main():
    started = time.monotonic()
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'smoke.json').exists():
        raise ValueError('use a fresh RUN_DIR')
    saved, _ = frozen_source()
    q_saved = q_source()
    source_rows = saved['search.jsonl']
    c_rows = [r for r in source_rows if r['phase'] == 'training' and r['arm'] == 'C']
    g4_solvers = [r for r in source_rows if r['phase'] == 'collection' and r['arm'] == 'G4' and r.get('solver')]
    availability = dict(C_searches=len(c_rows), C_solved=sum(r['solved'] for r in c_rows),
                        C_rows_with_solver_field=sum('solver' in r for r in c_rows),
                        C_saved_solver_tapes=sum(bool(r.get('solver')) for r in c_rows),
                        G4_collection_solver_tapes=len(g4_solvers),
                        G4_corpora=len({r['corpus'] for r in g4_solvers}),
                        G4_collection_evaluations=sum(r['evaluations'] for r in source_rows if r['phase'] == 'collection'))
    write_json(out, 'source_audit.json', availability)
    bank, cells = bank_module.load()
    _, _, c_index = historical_source(saved['corpora.json'], saved['freeze.json'], bank)
    q_index = {key(r): r for r in q_saved['search.jsonl'] if r['arm'] == 'Q'}
    # One paired historical row in one corpus: smoke, not the full 32-row gate.
    ref = next(r for r in q_saved['schedule.json'] if r['arm'] == 'Q' and r['corpus'] == 'BE1')
    table = q_saved['projected_tables.json']['BE1']['Q']
    base = np.random.default_rng(202610090537).integers(R, size=(4096, 32), dtype=np.int32)
    result = dict(method=METHOD, source_audit=availability, maps={}, replays={}, small_searches=[],
                  scope='one-corpus implementation smoke only; no efficacy inference; C tapes require deterministic recovery')
    for arm in ('Q', 'C'):
        t = table if arm == 'Q' else saved['corpora.json']['BE1']['tables']['C']
        job = (cells[ref['cell']], arm, t, ref['seed'], 524288, 256, bank['inputs'], bank['alphabet'])
        row = search(job, decoder_factory=decoder_for)
        row.update({k: ref[k] for k in ('phase', 'family', 'corpus')})
        historical = (q_index if arm == 'Q' else c_index)[key(row)]
        if deterministic(row) != deterministic(historical):
            raise ValueError('historical smoke replay failed: ' + arm)
        result['replays'][arm] = dict(passed=True, evaluations=row['evaluations'], seconds=row['seconds'])
    for dose in (0, 30, 100):
        tick = time.monotonic()
        d = RecodedDecoder(dict(table=table, corpus='BE1', dose=dose, k=0))
        checks = d.validate()
        checks['validation_wall_seconds'] = time.monotonic() - tick
        initial = np.random.default_rng([ref['seed'], 1]).integers(R, size=(256, 32), dtype=np.int32)
        h = hashlib.sha256(d.decode(d.recode(initial)).tobytes()).hexdigest()
        if h != q_index[key(ref)]['initial_tokens_hash']:
            raise ValueError('generation-zero tape hash mismatch')
        # Exercise conditional-uniform encoding on arbitrary actual saved tapes;
        # these are explicitly G4-derived and do not stand in for C's missing audit.
        sample = np.asarray([r['solver'] for r in g4_solvers[:32]], dtype=np.uint8)
        encoded = d.encode(sample, np.random.default_rng([537, 999]))
        checks.update(initial_hash_equal=True, encoded_sample_tapes=len(encoded),
                      uniform_variation=audit(d, d.recode(base), 202610090537))
        result['maps'][str(dose)] = checks
        job = (cells[ref['cell']], f'R{dose}', None, ref['seed'], 4096, 256, bank['inputs'], bank['alphabet'])
        row = search(job, decoder_factory=lambda _: d, initial_transform=lambda pop, dec: dec.recode(pop))
        if row['initial_tokens_hash'] != h or row['training_indices'] != q_index[key(ref)]['training_indices']:
            raise ValueError('small search pairing mismatch')
        result['small_searches'].append(row)
    result['wall_seconds'] = time.monotonic() - started
    result['implementation_smoke_passed'] = True
    result['full_design_feasible'] = None
    write_json(out, 'smoke.json', result)
    print(json.dumps(dict(source_audit=availability, wall_seconds=result['wall_seconds'],
                          implementation_smoke_passed=True, full_design_feasible=None)), flush=True)


if __name__ == '__main__':
    main()
