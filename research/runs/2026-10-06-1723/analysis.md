---
outcome: 4
---
# Analysis — 2026-10-06-1723 (crossed BE/PA token-multiplier learning, stage 1, training only)

Reviewer: Claude (Fable 5.1), independent of the researcher. Inputs: proposal.md, queue.yaml,
execution.md, code at `db96645`, and the run folder
`experiments/output/2026-10-06/2026-10-06-1723-crossed-family-training/`. Every headline
number below was recomputed from `fresh_scores.json`, `trajectories.json` and
`generations.jsonl` with my own script; it agrees with the run's `result.json` to all printed
digits. plan.md was not read until the section "Against the predictions". Figures saved in
this folder: `per_cell_gains.png`, `own_off_and_curves.png`, `token_multipliers.png`.

## 1. Data completeness

Complete. Nothing is missing, duplicated, truncated or failed.

| Check | Result |
|---|---|
| Queue entry | 1/1 done, exit 0, wall 15 394 s (4.28 h) of a 28 800 s timeout; internal deadline 27 000 s never approached; `stop_reason` null; `stderr.log` empty |
| Expected outputs | 12/12 present |
| Validation | frozen bank SHA256 and G4 hash verified; D1331 labels verified; training/holdout labels disjoint; holdout roles covered; search payloads carry only `id` and `labels` |
| Holdout exposure | zero. `search.jsonl` contains exactly the ten training cells (BE cells 26 790 rows each, PA cells 18 210 each); no holdout cell ID and no probe rows |
| Raw searches | 216 420 rows = 193 920 learning (20 trajectories × (4 + 25 × 16) candidates × 24) + 12 000 selection (20 × 5 maps × 120) + 10 500 fresh (21 maps × 10 cells × 50 seeds). All three counts match the design exactly |
| Trajectories | 10 BE + 10 PA, outer seeds 1723200–1723219 as configured, 26 generation records each, 20 distinct final table hashes |
| Admission | all 10 pairs admitted (`schedule.json`); the early gate never fired (first four selection gains 1.35, 1.62, 1.80, 0.78 log2 against a threshold of 0.14) |
| Fresh scoring | 10 500 rows, 0 duplicates, 0 missing, 0 extra; one cap (524 288); one phase; table hash matches G4 or the saved map for every row; training-case indices identical across arms for every cell × seed (report's pairing check, 0 errors) |
| Shortcut solutions | a "shortcut" is an individual perfect on the 64 training cases that fails the exact 1 331-input check; it is never credited as a solve. 1–3 % of fresh searches per arm saw at least one; G4's high mean count (485 per search) is one run with 227 336 sightings on `(S?M:F)+m`. Solve counts are not inflated |

Seeds: inner `outer × 10 000 + gen × 100 + j`, selection `outer × 10 000 + 5 000 + j`, fresh
1723300–1723349 shared by all 21 maps. No block overlaps within or across trajectories and
none overlaps 1603's seed blocks.

**Cost.** Trajectories took 572–822 s each (9.5–13.7 min, mean ≈ 11.8 min); pairs
1 305–1 629 s; learning 236 min in total; fresh scoring about 20 min wall (mean 1.02 s per
full-cap search on 10 workers). CPU efficiency 9.5 of 10 workers. The proposal's 12–14 min
per trajectory and the researcher's 345 min total were both slight overestimates; the
strategy's 35–70 min per trajectory was a 3–6× overestimate.

## 2. Primary readouts (trajectory as unit, n = 10 per family, 95 % t intervals)

Per map and cell the gain is the mean over 50 shared seeds of log2(T_G4 / T_map), T = evaluations
to an exact solve or 524 288 if unsolved; cells are averaged with equal weight within a
training set. Ratios are 2^(mean log2).

| Readout | BE-trained maps | PA-trained maps |
|---|---|---|
| **Own-family training gain over G4** (primary) | **2.18× [1.98, 2.40]**, label **L** | **2.27× [1.95, 2.65]**, label **L** |
| per-trajectory own gains | 1.70–2.65×, 10/10 above 1 | 1.39–2.84×, 10/10 above 1 |
| between-trajectory sd of own gain (log2) | 0.19 | 0.31 |
| Off-family training gain over G4 (descriptive) | on PA cells: 2.07× [1.94, 2.21] | on BE cells: 1.93× [1.61, 2.30] |
| **Crossed contrast on that family's cells** (secondary; Welch) | BE-trained over PA-trained on BE cells: **1.13× [0.93, 1.37]**, label **X** (df 13.9) | PA-trained over BE-trained on PA cells: **1.10× [0.93, 1.29]**, label **X** (df 12.0) |

Solves at the 524k cap: G4 480/500 (BE cells 185/200, PA cells 295/300); learned maps
481–499/500 each. The gains are mostly speed, not rescue of unsolved runs.

**Per cell** (mean log2 gain over G4, BE-trained arm vs PA-trained arm, `per_cell_gains.png`):

| Cell | BE-trained | PA-trained | BE − PA |
|---|---|---|---|
| BE F?S:(M+m) | 1.72 | 1.33 | +0.38 |
| BE F?m:(S+M) | 0.66 | 0.42 | +0.24 |
| BE S?F:(M+m) | 0.58 | 0.51 | +0.07 |
| BE S?M:(m+F) | 1.54 | 1.52 | +0.02 |
| PA (F?S:m)+M | 1.42 | 1.54 | −0.12 |
| PA (F?m:M)+S | 1.23 | 1.21 | +0.02 |
| PA (F?m:S)+M | 0.65 | 0.66 | −0.02 |
| PA (S?M:F)+m | 1.28 | 1.43 | −0.14 |
| PA (S?m:F)+M | 0.90 | 1.26 | −0.35 |
| PA (S?m:M)+F | 0.83 | 1.00 | −0.17 |

The sign favours the matched arm on 4/4 BE cells and 4/6 PA cells, with the other two PA cells
tied (|diff| ≤ 0.02). Within-arm sds per cell are 0.17–0.53 log2, so no single cell's contrast
is resolved on its own (SE about 0.19 log2 per cell).

**Exploratory, not pre-registered: the within-map interaction.** Each map's own-minus-off
difference removes its generic quality; the Welch contrast of that difference between the two
arms is the sum of the two crossed log2 contrasts:
1.24× [1.09, 1.41] (log2 0.31, df 18). BE maps' (BE − PA) differences: +0.15, +0.40, +0.02,
+0.07, +0.04, −0.11, +0.28, +0.21, −0.20, −0.13; PA maps': −0.35, −0.54, −0.06, +0.01, +0.03,
−0.26, −0.22, −0.23, −0.25, −0.51. Read this as "the two in-sample preferences are jointly
unlikely to both be zero", not as a per-direction result; the pre-stated per-direction
contrasts are X, and this pooled estimate was chosen after seeing the data.

## 3. Descriptive measures

**Learning dynamics** (`own_off_and_curves.png`, right). Mean best-parent in-loop score falls
from 13.9 (BE) / 14.0 (PA) at generation 0 to 12.4 / 12.5 at generation 25, and is still
falling slowly over generations 10–25 (BE 12.93 → 12.41, PA 13.10 → 12.48). On average 2.9 of
the 4 parent slots are replaced by children every generation, which with the rank statistics
below is mostly noise-driven churn rather than steady improvement.

**Repeatability.** The within-generation Spearman between a parent's previous and rescored
24-search score has median 0.20 (BE) and 0.00 (PA) over 242 defined values per family: a
24-search score barely ranks four parents consistently. The 120-seed selection score does
predict fresh performance: Spearman between the selected map's selection score (lower is
better) and its fresh own-family gain (higher is better) is −0.45 (BE) and −0.83 (PA), i.e.
concordant. Final in-loop score vs fresh gain: −0.27 (BE), −0.73 (PA). Selection gains
(0.77–1.80 log2, 65k cap, best-of-4) run about 0.3 log2 above fresh own gains (0.48–1.51),
the expected in-sample optimism.

