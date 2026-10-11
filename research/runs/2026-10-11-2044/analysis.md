---
outcome: observations
---
# Analysis — signed-chain depth probe (2044)

Reviewer, independent recompute from the raw `score.jsonl` rows in
`experiments/output/2026-10-11/2026-10-11-2044-{prepare,development}/` (code commit `8a621df`).
All numbers were recomputed from rows; where `report.json` also reports them they agree to the stated
precision. My bootstrap uses a different seed (1, 8 192 draws) from the report's (202610112044, 8 192).
This is a `kind: probe`: everything below is an observation, not a belief.

## 1. Data completeness

| Phase | Rows | Expected grid | Duplicates | Missing | Seeds shared by the 3 arms per unit | Seeds reused | Capped jobs |
|---|---|---|---|---|---|---|---|
| prepare | — (no search) | admission replay + 24 saved libraries | — | — | — | — | — |
| development | 864 | 3 arms × 24 builds × 6 cells × 2 repeats | 0 | 0 | 288/288 | 0 of 2 304 | 26 (see below) |

- Both queue entries exited 0, inside their timeouts: prepare 111 s of 900, development 765 s of 2 400. No `failure.json`.
- Bank admitted all 24 chain destinations; 6 development cells (the 4 stage-0 cells plus `p20+n03+p31`, `p23+n30+p01`) and 18 protected, `protected_searches: 0`. Bank hash and preparation hash match the committed `presearch.json.gz` values quoted in smoke.md and code_review.md.
- Seeds 20450000–20452303, 2 304 distinct, none inside stage 0 (20440000–20443027) or 1938's range; every unit's 8-seed tuple is identical across R-tree, R-all and R-gate.
- Accounting checks pass on every row: attempt seeds equal the row's seed list, `evaluations` is the sum over attempts, unsolved attempts are exactly 65 536, unsolved jobs have exactly 8 attempts and 524 288 evaluations, no solved job has an earlier solving attempt, solvers are at most 32 tokens. `solved` is set only after the full D625 check in the shared engine (unchanged from 1938).
- Arm wiring as reviewed: R-tree rows carry no library counters, R-all and R-gate carry library draws/insertions with `empty_fallbacks: 0`.

The dataset is complete and usable as designed. Nothing was dropped or resampled.

## 2. Key numbers (6 development cells × 24 builds × 2 repeats = 288 jobs per arm)

### Arm summaries

| Arm | Jobs | Solves | Capped | First-attempt solves | ≥ 4 attempts | Capped mean evals | Median | p95 | Mean worker s | Max worker s |
|---|---|---|---|---|---|---|---|---|---|---|
| R-tree | 288 | 272 (94.4%) | 16 (5.6%) | 87 (30.2%) | 89 | 158 683 | 105 216 | 524 288 | 9.93 | 35.2 |
| R-all | 288 | 278 (96.5%) | 10 (3.5%) | 106 (36.8%) | 64 | 125 836 | 78 208 | 457 690 | 7.70 | 34.0 |
| R-gate | 288 | 288 (100%) | 0 | 186 (64.6%) | 12 | 47 269 | 18 048 | 156 032 | 3.09 | 19.1 |

For scale, 1938's protected R-tree on the two-piece family had a capped mean of 7 775 evaluations and 97.7% first-attempt solves. The chain bank is about 20× dearer for R-tree, and 70% of R-tree jobs need a restart.

Attempt-level success probability (solves / attempts started): R-tree 0.31 (874 attempts), R-all 0.37 (753), R-gate 0.65 (445). Capped jobs contribute 18.4% of all R-tree evaluations and 14.5% of R-all evaluations, so the capped means lean on the 8-attempt cap; the ratio of medians (0.74) and the ratio restricted to the 262 units where both arms solved (0.79) tell the same story as the capped-mean ratio.

### Contrasts (ratio of pooled capped means; 95% two-way bootstrap over builds and cells, repeats retained, arms paired)

| Contrast | Evaluations | Worker seconds | Report (evaluations) |
|---|---|---|---|
| R-all / R-tree | **0.793 [0.60, 1.03]** | 0.775 [0.58, 1.00] | 0.793 [0.596, 1.023] |
| R-gate / R-tree | **0.298 [0.23, 0.38]** | 0.311 [0.24, 0.40] | 0.298 [0.234, 0.385] |
| R-gate / R-all | 0.376 [0.27, 0.51] | — | not in report |

Resampling sensitivity for R-all/R-tree: builds only [0.65, 0.96], cells only [0.68, 0.89], two-way [0.60, 1.03]. Each single axis would exclude 1; the two-way interval does not. Solve-fraction difference R-all − R-tree: +0.021 [−0.03, +0.08]. First-attempt difference: +0.066 [−0.04, +0.17].

