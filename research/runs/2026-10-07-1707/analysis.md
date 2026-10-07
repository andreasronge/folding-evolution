---
outcome: row 1
---

# Analysis: 2026-10-07-1707 solver-corpus context fit

Reviewer analysis of the queue run at commit `627336d`
(output: `experiments/output/2026-10-07/2026-10-07-1707-solver-corpus-context/`).
All numbers below were recomputed independently from `search.jsonl`; they agree with
`result.json` to three decimals. My per-corpus contrast plot is
[corpus_contrasts.png](corpus_contrasts.png).

## 1. Data completeness

Complete. Every stage ran to its full roster, nothing was skipped, and no run failed.

| phase | arm | rows | expected | solved |
|---|---|---:|---:|---:|
| replay | GG | 40 | 40 | 40 bit-identical to 0315 on all scientific fields |
| collection | G4 | 7 680 | 7 680 | 7 408 (96.5%) |
| training | T / C / K | 5 120 each | 5 120 each | 5 057 / 5 077 / 5 018 |
| training | G4 | 960 | 960 | 923 |
| training | M (1723 maps) | 1 600 | 1 600 | 1 581 |
| holdout | T / C / K | 3 072 each | 3 072 each | 3 028 / 3 034 / 3 013 |
| holdout | G4 | 384 | 384 | 371 |

- 35 240 rows, zero duplicate (phase, family, corpus, cell, arm, seed) keys.
- Every corpus × cell × arm group has exactly 32 evaluation seeds; T, C and K share identical
  seed sets within each corpus × cell (480 training groups, 288 holdout groups, 0 mismatches).
- Evaluation seed blocks are disjoint across corpora and across phases (0 overlaps).
- Every unsolved row has `evaluations == cap` (524 288); the run's own roster, table-hash,
  case-index and arm-pairing checks all passed (16 384 pairing checks, 7 447 solver
  re-verifications on all 1 331 inputs, 96 table checks).
- Collection yield per cell: minimum 40/48 (BE), 45/48 (PA), far above the 24/48 floor.
  Family totals 2 861/3 072 BE and 4 547/4 608 PA.
- K validated on all 32 corpora (max error 3.3e−5 against the 1e−3 tolerance); T's L-BFGS-B
  converged on all 32. No K exclusions, so the "K-valid subset" C/T equals the all-corpus C/T.
- Stage 2 was admitted on time only (projected 1 141 s against 3 934 s remaining) and completed.
- Wall clock 80.6 min: replay 17 s, collection 31 min, stage 1 33 min, stage 2 16 min.
  The proposal projected 70–85 min. Collection cost 2.08 worker-s per search.

## 2. Key numbers (stage 1, training cells, unsolved = 2 × cap)

Speed ratio is 2^(−Δ mean log2 evaluations); > 1 means the first arm is faster.
Per-corpus contrast = mean over cells of per-cell mean log2 cost, 16 corpora per family,
t on 15 df; pooled = equal-weight family mean.

| contrast | pooled | BE | PA |
|---|---|---|---|
| C / T | **1.365 [1.288, 1.446]** | 1.460 [1.322, 1.612] | 1.275 [1.201, 1.354] |
| C / K | **1.654 [1.568, 1.744]** | 1.846 [1.688, 2.018] | 1.482 [1.400, 1.569] |
| K / T (not in the report) | 0.825 [0.776, 0.878] | 0.791 [0.711, 0.881] | 0.861 [0.809, 0.915] |
| T / G4 (unpaired) | 2.422 [2.172, 2.701] | 2.498 [2.063, 3.025] | 2.348 [2.115, 2.607] |
| C / G4 (unpaired) | 3.305 [2.984, 3.660] | 3.647 [3.058, 4.350] | 2.994 [2.700, 3.321] |
| T / M (unpaired, Welch) | — | 0.951 [0.813, 1.113] | 1.017 [0.808, 1.282] |

Consistency across replicates:

