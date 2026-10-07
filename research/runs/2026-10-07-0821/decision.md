---
next: strategy
---
# Decision — 2026-10-07-0821

**Park [18](../../questions/10-compositional-map-transfer/18-compact-context-learning/question.md)
(1 of 2 slots used) and return root 10 to the strategist. No proposal is written.**

## Result

Outcome row 3, matched cleanly ([analysis](analysis.md)). Data complete: 16/16 pairs, 174 964
searches, hashes pinned, no holdout touched, 2.64 h of a 3.8 h deadline.

- C/T 0.955× [0.833, 1.095]: the upper bound is below the pre-registered 1.15×, so a gain above
  about 1.10× is excluded for this procedure and budget.
- T/S 1.03× [0.90, 1.16] and C/S 0.98× [0.90, 1.07]: neither arm resolved learning, and in-loop
  slopes are flat in both.
- Stage A: single context steps have repeatable effects (σ²_T 0.047 [0.027, 0.065]). The best
  quarter of mutants beats the average mutant on new seeds, but it only reaches parent level
  (−0.017 [−0.085, +0.041] log2).

## Why park, not close or continue

- **Not close.** Row 3 was pre-registered as uninformative about context. The token arm, which
  serves as the positive control, did not learn, so the C/T null cannot tell ineffective context
  (A false) from a loop that does not climb (new explanation E in 18). Closing would read an
  unresolved result as absence.
- **Not continue with a proposal now.** The only informative next run would first have to show
  that token continuation from these saved maps learns (T/S resolved > 1), then run C in that
  loop. That needs a different loop, not more pairs, and the pre-registered row 3 action is
  "park; strategy". The analysis argues that more generations at 24 searches per child would
  drift rather than climb. My own check partly disagrees. T/S's upper bound allows about
  5.4 × 10⁻⁵ log2 per search, and 0811's token continuation achieved about 4.0 × 10⁻⁵ (other bank
  and start), so depth is not excluded either. Both routes cost about 5–6 h of queue. That
  would spend root 10's last slot on fixing the learning loop, which is a program-level choice
  between this, a transfer-free close of root 10, or another direction.
- **Parked questions re-checked.** None of root 01's parked questions (02, 04, 07, 08, 09) has
  its reopen condition met by this run. The run concerns decoder context on root 10's bank.

## For the strategist

Root 10 has 1 slot left. The deadline is 22:25, about 10.5 h from 11:40, and the run's
measured throughput is about 1 200 searches/min. Options, with what each could change:

1. **Make the loop learn first, then test context (one ~5.5–6 h queue, gated in code).** Stage 1
   is a token-only pilot from a few saved maps, either 3× longer (about 12 000 searches per arm)
   or with about 4× more searches per child at the same budget. If T/S resolves above 1, stage 2
   runs C at the same loop. Size the main stage with pair sd 0.38 log2: 16 pairs give a
   half-width of about 0.20 log2. If the pilot shows no learning, the result bounds what this
   learner can do from token-tuned starts, which is also worth knowing. The timing is tight
   against the deadline.
2. **Learn from G4 instead of saved maps.** In 1723, token learning from G4 climbed about 2.2×,
   so the positive control works there. C versus T from G4 would test explanation D. The cost is
   start-to-start spread (sd 0.19–0.31), which leaves about 8 pairs in 4 h and an expected
   unresolved result. Not recommended.
3. **Close root 10 at its current answer.** Learned token maps transfer about 2–3×. There is no
   resolved family advantage on the withheld cells (upper bounds about 1.25× BE and 1.15× PA).
   Three contextual procedures gave no resolved gain beyond token learning, and in the third the
   token arm did not learn either. The gain has two overlapping parts, starting programs and
   ongoing decoder use. Learned context stays untested in a loop that is known to climb.

My recommendation: I lean to option 3. Choose option 1 only if the strategist judges that the
context question is still worth root 10's last slot.
