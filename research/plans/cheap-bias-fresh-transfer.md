# Does the cheap adaptive bias transfer when addition moves into the condition?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
allocated by [strategy 2303](../runs/2026-10-09-2303/strategy.md). The steward supplies
the proposal, fixed sample size and primary decision rule. This is not an experiment
registration.

The question is whether the frozen cheap adaptive pipeline A8 retains useful search
performance relative to the full-corpus pipeline on a fresh composition shape, including
its acquisition cost. [2033](../runs/2026-10-09-2033/analysis.md) makes this worth asking:
A8 approaches full F on then-addition at about a tenth of its acquisition evaluations,
but every evaluation of this acquisition policy has used development targets. A cheap
bias could specialize more strongly to those shapes than the larger corpus does.

**Transfer the existing acquisitions.** Reuse all sixteen corpus identities, both source
families and the four nested source blocks from 2033. Freeze A8 and S8 tables/libraries,
the full C+F reference from 1036, their construction rules, and the ordinary search
procedure before any new-bank search. Transfer these artifacts to fresh populations;
do not acquire or tune anything on the new targets. This tests fresh-target transfer of
the existing acquisitions. It does not replicate acquisition on a new training family.
New first batches and another 48-attempt source collection are unnecessary for this
question, although their historical costs remain charged in deployment comparisons.

**One candidate shape.** Retain D1331 (length-three lists over −5..5), the
`v2_rmin_first` alphabet and 32-token tapes. Let A–E range over SUM, MAX, MIN and FIRST,
using all four with one repeated occurrence. The candidate is:

`(A(X)+B(X)) > C(X) ? D(X) : E(X)`.

Its thirteen-token canonical has the same primitive inventory as the earlier
comparison-gate shapes, but ADD now constructs the predicate rather than an output
branch or the final output. This changes the required composition while keeping the
executor and supplied primitive support. It is a boundary test of reusable assembly
bias, not a factorial identification of the effect of ADD placement: output statistics,
shorter identities and difficulty can change too.

A [label-only preflight](../runs/2026-10-09-2303/gate-addition-preflight.json) enumerated
240 assignments: 216 have nonconstant gates and contributing branches, representing
120 distinct behaviours. Of these, 64 agree on fewer than 80% of D1331 inputs with
every behaviour in the saved comparison-gate and then-addition rosters. This uses all
220 and 86 saved behaviours, respectively, including excluded cells. It ran no search
and did not validate canonical execution or perform the short-program screen. Those
64 are candidates, not an admitted bank or evidence of headroom.

Reuse `then_addition_bank.py`, `comparison_gate_bank.py` and the bounded semantic
screen on `research/main`. Validate Python/Rust canonical agreement, active conditions
and branches, deduplication, and aliases against older banks. Apply the existing
through-nine-token exact/80%-agreement screen and the old-bank exclusion above;
retain its explicit limitation that thirteen-token minimality is unproved. Do not
relax the screen or change the domain to rescue this candidate. Canonicals and witnesses
are validation data only and cannot seed searches or supply learned fragments.

Select a multi-cell confirmation roster and a disjoint development/timing subset by
a deterministic semantic/hash rule before performance inspection. Aim for 8–16 distinct
confirmation behaviours spanning multiple predicates and repeated reducers, with a
fixed balanced selection if more survive. The proposal fixes the exact rule and minimum
coverage. Check behavioural separation from the timing subset too. Freeze the input
manifest, eligible/excluded rosters, selection rule, method artifacts and all hashes
together. No new shape sweep is included if this one fails.

**Bounded implementation and first experiment.** Reuse the reviewed
`sparse_feedback_run.py`, `sparse_feedback_report.py`, `fragment_reuse_run.py` and
`composition_search.py` on `research/main` (2033 code `e12edbf`). These runners are
absent from the current `main` experiment directory. Extend the target-bank interface,
not the decoder, fitter, library extractor or executor. Validate source provenance,
table/library hashes and historical replay; preserve the existing block rate, length
rules, suffix policy, fallbacks, support, cap, population size and exact verifier.

