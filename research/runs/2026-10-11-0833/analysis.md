---
outcome: portable_complete_procedure
---
# Analysis: tree libraries rebuilt from branch-sum (TS) sources, scored on gate-sum B/C (0833)

Reviewer analysis of [proposal.md](proposal.md), [queue.yaml](queue.yaml) and [execution.md](execution.md),
written before reading plan.md. Code at commit `28db964` on `research/2026-10-11-0833`. Raw data:
`experiments/output/2026-10-11/2026-10-11-0833-prepare` and `.../2026-10-11-0833-score`. Every number below
was recomputed from `search.jsonl`, `acquisition.jsonl` and `libraries.json`; the harness `result.json` and
`report.md` agree exactly on means and solve counts, and my own block bootstrap (different RNG, 4,000 draws)
reproduces every harness interval to within 0.02.

## 1. Data completeness

| Check | Result |
|---|---|
| Queue | both entries `done`, runner exit 0; prepare 105 s wall (of 2,700 s), score 3,173 s wall (53 min of 9,000 s); both `stderr.log` empty |
| Validation (prepare) | canonical interpreter/Python/VM agreement on all 12 TS cells and all 144 GS cells; source/target separation passed; 8 saved 0150 off-path replay jobs identical on all deterministic fields; all 24 archived DG libraries reconstructed (768 source rows, 4 failed rows charged) with the original preparation hash; seed audit admitted (pairwise disjoint phases, disjoint from the historical seed snapshot) |
| Stage-0 gate | timing only; projected 269 s preparation / 5,733 s scoring against 2,700 / 9,000 s; admitted. Calibration: 64 TS source jobs 64/64 solved, 96 B/C and 48 native jobs all solved |
| Acquisition | 768 TS source jobs = 24 builds × 4 source cells × 8 jobs; **768/768 solved**; 0.245 M evaluations per build (min 0.115 M, max 0.415 M); mean 7.7 k evaluations per job (per cell 5.8 k / 6.1 k / 7.0 k / 11.7 k) |
| Libraries | 24 TS libraries, sizes 3–10 (median 6.5), 148 entries in total, none empty, so the empty-library fallback never ran (`empty_fallbacks = 0`); 148 size- and length-matched controls, one per entry; scoring re-derived every library and control from the saved rows and seeds and compared deterministically before running |
| Scoring rows | **9,216 / 9,216**: 6,912 B/C rows = 4 arms × 12 cells × 24 builds × 6 repeats, and 2,304 native rows = 3 arms × 8 cells × 24 builds × 4 repeats; 0 duplicate (family, arm, cell, build, repeat) keys |
| Seed pairing | all arms share the identical 8-seed attempt list in every one of the 1,728 B/C slots and 768 native slots (0 mismatches) |
| Failures | B/C: R-tree 5, R-sizeTS 6, R-TS 0, R-DG 0 unsolved jobs, each charged exactly 524,288 after 8 attempts; native: 0 failures in all arms |
| Arm wiring | R-tree rows carry no library statistics; R-TS / R-DG / R-sizeTS rows do; library draws are 50.0 % of mutations in every donor arm; insertions + oversize rejections = library draws in each arm |
| Hashes | the score run's `preparation_hash` equals the prepare run's; `rows_hash` recorded |

Nothing is missing, duplicated or substituted. The B/C R-tree arm reproduces earlier runs on the same cells:
71,036 mean evaluations and 1,723/1,728 solved here against 69,637 and 1,724/1,728 in 0652. The native TS
R-tree arm is a little cheaper than the 0024 reference (5,414 vs 6,672 mean; 768/768 vs 748/768 solved), which
is consistent with 0024 using different cells/seeds; it does not affect any within-run contrast.

## 2. Key numbers

### 2.1 Gate-sum B/C (12 cells, 1,728 jobs per arm, failures at 524,288)

| Arm | Solved / jobs | Mean evaluations | Median | p90 | Geometric mean | First-attempt solves | Jobs > 65,536 | Worker s / job |
|---|---|---|---|---|---|---|---|---|
| R-tree | 1,723 / 1,728 | 71,036 | 38,656 | 198,144 | 28,689 | 921 (53 %) | 807 (46.7 %) | 6.63 |
| **R-TS** | **1,728 / 1,728** | **27,124** | **5,888** | **73,472** | **9,869** | **1,345 (78 %)** | **383 (22.2 %)** | **2.40** |
| R-DG | 1,728 / 1,728 | 26,281 | 5,888 | 73,216 | 9,704 | 1,365 (79 %) | 363 (21.0 %) | 2.32 |
| R-sizeTS | 1,722 / 1,728 | 66,844 | 25,472 | 199,424 | 24,108 | 977 (57 %) | 751 (43.5 %) | 6.13 |

