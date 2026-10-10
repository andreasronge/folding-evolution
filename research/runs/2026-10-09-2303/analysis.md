---
outcome: useful_retention
---
# Analysis — 2303 frozen A8 versus full F, S8 and G4 on the fresh two-sum-v1 bank

Code: commit `74196a8` on `research/2026-10-09-2303`. Queue runner exit 0, both entries done.
Outputs: [prepare](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-2303-two-sum-prepare), [score](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-2303-two-sum-score). Plot in this folder: `per_corpus_ratios.png` (per-corpus forest plots of ρ and σ, per-cell solve fractions). The runner's `diagnostics.png` and `cost_curves.png` are in the score folder.

All numbers below were recomputed from `search.jsonl` with an independent script; every one matches `result.json`. The primary ratio, its interval, σ, the per-arm solve counts and the pooled G4 ratios agree to the printed precision.

## 1. Data completeness

| check | result |
|---|---|
| prepare stage | done, 246 s wall (limit 2 700). Bank, builds, freeze, schedules, 50 historical replay rows and 112 timing rows written; `validation.passed = true` |
| stage 0 admission | 8-seed/all-arms projected 13 902 s (× 1.15 > 150 min, rejected); **4-seed/all-arms** projected 7 274 s, admitted; 4-seed/no-S8 not needed. Pre-registered fallback order followed |
| score stage | done, 6 252 s wall (limit 10 800, deadline 10 680), under the 7 274 s projection; `progress.json` 3 328/3 328, phase `two_sum` |
| rows in `search.jsonl` | **3 328** = 16 corpora × 16 cells × 4 blocks × 1 ordinal × 3 fitted arms (3 072) + 16 cells × 16 G4 seeds (256) |
| per fitted arm | 1 024 rows; 16 corpora × 64; every (corpus, block) has exactly 16 rows; ordinals 0–3; blocks 0–3 |
| G4 | 256 rows, 16 per cell, 64 per block label |
| duplicates | 0 on (arm, cell, corpus, block, ordinal); 0 on (arm, cell, seed) |
| pairing | all 1 024 (corpus, cell, block, ordinal) triples have A8, S8 and full F with identical seed and identical 64 training indices; 0 bad |
| seed disjointness | 1 024 fitted seeds, 256 G4 seeds, overlap 0 |
| cap / pop | all rows cap 524 288, pop 256; no row above cap; every unsolved row stopped exactly at cap (enforced by `jobs()` on save) |
| solve definition | a training-perfect program (64/64 cases) that also matches the target on all 1 331 inputs; training-only "shortcut" programs are counted but never solved |
| timing replay | 112/112 timing rows replayed at the start of the score stage with identical solved/evaluations/solver; 0 mismatches. The 4 timing cells are disjoint from the 16 confirmation cells |
| historical replay | 16 A8, 16 S8, 16 full F (1036) and 2 G4 rows replayed with scientific fields equal to the stored references (`validation.passed`); 2 048 empty-fallback edits identical for F and W; 10 000 suffix-edit audits passed |
| errors | 0 rows with an error key; `stderr.log` empty in both stages |

Nothing is missing, duplicated or failed. The roster is the 4-seed fallback (1 seed per block per cell per corpus), half the proposal's preferred 8-seed design, chosen by the stage-0 rule exactly as pre-registered.

Bank (`bank.json`): 444 raw assignments → 333 non-constant → 289 distinct behaviours → 76 eligible after the ≤9-token screen and the <80 % agreement filter against all 306 old-roster behaviours; 16 confirmation + 4 timing cells picked by SHA-256 order with ≤4 per unordered gate pair (MS, Sm, FM, FS, Fm) and mutual agreement <80 % (max 0.78). Canonical outputs validated on all 1 331 inputs in both Python and Rust with 0 mismatches. Selection used labels only; no search performance entered it.

## 2. Primary comparison: ρ = cost(A8) / cost(full F)

Estimator as pre-registered: log capped evaluations, unsolved = 2 × cap, mean over cell/seed pairs within (corpus, block), equal block weights, 16 corpus contrasts, 95 % t interval on 15 df.

