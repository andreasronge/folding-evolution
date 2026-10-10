# Can cheap acquisition learn a family beyond reducer/output syntax?

Future concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
from [strategy 0311](../runs/2026-10-10-0311/strategy.md). **Not allocated in the current
run.** No new root is needed. This is a direction and staged cost envelope, not an
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
not a large source-corpus bill. With under five hours left now, funding only the
bank stage would leave the substantive portability question unfinished. Reconsider
this plan in the next full window, or if a validated bank and measured complete
price reduce that uncertainty enough to fit a shorter allocation.
