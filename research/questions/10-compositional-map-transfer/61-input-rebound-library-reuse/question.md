---
status: parked
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, signed-gates, hard-tier, input-rebinding, supplied-symmetry]
budget: {experiments: 1, used: 0}
---
# Does consistent input rebinding make the saved signed-gate libraries more useful on the signed-chain cells?

Opened 2026-10-12 by the steward on [strategy 2353](../../../runs/2026-10-11-2353/strategy.md) and the
[plan](../../../plans/input-rebound-library-reuse.md). Root 10 budget 50 → 51; this sub-question gets that slot.
Follows [58](../58-signed-gate-acquisition/question.md), [59](../59-signed-chain-depth/question.md) and
[60](../60-signed-chain-protected-reuse/question.md). The saved 1938 libraries saved 0.778× [0.696, 0.870] of
R-tree on the chain cells. That saving tracked how many of a cell's needed helpers a library held with the right
input binding. The libraries keep 8.6 of 24 helper bindings on average.

R-bind expands every entry of the 24 saved libraries into its 24 consistent X0–X3 permutations. It keeps the
learned entry weights and does not deduplicate. The input symmetry is supplied, not learned. The 24-cell roster is
exactly the permutation orbit of `p(a,b)+n(b,c)+p(c,d)`. So pooled over the roster, R-bind and R-all hold the same
content and the same average needed-helper mass. The contrast asks whether spreading that mass over all bindings in
every search (reach) beats concentrating it on the bindings the sources built (dose).

Competing explanations for the outcome:
- Reach: a little probability on every needed binding is worth more than full weight on a few. R-bind is cheaper,
  mostly where R-all held none of a cell's helpers.
- Dose: arrival needs concentrated mass. Spreading it makes R-bind no better than R-all, or worse where R-all had
  the right helpers.
- Non-helper entries rebound to the wrong roles add noise that cancels any helper gain.
- The bottleneck is helper *types* the sources never built (98/576 slots absent; build 5 has no negative gates),
  not bindings. Rebinding then closes little of the gap to R-gate.

Current summary: **parked; partly answered: rebinding helps somewhat on these development cells, but the
pre-set 10% materiality bar is unresolved.** Run 2353 (commit `465f2fa`; 24 builds × 24 cells × 6 repeats per
library arm): R-bind/R-all **0.853× [0.785, 0.927]** in pooled capped mean evaluations. A saving above 10% is not
established, one above 15% is not excluded, and harm is excluded. Precision was as forecast (log half-width 0.084).
R-bind solved more (97.7% vs 95.9%), cost 0.664× [0.545, 0.801] of R-tree (repeat-0 pairing) and repaid acquisition
against R-tree within ten searches. The supplied prior stays 2.5× cheaper (R-gate/R-bind 0.403× [0.317, 0.510]).
Validity passed (R-tree 27.4% first attempt, 7.3% capped; R-gate 100% solved).
By R-all's needed-helper coverage (descriptive, confounded), R-bind/R-all ran 0.69 / 0.87 / 1.05 / 1.24 with
0 / 1 / 2 / 3 helpers present, a gradient that survives build and cell fixed effects. Spreading helper mass over all
bindings bought reach where the literal library lacked the binding and cost dose where it had it.
Development data only: all 24 cells of `x4-signed-chain-v1` have been searched. Not transfer, not a learned
abstraction (the symmetry is supplied), not helper causality.
[Analysis](../../../runs/2026-10-11-2353/analysis.md), [decision](../../../runs/2026-10-11-2353/decision.md),
[log](log.md).

Against the explanations above: reach where literal coverage was absent and dose where it was present are both
supported descriptively. Pooled cancellation by rebound non-helpers is not supported. Missing bindings do not
explain the remaining R-gate gap, so the never-built helper types, entry weights or dilution remain candidates.

Reopen if: a design that keeps literal entry mass and adds rebound reach (e.g. literal library plus rebound copies at
reduced weight, or rebinding only entries whose binding the literal library lacks) is funded on this bank; or a
fresh-bank or deployment decision depends on whether uniform rebinding clears 10% (price: about r ≥ 14 on this
contrast, 6–7 h queue, and still a coin flip if the true ratio is about 0.86). Reuse the 2353 rows for descriptive
follow-ups.

Related: [58](../58-signed-gate-acquisition/question.md), [59](../59-signed-chain-depth/question.md),
[60](../60-signed-chain-protected-reuse/question.md), [54](../54-rectified-sum-acquisition/question.md),
[planning audit](../../../runs/2026-10-11-2353/library-planning-audit.json),
[plan](../../../plans/input-rebound-library-reuse.md), [50](../50-library-easy-target-harm/question.md) (harm-avoidance policy;
the dose loss at strata 2–3 is a related trade-off).
