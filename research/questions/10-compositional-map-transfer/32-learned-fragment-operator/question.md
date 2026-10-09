---
status: closed
tags: [compositional-transfer, comparison-gate, fragments, library-learning, variation-operator, external-fitting, block-edit]
budget: {experiments: 2, used: 0}
---
# Do executable fragments learned from training solvers make fresh search faster than the fitted context table C?

Current summary: **yes at the tested scope, and the advantage held on excluded compositions
(runs 2026-10-09-0843, commit `e347793`, and 2026-10-09-1036, commit `348f9e2`); closed.** C is
a previous-token table fitted to G4 exact-solver tapes. It beats a token-only fit about 2–3×, and
frozen pooled or positional frequency projections and random width-matched recoding do not
reproduce it (29–31). On top of C's unchanged search, each non-elite child (p 0.2) gets one intact
3–6-token fragment from a library of 32 knockout-active windows recurring in the corpus's
training solvers.

- **Training cells (0843, leave-one-cell-out libraries):** F/C **1.57× [1.42, 1.75]** (16/16
  corpora, both families), F/B 1.60× [1.45, 1.77] against blocks from the library's per-position
  marginals, F/W **1.23× [1.12, 1.36]** against blocks sampled from C's own chain. W/C 1.28×
  [1.17, 1.39]. B/C 0.98× [0.93, 1.04]: no resolved gain; gains above about 4.4% excluded at
  this scope, a small loss not.
- **Excluded compositions (1036, frozen whole-corpus libraries, no B arm):** on then-addition-v1
  (`A>B ? C+D : E`, 16 cells × 16 corpora × 16 seeds) F/C **1.47× [1.38, 1.56]** (16/16 corpora),
  F/W **1.20× [1.11, 1.29]** (14/16; both-solved 1.15× [1.09, 1.22]), W/C 1.23× [1.15, 1.31].
  On the 8 protected comparison-gate holdouts (reference) F/C 1.75× [1.57, 1.95], F/W 1.27×
  [1.17, 1.38], W/C 1.38× [1.23, 1.56]. The change of F/C from training to then-addition,
  0.93× [0.83, 1.05] (descriptive; different library construction), is unresolved, whereas C/T
  lost a third across the same shape change. Pre-registered rule 2 fired:
  `repertoire_earns_acquisition_review`. The F/W lower bound clears the worthwhile 1.10× by only
  1%, and not in the both-solved or BE-only sensitivities, so a true increment above 1.10× is
  not established.

Scope and limits: development banks only (then-addition-v1 was fresh for 1548, not here). The
libraries are mostly the banks' shared 3–5-token syntax (`input first gt`, `add input first`),
which then-addition needs by construction, so this shows reuse of one externally fitted
literal-block procedure across one shape change, not modularity, fresh-bank transfer, family
specificity or acquisition. On this shape F/W does not separate intact content from changed
token supply (no B). The gain is uneven across cells: F/C 0.99–2.17× on training cells
(descriptive; on `BE:F>S?F:M+m` F/C is unresolved, 0.99× [0.70, 1.41], and F is worse than W in
the descriptive comparison, 0.79× [0.65, 0.96]); F/W 0.96–1.54× on then-addition cells, 5/16
resolved, negatively correlated with W/C across cells (r −0.67, post hoc), so fragments and chain
blocks may partly substitute. Why W beats C is not isolated: C's point mutation re-decodes the
whole suffix, the block arms keep it, so W/C bundles local, suffix-preserving editing with
chain-sampled content. Solvers under F carry more library windows (occurrence, not ancestry).
Cost: F saves about 0.5 worker-s per search over W on then-addition; extraction is 4 s, but the
shared solver corpus cost 48 039 worker-s.

Competing explanations for the F gain: (a) learned joint content — supported over B and W on
training cells and over W across shape; (b) extra contiguous editing — W and B rule out "more
mutation" as the whole story; (c) the re-encoding path's suffix preservation — part of W/C,
unseparated; (d) memorization of the scored cell's solutions — not needed: the gain holds on
holdouts and on then-addition, where no fragment solves a cell when NOP-padded; (e) changed token
supply — excluded for B on training cells, untested across shape.

Open follow-ons, not allocated (strategy decides): whether evolution can acquire such a
repertoire, and at what source cost; why a library-free chain block beats C's point mutation;
reuse on a bank fresh to the method.

Closest technique: run-transferable libraries ([Keijzer, Ryan & Cattolico 2004](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)),
adaptive representation through learning ([Rosca 1995](https://cdn.aaai.org/Symposia/Fall/1995/FS-95-01/FS95-01-011.pdf)),
[DreamCoder](https://arxiv.org/abs/2006.08381) (abstraction learning plus a search guide; this
tests literal blocks only).

Related: [20](../20-solver-corpus-context/question.md), [24](../24-comparison-gate-bank/question.md),
[25](../25-comparison-gate-transfer/question.md), [26](../26-then-addition-fresh-bank/question.md),
[29](../29-frequency-matched-transfer/question.md), [31](../31-distribution-preserving-recoding/question.md),
[plan](../../../plans/learned-executable-fragments.md), [strategy 0826](../../../runs/2026-10-09-0826/strategy.md),
[run 0843 decision](../../../runs/2026-10-09-0843/decision.md),
[reuse plan](../../../plans/fragment-reuse.md), [strategy 1036](../../../runs/2026-10-09-1036/strategy.md),
[run 1036 decision](../../../runs/2026-10-09-1036/decision.md), root 23 (acquisition by
inheritance, [question](../../23-heritable-variation-bias/question.md)), root 01's cheap-join result
([findings items 4–16](../../../../docs/map-bias/findings.md)).

Reopen if: an acquisition design needs a frozen-F benchmark this question has not measured
(e.g. F on a bank fresh to the method, F with a supply control on an excluded shape, or F built
from fewer or cheaper source tapes), or a test of why block edits beat C's point mutation has a
specific rationale and price.
