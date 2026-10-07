---
outcome: "row 1: source-attributed training gain (C2/C 1.40x, C2/C' 1.41x) with holdout transfer on both contrasts"
---

# Analysis: one feedback refit of the solver-corpus decoder (1924)

Reviewer: claude-fable-5-1. Code: `5565d54` on `research/2026-10-07-1924`. Output:
`experiments/output/2026-10-07/2026-10-07-1924-solver-feedback/` (`search.jsonl`, `result.json`,
`corpora.json`, `timing.json`, `admission.json`, `validation.json`). All numbers below were
recomputed from `search.jsonl` with an independent script and match `result.json` to three decimals
unless marked.

## 1. Data completeness

Complete. Every stage ran at full size and nothing is missing, duplicated or truncated.

| phase | arm | rows found / expected | solved |
|---|---|---|---|
| replay (1707 GG rows) | GG | 40 / 40 | bit-identical to 1707 (validation `replay.passed`) |
| A: collection under C | C | 7 680 / 7 680 (32 lineages × 48 × own cells) | 7 623 |
| B: training | C, C2 | 5 120 / 5 120 each | C 5 081, C2 5 106 |
| C: holdout | C, C2 | 3 072 / 3 072 each | C 3 042, C2 3 049 |
| D: collection under G4 | G4 | 7 680 / 7 680 | 7 378 |
| D: training | C' | 5 120 / 5 120 | 5 082 |
| D: holdout | C' | 3 072 / 3 072 | 3 023 |
| total | | 39 976 | |

- Zero duplicate (phase, arm, corpus, cell, seed) keys. All rows at cap 524 288, population 256.
- Pairing: all 256 lineage × cell groups (training 160, holdout 96) have 32 seeds per arm, with
  identical seed sets and identical `training_indices` across C, C2 and C'. No unpaired rows.
- Validation passed: 32 parent tables hash to 1707's C hashes; 224 fitted tables pass
  `validate_table`; all 7 408 saved 1707 solvers and all 15 040 new solvers re-verified exact on
  the 1 331 inputs; the bank sha and G4 hash match.
- Stage D was admitted at full size (32 lineages) by the timing gate alone: 4 196 s remained
  against a projection of 2 638 s × 1.25. No result entered the gate. Queue exit 0, wall 72.9 min
  (A 12.2, B 10.2, C 7.3, D collection 31.6, D training 6.4, D holdout 4.7), within the
  proposal's 75–80 min projection. `stop_reason` null, `control_valid` true.
- Yield floor (24/48 per cell under C): the worst cell was 44/48 (three BE lineages on
  `BE:F?S:(M+m)`); 121/160 cells gave 48/48. Row 0 is not triggered.
- Exactness is enforced: training-perfect but non-exact individuals ("shortcuts") are rejected and
  the search continues. Such rejections occurred in 94–109 of 5 120 training searches per arm and
  are similar across arms, so no arm wins by accepting shortcuts.

## 2. Key numbers

Estimator as pre-stated: per lineage and arm, mean over cells of the per-cell mean log2
evaluations (unsolved = 2 × cap); contrasts are per lineage; training pooled with equal family
weight (t on 15 df); holdout one-sample over 32 lineages (31 df). Speed ratio = 2^(−Δ), >1 means
the first arm is faster.

### 2.1 Pre-stated contrasts

| phase | contrast | speed ratio | 95% interval | Δ log2 | per-family | lineages with first arm faster |
|---|---|---|---|---|---|---|
| training (primary) | **C2/C** | **1.404** | **[1.347, 1.464]** | −0.490 ± 0.060 | BE 1.558 [1.463, 1.659], PA 1.265 [1.198, 1.336] | 32/32 |
| training | C2/C' | 1.408 | [1.342, 1.478] | −0.494 ± 0.070 | BE 1.486, PA 1.334 | 32/32 |
| training | C'/C | 0.997 | [0.940, 1.058] | +0.004 ± 0.085 | BE 1.048, PA 0.948 | 15/32 |
| holdout | **C2/C** | **1.289** | **[1.204, 1.381]** | −0.367 ± 0.099 | BE 1.280, PA 1.299 | 28/32 |
| holdout | C2/C' | 1.330 | [1.263, 1.401] | −0.412 ± 0.075 | BE 1.318, PA 1.343 | 31/32 |
| holdout | C'/C | 0.969 | [0.908, 1.035] | +0.045 ± 0.094 | BE 0.972, PA 0.967 | 11/32 |

