---
estimated_minutes: 380
---

# Implementation plan, written before experimental execution

Implement the approved [proposal](proposal.md), with [critique](critique.md)
notes 1–5 applied as follows. No holdout, off-family, or sampling observations
choose operators, maps, generations, or stopping. Notes 6–11 concern the digest
and question ledger: those files are outside the researcher's permitted write
scope and are left for the steward. This implements an approved design rather
than opening a new preregistration or promoting a finding.

## Conditions and fixed resources

Reuse the 0132 PA bank, production `composition_search.search`, frozen G, and
all six saved M vectors/tables. Vendor the starting maps and the eight retained
non-PA cells from 0001 with source paths and content hashes. Verify canonical
program labels and that an R vector with zero residuals exactly reconstructs
every saved M table. Parameters: D1331, population 256, 32 alleles, 23,000
allele range, v2_rmin, 64 lexicase cases, crossover .7, mutation .03, exact
verification on 1,331 inputs. Learning cap 65,536; test cap 524,288.

M+ continues the 23 multipliers on G, mutating three coordinates with N(0,.5).
R has those multipliers plus 24×23 residuals initially zero; half of children
use the same multiplier operator, half mutate one uniformly selected complete
row with sigma .5 or 1 chosen equiprobably. Each coordinate is bounded by
±log(16), independently of the inherited value. Reuse lower-bound water
filling (250 counts per token) and stable integer normalization. R_abl removes
residuals from the final selected R vector; it receives no additional learning.

Run twelve matched pairs, ordered 1a…6a,1b…6b, M+ then R. Both trajectories
have (4+12) selection for 35 generations, four shared seeds per training cell
per generation, and final parent selection on twenty separate seeds per cell.
Test each completed pair immediately before admitting the next pair, reserving
time for its M+, R and R_abl tests. Do not classify an incomplete planned study
as a full twelve-pair result; report coverage and observed precision instead.

## Seeds

Use disjoint integer namespaces: harness 811200000; calibration search
811300000 (start index ×100); timing 811400000; learning 812000000 (pair index
×10000 + generation ×100); final selection 813000000 (pair index ×1000);
PA tests 814000000; non-PA tests 815000000; sampling 816000000; mutation
817000000 (pair index ×100 + arm index); bootstrap 818000000. Calibration
mutation uses 817100000 + start index. Smoke adds 10,000,000 throughout.
These avoid 0001, 0132 and steward probe namespaces. Within each phase shared
seed indices are used jointly across cells/maps; generation and selection seeds
are shared within a pair. Mutation streams are distinct. Log all actual seeds.
The implementation-time calibration-only verification adds 20,000,000 to
these namespaces, keeping its measured feasibility observations separate from
the full queue's Stage 0. Smoke adds 10,000,000 as above. Verification never
runs the substantive learning study or chooses a map using test scores.

## Gates, timing, and measurements

First smoke at reduced seeds/generations/sample count without interpreting its
gate. Stage 0 of the full queue scores G on 6×20 fresh searches at 65k; a mean
more than .6 from 13.84 is a harness mismatch and stops interpretation entirely.
Calibrate sixteen actual R row children and sixteen M children per inherited
map, each paired with its parent on 6×4 training searches. Subtract estimated
paired sampling variance from the across-child variance of mean effects; clamp
negative variance to zero. Treat cells as fixed strata when estimating the
sampling variance. Save all signed child effects, beneficial fractions, solve
counts, and a start-cluster/within-start-child bootstrap diagnostic interval.
Shared parent noise makes this an approximate variation diagnostic, not proof
of beneficial signal. If pooled R row spread is below .15, run frozen-reference
stage 1 and frozen-M-only stage 5, and report row 0 (variation not established
by this calibration). This is the proposal's approved gate, not redesign.

Measure throughput including pool overhead on calibration and representative
G/M/R/R_abl training and 524k training/holdout/non-PA searches. Use only training
tasks for stage-0 timing; extend their measured per-map costs conservatively
to scheduled holdout work without inspecting holdouts. The slow R and ablation
tables must be represented. Prior M solved 1753/1800 by 65k, 1799/1800 training
and 1194/1200 holdouts by 524k; G holdouts 194/200, difficult BE 42/50. These
are assumptions to check, not guarantees for learned R or ablation tables.
Project elapsed stage 0 plus remaining work with 10% headroom applied once,
including report time. Freeze the timing-only schedule before stage 1/learning.
If over 7 h, remove sampling, then learned off-family stage 4, then shorten all
trajectories from 35 to 28 generations. If still over, stop as infeasible with
measurements. Internal deadline is 7 h 40 min; queue timeout 8 h.

