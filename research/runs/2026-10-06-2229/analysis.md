---
outcome: 4
---
# Analysis — 2026-10-06-2229: frozen crossed BE/PA maps on the three holdouts

Reviewer: Claude (Fable 5.1), independent of the researcher. Every number below was
recomputed from `search.jsonl` with a separate script (`/tmp/recompute_2229.py`, inlined
checks: completeness, hashes, per-row cost, t/Welch intervals) and agrees with
`result.json` to the printed precision. Code: commit `33fcee2` on
`research/2026-10-06-2229`. Output:
`experiments/output/2026-10-06/2026-10-06-2229-frozen-crossed-holdouts/`.

## 1. Data completeness

| Check | Result |
|---|---|
| Rows in `search.jsonl` | 25 200 = 21 arms × 3 holdouts × 400 seeds; 25 200 unique (arm, cell, seed) keys; 0 missing, 0 extra, 0 duplicates |
| Seeds | exactly 2229000–2229399, shared by all 21 arms; per-row 64 training-case indices equal `default_rng([seed,0]).choice(1331,64)` for every row (pairing enforced, not assumed) |
| Settings | cap 524 288, pop 256, phase `fresh_holdout` on all 25 200 rows; every unsolved row has `evaluations == cap` |
| Map identity | every row's `table_hash` equals the frozen hash in `config.json`; the 20 stage-1 maps and G4 (`8a7b3091…`) hash-verified against stage-1 source files (`source_hashes_verified`, `map_hashes_verified`, `vector_tables_verified` all true) |
| Cells | only the three holdouts; `training_holdout_disjoint` true; `no_learning` true; the queue produced no training or learning rows |
| G4 solve gate (≥ 85 %) | BE `S?m:(M+F)` 385/400 (96.3 %), PA `(F?S:M)+m` 377/400 (94.3 %), PA `(S?M:m)+F` 398/400 (99.5 %) — all pass |
| Runtime | wall 2 091 s (35 min), mean 0.83 s/search, stop reason none; no deadline truncation |
| Failures | 0 errors, empty `stderr.log`, exit 0 |

Unsolved rows (cost = cap): 299/25 200 (1.2 %): G4 40, BE maps 129, PA maps 130.

One caveat carried from the smoke: seeds 2229000–2229001 were touched once at cap 8 192
during the first infrastructure smoke. Maps are frozen and nothing was selected on them, so
no inference can have adapted; it only limits a literal "every seed wholly unseen" claim.

Both stated outputs of the run were used; nothing was dropped or re-weighted. The 50-seed
stage-1 training rows (10 500, hash-verified) enter only the descriptive transfer-loss
comparison.

## 2. Key numbers

Metric: per map and cell, the mean over the 400 shared seeds of log2(T_G4 / T_map), T = cap
when unsolved. Trajectory (map) is the unit, n = 10 per family. Intervals are 95 % t
(one-sample within an arm) or Welch (between arms). Ratios are 2^(mean log2).

### Readout 1 — generic transfer over G4 (6 estimates)

| Arm → holdout | Gain over G4 | 95 % CI | Label |
|---|---:|---|---|
| BE maps → BE `S?m:(M+F)` (matched) | 2.01× | [1.86, 2.18] | L |
| BE maps → PA `(F?S:M)+m` | 2.29× | [2.12, 2.48] | L |
| BE maps → PA `(S?M:m)+F` | 2.92× | [2.68, 3.18] | L |
| PA maps → BE `S?m:(M+F)` | 1.97× | [1.63, 2.39] | L |
| PA maps → PA `(F?S:M)+m` (matched) | 2.09× | [1.74, 2.51] | L |
| PA maps → PA `(S?M:m)+F` (matched) | 2.93× | [2.42, 3.55] | L |

Aggregates: BE maps on the two PA holdouts 2.59× [2.41, 2.77]; PA maps on the two PA
holdouts 2.48× [2.07, 2.96]. All six arm × cell gains are L. Per-seed, a learned map beats
G4 on 67–75 % of seeds depending on arm and cell.

### Readout 2 — crossed contrasts (primary)

| Contrast | Matched / mismatched | 95 % CI | Flags |
|---|---:|---|---|
| C_BE: BE − PA maps on BE `S?m:(M+F)` | 1.02× | [0.835, **1.2485**] | not W; B (upper < 1.25 by 0.0015) |
| C_PA: PA − BE maps, per-map mean of two PA holdouts | 0.96× | [0.79, 1.15] | not W; B |
| PA `(F?S:M)+m` alone (descriptive) | 0.91× | [0.75, 1.11] | not W; B |
| PA `(S?M:m)+F` alone (descriptive) | 1.00× | [0.82, 1.23] | not W; B |