**Outliers.** PA9 is the weakest map on both cell sets (own 1.39×, off 1.17×; selection gain
0.77 log2). PA2 is ordinary on PA (1.98×) but weak on BE (1.36×). BE9 is the weakest BE map
(1.70× own, 1.95× off). Removing PA9 and PA2 would not change any label.

**Parameter divergence** (`token_multipliers.png`). Distance between the two families' mean
log-multiplier vectors is 1.46 against within-family RMS spreads of 2.62 (BE) and 2.89 (PA);
ratio 0.53, permutation p = 0.20 (10 000 permutations, exploratory). Both families make the
same large moves: INPUT (token 1) +1.45 in both, positive in 20/20 maps; IF_GT (17) +0.72 /
+0.55, positive in 18/20; REDUCE_ADD (11) +0.66 / +0.75; DUP (9) −0.77 in both, negative in
17/20; CHARS (4) −0.67 in both; ANY (6) −0.42 in both. The largest family differences (BE
minus PA, natural log) are NOP (0) −0.60, SWAP (10) −0.60, REDUCE_MAX (18) −0.58, FIRST (23)
−0.52, SUM (5) +0.48, REDUCE_MIN (22) −0.37; each is about one within-family sd, so none is
individually resolved. The direction is readable (PA maps raise the list reducers MAX, MIN and
FIRST; BE maps raise SUM and ADD) but descriptive only.

