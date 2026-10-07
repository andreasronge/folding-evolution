---
status: closed
tags: [compositional-transfer, decoder, token-multipliers, selection-noise, contextual-learning, rank-one, fresh-start]
budget: {experiments: 2, used: 0}
---
# Does a more reliable selection score make token continuation from the saved maps learn, and then does compact context add to it?

Current summary: **closed after run 2026-10-07-1137 (row 6, 1 of 2 slots). With 96 searches per
candidate (2 + 6 loop, 12 generations, 9 600 searches per trajectory), token continuation from the
16 saved 1723 maps improved fresh training search: T/S 1.143× [1.089, 1.200] on 0821's fresh seeds
(16/16 starts) and 1.122× [1.031, 1.222] on a new seed block. In that same loop, rank-one context
steps (half of all steps) added no resolved increment over token-only continuation under equal
search funding: C/T 0.967× [0.871, 1.073] (pre-registered bound < 1.15× met; the 95% interval
admits a 13% loss to a 7% gain).** Scope: these starts, the ten training cells, this loop and
the ½ token/context mixing rule. Not shown: why this loop climbed and 0821's did not (searches
per candidate, generations and total searches all changed together); whether learning had
plateaued (T/T_mid 1.058× [0.990, 1.130], in-loop curve still falling); whether context helps
when added on top of a full token budget (C made half as many token proposals, and its token
component was slower in the point estimate: C0/T 0.932× [0.860, 1.010], unresolved); per-start or per-family token gains
(F1/F2 per-start correlation 0.15).

Measured before the first run (steward probe on 0821's raw rows): per-search variance of a
shared-seed child-minus-parent difference 3.95 log2² (seed correlation ≈ 0.22), so a 24-search
difference has noise sd 0.41 and a 96-search one 0.20, against a true token-step sd of about
0.17 (0821 stage A, σ²_T 0.028 [0.005, 0.051]): reliability ≈ 0.15 → 0.41. The 16 saved starts
differ little on BE (true between-start sd ≈ 0.04 log2) and more on PA (≈ 0.25), so headroom for
token tuning is likelier on the weaker PA starts.

Competing explanations:
- A: The saved maps can still improve by token steps; 0821's selection was too noisy to find the
  improving steps. A more reliable score climbs.
- B: The saved maps sit near a plateau for this token operator (σ 0.5 on three coordinates);
  better scoring finds parent-level steps, not better ones. Consistent with BE's tight start
  spread and 0821's selected mutants not being resolved from their parents (−0.017 [−0.085, +0.041] log2).
- C: Progress needs depth more than per-step reliability; a 4× more reliable but shorter loop
  trades one limit for another.
- D (inherited from 18, conditional on A): in a loop that climbs, compact rank-one context does
  or does not add to equally funded token tuning.

Status by explanation: A supported for this procedure (resolved T/S on two seed blocks; the
cause is not isolated to scoring reliability). B not supported as stated: the maps were not at a
plateau for this operator at this budget. C not tested separately (the run did not vary depth at
fixed reliability). D answered at this scope: no resolved increment, gain above 1.073× excluded.

Scope: the ten 1723 training cells (4 BE, 6 PA) of the frozen 1603 bank, D1331,
`v2_rmin_first`, G4, saved 1723 token maps BE1–8 and PA1–8 as starts. No holdout is touched.
Results apply to these token-tuned starts and this operator; improvement from G4 is a different
question (1723 already showed it).

Related: [root 10](../question.md), [18 compact context](../18-compact-context-learning/question.md)
(its reopen condition was met by run 1137; closed at its tested scope),
[concept plan](../../../plans/selection-calibrated-continuation.md),
[strategy 1137](../../../runs/2026-10-07-1137/strategy.md),
[run 0821 analysis](../../../runs/2026-10-07-0821/analysis.md),
[run 1723 analysis](../../../runs/2026-10-06-1723/analysis.md),
[run 1137 analysis](../../../runs/2026-10-07-1137/analysis.md),
[run 1137 decision](../../../runs/2026-10-07-1137/decision.md).

Reopen if: a context design that does not displace token steps (context added after or on top
of a full token budget, or learned jointly from G4) is funded and needs this loop's measured
token rate (about 0.17–0.19 log2 per 9 600 searches from these starts) as its control; or a
replication of the learning trajectories (not just fresh re-scoring) is needed before root 10
cites the 1.12–1.14× token gain as settled.
