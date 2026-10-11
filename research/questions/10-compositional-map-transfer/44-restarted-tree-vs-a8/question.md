---
status: closed
tags: [compositional-transfer, baseline, tree-gp, restarts, external-fitting, acquisition-cost, independent-inputs]
budget: {experiments: 1, used: 0}
---
# Under the same restart schedule, does acquisition-free tree GP remove A8's remaining DG advantage?

Current summary: **closed (run 2026-10-11-0024, commit `1773d11`): under the same restart schedule
(up to 8 attempts of 65,536 evaluations, total cap 524,288), restarted tree GP spent fewer evaluations than
restarted A8 on DG and was noninferior in reliability within the prespecified three-point margin (equal
reliability not established); in worker seconds A8 stayed cheaper.** Development
rosters, saved 1717 builds, one cutoff.
- **DG (primary, 768 jobs per arm)**: mean evaluations R-tree ÷ R-A8 **0.792 [0.682, 0.915]** (paired
  24-build bootstrap); solved 765/768 vs 754/768, difference +0.014 [0.000, 0.034] (noninferiority within
  3 points; equality not shown). Tree cheaper in all 8 cells and 20/24 builds. Pre-registered PASS cell.
- **Worker seconds reverse it**: 1.388 [1.196, 1.604] (tree 98 µs per evaluation, A8 56). R-A8 saves about
  2.5 s per search and repays its historical acquisition after about 312 [211, 579] searches per build (never
  on 6 builds). In evaluations A8 never repays.
- **Restarts helped A8 too**: R-A8 ÷ full-cap A8 0.727 [0.647, 0.814], solved 98.2% vs 83.6%. So 43's A8
  reliability lead (314 vs 202 of 384) was mainly a full-cap schedule effect.
- **TS (descriptive)**: R 0.181 [0.159, 0.202], worker seconds 0.265; both 768/768.
- Tree GP's restart gain may partly come from redrawing training cases (9.6% of its DG evaluations went to
  training-perfect, non-exact programs); not separated from population reset.

Reading: the restarted comparison favours tree GP in evaluations at this schedule; (b)'s stagnation/shortcut
mechanisms remain hypotheses (the comparison does not test them). (a) survives only as a worker-time saving.
Tree hazards are consistent with the independence projection (per-attempt success flat), so (c) gets no support
for tree GP; A8's slight shortfall is consistent with build heterogeneity (not a test ruling out dependence).
Background: [43](../43-acquired-bias-vs-tree-gp/question.md) left frozen A8 with better full-cap DG
reliability and an arithmetic saving of about 86k evaluations per search; a post hoc projection from 2254's
rows ([planning audit](../../../runs/2026-10-11-0024/planning-audit.json), [proposal](../../../runs/2026-10-11-0024/proposal.md))
predicted the restarted ratio (0.78) closely.

Competing explanations:
- (a) A8's DG reliability reflects learned family content that a restarted generic search cannot replace:
  restarted A8 cheaper than restarted tree GP;
- (b) A8's advantage was mainly tree GP's late stagnation (32-token crowding, D625 shortcuts on fixed
  training cases), which restarts with new training cases remove: restarted tree GP cheaper at equal
  reliability;
- (c) restart attempts are not independent (failures recur within a cell), so neither projection holds.

Scope: development data (8 DG spare cells of `x4-double-gate-v1`, 8 TS targets of `x4-branch-sum-v1`),
saved 1717 builds, frozen 2254 tree configuration (mix 0.5), one fixed cutoff. Complete procedures, not a
causal effect of learning, and not an optimal restart policy.

Opened 2026-10-11 (steward, run 2026-10-11-0024) on [strategy 0024](../../../runs/2026-10-11-0024/strategy.md)
and its [plan](../../../plans/restarted-tree-acquisition-value.md). Slot 36 of root 10.

Related: [43](../43-acquired-bias-vs-tree-gp/question.md) (baseline), [run 2254 analysis](../../../runs/2026-10-10-2254/analysis.md),
[tree-native learning plan](../../../plans/tree-native-fragment-learning.md), [run 0024 analysis](../../../runs/2026-10-11-0024/analysis.md),
[run 0024 decision](../../../runs/2026-10-11-0024/decision.md), [log](log.md).

Reopen if: a decision comes to depend on (i) the restart comparison at another cutoff or a Luby-type
schedule, (ii) separating training-case redraw from population reset in tree GP's restart gain, or (iii)
restarted A8 against restarted tree GP on a fresh bank frozen with both procedures, or under a size-aware or
larger-limit tree GP. The saved 0024 rows answer descriptive follow-ups without new search.
