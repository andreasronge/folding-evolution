---
estimated_minutes: 80
---
# Pre-registration: 0024 restarted tree versus A8

**Status:** QUEUED · target commit `1773d11` · 2026-10-11. This plan preceded all new experimental execution. The approved proposal fixes the design; no cutoff sweep or sample expansion is authorized.

## Question (one sentence)

Does restarted generic tree GP remove restarted A8's arithmetic evaluation saving while meeting a three-percentage-point reliability noninferiority criterion on the fixed DG roster?

## Hypothesis

Repeated independent discovery could remove the residual DG saving attributed to externally fitted A8. Conversely, build-specific acquired bias could retain lower cost or better reliability under the same schedule. The pooled historical projection R≈0.78 and 98–99% solving is provisional: pooling by build gives A8 approximately 123,714 evaluations and 96.44% solving instead of 110,563 and 98.68%. Neither estimates cell×build interactions well. The stated 90% resolution probability is not a validated power guarantee. Four scoring repeats increase within-build precision, not the number of acquisition replicates (24). A8 solving below 95% would warrant fixed-build heterogeneity inspection, not establish dependent restarts.

## Setup

- **Sweep file:** this folder's `queue.yaml`, preparation/DG/TS timeouts 1800/5400/1800 s (2.5 hours summed).
- **Conditions:** R-tree and R-A8: at most eight attempts of 65,536 evaluations, stopping at first D625-exact solve; total cap 524,288. F-A8: one unchanged full-cap search. Frozen mix 0.5, 32-token limit, P256, 64 training cases, unchanged native A8 builds and search engines at c32ff04. Each restart refreshes population, verifier cache, cases and search RNG, retaining the A8 build.
- **Counts:** eight cells per family, 24 builds, four paired repeats: 96 jobs/cell, 768/family/arm for R-tree and R-A8. F-A8 has two repeats: 48/cell, 384/family. Complete scheduled jobs are the units; attempts are never independent replications in analysis. Both DG and TS are retained, reported separately.
- **Production seeds:** restarted attempt k (0..7): `22300000 + 1000*(8*f+c) + 8*(4*b+r) + k`; F-A8: `22320000 + 1000*(8*f+c) + 2*b+r`. Only paired restarted arms intentionally share these seeds.
- **Stage 0:** 64 sustained DG jobs per restarted arm, on eight source/development cells × eight builds, with attempt seed `22340000 + 1000*c + 8*b+k`, intentionally paired across arms. Separate small validation searches use `22350000 + 1000*f + 8*r+k` (two repeats per family, development cells, small caps); semantic validation seed 22352000. The sixteen historical A8 replays intentionally reuse their original replay seeds. Publish actual schedules and unique seed sets; audit against every 2214/2239/2254 calibration, scoring (including refused old 22150000 formula), smoke, forced-tail, acquisition and replay seed. Statistical RNG seeds 2230024 (bootstrap) and 2230025 (historical sensitivity) are not search seeds.
- **Cost:** expected queue 80 min including margin; bounded implementation/smoke ≤120 min. Ten processes, one Rayon thread each. Preparation reruns all sixteen saved native replays, semantic checks, deterministic first-attempt equivalence for both methods, then 64 sustained DG jobs per restarted arm. Reject a projected DG wall above 75 min. Project all fresh DG jobs including F-A8 and measured initialization/verification/reset overhead; report assumptions about concurrency. Smoke checks use development cells, never target scoring.

## Baseline measurement (required)

Primary baseline is contemporaneous R-A8 on exactly the same seeds, cells and builds. Ratios compare arithmetic actual evaluations, failures charged their actual total cap. F-A8 is a contemporaneous secondary schedule reference. Saved 2254 full-cap tree rows provide a labelled historical reference, never replicated under new build labels. Historical timings are planning anchors only (tree DG 107 µs/eval, A8 66; effective concurrency 9.1).

## Internal-control check (required)

Yes: restart both representations with the identical schedule. R-A8 versus F-A8 separates a schedule contrast within A8 descriptively. Restarting bundles population/case/cache/RNG renewal; it does not isolate reset, bloat or learned-map causality. The calibration-selected tree mix was frozen before target scoring. One inspected shorter cutoff favored tree more; this does not establish neutrality or optimality of the chosen cutoff.

## Pre-registered outcomes (required — at least three)

R is mean R-tree evaluations divided by mean R-A8 evaluations, equally weighting cells. D is solve-fraction R-tree minus R-A8. Both have paired 24-build block bootstrap 95% intervals. Reliability holds only if D lower >−0.03. A guard that does not pass is not demonstrated inferiority unless its upper <−0.03.

| Evaluation interval | D lower >−0.03 | D lower ≤−0.03 (unresolved or inferior) |
|---|---|---|
| R upper <1 | PASS: no A8 evaluation saving on this roster/schedule within this reliability margin; use R-tree as evaluation comparator | PARTIAL: cheaper expenditure without established reliability noninferiority; report unresolved/inferior distinction |
| R lower >1 | FAIL of generic-saving hypothesis: A8 retains evaluation saving; report A+N*S and reliability together | FAIL of generic-saving hypothesis: A8 retains evaluation saving; repayment does not alone establish efficiency superiority; report reliability |
| Otherwise | INCONCLUSIVE on cost; reliability bounded within margin only | INCONCLUSIVE on cost and/or reliability; no equality claim |

