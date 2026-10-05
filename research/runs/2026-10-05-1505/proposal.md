---
node: questions/01-map-bias/08-evolve-bias
title: Sum vs max families — does a fitted op-frequency bias transfer to held-out members, and only within its family? (sampling stage, gated)
---

**Why this now.** Part 2 of the root question ("evolve the map's bias") is still untested, and
08 is open with budget 3. The critic accepted the direction for run 2026-10-05-0040 but asked
for four changes ([critique](../2026-10-05-0040/critique.md)). This version makes them:

- **Specificity.** Family specificity is now the test: a reciprocal matched-vs-mismatched
  matrix. Both-fit stays as a benchmark, not a veto, and there is a training-defined
  irrelevant-op control.
- **Frozen split.** Alphabet, families, roles and substitutes are all fixed below, before any
  data.
- **Validated fit.** Fitting gets fresh-sample validation, several starts and a bounded
  budget, and has no surrogate objective.
- **Gate.** Evolution is cut from this queue. It becomes a separate, gated cycle with a
  minimum worthwhile gain stated now.

The question this cycle answers: **is there a family-specific frequency bias for map evolution
to find at all?**

**One shared alphabet: the tagged (TAG) alphabet.**
- It has 22 op ids, intlist only, and slots 12/13 are bound to NOP. Every op means the same
  thing in every task here.
- One trap: op 19 (THRESHOLD_SLOT) pushes `task.alphabet.threshold`. All tasks must keep the
  mbs default of 0, so op 19 means "push 0" everywhere.
- Using string tasks is dropped. The TAG interpreter does not run them, and their exactness
  cannot be checked exhaustively.
- Every task below is a predicate on length-4 lists over [0,9]. "Exact" means correct on all
  10,000 lists, checked exhaustively.

**Families and roles.** Fixed now. Tags stay uniform; `op_weights` covers ops 0..21.
- *Σ family* (family op SUM/REDUCE_ADD). Fit on sum>5, sum>10, sum>15; **hold out sum>7,
  sum>12**.
- *M family* (family op REDUCE_MAX). Fit on max>2, max>5, max>7; **hold out max>3, max>6**.
- Thresholds alternate between fit and holdout. Every threshold can be built from CONST
  0/1/2/5 with ADD/DUP, so constants are shared machinery and the aggregator is what differs.
- Each task trains on 64 label-balanced cases drawn from the 10,000 lists, not the mbs
  stratification, which leaves max>2 with about one negative.
- One fixed screening set holds the union of all training cases. A tape is evaluated once on
  it, which scores every task. Any tape perfect on a task's training cases then gets the
  exhaustive check.

**What would run.** One queue entry, sampling only, three steps.

1. **Calibration (uniform only).** Draw 30M uniform tapes and measure P(train-perfect) and
   P(exact) for all ten tasks.
   - A task is eligible if it has ≥ 10 exact hits (P ≳ 3e-7) and P(exact) ≤ 1e-3.
   - An ineligible holdout is replaced by a fixed substitute, written in code before the run:
     Σ uses sum>8, then sum>11; M uses max>4, then max>1.
   - An ineligible fitting task is dropped, provided ≥ 2 remain per family.
   - The code applies this rule automatically and logs the frozen task set before any fitting
     starts. No one looks at fitted holdout data before the split is frozen.
2. **Fitting.** Three fits: Σ-fit, M-fit and both-fit (all six fitting tasks).
   - Method: cross-entropy over op weights. The elite set is the training-perfect tapes on
     that fit's tasks (no balanced-accuracy surrogate). The update is the op frequency in
     those tapes' output-run cells, smoothed (α ≈ 0.5), with every op clamped to ≥ 0.05×
     uniform.
   - 3 independent starts per fit, ≤ 6 iterations each, and a hard cap of 15M tapes per fit.
   - Score: mean log P(train-perfect) over the fit's tasks.
   - **Validation.** For each start, measure P(train-perfect) and P(exact) on the fitting
     tasks with 5M fresh tapes. A fit counts as validated if it is ≥ 3× uniform on every one
     of its fitting tasks. Keep the best validated start, and report the spread across starts
     and the fitted vectors (which ops moved, and by how much).
   - **Irrelevant-op control (`prune`).** Built from the step-1 uniform pool and blind to
     family. An op is irrelevant if deleting all its cells leaves behaviour unchanged in ≥ 95%
     of training-perfect tapes pooled over all six fitting tasks. Irrelevant ops go to the
     floor; all others stay uniform.
