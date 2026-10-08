---
outcome: resolved_relative_gain
---

# Analysis: 2026-10-08-1548 frozen C/T on then-addition-v1 (row F) and v1 holdouts (row D)

Reviewer analysis of the queue run at commit `45b2bdb` (outputs
`experiments/output/2026-10-08/2026-10-08-1548-fresh-then-addition/` and
`…/2026-10-08-1548-development-holdouts/`). Every number below was recomputed from
`search.jsonl`; the primary endpoints, intervals, per-cell and per-family values agree with
both `result.json` files to three decimals. Plots: [ct_rows.png](ct_rows.png) (per-corpus
C/T for training, row D and row F side by side, and pooled solve curves) and
[ct_per_cell_fresh.png](ct_per_cell_fresh.png) (row F per cell with solve counts).

## 1. Data completeness

Complete. Both rows ran their full frozen rosters, nothing was skipped or duplicated, no
search failed, and the queue exited 0.

| row | rows | expected | C | T | G4 | wall | timeout | stop |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| F then-addition (fresh) | 4 352 | 4 352 | 2 048 | 2 048 | 256 | 4 171 s (70 min) | 14 400 s | none, 8/8 pairs |
| D v1 holdouts (development) | 4 352 | 4 352 | 2 048 | 2 048 | 256 | 3 143 s (52 min) | 12 600 s | none, 8/8 pairs |

- Zero duplicate (phase, family, corpus, cell, arm, seed) keys in either row. Row F: every
  corpus × cell has exactly 8 C and 8 T seeds; every cell has 16 G4 seeds. Row D: 16 C/T
  seeds per corpus × cell, 32 G4 per cell.
- The executed rows equal the frozen rosters in both files. Row D's roster is identical,
  row for row, to the 4 352 `phase == holdout` rows of 1246's `schedule.json` (same corpus,
  cell, arm and seed), so it is the unchanged stage-2 roster frozen in 1246.
- Every C/T pair shares its seed and an identical 64-case training draw (2 048/2 048 pairs
  per row). No seed is shared between corpora or between G4 and C/T; row F's seed block is
  disjoint from row D's and from 1246's 5 376 source searches.
- One table hash per (arm, corpus) in each row; all 48 frozen table hashes (C/T/K × 16)
  validated against 1246's `freeze.json` and `corpora.json`; the five source files hash to
  the 1246 originals. No re-encoding, no refit, K never scored.
- Fresh bank: 16 cells, SHA `26be2d56…` pinned in code; all 16 use gate F>m or M>F; maximum
  agreement with any v1 behaviour 0.78, with no exact alias of the 1603 bank. The bank was
  built from the semantic screen alone; no search touched it before the queue.
- `solved` means exact on all 1 331 inputs. Cap 524 288 and P 256 in every row; every
  unsolved search sits exactly at the cap.
- Timing came in close to the proposal's training-difficulty projection (66 min per row):
  F took 70 min, D 52 min. Mean worker seconds per search were C 7.1, T 11.2, G4 13.5 on F
  and C 4.5, T 8.9, G4 12.0 on D.

## 2. Key numbers

Speed ratio = exp(mean over corpora of mean over cells × paired seeds of
log cost_T − log cost_C); > 1 means C solves sooner. Unsolved = 2 × cap unless stated.
n = 16 corpora (8 BE-fitted, 8 PA-fitted), t interval on 15 df.

| contrast | row F: then-addition (16 fresh cells) | row D: v1 holdouts (8 cells) | 1246 training (own-family cells, for reference) |
|---|---|---|---|
| C/T, 2 × cap (primary) | **2.12 [1.86, 2.41]** | **2.60 [2.31, 2.92]** | 3.11 [2.78, 3.48] |
| C/T, 1 × cap | 1.96 [1.75, 2.21] | 2.44 [2.19, 2.71] | 2.82 [2.52, 3.14] |
| C/T, both-solved pairs only (uncensored) | 1.74 [1.53, 1.98] | 2.11 [1.89, 2.34] | — |
| BE-fitted corpora (8) | 2.49 [2.18, 2.83] | 2.76 [2.31, 3.30] | 2.86 [2.56, 3.20] |
| PA-fitted corpora (8) | 1.81 [1.52, 2.15] | 2.45 [2.02, 2.96] | 3.37 [2.74, 4.16] |
| BE − PA source-family ratio | 1.38 [1.13, 1.68] | 1.13 [0.89, 1.43] | — |
| corpora with C/T > 1 | 16/16 | 16/16 | 16/16 |
| corpus × cell with C/T > 1 | 220/256 | 121/128 | 64/64 |
| cells with point C/T > 1 (LB > 1) | 16/16 (14/16) | 8/8 (8/8) | 8/8 |
| leave-one-cell-out range | 2.05–2.19 | 2.49–2.80 | — |
| C/G4, T/G4 (descriptive, unpaired) | 3.89, 1.83 | 4.86, 1.87 | 5.77, 1.86 |
| per-corpus sd (log) | 0.243 | 0.221 | 0.212 |

Solve counts and censoring:

