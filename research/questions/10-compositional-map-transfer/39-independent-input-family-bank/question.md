---
status: closed
tags: [compositional-transfer, new-family, bank-design, acquisition-cost, external-fitting, independent-inputs]
budget: {experiments: 1, used: 0}
---
# Does an independent-input double-gate bank support a fair test of cheap acquisition on a new family?

Current summary: **closed (answered at this scope, development data only).** The independent-input
double-gate bank `x4-double-gate-v1` (alphabet `v2_x4`, D625, `(Xa+Xb)>(Xc+Xd) ? Xe:Xf`) supports a
protected test: 24 mutually separated behaviours under the real-token ≤ 9-token screen, a frozen
4 source / 4 development / 8 protected split covering all three predicate pairings, and agreement of
Python, Rust and the semantic machine. Source discovery under the unchanged G4 prior is sparse
(first batch 22/128, 17% [12, 25]; per-build median 2.5/16, below the pre-stated 4/16 reading), yet
the unchanged A8 recipe completed all eight pilot builds, its adaptive batch solving 81/128. On the
four development cells (16 shared seeds per arm) the pilot observed G4 7/64, A8 55/64, old-family
A8′ reinterpreted (O) 22/64 solved; G4/A8 12.2× [6.7, 20.7], O/A8 6.7× [3.5, 12.5], magnitudes inflated
by 57/64 G4 searches at the cap. These are probe observations on hash-chosen development cells, not
beliefs; the protected comparison is [40](../40-independent-input-protected-transfer/question.md).
Pilot run: [analysis](../../../runs/2026-10-10-0311/analysis.md).

Before the run, the earlier candidates with addition inside the predicate had failed the semantic
screen on the reducer domains (at most 6 or 4 separated behaviours,
[audit](../../../runs/2026-10-10-0311/semantic-split-audit.json)).

Stage 1 asked four things:
- Does the real `v2_x4` alphabet give a validated 4 source / 4 development / 8 protected split?
- Do four G4 attempts per source cell find solvers?
- Does G4 leave headroom on the development cells?
- What would the stage-2 transfer comparison cost?

It also asked whether frozen old-family A8 builds (O) already help on the development cells.

Competing explanations for a later A8 gain on this family:
- (a) the recipe learns the new assembly from its own sources;
- (b) the generic push/ADD/GT syntax shared with the old families carries it, which the O arm checks;
- (c) the gain comes from supply alone.

This question tests none of these on protected cells. On development cells O was clearly costlier
than A8 and only modestly cheaper than G4, which bounds (b) for these eight reinterpreted
artifacts only.

Scope: one family, one alphabet and one domain (alphabet, domain and predicate placement changed
together); development cells only; 8 pilot builds; external fitting, not inheritance.

Opened 2026-10-10 (steward, run 2026-10-10-0311) under
[strategy](../../../runs/2026-10-10-0311/strategy.md) and the
[plan](../../../plans/independent-input-family-acquisition.md). Slot 31 of root 10. Closed 2026-10-10 after run 0311.

Related: [38](../38-cheap-bias-source-replication/question.md), [37](../37-cheap-bias-fresh-transfer/question.md),
[40](../40-independent-input-protected-transfer/question.md),
[proposal](../../../runs/2026-10-10-0311/proposal.md), [analysis](../../../runs/2026-10-10-0311/analysis.md),
[decision](../../../runs/2026-10-10-0311/decision.md), [log](log.md).

Reopen if: the protected comparison (40) needs a different split or more cells (8 separated cells are
spare in the frozen clique, already screened and validated but unscored), or a decision comes to
depend on why first-batch discovery is sparse under G4 on `v2_x4` (e.g. a changed prior or attempt
count would be needed for a fair acquisition elsewhere).
