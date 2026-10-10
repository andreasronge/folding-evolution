---
outcome: "unresolved (replacement increment R = T/T ÷ T/D on DG 1.95 [1.43, 2.66] crosses the 1.5 margin; table-carried contribution resolved, B 3.26 [2.43, 4.30]; portable library activity resolved, T/∅ ÷ T/D 3.05 [2.32, 4.07]; no native D-library-identity advantage, D/T ÷ D/D 1.35 [1.10, 1.68]; fresh native gap reproduced 3.03 vs 2.98; not penalty-sensitive; TS retention 1.01 [0.83, 1.25], no loss)"
---
# Analysis: table × library transplant (DG-built vs TS-built A8 components, 8 DG spare cells + 8 TS target cells)

Code commit `6dabda8` on `research/2026-10-10-2001` (clean tree). Data: `experiments/output/2026-10-10/2026-10-10-2001-component-prepare/` (validation, 16 native replays, 96 calibration searches, frozen preparation), `.../2026-10-10-2001-component-DG/` (2 304 DG target searches, DG-only `result.json`) and `.../2026-10-10-2001-component-TS/` (2 304 TS target searches, combined 4 608-row `result.json`, `report.md`, `dynamics.png`). Every number below was recomputed from the two `search.jsonl` files, `preparation.json` and the frozen builds in `experiments/chem_tape/data/component_transfer_2001/`; all agree with the runner's `result.json` to the printed precision, including an independent re-implementation of the pair × seed bootstrap (8 192 draws, different RNG seed: R 1.40–2.72 against the runner's 1.43–2.66).

Figure in this folder: `contrasts.png` — (a) the six arm costs on both rosters, (b) per-pair R against D library size, (c) per-cell R, G and B on DG. `recompute_per_pair.json` holds the per-pair table.

## 1. Data completeness

All three queue entries exited 0 inside their timeouts; every `expect_outputs` file is present.

| Entry | Wall | Timeout | Projection at admission | Effective workers (of 10) |
|---|---:|---:|---:|---:|
| prepare (validation, 16 replays, 96 calibration searches) | 142 s | 1 800 s | — | 8.6 (DG batch) |
| DG score (2 304 searches, bootstrap, plot) | 4 056 s | 9 000 s | 5 347 s ≤ 8 970 s | 9.96 |
| TS score (2 304 searches, combined report) | 1 148 s | 3 600 s | 1 735 s ≤ 3 570 s | 9.93 |

- **Provenance and freeze.** The 48 builds, banks, 1717 preparation and 16 historical native rows loaded with hash verification against the 1717 artifacts (`provenance.json`, commit `b5697a1`). Python/Rust/semantic validation passed (7 240 depth-3 programs, 10 000 random tapes, 708 canonical and witness cells). All 16 native replays matched the 1717 rows bit-exact excluding timing fields. The donor permutation (seed 2001) is a bijection on 0–23; I checked every row's `table_build` and `library_build` against it (D component = pair index, T component = π(pair)): 4 608/4 608 correct.
- **Admission.** Price-only gate, both families admitted; actual scoring time was 75 % (DG) and 62 % (TS) of the projection. The code review's worry that TS calibration under-predicts the protected targets did not bite.
- **Scoring rows.** 2 304 rows per family = 8 cells × 24 pairs × 2 repeats × 6 arms; no duplicates, no missing or extra keys, no `error` fields, cap 524 288 and population 256 in every row. Seeds 2 100 000–2 107 047 (DG) and 2 108 000–2 115 047 (TS), 384 distinct per family, each shared by the six arms of its (cell, pair, repeat); disjoint from the 1717 target seeds, so D/D and T/T are fresh references.
- **Arm integrity.** Within every (cell, pair, repeat), the three arms sharing a table have identical `initial_tokens_hash` (768/768 groups per family). Both bare arms carry `operator_mode: off` and zero `block_events` in all 768 rows per family; every library arm has non-zero block events; no `empty_library_fallback`. 48 distinct table hashes and 48 distinct library hashes (plus the "none" digest) appear, as designed.
- **Failures.** Every unsolved row sits at exactly 524 288 evaluations; no solved row reached the cap. `solved` requires the exact check on all 625 inputs.
- **Shortcut tails.** Searches containing at least one training-perfect-but-wrong program: DG 21–34 of 384 per arm (D/D 24, T/T 34, T/D 33, D/T 32, D/∅ 22, T/∅ 21); TS 18–31 of 384. None passed the 625-input check. Exact verification cost 167 s of 40 203 worker-s on DG and 129 s of 10 714 on TS; the single largest check was 45 s (one TS D/D search). Nothing is distorted by verification cost.

