---
outcome: 3
---

# Analysis: frozen starting-program × ongoing-decoder 2×2 (run 2026-10-06-2331)

Reviewer: independent re-analysis of `search.jsonl` from
`experiments/output/2026-10-07/2026-10-06-2331-initialization-ongoing-decoder/`
(code commit `8f42f38`, queue exit 0, wall 10 799 s ≈ 3.0 h, under the 4.5 h internal
deadline; `stop_reason: null`). All numbers below were recomputed from the raw rows
and agree with the runner's `result.json` to three decimals unless stated.

## 1. Data completeness

| Check | Result |
|---|---|
| Rows in `search.jsonl` | 79 200 = 73 200 main + 6 000 MMr (law check), as planned |
| Unique (map, arm, cell, seed) keys | 79 200 / 79 200, no duplicates |
| Seeds | 400 complete blocks, 2331000–2331399, none missing; MMr on the first 100 only |
| Arms per map | MM, MG, GM: 1 200 each for all 20 maps (3 cells × 400 seeds); GG: 1 200 shared rows under G4 |
| Pairing | MG token hash = MM token hash and GM token hash = GG token hash on all 24 000 (map, cell, seed) triplets, 0 mismatches |
| Unsolved rows | 1 251 / 79 200, all recorded at the cap 524 288; 1 row solved exactly at the cap |
| Generation-0 solvers | 12 / 79 200 (MM 5, MG 5, MMr 2, none under G) |
| Validation gates | round trips 40/40 pass (10 000 tapes each); chi-square uniformity p = 0.83, 0.66, 0.68 for G4, BE1, PA1 (threshold 0.0167); 630/630 historical 2229 rows bit-identical; MMr/MM 99 % interval [0.95×, 1.09×] contains 1 |
| Outcome gates | GG solves per cell 378, 380, 398 of 400 (94.5–99.5 %, gate ≥ 85 %); D lower bound 2.05× > 1.25×; 400 ≥ 200 seeds |

Nothing is missing and nothing failed. The analysis set is the full planned grid.

## 2. Key numbers

Cost T = evaluations to the first exact D1331 solve, cap if unsolved. Contrasts are paired
per (map, cell, seed) in log2, averaged over 400 seeds and 3 cells with equal weight, then
over 20 maps. Intervals: the runner's crossed map-within-family / whole-seed bootstrap
(primary, 20 000 replicates). My map-level t interval (n = 20, the proposal's original
primary) is given alongside; the two agree to about 0.01 log2.

| Contrast | Meaning | Ratio | 95 % bootstrap | 95 % map-level t (log2) | Label |
|---|---|---:|---|---|---|
| **P1** = T_MG/T_MM | ongoing-decoder increment, given M start | **1.39×** | [1.31, 1.47] | +0.47 [+0.39, +0.56] | P |
| **P2** = T_GM/T_MM | start increment, given M ongoing | **1.30×** | [1.24, 1.36] | +0.38 [+0.33, +0.43] | P |
| D = T_GG/T_MM | diagonal (full map gain) | 2.29× | [2.05, 2.54] | +1.19 [+1.08, +1.31] | P |
| I_G = T_GG/T_MG | start effect under G | 1.65× | [1.50, 1.81] | +0.72 [+0.65, +0.79] | P |
| O_G = T_GG/T_GM | ongoing effect from G start | 1.76× | [1.61, 1.92] | +0.82 [+0.73, +0.90] | P |
| interaction = P1 − O_G | | 0.79× | [0.73, 0.86] | −0.34 [−0.40, −0.29] | N (resolved negative) |

Both primary increments are resolved positive and both lower bounds sit above the practical
margin δ = 0.25 log2 (1.19×): P1's lower bound is +0.39, P2's is +0.33. Shares of the
diagonal: I_G/D = 0.60, O_G/D = 0.68. The two components overlap: I_G + O_G = 1.53 log2
against D = 1.19, and P1 + P2 = 0.85 against D = 1.19. Either component alone recovers
60–68 % of the full gain in log units; adding the second gives a smaller increment
(1.30–1.39×) than the first did (1.65–1.76×). The interaction is negative in every one of
the 20 maps.

The diagonal of 2.29× [2.05, 2.54] on fresh seeds matches the 2229 holdout gains
(2.0–2.9× by cell), so the GG/MM arms reproduce the known result as well as the 630-row
bit-exact check.

### Per cell (map-level t intervals, log2)

| Cell | P1 | P2 | I_G | O_G | D | interaction |
|---|---|---|---|---|---|---|
| BE `S?m:(M+F)` | +0.15 [+0.06, +0.25] (1.11×) | +0.42 [+0.33, +0.51] (1.34×) | +0.92 | +0.65 | +1.07 (2.11×) | −0.50 |
| PA `(F?S:M)+m` | +0.55 [+0.44, +0.65] (1.46×) | +0.28 [+0.21, +0.35] (1.22×) | +0.53 | +0.80 | +1.08 (2.11×) | −0.25 |
| PA `(S?M:m)+F` | +0.72 [+0.63, +0.82] (1.65×) | +0.43 [+0.38, +0.49] (1.35×) | +0.70 | +0.99 | +1.42 (2.68×) | −0.27 |

