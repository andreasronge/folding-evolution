---
outcome: "row 1: training interaction I 1.17 [1.09, 1.25], both fits improved; holdout row 4, transfer unresolved"
---
# Analysis — 2026-10-07-2156 (token-only T1 and T2 on the 1924 seeds)

Reviewer: Claude Fable 5.1. Data: commit `36c665d`, output
`experiments/output/2026-10-07/2026-10-07-2156-context-increment/`. All numbers below were
recomputed from `search.jsonl` plus the frozen C1/C2 rows
(`experiments/chem_tape/data/context_increment_2129/context_rows.jsonl.gz`); they match
`result.json` to three decimals. Plots: `lineage_interaction.png`, `contrasts.png`; per-lineage
contrasts in `lineage_contrasts_recomputed.json` (this folder).

## 1. Data completeness

Every stage ran, every arm and seed is present, and no row is duplicated.

| Check | Expected | Observed |
|---|---:|---:|
| Provenance SHA, 2 artifact SHAs, 128 table hashes | pass | pass |
| Saved C1/C2 roster (`validate_rows`) | 16,384 | 16,384, pairing checks 8,064 |
| Replay of saved C1/C2 rows (exact `scientific_fields`) | 64/64 | 64/64, 0 errors |
| T2 timing block (training, seed index 0) | 160 | 160, counted once |
| Training T rows (T1 + T2, incl. timing block) | 10,240 | 10,240 |
| Holdout T rows (T1 + T2) | 6,144 | 6,144 |
| Duplicate keys (phase, corpus, cell, arm, seed) | 0 | 0 |
| Per arm × phase: training 5,120, holdout 3,072 | 4 × 2 cells | all exact |
| Queue exit | 0 | 0, `stop_reason: null` |

Timing. Queue wall 1,585 s (26.4 min of 4,500 s). Replay 5.6 s, timing block 17.4 s, training
1,018 s, holdout 540 s. Effective workers over the primary roster were 9.88 of 10. The holdout
gate projected 642 s against 3,157 s remaining and admitted; the actual holdout took 540 s, so
the projection was conservative by 19%. Observed mean worker-seconds per search: T1 1.069
(historical 1.042), T2-BE 1.338 (preflight 0.665), T2-PA 0.655 (preflight 0.343). The preflight
T2 block underestimated the full-roster T2 cost by about 2×, as the code review's bootstrap
warned; it did not matter here because throughput was high.

Solve counts (exact D1331 verification; unsolved charged 2 × cap):

| Phase | Arm | Solved / total | Unsolved BE / PA |
|---|---|---:|---:|
| training | C1 | 5,081 / 5,120 | 35 / 4 |
| training | C2 | 5,106 / 5,120 | 9 / 5 |
| training | T1 | 5,044 / 5,120 | 58 / 18 |
| training | T2 | 5,051 / 5,120 | 55 / 14 |
| holdout | C1 | 3,042 / 3,072 | 14 / 16 |
| holdout | C2 | 3,049 / 3,072 | 11 / 12 |
| holdout | T1 | 3,029 / 3,072 | 19 / 24 |
| holdout | T2 | 3,038 / 3,072 | 18 / 16 |

Unsolved rate is 0.3–1.5% in every arm. In holdout, 69 of the 118 unsolved rows across all four
arms sit in one cell, `PA:(F?S:M)+m`; the other two holdout cells have at most 17 unsolved rows
per arm. Shortcut solutions (perfect on the 64 training cases, failing exact verification)
occurred in 1.0–2.2% of searches in every arm with no arm bias, and they never count as solved,
so the cost metric is not leaking training-case overfitting.

## 2. Key numbers

Speed ratios above one favour the numerator. I = 2^(−D), D = (C2 − T2) − (C1 − T1) in log2 cost.
Training: equal family weight, t on 15 df. Holdout: all 32 lineages, t on 31 df. Per-family
intervals use the 16 lineages of that family (15 df).

### Training (primary, 32 lineages × own cells × 32 seeds, 5,120 searches per arm)

| Contrast | Pooled | BE (16 lineages) | PA (16 lineages) |
|---|---|---|---|
| **Interaction I** | **1.169 [1.093, 1.250]** | 1.337 [1.192, 1.500] | 1.021 [0.953, 1.094] |
| T2/T1 | 1.201 [1.150, 1.255] | 1.165 [1.086, 1.250] | 1.239 [1.175, 1.305] |
| C2/T2 | 1.580 [1.520, 1.641] | 1.804 [1.682, 1.934] | 1.384 [1.340, 1.428] |
| C1/T1 | 1.352 [1.274, 1.434] | 1.349 [1.223, 1.488] | 1.355 [1.267, 1.449] |
| C2/C1 | 1.404 [1.347, 1.464] | 1.558 [1.463, 1.659] | 1.265 [1.198, 1.336] |

