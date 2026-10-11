---
outcome: useful_search_content_increment_consider_fresh_bank
---
# Analysis: frozen source-subtree library as mutation donors in restarted tree GP (0150)

Reviewer analysis of [proposal.md](proposal.md), [queue.yaml](queue.yaml) and
[execution.md](execution.md). Code: commit `d7ec100` on
`research/2026-10-11-0150`. Every number below was recomputed from the raw
`search.jsonl` and `libraries.json` in
`experiments/output/2026-10-11/2026-10-11-0150-dg/`; the harness
`result.json`/`report.md` values agree exactly for means and solve fractions,
and my block bootstrap (different RNG, 4000 draws) reproduces the harness
intervals to within 0.01.

## 1. Data completeness

Both queue entries finished with exit 0: prepare 848 s of a 2,700 s timeout,
scoring 3,137 s of 9,000 s (3.25 h allocated, 66 min used).

**Preparation (`2026-10-11-0150-prepare`).**

- Off-path replay of the 8 saved 0024 R-tree jobs matched on all
  deterministic fields (`replay.json: passed`).
- Seed audit admitted: the published source / stage-source / score / stage /
  control / smoke seed sets are pairwise disjoint and disjoint from the
  historical snapshot and the reconstructed 0024/2254 schedules.
- Stage-0 gate passed with margin: projected scoring 5,957 s against a 9,000 s
  ceiling, projected preparation 1,386 s against 2,700 s. Actual scoring wall
  was 3,126 s at effective concurrency 9.97.
- Acquisition: 768 source jobs, all present; 764/768 solved (minimum 31/32
  per build). 24 libraries, sizes 3–12 (181 entries in total), no empty
  library, so no empty-library fallback was ever exercised
  (`empty_fallbacks = 0`). 181 size controls built from the recorded seeds,
  all within the depth-3 donor support (3–843 draws each). Scoring re-derived
  every library and every control from the saved rows and seeds before
  running.

**Scoring (`2026-10-11-0150-dg`).**

| Check | Result |
|---|---|
| Rows | 4,608 = 3 arms × 24 builds × 8 cells × 8 repeats, 0 duplicates, 0 missing |
| Seed pairing | the three arms share the identical 8-seed list for every (build, cell, repeat); all 1,536 × 8 R-tree attempt seeds distinct |
| Failures | 12 R-tree, 0 R-lib, 17 R-size jobs unsolved; each charged exactly 524,288 |
| Donor accounting | library draws + ordinary donors = mutations; insertions + oversize rejections = library draws (R-lib: 5,725,581 + 7,133,199 = 12,858,780) |
| Arm wiring | R-tree rows carry no library statistics; R-lib and R-size rows do; `envelope()` indexes `entries` vs `controls` by build |

Nothing is missing, duplicated or silently substituted. The R-tree arm
reproduces 0024: 87,352 mean evaluations here versus 90,392 there
(1,524/1,536 vs 765/768 solved); every per-cell mean here lies inside the
0024 per-cell interval.

## 2. Key numbers

Means over 8 cells with equal weight, failures at 524,288. Intervals are
paired block bootstraps over the 24 acquisition builds. Solve denominators
are jobs.

| Arm | Solved / jobs | Mean evaluations | Median | Geometric mean | Mean worker s | Mean attempts |
|---|---|---|---|---|---|---|
| R-tree | 1,524/1,536 = 0.992 | 87,352 | 68,480 | 33,878 | 8.83 | 2.14 |
| R-lib | 1,536/1,536 = 1.000 | 34,109 | 5,376 | 9,719 | 3.29 | 1.41 |
| R-size | 1,519/1,536 = 0.989 | 82,473 | 61,184 | 27,717 | 8.15 | 2.10 |

| Contrast | Evaluation ratio [95 %] | Worker-second ratio [95 %] | Solve difference [95 %] |
|---|---|---|---|
| **R-lib / R-tree (primary)** | **0.390 [0.332, 0.463]** | 0.373 [0.315, 0.443] | +0.008 [+0.004, +0.012] |
| **R-lib / R-size (control)** | **0.414 [0.332, 0.533]** | 0.404 [0.323, 0.522] | +0.011 [+0.005, +0.019] |
| R-size / R-tree (descriptive) | 0.944 [0.790, 1.120] | – | −0.003 |

Decision-rule inputs: R-lib/R-tree upper bound 0.463 < 0.90; R-lib/R-size
upper bound 0.533 < 1; solve-difference lower bound +0.004 > −0.03. The
harness label is `useful_search_content_increment_consider_fresh_bank`.
The size control is itself unresolved against R-tree (interval spans 1).

Robustness, all descriptive:

- R-lib's per-build mean is below R-tree's in 24/24 builds; leave-one-build-out
  ratio ranges 0.364–0.402. R-size is below R-tree in 14/24 builds, with
  per-build ratios from 0.42 to 2.10 ([analysis_builds_cells.png](analysis_builds_cells.png), left).
- Excluding failures (solved jobs only): 83,912 vs 34,109, ratio 0.41. The
  12 R-tree failures add about 4,100 to its mean; they are not what drives
  the ratio.
- Per repeat (seed slot), the R-lib/R-tree ratio ranges 0.32–0.46.
- Shortcut load is flat: training-perfect-but-not-exact individuals are
  10.0 % / 10.6 % / 10.1 % of evaluations in R-tree / R-lib / R-size, so the
  gain is not a change in the D625 generalisation gap.

### 2.1 Per cell

| Target cell | R-tree mean (solves) | R-lib mean (solves) | R-size mean (solves) | R-lib/R-tree [95 %] | R-lib/R-size [95 %] |
|---|---|---|---|---|---|
| (X0+X1)>(X2+X3)?X3:X2 † | 82,927 (192) | 9,723 (192) | 80,892 (190) | **0.117 [0.064, 0.193]** | 0.120 [0.066, 0.203] |
| (X0+X3)>(X1+X2)?X3:X0 | 83,645 (192) | 32,981 (192) | 82,211 (191) | 0.394 [0.306, 0.493] | 0.401 [0.291, 0.575] |
| (X1+X2)>(X0+X3)?X0:X2 | 103,815 (189) | 39,816 (192) | 93,016 (189) | 0.384 [0.293, 0.495] | 0.428 [0.329, 0.576] |
| (X1+X2)>(X0+X3)?X3:X1 | 103,327 (187) | 37,911 (192) | 77,161 (191) | 0.367 [0.257, 0.510] | 0.491 [0.334, 0.728] |
| (X1+X3)>(X0+X2)?X2:X0 | 74,543 (192) | 39,805 (192) | 76,001 (191) | 0.534 [0.387, 0.710] | 0.524 [0.362, 0.742] |
| (X1+X3)>(X0+X2)?X3:X1 | 89,463 (189) | 44,285 (192) | 89,705 (189) | 0.495 [0.374, 0.653] | 0.494 [0.355, 0.703] |
| (X1+X3)>(X0+X2)?X0:X2 | 72,071 (192) | 37,293 (192) | 74,812 (189) | 0.517 [0.402, 0.653] | 0.498 [0.376, 0.662] |
| (X0+X2)>(X1+X3)?X3:X2 | 89,027 (191) | 31,059 (192) | 85,983 (189) | 0.349 [0.271, 0.446] | 0.361 [0.270, 0.488] |

192 jobs per cell per arm. † This cell shares its full comparison predicate
with source cells `(X0+X1)>(X2+X3)?X3:X0`, `(X2+X3)>(X0+X1)?X0:X2` and
`(X2+X3)>(X0+X1)?X1:X0` (same pair split, different output branches).

The harness's covered/uncovered split (pair split present among source
predicates: 4 cells each) gives 0.322 [0.266, 0.388] covered versus
0.469 [0.387, 0.570] uncovered. That split is misleading here: the
"covered" figure is carried by the one † cell. The other three covered cells
(0.37–0.39) overlap the uncovered cells (0.35–0.53). With the † cell
excluded, the primary ratio is **0.427 [0.361, 0.504]** against R-tree and
**0.455 [0.365, 0.589]** against R-size, both still well below 0.90 and 1.

### 2.2 Where the saving comes from

| Solving attempt | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | all failed |
|---|---|---|---|---|---|---|---|---|---|
| R-tree | 715 | 394 | 185 | 112 | 64 | 20 | 24 | 22 | 12 |
| R-lib | 1,121 | 279 | 83 | 34 | 11 | 6 | 0 | 2 | 0 |
| R-size | 776 | 338 | 191 | 108 | 51 | 26 | 18 | 28 | 17 |

R-lib solves 1,121/1,536 jobs in the first 65,536-evaluation attempt against
715/1,536 for R-tree, and its first-attempt solves are earlier (median
5,376 evaluations for a whole job versus 68,480). The per-attempt success
rate rises from 0.47 to 0.73, which through the restart schedule is what
collapses the mean. The dynamics plot in the output folder shows the same
thing: R-lib's training best score and D625 solve curve lead at every
expenditure and its training output diversity stays higher.

### 2.3 What the libraries contain