The ordering of the two increments flips between cells. On the BE cell the ongoing
increment given a learned start is small (1.11×, upper bound exactly at δ) and the start
effect under G is the larger component (1.89×). On both PA cells the ongoing increment is
the larger one (1.46–1.65×) and the start increment is 1.22–1.35×. This is descriptive
(three reused cells) and cannot change the row, but the pooled P1 hides it: P1 is "P" on
the pooled analysis and borderline N on the BE cell alone.

### Per family and per map

| Family (10 maps) | P1 | P2 | D |
|---|---|---|---|
| BE maps | 1.41× [1.32, 1.50] | 1.33× [1.27, 1.39] | 2.33× [2.21, 2.46] |
| PA maps | 1.37× [1.23, 1.52] | 1.27× [1.19, 1.35] | 2.24× [1.90, 2.65] |

The families agree. Per map (see `increments.png`, left), 18 of 20 maps have both P1 and
P2 above 0.25 log2 or within 0.01 of it. The exceptions are PA9 (P1 +0.08, P2 +0.14,
D +0.45, the weak map already known from 2229) and PA2 (P1 +0.16, P2 +0.31, D +0.83).
Between-map spread is 0.17 log2 (P1), 0.11 (P2), 0.24 (D); PA9 alone drives most of the PA
spread, as in 2229.

### Distributions and solve rates (pooled over maps)

| Arm | n | solved | median T | geometric mean T | cap hits | median generations |
|---|---:|---:|---:|---:|---:|---:|
| GG | 1 200 | 1 156 (96.3 %) | 10 752 | 13 685 | 44 (3.7 %) | 42 |
| MM | 24 000 | 23 753 (99.0 %) | 5 120 | 5 986 | 247 (1.0 %) | 20 |
| MG | 24 000 | 23 434 (97.6 %) | 6 656 | 8 316 | 566 (2.4 %) | 26 |
| GM | 24 000 | 23 681 (98.7 %) | 6 656 | 7 777 | 320 (1.3 %) | 26 |
| MMr | 6 000 | 5 925 (98.8 %) | | | 75 (1.3 %) | 21 |

Fraction solved within a budget: at 4 096 evaluations GG 16 %, MG 34 %, GM 29 %, MM 41 %;
at 16 384 GG 65 %, MG 75 %, GM 82 %, MM 86 %. MG and GM have the same median cost but MG has
the heavier tail (more cap hits), which is why P1 > P2 on the mean of logs while the medians tie.

At the (map, cell, seed) level the effects are shifts, not sweeps: MG is slower than MM in
57 % of the 24 000 pairs, faster in 39 %, tied in 3 %; GM is slower than MM in 57 %, faster
in 41 %. The diagonal D is positive in 69 % of pairs.

### Sensitivity to the cap

Unsolved searches enter at the cap, and MG has the most of them. Two checks:

| Variant | P1 | P2 | D |
|---|---|---|---|
| As planned (cap = 524 288) | 1.39× [1.31, 1.47] | 1.30× [1.25, 1.35] | 2.29× [2.11, 2.47] |
| Drop the 1 858 / 24 000 triplets where any of the four arms hit the cap | 1.33× [1.27, 1.40] | 1.29× [1.24, 1.33] | 2.11× [1.97, 2.26] |
| Winsorise all costs at 65 536 | 1.32× [1.26, 1.39] | 1.28× [1.24, 1.33] | 2.06× [1.92, 2.21] |

(t intervals over 20 maps.) Both primary labels stay P with lower bounds above δ in every
variant. The tail contributes about 0.05 log2 to P1 and nothing to P2.

### The MMr law check (recomputed)

MMr/MM on the first 100 seeds: 1.02× with a 99 % t interval [0.97×, 1.07×] (bootstrap
[0.95×, 1.09×]); MMr is slower in 47.2 % of pairs and faster in 46.3 %. Re-encoding M into
itself leaves the search cost unchanged within ±7 %, so the re-encoding step itself is
not what slows MG or GM. This is a non-rejection on 6 000 searches, not equivalence.

## 3. What the data shows

1. **Neither component alone is the mechanism.** With the starting tapes held identical
   (MG vs MM), using the learned map for mutation and crossover during search saves 1.39×
   [1.31, 1.47] in evaluations. With the ongoing decoder held at M (GM vs MM), starting from
   M's programs instead of G's saves 1.30× [1.24, 1.36]. Both are resolved above the 1.19×
   margin on 20 maps × 3 cells × 400 seeds.
2. **The components are strongly sub-additive.** Each alone gives 1.65–1.76× of the 2.29×
   diagonal (60–68 % in log units); the second component adds only 1.30–1.39×. The
   interaction is −0.34 log2 [−0.40, −0.29] and negative in all 20 maps. Part of what the
   learned start supplies is the same thing the learned ongoing decoder supplies.
