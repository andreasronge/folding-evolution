---
outcome: material_saving_recipe_extends_return_to_strategy
---
# Analysis — signed-gate acquisition (1938)

Reviewer, independent recompute from the raw `score.jsonl` rows in
`experiments/output/2026-10-11/2026-10-11-1938-{prepare,development,protected}/`
(code commit `9da9c2c`). All numbers below were recomputed from rows, not copied
from `report.json`; where both exist they agree to the stated precision. My
bootstrap uses a different seed (777, 10 000 draws) from the report's (202610111938, 8 192).

## 1. Data completeness

| Phase | Rows | Expected grid | Duplicates | Missing | Seed tuple shared by all 4 arms per unit | Unsolved | Capped jobs (524 288) |
|---|---|---|---|---|---|---|---|
| prepare (sources) | 2 304 | 48 cells × 24 builds × 2 | 0 | 0 | n/a | 0 | 0 |
| development | 1 152 | 4 arms × 24 × 6 cells × 2 | 0 | 0 | 288/288 | 0 | 0 |
| protected | 6 912 | 4 arms × 24 × 18 cells × 4 | 0 | 0 | 1 728/1 728 | 0 | 0 |

- All three queue entries finished with exit 0, well inside their timeouts (33 s, 52 s, 261 s wall against 1 800, 1 200, 3 600 s).
- Every destination job solved on the full 625-input domain (`solved` is set only after a full-domain check, `tree_gp_search.py:210-217`; the 64 training cases are the fitness proxy only). No job hit the restart cap; the worst job used 3 of 8 restarts.
- `evaluations` equals the sum over attempts in every row. No degenerate R-tree replay rows exist (all 24 libraries are non-empty).
- Distinct seeds equal units × 8 (13 824 protected, 2 304 development), so no seed is reused within a phase; arms share seeds per unit as designed.
- Bank admitted, verification and executor check passed, `protected_searches: 0` before scoring. Bank/method/library hashes match across the three output folders (`preparation_hash` identical).
- Acquisition: 2 304/2 304 source jobs solved (2 301 on the first attempt). Charged acquisition per build: mean 215 520 evaluations (range 185 600 – 276 992).

The dataset is complete and usable as designed.

## 2. Key numbers (protected roster, 18 cells × 24 builds × 4 repeats = 1 728 jobs per arm)

### Arm summaries

| Arm | Jobs | Solves | First-attempt solves | Capped mean evals | Median | p95 | p99 | Max | Mean worker s |
|---|---|---|---|---|---|---|---|---|---|
| R-tree | 1 728 | 1 728 | 1 689 (97.7%) | 7 775 | 3 584 | 28 672 | 68 608 | 149 760 | 0.544 |
| R-all | 1 728 | 1 728 | 1 714 (99.2%) | 4 489 | 2 560 | 11 174 | 43 756 | 134 144 | 0.291 |
| R-order | 1 728 | 1 728 | 1 679 (97.2%) | 8 692 | 4 096 | 38 054 | 69 888 | 136 704 | 0.628 |
| R-gate | 1 728 | 1 728 | 1 727 (99.9%) | 1 915 | 1 536 | 3 584 | 6 843 | 66 560 | 0.101 |

### Contrasts (ratio of pooled capped means; 95% two-way bootstrap over builds and cells, repeats retained, arms paired)

| Contrast | Evaluations | Worker seconds | Note |
|---|---|---|---|
| **R-all / R-tree (primary)** | **0.577 [0.47, 0.72]** | 0.535 [0.42, 0.69] | upper bound < 0.80 |
| R-all / R-order | 0.516 [0.44, 0.61] | 0.463 [0.38, 0.57] | new acquisition beats transported order libraries |
| R-order / R-tree | 1.118 [0.94, 1.34] | 1.154 [0.95, 1.42] | not in report; computed here |
| R-gate / R-tree | 0.246 [0.21, 0.30] | 0.186 [0.15, 0.24] | not in report; computed here |
| R-all / R-gate | 2.344 [1.99, 2.76] | 2.871 [2.30, 3.54] | |

Report values for the three reported contrasts: 0.577 [0.468, 0.715], 0.516 [0.435, 0.615], 2.344 [1.976, 2.769]. Agreement is within bootstrap noise.

