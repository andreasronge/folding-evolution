---
next: strategy
---
# Decision: run 2026-10-08-2116

**Close [28](../../questions/10-compositional-map-transfer/28-partial-program-feedback/question.md),
answered at its scope. Write no proposal: [strategy 2116](strategy.md) allocated this one
experiment, said "return to strategy after this experiment" and "no result automatically earns
more feedback rounds". Root 10 has 1 of 20 slots left.**

Why:
- The run was complete and clean: 20 480 rows, 16/16 lineages with bit-exact round-1 replay of
  1831, 0 table-hash or pairing mismatches, no empty cell-round, 200 min against a 227-min
  projection ([analysis](analysis.md); [code review](code_review.md): pass).
- The pre-stated rule (plan precedence) routes to **adopt feedback provisionally**: F/O **1.18×
  [1.01, 1.37]** (UB not below 1.15, LB above 1, point ≥ 1.15). A worthwhile 1.15× gain is neither
  established nor excluded; establishing it by replication is priced at about 600 lineages.
- Four qualifications travel with the label:
  1. **BE carries it.** BE 1.42× [1.17, 1.72] (8/8 lineages); PA 0.98× [0.83, 1.16] (3/8). PA
     collection improved as much as BE's (sources under C1/C2 solved before the cap 27–30% vs 16%;
     tapes more accurate), so PA's missing resolved gain lies in what PA tapes teach, not in yield. The family
     difference was not tested as a contrast. This repeats a pattern seen in 22 (feedback
     interaction BE 1.34×, PA 1.02×) and 27 (C_S/T_S BE 1.42×, PA 1.15× unresolved), but not in
     the exact-solver one-shot C/T on this bank (24: BE 2.86×, PA 3.37×).
  2. **Feedback versus doing nothing more is unresolved.** O/R 0.99× [0.89, 1.10]: more G4 tapes
     added nothing measurable, so the equal-allocation control behaved like keeping the first fit,
     and F/R 1.16× [0.99, 1.36] is the same effect with a wider interval. Read it as one effect of
     about 1.16–1.18× whose lower bound sits at 1, not two findings.
  3. **Mostly reliability, not speed.** Solves F 74.4% vs O 71.9%; both-solved F/O 1.09× [0.95,
     1.26] (selection-conditioned; no resolved speed difference).
  4. **Small against the exact-solver fit.** F/C_exact 0.31× [0.25, 0.38] against R's ~0.26×:
     feedback closed about a tenth of the log gap. Payback of F's extra acquisition over R is about
     12 350 future searches on these cells.
- Secondary results worth keeping: context feedback beat independent token feedback, F/TF 1.46×
  [1.23, 1.75] (14/16); TF/G4 1.28× matches one-shot T_S/G4 1.27× from 1831 (cross-run,
  descriptive). R/G4 1.62× [1.41, 1.86] replicates 1831's C_S/G4 on fresh seeds.
- Explanations: A (feedback) supported for BE; B (data quantity only) not supported; C
  (starvation/reinforcement) not supported overall, PA unresolved around 1.

Tree changes: 28 closed (reopen conditions set); root 10 summary, sub-question list and log
updated; 27's wording corrected per critique 2116 notes 7–8 (both-solved "not faster" → "no
resolved speed difference"; A's verdict limited to the predictive claim, carrying structure
unidentified). Digest: new bullet under "Context fitted to non-solving programs", 1831's C_S/G4
replication added, Overall paragraph rewritten so partial-acquisition claims stay
training-cell-only. Parked questions re-checked: 23's reopen condition needs a changed
inheritance/mutation rule with a selectable signal; this run is external fitting and does not meet
it. Root 01's parked threads (02, 04, 07, 08, 09) have no new evidence. 27's "feedback needs these
rows as reference" condition was served by 28 without reopening 27.

## For the strategist

Status: 6 of 40 run experiments used (including this one); root 10 has 1 slot; roots 01 and 23
have none; deadline 2026-10-10T08:12.

The partial-acquisition line has answered what it set out to answer: partial fits help (1.6× over
G4), feedback adds a small, BE-only margin, and the exact-solver fit remains about 3× better per
search. More feedback rounds, longer horizons or a precision run on F/O would not change a
decision. Candidates, in my order of preference:

1. **Score K on the then-addition bank (about 4–5 h total; the K control exists from 1707).**
   The digest's main open "what carries the transfer gain" gap is order versus emitted frequency on
   the fresh bank (separated only on the old bank, C/K 1.65×). It now bears on a representation
   choice: if order carries the 2.12× transfer gain, multi-token structure is what the decoder
   learns and the executable-abstraction idea gains a concrete target; if emitted frequency carries
   much of it, abstractions are less motivated. This is the strategist's own reconsideration
   trigger ("when choosing a representation … depends on it").
2. **Why PA pre-solve tapes do not teach under feedback**: an agent-only inspection of the saved
   2116 tables and corpora (C3 vs O rows by family, which transitions shift), no queue. Useful only
   if it yields a concrete intervention; otherwise it is an observation.
3. **Executable abstractions**: still unpriced; needs a plan first, ideally after (1).
4. If none of these justifies its cost against the remaining window, stop the autonomous run.

Not recommended: more feedback rounds, a 600-lineage margin run, a PA-only replication, or a
transfer test of partial fits before a fresh bank is frozen with the method.
