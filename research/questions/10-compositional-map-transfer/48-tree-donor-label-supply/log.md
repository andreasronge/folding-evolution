# Log: 48 tree-donor label supply

- 2026-10-11 (steward, 0652): opened. Read-only probe on 0524 `libraries.json` (181 entries over 24 builds):
  binary nodes ADD 212 / GT 40; input slots X0–X3 346 / ANY 19; constants 0:34, 1:31, 2:5, 5:4. Distinct-input
  `ADD(Xi,Xj)` occurrences A/B/C (total): intact 100/1/6 (107); R-perm mean 28/27/33 (88); uniform relabelling
  (20 draws) 12/10/12 (35); 0150 size controls 10/4/9 (23). 131/181 entries have 3 nodes, where the size
  control's law is essentially the uniform compatible-label law. 0348 B/C worker s/job: R-size 5.40.

- 2026-10-11 (steward, 0652): **experiment** [run 0652](../../../runs/2026-10-11-0652/analysis.md), commit
  `163f005`. Five arms on gate-sum B/C (12 cells, 24 builds, 6 repeats, realization = repeat mod 3, 8 × 65,536
  cap, shared attempt seeds): R-tree, R-lib (intact 0150), R-perm (0524's 72 constructions, hashes re-checked),
  R-unif (each node uniform within binary {ADD, GT}, ternary {IF_GT}, width-2 {X0–X3, ANY}, width-1 {0, 1, 2,
  5}; 72 frozen constructions keeping skeleton, widths, sizes, order, multiplicity), R-size (0150's controls).
  Stage gate admitted all five arms (projection 92 min); 8,640/8,640 rows; scoring 61 min wall. Validity:
  72/72 uniform constructions passed invariants and D625 agreement; 6/6 0524 replays identical. Unsolved jobs
  (8 attempts, capped): R-tree 4, R-unif 3, R-size 3, R-perm 1, R-lib 0.
  **Result.** Mean capped evaluations: R-tree 69,637 · R-lib 26,987 · R-perm 25,421 · R-unif 52,601 · R-size
  57,605. Primary **R-unif ÷ R-perm 2.069 [1.679, 2.608]** (paired build/realization bootstrap): registered
  *worthwhile replacement loss* (lower > 1.10, point ≥ 1.25). R-unif ÷ R-lib 1.949 [1.636, 2.315]; R-unif ÷
  R-tree 0.755 [0.645, 0.884] (cheaper than plain tree GP, but the registered 0.80 "uniform suffices" bound not
  met); guards R-perm ÷ R-tree 0.365 [0.295, 0.441], R-lib ÷ R-tree 0.388 [0.328, 0.456]; solve fraction
  R-unif − R-perm −0.0012 [−0.0046, +0.0017]. R-unif/R-perm above 1 in 23/24 builds and all 12 cells (every
  cell's lower bound > 1), in B 1.89 and C 2.30, in all three realizations (1.70, 2.83, 1.93). Descriptive:
  R-size ÷ R-unif 1.095 [0.864, 1.367] (unresolved; a skeleton effect up to about 30% under uniform labels not
  excluded); R-lib ÷ R-perm 1.062 [0.875, 1.294] (47's retention replicated contemporaneously, point now on
  the other side of 1). First-attempt solves 53% / 77% / 80% / 62% / 61% (tree, lib, perm, unif, size).
  Repayment per acquisition: R-unif 169 [112, 370] searches vs R-perm 65, R-lib 67.
  Content audit (descriptive): uniform relabelling moved binary nodes from 84% to 49% ADD, inputs from 5% to
  20% ANY, flattened constants; distinct-input `ADD(Xi,Xj)` 31 per 24-library set (R-perm 88, intact 107);
  learned-orientation `GT(ADD,ADD)` 0 on every split. Library draws were inserted at the same rate in all donor
  arms, but R-unif material ended up verbatim in solvers at R-size's rate (48% any entry, 2% ≥ 5-node), not
  R-perm's (79%, 10%).
  Explanations: (a) supported in the replacement sense: replacing the learned label law with this uniform law
  keeps only 17 k of R-perm's 44 k evaluations saved per search over R-tree, i.e. loses about 60% of the B/C
  saving (the analysis's "about 85%" does not follow from its own numbers; on the log-ratio scale about 70%); (b) not supported:
  skeletons, widths, sizes and multiplicities with uniform labels perform like random size-matched donors; (c)
  not supported as stated (R-unif resolved worse than R-perm, unresolved against R-size). Not shown: which part
  of the label law matters (ADD share, ANY share, constants and finite-library dependencies all changed at
  once; pair-sum supply is the leading hypothesis, not a result); that a learner needs these exact
  frequencies; transfer (development bank, one cohort, one extractor, one uniform law).

  Decision: close 48 and return to strategy (`next: strategy`) because the primary landed decisively on its
  pre-set loss branch with both guards passing, the question (does the gain need the learned label law, given
  shapes?) is answered for this replacement, root 10's 40-slot allocation is spent, and strategy 0652 reserved
  the next choice (acquisition portability, unfamiliar-content boundary, or a label-preserving learner) for
  its own review.
