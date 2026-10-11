---
next: strategy
---
# Decision: close 44, return to strategy

**Close [44](../../questions/10-compositional-map-transfer/44-restarted-tree-vs-a8/question.md).** The run
was complete and valid ([analysis](analysis.md), code review pass, commit `1773d11`) and landed on the
pre-registered PASS cell. Under the same restart schedule (up to 8 × 65,536 evaluations, cap 524,288), DG
mean evaluations R-tree ÷ R-A8 were **0.792 [0.682, 0.915]**. Solve rates were 765/768 vs 754/768, a
difference of +0.014 [0.000, 0.034], which meets the 3-point noninferiority guard (equality not shown).
Restarting also helped A8 itself (0.727× in cost, 83.6% → 98.2% solved). So question 43's A8 reliability
lead was mainly a full-cap schedule effect. Worker seconds reverse the evaluation result (tree ÷ A8 1.388
[1.196, 1.604]). A8's only remaining DG value on these rosters is therefore a time saving of about 2.5 s per
search, repaying acquisition after about 312 searches per build. TS (descriptive) favours restarted tree
about 5× in evaluations.

**Why `next: strategy` and no proposal.** Strategy 0024 funded exactly this one experiment and required an
exit to strategy after its result. Root 10's budget is now 36/36. The obvious successor is the
[tree-native fragment plan](../../plans/tree-native-fragment-learning.md), which would now be measured against
*restarted* tree GP. The strategy deliberately left that plan unallocated until this review, and it
would cost 7–10 h. That is an allocation decision, not a steward continuation. Root 23 and the parked root-01
questions do not meet their reopen conditions. Nothing in 44 supplies an inherited selection signal or
fixed-target evidence, so no other open question has budget or a case to propose into.

**Points for the strategist.**
- **Cost unit.** Evaluations and worker seconds now point in opposite directions. "Is A8 worth buying" depends
  on which unit the program values. The tree arm's 1.75× per-evaluation cost is an implementation property,
  not a search property. If the tree-native plan proceeds, I suggest fixing evaluations as the primary unit
  in advance and reporting seconds as the deployment unit.
- **Comparator.** Any learned increment inside tree GP should face R-tree (restarts with case redraw), not
  full-cap tree. That comparator already solves 99.6% of DG jobs at about 90k evaluations, so there is less
  headroom than 43 suggested.
- **Unseparated mechanism.** Part of tree GP's restart gain may come from redrawing training cases: 9.6% of
  its DG evaluations went to programs that were training-perfect but not exact. This matters for the core
  question only if a learned bias would be claimed to fix shortcutting. It is not a reason for a precision
  run.

**Digest check (critique 0024, notes 6–9) applied.** 43's metric is now named (no ≥ 1.5× geometric
advantage under 2 × cap; arithmetic savings remained). The TS magnitudes are corrected (A8 about 7.2×, tree
about 40.8× over G4; root-10 summary fixed, and the error noted in the root log). "Untuned" is replaced with
"mix selected on development cells, frozen before target scoring". "Estimated" is restored to A8's total-cost
claim in the digest.
