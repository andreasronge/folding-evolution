---
outcome: replacement_insufficient
---
# Analysis: frozen frequency-matched K tables on 1548 row F

Reviewer analysis of queue entry `2026-10-09-0125-frequency-matched-K`
(commit `8e62831`, output
`experiments/output/2026-10-09/2026-10-09-0125-frequency-matched-K/`).
All numbers below were recomputed independently from `search.jsonl` and the
vendored 1548 row F rows (`experiments/chem_tape/data/then_addition_1548_frozen/`),
not copied from `result.json`. They agree with `result.json` to the printed
precision.

## 1. Data completeness

| Check | Result |
|---|---|
| Queue status / exit code | done, exit 0, wall 2493 s (41.5 min; projection was 72 min) |
| K rows in `search.jsonl` | 2048 / 2048, all `arm == 'K'`, no duplicates on (corpus, cell, seed) |
| Corpora × cells × seeds | 16 corpora × 128 rows; 16 cells × 128 rows; 2048 distinct seeds |
| Cap / population | all 524 288 / 256; 0 budget anomalies (unsolved rows all at exactly cap) |
| Reference rows (1548 row F) | 4352: C 2048, T 2048, G4 256 (16 per cell); SHA-pinned |
| C/T/K triples | 2048 / 2048 complete; 0 training-index mismatches across the three arms |
| K table identity | exactly one table hash per corpus, 16 distinct; hashes checked against the 1246 freeze by the runner |
| Pooled marginal match C vs K | max abs error 2.90e-5 (threshold 1e-3) |
| 16 preparation timing rows | all 16 replayed deterministically (non-clock fields identical) inside the full roster |
| Failures / errors | none (`validation.passed = true`, `error = null`, `stderr.log` empty) |

Nothing is missing, nothing is duplicated, and the roster is exactly the one
pre-registered. The C/T interval reproduces the 1548 report (2.12 [1.86, 2.41]).

## 2. Key numbers

Primary: C/K = exp(mean over 16 corpora of the mean over 16 cells × 8 paired
seeds of log cost_K − log cost_C). Unsolved = 2 × cap. t interval, 15 df.

| Contrast | unsolved = 2×cap | unsolved = 1×cap | both-solved pairs only (n corpora = 16) |
|---|---|---|---|
| **C/K** (primary) | **2.48 [2.17, 2.83]**, sd log 0.25 | 2.25 [1.98, 2.54] | 1.92 [1.68, 2.21] |
| C/T (reused 1548) | 2.12 [1.86, 2.41] | 1.96 [1.75, 2.21] | 1.69 [1.50, 1.91] |
| K/T | 0.86 [0.77, 0.96] | 0.87 [0.80, 0.96] | 0.86 [0.76, 0.97] |
| K/G4 (unpaired G4, descriptive) | 1.57 [1.45, 1.70] | 1.47 [1.38, 1.58] | — |

Decision-rule band: the C/K lower bound (2.17) is above 1.20 by a wide margin
under both censoring treatments and under the selection-conditioned
both-solved view. The pre-stated label is **pooled frequencies insufficient**.

Solve counts (exact D1331, cap 524 288):

| Arm | Solved | BE corpora | PA corpora |
|---|---|---|---|
| C | 1771 / 2048 (86.5%) | 898 / 1024 | 873 / 1024 |
| T | 1547 / 2048 (75.5%) | 770 / 1024 | 777 / 1024 |
| K | 1484 / 2048 (72.5%) | 752 / 1024 | 732 / 1024 |
| G4 | 162 / 256 (63.3%) | — | — |

Median evaluations among solved runs: C 44 800, T 82 944, K 89 856, G4 145 408.

Per-search pairing (C vs K, same seed and case draw): K slower in 1322, tie in
103, K faster in 623 of 2048. Solve pattern (C, K): both 1309, C only 462,
K only 175, neither 102.

Per-corpus C/K ranges from 1.44 (PA8) to 3.67 (BE1); all 16 corpora are above
1.20. By fitting family: BE-fitted 2.77 [2.36, 3.25] (n = 8), PA-fitted
2.21 [1.77, 2.76] (n = 8). Per-cell C/K ranges from 1.42 (`TA:F>m?S+S:M`) to
3.67 (`TA:M>F?S+m:F`); every cell is above 1.20 (see
`ck_per_corpus_cell.png`, right panel; this is 16 corpora × 8 seeds per
point, not the pre-registered unit).

K/T: K is slower than T in 14 of 16 corpora and 12 of 16 cells; the corpus
interval excludes 1. The descriptive share log(K/T)/log(C/T) is −0.21: moving
T's multipliers to C's pooled marginals costs speed rather than buying any.

Shortcut check: "shortcuts" (training-perfect individuals that fail the
exact D1331 check) occur in 174 C, 156 T, 126 K and 8 G4 runs, and are never
counted as solves. K does not solve by shortcut more than the other arms.

Sizing note from the report: at the observed spread, about 30 corpora would be
needed for a ±10% half-width. It is irrelevant to the decision here because
the interval is already far from 1.20.

## 3. What the data shows

