# Pre-registration: §v2.13 — BP_TOPK(k=5) parameter sweep on §v2.3 and §v2.6 Pair 1

**Status:** QUEUED · target commit `75ab827` · 2026-04-15

Derived from the §v2.6-pair1 follow-up sweeps' observation that BP_TOPK's
**permeability absorbs tape-level scatter** ([`docs/chem-tape/experiments-v2.md
§v2.6-pair1-scale`](../docs/chem-tape/experiments-v2.md#v26-pair1-scale)).
If permeability is load-bearing, widening the top-K window from k=3 to
k=5 should change the decoder's absorbing capacity, with two competing
predictions on which direction the change moves solve rate.

## Question (one sentence)

Within the BP_TOPK decoder family, does increasing `topk` from 3 to 5 —
holding all other config fixed — change BOTH-solve rate, ADI, and
solved-seed identity on (a) §v2.3's `sum_gt_{5,10}_slot` 4-token body and
(b) §v2.6 Pair 1's `any_char_count_gt_{1,3}_slot` 6-token body?

## Hypothesis

Two competing decoder-mechanism readings produce opposite predictions:

1. **Permeability absorbs scatter (helpful at higher k).** k=5 widens
   the run-extraction window, so more tape configurations extract to
   the canonical body. Predicted: BOTH lifts on Pair 1 (more component
   sets become reachable behaviorally). On §v2.3 (already at ceiling
   under k=3), no effect or marginal lift only on the one stuck seed.

2. **Permeability dilutes the body (harmful at higher k).** k=5 admits
   more non-canonical token sequences as valid extracts, weakening the
   selection pressure for canonical-body assembly. Predicted: BOTH
   regresses on Pair 1 (noisier extraction); on §v2.3, mild regression
   if any.

3. **Null (k is a saturated parameter at k=3).** No measurable effect
   on either body at this budget.

The §v2.6-pair1 follow-up sweeps' read — "the decoder's permeability
absorbs tape-level scatter and is part of why components-present implies
behavioral solve at scaled compute" — weights the prior toward (1) on
Pair 1 specifically. (3) is the methodological null.

## Setup

- **Sweep files:**
  - `experiments/chem_tape/sweeps/v2/v2_13_k5_v2_3_alt.yaml` —
    alternation `{sum_gt_5_slot, sum_gt_10_slot}` under BP_TOPK(k=5, bp=0.5).
  - `experiments/chem_tape/sweeps/v2/v2_13_k5_v2_3_fixed.yaml` —
    fixed-task baselines on each task under k=5.
  - `experiments/chem_tape/sweeps/v2/v2_13_k5_pair1_alt.yaml` —
    alternation `{any_char_count_gt_1_slot, any_char_count_gt_3_slot}`
    under BP_TOPK(k=5, bp=0.5).
  - `experiments/chem_tape/sweeps/v2/v2_13_k5_pair1_fixed.yaml` —
    fixed-task baselines on each task under k=5.
- **Tasks:** four existing tasks across two pairs.
- **Alphabet:** `v2_probe`.
- **Intervention:** `topk: 5` (only change vs §v2.3 / §v2.6 Pair 1
  baselines; arm and bond_protection_ratio held).
- **Fixed params (matched verbatim to baselines):**
  `arm: BP_TOPK`, `topk: 5` (this sweep's intervention), `bond_protection_ratio: 0.5`,
  `tape_length=32`, `n_examples=64`, `holdout_size=256`, `pop_size=1024`,
  `generations=1500`, `tournament_size=3`, `elite_count=2`, `mutation_rate=0.03`,
  `crossover_rate=0.7`, `task_alternating_period=300`.
- **Seeds:** `0..19` per sweep — matched to baselines.
- **Est. compute:** ~30 min at 10 workers (160 runs total: 4 sub-sweeps × 20 ×
  alt-or-fixed; alt sweeps and fixed sweeps both at the same per-run cost).
- **Related experiments:**
  [§v2.3](../docs/chem-tape/experiments-v2.md#v23) ·
  [§v2.6 Pair 1](../docs/chem-tape/experiments-v2.md#v26) ·
  [§v2.6-pair1-scale (the permeability inference source)](../docs/chem-tape/experiments-v2.md#v26-pair1-scale).

## Baseline measurement (required)

- **Baseline quantity:** §v2.3 and §v2.6 Pair 1 results under BP_TOPK(k=3,
  bp=0.5) at matched compute.
- **Measurement:** previously recorded.
  - §v2.3 (commit `e3d7e8a`, seeds 0..19 block):
    `BOTH_BP_v2_3 = 20/20`, `F_5_BP = 20/20`, `F_10_BP = 19/20`,
    flip-cost mean = 0.000.
  - §v2.6 Pair 1 (commit `0230662`, seeds 0..19):
    `BOTH_BP_pair1 = 4/20`, `F_gt1_BP = 4/20`, `F_gt3_BP = 10/20`,
    `COMP_BP = 6/20`, `ADI_BP = +0.10`.
- **Threshold calibration (principle 6):** outcome rows below are
  expressed as deltas from these k=3 baselines on each pair separately.
  No absolute thresholds.

## Internal-control check (required)

- **Tightest internal contrast:** §v2.3 and §v2.6 Pair 1 themselves under
  k=3. Same tasks, same seeds, same compute, same arm, same bp. Only
  `topk` varies. This is the cleanest within-decoder-family parameter
  sweep available.
- **Are you running it here?** Yes. The k=5 sweeps form the within-family
  parameter-sweep internal control on each body (per principle 1).

## Sampler-design audit (principle 20)

**NOT TRIGGERED.** No change to training distribution. Same task builders,
same `n_examples`, same `holdout_size`, same per-seed RNG path. Class
balance, proxy accuracy, and label-function viability inherit verbatim
from §v2.3 and §v2.6 Pair 1.

## Pre-registered outcomes (required — at least three)

Outcomes are graded **per pair**; combined verdict at the end.

### Per-pair scoring

Definitions (per pair):
- `BOTH_5 = ` BP_TOPK(k=5) alternation BOTH-solve at fitness ≥ 0.999.
- `COMP_5 = ` BP_TOPK(k=5) winners with full canonical token set.
- `ADI_5 = (COMP_5 − BOTH_5) / 20`.
- `Δ_BOTH = BOTH_5 − BOTH_3` (positive = k=5 helps).
- `Δ_ADI = ADI_5 − ADI_3`.

Row precedence: top-to-bottom (first match wins). Default-INCONCLUSIVE
catches every cell not explicitly classified (codex [P1] exhaustiveness
finding addressed).

| per-pair outcome | criterion | interpretation |
|---|---|---|
| **HELPS — clean (permeability widens absorption)** | `Δ_BOTH ≥ +3` AND `Δ_ADI ≤ 0` AND McNemar one-sided p ≤ 0.05 | Reading (1) supported. Wider k absorbs more tape configurations into canonical body without assembly cost. |
| **HELPS — solve-count only (assembly gap rises)** | `Δ_BOTH ≥ +3` AND `Δ_ADI > 0` (k=5 raises BOTH AND assembly gap) | Wider k extracts more bodies but with more assembly fragmentation. Net positive on solve count, but mechanism is "permeability widens AND tolerates non-canonical assembly," not pure permeability win. Inspection required. |
| **REGRESSES — solve drop** | `Δ_BOTH ≤ −3` AND McNemar one-sided p ≤ 0.05 | Reading (2) supported. Wider k weakens selection pressure for canonical-body assembly. |
| **REGRESSES — assembly gap rises without solve drop** | `\|Δ_BOTH\| ≤ 2` AND `Δ_ADI ≥ +0.10` | Wider k destabilises canonical-body assembly without (yet) costing solves; consistent with reading (2) at smaller magnitude. |
| **NULL — k saturated at 3** | `\|Δ_BOTH\| ≤ 2` AND `\|Δ_ADI\| ≤ 0.05` | Reading (3): k is not a load-bearing axis at this budget on this body. |
| **INCONCLUSIVE — small directional lift, mechanism uncertain** | `Δ_BOTH ∈ [+1, +2]` AND `\|Δ_ADI\| ≤ 0.10` (and no McNemar significance) | Suggestive but not statistically distinguishable from noise at n=20. Report as-is; no mechanism reading triggered. |
| **DEFAULT INCONCLUSIVE** (codex [P1] addressed) | any other cell | Result lands outside all enumerated rows. Report descriptively; no mechanism reading; flag as outcome-table-incomplete for future-prereg lessons. |

### Combined verdict (across both pairs)

Encoded as a 7×7 grid (one row per per-pair outcome). The full grid is
mechanically expanded below per the codex [P1] exhaustiveness finding.
Verdicts use the more pessimistic of the two pair outcomes when they
conflict, except where explicitly noted; rows are ordered by precedence.

Per-pair outcomes (rows): HELPS-clean, HELPS-solve-only, REGRESSES-solve,
REGRESSES-assembly, NULL, INCONCLUSIVE-small, DEFAULT.

| §v2.3 outcome | Pair 1 outcome | combined verdict |
|---|---|---|
| HELPS-clean | HELPS-clean | **PASS — permeability is the lever (both bodies)** |
| HELPS-clean | HELPS-solve-only | **PASS — body-shape-asymmetric (Pair 1 has assembly cost)** |
| HELPS-clean | NULL or INCONCLUSIVE-small | **PASS — §v2.3 only; Pair 1 unchanged** |
| HELPS-clean | REGRESSES-solve or REGRESSES-assembly | **PASS — body-shape-divergent** (k helps short body, hurts long) |
| HELPS-solve-only | HELPS-clean | **PASS — body-shape-asymmetric (§v2.3 has assembly cost)** |
| HELPS-solve-only | HELPS-solve-only | **PASS — solve-count gain across bodies, with assembly cost on both** |
| HELPS-solve-only | NULL/INCONC/REGRESSES | **PASS-partial — solve-count gain on §v2.3 only, with caveat** |
| REGRESSES-solve | any | **FAIL — k=5 hurts §v2.3** (the load-bearing body); the constant-slot-indirection finding's scope further narrows |
| REGRESSES-assembly | REGRESSES-solve or REGRESSES-assembly | **FAIL — k=5 hurts both bodies** |
| REGRESSES-assembly | other | **PARTIAL-FAIL — assembly degradation on §v2.3 without Pair 1 corroboration** |
| NULL | HELPS-clean | **PARTIAL — Pair 1 only; §v2.3 saturated at k=3** |
| NULL | HELPS-solve-only | **PARTIAL — Pair 1 solve gain with assembly cost** |
| NULL | NULL or INCONCLUSIVE-small | **NULL across both** — k saturated at 3 in BP_TOPK family |
| NULL | REGRESSES-solve or REGRESSES-assembly | **FAIL-on-Pair-1** — k=5 hurts long body without helping short |
| INCONCLUSIVE-small | any | **DEFAULT INCONCLUSIVE** — combine with §v2.3 default fallback |
| DEFAULT | any | **DEFAULT INCONCLUSIVE** — outcome-table-incomplete; report as-is |
| (any) | DEFAULT | **DEFAULT INCONCLUSIVE** |

**PARTIAL-on-scales-bar threshold dropped (codex [P2] finding addressed):**
the earlier draft had a `BOTH_5 < 14/20` "scales bar" threshold imported
from §v2.3's reference. Per principle 6 this is a transported absolute
bar. Removed; the per-pair table's HELPS / REGRESSES / NULL relative
classifications are sufficient. Pair 1's clearing-the-scales-bar question
is reframed as: "did Pair 1 land HELPS-clean with `BOTH_5 ≥ Fmin_Pair1_5
− 1`?" — anchored to k=5's own measured Fmin on Pair 1, not §v2.3's
absolute reference.

## Degenerate-success guard (required)

- **Too-clean candidates:**
  - On §v2.3 (HELPS direction): k=5 produces 20/20 BOTH AND raises the
    one stuck seed (currently F_10 = 19/20) to 20/20.
  - On Pair 1 (HELPS direction): k=5 lifts BOTH from 4/20 to ≥ 12/20,
    crossing into the "scales" range without compute increase.
- **Candidate degenerate mechanisms:**
  1. **k=5 admits a degenerate extract that scores ≥ 0.999 by accident
     on this task family.** Wider top-K means more tape positions
     produce valid extracts; some of those extracts may be short
     constant-output programs that happen to score ≥ 0.999 on the seed
     × n_examples sample (without genuinely solving the task on holdout).
     Holdout gap is the diagnostic.
  2. **k=5 reproduces the §v2.4-alt seed 2 "alternative assembly" pattern
     more frequently** — multiple tape-level assemblies map to the same
     behavioral body. This is genuine PASS but with a different
     attractor-category breakdown than k=3. Inspection required to
     distinguish from (1).
  3. **k=5 NULL on §v2.3 may itself be degenerate** if the §v2.3 body is
     already at ceiling (as the F_5 baseline shows). NULL must be
     interpreted as "saturated, not informative" rather than "k irrelevant."
- **How to detect (inspection commitment):**
  1. Compute holdout gap per seed per sub-sweep. Any winner with
     train ≥ 0.999 AND holdout < 0.95 is flagged for inspection.
  2. For every BOTH-solver on each sub-sweep, run `decode_winner.py
     <sweep_id> --all` and classify into: canonical-contiguous,
     canonical-with-scatter (BP_TOPK absorption), alternative-assembly
     (§v2.4-alt seed 2 type), degenerate-extract.
  3. Solved-seed overlap with the k=3 baseline on shared seeds 0..19.
     If k=5 unlocks a different seed set rather than extending k=3's
     set, the body-shape-dependent reading is supported (decoder-parameter
     and body-shape interact non-additively, per principle 9).
  4. ADI per seed: HELPS-with-rising-ADI is the MIXED-on-pair row,
     not pure HELPS.

## Statistical test

- **Per pair:** paired McNemar on BOTH-solve, k=5 vs k=3, shared seeds
  0..19. Two-sided exact binomial on (b, c). **One-sided α=0.05** for
  the directional test (codex [P1] threshold-shopping finding addressed:
  earlier draft used α=0.10 citing §v2.6-pair1 follow-up sweeps as
  precedent, but those sweeps used α=0.05 and explicitly noted
  `p=0.0898` did NOT pass — using their data to justify α=0.10 was
  threshold-shopping). Reverting to project-standard α=0.05.
- **Per pair, secondary:** McNemar on COMP-presence (k=5 vs k=3), same
  seeds, α=0.05.
- **Across pairs:** descriptive only; no across-pair meta-test.

## Diagnostics to log (beyond fitness)

- Per pair: BOTH_5, F_a_5, F_b_5, COMP_5, ADI_5 raw counts.
- Per seed: best-of-run final fitness on each task.
- Per seed: train, holdout, train−holdout gap.
- Per BOTH-solver: winner decode + attractor-category classification.
- Solved-seed overlap with k=3 baseline per pair.
- Mean and max post-flip fitness drop on alternation per pair.
- ADI trajectories per pair (per-generation history if computable from
  existing logs; defer if too expensive — note as deferred per principle).
- For every alternation seed: count of seeds with `COMP_5 = 1` AND
  `BOTH_5 = 0` (assembly-but-not-solve gap, mirrors §v2.6-pair1-scale's
  load-bearing diagnostic).

## Scope tag (required for any summary-level claim)

**If PASS on either pair, the claim enters notes (not a new findings.md
entry — this is parameter-sweep evidence on existing entries) scoped as:**

`within-decoder-family · n=20 per pair · at pop=1024 gens=1500 v2_probe
alphabet · on bodies {INPUT SUM THRESHOLD_SLOT GT (4-token);
INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT (6-token)} ·
across BP_TOPK k ∈ {3, 5} at bp=0.5`

Explicitly **NOT** claiming on PASS:
- Generalisation to other k values (k=7, k=10).
- Generalisation to other bond_protection_ratio values.
- Generalisation to non-BP_TOPK decoders (Arm A is §v2.11 / §v2.12).
- That k=5 is a "better default" — the result characterises k as a
  body-shape-dependent axis, not a global hyperparameter improvement.

## Decision rule

- **PASS — permeability is the lever (both pairs) →** add a "k is a
  body-shape-tunable axis" note to `findings.md#constant-slot-indirection`
  Open external-validity questions section. No new findings entry; this
  is a parameter-sweep refinement of existing entries. Queue `§v2.13-k7`
  if the user values further parameter exploration; not auto-queued.
- **PASS — body-shape-dependent →** record as decoder × body interaction
  evidence. Update `findings.md#constant-slot-indirection` Open external-validity
  questions to note that k is a body-shape-dependent axis, not a global
  improvement direction. Most informative outcome; warrants chronicle
  attention.
- **PARTIAL — Pair 1 helped but below scales bar →** add to Pair 1
  follow-up ledger ([`docs/chem-tape/experiments-v2.md
  §v2.6-pair1 follow-up sweeps`](../docs/chem-tape/experiments-v2.md#v26-pair1-follow-up-sweeps-2×2×2-of-compute-×-tape-×-decoder))
  as one more axis with diminishing returns. No findings change.
- **NULL across both →** record as parameter-saturation evidence.
  No findings change. Treat as closing the k-axis question; future
  preregs need not test k variation unless body shape changes
  substantially.
- **FAIL — k=5 worse on §v2.3 →** trigger supersession-mode pass on
  `findings.md#constant-slot-indirection`. The "Tested only at BP_TOPK(k=3,
  bp=0.5)" caveat upgrades from honesty note to **strict scope tag**.
  Mechanism rename check: name should reference k.

---

*Audit trail.* Five pre-registered per-pair outcome rows (HELPS, REGRESSES,
NULL, MIXED-on-pair, plus the FAIL case in combined verdict) and four
combined-verdict rows (principle 2). Per-pair thresholds anchored to
measured k=3 baselines on each body (principle 6). Two within-family
internal controls (§v2.3 self-comparison and Pair 1 self-comparison),
both running here (principle 1). Sampler-design audit not triggered,
explicitly stated (principle 20). Degenerate-success candidates enumerated
per direction with explicit attractor-classification commitment (principle 4
+ 21). Decision rule includes both narrowing (FAIL) and refinement (PASS)
supersession triggers (principle 13). Pairing strength preserved by
parameter-only change (principle 7).
