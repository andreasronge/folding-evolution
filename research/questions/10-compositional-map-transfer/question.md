---
status: open
tags: [map-bias, evolve-the-bias, task-family, compositional-transfer, decoder, fresh-start]
budget: {experiments: 4, used: 0}
---
# Can an adapted decoder help fresh populations solve unseen operation combinations beyond a token-frequency bias?

Current summary: Unmeasured. Root 01 showed useful transfer of fitted token frequencies
between constant thresholds, but a hand-set scaffold performed comparably. This question
changes both the transfer target and what can adapt: hold out combinations of operations,
and let a small decoder carry context-dependent assembly preferences. Transfer only the
decoder; discard all training programs before testing on new tasks. First establish an
expressible, tractable task suite and measure the cost of the proposed adaptation loop.
See the [plan](../../plans/compositional-map-transfer.md) and
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

Sub-questions: [11-composition-bank](11-composition-bank/question.md) (feasibility; runs
2026-10-05-2039 and 2026-10-05-2242 blocked by a merge conflict before running; conflict
resolved, re-proposed as run 2026-10-05-2247).

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
