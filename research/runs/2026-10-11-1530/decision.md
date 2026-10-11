---
next: strategy
---
# Decision — 2026-10-11-1530 frozen R-all libraries on the 24 protected order cells

**Close [56](../../questions/10-compositional-map-transfer/56-order-library-protected-cells/question.md); no
proposal; return to strategy.** The pre-stated rule fired its "useful held-out saving" branch. Both
[strategy 1530](strategy.md) and the [proposal](proposal.md) route that outcome to strategy, and no later
experiment was allocated. Root 10 is at 46/46. Roots 01, 23 and 55 have nothing left. The run has used 17 of 40
slots, with about 22 h before the 2026-10-12 14:19 deadline.

**What the run showed (commit `53f0e06`; complete 3,456-row grid; [analysis](analysis.md)).**
- The 24 saved 1228 R-all libraries were rebuilt and checked byte-identical. Nothing was refitted. On the 24
  never-searched protected cells, **R-all / R-tree was 0.37 [0.33, 0.42]**. That is a ratio of pooled capped
  means with a whole-build bootstrap. On the development cells it was 0.40 [0.32, 0.50].
- Reliability: R-all solved 1,152/1,152 and R-tree 1,146/1,152, so there was no reliability loss.
- R-all was below 0.67 in 24/24 builds. Every cell is below 1 by point estimate. Disjoint cells gave 0.34 and
  overlapping cells 0.38.
- The supplied order prior is still 6.9× [5.7, 8.6] cheaper than R-all. R-all recovers about half of the log gap
  from R-tree to R-order, the same as in 1228.
- Against R-tree, acquisition repays after about 4 searches.
- The post-hoc coverage gradient reproduced: 0.74 / 0.42 / 0.19 of R-tree with 0 / 1 / 2 needed helpers in the
  library.

**Why close.** The question was whether a saving chosen with six cells in view holds on the combinations kept out
of development. It does, at least as strongly, with nothing tuned on those cells. Getting this answer did not
need a further stage, and more seeds would not change it. It enters the digest as a belief, scoped to
**held-out cells of a development bank**. The same twelve helpers and source corpora serve both rosters. So the
result says nothing about fresh-bank transfer, does not show that the helpers cause the saving (the no-helper
stratum is still 0.74 [0.57, 0.93]), and gives no advantage over supplied helpers. Competing explanation (a),
roster luck, is not supported: the held-out estimate is not weaker. That is a comparison of two intervals, not a
measured equality. Explanation (b), lower coverage, is ruled out descriptively: coverage matched. Explanation (c),
cell-specific content, cannot apply to cells no library ever saw.

**Tree upkeep.**
- 56 closed. Root 10's summary, sub-question list and budget line are updated, and 53's stale "open" entry there
  now reads closed.
- The digest's order bullet now covers both rosters. The Overall paragraph's "beyond development cells" gap now
  reads "on a fresh bank".
- The critique's digest-check notes 6–9 are applied to question 55's summary, with a correction entry in its log:
  - 290/336 trajectories absorbed in episode 0, not 328/336.
  - "Not better than R-all" now reads "no improvement established".
  - Z is neutral-compatible, which does not exclude an increase.
  - The ≈1.2× dose-curve figure is labelled an unvalidated projection.
  - "Drift decided every trajectory" now reads "every trajectory absorbed rapidly".
  The digest did not carry these wordings.
- Parked questions re-checked; none has its reopen condition met:
  - 50 needs a destination where R-tree solves ≥ ~90% on the first attempt. Here 598/1,152 R-tree jobs needed a
    restart.
  - 54 needs a rectifier source design that forces the helper.
  - 55 needs a redesigned polymorphism-keeping instrument.
  - 23 needs a changed rule or bank.
  - Root 01's parked questions are untouched by this result.
  - 53's closed-question reopen condition (a decision that needs helper causality) is the strategist's call; see
    below.

**Candidates for the strategist (my pricing, not funded).**

| Candidate | What it would decide | Cost |
|---|---|---|
| **Fresh content-family bank, frozen R-all recipe** (new root-10 question) | Whether externally acquired donor libraries transfer to a bank frozen before scoring. This is the only step that widens this line's scope beyond a development bank. Rectifiers ([54](../../questions/10-compositional-map-transfer/54-rectified-sum-acquisition/question.md)) failed because sources could route around the helper. A new family needs a stage-0 own-helper census (≥ 25% of source solvers build a needed helper) before any scoring. | Two stages: stage 0 probe about 2 h, then scoring about 4–5 h. Total 7–9 h, which fits before the deadline. |
| Helper ablation from saved 1228 libraries (reopens 53) | Whether the twelve helper classes carry R-all's saving, versus other recurrent content or a lower trivia share. It is causal and cheap: no acquisition, saved libraries, development cells. | 2–3 h |
| Stop the run | Root 10's order line has its answer at development-bank scope. The inheritance roots (23, 55) need redesigns that strategy 1530 priced at 10–14 h, against a fixed R-all that already wins. | 0 |

**Recommendation.** If the strategist wants one more answer from root 10, fund the **fresh-bank test**. It is the
only candidate that could change what we claim: external acquisition would go from "works where it was developed"
to "transfers". It should start with the census probe, so that a 54-style source failure is caught in about 2 h.
Helper ablation would sharpen a mechanism no current decision depends on. I would buy it only if the fresh-bank
design needs to know which content to require of its sources. If neither seems worth its full cost against the
core question, stopping is reasonable: the run has given clean answers, and the 23 unused slots are not an
obligation.
