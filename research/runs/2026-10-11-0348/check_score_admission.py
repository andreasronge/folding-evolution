"""Exercise full score admission, intercepting before protected submission."""
import json
import os
from pathlib import Path
from types import SimpleNamespace
from experiments.chem_tape.gate_sum_run import Runner

class BeforeProtectedSubmission(Exception):
    pass

out = Path(os.environ['RUN_DIR'])
args = SimpleNamespace(prepare=False, smoke=False, preparation=str(out.parent/'smoke-stage'),
                       workers=10, deadline_seconds=5400)
runner = Runner(args)
def intercept(metas, name, libraries):
    assert name == 'search' and len(metas) == 5184 and len(libraries) == 24
    assert {m['cell'] for m in metas} == set(runner.bank['split']['protected'])
    raise BeforeProtectedSubmission
runner.jobs = intercept
try:
    runner.score()
except BeforeProtectedSubmission:
    (out/'admission_check.json').write_text(json.dumps(dict(passed=True,
        production_evidence_checked=True, protected_jobs_submitted=0,
        intended_jobs=5184), indent=2))
    print('Full production admission passed; intercepted before protected submission.')
else:
    raise AssertionError('Did not reach the protected submission boundary')
