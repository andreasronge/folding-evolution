---
status: parked
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, acquisition-cost, comparator, order-helpers, semantic-keying]
budget: {experiments: 1, used: 0}
---
# Can the subtree-acquisition recipe learn order helpers (pairwise min/max) from evolved sources, and what limits it?

Current summary: **parked after one probe (run 2026-10-11-1129, commit `db30b15`); observations only, six
development cells, protected roster never searched.** Bank `x4-order-v1` on `v2_x4`/D625: sources `lo(a,b)+Xc`,
`hi(a,b)+Xc` (24), destinations `lo(a,b)+hi(c,d)` (30; 6 development, 24 protected), built from ordinary GT/IF_GT
([plan](../../../plans/order-helper-acquisition.md)). The unchanged literal extractor (R-L) held an order helper in
0/8 builds and was dearer than plain restarted tree GP (R-L/R-tree 1.55× [1.09, 2.17] in geometric cost); a
behaviour-keyed extractor on the same solvers (R-S) held one in 3/8 builds (a destination-needed one in 2/8) and was
not resolved from R-tree (1.00× [0.68, 1.46]). A supplied 12-helper order prior was about 20× cheaper than R-tree
(0.048× [0.04, 0.06]); neither learned arm recovered any of that gap. Evolution does build the helpers (63% of 384
source solvers contain their own), but mostly in bloated or syntactically varied forms; literal keying pools them in
5/96 helper × build cases, behaviour keying in 49/96, of which 44 lost to the 16-entry cap under cells-first ranking
(each helper recurs in at most 2 source cells; 3-node sums, comparators and a constant class reach 3–8). The 1019
sum prior raised cost here (2.12× [1.54, 2.91]). Whether an included helper speeds search is unresolved (post-hoc,
24 pairs: 0.67× [0.33, 1.31]). These are probe observations, not beliefs.

Competing explanations for a failure to acquire helpers:
- (a) evolution does not build the helper as a reusable unit (nothing to extract);
- (b) it does, but in varied literal forms, so literal-canonical recurrence misses it (a keying limit);
- (c) helpers are extracted but crowded out by ubiquitous 3-node sums/comparisons under the 16-entry,
  cell-count ranking.

Probe reading (1129, observations): (a) not supported (census 63%); (b) is the limit of the unchanged recipe;
under behaviour keying (c) is the first limit, emission size (> 9 nodes) the second. R-S changes keying, pooled
sizes and representative choice together, so its gain over R-L (0.65× [0.43, 0.97]) implicates that bundle.

Related: [45](../45-tree-subtree-library/question.md) (recipe; reopen item iii, unfamiliar content),
[51](../51-source-free-donor-prior/question.md) (fresh-bank reopen condition; R-sum),
[50](../50-library-easy-target-harm/question.md) (library harm; R-tree first-attempt rate here 56%, below its
90% trigger; irrelevant donors still raised cost here), [47](../47-tree-donor-arrangement/question.md), [strategy 1129](../../../runs/2026-10-11-1129/strategy.md),
[run 1129 analysis](../../../runs/2026-10-11-1129/analysis.md), [decision](../../../runs/2026-10-11-1129/decision.md), [log](log.md).

Reopen if: strategy funds a test of whether a changed extractor (e.g. ranking that does not structurally exclude
2-cell classes, a larger cap, or filtering semantically constant classes) converts acquired helpers into a
destination saving — that test needs a pre-stated rule on the development cells first, and the frozen protected
roster and near-alias rule only after it; or a parameterized-abstraction method (DreamCoder-like) is proposed and
needs a bank where literal reuse is known to fail; or a decision needs order helpers as a fresh-content check for
another library method. Reuse the saved 1129 libraries, census and rows for descriptive follow-ups without new search.
