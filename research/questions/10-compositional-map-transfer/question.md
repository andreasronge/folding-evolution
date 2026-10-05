---
status: open
tags: [map-bias, evolve-the-bias, task-family, compositional-transfer, decoder, fresh-start]
budget: {experiments: 5, used: 0}
---
# Can an adapted decoder help fresh populations solve unseen operation combinations beyond a token-frequency bias?

Current summary: No transfer measured yet; two feasibility studies, two bank failures (2 of
5 slots used). Run 2026-10-05-2247 ([11](11-composition-bank/question.md)): the 3×3
reducer/combiner bank had no eligible split at 524 288 evaluations (Sm-SEL 27/50 under uniform,
SM-SEL an exact alias), and all four structural splits failed the 4 096-evaluation headroom
rule under the hand-set previous-token grammar G (held-out medians 768–4 096); raising the
search cap alone does not remedy that. Run 2026-10-06-0001
([12](12-generic-grammar-headroom/question.md)): ten-token cells do leave room above G
(post-addition and branch-else medians 8 192–41 728, 2–10× the 4 096 line), but none of six
same-primitive assembly shapes (162 canonicals over {S, M, m}, three domains) yields two
families with ≥ 4 non-aliased cells each — ADD/IF_GT/CONST_0/DUP identities and S-sign
correlation make most variants reducible to ≤ 9 tokens. Across both banks G beats its own
context-free marginals (G-marg): 2.6–19.5× in KM median on 2247's eight cells, 1.5–6.0× in
paired capped time on 0001's 16 (15/16 intervals exclude 1) — context in the decoder is a large
lever on this tape, but supply and mutation structure change together, so it names no
mechanism. Root 01 earlier showed useful transfer of fitted token frequencies between constant
thresholds, with a hand-set scaffold performing comparably. This question holds out
combinations of operations and lets a small decoder carry context-dependent assembly
preferences; only the decoder transfers. Next design (strategist): a one-family post-addition
split (valid on D1331, both holdouts > 13k under G), a different contrast, or an alphabet
change. See the [plan](../../plans/compositional-map-transfer.md),
[family addendum](../../plans/compositional-family-headroom.md) and
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
