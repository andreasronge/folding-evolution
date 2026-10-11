---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, donor-content, mechanism]
budget: {experiments: 1, used: 0}
---
# Must transferable tree donors keep their learned label arrangements, or do shapes and primitive counts suffice?

Current summary: **closed (run 2026-10-11-0524, commit `7c0e5df`): on the two gate-sum splits no learned
predicate covers (B, C), label-rearranged libraries kept the intact libraries' gain at the registered
resolution: mean evaluations R-perm ÷ R-lib 1.031 [0.854, 1.225] (retention margin 1.25), R-perm ÷ R-tree
0.360 [0.299, 0.429], 1,728/1,728 solved in both donor arms (no loss observed; the registered 3-point
guard passed).** The intact gain replicated (R-lib ÷ R-tree 0.349 [0.301, 0.410]). On the split whose
predicate the libraries learned (A, positive control), rearrangement raised cost 5.14× [3.68, 7.14] and
removed most of A's extra gain (R-perm ÷ R-tree 0.325 on A, like B/C).
- So the A-specific extra gain needs the learned arrangement; the B/C gain does not need it at this
  resolution. An intact advantage on B/C of up to about 20% is not excluded.
- The control is one construction: labels permuted within (entry node count, compiled length, node
  arity, token width) pools, 3 frozen realizations per build. It removed the learned predicate almost
  entirely (0–1 of 63 kept) but also tripled B/C pair supply (`ADD` over the right inputs 21 → 57–62)
  and changed 78% of entries' behaviour, so retention is consistent with (b) but also with a cancellation
  between lost arrangement and gained B/C pairs.
- Not shown: what carries the B/C gain; that label counts alone (without shapes) or an unlearned
  distribution would do; that a statistical acquisition would be cheaper.

Competing explanations:
- (a) the gain needs the specific learned arrangements: rearranged donors lose a worthwhile amount
  (R-perm/R-lib lower > 1.10);
- (b) shapes, sizes and size-conditioned primitive counts suffice: R-perm ≈ R-lib (upper < 1.25), still
  well below R-tree;
- (c) the learned pairings misdirect on B/C, which need pairs the libraries almost never contain:
  R-perm < R-lib.

Reading: (b) consistent at this resolution, for this construction; (a) not supported on B/C (lower bound
0.85) but supported on A; (c) not supported (R-perm not resolved cheaper, point above 1, despite more
B/C pairs and more verbatim use of its entries in solvers: 10% vs 2%).

Scope: development bank `x4-gate-sum-v1` (protected cells spent in 0348); one DG acquisition cohort (24
libraries from 0150); one extractor, rate, restart schedule and construction; a shape built from the
libraries' own parts.

Opened 2026-10-11 (steward, run 2026-10-11-0524) on [strategy 0524](../../../runs/2026-10-11-0524/strategy.md)
and its [plan](../../../plans/tree-donor-arrangement.md); closed the same day. Slot 39 of root 10.

Related: [46](../46-tree-library-fresh-composition/question.md), [45](../45-tree-subtree-library/question.md),
[29](../29-frequency-matched-transfer/question.md) (tape analogue: frequency projections did not reproduce C;
here, for tree donors, a count-preserving rearrangement did reproduce the unmatched-split gain),
[proposal](../../../runs/2026-10-11-0524/proposal.md), [analysis](../../../runs/2026-10-11-0524/analysis.md),
[decision](../../../runs/2026-10-11-0524/decision.md), [log](log.md).

Reopen if: (closed) a statistical or generator-based donor acquisition is proposed and needs this
retention re-measured at a tighter margin (e.g. to bound a ≤ 10% intact advantage), or a later
experiment on another bank or cohort shows rearranged donors losing resolvably on predicate-unmatched
cells.
