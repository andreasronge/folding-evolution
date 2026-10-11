# Do the acquired order helpers need their learned arrangements?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
funded by [strategy 1628](../runs/2026-10-11-1628/strategy.md). The steward supplies
the proposal, fixed size and primary decision rule. This is a mechanism question
and implementation direction, not an experiment registration.

The frozen order libraries reduced evaluations to 0.37 of ordinary tree GP on
held-out combinations. Their post-hoc coverage gradient is strong, but libraries
with no destination-needed helper also helped. Before requiring future source
tasks to produce named helpers, ask whether the helper entries' arrangements
add useful information beyond their primitive supply and shapes. A loss under
replacement would support acquiring intact computations; useful retention would
make a simpler donor-generation target worth considering. Neither outcome alone
establishes a new learner or portability to new content.

Reuse all 24 saved R-all libraries and the six original development cells of
`x4-order-v1`. The bank is development data; do not describe another scoring pass
as protected. Reconstruct and verify the libraries from
[execution 1530](../runs/2026-10-11-1530/execution.md), preserving their acquisition
identities. No source collection, corpus selection, refitting or cap change.

Build a constrained replacement of the entries whose complete D625 output vector
equals one of the twelve pairwise min/max helpers. Identify all twelve classes,
independently of which destination will be searched. Leave every other entry
byte-identical. Within each helper entry, permute labels only among positions
with the same arity and compiled token width. This preserves its exact primitive
counts, arity/width skeleton, node count and compiled length. Accept a replacement
only when neither it nor a proper subtree equals any of the twelve helpers on
D625. Retain the original library slots and uniform draw probabilities, including
duplicates created by rearrangement; deleting entries and renormalizing the
remainder would change the intervention.

Use a fixed, bounded construction rule and independent construction seeds, with
several pre-stated realizations per acquisition. Never choose replacements by
search performance. Audit every invariant and report semantic diversity and
construction failures. A support failure returns to strategy; it does not permit
dropping an entry or relaxing the matching. These are diagnostic, helper-aware
controls, not an acquisition algorithm or a proposed deployment procedure.

The [static planning audit](../runs/2026-10-11-1628/helper-planning-audit.json)
independently reproduced all saved semantic hashes. Every build contains 4–10
helper entries, 177 total; none of the other entries contains a helper-valued
subtree. A fixed-seed support check found an admissible within-entry permutation
for all 177, with at most 16 draws under a 256-draw limit. This establishes support
for the proposed intervention on these artifacts, not efficacy, production-VM
agreement for the new controls, or timing of the experiment. Reproduce those
checks in the reviewed harness before scoring.

Reuse `order_library.py`, `tree_permutation.py`, `tree_library.py` and the order
scoring wrappers on `research/main` (latest completed study `53f0e06`). The
existing permutation code pools across entries: this intervention must instead
keep pools within each helper entry and preserve nonhelper entries. Reuse its
signature checks and the independent interpreter/VM checks. The existing search
accepts a frozen donor list; no change to the evaluator or selection engine is
needed. Keep the initializer, half-library mutation probability, crossover,
32-token capacity and eight-attempt restart schedule fixed. Ordinary mutation
and crossover may still discover helpers; do not add an evolutionary veto.

Compare intact R-all, the constrained replacements and ordinary R-tree on fresh
paired searches. The primary question is the cost of replacing the helpers'
arrangements. R-tree is necessary to distinguish useful retention from both
procedures being poor, and to expose a replacement that is actively harmful.
Use one decision-sized capped arithmetic-cost comparison with a 95% interval,
plus solve counts. Preserve uncertainty over acquisition builds and construction
realizations; more searches under one replacement are not independent library
acquisitions. Do not turn the historical coverage strata into selected cohorts.
The supplied R-order reference remains far cheaper in the existing record;
this study does not buy a new practical-superiority claim.

A material loss identifies a contribution of these entries' learned arrangements
relative to this matched replacement law, conditional on the rest of R-all.
It does not isolate an abstract semantic mechanism from every consequence of
rearrangement, prove that these twelve functions are uniquely necessary, or
attribute a universal percentage of the saving to helpers. Useful retention at
a resolved bound would show that their exact computations are unnecessary at
that resolution, not that all library content is irrelevant. Broad uncertainty
needs a price for resolving a consequential difference, not an automatic top-up.

Allocate one full experiment, **3–5 hours total**, including proposal, preparation,
validation, reviews, scoring, analysis and contingency; preparation at most 120
minutes and summed queue timeouts at most 90 minutes, within the five-hour total.
1228 completed 2,304 development scoring jobs in 836 seconds; 1530 measured
R-tree/R-all means of 6.36/2.39 worker-seconds and 9.8 effective workers on its
held-out roster. Replacement tails and construction overhead remain unmeasured.
Price precision and complete cost from saved development data and bounded
implementation timing before admission. Do not substitute a small exploratory
probe if a useful comparison cannot fit.

Return to strategy after the result or an earlier validity, precision or cost
obstacle. A positive contribution makes source opportunity for intact content a
defensible consideration in a later fresh-family plan. Useful retention removes
the rationale for a helper-containment admission gate and shifts attention to
statistical donor supply. Neither branch automatically funds that next learner,
another bank, a rate sweep or an abstraction engine. Finish before
**2026-10-12 14:19:15 Europe/Stockholm**.

The closest reuse precedent found during this review is [Keijzer, Ryan and
Cattolico, *Run Transferable Libraries* (2004)](https://link.springer.com/chapter/10.1007/978-3-540-24855-2_63).
Here external extraction supplies expanded mutation donors. The question adds a
mechanism comparison on that known class of approach; it does not claim novelty
for transferring acquired program pieces.
