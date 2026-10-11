---
outcome: retained
---
# Analysis: fixed sum-donor prior vs acquired TS libraries on gate-sum B/C

Reviewer: independent re-analysis of `search.jsonl` and `result.json` from the score run
(commit `e29219b`). Output folders:
`experiments/output/2026-10-11/2026-10-11-1019-prepare` and `…-score`. The researcher's
`report.md` and `result.json` were read only after my recomputation; all headline numbers
below were reproduced from the raw rows (ratio of means with equal cell weights,
block bootstrap over the 24 build slots, 4,000 draws with a different seed) and agree
with `result.json` to the third decimal.

## 1. Data completeness

| Check | Result |
|---|---|
| Queue entries | 2/2 done, exit 0. Prepare 49 s wall; score 1,881 s wall (gate projected 4,060 s; 7,200 s limit) |
| Score rows | 5,184 = 3 arms × 12 cells × 24 build slots × 6 repeats; 0 duplicates, 0 missing units |
| Seed pairing | all 1,728 units share identical 8 attempt seeds across the three arms (0 mismatches); 13,824 attempt seeds, all distinct |
| Arm wiring (from the rows) | library draws R-tree 0, R-TS 11.13 M, R-hand 9.47 M; every R-hand attempt reconciles P+K class counts with the engine's own library counters |
| TS reconstruction | passed: 24 builds from 768 source jobs, 0 failed source jobs, library hash equal to archived 0833 |
| Replay of 8 historical R-tree jobs | passed, all deterministic fields |
| Hand prior | 192 entries, 44 distinct, 96 P / 96 K; token ids checked (ADD = 9, inputs 0–3, constants 5–8 = {0,1,2,5}); verification passed |
| Capped failures (8 × 65,536 charged) | R-tree 5/1,728; R-TS 0/1,728; R-hand 0/1,728 |

Nothing is missing, nothing is duplicated, and the stage-0 gate was timing-only as
registered. The 72 stage jobs reran the identical fixed-seed set from the admission check.

## 2. Key numbers

Primary: mean capped evaluations per job, cells equally weighted, failures at 524,288,
95% paired block bootstrap over the 24 build slots.

| Arm | Jobs | Solved | First-attempt solves | Mean capped evals | Median evals | Mean worker-s |
|---|---|---|---|---|---|---|
| R-tree | 1,728 | 1,723 | 940 | 70,481 | 36,224 | 6.49 |
| R-TS | 1,728 | 1,728 | 1,372 | 26,300 | 6,272 | 2.30 |
| R-hand | 1,728 | 1,728 | 1,408 | 22,415 | 5,632 | 1.93 |

| Contrast | Evaluations ratio [95%] | Worker-seconds ratio [95%] |
|---|---|---|
| **R-hand / R-TS (primary)** | **0.852 [0.762, 0.958]** | 0.840 [0.747, 0.950] |
| R-hand / R-tree | 0.318 [0.291, 0.349] | 0.297 [0.271, 0.327] |
| R-TS / R-tree | 0.373 [0.337, 0.411] | 0.353 [0.317, 0.391] |

Solve-rate differences: R-hand − R-tree = +0.0029 [+0.0006, +0.0052]; R-hand − R-TS = 0
(both solved everything). R-TS / R-tree replicates run 0833 (0.382 [0.335, 0.433] there)
on fresh seeds.

Decision rule, applied: primary upper 0.958 < 1.25 ✓; R-hand/R-tree upper 0.349 < 0.80 ✓;
solve difference lower +0.0006 > −0.03 ✓. All three retention conditions hold. The
"learned increment" branch (lower > 1.25) is far away: the lower bound is 0.76.

### Heterogeneity (secondary, no rules)

Plot: `hand_vs_ts_ratios.png` (per-build and per-cell R-hand/R-TS with intervals).

- **Per build slot** (point ratio hand/TS over 12 cells × 6 repeats): 19/24 below 1,
  5/24 above 1 (builds 1, 3, 19, 20, 21; the largest 1.78 at build 20). No single
  build's interval excludes 1 on the learned side except build 20 (TS/hand 0.56
  [~0.47, ~0.8]). Per-unit pairing: hand cheaper in 889, TS cheaper in 807, tie in 32
  of 1,728 units, so the mean advantage comes from the tail of expensive TS jobs,
  not from a uniform shift.
- **Per split**: split (02|13) hand/TS 0.975 [0.851, 1.125] (no difference); split
  (03|12) 0.749 [0.621, 0.899] (hand cheaper).
- **Per cell**: 8/12 cells have hand/TS point < 1, 4/12 > 1. One cell,
  `(X0+X2)>(X1+X3)?(X1+X2):X3`, has TS clearly cheaper: hand/TS 1.60 [1.12, 2.22].
  Its sibling cells on the same split are 0.93–1.10. The strongest hand advantage is
  on `(X1+X2)>(X0+X3)?(X1+X2):X1`, 0.66 [0.47, 0.94].
- **Donor classes in R-hand**: P (pair sums) 4.73 M draws, insertion rate 0.508;
  K (input+constant) 4.74 M draws, insertion rate 0.576. Draw mass is ½/½ as
  frozen; overall insertion rate 0.542 vs R-TS 0.525 under the same 32-token cap.
- **TS library audit** (from `libraries.json`): 3–10 entries per library, pair-sum
  fraction mean 0.45 (range 0.25–1.0). Across the 24 libraries the unordered pair
  X0+X2 appears in 24/24 and X1+X2 in 23/24; X0+X3 in 6, X1+X3 in 5, X2+X3 in 1,
  X0+X1 in 1. The hand prior gives all six pairs equal mass.
