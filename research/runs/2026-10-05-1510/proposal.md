---
node: questions/01-map-bias/08-evolve-bias
title: Sum vs max families — is there a family-specific op-frequency bias that transfers to held-out members? (sampling only, CI-gated)
---

**Why this now.** Part 2 of the root question ("evolve the map's bias") is still untested, and
[08](../../questions/01-map-bias/08-evolve-bias/question.md) is open with budget 3, used 0.
The critic has accepted the direction twice. It sent back
[run 0040](../2026-10-05-0040/critique.md) for design and
[run 1505](../2026-10-05-1505/critique.md) for three points: the pruning control, fit
validation on exact success, and C/D verdicts that rule out a worthwhile effect. This version
keeps 1505's design (shared TAG alphabet, frozen split, uniform-only calibration, reciprocal
matrix, evolution in a later gated cycle) and changes only what the critique asked for:

| Critique point | Change |
|---|---|
| Pooled 95% pruning rule can floor an op that a rare task needs | Knockouts are run per fitting task. An op is pruned only if it is **observed** to run in solvers, it never breaks a solver of **any** task, and the **joint** knockout is harmless. Ops that are absent or barely used stay uniform. Support counts are reported. |
| Validation must be on P(exact), with uncertainty, per task | A fit is validated only if, on **every** retained fitting task, the P(exact) ratio to uniform is ≥ 3× with a 95% lower bound > 1. |
| Easy tasks could swamp the elite update | Elites are **exact** solvers, not training-perfect ones. Each task gets **equal weight** in the update. |
| C/D need a CI that rules out a worthwhile effect; inconclusive comes first | Every comparison is classified G / N / U (below). C and D need N, i.e. an upper bound < 3×. U at the cap is inconclusive, and inconclusive outranks every other outcome. |
| Prune within 3× doesn't mean "generic" if specificity holds | Specificity (matched vs mismatched) and gain over pruning are now **two separate axes**. Only specificity decides A vs C. |
| Extend by uncertainty, not by count; benchmark costs | Pools are extended until each decision comparison resolves, up to a cap. Throughput of the fitted distributions and the cost of the exhaustive check are measured first. |
| Calibration stop rule | The run stops after calibration if fewer than 2 fitting tasks per family, or no eligible holdout after the substitutes, remain. |
| Aggregator vs threshold construction | Added the critic's **aggregator-swap** diagnostic. It is descriptive only. |

**Setup (frozen now; same as 1505).**
- **Alphabet.** TAG alphabet, ops 0..21, tape length 64, tags uniform, slots 12/13 = NOP,
  threshold 0, so op 19 pushes 0 everywhere. `op_weights` covers ops 0..21.
- **Tasks.** Every task is a predicate on length-4 lists over [0,9]. "Exact" means correct on
  all 10,000 lists, checked exhaustively. Training uses 64 label-balanced cases per task, and
  one screening set holds their union, so a tape is executed once and scores all tasks.
- **Σ family** (SUM, REDUCE_ADD). Fit on sum>5, sum>10 and sum>15. Hold out sum>7 and sum>12.
  Substitute holdouts, in order: sum>8, then sum>11.
- **M family** (REDUCE_MAX). Fit on max>2, max>5 and max>7. Hold out max>3 and max>6.
  Substitute holdouts, in order: max>4, then max>1.

**What would run.** One queue entry with sampling only, no evolution. The steps run in order,
and code applies every gate automatically and logs it before the next step starts.

0. **Benchmark (≈ 5 min).** Measure tapes/s for uniform and for a crude enriched vector
   (aggregators, constants, GT, SEP ×3), and the cost per exhaustive check. Pool sizes below
   are then scaled to fit the timeout in priority order. Anything cut is reported as
   unresolved, never as N.
1. **Calibration (uniform, 30M; may extend to 60M).**
   - **Eligibility.** A task is eligible if it has ≥ 10 exact hits and P(exact) ≤ 1e-3.
   - **Substitution.** An ineligible holdout is replaced by its next substitute, and an
     ineligible fitting task is dropped.
   - **Stop.** The run stops here, with outcome *infeasible task set*, if fewer than 2 fitting
     tasks per family remain or a family has no eligible holdout left. The calibration table
     is still reported.
   - **Extension.** Up to 60M if any fitting task has < 20 exact solvers. The pruning control
     below needs ≥ 20 per task.
   - **Freeze.** The final task set is logged and frozen here.
