---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, acquisition-cost, signed-gates, semantic-keying, fresh-content, fresh-bank]
budget: {experiments: 1, used: 0}
---
# Does the frozen uncapped semantic recipe (R-all) acquire useful bias for signed gates on a fresh bank?

Opened 2026-10-11 by the steward on [strategy 1938](../../../runs/2026-10-11-1938/strategy.md) and the
[signed-gate plan](../../../plans/signed-gate-content-acquisition.md). This is the fresh-family portability test
that [54](../54-rectified-sum-acquisition/question.md) (rectifiers, probe only) could not reach. It meets
[45](../45-tree-subtree-library/question.md) (iii) if its protected roster, frozen with the method, is scored.

Bank `x4-signed-gate-v1` (new): `v2_x4` on D625, with helpers `p(a,b) = Xa>0 ? Xb : 0` and its complement `n`.
Sources are `p/n(a,b)+(Xc+Xc)` (48 cells); destinations are `p(a,b)+n(c,d)` with all four indices distinct
(24 cells). Arms: R-tree, new R-all, the transported 1228 R-all order libraries, and a supplied R-gate prior.

Current summary: **closed after experiment 1938 (commit `9da9c2c`): yes, on this family.** On 18 never-searched
protected cells frozen with the method, 24 new R-all acquisitions cost **0.577× [0.47, 0.72]** of R-tree in pooled
capped mean evaluations (pre-stated rule: upper < 0.80, met), below 1 in 18/18 cells and 22/24 builds, all 1,728 jobs
solved in every arm (no solve loss observed). The new libraries also beat the transported 1228 order libraries,
0.516× [0.44, 0.61]; those showed no saving here (1.12× [0.94, 1.34] of R-tree: a 20% saving excluded, harm
unresolved). The supplied
24-helper prior was 0.246× [0.21, 0.30] of R-tree, 2.3× cheaper than R-all. Libraries kept 8.6 of 24 helpers on
average; the saving was larger where needed helpers were present (descriptive, confounded) but did not vanish
where none were. Repays acquisition after about 66 [46, 110] searches. Scope: input rebindings of one construction,
easy destinations (R-tree 97.7% first attempt), one extractor, mix and restart schedule. Not shown: helper
causality, the hard tier, or families unlike these two.
[Analysis](../../../runs/2026-10-11-1938/analysis.md), [decision](../../../runs/2026-10-11-1938/decision.md).

Stage 0 (off-harness, observations only, [notes](../../../runs/2026-10-11-1938/stage0/README.md)):
- 37% of evolved sources contain their own helper (rectifiers: 8.9%).
- Two R-all builds retained 11/24 and 6/24 helpers.
- Destinations are easy (R-tree 12/12 first attempt, ~5 k evaluations), and every library was cheaper there.

Competing explanations for a saving:
- (a) acquired signed-gate content;
- (b) generic small-subtree donors, which any library supplies (transported order libraries test this);
- (c) easy targets, where any near-ready material is inserted quickly.

Competing explanations for no saving:
- (d) helpers rarely retained in pairs;
- (e) the four probe cells were unrepresentative.

After 1938: (b) is ruled out as the whole story for the order libraries (no saving; a 20% saving excluded); (e) did not occur
(development 0.58, protected 0.58); (a) versus other content in the same libraries (other-index p/n forms, small
ADD entries) and (c) are not separated.

Related: [53](../53-order-library-cap-release/question.md) (recipe), [56](../56-order-library-protected-cells/question.md)
(order protected result), [54](../54-rectified-sum-acquisition/question.md) (rectifier probe),
[50](../50-library-easy-target-harm/question.md) (easy-target harm; its ≥ 90% condition is met here),
[51](../51-source-free-donor-prior/question.md) (supplied prior), [log](log.md).

Reopen if: a decision needs helper causality for signed gates (e.g. a helper-entry rearrangement as in
[57](../57-order-helper-arrangement/question.md)), the hard tier of this family, or the reason the extractor keeps
only a third of the helpers; reuse the saved 1938 libraries and rows. The 1938 protected cells are now seen.
