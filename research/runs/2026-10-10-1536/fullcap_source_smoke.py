"""Two full-cap smoke builds; source only, never reused for scoring/full data."""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from experiments.chem_tape.composition_run import write_json
from experiments.chem_tape.independent_input_run import Runner, CAP

if __name__ == "__main__":
    args = argparse.Namespace(prepare=True, preparation=None, smoke=True,
                              protected=True, workers=10, deadline_seconds=600)
    runner = Runner(args)
    runner.cap = CAP
    runner.config.update(cap=CAP, fullcap_source_smoke=True,
                         protected_performance_scored=False,
                         reuse="source-only implementation smoke; cannot be admitted by CLI scoring")
    write_json(runner.out, "config.json", runner.config)
    runner.run()
