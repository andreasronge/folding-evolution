---
verdict: pass
---
# Code review: 2026-10-05-1705 evolve-bias (diff 79170dd..9abc25c)

## Blocking issues

None.

## What I checked

- **Arm wiring.** `vectors()` maps uniform / matched / mismatched / hand to the right frozen
  vector for each task. The frozen `sum` and `max` vectors are identical to `vectors` in the
  1558 `result.json` (file SHA256 matches the recorded one). Both hand vectors sum to 1, keep
  CONST_0/1/2/5 (ids 2/3/15/16) at exactly 1/22, and give the multipliers the proposal quotes
  (Σ: INPUT 2.86×, GT 3.23×, SUM 1.96×, REDUCE_ADD 1.73×, others 0.59×; M: 2.60×, 2.97×,
  2.84×, others 0.64×). The 1558 sampling counts in the JSON match the plan.
- **Bias reaches both init and mutation.** `op_weights` feeds `random_genotype`, and
  `mutate_batch` uses it for op replacement and insertion. The uniform arm passes an explicit
  22-vector too, so all four arms take the same code path.
- **Seeds.** Arms share the training cases and the evolution seed within a task and replicate.
  This is the pre-registered pairing, and the paired bootstrap resamples seeds jointly, so it
  is analysed correctly. Pilot (+10000), smoke (+20000), main (+100000) and the sampling
  streams are disjoint, and bootstrap seeds differ per comparison and look.
- **Endpoint.** Time is `gen*P + pos + 1`, with the earliest exact candidate in population
  order. Every training-perfect genome is verified on all 10,000 inputs, cached by full genome
  bytes. There is no training-fitness early exit. Deadline aborts are marked incomplete and
  never treated as censoring.
- **Executor.** Evolution uses `rust_tag_outputs` and sampling uses `rust_tag_screen`; both
  call the same `Tape::tag(0, a, 0, 0, …)`, so the random-search baseline and the evolution
  runs share semantics.
- **Statistics.** The KM median equals the ⌈n/2⌉-th order statistic used in the bootstrap
  under a common administrative cap. α = 0.05/12 per comparison per look. F / E / R are
  mutually exclusive, and unestimable medians or bounds give U. `look()` never rewrites a
  resolved comparison. `overall()` matches the plan's routing grid, including "a one-look
  screen cannot route B".
- **Queue.** One entry, 28800 s timeout, 27900 s internal deadline. Every `expect_outputs`
  file is written on the finished paths; incomplete paths exit nonzero without `COMPLETE`.
- **Critique.** All points are addressed in the plan and the code: estimator fixed before the
  pilot (KM median ratio, no AFT), unestimable → U, stopped verdicts frozen, crossover rate
  0.7 and mate policy `selected` recorded, the SE ≈ 0.14 power claim withdrawn, solve rates
  and KM curves kept visible.
- **Tests.** `tests/test_evolve_bias.py`: 15 passed. I did not rerun the 60 pre-existing
  sampling/tagged tests the plan mentions.

## Runtime check (reviewer's own runs, seeds disjoint from pilot and main)

I ran an 80-run mimic of the pilot (MASTER+555000+i, 4 workers, Rayon 1) and timed the hand
sampling.

- The mimic took 55 s wall. All 80 runs solved, between 1.2k and 167k evaluations, well under
  the smallest cap of 262,144. The longest single run was 41 s.
- Hand sampling runs at about 220 s per vector single-threaded, so about 7.5 min for both.
- The frozen design rule on the mimic picked sum2 P256 and max2 P1024, both at cap 262,144,
  with two looks allowed.

The pilot's 9000 s deadline and the 8 h envelope are therefore not at risk.

## Minor notes (non-blocking)

1. **The two-look decision has a thin margin.** The cost model is the worst pilot
   seconds-per-candidate × the full cap × 1.5. On the mimic that gave 22.6k s for two looks
   against 26.4k s available, although real runs stop at the solve and 800 of them would take
   minutes. One shortcut-heavy pilot run in a selected cell could flip the design to a
   one-look large-effect screen, which cannot route B. That would follow the frozen rule and
   stay interpretable. If it happens, the analysis should say the screen came from the
   estimator, not from real cost.
2. **Shortcut phases are common on sum2.** In the mimic most sum2 runs had populations of
   training-perfect but non-exact genomes before the exact solve (up to about 2.8k shortcut
   candidates per run); max2 mostly had none, with one run at 39k. Time-to-exact therefore
   mixes "reach training-perfect" with "drift from a shortcut to the exact program". Report
   `shortcut_candidates` per arm next to the medians.
3. **Expect small effects.** In the mimic, uniform and hand medians differed by about 1.2–2×
   on 10 seeds (not a registered contrast, and too few seeds to mean anything). The critic's
   precision caveat stands: U or E at look 1 is likely.
4. **Elites are re-evaluated** each generation and count as evaluations. This is the same in
   every arm and is stated in the plan.
5. The proposal says "13 other ops"; the vectors dilute 14 (Σ) and 15 (M). The frozen numbers
   are what the plan lists, so this is wording only.
6. `select_design` takes the first passing cap per size and never considers a larger cap for
   that size. This matches the plan ("smallest cap with ≥ 8/10").
