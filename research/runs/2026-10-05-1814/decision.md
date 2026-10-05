---
next: strategy
decision: park
node: questions/01-map-bias/09-generic-bias-speedup
also_parked: questions/01-map-bias/08-evolve-bias
---
# Decision — 2026-10-05-1814

**Park 09, park 08 with it, and hand the program to the strategist. No proposal.**

The run is complete and clean: 2,000 runs, 60 min wall of a 3 h timeout, one look at n = 250
as frozen, all 1,953 solvers re-verified exact, all 10 contrasts reproduced by the reviewer.

| Ratio of median evaluations (99.5% CI) | sum>2 | max>2 |
|---|---|---|
| U ÷ X (replication) | 2.73 (2.12–3.48) | 2.02 (1.45–2.46) |
| IG ÷ X | 1.29 (0.92–1.63) | 0.90 (0.71–1.08) |
| R ÷ X | 1.69 (1.39–2.20) | 2.16 (1.57–2.78) |
| U ÷ IG / U ÷ R | 2.11 / 1.61 | 2.24 / 0.93 |
| Labels | IG unresolved, R unresolved | IG carries, R falls short |

**Why park 09.** The frozen rule closes 09 only if the same arm carries in both tasks. The
carrying set is {IG} on max>2 and empty on sum>2, which is "task disagreement → park". The
plan also forbids a follow-up run to firm up the sum>2 reading, and 09's stop rule was one
experiment. I do not see an argument that beats that rule: sum>2's two near misses (IG's upper
bound 1.63 against 1.5; R's lower bound 1.39 against 1.5) would need about 2.5× the pairs
(≥ 650) to resolve if the point estimates held, and either answer would still be about which
*intervention* suffices, not why.

**Why park 08.** 1814's proposal fixed that 08 follows 09. 08's open part, family specificity
(1.66× / 1.80× against a 2× bar), can at best show "real but small". Its answered part stands.

**What changed in what we believe.** The 1705 speed-up is real. The premise "no sampling lift"
was a cancellation: INPUT/GT alone raises exact solvers 3–4×, the rest of the vector cuts them
3–4×. On max>2 the carrying part is therefore a supply-raising change, which softens the
"supply does not predict speed" story. A speed-up *against* supply survives in one cell only
(R on sum>2: 1.61× faster with 0.23× the solvers). There R and X meet about 10× more
training-perfect inexact programs, which fits the max>2 stepping-stone idea (G3). Nothing here
tests that.

**Why strategy, not a proposal.** No open sub-question is left under root 01. Its last
experiment should go where the strategist points, not to a rescue of 09. If the strategist
wants to stay on this thread, I rank the options as:
1. A direct test of G3 on sum>2 (for example R with REDUCE_MAX reset to 1/22, or training
   sets on which max>2 is not training-perfect). This is the one effect left that supply
   does not explain. It is one task only, so a "yes" would be narrow.
2. Close part 2 at its bounded answer and move the program elsewhere, e.g. heritable bias,
   which now has a concrete hint: carry INPUT/GT mass, not the whole fitted shape.
3. Resolve sum>2 IG vs X at ≥ 650 pairs. Not recommended: it only tightens a label.

**Parked questions re-checked.** None reopens.
[02](../../questions/01-map-bias/02-fixed-target-sampling/question.md) still needs an owner
request. [07](../../questions/01-map-bias/07-shared-arrival/question.md) has no testable
B-helper copy or replay, and [04](../../questions/01-map-bias/04-random-start-discovery/question.md)
depends on 07. 09's and 08's own reopen conditions are not met by this run.

**Tree changes.** 09: log entry; status parked; summary, explanation states, stop rule and
three reopen conditions rewritten. 08: log entry; status parked; summary, C's state, stop
rule, reopen condition and Related updated. Root 01: summary and log (runs 1558/1705/1814
and this decision). Digest: header, intro, a new bullet on the component result, and the
open-question entries for 08 and 09.
