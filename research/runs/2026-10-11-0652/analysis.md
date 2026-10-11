---
outcome: worthwhile_replacement_loss
---
# Analysis: uniform compatible labels on learned donor shapes (0652)

Reviewer analysis of [proposal.md](proposal.md), [queue.yaml](queue.yaml) and [execution.md](execution.md),
written before reading plan.md. Code at commit `163f005`. Raw data:
`experiments/output/2026-10-11/2026-10-11-0652-prepare` and `.../2026-10-11-0652-score`. All numbers below
were recomputed from `search.jsonl` and checked against `result.json` and `report.md`; where I ran my own
bootstrap it is noted.

## 1. Data completeness

| Check | Result |
|---|---|
| Queue | both entries `done`, runner exit 0; prepare 147 s wall, score 3,674 s wall (61 min, under the 120 min timeout and the 100 min projection) |
| Stage gate (prepare) | admitted **all five arms, 6 repeats, 3 realizations**; projection 5,523 s against the 6,000 s limit (no fallback used); 288/288 development R-unif calibration jobs ran, 285 solved, 3 capped |
| Validation (prepare) | replay of 6 saved 0524 R-perm jobs: all deterministic fields identical; interpreter/compiler check 144 cells passed; construction audit 72/72 uniform constructions and 72/72 permutations passed invariants and D625 agreement (543 entries each); 24 frozen 0524 hashes re-checked |
| Rows | **8,640 / 8,640** jobs in `search.jsonl`; 1,728 per arm; 24 builds × 12 cells × 6 repeats; no duplicate (arm, build, cell, repeat) keys |
| Seed pairing | every (build, cell, repeat) job has the same 8 attempt seeds in all 5 arms (0 mismatches over 1,728 jobs); 13,824 distinct seeds, each used once per arm; 0 overlap between the 288 stage-0 jobs and scoring seeds; realization = repeat mod 3 holds for all rows |
| Cells | 12 B/C cells (6 B, 6 C), as approved; the 4 stage-0 development cells are not among them |
| Failures | 11 unsolved jobs, all charged the full cap of 524,288 after 8 attempts: R-tree 4, R-unif 3, R-size 3, R-perm 1, R-lib 0; no errors, `stderr.log` empty |
| Arm wiring | `envelope()` gives R-tree no donors, R-lib the intact entries, R-size the single 0150 control set per build, R-perm `constructions[realization]`, R-unif `uniform_constructions[realization]`; all other search settings go through the unchanged R-tree envelope. R-tree rows carry no library statistics; library-draw fraction of mutations is 0.500 in all four donor arms |
| Estimand | repeats averaged within realization first, three realizations weighted equally, paired hierarchical bootstrap over builds then realizations (8,192 draws); my own 4,000-draw version reproduces every interval to ±0.02 |

Note on R-size: there is one control set per build, so its "realization" index is nominal (same donors in all
three). Its within-build spread across realization blocks (median max/min 1.49) is therefore a pure
search-noise floor; R-unif (2.12) and R-perm (2.41) spread more, so construction identity matters in both.

The data are complete and the design ran as approved. Nothing in the harness was changed from the 0524 search,
construction or Rust code (method hashes re-checked at run time).

## 2. Key numbers

Mean capped evaluations per B/C job (1,728 jobs per arm):

| Arm | Mean | Median | p90 | First-attempt solves | Jobs > 65,536 | Capped at 524,288 | Solved | Worker s / job |
|---|---|---|---|---|---|---|---|---|
| R-tree | 69,637 | 43,904 | 185,498 | 910 / 1,728 (53%) | 47.3% | 4 | 1,724 / 1,728 | 6.48 |
| R-lib (intact) | 26,987 | 5,888 | 72,960 | 1,339 / 1,728 (77%) | 22.5% | 0 | 1,728 / 1,728 | 2.37 |
| R-perm | 25,421 | 4,864 | 72,269 | 1,387 / 1,728 (80%) | 19.7% | 1 | 1,727 / 1,728 | 2.24 |
| **R-unif** | **52,601** | **12,928** | **137,549** | **1,074 / 1,728 (62%)** | **37.8%** | **3** | **1,725 / 1,728** | **4.77** |
| R-size | 57,605 | 16,128 | 143,872 | 1,046 / 1,728 (61%) | 39.5% | 3 | 1,725 / 1,728 | 5.24 |

Registered contrasts on B/C (ratios of means, paired hierarchical bootstrap, 95% intervals):

