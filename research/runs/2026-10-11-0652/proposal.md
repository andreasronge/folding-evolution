---
node: questions/10-compositional-map-transfer/48-tree-donor-label-supply
title: Uniform compatible labels on learned donor shapes versus count-preserving rearrangement, gate-sum B/C
bank: x4-gate-sum-v1 (development bank since 0348; 0150 libraries and 0524 constructions unchanged)
---
**Question.** This follows [strategy 0652](strategy.md) and its [plan](../../plans/tree-donor-label-supply.md). On gate-sum's predicate-unmatched splits B/C, donors that keep the learned shapes and the size-conditioned label counts (R-perm) matched intact libraries: 1.031× [0.854, 1.225] ([47](../../questions/10-compositional-map-transfer/47-tree-donor-arrangement/question.md)). Does that gain also need the **learned label law**, given fixed acquired skeletons, node widths, sizes and multiplicities? The answer decides whether a later statistical donor learner must learn label supply or only shapes. It cannot show that no acquisition is needed.

**Probe (read-only, 0524 `libraries.json`).** The learned law is far from uniform:
- binary nodes are 84% ADD;
- input slots are 5% ANY;
- constants are mostly 0/1.

Distinct-input `ADD(Xi,Xj)` occurrences, counted as A/B/C (total):

| Library | A/B/C (total) |
|---|---|
| intact | 100/1/6 (107) |
| R-perm (mean of 3) | 28/27/33 (88) |
| uniform relabelling (expected) | 12/10/12 (35) |
| 0348's size-matched random donors (R-size) | 10/4/9 (23) |

B/C-specific pairs did not matter in 47: 7 versus 60 occurrences, at the same cost. Total pair supply tracks usefulness: R-size cost 0.86× R-tree ([0348](../2026-10-11-0348/analysis.md)). On the 131/181 three-node entries, R-size is almost the uniform law; it differs only in the 50 larger entries' skeletons.

**Closest known technique.** The candidate learner is a probabilistic prototype tree ([PIPE, Salustowicz & Schmidhuber 1997](https://gpbib.pmacs.upenn.edu/gp-html/Salustowicz_97ecml.html); reviewed in [Kim et al. 2014](https://gpbib.pmacs.upenn.edu/gp-html/KangilKim_2014_GPEM.html)). It learns per-node label probabilities from selected programs. This experiment is a **mechanism test of a known method**: would those label tables carry information beyond structure here? The map is fitted externally and frozen; there is no inheritance.

**Arms.** All arms use B/C only (12 cells, equal weight) and 0524's harness at `7c0e5df`. Search, cap (8 × 65,536), restarts and the library-draw rule are unchanged.
- **R-tree:** plain restarted tree GP.
- **R-lib:** the 24 intact 0150 libraries.
- **R-perm:** 0524's 72 frozen constructions, with hashes re-checked.
- **R-unif (new):** each node is relabelled independently and uniformly within its whole-grammar class:
  - binary {ADD, GT};
  - ternary {IF_GT};
  - width-2 terminals {X0–X3, ANY};
  - width-1 terminals {0, 1, 2, 5}.

  Widths still fix which slots are inputs and which are constants. There are 3 realizations per build, from a seed rule frozen before scoring and separate from search seeds. There is no filtering or deduplication.
- **R-size (descriptive):** 0150's saved controls. R-size ÷ R-unif asks whether the learned skeletons matter under uniform labels.

**Unit and size.** One job is (build, cell, repeat), with 6 repeats; realization = repeat mod 3. All arms share each job's 8 fresh attempt seeds, disjoint from history. That is **1,728 jobs per arm** and 8,640 in total, all contemporaneous. Intervals are paired bootstraps over builds, with constructions nested; in 0524 this size gave about ±18%.

**Validation before scoring:**
- R-unif skeleton, width, size and multiplicity invariants;
- interpreter, compiler and Rust agreement on D625;
- replay of saved 0524 jobs;
- a content audit (label counts, pair sums by split, predicates, behaviours), descriptive only.

**Feasibility and cost.** Measured worker-s per B/C job: R-tree 6.84, R-lib 2.25, R-perm 2.34, R-size 5.40. R-unif is priced as R-tree. That is about 41,000 worker-s, or **about 70 min** at 0524's 10× concurrency.
- **Stage gate:** R-unif on 0524's 4 development cells. Above a 100-min projection, drop R-size first, then fall back to 4 repeats.
- **Timeouts:** 40 + 120 min.
- **Full cost about 4.5 h:** build ≤ 2 h, queue about 1.3 h, analysis about 1 h.

**Primary comparison.** Mean capped evaluations, **R-unif ÷ R-perm on B/C**, with a 95% interval; the margin is 1.25, as in 47.
- **Label law carries worthwhile information:** lower bound > 1.10 and point ≥ 1.25.
- **Uniform labels suffice at this resolution:** upper < 1.25, R-unif ÷ R-tree upper < 0.80, and solve-fraction difference lower bound > −0.03. Saying the *acquired* benefit is retained also needs R-unif ÷ R-lib upper < 1.25. Otherwise the result reads "matches R-perm; relation to intact unresolved"; 47's 1.225 upper bound forbids chaining.
- **Otherwise unresolved:** report the precision price.
- **Validity guard:** R-lib ÷ R-tree and R-perm ÷ R-tree upper < 0.60. If either fails, read nothing.

The analysis also reports:
- acquisition charged to R-unif (2.88M evaluations per library);
- worker seconds;
- per-split results and solves;
- insertion rates;
- the spread across realizations.

**Expectation.** About 70%: a worthwhile loss, with R-unif ÷ R-perm about 1.6–2.5 and R-unif near R-size. The likely reason is that uniform ADD/GT/ANY dilutes the general supply of pair sums. **Surprise:** R-unif ≈ R-perm, meaning the larger entries' learned skeletons carry the gain. That would contradict the pair-supply reading.

**Next action.**
- **Loss:** return to strategy; any PIPE-like or different-source acquisition must keep label supply.
- **Retention:** price a source-independent structural generator or shape acquisition on new sources.
- **Unresolved:** report the price and return.

Nothing is funded automatically.
