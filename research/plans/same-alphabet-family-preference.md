# Does cheap acquisition learn a useful family preference on one alphabet?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 1717](../runs/2026-10-10-1717/strategy.md). This is a direction
and complete-cost envelope; the steward supplies the proposal, fixed size and
primary decision rule. It is not an experiment registration.

**Question and value.** Does training on different task families produce a useful
crossed preference on excluded compositions? A8's protected double-predicate
result establishes usefulness against G4, but its old-family comparator changed
token meanings. Earlier same-alphabet comparisons involved closely related output
families and left specificity unresolved. The next comparison keeps the executor,
alphabet, domain and acquisition recipe fixed. Its answer chooses between pursuing
family-specific acquisitions and a shared learned bias.

**One candidate contrast.** Use `v2_x4`, D625 and the existing double-predicate
family DG, `(A+B)>(C+D) ? E:F`. The candidate output family TS is
`A>B ? C+D:E+F`, with roles drawn from X0–X3 and all four readouts represented.
Both canonicals use six INPUT/readout pairs, two ADDs, GT and IF_GT: sixteen
tokens. This avoids the gross primitive-count difference of the one-addition
branch-else candidate. Where the semantic roster permits, balance aggregate
readout occurrences in the source rosters by a rule fixed before performance.
Keep the existing DG source roster. Matching actual evolved token counts is not
part of this test; family dependence may reside in frequencies as well as context
or fragments. Different output distributions prevent attributing a contrast solely
to ADD placement.

**Bounded bank work.** Reuse the reviewed `independent_input_bank.py`, `XMachine`,
`assembly_bank.screen_domain`, `independent_input_run.py`, `build_source` and the
fragment/search code on `research/main` (1536 code `7244fa1`). They are not all in
the current main checkout. Extend bank and source-roster interfaces, preserving
the old frozen-bank loader and replay. No new alphabet, executor or operator is
needed. Audit hardcoded source membership and padded-complete-solver exclusion.

Enumerate only TS; validate Python/Rust/reference canonical agreement, active
gates and branches, aliases and the existing real-token through-nine-token,
80%-agreement screen. Require a deterministic 4 source / 4 development / 8 target
split with multiple predicates and readout coverage. Check within-bank separation
and cross-family source/target aliases; do not admit targets already solved by a
source behaviour. Choose by semantics and deterministic ties, never fitted-map
performance. The screen does not certify sixteen-token minimality. Canonicals
validate labels, never supply learned counts, fragments or initial programs.

DG has eight unused cells in its frozen 24-cell clique after the 4/4/8 split.
Use those eight as the proposed DG target roster, after checking they were never
searched and remain excluded from every source. Preserve the old four development
cells for timing. If the spare roster or TS split is unsuitable, return the
specific obstruction; do not silently substitute scored targets, relax the screen
or sweep shapes/domains. Both rosters and the method must be frozen together before
target scoring. DG remains a development bank even with unscored reserved cells;
the two directions have different novelty and should be described separately.

**Acquisition and comparison.** Retain all 24 independent DG builds from 1536,
including weak builds and fallbacks, after hash/provenance and method checks. Their
selection is the complete existing cohort, not its favourable members. Build TS
artifacts independently using the unchanged four-G4-attempts, fit, four-adaptive-
attempts, pooled-refit recipe on four TS sources. No old-family token
reinterpretation. Keep support, normalized fitting mass, shrinkage, extractor,
library cap, insertion law, search cap and exact verification fixed. Equal
attempt allocations need not give equal solver yields or realized costs; retain
all failures and empty-source fallbacks. Development calibration builds are
separate from confirmation builds.

Score both families' frozen artifacts on both target rosters with fresh program
populations and common target seeds, alongside contemporaneous G4. Transfer only
tables/libraries. Retain build uncertainty and the repeated use of each build
across targets; neither cells nor search seeds are extra acquisitions. Old DG and
new TS builds are independent cohorts, not paired ancestors. Account for shared
baseline rows without counting them repeatedly. Reuse historical scores only if
the roster, pairing and exact replay actually match; the spare DG targets require
new scores.