Nothing is missing, duplicated or silently substituted.

## 2. The 2 × 3 table (both rosters)

Solves out of 384 (8 cells × 24 pairs × 2 seeds) and geometric capped cost over the 8 fixed cells (failures at 2 × cap, thousands of evaluations). Arm = table/library.

| Roster | D/D | T/T | **T/D** | D/T | D/∅ | T/∅ |
|---|---:|---:|---:|---:|---:|---:|
| DG solves | **312** (81 %) | 199 (52 %) | 264 (69 %) | 288 (75 %) | 291 (76 %) | 133 (35 %) |
| DG cost | **93 k** | 282 k | 145 k | 126 k | 135 k | 442 k |
| TS solves | 363 (95 %) | 363 (95 %) | **368** (96 %) | 365 (95 %) | 337 (88 %) | 353 (92 %) |
| TS cost | 25.8 k | 23.7 k | 24.0 k | 25.7 k | 51.3 k | 36.0 k |

Mean seconds per search on DG: D/D 11.7, T/T 22.4, T/D 16.2, D/T 14.6, D/∅ 13.6, T/∅ 26.2; on TS 3.6–6.9.

**The fresh native references reproduce 1717.** Native gap cost(T/T)/cost(D/D) on DG = 3.03 [2.28, 3.97] against 1717's 2.98 [2.07, 4.33]; solves 312 vs 307 (D) and 199 vs 187 (T) of 384. On TS, 0.92 [0.71, 1.20] against 1717's P_TS 1.29 [0.94, 1.78] (the TS direction stays unresolved, now leaning the other way). Attribution below is therefore conditional on references that behave like the historical ones.

## 3. Pre-stated contrasts

Runner's pair × seed bootstrap (8 192 draws; 24 donor pairs resampled jointly across both rosters and all six arms, two repeats resampled jointly within pair × cell, cells fixed). My columns: a pair-only bootstrap (seeds not resampled) and a paired t interval on the 24 per-pair log ratios, both at 2 × cap; "pairs > 1" counts donor pairs whose own ratio exceeds 1.

**DG roster (primary)**

| Contrast | Arms | 2 × cap | 95 % (runner) | pair-only | paired t | pairs > 1 | 1 × cap | 95 % (1 × cap) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **R replacement** | T/T ÷ T/D | **1.95** | **1.43 – 2.66** | 1.51 – 2.56 | 1.46 – 2.60 | 22/24 | 1.73 | 1.33 – 2.25 |
| G residual | T/D ÷ D/D | 1.55 | 1.15 – 2.09 | 1.21 – 2.00 | 1.18 – 2.04 | 19/24 | 1.42 | 1.10 – 1.84 |
| B bare table | T/∅ ÷ D/∅ | **3.26** | **2.43 – 4.30** | 2.51 – 4.10 | 2.49 – 4.27 | 23/24 | 2.45 | 1.94 – 3.07 |
| D library gain | D/∅ ÷ D/D | 1.45 | 1.18 – 1.79 | 1.25 – 1.70 | 1.22 – 1.73 | 20/24 | 1.40 | 1.17 – 1.67 |
| T portable gain | T/∅ ÷ T/D | **3.05** | **2.32 – 4.07** | 2.41 – 3.88 | 2.35 – 3.95 | 24/24 | 2.41 | 1.91 – 3.07 |
| D library identity | D/T ÷ D/D | 1.35 | 1.10 – 1.68 | 1.15 – 1.58 | 1.13 – 1.60 | 19/24 | 1.29 | 1.08 – 1.56 |
| T native library gain | T/∅ ÷ T/T | 1.57 | 1.23 – 2.00 | 1.27 – 1.93 | 1.25 – 1.96 | 19/24 | 1.39 | 1.14 – 1.70 |
| reverse gain | D/∅ ÷ D/T | 1.08 | 0.86 – 1.35 | 0.91 – 1.29 | 0.89 – 1.31 | 9/24 | 1.08 | 0.89 – 1.32 |
| native gap | T/T ÷ D/D | 3.03 | 2.28 – 3.97 | 2.37 – 3.79 | 2.35 – 3.90 | 23/24 | 2.47 | 1.93 – 3.12 |

