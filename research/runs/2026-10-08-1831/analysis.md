---
outcome: useful
---

# Analysis: partial-program context vs token fit (2026-10-08-1831)

Reviewer analysis of `experiments/output/2026-10-08/2026-10-08-1831-partial-program-context/`
(code `998a9fe`, queue exit 0, wall 7 202 s against a 7 269 s smoke projection). All numbers
below were recomputed from `search.jsonl`; they agree with the runner's `result.json` and
`report.md` to the printed precision. Plot: [analysis_contrasts.png](analysis_contrasts.png).

## 1. Data completeness

Complete. Nothing is missing, duplicated or errored.

| Check | Expected | Found |
|---|---:|---:|
| Rows in `search.jsonl` | 7 168 | 7 168 (2 048 collection + 5 120 training) |
| Collection cells × sources | 64 × 32 | 64 × 32, all with 32 rows |
| Training (corpus, cell, arm) combos × seeds | 320 × 16 | 320 × 16, no duplicate keys |
| Arms per fresh seed | 5 | 1 024 seed groups, every one has exactly {C_S, T_S, C_P, C_exact, G4} |
| Corpora analysed | 16 (8 BE_i/PA_i pairs) | 16, all 8 pairs complete, `stop_kind` null |
| Seed overlap collection vs training | 0 | 0 (2 048 + 1 024 distinct seeds) |
| Table hash | one G4 table | one hash on all 2 048 collection rows; 4 096 pairing checks passed |
| Archive verifications on D1331 | all archived tapes | 89 536 passed; 0 exact tapes archived; 0 holdout searches |
| Empty cells | 0 | 0 (29–32 contributing sources per cell) |

Collection behaved as designed. Of 2 048 sources, 47 / 150 / 351 had solved by the 64 / 128 / 256
population checkpoints (2.3 / 7.3 / 17.1%; the proposal assumed 2.1 / 6.2 / 14.9% from 1246).
Each unsolved source contributed 8 S + 8 P tapes per checkpoint: 2 001, 1 898 and 1 697 sources
at the three checkpoints, 89 536 tapes in total, 44 768 of each kind. 58 archived tapes were
training‑perfect but not exact (plan excluded only exact solvers, so this is per spec). 8 080 of
89 536 archive rows (9.0%) came from sources that solved later within the 65 536 cap; per cell
0–32.5%. Duplicate rate among S tapes 3–9% per cell, among P tapes 0.6–3%.

Archived tape quality differs strongly by kind: mean D1331 accuracy 0.68 (S) vs 0.49 (P); mean
training accuracy for S rises 0.66 → 0.72 → 0.76 across the three checkpoints, for P
0.48 → 0.51 → 0.53.

## 2. Key numbers

Unit: corpus (n = 16, 8 BE + 8 PA). Each corpus score is the mean over its 4 own training cells
of the mean over 16 paired fresh seeds of log cost(right) − log cost(left); cost = evaluations
to an exact D1331 solve, else 2 × 524 288. Interval: 95% t over the 16 corpus scores.
"Solved" means exact on the full 1 331-row table; training-perfect non-exact tapes
(shortcuts) never count as solves.

### Solve rates and median cost (1 024 searches per arm = 16 corpora × 4 cells × 16 seeds)

| Arm | Solved | Rate | Median cost (evals) | Searches with ≥1 shortcut |
|---|---:|---:|---:|---:|
| C_exact | 925 / 1 024 | 90.3% | 38 656 | 101 |
| C_S | 746 / 1 024 | 72.9% | 166 144 | 107 |
| C_P | 749 / 1 024 | 73.1% | 183 040 | 110 |
| T_S | 674 / 1 024 | 65.8% | 237 312 | 66 |
| G4 | 624 / 1 024 | 60.9% | 324 992 | 34 |

### Contrasts (speed ratio, 95% interval, n = 16 corpora)

| Contrast | 2 × cap (primary convention) | 1 × cap | Both-solved pairs only | Corpora > 1 (2 × cap) |
|---|---|---|---|---:|
| **C_S / T_S** (primary) | **1.28 [1.12, 1.45]**, SD 0.24 log | 1.22 [1.09, 1.36] | 1.05 [0.88, 1.24] | 13 / 16 |
| **C_S / G4** | **1.62 [1.37, 1.90]**, SD 0.30 log | 1.49 [1.30, 1.70] | 1.41 [1.21, 1.64] | 16 / 16 |
| C_S / C_P | 1.04 [0.92, 1.16] | 1.04 [0.94, 1.14] | 1.02 [0.85, 1.23] | 8 / 16 |
| C_S / C_exact | 0.27 [0.24, 0.30] | 0.31 [0.28, 0.33] | 0.36 [0.32, 0.41] | 0 / 16 |
| T_S / G4 | 1.27 [1.10, 1.45] | 1.22 [1.08, 1.38] | 1.25 [1.01, 1.56] | 13 / 16 |
| C_P / G4 | 1.56 [1.32, 1.84] | 1.43 [1.24, 1.66] | 1.34 [1.11, 1.61] | 16 / 16 |
| C_exact / G4 | 5.97 [5.26, 6.78] | — | — | 16 / 16 |

