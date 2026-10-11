---
outcome: observations
---
# Analysis — rectified-sum probe (2026-10-11-1315)

Reviewer analysis of the two queue entries at commit `4a60cc7` (both `done`, exit 0).
Raw data: [prepare](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1315-prepare)
and [score](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-11/2026-10-11-1315-score).
Numbers below were recomputed from `score.jsonl`, `acquisition.jsonl` and `libraries.json`; they match `report.json`.
Summary figure: [analysis.png](analysis.png). Engine figure: `dynamics.png` in the score folder.

## 1. Data completeness

| Check | Result |
|---|---|
| Bank | `x4-rectified-sum-v1`, hash matches `BANK_HASH`; 24 sources, 6 development cells (4 stage-0 seen + 2 overlapping), 24 protected cells; `protected_searches: 0` in both phases |
| Prepare | 384/384 source jobs present (8 builds × 24 cells × 2 repeats), 384/384 solved, 11.3 s wall; eight libraries written; preparation hash recorded |
| Score | 384/384 rows, 384 distinct (build, cell, repeat, arm) keys, 0 duplicates, 0 missing; 96 per arm |
| Seeds | all 96 units share the same eight attempt seeds across the four arms; 768 distinct seeds across the 96 units; audit against historical seeds passed in prepare |
| Failure charging | 0 unsolved rows with evaluations ≠ 524,288; 0 solved rows at the cap; 275/384 rows used all 8 attempts |
| Replay | score phase rebuilt all eight libraries from the acquisition rows and matched (1.0 s) |
| Method freeze | all 1228 method hashes except the extension (pinned by path and SHA-256 in the worktree venv) verified |
| Runtime | score 1151 s wall of a 2370 s internal deadline; effective concurrency 10.8 on 11 workers; max job 45.6 worker-s |

Nothing is missing, duplicated or truncated. The grid is complete and the analysis below uses all of it.

## 2. Source acquisition (prepare phase)

Denominator: 384 source jobs (8 builds × 24 source cells × 2 repeats), all solved.

| Quantity | Value |
|---|---|
| Solved / first-attempt solved | 384/384 / 381/384 |
| Capped mean / median evaluations per source job | 3,469 / 2,304 |
| Acquisition cost per build (48 jobs) | 126k–204k evaluations, mean 166k; 9.1 worker-s |
| Root operator of solver | IF_GT 335/384, ADD 49/384 |
| Solver contains the exact three-input sum `a+b+c` (any size) | 326/384 |
| Solver contains its own helper's output vector (any size) | **34/384 (8.9%)** |
| … at an emittable size (3–9 nodes) | 9/384 (all 8 nodes) |
| Any helper vector other than its own | 0/384 |

Per helper over the eight builds (12 helpers × 8 builds = 96 helper-build pairs): the helper vector appeared in at
least one solver in 32/96 pairs, at an emittable size in 8/96, in ≥ 2 source cells (the recurrence rule) in 1/96
(pos13, build 1, smallest form 19 nodes) and at both emittable size and recurrence in **0/96**. So no rectifier
entered any R-all library, and the one recurrence that did happen was filtered by size.

**What the R-all libraries contain.** 13–18 semantic classes per build (`eligible_semantic_classes` equals the entry
count, so nothing eligible was dropped). Each build holds the same core: all 6 pairwise input sums, all 4 three-input
sums, plus 3–8 other classes (comparisons such as `GT X1 2`, sums with `ANY`, and one 7–9-node mixed form in five
builds). None is a rectifier.

## 3. Destination scoring (96 jobs per arm; 8 builds × 6 cells × 2 repeats; cap 8 × 65,536 = 524,288)

| Arm | Solved | First attempt | Capped mean (k) | Median (k) | Geometric mean (k) | Worker-s total |
|---|---|---|---|---|---|---|
| R-tree | 20/96 | 0/96 | 468.9 | 524.3 | 436.5 | 3,452 |
| R-rect (12 supplied helpers) | **73/96** | 11/96 | **268.9** | 263.9 | 143.1 | 2,024 |
| R-all (8 new builds) | 14/96 | 1/96 | 481.6 | 524.3 | 440.0 | 3,447 |
| R-order-all (1228 builds 0–7) | 15/96 | 2/96 | 488.2 | 524.3 | 448.4 | 3,546 |

