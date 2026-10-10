# Does cheap acquisition survive changing its source compositions?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 0145](../runs/2026-10-10-0145/strategy.md). The steward supplies
the proposal, fixed size and primary decision rule. This is not an experiment registration.

The next question is whether the unchanged four-plus-four adaptive procedure acquires
a useful frozen bias from a different set of source compositions. A8 already has
multiple independent acquisitions and useful fresh-target performance. Merely adding
source seeds on the original cells would mostly increase precision. Changing the source
cells instead tests whether the acquisition recipe depends on the particular tasks on
which its source size, fallback and feedback policy were developed. A collapse would
keep A8 as a demonstrated source-specific recipe; useful replication would justify
carrying the procedure to a later, genuinely new family.

**Source change, fixed target.** Use all four former comparison-gate-v1 holdouts per
family as the replacement acquisition roster. Recover their exact IDs from the frozen
1246 bank's `split.holdouts`, also recorded in the
[historical cost audit](../runs/2026-10-10-0145/source-replication-cost-audit.json).
Choose the complete roster because it is the existing complementary split, not because
individual source cells yielded attractive results. Keep BE and PA separate. Preserve
D1331, primitives, G4, P256, 32-token tapes, cap, exact verifier and ordinary operators.
These cells have already been scored as targets: they are development tasks, newly used
as sources, not an untouched bank or a new family. Original holdout evidence remains
historically valid for the maps that did not train on them.

Keep the complete sixteen-cell two-sum-v1 roster as the evaluation destination. It is
now development data too. Check exact behavioural separation and the frozen manifests;
do not build another bank, relax a screen or choose targets after seeing new maps.
No target score or target solver may select source cells, maps, libraries or checkpoints.
This deliberately changes acquisition while holding the destination fixed; changing both
would make any failure harder to interpret and add avoidable bank work.

**Bounded build.** Reuse reviewed `research/main` code: `small_source_run.py`,
`sparse_feedback_run.py`, `solver_corpus_fit.py`, `fragment_library.py`,
`fragment_operator.py`, `two_sum_run.py` and `composition_search.py` (latest study
`74196a8`). These runners are absent from this `main` checkout. Inspect that branch;
do not duplicate the search engine.

Source inspection found two concrete changes: `build_source` passes the hardcoded
`TRAINING` roster to the count fitter, and `extract_windows` uses it for padded-solver
exclusion and leave-one-cell-out libraries. Pass an explicit source roster through those
interfaces, retaining the original default and exact old-source replay. The old
`load_training` intentionally returns only original training labels: add a validated,
explicit replacement-source loader rather than silently changing its contract. Audit
all source-membership, recurrence, fallback and full-solver-exclusion checks against
the replacement roster. Do not alter shrinkage, normalization, extraction or edit laws.

For every independent acquisition, collect four fresh G4 attempts per source cell,
fit C4 and extract F4, then collect four more under that build's own frozen C4+F4 and
refit the pooled attempts to A8. Retain failures, empty cells and the existing fallbacks.
No saved old decoder, library, solver tape or transition count enters the new build.
Save all costs and provenance, including the intermediate fit used for collection.

Keep an equal-attempt static S8 comparator: share the first four attempts, collect four
further fresh G4 attempts, then apply the same final fitting rule. It can distinguish
a failure of adaptive collection from a source set that teaches both procedures poorly.
It is a secondary policy comparison, not an attempt to resolve the old 1.10× increment.
There is no third round, new 48-attempt reference, or source-size sweep. Prior full-F
parity is not being retested. Freeze the procedure before collecting confirmation sources.

**First experiment and answer.** Score every new A8 and S8 with fresh populations and
paired evaluation seeds on the full target roster; retain G4 for absolute usefulness.
The primary question is useful frozen A8 acquisition against G4. A speed gain of about
1.5× is a plausible practical resolution to price against the previous 2.73× effect;
the steward must set the actual margin, adequate fixed size and explicit unresolved
outcome before confirmation. Do not make a tiny feedback increment the admission target.
Keep solve counts, both source families, every target and cap sensitivity visible.
Report adaptive/static performance separately from absolute usefulness.

Independent new acquisitions are the uncertainty units; targets and scoring seeds do
not create more acquisition replicates. Sixteen builds, eight per family, with four
evaluation seeds per target is a costing scenario, not an imposed adequate size. Unlike
the old sixteen-corpus/four-nested-block analysis, these can be sixteen independent
builds without a redundant block hierarchy. Allow for their potentially greater spread.
Historical A8 is contextual evidence, not a paired ancestor or another new replicate.
Reuse historical G4 rows only with provenance/replay and their sampling uncertainty
propagated; otherwise price fresh G4 searches. Never count one shared baseline repeatedly
as independent evidence.

Charge arithmetic acquisition plus repeated-search cost, A + N*S, in evaluations and
separately in measured time. Include failed searches, both fits, verification and library
extraction; charge the shared first batch once per deployed procedure. A capped-cost
advantage is not uncapped expected solve time. Show break-even horizons and uncertainty
without assuming the owner's intended deployment horizon.

Useful A8 beyond G4 would extend acquisition evidence to this complementary source
roster. Useful S8 with poor A8 would limit the adaptive policy. Both performing poorly
would limit this small-source recipe on these tasks, without identifying a decoder,
library or source-yield cause. A broad interval remains unresolved and needs a resolution
price. No outcome establishes new-family generality, family specificity, semantic modules
or inherited map evolution. Without token/chain controls it does not isolate context
or fragments. The mechanism is externally updated program bias, related to
[Salustowicz and Schmidhuber, PIPE (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/),
with frozen reuse and block edits rather than PIPE's particular update rule.

**Complete cost and exit.** Allocate one experiment through the next strategy review,
**4–5 hours total**, within the remaining approximately six hours. Target about one hour
of preparation, 1.5–2 hours of collection/scoring and 1.5–2 hours of proposal, review,
analysis and contingency. Preparation remains capped at 120 minutes; summed queue
timeouts at most **3 hours**, reduced against the actual deadline
**2026-10-10T08:12:10 Europe/Stockholm**, leaving at least one hour for analysis/decision.
These maxima are not additive entitlements.

The historical audit found G4 solved 196/256 searches on the replacement cells, averaging
12.03 worker-seconds; no new searches were run for this review. Sixteen paired acquisitions
need 512 G4 attempts and 256 adaptive attempts. At that G4 rate and 2033's approximately
4.9-second adaptive rate, collection is about 15–20 minutes at eight effective workers.
Two fitted arms × sixteen builds × sixteen targets × four seeds gives 2,048 searches;
adding 256 G4 searches at 2303's measured 17–23 worker-seconds suggests roughly 85–90
minutes of scoring at that concurrency. Fitting, extraction, replay and timing add to
that. These are projections: new source maps and their tails have not been measured.

Validate the roster change and measure collection, fitting and scoring at intended
concurrency on separate calibration seeds. Freeze confirmation size using an honest
precision allowance and the full price, not favorable efficacy from a small timing batch.
Return to strategy after the complete comparison or earlier on a build, validity,
precision or deadline obstacle. A standalone feasibility cycle is not the intended
deliverable; do not spend a slot merely demonstrating that new sources can be collected.
No second experiment is funded. Stop if an informative complete comparison cannot fit;
preserve this plan for later rather than shrinking into an uninformative result.
