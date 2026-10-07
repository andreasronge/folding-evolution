---
node: questions/10-compositional-map-transfer/18-compact-context-learning
title: Rank-one context steps — measured selection signal, then paired context-vs-token continuation from saved token maps
---

## Why this now

[Strategy 0803](strategy.md) puts root 10's open question first: can selection learn useful
decoder context beyond token tuning? It asks for training feasibility before any transfer test.
I follow its [plan](../../plans/learnable-context.md) with one deliberate change (below:
the arms continue from saved token-tuned maps, not from G4). The question folder is the new
child [18](../../questions/10-compositional-map-transfer/18-compact-context-learning/question.md)
(slots 11 and 12 of root 10's 12).

What the earlier attempts leave open. 0132 (3 of 552 free weights per step) and 0811 (whole
rows on top of saved token maps) found no fresh-training increment over token learning
(0811: R/M+ 1.00× [0.90, 1.11], 12 pairs). 0811's single-block calibration could neither show
nor rule out usable variation (row-step true-effect sd 0.00 [0.00, 0.11]), and its gate was
removed. Hand-set context does matter on this bank (1603's crossed preference 1.68× / 1.32×).
Nobody has measured whether a *compact* context step has a selectable effect.

**Steward probe (read-only, on 1723's `search.jsonl` / `generations.jsonl`).** These numbers
size the design:

| Quantity (65 536 cap, 24 searches per candidate, own training cells) | Measured |
|---|---|
| per-search log2 cost sd | 1.67, so a 24-search score has noise sd 0.34 |
| child − parent noise variance on the same 24 seeds | 0.14–0.25 (shared seeds barely help: ≈ 2× single-score variance) |
| token-step true-effect variance (observed − noise) | 0.075–0.086 in generations 1–5, 0.025–0.037 in generations 6–25 |
| reliability of a 24-search child − parent difference | 0.10–0.29 |
| mean token-step effect | +0.02 to +0.09 log2 (slightly harmful) |
| runtime | 0.66 s per 65k-cap search; about 1.1 s per 524k fresh search (10 500 in about 20 min on 10 workers) |
| rank-one capacity (SVD of log G4-BE − log G4 etc., after removing row and column means) | captures 55% / 64% of the BE / PA hand-set context, **93% of the BE − PA contrast** |

So a token-tuned map's 24-search scores rank candidates poorly. The first thing to measure is
whether context steps have a true effect large enough to select at all.

## What would be run (one queue entry, two stages gated in code, ≤ 4 h)

Fixed throughout: frozen 1603 bank (SHA verified), G4 (hash verified), D1331,
`v2_rmin_first`, inner search exactly as 1723 (population 256, length 32, crossover 0.7,
mutation 0.03, 64 sampled cases, exact 1 331-input verification). Only the ten 1723 training
cells (BE 4, PA 6) are searched. **No holdout cell, holdout seed or holdout score appears
anywhere.** Each map is scored on its own family's training cells. New seed blocks must not
overlap any earlier run's blocks.

**Representation (fixed before any scoring).** The table is normalize(G4 counts ·
exp(m_j) · exp(a_i b_j)). m holds the 24 token log-multipliers, bounded within ±ln 16 of G4 as
in 1723. a ∈ ℝ²⁵ (previous-token rows, including the start row) is centred and scaled to unit
RMS, drawn N(0,1) from a seeded stream per trajectory. b ∈ ℝ²⁴ is centred and starts at 0, so
the starting table is exactly the start map. Centring a means the residual adds nothing to any
column's mean across rows, so it cannot act as another global token multiplier.
- Token step: as in 1723, 3 coordinates of m, N(0, 0.5).
- Context step: 3 coordinates of b, N(0, 0.5), then re-centre b. This changes three columns
  by 0.5 × a_i in row i, the same RMS size as a token step but mean-zero over rows. Once b ≠ 0,
  half of the context steps instead move 3 coordinates of a, N(0, 0.5), re-centring and
  re-scaling a. A step that would leave the table unchanged is redrawn as a b-step.
  |a_i b_j| is clipped to ln 16, and any clipping is reported.
Nothing here uses the hand-set BE/PA grammars, canonical solutions, task identity or holdout
scores. The grammars appear only in the descriptive capacity and alignment readouts.

**Stage A — selection-signal calibration (~34 min).** Starts are the saved 1723 maps BE9, BE10,
PA9 and PA10. They are used only here and never in stage B. Per start: 48 context mutants (one
b-step from b = 0 with that start's seeded a) and 24 token mutants. Each mutant is scored on
two independent seed blocks A and B of 48 searches each. The parent is scored on 192 searches
in each block. Δ = mutant − parent mean log2 cost (unsolved = 2 × cap).
- Signal variance σ²_T per operator = covariance of Δ_A and Δ_B across mutants, centred within
  start and pooled over the four starts. The 95% interval comes from bootstrapping mutants
  within starts (2 000 reps). This estimator needs no noise model, unlike 0811's variance
  subtraction. Expected SE about 0.006–0.007 for context (K = 192).
- Per-search noise variance v (within candidate) and mean step effect μ per operator.
- Selected-change check (descriptive, as the plan asks): take the top quarter of mutants by
  Δ_A (also using the first 24 searches of A only). Report their mean Δ_B on the independent
  seeds, per operator.
- Runtime of perturbed maps, which feeds stage B admission.
- **Gate:** if the context σ²_T 95% upper bound is < 0.015 (true-effect sd < 0.12 log2), stage
  B is not run. Fresh-score nothing further, and report.
- **Effort rule** (otherwise): choose the searches per candidate n ∈ {24, 48, 96} maximizing
  Γ(n) = (1/n)·max(0, 1.27·σ²_T/√(σ²_T + 2v/n) − μ), using the context operator's stage-A
  estimates. 1.27 is the expected best of six standard normals. If Γ = 0 for all n, use 96. Both
  arms use the chosen n, so funding stays equal.

**Stage B — paired continuation (~148 min).** Starts: saved 1723 maps BE1–BE8 and PA1–PA8.
From each start run two trajectories:
- **T**: token steps only.
- **C**: each step is token or context with probability ½.
Both trajectories of a pair use the same inner seeds every generation, with separate mutation
streams. Each generation has 2 parents (rescored on that generation's seeds) and 6 children,
and the best 2 of 8 survive. Searches cycle over the family's own training cells. Budget per
trajectory is ≤ 4 000 inner searches at cap 65 536: G = ⌊3 800 / (8n)⌋ generations (19 / 9 / 4
for n = 24 / 48 / 96). The final choice rescores the two final parents on 100 new seeds each.
Pairs run interleaved BE, PA, BE, …. Before each pair is admitted, reserve 1.3× the slowest
pair plus the remaining fresh scoring against an internal deadline of 3.75 h. Analysis needs at
least 6 complete pairs per family.

**Fresh scoring (~32 min).** Per start: S (the start map), T, C, and C0 (C's table with the
residual removed, keeping C's m). Each is scored on its own family's training cells with 50 new
shared seeds per cell at cap 524 288. G4 is scored on all ten cells as an anchor. That is about
16 500 searches.

**Primary readout.** For each pair k, D_k = mean over own cells of the seed-mean
log2(T_T / T_C). Positive means context helped. Report the pooled mean over 16 pairs with a 95%
t interval (df 15) and the ratio 2^D. Per-family intervals (df 7) are descriptive. A result in
only one family is partial evidence, not a reason to change the split.

**Descriptive readouts.** T/S (is token continuation still learning?), C/C0 (the residual's own
contribution inside C), C0/T, the drift attributable to the residual, the cosine between each
learned residual and the hand-set BE − PA contrast, actual evaluations and time per arm, and
in-loop versus fresh agreement.

**Runtime.** Stage A 29 200 searches × 0.66 s / 9.5 workers ≈ 34 min. Stage B 32 × 4 000 =
128 000 searches ≈ 148 min. Fresh scoring ≈ 32 min. Total about 3.6 h (3.55 h of computing
plus overhead), with a 4.0 h timeout. Each continuation is about 4.6 min. If the gate fires, the
queue ends after about 35 min.

## Feasibility (what the design depends on)

- **Gate power.** With K = 192 context mutants, n = 48, v ≈ 2.8 and SE ≈ 0.0065: a true σ²_T = 0
  gives an upper bound near 0.013, so the gate fires about 65% of the time. A context step as
  selectable as a late token step (σ²_T ≈ 0.03) essentially never trips it. 0811's row step had
  an upper bound of 0.11² ≈ 0.012, so a firing gate is a live possibility (my estimate ~40%).
- **Primary precision.** 0811's continuation pairs had a between-pair sd of 0.29 log2 on
  training. With 16 pairs the half-width is 2.13 × 0.29 / 4 ≈ 0.155 log2 (±1.11×). Under a true
  null, the upper bound falls below 1.15× about 70% of the time. A true 1.25× increment
  (0.32 log2) is resolved (lower bound > 1) more than 95% of the time. With 6 pairs per family the
  half-width is about 0.18 log2.
- **Learning capacity.** 0811's token continuation still gained 1.45× over 35 generations, so
  saved maps are not at a ceiling. 4 000 searches is a smaller budget (0811: about 13 400 per
  trajectory). T/S shows whether either arm is still learning.
- **Deadline.** It is 08:20 now. If the queue starts around 10:30 it ends around 14:10, and
  analysis would finish by about 15:30. That leaves slot 12 (≤ 5 h) within the 22:25 deadline.

## Outcome rules (applied in order, non-overlapping)

| Row | Condition | Meaning | Next |
|---|---|---|---|
| U | invalid data (pairing, leakage, hashes, missing rows) or < 6 complete pairs in either family, not caused by the gate | infrastructure/runtime limit | report the measured limit; strategy |
| 1 | gate: context σ²_T upper bound < 0.015 | single compact context steps at token-tuned starts have no selectable fresh-search effect (sd < 0.12 log2): a selection-signal bound (explanation B), not a proof that useful context is absent (D untouched) | close 18 for this procedure; strategy; slot 12 not spent on it |
| 2 | pooled C/T lower bound > 1 | accessible fresh-training increment beyond equally funded token tuning (A). C/C0 says whether the residual itself carries it | if point ≥ 1.1×: slot 12 freezes the procedure and tests transfer on the three holdouts with token, G4, residual-off and marginal-matched controls; else strategy |
| 3 | lower ≤ 1 and upper < 1.15× | no increment ≥ 1.15× from this procedure and budget (B or C, using T/S and C/C0) | close 18 as a bounded negative; root 10's beyond-token answer: not found by three procedures; strategy |
| 4 | otherwise | **unresolved** | slot 12 adds pairs only if the observed pair sd projects a row-2 or row-3 answer within 5 h; else strategy |

My prediction: row 1 or row 3 (together ~65%), row 2 ~15%, row 4 ~20%.

## Alternatives considered

- **Both arms learn from G4 (the plan's default).** Rejected for this slot. Independent
  token-learning trajectories differ by sd 0.19–0.31 log2 (1723). Re-running the 12-minute token
  phase in both arms would leave about 8 pairs in 4 h, a half-width near 0.3 log2, and an
  unresolved result by design. Continuing from shared token-tuned starts measures exactly
  "beyond token tuning" and removes the start-to-start spread. Cost: it cannot test explanation
  D (context learnable only jointly from G4). A positive here would make that test worth having;
  a null leaves it open, and the question file says so.
- **Calibration-only slot.** Costs a full agent cycle to answer a gate. Gating in code gets the
  same answer and continues automatically.
- **Rank two or row-specific residuals.** Rank one already captures 93% of the hand-set BE − PA
  contrast. Whole-row and full-table learners are on the strategy's stop list.
- **Higher fixed scoring effort without calibration.** The probe shows the n trade-off depends
  on σ²_T and μ, which are unknown for context steps. Choosing n from three pre-stated levels by
  a stated formula is bounded and not an optimizer sweep.
- **Off-family or holdout scoring now.** Deferred to slot 12. Training feasibility comes first,
  and the holdouts stay out of procedure choice.
