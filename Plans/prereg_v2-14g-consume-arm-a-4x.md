# Pre-registration: §v2.14g — Consume × Arm A × 4× compute on 6-token string-count body

**Status:** QUEUED · target commit `TBD` · 2026-04-16

## Question (one sentence)

Is the §v2.14d Arm A consume null result (5/20 vs preserve 7/20 at 1× compute) rescued by 4× compute, mirroring the §v2.14c BP_TOPK consume × compute stacking (consume-4× = 14/20 > preserve-4× = 8/20)?

## Hypothesis

Three non-overlapping readings of the current evidence are consistent with the data:

1. **Decoder-arm-dependent effect at any compute.** Consume does not help Arm A, period. §v2.14d's 5/20 is the honest result; 4× compute will not change it.
2. **Compute-threshold effect.** Consume × Arm A needs 4× compute to cross the effect threshold, matching the BP_TOPK × compute pattern in §v2.14c. Prediction: C_A_4x ∈ [10, 14]/20, exceeding preserve-Arm-A at both 1× and 4× compute.
3. **Consume uniformly hurts Arm A.** The null is actually a mild negative, and 4× compute will amplify it rather than rescue it. Prediction: C_A_4x ≤ P_A_4x.

The §v2.14 findings.md entry states the consume lift is BP_TOPK-specific at 1×; this experiment closes the off-grid §v2.14d gap at the next compute tier.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_14g_consume_arm_a_4x.yaml`
- **Arms / conditions:** Arm A direct GP, consume rule, 4× compute (pop=2048, gens=3000)
- **Tasks:** `{any_char_count_gt_1_slot, any_char_count_gt_3_slot}` alternation, period 600 (doubled to match gens scaling, consistent with §v2.14c convention)
- **Seeds:** 0-19
- **Fixed params:** v2_probe alphabet, tape_length=32
- **Est. compute:** ~40-60 min at 10 workers (Arm A has slightly different per-run cost than BP_TOPK)
- **Related experiments:**
  - §v2.14c: BP_TOPK consume-4× = 14/20, preserve-4× = 8/20, preserve-1× = 4/20, consume-1× = 8/20. Compute + consume levers stack on BP_TOPK.
  - §v2.14d: Arm A consume-1× = 5/20 vs preserve-1× = 7/20. Null / mildly negative.
  - §v2.6-pair1-scale-A: Arm A preserve-1× = 7/20 (commit `c8af29d`). Anchors the Arm A 1× baseline.

**Principle 20 audit:** label function, input distribution, and sampler unchanged from §v2.14d. Principle 20 **not triggered**.

## Baseline measurement (required)

**Design decision (resolved 2026-04-16):** Option A adopted. Preserve-Arm-A-4× runs as a companion sweep on the same commit so the preserve/consume contrast is matched-commit + matched-compute. The alternative (cross-commit baseline against §v2.6-pair1-scale-A) was rejected because it would mix hardware/code-drift noise into a borderline comparison.

- **Baseline quantity:** preserve-Arm-A BOTH at 4× compute. Companion sweep in same commit.
- **Anchors:** §v2.6-pair1-scale-A (Arm A preserve-1× = 7/20, commit `c8af29d`) and §v2.14c (BP_TOPK consume-4× = 14/20, commit `76bb58f`) for cross-arm / cross-compute comparison only.

## Internal-control check (required)

- **Tightest internal contrast:** preserve-Arm-A-4× vs consume-Arm-A-4× on the same task/seeds (Option A). This is the three-way interaction minus the 1× level — directly tests whether compute-scaling rescues consume under Arm A.
- **Are you running it here?** Yes, contingent on Option A above.

## Pre-registered outcomes (required — at least three)

Let `P_A_4x` = preserve-Arm-A-4× BOTH, `C_A_4x` = consume-Arm-A-4× BOTH.

| outcome | quantitative criterion | interpretation |
|---------|------------------------|----------------|
| **PASS — consume rescued by 4× compute** | `C_A_4x ≥ P_A_4x + 4` AND `C_A_4x ≥ 11/20` | Compute-threshold effect. Consume × Arm A works at 4× but not 1×. The BP_TOPK-specific scope boundary in findings.md relaxes to "decoder-arm-dependent at 1× compute; decoder-general at 4×." |
| **PASS — compute helps both** | `C_A_4x ≥ P_A_4x + 2` AND `P_A_4x > 7/20` (4× helps preserve too) | Both levers additive under Arm A but smaller consume-effect than under BP_TOPK. |
| **INCONCLUSIVE** | `|C_A_4x − P_A_4x| ≤ 1` | Consume still doesn't help Arm A. Compute helps the body (P_A_4x > 7) but adds no consume-specific lift. Finding: decoder-arm dependence is structural, not compute-threshold. |
| **FAIL — consume damages Arm A at 4×** | `C_A_4x < P_A_4x − 2` | Consume hurts Arm A, and compute amplifies the harm. Finding: the consume rule should NOT be the Arm A default; strong evidence for keeping consume gated to BP_TOPK. |
| **SWAMPED** | `P_A_4x ≥ 18/20` OR `C_A_4x ≥ 18/20` with both high | 4× on Arm A saturates this body; no executor-rule signal measurable. Report the saturation as its own result (compute alone clears Pair 1 under Arm A). |

**Threshold justification:** +4 for PASS-rescued matches the §v2.14c consume × compute effect size on BP_TOPK (14 − 8 = +6 with compute, 8 − 4 = +4 from consume alone). The 11/20 absolute floor for PASS ensures the lift is visible against noise. ±1 INCONCLUSIVE band matches §v2.14d convention.

## Degenerate-success guard (required)

- **Too-clean (C_A_4x ≥ 18/20):** 4× compute under Arm A may trivialize the Pair 1 body if the extra gens allow random search to find canonical-6-token assemblies without the type-barrier dynamics mattering. Attractor-inspect.
- **Saturation symmetry:** if P_A_4x and C_A_4x both ≈ 18-20/20, the body is too easy at 4× — report as SWAMPED, do not interpret the preserve/consume delta.
- **Preserve-Arm-A-1× drift check:** cross-commit baseline (7/20, `c8af29d`) — if P_A_4x < 7/20, code drift is plausible and must be investigated before interpreting.
- **Program-structure inspection:** §v2.14d noted Arm A programs are typically 32 tokens with NOPs. Check whether consume changes effective program length / structure under 4× compute (consume may prune more aggressively at higher gens).
- **Detection:** `decode_winner.py` on all 40 winners + per-arm canonical-6-token attractor rate.

## Statistical test (if comparing conditions)

- **Test:** paired McNemar on seeds 0-19 (preserve-4× vs consume-4× Arm A).
- **Significance threshold:** α = 0.05, two-sided.
- **Secondary:** descriptive comparison against (i) §v2.14d Arm-A-1× pair (cross-compute, same arm), (ii) §v2.14c BP_TOPK-4× pair (cross-decoder, same compute).

## Diagnostics to log (beyond fitness)

- Per-seed BOTH-solve + best-fitness under both rules
- Winner-genotype attractor-category classification (both arms)
- Program effective-length distribution (NOP count under Arm A)
- Seed overlap with §v2.14d (Arm-A-1× consume solvers) and §v2.14c (BP_TOPK-4× consume solvers)
- Holdout gap

## Scope tag (required for any summary-level claim)

**If PASS-rescued:** `within-family · n=20 · at Arm A 4× compute v2_probe · on 6-token string-count body · executor-rule × decoder-arm × compute three-way — decoder-arm dependence relaxes at 4×`

**If INCONCLUSIVE/FAIL:** existing findings.md scope stays. The null adds concrete evidence: decoder-arm dependence is structural, not compute-threshold.

## Decision rule

- **PASS — consume rescued →** broaden findings.md `safe-pop-consume-effect` decoder-arm scope to "decoder-arm-dependent at 1×; decoder-general at 4×." Queue E-count × 4× as the replication candidate.
- **PASS — compute helps both →** note the smaller Arm A effect; keep BP_TOPK-specific solve-rate claim; add Arm A 4× as supporting-but-weaker evidence.
- **INCONCLUSIVE →** strengthen findings.md scope boundary: decoder-arm dependence is structural (1× and 4× both fail for Arm A). BP_TOPK-specific becomes a firmer claim.
- **FAIL — consume damages →** firm up findings.md: consume rule should remain BP_TOPK-gated. Do NOT change project default to consume regardless of decoder.
- **SWAMPED →** compute alone clears the body; consume is irrelevant at this compute tier. Report as a separate "compute clears Pair 1" finding; do not confuse with the consume question.

---

*Audit trail.* Four outcome rows plus SWAMPED (principle 2). Baseline is matched-commit preserve-Arm-A-4× (principle 6; Option A). Internal control is the preserve/consume ablation on shared seeds at 4× (principle 1). Degenerate-success candidates enumerated including saturation and cross-commit drift (principle 4). Principle 20 not triggered. Decision rule commits to exact findings.md edits per outcome (principle 19).

*Resolved design decisions: Option A (companion preserve baseline), pop=2048 gens=3000 matching §v2.14c, ≥11/20 absolute PASS floor, commit-hash gated.*
