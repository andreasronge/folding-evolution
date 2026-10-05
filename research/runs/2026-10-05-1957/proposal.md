---
node: questions/01-map-bias/09-generic-bias-speedup
title: Does R's sum>2 speed-up use the max>2 shortcut? Shortcut-veto reproduction, U/R × ordinary/veto on shortcut-admitting sets
---

## Why this now

This follows the [strategy](../2026-10-05-1945/strategy.md): spend root 01's last experiment
on one causal test of the max>2 stepping stone (G3) behind R's sum>2 gain. It reopens
[09](../../questions/01-map-bias/09-generic-bias-speedup/question.md) under its condition (c).
I will record the reopening in 09 at the decide step. No parked question's reopen condition is
met. 02 still needs an owner request, 07 has no testable B-helper copy, 04 depends on 07, and
08 needs 09 to *show* what a heritable bias must carry, not just to be reopened.

This revises [1945](../2026-10-05-1945/proposal.md) and follows the
[critique](../2026-10-05-1945/critique.md). 1945 crossed two broad interventions: an
op-vector edit (R−M) and a training-set block (B). Each changes many things besides the route,
and those side effects can interact, so the cross could not isolate max>2. Its null also bounded
only the vector edit, while the route stayed open. This version leaves vectors, cases and
variation the same, and removes **only the shortcut's access to reproduction**.

The residual is unchanged ([1814 analysis](../2026-10-05-1814/analysis.md)). R reaches an
exact sum>2 solve 1.61× sooner than uniform (99.5% CI 1.23–2.01). Yet it samples 0.23× as
many exact solvers. R raises REDUCE_MAX 3.46×. R runs meet about 10× more training-perfect
inexact programs than U runs (median 637 vs 58). All of that is association.

## What would be run

**Training sets: admit only (A).** sum>2 and max>2 differ on just 66 lists of the 10,000-list
domain: lists in {0,1,2}⁴ with sum ≥ 3. A draws its 32 positives only from the other 9,919
positives. Negatives use the existing sampler. On A, max>2 is training-perfect by construction,
so 1814's `first_exact` already evaluates **every** exact-max>2 program on the full domain. That
makes detection exhaustive at almost no extra cost. A differs from 1814's natural sets, where
about 81% admit the shortcut, so the gate C1 below re-checks R's gain on A.

**Veto.** A program is *vetoed* if it equals max>2 on all 10,000 lists. It is checked after the
exact-sum>2 check, so a solver is never vetoed, and the two tasks differ on 66 lists in any
case. The phenotype class (exact sum>2 / exact max>2 / other) is cached with the existing
byte-keyed cache. In veto cells, a vetoed program cannot be a parent in either crossover role,
cannot be cloned and cannot survive as an elite. The plan fixes how this is implemented, for
example by giving vetoed programs an all-fail case row and fitness −1 before
`_reproduce_one_island`. It must check that a vetoed program can never win a lexicase
selection or an elite slot. Two further rules are frozen before the run:
- **Fully vetoed population.** If every individual is vetoed (I expect never), the run is
  censored at the cap and counted.
- **Identity check.** Veto and ordinary runs share the seed, vector and training set. They
  must stay byte-identical until the first exact-max>2 program appears. Any divergence before
  that is a bug and stops the run. Runs in which no exact-max>2 program ever appears must
  therefore give identical times in both cells.

**Cells (sum>2 only, 4):** U-ord, U-veto, R-ord, R-veto. U is uniform. R is 1814's frozen sum>2
R vector. All cells share the seed, evolution seed and training set within a seed.

**Fixed setup.** 1814's harness at `31d4408` (`evolve_bias_components.py` on top of
`evolve_bias.py`): TAG, L 64, P1024, lexicase, crossover v2 0.7 with a selected mate, mutation
0.015, cap 262,144. An exact solve means correct on all 10,000 lists. The only additions are
the A sampler, the veto and a phenotype cache. Each run uses a new master seed and gets one
look.

**Registered contrasts.** Each is a ratio of median evaluations to the first exact solve, with
a paired seed bootstrap. There are four, so each gets a 98.75% interval.
1. **C1 = U-ord ÷ R-ord.** Gate: does R's gain hold on A?
2. **P_R = R-veto ÷ R-ord.** What does blocking the shortcut cost R?
3. **P_U = U-veto ÷ U-ord.** What does blocking the shortcut cost uniform?
4. **I = P_R ÷ P_U** (= C1 ÷ (U-veto ÷ R-veto)). Does blocking it remove part of R's advantage?

**Practical threshold, fixed now:** τ = 1.25. This is about half of R's log gain over uniform
(√1.61 ≈ 1.27). Neither τ nor the labels move after the pilot.

**Sample size: powered on the interaction, from a pilot inside the queue.** Stage 1 runs 50
seeds × 4 cells on a separate master seed. It measures veto overhead, censoring, and the
fraction of runs in which an exact-max>2 program appears before the solve. It also measures
the paired correlation between veto and ordinary times, which is high because the trajectories
stay identical until the shortcut appears. A simulation then resamples pilot pairs with
injected effects and estimates three powers at n ∈ {600, 800}:
- (a) I's lower bound exceeds 1 when I = 1.6, i.e. when the veto removes about all of R's
  gain;
