---
outcome: 3
---

# Analysis — 2026-10-07-0821 rank-one context vs token continuation

Reviewer: independent recomputation from the raw run outputs
(`experiments/output/2026-10-07/2026-10-07-0821-rank-one-continuation/`, commit `f61aec4`).
Script and log: [analysis_files/recompute.py](analysis_files/recompute.py),
[analysis_files/recompute.log](analysis_files/recompute.log). Figure:
[analysis_files/contrasts.png](analysis_files/contrasts.png). All numbers below were recomputed
from `search.jsonl`, `fresh_scores.json`, `generations.jsonl`, `trajectories.json` and
`calibration_units.json`; they match `report.json` to the printed precision.

## 1. Data completeness

Complete. Every arm, start and seed is present, nothing is duplicated, and no search failed.

| Check | Result |
|---|---|
| Queue runner exit | 0; `status.json` state `complete`; wall 9 519 s (2.64 h of the 3.8 h internal deadline) |
| Rows in `search.jsonl` | 174 964 = 29 184 calibration + 122 880 learn + 6 400 selection + 16 500 fresh; 0 duplicate (arm, cell, seed) keys |
| Caps | calibration/learn/selection all at 65 536; fresh all at 524 288 |
| Pairs admitted | 16/16 (BE1–8, PA1–8), alternating, no refusal; family counts 8 + 8 |
| Trajectories | 32; every one has exactly 3 840 learn + 200 final-selection searches = 4 040; 20 generations each |
| T/C pairing | in every pair and generation T and C used identical (seed, cell) sets; generation-0 parent scores are identical across arms in all 16 pairs (both arms start from the same table) |
| Fresh rows | 16 500 expected = 16 500 observed, 0 missing, 0 extra; every row's table hash matches `fresh_maps.json`; no two fresh maps share a hash |
| Calibration | 12 units × 24 mutants; 96 rows per mutant (2 blocks × 48), 384 per parent block; 4 parent-block pairs |
| Validation | `validation.json` passed; bank SHA, 1723 source SHAs and G4 hash pinned; only the ten training cells appear; no holdout anywhere |
| Solve fractions | 65k: 0.937 calibration, 0.952 learn, 0.957 selection; 524k fresh: 0.988 (194/16 500 unsolved, spread evenly over S/T/C/C0: 47/44/40/49) |

Seed namespaces are disjoint by construction (calibration ≤ 1 821 372 548, learning ≥ 1 822 000 000,
selection ≥ 1 823 000 000, fresh 1 824 000 000–049); I checked the ranges, not every value.

Runtime was well inside the budget: Stage A 27 min, 16 pairs 107 min (mean 403 s, max 455 s per pair),
fresh scoring 24 min. About 70 min of the 3.8 h deadline went unused, so the continuation could have
been roughly 40 % deeper, or the pairs more numerous, at the same timeout.

## 2. Key numbers

Metric: improvement X/Y = mean over own training cells × 50 shared fresh seeds of
log2(cost_Y) − log2(cost_X), unsolved = 2 × cap. Positive log2 means X is cheaper. Family-balanced
mean over 8 BE + 8 PA pairs, t interval on 14 df. Per-family intervals are descriptive (7 df).

| Contrast | Ratio [95 %] | log2 mean ± half-width | BE (8) | PA (8) | pair sd (log2) | pairs > 0 | Wilcoxon p |
|---|---|---|---|---|---|---|---|
| **C/T** (primary) | **0.955 [0.833, 1.095]** | −0.067 ± 0.197 | 1.052 [0.839, 1.320] | 0.866 [0.710, 1.058] | 0.384 | 7/16 | 0.46 |
| T/S | 1.026 [0.904, 1.165] | +0.038 ± 0.182 | 1.010 [0.856, 1.191] | 1.043 [0.833, 1.307] | 0.330 | 7/16 | 0.86 |
| C/S | 0.980 [0.900, 1.067] | −0.029 ± 0.123 | 1.062 [0.944, 1.195] | 0.904 [0.781, 1.046] | 0.252 | 6/16 | 0.56 |
| C/C0 | 0.961 [0.903, 1.022] | −0.058 ± 0.089 | 1.011 [0.902, 1.134] | 0.913 [0.848, 0.982] | 0.178 | 6/16 | 0.21 |
| C0/T | 0.994 [0.878, 1.125] | −0.009 ± 0.179 | 1.040 [0.851, 1.273] | 0.949 [0.788, 1.143] | 0.330 | 6/16 | 0.86 |