Sensitivity of the primary interval to the resampling unit (recomputed): builds-only [0.50, 0.67], cells-only [0.52, 0.64], two-way [0.47, 0.72]. Both single sources of variation give the same answer.

### Pairing at the unit level (protected)

- R-all cheaper than R-tree in 1 071 of 1 728 units, equal in 81, dearer in 576.
- R-order cheaper than R-tree in 779 of 1 728, equal in 61, dearer in 888.
- Per cell (96 jobs per arm per cell): R-all/R-tree is below 1 in 18/18 cells, below 0.80 in 17/18 (range 0.33 – 0.87). R-order/R-tree is above 1 in 11/18 cells (range 0.81 – 1.91).
- Per build (72 jobs per arm per build): R-all/R-tree is below 1 in 22/24 builds, below 0.80 in 17/24 (range 0.31 – 1.17). Builds 5 and 20 are above 1 (1.17 and 1.14).

Per-cell table:

| cell | R-tree | R-all | R-order | R-gate | R-all/R-tree | R-order/R-tree |
|---|---|---|---|---|---|---|
| p02+n31 | 6320 | 4587 | 8571 | 1752 | 0.73 | 1.36 |
| p32+n10 | 10029 | 6115 | 9061 | 1779 | 0.61 | 0.90 |
| p21+n30 | 6197 | 4171 | 8808 | 1949 | 0.67 | 1.42 |
| p02+n13 | 9685 | 5672 | 8112 | 2501 | 0.59 | 0.84 |
| p30+n12 | 6992 | 3803 | 6504 | 1760 | 0.54 | 0.93 |
| p13+n02 | 7173 | 4853 | 7352 | 1816 | 0.68 | 1.02 |
| p20+n13 | 7843 | 4341 | 8856 | 1744 | 0.55 | 1.13 |
| p01+n32 | 9499 | 4059 | 7688 | 1723 | 0.43 | 0.81 |
| p10+n32 | 10616 | 3555 | 9312 | 1936 | 0.33 | 0.88 |
| p13+n20 | 6248 | 4848 | 8363 | 2163 | 0.78 | 1.34 |
| p31+n20 | 6501 | 3568 | 8832 | 1781 | 0.55 | 1.36 |
| p12+n03 | 7619 | 3512 | 9613 | 2027 | 0.46 | 1.26 |
| p30+n21 | 6173 | 3813 | 10043 | 2192 | 0.62 | 1.63 |
| p32+n01 | 8051 | 4211 | 7477 | 1840 | 0.52 | 0.93 |
| p10+n23 | 10661 | 6096 | 9211 | 1821 | 0.57 | 0.86 |
| p03+n21 | 5149 | 4461 | 9816 | 1907 | 0.87 | 1.91 |
| p20+n31 | 6792 | 4800 | 8896 | 1771 | 0.71 | 1.31 |
| p23+n10 | 8392 | 4341 | 9939 | 2005 | 0.52 | 1.18 |

### Development roster (6 seen cells × 24 builds × 2 repeats = 288 jobs per arm; descriptive)

Capped means R-tree 7 514, R-all 4 382, R-order 8 078, R-gate 1 895. R-all/R-tree 0.583 [0.39, 0.86]; R-all/R-order 0.542 [0.34, 0.88]. Same ordering as protected, wider intervals (2 repeats, 6 cells). 0 capped jobs, 288/288 solves in every arm.

### Library content and coverage (24 R-all builds)

- Signed-gate helpers kept per build: mean 8.6 of 24 (range 5 – 14). Across the 576 helper×build slots: 206 included, 151 built but not recurrent, 121 built but inadmissible, 98 never built by any solver.
- Library size: mean 37.4 semantic entries per build (29 – 44); 255 of 897 pooled entries contain IF_GT, the rest are mostly 3-node ADD/SUB forms (e.g. `ADD X1 X1` is in all 24 libraries), i.e. the `(Xc+Xc)` halves of the sources.
- Source solver census: 855/2 304 source solvers (37.1%) contain their own helper's output; 503 (21.8%) at an emittable 3–9 nodes. Stage 0 reported 37% / 23% on 192 jobs; this replicates.
- Needed-helper coverage on protected (build × cell, 432 pairs): both present 51, one present 191, none present 190.
- R-all/R-tree by coverage (pooled over the pairs in each stratum, descriptive, not pre-registered): both 0.31 (51 pairs), one 0.47 (191), none 0.77 (190). The saving is largest when the needed helpers are in the library but does not vanish when neither is.
- Correlation between helpers kept and build ratio: −0.45 over 24 builds (descriptive; see right panel of the figure).

