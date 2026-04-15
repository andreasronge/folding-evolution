# Pre-registration: §v2.6-pair1-scale-A — Pair 1 under Arm A direct GP

**Status:** PASS-partial · target commit `af0a7e5` · 2026-04-15 · resolved by [experiments-v2.md §v2.6-pair1 follow-up sweeps](../docs/chem-tape/experiments-v2.md) at commit `ef8f809` (BOTH_A=7, matched pre-reg `PASS — partial help from Arm A` row)

Derived from [docs/chem-tape/experiments-v2.md §v2.6-pair1-scale](../docs/chem-tape/experiments-v2.md#v26-pair1-scale). The 4× BP_TOPK run showed that component presence and BOTH-solve coincide once components are found, suggesting that BP_TOPK's permeability may be absorbing tape-level assembly scatter rather than causing the main remaining bottleneck.

## Question (one sentence)

On Pair 1 at the original budget (`pop=1024`, `gens=1500`), does Arm A direct execution outperform BP_TOPK because the developmental decoder is the bottleneck, or does the Pair 1 failure remain upstream of decoder choice?

## Hypothesis

If BP_TOPK's permeability is load-bearing, Arm A should not rescue Pair 1 and may even convert "components present" states into non-solvers because full-tape execution cannot skip interleaved junk. If the main bottleneck is upstream component discovery, Arm A should remain near the BP_TOPK baseline because swapping decoders does not materially change whether the needed tokens appear.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_6_pair1_scale_A.yaml`
- **Tasks:** `any_char_count_gt_1_slot`, `any_char_count_gt_3_slot`
- **Alphabet:** `v2_probe`
- **Fixed params:** `tape_length=32`, `n_examples=64`, `holdout_size=256`, `pop_size=1024`, `generations=1500`, `task_alternating_period=300`
- **Intervention:** `arm=A`
- **Seeds:** `0..19`
- **Est. compute:** same scale as the original Pair 1 run; decoder arm is the only intended axis.

## Baseline measurement (required)

- **Baseline quantity:** original BP_TOPK Pair 1 result at the same tasks, seeds, tape length, and compute.
- **Values:** `BOTH_BP = 4/20`, `COMP_BP = 6/20`, `ADI_BP = 0.10`
- **Threshold calibration (principle 6):** rows are defined relative to these measured BP_TOPK values and the decoder-arm question this experiment asks.

## Internal-control check (required)

- **Tightest internal contrast:** §v2.6 Pair 1 baseline (`arm=BP_TOPK`, `topk=3`, `bp=0.5`) vs this sweep (`arm=A`). Same tasks, seeds, alphabet, tape length, and compute; only decoder changes.
- **Are you running it here?** Yes.

## Sampler-design audit (principle 20)

**Not triggered.** Same task builders, same `n_examples`, same held-out evaluation, same seeds.

## Pre-registered outcomes (required — at least three)

Definitions:
- `BOTH =` seeds solving both alternating tasks.
- `COMP =` seeds whose winner contains the full canonical component set on both tasks.
- `ADI = (COMP - BOTH) / 20`.

| outcome | criterion | interpretation |
|---|---|---|
| **PASS — Arm A rescues** | `BOTH_A >= 10/20` AND `BOTH_A - BOTH_BP >= 6` | The BP_TOPK developmental layer is a real cost on this pair. Direct execution makes materially more of the search space reachable at the same compute. |
| **PASS — partial help from Arm A** | `BOTH_A in [6, 9]` | Decoder choice matters, but not enough to close the pair. Arm A is directionally better at this budget, yet Pair 1 is still hard for reasons beyond BP_TOPK alone. |
| **FAIL — permeability is load-bearing** | `COMP_A >= COMP_BP` AND `BOTH_A <= BOTH_BP + 1` | Arm A finds components at least as often as BP_TOPK but cashes them out no better. The BP_TOPK decoder's permeability, not raw component discovery, is doing real work on this body. |
| **FAIL — bottleneck is upstream of decoder** | `COMP_A <= COMP_BP + 1` AND `BOTH_A <= BOTH_BP + 1` | Swapping to direct GP does not materially improve component discovery or solve rate. Pair 1's failure is primarily upstream of decoder choice. |

## Degenerate-success guard (required)

- **Too-clean result to guard against:** `BOTH_A >= 15/20` with one brittle full-tape idiom dominating.
- **Checks required before verdict:**
  1. Decode all BOTH-solvers and classify whether Arm A winners are canonical full-tape chains, junk-tolerant full-tape programs, or token-set false positives.
  2. Report `COMP_A` and `ADI_A` alongside BOTH; a high `COMP_A` with low BOTH is the critical failure mode for the permeability hypothesis.
  3. Compare solved-seed overlap with the BP_TOPK baseline to see whether Arm A unlocks new seeds or merely re-solves the same easy ones.

## Statistical test

- **Primary comparison:** paired McNemar on BOTH-solve, Arm A vs BP_TOPK, seeds `0..19`, one-sided `alpha = 0.05` for `A > BP_TOPK`.
- **Secondary:** raw `COMP` and `ADI` differences, reported descriptively.

## Diagnostics to log

- BOTH, `COMP`, and `ADI`
- Winner decode on all BOTH-solvers
- Solved-seed overlap with BP_TOPK baseline
- Any cases with `COMP` present but not BOTH-solve

## Scope tag

**If Arm A rescues, the claim is still narrow:** `within-family · one 6-token CHARS-chain body · n=20 · Arm A vs BP_TOPK(k=3,bp=0.5) at pop=1024 gens=1500`

Explicitly **not** claimed: Arm A is generally better on chem-tape v2 tasks, or BP_TOPK is worse everywhere.

## Decision rule

- **PASS / PASS-partial →** record as decoder-arm evidence specific to Pair 1. No findings-level scope change without a second task family.
- **FAIL-permeability-load-bearing →** sharpen the interpretation from the 4× chronicle: BP_TOPK's permeability is part of why discovered components become behavioral solves.
- **FAIL-upstream →** treat decoder choice as secondary; discovery-focused interventions like `tape24` remain primary.

---

*Audit trail.* Four pre-registered rows, including a partial row, are committed before running (principle 2). Thresholds are relative to the measured BP_TOPK baseline in the same task/setup (principle 6). Internal control isolates the decoder arm as the only intended variable (principle 1). Degenerate-success checks and decode commitments are explicit (principle 4/21). Sampler audit not triggered (principle 20).
