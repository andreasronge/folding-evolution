# Pre-registration: §v2.4-proxy-4c — Cross-decoder / cross-executor replication of §v2.4-proxy-4b F/R dissociation

**Status:** QUEUED · target commit `TBD` · 2026-04-17

## Question (one sentence)

Does the §v2.4-proxy-4b F/R dissociation (20/20 best-of-run solve with exact-match full-population retention R ≤ 0.04) replicate under Arm A direct GP and under the `consume` executor rule, or is it specific to BP_TOPK(k=3, bp=0.5) preserve?

## Hypothesis

§v2.4-proxy-4b (experiment commit `f10b066`, chronicle `cac7537`) established that on `sum_gt_10_AND_max_gt_5` natural sampler under BP_TOPK(k=3, bp=0.5) preserve:
- Seeded canonical body reaches 20/20 BOTH at full horizon (best-of-run layer PASS on F_1 / F_2 criteria)
- Full-population exact-match retention R_2 ≤ 0.036 (bimodal population, mean fitness 0.845)
- Observed (F=20, R≤0.04) did not match any pre-registered outcome → mechanism narrowing of `proxy-basin-attractor`

This prereg tests whether the F/R dissociation is a property of BP_TOPK preserve specifically, or a general feature of the `proxy-basin-attractor` on this task under any decoder/executor combination.

**Three non-overlapping readings:**
1. **Replicates under both interventions.** F/R dissociation is a property of the canonical body × task pressure combination; decoder arm and executor rule are irrelevant. Mechanism narrowing in findings.md is strengthened.
2. **Arm A / consume break the pattern.** F and R co-move under Arm A or consume — either both high (full PASS) or both low (FAIL maintainability). The F/R dissociation is BP_TOPK-preserve-specific.
3. **Partial replication.** One intervention replicates, the other doesn't — the dissociation has specific decoder- or executor-level conditions.

## Setup

- **Sweep files:** `v2_4_proxy4c_arm_a.yaml`, `v2_4_proxy4c_consume.yaml`
- **Arms / conditions:** each sweep runs 3 seed_fraction arms {0.0, 0.001, 0.01} × 20 seeds = 60 configs per sweep
- **Sweep 1 (Arm A):** same as §v2.4-proxy-4b except `arm: A` (no BP_TOPK extraction)
- **Sweep 2 (consume):** same as §v2.4-proxy-4b except `safe_pop_mode: consume`
- **Task:** `sum_gt_10_AND_max_gt_5` (fixed, natural sampler — matches §v2.4-proxy-4b for comparability)
- **Seeds:** 0-19 (same as §v2.4-proxy-4b)
- **Fixed params:** pop=1024, gens=1500, v2_probe alphabet, tape_length=32, `disable_early_termination: true`, seed_tapes = canonical 12-token body hex
- **Est. compute:** ~15-20 min wall per sweep at 10 workers (Arm A has slightly lower per-run cost; consume similar to preserve). Total ~30-40 min.
- **Related experiments:** §v2.4-proxy-4b (baseline), §v2.12 (Arm A on §v2.4 under random-init → basin-trapped), §v2.14b (consume on §v2.4 under random-init → 0/20)

**Principle 20 audit:** label function, sampler, input distribution all identical to §v2.4-proxy-4b. No sampler change.

**Principle 23 declaration:** this prereg runs two sweeps (Arm A, consume) as one batch. Each sweep is a single-knob change from §v2.4-proxy-4b. The prereg is authored before either sweep runs.

## Baseline measurement (required)

- **Baseline quantity:** F_AND and final_mean_fitness under `seed_fraction=0.0` for each sweep — the drift check vs §v2.4 baseline under the respective decoder/executor.
- **Anchors:**
  - BP_TOPK preserve seeded 20/20 with final_mean=0.845 (§v2.4-proxy-4b, `f10b066`)
  - Arm A under random-init (no seeds): 0/20 (§v2.12 natural, `1cfe7d5`)
  - Consume under random-init (no seeds): 0/20 (§v2.14b natural, `1fc51c5`)
- **Expected behaviour of seed_fraction=0.0 arms:** both new sweeps should reproduce 0/20 solve at F_AND (matching §v2.12 / §v2.14b baselines on this task).

## Internal-control check (required)

- **Tightest internal contrast (per sweep):** seed_fraction ∈ {0.0, 0.001, 0.01} within the sweep. Same 3-arm design as §v2.4-proxy-4b.
- **Cross-sweep contrast:** Arm A sweep vs consume sweep vs §v2.4-proxy-4b (BP_TOPK preserve baseline). Three decoder/executor cells on the same task with matched seeds.

## Pre-registered outcomes (required — at least three, per sweep)

Let `F_i` = BOTH-solve count at `seed_fraction = i` (seeded arms: i ∈ {0.001, 0.01}). Let `R_exact` = exact-match upper bound on full-population retention inferred from `unique_genotypes / pop_size` at final gen.

