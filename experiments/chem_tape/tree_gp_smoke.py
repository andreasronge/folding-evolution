"""Complete production-cap search smoke on development cells, never targets."""
import os
from pathlib import Path

from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.independent_input_run import CAP
from experiments.chem_tape.tree_gp_search import search


def main():
    saved, _ = load_saved()
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for fi, family in enumerate(('DG', 'TS')):
        bank = saved['banks.json'][family]
        cid = bank['split']['development'][0]
        cell = next(c for c in bank['screen']['cells'] if c['id'] == cid)
        job = (cell, 22160000 + 1000 * fi, CAP, 256, bank['inputs'], 0.9)
        row = search(job)
        replay = search(job)
        ignored = {'seconds', 'budget_seconds', 'compile_seconds', 'variation_seconds',
                   'exact_check_seconds', 'exact_check_max_seconds'}
        assert all(row[k] == replay[k] for k in row if k not in ignored)
        row['family'] = family
        row['deterministic_replay_passed'] = True
        rows.append(row)
        write_json(out, 'search_smoke.json', rows)
        print(f"{family}: solved={row['solved']} evaluations={row['evaluations']} seconds={row['seconds']:.2f}", flush=True)


if __name__ == '__main__':
    main()