Paired seeds (1 024 pairs): C_S cheaper than T_S in 506, dearer in 407, tied (both capped) in 111.
C_S cheaper than G4 in 550, dearer in 342, tied in 132. C_S solved more often than T_S in 12 of
16 corpora (+72 solves overall).

### By family (n = 8 corpora each, 2 × cap)

| Contrast | BE | PA |
|---|---|---|
| C_S / T_S | 1.42 [1.17, 1.72] | 1.15 [0.96, 1.38] |
| C_S / G4 | 1.86 [1.40, 2.48] | 1.40 [1.20, 1.64] |
| C_S / C_P | 1.02 [0.84, 1.25] | 1.05 [0.88, 1.25] |
| T_S / G4 | 1.31 [1.01, 1.71] | 1.22 [1.02, 1.45] |

### By training cell (128 searches per arm per cell, 8 corpora pooled; descriptive)

| Cell | C_S / T_S | C_S / G4 | Solved C_S / T_S / G4 of 128 |
|---|---:|---:|---|
| BE:F>S?F:M+m | 1.57 | 1.97 | 74 / 55 / 52 |
| BE:F>m?S:F+M | 0.80 | 1.23 | 81 / 91 / 74 |
| BE:S>F?M:F+m | 1.92 | 2.18 | 101 / 74 / 66 |
| BE:S>F?m:M+S | 1.66 | 2.26 | 109 / 100 / 89 |
| PA:(F>S?F:m)+M | 1.25 | 1.63 | 70 / 63 / 52 |
| PA:(F>S?m:M)+F | 1.24 | 1.59 | 101 / 89 / 88 |
| PA:(M>F?m:S)+S | 0.83 | 1.00 | 104 / 105 / 100 |
| PA:(S>F?M:m)+m | 1.37 | 1.50 | 106 / 97 / 103 |

## 3. What the data shows

1. **Context fitted to pre-solution tapes beats the token fit to the same tapes, on the
   penalized endpoint.** C_S / T_S = 1.28 [1.12, 1.45]; 13 of 16 corpora positive, Wilcoxon
   over corpora p = 0.002. The interval excludes 1 but contains the 1.20 worthwhile margin, so a
   worthwhile gain is plausible, not established. The direction survives the 1 × cap convention
   (1.22 [1.09, 1.36]).

2. **Where the C_S advantage over T_S lives.** Among pairs where both arms solved, C_S / T_S is
   1.05 [0.88, 1.24]: no resolved speed difference. The penalized advantage comes from C_S solving
   within the cap more often (72.9% vs 65.8%), not from reaching solutions faster when both
   succeed. Both-solved conditioning is selection-biased, so this is a decomposition, not a
   separate test; but it means the gain is a reliability gain under the 2 × cap penalty.
   C_S / G4, by contrast, holds in the both-solved subset too (1.41 [1.21, 1.64]).

3. **Partial-program context beats fresh G4 search clearly.** C_S / G4 = 1.62 [1.37, 1.90],
   all 16 corpora positive. About half of that log gain is already delivered by the token fit
   (T_S / G4 = 1.27, log 0.24 of 0.48); the previous-token context adds the other half.

4. **No resolved parent-selection enrichment.** C_S / C_P = 1.04 [0.92, 1.16] despite S tapes
   being far more accurate than P tapes (D1331 0.68 vs 0.49). An effect above 1.16× is excluded.
   Uniform population samples carry about as much usable context as lexicase-selected parents.

