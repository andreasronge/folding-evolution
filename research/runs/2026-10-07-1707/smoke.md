# Implementation and smoke validation

Approved design remains feasible. These diagnostics are excluded from full-run inference.

## 48/cell feasibility probe

`smoke-probe/` uses separate base 2,226,100,717. Collection used one corpus per family and the full cap 524,288, P=256, ten workers. It replayed all 40 historical rows first; every deterministic scientific field matched and each returned solver was independently re-verified on D1331.

| Corpus | Solvers per cell (training order) | Collection wall s | K max error |
|---|---|---:|---:|
| BE1 | [42, 47, 44, 42] | 67.52 | 0.00002581 |
| PA1 | [48, 48, 46, 47, 45, 47] | 57.12 | 0.00002443 |

Total: 456/480 solvers; minimum cell yield 42/48 (floor 24). Collection wall 124.64 s projects to 33.2 min for all 32 corpora. Both T optimizers converged; all six tables passed shape/range/support/Decoder checks. Both K fits passed <=0.001. The reduced fresh evaluation had 180/180 expected rows. Probe total wall: 168.53 s.

## Final end-to-end smoke

`smoke-final/` uses separate base 2,126,100,717 and the final seed spacing (cell stride 200, corpus stride 2,000). Two corpora/family with eight collection seeds/cell, two fresh seeds/cell, small G4/M references, and all three holdouts exercise the full path at the unchanged scientific cap. This checks implementation, not inferential precision.

All four corpora fitted successfully, 12/12 tables validated, and all four K fits passed. Stage 1: 240/240 rows. Stage 2: 78/78 rows. Independent solver verifications: 151; paired-case checks: 128. Total wall 120.50 s; no stop reason.

Admission was independent of results: remaining 677 s versus 1.5 times a 13.24 s projection; it admitted holdouts. Actual holdout wall time is recorded in smoke-evidence.json. Primary and 1×cap sensitivities, subset contrasts, arithmetic break-even, family comparisons and PNG diagnostics serialized successfully.

An earlier `smoke-end-to-end/` exposed a NumPy boolean in admission JSON. `admit_holdouts` now returns a Python bool; a regression test covers serialization, and the final smoke passed. The 128-seed G4 holdout block also required widening the cell seed stride; full roster tests verify disjointness of collection, evaluation, reference, corpus, cell and phase blocks. The initial feasibility probe used smaller strides, which were disjoint at its reduced counts.

## Checks and queue sizing

66 related tests passed (solver-corpus, four-reducer, map-learning, crossed-learning/holdout and initialization-bank). After final fixes and added inference/amortization tests, all seven focused solver-corpus tests passed. Ruff and git diff --check passed. No Rust source changed.

The 48/cell probe projects collection to 33 min. Final smoke fitted-search worker means were T 0.98 s, C 0.35 s and K 1.15 s, with about seven effective workers in the short grid. Conservative extrapolation puts training plus references near 38 min and holdouts near 26 min, about 100 min total including validation/fitting/reporting. These small evaluation blocks are noisy; they do not justify changing sample counts or fitting parameters. The timeout stays 8,100 s (135 min), internal deadline 7,920 s and reporting reserve 120 s. The real stage-2 gate recalculates from full stage-1 throughput.

Full queue roster tests confirm 7,680 collection, 17,920 training/reference and 9,600 holdout searches (35,200 total), before allowed K-only exclusions. Queue commands use the worktree .venv and write only under RUN_DIR. The full queue has been prepared, not executed.

Raw diagnostic files remain in the task folder; smoke-evidence.json preserves configs, counts, fit table hashes, convergence diagnostics, timing and summary checks for review. Earlier belief-file corrections from critique 6–7 are documented in plan.md for the steward; no belief files were edited.
