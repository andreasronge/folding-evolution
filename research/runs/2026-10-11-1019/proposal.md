---
node: questions/10-compositional-map-transfer/51-source-free-donor-prior
title: Fixed source-free sum-donor prior vs acquired TS libraries on gate-sum B/C
bank: x4-gate-sum-v1 B/C (12 cells) + saved 0833 TS libraries (24 builds), development data
---
**Question.** Following [strategy 1019](strategy.md) and its [plan](../../plans/source-free-tree-donors.md): does a fixed ADD-sum donor set written from the alphabet alone keep the B/C saving of the 24 acquired TS libraries ([49](../../questions/10-compositional-map-transfer/49-tree-library-source-portability/question.md): 0.382 [0.335, 0.433] of R-tree)? TS and DG libraries share little beyond small `ADD(input, input|const)` donors yet save the same. Explanations in [51](../../questions/10-compositional-map-transfer/51-source-free-donor-prior/question.md).

**Closest known technique.** Enriching a GP primitive set with hand-chosen compound building blocks versus mining them from solved runs: run-transferable libraries ([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)), transferred subtrees in mutation ([Dinh, Chu & Nguyen 2015](https://gpbib.cs.ucl.ac.uk/gp-html/Dinh_2015_CEC.html)), in-run subroutine discovery ([Rosca & Ballard 1995](https://gpbib.cs.ucl.ac.uk/gp-html/rosca_1995_tadbb.html)), and DreamCoder's learned library against its base DSL ([Ellis et al. 2021](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf)). The acquired arm adapts by external fitting, frozen; the hand arm does not adapt. This is a **control of a known method**: what a learned library adds over a strong supplied prior, priced with acquisition.

**The prior (frozen here, before any scoring).** Alphabet `v2_x4`: inputs X0–X3, constants 0, 1, 2, 5. Two classes, ½ of library-draw mass each, uniform within class:
- *P*: `ADD(Xi, Xj)`, all ordered i ≠ j (12 entries; each unordered pair 1/12 of draws).
- *K*: `ADD(Xi, c)` and `ADD(c, Xi)`, all i and all four constants (32 entries; each input–constant pair 1/32).

Both operand orders are kept instead of canonicalizing, so no orientation is chosen (learned entries keep source order; both occur). Constant 0 is included (an existing constant; the TS libraries use it). ANY, GT, IF_GT and nested sums are excluded. Implemented as a 192-entry multiset (P × 8, K × 3) passed to the unchanged uniform library sampler; the constructor takes only the alphabet. Nothing is copied from learned libraries. Differences from TS libraries — 44 vs 3–10 distinct entries, all six pairs instead of mostly X0+X2/X1+X2 ([audit](../../questions/10-compositional-map-transfer/51-source-free-donor-prior/log.md)), constants 2 and 5 — are audited, not tuned. Validate every entry with the existing interpreter/VM check.

**Arms.** Unchanged 0833 search (restarts ≤ 8 × 65,536 evaluations, 32-token cap, mix 0.5). Experimental unit: build slot × cell × repeat, all arms sharing the attempt seeds; 24 build slots × 12 B/C cells × 6 repeats = 1,728 jobs per arm, fresh seeds disjoint from history.
- **R-tree** (contemporaneous baseline).
- **R-TS**: the 24 saved 0833 libraries, reconstructed and hash-checked.
- **R-hand**: the fixed prior in every slot (deterministic; its 24 slots are seed blocks, not acquisition replicates).

**Feasibility (measured, 0833).** Worker-s per B/C job: R-tree 6.63, R-TS 2.40; R-hand priced between them (≤ 6.63). 5,184 jobs ≈ 20–27k worker-s; 0833 ran 31.5k worker-s in 53 min (≈ 10× parallel), so ≈ **35–45 min wall**. Precision: the paired R-TS ÷ R-tree interval had a log half-width ≈ 0.13 with this block structure; R-hand, like R-tree, adds no build variance, so R-hand ÷ R-TS near 1 should give about [0.88, 1.14]. Upper < 1.25 is then reachable if the true ratio is ≤ ~1.10; lower > 1.25 if ≥ ~1.42.

**Cost.** Preparation ≤ 90 min (constructor plus a third arm in the 0833 score runner; reuse reconstruction, replay, seed audit). Timeouts: prepare 30 min, score 120 min with a stage-0 timing gate = 2.5 h ≤ 3 h. Agents ≈ 2.5 h. Total ≈ **4–5 h**.

**Primary comparison.** Mean capped evaluations R-hand ÷ R-TS on B/C (cells equal weight, failures at 524,288); 95% block bootstrap over the 24 build slots, paired. Margin 1.25: at that ratio TS saves ≈ 6.8k evaluations per search over the hand prior and repays its 0.245 M acquisition only after ≈ 36 searches, versus ≈ 6 against R-tree.
- **Retained**: upper < 1.25, *and* R-hand ÷ R-tree upper < 0.80, *and* solve difference R-hand − R-tree lower > −0.03. The hand prior becomes the comparator; the B/C case for learning reduces to supplied sums.
- **Learned increment**: lower > 1.25. TS acquisition stays the leading method on this bank.
- Otherwise **unresolved** (including a hand prior that fails to beat R-tree): report the price of resolution; no follow-up hand variants.

**Secondary (intervals, no rules).** R-hand ÷ R-tree; worker-second ratios; solve counts; per-split and per-cell ratios; per-build R-TS ÷ R-hand (which learned builds beat the prior); failure sensitivity; insertion and oversize rates by class; acquisition-plus-search cost against R-tree and R-hand over 1–200 searches.

**Expectation.** Retention, R-hand ÷ R-TS ≈ 0.9–1.15. Pair-sum supply looks like the active ingredient: R-perm, which tripled pair supply, matched R-lib ([47](../../questions/10-compositional-map-transfer/47-tree-donor-arrangement/question.md)); here half of all draws are pair sums, more than the TS libraries' ≈ 40%. Surprises: lower > 1.25 (the learned concentration on X0+X2/X1+X2 or on constants 0/1 matters), or R-hand ≈ R-tree, like R-unif's weak 0.755 ([48](../../questions/10-compositional-map-transfer/48-tree-donor-label-supply/question.md)), which would mean breadth dilutes the useful pairs.

**Next action.** The researcher implements this in a worktree from `research/main` (`28db964`). Return to strategy after the result, as the plan says. No native-TS or easy-target arm ([50](../../questions/10-compositional-map-transfer/50-library-easy-target-harm/question.md) stays parked).
