---
status: closed
tags: [compositional-transfer, comparison-gate, external-fitting, partial-programs, eda, context, token-control, acquisition]
budget: {experiments: 1, used: 0}
---
# Can non-solving programs selected during short searches teach a useful context decoder?

Current summary: **closed after run 1831 (answered at this scope). Context fitted to tapes from
G4 searches that had not yet solved beats a token fit to the same tapes, C_S/T_S 1.28× [1.12, 1.45]
(13/16 corpora), and beats G4, C_S/G4 1.62× [1.37, 1.90] (16/16), on fresh searches of the
comparison-gate training cells. A worthwhile 1.20× over T is plausible, not established. The C/T
gain is mostly more searches solving within the cap (73% vs 66%); no speed difference was resolved
among pairs where both solved, 1.05× [0.88, 1.24] (selection-conditioned). It is BE-carried (BE 1.42× [1.17, 1.72]; PA 1.15× [0.96, 1.38], unresolved).
No parent enrichment was resolved: a fit to uniform population samples was within C_S/C_P
1.04× [0.92, 1.16] of the selected-parent fit. The exact-solver fit stays far faster (C_S/C_exact 0.27× [0.24, 0.30]), at about 7.9× more
source evaluations per cell.** Every useful fitted context before this ([20](../20-solver-corpus-context/question.md)–[26](../26-then-addition-fresh-bank/question.md))
was fitted to exact solvers. Plan: [partial-program context](../../../plans/partial-program-context.md).
Not shown: transfer (own training cells of a development bank only), order versus emitted
frequencies (K unscored), other collection horizons, or whether feedback rounds close the gap
to the exact fit.

Competing explanations:
- A: incomplete, selected programs already carry reusable order/assembly information; partial C
  beats partial T and G4 on fresh searches.
- B: the useful signal appears only after complete assembly (or is masked by training-perfect
  shortcuts); partial C is not worthwhile over partial T.
- C: any signal comes from the evolved population as a whole, not from extra parent selection;
  a uniform within-population fit does as well as the selected-parent fit.

Where they stand after run 1831: A's predictive claim supported on the training cells (the
context-fitting procedure beats T and G4; the carrying structure, order or otherwise, is
unidentified, K unscored); B not supported in its strong form,
though the both-solved decomposition and the 0.27× gap to C_exact leave room for much useful
structure to appear only with complete assembly; C consistent at the measured resolution
(parent enrichment above 1.16× excluded; a small enrichment or a loss up to about 8% is not).

Scope limits: external fitting (an EDA-style learning signal), not inheritance or selection among
decoders; comparison-gate-v1 training cells only (development bank); one collector horizon.

Related: [root 10](../question.md), [24](../24-comparison-gate-bank/question.md),
[run 1246](../../../runs/2026-10-08-1246/analysis.md), [strategy 1831](../../../runs/2026-10-08-1831/strategy.md),
[run 1831 analysis](../../../runs/2026-10-08-1831/analysis.md), [run 1831 decision](../../../runs/2026-10-08-1831/decision.md); feedback follow-up [28](../28-partial-program-feedback/question.md).

Reopen if: a feedback or EDA-style continuation needs this collector's frozen C_S/T_S/C_P rows
as its first-round reference, or a fresh bank frozen with the partial-fitting method is
built (to test transfer of partial-program fits); a precise 1.20× resolution alone would
need about 64 corpora (≈ 6 h queue) and is not by itself a reason.
