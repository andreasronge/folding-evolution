---
outcome: recommend_stage2
---

# Analysis: 2026-10-08-1246 comparison-gate bank, stage 1 (training cells)

Reviewer analysis of the queue run at commit `5dd86bd` (output:
`experiments/output/2026-10-08/2026-10-08-1246-comparison-gate-training/`). All numbers
below were recomputed independently from `search.jsonl` and `corpora.json`; the primary
endpoint agrees with `result.json` to three decimals. My plots are
[ct_training.png](ct_training.png) (per-corpus C/T and pooled solve curves) and
[ct_per_cell.png](ct_per_cell.png) (solve curves per training cell).

## 1. Data completeness

Complete. The full stage 1 roster ran, nothing was skipped, no row failed, no holdout was
searched, and the queue exited 0 in 7 127 s wall (projection 7 111 s; 3 h timeout).

| phase | arm | rows | expected | solved |
|---|---|---:|---:|---:|
| collection | G4 | 3 072 | 3 072 | 1 808 (58.9%) |
| training | C | 1 024 | 1 024 | 936 (91.4%) |
| training | T | 1 024 | 1 024 | 791 (77.2%) |
| training | G4 | 256 | 256 | 174 (68.0%) |

- 5 376 rows, zero duplicate (phase, family, corpus, cell, arm, seed) keys. Every corpus ×
  cell has exactly 48 collection and 16 C/T seeds; every training cell has 32 G4 seeds.
- C and T share identical seed sets and identical 64-case training draws in all 1 024
  pairs. No seed is shared between collection, C/T and G4 blocks.
- One table hash per (arm, corpus); every G4 row carries the pinned G4 hash. All 16 T fits
  converged with no multiplier at the 1/16 or 16 bound; K valid on 16/16 (never scored).
- Run-internal checks: 1 808 solver re-verifications on all 1 331 inputs, 1 024 pairing
  checks, bank and split hashes match, `validation.passed` true, `completed_pairs` 8/8.
- Collection yield: pooled 1 808/3 072 = 58.9% (BE 860/1 536 = 56.0%, PA 948/1 536 =
  61.7%). Weakest corpus-cell 14/48 (BE `F>S?F:M+m` in BE2, PA `(F>S?F:m)+M` in PA3 and
  PA4); no empty cell. All solver tapes within a corpus-cell are distinct.
- The stage-2 roster (holdout ids, table hashes, seeds) is frozen in `freeze.json` with
  `stage2_searches_executed: 0`.

## 2. Key numbers (training cells, unsolved = 2 × cap)

Speed ratio = exp(mean over corpora of mean over 4 cells × 16 paired seeds of
log cost_T − log cost_C); > 1 means C solves sooner. 8 corpora per family, equal family
weight, t interval on 15 df.

| contrast | pooled (16 corpora) | BE (8) | PA (8) |
|---|---|---|---|
| C / T, 2 × cap | **3.11 [2.78, 3.48]** | 2.86 [2.56, 3.20] | 3.37 [2.74, 4.16] |
| C / T, 1 × cap | 2.82 [2.52, 3.14] | 2.60 [2.31, 2.93] | 3.05 [2.50, 3.71] |
| C / G4 (descriptive, unpaired) | 5.77 | 5.77 | 5.78 |
| T / G4 (descriptive, unpaired) | 1.86 | 2.02 | 1.72 |

Consistency across replicates:

- C beat T in 16/16 corpora (range 2.05× PA8 to 4.46× PA4) and in 64/64 corpus × cell
  pairs. The per-corpus sd is 0.21 log (0.13 BE, 0.25 PA), near the 0.27/0.16 log2 seen on
  the old bank.
- Paired per search: C solved in 936/1 024, T in 791/1 024; (C yes, T no) 205, (C no, T yes)
  60, neither 28. Among the 731 pairs both solved, median T/C evaluations = 2.21×; C was
  faster in 69.6% of those pairs, tied 0.3%. So the effect is a broad shift, not a few
  unsolved T runs charged at the cap, and the 1 × cap sensitivity stays near 2.8×.
