---
node: questions/01-map-bias/09-generic-bias-speedup
title: Is R's sum>2 speed-up the max>2 shortcut route? REDUCE_MAX removal × shortcut-blocking training sets (sum>2, n 600)
---

## Why this now

This follows the [strategy](strategy.md): use root 01's last experiment for one causal test of
the max>2 stepping stone (G3). It reopens [09](../../questions/01-map-bias/09-generic-bias-speedup/question.md)
under its reopen condition (c), "a direct test of the max>2 stepping stone on sum>2". I will
record the reopening in 09 at the decide step. No parked question's condition is met: 02
still needs an owner request, 07 has no testable B-helper copy, and 04 depends on 07.

The residual effect is R on sum>2. R is the max-fit vector's shape with INPUT and GT reset
to uniform. It reaches an exact solve 1.61× sooner than uniform (99.5% CI 1.23–2.01), even
though it samples only 0.23× as many exact solvers
([1814 analysis](../2026-10-05-1814/analysis.md)). R raises REDUCE_MAX 3.46× and lowers
REDUCE_ADD to 0.49×. max>2 is training-perfect on 80% of sum>2 training sets. R and X runs
meet about 10× more training-perfect inexact programs than U and IG. In the saved shortcuts,
about half agree exactly with max>2 on the full domain in every arm. At least one exact max>2
shortcut was saved in 118 of 250 R runs, against 83 of 250 U runs. All of this is
association. The strategy asks for an intervention whose side effects can be separated from
the route.

## The design: two interventions, crossed

Each intervention has a known side effect. Crossing them lets each one control for the
other's side effect.

**Factor 1: remove the supply (vector).**
- **R** is 1814's frozen sum>2 R vector.
- **R−M** is R with REDUCE_MAX set back to 1/22. The freed mass (about 0.11) is spread over
  the other 19 non-INPUT/GT ops in R's proportions, so each rises about 1.15×. INPUT and GT
  stay at 1/22.
- Side effect: every other op rises a little, including REDUCE_ADD, sum's own aggregator
  (0.49 → 0.56 × uniform). That pushes R−M to be *faster*. The bias therefore works against
  finding a route effect.

**Factor 2: remove the reward for the shortcut (training set).** The domain is 0–9⁴. Of the
9,985 sum>2 positives, only 66 separate the two tasks: the lists in {0,1,2}⁴ with sum ≥ 3.
The current sampler draws 32 positives with replacement, so about 81% of sets contain none
of these lists, which matches 201 of 250 sets.
- **Admit (A):** positives are drawn only from the other 9,919. max>2 is then
  training-perfect by construction. Negatives are unchanged.
- **Block (B):** the same set for the same seed, with 8 of the 32 positives replaced by
  separating lists. max>2 now fails 8 of 64 cases. Under lexicase it loses every selection
  event in which a separating case comes up before the pool narrows to it.
- Side effect: B changes selection and the case mix for every arm. Blocking also weakens the
  route without removing it, because a 56/64 program can still be a stepping stone. k = 8 is
  my judgement: strong enough that max>2 is no longer near-elite, and still 24 of 32
  positives unchanged. The plan may argue for a different k before freezing, but not after.

**Cells** (sum>2 only; max>2 has no such shortcut): A×U, A×R, A×R−M, B×R, B×R−M. U on A
re-anchors R's gain on forced-admit sets, which differ from 1814's natural mix.

**Fixed setup.** 1814's harness at `31d4408` (`evolve_bias_components.py` on top of
`evolve_bias.py`): TAG, L 64, P1024, lexicase, crossover v2 0.7 with a selected mate,
mutation 0.015, cap 262,144. An exact solve means correct on all 10,000 lists. Only the
R−M vector and the A/B training samplers are added. New master seed. 600 paired seeds per
cell; within a seed, all cells share the evolution seed and B's set is derived from A's. One
look.

**Contrasts.** Each contrast is a ratio of median evaluations to the first exact solve, with
a paired seed bootstrap. There are four registered contrasts, so each gets a 98.75% interval:
1. **C1 = U÷R on A**: does R's gain still hold here?
2. **D_A = (R−M)÷R on A**: does removing the REDUCE_MAX raise cost speed when the shortcut is
   rewarded?
