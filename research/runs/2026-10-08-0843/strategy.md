---
next: proposal
---

Continue [root 23](../../questions/23-heritable-variation-bias/question.md) for **one corrected,
replicated acquisition test**, then review. The next question is: **at equal evolutionary
exposure, can inherited token frequencies acquire useful bias that survives discarding the
programs?** Use the [equal-exposure addendum](../../plans/heritable-bias-equal-exposure.md).
This is worth its full cost because it can distinguish useful acquisition, protection against
a degraded control, and failure of this selection route. Code availability makes it cheaper;
it is not the reason to run it.

**What the program has learned.** The [core question](../../../README.md#core-question) has
two parts: how a map biases discovery, and whether its bias can evolve toward a task family.
The [digest](../../digest.md), question tree, plans, [previous run's summary](../../briefs/2026-10-05-2225-auto-summary.md)
and recent decisions support four conclusions:

- Maps affect what arrives, but exact-solver frequency alone does not predict evolutionary
  speed. Folding's fixed-target advantage was consistent with greater solver supply; TAG
  evolution sometimes beat its computed random-search expectation substantially. Cheap joins,
  rather than modularity itself, explained the early composition advantage. The helper work
  separated arrival from establishment: mixing lineages obstructed rare seeded shared forms,
  while natural B-helper arrival remained unresolved. These are scoped mechanisms, not a
  general developmental advantage ([root 01](../../questions/01-map-bias/question.md)).
- Bias can transfer. Externally fitted threshold weights speed search about 4× over uniform,
  with a simple hand-set scaffold performing comparably. Outer-selected token multipliers
  transferred about 2–3× on screened compositions. Both starting programs and ongoing decoder
  use contribute, with overlapping benefits. Family specificity remains unresolved; none of
  this identifies mutation alone as the cause ([root 10](../../questions/10-compositional-map-transfer/question.md)).
- Useful context exists beyond token frequency. Solver-corpus fitting gave C/T 1.365×
  [1.288, 1.446] on training and 1.293× [1.213, 1.378] on withheld cells
  ([1707](../2026-10-07-1707/analysis.md)). One feedback refit improved over its parent
  1.40× / 1.29× and beat fresh one-shot refitting ([1924](../2026-10-07-1924/analysis.md)).
  Search-selected context did not add a resolved increment in the procedures tried; the
  calibrated comparison was 0.967× [0.871, 1.073] ([1137](../2026-10-07-1137/analysis.md)).
  Thus the missing result is acquisition by selection, not the existence of useful context.
- Feedback increased context's relative advantage on training, 1.169× [1.093, 1.250], mostly
  in branch-else; the withheld interaction remains unresolved, 1.087× [0.984, 1.200]
  ([2156](../2026-10-07-2156/analysis.md)). This completes a comparison using 1924's context
  rows, not an independent replication. The repeatedly inspected bank and single branch-else
  holdout limit task generality. More scoring seeds or new lineages could improve precision;
  neither supplies new task replication.

Root 23 has **no result**. [2243](../2026-10-07-2243/decision.md) stopped before its substantive
queue. Its single acquisition per arm/family revealed unequal stopping exposure and poor max
performance. Those observations change the design, not our beliefs about inherited adaptation.
The 569-minute gate estimate was a worst-search envelope; mean-based pricing was about 54 minutes
before allowances. Neither prices the revised fixed-duration acquisition reliably.

**Root priorities.** First, 23 tests a selection unit missing from the evidence: the variation
law travels with each program and is selected through program reproduction. It addresses a
limited part of map evolution with fixed token meanings, not evolved developmental context.
Second, 10 remains the strongest route to compositional transfer; its valuable next work is
generalization beyond the old bank or a learning signal that can reach the useful context.
Third, 01 supplies essential controls and the arrival/establishment distinction, but its parked
helper, rarity and shortcut refinements would not currently change the choice of research
direction. The older folding and CA results remain background, not evidence for family-adapted
bias. No new observation justifies restarting those tracks in this block.

**Current line against a different mechanism.** Literature searched for this review puts
23 closest to self-adaptation. [Stephens et al., *Self-adaptation in evolving systems*
(1998; 1997 preprint)](https://pubmed.ncbi.nlm.nih.gov/9847423/) encode mutation and crossover
probabilities without directly rewarding those parameters, and demonstrate adaptation in a
changing environment. Our proposed test instead inherits token probabilities and asks whether
their frozen value transfers after the programs are discarded. The paper motivates this route;
it does not establish that result here.

The mechanistically different candidate is further corpus-distribution learning, related to
[Salustowicz and Schmidhuber, *Probabilistic incremental program evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/).
PIPE updates a program-generating distribution from successful programs. Root 10 similarly
extracts statistical information from solvers, but with its own full-tape contextual fit and
fresh-population evaluation. This supplies a direct learning signal, whereas 23 relies on
association between inherited modifiers and reproductive success. A further fit could improve
search without answering whether selection can acquire the bias. Conversely, failure of 23
would not undermine the demonstrated usefulness of externally fitted context.

| Candidate | Value relative to full cost now |
|---|---|
| Corrected inherited-frequency acquisition | First: 5–7 h including agent work and contingency; changes what we know about an untested acquisition route. Uniform and scaffold prevent a large linkage ratio from being mistaken for useful learning. |
| Another corpus-feedback round or precision on the old interaction | Roughly 1–3 queue hours plus a review cycle, based on recent runs. Cheaper, but primarily refines an established external-fitting result on the same tasks. Defer until iteration stability or this interaction changes a chosen method. |
| Fresh bank with several covered holdouts per family | The strongest next generalization question. Semantic construction, screening and replicated learning need their own bounded plan and full price; the three earlier screens show that a quick baseline is not the whole cost. Reconsider at the first root-23 review, while roughly 40 h should remain. |
| More contextual outer-loop optimization | Earlier substantive learning alone cost 4.6 queue hours, before preparation and analysis. Defer until a specific change addresses the demonstrated acquisition gap; another parameter sweep is lower value. |

**Next for the steward.** Test frozen usefulness against uniform under equal scheduled
generations, retaining ancestry-broken and scaffold controls. The linkage comparison remains
necessary for attributing benefit to persistent inheritance. Keep both families and interpret
them separately; exact-solve counts alone do not measure selection on partial fitness. Continuing
after solving introduces maintenance selection, so name that scope. The addendum covers the
implementation direction; the steward chooses the primary effect, replication and decision
rule. Do not carry forward 2243's early-stop acquisitions as confirmation.

**Owner note disposition.** The only note is [owner-heritable-map.md](../../plans/owner-heritable-map.md).
It is unchanged since [strategy 2243](../2026-10-07-2243/strategy.md) answered it: SHA-256
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
There are no new or changed notes awaiting an answer. Reaffirmed in light of preparation:

- **Pursued:** step 1, inherited frequencies, with fixed meanings, uniform/scaffold controls,
  acquisition costs and the 120-minute prepare limit. Reconsider after this first corrected
  result, not after automatically spending both slots.
- **Deferred:** step 2, capture and synonyms. Reconsider only after useful frozen transfer,
  credible value beyond the scaffold, and a specific limitation that reassignment could fix.
  Merely moving weights or recovering the scaffold does not justify engine work.
- **Deferred:** step 3, population-level maps. Root 10 already tested outer selection;
  reconsider for a concrete new learning signal or a planned fresh-bank comparison.
- **Declined for this block:** free table mutation and ambiguous intermediates. They explain
  no current observation. Reconsider only as necessary controls in a funded reassignment study.

**Allocation and exit.** `research.py status` reports 0/40 experiments in run `2026-10-08-0812`,
deadline `2026-10-10T08:12:10`, and root balances 01: 0, 10: 0, 23: 2. Keep all budgets unchanged;
open no new root. Use one of 23's two slots through the next strategy review, targeting ≤3 queue
hours and **5–7 h total**, based on the steward's roughly one-hour queue estimate plus revised
timing, review, analysis and contingency. The second slot stays conditional; the original
two-slot 10–14 h ceiling remains. The other 38 experiment slots are unallocated, not a quota.

Review immediately after the first result, a feasibility-only outcome, or another build/cost
obstacle. Exit this block with a useful acquisition result, a decision-relevant bound on this
procedure, or a measured unresolved obstacle and continuation price. Fund transfer only if it
can change the acquisition/practical-value conclusion; fund more training precision only if
measured uncertainty and full cost justify it. At that review, a promising fresh-bank direction
needs a concrete plan before a stop decision. No deadline extension is implied.

**What to stop.** Stop the early-stop exposure design, worst-search-times-every-batch pricing,
automatic C3/C4 progression, old-bank small-preference refinement, and optimizer/curriculum
sweeps. Keep 08/09 and the helper questions parked. Stop expanding inherited frequencies if
the only established achievement is costly recovery of the supplied scaffold; preserve that
scientific acquisition result without escalating to reassignment. A decision-changing,
affordable inheritance test remains, so stopping the autonomous run now is not justified.
