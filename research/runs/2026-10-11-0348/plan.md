---
estimated_minutes: 70
---

Implement the approved fresh gate-sum transfer experiment without changing the
0150 tree search, initializer, extraction rule, donor mix (0.5), lexicase,
32-token cap, or eight 65,536-evaluation attempts. Expected queue wall clock
is about 70 minutes (updated from the initial 60-minute estimate after stage 0); hard queue allowances are
40 + 90 = 130 minutes. Implementation and small smoke checks precede the queue.

Bank admission is performance-blind: enumerate the planning audit's 144 roles
in ascending little-endian int64 label SHA-256 order, exclude old DG/TS exact
aliases and inactive shapes, preserve pairwise agreement strictly below 80%,
and screen every candidate against executable programs through nine tokens on
D625. Verify canonicals in the interpreter, Python and Rust. Development is
the first four admitted cells; both previously probed cells must belong to
that split, and all three unordered predicate pair splits must occur. Protected
is the first six remaining admitted cells per split (18). A mismatch with the
probe exclusion, a deficient split, or failed semantic verification stops the
design rather than changing the split. Save the full roster/exclusions and
freeze bank, split, method, artifact hashes and seed schedule before searches.

Reconstruct all 24 source libraries from 0150 acquisition rows using the exact
original rule; compare each to libraries.json, including entry hashes and
recorded random-donor seeds. Preserve failed source attempts and per-build
acquisition evaluations, worker seconds and extraction time. Rebuild R-size
using those recorded seeds. No new acquisition or target-driven filtering.

Seeds: derive a new deterministic namespace for this run, separate preparation
and protected schedules, and pair all eight attempt seeds across arms within
each job. Audit against historical acquisition/target/stage schedules, saved
replays and the two-cell probe, and save the actual schedule and audit. Protected
jobs are exactly 24 builds × 18 cells × 4 repeats × 3 arms = 5,184. Smoke and
stage-0 search only development cells; no protected timing runs. Bootstrap
uses a separately fixed reporting seed and resamples the 24 acquisition blocks
jointly across all arms, cells and acquisition costs (equal cell weights).

Preparation includes the short screen, executor checks, hash reconstruction,
eight off-path 0150 replay checks, and actual restarted stage 0 on every build
× every development cell × every arm (288 jobs), at ten workers. Report measured
sustained wall time, evaluation/worker-time costs and projected solve counts;
admit scoring only if projected full scoring wall time is at most 90 minutes.
On any measured obstruction write infeasible.md with measurements and a viable
alternative, commit code, and stop for steward redesign. During queued preparation
emit the measured gate and fail closed without authorizing protected scoring.

Measurements: capped arithmetic mean evaluations (524,288 for failed jobs),
exact D625 solve counts, worker seconds, restarts/attempt-of-solve, per-cell and
per-split costs, insertion/oversize/fallback counts and shortcut share. Primary
R-lib/R-tree ratio and 95% paired acquisition-block bootstrap interval; guard
is the 95% lower bound on solve-fraction difference > -0.03. Secondary
R-lib/R-size interval tests content beyond the matched size procedure, not
structure beyond input/ADD frequency. Save raw jobs and visualization/report
artifacts using the established harness conventions.

Decision precedence (addresses critique 4): harm (ratio lower > 1) first;
otherwise Transfers if upper < 0.90 and the reliability guard passes, even when
lower > 0.85; otherwise Small or none if lower > 0.85. A speed interval meeting
Transfers with a failed/unresolved guard is reliability-unresolved and returns
to strategy with a resolution price, rather than being called useful transfer.
All other broad intervals are unresolved. These are search-cost classifications.
For deployment separately report acquisition-plus-search costs at horizons
1, 10, 50, 100, 500 and 1,000 searches per build in evaluations and worker
seconds, and joint-bootstrap break-even estimates. When savings cross zero,
retain an unbounded/no finite repayment interval instead of dropping draws.
Do not treat the approximate 2.88 M acquisition mean as an exact constant.

Interpretation: gains across all splits support reuse across composition of
familiar parts; a gain concentrated in the learned-predicate split supports
limited reuse and contradicts the all-split expectation. R-size close to R-lib
suggests donor size/token supply; R-lib beating R-size supports content beyond
this size control but does not identify semantic modularity. Small effects or
harm stop route expansion; broad intervals or unresolved reliability require
a priced next decision. All results retain the disclosure that two development
cells were probed before freeze; protected confirmation is within a deliberately
selected new shape, not broad task transfer or an unprobed family.

Critique 1–5 are addressed above. Critique 6–8 concern digest/question wording
outside the researcher's permitted task folder: no edits to those files here;
carry these corrections to steward review. No additional mechanism arms,
extractor changes, or new-source acquisitions are authorized.

Implementation details fixed before protected scoring: stage attempt seeds are
`34,000,000 + 1,000*development_index + 32*build + attempt`; protected
attempt seeds are `34,200,000 + 1,000*protected_index + 32*build + 8*repeat + attempt`.
Small smoke reserves 34,100,000–34,100,007; bootstrap seed is 34,100,200.
Historical audit includes every published/spent 0150 namespace and both valid
and discarded probe namespaces (934,800,000 and 934,900,000 formulas). All
reused control/replay seeds are explicitly identified as validation exceptions.

The generic short-program screen also reports >=80% *short-program* near
aliases. The approved proposal's admission is **no exact solution through nine
tokens**; the <80% separation rule is between candidate cells. Accordingly the
new bank retains near-alias diagnostics but does not add an unapproved stricter
short-program admission rule. All 144 candidates survive the exact screen.
The first four survivors match the specified development roster, including both
probed cells. Development-only validation includes a 12-job small smoke and one
complete preparation/stage check; the production queue repeats preparation
without changing the method or selecting cells from those outcomes.


Measured feasibility (development only): exact screen 104.8–106.7 seconds;
all 144 candidates admitted; every canonical/witness executor check passed.
All 24 original libraries and controls reconstructed exactly; 768 source jobs
include four failures. Small smoke passed 12 restarted jobs at 2,048 per
attempt, deterministic repeats and four ordinary-engine equivalence checks.
Eight saved 0024 jobs matched in every deterministic field. Full stage 0:

| Arm | Solves / jobs | Mean evaluations | Mean worker seconds | Projected protected solves |
|---|---:|---:|---:|---:|
| R-tree | 96 / 96 | 80,920 | 6.972 | 1,728 |
| R-lib | 96 / 96 | 16,309 | 1.327 | 1,728 |
| R-size | 94 / 96 | 75,528 | 6.504 | 1,692 |

Sustained stage wall time 153.81 seconds, effective concurrency 9.239;
full scoring projection with 30% reserve plus 90 seconds is 3,689.15 seconds
(61.49 minutes), below the fixed 5,400-second gate. This is slower than the
pooled two-cell single-attempt price, which is why actual restart and all-four
cell pricing were required; the explicit approved timing gate passes. The
projected solve counts are descriptive development extrapolations, not bounds
on protected reliability. Preparation plus reserved scoring is about 67 minutes;
70 minutes is the revised expected queue wall clock. Full timeouts remain
2,400 + 5,400 = 7,800 seconds (130 minutes), unchanged from the proposal.
Evidence is in [smoke-stage/](smoke-stage/) and [smoke-small/](smoke-small/).
No protected evolutionary searches have run.
