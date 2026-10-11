# Can learned subtrees improve an already structural search prior?

Concept plan for [root 10](../questions/10-compositional-map-transfer/question.md),
written at [strategy 0024](../runs/2026-10-11-0024/strategy.md). **One first-stage
experiment allocated by [strategy 0150](../runs/2026-10-11-0150/strategy.md).**
The update below fixes its current comparator, cost units and exit. A later
fresh-bank stage remains unallocated. The steward supplies the experimental
design and fixed decision rule; this is not an experiment registration.

The core question now needs an increment from learned bias beyond conventional
structural search. A8 learned useful information, but its complete tape procedure
has no worthwhile geometric advantage over plain tree GP on DG, and tree GP is
cheaper on TS. Learning which complete expressions to propose is a plausible
next mechanism. It must earn its acquisition cost against the best justified
structural comparator, including restarts if they prove useful.

The closest precedent is [Keijzer, Ryan and Cattolico, *Run Transferable Libraries
— Learning Functional Bias in Problem Domains* (2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf),
which transfers acquired functions between GP runs. Our first candidate is
narrower: external extraction and frozen insertion of literal subtrees, expanded
into ordinary primitives. It adds neither callable abstractions nor an inherited
decoder. The paper motivates reuse, not a predicted result on our banks.

**Do not directly transplant the saved tape libraries.** The
[syntactic audit](../runs/2026-10-11-0024/planning-audit.json) found only 30/693 DG
entries and 1/768 TS entries that parse as one complete expression in the current
tree grammar without underflow or leftover stack values. Filtering would leave
4/24 DG and 23/24 TS libraries empty. These are entries across builds, not unique
motifs or efficacy measurements. Activity in a source tape does not establish a
self-contained function. Completing windows from target canonicals, silently
supplying missing operands, or promoting default-stack behavior into a new
terminal would change the representation and the question.

**What to build instead.** Collect exact source solutions using the reviewed
tree search itself, on the existing four source cells per family. Save immutable
trees and provenance. Use a small fixed source-attempt allocation, chosen and
priced before outcome inspection, and retain every failure and empty library.
No target solver, target-dependent subtree score or canonical enters extraction.
If restarts are adopted, charge every constituent source attempt. This is a new
acquisition recipe, not reuse of A8's already demonstrated economics.

Extract proper subtrees directly from those trees, with a bounded primitive-token
size range, deterministic recurrence/ranking rule and capped library size. Freeze
the rule using source material only. Favor recurrence across source tasks;
many copies in one lineage are not independent source evidence. Exclude complete
source solutions and retain an explicit ordinary-mutation fallback for empty
libraries. Verify compiler/interpreter/VM agreement and the exclusion rules.
The current tree representation already has subtree spans, insertion and a
32-token primitive cap; reuse those interfaces without a new execution engine.

Use the frozen library as one bounded source of mutation donors. Start fresh
populations with the unchanged initializer. Expand every inserted subtree fully:
it receives neither a free one-token macro cost nor an increased size allowance.
Keep selection, crossover, total effort and any restart schedule common across
the comparison. Preserve the ordinary random-donor route so the library cannot
remove support. Record actual insertion, size rejection and fallback frequencies.

**First experiment.** On the development DG target roster, ask whether the
acquired subtree procedure improves fresh search beyond the structural baseline
and a generic subtree-donor control matched to the learned donor's size law.
Both controls must use valid trees; invalid shuffled tokens are an inadequate
control. Keep the ordinary baseline to detect a degraded matched control. A
gain over size-matched donors addresses learned content beyond donor size; it
does not isolate token frequency from subtree dependencies. Avoid another broad
component matrix. TS is a separate boundary if affordable, not evidence of a
crossed family preference without its own acquisition comparison.

Independent source acquisitions, not inserted fragments or target seeds, are
the learning units. Discard resident source trees after extraction. Choose a
fixed comparison capable of changing the decision, with a 95% cost interval,
solve fractions, individual cells and capped-cost sensitivity. Charge source
searches, failures, extraction and later search in consistent arithmetic units.
A frozen search improvement and a credible repayment range justify carrying
this procedure forward. Improvement only over a damaged control, or a tight
small/harmful increment over ordinary structural search, ends this extractor's
expansion. Broad intervals require a priced resolution.

**Complete cost and later answer.** Provisional **7–10 hours total** for the
first substantive acquisition/usefulness study, including at most two hours
implementation and validation, about 2–4 queue hours, proposal, reviews and
contingency. These are unmeasured allowances: tree source discovery is available,
but extraction yield and learned search are not priced. Use source/development
timing under sustained concurrency. Do not fund a build merely because it fits.

A positive first result earns consideration of a separately reviewed transfer
study: freeze the full method with a genuinely unsearched composition bank,
retain the structural comparator, replicate acquisition and reset all target
populations. Allow provisionally **5–8 further hours**, **12–18 hours for the
complete candidate**; semantic bank construction and actual rates can change
that price. If the new bank cannot be validated, report that limit without
calling new seeds on DG/TS fresh transfer. No second-stage slot is allocated.
A fresh-bank result would extend externally learned
structural bias, while per-individual inherited acquisition remains a separate
root-23 question.

**Allocation update, 2026-10-11 0150.** The [restart result](../runs/2026-10-11-0024/analysis.md)
selects R-tree as the evaluation comparator: 90,392 mean evaluations and
765/768 exact DG solves, against R-A8's 114,137 and 754/768. A8 remains cheaper
in worker seconds. This supersedes any reading of the earlier plan that plain
full-cap tree GP is an adequate primary comparator or that an evaluation win
necessarily saves time.

Ask whether a frozen library learned from **new tree-source searches** lowers
fresh DG search cost beyond both R-tree and valid generic donors matched to its
size law. The complete eight-cell DG development roster is the primary scope;
source collection uses the existing four DG source cells. TS may provide a
separately priced boundary, but no second acquisition family or crossed-family
claim is needed in this block. All these banks are development data.

Use the frozen 0024 restart policy in every scoring arm: at most eight fresh
65,536-evaluation attempts, 524,288 total, with training-case redraw and exact
D625 verification. Retain the same library throughout a learned job's restarts.
Keep the initializer, crossover mix, primitive capacity and selection fixed.
Only a bounded fraction of ordinary mutation donors becomes library draws;
specify the ordinary-donor fallback before scoring. No learned initialization,
restart tuning, new size-control method or callable macro is part of this study.
For the matched donor control, price a sampler of valid trees conditional on
compiled primitive size, including rejection costs. A small library need not
be forced to 32 entries, and an empty one stays in the acquisition cohort.

Source inspection at `1773d11` confirms that `tree_gp_search.Tree` already stores
subtree spans, compiles primitive tokens and provides size-checked insertion;
`search` returns `solver_tree`. `restart_gp_run.py` saves constituent attempts.
Reuse those reviewed interfaces on the research branch. The missing work is
bounded source orchestration, extraction, donor controls and reporting, not a
new VM. Verify that source searches retain their exact trees through the wrapper.
Do not recycle target-solving trees from 0024 as training data. Preserve an exact
operator-off replay and audit actual seed sets across acquisition, calibration,
confirmation and historical data before the queue.

**Cost unit and decision value.** Make arithmetic capped evaluations the primary
search-efficiency unit, with a reliability guard and acquisition-build uncertainty.
Measure worker seconds under comparable sustained load as a separate deployment
unit, including donor construction, verification and extraction. A worthwhile
effect of roughly a **20% evaluation saving** is a sizing scenario for the steward,
not a registered rule or prediction. DG's near-complete solving leaves little
reliability headroom, but its 90k mean cost leaves a meaningful speed question.
The generic-donor comparison asks whether source content adds beyond donor size;
it does not isolate token frequency from dependencies. A benefit only over a
degraded control cannot justify continuation.

Charge the complete source policy, every unsuccessful attempt and extraction
once per deployed library. Report arithmetic acquisition-plus-search curves in
both units without assuming a reuse horizon. An evaluation gain with a time
loss is still evidence about learned search bias, but does not establish a
practical faster method. Any later allocation must weigh the price of that
remaining obstacle explicitly.

Raise root 10 **36 → 37**, one substantive experiment through the next review.
Allow **7–10 h total**, at most **120 min preparation** and **4 h summed queue
timeouts**, including proposal, validation, collection, scoring, reviews and
contingency. The 0024 queue completed preparation and 3,840 scoring jobs in
about 36 minutes; DG R-tree averaged 8.86 worker-seconds. These anchor baseline
scoring only: tree-source yield, extraction, learned search tails and precision
need sustained development/source timing before admission. Freeze a decision-sized
comparison after that pricing. A standalone probe is not the intended purchase;
if only one is justified, use its 60-minute limit and return for review.

Return to strategy after the result or a measured build, validity, precision or
complete-cost obstacle. Useful learned improvement with credible economics earns
consideration of the separately reviewed **5–8 h** fresh-bank stage; the complete
candidate remains **12–18 h**, inside the approximately 36 h remaining at review.
Tight small effects or harm end this extractor's expansion; broad uncertainty
requires a priced resolution. No result automatically funds more corpus sizes,
fragment lengths or rates. Finish analysis before the run deadline,
**2026-10-12T14:19:15 Europe/Stockholm**.
