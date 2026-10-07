---
node: questions/10-compositional-map-transfer/18-compact-context-learning
title: Rank-one context steps — calibrate selection signal and scoring effort, then 16 paired context-vs-token continuations from saved token maps (no stopping gate)
---

## Why this now

[Strategy 0803](../2026-10-07-0803/strategy.md) puts root 10's open question first: can selection
learn useful decoder context beyond token tuning? It asks for training feasibility before any
transfer test. The question is [18](../../questions/10-compositional-map-transfer/18-compact-context-learning/question.md),
which has root 10's slots 11 and 12. This revises [proposal 0803](../2026-10-07-0803/proposal.md).
The [critic](../2026-10-07-0803/critique.md) accepted the paired continuation but blocked its stopping
rule. The changes are:

| Critique point | Change |
|---|---|
| 2 (blocking): low step variance does not bound selected improvement, so it cannot justify stopping or diagnosing B | **Gate removed.** Stage A only measures and picks the scoring effort; stage B always runs. No outcome is decided by σ²_T. Stage A's selected-quarter rescoring is reported as a diagnostic next to the C/T result. |
| 1: solve fractions, perturbed-map runtime, first-pair reserve | Historical 65k solve fractions are below. Stage A measures solve fraction and seconds per search for each operator, and these set the reserves. The first-pair reserve is defined explicitly. |
| 3: calibration scope, seed dependence, direction of "selected" | 4 starts × **2 random row directions** = 8 context units. Every mutant gets **its own seeds**, independent across mutants. Results are reported per unit and per family. The selected quarter is the **lowest** Δ_A (cheapest). b-steps at b = 0 only; a-steps are uncalibrated, and this is stated. |
| 4: shallow at n = 96; actual budgets | n = 96 is dropped. n ∈ {24, 48}, and both settings spend **exactly 3 840 in-loop + 200 final = 4 040 searches per trajectory**: 20 or 10 generations, 120 or 60 children, about 60 or 30 context proposals in C. A null concerns this short continuation. The interval uses the achieved pairs with equal family weights. |
| 5: name the outcome that leaves mechanism unresolved | Separate rows for "C/T null while T still learned" and "C/T null, neither arm learned (depth-limited)". A C/T win without a resolved C/C0 is a benefit of the mixed procedure, not attribution to the residual. C0 does not preserve emitted marginals. |
| 6–7: digest overclaims | Fixed in this cycle in [digest](../../digest.md) and [17](../../questions/10-compositional-map-transfer/17-decoder-initialization-variation/question.md) with the critic's wording. |

Earlier attempts and the case for this one: 0132 (3 of 552 free weights per step) and 0811 (whole
rows on top of saved token maps) found no fresh-training gain over token learning (0811: R/M+
1.00× [0.90, 1.11], 12 pairs). Hand-set context does matter on this bank (1603's crossed
preference was 1.68× / 1.32×). No one has yet measured whether a *compact* context step has an
effect that selection can pick up. Rank one captures 93% of the hand-set BE − PA contrast (steward
probe 0803).

## What would be run (one queue entry, ≤ 4 h)

**Fixed throughout:** the frozen 1603 bank (SHA verified), G4 (hash verified), D1331, `v2_rmin_first`.
The inner search is exactly as in 1723: population 256, length 32, crossover 0.7, mutation 0.03,
64 sampled cases, exact 1 331-input verification. Cost is log2 evaluations, with unsolved = 2 × cap.
Only the ten 1723 training cells are searched: BE 4, PA 6. **No holdout cell, holdout seed or
holdout score appears anywhere.** Each map is scored only on its own family's training cells. All
seed blocks are new and disjoint from every earlier run.

**Representation (fixed before any scoring).** The table is normalize(G4 counts · exp(m_j) ·
exp(a_i b_j)).
- m: 24 token log-multipliers, bounded within ±ln 16 of G4, as in 1723.
- a ∈ ℝ²⁵ (previous-token rows, including the start row): centred and scaled to unit RMS, drawn
  N(0, 1) from a seeded stream.
- b ∈ ℝ²⁴: centred, starts at 0. The starting table is therefore exactly the start map.
- Token step: 3 coordinates of m, N(0, 0.5), as in 1723.
- Context step: 3 coordinates of b, N(0, 0.5), then re-centre b. Once b ≠ 0, half of the context
  steps instead move 3 coordinates of a, N(0, 0.5), then re-centre and re-scale a. A step that
  leaves the table unchanged is redrawn as a b-step.
- |a_i b_j| is clipped at ln 16, and every clip is counted.

Centring a keeps the residual from shifting any column's mean log weight, so it cannot simply act as
another token multiplier. It does **not** keep emitted token frequencies fixed. Nothing uses the
hand-set grammars, canonical solutions, task identity or holdout scores. The grammars appear only
in a descriptive alignment readout.

### Stage A — calibration and effort choice (~34 min, never stops the run)

**Starts:** saved 1723 maps BE9, BE10, PA9 and PA10. They are used only in stage A.

