---
outcome: 3
---
# Analysis: 2026-10-06-1425 saved-map shape shift

Reviewer's independent analysis of
[`experiments/output/2026-10-06/2026-10-06-1425-saved-map-shape-shift`](/Users/andreas/developer/folding-evolution/experiments/output/2026-10-06/2026-10-06-1425-saved-map-shape-shift)
(code commit `b397f72`). Everything below was recomputed from the raw `search.jsonl` with
[analysis_recompute.py](analysis_recompute.py) and [analysis_plots.py](analysis_plots.py); the
run's own `result.json` agrees with the recomputation to the last digit (max group-cost
difference 0.0 log2), so the numbers are the same, but the reading is mine.

## 1. Data completeness

| check | result |
|---|---|
| rows in `search.jsonl` | 88 000 = 55 maps × 8 cells × 200 seeds |
| unique (map, cell, seed) keys | 88 000, 0 duplicates |
| every (map, cell) at n = 200 | yes, 440/440 |
| seeds | 1 419 000 000–1 419 000 199, identical across maps and cells; no overlap with 0811's ranges |
| cap / population | 524 288 / 256 on all 88 000 rows |
| `log2_cost` = log2(evaluations), 20.0 if unsolved | 0 mismatches |
| hash checks on 0132 and 0811 sources, cells file | passed (config.json records SHA-256 of each) |
| R_fm fits accepted (TV to R < 0.005) | 12/12, TV 3e-5 to 7e-5 |
| gate (G 8-cell mean vs 0811's G) | passed: 12.452 vs 12.502, difference −0.051 log2 (threshold 0.6) |
| complete "b" starts | 6/6; complete "a" starts 6/6; all 55 maps complete |
| run state / exit | `complete`, exit 0, 2 876 s wall (48 min) against a 9 000 s timeout; no deadline stop |

No stage was cut, so the design ran exactly as approved. The order (G, b pairs, a pairs, M
references) was irrelevant in the end because everything finished.

**Solve rates.** Censoring is confined to the hard branch-else cell `S?M:(S+m)`; every linear
cell solved 200/200 for every map (6 × 55 × 200 = 66 000/66 000).

| family | `S?M:(S+m)` solved | `S?m:(S+M)` solved | linear (6 cells) |
|---|---|---|---|
| G | 190/200 | 199/200 | 1200/1200 |
| M1–M6 | 1174/1200 | 1198/1200 | 7200/7200 |
| M+ (12) | 2375/2400 | 2399/2400 | 14400/14400 |
| R (12) | 2386/2400 | 2400/2400 | 14400/14400 |
| R_abl (12) | 2378/2400 | 2396/2400 | 14400/14400 |
| R_fm (12) | 2376/2400 | 2399/2400 | 14400/14400 |

The worst learned map on the hard cell is M+5a at 193/200; G is 190/200. Replacing cell means
with medians changes the b-only R/M+ BE ratio from 0.944 to 0.925 and LIN from 1.29 to 1.30, so
the unsolved-cost convention does not drive anything below.

**Seed noise is small relative to start-to-start spread.** The seed-level standard error of a
map's BE group cost is about 0.08 log2 (sd 1.2 across 200 seeds) and of its LIN cost about
0.035 log2. Per-start contrasts below range over ±1 log2, so, as the proposal said, more seeds
would not have helped.

**Shortcut solutions.** 822/88 000 rows report non-zero `shortcuts` (training-perfect
individuals that fail held-out cases); the harness counts to exact solution, so these do not
inflate solve counts. They are spread over all families and I did not pursue them further.

## 2. Primary layer: the six "b" pairs, R vs M+

Ratios are 2^(cost_M+ − cost_R), so > 1 means R is faster. Intervals are 95% t with 5 df over
six start clusters (one pair per start).

| contrast ("b" only) | BE ratio | LIN ratio | shift (BE ÷ LIN) | starts with R faster (BE / LIN) |
|---|---|---|---|---|
| R / M+ | 0.944 [0.766, 1.164] | 1.292 [0.876, 1.905] | **0.731 [0.571, 0.935]** | 2/6 BE, 5/6 LIN |

Per-start log2 R/M+ on the "b" continuations (BE, LIN, shift):

| start | 1b | 2b | 3b | 4b | 5b | 6b |
|---|---|---|---|---|---|---|
| BE | −0.23 | +0.40 | −0.29 | +0.12 | −0.34 | −0.17 |
| LIN | +0.29 | +1.40 | +0.26 | +0.15 | −0.17 | +0.29 |
| shift | −0.52 | −1.00 | −0.54 | −0.02 | −0.17 | −0.46 |

**What this shows.** The "a" pattern (R faster on BE, slower on LIN) does not appear in the
"b" continuations. On the "b" maps the shift is in the *opposite* direction in 6/6 starts, and
its 95% interval excludes 1 on the low side (upper bound 0.935). That is, among the "b" pairs R
is, if anything, relatively *faster on linear* than M+ (LIN 1.29×, 5/6 starts, interval spans 1)
and no faster on BE (0.94×, interval spans 1). The proposal's row 3 condition holds (shift upper
0.935 < 1.41 and BE upper 1.164 < 1.25), and no earlier row matches. The data go one step further
than row 3's wording: the "b" shift is not merely bounded below 1.41×, its interval sits entirely
below 1.