2. **Pruning control (`prune`, from the calibration pool, blind to family).**
   - **Knockout.** For each op o other than SEP and RECV, and each retained fitting task t,
     delete every o cell of each exact solver and count how many solvers stop being exact:
     k(o,t).
   - **Candidates.** An op is a candidate if k(o,t) = 0 for every t and it runs in ≥ 5
     solvers pooled. That is harmless use that was observed, not inferred from absence.
   - **Joint check.** Delete all candidates together. If any solver of any task breaks,
     remove candidates one at a time, least-used first, until the joint deletion breaks
     none.
   - **Weights.** Survivors go to the floor (0.05× uniform); every other op stays uniform.
   - **Report.** Per op and task: present / executed / broken counts. Ops kept because they
     are absent or barely used are listed separately.
3. **Fitting.** Three fits: Σ-fit, M-fit and both-fit.
   - **Method.** Cross-entropy over op weights, 3 independent starts per fit, ≤ 6
     iterations, hard cap 15M tapes per fit.
   - **Elites.** Each task's exact solvers in that iteration's sample.
   - **Update.** The mean over the fit's tasks, weighted equally, of each task's op frequency
     in its elites' executed cells. A task with < 10 elites keeps its previous contribution.
     The update is smoothed (α 0.5) with every op floored at 0.05× uniform.
   - **Objective.** Mean log P(exact) over the fit's tasks.
4. **Validation.** For each start, draw 5M fresh tapes; the uniform reference is the
   calibration pool.
   - **Rule.** A start is validated if, on every retained fitting task, its P(exact) is ≥ 3×
     uniform with a 95% lower bound > 1.
   - **Selection.** Keep the best validated start by mean log ratio.
   - **Report.** Every start's ratios, the spread across starts, and which ops moved and by
     how much.
   - **Failure.** No validated start for Σ-fit or M-fit makes the run *inconclusive*.
5. **Transfer matrix (fresh pools; each pool scores all tasks).**
   - **Decision vectors.** uniform, Σ-fit, M-fit and prune. Each starts at 10M and is
     extended in 10M steps, up to 40M, while any decision comparison it enters is U.
   - **Reported only, 10M each.** both-fit, plus **Σ-swap** and **M-swap**: each fit with the
     total mass of SUM+REDUCE_ADD exchanged with that of REDUCE_MAX, and all other weights
     unchanged. If the aggregator carries the specificity, Σ-swap should look like M-fit on
     M holdouts, and vice versa. This separates the aggregator from threshold-constant
     construction.
   - **Fitting tasks are re-reported** from these fresh pools. This removes the
     winner's-curse bias left by choosing starts on their validation scores.

**Size.** Calibration 30–60M, fitting ≤ 45M, validation 45M, transfer 70–190M. Total about
190–340M tapes. The 2026-10-04-2135 run did about 270M tagged evaluations in 2.3 h, and
enriched tapes run more cells, so I expect **3–5 h; timeout 6 h**, under the 8 h cap. Step 0
rescales pool sizes if fitted tapes are much slower.

**How results are read.** For a ratio R = P(exact | X) / P(exact | Y), use a 95% CI from the
Poisson counts. The worthwhile gain is **3×**: §1's ≤ 2× decoder differences predicted
nothing, while §28's ≈ 4× weight-driven change moved solve rates by 30–70 points.
- **G (gain):** lower bound > 1 and point estimate ≥ 3.
- **N (no worthwhile gain):** upper bound < 3. This includes "real but small", which is
  reported as such.
- **U (unresolved):** anything else. A 1.6–5 interval with point 2.8 is U.

Family-level verdicts use the mean of the family's two holdout log-ratios, with the combined
variance. Each holdout is also reported on its own. All fitted vectors are trained on fitting
tasks only, so every holdout comparison is out of sample.

