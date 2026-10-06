---
status: open
tags: [map-bias, evolve-the-bias, task-family, compositional-transfer, decoder, fresh-start]
budget: {experiments: 7, used: 0}
---
# Can an adapted decoder help fresh populations solve unseen operation combinations beyond a token-frequency bias?

Current summary: **learned token weights on G transfer about 2× to the withheld compositions
and to branch-else; allowing learned contextual moves added no resolved training gain on top (≤ 1.11×), and
their holdout increment is unresolved** (4 of 7 slots used; strategy 1400 raised the budget
from 5 to 7).
Run 2026-10-06-0811 ([13](13-post-addition-map-learning/question.md), commit `0709104`, row 4):
from the six saved M maps, 12 matched pairs × 35 generations compared R (token steps plus
whole-row contextual residuals) with M+ (token steps only). R / M+ on fresh training 1.00×
[0.90, 1.11] (a gain above 1.11× excluded); on the two holdouts 1.16× [0.91, 1.48] and 1.06×
[0.83, 1.31], unresolved because the between-start spread is about twice the planned one.
Continued token learning still helped (M+ / M 1.45× on training). Frozen M was faster than G
on the two branch-else cells (2.23× [1.66, 3.06]), with a point estimate similar to the PA
holdouts (2.25×, 2.06×; lower bounds 1.81, 1.60; separate estimates, not an equivalence test),
and unresolved on linear cells, so its benefit is not confined to PA on the cells scored; a PA
preference is not ruled out. An unregistered six-map pattern, R faster than M+ on branch-else
(1.33× [1.05, 1.66], 5/6 starts) and slower on linear (0.65× [0.44, 0.88]), is the only hint of
learned context tied to the training shape. Operator acceptance was near 25% for every
operator; these counts do not establish how well selection ranks individual steps.

Run 2026-10-06-1400 ([14](14-saved-map-shape-shift/question.md)): the pre-registered check of
that pattern on the unscored "b" continuations, with residual ablation and a frequency-matched
token-only control (R_fm), was approved by the critic but did not run: the driver stopped at
prepare on a merge conflict (main into research/main). Run 1419 re-proposed it, was approved
and blocked the same way. The steward resolved the conflict on research/main (`e37c4a7`); no
data, no slot used (still 4 of 7); re-proposed as run 1425.

Run 2026-10-06-0132 ([13](13-post-addition-map-learning/question.md), commit `02cf76f`): on the
one-family post-addition split (six training, two withheld cells on D1331), 23 learned token
multipliers on G's rows (M, 6 trajectories × 25 generations) sped fresh search 2.2× over frozen G
on training and 2.0× / 1.7× on the two holdouts (95% lower bounds 1.47, 1.26; 6/6 trajectories).
The full contextual learner (C, 552 weights, three-coordinate mutations) drifted modestly but
showed no resolved training gain (0.92× [0.78, 1.09]). A frequency-only learner (T) beat its
context-free start 1.7–2.1× but stayed 1.8–2.4× slower than G. Family specificity and mechanism
are unmeasured; the bank was screened, so this is fresh-seed transfer on a screened bank, not an
untouched benchmark.

Earlier: two feasibility studies. Run 2026-10-05-2247 ([11](11-composition-bank/question.md)):
the 3×3 reducer/combiner bank failed its split and headroom requirements (no eligible split at
524 288 evaluations — Sm-SEL 27/50 under uniform, SM-SEL an exact alias — and all four structural
splits failed the 4 096-evaluation headroom rule under the hand-set previous-token grammar G,
held-out medians 768–4 096). Run 2026-10-06-0001 ([12](12-generic-grammar-headroom/question.md))
failed the two-family requirement but kept a usable one-family post-addition split: ten-token
cells leave room above G (post-addition and branch-else medians 8 192–41 728), yet none of six
same-primitive shapes gave two families with ≥ 4 non-aliased cells each. Across both banks G beats
its own context-free marginals (G-marg) 2.6–19.5× (KM median, 2247) and 1.5–6.0× (paired capped
time, 0001; 15/16 intervals exclude 1). Root 01 earlier showed useful transfer of fitted token
frequencies between constant thresholds, with a hand-set scaffold performing comparably. See the
[plan](../../plans/compositional-map-transfer.md),
[family addendum](../../plans/compositional-family-headroom.md),
[one-family plan](../../plans/post-addition-map-adaptation.md) and
[opening strategy](../../runs/2026-10-05-2039/strategy.md).

Competing explanations:
- A: Experience across training tasks selects reusable assembly preferences. The adapted
  decoder improves held-out search beyond a fitted independent-token map and simple fixed
  assembly controls, with an advantage tied to the training family.
- B: More useful tokens or generic well-formed programs explain the gain. An independent
  token bias or task-agnostic assembly rule performs comparably.
- C: The decoder specializes to training programs. Training improves but transfer fails
  when programs are reset or operation combinations are withheld.
- D: Held-out solvers become more frequent, but that distributional gain does not improve
  evolutionary search at the tested budget, or decoder changes damage useful local moves.
- E: The proposed tasks or adaptation loop are not tractable at the measured budget.
  This is a feasibility result about this design, not a negative answer to A.

Sub-questions: [11-composition-bank](11-composition-bank/question.md) (closed: this bank
fails on tractability at 524k and on the 4 096 headroom rule against G; run 2026-10-05-2247),
[12-generic-grammar-headroom](12-generic-grammar-headroom/question.md) (closed: ten-token
branch cells leave headroom above G, but no same-primitive family pair survives the alias
screen; run 2026-10-06-0001).
[13-post-addition-map-learning](13-post-addition-map-learning/question.md) (closed, 2 of 2
slots: G-based token multipliers transfer about 2× to the withheld pair and to branch-else;
contextual row moves on top add no resolved training gain (R / M+ 1.00× [0.90, 1.11]), holdout
increment unresolved; runs
2026-10-06-0132 and 2026-10-06-0811).
[14-saved-map-shape-shift](14-saved-map-shape-shift/question.md) (open, 1 slot, run 1400
blocked before running: does 0811's
branch-versus-linear shift of R over M+ replicate in the unscored "b" continuations, and does
it need R's residuals beyond its token frequencies? Saved maps only).

Related: [core question](../../../README.md#core-question),
[01-map-bias](../01-map-bias/question.md),
[08-evolve-bias](../01-map-bias/08-evolve-bias/question.md),
[09-generic-bias-speedup](../01-map-bias/09-generic-bias-speedup/question.md),
[run 0811 decision](../../runs/2026-10-06-0811/decision.md),
[digest](../../digest.md), [chem-tape findings](../../../docs/chem-tape/findings.md).

Review after the feasibility experiment and after the four allocated experiments. A
failed task candidate should prompt a bounded redesign, not an automatic stop of the
program. An unresolved transfer effect should be sized against measured runtime before
deciding whether another allocation could settle it.

Reopen if parked: a tractable task suite supplies the missing compositional contrast, a
decoder with demonstrably better training/search feasibility becomes available, or new
evidence defeats the specific generic-bias or overfitting explanation that caused parking.
