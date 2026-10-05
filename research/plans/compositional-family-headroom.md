# Assembly families with headroom

Concept-plan addendum to [compositional map transfer](compositional-map-transfer.md),
following [strategy 0001](../runs/2026-10-06-0001/strategy.md). It replaces the failed
first-bank candidate, not the root's transfer question. This is not an experiment
registration; the steward supplies measured feasibility and outcome rules.

The target is family information about assembly beyond token frequencies. Keep the
reviewed latent-allele decoder, straight stack executor and fresh-population search.
The implementation is on `research/main` (`composition_bank.py`, `composition_search.py`,
`composition_run.py`, `composition_report.py`), with the completed study at `0995d33`.
Inspect and reuse it rather than duplicating a harness in the current checkout.

**Candidate bank.** Start on the existing 625 signed-list inputs and `v2_rmin` alphabet.
Compare two expression families using the same reducers, ADD and IF_GT, with addition
in different structural positions. Concrete candidates, with A/B/C/D denoting reducer
outputs from SUM, MAX and MIN, are:

- Gate-addition: `(A+B)>0 ? C : D`.
- Branch-addition: `A>0 ? (B+C) : D`.

Both use four reducer occurrences, one ADD and one IF_GT; choose assignments that balance
primitive counts across families and training splits. Their natural postfix assemblies
place ADD next to different continuations, offering a candidate previous-token contrast.
This is a hypothesis about the decoder, not a property established by writing canonical
programs: alternate equivalent programs may erase that contrast. Repeated reducers,
commutativity, conditional identities and the finite domain can also erase task differences.
No candidate's search rate or non-alias status is yet known.

Build a small balanced roster and check canonical semantics against the actual executor.
Require active, nonconstant gates and branches whose contribution changes outputs.
Remove exact aliases within/across families and screen simpler behaviours, including the
old bank, single reducers and collapsed conditionals. Hold out reducer/role combinations,
with all constituent primitives and structural operations represented in training, and
at least two distinct held-out behaviours per family. Reject splits where a training
solver solves a holdout or where the distinction is only a constant substitution. Reserve
additional combinations for replication. Freeze the roster and selection rules before
the measured screen; do not select tasks by a later learned decoder's advantage.

The old exhaustive enumerator is verified only through six tokens. Reuse its results as
a bounded screen, not a proof that longer candidates lack shorter aliases. Calibrate any
deeper enumeration before committing to it; report exactly what it covers. Inspect
discovered solutions for shorter routes. If stronger screening is too expensive, narrow
the candidate bank or the resulting claim rather than calling a partial search exhaustive.

**Control choice.** Retain the exact frozen G table from 2247 and its measured marginal
control as benchmarks. G is a bank-informed prior, not a bank-blind grammar. It must remain
in the later comparison even if an additional type-based generic control is built; specify
such a control from executor semantics before measuring the new bank. A previous-token
row cannot in general guarantee a type-valid stack. Keep token support and execution
semantics identical, and never retune G after seeing candidate outcomes.

**First experiment.** Under question 12, combine a short semantic/runtime calibration
with a gated, adequately sized feasibility stage. Measure exact fresh-start solves under
uniform, token bias and frozen G, with sampling as supporting evidence. Test whether the
family distinction is usable by the proposed contextual map: a limited, explicitly
hand-set family-grammar positive control, compared with its swapped-family and empirical
marginal versions, can establish room in that decoder class before building the outer
loop. Construct those controls from the family rules before outcome inspection; they are
diagnostic priors, not learned maps or transfer evidence. Do not seed search with canonical
solutions. If even that diagnostic has no useful family contrast, simply adding length is
unlikely to justify decoder evolution.

Keep the previous 4,096-evaluation headroom benchmark visible; do not lower it to rescue
the old bank. Also report whether a worthwhile improvement could be measured against the
strongest fixed comparator, given population size and censoring. Estimate the full cost
of independent outer trajectories, training searches, both transfer directions, fitted
token controls, marginal controls and held-out evaluation. Use fresh seeds for the later
transfer study. Uniform need not produce abundant random exact hits, but inner evolutionary
discovery must be measured; unresolved sampling rates are bounds.

**What permits adaptation next.** A surviving split, affordable training searches, genuine
headroom against G and a usable family contrast justify the original plan's map-evolution
stage. Only decoder parameters transfer; new program populations start from scratch.
Use equally funded matched/mismatched training and independent token adaptation, plus
each learned decoder's empirically matched marginals. Independent adaptation trajectories
are the unit of evidence about learning. Report fitting cost separately from transfer
benefit. Matching G would show acquisition of a supplied prior, but would not establish
improvement beyond fixed assembly; matched and mismatched gains alike support generic
learning, not family specificity.

If this bank fails, record whether semantics, tractability, headroom, context capacity or
outer-loop cost failed and return to strategy. A deeper version of the old bank remains
a candidate, but must explain what new family contrast it introduces. Do not infer that
no feasible learned map exists from one unsuccessful bank or a finite no-hit sample.