The primary question is the training-family by target-family contrast in capped
search cost. Report each directional matched/mismatched ratio and each matched
arm's usefulness over G4: an aggregate interaction can conceal one bias winning
everywhere or one procedure merely harming the other family. The steward chooses
a worthwhile contrast and a fixed size that could change the choice between
family-specific and shared acquisition. Price a material preference, not the old
1.10× precision project. Solve fractions, per-cell costs and the one-cap penalty
sensitivity accompany the main interval. Capped effort is not uncapped solve time.
There is no token/context/library attribution or competitive-baseline claim here.

**Preparation, admission and full cost.** The standalone probe allowance is used
(0311 probe, 1536 full experiment). Propose a substantive crossed experiment with
bounded semantic and development-only calibration stages. Do not call a purely
descriptive bank run a full experiment to evade that rule. A failed prerequisite
returns to strategy without a transfer verdict.

After semantic checks, time both acquisition and matched/crossed search on the
development cells under representative concurrency; at least 64 jobs or sustained
collection batches avoid 0145's utilization error. Freeze the size before target
performance is opened. Admission concerns semantics, validity and an informative
complete price, not a favourable pilot interaction. Neither weak G4 nor sparse
first-batch discovery alone makes the crossed contrast uninformative. Conversely,
mostly capped fitted arms can make it uninformative even when code works.

Cost anchor: 1536 used **1,902 s** for validation plus 768 source searches/fits,
and **1,893 s** for 896 scoring searches, with about 9.8 effective workers. A
scenario with 24 builds per family, eight targets per family and two seeds per
build/target has 1,536 fitted searches plus 768 shared G4 searches. New TS
acquisition adds 768 attempts; existing DG acquisition need not be rerun. This
suggests roughly **2–3 queue hours**, allowing for slower crossed arms, but TS
screening, source yield and cross-family variability are unmeasured. Twenty-four
builds and two seeds are costing examples, not a justified final sample size.
Check the attainable uncertainty for the crossed contrast; the large G4/A8 effect
does not predict its size or precision.

Allocate **one root-10 experiment**, budget **32 → 33**, through the next strategy
review. Expected complete cost **6–9 hours**, including build, validation, timing,
acquisition, scoring, reviews, analysis and contingency. Preparation at most
120 minutes; summed queue timeouts at most four hours, reduced against the actual
2026-10-12T14:19:15 deadline. Reprice before admission if the design needs more
independent builds or new infrastructure. Do not dilute the substantive answer to
fit a nominal small queue.

Report arithmetic acquisition-plus-search curves, charging each deployed build's
whole acquisition once, including intermediate fitting, failures and extraction.
DG acquisition is sunk for executing this study but remains a deployment cost.
Report evaluations and measured time separately. Compare family-specific costs
without assuming an owner's reuse horizon or using geometric ratios to calculate
repayment. No saving means no demonstrated break-even.

**Answers and exit.** Useful reciprocal preferences would establish acquired
family dependence on these rosters, not inheritance or a pure assembly-order
mechanism. A one-directional preference is a narrower result. Tight small
contrasts with useful performance support investigating shared acquisition;
they do not establish universal family independence. One bias winning both
families suggests retaining it before paying for family specialization. Poor TS
acquisition bounds the recipe on that family rather than proving DG specificity.
Broad intervals require a priced resolution. Return to strategy after the result
or any admission obstruction; no automatic extra family, component matrix or
feedback round is funded.

The closest precedent for the current acquisition mechanism is
[Salustowicz and Schmidhuber, *Probabilistic incremental program evolution*
(1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/), found in this review's literature
search. This study tests frozen family-dependent reuse of external fits and
literal fragments; it does not implement PIPE or per-individual map inheritance.