Per-pair C/T (log2): BE +0.26, −0.20, +0.71, +0.32, −0.46, +0.05, +0.25, −0.35; PA −0.13, −0.85,
+0.33, +0.00, −0.39, −0.06, −0.30, −0.26. The between-pair sd (0.38) is larger than the 0.29 the
proposal assumed, so the primary half-width is 0.197 log2 (±1.15×) rather than the planned 0.155.

**Absolute level.** Fresh mean log2 cost on own cells: BE S 12.62, T 12.60, C 12.53, C0 12.55;
PA S 12.70, T 12.64, C 12.84, C0 12.71. G4 on the same cells: BE 13.86, PA 14.11. So the saved
token maps start 2.4× (BE) and 2.7× (PA) cheaper than G4, and 4 040 further searches of either
procedure left that essentially where it was.

**In-loop corroboration (shared seeds, 65k cap, selection-biased).** The final selected parents of
T and C were scored on the same 100 seeds in-loop; their paired contrast gives C/T = 0.920
[0.815, 1.039], the same direction as the fresh result. In-loop selected scores track fresh costs
across the 16 maps (Spearman 0.80 for T, 0.63 for C); in-loop is optimistic by +0.09 (T) and
+0.04 (C) log2, as expected for a selected minimum.

**Did either arm move during the loop?** Mean in-loop score of the two parents per generation
(24 searches each, so noisy) fitted with a per-trajectory slope:

| Arm | slope per generation (log2) [95 %, n = 16] | gen 16–20 minus gen 1–5 | children replacing a parent per generation |
|---|---|---|---|
| T | −0.003 [−0.010, +0.005] | −0.001 [−0.104, +0.102] | 1.40 of 2 |
| C | +0.003 [−0.005, +0.010] | +0.006 [−0.094, +0.105] | 1.42 of 2 |

Negative slope would be learning. Over 20 generations the in-loop drift is bounded to roughly
±0.2 log2 per arm (±1.15×), matching the fresh T/S and C/S intervals. A child displaced at least one
parent in 229/320 (T) and 230/320 (C) generations, i.e. the population turned over constantly
without any net movement.

**C's step mix.** Proposed / survived into the parent set: token 954 / 210 (0.22), b 552 / 133
(0.24), a 414 / 111 (0.27); T token 1 920 / 447 (0.23). Survival rates are the same for all three
operators, so in-loop selection did not discriminate against context steps. Clipping was rare
(303 clipped elements over 1 920 C proposals; final C maps have 0–1 clipped elements) and the
post-clipping column means of the residual are ≈ 2 × 10⁻⁴, so the centring property held in
practice. Final residual RMS 0.13–0.43 log-weight units; residual table L1 1.1–7.7 (of 24 000),
comparable to the token drift. Cosine of each learned residual with the hand-set BE − PA contrast:
|cos| ≤ 0.105, mean −0.01 — the residuals that accumulated are unrelated to the hand-set direction.

**Stage A (calibration, single steps from b = 0; 8 context units, 4 token units, 24 mutants each,
2 × 48 searches per mutant).**

| Operator | σ²_T = cov(Δ_A, Δ_B) [95 %] | μ (mean Δ, + = worse) | per-search var v | corr(Δ_A, Δ_B) within unit | selected-quarter mean Δ_B [95 %] | selected − all [95 %] |
|---|---|---|---|---|---|---|
| context (b) | 0.047 [0.027, 0.065] | +0.059 | 2.65 | 0.50 (n = 192) | −0.017 [−0.085, +0.041] | −0.116 [−0.182, −0.060] |
| token | 0.028 [0.005, 0.051] | +0.028 | 2.63 | 0.33 (n = 96) | −0.006 [−0.100, +0.109] | −0.096 [−0.178, +0.005] |

