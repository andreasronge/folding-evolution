---
outcome: useful_acquisition
---
# Analysis — 2026-10-11-1228 uncapped semantic library (R-all) on order development cells

Reviewer: independent analysis of the two queue entries at commit `60ab766`. Raw data:
[prepare](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1228-prepare)
(`bank.json`, `acquisition.jsonl`, `libraries.json`, `preparation.json`) and
[score](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1228-score)
(`score.jsonl`, `report.json`, `dynamics.png`). Every number below was recomputed from `score.jsonl` and
`libraries.json` with my own script; the runner's `report.json` agrees to the printed precision, including the
bootstrap interval (same seed) and a second bootstrap seed ([0.314, 0.501]). My plot:
[analysis_ratios.png](analysis_ratios.png).

Scope, as the proposal fixed it: external fitting, frozen 1129 recurrence recipe with the cap removed, six
development cells of `x4-order-v1`. Nothing here is protected-cell or fresh-bank evidence.

## 1. Data completeness

Both entries finished with exit 0, no `failure.json`, queue runner exit 0. `git_dirty = false` in both
`metadata.json`; commit matches `execution.md`.

| Phase | Expected | Found | Notes |
|---|---|---|---|
| Bank | frozen 1129 bank, 24 source / 6 development / 24 protected | hash `2fc0d88c…` matches the constant in the driver; `admitted = true`; no re-screen | `protected_searches = 0` in both phases |
| Acquisition | 24 builds × 24 source cells × 2 R-tree jobs = 1,152 | 1,152 rows, 1,152/1,152 solved | mean 214 k evaluations and 13.3 worker-s per build (1129: 202 k, 11.4) |
| Libraries | 24 × (R-S capped 16, R-all uncapped) | 24 × 16 and 24 × 25–37 (median 28) | prefix identity, all-eligible count and own-corpus provenance asserted in `libraries_from`; score phase rebuilt them from the saved rows and matched |
| Scoring | 6 cells × 24 builds × 4 repeats × 4 arms = 2,304 | 2,304 rows, 2,304 unique keys, 0 duplicates, grid exactly matches the schedule | all 576 (build, cell, repeat) units carry identical 8-seed schedules across the 4 arms |
| Unsolved jobs (charged 524,288) | — | R-tree 2, R-order 0, R-S 4, R-all 0 (each of 576) | every unsolved row has exactly 8 attempts and exactly 524,288 evaluations |

Seed audit: 283,130 historical seeds, no collision with the new source/score/smoke namespaces (checked by the
driver and recorded in `seed_audit.json`). Timing: prepare 40 s wall of 1,200 s; score 836 s wall (14 min) of
5,400 s. Total queue 14.6 min against the 110 min approved; the scoring estimate of 25–51 min was conservative
because R-all jobs are cheap (2.1 worker-s mean against R-S 6.4).

Arm wiring (checked in `order_cap_run.envelopes` and `order_run.envelopes`): R-all is dispatched as an R-S
job with `semantic_all` substituted per build; donors are a flat prefix list drawn uniformly by the unchanged
engine; workers receive only cell id and labels. The helper census is used only after extraction for the
descriptive coverage split. I found nothing that leaks destination identity or helper labels into the library.

## 2. Key numbers

### 2.1 Arms on the six development cells (576 jobs each, 8 × 65,536 cap, paired seeds)

| Arm | Solved | Capped mean | Median | Geometric mean | Mean attempts | Worker-s / job |
|---|---|---|---|---|---|---|
| R-tree | 574/576 | 73.1 k | 34.8 k | 33.7 k | 1.87 | 5.31 |
| R-order (12 supplied helpers) | 576/576 | 4.0 k | 1.5 k | 1.7 k | 1.03 | 0.27 |
| R-S (capped 16) | 572/576 | 89.9 k | 69.1 k | 35.3 k | 2.20 | 6.39 |
| R-all (uncapped) | 576/576 | 29.3 k | 4.6 k | 8.2 k | 1.35 | 2.14 |

### 2.2 Primary comparison and the other contrasts

Ratio of pooled capped arithmetic means; 95% interval from 8,192 bootstrap draws over the 24 paired whole
builds (equal cell/repeat weights), as the plan specified.

| Comparison | Point | 95% interval | Units where numerator cheaper (of 576) |
|---|---|---|---|
| **R-all / R-tree (primary)** | **0.40** | **[0.32, 0.50]** | 468 (1 tie) |
| R-all / R-S | 0.33 | [0.27, 0.39] | 442 |
| R-S / R-tree | 1.23 | [1.07, 1.41] | 306 |
| R-all / R-order | 7.27 | [5.49, 9.81] | — |
| R-order / R-tree | 0.055 | [0.043, 0.067] | 576 |

