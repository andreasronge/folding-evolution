# Pre-registration: §v2.6-pair1-scale-8x — Pair 1 at 8× compute

**Status:** PASS-partial · target commit `af0a7e5` · 2026-04-15 · resolved by [experiments-v2.md §v2.6-pair1 follow-up sweeps](../docs/chem-tape/experiments-v2.md) at commit `ef8f809` (BOTH_8x=13, matched pre-reg `PASS — partial, still discovery-limited` row with a noted off-by-one on the strict COMP=BOTH criterion — one alternative-assembly solver, |ADI|=0.05; methodology lesson recorded in chronicle)

Derived from [docs/chem-tape/experiments-v2.md §v2.6-pair1-scale](../docs/chem-tape/experiments-v2.md#v26-pair1-scale). The 4× run moved Pair 1 from 4/20 to 8/20 BOTH and closed the assembly barrier (`ADI = 0.00`), but left the result pre-registered `INCONCLUSIVE`.

## Question (one sentence)

At 8× compute (`pop=4096`, `gens=6000`), does Pair 1 move from the 4× mid-band into a genuine scales-with-compute regime, or does it remain component-discovery-limited on the 32-cell tape?

## Hypothesis

The 4× run already closed the assembly barrier: components-present and BOTH coincide at 8/20, and `ADI = 0.00`. If Pair 1 is still budget-limited upstream of assembly, 8× compute should mainly raise **component discovery** and bring BOTH up with it. If the 8× run stays near 8/20, the current 32-cell tape/alphabet setup is discovery-limited rather than merely under-budgeted.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_6_pair1_scale_8x.yaml`
- **Tasks:** `any_char_count_gt_1_slot`, `any_char_count_gt_3_slot`
- **Alphabet:** `v2_probe`
- **Fixed params:** `tape_length=32`, `n_examples=64`, `holdout_size=256`, `arm=BP_TOPK`, `topk=3`, `bond_protection_ratio=0.5`, `task_alternating_period=300`
- **Intervention:** `pop_size=4096`, `generations=6000`
- **Seeds:** `0..19`
- **Est. compute:** long sweep; same task pair and decoder as §v2.6 Pair 1, only budget changes.

## Baseline measurement (required)

- **Baseline quantity:** 4× Pair 1 result from §v2.6-pair1-scale at matched decoder/tape/task setup.
- **Values:** `BOTH_4x = 8/20`, `COMP_4x = 8/20`, `ADI_4x = 0.00`
- **Threshold calibration (principle 6):** outcome rows are defined relative to these measured 4× values, not imported from a different pair or decoder.

## Internal-control check (required)

- **Tightest internal contrast:** §v2.6-pair1-scale (4×) vs this 8× run. Same tasks, sampler, decoder, alphabet, and tape length; only budget changes.
- **Are you running it here?** Yes.

## Sampler-design audit (principle 20)

**Not triggered.** No task-builder or training-distribution change; same alternating pair and same seeds as the baseline and 4× runs.

## Pre-registered outcomes (required — at least three)

Definitions:
- `BOTH =` seeds solving both alternating tasks.
- `COMP =` seeds whose winner contains the full canonical component set on both tasks.
- `ADI = (COMP - BOTH) / 20`.

| outcome | criterion | interpretation |
|---|---|---|
| **PASS — scales with compute** | `BOTH_8x >= 14/20` AND `BOTH_8x - BOTH_4x >= 6` | Pair 1 was still compute-limited at 4×. The component-discovery barrier on the 32-cell tape can be pushed substantially further by budget alone. |
| **PASS — partial, still discovery-limited** | `BOTH_8x in [10, 13]` AND `COMP_8x = BOTH_8x` AND `ADI_8x <= 0.05` | More budget helps, but the remaining gap is upstream of assembly: discovered components rise, and solves rise with them, yet the pair still does not clear the scales bar. |
| **INCONCLUSIVE — little slope beyond 4×** | `BOTH_8x in [8, 9]` | The 8× run does not materially move beyond the 4× result. "Just add compute" is not an adequate explanation at this tape length / alphabet setting. |
| **FAIL — discovery ceiling at 32 cells** | `BOTH_8x <= 7` | Even 8× compute fails to improve on the 4× result. Pair 1's main bottleneck is not residual assembly difficulty; it is a more structural discovery limit on this representation/configuration. |

## Degenerate-success guard (required)

- **Too-clean result to guard against:** `BOTH_8x >= 18/20` with a single winner architecture dominating.
- **Checks required before verdict:**
  1. Run winner decode on all BOTH-solvers and classify whether they are canonical-chain or alternative assemblies.
  2. Report `COMP_8x` and `ADI_8x`; a PASS driven by `COMP_8x >> BOTH_8x` would actually be an assembly relapse, not a clean discovery gain.
  3. Compare solved-seed identities against the 4× run to check whether 8× adds genuinely new seeds or merely stabilizes previously solved ones.

## Statistical test

- **Primary comparison:** paired McNemar on BOTH-solve, 4× vs 8×, seeds `0..19`, one-sided `alpha = 0.05`.
- **Secondary:** raw lift in `COMP` and `ADI`; no extra null-comparison against historical runs.

## Diagnostics to log

- BOTH solve count, component-present count, and `ADI`
- Winner decode for all BOTH-solvers
- Solved-seed identity set relative to the 4× run
- Fitness trajectories and first-solve generations for any new solves

## Scope tag

**If this experiment passes, the claim remains narrow:** `within-family · one 6-token CHARS-chain body · n=20 · BP_TOPK(k=3,bp=0.5) · tape_length=32 · pop=4096 gens=6000`

Explicitly **not** claimed: general scaling of all 6-token bodies, body-length as the decisive axis, or decoder-agnostic rescue.

## Decision rule

- **PASS-scales →** record as a positive slope-tightening result for this one body. No automatic findings upgrade beyond the current narrow scope without a second body or decoder replication.
- **PASS-partial →** record as "compute helps discovery but does not close the pair." Keeps `tape24` and `scale-A` load-bearing.
- **INCONCLUSIVE or FAIL →** treat the 32-cell discovery limit as unresolved by budget. `tape24` becomes the primary next test; `scale-A` remains the decoder counterfactual.

---

*Audit trail.* Outcome table has four rows including a partial row (principle 2). Thresholds are explicitly relative to the measured 4× baseline (principle 6). Internal control is the matched 4× run with only budget changed (principle 1). Degenerate-success checks are committed up front (principle 4). Sampler audit not triggered (principle 20).
