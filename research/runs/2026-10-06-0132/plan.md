---
estimated_minutes: 405
---

# Implementation plan frozen before experiment execution

Implement the approved G-refinement experiment on the eight retained PA cells from
0001's D1331 bank. Six training cells and the two withheld M/S compositions are
frozen from that artifact's roster and `split_shape`, with canonical programs used
only for full-domain evaluator validation. Reuse composition_search.search unchanged
(P=256, 32 alleles, R=23000, v2_rmin, 64 lexicase cases, crossover .7,
allele mutation .03). Save source artifact SHA256 and decoder hashes.

C starts at G and varies 552 row/token log-weights; M starts at G and varies
23 global log multipliers; T starts at G-marg and varies 23 tied log-weights.
Use four parents plus twelve children, rescore all sixteen on fresh shared
six-cell/four-seed sets each generation, choose the four lowest mean log2 costs
(stable index tie break), run 25 generations, and select among final parents on
six cells/twenty separate seeds. Each mutation chooses three distinct coordinates
uniformly, adds independent N(0,.5), then clips each coordinate within log(16)
of its initial value. Normalization is frozen: proportional row probabilities
with lower-bound water filling at 250/23000, then largest-remainder integer
allocation (stable token-index ties). No post-hoc normalization tuning. M applies
multipliers before row normalization. Save every candidate's parameters, table,
score, L1 probability drift, mutation/table-change diagnostics, cumulative
inner evaluations and wall time. Six matched trajectories of each learner.

Seed namespaces (all distinct from 0001, 2247 and steward probes): 132000000
stage-0; 132100000 + k*10000 + generation*100 + seed-index for learning;
132200000 + k*1000 + seed-index for final-parent selection; 132300000 +
seed-index for fresh tests (same seeds across cells/maps); 132400000 + k*10
for C-marg measurement and independent validation; 132500000 for sampling,
with unique map/chunk offsets; 132600000 + learner-index*100 + k for mutation
streams; 132700000 for bootstrap. k is zero-based. Smoke uses 133000000+
separately. Stage-0 calibration trajectories use their own mutation and seed
streams and are discarded; the main learning budget starts afresh.

Stage 0 times two complete generations for each arm separately, two independent
120-run G repeatability sets, and representative 524288-cap PA training and
holdout searches for C/M/T starting tables, G-marg, U and F. Record how often
three-coordinate mutations change the integer table and their paired score
variability. Project arm-specific learning, selection and full stage-2 costs
with 15% timing headroom and reserve analysis time. Full stage 2 is 26 maps x
500 searches = 13000 searches, plus U/F's 400 holdout searches; T and C-marg
are slow arms. Time marginal construction and optional exact sampling too.
Two G costs differing by >.6 log2 stop the run as a harness mismatch. If total
projected time exceeds seven hours, first remove optional sampling, then use
four T trajectories, then twenty generations for all learners; stop as
infeasible if still over seven hours. Fix the resulting schedule in a saved
stage-0 decision before learning; holdout values never enter this decision.

Run trajectories C1/M1/T1/C2/...; evaluate each finished selected map immediately
on six training cells x 50 seeds and two holdouts x 100 seeds, cap 524288.
Construct and validate each C-marg with 312500 genotypes independently for
measurement/check, using 0001's abs-error <= max(.02*p,.0005) rule, and score
it on the identical tests. Evaluate G/G-marg on both sets and U/F on holdouts.
Reserve evaluation time before starting each trajectory; stop rather than begin
one that cannot finish learning and evaluation. An interrupted fixed schedule
is an incomplete study with explicit missing IDs and no planned-study outcome
classification. Sampling comes last: 1e8 genotypes per C and M table on all
eight PA targets, descriptive sparse counts with exact full-domain checks.

Report fresh-training costs at both 65536 and 524288 (the former derived by
censoring the longer searches); unsolved costs are 17 and 20 respectively.
Primary ratios are 2 raised to the mean paired log-cost difference, not an
arithmetic average of per-trajectory speed ratios. Use 10000 two-level bootstrap
resamples: matched trajectory indices jointly across C/M/T (each C-marg follows
its C), and shared seed indices jointly across every map/control/cell. For the
approved four-T fallback, use matched first-four blocks for T contrasts and
all six blocks for contrasts without T; never independently replicate frozen
control observations for each trajectory. Faster means lower bound >1;
otherwise upper bound <1.5 means no practical gain; else unresolved.

Outcome rules (critic refinements, ordered):
1. Fresh-training C/G at the approved 524k test cap is unresolved: unresolved
learning; no transfer conclusion. If no practical gain: no practical training
gain at the larger test cap, not zero gain and not a rejection
of contextual learning. Also report the 65k training contrast; a faster 65k
contrast followed by no larger-cap gain is an objective/cap discrepancy.
2. C faster on fresh training, but no practical C/G gain on both holdouts:
no >=1.5x holdout gain supported within interval resolution; compatible with
limited transfer/overfitting, not proof of overfitting.
3. C faster than G and M on both holdouts: learned contextual preferences
transfer within this screened family beyond G token retuning.
4. C faster than G on both holdouts, with no practical C/M advantage on both:
bound C's incremental gain over M at this budget. Report M/G before asserting
M transfers; do not assert equality or contextual preferences unnecessary.
5. All remaining mixed/broad contrasts: unresolved. Report intervals and
between-trajectory spread with approximate trajectory counts for resolution.

Every outcome includes C/C-marg, T/G-marg, M/G, training/holdout gaps,
learning/drift curves, integer mutation-change rates, score variability,
adaptation cost separate from test cost, and sampled solver rates if complete.
No outcome establishes mechanism, family specificity, or performance of a
better optimizer. The screened bank is reused, not an untouched benchmark.

Critique 1-5 are implemented above. The reviewed old holdout KM medians are
G=13568/18688 and U=83968/148480; proposal medians are not used for inference
or runtime gates. Critique 6-9 concern notebook belief files outside the
researcher's write scope; leave them for the steward rather than edit those
files. No code_review.md or driver_feedback.md was present on initial read.

Before queue creation, run deterministic normalization/seed/bootstrap/deadline
checks and a separate small end-to-end smoke through learning, marginal
validation, evaluation, sampling and report. If measured rates or gates make
the approved design infeasible, write infeasible.md with measurements, commit,
and stop. Queue timeout is 28800 seconds with internal deadline 27600 seconds;
all runtime outputs go under RUN_DIR. Keep a copy of these task artifacts in
this worktree for the task-branch commit, and mirror authored notes/queue back
to the driver's task folder.

Implementation clarification before reading smoke results: the approved 524k
fresh-training contrast remains the outcome-rule gate; the derived 65k
contrast diagnoses learning of the selected objective separately.

Smoke timing update (no design change): with one generation per arm and one
seed/cell, the training rates were C=.754, M=.544, T=1.540 seconds/search;
representative full-cap PA tests plus one-thread worker sampling gave a
395-minute full-budget projection, including 15% headroom but only the
short smoke calibration. Allow about ten more minutes for full stage 0,
hence the revised expected queue time of 405 minutes. The full queue repeats
calibration at its approved sizes and freezes its own timing-only decision.
