---
status: open
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

Current summary: **open after probe 2044 (commit `8a621df`; observations only, six development cells, protected
roster frozen and unsearched); a protected confirmation is priced and awaits strategy.** The chain bank is a hard
tier without a ceiling: R-tree solves 30% of jobs on the first attempt and caps 5.6%, at 159 k mean evaluations
(about 20× the easy family); the supplied 24-helper prior solves every job and costs 0.30× [0.23, 0.38] of R-tree.
The 24 saved 1938 libraries gave a small saving that is not resolved: R-all/R-tree 0.79× [0.60, 1.03]
(descriptive), below 1 in 6/6 cells but only 14/24 builds; a 40% saving is excluded, any saving and the 0.80 bar
are not. The supplied prior is 0.38× [0.27, 0.51] of R-all. By point estimate R-all's saving appears only where a
library holds at least one needed helper (confounded, few units). A protected confirmation costs about 0.6–2.5 h of
queue wall time at r = 2–4 (central to doubled tails); an "any saving" rule is decidable near the observed effect, a 0.80 rule probably not.
[Analysis](../../../runs/2026-10-11-2044/analysis.md), [decision](../../../runs/2026-10-11-2044/decision.md),
[log](log.md).

After 2044, against the explanations above: on these cells linking alone did not limit search (R-gate
never capped); acquired
helpers versus other library content are not separated, though the coverage gradient leans toward helper supply.

Related: [58](../58-signed-gate-acquisition/question.md), [57](../57-order-helper-arrangement/question.md),
[50](../50-library-easy-target-harm/question.md).

Reopen if: (when parked) strategy funds the protected confirmation priced in run 2044 (reuse the frozen bank,
method, seed namespace and 24 saved libraries; no further development search), or an acquisition recipe that
retains most needed helpers is proposed for a hard tier.
