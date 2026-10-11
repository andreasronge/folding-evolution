---
outcome: useful_held_out_saving
---
# Analysis — 2026-10-11-1530 frozen R-all order libraries on the 24 protected order cells

Reviewer: independent analysis of the two queue entries at commit `53f0e06`. Raw data:
[prepare](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1530-prepare)
(`bank.json`, `libraries.json`, `method_freeze.json`, `coverage.json`, `seed_audit.json`, `smoke_report.json`,
`preparation.json`) and
[score](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1530-score)
(`score.jsonl`, `report.json`, `dynamics.png`). Every number below was recomputed from `score.jsonl`,
`libraries.json` and `coverage.json` with my own script. The runner's `report.json` agrees to the printed
precision, including the primary bootstrap interval (same seed); a second bootstrap seed gives [0.329, 0.419].
My plot: [analysis_ratios.png](analysis_ratios.png).

Scope, as the proposal fixed it: the 24 saved 1228 R-all libraries, unchanged, scored on the 24 `split.protected`
cells of `x4-order-v1` that no earlier run had searched. Same bank, same twelve helpers, same source corpora as
the development result. This is a held-out-cell replication inside a development bank, not a fresh-bank
transfer test.

## 1. Data completeness

Both entries exit 0, no `failure.json`, queue runner exit 0, `git_dirty = false`, commit matches `execution.md`.
Prepare took 29 s of 1,500 s; score took 1,073 s (17.9 min) of 5,400 s. Both repeats completed, so the
repeat-0 fallback was not needed and `ignored_partial_jobs = 0`.

| Check | Expected | Found |
|---|---|---|
| Bank | hash `2fc0d88c…d74a`, 24 protected cells (4 disjoint-pair, 20 overlapping) | matches; `admitted = true`; no re-screen; `protected_searches = 0` in prepare, 3,456 in score |
| Libraries | 24 saved 1228 R-all libraries, rebuilt from their own corpora | 24 libraries, 25–37 entries (median 28), saved hash `375c7b69…` reproduced; `coverage.present` agrees with the library diagnostics on all 576 build × cell pairs |
| Method | unchanged from `60ab766` | `method_freeze.json` admitted; code review diffed the two files allowed to differ |
| Grid | 24 builds × 24 cells × 2 repeats × 3 arms = 3,456 | 3,456 rows, 3,456 unique keys, 0 duplicates; every cell 144 rows, every build 144 rows, every arm × repeat 576 |
| Cells | only `split.protected` | the 24 scored cells equal the protected list exactly; no development cell appears |
| Seed pairing | three arms share seeds inside a unit, nothing shared across units | 1,152/1,152 units share one 8-seed schedule across the three arms; 9,216 seeds all distinct; audit against 302,283 historical seeds (1129, 1228, 1427 included) found no collision |
| Caps | 8 × 65,536, cap 524,288, pop 256 | identical on all rows; solved costs are multiples of 256 in [768, 495,616] |
| Unsolved jobs (charged 524,288) | — | R-tree 6/1,152, R-all 0/1,152, R-order 0/1,152; every unsolved row has 8 attempts and exactly 524,288 evaluations |

The six R-tree failures fall on four overlapping cells: `lo01+hi03` (2), `lo12+hi13` (2), `lo01+hi13` (1),
`lo12+hi23` (1), in five different builds. No arm-wiring problem is visible in the rows: R-tree rows carry no
library counters, R-order rows draw from a 12-entry pool, R-all rows draw from the unit's own build.

Timing against the proposal's feasibility numbers: R-tree 6.36 worker-s per job (priced 5.31), R-all 2.39
(2.14), R-order 0.33 (0.27), about 9.1 worker-s per unit. Total 10,467 worker-s in a 1,063 s batch, 9.8
effective workers. The run cost about 1.2× the proposal's central estimate and well under the 3× allowance.

The development smoke in prepare (build 0, 6 development cells, 2 repeats, fresh seeds, 36 jobs) solved 36/36
and gave R-all/R-tree = 0.96 on its 12 units. That is one build on new seeds and is a correctness check only;
it is not a replication of 1228 and is not used below.

## 2. Key numbers

### 2.1 Arms on the 24 protected cells (1,152 jobs each, 8 × 65,536 cap, paired seeds)

