---
outcome: "6"
---

# Analysis: 2026-10-07-1137 selection-calibrated continuation

Reviewer analysis of the single queue entry
`2026-10-07-1137-selection-calibrated-continuation`. All contrasts below were
recomputed from the raw fresh-score rows (`f1_scores.json`, `f2_scores.json`,
plus the pinned 0821 reference for T24) with an independent implementation of
the family-balanced estimator; every value agrees with `report.json` to the
printed precision. Recomputed values are in
[recomputed_contrasts.json](recomputed_contrasts.json); the figure is
[analysis_figure.png](analysis_figure.png).

## 1. Data completeness

| Check | Expected | Observed |
|---|---|---|
| Queue entries | 1 | 1, `done`, exit 0, wall 16 653 s (4.63 h) of 20 700 s timeout; internal deadline 19 800 s had 4 929 s left at the last admission |
| Commit | `86ef669` | `86ef669`, `git_dirty: false`, workers 10 |
| T trajectories | 16 (BE1–8, PA1–8) | 16, each exactly 9 600 searches |
| C trajectories | admitted in order BE1, PA1, … | all 16 admitted, each exactly 9 600 searches |
| `generations.jsonl` | 32 × 12 = 384 | 384 (12 per trajectory) |
| `selected_changes.jsonl` | 32 × 12 = 384 | 384 |
| `search.jsonl` rows | 294 912 learn + 12 288 selection + 12 000 F1 + 16 500 F2 = 335 700 | 335 700, caps 65 536 (learn, selection) and 524 288 (F1, F2) as designed |
| F1 rows | 16 starts × {S, T, T_mid} × own cells × 50 seeds = 12 000 | 12 000, 48 arms, no duplicates, seeds 1 824 000 000–049 |
| F2 rows | 16 × {S, T, C, C0} × own cells × 50 + G4 × 10 cells × 50 = 16 500 | 16 500, no duplicates, seeds 1 863 000 000–049 |
| Shared training cases per seed | identical across arms | 0 unpaired rows in F1 or F2 |
| T/C in-loop seed sharing | identical 96-seed block per start × generation | verified from `search.jsonl`: 0 mismatches in 192 start-generations |
| 0821 S identity (16 scientific fields) | 4 000 rows bit-identical | 4 000/4 000, 0 mismatches |
| Midpoints | 16 T maps after generation 6 | 16 |

Solve fractions: in-loop 282 055/294 912 (95.6 %); final selection 11 815/12 288;
F1 11 883/12 000; F2 16 336/16 500. Unsolved rows at the 524 288 fresh cap, imputed at
2 × cap: F1 S 47, T 42, T_mid 28 (each of 4 000); F2 S 41, T 50, C 21, C0 33 (of 4 000),
G4 19/500. Re-running every contrast with unsolved imputed at 1 × cap changes no
ratio by more than 0.006 (table in §2.4), so the imputation does not drive any result.

Nothing is missing, duplicated or failed. The gate, admission and outcome logic ran as
pre-stated in the code: gate passed on the F1 point estimate, all 16 C starts fit,
and the runner's own outcome row is 6.

## 2. Key numbers

Metric throughout: A/B improvement = mean over own cells and seeds of
log2(cost_B) − log2(cost_A), averaged per start, then equal weight per family;
95 % t interval on 14 df (8 + 8 starts). "Starts improved" counts starts with a
positive per-start log2 effect, out of 16.

### 2.1 Token continuation (stage 1, F1 = 0821's fresh block)

| Contrast | Ratio [95 %] | BE (8) | PA (8) | Starts improved |
|---|---|---|---|---|
| **T/S(F1)** (gate) | **1.143 [1.089, 1.200]** | 1.124 [1.067, 1.183] | 1.163 [1.060, 1.277] | 16/16 |
| T_mid/S(F1) | 1.081 [1.017, 1.149] | 1.087 [0.980, 1.206] | 1.075 [0.986, 1.171] | 13/16 |
| T/T_mid(F1) | 1.058 [0.990, 1.130] | 1.034 [0.925, 1.155] | 1.083 [0.985, 1.190] | 10/16 |
| T96/T24(F1) | 1.114 [0.987, 1.257] | 1.113 | 1.115 | 12/16 |
| T24/S(F1), 0821 reference, recomputed | 1.026 [0.904, 1.165] | | | |

