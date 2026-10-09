---
next: strategy
---
# Decision: run 2026-10-09-1606 — close question 34, return to strategy

**Result.** R is W's C-chain block operator without the boundary repair. It uses the same blocks
and draws, but the boundary allele is refreshed neutrally within the token it now decodes to, so
the decoded suffix may ripple. R was scored on then-addition-v1, 16 corpora × 16 cells × 16 seeds
(commit `af8a7e5`), and paired with 1036's W and C rows. All 15 360 historical rows were
re-matched and 32 were replayed bit-exactly, so the main paired path ran. The 10 000-edit audit
passed. Scoring took 47 min.
- **W/R 0.954× [0.903, 1.007]** (> 1 would favour the repair), 5/16 corpora above 1. Upper bounds
  are 1.008 (1 × cap), 1.031 (both-solved), 1.061 (BE) and 1.016 (PA). On the holdouts
  (descriptive) it is 0.963 [0.850, 1.092].
- **R/C 1.286× [1.208, 1.370]**, 16/16 corpora. W/C in the same pairs is 1.227×.
- Solves: R 3 685, W 3 643 and C 3 566 of 4 096. Most of the W/R gap is censoring.
- Ripple: 64% of R's edits change the suffix, by about 3 tokens when they do. That is 4.7
  changed tokens per edit, against W's 2.9.

Pre-registered rule 3 fired (`not_needed_at_this_resolution`). Rule 1 ("ripple helps") missed by
0.7% on the upper bound. My guess was W/R 1.03–1.10, which was on the wrong side of 1. R/C > 1
was as I expected. ([analysis](analysis.md))

**Decision: close 34 and return to strategy (`next: strategy`); no proposal written.** Because:
1. **The question is answered at its scope.** The repair adds no gain above 0.7% here. The
   worthwhile 1.10× is excluded under every sensitivity and in both families. A later
   acquisition baseline can use either boundary policy at this resolution. More seeds would only
   sharpen the "ripple helps" direction, which decides nothing now.
2. **The pre-set routing says so.** Strategy 1606 and the proposal route every outcome back to
   strategy, and no second experiment is funded.
3. **No slots are left.** Root 10 has used 26 of 26, every other root is exhausted, and 34 has
   used 1 of 1.

The limits stay attached:
- **Not equality.** W can be at most 0.7% better than R and up to about 10% worse.
- **Not that ripple helps.** That is a direction only: the both-solved estimate is 0.984, and the
  gap is 42 extra R solves.
- **Not that chain proposals are W's sole cause.** W's length law came from F, and token supply
  is untested.
- **Narrow scope.** One externally fitted previous-token decoder, with ripple of about 3 tokens.
  Ordinary mutation and crossover are unchanged, so this is not a general GE locality result.
  Development bank; nothing acquired.

**Tree changes.**
- [34](../../questions/10-compositional-map-transfer/34-chain-block-suffix-preservation/question.md)
  is closed, with its summary, log, Related links and a reopen condition (a long-ripple decoder,
  or a decision that needs W against R finer than about 5%).
- Root 10: summary sentence, budget line (26 of 26), the "where they stand" paragraph,
  sub-question entry, Related and log are updated.
- Digest: question 32's "C's point mutation re-decodes the whole suffix" was corrected and a new
  bullet added for 34. Overall gained a clause, and the header and root heading were updated.
  The digest is now 2 997 words.

**Digest check (critique 1606, notes 6–7).** Both are fixed in
[33](../../questions/10-compositional-map-transfer/33-pre-solve-fragment-source/question.md).
- **Family scope.** The 1.10 bound holds pooled, under the cap and both-solved sensitivities, and
  in BE. PA stays unresolved at 1.10 (upper bound 1.122).
- **E/C.** "E/C equals W/C, the block operator's gain" now reads as similarity of point
  estimates. No E/W gain was resolved, and W_E/W leaves a length-law effect open.
- Corrections are appended to 33's log and root 10's log; the earlier entries are left intact.
  The digest's own 33 bullet was already correct.

**Parked questions.** No reopen condition is met.
- Root 23 needs a changed inheritance rule with a measured selectable signal; this run changed
  only an operator.
- Root 01's 02/04/07/08/09 are untouched.
- 33 needs a source with `gt` joins or a join knock-in/knock-out, and neither was run.

**For the strategist to weigh.** This is a ranking, not priced designs. 13 of 40 experiments are
used. The deadline is 2026-10-10 08:12, about 14.5 h away.
1. **The operator side of root 10 is now largely explained.**
   - W beats C through coordinated chain proposals: marginal blocks of similar width did not help
     (B/C 0.98×, 32), and containment is not needed (34).
   - F adds about 1.2× more through solver content.
   - What remains open is acquisition: no evolutionary or cheap route has reached C or F.
2. **The `gt`-join knock-out of F** (about 5 h, deferred in strategy 1606) is still the
   nearest mechanism test. It is only worth running if a concrete cheap source would be chosen
   by its answer.
3. **Ending the run here is reasonable.** The remaining open item is acquisition, and no priced
   acquisition design yet has a measured signal to justify it. Root 23's reopen condition is
   unmet.