**Stage-2 sizing proxy** (pre-stated rule). s_off = median over ten cells of
sqrt((s_BE² + s_PA²)/2) = 0.355 log2 (BE cells 0.447, PA cells 0.306). Half-width
t(0.975, 2n − 2) · s_off · √(2/n): n = 10 → 0.334, 14 → 0.276, 18 → 0.241; all meet the
0.50 target, so the rule selects **n = 10 per family, no extension**. Using the BE-cell median
alone (the single BE holdout is a BE cell) gives 0.42 at n = 10, still under target. The
realised crossed half-widths on the training sets, 0.28 (BE) and 0.23 (PA) log2, are
consistent with the proxy. The proposal's s_off guess of 0.45–0.55 was high.

**Comparison with prior runs** (for scale, not tested here). 0132's M learner over G on its
own training cells was 2.23× [1.82, 2.75]; the same learner on G4 here gives 2.18× and 2.27×.
1603's hand-set grammars gave crossed preferences of 1.68× [1.39, 2.05] (BE) and
1.32× [1.12, 1.57] (PA) but G4-BE beat G4 by only 1.36× on BE and hurt PA (0.66×). The
learned maps are the opposite profile: about 2× on both families, with crossed preferences
near 1.1× that are not resolved.

## 4. What the data show and do not show

Shown:
- The token learner improves G4 on both frozen training sets, by about 2.2× in both, with
  every one of 20 independent trajectories above 1 and lower bounds near 2×. Both families
  are **L**.
- Almost all of that gain is generic: maps trained on one family speed the other family's
  training cells by 1.9–2.1×. The "damage" explanation (C in question 16) does not apply on
  training cells; neither arm hurts the other family.
- The in-sample crossed preferences are small and point the matched way in both families
  (1.13× and 1.10×), with intervals that include 1 and exclude neither 1 nor 1.25. Both are
  **X**. The sign is consistent across 8 of 10 cells, and a post hoc pooled interaction is
  1.24× [1.09, 1.41]; this is suggestive of some family information in-sample, nothing more.
- Learning cost is 10–14 min per trajectory at this scale; a 20-trajectory stage plus fresh
  scoring fits in 4.3 h.