Of the 181 learned entries: 56 pair sums `ADD(Xi,Xj)`, 20 full comparison
predicates `GT(ADD(Xa,Xb),ADD(Xc,Xd))`, 2 near-predicates (9 nodes), about
60 sums of an input and a constant or `ANY`, 10 `GT(Xi,Xi)` (constant 0),
and a handful of nested sums. Every full predicate is the X0+X1 vs X2+X3
split, present in 20/24 libraries: 3 of the 4 source cells share that
split, so it recurs across cells almost by construction, while the lone
X0+X3 vs X1+X2 source cell's predicate cannot pass the "≥ 2 cells" rule. In
effect every library is "pair sums plus (usually) one comparison skeleton".

The 181 size controls match node count and compiled length but not content:
only 24 are pair sums, 23 are `GT(Xi,Xi)`, and about a third contain no
input at all (`GT(ANY,ANY)`, `ADD(5,X0)`, `IF_GT(2,…)`).

Library donors were drawn for 50.0 % of mutations as designed, but 55.5 %
of those draws were oversize-rejected (ordinary donors: 38 %), so a library
subtree actually entered 22 % of mutation children, i.e. about 11 % of all
children, not the 25 % the proposal assumed. R-size's insertion rate is the
same (10.9 %).

### 2.4 Mechanism diagnostics (observations, not tests)

- **Builds without a predicate entry.** Builds 0, 7, 14, 17 lack the 7-node
  predicate; their R-lib/R-tree ratios are 0.98, 0.66, 0.26, 0.50 (build 14
  carries a 9-node near-predicate `GT(ADD(X0,ADD(X1,1)),ADD(X2,X3))`). The
  20 builds with it range 0.16–0.51 (mean 0.35). Build 0, whose library is
  two pair sums, `ADD(X0,1)`, `IF_GT(X2,X3,X1)` and a nested sum, is the only
  build with no gain. This points at the comparison skeleton as the active
  ingredient, with pair sums alone giving a smaller and variable gain, but
  n = 4 builds is an observation.
- **Final solvers do not carry the entries verbatim.** Exact solvers average
  17 nodes in all arms (R-tree 17.2, R-lib 16.7, R-size 16.8; minimum 10).
  Only 10/1,536 R-lib solvers contain a library predicate as a literal prefix
  substring and 57 contain any ≥ 5-node entry literally (R-size: 0 and 49).
  Literal matching understates reuse (orientation variants, interleaved
  bloat), but the library is not acting as a copy-and-finish template at the
  solver level; it changes what the population explores on the way.
- **R-size is a noisy control, not a neutral one.** Its per-build ratios
  span 0.42–2.10. Builds whose random controls happened to include useful
  pair sums (build 0: `ADD(X0,X3)`; build 9: `ADD(X3,X2)`, `ADD(ADD(X1,X2),0)`)
  gained; builds with 7–9-node junk donors occupying 11 % of children lost up
  to 2×. This is why the R-lib/R-size interval is wider than R-lib/R-tree.
- **Economics.** Acquisition costs 2.88 M evaluations [2.60, 3.16] and 286
  worker-s per library; the per-search saving is 53,243 evaluations
  [46,160, 59,814] and 5.54 worker-s. Repayment needs 54 target searches
  [45, 65] (worker-s: 52 [43, 62]). At a 64-search horizon R-lib's total is
  5.06 M versus 5.59 M for R-tree; at 16 searches it is 3.42 M versus 1.40 M.
  R-size's repayment interval is unbounded (saving interval spans 0).

## 3. What the data shows and does not show

Shows, on the DG development bank with this extractor and restart policy:

1. A frozen library of source-cell subtrees, used as half of the mutation
   donors, cuts restarted tree GP's mean cost to exact solution by a factor
   of about 2.5 (ratio 0.39 [0.33, 0.46]) with no loss of reliability
   (1,536/1,536 solved), in every one of 24 independent acquisitions and in
   all 8 target cells. The effect is far outside the proposal's expected
   0.8–0.95 and past its stated surprise threshold (a gain above 1.3×).
2. The gain is content, not donor size: size- and length-matched random
   donors from the same generator give 0.94 [0.79, 1.12] against R-tree,
   and R-lib beats them 0.41 [0.33, 0.53].
3. The gain is not confined to the target that shares its predicate with
   the sources: excluding it the ratio is 0.43 [0.36, 0.50]. Cells whose pair
   split never appears in any source predicate gain 0.35–0.53.
4. The gain arrives as a higher first-attempt success rate (0.73 vs 0.47)
   and earlier solves, not as smaller or differently shaped final programs.
5. Under acquisition charging the library pays back after about 54 target
   searches; below that it is a net loss.

Does not show:

- Transfer to a fresh bank; DG is development data and 3 of 4 source cells
  share one pair split, so the library is unusually homogeneous.
