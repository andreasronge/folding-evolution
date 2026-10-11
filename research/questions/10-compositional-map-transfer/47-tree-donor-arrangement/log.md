# Log: 47 tree-donor arrangement

- 2026-10-11 (steward, 0524): opened. Read-only probe on 0150 `libraries.json` (approximate audit construction,
  20 realizations per build): distinct-input `ADD` pair sums by split, intact A 48 / B 1 / C 6; permuted mean
  A 17.1 / B 16.9 / C 15.1. 0348 B/C means (1,152 jobs/arm): R-tree 68,647, R-lib 24,070, R-size 57,282
  evaluations; worker s/job 6.41 / 2.12 / 5.22; R-lib half-vs-half ratio [0.83, 1.26] at 576 jobs each.

- 2026-10-11 (steward, run 0524): ran at commit `7c0e5df` (code review pass; prepare 67 s, scoring 2,737 s of
  7,200 s; [analysis](../../../runs/2026-10-11-0524/analysis.md)). Stage gate admitted 6 repeats × 3 realizations
  (projection 3,796 s < 6,000 s); 72/72 constructions passed invariants and Rust/interpreter/Python agreement;
  0348 R-lib replay identical. 7,776/7,776 rows, the three arms share each job's 8 seeds, seeds disjoint from
  history. Unsolved: 10 R-tree jobs, 0 R-lib, 0 R-perm.
  Primary (B/C, 12 cells, 1,728 jobs/arm, nested build/construction bootstrap): mean evaluations
  **R-perm ÷ R-lib 1.031 [0.854, 1.225]** (upper below the 1.25 margin by 0.025; build-only bootstrap
  [0.897, 1.187]; R-perm below R-lib in 11/24 builds). R-perm ÷ R-tree 0.360 [0.299, 0.429]; replication
  R-lib ÷ R-tree 0.349 [0.301, 0.410] (0348: 0.363 / 0.338); solves 1,728/1,728 in both donor arms (difference
  0.000 [0.000, 0.000]). Positive control A: **R-perm ÷ R-lib 5.14 [3.68, 7.14]**, every A cell 3.5–7.2; after
  rearrangement A behaves like B/C (R-perm ÷ R-tree 0.325 vs 0.360). Registered label: *arrangement unnecessary
  at this resolution*, under the plan's restricted reading.
  Descriptive: B 1.02 [0.78, 1.30], C 1.05 [0.82, 1.31]; the 4 B/C cells whose then-pair is a learned pair 0.87
  [0.63, 1.17] vs the other 8 1.13 [0.93, 1.36] (unresolved); per realization 1.08, 1.01, 1.01. R-perm's median
  (4,864 vs 5,632) and first-attempt solves (80% vs 79%) were slightly better, its mean slightly worse through the
  upper tail. Worker s/job 2.34 vs 2.25. Construction content: the learned predicate `GT(ADD(X2,X3),ADD(X0,X1))`
  survived 0/1/0 times in the three realizations (intact 63), so A lost almost all of it (not "about 1/3 kept", as
  proposed); distinct-input `ADD` occurrences on B/C rose from 21 to 57–62; 3–6 accidental B/C predicates per
  realization; 78% of entries changed behaviour on D625. R-perm solvers on B/C held a ≥ 5-node donor entry
  verbatim in 10% (R-lib 2%) and the cell's correct `GT(ADD,ADD)` in 35% (R-lib 25%, R-tree 28%), with no
  matching change in mean cost. Acquisition-inclusive repayment on B/C about 61 (R-lib) and 62 (R-perm) searches.
  Explanations: (b) consistent: this shape/size/arity/width-conditioned rearrangement keeps the B/C gain at the
  registered resolution, though an intact advantage up to about 20% is not excluded; (a) not supported on B/C
  (lower 0.85 < 1.10), but supported on A, where the extra gain needs the learned arrangement; (c) not supported
  (R-perm not resolved cheaper despite more B/C pairs). Retention could also be a cancellation (lost arrangement
  vs gained B/C pairs); the carrier is not identified, and token-only sufficiency or cheaper acquisition is not
  shown. Development bank, one acquisition cohort, one construction.

  Decision: close 47 and return to strategy (`next: strategy`) because the primary landed on its pre-set
  retention branch with both guards and the positive control passing, root 10's 39-slot budget is spent, and
  strategy 0524 reserved the follow-up (price a statistical acquisition, or carry intact expressions) for its
  own review.

- 2026-10-11 (steward, 0652): wording correction (critic digest check, run 0652). The 0524 entry's "with no
  matching change in mean cost" should read "without a resolved mean-cost difference (1.031 [0.854, 1.225]);
  the registered 1.25 retention margin passed": an unresolved ratio is not equality. Run 0652 re-ran R-lib and
  R-perm contemporaneously: R-lib ÷ R-perm 1.062 [0.875, 1.294], again unresolved; no decision changes.