| Contrast | Point | 95% interval | Rule | Verdict |
|---|---|---|---|---|
| **Primary: R-unif / R-perm** | **2.069** | **[1.679, 2.608]** | loss if lower > 1.10 and point ≥ 1.25; retention if upper < 1.25 | **worthwhile loss**; retention excluded by a wide margin |
| Intact: R-unif / R-lib | 1.949 | [1.636, 2.315] | retention needs upper < 1.25 | not retained |
| Baseline: R-unif / R-tree | 0.755 | [0.645, 0.884] | retention needs upper < 0.80 | upper 0.884: R-unif is resolvably cheaper than R-tree, but not by the registered margin |
| Validity guard: R-perm / R-tree | 0.365 | [0.295, 0.441] | upper < 0.60 | passes |
| Validity guard: R-lib / R-tree | 0.388 | [0.328, 0.456] | upper < 0.60 | passes |
| Reliability: solve fraction R-unif − R-perm | −0.0012 | [−0.0046, +0.0017] | lower > −0.03 | passes (finite-sample; 1,725 vs 1,727 solves) |
| Descriptive: R-size / R-unif | 1.095 | [0.864, 1.367] | none | unresolved; both sides of 1 |
| Descriptive: R-size / R-tree | 0.827 | [0.671, 1.017] | none | unresolved, as in 0348 (0.860 [0.716, 1.011]) |
| Descriptive: R-lib / R-perm | 1.062 | [0.875, 1.294] | none | replicates 47's R-perm/R-lib 1.031 [0.854, 1.225] inverted |

The harness label is `worthwhile_uniform_replacement_loss_return_to_strategy`. The decision does not depend on
the inference method: the raw per-arm means give 52,601 / 25,421 = 2.07 directly, and the per-build ratio
R-unif/R-perm is above 1 in **23 of 24 builds** (median 1.86, range 0.95 to 5.81; the one exception is build 22
at 0.95). At the construction level, 11 of 72 uniform constructions are cheaper than their build's mean R-perm
cost. ([analysis_cells_builds.png](analysis_cells_builds.png): per-cell intervals, per-build paired means,
solved fraction by budget.)

**By split and subgroup** (R-unif / R-perm): B 1.89 [1.47, 2.48] (864 jobs/arm); C 2.30 [1.77, 3.05];
the four cells whose then-branch pair was learned in the DG source 2.25 [1.71, 2.99]; the other eight 1.97
[1.53, 2.58]. All twelve cells have R-unif/R-perm above 1 with the lower bound above 1 (lowest lower bound
1.01 on B `(X1+X3)>(X0+X2)?(X0+X3):X3`). No split or subgroup differs resolvably from the pooled estimate.

**By realization** (24 builds each): R-unif/R-perm 1.70, 2.83, 1.93 for realizations 0, 1, 2. R-perm
realization 1 happens to be cheap (18,876 vs 27,403 and 29,984); R-unif's three realizations are 46,525,
53,458 and 57,821. Equal weighting was registered, and the loss holds in every realization.

**Replication of prior arms.** R-tree 69,637 (0524: 72,558; 0348: 69,442), R-lib 26,987 (0524: 25,343),
R-perm 25,421 (0524: 26,125), R-size 57,605 (0348: 59,692). Contemporaneous controls replicate the archived
ones within a few percent.

**Dynamics.** Fraction of 1,728 jobs solved within a budget: at 4,096 evaluations R-perm 0.45, R-lib 0.37,
R-unif 0.24, R-size 0.21, R-tree 0.12; at 65,536 (one attempt) 0.80, 0.78, 0.62, 0.61, 0.53; at 262,144 all
between 0.96 and 1.00. R-unif tracks R-size closely across the whole budget range and sits between the
learned-label arms and plain tree GP throughout.

**Economics** (acquisition charged to R-unif at the approved 2.88 M evaluations per library). Savings per
B/C search versus R-tree: R-unif 17,035 [7,787, 25,753] evaluations, against R-lib 42,650 and R-perm
44,216. Repayment horizon: R-unif 169 searches [112, 370], R-lib 67 [56, 83], R-perm 65 [54, 80].
R-unif's acquisition-inclusive curve stays above R-lib/R-perm at every horizon and crosses R-tree only after
about 170 searches.

**Scoring cost.** 36,480 worker-s (R-tree 11,197 · R-lib 4,091 · R-perm 3,879 · R-unif 8,251 · R-size
9,063), 3,656 s wall, sustained concurrency 9.98. The proposal priced 41,000 worker-s / 70 min; actual was
61 min.

## 3. What the uniform relabelling did to the libraries (content audit, descriptive)

