# Log: 46 tree library on a fresh composition

2026-10-11 (steward, run 2026-10-11-0348): opened from strategy 0348. Feasibility probe, before any bank or
method freeze ([probe/](../../../runs/2026-10-11-0348/probe/): script and rows). Code `d7ec100`
(git archive in /tmp with its own venv and release Rust build; the main checkout's Rust module lacks
`v2_x4`, so two earlier probe runs scored canonical programs at 20% and were discarded; their seeds,
934,8xx,xxx and 934,9xx,xxx, are spent and must enter the seed audit). Cells: the first two of the
planning audit's 144 candidates in ascending label-hash order, `(X1+X3)>(X0+X2)?X0+X1:X3` (pair split
absent from every learned predicate) and `(X0+X1)>(X2+X3)?X0+X3:X0` (the learned predicate's split);
canonical compiled length 19, interpreter and VM both match labels. These two become development cells
and can never be protected. One unrestarted attempt per job up to 524,288 evaluations, pop 256, mix 0.5,
one job per 0150 library per cell per arm (24), 10 processes.

| cell (split) | arm | solved ≤ 65,536 | solved ≤ 524,288 | median solve (evals) |
|---|---|---|---|---|
| X1+X3 / X0+X2 | R-tree | 16/24 | 19/24 | 18,944 |
| X1+X3 / X0+X2 | R-lib | 22/24 | 22/24 | 3,712 |
| X0+X1 / X2+X3 | R-tree | 14/24 | 17/24 | 11,264 |
| X0+X1 / X2+X3 | R-lib | 24/24 | 24/24 | 3,328 |

Per-attempt success at the 65,536 cutoff: R-tree 30/48 (DG first attempt in 0150: 715/1,536 = 0.47),
R-lib 46/48 (DG 0.73). Library subtrees entered 9–15% of children (DG 11%). Throughput 72–87 µs per
evaluation. Rough expected restarted cost: R-tree ≈ 54k, R-lib ≈ 9k evaluations per job (ratio ≈ 0.16;
two cells, not a result). Observation only.

Decision: propose the frozen 0150 method on protected cells of a performance-blind fresh bank (R-lib,
R-tree, R-size), because the probe shows the comparison is feasible and cheap (≈ 30 min of scoring) and
only a protected roster across all three pair splits can support a transfer claim.

2026-10-11 (steward, run 2026-10-11-0348): ran at commit `1f02bb7` (code review pass; prepare 275 s of
2,400 s, scoring 2,317 s of 5,400 s; [analysis](../../../runs/2026-10-11-0348/analysis.md)). Bank
`x4-gate-sum-v1`: all 144 candidates passed the exact ≤ 9-token D625 screen (0 exclusions); canonicals
agree in interpreter, Python and Rust; 4 development cells (both probe cells among them) and 18 protected
cells, 6 per pair split, frozen with the method before any protected search. All 24 0150 libraries and
size controls re-derived from the saved acquisition rows, hash-equal to 0150's `libraries.json`; 8 saved
0024 jobs replayed exactly; seed audit clean. Stage 0 (development cells, descriptive): R-lib/R-tree 0.20.
Scoring: 5,184/5,184 rows, arms share each job's 8 attempt seeds; every one of 5,175 solvers re-verified
exact on D625 by the reviewer.
Primary (18 protected cells, equal weight, failures at 524,288, 24-acquisition paired block bootstrap,
1,728 jobs per arm): mean evaluations R-lib ÷ R-tree **0.250 [0.217, 0.289]** (69,442 → 17,346); guard
solve difference +0.0012 [0.000, +0.0029] (1,728/1,728 vs 1,726/1,728). Plan precedence: **transfers**
(upper < 0.90, guard passes). Secondary: R-lib ÷ R-size **0.291 [0.231, 0.372]**; R-size ÷ R-tree 0.860
[0.716, 1.011] (unresolved; R-size had the most failures, 7); worker seconds R-lib ÷ R-tree 0.234 [0.201,
0.273]. By pair split: A {X0+X1 | X2+X3}, the learned predicate's split, **0.055 [0.042, 0.071]**; B
{X0+X2 | X1+X3} **0.363 [0.299, 0.434]**; C {X0+X3 | X1+X2} **0.338 [0.287, 0.400]**; R-lib below R-tree
in 18/18 cells (A 0.038–0.086, B/C 0.27–0.46) and 24/24 builds (0.14–0.54). Verbatim reuse (literal
matcher, solved jobs): the library's own `GT(ADD,ADD)` in 309/576 R-lib solvers on A, 29 and 36 on B and C;
any ≥ 5-node entry 351 / 13 / 7; the share of solvers holding some `GT(ADD,ADD)` on B/C (167, 173) equals
R-tree's (166, 169). The three builds without a 7-node predicate by this matcher (0, 7, 17; 0150 counted
four, one with a 9-node near-predicate) gave pooled 0.54 / 0.45 / 0.32 vs a mean 0.23 for the other 21
(observation). Economics: acquisition 2.877 M [2.600, 3.163] evaluations per library, saving 52,096
[47,102, 56,933] per search, break-even **55.2 [49.4, 61.9]** searches (worker seconds 58.0 [51.8, 65.3]);
R-size vs R-tree break-even 295 [149, unbounded]. By 16,384 evaluations R-lib had solved about 0.79 of
jobs, R-size 0.49, R-tree 0.39. 99.97% of training-perfect individuals were not D625-exact; the exact
check matters. DG's 0.390 (0150) is a different bank: comparison descriptive.

Explanations: (a) supported at this scope: the libraries' parts help a new composition in every pair
split, beyond the size control; (b) not supported (the DG gain was not specific to DG's composition);
(c) not supported (R-lib/R-size resolved below 1; size control's own effect unresolved). Most of the pooled
gain is predicate-matched (split A ≈ 18×); the unlearned splits keep a ≈ 3× floor whose carrier (pair
sums, small entries, input/`ADD` frequency) is unidentified, and large entries rarely survive verbatim
there. Shape assembled from the libraries' own parts, two development cells probed before freeze: reuse
across composition of familiar parts, not unfamiliar content or modularity. The gate-sum protected cells
are now spent: `x4-gate-sum-v1` is a development bank from here on.

Decision: close 46 and return to strategy (`next: strategy`) because the primary landed on the pre-set
"transfers" branch with a wide margin and passed the guard, root 10's 38-slot budget is spent, and
strategy 0348 reserved the next choice (mechanism, acquisition on different sources, broader tasks) for
its own review.

2026-10-11 (steward, run 0524): wording corrections from critique 0524's digest check (notes 6–8). (i) "Most of
the pooled gain is predicate-matched" above overstates attribution: split A contributes about 43% of the
arithmetic evaluation savings (pooled 52,096 per job; B/C about 44,577); read instead "the relative gain is much
larger on the predicate-matched split (0.055× vs 0.34–0.36×)". Its causal carrier was unidentified at 0348; 47
has since shown, by intervention, that A's extra gain needs the learned arrangement. (ii) "the share of solvers
holding some `GT(ADD,ADD)` on B/C … equals R-tree's" should read: observed shares were similar (167/576 and
173/576 vs 166/575 and 169/575); differences were not assessed. (iii) "no reliability loss" in the summary now
reads "no loss observed; the registered 3-point noninferiority guard passed". The summary has been corrected;
these entries above stay as written.
