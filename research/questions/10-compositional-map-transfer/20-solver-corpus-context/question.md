---
status: closed
tags: [compositional-transfer, decoder, external-fitting, solver-corpus, contextual-learning, token-multipliers, fresh-start]
budget: {experiments: 1, used: 0}
---
# Does a previous-token decoder fitted to independently evolved training solvers speed fresh search beyond a token-only fit to the same solvers?

Current summary: **closed after run 2026-10-07-1707 (row 1, 1 of 1 slot; commit `627336d`). A
previous-token table C fitted to exact G4 solver tapes (transition counts shrunk toward G4, α 50)
speeds fresh search beyond a token-only maximum-likelihood fit T to the same tapes: C/T 1.365×
[1.288, 1.446] on the training cells (16 independent corpora per family; BE 1.46×, PA 1.28×; 31/32
corpora) and 1.293× [1.213, 1.378] on the three withheld cells (30/32). A token-only table K
matched to C's pooled emitted frequencies does not reproduce the gain (C/K 1.65×), but K is itself
slower than T (0.83×), so C/T is the better size of the contextual increment. Both fits beat G4
(T 2.4×, C 3.3× on training; unpaired); T was not resolved from the saved 1723 search-selected
maps, and those intervals allow appreciable differences (BE 0.95× [0.81, 1.11], PA 1.02× [0.81,
1.28]). No family-specific advantage was resolved; C's gains extend to both families, but the carrying structure and modest family preferences remain unresolved: matched over mismatched C is 1.02× [0.91, 1.15] on the one
BE holdout and 0.75× / 0.99× on the PA holdouts (the first favours the BE-fitted tables). This is
external fitting, not evolutionary discovery; which structure carries the gain (specific bigrams,
executed versus inert tokens, position) and the α dependence are not mapped.**
This changed the learning procedure: decoder tables are fitted directly to the token tapes of
exact solvers found by fresh G4 searches on the training cells (external fitting), not selected
by search cost.

Measured before the first run (steward probe, one corpus per family, 48 G4 collection seeds per
training cell, 12 fresh seeds per cell and arm; [script](../../../runs/2026-10-07-1707/steward_probe.py)):
corpus yield 175/192 (BE) and 281/288 (PA); collection about 1 min per family on 10 workers.
Mean log2 evaluations to an exact solve, G4 / token-only fit T / contextual fit C (α 50) /
emitted-marginal control K: BE 13.99 / 12.33 / 11.55 / 12.95, PA 14.16 / 12.83 / 12.55 / 12.84.
A second contextual shrinkage (α 400) gave BE 12.87, PA 12.53. One corpus each, 48–72 searches
per arm: a calibration, not evidence.

Competing explanations:
- A: Solver tapes carry assembly information (which token follows which) that a token-only fit
  cannot express, and it speeds fresh search. C beats T and its own emitted-marginal control K.
- B: The useful content is token frequency. C's gain over T, if any, is explained by the
  frequencies C happens to emit (C ≈ K).
- C: The contextual fit overfits the corpus (hitchhiking inactive material, small rows) and
  is no better, or worse, than the token fit.
- D: A training-cell gain does not transfer to the withheld compositions.

After run 1707: A is supported at this scope (C beats T and K on training and holdout cells,
replicated over 32 corpora). B is rejected for pooled emitted frequencies (C/K 1.65×), not for
position-specific or in-population frequencies. C is not supported here: C outperformed T on fresh
training searches and the three holdouts; the extent of overfitting (including inert material in
the tapes) was not isolated. D is not supported:
C/T 1.29× [1.21, 1.38] on the withheld cells.

Scope: the frozen 1603 four-reducer bank, the 1723 split (BE trains on 4 cells, PA on 6; three
holdouts never used in collection or fitting), D1331, `v2_rmin_first`, G4, P 256, length 32,
the 0315/2229 search regime. Holdouts are a reused screened bank, not an untouched benchmark;
one BE holdout is one task.

Related: [root 10](../question.md), [21 iterated solver corpus](../21-iterated-solver-corpus/question.md), [concept plan](../../../plans/solver-corpus-context.md),
[strategy 1707](../../../runs/2026-10-07-1707/strategy.md),
[18 compact context](../18-compact-context-learning/question.md),
[19 selection-calibrated continuation](../19-selection-calibrated-continuation/question.md),
[16 crossed family](../16-crossed-family-adaptation/question.md),
[run 1707 analysis](../../../runs/2026-10-07-1707/analysis.md),
[run 1707 decision](../../../runs/2026-10-07-1707/decision.md).

Reopen if (once parked/closed): a fitting rule over executable structure (active tokens only)
is funded, a later study needs a data-derived context target for map evolution, or new
evidence shows the C/T gain depends on the frozen α 50 (the probe's α 400 was weaker on BE).