Per cell, the sign flip between letters is uniform: on all six linear cells the "b" R/M+ mean
is positive (+0.27 to +0.45 log2, R faster in 5/6 or 6/6 starts) where the "a" mean is negative
(−0.46 to −0.76, R faster in 1/6). On the two BE cells "b" is +0.02 and −0.19 (2/6 starts each)
where "a" is +0.41 and +0.22 (5/6 each).

## 3. Were the "a" numbers seed noise? No: the "a" maps repeat on fresh seeds

The 12 "a" maps were re-scored here on the 200 fresh seeds (0811 used 50 different seeds per
cell). Per start, log2 R/M+ (BE, LIN, shift), 0811 seeds vs fresh seeds:

| start | 0811 (50 seeds) | fresh (200 seeds) |
|---|---|---|
| 1a | +0.52, −0.13, +0.65 | +0.57, −0.04, +0.61 |
| 2a | +0.56, −0.67, +1.23 | +0.59, −0.78, +1.36 |
| 3a | +0.60, −0.65, +1.24 | +0.27, −0.60, +0.87 |
| 4a | −0.10, −1.88, +1.77 | −0.50, −1.81, +1.31 |
| 5a | +0.47, −0.34, +0.81 | +0.48, −0.28, +0.77 |
| 6a | +0.42, −0.01, +0.43 | +0.48, +0.04, +0.44 |

"a"-only intervals on fresh seeds: BE 1.24× [0.92, 1.68], LIN 0.67× [0.41, 1.10], shift
1.86× [1.41, 2.44] (0811: 1.33, 0.65, 2.03). So the 0811 §2.5 pattern is a real property of
those six saved maps, not of the seeds it was measured on. What did not replicate is the
*learner-level* claim: six independent continuations of the same learner from the same six
starts, differing only in learning seed, show the opposite shift. Both letters were selected on
the PA training cells only, so their off-family behaviour is unconstrained, and the "a"/"b"
split shows how far it wanders between runs of the same learner.

Where the divergence sits (per-start "b" minus "a" group cost, positive = "b" costlier):

| family | BE | LIN |
|---|---|---|
| M+ | −0.03 ± 0.16 | +0.55 ± 0.38 (5/6 starts; the "a" M+ maps are faster on linear) |
| R | +0.37 ± 0.59 (5/6) | −0.40 ± 0.82 (4/6) |
| R_fm | +0.04 ± 0.34 | −0.18 ± 0.74 |
| R_abl | +0.08 ± 0.44 | −0.10 ± 0.45 |

Both arms move: the "a" M+ maps happen to be fast on linear and the "a" R maps slow on linear
and fast on BE; the "b" maps show neither. Against their M starts, M+ gains on BE in both letters
(1.40× [1.07, 1.83] "a"; 1.42× [1.09, 1.86] "b"), and R gains on BE in both letters (1.74×
[1.05, 2.88]; 1.34× [1.10, 1.64]). Continued learning on PA cells transfers to BE for both
learners; whether it also transfers to linear differs by run, and that is what the "shift" was
measuring.

## 4. Dependency layer

