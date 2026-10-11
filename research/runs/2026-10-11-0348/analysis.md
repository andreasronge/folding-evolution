---
outcome: transfers
---
# Analysis: frozen DG subtree libraries in restarted tree GP on a fresh gate-sum bank (0348)

Reviewer analysis of [proposal.md](proposal.md), [queue.yaml](queue.yaml) and
[execution.md](execution.md). Code: commit `1f02bb7` on
`research/2026-10-11-0348`. Every number below was recomputed from the raw
`search.jsonl`, `libraries.json` and `bank.json` in
`experiments/output/2026-10-11/2026-10-11-0348-gate-sum/` (and the
preparation folder next to it). The harness `result.json` / `report.md`
values agree exactly for means, solve counts and point ratios; my paired
block bootstrap (different RNG, 4,000 draws) reproduces the harness intervals
to within 0.005.

## 1. Data completeness

Both queue entries finished with exit 0: prepare 275 s of a 2,400 s timeout,
scoring 2,317 s of 5,400 s (the stage-0 gate projected 3,679 s; actual wall
was 63% of that).

**Bank (`x4-gate-sum-v1`, built before any protected search).**

- 144 candidate cells screened on D625 through 9 tokens (17,807 distinct
  output vectors at depth 9, `complete: true`); **0 exclusions**: no ≤ 9-token
  program computes any label, so all 144 were admissible. Split by ascending
  label hash: 4 development cells, 18 protected (6 per pair split), as the
  proposal specified.
- The two probe cells (`(X1+X3)>(X0+X2)?X0+X1:X3`, `(X0+X1)>(X2+X3)?X0+X3:X0`)
  are development cells 0 and 1; neither is protected.
- Canonical trees verified identical in interpreter, Python and Rust for all
  144 cells; `protected_searches: 0` before the freeze.

**Preparation (`2026-10-11-0348-prepare`).**

- Reconstruction: 24 libraries re-derived from the 768 saved 0150 acquisition
  rows (4 failed source jobs, included in charged acquisition); entries and
  size controls hash-equal to 0150's `libraries.json`. Library sizes 3–12,
  181 entries in total (131 of 3 nodes, 3 of 4, 23 of 5, 21 of 7, 3 of 9).
- Off-path replay of 8 saved 0024 jobs matched on all deterministic fields.
- Seed audit admitted: no overlap between stage, score, smoke, bootstrap,
  both probe namespaces and 211,014 historical seeds.
- Stage 0: 288 development jobs (24 builds × 4 cells × 3 arms), all present;
  R-lib/R-tree there 16,309 / 80,920 = 0.20 (descriptive, development cells).

**Scoring (`2026-10-11-0348-gate-sum`).**

| Check | Result |
|---|---|
| Rows | 5,184 = 3 arms × 24 builds × 18 cells × 4 repeats; 0 duplicates, 0 missing |
| Seed pairing | the three arms share the identical 8-seed list for every (build, cell, repeat); all 13,824 attempt seeds distinct |
| Cap / cutoff / population | 524,288 / 65,536 / 256 on every row |
| Failures | 2 R-tree, 7 R-size, 0 R-lib jobs unsolved; each ran 8 attempts and is charged exactly 524,288 |
| Exactness | all 5,175 solver programs re-run by me on all 625 inputs against the bank labels: 5,175 exact, 0 wrong (a solve requires D625 exactness in the search loop, not just the 64 training cases) |
| Donor accounting | R-lib: 7,306,515 library draws + 7,305,210 ordinary = 14,611,725 mutations; 3,599,237 insertions + 3,707,278 oversize rejections = 7,306,515 draws; R-size likewise balances; `empty_fallbacks = 0` |
| Arm wiring | R-tree rows carry no library statistics; R-lib and R-size do; libraries used equal the frozen 0150 ones byte-for-byte |

Nothing is missing, duplicated or substituted.

## 2. Key numbers

