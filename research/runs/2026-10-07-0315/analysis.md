---
outcome: 1
---
# Analysis: starting programs versus ongoing decoder on the ten training cells

Reviewer analysis of run `2026-10-07-0315-training-bank-initialization`
(commit `5dae3a6`, output
`experiments/output/2026-10-07/2026-10-07-0315-training-bank-initialization/`).
Every number below was recomputed from the raw `search.jsonl` rows with an
independent script; all agree with the runner's `result.json` to the printed
precision.

## 1. Data completeness

| Check | Result |
|---|---|
| Rows in `search.jsonl` | 122 000 = 10 cells × 200 seeds × (1 GG + 20 maps × 3 arms) |
| Duplicates on (cell, arm, map, seed) | 0 |
| Seeds | 3150000–3150199, all 200 present, 200 `complete_seeds` |
| Every (arm, cell, map) stratum | exactly 200 rows |
| GG rows use decoder G4 only; MG decoder = G4; GM decoder = the map's own table | all true |
| MG generation-0 token hash = MM's; GM = GG's, per (map, cell, seed) | 0 mismatches of 80 000 |
| `initial_reencoded` true on MG/GM only | 0 flag errors |
| Unsolved rows not at cap, or solved rows at cap | 0 / 0 |
| Cap | 524 288 on every row |
| Validation (40 round trips × 10 000 tapes; 786 bit-exact reproductions: 420 from 1723, 366 from 2331) | passed |
| Row-U gates: ≥120 seeds; GG ≥ 75 % on every cell; D lower bound > log2 1.25 | 200; min 91 %; 1.16 log2 |
| Wall time | 15 385 s (4.27 h) of a 25 200 s deadline; no stop reason; 9.4 effective workers |
| stderr | empty |

The run is complete and balanced. Nothing was dropped, truncated or
re-run. The runner's deadline logic never triggered.

Solves use exact verification on all 1 331 inputs, so no shortcut can be
counted as a solve. Individuals that were perfect on the 64 training inputs
but not on the full input set appeared in 2 056 of 122 000 searches (1.7 %);
they are visible in `shortcuts` and never terminate a search.

## 2. Solve fractions and caps

| Arm | n | solved | fraction | at cap |
|---|---:|---:|---:|---:|
| GG | 2 000 | 1 931 | 0.966 | 69 |
| MM | 40 000 | 39 504 | 0.988 | 496 |
| MG | 40 000 | 39 113 | 0.978 | 887 |
| GM | 40 000 | 39 376 | 0.984 | 624 |

GG per cell (of 200): BE 182, 194, 182, 185; PA 196, 200, 195, 198, 199, 200.
Caps concentrate on the BE cells: MM 422/16 000, MG 689/16 000, GM 542/16 000
on BE cells versus 74, 198 and 82 of 24 000 on PA cells. Capped searches
enter the contrasts at the cap (log2 = 19), so the BE contrasts carry more
cap pressure; the sensitivities in §5 bound its effect.

Generation-0 solves: 20 of 122 000 (10 MM, 10 MG, 0 GM, 0 GG). Seeding a
solver into the start population is not what the M start supplies.

## 3. Pooled contrasts (replication of 2331)

Weighting as planned: equal cell families, equal cells within family, equal
map families, equal maps within family. Intervals: crossed bootstrap, 20 000
replicates, maps resampled within family and whole seed blocks shared across
arms, maps and cells. δ = 0.25 log2.

| Contrast | Definition | log2 | ratio | 95 % | width | label |
|---|---|---:|---:|---|---:|---|
| P1 | T_MG / T_MM: cost of losing the ongoing M decoder, given M's start | +0.357 | 1.28× | [1.22, 1.34] | 0.13 | **P** |
| P2 | T_GM / T_MM: cost of losing M's start, given the M decoder | +0.411 | 1.33× | [1.26, 1.40] | 0.15 | **P** |
| D | T_GG / T_MM | +1.289 | 2.44× | [2.23, 2.66] | 0.26 | P |
| I_G | T_GG / T_MG | +0.932 | 1.91× | [1.76, 2.06] | 0.23 | P |
| O_G | T_GG / T_GM | +0.879 | 1.84× | [1.73, 1.96] | 0.19 | P |
| interaction | P1 − O_G | −0.521 | 0.70× | [0.65, 0.75] | 0.20 | N (resolved negative) |

Both conditional increments resolve positive with lower bounds above δ.
Neither P1 nor P2 is negative, so there is no antagonism flag. The
interaction is sub-additive: the two gains together (D = 1.29 log2) are
less than the sum of the two marginal removals (I_G + O_G = 1.81 log2).

For reference, 2331 on its three cells at 400 seeds gave P1 1.39× [1.31,
1.47], P2 1.30× [1.24, 1.36], interaction −0.34 [−0.40, −0.29]. The cells
differ, so the comparison is descriptive, but both increments again sit well
above δ and the interaction is again resolved negative (larger here).

## 4. Family balance (co-primary)

S_c = mean over 20 maps × 200 seeds of log2(T_MG / T_GM) = P1 − P2 per cell.
Positive S means losing the ongoing decoder costs more than losing the start.

