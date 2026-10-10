---
next: strategy
---
# Decision — run 2026-10-10-0311 (question 39)

**Close [39](../../questions/10-compositional-map-transfer/39-independent-input-family-bank/question.md);
open [40](../../questions/10-compositional-map-transfer/40-independent-input-protected-transfer/question.md);
return to strategy, with the stage-2 design as the steward's suggestion
([proposal](../2026-10-10-1536/proposal.md); the driver renames it `steward_proposal.md`).**

**Result (probe; observations, not beliefs).** Code review passed; data complete (256 source rows,
192 development rows, no missing or substituted rows; protected cells never searched).
- *Bank:* `x4-double-gate-v1` on alphabet `v2_x4` (D625) has 24 separated cells after the real-token
  screen; frozen 4 source / 4 development / 8 protected split; Python, Rust and the semantic machine agree.
  The bank-obstacle reading (< 12 cells) is far from met.
- *Discovery:* first-batch G4 22/128 (17% [12, 25]); per-build median 2.5/16 is below the pre-stated 4/16,
  so the discovery-obstacle reading applies. Four of eight builds had an empty intermediate library;
  the adaptive batch still solved 81/128 and every build ended with a full library.
- *Development cells* (16 shared seeds per arm): solved G4 7/64, A8 55/64, O 22/64. G4/A8 12.2× [6.7, 20.7]
  (1 × cap 7.3×), A8 cheaper in all four cells including the one whose predicate pairing no source has;
  G4/O 1.8× [1.3, 2.5]; O/A8 6.7× [3.5, 12.5]. 57/64 G4 searches hit the cap, so magnitudes are
  penalty-driven, ordering is not. G4 headroom 10.9% [5.4, 20.9], at the lower edge of the 10–80% band.
- *Spread and price:* between-build SD of A8 log cost 0.79 (factor 2.2). 448 searches took 17 min of queue.
([analysis](analysis.md))

**Why close 39.** It asked whether this bank supports a fair test and at what price. Answered at this
scope: the split is valid and protected; discovery is sparse but the unchanged recipe completes; headroom
exists (narrowly); stage 2 is priced from measured rates. Further stage-1 work would not change the next
choice. The sparse-discovery reading is a property of G4 on `v2_x4`, kept as a reopen condition rather
than fixed by raising attempts (which would change the recipe under test).

**Why stage 2 is the right next experiment.** The pilot signal is large on development cells but rests
on four hash-chosen cells and eight builds; the core question's practical answer (does external
acquisition extend beyond output-addition families?) depends on the protected cells. The suggested
design: 24 fresh builds, 8 protected cells × 48 shared seeds for G4 and A8″, O descriptive; primary
G4/A8″ against a pre-set 1.5× margin; about 2 h of queue timeouts and 4.5–5 h in total. I chose a
margin test rather than the analysis's ±1.25× scenario (53–64 builds) because the decision is "useful
or not", and at pilot variance 24 builds resolve any true effect above about 2.2×.

**Why `next: strategy`.** Root 10 has used 31 of 31 slots, and strategy 0311 allocated only stage 1,
saying stage 2 "needs its own allocation" and to return after this stage. Parked questions re-checked,
none met: root 23 needs a selectable inherited signal (this was external fitting); root 01's parked
children are unchanged; 38's reopen (a decision depending on the PA deficit) is unmet.

**What this does not settle.** Nothing about protected cells, family specificity, context vs fragments
vs supply, or inheritance; O bounds only eight reinterpreted artifacts; alphabet, domain and predicate
placement changed together.

**Tree edits this cycle.**
- 39: log entry, closed, summary/scope/Related/Reopen updated.
- 40: opened (budget 1, awaiting allocation), question and log.
- Root 10: summary sentence (probe, not belief), slot line 31/31, sub-question list, Related, log entries.
- Digest: header, root 10 header (31 of 31), sub-question line, "Not shown" pointer to 40. No belief
  changed: probe results stay out of the digest's beliefs.
- Critique 0311 digest-check note 7: the "S8′ would place the PA deficit" overstatement corrected by an
  appended note in 38's log and root 10's log (decision 0145 left as written, flagged there).
