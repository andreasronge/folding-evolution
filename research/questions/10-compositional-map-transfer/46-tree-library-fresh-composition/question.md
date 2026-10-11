---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, acquisition-cost, independent-inputs, fresh-bank]
budget: {experiments: 1, used: 0}
---
# Do frozen DG-acquired subtree libraries make restarted tree GP cheaper on a fresh composition shape?

Current summary: **closed (run 2026-10-11-0348, commit `1f02bb7`): yes, as a search-cost saving on this fresh
shape. On 18 protected cells of `x4-gate-sum-v1` (`(Xa+Xb)>(Xc+Xd) ? Xe+Xf : Xg`, frozen with the method before
any protected search), the 24 unchanged 0150 libraries cut restarted tree GP's mean evaluations to 0.250×
[0.217, 0.289] of R-tree's (69,442 → 17,346) and to 0.291× [0.231, 0.372] of size- and length-matched random
donors; no reliability loss observed (1,728/1,728 vs 1,726/1,728 solved) and the registered 3-point
noninferiority guard passed (lower bound 0.000).** Lower in 18/18
cells and 24/24 builds; worker seconds agree (0.234×); with the 0150 acquisition charged a library repays after
about 55 [49, 62] gate-sum searches.
- The gain is strongly split-dependent: 0.055× [0.042, 0.071] on the split whose predicate the libraries learned
  on DG, where about half the solvers contain that predicate verbatim; 0.363× [0.299, 0.434] and 0.338× [0.287,
  0.400] on the two splits no learned predicate covers, where large entries rarely survive verbatim. Quote the
  pooled 0.25 only with these.
- Later ([47](../47-tree-donor-arrangement/question.md)): label-rearranged libraries kept the B/C gain (R-perm ÷
  R-lib 1.03 [0.85, 1.23]) and lost A's extra gain (5.1×), so A's extra gain needs the learned arrangement.
- Not separated: what carries the ≈ 3× floor on the unlearned splits (pair sums, small entries, or an
  input/`ADD` frequency shift the size control does not match). The size control's own effect is unresolved
  (R-size ÷ R-tree 0.860× [0.716, 1.011]).
- The three builds without a 7-node predicate gained less (0.32–0.54 vs mean 0.23; n = 3, observation).

Competing explanations:
- (a) the libraries carry reusable parts (pair sums, comparison skeleton) that a new composition can use:
  R-lib cheaper than R-tree and R-size on protected cells of every pair split;
- (b) the DG gain was specific to DG's composition (predicate-plus-readout); on a new shape the donors
  add little or crowd the 32-token cap: R-lib ≈ R-tree;
- (c) any gain is donor size/repetition, not content: R-lib ≈ R-size < R-tree.

Reading: (a) supported at this scope, in every pair split and beyond the size control; the relative gain is
much larger on the predicate-matched split (0.055× vs 0.34–0.36×), though that split carries only about 43% of
the pooled evaluation savings; (b) not supported; (c) not supported for content beyond this size control.

Scope: one fresh shape built from the libraries' own parts (reuse across composition, not unfamiliar
content); one acquisition cohort on DG sources; one extractor, rate and restart schedule. Two development cells were probed before the freeze; protected
cells are now spent, so the bank is a development bank from here on.

Opened and closed 2026-10-11 (steward, run 2026-10-11-0348) on [strategy 0348](../../../runs/2026-10-11-0348/strategy.md)
and its [plan](../../../plans/tree-library-fresh-composition.md). Slot 38 of root 10.

Related: [45](../45-tree-subtree-library/question.md), [44](../44-restarted-tree-vs-a8/question.md),
[26](../26-then-addition-fresh-bank/question.md), [37](../37-cheap-bias-fresh-transfer/question.md) (earlier
fresh-shape tests), [proposal](../../../runs/2026-10-11-0348/proposal.md), [analysis](../../../runs/2026-10-11-0348/analysis.md),
[decision](../../../runs/2026-10-11-0348/decision.md), [log](log.md).

Reopen if: (closed) a later experiment shows the gain is an artefact of this bank's construction (e.g. a
replication on another gate-sum roster or cohort falls below 0.90×), or a donor-ingredient test needs this
bank's per-split contrast re-measured.
