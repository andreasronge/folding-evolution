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

- 2026-10-06 (run 2026-10-06-1419, result): same design with the 1400 critic's notes applied;
  critic approve_with_notes (asks for BE R/R_fm *95% lower bound* > 1 in the full-arm rule, and
  D-a read as "residuals contribute beyond matched pooled emitted frequencies", not "the shift
  needs residuals"). Auto-approved, then **blocked again before running** by the same add/add
  conflict. No code, no data, no slot used. The steward then committed main's second-pass
  review onto research/main (`e37c4a7`); `git merge-tree` now merges main into research/main
  cleanly. Decision: keep 14 open and re-propose the same design as run 1425 with the 1419
  notes applied, because the design was approved twice, nothing was learned, and the blocker
  is now removed.

- 2026-10-06 (correction, from the 1419 critique's digest check): the 1400 proposal entry above
  says an "exact" G-based token-only match exists. Read instead: all twelve G-based token-only
  controls match R's emitted token frequencies within the stated tolerance (TV < 1e-4 in the
  probe; 0.000029–0.000070 after production `normalize()`); the emitted frequencies are
  computed exactly, but the fitted distributions are not exactly equal.

- 2026-10-06 (run 2026-10-06-1425, result): ran as approved (commit `b397f72`, 88 000 searches,
  48 min, all 55 maps × 8 cells × 200 fresh seeds complete; gate passed, G within −0.05 log2 of
  0811; 12/12 R_fm fits TV ≤ 7e-5; every linear cell 200/200 solved, censoring only on
  `S?M:(S+m)`, learned maps 193–200/200). **Outcome row 3**
  ([analysis](../../../runs/2026-10-06-1425/analysis.md)). On the six "b" pairs, R / M+ on BE
  0.94× [0.77, 1.16], LIN 1.29× [0.88, 1.91], shift 0.73× [0.57, 0.94]; the shift is below 1 in
  6/6 starts, i.e. opposite to "a". Re-scored on the same fresh seeds the "a" maps repeat 0811
  (shift 1.86× [1.41, 2.44], BE 1.24× [0.92, 1.68]), so the "a" pattern is a stable property of
  those six map pairs, not seed noise; what fails is the learner-level claim. Dependency (read
  descriptively, since rows 1–2 did not match): "b"-only R / R_fm BE 1.04× [0.91, 1.17], shift
  1.02× [0.92, 1.12] (D-c), and R_fm / M+ shows the same reversed shift as R / M+ (0.72×
  [0.54, 0.95]); pooled D-a (shift 1.23× [1.11, 1.36]) is carried by the selected "a" maps, with
  BE R / R_fm lower bound 0.97. Exact IF_GT emitted frequency does not track the shift (r = 0.28,
  n = 12). Side result: against their M starts both learners got faster on BE in both letters
  (M+ / M 1.40× "a", 1.42× "b"; R / M 1.74×, 1.34×; lower bounds 1.05–1.10). Decision: close 14,
  because row 3 answers it at the stated bounds: the branch/linear shift is not a reproducible
  property of the contextual learner from these starts (it differs between learning runs in
  sign), and on the unselected "b" maps a G-context token-only map with R's pooled emitted
  frequencies reproduces R within about 1.17× (BE) and 1.12× (shift). Context gets at most a
  secondary arm in the four-reducer study. Root 10 is at 5 of 7; return to strategy as strategy
  1400 asked.
- 2026-10-06 (critique 1536, notes 5–8): wording corrections applied to this question, root 10 and
  the digest. "R_fm reproduces/matches R" → not resolved from R (R's advantage bounded to about
  17% on BE, 12% on the shift). The pooled residual shift is resolved, but its linear (0.94×
  [0.87, 1.03]) and BE (1.16× [0.97, 1.39]) parts are not resolved alone. "Not of the learner"
  → a consistently positive learner-level shift was not demonstrated. The IF_GT line above
  should read: no association was resolved (r = 0.28, n = 12), which does not exclude one.
- 2026-10-06 (critique 1603, digest check notes 5–8): the remaining wording is fixed in
  question.md. "So it was selection of six particular learning runs" now reads: the "a" pattern
  persists on fresh seeds but does not generalize to the "b" continuations, so in this sample it
  depends on the learning run; selection as an isolated cause is not shown. The 1425 entries
  above stay as written; read them with this and the previous correction.

## 2026-10-08 — digest condensing (run 2026-10-07-2243): former digest text moved here

The digest was rewritten as current beliefs only (word limit). This is section "Saved-map shape shift", moved verbatim as it stood before the rewrite; no belief changed. Relative links below are relative to `research/`, not to this folder.

## Saved-map shape shift (root 10, run 2026-10-06-1425)

One run, commit `b397f72`, complete data (55 frozen maps × 8 off-family cells × 200 fresh
seeds = 88 000 searches, 48 min; gate passed, G within 0.05 log2 of 0811). Maps: G, M1–M6, and
for each of the 12 0811 pairs M+, R, R_abl (residuals zeroed) and R_fm (G's context rows with
token multipliers fitted so its pooled uniform-allele emitted token frequencies match R's; TV
≤ 7e-5). Cells: the two branch-else (BE) and six linear (LIN) cells of 0811. Pre-registered;
primary layer the six "b" continuations, which share their M starts with the "a" maps, so this
is a conditional replication over learning runs, not over starts. 95% t intervals over six
start clusters; > 1 means the first map is faster. Reviewed analysis; fairly sure of the
numbers, narrow in scope.
([14](questions/10-compositional-map-transfer/14-saved-map-shape-shift/question.md),
[run analysis](runs/2026-10-06-1425/analysis.md))

- **The branch-over-linear shift of R over M+ did not replicate; on the "b" maps it reversed.**
  "b" R / M+: BE 0.94× [0.77, 1.16], LIN 1.29× [0.88, 1.91], shift (BE ÷ LIN) 0.73× [0.57,
  0.94], below 1 in 6/6 starts. Outcome row 3: any BE gain on these maps is bounded below
  1.17×. The reversal was not pre-stated; read it as run-to-run variation, not a lead.
- **The "a" pattern is real for those six maps, so the shift is a property of individual
  learning runs.** Re-scored on the fresh seeds, "a" R / M+ gives shift 1.86× [1.41, 2.44]
  (0811: 2.03×). Two sets of runs of the same learner from the same starts disagree in sign;
  both were selected on post-addition cells only, so off-family linear speed is unconstrained
  and wanders by about 0.5 log2 within a family.
- **On the unselected "b" maps, a token-only map matched to R's pooled emitted token
  frequencies on G's context was not resolved from R; R's advantage is bounded to about 17% on
  BE and 12% on the shift.** R / R_fm: BE 1.04× [0.91, 1.17], LIN 1.02× [0.97, 1.06], shift 1.02× [0.92, 1.12]; R_fm / M+
  shows the same reversed shift as R / M+ (0.72× [0.54, 0.95]). The pooled a/b residual effect
  (shift 1.23× [1.11, 1.36]) comes from the selected "a" maps; its point estimates combine a
  linear slow-down (0.94× [0.87, 1.03]) and a BE gain (1.16× [0.97, 1.39]), neither resolved alone. This bounds, not excludes, a residual
  contribution, and matches only pooled frequencies, not positional or in-population ones.
- **Continued post-addition learning carried over to branch-else for both learners.** Against
  their M start on BE: M+ 1.40× ("a") and 1.42× ("b"), R 1.74× and 1.34×; lower bounds
  1.05–1.10. Branch-else is a related shape, not a separately trained family.