Ratios of pooled capped arithmetic means, paired whole-build bootstrap (8 builds, 8,192 draws), descriptive:

| Contrast | Point | 95% interval |
|---|---|---|
| R-rect / R-tree | 0.573 | 0.502–0.638 |
| R-all / R-tree | 1.027 | 0.958–1.099 |
| R-order-all / R-tree | 1.041 | 1.003–1.085 |
| R-all / R-order-all | 0.986 | 0.913–1.070 |

Unit-level pairing (same seeds, 96 units): R-rect used fewer evaluations than R-tree in 67 units, more in 9, tie in 20
(ties are double caps). R-all vs R-tree: fewer in 14, more in 16, tie in 66. R-order-all vs R-tree: 10 / 19 / 67.

Per cell (16 jobs per arm per cell):

| Cell | Disjoint | R-tree | R-rect | R-all | R-order-all |
|---|---|---|---|---|---|
| pos01+neg02 | no | 4 | 14 | 1 | 1 |
| pos13+neg23 | no | 2 | 12 | 1 | 2 |
| pos01+neg23 | yes | 4 | 16 | 3 | 6 |
| pos12+neg03 | yes | 8 | 12 | 4 | 4 |
| pos12+neg13 | no | 1 | 10 | 3 | 1 |
| pos03+neg13 | no | 1 | 9 | 2 | 1 |

Per build, R-rect was the best arm in all 8 builds (8–12 solves of 12 vs 1–4 for R-tree); R-all beat R-tree on capped
mean in 3/8 builds and R-order-all in 3/8.

**Coverage.** Needed helper present in the R-all pool: **0/48** cell × build pairs (0/96 needed-helper slots).

**Solver content (shortcut check).** Every solved destination solver in every arm contains the output vectors of both
needed helpers as subtrees (R-tree 20/20, R-rect 72/73 both plus 1 with one, R-all 14/14, R-order-all 15/15). In
R-rect, 126 of 153 helper-matching subtrees are the 8-node supplied form; in the other arms the smallest forms are
8–15 nodes and mostly 10. R-rect solvers are the canonical 25-token length (median 25) while the other arms' solvers
are median 30.5–31 tokens against a 32-token cap. So destinations do factor through the helpers, the supplied helpers
are being used, and no helper-free shortcut was found for destinations.

**Economics (per report).** Mean acquisition 166k evaluations per build; mean saving of R-all over R-tree is negative
(−12.7k per destination job), so no repayment. Transported 1228 libraries cost 173k–277k evaluations per build and
likewise save nothing here.

## 4. Pre-stated recommendation rule

| Condition | Threshold | Observed | Holds |
|---|---|---|---|
| (1) coverage | ≥ 24/48 pairs | 0/48 | no |
| (2) headroom | R-rect solves ≥ 90% and R-rect/R-tree ≤ 0.5 | 73/96 = 76%; 0.573 (0.50–0.64) | no |
| (3) saving | R-all/R-tree ≤ 0.67 | 1.027 (0.96–1.10) | no |

Own-helper census 34/384 = 8.9% < 25%, so (1) fails with the label *low observed acquisition under this source
effort*. The report's `decision` block gives the same three failures and recommends returning to strategy. The
`mechanism_lead` flag is false and that reading is correct here: R-all/R-tree is 1.03, not ≤ 0.67.

## 5. What the data shows

- **Acquisition did not happen.** With 24 source cells, 8 builds and the frozen uncapped semantic recipe, no rectifier
  helper entered any library (0/96 helper-build pairs). The reason is measured, not inferred: source solvers contain
  the helper in 34/384 cases and the three-input sum in 326/384, so the recurrence rule (≥ 2 source cells) and the
  size filter (3–9 nodes) had almost nothing to pass. The one recurrent helper appeared at 19 nodes.
- **Headroom exists but is below the investment threshold.** Supplying the 12 helpers cuts the capped mean by
  43% (interval 36–50%) and raises solves from 20/96 to 73/96; 23/96 R-rect jobs still cap. This matches stage 0
  (11/16 vs 4/16) with far more data.