- C beat T in 31 of 32 corpora (the exception is PA13, +0.047 log2) and in 129 of 160
  corpus × cell pairs. C beat K in 32/32 corpora and 152/160 pairs.
- K beat T in only 5 of 32 corpora and 43/160 pairs.
- Per-corpus contrast sd: 0.27 log2 (BE) and 0.16 (PA) for C − T. The proposal assumed 0.3.
- Paired per search (both solved, 5 016 of 5 120 pairs): median log2 T/C = 0.38; C was faster
  in 57.5% of pairs and tied in 2%. So the mean effect is a broad shift, not a few outliers.
- 1 × cap sensitivity: C/T 1.360 [1.285, 1.440], C/K 1.639 [1.559, 1.723]. Unchanged.
- Per cell, every one of the 10 training cells has C mean below T mean and C solve rate ≥ T's.

Reference arms: G4 mean log2 cost 14.06 on training cells (probe: 13.99 / 14.16), 923/960
solved. The 1723 learned maps M (12.78) sit level with T (12.79); T versus M is unresolved in
both families.

## 3. Stage 2, holdouts (descriptive unless row 1–2; it is row 1, so interpreted)

One-sample over 32 corpora (31 df); each corpus's score is its mean over the three holdout cells.

| contrast | all 32 corpora | BE-fitted (16) | PA-fitted (16) |
|---|---|---|---|
| C / T | **1.293 [1.213, 1.378]** | 1.332 [1.224, 1.449] | 1.255 [1.132, 1.391] |
| C / K | **1.537 [1.431, 1.650]** | 1.628 [1.483, 1.789] | 1.450 [1.299, 1.619] |
| K / T | 0.841 [0.792, 0.893] | 0.818 [0.749, 0.893] | 0.865 [0.792, 0.946] |
| T / G4 | 2.125 [1.846, 2.446] | | |
| C / G4 | 2.747 [2.388, 3.161] | | |

C beat T in 30/32 corpora on the holdouts. Per holdout cell (mean log2, all 32 corpora):

| cell | G4 | T | C | K |
|---|---|---|---|---|
| BE `S?m:(M+F)` | 13.21 (122/128) | 12.07 (1011/1024) | 11.51 (1019/1024) | 12.29 |
| PA `(F?S:M)+m` | 14.09 (122/128) | 13.19 (994/1024) | 12.91 (992/1024) | 13.44 |
| PA `(S?M:m)+F` | 13.72 (127/128) | 12.50 (1023/1024) | 12.23 (1023/1024) | 12.78 |

Family adaptation (C fitted on the matched family over C fitted on the mismatched family,
Welch 16 vs 16):

| cell | matched / mismatched | matched / G4 |
|---|---|---|
| BE `S?m:(M+F)` | 1.022 [0.911, 1.147] | 3.29 [2.53, 4.28] |
| PA `(F?S:M)+m` | **0.748 [0.629, 0.891]** | 1.97 [1.48, 2.63] |
| PA `(S?M:m)+F` | 0.989 [0.886, 1.103] | 2.79 [2.29, 3.39] |

No cell shows a family-specific advantage. On PA `(F?S:M)+m` the *mismatched* (BE-fitted) C is
faster than the PA-fitted C: 12.70 versus 13.11 log2. BE-fitted T is also ahead of PA-fitted T
there (13.11 vs 13.28), so the direction is shared by both fits, not specific to context.

## 4. What the corpora and tables look like

- All 7 408 collected solver tapes are distinct; no tape is shared between any two corpora of
  the same family. The corpora are independent samples, not re-collections of a few solutions.
- Transition counts hold real order information. Mutual information between previous and
  current token is 0.54 bits (BE1) and 0.51 bits (PA1); permuting tokens within each tape
  (same marginals, destroyed order) gives 0.08 ± 0.004 and 0.05 ± 0.002. About 0.45 bits per
  transition is order structure, consistently across all 32 corpora (0.50–0.56 bits).