Worker-seconds give the same picture: R-all / R-tree 0.40 [0.31, 0.50], R-all / R-S 0.33 [0.28, 0.40].
Geometric R-all / R-tree is 0.24 [0.20, 0.29]. Solve fractions differ by at most 0.7 percentage points.

The upper bound of the primary interval (0.50) is below the 0.80 threshold, and the lower bound (0.32) is below
0.67, so the plan's precedence rule lands on **useful acquisition**. The point estimate also sits at the
proposal's stated surprise line (R-all ≤ 0.5×).

Per build (each pooled over 24 units): R-all is cheaper than R-tree in 24/24 builds, below 0.67 in 20/24, range
0.06–0.99. R-S is cheaper than R-tree in 7/24 builds. Per cell (96 jobs per arm): R-all / R-tree runs 0.35–0.47
on all six cells, with no cell carrying the result. The 1129 probe's R-S / R-tree was 1.00 [0.68, 1.46] on
8 builds; at 24 builds it is 1.23 [1.07, 1.41], so the capped library is now a measurable cost, not a wash.

### 2.3 Share of the R-tree → R-order gap recovered (reported, outside the rule)

Log gap R-tree → R-order is 2.97 nats (18× geometric). R-all recovers 0.47 of it (geometric definition);
R-S recovers −0.02. R-all is still 7.3× R-order on the arithmetic mean, so no repayment against R-order is
claimed, as the proposal said.

### 2.4 Economics against R-tree (reported, outside the rule)

| Metric | Mean acquisition per build | Mean saving per search | Break-even searches [95%] |
|---|---|---|---|
| Evaluations | 214 k (1,152/1,152 source solves, nothing to charge) | 43.8 k | 4.9 [3.8, 6.5] |
| Worker-s | 13.3 (both extractions, census and validation included) | 3.18 | 4.2 [3.2, 5.7] |

The proposal priced "worthwhile" at about 8 searches at 0.67×; the observed break-even is about 5.

### 2.5 What the cap had been removing

Across the 24 builds the uncapped pool admits 177 helper classes (of 12 × 24 = 288 helper × build cases); the
capped prefix admits 18. The included helpers' uncapped ranks run 14–37 (median 21), so almost all sit past
position 16. The reason is visible in the ranking key: the first 16 entries are almost all 3-node forms
(363/384) recurring in 3–10 source cells, while the 305 extra entries all recur in exactly 2–3 cells and are
split between 3-node forms (115) and 6–9-node forms (165), where the min/max helpers live.

Coverage of the needed helpers for a development cell, per cell × build pair (144 pairs):

| Pool | ≥ 1 needed helper present | both present |
|---|---|---|
| R-S (capped) | 14/144 | 0/144 |
| R-all | 126/144 | 53/144 |

The proposal's read-only prediction from the 1129 libraries was 31/48 and 10/48; the fresh builds give a
higher rate (0.88 vs 0.65 for ≥ 1). Not a tested claim, just noted.

### 2.6 Cost by needed-helper coverage (descriptive, as pre-stated)

Strata are defined by how many of the cell's two needed helpers are in the R-all pool. Intervals here are a
bootstrap over cell × build pairs within the stratum, descriptive only.

| Needed helpers in pool | Pairs | R-tree mean | R-S mean | R-all mean | R-all / R-tree | R-all / R-S |
|---|---|---|---|---|---|---|
| 0 | 18 | 65.3 k | 87.6 k | 50.4 k | 0.77 [0.50, 1.12] | 0.58 [0.41, 0.76] |
| 1 | 73 | 72.6 k | 91.0 k | 32.5 k | 0.45 [0.37, 0.54] | 0.36 [0.28, 0.46] |
| 2 | 53 | 76.4 k | 89.1 k | 17.6 k | 0.23 [0.17, 0.31] | 0.20 [0.15, 0.25] |

### 2.7 Mechanism check on the solvers (descriptive)

For every solved job I tested whether the final solver tree contains, as a contiguous subtree, a library entry
whose semantics equal a helper the cell needs.

| Arm | Solved | Solver contains a needed-helper library entry | Solver contains any library entry | Median solver nodes |
|---|---|---|---|---|
| R-S | 572 | 43 | 530 | 20 |
| R-all | 576 | 382 | 572 | 18 |

R-tree solvers have a median of 19 nodes, R-order 13. Library insertion rates per draw are similar in R-S
(0.50) and R-all (0.45), so R-all is not inserting more often; it is inserting different content.

## 3. What the data shows

1. **Removing the cap turns the same corpus from a cost into a saving.** On these six cells R-all costs 0.40×
   R-tree [0.32, 0.50] and 0.33× the capped R-S [0.27, 0.39], with the pre-registered bootstrap on 24
   independent acquisitions. The effect is present in all 24 builds and all six cells; no outlier drives it.
