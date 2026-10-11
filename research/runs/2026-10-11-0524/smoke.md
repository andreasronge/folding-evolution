# Implementation and smoke evidence

Full scoring was not run. These are implementation checks and development-stage
calibration, not a finding or a B/C replacement result.

- `smoke-prepare/`: initial 36-job implementation smoke completed all searches
  and six deterministic replays, then exposed a NumPy boolean JSON serialization
  bug in the gate output. Converted rate values to native floats and reran.
- `smoke-prepare-v2/`: corrected non-admitting smoke; 36/36 solved, mean 25,024
  evaluations and 1.7990 worker seconds, stage wall 13.286 s. Short-batch
  concurrency was 4.875, so its conservative estimate selected four repeats.
  Its `preparation.json` has `admitted=false` regardless of timing gate.
- `validation-prepare/`: production preparation at small scale (development
  stage only). Reconstructed all 24 source libraries, including four source
  failures; 72 frozen constructions /543 entries passed every exact/semantic
  check. Six saved 0348 R-lib jobs matched all deterministic fields. Development
  calibration: 288/288 solved, mean 23,486.222 capped evaluations, mean 1.918282
  worker seconds; max job 18.959 s. Stage wall 57.054 s and worker total 552.465 s,
  effective concurrency 9.683. Conservative six-repeat projection 3,800.057 s;
  selected six repeats /three constructions. Four-repeat projection 2,563.371 s.
- `validation-score-preflight/`: actual scoring admission, source rebuilding,
  construction regeneration, replay/stage evidence and selected-schedule checks
  passed. A local validation callback stopped before executing any scoring job.
- `smoke-report/`: **synthetic** complete 7,776-row test fixture, all 8,192
  bootstrap draws, acquisition curves and plots, 1.595 s. Both plots visually
  checked. Synthetic data deliberately contain paired repeat effects that
  cancel, to verify that bootstrap resampling retains the two-repeat blocks.
  This is not scientific evidence for retention or positive-control sensitivity.

Commands:

```sh
RUN_DIR=<task-folder>/smoke-prepare-v2 RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.tree_permutation_run --prepare --smoke --deadline-seconds 600
RUN_DIR=<task-folder>/validation-prepare RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.tree_permutation_run --prepare --deadline-seconds 600
RAYON_NUM_THREADS=1 .venv/bin/python -m pytest tests/test_tree_permutation.py tests/test_tree_library.py tests/test_gate_sum.py -q
.venv/bin/python -m ruff check experiments/chem_tape/tree_permutation*.py tests/test_tree_permutation.py
```

34 tests passed in 19.39 s. The queue parses with `scripts.queue_lib.load_queue`:
two sequential entries, timeout sum 9,600 seconds (160 minutes). Preparation
recalibrates before choosing the approved six/four-repeat grid; both grids keep
exactly two repeats per construction, shared reference rows and all arms.

Method files from the reviewed acquisition/search implementation were not
modified. No Rust changes or new dependencies. Reference snapshots have fixed
gzip timestamps and SHA256 provenance; raw smoke artifacts stay in this task
folder in the main checkout, outside the committed worktree changes.

Implementation committed as `7c0e5df` on `research/2026-10-11-0524`; the
worktree is clean and the commit contains no `research/` files. Preparation
validation ran before that commit, with identical final method hashes; the
full queue will log the committed revision in `config.json`.