Means over the 18 protected cells with equal weight, failures at 524,288.
Intervals are paired block bootstraps over the 24 acquisition builds. Solve
denominators are jobs.

| Arm | Solved / jobs | Mean evaluations | Median | Q25–Q75 | Mean worker s | Solved on attempt 1 |
|---|---|---|---|---|---|---|
| R-tree | 1,726/1,728 = 0.9988 | 69,442 | 41,216 | 7,680–94,720 | 6.42 | 923/1,728 = 0.53 |
| R-lib | 1,728/1,728 = 1.0000 | 17,346 | 3,840 | 2,304–9,984 | 1.50 | 1,478/1,728 = 0.86 |
| R-size | 1,721/1,728 = 0.9959 | 59,692 | 16,896 | 4,864–74,752 | 5.40 | 1,034/1,728 = 0.60 |

| Contrast | Evaluation ratio [95%] | Worker-second ratio [95%] | Solve difference [95%] |
|---|---|---|---|
| **R-lib / R-tree (primary)** | **0.250 [0.217, 0.289]** | 0.234 [0.201, 0.273] | +0.0012 [0.000, +0.0029] |
| **R-lib / R-size (secondary)** | **0.291 [0.231, 0.372]** | 0.278 [0.219, 0.359] | +0.0041 [+0.0006, +0.0087] |
| R-size / R-tree (descriptive) | 0.860 [0.716, 1.011] | – | −0.0029 |

Decision-rule inputs: R-lib/R-tree upper bound 0.289 < 0.90; reliability
guard lower bound 0.000 > −0.03; R-lib/R-size upper bound 0.372 < 1. The
harness label is `search_cost_transfers_return_to_strategy` and
`resolved_increment_over_size_control`.

**By pair split** (6 cells each, 576 jobs per arm; interval over builds):

| Split | R-lib / R-tree | R-lib / R-size | Solves R-tree / R-lib / R-size |
|---|---|---|---|
| A: {X0+X1 \| X2+X3} — the learned predicate's split | **0.055 [0.042, 0.071]** | 0.060 [0.041, 0.090] | 576 / 576 / 570 |
| B: {X0+X2 \| X1+X3} | 0.363 [0.299, 0.434] | 0.420 [0.320, 0.552] | 575 / 576 / 576 |
| C: {X0+X3 \| X1+X2} | 0.338 [0.287, 0.400] | 0.420 [0.326, 0.553] | 575 / 576 / 575 |

Every split's upper bound is below 0.90, and every one of the 18 cells has
R-lib below R-tree (per-cell ratios 0.038–0.086 in split A, 0.27–0.46 in B
and C; [analysis_splits.png](analysis_splits.png), right).

