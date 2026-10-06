---
status: closed
tags: [compositional-transfer, task-family, two-family, crossed-design, decoder, token-multipliers, FIRST, fresh-start]
budget: {experiments: 3, used: 0}
---
# Does adapting G4's token multipliers to branch-else versus post-addition make that family's own withheld compositions easier than the other family's training does?

Current summary: **closed after stage 2 (run 2026-10-06-2229, commit `33fcee2`, row 4). On
the three withheld cells, both families' token maps beat G4 about 2–3× (all six arm × cell
gains resolved), and no matched-family advantage was detected: matched over mismatched 1.02×
[0.84, 1.25] on the BE holdout and 0.96× [0.79, 1.15] on the two PA holdouts. A matched
advantage above about 1.25× is excluded in both directions; one of 1.1× is not.** Fairly sure
of the numbers; narrow in scope (three screened cells, one of them BE; one learner; G4's
hand-supplied context; 10 independent trajectories per family).

Stage 2 (2229): 20 frozen stage-1 maps plus G4, 400 shared fresh seeds per holdout, 524k cap,
trajectory as the unit. Gains over G4 on the holdouts: BE maps 2.01× [1.86, 2.18] (BE cell),
2.59× [2.41, 2.77] (PA cells); PA maps 1.97× [1.63, 2.39] (BE cell), 2.48× [2.07, 2.96] (PA
cells). Pre-stated within-map interaction 0.98× [0.83, 1.15]. The BE bound sits at the margin
(upper 1.2485): dropping any one of 14 maps lifts it to 1.25–1.30, so "bounded below 1.25×" on
BE is fragile; the reading (generic transfer, preference unresolved below about 1.3×) is not.
Holdout gains match or exceed the training gains, so these maps did not overfit their training
cells in any way these holdouts can detect. Cell identity moves the gain by about 50%; the
training family by a few percent in the point estimates (intervals allow up to about 1.25×).

Stage 1 (1723, commit `db96645`, row 4): 10 independent trajectories per family. Own-family
training gain over G4: BE 2.18× [1.98, 2.40], PA 2.27× [1.95, 2.65]. Off-family training
cells: 2.07× [1.94, 2.21] and 1.93× [1.61, 2.30]; all 20 maps had positive estimated gains
averaged over the other family's training cells. In-sample matched over mismatched 1.13× [0.93,
1.37] (BE) and 1.10× [0.93, 1.29] (PA), both unresolved; 8 of 10 cell point estimates favoured
matched training, the other two within 0.02 log2 of zero. These in-sample point estimates did
not reappear on the holdouts.

Uses the screened four-reducer bank from run
2026-10-06-1603 ([15](../15-four-reducer-family-bank/question.md)) with a narrower split
than the frozen two-holdouts-per-family rule, authorized by strategy 1723 after the bank data
were seen: BE holds out `S?m:(M+F)` (trains on the other four retained BE cells), PA holds out
`(F?S:M)+m` and `(S?M:m)+F` (trains on the other six). D1331, `v2_rmin_first`, G4 (hash
`8a7b3091…`) and the 1603 roster are unchanged. This is fresh-seed transfer on a screened bank,
with one BE task; repeated learning cannot add BE task replication.

Plan: [asymmetric family transfer](../../../plans/asymmetric-family-transfer.md).

Competing explanations, after stage 2:
- A: Token learning picks up family information that reaches the withheld cells. Not
  supported at this resolution: both directional contrasts and the interaction sit within 0.06
  log2 of zero. A preference up to about 1.25× (1.3× on BE without the margin case) remains
  possible.
- B: Token learning is generic here. Fits: every arm improves every holdout 2–3×, and which
  family trained the map shifts the point estimates by a few percent. This is a bound, not equality.
- C: A crossed preference only through damage to the other family. Does not apply: no
  preference appeared, and both mismatched arms improve G4 on the other family's holdouts
  (1.97×, 2.59×, both resolved).
- D: The learner fails on one training set. Out since stage 1.

Not separated: whether the generic gain is a better token prior for this reducer family as a
whole or a correction of G4's weak spots (a union-trained or scrambled-family arm would be
needed); learned context (only token weights moved).

Related: [root 10](../question.md), [15](../15-four-reducer-family-bank/question.md),
[13](../13-post-addition-map-learning/question.md),
[strategy 1723](../../../runs/2026-10-06-1723/strategy.md),
[analysis 1723](../../../runs/2026-10-06-1723/analysis.md),
[decision 1723](../../../runs/2026-10-06-1723/decision.md),
[analysis 2229](../../../runs/2026-10-06-2229/analysis.md),
[decision 2229](../../../runs/2026-10-06-2229/decision.md),
[08-evolve-bias](../../01-map-bias/08-evolve-bias/question.md) (root 01's version: fitted
frequencies barely beat the other family's fit, 1.7–1.8×, unresolved).

Reopen if: a bank with at least two covered BE holdouts (BE task replication) becomes
available; a learner that can change context, not only token weights, shows a resolved
training gain over the token learner on this bank; or the owner funds a detection-sized rerun
for a 1.1× preference (about 64–75 trajectories per family, 14–30 h of learning plus 2–6 h of
holdout scoring).
