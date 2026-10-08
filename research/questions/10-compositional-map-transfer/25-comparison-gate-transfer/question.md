---
status: open
tags: [compositional-transfer, comparison-gate, external-fitting, solver-corpus, context, token-control, holdout, family-specificity]
budget: {experiments: 1, used: 0}
---
# Do the frozen comparison-gate corpus fits keep context's advantage over token fitting on the eight protected holdout compositions?

Current summary: **open (opened by the steward after run 1246; proposed for run 1534).**
Run 1246 ([24](../24-comparison-gate-bank/question.md)) fitted C (previous-token table) and T
(24 token multipliers on G4) to 16 independent G4 solver corpora on the comparison-gate bank's
4 + 4 training cells; on those cells C/T was 3.11× [2.78, 3.48]. All 32 tables, the 8 holdout
ids (4 BE, 4 PA, one per repeated reducer, chosen performance-blind), the 4 352-search roster,
seeds and endpoint were frozen in run 1246's `freeze.json` before any holdout search. No
holdout has been searched. This is the tree's first transfer test with several protected
compositions per family; root 10's earlier holdout evidence rests on one BE and two PA cells.

Competing explanations:
- A: The tapes carry assembly information that is reusable on new compositions of the same
  primitives; holdout C/T resolves above 1, perhaps shrunk from 3.1× (old bank: 1.37× → 1.29×).
- B: C's training gain is specific to the cells it was fitted on (overfitting the source
  compositions); on holdouts C/T ≈ 1 or below, bounded under 1.10×.
- F: The gain transfers mainly within the training family; matched-family holdouts show a
  larger C/T than mismatched ones (secondary, interval only).

Scope limits fixed in advance: C versus the restricted token fit, not an isolated token-order
mechanism (K unscored); external fitting, not evolutionary acquisition; one bank, cap and
shrinkage; 8 holdouts, so task-to-task spread is reported per holdout, not inferred.

Related: [root 10](../question.md), [24](../24-comparison-gate-bank/question.md),
[20](../20-solver-corpus-context/question.md),
[plan](../../../plans/comparison-gated-transfer.md),
[analysis 1246](../../../runs/2026-10-08-1246/analysis.md),
[decision 1246](../../../runs/2026-10-08-1246/decision.md).

Reopen if parked: an unresolved holdout C/T whose interval an affordable number of fresh
corpora (priced from 1246's 423 s per extra corpus plus holdout scoring) could resolve, or a
fresh bank on which the same frozen procedure can be tested.