3. **D_B = (R−M)÷R on B**: the same comparison when the shortcut is not rewarded.
4. **I = D_A ÷ D_B**: does the REDUCE_MAX effect depend on the shortcut being
   training-perfect?

**Practical threshold, fixed now:** τ = 1.25. That is about half of R's log gain over
uniform (√1.61 ≈ 1.27). "No practically meaningful contribution" means removing REDUCE_MAX
costs R less than about half its gain.

**Precision.** The plan reruns 1814's check on its saved sum>2 R and U times. It must report
two probabilities at n = 600: that D_A's upper bound falls below 1.25 when D_A = 1, and that
D_A's lower bound exceeds 1 when D_A = 1.6. Each should be ≥ 0.80. If either falls short, the
plan may raise n to at most 800. It may not move τ. The interaction has less power. My rough
estimate is that it resolves only if blocking removes most of the route (I ≳ 1.4), and the
outcome table treats it that way.

**Runtime.** 3,000 runs. In 1814, sum>2 runs averaged 2.2–3.3 CPU-s, so this is about 2.7
CPU-h, or about 45–60 min on 4 workers. Add one 125M-tape sample of R−M (about 4 min) to
show its exact-solver supply, which is descriptive only. Queue timeout 2.5 h.

**Descriptive, no gates:** first generation at training accuracy 1.0 and 0.75; saved
shortcuts with their full-domain max>2 agreement; and, if cheap in the harness, whether the
first exact solver's parent(s) compute max>2 exactly. Ancestry shows the route was used, not
that it was needed.

## What each outcome would mean

Gate first: if C1's lower bound is ≤ 1, R's gain is not reproduced on forced-admit sets.
I report that and make no route claim.

| Result | Meaning |
|---|---|
| D_A lower > 1 **and** I lower > 1 | **Route supported.** R's speed needs the extra REDUCE_MAX, and this need is larger when max>2 is training-perfect. Access to the max>2 shortcut causally helps reach exact sum>2 in this harness. The redistribution side effect cannot explain the dependence on training set. Training-set changes affect R and R−M equally, so they cannot explain it either. Still one task, one vector, one harness. |
| D_A upper < 1.25 | **Practically meaningful contribution ruled out.** Removing the max>2 supply costs R less than half its gain. G3 does not explain R's sum>2 speed-up. Its gain over uniform remains unexplained by anything tested. |
| D_A lower > 1, I unresolved (D_B also > 1, or I spans 1) | **Supply matters, route unconfirmed.** R needs REDUCE_MAX, but the run cannot show that it acts through the shortcut's training-perfect status. Two readings remain: max>2 is a stepping stone even at 56/64, or REDUCE_MAX helps sum>2 some other way, for example inside exact solvers. A decode of REDUCE_MAX on the solvers' output path is reported but cannot decide. |
| D_A interval contains 1 and reaches above 1.25 | **Unresolved** at n = 600. Reported as unresolved. |
| I lower > 1 but D_A not resolved > 1 | Reported literally (the blocking effect is real, but its size on A is not resolved). No route claim. |

## After the run

I report the bounded answer and stop this threshold line, whatever the
result. There will be no precision extension and no sweep of k or REDUCE_MAX levels. 09 closes
on a supported or ruled-out route. It is parked otherwise, with no new reopen condition from
this line. This uses root 01's last experiment, and 09's second. The program then returns to
strategy.

## Alternatives considered

- **Only R vs R−M.** This cannot separate the route from the redistribution and from
  REDUCE_MAX uses other than the shortcut. The strategist warns exactly about this. Rejected.
- **Only admit vs block on R.** This cannot separate the route from training-set effects on
  selection. Rejected for the same reason.
- **U+M (uniform with REDUCE_MAX raised).** This tests whether REDUCE_MAX alone is
  sufficient. It is a different question from what makes R fast. Dropped to keep the run
  focused.
- **Splitting 1814's natural sets by shortcut admission.** This was already done: 49 seeds,
  and the separating sets carry only about 1 separating case each. It is association and has
  no power. Rejected.
- **Ancestry tracing alone.** It gives the route's use, not its necessity. It is kept only
  as a descriptive add-on.
- **Spending the slot elsewhere** (02, 08's specificity, ≥650-pair IG vs X): this would go
  against the strategy, and no reopen condition is met.

**Budget.** 09 has 2 experiments with 1 used, and this uses the second. Root 01 has 1 left,
and this uses it.
