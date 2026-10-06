"""Frozen provenance and deterministic pooled-frequency controls for 1425."""

import hashlib
import json
from pathlib import Path

import numpy as np

from experiments.chem_tape.assembly_maps import frozen_controls
from experiments.chem_tape.composition_search import Decoder, outputs, R
from experiments.chem_tape.contextual_learning import table
from experiments.chem_tape.contextual_learning_run import SOURCES
from experiments.chem_tape.map_learning import BOUND, MIN_COUNT, log_cost, normalize

OUTPUT_ROOT = Path('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-06')
FILES = {
    'starts': ('2026-10-06-0132-post-addition-map-learning/final_maps.json',
               '2cf5c89885cf9e0dc3215dfbecfe2ca1f1c8670eb33e803ea67e7c2de9987506'),
    'continuations': ('2026-10-06-0811-contextual-continuation/final_maps.json',
                      'be9bf84da981c94d0022777f1e271d0156e4045625fadc65779ee9954f0efbfe'),
    'prior_search': ('2026-10-06-0811-contextual-continuation/search.jsonl',
                     '05ad282021b0a96155238cb41f13d2cff20c27d95c6c3b40c529e3085dc33440'),
    'prior_config': ('2026-10-06-0811-contextual-continuation/config.json',
                     '5a4ce04e2a048a29bb1b6110807f9a8dc7098c709404c080394d32ccefae9188'),
}
SOURCES_HASH = 'cf43411ad46419db4f312c3f06c7fe97f3145ff4e017640aa1951b1c28d05bbe'


def checked_bytes(path, expected):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f'source hash mismatch: {path}')
    return data


def emitted_counts(counts, length=32):
    """Exact expectation under independent uniform alleles; START is row 23."""
    p = counts / counts.sum(axis=1, keepdims=True)
    d = p[23].copy()
    total = d.copy()
    for _ in range(length - 1):
        d = d @ p[:23]
        total += d
    return total / length


def emitted(t):
    return emitted_counts(np.diff(t, prepend=0, axis=1).astype(float))


def float_counts(weights):
    """Continuous production water filling, used only during proportional fit."""
    fixed = np.zeros_like(weights, dtype=bool)
    while True:
        shares = weights * ((R - MIN_COUNT * fixed.sum(1)) /
                            np.where(fixed, 0, weights).sum(1))[:, None]
        shares[fixed] = MIN_COUNT
        new = (~fixed) & (shares < MIN_COUNT)
        if not new.any():
            return shares
        fixed |= new


def fit_frequency(target, g):
    weights = np.diff(g, prepend=0, axis=1).astype(float)
    vector = np.zeros(23)
    # Match the approved steward probe exactly; no scoring or search selection.
    for _ in range(3000):
        current = emitted_counts(float_counts(weights * np.exp(vector)[None, :]))
        vector = np.clip(vector + 0.5 * np.log(target / current), -BOUND, BOUND)
    fitted = normalize(weights * np.exp(vector)[None, :])
    frequencies = emitted(fitted)
    tv = float(np.abs(target - frequencies).sum() / 2)
    return dict(table=fitted.tolist(), table_hash=Decoder(fitted).hash(),
                vector=vector.tolist(), emitted_frequencies=frequencies.tolist(),
                tv=tv, accepted=tv < 0.005,
                at_bound=int(np.count_nonzero(np.abs(vector) >= BOUND - 1e-6)))


def load_saved(inputs):
    raw = {key: checked_bytes(OUTPUT_ROOT / name, sha)
           for key, (name, sha) in FILES.items()}
    sources = json.loads(checked_bytes(SOURCES, SOURCES_HASH))
    cells = sources['off_family']['cells']
    if len(cells) != 8 or [c['shape'] for c in cells].count('BE') != 2:
        raise ValueError('invalid frozen cell bank')
    for c in cells:
        if not c['retained'] or c['shape'] == 'PA':
            raise ValueError('invalid off-family cell')
        sha = hashlib.sha256(np.asarray(c['labels'], dtype='<i8').tobytes()).hexdigest()
        if sha != c['label_hash'] or not np.array_equal(outputs([c['canonical']], inputs)[0], c['labels']):
            raise ValueError(f'cell verification failed: {c["id"]}')
    controls = frozen_controls()
    g = controls['G']
    prior_g = json.loads(raw['prior_config'])['controls']['G']
    if Decoder(g).hash() != prior_g['hash'] or not np.array_equal(g, prior_g['table']):
        raise ValueError('G hash mismatch')
    starts, continuations = (json.loads(raw[k]) for k in ('starts', 'continuations'))
    maps = {'G': dict(table=g.tolist(), table_hash=Decoder(g).hash())}
    maps.update({f'M{k}': starts[f'M{k}'] for k in range(1, 7)})
    maps.update(continuations)
    expected = {f'{a}{k}{rep}' for a in ('M+', 'R', 'R_abl')
                for k in range(1, 7) for rep in ('a', 'b')}
    if set(continuations) != expected:
        raise ValueError('missing or unexpected continuation maps')
    for name, record in maps.items():
        if Decoder(record['table']).hash() != record['table_hash']:
            raise ValueError(f'map hash mismatch: {name}')
        if name != 'G' and not np.array_equal(table(record['vector'], controls), record['table']):
            raise ValueError(f'vector/table mismatch: {name}')
        record['emitted_frequencies'] = emitted(record['table']).tolist()
    fits = {}
    for rep in ('b', 'a'):
        for k in range(1, 7):
            pair = f'{k}{rep}'
            if not np.array_equal(continuations[f'R{pair}']['vector'][:23],
                                  continuations[f'R_abl{pair}']['vector']):
                raise ValueError(f'ablation multiplier mismatch: {pair}')
            fit = fit_frequency(np.array(maps[f'R{pair}']['emitted_frequencies']), g)
            fits[pair] = fit
            if fit['accepted']:
                maps[f'R_fm{pair}'] = fit
    prior = [json.loads(line) for line in raw['prior_search'].splitlines()]
    costs = {}
    for c in cells:
        rows = [r for r in prior if r['arm'] == 'G' and r['cell'] == c['id']
                and r['phase'].startswith('test:off:')]
        if len(rows) != 50 or len({r['seed'] for r in rows}) != 50:
            raise ValueError('incomplete prior G reference')
        if any(r['table_hash'] != prior_g['hash'] or r['cap'] != 524288 for r in rows):
            raise ValueError('prior G harness mismatch')
        costs[c['id']] = float(np.mean([log_cost(r, 524288) for r in rows]))
    provenance = {key: dict(path=str(OUTPUT_ROOT / name), sha256=sha)
                  for key, (name, sha) in FILES.items()}
    provenance['cells'] = dict(path=str(SOURCES), sha256=SOURCES_HASH)
    return maps, cells, fits, costs, provenance
