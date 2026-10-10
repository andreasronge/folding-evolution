"""Small full-cap timing check; source cells only; not sustained-load admission."""
import json, multiprocessing as mp, time
from pathlib import Path
from experiments.chem_tape.composition_run import run_jobs, write_json
from experiments.chem_tape.four_reducer_maps import tables
from experiments.chem_tape.independent_input_run import execute, load_frozen, method_hashes, schedules, ALPHABET, CAP, BANK_SHA, OLD_SHA

if __name__ == '__main__':
    out=Path(__file__).parent
    bank, old=load_frozen()
    cells={c['id']:c for c in bank['screen']['cells']}
    schedule=[dict(phase='timing_smoke',build=0,cell=cid,arm='G4',attempt=a,seed=430000+10*ci+a) for ci,cid in enumerate(bank['split']['source']) for a in range(4)]
    write_json(out,'timing_smoke_freeze.json',dict(bank_sha256=BANK_SHA,old_sha256=OLD_SHA,method_hashes=method_hashes(),source_and_score_schedules=schedules(bank),timing_schedule=schedule,scope='16 small-scale source attempts; not64-job sustained load; no protected scoring'))
    envelopes=[((cells[r['cell']],r['arm'],tables()['G4'],r['seed'],CAP,256,bank['inputs'],ALPHABET),r,[],[]) for r in schedule]
    rows=[]; started=time.monotonic()
    with (out/'timing_smoke.jsonl').open('w',buffering=1) as f:
        def save(r):
            rows.append(r); f.write(json.dumps(r)+'\n')
            print(r['cell'],r['seed'],r['solved'],round(r['seconds'],3),flush=True)
        with mp.get_context('spawn').Pool(10) as pool:
            assert run_jobs(pool,execute,envelopes,started+300,save)
    write_json(out,'timing_smoke_summary.json',dict(solved=sum(r['solved'] for r in rows),attempts=len(rows),wall_seconds=time.monotonic()-started,worker_seconds=sum(r['seconds'] for r in rows),exact_check_seconds=sum(r['exact_check_seconds'] for r in rows),max_exact_check_seconds=max(r['exact_check_max_seconds'] for r in rows),scope='small-scale timing only; sustained-load admission uses queued128-job batches'))
