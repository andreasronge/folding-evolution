# Stop: conservative queue admission gate fails

The modifier path is implemented and small-scale smoke checks pass. Stop before
preparing or launching the substantive queue, as required by the researcher role.
This is a **cost-admission failure**, not an unreachable-target or engine failure.
The measurements do not establish that the actual roster would take 9.5 hours;
that number is the conservative envelope used by the pre-run admission rule.

Evidence: [stage-zero summary](stage0/stage0.json),
[corrected full-roster projection](stage0/projection-corrected.json),
[validation](stage0/validation.json), [progress log](stage0.log), and individual
files in `stage0/acquisition/timing/` and `stage0/timing_searches/`.
All four acquisition runs and all 80 frozen timing searches completed.
These are smoke/cost observations, not the 64-run primary experiment.

| Family / arm | Seconds | Exact episodes / 48 | Reproduction generations | Mean modifier depth | Verification seconds |
|---|---:|---:|---:|---:|---:|
| sum inherited | 69.03 | 47 | 1679 | 1637.96 | 22.01 |
| sum broken | 217.06 | 17 | 5053 | 5041.65 | 90.77 |
| max inherited | 238.57 | 7 | 5624 | 4680.57 | 87.83 |
| max broken | 229.29 | 6 | 5793 | 5780.00 | 78.13 |

Acquisition timings agree with the proposal's four-minute estimate, and modifier
exposure is substantial. Depth counts nonelite recipient-copy generations;
elites retain depth. Four timings cannot estimate between-run variation reliably.

Frozen timing used four distinct seeds per target/vector: uniform, scaffold,
matched fit, and both timing-run extractions. Each search was capped at 262144
population evaluations. Solves and times below pool these five different vectors;
per-vector data are in the individual files and cannot be read as one arm's rate.

| Target | Exact searches / 20 | Mean seconds | Maximum seconds | Total verifier seconds |
|---|---:|---:|---:|---:|
| sum1 | 20 | 3.13 | 12.89 | 18.30 |
| sum5 | 19 | 2.25 | 8.66 | 0.74 |
| max1 | 11 | 16.53 | 170.63 | 224.13 |
| max5 | 9 | 6.50 | 11.20 | 0.52 |

All four target labels, planted exact solvers on the entire 10000-input domain,
modifier support/normalization, distinct-row recipient/elite bookkeeping, broken
shuffle ordering (including generation-zero solves), and unchanged resident-tape
execution pass. Sigma-zero identical-row replay passes on 20 small-search seeds.
Relevant regression and mechanism tests: **151 passed**; Ruff and git diff checks pass.
No Rust changes or rebuild are needed.

## Gate and its limitation

The operational conservative rule prices acquisition as twice the slower arm
within each family, charging four ten-worker batches for its 32 runs. It prices
scoring as twice the worst observed search for each target, charging 71 batches
for its 704 searches. The exact fixed roster is 2048 learned-vector searches plus
768 reference searches = **2816**, rather than the proposal's approximate 2600.
Stage zero is conservatively charged serially, plus five minutes overhead.

Correct projection: acquisition **60.75 min**, scoring **481.35 min**, stage zero
**22.03 min**, overhead **5 min**: **569.13 min**, above both the proposal's
210-minute timeout ceiling and the repository's eight-hour ceiling. The max1
uniform timing tail (170.63 s) drives this envelope. Its magnitude is broadly
consistent with the proposal's known approximately 150-second tails; extrapolating
that tail to every scoring batch makes admission stringent. This is insufficient
support for admitting the fixed roster under this rule, not proof of actual
nine-hour execution or failure to acquire useful bias.

`stage0.json` was produced by a process loaded before a planning-count correction:
it priced 608 rather than 704 searches per target. Its original projection was
also infeasible (501.34 min). Keep that raw summary intact; use
`projection-corrected.json` for the corrected calculation with the exact approved
roster. No measured search outcomes or acquisition parameters changed.

## What would work instead (requires steward re-plan)

Retain the scientific roster and consider an explicitly revised, stratified cost
admission rule, or separate reviewed acquisition and scoring stages. Using the
measured means with the actual per-vector roster weights gives about **20.11 min
acquisition + 34.14 min scoring** on ten workers. Doubling that point estimate,
then adding the conservative stage-zero charge and overhead, gives **135.53 min**,
inside the proposal ceiling. This is a plausible pricing alternative, not a
validated tail guarantee: one acquisition per arm/family and four scoring seeds
per vector give little tail information. The steward should choose whether a
bounded timing extension, staged review, or a revised cost envelope is warranted;
the researcher has not silently switched gates or reduced the roster.

The program–modifier contrast bundles initialization and ongoing variation under
resets. The frozen max targets have substantial censoring in these timings; the
full comparison would still need capped costs, solve counts, per-family results,
and crossed acquisition/seed uncertainty. No scientific decision is made here.

## Implementation available for a revised plan

`experiments/chem_tape/inherited_bias.py` supplies validation, smoke, stage-zero
cost checks, the fixed acquisition roster, frozen scoring, crossed bootstrap,
Price covariances, lineage-depth logging, trajectories and reference break-even
costs. Minimal TAG engine changes add a per-recipient modifier callback and per-row
op sampling; the legacy fixed-vector path retains exact RNG replay. The old
threshold-2 label closure and diagnostic comparator are generalized.

The substantive queue was **not written or launched** because the admission gate
failed. Research task files remain in the main checkout's task folder and are not
committed on the worktree branch. Smoke artifacts were produced during implementation
from a dirty worktree; their manifest's original HEAD is not the completed code
commit. Changes after timing began correct roster pricing and enrich analysis/
provenance logging; they do not change the measured acquisition or scoring law.

Implementation commit: `25f929e1f162756fbffc56b8a1d3e8a06cce00fc` on
`research/2026-10-07-2243`. Worktree status is clean; the commit contains only
experiment code, engine changes and tests, with no research/ files.
