---
estimated_minutes: 65
---

Implement the approved [proposal](proposal.md) without adding targets or learning new maps. This is implementation of an approved design, not a new preregistration or findings promotion. Read the researcher role and CLAUDE.md; approval is autonomous critic approval. No code_review.md or driver_feedback.md exists at preparation time.

Conditions: 55 frozen maps: G, M1–M6, and M+, R, residual-zero R_abl, and deterministic frequency-matched R_fm for each of 1a–6b. Load the 0132 and 0811 saved maps with hash checks. R_fm uses G rows and bounded (±ln 16) log token multipliers, fitted to exact expected emitted frequencies over L=32 uniform-allele tape positions, then production normalization. Keep a fit only if post-normalization TV <0.005; retain failures as missing controls in the report.

Evaluate the two frozen branch-else (BE) and six frozen linear (LIN) cells using the existing D1331 harness, P=256, L=32, crossover=0.7, lexicase and cap=524288 evaluations. Use 200 fresh, shared seeds per cell starting at base 1419000000. As in the existing 0811 harness, the same seed range is shared across cells as well as across maps; there is no cell-index offset. Record this convention in metadata. Order: G on all cells once; b pairs by complete start; a pairs by complete start; M1–M6. Ten workers, expected ~53 minutes search time plus fitting/reporting overhead; one queue entry with a 9000-second timeout. A deadline leaves only complete starts eligible for inference.

Measurements: append per-search exact solve, evaluations, penalized log2 cost (unsolved=log2(2×cap)), seed, cell, map identity/hash, and worker elapsed time. Save maps, all parameters and source provenance; report per-pair solved counts, cell costs, exact IF_GT frequencies, R−M+ IF_GT differences against shifts, G costs and M/G ratios. BE and LIN costs are equal-weight cell means. Ratios X/Y=2^(cost_Y−cost_X); shift=BE ratio/LIN ratio. Report R/M+, R/R_fm, R/R_abl and R_fm/M+.

Intervals: one log2 contrast per start; 95% t interval, df=5, across exactly six starts. Primary layer uses b only. Pooled layer averages a/b within each start and remains distinct because a selected the lead. Always report b-only dependency beside pooled dependency. Missing starts or frequency fits make the affected layer unresolved; never lower df or silently drop starts.

Gate/outcomes (first match, exactly as approved):

- Row 0: any source hash mismatch, G eight-cell mean >0.6 log2 from 0811 G, or fewer than six complete b starts: no verdict. G searches are reused as reference.
- Row 1: b BE R/M+ lower >1 and shift lower >1: conditional BE gain and shift replicate on the same M starts.
- Row 2: shift lower >1 but BE lower ≤1: relative shift only; call it a linear loss only when LIN upper <1.
- Row 3: shift lower ≤1, shift upper <1.41 and BE upper <1.25: no replication at the prior size, bounded effects rather than absence.
- Row 4: otherwise unresolved; report intervals and move on.

Dependency first match: D-a when R/R_fm shift lower >1 (residual contribution beyond matched pooled uniform-allele marginals); D-b when that shift upper <1.25 and R_fm/M+ shift lower >1 (frequencies reproduce shift with bounded residual increment); otherwise D-c unresolved. Under D-a residual branch help requires BE R/R_fm lower >1; otherwise it is only a trade-off. R/R_abl alone attributes nothing because it also changes frequencies. Neither layer establishes family specificity, positional or selected-population frequencies, or solver supply versus mutation effects.

Downstream: row 1+D-a with BE residual gain supports a full contextual arm; row 1+D-a trade-off, row 1+D-b or row 2 prioritizes token learning with context secondary. Row 1+D-c retains context secondary with R_fm control. Row 3 drops the lead at its bounds. Row 4 records uncertainty without a precision loop. The steward closes question 14 and returns to strategy; this implementation does not edit research questions or digest.

Critique addressed: preserve exact design and realistic runtime; measure novel control/ablation feasibility in smoke; retain evaluator TV validation, hashes, G gate, complete-start requirement, b versus pooled distinction, branch-help versus linear-penalty distinction and bounded-null language. Critic requested no additional changes.

Before full queue preparation, smoke-test loading/fitting, deterministic seeds, controls and representative search cells at small scale. If observed target reachability, rates or projected runtime invalidate the approved design, write infeasible.md with measurements, commit and stop for steward replanning. Smoke is infrastructure/feasibility only and cannot yield a scientific verdict.

Preparation result: the all-map/all-cell smoke used four seeds per cell, offset +10000000 from the full seeds, at the approved search cap. All 1760 searches completed in 100.44 seconds (421.85 summed worker seconds), with 1757 solves; all three failures were BE. All twelve fits passed (TV 0.000029–0.000070); G differed by +0.0131 log2 from the prior mean. Worker-time extrapolation is 35.2 minutes at ten workers, below the proposal's 53-minute forecast. This small probe supports feasibility; it cannot establish precise solve rates. Retain the original 65-minute expected queue estimate to allow search variation and overhead, and the approved 2.5-hour timeout. Focused tests and recorded smoke evidence: [validation.md](validation.md).