| layer | contrast | BE | LIN | shift |
|---|---|---|---|---|
| "b" only | R / R_fm | 1.035 [0.913, 1.172] | 1.017 [0.974, 1.062] | 1.017 [0.921, 1.123] |
| "b" only | R / R_abl | 1.113 [0.808, 1.534] | 1.045 [0.838, 1.303] | 1.066 [0.800, 1.419] |
| "b" only | R_fm / M+ | 0.913 [0.726, 1.147] | 1.270 [0.864, 1.866] | 0.719 [0.541, 0.954] |
| "a" only | R / R_fm | 1.300 [0.952, 1.775] | 0.877 [0.752, 1.022] | 1.483 [1.234, 1.782] |
| "a" only | R / R_abl | 1.360 [0.914, 2.023] | 0.851 [0.698, 1.037] | 1.599 [1.190, 2.148] |
| "a" only | R_fm / M+ | 0.956 [0.843, 1.086] | 0.765 [0.518, 1.129] | 1.251 [0.839, 1.866] |
| pooled (a/b mean per start) | R / R_fm | 1.160 [0.965, 1.394] | 0.944 [0.865, 1.031] | 1.228 [1.112, 1.357] |
| pooled | R / R_abl | 1.230 [0.920, 1.645] | 0.943 [0.812, 1.095] | 1.305 [1.071, 1.591] |
| pooled | R_fm / M+ | 0.934 [0.833, 1.048] | 0.985 [0.783, 1.241] | 0.948 [0.727, 1.236] |
| pooled | R / M+ | 1.083 [0.918, 1.278] | 0.930 [0.690, 1.255] | 1.164 [0.982, 1.381] |

