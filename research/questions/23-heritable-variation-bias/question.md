---
status: parked
tags: [map-bias, self-adaptation, inheritance, variation, op-frequencies, task-family, fresh-start]
budget: {experiments: 2, used: 0}
---
# Can inherited token-generation frequencies learn a useful bias through program selection and transfer it to fresh populations?

Current summary: Answered for one procedure, negatively (run 2026-10-08-1046, code `a804f4f`,
pre-registered). Each program carried θ, inherited with N(0, 0.03²) per component; 20
acquisitions per family × arm, 48 episodes × 128 generations, then each final vector frozen
and scored on 16 fresh seeds per training target. Uniform ÷ inherited cost: sum 0.33
[0.21, 0.53] (inherited resolved worse than uniform), max 0.73 [0.50, 1.06] (a gain above
1.06× excluded). Bounded in both families. The hand scaffold is 11.9× [7.0, 20.4] (sum) and
5.75× [3.66, 8.95] (max) cheaper than inherited. Persistent ancestry beat shuffled ancestry on
max (broken ÷ inherited 1.58 [1.04, 2.36], resolved); on sum the linkage effect is
unresolved (1.00 [0.69, 1.41], appreciable effects either way not excluded). On max it made
vectors less costly than shuffled ancestry without establishing a gain over uniform. Scope: one modifier law,
σ = 0.03, this exposure schedule, development bank `tag-threshold-v1`, training targets only,
fixed token meanings. It bounds this procedure, not self-adaptation. Post hoc (log only):
final vectors concentrate on run-specific tokens; acquisition and frozen solves correlate
0.59–0.85 within cells (shared-seed confounded); drift versus selection was not isolated.
Earlier runs 2243 and 0843 stopped at cost gates; 0918 ran acquisition but a hidden deadline
blocked scoring, and 1046 completed it. Both arms reached similar observed mean distances
from uniform (L1 0.90–0.93) in 0918; that is not evidence of equal drift or direction.

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
[run 1046 analysis](../../runs/2026-10-08-1046/analysis.md) and
[decision](../../runs/2026-10-08-1046/decision.md),
[self-adaptation, Stephens et al. 1998](https://pubmed.ncbi.nlm.nih.gov/9847423/),
[root-10 reserve plan](../../plans/comparison-gated-transfer.md),
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
stopped on a build defect, so it went to strategy with a recommended recovery run. Run 1046
completed it (2 of 2 used) and the question was parked; see the explanations' status below.

Status of the explanations after 1046 (this procedure only): A not supported (Acquired
excluded in both families); C not supported (no gain over uniform established; above 1.06× excluded on max); B fits sum, while on max
linkage had a resolved but not useful effect; D not separable (resident benefit not
measured); E open as a redesign hypothesis, unmeasured.

Reopen if: a changed inheritance, mutation-scale or exposure rule comes with a measured
selectable signal that this procedure lacked (e.g. a cheap acquisition probe whose frozen
vectors beat uniform on training targets at a resolved bound, or a mutation-only control
showing that selection, not drift, moves the vectors); a new bank makes a learned frequency
bias useful beyond a hand-set scaffold; or a later decoder-inheritance experiment needs a
specific frequency-only control (this run's acquisitions and scoring harness can serve).
Mere vector movement, the post hoc acquisition/frozen correlation, more seeds under the same
procedure, or available compute does not meet this condition.
