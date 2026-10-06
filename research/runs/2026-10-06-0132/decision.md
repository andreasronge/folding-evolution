---
next: strategy
---
# Decision: run 2026-10-06-0132 (13, post-addition decoder learning)

**Continue 13 (open, 1 of 2 slots left) and root 10 (2 of 5 left), but return to strategy
before the next slot.** No proposal is written for 2026-10-06-0811.

## Why

- **The outcome rule sends it there.** Row 1 fired on complete data: the contextual learner C
  showed no practical training gain over frozen G (0.92× [0.78, 1.09] at the 524k cap, 0.94×
  [0.81, 1.09] at 65k). Row 1 says "return to strategy with the measured obstacle", and
  strategy 0132 asked for a review after the first adaptive result, before slots 2–3.
- **The result changes what the root's next slot should be.** The plan expected either
  learning-plus-transfer or a clean null. What came back is a split: the 23-parameter learner M
  (token multipliers on G) improved training 2.2× and transferred 2.0× / 1.7× to the withheld
  pair (lower bounds 1.47 / 1.26, 6/6 trajectories), while the 552-parameter C never moved
  (L1 drift 1.1–1.5 against M's 11–14). So the root has its first held-out gain from a learned
  decoder change, but it is a token-weight change on a hand-supplied context. The question that
  decides A1 (do *learned contextual* preferences add anything?) was not reached. Choosing
  between making C move, checking whether M's gain is generic, and splitting supply from
  mutation is a program-level call with two root slots left.
- **Not park or close.** 13 is not answered: A1 is untested, and the obstacle is a named,
  fixable property of the operator (three cells × e^±0.5 per child against a per-run score sd of
  about 1.6 log2), not of the question. Parking would discard the only split that works.

## What the strategist should weigh (steward's view)

1. **Is M's gain PA-specific or generic? (cheap, decides interpretation).** Score the six frozen
   M maps against G on D1331's other eight retained cells (two branch-else, six linear) from run
   0001, and sample them at 10⁸ (≈ 12 min; dropped this run by the gate). No learning needed;
   under an hour. If M is just as much faster off-family, the learned change (INPUT up, DUP down)
   is a generic fix to G on this alphabet — consistent with root 01's INPUT/GT raise
   ([09](../../questions/01-map-bias/09-generic-bias-speedup/question.md)) — and "transfer" should
   be read that way. Linear cells lack IF_GT, so this is not a token-matched specificity control;
   the branch-else pair is the closer comparison.
2. **A contextual learner that can move (decides A1).** Learn contextual residuals on top of the
   M maps (or jointly with M), with row-level steps; compare against continuing M for the same
   budget. The steward probes already showed single-row N(0, 0.7) perturbations move the score by
   −0.26 to +0.54 (paired SE ≈ 0.17), so row-level steps are measurable where three-cell steps
   were not. About the cost of this run (≈ 6 h).
3. **Recommendation:** one queue with (1) as a fast first stage and (2) as the main stage, using
   13's last slot. (1) is cheap and changes how the only positive result reads; (2) is the
   contrast the root was opened for. Holdout-precision work on M alone (more seeds to settle the
   1.5× line) is lower value: it would sharpen a number whose meaning (1) may change.

## Bookkeeping

- Logged in [13](../../questions/10-compositional-map-transfer/13-post-addition-map-learning/log.md)
  and [root 10](../../questions/10-compositional-map-transfer/log.md); both question.md files
  updated; new digest section "Decoder learning on post-addition".
- Critique digest-check notes 6–9 fixed: the bank failures now carry their design qualifiers
  (digest intro, root 10, open-questions list); 12's question.md scopes the generic-grammar
  entry to frozen G and the domain claim to the three tested domains and cutoffs 0.70–0.85
  (correction appended to 12's log, earlier entry left as written). Note 9 needed no change.
- Parked questions re-checked: none reopens. 09's reopen (b) ("a heritable-bias design needs to
  know whether INPUT/GT supply alone is what evolution uses") is closer — M's learned change
  raises INPUT and IF_GT — but no planned design needs that answer yet; option (1) above would
  be the moment to decide. 08's "decoder-rule version of part 2" is what root 10 already is.
