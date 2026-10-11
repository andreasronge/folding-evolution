---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, acquisition-cost, order-helpers, held-out-cells]
budget: {experiments: 1, used: 0}
---
# Do the frozen 1228 R-all libraries lower search cost on the 24 order combinations kept out of development?

Opened 2026-10-11 by the steward on [strategy 1530](../../../runs/2026-10-11-1530/strategy.md) and the
[protected-reuse plan](../../../plans/order-library-protected-reuse.md). Not a reopening of
[53](../53-order-library-cap-release/question.md): 53 answered the development-cell question; its reopen note
names protected scoring as a new question.

Current summary: **closed after run 2026-10-11-1530 (commit `53f0e06`): yes, on the held-out cells of this
development bank.** The 24 saved R-all libraries, unchanged and unrefitted, were scored on the 24 never-searched
`split.protected` cells (4 disjoint-pair, 20 overlapping-pair) against R-tree and the supplied 12-helper R-order prior;
24 builds × 24 cells × 2 repeats, 1,152 seed-paired units per arm, complete grid.

- **R-all / R-tree 0.37 [0.33, 0.42]** (ratio of pooled capped arithmetic means, whole-build bootstrap). Pre-stated
  rule: upper < 0.80 with no more than 12 extra failures → useful held-out saving. R-all solved 1,152/1,152, R-tree
  1,146/1,152. Cheaper in 24/24 builds and in all 24 cells by point estimate (0.18–0.61). Development value 0.40
  [0.32, 0.50]; the held-out estimate is not visibly weaker (no direct shrinkage contrast computed).
- Strata (descriptive): disjoint 0.34 [0.25, 0.45], overlapping 0.38 [0.33, 0.42]. Post-hoc coverage gradient
  reproduced: 0 / 1 / 2 needed helpers in the library 0.74 / 0.42 / 0.19 of R-tree.
- R-order stays 6.9× [5.7, 8.6] cheaper than R-all; no repayment against it is claimed. Against R-tree, acquisition
  repays after about 4.0 [3.4, 4.6] searches (evaluations).

Not shown: transfer to a fresh bank (same bank, same twelve helpers, same source corpora); that the helpers cause
the saving (the no-helper stratum is still 0.74 [0.57, 0.93] of R-tree, and size and content vary with coverage);
inherited or per-individual acquisition; any advantage over supplied helpers.

Competing explanations if the saving shrinks (none was needed: the saving did not visibly shrink, and coverage of
protected cells matched development): (a) the six development cells were favourable (roster luck);
(b) helper coverage of protected destinations is lower in the saved pools; (c) the saving on development cells came
partly from cell-specific non-helper content.

Related: [53](../53-order-library-cap-release/question.md), [52](../52-order-helper-acquisition/question.md),
[50](../50-library-easy-target-harm/question.md), [run 1228](../../../runs/2026-10-11-1228/analysis.md),
[proposal](../../../runs/2026-10-11-1530/proposal.md), [analysis](../../../runs/2026-10-11-1530/analysis.md),
[decision](../../../runs/2026-10-11-1530/decision.md), [log](log.md).

Reopen if: (closed) a decision needs a per-cell or per-stratum result on these 24 cells (reuse the saved 1530
rows; per-cell intervals at 48 units are wide). Helper causality (a helper-ablated library) reopens
[53](../53-order-library-cap-release/question.md); a fresh content-family bank scored with the frozen recipe is a
new question under root 10.
