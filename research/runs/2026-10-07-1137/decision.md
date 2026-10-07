---
next: strategy
---
# Decision — 2026-10-07-1137

**Close [19](../../questions/10-compositional-map-transfer/19-selection-calibrated-continuation/question.md)
(1 of 2 slots used), close [18](../../questions/10-compositional-map-transfer/18-compact-context-learning/question.md)
at its tested scope, and return root 10 to the strategist with one slot left. No proposal is
written.**

## Result

Outcome row 6, matched cleanly and confirmed by the runner and the reviewer's independent
recomputation ([analysis](analysis.md)). Data complete: 32/32 trajectories, 335 700 searches,
4.63 h of a 5.75 h timeout. 0821's 4 000 fresh S rows reproduced bit-identically. No holdout
touched.

- **Token control works.** T/S 1.143× [1.089, 1.200] on 0821's fresh seeds (16/16 starts) and
  1.122× [1.031, 1.222] on new seeds. The in-loop parent score fell in 14/16 trajectories.
- **Context adds no resolved increment in that loop.** C/T 0.967× [0.871, 1.073]. The
  pre-registered bound (< 1.15×) is met, and a mean gain above about 1.07× is excluded. Gains
  below that, and losses up to 13%, are not.
- C's token part fell behind T's: C0/T 0.932× [0.860, 1.010], unresolved and not pre-stated.
  C spent half its proposals on context steps.

## Why close, not continue

- **19 is answered.** It asked whether a more reliable score makes continuation from these maps
  learn and then whether context adds. Both parts have pre-registered answers. The run does not
  say *why* this loop climbed and 0821's did not, because evidence per candidate, depth and
  total effort all changed together. Isolating that would not change any decision on root 10.
- **18's reopen condition was met, and its test has now run with a working control.** Row 6 was
  pre-registered as "close 18 for this representation and loop". Two parts of 18 stay untested,
  and the new question text records them: context learned jointly from G4 (explanation D), and
  context that does not take steps away from token learning (which bears on explanation C).
  Each needs a new design. Neither is a precision rerun of this one.
- **Why no proposal for slot 13.** The strategist reserved slot 13 for settling C/T after a
  working token control, or for testing transfer if context helped. C/T is settled at this
  scope and context did not help, so the slot has no assigned use left. The candidates are:
  1. **C added after or on top of a full token budget.** For example, continue each T96 map
     with context-only steps versus more token steps. This needs two new arms of 9 600 searches
     per start, about 4.2 h of learning plus fresh scoring at 16 starts. With 8 starts it would
     fit, but the C/T half-width would be about 0.24 log2 (0.15 here at 16), and an unresolved result is likely.
     Token learning had also not flattened (T/T_mid 1.058× [0.990, 1.130]), so "after token
     convergence" is not yet true.
  2. **Joint context and token learning from G4 (D).** Needs fresh full trajectories (about 10–14
     min each at 1723's rates, 32 for 16 pairs). That does not fit with replication.
  3. **Close root 10** at its current answer.

  About 5.2 h remain before the 22:25 deadline, and a cycle needs about 1.5 h of agent work. So
  any queue must be under about 3.5 h, which is too short for either design at a size that could
  change a belief. This is a choice between the last slot, closing root 10, and other roots, so
  it is the strategist's call.

## Parked questions re-checked

18's reopen condition (a loop where token continuation learns, plus a C arm at that loop) is met
and acted on above. None of root 01's parked questions (02, 04, 07, 08, 09) has its condition met.
This run concerns decoder context on root 10's bank only.

## Digest check (critique notes 6–9)

These are fixed in digest.md, in 18's question.md and in the root summary:
- "parent level" is now "difference from the parent unresolved (−0.017 [−0.085, +0.041])".
- "no net movement" is now "no resolved net movement".
- "same rate" is now "observed survival proportions 0.22–0.27".
- "unrelated" is now "small absolute cosine alignment (≤ 0.105)".

The 0821 log entries are append-only. They keep the old wording, and a correction entry has been
appended to 18's log.

## For the strategist

My recommendation is option 3, closing root 10. The answer stands:
- Learned token maps transfer about 2–3× to withheld cells.
- There is no resolved family advantage (upper bounds about 1.25× BE, 1.15× PA).
- The gain comes from overlapping start and ongoing-use parts.
- Four contextual procedures (0132, 0811, 0821, 1137) gave no resolved gain beyond token
  learning. The last of them excludes more than about 1.07× in a loop with a confirmed token
  control.

Learned context is still untested in two forms: jointly from G4, and without displacing token
steps. Either is a fresh multi-cycle question, not a last-slot experiment. If the strategist
wants one more root-10 experiment anyway, option 1 at 8 starts is the only design that fits
tonight, and it would most likely end unresolved.
