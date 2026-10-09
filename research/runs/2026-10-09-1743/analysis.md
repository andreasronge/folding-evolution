---
outcome: tight_loss
---
# Analysis — 1743 four-attempt sources for the complete C+F pipeline on then-addition

Reviewer: independent re-analysis from the raw rows (`search.jsonl` of this run and of 1036), not from `result.json`. Every number below was recomputed; where the runner's `result.json` reports the same quantity the two agree to three decimals. Code at commit `652fde5` (clean tree), review verdict pass.

Outputs: [prepare](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1743-small-source-prepare), [score](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-09/2026-10-09-1743-small-source-score). Plot in this folder: `retention_per_acquisition.png` (data in `per_acquisition.json`).

## 1. Data completeness

Both queue entries finished with exit 0, empty stderr, within timeout (prepare 131 s of 1800; score 6243 s of 10800). Admission froze **16 seeds** (projection 6843 s with margin; actual scoring wall 6243 s).

| check | result |
|---|---|
| prepare validation | passed: 16/16 full-C hashes reproduced, all-empty source recovers G4, 10 000 F and 10 000 W suffix-edit audits passed, 2 048 forced empty-library edits identical for F and W, bit-exact replay of 16 F + 16 W rows (1036) and 2 G4 rows (1548) |
| score validation | passed: 128/128 preparation-smoke rows replayed bit-exactly before scoring |
| scoring rows | 8 192 = 2 arms × 16 corpora × 16 cells × 16 seeds; 0 duplicates; 128 smoke rows kept separate under `phase: smoke` |
| blocks | every (corpus, cell, arm) has exactly 4 seeds in each of blocks 0–3 (2 048 groups × 4) |
| new-arm pairing | all 4 096 (corpus, cell, seed) F/W pairs share `initial_tokens_hash` and training cases (0 mismatches) |
| references | 4 096 each of full F, W, C from 1036 then-addition present for every key; same training cases (0 mismatches), different initial programs in all 4 096 (as designed) |
| cap / pop | all rows cap 524 288, pop 256 |
| sources | 1 024 of 3 072 1246 attempts selected (4 blocks × 4 attempts × 256 cells), 615 solvers; 64 acquisitions built, 0 library fallbacks; 51 acquisitions with no empty source cell, 12 with one, 1 with two; F4 library sizes 4–32 (12 at the cap of 32, 4 with ≤ 8 fragments) |

Nothing is missing, nothing was resampled, and no fallback to 12 seeds was used. The roster is complete so the efficacy rule may be applied.

## 2. Primary comparison

ρ = cost(full F) / cost(C4+F4), log cost averaged over cells and seeds, then equal weight over the 4 source blocks, then over corpora; unsolved = 2 × cap; 95 % t interval on 15 df. Threshold 0.833.

| | ρ | 95 % | n |
|---|---|---|---|
| **primary** | **0.679** | **[0.614, 0.752]** | 16 corpora |
| 1 × cap penalty | 0.703 | [0.641, 0.771] | 16 |
| both-solved only | 0.767 | [0.707, 0.832] | 16 |
| BE corpora | 0.697 | [0.588, 0.827] | 8 |
| PA corpora | 0.662 | [0.567, 0.773] | 8 |
| block 0 (audited prefix) | 0.662 | [0.511, 0.858] | 16 |
| block 1 | 0.746 | [0.611, 0.912] | 16 |
| block 2 | 0.671 | [0.555, 0.811] | 16 |
| block 3 | 0.643 | [0.511, 0.808] | 16 |

The upper bound 0.752 is below 0.833: **tight loss**. In plain terms the four-attempt pipeline needs about 1.47× the search of the full pipeline (interval 1.33×–1.63×). All 16 corpus means are below 1 and 13/16 are below 0.833 (per-corpus ρ from 0.531 to 0.944). The loss survives dropping the failure penalty, restricting to both-solved pairs (upper bound 0.832, just inside), both task families, and each source block separately. Block 0, the only block the steward's probe inspected, is not special.

Solve counts (all /4 096): C4+F4 **3 519** (85.9 %), C4+W4 3 533 (86.3 %), full F 3 719 (90.8 %), full W 3 643 (88.9 %), full C 3 566 (87.1 %). Per-corpus solve-rate difference C4+F4 − full F: −4.9 points, 95 % [−6.5, −3.3]. Median evaluations among solved: C4+F4 41 728 vs full F 32 256.

## 3. Secondary comparisons (no decision rule)

Cost ratios, same estimator (>1 means the numerator costs more):

