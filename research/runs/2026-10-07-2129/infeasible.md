# Primary timing gate cannot admit this roster before the deadline

Stopped after implementation QA and the fixed preflight. No primary interaction
was computed, no stage-1 roster was launched, and no full queue is supplied.
This is a runtime-admission failure, not evidence about the competing scientific
explanations or proof that the search itself is too slow.

The owner deadline is 2026-10-07 22:25:38 Stockholm. The plan's work cutoff is
22:20:38, leaving five minutes for reporting and downstream review/analysis.
The preflight started at 21:53:45.153 and finished in 24.333 seconds; approximately
1,588.514 seconds (26.48 minutes) then remained to that absolute work cutoff,
before code review/build/queue startup. The preflight's own 600-second QA limit
is **not** the evidence for failure: the full absolute window also fails the gate.

Measured preflight:

| Measurement | Value |
|---|---:|
| Four-arm tables validated against saved hashes | 128 |
| Saved C1/C2 row keys, seeds, indices and budgets validated | 16,384 |
| Deterministic C1/C2 replays | 64/64 exact scientific matches |
| Replay wall / worker seconds | 5.711 / 29.218 |
| Fixed T2 timing block | 160 searches, all 32 lineages and own training cells |
| T2 timing solves | 160/160 (timing admission does not use this count) |
| Timing wall / worker seconds | 17.428 / 75.507 |
| Observed effective workers | 4.333 |
| BE T2 mean worker-seconds/search | 0.665132 |
| PA T2 mean worker-seconds/search | 0.343111 |
| Longest timing search | 17.043 seconds |
| Projected remaining full primary at observed throughput | 1,771.656 seconds = 29.53 minutes |
| Required remaining time with 1.25 safety allowance | 2,214.570 seconds = 36.91 minutes |
| Time left to absolute work cutoff at preflight end | 1,588.514 seconds = 26.48 minutes |

The projection retains all 5,120 T1 and 5,120 T2 training searches and counts
the 160 timing rows once. It combines historical T1 cost 1.042 seconds/search
with measured family-specific T2 costs and divides by observed effective
workers. Admission requires remaining > 1.25 × projection. Even an immediate
full launch would require 36.91 minutes versus 26.48 available, before repeating
validation/replay or allowing preparation overhead. Shrinking lineages/seeds,
using inspected effect sizes to select rows, or extending the owner's deadline
is not authorized.

The timing block is small and its long tail leaves workers idle. The measured
4.333 effective workers therefore need not represent a saturated full roster;
1924 achieved roughly 9.7. This probe does not establish a true 29.53-minute
primary runtime. Nevertheless, replacing its measured throughput with the
optimistic historical throughput to force admission would change the specified
gate after seeing the measurements. The roster cannot pass the implemented,
pre-stated gate in the available window.

What would work instead: the steward can authorize a fresh work window with
at least 40 minutes for primary-only work at this observed projection (plus
review/report time), then admit holdout only with sufficient measured time.
A complete training+holdout roster may need a longer allocation than the
proposal's 26–30 minutes at this probe throughput. Alternatively, approve a
longer, fixed, family/cell-balanced saturation probe and a throughput estimator
that explicitly accounts for the small-block tail, while retaining its rows
in the same 32-lineage/32-seed roster. That can test whether 1924's 9.7-worker
throughput remains attainable; no scientific sample-size redesign is required.
A new cutoff must be reviewed before use; this implementation retains today's
absolute cutoff.

QA: the initial two-lineage/two-seed smoke completed training and holdout in
34.589 seconds, with all four replay rows exact. The 16 targeted tests for the
new crossing and reused corpus/feedback invariants passed. After refining the
timing block to cover all own cells, all four new tests passed again and Ruff
passed. No Rust or search/fitting engine code changed. Smoke and preflight
produce row 0 and make no scientific claim.

Raw QA outputs (git-ignored) are in this worktree's
`experiments/output/2129-smoke-1/` and `experiments/output/2129-preflight/`.
`smoke_checks.json` preserves validation/timing/admission snapshots. Portable
inputs and their pinned source hashes are committed under
`experiments/chem_tape/data/context_increment_2129/`.
