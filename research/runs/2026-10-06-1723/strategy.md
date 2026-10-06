---
next: proposal
---

Continue [root 10](../../questions/10-compositional-map-transfer/question.md).
**Next question: does independently adapting the same decoder to branch-else versus
post-addition make its own withheld compositions easier than the other family's training
does?** Use the measured four-reducer bank with an explicitly narrower split, following
the new [asymmetric transfer plan](../../plans/asymmetric-family-transfer.md).

The [core question](../../../README.md#core-question) concerns both the bias a map imposes
and whether that bias can evolve to fit a task family. Reading the [digest](../../digest.md),
whole question tree, [ledger](../../briefs/2026-10-05-2225-ledger.md), recent briefs and
decisions leaves four main lessons:

- Program frequency matters, but does not determine search success. Folding's fixed-target
  advantage was consistent with greater solver supply; evolution often lost to random
  sampling there. TAG lexicase instead beat a sampling-derived random-search baseline.
  Supply, variation and selection remain separate explanatory questions.
- Cheap joins explained the earlier recombination advantage. Mixing selected lineages
  blocked establishment of rare seeded shared forms; self-mating allowed discovery and
  seeded establishment. Natural B-helper arrival and single-copy establishment remain
  unresolved. This is useful operator-specific knowledge, not general developmental superiority.
- Map adaptation can improve fresh search after all programs are discarded. Root 01's
  threshold fits helped about fourfold over uniform, with comparable performance from a
  hand-set scaffold. In root 10, learned token multipliers on G transferred to withheld
  operation combinations: [0811](../2026-10-06-0811/analysis.md) re-scored holdout gains at
  2.25× and 2.06×, with lower bounds above 1.5×. Similar benefits on related branch-else
  cells leave family specificity open. The context was supplied by hand.
- Learned contextual improvement is still unestablished. Row moves versus continued token
  learning gave training 1.00× [0.90, 1.11] and unresolved holdout increments. The off-family
  hint reversed on the unused continuations in [1425](../2026-10-06-1425/analysis.md).
  Conversely, [1603](../2026-10-06-1603/analysis.md) showed that hand-set context can express
  a crossed family preference on the four-reducer bank. Only its BE grammar beat G4 on its
  own family; the PA contrast partly reflects damage from the BE grammar. Expressibility
  is positive evidence about the decoder class, not evidence that learning finds it.

**Root priorities and alternatives.** Root 10 remains first: a working learner, measured
search headroom and a missing training-family comparison connect directly to part 2.
Root 01 remains the foundation for part 1, but its unresolved mechanisms do not block
that comparison. Its budget stays unchanged. Earlier folding and slot-indirection results
motivate the program; CA robustness would need an explicit connection to learned map bias
to displace the current work.

| Direction | What it could change | Decision now |
|---|---|---|
| Crossed learning on the existing bank, with one BE holdout and two PA holdouts | Separates a training-family preference from generic improvement on these compositions. Tractability, semantics and headroom are already measured. | First. Accept narrower task coverage and replicate learning trajectories. |
| Another symmetric bank, changing the condition or reducer inventory | Could support broader transfer claims and escape MAX/MIN sign imbalance. It needs fresh semantic and runtime screening, after three bank studies. | Defer: the existing bank already supports a bounded version of the missing comparison. |
| More PA contextual starts or optimizer redesign | Could resolve the small contextual increment; the old estimate was about 20 independent starts for a 1.16× effect. | Defer: still one trained family, with no resolved training advantage from context. |
| Supply versus useful variation, or helper/CA follow-ups | Could explain mechanisms or developmental robustness. | Valuable later; less direct than asking what information the learned map retains now. |

**Direction for the steward.** Open a new child under root 10; do not reopen the completed
feasibility study as though its outcome changed. I explicitly authorize changing the
previous requirement of two covered holdouts per family to **one BE and two PA holdouts**.
Keep the domain, alphabet, alias threshold, role coverage and fixed G4 unchanged. The
unique covered BE holdout is `S?m:(M+F)`; use the already identified PA split. This choice
follows inspection of bank data and must be labelled accordingly. It provides fresh-seed
transfer on a screened bank, not an untouched benchmark or broad evidence across BE tasks.

Use independently trained G4-based token multipliers as the primary comparison. Identical
canonical token counts do not guarantee that token learning cannot distinguish the families.
A positive would establish family information in this restricted map, not newly learned
context. Do not add a full contextual arm now: the hand-set witness makes that a future
option, while the demonstrated learner can answer the narrower question first. Retain G4
so a matched-over-swapped advantage caused only by harming the other family is distinguishable
from a useful gain. Fresh training scores distinguish failure to learn from failure to transfer.

**Allocation.** Status confirms **6/40 experiments used, root 10 left=1, root 01 left=0**,
with about 29 hours remaining. Raise only root 10's frontmatter `experiments` **7 → 9**,
one **+2** allocation step. It funds independent learning and a crossed evaluation beyond
the existing feasibility slot:

1. Existing slot 7: settle whether equally funded learning on both frozen training sets
   improves fresh training search and has affordable, repeatable scoring. Save complete
   independent trajectories; this is learning feasibility, not another bank screen.
2. Added slot 8: extend independent, balanced learning across both families sufficiently
   to estimate variation between learning runs. This addresses the limitation that inner
   search seeds cannot replace independent adapted maps.
3. Added slot 9: complete any pre-sized learning and the frozen crossed holdout evaluation,
   settling whether gains are generic, family-dependent, lost on transfer, or unresolved
   at the achieved bounds. It does not settle generalization beyond the single BE holdout.

The plan sketches six trajectories per family across stages; the steward must size the
actual study from training variability and full cost. At the measured 35–70 minutes per
trajectory, twelve cost about 7–14 hours before evaluation. Eight alone can cost 9.3 hours:
the latest decision's suggestion that eight plus scoring fit one queue is not justified
under its conservative estimate. Keep every queue ≤8 hours, target ≤18 hours total compute,
and leave the remainder for implementation, review and analysis. Return to strategy after
the first learning stage if the cost or training signal defeats that allocation; do not
quietly reduce replication or inspect holdouts to rescue the design. No new root is needed.

**What to stop.** Stop repeated bank expansion as the default response to a failed split.
Stop saved-map branch/linear checks, same-start PA precision extensions, repeated
G-versus-marginals demonstrations and large zero-hit sampling exercises. Keep threshold
veto refinements and shared-helper censuses parked. Preserve unresolved effects as
unresolved. Continue the autonomous run: the crossed learning question deserves a measured
learning probe, so stopping the program is not justified.
