---
outcome: no_useful_gain_for_this_recoding
---
# Analysis — Recoded Q: wider mutation ripple at an exactly fixed random-program distribution

Reviewer: Claude Fable 5.1 (independent of the researcher). Code `fe196c1`. Raw data in
`experiments/output/2026-10-09/2026-10-09-0537-recoded-prepare/` and `…-recoded-score/`.
All ratios below were recomputed from `search.jsonl` plus the vendored Q (0306) and C (1548) rows;
they agree with `result.json` to three decimals.

## 1. Data completeness

**The scoring entry is marked `failed` (exit 1), but the science is complete.** The traceback is a
missing `import json` in `recoded_report.py` at the very last step (the `variation.png` figure).
By then the run had already written `result.json`, `report.md` and `diagnostics.png`, and
`validation.json` reports `passed: true` with `error` absent. The only missing expected output is
`variation.png`; I regenerated the same figure from `variation.json` as `variation.png` in this folder.
Nothing in the scientific pipeline is affected: `make_report` ran with `error=None`, so
`efficacy_eligible` is true.

| Check | Result |
|---|---|
| Preparation entry | done, 512.8 s wall (limit 1 800 s) |
| Historical C solver recovery | 936/936 bit-exact |
| Identity-recoding replay of Q and C rows | 32/32 bit-exact (16 Q, 16 C) |
| Fixed maps validated and hashed | 64/64 (16 corpora × 2 doses × 2 realizations) |
| Generation-0 token hashes equal Q's | 4 096/4 096 |
| Scoring rows | 4 096/4 096, 4 096 unique keys, 0 duplicates |
| Arms | R30 2 048, R100 2 048; 16 corpora × 16 cells × 8 seeds each |
| Realizations | k=0 and k=1 each 1 024 rows per arm (seed indices 0–3 / 4–7) |
| Pairing to Q (case draws and initial-token hash) | 4 096/4 096 match (my recheck: 0 mismatches) |
| Budget convention | all rows cap 524 288, pop 256; every unsolved row has evaluations = cap |
| Timing rows (64 from preparation) replayed identically in full run | enforced by the runner; the run completed, so yes |
| Scoring wall time | 5 972 s vs admitted expectation 7 634 s and all-capped bound 10 391 s |

Reference arms: Q and C are the frozen 0306 and 1548 rows (2 048 each). My recomputed Q/C from
those rows is 2.411 [2.114, 2.749], identical to the 0306 number the proposal cites, so the
references are the right ones.

Scheduling order grouped searches by map to amortise decoder setup; setup cost totalled 386 s of
worker time over 4 096 rows (max 0.79 s per search) and is included in `seconds`, not in
evaluation counts. It does not touch the cost metric.

## 2. Key numbers

Cost = evaluations to the first D1331-exact program; unsolved = 2 × cap (primary) or 1 × cap.
Unit = corpus (n = 16, 128 paired searches each), 95 % t interval on 15 df.

### Solves (out of 2 048 per arm)

| Arm | Solved | Rate | Geometric cost (2×cap) |
|---|---|---|---|
| C | 1 771 | 0.865 | 67 720 |
| Q | 1 514 | 0.739 | 163 252 |
| R30 | 1 509 | 0.737 | 190 886 |
| R100 | 1 074 | 0.524 | 398 756 |

### Contrasts (speed ratio; > 1 means the second arm is cheaper)

| Contrast | 2×cap | 1×cap | both-solved only | corpora with ratio < 1 |
|---|---|---|---|---|
| **G = Q/R30 (primary)** | **0.855 [0.801, 0.914]** | 0.857 [0.806, 0.910] | 0.810 [0.733, 0.895] | 14/16 |
| G100 = Q/R100 | 0.409 [0.386, 0.434] | 0.475 [0.450, 0.502] | 0.473 [0.418, 0.535] | 16/16 |
| R30/R100 | 0.479 [0.455, 0.504] | 0.555 [0.532, 0.578] | 0.595 [0.546, 0.649] | 16/16 |
| H = R30/C | 2.819 [2.488, 3.193] | 2.580 [2.303, 2.890] | 2.272 [2.051, 2.517] | 0/16 |
| Q/C (reference) | 2.411 [2.114, 2.749] | 2.210 [1.966, 2.484] | 1.954 [1.714, 2.228] | 0/16 |

