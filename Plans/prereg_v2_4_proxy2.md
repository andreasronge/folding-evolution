# Pre-registration: §v2.4-proxy-2 — Simultaneous dual-proxy decorrelation on AND-composition

**Status:** DONE · FAIL (proxy cascade) · run commit `92b3325` · chronicle commit `92b3325` · 2026-04-16

Derived from [`docs/chem-tape/findings.md#proxy-basin-attractor`](../docs/chem-tape/findings.md)
(now `ACTIVE · decoder-general`) and from §v2.4-proxy's open question
(experiments-v2.md §v2.4-proxy caveats): "under simultaneous decorrelation
of max>5 and sum>10, does the `any cell > 6` attractor (0.844 accuracy
under the current distribution) take over?"

## Question (one sentence)

When the top-2 single-predicate proxies (`max > 5` at ~0.92 and `sum > 10`
at ~0.91) are simultaneously decorrelated to ≤0.75 in the training
distribution, does evolution (a) shift to a third-best proxy, (b) find
genuine AND-composition, or (c) collapse — and is the outcome
decoder-general (tested across BP_TOPK and Arm A)?

## Hypothesis

Three competing readings:

1. **Proxy cascade — third proxy takes over.** Even with max>5 and sum>10
   weakened, `sum > 15` (~0.89 accuracy under dual-decorr sampler) or
   `any cell > 7` (~0.81) becomes the new attractor. The basin story
   generalises fully: *any* cheap single-predicate dominates.
   Predicted: F_AND ≤ 5/20 on both decoders; attractor inspection shows
   a dominant third-predicate attractor.

2. **AND-composition freed.** Removing both ≥0.90 proxies opens enough
   fitness-landscape gradient for the compositional body to win.
   Predicted: F_AND ≥ 12/20 on at least one decoder; attractor inspection
   shows genuine AND-composition (IF_GT + CONST_0 prefix template).

3. **Collapse — sampler destroys learnability.** The dual-decorrelation
   sampler is too aggressive; removing neg_lo_lo (max≤5 AND sum≤10)
   examples from training makes the AND boundary less discoverable.
   Predicted: F_AND ≤ 2/20 AND mean best fitness < 0.85 (fitness
   landscape is flatter, not just proxy-trapped).

The §v2.4-proxy result (3/20 under single decorrelation) weights the prior
toward (1) given that `sum > 10` at 0.91 remained as a ready-made attractor.
Whether a third-tier proxy at ~0.85 is sufficient to trap evolution is the
open question.

## Setup

- **Sweep files:** (to be created)
  - `experiments/chem_tape/sweeps/v2/v2_4_proxy2_bp_topk.yaml` — BP_TOPK(k=3, bp=0.5) on `sum_gt_10_AND_max_gt_5_dual_decorr`.
  - `experiments/chem_tape/sweeps/v2/v2_4_proxy2_arm_a.yaml` — Arm A on the same task.
- **Tasks:** `sum_gt_10_AND_max_gt_5_dual_decorr` (new task builder required — see Sampler design below).
- **Alphabet:** `v2_probe`.
- **Arms / conditions:** `BP_TOPK(k=3, bp=0.5)` and `Arm A`. Both at matched compute.
- **Fixed params (matched to §v2.4 / §v2.12):**
  `tape_length=32`, `n_examples=64`, `holdout_size=256`, `pop_size=1024`,
  `generations=1500`, `tournament_size=3`, `elite_count=2`, `mutation_rate=0.03`,
  `crossover_rate=0.7`. Fixed-task (no alternation).
