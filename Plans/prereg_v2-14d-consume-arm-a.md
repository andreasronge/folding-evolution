# Pre-registration: §v2.14d

**Status:** QUEUED · target commit `TBD` · 2026-04-16

## Question (one sentence)

Does the safe-pop consume rule also lift 6-token body assembly under Arm A direct GP (no extraction layer), or is the effect specific to BP_TOPK's run-based decode?

## Hypothesis

§v2.14 showed consume lifts BOTH from 4→8/20 under BP_TOPK. §v2.6-pair1 follow-ups showed Arm A preserve at 1× = 7/20 BOTH (vs BP_TOPK preserve 4/20). Under Arm A the full tape executes (no run extraction), so the type-barrier dynamics are different: all 32 tokens run, not just the extracted bonded run. The stack-jam effect may be more or less pronounced under Arm A — prediction is genuinely uncertain.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_14d_consume_arm_a.yaml`
- **Arms / conditions:** consume rule, Arm A direct GP, 1× compute
- **Tasks:** `{any_char_count_gt_1_slot, any_char_count_gt_3_slot}` alternation, period 300
- **Seeds:** 0-19
- **Fixed params:** pop=1024, gens=1500, v2_probe alphabet, tape_length=32
- **Est. compute:** ~15 min at 4-worker M1
- **Related experiments:** §v2.14 (consume BP_TOPK = 8/20), §v2.6-pair1-scale-A (preserve Arm A = 7/20)

No sampler changes. Principle 20 not triggered.

## Baseline measurement (required)

- **Baseline quantity:** BOTH-solve rate under Arm A preserve (§v2.6-pair1-scale-A)
- **Value:** 7/20 (commit `c8af29d`)
- **Note:** Arm A at 1× was not run in the §v2.14 sweep (which used BP_TOPK only). The baseline comes from the §v2.6-pair1 follow-up sweep.

## Internal-control check (required)

- **Tightest internal contrast:** consume-Arm-A vs preserve-Arm-A on the same task/seeds.
- **Are you running it here?** The consume-Arm-A arm is the new run. Preserve-Arm-A baseline from §v2.6-pair1-scale-A.

## Pre-registered outcomes (required — at least three)

Let `P_A` = 7/20 (preserve Arm A), `C_A` = consume Arm A BOTH.

| outcome | quantitative criterion | interpretation |
|---------|------------------------|----------------|
| **PASS — consume helps Arm A** | `C_A ≥ P_A + 4` (i.e., ≥11/20) | Consume effect generalizes beyond BP_TOPK. The executor-rule lever works regardless of whether run extraction is present. Broadens the findings.md scope. |
| **PARTIAL — small lift** | `P_A + 1 ≤ C_A ≤ P_A + 3` (i.e., 8-10/20) | Consume helps Arm A but less than it helped BP_TOPK (+4). The run-extraction layer amplifies the type-barrier effect. |
| **INCONCLUSIVE** | `|C_A − P_A| ≤ 1` (i.e., 6-8/20) | Consume is irrelevant under Arm A. The effect is BP_TOPK-specific — possibly because run extraction concentrates programs into the type-critical region. |
| **FAIL — consume hurts Arm A** | `C_A < P_A − 2` (i.e., ≤4/20) | Consume damages Arm A. Under full-tape execution, aggressive stack clearing disrupts useful type-barrier effects. |

**Threshold justification:** +4 for PASS matches the §v2.14 delta (4→8 = +4). The ±1 INCONCLUSIVE band is tight because Arm A's 7/20 baseline is already higher than BP_TOPK's 4/20, so the noise band is narrower relative to the effect size.

## Degenerate-success guard (required)

- **Too-clean result:** C_A = 20/20. Full-tape execution + consume might trivialize the task by making all programs produce some output. Check winner genotypes for canonical 6-token bodies vs noise programs that happen to score well.
- **Preserve-baseline drift:** if a fresh preserve-Arm-A run deviates from 7/20 by more than ±3, flag code drift.

## Statistical test (if comparing conditions)

- **Test:** descriptive (solve counts + seed overlap with §v2.6-pair1-scale-A solvers). Cross-commit comparison, not paired.

## Diagnostics to log (beyond fitness)

- Per-seed BOTH-solve + best-fitness
- Seed overlap with §v2.6-pair1-scale-A preserve-Arm-A solvers
- Winner-genotype attractor-category classification
- Program length distribution (Arm A programs are typically 32 tokens with NOPs; consume may change effective program structure)

## Scope tag (required for any summary-level claim)

`within-family / n=20 / at Arm-A v2_probe / on 6-token string-count body / executor-rule × decoder-arm interaction`

## Decision rule

- **PASS →** Broaden findings.md `safe-pop-consume-effect` scope from BP_TOPK-only to across-decoder-arms. Strong evidence for making consume the project default.
- **PARTIAL →** Note the smaller effect under Arm A. The finding stays BP_TOPK-scoped for the solve-rate claim but with an Arm A observation.
- **INCONCLUSIVE →** The effect is BP_TOPK-specific. Document in findings.md scope boundaries.
- **FAIL →** Document. The consume rule is decoder-arm-dependent — helps BP_TOPK, hurts Arm A. Do NOT change project default.
