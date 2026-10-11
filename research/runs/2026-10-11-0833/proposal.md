---
node: questions/10-compositional-map-transfer/49-tree-library-source-portability
title: Tree libraries rebuilt from branch-sum sources, scored on gate-sum B/C (native TS reported separately)
bank: x4-gate-sum-v1 B/C (12 cells) + x4-branch-sum-v1 (4 source cells for new tree searches; 8 target cells native), development data
---
**Question.** Following [strategy 0833](strategy.md) and its [plan](../../plans/tree-library-source-portability.md): the unchanged 0150 extractor was rebuilt only from the four DG sources. If it instead learns from the four TS sources (`A>B ? C+D : E+F`), does fresh restarted tree GP on gate-sum B/C still become clearly cheaper than R-tree? Explanations (portable recipe / DG-specific content / native-only reuse) in [49](../../questions/10-compositional-map-transfer/49-tree-library-source-portability/question.md).

**Closest known technique.** Run-transferable libraries ([Keijzer, Ryan & Cattolico 2004](https://link.springer.com/chapter/10.1007/978-3-540-24855-2_63)) and subtree transfer between GP runs ([Dinh, Chu & Nguyen 2015](https://gpbib.cs.ucl.ac.uk/gp-html/Dinh_2015_CEC.html)). The map adapts by external fitting, frozen before use; there is no inheritance. A **boundary test of a known method**; mechanism unchanged from 0150, so no new search.

**Probe (read-only, done).** I ran the unchanged `extract` (`163f005`) on saved 0024 TS R-tree solvers, using 4-cell pseudo-rosters with 8 jobs per cell ([log](../../questions/10-compositional-map-transfer/49-tree-library-source-portability/log.md)). It gives **2–11 entries (median 6)**: pair sums, single-input `GT(Xi,Xj)`, input+constant sums, and **no 7-node predicate**. TS libraries are DG libraries minus the comparison skeleton: [48](../../questions/10-compositional-map-transfer/48-tree-donor-label-supply/question.md) tied the B/C gain to the ADD-heavy label law; [47](../../questions/10-compositional-map-transfer/47-tree-donor-arrangement/question.md) left a relabelled-skeleton route open.

**Acquisition.** Run the 0150 policy unchanged on `TS.split.source` (1717 `banks.json`). Each build gets 8 R-tree jobs per source cell (≤ 8 × 65,536 evaluations each, exact D625), giving **24 independent builds** on new seeds. Use the same extractor (proper subtrees, 3–9 nodes, contains an input, ≥ 2 source cells, deterministic rank, cap 16), frozen before collection. Small/empty libraries stay (ordinary fallback); failures charged.

**Arms (scoring, shared attempt seeds within each build slot × cell × repeat).**
- *Gate-sum B/C* (12 cells × 24 builds × 6 repeats = 1,728 jobs per arm):
  - **R-tree**;
  - **R-TS** (new libraries);
  - **R-DG** (the saved 0150 libraries, the current acquired reference);
  - **R-sizeTS**: size- and length-matched random donors per TS library, built by 0150's `controls`. About 15 min; separates learned content from donor size, which decides whether source learning earned its acquisition.
- *TS native* (the 8 target cells × 24 × 4 = 768 jobs per arm): R-tree, R-TS, R-DG. These are separately reported and never pooled.

**Feasibility (measured).**
- TS R-tree ([0024](../2026-10-11-0024/analysis.md)): 6,672 mean evaluations, 0.49 worker-s, 748/768 solved on the first attempt.
  - Acquisition ≈ 32 × 6.7k ≈ **0.21 M evaluations per library**, 13× cheaper than DG's 2.88 M.
- B/C worker-s per job ([0652](../2026-10-11-0652/proposal.md)): R-tree 6.84, R-lib 2.25, R-size 5.40.
  - B/C total ≈ 39k worker-s (R-TS and R-sizeTS priced as R-tree); native ≈ 2k.
  - That is **≈ 70 min wall at 10×**, matching 0652's 8,640 jobs in 61 min.
- Precision: 0652's R-lib ÷ R-tree at this size was 0.388 [0.328, 0.456], a half-width of about ±17% on the ratio.

**Cost.** Timeouts: prepare + acquire + validation 45 min, scoring 150 min with a stage-0 timing gate (3.25 h ≤ 4 h). Preparation ≤ 120 min. Validation:
0150 off-path replay, interpreter/VM agreement per entry, seed disjointness, source/target separation. Agent time ≈ 4–5 h; total ≈ 6–8 h.

**Primary comparison.** Mean capped evaluations R-TS ÷ R-tree on B/C (cells equal weight, failures at 524,288). The interval is a 95% block bootstrap over the 24 build slots. Guard: solve-fraction difference lower bound > −0.03.
- **Portable**: upper < 0.80 and guard passes. Return to strategy for the choice between the unfamiliar-content boundary and a simpler statistical generator.
- **Not portable to B/C**: lower > 0.80 (a saving ≥ 20% excluded). Read native TS: R-TS ÷ R-tree upper < 0.80 there means a reuse limit; otherwise it limits this extractor/source policy.
- Otherwise: unresolved. Report the price of resolution.

0.80 because generic donors already reach 0.76–0.86 on B/C (R-unif, R-size).

**Secondary, reported with intervals, no rules.**
- R-TS ÷ R-sizeTS (content beyond size).
- R-TS ÷ R-DG (independent cohorts; TS need not beat DG).
- Native-TS ratios and per-cell and per-build ratios.
- Library audit: size, pair sums by split, predicates, insertion and oversize rates.
- Acquisition-plus-search curves in evaluations and worker seconds against R-tree and R-DG, with TS and DG acquisition each charged.

**Expectation.** R-TS ÷ R-tree ≈ 0.4–0.6 on B/C, a little weaker than R-DG (fewer recurring pair sums: in the TS formulas only X0+X2 and X1+X2 recur across cells). R-TS should be resolved below R-sizeTS. Because acquisition is ~13× cheaper, repayment should come within roughly 5–10 searches. On native TS, which is near-solved on the first attempt, I expect a small gain (0.6–1.0) and possibly harm from 32-token crowding.

What would surprise me:
- R-TS ≥ 0.8 with R-DG ≈ 0.4. That would mean DG's skeletons, not pair-sum supply, carried B/C, contradicting the 48 reading.
- R-TS ≈ R-sizeTS.

**Next action.** The researcher implements this in a worktree from `research/main` (`163f005`). Return to strategy after the result.