3. **Transfer matrix (fresh samples).** Five weight vectors: uniform, Σ-fit, M-fit, both-fit
   and prune.
   - Each gets its own fresh pool of 10M tapes, which scores all ten tasks at once.
   - Any decision-critical cell (a holdout under uniform, a matched or a mismatched vector)
     with < 10 exact hits is extended in 10M steps, up to 40M.
   - Report P(train-perfect) and P(exact) with Poisson 95% CIs, and the log-ratios with CIs.

Total is roughly 150–250M tape evaluations. About 95% of uniform tapes have no tag-0 run and
cost almost nothing. Run 2026-10-04-2135 pushed about 270M tagged evaluations through in
2.3 h, so I expect **2–4 h; timeout 5 h**. The researcher smoke-tests throughput first and
scales the pool sizes, keeping the floors above (≥ 10 exact hits per decision cell, or report
the cell as unresolved).

**What each outcome would mean.** "Worthwhile" is set to **≥ 3× P(exact)**, for two reasons:
§1's ≤ 2× decoder differences predicted nothing, while §28's ~4× weight-driven P(exact) change
moved solve rates by 30–70 points.

- **A, family-specific transfer.** In *both* families, on at least one held-out task each,
  the matched fit beats the mismatched fit by ≥ 3×, with the 95% CI lower bound > 1. The
  matched fit also beats uniform and prune by ≥ 3×.
  - Meaning: there is a family-specific frequency bias to find, and it goes beyond deleting
    junk ops.
  - Next: the gated evolution stage, proposed as its own cycle.
    - Arms: uniform / matched / mismatched / prune on the held-out tasks, 50 paired seeds.
    - Readouts: time to first exact, plus solve rate.
    - Worthwhile there: a median time to exact ≥ 1.5× shorter, or a solve rate ≥ 15 points
      higher. Effects are reported with CIs, not just p-values.
    - These tasks sit near §1's "always solved" band, so speed is the main readout. Composite
      mbs_and/or/xor as both-fit holdouts are an option for that cycle.
- **C, generic.** Matched ≈ mismatched (under 3×, or the CI includes 1) while both beat
  uniform, *or* prune reaches within 3× of matched. The gain is "drop useless ops", not a fit
  to the family. Park the frequency-only version of part 2 by 08's stop rule.
- **D, no transfer.** The fits are validated on their own tasks but give < 3× over uniform on
  every holdout. Park, same as C.
- **One family only.** Specificity shows in one direction only. Report it as a partial A. One
  follow-up is allowed, only if the asymmetry has an obvious cause, such as the M family's
  holdouts already being near ceiling under uniform. Otherwise treat it as C.
- **Inconclusive, not parked as B/C/D.** Any of these:
  - no start validates for some fit;
  - decision cells stay under 10 exact hits at 40M;
  - the matched/mismatched CI still admits both < 1.5× and ≥ 3×.
  If the steward parks after this for budget reasons, the note will not claim that decoder
  rules are needed. A failed *static* fit also cannot rule out weights tuned to evolutionary
  trajectories, and the decision note will say so.
- **Where both-fit sits** is reported in every outcome. If both-fit ≈ matched, that means one
  map can carry both families' biases, not that the effect is generic.

**Prior.** I expect A at the sampling level, because the aggregator is a real family-specific
op. This is deliberately the easy case, a positive control for the knob: if even sum vs max
shows no reciprocal transfer, the frequency-only part 2 is dead cheaply. If A holds, the open
question moves to whether evolution cares (item 12 says frequency is a supply rate; §28 says
supply moves solve rates under a fixed budget). That is the next cycle's job.

**Alternatives considered.**
- *Run evolution in the same queue* (the last proposal). The critic was right: 240 runs before
  the fit is validated can only produce uninterpretable nulls.
- *Intlist vs string families.* No shared alphabet, and string tasks cannot be checked
  exhaustively for exactness. Dropped.
- *Composite tasks (mbs_and/or/xor) as holdouts now.* Their uniform P(exact) is probably near
  zero on a 64-cell tagged tape, which gives the sparse-count failure the critic named. Kept
  for stage 2.
- *Importance-reweighting one uniform pool instead of fresh sampling.* The likelihood ratios
  over 64 cells make the variance unusable. Fresh pools are cheap here.
- *02's rarity ladder.* Still needs the owner's wish (not recorded). 07 has no newly testable
  B-helper. Neither reopen condition is met.

**Budget.** 08: 3, used 0. This is 1. The gated evolution stage would be the 2nd, and a
heritable-weights test would be the 3rd. The root has 4 left. Stop rule unchanged: a clean C
or D parks the frequency-only version of part 2.
