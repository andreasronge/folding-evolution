---
status: closed
tags: [compositional-transfer, acquisition-cost, solver-corpus, fragment-library, block-edit, external-fitting, data-efficiency]
budget: {experiments: 1, used: 0}
---
# Can four source attempts per cell teach the whole C+F procedure?

Current summary: **no, not at the pre-set 20% retention target; it is cheaper only over a short
reuse horizon (run 2026-10-09-1743, commit `652fde5`); closed.** The full-corpus pipeline (C fitted
to 48 G4 collection searches per training cell, plus its fragment library F) is the best known
procedure on then-addition (F/C 1.47×, [32](../32-learned-fragment-operator/question.md)). C4+F4
rebuilt each corpus's decoder and library from four capped G4 attempts per training cell, failures
charged, empty cells given G4's expected transitions; four disjoint acquisitions per corpus, 16
corpora × 16 then-addition cells × 16 seeds, paired with 1036's full rows:

- **Retention ρ = cost(full F)/cost(C4+F4) 0.679× [0.614, 0.752]**: about 1.47× the search cost
  (1.33–1.63×). The 0.833 tolerance is excluded under 1 × cap, both-solved (upper 0.832), BE, PA
  and in each of the four source blocks. Solves 85.9% against 90.8%.
- **C4+F4 is not resolved from the full decoder alone**: full C/C4+F4 0.996× [0.919, 1.080] in cost.
  The cheap pipeline gives back roughly the library's whole advantage, but stays about 4× cheaper
  than G4 per capped search (unpaired).
- **F4 still beats its own chain blocks**: cost C4+W4/C4+F4 1.12× [1.03, 1.22], unresolved against
  the worthwhile 1.10×. W4 did not retain either (C4+W4/full W 1.38×).
- **Economics (arithmetic A + N·S, evaluations)**: acquisition 8.1% of the full corpus's, per-search
  cost 1.33× higher. C4+F4 is the cheaper deployment up to about 1 530 [1 247, 2 016] fresh searches
  on this bank, the full pipeline beyond; both repay against G4 within about 31 searches.
  Worker-second curves (≈ 780) use a qualified calibration and are indicative only.

Competing explanations: (a) a handful of recurring joins that a few solvers already show —
not sufficient at four attempts; (b) the library rescues a weaker decoder — consistent with C4+F4 ≈
full C and C4+W4 < full C, but there is no bare-C4 arm and W4 carries F4's length law, so decoder
and library losses are not separated; (c) context and library need more solvers per cell —
consistent with the post hoc per-acquisition pattern (64 builds, ρ 0.21–1.34; worse with empty
source cells and small libraries, Spearman −0.35 and 0.36), not tested. Full-size 32-fragment
libraries from four attempts still average 0.77, so library size alone does not close the gap.

Scope: one source size (4 of 48 attempts), reused development sources (1246) and development bank
then-addition-v1, one fitter/extractor/operator, external fitting. Average over four replicate
acquisitions per corpus; single builds vary widely. Not fresh-bank transfer, not inherited map
evolution, not where between 4 and 48 attempts retention returns.

Opened 2026-10-09 (steward, run 1743) under [strategy 1743](../../../runs/2026-10-09-1743/strategy.md)
and the [plan](../../../plans/small-corpus-complete-pipeline.md); slot 27 of root 10.

Related: [32](../32-learned-fragment-operator/question.md), [33](../33-pre-solve-fragment-source/question.md),
[27](../27-partial-program-context/question.md), [28](../28-partial-program-feedback/question.md),
[run 1743 decision](../../../runs/2026-10-09-1743/decision.md), [log](log.md).

Reopen if: a different source budget or source rule is priced as a complete pipeline with a
concrete reason to expect retention (e.g. a solver-count stopping rule motivated by the
empty-cell/library-size pattern, or an intermediate attempt count whose break-even against full F
matters for a deployment decision); or a fresh bank is frozen with this four-attempt policy to test
whether its loss or its short-horizon cost advantage transfers.
