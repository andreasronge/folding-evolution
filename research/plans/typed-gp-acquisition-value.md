# Does acquired tape bias pay beyond a generic structural prior?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 2214](../runs/2026-10-10-2214/strategy.md). This is an
implementation direction and cost envelope, not an experiment registration.
The steward supplies the fixed design, sample size and primary decision rule.

**Question.** Does the complete, frozen A8 procedure retain a useful search-cost
advantage over task-agnostic typed subtree GP on the existing independent-input
families, and at what reuse horizon does that advantage repay acquisition?
This is a comparison of complete search procedures. It does not isolate a causal
effect of learning while holding representation and variation fixed.

The component study [2001](../runs/2026-10-10-2001/decision.md) establishes that
both learned objects are useful. Another component control would mostly refine
that answer. G4 is weak on DG; outperforming it by 6–10× does not establish a
competitive synthesis procedure. A generic tree representation supplies valid
expression structure and exchanges complete subexpressions without a learned
table or library. If that suffices here, the next learning target should be an
increment beyond this structural prior, rather than further repair of G4.

The precedent is [Montana, *Strongly Typed Genetic Programming*
(1995)](https://davidmontana.net/papers/stgp.pdf): type constraints restrict
construction to appropriate function arguments. The proposed baseline is a
small typed subtree implementation, not a reproduction of all of Montana's
generic-type machinery. Its performance in this repository is unmeasured.

**Build only the missing representation and operators.** Reuse reviewed
`research/main` code (latest experiment `6dabda8`), especially
`composition_search.py`, `independent_input_bank.py`, `family_preference_run.py`
and the component runner/artifacts from 2001. The current `main` checkout lacks
these runners. Source inspection confirms the Rust batch executor, exact D625
verification, lexicase implementation and frozen cohorts exist; no tree-GP
runner was found. Do not recreate the executor or port the entire experiment
suite. A small direct implementation or a conventional library is acceptable;
check dependencies before promising a library-based build.

Construct typed expression trees from the executor's function signatures,
with an integer output, list input/readouts, existing integer constants,
arithmetic, comparison and conditional operations. Types must follow VM
semantics: GT produces an integer 0/1 and IF_GT tests positivity, so do not
restrict the conditional to a special Boolean-only predicate type that quietly
supplies the target skeleton. Permit arbitrary compositions and repeated
operations within the size bound, including nested conditionals. No DG/TS
shape productions, role assignments, canonical templates, source-solver
fragments, fitted frequencies or family-specific parameter settings.

Compile trees to ordinary postfix tokens and use the same production evaluator.
An indexed readout that compiles to INPUT plus Xi costs two primitive tokens,
not one free terminal. Count all compiled tokens toward the existing 32-token
limit; padding for batching does not create extra effective program capacity.
Preserve each primitive's argument order, constants, overflow and conditional
semantics. Make the grammar/VM correspondence explicit before scoring. Trees
need not reproduce every stack manipulation or default/underflow program:
identify omissions such as DUP/SWAP, inert aliases and malformed tapes, verify
that all roster targets are expressible, and describe a representation
comparison rather than claiming identical search spaces or identical priors.
Do not add task-specific superinstructions to compensate for omissions.

Use conventional type-compatible subtree crossover and mutation, bounded tree
initialization, and an explicit size-limit/rejection policy. Reuse population
size, lexicase case selection, fitness and the exact-solve criterion where
applicable. Keep ordinary randomness streams separate from case draws. No need
for identical initial programs across representations. A bounded choice among
standard initialization settings on source/development cells is acceptable if
necessary; freeze the choice and charge that calibration before final scoring.
Do not search an operator grid until tree GP wins or tune against the target
rosters. A8 remains unchanged.

Validate generated and mutated trees against an independent interpreter and
Python/Rust execution, including noncanonical/random expressions. Check
conditional argument order, type closure, size rejection, exact verification,
evaluation accounting and reproducibility. Canonicals are validation fixtures
only. Simple known expressible tasks can detect a broken search path; solving
fixtures alone is not evidence of competitive performance.

**One substantive comparison.** Use the full eight DG and eight TS target
rosters from 1717/2001, all now development data, with fresh search seeds.
Compare each family's native A8 cohort with the same family-blind tree-GP
procedure. Retain every one of the 24 builds per cohort. Do not select the best
DG build, choose a different winner on each target, or replace the whole
cohort with its mean table. Include a modest contemporaneous G4 reference to
show the baseline's place relative to the old prior; avoid another six-arm
component matrix. Saved A8 rows may reduce execution only if exact pairing,
provenance and replay are recovered; the price should initially include fresh
references and comparable timing.

DG is the primary scope because the present practical claim is largest there.
TS is a mandatory separate boundary reading, not a pooled opportunity to hide
a reversal. The steward should choose one material A8/tree-GP cost contrast
and fixed size that can distinguish a useful gain from a bounded small gain
or loss. About 1.5× is a planning resolution, not a promised effect. Use a 95%
interval, show solve fractions and per-cell results, and retain the one-cap
versus two-cap sensitivity. Unresolved is a valid answer, with a resolution
price. Near-complete solving does not make search costs equal.

Keep acquisition-build uncertainty and scoring-seed uncertainty distinct. The
tree baseline has no acquisition replicates: a shared baseline row must not
be counted 24 times as independent evidence. Pair case draws when possible,
but do not pretend random choices in different representations have identical
meaning. A cost comparison at equal evaluated-program caps is useful and
imperfect; record compiled lengths, primitive work and actual time as well.

**Acquisition and economic interpretation.** Report arithmetic cost curves
`A + N*S` in evaluations and separately in comparable worker time. Charge a
deployed A8 build its entire acquisition, failures, intermediate/final fits
and extraction once, even though those artifacts are saved for this study.
Tree GP has no learned acquisition; disclose any baseline configuration
search separately as research/development cost, just as historical A8 method
development is separate from each build's acquisition. Do not infer wall-time
savings from evaluation ratios, omit tree construction/compilation, or compare
an uncontended replay with a loaded queue. No assumed owner reuse horizon.
Negative mean savings imply no demonstrated repayment. Capped costs and
reliability do not estimate unlimited time to first solve.

**Full price and admission.** Allocate one root-10 experiment through the next
strategy review. Expected complete time **7–10 hours**, including up to two
hours implementation/validation, roughly 2–4 queue hours, proposal, reviews,
analysis and contingency. Preparation remains at most **120 minutes**; summed
queue timeouts at most **4 hours**. These are provisional allowances, not
measured tree-GP rates. Keep the complete answer inside the current deadline,
2026-10-12T14:19:15 Europe/Stockholm, with analysis time reserved.

The measured anchor is 2001: 4,608 searches in about 89 queue minutes;
native DG A8 averaged 11.7 worker-seconds/search and native TS A8 about 3–4.
Tree construction, compile throughput, bloat rejection and failed searches
are unknown. Time representative source/development batches at sustained
concurrency (at least 64 jobs or comparable batches), including full-cap tails,
before fixing the final size. Historical A8 variation can size its side of the
comparison, not guarantee the baseline's variance. No standalone probe is
currently available (one probe plus three full experiments have run). Use
bounded prerequisites within a substantive proposal; do not relabel a pure
timing study as a full experiment. A failed prerequisite returns to strategy.

**Answer and exit.** A8 beating this validated structural comparator, with
useful reliability and a credible repayment range, earns consideration of a
fresh-bank comparison with both methods frozen. Tree GP matching or beating
A8 would show that supplied structure can be competitive with this acquired
tape procedure; it would not erase the previous acquisition and family
effects, or prove that learning cannot improve tree search. A8 winning against
an ineffective tree implementation cannot establish a strong-baseline claim.
Treat configuration limitations and representation restrictions explicitly.

Return after the result or a measured build, validity, precision or full-cost
obstruction. Do not automatically tune trees, extend the table/library
ablations, or launch PSB2. If the comparison changes which procedure should
carry forward, the next strategy should price its fresh-bank evaluation.
The old PSB2 plan tests a different, pre-reframe generalization hypothesis
and is not an executable continuation of this plan. Broader benchmark work
needs a current task-family split and interface plan; it is not permanently
conditional on A8 winning.