5. **Partial context recovers a minority of the exact-corpus value.** C_exact / G4 = 5.97
   [5.26, 6.78]; C_S captures 27% of that log gain (C_S / C_exact = 0.27 [0.24, 0.30]).
   The acquisition budgets differ by roughly 5–6× in source evaluations per cell (≤ 66k × 32
   here versus ≈ 250k × 48 for 1246's exact corpora, per the proposal), so this is not a
   per-evaluation efficiency comparison.

6. **Family and cell heterogeneity.** The primary is carried by BE (1.42 [1.17, 1.72]); PA alone
   is unresolved (1.15 [0.96, 1.38]). Two of the eight cells show C_S / T_S below 1 (0.80 and
   0.83); they are the two cells where T_S solves most often (91 and 105 of 128). Context seems to
   help most where the token fit struggles. With four cells per family this is a pattern to
   watch, not a finding.

7. **Shortcuts.** Fitted decoders hit training-perfect but non-exact tapes about three times as
   often as G4 (C_S 107, C_P 110, C_exact 101, T_S 66, G4 34 of 1 024 searches). The endpoint
   requires exactness on D1331, so this does not inflate any arm; it does show the fitted
   priors concentrate search on tapes that fit the 64 training cases, true or not.

8. **The capped-arm caution does not apply.** `almost_all_primary_capped` is false; partial-arm
   solve rates are 66–73%, so the penalized comparison reflects genuine search differences.

## 4. What the data does not show

- Not a worthwhile (≥ 1.20×) C_S / T_S gain: the interval spans it. To put the lower bound
  above 1.20 at the observed point estimate and SD (0.24 log) would need roughly 64 corpora,
  i.e. about 24 more BE/PA pairs at ≈ 15 min each (≈ 6 h queue), and would only pay if the point
  estimate held. The runner's own sizing block reports the same conclusion (no finite add-on
  excludes the margin from the current estimate).
- Not transfer: development bank, own training cells, no holdout, no fresh bank, no K scoring.
  The C/T difference is a fitting-procedure difference (α 50 context estimator vs bounded token
  estimator on identical counts), not an isolated-order effect.
- Not a statement about complete solvers adding nothing or everything: C_exact wins by a wide
  margin, but with a different acquisition budget.
- Not a per-horizon result: one collection cap (65 536), three checkpoints, 8 + 8 tapes each.
  Whether later checkpoints or more tapes per source would close the gap to C_exact is untested.
- The 2 × cap penalty is a convention; under 1 × cap the same labels hold with narrower ratios.

## 5. Pre-stated routing (from the proposal's decision rule)

Upper bound of C_S / T_S is 1.45, not below 1.20, so the "bounded" branch does not fire.
Lower bound 1.12 > 1.0 and C_S / G4 lower bound 1.37 > 1.0, so the data lands in the
"useful partial-program context" branch: resolved relative and G4 improvements, worthwhile
gain still plausible. The sub-finding that the C_S / T_S gain is a cap-reliability gain rather
than a speed gain among solved pairs should travel with that label.

## Against the predictions

plan.md's routing has four labels. The data match **useful**: the C_S / T_S upper bound (1.45)
is not below 1.20, so the precedence branch does not fire; the C_S / T_S lower bound (1.12)
and the C_S / G4 lower bound (1.37) are both above 1. As the plan words it, this is "useful
partial-context fitting with a worthwhile effect still plausible, not an established 1.20×
improvement".

The plan's required preconditions for interpreting the cost endpoint were met: solve rates,
the 1 × cap sensitivity and the both-solved sensitivity are all reported above, and the
"almost universal caps" situation did not arise (61–73% solved in the non-exact arms).

Against the proposal's stated expectations:

| Expectation | Observed | Verdict |
|---|---|---|
| C_S / T_S ≈ 1.3–2× | 1.28 [1.12, 1.45] | At the low edge; point estimate just under the expected range, interval overlaps it |
| C_P ≈ C_S | C_S / C_P 1.04 [0.92, 1.16] | As expected |
| C_S / C_exact ≈ 0.5–0.8 | 0.27 [0.24, 0.30] | Well below expectation: partial context recovers about a quarter of the exact-corpus log gain over G4, not half or more |
| Surprise: C_S not above T_S | Above, 13 / 16 corpora | Did not occur |
| Surprise: C_S below G4 (shortcuts mis-teach) | 1.62× above G4, 16 / 16 corpora | Did not occur |
| Surprise: C_S ≈ C_exact | Far from it | Did not occur |
| Surprise: C_P clearly better than C_S | No | Did not occur |

Two things the plan did not anticipate and the steward should weigh:

- The C_S / T_S advantage is a within-cap reliability gain, not a speed gain among solved pairs
  (both-solved 1.05 [0.88, 1.24]). The plan listed the both-solved sensitivity as a check against
  uninformative capping, not as a decomposition; here it changes how the primary should be read.
- The gain is concentrated in BE (1.42) and in the cells where T_S solves least; PA alone is
  unresolved (1.15 [0.96, 1.38]). A feedback stage built on this collector would rest mainly
  on the BE half of the bank unless more PA corpora resolve it.

The plan's "price additional independent corpora" clause applies only to the unresolved label,
but the same arithmetic is relevant to the feedback decision: establishing the 1.20× margin
from the current estimate would need about 64 corpora in total (≈ 6 h more queue), and only if
the point estimate held.
