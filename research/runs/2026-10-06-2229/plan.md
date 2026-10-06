---
estimated_minutes: 45
---

# Implementation plan, recorded before experimental execution

Implement proposal 2229 as one frozen holdout evaluation, reusing
composition_search.search and the stage-1 t/Welch inference helpers. No learning,
map selection, new trajectories, or training searches are allowed. Expected queue
wall time 45 minutes (initial estimate 55, updated after the probe); ten workers, 6,300-second internal
deadline including a reporting reserve, and 7,200-second external timeout.

## Conditions, provenance and seeds

Load all BE1–BE10 and PA1–PA10 from stage 1723's recorded trajectories.json.
Freeze original source bytes in experiments/chem_tape/data/ (fresh_scores.json
is gzip-compressed losslessly) and verify
source SHA256s, exact IDs/families/outer seeds, table hashes, and the tables
reconstructed from the saved 24-dimensional vectors against G4. Preserve every
map at equal weight. G4 hash is
8a7b3091f411e659f553981b8680dc5db4bd5f3f34b6eca9c8ab3ee3e728dc10.
Read the frozen 1603 bank (SHA256
b2b856cb6d051e65599b22409cf49f654ba8d87539f073d2e9b7d061079aceb9), verify D1331
labels, and expose only holdout IDs and labels to search jobs:
BE:S?m:(M+F), PA:(F?S:M)+m, PA:(S?M:m)+F.
Training/holdout ID and label disjointness must hold. Source stage-1 fresh training
scores are frozen for descriptive transfer loss, never searched again.

Full design: 21 maps × 3 holdouts × 400 seeds = 25,200 searches. Shared seed block
2229000–2229399 for every map/cell. Cap 524,288, P=256, length 32, crossover .7,
mutation .03, 64 sampled training cases and exact checking on all 1,331 inputs;
unsolved cost equals cap. Use the unchanged stage-1 search engine. Log source
hashes, commit, all settings, per-search timings, table hashes, case indices,
solve/shortcut counts and curves under RUN_DIR. Validate the exact Cartesian
product and common case indices before inference. Deadline interruption or any
missing/duplicate/extra row is unresolved; never analyse a completed subset.

## Measurements

For each map/cell average log2(T_G4/T_map) across shared seeds. Independent
learning trajectories are the unit (n=10 per family); one-sample 95% t intervals
for arm gains and Welch 95% intervals for between-arm contrasts. Exponentiate
means and interval bounds to report ratios. Give six arm × cell estimates,
BE and equal-weight two-cell PA aggregate arm gains, per-map rows, solve counts,
shortcut counts, fitness/diversity and solve curves, and own-training-to-own-
holdout log-gain loss using stage 1's existing 50-seed rows.

Primary C_BE = BE minus PA maps on the BE holdout; C_PA = PA minus BE maps on
each map's mean of the two PA holdouts. Also retain each PA contrast separately.
W means lower ratio bound >1; B means upper bound <1.25; X otherwise, with W
precedence while reporting both flags. Report signed estimates and a reversed
preference when upper <1. The secondary interaction in every outcome is Welch
on d(map)=BE-cell gain minus mean PA-cell gain, BE maps minus PA maps;
its point estimate must equal C_BE+C_PA in log2 space.

For every W direction give matched and mismatched aggregate G4 gains, each
labelled improved (lower >1), harmed (upper <1), or unresolved. Useful improvement
requires resolved matched gain; mismatch damage requires resolved mismatched
harm. Unresolved harm is not absence of harm. Individual PA cells remain visible.

## Outcome meanings and competing explanations (ordered rules)

U: hash/semantic/job validation failure, incomplete data, learning/training jobs,
or G4 solve fraction <.85 on any holdout. Frozen evaluation is unresolved and
can be rerun; preserve diagnostic measurements, no selected-subset inference.
1: both directions W. Family-dependent matched advantages on these three cells;
A's useful specialization is supported only in directions with matched gain L.
Report C (mismatched-arm harm) if resolved, otherwise harm remains as bounded.
2: exactly one W. Family dependence shown in one direction; the other is B/X,
with separate useful-improvement and damage labels.
3: neither W and none of the six arm/cell gains L. Holdout improvement unresolved;
report upper bounds. This does not establish transfer loss or explain it as C.
4: neither W and both B. Matched advantages below 1.25 at these intervals;
retain reversed preferences if present. Approximate equality/generic transfer
is not established by B alone. Report whatever G4 gains are resolved.
5: remaining cases. Directional family dependence unresolved despite at least
one resolved holdout improvement. 5a: interaction W shows aggregate family
information without locating its direction. 5b: interaction not W leaves A vs B
unresolved even with generic improvement. More seeds cannot replace independent
trajectories or additional BE tasks. D was ruled out at stage 1's training scope.
Always report the interaction, including rows 1–4.

