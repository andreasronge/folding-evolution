---
next: strategy
---
# Decision — 2026-10-11-1315 rectified-sum probe of the frozen R-all recipe

**Park [54](../../questions/10-compositional-map-transfer/54-rectified-sum-acquisition/question.md); no proposal;
return to strategy.** Root 10 is at 45/45, and strategy 1315 asked for a program review after this probe,
whatever it found.

**What the probe showed (observations; six development cells, protected roster never searched; commit `4a60cc7`).**
- Sources `pos/neg(a,b)+Xc` are easy: 384/384 solved, ~166 k evaluations per build. But they are mostly solved
  through the three-input sum (`a+b+c` in 326/384 solvers, IF_GT root 335/384). Only 34/384 solvers contain their
  own helper (8.9%), 9/384 at an emittable size. No helper both recurred in ≥ 2 cells and fit 3–9 nodes (0/96
  helper × build pairs).
- So the frozen R-all recipe pooled no rectifier: needed-helper coverage **0/48**. It cost **1.03× [0.96, 1.10]** of
  R-tree (capped arithmetic means, whole-build bootstrap); transported order libraries 1.04× [1.00, 1.08].
- Supplied helpers help but sit below the pre-set investment bar: R-rect solved 73/96 against R-tree's 20/96, at
  **0.57× [0.50, 0.64]** (bar: ≥ 90% solved and ≤ 0.5).
- All three advisory conditions failed. The labels are *low observed acquisition under this source effort*,
  *supplied prior below the investment threshold*, and no saving. Every proposal expectation held, and stage 0 was
  reproduced on-harness.

**Why park, not close or continue.** The question asked whether the unchanged recipe acquires useful bias here.
Under this source design it did not, and the loss sits at the source: evolution rarely builds the helper when a
helper-free route exists. Neither more seeds nor protected scoring could change that, and a decision-sized
confirmation needs all three conditions. The question is not closed because this is one probe on development cells
under one source design. It does not show that rectifiers cannot be acquired, and it gives no portability verdict on
R-all. A forcing source design (no three-input-sum route) or a different acquisition method could change the answer.
Both would be new designs, and strategy 1315 ruled out silently enlarging this candidate. The reopen condition in
54 is written that way.

**Why no proposal.** Every open line in root 10 now needs a strategy decision, not a steward pick:
- Root 10 has no budget.
- The strategy's stated next candidates for root 10 change the design: protected order scoring (4–5 h), helper
  ablation (2–3 h), or a gate-sum return (4–6 h). It deferred each until a decision needs it.
- A rectifier source redesign would be a second try at the same candidate after a failed rule.
- Roots 01 and 23 have no allocation, and no reopen condition is met.

What the program review should weigh:
1. **R-all's portability record.** It now has one development-bank success (order helpers, 0.40×) and one fresh-content
   probe that acquired nothing. That probe failed for a reason specific to how the sources are solved. Is a forcing
   source design (say a census-gated stage 0, ~2 h) worth one more look, or does this end the frozen-recipe line?
2. **Parameterized abstraction.** Strategy deferred it until "a frozen-recipe boundary exposes a representational
   limit that parameterization specifically addresses". This probe does not meet that: the limit here is that
   sources rarely build the helper at all, and parameterization would not fix that either.
3. **Root 23 (inherited variation).** It is the owner's long-term gap. Its reopen conditions are still unmet.

**Parked questions re-checked.**
- 50: needs R-tree first-attempt ≥ ~90%; it was 0/96 here.
- 52, 53: their reopen conditions name a parameterized method or a mechanism decision; neither applies.
- 45(iii): needs protected cells scored with the frozen method; none were scored.
- 01's parked children and root 23: no trigger.
None reopened.

**Digest check (critique notes 5–7), fixed.**
- 52's summary and reopen text no longer turn eight capped literal libraries into "fails".
- 53's summary now reports helper containment and the coverage stratum as observations, without donor use or a
  causal coverage limit. The append-only logs got correction entries.
- The digest's Overall now says "an uncapped library holding acquired order helpers … helpers' causal contribution
  unresolved".
- The 54 probe stays out of the digest's beliefs. It is mentioned only as a parked sub-question and in the "Not
  shown" list.