- **Seeds:** `0..19` per arm — matched to §v2.4 / §v2.12 baselines.
- **Est. compute:** ~12 min at 10 workers (40 runs: 2 arms × 20 seeds).
- **Related experiments:**
  [§v2.4 baseline](../docs/chem-tape/experiments-v2.md) ·
  [§v2.4-proxy](../docs/chem-tape/experiments-v2.md#v24-proxy) ·
  [§v2.12](../docs/chem-tape/experiments-v2.md#v212-arm-a-direct-gp-on-v24-proxy-basin-tasks-2026-04-16).

## Baseline measurement (required)

- **Baseline quantities:** §v2.4, §v2.4-proxy, and §v2.12 results at the
  same task family under natural and single-decorr samplers.
- **Measurement:** previously recorded.
  - §v2.4 BP_TOPK natural: F_AND = 0/20, attractor 14/20 max>5.
  - §v2.4-proxy BP_TOPK single-decorr: F_AND = 3/20, attractor 11/17 sum>10.
  - §v2.12 Arm A natural: F_AND = 0/20, attractor_share = 0.80.
  - §v2.12 Arm A single-decorr: F_AND = 1/20, attractor_share = 0.84.
- **Threshold calibration (principle 6):** outcome rows are expressed
  relative to these baselines. The §v2.4-proxy's 3/20 under single-decorr
  is the strongest existing signal; dual-decorr should either match, lift,
  or drop relative to that.

## Internal-control check (required)

- **Tightest internal contrast:** §v2.4-proxy (single decorr) on the same
  seeds, same arm, same compute. Only the sampler changes. The BP_TOPK vs
  Arm A contrast within this experiment provides the decoder-generality
  check (per §v2.12's FAIL result).
- **Are you running it here?** Yes — two arms on the same dual-decorr task.

## Sampler-design audit (principle 20)

**TRIGGERED.** This experiment introduces a new training distribution.

### Sampler design: dual-decorrelation (50/50 balanced, 2-cohort negatives)

Label: `sum > 10 AND max > 5` (same as §v2.4).

Negative cohorts (no neg_lo_lo):
- **neg_hi_lo:** `sum > 10 AND max ≤ 5` (has sum>10 but not max>5)
- **neg_lo_hi:** `sum ≤ 10 AND max > 5` (has max>5 but not sum>10)

Proportions per n_train=64:
- 32 positives (sum>10 AND max>5)
- 16 neg_hi_lo
- 16 neg_lo_hi

This gives:
- P(max>5 | neg) = 16/32 = 0.50 → `max > 5` predictor accuracy = 0.75
- P(sum>10 | neg) = 16/32 = 0.50 → `sum > 10` predictor accuracy = 0.75

### Required pre-sweep measurements (seeds {0, 1, 2})

**(i) Class balance:** positives ÷ total.
- Seed 0: 0.500 ✓
- Seed 1: 0.500 ✓
- Seed 2: 0.500 ✓

**(ii) Proxy accuracies (measured at commit `3e19e0f`):**

| proxy | seed 0 | seed 1 | seed 2 |
|-------|--------|--------|--------|
| max > 5 | 0.750 | 0.750 | 0.750 |
| sum > 10 | 0.750 | 0.750 | 0.750 |
| any cell > 6 | 0.844 | 0.812 | 0.812 |
| any cell > 7 | 0.859 | 0.891 | 0.750 |
| sum > 15 | 0.906 | 0.891 | 0.828 |
| max > 7 | 0.859 | 0.891 | 0.750 |
| constant-1 | 0.500 | 0.500 | 0.500 |

**Key observation: `sum > 15` is the new dominant proxy at 0.83-0.91.**
The dual-decorrelation weakens the top-2 proxies to 0.75 but leaves
third-tier proxies at 0.81-0.91. This is by design — the experiment
tests whether a ~0.85-accuracy proxy is sufficient to trap evolution,
not whether all proxies can be eliminated.

**(iii) Label viability:** positives ≥ 5 per seed.
- All seeds: 32/64 positives ✓

**Audit PASSES** all three checks. Required: class balance 0.40-0.60 (met
at 0.50), max proxy on dual-decorr ≥ 0.75 (met — confirms decorrelation
worked), label viability (met at 32 positives). No HALT condition.

## Pre-registered outcomes (required — at least three)

Definitions:
- `F_AND_BP` = BP_TOPK solve count at fitness ≥ 0.999.
- `F_AND_A` = Arm A solve count at fitness ≥ 0.999.
- `attractor_3rd` = fraction of non-solvers whose winner converges to a
  third-tier single-predicate (sum>15, any_cell>7, max>7, any_cell>6).
- `attractor_AND` = fraction of solvers with genuine AND-composition body
  (IF_GT + CONST_0 prefix template, confirmed by decode_winner.py).

| outcome | criterion | interpretation |
|---|---|---|
| **PASS — AND-composition freed** | `F_AND_BP ≥ 10/20` OR `F_AND_A ≥ 10/20` AND `attractor_AND ≥ 0.70` (≥70% of solvers use genuine AND) | Removing both ≥0.90 proxies opens the AND pathway. The proxy-basin claim narrowrows to "requires ≥0.90 proxy accuracy to trap; ≤0.85 is insufficient." |
| **PASS — partial (small lift)** | `F_AND_BP ∈ [4, 9]` OR `F_AND_A ∈ [4, 9]` AND at least one arm shows `F_AND > F_AND_single_decorr_baseline` (i.e., >3 for BP_TOPK, >1 for Arm A) | Weakening both proxies helps but doesn't fully free AND. The ~0.85 proxy is weaker but still partially trapping. |
| **FAIL — proxy cascade (third proxy traps)** | `F_AND_BP ≤ 3/20` AND `F_AND_A ≤ 3/20` AND `attractor_3rd ≥ 0.50` | Evolution shifts to the next-best proxy. The "any cheap proxy" reading strengthens. proxy-basin claim **broadens** to "any single-predicate ≥ ~0.85 accuracy traps." |
| **FAIL — collapse (sampler too aggressive)** | `F_AND_BP ≤ 2/20` AND `F_AND_A ≤ 2/20` AND mean best fitness < 0.85 AND `attractor_3rd < 0.30` | The dual-decorrelation sampler destroys learnability. No clear attractor; fitness landscape is flat. Report as sampler-design failure, not mechanism evidence. |
| **INCONCLUSIVE — decoder-divergent** | One arm ≥ 10/20 AND other ≤ 3/20 | Proxy-basin trapping is decoder-dependent under dual-decorr but not under natural/single-decorr. Would narrow the "decoder-general" reading from §v2.12. |

## Degenerate-success guard (required)

- **Too-clean candidate (PASS direction):** `F_AND ≥ 18/20` on both arms —
  near-perfect rescue across both decoders.
- **Candidate degenerate mechanisms:**
  1. **Solver uses `sum > 15` or another proxy that happens to be
     ≥0.999-accurate on this specific seed × n_examples slice.** Holdout
     gap is the diagnostic.
  2. **Solver uses an alternative composition route** (not the canonical
     IF_GT+CONST_0 prefix). Genuine PASS but different mechanism than
     expected. decode_winner.py required.
- **Too-clean candidate (FAIL direction):** identical attractor breakdown
  to single-decorr (11/17 sum>10 under BP_TOPK). Would suggest dual-decorr
  didn't actually change the landscape — possible if `sum > 10` accuracy
  didn't actually drop enough at n=64.
- **How to detect:** decode_winner.py on all 40 winners (20 per arm).
  Classify into: sum>15 attractor, any_cell>7 attractor, max>7 attractor,
  genuine AND, other. Report per-arm attractor breakdown.

## Statistical test

- **Per arm:** paired McNemar on F_AND, dual-decorr vs single-decorr
  baseline (§v2.4-proxy for BP_TOPK, §v2.12 decorr for Arm A), shared
  seeds 0..19. Two-sided α=0.05.
- **Across arms:** paired McNemar on F_AND, BP_TOPK vs Arm A on shared
  seeds 0..19. Two-sided α=0.05.
- **Pairing strength:** seed-matched, same task, same compute. Decoder is
  the only varied axis within each cross-arm comparison.

## Diagnostics to log (beyond fitness)

- `F_AND_BP`, `F_AND_A` at thresholds 0.999 and 0.95.
- Per-seed best-of-run final fitness.
- Mean and max train−holdout gap (overfit audit).
- Attractor breakdown per arm (decode_winner.py on all 40 winners).
- Solved-seed overlap: (a) BP_TOPK dual-decorr vs §v2.4-proxy single-decorr,
  (b) Arm A dual-decorr vs §v2.12 single-decorr, (c) BP_TOPK vs Arm A
  within this experiment.
- Per non-solver: dominant proxy classification and training accuracy of
  that proxy.
- Class balance verification on actual training data (per seed, confirms
  sampler is operating as designed).

## Scope tag (required for any summary-level claim)

**If PASS (AND freed):**

`within-family / cross-decoder on AND-composition · n=20 per arm ·
at pop=1024 gens=1500 v2_probe alphabet ·
across decoder arms {BP_TOPK(k=3,bp=0.5), Arm A} ·
on integer-list AND label (sum > 10) AND (max > 5) ·
under dual-decorrelation sampler (max>5 and sum>10 weakened to 0.75)`

**If FAIL (proxy cascade):**

`within-family / cross-decoder on AND-composition · n=20 per arm ·
proxy-basin threshold narrows to "any single-predicate ≥ ~0.85 traps" ·
under dual-decorrelation with third-tier proxy still available`

Explicitly NOT claiming on any outcome:
- Generalisation to non-AND compositions.
- Generalisation to samplers where ALL single-predicates are below 0.75
  (that would require a fundamentally different input distribution).
- That dual-decorrelation is the "correct" sampler for this task family —
  it's an experimental tool, not a recommended training practice.

## Decision rule

- **PASS — AND freed →** add a "proxy threshold ≥0.90 is the trapping
  condition; ≤0.85 is insufficient" scope-boundary bullet to
  `findings.md#proxy-basin-attractor`. This narrows the claim from "any
  cheap proxy" to "proxies above ~0.90 accuracy." Queue §v2.4-proxy-3
  (triple-decorrelation or fundamentally different input range) only if
  the user prioritises closing the proxy-accuracy-threshold question fully.
- **PASS — partial →** note as directional evidence toward a proxy-accuracy
  threshold. No findings change. Queue nothing automatically.
- **FAIL — proxy cascade →** trigger principle 16b broadening pass on
  `findings.md#proxy-basin-attractor`. The "≥ ~0.90" threshold in the
  claim sentence relaxes to "≥ ~0.85" (or whatever the dominant third-tier
  proxy accuracy is). This makes the basin story stronger and more general.
- **FAIL — collapse →** report as sampler-design failure. No findings
  change. Note that dual-decorrelation without neg_lo_lo examples may
  remove signal needed for AND discovery — a methodology lesson, not a
  mechanism finding.
- **INCONCLUSIVE — decoder-divergent →** queue inspection to understand
  which decoder exploits the weakened landscape. No findings change; the
  "decoder-general" reading from §v2.12 would need qualification.

---

*Audit trail.* Five pre-registered outcome rows including partial, collapse,
and decoder-divergent (principle 2). Thresholds anchored to §v2.4-proxy
and §v2.12 measured baselines (principle 6). Sampler-design audit discharged
with measured numbers on seeds {0, 1, 2} (principle 20). Internal control
is decoder-arm contrast within this experiment + comparison to single-decorr
baselines (principle 1). Degenerate-success candidates enumerated per
direction (principle 4 + 21). Decision rule includes both narrowing (PASS)
and broadening (FAIL) actions on findings.md (principle 13 + 16b).