Neither direction resolves a matched advantage; neither resolves a reversed one (no upper
bound below 1). On PA `(F?S:M)+m` the point estimate favours the *mismatched* (BE) maps.

### Readout 3 — within-map interaction (secondary)

I = 0.98× [0.83, 1.15] (log2 −0.033, Welch df 16.5). Not W; upper bound below 1.25. Pooled
over both directions, no family information is detected reaching the withheld cells.

### Readout 4 — damage check

Not applicable (no W direction). For the record, both mismatched arms improve on G4 on the
other family's holdouts (1.97× and 2.59×, both L), so no harm is visible at the arm level.

### Readout 5 — descriptive

- **Transfer loss** (own stage-1 training gain minus own-family holdout gain, mixed seed
  blocks: 50 vs 400): BE 1.08× [0.96, 1.22]; PA 0.92× [0.86, 0.98]. BE maps keep about
  their training gain on the BE holdout (2.18× → 2.01×); PA maps gain *more* on the PA
  holdouts than on their training cells (2.27× → 2.48×). This is descriptive; read no test
  into it.
- **Solve counts** (of 400 per map × cell): BE maps 385–397 on the BE holdout, 389–397 on
  PA `(F?S:M)+m`, 397–400 on PA `(S?M:m)+F`. PA maps 373–399, 382–400, 399–400. Family
  totals per cell, of 4 000: BE 3 937 / 3 938 / 3 996; PA 3 947 / 3 927 / 3 996. G4: 385 /
  377 / 398.
- **Shortcuts.** 259/25 200 rows produced at least one training-perfect program that failed
  the exact 1 331-input check; 258 of those rows were nonetheless solved by a true solution,
  so no shortcut was counted as a solve. Per map × cell, 0–12 such rows out of 400. One row
  (PA1 on PA `(S?M:m)+F`) cycled through ~180 k distinct false positives before solving.
- **Per-map rows** are in `result.json` → `per_map`. PA9 is the weak trajectory already
  visible in stage 1 (training gain 1.39×): on the BE holdout it is the only map with a
  negative gain (0.94×, log2 −0.097) and it solves 373/400 there. It alone carries most of
  the PA arm's between-map spread (PA arm sd 0.39 log2 vs BE arm 0.16 on the BE cell).
- **Seed noise after 400 seeds.** Per-map seed standard error is 0.11–0.13 log2 on every
  cell, against between-map sd of 0.16–0.17 (BE arm) and 0.37–0.39 (PA arm). The 400-seed
  choice did what the proposal intended: the BE arm's spread is now close to its noise
  floor; the PA arm's spread is mostly real (PA9).

Figures (this folder): `holdout_gains_per_map.png` (per-map dots with arm means and
intervals, plus the stage-1 training gains for scale), `crossed_contrasts.png` (the five
contrasts against 1 and the 1.25× margin). The run's own `holdout_solves.png` shows the
BE-arm and PA-arm solve curves lying on top of each other on all three cells, well left of
G4.

## 3. What the data shows

1. **Generic transfer is real on these three cells.** Every learned arm beats G4 on every
   holdout with lower bounds ≥ 1.63×, and the magnitude (2.0–2.9×) matches or exceeds the
   stage-1 training gains (2.2–2.3×). Token-only learning on four or six training cells of
   one family did not overfit to those cells in any way these holdouts can detect.
2. **No matched-family advantage is visible.** Both directional contrasts and the
   interaction sit within 0.04 log2 of zero with upper bounds at or below 1.25×. The
   in-sample point estimates from stage 1 (1.13× and 1.10×) did not reappear on the
   holdouts; on one PA cell the sign is reversed (unresolved).
3. **Cell identity dominates arm identity.** Both arms gain 2.9× on PA `(S?M:m)+F` and about
   2.0× on the BE cell. Which family trained the map shifts the gain by a few percent at
   most; which cell is being searched shifts it by 50 %.

## 4. What the data does not show

- **It does not establish equality or absence of a family preference.** A true 1.1×
  preference (the stage-1 in-sample size) is inside every interval here. B is a bound on
  the matched advantage, not a null.
