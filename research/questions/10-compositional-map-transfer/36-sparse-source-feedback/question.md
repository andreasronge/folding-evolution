---
status: closed
tags: [compositional-transfer, acquisition-cost, solver-corpus, fragment-library, feedback, external-fitting, data-efficiency]
budget: {experiments: 1, used: 0}
---
# Can a cheap acquired bias improve its own next source batch?

Current summary: **closed after run 2026-10-09-2033: yes at this scope, with no lock-in observed
on this one update and development roster; whether the gain over static collection reaches the
worthwhile 1.10× is unresolved.** Each of 35's 64
four-attempt C4+F4 builds collected four more attempts per training cell under itself (A8) or took
four more G4 attempts (S8), then refitted C and F unchanged. A8's collection solved 92.5% of its
attempts (S8 57.6%) at 0.30× the second batch's evaluations. On then-addition, cost(S8)/cost(A8)
**1.126× [1.039, 1.220]** (16 corpora; 14/16 above 1), resolved above 1 but not against 1.10, under
every sensitivity. A8 was not resolved from the full 48-attempt pipeline: cost(full F)/cost(A8)
1.031× [0.951, 1.117], so A8 slower than full F by more than about 5% is excluded (S8 0.915×
[0.839, 0.998]). Both enlarged sources beat the four-attempt seed (1.52×, 1.35×). Counting
acquisition, A8 has lower estimated total evaluation cost than S8 at every reported horizon,
resolved through 1 024 searches (worker-seconds through 256) and repays its extra cost over the seed after about 44 searches.
Resolving 1.10 at the observed point would need about 163 corpora.

Competing explanations, as far as they were tested: (c) lock-in (biased solvers narrow the fit) is
not supported on this update and roster: σ > 1 resolved, no empty cells, libraries full (absence of
specialisation in general is not shown; [37](../37-cheap-bias-fresh-transfer/question.md) found
σ 1.173× [1.036, 1.327] again on one fresh bank). (a) yield and (b) content are not
separated: A8 had more solvers per build (24.4 vs 18.8), but S8's libraries were also at or near
cap, so library size alone does not explain it. Decoder versus library contribution is not
separated.

Scope: development sources (1246) and bank (then-addition-v1), external fitting, one update step,
capped search cost. Not transfer to a fresh bank, not a second feedback round, not inherited map
evolution.

Opened 2026-10-09 (steward, run 2033) under [strategy 2033](../../../runs/2026-10-09-2033/strategy.md)
and the [plan](../../../plans/sparse-source-feedback.md); slot 28 of root 10. Closed 2026-10-09.

Related: [35](../35-small-source-acquisition/question.md), [21](../21-iterated-solver-corpus/question.md),
[28](../28-partial-program-feedback/question.md), [proposal](../../../runs/2026-10-09-2033/proposal.md),
[analysis](../../../runs/2026-10-09-2033/analysis.md),
[decision](../../../runs/2026-10-09-2033/decision.md), [37](../37-cheap-bias-fresh-transfer/question.md), [log](log.md).

Reopen if: a decision comes to depend on adaptive collection's per-search speed over static
collection clearing 1.10× (for example a deployment where search cost dominates acquisition) and a
design can resolve it far more cheaply than about 163 corpora; or a fresh-bank or second-round test
of the adaptive pipeline needs this one-step comparison repeated as its baseline.
