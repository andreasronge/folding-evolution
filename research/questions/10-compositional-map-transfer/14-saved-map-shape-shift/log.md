# Log: 14-saved-map-shape-shift

- 2026-10-06 (run 2026-10-06-1400, proposal): opened from strategy 1400. Pre-registered check
  of 0811's unregistered branch/linear shift on the "b" continuations, with residual ablation
  and a frequency-matched token-only control. Steward probe: an exact G-based token-only match
  to each R map's emitted token frequencies exists within the multiplier bound (12/12 maps,
  TV < 1e-4; `runs/2026-10-06-1400/steward_probes/marginal_fit.py`).

- 2026-10-06 (run 2026-10-06-1400, result): critic approve_with_notes (five interpretation notes:
  add the solve-count forecast; separate a relative shift from a branch gain using the BE and LIN
  R / R_fm intervals; scope "beyond token frequencies" to pooled emitted frequencies under uniform
  alleles; make row 3 a bound, not "noise"; require all six starts; BE wins were 5/6, not 6/6).
  Auto-approved, then **blocked before running**: the driver could not merge main into
  research/main (add/add conflict on `runs/2026-10-06-0811/code_review.md`). No code, no data, no
  slot used. Decision: keep 14 open and re-propose the same design as run 1419 with the critic's
  notes applied, because nothing about the question or its feasibility changed and the blocker is
  a one-file merge fix.
