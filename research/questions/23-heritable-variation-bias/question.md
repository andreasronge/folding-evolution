---
status: open
tags: [map-bias, self-adaptation, inheritance, variation, op-frequencies, task-family, fresh-start]
budget: {experiments: 2, used: 0}
---
# Can inherited token-generation frequencies learn a useful bias through program selection and transfer it to fresh populations?

Current summary: Untested; no primary measurement yet. Three runs of the same mechanism:
run 2026-10-07-2243 (early-stopped episodes) stopped at an over-strict worst-search cost gate;
in its single sum timing pair the less successful broken arm received about 3× as many
generations under early stopping (5 053 vs 1 679; max 5 793 vs 5 624). Run 2026-10-08-0843
(equal 128-generation episodes, uniform as primary reference, code `c01f16d`) missed a 3 h
timeout ceiling by 68 s. Run 2026-10-08-0918 (same design, 16 reference seeds, code `511711c`)
executed: 79 of 80 acquisitions completed, but one max acquisition was cut by a hidden 1 200 s
per-job deadline. The completeness check correctly blocked scoring, so no frozen search ran.
Acquisition observations only (not evidence): no resolved inherited − broken difference in
within-acquisition solves (sum −0.6 [−7.5, +6.0], max +4.1 [−1.3, +9.5] of 48). Both arms drifted
equally far from uniform (L1 ≈ 0.9), as the σ = 0.03 walk alone would produce. Solve rate fell over
the 48 episodes in every cell.
Background: root 01 established that externally fitted frequencies speed TAG
threshold search and that a hand-set INPUT/GT/aggregator scaffold performs comparably;
root 10 established outer-selected token transfer and useful externally fitted context.
Neither tested a frequency vector inherited with each program and selected only through
that program's descendants. This root tests that mechanism with fixed token meanings,
against uniform, broken ancestry and the hand-set scaffold.

Competing explanations:
- A: Persistent association between a program lineage and its variation bias lets selection
  accumulate a useful bias; after programs are discarded, the frozen bias improves fresh
  search, including on the withheld member of its training family.
- B: Vectors move by drift or hitchhiking with good tapes. The inherited procedure produces
  no useful frozen-search increment over an ancestry-broken control at a resolved bound.
- C: Selection learns generic token supply, or recovers the known scaffold. Frozen transfer
  improves over uniform but does not establish family specificity or a practical gain over
  the hand-set benchmark.
- D: The bias serves its resident programs or training targets; it does not remain useful
  when programs are reset, or suppresses the constant needed by the withheld target.
- E: This inheritance rule, mutation scale or task exposure provides too little selection
  signal at the affordable effort. A bounded failure limits the procedure, not self-adaptation.

Related: [concept plan](../../plans/heritable-variation-bias.md),
[opening strategy](../../runs/2026-10-07-2243/strategy.md),
[run 2243 stop](../../runs/2026-10-07-2243/infeasible.md) and
[decision](../../runs/2026-10-07-2243/decision.md),
[equal-exposure addendum](../../plans/heritable-bias-equal-exposure.md),
[run 0843 stop](../../runs/2026-10-08-0843/infeasible.md) and
[decision](../../runs/2026-10-08-0843/decision.md),
[run 0918 analysis](../../runs/2026-10-08-0918/analysis.md) and
[decision](../../runs/2026-10-08-0918/decision.md),
[owner note](../../plans/owner-heritable-map.md),
[01 map bias](../01-map-bias/question.md),
[08 fitted frequency transfer](../01-map-bias/08-evolve-bias/question.md),
[09 generic frequency gain](../01-map-bias/09-generic-bias-speedup/question.md),
[10 compositional transfer](../10-compositional-map-transfer/question.md).

Allocation: two experiments through the next strategy review, at most 8 queue hours and
about 6 h of agent work/contingency. Return earlier after a feasibility-only result or a
build/cost failure. The steward sets the actual experiment design and sizes.
After the 68 s overrun in 0843 the steward re-proposed directly instead of returning to
strategy (reasons in [decision 0843](../../runs/2026-10-08-0843/decision.md)); any further
cost or build stop on this design goes to the strategist. Run 0918 executed (it counts as 1 of 2) and
stopped on a build defect, so it went to strategy with a recommended recovery run.

Reopen if parked or closed: a changed inheritance/exposure rule has evidence of selectable
benefit that the tested procedure lacked; a new bank makes a learned frequency bias useful
beyond a hand-set scaffold; or a later decoder-inheritance experiment needs a specific
frequency-only control. Mere vector movement, more seeds under one learned vector, or
available compute does not meet this condition.