Formal sub-rows: "b"-only is **D-c** (R/R_fm shift lower 0.92 ≤ 1; R_fm/M+ shift lower 0.54 ≤ 1
so D-b's second clause fails). Pooled is **D-a** (R/R_fm shift lower 1.11 > 1) with BE R/R_fm
lower 0.965 ≤ 1, i.e. the "trade-off only" reading.

**What this shows.**

- On the unselected "b" maps, the frequency-matched control reproduces R almost exactly: R/R_fm
  is within 1.17× on BE and 1.06× on LIN at the interval edges, and R_fm/M+ shows the same
  reversed shift as R/M+ (0.72 [0.54, 0.95]). Whatever the "b" R maps do off-family, a G-context
  map with R's pooled emitted token frequencies does the same. Any contribution of the learned
  residuals is bounded there below 1.17× (BE) and 1.12× (shift).
- The pooled D-a verdict is carried entirely by the "a" maps (shift 1.48 [1.23, 1.78] "a" vs
  1.02 [0.92, 1.12] "b"). Since the "a" maps are the ones on which the lead was found, the
  pooled layer is contaminated by selection, exactly as the proposal's [note 3]/[1419-3] warned.
  Even on "a", R/R_fm BE lower bound is 0.95, so the residual effect is a linear slow-down with
  an unresolved BE gain, not a demonstrated branch gain.
- R/R_abl tells the same story as R/R_fm in both letters and attributes nothing on its own.

## 5. Descriptive items the proposal asked for

- **IF_GT emitted frequency.** R − M+ differences range −0.071 to +0.064 across the 12 pairs
  with no relation to the shift (Pearson r = 0.28, n = 12, p = 0.38; "a" shifts are all above
  the "b" shifts at every value of the covariate, see [shift_vs_ifgt.png](shift_vs_ifgt.png)).
  Across the 48 learned maps, IF_GT frequency correlates weakly with lower BE cost (r = −0.27,
  p = 0.06) and not with LIN cost (r = 0.22). The covariate does not explain the "a"/"b" split.
- **G costs** per cell (log2): BE 15.46 (190/200) and 12.96; linear 11.33–12.49, all solved.
  G's 8-cell mean matches 0811 within 0.05 log2.
- **M/G.** All six M starts are faster than G on BE (M/G 1.72–4.49 on `S?M:(S+m)`,
  1.30–2.36 on `S?m:(S+M)`); on linear cells M1 and M5 are slower than G (0.41–0.91), M2–M4 and
  M6 faster (1.08–1.9), repeating 0811 §2.5 on 200 seeds.
- Per-pair ratios and solve counts are in `result.json` (`per_pair`, `cell_stats`).

Plots: [per_start_R_over_Mplus.png](per_start_R_over_Mplus.png) (per start, both letters, with
0811 "a" values overlaid), [dependency_by_letter.png](dependency_by_letter.png), and the run's
own `diagnostics.png` (shift vs IF_GT; search curves, which separate the letters cleanly in the
first panel and show nothing of note in the other two).

## 6. What the data do and do not show

Shown:
1. The 0811 "a" pattern is a stable property of those six R/M+ map pairs (repeats on 200 fresh
   seeds), not seed noise.
2. The same learner's six "b" continuations from the same starts do not show it. Their shift is
   below 1 in 6/6 starts with 95% interval [0.57, 0.94]; their BE R/M+ is 0.94 [0.77, 1.16].
   Any BE gain is bounded below 1.17× and any shift below 0.94× on this set.
3. On the "b" set a G-based map with R's pooled uniform-allele emitted frequencies reproduces R
   on BE, LIN and shift to within about 1.1×. The learned residuals add nothing measurable there.
4. Both learners, both letters, are faster on BE than their M start (lower bounds 1.05–1.10×).
   The off-family linear behaviour varies by learning run by about 0.5 log2 within a family.

Not shown:
- That residuals never matter: on the "a" set R beats R_fm on BE in 5/6 starts (point 1.30×,
  lower bound 0.95). That set is selected, and the "b" set contradicts it, so this is at most a
  per-run property, not a learner property.
- Family specificity, solver supply, positional or selected-population frequencies (out of
  scope by design).
- Anything about new starts: all 12 pairs share the same six M starts.

The outcome rules were written for "does the pattern repeat, and if so is it residual-dependent".
The answer is that the pattern did not repeat and reversed, which the rules file under row 3.
The reversal itself (shift interval below 1 on "b") was not a pre-registered hypothesis and
should be read as "the sign of the off-family shift is a property of the individual learning
run", not as a new lead in the other direction.

## Against the predictions

Read after the analysis above was written. The plan ([plan.md](plan.md)) restates the proposal's
rules unchanged, so the comparison is against the proposal's outcome table and its "what each
outcome changes" list.

- **Row 0 gate:** did not fire. Hashes matched, G differed from 0811 by −0.05 log2 (threshold
  0.6), all six "b" starts and all 12 R_fm fits complete.
- **Row 1 (BE gain and shift replicate):** no. "b" BE R/M+ lower bound 0.77 (needs > 1);
  shift lower bound 0.57 (needs > 1).
- **Row 2 (shift replicates without BE gain):** no, same shift bound.
- **Row 3 (no replication at the prior size):** **yes.** Shift upper 0.935 < 1.41 and BE upper
  1.164 < 1.25. This is the first matching row. The data exceed row 3's wording in one respect:
  the "b" shift interval lies entirely below 1 (6/6 starts), i.e. the sign reversed, which no
  row anticipated. I do not treat the reversal as a finding in its own right because it was not
  pre-stated and the "a" set shows the opposite with the same strength; together they say the
  off-family shift is run-specific.
- **Dependency layer:** interpreted only under rows 1–2, so it carries no verdict here. For the
  record: "b"-only D-c, pooled D-a trade-off-only (R/R_fm BE lower 0.965). The pooled D-a is
  driven entirely by the selected "a" maps and should not be read as evidence about the learner.
- **Precision forecast:** the proposal expected, if "b" repeated "a", BE ≈ [1.09, 1.62] and
  shift ≈ [1.43, 2.87]. The realised "b" intervals are about as wide as forecast (BE width
  0.60 log2 vs 0.57 forecast; shift 0.71 vs 1.0), so the design had the sensitivity it claimed;
  the effect was simply not there.
- **Solve forecast:** about 196/200 per learned map on the hard cell. Observed: learned maps
  2375–2386 of 2400 per family, i.e. 198–199 per map. Linear 100% as forecast.
- **Runtime forecast:** 53 min search at 10 workers plus overhead, 2.5 h timeout. Actual 48 min
  wall including fitting and reporting (worker mean 0.325 s per search).
- **Expected outcome probabilities** (row 1 ≈ 35%, row 4 ≈ 35%, row 3 ≈ 20%, row 2 ≈ 10%): the
  20% case occurred.
- **Downstream rule for row 3:** "drop the lead at the stated bounds; token-only adaptation
  stays the demonstrated gain." The data support that. One qualification for the steward: the
  bound applies to the shift and BE gain of this learner's saved maps on these cells; the
  "a"-set pattern is real for those maps, so the correct statement is that the branch/linear
  shift is not a reproducible property of the contextual learner, not that it was never present.
  The "b"-only R/R_fm result (R reproduced within 1.1× by a frequency-matched token-only map)
  additionally supports giving context no more than a secondary arm in the four-reducer study.