**Mutants per start:**
- Context: two independent row directions a, with 24 b-step mutants each (b = 0 → one step).
  That gives **8 context units** of 24 mutants.
- Token: 24 token mutants per start, so 4 token units.

**Scoring:** each mutant is scored on two blocks, A and B, of 48 searches at cap 65 536. Each block
cycles over the family's training cells. Each mutant's seeds are its own, so mutants are
independent given their start. The parent gets 192 searches in each block, on its own seeds.

Δ = mutant mean − parent mean on the same block. Negative Δ means the mutant is cheaper, i.e. better.

**Readouts:**
- σ²_T per operator: the covariance of Δ_A and Δ_B across mutants, centred within unit, pooled.
  The 95% interval comes from bootstrapping mutants within units, 2 000 replicates. Also reported
  per unit and per family.
- μ (mean Δ) and v (within-mutant per-search variance) per operator.
- **Selected-quarter check:** in each unit, take the 6 mutants with the **lowest** Δ_A, using all 48
  searches and also only the first 24. Report their mean Δ_B on independent seeds, and the realized
  selection gain: mean Δ_B of the selected minus mean Δ_B of all. Give a bootstrap 95% CI per
  operator.
- Solve fraction at 65k and seconds per search per operator and family. These feed stage B's
  reserves.

**Effort rule:** choose n ∈ {24, 48} maximizing Γ(n) = (1/n)·max(0, 1.27·σ²_T/√(σ²_T + 2v/n) − μ),
using the context operator's point estimates. 1.27 is the expected best of six standard normals.
Ties, or Γ = 0 at both, go to n = 24 (deeper). Both arms use the chosen n.

**Scope:** stage A calibrates single b-steps from b = 0 at four token-tuned starts with eight random
row directions. It does not calibrate later a-steps or steps from a nonzero residual.

### Stage B — paired continuation (~150 min)

**Starts:** saved 1723 maps BE1–BE8 and PA1–PA8. From each start, two trajectories:
- **T:** token steps only.
- **C:** each step is a token step or a context step with probability ½. C gets its own seeded a.

Both trajectories of a pair use the same inner seeds every generation, with separate mutation
streams.

Each generation has 2 parents, rescored on that generation's seeds, plus 6 children; the best 2
of the 8 survive. Searches cycle over the family's own training cells.

**Budget, equal per trajectory:** 3 840 in-loop searches. That is 20 generations at n = 24 or 10
at n = 48. The final choice rescores the 2 final parents on 100 new seeds each, for 4 040 searches
in total.

