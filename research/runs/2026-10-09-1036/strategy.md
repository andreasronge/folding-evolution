---
next: proposal
---

Continue **root 10 for one experiment on frozen-fragment reuse**, then review.
Raise only its frontmatter `budget.experiments` **23 → 24**. Expected complete cost:
**5–7 hours**, including agents and queue. The next question is whether a library
adds useful search bias on excluded compositions beyond the simpler chain-block
operator. The [continuation plan](../../plans/fragment-reuse.md) makes this executable.

This review covers the [core question](../../../README.md#core-question),
[digest](../../digest.md), all three roots and their sub-questions, plans and owner
note, recent strategies, decisions and [briefs](../../briefs/2026-10-09-2026-10-09-0843.md),
and the [current ledger](../../briefs/2026-10-08-0812-ledger.md). The task remains to
explain the map's bias and learn whether evolution can acquire a bias useful across
tasks. A faster externally supplied operator answers only part of that question.

**What we have learned.**

- **Arrival and successful search differ.** Root 01's random frequencies predict easy
  tasks and are consistent with folding's fixed-target advantage, but do not generally
  predict evolutionary speed. Cheap joins explained the tested composition advantage.
  Lineage mixing obstructed rare seeded shared forms; self-mating permitted both
  discovery and establishment. Natural single-copy fate and B-helper arrival remain
  unresolved. These constrain interpretation of fragments without justifying another
  helper or threshold experiment ([root 01](../../questions/01-map-bias/question.md)).
- **Selection can acquire transferable token bias.** Root 10's outer-selected token
  multipliers improve fresh search about 2× on withheld compositions; initialization
  and ongoing decoder use both contribute. No useful training-family preference was
  resolved. The tested contextual selection procedures have not established an
  additional reproducible gain; calibrated continuation gave C/T 0.967× [0.871, 1.073].
  This bounds those procedures and starts, not contextual learnability
  ([root 10](../../questions/10-compositional-map-transfer/question.md)).
- **Externally fitted structure is useful and partly transferable.** Exact-solver
  context C beats the restricted token fit T 3.11× on comparison-gate training cells,
  2.60× on its holdouts, and **2.12× [1.86, 2.41] on a bank that was fresh at that
  evaluation**. Cross-shape shrinkage is resolved; its cause and family specificity
  remain open. That bank is now development data, with one alphabet/domain and two
  gates limiting generality ([1548](../2026-10-08-1548/analysis.md)).
- **The tested simpler replacements do not recover C.** Pooled and positional
  frequency projections leave C about 2.4× faster. Randomly recoding the positional
  map to C's mutation width makes it slower while preserving its complete random-tape
  distribution. These results distinguish supply from variation and reject specific
  replacements; C's content and structured coupling remain unseparated
  ([0306](../2026-10-09-0306/decision.md), [0537](../2026-10-09-0537/decision.md)).
- **The latest gain has two parts worth retaining.** On training cells, learned
  fragment edits F beat C **1.57× [1.42, 1.75]**, marginal blocks B 1.60×, and C-chain
  blocks W **1.23× [1.12, 1.36]**. W itself beats C **1.28× [1.17, 1.39]**. Both source
  families favor F/C, but one cell favors W over F. Most fragments are short shared
  syntax; leave-one-out libraries overlap heavily. This supports the procedure on
  training cells, not computational abstractions, acquisition, or reuse across shape
  ([0843](../2026-10-09-0843/analysis.md), code `e347793`).
- **Acquisition remains the largest gap.** Partial-program fitting gives a weaker
  training signal; two feedback updates add only 1.18× [1.01, 1.37] over equal-allocation
  one-shot fitting, with gain over keeping the first fit unresolved. Root 23's tested
  inherited frequencies give no useful frozen bias: uniform/inherited speed 0.33×
  on sum and 0.73× on max, whose upper bound is 1.06×. Linkage helps max relative to
  shuffled ancestry without establishing usefulness over uniform
  ([2116](../2026-10-08-2116/analysis.md), [1046](../2026-10-08-1046/analysis.md)).

**Root priorities.** Root **10** has the highest immediate value: the fragment result
can change whether acquisition should target a separate repertoire or reuse the existing
chain with a better edit operator. Root **23** remains central to endogenous acquisition,
but its restart condition is unmet; an externally extracted library is not a new
selectable inherited signal. Root **01** supplies the supply/variation/establishment
distinction and the cheap-join warning, without needing new allocation. Older folding,
CA repair and runtime plasticity offer no more direct, prepared answer at a justified
complete cost now. No new root is needed; retain the one permitted opening.

**Current line versus different mechanisms.** I searched the literature for this
review. [Keijzer, Ryan and Cattolico, *Run Transferable Libraries* (2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf)
transfers learned functions between GP runs. [Ellis et al., *DreamCoder* (2020
preprint)](https://arxiv.org/abs/2006.08381) learns symbolic abstractions together with
a neural search guide. These are precedents for retaining reusable units. Our narrower
procedure extracts literal windows externally and inserts them into fresh searches;
it neither implements their abstraction learners nor demonstrates autonomous acquisition.
The papers motivate the question, not an expected effect in this harness.

The strongest immediate alternative is **local editing without a fragment library**.
W already shows a gain using C alone. A suffix-preserving point mutation could test
whether avoiding downstream re-decoding explains W's advantage. That changes the
variation operator without acquiring additional repertoire content. It is mechanistically
different from library extraction and now has repository evidence, although W/C bundles
locality with chain-sampled content. Its proposed 3–4-hour explanation study is cheaper,
but a reuse comparison carrying W can first decide whether the library adds anything
worth explaining. A W mechanism study is most valuable if W remains useful and F's
increment is tightly small; it is not the automatic next control.

The owner's **inherited modifiers** change the credit mechanism instead. In
[Stephens et al., *Self-adaptation in evolving systems* (1998)](https://pubmed.ncbi.nlm.nih.gov/9847423/),
encoded mutation/crossover probabilities can be indirectly selected through their
descendants. This motivates inheritance rather than external extraction. Root 23
tested one token-frequency instance and limits that instance, not the broader idea.
A changed inheritance procedure would address the core acquisition gap more directly,
but currently lacks a measured new selection signal and a complete study price.

| Candidate | Decision and full-cost judgment |
|---|---|
| Frozen fragment reuse, with F/W and F/C | **Pursue, 5–7 h.** Training evidence exceeds the prior expectation; excluded compositions can change the representation investment. Existing code and libraries make a complete answer plausible. |
| Explain W using suffix-preserving point mutation | **Defer, provisional 3–4 h.** Useful rival mechanism; first establish W's and F's usefulness beyond training. New-arm cost still needs measurement. |
| Acquire fragments during population search | **Defer pending reuse.** Potentially consequential, but online harvesting is a changed acquisition procedure; it needs an equal-cost frozen-usefulness comparison. Simple harvesting would still be algorithmic extraction, not inherited map evolution. No automatic build follows reuse. |
| Revised inherited frequencies / competing map populations | **Defer.** No revised, measured acquisition signal yet. The previous inheritance budget does not price a redesign. Reconsider at the owner's conditions below. |
| More projections, random recodings, partial feedback, or family-preference precision | **Decline this block.** Their current answers do not leave a decision valuable enough to justify repetition; partial-feedback margin resolution was priced around 600 lineages. |
| Another fresh task shape or a larger abstraction engine | **Defer.** The immediate question is incremental library value. Both alternatives add construction cost before that value is established. |

**What the steward should ask next.** Do frozen fragments from the training solvers
make fresh searches on excluded compositions usefully cheaper than both C and W,
especially when addition moves to the then-branch? A positive makes a repertoire an
acquisition target; a tight small increment favors the simpler W procedure. This is
a representation choice with consequential outcomes in either direction.

Use the [reuse plan](../../plans/fragment-reuse.md); the steward supplies the design.
Keep the cross-shape result separate from the within-shape reference. These are reused
development banks, and shared syntax can remain useful on both: success would establish
reuse of this procedure, not distinguish syntax from functional modularity. Likewise,
an unresolved F/W contrast is not evidence that block editing explains the gain.
Do not turn the latest decision's informal “collapse to F≈W” into that inference.
The price of resolving a broad interval must return to strategy.

**Owner note.** The only note is
[owner-heritable-map.md](../../plans/owner-heritable-map.md). Its SHA-256 is
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`, unchanged since
[strategy 0826](../2026-10-09-0826/strategy.md), which answered it. There are **no new
or changed unanswered owner notes**. Current dispositions and reconsideration points:

- **Pursued at tested scope; continuation deferred:** step 1, inherited frequencies.
  The bounded negative result stands. Reconsider a changed rule with useful frozen
  acquisition or measured selection-versus-drift evidence meeting root 23's restart
  condition, or a specific frequency control needed by a later inheritance study.
- **Deferred:** step 2, capture and synonyms. The owner's useful inherited-learning
  prerequisite remains unmet. Reconsider after it is met and reassignment addresses
  a demonstrated limitation, with engine validation priced separately.
- **Deferred:** optional step 3, competing population-level maps. Outer-selected token
  maps already worked; useful additional context was not established that way.
  Reconsider with an affordable candidate-ranking signal and complete learning/reuse
  price. Fragment extraction does not fulfill this item.
- **Declined for this block:** free table mutation and ambiguous intermediates.
  Reconsider only as necessary contrasts in a justified reassignment study.

**Allocation and exit.** `research.py status` reports **10/40 experiments used**, all
roots exhausted, deadline **2026-10-10T08:12:10**; the supplied remaining window is
about **22 h**. Grant **one root-10 slot**, budget **24**, through the next strategy
review. Leave root 01 and root 23 unchanged. Question 32's one-slot child budget is
also exhausted: the steward must allocate the new slot to its continuation (update
the child's budget or create a reuse sub-question) before proposing. This strategy
does not edit existing question text or child budgets.

The measured training queue took 74 minutes. The steward's reuse scenario costs
about 106 scoring minutes for F/W/C, about 10 minutes library validation/reporting,
and 2.5 agent hours: roughly **4.5 h**, extrapolated from training. Allow **5–7 h total**
for preparation, reviews, queue, analysis and contingency; at most **4 h summed queue
timeouts**, with **120 min preparation**. Price harder targets and decision-relevant
precision before admission. Corpus collection is sunk for execution but still belongs
in the eventual acquisition-cost accounting. This block leaves about **15–17 h** for
review and a separately justified continuation; it does not reserve another experiment.

Return to strategy after the reuse result, or sooner on a measured validity, build or
complete-cost obstruction. Useful F/W and F/C across shape earn consideration of an
acquisition plan. Tight small gains or harm end expansion of this extractor at that
scope; broad uncertainty gets a resolution price. No additional controls, harvesting
engine or fresh bank are automatically funded.

**What to stop.** Stop the frequency/position projection and random-recoding sequence,
unchanged feedback rounds, longer partial-collection horizons, blind optimizer sweeps
and precision-only family-preference runs. Do not repeat root 23's unchanged procedure
or score its threshold-2 transfer. Do not revive helpers or CA to fill available time.
Stop using a training-cell library win as a reason to keep elaborating externally
supplied machinery: this reuse stage must change the acquisition target or end that
expansion. End the autonomous run when no complete candidate can change a worthwhile
decision within the remaining time. That condition is not met now: a concrete,
bounded reuse question has both a plausible benefit and an informative failure outcome.
