---
verdict: pass
---
# Code review — 2026-10-07-2156

Reviewed commit `36c665d` against `86a4205` (the whole harness is new on this branch) and
against its source `ec742da` on `research/2026-10-07-2129` (the actual code delta: time
budget, holdout gate, primary snapshot). Also reviewed proposal.md, plan.md, queue.yaml,
critique.md and smoke_checks.json. Re-ran the 6 harness tests and Ruff in the worktree
(both pass; worktree clean).

## Blocking issues

None.

## What was checked

**Arm wiring and seeds.** `frozen_sources` pins provenance, both artifacts and all 128 table
hashes; T1 = 1707 `tables.T`, T2 = 1924 `C2.tables.T`, C1/C2 are the renamed 1924 `C`/`C2` rows
(freeze script lines 51–70). `expected_rows` uses phase 11/12 `seed_for(BASE, family, index,
cell, seed)` for all four arms, and `validate_rows` requires the exact roster, identical
regenerated training indices, cap, population, table hash and unsolved budget for every row of
every arm, so the four arms are paired per seed by construction. Training = 16×4 + 16×6 cells ×
32 seeds = 5,120 per arm; holdout = 32 × 3 × 32 = 3,072 per arm. The 160-row T2 timing block is
excluded from the main training job list by `timing_key` and counted exactly once; the
post-training `validate_rows` would fail on any duplicate or gap.

**Replay.** 64 rows (C1 and C2 at each lineage's first training cell, seed index 0), exact match
on `scientific_fields`; replay rows are discarded from inference and the file is renamed to
`replay.jsonl` before any T search. Preflight: 64/64 exact.

**Estimator.** `phase_report` builds per-cell paired contrasts over seeds, averages over the
lineage's own cells, then pools: training with equal family weight, SE = ½√(SE_BE²+SE_PA²),
df = min(15,15) = 15; holdout one-sample over 32 lineages, df 31. `speed_ratio` = 2^(−Δ) and the
interval is sign-flipped consistently (`interval()`), so I > 1 means a larger contextual advantage
after feedback, as the proposal states. Outcome rows 0–4 match the proposal's table exactly,
including the row-3 boundary; the smoke/preflight path is forced to row 0.

**Time budget and holdout gate (the one change from 2129).** No absolute cutoff remains.
`started` is aligned to `metadata.json: started_at`, which `run_queue._run_entry` writes
(timezone-aware ISO) before `Popen`, so elapsed time counts interpreter startup, loading,
validation, replay, timing and training. `work_deadline = start + 4500 − 300`. Primary is
unconditional. The complete primary report is written to `primary/` before the gate is evaluated.
Gate: effective workers = min(10, worker/wall) over timing+training rows; T1 mean and
family-specific T2 means from all primary rows; inflation max(1, 0.946/1.042) = 1; admit iff
remaining > 1.25 × projected. This is what plan.md and the critique's note 2 specify. Holdout is
whole-stage or none; an overrun hits `run_jobs`' deadline, raises `TimeoutError`, keeps
`validation.passed`, and the final report leaves holdout empty while `primary/` survives.

**Gate stability (recomputed).** Bootstrapping the 160 preflight T2 rows (4,000 resamples):
BE mean 0.671 s, 95% [0.26, 1.31] (one 17 s tail row); PA 0.344 s, [0.24, 0.48]. With T1 at
1,042 ms (1707: 5,120 rows), projected primary ≈ 7,765 worker-s and holdout ≈ 4,760 worker-s.
The gate admits holdout for any full-roster effective throughput above ≈ 3.4 workers
(E = 3.3 → refuse by 0.2 min; E = 3.5 → admit by 3.7 min; E = 4.3 → admit by 15.8 min;
E = 8.5 → 42 min slack). Observed full-roster throughput was 9.97 (1707) and 8.47 (1924); the
4.3 figure is the small block with its tail. Even with T2 holdout at 2× the upper bootstrap mean,
the whole run fits in 65 min of the 70-min work budget at E = 4.3. The gate is not a size grid
(whole holdout or none), so nothing is truncated below what 75 min allows.

**Critique.** Notes 1–4 are implemented in code and restated in plan.md's outcome rules with the
narrower wording. Notes 5–6 concern digest/question text outside the researcher's write scope;
plan.md says so and gives the corrected wording for the steward. No unanswered point.

**Queue.** One entry, 4,500 s, cwd = worktree, `.venv/bin/python`, `expect_outputs` all under
`$RUN_DIR` and all produced in both smoke and skipped-holdout paths (`primary/*` exists once
training completes; a stage-1 failure correctly fails the entry).

## Minor notes

1. Unsolved searches cost ≈ 19–26 worker-s each (1707: 25.9 s mean at cap). The 1.25 allowance
   covers cost variance but not a jump in T2 holdout unsolved rate (T1 historical 1.4%). If T2
   holdout unsolved reached ~10% at low throughput, holdout would be cut by the work deadline and
   reported as unresolved transfer; the primary is unaffected. Acceptable, but the analysis should
   read `timings.holdout.complete` and the T2 holdout solve count before interpreting any skip.
2. A `ValueError` raised during the holdout stage (roster/hash check) sets
   `validation.passed = False` and forces the final `result.json` to row 0, even though training
   was validated. `primary/result.json` keeps the valid primary. Analysis should use the primary
   snapshot in that case rather than the top-level outcome.
3. Preflight writes `validation.passed: false` because the flag is set only after training; the
   preflight exit code and `stages.timing` are the right signals there, not that flag.
4. Plan.md says "18 targeted tests"; `tests/test_context_increment.py` alone has 6 (all pass).
   The remainder are presumably the reused corpus/feedback invariant tests. Not a result issue.
5. `--deadline-seconds` is capped at 4,500 in `main()`, equal to the queue timeout; a future
   longer queue needs that constant raised too.