- C's body rows have count-weighted entropy ≈ 3.7 bits versus 4.19 for G4; C's start row is
  *flatter* (2.6–3.1 bits, top token 0.52–0.63) than G4's start row (3.17 bits, top token 0.69).
  So the C advantage is not a sharper first-token prior. 60% (BE) and 58% (PA) of solver tapes
  begin with token 1.
- T multipliers span about 0.3–2.1 against the ±16 bound; K's 0.4–1.75. Neither hit a bound.
- Corpus token frequencies versus G4's uniform-latent emitted marginal: tokens 1, 23, 18, 22, 7
  enriched 1.35–1.7×; tokens 4, 14, 16, 15, 3 depleted to 0.3–0.5×.

## 5. Amortization (descriptive, arithmetic mean capped evaluations and seconds)

Per corpus, collection cost 9.0–15.6 M evaluations (median 11.9 M) and about 500 worker-s.

| arm | median evals saved per search vs G4 | median s saved | break-even searches (evals) | break-even (seconds) |
|---|---|---|---|---|
| T | 38 953 | 0.98 | 141–763 | 198–1 316 |
| C | 48 198 | 1.51 | 120–593 | 169–865 |

All 32 corpora have finite break-even on both measures at 2 × cap. On holdouts the per-search
saving is smaller and two corpora have negative evaluation savings for T (one for C).

## 6. What the data shows

1. **C is faster than T, replicated.** 1.37× pooled on training cells [1.29, 1.45], 31/32
   corpora, both families separately resolved, robust to the unsolved-run convention, and the
   transfer to three unseen holdout cells is 1.29× [1.21, 1.38] with 30/32 corpora.
2. **C is faster than K, by more than it is faster than T.** This is the row-1 condition, and
   it is met with margin. But the reason deserves care: K is *slower than T* (0.83×,
   [0.78, 0.88], K < T in only 5/32 corpora). K is a token-only G4 reweighting whose
   uniform-latent emitted marginal is forced to match C's. That marginal turns out to be a
   worse token-only target than T's likelihood fit. So C/K = 1.65 is the product of C's real
   gain over the best token fit (1.37) and K's own damage (1/0.83). The isolated "context beyond
   emitted frequencies" increment is best read as C/T = 1.37, not C/K = 1.65.
   What C/K does establish: C's advantage cannot be reproduced by matching its pooled emitted
   token frequencies with a context-free table. That supports the proposal's intended reading
   of row 1 (the increment is not explained by emitted frequencies) while showing the
   emitted-marginal control is not a neutral control.
3. **Both fits beat G4 by a lot** (T 2.4×, C 3.3× on training; 2.1× and 2.7× on holdouts).
   Neither damages search. T lands level with the 20 saved 1723 maps M (unresolved either way),
   so a one-shot token fit from ~200 G4 solver tapes matches what a 4–6 h nested learner found.
4. **No family specificity.** The matched-family C is never resolved ahead of the mismatched
   one, and on one PA holdout the BE-fitted tables are ahead. Whatever C captures is shared
   between the BE and PA families at this granularity (the BE holdout is a single cell).
5. **The corpora carry genuine order information** (≈ 0.45 bits per transition above the
   shuffled baseline), and the fitted C tables are not a sharper start-row prior.

## 7. What the data does not show

- It does not show that evolution or any search-cost-selected procedure can *find* C. This is
  external fitting from exact solvers; the four earlier selection procedures remain null.
- It does not isolate *which* contextual structure matters (specific bigrams, executed versus
  inert tokens, position). Full tapes were fitted; the inert-token question is open.
- C/G4, T/G4 and T/M are unpaired (own seed blocks) and are descriptive.
- α = 50 was frozen from one probe corpus per family; the probe's C400 sensitivity suggests the
  gain depends on α. Nothing here maps that dependence.
