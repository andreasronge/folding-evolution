---
outcome: saving
---
# Analysis — protected signed-chain reuse confirmation (2150)

Reviewer, independent recompute from the raw `score.jsonl` rows in
`experiments/output/2026-10-11/2026-10-11-2150-{prepare,confirm}/` (code commit `83c7c5b`).
All numbers below were recomputed from rows with my own bootstrap (seed 12345, 4 000 draws, two-way
build × cell, repeats averaged inside each unit, arms paired); where `report.json` reports the same
quantity the two agree to the third decimal. Plots in this folder: `protected_cells_builds_cdf.png`
and `protected_restarts_coverage.png`.

## 1. Data completeness

| Phase | Rows | Expected grid | Duplicates | Missing | Seed tuple shared by the 3 arms per unit | Seeds reused | Exit |
|---|---|---|---|---|---|---|---|
| prepare | — (no search) | admission replay + 24 saved libraries | — | — | — | — | 0 in 111 s of 900 |
| confirm | 5 184 | 3 arms × 24 builds × 18 cells × 4 repeats | 0 | 0 | 1 728/1 728 | 0 of 13 824 | 0 in 5 105 s of 11 520 |

- `preparation.json`: `admitted: true`, `protected_searches: 0`, bank hash
  `e3873e17…` and the same method-freeze hash as the smoke preparation in smoke.md. The seed audit
  compared against 53 263 historical seeds (stage 0, 1938, 2044 development and smoke) and admitted.
- The 18 cells in the rows are exactly `bank.split.protected`; none of the 6 development cells
  appears. I scanned all 26 other `score.jsonl` files under `experiments/output/` and none contains a
  protected cell name, so these compositions were first searched here.
- Seeds run 20461000–20474823, 13 824 distinct, 8 consecutive per unit, disjoint from the 2044
  range (20450000–20452303), stage 0 (20440000–20443027) and the 2044 smoke seeds.
- Accounting on every row: `evaluations` equals the sum over attempts; every unsolved job has
  exactly 8 attempts and 524 288 evaluations; no solved job exceeds the cap; solvers are at most
  32 tokens. `solved` is set only after the full D625 check in the unchanged engine.
- Arm wiring: R-tree rows carry no library counters; R-all rows total 59.2 M library draws and
  R-gate 19.9 M, both with `empty_fallbacks: 0`. The attempt-level `arm: "tree"` field is the
  engine's search mode, identical in all three arms; the donor set is what differs.
- The `shortcuts` counter is the engine's count of training-perfect individuals that fail the exact
  D625 check (overfits), not a solution shortcut. All claimed solvers were re-executed against the
  labels by `validate_rows`.
- Throughput: 5 096 s scoring wall, 40 679 worker-seconds, 7.98 effective workers, 1.02 jobs/s,
  slowest job 36.1 s. The proposal's central estimate was 76 min; the run took 85 min, inside the
  planned 192 min deadline.

The dataset is complete and usable as designed. Nothing was dropped, resampled or topped up.

## 2. Validity checks (pre-stated, reported first)

| Check | Threshold | Observed | Flag |
|---|---|---|---|
| R-tree first-attempt solve rate (hard tier) | ≤ 85% | 467/1 728 = 27.0% | hard tier supported |
| R-tree capped jobs (cap-dominated) | ≤ 25% | 118/1 728 = 6.8% | not cap-dominated |
| R-gate solve rate (supplied reference reliable) | ≥ 95% | 1 728/1 728 = 100% | reliable |

All three pass, so the primary is interpreted as intended. The protected roster is at least as hard
for R-tree as the development roster in 2044 (27.0% first attempt and 178 k mean here against 30.2%
and 159 k there).

## 3. Key numbers (18 protected cells × 24 builds × 4 repeats = 1 728 jobs per arm)

### Arm summaries

