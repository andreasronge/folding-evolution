---
outcome: PASS
---
# Analysis: restarted tree GP versus restarted and full-cap A8 (0024)

Reviewer analysis of [proposal.md](proposal.md), [queue.yaml](queue.yaml) and
[execution.md](execution.md). Code: commit `1773d11` on
`research/2026-10-11-0024`. All numbers below were recomputed from the raw
`search.jsonl` rows with [analysis_recompute.py](analysis_recompute.py)
(output in [analysis_recompute.log](analysis_recompute.log)); the harness
`result.json`/`report.md` values agree to the printed precision. Bootstrap
intervals here use a different RNG seed (777) from the harness (2230024) and
reproduce its intervals to three decimals.

## 1. Data completeness

All three queue entries finished with exit 0 (prepare 186 s, DG 1626 s,
TS 377 s; 2.5 h of timeouts, about 36 min used).

| Family | Rows | Duplicates | Grid 8 cells × {R-tree 24×4, R-A8 24×4, F-A8 24×2} | Failures counted |
|---|---|---|---|---|
| DG | 1920 | 0 | complete (768/768/384) | every unsolved job spent exactly 524,288 |
| TS | 1920 | 0 | complete (768/768/384) | every unsolved job spent exactly 524,288 |

Checks that passed on every row of both families:

- Job evaluations equal the sum of its attempt evaluations; no job exceeds
  524,288; every restarted attempt ran at cutoff 65,536; F-A8 jobs have one
  attempt at cap 524,288. The stop rule holds: only the last attempt of a
  job is solved, never an earlier one. No `force_cap` attempt.
- Seeds follow the published formulas (`22300000 + 1000·(8f+c) + 8·(4b+r) + k`
  in roster order, F-A8 `22320000 + …`). All 768 R-tree/R-A8 job pairs per
  family share their eight attempt seeds (intended). No seed used by any
  attempt appears in the 2254 rows; the only multiplicity is the intended
  pair sharing.
- Preparation: semantic/grammar check passed, 8/8 first-attempt equivalence
  checks against the ordinary capped search, 8/8 deterministic job replays,
  16/16 saved native A8 replays matched; historical-artifact hashes matched.
  Stage 0 projected DG wall 2254 s against a 4500 s ceiling and admitted
  scoring. Actual DG search wall was 1570 s at effective concurrency 9.9.
- First attempts reproduce the 2254 cutoff-truncated rates: DG tree
  350/768 = 0.456 versus 179/384 = 0.466 historical; DG A8 345/768 = 0.449
  versus 174/384 = 0.453. TS tree 0.974 versus 0.966; TS A8 0.792 versus 0.810.
- Restart overhead: the wrapper adds no measurable worker time (job seconds
  equal attempt seconds), and cost per evaluation is flat across attempt
  index (tree 98–100 µs, A8 53–57 µs). The "overhead above 30 %" surprise
  did not occur.

Nothing is missing, duplicated or failed. The data is complete for the
pre-registered analysis.

## 2. Key numbers

### 2.1 DG (primary)

Means over 8 cells with equal weight; failures charged the full 524,288.
Intervals are paired block bootstraps over the 24 acquisition builds
(8192 draws). Solve denominators are jobs.

| Arm | Solved / jobs | Mean evaluations | Median | Mean worker s | µs per evaluation |
|---|---|---|---|---|---|
| R-tree | 765/768 = 0.996 | 90,392 | 68,608 | 8.86 | 98 |
| R-A8 | 754/768 = 0.982 | 114,137 | 76,416 | 6.39 | 56 |
| F-A8 | 321/384 = 0.836 | 156,984 | 59,904 | 10.14 | 65 |
| 2254 full-cap tree (unpaired reference) | 202/384 = 0.526 | 263,353 | – | 28.18 | 107 |
| 2254 full-cap A8 (unpaired reference) | 314/384 = 0.818 | 177,639 | – | – | 66 |

| Contrast | Evaluation ratio [95 %] | Worker-second ratio [95 %] | Solve difference [95 %] |
|---|---|---|---|
| **R-tree / R-A8 (primary)** | **0.792 [0.682, 0.915]** | 1.388 [1.196, 1.604] | +0.014 [0.000, 0.034] |
| R-tree / F-A8 | 0.576 [0.501, 0.668] | 0.874 [0.760, 1.016] | +0.160 [0.124, 0.198] |
| R-A8 / F-A8 | 0.727 [0.647, 0.814] | 0.630 [0.558, 0.709] | +0.146 [0.112, 0.180] |

Decision-rule inputs: the primary ratio's upper bound 0.915 is below 1, and
the lower bound of the solve-fraction difference is 0.000, above −0.03. The
harness classifies this as `tree_evaluation_win_with_noninferiority`,
`reliability_status: within_three_percentage_points`. The reliability bound
sits exactly on zero: in 2.5 % of build resamples tree and A8 solve equally
or A8 solves more. Noninferiority within three points is established;
"equal reliability" is not.

