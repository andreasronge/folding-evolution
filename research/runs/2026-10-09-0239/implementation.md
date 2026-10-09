Implementation uses the original composition search with a single optional decoder-factory
argument; all RNG streams, selection, variation, executor and exact verification remain
on that path. New modules implement the frozen Q/P projections, positional lookup,
preparation gates, roster execution and paired corpus report. Historical K output is
vendored with independently pinned provenance; the existing pinned C/T/G4 and source
tables are reused.

Targeted checks: `RAYON_NUM_THREADS=1 .venv/bin/python -m pytest -q
 tests/test_position_matched.py tests/test_frequency_matched.py` — 10 passed in 63.45 s.
The checks include a changing-position scalar decoding oracle, identical-K map identity,
quantized support and marginal propagation, exact roster/case pairing metadata, known
ratio directions, joint Q/P interpretation, incomplete/duplicate refusal and empty
both-solved sensitivity. `git diff --check` and compilation passed. Rust is unchanged.

Preparation command (raw validation/timing output in [smoke/](smoke/)):

```sh
RUN_DIR=/Users/andreas/developer/folding-evolution/research/runs/2026-10-09-0239/smoke RAYON_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.position_matched_run --prepare --workers 10 --deadline-seconds 1780
```

These are implementation checks and fixed-seed preparation measurements, not a full-roster
research result. Admission and final queue disposition will be recorded after preparation.

Preparation disposition: all marginal, support, lookup and legacy replay gates passed;
runtime admission failed (10,869.70 s including 15% safety, fitting and reporting vs
10,800 s approved scoring timeout). See [infeasible.md](infeasible.md) for measured costs
and a priced steward alternative. Stop without queue.yaml or full scoring. No code
or admission rule was adjusted after this failure.
