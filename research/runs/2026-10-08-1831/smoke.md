# Implementation smoke validation

Two ten-worker smokes used one BE/PA corpus pair, four sources per own cell and two
fresh paired seeds per cell, with the full intended population, collection checkpoints
and scoring cap. Seeds are base+100,000,000 and are disjoint from confirmation.

All112 search rows replayed identically between smokes with timings excluded, including
archives; all fitted decoder hashes match. The final smoke method/code hashes match
the implemented files. The initial smoke preceded the final reporting/sizing changes.

Final smoke: 135.32 seconds;32 sources and80 scoring searches.
Archive verification: 1408 tape rows on D1331;64 paired-case checks;zero holdout searches.
Exact solvers and solve-generation archives are excluded; all attempts remain in search.jsonl.

| Phase/arm | Searches | Solved | Mean worker seconds |
|---|---:|---:|---:|
| collection:G4 | 32 | 5 | 2.045 |
| training:C_S | 16 | 10 | 17.054 |
| training:T_S | 16 | 10 | 13.828 |
| training:C_P | 16 | 12 | 13.597 |
| training:C_exact | 16 | 12 | 10.777 |
| training:G4 | 16 | 9 | 14.032 |

Full mean projection: 143.94 minutes;210-minute feasibility gate passed.
All partial arms capped sensitivity: 210.33 minutes;240-minute outer timeout retained.
Archive scoring, search instrumentation, serialization and dispatch are included in measured
worker/wall rates; fitting measured separately, with120 seconds for startup/reporting.
This is small-scale timing/implementation QA, not an efficacy result or an estimate of
confirmation corpus variance. The capped sensitivity exceeds210 slightly but does not
describe the measured solve-rate mean; no search size or horizon was changed.

Scientific and regression validation:25 targeted tests passed (partial-program, solver-corpus,
comparison-gate and solver-feedback); the final terminal-solve boundary addition also passed
all7 partial-program tests. Ruff and git diff --check pass. Diagnostic PNG visually inspected.
Queue parsed with scripts/queue_lib.load_queue:one entry, correct id prefix,14,400-second total.

Confirmation schedule:7,168 rows (2,048 acquisition+5,120 scoring), canonical SHA256 `bf362b4bf05fb321c3828977c1b0c2e6356109131c48ffce5acc507ec8b3057c`.
Raw smoke outputs: [final result](smoke-final/result.json), [timing](smoke-final/timing.json),
[validation](smoke-final/validation.json), [search rows](smoke-final/search.jsonl),
[curves](smoke-final/diagnostics.png). No full confirmation searches were run during preparation.

Implementation committed as `998a9fe` on `research/2026-10-08-1831`.
Smoke collection happened during implementation; final source byte hashes match the
committed code. Task artifacts remain in the main checkout's task folder, outside this
code commit. The task worktree is clean.
