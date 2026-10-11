# Log: 53 order-library cap release

- 2026-10-11 (steward, 1228): opened; proposal [run 1228](../../../runs/2026-10-11-1228/proposal.md). Read-only
  re-derivation from saved 1129 libraries: uncapped pools 22–32 classes; needed-helper coverage 31/48 cell × builds
  (R-S 3/48). 1129 pair SD of log cost ratio R-S/R-tree 1.88 nats; per-build arithmetic ratio spread 0.46–2.22.

- 2026-10-11 (steward, 1228): **experiment run** (slot 44, commit `60ab766`, code review pass, queue 14.6 min of
  110 approved; [analysis](../../../runs/2026-10-11-1228/analysis.md), [execution](../../../runs/2026-10-11-1228/execution.md)).
  24 new acquisitions from the frozen 1129 roster (1,152/1,152 source jobs solved; 214 k evaluations, 13.3 worker-s
  per build); R-S 16 entries, R-all 25–37 (median 28), R-all's first 16 equal R-S in every build. Scoring: 4 arms ×
  6 development cells × 24 builds × 4 repeats, 2,304/2,304 rows, seeds paired; protected cells unsearched.
  Capped arithmetic means: R-tree 73.1 k (574/576 solved), R-order 4.0 k (576), R-S 89.9 k (572), R-all 29.3 k (576).
  **Primary R-all / R-tree 0.40 [0.32, 0.50]** (ratio of pooled means, whole-build bootstrap, 8,192 draws; a second
  bootstrap seed gave [0.31, 0.50]). Plan precedence: lower 0.32 is not > 0.67; upper 0.50 < 0.80 → **useful
  acquisition**. R-all / R-S 0.33 [0.27, 0.39]; R-S / R-tree 1.23 [1.07, 1.41]; R-all / R-order 7.27 [5.49, 9.81];
  R-order / R-tree 0.055 [0.043, 0.067]; geometric R-all / R-tree 0.24 [0.20, 0.29]. Per build 24/24 below 1
  (20/24 below 0.67); per cell 0.35–0.47. Gap to R-order recovered about 0.47 (geometric). Break-even against
  R-tree 4.9 [3.8, 6.5] searches (evaluations), 4.2 [3.2, 5.7] (worker-s). Descriptive: needed helper in pool
  126/144 cell × builds (R-S 14/144), both 53/144 (R-S 0); cost by coverage 0 / 1 / 2 helpers: 0.77 [0.50, 1.12],
  0.45 [0.37, 0.54], 0.23 [0.17, 0.31] of R-tree; needed-helper entry in 382/576 R-all solvers vs 43/572 R-S.
  This was the proposal's named surprise (R-all ≤ 0.5×); the steward had expected 0.8–1.0×.
  Read against the explanations: dilution (a) did not cancel the gain; unused helpers (b) not supported
  (descriptive); coverage (c) is a residual limit in 18/144 pairs. Cap removal is the intervention; helper
  causality is not isolated (sizes, content and trivia share of draws changed together; the no-helper stratum is
  also cheaper than R-S, 0.58 [0.41, 0.76]).

  Decision: close 53 because the pre-registered rule answered its question at its stated scope — keeping every
  eligible recurrent semantic class turned acquisition into a large, build-consistent saving over R-tree on the
  development cells — and the plan routes this outcome back to strategy with a protected-stage case, which needs
  new budget (root 10 is at 44/44). The next-step options and my recommendation are in the
  [decision](../../../runs/2026-10-11-1228/decision.md).
