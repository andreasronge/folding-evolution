# Log — 57 order-helper arrangement

- 2026-10-11 (steward, 1628): opened on strategy 1628. Proposal: R-all vs R-hx (helper entries permuted within
  entry, four realizations per build) vs R-tree on the six development cells, 24 builds × 8 repeats, 1,152 jobs per
  arm. Primary Q = R-hx / R-all; material loss if lower > 1.25, retention if upper < 1.25 and R-hx / R-tree upper
  < 0.80. Read-only probes: same-library half-splits of 1228 R-all rows gave 0.93 [0.76, 1.17] and 1.02 [0.79, 1.29]
  (288 vs 288); enumeration of all admissible within-entry permutations (5-value proxy grid) found 135/177 helper
  entries can only become a single-input expression, 131 with exactly two admissible forms.
- 2026-10-11 (steward, 1628): critic approve_with_notes ([critique](../../../runs/2026-10-11-1628/critique.md):
  explicit 1228 counts; R-S speed is pessimistic, not a bound; incomplete grid = no verdict; narrower outcome
  language; a projection-valued entry is trivial as an expression but not evolutionarily inert);
  [plan](../../../runs/2026-10-11-1628/plan.md) took notes 1–4 and deferred digest notes 5–7 to the steward; code
  review pass ([review](../../../runs/2026-10-11-1628/code_review.md); minor: the rediscovery census needs a
  baseline in the other arms).

- 2026-10-11 (steward, 1628): **run** (commit `46e05cb`; queue 37 s prepare + 1,537 s score of 4,200 s;
  [analysis](../../../runs/2026-10-11-1628/analysis.md), [execution](../../../runs/2026-10-11-1628/execution.md)).
  24 saved R-all libraries rebuilt and hash-checked; 96 constructions (4 per build, all distinct), 708/708 helper
  slots replaced, max 16 of 256 draws, 613/708 projection-valued, all invariants and interpreter/VM checks passed.
  Grid 3,456/3,456 rows, seed-paired across arms, no failures. Capped means: R-tree 77.9 k (1,146/1,152 solved),
  R-all 30.0 k (1,151), R-hx 70.5 k (1,147). **Primary Q = R-hx / R-all 2.35 [2.07, 2.66]** (pooled capped means,
  8,192 whole-build bootstrap draws; reviewer's independent bootstrap [2.08, 2.66]) → pre-set branch **material
  loss** (lower > 1.25). R-hx / R-tree 0.90 [0.83, 0.98] (above the 0.80 retention bar); R-all / R-tree 0.38
  [0.34, 0.43], replicating 1228's 0.40 under a fresh seed namespace. Q > 1 in 24/24 builds (1.22–4.23; > 1.25 in
  23/24), 6/6 cells (1.61–3.03) and 4/4 realizations (2.20–2.57). Coverage strata (descriptive): R-all 0.78 / 0.41 /
  0.22 of R-tree for 0 / 1 / 2 needed helpers; R-hx 0.99 / 0.86 / 0.94, i.e. the gradient disappears; stratum-0 Q
  1.28 [0.98, 1.72] on 144 units, unresolved. Library draw and insertion rates equal in R-all and R-hx (≈ 245 and
  ≈ 110 per 1,000 evaluations), so the permuted entries were used, not filtered out. Rediscovery census: 100% of
  solvers in every arm contain a helper-valued subtree (targets are built from helpers), so it is uninformative;
  both cell-needed helpers as subtrees in 977 R-all, 899 R-tree, 826 R-hx solvers (descriptive). Solver sizes and
  compiled lengths matched across arms. The steward expected Q ≈ 1.5–2; the loss was larger, and R-hx kept less
  than R-all's no-helper stratum.
  Against the explanations: (a) intact helper computations — supported at this scope; (b) primitive supply in
  useful shapes and (c) other 2-cell content / trivia share — together worth at most a small residual (R-hx / R-tree
  upper 0.98, about a tenth of R-all's log saving by point), not separated from each other.

  Decision: close 57 because the pre-stated rule reached its "material loss" branch with the whole interval above 2
  and a consistent direction across builds, cells and realizations; more seeds would not change it. Scope: intact
  helper entries versus mostly projection-valued same-material entries, conditional on the rest of R-all, the six
  development cells of `x4-order-v1`, half-library donors and 8 × 65,536 restarted tree GP. Not shown: that min/max
  beat other nontrivial computations, which helpers or how many carry the saving, or anything about a fresh bank.
  Root 10 is at 47/47 and strategy 1628, the plan and the proposal route every outcome back to strategy. See the
  [decision](../../../runs/2026-10-11-1628/decision.md).

- 2026-10-11 (steward, 1736): wording correction after [critique 1736](../../../runs/2026-10-11-1736/critique.md)
  (digest check, notes 6–7); the 1628 entry above stays as written, read it with these corrections. No numbers change.
  - "(b) … and (c) … together worth at most a small residual" overstates: the experiment permuted the helper entries
    only; it did not remove primitive supply or other content separately, nor rule out interactions or harm from the
    replacement entries. Read: "the complete permuted library retains a small net saving (R-hx / R-tree 0.90
    [0.83, 0.98], a point saving of 10%, interval about 2–17%); contributions of unchanged content and its
    interactions with the replacement entries are unidentified."
  - "The gradient disappears" overstates a descriptive flattening: R-hx strata 0.99 [0.77, 1.36] / 0.86 [0.74, 0.99]
    / 0.94 [0.82, 1.08] with no gradient-equivalence test. Read: "the strong intact-library gradient was not apparent
    in the permuted-library point estimates." question.md updated accordingly. The close decision is unchanged.
