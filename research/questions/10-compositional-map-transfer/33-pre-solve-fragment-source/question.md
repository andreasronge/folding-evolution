---
status: closed
tags: [compositional-transfer, fragments, library-learning, partial-programs, external-fitting, block-edit, acquisition]
budget: {experiments: 1, used: 0}
---
# Can a fragment library extracted from pre-solve programs speed fresh search beyond C-chain blocks?

Current summary: **no worthwhile increment for this source and extractor on then-addition (run
2026-10-09-1350, commit `e9a04f8`); closed.** The 0843 extractor (all-active 3–6-token windows,
≥ 2 source cells, ranked by cell count then raw occurrence, top 32), applied to selected parents
archived before their 1831 source search first solved, fills 32/32 in all 16 corpora. Inserted as
block edits on C's unchanged search (E), it is not resolved from C-chain blocks with E's length law
(W_E): **E/W_E 0.981× [0.911, 1.057]**, 7/16 corpora above 1; a gain above about 1.06× is excluded
at this scope, a small gain or loss is not. The pooled 1.10 bound holds under both cap/both-solved
sensitivities and in BE; PA remains unresolved at 1.10 (upper bound 1.122).
Paired against 1036's rows (replayed bit-exactly): E is resolved slower than the exact-solver
library, **E/F 0.843× [0.795, 0.892]** (0/16 corpora above 1), and not resolved from W
(E/W 1.007× [0.948, 1.070]); E/C 1.235× is similar in point estimate to W/C (1.227×), but no
additional E/W gain was resolved and W_E/W 1.026× [0.942, 1.117] leaves a length-law effect open. Pre-registered
rule 3 fired: this source/extractor ends at this scope.

Descriptive (not tested): the pre-solve libraries share their reducer/add syntax with the exact
libraries but contain no `gt` token; the exact libraries' comparison joins (`input first gt`,
`first gt if_gt`) are replaced by reducer→`if_gt` windows. E solvers contain exact-library `gt`
joins no more often than C-chain-arm solvers (about 64%), F solvers more often (78%).

Competing explanations, after 1350:
- **Shared syntax carries F's increment** (E ≈ F, E > W): not supported here; E/F resolved below 1
  and E/W ≈ 1, though E also differs from F in source and length law.
- **Gate joins carry it** (E ≈ W): consistent with the result and the lexical difference, but
  untested; no knock-in/knock-out of the joins was run.
- **Pre-solve windows mislead** (E < W): not supported; E/W_E's interval includes 1. E does drive
  populations into near-alias (training-perfect, inexact) regions about 3× as often as W_E.

Scope: external extraction, frozen library, C held fixed (fitted from exact solvers), one source
selection (lowest-slot parents at generations 64/128/256), one extractor, development bank
then-addition-v1. Not per-individual inheritance, not a complete early-data pipeline, not a
verdict on pre-solve learning in general. Cost: pre-solve collection 5 058 worker-s (about a tenth
of the exact corpus), extraction 8.6 worker-s; E costs 0.39 worker-s per search more than W_E.

Opened 2026-10-09 (steward, run 1350) under [strategy 1350](../../../runs/2026-10-09-1350/strategy.md)
and the [plan](../../../plans/pre-solve-fragment-acquisition.md).

Related: [32](../32-learned-fragment-operator/question.md),
[27](../27-partial-program-context/question.md), [28](../28-partial-program-feedback/question.md),
[run 1350 decision](../../../runs/2026-10-09-1350/decision.md), [log](log.md).

Reopen if: a different pre-solve source or extractor comes with a measured reason to expect it to
recover F's increment (e.g. a probe showing its libraries contain the exact libraries' `gt` joins,
or a join knock-in/knock-out showing those joins carry F/W, which would tell a source what to
supply), or an acquisition design needs E as a frozen benchmark on another bank.
