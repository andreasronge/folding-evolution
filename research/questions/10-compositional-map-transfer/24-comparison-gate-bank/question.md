---
status: closed
tags: [compositional-transfer, task-bank, comparison-gate, external-fitting, solver-corpus, context, token-control]
budget: {experiments: 1, used: 0}
---
# Does a reducer-comparison bank give a protected multi-holdout test, and does corpus context still beat token fitting on its training cells?

Current summary: **closed, answered (run 2026-10-08-1246, commit `5dd86bd`, 1 of 1 slot).**
Yes to both parts, at this bank's scope. The comparison gate replaces the sign gate: BE
`A>B ? C : D+E` and PA `(A>B ? C : D)+E`, 13 tokens each, A–E from SUM/MAX/MIN/FIRST with one
repeat. The exact ≤ 9-token screen keeps 37 BE and 56 PA behaviours (not a 13-token minimality
certificate). A frozen, performance-blind split gives 4 training and 4 untouched holdouts per
family with matched token totals; G4 solves 68% of training-cell searches at 524k, so there is
headroom. Over 16 independent solver corpora, the context fit C solved fresh training-cell
searches **3.11× [2.78, 3.48]** sooner than the token-only fit T to the same tapes (16/16
corpora, 64/64 corpus × cells; BE 2.86×, PA 3.37×; 1 × cap 2.82×), with collection yield 58.9%.
Both fits beat G4 descriptively (C 5.8×, T 1.9×). Scope: training cells only (each cell was its
fit's source), C versus the restricted token fit (emitted frequencies not controlled), one
bank, cap and shrinkage. Transfer to the frozen holdouts is
[25](../25-comparison-gate-transfer/question.md).

Competing explanations for stage 1 (training cells only):
- A: The solver tapes still carry assembly information beyond token frequency on these longer
  gated tasks; C/T > 1 as on the old bank (1707: 1.365×).
- B: The old-bank advantage came from that bank's short shapes; on 13-token GT-gated tasks a
  token-only fit does as well (C/T ≈ 1).
- E: Collection yield or search cost under G4 is too low to fit useful tables at this cap.

Status of the explanations after 1246: A consistent (C/T 3.11×); B ruled out on training
cells (lower bound 2.78); E not supported (yield 59%, collection 80 min).

Related: [root 10](../question.md), [25](../25-comparison-gate-transfer/question.md),
[analysis 1246](../../../runs/2026-10-08-1246/analysis.md), [20](../20-solver-corpus-context/question.md),
[15](../15-four-reducer-family-bank/question.md),
[plan](../../../plans/comparison-gated-transfer.md),
[strategy 1246](../../../runs/2026-10-08-1246/strategy.md).

Reopen if: the bank itself is found defective (a canonical, label or screen error in
`comparison_gate` bank `df3476d0…`), or 25 needs the training-cell C/T re-measured under a
changed fitting rule.