### Pairing at the unit level

- R-all cheaper than R-tree in 160 of 288 units (55.6%), equal in 2, dearer in 126. R-gate cheaper than R-tree in 232 of 288 (80.6%).
- Per cell (48 jobs per arm per cell): R-all/R-tree is below 1 in 6/6 cells, range 0.56 – 0.90; R-gate/R-tree range 0.25 – 0.37. R-tree first-attempt solves per cell range 10/48 to 19/48, so no development cell is easy.
- Per build (12 units per build): R-all/R-tree ranges 0.24 – 1.96, median 0.74, below 1 in 14/24 builds. Build-to-build spread is large, but R-tree does not depend on the build, so the "build" axis for R-tree is 24 seed sets whose means already range 83 k – 241 k (CV 0.29). R-all per-build means range 53 k – 233 k (CV 0.34). Most of the per-build ratio spread is search noise, not library quality.

| cell | R-tree mean | R-all mean | R-gate mean | R-all/R-tree | R-gate/R-tree | R-tree first attempt |
|---|---|---|---|---|---|---|
| p01+n12+p23 | 128 853 | 116 277 | 41 797 | 0.90 | 0.32 | 19/48 |
| p13+n30+p02 | 151 035 | 128 635 | 40 005 | 0.85 | 0.26 | 18/48 |
| p20+n03+p31 | 159 019 | 142 597 | 39 963 | 0.90 | 0.25 | 10/48 |
| p23+n30+p01 | 167 685 | 127 771 | 61 888 | 0.76 | 0.37 | 14/48 |
| p30+n01+p12 | 148 384 | 129 675 | 42 784 | 0.87 | 0.29 | 14/48 |
| p30+n02+p21 | 197 120 | 110 064 | 57 179 | 0.56 | 0.29 | 12/48 |

### Needed-helper coverage (descriptive, confounded; never used for selection)

The 24 saved libraries keep on average 8.6 of 24 signed-gate helpers (37.4 semantic entries). Over all 576 build × cell pairs, a build holds 0 / 1 / 2 / 3 of the cell's three needed helpers in 144 / 275 / 138 / 19 pairs (25% / 48% / 24% / 3.3%, as stage 0 counted). On the development roster: 30 / 77 / 29 / 8 pairs.

| Needed helpers present | Units | R-all mean | R-all / paired R-tree | R-all / cell-matched R-tree mean | R-gate mean (same units) |
|---|---|---|---|---|---|
| 0 | 60 | 161 890 | 1.24 | 1.02 | 45 828 |
| 1 | 154 | 128 525 | 0.76 | 0.81 | 51 329 |
| 2 | 58 | 99 187 | 0.60 | 0.64 | 38 223 |
| 3 | 16 | 61 360 | 0.47 | 0.37 | 46 384 |

The paired denominators in the 0- and 3-helper strata happen to be lucky seed sets (paired R-tree mean 0.80–0.82 of the cell expectation), so the cell-matched column is the fairer read. Either way the gradient is monotone: with none of the needed helpers R-all is about even with R-tree here, unlike 1938 where the no-helper stratum still saved 23%. Correlation between helpers kept and the build ratio is +0.19 (1938: −0.45); between mean development coverage and the build ratio −0.20. With 16 units in the top stratum and heavy search noise, none of this is more than a hint.

### Economics (evaluations; report values, recomputed where shown)

- Charged acquisition per saved build (from 1938): 215 520 [206 421, 225 312], range 185 600 – 276 992.
- Saving per search R-tree − R-all: 32 846 [−3 212, 74 040]. Point repayment 6.6 searches; the interval runs from 2.9 searches to never, because the saving's interval includes 0.
- Newly deployed difference at N = 10 searches: −112 942 [−524 072, +251 108]; at N = 100: −3.07 M [−7.18 M, +0.54 M]. Worker-seconds give the same shape (repayment 4.7 searches, point), but 1938's acquisition seconds and today's deployment seconds ran under different load, so treat the second-based figures as rough.

### Dynamics and library use

- Mean generations per job: R-tree 620, R-all 492, R-gate 185. R-all inserts about 12 500 library donors per job and rejects 60% of draws; R-gate inserts about 4 600 and rejects 60%. Rejection rates are the same, so R-gate's advantage is not a donor-admissibility artefact.
- Solver sizes are alike across arms (mean 29.6 / 30.0 / 28.4 tokens; maximum 32, the solver limit). Solutions use most of the token budget in every arm, which is consistent with a 20-token canonical form plus slack, and does not suggest a shortcut.
- The runner's `dynamics.png` (output folder) shows exact-solve fraction against evaluations: R-gate pulls ahead from about 10³ evaluations, R-all tracks slightly above R-tree throughout, and all three keep climbing to the cap, i.e. no arm plateaus early.

