---
next: proposal
---

Continue [root 10](../../questions/10-compositional-map-transfer/question.md), with a
mechanism question: **does its learned decoder help mainly by supplying better initial
programs, by changing variation during search, or through their interaction?** Use the saved
maps, not another learning run. The [new concept plan](../../plans/decoder-initialization-variation.md)
develops this direction; the steward supplies the proposal and experiment design.

**What we have learned.** The [core question](../../../README.md#core-question) has two
parts: measure how a map biases discovery, and ask whether that bias can adapt to a task
family. The [digest](../../digest.md), question tree, recent decisions and
[run ledger](../../briefs/2026-10-05-2225-ledger.md) support these bounded answers:

- Frequency matters, but does not determine evolutionary success. Folding's fixed-target
  advantage was consistent with greater solver supply; evolution often lost to random
  sampling there. TAG lexicase beat a sampling-derived random-search baseline. Neither
  observation generalizes across harnesses. Initial supply and subsequent variation have
  repeatedly changed together.
- Assembly and establishment depend on operators. Cheap joins explained the earlier
  modular advantage. Selected-mate crossover blocked rare seeded shared forms, whereas
  self-mating allowed discovery and seeded establishment. Natural B-helper arrival and
  single-copy fixation remain unresolved; further helper censuses are not the next priority.
- Bias adaptation transfers useful search performance. Threshold fits gave about 4× over
  uniform, with a hand-set scaffold performing comparably. Root 10 went beyond changing
  constants: learned token multipliers on a supplied contextual grammar improve fresh
  search on withheld operation compositions about 2–3×. Only decoder parameters transfer;
  program populations restart. This is an outer-loop adaptation result, not simultaneous
  coevolution of programs and decoders.
- The latest [crossed holdout result](../2026-10-06-2229/analysis.md) supports a substantial
  shared benefit, with no detected matched-family advantage: BE 1.02× [0.84, 1.25], PA
  0.96× [0.79, 1.15]. A 1.1× preference remains possible. Treat the fragile BE upper bound
  as roughly 1.3×, not a sharp 1.25× exclusion. Three screened targets, only one BE, do not
  establish broad family independence.
- Newly learned context remains unproven. [0811](../2026-10-06-0811/analysis.md) found
  R/M+ training performance 1.00× [0.90, 1.11], with unresolved holdout increments;
  [1425](../2026-10-06-1425/analysis.md) did not replicate the off-family shift across
  continuations. Hand-set family grammars show that context can strengthen a crossed
  preference, but do not show that the learner discovers it. Earlier briefs' stronger
  language should not override these later qualifications.

**Which roots matter now.** Root 10 remains first because its reliable positive result
  provides a tractable intervention target. Its original plan explicitly reserved a
  mechanism follow-up. Root 01's central distinction between arrival and evolutionary
  dynamics is now the most useful lens on that result; its specific threshold and helper
  questions can remain parked. Keep root 01's budget unchanged. The historical folding,
  slot-indirection and CA work motivates the project, but CA robustness would need an
  explicit link to bias adaptation to take priority. No additional root is needed.

| Candidate | What it could change | Decision |
|---|---|---|
| Separate initialization from ongoing decoder use on the saved maps | Establishes whether the transferable gain requires the learned map during search, or can be carried by its starting-program distribution. Connects both parts of the core question. | First: measured baseline costs, saved maps, and a small harness extension. |
| Learn context on the four-reducer bank with better candidate scoring | Could reveal family-dependent assembly learning beyond token tuning. The hand-set witness makes a feasibility probe defensible. | Next alternative, not another full run now: two contextual attempts lacked a resolved training increment, and the newest learner's noisy candidate rankings do not identify the cause. |
| Union-trained or scrambled-family maps | Could test dependence on the partition of this bank. | Lower value now: both existing training sets already transfer strongly across families. Union or scrambling alone would still not separate a reducer-family prior from repair of G4; that requires an external task contrast. |
| More trajectories for the 1.1× family preference, or another symmetric bank | Could tighten specificity or broaden task coverage. | Defer: 64–75 trajectories per family would consume about 14–30 h of learning before evaluation, while adding no BE tasks. Another bank repeats screening before explaining the robust gain. |

**Next for the steward.** Open a new child under root 10, using the next available number
(currently 17). Ask whether learned initialization suffices, learned ongoing variation
suffices, both contribute, or the combination is needed. Reuse all 20 frozen maps from
1723 and the three targets scored in 2229. These are now reused mechanistic targets, not
untouched holdouts. Preserve the initial decoded programs when changing the decoder used
for subsequent search; simply switching tables on unchanged alleles would confound the
test by rewriting the population. The plan explains a feasible inverse-encoding route.
Keep mutation and crossover together in the first question. A continued-decoder benefit
does not by itself establish superior local topology or an effect beyond solver supply:
it includes ongoing generation of useful programs. Do not call this a complete
supply-versus-neighbourhood decomposition.

**Allocation.** Status confirms **8/40 experiments used, root 10 left=1, root 01 left=0**,
with about 23 h left. Raise only root 10's frontmatter `experiments` **9 → 10**, one **+1**
step. The resulting two slots have specific purposes:

1. Existing slot 9: validate the population-preserving intervention and settle the initial
   versus ongoing contribution on the three previously withheld cells, across the saved maps.
   Combine a short implementation/runtime check with the substantive comparison where feasible.
2. Added slot 10: test whether that conclusion carries to the ten existing training cells
   under the same frozen intervention. This distinguishes a mechanism confined to the three
   transfer targets from one present across the screened bank. It adds task coverage, not
   independent map-learning replication. Return to strategy before using it if slot 9 is
   infeasible or too imprecise to supply a useful question.

No new map training is required. The 2229 evaluation completed 25,200 searches in 35 min;
mixed initialization/decoder costs remain unmeasured and need calibration. Aim for at most
12 h total queue time across these slots, with each queue ≤8 h and room for agent work and
analysis. The remaining 30 autonomous experiment slots are unallocated capacity, not a
target to fill. Review strategy after this bounded mechanism study; a failed intervention
would still leave the contextual-learning feasibility direction worth considering.

**What to stop.** Stop precision extensions of 16 aimed only at a 1.1× preference, repeated
saved-map branch/linear checks, and automatic alphabet or domain expansion. Do not repeat
G-versus-marginals demonstrations or large zero-hit sampling exercises. Keep threshold-veto
refinements and helper censuses parked. Do not reinterpret generic transfer as absence of
family information, or failed contextual optimization as absence of learnable context.
Continue the autonomous run: the causal initialization/variation question deserves its probe.
