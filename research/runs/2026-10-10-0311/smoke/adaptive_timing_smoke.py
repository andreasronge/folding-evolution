"""Four full-cap fitted-path source timings; not sustained-load admission."""
import json,multiprocessing as mp,time
from pathlib import Path
from experiments.chem_tape.composition_run import run_jobs,write_json
from experiments.chem_tape.independent_input_run import execute,load_frozen,method_hashes,ALPHABET,CAP

if __name__=='__main__':
    out=Path(__file__).parent
    bank,_=load_frozen(); build=json.loads((out/'nonempty_build.json').read_text()); cells={c['id']:c for c in bank['screen']['cells']}
    schedule=[dict(alphabet=ALPHABET,phase='adaptive_timing_smoke',build=0,cell=cid,arm='A8',seed=440100+ci) for ci,cid in enumerate(bank['split']['source'])]
    write_json(out,'adaptive_timing_freeze.json',dict(alphabet=ALPHABET,method_hashes=method_hashes(),schedule=schedule,build_hash=__import__('experiments.chem_tape.comparison_gate_bank',fromlist=['digest']).digest(build),scope='four small-scale fitted-path source timings; not sustained-load admission'))
    envs=[((cells[r['cell']],r['arm'],build['table'],r['seed'],CAP,256,bank['inputs'],ALPHABET),r,build['library']['fragments'],bank['inputs'][:4]) for r in schedule]
    started=time.monotonic(); rows=[]
    with (out/'adaptive_timing_smoke.jsonl').open('w',buffering=1) as stream:
        def save(r):
            rows.append(r);stream.write(json.dumps(r)+'\n');print(r['cell'],r['solved'],round(r['seconds'],3),flush=True)
        with mp.get_context('spawn').Pool(10) as pool:
            assert run_jobs(pool,execute,envs,started+300,save)
    write_json(out,'adaptive_timing_summary.json',dict(alphabet=ALPHABET,attempts=len(rows),solved=sum(r['solved'] for r in rows),wall_seconds=time.monotonic()-started,worker_seconds=sum(r['seconds'] for r in rows),exact_check_seconds=sum(r['exact_check_seconds'] for r in rows),max_exact_check_seconds=max(r['exact_check_max_seconds'] for r in rows),scope='small-scale timing only; queue acquisition batches determine sustained load'))
