"""Reproduce legacy signed-gate freeze failure with pre-change method inventory."""
import json
import subprocess
from pathlib import Path
from experiments.chem_tape import independent_input_run as inventory, signed_gate_run as legacy

new = {'experiments/chem_tape/input_rebound_run.py', 'experiments/chem_tape/rebound_library.py'}
changed = set(subprocess.check_output(['git','diff','--name-only','997ccdb','HEAD']).decode().splitlines())
assert changed == new | {'tests/test_input_rebound.py'}
original = inventory.method_hashes
inventory.method_hashes = lambda: {k:v for k,v in original().items() if k not in new}
try:
    legacy.load_bank()
except ValueError as error:
    assert str(error) == 'presearch method/schedule/seed freeze mismatch'
    report = dict(baseline='997ccdb', reproduced=True, error=str(error), changed_files=sorted(changed),
                  scope='Pre-change method inventory restored in memory; all existing tracked sources and compiled backend unchanged. No repository edits. Both failing tests call this same legacy load_bank gate.')
else:
    raise AssertionError('baseline legacy freeze unexpectedly passed')
finally:
    inventory.method_hashes = original
Path(__file__).with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
