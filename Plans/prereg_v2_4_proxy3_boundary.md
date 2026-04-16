# Pre-registration: §v2.4-proxy-3 — Split-halves AND proxy-basin boundary sweep

**Status:** QUEUED · target commit `070def5` · 2026-04-16

Derived from the proxy-basin finding (`findings.md#proxy-basin-attractor`, now at
"≥~0.85 trapping threshold") and the structural insight that whole-list predicates
on [0,9]^4 always correlate with AND(sum>t1, max>t2). The split-halves design
uses independent input-halves to create AND tasks where no whole-list predicate
achieves ≥0.85 at the population level.

## Question (one sentence)

At what single-predicate proxy accuracy does the proxy-basin attractor stop
trapping greedy evolution: does the boundary lie near ~0.80 (where split-halves
AND escapes) or does trapping persist even at ~0.80, and is this
decoder-general?

## Hypothesis

The current claim says "≥ ~0.85 traps." Three possible refinements:

1. **Boundary is ~0.85.** Threshold >6 (best population proxy ~0.79) escapes;
   threshold >8 (best population proxy ~0.86) traps. The 0.85 boundary in the
   current claim is approximately correct.

2. **Boundary is lower (~0.80).** All three thresholds trap because per-seed
   variance at n=64 pushes proxy accuracy above the trapping floor on enough
   seeds. The "≥ ~0.85" claim needs to be relaxed further.

3. **Escape at all three.** The structural independence of left/right halves
   qualitatively changes the fitness landscape; even threshold >8 with a
   ~0.86 population proxy escapes. This would suggest the basin is not just
   about proxy accuracy but about the correlation structure.

## Setup

- **Sweep files:** 6 files: `v2_4_proxy3_gt{6,7,8}_{bp_topk,arm_a}.yaml`
- **Tasks:** `split_and_gt6`, `split_and_gt7`, `split_and_gt8` (new task
  builders using balanced [0,9]^4 with AND(sum_left2>t, sum_right2>t)).
- **Alphabet:** `v2_split` (extends v2_probe with SUM_LEFT2=22, SUM_RIGHT2=23).
- **Arms:** BP_TOPK(k=3, bp=0.5) and Arm A on each threshold.
- **Fixed params:** tape_length=32, n_examples=64, holdout_size=256,
  pop_size=1024, generations=1500, tournament_size=3, elite_count=2,
  mutation_rate=0.03, crossover_rate=0.7.
- **Seeds:** 0..19 per arm per threshold.
- **Est. compute:** ~30 min total at 10 workers (120 runs: 3 × 2 × 20).
- **Related experiments:** §v2.4, §v2.4-proxy, §v2.4-proxy-2, §v2.12.

## Baseline measurement (required)

- **Baseline:** §v2.4-proxy-2 (dual-decorr on correlated AND, same decoder arms):
  BP_TOPK 0/20, Arm A 1/20, best population proxy ~0.91 (sum>15).
- **Reference:** §v2.4-alt (threshold=5 body-matched pair, no high proxy):
  17/20 under BP_TOPK, proving AND-composition IS reachable when proxies are absent.
- **Threshold calibration (principle 6):** outcome rows are relative to these
  baselines. The §v2.4-alt 17/20 sets the "composition reachable" ceiling;
  the §v2.4-proxy-2 0-1/20 sets the "proxy-trapped" floor.

## Internal-control check (required)

- **Tightest internal contrast:** the three thresholds form a within-family
  gradient: >6 (proxy ~0.79), >7 (~0.81), >8 (~0.86). If the trapping
  threshold is in this range, at least one pair of adjacent thresholds
  should show a sharp transition.
- **Decoder contrast:** BP_TOPK vs Arm A within each threshold (per §v2.12
  decoder-generality).
- **Are you running it here?** Yes — the 3-threshold × 2-decoder grid IS
  the internal control.

## Sampler-design audit (principle 20)

**TRIGGERED.** New task family with new alphabet tokens and new label function.

### Pre-sweep measurements (seeds {0, 1, 2})

**split_and_gt6 (population proxy ~0.79):**
- seed 0: balance=0.500, best_proxy right>6=0.875, positives=32
- seed 1: balance=0.500, best_proxy left>6=0.906, positives=32
- seed 2: balance=0.500, best_proxy left>6=0.844, positives=32

**split_and_gt7 (population proxy ~0.81):**
- seed 0: balance=0.500, best_proxy sum_all>16=0.844, positives=32
- seed 1: balance=0.500, best_proxy left>7=0.938, positives=32
- seed 2: balance=0.500, best_proxy left>7=0.812, positives=32

**split_and_gt8 (population proxy ~0.86):**
- seed 0: balance=0.500, best_proxy sum_all>18=0.859, positives=32
- seed 1: balance=0.500, best_proxy left>8=0.906, positives=32
- seed 2: balance=0.500, best_proxy sum_all>18=0.828, positives=32

**Critical caveat (per-seed variance):** Population-level best proxies are
~0.79/0.81/0.86, but per-seed training accuracies at n=64 range from 0.81
to 0.94 due to sampling noise. Seed 1 consistently runs high (left>t
at 0.91-0.94). The experiment therefore tests the *distribution* of per-seed
proxy accuracies, not a single population-level number. This is noted as a
pre-registered design limitation.