**TS roster (secondary)**

| Contrast | Arms | 2 × cap | 95 % (runner) | pairs > 1 | 1 × cap | 95 % (1 × cap) |
|---|---|---:|---:|---:|---:|---:|
| TS retention | T/D ÷ T/T | 1.01 | 0.83 – 1.25 | 11/24 | 1.02 | 0.80 – 1.28 |
| R replacement | T/T ÷ T/D | 0.99 | 0.80 – 1.21 | 13/24 | 0.98 | 0.80 – 1.18 |
| G residual | T/D ÷ D/D | 0.93 | 0.71 – 1.23 | 11/24 | 0.94 | 0.70 – 1.25 |
| B bare table | T/∅ ÷ D/∅ | 0.70 | 0.50 – 0.99 | 9/24 | 0.72 | 0.51 – 1.02 |
| D library gain | D/∅ ÷ D/D | **1.99** | **1.58 – 2.52** | 22/24 | 1.90 | 1.46 – 2.44 |
| T portable gain | T/∅ ÷ T/D | 1.50 | 1.16 – 1.92 | 20/24 | 1.46 | 1.11 – 1.89 |
| D library identity | D/T ÷ D/D | 1.00 | 0.79 – 1.27 | 11/24 | 1.00 | 0.78 – 1.32 |
| T native library gain | T/∅ ÷ T/T | 1.52 | 1.21 – 1.91 | 17/24 | 1.49 | 1.16 – 1.89 |
| reverse gain | D/∅ ÷ D/T | 1.99 | 1.56 – 2.54 | 21/24 | 1.89 | 1.46 – 2.43 |
| native gap | T/T ÷ D/D | 0.92 | 0.71 – 1.20 | 10/24 | 0.92 | 0.69 – 1.22 |

Runner's classification: primary `replacement increment unresolved` (R lower bound 1.43 < 1.5 < upper 2.66), sufficiency not assigned; flags `table_contribution` true (B lower 2.43 > 1.5), `portable_activity` true (T portable gain lower 2.32 > 1.5), `native_D_identity_advantage` false (D/T ÷ D/D lower 1.10), `fresh_native_gap_resolved` true. The 1 × cap repeat gives the same label (`penalty_sensitive: false`); TS retention guidance "cost loss below 1.5 × tolerance".

### How firm is the primary label?

- The runner's own DG-only report (before TS was joined) gave R 1.95 [1.456, 2.653]; the combined report gives [1.432, 2.657]. The two differ only in how the RNG stream is consumed, so the lower bound carries about ± 0.03 of Monte Carlo jitter, and 1.5 sits 0.07 above it.
- Dropping the within-pair seed resample (pair-only bootstrap) moves the lower bound to 1.51; a paired t interval on the 24 pair log ratios gives 1.46. The pre-registered estimator is the pair × seed bootstrap, and by that rule R is **unresolved against 1.5**, but the data put R most plausibly between about 1.5 and 2.5, and no reasonable estimator puts the lower bound below 1.4.
- Leave-one-pair-out R ranges 1.80–2.05; the largest single pair (pair 10: T build 2, R 11.9, T/T solved 5/16 against T/D 14/16) pulls the point from 1.80 to 1.95 but does not create the effect: 22 of 24 pairs have T/D cheaper than T/T.
- Observed per-pair SD of log R is 0.69 against the proposal's planning value 0.6, so the interval is ×/÷ 1.36 rather than the planned 1.3; the proposal's own precision note ("R ≈ 1.6–1.8 likely unresolved") was slightly optimistic and a point of 1.95 landed just short.

### Per cell (DG, 2 × cap)

Solved of 48 · cost in thousands; R, G, B as above.

