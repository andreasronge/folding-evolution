---
next: strategy
---
# Decision — 2026-10-11-1628 helper-entry rearrangement in R-all order libraries

**Close [57](../../questions/10-compositional-map-transfer/57-order-helper-arrangement/question.md); no proposal;
return to strategy.** The pre-stated rule reached its *material loss* branch. [Strategy 1628](strategy.md), the
[plan](../../plans/order-helper-arrangement.md) and the [proposal](proposal.md) route every outcome back to
strategy. Root 10 is now at 47/47, and roots 01, 23 and 55 have nothing left. The run has used 18 of 40 slots, with
about 20.5 h before the 2026-10-12 14:19 deadline.

**What the run showed** (commit `46e05cb`; complete 3,456-row grid; [analysis](analysis.md)).
- In each saved R-all library, only the 4–10 helper-valued entries were changed (177 in total). Their labels were
  permuted within the entry until no subtree computed a helper. Material, shape, slots and draw probability stayed
  fixed. There were four realizations per build, and 613/708 replaced slots became single-input projections.
- **R-hx / R-all = 2.35 [2.07, 2.66]**. The whole interval is above the 1.25 bar. Q was above 1 in 24/24 builds,
  6/6 cells and 4/4 realizations.
- R-hx / R-tree = 0.90 [0.83, 0.98], against R-all / R-tree 0.38 [0.34, 0.43]. That 0.38 replicates 1228's 0.40
  under fresh seeds. In log terms, about a tenth of R-all's saving survives the rearrangement.
- With the helpers permuted, the coverage gradient disappears (R-hx 0.99 / 0.86 / 0.94 of R-tree).
- Permuted entries were drawn and inserted at the same rate as the originals. So the loss is not caused by the
  library going unused.
- The solve counts were 1,146 / 1,151 / 1,147 of 1,152.

**Why close.** The question had one registered answer and it landed far from the threshold, with a consistent
direction everywhere. More seeds would not change it. The result enters the digest as a belief with a narrow scope.
On the order development cells, intact helper entries beat mostly trivial entries of the same material, given the
rest of R-all and this search regime.

What it does not show:
- That min/max beat *other nontrivial* computations. Matched nontrivial replacements mostly cannot exist for
  six-node entries.
- Which helpers, or how many per build, carry the saving.
- Whether search reconstructs helpers. The solver census is 100% in every arm, so it carries no information.
- Anything on a fresh bank.

The stratum-0 Q (1.28 [0.98, 1.72], 144 units) is unresolved. So whether R-all's small no-helper saving is also
helper-borne stays open. I do not think a decision depends on it.

**Tree upkeep.**
- 57 is closed. Root 10's summary, sub-question entry, budget line (47-slot) and log are updated.
- Digest:
  - New bullet: "Rearranging only the helper entries removed most of that saving on the development cells."
  - The order bullet is tightened. Its "helpers' causal share is untested" clause is gone, now superseded.
  - The Overall paragraph is updated.
- Critique digest-check notes:
  - **5**: "no reliability loss" now reads "no loss observed; registered failure-count guard passed" in root 10's
    summary and sub-question list. A correction entry is in 56's log.
  - **6**: 56's explanation (c) is corrected in a log entry: unsearched cells exclude fitting to their outcomes,
    not reusable non-helper content, and the carrier was unidentified there.
  - **7**: the digest's capped-library clause now says "on the development cells".
- Parked questions re-checked; none has its reopen condition met:
  - 50 needs a destination where R-tree solves ≥ ~90% first time. Here it was 629/1,152 = 55%.
  - 54 needs a funded rectifier source design that forces the helper. 57 strengthens the reason for such a gate
    but does not fund one.
  - 55 and 23 need redesigned instruments.
  - Root 01's parked questions are untouched.

**Candidates for the strategist (my pricing, not funded).**

| Candidate | What it would decide | Cost |
|---|---|---|
| **Fresh content-family bank, frozen R-all recipe, stage-0 source census** (new root-10 question) | Whether externally acquired donor libraries transfer beyond the bank they were developed on. 57 now says the saving rides on intact helper entries. Transfer therefore hinges on whether the new family's sources build its helpers and the extractor keeps them, and that is exactly what [54](../../questions/10-compositional-map-transfer/54-rectified-sum-acquisition/question.md)'s rectifier sources failed to do. Stage 0 measures the own-helper rate in source solvers (≥ 25% gate) and whether R-all pools contain them, before any scoring. | About 2 h for the stage-0 probe, then about 4–5 h of scoring; 7–9 h total. Needs a concrete family, which strategy 1628 found missing. |
| Partial helper permutation (dose / per-helper attribution) | Whether the saving scales with the number of intact needed helpers, as the strata suggest (stratum Q 1.28 / 2.10 / 4.22). | About 3 h, saved libraries, no acquisition. It adds mechanism precision, but no current decision depends on it. |
| Root 55 redesign (inherited choice of a useful library) | The missing per-individual inheritance half of the core question. | Strategy 1628 priced it at 10–14 h, with instrument gaps still open. |
| Stop the run | The order line has a held-out answer and a mechanism answer at development-bank scope. | 0 |

**Recommendation.** If anything more is bought in root 10, buy the **fresh-family bank with a census-first stage
0**. 57 removes the main reason to doubt that a helper census is the right gate: the helpers carry the saving.
The strategist should hold the design to a concrete family whose sources cannot route around the helpers. The
stage-0 census is the cheap stop: if it fails, the bank fails before any scoring. I would not buy partial
permutation. If the strategist judges the inheritance root more central to the core question than a fresh-bank
transfer claim, a fully priced 55 redesign is the alternative. Stopping is also reasonable.