Sensitivities, all descriptive:

- Geometric mean with failures at 2×cap: R-tree 35,095, R-A8 65,425,
  F-A8 74,177; R-tree/R-A8 = 0.536 [0.435, 0.651]. The tree arm's median
  advantage is larger than its mean advantage because its solves cluster in
  attempt 1 (median solved attempt 6,400 evaluations versus 25,344 for A8).
- Cell-resampled interval (8 cells, not the pre-registered unit): [0.719,
  0.874]. Per-cell ratios range 0.639 to 0.982; tree is cheaper in all eight
  cells, with the smallest margin on `(X1+X3)>(X0+X2)?X3:X1`.
- Leave-one-build-out ratio ranges 0.767 to 0.834. Build 16 (the weakest
  2254 build, 9/16 solves there) is the single strongest driver: R-A8 solved
  25/32 jobs on it at a mean of 259,536 evaluations, and 7 of R-A8's 14 DG
  failures are on that build. Excluding it the ratio is 0.834, still below
  the full-sample upper bound.
- Per build, R-tree's mean is below R-A8's in 20 of 24 builds
  ([analysis_builds_cells.png](analysis_builds_cells.png), left).

### 2.2 Attempt structure (DG)

| Solving attempt | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | all 8 failed |
|---|---|---|---|---|---|---|---|---|---|
| R-tree (768 jobs) | 350 | 183 | 105 | 59 | 35 | 17 | 10 | 6 | 3 |
| R-A8 (768 jobs) | 345 | 171 | 112 | 48 | 43 | 20 | 14 | 1 | 14 |

Conditional per-attempt success among jobs reaching that attempt: tree
0.456, 0.438, 0.447, 0.454, 0.493, 0.472, 0.526, 0.667 (flat; the
independence projection 1−(1−0.456)^8 = 0.992 matches the observed 0.996).
A8: 0.449, 0.404, 0.444, 0.343, 0.467, 0.408, 0.483, 0.067 (drifting down;
the projection 0.992 overstates the observed 0.982 by 7 jobs). That is the
build-heterogeneity effect the critique predicted: an A8 job keeps its build,
so later attempts are enriched for weak builds. It is a fixed-build effect,
not evidence of dependence between attempts within a build.

Among the 321 F-A8 solves, 199 came by 65,536 evaluations, 97 between
65,536 and 262,144, and 25 later. Full-cap A8 does keep solving late, and
the restart schedule discards those late solves, yet R-A8 still spends 27 %
fewer evaluations than F-A8 and solves 15 points more jobs. On this roster
a fresh seed at 65,536 beats continuing.

### 2.3 Cost units and economics (DG)

Tree GP costs 1.75× more worker time per evaluation than A8 here (98 versus
56 µs), so the evaluation win is a worker-time loss: R-tree 8.86 s per job
versus R-A8 6.39 s, ratio 1.388 [1.196, 1.604]. Against F-A8 the worker-time
ratio is 0.874 [0.760, 1.016], unresolved.

Harness economics (acquisition cost from the saved 2254 build timings, mean
12.5 M evaluations or 772 worker seconds per build):

- In evaluations, A8 saves nothing (saving −23,745 [−41,095, −8,596] per
  search against R-tree), so the repayment horizon is unbounded.
- In worker seconds, R-A8 saves 2.48 s [1.39, 3.52] per search; the
  acquisition repays after about 312 searches [211, 579] on this roster.
  Per build this ranges from never (6 builds with negative saving) to 162.

### 2.4 TS (descriptive, never pooled with DG)

| Arm | Solved / jobs | Mean evaluations | Mean worker s |
|---|---|---|---|
| R-tree | 768/768 | 6,672 | 0.49 |
| R-A8 | 768/768 | 36,952 | 1.84 |
| F-A8 | 369/384 = 0.961 | 59,125 | 3.29 |
| 2254 full-cap tree | 382/384 | 11,496 | 0.97 |

R-tree/R-A8 evaluations 0.181 [0.159, 0.202]; worker seconds 0.265 [0.225,
0.305]; solve difference 0. Tree is cheaper in all eight cells and all 24
builds, in both units. R-A8/F-A8 evaluations 0.625 [0.502, 0.790]. Tree
solved 748/768 jobs on attempt 1 and needed at most 3 attempts; A8 needed up
to 5.

### 2.5 Shortcut check

Solves are D625-exact, so training-case shortcuts cannot count as solves.
They are, however, common in the tree arm: 9.6 % of all R-tree evaluations
on DG were spent on individuals that were perfect on the 64 training cases
but not D625-exact, against 0.18 % for R-A8; 309 of tree's 921 failed
attempts held such a program at cutoff, versus 11 of A8's 1,014. Since each
attempt redraws its training cases, part of the restart benefit for tree GP
is escape from an overfitted training sample, not only a fresh population.
The two effects were not separated here.

