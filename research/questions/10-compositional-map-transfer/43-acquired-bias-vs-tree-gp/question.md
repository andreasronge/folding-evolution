---
status: closed
tags: [compositional-transfer, baseline, tree-gp, external-fitting, fragments, acquisition-cost, independent-inputs]
budget: {experiments: 1, used: 0}
---
# Does frozen A8 beat family-blind closure-based subtree GP on the independent-input families, after paying for acquisition?

Current summary: **closed (run 2026-10-10-2254, commit `c32ff04`): on DG cells frozen A8 showed no ≥ 1.5×
geometric advantage (failures charged at 2 × cap) over this frozen closure-based subtree GP, while keeping
positive arithmetic savings; on TS cells tree GP was much cheaper (descriptive).** Development rosters,
evaluations as the unit, one tree configuration (crossover mix 0.5 selected on source/development cells,
frozen before target scoring). *Superseded in part by [44](../44-restarted-tree-vs-a8/question.md): with both
procedures restarted at 65,536 evaluations, A8's reliability lead and arithmetic saving disappeared (R-tree ÷
R-A8 0.792 [0.682, 0.915] in evaluations), though A8 remained cheaper in worker seconds.*
- **DG (primary)**, Q = cost(tree) ÷ cost(A8) at 2 × cap: **0.961 [0.683, 1.352]**, inside the [0.67, 1.5]
  margin (lower end 0.013 above it). An A8 advantage of 1.5× is excluded; a tree advantage up to about 1.46×
  is not. At 1 × cap 0.785 [0.583, 1.055], unresolved. Not equality: the ratio hides two opposite effects.
  A8 solved 314/384, tree 202/384 (G4 19/128); when tree GP solved it was fast (median 6 784 evaluations
  against 57 088; faster in 134/165 pairs both solved). Failed tree searches crowded the 32-token cap (about
  half their programs at 32 tokens, 35–42% of offspring rejected as oversize); half of them found only D625
  shortcuts.
- **Arithmetic (actual evaluations)**: A8 saves 85 714 [47 278, 123 791] evaluations per DG search, so its
  12.5 M acquisition repays after about 146 [99, 269] searches per build; tree GP is about 1.6× slower per
  evaluation and cost more worker time per DG search (28 s vs 12 s).
- **TS (descriptive)**: Q 0.175 [0.142, 0.217]; 7/8 cell intervals below 0.67 (worst 0.40 [0.22, 0.74]);
  solved tree 382/384, A8 372/384. A8 never repays on TS.
- Both arms are far cheaper than G4 (tree ÷ G4 0.105 [0.075, 0.147] DG, 0.024 [0.018, 0.033] TS).
- Two earlier attempts stopped before scoring: 2214 on an impractical initializer (full-depth-4 bin
  1.2 × 10⁻⁷ acceptance under the 32-token cap), 2239 on a calibration/scoring seed collision in the plan
  ([log](log.md)).

Reading: explanation (a) is not supported; (b) holds on TS and is not excluded on DG; on DG the arms trade
reliability (A8) against speed when solving (tree). Which part of A8 (table, library, learned content) buys
its reliability, and whether a size-aware or larger-limit tree GP would close the gap, is untested.

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
[run 2239 decision](../../../runs/2026-10-10-2239/decision.md), [run 2254 proposal](../../../runs/2026-10-10-2254/proposal.md), [run 2254 analysis](../../../runs/2026-10-10-2254/analysis.md),
[run 2254 decision](../../../runs/2026-10-10-2254/decision.md), [log](log.md).

Reopen if: a decision comes to depend on (i) the DG direction under 1 × cap or in worker seconds (tree GP
possibly better), (ii) whether a size-aware or larger-limit tree GP removes the DG reliability gap (its
failures sat at the 32-token cap), or (iii) A8 against tree GP on a fresh bank frozen with both procedures.
The saved rows of run 2254 answer descriptive follow-ups without new search.
