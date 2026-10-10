---
status: closed
tags: [compositional-transfer, family-specificity, crossed-design, acquisition-cost, external-fitting, independent-inputs]
budget: {experiments: 1, used: 0}
---
# On one alphabet, does cheap acquisition learn a useful preference for its own task family?

Current summary: **closed after run 2026-10-10-1717 (answered in one direction at this scope).** Every
earlier specificity test compared two closely related output-addition families and was unresolved near
1.0–1.1× ([16](../16-crossed-family-adaptation/question.md), [20](../20-solver-corpus-context/question.md),
[25](../25-comparison-gate-transfer/question.md)). This question crossed two families on the same alphabet
(`v2_x4`, D625), executor and A8 recipe: double-gate DG `(Xa+Xb)>(Xc+Xd) ? Xe:Xf` and branch-sum TS
`Xa>Xb ? Xc+Xd : Xe+Xf` (both canonicals: six readouts, two ADD, GT, IF_GT). 24 DG-built (D, from run 1536)
and 24 TS-built (T, fresh) builds were scored with G4 on 8 never-searched cells per family, 48 shared seeds
per cell ([analysis](../../../runs/2026-10-10-1717/analysis.md)).

- **On the DG cells the DG-built cohort was clearly better:** cost(T)/cost(D) **2.98× [2.07, 4.33]** with
  failures at 2 × cap, 2.40× [1.76, 3.30] at 1 × cap; 8/8 cells; solved D 307/384, T 187/384, G4 59/384.
- **On the TS cells the direction is unresolved:** cost(D)/cost(T) **1.29× [0.94, 1.78]** (a T advantage
  up to about 1.8× or a small D advantage not excluded). This roster is near ceiling for both fitted cohorts
  (95–97 % solved; G4 69 %), so it had little power to separate them. Not evidence of equality.
- The geometric interaction √(P_DG·P_TS) was **1.96× [1.58, 2.44]**, above the pre-set 1.5× margin at 2 × cap
  but not at 1 × cap (1.75× [1.45, 2.12]); it is carried almost entirely by the DG direction. Not reciprocal;
  no cohort was resolved better on both rosters.
- Both cohorts were useful on both rosters against G4 (lowest: T on DG 2.75× [2.20, 3.47]).
- TS sources were far easier to solve (G4 first batch 63 % vs 17 %), and T builds cost half the evaluations.

Competing explanations, after 1717:
- (a) family-dependent acquisition: **supported in the DG direction**; reciprocity unresolved, limited by the
  TS roster's headroom;
- (b) one shared correction to a poor prior: **not sufficient** — the TS-built correction loses about 3× to the
  DG-built one on DG cells, although it still beats G4 2.75×;
- (c) one bias dominates: not resolved (D not resolved better on TS; D's TS interval allows up to 1.78× worse);
- (d) one-sided specialization without usefulness: not supported (all four arm/G4 ratios ≥ 2.2× lower bound).
- Not separated: the DG advantage could come from the `(a+b)>(c+d)` join content of DG fragments/context or
  from learning on a harder source family; context, fragments and supply are bundled.

Scope: external fitting (context table + literal fragments, frozen), not inheritance; one pair of families on
one alphabet; DG target cells come from development bank `x4-double-gate-v1` (never searched, but the bank's
method and split were tuned on it); TS bank new and performance-blind; G4 a weak supplied prior; capped cost at
cap 524 288; output ranges differ (TS −4..4, DG −2..2), so the preference is family-level, not pure ADD placement.

Opened 2026-10-10 (steward, run 2026-10-10-1717) on [strategy 1717](../../../runs/2026-10-10-1717/strategy.md)
and its [plan](../../../plans/same-alphabet-family-preference.md). Slot 33 of root 10. Closed 2026-10-10.

Related: [40](../40-independent-input-protected-transfer/question.md),
[39](../39-independent-input-family-bank/question.md), [16](../16-crossed-family-adaptation/question.md),
[25](../25-comparison-gate-transfer/question.md), [run 1717 proposal](../../../runs/2026-10-10-1717/proposal.md),
[run 1717 analysis](../../../runs/2026-10-10-1717/analysis.md),
[run 1717 decision](../../../runs/2026-10-10-1717/decision.md), [log](log.md).

Reopen if: a decision comes to depend on the TS direction (e.g. choosing per-family versus one acquisition for
an output-addition family), and a branch-sum roster with headroom exists (G4 solving at most about a third and
fitted arms well below ceiling at this cap, or a lower cap fixed in advance); or a saved-build attribution
(context-only vs context + fragments, D and T on the DG roster) shows the DG advantage is carried by a component
whose family dependence this design could not see.