### Throughput (for pricing)

| Quantity | Value |
|---|---|
| Scoring wall | 758 s for 864 jobs (1.14 jobs/s) |
| Worker seconds | 5 967 (mean 6.9 per job) |
| Effective concurrency | 7.87 of 8 workers |
| Slowest job | 35.2 worker-s (a capped R-tree job) |

The proposal's estimate (11 min of scoring at 7.6 effective workers) was accurate: 12.6 min observed, with 26 capped jobs.

### Confirmation forecast (report's model, rechecked)

Variance components of the paired normalised difference (method of moments, crossed 24 × 6 × 2): build 0.110, cell 0.002, build × cell 0 (truncated), search 2.09. Search noise dominates; the cell and interaction components are estimated from 5 and 115 degrees of freedom and are unreliable.

| Protected design (18 cells × 24 builds) | Jobs | Central wall | 2× tail | Summed timeouts | Expected upper/lower (central) | (2× variance) |
|---|---|---|---|---|---|---|
| r = 1 | 1 296 | 19 min | 38 min | 65 min | 1.47 | 1.72 |
| r = 2 | 2 592 | 38 min | 76 min | 112 min | 1.39 | 1.60 |
| r = 4 | 5 184 | 76 min | 152 min | 207 min | 1.35 | 1.53 |

Two cautions on the central scenario. First, applied to this probe's own design (6 cells, r = 2), the same model predicts an interval ratio of 1.54, while the probe's bootstrap interval actually has a ratio of 1.72; the 2× scenario (1.85) brackets it. The central numbers are therefore optimistic and the 2× column is the better planning anchor. Second, precision is not decisiveness: with the proposal's intended primary rule (upper < 0.80 saving, lower ≥ 0.80 excluded), an r = 2 confirmation is expected to come out unresolved for any true effect between about 0.68 and 0.94 (central) or 0.63 and 1.01 (2×). The probe's point estimate, 0.79, sits in the middle of that band.

Report flags: `hard` true, `not_ceilinged` true, `precise_and_affordable` true (central scenario only, as code_review.md noted), `consider_separately_approved_confirmation` true. These are flags for strategy, not an authorisation.

## 3. What the data shows

1. **The chain bank is a hard tier for restarted tree GP without being capped.** R-tree solves 30% of jobs on the first attempt, needs 4 or more attempts in 89/288, and caps in 16/288; the capped mean is 159 k evaluations against 7.8 k on the two-piece family. R-gate still solves 288/288 with at most 5 attempts, so the targets are reachable and the difficulty is in assembly, not in the token limit or the domain.
2. **The supplied helper repertoire has large headroom over the saved libraries.** R-gate costs 0.30 [0.23, 0.38] of R-tree and 0.38 [0.27, 0.51] of R-all, cheaper than R-tree in 81% of paired units and in 6/6 cells. This is about the same relative advantage R-gate had on the easy family (0.25).
3. **The saved 1938 libraries show a small, unresolved saving.** R-all/R-tree = 0.79 [0.60, 1.03] on evaluations, 0.78 [0.58, 1.00] on worker seconds; below 1 in all 6 cells but in only 56% of paired units and 14/24 builds. A 40% saving is excluded; neither "no saving" nor the 0.80 usefulness bar is resolved. R-all also caps less (10 vs 16) and solves on the first attempt more often (37% vs 30%), both unresolved.
4. **The saving, where it appears, tracks needed-helper coverage more tightly than on the easy family.** With none of a cell's three helpers present, R-all is about even with R-tree (ratio 1.02 against the cell-matched mean, 1.24 paired); with all three it is 0.37–0.47. Only 3% of build × cell pairs have full coverage. This is descriptive and confounded with library size and seed luck.
5. **Repayment is faster per search than in 1938 but less certain.** The point saving of 33 k evaluations per search repays the 216 k acquisition in about 7 searches, versus 66 on the easy family, but the saving's interval includes zero.
6. **Pricing.** A protected confirmation at r = 2 is 2 592 jobs, about 38 min central and 76 min with doubled tails, well under the 4 h cap; r = 4 also fits (207 min of summed timeouts).

## 4. What the data does not show

