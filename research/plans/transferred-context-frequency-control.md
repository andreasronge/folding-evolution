# Does the transferred advantage survive matching emitted frequencies?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
selected by [strategy 0125](../runs/2026-10-09-0125/strategy.md). The steward supplies
the proposal, sample size and decision rule. This is not an experiment registration.

**Question and value.** Can a G4-based token-multiplier map matched to the contextual
decoder's emitted frequencies reproduce its search performance on then-addition-v1?
The 2.12× C/T result compares fitting procedures; their output frequencies differ.
We need to know whether pooled frequencies suffice before prioritizing another contextual
learner or a richer representation. This completes a mechanism comparison on a reused
bank, not a second fresh-bank transfer test.

**Reuse.** All 16 independent corpora in
`experiments/output/2026-10-08/2026-10-08-1246-comparison-gate-training/corpora.json`
already contain C, T and K. K retains G4's conditional template and tunes global token
multipliers to match C's pooled emitted frequencies. It is neither independent-token
sampling nor a new fit to evaluation results. Strategy recomputed the finite-length
Markov marginals: maximum absolute C–K error across all tokens/corpora is
`2.8970847247511422e-05`, below the original 0.001 tolerance.

Use the reviewed `solver_corpus_fit.py`, `composition_search.py`, source artifacts and
1548 evaluation machinery on `research/main` (1246 code `5dd86bd`, 1548 code `45b2bdb`).
Recover the frozen then-addition bank, input manifest, cases, schedules and C/T rows from
`experiments/output/2026-10-08/2026-10-08-1548-fresh-then-addition/`.
Verify hashes, support, table quantization and the marginal calculation before search.
No solver collection, new fitting rule, smoothing choice or task selection is needed.

**First experiment.** Score K on the same 16 cells and paired seeds as 1548's row F,
keeping all 16 corpora and both training-family labels. That is 2,048 additional searches
at the existing eight seeds per corpus/cell. Reuse C/T only after representative replay
checks recover their costs, cases and hashes. Pin code and RNG behavior; if replay fails,
return a priced correction rather than combine incompatible rows. This is a conditional
extension of the existing experiment, not independent replication of C/T.

Use one primary paired C/K capped-cost contrast with corpus-level uncertainty. Keep C/T
and K/T visible so a weak K cannot inflate the practical estimate of learned context.
Report solve counts, per-cell results and the one-cap sensitivity. A both-solved analysis
is selection-conditioned. Fix an informative practical bound and an unresolved outcome
before scoring K; failure to reject equality is insufficient to declare K adequate.
Check the expected precision against the saved C/T variability and measured K runtime.
The steward may choose a different fixed size if justified and within the same full cost;
do not top up opportunistically after looking at K's effect.

**Interpretation.** A worthwhile C advantage rules out this pooled-frequency-matched
G4 token map as a sufficient replacement on these cells. It leaves a concrete target for
contextual or fragment-based learning. If K reproduces C within a useful bound, prioritize
acquiring those frequencies with the simpler map before building a richer representation.
A broad interval returns to strategy with its resolution cost. A degraded K is informative
about sufficiency but C/K is not the fraction of the C/T gain caused by order.

Matching pooled frequencies under uniform latent initialization does not match positional
frequencies, exact-solver supply, selected-population frequencies or mutation neighborhoods.
C/K therefore does not isolate active program order, prove that long fragments are needed,
or explain cross-shape shrinkage. The tested K retains supplied context. Neither outcome
establishes family specificity or evolutionary acquisition of a decoder.

**Cost and exit.** Allocate one existing root-10 slot, **4–5 h total**, including preparation,
replay, review, queue, analysis and contingency. The latest decision estimates 40–60 queue
minutes for K, about 1.7 h if every search caps; these remain projections until K is timed
at the intended concurrency. Allow at most **3 h summed queue timeouts**, within the
120-minute preparation limit. Price all overhead before admission. Return to strategy
after the result or earlier on a validity/build/cost obstacle. No automatic additional
bank, feedback round, sampling census or decoder sweep follows.
