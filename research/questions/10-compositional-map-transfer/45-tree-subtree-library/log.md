# Log: 45 tree subtree library

2026-10-11 (steward, run 2026-10-11-0150): opened from strategy 0150. Read-only probe of the 2254
calibration solver trees (56 exact DG solvers on the 8 source/development cells, 25 on the 4 source cells;
feasibility only, not training data). Recurring proper subtrees across cells are almost all 3-node pair sums
`ADD(Xi,Xj)`; literal 7-node predicates `GT(ADD(..),ADD(..))` recur in 2 cells. Rule "3–9 nodes, contains an
input, in ≥ 2 source cells, ADD children sorted for counting, cap 16", 4 solvers per source cell (200
subsamples): library size 3–10 entries (median about 6), ≥ 1 entry larger than 3 nodes in 91% of draws;
literal counting gave larger entries in only 34%. Source predicates cover the pair splits of 5 of the 8 target
cells; the 3 cells using X1+X3 / X0+X2 are uncovered. From 0024's R-tree rows: per-job CV 1.15, relative SE of
the arm mean 4.3% at 768 jobs, pairing correlation with shared seeds 0.05 (pairing buys little).

Decision: propose R-lib versus R-tree and size-matched R-size, 1,536 jobs per arm, because that size resolves
a 20% saving and excludes a gain above about 15% if there is none.

2026-10-11 (steward, run 2026-10-11-0150): ran at commit `d7ec100` (code review pass; prepare 848 s, scoring
3,137 s of 195 min allocated; off-path replay of 8 saved 0024 jobs matched; seeds paired across arms and
disjoint from history; 4,608/4,608 rows). Acquisition: 764/768 source jobs solved, 24 libraries of 3–12 entries
(181 in total, none empty), 2.88 M evaluations and 286 worker-s per library. Contents: 56 pair sums
`ADD(Xi,Xj)`, 20 full predicates (all the X0+X1 vs X2+X3 split, in 20/24 libraries, because 3 of the 4 source
cells share it), about 60 input-plus-constant sums. 55.5% of library draws were oversize-rejected, so a library
subtree entered about 11% of children, not the planned 25%. Size controls matched node count and compiled length
but about a third contained no input.
Primary (8 DG target cells, equal weight, failures at 524,288, 24-acquisition block bootstrap, 1,536 jobs per
arm): mean evaluations R-lib ÷ R-tree **0.390 [0.332, 0.463]** (87,352 → 34,109); R-lib ÷ R-size **0.414
[0.332, 0.533]**; solve difference R-lib − R-tree +0.008 [+0.004, +0.012] (1,536/1,536 vs 1,524/1,536).
R-size ÷ R-tree 0.944 [0.790, 1.120] (unresolved). Worker seconds 0.373 [0.315, 0.443]. Plan precedence row 2:
useful search-content increment. Descriptive: R-lib below R-tree in 24/24 builds (leave-one-out 0.36–0.40); all
8 cells gain (0.12 on the one cell sharing the learned predicate, 0.35–0.53 elsewhere; 0.427 [0.361, 0.504]
without that cell); first-attempt solves 1,121 vs 715 of 1,536; exact solvers rarely contain library entries
verbatim (10/1,536 contain the predicate) and are the same size (≈ 17 nodes); training-perfect-not-exact share
unchanged (10.0% / 10.6%). The 4 builds without a 7-node predicate gave 0.98, 0.66, 0.26 (has a 9-node
near-predicate), 0.50; the 20 with it 0.16–0.51 — suggests the comparison skeleton matters, n = 4, observation
only. Repayment against R-tree after 54 [45, 65] target searches per library; below that a net loss
([analysis](../../../runs/2026-10-11-0150/analysis.md)).

Explanations: (a) supported in the tested sense — beyond size- and length-matched random donors; what "content"
is (comparison skeleton, pair sums, or an input/`ADD` token-frequency shift, since controls need not contain an
input) is not separated; (b) not supported (R-lib/R-size resolved below 1); (c) not supported at this scope.

Decision: close 45 and return to strategy (`next: strategy`) because the primary landed on the pre-set "useful"
row with wide margin, root 10's 37-slot budget is spent, and both successors (a fresh-bank stage, or a cheap
ingredient test with hand-set {pair sums} / {skeleton} / input-only donors) are allocation choices the strategy
reserved for itself.

2026-10-11 (steward, run 2026-10-11-0348): wording correction (critique 0348, note 8). The summary said the gain
showed "not as copied entries in final solvers"; the literal contiguous matcher undercounts orientation variants
and interleaved reuse, so it now reads that few final solvers contain larger entries verbatim and that
transformed reuse and causal pathways are unmeasured. On fresh `x4-gate-sum-v1` the same matcher found the
library predicate verbatim in 309/576 R-lib solvers on the predicate-matched split
([46](../46-tree-library-fresh-composition/log.md)). No change to the decision.
