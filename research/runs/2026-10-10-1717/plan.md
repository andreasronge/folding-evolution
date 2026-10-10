---
estimated_minutes: 110
---

Implement the approved same-alphabet crossed DG/TS comparison, without running
confirmation searches in this researcher turn. Queue allowance is 80 minutes
preparation plus 140 minutes scoring (220 minutes summed timeouts). The
strategy's 120-minute preparation envelope is an outer ceiling; this proposal's
80-minute queue entry is the tighter admission limit, including bank work,
validation, acquisition, calibration and freezing. Expected wall-clock is110 minutes from the development measurements below;
full preparation recomputes admission from the confirmation-cohort calibration.

Conditions and admission

- Unchanged v2_x4 executor, D625, G4 and A8 recipe from 7244fa1: four G4 attempts
  per source, context/literal-fragment fit, four adaptive attempts, pooled refit;
  cap 524288, population 256, 64 lexicase cases, exact verification on all625.
  Preserve every build, failure and empty-corpus/library fallback.
- Performance-blind TS enumeration, all-four-readout eligibility, active GT and
  output branches; exhaustive real-token screen through nine tokens and strict
  <80% agreement; exact maximum separated clique; deterministic 4-source /
  4-development / 8-target split. Sources cover >=2 GT pairings and all readouts;
  targets cover >=3. Aggregate readout balance is a deterministic split tie-break
  when feasible, never a performance criterion. Screen plus exact-clique work has
  a hard 20-minute bound inside the preparation entry. An unfinished screen or
  unproved maximum is failed admission, never permission to weaken the screen.
- Reuse all24 frozen DG builds from1536, checking raw hashes, source schedules,
  tables/libraries, recipe and production code provenance. DG targets are the
  eight clique cells excluded from the old4/4/8 split. Verify never searched and
  excluded from both families' source behaviours (including actual source solvers).
- Small-scale smoke uses development cells only. A measured semantic/runtime
  obstruction writes infeasible.md and ends implementation; no bank substitution.
- Full preparation acquires24 independent TS builds, times >=64 full-cap searches
  across G4/D/T on both development rosters under10 workers, and logs yields,
  fallback incidence, exact verification/fitting/extraction time, concurrency,
  per-arm/family worker rates and projected2304-search cost with30% reserve.
  Admission depends on validity and complete price, never favourable contrasts or
  TS yield. Projected scoring plus reporting must fit140minutes. No target search
  occurs until both rosters, both cohorts, method, schedules and admission are hashed.

Seeds and units

Fresh TS confirmation attempts: first900000/adaptive1000000 +1000*build
+10*source_index+attempt, build0..23, attempt0..3. Development calibration:
1100000 +1000*(8*family_index+cell_index)+ordinal, four ordinals per development
cell, all three arms (96 searches), deterministically cycling all24 builds for
the price check. Confirmation:1200000 +1000*target_index
+ordinal,16 targets,48 ordinals, common seeds across G4/D/T; each acquired build
receives ordinals2*b and2*b+1. Smoke/pilot uses two separate builds, seeds1300000/1400000 for sources and
1500000/1600000 for development searches; full-cap pilot builds use the same
recipe and are excluded from confirmation. Smoke/calibration acquisitions have separate
seed blocks and cannot enter the confirmation TS cohort. Existing DG acquisition
seeds remain unchanged. Experimental unit is an acquisition build; the independently
acquired cohorts are not paired acquisitions.

Measurements and interpretation fixed before execution

Primary fixed-roster geometric capped-evaluation ratios: P_DG=T/D on DG,
P_TS=D/T on TS, I=sqrt(P_DG*P_TS), failures charged2cap. Report95% bootstrap
intervals with independent cohort build resampling, keeping every selected build's
rows on both rosters, and within-build/cell two-seed resampling. Common seed
ordinals are retained jointly across fitted-arm comparisons; independent build
resamples do not imply paired acquisition. G4 uses one shared cell/ordinal
resample per draw and is never counted twice. Repeat with1cap and flag changes.

- I lower>1.5: material geometric family interaction. Reciprocal preference only
  if both directional lower bounds>1. If one directional upper<1, the same bias
  dominates both rosters, even if I is material; report dominant bias with an
  interaction. A direction whose interval spans1 remains unresolved, not proven
  one-directionality. Family-specific acquisition is a candidate next action only
  if both own-family G4/fitted lower bounds>1 as well as reciprocal contrasts.