Not shown:
- Anything about the three holdouts; they were not searched and no holdout seed exists.
- Whether the in-sample preference survives on withheld cells. In-sample, a matched arm can
  look better by fitting its own cells' idiosyncrasies; that is exactly what stage 2 tests.
- Learned context: G4's hand-set context is unchanged; only 24 column multipliers moved.
- Which tokens carry family information; the per-token differences are all within noise.
- Anything beyond these ten screened bank cells, D1331 and `v2_rmin_first`.

Outcome by the proposal's rules: both families L and both crossed contrasts X → **row 4**
(stage 2 at the size set by the rule, which is the achieved n = 10 per family).

## Against the predictions

plan.md (read after the sections above) implements the proposal without changing its outcome
rules; its own predictions are operational.

| Prediction (plan / proposal) | Observed | Verdict |
|---|---|---|
| Queue wall about 5.75 h (plan), 4.7–5.4 h (proposal); 345 min estimate | 4.28 h (257 min); learning 236 min, fresh scoring about 20 min | Faster than both; the 1.3× reserves were never binding and all 10 pairs were admitted |
| 17.8 (BE) / 13.1 (PA) min per trajectory at G4 speed, falling as maps improve | 9.5–13.7 min per trajectory, mean 11.8 | As predicted, at the fast end |
| Early gate would not stop real learning | Never fired; first four selection gains 0.78–1.80 log2 vs 0.14 threshold | As predicted |
| Fresh reserve about 2× conservative (code review note) | Reserved 1.88–2.32 s per search; observed 1.02 s | As predicted; harmless |
| Proposal prediction: row 4 | Row 4 | Matches |
| Both families L, 1.5–2.2× over G4 | BE 2.18× [1.98, 2.40], PA 2.27× [1.95, 2.65] | Matches; PA's point estimate is just above the predicted range |
| In-sample crossed contrasts 1.1–1.3×, X | 1.13× [0.93, 1.37] and 1.10× [0.93, 1.29], both X | Matches |
| Positive off-family gains, as M on BE (2.23×) | 2.07× [1.94, 2.21] and 1.93× [1.61, 2.30] | Matches |
| s_off about 0.45–0.55 log2, so n = 10 meets or nearly meets the size rule | 0.355 (BE cells 0.447, PA cells 0.306); n = 10 gives half-width 0.33 ≤ 0.50 | Spread lower than predicted; the rule selects n = 10 with no extension |
| Plan's interpretation rule: gains on both sets suggest generic adaptation; own gain plus off-family harm suggests specialization/damage | Gains on both sets in both arms; no off-family harm in any of 20 maps | Generic-adaptation reading applies on training cells |
| Plan: broad crossed intervals spanning 1 and 1.25 never establish generic transfer | Both crossed intervals span 1 and 1.25 | Correctly left unresolved; the post hoc interaction (1.24× [1.09, 1.41]) is suggestive and is reported as exploratory only |
| Plan: even good scores require pairing, leakage, clipping and degeneracy checks | Pairing 0 errors; no holdout rows; no vector at the ±ln 16 bound in any final map (max |v| = 2.4); no degenerate scores | Passed |

Critique notes 1–4 are implemented as the plan says (reserves from observed costs, ten
workers total, separate resolved/bounded flags, two-arm sizing proxy with per-family medians).
Notes 5–7 (wording in belief files) were left to the steward and remain open.

**Routing.** Row 4 → stage 2 at n = 10 per family: the frozen crossed holdout evaluation of all
20 saved maps plus G4 on the three holdouts at 200 fresh seeds each, plus fresh training, with
no additional trajectories. The precision proxy says a true 1.5× matched-over-mismatched
effect on one holdout cell would show a lower bound above 1 at this n; the training-cell
preference here is only about 1.1×, so stage 2 should be expected to bound rather than
resolve a per-direction preference unless the holdouts amplify it. The steward may want to
state in the stage-2 proposal what a 1.1–1.25× holdout preference would and would not mean
before the holdouts are scored.
