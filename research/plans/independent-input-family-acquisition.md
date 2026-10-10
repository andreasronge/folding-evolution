# Can cheap acquisition learn a family beyond reducer/output syntax?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
from the [prior strategy 0311](../runs/2026-10-10-0311/strategy-prior-run.md).
**First stage allocated in autonomous run 2026-10-10-1419; transfer requires the
next strategy review.** No new root is needed. This is a direction and staged cost envelope, not an
experiment registration; the steward supplies the proposal and decision rules.

The question is whether the unchanged four-plus-four acquisition recipe can learn
a useful frozen bias from a structurally different family and help on excluded
members. All successful acquisitions so far used branch-else or post-addition
sources. New output targets and the complementary source roster support carrying
the recipe forward, but do not show that it learns different assembly requirements.

**Why a bank redesign is needed.** Moving addition into the predicate on D1331
already failed in [2303](../runs/2026-10-09-2303/semantic-probe.json). Strategy 0311
checked two bounded alternatives without running evolutionary searches:

- `(A+B)>C ? D:E` on the existing D2401 domain: seven behaviours survive the
  through-nine-token screen; at most six are mutually below 80% agreement.
- `(A+B)>(C+D) ? E:F` on D1331: eight survive both that screen and exclusion against
  all saved comparison-gate, then-addition and two-sum cells; at most four are
  mutually below 80% agreement.

The [split audit](../runs/2026-10-10-0311/semantic-split-audit.json) exhaustively
checks all subsets of each retained set. Neither supports the planned four-source,
four-holdout split. This rejects those candidates under that rule, not every
smaller split or every predicate task. The screen validates Python semantics only;
an experiment would still require the matching Rust validation. It says nothing
about evolutionary difficulty or useful acquisition.

**Candidate redesign.** Separate the scalar inputs instead of deriving SUM, MAX,
MIN and FIRST from the same list. Use a finite vector of four independently varied
integers, initially all length-four lists over −2..2 (625 inputs). Supply four
indexed scalar readouts X0–X3 in an explicitly separate alphabet. Keep the number
of scalar readout slots equal to the four-reducer alphabet; do not grow an
unbounded primitive set. Old alphabets and semantics must remain replayable.

Candidate families are output addition `A>B ? C:D+E` and composite predicates
`(A+B)>(C+D) ? E:F`, with roles drawn from X0–X3. The hypothesis is that removing
the order constraints among MIN, MAX and FIRST and their dependence on SUM will
leave more genuinely different predicates. This is a hypothesis about semantic
coverage, not evidence that new maps will learn or that all earlier aliases had
that cause. Choose one compound-predicate family for acquisition first; a crossed
family-specificity experiment is conditional later work.

**What to build.** Reuse `assembly_bank.py`, `four_reducer_bank.py`,
`composition_search.py`, `source_replication_run.py`, `solver_corpus_fit.py` and
`fragment_library.py` from `research/main` (`b6d1974` at this review). These runners
are absent from the current `main` checkout. Implement indexed readouts in Python,
Rust and the typed semantic machine, with explicit empty/short-input and wrong-type
rules. Validate every index, scalar/type behavior and legacy replay. A separate
alphabet must be named in all artifacts; do not silently reinterpret saved maps.

Construct the fixed generic G4 analogue by applying the existing INPUT/readout/
scalar rules to the new readout slots before inspecting search performance. Keep
the latent decoder, tape length, population, operators, fitting normalization,
shrinkage, library extractor and fallback rules fixed. Any necessary change to the
prior is supplied task-language knowledge, not learned bias, and must be reported.

Enumerate the bounded shapes, remove inactive gates/branches and duplicate outputs,
and use the existing exact/80%-agreement screen through nine tokens. Require four
source and at least four excluded target behaviours, pairwise separated under the
same rule, all readouts covered in sources and multiple predicates represented.
Freeze a deterministic semantic split with a separate timing subset before search.
Validate canonical programs and witnesses in both executors. Canonicals validate
expressibility and never supply fitted counts, libraries or initial programs.
The screen does not establish minimality of the longer canonical programs.

**First experiment and continuation.** First establish the new alphabet and bank,
then measure source discovery, verification cost and headroom under the fixed
prior on development cells. A feasibility probe has fixed seeds, descriptive
output and at most 60 minutes summed queue timeouts. Its deliverable is a usable
split and a price for the complete acquisition/transfer comparison. A failure
ends this candidate without weakening the screen or adding primitives. Do not
call successful code execution evidence of learned bias.