| Cell | D/D | T/T | T/D | D/T | D/∅ | T/∅ | R | G | B |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| (X0+X1)>(X2+X3) ? X3:X2 | 37 · 81 | 21 · 314 | 34 · 105 | 37 · 105 | 35 · 152 | 17 · 523 | 2.99 | 1.29 | 3.44 |
| (X0+X2)>(X1+X3) ? X3:X2 | 37 · 100 | 26 · 249 | 35 · 150 | 35 · 138 | 35 · 131 | 21 · 305 | 1.66 | 1.49 | 2.33 |
| (X0+X3)>(X1+X2) ? X3:X0 | 44 · 50 | 28 · 202 | 30 · 191 | 40 · 103 | 41 · 91 | 17 · 373 | 1.06 | 3.82 | 4.07 |
| (X1+X2)>(X0+X3) ? X0:X2 | 39 · 95 | 32 · 225 | 36 · 120 | 34 · 126 | 35 · 149 | 13 · 553 | 1.88 | 1.26 | 3.72 |
| (X1+X2)>(X0+X3) ? X3:X1 | 41 · 115 | 26 · 281 | 32 · 166 | 36 · 160 | 35 · 162 | 12 · 582 | 1.70 | 1.44 | 3.59 |
| (X1+X3)>(X0+X2) ? X0:X2 | 39 · 105 | 19 · 424 | 35 · 118 | 34 · 125 | 37 · 148 | 18 · 476 | 3.60 | 1.12 | 3.22 |
| (X1+X3)>(X0+X2) ? X2:X0 | 35 · 129 | 16 · 480 | 25 · 219 | 32 · 191 | 38 · 124 | 13 · 517 | 2.20 | 1.70 | 4.17 |
| (X1+X3)>(X0+X2) ? X3:X1 | 40 · 95 | 31 · 198 | 37 · 126 | 40 · 86 | 35 · 141 | 22 · 308 | 1.57 | 1.33 | 2.19 |

R > 1 in 8/8 cells and > 1.5 in 7/8; B > 2 in 8/8. One cell, `(X0+X3)>(X1+X2) ? X3:X0`, is the exception on both sides: the D library gives the T table almost nothing there (R 1.06) and the hybrid stays 3.8 × behind D/D, while D/D is at its cheapest (44/48). The DG cells are not uniform in what the library can do for a foreign table.

### Per pair and library size

D libraries hold 7–32 fragments (18 of 24 at the 32 maximum; the others 7, 13, 17, 22, 27, 31); all T libraries hold 32. Spearman correlation of D library size with per-pair log R is 0.08 (p = 0.72) and with log T portable gain 0.10; the six sub-maximal libraries give geometric R 1.58 and the 18 full ones 2.09. With six small libraries this says only that size is not visibly the driver; it does not separate content from size.

## 4. Economics (arithmetic, hybrids charged both acquisitions)

Mean worker-seconds per pair, DG roster, acquisition plus search at hypothetical horizons (from `result.json` → `economics`):

| Arm | Acquisition | 1 search | 16 searches | 256 | 4 096 |
|---|---:|---:|---:|---:|---:|
| D/D | 772 | 783 | 959 | 3 766 | 48 687 |
| T/T | 307 | 330 | 666 | 6 041 | 92 045 |
| T/D | 1 079 | 1 095 | 1 338 | 5 227 | 67 449 |
| D/T | 1 079 | 1 094 | 1 312 | 4 809 | 60 754 |
| D/∅ | 772 | 785 | 990 | 4 263 | 56 634 |
| T/∅ | 307 | 334 | 726 | 7 012 | 107 580 |

Charged for both acquisitions, the T/D hybrid is never cheaper than D/D at any horizon on DG and overtakes T/T between 16 and 256 searches. On TS all library-bearing arms are within 15 % of each other at 4 096 searches (16–17.5 k) and the bare arms cost more (D/∅ 29 k, T/∅ 23 k). This is descriptive: nobody would pay for two acquisitions to build a hybrid when D/D is available; the relevant reading is that a D library is cheap to carry (it adds nothing on TS and roughly halves cost on DG relative to the T library).

**Resolution price** (runner, descriptive): with the observed pair variance 0.47 (log scale) and the point fixed at 1.95, about 5 more independent donor pairs (29 total) would be needed for the pair × seed interval to clear 1.5; ≈ 16 000 worker-s, ≈ 35 min at 10 workers with reserve, assuming new D and T acquisitions at the 1717 cost. This is a conditional estimate, not a guarantee: a true R of 1.6 would not resolve with 29 pairs either.