| contrast | ratio | 95 % |
|---|---|---|
| C4+W4 / C4+F4 (F4's increment over chain blocks) | 1.119 | [1.030, 1.216] |
| full W / full F from 1036 (same estimator, for reference) | 1.195 | [1.111, 1.286] |
| C4+W4 / full W | 1.378 | [1.298, 1.463] |
| full C / C4+F4 | 0.996 | [0.919, 1.080] |
| full C / C4+W4 | 0.890 | [0.837, 0.947] |
| full W / C4+F4 | 0.812 | [0.750, 0.879] |
| full F / C4+W4 | 0.607 | [0.577, 0.639] |

What these show:
- **F4 still beats W4**, resolved above 1 but **unresolved against 1.10** (interval covers it). The library increment on a cheap decoder (1.12) is in the same range as on the full decoder (1.20); the intervals overlap heavily.
- **C4+F4 costs the same as full C alone** (0.996 [0.92, 1.08]): the cheap complete pipeline recovers roughly the full decoder's level, no more. Equivalently, the gap to full F (ρ = 0.68) is about the size of F's whole advantage over C in 1036 (full F / full C recomputed here: 0.68).
- **C4+W4 is worse than full C** (0.89 [0.84, 0.95]): the four-attempt decoder with chain blocks does not reach the full decoder with its own blocks.
- Per block, C4+F4 solved 881/897/874/867 of 1 024 and C4+W4 878/877/890/888; geometric costs 71k/62k/65k/73k vs 76k/75k/75k/76k. F4's advantage over W4 is present in every block.

Against G4 (unpaired; 1548 reference, 162/256 solved, geometric cost 263k): C4+F4 geometric cost ratio 0.257 [0.212, 0.313]. The cheap pipeline is still about 4× cheaper than the untrained decoder per capped search.

## 4. Economics (A + N·S, one acquisition per deployed method)

| units | method | A (acquisition) | S (per capped search) | solve prob. |
|---|---|---|---|---|
| evaluations | C4+F4 | 4.97 M | 148.9 k | 0.859 |
| evaluations | C4+W4 | 4.97 M | 152.5 k | 0.863 |
| evaluations | full F | 61.3 M | 112.0 k | 0.908 |
| evaluations | G4 | 0 | 306.6 k | 0.633 |
| worker-s (qualified) | C4+F4 | 155 | 7.44 | |
| worker-s (qualified) | full F | 1 914 | 5.18 | |
| worker-s (qualified) | G4 | 0 | 8.61 | |

Acquisition is 8.1 % of the full corpus in evaluations (the proposal's "about 8 %"), but each capped search costs 33 % more on average. Corpus-bootstrap crossovers (4 096 replicates, seed 1743):
- **C4+F4 vs full F**: cheaper initially, loses after N ≈ **1 530** fresh searches [1 247, 2 016] in evaluations; after N ≈ 781 [666, 953] in qualified worker-seconds. Crossover direction "cheap loses" in 100 % of replicates.
- **C4+F4 vs G4**: wins after N ≈ **31** searches [27, 38] in evaluations; N ≈ 131 [75, 450] in worker-seconds.
- C4+W4 behaves the same (crossover 1 392 vs full F; 32 vs G4).

So the four-attempt pipeline is the cheaper deployment for fewer than about a thousand fresh searches of this kind, and the full pipeline beyond that; both repay against G4 within tens of searches. Worker-second curves use selected same-hardware replay calibration (F 0.91, W 0.81, G4 0.64 from 2 rows) and are indicative only; evaluation curves exclude fit/extraction, which is ~0.2 s per acquisition and immaterial. These curves use arithmetic capped effort and 16 development corpora on development tasks; they are not a transfer claim.

## 5. Per-acquisition variation (exploratory, post hoc)

The 64 individual acquisitions range from ρ = 0.21 to 1.34; 14/64 are at or above 1, 22/64 above 0.833 (left panel of `retention_per_acquisition.png`). Retention correlates with acquisition quality: Spearman 0.36 (p = 0.004) with F4 library size and −0.35 (p = 0.005) with the number of empty source cells. The 13 acquisitions with at least one empty cell average ρ = 0.52 (0.27 for the one with two); the 51 with none average 0.735. The four libraries with ≤ 8 fragments average 0.39. But the 12 acquisitions whose library reached the 32-fragment cap still average 0.77, so a full-size library from four attempts does not recover the full pipeline either. Source solver count per acquisition (4–14 of 16 attempts, median 10) is only weakly related (0.19, p = 0.13). These are 64 observations with shared corpora, offered as a lead, not a result.

## 6. Integrity checks

- Shortcut solutions: rows with any shortcut 300/4 096 (C4+F4), 260 (C4+W4), 341 (full F), 293 (full W), 312 (full C). No arm is enriched; the loss is not a shortcut artefact.
- Edit diagnostics (runner's `diagnostics.png`): F4 and W4 edit about 20 % of eligible children, realised changed-token spans peak at 3 for both, mean realised edits per attempted block 2.87 vs 2.97. The operators behaved as in 1036.
- The fitness and diversity panels show no divergence between the new arms.
- Timing: C4+F4 mean 7.4 worker-s per search vs 6.4 in the smoke; within the admission margin.

## 7. What the data does and does not show

Shows:
- Rebuilding decoder and library from four capped G4 attempts per training cell (failures charged) **does not retain** the full pipeline's search efficiency on then-addition: 1.47× the cost, interval excludes the 20 % tolerance under every sensitivity. This closes the four-attempt policy as a retention target.
- The cheap pipeline lands at the level of the full decoder alone and remains far better than G4; its acquisition is 12× cheaper. Whether it is the better deployment depends on the reuse horizon (break-even against full F around 10³ searches).
- The library's increment over chain blocks persists on the cheap decoder (1.12 [1.03, 1.22]), unresolved against 1.10.

Does not show:
- Whether the loss is in the decoder, the library, or both: there is no bare-C4 arm, and W4 carries F4's length law (critique note 4). The C4+W4 < full C contrast suggests the decoder itself is weaker, but full C uses its own chain law, so this is not a clean decoder comparison.
- Where between 4 and 48 attempts retention is reached; only one source size was tested. The per-acquisition correlation with empty cells and library size suggests the loss shrinks with better-filled sources, but that is post hoc.
- Anything about fresh-bank transfer, inherited adaptation, or uncapped time-to-solve. Development sources and tasks, external fitting throughout.
- Individual-acquisition reliability: aggregate ρ is an average over 4 replicate builds per corpus; single builds vary from 0.21 to 1.34.

## Against the predictions

Plan labels: lower bound > 0.833 **retained**; upper bound < 0.833 **tight loss**; otherwise unresolved. Measured ρ = 0.679, 95 % [0.614, 0.752]: the upper bound is below 0.833, so the data match **tight loss**. The plan's interpretation of that label ("sparse acquisition misses useful bias") is consistent with the per-acquisition lead in §5 but is not established by this design.

- **Expected ρ ≈ 0.95 [0.85, 1.06]** (proposal). Observed 0.68 [0.61, 0.75]; the whole interval lies below the expected interval. The proposal named ρ < 0.7 as a surprise; the point estimate is 0.68 and the interval reaches 0.61, so this is the surprising direction. The steward's probe (64 unpaired searches, C4+F4 geometric cost 42k against full F's 46k) over-estimated retention; the paired full roster gives C4+F4 67.5k vs full F 45.9k.
- **Expected half-width ×1.08–1.15.** Observed ×1.107 (0.752/0.679), inside the projection. The interval was narrow enough to resolve; the resolution price in `result.json` is moot.
- **Expected F4/W4 ≥ 1.2.** Observed 1.12 [1.03, 1.22]: resolved above 1 but below the expected 1.2 as a point estimate, and unresolved against the 1.10 worthwhile-gain threshold. The plan's secondary reading "if W4 retains and F4 adds less than 1.10, acquiring C alone is favoured" does not apply: W4 did not retain (C4+W4 / full W = 1.38 [1.30, 1.46]).
- **Cheap W vs full W, cheap F vs G4** were descriptive only. Both are reported in §3; C4+F4 is 0.26 [0.21, 0.31] of G4's geometric cost.
- **Economics.** The plan required A + N·S curves with both crossover directions. The cheap pipeline is the "smaller A, larger S" case the plan anticipated: cheaper up to about 1 500 fresh searches in evaluations (780 in qualified worker-seconds), then losing; it repays against G4 after about 30 searches. The plan's caution that a retention loss "need not imply no economically useful horizon" is borne out.
- **Sensitivities.** Cap-1, both-solved, BE, PA and each block individually all keep the upper bound at or below 0.91, and none reaches the retained rule. The plan's warning that block variability limits single-acquisition claims applies in the other direction too: 14 of 64 individual acquisitions showed ρ ≥ 1, so a single cheap acquisition can occasionally match the full pipeline, but on average it does not.
- **Scope held.** Development sources and tasks, external fitting, no bare-C4 arm; nothing here attributes the loss to decoder versus library, and nothing supports a transfer or inherited-adaptation claim. Every outcome returns to strategy, as the plan states.