- Whether the active ingredient is the structural skeleton
  `GT(ADD(·,·),ADD(·,·))`, the pair sums, or simply a token-frequency shift
  toward inputs and `ADD` (every learned entry contains an input; a third of
  the controls contain none). The size control does not separate these; the
  predicate-free builds are suggestive only.
- That this extractor or this acquisition size is needed: the two stage
  libraries built from 16 source jobs already contained the same predicate
  and pair sums, and a hand-written five-entry library would likely
  reproduce most of the effect. The repayment figure of 54 searches is
  therefore an upper bound on what the information costs, not a property of
  the information.
- Anything about the 25 % insertion rate the proposal planned; the realised
  rate was 11 % because most 7–9-node donors are oversize at the 32-token
  cap. A smaller cap-aware insertion or a different rate was not tested.
- A mechanism for why ordinary depth-3 donors, which can generate the same
  skeleton, fall so far behind; the proposal's own reading ("ordinary tree
  search misses composable blocks") is consistent with the data but is not
  tested against alternatives such as reduced destructive mutation.

Files: [analysis_builds_cells.png](analysis_builds_cells.png) (per-build
ratios with predicate-free builds marked; per-cell means). Harness plots
`dynamics.png` and `economics.png` are in the output folder.

## Against the predictions

Read [plan.md](plan.md) after the analysis above was written.

**Precedence table.** B = R-lib/R-tree = 0.390 [0.332, 0.463];
C = R-lib/R-size = 0.414 [0.332, 0.533]; D = solve difference
+0.008 [+0.004, +0.012].

| Row | Condition | Holds? |
|---|---|---|
| 1 | D lower ≤ −0.03 (reliability guard fails) | no (+0.004) |
| **2** | **B upper < 0.90 and C upper < 1** | **yes (0.463, 0.533)** |
| 3 | C lower > 1 | no |
| 4 | B upper < 0.90 only | superseded by row 2 |
| 5 | B lower > 0.85 | no |

Row 2 is the first match: a useful search-content increment, with the
plan's instruction to return to strategy recommending consideration of a
frozen fresh-bank stage, economic usefulness depending on measured repayment
(54 searches [45, 65] per library). The harness label
`useful_search_content_increment_consider_fresh_bank` is correct and is the
frontmatter outcome.

**Expectation versus result.** The proposal expected a modest gain,
B ≈ 0.8–0.95, concentrated in covered cells, with R-size near R-tree. Two
of three held in direction only: R-size is near R-tree (0.94, unresolved),
and the one target sharing a source predicate gained most (0.12). But the
size of the effect (0.39, a 2.6× saving) is past the proposal's own surprise
threshold ("a gain above 1.3× would mean ordinary tree search misses
composable blocks"), and the gain is not concentrated: every cell, including
the four whose pair split never appears in a source predicate, gained
0.35–0.53. The plan's "R-lib beating both arms supports recurring source
content" reading applies. The plan's other named surprises (R-size as good
as R-lib; a gain on uncovered cells) did not occur in the first case and did
occur in the second.

**Plan-mandated inspection.** The plan says implausible savings trigger
inspection of seeds, training sets, VM verification, source-only provenance
and attempt-cost accounting before any mechanism claim. Done in §1: seeds
are paired and disjoint from history; training indices derive from the
shared attempt seed, so all arms saw the same 64 cases; exact solving is
checked on all D625 inputs by the unchanged search loop; the extractor
raises on any non-source row and scoring re-derives all 24 libraries from
the saved source rows; job evaluations equal the sum of attempt evaluations
and no job exceeds 524,288. I found no accounting route by which R-lib could
be under-charged. One design detail differs from the proposal: the realised
library insertion rate is 11 % of children, not 25 %, because 55 % of
library draws are oversize at the 32-token cap. That makes the effect
larger per inserted donor than planned, not smaller.

**What the plan did not anticipate and the steward should weigh.** The
coverage split written into the plan (4 covered / 4 uncovered by pair split)
does not describe the libraries actually learned: only the X0+X1 vs X2+X3
predicate ever recurs across ≥ 2 source cells, so three of the four
"covered" cells received no exact predicate and behave like the uncovered
ones. The learned content is nearly the same five-to-eight entries in every
build (pair sums plus one comparison skeleton), and the stage libraries
built from 16 source jobs already contained them. The fresh-bank stage the
plan points to would be the right next test of transfer; a cheaper
mechanism probe (hand-written {pair sums}, {skeleton only}, and an
input-only token-frequency control at the same insertion rate) would
separate structure from token bias, which neither this run nor a fresh bank
can.
