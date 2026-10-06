---
estimated_minutes: 345
---

# Implementation plan (before experimental execution)

Implement approved proposal 1723 as one training-only queue entry, targeting ten
independent G4 starts per family. Expected queue wall time is about 5.75 hours
(updated after the diagnostic smoke; initial estimate was 325 minutes);
internal deadline 27,000 seconds, external timeout 28,800 seconds. No holdout
search or holdout seed generation occurs. Use existing composition_search.search
and map_learning initial/mutate/table_for/log_cost; no Rust change is planned.

## Frozen conditions and seeds

Freeze a byte-identical copy of 1603 bank.json from the main repository's
recorded output in experiments/chem_tape/data/four_reducer_1603_bank.json.
Verify its SHA256, D1331 labels against the current roster, and the full G4 hash
against 1603 maps.json. Copy the verified bank and provenance into RUN_DIR.
Search jobs receive only
cell ID and labels, never canonical programs or family grammar.

BE training: F?S:(M+m), F?m:(S+M), S?F:(M+m), S?M:(m+F).
PA training: (F?S:m)+M, (F?m:M)+S, (F?m:S)+M, (S?M:F)+m,
(S?m:F)+M, (S?m:M)+F. Exclude BE:S?m:(M+F), PA:(F?S:M)+m,
PA:(S?M:m)+F; assert disjoint training/holdout label vectors and reject any
job outside the training set. Keep the approved screened split and its scope.

Outer seeds: BE k uses 1723200+2k; PA k uses 1723201+2k, k=0..9.
Inner seeds: outer_seed*10000 + generation*100 + j (j=0..23).
Selection seeds: outer_seed*10000+5000+j, j=0..119, cycled across own
training cells, identical for four final parents and G4. Fresh scoring uses
1723300..1723349 on every map and all ten training cells. Descriptive
permutation seed 1723500; no holdout seed block is allocated.

24 log-multipliers, bounds +/-ln(16), minimum count 250; four parents plus
twelve children, three-coordinate N(0,0.5) mutations, 25 generations,
rescored parents, 24 searches per candidate at cap 65,536. Same cell cycling
as the reviewed learner: 6 searches/cell BE and 4/cell PA. Mean log2 cost,
unsolved cost 2*cap. Select best final parent on 120 new searches; include
G4 on those seeds for the operational early gate. Fresh cap 524,288,
population 256, length 32, crossover .7, mutation .03, 64 sampled cases.

Run pairs sequentially, each family's trajectory using the shared ten-worker
pool. This approved scheduling choice guarantees ten workers total and equal
completed n after each pair. Before admitting a pair reserve 1.3 times the
slowest completed pair (including selection), all saved/prospective maps'
fresh scoring, and reporting. Initially use the rounded diagnostic G4 projection
of 31 minutes/pair (17.8+13.1; original calibration projected 15.9+13.1).
Fresh reserve uses at least 1.88 seconds/search plus a 1.3
allowance, updated from observed per-cell rates; explicitly extrapolate
unsolved inner runs to the full cap. Record every admission calculation.
After two pairs, stop if all four selection gains are below log2(1.1),
then fresh-score all four maps and G4.

## Measurements and infrastructure

All outputs live under RUN_DIR. config.json records parameters, source SHA256,
git commit, seeds, and smoke overrides. generations.jsonl records all initial
and generation candidates, scores, selected parents, mutations and Spearman
between prior/rescored parent scores. search.jsonl records every search with
phase, actual evaluations, solve status, map hash, timing and curves.
trajectories.json records final vectors/tables/hashes, selection/G4 scores,
actual evaluations and trajectory wall time. schedule.json records reservations.
fresh_scores.json contains fresh rows only; result.json/summary.md and plots
report trajectory-level inference, crossed effects, sizing and diagnostics.

Each cell's log2 gain is the seed mean log2(T_G4/T_map), with unsolved T=cap.
Aggregate cell means equally within each training set, then use independent
trajectory units: one-sample 95% t intervals for gains; Welch 95% intervals
for crossed differences. Validate the full map/cell/seed cross product before
inference; duplicate or missing rows are unresolved. Retain per-cell summaries.
Report per-generation rank repeatability, across-map correlations of in-loop,
selection and fresh own-family gain, Euclidean distance between mean vectors
and within-family RMS spread, a descriptive permutation p (no confirmatory
test or p gate), token-wise mean differences, and runtime/evaluations.

For each of ten training cells report separate BE and PA trajectory SDs and
the equal-n contrast proxy sqrt((s_BE^2+s_PA^2)/2). Define s_off for sizing
as the median of these ten contrast proxies; retain family-specific medians
and individual cell values for the future one-BE/two-PA holdout directions.
Apply the approved candidate sizes {achieved n,14,18}, half-width
t(.975,2n-2)*s_off*sqrt(2/n) <= .50 log2. This is a training-only precision
proxy, not a guarantee or conservative bound for any particular holdout.
If 18 fails, retain achieved n and report the half-width/effect resolvable.

## Interpretation and critique dispositions

Retain separate flags for resolved improvement (lower >1) and bounded gain
(upper <1.25). For mutually exclusive labels, L takes precedence over N;
otherwise X. Similarly W takes precedence over B for crossed comparisons.
This preserves small resolved gains rather than calling them learning failure.
These are estimation readouts, with no confirmatory p-value gate.

Apply proposal rows in order: U for invalid data or <6/family except early
gate; row 1 for early stop; row 2 both N; row 3 both L and both crossed B;
row 4 both L and any crossed W/X; row 5 exactly one L; row 6 remaining.
Row 1 is an early low-yield stop with learning unresolved pending fresh
intervals. Row 2 excludes gains >=1.25 at these intervals, not all improvement.
Row 3 supports generic improvement on training cells; holdout family preference
remains untested. Row 4 supports learning with possible/resolved training-set
information, but does not establish transfer. Row 5 demonstrates improvement
in one arm only; the other remains bounded or unresolved as measured. Row 6
leaves learning unresolved against trajectory variation. Broad crossed
intervals spanning both 1 and 1.25 never establish generic transfer.
Gains on both sets suggest generic adaptation; own gain plus off-family harm
suggests specialization/damage. Even perfect scores or identical vectors
require checks for pairing, leakage, clipping, and score degeneracy.

Critique notes 1-4 are incorporated above. Notes 5-7 concern existing belief
files; researcher role forbids editing those files. Leave them for steward
review and preserve their uncertainty qualifications in this run's report.
This task implements an approved design, not a new preregistration, result
chronicle, or finding promotion; the research-rigor manual was read for mode
selection and no matching workflow is invoked.

## Small-scale verification and stop rule

First test semantic/hash/leakage invariants, objective accounting, independent
Welch inference, label precedence, fresh completeness and runtime reservations.
Then run a reduced smoke (one generation, smaller caps and seed counts) to
exercise persistence and report generation. Measure a separate real 65k-cap
batch on both G4 and first sparse perturbations across all ten cells, using
ten workers and new diagnostic seeds, without holdout searches. Compare
rates/solve fractions and projections to the approved 0.928/0.764 s calibration.
Smoke is infrastructure verification, not evidence about the research question.
If measured runtime, reachability or validation defeats the approved design,
write infeasible.md with measurements, commit and stop without a full queue.
Otherwise write and validate queue.yaml, commit all changes and leave a clean
research/2026-10-06-1723 worktree. Full learning is deferred to the driver.
