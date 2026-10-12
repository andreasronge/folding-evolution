---
next: proposal
---

Fund **one test of consistent input rebinding in acquired libraries**, under
root 10. Ask whether literal input bindings limit reuse of computations already
discovered. Expected full cost **5–7 h, ceiling 8 h**. This is worth buying because
it chooses between collecting more literal examples and representing acquired
expressions with variable arguments. Another confirmation of unchanged library
use would not make that decision.

The [core question](../../../README.md#core-question) has two unequal answers:
we can acquire useful search bias from evolved programs, but inherited learning
of transferable content remains unshown. This review weighs the
[digest](../../digest.md), question tree, historical and active plans,
[owner note](../../plans/owner-heritable-map.md), recent decisions and
[briefs](../../briefs/2026-10-11-2026-10-11-2150.md).
`research.py status` reports **22/40 experiments used**, about **14 h left**,
and zero remaining allocations in roots 01, 10, 23 and 55 before this change.
The [ledger](../../briefs/2026-10-10-1419-ledger.md) contains seventeen full
experiments and five probes: no unused probe allowance at this review.

**What the program has learned.**

- **Supply, variation and lineage association all matter.** Random-genome
  frequency predicts easy behaviours better than hard discoveries; folding's
  tested fixed-target advantage largely tracked solver supply. Cheap joins,
  rather than modularity alone, explained the tested composition advantage.
  Mixing lineages can prevent establishment of useful rare forms
  ([01](../../questions/01-map-bias/question.md)). These constrain learning
  mechanisms; they do not establish a general developmental advantage.
- **Evolved programs contain reusable information beyond token frequencies.**
  Externally fitted context transferred, including **2.12× [1.86, 2.41]** over
  token fitting on a fresh then-addition shape. Frequency matching and undirected
  mutation widening did not reproduce it. Fragment reuse and cheap feedback
  improved the complete procedure. DG/TS acquisition showed family dependence
  in one direction, carried by both table and library. Outer-selected token
  maps helped, but the contextual selection procedures added no resolved gain
  ([10](../../questions/10-compositional-map-transfer/question.md)). External
  extraction, outer-loop selection and per-individual inheritance remain
  different achievements.
- **Better baselines narrowed the practical claim.** Restarted tree GP needed
  fewer DG evaluations than A8, though A8 used fewer worker seconds. Learned
  tree donors then helped substantially, including on a fresh shape. Supplied
  sum donors removed the practical case for TS acquisition on B/C, while
  libraries harmed near-solved TS targets. A learned method must earn its cost
  against an appropriate structural prior, not just a weak decoder
  ([44](../2026-10-11-0024/analysis.md), [46](../2026-10-11-0348/analysis.md),
  [51](../2026-10-11-1019/analysis.md)).
- **Useful acquired computations extend beyond sums, with substantial limits.**
  Uncapped semantic libraries reduced order holdout cost to **0.37 [0.33, 0.42]**
  of R-tree; rearranging helper entries removed most development saving, though
  replacements were mostly trivial. The unchanged recipe then worked on a fresh
  signed-gate family (**0.577 [0.47, 0.72]**), where transported order content
  gave no resolved saving. The rectifier probe instead observed scarce useful
  source content. Supplied family priors remained much better
  ([56](../2026-10-11-1530/analysis.md), [57](../2026-10-11-1628/analysis.md),
  [58](../2026-10-11-1938/analysis.md),
  [54](../../questions/10-compositional-map-transfer/54-rectified-sum-acquisition/log.md)).
- **The latest hard-tier result is sufficient.** Frozen signed-gate libraries
  cost **0.778 [0.696, 0.870]** of R-tree on eighteen previously unsearched
  chain cells, repaying acquisition after **5.4 [3.8, 9.7] searches**. The 20%
  saving label remains unresolved; more precision there changes no decision.
  Supplied helpers cost **0.338 [0.298, 0.383]** of acquired-library search.
  Coverage tracks savings, but is confounded. These are held-out cells of the
  development chain bank, not fresh-bank transfer or helper causality
  ([60](../2026-10-11-2150/analysis.md)).
- **Inheritance has selected a supplied dose, not discovered content.** Root
  23 did not establish useful inherited token frequencies. In 55, recurrent
  modifier mutation let linked selection raise the library bit above controls;
  frozen endpoint laws cost **0.805 [0.704, 0.913]** of the start, unresolved at
  the pre-set 10% bar. Arm-average costs roughly followed dose predictions;
  fixed R-all stayed 1.71× cheaper. There is no inherited content or transfer
  result ([23](../../questions/23-heritable-variation-bias/question.md),
  [55](../../questions/55-inherited-library-choice/question.md)).

**Which roots matter now.** **10 first:** whether acquired computations are
represented so they can be reused, rather than repeatedly rediscovered for each
input role. It directly serves the goal of cheaper related-task search and has
a measured hard tier and large supplied-prior gap. **55 second, parked:**
equal-dose choice among useful contents is the next meaningful inheritance
question; another dose result is not. **23 stays parked:** 55 supplies no
token-specific reopening signal. **01 stays unfunded:** its supply/linkage
lessons inform these choices, but more rarity precision will not select the
next learner. CA, folding and runtime plasticity offer no better bounded
answer in this window. PSB2 remains a later breadth test; its older
[plan](../../../Plans/psb2-sanity-probe.md) does not price the current acquisition
procedure against suitable baselines.

**What changes the recommendation.** I checked the
[steward's extraction proposal](../2026-10-11-2150/decision.md) against the saved
sources and implementation. The reproducible
[planning audit](library-planning-audit.py) and [output](library-planning-audit.json)
run no new evolution and measure no new efficacy. They reproduce all 24 original
semantic membership sets. Of 576 helper/build slots, 206 were kept, 151 were
admissible but seen in only one source cell, 121 had minimum observed sizes of
10–20 nodes, and 98 were absent. Of those 121 oversized cases, only 32 were
recurrent. Thus “three quarters of missing helpers occurred in sources” does
not mean one filter change recovers them as compact donors.

Relaxing recurrence alone raises average helper coverage **8.6 → 14.9**, but
entries **37.4 → 113.9** and lowers helper draw share **23% → 13%**. That does
not predict harm, but weakens the case for a simple admission relaxation.
Instead, applying all consistent input permutations to the *retained* entries
preserves their draw weights, structures and total helper mass. It makes all
24 helpers available in **23/24 builds**; build 5 still lacks negative gates.
Average support becomes **23.5**, not a promise of speed. Rare bindings gain
probability while common ones can lose it. This is a concrete, cheap test of
reuse across variable roles, with a genuine possible negative answer.

**Current line against different mechanisms.** I searched for the papers below
in this review; they motivate mechanisms, not expected effects here. Alternative
prices are planning estimates including implementation, validation and readout.

| Candidate | Decision and reason |
|---|---|
| Literal external extraction; relax recurrence or size | **Defer, 4–6 h.** [Keijzer, Ryan and Cattolico, *Run Transferable Libraries* (2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf) transfers acquired GP functions across runs. This is the current line's closest precedent. The audit exposes dilution and oversized representatives; do not assume retaining more entries solves coverage. Reconsider if binding generalization fails and a specific admission change retains useful probability mass. |
| Consistent input rebinding of acquired entries | **Pursue, 5–7 h; ceiling 8 h.** Parameterized reuse has a precedent in [Koza, *Hierarchical Automatic Function Definition in Genetic Programming* (1993)](https://doi.org/10.1016/B978-0-08-094832-4.50024-6). Our bounded permutation procedure adds neither evolved function definitions nor arbitrary arguments. It tests a supplied symmetry rule on learned computations, without learning more literal examples. |
| Corpus abstraction synthesis | **Defer, approximately 12–18 h.** [Bowers et al., *Top-Down Synthesis for Library Learning* (POPL 2023)](https://arxiv.org/abs/2211.16605) synthesizes abstractions guided by corpus structure and evaluates compression. It can generalize more than input names, but integration and a complete search-value test do not comfortably fit. Reconsider after this bounded representation test, or evidence that sources require larger structural abstractions. Compression alone is not the required payoff. |
| Inherited choice between order and signed-gate libraries at equal donor rate | **Defer, approximately 8–12 h.** [Stephens et al., *Self-Adaptation in Evolving Systems*](https://arxiv.org/abs/adap-org/9708002) studies indirect selection of encoded variation probabilities. Here ancestry, rather than external extraction, would select supplied content. It addresses the core inheritance gap, but reciprocal family preference, exposure and separate frozen readouts all need funding; even a win does not invent content. Reconsider at the next review only if the full comparison fits and changes the route to inherited family learning. |

**Next question for the steward.** *Does consistent input rebinding make the
same acquired computations materially more useful on hard linked compositions?*
Use the [new plan](../../plans/input-rebound-library-reuse.md). This is a changed
donor procedure on development data. Its value is the increment over R-all and
the remaining gap to R-gate, not another win over R-tree alone. Keep all saved
builds and generic rebinding of every entry; the input symmetry is supplied
knowledge and must be described that way. The plan specifies what to build;
the steward fixes the comparison, size and decision rule.

**Allocation and exit.** Change only root 10's frontmatter
`budget.experiments` **50 → 51**, one full experiment through the next strategy
review. No other root receives an increase. No new root is necessary; the
remaining root allowance stays unused. The steward may open a sub-question
(next unused number currently 61), linking 58–60 and their reopening conditions.

Expected **5–7 h complete, ceiling 8 h**, including all agent work and analysis;
preparation at most 120 minutes and summed queue timeouts at most four hours,
within that ceiling. The measured 2150 reference rates price an illustrative
four-arm, all-cell r=4 comparison at about **155 queue minutes** if the new arm
costs R-all's time; that assumption and precision need checking. Finish analysis
before **2026-10-12 14:19:15 Europe/Stockholm**. Return to strategy after the
answer or an earlier validity, build, precision or complete-cost obstacle.
Material improvement earns consideration of a fresh-bank test, not an automatic
one. A bounded small effect or harm ends uniform rebinding; broad uncertainty
requires a new consequential resolution case. Stop at review if no candidate
justifies its whole remaining cost. Eighteen spare slots are not a work target.

**Owner note.** The only `owner-*.md` is
[owner-heritable-map.md](../../plans/owner-heritable-map.md), unchanged since
[strategy 2150](../2026-10-11-2150/strategy.md), SHA-256
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
There are **no new or changed unanswered notes**. Overall **pursued**, with
continuing dispositions:

| Owner direction | Disposition, why, when to reconsider |
|---|---|
| Inherited op frequencies | **Pursued** in 23; further work **deferred** after poor frozen usefulness. Reconsider a selectable token-specific signal, headroom beyond the scaffold, or a necessary frequency-only control. |
| Safe capture and synonyms | **Deferred.** Useful inherited token learning remains unshown. Reconsider once that prerequisite and a consequential reassignment question justify separate engine validation. Input rebinding here does not change token meanings. |
| Population-level maps | **Pursued** through outer-selected token maps; more contextual selection **deferred** after no resolved increment. Reconsider changed representation or ranking evidence with acquisition and transfer fully priced. Corpus fitting is a different procedure. |
| Free table mutation; ambiguous intermediates | **Declined for this block.** Reconsider free mutation as a necessary contrast for justified reassignment; ambiguity only for a specific gap left by the preceding steps. |

**What to stop.** Stop extending unchanged libraries to longer versions of the
same construction, tightening the 20% label, dose-only inheritance top-ups,
modifier-rate sweeps and per-helper attribution with no decision consequence.
Keep source-forcing rectifier retries, simultaneous filter changes and general
abstraction-engine work outside this allocation. Question 50 stays parked until
mixed-family default deployment makes a harm-avoidance policy consequential;
54 stays parked without a funded changed rectifier method. Do not label new
seeds on spent banks as transfer, or increased helper support as learned efficacy.
