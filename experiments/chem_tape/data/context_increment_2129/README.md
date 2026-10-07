Frozen 2129 inputs, derived from the hash-pinned 1707 and 1924 outputs.

- `tables.json`: T1/C1 from 1707, T2/C2 from 1924's C2 fit, all 32 lineages;
  each table is matched to the original fitter's saved SHA256.
- `context_rows.jsonl.gz`: all 16,384 1924 C/C2 training/holdout rows, preserving
  every field; C is aliased C1. gzip mtime=0 makes extraction deterministic.
- `provenance.json`: source paths, full source hashes, source configs, artifact
  hashes and row count. Its SHA256 is pinned in context_increment_run.py.

Regenerate using `.venv/bin/python -m experiments.chem_tape.context_increment_freeze`
when the original outputs are available. Runtime validation is portable and
requires only these committed files. It validates the entire row-key roster,
seed-generated training indices, all four table hashes, and scientific budgets.

Implementation QA:
`RUN_DIR=<fresh directory> .venv/bin/python -m experiments.chem_tape.context_increment_run --smoke --deadline-seconds 600`
uses two lineages and two seeds per cell, without scientific claims.
`--preflight --deadline-seconds 600` instead performs all 64 deterministic
replays and the 160-row fixed T2 block, records their timing, and stops
without inference. Full runs retain that block exactly once within training.

The original 2129 task stopped after preflight because its timing gate could not admit the
full primary before the absolute owner cutoff. See research/runs/2026-10-07-2129/infeasible.md.
The 2156 harness reuses these identical frozen inputs with a 75-minute queue
budget, unconditional primary execution after validation/replay, and holdout
admission based on the full primary roster. No absolute cutoff remains.
