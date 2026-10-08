---
next: proposal
---

Continue root 10, changing the acquisition question: **can selection among non-solving
programs supply a useful decoder bias, before complete solutions supply the fitting data?**
Use one of its three remaining experiments for the first stage of the new
[partial-program context plan](../../plans/partial-program-context.md), then review.
The full candidate merits a provisional 14–20 h including agents; only its 6–8 h first
stage is allocated now. No budget increase or new root is needed.

**What we have learned.** The [core question](../../../README.md#core-question) asks both
how a developmental map biases discovery and whether that bias can evolve to fit tasks.
The [digest](../../digest.md), all question files and plans, recent decisions and
[run ledger](../../briefs/2026-10-08-0812-ledger.md) support four conclusions:

- **Supply and evolutionary success are different.** Root 01 found that random-genome
  frequencies explain easy tasks and much of folding's fixed-target advantage, but do
  not generally predict search speed. Cheap joins explained the composition advantage;
  lineage mixing blocked establishment of rare seeded shared forms, and self-mating
  removed that barrier. Natural shared-form arrival and single-copy fate remain partly
  unresolved. These are specific mechanisms, not a general developmental advantage
  ([01](../../questions/01-map-bias/question.md)).
- **Useful biases can be acquired and reused, mainly without demonstrated family
  specificity.** External threshold fits speed search roughly 4× over uniform, with a
  hand scaffold comparable within the tested broad margin. Outer-selected token maps
  transfer about 2× on compositions. Their starting programs and ongoing decoder use
  both help. No contextual increment was resolved from the tested outer-selection
  procedures; the calibrated continuation gave C/T 0.967 [0.871, 1.073]. This does not
  show context is inaccessible to selection
  ([16–19](../../questions/10-compositional-map-transfer/question.md)).
- **Exact solvers contain reusable information that the tested token fit misses.**
  External previous-token fitting beat token fitting on the older bank; one feedback
  refit helped further. The new comparison-gate training result was 3.11× [2.78, 3.48].
  Its frozen fits retained **2.12× [1.86, 2.41] on one fresh then-addition bank**, and
  2.60× [2.31, 2.92] on comparison-gate development holdouts
  ([1246](../2026-10-08-1246/analysis.md), [1548](../2026-10-08-1548/analysis.md)).
  Across-shape shrinkage is resolved; matched-family preference remains unresolved.
  This is external fitting, one fresh shape on two gates, and a capped endpoint.
  Emitted frequencies versus order are separated only on the older bank. The
  both-solved-pairs estimate supports robustness but conditions on success in both arms;
  it is not an uncapped population estimate.
- **Program-linked inheritance has not supplied a useful frozen bias under its tested
  rule.** Root 23's uniform/inherited cost was 0.33 [0.21, 0.53] for sum and 0.73
  [0.50, 1.06] for max; the scaffold was much better. Persistent linkage helped relative
  to shuffled ancestry on max without establishing improvement over uniform. This bounds
  one mutation law, exposure schedule and extraction rule; drift was not isolated
  ([1046](../2026-10-08-1046/analysis.md)).

**Which roots matter now.** Root 10 remains first: a transferable fitted target now exists,
so acquisition is more consequential than another small extension of its transfer score.
The key unknown is whether incomplete search already offers usable information for
changing the map. A positive would remove the exact-solver prerequisite; a bounded
negative would make the successful corpus method look more dependent on completed
assembly. Neither outcome alone answers evolutionary inheritance.

Root 23 is second in conceptual importance but remains parked: no new measured signal
meets its restart condition. Root 01 supplies the arrival/establishment foundation; its
helper, threshold and fixed-target threads have no new evidence requiring a restart.
The broader-transfer result makes root 10's saved-map mechanism tools relevant again,
but does not make all their possible follow-ups worth running. Older folding, CA and
runtime-plasticity work offer broader mechanisms but no cheaper, prepared test of the
present acquisition gap. Leave the permitted extra root opening unused.

**Current line versus different mechanisms.** Literature searched for this review:
[Salustowicz and Schmidhuber, *Probabilistic incremental program evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/)
updates a program-generating distribution using the best current program.
[McPhee and Poli, *N-gram GP: Early results and half-baked ideas* (2008)](https://drops.dagstuhl.de/entities/document/10.4230/DagSemProc.08051.5)
uses distribution estimation over instruction triplets. These motivate testing selected
partial programs as data; they do not establish transfer in this repository. Our candidate
keeps the existing previous-token representation and first asks whether that earlier
signal is useful, rather than assuming a full adaptive loop will work.

The mechanistically different alternative is inherited variation parameters, as in
[Stephens et al., *Self-adaptation in evolving systems* (1998)](https://pubmed.ncbi.nlm.nih.gov/9847423/):
parameters propagate through descendants rather than being estimated from a corpus.
Root 23 tested this route. Another modifier law could succeed, but there is no measured
direction of useful acquisition to justify its next complete cycle. My inference is that
the positive corpus results make an earlier statistical signal a better bet now.

| Candidate | Value, full cost and decision |
|---|---|
| Partial-program context, then conditional feedback | **Pursue the first stage.** New acquisition signal; provisional 14–20 h for the direction, including build, queues and agents. It can distinguish learning from incomplete search from dependence on complete solvers. |
| Score existing K on 1548's fresh-bank row | **Defer.** About 40–60 min queue (roughly 1.7 h if all capped), plus about 3 h agents, per the latest decision. Useful frequency-control check, but either result leaves the acquisition question live. Reconsider when a claim or a learner choice depends on order rather than changed frequencies. Old-bank K being weak is not evidence about new-bank K. |
| Changed inherited-frequency law | **Defer.** Roughly 5–7 h for a complete cycle, with new-law runtime unmeasured. Reconsider with a specific selection argument and measured signal beyond drift/hitchhiking. |
| Another blind contextual outer learner | **Defer.** The earlier calibrated queue alone took 4.6 h; new-bank learning could cost more, plus agents and transfer. Reconsider after a useful direction can be measured, not merely because the fitted endpoint is good. |
| Second fresh shape or another exact-solver feedback round | **Defer.** New-shape semantics and rates are unpriced; feedback is cheaper but extends an established procedure. Reconsider for a specific generality boundary or after a new acquisition method earns transfer testing. |

**Next for the steward.** Ask whether context fitted to non-solving, selected training
programs improves independent fresh search beyond a token fit to those same tapes, while
remaining useful against G4. The [plan](../../plans/partial-program-context.md) reuses the
comparison-gate training split and reviewed search/fitting code. It includes a population
sample control to interpret selection enrichment, excludes exact solvers and their
descendants from collection, and prices the entire result. The steward chooses the
design and decision rule; no experiment is registered here.

This deliberately narrows the [latest decision's](../2026-10-08-1548/decision.md) suggestion
to test an in-run refit. Calling fitting during evolution does not establish that evolution
selected the decoder. The first stage tests an EDA learning signal. Only if it works is a
bounded feedback loop justified. Genuine outer-map selection and per-individual inheritance
remain separate questions. Reused then-addition targets are now development data.

**Owner note disposition.** The sole [owner-heritable-map.md](../../plans/owner-heritable-map.md)
is unchanged since [strategy 1246](../2026-10-08-1246/strategy.md): SHA-256
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
There are no new or changed unanswered notes. Reassessed against the new transfer result:

- **Pursued, completed at tested scope:** inherited op frequencies (step 1). Further work
  is **deferred** until root 23's measured selection-signal condition is met or another
  inheritance study needs this control. The external-context result does not meet it.
- **Deferred:** capture and synonyms (step 2). The owner's useful-learning prerequisite
  for inherited frequencies remains unmet. Reconsider after useful inherited acquisition,
  credible value beyond the scaffold, and a limitation that reassignment addresses;
  engine validation would still be a separate stage.
- **Deferred as literally proposed:** competing population-level maps (step 3). Broader
  transfer now supplies the worthwhile target requested in the previous strategy, but
  an affordable selective update signal is still missing. The adjacent partial-program
  fitting route is **pursued** to investigate a different signal; it is not fulfillment
  of this outer-selection item. Reconsider actual competing maps after that signal is
  measured or a separately priced search-selected procedure becomes credible.
- **Declined for this block:** free table mutation and ambiguous intermediates. Neither
  changes a current decision. Reconsider only as necessary contrasts in a justified
  reassignment study.

**Allocation and exit.** `research.py status` confirms **4/40 experiments used**, deadline
`2026-10-10T08:12:10`, and root balances **01: 0, 10: 3, 23: 0**. The assignment gives
about **38 h left**. Supersede allocation 1534's remaining work direction: use **one existing
root-10 slot** for this first stage, expected **6–8 h total**, at most **4 h summed queue
timeouts**, with the 120-minute preparation limit. Leave `budget.experiments: 20` unchanged;
the other two slots await review. No existing question, digest or brief is edited.

Exit to strategy after that result, or earlier if construction or the measured full price
fails. Deliver a decision-sized estimate of partial-fit usefulness and a priced continuation,
or the specific reason one cannot be obtained. A promising but unresolved result warrants
a sized resolution only if it can change the choice. The provisional next stage costs
another 8–12 h; the full direction would leave roughly 18–24 h of the stated window.
Recalculate at proposal time; neither those hours nor unused slots are spending targets.

**What to stop.** Stop repeating the inherited σ=0.03 procedure and its threshold-2
extension, automatic exact-solver feedback iterations, fine family-preference estimates
on old banks, and optimizer/decoder/alias-screen sweeps. Do not reopen helper or CA work
just to fill the run. Do not turn this candidate into exact-solver fitting by extending
collection until success, or call statistical refitting inherited evolution. If the new
signal fails, compare the remaining candidates at their full costs; end with `next: stop`
when none could change an important belief in the remaining time. That condition is not
met now: the incomplete-program learning question has both a plausible mechanism and a
bounded plan that can change the next acquisition decision.
