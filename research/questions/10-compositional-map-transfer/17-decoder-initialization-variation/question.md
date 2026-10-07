---
status: closed
tags: [compositional-transfer, decoder, token-multipliers, mechanism, initialization, variation, frozen-maps, fresh-start]
budget: {experiments: 2, used: 0}
---
# Does the learned token map help search through its starting programs, through the variation it produces during search, or both?

Current summary: **closed (2 of 2 slots). On all 13 cells tested, both parts of the learned map
help, each by about 1.3× given the other, and they overlap heavily; on the ten training cells the
balance between them differs by cell family.** Run 2026-10-06-2331 (commit `8f42f38`, row 3,
three withheld 2229 cells, 400 seeds): with identical generation-0 token tapes, searching under M
instead of G saves 1.39× [1.31, 1.47] (P1); with the search decoder held at M, starting from M's
programs saves 1.30× [1.24, 1.36] (P2); interaction −0.34 log2 [−0.40, −0.29]. Run 2026-10-07-0315
(commit `5dae3a6`, row 1, ten training cells, 200 seeds): P1 1.28× [1.22, 1.34], P2 1.33× [1.26,
1.40], diagonal 2.44× [2.23, 2.66], interaction −0.52 log2 [−0.62, −0.42]. The family balance
S = log2(T_MG/T_GM) is negative (start relatively heavier) on all four BE cells (−0.21 to −0.39,
each resolved) and −0.05 to +0.54 on the six PA cells (three resolved positive, none resolved
negative): C = BE − PA −0.45 log2, Welch 95% [−0.68, −0.22] over cells; 20/20 maps agree in
direction; robust to the cap and to leaving out any one cell. This is a relative difference: both
components are resolved positive within each family. 2331's withheld BE cell (S −0.27) lies in
the BE training range (different seeds; descriptive).
Fairly sure of the numbers; narrow in scope: 13 reused, screened cells from one bank (the ten
training cells are the ones the maps were selected on), 20 frozen maps, G4's hand-supplied
context, one population/operator/budget regime. Family is confounded with other cell properties:
across the ten cells S correlates with MM median cost (r 0.77, post hoc); at matched difficulty
the families still separate, but with 4 and 6 cells "family", "branch-else versus plus-arg
shape" and "difficulty tail" cannot be told apart, and nothing here says what a fresh cell would
do. The interaction is sub-additivity on capped log cost, consistent with — but not establishing
— a shared supply of useful partial programs. "Ongoing" bundles mutation, crossover, inherited
latent alleles and continued program supply. Generation-0 solves were rare (12/79 200 and
20/122 000), so direct solver seeding is unlikely to explain the start gain; which properties of
the starting population carry it is unresolved.

Competing explanations (status after both slots):
- I: The learned initial distribution carries the gain; MG ≈ MM. Not supported: P1 is 1.39×
  (lower bound 1.31×) on the withheld cells and 1.28× (1.22×) on the training cells. On BE
  training cells P1 is smaller (+0.20 log2 [0.11, 0.30], about 1.15×) but still resolved.
- O: Ongoing use of M carries it; GM ≈ MM. Not supported: P2 1.30× and 1.33× (lower bounds
  1.24×, 1.26×).
- B: Both contribute. Fits in both runs, with a strongly negative interaction (−0.34 and −0.52
  log2).
- R: Either alone gives nearly all of it. Partly: either alone gives most of the diagonal, but
  the second still adds a resolved 1.28–1.39×.
- Task-dependent balance: the relative weight of start and ongoing use differs between BE and
  PA cells. Supported on the ten training cells (C −0.45 [−0.68, −0.22]); not separated from
  composition shape or difficulty, and not tested on fresh cells.

Slot plan (strategy 2331), done: slot 1 = the three 2229 cells (row 3); slot 2 = the ten training
cells (row 1). Neither slot isolates mutation from crossover, matches solver frequencies, or bears
on learned context or on whether the maps are family-specific. On training cells each map is
in-sample for its own family's cells; S was set by the cell family, not the map family
(descriptive).

Related: [parent](../question.md), [plan](../../../plans/decoder-initialization-variation.md),
[strategy 2331](../../../runs/2026-10-06-2331/strategy.md),
[16 crossed-family adaptation](../16-crossed-family-adaptation/question.md),
[run 2229 analysis](../../../runs/2026-10-06-2229/analysis.md),
[run 2331 analysis](../../../runs/2026-10-06-2331/analysis.md),
[decision 2331](../../../runs/2026-10-06-2331/decision.md),
[run 0315 analysis](../../../runs/2026-10-07-0315/analysis.md),
[decision 0315](../../../runs/2026-10-07-0315/decision.md),
[01 map bias](../../01-map-bias/question.md) (arrival versus evolutionary dynamics),
[09 generic bias speed-up](../../01-map-bias/09-generic-bias-speedup/question.md) (supply versus
dynamics).

Reopen if parked or closed: a mechanism result elsewhere (e.g. learned context or a new bank)
needs this initial/ongoing split to interpret it; the population-preserving re-encoding is
shown flawed; or a bank with several covered BE cells makes the family dependence of the split
testable beyond the ten screened training cells (fresh BE and PA cells, or cells that vary shape
and difficulty independently); or a finer intervention (mutation-only versus crossover-only under
M, or a census of generation-0 partial programs) gets its own slot and needs this baseline.
