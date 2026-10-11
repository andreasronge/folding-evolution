"""Development-only small operator/restart smoke of the production harness."""
import json
import os
from pathlib import Path
from experiments.chem_tape.component_transfer_run import load_saved
from experiments.chem_tape.gate_sum_run import schedules, seed_audit, reconstruct, freeze
from experiments.chem_tape.independent_input_run import method_hashes
from experiments.chem_tape import tree_library_run as base
from experiments.chem_tape import restart_gp_run as restart

out = Path(os.environ['RUN_DIR']); out.mkdir(exist_ok=True)
bank = json.loads((out.parent/'smoke-bank/bank.json').read_text())
saved,_=load_saved();saved['banks.json']['GS']=bank
schedule=schedules(bank); audit=seed_audit(schedule)
assert audit['admitted']
freeze(bank,schedule,method_hashes())
libraries,evidence=reconstruct(saved)
rows=[]
for ci,cid in enumerate(bank['split']['development']):
    for arm in base.ARMS:
        m=dict(family='GS',cell=cid,arm=arm,build=ci,repeat=0,
               seeds=[34100000+k for k in range(8)])
        e=base.envelope(m,saved,libraries,2048)
        row=base.execute(e)
        base.validate_rows([row],[m],saved,2048)
        assert restart.deterministic(row)==restart.deterministic(base.execute(e))
        if arm=='R-tree':
            assert restart.deterministic(row)==restart.deterministic(restart.execute(restart.envelope(m,saved,2048)))
        rows.append(row)
(out/'search.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
(out/'smoke.json').write_text(json.dumps(dict(passed=True,jobs=len(rows),cutoff=2048,
    deterministic_replays=len(rows),ordinary_equivalence=4,audit=audit,
    reconstruction=evidence,protected_searches=0),indent=2))
print('Passed: 12 development-only restarted jobs, deterministic replay, baseline equivalence; no protected searches.')