Decision rule on G: upper bound 0.914 ≤ 1.20 → **no useful gain**. The same holds for R100
(upper bound 0.434). R30/C upper bound 3.19 > 1.5 → does not approach C. Descriptive gap share
log(Q/R30)/log(Q/C) = −0.18 (R30 moves *away* from C by about a sixth of the Q–C gap in log cost).

Per search (2 048 Q–R30 pairs): R30 cheaper in 878, Q cheaper in 985, tie (both unsolved) in 185.
Solve crosstab Q×R30: both 1 159, Q only 355, R30 only 350, neither 184. So R30 solves about as
often as Q but, when both solve, takes longer (both-solved G = 0.81).

Per search Q–R100: R100 cheaper in 489, Q cheaper in 1 266, tie 293. R100 loses 682 solves Q had
and gains 242.

### Spread

- Realization k=0: G = 0.829 [0.747, 0.920]; k=1: G = 0.883 [0.810, 0.962]. Both below 1; the two
  random permutations per corpus agree.
- Families: BE G = 0.836 [0.741, 0.942], PA G = 0.875 [0.801, 0.955].
- Per corpus, G ranges 0.71 (PA1) to 1.09 (BE2); only BE2 and PA2 are above 1, neither above 1.2.
- Per cell, G point estimates range 0.69 to 1.18; no cell's interval (8 seeds × 16 corpora) has a
  lower bound above 1.
- G100 per corpus ranges 0.33 to 0.48. No corpus, cell, family or realization shows R100 ≥ R30.

Plots: `ratios.png` (per-corpus bars and the five contrasts with both-solved sensitivity),
`variation.png` (token-change and span histograms of the full offspring operator, all four arms),
and the run's own `diagnostics.png` (solve fraction vs evaluations: C above Q, R30 tracking Q
slightly below until the end, R100 well below; R100 also shows lower behavioural diversity among
active runs).

### Variation audit (did the recoding do what it was built to do?)

Mean over corpora and realizations, 4 096 uniform parent tapes per corpus:

| Arm | tokens changed / single resample | of which downstream | P(≥4) | Bernoulli 0.03 | crossover | full offspring |
|---|---|---|---|---|---|---|
| C | 2.95 | 2.08 | 0.31 | 2.68 | 10.32 | 11.99 |
| Q | 1.71 | 0.83 | 0.09 | 1.62 | 10.33 | 11.36 |
| R30 | 3.00 | 2.12 | 0.31 | 2.71 | 10.33 | 12.02 |
| R100 | 7.71 | 6.82 | 0.64 | 6.17 | 10.33 | 13.96 |

