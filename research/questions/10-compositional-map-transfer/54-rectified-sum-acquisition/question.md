---
status: parked
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, acquisition-cost, rectified-sums, semantic-keying, fresh-content]
budget: {experiments: 1, used: 0}
---
# Does the frozen uncapped semantic recipe (R-all) acquire useful bias for a different computation, rectified pair sums?

Opened 2026-10-11 by the steward on [strategy 1315](../../../runs/2026-10-11-1315/strategy.md) and the
[rectified-sum plan](../../../plans/rectified-sum-acquisition.md). Fresh-family work after
[53](../53-order-library-cap-release/question.md); meets the condition in [45](../45-tree-subtree-library/question.md) (iii)
only if a protected roster frozen with the method is later scored.

Current summary: **parked after probe 1315 (commit `4a60cc7`; observations only, six development cells,
protected roster never searched).** Under this source design the frozen recipe acquired no rectifier helper and
saved nothing. Sources `pos/neg(a,b)+Xc` are easy (384/384 solved, ~166 k evaluations per build) but are mostly
solved through the three-input sum (`a+b+c` in 326/384, IF_GT-rooted 335/384); only 34/384 solvers contain their own
helper, 9/384 at an emittable size, and no helper both recurred and fit the 3–9-node window (0/96 helper × build
pairs). So R-all held a needed helper in **0/48** cell × build pairs and cost **1.03× [0.96, 1.10]** of R-tree in
capped arithmetic mean evaluations; the transported order libraries cost 1.04× [1.00, 1.08]. Supplied helpers
(R-rect) did help: 73/96 solved against R-tree's 20/96, **0.57× [0.50, 0.64]**, below the probe's 0.5 / 90%
investment threshold. Destinations are hard and cap-bound (66/96 R-all/R-tree units double-capped), so capped
means, not time to solution, are what was measured. Stage 0 (off-harness, [notes](../../../runs/2026-10-11-1315/stage0/README.md))
is reproduced on-harness ([analysis](../../../runs/2026-10-11-1315/analysis.md)).

Competing explanations for a failure of R-all here, and where the probe leaves them (observations):
(a) **little acquisition opportunity**: sources admit a helper-free route, so recurrence pooling has little to keep —
consistent: the loss is at the source (8.9% own-helper census), before the recurrence rule and size filter;
(b) **no headroom**: too strong — supplied helpers cut capped cost 43% and solve 3.7× as often, but 23/96 still cap;
(c) both: the advisory rule failed on coverage, headroom threshold and saving. Not shown: that rectifiers cannot be
acquired under a source design that forces the helper, or what R-all would do with helpers in the pool here.

Related: [53](../53-order-library-cap-release/question.md) (recipe and order result),
[52](../52-order-helper-acquisition/question.md) (cap located), [45](../45-tree-subtree-library/question.md),
[50](../50-library-easy-target-harm/question.md) (harm), [51](../51-source-free-donor-prior/question.md) (supplied prior),
[proposal](../../../runs/2026-10-11-1315/proposal.md), [analysis](../../../runs/2026-10-11-1315/analysis.md),
[decision](../../../runs/2026-10-11-1315/decision.md), [log](log.md).

Reopen if: (parked) strategy funds a rectifier source design whose solvers must build the helper (e.g. sources
where the three-input-sum route is unavailable, with a stage-0 own-helper census ≥ 25% before any scoring), or a
changed acquisition method (e.g. parameterized abstraction) proposes this bank as its test; or a decision needs
the supplied-prior headroom at a larger restart cap. Reuse the saved 1315 rows, census and libraries for
descriptive follow-ups without new search. The 24 protected cells remain unsearched.
