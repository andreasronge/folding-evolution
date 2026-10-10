"""2239 frozen schedule audit. Seed disjointness failure blocks preparation.

No calibration or target scorer is provided for this infeasible design. The
approved seed formulas are deliberately preserved for steward/reviewer audit.
"""
import json
import os
from pathlib import Path
import subprocess

from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.tree_gp_search import MIXES

TASK = '2026-10-10-2239'


def schedules(banks, targets):
    calibration, scoring = [], []
    for fi, family in enumerate(('DG', 'TS')):
        cells = banks[family]['split']['source'] + banks[family]['split']['development']
        if len(cells) != 8 or set(cells) & set(targets[family]):
            raise ValueError('calibration/target split changed')
        for ci, cid in enumerate(cells):
            for repeat in range(8):
                for mix in MIXES:
                    calibration.append(dict(family=family, cell=cid, arm='tree',
                                            repeat=repeat, crossover=mix, phase='calibration',
                                            seed=22140000 + 1000 * (8 * fi + ci) + repeat))
        for ci, cid in enumerate(targets[family]):
            for build in range(24):
                for repeat in range(2):
                    for arm in ('A8', 'tree'):
                        scoring.append(dict(family=family, cell=cid, arm=arm, build=build,
                                            repeat=repeat, phase='target',
                                            seed=22150000 + 1000 * (8 * fi + ci) + 2 * build + repeat))
            for repeat in range(16):
                scoring.append(dict(family=family, cell=cid, arm='G4', build=None,
                                    repeat=repeat, phase='target',
                                    seed=22150000 + 1000 * (8 * fi + ci) + 100 + repeat))
    return calibration, scoring



def audit_seeds(calibration, score):
    cal = {r['seed'] for r in calibration}
    target = {r['seed'] for r in score}
    smoke = {22160000, 22161000}
    overlap = sorted(cal & target)
    smoke_overlap = sorted(smoke & target)
    implicated = [r for r in calibration if r['seed'] in overlap]
    scored = [r for r in score if r['seed'] in overlap]
    return dict(task=TASK, admitted=not overlap and not smoke_overlap,
                calibration_searches=len(calibration), target_searches=len(score),
                calibration_unique_seeds=len(cal), target_unique_seeds=len(target),
                calibration_scoring_overlap=overlap, smoke_scoring_overlap=smoke_overlap,
                implicated_calibration_rows=len(implicated), implicated_scoring_rows=len(scored),
                calibration_examples=implicated[:4], scoring_examples=scored[:4],
                targets_scored=False)


def main():
    saved, targets = load_saved()
    calibration, score = schedules(saved['banks.json'], targets)
    result = audit_seeds(calibration, score)
    result['git_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    out = Path(os.environ['RUN_DIR'])
    out.mkdir(parents=True, exist_ok=True)
    write_json(out, 'schedule_audit.json', result)
    write_json(out, 'calibration_schedule.json', calibration)
    write_json(out, 'target_schedule.json', score)
    print(json.dumps(result, indent=2), flush=True)
    if not result['admitted']:
        raise SystemExit('Seed disjointness gate failed; no calibration or scoring. Return to strategy.')


if __name__ == '__main__':
    main()
