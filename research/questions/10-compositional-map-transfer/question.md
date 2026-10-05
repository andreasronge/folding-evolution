---
status: open
tags: [map-bias, evolve-the-bias, task-family, compositional-transfer, decoder, fresh-start]
budget: {experiments: 4, used: 0}
---
# Can an adapted decoder help fresh populations solve unseen operation combinations beyond a token-frequency bias?

Current summary: No transfer measured yet. The first feasibility study (run
2026-10-05-2247, 11) found its 3×3 reducer/combiner bank unusable: no eligible split at
524 288 evaluations (Sm-SEL 27/50 under uniform search, SM-SEL an exact alias), and, more
bindingly, a hand-set previous-token grammar G solved every held-out cell in a median of
768–4 096 evaluations, so no split could have headroom against it. In median evaluations to
solve, G was 8.6–31× faster than uniform (seven cells with intervals) and 2.6–19.5× faster
than its own context-free marginals (G-marg, all eight paired intervals above 1) — context-dependent decoding is a large lever on this tape, but here a generic grammar
already supplies it. Root 01 earlier showed useful transfer of fitted token frequencies
between constant thresholds, with a hand-set scaffold performing comparably. This question
holds out combinations of operations and lets a small decoder carry context-dependent
assembly preferences; only the decoder transfers. Before experiment 2 it needs a bank and a
fixed control under which held-out cells keep headroom ([12](12-generic-grammar-headroom/question.md)).
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

Sub-questions: [11-composition-bank](11-composition-bank/question.md) (closed: this bank
fails on tractability at 524k and on headroom against G; run 2026-10-05-2247),
[12-generic-grammar-headroom](12-generic-grammar-headroom/question.md) (open, unmeasured:
which bank and which fixed control leave room for a learned decoder; strategist's call).

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
