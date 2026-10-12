"""Read-only inventory of saved donors; no evolutionary search or efficacy test."""
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_suffix('.json')
BASE = ROOT / 'experiments/output/2026-10-11'
SOURCES = {
    'order': ('2026-10-11-1228-prepare', 'semantic_all'),
    'gate': ('2026-10-11-1938-prepare', 'semantic'),
}


def key(values):
    return hashlib.sha256(np.asarray(values, dtype='<i8').tobytes()).hexdigest()


def evaluate(prefix, inputs):
    def walk(i):
        op = prefix[i]
        i += 1
        if op < 4:
            return inputs[:, op], i
        if op == 4:
            return np.any(inputs, axis=1).astype(np.int64), i
        if op < 9:
            return np.full(len(inputs), (0, 1, 2, 5)[op - 5], dtype=np.int64), i
        args = []
        for _ in range(3 if op == 11 else 2):
            x, i = walk(i)
            args.append(x)
        if op == 9:
            return args[0] + args[1], i
        if op == 10:
            return (args[0] > args[1]).astype(np.int64), i
        assert op == 11
        return np.where(args[2] > 0, args[1], args[0]), i
    result, end = walk(0)
    assert end == len(prefix)
    return result


report = {'scope': 'static saved-artifact inventory; no search or efficacy measurement', 'cohorts': {}}
for name, (folder, field) in SOURCES.items():
    path = BASE / folder
    raw = (path / 'libraries.json').read_bytes()
    libs = json.loads(raw)
    bank = json.loads((path / 'bank.json').read_text())
    xs = np.asarray(bank['inputs'], dtype=np.int64)
    order = {key(fn(xs[:, a], xs[:, b])) for a, b in itertools.combinations(range(4), 2)
             for fn in (np.minimum, np.maximum)}
    gate = {key(np.where(xs[:, a] > 0, xs[:, b] if positive else 0,
                        0 if positive else xs[:, b]))
            for a, b in itertools.permutations(range(4), 2) for positive in (True, False)}
    rows = []
    for b, lib in enumerate(libs):
        entries = lib[field]
        hashes = [key(evaluate(e['prefix'], xs)) for e in entries]
        assert hashes == [e['semantic_hash'] for e in entries]
        rows.append(dict(build=b, entries=len(entries), order_helpers=len(set(hashes) & order),
                         gate_helpers=len(set(hashes) & gate)))
    report['cohorts'][name] = dict(path=str(path.relative_to(ROOT)), field=field,
        file_sha256=hashlib.sha256(raw).hexdigest(), builds=len(libs),
        development_cells=bank['split']['development'], rows=rows,
        means={k: float(np.mean([r[k] for r in rows]))
               for k in ('entries', 'order_helpers', 'gate_helpers')})
OUT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v['means'] for k, v in report['cohorts'].items()}, indent=2))