| Arm | Jobs | Solves | Capped | First-attempt solves | ≥ 4 attempts | Capped mean evals | Median | p95 | Mean worker s | Max worker s |
|---|---|---|---|---|---|---|---|---|---|---|
| R-tree | 1 728 | 1 610 (93.2%) | 118 (6.8%) | 467 (27.0%) | 659 | 178 423 | 139 648 | 524 288 | 11.56 | 36.1 |
| R-all | 1 728 | 1 657 (95.9%) | 71 (4.1%) | 613 (35.5%) | 475 | 138 815 | 84 864 | 472 730 | 8.80 | 35.4 |
| R-gate | 1 728 | 1 728 (100%) | 0 | 1 125 (65.1%) | 78 | 46 917 | 15 488 | 166 630 | 3.18 | 33.4 |

Capped jobs contribute 20.1% of all R-tree evaluations and 15.5% of R-all evaluations. Mean
generations per job: R-tree 697, R-all 542, R-gate 183. R-all inserts about 13 800 library donors
per job, R-gate about 4 600; both reject about 60% of draws.

### Primary contrast and secondaries (ratio of pooled capped means; 95% two-way bootstrap)

| Contrast | Evaluations | Worker seconds | Report (evaluations) |
|---|---|---|---|
| **R-all / R-tree (primary)** | **0.778 [0.696, 0.870]** | 0.761 [0.680, 0.848] | 0.778 [0.694, 0.870] |
| R-gate / R-tree | 0.263 [0.233, 0.296] | 0.275 [0.244, 0.308] | 0.263 [0.233, 0.297] |
| R-gate / R-all | 0.338 [0.298, 0.383] | 0.361 [0.317, 0.409] | 0.338 [0.298, 0.386] |

- **Primary rule:** upper bound 0.870 < 1.00 → **saving**. The lower bound is 0.696, so the saving is
  between about 13% and 30% of R-tree's capped cost.
- **0.80 bar (label only):** lower 0.696 < 0.80 < upper 0.870 → **unresolved**. Neither a ">20%
  saving" nor "20% saving excluded".
- Resampling sensitivity for the primary: cells only [0.745, 0.812], builds only [0.717, 0.844],
  two-way [0.696, 0.870]. The two-way interval is the widest and is the pre-stated one; every
  variant excludes 1.
- Robustness of the point estimate: ratio of medians 0.61; ratio restricted to the 1 548 jobs where
  both arms solved 0.81; solved-only means 0.80; per-repeat ratios 0.73–0.81. The capped mean is
  the most conservative of these, so the result does not depend on how capped jobs are priced.
- Solve-fraction difference R-all − R-tree: +0.027 [+0.005, +0.050]. First-attempt difference:
  +0.085 [+0.029, +0.141]. Both small and in R-all's favour.

### Pairing at the unit level

