# Can unfinished searches improve their own decoder-acquisition signal?

Concept-plan addendum for [root 10](../questions/10-compositional-map-transfer/question.md),
chosen by [strategy 2116](../runs/2026-10-08-2116/strategy.md). It advances the conditional
stage in [partial-program context](partial-program-context.md). This is an implementation
direction, not an experiment registration; the steward fixes sizes and outcome rules.

**Question.** At matched total acquisition effort, does bounded feedback from non-solving
program populations produce a more useful frozen decoder than one-shot collection under
G4? Does it improve beyond retaining the first partial fit? The result chooses an
acquisition procedure. Closing the entire gap to exact-solver fitting is not required.

[1831](../runs/2026-10-08-1831/analysis.md) established a partial-corpus C/T advantage on
training cells, 1.28× [1.12, 1.45], with C/G4 1.62×. It did not demonstrate feedback or
equal-cost superiority to exact-solver acquisition. The source-cost ratio was corrected to
7.9× in the [decision](../runs/2026-10-08-1831/decision.md). Keep that distinction when
comparing acquisition efficiency. The closest technique is
[Salustowicz and Schmidhuber's PIPE (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/):
distribution updates informed by program search. This is external statistical fitting,
not inheritance or selection among competing map genotypes.

**What to build.** Extend the reviewed partial collector and solver-corpus fitter at
`998a9fe` on `research/main`; use the prior feedback runner as orchestration reference.
Preserve the comparison-gate training split, D1331 length-three inputs, `v2_rmin_first`,
G4, P 256, tape length 32, executor, support and exact checks. Run separately on BE and
PA, retaining both. Update the table only between short collection batches and reset all
program populations. Freeze the final tables for scoring on fresh program searches.
No resident genotype needs reinterpretation and no Rust decoder rewrite is expected.

Use a small, fixed number of batches; a first fit followed by two updates is a candidate
to price, not a commitment to a learning curve sweep. Preserve the full-tape estimator,
G4 shrinkage prior and α 50. The proposal must fix whether each update uses the new batch
alone or accumulated counts, including task/source weights and normalized fitting mass,
so extra data cannot silently change regularization strength. Do not select the best
round using final-evaluation scores. Save every lineage's intermediate tables and costs.

**Comparisons that give feedback meaning.** The main comparison is final contextual
feedback against a contextual one-shot fit collected under unchanged G4 with the same
total source-evaluation allocation. The one-shot arm pools its allotted acquisition data
and fits once. Retaining the first contextual fit is a separate, lower-cost baseline;
it cannot stand in for this equal-effort comparator. Include an independently updating
token-only lineage at comparable source effort. Fitting T to C's later corpus alone
would repeat question 22's limitation: it does not test token-only feedback.

Retain G4 as an absolute-usefulness reference. The saved exact-solver fits are an optional
ceiling reference if cheap; their unequal acquisition cost prevents an efficiency verdict.
Prioritize the feedback/one-shot and retained-first comparisons over a large diagnostic
matrix. The S collector preserves continuity with 1831's primary result. Switching to P
is a possible simplification, but must be fixed before confirmation and labelled a changed
collector: C_S/C_P being unresolved is not proof of equality. Do not run another S/P sweep.

**The main implementation risk is informative loss of source tapes.** Better source maps
may solve before the collection checkpoints. Fix checkpoint, budget, restart and empty-cell
handling before the main run. Only tapes archived before a source's first exact-solve
generation may enter a partial corpus; later success must not retroactively exclude
earlier tapes. Solvers and their descendants cannot enter. A deterministic resource-based
restart schedule can use unused acquisition effort, but it must apply consistently across
arms, count every attempt, and never continue until a favourable tape quota is reached.
Keep horizons short rather than lengthening them to recover solver-like performance.

Measure actual source evaluations as well as their allocated ceiling: first-solve stopping
makes equal attempt counts unequal effort. If exact matching is impractical, the proposal
must state the resource policy and narrow the claim to equal allocation, not pretend actual
costs match. Count verification, collection and fitting time too. Empty sources or cells
remain visible; use a pre-stated fallback or feasibility exit, never drop poor lineages.
Changes to checkpoints after calibration require a newly frozen procedure and independent
confirmation. Instrumentation must preserve search randomness and legacy replay.

**First experiment and cost.** Combine a bounded training-only timing/yield calibration
with a substantive independently replicated comparison where affordable. Independent
acquisition lineages are the units; batches, tapes and scoring seeds are not independent
learning replicates. Use common fresh scoring seeds within comparisons and report each
family and cell. Choose one practical feedback-versus-one-shot cost effect, a 95% interval,
and an explicit unresolved outcome. Check solve counts and sensitivity to the unsolved
penalty, because much of the first-stage C/T gain was in within-cap reliability.
Without a validated emitted-frequency control, report fitting-procedure comparisons,
not an isolated causal effect of token order.

The measured anchor is 1831: 2,048 short source searches plus 5,120 five-arm evaluation
searches completed in 120 minutes; preparation's projection was about 9 minutes of
collection and 133 minutes of scoring. Extra collection may be relatively cheap, but
feedback-table scoring, starvation and between-lineage variance are unmeasured.
Price the full roster at the intended worker count before admission, including failed
sources, fitting, exact verification and reporting. Allow **8–12 h total**, of which at
most **6 h is summed queue timeouts**, with preparation capped at 120 minutes. One existing
root-10 slot is allocated; no automatic second stage. A probe alone must obey the separate
60-minute probe timeout rule and return for review.

**Answers and exit.** A useful gain over equal-effort one-shot and over the first fit
supports feedback as an acquisition procedure; compare the token lineage before arguing
that contextual updating is worth its added machinery. Improvement over the first fit
alone can be explained by additional data. A bounded small feedback increment favours
one-shot acquisition at this effort. Degradation can reflect reinforced shortcuts or
source starvation, but neither cause is isolated without an intervention. Broad intervals
remain unresolved and need a priced resolution before more work. Report the extra
acquisition cost and how many future searches would repay measured savings.

Return to strategy after this result or an earlier build/cost failure. Success earns
consideration of generalization, not more automatic rounds. This stage scores training
cells only. Both comparison-gate and then-addition are now development banks; a later
fresh-bank transfer claim requires a separately frozen bank and method. No result here
establishes family specificity or evolutionary inheritance of the decoder.