## 5. What the data show

1. **The bare D table alone reproduces the whole family gap on DG.** T/∅ ÷ D/∅ = 3.26 [2.43, 4.30], as large as the native gap 3.03 [2.28, 3.97], in 23/24 pairs and 8/8 cells. Whatever DG-specific bias the D build carries, the context table carries it without any library. (Caveat from the proposal: the bare tables were fitted while intermediate libraries were in use, so D/∅ is not a library-free acquisition, only library-free search.)
2. **The D library is active on a foreign table.** On the fixed T table, swapping in the D library cuts DG cost by 3.05 × [2.32, 4.07] over the bare T table, in 24/24 pairs, versus 1.57 × [1.23, 2.00] for the T table's own library. The replacement increment R = 1.95 [1.43, 2.66] misses the 1.5 margin by its lower bound and is **unresolved** by the pre-stated rule; the evidence is nevertheless one-sided (22/24 pairs, 8/8 cells above 1, lower bound ≥ 1.40 under every estimator tried).
3. **The hybrid does not reach the native D pair.** G = T/D ÷ D/D = 1.55 [1.15, 2.09]: T/D is reliably costlier than D/D (19/24 pairs; lower bound above 1 at both penalties) but whether the residual exceeds 1.5 is unresolved. Together with (1), the library is a partial carrier at most; the table is the larger one.
4. **The asymmetry runs one way.** The T library on the D table gives nothing resolvable over the bare D table on DG (1.08 [0.86, 1.35]) and is 1.35 × [1.10, 1.68] worse than the D library there. So on DG the D library helps either table, the T library helps only its own, and that help (1.57 ×) is half what the D library gives the same table.
5. **On TS the libraries are interchangeable and the transplant costs nothing.** Retention T/D ÷ T/T = 1.01 [0.83, 1.25]; D/T ÷ D/D = 1.00 [0.79, 1.27]; all four library-bearing arms solve 363–368/384 at 24–26 k. Bare tables do pay on TS: the D table needs a library (1.99 × [1.58, 2.52], either library) and the T table 1.52 × [1.21, 1.91]. The bare-table direction reverses on TS (B = 0.70 [0.50, 0.99]), i.e. the bare T table is cheaper than the bare D table on its own family, but not by a worthwhile margin.
6. **Fresh references reproduce 1717** (native gap 3.03 vs 2.98; solves within 12/384), so the attribution is not an artefact of new seeds.
7. **Robustness.** The label and every flag are unchanged at 1 × cap; no shortcut programs passed verification; effect not driven by one pair (leave-one-out 1.80–2.05) or one cell.

## 6. What the data do not show

- **Whether the library's replacement value exceeds 1.5 ×.** The pre-registered interval straddles the margin, and the label is sensitive to the bootstrap design at the ± 0.05 level. Unresolved is not "no effect": a replacement increment of 1.0–1.4 is only marginally compatible with 22/24 pairs favouring the transplant, but the stated rule does not exclude it.
- **Why the D library works on the T table.** Content versus size is not separated (6 sub-maximal libraries, no size correlation); nothing here identifies which fragments act or whether they encode the DG double-gate structure. The one exceptional cell shows the effect is cell-dependent.
- **Any fresh-bank or transfer claim.** Both rosters are development data (x4-double-gate-v1 spare cells, x4-branch-sum-v1 targets); the libraries were built on DG and TS sources respectively. "Portable" here means between two saved decoders on their development families.
- **Native compatibility versus coadaptation.** The D-library-identity contrast (D/T vs D/D, 1.35 [1.10, 1.68]) shows the D table does better with its own library than with the T one, but T/D also beats T/T, so nothing requires that table and library were tuned to each other; "the D library is simply more useful on DG cells" fits all four library cells.
- **Inheritance, selection, or a join motif**; the libraries and tables are frozen external fits throughout.
- **The TS cost direction** between cohorts (native gap 0.92 [0.71, 1.20]), unresolved as in 1717.

## Against the predictions

