---
node: questions/10-compositional-map-transfer/28-partial-program-feedback
title: Partial-program feedback vs equal-allocation one-shot acquisition, comparison-gate training cells
bank: comparison-gate-v1
---

**Question.** Per [strategy 2116](strategy.md) and its [plan](../../plans/partial-program-feedback.md);
new sub-question [28](../../questions/10-compositional-map-transfer/28-partial-program-feedback/question.md),
root 10's 19th slot. 1831's one-shot fit to pre-solve G4 tapes helps (C_S/T_S 1.28×, C_S/G4 1.62×).
Does spending the remaining two thirds of acquisition under the updated decoder teach a better
frozen decoder than spending it under G4, with identical fit and data quantity?

**Closest technique.** Iterated EDA refitting by external fitting:
[PIPE (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/), the cross-entropy method
([de Boer et al. 2005](https://cs.utexas.edu/~shivaram/readings/b2hd-DeBoerKMR2005.html)); the
accumulated-count update resembles [PBIL (1994)](https://www.ri.cmu.edu/publications/population-based-incremental-learning-a-method-for-integrating-genetic-search-based-function-optimization-and-competitive-learning).
New here: an equal-allocation one-shot control with an identical estimator, independent token
feedback, frozen reuse. A mechanism test of a known method; not inheritance or decoder selection.

**Design.** 1831's harness and S collector, unchanged (`998a9fe`; ≤ 65 536 evals per source, 8 parent tapes
at generations 64/128/256, first solve ends a source, only earlier tapes enter) and the 1707 fit
(equal weight per contributing source, cell rescaled to 1 600, α 50, G4 prior). **Lineage = one
1831 corpus** (8 BE + 8 PA, n 16). Round 1 = 1831's 32 G4 sources per own cell, regenerated and
hash-checked. Each round adds 32 sources per cell: every arm gets **96 sources per cell**.
- **F**: collect round 2 under C1 (= 1831 C_S) and fit C2 to rounds 1+2. Collect round 3 under C2;
  **F = C3**, fitted to all 96.
- **O**: 64 more G4 sources and one fit to all 96, using the same estimator, mass and weights.
- **TF**: the same loop with token-only fits from T1 (= 1831 T_S); TF = T3.
- **R** = C1 (first fit kept); **G4**; **C_exact** (1246; a cost-unmatched ceiling, descriptive).

Rounds 2–3 use fresh source seeds shared across F, TF, O. No intermediate table is scored or
chosen; all are saved. Empty cell–rounds stay empty and reported; no top-up or restart. Scoring is
6 arms × 16 lineages × 4 own cells × 16 fresh paired seeds = **6 144 searches**.

**Feasibility** (from 1831 [timing](../../../experiments/output/2026-10-08/2026-10-08-1831-partial-program-context/timing.json)).
Collection ran about 31 s wall per 128 G4 sources, so the 12 288 new sources take ≤ 50 min.
Scoring ran 1.30 s wall per search, about 22 min per partial arm and about 10 min for C_exact. That
gives ≈ 2 h of scoring and a **≈ 3 h queue**. If every fitted arm costs as much as an unsolved
search, the queue is 4.9 h, so the **timeout is 5 h**. Starvation risk is low: 17% of G4 sources
solved by generation 256. Even 50% early solves would leave about 16 contributing sources per cell.
The smoke measures per-round solve rates. If the mean projection exceeds 4 h, drop C_exact first;
if it still exceeds 4 h, write `infeasible.md`.

**Cost.** Preparation ≤ 2 h (new work is round orchestration, accumulation and round-1 replay).
Queue ≈ 3 h. Review, analysis and decision ≈ 3 h. **Total ≈ 8–10 h.**

**Primary comparison: F/O.** The score is exp(mean over lineages of the mean over 4 cells × 16
paired seeds of log cost_O − log cost_F). Unsolved searches count as 2 × cap. The interval is a 95%
t over 16 lineages, with an expected half-width of ×1.12 (1831's lineage SD 0.22–0.24 log). The
margin is **1.15×**: F costs no extra evaluations, only sequential rounds, so a smaller gain does
not repay the machinery.
- **Lower bound > 1.0:** feedback becomes the acquisition route, graded by its point estimate against 1.15.
- **Upper bound < 1.0:** feedback degrades. Report the starvation and shortcut diagnostics; the cause stays unisolated.
- **Upper bound < 1.15 otherwise:** at most a small gain. Prefer one-shot.
- **Else:** unresolved. Report the lineages needed and the price. No automatic follow-up.

**Secondary (no rules).** F/R (gain beyond the first fit), O/R (data quantity), F/TF (context vs
token feedback), TF/G4, F/G4 and F/C_exact. Also 1 × cap, both-solved pairs, solves, per family and cell. Per round and arm: actual source evaluations (the
allocation is equal, use is not), contributing and solved sources, tape D1331 accuracy, the
training-perfect share and row entropy. Payback of extra acquisition over R.

**Expectation.** O/R ≈ 1.05–1.15×: more G4 tapes add little (compare C′ ≈ C in 21). F/O ≈ 1.1–1.3×,
because later sources run closer to complete assemblies. F/TF > 1. **Surprises:** F < O
(reinforced shortcuts), F ≥ C_exact/2, or TF ≈ F.

**Scope.** Training cells of a development bank only. One horizon and three rounds. External
fitting. K unscored: procedures, not order. No transfer or family claim.

**Next action.** The researcher builds on `998a9fe` and smoke-tests round-1 hash replay,
accumulation, per-round exclusion and timing, then queues. After analysis, return to strategy. A
useful result earns at most a separately priced fresh-bank study, not more rounds.
