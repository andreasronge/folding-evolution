---
node: questions/10-compositional-map-transfer/43-acquired-bias-vs-tree-gp
title: Frozen A8 versus family-blind subtree GP on the DG and TS rosters (retry 2, scoring seeds moved)
bank: x4-double-gate-v1 (8 spare cells) + x4-branch-sum-v1 (8 targets), saved 1717 builds; development data
---
**Retry of the approved [proposal 2239](../2026-10-10-2239/proposal.md) as implemented in [plan 2239](../2026-10-10-2239/plan.md)
(commit `6b40e16`, branch `research/2026-10-10-2239`), with one change: the scoring seed base.** Arms,
initializer, operators, budgets, counts, pairing, Stage 0, timing and solve gates, statistics, decision rule,
critic notes 1–5 of [critique 2239](../2026-10-10-2239/critique.md) and the strategy exit are carried over verbatim. Run
2239 stopped at its own seed audit before any target search ([infeasible](../2026-10-10-2239/infeasible.md),
[decision](../2026-10-10-2239/decision.md)); no slot was used.

**Question.** A8 is 6–10× cheaper than the weak G4 prior on DG cells. Does frozen native A8 keep a worthwhile
search-cost advantage over conventional, family-blind closure-based subtree GP, and at what reuse horizon would
its acquisition repay? Complete procedures, not a causal test of learning.

**Closest technique.** Closure-based subtree GP ([Koza 1992](https://www.genetic-programming.org/gpbook1toc.html))
with lexicase selection ([Helmuth 2015](https://web.cs.umass.edu/publication/docs/2015/UM-CS-PhD-2015-005.pdf)).
A8 resembles PIPE-like external distribution fitting ([Salustowicz & Schmidhuber 1997](https://pubmed.ncbi.nlm.nih.gov/10021756/))
plus literal fragment reuse; its map adapts by external fitting. A baseline test.

**The change.** The plan's seed formulas overlap: calibration `22140000 + 1000·(8f + c) + r` spans
22140000–22155007, while scoring `22150000 + 1000·(8f + c) + 2b + r` starts inside it. That means 48 seed values
are shared (96 searches each side), and both smoke seeds are TS scoring seeds. New scoring base **22180000**
(scoring 22180000–22195115; G4 offsets 100–115 unchanged). Calibration (22140000) and smoke (22160000) are
unchanged. The researcher's [prospective audit](../2026-10-10-2239/alternative-seed-audit.json) finds no overlap
with calibration, smoke or the 1 544 saved acquisition/replay seeds; no earlier run folder uses that range. The
runner's seed auditor must pass on the new constant, and its regression test must still refuse the old one.
Nothing was searched on any target cell, so no outcome has been seen.

**Feasibility (measured in 2239, development cells only).**
- Initializer: depth 1/2 bins 100% accepted, full depth 3 72.1%, grow depth 3 99.5%; six bins balanced
  43/43/43/43/42/42 in 272 draws.
- Search smoke: DG development seed solved at 6 144 evaluations; TS development seed capped (one search each).
- Ten-worker forced full-cap timing: 50.5 s (DG) and 48.5 s (TS) per search, effective concurrency 9.1.
- Planning projection with historical A8/G4 rates and 30% reserve: DG 4 048 s and TS 3 223 s against
  admission gates of 5 760 and 4 320 s. Real admission still needs the 16 A8 replays and the sustained
  256-search Stage 0. A DG calibration solve rate below 25% goes to the code reviewer before scoring.

**Arms and unit.** Per roster: native A8 24 builds × 2 seeds × 8 cells = 384; tree GP 384 on the same
(cell, seed) pairs; G4 reference 128. 1 792 scored searches; unit: the 24 build blocks.

**Cost.** Agent: change one constant and its test, replay the audits, then review and analysis; about 3–4 h in
total. Queue: preparation ≤ 25 min expected (timeout 30), DG scoring about 25–50 min, TS 10–40 min; summed
timeouts 4 h. About 39 h remain in the run.

**Primary comparison (unchanged).** DG roster: Q = cost(tree) ÷ cost(A8-D). Cost is geometric capped cost over
8 fixed cells, with failures counted at 2 × cap. Paired block bootstrap, 8 192 draws. Margin 1.5×:
- lower > 1.5 → A8 has a worthwhile advantage: price a fresh-bank comparison with both procedures frozen;
- upper < 0.67 → tree GP is worthwhile better: redirect learning toward an increment over tree search;
- interval inside [0.67, 1.5] → no difference beyond the margin: same redirect (a smaller arithmetic saving
  can still repay acquisition);
- otherwise unresolved, with a resolution price.

Search-cost verdict and acquisition repayment (arithmetic `A + N·S`, actual expenditures, unbounded where
savings are compatible with zero) are reported separately. TS Q, solves, per-cell Q, 1 × cap, tree ÷ G4,
lengths, rejection rates and seconds per search are descriptive.

**Expectations.** I expect tree GP to solve most DG searches, with Q between 0.5 and 1.5, and to be competitive
or better on TS. **Surprises:** Q lower bound > 1.5 (A8's literal joins beat whole-subtree exchange); tree GP
solving fewer DG searches than G4.

**Why this rather than strategy now.** Proposal 2239's exit clause said any failed gate parks 43 and goes to
strategy. This departs from its letter. The failed gate was a bookkeeping error in the pre-registration that
I carried over, not a measurement of either method or of cost. Strategy 2214 funded exactly this comparison
and allowed an early exit only on validity, build or cost obstacles. A strategy review now would re-buy the
same run one cycle later. If the critic judges otherwise, send it to strategy.

**Next action.** Exit to strategy after the result. If any gate fails (seed audit, replays, Stage 0 timing,
solve diagnostic, validity), park 43 with the measured obstacle and go to strategy. No further amendment of
any kind.