Stage 1: G and six M starts on PA training 6×50, holdouts 2×200,
and non-PA 8×50. Stage 2 tests all twelve pairs' M+, R, R_abl on identical
fresh PA seeds. Stage 4 tests only the a continuation's M+ and R (12 maps) on
8×50 non-PA searches. Stage 5 samples 10^8 genotypes each for six inherited M
and twelve stage-4 maps, even if off-family tests were dropped; reuse G's
0001 rates. If the contextual gate fails there are only six frozen M maps to
sample. Sparse hits are descriptive estimates/bounds, zero is not absence.

All outputs go under RUN_DIR: config/source hashes, copied banks and starts,
stage0 diagnostics and frozen schedule, raw search and generation JSONL,
selected vectors/tables, sampling counts and intervals, status, report JSON,
summary, and curves. Record adaptation evaluations/time separately from tests;
log per-map/cell solve counts, 65k/524k capped costs, L1 table drift, multiplier
and residual contributions, changed rows, and across-continuation directions.

## Precision and outcome meanings

Effect A/B = 2^(mean cost_B − mean cost_A), so greater than one means A is
faster. Report 95% percentile intervals from 10,000 two-level bootstrap draws:
six inherited starts with all their available continuations, then shared seed
indices jointly across maps and fixed task strata. Classify faster if lower
bound >1; otherwise no practical gain if upper bound <1.25; otherwise unresolved.
Also report whether the lower bound exceeds 1.25 and whether the point effect
reaches 1.25. A resolved smaller gain is still "faster" under the approved rule.

Conservative sensitivity: for six start clusters, sd .30 log2 of the start-mean
contrast and a retained shared-seed term .13 give SE=sqrt(.30²/6+.13²)=.179,
normal 95% half-width .350 log2 (factor 1.27). If the seed term is .08 the
factor is 1.22; if cluster sd is .20 and seed term .08 it is 1.17. Thus the
optimistic twelve-independent-pair sketch is not assumed: with .13 seed noise
even unlimited starts give factor 1.19. The approved size can resolve 1.25 in
the latter regimes and resolved improvements in others, but cannot guarantee
a null will be bounded. Keep all twelve pairs/200 holdout seeds: uncertainty
about the conservative parameters does not establish infeasibility. Report
actual start-cluster and seed components. Follow-up sizing separates more
continuations (within-start noise), more independent starts (cluster noise),
and more seeds (shared test noise); never count twelve pairs as twelve starts.

Apply the proposal's first-match rows, with these narrower interpretations:

| Row | Condition | Meaning |
|---|---|---|
| 0 | Calibration spread <.15, or harness mismatch | Calibration did not establish usable row variation; frozen checks remain descriptive. A harness mismatch stops all interpretation. |
| 1 | R/M+ faster on both holdouts | Allowing contextual moves improves this learning procedure's transfer in the screened PA family. An unresolved R/R_abl leaves residual contribution unresolved; ablation is a dependency check, not unique contextual causation. |
| 2 | R/M+ faster on fresh training, no practical gain on both holdouts | Training improves; holdout gains are bounded below 1.25, not proven absent. Investigate generalization. |
| 3 | R/M+ no practical gain on training and both holdouts | At this budget/operator, no resolved gain ≥1.25 from allowing row moves. R/R_abl faster indicates useful residual dependence with token-step displacement; otherwise report no resolved residual benefit, explicitly distinguishing bounded-small from unresolved. |
| 4 | Everything else | Unresolved; report every interval, cluster spread, coverage, and sensitivity for a follow-up rather than asserting equality or optimization failure. |

Always report M+/M and R/M, training-to-holdout log-gain shrinkage per arm,
learning curves, adaptation cost and map changes. Off-family M/G is descriptive
with BE and linear separate: BE upper bound <1.25 bounds gains of that size,
not all extension; floor-limited linear cells and two BE tasks cannot establish
family specificity. Supply and variation change together, so no mechanism
claim is available. Digest wording corrections in notes 6–11 are recorded for
the steward; no evidence-ledger changes are made by this implementation.

## Verification and handoff

Check exact inherited reconstruction, coordinate bounds, deterministic operator
behavior, paired seed schedules, gate routing, priority cuts, cluster-preserving
bootstrap, completeness handling, and queue loading. Smoke the complete pipeline
with the real backend at small scale, storing observations in this task folder.
If measured assumptions make the approved design impossible, write infeasible.md,
commit, and stop for steward redesign. Otherwise write one eight-hour queue entry
with id prefix 2026-10-06-0811-, commit implementation and task artifacts on
research/2026-10-06-0811, and verify a clean worktree. Do not run the full queue.