**By build.** R-lib is below R-tree in 24/24 builds; per-build pooled ratios
range 0.14–0.54 ([analysis_splits.png](analysis_splits.png), left). 21/24
libraries contain at least one 7-node `GT(ADD(.,.),ADD(.,.))` entry (all of
them compare X2+X3 against X0+X1, so the harness's split-A flag is right).
The three without (builds 0, 7, 17) have pooled ratios 0.54, 0.45, 0.32
versus a mean of 0.23 for the other 21; their split-A ratios are 0.12, 0.11,
0.17 versus 0.044. Three builds is descriptive only.

**Reuse in final solvers** (literal contiguous-subtree match of library
entries in each job's solver tree; denominators are solved jobs per split):

| Arm, split | contains its library's `GT(ADD,ADD)` verbatim | contains any ≥ 5-node entry verbatim | contains any `GT(ADD,ADD)` subtree |
|---|---|---|---|
| R-lib A | 309/576 | 351/576 | 332/576 |
| R-lib B | 29/576 | 13/576 | 167/576 |
| R-lib C | 36/576 | 7/576 | 173/576 |
| R-tree A / B / C | – | – | 157 / 166 / 169 of 575–576 |
| R-size A / B / C | – | 10 / 15 / 30 (control entries) | 159 / 175 / 180 |

Verbatim reuse of large entries is concentrated in split A; in B and C the
≥ 5-node entries almost never survive into the solver, and the share of
solvers containing some `GT(ADD,ADD)` is the same as R-tree's.

**Shortcut diagnostics.** Training-perfect-but-not-exact individuals took
5.1% / 3.5% / 5.4% of evaluations (R-tree / R-lib / R-size); 99.97% of all
training-perfect individuals were not D625-exact, so the 64-case training set
is far from sufficient and the D625 exactness check is doing real work. The
solve criterion is unaffected (see completeness table).

**Economics** (original 0150 acquisition per build, including the 4 failed
source jobs, extraction and validation; 24-build joint bootstrap):

| Quantity | Evaluations | Worker seconds |
|---|---|---|
| Acquisition per library | 2.877 M [2.600 M, 3.163 M] | 285.7 [257.5, 314.6] |
| Saving per search, R-lib vs R-tree | 52,096 [47,102, 56,933] | 4.92 [4.44, 5.39] |
| Break-even searches per library | **55.2 [49.4, 61.9]** | 58.0 [51.8, 65.3] |
| Break-even, R-size vs R-tree | 295 [149, unbounded] | 279 [150, 6,277] |

Acquisition-plus-search totals: at 50 searches R-lib 3.74 M vs R-tree
3.47 M; at 100 searches 4.61 M vs 6.94 M; at 1,000 searches about 20 M vs
69 M ([economics.png](../../../experiments/output/2026-10-11/2026-10-11-0348-gate-sum/economics.png)).
Per-build break-even ranges 34–115 searches.

**Dynamics.** Solve fraction by expenditure
([dynamics.png](../../../experiments/output/2026-10-11/2026-10-11-0348-gate-sum/dynamics.png)):
by 16,384 evaluations R-lib had solved about 0.79 of jobs, R-size 0.49,
R-tree 0.39; all arms converge near 1.0 at the cap. R-lib keeps higher
training output diversity throughout (≈ 131–135 vs ≈ 117–124 distinct output
vectors). The worker-second ratio (0.234) tracks the evaluation ratio
(0.250), so library insertion carries no hidden per-evaluation cost.

**Development-bank comparison (descriptive only, different bank).** 0150's
primary on the 8 DG cells was 0.390 [0.332, 0.463]; the same 24 libraries on
the 18 protected gate-sum cells give 0.250 [0.217, 0.289]. The R-size control
was 0.944 [0.790, 1.120] vs R-tree there and 0.860 [0.716, 1.011] here.

## 3. What the data shows

1. **The frozen, externally acquired libraries transfer as a search-cost
   saving to this fresh shape.** On 18 protected cells never searched before
   the freeze, R-lib needs a quarter of R-tree's capped evaluations (upper
   bound 0.29) with no reliability loss (R-lib solved every job), and the
   saving holds in every one of the 18 cells and all 24 builds. The primary
   decision rule's "transfers" branch is met with wide margin.
2. **The gain is content, not just token supply.** R-lib beats the size- and
   compiled-length-matched random donors by about 3.4× (upper bound 0.37).
3. **The gain is strongly split-dependent.** Where the target's predicate is
   the one the libraries learned on DG (split A), the saving is about 18× and
   most R-lib solvers contain that library predicate verbatim. On the two
   splits with no matching predicate, the saving is about 3× and large
   entries are almost never reused verbatim. All three splits do gain, so the
   proposal's "surprise" condition (no gain on the unlearned splits) did not
   occur.
4. **Repayment is finite and measured.** Charging the full 0150 acquisition,
   a library pays for itself after about 55 gate-sum searches [49, 62] in
   either evaluations or worker seconds.

## 4. What the data does not show

- **Which ingredient carries the B/C gain.** Pair-sum entries, the small
  3-node `GT` entries, and an ADD/input frequency shift in the donor pool are
  all compatible with a 3× saving without verbatim reuse of large entries;
  this run had no arm to separate them. R-lib beating R-size rules out size
  alone, not frequency.
- **Whether the size control itself helps.** R-size/R-tree is 0.86 with an
  interval reaching 1.01, and R-size had the most failures (7). This is
  unresolved here as it was in 0150, and it bears on how much of the R-lib
  gain is "any extra donors" rather than DG content.
- **Breadth of transfer.** The target shape was deliberately assembled from
  the libraries' own parts (three pair sums, one of the three predicates
  learned). This is a within-family composition test. Nothing here speaks
  to shapes with unfamiliar content, other alphabets, or modularity.
