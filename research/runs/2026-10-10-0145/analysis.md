---
outcome: useful_replication
---
# Analysis — 2026-10-10-0145 A8 rebuilt from the complementary source roster, scored on two-sum-v1

Code: commit `b6d1974` on `research/2026-10-10-0145`. Queue runner exit 0, both entries done.
Outputs: [prepare](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-0145-source-replication-prepare), [score](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-10/2026-10-10-0145-source-replication-score). Plot in this folder: `build_contrasts.png` (per-build δ forest with the four block contrasts; per-cell solve fractions for A8′, historical A8 and G4). The runner's `diagnostics.png` and `cost_curves.png` are in the score folder.

Every number below was recomputed from `search.jsonl`, `first.jsonl`, `continuation.jsonl` and 2303's `search.jsonl` with an independent script; all match `result.json` to the printed precision (u, its interval, δ, per-family u, solve counts, per-cell counts, acquisition totals).

## 1. Data completeness

| check | result |
|---|---|
| prepare stage | done, 755 s wall (limit 2 400, internal 2 280). `validation.passed = true`: legacy 2033 `BE1|0|A8` table and library hashes reproduced under the old default roster, 2 048 empty-fallback edits identical F/W, 10 000 suffix-edit audit passed, 2 historical G4 rows replayed with identical solved/evaluations |
| source collection | `first.jsonl` 256 rows (16 builds × 4 cells × 4 attempts, all G4); `continuation.jsonl` 512 rows (256 adaptive under each build's own C4+F4, 256 static G4). 768 unique collection seeds; per build exactly 16/16/16. No empty source cells in any of the 32 artifacts; library size 32 in all |
| artifacts | 32 builds (16 A8′ + 16 S8′), one table hash per build; every A8′ row in scoring carries its build's single hash, so each new build is one artifact used for all four ordinals |
| admission | timing 32/32 searches (4 builds × 2 arms × 4 disjoint timing cells), 92.9 s wall. Both-arm candidate projected 6 841 s, 7 188 s with reserves, above the 7 080 s ceiling → **rejected**; A8′-only candidate 3 540 s / 3 887 s → **admitted**. Pre-registered fallback order followed; solve rates not consulted (`timing_only = true`) |
| score stage | done, 1 892 s wall (limit 7 200). Score-stage `validation.passed`: 32/32 timing rows replayed with identical scientific fields. `progress.json` 1 024/1 024, phase `two_sum` |
| rows in `search.jsonl` | **1 024** = 16 A8′ builds × 16 cells × 4 ordinals. Every build has 64 rows; every cell 64; ordinals 0–3 each 256. 0 duplicates on (corpus, cell, ordinal) and on (arm, cell, seed) |
| pairing to history | all 1 024 rows match a 2303 A8 row on (corpus, cell, seed) with identical 64 training indices, and the historical block equals the new ordinal in 1 024/1 024. `historical_pairing.json` lists the 1 024 mappings with both artifact hashes |
| G4 baseline | 256 rows reused from 2303 (`historical_provenance.json` pins the file by SHA-256); 16 per cell; 51 solved, as in 2303 |
| cap / pop | all rows cap 524 288, pop 256; 0 rows over cap; every unsolved row (535) stopped exactly at cap; no solved row at cap |
| errors | 0 rows with an error field; `stderr.log` empty in both stages |

Nothing is missing, duplicated or failed. **S8′ was built (16 artifacts, 256 static attempts paid for) but never scored**, so σ′ = S8′/A8′ is absent and the adaptive-versus-static diagnostic is lost. See §7 for why: the drop was the approved fallback, but the projection that triggered it was biased, not a real cost obstacle.

Scope reminder: both rosters are development data (the comparison-gate cells), the target bank two-sum-v1 is the 2303 development bank, external fitting, D1331.

## 2. Primary comparison: u = cost(G4) / cost(A8′) on two-sum-v1

Estimator as pre-registered (2303's): log capped evaluations, unsolved = 2 × cap, per-build mean over 64 (cell, ordinal) rows, builds resampled within family (8 BE, 8 PA), one shared G4 baseline per draw with seeds resampled within each fixed cell, 8 192 draws.

| | u | 95 % | n |
|---|---|---|---|
| **primary** | **2.50** | **[2.17, 2.85]** | 16 builds, 1 024 rows vs 256 G4 |
| cap penalty 1× | 2.06 | [1.84, 2.28] | 16 |
| BE builds | 3.14 | [2.61, 3.71] | 8 |
| PA builds | 1.99 | [1.66, 2.32] | 8 |
| historical A8 (2303, same estimator, same G4 rows) | 2.73 | [2.36, 3.17] | 16 corpora of 4 blocks |

**Decision rule.** Lower bound 2.17 > 1.5, under both cap penalties and in each family separately. The pre-registered label for LB > 1.5 is **useful replication**: the unchanged recipe, fed fresh G4 searches on the four other cells per family, produces a frozen bias that resolves two-sum targets about 2.5× cheaper than G4, with the interval well clear of the margin.

Between-build spread: build log-SD 0.229 (BE) and 0.220 (PA), below the proposal's feared 0.35 and close to 2303's 0.27 for four-block corpus means. Builds' geometric capped costs run from 171 k (BE6) to 552 k (PA1); G4's is 702 k. 16 of 16 builds have a geometric cost below G4's, the worst (PA1) by a factor of 1.27.

## 3. Solve counts

| arm | solved / n | fraction | geometric capped cost |
|---|---|---|---|
| A8′ (this run) | 489 / 1 024 | 0.478 | 281 k |
| historical A8 (2303) | 521 / 1 024 | 0.509 | 257 k |
| G4 (2303 rows) | 51 / 256 | 0.199 | 702 k |

By family: A8′ BE 272/512, PA 217/512; historical A8 BE 272/512, PA 249/512. The whole 32-solve deficit against historical A8 is in the PA family.

Per build (of 64): BE 28–39, PA 18–39; PA1 (18) and PA6 (24), PA7 (25) are the three weakest; see §4. Per ordinal: 126/122/128/113 of 256, flat.

Row-level pairing on identical keys against historical A8: A8′ cheaper in 337 rows, historical cheaper in 378, tie 309 (nearly all both-unsolved at cap). Joint solves: both 295, A8′ only 194, historical only 226, neither 309.

Shortcut programs (training-perfect, wrong on the full domain): 56 of 1 024 A8′ rows had at least one, 3.75 M unique shortcut programs across the run. These are never counted as solved; they cannot inflate u.

## 4. δ = cost(A8′) / cost(historical A8), paired by key (reported, no rule)

16 corpus contrasts (new single build vs the four historical block artifacts on identical keys), t interval on 15 df.

| | δ | 95 % | n |
|---|---|---|---|
| primary estimator | **1.093** | **[0.905, 1.321]** | 16 |
| cap penalty 1× | 1.070 | [0.917, 1.248] | 16 |
| both solved only | 1.169 | [0.969, 1.410] | 16 (295 pairs) |
| BE | 0.959 | [0.803, 1.145] | 8 (7 df) |
| PA | 1.247 | [0.870, 1.789] | 8 (7 df) |

Observed contrast log-SD 0.355 (proposal assumed 0.40); half-width factor 1.21 (proposal expected ≈ 1.25). The interval spans 1: the new builds are not resolved as either worse or better than the historical artifacts on these targets. The point sits 9 % costlier, and the three estimators agree on the direction.

Per build (plot, left): 9 of 16 have δ above 1. Three PA builds are clearly worse than their historical counterpart: PA1 δ 1.93, PA6 1.86, PA7 2.27, each with all four block contrasts above 1. No BE build has a per-build interval excluding 1 in either direction; BE2 and BE5 are the best (0.74). Per-family δ differs (BE 0.96 vs PA 1.25) but the PA interval is wide (log-SD 0.43 against BE's 0.21) and includes 1.

**Caveat on δ's pairing.** Pairing on identical target keys removes target-search randomness only. The historical side is four block-specific artifacts built from the original roster; the new side is one artifact built from the complementary roster. A δ above 1 would mix source-roster effect with single-build-versus-four-build averaging; the design cannot separate them. Nor can this run say whether the weak PA builds reflect the PA complementary cells, bad luck in 16 first-batch attempts, or the adaptive step, because S8′ was not scored.

## 5. What the sources looked like

| phase | solved / n | fraction | mean worker-s | mean evaluations |
|---|---|---|---|---|
| first batch, G4, 4 per cell | 193 / 256 | 0.754 | 11.3 | 251 k |
| adaptive, F under own C4+F4, 4 per cell | 255 / 256 | 0.996 | 1.5 | 31 k |
| static, G4, 4 more per cell (S8′ only) | 200 / 256 | 0.781 | 10.6 | 232 k |

Per complementary cell, first-batch G4 solves range 20/32 to 27/32 (BE) and 23/32 to 26/32 (PA); the audit's historical rate for these cells was 196/256 (0.766). The adaptive step solved 255/256 against 2033's 92.5 % on the original roster, at about one eighth of a G4 attempt's cost. A8′ library yield (solved windows of 32 attempts) ranges 26–31 per build; first-batch yield does not predict build cost (correlation with log cost 0.13 over 16 builds). PA1, the weakest build on targets, had an above-median first-batch yield (13/16). Weak builds are not explained by thin sources.

Mean A8′ acquisition: 4.51 M evaluations [4.18 M, 4.84 M] per build (range 3.42–5.81 M), below historical A8's 6.51 M because both the first batch (75 % vs 68 %) and the adaptive step (99.6 % vs 92.5 %) solved more often and so hit the cap less. Source worker time 205 s per build.

## 6. Economics (reported, no rule)

Arithmetic capped costs on the bank: A8′ 333 k evaluations per search (17.3 worker-s), G4 460 k (22.6 worker-s as measured in 2303).

- **Evaluations.** A8′ repays its 4.51 M acquisition against G4 after **35 searches [30, 43]**, never-repay fraction 0 of 8 192 draws. Historical A8 repaid after about 47 (2303 §7). At N = 4 096 the A8′ curve is 1.37 G vs G4's 1.88 G.
- **Worker-seconds.** The runner reports **no repayment at any horizon** (never-repay fraction 1.0). This verdict rests on a G4 time calibration of 0.558 from two 2303 G4 rows replayed during prepare, which makes historical G4 appear 1.8× faster on this machine than in 2303 (12.6 vs 22.6 worker-s per search). The evaluation throughputs say otherwise: A8′ in this run ran at 19.2 k evaluations per worker-second, 2303's A8 at 18.9 k and 2303's G4 at 20.4 k, so the two scoring runs were equally fast under the ten-worker load. The two replay rows evidently ran without contention. With the calibration set to 1 the worker-second break-even would track the evaluation one (A8′ 17.3 vs G4 22.6 worker-s per search, acquisition 205 s). **Treat the worker-second economics in `result.json` as an artifact of the calibration; the evaluation-unit curves are the firm ones.** The code review had already labelled the calibration approximate; this run shows it was wrong in direction as well as size.

## 7. Admission and the loss of S8′

The timing stage ran 32 searches on 10 workers: 564 s of job time in 92.9 s wall, 6.07 effective workers. The scoring stage then ran 1 024 searches at 17 740 s of job time in under 1 892 s wall, at least 9.4 effective workers. The timing batch's low utilisation (3.2 rounds of 10 jobs with a 60 s maximum job) biased the both-arm projection to 7 188 s with reserves against the 7 080 s ceiling; at the throughput the score stage achieved, both arms would have taken about 4 800 s with reserves and the actual stage used 26 % of its timeout. The code review flagged this bias as non-blocking because the fallback was approved. The fallback kept the primary comparison intact, but the drop was caused by the admission estimator, not by a cost obstacle, and it cost the one diagnostic (σ′) that could have placed the PA deficit on the adaptive step or on the sources. Any rerun of this admission pattern should time at least 64 searches or estimate effective workers from the prepare stage's own collection batches (768 jobs).

The resolution-price scenario reports 16 builds sufficient at the observed effect (within-family log variance 0.050, shared G4 log variance 0.002); the usefulness decision needed no top-up.

## 8. What the data show

- The unchanged A8 recipe, rebuilt 16 times from fresh G4 searches on the four complementary comparison-gate cells per family, with new seeds disjoint from all prior collection, yields frozen artifacts that resolve two-sum-v1 targets 2.50× [2.17, 2.85] cheaper than G4. The margin of 1.5 is cleared in both families separately (BE 3.14, PA 1.99) and under a 1× cap penalty (2.06 [1.84, 2.28]). 16 of 16 builds beat G4's geometric cost.
- The complementary-roster builds cost 1.09× [0.90, 1.32] the historical A8 artifacts on identical keys: not resolved as different. The 2303 figure of 2.73× therefore did not depend on favourable sources in the sense the question asked.
- Fresh acquisition on this roster was cheaper than the historical one (4.5 M vs 6.5 M evaluations per build) because both source phases solved more often; the adaptive step solved 255/256.
- Against G4 in evaluations, a fresh A8′ repays after about 35 searches.

## 9. What the data do not show

- **Not source-set robustness in general.** One alternative roster, inside the same two families and the same development bank from which the targets were drawn. Both rosters were in play when the recipe was developed.
- **Not equality with historical A8.** δ's interval allows 10 % cheaper to 32 % costlier; three PA builds (PA1, PA6, PA7) are about twice as costly as their historical counterparts, and the PA family's u (1.99) is below the BE family's (3.14) and below historical PA (2.48). Whether that is the PA complementary cells, single-build noise, or the adaptive step cannot be told: S8′ was not scored and the pairing does not share source ancestry.
- **Nothing on mechanism.** Decoder versus library, yield versus content, remain bundled; yield does not predict build cost here, which argues weakly against a thin-source explanation for the weak PA builds.
- **Worker-second repayment is not established either way**; the runner's "never repays" is a calibration artifact (§6).
- **No new-family, fresh-bank or inherited-evolution claim.** This is a replication across source sets on development data.

## Against the predictions

Plan labels (fixed before running): LB(u) > 1.5 → useful replication on this complementary development roster; UB(u) < 1.5 → misses the usefulness bar, with δ supplying the evidence on deterioration; interval spanning 1.5 → unresolved with a resolution price; a timing stop → no confirmation evidence. Observed u = 2.50 [2.17, 2.85], so the data match **useful replication**. The plan's own qualification applies: carry the recipe toward a later genuinely new family, as a replication within two development families, not a general source-robustness claim.

- **Proposal expected u ≈ 2.2–2.8 with LB above 1.5 (about 80 %).** Observed 2.50 [2.17, 2.85]: inside the expected band, lower bound clear of the margin under both cap penalties and in each family. The surprise "u UB < 1.5" did not occur.
- **Expected δ ≈ 0.9–1.2.** Observed 1.09 [0.90, 1.32]: point inside the band, interval slightly wider on the costly side. The surprise "δ LB > 1.25" did not occur (LB 0.90). The plan's half-width scenario of 1.25 at log-SD 0.40 came out at 1.21 with log-SD 0.355.
- **Expected σ′ > 1.** Not measured: S8′ was dropped by the timing admission. The plan said this would forfeit the diagnostic and keep the 16 builds; both happened. The plan did not anticipate that the admission projection itself would be biased by a 32-job timing batch (6.07 effective workers measured, 9.4 achieved), so the fallback fired without a real cost obstacle (§7). The code review had noted the risk as minor.
- **Surprise "a PA/BE split where one family's sources fail."** Partly observed, not resolved. PA u 1.99 [1.66, 2.32] against BE 3.14 [2.61, 3.71]; PA solves 217/512 against historical PA 249/512, BE unchanged at 272/512; three PA builds about twice as costly as their historical counterparts. PA sources did not "fail" (PA u still clears 1.5 with margin), and PA δ 1.25 [0.87, 1.79] does not resolve a loss. Without S8′ the deficit cannot be placed on the adaptive step or on the complementary PA cells.
- **Expected first-batch yield similar or higher than the original roster (68 %).** Observed 193/256 (75 %), matching the audit's 77 % for these cells. The plan's adaptive assumption of about 237/256 (92.5 %) was exceeded: 255/256. Acquisition came out at 4.5 M evaluations per build against the expected ~6.5 M.
- **Precision scenario.** The plan feared single-build log-SD up to 0.35; observed 0.23 in each family, so the interval (half-width factor 1.15) was tighter than the 1.23 scenario, and a true u near 1.8 would have resolved rather than remained unresolved.
- **Feasibility.** Prepare 755 s against a 2 400 s limit (plan expected 15–20 min); score 1 892 s against 7 200 s. Collection cost of 7.4 k worker-s was predicted; the measured total for all 768 attempts was 6.0 k worker-s. Expected queue wall of 125 min came out at 44 min, mostly because the secondary arm was not scored.
- **Economics.** The plan required reporting break-even including never-repay draws; evaluations give 35 [30, 43] searches, no never-repay draws. The worker-second curve's "never repays" is a calibration artifact (§6) and should not be carried into the digest.
- **Critique notes 7–8** (digest and question-log wording) remain for the steward; nothing here changes them.
