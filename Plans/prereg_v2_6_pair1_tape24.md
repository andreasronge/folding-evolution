# Pre-registration: §v2.6-pair1-tape24 — Pair 1 at shorter tape length

**Status:** QUEUED · target commit `af0a7e5` · 2026-04-15

Derived from [docs/chem-tape/experiments-v2.md §v2.6-pair1-scale](../docs/chem-tape/experiments-v2.md#v26-pair1-scale). The 4× run closed the assembly barrier but left Pair 1 component-discovery-limited on the 32-cell tape. This experiment asks whether tighter per-cell token pressure reduces that upstream discovery burden.

## Question (one sentence)

At the original compute budget, does shortening the tape from 32 to 24 cells materially improve Pair 1 by increasing canonical-component discovery?

## Hypothesis

If Pair 1 is discovery-limited because six required tokens are diluted across a 32-cell tape, then a 24-cell tape should raise `COMP` even if the decoder and compute stay fixed. If `COMP` does not move, the barrier is not simply token-pressure on tape length.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_6_pair1_tape24.yaml`
- **Tasks:** `any_char_count_gt_1_slot`, `any_char_count_gt_3_slot`
- **Alphabet:** `v2_probe`
- **Fixed params:** `n_examples=64`, `holdout_size=256`, `pop_size=1024`, `generations=1500`, `arm=BP_TOPK`, `topk=3`, `bond_protection_ratio=0.5`, `task_alternating_period=300`
- **Intervention:** `tape_length=24`
- **Seeds:** `0..19`
- **Est. compute:** same order as the original Pair 1 baseline; tape length is the only intended axis.

## Baseline measurement (required)

- **Baseline quantity:** original 32-cell Pair 1 result at matched compute and decoder.
- **Values:** `BOTH_32 = 4/20`, `COMP_32 = 6/20`, `ADI_32 = 0.10`
- **Threshold calibration (principle 6):** rows are defined relative to these measured 32-cell values, not to another pair or another decoder.

## Internal-control check (required)

- **Tightest internal contrast:** §v2.6 Pair 1 baseline (`tape_length=32`) vs this sweep (`tape_length=24`). Same tasks, seeds, alphabet, decoder, and compute; only tape length changes.
- **Are you running it here?** Yes.

## Sampler-design audit (principle 20)

**Not triggered.** Same task builders and seed schedule; tape length changes representation capacity, not the training distribution.

## Pre-registered outcomes (required — at least three)

Definitions:
- `BOTH =` seeds solving both alternating tasks.
- `COMP =` seeds whose winner contains the full canonical component set on both tasks.
- `ADI = (COMP - BOTH) / 20`.

| outcome | criterion | interpretation |
|---|---|---|
| **PASS — tape shortening closes discovery gap** | `COMP_24 >= 12/20` AND `COMP_24 - COMP_32 >= 6` AND `BOTH_24 >= 10/20` | The 32-cell representation was discovery-diluted. Shorter tapes materially improve Pair 1 by increasing canonical-component discovery. |
| **PASS — partial discovery gain** | `COMP_24 in [9, 11]` AND `COMP_24 - COMP_32 >= 3` | Tighter tape pressure helps component discovery, but not enough to close the pair at this compute budget. |
| **INCONCLUSIVE — discovery moves only slightly** | `COMP_24 in [7, 8]` | There is some discovery lift, but too little to support a strong tape-length claim. |
| **FAIL — tape length is not the main barrier** | `COMP_24 <= 6` | Shortening the tape does not improve canonical-component discovery. The upstream bottleneck lies elsewhere (alphabet search, decoder interactions, or general search difficulty). |

## Degenerate-success guard (required)

- **Too-clean result to guard against:** `COMP_24` jumps sharply but `ADI_24` also rises, suggesting the shorter tape creates component presence without executable solves.
- **Checks required before verdict:**
  1. Report BOTH, `COMP`, and `ADI` together; `COMP` lift without BOTH lift is not a clean rescue.
  2. Decode all BOTH-solvers to confirm the shorter tape does not merely create a new alternative attractor unrelated to the canonical body.
  3. Compare solved-seed identities against the 32-cell baseline to see whether tape shortening unlocks new seeds.

## Statistical test

- **Primary comparison:** paired McNemar on BOTH-solve, tape24 vs tape32 baseline, seeds `0..19`, one-sided `alpha = 0.05` for `tape24 > tape32`.
- **Secondary:** descriptive lift in `COMP` and change in `ADI`.

## Diagnostics to log

- BOTH, `COMP`, and `ADI`
- Winner decode on all BOTH-solvers
- Solved-seed overlap with 32-cell baseline
- Any cases where `COMP` rises but BOTH does not

## Scope tag

**If this experiment passes, the claim stays narrow:** `within-family · one 6-token CHARS-chain body · n=20 · BP_TOPK(k=3,bp=0.5) · tape_length 24 vs 32 at pop=1024 gens=1500`

Explicitly **not** claimed: "shorter tapes are better" in general, or that tape length alone explains the broader v2.6 breadth failure.

## Decision rule

- **PASS / PASS-partial →** record as representation-pressure evidence specific to Pair 1. The dominant mechanism reading becomes "component discovery is sensitive to tape length on this body."
- **INCONCLUSIVE →** report as weak evidence only; no scope change.
- **FAIL →** deprioritize tape length as the main rescue axis; keep decoder and alphabet explanations in front.

---

*Audit trail.* Outcome table includes four rows with a partial row (principle 2). Thresholds are explicitly baseline-relative to the measured 32-cell Pair 1 run (principle 6). Internal control changes only tape length (principle 1). Degenerate-success checks are committed before running (principle 4). Sampler audit not triggered (principle 20).