Figures: [analysis_solve_curves.png](analysis_solve_curves.png) (solve
fraction against job expenditure, with the 2254 full-cap references dashed),
[analysis_builds_cells.png](analysis_builds_cells.png) (paired per-build
means, per-cell spread). Harness plots: `dynamics.png`, `economics.png` in
the output folders.

## 3. What the data shows and does not show

Shows:

- Under the same 8 × 65,536 restart schedule, on the fixed DG roster, tree GP
  spends fewer evaluations than A8 (ratio 0.79, interval entirely below 1)
  and is at least as reliable within three points. A8's remaining DG
  evaluation advantage from question 43 was an artefact of the full-cap
  schedule, not of the representation.
- Restarting also helps A8 itself (R-A8 beats F-A8 by 27 % in evaluations and
  15 solve points), so the old "A8 is more reliable than tree" result was
  mostly a schedule effect too: both restarted arms solve about 98–100 %.
- The evaluation win is not a worker-time win on DG. Tree GP evaluations cost
  1.75× more, so R-A8 is 28 % cheaper in worker seconds per search. On that
  unit A8's acquisition repays after roughly 300 searches per build.
- On TS, restarted tree beats restarted A8 by about 5× in evaluations and
  about 4× in worker seconds with no reliability difference.

Does not show:

- Anything about optimal cutoffs or Luby schedules; one cutoff was tested.
- Anything beyond these two development rosters; no transfer claim.
- Why A8 is slower in evaluations: the data is consistent both with A8's bias
  being too weak to beat a plain tree search that resamples training cases,
  and with the restart schedule simply suiting a heavy-tailed solve-time
  distribution that both arms share. The shortcut statistic (§2.5) points at
  training-case resampling as a mechanism for the tree arm but is not a test
  of it.
- Equal reliability: the solve-difference lower bound is exactly 0.000, so
  the three-point margin is met but not with room to spare, and 7 of A8's
  14 failures come from one build.

Outcome relative to the proposal's rules: "upper < 1 and reliability holds",
with the critique's qualification that this is an evaluation-count result
and the worker-time direction is the opposite.

## Against the predictions

The plan's outcome grid has R (paired 24-build bootstrap) and D (solve
difference) with the guard "D lower > −0.03". Observed: R = 0.792 [0.682,
0.915], so R upper < 1; D = +0.014 [0.000, 0.034], so D lower > −0.03. That
is the grid's **PASS** cell: no A8 evaluation saving on this roster and
schedule within the three-point reliability margin; R-tree becomes the
evaluation comparator. The harness reached the same classification.

Prediction by prediction:

- **R between 0.65 and 0.9**: observed 0.79, within the range; the
  cell-pooled historical projection (0.78) was close to the point estimate.
- **Both restarted arms solve 98–99 %**: tree 99.6 %, A8 98.2 %. The
  build-pooled sensitivity (A8 96.4 %) was too pessimistic and the
  cell-pooled one (98.7 %) slightly optimistic; the observed value sits
  between them, as the plan said neither pooling would capture cell×build.
- **A8 below 95 % as a surprise**: did not occur. The plan asked for
  fixed-build inspection rather than a dependent-attempt claim if A8 fell
  short of projection; the inspection in §2.2 attributes the 7-job shortfall
  against the independence projection to build heterogeneity (half of the
  failures on build 16), consistent with the plan's hypothesis text.
- **TS R about 0.2**: observed 0.18 [0.16, 0.20].
- **Restart overhead above 30 % of wall**: not observed; the wrapper adds no
  measurable worker time, and DG search wall (26 min) was under the Stage 0
  projection (38 min).
- **Power**: the plan qualified the 90 % resolution claim; the cost
  interval resolved with the upper bound 0.085 below 1, and the reliability
  guard passed with its lower bound exactly at 0 (margin 0.03 to spare).
  The harness resolution price reports no additional builds needed.
- **Seconds loss alongside an evaluation win**: the plan anticipated this
  case ("leaves purchasing dependent on the owner's cost objective"). It
  occurred: worker-second ratio 1.39 [1.20, 1.60] against R-A8. The PASS
  label is on evaluations only, as the scope tag requires.
- **Degenerate-success guard**: the near-boundary reliability result and the
  TS 768/768 solves triggered inspection. Seeds follow the formulas, every
  job's attempts are present and accounted, no seed overlaps 2254, first
  attempts reproduce the 2254 cutoff-truncated rates, and all solves are
  D625-exact. No artefact found.

Pre-registered scope holds: fixed DG/TS development rosters, saved 1717
builds, one cutoff. No transfer, optimal-policy, equal-reliability or
learning-is-useless claim follows. Decision rule says return to strategy
with both cost units and reliability reported, no automatic follow-up.
