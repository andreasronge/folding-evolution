---
estimated_minutes: 214
---

# Implementation plan, recorded before experimental execution

Implement the approved proposal without adding a stopping gate. One queue entry,
four-hour timeout, internal deadline 13,680 seconds, ten processes (9.5 effective
workers, reduced proportionally if fewer are requested). Full study is queued,
not executed by the researcher. No Rust changes are planned.

## Conditions and budgets

Pin the 1603 bank SHA, G4 hash, and the 1723 config/trajectory hashes. Reconstruct
all twenty saved token maps exactly. Search payloads contain only training cell
IDs and labels: BE's four or PA's six cells, never canonical/witness programs,
holdout cells, holdout scores, or off-family scores. Use D1331,
v2_rmin_first, population 256, length 32, 64 sampled cases, crossover 0.7,
mutation 0.03 and exact verification over all 1,331 inputs. Cost is log2
evaluations, unsolved = twice cap, including fresh scoring.

Representation: 24 bounded token multipliers m, 25 centred unit-RMS row
coordinates a, and 24 centred column coordinates b. Start b=0 reproduces the
saved token table exactly. Sparse steps change three coordinates with sigma
0.5. Context steps move b at zero residual; subsequently half move a. Redraw
unchanged context tables as b-steps. Clip elementwise a*b at +/-ln16; retain
support and integer normalization from the existing map-learning harness.
Before clipping, column mean log residual is zero and rank is one; clipping
generally breaks both properties. Record clip counts and post-clipping column
means. Centering does not fix emitted token frequencies.

Stage A uses BE9/BE10/PA9/PA10 only: two independently drawn a directions and
24 b mutants each, plus 24 token mutants per start. Each mutant gets independent
48-search A and B blocks; each parent gets independent 192-search A and B
blocks. Blocks cycle evenly through own-family cells. Total 29,184 searches at
65,536 cap. Report raw within-unit centred covariance and a 2,000-replicate
within-unit paired A/B mutant bootstrap, pooled and per family/unit. Use
max(0, raw covariance) only as Gamma's nonnegative variance plug-in; choose
n=24 or 48 by the approved formula, ties or both zero choose 24.

For each operator/unit select the six lowest-cost A effects using all 48 and
the first 24 searches. Bootstrap paired mutant records within each fixed unit,
repeat selection in each replicate, and report independent B effect relative
to the parent separately from selected-minus-all B gain. These intervals are
conditional on these starts and directions. Also report mean effects,
within-mutant per-search variance, solve fractions and seconds per search by
operator/family. Later a-steps and nonzero residuals are uncalibrated.

Stage B always follows A. Alternately admit BE1, PA1, ..., BE8, PA8, stopping
admission at the first refusal. T takes only token steps; C chooses token or
context with probability one half and has its own seeded a. Each generation
rescores two parents and six children on shared seeds within a pair, retains
the two cheapest candidates, and uses separate mutation streams by arm.
Exactly 3,840 in-loop plus 200 final searches per trajectory: 20 generations
at n=24 or 10 at n=48; final two parents each scored on 100 new seeds.

Reserve the first pair at 1.3*2*4040*slowest Stage-A group seconds/search/9.5;
later pairs at 1.3*slowest completed pair wall time. Every admission reserves
fresh scoring for all completed pairs AND the prospective pair, including
the 500-search G4 anchor. Fresh projection starts at historical 1.02 s scaled
by slowest Stage-A 65k time / 0.66 s; scale it further upward if B's measured
per-search cost is slower than A. Include 180 seconds for reporting. Do not
assume all sixteen pairs fit; fewer than six per family is outcome U.

Fresh scoring: S, T, C, C0 (C with b=0 and the same m), own-family cells only,
50 new shared seeds per cell, cap 524,288; G4 on all ten training cells.
At 16 pairs this is 16,500 searches. Fresh data never select a trajectory or
set scoring effort/admission. Preserve raw search rows and all final vectors,
integer tables, hashes, mutation records, generations and admission decisions.

## Seeds

New full-run namespaces start at 1,821,000,000: calibration searches +0,
continuation searches +1,000,000, final selection +2,000,000, fresh +3,000,000,
mutation +4,000,000, row directions +5,000,000, bootstrap +6,000,000.
Allocate each calibration candidate independent A/B intervals with at least
1,000 positions, each pair/generation independent 100-position intervals,
and independent final intervals per pair. Use the same continuation/final
inner seeds in T and C. Fresh seeds are shared across S/T/C/C0 and G4.
Smoke and timing-probe namespaces add 10,000,000 and 20,000,000 respectively.
Check these ranges against prior experiment seed definitions before execution.

## Readouts and outcome meaning

Primary: per pair mean over own cells of seed-mean log2(T_T/T_C), equal BE/PA
family weight. SE=0.5*sqrt(s_BE^2/n_BE+s_PA^2/n_PA), t df=n_BE+n_PA-2;
report exponentiated estimate/95% interval and descriptive family intervals.
Use the same family-balanced pairing for S/T (labelled T/S improvement), S/C,
C0/C (C/C0 improvement) and C0/T comparisons. Record step proposals/survivals
by token/b/a, clipping, residual/table drift, grammar-contrast cosine (only
descriptive, loaded after learning), solve fractions, evaluations/timing, and
in-loop/fresh score agreement. Produce a learning/contrast visualization.

Apply proposal rows in order:

* U: invalid hashes, leakage, pairing, missing/duplicate rows, or fewer than
  six complete pairs in either family: report infrastructure/runtime limit.
* 1: C/T lower >1: mixed procedure helps at this budget. Resolved C/C0 >1
  supports benefit under residual removal, including emitted marginal changes;
  otherwise residual attribution is unresolved. Point >=1.1 proposes frozen
  transfer next; smaller resolved increments return to strategy.
* 2: C/T upper <1.15 and T/S lower >1: bounded context increment despite
  resolved token learning. Stage A may be compatible with weak initial b-step
  signal (B), or signal that failed to accumulate (C), but a wide diagnostic
  interval leaves attribution unresolved. Selected-minus-all gain alone is
  not evidence of a step beneficial relative to the parent. D is untested.
* 3: C/T upper <1.15 and T/S lower <=1: depth versus ineffective context is
  unresolved. Say neither arm resolved learning only if C/S lower also <=1.
* 4: otherwise: unresolved primary interval; future sizing uses observed pair
  SD, without adding unapproved pairs here.

## Small-scale validation

Check representation invariants, raw negative covariance handling, paired
bootstrap reselection, exact search budgets, reserves including prospective
family cells/G4, outcome precedence, and missing-row/pairing detection.
Run a reduced end-to-end smoke with both families, both context directions,
all operators, final selection and fresh scores. Then measure a modest fixed
sample of initial token/context mutants at the approved 65k cap and fresh cap
on training cells with ten processes. These smoke/probe results do not choose
full-run parameters. If unreachable targets, severe throughput change or a
design gate makes the approved run infeasible, record measured numbers and an
alternative in infeasible.md, commit and stop for steward replanning.

Critique points 1-5 are incorporated above. Points 6-7 concern already corrected
belief files outside researcher scope; this implementation does not repeat or
edit those claims. No code_review.md or driver_feedback.md was present.
