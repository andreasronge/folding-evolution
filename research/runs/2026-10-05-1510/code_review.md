---
verdict: fail
---
# Code review (second round) — 2026-10-05-1510 family-bias sampling

Reviewed `git diff 1ce853c..3803bca` (family_bias.py, tag_sampling.rs, tests), proposal, plan,
queue and critique. The repair commit fixed the code-level issue from the first review. The
design-level issue is unchanged, and plan.md and queue.yaml say so themselves: the run will
stop at the calibration gate. The code is correct; the experiment as queued cannot answer its
question. This needs the steward (task set or calibration cap), not another researcher repair.

## Blocking issues

1. **The outcome is predetermined: "infeasible task set".** I ran a fresh uniform pool at the
   full 60M calibration cap with the experiment's own `Experiment.pool` (reviewer-only seed
   and stream, 8 threads, 110 s; not part of the run's data):

   | n | sum5 | max2 | max5 | max1 | max3 | sum10, sum15, max7, sum7, sum12, max6, sum8, sum11, max4 |
   |---:|---:|---:|---:|---:|---:|---|
   | 60M | 75 | 42 | 30 | 47 | 2 | 0 each |

   Together with the first review's 35M probe (sum7: 1 hit, the rest of the last column 0),
   that is 0 hits in 95M for sum10, sum15, max7 and every Σ holdout except sum7. Eligibility
   needs ≥ 10 hits in 60M. The Σ family keeps one fitting task (sum5; the gate needs 2) and no
   holdout. The M family keeps max2 and max5, with max1 as its only holdout. `calibrate()`
   returns `valid=False` and nothing after it runs. Executing the queue would spend one of
   08's three experiments to reproduce the table above.

   What the steward could change (each needs a proposal amendment):
   - **Task set.** Only thresholds equal to a single constant (1, 2, 5) are reachable at
     ~1e-6. Thresholds one ADD away (max3: 2 in 60M; sum7: 1 in 95M) are at ~1e-8 to 3e-8.
     Anything further has no hits at all.
   - **Calibration size.** Uniform throughput is about 550k tapes/s, so 1G tapes is ~30 min
     and 5G is ~2.5 h, inside the 6 h timeout the current design uses ~15 min of. At ~1e-8,
     ≥ 10 hits needs roughly 1–3G tapes, and it would reach only the one-ADD thresholds.
   - Both changes also need the fit's per-iteration size revisited (see note 1 below).

## Fixed since the first review

- **Fit can now update.** Start 0, iteration 0 uses the calibration pool's exact solvers
  (uniform samples, so legitimate elites for a uniform start); only tasks in the fit enter,
  never holdouts; starts 1–2 are untouched. "No task updated" is its own gate and reason.
  I emulated it on my probe pool: the resulting vectors gave sum5 43 hits in 5M (≈ 6.9×
  uniform) for the Σ-fit, and max2 27 / max5 21 in 5M (≈ 7.7× / 8.4×) for the M-fit, so
  validation would pass for the tasks that are eligible.
- **Deadlines** during the prune extension or both/swap pools no longer overwrite a decided
  outcome. `descriptive_fixed_95` is named for what it is. Prune floor and below-floor swap
  weights are logged.
- 15 family-bias tests pass. Rust evaluator, exactness checks, seed streams, arm wiring,
  adjusted intervals and the verdict table are unchanged from the first review, where they
  checked out. All critique points remain addressed (adjusted bounds over four looks,
  one-holdout labelling, mixed/unresolved fallback, under-supported pruning flag, member
  reversals, descriptive pools cut first).

## Minor notes

1. With the bootstrap, the fit is in practice a single cross-entropy step. After the first
   update I saw 6 (sum5) and 3 / 1 (max2 / max5) exact elites per 833k-tape iteration, below
   the 10 needed, so iterations 1–5 only move the weights closer to the calibration elites'
   frequencies. Starts 1–2 will most likely report "no task updated". No op ends above ~1.8×
   uniform, because executed-cell counts include all junk inside visited runs. A larger
   per-iteration pool would let the fit iterate; time is not the constraint.
2. From the same emulation, descriptive only: the M-fit raised sum5 to 18 in 5M (≈ 2.9×
   uniform) and the Σ-fit raised max5 to 13 in 5M (≈ 5×). Much of the gain may be generic.
   That is the question the experiment is meant to answer, and a reason to get a runnable
   task set rather than drop it.
3. `verdict()` returns inconclusive on any U, even when the other classes already fix the
   outcome. Conservative.
4. The proposal's 3–5 h runtime estimate is off by more than 10×: the full 340M-tape design
   takes about 10–15 min.
