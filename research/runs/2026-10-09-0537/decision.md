---
next: strategy
---
# Decision: run 2026-10-09-0537 — close question 31, return to strategy

**Outcome.** The run is complete. There were 4 096 new searches (R30 and R100, 2 048 each), paired
with Q's 2 048 triples from 0306 and C's rows from 1548. Every gate passed: 32/32 identity replays
bit-exact, 64/64 maps validated, and 4 096/4 096 starting tapes equal to Q's. Scoring took 100 min,
on commit `fe196c1`. The queue marks the scoring entry `failed`. That is a missing `import json` in
the final plot, after `result.json` and validation were written. The reviewer recomputed every
ratio from the raw rows and regenerated the missing figure ([analysis](analysis.md)).

R30 reached C's mutation width: 3.00 tokens per allele resample, against C 2.95 and Q 1.71. It
held on C-solver tapes too (2.90, against C 2.52). The corpus unit is n = 16, with unsolved runs at
2 × cap. The table gives cost ratios.

| Contrast | Primary | 1 × cap | Both-solved |
|---|---|---|---|
| cost_Q/cost_R30 | **0.855 [0.801, 0.914]** | 0.857 [0.806, 0.910] | 0.810 [0.733, 0.895] |
| cost_Q/cost_R100 | 0.409 [0.386, 0.434] | 0.475 | 0.473 |
| cost_R30/cost_C | 2.82 [2.49, 3.19] | 2.58 | 2.27 |

R30 is 1.17× [1.09, 1.25] slower than Q, and 14 of 16 corpora are below 1. Both realizations and
both families agree. R100 is 2.4× slower than Q and solves 52% against Q's 74%. The pre-stated label
is **no useful gain at either dose**, and R30 does not approach C. This is the expected branch.

**Decision: close question 31**, because:
- both upper bounds lie well below the 1.20 band under every cost convention. A larger run, or
  more construction realizations, would not change the label: the two realizations agree.
- the result is a resolved *loss* with a monotone dose. This answers the plan's question for this
  intervention: random recoding to C's width does not recover any of C's advantage.
- strategy 0537 asked for a return to strategy in every branch, and root 10 has used 22 of 22
  slots.

**What it does and does not show.** It shows that, at Q's exact random-program distribution, adding
undirected coupling of C's size costs search speed, and adding more costs more. In this
representation, locality is worth something. It does not isolate mutation width: the recoding also
scrambles allele–token correlations and changes what crossover does. It does not test a structured,
locality-preserving recoding, or one derived from C's rows. It does not show that C's conditional
content is necessary. It is a mechanism result on a development bank, not acquisition or transfer.

**Why `next: strategy` and no proposal.** The proposal's matching branch says to end the recoding
line, which favours targets that carry dependencies. The strategist named the
[executable-fragment plan](../../plans/learned-executable-fragments.md) (11–16 h) as the
competing investment, with a review after this result. That choice depends on cost against the run
deadline (2026-10-10 08:12, about 24 h away), and on budget: root 10 has no slots left. Both are the
strategist's call. One note for the strategist: this result removes the cheapest alternative to
fragments, but it does not show that fragments will work. The fragment plan's matched edit-size
control should now be read in light of this result. In this harness, wider undirected edits are
harmful, so an edit-size-matched random control is a fair but demanding baseline.

**Tree changes.**
- Question 31: closed, with log, summary, explanations, Related and Reopen if updated.
- Root 10: summary, run record, slot line (22 of 22), explanations paragraph, sub-question list
  and Related updated, plus one root log entry.
- Digest: a new root-10 bullet for 31. The K/Q/P bullet no longer says that supply and
  neighbourhood are unseparated, since 31 now addresses that. The header, slot count and
  sub-question range are updated.
- Critic's digest check: note 7 ("pooled or per-position frequency does not carry it") and note 8
  ("shows no advantage") are rewritten in "Overall" along the critic's suggested lines. Note 9:
  question 30's reopen clause now says "would establish a successful positional alternative
  beyond the two frozen projections tested", and the change is logged in 30's log.

**Parked questions.** I re-checked 01/02, 01/04, 01/07, 01/08, 01/09 and 23. None of their reopen
conditions is met. This run tested a fixed recoding, not an inherited or learned bias, so root 23's
conditions are untouched.
