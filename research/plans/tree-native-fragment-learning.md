# Can learned subtrees improve an already structural search prior?

Unallocated candidate plan for [root 10](../questions/10-compositional-map-transfer/question.md),
written at [strategy 0024](../runs/2026-10-11-0024/strategy.md). Reconsider at the
next strategy review, after the restart comparison or its measured obstruction.
The steward supplies any eventual experimental design and fixed decision rule.

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
calling new seeds on DG/TS fresh transfer. No second stage or experiment slot
is allocated by this plan. A fresh-bank result would extend externally learned
structural bias, while per-individual inherited acquisition remains a separate
root-23 question.
