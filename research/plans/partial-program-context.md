# Can unfinished searches teach a useful decoder?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md), chosen
by [strategy 1831](../runs/2026-10-08-1831/strategy.md). This is a direction and cost plan;
the steward supplies the proposal, fixed sizes and primary decision rule.

**Question.** Can non-solving programs selected during short training searches teach a
decoder that improves fresh search beyond token fitting? Or does the useful signal in
the exact-solver corpora appear only after successful assembly?

The existing positive result starts with complete solutions. The failed outer learners
instead tried to rank decoder mutations by noisy search costs. A third signal is the
distribution of promising but incomplete programs. It could expose useful assembly
preferences earlier and more cheaply, or reinforce the training-perfect shortcuts already
seen in this system. Neither possibility is established by the exact-solver result.

The closest literature is [Salustowicz and Schmidhuber, PIPE (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/),
which updates a program distribution using the current best program, and
[McPhee and Poli, N-gram GP (2008)](https://drops.dagstuhl.de/entities/document/10.4230/DagSemProc.08051.5),
which uses an estimation-of-distribution update for instruction triplets. The proposed
previous-token estimator is different, and the question here is frozen reuse across
compositions. This is selection-informed **external fitting**, potentially a component
of an EDA. It is not per-individual inheritance or selection among competing decoder
genotypes. Moving the fitting call inside a search loop would not change that distinction.

**Build and reuse.** Use `research/main`'s reviewed `composition_search.py`,
`solver_corpus_fit.py`, and the comparison-gate bank and frozen artifacts introduced in
`5dd86bd`; the current main checkout lacks these experiment runners. Keep D1331
(length-three lists), `v2_rmin_first`, G4, tape length 32, P 256, operators, training cases
and exact verification. Train on the same four BE or four PA cells as 1246, separately
by family. No new bank, alphabet, canonical-program training or executor change is needed.

Add bounded collection of decoded non-solving tapes and their provenance to short G4
searches. The existing loop already verifies training-perfect candidates before reproduction,
stops on its first exact solver, and records lexicase parent indices. Collect only material
before that first exact-solve generation; neither its solver nor descendants may enter the
corpus. Fix the collection cap, checkpoint/sampling rule and contribution per source search
before confirmation. Keep early-solving and empty attempts in the manifest and cost; no
replenishing selected failures or silently dropping corpora. An explicit empty-cell rule
belongs in the proposal. Do not extend individual searches until enough attractive tapes appear.

Use actual lexicase-selected parent tapes as one source. At the same recorded population
and generation, draw a matched uniform sample as a control for the additional selection
weighting. Both sources have already experienced earlier selection: their contrast tests
parent enrichment, not all selection versus neutral evolution. Separate instrumentation
randomness so collection cannot alter the search. Preserve the legacy runner and check replay,
source timestamps, exclusion of exact programs, deterministic hashes and task separation.

Reuse the full-tape C and G4-based token-multiplier T estimators, support floor and alpha 50.
Generalize the count interface explicitly: partial tapes must not be marked `solved` to
pass the existing solver-only validator. Weight source searches and tasks consistently;
many copies or checkpoints from one population are not independent learning replicates.
Record duplicate rate, effective source count and collection effort. Do not add active-token
pruning, new shrinkage settings or a representation sweep to this first test.

**First experiment.** Compare frozen partial-corpus C and T on independent fresh searches
of their training cells, with G4 for absolute usefulness and the uniform-within-population
context fit for interpreting parent enrichment. Independent collections, balanced across
BE and PA, are the learning units. Exact-solver C from 1246 is a useful, labelled historical
reference; a small re-score can provide a positive control, but its old acquisition cost
and different corpus source prevent calling it an equal-cost comparison.

Choose one primary C/T cost contrast with a worthwhile effect, a 95% interval and an
unresolved outcome. Report G4 improvement, solve rates and per-family results alongside
it: beating a degraded T alone is not useful acquisition. A parent-enrichment null would
leave open useful information in the evolved population as a whole. C/T does not match
emitted frequencies; without scoring a validated K control, describe a fitting-procedure
advantage rather than an isolated effect of token order.

Combine a bounded training-only calibration with independent confirmation if it fits.
Price collection, verification, fitting, every evaluation arm and analysis. Calibrate
partial-corpus variability rather than importing the exact-corpus effect or precision.
A tiny unresolved pilot is not a negative answer. If only a probe is affordable, use
`kind: probe`, fixed seeds, descriptive output and the 60-minute timeout-sum limit.

**Cost and continuation.** One existing root-10 slot is allocated now: **6–8 h total**,
including up to **4 h of queue timeouts**, the 120-minute preparation allowance, review,
analysis and contingency. These are planning allowances, not measured partial-collector
rates. For anchors, 1246 collected 3,072 full-cap attempts in about 80 minutes and scored
2,304 training searches in about 39 minutes; 1548's 4,352-search fresh-bank row took
70 minutes. Partial collection should shorten evolution, but archive verification and
possibly poor fitted maps must be measured at the intended worker count.

Return to strategy after this first stage or an earlier build/cost obstacle. A useful
partial-context signal would justify considering one batched feedback study: update maps
between short training episodes, reset program populations, compare contextual and token
updates at equal acquisition effort, then freeze maps for independent scoring. Compare
with retaining the first fit so feedback must earn its cost. No table changes on resident
alleles are needed. Budget provisionally another **8–12 h**, or **14–20 h total** for
signal plus feedback/generalization, including agents. This continuation is not allocated.

The comparison-gate holdouts and then-addition bank are now development data. Excluding
them from fitting permits a mechanism check on reused compositions, not a fresh-bank
transfer claim. A genuinely fresh transfer study needs a separately frozen bank and method;
it is not a prerequisite for answering the first training-signal question.

**Answers and stopping.** Useful frozen C performance beyond T supports contextual fitting
from incomplete search material under this collector. A comparable population-sample fit
would make extra parent enrichment unnecessary at the measured resolution. Improvement
only in resident training populations does not count as frozen usefulness. A tight small
or harmful effect limits this one early-data procedure; a broad interval needs a priced
resolution. Do not respond automatically by increasing the horizon until exact-solver
fitting has been recreated. Fund feedback only if the first result makes its scientific
value and complete cost credible. Even a positive leaves endogenous inherited map
evolution and family specificity open.