`plan.md` pre-registered the primary rule R = cost(T/T)/cost(T/D) on DG against a 1.5 × replacement margin, with G, B, the portable-activity contrast T/∅ ÷ T/D, the D-library-identity contrast D/T ÷ D/D, the fresh-reference check and TS retention as secondary readings, and said R around 1.6–1.8 could remain unresolved.

| Prediction or rule | Stated | Observed | Verdict |
|---|---|---|---|
| Primary R lower > 1.5 → worthwhile replacement increment; upper < 1.5 → none; crossing → unresolved | — | 1.95 [1.43, 2.66] | **Unresolved**, by 0.07 on the lower bound. Sufficiency sub-label not assigned (rule requires R resolved first). |
| Expected R ≈ 1.6–2.2 (proposal) | 1.6–2.2 | 1.95 | Point inside the expected band; interval width (×/÷ 1.36) slightly wider than the planned 1.3, so the band's upper half was needed to resolve and did not quite suffice. |
| G residual ≈ 1.3–1.8 | 1.3–1.8 | 1.55 [1.15, 2.09] | Point inside; crosses 1.5 (would have been "sufficiency unresolved" had R resolved). |
| Bare B = T/∅ ÷ D/∅ lower > 1.5 supports a table-carried contribution; proposal expected D/∅ to beat T/∅ by 1.3–1.7 | 1.3–1.7 | 3.26 [2.43, 4.30] | **Table contribution resolved**, and about twice the expected size: the bare tables carry the whole native gap. |
| Portable activity T/∅ ÷ T/D (reported when R unresolved or excluded) | — | 3.05 [2.32, 4.07] | **Resolved above 1.5** in 24/24 pairs; the D library is useful on the T table even though its replacement increment over the T library is unresolved. |
| D-library identity under the D table, D/T ÷ D/D; native-combination language needs lower > 1.5 | — | 1.35 [1.10, 1.68] | Not resolved above 1.5; no native-combination claim. The D table does measurably better with its own library (lower bound 1.10). |
| Fresh D/D vs T/T must reproduce the historical DG gap, else attribution is conditional | 2.98 [2.07, 4.33] (1717) | 3.03 [2.28, 3.97] | **Reproduced.** |
| TS retention T/D ÷ T/T wholly above 1.5 would make an indiscriminate D-only repertoire unattractive; crossing leaves it unresolved; proposal expected within 1.25 × | ≤ 1.25 | 1.01 [0.83, 1.25] | Loss excluded at 1.5 and at the proposal's 1.25; swapping the D library onto the T table costs nothing on TS. |
| 1 × cap repeat, flag if label changes | — | R 1.73 [1.33, 2.25]; all flags unchanged | Not penalty-sensitive. |
| Surprise: R ≤ 1.1 while D/∅ ÷ D/D ≥ 1.5 (library helps only its own table) | — | R 1.95; D/∅ ÷ D/D 1.45 [1.18, 1.79] | Did not occur. |
| Surprise: T/D cheaper than D/D | — | G 1.55, 19/24 pairs the other way | Did not occur. |
| Surprise: a bare table cheaper than its native pair | — | D/∅ ÷ D/D 1.45 [1.18, 1.79]; T/∅ ÷ T/T 1.57 [1.23, 2.00]; on TS 1.99 and 1.52 | Did not occur; libraries help every table on every roster. |
| Too-clean hybrid equality must be checked against operator activity, hashes, initialization | — | TS library arms within 1.01–1.00 of each other; block events non-zero in all library rows, 48 distinct library hashes, initial hashes equal only within table | Equality on TS is genuine, not a wiring artefact. |
| Queue ≈ 100–150 min expected, 240 min ceiling | 100–150 | 89 min total (DG 68, TS 19, prepare 2) | Faster than expected; projections held with margin. |

Outcome by the plan's rule: **replacement increment unresolved**, with the three secondary readings the plan asked for all resolved in the same direction (table contribution yes, portable library activity yes, native-identity advantage not shown). The plan's own precision note anticipated this band. What was not anticipated is that the bare tables alone reproduce the full gap, which makes the table the larger carrier and limits what resolving R could add: even a resolved R ≈ 2 would leave G ≈ 1.5 and B ≈ 3.3 in place. The runner's resolution price for R (about 5 more independent pairs, ≈ 35 min queue plus two acquisitions per pair) is the cheapest follow-up but, per the proposal, exit to strategy in every case.