| | ρ | 95 % | n | pairs |
|---|---|---|---|---|
| **primary** | **0.945** | **[0.819, 1.092]** | 16 corpora | 1 024 |
| cap penalty 1× | 0.958 | [0.843, 1.088] | 16 | 1 024 |
| both solved only | 0.976 | [0.799, 1.193] | 15 (PA5 block 0 empty) | 308 |
| BE corpora | 0.922 | [0.770, 1.103] | 8 | 512 |
| PA corpora | 0.969 | [0.735, 1.278] | 8 | 512 |
| block 0 | 0.951 | [0.747, 1.210] | 16 | 256 |
| block 1 | 0.863 | [0.678, 1.098] | 16 | 256 |
| block 2 | 0.823 | [0.607, 1.117] | 16 | 256 |
| block 3 | 1.183 | [0.952, 1.470] | 16 | 256 |

Inverted to 2033's convention, cost(full F)/cost(A8) = 1.058 [0.916, 1.222], against 1.031 [0.951, 1.117] on then-addition. The point estimate moved slightly in A8's favour; the interval is wider (corpus log-SD 0.270 here versus 0.151 in 2033, with half the seeds).

Per corpus (mean over 4 blocks): A8 cheaper in 10/16 corpora. Corpus ratios range from 0.62 (PA6) to 1.72 (PA4). Every single-corpus interval (4 blocks, 3 df) includes 1 except PA4; PA4 and PA3 also favoured S8 over A8 in 2033, so those two sources may be genuinely weaker for the cheap pipeline, but 2 of 16 is not a pattern this design can confirm.

Row level: A8 cheaper in 376 of 1 024 paired rows, full F in 339, tie 309 (nearly all ties are both-unsolved at cap). Joint solves (A8, full F): both 308, A8 only 213, full F only 194, neither 309.

**Decision rule.** Upper bound 1.092 < 1.20: ρ does not show a material loss. Lower bound 0.819 < 1: the sign of any difference is unresolved. The pre-registered label for UB < 1.20 is bounded retention, conditional on the two guards below.

## 3. Guards: usefulness against G4 and the full-F solve floor

| method | solved / n | fraction | geometric capped cost | G4 / method cost ratio (95 %) |
|---|---|---|---|---|
| A8 | 521 / 1 024 | 0.509 | 257 k | **2.73 [2.36, 3.17]** |
| S8 | 482 / 1 024 | 0.471 | 302 k | 2.33 [2.07, 2.61] |
| full F | 502 / 1 024 | 0.490 | 272 k | 2.58 [2.28, 2.90] |
| G4 | 51 / 256 | 0.199 | 702 k | — |

G4 intervals: G4 seeds resampled within each fixed cell, each draw shared across every corpus and method, corpora resampled stratified by family, 8 192 replicates (critique note 4). All three fitted arms are resolved faster than G4 by a factor of two to three. The full-F solve guard (≥ 25 %) passes at 49.0 %. Both guards pass, so the runner's label **useful_retention** is the one the pre-registered rule produces.

## 4. σ = cost(S8) / cost(A8) (reported, no rule)

| | σ | 95 % | n |
|---|---|---|---|
| primary estimator | **1.173** | **[1.036, 1.327]** | 16 |
| cap penalty 1× | 1.142 | [1.031, 1.266] | 16 |
| both solved only | 1.133 | [0.930, 1.381] | 16 (300 pairs) |
| S8 / full F | 1.109 | [0.991, 1.241] | 16 |

S8 is again resolved slower than A8 (lower bound above 1 under both cap penalties), 12/16 corpora favour A8, and the point sits at 2033's 1.126 or above. The code review warned σ might be driven by the 2·cap penalty; the 1× penalty and the both-solved estimates say otherwise, the gap is in cost among solved searches as well as in solve count (482 vs 521). The adaptive-specialisation signature (σ < 1) did not appear.

## 5. What the bank looks like

Solve fractions per cell (64 fitted searches per arm per cell, 16 G4) run from 0.19–0.25 (`S>M?F+S:M+m`) to 0.94–0.95 (`M>F?m+m:S+S`, `F>m?M+M:S+S`). The two easy cells are the ones whose branches use repeated reducers; the hard cells need four distinct sums. A8's rank within a cell is not consistent: it leads in 8 cells, trails full F in 6, ties in 2, with no cell interval excluding 1 (per-cell intervals in `result.json`, descriptive).

Solve counts by block: A8 132/130/135/124, S8 112/124/126/120, full F 118/125/122/137 (of 256 each). Block 3 is the only block where full F leads A8; it is also the only block with ρ above 1 (1.18 [0.95, 1.47]). By family: A8 BE 272, PA 249; full F BE 260, PA 242; S8 BE 252, PA 230.