Class balance: all 0.500 ✓. Positives ≥ 5: all 32 ✓.
Audit PASSES.

## Pre-registered outcomes (required — at least three)

Graded per threshold, then combined. Per-threshold:

| outcome | criterion | interpretation |
|---|---|---|
| **ESCAPES** | F_AND ≥ 8/20 on at least one arm AND attractor_AND ≥ 0.50 | Proxy basin does NOT trap at this proxy level. |
| **PARTIAL ESCAPE** | F_AND ∈ [3, 7] on at least one arm | Some seeds escape; boundary region. |
| **TRAPS** | F_AND ≤ 2/20 on both arms AND attractor_proxy ≥ 0.50 | Proxy basin still traps at this proxy level. |
| **COLLAPSE** | F_AND ≤ 2/20 AND mean best < 0.80 | Task not learnable at this threshold (class too sparse). |

Combined (3-threshold gradient):

| >6 | >7 | >8 | interpretation |
|----|----|-----|---------------|
| ESCAPES | TRAPS | TRAPS | **Boundary at ~0.80.** The current "≥~0.85" claim is approximately right. |
| ESCAPES | ESCAPES | TRAPS | **Boundary at ~0.85.** Narrower than expected — only the highest proxy traps. |
| ESCAPES | PARTIAL | TRAPS | **Gradient.** Boundary is in the 0.80-0.85 range. Best result. |
| TRAPS | TRAPS | TRAPS | **Threshold below 0.80.** Per-seed variance dominates; population proxy level is insufficient to predict trapping. Relax claim to "per-seed proxy accuracy" framing. |
| ESCAPES | ESCAPES | ESCAPES | **Independence changes the game.** The basin is about correlation structure, not proxy accuracy alone. |

## Degenerate-success guard (required)

- **Too-clean (ESCAPE direction):** F_AND ≥ 18/20 at threshold >6.
  Candidate: evolution finds a constant-output or input-invariant program
  that scores 0.999 on this specific seed × n_examples slice. Holdout gap
  is the diagnostic. Also: SUM_LEFT2/SUM_RIGHT2 are new tokens — check that
  solvers actually USE them rather than finding a whole-list shortcut.
- **Too-clean (TRAPS direction):** identical attractor breakdown across all
  three thresholds. Would suggest the threshold sweep is uninformative
  (all land in the same basin).
- **How to detect:** decode_winner.py on all solvers + non-solver sample.
  Check whether winners use SUM_LEFT2/SUM_RIGHT2 (the intended compositional
  route) or find alternative solutions. For Arm A, check whether the tape
  contains the tokens at all.

## Statistical test

- **Per threshold:** paired McNemar on F_AND, BP_TOPK vs Arm A, seeds 0..19.
  Two-sided α=0.05.
- **Across thresholds (primary):** descriptive gradient analysis. Is there a
  monotone relationship between proxy level and F_AND? Reported as a table,
  not a formal test (3 data points don't support regression).

## Diagnostics to log (beyond fitness)

- F_AND per arm per threshold at 0.999 and 0.95.
- Per-seed best-of-run fitness.
- Mean and max train-holdout gap (overfit audit).
- Attractor breakdown per arm per threshold (decode_winner.py).
- Whether solvers use SUM_LEFT2/SUM_RIGHT2 tokens.
- Per-seed proxy accuracy of left>t and right>t on the actual training data
  (to check per-seed variance against the pre-registered audit).

## Scope tag (required for any summary-level claim)

**If gradient result (escape at low proxy, trap at high):**

`within-family / cross-decoder · n=20 per arm per threshold ·
at pop=1024 gens=1500 v2_split alphabet · across decoder arms
{BP_TOPK(k=3,bp=0.5), Arm A} · on split-halves AND(sum_left2>t,
sum_right2>t) over [0,9]^4 · proxy-basin trapping boundary at
per-seed proxy accuracy ~X`

## Decision rule

- **Gradient (ESCAPE/PARTIAL/TRAPS across thresholds) →** update
  `findings.md#proxy-basin-attractor` with the measured trapping
  boundary. Add split-halves experiments to Supporting experiments.
  This is the highest-value outcome: it pins the threshold.
- **All TRAP →** relax claim to "per-seed proxy accuracy" framing.
  The population-level ~0.80 is insufficient to predict escape when
  per-seed variance pushes accuracy above ~0.85 on many seeds.
  Queue longer-list experiments ([0,9]^8 or [0,3]^8) where per-seed
  variance is lower due to larger n.
- **All ESCAPE →** the proxy basin is about correlation structure, not
  just accuracy. The split-halves independence qualitatively changes the
  landscape. Update the mechanism name to include "correlated proxy"
  qualifier. This would be a significant narrowing of the current claim.

---

*Audit trail.* Four per-threshold outcome rows plus five combined-gradient
rows (principle 2). Thresholds anchored to §v2.4-proxy-2 and §v2.4-alt
measured baselines (principle 6). Internal control is the 3-threshold
gradient itself plus decoder-arm contrast (principle 1). Sampler audit
discharged with measured numbers including per-seed variance caveat
(principle 20). Degenerate-success candidates enumerated including
new-token usage check (principle 4). Decision rule includes gradient,
all-trap, and all-escape branches (principle 19).
