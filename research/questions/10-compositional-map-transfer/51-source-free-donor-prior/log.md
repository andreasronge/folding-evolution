# Log: 51 source-free donor prior

- 2026-10-11 (steward, 1019): opened on strategy 1019. Read-only audit of the 24 saved 0833 TS libraries
  (`experiments/output/2026-10-11/2026-10-11-0833-prepare/libraries.json`): 148 entries, 144 three-node;
  most frequent X1+X2 (23 incl. both orders) and X0+X2 (24), then input+1, input+0 and input+ANY; constants
  2 and 5 rare. Entries keep source operand order (both orders occur across builds). Proposal: R-hand vs
  R-TS vs R-tree on B/C ([proposal](../../../runs/2026-10-11-1019/proposal.md)).

- 2026-10-11 (run 2026-10-11-1019, commit `e29219b`). **Experiment.** Fixed 192-entry source-free prior
  (R-hand: all 12 ordered `ADD(Xi,Xj)` × 8 and all 32 `ADD(Xi,c)`/`ADD(c,Xi)` with c ∈ {0,1,2,5} × 3; half the
  draw mass per class; built from the alphabet only) against the 24 saved, hash-checked 0833 TS libraries (R-TS)
  and plain restarted tree GP (R-tree) on gate-sum B/C. 24 build slots × 12 cells × 6 repeats = 1,728 jobs per
  arm, fresh shared seeds, unchanged 0833 search (≤ 8 × 65,536 evaluations, mix 0.5, 32-token cap). Timing-only
  stage-0 gate passed (projected 4,045 s; score ran 1,881 s). 5,184/5,184 rows, no duplicates, seed pairing exact
  ([analysis](../../../runs/2026-10-11-1019/analysis.md), [code review](../../../runs/2026-10-11-1019/code_review.md)).
  **Result.** Mean capped evaluations: R-tree 70,481 · R-TS 26,300 · R-hand 22,415; solved 1,723 / 1,728 /
  1,728. Primary **R-hand ÷ R-TS 0.852 [0.762, 0.958]** (paired 24-slot block bootstrap); worker-seconds 0.840
  [0.747, 0.950]. R-hand ÷ R-tree 0.318 [0.291, 0.349]; R-TS ÷ R-tree 0.373 [0.337, 0.411] (replicates 0833's
  0.382 on fresh seeds). Solve difference hand − tree +0.003 [+0.001, +0.005]. All three retention predicates
  hold (0.958 < 1.25; 0.349 < 0.80; +0.0006 > −0.03): **retained**. With TS acquisition (245 k [218 k, 274 k]
  evaluations per library) charged, TS never repays against R-hand within 200 searches (cumulative TS ÷ hand
  1.23 [1.10, 1.37] at 200).
  Secondary (no rules): 19/24 build slots have hand/TS < 1 (per-build points 0.48–1.78; build 20, at 1.78, clearly
  favours TS); per-unit hand cheaper 889, TS cheaper 807, tie 32 of 1,728, so the mean gain comes from TS's expensive
  tail rather than a uniform shift. Split (02|13) 0.975 [0.851, 1.125], split (03|12) 0.749 [0.621, 0.899]. One
  cell, `(X0+X2)>(X1+X3)?(X1+X2):X3`, favours TS (hand/TS 1.60 [1.12, 2.22]). TS libraries contain X0+X2 in
  24/24 and X1+X2 in 23/24 builds, X0+X3 in 6, X1+X3 in 5, X2+X3 in 1, X0+X1 in 1; the prior gives all six equal
  mass. Insertion rates: P 0.508, K 0.576 (R-TS overall 0.525).
  Explanations: (a) supported at the substitution level (upper 0.958, and the interval excludes 1 in the
  prior's favour). (b) not supported: a learned advantage above 1.25 is excluded (lower 0.762). (c)
  contradicted: R-hand ÷ R-tree 0.318, so the breadth did not dilute the saving. The split/cell pattern (hand's
  gain where TS rarely covers the needed pair; TS's win on the cell whose sums are the pairs TS concentrates on)
  is consistent with "coverage of the gate's pairs is what matters", but it is a post-hoc reading of 12 cells,
  and pair coverage, constants 2/5, entry count and missing ANY/GT entries all changed together.
  Not shown: which ingredient carries the saving; transfer to a fresh bank or other alphabet (development bank,
  `v2_x4`, prior written knowing the family sums inputs); behaviour on easy targets (cf. 50); horizons beyond
  200 searches.

  Decision: close 51 because the pre-set retained branch was met with margin on every predicate, so the question
  (does a fixed supplied sum prior keep the B/C saving?) is answered for this bank: on B/C the prior, not R-tree,
  is now the comparator any learned library must beat, and TS acquisition has no measured economic case against
  it here. Root 10's 42-slot allocation is spent and strategy 1019 reserved the next choice (unfamiliar-content
  boundary, a statistical generator, or stopping the library line) for its own review, so return to strategy
  (`next: strategy`). No hand-prior variants or ingredient matrix (strategy 1019 "What to stop").

- 2026-10-11 (steward, 1129): the fresh-bank reopen item ("rebuilt from the alphabet alone and scored against R-tree
  and a learned library") was exercised by probe [52](../52-order-helper-acquisition/log.md) without reopening 51:
  on order-helper development cells the unchanged constructor cost 2.12× [1.54, 2.91] of R-tree (93/96 solved), and
  more than the literal (1.55×) or behaviour-keyed (1.00×) libraries. The B/C saving is family-specific content, as
  expected for a sum prior on non-sum helpers; a probe observation, not a belief. Status unchanged (closed).
- 2026-10-11 (steward, 1129): correction to the 1019 entry's and the digest's wording, from
  [critique 1129](../../../runs/2026-10-11-1129/critique.md) note 5: "all jobs solved" means both donor arms solved
  1,728/1,728; R-tree solved 1,723/1,728. The numbers in the entry above were already correct.
- 2026-10-11 (steward, 1228): wording correction from [critique 1228](../../../runs/2026-10-11-1228/critique.md)
  note 9: the 1129 entry's "The B/C saving is family-specific content" claims more than the probe isolated. Better:
  the same sum prior helped B/C but harmed these order cells; content mismatch is a plausible explanation, not an
  isolated mechanism. Related: on those order development cells the uncapped acquired library of
  [53](../53-order-library-cap-release/question.md) cost 0.40× [0.32, 0.50] of R-tree; acquisition there supplied
  content a sum prior lacks, but a supplied order prior was still 7.3× cheaper. Reopen condition (a learned library
  proposed as an improvement on B/C) not met; status unchanged (closed).
