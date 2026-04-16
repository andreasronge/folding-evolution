# Pre-registration: §v2.14b

**Status:** PARTIAL · commit `1fc51c5` · 2026-04-16

## Question (one sentence)

Does the safe-pop consume rule (which lifted 6-token mixed-type assembly in §v2.14) also affect the proxy-basin-attractor dynamics on the §v2.4 AND-composition tasks?

## Hypothesis

§v2.14 showed consume doubles BOTH-solve on the 6-token mixed-type body (4→8/20) by clearing type barriers in the str→charlist→intlist→int chain. The §v2.4 proxy-basin tasks use intlist inputs, so the type chain is simpler (intlist→int). The AND composition body is ~13 tokens but mostly int-typed after the first `SUM`/`REDUCE_MAX` pop.

**Prediction:** consume is likely **neutral** on these tasks because the type barriers that mattered in §v2.14 (str, charlist) don't exist here. However, during assembly of the 13-token AND body, transient type mismatches from wrong-order token sequences could still benefit from consume. Testing this distinguishes whether the §v2.14 effect is specific to multi-type-boundary chains or more general.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_14b_consume_proxy_natural.yaml`, `v2_14b_consume_proxy_decorr.yaml`
- **Arms / conditions:** consume rule only (2 sweeps). Preserve-rule baselines reused from §v2.4 (natural, commit `e3d7e8a`) and §v2.4-proxy (decorr, commit `0230662`). The preserve rule was the only executor mode at those commits; code changes since (adding safe_pop_mode) do not affect preserve-mode behavior.
- **Tasks:** `{sum_gt_10_AND_max_gt_5, sum_gt_10_OR_max_gt_5}` alternation, period 300.
- **Samplers:** (a) natural (§v2.4's sampler), (b) decorrelated (§v2.4-proxy's sampler, P(max>5|+)=1.0, P(max>5|−)=0.5).
- **Seeds:** 0-19
- **Fixed params:** pop=1024, gens=1500, BP_TOPK(k=3, bp=0.5), v2_probe alphabet
- **Est. compute:** ~30 min (2 sweeps × ~15 min)
- **Related experiments:** §v2.4 (F_AND=0/20 natural), §v2.4-proxy (F_AND=3/20 decorr), §v2.14 (consume PASS on 6-token body), §v2.12 (proxy basin is decoder-general)

**No sampler changes from §v2.4/§v2.4-proxy.** Same samplers, same tasks. Principle 20 not triggered.

## Baseline measurement (required)

- **Baseline quantity:** F_AND under preserve rule on each sampler
- **Measurement:** reused from prior experiments at the same budget/params
  - Natural: F_AND = 0/20 (§v2.4, commit `e3d7e8a`)
  - Decorr: F_AND = 3/20 (§v2.4-proxy, commit `0230662`)
