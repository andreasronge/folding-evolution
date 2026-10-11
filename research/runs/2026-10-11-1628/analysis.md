---
outcome: material_loss
---
# Analysis — 2026-10-11-1628 helper-entry arrangement intervention on R-all order libraries

Reviewer: independent of the researcher. Code at commit `46e05cb`; outputs in
`experiments/output/2026-10-11/2026-10-11-1628-prepare/` and `…/2026-10-11-1628-score/`. Every number below was
recomputed from `score.jsonl` with my own code and an independent bootstrap seed; where the report's number is quoted,
mine agrees to the stated precision.

Question: does R-all's order-task saving survive when only the twelve min/max helper entries lose their learned
arrangement (labels permuted within each entry, material, shape, slots and draw probabilities fixed)? Primary
contrast Q = capped mean evaluations R-hx / R-all on the six development cells; whole-build bootstrap.

## 1. Data completeness

| Item | Planned | Found |
|---|---|---|
| Prepare entry | construction + 72 smoke jobs | done, exit 0, 37 s wall; `preparation.json` admitted; smoke 72/72 rows, hash recorded |
| Score entry | 24 builds × 6 cells × 8 repeats × 3 arms = 3,456 | 3,456 rows, 3,456 unique (build, cell, repeat, arm) keys, 0 duplicates, 0 missing; `complete = true` |
| Seed pairing | identical 8-seed schedule across arms per unit | 1,152/1,152 units identical across the three arms; initial-population hash and training indices also validated by the runner |
| Realization | repeat mod 4 | every arm/repeat carries realization = repeat mod 4 (144 rows each); R-all and R-tree ignore it |
| Cap accounting | 8 × 65,536 = 524,288 | every row has cap 524,288, cutoff 65,536; every unsolved row charged exactly 524,288 |
| Constructions | 4 per build, 177 helper entries replaced | 96 constructions, 96 distinct hashes, 708 replaced slots (= 177 × 4), max 16 draws of 256 allowed, 635 unique subtrees validated interpreter = VM, all invariants admitted |
| Replacement content | audit predicted mostly single-input ("projection") outputs | 613/708 replaced slots are projection-valued (87%), as the planning audit predicted |
| Runtime | 22–28 min expected | 25.4 min batch (1,537 s wall), 10 workers, cpu efficiency 9.8; worker-s/job R-tree 5.78, R-all 2.24, R-hx 5.17 |
| Failures | none allowed | stderr empty; no construction, validation or job failure |

Provenance: `source_preparation_hash` equals the 1530 preparation hash; artifact hashes match between prepare and
score folders. Nothing is missing or duplicated; the primary estimate is computable from the full planned grid.

## 2. Key numbers

### 2.1 Arms (1,152 jobs each, paired seeds, 8 attempts × 65,536)

| Arm | Solved | Capped mean | Median | Geometric mean | Solved within first attempt (≤ 65,536) | Worker-s/job |
|---|---|---|---|---|---|---|
| R-tree (no library) | 1,146/1,152 | 77.9 k | 40.8 k | 36.0 k | 629/1,152 | 5.78 |
| R-all (24 saved libraries) | 1,151/1,152 | 30.0 k | 4.6 k | 8.3 k | 865/1,152 | 2.24 |
| R-hx (helper entries permuted) | 1,147/1,152 | 70.5 k | 39.3 k | 27.6 k | 604/1,152 | 5.17 |

### 2.2 Contrasts (ratio of pooled capped means; 95% bootstrap over the 24 builds, 8,192 draws)

| Comparison | Point | 95% interval | Paired units where numerator costlier (of 1,152) |
|---|---|---|---|
| **Q = R-hx / R-all (primary)** | **2.35** | **[2.07, 2.66]** | 886 (7 ties) |
| R-hx / R-tree | 0.90 | [0.83, 0.98] | 483 costlier, 665 cheaper (4 ties) |
| R-all / R-tree | 0.38 | [0.34, 0.43] | — |

The report's interval for Q is [2.07, 2.66]; my independent bootstrap gives [2.08, 2.66]. The lower bound sits well
above the pre-registered 1.25 threshold, and the whole interval lies above 2.

**Per build** (48 jobs per arm per build; `per_build_and_strata.png`, left): Q > 1 in 24/24 builds, Q > 1.25 in
23/24 (the exception is build 0 at 1.22); range 1.22–4.23, median 2.63. The effect is not carried by a few builds.
R-hx / R-tree per build ranges 0.58–1.26, with 17/24 below 1.

**Per cell** (192 jobs per arm per cell): Q between 1.61 (lo23+hi02) and 3.03 (lo01+hi23); R-hx / R-tree between
0.84 and 1.05. **Per realization** (288 jobs per arm): Q 2.57, 2.26, 2.20, 2.43 for realizations 0–3. No realization
or cell reverses the direction.

