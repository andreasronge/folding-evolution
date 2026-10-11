# Log — 56 order-library protected cells

- 2026-10-11 (run 1530): opened by the steward on strategy 1530. Proposal: frozen 1228 R-all libraries (24 builds)
  vs R-tree and R-order on the 24 protected `x4-order-v1` cells, 2 repeats, fresh paired seeds.
- 2026-10-11 (steward, 1530): critic approve_with_notes ([critique](../../../runs/2026-10-11-1530/critique.md):
  state rule precedence and an exact reliability count; timeout fallback only on a complete balanced repeat 0;
  charge 13.3 worker-s/build); [plan](../../../runs/2026-10-11-1530/plan.md) took notes 1–5; code review pass
  ([review](../../../runs/2026-10-11-1530/code_review.md)).

- 2026-10-11 (steward, 1530): **run** (commit `53f0e06`; queue 29 s prepare + 1,073 s score of 6,900 s;
  [analysis](../../../runs/2026-10-11-1530/analysis.md), [execution](../../../runs/2026-10-11-1530/execution.md)).
  The 24 saved 1228 R-all libraries (rebuilt from their corpora, byte-identical, hash `375c7b69…`), unchanged
  method, bank hash `2fc0d88c…d74a`; 24 builds × 24 protected cells × 2 repeats × 3 arms = 3,456/3,456 rows,
  seed-paired, no collision with 302,283 historical seeds; both repeats complete, fallback not used.
  Capped arithmetic means: R-tree 85.9 k (1,146/1,152 solved), R-all 32.0 k (1,152), R-order 4.6 k (1,152).
  **Primary R-all / R-tree 0.37 [0.33, 0.42]** (pooled means, 8,192 whole-build bootstrap draws; second seed
  [0.329, 0.419]). Plan precedence: lower 0.33 is not > 0.67; upper 0.42 < 0.80 and R-all has 6 *fewer* unsolved
  units than R-tree (allowance 12 more) → **useful held-out saving**. Worker-s 0.38 [0.33, 0.42]; geometric 0.21
  [0.18, 0.25]; R-all / R-order 6.9 [5.7, 8.6]; about half (0.49) of the R-tree → R-order log gap recovered
  (1228: 0.47). Per build 24/24 below 0.67 (0.20–0.65); per repeat 0.374 / 0.371. Strata (descriptive):
  disjoint 0.34 [0.25, 0.45] (4 cells), overlapping 0.38 [0.33, 0.42] (20). Per cell 0.18–0.61, 23/24 intervals
  below 1 (`lo23+hi03` 0.61 [0.27, 1.17], 48 units). Coverage strata (post-hoc, sizes and content vary with it):
  0 / 1 / 2 needed helpers present 0.74 [0.57, 0.93] / 0.42 [0.37, 0.48] / 0.19 [0.16, 0.24] (1228: 0.77 / 0.45 /
  0.23). Needed-helper entry contained in 801/1,152 R-all solvers vs 273/1,146 R-tree (containment, not ancestry).
  Break-even against R-tree 4.0 [3.4, 4.6] searches (evaluations), 3.3 [2.9, 3.9] (worker-s), charging 214 k
  evaluations / 13.3 worker-s per build. Protected R-tree was dearer than development (85.9 k vs 73.1 k) while
  R-all barely moved (32.0 k vs 29.3 k). The steward expected 0.40–0.55; the named surprises (upper ≥ 0.80, a
  stratum with R-all dearer) did not occur.
  Against the explanations for shrinkage: none was needed. (a) roster luck: the held-out estimate is not weaker
  than development (0.37 vs 0.40, intervals overlap; no direct shrinkage contrast was computed, so "no shrinkage"
  means none visible, not equality); (b) coverage of protected cells matched development (15/48/37% vs 13/51/37%);
  (c) cell-specific non-helper content cannot have carried this saving, since no library saw these cells, but
  non-helper content still contributes (the 0-helper stratum is 0.74 [0.57, 0.93]).

  Decision: close 56 because the pre-stated rule answered the question at its scope: the frozen, unrefitted R-all
  libraries lowered search cost on all 24 held-out order combinations about as much as on the six development
  cells, with no reliability loss. Scope: held-out cells of the development bank `x4-order-v1`, the same twelve
  helpers, one acquisition recipe; not fresh-bank transfer, not helper causality, not superiority to R-order
  (6.9× cheaper). Root 10's budget is now 46/46 and both the strategy and proposal route this outcome back to
  strategy; no further experiment is allocated. See the [decision](../../../runs/2026-10-11-1530/decision.md).
