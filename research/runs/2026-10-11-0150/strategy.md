---
next: proposal
---

Fund **one test of learned subtrees inside restarted tree GP**, then review.
The next useful answer is whether learning improves an already effective
structural search. Further refinement of A8 against G4 would not answer that.

This review covers the [core question](../../../README.md#core-question),
[digest](../../digest.md), question tree and reopening conditions, plans and
owner note, and recent briefs/decisions through
[0024](../2026-10-11-0024/decision.md). `uv run python scripts/research.py status`
reports **6/40 experiments used**, root 10 **36/36 used**, and no allocation
left in roots 01 or 23. About **36 h remain**, until
**2026-10-12T14:19:15 Europe/Stockholm**. The current run has used one probe and
five full experiments; another probe is available, but is not itself a reason
to spend a cycle.

**What we have learned.**

- **Maps affect supply and evolutionary access differently.** Root 01 found
  random-program frequency informative about easy targets but insufficient
  for predicting hard discoveries. Cheap joins explained the tested composition
  advantage; lineage mixing impeded rare shared forms. This supports studying
  concrete map/operator combinations, not general developmental superiority
  ([root 01](../../questions/01-map-bias/question.md)).
- **Evolution's discoveries contain reusable search information.** Outer-selected
  token biases transferred roughly twofold. The contextual selection procedures
  tested added no resolved increment, while external solver-corpus fitting did:
  context beat token fitting **2.12× [1.86, 2.41]** on then-addition when that
  bank was fresh. Pooled and positional frequency replacements, and random
  recoding to match mutation width, did not reproduce the advantage. Conditional
  content versus structured variation remains unresolved. Partial-program fits
  also helped, more weakly; the tested pre-solve fragment extractor did not
  recover a worthwhile increment ([digest](../../digest.md)).
- **Acquisition became cheaper and showed one useful family preference.**
  A8's four-plus-four source policy approached the full pipeline's search speed
  at much lower acquisition cost on the original output families, transferred
  to a fresh output shape, and survived replacement sources. On independent-input
  DG, a family with addition inside the predicate, DG-acquired builds were
  about **3×** cheaper than TS-acquired builds; the reverse preference remains
  unresolved. Both the table and library carry useful information within tape
  search, without an identified dominant component or semantic-module mechanism
  ([41](../2026-10-10-1717/analysis.md),
  [42](../2026-10-10-2001/analysis.md)).
- **A stronger baseline changes the practical conclusion.** Under the same
  restart schedule, DG mean evaluations R-tree/R-A8 are **0.792 [0.682, 0.915]**:
  tree uses fewer evaluations, solving **765/768 versus 754/768**, within the
  three-point reliability guard. Restarting helps A8 too, so its earlier
  reliability lead was largely schedule-dependent. Worker seconds reverse the
  ordering: R-tree/R-A8 **1.388 [1.196, 1.604]**. A8 repays acquisition after
  about **312 [211, 579]** DG searches per build in seconds, with no demonstrated
  repayment in evaluations. TS descriptively favors tree in both units. These
  are development rosters, one tree configuration and one cutoff
  ([0024 analysis](../2026-10-11-0024/analysis.md)). The time reversal compares
  complete implementations; it does not isolate which learned or engineering
  feature caused it.
- **Useful acquisition by inheritance remains unshown.** Root 23's tested
  inherited-frequency rule was worse than uniform on sum and excluded a max
  gain above about **1.06×**. Persistent ancestry helped against its shuffled
  control on max without producing useful frozen bias. This limits that rule,
  exposure and bank, not self-adaptation generally
  ([root 23](../../questions/23-heritable-variation-bias/question.md)).

The core question therefore has a qualified positive answer for **externally
acquired, reusable bias**, including one direction of family preference.
Acquisition through inheritance and a learned evaluation advantage over
competent structural search remain open. All banks used so far are now
development data; their earlier protected results retain their original scope.

**Root priorities.** Root **10** remains first, redirected from repairing a
tape prior to learning beyond structural search. This is a stronger test of
whether previous discoveries make later search cheaper. Root **23** is second
in conceptual importance, because inheritance is the long-term goal; the latest
result supplies no changed selectable signal meeting its reopening condition.
Root **01** stays unfunded: helper-arrival, fixed-target sampling and shortcut
refinements would not choose the next acquisition procedure. Existing roots
cover the live questions. Open **no new root**; retain both allowances.

**Current line against alternatives.** Literature was searched in this review;
the papers below motivate mechanisms, not expected effects on our tasks.

| Candidate | Mechanism and decision |
|---|---|
| **A8 and more tape fitting — defer expansion** | External fitting updates a sequential program generator, with literal fragment edits. This is related to [Salustowicz and Schmidhuber, *Probabilistic incremental program evolution* (1997)](https://pubmed.ncbi.nlm.nih.gov/10021756/), rather than per-individual inheritance. Its transfer and DG worker-time value stand. More source sizes or component controls would refine an already useful weak-prior comparison without establishing an increment over R-tree. Reconsider for a concrete deployment horizon or a new transfer question with a strong comparator. |
| **Tree-native library learning — pursue one experiment** | Externally acquired complete subexpressions become mutation donors in a fixed structural representation. [Keijzer, Ryan and Cattolico, *Run Transferable Libraries—Learning Functional Bias in Problem Domains* (2004)](https://www.cs.york.ac.uk/rts/docs/GECCO_2004/Conference%20proceedings/papers/3103/31030531.pdf) transfers acquired functions across GP runs. Our bounded literal-subtree procedure is narrower, with full primitive expansion. It tests whether learned content helps after valid expression construction and restarts are already supplied. Price **7–10 h** for usefulness, **12–18 h** including separately reviewed fresh-bank transfer. |
| **Inherited variation parameters — defer** | Mechanistically different: strategy parameters spread through successful descendants, without an external corpus estimator. [Stephens et al., *Self-Adaptation in Evolving Systems* (1997 preprint)](https://arxiv.org/abs/adap-org/9708002) studies encoded mutation/crossover probabilities and adaptation in changing environments. It does not establish token-frequency learning here. The existing [inheritance plan](../../plans/heritable-variation-bias.md) prices usefulness plus transfer at **10–14 h**, but its tested procedure failed and a changed rule lacks evidence of useful signal. A smaller noise scale alone is not a sufficiently grounded next purchase. |

The library study is worth its full cost because either a useful increment or
a tight small-effect bound changes which representation we should teach.
Existing tape library gains provide a reason to test it, not evidence that it
will work in trees. The competing explanation is that those gains largely
supplied structure that ordinary subtree search already has. R-tree's **99.6%**
DG solving leaves little reliability headroom, but its **90,392 mean evaluations**
leave a meaningful speed question. This is one learning attempt against the
new baseline, not permission for another sequence of small ablations.

The unexplained training-perfect shortcuts in 0024 are another possible target:
**9.6%** of tree evaluations were training-perfect but not exact. Restarting
redraws cases as well as populations, so their contributions are unseparated.
Keep that observation visible, but defer a case-redraw/reset factorial: it
would explain the baseline rather than establish learning from prior tasks.
Reconsider if the learned library is claimed to remove shortcutting or that
distinction becomes necessary to choose its search policy.

**What the steward should ask next.** *Can a small library acquired from tree
solutions reduce fresh DG search cost beyond restarted tree GP, and beyond
valid generic subtree donors of matched size, enough to justify acquisition?*
Use the updated [tree-native plan](../../plans/tree-native-fragment-learning.md).
Open the next child, currently **45**, under root 10; leave 43 and 44 closed as
references. Use new source searches and independent acquisitions. The previous
[syntactic audit](../2026-10-11-0024/planning-audit.json) found only **30/693 DG**
and **1/768 TS** tape-library entries that parse as complete expressions;
filtering them would leave most TS libraries empty. They are not ready-made
subtrees. Source inspection at `1773d11` confirms the reviewed tree code already
has subtree spans, insertion and saved exact solver trees, keeping the new
build bounded.

Fix **arithmetic capped evaluations as the primary scientific cost unit** for
this within-tree comparison. Retain reliability, measured worker time and
acquisition-plus-search curves as necessary practical readings. The cost choice
does not declare the owner's deployment objective: a result may improve search
while failing to save time. Keep the current restart policy common and show
per-cell results. A later transfer claim requires a genuinely unsearched bank
frozen with the method, not new DG seeds. The steward chooses the full design
and decision-sized sample; this strategy is not a registration.

**Allocation and exit.** Raise only root 10's frontmatter `budget.experiments`
**36 → 37**: **one substantive experiment through the next strategy review**,
expected **7–10 h total**, including implementation, validation, acquisition,
scoring, proposal/reviews, analysis and contingency. Preparation stays within
120 minutes; summed queue timeouts within four hours. The completed 0024 queue
took about 36 minutes, but that does not price source yield, extraction or
learned-donor scoring. Measure them before admitting a fixed informative study.
Of the **34 remaining run slots**, one is allocated and **33 remain unallocated**.

Return to strategy after the result or a measured build, validity, precision or
complete-cost obstruction. Useful improvement over R-tree, supported by the
donor control and credible economics, earns consideration of a **5–8 h**
fresh-bank stage. It does not allocate that stage. A tight small or harmful
effect ends this extractor's expansion; a broad interval needs a resolution
price. The complete candidate's **12–18 h** allowance fits the time left and
answers a consequential gap, so **continue the run**. Stop at a later review
if no complete candidate still justifies its cost, irrespective of unused slots.

**Owner note disposition.** The sole note,
[owner-heritable-map.md](../../plans/owner-heritable-map.md), is unchanged since
[strategy 0024](../2026-10-11-0024/strategy.md), verified by SHA-256
`439bf7393e478eecebe519357bbcb314b90720df3de73fd0f482a0e715e7bba8`.
There are **no new or changed unanswered owner notes**. Standing dispositions:

| Direction | Disposition, reason and when to reconsider |
|---|---|
| Inherited op frequencies | **Pursued** at root 23's tested scope; further work **deferred** after failed frozen usefulness. Reconsider a changed rule with measured selectable signal, a bank where learned frequencies improve beyond the scaffold, or a required inheritance control. |
| Capture and synonyms | **Deferred**: the owner's useful-learning prerequisite is unmet. Reconsider after useful inherited acquisition and a concrete need for reassignment, with engine validation priced separately. |
| Population-level maps | **Pursued** by outer-selected token maps; renewed context selection **deferred**. Reconsider a changed representation or selection signal with a credible complete acquisition/transfer price. A8 fitting and tree extraction do not fulfill this mechanism. |
| Free table mutation; ambiguous intermediates | **Declined for this block**. Reconsider only as a necessary contrast or specific gap in a justified reassignment study, preserving the owner's ordering. |

**What to stop.** Stop G4-only confirmations, tape component matrices, reciprocity
precision for completeness, source-size/feedback sweeps and full-F parity work.
Do not optimize restart cutoffs or tree engineering merely to reverse the
worker-time result. Keep unchanged pre-solve extraction, blind contextual
optimizer retries, shared-helper and CA expansion parked. Do not execute the
old [PSB2 plan](../../../Plans/psb2-sanity-probe.md), which targets an earlier
question. Broader benchmarks need a current acquisition/comparator plan; they
must not wait for every internal mechanism to be explained or for A8 to win.
