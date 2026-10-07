---
verdict: pass
---

# Code review — 2026-10-07-0821 (rank-one context vs token continuation)

Reviewed commit `f61aec4` against `5312e96` (three new modules, one test file, task
folder), plus proposal.md, critique.md, plan.md, queue.yaml and the preparation
evidence. Re-ran `tests/test_rank_one_learning.py` (10 passed) and ruff in the
worktree. No blocking issues.

## What was checked

- **Arm wiring.** T forces token steps; C draws token/context at ½, b-steps at zero
  residual and a-steps at ½ once b ≠ 0, with redraw of no-op context steps. Both
  arms start from the same saved table (verified in code against the 1723 table and
  hash), get 2 parents + 6 children per generation, keep the cheapest 2, and spend
  exactly 8·n·G + 200 = 4 040 searches each; `validate_fresh` rejects any other budget.
- **Seeds.** Calibration seeds `base + si·1e5 + ci·1e3 + block·500 + j` are disjoint
  across all 29 184 searches (parent and each mutant have their own blocks; the test
  asserts this). Learning seeds `base + pair·1e4 + gen·100 + j` and the cell rotation
  are identical for T and C within a generation; mutation streams differ by arm.
  Final-selection and fresh seeds are separate namespaces, fresh seeds shared across
  S/T/C/C0/G4. The 1.821–1.827 × 10⁹ range does not intersect any earlier harness I
  could find (map_learning 1.32e8, assembly 2.6e8, contextual 8.1e8, saved_shape
  1.419e9, 1723 inner seeds ≥ 1.7e10). Smoke/probe offsets (+1e7/+2e7) stay inside
  the namespace and never feed the full run.
- **Metrics.** `log_cost` with unsolved = 2·cap at every stage. "C/T" = mean of
  log2(cost_T) − log2(cost_C) over own cells × shared seeds, so positive means
  context helped; T/S, C/S, C/C0, C0/T have the same sign convention. `balanced()`
  implements the family-balanced mean, SE = ½√(s²_BE/n_BE + s²_PA/n_PA), t on
  n_BE + n_PA − 2 df. Outcome rows are applied in the proposal's order; U on any
  validation failure or < 6 pairs per family.
- **Leakage.** `job()` rejects any non-training cell; only id + labels enter a
  search payload; holdouts are never loaded; grammars are loaded only in the
  report for the cosine readout.
- **Calibration estimator.** σ²_T = within-unit cov(Δ_A, Δ_B) pooled over units;
  Γ uses max(0, cov) as the plug-in while the raw covariance and its interval are
  reported; selected-quarter uses lowest Δ_A (full 48 and first 24, which are
  cell-balanced because rows are sorted by seed and rotation is 0), evaluated on the
  independent B block; the bootstrap resamples paired A/B mutant records within
  units and repeats selection (the test cross-checks it against a manual bootstrap).
  Sign of Γ = (1/n)·max(0, 1.27σ²/√(σ² + 2v/n) − μ) is right given Δ < 0 = better.
- **Gates.** There is no stop gate; Stage B always runs, as the critic required.
  The only data-driven choice is n ∈ {24, 48}, which changes depth vs precision
  but not the budget, so an unstable choice cannot prevent the main stage. The
  size grid matches the proposal.
- **Admission and time.** Reserve = 1.3 × (first pair from Stage A's slowest
  operator:family rate, later pairs from the slowest completed pair) + 1.3 × fresh
  scoring for completed pairs **and the prospective pair and the 500-search G4
  anchor** + 180 s, checked against the 13 680 s internal deadline; the queue
  timeout is 14 400 s. At the probe's rates Stage A ≈ 30 min, 16 pairs ≈ 133 min,
  fresh ≈ 26 min, leaving about 70 min of slack. Admission order BE1, PA1, … and
  stop-at-first-refusal are enforced by `validate_fresh`.
- **Critique points 1–5** are implemented (prospective-pair/G4 reserve, slower-B
  rescaling, nonnegative Γ plug-in with raw covariance reported, paired-bootstrap
  reselection, parent-relative vs selected-minus-all gain, row 3 "neither arm"
  flag conditioned on C/S, clipping qualification with post-clipping column means
  and clip counts). Points 6–7 concern belief files already corrected; plan.md
  says so.

## Blocking issues

None.

## Minor notes (no change required before the run)

1. **Effort-choice stability is not logged.** `choose_effort` runs on the pooled
   point estimate only. Cheap improvement: apply it inside the existing bootstrap
   loop and record the fraction of replicates choosing n = 48, so the analysis can
   say whether n was a coin flip. Both branches are approved designs with equal
   budgets, so this is diagnostic, not a gate.
2. **Stage A overhead factor is slightly inflated.** `wall_total` includes the
   parent batches' wall time but `collected` excludes parent rows, so the overhead
   ratio is ~5% too high. This only makes `slow_a` and the reserves more
   conservative.
3. **`slow_b` is an arm-level mean, `slow_a` a per-operator:family max.** The
   comment in `evolve_pair` says the grains match; they do not. Because `slow_a`
   is a max over groups it will usually dominate, so the fresh projection stays
   conservative; the grain mismatch only matters if B becomes much slower than A.
4. **Fresh scoring is all-or-nothing.** A deadline hit during the final batch
   raises and skips the report; rows are retained in `search.jsonl` (phase
   `fresh`) and jobs are submitted pair by pair after G4, so complete pairs could
   still be analysed by hand. The 1.3× reserve plus ~70 min slack makes this
   unlikely.
5. **Per-search variance v includes between-cell spread.** Blocks are
   cell-balanced, so the noise in a block mean is really the within-cell variance.
   On the 65k probe rows the total/within ratio is 1.00–1.06 (one group 1.34), so
   the effect on Γ is negligible here.
6. Generation 0 evaluates four identical tables per seed (both parents of both
   arms equal the start map). This is the approved design and keeps the budgets
   equal; it just spends 2·n searches per pair on known-equal scores.
