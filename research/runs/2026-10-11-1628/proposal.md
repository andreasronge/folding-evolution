---
node: questions/10-compositional-map-transfer/57-order-helper-arrangement
title: Do R-all's order helpers need their learned arrangements?
bank: x4-order-v1 (development roster only; saved 1228 R-all libraries; protected cells untouched)
---
**Question.** R-all cut order-task cost to 0.40 [0.32, 0.50] of R-tree on development cells and 0.37 on
held-out cells ([53](../../questions/10-compositional-map-transfer/53-order-library-cap-release/question.md),
[56](../../questions/10-compositional-map-transfer/56-order-library-protected-cells/question.md)). The coverage
gradient points at the twelve min/max helpers, but coverage was not an intervention and the no-helper stratum still
cost only 0.74 of R-tree. Is the saving lost when **only the helper entries lose their learned arrangement**,
with their material, shapes, slots and draw probabilities fixed? This follows [strategy 1628](strategy.md) and
its [plan](../../plans/order-helper-arrangement.md); recorded as new sub-question 57.

**Closest known technique.** External library extraction for GP mutation donors: [Keijzer, Ryan & Cattolico,
*Run Transferable Libraries* (2004)](https://link.springer.com/chapter/10.1007/978-3-540-24855-2_63); semantics-keyed
subprogram libraries: [Pawlak, Wieloch & Krawiec, *Semantic Backpropagation* (IEEE TEC 2015)](https://gpbib.cs.ucl.ac.uk/gp-html/Pawlak_2014_ieeeEC.html).
The map adapts by external fitting, frozen before search. This is a **mechanism test** of a known approach: which
library content carries a replicated saving. It refines [47](../../questions/10-compositional-map-transfer/47-tree-donor-arrangement/question.md),
which permuted labels across whole libraries; here only helper entries change, within each entry.

**Arms** (restarted tree GP, ≤ 8 × 65,536, half the mutation donors from the library, everything else fixed):
- **R-all**: the 24 saved libraries, reconstructed and hash-checked from [1530](../2026-10-11-1530/execution.md).
- **R-hx**: same libraries; each entry whose D625 output equals one of the twelve helpers has its labels permuted
  within (arity, token-width) pools of that entry, accepted only if no subtree equals any helper on D625. All
  other entries byte-identical; same slots, uniform draws, duplicates kept. Four seeded realizations per build,
  fixed before scoring, never chosen by performance; realization = repeat mod 4.
- **R-tree**: no library.

Unit: build × development cell × repeat, seed-paired across arms. 24 builds × 6 cells × 8 repeats =
**1,152 jobs per arm, 3,456 total**.

**Feasibility (measured).** The [static audit](helper-planning-audit.json) reproduced all semantic hashes and found
177 helper entries (4–10 per build; 130 six-node, 26 eight-node, 21 nine-node), none embedded elsewhere, and support for
all 177 (≤ 16 draws). My enumeration of every admissible permutation (on a 5-value proxy grid; prepare recomputes on
D625): **135/177 entries can only become an expression equal to a single input** (e.g. `IF_GT(X1,X1,GT(X3,X3))`),
131 have just two admissible forms. So R-hx mostly swaps each helper for an inert same-material entry, and realizations
differ mainly on the 42 larger entries. Runtime from [1228](../2026-10-11-1228/execution.md) rows: R-tree 5.31,
R-all 2.14 worker-s/job; 2,304 jobs took 836 s (≈ 9.7 workers). Worst case, R-hx as slow as capped R-S (6.39):
≈ 16k worker-s ≈ 28 min; expected 22–25 min.
Precision: splitting 1228's R-all rows into two same-library halves (288 vs 288 jobs, whole-build bootstrap) gave
0.93 [0.76, 1.17] and 1.02 [0.79, 1.29]. At 1,152 per arm, within-build noise halves in log, so a true ratio of 1.0
should give an upper bound near 1.15–1.2, plus build-to-build variation in the effect.

**Cost.** Queue: construction + validation ≤ 10 min timeout, scoring 60 min timeout (70 min summed; cap 90).
Agents: preparation ≤ 120 min (reuse `order_library.py`, `tree_permutation.py` with pools restricted to one entry,
the scoring wrappers on `research/main` at `53f0e06`), reviews and analysis ≈ 1.5 h. **About 4–4.5 h total**, inside
the 5 h ceiling and the 21.6 h left.

**Primary comparison.** Q = cost(R-hx) / cost(R-all): ratio of pooled capped arithmetic means, 95% bootstrap over
whole builds (each build's realizations and repeats resampled with it). R-all's saving is about 2.5× (0.92 in log),
so 1.25 is about a quarter of it.
- **Lower(Q) > 1.25 → material loss**: the helpers' arrangements carry a material share of the saving, relative to
  this same-material replacement and conditional on the rest of R-all.
- **Upper(Q) < 1.25 and upper(R-hx / R-tree) < 0.80 → useful retention**: exact helper computations are not needed
  at this resolution.
- Otherwise **unresolved**; the analysis prices a run that would decide it, with no automatic top-up.

Reported, not gated: solve counts per arm; R-hx / R-tree (whether the replacement harms); Q in the saved
coverage strata (descriptive, not selected cohorts); share of R-hx solvers containing a helper-valued subtree
(rediscovery); every construction invariant (primitive counts, skeleton, nodes, compiled length,
interpreter/VM agreement) and any failure. A construction failure returns to strategy: no dropped entries, no relaxed matching.

**Expectation.** If the helpers carry the coverage gradient, R-hx should sit near the no-helper stratum (≈ 0.75 of
R-tree), Q ≈ 1.5–2: material loss. Q near 1 would surprise me and point to supply of order primitives and other
2-cell content. Caveat: because most replacements are inert, a loss shows "helper beats same-material inert entry",
not that min/max specifically beats any other nontrivial computation; matched alternatives of that kind do not
exist for six-node entries.

**Next action.** Return to strategy either way. Loss: intact learned computations become a requirement for the
next acquisition plan, and a fresh-family source census earns its case. Retention: drop the helper-containment idea
and look at statistical donor supply. No branch automatically funds another order-bank run.
