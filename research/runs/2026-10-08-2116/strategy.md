---
next: proposal
---

Continue root 10 for **one bounded partial-program feedback experiment**, then review.
The question is whether updating the source decoder makes unfinished searches progressively
better teachers than spending the same acquisition effort under a fixed decoder. This can
change our choice of acquisition method; merely obtaining another positive C/T ratio cannot.
Use the new [feedback plan](../../plans/partial-program-feedback.md). Expected full cost is
**8–12 h**, including preparation, queues, review and analysis. Use one of root 10's two
remaining slots; no budget increase or new root is needed.

**What the program has learned.** Read against the [core question](../../../README.md#core-question),
the [digest](../../digest.md), question tree, plans, recent decisions and
[run ledger](../../briefs/2026-10-08-0812-ledger.md), the evidence supports four distinctions.

- **Arrival, search and establishment are different.** Random-genome frequencies explain
  easy tasks and much of folding's fixed-target advantage, but do not generally predict
  evolutionary speed. Cheap joins, rather than modularity alone, explain the tested
  composition advantage. Mixing between lineages blocks rare seeded shared forms;
  self-mating removes that barrier while retaining discovery. Natural single-copy fate
  and B-helper arrival remain unresolved. These are scoped answers to part 1, not a
  general advantage of development ([root 01](../../questions/01-map-bias/question.md)).
- **Selection can acquire reusable token bias; useful additional context has so far come
  from external fitting.** Outer-selected token maps transfer about 2× on compositions,
  with both initialization and ongoing decoder use contributing. Family specificity
  remains unresolved. Four contextual selection procedures supplied no resolved increment;
  the calibrated continuation bounded C/T to 0.967 [0.871, 1.073] for its starts and budget.
  This limits those procedures, not the possibility of selecting useful context
  ([16–19](../../questions/10-compositional-map-transfer/question.md)).
- **The fitted target is now credible beyond its training compositions.** Exact-solver
  context fitting gave C/T 3.11× on comparison-gate training tasks and **2.12× [1.86, 2.41]**
  on one fresh then-addition bank, with resolved cross-shape shrinkage. Earlier exact-solver
  feedback added about 1.29× on reused holdouts. These are external fitting results;
  family preference and the carrying structure remain open. Order versus pooled emitted
  frequencies was separated only on the older bank, not on the new bank
  ([1548](../2026-10-08-1548/analysis.md), [20–22](../../questions/10-compositional-map-transfer/question.md)).
- **Complete solutions are not required for a useful first fit, but the early signal is
  much weaker.** In [1831](../2026-10-08-1831/analysis.md), partial C/T was **1.28×
  [1.12, 1.45]**, and C/G4 1.62× [1.37, 1.90], on training cells only. A 1.20× C/T benefit
  is plausible, not established. The gain mainly reflects more solves within the cap;
  BE carries the resolved family result, while PA is unresolved. Extra parent enrichment
  was unresolved (C_S/C_P 1.04 [0.92, 1.16]); this does not show that earlier population
  selection was unnecessary. Exact-solver C remains about 3.7× faster. The
  [decision's corrected source accounting](../2026-10-08-1831/decision.md) gives 7.9× more
  evaluations for exact corpora, so neither method has established equal-cost superiority.

Root 23 supplies the other important boundary: inherited token frequencies did not yield
useful frozen bias under the tested mutation/exposure rule. Uniform/inherited cost was
0.33 [0.21, 0.53] on sum and 0.73 [0.50, 1.06] on max; the scaffold was substantially
better. Persistent linkage helped max relative to shuffled ancestry without establishing
usefulness over uniform. Drift was not isolated
([1046](../2026-10-08-1046/analysis.md)).

**Which roots matter now.** Root **10 is first** because it can connect an observed early
learning signal to a working acquisition procedure. A feedback advantage at matched effort
would establish that the map can improve the data used to update itself before completed
solutions supply the fit. A bounded failure would favour one-shot acquisition and weaken
the case for further partial-feedback machinery. Both change a research decision.

Root **23 remains second in conceptual importance but parked**: it addresses endogenous
inheritance directly, yet partial-corpus fitting on a different harness does not meet its
changed-rule/selection-signal restart condition. Root **01 remains the mechanism foundation**;
none of its parked threads has new evidence requiring a restart. Older folding, CA repair
and runtime plasticity offer different developmental questions, but presently lack a
prepared, higher-value test of this acquisition gap. Existing root 10 serves the next
question; leave the permitted additional root opening unused.

**Current line against different mechanisms.** Literature searched for this review:
[Salustowicz and Schmidhuber, *Probabilistic incremental program evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/)
iteratively updates a program-generating distribution using the current best program.
Our proposed population-corpus feedback is a related estimation-of-distribution approach,
with frozen reuse as the endpoint. Its update is externally fitted, not selected among
decoder genotypes or inherited with individual programs.

A genuinely different candidate is **learning reusable program abstractions**, motivated by
[Ellis et al., *DreamCoder: Growing generalizable, interpretable knowledge with wake-sleep
Bayesian program learning* (2020 preprint)](https://arxiv.org/abs/2006.08381).
DreamCoder learns symbolic abstractions as well as a neural search guide. A small repository
analogue would extract executable fragments from training solvers and make those fragments
available to later search. That changes the units of assembly, whereas feedback changes
probabilities over the existing units. My inference is that this could preserve dependencies
which a previous-token table misses. The paper is motivation, not evidence that it will
help this stack system. Root 01 also warns that cheap joins alone can explain a putative
modularity advantage, so an abstraction test would need an expanded-program cost control.

The owner's alternative, **inherited variation parameters**, has a different credit path
again: descendant success propagates parameters without corpus estimation.
[Stephens et al., *Self-adaptation in evolving systems* (1998)](https://pubmed.ncbi.nlm.nih.gov/9847423/)
studies encoded mutation and crossover probabilities and their indirect selection. Root 23
tested a token-frequency instance; its negative result does not refute that mechanism.

| Candidate | Full cost and present decision |
|---|---|
| Partial-program feedback versus equal-effort one-shot acquisition | **Pursue, 8–12 h total.** A new test of whether the observed early signal can improve its own acquisition. The result selects feedback or one-shot as the next route. |
| Learned executable abstractions | **Defer.** Extraction, stack semantics, operators, cost controls and a new comparison all need building; end-to-end runtime is unmeasured. I cannot honestly price a complete answer yet. Reconsider after feedback if remaining error suggests missing multi-token dependencies, or a corpus inspection supplies a concrete reusable fragment and a bounded implementation plan. Lack of a plan would then call for writing one, not stopping. |
| Changed inherited-frequency law | **Defer.** Prior plan suggests 5–7 h per complete cycle; the changed procedure itself is unpriced. Reconsider with a specific selectable change or evidence separating selection from drift. Another smaller-noise setting alone is not a reason. |
| Frozen emitted-frequency control K on then-addition | **Defer, about 4–5 h total** (40–60 min expected queue, up to about 1.7 h if capped, plus agents). Reconsider when choosing a representation or making an order-specific claim depends on it. It does not settle whether feedback earns its acquisition cost. |
| More precision for partial C/T ≥1.20 or PA alone | **Decline this block:** roughly 6 h extra queue plus agents for the former, conditional on the point estimate. It would not change the next acquisition choice. |

**Next question for the steward.** Does a short sequence of refits from pre-solution
populations acquire a better frozen decoder than one-shot fitting at the same total source
effort, and does it improve beyond retaining the first fit? This is worth asking because
partial fitting already helps, exact-solver feedback has worked elsewhere in the tree,
and there is substantial remaining headroom. Those observations support a test, not an
assumption of compounding gains. The [plan](../../plans/partial-program-feedback.md) adds
the equal-effort source control and an independently updating token lineage. The steward
sets sizes and the decision rule. Do not spend this slot merely showing that repeated
fitting beats G4 or beats an underfunded first-round fit.

**Owner note disposition.** The sole [owner-heritable-map.md](../../plans/owner-heritable-map.md)
is unchanged since [strategy 1831](../2026-10-08-1831/strategy.md), verified SHA-256
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
There are no new or changed unanswered notes. Reassessment after the partial-program result:

- **Pursued at tested scope; further work deferred:** step 1, inherited op frequencies.
  The bounded result stands. Reconsider at root 23's concrete restart condition, including
  useful frozen acquisition under a changed rule or a demonstrated selection signal.
- **Deferred:** step 2, capture/synonyms. The owner's useful-learning prerequisite for
  inherited frequencies remains unmet. Reconsider after that prerequisite and evidence
  of a limitation reassignment could address; engine validation still needs its own stage.
- **Deferred as proposed:** step 3, competing population-level maps. The partial result
  supplies data for fitting, not a demonstrated way to rank competing maps affordably.
  The adjacent feedback route is pursued but does not fulfill this item. Reconsider actual
  map competition when measured candidate improvements and scoring cost support it.
- **Declined for this block:** free table mutation and ambiguous intermediates. Reconsider
  only as necessary contrasts in a justified reassignment study; they currently answer
  no live decision.

**Allocation and exit.** `research.py status` confirms **5/40 experiments used**, deadline
`2026-10-10T08:12:10`, root balances **01: 0, 10: 2, 23: 0**. With about **35 h left**, allocate
**one existing root-10 slot**, expected **8–12 h total**, including at most **6 h summed queue
timeouts** and the 120-minute preparation limit. Keep root 10's `budget.experiments: 20`.
The remaining slot awaits strategy review. This supersedes the earlier conditional
continuation language; it funds training acquisition only, not a new transfer bank.

Return to strategy after this experiment, or earlier on a build/cost obstacle. The exit
deliverable is an independently scored, decision-sized feedback-versus-one-shot result
with acquisition costs, or the measured reason it cannot be obtained. Review a broad
interval by its resolution cost; do not call it a plateau. A useful result can earn a
separately priced generalization study. No result automatically earns more feedback rounds.
The block leaves approximately 23–27 h of the stated window for the next decision; that
reserve is not an obligation to spend it. No existing questions, digest or briefs are edited.

**What to stop.** Stop automatic exact-solver feedback iterations, collection-horizon
extensions toward complete solutions, precision-only family refinements, and blind
optimizer/decoder/alias-screen sweeps. Do not rerun the inherited σ=0.03 procedure or add
threshold-2 scoring to it. Do not revive helpers or CA to fill idle time. Stop describing
statistical refitting as individual map inheritance, and stop treating an unresolved
parent-enrichment contrast as equality. At the next review, stop the autonomous run if
no candidate's complete answer justifies its remaining cost. That condition is not met
now: the equal-effort feedback question has a measured starting signal and can alter the
program's acquisition strategy within this allocation.