- **R-all does not help without the helpers.** Pooled sums and comparisons give a ratio of 1.03 to R-tree, interval
  spanning 1. The transported order libraries are slightly worse than R-tree (1.04, interval just above 1).
- **The stage-0 picture is reproduced on-harness** in every respect: easy sources, helper-free source solutions,
  hard destinations for all arms, strong but incomplete gain from supplied helpers.

## 6. What the data does not show

- It does not show that rectifier helpers *cannot* be acquired; it shows the frozen recipe acquired none under this
  source design. Sources admit a cheaper route (`max(a+b+c, c)`-style trees rooted in IF_GT), so the sources do not
  select for the reusable part. A different source family might.
- It does not establish helper causality for the R-rect gain beyond containment: R-rect solvers contain the supplied
  8-node helpers, but donor ancestry was not traced. The pairing and the magnitude make a non-helper explanation
  unlikely, but it is not excluded.
- It is a development roster (6 cells, 4 of them seen in stage 0 before the freeze), so no transfer or portability
  claim follows. The 24 protected cells were not searched.
- R-all vs R-order-all (0.99, 0.91–1.07) says nothing about which non-helper content is useful; both are near R-tree.
- With 66/96 double-capped units, capped means and solve counts are the informative quantities; time-to-solution
  beyond the cap is unknown.

## 7. Notes for the steward

- The code reviewer's minor note about `mechanism_lead` did not matter: coverage is 0 and the ratio is 1.03.
- Capped-job dominance means the worker-second ratio tracks the evaluation ratio (R-rect 0.59, R-all 1.00).
- The per-cell table suggests cell difficulty differs (R-tree 1/16 to 8/16), but 16 jobs per cell is too few to rank
  cells.

## Against the predictions

plan.md (read after the analysis above was written) is a probe plan: no outcome table, only the advisory
recommendation rule already evaluated in §4, plus the proposal's stated expectations. Checked item by item:

| Plan / proposal statement | Observed | Match |
|---|---|---|
| Queue about 26 min wall, 55 min of timeouts | prepare 11 s + score 1,151 s = 19.4 min; no deadline hit | yes |
| Fixed grids: 384 source jobs, 384 score jobs, failures charged, empty builds retained | 384 + 384, all failures at 524,288; no empty build (13–18 entries each) | yes |
| Validation gate, worktree extension path, bank digest `eb7965…` | passed in prepare; hashes recorded; protected searches 0 | yes |
| Own-helper census about 10% | 34/384 = 8.9% | yes |
| R-all holds a needed helper in ≤ 10/48 pairs | 0/48 | yes (lower end) |
| R-all/R-tree 0.8–1.1 | 1.03 (0.96–1.10) | yes |
| R-rect solves 65–80%, R-rect/R-tree about 0.6–0.8 | 76%; 0.57 (0.50–0.64) | solves yes; ratio slightly better than predicted |
| R-order-all worse than R-tree | 1.04 (1.00–1.08), 15 vs 20 solves | yes, marginally |
| Predicted outcome: both obstructions (acquisition and headroom) | all three advisory conditions fail; labels: low observed acquisition under this source effort, supplied prior below the investment threshold, R-all saving below threshold | yes |
| Surprises listed: helpers recurring over 8 builds; R-rect near the floor; R-all helping without helpers | none occurred: 1/96 helper-build recurrences (filtered by size), R-rect 23/96 capped, R-all ≈ R-tree | no surprise |
| "Saving ≤ 0.67 without coverage is a lead for 53" | ratio 1.03; no lead | n/a |
| "Near-one ratio with low coverage leaves rarity, emission filtering, donor usefulness and difficulty unresolved" | ratio is near one with zero coverage; this probe does add one measured fact: rarity at the source (34/384) precedes the size filter (8/96 emittable) and the recurrence rule (1/96), so filtering is not the main loss | partly resolved, as the plan allowed |

Verdict: every quantitative expectation in the proposal fell inside its predicted range, and the plan's advisory rule
returns "return to strategy; recommend ending this candidate at current allocation" with both the acquisition and
headroom labels. As a probe these are observations for question 54's log, not beliefs; the frontmatter is
`observations`.
