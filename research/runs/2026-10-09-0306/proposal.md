---
node: questions/10-compositional-map-transfer/30-position-matched-replacement
title: Position-matched replacements Q and P for C, re-run with a 3 h 15 min scoring timeout
bank: then-addition-v1
---
**Question and mechanism.** Unchanged from [proposal 0239](../2026-10-09-0239/proposal.md) (critic
notes in [critique 0239](../2026-10-09-0239/critique.md), plan in [plan 0239](../2026-10-09-0239/plan.md)).
On then-addition, frozen context tables C beat K (G4 reweighted to C's *pooled* frequencies) 2.48×
[2.17, 2.83] ([0125](../2026-10-09-0125/analysis.md)). Do C's *per-position* frequencies close that gap?
- **Q** (primary): G4's rows × per-position multipliers, matched to C's emitted marginal at all 32
  positions; keeps G4's previous-token dependence; C's start row at position 0.
- **P** (interpretation): independent draws from C's positional marginals.

**What changed.** Only the scoring timeout: **11 700 s instead of 10 800 s**. Run 0239 built Q and P
and passed every gate, then stopped at its runtime admission gate, 69.7 s short
([infeasible 0239](../2026-10-09-0239/infeasible.md)). Measured: worst token error Q 3.8e-5,
P 2.7e-5; worst positional TV ≤ 1.61e-4; Q start rows = C's; lookups match a scalar reference;
32/32 C/T and 16/16 K replays bit-exact.

**Closest known technique.** Position-specific EDA program models, adapted by external fitting:
P resembles PBIL ([Baluja 1994](https://www.ri.cmu.edu/pub_files/pub1/baluja_shumeet_1994_2/baluja_shumeet_1994_2.pdf))
and PIPE ([Salustowicz & Schmidhuber 1997](https://pubmed.ncbi.nlm.nih.gov/10021756/)); C is a
position-free bigram like N-gram GP ([Poli & McPhee 2008](https://repository.essex.ac.uk/9722/)). A
**mechanism test**: order-versus-position controls for maps used inside evolutionary search.

**Arms, unit, seeds.** As 0239: 16 pinned 1246 C tables (8 BE, 8 PA) → Q and P; 1548 row F's 16
then-addition cells, the same 8 paired seed/case draws per corpus and cell: 4 096 new searches. Reuse
1548 C/T/G4 and 0125 K rows. Population 256, cap 524 288, D1331 exact check, operators unchanged.
Unit: corpus, n = 16. The 32 preparation timing searches are not part of the roster or analysis.

**Implementation.** Reuse commit `37c78c1` on branch `research/2026-10-09-0239` (not yet on
`research/main`; bring it in). Change only the admission constant and default deadline in
`position_matched_run.py` (10 800 → 11 700; 10 680 → 11 580) and the queue timeout. Keep the
admission formula (1.15 × max of average, batch and all-capped projections + fitting + 120 s
reporting), all tolerances, fits, hashes and tests. The queue's preparation entry reruns all gates
and re-prices; it admits only if the price fits 11 700 s. The code has not had a code review yet; it
needs one.

**Feasibility.** Measured in 0239 (10 workers): preparation 197 s; Q 13.9 and P 17.3 worker-s/search;
4 096-search projections 107 min (average cost), 128 min (finite batch), 155 min (all capped + tail);
conservative price 181.2 min, leaving 13.8 min under 195 min.

**Full cost.** Queue timeouts 0.5 h + 3.25 h = **3 h 45 min** (strategy ceiling 4 h); expected queue
about 2–2.2 h. Agents: about 1 h integration and review, 1.5 h analysis and decision. Total about
**4.5–6 h**, within strategy 0239's 5–7 h for this slot (root 10: 20 of 21 used; question 30: 0 of 1).

**Why not return to strategy first.** Strategy 0239 asked for a return on a cost obstruction. This
one changes none of the quantities it priced (slot, 4 h ceiling, 5–7 h, window ending
2026-10-10T08:12 with about 29 h left). If the critic judges the 107–128 min runtime or the
preparation hints change the value, send this to the strategist instead.

**Primary comparison and decision rule.** Unchanged. C/Q = exp(mean over corpora of the mean over
16 cells × 8 seeds of log cost_Q − log cost_C); unsolved = 2 × cap; 95% t interval, 15 df.
- Lower bound ≥ 1.20 → **this G4-based positional replacement is insufficient**.
- Upper bound ≤ 1.20 → sufficient within 20%.
- Otherwise unresolved; report the interval and the price of resolving it.

Always read C/P against the same bands. Q fails and P succeeds → independent positional supply stays
viable. Q succeeds and P fails → supplied grammar is useful. Both fail → these two frozen replacements
failed under these operators, which favours dependency-carrying targets without ruling out every
positional learner. Neither success shows learnability. A C advantage cannot separate solver supply
from the changed variation neighbourhood (one allele resample changes about 2.9 tokens under C, 1.7
under Q, 0.9 under P). Reported without a rule: Q/K, Q/P, log(C/Q)/log(C/K) as arithmetic, 1 × cap and
both-solved sensitivities, solves, per-cell and BE/PA, tokens changed per mutation and crossover. No
top-up.

**Expectations.** C/Q 1.7–2.4× and P slower than Q. The preparation solve counts make "both
insufficient" the likeliest outcome. It would surprise me if C/Q's upper bound fell to ≤ 1.20, or if
P matched or beat Q.

**Scope.** Development bank (mechanism, not transfer); external projections, not acquisition;
uniform-prior marginals.

**Next action.** Researcher: bring in `37c78c1`, apply the timeout change, rerun tests and
preparation, write queue.yaml. After analysis, return with `next: strategy`.