### Economics (from report, evaluations)

- Charged acquisition A: 215 520 [206 491, 225 858] per new build; transported 1228 libraries cost 214 187 originally.
- Saving per search vs R-tree: 3 285 [1 967, 4 662]; vs R-order: 4 203 [3 141, 5 306].
- Repayment vs R-tree (owned nothing): 66 searches [46, 110]. Vs R-order owned: 51 [40, 69]. If the order libraries were also to be newly acquired, the acquisition costs cancel and R-all is ahead from the first search (cost difference at N=10: −40 693 [−66 403, −15 808]).
- Worker-seconds tell the same story with shorter repayment (41 [28, 72] searches vs R-tree).

### Dynamics

- R-all solves in 17.5 generations on average vs 30.4 for R-tree and 34.0 for R-order; R-gate 7.5. R-all jobs draw a library donor ~1 036 times per job and insert ~682; R-order draws ~2 038 and inserts ~1 108, so the transported libraries are used at least as heavily but do not help.
- Solver sizes are similar across arms (mean 17.8 – 18.4 nodes; R-gate 15.4). No evidence of a different kind of solution; R-gate just gets there faster.

Plots: `protected_per_cell_and_build.png` (left: per-cell arm means; right: per-build ratio vs helpers kept), `protected_evaluations_cdf.png` (evaluation distributions per arm), and the runner's `dynamics.png` in the protected output folder (solve curves, training score, output diversity, library size per build).

## 3. What the data shows

1. **The primary comparison is resolved in favour of a material saving.** R-all costs 0.58 of R-tree on 18 never-searched signed-gate cells, with a two-way 95% interval [0.47, 0.72] whose upper bound is below the 0.80 threshold. The saving is consistent across cells (18/18 below 1) and across most builds (22/24), so it is not driven by a few cells or a few lucky acquisitions. The worker-seconds ratio is slightly lower (0.54) because library insertions also shorten per-generation time.
2. **New acquisition adds beyond the owned order libraries.** R-all / R-order = 0.52 [0.44, 0.61]. By the report's own wording: "incremental search advantage resolved".
3. **The transported order libraries do not save anything on this family and may mildly hurt.** R-order / R-tree = 1.12 with the two-way interval [0.94, 1.34]; a 20% saving is excluded, harm is not resolved under the pre-stated unit (both one-way intervals exclude 1, 11/18 cells above 1, first-attempt rate 97.2% vs 97.7%). This is the proposal's "any library harm" surprise, in a weak form.
4. **The supplied gate prior remains far ahead of acquisition.** R-gate / R-tree = 0.25 [0.21, 0.30], R-all / R-gate = 2.34 [1.99, 2.76]. The frozen extractor recovers on average 8.6 of the 24 helpers; even the best build (14 helpers) does not approach R-gate.
5. **No reliability loss observed.** 1 728/1 728 solves in every arm; first-attempt solving 99.2% (R-all) vs 97.7% (R-tree) vs 97.2% (R-order). Zero capped jobs anywhere.
6. **Economics.** At A ≈ 216 k evaluations and a saving of ≈ 3.3 k per search, repayment vs no library takes about 66 searches [46, 110]; vs the already-owned order libraries about 51 [40, 69].

## 4. What the data does not show

- **Not a transfer claim about content families in general.** All 18 protected cells are input rebindings of one construction `p(a,b)+n(c,d)` in D625; the cell bootstrap measures sensitivity to which rebindings were drawn, not variation across independent families. The scope string in the report says the same.
- **Not helper causality.** The coverage gradient (0.31 / 0.47 / 0.77 for 2 / 1 / 0 needed helpers present) is descriptive and confounded with build quality and library size. The 0.77 saving with no needed helper present means a substantial part of the saving comes from other content (likely the other-index `p`/`n` forms, which a point mutation can rebind, or the 3-node ADD entries). An ablation would be needed to attribute.
- **Not the hard tier.** Destinations solve in a median of 3 584 evaluations (R-tree) and at most 3 restarts; the result covers easy compositions, as the proposal said. Whether the saving holds where R-tree fails often is untested.
- **Not resolved harm from transported libraries.** The point estimate is 12% worse than R-tree, but the pre-stated two-way interval includes 1. Treat as "no saving from transported order content on this family; mild harm plausible".
- **Not a general extractor-quality statement.** The extractor keeps a third of the helpers it could; whether a different admission rule would close the gap to R-gate is an open question, and the proposal explicitly made no claim about it.
- **Between-build variation is real.** Two builds (5, 20) had R-all dearer than R-tree; a single acquisition is not guaranteed to pay off. The pooled interval covers the average over builds, not a single deployment.

