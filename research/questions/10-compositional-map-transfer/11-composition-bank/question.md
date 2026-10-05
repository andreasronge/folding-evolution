---
status: open
tags: [compositional-transfer, task-bank, feasibility, decoder, stack-tape, reduce-min]
budget: {experiments: 1, used: 0}
---
# Is there a tractable bank of held-out reducer/combiner compositions with room for a learned decoder?

Current summary: Unmeasured as a bank; steward probes only (unreviewed, one run each).
Two attempts (runs 2026-10-05-2039 and 2026-10-05-2242) were blocked by the same merge
conflict before any code ran; the steward resolved it on `research/main` (merge `823bc27`)
and re-proposed the study as run 2026-10-05-2247. Slot not yet charged.
The plan's candidate bank (SUM/MAX/ANY with ADD and GT on signed length-4 lists) mostly fails
the alias check: ANY is 1 on 624 of 625 inputs, so every ANY task is within one input of a
constant-substituted single-reducer task, and every GT comparison agrees ≥ 96.6% with a
single-reducer threshold, i.e. the old threshold family. For integer-valued compositions
(X+Y, 2X+Y, "S>0 ? X : Y") of SUM, MAX and MIN, label-vector probes against the listed simple
comparator families (single, doubled and constant-shifted reducers, two-reducer sums,
constants) found at most 69% agreement; selects conditioned on MAX or MIN were 87–98% and are
excluded. Exhaustive shorter-program screening is pending, and MIN has no executor yet, so
nothing about MIN cells has been searched. Among the four MIN-free probe cells, uniform
evolution on the stack tape (P 256, lexicase) solved 6/6, 8/8, 7/8 and 4/8 runs by 524k
evaluations; successful runs often solved in tens of thousands.

Competing explanations for a failure here (each is about this design, not root 10's answer):
- Bank: too few cells survive exhaustive alias and near-alias screens for a crossed split.
- Tractability: held-out cells are too hard for uniform evolution at the measured budget.
- Headroom: a hand-set, task-agnostic grammar decoder already solves held-out cells almost
  at once, leaving no room for learned family structure.
- Cost: the nested adaptation loop needed next does not fit an 8-hour queue.

Related: [root 10](../question.md), [plan](../../../plans/compositional-map-transfer.md),
[first proposal](../../../runs/2026-10-05-2039/proposal.md) and
[critique](../../../runs/2026-10-05-2039/critique.md),
[second proposal](../../../runs/2026-10-05-2242/proposal.md) and
[critique](../../../runs/2026-10-05-2242/critique.md),
[third proposal](../../../runs/2026-10-05-2247/proposal.md).

Reopen if parked: a different reducer set or domain gives at least seven cells (the minimum for an
eligible split) passing the same screens.
