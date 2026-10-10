---
next: strategy
---
# Decision: run 2026-10-10-1717 (41, crossed DG/TS family preference)

**Close [41](../../questions/10-compositional-map-transfer/41-same-alphabet-family-preference/question.md)
and return to strategy.** No proposal written for 2026-10-10-2001.

**What the run settled.** The experiment ran cleanly (commit `b5697a1`, code review pass, all admission
gates passed, 2 304/2 304 searches, 75 min of queue against 220 min of timeouts). On the 8 never-searched
DG cells the DG-built cohort beat the TS-built cohort: cost(T)/cost(D) **2.98× [2.07, 4.33]** at 2 × cap,
**2.40× [1.76, 3.30]** at 1 × cap, 8/8 cells. That direction is a clear, charge-robust own-family preference
for DG acquisition, the first resolved family preference in root 10 (16, 20, 25 were unresolved near 1.0–1.1×).
On the TS cells the direction is unresolved, cost(D)/cost(T) 1.29× [0.94, 1.78]. The pre-set interaction
(1.96× [1.58, 2.44]) cleared its 1.5× margin at 2 × cap only (1.75× [1.45, 2.12] at 1 × cap). Not reciprocal,
no dominant bias; every cohort beat G4 on both rosters by ≥ 2.75×.

**Why close rather than continue.** The question asked whether cheap acquisition learns a useful
own-family preference. It does in the direction that this design could measure. The other direction is
limited by the TS roster's headroom: both cohorts solve 95–97 % of TS searches. More builds on this roster
would buy precision on a compressed contrast; the analysis is right that the runner's 512-build resolution
price is not worth paying. Resolving P_TS needs a harder branch-sum roster or a pre-fixed lower cap. That is
a new design, and I see no decision that currently waits on it. Practically, a DG-built bias already serves TS
cells 6.3× over G4 (a loss of at most about 1.8× against the TS-built one is not excluded), while a TS-built
bias loses about 3× on DG cells. The reopen condition in 41 records both routes back.

**Why `next: strategy`.** Root 10's 33 slots are used. Strategy 1717 asked to exit to strategy after the
crossed result in every case, and it named PSB2 planning as conditional on this outcome. The pre-stated next
actions did not fire: not reciprocal, so no family-specific-acquisition action; and the material DG
interaction rules out the shared-bias action. So the choice of next direction belongs to the strategist.
Candidates I would put in front of it, in my order:

1. **Saved-artifact attribution (cheapest, no acquisition).** Context-only versus context + fragments for
   the 24 D and 24 T builds on the DG roster (and, cheaply, TS). It asks whether P_DG ≈ 3 sits in the
   fragments (the `(a+b)>(c+d)` join), the context table, or both. This is the reopen condition of 40 and
   41. It does not separate content from source difficulty by itself. A third arm could do that: T builds
   given D's fragments, or the reverse. 40 and 41 saved all inputs, so this should be a short queue.
2. **Content versus source difficulty.** The D cohort learned from sparse solvers of hard sources
   (first batch 17 %); the T cohort from abundant solvers of easy ones (63 %). A design matching the
   corpus size between cohorts, e.g. subsampling T's corpus to D's yield, would test whether a poorer
   corpus explains any of it. D won despite the poorer corpus, so I expect content, but this is untested.
3. **Harder branch-sum roster** to resolve the TS direction — only if (1)–(2) or PSB2 planning make the
   reciprocity question decision-relevant.
4. Outside root 10: root 23's changed-rule inheritance and parameterized abstractions, unchanged since
   strategy 1717. No parked question's reopen condition is met by this result. It is an external-fit
   family-preference result, which bears on none of root 01's helper/sampling conditions or root 23's
   selectable-signal condition.

**Critique notes.** 1–6 were implemented in plan.md and the report (code review confirms). Note 7 (digest
check) is fixed: the "Overall" paragraph now scopes the "tenth of full-F acquisition" to the original
output-family sources and states the predicate-addition results separately.

**Tree changes.** 41 closed; root 10 summary, sub-question list and log updated. Digest: new belief bullet for
41, 37 and 38 merged, 40 shortened, condensed text moved to the root 10 log, header and bank list updated.
