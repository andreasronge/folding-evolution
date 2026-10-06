---
next: proposal
---

Continue [root 10](../../questions/10-compositional-map-transfer/question.md).
**Next question: can selection on the six surviving post-addition training tasks improve
a decoder so that fresh populations solve the two withheld compositions faster than with
the fixed grammar or frequency-only adaptation?** Use the
[one-family transfer plan](../../plans/post-addition-map-adaptation.md). This is a deliberate
narrowing: test learned transfer within one assembly family now; leave family specificity
unanswered. Do not spend the next cycle screening another two-family bank.

**What the program has learned.** The [core question](../../../README.md#core-question)
asks both what a map makes likely and whether that bias can evolve to fit tasks. The
[digest](../../digest.md), question tree and recent decisions give a substantial answer to
the first part and a limited answer to the second.

- Supply matters, but is not a general predictor of search. Folding's fixed-target
  advantage was consistent with more frequent solvers; evolution often lost to sampling
  there. TAG threshold search beat a sampling-based random-search baseline. These are
  different tasks and harnesses, not evidence that one representation always wins.
- Discovery and retention differ. Cheap joins explained the modular assembly advantage.
  Selected-mate crossover removed rare seeded shared forms; self-mating permitted both
  discovery and establishment. Natural B-helper arrival and single-copy establishment
  remain unresolved. More census precision would not answer whether a map learns.
- Fitted token weights transferred between constant thresholds and sped solving about
  fourfold over uniform, but a hand-set scaffold performed comparably. Family specificity
  remained unresolved. The component experiment narrowed the apparent no-supply gain;
  the shortcut-veto pilot did not establish its mechanism. See
  [1705](../2026-10-05-1705/analysis.md), [1814](../2026-10-05-1814/analysis.md) and
  [1957](../2026-10-05-1957/decision.md).
- Contextual decoding is a useful intervention: G beat its own context-free marginals
  on both composition banks. That changes supply and mutation effects together, so it
  does not identify a mechanism. **No decoder has yet been evolved in root 10.**
  [2247](../2026-10-05-2247/analysis.md) lacked headroom on its short tasks;
  [0001](../2026-10-06-0001/analysis.md) found headroom on ten-token branches but no
  eligible pair among six screened shapes. This rejects those banks under their rules,
  not learned transfer or the alphabet as a whole.

Older tracks make fresh program populations especially important. Folding's later
[assessment](../../../docs/folding/findings.md#8-the-complexity-ceiling-revised) bounded
transfer by preserved scaffolds, reachable structure and partial-credit scoring.
[Chem-tape slot transfer](../../../docs/chem-tape/findings.md) depended on a shared body.
[CA specialization](../../../docs/ca/experiments.md) improved parity, but has not tested
map learning across tasks. [Coevolution](../../../docs/coevolution.md) exposed role conflict
and constant-output collapse. None supplies the missing decoder-only transfer result.

**Priorities and alternatives.** Root 10 is first because it directly tests the missing
part of the core question and now has reusable tasks and a reviewed harness. Root 01 is
second as the source of supply/search explanations; its parked questions need a concrete
dependency before further work. Current results do not require reopening 02 or 04–09.

| Candidate direction | Value and limitation | Decision |
|---|---|---|
| Adapt on the surviving post-addition family | Tests whether training leaves useful information in the map after discarding programs. Known split and headroom; outer learning remains unmeasured. Cannot establish family specificity. | First: proceed to an adaptive feasibility/transfer study. |
| Add a reducer or change the comparison to obtain two families | Could separate family-specific assembly from generic syntax, but needs new semantics, screening and runtime evidence before any learning test. | Defer until a transfer result makes this contrast the next useful question. Still deserves a bounded probe if the chosen direction fails. |
| Separate supply from mutation under fixed G | Answers part 1 more causally, using a large replicated effect. Would still leave learned bias untested. | Reserve for a result where this distinction changes the next decision. |
| Revisit root 01's veto, rarity ladder or helper arrivals | Resolves narrower mechanisms, with substantial work already invested. | Keep parked: no new evidence or dependency justifies return. |
| CA damage and I/O-shift assays | A credible developmental-robustness direction with an [existing plan](../../../Plans/ca-developmental-revival.md), but less direct for task-family map learning. | Defer; preserve the remaining root opening. |

**Direction for the steward.** Open a new child under root 10 for the question above;
12's completed two-family screen stays closed. Reuse its PA split and data. The two
holdouts have G medians 13,568 and 18,688 evaluations and 49/50 and 48/50 exact solves.
That supports testing improvements, not assuming one exists. Begin with an outer-loop
cost and training-signal calibration, then gate a substantial transfer stage in the same
proposal if it fits. Choose sizes and outcome rules in that proposal. Retain frozen G,
fresh program populations, independent map trajectories and controls for token weights.
Starting maps from G tests refinement of a supplied prior; say so. A linear-family fit
without IF_GT cannot serve as a token-matched specificity control.

The [latest decision](../2026-10-06-0001/decision.md) explicitly offers this one-family
route. Accepting it does not relabel the failed two-family experiment as successful or
relax its alias/headroom rules. It removes the second-family requirement from the next,
narrower question. Generic syntax learning remains a live explanation even if transfer
succeeds.

**Allocation.** `uv run python scripts/research.py status` reports 2/40 experiments used,
root 10 left=3 and root 01 left=0, with about 45 hours remaining. Leave root budgets
unchanged (10: experiments=5; 01: experiments=6); open no new root. Use the three existing
root-10 slots provisionally for:

1. Outer-learning feasibility and the first controlled transfer measurement, with a
   gated main stage when affordable.
2. Independent adaptation replication or a better-sized resolution of the leading
   transfer contrast. More inner seeds under one map do not replicate learning.
3. The one follow-up that changes the interpretation: a specificity contrast, a
   supply/variation separation, or a measured redesign after failure. Choose at review.

The other 35 remaining run slots are unallocated, not forbidden. Return to strategy after
the first adaptive result or a calibration failure, before spending slots 2–3. A promising
unresolved effect can justify a later budget increase. Each queue remains at most eight
hours; the historical 1.1–4.3 seconds per inner run is not a measured outer-loop runtime.

**What to stop.** Stop the sequence of exhaustive task-bank screens before attempting
learning. Do not weaken G, relax the alias cutoff, top up the old Sm-SEL cell alone, or
repeat G-versus-marginals for precision. Avoid another large uniform-sampling run whose
likely contribution is only a tighter zero-hit bound. Keep threshold refinements,
shared-helper censuses, CA retraining, plasticity expansion and coevolution ports deferred.
This is not a program stop: the surviving one-family direction warrants more than another
semantic feasibility screen, and the alternative directions remain viable.
