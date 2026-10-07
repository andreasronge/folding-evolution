---
status: open
tags: [compositional-transfer, decoder, external-fitting, solver-corpus, feedback, context, token-control]
budget: {experiments: 1, used: 0}
---
# Does one feedback round increase the advantage of a contextual fit over a token-only fit?

Current summary: **open (strategy 2129); first attempt, run 2129, stopped before any primary
search because the autonomous deadline left too little time (row 0, no result; slot unused).
Its preflight validated all tables, the saved C1/C2 roster and 64/64 deterministic replays, and
timed T2 (160/160 solved, 0.34–0.67 worker-s per search). Re-proposed as run 2156 without the
deadline cutoff.** Run 1707 found the previous-token fit C1 faster than
the token-only fit T1 (1.37× training, 1.29× withheld). Run 1924 found the feedback refit C2
faster than C1 (1.40×, 1.29×). The token-only fit to the same feedback corpus, T2, was saved but
never evaluated, so we do not know whether feedback made context more valuable or improved any
fit to that corpus equally. The quantity is the within-lineage interaction
I = (C2/T2) / (C1/T1), equivalently (C2/C1) / (T2/T1).

Competing explanations:
- A: The feedback increment is contextual. T2 ≈ T1 or T2/T1 well below C2/C1; I > 1.
- B: Feedback improves the corpus for any fit (yield, diversity, which tapes). T2/T1 ≈ C2/C1;
  I ≈ 1 while both ratios exceed 1.
- C: Token frequency is what improved most; I < 1. Context may still help within C2.

Scope: one feedback step, both second-round fits from corpora collected under C1, external
likelihood fitting (T is a restricted token fit, not the best token-only map), the reused
screened four-reducer bank and its three withheld cells. Does not isolate bigrams, yield or
diversity, and does not test a token-only self-updating lineage.

Related: [20](../20-solver-corpus-context/question.md), [21](../21-iterated-solver-corpus/question.md),
[concept plan](../../../plans/feedback-context-increment.md),
[iteration plan](../../../plans/iterated-solver-corpus.md),
[run 2129 infeasible](../../../runs/2026-10-07-2129/infeasible.md),
[run 2129 decision](../../../runs/2026-10-07-2129/decision.md).

Reopen if: (not parked)
