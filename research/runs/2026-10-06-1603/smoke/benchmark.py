import json
import multiprocessing as mp
import os
from pathlib import Path
import time
from types import SimpleNamespace
from experiments.chem_tape.composition_run import run_jobs
from experiments.chem_tape.composition_search import search
from experiments.chem_tape.assembly_bank import inputs_for
from experiments.chem_tape.four_reducer_bank import ALPHABET
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.four_reducer_run import Runner


def main():
    out=Path(__file__).parent
    os.environ['RAYON_NUM_THREADS']='1'
    screen=json.loads((out/'full_screen.json').read_text())
    ids=['BE:F?S:(M+m)','BE:S?m:(M+F)','PA:(F?m:S)+M','PA:(S?M:m)+F']
    cells=[c for c in screen['cells'] if c['id'] in ids]
    ts=tables()
    jobs=[(c,a,t,1603900+s,524288,256,inputs_for('D1331'),ALPHABET)
          for s in range(2) for c in cells for a,t in ts.items()]
    tick=time.monotonic(); rows=[]
    ctx=mp.get_context('spawn')
    with ctx.Pool(10) as pool:
        assert run_jobs(pool,search,jobs,time.monotonic()+600,rows.append)
    result=dict(wall_seconds=time.monotonic()-tick,rows=rows)
    (out/'full_cap_benchmark.json').write_text(json.dumps(result,indent=2)+'\n')
    print('BENCH',result['wall_seconds'],len(rows),flush=True)
    for a in ts:
        rs=[r for r in rows if r['arm']==a]
        print(a,'solves',sum(r['solved'] for r in rs),'/',len(rs),
              'mean_seconds',sum(r['seconds'] for r in rs)/len(rs),flush=True)
    os.environ['RUN_DIR']=str(out/'actual_pilot')
    runner=Runner(SimpleNamespace(smoke=True,cap=256,deadline_seconds=600,workers=2))
    runner.bank=cells
    runner.splits={f:dict(training=[c['id'] for c in cells if c['shape']==f]) for f in ('BE','PA')}
    runner.pool=ctx.Pool(2)
    try:
        for f in ('BE','PA'):
            runner.evolve(f,0)
        print('PILOT', {k:v['seconds'] for k,v in runner.pilot.items()},flush=True)
    finally:
        runner.pool.terminate(); runner.pool.join()


if __name__=='__main__':
    main()
