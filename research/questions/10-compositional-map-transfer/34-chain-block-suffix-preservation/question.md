---
status: closed
tags: [compositional-transfer, block-edit, variation-operator, locality, suffix-preservation, external-fitting]
budget: {experiments: 1, used: 0}
---
# Does preserving the decoded suffix carry the C-chain block operator's gain over C?

Current summary: **no worthwhile gain from the boundary repair on then-addition at this resolution;
chain blocks beat C without it (run 2026-10-09-1606, commit `af8a7e5`); closed.** W (C-chain blocks
inserted on C's unchanged search, with the next allele re-encoded so the decoded suffix is kept)
beats C 1.23× [1.15, 1.31] on then-addition-v1 ([32](../32-learned-fragment-operator/question.md)).
R is the same operator without containment: same blocks and draws, the boundary allele refreshed
neutrally within the token it now decodes to, so the change may ripple on. Paired with 1036's W and
C rows (replayed bit-exactly), 16 corpora × 16 cells × 16 seeds:

- **W/R 0.954× [0.903, 1.007]** (> 1 favours the repair). A repair gain above 0.7% is excluded at this
  scope, and so is the worthwhile 1.10×; a repair cost up to about 10% is not excluded, nor is no
  difference. Same direction and bound under 1 × cap (upper 1.008), both-solved (1.031), BE (1.061),
  PA (1.016) and on the comparison-gate holdouts (0.963 [0.850, 1.092], descriptive).
- **R/C 1.286× [1.208, 1.370]**, 16/16 corpora (W/C 1.227× in the same pairs). Coordinated chain
  proposals help without containment; whether they are W's sole cause (its length law, token supply)
  is untested.
- **Ripple is frequent but local**: 64% of R's block edits change the decoded suffix, by about 3
  tokens when they do; an edit changes 4.7 tokens on average against W's 2.9. C's previous-token
  chain resynchronises quickly, so 32's "point mutation re-decodes the whole suffix" was wrong.

Competing explanations for W/C, after 1606: (a) containment — not supported, excluded above 1.007×
at this scope; (b) coordinated chain content — consistent (R/C > 1), not isolated from W's length
law or changed token supply; (c) both — not needed to explain the result. That ripple *helps*
(W/R < 1) is a direction only: rule 1 missed by 0.7%, the both-solved estimate is 0.984, and most of
the gap is 42 extra R solves in 4 096.

Scope: one externally fitted previous-token decoder (C from exact solvers; W's length law from F),
32-token tapes, blocks of 3–5 tokens; ripple rides on the block operator only, ordinary mutation and
crossover unchanged; development bank then-addition-v1. Not a general locality or GE-ripple result,
not acquisition, not transfer. Practical consequence: later acquisition baselines need not keep the
boundary repair at this resolution.

Opened 2026-10-09 (steward, run 1606) under [strategy 1606](../../../runs/2026-10-09-1606/strategy.md)
and the [plan](../../../plans/chain-block-suffix-preservation.md); slot 26 of root 10.

Related: [32](../32-learned-fragment-operator/question.md), [33](../33-pre-solve-fragment-source/question.md),
[31](../31-distribution-preserving-recoding/question.md),
[run 1606 decision](../../../runs/2026-10-09-1606/decision.md), [log](log.md).

Reopen if: a later operator or decoder makes the ripple long (e.g. a context longer than one token,
or a measured suffix change well beyond 3 tokens per edit), so containment could matter again; or an
acquisition baseline needs W versus R settled at a finer resolution than about 5% (the measured
half-width), e.g. if the ripple-helps direction (W/R 0.954) decides between two operators.
