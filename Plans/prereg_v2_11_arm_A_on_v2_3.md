# Pre-registration: §v2.11 — Arm A direct GP on §v2.3's `sum_gt_{5,10}_slot` pair

**Status:** DONE · PASS (decoder-robust) · run commit `29c524e` · chronicle commit `23826da` · 2026-04-16

Derived from the decoder-arm dependence caveat added to
[`docs/chem-tape/findings.md#constant-slot-indirection`](../docs/chem-tape/findings.md)
on 2026-04-15 (commit `344e4de`) and from the §v2.6-pair1 follow-up sweeps
([`docs/chem-tape/experiments-v2.md §v2.6-pair1 follow-up sweeps`](../docs/chem-tape/experiments-v2.md))
which observed Arm A at 1× compute ≈ BP_TOPK at 4× compute on a 6-token body.

## Question (one sentence)

On §v2.3's `sum_gt_{5,10}_slot` pair — the **only** body where the
`constant-slot-indirection` mechanism is currently demonstrated at
precision (80/80 across four seed blocks under BP_TOPK(k=3, bp=0.5)) —
does Arm A direct GP at matched compute reproduce the BOTH-solve, or
does the mechanism narrow to the BP_TOPK decoder?

## Hypothesis

`findings.md#constant-slot-indirection` is currently `NARROWED · within-family
· one body shape · n=80 on one pair` and carries a decoder-arm dependence
caveat: "the finding should be read as specific to the tested decoder arm
when the body shape demands ≥6 tokens in strict dependency order. On
4-token bodies (§v2.3), decoder choice did not matter because the search
landscape was swamp-level easy; on 6-token bodies, it materially does."

The **caveat is itself untested on the §v2.3 body**. The "did not matter"
clause is an assertion drawn from §v2.3's BP_TOPK landscape behavior, not
a measured Arm A vs BP_TOPK comparison on this pair. This experiment fills
that gap. Three plausible outcomes:

1. **Arm A reproduces ≈80/80** → decoder-independence on 4-token bodies;
   caveat narrows correctly to "Pair-1-specific."
2. **Arm A produces materially less** → §v2.3's 80/80 is partly BP_TOPK's
   permeability absorbing tape-level scatter even on a 4-token body;
   constant-slot-indirection finding splits into two decoder-specific claims.
3. **Arm A produces materially more** → unlikely but possible; would be
   itself a new finding (Arm A is more discriminating on this body class).

## Setup

- **Sweep files:**
  - `experiments/chem_tape/sweeps/v2/v2_11_arm_A_alt.yaml` — alternation
    `{sum_gt_5_slot, sum_gt_10_slot}` under Arm A.
  - `experiments/chem_tape/sweeps/v2/v2_11_arm_A_fixed.yaml` — fixed-task
    baselines under Arm A on each task (matches §v2.3's
    `v2_3_fixed_baselines.yaml` shape).
- **Tasks:** `sum_gt_5_slot`, `sum_gt_10_slot` (existing in `TASK_REGISTRY`).
- **Alphabet:** `v2_probe`.
- **Intervention:** `arm: A` (only change vs §v2.3).
- **Fixed params (matched verbatim to §v2.3 prereg block, seeds 0..19):**
  `tape_length=32`, `n_examples=64`, `holdout_size=256`, `pop_size=1024`,
  `generations=1500`, `tournament_size=3`, `elite_count=2`, `mutation_rate=0.03`,
  `crossover_rate=0.7`, `task_alternating_period=300`.
- **Seeds:** `0..19` — matched to §v2.3's first seed block (the only block
  where a paired McNemar comparison is defensible, since seed RNG streams
  are identical under matched config).
