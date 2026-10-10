---
status: open
tags: [compositional-transfer, baseline, tree-gp, external-fitting, fragments, acquisition-cost, independent-inputs]
budget: {experiments: 1, used: 0}
---
# Does frozen A8 beat family-blind typed subtree GP on the independent-input families, after paying for acquisition?

Current summary: **open; first attempt stopped before scoring (run 2026-10-10-2214), re-proposed as run
2026-10-10-2239.** The pre-registered initializer (ramped half-and-half, depth 2–4 counted in edges) cannot
fill its full-depth-4 bin under the 32-token cap (exact acceptance 1.2 × 10⁻⁷ per draw); the tree
representation itself validated (16 canonicals, 1 998 random trees across three interpreters). No A8/tree
evidence exists yet; the retry uses depth 1–3 edges and a function root in grow ([infeasible](../../../runs/2026-10-10-2214/infeasible.md)).

Background: A8 (context table + literal block library, fitted from eight
source searches per cell) is 6–10× cheaper than the weak G4 prior on DG cells
([40](../40-independent-input-protected-transfer/question.md)) and about 3× cheaper than TS-built A8 there
([41](../41-same-alphabet-family-preference/question.md), [42](../42-family-bias-component-transfer/question.md)).
Every comparison so far is against tape search. A conventional tree representation supplies well-formed
expression structure and exchanges whole subexpressions without any learned prior. If that suffices,
A8's practical value is small and the next learning target is an increment over tree search.

Competing explanations:
- (a) A8 carries family-specific content (joins, roles) a generic structural prior lacks: A8 cheaper by a
  worthwhile margin (> 1.5×) on DG;
- (b) most of A8's gain over G4 is just "make well-formed expressions": tree GP matches or beats A8;
- (c) mixed: tree GP wins on the easy TS family and A8 on DG.

Scope: development data (8 DG spare cells of `x4-double-gate-v1`, 8 TS targets of `x4-branch-sum-v1`),
saved 1717 builds, `v2_x4`, D625, P 256, lexicase on 64 cases, cap 524 288. A comparison of complete
procedures, not a causal effect of learning.

Opened 2026-10-10 (steward, run 2026-10-10-2214) on [strategy 2214](../../../runs/2026-10-10-2214/strategy.md)
and its [plan](../../../plans/typed-gp-acquisition-value.md). Slot 35 of root 10.

Related: [40](../40-independent-input-protected-transfer/question.md) (its reopen clause anticipates a
stronger baseline), [41](../41-same-alphabet-family-preference/question.md),
[42](../42-family-bias-component-transfer/question.md), [run 2214 proposal](../../../runs/2026-10-10-2214/proposal.md), [run 2214 infeasible](../../../runs/2026-10-10-2214/infeasible.md),
[run 2214 decision](../../../runs/2026-10-10-2214/decision.md), [run 2239 proposal](../../../runs/2026-10-10-2239/proposal.md), [log](log.md).

Reopen if: (set when closed or parked). If the corrected initializer also fails its gates, park with the
measured obstacle and return to strategy rather than redesigning the baseline again.