| row | C solved | T solved | G4 solved | C at cap | T at cap | pairs both / C only / T only / neither |
|---|---:|---:|---:|---:|---:|---|
| F | 1 771/2 048 (86.5%) | 1 547/2 048 (75.5%) | 162/256 (63.3%) | 13.5% | 24.5% | 1 353 / 418 / 194 / 83 |
| D | 1 924/2 048 (93.9%) | 1 736/2 048 (84.8%) | 196/256 (76.6%) | 6.1% | 15.2% | 1 640 / 284 / 96 / 28 |

The 25% shared low-solve guard is far from triggered in either row. Among pairs both arms
solved, the median T/C evaluation ratio is 1.90 on F (C faster in 64.4% of 1 353 pairs) and
2.25 on D (68.1% of 1 640). Median evaluations to an exact solve, solved runs only: F C
44 800, T 82 944, G4 145 408; D C 29 696, T 64 896, G4 117 760. The effect is a broad shift
of the whole solve curve (right panel of [ct_rows.png](ct_rows.png)), not a few capped T
runs; the uncensored both-solved estimate stays at 1.74× on F.

Shrinkage from training (secondaries, ratio of ratios):

- F versus each corpus's own-family training C/T: 0.68 [0.57, 0.81]. The fresh-bank gain is
  about a third smaller than the training gain and that reduction is resolved.
- D (pooled holdouts) versus own-family training: 0.84 [0.70, 1.00]; D own-family holdouts
  versus own-family training: 0.88 [0.72, 1.07]. Within-shape shrinkage is small and not
  resolved from 1.
- D matched-family versus mismatched-family holdouts: 2.72 [2.35, 3.16] versus 2.48 [2.10,
  2.92], ratio 1.10 [0.89, 1.35]. No detectable family-matching effect within the shape.

Row F per cell ([ct_per_cell_fresh.png](ct_per_cell_fresh.png)): point C/T ranges from 1.28
(`F>m?M+S:S`, interval [0.85, 1.92]) to 3.46 (`M>F?S+m:m`, [2.41, 4.97]); 14/16 cells have a
lower bound above 1. The nine F>m cells average lower (1.28–2.35) than the seven M>F cells
(2.05–3.46), but with 16 corpora × 8 seeds per cell the per-cell intervals are wide and this
split was not pre-registered. Every cell keeps the ordering C solves ≥ T solves ≥ G4 solves
except `M>F?M+m:S`, where G4 (13/16) edges T (100/128) in cost (T/G4 0.97).

## 3. Checks for shortcut or artefact explanations

- **Capped endpoint.** Not the driver. The 1 × cap sensitivity (1.96) and the uncensored
  both-solved estimate (1.74) both keep the lower bound well above 1 on F; worker seconds
  per corpus show the same direction (T/C 1.60 on F, 1.99 on D).
- **Training-perfect shortcuts.** Solves require exactness on all 1 331 inputs. Among
  unsolved searches on F, only 9 C and 7 T runs ever produced a training-perfect individual,
  so no capped run is a near miss counted either way. Descriptively, C encounters far more
  training-perfect-but-inexact programs per search on F (mean 1 268) than T (543) or G4
  (9); the then-addition bank is rich in tie-level variants that agree on most inputs, and C
  steers populations into that neighbourhood. This does not inflate the endpoint, but it
  means C's edge on this bank is partly "finds the right shape, then has to discriminate
  near-aliases".
- **Arm wiring and leakage.** Table hashes, seed pairing and roster identity are verified
  above; the search payload carried only cell ids and labels. The G4 baseline is unpaired
  and not replicated per corpus, so C/G4 and T/G4 are descriptive only.
- **Bank difficulty.** G4 solved 63% of fresh searches at the cap, between the 1246 training
  (68%) and row D (77%) rates, so the fresh bank is of comparable difficulty for the
  hand-set baseline and there is headroom on both sides.

## 4. What the data shows

- On the frozen, semantically selected then-addition bank, the context fit C solves fresh
  searches about 2.1× sooner than the token-only fit T to the same solver tapes (95%
  interval 1.86–2.41, 16/16 corpora, 220/256 corpus × cells, 14/16 cells individually
  resolved, robust to the cap penalty). The advantage of C over the restricted T procedure
  survives a bank of a new shape at this procedure's scope.
- The gain shrinks from training: 3.11× on own-family training cells, 2.60× on the
  within-shape holdouts, 2.12× on the cross-shape bank. The within-shape shrinkage (0.84–0.88)
  is not resolved from 1; the cross-shape shrinkage (0.68 [0.57, 0.81]) is.
- Both fitted maps beat G4 descriptively on both rows (C/G4 3.9 and 4.9; T/G4 1.8 and 1.9), so
  this is not C beating a damaged T, and the token fit itself transfers about 1.8×.
- Row D answers question 25 on its own terms: within the development bank, C beats T on all
  eight protected holdouts (2.60× [2.31, 2.92]), with no detectable family-matching effect.
