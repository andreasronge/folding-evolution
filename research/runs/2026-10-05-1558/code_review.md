---
verdict: pass
---
# Code review — 2026-10-05-1558 family-bias sampling (constant thresholds)

Reviewed `git diff 6022128..cd69bce` (family_bias.py, tag_sampling.rs, tests), the delta
against the previously reviewed `3803bca`, and proposal, critique, plan and queue. The 26
family-bias tests pass in the worktree. The worktree is clean at `cd69bce`, and the committed
plan and queue match the canonical copies.

## Blocking issues

None.

## What I checked

- **Task set is feasible.** I ran a reviewer-only 40M uniform pool (seed 999001, not part of
  the run's data, 73 s):

  | n | sum1 | sum5 | max1 | max5 | sum2 | max2 | sum6 | sum7 | max3 | max6 |
  |---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
  | 40M | 67 | 44 | 27 | 28 | 53 | 30 | 0 | 0 | 0 | 1 |

  At these rates the 200M calibration gives roughly 135–335 hits per mandatory task, well
  over the 10 needed. The 1510 blocker is resolved.
- **Runtime fits.** The 100k-tape benchmarks measured 532k (uniform) and 563k (enriched)
  tapes/s; one-step fitted vectors ran at 543k–557k. The full 2.785B reserve is about 5,200 s
  against the 10,500 s internal deadline. The initial scale is 1.0 (raw 1.58), so no runtime
  cut is expected. Exhaustive checks are negligible (≈ 250 candidates per 10M fitted tapes).
- **Arm wiring and seeds.** Fits use only their own two tasks. Holdouts and the four
  descriptive tasks never enter eligibility-independent stages: not pruning, fit updates,
  validation or the verdict. Eligibility is gated on exactly the six mandatory tasks. Every
  pool has its own named stream; benchmark and training seeds are separate from the master.
- **Statistics and verdicts.** Decisive bounds use alpha 0.05/64 over four looks. A
  runtime-reduced transfer cap forces U, as the proposal requires. The verdict table matches
  plan.md, and failed validation or any U gives inconclusive before C/D.
- **Deadlines.** A deadline before the decisive looks finish gives inconclusive; one during
  the prune extension or diagnostics keeps the completed verdict.
- **Queue.** One entry, 10,800 s timeout (limit 8 h), worktree python, outputs under
  `$RUN_DIR`, expected outputs all written by `finish()`.
- **Critique.** All points are addressed in plan.md and the code: swaps kept, CONST_2 weight
  and per-start update support in report.md, the 5M probe is not an eligibility gate,
  one-holdout labelling, optional pools cut first, U never promoted to C/D.

## Minor notes

1. **Expect a result near the 3× gain boundary.** Emulating only the bootstrap step from my
   40M pool (so weaker than the real six-iteration fit), on 10M tapes per fitted vector:

   | Task | Uniform rate | Σ-fit | M-fit |
   |---|---:|---:|---:|
   | sum1 (Σ fit task) | 1.7e-6 | 8.8e-6 (5.3×) | 3.8e-6 |
   | sum5 (Σ fit task) | 1.1e-6 | 6.1e-6 (5.5×) | 3.1e-6 |
   | max1 (M fit task) | 6.8e-7 | 2.1e-6 | 5.5e-6 (8.1×) |
   | max5 (M fit task) | 7.0e-7 | 1.4e-6 | 4.0e-6 (5.7×) |
   | sum2 (holdout) | 1.3e-6 | 4.6e-6 (3.5×) | 2.3e-6 |
   | max2 (holdout) | 7.5e-7 | 1.7e-6 | 3.0e-6 (4.0×) |

   Matched-over-mismatched on the holdouts is about 2.0× (sum2) and 1.8× (max2), with matched
   gain of 3.5–4×. That points toward C, but gain sits close enough to 3× that a U, and so
   inconclusive, is plausible. These are small counts (17–46 holdout hits) from a one-step
   fit; treat them as a prior, not a result.
2. **Starts 1–2 may not update, mainly for the M family.** A Dirichlet start at near-uniform
   rates expects about 7 elites per 10M for max1 and max5, below the 10 needed. Start 0 has
   the calibration bootstrap and then about 40–90 fresh elites per iteration, so it does
   iterate. The fit may in effect be one start; `start_updates` in report.md will show it.
3. **Validation is tight for the M tasks if the fit gains less than about 5×.** With ~135
   calibration hits and 5M validation tapes, max1 needs roughly 9+ hits to get its lower
   bound above 1. The emulated 5.7–8.1× clears this, but a weaker fit would end as
   inconclusive rather than C/D.
4. **A slow machine predetermines inconclusive.** If the opening 100k-tape benchmarks measure
   below about 335k tapes/s, the global scale drops below 1, the transfer cap is cut, and
   every decisive class is forced to U, yet the run continues to the end. The measured margin
   is 1.6×, so this matters only if something heavy runs alongside. If `runtime_budget` in
   progress.jsonl shows scale < 1, the run can be stopped early.
5. `descriptive_comparisons` includes uniform against itself (ratio 1). Harmless.