Per unit, σ²_T for context ranges from −0.001 (PA9:0) to 0.125 (PA10:0); BE 0.038, PA 0.056.
Effort rule: Γ(24) = 0.00237 > Γ(48) = 0.00192, so n = 24 (20 generations). Resampling mutants
within units, 17 % of 2 000 bootstrap replicates would have chosen n = 48, so the choice was not a
coin flip, though both branches have the same budget.

Reading: single b-steps do have real, repeatable effects (σ²_T is resolved above zero; the A/B
correlation is 0.5), and ranking 24 mutants by 48 searches does pick out mutants that are better
than the average mutant on independent seeds. But the average mutant is worse than its parent
(μ > 0 for both operators), and the selected quarter is only back at parent level: its Δ_B interval
includes zero for both operators. Under a normal model of true effects (sd 0.22 context, 0.17
token), roughly 23 % of single steps of either kind would be ≥ 0.1 log2 better than the parent, so
beneficial steps exist but are a minority and are small relative to the scoring noise
(sd of a 24-search block mean = 0.33 log2).

## 3. What the data show

1. **The primary contrast is a bounded null.** Adding rank-one context steps to token continuation
   from the saved 1723 maps gave C/T = 0.955 [0.833, 1.095] over 16 paired starts. The upper bound
   is below 1.15×. A sign test (7/16), Wilcoxon (p = 0.46) and the in-loop paired comparison on
   shared seeds (0.92 [0.82, 1.04]) agree. Within this budget the mixed procedure is, if anything,
   slightly worse than token-only, but the interval includes 1.
2. **Neither arm learned.** T/S = 1.03 [0.90, 1.16], C/S = 0.98 [0.90, 1.07]. The in-loop parent
   scores show no trend in either arm from generation 1 onward (slopes ±0.003 log2/generation,
   intervals spanning zero). This is the row-3 situation: the token arm did not resolve an
   improvement either, so the C/T null cannot be read as "context is ineffective".
3. **The null is not simply "too shallow"; the loop made no measurable progress per generation.**
   The upper bound on T/S (0.22 log2 over 20 generations) caps average progress at about 0.011
   log2 per generation for token steps. Stage A shows why that is plausible: selected single
   steps of either operator are at best parent-level on independent seeds, and the per-child
   scoring noise (0.33 log2 at n = 24) is larger than the true-effect spread (0.17–0.22), so
   the 2 + 6 loop replaces parents 1.4 times per generation largely by noise. A deeper run of the
   same loop would be expected to drift, not climb, unless scoring effort per child rises.
4. **Family split (descriptive).** In PA, context looks harmful: C/T 0.87 [0.71, 1.06], C/S 0.90
   [0.78, 1.05], and removing the residual improves C (C/C0 0.91 [0.85, 0.98]; C0 is cheaper than C
   in 7/8 PA pairs). In BE all contrasts are near 1 with wide intervals. The pooled C/C0 interval
   (0.96 [0.90, 1.02]) includes 1, and C0 also shifts emitted marginals, so this is a hint about
   the PA residual, not an attribution.
5. **Infrastructure and precision.** Everything ran, hashes verified, no holdout touched. The pair
   sd (0.38) exceeded the sizing assumption (0.29); the achieved half-width (±1.15×) was still
   enough to decide the row. Timing projections were conservative by about 70 min.

## 4. What the data do not show

- They do not show that compact context cannot be learned by selection. Stage A found repeatable
  single-step effects of b-steps (σ²_T > 0) comparable to token steps; what failed is accumulation
  under this loop (n = 24, 2 + 6, 20 generations) from already token-tuned starts. a-steps and steps
  from a nonzero residual were never calibrated.
- They do not show that the token procedure has converged in any absolute sense. They show it did
  not move in 4 040 searches at this scoring effort; 0811's 1.45× over 13 440 searches used a
  different loop and is not contradicted by a ±1.15× interval here.
- They do not separate "ineffective context" from "insufficient selection signal per step". The
  Stage A and in-loop evidence point to the second (per-child noise ≫ true effects, no progress in
  either arm), but that is an interpretation, not a measured contrast.
- They say nothing about transfer or holdout cells (by design), and the PA residual-harm hint rests
  on per-family descriptive intervals with 7 df.