- The K control is informative as a negative (matching C's marginals is not enough) but it is
  slower than T, so "C/K" overstates the contextual increment. A fairer bound on the
  increment is C/T.
- Family-specific transfer is not shown; with one BE holdout cell, BE-family specificity is
  also not refuted.
- Break-even counts are arithmetic and at this cap; they assume future searches resemble the
  training cells. Holdout savings are smaller and in a few corpora negative.
- Shortcut solutions: shortcut counts per arm are similar (T 122, C 107, K 103 of 5 120 rows),
  so C does not win by exploiting more shortcuts. Evaluation-phase solver tapes were not saved,
  so what C's solvers look like is unknown.

## Against the predictions

The plan's rows are evaluated on pooled stage-1 estimates with 95% bounds.

| row | condition | data | met |
|---|---|---|---|
| 0 infeasible | any cell < 24/48, validation failure, > 4 K failures/family, stage 1 incomplete | min yield 40/48; validation passed; 0 K failures; stage 1 complete | no |
| 1 | C/T lower > 1 **and** C/K lower > 1 | C/T lower 1.288; C/K lower 1.568 (K-valid subset = all 32) | **yes** |
| 2 | C/T lower > 1, C/K lower ≤ 1 | — | no |
| 3 | C/T lower ≤ 1 and upper < 1.10 | — | no |
| 4 unresolved | C/T lower ≤ 1 and upper ≥ 1.10 | — | no |

Outcome **row 1**: solver corpora carry useful context beyond token fitting and beyond C's own
emitted frequencies, on training cells, with this fit. Stage 2 is therefore interpreted:

- **Transfer rule**: C/T on holdouts lower bound 1.213 > 1 → *transfers*. C/K lower 1.431 > 1 →
  the transferred increment is "contextual" by the plan's rule, with the same caveat as above
  (K is slower than T, so the plan's C/K test is lenient; C/T alone already satisfies the
  transfer rule).
- **Family rule**: no holdout cell has matched/mismatched lower > 1 (1.02 [0.91, 1.15],
  0.75 [0.63, 0.89], 0.99 [0.89, 1.10]). No family-specific claim. On PA `(F?S:M)+m` the
  mismatched fit is resolved faster.
- **Always-reported**: C/G4 upper > 1 everywhere (C does not damage search); T versus M
  unresolved in both families; per-family C/T is BE 1.46 > PA 1.28, matching the probe's
  direction, with family still confounded with cell count and difficulty.

Plan predictions versus observations:

- Precision: the plan expected a pooled half-width ≈ 0.11 log2 from a 0.3 sd; observed
  half-width 0.084 log2 (sd 0.27 BE, 0.16 PA). Better than planned.
- Effect size: the probe suggested C − T ≈ −0.78 (BE) and −0.28 (PA) log2; observed −0.55 and
  −0.35. The BE probe value was an overestimate, the PA one an underestimate; both are inside
  the confirmation's range.
- Runtime: 80.6 min observed. The proposal projected 70–85 min; the plan's smoke revised that to
  a conservative 90–100 min. Stage 2 was admitted on the time gate alone, as the plan requires.
- The plan's row-4 sample-size requirement does not apply (row 1). The plan's family rule, that useful
  adaptation needs matched C ahead of both the mismatched C and G4, is reported above; no cell meets it.
- The plan's expectation that K would emit C's frequencies while retaining G4's template held
  (max error 3.3e−5), but the plan did not anticipate that K would be slower than T. Future
  designs wanting an emitted-frequency control should pair K against a token-only fit of equal
  quality, or report K/T alongside C/K as done here.

Decision-relevant reading: the plan's row-1 decision (close sub-question 20 as answered and
return to strategy, next distinction being whether evolution can discover the fitted context)
is supported by the data. The claim to promote should be stated as "a transition-count decoder
fitted to ~200 exact G4 solver tapes is 1.37× [1.29, 1.45] faster than the best token-only fit
of the same tapes on training cells and 1.29× [1.21, 1.38] on unseen holdouts, both families,
no family specificity", with C/K reported as a negative control (frequency matching does not
reproduce the gain) rather than as the size of the contextual increment.