- **The B label on C_BE is at the margin.** The upper bound is 1.2485 against a 1.25
  threshold (0.0017 log2). Leave-one-map-out: removing any one of 14 of the 20 maps moves
  the upper bound above 1.25 (to 1.25–1.30), flipping the rule from row 4 to row 5b.
  Removing PA9 moves C_BE to 0.94× [0.86, 1.03]. A pooled-variance t instead of Welch gives
  [0.84, 1.24]. The pre-stated rule is met and the label stands, but no decision should
  rest on the difference between "B in both directions" and "B in one, X in the other": the
  substantive reading is identical (generic transfer, direction unresolved).
- **One BE cell.** The BE direction is a single task; nothing here generalises beyond it.
- **Three screened cells.** The holdouts were screened by the bank and the G4 calibration;
  they are not a random sample of D1331 cells.
- **Transfer loss is cross-block.** Training gains are 50-seed stage-1 rows, holdout gains
  400 new seeds; the PA "negative loss" is suggestive of easier holdouts, not evidence of
  anything about the maps.
- **Mechanism.** Whether the generic gain is a better token prior for this reducer family
  as a whole, or a G4-weakness correction, cannot be separated with these arms; a
  union-trained or scrambled-family arm would be needed.
- **Hand-supplied context, token weights only**, as in stage 1.

## Against the predictions

Plan.md, read after sections 1–4 were written, fixes the ordered rules with the critic's
corrections: row 3 reads "holdout improvement unresolved", row 4 reads "matched advantages
below 1.25 at these intervals; approximate equality/generic transfer is not established by
B alone", reversed preferences are retained, and the interaction is reported in every row.
Applying the rules in order:

- **U**: no. Validation passed, 25 200/25 200 rows, no learning or training jobs, G4 solved
  94–100 % on every holdout (gate 85 %).
- **Rows 1–2**: no. Neither C_BE nor C_PA is W (lower bounds 0.835 and 0.79).
- **Row 3**: no. All six arm × cell gains are L.
- **Row 4**: yes. C_BE upper bound 1.2485 and C_PA upper bound 1.15 are both below 1.25.
  Reversed-preference flag false in both directions (no upper bound below 1). Interaction
  reported: 0.98× [0.83, 1.15], not W. Resolved G4 gains: all six. Outcome **row 4**.

Plan.md's prediction was "row 5, mostly 5b; anticipated gains 1.6–2.0× and directional
preferences about 1.1×, unresolved at n = 10" (proposal: row 5 at 55 %, row 4 at 10 %).

- **Row.** The data matched row 4, not the predicted row 5b, and did so by 0.0015 on C_BE's
  upper bound. The proposal projected a C_BE half-width of 0.35–0.45 log2, which would have
  made B unreachable unless the point estimate sat near 1; the observed half-width is 0.29
  and the point estimate is 1.02×, so both conditions for B happened. Section 4 shows the
  label is not robust to removing any one of 14 maps. The substantive conclusion of row 4
  and the predicted 5b are the same here: generic transfer resolved, matched preference
  unresolved, with both directions now bounded at about 1.25×.
- **Generic gains.** Predicted 1.6–2.0×, L on all six. Observed 2.0–2.9×, L on all six. The
  direction was right; the size was underestimated. The proposal's premise that holdouts keep
  about three quarters of the training log-gain did not hold: BE kept about 93 % on its one
  holdout and PA exceeded its training gain.
- **Directional preferences.** Predicted C_BE 1.1–1.2× and C_PA 1.05–1.15×, both X.
  Observed 1.02× and 0.96×, both B. The stage-1 in-sample estimates (1.13×, 1.10×) did not
  reappear on the withheld cells.
- **Future sizing.** Plan.md projected, from the proposal's half-widths, BE 60–100 per
  family for interval-width sizing, PA 20–33, interaction 32–60, with detection about twice
  that. The report's numbers from observed variances are BE 38, PA 33, interaction 27 for
  width and BE 75, PA 64, interaction 53 for 80 % detection of a true 1.1×. BE came in
  below the plan's range because the BE arm's holdout spread (sd 0.16 log2) is smaller than
  the training-cell spread the proposal extrapolated from; PA is at the top of its range
  because PA9 inflates the PA arm variance. At 10–14 min per trajectory, the detection
  designs cost roughly 14–30 h of learning plus 2–6 h of holdout evaluation. With both
  holdout point estimates within 0.07 log2 of zero, that spend would most likely buy a
  tighter bound around 1, not a detection. That is the strategist's call; the data here do
  not argue for it.
