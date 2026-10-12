"""Steward feasibility probe (<=10 min): fixed-law headroom for the content-choice design.

Existing engine only (order_run.execute, research/main 465f2fa). Laws, all at library
probability 0.5: O = 1228 semantic_all build b, G = 1938 semantic build b,
M = within-library-normalized 50/50 mixture of the two (entries replicated so each
library carries mass 1/2). One paired seed tuple per (family, build, cell).
Development cells of both banks only. Observations, not an efficacy pilot.
"""
import hashlib, json, multiprocessing as mp, sys, time
from pathlib import Path
from experiments.chem_tape.order_run import execute

ROOT = Path('/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11')
OUT = Path(__file__).with_name('rows.jsonl')
BANKS = {'order': ('2026-10-11-1228-prepare', 'semantic_all'), 'gate': ('2026-10-11-1938-prepare', 'semantic')}


def seed(*parts):
    raw = json.dumps(['steward-probe-2026-10-12-0250', *parts], separators=(',', ':'))
    return int.from_bytes(hashlib.sha256(raw.encode()).digest()[:8], 'big') & ((1 << 63) - 1)


def main(builds):
    libs = {k: json.loads((ROOT / f / 'libraries.json').read_text()) for k, (f, _) in BANKS.items()}
    lib = {k: [[e['prefix'] for e in libs[k][b][BANKS[k][1]]] for b in range(24)] for k in BANKS}
    jobs = []
    for fam, (folder, _) in BANKS.items():
        bank = json.loads((ROOT / folder / 'bank.json').read_text())
        cells = {c['id']: c for c in bank['screen']['cells']}
        for b in builds:
            o, g = lib['order'][b], lib['gate'][b]
            mix = o * len(g) + g * len(o)
            for c in bank['split']['development']:
                seeds = [seed(fam, b, c, k) for k in range(8)]
                for law, donors in (('O', o), ('G', g), ('M', mix)):
                    meta = dict(family=fam, build=b, cell=c, law=law, seeds=seeds)
                    jobs.append((meta, dict(id=c, labels=cells[c]['labels']), bank['inputs'], 65536, donors))
    start = time.monotonic()
    with mp.get_context('spawn').Pool(11) as pool, OUT.open('w') as f:
        for row in pool.imap_unordered(execute, jobs):
            row = {k: row[k] for k in ('family', 'build', 'cell', 'law', 'solved', 'evaluations', 'worker_seconds')} | \
                  dict(attempts=len(row['attempts']))
            f.write(json.dumps(row) + '\n'); f.flush()
    print('jobs', len(jobs), 'wall', round(time.monotonic() - start, 1))


if __name__ == '__main__':
    main(range(int(sys.argv[1])))
