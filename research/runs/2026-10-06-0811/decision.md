---
next: strategy
---
# Decision: run 2026-10-06-0811 (13, contextual moves vs continued token learning)

**Close 13 (2 of 2 slots used). Keep root 10 open with its last slot (4 of 5 used), and return
to strategy before spending it.** No proposal is written for 2026-10-06-1400.

## Why

- **The outcome rule fired row 4, unresolved, on complete data.** R / M+ (contextual row moves
  allowed vs continued token steps, 12 matched pairs from the six M maps): training 1.00×
  [0.90, 1.11], "no practical gain"; holdouts 1.16× [0.91, 1.48] and 1.06× [0.83, 1.31], both
  spanning 1 and 1.25. Row 3 needed all three bounded, row 2 needed training faster.
- **13's question is answered for the learner that moved.** Selecting on six PA tasks gives a
  decoder that speeds the withheld pair about 2× over G. Re-scored on 200 new seeds per holdout
  the M maps give 2.25× [1.81, 2.81] and 2.06× [1.60, 2.63], which now clear 0132's 1.5× line.
  What is left is A1, the contextual increment. On training it is bounded below 1.11×; on the
  holdouts it is open.
- **Resolving the holdout increment does not fit 13 or a cheap follow-up.** The between-start
  spread is 0.41–0.45 log2, about twice the plan's figure, and it dominates. Bounding a true null
  below 1.25× needs about 7–9 independent starts. Resolving a true 1.16× needs about 20, so a new
  M-map screen first. More seeds or more continuations per start would not help (analysis §2.1).
  13's budget is spent, and the training tie already says a 24× larger parameterization buys
  nothing resolved on the tasks it was trained on.
- **Not parked, because the question as posed is answered.** The unresolved A1 remainder and an
  unregistered off-family hint carry concrete reopen conditions in 13's question.md.
- **Strategy 0811 asked for a return to strategy after this result.** It reserved root 10's last
  slot for one of three uses: replication or resolution if the contextual contrast looked
  promising, a second-family feasibility study, or a mechanism question. That choice belongs to
  the strategist.

## What the strategist should weigh (steward's view)

1. **Recommended: a pre-registered off-family test of the learned maps, with no new learning.**
   The one new lead is unregistered and rests on six maps. Allowing row moves made the "a" maps
   faster than M+ on branch-else (1.33× [1.05, 1.66]) and slower on linear (0.65× [0.44, 0.88],
   6/6). It also doubled PA-training solver supply in 5 of 6 starts, but gave no resolved PA
   search gain. The six "b" continuations, which never saw these cells, are an independent
   replication set. The 12 R_abl maps say whether the shift needs the residuals. Add more seeds
   on the 8 non-PA cells. If 0001's screen has further IF_GT-bearing canonicals that are not
   aliases of the training cells, add them too: that widens the "related shape" set beyond two
   branch-else cells. The pre-stated contrast would be R / M+ on branch shapes against linear.
   This costs no learning: roughly 36 maps × 8+ cells × 100 seeds, about 1–2 h with sampling.
   It either gives the root its first evidence that learned context is tied to the training
   shape, with a cost on unrelated shapes, or closes the root on "every resolved gain is token
   retuning". Limits: linear cells lack IF_GT and sit near the floor under G, and branch-else is
   not an independently trained family. So this would show a shape-tied shift, not family
   specificity.
2. **Alternative: a discriminating outer loop.** Every operator was accepted at the chance rate
   (24–26% vs 25%), so the loop never told row moves from token moves. A loop with fewer
   children and more searches per candidate would show whether R separates from M+ once
   selection actually works. That speaks to the "inadequate optimization" reading of A1. It
   needs a full queue and a measured acceptance rate first.
3. **Second family.** Still the only route to family specificity proper, but it needs a new
   screen after two bank failures. It is a bigger commitment than the root's single slot.

Lower value: re-running R vs M+ with more seeds or continuations from the same six starts. The
spread is between starts.

## Bookkeeping

- Logged in [13](../../questions/10-compositional-map-transfer/13-post-addition-map-learning/log.md)
  (result plus a correction note on the 0132 entry) and in
  [root 10](../../questions/10-compositional-map-transfer/log.md). 13's question.md was rewritten
  (closed; A1/B1/C1/E1/G1 updated; three reopen conditions). Root 10's summary, sub-question
  line and Related links were updated.
- Digest: new section "Contextual moves on top of M"; the decoder-learning section was revised;
  the header, intro and open-questions list were updated.
- Critique digest-check notes 6–11 were fixed in the digest and in 13's and root 10's
  question.md:
  - (6) C-marg is "no resolved improvement", with its intervals.
  - (7) C "drifted modestly, no resolved gain, a gain above 1.09× excluded"; the operator is a
    plausible rather than isolated cause.
  - (8) "still declining at generation 25", now with 0811's measured 1.45× further gain.
  - (9) shrinkage is "about a quarter" (≈ 22% pooled; 14%, 33%).
  - (10) learned directions are named separately (INPUT and DUP in M and T, IF_GT in M, reducers
    with exceptions).
  - (11) the "local optimum" heading is replaced by "found maps 2.2× faster".
  - The log entries were left as written. The correction is appended to the 0811 log entry.
- Parked questions re-checked; none reopens:
  - 09 (a) needs a speed-up with no or negative sampling lift on more than one task. Here R
    raised PA supply without a resolved speed gain (the opposite pattern), and lowered linear
    supply along with linear speed.
  - 08's "decoder-rule version of part 2" is what root 10 already is.
  - The shared-helper questions (02, 04, 07) are untouched by this run.