**Admission:** pairs are admitted alternately BE, PA, BE, …. Admission stops at the first refusal,
so the family counts differ by at most one. Before each pair, the run reserves time against an
internal deadline of 3.8 h:
1. Pair cost: for the first pair, 1.3 × 2 × 4 040 × (stage A's slowest per-search seconds) / 9.5
   workers, about 12 min. For later pairs, 1.3 × the slowest completed pair.
2. Fresh scoring for the pairs admitted so far: 1.3 × its projected cost. This uses 1723's 1.02 s
   per fresh search, scaled by the ratio of stage A's perturbed-map 65k seconds to 1723's.

### Fresh scoring (~30 min)

Per start, four maps:
- **S**: the start map.
- **T**: the token arm's final map.
- **C**: the context arm's final map.
- **C0**: C's table with the residual removed, keeping C's m.

Each is scored on its own family's training cells at cap 524 288, with 50 new seeds per cell
shared across the four maps. G4 is scored on all ten cells as an anchor. That is about 16 500
searches.

### Primary readout

For each pair k, D_k = mean over own cells of the seed-mean log2(T_T / T_C). Positive means
context helped. The estimate is the family-balanced mean D̄ = (D̄_BE + D̄_PA)/2, with
SE = ½√(s²_BE/n_BE + s²_PA/n_PA) and a t interval on n_BE + n_PA − 2 df. With 8 + 8 pairs this is
the plain pooled mean. Report 2^D̄. Per-family intervals are descriptive. A result in only one
family is partial evidence.

### Descriptive readouts

- T/S and C/S with t intervals over starts: is either arm still learning?
- C/C0: the residual's share inside C. This is not pure context attribution, because removing the
  residual also shifts emitted marginals.
- C0/T, the residual's drift, and the cosine of each learned residual with the hand-set BE − PA
  contrast.
- C's step mix: token / b / a steps, acceptance by operator, clips.
- Solve fractions, actual evaluations and time per arm, and agreement between in-loop and fresh scores.

### Runtime

| Part | Searches | Time |
|---|---|---|
| Stage A | 4 × (72 mutants × 96 + 384) = 29 184 | × 0.66 s / 9.5 ≈ 34 min |
| Stage B | 32 × 4 040 = 129 280 | ≈ 150 min |
| Fresh scoring | 16 500 | × 1.02 s / 9.5 ≈ 30 min |
| **Total** | | **≈ 3.6 h**, timeout 4.0 h |

The reserves trade pairs for time if perturbed maps are slower. The analysis needs ≥ 6 complete
pairs per family.

## Feasibility (measured)

| Quantity | Value | Source |
|---|---|---|
| per-search log2 cost sd, 65k cap | 1.67 | steward probe 0803, 1723 `search.jsonl` |
| 65k solve fraction during token learning | BE 0.88, PA 0.93; by cell 0.84–0.995 | probe 0821, same file (193 920 learning searches) |
| seconds per search | 0.66 (65k), 1.02 (524k fresh), 9.5 effective workers | 1723 analysis |
| token-step true-effect variance | 0.075–0.086 (gen 1–5), 0.025–0.037 (gen 6–25) | probe 0803 |
| between-pair sd of paired continuation contrast (training) | 0.29 log2 | 0811 R vs M+ (35 gen, so likely conservative for 10–20 gen) |
| token learning still moving at 1723's end? | best-of-16 in-loop 12.45 → 12.24 over gen 15–25 (≈ 3 840 searches; selection-biased) | probe 0821 |
| continued token learning from saved maps | M+/M 1.45× [1.26, 1.69] over 13 440 searches | 0811 |

What these imply:
- **Primary precision.** With 16 pairs and sd 0.29, the half-width is 2.13 × 0.29 / 4 ≈ 0.155 log2
  (±1.11×). Under a true null, the upper bound falls below 1.15× about 74% of the time. A true
  1.25× increment is resolved above 1 more than 95% of the time. With 6 + 6 pairs, the half-width is
  ≈ 0.18 log2.
- **Depth is the main risk.** 4 040 searches is about 30% of 0811's continuation. The in-loop slope
  suggests T/S may be only about 1.05–1.2×, and over 16 starts the T/S half-width is ≈ 0.13 log2.
  Stage B may therefore show little learning in either arm. Outcome rows 2 and 3 keep that case
  from being read as evidence against context.
- **Capping** is mild at 65k: 0.5–16% unsolved per cell. Stage A reports it for perturbed maps.
- **Deadline.** It is 08:35. A queue starting around 11:00 ends around 14:40, and analysis would be
  done by about 16:00. That leaves slot 12 (≤ 5 h of queue) inside the 22:25 deadline, though tightly.

## Outcome rules (applied in order; the first that matches)

| Row | Condition | Meaning | Next |
|---|---|---|---|
| U | invalid data (pairing, leakage, hashes, missing rows), or < 6 complete pairs in either family | infrastructure or runtime limit | report the measured limit; strategy |
| 1 | C/T lower bound > 1 | The mixed token+context procedure gives a fresh-training increment over equally funded token continuation (A for the procedure). C/C0 resolved > 1 would attribute part of it to the residual. Otherwise it is a procedure benefit only. | point ≥ 1.1×: slot 12 freezes the procedure and tests transfer on the three holdouts, with token, G4, residual-off and marginal-matched controls. Else strategy. |
| 2 | C/T upper < 1.15× and T/S lower > 1 | Token continuation still improved fresh search, but adding context steps gained < 1.15× (or cost something, if upper < 1). Bounded negative for this procedure and budget. Stage A tells B from C, descriptively: no realized selection gain for context mutants on independent seeds → B; a realized gain that did not accumulate → C. D untouched. | close 18; root 10's beyond-token answer: not found by three procedures; strategy |
| 3 | C/T upper < 1.15× and T/S lower ≤ 1 | No increment, but token learning did not resolve either. Too little depth cannot be told apart from ineffective context. | park 18; reopen if a continuation at least 3× longer (or a cheaper inner search) is affordable; strategy |
| 4 | otherwise (C/T interval includes 1 and reaches ≥ 1.15×) | **unresolved** | slot 12 adds pairs only if the observed pair sd projects a row 1 or 2 answer within 5 h; else strategy |

Stage A never changes a row. It is reported beside the result and decides only n.

My prediction: U 5%, row 1 15%, row 2 30%, row 3 25%, row 4 25%.

## Alternatives considered

- **Keep a gate, but on the selected-quarter gain.** A bound on realized selected gain per step is
  closer to what matters, but turning it into "cannot accumulate in G generations" needs a
  learning model we do not have. Running stage B costs about 2.5 h and gives the direct answer.
- **Fewer, deeper pairs** (12 pairs × about 5 400 searches). The half-width would grow to ≈ 0.18
  log2, and under a null row 2 would become much less likely. I chose precision on the primary
  contrast. Row 3 is how a lack of depth gets reported.
- **Both arms learn from G4 (the plan's default).** Start-to-start spread (sd 0.19–0.31 log2 in
  1723) would leave about 8 pairs in 4 h and an unresolved result by design. Continuing from shared
  token-tuned starts measures exactly "beyond token tuning". It cannot test D, as question 18 says.
- **Calibrate a-steps too** (a displaced parent with b ≠ 0 per start). That would add about 10 min
  and an arbitrary choice of b. The C arm's in-loop acceptance by step type is reported instead.
- **Off-family or holdout scoring now.** Deferred to slot 12. Training feasibility comes first, and
  the holdouts stay out of the choice of procedure.
