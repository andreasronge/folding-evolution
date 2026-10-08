---
status: closed
tags: [compositional-transfer, decoder, external-fitting, solver-corpus, feedback, context, token-control]
budget: {experiments: 1, used: 0}
---
# Does one feedback round increase the advantage of a contextual fit over a token-only fit?

Current summary: **closed (run 2156, training row 1, holdout row 4). On the training cells
feedback raised the contextual fit's advantage over the token-only fit: I = (C2/T2)/(C1/T1) =
1.169× [1.093, 1.250] over 32 lineages, while the token-only fit also improved (T2/T1 1.201×
[1.150, 1.255]). The interaction is concentrated in BE (1.34× [1.19, 1.50]); in PA it was not
resolved and sits inside ±10% (1.02× [0.95, 1.09]). Part of the mean effect is in the slow tail
(median-over-seeds variant 1.09× [1.008, 1.18], not pre-registered). On the three withheld cells
the interaction is unresolved, 1.087× [0.984, 1.200]: neither equality nor absence; C2 still
beats T2 there 1.37×.** Run 1707 found C1/T1 = 1.37× (training) and 1.29× (withheld); run 1924
found C2/C1 = 1.40× and 1.29×. Run 2156 scored T1 and T2 on the exact 1924 seeds, completing the
four-arm crossing. The quantity is the within-lineage interaction I = (C2/T2) / (C1/T1),
equivalently (C2/C1) / (T2/T1). The first attempt, run 2129, stopped at preparation on the
autonomous deadline (only a 160-row T2 timing block ran).

Competing explanations:
- A: The feedback increment is contextual. T2 ≈ T1 or T2/T1 well below C2/C1; I > 1.
  *Partly supported (2156): I > 1 on training, but T2/T1 is also 1.20×; of C2's 1.40× over C1
  on training, the token-only fit matched 1.20× and the interaction is 1.17×. Carried by BE.*
- B: Feedback improves the corpus for any fit (yield, diversity, which tapes). T2/T1 ≈ C2/C1;
  I ≈ 1 while both ratios exceed 1. *Not excluded for PA (I inside ±10%) or on the withheld
  cells (unresolved); rejected as the whole story for BE training cells.*
- C: Token frequency is what improved most; I < 1. *Excluded on training (lower bound 1.093);
  not excluded on the withheld cells.*

Scope: one feedback step, both second-round fits from corpora collected under C1, external
likelihood fitting (T is a restricted token fit, not the best token-only map), the reused
screened four-reducer bank and its three withheld cells. Does not isolate bigrams, yield or
diversity, and does not test a token-only self-updating lineage.

Related: [20](../20-solver-corpus-context/question.md), [21](../21-iterated-solver-corpus/question.md),
[concept plan](../../../plans/feedback-context-increment.md),
[iteration plan](../../../plans/iterated-solver-corpus.md),
[run 2129 infeasible](../../../runs/2026-10-07-2129/infeasible.md),
[run 2129 decision](../../../runs/2026-10-07-2129/decision.md),
[run 2156 analysis](../../../runs/2026-10-07-2156/analysis.md),
[run 2156 decision](../../../runs/2026-10-07-2156/decision.md).

Reopen if: a seed extension on these lineages or a replication with new lineages (fresh C1/C2/T1/T2 corpora; about 46 balanced
lineages put the holdout lower bound above 1 at the observed 1.09×, roughly twice that for good
power) is funded, or a mechanism study (start row, active tokens, BE versus PA) needs the
interaction on withheld cells. Both lineage and scoring-seed uncertainty matter (between-lineage
variance about 1.6× seed noise); a plug-in projection does not exclude resolution by more seeds
on these 32 lineages ([critique 2243](../../../runs/2026-10-07-2243/critique.md), note 6), so
price seed and lineage extensions before choosing.
