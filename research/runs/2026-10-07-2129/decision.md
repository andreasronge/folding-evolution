---
next: proposal
---
# Decision — 2026-10-07-2129

**Continue [22](../../questions/10-compositional-map-transfer/22-feedback-context-increment/question.md)
with the same design in a fresh work window: proposal
[2026-10-07-2156](../2026-10-07-2156/proposal.md).**

What happened: the approved four-arm crossing (T1 and T2 scored on the exact 1924 seeds where C1
and C2 were already scored) was implemented and preflighted (commit `ec742da`, branch
`research/2026-10-07-2129`), then stopped by its own timing gate. No primary search ran; no
interaction was computed; the slot was not used. Row 0, no claim about explanations A–C.

Why this is a calendar failure, not a design failure ([infeasible.md](infeasible.md)):
- Everything the design depends on passed: 128 table hashes, all 16 384 saved C1/C2 row keys,
  seeds and training indices, and 64/64 deterministic C1/C2 replays with every scientific
  field identical.
- T2 is cheap and solvable: 160/160 timing searches solved, 0.665 worker-s per search on BE and
  0.343 on PA (T1 historically 1.042).
- The gate refused only because the plan's work cutoff (22:20:38, five minutes before the
  autonomous deadline) left 26.5 min, against a projected 29.5 min, or 36.9 min with the
  1.25 allowance. That projection used the 160-row block's 4.33 effective workers, which a small
  block with a 17-second tail understates. 1924 reached about 9.7 on full rosters. The
  researcher was right not to change the gate after seeing the measurement.

Why continue rather than park or hand to strategy: the question has not been tested at all.
It is still the comparison strategy 2129 ranked first. Its slot is unused, and root 10 has
1 of 15 slots left. The design, code and inputs are validated. The only missing resource is
wall time: about 210–230 worker-minutes for training plus holdout, so 22–25 min at full-roster
throughput and under 55 min even at the pessimistic preflight rate. Nothing else in the tree is
better prepared. Strategy 2129's "what to stop" list still stands (no C3, no new bank, no
smoothing or active-token work in this allocation).

Wording fixes from the critique's digest check (notes 6–9) are applied to `digest.md`,
root 10's summary, question 21's summary, and question 21's log (as an appended correction).
"C' matches C" now reads "similar means, no equivalence test". The `(S?M:F)+m` cell reads "no
gain resolved, [0.84, 1.13]". The source heading now reads "Collecting under C beats a fresh
G4-collected refit at matched attempts". "Adds more" now reads "adds further search speed; whether
contextual is untested".

Parked questions re-checked (02, 04, 07, 08, 09): a deadline stop gives no new evidence for
any reopen condition. Question 21's reopen condition names a T2 allocation; that allocation is
question 22, so 21 stays closed.

Note for the owner: the autonomous run's deadline (22:25:38) falls before this proposal can run,
so it needs your approval in a later window. The driver also logged a failed push at 21:35
(`research/main research/2026-10-07-1924`); push that by hand.
