# Can successful training programs teach a useful decoder context?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md), chosen
by [strategy 1707](../runs/2026-10-07-1707/strategy.md). This is a direction and feasibility
plan, not an experiment registration. The steward fixes the design, sizes and outcome rules.

**Question and changed scope.** Can a previous-token decoder fitted to independently
evolved exact training solutions speed fresh search beyond token-only fitting, and can
any increment transfer to the existing withheld compositions? The previous experiments
selected map mutations using noisy search costs. Here successful program sequences provide
the fitting signal directly. This is external fitting, as distinguished in the
[original root plan](compositional-map-transfer.md), not evolutionary adaptation of decoder
parameters. A positive result would supply a data-derived target for later map evolution.
A negative result would limit this estimator and corpus, not contextual decoder capacity.

**What to build.** Reuse the reviewed code on `research/main`, particularly
`composition_search.py`, `four_reducer_maps.py`, the frozen four-reducer bank and the
[1723 split](asymmetric-family-transfer.md). Keep D1331, G4, `v2_rmin_first`, population
size, latent tape length, operators and exact verification fixed. Train on the four BE or
six PA training cells; exclude all three holdouts from corpus production and fitting.

The current `composition_search.search` verifies exact programs but returns search summaries
without their token tapes. Add an optional return/save of the first exact solver, preserving
random-number consumption and search behaviour. Do not assume the old result files contain
recoverable solver corpora. Generate independent corpora through fresh G4 searches; old
training runs may be deterministically replayed only with provenance and unchanged behaviour.
Do not collect from the learned family maps, whose training histories would confound the
new comparison. Save task, seed, failed attempts, cost, table hash and solver tokens.

Fit a regularized previous-token table and a restricted G4-plus-global-token-multiplier
table to the same corpus, using the same full decoded tapes and task weighting. Shrink
the contextual fit toward G4, preserve token support and validate the quantized decoder.
Use the restricted fit as the important control: stripping all G4 context would create
an unnecessarily weak baseline. A likelihood fit to observed token transitions is one
simple implementation; this plan does not assert that its likelihood predicts search speed.
Include frozen G4 to detect degradation in both fits.

Canonical solutions and the hand-set BE/PA grammars must not supply fitted parameters.
Only training solver tapes enter fitting. Transfer only decoder tables; evaluation starts
with fresh latent genomes, never corpus programs. Freeze one fitting/preprocessing rule
before confirmation. Full tapes contain inactive material, so a negative result cannot
exclude a learner over executable structure; do not respond with an unbounded pruning or
smoothing sweep. Weight tasks equally and account for uneven solve rates rather than
letting the easiest task dominate the corpus. Corpus-generation failures consume budget.

**First experiment.** Measure corpus yield, fitting stability, emitted marginals and actual
search cost on training cells. G4 solved 45–50 of 50 searches per retained cell in
[1603](../runs/2026-10-06-1603/analysis.md), with reported full-cap search cost around
1.9 seconds; these justify a probe, not a runtime guarantee for newly fitted tables.
The nested-learning rate from 1137 must not be used to price this different procedure.

Use disjoint sets of corpus-generation searches as independent fitting replicates. A
bootstrap of one corpus measures conditional uncertainty; it is not independent learning
replication. Pair contextual and restricted fits within each corpus and evaluate them on
shared fresh seeds. Fit once per corpus, rather than repeatedly optimizing against the
evaluation block. Choose regularization on separate training-only calibration data, if
needed, then freeze it before independent confirmation.

Prefer a single queue containing a bounded calibration and an adequately replicated
fresh-training comparison. Budget all solver collection, fitting, failed searches and
evaluation. Target no more than three queue hours, reduced by elapsed preparation against
the 22:25 deadline; retain approximately two hours outside the queue. A small probe that
only demonstrates fitting or greater likelihood is not evidence of search improvement.
If confirmation cannot fit, report the measured feasibility and precision limit honestly.

**Transfer and interpretation.** If meaningful training improvement and adequate time are
established under pre-stated rules, freeze the maps and evaluate both training families'
fits on the three existing withheld cells. Include the paired restricted fit and G4.
For attribution to additional context, also fit a G4-based token-multiplier control to the
contextual map's emitted token marginals and verify the match over the actual finite tape
length. Merely averaging transition rows or removing residuals does not preserve those
marginals. If this control cannot be validated, report a comparison of procedures without
claiming an isolated contextual contribution.

The withheld cells have been inspected repeatedly; call this transfer on a reused screened
bank, not an untouched benchmark. One BE target remains one task. Matched/mismatched
performance and own-family improvement are separate questions: slowing the other family
alone does not establish useful family adaptation. A contextual gain without a family
preference would still establish useful generic learned assembly bias at this scope.

**What counts as an answer.** Search improvement over both the restricted fit and G4
establishes useful external fitting; an increment surviving the marginal control supports
additional context. Transfer strengthens that answer beyond the fitted tasks. Better
likelihood or sampling alone does not establish evolutionary-search usefulness. Training
gain without transfer limits generalization. Tight small-effect bounds limit this fitting
rule; wide intervals remain unresolved. Charge corpus production separately and report
whether future search savings could amortize it. No outcome resolves joint map/program
coevolution or isolates solver supply from variation quality.

One existing root-10 slot is allocated. Any further study returns to strategy for an
allocation; a promising result does not authorize an optimizer sweep or a new bank here.
