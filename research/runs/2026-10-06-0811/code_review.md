---
verdict: pass
---
# Code review: 2026-10-06-0811 contextual continuation (second pass)

Reviewed `f413e47..0709104` (`contextual_learning.py`, `contextual_learning_run.py`,
`contextual_report.py`, vendored sources, tests), plus proposal.md, critique.md,
plan.md, queue.yaml, verification.md and the feasibility / smoke-final /
smoke-review-fix artifacts. The first pass (range `f413e47..850c76e`) failed on one
blocking issue: the stage-0 contextual spread gate (row-move true-effect sd ≥ 0.15)
decided whether the learning stage ran and failed in about half of resamples of the
researcher's own pilot. Commit `0709104` applies the amendment that review permitted.
No blocking issues remain.

## Blocking issues

None.

## The fix, verified

- **Gate removed, calibration kept descriptive.** `calibration()` no longer computes
  `gate_passed`; `projection()` lost its `gate_passed` parameter and the frozen-only
  `(0, …)` choices; `run()` admits pairs unconditionally after a passing harness check;
  `report()` lost `gate_failed` and the row-0 "no usable row variation" branch.
  `grep gate` over the four files finds only the two descriptive `calibration_role`
  strings and a test asserting the old key is absent. `stage0.json` from the fresh
  smoke has no `contextual_gate_passed` key and still carries `variation` (signed
  effects, beneficial fractions, interval), `calibration_children` and solve counts.
- **Row 0 now means harness mismatch only.** `report(..., harness_mismatch=True)`
  returns row 0 and `complete=False` before any coverage logic; `run()` returns before
  references, learning, off-family and sampling on mismatch. Covered by the rewritten
  routing test (evaluate/evolve/sampling all forbidden on mismatch).
- **Zero spread still admits learning.** New test drives `calibration()` with
  synthetic identical costs (true-effect sd = 0) and asserts 35 generations are
  scheduled and `evolve` is reached.
- **Amendment recorded.** plan.md has a "Reviewer-required amendment" section with
  the pilot instability numbers, row 0 in its outcome table reads "Harness mismatch"
  only, and queue.yaml notes say the same. The steward will see why row 0 narrowed.
- **Nothing else changed.** The `850c76e..0709104` diff touches only gate plumbing,
  the three descriptive strings, tests, plan/queue/verification text and the new
  smoke folder. Arms, operators, seeds, bounds, contrasts and cut order are the same
  code the first pass verified.

## Remaining gates, checked for stability

- **Harness mismatch gate** (|mean G cost − 13.84| > 0.6 on 6 cells × 20 seeds at
  65k). On the pilot's 120 harness searches: mean 13.743, sd 1.63, SE 0.149.
  Resampling the 20 shared seed indices jointly across cells (10 000 draws) gives a
  95% interval of [13.52, 13.96] and a 0/10 000 trip rate. Stable; it will only fire
  on a real harness change.
- **Timing projection** (7.0 h cap, cut order sampling → stage 4 → 28 generations,
  infeasible if still over). Recomputed with the amended `projection()` on the pilot's
  measured rates and sampling time: selects 35 generations with sampling and
  off-family at 6.32 h, identical to the stored pilot selection, leaving 1.29 h of
  slack to the 7 h 37 min work deadline. Rates enter as worker-seconds per search
  with pool overhead and a floor at the proposal's anchors, so a modest slowdown in
  the full run degrades gracefully through the approved cuts rather than cancelling.
- **Pair admission** reserves `max(1.1 × projected pair seconds, 1.1 × slowest
  completed pair)` before each pair, so a deadline leaves whole pairs with their M+,
  R and R_abl tests. Projected pair cost is about 22 min; 12 pairs fit with margin.

## Carried over from the first pass (unchanged code, re-spot-checked)

- Zero-residual R vectors reproduce every saved M table (asserted in
  `Runner.__init__`); `R_abl` is exactly `R[:23]` through `table_for('M', …)`; M+ uses
  0132's `mutate` with ±log 16 bounds; R's row step clips each coordinate to ±log 16.
- Learning seeds `812000000 + pair×10000 + gen×100` and selection seeds
  `813000000 + pair×1000` are shared between the two arms of a pair; mutation
  streams `817000000 + pair×100 + {0,1}` differ per arm. Test seeds are identical
  across every map per cell. Namespaces are disjoint from 0001, 0132 and the steward
  probe; smoke (+10M) and calibration-only (+20M) offsets keep verification seeds out
  of the real run.
- `contrast` resamples starts as clusters then shared seed indices jointly across
  maps; classification thresholds (lower > 1; upper < 1.25) and the outcome rows
  match plan.md. Completeness requires every expected map/cell to have exactly the
  expected unique seeds; `complete` can only be true after all 12 pairs.
- Critique notes 1–5 are addressed in plan.md and code; notes 6–11 are digest edits
  outside the researcher's scope and are correctly deferred to the steward.
- Queue: one entry, `timeout_seconds` 28 800 at the 8 h cap, internal deadline
  27 600 s, outputs under `RUN_DIR`; loads via `queue_lib.load_queue`. The 8 tests in
  `tests/test_contextual_learning.py` pass; worktree is clean at `0709104`.

## Minor notes

- The calibration spread estimates remain noisy (per-start values 0.00–0.37 on the
  pilot). analysis.md should report only the pooled value with its interval, as a
  descriptive, and never read the per-start numbers.
- Stages 4 and 5 have no time reservation and may be cut by the deadline. That is
  the approved priority order; analysis.md should state which stages were cut.
- `training65` contrasts re-cap the 524k test rows at 65k; fine as a derived
  descriptive, not a separate run.
- The `sampling` phase keeps 10⁸ genotypes per map at a measured 123 s per map (18
  maps ≈ 37 min), slower than the proposal's 68 s. Already inside the 6.32 h
  projection, so no action.
