# Pre-registration: §v2.12 — Arm A direct GP on §v2.4 and §v2.4-proxy AND tasks

**Status:** DONE · FAIL (decoder-general) · run commit `29c524e` · chronicle commit `1cfe7d5` · 2026-04-16

Derived from [`docs/chem-tape/findings.md#proxy-basin-attractor`](../docs/chem-tape/findings.md)
(`ACTIVE` · scope-tagged "Tested only at BP_TOPK(k=3, bp=0.5); other arms
not characterised") and from the Arm-A-as-developmental-bias framing
emerging from the §v2.6-pair1 follow-up sweeps.

## Question (one sentence)

Is `findings.md#proxy-basin-attractor` (single-predicate proxy basins
dominate greedy search under BP_TOPK whenever a ≥ ~0.90-accurate
single-predicate exists) **decoder-specific to BP_TOPK**, or is it a
**general property of greedy search** under any chem-tape decoder?

## Hypothesis

The current scope tag explicitly flags this as untested. Two competing readings:

1. **BP_TOPK-specific.** BP_TOPK's permeability allows short proxy programs
   (e.g., `INPUT REDUCE_MAX CONST_5 GT` for `max > 5`) to occupy a basin
   in tape-space whose extracted-program is highly preserved under
   surrounding-token mutation. Under Arm A direct GP (no decoder
   permeability), the same tape positions code different programs; the
   proxy basin should be **less stable** because its tape-neighbors no
   longer extract to the same proxy. Predicted: F_AND_A_natural ≥ 10/20,
   F_AND_A_decorr ≥ 10/20.

2. **Decoder-general.** Proxy-basin dominance is a property of greedy
   single-objective fitness with a near-perfect cheap proxy; the decoder
   is incidental. Under Arm A, evolution still finds the cheap program
   first because it has higher fitness gradient than the compositional
   AND; whether that program is reached via tape-extraction or direct
   token execution is irrelevant. Predicted: F_AND_A_natural ≤ 3/20,
   F_AND_A_decorr ≤ 5/20 (both roughly matching BP_TOPK baselines).

The two readings produce **clearly distinct** predictions but the
experiment is **not strictly decisive**: it admits middle outcomes
(asymmetric lift, modest lift, different-attractor) which the outcome
table below treats as their own rows, not as a forced binary. (Codex
[P1] finding addressed inline: earlier "decisive" language overclaimed
given that PASS-partial, INCONCLUSIVE, and "different-proxy" rows are
all pre-accepted possibilities.) A clean PASS or FAIL would distinguish
the two readings; intermediate outcomes refine the basin's
decoder-dependence story without resolving it cleanly.

## Setup

- **Sweep files:**
  - `experiments/chem_tape/sweeps/v2/v2_12_arm_A_v2_4_natural.yaml` —
    `sum_gt_10_AND_max_gt_5` under Arm A, natural sampler ([0,9] intlists).
  - `experiments/chem_tape/sweeps/v2/v2_12_arm_A_v2_4_decorr.yaml` —
    `sum_gt_10_AND_max_gt_5_decorr` under Arm A, 3-way stratified
    decorrelated sampler (matched verbatim to §v2.4-proxy's task builder).
- **Tasks:** `sum_gt_10_AND_max_gt_5` (existing), `sum_gt_10_AND_max_gt_5_decorr`
  (existing, builder added at commit `0230662`).
- **Alphabet:** `v2_probe`.
- **Intervention:** `arm: A` (only change vs §v2.4 / §v2.4-proxy baselines).
- **Fixed params (matched verbatim to §v2.4 prereg block):**
  `tape_length=32`, `n_examples=64`, `holdout_size=256`, `pop_size=1024`,
  `generations=1500`, `tournament_size=3`, `elite_count=2`, `mutation_rate=0.03`,
  `crossover_rate=0.7`. Both sub-sweeps are fixed-task (no alternation).
- **Seeds:** `0..19` per sub-sweep — matched to §v2.4 / §v2.4-proxy.
- **Est. compute:** ~12 min at 10 workers (40 runs total: 20 × 2).
- **Related experiments:**
  [§v2.4 baseline](../docs/chem-tape/experiments-v2.md) ·
  [§v2.4 follow-up at 4× compute](../docs/chem-tape/experiments-v2.md) ·
  [§v2.4-alt body-matched compositional pair](../docs/chem-tape/experiments-v2.md#v24-alt) ·
  [§v2.4-proxy decorrelation sweep](../docs/chem-tape/experiments-v2.md#v24-proxy).

## Baseline measurement (required)

- **Baseline quantity:** §v2.4 and §v2.4-proxy BP_TOPK results at the same
  task definitions, same seeds, same compute.
- **Measurement:** previously recorded.
  - §v2.4 baseline at commit `e3d7e8a` (natural sampler):
    `F_AND_BP_natural = 0/20` · 14/20 winners converge to `max > 5` exactly
    · mean train ≈ 0.921, mean holdout ≈ 0.909.
  - §v2.4 4× compute follow-up at commit `f806d04`:
    `F_AND_BP_natural_4x = 0/20` (no rescue at scaled compute).
  - §v2.4-proxy at commit `0230662` (decorrelated sampler):
    `F_AND_BP_decorr = 3/20` · 11/17 non-solvers shifted to `sum > 10`
    attractor (next-best single-predicate at 0.91 accuracy).
- **Threshold calibration (principle 6):** outcome rows below are
  expressed as deltas from these BP_TOPK measurements. The 4× compute
  follow-up establishes that **compute scaling does not rescue this
  failure mode under BP_TOPK** — the present experiment's lift, if any,
  is therefore decoder-attributable, not budget-attributable.

## Internal-control check (required)

- **Tightest internal contrast:** §v2.4 (natural) and §v2.4-proxy
  (decorrelated) themselves. Both are fixed-task BP_TOPK runs at matched
  compute on the exact tasks this sweep tests. Decoder is the only
  varied axis.
- **Are you running it here?** Yes. The two sub-sweeps form the within-family
  decoder-arm internal control across two sampler conditions
  (per principle 1 + 9 — sampler and decoder are non-additive axes that
  must be crossed before claiming generality).

## Sampler-design audit (principle 20)

**TRIGGERED. Re-measurement at this commit is REQUIRED — inheritance
is insufficient (codex [P1] finding addressed inline).** The §v2.4 and
§v2.4-proxy task builders may have evolved between commits `e3d7e8a` /
`0230662` and the current `75ab827`. Principle 20 requires "representative
seeds, plural" — seed=0 alone is not adequate. Required pre-sweep audit
on **seeds {0, 1, 2}** at this commit, before either sub-sweep runs:

For both samplers (`sum_gt_10_AND_max_gt_5` and
`sum_gt_10_AND_max_gt_5_decorr`), on each of seeds {0, 1, 2}, n_train=64:
- (i) class balance: positives / total. **Required: 0.40 ≤ ratio ≤ 0.60**
  on every audited seed.
- (ii) proxy accuracies for: `constant-1`, `max > 5`, `max > 7`,
  `sum > 10`, `sum > 15`, `any cell > 6`, `any cell > 7`.
  **Required: max proxy accuracy on natural sampler ≥ 0.85 on each
  seed (sanity that the §v2.4 max>5 attractor signature still holds);
  max proxy on decorrelated sampler ≤ 0.93 (sanity that decorrelation
  still works as designed).** Significant drift (max-proxy on
  natural < 0.85, or max-proxy on decorrelated > 0.93) means task
  builders have changed semantics; HALT and investigate.
- (iii) label viability: positives ≥ 5 per task per seed.

**Reference values (from prior preregs, for sanity comparison only):**
- §v2.4 natural sampler at commit `e3d7e8a`, seed=0: positives=32/64,
  `max > 5` accuracy = 0.92.
- §v2.4-proxy decorrelated sampler at commit `0230662`, seed=0:
  positives=32/64, `max > 5` accuracy = 0.750, `sum > 10` accuracy = 0.906.

Audit numbers must be **measured at commit `75ab827` and reported in
the chronicle** before main-sweep results are interpreted. If audit
fails any required check, HALT and re-prereg.

## Pre-registered outcomes (required — at least three)

Definitions:
- `F_AND_A_natural = ` Arm A solve count on `sum_gt_10_AND_max_gt_5`
  at fitness ≥ 0.999.
- `F_AND_A_decorr = ` Arm A solve count on `sum_gt_10_AND_max_gt_5_decorr`
  at fitness ≥ 0.999.
- `Δ_natural = F_AND_A_natural − 0` (BP_TOPK natural baseline).
- `Δ_decorr = F_AND_A_decorr − 3` (BP_TOPK decorrelated baseline).

Row precedence: top-to-bottom (first-matching wins). Inspection-derived
metrics (`attractor_share_natural`, `attractor_share_decorr`) are
computed per Gate 4 below and apply to ALL rows, not just extremes
(codex [P2] finding addressed inline).

| outcome | criterion | interpretation |
|---|---|---|
| **PASS — proxy-basin is BP_TOPK-specific** | `F_AND_A_natural ≥ 10/20` AND `F_AND_A_decorr ≥ 10/20` AND `attractor_share_natural < 0.25` AND `attractor_share_decorr < 0.25` | Proxy basin mediated by BP_TOPK's tape-extraction. Under Arm A direct execution, basin loses grip. Update `findings.md#proxy-basin-attractor` **scope tag** (claim condition: "under BP_TOPK") — the mechanism *name* `single-predicate proxy basin attractor` is already decoder-agnostic; this is a scope rewrite, not a rename (codex [P2] correction). |
| **PASS — partial (asymmetric)** | Exactly one of: (`F_AND_A_natural ≥ 10/20` AND `F_AND_A_decorr ≤ 5/20`), or (`F_AND_A_natural ≤ 3/20` AND `F_AND_A_decorr ≥ 10/20`) | Decoder × sampler interaction; basin decoder-dependence depends on which proxy is at play. Asymmetry direction is informative. Add asymmetric scope-boundary bullet to findings entry. |
| **INCONCLUSIVE — different-attractor PASS** (codex [P1] missing-row addressed) | (`F_AND_A_natural ≥ 10/20` OR `F_AND_A_decorr ≥ 10/20`) AND attractor inspection shows the solvers reached AND via a **DIFFERENT** mechanism than canonical IF_GT-CONST_0-prefix template AND not via BP_TOPK's known proxies | High solve count but mechanism-uncertain. Arm A finds AND but via a route that is neither the §v2.4 proxy basin nor the canonical compositional template. This is mechanism-divergence, not basin-escape. **No findings change.** Report as a new mechanism observation; queue inspection deeper before any claim. |
| **INCONCLUSIVE — small lifts** | `Δ_natural ∈ [3, 9]` OR `Δ_decorr ∈ [3, 9]` AND no clear attractor-shift pattern | Decoder is a small lever; basin reading still applies broadly. No scope change. Queue Arm A at 4× compute as §v2.12-scale only if user prioritises the data. |
| **FAIL — proxy-basin is decoder-general** | `F_AND_A_natural ≤ 3/20` AND `F_AND_A_decorr ≤ 5/20` AND `attractor_share_natural ≥ 0.50` AND `attractor_share_decorr ≥ 0.50` | Basin operates under Arm A as well. Decoder permeability is incidental; greedy fitness with cheap proxy is sufficient. `findings.md#proxy-basin-attractor` **scope BROADENS** (16b) — caveat "Tested only at BP_TOPK" updates to "Tested at BP_TOPK and Arm A; both trap." Claim sentence does NOT change (already decoder-general in form); **scope tag** updates. |

Notes on row construction:
- The PASS row requires both numerical lift AND attractor inspection
  evidence (Gate 4). A lift without inspection could be Arm A finding a
  *different* attractor — that would not be PASS-decoder-specific, it
  would be a confounded mechanism change.
- The 10/20 threshold for "PASS" mirrors §v2.4-alt's threshold=5 result
  (17/20 when no proxy exists), which sets the upper end of "compositional
  body is reachable when no proxy traps." 10/20 is roughly half of that
  upper bound, accounting for Arm A's expected efficiency loss vs
  BP_TOPK on shorter bodies.
- The PASS-partial rows are asymmetric on purpose: under decorrelated
  sampler the secondary proxy `sum > 10` (0.91 acc) is the basin, while
  under natural sampler the primary proxy `max > 5` (0.92 acc) is the
  basin. The two basins may have different decoder-dependence.

## Degenerate-success guard (required)

- **Too-clean candidate (PASS direction):** `F_AND_A_natural ≥ 18/20` and
  `F_AND_A_decorr ≥ 18/20` — clean rescue across both samplers.
- **Candidate degenerate mechanisms:**
  1. **Arm A finds a different proxy that scores ≥ 0.999 on training
     by coincidence** (not the AND, but a 4-token program that scores
     perfectly on this specific seed × n_examples slice). The §v2.4
     mechanism inspection found this on §v2.4-alt — seed 2 found a
     "non-canonical compositional route" that reached AND via an
     alternative decode. Under Arm A this would look like rescue but
     mechanistically be "single-seed alt-route luck."
  2. **Arm A solves AND directly via a high-fitness compositional body
     that BP_TOPK was missing because of decoder-specific epistasis.**
     Genuine PASS, but distinguishing it from (1) requires inspection.
- **Too-clean candidate (FAIL direction):** identical attractor breakdown
  to BP_TOPK (14/20 max>5 on natural; 11/17 sum>10 on decorr). Would
  imply Arm A and BP_TOPK explore the same fitness landscape on this
  task family — a strong claim that itself deserves verification (could
  be coincidence at n=20).
- **How to detect (inspection commitment, all required before verdict):**
  1. Run `decode_winner.py v2_12_arm_A_v2_4_natural --all` and
     `decode_winner.py v2_12_arm_A_v2_4_decorr --all` on every solver and
     non-solver winner.
  2. Classify each winner into one of: `max > 5` exact, `max > c` other,
     `sum > 10` exact, `sum > c` other, `genuine AND-composition`,
     `compositional but broken`, `other`.
  3. Report the per-sub-sweep attractor breakdown (X/20 in each category)
     and compare to §v2.4 / §v2.4-proxy BP_TOPK breakdowns
     (14/20 max>5 / 6/20 AND-partial; 2/17 max>5 / 11/17 sum>10 / 3/20 AND).
  4. For any seed classified as `genuine AND-composition`, inspect whether
     the body matches the canonical IF_GT / CONST_0 prefix template
     (§v2.4-alt) or is an alternative compositional route (§v2.4-alt seed 2).
     Report counts.
  5. Solved-seed overlap with §v2.4 / §v2.4-proxy BP_TOPK winners on
     shared seeds 0..19. Disjoint solve sets are evidence against
     "decoder-incidental" reading even if aggregate counts match.

## Statistical test

- **Per sub-sweep:** paired McNemar on F_AND solve, Arm A vs BP_TOPK,
  shared seeds 0..19. Two-sided exact binomial on (b, c). One-sided
  α=0.05 for "Arm A > BP_TOPK" (the directional escape hypothesis).
- **Across sub-sweeps:** descriptive only (two data points; no across-sweep
  meta-test). The asymmetry diagnosis (PASS-partial row) is qualitative.
- **Pairing strength:** Arm A vs BP_TOPK at matched config does NOT
  perturb the population-init RNG path (same as §v2.11 comment); the
  pairing is genuinely matched.

## Diagnostics to log (beyond fitness)

- `F_AND_A_natural`, `F_AND_A_decorr` raw counts at thresholds 0.999
  AND 0.95 (mirror §v2.4 reporting).
- Per-seed best-of-run final fitness on each task.
- Mean and max train−holdout gap (overfit audit per §v2.4 protocol).
- Attractor breakdown per sub-sweep (per Gate 4 above).
- Solved-seed overlap with BP_TOPK baselines per sub-sweep.
- Single-predicate proxy accuracies on the actual seed=0 sample of each
  sweep (sanity confirmation that sampler is operating as intended;
  recompute, do not trust stored values).
- For every BOTH-non-solver: extracted predicate accuracy on training
  (e.g., "0.92 ≈ max > 5 attractor"). This was the load-bearing diagnostic
  in §v2.4-proxy.

## Scope tag (required for any summary-level claim)

**If PASS-decoder-specific, the existing `findings.md#proxy-basin-attractor`
claim sentence rewrites with this scope tag:**

`within-family / cross-axis on AND-composition · n=20 per sub-sweep ·
at pop=1024 gens=1500 BP_TOPK(k=3, bp=0.5) v2_probe alphabet ·
on integer-list AND-composition labels of the form (sum > t1) AND (max > t2) ·
under BP_TOPK greedy search (decoder-specific; Arm A escapes)`

**If PASS-partial (asymmetric), the scope tag refines to:**

`...under BP_TOPK greedy search; decoder-dependence varies by sampler:
{natural / decorrelated} basin escapes under Arm A, {decorrelated / natural}
does not.`

**If FAIL-decoder-general, the scope tag BROADENS:**

`...under greedy search at this budget (decoder-general: BP_TOPK and
Arm A both trap)`

Explicitly **NOT** claiming on any outcome:
- Generalisation to OR / XOR / k-way compositions (out of scope; queued).
- Generalisation to non-AND label families.
- Generalisation to other input-list sizes / ranges than length-4 over [0,9].

## Decision rule

- **PASS — decoder-specific →** trigger supersession-mode pass on
  `findings.md#proxy-basin-attractor`. Rewrite the claim sentence with
  the "under BP_TOPK greedy search" qualifier and add Arm A escape as
  Narrowing/falsifying experiment row. Mechanism rename check: name
  should reference decoder.
- **PASS — partial (asymmetric) →** add an asymmetric scope-boundary
  bullet to `findings.md#proxy-basin-attractor`. Do NOT rewrite the
  claim sentence. Queue follow-up `§v2.12-asymmetry` to characterize
  which proxy depends on decoder.
- **INCONCLUSIVE →** report as-is; no findings change. Decoder is a
  small lever on this attractor, but the basin reading still applies
  broadly. Note that a 4× compute Arm A run is the natural follow-up
  but not auto-queued.
- **FAIL — decoder-general →** principle 16b broadening pass on
  `findings.md#proxy-basin-attractor`. The current "Tested only at
  BP_TOPK" caveat broadens to "Tested at BP_TOPK and Arm A; both trap."
  Mechanism name should NOT reference decoder; the basin is a property
  of greedy fitness search with cheap proxies, period.

---

*Audit trail.* Four pre-registered outcome rows including PASS-partial
and INCONCLUSIVE (principle 2). Thresholds anchored to §v2.4 / §v2.4-proxy
measured BP_TOPK baselines on matched seed block (principle 6). Internal
control isolates decoder-arm across two sampler conditions (principle 1).
Sampler-design audit discharged by inheritance with all numbers restated
explicitly (principle 20). Degenerate-success candidates enumerated with
inspection commitments before running (principle 4 + 21). Decision rule
includes both narrowing (PASS) and broadening (FAIL) supersession triggers
(principle 13 + 16b). Both Arm A vs BP_TOPK comparisons preserve seed
RNG path; pairing is matched (principle 7).
