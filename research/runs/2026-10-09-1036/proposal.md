---
node: questions/10-compositional-map-transfer/32-learned-fragment-operator
title: Frozen fragment reuse on excluded compositions (then-addition primary, holdouts reference)
bank: then-addition-v1
---
Follows [strategy 1036](strategy.md) and the [reuse plan](../../plans/fragment-reuse.md).
Question 32's budget was raised 1 → 2; root 10 is at 24.

**Question.** On training cells, intact solver fragments inserted as block edits beat C 1.57×
and C-chain blocks W 1.23× ([0843](../2026-10-09-0843/analysis.md)). Those libraries were
mostly shared 3-token syntax. Do frozen whole-corpus libraries still beat W when addition
moves into the then-branch (`A>B ? C+D : E`)? If yes, a separate repertoire is worth
acquiring. If the increment is tightly small, keep W, which needs no library.

**Closest known technique.** Run-transferable libraries
([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)),
ARL ([Rosca 1995](https://cdn.aaai.org/Symposia/Fall/1995/FS-95-01/FS95-01-011.pdf)) and
[DreamCoder](https://arxiv.org/abs/2006.08381). The library is fitted externally and then
frozen; nothing is inherited. This adds a cross-shape test against a control differing only in
block content: a boundary test of a known technique, not new to this tree (no new search).

**Arms and unit.** C's 16 frozen tables and its search are unchanged (P 256, lexicase, 524k
cap, code `e347793`).
- **C:** no operator.
- **F:** with p 0.2, each non-elite child gets one fragment drawn uniformly from the corpus's
  whole-corpus library. That library holds 32 fragments from all four training cells; it is
  already saved in 0843 prepare (113 distinct; lengths 3/4/5).
- **W:** C's chain, given the preceding token, with F's length law, start law and suffix
  repair.

There is no B arm, so the F/W increment does not separate dependencies from changed token
supply. Fresh paired seeds; shared initial populations. The unit is the
source corpus, n = 16 (8 BE-fitted, 8 PA-fitted).
- **Primary, then-addition-v1:** 16 corpora × 16 cells × **16 seeds**, 4 096 searches per arm.
- **Within-shape reference, 8 comparison-gate holdouts:** 16 × 8 × **8 seeds**, 1 024 per arm.
  Reported separately, with no decision rule.

**Prepare** (no tuning) checks:
- the library hashes it rebuilds against 0843;
- 10k edits per block arm in the edit audit;
- 16 C rows from 1548, replayed bit-exactly with the operator off;
- fragments that solve an evaluation cell when NOP-padded (expected 0; reported, not
  filtered);
- a timing smoke of 3 arms × 8 cells × 4 seeds.

**Feasibility (measured).** Every corpus has a 32/32 whole library. On search time, C took
7.1 s on then-addition and 4.5 s on holdouts ([1548](../2026-10-08-1548/analysis.md)). F and W
ran at 0.76× and 0.80× of C's time on training. The projection is 86k worker-s, which is
144 min on 10 workers, or 166 min with 15% margin.

**Precision** ([probe](steward_probe/variance_probe.py), on 0843 rows): pair SD 1.85 and
between-corpus F/W SD 0.06. That projects an F/W half-width of **×1.072** at 256 pairs per
corpus (×1.098 at 128). Then-addition censors more (C solved 86.5%), so the real width may be
somewhat wider.

**Admission.** If smoke × 1.15 exceeds 195 min of scoring, every arm drops to 12
then-addition seeds. If that still does not fit, write `infeasible.md`. No cells or corpora
are pruned.

**Cost.** Queue timeouts are 30 + 205 min (under 4 h); about 2.9 h of queue is expected.
Agents need about 3 h. **Total about 6 h.**

**Primary comparison.** On then-addition: X/Y = exp(mean over corpora of paired log
cost_Y − log cost_X). Unsolved runs count as 2 × cap. Intervals are 95% t on 15 df. F/W is
the scientific contrast; F/C is the practical benchmark. A worthwhile increment is **1.10×**.
Below that, a second learned object is not worth acquiring beside W. Rules, in order:
1. **Harm:** F/W or F/C upper bound < 1. Ends this extractor's expansion across shape.
2. **Repertoire earns acquisition review:** F/W lower bound > 1 and point ≥ 1.10, and F/C
   lower bound > 1.
3. **No worthwhile library increment:** F/W upper bound < 1.10. Report W/C. If W/C's lower
   bound is > 1, W is the cheaper candidate.
4. **Unresolved:** otherwise. Price a ×1.05 half-width. This is not evidence for block
   mechanics.

**Descriptive:** holdout contrasts, BE/PA corpora, per cell, 1 × cap, both-solved, solves,
realized edits, library windows in solvers (occurrence, not ancestry), wall time. Repayment:
mean evaluations saved against library extraction cost; corpus collection reported separately.

**Scope.** These are development banks. A win shows that this procedure is reused across one
shape change. It does not show modularity rather than syntax, acquisition, or family
specificity.

**Expectation.** The fragments are generic syntax (`input reduce input`, `add input first`)
that then-addition also needs. Reuse probably survives but shrinks, as C/T lost a third. My
guess: F/W 1.05–1.15 (rule 2 or 4), F/C about 1.4, W/C about 1.25. Two results would
surprise me: F/W ≥ 1.2 here, or F/W < 1 here while the holdouts stay above 1.1.

**Next action.** Every rule returns to strategy (2: acquisition plan; 3: W candidate, library
ends; 1: line ends; 4: resolution price). Nothing is funded automatically.
