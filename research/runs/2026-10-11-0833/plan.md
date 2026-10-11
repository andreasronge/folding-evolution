---
estimated_minutes: 105
---
Implement the approved fixed-size boundary experiment using the existing tree search,
extractor and size-control generator. No engine, extraction policy, task roster,
restart budget or donor probability changes. Preparation/acquisition/validation has
a 45-minute timeout; scoring has 150 minutes (195 minutes total timeout).

Conditions: four frozen `TS.split.source` cells from 1717; 24 independent builds,
eight scheduled R-tree jobs per source cell, including failures. Each job has up
to eight attempts of 65,536 evaluations on exact D625; failure cost 524,288.
Extraction stays proper subtrees, 3–9 nodes, contains an input, recurrence in at
least two source cells, deterministic ranking, cap 16. Keep small/empty libraries
with ordinary-donor fallback. Construct one unchanged size/length-matched random
control per TS build. Recover and reconstruct all 24 saved 0150 DG libraries.

Scoring: twelve gate-sum B/C cells × 24 builds × six repeats × R-tree/R-TS/R-DG/
R-sizeTS (6,912 jobs), plus eight TS target cells × 24 builds × four repeats ×
R-tree/R-TS/R-DG (2,304 jobs). Destinations remain separate. Shared attempt seeds
within destination × cell × build × repeat; fresh initialization and cases follow
the existing restarted-search harness. Total scoring is 9,216 jobs; acquisition
is 768 jobs. No data-dependent downsizing, extension, or selection of builds.

Seeds: SHA256 of canonical JSON ["2026-10-11-0833", domain, parts], first eight
bytes, masked to 63 bits. Separate domains for production acquisition, B/C scoring,
native scoring, calibration acquisition, calibration scoring, size controls,
calibration controls and bootstrap. Publish complete schedules and seed sets;
audit against saved historical schedules through 0652, reserved probes and all
new phases. Historical off-path replay seeds and saved DG-control reconstruction
are explicit validation-only exceptions, never production acquisition/scoring.

Before any calibration, rebuild the local Rust extension and check canonical TS
and gate-sum programs against interpreter and VM on all D625 cases. Replay the
0150 off-path fixtures. Check source/target exclusion, source-only extraction,
per-entry interpreter/VM agreement, empty fallback, attempt accounting and paired
initialization/cases. Freeze bank hashes, method hashes and schedules.

Timing-only stage 0: two fresh calibration builds (64 actual TS-source jobs), then
one repeat on every B/C cell and every native target with both builds and all
respective arms (96 B/C + 48 native jobs). These seeds never enter confirmation.
Run at full attempt budgets with ten workers and one Rayon thread each. Measure
source rates by cell, donor yields, scoring rates by arm/destination, sustained
concurrency, and validation overhead. Project the exact approved full workload
using measured means, historical worker-time floors (B/C R-tree and new TS arms
6.48s, DG 2.37s; native 0.49s; TS-source 0.49s is only a conservative floor),
30% reserve and 90 seconds overhead. Admit only projected preparation ≤2,700s
and scoring ≤9,000s. Gates use runtime only, never cost-effect or solve-yield
selection. If this envelope or a semantic gate fails, preserve measurements,
write infeasible.md with alternatives, commit and stop. No quiet redesign.
Smoke-test this stage before queuing; production preparation repeats it unchanged.
The earlier 0.21M evaluations/build and 13× acquisition saving are projections,
not measurements of the four actual source cells.

Measurements: capped evaluation means and worker seconds, exact solves, attempts,
per-cell/per-build costs, library sizes/lengths, pair sums by split, predicates,
label counts, insertion/oversize rates, and acquisition-plus-search cost curves
with acquisition charged for both TS and DG. Primary ratio R-TS/R-tree on B/C,
cells equally weighted, with a 95% block bootstrap over 24 build slots. Bootstrap
solve-fraction difference alongside it. Secondary intervals: R-TS/R-sizeTS,
R-TS/R-DG and native ratios; DG source cohorts are independent of TS cohorts.
Acquisition uncertainty is resampled with its own build; shared contemporaneous
baseline jobs are not duplicated as independent observations. Store machine-
readable summaries, raw job records and plots for the later analyst.

Outcomes: B/C upper ratio <0.80 plus solve-difference lower bound >−0.03 supports
complete-procedure portability between these development rosters. An unresolved
R-TS/R-sizeTS contrast leaves learned-content advantage unresolved. B/C lower
ratio >0.80 excludes the specified ≥20% saving, not every useful saving. Then
native upper <0.80 with the same reliability guard supports native-only reuse;
native lower >0.80 excludes that native saving; otherwise native usefulness is
unresolved. A straddling ratio or failed reliability guard leaves routing unsettled
and needs a decision-relevant resolution price, not automatic extra jobs.

If TS fails to reproduce DG's B/C saving, responsible content remains unidentified:
source changes pair sums, probabilities, sizes, labels, solver yield and insertion
behavior together. The pseudo-build observation of no seven-node predicate does
not constrain future libraries. No skeleton-only inference, new learning mechanism,
inheritance conclusion or fresh-bank transfer claim is warranted.

Critique disposition: notes 1–5 are incorporated above, including calibration on
actual sources, fixed size, cautious attribution and explicit unresolved/native
reliability handling. Notes 6–8 concern digest/question wording; those files are
outside this role's authorized task-folder scope, so leave edits to the steward
and retain their narrower interpretations in this experiment's output language.
