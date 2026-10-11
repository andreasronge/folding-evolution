---
status: closed
tags: [compositional-transfer, tree-gp, restarts, library-learning, external-fitting, order-helpers, mechanism, donor-arrangement]
budget: {experiments: 1, used: 0}
---
# Do the acquired order helpers need their learned arrangements?

Opened 2026-10-11 by the steward on [strategy 1628](../../../runs/2026-10-11-1628/strategy.md) and the
[helper-arrangement plan](../../../plans/order-helper-arrangement.md). Meets the reopen trigger of
[53](../53-order-library-cap-release/question.md) (a decision needs what carries R-all's saving), recorded here as a
distinct mechanism comparison; 53 and [56](../56-order-library-protected-cells/question.md) stay closed as references.

Current summary: **closed after run 2026-10-11-1628 (commit `46e05cb`): yes, at this scope — rearranging only the
helper entries removed most of R-all's saving.** The 24 saved R-all libraries were kept byte-identical except their
177 helper-valued entries (4–10 per build), whose labels were permuted within each entry's own arity/width pools until
no subtree computed any of the twelve helpers on D625 (same material, shape, slots and draw probability; four
realizations per build; 613/708 replaced slots became single-input projections). Six development cells of
`x4-order-v1`, 24 builds × 8 repeats, 1,152 seed-paired jobs per arm, complete grid.

- **Q = R-hx / R-all 2.35 [2.07, 2.66]** (ratio of pooled capped arithmetic means, whole-build bootstrap) → pre-set
  branch *material loss* (lower > 1.25). Above 1 in 24/24 builds, 6/6 cells and 4/4 realizations.
- R-hx / R-tree 0.90 [0.83, 0.98]; R-all / R-tree 0.38 [0.34, 0.43] (replicates 0.40 from 1228). The residual
  saving after permutation is small (upper bound below 1, above the 0.80 retention bar).
- With helpers permuted, the strong intact-library coverage gradient was not apparent in the point estimates (R-hx
  0.99 [0.77, 1.36] / 0.86 [0.74, 0.99] / 0.94 [0.82, 1.08] of R-tree for 0 / 1 / 2 needed
  helpers; R-all 0.78 / 0.41 / 0.22). Whether R-all's small no-helper-stratum saving is also helper-borne is
  unresolved (stratum Q 1.28 [0.98, 1.72], 144 units).
- Solve counts R-tree 1,146, R-all 1,151, R-hx 1,147 of 1,152. Permuted entries were drawn and inserted as often as
  the originals.

Competing explanations for R-all's saving:
(a) intact helper computations — supported: the material loss;
(b) supply of order primitives (GT, IF_GT, inputs) in useful shapes, whatever their arrangement, and
(c) other recurrent 2-cell content and a lower trivia share — not removed separately: the complete permuted library
retains a small net saving (R-hx / R-tree 0.90 [0.83, 0.98]), and the contributions of the unchanged content and its
interactions with the replacement entries are unidentified.

Not shown: that min/max beat *other nontrivial* computations of the same material (the control is mostly trivial
projections; matched nontrivial alternatives mostly do not exist for six-node entries); which helpers, or how many
per build, carry the saving (all permuted together); whether search reconstructs helpers (the solver census is 100%
in every arm because the targets are built from helpers); anything on a fresh bank or under another search regime.

Related: [53](../53-order-library-cap-release/question.md), [56](../56-order-library-protected-cells/question.md),
[47](../47-tree-donor-arrangement/question.md) (whole-library label permutation on gate-sum: B/C retained, A lost),
[48](../48-tree-donor-label-supply/question.md), [52](../52-order-helper-acquisition/question.md),
[54](../54-rectified-sum-acquisition/question.md) (rectifier sources routed around the helper),
[proposal](../../../runs/2026-10-11-1628/proposal.md), [analysis](../../../runs/2026-10-11-1628/analysis.md),
[decision](../../../runs/2026-10-11-1628/decision.md), [log](log.md).

Reopen if: (closed) a decision needs helper versus nontrivial non-helper content of matched material (needs a
different matching rule, e.g. larger entries or matched-size nontrivial donors); a decision needs per-helper or
dose attribution (permute a subset of helper entries per build, same 1,152-per-arm size, saved libraries, no new
acquisition); or the same intervention is wanted on a fresh content family (a new question under root 10).
