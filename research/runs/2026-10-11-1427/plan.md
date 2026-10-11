---
estimated_minutes: 20
---

Implement the approved standing-variation probe without changing library content,
exposure size, starting frequency, or scoring roster. Read-only inspection and
this plan precede all experiment execution. No protected cells are scored.

Conditions: 24 saved 1228 R-all libraries; P=256, crossover=0.5, lexicase,
two elites; exactly 64 randomly assigned carrier slots, independent of initial
programs. L uses R-all for bit 1, S uses the same law with bits permuted before
each generation's selection, Z uses random donors matched per library entry
in nodes and compiled length, and N uses ordinary donors for both states.
Recipient inheritance applies to crossover, mutation, failed insertion and
elites; no bit mutation. Four trajectories per library in L/S/Z, two in N
(336 total). Each trajectory has 12 episodes (six development cells twice),
64 generations per episode; starts rotate across library/replicate identities
so each cell leads equally often. Programs reset independently at each episode;
bits retain their slots.

Seeds: fixed dedicated namespaces for program evolution, modifier assignment,
shuffle, size-null construction and frozen readout, separate from historical
acquisition/scoring. Log every actual seed and schedule. Neutral and fixed-bit
checks compare against the original engine under identical program seeds;
modifier RNG calls must never consume program RNG state.

Measurements: save all generation censuses, recipient frequencies, operator
counts by bit and solve phase (draws, accepted insertions, oversize reverts),
first exact hit and verification, fitness/diversity, final f, fixation/loss,
and episode pre/post-first-solve changes. Continue past solves with a preserved
first-hit witness. Validate bit/tree alignment, elite/fallback inheritance,
independent initialization, fixed off/on recovery and neutral RNG invariance.
Time complete 768-generation trajectories including Z and post-solve logging
before queuing. Stop with infeasible.md if the approved design cannot fit its
1,500-second exposure and 1,800-second readout ceilings.

Frozen readout: discard programs; for each library deploy probabilities 0,
0.125, 0.5*mean(f_L), 0.5*mean(f_S), and 0.5. Mean f uses all four trajectories,
not the best endpoint. Score six development cells × two repeats × five laws
× 24 builds = 1,440 restarted jobs, eight attempts and 65,536 evaluations per
attempt, paired fresh seeds across laws. This tests the aggregate deployment
rule, not deploying a randomly selected evolved population. Save capped failures,
per-cell costs/ratios, solve rates and uncertainty, plus library provenance.

Interpretation: report L−S with a bootstrap over 24 library units, L−Z, neutral
movement and initial/R-all capped evaluation cost. The approved advisory
continuation thresholds are L−S≥0.15 with lower interval>0, L−Z≥0.10, and
initial/R-all≥1.25. Passing them motivates strategist review, not confirmation;
a useful frozen L-final saving must also be inspected. Failing linkage contrast
leaves weak selection, drift, early allele loss or insufficient exposure
unresolved; a tight small contrast weakens investment in this procedure.
Failing the size contrast means content advantage over this size control is
unresolved. Matching donor sizes does not equate realized rejection, semantic
neutrality or damage: compare measured rejection by bit and solve phase.
Missing initial headroom weakens the usefulness case. A neutral interval excluding
0.25 raises a diagnostic alarm; direct alignment and RNG validation determine
whether bookkeeping is broken. Broad intervals imply uncertainty, not equality
or absence. No confirmatory outcome table or transfer claim.

Critique disposition: notes 1–4 are incorporated above, including complete timing,
first-hit semantics, size-control limits, advisory thresholds and aggregate
readout. Notes 5–6 concern historical digest/question wording; those files are
outside the researcher's authorized write scope, so leave them for the steward.
No new literature acquisition is needed for this implementation.

Implement with the existing tree engine and order-cap harness; smoke checks will
be recorded here after completion. The full queue will use ten workers and
RAYON_NUM_THREADS=1, output only under RUN_DIR, summed timeouts 55 minutes.

Engine convention (fixed before smoke): a 64-generation episode evaluates 64
populations and performs 63 offspring transitions, exactly the existing tree
engine's cap/P convention. The last census is logged with no recipient draw;
there is no unscored extra reproduction after the final evaluated population.
Thus exposure is 768 evaluated populations and 756 selection transitions per
trajectory; this interpretation keeps the approved tree engine unchanged.

Validation completed before queuing:

- `RAYON_NUM_THREADS=1 .venv/bin/python -m pytest -q
  tests/test_inherited_library.py tests/test_tree_hand.py
  tests/test_tree_library.py tests/test_tree_source.py tests/test_tree_gp.py
  tests/test_tree_uniform.py`: **60 passed in 50.98 s**. Default ordinary and
  R-all searches replay exactly against the immutable 1228 engine at
  `60ab76697cc1e5592474b4819f4bb3761c5bbbcd`, excluding timings. Checks cover
  fixed bits, neutral RNG independence, recipient/elite/revert alignment,
  shuffled alignment, first-hit continuation, seed separation, grids and
  all 24 size-null constructions. The historical source guard retains the
  archived engine check and additionally pins this exact opt-in extension's
  source hash; it does not admit arbitrary engine drift.
- Final end-to-end smoke outputs are in [smoke/final-exposure](smoke/final-exposure/)
  and [smoke/final-readout](smoke/final-readout/). Four complete trajectories
  (one per arm, library 0; 12 × 64 evaluated generations each) took L 9.990 s,
  S 10.276 s, Z 10.220 s, N 10.088 s of worker wall time under four workers:
  0.01301–0.01338 s/generation. Exposure batch wall time was 10.686 s;
  preparation plus exposure 18.108 s. All twelve episode initial-program
  hashes match across arms. Size-null construction for all 24 builds took
  0.874 s (separate interpreter/VM validation also completed).
- Five-law fresh scoring completed the entire 60-job smoke grid, with the
  approved eight-attempt/65,536-evaluation caps, in 58.949 s on four workers,
  consuming 203.568 worker-s. The final readout successfully revalidated the
  frozen code, saved library identity, seed audit, complete trajectories,
  reconstructed size controls, mean-frequency extraction and exact witnesses.
  A dynamics plot was generated. Smoke efficacy is not used to alter design.
- Linear ideal-ten-worker projections are ~343–346 s for exposure and 489 s
  for readout. These are engineering estimates from one performance-blind
  library, not guarantees for the remaining mixtures/builds or full-cap tails.
  The historical ten-worker anchors plus the approved 1,500/1,800 s timeouts
  leave substantial slack, so no infeasibility stop is indicated. The initial
  expected queue wall-clock estimate of 20 min remains conservative.
- `scripts/queue_lib.load_queue` accepts the two-entry queue; ids use the
  required prefix and timeout sum is 3,300 s (55 min). Commands use worktree
  cwd and write experiment outputs solely under RUN_DIR. Partial results are
  flushed; failure files prevent downstream readout and complete-grid checks
  prevent inference from incomplete stages. Syntax and `git diff --check`
  checks passed. No Rust source changed.

Implementation: `experiments/chem_tape/inherited_library_run.py` supplies the
immutable-corpus reload, controls, schedules, provenance, two execution phases,
whole-library descriptive bootstrap and plots. Optional parameters on
`tree_gp_search.search` carry the modifier and global donor probability while
preserving the old default RNG path. No source acquisition or protected search
was performed. The full queue has been prepared, not executed by this role.

Code committed on `research/2026-10-11-1427` as `f8f4246` (Implement inherited
library-choice probe and frozen readout). Only four implementation/test files
are in the commit; task-folder plan, queue and smoke artifacts remain in the
main checkout's research directory. Worktree status is clean.
