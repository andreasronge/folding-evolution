# Decision: park 07, park 04, open 08 (README part 2)

**Park [07-shared-arrival](../../questions/01-map-bias/07-shared-arrival/question.md).**
The run was clean (exit 0, 50/50 census populations, 100/100 insertion pairs, guards held, the
reviewer's counts agree across files). It lands in the plan's "both may limit, bounds broad"
cell, which the plan counts as unresolved, not as a closed mechanism:
- E ≈ 2 shared arrivals per run (envelope 0.34–9.2): above the arrival-limited bar (≲ 1),
  far below the fixation-limited bar (≳ 10).
- p = 0/100 (≤ 3.6%): rules out p ≥ 10% but does not reach the 1% the proposal wanted. A
  neutral single copy would establish about 0.25% of the time, so 100 trials cannot tell
  "neutral" from "disadvantaged" either.
- ~32 arrivals × ≤ 3.6% ≤ ~1.2 expected replacements vs 1 observed: consistent, explains nothing.

So closing with "arrival-limited" or "fixation-limited" would overstate it. The stop rule
written when 07 opened says the shared-helper line ends after this experiment whatever it
shows, so the choice is park, not continue.

**What the run did settle, and why it is still worth recording.**
- "Shared helpers are rare because they never arrive" is wrong as stated. Exact shared
  children arrive about twice per run in established partly populations, and controls show
  them appearing and vanishing in situ.
- The arrivals are the wrong kind. 56 of 56 were A-only or other, 0 B-helper (≤ 1.2e-7 per
  child), and both shared-ending runs are B-helper. This gives a sharper hypothesis (07's new
  explanation D): A-only copies arrive and drift out; B-helper almost never arrives and wins
  when it does. It is the best reason to reopen 07, and it is written into the reopen
  condition: a B-helper single-copy test with ≥ 300 insertions, or in-situ replay.

**Why not spend 07's last experiment on B-helper insertions now.** It would test the most
interesting hypothesis left in the line. But:
- no natural B-helper child exists to insert (none in 30M draws), so it would be a transfer
  test of copies taken from seed 7 / seed 18, which the approval said to skip when natural copies are missing;
- resolving p near 1% needs ~300 insertions, and separating neutral from disadvantaged needs
  thousands;
- the owner and the critic both kept the stop rule.

The root's untested half is a better use of the remaining root budget (4 left).

**Park [04-random-start-discovery](../../questions/01-map-bias/04-random-start-discovery/question.md).**
It is part of the same line, and its two leftovers (duplication-only companion, 0.3 vs 0.7
parity) change no decision now. Reopen condition written.

**Open [08-evolve-bias](../../questions/01-map-bias/08-evolve-bias/question.md)** (budget 3)
for the README's part 2. This is the "new question" outcome for the root. Its first experiment
is the next proposal.

**Parked questions re-checked.**
- 02: its condition is "the shared-helper line stalls *and* the owner wants fixed-target map
  bias settled". The first half is now met (the line has stopped), but no owner wish for the
  second half is recorded, so 02 stays parked. The brief offers it as the alternative to 08.
- 06: its reopen condition (late reversals after ≥ 95% shared replicate) got no new evidence.
- 03 and 05: stay closed.

**Uncertainty carried forward.**
- Every per-run figure extrapolates from generation-3000 final populations; the mid-phase
  check verified 2 of 5 replays with too few draws to compare rates.
- Seed 7's partly phase (the one replacement) was not sampled. Seed 23 has no known duration
  and could only raise E.
- The suggestion that shared copies are less heritable than the resident form (6 vs ~16 of
  100 lineages left at generation 10) rests on the analyst's branching model. Suggestive only.
- One task, one cell (L 64, self-mate, 0.3), 86 of 100 trials from five populations.