Holdout labels under the pre-stated rule: C2/C **transfers**, C2/C' **transfers**. Applying the
same rule to the replication contrast C'/C gives "no transfer above 10%" (lower 0.908 ≤ 1 ≤ upper
1.035 < 1.10); the code's label field reports only the two C2 contrasts, so this one is mine.

Per-lineage values are in [lineage_contrasts.png](lineage_contrasts.png). The training C2/C
contrast is positive in every one of the 32 lineages (range 1.09× to 1.84×); the smallest BE value
(1.26×) exceeds the largest C'/C value in that family. Per-cell values are in
[cell_contrasts.png](cell_contrasts.png).

### 2.2 Robustness of the primary contrast (descriptive, not pre-stated)

| statistic | training C2/C | holdout C2/C |
|---|---|---|
| pre-stated mean log2, unsolved = 2 × cap | 1.404 [1.347, 1.464] | 1.289 [1.204, 1.381] |
| median per cell | 1.330 [1.267, 1.397] | 1.267 [1.171, 1.372] |
| solved pairs only | 1.365 [1.309, 1.424] | 1.277 [1.194, 1.366] |
| share of paired seeds where C2 strictly faster (mean over lineages) | 0.577 (min 0.51, max 0.66) | 0.559 |

The gain is a shift of the whole distribution rather than a penalty artefact: training evaluation
quantiles (10/50/90/99 %) are C 1 536 / 4 352 / 22 272 / 351 915 against C2 1 024 / 3 328 / 13 824
/ 166 986; unsolved searches fall from 39 to 14 of 5 120. Per paired seed the advantage is modest
(C2 wins about 58% of pairs); the 1.4× is a mean-of-logs effect driven by the upper tail.

### 2.3 Per cell (descriptive; the design does not pre-state per-cell claims)

Mean over 16 lineages of the per-cell C2/C ratio, 95% t on 15 df:

| cell | phase | C2/C | C mean log2 evals |
|---|---|---|---|
| BE:F?S:(M+m) | training | 1.48 [1.29, 1.71] | 12.47 |
| BE:F?m:(S+M) | training | 1.41 [1.25, 1.59] | 11.88 |
| BE:S?F:(M+m) | training | 1.54 [1.31, 1.82] | 12.13 |
| BE:S?M:(m+F) | training | 1.83 [1.58, 2.12] | 12.48 |
| PA:(F?S:m)+M | training | 1.33 [1.15, 1.53] | 12.64 |
| PA:(F?m:M)+S | training | 1.23 [1.09, 1.39] | 12.12 |
| PA:(F?m:S)+M | training | 1.38 [1.23, 1.55] | 12.44 |
| PA:(S?M:F)+m | training | 0.98 [0.84, 1.13] | 12.98 |
| PA:(S?m:F)+M | training | 1.39 [1.23, 1.58] | 12.48 |
| PA:(S?m:M)+F | training | 1.34 [1.24, 1.45] | 11.80 |
| BE:S?m:(M+F) | holdout | 1.36 [1.23, 1.51] | 11.59 |
| PA:(F?S:M)+m | holdout | 1.24 [1.02, 1.50] | 13.14 |
| PA:(S?M:m)+F | holdout | 1.25 [1.07, 1.46] | 12.22 |

One training cell, `PA:(S?M:F)+m` (the hardest PA training cell), shows no gain on its own. The
hardest cell overall, holdout `PA:(F?S:M)+m`, has the widest holdout interval and is barely above
1 alone. Thirteen cells with t intervals is a multiplicity-prone readout; take it as a pattern
(BE cells gain more than PA cells, hard cells gain less), not as cell-level findings.

### 2.4 Collection, yields and tape diversity

