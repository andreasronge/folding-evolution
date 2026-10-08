# Transfer on compositions with reducer-to-reducer conditions

Reserve concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
written by [strategy 1046](../runs/2026-10-08-1046/strategy.md). No experiment is allocated
yet. The steward should price it at the next review, after root 23's recovery. This is a
direction and implementation plan, not an experiment registration.

**Question.** Does solver-corpus context retain a useful advantage over token fitting on
new operation combinations, with several withheld behaviours in each of two task families?
Does the training family affect that advantage? The current bank's single branch-else
holdout cannot supply this evidence, however many seeds are added.

**Candidate and reason.** Retain the straight-stack `v2_rmin_first` alphabet, exact
executor and D1331 inputs. Change the condition from a reducer's sign to a comparison
between two reducers. Consider these two shapes, with A–E chosen from SUM, MAX, MIN and
FIRST, using all four reducers with exactly one repeated occurrence:

- Branch-else: `A(X)>B(X) ? C(X) : D(X)+E(X)`.
- Post-addition: `(A(X)>B(X) ? C(X) : D(X))+E(X)`.

These have matching primitive inventories for matched role assignments: five INPUTs,
five reducer occurrences, GT, ADD and IF_GT. They are new 13-token canonical compositions,
not new seeds or one extra target on the old bank. GT and IF_GT already exist; Python
inspection confirms GT returns an integer Boolean suitable for IF_GT's positive condition.
Validate their composition against Rust before search. Some reducer orderings are constant,
and shorter identities may survive; neither diversity nor tractability is assumed.
The hypothesis is that varying the comparison reduces the sign-condition restrictions
that eliminated most earlier branch-else cells. No new primitive or engine rewrite is needed.

**What to build.** Extend the reviewed bank generator and semantic checks on `research/main`
(`four_reducer_bank.py`, `composition_bank.py`), reusing the search and corpus-fit runners.
Enumerate this bounded roster and remove commutative duplicates, constant gates, inactive
branches, exact aliases within/across families, and behaviours identical to the old bank.
Check the existing short-program witnesses and condition reuse. A search through nine
tokens cannot certify minimality of a 13-token canonical; state that bound explicitly.
Measure any deeper enumeration before committing to it. Canonical programs verify targets
only; they never enter initialization or fitted corpora.

Construct balanced training splits with at least two distinct held-out behaviours per
family and reducer-role coverage in training. Match token occurrence counts between
families where the semantic roster allows it. Freeze a deterministic split rule and a
separate development subset before performance screening. If the semantic roster cannot
support these requirements, reject this candidate at that scope; do not silently return
to the one-holdout split or sweep domains and primitives.

**First experiment if funded.** Establish semantics and measured search feasibility on
the development subset, then price the complete transfer study. Retain G4 as a fixed,
bank-informed comparator without retuning it to the new canonical sequences. Use the
successful one-shot corpus fitting procedure: context C and restricted token multipliers
T fitted to identical independent corpora, with fixed full-tape treatment and shrinkage
from 1707. This is external fitting, related to
[Salustowicz and Schmidhuber's PIPE (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/),
not inheritance or selection of decoder parameters. No second feedback round is required
to answer the first transfer question.

Measure collection yield, capped search cost, task spread, fitted-table throughput and
remaining headroom over G4. Include failed collection attempts and slow verifier cases in
the price. The 81-minute old-bank corpus study is an implementation anchor, not a forecast
for these longer tasks. A feasibility probe, if chosen, obeys the 60-minute timeout cap
and reports observations only. Prefer a substantive development check in the first slot
when it can also resolve a meaningful comparison.

**Conditional transfer experiment.** Freeze the bank, split, fitting method, sample sizes
and scoring rules before any performance evaluation of the protected targets. Calibrate
only on development/training tasks. Fit independent corpora for each training family;
evaluate both families' C and T tables on all held-out tasks, plus G4 and fresh training
searches. Only decoder tables transfer; every program population starts anew. Retain
corpus uncertainty and individual task results. If attributing the gain specifically to
context, validate a matched-emitted-frequency control as in 1707.

No holdout score may select a map, a task, a smoothing value or a stopping point. If held-out
baseline results trigger a redesign, those targets become development data; new seeds do
not restore freshness. Semantic checks alone do not establish search headroom. Avoid
promising a symmetric positive result by selecting targets where fitted C happens to win.

**Answers and full cost.** A C/T advantage on multiple new targets supports broader
transfer of this fitting procedure. Matched-over-mismatched gains are a separate family
question and must accompany useful absolute performance, not only harm to the other
family. Generic contextual gains remain valuable. Training gains without held-out gains
limit transfer; tightly bounded small gains limit this method and bank; broad intervals
remain unresolved. Report fitting cost and whether measured savings repay it.

Provisional envelope: **4–6 hours total** for semantic/build/development work and review,
then **8–12 further hours** for replicated collection, transfer scoring and analysis:
**12–18 hours total**, roughly two substantive experiments, with every queue at most eight
hours. These are planning allowances, not measured rates or authorization. Before funding,
require a credible price for the complete answer within the remaining autonomous time,
including the 120-minute prepare limit per build. Review after feasibility before allocating
transfer. Failure of this candidate does not show that transferable assembly bias is absent;
it supplies a specific obstacle for the next cost/value decision.
