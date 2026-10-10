"""Replay diagnostic timing only, then demonstrate smoke-handoff refusal."""
import argparse
import json
import multiprocessing as mp
import os
from pathlib import Path

from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.source_replication_run import Runner

TASK=Path('/Users/andreas/developer/folding-evolution/research/runs/2026-10-10-0145')

def main():
    os.environ['RUN_DIR']=str(TASK/'smoke_replay')
    runner=Runner(argparse.Namespace(smoke=True,prepare=False,preparation=None,workers=10,deadline_seconds=300))
    runner.builds=json.loads((TASK/'smoke/builds.json').read_text())
    prep=json.loads((TASK/'smoke/preparation.json').read_text())
    schedule=[r for r in runner.timing if r['corpus'] in ('BE1','PA1')]
    with mp.get_context('spawn').Pool(10) as pool:
        runner.pool=pool
        replay=runner.jobs(schedule,'timing_replay.jsonl')
    assert runner.scientific(replay)==runner.scientific(prep['timing_rows'])
    os.environ['RUN_DIR']=str(TASK/'smoke_refusal')
    scorer=Runner(argparse.Namespace(smoke=False,prepare=False,preparation=str(TASK/'smoke/preparation.json'),workers=10,deadline_seconds=300))
    try:
        scorer.score()
    except ValueError as error:
        assert str(error)=='changed/smoke/incomplete handoff'
    else:
        raise AssertionError('smoke was admitted')
    write_json(TASK,'smoke_validation.json',dict(passed=True,scientific_timing_replay_rows=len(replay),smoke_scoring_refused=True))

if __name__=='__main__':
    main()
