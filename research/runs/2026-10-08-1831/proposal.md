---
node: questions/10-compositional-map-transfer/27-partial-program-context
title: Context fitted to selected non-solving tapes vs token fit, on comparison-gate training cells
bank: comparison-gate-v1
---

**Question and mechanism.** Following [strategy 1831](strategy.md) and its
[plan](../../plans/partial-program-context.md): can tapes that lexicase selects in short G4 searches,
**before any exact solve**, teach a previous-token decoder (C) that speeds fresh search beyond a
token-only fit (T) to the same tapes, and beyond G4? New sub-question [27](../../questions/10-compositional-map-transfer/27-partial-program-context/question.md),
root 10's 18th slot.

**Closest technique.** Fitting a program-generating model to the current best, non-solving
programs is what EDA-GP does: [PIPE (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/) updates
from the best program, [N-gram GP (2008)](https://drops.dagstuhl.de/entities/document/10.4230/DagSemProc.08051.5)
fits instruction triplets from good population members; review in
[Kim et al. 2014](https://gpbib.cs.ucl.ac.uk/gp-html/KangilKim_2014_GPEM.html).
[Dinh et al. 2015](https://gpbib.cs.ucl.ac.uk/gp-html/Dinh_2015_CEC.html) transfers final-generation
individuals and subtrees to new runs. This is **external fitting**, not inheritance or selection
among decoders. New here: frozen reuse in independent searches, a token-fit control on identical
data, a selection-enrichment control and a paired exact-fit comparison. A mechanism test.

**Collector (fixed now).** Reviewed `composition_search` on `research/main` (`45b2bdb`), G4, cap,
P 256, tape 32, D1331. Each source search runs G4 to at most **256 generations (65 536 evals)**
and stops at its first exact solve. At the ends of generations 64, 128 and 256, if not yet solved,
it records 8 decoded tapes drawn from that generation's lexicase parent picks (selection-weighted;
**S**) and 8 drawn uniformly from the population (**P**). A separate RNG does the draws, so
collection cannot change the search (replay check); an exact solve ends the search before any
checkpoint of that generation. Partial rows get an explicit count interface, not `solved`. **32 source searches per own training
cell**, 8 corpora per family (2 048 sources). Within a cell every contributing source gets equal
weight; then the frozen 1707 rule applies (cell rescaled to 1 600, α 50, G4-based T). All
sources stay in manifest and cost; an empty cell is an execution obstacle, never replaced.

**Arms, unit, seeds.** Per corpus, on its 4 own training cells × 16 fresh seeds, paired across
arms: **C_S, T_S** (primary), **C_P** (uniform-population context), **C_exact** (1246's frozen C
for the same family/corpus index; positive control, hash-checked) and **G4**, paired by seed.
5 120 scored searches. The unit is the corpus (n 16, BE/PA equal weight). Run in pair blocks
(BE_i, PA_i), each collect → fit → score; a timeout leaves the largest complete prefix (≥ 12
corpora required).

**Feasibility.** From 1246's 5 376 rows: ≈ 20k evals per worker-second, ≈ 9.7 effective workers;
G4 solves 2.1/6.2/14.9% of searches by 16k/33k/66k evals, so most sources reach all three
checkpoints. Mean worker-s per search: C_exact 5.5, G4 13.5, unsolved ≈ 27. Collection ≈ 2 048 ×
≤ 3.3 s ≈ 2 min wall. Scoring with the three partial arms at 12 s each: ≈ 1.8 h; all three at
the unsolved cost: ≈ 3.2 h. A smoke measures collector and fitted-arm rates; a projection over 3.5 h means
`infeasible.md`, not a resize.

**Cost.** Queue timeout **4 h** (expected ≈ 2 h). Preparation ≤ 2 h; review, analysis and decision
≈ 2.5 h. Total ≈ **6.5–8.5 h**, within the 6–8 h allocation at the expected rate. Acquisition is
about 1/12 of exact collection's evaluations per cell (32 × ≤ 66k vs 48 × ≈ 250k mean).

**Primary comparison.** C_S/T_S = exp(mean over corpora of mean over 4 cells × 16 paired
seeds of log cost_T − log cost_C), unsolved = 2 × cap, 95% t interval over corpora. Worthwhile
margin **1.20×** (the feedback stage costs 8–12 h; exact C/T was 3.11×). C_S/G4 is computed
the same way (paired seeds).
- **Upper bound < 1.20:** no worthwhile context signal from this collector; do not fund
  feedback on it. (Takes precedence.)
- **Lower bound > 1.0 and C_S/G4 lower bound > 1.0:** useful partial-program context;
  recommend strategy consider the bounded feedback stage.
- **Lower > 1.0 but C_S/G4 not > 1:** relative fit advantage only, not useful acquisition.
- **Otherwise unresolved:** report corpora needed at the observed SD, with price.

Half-width ≈ ×1.12 at 1246's per-corpus SD (0.21 log), ×1.17 at 0.30: a true null resolves.

Secondary (reported, no rule): C_S/C_P (parent enrichment), C_S/C_exact (share of exact-fit
value; acquisition costs differ), T_S/G4, per family, 1 × cap, both-solved pairs, solve rates.
Descriptive: duplicate rate, effective sources, share from sources that later solved,
training-perfect share and D1331 accuracy of collected tapes, fit row entropy.

**Expectation.** C_S/T_S ≈ 1.3–2×: by generation 256 populations hold near-complete assemblies.
C_P ≈ C_S; C_S/C_exact ≈ 0.5–0.8. **Surprises:** C_S
not above T_S, or below G4 (shortcuts mis-teach); C_S ≈ C_exact (complete solvers add nothing
at this scale); C_P clearly better than C_S.

**Scope.** Development bank, training cells, one horizon; K unscored (a fitting-procedure
difference, not isolated order). A null bounds this collector only.

**Next action.** Researcher adds the collector on `research/main`, smoke-tests replay,
exclusion and timing, queues; then analysis and strategy (feedback versus deferred candidates).
