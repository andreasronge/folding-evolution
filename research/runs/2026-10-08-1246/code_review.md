---
verdict: pass
---

# Code review: 2026-10-08-1246 comparison-gate training stage

Reviewed `891ae91..5dd86bd` (six new files: bank module, runner, report, pinned bank
JSON + README, tests), proposal.md, critique.md, plan.md, queue.yaml and the smoke
artifacts. Ran `tests/test_comparison_gate.py` in the worktree: 6 passed.

## Blocking issues

None.

## What was checked

- **Arm wiring.** `envelope()` gives G4 rows the validated G4 table (hash pinned) and
  C/T rows their own corpus's fitted table; `jobs()` verifies every returned row's
  `table_hash` against the table it was sent, and that each (phase, family, corpus,
  cell, arm, seed) key is expected exactly once. Holdout-phase rows and any cell
  outside `TRAINING` raise before dispatch; the report raises if any holdout row is
  present. Search payloads carry only `id` and `labels`.
- **Seeds.** Injective rule with distinct phase offsets (0 collection, 1 C/T, 3 G4
  training, 2/5 frozen stage 2); `roster()` rejects any seed shared outside the
  declared C/T pair, and the test confirms the three blocks are disjoint and that the
  smoke base cannot touch them. Seed-derived training cases are re-derived and checked
  per row, and C/T pairing is verified. G4 training seeds are independent of C/T, so
  C/G4 and T/G4 are correctly labelled descriptive.
- **Metric.** `cost` = evaluations if solved else penalty×cap; corpus score =
  mean over 4 cells × 16 paired seeds of log(cost_T) − log(cost_C); C/T = exp(mean of
  corpus scores) with a 95% t interval over corpora (ddof=1). This matches the plan's
  signed endpoint; the test confirms C/T > 1 means C is faster. Evaluations are
  generation-granular in `composition_search.search`, so the `% 256` budget check
  cannot reject a valid solve.
- **Bank and split.** Labels come from the numpy formula and every canonical (480
  programs) is verified on all 1331 inputs in both executors. `PROBED` equals the 12
  cell ids actually searched by the steward probe (`steward_probe/search_res.json`).
  Holdouts are the lowest sha256(id+"1246") among retained, unprobed, role-covered
  behaviours, one per repeated reducer; `load_training()` recomputes the split and
  checks the pinned bank hash on every load. Retained counts (37/56) are asserted
  against the probe.
- **Fitting.** `solver_corpus_fit.py` is unchanged (T: 24 bounded multipliers on G4;
  C: α=50 shrinkage; 1600-weight per-cell normalization). The 1707 24/48 yield floor is
  not inherited; an empty cell raises, as the plan specifies. K is fitted, hashed and
  never scored.
- **Timeout unit.** `completed_pairs` only advances after both corpora of a pair are
  collected, fitted and fully scored; the report analyses exactly the first
  `completed_pairs` pairs, requires every C/T cell of that prefix to have `fresh_n`
  distinct seeds, and marks trailing partial corpora separately. Eligibility needs
  G4 complete and ≥ 6 pairs. The pooled 40% yield gate is computed over the same
  prefix. Tests cover fast/slow trailing jobs not moving the endpoint or the yield.
- **Routing.** `route()` implements the plan's precedence (LB>1 & yield≥0.4 →
  stage 2; LB>1 & yield<0.4 → acquisition obstacle; UB<1.10 → bounded small gain;
  else unresolved) and returns `incomplete` when ineligible. No gate in this queue
  decides whether the main stage runs: the whole stage 1 runs unconditionally, and
  the only stop rules are the deadline and validation errors.
- **Feasibility.** Smoke projection 145.7 min against a 176 min internal work
  deadline and 180 min outer timeout; the ≥ 6-pair minimum is still reached at
  roughly 1.4× slower than projected. Timeout 10800 s is under `max_queue_hours`.
  The driver runs the queue with the worktree as cwd, and `.venv/bin/python` imports
  `_folding_rust` there.
- **Critique.** Notes 1–6 are implemented (fitted-arm timing in smoke, yield policy
  and distinct-tape diagnostics, signed endpoint, precedence and precision scenarios,
  fixed balanced prefix, restricted scope with C/G4, T/G4 and solve rates). Notes 7–9
  concern digest/question text outside this run; plan.md defers them to the steward,
  which is a stated reason.

## Minor notes

1. **Non-timeout error after a complete prefix forfeits the decision.** If a
   validation error or empty cell occurs in pair 7 or 8, `eligible` is false even
   though ≥ 6 balanced pairs are complete. The plan chose this deliberately. The risk
   is small: at the weakest probed cell rate (2/8) the chance of 0/48 is about 1e-6,
   and under 3% across all 64 corpus-cells even at a 15% rate. All rows and corpora
   are persisted, so if it does happen the analysis should report `incomplete` and
   let the steward decide, not silently re-label it as a timeout.
2. **Worker-utilization projection is conservative.** Effective workers (7.8
   collection, 6.8 scoring) come from 32-job smoke blocks; full blocks are 192 and
   256 jobs, so real throughput should be higher.
3. **Resume edge case.** `Runner` refuses a `RUN_DIR` that already holds
   `config.json`. If the driver crashes mid-queue and re-runs the entry into the same
   output folder, the entry will fail immediately rather than restart. Same behaviour
   as the 1707 runner; operational only.
4. **Queue command `cd` is redundant** since the driver already uses the worktree as
   cwd; harmless.
5. **Report sizing fields** (`total_corpora_for_half_width_log_1_10`, power target)
   are planning aids from observed spread only; the analysis should quote them as
   such, as the report's own note says.