Lineages with I > 1: 25 of 32 (BE 15 of 16, PA 10 of 16). Lineage I ranges 0.74 to 1.82.
Leave-one-lineage-out lower bound of the pooled I: 1.082 to 1.112, so no single lineage carries
the result. C2/C1 is identical to 1924 by construction (same rows). C1/T1 on these seeds
(1.352) agrees with 1707's independent-seed estimate (1.365 [1.288, 1.446]).

Sensitivity of the training interaction to the cost rule:

| Rule | I | T2/T1 |
|---|---|---|
| Pre-registered: unsolved = 2 × cap, mean over seeds | 1.169 [1.093, 1.250] | 1.201 [1.150, 1.255] |
| Unsolved = 1 × cap | 1.165 [1.091, 1.243] | 1.200 [1.151, 1.251] |
| Unsolved = 4 × cap | 1.173 [1.094, 1.257] | 1.202 [1.148, 1.259] |
| Drop seeds unsolved in any arm (pairwise) | 1.131 [1.059, 1.209] | 1.203 [1.157, 1.250] |
| Median over seeds instead of mean | 1.089 [1.008, 1.177] | 1.184 [1.126, 1.244] |

The lower bound stays above 1 under every rule, but the median rule shrinks the point estimate
to 1.09 with a lower bound of 1.008. Part of the mean-based interaction therefore comes from the
upper tail of the cost distribution (slow or unsolved seeds), not only from a shift of typical
cost.

Noise split (log2 variance of lineage I): BE observed between-lineage 0.097 versus estimated seed
contribution 0.104; PA 0.035 versus 0.046. In training, seed noise accounts for essentially all
of the between-lineage spread, so the lineage SDs (BE 0.311, PA 0.187 log2) are mostly seed noise
and more seeds per cell would tighten the interval. Conditional sizing (report): 6 lineages per
family would suffice for lower > 1 at the observed effect; no finite n bounds it within ±10%
because the point estimate (1.17) is already outside the margin.

### Holdout (3 withheld cells × 32 lineages × 32 seeds, 3,072 searches per arm)

| Contrast | Pooled (32 lineages) | BE lineages | PA lineages |
|---|---|---|---|
| **Interaction I** | **1.087 [0.984, 1.200]** | 1.064 [0.919, 1.233] | 1.110 [0.956, 1.289] |
| T2/T1 | 1.186 [1.107, 1.271] | 1.203 [1.079, 1.342] | 1.170 [1.061, 1.290] |
| C2/T2 | 1.365 [1.287, 1.447] | 1.399 [1.295, 1.512] | 1.331 [1.209, 1.464] |
| C1/T1 | 1.255 [1.169, 1.349] | 1.315 [1.159, 1.492] | 1.199 [1.110, 1.295] |
| C2/C1 | 1.289 [1.204, 1.381] | 1.280 [1.144, 1.433] | 1.299 [1.184, 1.424] |

Lineages with I > 1: 21 of 32. Lineage I ranges 0.66 to 1.87. Leave-one-out lower bound 0.971 to
1.003. Sensitivity: 1 × cap 1.087 [0.987, 1.198]; drop-unsolved 1.078 [0.981, 1.184]; median
1.128 [1.020, 1.246]. The pooled holdout interval spans 1 under every rule except the median,
which was not pre-registered. Noise split: between-lineage variance 0.159 (BE) and 0.164 (PA)
versus seed contribution 0.098 and 0.103, so here lineage variation is real and larger than
seed noise. Conditional sizing: 46 balanced lineages for lower > 1 at the observed effect; about
2,000 lineages for a ±10% bound. Per holdout cell, the only interval excluding 1 is the BE
holdout cell `BE:S?m:(M+F)` scored by PA lineages (I 1.45 [1.19, 1.75], 16 lineages); this is
one of six cell-by-family subgroups and is reported as descriptive only.

## 3. What the data shows

