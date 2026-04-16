# Pre-registration: §v2.14c

**Status:** QUEUED · target commit `TBD` · 2026-04-16

## Question (one sentence)

Do the consume rule and 4× compute stack on the 6-token string-count body, or do they relieve the same bottleneck?

## Hypothesis

§v2.14 showed consume at 1× = 8/20 BOTH. §v2.6-pair1-scale showed preserve at 4× = 8/20 BOTH. Both interventions independently reach the same level from the 4/20 preserve-1× baseline. If they relieve the same bottleneck (partial-assembly→canonical completion), they should substitute: consume-4× ≈ 8/20. If they relieve different bottlenecks (consume clears type barriers, compute extends search depth), they should stack: consume-4× > 8/20.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_14c_consume_4x.yaml`
- **Arms / conditions:** consume rule, 4× compute (pop=2048, gens=3000)
- **Tasks:** `{any_char_count_gt_1_slot, any_char_count_gt_3_slot}` alternation, period 300
- **Seeds:** 0-19
- **Fixed params:** BP_TOPK(k=3, bp=0.5), v2_probe alphabet, tape_length=32
- **Est. compute:** ~60 min at 4-worker M1
- **Related experiments:** §v2.14 (consume-1× = 8/20), §v2.6-pair1-scale (preserve-4× = 8/20), §v2.6 Pair 1 (preserve-1× = 4/20)

No sampler changes. Principle 20 not triggered.

## Baseline measurement (required)

- **Baseline quantity:** BOTH-solve rate under consume at 1× (§v2.14) and preserve at 4× (§v2.6-pair1-scale)
- **Values:**
  - Consume-1×: 8/20 (§v2.14, commit `cdf9c39`)
  - Preserve-4×: 8/20 (§v2.6-pair1-scale, commit `600ef20`)
  - Preserve-1×: 4/20 (§v2.6 Pair 1, commit `0230662`)

## Internal-control check (required)

- **Tightest internal contrast:** consume-4× vs consume-1× (§v2.14) on the same task/seeds. Also compared to preserve-4× (§v2.6-pair1-scale).
- **Are you running it here?** The consume-4× arm is the new run. Comparison is to existing data.

## Pre-registered outcomes (required — at least three)

Let `C4` = consume-4× BOTH.

| outcome | quantitative criterion | interpretation |
|---------|------------------------|----------------|
| **PASS — levers stack** | `C4 ≥ 13/20` | Consume and compute relieve different bottlenecks. Combined effect exceeds either alone. Strong result — suggests making consume the default and running harder tasks at 4× would push into new territory. |
| **PARTIAL — mild stacking** | `9 ≤ C4 ≤ 12` | Some stacking but diminishing returns. The bottlenecks partially overlap. |
| **INCONCLUSIVE — substitution** | `C4` within ±2 of 8/20 (i.e., 6-10/20) | Consume and compute relieve the same bottleneck (partial-assembly completion). No benefit to combining them at this budget. |
| **FAIL — negative interaction** | `C4 < 6/20` | Consume at higher compute is worse than either alone. Unexpected — would require inspection. |

**Threshold justification:** The ±2 band around 8/20 for INCONCLUSIVE matches the noise observed in §v2.14 seed-overlap analysis. ≥13/20 as PASS is set to exceed preserve-16× (13/20 from §v2.6-pair1-scale-8x) — if consume-4× matches preserve-16×, that's a 4× effective compute multiplier.

## Degenerate-success guard (required)

- **Too-clean result:** C4 = 20/20. Would require winner-genotype inspection — are these genuine canonical assemblies or overfitting artifacts?
- **Seed overlap with consume-1×:** If C4's solver set is a superset of consume-1×'s {3,4,5,7,12,15,17,19}, stacking is genuine. If disjoint, it's seed substitution.

## Statistical test (if comparing conditions)

- **Test:** descriptive (solve counts + seed overlap). Comparing against historical baselines from different commits. Seed-level overlap analysis is the primary signal.

## Diagnostics to log (beyond fitness)

- Per-seed BOTH-solve + best-fitness
- Seed overlap with §v2.14 consume-1× solvers and §v2.6-pair1-scale preserve-4× solvers
- Winner-genotype attractor-category classification

## Scope tag (required for any summary-level claim)

`within-family / n=20 / at BP_TOPK(k=3,bp=0.5) v2_probe / on 6-token string-count body / consume × compute interaction`

## Decision rule

- **PASS →** Make consume the default for future experiments. Design §v2.14e: consume-4× on a second mixed-type body for external validity.
- **PARTIAL →** Document diminishing returns. Consume is still worth defaulting to (it's free at 1×).
- **INCONCLUSIVE →** Document substitution. Consume is a compute-equivalent lever, not an independent one. Still worth defaulting to (cheaper than 4× compute).
- **FAIL →** Investigate the negative interaction. Do NOT make consume the default.
