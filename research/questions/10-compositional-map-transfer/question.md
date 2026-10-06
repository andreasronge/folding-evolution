---
status: open
tags: [map-bias, evolve-the-bias, task-family, compositional-transfer, decoder, fresh-start]
budget: {experiments: 5, used: 0}
---
# Can an adapted decoder help fresh populations solve unseen operation combinations beyond a token-frequency bias?

Current summary: **first learned-decoder transfer measured: retuning G's token weights helps
the withheld compositions; a contextual learner did not move** (3 of 5 slots used).
Run 2026-10-06-0132 ([13](13-post-addition-map-learning/question.md), commit `02cf76f`): on the
one-family post-addition split (six training, two withheld cells on D1331), 23 learned token
multipliers on G's rows (M, 6 trajectories × 25 generations) sped fresh search 2.2× over frozen G
on training and 2.0× / 1.7× on the two holdouts (95% lower bounds 1.47, 1.26; 6/6 trajectories);
the learned change is mainly INPUT up and DUP down. The full contextual learner (C, 552 weights,
three-coordinate mutations) showed no practical training gain (0.92× [0.78, 1.09]) and stayed at G
plus noise, so whether learned *contextual* preferences transfer is still untested. A
frequency-only learner (T) beat its context-free start 1.7–2.1× but stayed 1.8–2.4× slower than
G. Family specificity and mechanism are unmeasured; the bank was screened, so this is fresh-seed
transfer on a screened bank, not an untouched benchmark.

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
[13-post-addition-map-learning](13-post-addition-map-learning/question.md) (open, 1 of 2
slots used: G-based token multipliers transfer 1.7–2.0× to the withheld pair; the contextual
learner did not move under its mutation operator; run 2026-10-06-0132).

Related: [core question](../../../README.md#core-question),
[01-map-bias](../01-map-bias/question.md),
[08-evolve-bias](../01-map-bias/08-evolve-bias/question.md),
[09-generic-bias-speedup](../01-map-bias/09-generic-bias-speedup/question.md),
[digest](../../digest.md), [chem-tape findings](../../../docs/chem-tape/findings.md).

Review after the feasibility experiment and after the four allocated experiments. A
failed task candidate should prompt a bounded redesign, not an automatic stop of the
program. An unresolved transfer effect should be sized against measured runtime before
deciding whether another allocation could settle it.

Reopen if parked: a tractable task suite supplies the missing compositional contrast, a
decoder with demonstrably better training/search feasibility becomes available, or new
evidence defeats the specific generic-bias or overfitting explanation that caused parking.
