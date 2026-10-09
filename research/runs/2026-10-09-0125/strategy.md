---
next: proposal
---

Use root 10's **one remaining experiment** to ask whether its transferred C/T gain
survives matching emitted token frequencies. Then review. Stop extending partial-program
feedback for now. The [frequency-control plan](../../plans/transferred-context-frequency-control.md)
costs **4–5 h total** and can decide whether the next learner needs structure beyond a
G4-based frequency map. I have also written a bounded
[executable-fragment plan](../../plans/learned-executable-fragments.md), so that alternative
can be considered concretely at the next review. It is not yet allocated.

**What the program has learned.** The [core question](../../../README.md#core-question)
asks how a developmental map biases discovery and whether that bias can evolve to fit
tasks. Read together, the [digest](../../digest.md), question tree, plans, recent decisions
and [run ledger](../../briefs/2026-10-08-0812-ledger.md) give a substantial but incomplete answer:

- **Arrival, discovery and establishment differ.** Random-genome frequencies explain easy
  tasks and much of folding's fixed-target advantage, but generally fail to predict search
  speed. Cheap joins explained the tested composition advantage. Lineage mixing blocks
  establishment of rare seeded shared forms; self-mating removes that barrier while
  retaining discovery. Natural single-copy fate and B-helper arrival remain unresolved.
  These are scoped mechanisms, not a general superiority of developmental encodings
  ([root 01](../../questions/01-map-bias/question.md)).
- **Evolution can acquire reusable token bias.** Outer-selected token maps transfer about
  2× on compositions; both starting programs and ongoing decoder use contribute.
  Family preference remains unresolved. Four contextual selection procedures established
  no additional contextual gain; calibrated continuation gave C/T 0.967 [0.871, 1.073]
  for its starts, effort and mixing rule. This limits those procedures, not selection's
  ability in principle ([root 10](../../questions/10-compositional-map-transfer/question.md)).
- **External fitting finds a stronger transferable target.** Exact-solver context fitting
  gave C/T 3.11× on comparison-gate training cells, 2.60× on its protected development
  holdouts, and **2.12× [1.86, 2.41] on one fresh then-addition bank**. Cross-shape shrinkage
  is resolved. These results concern one alphabet/domain and a capped endpoint; the fresh
  bank has only two gate types. Pooled frequencies were controlled only on the older bank
  ([1548](../2026-10-08-1548/analysis.md)).
- **Incomplete populations supply useful fitting data, but more feedback has weak returns.**
  Partial C/G4 was 1.62× in two scoring blocks. The latest equal-allocation feedback
  comparison gave F/O **1.18× [1.01, 1.37]**, with improvement resolved on BE and unresolved
  on PA. F versus keeping the first fit was 1.16× [0.99, 1.36]; F remains about three times
  costlier per search than the exact-solver fit. The latter's acquisition cost is higher.
  Estimated repayment of F's extra acquisition is roughly 12,350 searches on these same
  cells. This supports a small procedure-specific effect, not a compelling next acquisition
  investment. Family differences were not tested directly; both-solved analyses condition
  on success ([2116 decision](../2026-10-08-2116/decision.md)).

The other direct acquisition route, [root 23](../../questions/23-heritable-variation-bias/question.md),
found no useful frozen inherited bias under its tested rule: uniform/inherited cost
0.33 [0.21, 0.53] on sum and 0.73 [0.50, 1.06] on max. Linkage helped max relative to
shuffled ancestry without establishing improvement over uniform. Drift was not isolated.
The main gap remains **how evolution acquires the useful contextual target**; repeated
external fitting has not answered it.

**Which roots matter now.** Root **10 comes first**: its strong transfer result makes
the content of the learned bias consequential for the next representation and learner.
Root **23 remains conceptually central but parked**; no changed rule with a measured
selectable signal has emerged. Root **01 supplies the mechanism foundation**, but its
parked threads have no new evidence that makes another experiment preferable. Older
folding, CA repair and runtime plasticity remain background; they do not presently offer
a comparably concrete test of transferable bias acquisition. Existing root 10 serves
both the immediate control and the fragment candidate. Leave the one permitted root
opening unused.

**Current line against different mechanisms.** Literature searched in this review:
[Salustowicz and Schmidhuber, *Probabilistic incremental program evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/)
updates a program-generating distribution from successful programs. The present corpus
line is related distribution estimation: external statistical updates over fixed units.
Further partial-feedback rounds would mostly refine the modest result already obtained.

[Ellis et al., *DreamCoder* (2020 preprint)](https://arxiv.org/abs/2006.08381)
learns symbolic abstractions as well as a search guide. A small repository analogue would
extract executable fragments from training solvers and use them as coordinated edits.
This changes the units of variation. My hypothesis is that useful dependencies could then
be introduced together instead of rediscovered through token-wise edits. The paper does
not establish that benefit here. Root 01's cheap-join result requires controls for edit
size, primitive supply and execution cost. The new plan limits the first candidate to
literal fragments and the existing executor; it does not propose a DreamCoder port.

The owner's inherited-frequency mechanism is different again: descendants propagate
variation parameters without a corpus fit. [Stephens et al., *Self-adaptation in evolving
systems* (1998)](https://pubmed.ncbi.nlm.nih.gov/9847423/) studies this indirect selection
of encoded mutation/crossover parameters. The repository's negative token-frequency
instance leaves that broader mechanism open, but gives no measured redesign direction.

| Candidate | Decision and full cost |
|---|---|
| Frozen emitted-frequency control K on then-addition | **Pursue, 4–5 h including agents.** Distinguishes whether this simpler map can reproduce the strongest cross-shape result; no new acquisition needed. |
| Learned executable fragments | **Plan now; defer execution to next review.** Provisional 11–16 h for construction, training comparison and development-bank reuse, with measured pricing required. Greater mechanistic change, greater implementation and control risk. |
| More partial-feedback rounds or a precision run | **Decline.** The 1.15× margin alone was priced near 600 lineages, about 123 queue hours; another short round would not justify its full acquisition and review cost. |
| Changed inherited-frequency law | **Defer.** Earlier complete-cycle allowance 5–7 h; a redesigned procedure remains unmeasured. Reconsider with a specific selective mechanism and training-only evidence that distinguishes useful acquisition from drift/hitchhiking. |
| Second fresh shape or another contextual optimizer | **Defer.** Complete cost unmeasured; neither currently answers a more decisive question than what the existing successful map carries. |

**Next question for the steward.** Can the saved G4-based token-multiplier control K,
matched to C's pooled emitted frequencies, reproduce C's performance on the then-addition
compositions? All 16 source corpora contain C/T/K. I recomputed their finite 32-position
marginals: maximum absolute C–K mismatch is **0.000029**. The control is ready to validate
and score, not merely a proposed implementation.

If K is sufficient within a useful bound, prioritize acquiring its frequencies before
paying for additional contextual machinery. If C retains a worthwhile advantage, pooled
frequencies are insufficient for this replacement; inspect executable corpus structure
and consider the fragment plan at its full price. This is not a binary verdict on token
order: K retains G4 context, and pooled matching does not match positions, solver supply
or variation neighborhoods. A positive C/K does not prove fragments will help. Keep C/T
visible if K is weak, and retain an unresolved outcome. Then-addition is now development
data, so this is a mechanism follow-up, not renewed fresh-bank evidence.

**Owner note disposition.** The only note,
[owner-heritable-map.md](../../plans/owner-heritable-map.md), is unchanged since
[strategy 2116](../2026-10-08-2116/strategy.md): verified SHA-256
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
There are no new or changed unanswered notes. Current dispositions remain explicit:

- **Pursued at tested scope; further work deferred:** inherited op frequencies, step 1.
  Reconsider with root 23's changed-rule/selectable-signal evidence or a specific need
  for its frequency-only control. External partial fitting does not meet that condition.
- **Deferred:** capture/synonyms, step 2. The owner's useful inherited-learning prerequisite
  is unmet. Reconsider after it is met and reassignment addresses a demonstrated limitation;
  engine validation would still need its own stage.
- **Deferred:** competing population-level maps, optional step 3. A worthwhile fitted
  target exists, but cheap, reliable selection among map candidates remains unestablished.
  Reconsider with a measured candidate-ranking improvement and complete cost. Corpus
  feedback and fragment extraction do not fulfill this item.
- **Declined for this block:** free table mutation and ambiguous intermediates. Reconsider
  only as necessary contrasts in a justified reassignment experiment.

**Allocation and exit.** `research.py status` confirms **6/40 experiments used**, root
balances **01: 0, 10: 1, 23: 0**, deadline `2026-10-10T08:12:10`. With the stated **31 h
remaining**, allocate the existing root-10 slot through the next review; keep
`budget.experiments: 20`. Expected total **4–5 h**, at most **3 h summed queue timeouts**,
including replay/timing, and the 120-minute preparation limit. The latest measured harness
supports a projected 40–60 min K queue, about 1.7 h if all searches cap; measure K itself
before admission. The balance of the window is a reserve, not a spending target.

Return to strategy after this comparison, or earlier if validity, precision or full cost
cannot support a decision. The exit deliverable is an interpretable sufficiency estimate
for K and the resulting representation choice, or its measured obstruction. Do not extend
the queue merely to use the slot. The fragment plan receives no experiment allocation
until its scientific value and complete staged price are reviewed.

**What to stop.** Stop partial-feedback extensions, horizon sweeps toward exact-solver
collection, automatic exact-solver feedback, and precision-only family refinements. Do
not repeat the inherited σ=0.03 procedure, score its threshold-2 transfer, or revive helpers
or CA to fill time. Keep statistical refitting distinct from inherited map evolution.
At the next review, stop the autonomous run if no candidate justifies its entire remaining
cost. That condition is not met now: the ready sufficiency test can change the next map
class, and the more ambitious alternative now has a bounded plan rather than an indefinite
deferral.
