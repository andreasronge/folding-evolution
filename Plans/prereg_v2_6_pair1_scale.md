# Pre-registration: §v2.6-pair1-scale — compute scaling on Pair 1

**Status:** QUEUED · target commit `dbca965` · 2026-04-15

Pair 1 of §v2.6 (`any_char_count_gt_{1,3}_slot`, 6-token CHARS-chain body)
failed at 4/20 BOTH at matched compute. Direct genotype inspection showed
that components were present in 75–94% of failing winners but not correctly
chained. This prereg tests whether the failure is **search-landscape-limited**
(resolvable by budget) or **structural** (not resolvable at this decoder).

Parallel scaffold: an assembly-difficulty metric (ADI) extension to
`decode_winner.py` that quantifies the "components present but full body
not assembled" gap across sweeps. The metric is informative regardless of
this prereg's outcome — it extends existing chronicle data.

## Question (one sentence)

Does Pair 1's 4/20 BOTH at pop=1024 gens=1500 rise to ≥ 15/20 at 4× compute
(pop=2048, gens=3000), mirroring the pattern of scales-with-compute on
other body-invariant pairs?

## Hypothesis

From the §v2.6 Pair 1 attractor-inspection: required components (CHARS,
MAP_EQ_R, SUM, THRESHOLD_SLOT) are present in most failing winners but
not in the correct dependency chain. If the failure is assembly-limited
(high epistasis around body ordering, not mechanism absence), 4× compute
should close the gap — consistent with §v2.3 / §v2.6 Pair 2 / Pair 3 ceiling
behavior on simpler 4-token bodies. If the failure is structural at this
BP_TOPK(k=3) decoder regardless of compute, the 4/20 stays near floor.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_6_pair1_scale.yaml`
- **Task builders (reused, no sampler change):** `any_char_count_gt_1_slot`,
  `any_char_count_gt_3_slot` — same as §v2.6 Pair 1 baseline.
- **Alphabet:** `v2_probe`.
- **Fixed params:** pop=**2048**, gens=**3000**, n_examples=64,
  holdout_size=256, arm=BP_TOPK, topk=3, bond_protection_ratio=0.5,
  tape_length=32 — matched to §v2.4 compute-scaling (commit `94da867`).
- **Seeds:** 0..19 (n=20). Task-alternating period=300 (matched to baseline).
- **Est. compute:** ~45–60 min at 4 workers (4× baseline).

## Baseline measurement (required)

- **Baseline quantity:** `F_pair1_baseline` = per-task solve rate at pre-reg
  (§v2.6 Pair 1) compute (pop=1024, gens=1500).
- **Value:** F_gt_1 = 4/20, F_gt_3 = 4/20, **BOTH = 4/20** at commit
  `0230662` per §v2.6 chronicle.
- **Threshold calibration (principle 6):** "scales with compute" bar set
  at **BOTH ≥ 15/20** — the same §v2.3 scales bar used throughout v2
  (`max(Fmin − 3, 12)` formula). No Fmin discount because BP_TOPK 4× compute
  has already produced a 0/20 → 0/20 non-result on §v2.4, so the bar here
  is the cross-pair scales bar, not a baseline-plus-delta bar.

## Internal-control check (required)

- **Tightest internal contrast:** §v2.6 Pair 1 baseline itself (same task
  pair, same sampler, same alphabet, only pop/gens changed). Single-variable
  change.
- **Are you running it here?** yes.

## Sampler-design audit (principle 20)

**No sampler change** — same task builders as §v2.6 Pair 1 baseline. Gate
trivially satisfied. For traceability: class balance 50/50 per task (standard
`_gen_balanced`), primary-proxy (`'R' in s`) accuracy 0.607 on threshold=1
and 0.442 on threshold=3 (below random for threshold=3 — no cheap
single-predicate proxy attractor; this is already diagnostic of an assembly
problem rather than a proxy-basin problem).

## Pre-registered outcomes (required — at least three)

| outcome | quantitative criterion | interpretation |
|---|---|---|
| **PASS — scales-with-compute** | BOTH ≥ 15/20 AND F_gt_1 + F_gt_3 each ≥ 15/20 | Pair 1's baseline failure was **search-landscape-limited**, not structural. The constant-slot-indirection finding upgrades to `across-family / 2 body shapes` (the §v2.3 `INPUT SUM THRESHOLD_SLOT GT` body and this `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT` body). Consolidation note: this does NOT rescue §v2.6 Pair 2 / Pair 3 from their swamp status — those still need redesigned intermediate thresholds. |
| **PASS — partial** | BOTH in [10, 14] | Compute helps but the assembly barrier is only partly traversed at 4×. Report as-is; queue §v2.6-pair1-scale-8x as ambiguity-breaker if paper scope needs tightening. |
| **INCONCLUSIVE** | BOTH in [6, 9] | Mid-range; re-read ADI metric to distinguish "components present but not chained" vs "components missing." No automatic follow-up. |
| **FAIL — structural at BP_TOPK(k=3)** | BOTH ≤ 5/20 | 4× compute does NOT rescue. The §v2.6 Pair 1 failure is structural to the BP_TOPK decoder at k=3 on 6-token bodies. The `body-invariant-route mechanism` finding tightens: applies at 4-token body shapes, not 6-token string-chain bodies. Queue §v2.6-pair1-scale-A (same task under Arm A direct GP) as the decoder-variation follow-up. |

## Degenerate-success guard (required)

A too-clean PASS (e.g., 20/20 BOTH) must trigger attractor-category
inspection per methodology §21 and the updated skill's log-result
"too-clean OR threshold-adjacent" gate:

1. **Run `decode_winner.py v2_6_pair1_scale --all`** on the new sweep.
2. **Classify each winner's body:** is it the canonical
   `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT` chain, or an alternative
   assembly that achieves the label function through a different
   arrangement? (§v2.4-alt seed 2 precedent — multiple valid assemblies
   exist for compositional bodies.)
3. **Compute per-seed ADI components** (see scaffolded metric below):
   - `components_set`: does the winner's tape contain {CHARS, MAP_EQ_R,
     SUM, THRESHOLD_SLOT}?
   - `behavioral_solve`: does the winner score ≥ 0.999 on both tasks'
     cross_task_fitness?

If ≥ 15/20 PASS is driven by a single canonical-body attractor, the
mechanism name stays as-is. If alternative assemblies dominate, the
current name (`body-invariant-route mechanism, constant-slot variant`)
widens to something like `multi-assembly constant-slot indirection` —
which is a **broadening** rename per methodology §16b, not a narrowing.

## Statistical test

- **Test:** paired McNemar on seeds (0..19) comparing BOTH-solve at
  baseline (§v2.6 Pair 1, pop=1024 gens=1500) vs scaled (this sweep,
  pop=2048 gens=3000). Shared seeds enable pairing. One-sided α=0.05.
- **Note:** the scaled sweep re-uses the same task-builder seed, so the
  training distributions are identical per seed — true pairing, not just
  shared seed label.

## Diagnostics to log

- Per-pair: fixed-task solve counts, alternation BOTH, holdout gap.
- **ADI per seed** (components-present / behavioral-solve — see below).
- Winner-genotype decode on any seed with BOTH-solve ≥ 0.999 at scaled
  compute (attractor-category check).
- Fitness-trajectory plot (`fitness_trajectories.png`) to visualise
  plateau-then-jump vs smooth-climb signatures — the dynamic signature
  of assembly-limited runs (principle 21 / user's proposed metric #6).

## Scope tag

**If this experiment passes, the claim enters findings.md scoped as:**
`across-family / n=20 / 2 body shapes / at pop=2048 gens=3000
BP_TOPK(k=3,bp=0.5) / on {INPUT SUM THRESHOLD_SLOT GT, INPUT CHARS
MAP_EQ_R SUM THRESHOLD_SLOT GT}` — upgrading the current
`within-family / one body shape` scope. Pair 2 and Pair 3 remain in
swamp territory and are NOT incorporated by this experiment.

Explicitly **not** claiming: "compute rescues all assembly failures,"
"constant-slot-indirection is universal," or "6-token bodies always
solve at 4× compute."

## Decision rule

- **PASS-scales-with-compute →** (a) update findings.md
  `constant-slot-indirection` entry with the new scope tag and Pair 1
  scaled as a supporting experiment; (b) add the §v2.6-pair1-scale
  result to the Narrowing-history block as a **re-widening** (methodology
  §16b — renaming can widen scope when data shows the mechanism
  generalises beyond the narrowed claim); (c) queue §v2.6' intermediate
  threshold design for Pair 2/3 to escape swamp.
- **PASS-partial →** report; defer scope change until §v2.6-pair1-scale-8x
  clarifies.
- **INCONCLUSIVE →** report; run ADI diagnostic to decide between
  assembly-limited and mechanism-absent readings.
- **FAIL →** tighten constant-slot-indirection entry with a new
  narrowing row: "mechanism does not extend to 6-token CHARS-chain bodies
  at BP_TOPK(k=3) up to 4× compute." Queue §v2.6-pair1-scale-A (Arm A
  direct GP) as the decoder-variation follow-up before writing the
  tightened finding.

---

*Audit trail.* Gates met:
- Outcome table ≥ 3 rows including partial (principle 2). ✓
- Thresholds baseline-relative to §v2.3 scales bar (principle 6). ✓
- Tightest internal control is this exact sweep (principle 1). ✓
- Degenerate-success candidates enumerated with ADI inspection
  commitment (principle 4 + 21). ✓
- Sampler-design audit: no change, class balance + proxy accuracy
  recorded (principle 20). ✓

The ADI metric scaffolded alongside this prereg is a standing diagnostic
tool (methodology §21 — attractor-category classification for
threshold-adjacent outcomes). It applies to all chem-tape v2 sweeps
retroactively, not just this experiment.