- (b) P_R's lower bound exceeds 1 when P_R = 1.6;
- (c) P_R's upper bound falls below 1.25 when P_R = 1.

n is the smallest of 600 and 800 at which all three powers are ≥ 0.80. If none qualifies,
**stage 2 does not run.** The slot ends with the pilot as the result and `next: stop` for this
line, as the strategy requires when an affordable design cannot decide. Pilot runs are
excluded from every contrast. They inform only n and the overhead estimate.

**Runtime.** In 1814, 2,000 runs took about 1 h on 4 workers. This run has 200 pilot runs plus
2,400–3,200 main runs. That is about 1–1.5 h, more if the veto pushes many runs to the cap. A
capped sum>2 run costs roughly 5–10× a median one. Queue timeout 3 h, with an internal
deadline. The pilot sizes the deadline.

**Descriptive, no gates:**
- per ordinary run, whether an exact-max>2 program appeared before the solve, and when;
- per veto run, vetoed individuals per generation, peak fraction vetoed, and solves by the
  cap;
- first generation at training accuracy 1.0;
- the inexact training-perfect programs that remain in veto cells. These are approximate
  max-like routes that the veto leaves open.
- in ordinary cells, whether either parent of the first exact solver was exact-max>2. This
  uses the `lineage` hook already in `_reproduce_one_island`, plus the previous generation's
  phenotype flags. It shows that the route was used, not that it was needed.

## What each outcome would mean

The gate comes first. If C1's lower bound is ≤ 1, R's gain is not reproduced on A. I report
P_R, P_U and I literally and make no route claim. Otherwise the rows below are checked in order,
and the first match is the label. That makes the labels mutually exclusive.

| # | Result | Meaning |
|---|---|---|
| 1 | P_R upper < 1 | **The shortcut is a trap in R.** Blocking exact max>2 speeds R up. G3 as a stepping stone is out for the exact phenotype. This fits chem-tape's proxy-basin result. |
| 2 | P_R upper < 1.25 | **No practically meaningful contribution.** Blocking the exact max>2 phenotype from reproduction costs R less than about half its gain over uniform. If P_R's lower bound is above 1 as well, I add "detectable but small". This bounds the exact phenotype's reproductive role. It says nothing about inexact max-like programs, which stay available, and those counts are reported. |
| 3 | P_R lower > 1 **and** I lower > 1 | **Route supported.** Access to exact max>2 helps R reach exact sum>2, and it helps R more than it helps uniform, so it explains part of R's advantage. The share log I ÷ log C1 is descriptive. Vectors, cases and variation are identical across the veto contrast, so the redistribution and case-mix side effects that sank 1945 cannot produce this. Scope: one task, one vector, one harness, shortcut-admitting sets. |
| 4 | P_R lower > 1, I not resolved > 1 | **Stepping stone real, but not shown to be R's advantage.** max>2 helps search in R. Whether it helps R more than uniform is unresolved; if P_U is similar, it helps both. R's extra gain stays unexplained. |
| 5 | anything else | **Unresolved** at the chosen n, reported as such. |

Row 1 or 2 closes G3 for the exact phenotype. Row 3 answers 09(c) positively. Rows 4 and 5
leave the question of what R's advantage is open, with the stepping stone's role bounded as
far as the data allow.

## After the run

As the strategy sets out, I report the bounded answer and stop this threshold line whatever
the result. There will be no precision extension, no sweep of veto definitions and no B or R−M
follow-up. 09 closes on rows 1–3. On rows 4–5 it is parked with no new reopen condition from
this line. Rows 1–2 are a negative for the exact phenotype only, and I will not record them as
"G3 ruled out" without that limit. 08 stays parked unless row 3 names something a heritable
bias would need to carry. Even then, the strategist decides. This spends root 01's last
experiment and 09's second. The program then returns to strategy.

## Alternatives considered

- **1945's R−M × admit/block cross.** Rejected for the critic's reasons. Both interventions are
  broad, their side effects can interact, and its null bounds only the vector edit.
- **Veto every training-perfect inexact program, not just exact max>2.** This would cover the
  approximate routes as well. On A sets, though, it also strips lexicase's top tier wholesale,
  which changes selection far beyond the hypothesis. It would also add cells to a one-slot
  budget. It is left out. Its absence is the stated limit on rows 1–2.
- **Veto on 1814's natural sets.** Shortcut detection would be incomplete there: max>2 is
  checked only when it is training-perfect, which happens on 81% of sets. Full-domain checks
  for every individual would cost far more. Rejected in favour of A plus gate C1.
- **R vs R−M only, or admit vs block only.** These cannot separate the route from their side
  effects. Rejected, as in 1945.
- **Ancestry tracing alone.** It shows that the route was used, not that it was needed. It is
  kept only as a descriptive add-on.
- **Spending the slot elsewhere** (02, 08's specificity, the IG vs X refinement at ≥ 650
  pairs). This goes against the strategy, and no reopen condition is met.

**Budget.** 09 has 2 experiments with 1 used, and this uses the second. Root 01 has 1 left,
and this uses it.