- Median evaluations to an exact solve (solved runs only): C 29 952, T 80 640, G4 136 448
  (training) and 134 528 (collection).

Per cell (C and T n = 128 each, G4 n = 32):

| cell | C solved | T solved | G4 solved | C/T | C/G4 | T/G4 | C faster of 128 |
|---|---:|---:|---:|---:|---:|---:|---:|
| BE `F>S?F:M+m` | 101 | 71 | 15 | 3.58 | 6.23 | 1.74 | 85 |
| BE `F>m?S:F+M` | 116 | 94 | 21 | 2.70 | 5.86 | 2.17 | 83 |
| BE `S>F?M:F+m` | 110 | 100 | 19 | 2.27 | 5.68 | 2.50 | 79 |
| BE `S>F?m:M+S` | 122 | 114 | 26 | 3.06 | 5.34 | 1.74 | 89 |
| PA `(F>S?F:m)+M` | 110 | 75 | 17 | 4.72 | 8.28 | 1.75 | 95 |
| PA `(F>S?m:M)+F` | 125 | 107 | 23 | 3.12 | 4.83 | 1.55 | 95 |
| PA `(M>F?m:S)+S` | 126 | 114 | 28 | 3.32 | 6.58 | 1.98 | 95 |
| PA `(S>F?M:m)+m` | 126 | 116 | 25 | 2.65 | 4.23 | 1.60 | 93 |

Every cell has C solve rate > T solve rate > G4 solve rate and the same cost ordering. The
largest C/T sits on the two hardest cells (lowest G4 rate), which is where unsolved
penalties matter most, but the ordering holds on the easiest cells too.

Routing inputs: lower bound 2.78 > 1.0 and pooled yield 0.589 ≥ 0.40, so the report's
own route is `recommend_stage2`. The `useful_adaptation_caution` flag is false: C and T both
beat G4 descriptively, so this is not C beating a damaged T.

## 3. Checks for shortcut or artefact explanations

- **Memorisation of corpus tapes.** Not supported. Solver tapes within a corpus-cell
  differ at 28.2 of 32 positions on average (min 27.6 over the 64 corpus-cells); only
  position 0 has low entropy (2.3–2.9 bits), later positions 3.5–4.2 bits. The fitted C
  tables are not peaked: mean row entropy 3.80 bits versus 3.82 for T and 4.15 for G4;
  mean maximum row probability 0.22–0.23 for both C and T. C encodes a diffuse transition
  preference, not a copied program.
- **T damaged or clipped.** No multiplier reached its bound in any corpus; T/G4 ≈ 1.9
  descriptively, so T still helps G4. T is simply weaker here than on the old bank (2.4×).
- **Training-perfect shortcuts.** Counted but not consumed as solves: `solved` requires
  exactness on all 1 331 inputs. Shortcut counts per search are similar for C (1 636 mean)
  and T (1 727 mean), so C is not winning by exploiting the 64-case training draw.
- **Shared G4 baseline.** C/G4 and T/G4 are descriptive only; G4 seeds are independent and
  the baseline is not replicated per corpus, as the report states.
- **Equal cell weight in the fit.** Each corpus-cell is rescaled to 1 600 transition
  weight regardless of its 14–43 tapes, so the thin cells (14 tapes) get as much pull on C
  as the rich ones. This is the frozen 1707 rule; it did not visibly hurt (the thin cells
  show the largest C/T), but 1 600 weights from 14 tapes are not 1 600 observations.

## 4. What the data shows

- On this bank's eight training cells, the context fit C solves fresh searches about
  3.1× sooner than the token-only fit T to the same solver tapes (95% interval 2.78–3.48,
  16/16 corpora, 64/64 corpus-cells, robust to the cap penalty). This replicates the
  old-bank direction (1707: 1.365× [1.288, 1.446]) with a much larger size, and it is the
  first result on 13-token comparison-gated compositions.
- Both fitted maps beat G4 descriptively; the context gain is additive on top of the
  token gain (C/G4 ≈ 5.8, T/G4 ≈ 1.9), not a recovery from a damaged control.
- G4 collection yield is 58.9% pooled, above the 40% continuation floor and above the
  steward probe's 40/64 on these cells, so acquisition is not the obstacle.
