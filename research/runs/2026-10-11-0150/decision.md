---
next: strategy
---
# Decision: close 45, return to strategy

**Close [45](../../questions/10-compositional-map-transfer/45-tree-subtree-library/question.md).** The run
was complete and valid ([analysis](analysis.md), code review pass, commit `d7ec100`): all 4,608 scoring rows
present, seeds paired across arms and disjoint from history, the off-path replay of 8 saved 0024 jobs matched,
and every library and control was re-derived from saved source rows before scoring. It landed on the plan's
row 2 ("useful search-content increment") by a wide margin:

- mean evaluations R-lib ÷ R-tree **0.390 [0.332, 0.463]** (87,352 → 34,109; about 2.6× cheaper);
- R-lib ÷ size- and length-matched random donors **0.414 [0.332, 0.533]**; R-size ÷ R-tree 0.944 [0.790, 1.120];
- solved 1,536 vs 1,524 of 1,536 (difference +0.008 [+0.004, +0.012]); worker seconds 0.373 [0.315, 0.443].

R-lib was below R-tree in 24/24 acquisitions and all 8 cells, including the cells whose pair split no
learned predicate contains (0.35–0.53×). The gain shows as more first-attempt solves (1,121 vs 715), not as
library entries copied into final solvers. Acquisition repays after about 54 [45, 65] target searches per
library. The effect is past the proposal's own surprise threshold (> 1.3×). The plan required an inspection
for an effect that large; it was done and found no route to under-charging R-lib.

**What it does not settle, and how sure I am.** I am fairly sure of the direction and rough size *on this
development bank*. Three things are open:
1. **Ingredient.** The size control matches node count and compiled length, not content. Every learned
   entry contains an input; about a third of the controls contain none. So "content" here may be the
   `GT(ADD,ADD)` comparison skeleton, the pair sums, or simply more inputs and `ADD` in donors. The 4
   predicate-free builds gained less (0.26–0.98), but n = 4 is only an observation.
2. **Homogeneity.** 3 of 4 source cells share one pair split, so nearly every library is "pair sums plus that
   predicate". A hand-written five-entry library might reproduce most of the effect, and two 16-job stage
   libraries already held the same entries. The 54-search repayment is therefore an upper bound on what the
   information costs.
3. **Transfer.** DG is development data. Gains on "uncovered" cells show the library does more than copy a
   matching predicate. That is still the same family, not a fresh bank.

**Why `next: strategy` and no proposal.** Strategy 0150 funded exactly this one experiment and required a
return to strategy after its result. A useful result "earns consideration of a 5–8 h fresh-bank stage"
without allocating it. Root 10 is at 37/37. No other open question has budget or a case. I re-checked
the reopen conditions for root 23, the parked root-01 questions, and 32, 33, 43 and 44. None is met: this
result concerns literal subtree donors in tree GP. It is not an inherited or frequency bias, it is not a
size-aware tree GP, and it is not a fresh bank.

**For the strategist.** I would rank the candidate follow-ups this way:
- **Cheap ingredient test first (about 2–3 h total).** Use the existing harness and saved acquisitions, with
  no new source searches. Arms: hand-set {pair sums}, {comparison skeleton only}, and an input-only
  token-frequency donor control at the realised ~11% insertion rate, all against R-tree. It separates
  structure from token bias, which a fresh bank cannot do. It also tells a fresh-bank design what to freeze.
  This is a mechanism test of a known method (run-transferable libraries; Keijzer et al. 2004).
- **Fresh-bank stage (5–8 h, per the plan).** This is the transfer claim the core question needs: the
  method frozen with a genuinely unsearched family, R-tree kept as the comparator, and acquisition
  replicated. It is worth doing whichever ingredient wins. Doing it second costs about one cycle and
  lowers the risk of freezing an over-specific extractor.
- **Not worth buying now:** other insertion rates or caps, larger acquisitions, TS as a boundary, or
  precision on DG.

This changes the program's position. It is the first learned bias in this tree to beat restarted tree GP
in evaluations, and it does so by a large margin. It does this by external fitting
plus frozen insertion, not by inheritance. Root 23's question remains separate.

**Digest check (critique 0150, notes 6–9) applied.**
- Note 6: 44's summary and the digest now read "noninferior within the prespecified 3-point margin; equal
  reliability not established".
- Note 7: 44's reading now gives (b)'s stagnation/shortcut mechanisms as hypotheses. Only the
  evaluation-ordering result is stated as a finding.
- Note 8: independence and build heterogeneity are now worded "consistent with". A correction note is
  appended to 44's log, which stays append-only.
- Note 9: the digest's "not shown: a learned bias that improves on restarted tree GP" is replaced. That
  is now shown in evaluations on development data. "What carries the subtree library's advantage" and
  "the subtree library on a fresh bank" are added as not shown.