- **Specificity, per family:** matched vs mismatched fit on that family's holdouts.
- **Gain, per family:** matched vs uniform.
- **Beyond pruning, per family:** matched vs prune. This is reported on its own axis and never
  changes the outcome class.

**Outcomes, in precedence order.**
1. **Infeasible task set:** the calibration stop fired. Report it. Next, the steward picks a
   different family pair or parks.
2. **Inconclusive:** Σ-fit or M-fit not validated, or any comparison that would decide the
   outcome is still U at the cap. This does not support parking as C or D. If 08 is parked
   afterwards for budget, the note will say the question is unresolved, and that decoder rules
   are not shown to be needed.
3. **A, family-specific transfer:** specificity G and gain G in **both** families.
   - Meaning: there is a family-specific frequency bias, and it can be fitted from some
     members and transfers to unseen ones.
   - Next: a gated evolution cycle on the holdouts.
     - Arms: uniform / matched / mismatched / prune, 50 paired seeds.
     - Worthwhile: median time to first exact ≥ 1.5× shorter, or solve rate ≥ 15 points
       higher, with paired CIs.
   - If beyond-pruning is N, the claim narrows: the fit's gain over uniform is no larger than
     junk removal, and what is family-specific is mainly that the other family's fit costs
     you. The evolution cycle still runs, with prune as the key control.
4. **Partial A:** specificity G and gain G in one family, with the other family N on
   specificity or on gain.
   - The evolution cycle may run on the specific family only.
   - The asymmetry is reported, for example a family whose holdouts are already near the
     eligibility ceiling under uniform.
5. **C, generic:** specificity N in both families while at least one family's gain is G. The
   fits help, but not because they fit the family. Park the frequency-only version of part 2
   by 08's stop rule.
6. **D, no transfer:** both fits validated, but gain N in both families. Also D: specificity
   G with gain N, meaning the mismatched fit hurts while the matched fit gives nothing worth
   evolving toward. Park, as for C.

The both-fit position, the swap diagnostic and prune vs uniform are reported in every outcome.
None of them changes the class. If both-fit ≈ matched, that means one map can carry both
families' biases, not that the effect is generic.

**Prior.** I expect A at the sampling level, mostly carried by the aggregator: the swaps
should roughly reverse the specificity. This is the easy case on purpose, a positive control
for the knob. If even sum vs max shows no specific, transferable fit, the frequency-only part 2
is dead cheaply. If A holds, the open question becomes whether evolution cares. Item 12 says
frequency is a supply rate, and §28 says supply moves solve rates under a fixed budget. That is
the next cycle.

**What would leave us no wiser, and how it is handled.**
- Fits that gain only on training cases: elites and validation use exact solvers.
- Sparse cells and intervals spanning 3×: extended until resolved, else inconclusive.
- A weak pruning control: per-task, observed-use, jointly checked, and only ever a side axis.

None of these is allowed to park the question as C or D.

**Alternatives considered.**
- *Evolution in this queue:* premature until a validated, specific fit exists. Both critiques
  agree.
- *A hand-set aggregator bias only (no fitting):* this tests the knob, not whether a bias can be
  fitted from some members. It is kept as the swap diagnostic.
- *Importance-reweighting one uniform pool:* likelihood ratios over 64 cells make its variance
  unusable, and fresh pools are cheap.
- *Composite tasks (mbs_and/or/xor) as holdouts:* uniform P(exact) is probably near zero.
  Kept as an option for the evolution cycle.
- *Parked questions:* no reopen condition is met. [02](../../questions/01-map-bias/02-fixed-target-sampling/question.md)
  still needs the owner's wish. [07](../../questions/01-map-bias/07-shared-arrival/question.md)
  has no testable B-helper single copy and no in-situ replay, so
  [04](../../questions/01-map-bias/04-random-start-discovery/question.md) stays parked too.

**Budget.** 08 has 3 experiments, 0 used. This would be the 1st; the gated evolution cycle
would be the 2nd, and a heritable-weights test the 3rd. The root has 4 left, and this uses 1. The
stop rule is unchanged: a clean C or D parks the frequency-only version of part 2.
