# Implementation and feasibility verification

The pre-execution plan is [plan.md](plan.md). The search engine, genetic
operators, decoder inverse law and RNG streams are unchanged. The new
`initialization_bank_run` reuses the prior runner's job construction and
per-block checks; its training-bank report adds the approved family analysis,
sensitivities and descriptive 13-cell roster. Existing default 2331 behavior
is preserved. No Rust code changed.

## Validation and measured runtime

Executed with ten workers and single-threaded OpenBLAS, OMP and Rayon:
`python -m experiments.chem_tape.initialization_bank_run --smoke` and
`--probe`, each with a fresh RUN_DIR and `--deadline-seconds 1800`.
Both use excluded seeds 3150900–3150901 and retain all maps/cells.

- Forty G↔M round trips ×10000 tapes passed (all 20 maps, both directions).
- Reduced-cap smoke: 393 historical rows reproduced exactly; 1220 searches
  at cap 8192 completed with both full paired blocks checked. Validation passed.
- Full-cap probe: all 420 1723 rows and 366 2331 rows reproduced exactly,
  with no changed substantive fields. Validation CPU time 820.90 seconds,
  wall time 89.54 seconds. All 1220 four-arm searches completed at cap 524288;
  both complete blocks passed every generation-0 hash and row-coverage check.
- Full-cap grid CPU time 1438.26 seconds, wall time 151.88 seconds,
  9.47 effective workers. A one-worker synthetic reporting benchmark briefly
  overlapped this probe; the recorded wall time includes that contention.

| Arm | Searches | Mean seconds/search | At cap (all unsolved) |
| --- | ---: | ---: | ---: |
| GG | 20 | 1.916 | 1 (5.00%) |
| MM | 400 | 0.705 | 1 (0.25%) |
| MG | 400 | 1.474 | 10 (2.50%) |
| GM | 400 | 1.321 | 7 (1.75%) |

The mixed-arm probe implies 719.13 CPU-seconds/seed and 75.94 wall-seconds/seed.
Projection: 200 seeds 253.13 minutes search, about 255 including measured
validation/reporting; 120 seeds 151.88 minutes search. Two excluded seeds give
limited timing/rate precision, so the original conservative 400-minute plan
estimate is retained. There is no measured runtime obstacle to the approved
minimum or full grid. Small-n per-cell solve fractions do not replace the
full-run GG≥75% coverage gate. No cells/maps were selected or dropped.

## Reporting and checks

[report_benchmark.json](report_benchmark.json) records a synthetic full-size
report benchmark: 122000 rows, 20000 bootstrap replicates, and 64 curve points
per row (maximum-length curves). Analysis 14.43 seconds, all reporting/plots
19.13 seconds, below the reserved 360 seconds. The artificial report was
removed; only performance measurements are retained. It is not evidence.

47 targeted tests pass (`tests/test_initialization_intervention.py`,
`tests/test_initialization_bank.py`, `tests/test_composition_bank.py`). Checks
cover conditional encoding, old stream identity, paired hashes, crossed seed
covariance, equal cell-family weighting, Welch cell units, B/E/R/X precedence,
component routing, missing/capped-pair handling, 122000-search counts, deadline
prefix retention, pairing failure stopping dispatch, and reference corruption.
Ruff and `git diff --check` pass. Full grid is queued, not executed here.

The cap sensitivity uses 2331's actual definition: remove a map/cell/seed
triplet if *any of the four arms* reaches cap. Sensitivity retains equal map
weights, averaging remaining seeds inside each map/cell; empty strata make
that sensitivity unresolved. This clarification was made during implementation
from the historical analysis, not by selecting effects from probe outcomes.

## Artifacts and provenance

[preparation/provenance.json](preparation/provenance.json) records raw hashes,
excluded diagnostic seeds and final code-file hashes. Compressed smoke/probe
search and reproduction rows, configs, validation, timing and diagnostic
reports/plots are in `preparation/`. Diagnostic reports were refreshed with
final reporting code; their row is U because they are diagnostic and have only
two seeds. Their effect estimates are not inference for this study.

The pinned 2331 reproduction subset and prior descriptive three-cell points
are in `experiments/chem_tape/data/initialization_0315`, with source hashes and
commit provenance. 1723 artifacts retain their independent original pins.
The queue will repeat all validation under the final committed code before
running seeds 3150000–3150199. The seven-hour internal deadline includes
validation and reporting; the timeout is 27000 seconds (7.5 hours).
