# Compositional map transfer

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md), opened
by the [2039 strategy](../runs/2026-10-05-2039/strategy.md). The steward should turn its
first question into a proposal with measured feasibility, sample size and outcome rules.
This is not an experiment registration.

The missing result is a map that retains useful information about a family after its
previous programs are discarded. Root 01's fitted frequencies already help constant
substitution, so neither another threshold nor evolving the INPUT/GT weights alone would
settle that gap. Test new operation combinations, against controls that can explain token
supply and generic syntax.

## What to build

Start with a small task bank and exact evaluator, using the existing chem-tape executor
and one fixed alphabet. A concrete first candidate is expressions combining two reducers
of a short signed integer list: `R1(X) + R2(X)` and `R1(X) > R2(X)`, with reducers drawn
from SUM, REDUCE_MAX and ANY. Signed inputs matter because positive-only lists make many
sum/max comparisons constant or nearly so. A finite domain such as length-four lists over
{-2,-1,0,1,2} has only 625 inputs and permits exhaustive behavioural checks. Verify the
executor on it; support and runtime are proposals to measure, not established facts.

Build a crossed training/holdout split: every primitive and constituent reducer is seen
in training, but at least two held-out reducer/combiner combinations are not. For example,
training can include same-reducer additions and cross-reducer comparisons, leaving mixed
additions out. This example is a candidate, not a frozen split. Exhaustively remove
constant, duplicate, commutatively equivalent and simpler-behaviour aliases; reject a split
if a training solver also solves its holdout or the distinction reduces to a changed
constant/slot. Compare to single-reducer shortcuts. Use canonical tapes only to verify
expressibility, never to seed search or train the adaptive map. Family definitions must
come from this task construction, not from which tasks the learned decoder later wins.

Once a suite is feasible, the smallest proposed structured map is a deterministic
context-dependent decoder from latent alleles to ordinary executor tokens. Each allele
selects a token through a categorical table; a small shared context, initially the previous
emitted token, selects the row. Independent rows tied together give the frequency-only
map. Untied, regularized rows can prefer operation sequences. Preserve token support,
fix token order and genotype length, and keep executor semantics identical across maps.
Start with a straight stack tape to avoid importing the shared-helper establishment
question. If this requires a different harness from TAG, measure its own baselines; do
not inherit TAG's reported speed-ups. This is a minimal sequential genotype-to-program
map, not a claim about folding or biological development.

Make the decoder parameters heritable in a small outer population. Select and mutate
them using performance of newly initialized inner program searches across training tasks.
No task identity, oracle labels, canonical solution, held-out score or previous solver
may enter decoding. Freeze each selected map for transfer, then initialize new latent
program populations. Keep latent initialization and mutation the same between decoder
arms. This cleanly tests adaptation of the map; it does not test simultaneous within-
population coevolution of decoder and program. An elite-frequency fit may help prototype
the interface, but must be labelled external fitting rather than evidence of map evolution.

Reuse the vectorized executor and search components where possible. Recent frequency-
bias experiments and `op_probs` support are on `research/main`, not all in the current
`main` checkout: inspect `family_bias.py`, `evolve_bias.py` and their run records on that
branch before extending them. Their intlist TAG screening helper is not automatically a
general evaluator for a new map. Verify decoder determinism, canonical semantics and the
independent-row special case before trusting new measurements.

## First experiments and allocation

1. **Task and runtime feasibility.** Measure random-start evolutionary discovery under a
   uniform map and a simple fixed relevant-token bias across the candidate bank, plus
   random sampling and exact verification. Establish whether multiple training tasks and
   at least two genuinely new combinations are tractable. Measure inner-search cost and
   the projected outer-loop cost before committing to nested adaptation. Fit-task progress
   need not wait for exact random-sampling hits; sparse sampling is not unreachability.
   Keep candidate selection separate from later evaluation, with fresh search seeds.
   Deliver the usable split, measured solve/time distributions, shortcut checks and an
   affordable next-stage design. If this bank fails, return to strategy with the specific
   bottleneck and a revised candidate bank rather than retrying rare thresholds.
2. **Adapt and transfer.** Run independent map-adaptation trajectories on the frozen
   training split and test their frozen decoders on fresh held-out searches. Compare with
   uniform, an independently fitted token map trained with comparable resources, and a
   simple fixed task-agnostic assembly bias. Include a context-removed version of each
   learned decoder with empirically matched emitted token marginals; marginal matching
   must be checked, not assumed from averaging conditional rows. Use a different-family
   training control with the same primitive support and adaptation budget to distinguish
   family information from generic syntax. Size this from experiment 1; if the full
   comparison does not fit, return for a narrower staged allocation before execution.
3. **Independent transfer replication.** If warranted, repeat adaptation from new map
   starts and test additional reserved operation combinations. This should settle whether
   any advantage survives a new learning trajectory and new task compositions, instead
   of adding inner-search seeds to one lucky decoder. For a broad unresolved effect,
   use this slot for a better-sized transfer comparison if that would change the decision.
4. **Explain the result that matters.** Use at most one targeted follow-up to distinguish
   the leading live explanations: e.g. sampling gain versus useful variation under
   selection, or family-specific assembly versus generic type correctness. Choose after
   the transfer result. If the prior slots answer the root, return this allocation; do
   not invent a mechanism sweep to spend it.

Four experiments are an initial allocation, not a ceiling on answering a promising
question. Every queue remains at most eight hours; budget substantial runs from measured
throughput and leave time for review within the roughly 48-hour autonomous window. A short
calibration can gate a larger stage within the same approved queue. Do not use an unstable
power estimate from a tiny pilot as evidence that no affordable experiment exists.

## What would count as an answer

The primary evidence is improved fresh-search performance on unseen compositions across
independently adapted maps, beyond the independent-token and simple fixed assembly
controls. The matched/mismatched training comparison determines whether to call that
family-specific. Count adaptation trajectories as independent evidence about learning;
many search seeds under one fitted map do not replace them. The steward should choose
one practical effect size and a 95% interval before the transfer run, with censoring and
an explicit unresolved outcome handled consistently.

Also measure held-out behaviour frequencies under the frozen maps, using the same
genotype prior, to connect the result to part 1 of the core question. Compare actual
random-search and evolutionary costs where affordable; do not infer mediation from
coincident sampling and search gains. Report adaptation cost separately and the number
of future tasks needed to amortize it. Transfer without net savings is still evidence
about learned bias, but not an efficiency win.

If only training improves, the tested map overfits. If independent token weights explain
the benefit, frequencies remain sufficient here. If fixed syntax or mismatched learning
explains it, the gain is generic. Sampling-only transfer answers a distribution question,
not evolutionary usefulness. Broad intervals remain unresolved; no-hits reports are
bounds. A feasibility failure rejects the tested task/map combination at its budget,
not the project's core hypothesis.