R30's mutation footprint matches C's on every corpus (max |R30 − C| single-resample mean 0.29
tokens, cf. proposal's 0.2 claim at a slightly different n). On the 936 C-solver tapes the same
ordering holds (C 2.52, Q 1.68, R30 2.90, R100 6.81), so the matching is not an artefact of
uniform parents. Crossover changes the same number of tokens in all arms (it is a tape-level
operator; the recoding only alters which tokens, not how many). The intervention therefore
delivered its target: R30 has C's mutation width at Q's exact random-program distribution.

## 3. What the data shows

1. **Widening Q's mutation ripple to C's width, at an exactly fixed random-program distribution,
   makes search slower, not faster.** R30 costs 1.17× Q [1.09, 1.25] (inverting G). The interval
   excludes 1, so this is a real loss on this bank, not just a failure to gain. It is consistent
   across both realizations, both families, 14/16 corpora and all cost conventions.
2. **Dose–response is monotone in the wrong direction.** Full-row permutation (R100) costs
   2.4× Q [2.3, 2.6] and roughly halves the solve rate (0.52 vs 0.74). R100 > R30 > Q in cost,
   with no overlap of intervals.
3. **R30 ends up 2.8× slower than C** despite having C's footprint. The fitted-C advantage of
   2.4× over Q is therefore not reproduced by width alone. Nothing here says what in C's rows
   produces it; the gap share of −0.18 is arithmetic, not mediation.
4. **Shortcut solutions do not explain the ordering.** Training-perfect-but-not-exact programs per
   search average Q 59, R30 67, R100 15, C 210 (unique shortcuts). C has the most shortcuts and
   the fastest exact solves; R100 has the fewest and is slowest. Shortcut rate tracks how much
   training-perfect material a run produces, not an exploit by any arm.

## 4. What the data does not show

- It does not bound *all* wider-mutation recodings. The permutations were random within rows;
  a structured recoding (for example one that preserves local token neighbourhoods) was not
  tested. "No useful gain" applies to these two frozen random recodings on this development bank.
- It does not separate mutation width from the other things the recoding changes: allele–token
  correlations, crossover's effective behaviour on the tape, and the local structure of the
  initial population after the inverse-mapping of generation 0. The scope line in `result.json`
  says the same.
- It does not say that C's conditional content is necessary. It says that at Q's distribution,
  adding undirected coupling of C's magnitude hurts. C's rows might win through content, through
  structured (not random) coupling, or both.
- Transfer is out of scope: one development bank, frozen maps, one operator set.
- The resolution price fields in `result.json` are moot (both doses are already bounded away from
  the 1.20 threshold with n = 16).

## 5. Notes for the decision

- Re-run cost: the whole cycle is reproducible from `fe196c1` with the vendored Q/C sources; the
  only defect is the missing import, which should be fixed (one line) before any reuse of
  `recoded_report.py`, and the queue status for the scoring entry should be read as "complete,
  reporting crashed after results were written".
- Runtime: scoring took 1 h 40 min against a 3 h 20 min timeout, so the 1.15× expected price was
  conservative by about 28 %.

## Against the predictions

The plan fixed four interpretation branches on G = Q/R30 (unsolved = 2 × cap, 95 % t interval over 16 corpora) and a conditional label on R100.

| Plan branch | Condition | Observed | Met? |
|---|---|---|---|
| Useful gain at fixed uniform-prior supply | G lower bound ≥ 1.20 | G = 0.855 [0.801, 0.914] | no |
| No useful R30 gain | G upper bound ≤ 1.20 | 0.914 ≤ 1.20 | **yes** |
| No useful gain at either dose | also R100 upper bound ≤ 1.20 | G100 = 0.409 [0.386, 0.434] | **yes** |
| Unresolved | G crosses 1.20 | interval entirely below 1 | no |
| Approaches C | H upper bound ≤ 1.50 | H = 2.819 [2.488, 3.193] | no; bounded outside 1.5 |

**Outcome label: no useful gain for this recoding, at either dose.** This is the plan's second branch with its R100 clause satisfied, and it is what the proposal called the expected result ("Q/R30 0.85–1.10 and R100 slower than Q"). The point estimate for G, 0.855, sits at the bottom edge of the proposal's expected band, and R100 is slower than the proposal's 0.6–0.9 guess (0.41). Neither "surprise" condition occurred: no lower bound ≥ 1.2, and R100 did not beat R30 (R30/R100 = 0.479 [0.455, 0.504], R100 is the slowest arm on all 16 corpora).

The plan's pre-stated caveats all apply and the data gives no reason to weaken them:

- The plan said a null "bounds these recodings, not all wider mutation and not the necessity of C's conditional rows". Correct: the two tested recodings are random within-row permutations, which also scramble allele–token correlations and alter what crossover does on the tape. The result says undirected coupling of C's magnitude is harmful at Q's distribution; it does not say width per se is harmful, and it does not say C's rows are necessary.
- The plan asked whether the C-matched footprint transports to solver tapes. It does: on the 936 recovered C-solver tapes R30's single-resample mean is 2.90 against C's 2.52 and Q's 1.68, the same ordering as on uniform tapes, so the null is not weakened by poor transport. If anything R30 is slightly wider than C on solver tapes while still being 2.8× slower, which strengthens the reading that width alone is not what C buys.
- Gap share (−0.18) was pre-declared as arithmetic, not mediation; it is reported as such.
- The plan's resolution-price machinery is not needed: both doses are bounded with n = 16.

Under the proposal's "next action" the matching branch is "No useful gain at either dose: end the recoding line. This favours dependency-carrying targets but does not prove C's rows are necessary." The data supports exactly that and nothing stronger. One qualification worth carrying forward: the effect is a *loss* with an interval excluding 1 (R30 costs 1.17× Q [1.09, 1.25]), so locality has measurable value in this representation. A structured, locality-preserving recoding is a different hypothesis that this experiment did not test.

Operational note for the steward: the scoring entry's `failed` status is a one-line missing import in the final plot, after all results were written. Treat the run as complete; fix the import before the report module is reused.