| Arm | Solved | Capped mean | Median | Geometric mean | Mean attempts | Jobs needing > 1 attempt | Worker-s / job |
|---|---|---|---|---|---|---|---|
| R-tree | 1,146/1,152 | 85.9 k | 69.9 k | 41.2 k | 2.06 | 598 | 6.36 |
| R-all (frozen 1228 library of the unit's build) | 1,152/1,152 | 32.0 k | 4.6 k | 8.8 k | 1.40 | 318 | 2.39 |
| R-order (12 supplied helpers) | 1,152/1,152 | 4.6 k | 1.5 k | 1.8 k | 1.04 | 44 | 0.33 |

For reference, the six development cells in 1228 gave R-tree 73.1 k, R-all 29.3 k, R-order 4.0 k. The
protected roster is somewhat harder for R-tree (85.9 k) and the arms keep their order.

### 2.2 Primary comparison and the other contrasts

Ratio of pooled capped arithmetic means; 95% interval from 8,192 bootstrap draws over the 24 paired whole
builds with all cells fixed, as the plan specified. Equal units per cell holds because the grid is complete.

| Comparison | Point | 95% interval | Units where numerator cheaper (of 1,152) |
|---|---|---|---|
| **R-all / R-tree (primary)** | **0.37** | **[0.33, 0.42]** | 942 (5 ties) |
| R-all / R-tree, worker-seconds | 0.38 | [0.33, 0.42] | — |
| R-all / R-tree, geometric | 0.21 | [0.18, 0.25] | — |
| R-all / R-order | 6.9 | [5.7, 8.6] | — |
| R-order / R-tree | 0.054 | — | 1,152 |

Reliability rule: R-tree has 6 unsolved units, R-all 0, so R-all has 6 *fewer* failures (allowance was 12
more). Solve fractions differ by 0.5 percentage points in R-all's favour.

Per build (48 units each): R-all is cheaper than R-tree in 24/24 builds, below 0.67 in 24/24, range 0.20–0.65.
Per repeat: 0.374 (repeat 0) and 0.371 (repeat 1). Nothing in the per-build or per-repeat split departs from
the pooled figure.

The interval is ×/÷1.13 around the point, better than the ×/÷1.25 the proposal priced. The interval's upper
bound (0.42) sits below the 1228 development point (0.40 [0.32, 0.50]) by a small margin; the two intervals
overlap substantially, so the development and held-out estimates are consistent with one another.

### 2.3 Strata and cells (descriptive, pre-stated)

| Stratum | Cells | Units | R-tree mean | R-all mean | R-order mean | R-all / R-tree [95% over builds] |
|---|---|---|---|---|---|---|
| Disjoint pair (`lo(a,b)+hi(c,d)`, no shared input) | 4 | 192 | 50.5 k | 17.0 k | 1.9 k | 0.34 [0.25, 0.45] |
| Overlapping pair | 20 | 960 | 92.9 k | 35.0 k | 5.2 k | 0.38 [0.33, 0.42] |

Disjoint cells are again the easiest for R-tree (about 51 k in 1228's development set as well), and R-all's
saving on them is at least as large as on overlapping cells. R-tree's six failures are all on overlapping cells.

Per cell (48 units each; full table in the script output, plotted in the left panel of
[analysis_ratios.png](analysis_ratios.png)):

- Point ratios run 0.18 (`lo12+hi13`) to 0.61 (`lo23+hi03`). All 24 are below 0.67; 22 of 24 are below 0.50.
- Per-cell intervals (bootstrap over builds within the cell, 48 units) exclude 1.0 on 23/24 cells. The exception
  is `lo23+hi03`, 0.61 [0.27, 1.17], where two builds carry expensive R-all runs; its R-tree mean (67.7 k) is
  among the lowest on the roster.
- R-tree per-cell cost spans 43.6 k to 120.0 k; the development cells sat at 51–103 k. No protected cell is
  outside the range the method had already been seen on, though three overlapping cells (`lo01+hi13`,
  `lo12+hi13`, `lo01+hi03`) are harder than any development cell.

### 2.4 Needed-helper coverage (descriptive, computed before scoring)

Of the 576 build × cell pairs, the frozen R-all library holds 0, 1 or 2 of the cell's two needed helpers in
84 / 278 / 214 pairs (15% / 48% / 37%). The development roster in 1228 had 18 / 73 / 53 of 144 (13% / 51% /
37%), so the proposal's symmetric-coverage expectation holds.

| Needed helpers in the library | Pairs | Units | R-tree mean | R-all mean | R-all / R-tree [95% over builds] | 1228 development value |
|---|---|---|---|---|---|---|
| 0 | 84 | 168 | 77.3 k | 57.2 k | 0.74 [0.57, 0.93] | 0.77 [0.50, 1.12] |
| 1 | 278 | 556 | 83.3 k | 35.2 k | 0.42 [0.37, 0.48] | 0.45 [0.37, 0.54] |
| 2 | 214 | 428 | 92.5 k | 18.0 k | 0.19 [0.16, 0.24] | 0.23 [0.17, 0.31] |

The monotone coverage gradient from 1228 reproduces almost number for number on cells that were never used to
build or select the libraries. Note that it is a post-hoc stratification: the libraries differ in size and
content across strata as well as in coverage, so this is consistent with the helper account but does not isolate
it (the same caveat 1228 carried).

### 2.5 Solver content (descriptive)

For every solved job I tested whether the final solver tree contains, as a contiguous prefix subsequence, an
entry of the unit's R-all library whose form is the library's representative of a helper the cell needs.

| Arm | Solved | Solver contains a needed-helper library entry | Median solver nodes |
|---|---|---|---|
| R-all | 1,152 | 801 (70%) | 17 |
| R-tree | 1,146 | 273 (24%) | 19 |
| R-order | 1,152 | 444 (39%) | 13 |

The R-tree row is the rate at which unaided search rediscovers the same helper form; R-all's rate is about
three times that. In 1228 the R-all figure was 382/576 (66%). "Contains any library entry" is uninformative here
because the 3-node entries occur in almost every solver of every arm (R-tree 1,095/1,146), so I do not report it
as evidence.

### 2.6 Economics against R-tree (reported, outside the rule)

| Metric | Mean acquisition per build (historical, failures included) | Mean saving per protected search | Break-even searches [95%] | 1228 development value |
|---|---|---|---|---|
| Evaluations | 214 k | 53.9 k | 4.0 [3.4, 4.6] | 4.9 [3.8, 6.5] |
| Worker-s | 13.3 | 3.97 | 3.3 [2.9, 3.9] | 4.2 [3.2, 5.7] |

The break-even is shorter on the protected roster because R-tree is dearer there while R-all's absolute cost
barely moved (29.3 k → 32.0 k). R-all remains 6.9× R-order, so no repayment against R-order is claimed.

## 3. What the data shows

1. **The frozen development saving holds on the held-out cells.** R-all costs 0.37× R-tree [0.33, 0.42] over
   all 24 protected cells, with libraries, method, roster and seeds frozen before any protected job ran and
   nothing refitted. The effect is present in 24/24 builds and all 24 cells by point estimate, and the
   per-cell interval excludes 1.0 on 23/24.
2. **The held-out estimate is not weaker than the development one.** 0.37 [0.33, 0.42] against 0.40
   [0.32, 0.50] on the six development cells. The proposal's named surprise (upper bound ≥ 0.80, a favourable
   development roster) did not happen, and no stratum or cell shows R-all costing more than R-tree by point.
3. **Reliability improved rather than degraded.** R-all solved every unit; R-tree failed 6.
4. **The disjoint and overlapping strata behave alike** (0.34 and 0.38), and the coverage gradient
   (0.74 / 0.42 / 0.19) reproduces the development gradient on unseen cells.
5. **R-all is still far from R-order**: 6.9× its mean cost, about half the log gap (0.49), the same share as in
   1228 (0.47).

## 4. What the data does not show

- **Not transfer to a fresh bank.** Every protected cell is a combination of the same twelve helpers whose
  recurrence the libraries were built from, and the bank is the one the method was developed on. This is the
  strongest within-bank evidence the design can give; a transfer claim still needs a bank frozen together
  with the method before scoring (`research/README.md`, task banks).
- **Not helper causality.** Coverage strata and solver content are post-extraction descriptives. The 0-needed
  stratum is still 0.74× R-tree with an interval below 1, so part of the gain comes from content other than
  the cell's named helpers, or from the donor mix itself. A content-controlled arm was not run here or in
  1228.
- **Not superiority to, or repayment against, supplied helpers.** R-order is 6.9× cheaper than R-all.
- **Not a result about inherited or per-individual acquisition.** The map adapts by external fitting only.
- **Not a per-cell result.** Per-cell intervals are wide (48 units); the one cell whose interval reaches 1.17
  is not evidence of harm, and the per-cell range 0.18–0.61 should not be read as cell-level findings.
- **Not a result about the smoke's 0.96.** One build, 12 units, new seeds; it is a correctness check.

## 5. Shortcut check

Looked for: protected-cell identity reaching the libraries (none: the libraries are byte-identical to the 1228
artifacts, rebuilt from source rows only, and coverage was computed after the libraries were fixed and before
scoring; the code review confirmed workers receive only cell id and labels); any development cell in the scored
grid (none); seeds differing across arms inside a unit or recycled from earlier runs (none of 1,152 units; none
of 9,216 seeds); failures under-charged (none; all six at 524,288 with 8 attempts); a library entry that solves a
protected cell outright (no entry exceeds 9 nodes; the smallest R-all solver tree is well above that, median
17); the repeat-0 fallback or partial rows entering the analysis (both repeats complete, 0 ignored rows).
Library draw counters in R-all rows (9.0 M draws, 4.1 M insertions, 0 empty fallbacks) are consistent with the
half-library donor mix running as frozen.

## Against the predictions

Plan routing, applied in its stated precedence (strict inequalities) to the primary interval [0.33, 0.42] and
the exact failure count:

| Rule (in order) | Threshold | Observed | Fires |
|---|---|---|---|
| 1. End expansion on this family | lower bound > 0.67 | lower 0.329 | no |
| 2. Useful held-out saving; return to strategy | upper bound < 0.80 **and** R-all unsolved − R-tree unsolved ≤ 12 | upper 0.420; R-all has 6 fewer unsolved (0 vs 6) | **yes** |
| 3. Unresolved; price the resolution | otherwise | — | — |

The outcome is **useful held-out saving**. The runner's `report.json` reached the same label by the same rule
(`useful_held_out_saving_return_to_strategy`), and the reliability check passed with margin. The timeout
fallback (repeat 0 only, allowance 6) was not invoked; both repeats are complete.

Against the plan's interpretation: the plan says a useful result "supports frozen externally acquired bias on
held-out combinations of this development bank" and does not establish fresh-bank transfer, helper causality,
inherited acquisition or practical superiority to R-order. The data matches that reading exactly and §4 keeps
each of those exclusions. The plan also fixed that both strata stay in the primary; they do, and separately they
agree (0.34 disjoint, 0.38 overlapping).

Against the proposal's expectations: the steward expected R-all/R-tree of 0.40–0.55 with R-order still 5–8×
cheaper. Observed 0.37 [0.33, 0.42], slightly better than the expected range, and R-order 6.9× cheaper, inside
the expected band. Neither named surprise occurred: the upper bound is 0.42, not ≥ 0.80, so the development
roster was not favourable; and no stratum has R-all costing more than R-tree (the one cell whose interval
reaches above 1 has point 0.61 and is a 48-unit descriptive). The expected precision (×/÷1.25 or better) was
met at ×/÷1.13; the disjoint stratum came in at ×/÷1.35 against the expected ×/÷1.4–1.5.

Against the feasibility anchor: source solves 1,152/1,152 were reused unchanged; protected jobs cost 6.36 /
2.39 / 0.33 worker-s against the anchor's 5.31 / 2.14 / 0.27, so about 1.2× the priced load (10.5 k worker-s
against 8.9 k); the score batch ran 17.7 min against the 15.3 min central estimate and the 90 min allowance.
R-tree solved 1,146/1,152 against the anchor's 574/576 rate (99.5% against 99.7%); R-all and R-order 100% as
anchored.

Against the critique's deferred notes 6–9: none of the historical claims the plan told the researcher not to
reproduce appear in this task's outputs or in this analysis; those corrections remain with the steward.