- Collection cost: 48 040 worker-seconds for 1 808 tapes (26.6 s per tape, 15.6 s per
  search). Break-even for a C table against G4 is about 200–220 further searches by
  evaluations (report's amortisation, descriptive).

## 5. What the data does not show

- **No transfer.** All eight cells were both the fit's source and its test; the C/T gain
  is a within-cell training-fit result. Whether frozen C beats frozen T on the eight
  untouched holdouts is stage 2's question and is still open. On the old bank the holdout
  gain was 1.29× against 1.37× in training; a similar shrinkage would still leave a large
  effect, but a bank with longer programs could also shrink more.
- **No isolated token-order mechanism.** K was fitted but not scored, so changed emitted
  token frequencies are not controlled; C/T compares two fitting procedures.
- **Why 3.1× rather than 1.4×** is not identified by this design. Candidates are longer
  programs with more sequential structure, a harder base task (G4 solves 68% here versus
  96% on the old bank, so there is more room to gain), and a weaker token-only fit on this
  bank; the data are consistent with all three.
- No family contrast was pre-registered; BE 2.86× and PA 3.37× have overlapping intervals.
- The G4 solve rate on training cells (174/256 = 68%) is descriptive; G4 was not paired
  with C/T.

## Against the predictions

Plan read after the analysis above was written.

- **Routing rule.** Plan: lower bound > 1 and pooled collection yield ≥ 40% → recommend
  that strategy consider stage 2, taking precedence over any other branch. Observed:
  lower bound 2.78 and pooled yield 0.589 (BE 0.560, PA 0.617). The rule is met with a
  wide margin, so the outcome label is `recommend_stage2`, matching the report's own route.
- **Execution rules.** The plan required the first six pair blocks at minimum; all eight
  completed in order with no timeout, validation error or empty cell. The G4 training
  block ran first as specified. No holdout search ran; the stage-2 roster is frozen.
- **Size prediction.** The proposal expected C/T of about 1.2–1.4× and named C/T ≤ 1 as a
  surprise. The observed 3.11× [2.78, 3.48] is a surprise in the other direction: the
  old-bank direction replicates, but the effect is more than twice the top of the
  expected range. The plan's interpretation sentence for this case ("the old-bank fit
  benefit replicates on these new training compositions; protected transfer remains
  open") applies as written.
- **Precision scenarios.** The plan projected a half-width of 0.118 log2 (×1.085) at n =
  16 from the old-bank sds. Observed half-width is 0.113 natural-log (×1.12). Spread was
  as planned on BE (0.13 natural, within the 0.27 log2 scenario) and higher on PA (0.25
  natural ≈ 0.36 log2, above the doubled-sd scenario). The interval is still far from
  1.0, so the precision shortfall changes nothing.
- **Headroom check.** The plan warned that uniformly easy searches would reveal a
  ceiling rather than a mechanism. Not the case: G4 solved 68% of training searches at
  the cap and the hardest cell 47%, so there is room on both sides and the fitted maps
  are measured against a hard baseline.
- **Useful-adaptation caution.** Not triggered: both C and T beat G4 descriptively
  (5.8× and 1.9×). The plan's "damaged T" interpretation does not apply.
- **Scope the plan fixed.** Training effects only, C versus the restricted T fitting
  procedure, no isolation of token order from emitted frequencies. The analysis keeps
  that scope. The competing explanation B in question 24 (old-bank gain belonged to its
  short shapes, C/T ≈ 1 here) is ruled out on training cells; explanation A (tapes carry
  assembly information beyond token frequency on these longer gated tasks) is
  consistent with the data; explanation E (acquisition too costly) is not supported at
  this cap, since yield is 59% and collection took 80 min of the 119 min run.
- **For the stage-2 decision.** The report prices stage 2 at about 3 940 s of queue at
  training difficulty (holdouts untimed). With a 16-corpus training effect of 3.1×, a
  holdout C/T interval would need to exclude 1.0 by a large margin to be uninformative;
  the useful question for strategy is how much the gain shrinks on untouched cells, not
  whether it exists on the training cells.
