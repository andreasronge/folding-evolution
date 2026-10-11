---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, signed-gates, hard-tier, assembly-depth]
budget: {experiments: 1, used: 0}
---
# Do frozen signed-gate libraries help where assembling linked conditionals is hard?

Opened 2026-10-11 by the steward on [strategy 2044](../../../runs/2026-10-11-2044/strategy.md) and the
[signed-gate composition-depth plan](../../../plans/signed-gate-composition-depth.md). Follows
[58](../58-signed-gate-acquisition/question.md), whose saving (R-all 0.577× of R-tree) came from easy targets
(R-tree 97.7% first attempt).

Bank `x4-signed-chain-v1` (new): `v2_x4` on D625, destinations `p(a,b)+n(b,c)+p(c,d)` over the 24
permutations of four indices, `p(a,b) = Xa>0 ? Xb : 0`, `n` its complement. Three linked conditional pieces,
versus two disjoint ones in 58. No new sources: the 24 saved 1938 R-all libraries are reused unchanged, against
R-tree and the supplied 24-helper R-gate prior.

Competing explanations for any R-all saving or its absence:
- the acquired helpers (partial: a build holds all three needed helpers for 3% of cells) shorten assembly;
- other library content (pair sums, conditionals) helps generically, as 58's no-helper stratum suggested;
- harder assembly is limited by linking, not supply, so neither acquired nor supplied helpers help much.

Current summary: **closed; answered by its protected confirmation
[60](../60-signed-chain-protected-reuse/question.md): yes, modestly, on this bank.** On the 18 never-searched protected
cells (run 2150, commit `83c7c5b`) the saved 1938 libraries cost R-all/R-tree **0.778× [0.696, 0.870]** (pooled capped
mean evaluations; 0.80 bar unresolved) and repay acquisition after about 5 [3.8, 9.7] searches; the supplied 24-helper
prior costs 0.263× [0.233, 0.296] of R-tree and 0.338× [0.298, 0.383] of R-all. This question's own probe (2044,
commit `8a621df`; observations on six development cells, four chosen in stage 0) saw a hard tier with 5.6% R-tree
capping, below the pre-set 25% cap-dominance flag (30% first-attempt solves, 159 k mean evaluations, about 20× the easy
family), and R-all/R-tree 0.79× [0.60, 1.03], unresolved; its descriptive lower cost-ratio bound was about 0.60. The
probe's forecast gave a meaningful but uncertain chance of resolving any saving at r = 4; the protected run resolved
it with a narrower interval than forecast.
[Probe analysis](../../../runs/2026-10-11-2044/analysis.md), [decision](../../../runs/2026-10-11-2044/decision.md),
[confirmation analysis](../../../runs/2026-10-11-2150/analysis.md), [log](log.md).

Against the explanations above, after 2044 and 2150: the supplied repertoire substantially reduced cost on these
cells, contradicting the prediction that supplying helpers would help little; residual assembly cost and helper
causality remain unresolved (R-gate still restarted on 35% of protected jobs). Acquired helpers versus other library
content are not separated, but on protected cells the no-helper stratum saved nothing (R-all/R-tree 0.98 on 456
jobs, against 0.77 on 1938's easy cells), so the generic-content reading is weaker here than on the easy family
(descriptive, confounded with library size).

Related: [60](../60-signed-chain-protected-reuse/question.md), [58](../58-signed-gate-acquisition/question.md),
[57](../57-order-helper-arrangement/question.md), [50](../50-library-easy-target-harm/question.md).

Reopen if: an acquisition recipe that retains most needed helpers (1938 kept 206 of 576 helper × build slots) is
proposed for a hard tier, or a helper ablation is needed to choose between acquisition procedures.
