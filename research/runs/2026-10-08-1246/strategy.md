---
next: proposal
---

Return to [root 10](../../questions/10-compositional-map-transfer/question.md): **does the
useful assembly bias fitted from solver tapes survive new compositions, beyond token
fitting, with several protected targets in each family?** Fund one bounded first stage
of the [comparison-gated transfer plan](../../plans/comparison-gated-transfer.md), then
review. Keep root 23 parked. A complete new-bank comparison could change our answer to
the core question enough to justify its provisional 12–18-hour cost; another small
improvement on the old bank would not.

**What the program has learned.** The [core question](../../../README.md#core-question)
concerns discovery bias and whether that bias can evolve to fit related tasks. The
[digest](../../digest.md), question tree, plans, latest decisions and
[recent briefs](../../briefs/2026-10-08-2026-10-08-1046.md) support these conclusions:

- Maps affect arrival and establishment separately. Random-genotype frequency explains
  easy behaviours and much of folding's fixed-target advantage, but does not generally
  predict evolutionary search speed. Cheap joins explained the early composition advantage.
  Mixing lineages obstructed rare seeded shared forms; self-mating removed that barrier.
  Natural B-helper arrival remains unresolved
  ([01](../../questions/01-map-bias/question.md)). These are scoped mechanisms, not a
  universal benefit of development or modularity.
- Useful token biases transfer. External threshold fits give roughly 4× speed-ups over
  uniform, with the hand scaffold comparable within the tested broad margin. Outer-selected
  token multipliers give about 2–3× on withheld compositions. Starting programs and ongoing
  decoder use both contribute, with overlapping benefits. No convincing matched-family
  advantage has been established on the three reused composition holdouts
  ([16](../../questions/10-compositional-map-transfer/16-crossed-family-adaptation/question.md),
  [17](../../questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md)).
- Solver tapes carry useful information beyond pooled token frequencies. External context
  fitting beat restricted token fitting by 1.365× [1.288, 1.446] on training and 1.293×
  [1.213, 1.378] on withheld cells ([1707](../2026-10-07-1707/analysis.md)). One feedback
  refit added 1.40× / 1.29× ([1924](../2026-10-07-1924/analysis.md)). Feedback increased
  context's relative advantage on training, mostly BE; its withheld interaction remains
  unresolved at 1.087× [0.984, 1.200] ([2156](../2026-10-07-2156/analysis.md)), reusing
  1924's context rows. The calibrated selection-based context procedure instead gave
  C/T 0.967× [0.871, 1.073] ([1137](../2026-10-07-1137/analysis.md)). External fitting
  succeeds where these selection procedures have not demonstrated a contextual increment.
- Inherited frequencies did not become useful frozen biases under root 23's tested law.
  [1046](../2026-10-08-1046/analysis.md) completed all 80 acquisitions and 2,752 frozen
  searches. Uniform/inherited cost was 0.33 [0.21, 0.53] on sum and 0.73 [0.50, 1.06]
  on max; the hand scaffold was 11.9× and 5.75× cheaper. Linkage helped relative to broken
  ancestry on max, 1.58× [1.04, 2.36], without establishing improvement over uniform.
  This bounds σ = 0.03, the 48 × 128 schedule and extraction rule on training targets.
  It neither refutes self-adaptation nor identifies drift as the cause. A small max gain
  remains compatible with its interval; “at best equal” in the analysis is too strong.

**Root priorities.** Root 10 now matters most: it contains the strongest positive evidence,
but task replication is narrow. Multiple protected compositions can distinguish reusable
assembly information from a benefit peculiar to the screened bank. Family specificity is
separate; generic contextual transfer would still be valuable. Even a positive from this
external fit would leave evolutionary acquisition of context open.

Root 23 remains conceptually important because per-individual inheritance tests another
acquisition route, but its latest result does not meet its reopen condition. Root 01
supplies the arrival/establishment foundation; none of its parked questions gained evidence
requiring a restart. Older folding, chem-tape plasticity and CA results remain background.
The chosen question fits root 10; no additional root is needed.

**Current line versus a different mechanism.** Literature searched for this review confirms
the distinction. [Stephens et al., *Self-adaptation in evolving systems* (1998)](https://pubmed.ncbi.nlm.nih.gov/9847423/)
encode mutation and crossover probabilities that are indirectly selected through descendants.
Root 23 applies this idea to token generation. A lower-noise law or different exposure
could change its result, but needs fresh acquisitions and frozen scoring. The max linkage
signal motivates a hypothesis, not a demonstrated direction of useful acquisition.

The alternative learns a distribution directly from successful programs.
[Salustowicz and Schmidhuber, *Probabilistic incremental program evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/)
generate programs from an adaptive distribution and refine it using the best program.
Our corpus estimator and sequential representation differ, but the direct statistical
learning signal is related. It does not depend on persistent modifier–program association.
My inference from the repository evidence is that testing this already useful signal on
a new bank is worth more now than another inheritance setting. Neither paper establishes
transfer in our system.

| Candidate | Decision and full cost |
|---|---|
| One-shot corpus context versus token fitting on comparison-gated compositions | Pursue. Provisional 12–18 h including construction, collection, scoring and agents; first 4–6 h allocated now. Tests task generality and separately training-family dependence. |
| Changed inherited-frequency law | Defer. Roughly 5–7 h per complete cycle is a planning allowance from recent runs, unpriced for a changed law. Reconsider with a specific selection argument and cheap evidence distinguishing it from drift/hitchhiking. |
| Another contextual outer optimizer | Defer. Earlier 4–6 h learning queues plus agent work did not establish a contextual increment. Reconsider when a measured learning signal or representation changes the acquisition argument. |
| C3, old-bank interaction precision, active-token/start-row dissection | Defer. More scoring may take only 1–3 queue hours plus a cycle; instrumentation adds work. Reconsider if broader transfer makes one of these explanations decisive. |

**Next for the steward.** Ask whether reducer-to-reducer conditions provide a usable,
affordable test of contextual transfer with at least two distinct protected behaviours
per family. The ready plan replaces sign conditions with comparisons while retaining the
executor and alphabet. This addresses the semantic restriction that defeated earlier BE
splits; it does not assume longer programs will work.

Reuse the bank, search and corpus code on `research/main`. Establish the semantic split
and development-only collection/scoring costs, then price the complete replicated
context/token comparison. Keep the fitting rule from the successful one-shot study.
Protect holdouts from all performance screening, including baseline timing. The steward
supplies the proposal and primary rule. The stage must deliver a continuation decision,
not just runnable code; a tiny unresolved development comparison is not a negative about
context. Training-family contrasts and absolute improvement remain separate questions.

**Owner note.** The sole [owner-heritable-map.md](../../plans/owner-heritable-map.md)
is unchanged since [1046's response](../2026-10-08-1046/strategy.md), verified SHA-256
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
There are no new or changed unanswered notes. Its disposition after the result is:

- **Pursued, completed at tested scope:** step 1 returned a bounded negative for useful
  frozen acquisition. Further inheritance work is **deferred** until root 23's measured
  selection-signal condition is met or another study needs its frequency control.
- **Deferred:** capture and synonyms. The owner's “only if step 1 shows the map can learn
  something” condition has not been met in useful frozen performance. Reconsider after
  useful acquisition/transfer, credible value beyond the scaffold, and a limitation that
  reassignment could address. Engine validation remains a separate stage.
- **Deferred:** population-level maps. Root 10 already tested outer selection; today's
  external fitting is not another test of it. Reconsider after broader transfer establishes
  a worthwhile target and a changed learning signal makes selection affordable.
- **Declined for this block:** free table mutation and ambiguous intermediates. They
  answer no current decision. Reconsider only as necessary contrasts in a funded
  reassignment study.

**Allocation and exit.** `research.py status` reports run `2026-10-08-0812`, **2/40
experiments**, deadline `2026-10-10T08:12:10`; the assignment gives about **43 h remaining**.
All roots had zero balance. Raise only root 10's frontmatter `budget.experiments`, **15 → 16**.
Roots 01 and 23 remain unchanged. Open no new root, leaving the one permitted opening unused.
This one-slot block lasts through the next strategy review: expected **4–6 h total**, at
most **3 h of queue timeouts**, including preparation, review, analysis and contingency in
the total. A probe instead has the usual 60-minute timeout-sum limit and descriptive status.
Keep the 120-minute prepare limit.

Exit after the first stage, or earlier after a build/cost obstacle, with either a frozen
eligible bank and measured price for a decision-sized transfer study, or a specific
semantic, search or cost obstacle. No automatic second experiment. The projected
continuation is another 8–12 h, subject to review; the full 12–18 h leaves roughly 25 h
of the stated window. These are allowances, not measured new-bank rates. Require
scientific value as well as tractability before allocating transfer.

**What to stop.** Stop the present inherited-frequency procedure and its threshold-2
extension: its training usefulness did not warrant transfer scoring. Stop automatic
feedback iterations, small-preference refinement on the old holdouts, modifier/optimizer
sweeps, and helper/shortcut refinements without new evidence. Do not relax the new bank
back to one BE holdout or launch exhaustive deeper alias enumeration merely to rescue it.
If this candidate fails, review its obstacle and alternatives at their full cost rather
than automatically expanding the alphabet. Stop the autonomous run when no alternative
could change a consequential belief within the time left. That is not the present
situation: the planned broader transfer test merits this bounded first step.
