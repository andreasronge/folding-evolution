---
status: open
tags: [compositional-transfer, task-family, two-family, crossed-design, decoder, token-multipliers, FIRST, fresh-start]
budget: {experiments: 3, used: 0}
---
# Does adapting G4's token multipliers to branch-else versus post-addition make that family's own withheld compositions easier than the other family's training does?

Current summary: **open, stage 1 done (run 2026-10-06-1723, commit `db96645`, row 4).
The token learner improves G4 about 2.2× on both training sets, and most of that gain is
generic; the in-sample family preference is small and unresolved (1.13× [0.93, 1.37] BE,
1.10× [0.93, 1.29] PA). Holdouts not yet scored.** 10 independent trajectories per family.
Own-family gain over G4: BE 2.18× [1.98, 2.40], PA 2.27× [1.95, 2.65]. Off-family training
cells: 2.07× [1.94, 2.21] and 1.93× [1.61, 2.30], so neither family's maps hurt the other.
Matched arm ahead on 8 of 10 training cells (2 tied); a post hoc within-map interaction is
1.24× [1.09, 1.41], suggestive only. The mean learned vectors differ by about half the
within-family spread (permutation p 0.20). Stage-2 size rule fixed n = 10 per family.

Uses the screened four-reducer bank from run
2026-10-06-1603 ([15](../15-four-reducer-family-bank/question.md)) with a narrower split
than the frozen two-holdouts-per-family rule, authorized by strategy 1723 after the bank data
were seen: BE holds out `S?m:(M+F)` (trains on the other four retained BE cells), PA holds out
`(F?S:M)+m` and `(S?M:m)+F` (trains on the other six). D1331, `v2_rmin_first`, G4 (hash
`8a7b3091…`) and the 1603 roster are unchanged. This is fresh-seed transfer on a screened bank,
with one BE task; repeated learning cannot add BE task replication.

Plan: [asymmetric family transfer](../../../plans/asymmetric-family-transfer.md).
Stage 1 (run 2026-10-06-1723, done): 10 independent G4-based token-multiplier trajectories
per family, fresh training scores on all ten training cells, no holdout scoring. Stage 2
(proposed as run 2026-10-06-2229): the 20 frozen maps plus G4 on the three holdouts, 400
fresh seeds each, no new trajectories.

Competing explanations:
- A: Token learning picks up family information: matched maps beat mismatched maps on the
  withheld cells of their own family, and beat G4.
- B: Token learning is generic here: both families' maps speed all holdouts about equally
  (equality only to the intervals' resolution).
- C: A crossed preference appears only because the other family's map hurts (degradation,
  as with the hand-set BE grammar on PA in 1603).
- D: The learner does not improve G4 on one or both training sets at this budget, so the
  crossed question cannot be asked of it.

After stage 1: D is out for this learner and budget (both families L, lower bounds near 2×).
C does not apply on training cells (off-family gains 1.9–2.1×). A versus B is open: in-sample
the matched preference is about 1.1× and unresolved, so stage 2 should be expected to bound it
more often than resolve it.

Related: [root 10](../question.md), [15](../15-four-reducer-family-bank/question.md),
[13](../13-post-addition-map-learning/question.md),
[strategy 1723](../../../runs/2026-10-06-1723/strategy.md),
[analysis 1723](../../../runs/2026-10-06-1723/analysis.md),
[decision 1723](../../../runs/2026-10-06-1723/decision.md).

Reopen if parked: a bank with two covered holdouts in both families becomes available, or a
learner that can change context (not only token weights) shows a resolved training gain over
the token learner. (The earlier condition, a learner with gains on both training sets, is now
met by run 1723.)