All six cells return to strategy after reporting. A seconds loss alongside an evaluation win leaves purchasing dependent on the owner's cost objective. No automatic follow-up, cutoff tuning or larger n. An invalid implementation, failed audit/replay or timing gate stops scoring, produces `infeasible.md`, commits code and exits to steward.

## Degenerate-success guard (required)

Too-clean outcomes (perfect solving, identical primary rows, implausibly few attempts) and near-boundary outcomes require per-cell/build/job inspection of attempt seeds, renewed training indices, exact solvers, accumulated costs and winner programs. Artifacts to rule out: overlapping seeds, recycled population/cache/cases, missing unsuccessful attempts, target fixture injection, constant/proxy solutions and operator-accounting errors. Independent D625 verification plus provenance/accounting checks detect spurious success; rejection/diversity diagnostics detect suppressed exploration. Canonicals are validation-only. Training distribution and label function remain unchanged; sampler-change gate does not apply.

## Statistical test (if comparing conditions)

Exploratory effect-size intervals, zero confirmatory p-value tests; no FWER paper claim. DG has one primary ratio interval with a paired reliability guard; TS and secondary contrasts are descriptive. 8,192 draws resample the 24 paired build blocks, keeping all eight cells and scoring repeats within each block; identical draws serve cost and reliability. No extra repeat resampling in the primary specified block bootstrap. Require a complete grid, finite positive costs and all finite draws, otherwise INCONCLUSIVE/invalid. Routing uses CI treatment (b); it does not diagnose a mechanism.

Historical sensitivity (pending report extension, ~30 min): pool by cell, by build, and by cell×build using 2254 capped first-hit rows; retain fixed A8 builds across eight attempts. Simulate the fixed 768-job design with 256 simulated datasets and 512 paired build draws each, reporting cost-resolution and reliability-pass frequencies, assumptions and worker price. Two observations/cell×build make this sensitivity unstable, not a power proof or admission criterion. No scoring-size change follows.

## Diagnostics to log (beyond fitness)

Pending narrow wrapper/report extensions (~90 min, complete before full queue): `restart_gp_run.execute` emits full per-attempt records, aggregate actual evaluations/worker seconds/attempt count/first solver and overhead in `search.jsonl`; `validate_rows` groups family×cell×arm×build×repeat and validates every attempt. Unchanged `tree_gp_run.execute` emits training indices, fitness/diversity curves, operator/rejection/length/work and exact-check timings. `restart_gp_report.report` groups both the complete family grid and per-cell table, emits primary intervals, solves, evaluation/seconds contrasts, geometric failures-at-2×cap sensitivity, attempts and solve-cost curves, labelled 2254 historical reference, and plots. Reused `component_transfer_report.acquisition` produces historical per-build total acquisition evaluations/seconds including failed sources, fitting and extraction. Report A+N*S curves with paired build uncertainty in both units; historical acquisition seconds are explicitly historical. Repayment is unbounded if savings admit zero or negative values. Approximate resolution price uses observed block variance and distance to both cost/reliability boundaries, never promises resolution. Acquisition is once per deployed build, development effort separate.

## Scope tag (required for any summary-level claim)

Fixed eight-cell DG and TS development rosters, saved 1717 builds, frozen v2_x4 methods, P256, 32 tokens, cutoff65,536/cap524,288. No transfer, optimal-policy, equal-reliability, independent-attempt or learning-is-useless claim. Historical 2254 arithmetic saving is distinct from its geometric result excluding a ≥1.5× advantage under failures-at-2×cap.

## Decision rule

Apply the outcome grid, report both cost units and reliability, and return to strategy. Quantify the price of unresolved boundaries without automatic top-up. Literature motivation is the known fixed-cutoff restart technique, not a new mechanism.

Critique disposition: notes 1–5 are implemented above without changing arms/counts/cutoff. Notes 6–9 concern digest/question claims outside authorized task-folder writes; deferred to steward. This run uses corrected arithmetic/geometric distinction, separate TS magnitudes (historical A8/G4≈7.2×, tree/G4≈40.8×), frozen calibration-selected mix and point-estimated acquisition economics. No other research files will be edited. The user's task-folder destination and prohibition on research-file commits override the research-rigor skill's Plans destination/commit request; approval is already explicit. Task artifacts stay in the main checkout; only code/tests/data needed for reproducibility are committed on this branch before full queued execution.

## Implementation complete

See [implementation.md](implementation.md) for smoke measurements, all sixteen
native replays, the seed audit, build-aware sensitivity, final 26-test pass and
actual queue-runner integration. The full queue is validated and unrun; full
production Stage 0 remains the admission gate. No targets were scored. The
historical sensitivity is a cheap descriptive calculation (about 0.24 worker
seconds), with paired historical rows retained across arms. Its build-pooling
joint-resolution frequency of about 58.6% reinforces that the pooled projection
and original power assertion are uncertain; it changes neither n nor the
pre-stated decision rule. All approved counts/arms/seeds/budgets are unchanged.
