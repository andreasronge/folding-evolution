---
estimated_minutes: 145
---

Implement the approved training-cell acquisition test; preparation stops after 120 minutes.
Queue wall time is provisionally 120 minutes (4-hour outer timeout); replace this estimate
with the smoke projection, including archive D1331 execution, serialization, fitting and
reporting. A measured projection above 210 minutes or any construction obstacle ends this
implementation with infeasible.md rather than a resized design.

Conditions: comparison-gate-v1, D1331, v2_rmin_first, P256, tape32, unchanged G4,
operators and exact checks. Eight independently acquired corpora per BE/PA family,
four own training cells each, 32 source searches per cell. Sources stop at their first
exact solve or 65,536 evaluations. Archive checkpoints are evaluated populations
64/128/256 (16,384/32,768/65,536 evaluations). Exact checks happen first: no archive
from a solve generation, and no descendants of solvers. At nonterminal checkpoints use
the 508 actual lexicase parent slots; at the cap copy the selection RNG state and draw
508 terminal parent slots without advancing search. Sample eight slots with replacement
for S and eight population indices with replacement for P, from the same evaluated
population. A separate seed-derived archive RNG performs both samples. Independently
execute every archived tape on D1331, logging exact exclusion, training-perfect status,
and accuracy. Preserve source attempts even if they archive nothing; empty cells fail.

All archived rows within a contributing source have equal weight (hence equal checkpoints
when all contribute eight tapes), then each contributing source has equal weight within
its cell. Each cell's full-tape transition counts rescale to 1,600; reuse the frozen
alpha50 C estimator and bounded G4 token-multiplier T estimator. Explicit partial-tape
counts must never masquerade as solved solver rows. Fit C_S/T_S to identical S counts,
C_P to P counts. Load C_exact from hash-verified 1246 family/index frozen artifacts.
K may be calculated by the existing estimator but is not scored.

Confirmation seed base 202610081831; existing seed_for formula with phase0 collection,
phase1 paired scoring, corpus indices0..7, cell indices0..3, source indices0..31,
score indices0..15. Smoke uses base+100,000,000, one corpus per family, smaller source
and fresh-search counts, retaining intended population/checkpoint/scoring caps and ten
workers. Smoke rows are excluded from confirmation. Freeze schedule before execution.
Five arms C_S,T_S,C_P,C_exact,G4 share each fresh seed; 2,048 source and 5,120 scoring
searches. Process fixed blocks BE1/PA1 through BE8/PA8, collect and freeze both before
score. Only the largest fully completed balanced prefix is inferential; at least six
pairs (12 corpora) required. Errors cannot become timeout prefixes.

Smoke checks: instrumented/uninstrumented replay excluding timings; deterministic archive
hashes; terminal population identity; checkpoints/exact exclusion with controlled cases;
independent D1331 validation; source weights; hash-checked exact controls; training-only
job payloads; five-arm pairing; complete-prefix reporting. Measure worker/wall rates,
archive verification and serialization, fit and report overhead, and partial-arm solve
rates. Project full count at measured ten-worker throughput, price uncertainty and capped
partial arms; retain the 210-minute feasibility gate.

Primary: exp(mean_corpus(mean_cell_seed(log(cost_T_S)-log(cost_C_S)))), equal BE/PA
weight; 95% t interval across independent corpora, unsolved cost2*524288. Compute
C_S/G4 likewise. Upper C_S/T_S bound<1.20 takes precedence: no worthwhile signal
resolved for this collector, no feedback funding. Otherwise both lower bounds>1 imply
useful partial-context fitting with a worthwhile effect still plausible, not an established
1.20x improvement. Resolved C/T with C/G4 crossing1 leaves usefulness unresolved;
resolved C/T without resolved C/G4 is only a relative fitting advantage. An interval
spanning1 and1.20 is unresolved: price additional independent corpora using observed SD.
Almost universal caps are uninformative about relative search behaviour: show solve rates,
1*cap sensitivity and both-solved sensitivity before interpreting the cost endpoint.

Secondary/descriptive: C_S/C_P tests extra checkpoint parent enrichment (P has already
undergone evolution); C_S/C_exact compares performance at unequal acquisition budgets,
not whether exact solvers add nothing. Also T_S/G4, per-family intervals, 1*cap,
both-solved pairs, duplicate rate, effective contributing sources, share of archive from
sources later solving, training-perfect share, D1331 accuracy and row entropy. Scope is
training-cell reuse on a development bank, a C/T fitting-procedure contrast, not isolated
order, inheritance or fresh-bank transfer.

Critique disposition: notes1–5 incorporated above, including corrected historical collection
estimate (~12 minutes, not2). Notes6–7 concern digest/question wording outside the
researcher's authorized task-folder scope; leave those files unchanged and flag them for
steward correction (1.38x is a C/T ratio-of-ratios; “No holdout had been searched when
the roster was frozen”). Alternative saved-K scoring does not test this acquisition question
and remains deferred under the approved strategy.


Measured feasibility (final smoke): [smoke.md](smoke.md), raw [outputs](smoke-final/result.json).
The complete ten-worker smoke projects 143.94 minutes (collection9.25, scoring132.60,
fitting0.09, startup/report reserve2.00), passing the pre-stated mean-projection210-minute
gate. The all-three-partial-arms-capped sensitivity is210.33 minutes; it is a conservative
scenario, not the observed solve-rate projection, and remains within the240-minute queue
timeout. Small-smoke fitted-arm rates remain uncertain; do not infer efficacy or corpus
variance from two smoke corpora. Confirmation size stays exactly as approved.
The confirmation schedule is separately frozen in confirmation_schedule.json; the runner
reconstructs that same deterministic schedule before confirmation work. Digest/question
wording corrections in critique notes6–7 remain for the steward.