If the full comparison earns an allocation, run independent acquisitions from
four fresh prior searches per source cell, fit C4+F4, collect four more under each
build's own bias, and refit all eight attempts. Preserve failures and empty-cell
fallbacks. Transfer only frozen decoder/library artifacts into fresh populations
on the excluded targets. Compare against contemporaneous fixed-prior search;
do not rebuild the 48-attempt full pipeline merely to repeat the old retention test.
Freeze the procedure and protected target roster together before target scoring.
Calibration may change the scientific status of development cells, never quietly
restore them to protected status.

Use acquisition builds as uncertainty units and propagate shared-baseline seed
uncertainty. Choose a fixed sample size for a worthwhile capped-search-cost gain;
about 1.5× is a candidate resolution, not a promised effect. Retain solve counts,
per-target results and cap sensitivity. Both arms failing is not useful retention.
Charge all acquisition, failed attempts, fitting and extraction once per deployed
build, and report arithmetic acquisition-plus-search cost curves in evaluations.
Wall-time economics require measurements under comparable sustained load; 0145's
two-row historical calibration must not be reused.

Useful frozen improvement on excluded compositions would extend the external
recipe to this new family/alphabet. A tight small-effect or harmful result would
bound its portability; broad intervals require a resolution price. No result
isolates context from fragments, proves matched-family specificity or establishes
inherited map evolution. This remains related to
[Salustowicz and Schmidhuber, PIPE (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/):
search supplies data for updating a program distribution, with different fitting
and reuse rules here.

**Full cost and exit.** Plan **3–4 hours** for alphabet/bank implementation,
validation, development timing and review, then **4–6 hours** for independently
replicated acquisition, protected scoring, review and analysis: **7–10 hours total**.
These are provisional planning allowances, not measured lower bounds. Each prepare
remains limited to 120 minutes; stages require separate review. Before the second
stage, replace the allowance with a measured complete price and adequate precision.

For scale, 0145 completed 768 source attempts plus preparation in 12.6 minutes and
1,024 scoring searches in 31.5 minutes. Those figures make search affordable on
its old bank; they do not price a new alphabet, new source yield or new verifier
tails. The decisive missing work is the valid bank and its complete comparison,
not a large source-corpus bill. The prior review had under five hours left and
deferred this plan. The new 48-hour window removes that scheduling objection;
the build, bank and scientific-value uncertainties remain.

**Allocation update, 2026-10-10, autonomous run 2026-10-10-1419.**
[Current strategy](../runs/2026-10-10-0311/strategy.md) raises root 10 from 30 to
31 experiments for one first-stage cycle, through the next strategy review.
Expected total first-stage time remains **3–4 hours**, including preparation,
validation, queue and agent review; preparation at most 120 minutes. If proposed
as a probe, use fixed seeds, descriptive output, no outcome table and at most
60 minutes summed queue timeouts. This run has its initial probe allowance.
No protected target performance may be inspected during this stage.

Use one fixed candidate: `(A+B)>(C+D) ? E:F` with roles drawn from X0–X3 on
the 625 independent inputs above. The output-addition family is an optional later
contrast, not a second bank to search if this candidate fails. Preserve the
four-source/at-least-four-holdout split, semantic separation and short-program
screen. Confirm source coverage of all four readouts and multiple predicates.
Develop and time on source/development cells only. The first stage must also
measure enough of the fitted search path on those cells to price independent
acquisition and protected scoring; merely timing the fixed prior is insufficient.
Any pilot fits remain development artifacts and cannot stand in for independent
confirmation builds.

The exit is a validated, performance-blind split with usable source discovery,
headroom and a measured price/precision scenario for the complete usefulness
comparison, or a specific semantic, build or cost obstacle. Return to strategy
after this stage in either case; do not relax the screen or add an alphabet/domain
sweep. A descriptive no-hit result is a bound, not proof of impossibility.

The complete candidate still has a provisional **7–10-hour** price: this stage
plus **4–6 hours** for a separately approved acquisition/transfer cycle. It is
worth funding because success would extend the recipe to different assembly
requirements and a resolved failure would locate a portability limit. Neither
code completion nor available time automatically earns stage two. Replace these
allowances with measured full costs before allocating confirmation; reassess
against the current run deadline, **2026-10-12T14:19:15 Europe/Stockholm**.
Use representative timing under sustained intended concurrency (at least 64 jobs
or the collection batches), and contemporaneous baseline measurements for any
wall-time economics. The defective two-row calibration in 0145 is not reusable.