- **Est. compute:** ~15 min at 10 workers (60 runs total: 20 alt + 20 fixed×2).
- **Related experiments:** [§v2.3 (the body)](../docs/chem-tape/experiments-v2.md#v23) ·
  [§v2.6-pair1 follow-up sweeps (Arm A on Pair 1)](../docs/chem-tape/experiments-v2.md#v26-pair1-follow-up-sweeps-2×2×2-of-compute-×-tape-×-decoder).

## Baseline measurement (required)

- **Baseline quantity:** §v2.3's BP_TOPK(k=3, bp=0.5) result at the same
  task pair, same seeds, same compute.
- **Measurement:** previously recorded in `experiments/output/2026-04-14/v2_3_alternation/`
  and `experiments/output/2026-04-14/v2_3_fixed_baselines/` at commit `e3d7e8a`.
- **Values (seeds 0..19 block, the matching subset):**
  `BOTH_BP = 20/20` · `F_5_BP = 20/20` · `F_10_BP = 19/20` ·
  flip-events: 100 alternation transitions, all zero-cost
  · max |train−holdout gap| = 0.000 on alternation, 0.016 on fixed.
- **Threshold calibration (principle 6):** outcome rows below are
  expressed as deltas from `BOTH_BP = 20/20`. Absolute "≥18/20" wording
  is used as a proxy for "≤2 BOTH-solves below baseline" because the
  BP_TOPK side is at the literal ceiling and absolute and relative
  framings coincide there.

## Internal-control check (required)

- **Tightest internal contrast:** §v2.3 itself. Same task pair, same
  seeds, same compute, same tape. **Only `arm` varies.** This is the
  cleanest decoder-arm contrast available in the project.
- **Are you running it here?** Yes. This experiment IS the within-family
  decoder-arm internal control (per principle 1).

## Sampler-design audit (principle 20)

**NOT TRIGGERED.** No change to training distribution: same task builders
(`make_sum_gt_5_slot_task`, `make_sum_gt_10_slot_task`), same `n_examples`,
same `holdout_size`, same per-seed RNG path. Class balance, proxy accuracy,
and label-function viability are inherited verbatim from §v2.3 and were
recorded there.

## Pre-registered outcomes (required — at least three)

Definitions:
- `BOTH_A = ` Arm A alternation seeds with both tasks ≥ 0.999 on winner.
- `F_5_A` , `F_10_A = ` Arm A fixed-task solve counts at fitness ≥ 0.999.
- `Fmin_A = min(F_5_A, F_10_A)` — Arm A's own fixed-task ceiling on this
  pair. **Used as the principle-6 baseline for alternation-cost
  interpretation, not just the BP_TOPK reference.**
- `alt_cost_A = Fmin_A − BOTH_A` (per-pair alternation cost on the
  Arm A side, anchored to its own ceiling).
- `Δ_BOTH = BOTH_BP − BOTH_A`. Positive Δ means Arm A is worse on
  alternation than BP_TOPK.
- `Δ_F = (F_5_BP + F_10_BP)/2 − (F_5_A + F_10_A)/2` (fixed-task
  decoder main effect, averaged across the pair).
- `flip_cost_A = ` mean post-flip fitness drop on alternation transitions.
- `attractor_PASS_share` (computed post-hoc per inspection commitment
  below): fraction of `BOTH_A` winners where the slot-indirection
  mechanism is the causally-attributed solve route (NOT merely
  THRESHOLD_SLOT-token-present, which is a correlate).

The table is structured so **decoder main effect** (`Δ_F`) and
**alternation cost** (`alt_cost_A`) are separable. Cells without a
unique row land in a default "INCONCLUSIVE" reading; row precedence is
top-to-bottom (first matching row wins).

| outcome | criterion | interpretation |
|---|---|---|
| **PASS — decoder-robust** | `BOTH_A ≥ 18/20` AND `F_5_A ≥ 18/20` AND `F_10_A ≥ 17/20` AND `flip_cost_A < 0.05` AND `alt_cost_A ≤ 1` AND `attractor_PASS_share ≥ 0.85` | Mechanism extends to Arm A at matched compute AND is causally slot-indirection (not parallel-per-task or token-present-correlate). Caveat in `findings.md#constant-slot-indirection` narrows to "Pair-1-specific." Promote no new claim; rewrite the caveat. |
| **PASS — decoder-robust on solve, mechanism uncertain** | `BOTH_A ≥ 18/20` AND `F_5_A ≥ 18/20` AND `F_10_A ≥ 17/20` AND `flip_cost_A < 0.05` AND `attractor_PASS_share < 0.85` | Solve count matches BP_TOPK but Gate 4 inspection cannot confirm slot-indirection mechanism. Decoder-arm extends solve capability but the mechanism reading does not transfer. Add "mechanism-attribution-uncertain on this decoder" caveat. Do NOT narrow Pair-1-specific caveat. |
| **PASS — partial (alternation cost real)** | `Fmin_A ≥ 18/20` AND `alt_cost_A in [2, 5]` AND `flip_cost_A ≥ 0.05` | Arm A reaches the body solo but pays a measurable alternation cost that BP_TOPK did not. Decoder-efficiency axis is real on 4-token bodies. Add "decoder-efficiency dependence on alternation" to scope boundaries. |
| **PASS — partial (decoder cost on fixed)** | `Δ_F ≥ 2` AND `BOTH_A ≥ Fmin_A − 1` AND `flip_cost_A < 0.05` | Arm A is materially worse on fixed-task solve than BP_TOPK but alternation tracks its own ceiling cleanly. Decoder main effect on fixed-task ceiling is the load-bearing differentiator, not slot-indirection. Add "decoder main effect on fixed-task ceiling" to scope boundaries. |
| **INCONCLUSIVE — efficiency-loss with structure** | `BOTH_A in [6, 17]` AND `attractor_PASS_share ≥ 0.50` AND inspection shows a coherent attractor pattern (e.g., consistent canonical body across solvers) | Mechanism partially extends; Arm A's solvers use slot-indirection but at lower efficiency. Report as-is; queue `§v2.11-scale` (Arm A at 4× compute). No findings change. |
| **INCONCLUSIVE — noisy middle** | `BOTH_A in [6, 17]` AND `attractor_PASS_share < 0.50` AND no coherent attractor pattern | Mechanism story unclear; Arm A solvers do not converge to a consistent body. Report as-is. Strong candidate for follow-up §v2.11-inspection-deeper before any scope change. No findings change. |
| **FAIL — decoder-specific (with mechanism evidence)** | `BOTH_A ≤ 5/20` AND inspection shows BP_TOPK's solvers used canonical slot-indirection AND Arm A's failures contain the canonical token set but fail to extract behaviorally | §v2.3's 80/80 required BP_TOPK's permeability or extraction; Arm A cannot reach the same mechanism even with components present. **Decision: SPLIT** the claim into two decoder-specific claims via supersession-mode. The two-claim split is the right action because BP_TOPK and Arm A operate on the same components but achieve different behavioral outcomes — they are mechanistically distinct, not just efficiency-different. |
| **FAIL — efficiency only** | `BOTH_A ≤ 5/20` AND inspection shows Arm A's failures DO NOT contain the canonical token set in most seeds (component-discovery upstream of decoder) | Arm A fails for component-discovery reasons (per §v2.6-pair1-scale precedent), NOT because the mechanism is decoder-specific. **Decision: NARROW** the claim to "BP_TOPK(k=3, bp=0.5) only" with explicit "Arm A fails upstream-of-decoder on this body" caveat — do NOT split the claim, since the mechanism IS the same when reachable. |

Notes on row construction:
- Asymmetric per-task cutoffs (F_5_A ≥ 18, F_10_A ≥ 17) are because
  §v2.3's BP_TOPK F_10 was 19/20 on this seed block (one stuck seed),
  not 20/20. Bar set 1 below BP_TOPK per task.
- Two PASS-partial rows separate alternation-cost (Arm A's body solo
  is fine but pays alternation overhead) from decoder-main-effect
  (Arm A's body solo is worse). Both are partial readings but
  different mechanism implications.
- Two INCONCLUSIVE rows distinguish "structure with low solve" from
  "no structure." Per principle 21 the attractor-category classifier
  is what differentiates them.
- Two FAIL rows explicitly pre-commit the supersession choice between
  SPLIT (decoder-specific mechanism) and NARROW (efficiency-only) based
  on the Gate 4 inspection of failure-mode token presence — addressing
  the "post-hoc choice between split and narrow" gap.

## Degenerate-success guard (required)

- **Too-clean candidate:** `BOTH_A = 20/20` AND `flip_cost_A = 0.000`.
- **Causal vs correlate distinction (codex review finding, addressed
  inline):** "THRESHOLD_SLOT token present on tape" is a correlate, NOT
  evidence of slot-indirection. The mechanism claim requires
  THRESHOLD_SLOT to be the **causal task-distinguisher**. Three failure
  modes can produce token-present winners that are NOT slot-indirection:
  1. **Parallel per-task bodies.** Tape contains both
     `INPUT SUM CONST_5 GT` and `INPUT SUM CONST_10 GT` as separate
     programs; BOTH solve without slot binding being the cause.
  2. **Token-as-passive-junk.** Tape contains THRESHOLD_SLOT in a
     no-effect position (e.g., after a non-consuming branch); the
     active body bypasses it entirely.
  3. **Body-irrelevant attractor.** A constant-output or input-
     invariant program that scores ≥ 0.999 on the seed × n_examples
     slice by coincidence. Holdout gap is the diagnostic; principle 21
     attractor classification confirms.
- **The causal test (post-hoc, per BOTH-solver):** the winner satisfies
  slot-indirection iff (a) the canonical body
  `INPUT SUM THRESHOLD_SLOT GT` is the active execution path on BOTH
  tasks (not bypassed), AND (b) the SAME body executes on both threshold
  values (the only differing bit is what THRESHOLD_SLOT pushes), AND
  (c) replacing THRESHOLD_SLOT with the wrong task's threshold would
  break the winner on the wrong task (a counterfactual test that can be
  computed by re-evaluating the winner with `task.alphabet.threshold`
  swapped).
- **How to detect (inspection commitment — applies to ALL 60 winners,
  not just BOTH-solvers, per principle 21):**
  1. Run `decode_winner.py v2_11_arm_A_{alt,fixed} --all` on **every
     winner** (60 winners total: 20 alt + 20 F_5 + 20 F_10).
  2. For each winner, classify into one of:
     - `causal-slot-indirection` — passes the causal test (a)+(b)+(c)
       above
     - `parallel-per-task-bodies` — both tasks solved but via separate
       sub-programs on the tape (slot not causally used)
     - `token-as-passive-junk` — THRESHOLD_SLOT present but execution
       bypasses it
     - `body-irrelevant-attractor` — solve attributable to a
       coincidental-match program
     - `unclassified` — classifier cannot resolve
  3. Compute `attractor_PASS_share = causal-slot-indirection / BOTH_A`.
     This is the load-bearing metric for the PASS-decoder-robust row.
  4. Solved-seed overlap with §v2.3 BP_TOPK on shared seeds 0..19. If
     Arm A solves a strictly-different seed set than BP_TOPK, the
     decoders are exploring partially-disjoint solution sets on this
     body — additional evidence weighing toward PASS-partial even at
     matched aggregate counts.

**Inspection-tooling deferral note (codex finding [P1] addressed via
explicit deferral):** The current `decode_winner.py:76` admits the
extracted program is a "permeable-all view" superset, NOT the actual
BP_TOPK extraction; under Arm A this is less of a problem because the
tape IS the program (no permeability), but the **causal-slot-indirection
classifier** described above (counterfactual test (c)) is not yet
implemented in `decode_winner.py`. Implementing it is a separate
infrastructure item (§v2.X-classifier-extension, not yet pre-registered).
Until it lands, the per-winner classification will be **manual** on the
~60 winners produced by this sweep — feasible at this n but not at scale.
Estimated classification time: ~20-30 min for 60 winners. Recorded as
deferred infrastructure cost.

## Statistical test

- **Primary:** paired McNemar on BOTH-solve, Arm A vs BP_TOPK, on shared
  seeds 0..19. Two-sided exact binomial on disagreement counts (b, c).
  One-sided α=0.05 for the directional test "Arm A < BP_TOPK" reported
  alongside.
- **Secondary:** per-task two-sided McNemar on F_5 and F_10. Descriptive
  only at this n; reported with raw (b, c) counts.
- **Note on pairing strength (codex finding [P2] addressed inline):**
  this experiment changes only `arm`, so the population-init RNG seed
  is the same across conditions. **However**, that does NOT mean the
  evolutionary trajectories are RNG-path-preserved: as soon as fitness
  evaluation differs (which it does, decoder-specific), tournament
  selection picks different individuals and downstream RNG consumption
  diverges. The pairing is **seed-matched**, not RNG-trajectory-matched.
  This is sufficient for valid McNemar pairing (matched experimental
  units) but does not justify any stronger causal-isolation claim.
  Earlier draft language suggesting "pairing is genuinely matched" in
  the strong sense is corrected to "seed-matched."

## Diagnostics to log (beyond fitness)

- `BOTH_A`, `F_5_A`, `F_10_A` raw counts.
- Per-seed best-of-run final fitness on each task (not just solve/no).
- Mean and max train−holdout gap across all 60 runs (overfit audit, per
  §v2.3 protocol).
- Mean and max post-flip fitness drop on alternation; full distribution.
- Flip-event count and zero-cost flip count (§v2.3's signature was 399/400
  zero-cost across all four blocks; matched-seed comparison here is
  100/100 vs whatever Arm A produces).
- `decode_winner.py` output on all BOTH-solvers (per Gate 4 above).
- Solved-seed overlap with §v2.3 BP_TOPK seed block.
- ADI per condition (component-presence vs solve mismatch). Under Arm A,
  ADI is computed differently — the tape IS the program, so component
  presence on tape implies execution. ADI = 0 is the expected null;
  ADI ≠ 0 would be an interpretation puzzle worth recording.

## Scope tag (required for any summary-level claim)

**If PASS-decoder-robust, the claim narrows the existing findings.md
caveat with this scope tag:**

`within-family · n=20 on shared seed block · at pop=1024 gens=1500 ·
on body INPUT SUM THRESHOLD_SLOT GT thresholds {5, 10} over [0,9] ·
across decoder arms {Arm A, BP_TOPK(k=3, bp=0.5)}`

Explicitly **NOT** claiming on PASS:
- Decoder-independence on bodies other than this one (Pair 1's failure
  under BP_TOPK and partial rescue under Arm A is a separate finding;
  this experiment does not extend or contradict it).
- Decoder-independence at body lengths other than 4 tokens.
- Decoder-independence under decorrelated input distributions (§v2.4-proxy
  not in scope).
- Decoder-independence at decoder parameters other than BP_TOPK(k=3,
  bp=0.5) — k=5 sweep is §v2.13.

## Decision rule

- **PASS-decoder-robust →** rewrite the decoder-arm caveat in
  `findings.md#constant-slot-indirection` to scope decoder-dependence to
  Pair-1's body only. No new findings entry; this is a caveat-narrowing
  pass via supersession-mode, not a claim promotion. Update the
  "Decoder-arm dependence caveat" subsection with this experiment as
  the disambiguation.
- **PASS-partial →** add a "decoder-efficiency dependence on §v2.3's
  body" line to `findings.md#constant-slot-indirection` Scope boundaries.
  Do NOT narrow the headline scope tag (still "one pair, BP_TOPK at
  precision"); the partial Arm A result complicates the picture without
  retracting the headline.
- **INCONCLUSIVE →** queue `§v2.11-scale` (Arm A at 4× compute on the
  same pair, prereg required). No findings change in this pass.
- **FAIL — mechanism is decoder-specific →** trigger supersession-mode
  on `findings.md#constant-slot-indirection`. The current claim sentence
  (which is decoder-agnostic in its surface form) must be either:
  (a) split into two decoder-specific claims, or
  (b) further narrowed to "under BP_TOPK(k=3, bp=0.5) on this body."
  The choice between (a) and (b) depends on whether Arm A produces a
  *different* mechanism (parallel per-task bodies, per Gate 4 inspection)
  or merely fails to find any mechanism. Decoder-arm becomes an
  explicit scope-tag dimension going forward.

---

*Audit trail.* Four pre-registered outcome rows including a partial row
(principle 2). Thresholds anchored to §v2.3's measured BP_TOPK baseline
on the matched seed block, not absolute or imported numbers (principle 6).
Tightest within-family decoder-arm internal control IS this experiment
(principle 1). Degenerate-success candidates enumerated with per-mechanism
detection commitments before running (principle 4 + 21). Sampler-design
audit not triggered, explicitly stated (principle 20). Decision rule
includes a supersession-mode trigger for FAIL outcome (principle 13).
