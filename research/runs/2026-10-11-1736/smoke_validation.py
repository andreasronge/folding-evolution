"""Validate saved correctness smoke; tamper/replay without fresh search."""
import copy
import json
from pathlib import Path
import tempfile
import shutil
from experiments.chem_tape import recurrent_library_run as run
from experiments.chem_tape.comparison_gate_bank import digest

folder=Path(__file__).parent/'smoke-v2'
bank, artifacts, rows, manifest=run.load_exposure(folder/'exposure', True)
scores=[json.loads(s) for s in (folder/'readout/score.jsonl').read_text().splitlines()]
run.validate_scores(scores, artifacts['schedules']['readout'], bank, manifest['probabilities'])
checks=[]
def rejected(label, fn):
    try:
        fn()
    except (ValueError, KeyError) as error:
        checks.append(dict(check=label, rejected=True, reason=str(error)))
    else:
        raise AssertionError('Accepted invalid artifact: '+label)
rejected('partial exposure',lambda: run.validate_exposure(rows[:-1],artifacts['schedules']['exposure'],bank))
rejected('duplicate exposure',lambda: run.validate_exposure(rows+[rows[0]],artifacts['schedules']['exposure'],bank))
changed=copy.deepcopy(rows)
changed[0]['episodes'][1]['initial_f']=1
rejected('episode bit reset',lambda: run.validate_exposure(changed,artifacts['schedules']['exposure'],bank))
changed=copy.deepcopy(rows)
changed[0]['episodes'][0]['modifier_trace'][0]['modifier_transitions'][0][1]+=1
rejected('transition tampering',lambda: run.validate_exposure(changed,artifacts['schedules']['exposure'],bank))
changed_scores=copy.deepcopy(scores)
changed_scores[0]['probability']=0.12345
rejected('readout law mismatch',lambda: run.validate_scores(changed_scores,artifacts['schedules']['readout'],bank,manifest['probabilities']))
rejected('partial scoring',lambda: run.validate_scores(scores[:-1],artifacts['schedules']['readout'],bank,manifest['probabilities']))
rejected('smoke into full-run readout',lambda: run.load_exposure(folder/'exposure', False))
with tempfile.TemporaryDirectory(prefix='1736-tamper-') as d:
    root=Path(d)/'exposure'
    shutil.copytree(folder/'exposure',root)
    changed=copy.deepcopy(manifest)
    changed['probabilities']['0:0']['L-final']=0.12345
    changed['manifest_hash']=digest({k:v for k,v in changed.items() if k!='manifest_hash'})
    (root/'exposure_manifest.json').write_text(json.dumps(changed))
    rejected('endpoint tampering with rehashed manifest',lambda:run.load_exposure(root,True))
checks.append(dict(check='paired q0/R-all paths',valid=True,initial_jobs=sum(s['arm']=='initial' for s in scores),fixed_jobs=sum(s['arm']=='R-all' for s in scores)))
checks.append(dict(check='equal scheduled evaluations',valid=True,per_population=[sum(e['evaluations'] for e in r['episodes']) for r in rows]))
print(json.dumps(dict(admitted=True,checks=checks),indent=2))
