"""Ten-worker full-cap smoke on development inputs (20 searches, no targets)."""
import multiprocessing as mp
import os
from pathlib import Path
import time

from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.independent_input_run import CAP
from experiments.chem_tape.tree_gp_search import search


def execute(job):
    meta, tree_job = job
    return search(tree_job, force_cap=True) | meta


def envelope(meta, saved):
    bank = saved['banks.json'][meta['family']]
    cell = next(c for c in bank['screen']['cells'] if c['id'] == meta['cell'])
    return meta, (cell, meta['seed'], CAP, 256, bank['inputs'], meta['crossover'])


def main():
    saved, _ = load_saved()
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    rows, batches = [], {}
    with mp.get_context('spawn').Pool(10) as pool:
        for fi, f in enumerate(('DG', 'TS')):
            metas = [dict(family=f, cell=saved['banks.json'][f]['split']['development'][i % 4],
                          arm='tree', phase='bench', seed=22160000 + 1000 * fi + 200 + i,
                          crossover=0.9) for i in range(10)]
            subset = []
            start = time.monotonic()
            assert run_jobs(pool, execute, [envelope(m, saved) for m in metas],
                            start + 300, subset.append)
            batches[f] = dict(wall_seconds=time.monotonic() - start,
                              worker_seconds=sum(r['seconds'] for r in subset),
                              mean_seconds=sum(r['seconds'] for r in subset) / len(subset),
                              max_seconds=max(r['seconds'] for r in subset))
            rows += subset
            write_json(out, 'benchmark.json', dict(rows=rows, batches=batches, targets_scored=False))
            print(f, batches[f], flush=True)


if __name__ == '__main__':
    main()
