---
verdict: pass
---
# Code review: 0833 tree libraries from TS sources

Reviewed `5411c26..28db964` (three new files: `experiments/chem_tape/tree_source_run.py`,
`experiments/chem_tape/tree_source_report.py`, `tests/test_tree_source.py`), proposal.md,
plan.md, queue.yaml, critique.md, the smoke evidence in `smoke/`, and the base modules the
wrapper reuses (0150 `tree_library_run`, 0024 `restart_gp_run`, 0348 `gate_sum_run`,
0652 `tree_uniform_run`, `tree_library`, `tree_gp_search`). Ran
`tests/test_tree_source.py` and `tests/test_tree_library.py` in the worktree: 21 passed.
Queue validates (2 entries, 2700 s + 9000 s = 195 min, under `max_queue_hours = 8`).

## Blocking issues

None.

## What was checked

- **Arm wiring.** `envelope()` builds every job as an R-tree restart envelope and attaches
  donors by arm: none for R-tree, `libraries["TS"][build]["entries"]` for R-TS,
  `libraries["DG"][build]["entries"]` for R-DG, `libraries["TS"][build]["controls"]` for
  R-sizeTS. Unknown arms raise. The reported arm name is the real one (no TS→DG relabel).
  `base.execute` passes `e["donors"]` straight into `search(donor_library=…)`, where the
  0.5 library probability and empty-library fallback are unchanged 0150 code.
- **Seeds and pairing.** Attempt seeds are `seed(phase, cell, build, repeat, k)`, independent
  of arm, so all arms in a slot share initial population and training cases; `validate_rows`
  additionally checks `initial_tokens_hash`/`training_indices` agree across arms, and the
  report's `grid()` re-checks seed equality. Phases use distinct domains; the audit checks
  pairwise and historical disjointness (269,537 historical seeds) and exact schedule
  identity. Same 63-bit SHA256 scheme as 0652, which ran cleanly.
- **Source/target separation.** Extraction accepts only `R-tree` rows from
  `TS.split.source`; `verify_banks` requires 4 sources, 8 native targets, no id overlap and
  no label-vector overlap with any destination (native TS or B/C). Libraries are built only
  from the 32 source rows of their own build; failures stay in the cohort and are charged.
- **Metric.** Primary is the ratio of mean capped evaluations R-TS/R-tree on the 12 B/C
  cells, per-build means over cells×repeats (equal cell weight), 8192-draw block bootstrap
  over the 24 build slots; failures are 8×65,536 by construction and enforced by
  `restart.validate_rows`. Guard is the bootstrap solve-fraction difference. Native TS is
  summarised separately and never pooled. R-TS/R-DG uses an independently resampled DG
  cohort; the test confirms its interval does not collapse like the paired contrasts.
- **Stage-0 gate.** Timing only: projects the fixed grid from measured means with
  historical floors (6.48 s for R-tree and both new TS arms, 2.37 s R-DG, 0.49 s native and
  source), measured effective concurrency, 30% reserve and 90 s overhead; admits only if
  preparation ≤ 2700 s and scoring ≤ 9000 s. No solve-yield, effect or library-content
  input. Smoke projection was 269 s / 5706 s against 2700 / 9000, and measured B/C arm
  times (5.0 / 2.5 / 1.5 / 2.9 s) sit below the floors, so the projection is conservative;
  risk of stopping the main stage for the wrong reason is low. The test confirms empty
  libraries and zero solves do not affect admission.
- **Score gating.** `score()` requires an admitted non-smoke preparation with matching
  freeze (all method and Rust-extension hashes), seed audit, preparation hash, passed
  verification/reconstruction/replay, rebuilds all 24 TS libraries and controls from
  `acquisition.jsonl` and compares deterministically, recomputes the stage gate from the
  saved evidence, and re-verifies the 0150 off-path replay. The float-exact recomputation
  pattern is the same one 0348 and 0652 used successfully. `$RUN_DIR/../…-prepare` is the
  precedent pattern (0348, 0652); the runner fixes the date folder at queue start.
- **Outputs.** Every `expect_outputs` entry is written by the code path for that entry.
- **Critique.** Notes 1–5 are addressed in plan.md and the code (actual-source
  calibration, rebuilt extension with canonical TS checks on all 12 TS cells, fixed size
  with no extension, skeleton inference replaced by "content unidentified" wording in
  report.md, explicit unresolved and native-reliability categories in `classify()`).
  Notes 6–8 concern digest/question wording outside the researcher's task folder; plan.md
  says so and leaves them to the steward. The critique itself marked them non-blocking.

## Minor notes (not blocking)

1. `classify()` (`tree_source_report.py:17`) tests the reliability guard before the ratio
   bounds. A result where R-TS both solves less (guard lower ≤ −0.03) and costs more
   (ratio lower > 0.80) is labelled `reliability_unresolved`/`reliability_inferior` and
   routes to `routing_unsettled`, although the proposal's "not portable" rule needs only
   lower > 0.80. This is conservative, not wrong; the analyst should read the intervals
   directly in that case rather than the label.
2. `price()` (`tree_source_report.py:81`) charges 64 source jobs per extra build; a build
   has 32 (8 per source cell × 4 cells). Affects only the descriptive resolution price.
3. The two calibration TS libraries are entirely 3-node entries (pair sums, input+constant
   sums, one `GT(X1,X1)`), matching the probe. Worth confirming in the production library
   audit, since with libraries this small the "32-token crowding" expectation for native
   TS is unlikely to apply.
4. DG acquisition worker-seconds in the economics curves are historical host measurements;
   this is already disclosed in `economics_scope`.
5. R-DG library b is paired with TS slot b by index. Cohorts are independent, and the
   bootstrap treats them as such, so this is fine; just do not read per-build R-TS/R-DG
   ratios as paired.
