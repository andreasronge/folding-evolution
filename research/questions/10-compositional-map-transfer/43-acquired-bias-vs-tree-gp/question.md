---
status: open
tags: [compositional-transfer, baseline, tree-gp, external-fitting, fragments, acquisition-cost, independent-inputs]
budget: {experiments: 1, used: 0}
---
# Does frozen A8 beat family-blind closure-based subtree GP on the independent-input families, after paying for acquisition?

Current summary: **open; two attempts stopped before scoring (runs 2026-10-10-2214 and 2239), re-proposed
as run 2026-10-10-2254 with only the scoring seed base moved.** No A8/tree evidence exists yet.
- 2214: the initializer (ramped half-and-half, depth 2–4 counted in edges) failed its 10 000-draw bound for
  the full-depth-4 bin under the 32-token cap and is impractical at the measured acceptance (1.2 × 10⁻⁷ per
  draw); the tree representation validated (16 canonicals, 1 998 random trees across three interpreters)
  ([infeasible](../../../runs/2026-10-10-2214/infeasible.md)).
- 2239: the corrected initializer (depth 1–3 edges, function root at initialization) validated, a complete
  development search smoke ran, and forced full-cap tree searches took about 50 s each at ten workers. The
  run stopped at the seed audit: the inherited seed formulas share 48 values between calibration and scoring
  ([infeasible](../../../runs/2026-10-10-2239/infeasible.md)). These are preparation observations only.

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
- (b) the complete generic tree procedure matches or beats A8 (the responsible structural feature —
  validity, subtree exchange, initialization or search-space coverage — would remain unidentified);
- (c) mixed: tree GP wins on the easy TS family and A8 on DG.

Scope: development data (8 DG spare cells of `x4-double-gate-v1`, 8 TS targets of `x4-branch-sum-v1`),
saved 1717 builds, `v2_x4`, D625, P 256, lexicase on 64 cases, cap 524 288. A comparison of complete
procedures, not a causal effect of learning.

Opened 2026-10-10 (steward, run 2026-10-10-2214) on [strategy 2214](../../../runs/2026-10-10-2214/strategy.md)
and its [plan](../../../plans/typed-gp-acquisition-value.md). Slot 35 of root 10.

Related: [40](../40-independent-input-protected-transfer/question.md) (its reopen clause anticipates a
stronger baseline), [41](../41-same-alphabet-family-preference/question.md),
[42](../42-family-bias-component-transfer/question.md), [run 2214 proposal](../../../runs/2026-10-10-2214/proposal.md), [run 2214 infeasible](../../../runs/2026-10-10-2214/infeasible.md),
[run 2214 decision](../../../runs/2026-10-10-2214/decision.md), [run 2239 proposal](../../../runs/2026-10-10-2239/proposal.md), [run 2239 infeasible](../../../runs/2026-10-10-2239/infeasible.md),
[run 2239 decision](../../../runs/2026-10-10-2239/decision.md), [run 2254 proposal](../../../runs/2026-10-10-2254/proposal.md), [log](log.md).

Reopen if: (set when closed or parked). If the 2254 retry fails any gate (seed audit, replays, Stage 0
timing or solve diagnostics), park with the measured obstacle and return to strategy; no further amendment.
