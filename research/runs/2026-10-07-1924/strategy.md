---
next: proposal
---

Allocate one more experiment to root 10: **does refitting a decoder to its own new
discoveries improve fresh search further, and does that increment transfer?** Compare
feedback with collecting another corpus under the original G4 map. The
[concept plan](../../plans/iterated-solver-corpus.md) supplies the route; the steward should
write the proposal. This direction deserves a feasibility probe, so do not end the run now.

**What the program has learned.** The [core question](../../../README.md#core-question)
has two parts: how maps bias discovery, and whether that bias can adapt to a task family.
The [digest](../../digest.md), question tree, [ledger](../../briefs/2026-10-05-2225-ledger.md)
and recent decisions support a substantial but bounded answer:

- Frequency predicts some discovery differences, but solver supply alone does not predict
  evolutionary speed. Fixed-target folding gains were consistent with sampling gains;
  TAG lexicase sometimes beat the corresponding random-search expectation. Cheap joins,
  rather than modularity alone, enabled composition. Selected-mate crossover caused a
  seeded shared-helper establishment barrier that self-mating removed. Natural B-helper
  arrival and single-copy establishment remain unresolved.
- Map adaptation transfers after program populations restart. Threshold fits gave about
  4× over uniform, with a hand-set scaffold performing comparably. Root 10's selected token
  weights on supplied G/G4 context gave about 2–3× on withheld compositions. Both starting
  programs and ongoing decoder use contribute, about 1.3× each given the other; their
  sub-additivity does not identify a shared mechanism.
- Four search-selected context procedures found no resolved increment beyond token
  learning. The [last](../2026-10-07-1137/analysis.md) had a working token control and
  C/T 0.967× [0.871, 1.073]. That bounds this procedure, not contextual learnability.
- The [latest result](../2026-10-07-1707/analysis.md) changes the opportunity: context
  fitted directly to exact solver tapes beat a token-only fit to the same tapes by
  1.365× [1.288, 1.446] on training and 1.293× [1.213, 1.378] on withheld cells, across
  32 independent corpora. Matching pooled emitted frequencies did not reproduce the gain,
  but that control was itself slower than the token fit. Use C/T to size the benefit.
  This establishes useful external fitting, not evolutionary discovery of the decoder.
- Family-specific adaptation remains unestablished. Crossed token transfer found no
  resolved matched-family advantage; the corpus fits also showed none, with one PA
  holdout favouring the other family's fit. Modest preferences remain possible. The three
  repeatedly inspected holdouts, only one BE, cannot settle general family specificity.

**Which roots matter now.** Root 10 remains the priority because it can test whether useful
learned bias supports a further cycle of discovery and adaptation. Root 01 supplies the
first half's foundation, but this result does not meet its parked questions' reopening
conditions. Leave its budget at 6. Historical folding dynamics and the CA developmental
revival remain motivations; neither currently offers a more direct, measured route to the
remaining map-adaptation question. No new root is needed: feedback fitting fits root 10.

| Candidate direction | Why it matters | Decision now |
|---|---|---|
| Refit from discoveries made under the fitted decoder | Tests whether the new learning signal supports another useful feedback step, or amplifies its own biases without further transfer. | First priority; reuse the reviewed collector and fitter. |
| Build a bank with several covered holdouts per family | Addresses the core question's largest generalization gap; the present bank cannot supply broad family evidence. | Worth a future feasibility study, but three screens already exposed alias and coverage problems. A new bank plus adaptation is less likely to yield an answer in this window. |
| Fit executable structure or intervene on particular transitions | Could explain why corpus context helps and distinguish useful structure from inactive tape correlations. | Second priority; an active-token extractor needs new validation, while a census alone would not establish causation. |
| Resume joint or non-displacing context selection | Tests whether evolutionary selection can reach useful context. | Still live, but replicated learning exceeds this window; another small noisy continuation is less informative than feedback fitting. |

**Next for the steward.** Open a new child under root 10 (next available number 21), leaving
20 closed at its answered scope. Ask whether one further fixed-rule refit improves on its
parent decoder and on an independently refreshed G4-corpus fit. Keep the existing bank and
fitting rule so a change in corpus source is interpretable. Transfer only maps into fresh
program populations. A positive result would support repeated external adaptation from
the system's own discoveries; it would not establish map mutation/selection, family
specificity, or indefinite improvement. The steward sets sizes and disjoint outcome rules,
including unresolved, degradation and infeasibility.

**Allocation and time.** Status reports 13/40 experiments used, both roots exhausted,
deadline 2026-10-07 22:25, about three hours remaining. Raise **root 10 from 13 to 14
(one step of +1)**. Slot 14 should settle whether a second refit produces a transferable
increment attributable to the changed source of discoveries, or bound that procedure's
gain; if infeasible, establish its measured yield and cost. No other question field changes.
No new root is opened. The 27 unused run slots are not 27 affordable cycles.

Run 1707 took 81 minutes, including 31 for G4 collection, 33 for training evaluation and
16 for transfer. These are anchors, not a runtime estimate for the additional control.
Target roughly 75–90 minutes of queue and reserve the rest for preparation, review and
analysis; reprice against the actual deadline. Prefer dropping redundant reference arms
and family-specific readouts to sacrificing independent corpus replication. If the complete
comparison cannot fit, the same slot may measure feasibility without claiming an answer.

**What to stop.** Stop repeating the current context-selection loop, rescoring unchanged
maps for tiny family contrasts, chasing the nonreplicating branch/linear shift, and refining
the old helper or threshold-veto mechanisms. Do not start a smoothing sweep or repeated
refits until one looks favourable. One further feedback step is the present allocation;
any extension returns to strategy. An unresolved or negative second step limits that step,
not all iterative learning, and does not show that the first fit captured everything.
