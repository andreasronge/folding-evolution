---
node: questions/10-compositional-map-transfer/43-acquired-bias-vs-tree-gp
title: Frozen A8 versus family-blind subtree GP on the DG and TS rosters (retry, corrected initializer)
bank: x4-double-gate-v1 (8 spare cells) + x4-branch-sum-v1 (8 targets), saved 1717 builds; development data
---
**Retry of the approved [proposal 2214](../2026-10-10-2214/proposal.md) and [plan 2214](../2026-10-10-2214/plan.md).**
The design, arms, seeds, gates, statistics and decision rule are carried over unchanged, including the
critic's notes 1–5 as implemented in plan 2214. Two parts of the initializer change; nothing else. The first
attempt stopped before any search ([infeasible](../2026-10-10-2214/infeasible.md), [decision](../2026-10-10-2214/decision.md));
no slot was used.

**Question.** A8 is 6–10× cheaper than G4 on DG cells, but G4 is a weak tape prior. Does frozen native A8
keep a worthwhile search-cost advantage over a conventional, family-blind structural prior, and at what
reuse horizon would its acquisition repay? This compares complete procedures. It is not a causal test of
learning and not a test of strong typing.

**Closest technique.** Closure-based subtree GP ([Koza 1992](https://www.genetic-programming.org/gpbook1toc.html);
typing background [Montana 1995](https://davidmontana.net/papers/stgp.pdf)) with lexicase selection
([Helmuth 2015](https://web.cs.umass.edu/publication/docs/2015/UM-CS-PhD-2015-005.pdf)). A8 is PIPE-like
external distribution fitting ([Salustowicz & Schmidhuber 1997](https://pubmed.ncbi.nlm.nih.gov/10021756/))
plus literal fragment reuse; its map adapts by external fitting. This is a baseline test: both methods are
known, and the experiment tells us which procedure deserves broader testing.

**What changes (initialization only).**
1. Ramped half-and-half over depths **1, 2, 3 edges** (2–4 levels; root alone is depth 0), six bins
   (depth × full/grow), equally allocated and shuffled. Before: 2–4 edges, whose full-depth-4 bin accepts
   1.2 × 10⁻⁷ of draws under the 32-token cap.
2. **Grow draws the root from the function set** (Koza's grow). Below the root it picks a terminal with
   probability 0.5, as before. Before, the root could be a terminal, which made about a quarter of the
   initial population single terminals.

Unchanged: uniform functions ADD/GT/IF_GT and terminals X0–X3, ANY, 0/1/2/5, same-bin resampling bounded at
10 000 draws, subtree mutation as a fresh grow subtree of depth ≤ 3 edges (root may be a terminal, as
frozen), one-offspring subtree crossover, oversize child reverts to parent 1, compiled length ≤ 32. Both
targets lie within the initial depth range (TS canonical depth 2, DG depth 3; 16 tokens each). Neither
change uses target information. Code: commit `3e961ad` (branch `research/2026-10-10-2214`); the change is the
`depths` tuple and the root rule in `random_tree`/`initialize`, plus tests.

**Feasibility (measured today, read-only on `3e961ad`, 20 000 draws per bin).** Acceptance: depth 1 and 2
bins 100%; full 3 71.9%; grow 3 99.5%. A P256 population takes 274 draws in 2 ms. Median compiled length:
full 5/11/25, grow 5/8/12 tokens. Search-loop throughput is still unmeasured. It is gated exactly as in plan
2214: a complete search smoke, 16 A8 replays, and Stage 0 (256 calibration searches on source/development
cells choosing the 0.9/0.1 or 0.5/0.5 mix). Admission requires projected scoring ≤ 80% of timeouts at
sustained ten-worker concurrency with full-cap tails. A DG calibration solve rate < 25% goes to the code
reviewer before scoring.

**Arms and unit.** Per roster (8 cells): native A8 24 builds × 2 fresh seeds × 8 cells = 384; tree GP 384
on the same (cell, seed) pairs; G4 reference 128. 1 792 scored searches. Unit: 24 build blocks; tree rows
are independent searches, never reused across blocks.

**Cost.** Agent: build change and validation about 30–45 min (the code exists), then review and analysis,
about 4–5 h in total. Queue: preparation ≤ 25 min expected (timeout 30), DG scoring about 25–50 min, TS
10–40 min, summed timeouts 4 h. Fits in the ~39 h left.

**Primary comparison (unchanged).** DG roster: Q = cost(tree) ÷ cost(A8-D), geometric capped cost over 8
fixed cells, failures at 2 × cap, paired block bootstrap (8 192 draws). Margin 1.5×:
- lower > 1.5 → A8 has a worthwhile search-cost advantage: price a fresh-bank comparison with both frozen;
- upper < 0.67 → tree GP worthwhile better: redirect learning toward an increment over tree search;
- interval inside [0.67, 1.5] → no difference beyond the margin: same redirect (a smaller arithmetic
  saving can still repay; that question is separate);
- otherwise unresolved, with a resolution price.

The search-cost verdict and acquisition repayment (arithmetic `A + N·S`, actual expenditures, savings
interval, unbounded horizon where savings are compatible with zero) are reported separately. TS Q, solves,
per-cell Q, 1 × cap, tree ÷ G4, lengths, rejection rates and seconds per search are descriptive.

**Expectations.** Tree GP solves most DG searches, with Q between 0.5 and 1.5; tree GP competitive or better
on TS. **Surprise:** Q lower bound > 1.5 (A8's literal joins beat whole-subtree exchange), or tree GP solving
fewer DG searches than G4.

**Next action.** Exit to strategy after the result. If the corrected initializer or any later gate fails,
park 43 with the measured obstacle and go to strategy. No further baseline redesign.