1. **Training interaction is above 1 with the pre-registered estimator.** I = 1.169, 95%
   [1.093, 1.250]. Feedback (1924's C2 procedure) increased the speed advantage of the additionally
   fitted context over the global-token fit by about 17% on the training cells, relative to the
   pre-feedback pair. Robust to the penalty rule and to leaving out any one lineage.
2. **The token-only fit also improved.** T2/T1 = 1.201 [1.150, 1.255] in training and 1.186
   [1.107, 1.271] in holdout. Both fits gained from the feedback corpus; the context fit gained
   more. Under row 1 of the outcome table, "both fits improved" applies.
3. **The interaction is a BE effect in this sample.** BE I = 1.337 [1.19, 1.50]; PA I = 1.021
   [0.953, 1.094]. The PA family's own interval is inside ±10% and spans 1. The pooled row-1
   verdict is carried by the BE lineages. The proposal's equal-family pooling was pre-registered
   and the pooled claim stands, but any mechanism reading must account for a family in which
   feedback helped the token fit (PA T2/T1 = 1.24) as much as the context fit (PA C2/C1 = 1.27).
4. **Transfer is unresolved.** Holdout I = 1.087 [0.984, 1.200]. The interval spans 1 and its
   upper bound exceeds 1.10, which is outcome row 4. The holdout C2/T2 (1.37) and C2/C1 (1.29)
   stay well above 1, so the context fit still wins after feedback on withheld cells; what is not
   resolved is whether its margin over the token fit grew.
5. **Stage sizing worked.** 26 min of a 75 min window, with the holdout gate projecting
   conservatively. The small-block preflight underestimated T2 cost by 2×; a future projection
   should use full-roster timing, as this run's gate did.

## 4. What the data does not show

- No independent confirmation. The C rows and seeds are 1924's; T1 and T2 were scored on the
  same seeds and training indices. This is the pre-registered extension, not a replication.
- Not a claim about token maps in general. T learns global token multipliers over G4's fixed
  context. The interaction compares two specific fitting procedures on one corpus pair.
- Not a mechanism. Yield, diversity, tape content and the fitting procedure are bundled in
  "feedback". The data cannot say whether the extra contextual advantage comes from the corpus
  or from how C2 uses it.
- Not a statement about typical cost alone. The median-over-seeds variant gives I = 1.09 with a
  lower bound of 1.008; a material part of the mean effect sits in the slow tail. The
  pre-registered estimator is the mean with 2 × cap, and that is the primary number, but the
  tail dependence should be mentioned wherever the 17% figure is quoted.
- No holdout claim about the interaction, in either direction. An interval spanning 1 is not
  equality; the point estimate (1.09) is close to the training PA value and the sizing says a
  lower bound above 1 at this effect size would need about 46 lineages.

## Against the predictions

The plan's ordered outcome rules apply separately to training (primary) and holdout, using the
95% bounds of I.

**Training: row 1.** Lower bound 1.093 > 1. By the plan's wording, feedback increased the
advantage of this additionally fitted context procedure over this restricted token procedure.
T2/T1's lower bound (1.150) is also above 1, so the row-1 sub-clause "both fits improved"
applies. The plan forbids reading this as token-map impossibility, a sharpening mechanism, or
"mostly contextual", and the data gives no reason to go beyond the plan: the PA family on its own
sits inside ±10% (1.021 [0.953, 1.094]), and the median-over-seeds variant brings the pooled
lower bound to 1.008. The pooled estimator was pre-registered with equal family weight, so row 1
is the matched label; the per-family split is the caveat that should travel with it.

**Holdout: row 4.** I = 1.087 [0.984, 1.200]. The interval spans 1 and the upper bound exceeds
1.10, so rows 1–3 do not apply. Per the plan, transfer stays unresolved. The requested
diagnostics are in section 2: lineage SDs 0.399 (BE) and 0.404 (PA) log2; between-lineage
variance exceeds the estimated seed contribution by about 1.6× in both families, so here more
seeds alone would not settle it; conditional sizing says 46 balanced lineages for a lower bound
above 1 at the observed effect and about 2,000 for a ±10% bound.

**Feasibility predictions.** The plan projected 22–53 min; the run took 26.4 min. The plan's
preflight T2 costs (0.671 BE, 0.344 PA worker-s) were half the full-roster values (1.338, 0.655),
which the plan flagged as unmeasured for holdout; the gate used full-roster timing as specified
and admitted with 4.9× headroom. The historical holdout/training inflation of 1 was slightly
optimistic for T1 (holdout 0.928 versus training 1.069 worker-s, so actually below 1) and fine for
T2 (0.804 versus 0.928).

**Allocation reading the plan permits.** Row 1 "can inform allocation to a later contextual-fit
investigation". With the holdout unresolved and the effect confined to BE in this sample, a
follow-up should say which family and which stage it targets before any sizing. None of this
authorizes C3.

Outcome label: training row 1 (primary); holdout row 4 (transfer unresolved).