Contrasts (ratio of means over equal-weight cells; 95 % block bootstrap over the 24 build slots, paired for
R-TS / R-tree and R-TS / R-sizeTS, independent DG cohort resampling for R-TS / R-DG):

| Contrast | Evaluation ratio [95 %] | Worker-second ratio [95 %] | Solve-fraction difference [95 %] |
|---|---|---|---|
| **Primary: R-TS / R-tree** | **0.382 [0.335, 0.433]** | 0.362 [0.315, 0.414] | +0.003 [+0.001, +0.005] |
| R-TS / R-sizeTS (content beyond size) | 0.406 [0.344, 0.482] | 0.392 [0.331, 0.467] | +0.003 [+0.001, +0.006] |
| R-TS / R-DG (independent cohorts) | 1.032 [0.862, 1.224] | 1.035 [0.858, 1.239] | 0 [0, 0] |
| R-DG / R-tree (descriptive) | 0.370 [0.325, 0.435] | – | – |
| R-sizeTS / R-tree (descriptive) | 0.941 [0.807, 1.090] | – | – |

Decision-rule inputs for the primary comparison: upper bound 0.433 < 0.80, solve-difference lower bound +0.001 > −0.03.
The harness label is `worthwhile_saving_supported` with `content_increment_supported` for the size control;
routing `portable_complete_procedure_return_to_strategy`.

Robustness, all descriptive:

- R-TS's per-build mean is below R-tree's in **24/24 builds** (per-build ratios 0.19–0.68, all under 0.80).
  R-sizeTS is below R-tree in 13/24 builds (0.35–1.85).
- Per cell, R-TS / R-tree ranges 0.29–0.61 and every one of the 12 per-cell intervals has upper bound below 0.80
  ([figure](analysis_cells_builds_economics.png), left). R-DG ranges 0.24–0.50. R-sizeTS straddles 1 in 11/12 cells.
- Solved jobs only (common solves): 0.390. Charging failures at half or double the cap moves the ratio to
  0.386 / 0.374. Failures do not drive the result.
- No relation between TS library size (3–10 entries) and the per-build B/C gain (Spearman −0.23).
- R-TS and R-DG are nearly identical on every distribution statistic (median, p90, first-attempt rate, tail
  fraction). The R-TS / R-DG interval [0.86, 1.22] cannot resolve a difference in either direction; the
  harness prices resolution at about 796 further builds, i.e. not a sensible next experiment.

### 2.2 Native TS targets (8 cells, 768 jobs per arm, reported separately, never pooled)

| Arm | Solved / jobs | Mean evaluations | Median | p90 | First-attempt solves | Jobs > 65,536 | Worker s / job |
|---|---|---|---|---|---|---|---|
| R-tree | 768 / 768 | 5,414 | 3,072 | 8,960 | 758 (98.7 %) | 10 (1.3 %) | 0.38 |
| R-TS | 768 / 768 | 9,622 | 3,840 | 22,016 | 732 (95.3 %) | 36 (4.7 %) | 0.76 |
| R-DG | 768 / 768 | 7,198 | 2,816 | 11,520 | 741 (96.5 %) | 27 (3.5 %) | 0.54 |

| Contrast | Evaluation ratio [95 %] | Worker-second ratio [95 %] |
|---|---|---|
| R-TS / R-tree | **1.777 [1.578, 2.000]** | 1.976 [1.707, 2.296] |
| R-DG / R-tree (descriptive) | 1.329 [1.122, 1.574] | – |
| R-TS / R-DG | 1.337 [1.116, 1.604] | – |

Both libraries make the native TS search **more** expensive; the lower bound of 1.58 excludes any saving. The
harness label is `saving_at_least_20pct_excluded`. Per build, R-TS / R-tree exceeds 1 in 23/24 builds (0.90–3.47)
and is unrelated to library size (Spearman −0.14). All jobs solve, so the loss is in restarts: 26 extra
second-or-later attempts for R-TS against R-tree's 10, and a heavier tail (p90 22,016 vs 8,960). On a task that
R-tree solves on the first attempt 98.7 % of the time in about 3 k evaluations, spending half of all mutations
on library draws (48 % of which are then rejected as oversize) is a cost with nothing to buy.

### 2.3 Library content (audit of the 24 TS and 24 DG libraries)