Label totals over the 72 uniform constructions versus the intact libraries counted three times (token ids:
0–3 X0–X3, 4 ANY, 5–8 constants 0/1/2/5, 9 ADD, 10 GT, 11 IF_GT):

| Class | Intact (×3) | R-unif | Note |
|---|---|---|---|
| binary nodes ADD : GT | 636 : 120 (84% ADD) | 373 : 383 (49% ADD) | half the ADD nodes became GT |
| input slots X0–X3 : ANY | 1,038 : 57 (5% ANY) | 874 : 221 (20% ANY) | four times the ANY supply |
| constants 0 : 1 : 2 : 5 | 102 : 93 : 15 : 12 | 56 : 60 : 58 : 48 | flat |
| ternary IF_GT | 9 | 9 | unchanged by construction |

Distinct-input `ADD(Xi,Xj)` occurrences by split, per library (A / B / C): intact 4.2 / 0.0 / 0.2 (107 per
24-library set); R-perm 1.2 / 1.1 / 1.4 (88 per set); **R-unif 0.46 / 0.43 / 0.39 (31 per set)**. The
proposal's probe expected about 35 per set for a uniform law; the realized 31 is consistent with that.
Learned-orientation predicates `GT(ADD,ADD)` on split A: intact 63 across the three copies; R-perm 7/11/13 by
split; **R-unif 0 on every split**. Uniform relabelling removed the learned predicate entirely and cut the
general pair-sum supply to about a third of R-perm's.

Behavioural uniqueness: R-unif 508 distinct D625 behaviours among 543 entries (R-perm 522; intact entries
are deduplicated by construction). 536 of 543 R-unif entries differ from their intact original in prefix;
525 differ in behaviour.

**Did the search use the material?** Final solvers of solved jobs containing a donor entry verbatim as a
contiguous subtree (R-tree compared against the intact entries as a chance level, since 131 of 181 entries
are 3-node `ADD(Xi,Xj)`-type trees that tree GP produces on its own):

| Arm | Any entry verbatim | ≥ 5-node entry verbatim |
|---|---|---|
| R-tree (chance) | 403 / 1,724 (23%) | 0 / 1,724 |
| R-lib | 1,103 / 1,728 (64%) | 29 / 1,728 (2%) |
| R-perm | 1,356 / 1,727 (79%) | 173 / 1,727 (10%) |
| R-unif | 824 / 1,725 (48%) | 37 / 1,725 (2%) |
| R-size | 800 / 1,725 (46%) | 40 / 1,725 (2%) |

Library draws were inserted at the same rate in all donor arms (45–47% of draws accepted; the rest rejected
as oversize). The uniform material was drawn and inserted as often as the permuted material, but ended up in
solvers much less often (48% vs 79% for any entry; 2% vs 10% for large entries), at the same rates as the
size-matched random controls.

## 4. What the data show

1. **Uniform labels on the learned skeletons lose most of the acquired B/C gain.** R-unif costs 2.07×
   R-perm [1.68, 2.61] and 1.95× intact R-lib [1.64, 2.32] in mean capped evaluations on the twelve
   predicate-unmatched cells, with no reliability difference. The loss is in 23 of 24 builds and all 12
   cells, and is well past the registered 1.25 margin on either side.
2. **R-unif is still resolvably cheaper than plain restarted tree GP** (0.755 [0.645, 0.884]) but the
   registered 0.80 upper bound for "uniform suffices" is not met, and the saving is small: a 17 k-evaluation
   saving per search against a 2.88 M acquisition charge repays only after about 170 searches, versus about
   65 for the learned-label libraries.
3. **R-unif is indistinguishable from the size-matched random controls.** R-size/R-unif is 1.095 [0.864,
   1.367]; the two arms have the same medians, tails, first-attempt rates, budget curves and solver-use rates.
   With uniform labels the learned skeletons, widths, sizes and multiplicities bought nothing resolvable
   beyond what 0150's random size-matched trees already provide.
4. **The learned label law is where the shape-conditioned donor gain lives, at this resolution.** Given the
   same skeletons, count-preserving rearrangement (R-perm) keeps the full gain (replicated here: R-lib/R-perm
   1.06 [0.88, 1.29]); uniform relabelling discards about 85% of it (R-tree − R-unif = 17 k of the
   R-tree − R-perm = 44 k saving).

## 5. What the data do not show

