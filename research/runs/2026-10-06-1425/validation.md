# Preparation validation

The approved experiment is feasible at the tested scale. No full-run results or scientific verdict have been produced.

Smoke command (worktree cwd): `env RUN_DIR=<fresh-smoke-directory> RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m experiments.chem_tape.saved_shape_run --smoke --workers 10 --deadline-seconds 600`.

The smoke uses all 55 maps and eight cells, four shared seeds 1429000000–1429000003, P=256 and cap=524288. Full-run seeds remain untouched: 1419000000–1419000199. The 1760 (map, cell, seed) keys are unique; all maps, six b starts and six a starts complete. Raw observations and diagnostics are stored under [the worktree smoke directory](/Users/andreas/developer/folding-evolution-research/2026-10-06-1425/experiments/output/verification/2026-10-06-1425-smoke/). These raw files are ignored by git; this note preserves the feasibility measurements.

Raw `search.jsonl` SHA-256: `bdc5086ac65e00042c76cc1d31ee5335644bae20183aaa57b40028041f5caa40`.

Elapsed before final reporting: 100.44 s; summed worker time: 421.85 s; worker mean: 0.23969 s/search. Extrapolation of worker time for 88000 searches / ten workers is 35.15 minutes. Short batches incur proportionally large straggler/dispatch overhead, so retain plan estimate 65 minutes and timeout 150 minutes.

| Family | Searches | Solved | Mean worker seconds |
|---|---:|---:|---:|
| G | 32 | 32 | 0.3056 |
| M+ | 384 | 383 | 0.2594 |
| R | 384 | 384 | 0.2005 |
| R_abl | 384 | 384 | 0.2116 |
| R_fm | 384 | 383 | 0.2319 |

The remaining 192 searches are M references. Overall 1757/1760 solved: BE 437/440, LIN 1320/1320. Four seeds per map/cell are only a feasibility probe, not precise rate estimates.

G prior eight-cell mean = 12.5023400 log2; smoke = 12.5154017; difference +0.0130617, passing the ±0.6 gate. Saved-file hashes, loaded table hashes, vector reconstructions, zero-residual reconstructions, frozen labels and canonical programs all pass.

All 12 frequency controls pass production normalization and evaluator validation:

| Pair | TV to R |
|---|---:|
| 1b | 0.00003937 |
| 2b | 0.00004231 |
| 3b | 0.00005541 |
| 4b | 0.00005310 |
| 5b | 0.00005163 |
| 6b | 0.00002874 |
| 1a | 0.00004537 |
| 2a | 0.00007011 |
| 3a | 0.00004984 |
| 4a | 0.00006100 |
| 5a | 0.00005771 |
| 6a | 0.00005969 |

Tests: `.venv/bin/python -m pytest -q tests/test_saved_shape.py tests/test_contextual_learning.py tests/test_map_learning.py` → 20 passed. After tightening smoke reporting to suppress dependency verdicts, the three new tests pass again. Tests exercise first-match precedence, boundary thresholds, branch gain versus linear loss, exact expectation, production fit, six-start t intervals, a/b clustering, missing control fits and duplicate observations. Final report generation from smoke observations preserves row 0 and D-c for smoke, and all 1760 unique searches have the correct cap/population. Ruff passes on all new files.

Queue parser check: one entry, id prefix correct, timeout sum 9000 s below the 8 h cap. Both `folding_evolution` and `_folding_rust` import from this worktree. No Rust source changed.
