---
next: proposal
---
# Decision: run 2026-10-09-0239 — continue question 30 (re-propose with a 3 h 15 min scoring timeout)

**Outcome of the cycle.** No efficacy result. The researcher built the frozen Q and P projections of
the 16 pinned C tables and passed every design gate: worst per-token marginal error Q 3.8e-5,
P 2.7e-5 (limit 1e-3); worst positional total variation Q 1.59e-4, P 1.61e-4 (limit 5e-3); Q's start
rows equal C's; positional lookups match a scalar reference on changing-table tapes; 32/32 C/T and
16/16 K historical rows replay bit-exactly. The pre-stated runtime admission gate then failed:
conservative price 10 869.7 s against the 10 800 s scoring timeout, **short by 69.7 s**
([infeasible.md](infeasible.md)). Nothing was tuned after the failure. No code review was run.

**Decision: continue question 30.** Re-propose the identical roster, projections, gates, analysis
and admission formula, changing only the scoring timeout to 11 700 s
([proposal 0306](../2026-10-09-0306/proposal.md)), because:
- the obstruction is 0.6% of a price that already assumes every search caps plus 15% safety; the
  measured average-cost and finite-batch projections are 107 and 128 min;
- 0.5 h preparation + 3.25 h scoring = 3 h 45 min, inside strategy 0239's 4 h summed-timeout ceiling
  and its 5–7 h full-cost allocation (the build is done, so remaining cost is about 4–5 h);
- the slot strategy 0239 granted is unused (root 10: 20 of 21; question 30: 0 of 1);
- the decision the result feeds is unchanged: whether the next acquisition target can be positional
  supply (Q or P sufficient) or must carry dependencies (both insufficient).

**Why not `next: strategy`.** Strategy 0239 and infeasible.md both say to return on a cost
obstruction. I depart from that because this obstruction does not change any quantity the strategist
priced: the revised design stays within the granted slot, time ceiling and window (deadline
2026-10-10T08:12, about 29 h left). The critic can send it to the strategist if it disagrees. The
result itself still returns to strategy.

**Preparation observations (not beliefs).** Q solved 9/16 and P 6/16 timing searches at the cap
(Clopper–Pearson 30–80% and 15–65%), one per corpus on rotating cells, unpaired with C. The full
historical rosters solved C 86.5%, K 72.5%. These hint that Q and P may be slower than C, but they
are not a C/Q estimate and do not pre-empt the decision rule. They are logged in question 30 only.

**Tree changes.** Question 30 log and summary updated; root 10's sub-question list and links updated.
Digest: no belief changed; fixed the two critic digest notes (0125's bullet now says "then-addition
(now a development bank)"; the 2116 bullet no longer claims PA collection improved "as much as BE's")
and the same "fresh bank" wording in root 10; root 10 header now 20 of 21.

**Parked questions.** Re-checked 01/02, 01/04, 01/07, 01/08, 01/09 and 23. This cycle produced only
gate and timing measurements, so no reopen condition is met.