## Against the predictions

Read after the analysis above was written. The plan's decision rule and labels are the ones implemented in `classify` (`signed_gate_run.py:284`).

| Prediction (proposal / plan) | Observed | Verdict |
|---|---|---|
| Primary rule: upper 95% bound of R-all/R-tree < 0.80 → "extends this frozen acquisition recipe to this second signed conditional-value family" | 0.577 [0.47, 0.72] (report [0.468, 0.715]) | **Met.** Label `material_saving_recipe_extends_return_to_strategy`. |
| Expected R-all/R-tree 0.5 – 0.65 | 0.577 | Inside the expected range. |
| Plan precision scenario: log half-width factor ≈ 1.27 at C=18, so an effect of 0.60 gives an upper bound of about 0.76–0.78 | Observed factor ≈ 1.24 either side (0.577 → 0.715 and 0.468); upper 0.715 | Scenario was conservative and about right. No heavy capped tail appeared (0 capped jobs). |
| Expected R-gate/R-tree ≈ 0.3 | 0.246 [0.21, 0.30] | Slightly better than expected; the supplied prior is as strong as assumed. |
| Expected R-order/R-tree 0.65 – 0.9 (transported order libraries help somewhat) | 1.118 [0.94, 1.34] | **Missed.** The transported libraries did not save evaluations here; the point estimate is mild harm, not resolved under the two-way unit. |
| Expected R-all/R-order 0.75 – 0.9, "possibly unresolved" | 0.516 [0.44, 0.61] | Clearer than expected, because R-order was worse than forecast rather than R-all better. Plan's wording applies: "incremental search advantage resolved". |
| Surprise 1: R-all ≥ 0.8 (probe cells unrepresentative) | Did not occur; the six development cells gave 0.583, the protected 0.577. | Stage-0 cells were representative. |
| Surprise 2: R-order matching R-all (saving generic) | Did not occur; R-order is about twice R-all's cost. | The saving is specific to the newly acquired content, within this family. |
| Surprise 3: any library harm | Weakly, for R-order only: 11/18 cells above R-tree, both one-way intervals exclude 1, the pre-stated two-way interval does not. R-all and R-gate show no harm on any cell. | Partial. Worth a line in the question log; it does not change the decision. |
| Stage-0 anchors: source own-helper 37% / emittable 23%; R-all keeps 11/24 and 6/24 helpers | 37.1% / 21.8% on 2 304 source jobs; helpers kept 5–14, mean 8.6 | Replicated. |
| Repayment ≈ 80 searches (A ≈ 200 k, saving ≈ 2.5 k) | 66 [46, 110] vs R-tree; 51 [40, 69] vs owned R-order | Close; slightly better because the saving per search was 3.3 k. |
| Feasibility: ~0.10 worker-s per source job, ~12 min ordinary queue wall time, 110 min of timeouts | 0.107 worker-s per source job; 5.8 min total wall over three entries; no entry near its timeout | Comfortable. The plan's capped-tail reserve was never needed. |
| Question 50 condition (R-tree first-attempt ≈ 100%) reported, no gate | R-tree 97.7% first attempt (1 689/1 728); every arm ≥ 97.2% | Reported; condition holds. |

Nothing in the data contradicts the plan's scope statements. The one qualification I would add to the steward's write-up: the plan says "a primary saving with an unresolved transport contrast establishes useful acquisition on this family while leaving the reason to buy new content unresolved"; here the transport contrast is resolved, so the reason to buy new content for this family is also resolved, with the caveat that the owned order libraries turned out to be worthless on it rather than merely weaker. Whether a library acquired on the *order* family would have been equally worthless with a fairer baseline (R-order has 25–37 entries vs R-all's 29–44) is not something this design separates.
