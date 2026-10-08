---
status: closed
tags: [compositional-transfer, comparison-gate, external-fitting, partial-programs, eda, feedback, acquisition, context, token-control]
budget: {experiments: 1, used: 0}
---
# Does collecting non-solving tapes under the partially fitted decoder teach a better frozen decoder than collecting the same allocation under G4?

Current summary: **closed after run 2116 (answered at this scope; root 10's 19th slot).
Spending two further rounds of partial-tape collection under the updated context decoder (F)
beat spending the same source allocation under G4 and fitting once (O): F/O 1.18× [1.01, 1.37]
(16 lineages, 2 × cap; 1 × cap 1.16× [1.01, 1.33]). The pre-stated rule labels this "adopt
feedback provisionally"; a worthwhile 1.15× gain is neither established nor excluded. The gain is
BE-carried: BE 1.42× [1.17, 1.72] (8/8 lineages), PA 0.98× [0.83, 1.16] (3/8). More G4 data did
not help (O/R 0.99× [0.89, 1.10]), and F over keeping the first fit is unresolved (F/R 1.16×
[0.99, 1.36]). Context feedback beat independent token feedback, F/TF 1.46× [1.23, 1.75]. The
exact-solver fit stays far ahead (F/C_exact 0.31× [0.25, 0.38]; its acquisition cost is
unmatched). Feedback sources solve about twice as often before the cap and leave more accurate
tapes in both families, so PA's unresolved result is not explained by yield.** Plan:
[partial-program feedback](../../../plans/partial-program-feedback.md);
[analysis](../../../runs/2026-10-08-2116/analysis.md).
Not shown: transfer (own training cells of a development bank only), equal actual evaluations
(F used 7.4% fewer), other horizons or round counts, order versus emitted frequencies (K
unscored), why PA tapes do not teach more under feedback.

Competing explanations:
- A (feedback): tapes from searches run under the updated decoder sit nearer complete assemblies
  and teach more; feedback beats equal-allocation one-shot.
- B (data quantity only): any gain over the first fit comes from more tapes; feedback ≈ one-shot.
- C (reinforcement/starvation): sources under the updated decoder solve sooner and contribute fewer,
  more self-similar tapes, or reinforce shortcuts; feedback is worse than one-shot.

Where they stand after run 2116: A supported at this scope for BE (overall lower bound 1.01);
B not supported (more G4 data added nothing, O/R 0.99×, while feedback collection added 1.18×);
C not supported overall (no starvation, no degradation; PA unresolved around 1).

Scope limits: external fitting (EDA-style), not inheritance or selection among decoders;
comparison-gate-v1 training cells only (development bank); one horizon; K unscored.

Related: [root 10](../question.md), [27](../27-partial-program-context/question.md),
[21](../21-iterated-solver-corpus/question.md), [22](../22-feedback-context-increment/question.md),
[run 1831](../../../runs/2026-10-08-1831/analysis.md), [run 2116 decision](../../../runs/2026-10-08-2116/decision.md).

Reopen if: a fresh bank is frozen together with a partial-acquisition method (feedback F versus
one-shot) to test transfer; a later design needs a partial-acquisition decoder and the choice
between F and O would change it (this run's frozen C1/C3/O/T3 tables and harness can serve); or
a mechanism for PA's missing gain (what PA pre-solve tapes lack) gives a concrete intervention to test.
Resolving the 1.15× margin by replication alone (about 600 lineages) is not a reason.
