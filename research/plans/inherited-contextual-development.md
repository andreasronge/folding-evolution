# Inherited contextual development under changing goals

Concept plan for [root 62](../questions/62-inherited-contextual-development/question.md),
funded by [strategy 0533](../runs/2026-10-12-0533/strategy.md) in autonomous run
2026-10-12-2311. Four experiments, expected 20–28 hours complete, ceiling 32.
This is a direction, not a registration: the steward chooses experiments,
sizes, schedules and primary comparisons. Update this plan as evidence arrives.

The question is whether ordinary program selection can improve an inherited
developmental decoder, with benefit surviving removal of every resident
program. Roots 23 and 55 tested future-variation modifiers; direct developmental
change could offer stronger selection, but also stronger coadaptation and
disruption. No improvement is assumed.

**Mechanism and prior work.**
[Watson et al., *The evolution of phenotypic correlations and developmental
memory* (2014)](https://doi.org/10.1111/evo.12337) models evolving developmental
interactions whose direct phenotypic effects also alter subsequent variation.
[Parter, Kashtan and Alon, *Facilitated Variation* (2008)](https://doi.org/10.1371/journal.pcbi.1000206)
tests generalization under systematically changing goals in circuits and RNA.
Both were found in this strategy's literature search. Neither establishes that
this decoder's selection landscape supports learning. Our addition is a
separable inherited chem-tape decoder, scored after removing training genomes,
with exact verification and acquisition charged.

Selection sees only current program performance. The map and tape jointly
evolve; no task identifier, source canonical, fitted table or known helper
determines a map mutation. This is distinct from external distribution fitting,
outer selection using many searches per map, and choosing supplied libraries.

**Bounded build.** Reuse the reviewed `research/main` implementation rather
than the older `main` experiment directory:

- `experiments/chem_tape/composition_search.py` supplies latent alleles,
  cumulative conditional tables, inverse encoding and the Rust executor.
- `map_learning.py` and `contextual_learning.py` supply bounded table
  representations and support normalization, currently for global maps.
- `inherited_bias.py` supplies recipient-aligned inheritance and separate
  random streams, but its TAG probability interface is not a drop-in decoder.

Source inspection establishes these interfaces, not new-path throughput.
Build per-individual decoding and a persistent multi-goal runner. Avoid a full
allele-range lookup per individual per generation: cumulative row comparisons
or shared immutable tables can retain the primitive batch executor without a
Rust rewrite. Check exact agreement with `Decoder` for identical maps.

Use a small, position-independent previous-token table, initially the same
fixed generic grammar for everyone. Prefer bounded local emission-mass changes
in one row to free table replacement; keep a support floor, fixed primitive
meanings and existing tape capacity. A small cumulative-boundary move is one
concrete candidate. It can still change a decoded suffix: quantify that rather
than claiming phenotype neutrality. The steward fixes one representation and
mutation rule using correctness and development evidence, never protected
performance. No arbitrary semantic reassignment or complete-target lookup.

Inherit map state from a declared parent with the tape; copy elites without
aliasing mutable arrays. Keep map randomness separate. Map changes must affect
the child's resident decoding; merely sampling new mutation tokens repeats
root 23. Recompute decoded programs and fitness after map changes: allele-only
caching is invalid. Validate crossover, rejected edits, map/tape alignment,
checkpoint reload and zero-map-mutation replay. Track map diversity, mutation
displacement and resident fitness effects as diagnostics, not usefulness.

**Exposure and program-discarded readout.** Retain resident tapes across related
training-goal changes, with a predetermined balanced schedule and fixed total
effort; the steward chooses cadence. Log pre-solve and post-solve time and
verify repeated adaptation opportunities. A schedule whose goals are all solved
by the same programs cannot test the intended pressure. Do not use 55's
success-conditioned first-hit frequencies as an unconditional forecast or pick
a checkpoint retrospectively. A success-triggered schedule would be an explicit
changed procedure requiring accounting for unequal goal exposures and costs.

At the declared endpoint, discard tapes, solvers, caches and archives. Extract
map states by a fixed fitness-blind rule from each independently evolved
population and freeze them. Preassigned uniform endpoint samples are one
option; never choose the best map by readout performance. Score sampled maps
separately before averaging costs: averaging tables first deploys a different
learner. The acquisition population remains the unit of evidence.

Fresh uniform latent genomes test the map's whole reusable benefit, including
initialization bias. If attributing a gain specifically to ongoing variation,
use inverse encoding to supply identical initial token tapes under different
frozen maps. That decomposition is conditional; removal of saved programs is
required in every usefulness readout.

**First studies and answers.** A reasonable block includes an instrument and
development probe, independent frozen-usefulness assessment, protected transfer,
and whichever replication or mechanism contrast decides the remaining question.
The steward may combine checks with full studies or return unused allocation.
One standalone probe is currently available, at most 60 minutes of summed
timeouts; its observations require later confirmation.

Existing comparison-gate tasks are suitable development candidates, including
their spent former holdouts. First ask whether independently evolved frozen
maps improve fresh search over the unchanged generic decoder. Keep a fixed-map
evolving-program baseline during exposure and a mutation-only map control for
drift. A same-cost fixed-goal exposure comparison is needed to attribute gains
to changing goals rather than joint evolution; balance its fixed goals over
the training roster. Shuffling maps across tapes changes current phenotypes,
so it is not the neutral ancestry shuffle used in root 23.

An inherited token-only restriction is the natural comparator for claims that
new context contributes beyond frequencies. It can live inside this root;
there is no need to restart root 23 separately. Fixed hand grammar and external
context fits are practical references, never inherited initial states. Include
ordinary tree GP on matching semantics for any practical competitiveness
claim. Choose contrasts that answer the primary question; do not automatically
build a full factorial of every possible control.

Before transfer, freeze the complete method with a new bank of unseen
recombinations of the training family's operations. Check behaviours against
prior banks and training tasks. Canonicals validate expressibility; they never
seed search. Protected searches cannot tune methods, screen for favourable
performance or price runtime; a separate development roster serves those roles.
A new split of an old bank is excluded-from-acquisition reuse, not fresh-bank
transfer. Use existing generators and exact verification, without new primitives.

The main answer is lower capped arithmetic fresh-search cost on unseen goals
under frozen, independently evolved maps compared with the fixed generic map.
The steward states a worthwhile effect and fixed size, with a 95% interval,
exact solve rates and an unresolved outcome. Preserve acquisition and cell
variation; many readout seeds do not replace independent acquisitions. A
token-only contrast decides whether context was needed; fixed-goal controls
decide whether environmental variation helped. Narrow conclusions when a
contrast is absent. Faster resident adaptation alone is not portable learned
bias. Sampling changes alone do not demonstrate cheaper evolutionary search.

Charge all exposure, failed acquisitions and extraction to each deployed map.
Report evaluations and worker seconds, then arithmetic acquisition plus N fresh
searches. Repayment requires measured positive savings against the named
reference. A mechanism result can matter without immediate repayment, but
beating weak generic decoding is not superiority to tree GP or informed priors.

**Full price and exit.** Reserve 4–6 hours for implementation, validation and
the first development assessment, 6–8 for independently replicated frozen
usefulness and controls, and 10–14 for fresh-bank validation, transfer,
replication/interpretation and reviews: **20–28 hours total**, **32-hour ceiling**
including contingency. These are estimates. The old fixed-map comparison-gate
queue took 7,127 seconds ([1246](../runs/2026-10-08-1246/execution.md)); inherited
frequency acquisition/scoring took about 75 minutes
([1046](../runs/2026-10-08-1046/execution.md)). Neither measures the new path.
Replace allowances with sustained timing, including difficult maps, full
episodes, verification and acquisition-level uncertainty, before substantial
scoring. Execution feasibility alone does not justify the purchase.

Each prepare remains within 120 minutes. Split larger implementation into
reviewed stages; efficacy pilots count as experiments. Each substantive queue
stays within the configured eight-hour limit and leaves time for analysis.
Do not admit development work whose complete remaining answer cannot fit the
block and actual deadline, currently 2026-10-14 23:11:38 Europe/Stockholm.

Review after four cycles, or earlier if the complete remaining question no
longer justifies its cost. Useful independent map-only evidence supports
protected confirmation inside this allocation. Tight small effects, harmful
transfer, unusable mutations or resident-only benefits end this candidate's
expansion at its tested scope. Broad uncertainty needs a priced resolving
study that would change the decision. No automatic rate sweep, larger table,
folding/Rust port, corpus-fitting fallback or second root follows failure.
