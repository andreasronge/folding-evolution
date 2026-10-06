---
next: proposal
---

Continue [root 10](../../questions/10-compositional-map-transfer/question.md).
**Next question: does the planned four-reducer bank provide two distinguishable task
families on which equally funded map adaptation can be compared?** This is the missing
bridge from demonstrated transfer to evidence that the map learns a family's preferences.
Use the existing [four-reducer plan](../../plans/four-reducer-family-transfer.md); the
steward should propose its feasibility study, not another saved-map check.

**What the program has learned.** The [core question](../../../README.md#core-question)
asks how the map biases discovery and whether that bias can evolve to fit a task family.
The [digest](../../digest.md), question tree, [run ledger](../../briefs/2026-10-05-2225-ledger.md),
recent briefs and decisions give a substantial but bounded answer:

- Frequency matters without determining evolutionary success. Folding's fixed-target
  advantage was consistent with greater solver supply; search often lost to random
  sampling there. TAG lexicase instead beat a sampling-derived random-search baseline.
  On the composition banks, large supply gains yielded much smaller search gains.
  Supply, variation and selection remain distinct explanatory questions.
- Assembly and preservation depend on the operators. Cheap joins explained the earlier
  modular advantage. Selected-mate crossover blocked rare seeded shared forms;
  self-mating permitted both discovery and seeded establishment. Natural B-helper
  arrival and single-copy establishment remain unresolved. These results do not establish
  that a developmental encoding is generally superior.
- Bias can be fitted or evolved to improve fresh search. Root 01's threshold fits gave
  about fourfold speed-ups over uniform, but a hand-set scaffold performed comparably
  and the family-specific increment remained unresolved. Root 10 went beyond constant
  substitution: learned token multipliers on the supplied grammar G transferred to
  withheld operation combinations. Re-scoring the six learned maps gave holdout gains
  of 2.25× [1.81, 2.81] and 2.06× [1.60, 2.63]. Only maps transferred; populations restarted.
  This is transfer on one screened family, with hand-supplied context.
- The benefit is not confined to the trained post-addition cells: related branch-else
  tasks also improved. That does not establish equal benefits or family specificity.
  Allowing learned contextual rows above token learning gave training 1.00× [0.90, 1.11]
  and unresolved holdout increments in [0811](../2026-10-06-0811/analysis.md).
- The latest [check](../2026-10-06-1425/analysis.md) removes the strongest reason to keep
  pursuing those contextual maps now. The branch-over-linear shift reversed on the unused
  continuations, 0.73× [0.57, 0.94], while the originally selected maps retained their
  pattern on fresh search seeds. On the unused maps, matching pooled token frequencies
  on G reproduced the shift within [0.92, 1.12]. This is a bounded conditional replication
  across learning runs sharing six starts, not proof that context never helps.

The older folding, slot-indirection and CA tracks provide background about scaffolds,
reuse and representation. They do not supply the missing comparison between independently
adapted families. In particular, the [CA revival](../../../Plans/ca-developmental-revival.md)
targets developmental robustness; it would need a further connection to map-bias transfer
to displace the present line.

**Priorities and competing directions.** Root 10 matters most now because it has a working
learner and positive transfer, but cannot yet distinguish a family preference from a
broadly useful correction to G. Root 01 remains the mechanism foundation; its unresolved
supply, shortcut and helper questions do not block that comparison. Root 10 already carries
08's decoder-rule follow-up, so reopening the old threshold study would duplicate direction
rather than fill the gap.

| Candidate direction | What it could change | Priority |
|---|---|---|
| Two families with the same primitive inventory | Tests whether training history changes which unseen compositions are easier, beyond generic improvement. | First: one bounded feasibility study, then a crossed transfer comparison if supported. |
| More independent PA learning starts or a better outer objective | Could resolve the small contextual increment or reveal a better learner, but still supplies only one trained family. | Defer. Roughly 20 independent starts were estimated for the 1.16× increment; more inner seeds cannot substitute. |
| Separate solver supply from useful variation under root 01 | Could explain why sampling gains and search gains diverge. | Important later; no current transfer decision requires that causal decomposition. |
| Resume helper discovery or CA robustness | Could clarify establishment or developmental dynamics. | Keep deferred: neither directly tests whether the current learned bias carries family information. |

**Direction for the steward.** Open a new child under root 10, following the tree's next
available number; all existing children are closed. Ask whether adding FIRST to SUM/MAX/MIN
supplies usable branch-else and post-addition families. Four distinct readouts may reduce
condition reuse and correlations, but do not remove conditional identities. The old
three-reducer failure is therefore a reason to screen this candidate, not evidence that
it will work.

The existing plan is sufficient: freeze the candidate roster and rules, check semantics
and simpler aliases first, then measure search headroom and complete adaptation cost in
the same gated queue where feasible. Preserve its alias and headroom rules. Extend the
fixed grammar once as G4 before seeing outcomes; old G rates do not establish G4's
tractability. A new primitive is a new experimental condition, not a replication of the
old bank. Canonical programs are evaluator checks, never transferred solutions.

Carry the successful **G4-based token-multiplier learner as primary** into the later
matched/mismatched comparison. Identical canonical token counts do not guarantee identical
frequencies among discovered programs; family specificity could reside in token weighting.
That would answer part of the core question without demonstrating newly learned context.
Context gets at most a secondary arm, justified by a measured training signal or useful
decoder-capacity diagnostic and affordable cost. A hand-set family grammar is a capacity
check, not evidence that learning acquired its preferences. Near-25% aggregate operator
acceptance is not evidence that candidate ranking fails.

If feasible, the next substantive question is whether independently adapting to each family
makes its own withheld combinations easier than adaptation to the other family does, in
both directions and relative to G4. Keep fresh-training performance visible so failure to
learn is distinguishable from failure to transfer. Use independent adaptation trajectories
and fresh program populations. The steward owns sample sizes and outcome rules; this
strategy does not prescribe a full experiment.

**Allocation.** `uv run python scripts/research.py status` confirms **5/40 experiments used,
root 10 left=2, root 01 left=0**. About 31 hours remain. Keep root 10's budget at **7**:

1. Slot 6 settles whether this four-reducer candidate supplies non-aliased family splits,
   measurable headroom and an affordable learning comparison.
2. Slot 7, conditional on feasibility and strategy review, tests matched versus mismatched
   family adaptation. If the probe fails, return its specific obstacle before reallocating
   this slot; do not spend it automatically on an alphabet or domain sweep.

No budget increase or new root is needed now. Preserve the remaining root opening; the
chosen question fits root 10 and already has a plan. The other 33 available run slots are
unallocated, not a target to fill. Allow up to eight hours per justified queue and reserve
time for implementation, review and analysis. A promising result needing an independent
replication or a better-sized comparison can receive a later named budget increase.
Return to strategy after feasibility. A failed bank rejects this candidate, not the core
hypothesis or the autonomous run.

**What to stop.** End the saved-map branch/linear follow-up here; do not chase the reversed
shift as a new lead. Stop same-start PA precision extensions, sparse three-cell contextual
mutations, repeated G-versus-marginals demonstrations and large zero-hit sampling exercises.
Keep threshold-veto refinements and helper censuses parked unless their concrete reopen
conditions become relevant. Do not weaken fixed controls or relax alias rules to obtain
a favourable bank. Continue the program: the planned two-family feasibility probe can
change the next scientific decision and deserves its slot.