| | under C (feeds C2) | under G4 (feeds C') |
|---|---|---|
| solved / attempted | 7 623 / 7 680 (99.3%) | 7 378 / 7 680 (96.1%) |
| cells below 48/48 | 39 / 160 (min 44) | 93 / 160 (min 38) |
| distinct tapes per BE corpus (of 192 attempts) | 184–192 | 165–183 |
| distinct tapes per PA corpus (of 288) | 286–288 | 280–287 |
| worker-s per search | 0.63 | 2.17 |
| geometric-mean evaluations per search | 5 207 | 17 310 |

So the C-collected corpora are both slightly larger (about 3% more tapes) and slightly more
diverse than the G4-collected ones, at about 29% of the cost. These differences are part of the
"source-decoder procedure" that C2/C' measures; they are not separated from any difference in the
kind of tape C finds.

### 2.5 Table readouts (mean over 32 lineages, range)

| metric | C (parent) | C2 | C' |
|---|---|---|---|
| mean body-row entropy (bits) | 3.907 [3.88, 3.93] | 3.800 [3.75, 3.84] | 3.905 [3.89, 3.93] |
| previous-token mutual information (bits) | 0.407 [0.40, 0.43] | 0.480 [0.46, 0.50] | 0.409 [0.39, 0.42] |
| start-row entropy (bits) | 2.864 | 2.826 | 2.901 |
| start-row top-token share | 0.575 | 0.581 | 0.568 |

C2 is sharper than its parent in every lineage (body-row entropy down about 0.11 bits, MI up about
0.07 bits), and C' is indistinguishable from C on these readouts. The sharpening is the expected
signature of fitting to tapes found under an already-biased decoder. At this one step it comes with
a holdout gain, not a holdout loss. The start row barely moves, so the gain is not a sharper first
token prior by these measures (the start row's causal contribution remains unmeasured).

### 2.6 Cost and break-even (descriptive)

- Second-round collection under C cost 4 821 worker-s in total (mean 151 per lineage, median
  break-even about 390 training searches or 430 holdout searches by worker-seconds; by penalised
  evaluations, median 351 and 318).
- Per-search cost on training: C 0.708 s, C2 0.453 s, C' 0.730 s. On holdouts: C 0.760, C2 0.643,
  C' 0.890.
- The worker-second saving is noisier than the evaluation saving: 8/32 lineages (all PA) show no
  worker-second saving on training despite positive evaluation savings, and 13/32 on holdouts.
  Seconds depend on load and program cost; evaluations are the cleaner measure.

### 2.7 Conditional sizing (from `result.json`, at observed mean and sd)

Training C2/C would have resolved > 1 with about 3 lineages per family; the holdout with about 6
lineages. C'/C would need about 8 lineages per family (training) or 12 lineages (holdout) to bound
its upper limit below 1.10. These are conditional on the observed effects and are reported only
because the plan asks for them.

## 3. What the data shows

1. **The feedback refit beats its parent on fresh training searches**, 1.40× [1.35, 1.46], in all
   32 lineages, in both families (BE 1.56×, PA 1.27×), and under median- and solved-only variants.
   This is a clean, well-replicated result at the pre-stated precision (half-width 0.06 log2,
   better than the planned 0.09).
2. **The gain transfers to the three withheld cells**, 1.29× [1.20, 1.38], in 28/32 lineages. The
   withheld cells were never used to fit C or C2, so this is an out-of-fit test, though the same
   three cells have now been inspected in several runs (1707, crossed learning) and were chosen
   by the researchers, not drawn at random.
3. **A fresh one-shot refit from G4-collected tapes reproduces the parent** (C'/C 0.997 [0.94,
   1.06] training, 0.969 [0.91, 1.04] holdout). This replicates 1707's fit with new code, new
   seeds and new corpora. It also rules out "any second corpus of the same size helps": matched
   attempts under G4 give nothing.
4. **The increment is attributable to collecting under C rather than G4** (C2/C' 1.41× [1.34,
   1.48] training; 1.33× [1.26, 1.40] holdout, 31/32 lineages). "Collecting under C" is a
   procedure that bundles higher yield (99.3% vs 96.1%), more distinct tapes, and whatever
   systematic difference exists in which tapes C finds; the design does not separate these.
