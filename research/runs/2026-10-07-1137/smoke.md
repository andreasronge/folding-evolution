# Implementation verification

The approved design is feasible at the measured representative rates. The
full experiment was not executed. The queue retains the approved sixteen
token starts, twelve generations, n=96, 192-search final parents, F1 gate,
and measured context admission with independent F2 reserves.

## Checks

`tests/test_continuation96.py` and `tests/test_rank_one_learning.py`: **21
passed** in 18.51 seconds. These include full 9,600-search trajectory budgets,
shared T/C blocks, disjoint new seed namespaces, midpoint capture, actual
source-parent diagnostics, fingerprint/timing exclusion, gate/outcome boundary
ordering, missing/duplicate observations, training-only payloads, deadline
refusal, and F2 reserves even when no C fits. Simulated full stage flows check
gate failure, all sixteen C starts, a six-per-family subset with matched
confirmation and df=10, and zero C starts with all-start S/T confirmation.
The full fresh counts are 12,000 F1 and 16,500 F2; F2 with zero C is 8,500.

Ruff checks pass for the new runner, inference helpers and tests. Queue
validation passes: one task-prefixed entry, timeout 20,700 seconds (5.75 h,
below the 8 h cap). Imports resolve into this worktree's `src/`. Rust code
was unchanged; real probes exercised the existing Rust executor.

## Real end-to-end smoke

Command: `RUN_DIR=experiments/output/1137-smoke-final .venv/bin/python -m
experiments.chem_tape.continuation96_run --smoke --workers 10
--deadline-seconds 900`.

BE1/PA1, both arms, six reduced generations, n=12, 12 final searches per
parent, inner cap 4,096, fresh cap 8,192, two fresh seeds per cell. All four
trajectories used exactly 600 searches. Total **2,560 searches**, **9,098,752
actual inner evaluations**, 60 F1 rows and 100 F2 rows, **37.68 seconds**.
All scientific row/count/map/pairing validations passed. Smoke is forced to
outcome U and always exercises C, irrespective of its non-scientific gate.
Midpoint is generation three in this reduced test; generation six in full.
The learning figure was visually inspected and renders correctly.

The selected-change diagnostics recorded actual child/source-parent pairs,
including cases where the source was discarded; they did not substitute a
retained competitor. The raw records and report contain coverage denominators.

## Historical baseline replay

Two full-cap replays of saved BE1/PA1 S on the first historical F1 seed,
all ten own-family cells, matched the pinned prior fingerprints exactly:
**10/10 scientific rows**, zero mismatches, each about 0.9 seconds. The
fingerprints include all sixteen deterministic fields, including training
indices, full curves, initialization and decoder hashes, generations and
shortcut counts; timing, arm and phase labels are excluded. The full queue
requires all **4,000 S observations** to reproduce before admitting C.
The compact reference also contains all 4,000 T24 solve/evaluation records
for the descriptive procedure comparison. Original source file hashes and
prior configuration are embedded and pinned.

## Throughput and feasibility

The first exploratory timing check reused 0821's calibration-unit mutant
probe (BE9/10, PA9/10): 384 learn and 192 fresh searches. Its cap batches took
22.58 and 24.54 seconds, respectively, implying about **6.03 h** for an
unshortened queue. This is slower than the proposal, so it was not used as
the sole feasibility check. Those starts are excluded from this experiment;
its fresh batch also had a long tail.

The representative probe instead used one full unselected generation from
the actual BE1/PA1 starts, both arms: two identical initial parents and six
children per arm, n=96, full caps, shared inner seeds, ten workers. Fresh
maps were S and each arm's predetermined first child, ten independent probe
seeds per own cell. No score selected a probe map or changed the full design.

| Measurement | Learn (65,536) | Fresh (524,288) |
|---|---:|---:|
| Searches | 3,072 | 300 |
| Solves | 2,950 (96.03%) | 299 (99.67%) |
| Actual evaluations | 31,168,000 | 3,148,288 |
| Mean worker seconds/search | 0.392 | 0.411 |
| Batch wall seconds | 121.49 | 20.77 |
| Searches/wall second | 25.29 | 14.45 |

Learn mean worker seconds by family/arm: BE:T 0.412, BE:C 0.438, PA:T 0.334,
PA:C 0.385. Measured batch throughput projects **115.1 minutes** for stage
1, **235.4 minutes (3.92 h)** for the full queue, and **207.7 minutes** with
twelve context starts. These are first-generation projections, not a
guarantee about learned maps or all starts. The original roughly five-hour
planning estimate is retained; admission updates from all completed token
trajectories, measured F1 time, and subsequent learning costs. No stage size,
scientific gate, outcome threshold or operator was changed in response to
the probe. The 1.3 timing reserves and local deadline remain in force.

## Evidence files

Compact verification evidence is archived in [smoke/](smoke/): final-smoke
config, status, report and figure; representative probe metrics and baseline
replay; initial probe metrics. Full raw rows remain in this worktree under
`experiments/output/1137-smoke-final/`, `1137-representative-probe/`, and
`1137-probe/`. These are feasibility/debug outputs, not experiment results
to promote. No code_review.md or driver_feedback.md was present.