| Cell | P1 | P2 | S_c | S 95 % (maps × seeds bootstrap) |
|---|---:|---:|---:|---|
| BE `F?S:(M+m)` | +0.291 | +0.678 | −0.387 | [−0.588, −0.184] |
| BE `F?m:(S+M)` | +0.149 | +0.360 | −0.211 | [−0.391, −0.031] |
| BE `S?F:(M+m)` | +0.138 | +0.423 | −0.285 | [−0.516, −0.057] |
| BE `S?M:(m+F)` | +0.236 | +0.470 | −0.234 | [−0.441, −0.020] |
| PA `(F?S:m)+M` | +0.462 | +0.417 | +0.045 | [−0.100, +0.187] |
| PA `(F?m:M)+S` | +0.426 | +0.271 | +0.155 | [+0.025, +0.287] |
| PA `(F?m:S)+M` | +0.447 | +0.403 | +0.044 | [−0.097, +0.183] |
| PA `(S?M:F)+m` | +0.834 | +0.292 | +0.541 | [+0.379, +0.702] |
| PA `(S?m:F)+M` | +0.618 | +0.313 | +0.305 | [+0.169, +0.442] |
| PA `(S?m:M)+F` | +0.282 | +0.334 | −0.052 | [−0.156, +0.051] |

Family means: BE −0.279 (sd 0.078 over 4 cells), PA +0.173 (sd 0.218 over
6 cells). Pooled within-family cell spread s_w = 0.179.

**C = mean S(BE) − mean S(PA) = −0.452, Welch 95 % [−0.684, −0.221], df 6.7.**
Label **B**. The interval is entirely below zero and not inside ±0.25, so
the B/E precedence question raised in the code review does not arise: B is
unambiguous at this margin.

Per-cell view: all four BE cells have S < 0 with upper bounds below zero.
Among the six PA cells, three have S resolved above zero, three straddle
zero. No PA cell is resolved negative and no BE cell is resolved positive.
By cell family, P1 is +0.20 [+0.11, +0.30] on BE and +0.51 [+0.42, +0.59]
on PA; P2 is +0.48 [+0.37, +0.59] on BE and +0.34 [+0.26, +0.41] on PA.
So on BE cells the start matters more, on PA cells the ongoing decoder
matters more, and this time both components are resolved positive within
each family too.

