---
status: closed
tags: [compositional-transfer, decoder, contextual, off-family, branch-else, replication, residual-ablation]
budget: {experiments: 1, used: 0}
---
# Do the saved contextual maps shift speed toward branch tasks, and does that shift need their contextual residuals?

Current summary: **closed (run 2026-10-06-1425, row 3): the shift did not replicate.** On the
six unscored "b" continuations R / M+ was 0.94× [0.77, 1.16] on branch-else (BE) and 1.29×
[0.88, 1.91] on linear (LIN); the BE-over-LIN shift was 0.73× [0.57, 0.94], below 1 in 6/6
starts, the opposite sign to the "a" maps. The six "a" maps repeat their 0811 pattern on 200
fresh seeds (shift 1.86× [1.41, 2.44]), so that pattern belongs to those saved maps, not to the
learner: two runs of the same learner from the same starts disagree in sign. On "b", a G-context
token-only map fitted to R's pooled emitted token frequencies (R_fm) matches R (R / R_fm BE 1.04×
[0.91, 1.17], shift 1.02× [0.92, 1.12]); the pooled a/b layer's residual effect (shift 1.23×
[1.11, 1.36]) comes from the selected "a" maps and is a linear slow-down with an unresolved BE
gain. Both learners, both letters, were faster than their M start on BE (lower bounds
1.05–1.10×). Scope: six M starts (not new starts), eight frozen off-family cells on D1331,
saved maps only; 95% t intervals over six start clusters. An S1 (residual shape preference) at
the learner level is not supported at these bounds; it is not shown to be zero, and nothing here
speaks to family specificity.

Pre-run summary: run 2026-10-06-0811 found, unregistered on the six "a"
continuations (50 seeds per cell), R (token steps plus row residuals) faster than M+ (token
steps only) on the two branch-else cells, 1.33× [1.05, 1.66] (5/6 starts; start 4 at 0.94), and
slower on the six linear cells, 0.65× [0.44, 0.88] (6/6). The six "b" continuations share the same M starts but were never
scored on these cells, so they are a conditional replication (not six new starting maps).
Runs 1400 and 1419 were approved but blocked by a merge conflict; 1425 ran the same design.

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

After 1425: S4's "does not replicate" holds for the learner, but not as seed noise: the "a"
maps keep their pattern on fresh seeds, so it was selection of six particular learning runs.
S1–S3 presupposed a replicating shift and are moot at the learner level; on the "b" maps the
S2-type control (R_fm) reproduces R, which is the only dependency evidence free of selection.

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
[analysis](../../../runs/2026-10-06-1425/analysis.md) and
[decision](../../../runs/2026-10-06-1425/decision.md),
[four-reducer plan](../../../plans/four-reducer-family-transfer.md).

Reopen if: new independent starts (not continuations) of the contextual learner exist, so the
shift can be tested across starts rather than runs; or a two-family study (the four-reducer
plan) shows a contextual advantage that a frequency-matched token-only control should
explain.
