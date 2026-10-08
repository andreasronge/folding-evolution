---
estimated_minutes: 100
---

Implement the approved proposal unchanged in sample size and exposure, incorporating
critique notes 1–5. Preparation stops after 120 minutes; an implementation or measured
cost obstacle produces infeasible.md rather than a redesigned experiment. This implements
an already approved design, rather than a new research-rigor registration or claim promotion.

Conditions: inherited and broken modifiers, separately for sum and max; P=1024,
L=64, lexicase, selected-mate v2 crossover 0.7, mutation 0.015, two elites.
Each run has 48 episodes, alternating thresholds 1 and 5, 64 fresh balanced
cases, stopping each episode at its first exact solve or 128 reproduction generations.
Threshold 2 is excluded from acquisition and scoring. Theta starts at zero,
is clipped to [-3,3], and receives independent N(0,0.03^2) increments per
recipient-derived child; elites copy exactly. Probabilities are
0.9 softmax(theta) + 0.1/22. A separate modifier RNG supplies perturbations
and control shuffles; program RNG consumption is preserved for identical rows.

Ordering: reset tapes from each current individual's probabilities, evaluate,
then (broken only) apply one uniform permutation of modifier rows across the
entire population before that generation's selection, including elite assignment.
Generation zero is included. An exact solve at generation zero still gets this
shuffle, but no reproduction. Each evaluated generation gets one shuffle, not
one per individual parent draw. After the final episode extract immediately,
without a reset or extra shuffle. Save every final theta and the mean final p.
This tests persistent program–modifier linkage under imposed resets, combining
initialization and ongoing variation; it does not isolate mutation.

Fixed acquisition roster: 16 runs per family/arm (64). Seeds and the reference
artifact hashes are frozen in the implementation manifest before queue execution.
Use paired program seeds across arms with separate modifier streams. Frozen
scoring: both training targets for each of 64 vectors, with 16 shared search
seeds per target. Uniform, manual scaffold, and the 1558 matched family fit each
get those 16 plus 48 additional seeds per target; cap 262144 evaluations.
Smoke seeds are separate from the full roster and never counted as full runs.

Before queue admission: validate labels and exhaustive checks for all four
targets, modifier support/normalization, distinct-row bookkeeping, resident-tape
execution independence, and 20-seed sigma-zero identical-row replay against
legacy search. Time one complete acquisition in each family/arm and frozen
searches by target. Record episode solves/48, generations, modifier-bearing
lineage depth, verification seconds, evaluator seconds, and censoring. Project
cost conservatively using the slower arm within each family and measured frozen
search tails; admit only if fixed roster and stage 0 fit <=210 minutes of queue
timeouts (and <=8 hours driver cap). The feasibility gate uses cost only, never
the observed arm advantage. Stage 0 repeats validations and timing in the queue.
The assumed 0.3-log between-run SD and x/divide 1.2 interval precision are
assumptions; four timing runs cannot estimate them reliably.

Primary endpoint: per-run geometric mean capped exact-search cost over 32
searches. Primary effect: broken/inherited, with families equally weighted.
Use a crossed bootstrap of paired acquisition-run indices within family and shared search
seed indices independently within target, preserving the shared seed block across
all vectors and arms. Save pooled and per-family effects, intervals and solve counts.

Outcome meanings, fixed before smoke tests:
- Lower 95% bound >1 and point >=1.5: linkage advantage. Useful acquisition also
  requires inherited costs to improve on uniform; a linkage advantage while both
  arms are worse than uniform does not establish useful learning. Report scaffold
  and matched-fit effects and acquisition-cost break-even searches for slot-2 review.
- Upper bound <1.5: bound on this exact procedure, provided exposure and solves
  support an informative endpoint. It does not rule out other inheritance rules.
- Otherwise: unresolved; price extensions for strategy. Broad intervals, both arms
  largely capped, or negligible lineage exposure also leave the mechanism unresolved.
- Similar improvement in both arms does not identify drift or the floor as its cause.
- Family-specific success remains family-specific even if the pooled result is positive.

Descriptive outputs: theta/probability trajectories (including CONST_2), Price
covariance with recipient offspring counts, actual modifier-bearing lineage depths,
episode solve times, capped-search solve counts and acquisition break-even costs.
Uniform establishes usefulness; scaffold compares practical value. Rediscovering the
scaffold alone does not justify escalation to more expensive map mechanisms.

Critique note 6 concerns digest/question-22 claims outside the researcher's writable
scope. No digest edit is authorized here; preserve its warning for the steward.

Implementation outcome: smoke and 151 relevant tests pass. Stage zero completed
four acquisition runs and 80 frozen timing searches. The conservative cost gate
fails: corrected fixed-roster envelope 569.13 minutes >210 minutes. See
[infeasible.md](infeasible.md) for the measurements, the envelope's conservative
limitation, and a mean-based pricing alternative for the steward. Stop before
writing a substantive queue; no acquisition effect is inferred from smoke data.

Implementation committed as `25f929e1f162756fbffc56b8a1d3e8a06cce00fc`;
worktree clean, no research/ files committed.
