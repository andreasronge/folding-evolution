---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, acquisition-cost, independent-inputs]
budget: {experiments: 1, used: 0}
---
# Does a frozen subtree library learned from tree-GP source solvers cut restarted tree GP's DG cost beyond size-matched random donors?

Current summary: **closed (run 2026-10-11-0150, commit `d7ec100`): yes, on the DG development targets. A frozen
library of recurring source subtrees, used as half of the mutation donors, cut restarted tree GP's mean
evaluations to exact solution to 0.390× [0.332, 0.463] of R-tree's (87,352 → 34,109), and to 0.414× [0.332,
0.533] of size- and length-matched random donors; solve difference +0.008 [+0.004, +0.012] (1,536/1,536 vs
1,524/1,536).** R-lib's mean was below R-tree's in 24/24 independent acquisitions (one only at 0.98) and in all
8 target cells: 0.12× on the one target sharing the learned predicate, 0.35–0.53× on the rest. The gain shows as more first-attempt solves
(1,121 vs 715 of 1,536); few final solvers contain larger entries verbatim under the literal matcher (10/1,536
the predicate), and transformed reuse and causal pathways remain unmeasured. On a fresh gate-sum bank the same
libraries transferred, 0.250× [0.217, 0.289] ([46](../46-tree-library-fresh-composition/question.md)). With acquisition charged (2.88 M evaluations
per library) it repays after about 54 [45, 65] target searches. Worker seconds agree (0.373× [0.315, 0.443]).
- Not separated: which part of the content carries it — the `GT(ADD(·,·),ADD(·,·))` skeleton (absent from 4
  builds, which gained less: 0.26–0.98, observation), pair sums, or an input/`ADD` token-frequency shift (every
  learned entry contains an input; about a third of size controls contain none).
- The libraries are homogeneous (pair sums plus, in 20/24, the one X0+X1 vs X2+X3 predicate that 3 of 4 source
  cells share) and were already present in two 16-job stage libraries, so the 54-search repayment is an upper
  bound on what this information costs.
- Library donors entered about 11% of children (55.5% of draws oversize at the 32-token cap), not the planned
  25%. Other rates untested.

Competing explanations:
- (a) Recurring source subtrees (pair sums `ADD(Xi,Xj)`, the predicate `GT(ADD,ADD)`) carry family content
  that ordinary depth-3 random donors rarely supply: R-lib cheaper than both R-tree and R-size;
- (b) any gain comes from donor size or repetition (a small fixed donor set), not content: R-lib ≈ R-size,
  both below R-tree;
- (c) subtree search already builds these blocks cheaply, so a library adds nothing or crowds the 32-token
  cap: R-lib ≈ R-tree or worse.

Reading: (a) supported beyond donor size and compiled length, with the carrying ingredient unidentified;
(b) not supported; (c) not supported at this scope.

Scope: development data (DG source cells of `x4-double-gate-v1`; the 8 spare cells scored in 43/44), one
extractor, one library rate, one restart schedule. Not a fresh-bank transfer claim.

Opened and closed 2026-10-11 (steward, run 2026-10-11-0150) on [strategy 0150](../../../runs/2026-10-11-0150/strategy.md)
and its [plan](../../../plans/tree-native-fragment-learning.md). Slot 37 of root 10.

Related: [44](../44-restarted-tree-vs-a8/question.md) (comparator), [43](../43-acquired-bias-vs-tree-gp/question.md),
[32](../32-learned-fragment-operator/question.md) (tape fragment blocks), [proposal](../../../runs/2026-10-11-0150/proposal.md), [analysis](../../../runs/2026-10-11-0150/analysis.md),
[decision](../../../runs/2026-10-11-0150/decision.md), [tree-native plan](../../../plans/tree-native-fragment-learning.md), [log](log.md).

Reopen if: a decision comes to depend on (i) which ingredient carries the gain (hand-set {pair sums},
{comparison skeleton}, input-only token-frequency donors at the realised ~11% insertion rate), (ii) another
insertion rate, a cap-aware library, or a smaller acquisition, or (iii) the same frozen method on a fresh bank
frozen with it (a new question under root 10, not new DG seeds). The saved rows and libraries answer descriptive
follow-ups without new search.
