---
outcome: unresolved
---
# Analysis — 2033 one feedback batch under C4+F4 (A8) versus four more G4 attempts (S8)

Reviewer: independent re-analysis from the raw rows (`search.jsonl` and `collection.jsonl` of this run, the pinned 1743 rows in `experiments/chem_tape/data/sparse_feedback_2033/`, and 1036's `search.jsonl`), not from `result.json`. Every contrast below was recomputed; where `result.json` reports the same quantity the two agree to three decimals. Code at commit `e12edbf` (clean tree), code review pass.

Outputs: [prepare](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-2033-sparse-feedback-prepare), [score](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-2033-sparse-feedback-score). Plots in this folder: `per_corpus_ratios.png` (per-corpus forest plot of the five cost ratios) and `acquisition_per_build.png` (pooled solvers and charged acquisition per build). The runner's `cost_curves.png` and `diagnostics.png` are in the score folder.

## 1. Data completeness

Both queue entries finished with exit 0 and empty stderr, within timeout (prepare 652 s of 2 700; score 4 961 s of 10 800). Admission was timing-only and froze **16 seeds** (projection 5 357 s with margin; the 12-seed fallback was not used).

| check | result |
|---|---|
| prepare validation | passed: all 64 first-batch C4/F4 tables and libraries rebuilt bit-exactly against the pinned 1743 builds (64/64 decoder hashes, 64/64 library hashes); first-batch and S8 continuation attempt keys disjoint; replay of 16 retained C4+F4 rows, 16 full-F rows (1036) and 2 G4 rows; 2 048 forced empty-library edits identical for F and W; 10 000 suffix-edit audits passed |
| collection | 1 024 rows (16 corpora × 4 blocks × 4 training cells × 4 attempts), seeds unique and disjoint from source, scoring and timing seeds; failures kept |
| final builds | 128 (64 A8 + 64 S8), builds hash frozen before scoring |
| score validation | passed: 128/128 timing-smoke rows replayed bit-exactly before any efficacy search |
| scoring rows | 8 192 = 2 arms × 16 corpora × 16 then-addition cells × 16 seeds; 0 duplicates; 128 smoke rows kept separate under `phase: smoke` |
| blocks | every (corpus, block, arm) has 64 rows; every (corpus, cell, arm) has 4 seeds in each of blocks 0–3; `seed_ordinal % 4 == block` in all 8 192 rows |
| arm pairing | all 4 096 (corpus, cell, seed) A8/S8 pairs share training cases (0 mismatches); all 4 096 use different tables and different initial programs (as designed) |
| references | 4 096 each of retained C4+F4 (1743), full F and full C (1036) present for every key, same training cases (0 mismatches); replayed by sample, not rescored |
| cap / pop | all rows cap 524 288, pop 256; 0 rows above cap; 0 unsolved rows below cap |

Nothing is missing, nothing was resampled, no gate fell to the smaller roster. The roster is complete so the efficacy rule may be applied.

## 2. Sources and builds

Each of the 64 builds shares its first batch of 16 G4 attempts (4 per training cell) with 1743 and adds 16 more attempts per arm.

| | first batch (shared) | A8 second batch (C4+F4, new) | S8 second batch (G4, positions 16+4b..) |
|---|---|---|---|
| attempts | 1 024 | 1 024 | 1 024 |
| solvers | 615 (60.1 %) | **947 (92.5 %)** | 590 (57.6 %) |
| by family | | BE 459/512, PA 488/512 | |
| by block | | 232 / 242 / 237 / 236 of 256 | |
| mean evaluations per attempt | ~306 k (G4) | **96.6 k** | ~306 k (G4) |
| mean worker-s per attempt | | 4.9 (current hardware) | 8.5 (calibrated) |

Pooled per build (32 attempts): A8 **24.4** solvers (17–29), S8 **18.8** (11–26); A8 ≥ S8 in 64/64 builds (63 strictly, 1 tie). The first batch left 14 empty cells in 13 builds; A8 filled all of them (0 empty cells in 64 builds), S8 filled all but one (BE8 block 3). Library size: A8 at the cap of 32 fragments in 64/64 builds; S8 mean 31.75 (28–32, 5 builds below cap). Ground-truth fragments in the library: A8 10.6 per build, S8 9.2.

Charged acquisition per build in evaluations (first batch + intermediate build + continuation with failures + final build): A8 **6.51 M**, S8 **10.20 M**, seed C4+F4 4.97 M. So the adaptive second batch cost 1.54 M against the static batch's 5.23 M, **0.30×**, and A8 was cheaper in 64/64 builds. The proposal's probe (117/128 solved, ~100 k evaluations, 4.5 s per attempt, "about a third of a G4 batch") predicted the collection accurately.

## 3. Primary comparison

σ = cost(S8) / cost(A8); log capped cost averaged over cells and seeds within block, equal weight over the 4 blocks, then over corpora; unsolved = 2 × cap; 95 % t interval on 15 df. Decision thresholds: lower > 1.10 feedback works; upper < 1.10 not worth it; otherwise unresolved.

| | σ | 95 % | n | pairs |
|---|---|---|---|---|
| **primary** | **1.126** | **[1.039, 1.220]** | 16 corpora | 4 096 |
| 1 × cap penalty | 1.124 | [1.042, 1.212] | 16 | 4 096 |
| both-solved only | 1.138 | [1.057, 1.225] | 16 | 3 325 |
| BE corpora | 1.130 | [1.058, 1.208] | 8 | 2 048 |
| PA corpora | 1.122 | [0.944, 1.333] | 8 | 2 048 |
| block 0 | 1.186 | [1.020, 1.379] | 16 | 1 024 |
| block 1 | 1.075 | [0.946, 1.220] | 16 | 1 024 |
| block 2 | 1.152 | [1.027, 1.294] | 16 | 1 024 |
| block 3 | 1.095 | [0.915, 1.310] | 16 | 1 024 |

The interval straddles 1.10: **unresolved**. The same is true of every sensitivity, and every point estimate is above 1.10 except blocks 1 and 3. A8 is resolved *faster than S8* (interval excludes 1 for the primary, both cap penalties, both-solved, BE, and blocks 0 and 2; 14/16 corpus means above 1, the exceptions PA3 0.97 and PA4 0.79, SD of corpus log ratios 0.151). What is not resolved is whether the increment reaches the 1.10 worthwhile bar.

Row-level view: A8 cheaper in 2 112 of 4 096 paired rows, S8 in 1 905, tie 79. Solved: A8 **3 686/4 096** (90.0 %), S8 **3 675** (89.7 %); both 3 325, only A8 361, only S8 350, neither 60. Median evaluations among solved: A8 30.2 k, S8 32.8 k. The advantage is a modest shift in cost among solved searches, not a solve-rate difference.

Per cell (16 cells, 256 pairs each, descriptive, no multiplicity correction): σ ranges from 0.86 [0.69, 1.07] (`F>m?M+M:S`) to 1.55 [1.26, 1.91] (`F>m?M+m:S`); four cells have lower bound above 1 (`F>m?M+m:S`, `F>m?S+S:M` 1.29, `F>m?S+m:M` 1.20, `M>F?S+S:m` 1.37), none has upper bound below 1.

## 4. Against the seed and the full pipeline (no decision rule)

Same estimator; > 1 means the numerator costs more.

| contrast | ratio | 95 % | corpora > 1 |
|---|---|---|---|
| C4+F4 / A8 (does the adaptive batch help over the seed) | **1.517** | [1.373, 1.676] | 16/16 |
| C4+F4 / S8 (does the static batch help over the seed) | **1.347** | [1.227, 1.479] | 16/16 |
| full F / A8 (ρ_A8) | **1.031** | [0.951, 1.117] | 10/16 |
| full F / S8 (ρ_S8) | **0.915** | [0.839, 0.998] | 4/16 |
| full C / A8 | 1.511 | [1.391, 1.641] | 16/16 |
| full F / C4+F4 (1743 primary, replicated here) | 0.679 | [0.614, 0.752] | 0/16 |

Both enlarged sources beat the four-attempt seed decisively, by 52 % (A8) and 35 % (S8). A8 is **indistinguishable from the full 48-attempt pipeline** on this roster: ρ_A8 = 1.03 with interval [0.95, 1.12], and A8's solve count (3 686) sits next to full F's (3 719, 90.8 %). S8 is still resolved below full F, by about 9 %, with the upper bound just under 1. Read against 1743's retention rule (lower bound > 0.833), both eight-attempt sources would count as retained, A8 comfortably (0.951) and S8 by 0.006; that rule was not pre-registered for this run, so this is descriptive. Solve counts by block for A8 925/921/922/918 of 1 024, full F 920/933/936/930, C4+F4 881/897/874/867.

## 5. Economics (A + N·S, one deployed build, fully charged)

Arithmetic means over 16 corpora with equal block weight; S is capped evaluations per fresh search (unsolved charged at cap); worker-seconds use the replay calibration (seed 0.83, full 0.80, G4 0.63) and are indicative only.

| units | method | A (acquisition) | S (per capped search) | solve prob. |
|---|---|---|---|---|
| evaluations | A8 | 6.51 M | 113.3 k | 0.900 |
| evaluations | S8 | 10.20 M | 119.4 k | 0.897 |
| evaluations | C4+F4 | 4.97 M | 148.9 k | 0.859 |
| evaluations | full F | 61.3 M | 112.0 k | 0.908 |
| evaluations | G4 | 0 | 306.6 k | 0.633 |
| worker-s | A8 | 232 | 5.76 | |
| worker-s | S8 | 317 | 6.00 | |
| worker-s | C4+F4 | 153 | 6.16 | |
| worker-s | full F | 1 897 | 4.54 | |
| worker-s | G4 | 0 | 8.54 | |

Paired corpus-bootstrap (4 096 replicates, seed 2033) total-cost differences, evaluations unless stated:

- **A8 vs S8**: A8 is cheaper at every horizon. Difference −3.69 M at N = 0 [−3.86, −3.51], −4.1 M at N = 64 [−4.6, −3.5], −9.9 M at N = 1 024 [−17.7, −1.1], −28.5 M at N = 4 096 [−59.7, +6.5]. No crossover in 92 % of replicates (A8 has both the smaller A and the smaller S). In worker-seconds A8 is cheaper through N = 256 [−258, −19] and unresolved beyond.
- **A8 vs C4+F4**: A8 costs 1.54 M more up front and wins after N ≈ **44** fresh searches [35, 57] (≈ 200 worker-s searches [96, 1 455]). **S8 vs C4+F4**: wins after N ≈ **178** [133, 266] (≈ 1 065 in worker-s, with no crossover in 25 % of replicates).
- **A8 vs full F**: A8 is 54.8 M cheaper at N = 0 and its per-search cost is within noise of full F's, so the evaluation crossover is far out (point ≈ 42 k searches, [6 k, 275 k], and 35 % of replicates never cross). In calibrated worker-seconds full F is faster per search and overtakes A8 after ≈ 1 360 searches [1 020, 1 970]. S8 vs full F: evaluation crossover ≈ 6.9 k [3.5 k, 41.5 k]; worker-s ≈ 1 080 [850, 1 410].
- Against G4 (unpaired): A8 repays after 34 searches [29, 39], S8 after 55 [48, 63].

The runner charges S8 the intermediate C4+F4 build (about 0.2 worker-s), as the proposal said; it cannot move any curve.

## 6. Integrity checks

- Shortcut solutions (training-perfect programs that fail the full label set) never count as solved. Rows with any shortcut: A8 356/4 096, S8 301; unique shortcut programs A8 1.36 M, S8 0.86 M. A8 is somewhat richer in training-only solutions, but these cost A8 evaluations rather than helping it, so they cannot manufacture its advantage.
- Edit diagnostics are identical between arms: realised child fraction 0.200 vs 0.200, 2.99 vs 2.95 tokens changed per edit, same span histogram peak at 3. Fitness and diversity traces (runner's `diagnostics.png`) overlap.
- Timing: A8 5.76 and S8 6.00 worker-s per scoring search against 4.55 and 4.58 in the 128-row admission sample, about 27 % slower per search, but the scoring wall (4 961 s) still came in under the projection (5 357 s). The timing-smoke seeds were shared between arms (code review note 5) and were not used for efficacy.
- The replicated 1743 primary (0.679 [0.614, 0.752]) matches that run's analysis exactly, so the pinned references and estimator are the same.

## 7. Resolution price

With the observed SD of corpus log ratios (0.151), the half-width factor is 1.084 at n = 16. The runner's scenario (half-width factor 1.05) needs 40 corpora, 24 more; the plan's resolution-at-1.15 target (log half-width 0.0445) needs 47. But the point estimate is only 2.4 % above the threshold: to put the lower bound above 1.10 at this point estimate would need about **163 independent corpora**, and 24 more corpora would leave the lower bound near 1.07 if the point held. Resolution therefore depends on the true σ being nearer 1.15 than 1.13, not on an affordable top-up. Each new corpus also needs fresh G4 source attempts and a full-F reference (1.47 G evaluations of historical source and reference effort underlie the 16 used here).

## 8. What the data does and does not show

Shows:
- One batch of adaptive collection under a sparse, hole-ridden C4+F4 **does not lock in**: it solved 92.5 % of its training attempts (G4: 57.6 %), filled every empty cell, filled every library, and the rebuilt bias searched excluded compositions faster than the static eight-attempt build (σ resolved above 1) and at the full pipeline's level (ρ_A8 interval [0.95, 1.12] includes 1; 1743's four-attempt seed sat at 0.68).
- Doubling the source helps either way: both A8 and S8 beat the seed by 35–52 %.
- Adaptive collection is the cheaper way to buy the second batch: a third of the evaluations, and the total-cost curve for A8 lies below S8's at every horizon measured, with the paired interval excluding zero out to N = 1 024 in evaluations and N = 256 in worker-seconds.
- The search-speed increment of A8 over S8 is **unresolved against 1.10** under every sensitivity: the point estimates sit at 1.08–1.19 and all intervals cover 1.10.

Does not show:
- Whether the increment is worth 1.10×. An unresolved σ is not equivalence, and at this point estimate a resolving sample is prohibitive (§7).
- Why A8 is better: decoder versus library, and yield (more solvers) versus content (solvers found under the bias) are bundled. S8's libraries were at cap in 59/64 builds and it still lost, so library size alone is not the explanation, but nothing here separates the parts.
- Anything beyond one update on development sources and bank with external fitting: no second feedback round, no fresh bank, no inherited adaptation, no uncapped time to solve. Full-F worker-second comparisons rest on a 16-row replay calibration.
- Per-build reliability: aggregate σ averages 4 builds per corpus; two corpora (PA3, PA4) favoured S8.

## Against the predictions

Plan labels: lower bound > 1.10 **worthwhile final-search speed gain** over equal-attempt static acquisition; upper bound < 1.10 **excludes that speed increment**; otherwise **unresolved, not equivalence**. Measured σ = 1.126, 95 % [1.039, 1.220]: the interval covers 1.10, so the data match **unresolved**. The proposal said this outcome was the risk of its own prediction, and it happened.

- **Expected σ ≈ 1.15 [1.05, 1.26]** (proposal; plan derived a half-width factor of ~1.095 from a corpus SD of ~0.171). Observed 1.126 [1.039, 1.220], half-width factor 1.084, corpus SD 0.151. The interval came in slightly narrower than projected and the point slightly lower; the predicted and observed intervals overlap almost entirely. The 16-seed roster was admitted, so the 12-seed widening scenario did not apply.
- **Expected yields ≈ 24 vs 19 solvers per build, fewer empty cells, second batch about a third of S8's evaluations.** Observed 24.4 vs 18.8, 0 vs 1 empty cells across 64 builds, and 0.30× the evaluations. The probe's forecasts held on the full collection (947/1 024 solved against the probe's 117/128).
- **Expected both enlarged arms to beat C4+F4.** Observed: C4+F4 / A8 = 1.52 [1.37, 1.68], C4+F4 / S8 = 1.35 [1.23, 1.48], 16/16 corpora each.
- **Expected neither arm to reach full F (ρ ≈ 0.75–0.85).** Wrong in the favourable direction. ρ_A8 = 1.03 [0.95, 1.12] and ρ_S8 = 0.915 [0.84, 1.00], both above the expected range. The proposal listed "A8 ≥ full F" as a surprise; the data show A8 *matching* full F (interval includes 1), not exceeding it, so the surprise is half realised. Eight attempts, static or adaptive, recover most of what 1743 found four attempts lose.
- **Surprise "σ < 1" (lock-in).** Did not occur: σ is resolved above 1 under the primary estimator, both cap penalties, both-solved, BE, and blocks 0 and 2. The plan's reading of A8 < 1 as reinforcement is moot.
- **Plan's before-run interpretations.** The observed pattern is "increased yield and filled cells *with* a resolved speed improvement that falls short of 1.10". That falls between the plan's two named cases (yield without speed; speed without yield) and, as the plan anticipated, does not separate quantity or coverage from content. The plan's condition for supporting the update, "A8 beating the retained seed plus repayment at a useful N", is met: A8 beats the seed by 52 % and repays its extra 1.54 M evaluations after about 44 fresh searches [35, 57]. The plan's caution that cheaper acquisition with an unresolved σ is "only cheaper acquisition" is answered by the stated-horizon intervals: A8's total cost is below S8's with the paired interval excluding zero at every N up to 1 024 in evaluations (256 in worker-seconds); at N = 4 096 the interval covers zero.
- **Precision scenarios.** The plan computed that resolving 1.10 at a point of 1.15 needs a log half-width under 0.0445, about fourfold the information. The observed point is 1.126, which needs 0.0234, about 163 corpora at the observed SD. The plan's warning against seed-only top-ups stands: the limiting noise is between corpora, not seeds, and the honest resolution price is roughly ten times the corpora used, each with its own G4 source and full-F reference.
- **Feasibility.** Prepare 652 s (collection wall 554 s against the planned ~8 min), scoring 4 961 s against a 5 357 s projection; the whole queue took 94 min against the plan's 135 min estimate. The 16-seed roster fitted; no fallback, no infeasible.md.
- **Scope held.** One external-fitting update, development sources and bank, decoder and library bundled, no fresh-bank, inherited-adaptation or second-round claim. Critique note 5 (1743's block 0/1 upper bounds 0.858 and 0.912 do not exclude 0.833) remains for the steward to carry into the root-10 log, as plan.md deferred it.
