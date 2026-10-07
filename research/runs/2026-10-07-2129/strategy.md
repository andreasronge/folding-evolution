---
next: proposal
---

Continue root 10 for one comparison using the saved maps: **does feedback increase the
advantage of fitting context, or can token-only fitting recover the additional improvement?**
This is more informative now than another feedback round, and avoids new corpus collection.

**What the program has learned.** The [core question](../../../README.md#core-question)
asks both how developmental maps bias discovery and whether that bias can adapt to a task
family. The [digest](../../digest.md) and question tree support a substantial but bounded answer:

- Random-genome frequency predicts easy behaviours, but exact-solver frequency alone does
  not predict evolutionary search speed across harnesses. Folding's fixed-target advantage
  was consistent with greater solver supply. The helper studies separated arrival from
  establishment: mixing between lineages obstructed rare seeded shared forms, self-mating
  removed that barrier, and naturally arriving helper types remained a different problem.
- Selected token weights transfer roughly 2–3× on root 10's screened composition bank.
  Both starting programs and continued decoder use contribute, each about 1.3× given the
  other. These interventions do not isolate solver supply from neighbourhood quality.
  Crossed training did not resolve a matched-family advantage on the three withheld cells.
- Several search-selected context procedures added no resolved benefit. The calibrated
  [last comparison](../2026-10-07-1137/analysis.md) bounded C/T at 0.967× [0.871, 1.073]
  with a working token control. This limits those procedures, not useful context itself.
- Fitting to exact solver tapes changed the answer: [1707](../2026-10-07-1707/analysis.md)
  found contextual versus token-only gains of 1.365× [1.288, 1.446] on training and
  1.293× [1.213, 1.378] on withheld cells. Then [1924](../2026-10-07-1924/analysis.md)
  found that refitting to discoveries made under C produced C2, faster than C by
  1.404× [1.347, 1.464] and 1.289× [1.204, 1.381], respectively. A refreshed G4-corpus
  fit did not resolve improvement over C. The source procedure matters, but yield,
  diversity and tape content remain bundled.

The last two studies establish useful external fitting and one useful feedback step.
They do not establish evolutionary discovery of decoder context, family specificity,
or sustained improvement. Transfer is on a repeatedly inspected, screened bank with only
one BE holdout. Sharper tables accompanied improvement; sharpening is not its identified cause.

**Which roots matter now.** [Root 10](../../questions/10-compositional-map-transfer/question.md)
has the strongest connection to the remaining adaptation question and the best measured
feasibility. Its immediate uncertainty is what the successful feedback procedure is learning.
Its larger unresolved question is family-specific transfer beyond this bank.
[Root 01](../../questions/01-map-bias/question.md) remains the foundation for arrival versus
search dynamics, but the new corpus results provide no practical reason to resume the parked
helper or threshold-veto studies. Leave its budget unchanged. Historical folding, chem-tape
plasticity and CA development supply motivations, but have no better prepared comparison
for this final window. The existing roots still serve the core question; open no new root.

| Candidate direction | What it could change | Priority |
|---|---|---|
| Compare token and contextual fits across both saved corpus rounds | Distinguishes further token improvement from an increased benefit of fitted context; directly qualifies what feedback achieved. | Next. All four tables already exist for every lineage. |
| Collect under C2 and fit C3 | Tests continued improvement or harmful concentration. | Worth a later probe, but adds collection and another iteration before explaining the current gain. Preserve the [iteration plan](../../plans/iterated-solver-corpus.md). |
| Build a broader family-transfer bank | Addresses the largest generalization gap and supplies task replication. | High scientific value, lower immediate feasibility after three alias/coverage screens. Extend the existing [family-bank plan](../../plans/four-reducer-family-transfer.md) before more family claims. |
| Resume context selection or extract active-token structure | Could bridge external fitting to selection or identify the carrying structure. | Requires longer learning or new validated instrumentation; lower value in this window than the saved-map comparison. |

**Next for the steward.** Add a child under root 10 (next available number 22); leave 20
and 21 closed at their answered scopes. Follow the new
[concept plan](../../plans/feedback-context-increment.md), setting the actual size and outcome
rules. Compare the context advantage in the original corpus round with its advantage in
the feedback corpus round. C2/T2 alone establishes whether context remains useful in the
final map; it cannot establish that the *feedback increment* is contextual. The paired
change in that advantage addresses the latter question. Include the reused holdouts to
test transfer, with independent corpus lineages retained as the replication unit.

**Allocation and deadline.** `research.py status` reports 14/40 experiments used and an
autonomous deadline of 22:25:38 Stockholm. Raise root 10 **14 → 15, one step of +1**.
Slot 15 should settle whether feedback increases context's benefit over the restricted
token fit, including transfer, or give a useful bound; if the comparison cannot fit,
measure its cost and attainable precision. No other existing-question field changes.
The root's prose still records the completed 14 slots; the steward updates it after the cycle.

At 21:37 about 48 minutes remained. The saved artifacts contain T and C for all 32 original
and feedback corpora; all parent C tables match exactly. No new fitting or collection is
needed. Run 1924 spent about 29 minutes evaluating three arms on training and withheld
cells, separate from collection. Four arms with slower token fits need a measured timing
probe, not that same runtime assumption. Aim for roughly 20–25 queue minutes after
preparation, preserving time for review and analysis; choose size from the actual remaining
time. If a decision-sized comparison cannot fit, a bounded feasibility probe still deserves
the slot. Unused experiment capacity is not available wall time.

**What to stop.** Stop automatic feedback iteration after each positive result, repeated
search-selected context tuning in the tested loops, rescoring this bank for tiny family
preferences, pursuing the nonreplicating branch/linear shift, and helper/threshold mechanism
refinements. Do not add smoothing sweeps, active-token extraction or another bank to this
allocation. Review the result before funding C3. There is no scientific case for `next: stop`
while this prepared comparison deserves at least a feasibility probe; let the deadline end
the run if necessary, without treating it as evidence that root 10 is answered generally.