3. **Which component dominates depends on the cell.** On the BE cell the ongoing increment
   given a learned start is only 1.11× [1.04, 1.19] and the start carries most of the gain;
   on the PA cells the ongoing decoder carries most of it. The per-cell P1 upper bound on
   the BE cell lands exactly on δ, so with that cell alone the result would be a different
   row. The pooled "both" verdict is an average over heterogeneous cells.
4. **The effects are robust to the cap and to the interval method.** Bootstrap and t
   agree; excluding unsolved triplets or winsorising at 65 536 moves P1 by ≤ 0.07 log2 and
   P2 by ≤ 0.02 and changes no label.
5. **Searches are short and almost nothing solves at generation 0** (12 of 79 200), so the
   start effect is about useful partial programs and allele structure in the initial
   population, not about seeding solvers.

## 4. What the data does not show

- It does not say *why* the ongoing decoder helps: mutation, crossover, inherited allele
  structure and continued program supply are bundled in "ongoing". P1 is the conditional
  value of the whole bundle.
- It does not separate "supply of useful partial programs" from "topology of the
  neighbourhood". The negative interaction is consistent with both components feeding a
  common pool, but that is an interpretation, not a measurement.
- Three reused screened cells with hand-supplied G4 context; nothing about holdout cells,
  learned context or family specificity. The cell-level flip (BE vs PA) is on one BE cell
  and two PA cells and is descriptive only.
- P is a sign-and-margin label, not a statement that 1.30–1.39× is practically large. The
  increments are a third to a half of the component effects measured from the G side.
- The MMr check bounds the re-encoding artefact at ±7 % on 100 seeds; it is not equivalence.
- One map (PA9) shows almost no gain and almost no increments; the map-level conclusions
  are about the population of 20 maps, not every map.

Figures in this folder: `increments.png` (left: per-map P1 vs P2 against δ; right:
per-cell contrasts with map-level t intervals). The run's own `contrasts.png` and
`search_curves.png` are in the output folder.

## Against the predictions

The plan's first-match row table routes on the pooled P1 and P2 labels with ≥ 200 complete
seeds, 20 maps and the crossed bootstrap. Row U does not apply: every validation check
passed, 400 seeds are complete, GG solves 94.5–99.5 % per cell, and D's lower bound (2.05×)
is above 1.25×. P1 = P and P2 = P, so the data matches **row 3: both conditional increments
are positive**. The steward predicted row 3 at 30 %, behind row 1 ("ongoing decoder carries
the gain", 45 %).

What the prediction got right and wrong:

- **Row 1 was wrong on P2.** The plan's leading hypothesis was that the learned start would
  add < 1.19× once M is used during search. It adds 1.30× [1.24, 1.36]; the lower bound is
  above δ, so P2 is not close to N. Starting programs matter even though almost nothing
  solves at generation 0 and searches take only 20–40 generations.
- **The proposal's own hint from the probe was that GM is close to MM.** On 400 seeds and
  20 maps it is not: GM costs 1.30× more than MM. The probe's 25 seeds on three maps
  (one of them PA9, which shows almost no effects at all) under-read the start effect.
- **The plan asked that row 3 be described through the interaction and the secondary
  effects.** The interaction is −0.34 log2 [−0.40, −0.29], resolved negative in all 20
  maps: the components are sub-additive, and either alone captures 60–68 % of the
  diagonal (I_G/D = 0.60, O_G/D = 0.68). This is the "both contribute, redundantly" corner
  of row 3, not an additive split.
- **Not predicted, and descriptive only:** the dominant component flips with the cell. On
  the BE cell P1 is 1.11× [1.04, 1.19] (its upper bound sits exactly on δ, which would be
  N-or-X on that cell alone) while P2 is 1.34×; on both PA cells P1 (1.46–1.65×) exceeds P2
  (1.22–1.35×). The plan forbids per-cell results from changing the row, and I have not
  let them; but slot 2 on the ten training cells should expect this heterogeneity and the
  steward should treat the pooled P1 label as an average over cells that disagree.

Validation gates behaved as designed: the MMr law check stayed within [0.95×, 1.09×] at
99 %, the 630 historical rows reproduced bit-exactly, and the run finished 1.5 h inside the
internal deadline (3.0 h wall against the 3.7 h the plan projected with slack; the code
review's ~3.5 h estimate from the seed-major barrier was closer than the plan's 2.5 h).

**Decision-rule consequence.** Row 3 permits slot 2 (same frozen 2×2 on the ten training
cells). The measured between-map spread for sizing is 0.17 log2 (P1) and 0.11 (P2) with
400 seeds; 200 seeds would roughly keep the labels given lower bounds of +0.39 and +0.33
against δ = 0.25, but the per-cell P1 on BE-type cells is near δ and would need the full
seed count to resolve per cell if that becomes a question.
