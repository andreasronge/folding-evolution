---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, hand-prior, acquisition-cost, comparator]
budget: {experiments: 1, used: 0}
---
# Does a fixed, source-free sum-donor prior keep the B/C saving of the acquired TS libraries?

Current summary: **closed (run 2026-10-11-1019, commit `e29219b`). On gate-sum B/C, a fixed prior of all
`ADD(input,input)` and `ADD(input,const)` forms, written from the alphabet with no acquisition, was cheaper than
the 24 acquired TS libraries: R-hand ÷ R-TS 0.852 [0.762, 0.958] in mean capped evaluations (pre-set retained
branch: upper < 1.25), R-hand ÷ R-tree 0.318 [0.291, 0.349], 1,728/1,728 solved in both donor arms.** R-TS ÷
R-tree replicated at 0.373 [0.337, 0.411]. Charged with its 0.245 M acquisition, TS never repays against the
prior within 200 searches (cumulative 1.23 [1.10, 1.37] at 200). The gain is not uniform: 19/24 build slots
favour the prior, one build and one cell clearly favour TS, and it concentrates on split (03|12) (0.749
[0.621, 0.899]; split (02|13) 0.975 [0.851, 1.125]), where TS libraries rarely hold the needed pair sums. That
pattern suggests pair coverage matters, but it is post-hoc over 12 cells and not an isolation.

Opened 2026-10-11 (steward, run 2026-10-11-1019) on [strategy 1019](../../../runs/2026-10-11-1019/strategy.md)
and its [plan](../../../plans/source-free-tree-donors.md), citing [45](../45-tree-subtree-library/question.md)'s reopen
item (i) ("hand-set {pair sums}"); closed the same day. Slot 42 of root 10.

Competing explanations:
- (a) a supplied sum prior suffices: R-hand within 1.25× of R-TS and clearly below R-tree;
- (b) the learned libraries' concentration (few pairs, constants 0/1, recurring source pairs) carries a
  worthwhile part: R-hand more than 1.25× R-TS;
- (c) uniform breadth dilutes useful pairs so much that R-hand barely beats R-tree (cf. R-unif in
  [48](../48-tree-donor-label-supply/question.md), 0.755 of R-tree).

Reading: (a) supported at the substitution level, and the interval excludes 1 in the prior's favour; (b) not
supported (a learned advantage above 1.25× excluded); (c) contradicted. Which ingredient (all six pairs, constants
2/5, 44 distinct entries, no ANY/GT entries) carries the result is not tested.

Scope: development bank (x4-gate-sum-v1 B/C), saved 0833 TS libraries, one fixed prior chosen after seeing
this program's results (source-free at execution, not task-blind), mix 0.5, one restart schedule.

Related: [45](../45-tree-subtree-library/question.md), [48](../48-tree-donor-label-supply/question.md),
[49](../49-tree-library-source-portability/question.md), [50](../50-library-easy-target-harm/question.md),
[proposal](../../../runs/2026-10-11-1019/proposal.md), [analysis](../../../runs/2026-10-11-1019/analysis.md),
[decision](../../../runs/2026-10-11-1019/decision.md), [log](log.md).

Reopen if: (closed) a learned or generated library is proposed as an improvement on B/C-type gate-sum cells
(it must then beat this prior, not R-tree); or a decision needs to know which ingredient carries the prior's
saving (then single-ingredient variants: six pairs only, constants 0/1 only, TS-matched pair mass); or a fresh
bank or alphabet is planned where this prior can be rebuilt from the alphabet alone and scored against R-tree and a
learned library.