- BE-fitted tables transfer better to then-addition than PA-fitted ones (1.38× [1.13,
  1.68], 8 vs 8 corpora, secondary). In training the order was the reverse (PA 3.37 versus
  BE 2.86), so the PA tables lose about half their advantage on the new shape while the BE
  tables lose less.

## 5. What the data does not show

- **One bank, chosen after seeing v1.** The bank is semantically selected, but it was
  designed after v1 results and consists of 16 cells on just two tie-heavy gates (F>m, M>F).
  The corpus interval conditions on these 16 fixed cells; a cell × arm interaction common
  to all corpora is not sampled. This is transfer to one new shape, not to arbitrary shapes.
- **Why the gain shrinks** is not identified. Branch placement, gate selection and the
  bank's near-alias density all changed together; the proposal's explanation B (shape
  specificity) is not supported as the sole story, since 2.1× remains, but the 0.68 shrinkage
  is consistent with partial shape dependence.
- **No isolated token-order mechanism.** K was not scored; C/T compares two fitting
  procedures with different emitted token frequencies.
- **No uncapped speed claim.** The endpoint is capped at 524 288 evaluations; 24.5% of T
  searches on F hit the cap. The uncensored both-solved estimate (1.74×) is the conservative
  reading.
- The source-family contrast (BE ahead on F) and the F>m-versus-M>F cell pattern are
  secondary and post hoc respectively; neither was a pre-registered primary.
- G4 is unpaired, so C/G4 and T/G4 carry no interval that includes G4 sampling uncertainty.

## Against the predictions

Plan read after sections 1–5 were written.

- **Primary rule (row F).** Plan: completeness and error eligibility first, then the shared
  <25% censoring flag, then the ordered numerical rule; LB > 1 means a resolved relative C/T
  gain on the frozen selected new-shape bank, with "also below 10%" only if UB < 1.10.
  Observed: 8/8 pairs complete with no error, C 86.5% and T 75.5% solved (flag not raised),
  LB 1.86 > 1 and UB 2.41 > 1.10. The data match the plan's first label, `resolved relative
  gain`, which is also the report's own route (`resolved_relative_gain`). The "bounded below
  10%" branch and the "unresolved, price extra corpora" branch do not apply; the report's
  sizing block correctly prices zero extra corpora for the observed effect.
- **Row D and the joint reading.** Plan: D positive with F positive "supports reuse of corpus
  information at this method/bank scope"; D positive with F bounded would be a boundary on
  the selected F>m/M>F behaviours. Observed: both rows positive (2.60× and 2.12×), so the
  joint reading is the former. The plan's caveat that branch placement, gate selection and
  behaviour distribution are not separated stands, and is now needed to explain the resolved
  0.68 cross-shape shrinkage rather than a boundary.
- **Size.** The proposal expected a fresh C/T of about 1.3–2×, below row D, with BE-fitted
  tables slightly ahead. Observed 2.12× [1.86, 2.41] sits at the top of that range, below row
  D's 2.60× as expected, and BE-fitted corpora lead PA-fitted by 1.38× [1.13, 1.68], a larger
  source-family gap than "slightly". Neither named surprise occurred: fresh C/T is not below
  1.10 while D stays large, and shrinkage from training is present and resolved (0.68).
- **Precision.** The proposal budgeted a per-corpus sd of 0.30 log and a ×1.17 half-width.
  Observed sd is 0.243 (F) and 0.221 (D), half-widths ×1.14 and ×1.12, so the 16-corpus
  design was adequately sized and resolved a true effect well above the 1.3× it was built
  to detect.
- **Execution rules.** G4 ran first, then the eight fixed BE/PA pairs in order; no trailing
  rows, no fallback, no stop reason. Row D is the unchanged 1246 holdout roster, confirmed row
  for row against the source schedule. Runtime (70 and 52 min) was close to the plan's
  historical 135 min total.
- **Censoring and G4 qualifications.** The plan asks that solve counts always accompany the
  ratio and that "above 25% does not make censoring harmless". Section 2 reports them; the
  1 × cap (1.96) and both-solved-only (1.74) estimates show the capped tail inflates the F
  ratio by roughly 10–20% but not its direction or resolution. Both fits beat G4
  descriptively, so the plan's "relative superiority without useful adaptation" case does not
  apply.
- **Secondaries the plan listed.** All are reported in section 2: per-cell intervals and
  leave-one-cell-out range (2.05–2.19), F source-family BE − PA, D matched − mismatched (1.10
  [0.89, 1.35], unresolved), D own-family holdout − training shrinkage (0.88 [0.72, 1.07],
  unresolved) and F − training shrinkage (0.68 [0.57, 0.81], resolved). K unscored; token
  order not isolated; the corpus interval conditions on this selected bank. The analysis keeps
  that scope.
- **For question 26's explanations.** A (C carries assembly preferences reusable on a new
  arrangement of the same primitives) is supported at this scope. B (gain specific to the
  fitted shapes, bounded under 1.10×) is ruled out on this bank. B' (within-shape but not
  cross-shape transfer) is ruled out in its strong form, but the resolved shrinkage from 2.60×
  to 2.12× means a shape-dependent component is consistent with the data.