| per-sweep outcome | criterion | interpretation |
|---|---|---|
| **PASS — full replication of §v2.4-proxy-4b F/R pattern** | `F_seeded ≥ 15/20` AND `R_exact ≤ 0.10` | The F/R dissociation replicates under this intervention. Mechanism narrowing of `proxy-basin-attractor` strengthens. |
| **PARTIAL — full saturation (F high, R also high)** | `F_seeded ≥ 15/20` AND `R_exact ≥ 0.25` | Canonical body saturates both best-of-run and population under this intervention. This would reverse the F/R dissociation: under the tested decoder/executor, selection DOES propagate canonical through the population. A stronger pro-canonical dynamic than BP_TOPK preserve. |
| **PARTIAL — canonical displaced (F low)** | `F_seeded < 10/20` | Seeded canonical body cannot maintain best-of-run under this intervention. Suggests decoder-arm or executor-rule actively erodes the canonical body even at the top of the population. Falsifies any "best-of-run absorbing state" generalization. |
| **INCONCLUSIVE** | any pattern not above | Report descriptively; do not consolidate without additional data. |

**Threshold justification:** `F_seeded ≥ 15/20` matches §v2.4-proxy-4b's threshold for PASS; `R_exact ≤ 0.10` is slightly more permissive than §v2.4-proxy-4b's ≤ 0.036 (allows for ±pop variation). `R_exact ≥ 0.25` is ~7× the §v2.4-proxy-4b observed value and would be a clear qualitative inversion.

## Degenerate-success guard (required)

- **Too-clean (F=20/20 with R_exact=1.0):** would indicate the canonical body saturates the entire population under this intervention. Worth confirming via attractor inspection, but not degenerate — it is the expected PARTIAL-full-saturation outcome.
- **Arm A under full tape execution:** the "best-of-run" genotype under Arm A is the full 32-token tape, not just the canonical 12-token prefix. For the attractor inspection, the solver signature is "canonical 12 tokens followed by any 20-token tail that does not corrupt the output under Arm A's stack semantics." Winner-genotype classification should allow this flexibility.
- **Cross-commit drift:** re-run §v2.4-proxy-4b's Arm-0 seed_fraction=0.0 arm under each sweep — this drift check was already done in §v2.4-proxy-4b (0/20 matched §v2.4 baseline) but must replicate on the new commit.

## Statistical test (if comparing conditions)

- **Primary:** descriptive per-arm counts + R_exact upper bound per arm.
- **Paired McNemar:** Arm 0 vs Arm 1 and Arm 0 vs Arm 2 within each sweep. Classification: **confirmatory**; family: **proxy-basin family** (same as §v2.4-proxy-4b).
- **Cross-sweep contrast (exploratory):** §v2.4-proxy-4b (BP_TOPK preserve) vs this sweep (Arm A or consume) at seed_fraction=0.01. Descriptive effect-size only.
- **Significance threshold:** α = 0.05 raw; family-size for proxy-basin family grows by 2 (Arm A sweep + consume sweep) → at family size 3 (counting §v2.4-proxy-4b), corrected α = 0.05/3 ≈ 0.017.

## Diagnostics to log (beyond fitness)

- Per-seed F_AND + best-of-run best_fitness + holdout gap, per arm, per sweep
- final_mean_fitness, final_std_fitness, final_unique_genotypes per arm per sweep (R_exact proxy)
- Best-of-run genotype hex per seed per arm — check exact-canonical match rate at best-of-run layer
- Cross-sweep seed overlap: which seeds solve under both Arm A and consume seeded arms?

## Scope tag

**PASS-replication:** `cross-decoder / cross-executor · n=20 per arm per sweep · at pop=1024 gens=1500 v2_probe disable_early_termination=true tape=32 · on sum_gt_10_AND_max_gt_5 natural sampler · F/R dissociation replicates under Arm A and/or consume`

**PARTIAL-full-saturation:** `cross-decoder or cross-executor · n=20 per arm · saturated retention under the intervention — F and R co-move high`

**PARTIAL-canonical-displaced:** `cross-decoder or cross-executor · n=20 per arm · canonical body cannot hold best-of-run under this intervention — BP_TOPK preserve was the unique stabilizer`

## Decision rule

- **Both sweeps PASS →** update `findings.md#proxy-basin-attractor` narrowing row: the F/R dissociation generalises across decoder arms and executor rules on this task. Strong mechanism-level claim.
- **One sweep PASS, one PARTIAL →** document the differential. The F/R dissociation is partially decoder- or executor-specific.
- **Both sweeps PARTIAL (full-saturation) →** F and R co-move under non-BP_TOPK-preserve interventions. The F/R dissociation is BP_TOPK-preserve-specific. Narrow the `proxy-basin-attractor` narrowing to cite only BP_TOPK preserve as the regime where dissociation holds.
- **Both sweeps PARTIAL (canonical-displaced) →** BP_TOPK preserve was a uniquely-stabilising regime. Canonical body is not an absorbing attractor under other interventions. This would be a sharp narrowing.

---

*Audit trail.* Four outcome rows per sweep (principle 2). Thresholds anchored to §v2.4-proxy-4b's measured R_exact (principle 6). Internal controls are the seed_fraction gradients + cross-sweep contrast (principle 1). Degenerate-success candidates enumerated (principle 4). Principle 20 not triggered. Principle 22 classification: confirmatory, proxy-basin family, adds 2 confirmatory tests → family size 3, corrected α ≈ 0.017. Principle 23 pre-declared: both sweeps run as one batch. Decision rule commits to specific findings.md edits per outcome (principle 19).
