---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, acquisition-cost, order-helpers, semantic-keying, library-size]
budget: {experiments: 1, used: 0}
---
# Does keeping every eligible recurrent semantic class turn source acquisition into a useful order-task search bias?

Opened 2026-10-11 by the steward on [strategy 1228](../../../runs/2026-10-11-1228/strategy.md) and the
[cap-release plan](../../../plans/order-library-cap-release.md). Meets [52](../52-order-helper-acquisition/question.md)'s
reopen condition (a changed extractor with a pre-stated rule on development cells first).

Current summary: **closed after run 2026-10-11-1228 (commit `60ab766`): yes on the six development cells of
`x4-order-v1`; protected cells never searched; not a transfer claim.** R-all is the behaviour-keyed extractor (R-S)
with its top-16 truncation removed: every class recurring in ≥ 2 source cells at 3–9 nodes, one minimum
representative each, uniform donor draws, half the mutation donors, restarted tree GP (≤ 8 × 65,536). 24 new
independent acquisitions (1,152/1,152 source jobs solved, about 214 k evaluations per build); libraries R-S 16
entries, R-all 25–37 (median 28). 576 seed-paired jobs per arm. Ratio of pooled capped arithmetic means, 95%
bootstrap over whole builds:

- **R-all / R-tree 0.40 [0.32, 0.50]** (pre-stated rule: upper < 0.80 → useful acquisition; lower > 0.67 would have
  ended the recipe). Cheaper in 24/24 builds (range 0.06–0.99) and all six cells (0.35–0.47); all 576 jobs solved
  (R-tree 574). Geometric 0.24 [0.20, 0.29]; worker seconds 0.40 [0.31, 0.50].
- R-all / R-S (capped, same corpora) 0.33 [0.27, 0.39]; R-S / R-tree **1.23 [1.07, 1.41]**: the capped library is a
  cost here, not a wash (1129's 8-build probe gave 1.00 [0.68, 1.46]).
- The supplied 12-helper order prior stays far cheaper: R-all / R-order 7.27 [5.49, 9.81]; R-all recovers about
  half the 2.97-nat R-tree → R-order log gap. No repayment against R-order is claimed.
- Acquisition repays against R-tree after about 4.9 [3.8, 6.5] searches in evaluations.

Descriptive, post-extraction (not tested claims): a destination-needed helper sits in the pool in 126/144 cell ×
build pairs (both helpers 53/144) for R-all against 14/144 (both 0/144) for R-S; helpers rank 14–37 under the
cells-first key, behind 3-node classes recurring in 3–10 cells. Cost falls with coverage: R-all / R-tree 0.77
[0.50, 1.12] with no needed helper (18 pairs), 0.45 with one (73), 0.23 with both (53). 382/576 R-all solvers
contain a needed-helper library entry, against 43/572 for R-S; per-draw insertion rates are similar (0.45 vs
0.50).

Against the competing explanations for failure: (a) dilution did not cancel the gain; (b) 382/576 R-all solvers
contain a needed-helper library entry (containment; donor ancestry not traced, so use is not shown); (c) 18/144
cell × build pairs lack a needed helper, and their cost is unresolved from R-tree (observational stratum; whether
coverage causes the cost differences is unmeasured).

Not shown: that order helpers cause the saving. Entry count, sizes, content and the trivia share of draws changed
together, and the no-helper stratum is also cheaper than R-S (0.58 [0.41, 0.76]), so part of the R-all/R-S gain may
be less dilution by 3-node trivia. Also not shown: transfer (same development bank and cells as 1129), any cap
between 16 and all, harm on easy targets, or any advantage over the supplied prior.

Related: [52](../52-order-helper-acquisition/question.md) (probe that located the cap limit),
[45](../45-tree-subtree-library/question.md) (recipe), [50](../50-library-easy-target-harm/question.md) (harm),
[51](../51-source-free-donor-prior/question.md) (fixed sum prior), [proposal](../../../runs/2026-10-11-1228/proposal.md),
[analysis](../../../runs/2026-10-11-1228/analysis.md), [decision](../../../runs/2026-10-11-1228/decision.md), [log](log.md).

Reopen if: (closed) a decision needs what carries R-all's saving (helper classes versus other 2-cell content versus a
lower trivia share; a helper-ablated or trivia-matched library rebuilt from the saved 1228 libraries answers it
without new acquisition); or a decision needs a cap-size curve. Scoring the 24 protected `x4-order-v1` cells or a
fresh content-family bank with the frozen R-all method is a new question under root 10, not a reopening.
