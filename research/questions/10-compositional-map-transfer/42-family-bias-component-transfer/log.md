# Log: 42 family-bias component transfer

2026-10-10 (steward, run 2026-10-10-2001): opened from strategy 2001. Read-only check of the 1717 score
rows (`search.jsonl`, b5697a1): per-search log-cost SD (2 × cap) on DG is 1.62 (D) and 1.52 (T), on TS
1.45 / 1.37; build-level SD on DG 0.66 (D), 0.42 (T). Worker `envelope()` receives table and fragments
separately but binds them by cohort arm label; explicit table-owner / library-owner / operator-mode fields
are needed. D libraries hold 7–32 fragments, T libraries 32 (strategy inventory).

Decision: propose the 2 × 3 table × library crossing ([proposal](../../../runs/2026-10-10-2001/proposal.md))
because it is the allocated question and every input is saved; no new acquisition is needed.

## 2026-10-10: run 2026-10-10-2001, table × library crossing (slot 34 of root 10)

Experiment: commit `6dabda8`, code review pass, [analysis](../../../runs/2026-10-10-2001/analysis.md),
[execution](../../../runs/2026-10-10-2001/execution.md). The 24 D and 24 T builds of 1717 (hash-verified),
paired by a frozen permutation (seed 2001) into 24 donor pairs; six arms written table/library: D/D, T/T,
T/D, D/T, D/∅, T/∅ (∅ = block edits off). 8 DG spare cells + 8 TS target cells × 24 pairs × 2 fresh seeds ×
6 arms = 4 608 searches, complete, no errors; 16 native 1717 rows replayed bit-exact; shared-table arms
had identical initial populations; bare arms ran zero block events. Queue 89 min (timeouts 240).

Result (DG roster, primary; failures at 2 × cap; pair × seed bootstrap; "pairs" = donor pairs with ratio > 1):
- Solves of 384: D/D 312, T/T 199, T/D 264, D/T 288, D/∅ 291, T/∅ 133.
- Fresh native gap T/T ÷ D/D 3.03× [2.28, 3.97] (1717: 2.98×): references reproduce.
- **Primary R = T/T ÷ T/D 1.95× [1.43, 2.66]**, 22/24 pairs, 8/8 cells > 1: **unresolved** against the
  1.5× replacement margin (lower bound short by 0.07; pair-only bootstrap 1.51, paired t 1.46; 1 × cap
  1.73× [1.33, 2.25]). Leave-one-pair-out 1.80–2.05. Observed pair SD of log R 0.69 (planned 0.6).
  Resolution price: about 5 more independent pairs (two new acquisitions each), ≈ 35 min queue, only if
  the true R is near 1.95.
- Bare tables B = T/∅ ÷ D/∅ **3.26× [2.43, 4.30]** (23/24 pairs, 8/8 cells; 1 × cap 2.45× [1.94, 3.07]).
- D library on the T table vs none: T/∅ ÷ T/D **3.05× [2.32, 4.07]** (24/24); T library on its own table
  1.57× [1.23, 2.00].
- Residual G = T/D ÷ D/D 1.55× [1.15, 2.09] (hybrid reliably behind D/D; whether by > 1.5× unresolved).
- D library identity under the D table D/T ÷ D/D 1.35× [1.10, 1.68]; T library on the D table vs none
  1.08× [0.86, 1.35]; D library on its own table 1.45× [1.18, 1.79].
- One cell (`(X0+X3)>(X1+X2) ? X3:X0`) is the exception: R 1.06, G 3.82.
- D library size (7–32 fragments) shows no visible relation to per-pair R (Spearman 0.08); size versus
  content not separated.

TS roster (secondary): the four library arms solve 363–368/384 at 24–26 k evaluations; retention
T/D ÷ T/T 1.01× [0.83, 1.25] (loss above 1.25× excluded); D/T ÷ D/D 1.00× [0.79, 1.27]. Bare tables need a
library (D 1.99× [1.58, 2.52], T 1.52× [1.21, 1.91]). Bare T table cheaper than bare D table on TS:
1/B 1.43× [1.01, 2.00] at 2 × cap, 1.39× [0.98, 1.96] at 1 × cap (penalty-sensitive, below the 1.5× margin
used elsewhere). Native TS gap T/T ÷ D/D 0.92× [0.71, 1.20], still unresolved.

Against the explanations: (a) portable D library — partly: it is active on a foreign table and costs
nothing on TS, but its replacement value over the T library is unresolved against 1.5× and the hybrid stays
behind D/D; (b) D table carries it — supported for the table half (bare tables give a gap as large as the
native one, point estimates), but "transplanted libraries add little" is refuted; (c) native combination —
not supported: the D library is better than the T library under both tables, so no evidence that a library
needs the table it was fitted with; (d) both contribute — best fit, sub-additively (the table effect
shrinks from 3.26× bare to 2.24× with the T library and 1.55× with the D library).

Not shown: why the D components are better (content versus size, source difficulty); fresh-bank transfer;
inheritance. Reopen clause of [41](../41-same-alphabet-family-preference/question.md) ("a component whose
family dependence the bundled design could not see") is only weakly touched: the bare-table TS direction is
resolved at 2 × cap only and below 1.5×; 41 stays closed.

Decision: close 42 at this scope and return to strategy (`next: strategy`) because its question is answered
in the form that matters for the next choice: both components carry the DG advantage — the bare DG table alone
shows a gap as large as the native one, and the DG library adds a portable increment that does not depend on its
native table and costs nothing on TS (which is larger depends on the order of swaps: library first 1.95× then
table 1.55×, table first 2.24× then library 1.35×). Whether
that increment exceeds 1.5× is unresolved, but resolving it would not change which components a learner
must acquire (both). Root 10's 34 slots are used and the strategy asked for a review after this result.
([decision](../../../runs/2026-10-10-2001/decision.md))