Gate: 1.143 ≥ 1.10, passed. Standard error of the gate estimate: 0.033 log2 from the
t formula; a bootstrap that resamples starts within family and seeds together gives
sd 0.060 log2, with 82 % of replicates ≥ 1.10 and 100 % > 1 (seeds-only sd 0.036).
The code review had asked for this; the pass is not a knife-edge.

### 2.2 Confirmation and context (stage 2, F2 = new seeds)

| Contrast | Ratio [95 %] | BE (8) | PA (8) | Starts improved |
|---|---|---|---|---|
| **T/S(F2)** | **1.122 [1.031, 1.222]** | 1.108 [0.945, 1.300] | 1.136 [1.029, 1.254] | 11/16 |
| **C/T** (primary) | **0.967 [0.871, 1.073]** | 1.037 [0.857, 1.253] | 0.901 [0.791, 1.027] | 8/16 |
| C/S | 1.084 [0.993, 1.184] | 1.149 [0.963, 1.371] | 1.024 [0.943, 1.110] | 11/16 |
| C/C0 | 1.037 [0.972, 1.107] | 1.096 [0.967, 1.241] | 0.982 [0.914, 1.055] | 9/16 |
| C0/S (not pre-stated) | 1.046 [0.984, 1.112] | 1.049 | 1.042 | 11/16 |
| C0/T (not pre-stated) | 0.932 [0.860, 1.010] | 0.946 | 0.918 | 6/16 |

Absolute levels on F2 training cells (mean log2 evaluations): G4 14.03 (BE) / 14.07
(PA); S 12.71 / 12.71; T 12.56 / 12.52; C 12.51 / 12.67. The saved starts are already
about 2.5× cheaper than G4 on their own cells; this run's token gain is on top of that.

### 2.3 Per-start structure

Per-start T/S effects on F1 and F2 correlate only 0.15 across the 16 starts (figure,
right panel). The sd of the F1 − F2 per-start difference is 0.24 log2, and splitting
F1's 50 seeds into halves gives a noise sd of about 0.16 log2 for a single 50-seed
per-start estimate. The implied true between-start sd of the token gain is only about
0.07 log2. So the per-start values, the "PA heterogeneity" readout and the
starts-improved counts on F2 are dominated by seed-block noise; only the pooled means
are informative. This contradicts the proposal's feasibility table, which treated the
0.33 log2 per-start sd from 0821 as mostly real. It also means F2 is a genuinely
independent re-measurement of the pooled gain, not a near-copy of F1 as the code
review expected.

Per cell, T/S(F1) ranges from 1.00 (BE:S?F:(M+m)) to 1.28 (BE:F?S:(M+m)); no cell
got worse. C/T per cell: BE 0.85–1.27 (two of four above 1), PA 0.79–0.98 (all six
below 1).

### 2.4 Sensitivity

| Contrast | Pre-stated | Unsolved = 1 × cap | Median per start | Unbalanced 16-start mean |
|---|---|---|---|---|
| T/S(F1) | 1.143 [1.089, 1.200] | 1.142 [1.087, 1.199] | 1.145 [1.064, 1.232] | 1.143 [1.090, 1.199] |
| T/S(F2) | 1.122 [1.031, 1.222] | 1.124 [1.036, 1.219] | 1.130 [1.047, 1.219] | 1.122 [1.034, 1.218] |
| C/T | 0.967 [0.871, 1.073] | 0.961 [0.867, 1.065] | 0.910 [0.820, 1.010] | 0.967 [0.868, 1.076] |
| C/S | 1.084 [0.993, 1.184] | 1.080 [0.990, 1.178] | 1.057 [0.964, 1.157] | 1.084 [0.991, 1.187] |

The T/S(F2) lower bound stays above 1 in all four variants (1.031–1.047) and the C/T
upper bound stays below 1.15 (1.010–1.076). The T/S(F2) lower bound is close to the
row 5 boundary, so the row 6 verdict is robust to these variants but not comfortable.

### 2.5 In-loop dynamics (descriptive, 65 536 cap, selection-biased)