Scope: three screened bank cells, one BE task, D1331, token-only learning with
hand-supplied G4 context. No general family or shape-causation claim follows.
Prediction remains row 5, mostly 5b; anticipated gains 1.6–2.0× and directional
preferences about 1.1×, unresolved at n=10.

## Critique dispositions and future precision

Notes 1–4 are implemented above: deadline incompleteness is U; negative and
reversed results retain their uncertainty; useful improvement and damage are
separate; PA aggregate gains and the interaction always appear. For note 5,
keep this run fixed at n=10. Future-study sizing will use each direction's
observed trajectory variances and Welch degrees of freedom. Report separately
n for expected half-width <log2(1.1)=.1375 and approximate 80% detection at a
true 1.1× effect (two-sided 95% normal approximation with t refinement); neither
is a guarantee and task replication remains fixed. The proposal's projected
half-widths imply roughly BE 60–100/family, PA 20–33/family, and interaction
32–60/family for interval-width sizing (smaller t multipliers included).
Detection sizing is about twice the interval-width n. At stage-1's measured
10–14 minutes/trajectory, adding BE's roughly 100–180 trajectories costs
17–42 hours before evaluation; direction-specific actual estimates and costs
will appear in the report. A later training-informed study is deferred for cost
and scientific scope, not inherently invalid as a 'rescue'.
Notes 6–8 concern existing digest/question wording. The researcher role forbids
editing those files, so leave their revisions to the steward; this run's wording
retains point-estimate and uncertainty qualifications.

## Verification and feasibility stop

First verify provenance, frozen map reconstruction, no-learning/job invariants,
Cartesian completeness, unsolved cost, trajectory Welch inference, interaction,
negative/reversed outcome precedence, and deadline partial persistence using
focused tests. Run a reduced-cap infrastructure smoke with all 21 maps and all
three cells (2 seeds 2229400–2229401, cap 8,192), explicitly non-scientific. Then a small
full-cap feasibility probe on all maps/cells with diagnostic seeds
2229500–2229504 (315 searches, disjoint from the confirmatory block), recording
per-map/cell solve fractions and runtime. This probe selects or excludes no map
and sets no scientific outcome. Compare the measured total projection to the
105-minute deadline and the approved reachability assumptions; tiny probe
solve fractions alone do not substitute for the full 400-seed .85 G4 gate.
If targets/runtime/validation make the approved design infeasible, write
infeasible.md with measurements and alternatives, commit and stop for steward
replanning. Otherwise write the single full queue entry, validate its schema
and timeout sum, commit all changes on research/2026-10-06-2229, and leave clean
status. Full evaluation is deferred to the driver.

## Preparation measurements (outcome rules above remain unchanged)

The full-cap diagnostic probe completed 315/315 searches in 34.21 seconds,
mean worker-search time .75065 seconds. Projection is 34.53 minutes including
a three-minute reporting allowance; retain 45 minutes for expected queue time,
105 minutes internally and 120 externally. G4 solved 5/5 on each holdout; BE
maps solved 150/150 and PA maps 147/150 across cells. Individual learned-map/
cell counts range 3/5–5/5. These small counts support reachability but do not
replace the full .85 G4 gate or yield research conclusions. No map is selected,
dropped or re-weighted. See smoke.md and verification.json for measurements.

The first reduced infrastructure smoke accidentally used 2229000–2229001 at
cap 8,192 (2 of the 400 planned evaluation seeds). It was never used for
inference, adaptation, selection, or a design change; those two diagnostic
rows per map/cell are excluded from the full results. The final implementation
uses a disjoint smoke block and records the initial exposure in config.json.
The prescribed 400-seed block and all frozen maps remain unchanged; the full
run independently repeats every job at the approved cap. This limits the
literal claim that every evaluation seed was wholly unseen during preparation,
without changing the prospective comparisons. Regression tests enforce seed
separation for subsequent smoke runs.
