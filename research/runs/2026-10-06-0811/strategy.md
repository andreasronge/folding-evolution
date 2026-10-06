---
next: proposal
---

Continue [root 10](../../questions/10-compositional-map-transfer/question.md).
**Next question: does learning contextual changes to an already improved decoder help
fresh populations solve withheld compositions beyond continuing to learn token weights?**
This is the missing comparison after [0132](../2026-10-06-0132/analysis.md). Use
[13](../../questions/10-compositional-map-transfer/13-post-addition-map-learning/question.md)'s
remaining slot, following the [one-family plan](../../plans/post-addition-map-adaptation.md)
with the change of starting point and comparator described below.

**What the program has learned.** The [core question](../../../README.md#core-question)
asks how the map biases discovery and whether that bias can evolve to fit a task family.
The [digest](../../digest.md), tree, recent decisions and
[current run ledger](../../briefs/2026-10-05-2225-ledger.md) support these working conclusions:

- **Supply matters, but search is not determined by exact-solver frequency.** Folding's
  fixed-target advantage was consistent with higher solver supply, and evolution often
  lost to random sampling there. TAG threshold search instead beat its sampling-based
  random-search baseline. Across the composition banks, large supply gains produced much
  smaller search gains. These are task-and-harness results, not a universal ranking of maps.
- **Discovery and preservation are different problems.** Cheap joins explained the
  earlier modular-assembly advantage. Selected-mate crossover prevented rare seeded shared
  forms from establishing; self-mating allowed both discovery and establishment. Natural
  B-helper arrival and single-copy success remain unresolved. Another helper census would
  refine that story without testing whether the map learns.
- **Token-bias transfer is real within tested settings; task-family specificity remains
  unresolved.** Root 01's fitted threshold biases sped search about fourfold over uniform,
  but a hand-set scaffold performed comparably and mismatched fits also helped. Its
  component study exposed cancellation behind the apparent absence of sampling lift;
  the shortcut-veto pilot did not settle the residual mechanism. See
  [1705](../2026-10-05-1705/analysis.md), [1814](../2026-10-05-1814/analysis.md) and
  [1957](../2026-10-05-1957/decision.md).
- **Root 10 now extends learned transfer beyond constant substitution.** In
  [0132](../2026-10-06-0132/analysis.md), six independent M trajectories learned token
  multipliers on the supplied grammar G. Fresh-search speed improved 2.23× on training
  and 2.01× [1.47, 2.81] / 1.71× [1.26, 2.32] on two withheld compositions. Both holdout
  intervals exclude 1, but neither establishes a gain of at least 1.5×. This is refinement
  of a hand-supplied contextual prior on one screened family. M was still improving;
  its eventual ceiling and gains outside post-addition are unknown.
- **The learned-context question is still open.** Fixed G repeatedly beat its empirical
  context-free marginals, demonstrating useful supplied context. C's 552-weight learner
  showed no fresh-training improvement and little drift under three-coordinate mutations.
  That bounds this procedure, not the usefulness or learnability of contextual preferences.
  There are no solver-supply measurements for the learned maps, so mechanism is also open.

Older tracks reinforce the need to transfer only the decoder. Folding's
[revised assessment](../../../docs/folding/findings.md#8-the-complexity-ceiling-revised)
bounded apparent transfer by preserved scaffolds, reachable structure and partial-credit
scoring. [Chem-tape slot transfer](../../../docs/chem-tape/findings.md) used a shared body.
CA specialization improved computation, but the
[developmental revival](../../../Plans/ca-developmental-revival.md) still asks about damage
and I/O robustness. [Coevolution](../../../docs/coevolution.md) exposed role conflict and
constant-output collapse. None supplies the missing learned-context transfer comparison.

**Priorities and alternatives.** Root 10 matters most now: there is a usable split,
measured learning cost and a positive restricted learner. Root 01 remains the source of
important supply/search explanations, but no current decision requires reopening its
parked children. The two unsuccessful bank studies rejected particular splits and
screened shapes; they did not reject the alphabet or map learning.

| Candidate | What it could change | Priority |
|---|---|---|
| Learn contextual changes beyond continued M | Tests whether experience can add useful assembly preferences beyond the transferable token retuning already demonstrated. | First; the unresolved contrast that motivated root 10. |
| Evaluate frozen M outside post-addition | Shows whether the observed benefit extends beyond its training shape, at low additional cost. | Supporting work in the next queue; not a substitute for learning. |
| Build a second family with the same primitive support | Enables a matched/mismatched training comparison for family specificity. Needs new semantic and search feasibility evidence after two bank failures. | Next strategic alternative; worthwhile if specificity becomes the binding uncertainty. Use the existing family-plan framework and write a concrete addendum before a new screen. |
| Separate solver supply from variation under G or M | Gives a more causal answer to part 1, but would leave learned context untested. | Defer until the answer changes the next map design. |
| CA damage/I/O assays, or root 01's helper and threshold follow-ups | Credible questions with existing plans, but less direct answers to the present transfer gap. | Keep deferred; preserve the remaining root opening. |

**Direction for the steward.** Accept the broad recommendation in the
[latest decision](../2026-10-06-0132/decision.md): combine a bounded evaluation of the saved
M maps with a substantial contextual-learning comparison. Keep the main question above
primary. The proposal owns sample sizes, implementation and outcome rules.

Use all six saved M starts, without choosing them by holdout performance. Compare allowing
contextual adaptation with continuing token-only adaptation from the same starts, under
comparable additional training resources. Comparing only against frozen M would confuse
learning context with spending more time optimizing: M had not plateaued. Retain frozen G
and the inherited M performance as references. Empirical marginal controls help interpret
the resulting maps, but merely beating context-free marginals does not show newly learned
context; G already did that.

Calibrate the contextual update on training tasks at the M starts before committing the
main stage. The old [single-row probes](../2026-10-06-0132/steward_probes/results.md) were
unreviewed perturbations around G, with weak evidence of beneficial changes. They justify
trying a larger or structured update, not assuming it will learn around M. Require measured
runtime and a usable training signal; retain fresh training evaluation to distinguish
failure to learn from failure to transfer. Freeze tuning before new holdout evaluation.
Fresh search seeds on these already examined tasks remain evaluation on a screened bank.

For the supporting check, score the frozen maps on the eight retained non-PA cells, with
branch-else and linear results kept distinct. Broad gains would support a generic component;
weak off-family gains would not establish specificity. Linear tasks omit IF_GT, the two
branch-else cells are not an independently trained family, and baseline difficulty differs.
This check should neither select the contextual learner nor gate it on a claim of
specificity. Include bounded sampling only if affordable; sparse counts give bounds and
sampling/search co-movement does not identify mediation.

**Allocation and review.** `uv run python scripts/research.py status` confirms 3/40 run
experiments used, root 10 left=2, child 13 left=1, root 01 left=0. About 38 hours remain.
Leave both root budgets unchanged (10: experiments=5; 01: experiments=6), and open no new
root. There is enough allocation for the next decisive comparison and a reviewed follow-up:

1. Spend 13's last slot on contextual-learning feasibility and transfer beyond continued M,
   with the supporting frozen-map check. Gate a substantial main stage in the same queue
   when feasible; the previous entire study took 5 h 46 min, but the revised cost must be
   measured. Keep the eight-hour queue limit.
2. Return to strategy after that result. Reserve root 10's final slot for independent
   adaptation replication or a better-sized resolution if the contextual contrast is
   promising; otherwise choose the second-family feasibility direction or a specifically
   motivated mechanism question. The steward must place any follow-up under a child with
   available allocation; 13 will then be exhausted.

The other 35 run experiments remain unallocated. A useful unresolved effect can justify a
later root-budget increase in a named step; neither exhausted child allocation nor another
optimizer failure warrants ending the program. If learning still fails, review whether
measured signal and cost support a bounded redesign. If training improves but transfer
does not, investigate generalization rather than merely extending training. If contextual
and continued-M results remain unresolved, size a resolution before calling them equivalent.

**What to stop.** Stop sparse three-cell C mutations as the default follow-up. Stop treating
G's contextual advantage as learned context, or one-family transfer as family specificity.
Do not spend a whole cycle tightening M's 1.5× interval before resolving what the gain means.
Keep repeated G-versus-marginals baselines, uniform zero-hit sampling, threshold-veto
refinements, helper censuses and blind exhaustive bank screens off the immediate queue.
Do not weaken G or relax failed alias rules to manufacture headroom. Continue the program:
the contextual comparison deserves a feasibility probe and main study, and a second-family
direction remains a credible alternative if that route fails.