Plots: [per_cell_S.png](per_cell_S.png) (S per cell with 95 % intervals,
2331's three cells overlaid hollow) and
[per_cell_P1_P2.png](per_cell_P1_P2.png) (P1 against P2 per cell). The
runner's own figures are `contrasts.png`, `family_balance.png` and
`search_curves.png` in the output folder.

### Robustness of C (descriptive)

- Leave-one-cell-out: C ranges from −0.38 to −0.50 and every interval's
  upper bound stays below −0.14. No single cell carries the result.
- Seed halves (seeds 0–99 vs 100–199): every BE cell is negative in both
  halves; the PA cells keep their ordering. `BE F?m:(S+M)` is the least
  stable (−0.06 vs −0.36).
- Per map: all 20 of 20 maps individually have lower S on the BE cells than
  on the PA cells (differences −0.09 to −0.81). The map side is unanimous;
  the limit on C is the cell count, as the proposal said.

## 5. Sensitivities

| Variant | P1 | P2 | D | interaction | C |
|---|---:|---:|---:|---:|---|
| Planned | +0.357 P | +0.411 P | +1.289 P | −0.521 N | −0.452 [−0.684, −0.221] B |
| Winsorised at 65 536 | +0.295 P | +0.386 P | +1.127 P | −0.446 N | −0.427 [−0.610, −0.244] B |
| Drop triplets with any capped arm (36 990 of 40 000 kept) | +0.305 | +0.398 | +1.185 | −0.483 | −0.483 [−0.703, −0.263] B |

No label changes. Winsorising shrinks P1 most (0.36 → 0.29), which is the
cap pressure on the BE cells noted in §2. Its winsorised lower bound (0.236)
dips just under δ = 0.25; P1 keeps label P because the rule is lower > 0 and
upper ≥ δ, and the planned row does not use the winsorised value.

## 6. Map family × cell family (descriptive)

| Maps \ cells | BE cells | PA cells |
|---|---|---|
| BE maps (in-sample on BE) | P1 +0.25, P2 +0.55, S −0.30, D +1.46 | P1 +0.53, P2 +0.35, S +0.18, D +1.21 |
| PA maps (in-sample on PA) | P1 +0.16, P2 +0.42, S −0.26, D +1.23 | P1 +0.50, P2 +0.33, S +0.17, D +1.26 |

The family balance S is set by the cell family, not the map family: BE maps
and PA maps give S ≈ −0.3/−0.26 on BE cells and +0.18/+0.17 on PA cells.
The proposal's guess that in-sample pairing would raise P2 holds on BE
cells (BE maps 0.55 vs PA maps 0.42) and not on PA cells (0.33 vs 0.35).
D is higher for in-sample BE maps on BE cells (1.46 vs 1.23); elsewhere
in-sample and off-family are within 0.05. These are point estimates with
no intervals and were not primary.

## 7. What the data shows

1. **Both components replicate across the bank.** With the decoder held at
   M, starting from M's programs saves 1.33× [1.26, 1.40]. With the start
   held at M's programs, searching under M saves 1.28× [1.22, 1.34]. The
   gains overlap (interaction 0.70× [0.65, 0.75]); neither is zero and
   neither is the whole of D = 2.44×.
2. **The balance tracks cell family on these ten cells.** On all four BE
   cells the start carries more than the ongoing decoder (S −0.21 to
   −0.39, each resolved); on the PA cells the ongoing decoder carries at
   least as much (S −0.05 to +0.54, three resolved positive, none resolved
   negative). C = −0.45 [−0.68, −0.22]. This is the pattern 2331 saw on one
   BE and two PA holdout cells, now on four and six screened cells, with 20
   of 20 maps agreeing in direction.
3. The family difference is relative. Both family means of P1 and P2 are
   resolved positive; C < 0 says the ratio shifts, not that either component
   vanishes on either family.

## 8. What the data does not show

- **Why.** "Ongoing" still bundles mutation, crossover, inherited latent
  alleles and continued program supply, and "start" bundles the
  generation-0 program census with whatever allele structure the
  re-encoding preserves. Nothing here separates them.
- **Family as the cause.** Family is confounded with other cell properties.
  Across the ten cells S correlates with the MM median cost (r = 0.77) and
  with GG cap rate (r = −0.77); within PA alone S correlates with MM median
  cost at r = 0.85: the two PA cells with S > 0.3 are the two hardest PA
  cells for MM. At matched MM difficulty (median log2 cost 12.3–12.6) the
  BE cells still sit at −0.21 to −0.39 and the PA cells at +0.04 to +0.16,
  so family is not explained away by difficulty, but with four and six
  cells from one screened bank "BE versus PA" and "branch-else versus
  plus-arg shape" and "difficulty tail" cannot be separated. These
  correlations are post hoc and descriptive.
- **Generality.** Ten screened training cells, 20 frozen maps from one
  bank, G4's hand-supplied context, one search regime. The Welch interval
  treats these cells as a sample; they are the cells the maps were
  screened on. Nothing here says what a fresh BE or PA cell would do.
- **Whether 2331's holdout BE cell was typical.** It was a different seed
  cohort and a withheld cell; the 13-cell view in `result.json` is
  descriptive only. Its S (−0.27) lies inside the BE range seen here.
- **Equivalence of anything.** The interaction being negative establishes
  sub-additivity on capped log cost, not a shared resource.

## Against the predictions

Plan.md's outcome table is the proposal's table unchanged. First match on the
planned analysis: P1 = P, P2 = P, C = B → **row 1**. Both sensitivity variants
also route to row 1.

- **Row prediction.** The proposal put 35 % on row 1 and 35 % on row 4, with
  the split hinging on the within-family cell spread s_w. The data landed on
  row 1. s_w came out at 0.18, inside the "resolves" zone the proposal
  described (s_w ≲ 0.35 for a 2331-sized difference), and the observed C
  (−0.45) is close to 2331's three-cell difference of −0.55.
- **Pooled replication.** Predicted to replicate because 2331's lower bounds
  sat well above δ. It did: P1 lower bound 0.29 log2 and P2 lower bound
  0.33 log2 against δ = 0.25. P1 is somewhat smaller here (1.28× vs 1.39×)
  and the interaction larger in magnitude (−0.52 vs −0.34); both are
  descriptive cross-cohort comparisons.
- **Precision.** Predicted pooled half-widths 0.08–0.12 log2; observed 0.066
  (P1) and 0.076 (P2), so more precise than planned. Predicted C half-width
  ≈ 1.55 × s_w = 0.28 at s_w = 0.18; observed 0.23. The proposal's note that
  label E would be hard to reach was moot because the point sits far from
  zero.
- **Row-U gates.** Predicted GG solves of roughly 172–200/200 per cell;
  observed 182–200. D's lower bound 2.23× against the 1.25× gate.
- **In-sample P2.** The proposal guessed that matched maps would raise P2 on
  their own family's cells. True on BE cells (0.55 in-sample vs 0.42
  off-family), not on PA cells (0.33 vs 0.35). Descriptive only, as planned.
- **Plan's row-1 meaning.** "Both conditional components help; BE is
  relatively more start-dependent than PA on this bank. No sign flip is
  established by C alone." The data support exactly that reading. Beyond
  what C alone can say, the per-cell view does show every BE cell with
  S resolved below zero and no PA cell resolved below zero, which is as
  close to a family-level flip as ten cells can show; the plan correctly
  withholds that as a routed claim, and the difficulty confound in §8
  is a reason to keep withholding it.
- **Feasibility.** Planned budget 400 min conservative, 255 min from the
  probe; actual 256 min. The probe projection was accurate.

Per plan, every row closes question 17 and returns root 10 to strategy. The
critic's notes 3 and 4 (relative difference, label precedence) were honoured
in the report and did not change the routing: C's interval is not inside the
margin, so B is unambiguous.
