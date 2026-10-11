---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, acquisition-cost, source-portability]
budget: {experiments: 1, used: 0}
---
# Does the unchanged tree-library recipe, rebuilt from branch-sum (TS) sources, still make restarted tree GP cheaper on gate-sum B/C?

Current summary: **closed (run 2026-10-11-0833, commit `28db964`). On gate-sum B/C, 24 libraries rebuilt by the
unchanged 0150 extractor from the four TS source cells cut mean evaluations to 0.382 [0.335, 0.433] of restarted
tree GP, with no reliability loss (1,728 vs 1,723 of 1,728 solved). That is the pre-set portable branch (upper
< 0.80). R-TS ÷ size-matched random donors was 0.406 [0.344, 0.482].** The saving holds in 24/24 builds and
12/12 cells. TS acquisition costs 0.245 M evaluations per library, about 12× less than DG, and repays after
about 6 B/C searches (DG: about 64).
- TS versus DG libraries on B/C: 1.03 [0.86, 1.22], independent cohorts. Unresolved: a difference of up to
  about 15–20% either way is not excluded.
- On the native TS targets, both libraries **raised** cost: R-TS ÷ R-tree 1.78 [1.58, 2.00], R-DG ÷ R-tree
  1.33 [1.12, 1.57], all jobs solved. Plain R-tree solves 98.7% of these on the first attempt; the fixed 0.5
  library mix adds restarts and a tail. Followed up as parked [50](../50-library-easy-target-harm/question.md).
- Audit (observational, two cohorts): TS libraries are almost all 3-node pair and input+constant sums with
  no `GT(ADD,ADD)` predicate (0/24, DG 21/24). Every TS library has pair sums for both B/C splits; 18/24 DG
  libraries have none, yet both cohorts give a similar saving. So neither the predicate nor split-matched pairs
  seem necessary for the B/C saving. What is sufficient is not identified; generic small `ADD` supply is a
  hypothesis consistent with [48](../48-tree-donor-label-supply/question.md).

Competing explanations:
- (a) the recipe is portable: TS sources yield pair-sum-rich libraries that cut B/C cost much like DG's
  (R-TS well below R-tree, near R-DG);
- (b) DG-specific content carried the B/C gain (e.g. `GT(ADD,ADD)` skeletons usable after relabelling): R-TS
  near R-tree or the size control, R-DG well below;
- (c) TS libraries help related TS tasks only: native gain, no B/C gain (a reuse limit, not a recipe failure).

Reading: (a) supported for this source pair and destination (R-TS ÷ R-DG is unresolved, not shown equal);
(b) not supported; (c) contradicted, since B/C was helped and native TS was harmed.

Scope: development rosters only (TS source/target cells of `x4-branch-sum-v1`, gate-sum B/C of
`x4-gate-sum-v1`); one extractor, 0.5 library mix and restart schedule; one TS cohort. Not a fresh-bank
transfer claim and not a claim about unfamiliar instruction content (TS and DG share ADD and indexed inputs).

Opened 2026-10-11 (steward, run 2026-10-11-0833) on [strategy 0833](../../../runs/2026-10-11-0833/strategy.md)
and its [plan](../../../plans/tree-library-source-portability.md); closed the same day. Slot 41 of root 10.

Related: [45](../45-tree-subtree-library/question.md), [46](../46-tree-library-fresh-composition/question.md),
[47](../47-tree-donor-arrangement/question.md), [48](../48-tree-donor-label-supply/question.md),
[44](../44-restarted-tree-vs-a8/question.md) (TS R-tree baseline), [41](../41-same-alphabet-family-preference/question.md)
and [42](../42-family-bias-component-transfer/question.md) (A8-era DG/TS crossing; no TS library difference resolved
on TS cells), [50](../50-library-easy-target-harm/question.md) (native harm),
[proposal](../../../runs/2026-10-11-0833/proposal.md), [analysis](../../../runs/2026-10-11-0833/analysis.md),
[decision](../../../runs/2026-10-11-0833/decision.md), [log](log.md).

Reopen if: (closed) a later experiment needs the TS-versus-DG library difference on B/C resolved (about 800
further builds by the harness's price, so only with a much cheaper design); or another source roster or a
fresh bank shows TS-style predicate-free libraries failing on a destination where DG libraries help
(R-TS ÷ R-tree lower > 0.80 with R-DG upper < 0.80).
