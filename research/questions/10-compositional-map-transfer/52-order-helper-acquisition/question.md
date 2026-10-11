---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, acquisition-cost, comparator, order-helpers, semantic-keying]
budget: {experiments: 1, used: 0}
---
# Can the subtree-acquisition recipe learn order helpers (pairwise min/max) from evolved sources, and what limits it?

Current summary: **closed after the 1129 probe (commit `db30b15`) and its follow-up experiment
[53](../53-order-library-cap-release/question.md) (run 1228, commit `60ab766`); six development cells, protected
roster never searched.** Bank `x4-order-v1` on `v2_x4`/D625: sources `lo(a,b)+Xc`,
`hi(a,b)+Xc` (24), destinations `lo(a,b)+hi(c,d)` (30; 6 development, 24 protected), built from ordinary GT/IF_GT
([plan](../../../plans/order-helper-acquisition.md)). Answer: no order helper entered the eight capped literal
libraries in the 1129 probe (the uncapped literal recipe remains untested); a behaviour-keyed extractor put a needed
helper in most libraries once its 16-entry cap was removed, and that library then saved search (53).

Probe 1129 (observations): the unchanged literal extractor (R-L) held an order helper in
0/8 builds and was dearer than plain restarted tree GP (R-L/R-tree 1.55× [1.09, 2.17] in geometric cost); a
behaviour-keyed extractor on the same solvers (R-S) held one in 3/8 builds (a destination-needed one in 2/8) and was
not resolved from R-tree (1.00× [0.68, 1.46]). A supplied 12-helper order prior was about 20× cheaper than R-tree
(0.048× [0.04, 0.06]). Neither learned arm met the probe's continuation rule; point estimates recovered none of the
gap, while R-S's benefit was unresolved. Evolution does build the helpers (63% of 384
source solvers contain their own), but mostly in bloated or syntactically varied forms; literal keying pools them in
5/96 helper × build cases, behaviour keying in 49/96, of which 44 lost to the 16-entry cap under cells-first ranking
(each helper is required by two source targets and was observed only in those targets' solvers; 3-node sums,
comparators and a constant class reach 3–8 cells). The 1019 sum prior raised cost here (2.12× [1.54, 2.91]).

Experiment 53 (full, pre-registered, 24 new builds): the uncapped behaviour-keyed library (R-all) cost 0.40×
[0.32, 0.50] of R-tree in capped arithmetic mean evaluations and 0.33× [0.27, 0.39] of capped R-S on the same
corpora; capped R-S cost 1.23× [1.07, 1.41]. A needed helper was in the R-all pool in 126/144 cell × build pairs
(R-S 14/144). So cap crowding, located by the probe, was a real obstacle to useful acquisition under behaviour
keying (helper causality not isolated; see 53). The literal-keying limit remains a probe observation.

Competing explanations for a failure to acquire helpers:
- (a) evolution does not build the helper as a reusable unit (nothing to extract);
- (b) it does, but in varied literal forms, so literal-canonical recurrence misses it (a keying limit);
- (c) helpers are extracted but crowded out by ubiquitous 3-node sums/comparisons under the 16-entry,
  cell-count ranking.

Probe reading (1129, observations): (a) not supported (census 63%). Helpers are often present; literal pooling,
cap crowding, nonrecurrence (26/96) and emission size (> 9 nodes, 21/96) restrict usable coverage. R-S changes
keying, pooled sizes and representative choice together, so its gain over R-L (0.65× [0.43, 0.97]) implicates that
bundle. Run 1228 (53) confirmed that removing the cap turns behaviour-keyed acquisition into a saving.

Related: [53](../53-order-library-cap-release/question.md) (uncapped follow-up), [45](../45-tree-subtree-library/question.md) (recipe; reopen item iii, unfamiliar content),
[51](../51-source-free-donor-prior/question.md) (fresh-bank reopen condition; R-sum),
[50](../50-library-easy-target-harm/question.md) (library harm; R-tree first-attempt rate here 56%, below its
90% trigger; irrelevant donors still raised cost here), [47](../47-tree-donor-arrangement/question.md), [strategy 1129](../../../runs/2026-10-11-1129/strategy.md),
[run 1129 analysis](../../../runs/2026-10-11-1129/analysis.md), [decision](../../../runs/2026-10-11-1129/decision.md), [log](log.md).

Reopen if: (closed) a parameterized-abstraction method (DreamCoder/Stitch-like) is proposed and needs a bank where
capped literal reuse acquired no helper (R-L here, 0/8 probe builds); or a decision needs to know whether literal keying alone, without the cap,
would acquire the helpers. Reuse the saved 1129 and 1228 libraries, census and rows for descriptive follow-ups
without new search. Further work with the uncapped extractor belongs under 53 or a new question.