Shortcut programs (training-perfect, wrong on the full domain): rows with at least one shortcut A8 73, S8 76, full F 74, G4 2. Unique shortcut programs A8 0.45 M, S8 0.53 M, full F 1.07 M. These cost evaluations and never count as solved; they cannot inflate any arm.

Median evaluations among solved: A8 69 k, S8 82 k, full F 67 k, G4 157 k. Operator edit rates are flat across fitted arms (edited/eligible children 0.200, 0.200, 0.200).

## 6. Difficulty shift from development to fresh bank

| | then-addition (2033, 16 seeds) | two-sum-v1 (this run, 4 seeds) |
|---|---|---|
| A8 solve fraction | 0.900 | 0.509 |
| full F solve fraction | 0.908 | 0.490 |
| S8 solve fraction | 0.897 | 0.471 |
| G4 solve fraction | 0.633 | 0.199 |
| A8 worker-s per search | 5.76 | 17.0 |
| full F worker-s per search | 4.54 | 17.7 |
| G4 worker-s per search | 8.54 | 22.6 |

The 16-token two-sum targets are far harder for every arm, including the baseline: solve fractions roughly halved for the fitted arms and fell by two thirds for G4. The fitted arms' advantage over G4 grew (2.7× vs about 1.6× implied by 2033's §5 table). So this bank is a fresh test of the same difficulty gap, not one where the fitted bias stops mattering.

Timing-stage means (A8 15.2, S8 17.9, full F 20.9, G4 21.1 worker-s) were close to scoring means (17.0, 18.1, 17.7, 22.6); the ordering of A8 and full F swapped but the projection held with margin (score stage 6 252 s against 7 274 s projected).

## 7. Economics (reported, no rule)

Charged acquisition means in evaluations: A8 6.51 M, S8 10.20 M, full F 61.31 M, G4 0. Mean arithmetic capped search cost on this bank: A8 321 k, S8 342 k, full F 329 k, G4 460 k.

- **A8 vs full F**: A8 is 54.8 M evaluations cheaper at N = 0 and its per-search cost is not resolved from full F's, so no crossover: the paired difference at N = 4 096 is −86 M [−148 M, −21 M]. In calibrated worker-seconds the same holds (−5 447 s [−8 788, −2 015] at N = 4 096). Unlike 2033, where full F was faster per search in worker-seconds and overtook A8 after about 1 360 searches, here full F's per-search time (17.7 s) is not below A8's (17.0 s), so no worker-time crossover is estimated either. The worker-second calibration of historical acquisition is approximate (replay ratios 0.83–0.92).
- **A8 vs S8**: A8 cheaper at every horizon; the interval excludes zero through N = 4 096 in both units (evaluations −86.9 M [−152.8 M, −18.6 M]).
- **A8 vs G4**: A8 repays its acquisition after ≈ 47 fresh searches (worker-s ≈ 52). Full F repays after ≈ 468 (worker-s ≈ 570).

## 8. Resolution price

The corpus log-SD is 0.270, against 0.15 in 2033 and the proposal's assumed 0.20. The observed half-width factor is 1.155 (proposal expected ≈ 1.14 at 4 seeds). The runner's scenario (resolve 1.20 against 1.05 at this SD) needs 20 corpora, 4 more, with about 30 min of extra scoring but new G4 source attempts, A8/S8/full-F acquisitions and full-F references for each (≥ 245 M acquisition evaluations, about 3.8 h lower bound). Resolving the *sign* of ρ (lower bound above or below 1 at a point of 0.945) would need far more: at this SD, roughly 95 corpora. Since the pre-registered question is only whether A8 loses materially (1.20), the sign is not needed for the decision.

## 9. What the data show

- On a bank frozen before any search, chosen on semantic grounds, with 16-token targets that none of the arms had seen, the frozen cheap acquisition A8 (6.5 M evaluations) costs within [0.82, 1.09]× of the frozen full 48-attempt acquisition (61.3 M evaluations) per capped search. A material loss (≥ 1.20) is excluded; a loss of any size is not excluded (upper bound 1.09); a gain is not excluded either.
- All three fitted arms are useful on the fresh bank: 2.3–2.7× cheaper than G4 with intervals well above 1, and solving about half of searches where G4 solves a fifth.
- S8 (static eight attempts) is again resolved slower than A8 (σ 1.17 [1.04, 1.33]), replicating 2033's direction on new targets. No sign of adaptive lock-in.
- The acquisition-plus-search curves put A8 below S8 and full F at every horizon to N = 4 096, with intervals excluding zero.

