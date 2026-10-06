# A fourth reducer for a two-family transfer test

Concept-plan addendum for [root 10](../questions/10-compositional-map-transfer/question.md),
following [strategy 1400](../runs/2026-10-06-1400/strategy.md). This is a candidate design
for the steward to turn into a measured proposal, not an experiment registration.

The missing comparison is adaptation to two families with the same primitive inventory.
The three-reducer screen left only two branch-else cells, versus eight post-addition
cells. Four scalar roles built from three reducers necessarily repeat a reducer. A
fourth signed readout allows four distinct roles and may reduce condition reuse and
some near-aliases. It will not remove conditional algebraic identities, and it is not
known to produce a usable bank.

**What to build.** Extend the existing stack alphabet by one ordinary list-to-integer
primitive, FIRST: first element, zero for an empty list, with wrong-type/underflow
behaviour specified consistently with the executor. Use the existing integer-list domain
D1331 (all length-three lists over −5..5). Retain SUM, MAX and MIN. All decoder arms get
the same new alphabet and semantics; FIRST must not access task identity or labels.
Verify Python/Rust evaluator agreement and extend the semantic screen before measuring
search. Reuse the reviewed harness on `research/main`, especially `assembly_bank.py`,
`composition_bank.py` and `composition_search.py`; do not duplicate it on `main`.

Candidate families, where A/B/C/D are a permutation of SUM, MAX, MIN and FIRST:

- Branch-else: `A(X)>0 ? B(X) : (C(X)+D(X))`.
- Post-addition: `(A(X)>0 ? B(X) : C(X)) + D(X)`.

Enumerate these two shapes and the 24 assignments each, removing commutative duplicates.
Every canonical uses four INPUTs, each reducer once, one ADD and one IF_GT: ten tokens,
with exactly matched primitive counts across families. FIRST breaks permutation symmetry
of the input list and may weaken some correlations; neither benefit is assumed. This
is a new task/alphabet condition, not a replication on the old bank.

**First experiment.** Freeze this bounded candidate roster and the selection rules before
search. Check active gates, genuinely contributing branches, exact within/across-family
aliases and shorter-program near-aliases using the previous ≤9-token, 80%-agreement
screen where computationally feasible. Include zero-constant rewrites, condition reuse
and simpler reducers among the witnesses. Measure enumeration time early: adding a
primitive can greatly increase the state frontier. If exhaustive screening is unaffordable,
report a bounded screen and return for review; do not silently call it exhaustive or
relax the agreement threshold. No domain or primitive sweep is planned in this slot.

Look for at least four distinct surviving cells per family, with at least two reserved
compositions in each, all primitives present in training, and no training solver exactly
solving a holdout. Prefer more training cells and a reserved replication split if the
roster permits. Select splits by semantic rules and baseline feasibility, never learned
map performance. Canonical tapes verify expressibility; they do not seed populations
or train learned decoder parameters.

Extend G once by its existing reducer/scalar rules, before inspecting this bank, and
name the result G4. Document the new row/column masses and normalization. G4 is a new
fixed comparator, not the unchanged old G; old rates cannot be imported. Include uniform,
a fixed token bias and empirical context-free marginals. Retain the earlier 4,096-evaluation
headroom reference and measure actual solve/censoring curves and runtime. A hand-set
family grammar and its swapped-family control can diagnose whether this decoder class
can express a useful family contrast; they are diagnostic priors, never learned evidence.
Gate search after the semantic checks within the same queue when feasible. Sparse random
solver counts are bounds and should not consume most of the feasibility budget.

**If feasible.** Adapt maps independently to each family's frozen training cells with
matched compute, then evaluate both learned maps on both families' withheld compositions.
Transfer only decoder parameters; reset every program population. Keep G4-based token
multipliers as a successful, restricted learner alongside any contextual learner, plus
fixed and marginal controls. Test on fresh training seeds as well as holdouts. Calibrate
candidate-ranking reproducibility on training tasks; an aggregate 25% acceptance rate
alone is not a reliable gate for whether learning works. Use independent learning starts,
not extra continuations as their replacement. Measure the complete learning and evaluation
cost before committing a queue, and report adaptation cost separately from search savings.

**What counts as an answer.** A matched-over-mismatched advantage on held-out compositions
in both directions supports adaptation to these families. A contextual advantage beyond
the equally trained restricted learner addresses learned assembly preferences; family
specificity can also reside entirely in token weighting, which is a distinct answer.
Equal improvements across families support a generic component only to the interval's
resolution. Training gains without transfer indicate overfitting at the tested budget;
failure to improve training limits the adaptation procedure. Broad intervals stay
unresolved. A failed semantic, headroom, decoder-capacity or runtime check returns that
specific obstacle to strategy and rejects only this candidate. It neither requires
another alphabet expansion nor ends the autonomous program.
