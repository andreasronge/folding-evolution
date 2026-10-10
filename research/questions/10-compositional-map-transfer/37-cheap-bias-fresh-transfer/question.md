---
status: closed
tags: [compositional-transfer, acquisition-cost, fresh-bank, solver-corpus, fragment-library, external-fitting]
budget: {experiments: 1, used: 0}
---
# Does the cheap adaptively acquired bias (A8) keep its usefulness on a fresh bank?

Current summary: **closed after run 2026-10-09-2303: on one fresh bank, the frozen cheap
acquisition A8 was not materially slower than the full pipeline and was clearly useful; whether it
is faster or slower is unresolved.** On `two-sum-v1` (`A>B ? C+D : E+F`, 16 cells pinned on labels
before any search), cost(A8)/cost(full F) was **0.945× [0.819, 1.092]** (16 corpora, 4 seeds per
cell; a loss of 1.20× or more excluded, a 9% loss or an 18% gain not). All fitted arms beat G4:
G4/A8 2.73× [2.36, 3.17], G4/full F 2.58× [2.28, 2.90]; solves A8 51%, full F 49%, S8 47%, G4 20%.
Static collection was again slower than adaptive: S8/A8 1.173× [1.036, 1.327] (2033: 1.126×). With
acquisition charged (A8 6.5 M, full F 61.3 M evaluations), A8 is cheaper than full F and S8 at
every reported horizon up to 4 096 searches. The bank is much harder than then-addition (G4 solves
0.63 → 0.20) and the fitted arms' lead over G4 grew. Intervals condition on the 16 selected cells.

Competing explanations, as tested: (a) A8 keeps parity on new compositions: consistent on this
one shape, not shown in general; (b) A8 is narrower, its adaptive half specialising to development
shapes: a 1.20× loss is excluded and S8 (no adaptive half) was again slower, so no sign of it here;
(c) neither fitted pipeline helps on the new shape: refuted here (both 2.6–2.7× over G4).

Scope: one fresh output-composition shape (16 tokens, familiar `+` joins) on D1331, frozen
development-bank acquisitions (no new sources), external fitting, capped evaluation cost. The
≤9-token screen leaves 10–15-token shortcuts possible. Not addition in the predicate, not
new-source replication, not inherited adaptation. Decoder versus library and yield versus content
remain bundled.

Bank: the strategist's gate-addition shape `(A+B)>C ? D : E` failed the existing ≤9-token screen
(4 of 124 behaviours survive; the mirror `A>(B+C)` adds 5 near-duplicates). One pre-specified
replacement, the two-sum shape `A>B ? C+D : E+F`, leaves 76 eligible behaviours
([probe](../../../runs/2026-10-09-2303/semantic-probe.json)). See the [log](log.md).

Opened 2026-10-09 (steward, run 2303) under [strategy 2303](../../../runs/2026-10-09-2303/strategy.md)
and the [plan](../../../plans/cheap-bias-fresh-transfer.md); slot 29 of root 10. Closed 2026-10-10.

Related: [36](../36-sparse-source-feedback/question.md), [35](../35-small-source-acquisition/question.md),
[32](../32-learned-fragment-operator/question.md), [26](../26-then-addition-fresh-bank/question.md),
[proposal](../../../runs/2026-10-09-2303/proposal.md),
[analysis](../../../runs/2026-10-09-2303/analysis.md),
[decision](../../../runs/2026-10-09-2303/decision.md), [log](log.md).

Reopen if: a decision comes to depend on the sign of A8 versus full F (about 95 corpora at the
observed spread, or a cheaper design), or on transfer to a structurally different shape (for
example addition in the predicate on a domain where it survives the screen); or a new acquisition
procedure needs this fresh-bank comparison as its baseline.