### 2.3 Replication of the R-all saving

R-all / R-tree here is 0.38 [0.34, 0.43] under a fresh search-seed namespace, against 0.40 [0.32, 0.50] on the same
cells in 1228 and 0.37 [0.33, 0.42] on the held-out cells in 1530. Solve counts are also in line (1228: R-all 576/576,
R-tree 574/576). The baseline the intervention is measured against is itself reproduced.

### 2.4 Saved coverage strata (descriptive; stratum = needed helpers present in the R-all library for that build × cell)

| Stratum | Paired units | R-tree | R-all | R-hx | Q | R-hx / R-tree | R-all / R-tree |
|---|---|---|---|---|---|---|---|
| 0 needed helpers | 144 | 71.1 k | 55.2 k | 70.7 k | 1.28 [0.98, 1.72] | 0.99 [0.77, 1.36] | 0.78 [0.55, 1.12] |
| 1 | 584 | 81.3 k | 33.3 k | 70.0 k | 2.10 [1.76, 2.50] | 0.86 [0.74, 0.99] | 0.41 [0.34, 0.48] |
| 2 | 424 | 75.6 k | 16.8 k | 71.0 k | 4.22 [3.50, 5.36] | 0.94 [0.82, 1.08] | 0.22 [0.18, 0.28] |

Intervals are whole-build bootstraps over the subset. The R-all gradient (0.78 → 0.41 → 0.22) replicates 1228's
(0.77 → 0.45 → 0.23). R-hx sits at 0.86–0.99 of R-tree in all three strata: once the helper entries are permuted,
coverage no longer predicts cost. Stratum 0 is small (144 units, 3–6 builds contribute most of it) and its
interval for Q includes 1, so whether R-all's modest saving in the no-helper stratum is also lost is not settled
by this run.

### 2.5 Rediscovery census (and its baseline)

The report says 1,147/1,147 R-hx solvers contain a helper-valued subtree on D625. The code review asked for the same
census in the other arms before reading this as rediscovery. Computed from `solver_tree` with the same `Semantics`
class:

| Arm | Solvers | Any helper-valued subtree | Both cell-needed helpers as subtrees | Solver nodes (median) |
|---|---|---|---|---|
| R-tree | 1,146 | 1,146 (100%) | 899 | 19 |
| R-all | 1,151 | 1,151 (100%) | 977 | 17 |
| R-hx | 1,147 | 1,147 (100%) | 826 | 19 |

Every solver in every arm contains at least one helper-valued subtree, because the targets are themselves built from
those helpers. The "rediscovery fraction" of 1.0 is therefore a tautology and carries no information about whether
R-hx search reconstructed what the library lost. The "both needed" counts differ (R-all highest), which is
consistent with R-all solvers more often using the two supplied entries directly, but this is a descriptive
observation with no pre-registered reading.

### 2.6 Operator usage (per 1,000 evaluations, summed over attempts)

| Arm | Library draws | Library insertions | Rejected library | Rejected mutation |
|---|---|---|---|---|
| R-all | 245 | 111 | 134 | 223 |
| R-hx | 246 | 108 | 139 | 230 |

R-hx draws from and inserts from its library at the same rate as R-all. The permuted entries are not being
filtered out by rejection; they are inserted as often and simply do not help. This rules out "R-hx lost its saving
because the inert entries were rejected and the arm effectively ran without a library".

### 2.7 Dynamics (`dynamics.png` in the score folder)

The D625 solve CDF of R-hx tracks R-tree closely from 4 k evaluations onward, a little above it below 65 k, and
both are far below R-all at every budget. Training-best and training-output-diversity curves of R-hx also lie near
R-tree, not near R-all. Evaluated tree nodes and compiled-length distributions are essentially identical across arms,
so the cost difference is not a program-size artefact.

## 3. What the data shows

1. **Permuting only the helper entries removes most of R-all's saving.** R-all costs 0.38 of R-tree; R-hx costs 0.90
   of R-tree, 2.35× R-all, with the whole interval above 2 and the direction consistent in 24/24 builds, 6/6 cells
   and 4/4 realizations. By the pre-registered rule (lower bound of Q above 1.25) this is a material loss.
2. **What is left after permutation is small.** R-hx / R-tree is 0.90 [0.83, 0.98]: the upper bound is below 1 but
   above the 0.80 retention threshold. The non-helper content (order primitives and other 2-cell entries, byte-identical
   between arms) carries at most a tenth or so of the cost, against R-all's roughly 60% saving.
3. **The coverage gradient is a helper-entry effect.** With helper entries permuted, the three coverage strata collapse
   to 0.86–0.99 of R-tree. The intact R-all gradient replicates (0.78 / 0.41 / 0.22).