## 10. What the data do not show

- **Not equivalence.** ρ's interval spans 0.82–1.09; A8 could be 9 % slower or 18 % faster. "Retains useful performance" means a 1.20 loss is excluded and usefulness against G4 holds, nothing finer.
- **Not general transfer.** One fresh shape, one domain (D1331), 16 cells from 76 eligible, 4 seeds. All intervals are conditional on the selected roster. The ≤9-token screen does not exclude 10–15-token solutions to these 16-token targets (bank `minimality` field); the per-cell solve ranking suggests reducer repetition makes some cells much easier, which is a property of the bank, not of the arms.
- **Nothing about mechanism.** Decoder versus library, yield versus content, and why PA4 (and to a lesser extent PA3, BE3) favour full F are all unaddressed, as in 2033.
- **Historical worker-second acquisition costs** are replay-calibrated, not remeasured; the evaluation-unit curves are the firmer ones.
- The 4-seed roster is the fallback design; the 8-seed design would have roughly halved the within-corpus noise but the limiting noise is between corpora (SD 0.27), as the proposal anticipated.

## Against the predictions

Plan labels (fixed before running): ρ UB < 1.20 with G4/A8 LB > 1 and full-F solve guard met → **useful retention on this fresh target roster**; ρ LB > 1.20 → material relative loss; LB > 1 and UB ≥ 1.20 → resolved loss of unresolved materiality; UB < 1.20 with failed usefulness → bounded retention and failed usefulness as separate findings; interval spanning retention and material loss → unresolved. Observed ρ = 0.945 [0.819, 1.092], G4/A8 = 2.73 [2.36, 3.17], full-F solve fraction 0.490 (502/1 024 ≥ 256): all three conditions of the first label hold, so the data match **useful retention**. The plan's own caveat applies: this label says a 1.20 loss is excluded and A8 is useful against G4, on this one roster; it does not say A8 equals full F, and it is not evidence of general transfer, inherited adaptation or addition-in-predicate transfer (the shape the strategy originally asked for was never tested, see the question log).

- **Proposal expected ρ ≈ 1.0–1.1 and gave "retains" about a 60 % chance.** Observed 0.945, inside the expected band on the favourable side; retention happened. The proposal's "surprise" ρ > 1.2 did not occur, and the interval excludes it.
- **Expected G4 to solve 35–50 % and A8/full F 70–85 %.** Both too high: G4 0.199 (51/256), A8 0.509, full F 0.490, S8 0.471. The bank is harder than forecast for every arm, roughly halving fitted solve rates from then-addition's 0.90. The proposal's plausible "2–3× harder on 16-token targets" was right about search time (17–23 worker-s per search against 4.5–8.5 on then-addition), and the stage-0 rule did its job by dropping to 4 seeds.
- **Expected fitted arms to beat G4 2–3×.** Observed 2.33–2.73× with intervals above 2: correct, and larger than the gap on the development bank.
- **Surprise "σ < 1" (adaptive specialisation) did not occur.** σ = 1.173 [1.036, 1.327], resolved above 1 under both cap penalties, 12/16 corpora, reproducing 2033's direction (1.126) on fresh targets. Whatever bias the adaptive half of A8's attempts introduced, it did not narrow A8 relative to the static S8 on this shape.
- **Surprise "fitted arms no better than G4" did not occur.**
- **Precision.** The proposal assumed corpus log-SD 0.20 (half-width factor ≈ 1.14 at 4 seeds); observed 0.270 and 1.155. Slightly worse than assumed, but the decision rule only needed the 1.20 bound, which the interval cleared with margin (1.092). A true ρ ≤ 1.05 resolving against 1.20 was the stated aim; it did. The proposal's expectation that "between-corpus noise is the limit" holds: the resolution price in §8 is in corpora, not seeds.
- **Stage 0.** Followed as written: 8 seeds rejected (projection 13 902 s × 1.15 > 150 min), 4 seeds with all arms admitted (7 274 s), actual score stage 6 252 s. The plan's statement that forecasts of solve rate never enter admission was respected; no efficacy selection happened.
- **Critique notes 7–10** (digest wording) were deferred to the steward in the plan; nothing in this run bears on them except that the "no lock-in" wording now has one fresh-bank data point in its favour (σ > 1 on two-sum-v1), which still falls short of "absence of specialisation" in general.