- **No protected effect.** All six cells are development cells; four were chosen by stage 0, which saw them. Nothing here is a transfer claim.
- **Not resolved at the planned threshold.** The probe cannot say whether R-all saves 20% or more; a confirmation with the proposed 0.80 rule is more likely than not to be unresolved if the true effect is near 0.79. If strategy wants a decidable confirmation, it should either pick a rule that the forecast can resolve at this effect size (for example, "any saving": upper bound of R-all/R-tree below 1, which r = 2 is expected to resolve for true effects below about 0.85 under the central scenario and 0.79 under 2×) or accept that the intended question is "is the saving material" and that the probable answer is "unresolved, small".
- **Not helper causality.** The coverage gradient is suggestive but confounded; R-gate's success does not identify whether missing helpers or other library content is the limiting factor. An ablation (R-gate restricted to the three needed helpers, or R-all plus the missing helpers) would be needed and is not proposed here.
- **Not uncapped time-to-solution.** Means are capped at 8 × 65 536; 18% of R-tree evaluations come from capped jobs. A different cap would change the ratio.
- **Not stable per build.** 10 of 24 builds are dearer than R-tree on their 12 units, but the per-seed-set R-tree means vary by nearly 3×, so per-build ratios are mostly search noise with two repeats.
- **Stage 0 was slightly optimistic about R-tree.** Stage 0 had 6/12 first-attempt solves and a 138 k mean on 4 cells; the probe has 30% and 159 k on 6 cells. The two new cells (10/48 and 14/48 first attempt) are at least as hard as the stage-0 four.

Plots in this folder: `development_cells_builds_cdf.png` (per-cell arm means; per-build R-all/R-tree against helpers kept; evaluation CDF per arm) and `development_restarts_coverage.png` (attempt-of-solve histogram with capped jobs; paired R-all/R-tree by coverage stratum).

## Against the predictions

Read after the analysis above was written. plan.md has no outcome table (probe); it lists interpretive readings and three recommendation criteria, and the proposal gives expectations and surprises.

| Prediction (proposal / plan) | Observed | Verdict |
|---|---|---|
| Criterion 1, hard: R-tree first-attempt rate ≤ 85% on development cells | 87/288 = 30.2% | **Met**, by a wide margin. Plan's "mostly first-attempt R-tree" reading does not apply; the difficulty boundary is real. |
| Criterion 2, not ceilinged: R-gate solves ≥ 95% and R-tree capped ≤ 25% | R-gate 288/288; R-tree capped 16/288 = 5.6% | **Met.** Plan's "heavy capping across arms" reading does not apply. |
| Criterion 3, decisive and affordable: some r gives expected upper/lower ≤ 1.6 within 4 h summed timeouts | r = 1: 1.47 central / 1.72 at 2×; r = 2: 1.39 / 1.60; r = 4: 1.35 / 1.53; all under 4 h (65, 112, 207 min) | **Met** on the central scenario at every r; at doubled variance only r = 2 (borderline) and r = 4. The model under-predicts the probe's own interval width (1.54 vs 1.72), so plan on the 2× column. |
| Report flag: consider a separately approved confirmation | all three flags true | **Raised**, as a flag to strategy only. |
| Expected R-tree first attempt 40–70%, mean 100–200 k | 30%, 159 k | First-attempt rate below the expected range (harder than stage 0 suggested); mean inside it. |
| Expected R-gate/R-tree 0.15–0.35 | 0.30 [0.23, 0.38] | Inside the range. |
| Expected R-all/R-tree 0.6–0.9, interval wide | 0.79 [0.60, 1.03] | Inside the range; interval wide as expected and spans both 0.80 and 1. |
| Surprise: R-all ≥ 1 | 0.79, upper bound 1.03, below 1 in 6/6 cells | Not observed as a point estimate; not excluded. |
| Surprise: R-all close to R-gate despite 3% full coverage | R-gate/R-all 0.38 [0.27, 0.51] | Not observed. R-all is much nearer R-tree than R-gate. |
| Surprise: R-tree mostly first-attempt on the two new cells | 10/48 and 14/48 | Not observed; the new cells are as hard as the stage-0 four. |
| Surprise: R-gate capping often (linking, not supply, limits search) | 0 capped, max 5 attempts | Not observed; supply is a large part of what limits R-tree. |
| Plan reading: "R-all saving suggests deeper reuse worth pricing, no protected claim" | small unresolved saving; coverage gradient steeper than in 1938 | This is the reading that applies, with the caveat in §4 that the intended 0.80 primary rule is forecast to be unresolved at this effect size. |
| Runtime: central 10.4 min scoring, 24 min with 10% caps at smoke concurrency | 12.6 min scoring at 7.87 effective workers, 3% of jobs capped; 765 s total of 2 400 | As estimated. |

Outcome label: `observations` (probe). The three recommendation criteria the plan set are all met, so the report's flag to strategy stands; whether a confirmation is worth 2–3.5 h depends on choosing a primary rule the forecast can actually resolve at an effect near 0.8, which is a strategy decision, not a data result.
