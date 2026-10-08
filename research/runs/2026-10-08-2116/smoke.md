# Implementation and admission checks

The complete small-scale smoke passed in **428.45 seconds** with ten workers
and `RAYON_NUM_THREADS=1`. It used two lineages, all original round-one sources,
four new sources/cell/round/arm and four fresh paired scoring seeds/cell/arm.
Its final fits have 40 allocated sources/cell; the full run has 96. No smoke
endpoint is an efficacy decision.

[Verified raw outputs](../../../experiments/output/2026-10-08/2026-10-08-2116-smoke-verified/),
[validation](../../../experiments/output/2026-10-08/2026-10-08-2116-smoke-verified/validation.json),
[replay](../../../experiments/output/2026-10-08/2026-10-08-2116-smoke-verified/replay.json),
[result and projection](../../../experiments/output/2026-10-08/2026-10-08-2116-smoke-verified/result.json),
[timing](../../../experiments/output/2026-10-08/2026-10-08-2116-smoke-verified/timing.json).

All 256 replayed sources matched scientific archive/search fingerprints; both
C1 and T1 decoder hashes and pooled count hashes matched on BE1/PA1. The
collector independently verified 18,864 archive rows, the runner checked 288
paired training-case observations, and no holdout searches ran. All 448
collection and 192 scoring searches completed. All new cell-rounds contributed
3–4 sources; no top-up, replacement, restart or lineage removal occurred.

| Source round | Arm | Solved | Contributing | Attempts |
|---|---|---:|---:|---:|
| 1 (shared replay) | G4 | 43 | 246 | 256 |
| 2 | F | 13 | 30 | 32 |
| 2 | TF | 10 | 31 | 32 |
| 2 | O | 5 | 31 | 32 |
| 3 | F | 7 | 30 | 32 |
| 3 | TF | 10 | 31 | 32 |
| 3 | O | 8 | 29 | 32 |

Frozen scoring solves per 32 searches were F 24, O 22, TF 18, R 22, G4 16,
C_exact 30. These are measured timing/yield anchors, not claims of feedback
superiority. Full-run mean projection is **227.39 min**: replay 8.31,
new collection 50.49, scoring 165.50, fitting 0.35, orchestration/reporting 2.74.
Effective workers: collection 9.53, scoring 8.58. The approved 240-minute gate
passes with C_exact included. Queue timeout is 18,000 seconds; one queue entry
keeps all 16 lineages and 6,144 fresh frozen scoring searches.

The first smoke's [retained diagnostics](../../../experiments/output/2026-10-08/2026-10-08-2116-smoke/)
show an infrastructure false alarm: unordered worker arrival changed raw
floating counts by at most 2.84e-14 although source/archive and C/T decoder
hashes matched. The corrected implementation uses the manifest's historical
source order for exact round-one summation and seed order for fresh rounds.
The verified smoke repeated the same fixed seeds; no design or seed changed.
Its logged Python code hashes match the final implemented files.

Validation: 19 targeted tests passed (`test_partial_feedback.py`,
`test_partial_program.py`, `test_solver_corpus.py`); Ruff passed for all three
new Python files. Tests cover pooled source weighting, empty-new-round
retention, pre-solve exclusion, exact replay rejection, full allocation and
seed pairing/disjointness, source-table selection, endpoint grouping,
complete-lineage eligibility and decision precedence. The queue loads through
`scripts.queue_lib.load_queue`, with the correct id prefix and relative
expected outputs. The generated six-arm diagnostic figure was inspected.

The full run has not been executed during preparation. Its code and command
are ready for independent review and driver execution.

Implementation commit: `393a4dc` on `research/2026-10-08-2116`. Worktree status
is clean. Only experiment code, replay fixture/documentation and tests were
committed; plan, queue and smoke notes remain in the main checkout's task
folder for the loop driver.
