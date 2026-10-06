---
status: closed
tags: [compositional-transfer, task-family, two-family, fourth-reducer, FIRST, alias-screen, headroom, decoder-capacity, feasibility]
budget: {experiments: 1, used: 0}
---
# Does adding FIRST to SUM/MAX/MIN give two usable task families (branch-else, post-addition) for a matched/mismatched adaptation test?

Current summary: **closed, run 2026-10-06-1603 (commit `92ba7c5`, Table A row 1): no.
Branch-else has no role-covered holdout pair on D625, D1331 or D2401, so this candidate cannot
carry the symmetric two-family test under the frozen split rule.** This is exact and
Rust-checked. On D1331, 13 of 36 cells survive the ≤ 9-token, 80% screen (BE 5, PA 8). Every
cell conditioned on M or m dies. In BE's `then` role, S, F and M each occur once; the one
BE cell that could be held out alone is `S?m:(M+F)`. PA splits: holdouts `(F?S:M)+m` and
`(S?M:m)+F`, 6 training cells.

What the run measured beyond the split (50 paired seeds per cell × arm, 13 cells):
- **G4 is tractable and leaves room above the 4 096 line on every cell.** G4 solves 45–50/50,
  KM medians 8.7k–28.7k. G4 / U is 10.3× [7.9, 13.5] on BE and 8.1× [6.8, 9.6] on PA.
- **A fixed previous-token grammar carried a crossed family preference on these cells.** These
  are two hand-set priors, not learned maps. Matched over swapped grammar: BE 1.68× [1.39, 2.05],
  PA 1.32× [1.12, 1.57]. The paired context-over-marginal contrast is resolved in both
  families: 1.51× [1.09, 2.09] and 1.46× [1.16, 1.82]. The PA half is the BE grammar
  slowing PA (0.66× [0.56, 0.77] of G4). No PA improvement over G4 was resolved for the PA
  grammar: 0.87× [0.75, 1.04], admitting gains up to about 4%; point estimate below G4 on 7 of 8
  cells. Only the BE grammar had a resolved own-family gain: 1.36× [1.04, 1.75]. Context
  strengthens the preference relative to the tied-marginal controls; the marginal contrasts
  alone are unresolved (BE 1.11× [0.90, 1.36], PA 0.91× [0.76, 1.10]).
- **Projected learner cost on this bank.** G4 takes about 1.9 s per full-cap search and 0.4–1.2 s
  per 65k-cap inner search. Measured G4 costs implied a conservative pilot projection (about
  2.4 h for 4 trajectories, 4.7 h with the frozen 2× allowance); the allowance excluded stage C.
  Actual learned-trajectory runtime was not measured here. Stage C never ran: the split failed
  as well. (Run 1723 later measured 10–14 min per trajectory on this bank.)

Not concluded: anything about learned family specificity, decoder capacity for learning, or
transfer. The asymmetric designs (BE as a training-only family; the single BE holdout) were not
tested and are strategy's call.

Competing explanations / outcomes:
- S: the bank supports two families (split, headroom, cost), so the matched/mismatched test can run.
- K: hand-set family grammars (matched vs swapped rows) show a resolved family contrast. That is
  a positive witness that a previous-token decoder can carry a BE/PA difference. A missing
  contrast is inconclusive about the decoder class (two hand-set priors, not its capacity; cf.
  0132, where a hand-set PA grammar did not beat G but learned token multipliers did), and it
  does not gate learning.
- R: the split rule fails (probe prediction). The candidate is rejected; only strategy can
  approve an asymmetric design or a new candidate.

After 1603: R holds and S does not. K was observed for these two hand-set priors in both
families; context strengthens it relative to the tied-marginal controls, whose own contrasts
are unresolved. It is a positive witness only: it says nothing about whether a learner would find such a preference.

Related: [root 10](../question.md), [12](../12-generic-grammar-headroom/question.md) (the
three-reducer screen and its frozen rules), [13](../13-post-addition-map-learning/question.md),
[strategy 1536](../../../runs/2026-10-06-1536/strategy.md).

Related runs: [proposal 1603](../../../runs/2026-10-06-1603/proposal.md),
[analysis 1603](../../../runs/2026-10-06-1603/analysis.md),
[decision 1603](../../../runs/2026-10-06-1603/decision.md).

Reopen if: strategy approves a changed split rule (e.g. BE training-only, or a one-cell BE
holdout), shape or primitive for this candidate. The screen, calibration and cost numbers above
are then reusable as-is. (Strategy 1723 approved the one-cell BE holdout; that work runs in
[16](../16-crossed-family-adaptation/question.md), not as a reopening of this feasibility study.)