- **Which part of the label law matters.** The uniform law changed four things at once: ADD share (84% → 49%),
  ANY share (5% → 20%), constant distribution, and the finite-library dependencies between labels. It also
  removed every learned-orientation predicate and cut distinct-input pair sums to a third. The design has no
  arm that varies one of these alone, so "pair-sum supply" remains the leading hypothesis, not a result. The
  R-perm arm, which has B/C pair sums at 1.1–1.4 per library and no more than 13 predicates per split, is
  enough to keep the gain, so whatever carries it survives count-preserving shuffling; that narrows the
  candidate to size-conditioned label frequencies or their joint distribution, not to specific B/C pairs
  (47) and not to skeletons (this run).
- **That skeletons carry nothing.** R-size/R-unif is unresolved (interval 0.86–1.37); the point estimate
  favours R-unif by 10%. A skeleton effect of up to about 30% under uniform labels is not excluded. It is
  excluded that skeletons alone carry the gain.
- **That a probabilistic learner needs the exact frequencies.** This is a replacement test of one uniform
  law against one empirical law; a learner that fits per-class label marginals (PIPE-like, without position)
  might sit anywhere between the two. The result says it must learn label supply at least to the level that
  rearrangement preserves; it does not price intermediate laws.
- **Transfer.** Development bank, one acquisition cohort, one extractor, B/C only. No fresh-bank claim.
- **Why R-unif beats R-tree at all.** Both R-unif and R-size are below R-tree (0.755 and 0.827, the latter's
  interval reaching 1.02). The shared ingredient is extra subtree supply of the learned size distribution;
  whether that is a size effect or a mutation-operator effect of library draws is not separable here, as it
  was not in 0348.

## 6. Observations for the log

- The 0524 R-perm result replicates contemporaneously (R-lib/R-perm 1.06 [0.88, 1.29]; point now on the
  other side of 1 from 47's 1.031), which supports reading 47's retention as real rather than a one-off.
- The R-unif construction-level spread (2.12 median max/min within build) is similar to R-perm's (2.41),
  so three realizations was the right choice; the primary interval (±22% relative half-width) was close to
  the proposal's ±18% estimate.
- Solver-use audit: inserted uniform material persists in solvers at the random-control rate, not the
  learned rate. A learner that reproduces the label law should restore the 10% large-entry survival as a
  cheap diagnostic before any scoring run.

## Against the predictions

Read [plan.md](plan.md) after the analysis above was written.

| Plan item | Registered rule | Observed | Verdict |
|---|---|---|---|
| Failed validity | R-lib/R-tree or R-perm/R-tree upper ≥ 0.60 | 0.456 and 0.441 | not triggered |
| **Worthwhile replacement loss** | primary lower > 1.10 and point ≥ 1.25 | R-unif/R-perm 2.069 [1.679, 2.608] | **matches**, lower bound 0.58 above the threshold |
| Uniform replacement sufficient | primary upper < 1.25, R-unif/R-tree upper < 0.80, solve-difference lower > −0.03 | 2.608, 0.884, −0.0046 | first two fail; only reliability passes |
| Intact benefit retained | additionally R-unif/R-lib upper < 1.25 | 2.315 | not reached |
| Otherwise unresolved | — | — | not reached; no precision price owed (harness reports zero additional acquisitions for every rule except the untriggered 0.80 baseline rule, which would have needed about 148 more acquisitions) |
| Admission | five arms/six repeats if ≤ 100 min projected; ordered fallbacks | projection 92 min, all five arms admitted, actual 61 min | ran as the primary design; the code review's worry that R-size might be dropped by a conservative concurrency estimate did not materialise (measured 9.70) |
| Weighting | realizations equal, repeats averaged within realization first, nested paired bootstrap | implemented and reproduced independently | as registered |
| Reporting | acquisition at 2.88 M, worker seconds, splits/solves, insertion rates, realization spread, R-size/R-unif descriptive | all present in result.json and section 2 above | complete |

Against the proposal's expectation (about 70%: a worthwhile loss with R-unif/R-perm about 1.6–2.5 and
R-unif near R-size): the point estimate 2.07 is inside the expected range, and R-size/R-unif is 1.095
[0.864, 1.367], so R-unif is "near R-size" in the sense of unresolved against it. The named surprise
(R-unif ≈ R-perm, skeletons carry the gain) did not occur.

The plan's conditions on the loss reading hold and should carry into the decision: this retains the empirical
construction pending strategy; it does not isolate label frequencies from finite-library dependencies, does not
show that these exact frequencies must be learned, and says nothing about transfer. The one addition from this
run beyond the registered rules is descriptive: uniform labels on the learned shapes perform like 0150's
random size-matched trees on every metric examined (cost, tails, budget curves, solver-use), which makes
"skeletons alone" the one explanation the data now exclude.

Outcome: **worthwhile replacement loss**.
