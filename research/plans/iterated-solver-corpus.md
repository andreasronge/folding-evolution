# Can decoder fitting improve through its own discoveries?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md), chosen
by [strategy 1924](../runs/2026-10-07-1924/strategy.md). This is a direction and feasibility
plan, not an experiment registration. The steward supplies the full design.

The [first corpus study](../runs/2026-10-07-1707/analysis.md) established a transferable
gain from fitting previous-token context to exact G4 solvers. It did not test feedback:
the fitted maps were never used to generate a new fitting corpus. The next question is
whether that feedback yields further transferable improvement, reaches diminishing
returns, or reinforces a narrower set of solutions and damages search.

**What to build.** Extend the collector and fitter from commit `627336d`
(`experiments/chem_tape/solver_corpus_run.py` and its fitting helpers; inspect the research
branch/commit, since the current checkout does not contain that runner). Load the saved
first-round C tables with their corpus identities and hashes. Collect fresh exact training
solvers under each C and fit a second-round table C2. Retain the first-round independent
corpora as the lineage units; do not select parents by their reported speed.

Use the same full tapes, equal task weighting, G4 shrinkage prior, alpha 50 and support
rules as 1707. Fix the source-corpus treatment before evaluation: fit to new tapes only,
without pooling in the first corpus or changing the shrinkage prior to C. Otherwise data
volume or a changed regularizer could explain the apparent iteration benefit.

Include a fresh G4-generated corpus per lineage, with matched collection attempts and the
same fitting rule, producing a refreshed one-shot table. Evaluate C2, its parent C and
that refreshed fit on common fresh seeds. C2 versus C measures further progress; C2
versus the refreshed fit tests the consequence of collecting under C rather than G4.
Save failed attempts, yields and collection costs: equal attempts need not produce equal
numbers of exact tapes. The resulting comparison tests the source-decoder procedure,
including any yield change, rather than isolating tape quality at a fixed solver count.

Keep the frozen 1723 split, search harness and exact verifier. Only training cells enter
collection or fitting. Start evaluation populations from fresh latent genomes and transfer
only decoder tables. Retain corpus/lineage replication across both training families;
extra evaluation seeds under one parent do not replace independent lineages. A new
token-only fit is useful if affordable, but the primary question is feedback improvement,
not whether every second-round increment is specifically contextual. Without that control,
make no such attribution. Repeating K or the old M reference comparison is not necessary.

**First experiment and feasibility.** Probe collection yield and runtime under C, validate
exact solvers and fitted tables, then gate a fixed-size comparison in the same queue.
1707 collected 7,408/7,680 exact G4 solvers, with at least 40/48 per cell; its 81-minute
queue included 31 minutes of collection and 49 of evaluation. C was faster at evaluation,
but its collection cost and the new tables' cost must be measured. Price the additional
G4 collections explicitly. Do not assume the steward's approximately 80-minute estimate
already includes this control.

Use measured lineage-level precision and throughput to choose a comparison that can change
the decision within the remaining window. Target 75–90 queue minutes, reduced if
preparation consumes the reserve. Budget transfer to the three reused holdouts as part of
the question; admit any separate stage on time/feasibility under fixed rules, not a
favourable interim effect. If only feasibility fits, report that limit and preserve the
concept for the next run rather than turn a tiny comparison into a negative conclusion.

**What would count as an answer.** A resolved C2 advantage over both its parent and the
refreshed one-shot control, retained on withheld compositions, supports a useful second
feedback step. A training-only gain limits transfer. Parent improvement without a resolved
source-control contrast leaves the contribution of feedback unresolved. Tight bounds can
exclude a specified worthwhile increment for this step; they do not establish a universal
plateau. Degradation supports harmful feedback at this scope; broad intervals stay
unresolved. The steward should make these interpretations into non-overlapping rules.

Charge second-round collection separately and assess whether its savings over retaining C
could repay that extra cost. Any success is repeated external fitting on a reused screened
bank, not proof of family-specific bias, evolutionary decoder selection or simultaneous
map/program coevolution. One additional root-10 slot is allocated; no automatic third round.
