---
next: strategy
---
# Decision: run 2026-10-09-0306 — close question 30, return to strategy

**Outcome.** Complete pre-registered roster: 4 096 new Q/P searches, quintuple-paired with the
1548 C/T and 0125 K rows, replays bit-exact, no errors, no top-up; scoring took 96 min under the
reviewed admission rule (commit `2bab2c2`). On then-addition row F, corpus unit n = 16, unsolved =
2 × cap ([analysis](analysis.md)):

| Contrast | Primary | 1 × cap | Both-solved |
|---|---|---|---|
| C/Q | **2.41× [2.11, 2.75]** | 2.21× [1.97, 2.48] | 1.95× [1.71, 2.23] |
| C/P | **5.47× [4.79, 6.25]** | 4.26× [3.80, 4.78] | 3.30× [2.85, 3.81] |
| Q/K | 1.03× [0.93, 1.13] | 1.02× | 1.00× |

All 16 corpora and all 16 cells are above 1.20 for both C/Q and C/P. Solves: C 86.5%, Q 73.9%,
K 72.5%, P 50.5%. The pre-stated rule gives **"this G4-based positional replacement is
insufficient"**, and P is insufficient on the same band: the "both fail" branch.

**Decision: close question 30**, because:
- both lower bounds lie far above the 1.20 band under every censoring treatment, so a larger or
  repeated run would not change the label;
- Q/K 1.03× [0.93, 1.13] shows that the per-position difference between C and K that strategy 0239
  flagged (position-0 TV 0.07–0.21) gives no resolved gain on this bank (a Q gain above about
  1.13× is excluded); another positional control (start-row ablation, position bins) would not
  change the representation decision;
- the plan's routing for this branch is to favour targets that carry dependencies, and to
  reconsider the bounded fragment plan or a specific contextual acquisition mechanism. Neither
  automatically earns a slot.

**What it does and does not show.** It rejects these two frozen, externally fitted projections
under these operators, on a development bank. It does not show that C's learned rows are
necessary: the marginals are matched under the uniform latent prior rather than the populations
selection visits, and C's advantage is confounded with its wider mutation neighbourhood (about 3
tokens changed per allele resample against 1.7 for Q/K and 0.9 for P). Nor is it a learnability
or transfer result.

**Why `next: strategy` and no proposal.** Root 10 has used all 21 slots; strategy 0239 granted
this one slot "through the next strategy review" and required a return after the result. The
candidates now differ in mechanism and price, which is the strategist's call: the
[executable-fragment plan](../../plans/learned-executable-fragments.md) (11–16 h, unmeasured), a
variation-neighbourhood control (e.g. C's rows decoded so that one allele resample changes about
as many tokens as under Q/K, or the reverse), or a specific contextual acquisition mechanism.
For the strategist: the mutation-neighbourhood confound is now the most specific unexplained
part of C − Q. A cheap matched-variation control could tell whether the next learner needs
dependencies or a wider edit neighbourhood. I have not priced it.

**Tree changes.** Question 30 closed (log, summary, explanations with critic note 5's narrower
wording for A, Reopen if, Related). Root 10: summary, run record, explanation-B paragraph,
sub-question list, slot count (21 of 21) and Related updated; one root log entry covering 0239 and
0306. Digest: the root-10 K bullet now covers K, Q and P with scope (supply and variation
neighbourhood not separated; learned positional map untested). The "Overall" line and header are
updated, and sub-questions 11–30 are listed as closed. Critic note 6 required no change.

**Parked questions.** Re-checked 01/02, 01/04, 01/07, 01/08, 01/09 and 23. None of their reopen
conditions is met. Root 23's "a new bank makes a learned frequency bias useful beyond a hand-set
scaffold" is not met: P, a pure positional frequency map, was the slowest arm and was not learned.
