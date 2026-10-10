---
estimated_minutes: 120
---

Implement the approved saved-build component crossing; no acquisition, refit,
new bank, G4 scoring, or full target execution in this researcher turn. Queue
wall-clock expectation is about 100–150 minutes, conditional on calibration;
timeouts remain 30 minutes preparation/validation, 150 minutes DG, 60 minutes TS.
Historical timings are costing scenarios, not bounds on hybrids or bare tables.

## Frozen conditions and seeds

Reuse all 24 D and 24 T final builds, banks, target manifests and acquisition
records from the completed 1717 preparation. Freeze their hashes and production
method hashes. Pair D i to T pi(i), where pi is the NumPy default_rng(2001)
permutation of range(24), recorded verbatim in the preparation manifest. Six arms
are D/D, T/T, T/D, D/T, D/none and T/none. Table owner, library owner and explicit
operator mode are separate fields. None means block edits disabled, retaining the
same learned table and ordinary search. All other production settings stay 1717:
v2_x4, cap 524288, population 256, 64 training cases and exact D625 verification,
ordinary mutation/crossover, support/conditional re-encoding and block edit law.

Full schedule: eight saved DG spare targets and eight saved TS protected targets,
24 donor pairs, two new common seeds, six arms = 4608 searches. Seed = 2100000 +
1000*(8*family_index + cell_index) + 2*pair + repeat, family DG=0, TS=1.
Arms with a shared table must have identical initial-population hashes. Ordinary
variation and block edit RNGs remain independent. Inference is conditional on
these development rosters and this frozen donor assignment.

Calibration uses each family's four saved development cells, pairs 0 and 12,
one seed per cell/pair, all six arms: 96 full-cap searches (48/family), with seeds
2200000 + 1000*(8*family_index + cell_index) + pair. No calibration row enters
confirmation. Sustain ten workers with RAYON_NUM_THREADS=1. Record worker-seconds,
wall time, solve counts and verifier tails per arm/family. Project each full
family from sustained wall throughput and summed worker time, with 30% reserve
plus reporting overhead. Both scoring stages must fit their allocated timeouts
before any target score. Otherwise write an obstruction and return to strategy;
never drop arms or seeds.

## Preparation and smoke gates

Verify provenance/hashes of all 48 artifacts, source membership, bank/target
manifests, unchanged production method and exact verifier. Replay 16 saved native
1717 target rows bit-exact on deterministic search fields (elapsed time excluded),
spread over both families/cohorts and builds, using their historical seeds. This
is validation of historical rows, not new confirmation scoring. Verify explicit
operator-off executes zero block events, enabled mode retains fallback behavior,
and identical table/seed yields identical initial populations across library
choices. Smoke at reduced cap on development cells, then run the sustained
96-job full-cap calibration if the implementation gates pass. Store smoke outputs
in this task folder, never in research tracked on the experiment branch.

## Measurements and interpretation

search.jsonl directly records table/library identities and hashes, pair, family,
cell, repeat, seed, solved, evaluation cost, search_seconds, exact-check counts,
fitness/diversity trajectories and initialization hash. A dedicated report groups
by family x arm x cell x pair, emits capped geometric costs (failures 2*cap),
solve fractions, full 2x3 table, per-cell/pair costs, and 1*cap sensitivity.
Bootstrap 8192 fixed-seed draws: resample the 24 donor pairs, keep all six arms
and both rosters together, jointly resample the two seeds within pair x cell;
cells fixed. Report effect sizes and 95% intervals, no p-value tests added.

Primary R=cost(T/T)/cost(T/D), worthwhile replacement margin 1.5. Lower>1.5:
a worthwhile D-library replacement increment under the T table. Residual
G=cost(T/D)/cost(D/D): upper<1.5 means library sufficient **within this 1.5x
replacement tolerance**, lower>1.5 means portable but partial, crossing 1.5 means
sufficiency unresolved. Upper R<1.5 excludes a worthwhile replacement increment,
not useful portable library activity: also report cost(T/none)/cost(T/D).
Crossing R means unresolved, with resolution price; R around 1.6–1.8 can remain
unresolved. Pair heterogeneity and the predicted interval factor are unmeasured
planning scenarios.

Bare B=cost(T/none)/cost(D/none) lower>1.5 supports a table-carried contribution,
which can coexist with library effects. A D/none versus D/D gain by itself does
not establish native dependence. Report cost(D/T)/cost(D/D) and both libraries'
gains under each table; native-combination language requires evidence that the
library identity matters under that table, rather than merely that blocks help.
Mixed contributions are possible. If fresh D/D versus T/T does not reproduce the
historical DG gap, report that explicitly and leave attribution conditional on
the new reference result. Too-clean hybrid equality requires checking operator
activity, library hashes, initialization and exact verification rather than a
mechanistic conclusion from equality alone.

On TS report retention cost(T/D)/cost(T/T). An interval wholly above 1.5 would
make an indiscriminate D-only repertoire practically unattractive and favor
family-aware or joint acquisition; an interval crossing 1.5 leaves that choice
unresolved. This is secondary guidance, not an added reciprocal decision gate.
Near-complete solving does not imply equal search effort. Report arithmetic
acquisition-plus-search evaluations and time at explicit horizons, hybrids
charged both acquisitions, native/bare arms their own acquisition. Bare final
tables were acquired using intermediate libraries. Resolution price extrapolates
observed pair log-ratio uncertainty with its assumptions and costs stated.
Return to strategy for every result, including unresolved or validity obstruction.

## Critique disposition and scope

Notes 1–4 are incorporated above; no extra arms or multiplicity machinery.
Note 5: closest reusable-library precedent additionally includes Keijzer, Ryan &
Cattolico, Run Transferable Libraries—Learning Functional Bias in Problem Domains
(2004), as linked in critique.md. PIPE is a distribution-learning precedent;
stitching here uses a shared token interface without a fitted adapter. The new
work attributes a learned family effect by crossing frozen external fits, not
inventing libraries or demonstrating inheritance. Library size, content and
length distribution move together; table initialization and ongoing decoding
move together. This is saved-decoder portability on development banks, not
fresh-bank transfer or evolutionary coadaptation.
Notes 6–9 concern digest/question/log edits outside the researcher's authorized
write scope; defer them to the steward. Do not copy their stronger labels into
this experiment's reports. No belief files will be edited.

## Measured feasibility before queue submission

At commit 6dabda8 the 96-search full-cap calibration and 16 native replays
finished in 141.6 seconds. Sustained DG/TS batches took 84.2/25.3 seconds,
with 8.59/4.87 effective workers (TS has short searches and a tail). The
conservative full-score projections are 5373.6 seconds DG and 1699.2 seconds TS,
including 30% reserve and 120 seconds per stage, below 8970/3570 seconds.
Calibration solves in arm order D/D,T/T,T/D,D/T,D/none,T/none were
DG 7,4,6,6,5,4 of eight and TS 7,8,8,7,8,7 of eight.
These are development calibration observations, not attribution evidence.
See smoke_measurements.json and smoke/full-cap-calibration/preparation.json.
The queue repeats validation and calibration at its executing code state.
Updated expected queue wall-clock is about two hours; its timeout ceiling remains
four hours. No new confirmation target search was run during implementation.