5. **The refit sharpens the decoder** (lower body-row entropy, higher previous-token MI) in every
   lineage. At one step this did not harm withheld cells.

## 4. What the data does not show

- It does not show that a second or third feedback step would help. One external refit with a
  frozen rule, shrunk toward G4, was tested. Amplification is visible in the table readouts and
  could compound.
- It does not show *why* C2 is faster: no token-only refit T2, no start-row ablation, no
  active-token analysis. The contextual, yield and diversity components are confounded within
  C2/C'. Whether C2 simply re-emits tapes from its own corpus could not be checked because
  training and holdout rows do not store solver tapes; the holdout transfer argues against pure
  memorisation but does not quantify it.
- It does not show family specificity or a general-family claim; three withheld cells, one of them
  BE, cannot. Per-family contrasts are confounded with cell count and difficulty.
- It does not establish a compounding "C2 vs G4" number. That contrast was not run; multiplying
  1707's C/T by this run's C2/C would assume independence that was not tested.
- The per-cell pattern (BE > PA, hardest cells gain least, one PA training cell at 0.98×) is
  suggestive only.
- Cost claims are per-search evaluation savings against a one-off collection cost; they do not
  include the cost of the first round or of any further step.

## Against the predictions

Plan rows (disjoint, evaluated in the plan's order 0, 1, 2, 4, 3, 5 on the pooled stage-B C2/C):

| row | condition | data | met |
|---|---|---|---|
| 0 | invalid A/B, any C yield < 24/48, validation failure, incomplete B | all validation passed, min yield 44/48, B complete 10 240/10 240 | no |
| **1** | C2/C lower > 1 **and** complete C2/C' lower > 1 | C2/C lower 1.347; C2/C' lower 1.342 on the complete 32-lineage roster | **yes** |
| 2 | C2/C lower > 1, C2/C' not resolved or D not run | — | no (row 1 takes precedence) |
| 4 | C2/C upper < 1 | upper 1.464 | no |
| 3 | lower ≤ 1 ≤ upper < 1.10 | — | no |
| 5 | otherwise | — | no |

**Row 1 is met**: a further training gain attributable to this source-decoder procedure, including
its yield and diversity effects, exactly as the plan scopes it.

Holdout rule: both holdout contrasts have lower > 1 (C2/C 1.204, C2/C' 1.263), so by the plan's
definition this is **source-attributed useful feedback**: row 1 plus transfer on both holdout
contrasts. The code's `source_attributed_transfer` flag is true and I agree with it.

Plan-specified descriptive items, checked:
- C'/C replication of the one-shot fit, expected ≈ 1: observed 0.997 [0.940, 1.058] training and
  0.969 [0.908, 1.035] holdout. As expected. The plan's warning that a resolved C'/C gain would
  mean "fresh-control improvement, not an unrepresentative parent" does not arise.
- Per-family C2/C reported descriptively (BE 1.56×, PA 1.27×); no family-specificity claim is
  made, as the plan requires.
- Table readouts, yields, distinct tapes and break-even are reported (sections 2.4–2.6).
- Conditional sizing is reported although nothing is unresolved (section 2.7).
- Precision: the plan assumed sd 0.25 log2 per family and a pooled half-width of about 0.09.
  Observed per-family sd was 0.17 (BE) and 0.15 (PA), half-width 0.06. Better than planned.
- Timing: the plan projected 75–80 min and full D admission if a queue started before about
  20:45 Stockholm. The queue started at 20:10, D was admitted at full size, and the run took
  72.9 min.

Things the plan said not to claim, and which this analysis does not claim: equality of C' and C
(the interval allows ±6%), general saturation, a start-row mechanism, a generic-assembly
explanation, family specificity, absence of overfitting, and anything about a second feedback
step. The plan authorises no second refit; the decision returns to strategy.

Reviewer's confidence: high that one feedback step gives a further gain of this size at this
scope (32 independent lineages, all positive, holdout transfer resolved). Low on mechanism, which
the design does not address.
