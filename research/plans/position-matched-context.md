# Does position-specific token supply reproduce the fitted decoder?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 0239](../runs/2026-10-09-0239/strategy.md). The steward supplies
the proposal, fixed size and decision rule. This is not an experiment registration.

**Question.** Can C's position-specific token frequencies, with only G4's supplied
conditional structure, reproduce C's search performance? If so, is that supplied
structure necessary, or do independent position-specific draws suffice? This decides
whether to target positional frequencies or learned token dependencies in a later learner.

The latest [C/K result](../runs/2026-10-09-0125/analysis.md) rules out the tested
pooled-frequency replacement. It does not settle this question. A deterministic
inspection in strategy 0239 propagated each saved C and K table through 32 positions:
`m[0] = transition[start]`, `m[j] = m[j-1] @ transition[body]`.
Across the 16 corpora, C–K total variation at position 0 ranges from 0.07150 to
0.21042; averaged over positions it ranges from 0.00908 to 0.01677. These are properties
of frozen tables, not new search results. Small average differences need not be harmless
when the beginning of a stack program is especially consequential.

**Build and controls.** Reuse the 1246 corpora at
`experiments/output/2026-10-08/2026-10-08-1246-comparison-gate-training/corpora.json`,
the 1548 row-F bank, seeds and C/T results, and the 0125 K results. The reviewed runner
is `experiments/chem_tape/frequency_matched_run.py` on `research/main` (0125 code
`8e62831`); the current main checkout lacks that harness. Preserve D1331 length-three
inputs, the alphabet, 32-position latent tapes, primitive executor, allele range,
selection, variation and exact verification.

Extend decoding narrowly to accept position-specific tables while preserving legacy
decoding and RNG consumption. Build two controls from each frozen C without consulting
target performance:

- **Q, primary replacement:** at each position, reweight G4's next-token columns by
  position-specific multipliers, normalize each conditional row, and match C's emitted
  marginal at that position under the uniform latent prior. Propagate the actual Q
  marginal to the next position. Q retains G4's previous-token dependence; it is
  not context-free and must not be described that way.
- **P, interpretation control:** sample each position independently from C's marginal
  for that position. This removes all previous-token dependence, including the supplied
  grammar. Its failure alone cannot establish that *learned* context is necessary.

Fix fitting, quantization and support treatment before scoring. Validate finite-length
marginal agreement after quantization at every position, using both maximum token error
and total variation; a pooled check is insufficient. Preserve the existing support floor
and allele range. If constrained Q fitting cannot attain an informative tolerance, report
that obstruction rather than silently change the intervention or accept mismatched rows.
P is a straightforward categorical lookup; Q needs position-and-previous-token lookup.
Validate deterministic decoding, uniform-allele marginals, support, and exact legacy C/T/K
replays. Do not introduce a general decoder engine or a new inverse-encoding path here.

An unrestricted positional map has 32 × 23 free probabilities, versus 25 × 23 for
the current conditional map. Independence simplifies dependencies, not necessarily
parameter count or learnability. Neither Q nor P is acquired by evolution: both are
external projections of C. A successful replacement supplies a target for acquisition,
not evidence that selection can reach it.

**First experiment and answer.** Score Q and P on the same complete then-addition roster
as 1548 row F, with corpus pairing and fresh program populations. Reuse saved C/T/K
rows only after replay and provenance checks. The primary question is C versus Q;
keep P and T visible to distinguish the need for supplied grammar and a degraded
replacement. Retain all corpora and both training-family labels. Use corpus-level
uncertainty, per-cell results, solve counts and sensitivity to the cap penalty. The
steward sets one useful sufficiency margin and a fixed size capable of changing the
representation decision. An unresolved interval is not equivalence.

If Q recovers C within that bound, learned changes to conditional structure are not
required by this replacement test; P distinguishes independent positional supply from
positional supply plus supplied grammar. If C retains a worthwhile advantage over
both, prioritize learning dependencies rather than positional frequencies alone.
Discordant controls or broad intervals remain explicit outcomes, with a resolution
price. C beating both does not identify active fragments, distinguish solver supply
from variation neighborhoods, or explain family specificity. All marginals concern
the uniform latent prior, not populations after selection. Then-addition is now a
development bank; this is a mechanism test, not another fresh-bank transfer result.

**Cost and exit.** One root-10 slot through the next strategy review, **5–7 h total**
for preparation, validation, queue, review, analysis and contingency; at most **4 h
summed queue timeouts**, preparation at most 120 minutes. The measured anchor is
0125's 2,048 K searches in 42 minutes. Two new arms suggest roughly 84 minutes at
that rate, but Q/P throughput, lookup construction, tails and reporting must be measured.
The full price includes both controls and a decision-sized comparison, not merely a
working decoder. A probe-only fallback has the separate 60-minute timeout cap and
returns to strategy without a sufficiency verdict. No new solver collection is needed.

Return after the result or any build, validity or full-cost obstacle. No automatic
position-bin sweep, start-row ablation, new bank or acquisition run follows. A positional
success merits a priced acquisition plan; failure merits reconsidering the already
bounded [fragment plan](learned-executable-fragments.md) or a specific contextual
acquisition mechanism. Neither automatically earns another experiment.

The position-factorized candidate is related to probability-vector models in
[Baluja, *Population-Based Incremental Learning* (1994)](https://www.ri.cmu.edu/pub_files/pub1/baluja_shumeet_1994_2/baluja_shumeet_1994_2.pdf).
This test evaluates a frozen representation, not PBIL's updating algorithm. The current
corpus line is related to [Salustowicz and Schmidhuber, *Probabilistic incremental program
evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/). These precedents motivate
the comparison; neither supplies evidence about this repository's tasks.
