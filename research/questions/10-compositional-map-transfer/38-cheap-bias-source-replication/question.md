---
status: closed
tags: [compositional-transfer, acquisition-cost, source-robustness, solver-corpus, fragment-library, external-fitting]
budget: {experiments: 1, used: 0}
---
# Does the cheap adaptive acquisition (A8) stay useful when rebuilt from different source compositions?

Current summary: **closed after run 2026-10-10-0145: rebuilt from the complementary source roster,
the unchanged A8 recipe again gave a clearly useful frozen bias; whether it is as good as the
original builds is unresolved.** A8 (four G4 attempts per source cell → C4+F4, four more attempts
under that bias → refit) had only been built from the comparison-gate *training* cells. Sixteen
fresh builds (8 per family) from the four former holdout cells per family, scored on `two-sum-v1`
(16 cells × 4 seeds): cost(G4)/cost(A8′) **2.50× [2.17, 2.85]** (pre-set usefulness margin 1.5×;
1× cap 2.06×; BE 3.14× [2.61, 3.71], PA 1.99× [1.66, 2.32]; 16/16 builds below G4). Against the
historical A8 artifacts on identical target keys, cost ratio **1.09× [0.90, 1.32]**: not resolved,
so neither equality nor a loss is shown. The PA builds were weaker than their historical
counterparts (217 vs 249 of 512 solved; three PA builds about 2× costlier), unexplained.
Acquisition was cheaper than historical (4.5 M vs 6.5 M evaluations; adaptive batch 255/256
solved) and repays against G4 after about 35 [30, 43] searches in evaluations; worker-second
economics are not established (calibration artifact, see log).

Competing explanations, as tested: (a) roster-robust within these families: supported for this one
alternative roster (useful, not resolved from historical); (b) success depended on favourable
sources: a fall below 1.5× is excluded, a loss up to about 30% against historical A8 is not;
(c) the new roster teaches both policies poorly: untested, because the static S8′ builds were made
but not scored (a biased timing projection dropped them).

Scope: one complementary roster inside the same two families, development data on both sides
(sources were scored targets in 25; two-sum-v1 was scored in 37); D1331; external fitting;
decoder, library, yield and content bundled. Not a fresh-bank, new-family, arbitrary-source-set or
inherited-adaptation claim.

Opened 2026-10-10 (steward, run 2026-10-10-0145) under
[strategy 0145](../../../runs/2026-10-10-0145/strategy.md) and the
[plan](../../../plans/cheap-bias-source-replication.md); slot 30 of root 10. Closed 2026-10-10.

Related: [37](../37-cheap-bias-fresh-transfer/question.md), [36](../36-sparse-source-feedback/question.md),
[35](../35-small-source-acquisition/question.md), [25](../25-comparison-gate-transfer/question.md),
[proposal](../../../runs/2026-10-10-0145/proposal.md),
[analysis](../../../runs/2026-10-10-0145/analysis.md),
[decision](../../../runs/2026-10-10-0145/decision.md), [log](log.md).

Reopen if: a decision comes to depend on where the weaker PA builds come from (score the 16 S8′
artifacts already built in the 0145 prepare output, ~35 min, with a timing batch of ≥ 64 searches
or effective workers taken from collection), or on equality with the historical builds (at δ's
observed point and spread, about 65 builds to exclude a 20% loss); or the recipe
is carried to a new family whose sources fail.
