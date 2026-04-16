# Pre-registration: §v2.14e

**Status:** QUEUED · target commit `TBD` · 2026-04-16

## Question (one sentence)

Does the safe-pop consume effect on 6-token mixed-type assembly replicate on a second slot binding (MAP_EQ_E instead of MAP_EQ_R), or is it specific to the R-count body?

## Hypothesis

§v2.14 showed consume lifts BOTH from 4→8/20 on the string-count body with slot_12=MAP_EQ_R. The canonical body is `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT`. The type chain (str→charlist→intlist→int) is identical regardless of which MAP op is at slot_12. If the consume effect is driven by the type-chain structure (as the stack-jam reading predicts), it should replicate with MAP_EQ_E. If it's specific to the MAP_EQ_R op or the R-count task distribution, it won't.

**Requires new task definitions:** `any_char_count_E_gt_1_slot` and `any_char_count_E_gt_3_slot`, identical to the R-count tasks but with target="E" and slot_12=MAP_EQ_E. The canonical body becomes `INPUT CHARS MAP_EQ_E SUM THRESHOLD_SLOT GT`.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_14e_consume_E_preserve.yaml`, `v2_14e_consume_E_consume.yaml`
- **Arms / conditions:** 2 executor rules (preserve, consume) × E-count pair = 2 sweeps
- **Tasks:** `{any_char_count_E_gt_1_slot, any_char_count_E_gt_3_slot}` alternation, period 300
- **Seeds:** 0-19
- **Fixed params:** pop=1024, gens=1500, BP_TOPK(k=3, bp=0.5), v2_probe alphabet, tape_length=32
- **Est. compute:** ~30 min (2 sweeps × ~15 min)
- **Related experiments:** §v2.14 (R-count: preserve 4/20, consume 8/20)

No sampler changes from the R-count tasks (same string alphabet, same balanced sampling, different target character). Principle 20 not triggered — the label function changes (count E instead of count R) but the input distribution is the same length-16 strings over the same 53-char alphabet.

## Baseline measurement (required)

- **Baseline quantity:** BOTH-solve rate under preserve on the E-count pair. This is a NEW pair — no prior baseline exists.
- **Measurement:** the preserve arm of THIS experiment is the baseline.
- **Expected value (calibration):** ~4/20 BOTH if the E-count tasks have similar difficulty to R-count. 'E' and 'R' have the same frequency in the 53-char string alphabet (each appears once), so the label distribution should be statistically identical. But this is a prediction, not a measurement — the actual preserve-arm result is the binding baseline.

## Internal-control check (required)

- **Tightest internal contrast:** preserve vs consume on the SAME E-count pair, SAME seeds, SAME commit. The ablation IS the internal control.
- **Are you running it here?** Yes.

## Pre-registered outcomes (required — at least three)

Let `P_E` = preserve-arm E-count BOTH, `C_E` = consume-arm E-count BOTH.

| outcome | quantitative criterion | interpretation |
|---------|------------------------|----------------|
| **PASS — replicates** | `C_E > P_E + 3` AND `P_E` within ±3 of 4/20 (confirming comparable difficulty) | Consume effect replicates on a second slot binding. The stack-jam mechanism is type-chain-driven, not op-specific. Broadens findings.md from one-pair to two-pair within-family. |
| **PARTIAL — replicates but baseline differs** | `C_E > P_E + 3` BUT `P_E` deviates from 4/20 by > 3 (i.e., `P_E ≤ 1` or `P_E ≥ 8`) | The consume lift is present but on a differently-difficult baseline. The E-count pair is either harder or easier than R-count. Interpretable as replication on a different baseline, not a clean replication of the §v2.14 effect size. |
| **INCONCLUSIVE** | `|C_E − P_E| ≤ 3` | Consume does not lift the E-count body. Either the effect is R-count-specific (unexpected given identical type chain) or the E-count tasks have different difficulty characteristics (e.g., swamped at `P_E ≥ 18`). |
| **FAIL — consume worse** | `C_E < P_E − 3` | Consume hurts on the E-count body. Unexpected — would require inspection to understand. |

**Threshold justification:** ±3 matches the §v2.14 noise band. The `P_E` calibration check (within ±3 of 4/20) ensures the E-count pair is comparably difficult to the R-count pair.

## Degenerate-success guard (required)

- **Swamp check:** if `P_E ≥ 18/20`, the E-count pair is too easy. The preserve baseline itself would show this. Log but do not interpret the consume comparison on a swamped pair (same lesson as §v2.6 Pair 2/3).
- **Too-clean result:** C_E = 20/20 with P_E ≈ 4/20 — a +16 delta would be extraordinary. Inspect winners for degenerate programs.
- **Seed overlap with §v2.14 R-count consume solvers:** if the same seeds solve on both slot bindings, the effect is seed-determined, not op-determined. If different seeds solve, the effect interacts with the specific slot op.

## Statistical test (if comparing conditions)

- **Test:** paired McNemar on seeds 0-19 (preserve vs consume on E-count pair). Secondary: seed-overlap with §v2.14 R-count results.
- **Significance threshold:** α = 0.05, two-sided (likely underpowered at n=20).

## Diagnostics to log (beyond fitness)

- Per-seed BOTH-solve + best-fitness under both rules
- Winner-genotype attractor-category classification on both arms
- Seed overlap between E-count and R-count (§v2.14) solver sets under consume
- Holdout gap

## Scope tag (required for any summary-level claim)

`within-family / n=20 / at BP_TOPK(k=3,bp=0.5) v2_probe / on 6-token E-count body / executor-rule ablation replication`

## Decision rule

- **PASS →** Broaden findings.md `safe-pop-consume-effect` scope from "one slot binding (MAP_EQ_R)" to "two MAP-family slot bindings (MAP_EQ_R, MAP_EQ_E)." The consume effect is type-chain-driven, not op-specific.
- **PARTIAL →** Document the replication with the baseline caveat. The finding broadens but the effect size comparison is confounded by difficulty differences.
- **INCONCLUSIVE →** The finding stays at one-pair scope. The E-count non-replication doesn't falsify the R-count result but prevents broadening.
- **FAIL →** Investigate. If the failure is specific to the E-count distribution, the finding stays narrow. If it reveals a §v2.14 artifact, flag for retraction review.
