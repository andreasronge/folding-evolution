---
status: open
tags: [compositional-transfer, decoder, contextual, off-family, branch-else, replication, residual-ablation]
budget: {experiments: 1, used: 0}
---
# Do the saved contextual maps shift speed toward branch tasks, and does that shift need their contextual residuals?

Current summary: **open, no data yet.** Runs 2026-10-06-1400 and 2026-10-06-1419 were both
approved by the critic and both blocked before running by the same one-file merge conflict
(main into research/main). The steward resolved it on research/main in commit `e37c4a7`
(kept main's second-pass 0811 code review); re-proposed with the same design as run 1425.
Run 2026-10-06-0811 found, unregistered on the six "a"
continuations (50 seeds per cell), R (token steps plus row residuals) faster than M+ (token
steps only) on the two branch-else cells, 1.33× [1.05, 1.66] (5/6 starts; start 4 at 0.94), and
slower on the six linear cells, 0.65× [0.44, 0.88] (6/6). The six "b" continuations share the same M starts but were never
scored on these cells, so they are a conditional replication (not six new starting maps).

Competing explanations:
- S1: Learned residuals encode a shape preference: the shift replicates in "b" and needs R's
  context beyond its emitted token frequencies (R beats a frequency-matched token-only map).
- S2: The shift is token frequency: it replicates, but a G-based token-only map fitted to R's
  emitted token frequencies (pooled over the 32 positions under uniform alleles) reproduces it.
  This matched quantity is not positional frequency, solver supply or token frequency in
  selected populations.
- S3: It is a linear-task loss only (linear cells lack IF_GT and sit near G's floor), not a
  branch gain.
- S4: It was noise or selection on six maps and does not replicate.

Scope: eight frozen non-PA cells from run 0001 (two branch-else, six linear) on D1331; saved
maps only, no new learning. Branch-else is a related shape, not an independently trained
family, so no answer here is family specificity.

Related: [root 10](../question.md), [13](../13-post-addition-map-learning/question.md),
[0811 analysis §2.5](../../../runs/2026-10-06-0811/analysis.md),
[strategy 1400](../../../runs/2026-10-06-1400/strategy.md),
[run 1400 proposal](../../../runs/2026-10-06-1400/proposal.md) and
[critique](../../../runs/2026-10-06-1400/critique.md) (blocked),
[run 1419 proposal](../../../runs/2026-10-06-1419/proposal.md) and
[critique](../../../runs/2026-10-06-1419/critique.md) (blocked),
[run 1425 proposal](../../../runs/2026-10-06-1425/proposal.md),
[four-reducer plan](../../../plans/four-reducer-family-transfer.md).

Reopen if parked: an independently trained second family is available (the four-reducer
plan), or new starts (not continuations) of the contextual learner exist.