- I upper<1.5: exclude a material geometric interaction at this margin, not all
  useful smaller reciprocal preference. Shared-bias candidate only if both
  cohorts beat G4 by1.5x on both rosters (interval lower bounds); dominance requires
  directional interval evidence. Mostly capped fitted arms provide a difficulty
  boundary, not evidence of shared useful correction.
- Otherwise unresolved; report directional and absolute uncertainty and a priced
  resolution, with no automatic sample enlargement. Poor TS acquisition bounds
  this recipe on these sources, not a diagnosis of why DG is family-dependent.

All branches return to strategy. Also produce solves, per-cell/per-build costs,
fitness/diversity traces and arithmetic acquisition-plus-search evaluations and
measured times, charging each deployed build's entire acquisition once including
intermediate fitting. DG acquisition is sunk for queue execution but charged for
deployment. Geometric ratios do not determine repayment; no arithmetic saving
means no demonstrated break-even. Usefulness comparisons concern G4 at this cap,
not a competitive baseline or uncapped solve-time speedup.

Precision is a scenario: an interval factor1.30..1.45 gives lower1.38..1.54 at
I=2, upper1.43..1.60 atI=1.1. Neither point guarantees resolution. The new TS
cross-roster variation is unknown; retain the fixed24-build size regardless.

Critique disposition

Notes1..5 are implemented above: bounded prerequisites, development rates/full
price, directional/absolute evidence, independent build uncertainty, and scope.
Note6: closest fragment-transfer precedent is Wild and Porter, Multi-Donor Neural
Transfer Learning for Genetic Programming (2022),
https://eprints.lancs.ac.uk/id/eprint/174982/?template=browse; alongside PIPE,
https://pubmed.ncbi.nlm.nih.gov/10021756/. A8 is external fitting and literal-fragment
injection, not inheritance or invention of distribution learning/fragment transfer.
Note7 is deferred to the steward: the researcher may write only this task folder
in research/, so cannot edit digest.md. The tenth-of-full-F cost claim is scoped
to original output-family sources, not DG. Conclusions remain conditional on these
source/target rosters; DG is a development bank; output ranges differ, so this is
neither broad fresh-bank generality nor isolation of ADD placement.


Measured preparation feasibility (researcher, before any target search)

The216-cell TS real-token screen completed in106.8s;192 retained cells and an
exact108-cell maximum clique were certified, with bank/split complete in125.3s.
The four sources have aggregate readout counts6/6/6/6; source GT coverage and
three-pairing target coverage passed. The complete24-build DG cohort, all768
source attempts, intermediate/final fits and production Python/Rust/backend
hashes passed provenance checks. Both canonical/reference checks and the reduced-
cap prepare/score/report path passed;56 relevant unit tests passed.

A separate2-build full-cap development pilot completed23/32 first and32/32
adaptive TS source solves; acquisition batches cost399.0+48.6 worker-s plus0.664s
fitting/verification/extraction. The96 development searches completed in156.2s,
1429.7 worker-s,9.15 effective workers. Mean worker-s/search:

|Roster|G4|D|T|
|---|---:|---:|---:|
|DG development|30.264|15.834|25.220|
|TS development|11.718|3.914|2.403|

Full2304-search projection including30%reserve+90s reporting is82.7minutes.
Conservatively scaling the two-build acquisition wall batches by12, plus bank,
validation and96-search calibration gives17.6minutes preparation (22.9 with30%
reserve); total about105.6minutes, rounded to110minutes expected queue wall-clock.
This fits80+140minute entries. Acquisition pilot batches had4.74..7.45 effective
workers due small batches/tails and brief overlapping reduced-cap checks;
calibration was sustained and independent at9.15. The rates use only two pilot TS
builds and two deterministic DG builds, so they are feasibility prices rather
than assured confirmation performance. Full preparation cycles all24 independently
acquired confirmation builds in the96-job development calibration and enforces
its measured price before scoring. No yield gate or adaptive sample enlargement.

Raw pilot rows/metadata and bank observations are preserved under[smoke](smoke/),
with a compact arithmetic price in[smoke_measurements.json](smoke_measurements.json).
Pilot code hashes precede the final all24-build calibration cycling change; its
TS/DG search recipe and operator are unchanged. A final reduced-cap smoke verifies
the committed orchestration. The full target rosters remain unsearched.
