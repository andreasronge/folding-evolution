---
next: strategy
---
# Decision: run 2026-10-07-1707 (question 20, root 10 slot 13)

**Close 20 as answered; send root 10 to the strategist.** I wrote no proposal for 1924.

**Why close 20.** The pre-stated row-1 rule is met with margin. It replicated over 32
independent corpora, and every validation and feasibility gate passed. C/T is 1.365× [1.288, 1.446]
on the training cells. Both families are resolved separately (BE 1.46×, PA 1.28×). On the
withheld cells C/T is 1.293× [1.213, 1.378]. Matching C's pooled emitted frequencies does not
recover the gain (C/K 1.65×). K is slower than T (0.83×), so I size the contextual increment by
C/T rather than C/K. More corpora or seeds would not change what we conclude. The remaining
unknowns (what structure carries the gain, how it depends on α, whether evolution can reach C)
are different questions.

**Why strategy and not a proposal.** Root 10 has now used 13 of its 13 slots, and only the
strategist can raise a root budget. The deadline is 22:25. It is about 19:35, which leaves
roughly 2 h 50 min for one more cycle.

**What changed in the tree.**
- 20 is closed. Its explanations stand as: A supported at this scope; B rejected for pooled
  frequencies only; C and D not supported.
- In root 10, the summary, the per-explanation status and the sub-question list now cover this
  result. Root 10 stays open with its budget spent.
- The digest has a new section, "Solver-corpus context fit", and updates to the intro, the
  "as of" line and the open-questions list.
- The critic's digest-check notes 6–7 (on 1137's wording) are applied. "C's token part
  fell/learned behind T" becomes "slower in the point estimate, direction unresolved" in the
  digest and in 18 and 19. "0821's selected mutants only reaching parent level" becomes "not
  resolved from their parents (−0.017 [−0.085, +0.041])" in 19.

**Parked questions re-checked.** None has its reopen condition met. 08's condition is "a
decoder-rule version of part 2 gets its own plan and owner go-ahead", and root 10 already is
that version. 02, 04, 07 and 09 depend on the shared-helper or threshold lines, and nothing new
arrived for them.

**Recommendation to the strategist.** The result changes root 10's answer. Useful, transferable
assembly information beyond token frequency exists in this system's own solvers. The
selection-based learners (13, 18, 19) did not reach it, and none of it is family-specific. In
order:

1. **Iterated refit (my pick, if a slot is raised).** Collect solvers under C, refit (C2), and
   score C2 against C on fresh training and withheld seeds. This is the cheapest bridge from
   "external fit" to "the map adapts from its own discoveries": an outer loop with no
   search-cost selection. The existing `solver_corpus_run.py` covers most of the code. The queue
   should be about 80 min, as in this run, with 16 corpora per family. Outcomes: C2/C lower > 1
   means it keeps adapting; upper < 1.10 means one round captures it; otherwise unresolved.
   Before stage 1, a stage 0 must measure collection yield under C, which is expected to be
   higher. It fits before 22:25 only if preparation is quick. Otherwise it is the first item for
   the next run.
2. **Executable-structure fit.** Fit only the active tokens, to see what carries the gain. This
   needs an extractor that has not been reviewed yet, so it is slower to prepare.
3. **Close root 10** at: "token maps transfer 2–3×, no resolved family advantage; a
   solver-fitted previous-token table adds about 1.3× beyond token fitting on withheld cells;
   selection-based context learners did not find such gains". This is a defensible stopping
   point if the strategist prefers to end the run here.

I would not spend more on family specificity on this bank. Only one BE cell exists, and the one
resolved family contrast goes the other way.
