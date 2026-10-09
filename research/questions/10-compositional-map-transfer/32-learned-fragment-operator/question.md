---
status: open
tags: [compositional-transfer, comparison-gate, fragments, library-learning, variation-operator, external-fitting, block-edit]
budget: {experiments: 1, used: 0}
---
# Do executable fragments learned from training solvers make fresh search faster than the fitted context table C?

Current summary: **on the comparison-gate training cells, yes, and by more than expected
(run 2026-10-09-0843, slot 23, commit `e347793`); reuse on excluded compositions is untested
and awaits strategy review.** C is a previous-token table fitted to G4 exact-solver tapes. It
beats a token-only fit about 2–3×, and frozen pooled or positional frequency projections and
random width-matched recoding do not reproduce it (29–31). On top of C's unchanged search, giving
each non-elite child (p 0.2) one intact 3–6-token fragment, taken from a leave-one-cell-out
library of 32 knockout-active windows recurring in the corpus's other training solvers, made
search **1.57× [1.42, 1.75]** cheaper than C (16 corpora × 4 cells × 32 paired seeds; 16/16 corpora
favour F; both families). F also beats blocks drawn from the library's per-position marginals
(F/B 1.60× [1.45, 1.77]) and blocks sampled from C's own chain (F/W 1.23× [1.12, 1.36]). A
library-free block edit helps on its own: W/C 1.28× [1.17, 1.39]. Marginal blocks do not:
B/C 0.98× [0.93, 1.04], so a gain above about 1.04× is excluded for B; a small loss is not.

Scope and limits: own training cells of a development bank. The leave-one-cell-out libraries
are mostly the bank's shared 3-token syntax and barely differ between held-out cells, so this
is within-bank reuse, not transfer. The gain is uneven across cells (F/C 0.99–2.17×,
descriptive; on `BE:F>S?F:M+m` F is no better than C and worse than W). Why W beats C is not
isolated: C's point mutation re-decodes the whole suffix, while the block arms keep it, so W/C
bundles local, suffix-preserving editing with chain-sampled content. B shares the locality and
gains nothing, which argues against locality alone, but B's content may be harmful, so it is
not a clean locality control. Solvers under F carry more library windows (occurrence, not
ancestry). Nothing here bears on evolutionary acquisition: the library is externally fitted.

Competing explanations for the F gain: (a) learned joint content — supported over B and W at
this scope; (b) extra contiguous editing — W and B rule out "more mutation" as the whole
story; (c) the re-encoding path's suffix preservation — part of W/C, unseparated; (d)
memorization of the scored cell's solutions — guarded by leave-one-cell-out libraries, but
these share most fragments, so held-out compositions are the real test.

Next stage (not allocated): frozen whole-corpus libraries on the 8 protected comparison-gate
holdouts and the then-addition cells, F against C and, per the analysis, W. Measured price for
F and C: 3 072 searches each, ~71 queue min, ~3.85 h with agents (training-rate extrapolation;
holdouts can be harder); adding W ~+35 queue min.

Closest technique: run-transferable libraries ([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)),
adaptive representation through learning ([Rosca 1995](https://cdn.aaai.org/Symposia/Fall/1995/FS-95-01/FS95-01-011.pdf)),
[DreamCoder](https://arxiv.org/abs/2006.08381) (abstraction learning plus a search guide; this
tests literal blocks only).

Related: [20](../20-solver-corpus-context/question.md), [24](../24-comparison-gate-bank/question.md),
[25](../25-comparison-gate-transfer/question.md), [26](../26-then-addition-fresh-bank/question.md),
[29](../29-frequency-matched-transfer/question.md), [31](../31-distribution-preserving-recoding/question.md),
[plan](../../../plans/learned-executable-fragments.md), [strategy 0826](../../../runs/2026-10-09-0826/strategy.md),
[run 0843 decision](../../../runs/2026-10-09-0843/decision.md), root 01's cheap-join result
([findings items 4–16](../../../../docs/map-bias/findings.md)).

Reopen if: (when parked or closed) the strategist allocates the reuse stage; or a different
extractor/operator, or a test of why block edits beat C's point mutation, has a specific
rationale and price.