| | TS libraries (148 entries) | DG libraries (181 entries) |
|---|---|---|
| Entry sizes | 144 × 3 nodes, 3 × 4, 1 × 5 | 131 × 3, 3 × 4, 23 × 5, 21 × 7, 3 × 9 |
| ADD-rooted entries | 131 (of which 60 distinct-input pair sums `ADD(Xi,Xj)`, 55 input+constant, 16 input+ANY) | 116 3-node ADD (55 pair sums) plus nested ADDs |
| GT-rooted entries | 13 (7 `GT(Xi,Xi)`, 4 `GT(Xi,const)`, 2 `GT(Xi,Xj)`) | 15 three-node plus the 7-node `GT(ADD,ADD)` predicate in **21/24** libraries |
| 7-node predicate | **0 / 24 libraries** | 21 / 24 |
| Recurring pair sums | X0+X2 in 24/24, X1+X2 in 23/24 (the two sums shared by the TS source formulas); X0+X3 in 6, X1+X3 in 5 | X2+X3 and X0+X1 in 24/24 (the DG split); X0+X3 in 4, X1+X2 in 2, X1+X3 in 1 |
| Pair sums matching a B/C destination split | every library has ≥ 1 for each of the two B/C splits | **18/24 libraries have none**; 5 have one; 1 has both |
| Controls | 148, same node sizes; 71 GT-rooted, 44 contain ANY, 19 contain no input | 181, same node sizes |

So the TS libraries are, as the proposal's probe predicted, DG libraries minus the comparison skeleton:
small, almost entirely 3-node, ADD-dominated. The size control differs from the learned entries mainly in
composition (48 % GT-rooted and 30 % containing ANY, against 9 % and 11 % for learned entries), which is what
the R-TS / R-sizeTS contrast measures.

### 2.4 Acquisition economics (B/C, acquisition jointly resampled with its library)

| | R-TS | R-DG | R-sizeTS |
|---|---|---|---|
| Acquisition, evaluations per library | 0.245 M [0.218, 0.275] | 2.877 M [2.602, 3.160] | 0.245 M |
| Saving per B/C search vs R-tree | 43.9 k [39.3 k, 48.7 k] | 44.8 k [39.2 k, 49.7 k] | 4.2 k [−6.1 k, 13.5 k] |
| Searches to repay acquisition (evaluations) | **5.6 [4.9, 6.4]** | 64 [54, 76] | 58, unbounded in 20 % of draws |
| Searches to repay (worker seconds) | 4.0 [3.5, 4.7] | 66 [56, 78] (historical host) | – |
| (acquisition + 10 searches) ÷ 10 R-tree searches | 0.73 [0.67, 0.79] | 4.42 [3.93, 4.94] | 1.26 |
| at 100 searches | 0.42 [0.37, 0.47] | 0.78 [0.70, 0.86] | 0.99 |

