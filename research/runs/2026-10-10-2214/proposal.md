---
node: questions/10-compositional-map-transfer/43-acquired-bias-vs-tree-gp
title: Frozen A8 versus family-blind typed subtree GP on the DG and TS rosters
bank: x4-double-gate-v1 (8 spare cells) + x4-branch-sum-v1 (8 targets), saved 1717 builds; development data
---
**Question.** Following [strategy 2214](strategy.md) and its [plan](../../plans/typed-gp-acquisition-value.md):
native A8 is 6–10× cheaper than G4 on DG cells, but G4 is a weak tape prior. Does frozen A8 keep a
worthwhile search-cost advantage over a conventional, family-blind structural prior (typed subtree GP),
and does its acquisition repay? A practical comparison of complete procedures, not a causal test of learning.

**Closest technique.** Strongly typed GP ([Montana 1995](https://davidmontana.net/papers/stgp.pdf)) with
lexicase selection ([Helmuth 2015](https://web.cs.umass.edu/publication/docs/2015/UM-CS-PhD-2015-005.pdf)).
A8 is PIPE-like program-distribution learning ([Salustowicz & Schmidhuber 1997](https://pubmed.ncbi.nlm.nih.gov/10021756/))
plus subtree-transfer between related problems ([Dinh et al. 2015](https://gpbib.cs.ucl.ac.uk/gp-html/Dinh_2015_CEC.html);
[O'Neill et al. 2017](https://gpbib.cs.ucl.ac.uk/gp-html/oneill_2017_CEC.html)); its map adapts by external
fitting. Those transfer papers compare against GP from scratch; this asks whether a learned tape bias beats
the stronger move of changing representation. A baseline test, worth running though both methods are known.

**Tree GP (build ≤ 120 min, from `research/main` `6dabda8`).** Under `v2_x4` the only consumed type is int
([log](../../questions/10-compositional-map-transfer/43-acquired-bias-vs-tree-gp/log.md)): terminals X0–X3
(INPUT + readout, 2 tokens), ANY, constants 0/1/2/5; functions ADD, GT, IF_GT (postfix else, then, cond).
No DG/TS templates, roles or fitted frequencies. Trees compile to postfix tokens and run on the production
Rust executor; compiled length ≤ 32. Ramped half-and-half (depth 2–4); each child is subtree crossover or
subtree mutation (grow, depth ≤ 3); oversize children are replaced by parent 1. Everything else is the A8
harness: P 256, 2 elites, lexicase on the same 64 cases (same `[seed, 0]` stream), cap 524 288, exact
625-input check. Validate against an independent interpreter on random trees, compiled canonicals of all 16
targets, size rejection and replay. The tree arm is essentially Koza closure GP with typed readout
terminals; DUP/SWAP and malformed tapes are absent: a representation comparison, not equal search spaces.

**Stage 0 (in preparation, before targets).** One bounded choice between two standard mixes,
crossover/mutation 0.9/0.1 and 0.5/0.5, on the DG and TS source + development cells (16 cells × 8 seeds × 2
= 256 searches), frozen by geometric capped cost and charged as development cost. These searches also give
the timing. **Admission:** projected scoring ≤ 80% of its timeouts; a tree arm solving < 25% of DG
calibration searches is flagged as possibly broken and goes to the code reviewer before scoring.

**Arms and unit (each roster: 8 cells).** A8 native: 24 builds × 2 fresh seeds × 8 cells = 384 (D on DG,
T on TS). Tree GP: 384 searches on the same (cell, seed) pairs, so case draws are paired. G4 reference: 16
seeds per cell = 128. Unit: the 24 build blocks (2 seeds × 8 cells, with the tree rows sharing those seeds;
tree rows are independent searches, never one row reused). Total 1 792 scored searches.

**Feasibility.** Measured: A8 11.7 s/search on DG, 3.6 on TS; G4 29 / 14 s (2001, 1717); 10 workers.
Unmeasured: tree generation time; bound 2 048 generations × ≤ 25 ms = ≤ 51 s per failed search (A8 runs
about 16 ms per generation including decode). Precision: D build-level log-cost SD 0.66 gives a 95% interval
of about ×/÷ 1.33 with 24 blocks, as in 2001 (observed ×/÷ 1.36).

**Cost.** Queue: prepare (validation, 16 A8 replays, 256 calibration searches) ≤ 25 min; DG score
expected 25 min, worst 50; TS 10–40 min. Timeouts sum ≤ 4 h. Agent time about 5–7 h. Fits well inside the
39.9 h left.

**Primary comparison.** DG roster: Q = cost(tree) ÷ cost(A8-D), geometric capped cost over 8 fixed cells,
failures at 2 × cap; block bootstrap (8 192 draws, blocks resampled, seeds within block × cell). Margin 1.5×:
- lower > 1.5 → **A8 worthwhile over tree GP**: next, price a fresh-bank comparison with both frozen;
- upper < 0.67 → **tree GP worthwhile better**: A8's practical case fails here; redirect learning to an
  increment over tree search;
- interval inside [0.67, 1.5] → **no worthwhile difference**: acquisition is not repaid; same redirect;
- otherwise **unresolved**, with a resolution price.

Reported, no rule: TS Q (separate boundary, never pooled), solves, per-cell Q, 1 × cap repeat, tree ÷ G4,
compiled lengths, seconds per search; repayment N* = acquisition ÷ (mean tree cost − mean A8 cost) per
build in evaluations and worker-seconds ("never" if negative).

**Expectations.** Tree GP starts from well-formed expressions over the six relevant terminals and three
functions, the advantage G4 lacks; DG targets are 10-node trees. I expect it to solve most DG searches and
Q between 0.5 and 1.5 (no worthwhile A8 gain, or tree better), and tree better on TS. **Surprise:** Q lower
bound > 1.5 (A8's literal joins beat whole-subtree exchange), or tree GP solving fewer DG searches than G4.

**Next action.** Exit to strategy after the result, or earlier on a failed admission or validity check.
