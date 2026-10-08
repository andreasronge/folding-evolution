---
next: strategy
---
# Decision — run 2026-10-07-2156

**Close [22](../../questions/10-compositional-map-transfer/22-feedback-context-increment/question.md)**
(training row 1, holdout row 4). No proposal for 2243: every question in the tree has 0 slots left
(root 10 used 15 of 15, root 01 spent), and the autonomous run's deadline (22:25) has passed.

**Why close.** The pre-registered primary contrast is answered. On training cells feedback raised
the fitted context's advantage over the token-only fit, I = 1.169× [1.093, 1.250]. The token-only
fit also improved (T2/T1 1.201× [1.150, 1.255]). The run was clean and complete: all validation,
64/64 replays, full holdout. The unresolved part is the interaction on the withheld cells,
1.087× [0.984, 1.200]. Rerunning this design would not settle it. There, between-lineage
variance exceeds seed noise, so it needs new lineages (new C1/C2/T1/T2 corpora): about 46
balanced lineages to put the lower bound above 1 at the observed effect, about twice that for
good power. That is a new allocation, recorded as 22's reopen condition, not a continuation.

**Caveats that travel with the result.** The interaction is BE-carried (BE 1.34× [1.19, 1.50],
PA 1.02× [0.95, 1.09]). A non-registered median-over-seeds variant shrinks it to 1.09× [1.008,
1.18], so part of the mean effect sits in the slow tail. The C rows and seeds are 1924's, so this
extends that run and does not replicate it independently. T is a restricted token fit.

**What I would put to the strategist** (in my order of preference):
1. **Wrap up root 10's external-fitting line at its current answer.** Fitted previous-token
   context beats token-only fitting and transfers (1.29×). One feedback step adds 1.29–1.40×,
   and on training cells it is partly contextual (BE). The root's open gaps are different
   problems: family-specific transfer beyond this one-BE-holdout bank, and whether any
   selection-based process reaches what external fitting reaches.
2. **If the owner wants the transfer question settled:** a holdout-focused replication with
   about 90 new lineages (45 per family) and fresh corpora, scored on the three withheld cells
   only. This is a rough projection from 1707/1924 costs: about 500 worker-s of G4 collection
   plus about 150 under C per lineage, plus four-arm holdout scoring, so roughly 2.5–3 h. It is
   decision-sized but refines a 1.09× effect on a reused bank.
3. **BE versus PA.** Why does the interaction (and 1707/1924's larger BE gains) concentrate in BE?
   This needs an active-token or start-row analysis on the saved tables. It is cheap in compute but
   needs new instrumentation, and the family split is confounded with shape and difficulty on
   this screened bank.
C3 (a second feedback step) remains unfunded. Nothing here argues for it over 1–3.

**Parked questions.** I re-checked 02, 04, 07, 08 and 09. None of their reopen conditions is met:
this run concerns external fitting on root 10's bank, not helpers, thresholds or the veto design.

**Digest check (critique 2156).** Note 5 ("fits in well under an hour") and note 6 ("never
evaluated", "before any primary search") are fixed. Question 22's summary has been rewritten,
and a wording-correction entry has been appended to its log, ahead of the 2156 result entry.
