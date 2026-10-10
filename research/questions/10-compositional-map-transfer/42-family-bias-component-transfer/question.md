---
status: closed
tags: [compositional-transfer, family-specificity, component-transplant, external-fitting, fragments, independent-inputs]
budget: {experiments: 1, used: 0}
---
# Which acquired component carries the double-gate advantage: the library, the table, or their native combination?

Current summary: **closed after run 2026-10-10-2001 (answered at this scope: both components carry it,
and neither was shown to need its native partner).** In [41](../41-same-alphabet-family-preference/question.md) the 24 DG-built A8
builds (D) cost about a third of the 24 TS-built builds (T) on 8 never-searched DG cells. Each build is a
previous-token context table plus a literal 3–6-token block library. Run 2001 crossed tables and libraries
of the saved builds (24 frozen donor pairs, fresh seeds, arms table/library; ∅ = block edits off;
[analysis](../../../runs/2026-10-10-2001/analysis.md)). On the DG cells, failures at 2 × cap:

- **The fresh native gap reproduced:** T/T ÷ D/D 3.03× [2.28, 3.97] (1717: 2.98×).
- **Without libraries the D table is as far ahead as the native pair** (point estimates): T/∅ ÷ D/∅
  **3.26× [2.43, 4.30]**, 23/24 pairs, 8/8 cells.
- **The D library helps the T table:** 3.05× [2.32, 4.07] over no library (24/24 pairs). Its gain over the
  T table's own library, the primary R = T/T ÷ T/D, is **1.95× [1.43, 2.66]**: unresolved against the
  pre-set 1.5× margin (22/24 pairs > 1; 1 × cap 1.73× [1.33, 2.25]).
- **The hybrid does not reach the native D pair:** T/D ÷ D/D 1.55× [1.15, 2.09]; a residual above 1.5× is
  unresolved.
- **No native-pair dependence shown:** the D library beats the T library under the D table too (D/T ÷ D/D
  1.35× [1.10, 1.68]); the T library gives the D table no resolved gain (1.08× [0.86, 1.35]).
- **On TS cells the libraries are interchangeable:** T/D ÷ T/T 1.01× [0.83, 1.25]; D/T ÷ D/D 1.00×.
  The bare T table is cheaper than the bare D table there only at 2 × cap (1.43× [1.01, 2.00]; 1 × cap
  1.39× [0.98, 1.96]).

Competing explanations, after 2001:
- (a) portable D library: **partly** — active on a foreign table and free on TS, but its replacement value
  is unresolved against 1.5× and it does not recover all of D's advantage;
- (b) the D table carries it: **supported** (the bare D table alone shows a gap as large as the native
  one), but "transplanted libraries add little" is refuted; which component is larger depends on the order
  of swaps (library first 1.95×, then table 1.55×; table first 2.24×, then library 1.35×; point estimates);
- (c) native combination: **not supported** — no evidence that a library needs the table it was fitted with;
- (d) both contribute: **best fit**, sub-additively (table effect 3.26× bare, 2.24× with the T library,
  1.55× with the D library).

Not separable here: library content versus size and diversity (D libraries 7–32 fragments, no visible size
relation); why harder DG sources produced better components (source difficulty versus content); a join
motif. Bare tables were fitted while intermediate libraries were in use, so D/∅ is library-free search,
not library-free acquisition.

Scope: development data (DG bank `x4-double-gate-v1` spare cells, TS bank `x4-branch-sum-v1` targets),
saved 1717 builds, external fitting only, frozen; `v2_x4`, D625, cap 524 288; one family pair; inference
conditional on these rosters and the frozen donor assignment.

Opened 2026-10-10 (steward, run 2026-10-10-2001) on [strategy 2001](../../../runs/2026-10-10-2001/strategy.md)
and its [plan](../../../plans/family-bias-component-transfer.md). Slot 34 of root 10. Closed 2026-10-10.

Related: [41](../41-same-alphabet-family-preference/question.md), [40](../40-independent-input-protected-transfer/question.md),
[32](../32-learned-fragment-operator/question.md), [34](../34-chain-block-suffix-preservation/question.md),
[run 2001 proposal](../../../runs/2026-10-10-2001/proposal.md),
[run 2001 decision](../../../runs/2026-10-10-2001/decision.md), [log](log.md).

Reopen if: a decision comes to depend on whether a transplanted library's replacement value exceeds 1.5×
(e.g. acquiring libraries separately from tables on a new family), and about 5–10 further independent D/T
donor pairs can be acquired (≈ 35–70 min queue at 1717 acquisition cost); or a later experiment separates
library content from size or source difficulty and needs this crossing as its reference.