4. **The R-all baseline replicates** under a fresh seed namespace (0.38 vs 0.40 and 0.37 before).

## 4. What the data does not show

- **Not that min/max computations specifically are needed.** 613/708 replacements are projection-valued (output
  equals one input). The contrast is "learned helper arrangement" versus "same material rearranged into a mostly
  trivial expression". A different nontrivial same-material replacement was not tested and, as the proposal notes,
  mostly cannot exist for six-node entries. The loss shows the learned helper computations beat inert same-material
  entries; it does not rank them against other useful computations.
- **Not a per-helper or per-entry attribution.** All 4–10 helper entries per build were permuted together. Which of the
  twelve helpers, or how many of a build's entries, carry the saving is not identified.
- **Not whether R-all's stratum-0 saving is helper-borne.** Q in stratum 0 is 1.28 [0.98, 1.72] on 144 units; the
  point estimate matches "lost" but the interval includes 1.
- **Not that R-hx retains anything useful.** R-hx / R-tree's upper bound (0.98) is below 1 but the pre-registered
  retention bar was 0.80; the residual saving is small and is not the kind of retention the plan defined.
- **Not rediscovery.** The census is uninformative (§2.5).
- **Not a transfer claim.** Development cells of a development bank only (bank `x4-order-v1`, protected cells untouched).
- The result is conditional on this library (24 saved R-all builds), this donor law (half of mutation donors from
  the library, uniform slots, duplicates kept) and this search regime (restarted tree GP, 8 × 65,536).

Shortcut check: arms share initialization and seeds; R-tree is unchanged from 1228/1530 and reproduces its cost; the
only thing that differs between R-all and R-hx is the content of the 4–10 helper slots per build. I found no
alternative explanation for a 2.35× cost difference in the operator counts, solver sizes or dynamics.

## Against the predictions

plan.md was read only after the sections above were written.

| Plan item | Predicted / required | Observed |
|---|---|---|
| Grid | 3,456 jobs, 1,152 per arm, all required | 3,456/3,456, no duplicates, no failures |
| Construction | 177 helper entries replaced per realization, ≤ 256 draws, no helper-valued subtree, invariants preserved | 708/708 slots replaced, max 16 draws, 96 distinct constructions, all invariants admitted; 613/708 projection-valued as the smoke found |
| Seeds | paired across arms; separate construction/search/bootstrap namespaces | 1,152/1,152 units paired; seed audit admitted |
| Runtime | 22–30 min | 25.4 min |
| Primary rule, loss | lower(Q) > 1.25 | Q = 2.35 [2.07, 2.66]: **material loss** |
| Retention rule | upper(Q) < 1.25 and upper(R-hx/R-tree) < 0.80 | not met on either condition (upper Q 2.66; upper R-hx/R-tree 0.98) |
| Precision caveat | do not expect an upper bound near 1.15–1.20 | the interval is ±12% around the point in log, which would have put a true ratio of 1.0 at about [0.88, 1.13]; irrelevant here since the point is 2.35 |
| Rediscovery census | report share of R-hx solvers containing a helper-valued subtree | 1,147/1,147, but 100% in R-tree and R-all too (§2.5): uninformative as designed |
| Coverage strata | descriptive only, no inference | reported with intervals for scale only; the R-all gradient replicates and R-hx is flat across strata |

**Outcome label: material loss**, exactly as the plan defines it: intact helper-valued entries benefit search
relative to this mostly projection-valued, same-material replacement, conditional on the remaining R-all content and
this search regime. The proposal expected Q ≈ 1.5–2 and R-hx near the no-helper stratum (≈ 0.75 of R-tree); the
observed Q of 2.35 is larger than expected and R-hx (0.90 of R-tree) retains even less than the no-helper stratum
did in R-all. The "surprise" branch (Q near 1, pointing at primitive supply and other 2-cell content) did not occur.

The plan's interpretive limits stand: this does not show unique min/max necessity or superiority over other
nontrivial computations, it attributes nothing to individual helpers or entries, and no fresh-bank claim follows.
The plan's caution that projection-valued entries "may supply useful subtrees through variation" is consistent with
the data in the sense that R-hx still sits a little below R-tree (0.90 [0.83, 0.98]); the operator counts (§2.6)
show the replacements are inserted as often as the originals, so whatever they supply is worth at most about a tenth
of R-tree's cost.

Pricing a resolving design is not needed: the registered decision is reached. If the steward wants per-helper
attribution, the cheapest next step is to permute a subset of helper entries per build rather than all of them, at
the same 1,152-per-arm size, since the per-build Q spread (1.22–4.23) already suggests the effect scales with how
many of a cell's needed helpers the build's library supplies (stratum Q 1.28 / 2.10 / 4.22).