2. **The saving is paid back quickly.** About 5 searches of 214 k acquisition evaluations, interval 3.8–6.5.
3. **The content that matters is the 2-cell-recurrent 6–9-node tail of the ranking.** The capped prefix held a
   needed helper in 14/144 cell × build pairs; the uncapped pool in 126/144. Cost falls monotonically with
   coverage (0.77 → 0.45 → 0.23 of R-tree), and 382/576 R-all solvers contain a needed-helper entry against
   43/572 for R-S.
4. **Dilution did not cancel the gain.** The pool roughly doubled (16 → 25–37), yet every stratum, including the
   18 pairs with no needed helper (0.58× R-S, interval excludes 1), is cheaper than capped R-S. The proposal's
   expectation of "trivia dilution cancels much of the coverage gain" is not what happened.
5. **R-all is still far from R-order**: 7.3× its mean cost, about half the log gap.

## 4. What the data does not show

- **Not helper causality.** R-all / R-S changes entry count, entry sizes and sampling probability together
  (critique note 4). The coverage strata and solver check are consistent with the helper account but are
  post-extraction descriptives, and the 0-needed stratum is also cheaper than R-S, so some of the gain comes
  from other 2-cell content or from the diluted share of 3-node trivia. Isolating that needs a content-controlled
  arm, which was not run.
- **Not transfer.** Six development cells, same bank as 1129, same split. The 24 protected cells remain
  unsearched. A transfer claim needs the frozen method and the protected roster scored under the separately
  priced stage the plan mentions, and the bank rule in `research/README.md` applies.
- **Not superiority to R-order.** Supplied helpers remain 7× cheaper; the recipe recovers about half the gap.
- **Not a general cap result.** Only cap = 16 and cap = none were compared; whether a cap of 24 or a different
  ranking key would do as well is untested.
- **Not a measurement of the 1129 R-S/R-tree discrepancy.** 1129 found 1.00 [0.68, 1.46]; here 1.23 [1.07, 1.41].
  The intervals overlap; the builds are different draws.

## 5. Shortcut check

Looked for: destination identity reaching the library (none; workers get id and labels only, extraction uses
source rows only, and the score phase rebuilt the libraries from the saved source rows and matched hashes);
seeds differing across arms (none of 576 units); failures under-charged (none; all at 524,288); near-alias
helper entries that solve a destination outright (no library entry exceeds 9 nodes and the smallest R-all solver
is well above that; median 18 nodes). The `shortcuts` counter in the rows is the engine's duplicate-evaluation
skip, not a solution shortcut, and it is of the same order in all arms.

## Against the predictions

Plan routing, applied in its stated precedence to the primary interval [0.32, 0.50]:

| Rule (in order) | Threshold | Observed | Fires |
|---|---|---|---|
| 1. End the recipe | lower bound > 0.67 | lower 0.32 | no |
| 2. Useful acquisition; return to strategy with a separately priced protected-stage case | upper bound < 0.80 | upper 0.50 | **yes** |
| 3. Unresolved | otherwise | — | — |

The outcome is **useful acquisition**. The runner's `report.json` reached the same label by the same rule.

Against the plan's explanations: the plan said a large gain "supports the explanation that cap crowding
obstructed useful acquisition and that the expanded repertoire pays for dilution under this procedure". That is
the case the data matches. The alternative, insufficient useful bias after dilution and acceptance costs, would
have shown as harm or an excluded one-third saving; neither occurred. The plan also pre-stated that R-all / R-S
isolates cap removal, not helper causality, and that coverage strata do not resolve that confounding. The
strata in §2.6 and the solver check in §2.7 are reported as descriptives under that restriction.

Against the proposal's expectations: the steward guessed R-all / R-tree at 0.8–1.0× and named R-all ≤ 0.5× as
a surprise. The point estimate is 0.40 and the whole interval sits under 0.5, so this is the surprising case.
The second named surprise, R-all clearly costlier than R-S, did not occur; R-all is 0.33× R-S. The proposal's
"some gain" prior from the 1129 helper-holding builds (0.67× geometric, post hoc) was conservative: the
geometric ratio here is 0.24.

Against the feasibility assumptions: source solves 1,152/1,152 (plan baseline 384/384); acquisition 214 k
evaluations and 13.3 worker-s per build (baseline 202 k, 11.4); R-all jobs averaged 2.1 worker-s, far under
the 10.6 s provisional price, so scoring took 14 min instead of the expected 25–51.

Scope stays where the plan put it: externally fitted subtree reuse on these six development cells of
`x4-order-v1`, no transfer, no protected evidence, no claim against R-order. The next action the plan names
for this outcome is a return to strategy with a separately priced protected-stage case.
