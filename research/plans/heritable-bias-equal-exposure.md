# Inherited bias at equal evolutionary exposure

Concept-plan addendum for [root 23](../questions/23-heritable-variation-bias/question.md),
selected by [strategy 0843](../runs/2026-10-08-0843/strategy.md). It supersedes the immediate
acquisition/exposure and cost guidance in [the original plan](heritable-variation-bias.md).
This is a direction for the steward, not an experiment registration; the proposal supplies
the fixed size, primary decision rule and complete queue price.

**Question.** With equal opportunities for modifier mutation, does program-linked inheritance
acquire a frozen token distribution that improves fresh search over its uniform starting law?
Does breaking ancestry remove that benefit, and is the benefit competitive with the hand-set
scaffold? These are usefulness, linkage and practical-value questions, respectively.

The [2243 preparation](../runs/2026-10-07-2243/infeasible.md) produced no experiment result.
Its early stopping gave the less successful sum control three times as many generations.
Do not pool those acquisitions with the revised procedure. Its one-run observations cannot
choose winning families, modifier vectors or checkpoints.

**What to build.** Reuse `inherited_bias.py` and the reviewed TAG modifier path at `25f929e`;
inspect that commit/research branch rather than recreating the runner on `main`. Keep the
alphabet, token meanings, inherited recipient rule, bounded weights, support floor, modifier
noise, balanced training targets and final mean-probability extraction. Change acquisition
to a fixed number of reproduction generations per episode, independent of exact solving.
The steward's proposed 48 × 128 generations is a reasonable single candidate, not a runtime
measurement. Both arms must complete the same scheduled population evaluations and resets.
An incomplete acquisition is a stopped run, not an early extracted map.

Record the first exact solve without ending the episode or overwriting its first-hit record.
Continue ordinary program selection; no success-triggered reset, modifier freeze or special
selection reward. Repeated exhaustive verification after a first exact witness is unnecessary
for that episode's first-hit endpoint, but population evaluation and reproduction must continue.
Validate immediate solves, last-generation solves, no solves, shuffle/elite ordering, final
extraction, and identical scheduled counts. Preserve separate modifier randomness and the
existing replay checks for the unchanged legacy path.

Equal schedule removes differential stopping exposure; it does not equalize realized lineage
depth, selection intensity or drift. Keep those diagnostics. Continuing after solving also
includes maintenance selection, so the result concerns acquisition under fixed-duration
episodes, not pure selection for discovery speed. Low exact-solve yield on max does not prove
absence of selection on partial program fitness. Neither issue warrants a curriculum sweep.

**First experiment.** Retain both sum and max, with thresholds 1 and 5 for acquisition and
fresh training evaluation. Threshold 2 remains excluded. Use independently acquired
populations and shared fresh scoring seeds, retaining both sources of uncertainty and the
per-family results. Mean final probabilities, never resident tapes, enter frozen searches.
Uniform is the primary usefulness reference. Keep ancestry-broken and scaffold comparisons
as necessary interpretation controls, and the saved external fit as a reference if affordable.
Beating a degraded broken control alone cannot establish useful acquisition; beating uniform
without a resolved linkage contrast does not identify persistent inheritance as the cause.
Use capped search cost with solve counts, one worthwhile effect and 95% intervals; avoid
pooling a sum success into a max claim. Price a size that can change the continuation decision.

Measure the revised acquisition path, including generations after solving and verifier time.
The old measurements price scoring, not this acquisition law. Use roster-weighted mean costs,
realized worker utilization and an explicit tail/overhead allowance, rather than charging the
single worst search to every batch. A 2× allowance is a candidate to check, not a tail guarantee.
Separate saved acquisition from scoring so a timeout preserves completed work. Predefine any
staging without selecting maps or families by favourable interim effects.

**Cost and exit.** The steward's revised estimate is roughly one queue hour, about 2.5 hours
of timeouts, plus three hours of agent work. Allow 5–7 hours total for this first cycle,
including preparation, validation, review, analysis and contingency; target ≤3 queue hours.
The old two-experiment, 10–14-hour block remains the outer ceiling, not a reason to spend it.
Keep the 120-minute prepare limit. Return to strategy after this first result or any further
build/cost obstacle, before consuming the conditional second slot.

Useful acquisition and a credible remaining transfer/practical-value question can justify
frozen matched/mismatched evaluation on threshold 2. A tight small-effect bound or a clear
scaffold disadvantage ends this procedure's expansion; record any acquisition it did show.
An unresolved result needs a measured precision/cost calculation before extension, not an
automatic stop or more tuning. Both learned arms censored cannot identify a linkage difference,
although they can still show poor capped performance relative to solving fixed controls.
Report acquisition cost and measured savings in the same units; no savings means no break-even.

The mechanism remains self-adaptation of strategy parameters, as in
[Stephens et al., 1998](https://pubmed.ncbi.nlm.nih.gov/9847423/) (1997 preprint), applied here
to token generation and frozen reuse across tasks. It does not change token meanings or learn
decoder context. No capture, synonyms, new bank or modifier-parameter sweep is included.