| Readout | T (16) | C (16) | 0821 for comparison |
|---|---|---|---|
| Retained-parent mean, generation 1 → 12 (log2) | 12.616 → 12.459 (−0.157) | 12.616 → 12.581 (−0.035) | flat over 20 generations |
| Per-trajectory slope, log2/generation [95 %] | −0.013 [−0.021, −0.005], 14/16 negative | −0.008 [−0.019, +0.002], 10/16 negative | T −0.003 [−0.010, +0.005]; C +0.003 |
| Children accepted per generation | 1.37 of 2 (0 in 11, 1 in 100, 2 in 81 of 192) | 1.41 of 2 (0 in 16, 1 in 81, 2 in 95) | 1.40 / 1.42 |
| Winner's curse: acceptance score − next-block rescore | −0.142 (sd 0.195, n = 241; 73 % negative) | −0.161 (sd 0.188, n = 247; 81 % negative) | not measured |
| Selected change, child − source parent on the next block (both retained) | −0.048 ± 0.026 se, n = 51 of 241 accepted (190 source parents discarded) | +0.039 ± 0.030, n = 41 of 247 (206 discarded) | not measured |
| Final selection, 2 parents × 192 searches: mean score gap | 0.125 log2 | 0.119 log2 | |

Negative values mean cheaper. The turnover is the same as in 0821, but T now shows a
resolved downward in-loop trend and a 0.16 log2 end-to-start drop that matches the
fresh T/S gain (log2 1.143 = 0.19). Accepted children were on average 0.14–0.16 log2
luckier at acceptance than on an independent block, which is the size of the whole
gain; the loop makes progress despite that. The selected-change readout covers only a
fifth of accepted children (the source parent usually did not survive) and is a selected
subset: descriptive only.

### 2.6 Context arm internals

Operator survival into the parent set (C arm): token 140/564 (0.248), b 79/361
(0.219), a 52/227 (0.229); T arm token 262/1 152 (0.227). Selection did not favour or
disfavour context steps. Clipping: 91 clipped elements over 588 context proposals,
final maps 0–1 clipped elements. Final residual RMS 0.04–0.37 log-weight units;
residual table L1 0.18–7.1 of 24 000 versus total C table L1 1.3–9.0. Cosine of the
learned residual with the hand-set BE − PA direction: |cos| ≤ 0.045 for all 16. Token
vectors: T moved 0.29–0.66 RMS from S, C's token part 0.12–0.57; the correlation
between T's and C's token displacement is −0.35 to +0.58 per start (mean +0.12), so the
two arms did not converge on a shared token direction.

Shortcut programs (perfect on the 64 training cases but not on all 1 331 inputs) have
median 0 per fresh search in every map, with a heavy tail (max 258 788 in one S row).
The cost metric counts evaluations until an exact solution, so shortcuts cannot inflate
a map's score; noted only because the brief asks for shortcut checks.

## 3. What the data shows