- On these 16 cells and 16 corpora, with the same seeds and case draws, the
  context tables C are about 2.5× cheaper than K, the G4 template reweighted
  by 24 per-token multipliers so its pooled emitted marginals match C's.
  The interval [2.17, 2.83] is entirely above the 1.20 band edge, under 2×cap,
  1×cap and both-solved treatments, in every corpus and every cell.
- Matching C's pooled marginals is not merely insufficient; it is slightly
  worse than T, the maximum-likelihood 24-multiplier fit to the same solver
  counts (K/T 0.86 [0.77, 0.96]). T and K are the same model family (G4 ×
  24 multipliers) differing only in which 24 numbers are chosen, so the
  pooled-marginal target is a worse choice of those numbers than the ML one.
- K is still better than raw G4 (K/G4 ≈ 1.57, descriptive, unpaired) and solves
  72.5% vs G4's 63.3%, so the 24 multipliers carry some of C's content, but
  less than a third of C's log advantage over G4 by this measure.
- C/K here (2.48) is larger than question 20's 1.65 on four-reducer training
  cells; K/T (0.86) is close to question 20's 0.83. The direction replicates
  on a different bank.

## 4. What the data does not show

- It does not isolate token order or positional context as the cause. K keeps
  G4's context template, so C differs from K in both its context dependencies
  and its positional marginals (K matches only the 32-position pooled
  marginal). "Structure beyond pooled frequency" is the correct claim; "context
  is what matters" is not yet.
- It is a development bank (then-addition, 16 selected cells on which earlier
  decisions rest), so this is a mechanism/boundary result, not transfer
  evidence.
- It does not say anything about what a fragment learner would achieve; a
  large C/K sets a target, not a benefit.
- The C/K advantage is measured against the capped endpoint; C's higher solve
  rate contributes (both-solved C/K is 1.92, still well above 1.20), so the
  effect is not an artefact of censoring but is somewhat smaller on solved
  pairs.
- The K/G4 interval ignores G4's own sampling uncertainty (16 unpaired seeds
  per cell); treat it as descriptive.
- Preparation's 16-search timing cell (9/16 solved) was a timing sample only
  and is not a solve-rate estimate; the full run solved K at 72.5%.

Plot: `ck_per_corpus_cell.png` (per-corpus C/K, C/T, K/T; per-cell C/K, K/T).
The run's own `diagnostics.png` shows the solved-fraction curves ordered
C > T > K > G4 at every budget above about 4 000 evaluations.

## Against the predictions

Plan outcome table (read after the analysis above was written):

| Plan row | Condition | Data | Match |
|---|---|---|---|
| Insufficient | C/K lower bound ≥ 1.20 | C/K 2.48 [2.17, 2.83] | **yes** |
| Adequate | C/K upper bound ≤ 1.20 | upper bound 2.83 | no |
| Unresolved | interval crosses 1.20 | it does not | no |
| Stop | validation/replay fails or runtime unfit | all gates passed; 41.5 min of a 150 min timeout | no |

The data lands in the first row: this G4-based pooled-frequency replacement is
insufficient within 20% on these cells. The plan's next action for that row is
to return to strategy with the structural-learner price, with useful structure
still unidentified and fragments not established. Nothing in the data argues
against that routing.

Checks the plan asked for, and their state:

- All pre-search verifications (provenance SHA, 48 table hashes, bank SHA,
  marginal error 2.90e-5 ≤ 1e-3, 32-row bit-exact C/T replay at the current
  build, source hashes at 45b2bdb) passed in preparation; the full run
  re-verified the implementation hashes and replayed all 16 timing rows
  identically. No `infeasible.md` was needed.
- Seeds follow the planned formula (2048 distinct, paired to C and T by
  corpus/cell/seed, identical 64-case draws in all 2048 triples).
- Every secondary the plan listed is present: C/T beside C/K, K/T, the
  descriptive log share (−0.21), K/G4 with its unpaired caveat, solve counts,
  per-cell C/K, BE vs PA C/K, 1×cap and both-solved sensitivities with
  occupancy (all 16 corpora, all cells occupied in both-solved).
- The plan said an unusually strong K triggers identity checks, not changed
  thresholds. K was weak, not strong, so no such check was triggered; the
  table-hash and pairing checks ran regardless and passed.

Against the proposal's expectations: C/K was expected at 1.5–2.5× with a
lower bound well above 1.20; observed 2.48 [2.17, 2.83], at the top of the
expected range. K/T was expected at 0.8–1.1; observed 0.86 [0.77, 0.96].
Neither named surprise occurred (C/K upper bound ≤ 1.20, or K/T clearly above
1.3). The one thing worth flagging beyond the plan is that K/T's interval
excludes 1: fitting the 24 multipliers to C's pooled marginals is reliably
worse than the ML fit to the same counts, which the plan did not have a
contingency for and which the steward may want to note in question 20/29.

The plan's own caveats hold: this is a development-bank mechanism result,
with context not isolated (K keeps the G4 template and matches only pooled,
not positional, marginals), and it says nothing about fragments. The
researcher's deferred critic notes 5–8 (wording edits in questions/ and the
digest) remain for the steward at `decide`.
