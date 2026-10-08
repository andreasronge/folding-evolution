---
next: proposal
---

Open [23-heritable-variation-bias](../../questions/23-heritable-variation-bias/question.md)
for a bounded test of the owner's first step: **can an inherited token-generation bias
acquire useful information through ordinary program selection, and retain that value when
the programs are discarded?** Use the new [plan](../../plans/heritable-variation-bias.md).
Do not buy another feedback iteration or precision extension on root 10's present bank.

**What we have learned.** The [core question](../../../README.md#core-question) asks how
maps bias discovery and whether the bias can evolve to fit related tasks. Reading the
[digest](../../digest.md), both roots and their children, plans, recent decisions and
[last run's summary](../../briefs/2026-10-05-2225-auto-summary.md) gives this answer:

- Bias matters, but exact-solver frequency alone does not predict search speed across
  these harnesses. Folding's fixed-target gains were consistent with greater solver supply;
  TAG evolution sometimes substantially outperformed its random-search expectation.
  Cheap joins explained the early composition advantage. The helper studies separated
  arrival from establishment: selected-mate crossover obstructed rare seeded shared forms,
  self-mating removed that barrier, and natural B-helper arrival remained unresolved.
- Externally fitted threshold frequencies improved fresh search about 4× over uniform;
  a simple hand-set scaffold performed comparably. Selection of token multipliers in an
  outer loop then transferred about 2–3× on withheld compositions. Both starting programs
  and ongoing decoder use contribute, about 1.3× each conditional on the other. This does
  not isolate mutation, crossover or useful-part supply.
- Search-selected context has not added a resolved increment in the procedures tried.
  The calibrated [1137 comparison](../2026-10-07-1137/analysis.md) had a working token
  learner and C/T 0.967× [0.871, 1.073]. Useful context itself is not ruled out:
  [1707's external corpus fit](../2026-10-07-1707/analysis.md) beat the restricted token
  fit 1.365× [1.288, 1.446] on training and 1.293× [1.213, 1.378] on withheld cells.
- One [feedback refit](../2026-10-07-1924/analysis.md) improved over its parent by
  1.404× [1.347, 1.464] on training and 1.289× [1.204, 1.381] on withheld cells, and
  beat a refreshed G4-corpus fit. Collecting under the learned map matters as a procedure;
  yield, diversity and tape content are still bundled.
- [2156](../2026-10-07-2156/analysis.md) found that feedback increased context's relative
  advantage on training, 1.169× [1.093, 1.250], mostly in branch-else (BE). Token-only
  fitting also gained 1.20×. The withheld interaction is unresolved, 1.087× [0.984, 1.200].
  These context rows reuse 1924, so this is a completed comparison, not independent
  replication. No broad family-specific adaptation is established: one repeatedly inspected
  bank, three withheld cells, only one BE cell. External fitting is not inherited map evolution.

**Which roots matter now.** Root 10 remains the strongest evidence about transferable
assembly bias. Its important remaining questions concern task generalization and selection
of that bias, rather than whether another fit gains a few percent. Root 01 supplies the
arrival/establishment foundation and the measured frequency controls. Its parked helper,
rarity-ladder and threshold-veto refinements have no new decision-changing evidence.

Root 23 addresses a different selection unit: the bias travels with a program individual,
and affects its offspring. Root 10 explicitly asks about improvement beyond token frequency;
08/09 concern externally supplied frequency vectors. Keeping inheritance in its own root
prevents a successful modifier experiment from being mistaken for learned contextual
development. It tests the simplest variation-distribution part of the core question;
token meanings and the developmental decoder remain fixed.

**Current line versus a different mechanism.** The corpus-feedback line is close to
probabilistic program-generation methods: Salustowicz and Schmidhuber's
[PIPE (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/) updates a program distribution
using successful programs. Our full-tape, previous-token fit and frozen-map transfer test
are particular implementations and measurements of that broad idea, not evidence of a
new class of learning.

The owner's alternative is **self-adaptation of variation parameters**. Stephens et al.,
[Self-Adaptation in Evolving Systems (1997)](https://arxiv.org/abs/adap-org/9708002),
study encoded mutation/crossover probabilities without a direct fitness reward for those
parameters. Serpell and Smith,
[Self-adaptation of mutation operator and probability for permutation representations
(2010)](https://doi.org/10.1162/EVCO_a_00006), test inherited choices of mutation operators
and parameters. These papers motivate the selection route; neither demonstrates transferable
token-frequency learning in this repository. Here the new evidence would be a frozen bias
that helps fresh programs, with ancestry broken as a control and the manual scaffold as
the practical benchmark. Weight movement alone could be drift or hitchhiking.

| Candidate | Decision and full-cost judgment |
|---|---|
| Inherited token frequencies | First. A bounded implementation and replicated test could establish or limit a selection route we have never tried. Reserve 10–14 h including agent work; measure actual cost before the substantive queue. |
| Fresh bank with several holdouts per family | Next strategic alternative. I agree with the last summary that this matters more than refining the old holdouts. It needs a specified semantic contrast, screening and learning; three earlier screens show why baseline feasibility alone is insufficient. Reconsider at root 23's review, with roughly 34 h still available if this block uses its ceiling. |
| C3, or ~90 new lineages to resolve the 1.09× interaction | Defer. Roughly 1–3 queue hours plus a cycle of agent work is affordable, but would refine external fitting on the same bank without answering inheritance or task generality. Reconsider if a new bank needs the iterative learner, or iteration stability becomes necessary to a chosen method. |
| Active-token/start-row intervention; another contextual outer optimizer | Defer. Potentially informative, but instrumentation or another 4–6 h learning queue should serve a concrete next decision. Reconsider if root 23 fails and the corpus/selection gap remains the best route. |

**Owner note response.** The only `owner-*.md` is
[owner-heritable-map.md](../../plans/owner-heritable-map.md), written 2026-10-06;
reviewed SHA-256 `439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
I found no earlier strategy explicitly answering this note. **Pursued, bounded to step 1.**
The new plan carries its fixed-meaning constraint, uniform and hand-set controls, adaptation
cost accounting and 120-minute preparation limit. Step 2 (capture/synonyms) is **deferred**
until inherited frequencies show useful frozen transfer and a concrete limitation that
reassignment could address. Step 3 (population-level maps) is **deferred**: root 10 has
already tested that selection unit for token/context adaptation; reconsider only for a
changed learning signal or fresh bank. Step 4 (free table mutation) and ambiguous
intermediates are **declined for this block**: they explain no current observation and
require more machinery. Reconsider only as necessary controls for a funded reassignment
study. Matching the scaffold would demonstrate acquisition but would not justify escalation
to the owner's more expensive steps.

**Next for the steward.** Ask whether selection-linked inheritance produces a frozen
frequency bias that speeds fresh searches beyond an ancestry-broken control, and whether
it improves on the scaffold. Start with the reviewed TAG threshold harness so the learning
mechanism changes without simultaneously replacing the executor and bank. This is a
mechanism study on a development bank, not fresh compositional-transfer evidence. The
plan specifies what to build; the steward sets the primary contrast, replication and
decision rule. Do not equate a population solving its training task with its bias learning.

**Allocation and exit.** `research.py status` reports the new autonomous run
`2026-10-08-0812`, 0/40 experiments, deadline `2026-10-10T08:12:10`; the previous
22:25 deadline in 2156's decision is historical. Existing roots remain at 01: 6/6 and
10: 15/15 used. Open root 23 with **2 experiments**, using one of the two permitted new
roots. No existing question field is changed. Reserve at most 8 queue hours across the
block, plus about 6 h for preparation, review, analysis and contingency (10–14 h total).
Each queue still respects its own cap and the actual remaining deadline.

Review after a feasibility-only first result, any build/cost failure, or the two-slot
learning/transfer block, whichever comes first. Exit with an inherited-transfer result,
a useful bound on this procedure, or a measured obstacle and price for resolving it.
An unresolved but affordable decision-sized extension returns to strategy; it is not a
null. The other 38 run slots are unallocated. No automatic tuning or engine expansion.

**What to stop.** Stop automatic C3/C4 progression, repeated scoring for small family
preferences on the old three cells, optimizer variations without a changed selection
argument, and helper/shortcut refinements. Keep 08/09 parked: this plan does not require
resolving their shortcut mechanism. Stop this inherited-frequency line if its only
demonstrated benefit is rediscovering the scaffold with no practical increment worth
its cost; record that acquisition result without escalating it. A worthwhile bounded
inheritance test remains, so `next: stop` is not justified now.
