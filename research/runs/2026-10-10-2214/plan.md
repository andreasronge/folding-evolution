---
estimated_minutes: 95
---

# Pre-registration: 2026-10-10-2214

**Status:** QUEUED · 2026-10-10 · implementation commit recorded by each runner.
This implements the approved proposal and critic notes, using the required
preregistration headings. The user-required task-folder destination and no
research-file commits override the skill's default Plans/ destination/commit.
Written before any execution, including smoke tests. No target scoring in this
researcher turn. Preparation is bounded; it is not a separate exploratory probe.

## Question (one sentence)

Does frozen native A8 retain a worthwhile capped search-cost advantage over
family-blind subtree GP on the saved eight-cell DG roster, and what arithmetic
reuse horizon would repay acquisition (with TS reported separately)?

## Hypothesis

Generic expression closure and whole-subtree exchange may supply much of A8's
practical benefit over G4: expect DG tree/A8 Q near 0.5–1.5, and tree competitive
on TS. A8's acquired literal/context bias may instead remain useful beyond this
structural prior. This compares complete procedures, not a causal effect of
learning or a benefit of strong typing. Closest techniques: [Koza 1992](https://www.genetic-programming.org/gpbook1toc.html),
[Montana 1995](https://davidmontana.net/papers/stgp.pdf), lexicase; A8 is PIPE-like
external distribution fitting with fragment reuse, not a PIPE reproduction.

## Setup

- Runner: pending `experiments/chem_tape/tree_gp_run.py`; tree implementation
  `tree_gp_search.py`; report `tree_gp_report.py`. Reuse unchanged audited A8,
  G4, saved banks/builds, Rust executor and lexicase.
- Fixed population 256, two elites, 64 cases without replacement from
  `default_rng([seed,0])`, cap 524288 (2048 evaluated generations), exact D625
  check before stopping. Failed searches spend the actual cap; geometric
  ranking assigns 2× cap (and reports 1× sensitivity).
- Integer terminals uniformly X0, X1, X2, X3, ANY(INPUT), 0, 1, 2, 5. Readout
  and ANY each compile to INPUT + readout (two tokens); constants one token.
  Uniform ADD, GT, IF_GT functions, consuming integer expressions; GT returns
  integer 0/1; IF_GT children in postfix order else, then, cond, positivity
  test. ADD follows signed 64-bit wrapping. No target templates/fitted weights.
  No DUP/SWAP, malformed tapes, aliases or extra stack operations. Different
  representations/search spaces are explicitly part of the comparison.
- Initialization: ramped half-and-half, equal allocation (within one) across
  depth 2/3/4 × full/grow, shuffled; depth counts edges from root to leaf.
  Full chooses functions above the depth boundary; grow chooses terminal with
  probability 0.5 at every node. Resample oversized initialization in its same
  bin until compiled length ≤32 (bounded at 10000 draws, then validity failure).
- Child: one uniformly chosen subtree point in parent 1; crossover inserts a
  uniformly chosen parent-2 subtree and produces only this one offspring;
  mutation inserts a fresh grow subtree of maximum depth 3. Operator mixes
  0.9/0.1 and 0.5/0.5, exactly one operator per child. Oversize child reverts to
  parent 1, without retry. Only compiled length limits later depth. Log all
  rejection denominators. Initial, variation and case RNG streams separate;
  same selection engine/seeding as A8, both parents drawn for each child.
- Stage 0: source + development cells (4+4 per family), eight seeds/cell and
  both mixes: 256 full-cap-bounded tree searches. Seed
  `22140000 + 1000*(8*family_index+cell_index) + repeat` (repeat 0–7).
  Freeze lower mean log capped cost over all 16 fixed cells and eight seeds,
  2× cap failures; exact ties choose 0.9. Same frozen mix for both families.
  Never calibrate against target rows, tune after a diagnostic, or drop an arm.
- Scoring: 24 builds × two distinct fresh searches × eight fixed cells for
  each of A8 and tree (384 each/family). Each tree row is executed separately;
  its build label is a pairing/block label, not an acquired tree replicate.
  G4: 16 additional seeds/cell (128/family). Total 1792 target searches.
  Paired seeds `22150000 + 1000*(8*family_index+cell_index)+2*build+repeat`;
  G4 adds 100+ordinal (0–15). Smoke seeds use base 22160000. Disjoint from
  calibration, source acquisition and historical scoring; validate sets.
- Timeouts: preparation 1800 s, DG scoring 7200 s, TS scoring/report 5400 s;
  sum 14400 s (4 h). Ten processes, Rayon one thread. Expected queue wall
  about 95 min; preparation target ≤25 min, with 30-min hard timeout. Build
  and validation preparation ≤120 min. Failure returns to strategy.

## Baseline measurement (required)

Q = tree/native A8 geometric capped evaluations, measured contemporaneously
on the same cell/seed pairs. Native means D on DG and T on TS, all 24 builds.
G4 is a descriptive current reference; historical timings (A8 11.7/3.6 s and
G4 29/14 s on DG/TS) are planning anchors, not fresh measurements. Timing
admission uses sustained ten-worker Stage 0 batches (128 jobs/family), actual
wall throughput and worker effort including compile/variation/exact checking,
and full-cap tails. Project chosen-tree 384 jobs plus the historical native/G4
rates (16 measured full A8 replays update native rate conservatively) using the
smaller of ten workers and observed effective concurrency, and no faster than
observed batch wall throughput. Apply 30% reserve +120 s report overhead.
Each family must project ≤80% of its scoring timeout (5760/4320 s). Include
max and mean full-cap seconds, exact-check overhead and rejection rates.
If no full-cap tree tails occur, time forced full-cap search-path diagnostic
jobs on source/development inputs (never targets) and charge preparation.
DG chosen-mix solve fraction <25% is a reviewer diagnostic that blocks scoring
pending reviewer clearance; passing is not evidence of competitiveness.

## Internal-control check (required)

Run the within-bank native A8/tree contrast before any fresh-bank claim.
Validate random noncanonical trees/operators versus an independent recursive
interpreter, Python and Rust VM; compile/verify all 16 target canonicals as
validation fixtures only; validate conditional order, overflow, size rejection,
budget accounting, case pairing and deterministic replay. Replay all 16 saved
native A8 records, comparing deterministic fields only. Validate saved raw
hashes, source membership, cohort completeness and production-method hashes.

## Pre-registered outcomes (required — at least three)

Primary outcome axis is DG Q's 95% interval. Economic axis (estimated arithmetic
savings in evaluations and worker seconds separately) is independent. Every
combination below is permitted; TS/solve rates/rejections remain diagnostics.

| DG Q outcome | Positive savings, interval excludes zero | Positive point saving, interval includes zero | Nonpositive point saving |
|---|---|---|---|
| Lower >1.5: PASS worthwhile A8 search gain | Price fresh-bank comparison; report conditional repayment interval | Price fresh bank; repayment uncertain/unbounded | Price fresh bank only on search verdict; no estimated repayment |
| Upper <0.67: FAIL tree worthwhile better | Redirect learning beyond tree; geometric/arithmetic disagreement reported | Redirect; repayment uncertain/unbounded | Redirect; no estimated repayment |
| Entire interval inside [0.67,1.5]: PASS partial, bounded geometric difference | Redirect learning beyond tree; a smaller saving can still repay | Redirect; repayment uncertain/unbounded | Redirect; no estimated repayment |
| Otherwise: INCONCLUSIVE | Resolution price; conditional repayment is separate | Resolution price; repayment uncertain/unbounded | Resolution price; no estimated repayment |

No branch means equality, learning superiority, or established "never".
Both family reports exit to strategy; no automatic tuning/top-up. Scope is the
fixed development rosters only. Invalid implementation or failed timing gate
stops before targets and writes measured infeasibility. Weak/rejection-heavy GP
limits how strongly even a primary A8 win can speak about structural baselines.

## Degenerate-success guard (required)

Too-clean solving, threshold-adjacent contrasts or a weak GP arm trigger
per-cell/per-seed inspection of winners, training-perfect shortcuts, D625
verification, case indices, distinct row/seed identity, expression length,
operator/initialization rejection and phenotype diversity. Guards cover both
spurious solves (wrong order, constant/proxy behavior, copied fixtures,
target leakage) and suppressed exploration (reversion-heavy operators, broken
selection/accounting). Canonicals cannot initialize or enter search. Check all
fixtures independently; log failures and do not reinterpret a validity failure
as evidence for acquired bias. Training sampler/labels are unchanged, so the
sampler-change gate is not applicable.

## Statistical test (if comparing conditions)

Exploratory effect-size comparison, no p-values or FWER-gated paper claim:
one primary DG interval; separate descriptive TS/per-cell/G4/economic intervals.
8192 bootstrap draws, seed 2214000; resample 24 paired blocks and jointly sample
two repeats within each selected block×cell, preserving A8/tree pairing. Cells
fixed. Report block log-ratio SD and interval multiplicative width. Calibration
checks implied precision from eight seed blocks; no promise from historical
A8 SD alone. Report expected width at 24 blocks and inability to resolve Q
near the 1.5 margin; do not change n based on calibration. Bootstrap reliability
requires complete 24-block grid, finite positive costs and all 8192 finite draws;
otherwise primary INCONCLUSIVE. The CI is routing only, not mechanistic proof.

## Diagnostics to log (beyond fitness)

Pending infrastructure extensions (complete before scoring, ~90 min build):
`tree_gp_search.search` emits solved/evaluations/seconds, exact-check time,
training indices, solver, compiled-length/primitive-work totals, fitness and
phenotype-diversity curves, initialization and child rejection counts, generation
and compile/variation timings. Unchanged A8 `composition_search.search` and
`component_transfer_run.execute` directly emit costs/solves/curves/solvers and
exact overhead; runner adds tape-length/work accounting, grouping by
family×cell×arm×build×repeat. `tree_gp_run.prepare` emits calibration aggregate,
frozen mix, admission/projection/precision/replay and provenance. Proposed
`tree_gp_report.report` groups the full grid, emits Q/per-cell Q, 1× sensitivity,
tree/G4 reference, solves, worker timing and plots. Existing
`component_transfer_report.acquisition` directly supplies per-build actual
source-search effort plus intermediate/final verification/fitting/extraction;
the report uses actual expenditures for `A+N*S`, savings intervals and per-build
N*, never the artificial 2× penalty. Bootstrap paired savings with acquisition
blocks; horizons become unbounded where savings are compatible with zero.
Tree calibration is separate development cost; saved A8 acquisition is still
charged once per deployed build. Historical acquisition worker timing is labeled
historical, with hardware/load comparability limits; it is not fresh wall time.
Unresolved resolution price uses observed paired block variance and distance
to decision boundaries, with approximate cost and no guarantee of resolution.

## Scope tag (required for any summary-level claim)

Fixed DG/TS development rosters under v2_x4, 32 compiled tokens, P256,
cap524288, frozen externally fitted A8 versus closure-based subtree GP;
not strong-typing benefit, causal learning effect, fresh-bank transfer or
unlimited time-to-solve. Representation changes validity, length, primitive
work, initialization, variation and search-space coverage together.

## Decision rule

Follow the outcome grid, always return to strategy. Search-cost verdict and
repayment are separate. Critique notes 1–5 are implemented above. Notes 6–9
concern existing digest/question/analysis claims outside the researcher's
authorized task-folder writes: deferred to steward, with no edits to those
files. This run uses the corrected scoped language in its own report.

## Preparation disposition (after smoke; original plan preserved above)

STOPPED before calibration/scoring: full edge-depth4 initialization failed its
10000-draw bound. See [infeasible.md](infeasible.md) for measured rejection,
exact acceptance probability, runtime projection and explicit alternative
depth conventions for steward re-planning. No queue is prepared under this
failed initialization. The original estimated_minutes is the pre-run queue
estimate, not a claim that a full queue was executed.
