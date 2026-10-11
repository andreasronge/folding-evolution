---
verdict: pass
---
# Code review: 1019 fixed sum-donor prior vs TS libraries

Reviewed `25607cc..e29219b` in the worktree (`experiments/chem_tape/tree_hand_run.py`,
`tree_hand_report.py`, `tests/test_tree_hand.py`, the two-line observer hook in
`tree_gp_search.py`, and the archived 0833 artifacts under `data/tree_hand_1019/`),
proposal.md, plan.md, queue.yaml, critique.md, and the admission evidence in
`admission-prepare/`, `admission-check.json` and `smoke/`. Also read the base modules the
runner reuses (0150 `tree_library_run`, 0024 `restart_gp_run`, 0833 `tree_source_run`,
0652 `tree_uniform_run`, 0348 `gate_sum_run.freeze`, `tree_source_report.grid/acquisition`).
Ran `tests/test_tree_hand.py` in the worktree: 12 passed (the plan's 39 count includes the
older library/source/GP test files). Queue parses: two sequential entries, 1800 s + 7200 s
= 2.5 h, under `max_queue_hours = 8`.

## Blocking issues

None.

## What was checked

- **Prior construction.** `hand_prior()` takes only the alphabet name. Token ids are
  correct: ADD = 9, inputs 0–3, constants 5–8 = {0, 1, 2, 5}. P = 12 ordered distinct-input
  pairs × 8 copies, K = 32 oriented input–constant forms × 3 copies, 192 entries, 44
  distinct, 96/96 draw mass per class. Nothing is read from the learned libraries. The
  unchanged sampler draws uniformly over the 192-entry tuple, so multiplicity is the draw
  law. Every entry is checked by `verify_entries` (interpreter vs VM) and additionally
  against `python_output`; the prior hash is frozen in `method_freeze.json`.
- **Arm wiring and seeds.** `envelope()` builds every job as an R-tree restart envelope and
  attaches donors by arm: none for R-tree, `libs["TS"][build]["entries"]` for R-TS (build
  order from the 0833 archive, same indexing 0833 used), the fixed prior for R-hand. R-tree
  and R-TS go through the unchanged `base.execute`; R-hand uses a copy of the same attempt
  loop plus the observer. Seeds are `seed("score", cell, build, repeat, k)`, independent of
  arm, so the three arms share attempt seeds, initial populations and training cases in
  every slot; `source.validate_rows` re-checks `initial_tokens_hash`/`training_indices`
  pairing and `grid()` re-checks seed equality. Stage/smoke/score domains are disjoint and
  audited against the 0833 schedule plus the older historical unions.
- **Observer.** The two-line hook runs only on a library draw, after the insertion decision,
  consumes no RNG and returns nothing to the search. `reviewed_methods()` requires the
  current engine to equal the archived 0833 engine with exactly that textual delta, and that
  the archived engine's hash is the one in the 0833 method freeze. `dg.freeze` receives the
  pristine hash so its 0150 core check still runs; the freeze then records the actual
  current hashes. The test confirms search output is identical with and without the
  observer and that class counts reconcile with the engine's own library statistics;
  `validate_rows` enforces that reconciliation on every R-hand attempt.
- **TS reconstruction.** All seven 0833 artifacts are byte-hashed against `provenance.json`;
  the 768 source rows are re-validated, libraries rebuilt with the original extractor, and
  deterministic fields plus acquisition costs compared. Failures stay in the cohorts.
- **Primary metric and rule.** `grid()` builds a (24 builds × 12 cells × 6 repeats) array
  per arm; per-build means over cells × repeats give equal cell weight; failures are
  8 × 65,536 by construction (enforced by `restart.validate_rows`). Ratio of means, 8192-draw
  paired bootstrap over the 24 build indices with the same draws for every arm, bootstrap
  seed fixed. `classify()` implements exactly the registered rule (upper < 1.25, hand/tree
  upper < 0.80, solve-difference lower > −0.03 → retained; lower > 1.25 → learned
  increment; else unresolved); the six boundary tests cover each predicate. Acquisition is
  resampled jointly with the TS build; R-hand has zero acquisition.
- **Stage-0 gate.** Timing only. Projection = 90 s + 1.3 × 1728 × Σ max(floor, measured
  mean) / measured concurrency, admitted iff ≤ 7200 s and preparation elapsed + 90 ≤ 1800 s.
  No solve, fitness or library-content input, no variant selection, no fallback. The stage
  jobs use fixed seeds, so the queue's fresh preparation will rerun the identical 72 jobs
  the admission run executed (24/24 solved per arm, 6.54 / 1.52 / 1.74 worker-s). With the
  floors the projection is 4045 s; a uniform 2× host slowdown gives 5836 s, and concurrency
  would have to fall below 4.95 (measured 8.9) at unchanged means to fail. A failure raises
  and writes `infeasible.json`; it cannot silently shrink the design.
- **Score gating.** `validate_preparation` requires an admitted, non-smoke preparation with
  identical freeze and seed audit, re-verifies the preparation hash, rebuilds the TS
  libraries and the prior and compares to the archived `libraries.json`, re-validates the
  stage rows and recomputes the gate float-exactly from stored timing (same sorted row
  order as at prepare time), and re-checks the eight 0024 off-path replays. The
  `admission-check` run exercised this path against `admission-prepare` and rejected both
  the smoke preparation and an altered donor file.
- **Outputs.** Every `expect_outputs` entry for both queue items is written by the code path
  of that item; `$RUN_DIR/../…-prepare` is the 0348/0652/0833 pattern.
- **Critique.** Notes 1–5 are addressed in plan.md and the code (counts and rates stated as
  measurements vs scenario, fixed stage seeds and timing-only admission with stop action,
  substitution-level wording, fixed size with unresolved branch, Dinh attribution
  corrected). Notes 6–8 are digest/question wording outside the researcher's write scope;
  plan.md says so and tells the analysis not to repeat the widened claims. Acceptable.

## Minor notes

1. The concurrency estimate is a makespan statistic: the stage batch wall (26.4 s) is
   dominated by its longest job (23.6 s, a five-attempt R-tree job), so "effective
   concurrency" is really worker-seconds over the longest job. It is conservative here and
   deterministic across reruns, but it is not a sustained-throughput measurement as the
   queue notes describe it. No action needed for this run.
2. `admission-prepare/config.json` records `git_commit` 25607cc (the pre-implementation
   HEAD with uncommitted changes), so the archived calibration cannot be tied to e29219b by
   hash. Harmless because the queue reruns preparation at the committed state, and
   `validate_preparation` compares freezes rather than commits.
3. The per-build `TS_over_hand` intervals resample repeats within fixed cells and are
   labelled as conditional; keep them descriptive in the analysis (24 overlapping
   intervals, no multiplicity handling).
4. `economics["R-hand/R-tree"]` repeats the same ratio at all 200 horizons; fine for the
   plot, but it is not an economics curve and should not be read as one.
5. `envelope()`'s arm check (`not in ARMS and != "R-tree"`) is redundant; harmless.
