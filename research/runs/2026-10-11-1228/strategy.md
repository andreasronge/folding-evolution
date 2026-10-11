---
next: proposal
---

Fund **one development experiment removing the semantic library's top-16 cap**,
then review strategy. The question is whether useful search bias is already in
the evolved source programs but discarded by library selection. This earns one
bounded test; it does not earn an extractor sweep or protected scoring yet.

This review uses the [core question](../../../README.md#core-question),
[digest](../../digest.md), all three roots and their child questions/reopening
conditions, the plan set and owner note, and the
[current ledger](../../briefs/2026-10-10-1419-ledger.md), decisions and briefs
through [1129](../2026-10-11-1129/decision.md). `research.py status` reports
**13/40 experiments used**, root 10 **43/43**, roots 01 and 23 with no remaining
allocation, and a deadline of **2026-10-12 14:19:15 Europe/Stockholm**. About
**26 h remain**. No new root is needed; both new-root allowances remain unused.

**What the program has learned.**

- Map bias affects discovery, but random-program frequency is an incomplete
  account of evolution. It predicts easy behaviours better than hard discovery.
  Cheap joins explained the tested compositional advantage; lineage mixing
  prevented rare shared forms from establishing. These are specific map/operator
  effects, not evidence that developmental encoding generally beats direct GP
  ([root 01](../../questions/01-map-bias/question.md)).
- Evolution's own solutions contain useful transferable information. Externally
  fitted context beats token-only fitting, including about **2.1×** on a fresh
  composition shape; pooled and positional frequency replacements and random
  mutation widening did not reproduce its advantage. Fragments added speed,
  and cheaper acquisition retained useful transfer. Outer selection learned
  token biases but the tested contextual extensions added no resolved benefit.
  External fitting, outer selection and inherited learning remain distinct
  ([root 10](../../questions/10-compositional-map-transfer/question.md)).
- Family information is present: DG-acquired tape biases were about **3×**
  cheaper than TS-acquired biases on DG; the reverse preference was unresolved.
  Both table and library carried useful contributions. But under matched
  restarts, plain tree GP used about **a fifth fewer evaluations** than A8;
  A8 retained a worker-time advantage. A win against G4 alone no longer chooses
  a competitive method ([42](../2026-10-10-2001/decision.md),
  [44](../2026-10-11-0024/analysis.md)).
- Tree-source libraries reduced evaluations to **0.39×** of restarted tree GP
  on DG and **0.25×** on a fresh gate-sum shape. Learned arrangement mattered
  strongly where a predicate matched; on other splits rearranged donors
  retained the gain within the tested margin. A fixed sum prior then beat
  acquired TS libraries on those latter splits: cost ratio **0.85 [0.76, 0.96]**,
  with acquisition never repaid against it through 200 searches. That limits
  the practical acquisition case there, not all context or predicate evidence.
  Libraries also harmed easy native targets
  ([45](../2026-10-11-0150/analysis.md),
  [46](../2026-10-11-0348/analysis.md),
  [47](../2026-10-11-0524/decision.md),
  [49](../2026-10-11-0833/decision.md),
  [51](../2026-10-11-1019/decision.md)).
- **The latest order-helper result is a probe, not a new belief.** On six
  development cells, the literal library acquired no order helpers and was
  slower than R-tree; semantic pooling was unresolved from R-tree. The supplied
  order prior was about **20× cheaper**. Yet 63% of source solvers contained
  their own helper, and semantic pooling had 49 recurrent admissible
  helper–build cases, of which **44 were discarded by the cap**. Larger or
  nonrecurring forms remain separate limits. The post-hoc advantage in builds
  containing a needed helper is unresolved and cannot establish usefulness
  ([1129 analysis](../2026-10-11-1129/analysis.md)).
- Useful inherited bias remains unshown. Root 23's frozen inherited frequencies
  did not improve fresh training-task search over uniform; the supplied scaffold
  was much better. Linkage helped relative to shuffling on max without showing
  useful acquisition. This limits one procedure, not self-adaptation generally
  ([root 23](../../questions/23-heritable-variation-bias/question.md)).

**Which roots matter now.** Root **10** has the highest immediate value: can
automatic acquisition recover useful new computational content, rather than
only rediscovering small sums? The observed discarded repertoire gives a
specific intervention with a consequential answer. Root **23** remains the
central missing mechanism for the long-term inherited decoder, but no new
selectable signal meets its reopening conditions. Root **01** remains useful
background; refining its threshold or rare-helper results would not decide
which acquisition to build next. Original folding, CA development, runtime
plasticity and broad PSB2 work do not presently supply a better-priced answer
to the task-family learning question.

**Current line versus different mechanisms.** I searched the literature during
this review and found the papers linked here. They motivate candidates; their
results are not evidence for performance in this repository.

| Candidate | Mechanism and decision |
|---|---|
| Retain all eligible semantic classes | External pooling of observed source subtrees, frozen as expanded mutation donors. Closest precedent: [Keijzer, Ryan and Cattolico, *Run Transferable Libraries* (2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf). **Pursue once**, 4–6 h now. Tests whether the current available repertoire is useful after paying for dilution. |
| Parameterized abstractions | [Bowers et al., *Top-Down Synthesis for Library Learning* (POPL 2023)](https://arxiv.org/abs/2211.16605) presents Stitch: corpus-guided synthesis of abstractions selected for compression. [Ellis et al., *DreamCoder* (2020 preprint)](https://arxiv.org/abs/2006.08381) combines learned abstractions with neural search guidance. Parameters could share structure across input bindings, unlike our fixed literals. **Defer this block**: syntactic abstraction need not fix semantic bloat, and more useful compression need not improve GP search. A narrow adapter, parameter-instantiation rule, validation and development/transfer comparison provisionally costs 12–18 h, unmeasured; a full DreamCoder reproduction is not priced. Reconsider if the bounded repertoire test leaves a specific representational limit that parameterization addresses. |
| Inherited variation probabilities | [Stephens et al., *Self-adaptation in evolving systems* (1998)](https://pubmed.ncbi.nlm.nih.gov/9847423/) studies encoded variation probabilities whose descendant effects drive propagation. This directly addresses the owner's mechanism, unlike external extraction. **Defer**: the old frequency procedure failed usefulness, and another 10–14 h block needs a changed rule and measured selection opportunity, not just available time. |
| Supplied helpers or a deployment gate | Retain R-order as the strong practical reference. It supplies family knowledge without acquisition. A library-on-failure policy might limit harm, but cannot create absent useful content. Keep question 50 parked until a mixed-difficulty deployment is funded or its easy-target condition applies. |

The abstraction candidate now has a concrete motivation—varied literal forms—
but an abstraction engine is not needed to release the already pooled forms.
Conversely, cap removal may still fail because most donors are irrelevant and
larger forms are rejected. That is a real risk to the selected candidate, not
a reason to filter donors using knowledge of the desired helpers.

**What the steward should work on next.** *Does retaining every already
eligible recurrent semantic class turn source acquisition into useful order-task
search bias, or does the acquired repertoire still cost more than it buys?*
Follow the new [cap-release plan](../../plans/order-library-cap-release.md).
Open a child under root 10 (next unused number **53**), referencing 52's
extractor-test reopening condition; the steward owns status and log changes.
Use independently acquired corpora and fresh searches on development cells.
Keep capped R-S, plain R-tree and the supplied order prior visible.

This is worth its full cost because it separates a consequential choice:
continue acquiring observed subtrees, or stop expanding this recurrence-only
recipe and reconsider how reusable content is represented or selected. It can
establish automatic useful acquisition without beating a domain-informed prior;
those are different conclusions. A small improvement over a harmful library,
more helper entries, or merely running successfully would not justify expansion.
Do not score protected cells to rescue a weak development result.

**Allocation and exit.** Raise only root 10's frontmatter `budget.experiments`
**43 → 44**, one full experiment through the next strategy review. Expected
total **4–6 h**, including preparation, validation, proposal/reviews, queue,
analysis and contingency; preparation at most 120 minutes and summed queue
timeouts at most 2 h within a 6 h total ceiling. The pilot's 118 s preparation
queue and 332 s scoring queue support a bounded study, not a guarantee for
the new arm or its required precision. The plan supplies a transparent sizing
scenario; the steward must price a decision-sized comparison before admission.

Return after that result or an earlier build, validity, precision or cost
obstacle. A conditional protected comparison costs another **6–8 h**, currently
**unallocated**: **10–14 h total** for the complete candidate, leaving about
12–16 h at this review's time estimate. Its value must be reassessed against
the observed gain, strong-prior gap and acquisition cost; a development win
does not automatically authorize it. Tight small effects or harm end this
uncapped procedure. Broad uncertainty warrants a resolution price, not equality
or an automatic top-up. If no candidate then justifies its complete cost before
the deadline, end the run rather than use the remaining experiment slots.

**Owner note disposition.** The only [owner note](../../plans/owner-heritable-map.md)
is unchanged since [strategy 1129](../2026-10-11-1129/strategy.md): SHA-256
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
There are no new or changed unanswered notes. Its standing requests are:

| Direction | Disposition, reason and reconsideration |
|---|---|
| Inherited op frequencies | **Pursued** in root 23; further work **deferred** after the failed usefulness test. Reconsider a changed rule with measured selectable signal, a bank where learned frequencies add beyond the scaffold, or a necessary inheritance control. Order-library observations do not supply that signal. |
| Capture and synonyms | **Deferred**: the owner's useful-inheritance prerequisite remains unmet. Reconsider after it is met, with a specific reassignment question and separately priced engine validation. |
| Population-level maps | **Pursued** via outer-selected token maps. More contextual selection **deferred** after the tested procedures added no resolved increment; reconsider a changed representation or ranking signal with full acquisition/transfer costs. External corpus extraction does not satisfy the inheritance request. |
| Free table mutation; ambiguous intermediates | **Declined for this block**. Reconsider free mutation only as a necessary contrast in justified reassignment work; ambiguous intermediates only for a specific gap left by the owner's preceding steps. |

**What to stop.** End the unchanged literal extractor's order-content expansion
and further gate-sum ingredient tests. No hand-prior variants, extra familiar-sum
shapes, TS/DG precision top-ups, source-size/rate/restart sweeps, or further
claims of practical value against G4 alone. No unchanged inheritance/context
optimizer reruns. The one authorized cap intervention does not permit successive
rankings, constant filters, larger emission limits, helper-aware extraction,
protected-target tuning, a neural policy or a new bank. Preserve the old negative
probe and its failed continuation rule; the revised procedure must earn its own
answer.