- **Economics** (evaluations, TS acquisition 245 k [218 k, 274 k] per library): TS vs
  R-tree repays after 5.5 searches [4.7, 6.6]. TS vs R-hand never repays within 200
  searches: cumulative ratio 1.23 [1.10, 1.37] at 200; the bootstrap fraction with any
  positive saving is 0.4%.
- **Failure sensitivity**: charging failures at 262,144 instead of 524,288 moves
  hand/TS not at all (no failures) and the two tree ratios by < 0.004.
- Dynamics plot (`dynamics.png` in the score folder): R-hand and R-TS solve curves
  track each other closely over all budgets, both far above R-tree; output diversity is
  slightly higher for R-hand than R-TS throughout.

## 3. What the data shows

1. On this bank (gate-sum B/C, 12 cells, development data) a fixed donor set of
   `ADD(input,input)` and `ADD(input,const)` forms written from the alphabet alone saves
   at least as many evaluations as the 24 acquired TS libraries, with the interval
   excluding the 1.25 margin and in fact excluding 1 (0.76–0.96). It also beats R-tree
   by the same wide margin TS does (0.32 vs 0.37 of R-tree).
2. The hand prior costs no acquisition. Priced with acquisition, TS libraries never
   repay against the hand prior on these cells within any horizon tested.
3. The retention is robust to the secondary views: both splits ≤ 1, 19/24 builds ≤ 1,
   solve rate 100% in both arms, worker-seconds agree with evaluations.
4. The R-TS/R-tree saving itself replicated on fresh seeds (0.373 vs 0.382 in 0833),
   so the comparator arm was healthy.

## 4. What the data does not show

- **Not an ingredient isolation.** The prior differs from TS libraries in several
  ways at once (all six pairs vs two; four constants vs mostly 0/1; 192-entry draw law
  vs 3–10 entries; no ANY/GT/nested entries). Which of these matters is not tested.
  The split-level pattern (hand's gain concentrated on split (03|12), where TS
  libraries rarely contain X0+X3) and the one cell where TS wins (its three needed sums
  are the two that TS concentrates on) are *consistent with* "coverage of the gate
  pairs is the active ingredient, and learned concentration helps where it happens to
  cover", but this is a post-hoc reading of 12 cells and stays a hypothesis.
- **Not a transfer claim.** The bank is development data, the alphabet is `v2_x4`
  only, and the prior was written knowing the task family uses sums of inputs. The
  claim is substitution within this family, as the proposal scoped it.
- **Not "TS is useless".** The per-build spread (0.48–1.78) says some learned
  libraries do beat the prior on these cells; the mean says acquisition is not worth its
  price here. Whether a cheaper acquisition or a library that *adds to* the prior
  would help is open (not tested).
- **Not a statement about the learned-vs-prior gap beyond 1.25.** The interval
  width is ~0.20 on the ratio, as projected. A true ratio between 0.76 and 0.96 is
  all that is supported.
- Worker-time acquisition costs for TS are historical-host measurements; the
  evaluations-based economics is the clean one.

No shortcut solutions were found: all solves are exact per the existing interpreter/VM
check, and per-attempt validation reran in `validate_rows`.

## Against the predictions

Read `plan.md` after the analysis above was written. The plan registers the same rule as
the proposal: retained iff primary upper < 1.25 and R-hand/R-tree upper < 0.80 and
hand − tree solve difference lower > −0.03; learned increment iff primary lower > 1.25;
otherwise unresolved. It also registers the expectation "retention, R-hand/R-TS ≈
0.9–1.15" and names two surprises: lower > 1.25, or R-hand ≈ R-tree (dilution by breadth).

- **Outcome label: retained.** All three predicates hold (0.958 < 1.25; 0.349 < 0.80;
  +0.0006 > −0.03). No gate, fallback or sample change occurred; the design ran at the
  registered fixed size (24 slots, 1,728 jobs per arm).
- **Direction matched, magnitude slightly beyond the expected band.** The observed
  ratio 0.85 [0.76, 0.96] sits below the predicted 0.9–1.15 and excludes 1. The hand
  prior is not merely a within-margin substitute; on this bank it is cheaper than the
  learned libraries. Neither registered surprise occurred: the lower bound is nowhere
  near 1.25, and R-hand/R-tree is 0.32, not ≈ 1, so breadth did not dilute the useful
  pairs the way R-unif's 0.755 in question 48 suggested it might.
- **Feasibility predictions held.** Projected 4,045 s; actual score wall 1,881 s.
  R-hand worker-s/job 1.93 vs the assumed ≤ 6.63 floor. Interval half-width on the log
  ratio ≈ 0.11, inside the projected ≈ 0.13.
- **Plan's interpretive limits apply unchanged.** The plan states that pair
  concentration, constants, ANY/GT content, size and frequency change together and that
  explanations stay hypotheses. The split and cell heterogeneity reported in §2 is
  consistent with a coverage explanation but was not pre-registered and should not be
  promoted. The plan's instruction not to repeat the widened "no GT(ADD,ADD)" absence or
  size-association claims is followed: this analysis makes neither.
- **Plan's "retention" wording.** Retention here permits a smaller learned advantage at
  long horizons; the economics curve shows none within 200 searches on this bank
  (TS/hand cumulative 1.23 [1.10, 1.37] at 200), so that caveat is not supported by the
  data at any tested horizon, though horizons beyond 200 were not computed.
- **Next action per proposal:** return to strategy. The hand prior becomes the B/C
  comparator; the B/C case for learning reduces to supplied sums, within the scope
  stated in §4 (development bank, `v2_x4`, substitution not ingredient isolation).