The TS source family is 12× cheaper to learn from (every source job solved, 7.7 k evaluations each against
DG's 90 k) and buys the same B/C saving, so a TS library pays for itself after about six B/C searches
([figure](analysis_cells_builds_economics.png), right). Minor: the harness `price()` charges 64 source jobs
per extra build instead of 32 (code review note 2); this only inflates the quoted R-TS / R-DG resolution price
by about 7 % and touches nothing else.

## 3. What the data show

1. **The recipe is portable across source family on this development bank.** Libraries learned from the four
   TS sources cut restarted tree GP's cost on the 12 gate-sum B/C cells to 0.38 [0.33, 0.43] of R-tree,
   indistinguishable from the DG-learned libraries (0.37) and well below the 0.80 margin, with no loss of
   reliability (R-TS solved all 1,728 jobs). The gain is in every build and every cell.
2. **Learned content, not donor size, carries the gain** (R-TS / R-sizeTS 0.41 [0.34, 0.48]), as in 0150 and 0652.
3. **The DG comparison skeleton is not needed for the B/C gain.** The TS libraries contain no `GT(ADD,ADD)`
   predicate at all and give the same B/C saving as DG libraries that carry it in 21/24 cases. The relabelled-
   skeleton route left open by question 47 is therefore not what moved B/C in 0150.
4. **Destination-matching pair sums are also not necessary.** 18/24 DG libraries contain no pair sum belonging
   to either B/C split and still give 0.37; TS libraries always contain one for each split and give 0.38. What
   both families share is a small supply of `ADD(input, input)` and `ADD(input, constant)` donors. This is
   consistent with question 48's ADD-heavy label-law reading and sharpens it: the specific pairs seem not to
   matter on B/C.
5. **The same libraries harm the native TS target** (1.78 [1.58, 2.00]), and so do the DG libraries (1.33).
   On a task the baseline solves in ~3 k evaluations with 99 % first-attempt success, the fixed 0.5 library
   mix adds restarts and a long tail. This is a cost of the mixing policy on easy targets, not a property of
   TS content specifically; explanation (c) in question 49 (native-only reuse) is the opposite of what happened.
6. **Acquisition is cheap enough to matter**: a TS library repays itself after about six B/C searches
   against about 64 for a DG library.

## 4. What the data do not show

- Nothing here is a fresh-bank transfer claim: both source rosters and the B/C destination are development
  banks that prior decisions (0150, 0348, 0524, 0652) rested on. The extractor, 0.5 mix, restart schedule and
  cutoff were all fixed; only the source family changed.
- The R-TS / R-DG contrast (1.03 [0.86, 1.22]) is uninformative about which family yields the better library;
  the design was not sized for it and resolving it is not worth the price.
- The audit shows that neither skeletons nor split-matching pair sums are *necessary*; it does not show what
  *is* sufficient. Point 4 is an observation on two cohorts, not a controlled contrast; a label-law or
  statistical generator test (strategy's "simpler generator" branch) is the experiment that would settle it.
- The native TS harm was measured only at mix 0.5 with libraries of 3–10 entries. It says that the complete
  procedure should not be applied blindly to near-solved targets; it does not say whether a lower mix, or
  gating the library on a failed first attempt, would remove the harm.
- Worker-second ratios include the DG acquisition cost measured on a historical host; evaluation counts are
  the comparable unit.

## Against the predictions

Read after the analysis above was written. [plan.md](plan.md) ran exactly as specified: 768 acquisition jobs,
9,216 scoring jobs, no downsizing or extension, stage 0 timing-only (admitted at 269 / 5,733 s projected),
all validation gates passed, seeds published and audited.

| Plan / proposal prediction | Observed | Verdict |
|---|---|---|
| **Portable**: B/C R-TS / R-tree upper < 0.80 and solve-difference lower > −0.03 | 0.382 [0.335, 0.433]; +0.003 [+0.001, +0.005] | **met** — supports complete-procedure portability between these development rosters (harness: `portable_complete_procedure_return_to_strategy`) |
| Proposal expectation R-TS / R-tree ≈ 0.4–0.6, "a little weaker than R-DG" | 0.38, with R-TS / R-DG 1.03 [0.86, 1.22] | slightly stronger than expected; no detectable difference from DG |
| R-TS resolved below R-sizeTS | 0.406 [0.344, 0.482] | met (`content_increment_supported`) |
| Repayment within roughly 5–10 searches | 5.6 [4.9, 6.4] searches in evaluations, 4.0 [3.5, 4.7] in worker seconds | met |
| Acquisition ≈ 0.21 M evaluations per library (a projection, as plan.md noted) | 0.245 M [0.218, 0.275]; 12× cheaper than DG rather than 13× | close; the plan was right to call the earlier figure a projection |
| Native TS: small gain (0.6–1.0), "possibly harm from 32-token crowding" | 1.78 [1.58, 2.00]; native saving excluded (`saving_at_least_20pct_excluded`) | **missed**: a clear loss, not a small gain. Crowding is not the explanation (libraries are 3–10 three-node entries, and harm is unrelated to library size); the cost is the 0.5 library mix adding restarts on a target the baseline solves first time 99 % of the time |
| Surprise 1: R-TS ≥ 0.8 with R-DG ≈ 0.4 (skeletons carried B/C) | R-TS 0.38, R-DG 0.37 | did not occur; the 48 reading (ADD-heavy supply) stands, and the audit adds that the 7-node predicate is absent from all 24 TS libraries |
| Surprise 2: R-TS ≈ R-sizeTS | 0.41 | did not occur |
| Plan: "If TS fails to reproduce DG's saving, responsible content remains unidentified" | TS reproduced it | the conditional did not trigger; the cross-cohort audit (§2.3, §3 points 3–4) is observational and makes no skeleton-only or mechanism claim |

The plan's routing rule for the primary result is "return to strategy" for the choice between the
unfamiliar-content boundary and a simpler statistical generator. The native-TS loss is a new, decision-relevant
fact for that choice: the complete procedure at mix 0.5 is a net cost on targets the baseline already solves
cheaply, so any next design that applies libraries by default should gate or lower the mix on easy targets,
or accept that the method's value is confined to hard destinations like B/C.
