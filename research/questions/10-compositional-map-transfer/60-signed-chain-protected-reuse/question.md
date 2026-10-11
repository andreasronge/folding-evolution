---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, signed-gates, hard-tier, protected-confirmation]
budget: {experiments: 1, used: 0}
---
# Do the frozen signed-gate libraries reduce search cost on the protected signed-chain cells?

Opened 2026-10-11 by the steward on [strategy 2150](../../../runs/2026-10-11-2150/strategy.md) and the
[confirmation addendum](../../../plans/signed-chain-protected-reuse.md). Confirms the development observation of
[59](../59-signed-chain-depth/question.md) (probe 2044: R-all/R-tree 0.79 [0.60, 1.03], R-gate/R-tree 0.30,
R-tree 30% first attempt) on the 18 protected `x4-signed-chain-v1` cells, frozen with the method in 2044 and
never searched. Same 24 saved 1938 libraries, R-tree and R-gate; no new acquisition.

Competing explanations for the outcome:
- the frozen libraries' content (partly the needed helpers) shortens linked assembly on unseen chain cells too;
- the development saving was seed luck or cell selection (four of six cells chosen in stage 0), and protected
  cells show none;
- the saving exists but is under 20%, too small to repay acquisition at practical reuse horizons.

Current summary: **closed, answered for this bank: the frozen libraries gave a modest resolved saving on the
18 never-searched protected cells** (run 2150, commit `83c7c5b`; 24 builds × 18 cells × 4 repeats, 1,728 paired
jobs per arm). R-all/R-tree **0.778× [0.696, 0.870]** in pooled capped mean evaluations (pre-stated rule: upper
< 1.00, met), worker seconds 0.761× [0.680, 0.848]; below 1 in 18/18 cells (0.67–0.94) and 20/24 builds. The 0.80
bar is unresolved: a saving of 13–30% is compatible, so ">20%" is neither established nor excluded. All three
validity checks passed: R-tree 27.0% first-attempt solves, 6.8% capped (hard tier, not cap-dominated), R-gate
1,728/1,728 solved. Solves +2.7 points [+0.5, +5.0] for R-all. The supplied 24-helper prior stays far ahead:
R-gate/R-tree 0.263× [0.233, 0.296], R-gate/R-all 0.338× [0.298, 0.383]. Saving per search 39.6 k [22.2 k,
57.1 k] evaluations against 216 k charged acquisition per build: repaid after **5.4 [3.8, 9.7] searches**
(66 on the easy 1938 cells). Needed-helper coverage (descriptive, confounded with library size and build):
R-all/paired R-tree 0.98 / 0.78 / 0.59 / 0.42 with 0 / 1 / 2 / 3 of a cell's three helpers present (456 / 792 /
436 / 44 jobs). Scope: held-out cells of a development bank (`x4-signed-chain-v1`, frozen with the method in
2044), one acquisition recipe and search regime, capped costs; not fresh-bank transfer, not helper causality;
depth and input sharing change together relative to the easy bank.
[Analysis](../../../runs/2026-10-11-2150/analysis.md), [decision](../../../runs/2026-10-11-2150/decision.md),
[log](log.md).

Against the explanations above: seed luck or cell selection in the development probe is not supported (protected
point 0.78 against development 0.79, every protected cell below 1); a saving under 20% is not excluded, but
repayment within about 10 searches does not depend on it being larger.

Related: [59](../59-signed-chain-depth/question.md), [58](../58-signed-gate-acquisition/question.md),
[56](../56-order-library-protected-cells/question.md), [57](../57-order-helper-arrangement/question.md),
[54](../54-rectified-sum-acquisition/question.md).

Reopen if: a changed acquisition recipe or donor policy needs a deployment readout on this hard tier (the
protected cells are now searched, so such a readout would be development data; a transfer claim needs a fresh
bank).