- **Predicate dependence beyond three builds.** The weaker ratios of the
  three libraries lacking a 7-node predicate are suggestive, not a finding.
- **Deployment horizon.** The 55-search break-even is relative to this bank's
  R-tree cost (69k per job). On easier targets the saving per search would be
  smaller and the break-even longer; on harder ones the reverse.
- Two cells were probed before the freeze. They are development cells and
  never scored, but the family was chosen with that look in hand (disclosed
  in the proposal).

## Against the predictions

Read after the analysis above was written. [plan.md](plan.md) sets the
precedence: harm (lower > 1) first; else **Transfers** if upper < 0.90 and the
reliability guard passes, even when lower > 0.85; else Small or none if
lower > 0.85; a speed interval with a failed or unresolved guard is
reliability-unresolved; all other broad intervals unresolved.

| Plan item | Prediction / rule | Observed | Verdict |
|---|---|---|---|
| Primary R-lib/R-tree | Transfers if upper < 0.90 with guard | 0.250 [0.217, 0.289]; guard lower bound 0.000 > −0.03 | **Transfers** |
| Harm | lower > 1 | lower 0.217 | not harm |
| Reliability guard | solve-fraction difference lower bound > −0.03 | +0.0012 [0.000, +0.0029]; R-lib 1,728/1,728 | passes |
| Secondary R-lib/R-size | content beyond size if upper < 1 | 0.291 [0.231, 0.372] | content beyond this size control |
| Proposal expectation | ratio 0.15–0.35, every split gaining | pooled 0.250; A 0.055, B 0.363, C 0.338, every split upper < 0.90 | as expected (B's point is just above 0.35) |
| Proposal surprise 1 | ratio above 0.6 | 0.250 | did not occur |
| Proposal surprise 2 | no gain on the two splits without a learned predicate | B 0.363 [0.299, 0.434], C 0.338 [0.287, 0.400] | did not occur |
| Proposal surprise 3 | R-size close to R-lib (token supply) | R-lib/R-size 0.291, upper 0.372 | did not occur |
| Proposal expectation | R-size ≈ R-tree as on DG | 0.860 [0.716, 1.011] | unresolved; possibly a small gain of its own |
| Plan interpretation | gains across all splits → reuse across composition of familiar parts; concentration in split A → limited reuse | all three splits gain, but A's gain (≈18×) is about six times B's and C's (≈3×); verbatim reuse of large entries only in A | both readings apply: reuse across composition holds, and most of the pooled saving is predicate-specific |
| Feasibility gate | projected scoring ≤ 5,400 s | projected 3,679 s, actual 2,317 s | held |
| Grid | exactly 5,184 jobs, shared seeds | 5,184, 0 duplicates, seeds paired | held |

The plan's label is **transfers**, in the plan's own sense of a search-cost
classification on protected cells of a deliberately familiar-parts shape, with
acquisition reported separately (break-even about 55 searches per library
[49, 62]). The plan asked that a split-A-concentrated gain be read as
"limited reuse"; the data give both a uniform floor of about 3× on the
unlearned splits and a much larger predicate-matched gain, so the pooled
0.25 should not be quoted without the per-split numbers. What this run does
not settle, and the plan flagged in advance, is the carrying ingredient on
splits B and C and whether the size control itself helps.