- **Reuse justification:** preserve is the default safe_pop_mode. The `safe_pop_mode="preserve"` codepath is identical to pre-§v2.14 behavior (verified by §v2.14's replication check: P_easy=20/20 matches §v2.3, P_hard=4/20 matches §v2.6 Pair 1).

## Internal-control check (required)

- **Tightest internal contrast:** consume vs preserve on the SAME task, SAME seeds, SAME sampler. The §v2.4 prior data serves as the preserve arm.
- **Are you running it here?** Partially — using existing preserve-arm data rather than fresh runs. If the consume-arm shows a surprising result, a fresh preserve replication would be needed to rule out code drift.

## Pre-registered outcomes (required — at least three)

Let `P_nat` = 0/20 (§v2.4 preserve-natural), `C_nat` = consume-natural F_AND.
Let `P_dec` = 3/20 (§v2.4-proxy preserve-decorr), `C_dec` = consume-decorr F_AND.

| outcome | quantitative criterion | interpretation |
|---------|------------------------|----------------|
| **PASS — consume escapes basin** | `C_nat ≥ 4/20` OR `C_dec ≥ 8/20` | Safe-pop consume affects proxy-basin dynamics, not just typed-chain assembly. The executor decision rule reshapes the fitness landscape broadly enough to change which evolutionary basins are reachable. Major finding. |
| **PARTIAL — attractor shift without escape** | `C_nat ≤ 3/20` AND `C_dec ≤ 7/20` BUT attractor-category breakdown differs from preserve (different dominant proxy predicate or different attractor shares) | Consume changes the landscape details but doesn't help escape the basin. The proxy-basin is robust to executor-rule variation, but the specific proxy that dominates shifts. Minor finding. |
| **INCONCLUSIVE — identical to preserve** | `C_nat ≤ 1/20` AND `C_dec` within ±2 of `P_dec` AND attractor breakdown matches preserve (same dominant categories, same shares ±10%) | Safe-pop mode is irrelevant on intlist-only tasks. The §v2.14 effect is specific to multi-type-boundary chains, not a general executor-landscape property. Narrows §v2.14's scope. |
| **FAIL — consume worse** | `C_dec < P_dec − 2` (i.e., `C_dec = 0/20`) AND attractor inspection shows consume produces lower-fitness programs | Consume actively damages search on AND-composition. The stack-jam clearing that helps assembly on mixed-type chains hurts on int-chain composition. |

**Threshold justification:** `C_nat ≥ 4/20` as PASS is absolute-looking, but it's against the `P_nat = 0/20` baseline — ANY AND-solve on the natural sampler under consume would be remarkable given that preserve, Arm A, and 4× compute all scored 0/20. The `C_dec ≥ 8/20` threshold is relative to `P_dec = 3/20` with a +5 lift, calibrated to exceed the §v2.14 noise band.

## Degenerate-success guard (required)

- **Too-clean result:** consume 10+/20 F_AND on natural sampler
  - **Candidate degenerate mechanism:** if consume accidentally makes programs that output constant-1 on the natural sampler (where ~65% of examples are label-1 due to correlated predicates), that would score ~0.65, not ≥0.999. So constant-output degeneracy can't produce high F_AND.
  - **How to detect:** winner-genotype inspection on all AND-solving seeds. Check for: (a) genuine AND-composition programs, (b) novel single-predicate proxies that happen to correlate better under consume, (c) overfitting to training set.
- **Attractor-category inspection (principle 21):** required for all results since the baseline is at 0/20 (any non-zero result is threshold-adjacent). Run attractor classification on all 20 consume seeds per sampler regardless of F_AND.

## Statistical test (if comparing conditions)

- **Test:** not applicable in the traditional sense — comparing against historical baselines (§v2.4, §v2.4-proxy), not paired same-commit runs. Descriptive comparison (F_AND counts + attractor breakdown) is the primary analysis. If consume produces F_AND > 0 on natural, the significance is self-evident against a 0/20 baseline.

## Diagnostics to log (beyond fitness)

- Per-seed best-fitness under consume for both samplers
- Winner-genotype decoded programs for ALL 20 seeds under consume × both samplers (attractor-category classification)
- Attractor-category breakdown (same taxonomy as §v2.4/§v2.12: max_gt_5, sum_gt_10, and_composition, other)
- Holdout gap (overfitting check — §v2.12 showed 13/20 overfit seeds on Arm A decorr)

## Scope tag (required for any summary-level claim)

**If this experiment passes, the claim enters findings.md scoped as:**
`within-family / n=20 / at BP_TOPK(k=3,bp=0.5) v2_probe / on AND-composition intlist tasks / executor-rule ablation / exploratory`

## Decision rule

- **PASS →** This is a major finding: executor semantics affect proxy-basin dynamics. Promote both §v2.14 and §v2.14b together to findings.md as "safe-pop consume lifts evolutionary search on both mixed-type assembly and proxy-basin tasks." Consider making consume the project default.
- **PARTIAL →** Characterize the attractor shift. The consume rule reshapes the proxy landscape without escaping it. Document as a narrowing of the proxy-basin finding (executor-sensitive attractor selection, even if not basin escape).
- **INCONCLUSIVE →** §v2.14's effect is specific to multi-type-boundary chains. Promote §v2.14 alone to findings.md scoped to mixed-type bodies. The proxy-basin-attractor finding is confirmed as executor-invariant (adding to its decoder-general status from §v2.12).
- **FAIL →** Document. Do NOT make consume the project default — it helps mixed-type assembly but hurts int-chain composition.
