---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, donor-content, mechanism, label-supply]
budget: {experiments: 1, used: 0}
---
# Once learned donor shapes are kept, do tree donors still need the learned label law?

Current summary: **closed (run 2026-10-11-0652, commit `163f005`): on gate-sum's predicate-unmatched splits
B/C, replacing the learned labels with uniform labels within each compatible class, on the same skeletons,
widths, sizes and multiplicities, lost most of the donor gain: mean evaluations R-unif ÷ R-perm 2.07 [1.68,
2.61] (registered loss: lower > 1.10, point ≥ 1.25), R-unif ÷ R-lib 1.95 [1.64, 2.32].** R-unif stayed
cheaper than plain restarted tree GP (0.755 [0.645, 0.884]) but kept only about 40% of R-perm's per-search
saving, and repays acquisition after about 169 searches against about 65. Reliability: 1,725 vs 1,727 of
1,728 solved (difference −0.0012 [−0.0046, +0.0017]). The loss holds in 23/24 builds, 12/12 cells, both
splits and all three realizations. Guards passed; 47's retention replicated (R-lib ÷ R-perm 1.06 [0.88, 1.29]).
- Uniform labels on learned shapes were not resolved from 0150's random size-matched donors (R-size ÷ R-unif
  1.095 [0.864, 1.367]; similar tails, budget curves and solver-use rates), so skeletons alone do not carry the
  gain; a skeleton effect up to about 30% under uniform labels is not excluded.
- The uniform law changed ADD share (84% → 49% of binary nodes), ANY share (5% → 20% of inputs), constants and
  the finite-library dependencies at once, and cut distinct-input pair sums to about a third of R-perm's. Which
  of these carries the gain is not identified; pair-sum supply is a hypothesis.
- Not shown: that a learner must fit these exact frequencies (an intermediate law, e.g. per-class marginals,
  is unpriced); transfer beyond this development bank and cohort.

Competing explanations:
- (a) the learned label law (84% ADD among binary nodes, 5% ANY among inputs) carries the B/C gain, plausibly
  through general pair-sum supply: R-unif loses worthwhile against R-perm, near R-size;
- (b) learned skeletons and widths carry it: R-unif ≈ R-perm, well below R-tree;
- (c) neither alone: R-unif between R-size and R-perm, unresolved against both.

Reading: (a) supported as a replacement result (uniform labels lose a worthwhile amount, R-unif near R-size);
(b) not supported (R-unif resolved worse than R-perm, lower bound 1.68); (c) not supported as stated (R-unif
resolved against R-perm, unresolved against R-size).

Scope: development bank `x4-gate-sum-v1`, one DG acquisition cohort (0150), one extractor, one uniform law.

Opened 2026-10-11 (steward, run 2026-10-11-0652) on [strategy 0652](../../../runs/2026-10-11-0652/strategy.md)
and its [plan](../../../plans/tree-donor-label-supply.md); closed the same day. Slot 40 of root 10.

Related: [47](../47-tree-donor-arrangement/question.md), [46](../46-tree-library-fresh-composition/question.md),
[45](../45-tree-subtree-library/question.md), [29](../29-frequency-matched-transfer/question.md) (tape
analogue: frequency projections lost C's advantage; here a frequency-*preserving* rearrangement kept the
donor gain and a frequency-*flattening* relabelling lost it),
[proposal](../../../runs/2026-10-11-0652/proposal.md), [analysis](../../../runs/2026-10-11-0652/analysis.md),
[decision](../../../runs/2026-10-11-0652/decision.md), [log](log.md).

Reopen if: (closed) a statistical donor generator (PIPE-like or per-class marginals) is proposed and needs to
know which label component to fit, in which case run single-component replacements (ADD share only, ANY
share only, constants only) first; or a later experiment on another bank or cohort shows uniform-label donors
matching the learned-label ones (R-unif ÷ R-perm upper < 1.25).