- Paired jobs: R-all cheaper in 997 of 1 728 (57.7%), tied in 10, dearer in 721.
- Build × cell units (R-all mean of 4 repeats vs R-tree's): R-all cheaper in 291 of 432 (67.4%).
- Per cell (96 jobs per arm): R-all/R-tree below 1 in **18/18** cells, range 0.67–0.94; the
  per-cell build-bootstrap interval is below 1 in 8 cells and above 1 in none. R-tree first-attempt
  solves per cell range 20/96 to 35/96, so no protected cell is easy. R-gate/R-tree per cell ranges
  0.23–0.33.
- Per build (72 jobs per arm): R-all/R-tree ranges 0.56–1.09, below 1 in 20/24 builds. R-tree
  does not depend on the build, so its per-build means (148 k–216 k, CV 0.11) are pure seed-set
  noise; R-all's (108 k–186 k, CV 0.14) carry library quality plus noise. Four builds (1, 9, 20, 23)
  cost more than R-tree on their 72 units.

| cell | R-tree mean | R-all mean | R-gate mean | R-all/R-tree [build boot 95%] | R-tree first attempt |
|---|---|---|---|---|---|
| p02+n23+p31 | 190 293 | 126 613 | 48 661 | 0.67 [0.45, 0.94] | 22/96 |
| p23+n31+p10 | 194 760 | 133 085 | 44 696 | 0.68 [0.52, 0.88] | 21/96 |
| p21+n13+p30 | 188 043 | 130 032 | 48 539 | 0.69 [0.53, 0.91] | 21/96 |
| p10+n02+p23 | 179 320 | 127 413 | 41 032 | 0.71 [0.54, 0.90] | 29/96 |
| p03+n32+p21 | 176 147 | 128 093 | 46 392 | 0.73 [0.58, 0.89] | 21/96 |
| p12+n20+p03 | 177 579 | 131 000 | 46 928 | 0.74 [0.57, 0.93] | 28/96 |
| p20+n01+p13 | 182 240 | 134 675 | 42 896 | 0.74 [0.53, 1.00] | 20/96 |
| p03+n31+p12 | 191 600 | 142 491 | 49 752 | 0.74 [0.55, 0.98] | 25/96 |
| p21+n10+p03 | 175 541 | 135 861 | 54 149 | 0.77 [0.56, 1.06] | 26/96 |
| p10+n03+p32 | 178 016 | 138 795 | 47 131 | 0.78 [0.59, 1.04] | 32/96 |
| p31+n10+p02 | 180 693 | 145 325 | 43 933 | 0.80 [0.58, 1.12] | 23/96 |
| p32+n21+p10 | 185 181 | 149 040 | 48 920 | 0.80 [0.64, 1.01] | 26/96 |
| p12+n23+p30 | 172 141 | 141 336 | 41 184 | 0.82 [0.69, 0.96] | 25/96 |
| p01+n13+p32 | 159 387 | 132 216 | 50 051 | 0.83 [0.60, 1.14] | 35/96 |
| p32+n20+p01 | 164 829 | 137 744 | 55 099 | 0.84 [0.62, 1.10] | 29/96 |
| p13+n32+p20 | 181 693 | 156 400 | 43 037 | 0.86 [0.70, 1.06] | 24/96 |
| p02+n21+p13 | 173 656 | 158 232 | 43 747 | 0.91 [0.70, 1.21] | 28/96 |
| p31+n12+p20 | 160 491 | 150 320 | 48 365 | 0.94 [0.75, 1.16] | 32/96 |

### Needed-helper coverage (descriptive, confounded; never used for selection)

The 24 saved libraries keep on average 8.6 of 24 signed-gate helpers (37.4 semantic entries). On the
protected roster a build holds 0 / 1 / 2 / 3 of the cell's three needed helpers in
114 / 198 / 109 / 11 of the 432 build × cell pairs (26% / 46% / 25% / 2.5%).

| Needed helpers present | R-all jobs | R-all mean | R-all / paired R-tree | R-all / cell-matched R-tree mean | R-all capped | R-all first attempt |
|---|---|---|---|---|---|---|
| 0 | 456 | 175 994 | 0.98 | 0.99 | 34 (7.5%) | 28.9% |
| 1 | 792 | 141 168 | 0.78 | 0.79 | 31 (3.9%) | 33.1% |
| 2 | 436 | 102 847 | 0.59 | 0.57 | 6 (1.4%) | 44.0% |
| 3 | 44 | 67 561 | 0.42 | 0.37 | 0 | 61.4% |

The gradient is monotone and the paired and cell-matched columns now agree (in 2044 they
disagreed in the 0- and 3-helper strata because of seed luck). With none of the needed helpers the
saved library is worth nothing on this tier; with all three it is close to R-gate (67.6 k against
R-gate's 46.9 k pooled). Correlation between helpers kept per build and the build's ratio is −0.24
(2044: +0.19; 1938: −0.45). Still descriptive: stratum membership is confounded with library size and
with which cells a build happens to cover, and the 3-helper stratum has 11 units.

### Economics (evaluations; report values, formulas checked in `summarize`)

- Charged acquisition per saved build (from 1938): 215 520 [206 549, 226 017], range
  185 600–276 992.
- Saving per search R-tree − R-all: 39 608 [22 216, 57 093]. The interval excludes 0 (bootstrap
  fraction of non-positive savings 0.0001), so repayment is finite: **5.4 searches, 95% [3.8, 9.7]**.
- Newly deployed total minus R-tree total: at N = 10 searches −180 557 [−353 192, −6 956]
  (labelled lower total cost, just); at N = 100, −3.75 M [−5.49 M, −2.00 M]. At N = 1 the
  difference is +175 912, higher total cost, as it must be.
- Already-owned case: R-all costs 0.78 of R-tree per search with no acquisition term.
- Worker seconds give the same shape (repayment 3.8 searches, [2.7, 6.3]) but the 1938 acquisition
  seconds and today's deployment seconds ran under different load, so treat them as rough.

### Dynamics (`dynamics.png` in the output folder)

Exact-solve fraction against evaluations: R-gate pulls ahead from about 10³ evaluations and reaches
1.0 before the cap; R-all tracks above R-tree throughout, by a roughly constant margin on the log
axis, and both keep climbing to the cap. No arm plateaus early. Solver sizes are alike across arms
(mean 29.7 / 29.9 / 28.2 tokens, max 32), so no arm is finding systematically shorter programs.

## 4. What the data shows

1. **Frozen 1938 libraries cut capped search cost on never-searched hard compositions.** The
   primary, R-all/R-tree = 0.78 [0.70, 0.87] on evaluations and 0.76 [0.68, 0.85] on worker seconds,
   resolves as a saving. The ratio is below 1 in all 18 protected cells and in 20 of 24 builds.
   The point estimate reproduces the development probe's 0.79 on fresh cells, with an interval
   about 40% narrower (ratio of bounds 1.25 against 1.72). This is the first protected-cell result
   for the signed-gate libraries on the chain bank.
2. **The saving is modest.** The 95% interval runs from a 13% to a 30% saving. The 0.80 bar is
   unresolved, so the data neither establish nor exclude a 20% saving. Median cost falls by 39%,
   which says the saving concentrates in the easier half of jobs; the capped mean, which counts the
   tail, is the pre-stated statistic.
3. **Supplied helpers remain far ahead.** R-gate costs 0.26 [0.23, 0.30] of R-tree and
   0.34 [0.30, 0.38] of R-all, solves every job, and needs 4 or more attempts in 78 jobs against
   R-tree's 659. The acquired libraries close about a quarter of the gap between restarted tree GP
   and the full repertoire (on a log scale, log(0.78)/log(0.26) ≈ 0.18).
4. **The saving tracks needed-helper coverage.** R-all is even with R-tree when a build holds none
   of a cell's three helpers (0.98–0.99 on 456 jobs) and approaches R-gate when it holds all three
   (0.37–0.42 on 44 jobs). Nearly three quarters of build × cell pairs hold at most one needed
   helper, which is where the pooled 0.78 comes from. Descriptive and confounded, but much better
   measured than in 2044.
5. **Acquisition repays in about 5 searches** (95% [3.8, 9.7]) at the charged 216 k evaluations
   per build. At 10 searches on this tier the total cost of acquiring and reusing is lower than
   searching from scratch, though only just at the interval's edge.
6. **R-tree solves and caps slightly less than R-all.** Solve fraction +2.7 points [+0.5, +5.0],
   first-attempt +8.5 points [+2.9, +14.1]. Small, resolved, consistent with the cost saving.

## 5. What the data does not show

- **Not a transfer claim.** The 18 cells are protected but belong to the development chain bank
  (`x4-signed-chain-v1`), frozen with the method in 2044. The bank's shape, inputs and the
  acquisition recipe were chosen while developing on this family. A claim about other banks or
  shapes needs a fresh bank. The report's scope string says this.
- **Not whether the saving is material.** The 0.80 label is unresolved. Whether 13–30% is worth
  the acquisition depends on the horizon: 5 searches at the point estimate, up to 10 at the
  interval's edge.
- **Not helper causality.** The coverage gradient is an association across builds. Only an
  ablation (R-all plus the missing helpers, or R-gate restricted to the three needed) would
  separate helper presence from the rest of the library content and from library size.
- **Not uncapped time-to-solution.** Means are capped at 8 × 65 536; 20% of R-tree evaluations
  come from capped jobs. The solved-only (0.80) and both-solved (0.81) ratios agree with the capped
  mean, so the cap is not driving the result, but a different cap would move the number.
- **Not stable per build with 72 jobs.** Four builds come out dearer than R-tree, but R-tree's own
  per-build means vary by 11% from seed luck alone, so individual build rankings are noisy.
- **Not about why acquisition keeps a third of the helpers.** This run used the libraries as
  saved; it says nothing about the acquisition step.

## Against the predictions

Read after the analysis above was written. plan.md defines the primary labels (saving / harm /
unresolved), the secondary 0.80 labels, three validity flags and a set of competing readings; the
proposal adds expectations, surprises and a resolution forecast.

| Prediction (plan / proposal) | Observed | Verdict |
|---|---|---|
| Primary: saving if 95% upper bound of R-all/R-tree < 1.00; harm if lower > 1.00 | 0.778 [0.696, 0.870] | **Saving.** Matches the plan's "resolved saving supports useful frozen acquired bias on these protected linked compositions". |
| Secondary 0.80 bar: ">20% saving" if upper < 0.80; "20% saving excluded" if lower > 0.80 | lower 0.696, upper 0.870 | **Unresolved**, as the proposal forecast ("the 0.80 bar should stay unresolved near 0.79"). Not evidence of a tightly small effect, per the plan. |
| Validity: R-tree first-attempt ≤ 85% | 27.0% | Passed. Hard-tier interpretation stands. |
| Validity: R-tree capped ≤ 25% | 6.8% | Passed. Not cap-dominated. |
| Validity: R-gate solves ≥ 95% | 100% | Passed. Supplied reference reliable. |
| Proposal forecast: probability the saving rule resolves at true ratio 0.79 about 0.6 (doubled variance) to 0.85 (central); expected interval width ratio 1.53 / 1.35 | Resolved; observed width ratio 0.870/0.696 = 1.25 | Resolved, and narrower than either forecast scenario. The 2044 variance model was pessimistic for the protected roster, probably because 18 cells average out the cell axis better than 6. |
| Expectation: R-all/R-tree 0.75–0.90, barely resolved or unresolved | 0.78, resolved | Inside the range; resolved more cleanly than expected. |
| Expectation: R-gate/R-tree 0.25–0.35 | 0.26 [0.23, 0.30] | Inside the range. |
| Surprise: resolved harm | lower bound 0.70 | Not observed. |
| Surprise: protected R-tree mostly first-attempt (stage-0 cells atypically hard) | 27% first attempt, below 2044's 30% | Not observed. Protected cells are at least as hard as the development cells. |
| Surprise: R-all within 1.5× of R-gate | R-all/R-gate 2.96 [2.59, 3.36] | Not observed. The plan's "R-all near R-gate despite incomplete coverage" reading does not apply; the "R-gate advantage with weak R-all" reading does, with the caveat it does not isolate helper causality. |
| Surprise: R-gate capping often | 0 caps, max 8 attempts once | Not observed. |
| Economics: repayment interval unbounded if the saving interval includes 0; compare A + N·C_all with N·C_tree at N = 10 and 100 | saving 39.6 k [22.2 k, 57.1 k] excludes 0; repayment 5.4 [3.8, 9.7]; N = 10 lower total cost (interval edge −7 k); N = 100 lower total cost | Bounded, as the proposal's point estimate (about 7 searches) suggested; slightly faster than that. |
| Runtime: about 76 min central, 152 min doubled tails, 207 min summed timeouts | 85 min scoring, 87 min queue, inside timeouts | Close to central; the smoke's revised 86 min was almost exact. |

What the plan says about this outcome: a resolved saving "supports useful frozen acquired bias on
these protected linked compositions; its economic value depends on measured absolute saving and
horizon." The measured saving is 13–30% per search on the capped mean, and acquisition is repaid
after 4–10 searches. The plan's reservations still apply: this is within the development chain bank,
depth and sharing remain confounded, and the coverage gradient does not isolate helper causality.
The proposal's stated next action, return to strategy, is unchanged by the result; the one thing
the data add to that discussion is a now well-measured coverage gradient (0.98 → 0.42 across the four
strata), which sharpens the question of why acquisition keeps about a third of the helpers.