- The Γ effort rule's own model is falsified by the outcome: it predicted about 0.06 log2 gain per
  generation for context at n = 24 (1.1 log2 over 20 generations) and the realized gain was ≈ 0.
  The rule should not be reused as a predictor of accumulated learning.

## Against the predictions

plan.md records the same five outcome rows as the proposal, applied in order: U (invalid hashes,
leakage, pairing, missing/duplicate rows, or < 6 complete pairs in either family), 1 (C/T lower > 1),
2 (C/T upper < 1.15 and T/S lower > 1), 3 (C/T upper < 1.15 and T/S lower ≤ 1; "say neither arm
resolved learning only if C/S lower also ≤ 1"), 4 (otherwise). plan.md itself gives no probabilities;
the proposal's were U 5 %, row 1 15 %, row 2 30 %, row 3 25 %, row 4 25 %.

- **Row U:** not matched. Hashes pinned and verified, no leakage (training cells only), pairing
  intact, 0 missing or duplicate rows, 8 + 8 complete pairs.
- **Row 1:** not matched. C/T lower bound 0.833 < 1.
- **Row 2:** not matched. C/T upper 1.095 < 1.15 holds, but T/S lower bound 0.904 ≤ 1.
- **Row 3:** **matched.** C/T upper < 1.15 and T/S lower ≤ 1. The plan's extra condition for
  saying "neither arm resolved learning" is also met: C/S lower bound 0.900 ≤ 1. The run's own
  `status.json` reports row 3 with that flag set, and I agree.
- **Row 4:** not applicable, since row 3 matched first.

Plan expectations against the data:

- **Depth versus ineffective context.** The plan's row 3 says this stays unresolved, and formally
  it does. The data do add that the loop made no measurable per-generation progress in either arm
  (in-loop slopes within ±0.01 log2 per generation; T/S upper bound caps token progress at about
  0.011 log2 per generation), and Stage A shows per-child scoring noise (0.33 log2 at n = 24)
  exceeding the true single-step spread (0.17–0.22). So "depth" in the sense of more generations at
  the same n is unlikely to be the fix; the proposal's reopen condition (a ≥ 3× longer continuation
  or a cheaper inner search) should be read with the emphasis on scoring effort per child or a
  cheaper search, not on generation count alone.
- **Stage A diagnostics for B versus C.** The plan warned that selected-minus-all gain alone is
  not evidence of a step that is beneficial relative to the parent. That is exactly the pattern
  observed: selected-minus-all −0.116 [−0.182, −0.060] for context, but the selected quarter's effect
  relative to the parent is −0.017 [−0.085, +0.041]. Attribution between B (weak initial signal)
  and C (signal that failed to accumulate) stays unresolved, as the plan allows for; the token
  operator shows the same pattern, so whatever limits accumulation is not specific to context.
- **Sizing.** The plan's primary SE formula was applied as written. The proposal's sizing
  assumption (pair sd 0.29, half-width 0.155 log2) was optimistic: realized sd 0.384, half-width
  0.197. Under row 4 the plan says future sizing should use the observed pair sd; row 3 was reached
  regardless, but any follow-up should size with 0.38.
- **Admission.** The plan said not to assume all sixteen pairs fit. All sixteen fit with about
  70 min of the 3.8 h deadline unused, because the reserve factors (1.3× pair, 1.3× fresh, slowest
  group rates) were conservative against measured per-search times of 0.47 s (learn) and 0.87 s
  (fresh). A follow-up at the same timeout could afford roughly 40 % more searches.
- **Representation qualifications.** The plan required reporting clip counts and post-clipping
  column means. Clipping was rare (303 elements over 1 920 C proposals; 0–1 in final maps) and
  post-clipping column means are ≈ 2 × 10⁻⁴, so the centring caveat did not bite in this run.
  The caveat that C0 changes emitted marginals still applies to the C/C0 readout.
- **Effort choice.** The plan's Γ rule picked n = 24 on the point estimate; 17 % of bootstrap
  replicates would have picked 48. Not a gate, but worth noting that the rule's underlying model
  predicted about 1.1 log2 of accumulated context gain over 20 generations and the realized gain
  was ≈ 0, so it is not a usable predictor of accumulation.