Score A8 and full F as the main retention comparison, with S8 to reveal any extra
specialization induced by adaptive collection, and G4 to establish absolute usefulness.
All four are scored on the new targets: old-bank performance is not a reference score
for this bank. Use common fresh cases/seeds and retain all acquisitions without
selecting winners. Different decoders need not give identical initial programs.

Keep the sixteen corpus units, four blocks nested within each and both source-family
labels. Full F and G4 rows shared by several comparisons are not extra independent
replicates. Report individual target results and solve rates as well as corpus-level
uncertainty; task generality is conditional on this frozen roster. A search cap gives
capped effort and solve probability, not expected uncapped time to solution.

The primary decision should distinguish material loss relative to full F from useful
retention. The earlier 20% tolerated cost increase is a reasonable resolution to price;
the steward must fix the actual margin and rule before confirmation. Do not make a
precise A8/S8 >1.10 verdict the admission target: 2033 already showed that resolving a
small increment can be dominated by between-corpus uncertainty. A8 resembling full F
when both fail or both lose to G4 is not a useful retention result. Keep explicit
branches for bounded loss, practical usefulness and unresolved comparisons.

Time only the disjoint development subset; no confirmation score may select targets,
maps, margins, methods or checkpoints. Fix confirmation size before opening its scores.
Use old-bank variability for an initial precision scenario and allow for changed-bank
spread. If confirmation cannot support a decision at measured rates, report the cost
obstacle. A tiny pilot that happens to run is not a substitute for this answer.

**Cost and interpretation.** Report acquisition plus repeated-search cost, A + N*S,
in arithmetic evaluations and separately in measured worker/wall time. Reuse the complete
source accounting, including failed attempts and intermediate/final fits; charge one
deployed build, not the aggregate cost of all scientific replicates. Keep hardware
calibration uncertainty visible. The old-bank evaluation and worker-time break-even
estimates differed substantially and cannot be transplanted to this bank. Show horizons
and uncertainty instead of assuming the owner's intended number of future tasks.

Useful retention beyond G4 would establish a second shape boundary for the cheap
externally acquired bias and support testing acquisition on new source families later.
A8 losing to full F where full F still helps would reveal a sparse/adaptive acquisition
limit. A8 losing to S8 would make adaptive specialization a candidate explanation,
without separating yield, content, decoder and library. All fitted procedures losing
their useful advantage would limit transfer more broadly. Wide intervals remain
unresolved. No result establishes family specificity, semantic modules, inherited map
evolution, or contextual effects isolated from token supply.

Allocate **one experiment, 5–7.5 hours total**, through the next strategy review.
Preparation at most **120 minutes**; summed queue timeouts at most **4 hours**,
reduced against the actual **2026-10-10T08:12:10** deadline to leave at least an hour
for analysis and decision. The total includes proposal, build, review, bank validation,
scoring, analysis and contingency; the maxima are ceilings, not simultaneous forecasts.

The measured anchor is 2033's 8,192 two-arm scoring searches in 83 minutes, plus eleven
minutes preparation/collection. A costing scenario of sixteen corpora × sixteen cells
× eight seeds gives 2,048 searches per fitted procedure: A8, S8 and full F together
give 6,144, plus a shared G4 roster. Eight seeds can cover the four source blocks equally.
This is roughly 1–2 hours at old-bank rates, not a promise for gate-addition or a prescribed
adequate size. Measure verifier tails, semantic screening and all four arms at intended
concurrency. Price the complete answer rather than a baseline screen followed by an
unfunded transfer stage.

Return to strategy after the result or an earlier semantic, build, precision or full-cost
obstacle. No new acquisitions, second feedback round, extra control matrix, or automatic
new bank follows. If only a descriptive probe is proposed it must obey the separate
60-minute timeout rule and justify a complete confirmation within the remaining time;
feasibility alone does not earn a cycle.

The fitting mechanism is related to [Salustowicz and Schmidhuber, *Probabilistic
incremental program evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/):
program search supplies information for updating a generating distribution. Our frozen
corpus fits and literal fragment edits differ from PIPE. The literature motivates the
mechanism; the repository's results motivate this transfer test.