1. **Token continuation with 96 searches per candidate improved the saved maps on their
   training cells.** T/S is 1.143 [1.089, 1.200] on the gate block and 1.122 [1.031,
   1.222] on independent seeds; 16/16 starts improved on F1. The in-loop parent score
   fell in 14/16 T trajectories. This is the first resolved token gain from the 1723
   starts (0821's T24/S on the same F1 seeds was 1.026 [0.904, 1.165]). The run
   delivers the positive control that 0821 lacked.
2. **In that same loop, rank-one context did not add to token tuning.** C/T 0.967
   [0.871, 1.073]: the upper bound excludes a 1.15× increment, and the point estimate
   is below 1. PA is the family that carries the negative direction (0.901 [0.791,
   1.027], all six PA cells below 1); BE is 1.037 [0.857, 1.253].
3. **C's token component learned less than T's** (C0/T 0.932 [0.860, 1.010]), and the
   residual gave back about 1.04× (C/C0 1.037 [0.972, 1.107], unresolved). The
   context arm spent half its proposals on the residual (564 token versus 1 152 in T),
   so C has fewer token steps than T. The net C/T null is consistent with "context
   steps are roughly neutral but displace token steps", and with "context is mildly
   harmful on PA"; the data do not separate these.
4. The procedure comparison T96/T24 is 1.114 [0.987, 1.257], unresolved on its own.

## 4. What the data does not show

- **Why this procedure climbed and 0821's did not.** Three things changed together
  (96 instead of 24 searches per candidate, 12 instead of 20 generations, 9 600 instead
  of 4 040 searches per trajectory). The run does not isolate scoring reliability as
  the cause, and the critique already said so.
- **Whether learning had plateaued.** T/T_mid 1.058 [0.990, 1.130] and the in-loop
  curve is still falling at generation 12. A longer run could add more; nothing here
  bounds that.
- **Anything about context with matched token effort.** C had half as many token
  proposals as T. A design where context steps are additional to a full token budget,
  or follow token convergence, is a different experiment. The row 6 claim is about
  this loop and this mixing rule only.
- **Transfer.** Only own training cells were scored. No withheld-cell result exists.
- **Independent replication of learning.** F2 re-scores the same 16 learned maps on new
  seeds; it does not rerun the learning. The per-start correlation of 0.15 between F1
  and F2 shows per-start token gains are not measurable at 50 seeds, so claims about
  which starts or families learned more are not supported.
- **A small context effect.** C/T admits anything from a 13 % loss to a 7 % gain.
  "Context adds < 1.15×" is the resolved statement; "context does nothing" is not.
- The T/S(F2) lower bound (1.031) is just above 1. Under the pre-stated rules this
  confirms the token gain; a slightly unluckier seed block would have put the run in
  row 5 with the same maps. The gate-block interval is the stronger evidence for the
  token gain, and the two blocks agree on the pooled mean (0.19 versus 0.17 log2).

## Against the predictions

The plan fixed rows U and 1–7, evaluated in order. Checked against the recomputed
numbers (§2):

- **U:** not matched. Hashes and the pinned reference verified, 4 000/4 000 S rows
  bit-identical to 0821, no missing or duplicate rows in F1 or F2, 8 complete T and
  8 complete C trajectories per family.
- **Rows 1–2** (gate fails): not matched. T/S(F1) point 1.143 ≥ 1.10, gate passed.
- **Row 3** (< 6 C per family): not matched. All 16 C trajectories completed, so the
  token confirmation is on the same 16 starts as C/T and no shortened-stage rule applies.
- **Row 4** (C/T lower > 1): not matched. C/T lower bound 0.871.
- **Row 5** (T/S(F2) lower ≤ 1): not matched, but narrowly. T/S(F2) lower bound 1.031
  (1.036–1.047 under the sensitivity variants in §2.4).
- **Row 6** (gate passes, T/S(F2) lower > 1, C/T upper < 1.15): **matched.** C/T upper
  bound 1.073 (1.010–1.076 across variants). Per the plan's wording: in a procedure with
  confirmed token gain, the mean context addition is bounded below 1.15× on training
  cells, for these starts, this representation and this loop; joint learning from G4
  remains untested.
- **Row 7:** not reached.

The runner's own `outcome.row` is 6 and agrees.

What the plan said row 6 would and would not mean, checked against the data:

- The plan restricts the claim to these 16 starts, the rank-one representation and the
  2 + 6 loop with the ½ token/context mixing rule. §2.2 and §3.3 add a reason the
  restriction matters: C's token component is itself behind T's (C0/T 0.932 [0.860,
  1.010]), because context proposals displaced token proposals. The row 6 bound is
  therefore about the mixed loop, not about context steps added on top of a full token
  budget.
- The plan says F2 confirms scoring of fixed maps, not learning. The data go a step
  further: F1 and F2 per-start gains correlate only 0.15, so per-start and per-family
  readouts (PA heterogeneity, starts improved on F2) are not measurable at this seed
  count. The pooled T/S is the only token quantity this design resolves.
- The plan's descriptive readouts behave as planned: T_mid/S 1.081 [1.017, 1.149] and
  T/T_mid 1.058 [0.990, 1.130] show progress in both halves without a resolved
  flattening; T96/T24 1.114 [0.987, 1.257] is a procedure comparison and stays
  unresolved; selected-change coverage is sparse (51/241 and 41/247 accepted children)
  as the code review predicted.
- The proposal's 45 % gate-pass estimate and its "0821's effort model is not reused"
  stance stand. The gate passed with a start-and-seed bootstrap pass rate of 82 %, so
  the pass is not a boundary case, whereas the row 5/6 boundary on F2 was close.

Confidence: high that token continuation with this procedure improves these maps by
roughly 1.12–1.14× on training cells (two independent seed blocks, all 16 starts on
F1, resolved in-loop trend). Moderate that context adds less than 1.15×: the bound is
pre-stated and robust to the sensitivity variants, but the interval still admits a 7 %
gain or a 13 % loss, and the comparison is confounded by the token-step budget C gave
up. Low confidence in anything per family or per start.
