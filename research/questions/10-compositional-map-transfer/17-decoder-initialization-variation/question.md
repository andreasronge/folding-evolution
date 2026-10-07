---
status: open
tags: [compositional-transfer, decoder, token-multipliers, mechanism, initialization, variation, frozen-maps, fresh-start]
budget: {experiments: 2, used: 0}
---
# Does the learned token map help search through its starting programs, through the variation it produces during search, or both?

Current summary: **on the three 2229 cells, both parts of the learned map help and they overlap
heavily (run 2026-10-06-2331, commit `8f42f38`, row 3).** Holding the generation-0 token tapes
identical, searching under M instead of G saves 1.39× [1.31, 1.47] (P1, given M's start);
holding the search decoder at M, starting from M's programs instead of G's saves 1.30× [1.24,
1.36] (P2). The full diagonal is 2.29× [2.05, 2.54]. Either component alone (from G's side)
gives 1.65× (start) or 1.76× (ongoing), 60–68% of the diagonal in log units; the interaction is
−0.34 log2 [−0.40, −0.29], negative in 20/20 maps. Which component is larger flips with the cell:
on the BE cell the start dominates (P1 only 1.11× [1.04, 1.19]), on both PA cells the ongoing
decoder does (P1 1.46–1.65×, P2 1.22–1.35×); one BE cell, descriptive. Fairly sure of the pooled
numbers (400 seeds, 20 maps, all validation passed, robust to the cap); narrow in scope (three
reused screened cells, G4's hand-supplied context, this population/operator/budget regime).
"Ongoing" bundles mutation, crossover, inherited latent alleles and continued program supply; it
is not evidence of a better neighbourhood beyond sampling. Almost nothing solves at generation 0
(12/79 200), so the start effect is about useful partial programs, not seeded solvers.

Slot 2 (proposed, run 2026-10-07-0315): the same frozen 2×2 on the ten training cells (4 BE,
6 PA), asking whether the 2331 pattern holds across the bank and whether the start-versus-ongoing
balance tracks cell family.

Competing explanations:
- I: The learned initial distribution carries the gain; MG ≈ MM. Not supported on these
  cells: MG is 1.39× slower than MM (lower bound 1.31×). On the BE cell alone P1 is 1.11×
  [1.04, 1.19], close to I's prediction.
- O: Ongoing use of M carries it; GM ≈ MM. Not supported: GM is 1.30× slower (lower bound 1.24×).
- B: Both contribute. Fits, with a strongly negative interaction (sub-additive).
- R: Either alone gives nearly all of it. Partly: either alone gives 60–68% of the diagonal in
  log units, not "nearly all"; the second still adds a resolved 1.30–1.39×.
- New, from the per-cell split (descriptive): the balance depends on the task (start-heavy on the
  BE cell, ongoing-heavy on the PA cells). Slot 2 tests whether this tracks family.

Slot plan (strategy 2331): slot 1 = the three 2229 cells, all 20 maps; slot 2 = the same frozen
intervention on the ten training cells, only if slot 1 gives a bounded answer (it did). Neither
slot isolates mutation from crossover, matches solver frequencies, or bears on learned context or
on whether the maps are family-specific; slot 2 asks only whether the mechanism's balance differs
between BE and PA cells. On training cells each map is in-sample for its own family's cells.

Related: [parent](../question.md), [plan](../../../plans/decoder-initialization-variation.md),
[strategy 2331](../../../runs/2026-10-06-2331/strategy.md),
[16 crossed-family adaptation](../16-crossed-family-adaptation/question.md),
[run 2229 analysis](../../../runs/2026-10-06-2229/analysis.md),
[run 2331 analysis](../../../runs/2026-10-06-2331/analysis.md),
[decision 2331](../../../runs/2026-10-06-2331/decision.md),
[proposal 0315](../../../runs/2026-10-07-0315/proposal.md),
[01 map bias](../../01-map-bias/question.md) (arrival versus evolutionary dynamics).

Reopen if parked or closed: a mechanism result elsewhere (e.g. learned context or a new bank)
needs this initial/ongoing split to interpret it; the population-preserving re-encoding is
shown flawed; or a bank with several covered BE cells makes the family dependence of the split
testable beyond the ten screened training cells.
