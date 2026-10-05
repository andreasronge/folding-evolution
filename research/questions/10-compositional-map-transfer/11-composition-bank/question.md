---
status: open
tags: [compositional-transfer, task-bank, feasibility, decoder, stack-tape, reduce-min]
budget: {experiments: 1, used: 0}
---
# Is there a tractable bank of held-out reducer/combiner compositions with room for a learned decoder?

Current summary: Unmeasured as a bank; steward probes only. The first attempt (run
2026-10-05-2039) was blocked by a merge conflict before any code ran; it is re-proposed with
the critic's notes as run 2026-10-05-2242. Slot not yet charged.
The plan's candidate bank (SUM/MAX/ANY with ADD and GT on signed length-4 lists) mostly fails
the alias check: ANY is 1 on 624 of 625 inputs, so every ANY task is within one input of a
constant-substituted single-reducer task, and every GT comparison is ≥ 96% a single-reducer
threshold, i.e. the old threshold family. Integer-valued compositions (X+Y, 2X+Y, and
"S>0 ? X : Y") of SUM, MAX and a new REDUCE_MIN have no simple near-alias (best simpler
program ≤ 69% agreement). Evolution on the stack tape solves the MIN-free ones in about
10k–100k evaluations at population 256.

Competing explanations for a failure here (each is about this design, not root 10's answer):
- Bank: too few cells survive exhaustive alias and near-alias screens for a crossed split.
- Tractability: held-out cells are too hard for uniform evolution at the measured budget.
- Headroom: a hand-set, task-agnostic grammar decoder already solves held-out cells almost
  at once, leaving no room for learned family structure.
- Cost: the nested adaptation loop needed next does not fit an 8-hour queue.

Related: [root 10](../question.md), [plan](../../../plans/compositional-map-transfer.md),
[first proposal](../../../runs/2026-10-05-2039/proposal.md) and
[critique](../../../runs/2026-10-05-2039/critique.md),
[re-proposal](../../../runs/2026-10-05-2242/proposal.md).

Reopen if parked: a different reducer set or domain gives at least six cells passing the same
screens.
