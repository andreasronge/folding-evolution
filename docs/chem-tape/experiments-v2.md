# Experiments: Chemistry-Tape v2 probe

**Scope:** pre-registered experimental suite for the v2 probe defined in [architecture-v2.md](architecture-v2.md). Each experiment has a sharp pre-registered outcome table before implementation, informed by what §v1.5a-internal-control taught us about overfit framings. v1 experimental record lives in [experiments.md](experiments.md) and is unchanged by this document.

> **Where to read what.**
> - **Durable scope-tagged claims** consolidated from these chronicles → [`findings.md`](findings.md) (op-slot-indirection, constant-slot-indirection, proxy-basin-attractor).
> - **v1 lab notebook** → [`experiments.md`](experiments.md).
> - **Architecture / decision tree** → [`architecture-v2.md`](architecture-v2.md) (and v1 in [`architecture.md`](architecture.md)).
> - **Methodology principles** referenced in interpretations → [`docs/methodology.md`](../methodology.md).

### Quick gloss on the v1 sections referenced throughout

- **[experiments.md §10](experiments.md) (K-alternation)**: K cycles between 3 and 999 on a single task; post-flip fitness drop exactly 0.000 on every flip; 7/20 solve rate. Established zero-cost cross-decode compatibility.
- **[experiments.md §v1.5a-binary](experiments.md)**: two tasks differing only in `slot_12`'s op binding (MAP_EQ_R vs MAP_IS_UPPER) under alternation; 20/20 BOTH-solves. Established that slot-indirection is a body-invariant route across regimes.
- **[experiments.md §v1.5a-internal-control](experiments.md)**: two sum-gt-N tasks differing only in threshold constant (5 vs 10); 0/20 BOTH despite matched basin, scaffold, and slots. Falsified the basin × scaffold framework — required-body-structure-differences canalize even with all other axes matched.

### Backend and compute

All sweeps use the MLX engine + Rust executor path (`_folding_rust.rust_chem_execute_batch`, same path used for v1's §8-§v1.5 measurements). Compute estimates assume pop=1024 × gens=1500 × 20 seeds at 4-worker parallelism on M1. Empirical v1 reference: `sum_gt_10_topk` at these settings = ~17.6 min; similar-shape v2 experiments should fall in the 10-15 min range each.

## North star (restated)

> Does chem-tape's body-invariant-route mechanism (v1 experiments.md §10 + §v1.5a-binary) scale with expressivity, or is it a v1-scale artifact?

Four possible regime outcomes define the decision tree in [architecture-v2.md](architecture-v2.md#decision-tree): scales cleanly, swamped by expressivity, does not scale, partial. Each suite experiment below pre-registers which outcome its result would support. §v2.1's Part A fixed-baseline check is the explicit swamp-detection gate.

## Suite at a glance

| # | experiment | target question | gates | ~compute |
|---|-----------|-----------------|-------|----------|
| §v2.1 | K-alternation replication + swamp-check | does §10's zero-cost cross-K signature survive? Is there mechanism headroom at v2 scale? | — | ~15 min + fixed baseline ~10 min |
| §v2.2 | Multi-slot indirection test | does §v1.5a-binary's slot-indirection scale across multiple slots / a broader primitive set? | — (run regardless of §v2.1) | ~15 min |
| §v2.3 | Constant-slot indirection (§v1.5a-internal-control at v2) | does slot-indirection absorb **constant** variation, not just op variation? Resolves or reaffirms §v1.5a-internal-control's falsification. | — (run regardless of §v2.1, §v2.2) | ~15 min |
| §v2.4 | Compositional depth probe | does the mechanism survive tasks using IF_GT? | §v2.1 pass OR §v2.3 pass | ~15 min |
| §v2.5 | Aggregator-variation pair | does matched-body with different aggregators co-solve? | exploratory (qualitative) | ~10 min |

Estimated total: ~1.5 hours of compute across all five. **§v2.1, §v2.2, and §v2.3 are pre-registered independents** — each tests a distinct mechanism axis, and any one passing is independently scientifically informative. Earlier version of this doc gated §v2.3 on §v2.2; that was a mistake (§v2.3 is arguably the most informative experiment, and gating it behind §v2.2 would have killed the test we most want to see if §v2.2 partially failed). §v2.4 remains gated because it tests compositional depth, which only becomes interesting if at least one slot-indirection axis passes.

---

## §v2.1 K-alternation replication + swamp-check at v2 expressivity

**Question.** [experiments.md §10](experiments.md) showed zero-cost K-alternation compatibility (7/20 solve rate, 0.000 post-flip drop) on sum_gt_10 at K ∈ {3, 999}. Does this signature survive at v2 expressivity? Also: does the new alphabet have enough headroom for a mechanism signal to be visible at all (swamp check)?

**Setup (two-part).**

**Part A — fixed-task baseline** (runs first, required for interpreting Part B).
- Task: `sum_gt_10_v2` — same label function as v1's `sum_gt_10`, but using direct `CONST_5 CONST_5 ADD` for constant construction instead of v1's `CONST_1 + DUP + ADD` chain.
- K=3 r=0.5 panmictic × seeds 0-19 × pop=1024, gens=1500. Single K, no alternation.
- Call resulting solve rate `F_10_v2`.

**Part B — alternation.**
- Same task, K schedule {3, 999} × period 300 × seeds 0-19.
- Call alternation solve rate `A_10_v2` and mean absolute flip delta `Δ_10_v2`.

**Pre-registered outcomes (baseline-relative thresholds).**

| swamp check (Part A) | alternation behavior (Part B) | interpretation |
|----------------------|-------------------------------|----------------|
| F_10_v2 ≥ 18/20 | any | **Swamped:** v2 expressivity has removed the selection pressure the mechanism exploited in v1. Fixed-task ceiling is so high that alternation cannot demonstrate mechanism-attributable lift. Declare swamped outcome; gate §v2.4 accordingly. |
| F_10_v2 < 18/20 | A_10_v2 ≥ F_10_v2 − 1 AND Δ_10_v2 < 0.05 | **Scales:** §10's zero-cost signature reproduces. |
| F_10_v2 < 18/20 | A_10_v2 ≥ F_10_v2 − 3 AND Δ_10_v2 < 0.15 | **Partial:** mechanism present but degraded. |
| F_10_v2 < 18/20 | A_10_v2 < F_10_v2 − 3 OR Δ_10_v2 ≥ 0.2 | **Does not scale:** K-alternation is no longer a free axis at v2 scale. |

Thresholds are **relative to the measured v2 fixed baseline**, not v1's 7/20. v1's 7/20 was absolute-number; for v2 it's likely a trivial bar (direct constants make the task easier), so relative framing is needed.

## §v2.2 Multi-slot indirection test

**Question.** [experiments.md §v1.5a-binary](experiments.md) showed 20/20 cross-task solves when two tasks differed only in slot_12's op binding (MAP_EQ_R vs MAP_IS_UPPER). Does this slot-indirection mechanism generalize beyond that specific contrast?

**Setup.**
- New tasks (all binary, 4-cell scan-map-aggregate shape `INPUT CHARS slot_12 ANY`):
  - `any_char_is_R`: `slot_12 = MAP_EQ_R`. Label 1 iff any char is 'R'.
  - `any_char_is_E`: `slot_12 = MAP_EQ_E` (new primitive). Label 1 iff any char is 'E'.
  - `any_char_is_upper`: `slot_12 = MAP_IS_UPPER`. Label 1 iff any char is uppercase.
- Schedule: alternation × period 300 × seeds 0-19, K=3 r=0.5 panmictic.
- **Pair A** = {any_char_is_R, any_char_is_E} — both slot_12 variants are MAP_EQ_* family.
- **Pair B** = {any_char_is_R, any_char_is_upper} — slot_12 variants cross MAP_EQ vs MAP_IS families. (This is the §v1.5a-binary pair, re-run under v2 alphabet.)

**Pre-registered outcomes (2×2 grid).**

| | Pair A: 15+/20 BOTH | Pair A: 0-14/20 BOTH |
|---|---|---|
| **Pair B: 15+/20 BOTH** | **Scales cleanly.** Slot-indirection generalizes to any MAP op at v2. §v1.5a-binary's 20/20 was a general property, not specific to the tested pair. | Asymmetric: cross-family works, within-family fails. Unlikely and would need inspection — not pre-registered as a primary outcome. |
| **Pair B: 0-14/20 BOTH** | **Partial:** indirection works within-family but breaks across MAP families. Reveals a within-family vs across-family axis we hadn't separated. | **Does not scale:** even direct slot-variation fails at v2 expressivity. Strong negative for the mechanism claim. |

**What this tests that §v1.5a-binary did not.** §v1.5a-binary was a single contrast (MAP_EQ_R ↔ MAP_IS_UPPER). §v2.2 disambiguates "the 20/20 was specific to that pairing" vs "the 20/20 is a general property of slot-level indirection across any same-shape map ops." Pair A answers the former; Pair B is the v2-alphabet replication of v1's result.

## §v2.3 Constant-slot indirection — does slot-indirection absorb constant variation?

**Question.** [experiments.md §v1.5a-internal-control](experiments.md) falsified the basin × scaffold framework by showing {sum_gt_5, sum_gt_10} co-solve at 0/20 despite matching basin, scaffold, input type, and slot bindings. The required bodies still differed — sum_gt_5 used a CONST_1-based construction producing 5, sum_gt_10 used a different one producing 10. §v2.3 tests whether the slot-indirection mechanism (v1's §v1.5a-binary, v2's §v2.2) extends from op-binding to **constant-binding**. If yes, body-invariant routes are available for constant variation and the framework is recoverable. If no, the §v1.5a-internal-control falsification stands at v2 scale and the mechanism's scope is genuinely narrower than we hoped.

**Design commitment (pre-registered).** The test uses slot-bound threshold constants. Specifically:

- Introduce a new token `THRESHOLD_SLOT` (part of the v2 alphabet extension — updates architecture-v2.md primitive table) that pushes an integer constant whose value is task-bound via `TaskAlphabet.threshold: int`. This is the same indirection mechanism as `slot_12` but binding a constant instead of an op.
- Both tasks share the identical body token sequence: `INPUT SUM THRESHOLD_SLOT GT`.
- `sum_gt_5_slot` binds `threshold = 5`. `sum_gt_10_slot` binds `threshold = 10`. No other difference.

This is the direct constant-indirection analogue of §v1.5a-binary's op-indirection. If §v1.5a-binary's mechanism (body-invariant route via slot binding) generalizes to constants, §v2.3 should produce §v1.5a-binary-like solve rates.

**Note on body-equivalence premise.** Under this design the two tasks use *literally identical token sequences*; the only inter-task variation is in the `threshold` value bound per task. This is a cleaner body-match than the earlier-drafted "both use CONST_5, one uses CONST_5 CONST_5 ADD" framing — acknowledged bluntly because the earlier draft overstated how body-identical those tasks were. The slot-indirection design below is the proper body-invariant-route test.

**Setup.**
- Tasks: `sum_gt_5_slot`, `sum_gt_10_slot` (both use `INPUT SUM THRESHOLD_SLOT GT` body, `threshold` task-bound).
- Schedule: alternation × period 300 × seeds 0-19, K=3 r=0.5 panmictic.
- Fixed-task baselines on each (part of §v2.1's baseline setup).

**Pre-registered outcomes.**

| BOTH solves at fitness ≥ 0.999 | interpretation |
|--------------------------------|----------------|
| 15+/20       | **Scales:** slot-indirection mechanism absorbs constant variation. §v1.5a-internal-control's falsification was specifically about constant-construction cost when no constant-binding primitive was available. Body-invariant route mechanism is genuinely the load-bearing axis, and the slot-indirection extension recovers full compatibility. |
| 6-14/20      | **Partial:** constant-slot indirection helps but doesn't fully resolve the falsification. Would need inspection of which seeds co-solve vs which don't. |
| 0-5/20       | **Does not scale:** even direct slot-bound constants don't produce co-solve. The §v1.5a-internal-control falsification isn't constant-construction-specific; some deeper axis (learning dynamics under alternation, differential selection on task samples, etc.) is at play. This would be the sharpest negative result of the suite. |

## §v2.4 Compositional depth probe

**Question.** v1 tasks are all scan-map-aggregate (no compositional depth). `IF_GT` enables conditional-branching tasks. Does the mechanism survive at compositional depth > 1?

**Setup.**

Both tasks operate on the same integer-list input space as v1's `sum_gt_10` (intlist; no string/char inputs involved — this eliminates the input-type confound).

- **Task A — `sum_gt_10_AND_max_gt_5`**: binary. Label 1 iff `sum(input) > 10` AND `max(input) > 5`.
- **Task B — `sum_gt_10_OR_max_gt_5`**: binary. Label 1 iff `sum(input) > 10` OR `max(input) > 5`.

Both predicates (`sum > 10` via existing SUM + CONST_5 CONST_5 ADD + GT; `max > 5` via v2's REDUCE_MAX + CONST_5 + GT) are native to intlist. Both tasks use v2's `IF_GT` as the compositional primitive. Example solving programs (not the only valid programs; GP may evolve equivalents):

**Task A (AND):**
```
CONST_0                           # else_val = 0          → [0]
INPUT REDUCE_MAX CONST_5 GT       # mg = (max > 5)        → [0, mg]
INPUT SUM CONST_5 CONST_5 ADD GT  # s = (sum > 10)        → [0, mg, s]
IF_GT                             # pops s (cond), mg (then), 0 (else)
                                  # → mg if s>0 else 0  =  AND(mg, s) ✓
```
(Prefix `CONST_0` is placed first so the else slot sits at stack-bottom without needing a subsequent `SWAP` — cleaner than build-and-swap.)

**Task B (OR):**
```
INPUT SUM CONST_5 CONST_5 ADD GT  # s = (sum > 10)        → [s]
INPUT REDUCE_MAX CONST_5 GT       # mg = (max > 5)        → [s, mg]
DUP                               # duplicate mg          → [s, mg, mg]
IF_GT                             # pops mg (cond), mg (then), s (else)
                                  # → mg if mg>0 else s  =  OR(mg, s) ✓
                                  # (valid because mg is binary: mg=1 when >0)
```

Primitives used: v1's `INPUT, SUM, ADD, GT, CONST_0, SWAP, DUP` + v2's `CONST_5, REDUCE_MAX, IF_GT`. Both programs respect IF_GT's (else, then, cond) signature with `cond` on top.

**Body-diff framing (explicit).** Bodies are *not* token-identical. Differences: AND prefixes `CONST_0` to seat the else-branch at stack-bottom; OR uses `DUP` to duplicate cond as then. Token multisets differ by exactly one token — `{CONST_0}` vs `{DUP}` — and the AND/OR programs are otherwise isomorphic. This is a *minimal body-diff* compositional pair, not a body-matched one. §v2.4 therefore tests a slightly weaker compatibility hypothesis than §v2.2 / §v2.3: can the mechanism absorb *structurally isomorphic but one-token-divergent* compositional programs? A body-matched compositional test (using THRESHOLD_SLOT + ADD + GT to vary AND/OR via threshold 1 vs 0, sidestepping IF_GT entirely) is queued as **§v2.4-alt** if §v2.4's result is ambiguous or motivates a cleaner follow-up.

Alternation schedule: `{sum_gt_10_AND_max_gt_5, sum_gt_10_OR_max_gt_5}` × period 300 × seeds 0-19, K=3 r=0.5 panmictic.

**Fixed-task baselines.** Both tasks' fixed-task solve rates measured first (same pattern as §v2.1) to establish max-of-fixed per task. Let `Fmin = min(F_AND, F_OR)` be the lower of the two fixed baselines. Alternation thresholds are expressed relative to `Fmin`, with an absolute floor to prevent row-overlap at low `Fmin`.

**Pre-registered outcomes.**

| BOTH solves | interpretation |
|-------------|----------------|
| ≥ max(Fmin − 3, 12)  | **Scales:** mechanism survives compositional depth + non-trivial body-diff. |
| 6 ≤ BOTH < max(Fmin − 3, 12) | **Partial:** compositional depth reduces but doesn't eliminate compatibility. |
| 0-5/20 | **Does not scale:** compositional depth (and/or the body-diff) breaks the mechanism. Chem-tape's body-invariant-route claim applies only to non-compositional task space. |

**Importance:** if §v2.4 fails but §v2.1-§v2.3 pass, the v2 probe ends with "mechanism scales up to compositional depth 1 but not beyond" — a clear, narrower-than-hoped result.

## §v2.5 Aggregator-variation pair (qualitative / exploratory)

**Question.** Does matched-body differing only in aggregator (REDUCE_ADD vs REDUCE_MAX) co-solve?

**Setup.**
- Tasks: `agg_sum_gt_10` (uses REDUCE_ADD), `agg_max_gt_5` (uses REDUCE_MAX). If slot-bindable, implement as same body with slot-13 varying between the two aggregators — direct analogue of §v2.3's constant-slot design.
- Schedule: alternation at period 300.

**Qualitative observations to make** (not hard thresholds — labeled exploratory, primarily descriptive):
- Does alternation solve either task at all?
- Does the solve-set resemble either fixed-task's solve-set (suggesting canalization toward one aggregator) or span both (suggesting co-solve)?
- Does flip-drop magnitude resemble §v2.1's (zero-cost) or §v1.5's (substantial)?

This experiment is labeled exploratory and reports distributions, not pass/fail verdicts. Its role is to characterize which structural variations are absorbable vs canalizing at v2 scale, contributing qualitative evidence to the combined decision tree rather than a hard pre-registered bit.

---

## Overall decision tree

The suite has **four graded experiments** (§v2.1, §v2.2, §v2.3, §v2.4) with pre-registered pass/fail columns and **one exploratory experiment** (§v2.5) that reports qualitative distributions only. Combined outcomes map to one of four regimes (full decision tree in [architecture-v2.md](architecture-v2.md#decision-tree)):

- **Scales cleanly (≥3/4 graded in "scales" column + §v2.5 consistent, swamp-check not triggered):** mechanism generalizes. Commit to full v2 + v3 chemistry ablation. Paper-level claim: chem-tape provides scalable evolvability via body-invariant-route mechanism.
- **Swamped by expressivity (§v2.1 Part A triggers the swamp gate):** v2 fixed-task ceilings are saturated; alternation cannot demonstrate mechanism-attributable lift. Paper claim narrows to v1 scope; full v2 unlikely to teach more about chemistry.
- **Does not scale (≥3/4 graded in "does not scale" column):** v1 findings are rep-scale-specific. Full v2 is primarily capability engineering. Consider pivoting.
- **Partial (mixed, or 2/4 graded in any column):** focused follow-up to nail the specific failure mode; paper-level claim is about mechanism scope rather than existence.

§v2.5 never flips a "scales" verdict to "does not scale" on its own; it contributes qualitative evidence. If §v2.5 shows strong canalization that contradicts §v2.1-§v2.4's "scales" picture, flag as partial pending follow-up.

## What this suite does NOT test (explicitly out of scope)

- **Full folding-Lisp expressivity.** Quotation tokens, structured records, field access, higher-order combinators. This is full v2 scope, gated on v2-probe outcome.
- **Evolvable primitive set / alphabet.** The level-2 "can the mapping be evolved" direction. Queued as an exploratory probe contingent on v2-probe mechanism-scaling result.
- **New chemistry mechanisms.** Bond persistence variants, multi-pass bonding, irreversibility. These are v3 ablation territory; v2 probe holds chemistry fixed at v1 best configuration.
- **External validity on genuinely different task structures.** Order-sensitive, memory-requiring, non-threshold-arithmetic tasks. Some of these need further alphabet expansion beyond v2 probe scope; others (order-sensitive) need new executor semantics.

## Secondary direction queued: evolvable-mapping probe (level 2)

Described in [architecture-v2.md §Secondary direction](architecture-v2.md#secondary-direction-evolvable-gp-mapping-exploratory). Waits on v2-probe mechanism-scaling result.

For the broader meta-learning design space (six approaches including
morphogen chemistry, population-based meta-learning, and self-referential
chemistry programs), see
[meta-learning-design-space.md](meta-learning-design-space.md). The
header-cell probe here is the narrowest entry point; that document covers
the full range from diagnostic gate through ES+morphogen hybrids.

---

## Results (overnight run 2026-04-14 → 2026-04-15)

**Commit:** `6f12a56` (alphabet + executor + Rust port + queue infra), `ff4d1b3` (train-holdout gap + overfit flagging).
**Compute:** 14 sweep entries across the pre-reg suite + fixed-task baselines + §v2.3 seed expansion + tape-length headroom check. ~3h wall, MLX + Rust batch executor path, pop=1024, gens=1500, n_examples=64, holdout_size=256.

All per-seed artefacts under `experiments/output/2026-04-14/<entry_id>/` (plus the §v2.4 follow-up under `experiments/output/2026-04-15/`). Per-sweep layout: `sweep_index.json`, `metadata.json`, `stdout.log`, `stderr.log`, and one `<config_hash>/` subdirectory per seed × condition containing `config.yaml`, `history.csv`, `history.npz`, `result.json`.

#### Output directory map

| section | entry_id (path under `experiments/output/YYYY-MM-DD/`) |
|---|---|
| §v2.1 Part A (fixed baseline) | `2026-04-14/v2_1_partA_fixed_baseline` |
| §v2.1 tape=48 headroom check | `2026-04-14/v2_1_partA_tape48` |
| §v2.1 Part B (K-alternation {3, 999}) | `2026-04-14/v2_1_partB_kalt` |
| §v2.2 fixed baselines (R / E / upper_v2) | `2026-04-14/v2_2_fixed_baselines` |
| §v2.2 Pair A ({R, E}, within-family) | `2026-04-14/v2_2_pairA` |
| §v2.2 Pair B ({R, upper}, cross-family) | `2026-04-14/v2_2_pairB` |
| §v2.3 alternation (seeds 0-19 pre-reg) | `2026-04-14/v2_3_alternation` |
| §v2.3 fixed baselines (`sum_gt_5_slot`, `sum_gt_10_slot`) | `2026-04-14/v2_3_fixed_baselines` |
| §v2.3 seed expansion block 1 (seeds 20-39) | `2026-04-14/v2_3_seeds_20_39` |
| §v2.3 seed expansion block 2 (seeds 40-59) | `2026-04-14/v2_3_seeds_40_59` |
| §v2.3 seed expansion block 3 (seeds 60-79) | `2026-04-14/v2_3_seeds_60_79` |
| §v2.4 alternation ({AND, OR}) | `2026-04-14/v2_4_alternation` |
| §v2.4 fixed baselines (F_AND, F_OR) | `2026-04-14/v2_4_fixed_baselines` |
| §v2.4 compute-scaling follow-up (pop=2048, gens=3000) | `2026-04-15/v2_4_compute_scaling` |
| §v2.5 aggregator variation (exploratory) | `2026-04-14/v2_5_alternation` |

Authoritative queue definition: `queue.yaml` at repo root; completion state in `queue.status.json`.

### Per-experiment outcomes

| experiment | headline | verdict (pre-reg) |
|---|---|---|
| **§v2.1 Part A** (fixed baseline `sum_gt_10_v2`) | F_10_v2 = **18/20** train, 18/20 holdout | **Swamp gate tripped** |
| **§v2.1 Part B** (K-alternation {3, 999}) | A_10_v2 = **15/20** = F_10_v2 − 3 | Partial (but measurement-limited by swamp) |
| **§v2.1 tape=48 headroom** | 18/20 train (15/20 holdout) | Comparable to tape=32; alphabet density is not a confound |
| **§v2.2 Pair A** {R, E} within-family | **20/20 BOTH** train, **20/20 BOTH holdout** | **Scales cleanly** |
| **§v2.2 Pair B** {R, upper} cross-family | **20/20 BOTH** (v2 replication of §v1.5a-binary's 20/20) | **Scales cleanly** |
| §v2.2 fixed baselines on string tasks | R / E / upper_v2 all **20/20** train and holdout | Swamp-check joint condition satisfied |
| **§v2.3** constant-slot indirection | **20/20 BOTH** pre-reg; **80/80 BOTH** across 4 seed blocks (0-79); **399/400 flip events zero-cost** (one 5-generation recovery, seed 54); max |gap| = 0.0156 (≈ 1 holdout example out of 256) | **Strong evidence for slot-constant indirection on this body-invariant pair** |
| §v2.3 fixed baselines | `sum_gt_5_slot` 20/20, `sum_gt_10_slot` 19/20 (one stuck seed) | Strong |
| **§v2.4** compositional {AND, OR} | 2/20 BOTH at ≥0.999; 12/20 at ≥0.90; F_AND fixed = **0/20** (mean 0.92), F_OR fixed = 9/20 | **Partial / does-not-scale** — AND is the bottleneck |
| **§v2.5** aggregator variation (exploratory) | **20/20 perfect co-solve**, zero flip cost | Consistent with scaling |

### Overfit audit

Every entry's `train_holdout_gap` below the 0.05 threshold on > 95% of seeds; no entry crossed the attention bar (≥25% of seeds with gap > 0.05 or any single gap > 0.15). Details:

| entry | overfit_seeds | max_gap | mean_gap |
|---|---|---|---|
| §v2.3 + 3 expansion blocks (80 seeds) | 0 / 80 | 0.016 | ≈0 |
| §v2.2 (pair A, pair B, fixed baselines, 140 seeds) | 0 / 140 | 0.000 | 0 |
| §v2.5 | 0 / 20 | 0.000 | 0 |
| §v2.1 Part A / tape48 / Part B | 0 / 1 / 1 | 0.016 / 0.062 / 0.090 | ≈0 |
| §v2.4 alternation / fixed baselines | 1 / 20 / 2 / 40 | 0.059 / 0.078 | 0.004 / 0.012 |

**Interpretation:** train-fitness pre-reg verdicts are trustworthy. The holdout-enabled pre-registration worked as designed — the concern that 1500 generations on 64 training examples could produce memorised solutions did not materialise.

### Combined verdict against the decision tree

By the architecture-v2.md rubric — *≥3/4 graded in "scales" AND §v2.5 consistent* — the suite lands at **Partial**: two graded experiments scale (§v2.2, §v2.3), one swamps (§v2.1), one does-not-scale or partial (§v2.4). §v2.5 supports scaling.

However, the Partial label alone under-describes the result shape. The two axes extending §v1.5a's mechanism (op variation §v2.2 and constant variation §v2.3) both passed their pre-registered bars cleanly on body-invariant tasks. §v2.4 is the only axis where the mechanism failed, on a family that already acknowledged a known confound (compositional depth intertwined with a decode-position constraint — see §v2.4 body-diff framing).

**Honest scope note.** The 15+/20 "scales" bar at n=20 is an operational gate, not a broad generalization claim. §v2.3's 80/80 across 4 seed blocks is **precision on one task pair**, not breadth across task families; it tightens the estimate for this specific body-invariant pair rather than buying external validity. The §v2.1 swamp gate trigger at F_10_v2 = 18/20 is arguably permissive — 2/20 failures is not ceiling saturation in an inferential sense, even though the pre-reg threshold was set before data. These are reviewer-facing concerns worth acknowledging rather than hiding behind pre-reg.

### Headline framing for writeup

> Chem-tape's body-invariant-route mechanism passed its pre-registered bars on two narrow axes: op slot-indirection (§v2.2, 20/20 within-family and 20/20 cross-family) and constant slot-indirection (§v2.3, 80/80 BOTH across four seed blocks with max |train-holdout gap| = 0.0156 and 399/400 zero-cost flip transitions). §v2.1's pre-registered swamp gate fired at v2 expressivity, moving `sum_gt_10_v2` out of the mechanism-testing range at this primitive set — the pre-reg threshold at 18/20 is permissive and we note this honestly. §v2.4 (`IF_GT`-compositional AND task) failed at 0/20 both at pre-reg compute (pop=1024, gens=1500) and at 4× compute (pop=2048, gens=3000); the confound between compositional depth and the `CONST_0`-at-start-of-run decode-position constraint is not disentangled by this follow-up and is queued as §v2.4-alt.

The §v2.3 result directly recovers §v1.5a-internal-control's falsification on this particular body-invariant pair: two tasks with **token-sequence-identical bodies** differing only in a task-bound integer (`threshold = 5` vs `10`) produce 80/80 BOTH-solve with near-zero within-distribution gap. This is the strongest single mechanism claim in the suite, and it is a narrow one by design.

### §v2.4 open question

Both `AND` and `OR` tasks are binary, IF_GT-based, same input distribution. They differ only in the truth-table shape and — critically — the required body construction:
- **OR body**: `[s_block] [mg_block] DUP IF_GT` — no specific token-at-start-of-run constraint.
- **AND body**: `CONST_0 [mg_block] [s_block] IF_GT` — `CONST_0` must appear at the start of the extracted program (under BP_TOPK, this means start of the tape-earliest bonded run).

The F_AND = 0/20 vs F_OR = 9/20 asymmetry is consistent with a **decode-structure placement artifact**: evolution can find bodies where required tokens are *present* (OR) more easily than bodies where a specific token must land at a specific position within the extracted program (AND). This is a sharper failure-mode hypothesis than "compositional depth breaks the mechanism," and it has different paper implications.

Follow-up queued: a compute-scaling diagnostic on `sum_gt_10_AND_max_gt_5` at pop=2048 and gens=3000 (4× the pre-reg search budget, single-variable change).

**Pre-registered decision rule (recorded 2026-04-15 before results land):**
- `F_AND_scaled ≥ 10/20` → compute-limited; §v2.4 softens to "mechanism extends with search budget." The paper claim becomes "scales to compositional depth with sufficient search."
- `F_AND_scaled ≤ 3/20` → structural; narrow claim stands cleanly. The paper claim remains "scales on op and constant indirection; does not extend to IF_GT-compositional bodies at this compute."
- `4/20 ≤ F_AND_scaled ≤ 9/20` → ambiguous; report as-is, no retconning either direction.

**A-priori prediction (from existing F_AND baseline fitness distribution, n=20):** all 20 baseline seeds landed in 0.859–0.969 (mean 0.921, holdout 0.909). No flat basins; no canalisation on constant-output strategies. This is a refinement-bottleneck signature, not a search-trap. Under the decision rule above, this pre-data prediction weights toward `F_AND_scaled ≥ 10/20`. Recording the prediction now so the outcome can be compared to it honestly.

**Watch-out applied regardless of outcome:** even if compute scaling lifts F_AND to ≥10/20, the matched-compute AND vs OR asymmetry at pre-reg (F_AND = 0/20 vs F_OR = 9/20) is itself a real finding. The softened claim would be "mechanism scales to compositional depth with sufficient search budget; matched-compute asymmetry across truth-table shapes is a characterizable limit of the pre-reg configuration" — not "no asymmetry exists." The asymmetry is not retconned by a positive follow-up.

**Sanity check (2026-04-15, before compute-scaling run):** both the canonical `CONST_0`-first AND body (12 tokens) and an alternative middle-`CONST_0`-via-`SWAP` layout (13 tokens) produce **64/64 train and 256/256 holdout** correct labels under the v2 executor. The task is not impossible under v2 semantics; the failure is purely a search-discovery problem under BP_TOPK at pre-reg compute.

### §v2.4 follow-up results (2026-04-15, commit `f806d04` → run)

**Outcome: F_AND_scaled = 0/20 → STRUCTURAL** per the pre-committed decision rule (≤ 3/20).

| metric | baseline (pop=1024, gens=1500) | scaled (pop=2048, gens=3000) | Δ |
|---|---|---|---|
| solve (≥0.999) | **0/20** | **0/20** | 0 |
| near-solve (≥0.95) | 4/20 | 4/20 | 0 |
| close (≥0.90) | **16/20** | **17/20** | +1 |
| train mean | 0.921 | 0.923 | +0.002 |
| train max | 0.969 | 0.969 | 0 |
| holdout mean | 0.909 | 0.909 | 0 |
| max train-holdout gap | 0.0781 | 0.0781 | 0 |
| wall (mean per seed) | ~180s | 463s | +283s |

Aggregate solve count unchanged (0/20 → 0/20). At the per-seed level the picture is slightly richer: **17/20 seeds produced identical final fitness at 4× compute**, despite different starting populations (pop=1024 vs pop=2048). One seed moved up (seed 19: 0.9219 → 0.9688, refine→near-solve), one moved down (seed 7: 0.9531 → 0.9219, near-solve→refine), one crossed the 0.90 line without reaching near-solve (seed 9: 0.8906 → 0.9219). The ≥0.999 solve bar was not crossed by any seed in either setting.

**A-priori prediction: falsified.** The pre-committed prediction (commit `f806d04`) weighted the 0.85–0.97 baseline distribution toward F_AND_scaled ≥ 10/20, reading it as a refinement-bottleneck signature. The outcome (0/20) falsifies that prediction. Reporting honestly: the refinement-zone surface signal was misleading, but the inferred "stable local optimum" framing in the initial writeup was story, not measurement. Direct inspection replaces it below.

**Mechanism interpretation (from direct genotype inspection, 2026-04-15).** Decoding the best-of-run genotypes from the 20 F_AND baseline seeds under BP_TOPK (k=3, bond_protection=0.5):

- **14/20 seeds converge to `max > 5` exactly** — a simpler single-predicate function that agrees with AND on 64/64 balanced training examples only by coincidence of the input distribution. P(max > 5 | length-4 intlist over [0,9]) ≈ 0.87, and balanced-class sampling makes `max > 5` a ~92% proxy for AND on both train and holdout.
- **6/20 seeds** produce AND-like behaviour with best-hypothesis fit against `AND` but miss exact match — these are closer to the target function but still not solving.
- No seed collapses to a trivial constant-output strategy.

This is not a refinement bottleneck. It is a **proxy-predicate attractor**: evolution finds `max > 5` (a 1–2 token computation: `INPUT REDUCE_MAX CONST_5 GT`) that already scores ~0.92 on both train and holdout, and the fitness gradient from there to actual AND (requiring the `sum > 10` branch + `IF_GT` with correctly-placed `CONST_0`) is not traversable at 4× compute. The 2/20 F_OR solves-vs-0/20 F_AND asymmetry is consistent: `max > 5` is also a proxy for OR, but the stepping-stones from the `max > 5` basin to exact OR (e.g., adding `DUP IF_GT` without stack-bottom constraints) are shorter than the stepping-stones to exact AND (requiring stack-bottom `CONST_0`).

### Updated §v2.4 verdict

**At this mechanism, compute budget, and task formulation, F_AND is not solvable.** The narrower, better-grounded claim:

> This specific AND formulation under BP_TOPK (k=3, bond_protection=0.5) was not rescued by 4× search budget (pop=2048, gens=3000). Best-of-run genotypes converged to a `max > 5` proxy-predicate attractor (14/20 seeds exactly, 6/20 AND-partial) rather than to the correct compositional body. The compositional-depth vs decode-position-fragility confound already noted in §v2.4's body-diff framing is **not** disentangled by this follow-up. "Mechanism does not extend to `IF_GT`-compositional bodies" is too broad a conclusion from this data alone; the correct narrow reading is "max > 5 is a local optimum that 4× compute cannot exit toward AND on this task formulation." §v2.4-alt (body-matched compositional pair that holds the `IF_GT`-with-`CONST_0`-prefix shape constant) is the cleaner follow-up to disentangle the two hypotheses.

### Combined decision-tree verdict (updated 2026-04-15)

Still **Partial** per rubric, with a narrower decomposition than the initial writeup implied:
- **Positive (two body-invariant axes):** §v2.2 passed its pre-reg bar (20/20 within-family, 20/20 cross-family); §v2.3 passed with 80/80 BOTH across four seed blocks. Both are precision results on narrow body-invariant tasks, not broad scaling claims.
- **Measurement-limited (one axis):** §v2.1 swamp gate fired; we note the 18/20 threshold is permissive.
- **Confirmed does-not-scale at this compute on this task formulation (one axis):** §v2.4 F_AND = 0/20 at both 1× and 4× compute. Direct genotype inspection identifies a `max > 5` proxy-predicate attractor as the specific failure mode. The compositional-depth vs decode-position-fragility confound is **not** disentangled.
- **Supports scaling (exploratory, within this task pair):** §v2.5 at 20/20 perfect co-solve.

The pre-committed decision rule and the falsified a-priori prediction make the "F_AND not rescued by 4× compute" call clean. They do **not** justify the broader "mechanism does not extend to compositional depth" conclusion — that would require §v2.4-alt to run first.

### Headline framing for writeup (updated 2026-04-15, post-codex-review)

> Chem-tape's body-invariant-route mechanism passed its pre-registered bars on two narrow axes: op slot-indirection (§v2.2, 20/20 within-family and 20/20 cross-family at matched compute) and constant slot-indirection (§v2.3, 80/80 BOTH across four seed blocks, max |train-holdout gap| = 0.0156, 399/400 zero-cost flip transitions with one 5-generation recovery on seed 54). §v2.3 is precision on one body-invariant task pair, not breadth across task families. §v2.1's pre-registered swamp gate fired at v2 expressivity (F_10_v2 = 18/20) — we note the 18/20 threshold is permissive and is a reviewer-facing concern. §v2.4 (`IF_GT`-compositional AND task) failed at 0/20 at pre-reg compute (pop=1024, gens=1500) and at 4× compute (pop=2048, gens=3000); direct genotype inspection shows 14/20 baseline seeds converge to a `max > 5` proxy-predicate attractor that achieves ~0.92 on both train and holdout by coincidence of the input distribution. The compositional-depth vs decode-position-fragility confound is not disentangled by this follow-up; §v2.4-alt (body-matched compositional pair) is queued. **Scope of the paper claim: strong evidence for slot-op and slot-constant indirection on body-invariant tasks; one task family made uninterpretable by expressivity; one confounded compositional formulation fails robustly under this decoder/search setup.**

### Proposed follow-up experiments (2026-04-15, post-review)

Three concrete, pre-registrable experiments that address the specific weaknesses a skeptical reviewer (including Codex) flagged on this dataset. Listed in priority order.

#### §v2.4-alt — body-matched compositional pair (disentangles the §v2.4 confound)

**Question.** Is §v2.4's 0/20 driven by (a) compositional depth through `IF_GT`, (b) the `CONST_0`-at-start-of-run decode-position constraint specific to the AND body, or (c) a proxy-predicate attractor specific to the `sum > 10 AND max > 5` label function?

**Design.** Two new tasks whose canonical bodies share the **identical** `IF_GT`-compositional shape with `CONST_0` prefix — differing only in a `THRESHOLD_SLOT`-bound integer. Concretely, tasks of the form `label = (pred > threshold AND <fixed predicate>)` where both tasks use the same body template `CONST_0 INPUT REDUCE_MAX CONST_5 GT INPUT SUM THRESHOLD_SLOT GT IF_GT` and differ only in `threshold ∈ {5, 10}`. Requires two new task builders analogous to `sum_gt_{5,10}_slot` but wrapped in the `IF_GT`/`CONST_0`-prefix shape.

**Pre-registered outcomes (n=20 seeds, pop=1024, gens=1500 — matched to §v2.4 pre-reg):**
- Both solve ≥15/20 → decode-position constraint is **not** the blocker; §v2.4's failure is specific to the proxy-predicate attractor or the specific label function, and the "does not scale on compositional depth" reading falls apart.
- Both fail ≤3/20 → the `IF_GT`-plus-`CONST_0`-prefix compositional shape is genuinely hard regardless of task; §v2.4's failure generalises to this mechanism.
- Mixed → task-specific effects matter; specific subsequent follow-up required.

**Compute:** ~15–20 min.

#### §v2.4-proxy — shift the input distribution to break the `max > 5` attractor

**Question.** Is the §v2.4 F_AND failure mode specifically the `max > 5` proxy, or will evolution find whatever proxy the input distribution provides?

**Design.** Re-run the original `sum_gt_10_AND_max_gt_5` task at pre-reg compute, but with the input sampler generating length-4 intlists over [0,5] instead of [0,9]. Under the new distribution, `P(max > 5)` collapses to 0, so `max > 5` can no longer be a ~0.92 proxy for AND — the label becomes equivalent to `sum > 10` alone. If F_AND rises toward 15/20 on this variant, the `max > 5` attractor was the specific barrier. If F_AND remains near 0/20, evolution finds a different proxy and the "proxy-predicate basin" story generalises. If F_AND lands between, we learn something about how easily attractors form.

**Pre-registered outcomes (n=20 seeds, matched compute):**
- F_AND_[0,5] ≥ 15/20 → `max > 5` proxy was the specific barrier on the original task.
- F_AND_[0,5] ≤ 3/20 → evolution finds a new proxy under the new distribution; attractor story is general.
- 4–14/20 → report as-is.

**Compute:** ~15 min (one sweep).

#### §v2.6 — task-diversity breadth check for the constant-indirection claim

**Question.** Does §v2.3's 80/80 result generalise beyond the `sum_gt_{5,10}_slot` pair to other body-invariant constant-indirection pairs, or is it specific to this pair?

**Design.** Three additional body-invariant constant-indirection task pairs at matched compute (pop=1024, gens=1500, n=20):
- `any_char_count_gt_{1,3}_slot` (string domain, `INPUT CHARS slot_12 SUM THRESHOLD_SLOT GT` with slot_12 = MAP_EQ_R)
- `sum_gt_{7,13}_slot` (offset thresholds under wider input range, e.g. length-4 over [0,12])
- `reduce_max_gt_{2,5}_slot` (aggregator-variant, slot_13 = REDUCE_MAX)

**Pre-registered outcomes:** each pair scored independently (15+/20 BOTH = scales on that pair, 0-5/20 = doesn't, 6-14 = partial). Combined: 3/3 pass → §v2.3's claim has real breadth; 2/3 → narrow positive with characterizable edge; 1/3 or 0/3 → §v2.3 was specific to `sum_gt_{5,10}_slot` and the headline narrows sharply.

**Compute:** ~45 min (three pairs, ~15 min each).

#### Priority and sequencing

Run **§v2.4-alt first** — it's the single experiment that could most change the current verdict (from "compositional depth doesn't scale" to "the mechanism scales on compositional depth when decode-position constraints are absent"). Run **§v2.6 second** — it's the breadth check that makes §v2.3's claim robust to the "narrow task diversity" reviewer pushback. Run **§v2.4-proxy third** — valuable but diagnostic rather than verdict-shifting.

Total wall if all three run in one queue: ~75–90 min at 4 workers. Fits easily in a single overnight slot with headroom.

---

## §v2.4-alt. Body-matched compositional pair (2026-04-15)

**Status:** `INCONCLUSIVE` · n=20 · commit `0230662` · —

**Pre-reg:** [Plans/prereg_v2_4_alt.md](../../Plans/prereg_v2_4_alt.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_4_alt.yaml`
**Compute:** 7.2 min at 8 workers (20 seeds, pop=1024, gens=1500)

### Question

Is §v2.4's 0/20 driven by (a) compositional depth through `IF_GT`, (b) the `CONST_0`-at-start-of-run decode-position constraint, or (c) a proxy-predicate attractor specific to the `sum>10 AND max>5` label?

### Hypothesis (pre-registered)

If the slot-indirection mechanism extends to compositional bodies, the body-matched pair (threshold ∈ {5, 10}, otherwise identical `IF_GT`+`CONST_0`-prefix body) should behave like §v2.3 — both tasks solve at 15+/20 via a shared canonical body with `THRESHOLD_SLOT` absorbing the only variation.

### Result

| task | solve/20 | mean train | mean hold | max|gap| | BOTH |
|---|---|---|---|---|---|
| `compound_and_sum_gt_5_max_gt_5_slot`   | **17/20** | 0.994 | 0.989 | 0.0586 | — |
| `compound_and_sum_gt_10_max_gt_5_slot`  | **1/20**  | 0.919 | 0.917 | 0.1016 | — |
| — alternation BOTH (both tasks ≥ 0.999 on winner) | **1/20** (seed 2) | — | — | — | — |

Flip events: 100 total across the 20 runs, 2 zero-cost (vs 399/400 in §v2.3). Mean cost 0.020; max 0.172.

**Matches pre-registered outcome:** `INCONCLUSIVE` (mixed: one task ≥15, the other ≤3). Per the prereg decision rule, §v2.4-proxy is the queued disambiguation experiment (run this same session; see §v2.4-proxy below).

**Statistical test:** paired McNemar (seeds 0-19, alternation-BOTH vs Fmin): McNemar disagreement b=0 / c=0 (both rates are identical at 1/20 discordant-positive rate on the threshold=10 task); the asymmetry is not driven by seed-dependent pairing but by a uniform task-specific failure mode.

### Interpretation

The result falls cleanly into the INCONCLUSIVE bracket, but the *shape* of the asymmetry narrows the mechanism reading much more than the 1/20 BOTH headline suggests. Direct genotype inspection on all 20 winners (attractor classifier + per-seed decode of best-of-run tapes, 2026-04-15) shows:

- **19/19 non-BOTH seeds converge to max-based proxies.** 7/19 have an explicit `REDUCE_MAX CONST_5 GT` signature (the original §v2.4 attractor). 4/19 substitute a different constant at the same structural position (`max > c`). 8/19 are decoratively compositional — `IF_GT` plus scattered `THRESHOLD_SLOT`/`CHARS` tokens — but still score ~0.92 via a max-dominant predicate. **No novel attractor emerged**: the §v2.4 max>5 basin persists and absorbs structural variation in the surrounding tape.
- **The threshold=5 vs threshold=10 asymmetry is fully explained by proxy accuracy.** Built both tasks at seed=0 and measured `1 iff max > 5` as a standalone predictor: **100.0% on `compound_and_sum_gt_5_max_gt_5_slot`** (max > 5 is a perfect classifier because `max > 5` implies `sum > 5` for length-4 intlists over [0,9]); **92.2% on `compound_and_sum_gt_10_max_gt_5_slot`** (5 false positives from `max > 5 AND sum ≤ 10`). Evolution gets exactly to the proxy ceiling on both tasks and stops.
- **Seed 2 (the one BOTH-solve) found a non-canonical compositional route.** Its best-of-run program is not the canonical template but combines `REDUCE_MAX CONST_5 GT` with a `THRESHOLD_SLOT`-reaching sum branch through an `IF_GT` — a topologically-different AND-logic body. That the 1 success uses an alternative assembly, and the 19 failures all cluster at the same proxy, is evidence the canonical body is not especially accessible: search finds it rarely *and* finds the proxy easily.

**Decode-position is not the blocker.** The body template including `CONST_0` at the start is learnable on threshold=5 (17/20), which would be impossible if the CONST_0-prefix constraint alone were the issue. The blocker is that the proxy basin at `max > 5` outcompetes the canonical compositional body on whichever task has imperfect proxy correlation. This **sharpens** §v2.4's verdict: the failure is attractor-driven, not structurally compositional-depth-driven. See methodology principle 3 (zero-compute inspection).

### Caveats

- **Seed count:** n=20 load-bearing. Attractor-category breakdown is precision-on-one-pair, not breadth.
- **Budget limits:** pop=1024 gens=1500 matched to §v2.4 pre-reg; a §v2.4-style 4× compute scaling was not run here because the already-run §v2.4 compute-scaling follow-up showed F_AND stays at 0/20.
- **Overreach check:** the INCONCLUSIVE verdict is correctly scoped — we *cannot* claim "decode-position is not a blocker in general"; we can claim "decode-position alone does not block threshold=5, and the threshold=10 failure is driven by a proxy-predicate attractor that evolution finds reliably." The framework of "compositional depth does not scale" is partially retracted in favour of "max>5 attractor dominates on tasks where it is a near-perfect proxy."
- **Open mechanism questions:** what happens when the body template is modified to prevent `max > 5` from being an accessible sub-program (e.g., no `CONST_5` in the alphabet, or `CONST_5` made costly via tape-length pressure)? Would the proxy basin vanish and the canonical body become the basin-of-attraction? Queued as §v2.4-alt2 if this track continues.

### Degenerate-success check

Not triggered (no BOTH ≥ 18/20). The lone BOTH-solve (seed 2) was decoded per the prereg inspection commitment: **alternative compositional route**, not a slot-indirection degenerate success. No claim upgrade triggered.

### Findings this supports / narrows

- Narrows §v2.4: the "IF_GT-plus-CONST_0-prefix compositional shape is genuinely hard regardless of task" framing in the §v2.4 open question is softened — threshold=5 solves at 17/20 under that exact body shape.
- Narrows §v2.4 proxy-attractor framing: attractor dominance depends on *how close the proxy is to the true label in training*; not on compositional structure per se.

### Next steps

- §v2.4-proxy ran in the same session (see below).
- Paper-claim update: §v2.4's "does not extend to compositional depth at this compute" becomes "the max>5 proxy attractor dominates whenever max>5 is a near-perfect classifier of the training distribution; evidence for genuine compositional-depth scaling is one seed out of twenty on one body shape."

---

## §v2.4-proxy. Input-distribution decorrelation of max>5 (2026-04-15)

**Status:** `FAIL` · n=20 · commit `0230662` · —

**Pre-reg:** [Plans/prereg_v2_4_proxy.md](../../Plans/prereg_v2_4_proxy.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_4_proxy.yaml`
**Compute:** 6.9 min at 8 workers (20 seeds, pop=1024, gens=1500)

### Question

Is §v2.4's F_AND = 0/20 specifically caused by the `max > 5` proxy attractor, or will evolution find whatever proxy the input distribution provides?

### Hypothesis (pre-registered)

Decorrelating `max > 5` from the AND label (via 3-way stratified balanced sampling: P(max>5|+)=1.0, P(max>5|−)=0.5) should weaken the `max > 5`-alone predictor from ~0.92 to 0.75. If `max > 5` was specifically the barrier, F_AND rises to ≥15/20. If not, evolution finds a different proxy and the attractor story generalises.

### Result

| condition | solve/20 | mean train | mean hold | max|gap| | attractor (dominant) |
|---|---|---|---|---|---|
| `sum_gt_10_AND_max_gt_5_decorr` (this sweep) | **3/20** | 0.934 | 0.899 | 0.1016 | sum-dominated (11/17 non-solvers) |
| Reference: §v2.4 `sum_gt_10_AND_max_gt_5` (natural sampler) | 0/20 | 0.921 | 0.909 | — | `max > 5` (14/20 all seeds) |

Genotype-inspection attractor breakdown of the 17 non-solvers (decode_winner.py classify):
- `max > 5` (§v2.4 attractor): **2/17** (12%) — collapsed from 14/20 on natural sampler
- `sum`-dominant (THRESHOLD_SLOT + sum variant): **11/17** (65%)
- `max > const`-other: **1/17**
- `IF_GT`-compositional but broken: **3/17**

Single-predicate proxy accuracy on the decorrelated training distribution (seed=0, n=64):

| predictor | train | holdout |
|---|---|---|
| `max > 5` | **0.750** | 0.750 |
| `sum > 10` | **0.906** | 0.891 |
| `any cell > 6` | 0.844 | 0.797 |
| constant-1 | 0.500 | 0.500 |

**Matches pre-registered outcome:** `FAIL — proxy-story generalises`. F_AND ≤ 3/20, as pre-registered.

### Interpretation

Decorrelating `max > 5` from the AND label does what the design said it would: it moves evolution **away** from the §v2.4 attractor (from 14/20 to 2/17 among failures) — but evolution immediately finds the next-best single-predicate proxy, `sum > 10` (0.906 accuracy), and 11/17 failing seeds converge to that new attractor. The attractor-basin framing is **general**, not max>5-specific. When one cheap proxy is disabled, evolution routes to whichever single-predicate has the highest training accuracy under the current distribution.

Supplementary positive evidence: 3/20 seeds (vs 0/20 on §v2.4) found the true AND body under decorrelation, with all three scoring ≥0.977 holdout. This is small but non-zero, and genotype inspection confirms they reach a genuine AND-composition rather than a coincidental shortcut. Read: weakening the proxy signal from ~0.92 to 0.75 is **necessary but not sufficient** for compositional AND to emerge — 15/20 of the proxy pressure remains via `sum > 10` (0.91), and that is enough to trap the majority of runs.

Per methodology principle 16 ("mechanism is usually narrower than the first-pass name"): the original §v2.4 framing was "max>5 proxy attractor." The correct narrower name is "single-predicate proxy basin attractor." The specific predicate is distribution-dependent; the *phenomenon* is general under this decoder/budget. This is a meaningful renaming: it reframes §v2.4's failure as about attractor dominance under greedy search, not about compositional-body unreachability.

### Caveats

- **Seed count:** n=20 load-bearing. Within-task precision only; no breadth across label families.
- **Budget limits:** matched to §v2.4 pre-reg; attractor-swap behavior may change with different pop/gens.
- **Overreach check:** the "proxy-story generalises" wording is scope-tagged to this specific task and this specific decorrelation scheme. We have not demonstrated that evolution will find *whichever* proxy the distribution provides — only that when max>5 is weakened, the next-best single-predicate (sum>10) steps in. A stronger decorrelation test would weaken both max>5 *and* sum>10 simultaneously and see whether a novel proxy (e.g., `any cell > 6`) steps in.
- **Open mechanism questions:** under simultaneous decorrelation of max>5 and sum>10, does the `any cell > 6` attractor (0.844 accuracy under the current distribution) take over? Queued as §v2.4-proxy-2.

### Degenerate-success check

Not triggered at ≥15/20. The 3 solvers were decoded per prereg: all three found genuine AND bodies with perfect or near-perfect holdout (1.0, 1.0, 0.977), ruling out the "range-check coincidence" candidate flagged in the degenerate-success guard.

### Findings this supports / narrows

- Narrows §v2.4 attractor claim to "single-predicate proxy basin" (one level broader than "max>5 proxy").
- Supports the methodology principle that distribution-aware sampler design is a first-class experimental axis — the 3/20 vs 0/20 lift is attributable to sampler change alone.

### Next steps

- Per prereg decision rule FAIL: proxy-basin framing is general; §v2.4's structural-failure verdict stands with reinforced mechanism reading.
- Deeper test: §v2.4-proxy-2 (simultaneous decorrelation of max>5 AND sum>10) would confirm or further narrow the "any attractor will do" hypothesis. Not queued automatically; decide after paper-scope review.

---

## §v2.6. Task-diversity breadth check (2026-04-15)

**Status:** `FAIL` · n=20 per pair (+ 120-run fixed-baseline sweep) · commit `344e4de` · —

> **Prereg-fidelity note (2026-04-15, added after research-rigor retro review).** The prereg required a fixed-task baseline sweep (six tasks × 20 seeds) *before* the alternation sweeps, so that per-pair `Fmin` could be computed and the "scales vs swamped" row chosen deterministically. The baseline sweep YAML exists (`experiments/chem_tape/sweeps/v2/v2_6_fixed_baselines.yaml`) but was not executed in the initial session — only the three alternation sweeps ran. The Appendix at the bottom of this section preserves the pre-baseline provisional verdict and its reasoning trail (methodology §13). The Final update below reports the baseline sweep that was run later, on commit `344e4de`, and the verdict it produces.

**Pre-reg:** [Plans/prereg_v2_6.md](../../Plans/prereg_v2_6.md)
**Sweeps:** `experiments/chem_tape/sweeps/v2/v2_6_pair{1,2,3}.yaml` (alternation) + `experiments/chem_tape/sweeps/v2/v2_6_fixed_baselines.yaml` (baselines)
**Compute:** 21.9 min (alternation, 60 runs, 8 workers) + 12.3 min (baselines, 120 runs, 10 workers)

### Question

Does §v2.3's 80/80 BOTH on `sum_gt_{5,10}_slot` generalise to other body-invariant constant-indirection pairs, or is it specific to that pair?

### Hypothesis (pre-registered)

If the slot-indirection mechanism is a general "body-invariant-route absorbs constant variation" phenomenon, three structurally distinct pairs (string-count, wider-range sum, aggregator variant) should all pass the §v2.3 scales bar. Partial pass narrows §v2.3; null retracts.

### Result (final — with fixed baselines)

Fixed-task baselines (n=20 each, 120 runs, commit `344e4de`):

| pair | task | F_task (solve/20) | mean train | mean hold | max\|gap\| |
|---|---|---|---|---|---|
| Pair 1 (string-count) | `any_char_count_gt_1_slot` | **4/20** | 0.905 | 0.905 | 0.074 |
| Pair 1 (string-count) | `any_char_count_gt_3_slot` | **10/20** | 0.938 | 0.932 | 0.055 |
| Pair 2 (sum r12) | `sum_gt_7_slot_r12` | **20/20** | 1.000 | 0.997 | 0.027 |
| Pair 2 (sum r12) | `sum_gt_13_slot_r12` | **20/20** | 1.000 | 1.000 | 0.008 |
| Pair 3 (reduce_max) | `reduce_max_gt_5_slot` | **20/20** | 1.000 | 1.000 | 0.000 |
| Pair 3 (reduce_max) | `reduce_max_gt_7_slot` | **20/20** | 1.000 | 1.000 | 0.000 |

Per-pair verdict against the prereg outcome table (`Fmin = min(F_task_a, F_task_b)`; scales-bar = `max(Fmin − 3, 12)`; swamp pre-accept if `Fmin ≥ 19/20`):

| pair | Fmin | scales-bar | alternation BOTH | outcome row | notes |
|---|---|---|---|---|---|
| Pair 1 | 4 | 12 | 4/20 | **does-not-scale** | Alternation BOTH ≤ 5/20 per prereg table (`does-not-scale`). Alternative: `baseline-fails` triggers at min(F) ≤ 5, so Pair 1 also qualifies as baseline-fails on `any_char_count_gt_1_slot` (4/20). Both rows land the same bottom-line: pair does not support the mechanism at matched compute. |
| Pair 2 | **20** | 17 | 20/20 | **swamped** | Fmin ≥ 19/20 pre-accepts swamp. The 20/20 alternation BOTH is exactly what two independently-easy tasks produce with or without slot-indirection; the mechanism is **untested** by this pair. |
| Pair 3 | **20** | 17 | 20/20 | **swamped** | Same as Pair 2. Prereg explicitly pre-accepted this swamp for Pair 3 (line 115-117 of `prereg_v2_6.md`) because thresholds {5, 7} over [0,9] are permissive; baseline confirmed the pre-acceptance. |

**Combined verdict:** `0/3 pairs scale` → **FAIL** per prereg decision rule (line 163-165): *"§v2.3's result was pair-specific. The 'body-invariant-route absorbs constant variation' framing is retracted; the claim narrows to 'a single body-invariant pair produces 80/80.'"*

**Matches pre-registered outcome:** `FAIL` (combined-verdict row; per-pair: 1× does-not-scale, 2× swamped). The provisional "PASS — narrow-positive" reading recorded before the baselines ran was wrong: the 20/20 BOTH on Pair 2 / Pair 3 alternation looked like scaling but is indistinguishable from swamp absent the baseline. This is exactly the gap the prereg flagged (principle 21 + the scoring table): threshold-adjacent/too-clean results must be measured against baselines to pick the outcome row.

**Statistical test:** paired McNemar per pair, alternation BOTH vs Fmin on shared seeds 0..19. Pair 1: disagreement b=0 / c=0 (both 4/20). Pair 2: b=0 / c=0 (20/20 = 20/20). Pair 3: b=0 / c=0 (20/20 = 20/20). **The test is not informative on any pair — no discordant pairs to test.** This is not evidence against alternation lift; it is a degenerate condition of the test. The reason the alternation result does not support the mechanism is the per-pair outcome-row assignment (Pair 1 does-not-scale / baseline-fails; Pairs 2 and 3 swamped per prereg pre-accept), not the McNemar null.

**Training-set label balance (diagnostic required by prereg line 135).** All six tasks, seed=0, measured via `build_task(...).labels`: `p_positive = 32/64 = 0.500` on training and `128/256 = 0.500` on holdout for every task. Stratified-balanced samplers produce exactly 50/50 class balance by construction; no imbalance flag triggered for any of the six tasks.

### Interpretation

The three pairs split into two distinct failure modes, and neither supports constant-slot-indirection as an `across-family` mechanism at this budget.

**Pairs 2 and 3 are swamped.** Each task solves 20/20 at the matched budget *without* alternation pressure. Decoded winners of the fixed-task sweeps (inline script on the 120 runs, 2026-04-15) confirm this is the mechanism of the swamp: 18/20 winners for `sum_gt_7_slot_r12`, 16/20 for `sum_gt_13_slot_r12`, 14/20 for `reduce_max_gt_5_slot`, and 19/20 for `reduce_max_gt_7_slot` contain the full canonical body token set (`INPUT SUM THRESHOLD_SLOT GT` or `INPUT REDUCE_MAX THRESHOLD_SLOT GT`). Solo training on these 4-token bodies hits the body reliably. Under the prereg's swamp-row reading this means **the alternation BOTH = 20/20 results (originally read as "body-invariant-route scales") are mechanism-untested** — they are consistent with either real slot-indirection OR with two independently-easy tasks that happen to share a body coincidentally. The baselines prove the latter is sufficient, so the alternation result cannot be attributed to the mechanism.

**Pair 1 fails both the scales-bar and the baseline-fails check.** `any_char_count_gt_1_slot` solves at 4/20 solo; `any_char_count_gt_3_slot` at 10/20 solo. The body requires a 6-token chain (`INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT`) that evolution does not reliably assemble at this budget. Decoded winners show **0/20 canonical-body winners** on `any_char_count_gt_1_slot` and likewise on `any_char_count_gt_3_slot`; 8/20 and 9/20 respectively are near-canonical-missing-MAP_EQ_R (the specific step that makes the chain string-aware). The Pair-1 failure is compatible with either a search-landscape difficulty (too-long body) *or* a string-domain-specific difficulty (MAP_EQ_R chain); the current design does not separate these (noted in the initial chronicle, stands here).

**Retraction of the "body-invariant-route absorbs constant variation (across-family)" framing.** The initial (pre-baseline) reading of §v2.6 claimed "two additional body-invariant pairs reproduce §v2.3's pattern at precision" and promoted Pair 2 / Pair 3 as supporting the across-family extension of §v2.3's constant-slot-indirection claim. With baselines in: this claim is false as stated. Pair 2 and Pair 3 do not provide evidence that the slot-indirection mechanism extends to these bodies — they provide evidence that these bodies are independently easy. Methodology §20 (sampler / threshold design as dependent-variable carrier) and §21 (threshold-adjacent results require attractor-category inspection) both apply: the permissive thresholds chosen for Pair 2 (r12 range, thresholds {7, 13}) and Pair 3 (r9 range, thresholds {5, 7}) put Fmin at ceiling, which turns the scales bar into a swamp pre-accept. Rerunning these pairs with Fmin-intermediate thresholds is the redesign needed to actually test the mechanism on these body shapes.

**Mechanism rename check (principle 16, both directions).** The constant-slot-indirection entry in `findings.md` currently reads "extending the op-slot-indirection mechanism from operator variation to constant variation across at least three structurally distinct body shapes." Narrower direction: the evidence only supports the single `INPUT SUM THRESHOLD_SLOT GT` body at thresholds {5, 10} (§v2.3) — the "three body shapes" is not supported. Broader direction: is there a more general name like "threshold-slot canalisation" that would survive this retraction? No — the §v2.3 evidence is still a single pair at one body, so there is nothing broader to rename to. The correct action is narrowing to "one pair (§v2.3)".

### Caveats

- **Seed count:** n=20 per task on both alternation (60 runs) and fixed baselines (120 runs). Load-bearing, not preview.
- **Budget limits:** Pair 1 could conceivably pass the scales bar at 4× or 8× compute. Not tested here. Pair 2 / Pair 3 are at ceiling at matched compute, so compute scaling cannot rescue them — only threshold redesign can.
- **Overreach check (principle 17).** The retracted language is listed verbatim above. The revised headline uses "one body-invariant pair at precision (§v2.3)" as the load-bearing constant-indirection evidence; it does NOT say "three pairs" or "across-family." The combined-verdict table and headline below the per-experiment sections have been updated in the same commit.
- **Prereg-as-threshold-design lesson.** The prereg's own swamp-pre-accept clause for Pair 3 (line 115-117) foresaw this risk and still allowed the permissive thresholds to proceed. The lesson is to tighten threshold selection *before* committing the prereg, not after running the sweep.
- **Open mechanism questions:** (i) does Pair 2 redesigned at thresholds {e.g., 18, 24} over [0,12] — pushed onto the ascending shoulder of the sum-CDF — pass the scales bar? (ii) does Pair 3 redesigned at thresholds {e.g., 8} (single permissive) paired with {e.g., 8 on shorter r6} (structurally distinct) produce Fmin-intermediate baselines? (iii) does Pair 1 at 4× compute pass the scales bar, separating search-landscape-difficulty from mechanism-absence?

### Degenerate-success check

**Prereg-named guards (two — from `Plans/prereg_v2_6.md` section "Degenerate-success guard", lines 96-117):**

**Pair 2 range-limit trick** (prereg line 109-112: "check whether evolution exploits a range-limit trick, e.g., `any cell > 9` correlating with sum-gt-threshold under this distribution"). **Discharged — ruled out.** Decoded winners on fixed-task `sum_gt_7_slot_r12` (n=20) and `sum_gt_13_slot_r12` (n=20) show THRESHOLD_SLOT present in **20/20 and 20/20** extracted programs respectively (classify_proxy category inventory: every winner's category string contains `uses_THRESHOLD_SLOT`). Canonical-body match (full `INPUT SUM THRESHOLD_SLOT GT` token set in extracted program): 18/20 on `sum_gt_7_slot_r12`, 16/20 on `sum_gt_13_slot_r12`; the remaining seeds are near-canonical-missing-SUM (still containing THRESHOLD_SLOT). No seed's winner fits a single-predicate `any cell > c` shortcut pattern as a standalone classifier. The range-limit trick is not what evolution is doing on these tasks.

**Pair 3 aggregator swamp** (prereg outcome-table row at line 84: "**swamped** | Fmin ≥ 19/20 AND alternation BOTH in [Fmin−1, Fmin]"; additional per-pair pre-accept clause at lines 113-117, written originally for thresholds `{2,5}` which were later tightened to `{5,7}` per the prereg's "Setup" section at line 40-43 — the pre-accept logic is threshold-independent and remains valid). **Discharged — swamp confirmed.** Fmin = 20/20, alternation BOTH = 20/20. The pair provides no evidence for or against slot-indirection on this body; the outcome-table row is read, per prereg instruction, as "baseline too high to measure alternation lift."

**Mid-session concern (one — not in the original prereg; raised after §v2.4-alt/proxy landed):**

**Pair 3 max-attractor exposure** (concern that `reduce_max_gt_5` overlaps the `REDUCE_MAX CONST_5 GT` attractor family that dominated §v2.4-alt greedy search, and that 20/20 solve could be the max-attractor rather than threshold-slot-canalisation). **Discharged for the specific concern; but the point is moot for the outcome-row assignment.** Decoded winners on fixed-task `reduce_max_gt_5_slot` (n=20): 14/20 canonical-body (full `INPUT REDUCE_MAX THRESHOLD_SLOT GT`), 4/20 near-canonical-missing-REDUCE_MAX, 2/20 near-canonical-missing-THRESHOLD_SLOT. Only 1/20 has the "max_gt_5_attractor" classifier signature. THRESHOLD_SLOT is present in 18/20 winners — this is not the §v2.4-alt attractor family. The mid-session concern is discharged. But it is moot for the scales-vs-swamp decision: because Fmin = 20/20 pre-accepts swamp, neither "canonical body" nor "max-attractor" is evidence for slot-indirection when the tasks solve independently.

### Findings this supports / narrows

- **Narrows `findings.md#constant-slot-indirection`** (currently `ACTIVE`). The claim's scope tag says "n=20 per pair × 4 pairs (1 with seed expansion to n=80)" and cites §v2.6 Pair 2 and Pair 3 as 20/20 BOTH supporting evidence. With baselines: §v2.6 Pair 2 and Pair 3 are `swamped` per the prereg's own outcome table and provide no evidence for the mechanism. Only §v2.3 (one pair, 80/80) remains. **Action required: supersession pass on `findings.md#constant-slot-indirection`** — narrow scope tag to `one pair (§v2.3) at one body shape` OR retract the consolidation pending a within-Fmin-range replication on a second body. See Pass 2 (supersession mode) queued for this session.
- Does **not** narrow `findings.md#op-slot-indirection` — that entry rests on §v1.5a-binary and §v2.2, neither of which is touched by this result.
- Does **not** narrow `findings.md#proxy-basin-attractor` — that entry is about a different axis (AND-composition failure mode), not touched by this result.

### Next steps

- Per prereg FAIL decision rule: **run Pass 2 (supersession mode) on `findings.md#constant-slot-indirection`** — narrow the scope tag and update the claim sentence; add a `Narrowing / falsifying experiments` row pointing to this chronicle update.
- Queue a redesigned §v2.6' at Fmin-intermediate thresholds per the open mechanism questions above. Explicit prereg required; not auto-run.
- Pair 1 compute-scaling remains an optional follow-up if the paper-scope review wants to pin down search-landscape-vs-string-domain for the 6-token body.

### Appendix — initial provisional verdict (pre-baselines, 2026-04-15, superseded by Final Result above)

The following blocks record the chronicle's state before the fixed-baseline sweep ran. They are preserved per methodology §13 (reasoning trail is not edited when a later pass narrows a claim). The verdict in the Appendix is **not** the current chronicle verdict — see the Final Result section above.

**Appendix-initial result (alternation-only, pre-baselines):**

| pair | body | solve per task | BOTH/20 | mean train | max\|gap\| | flip zero-cost |
|---|---|---|---|---|---|---|
| Pair 1 (string-count) | `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT` | {gt_1: 4/20, gt_3: 4/20} | **4/20** | 0.90 / 0.90 | 0.074 / 0.070 | 15/100 |
| Pair 2 (sum r12)      | `INPUT SUM THRESHOLD_SLOT GT` (over [0,12])  | {gt_7: 20/20, gt_13: 20/20} | **20/20** | 1.00 / 1.00 | 0.008 / 0.000 | 100/100 |
| Pair 3 (reduce_max)   | `INPUT REDUCE_MAX THRESHOLD_SLOT GT`          | {gt_5: 20/20, gt_7: 20/20} | **20/20** | 1.00 / 1.00 | 0.000 / 0.000 | 100/100 |

**Appendix-initial matches-pre-reg:** `PROVISIONAL — likely PASS-narrow-positive pending baselines`. This reading was wrong; baselines reclassify Pair 2/3 as swamped, not scaling. Kept here verbatim.

**Appendix-initial interpretation (superseded).** Read this for the reasoning that was done before the baselines arrived, not for the current claim. The line "The mechanism is not specific to the `sum_gt_{5,10}_slot` pair" in the original interpretation is retracted; the baselines show the opposite. The "Pair 1's failure characterises the edge" reading is unchanged (Pair 1's 4/20 is still real); what changes is that there is no longer a positive Pair-2/Pair-3 result for the edge to characterise against — so Pair-1-as-edge is no longer a meaningful framing either.

**Appendix-initial caveats (superseded).** The "Overreach check: scope tag in findings.md (when promoted) must read `across-family / 3 body-invariant pairs`" language was itself an overreach; the revised Caveats section above gives the narrower claim.

**Appendix-initial degenerate-success check (incomplete).** Had three guards listed as "not yet discharged" / "cannot be evaluated" — now all three are discharged; see the Degenerate-success check section above.

**Appendix-initial findings-this-supports (superseded).** Originally said "Supports §v2.3's claim with `across-family` scope upgraded from 'one body-invariant pair' to 'three body-invariant pairs.'" The current reading (Narrows §v2.3 rather than supports; scope drops back to one pair) is in the Findings section above.

---

## §v2.6-pair1-scale. Pair 1 compute-scaling (4× pop × gens) (2026-04-15)

**Status:** `INCONCLUSIVE` · n=20 · commit `600ef20` · —

**Pre-reg:** [Plans/prereg_v2_6_pair1_scale.md](../../Plans/prereg_v2_6_pair1_scale.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_6_pair1_scale.yaml`
**Compute:** 29.6 min at 8 workers (20 seeds · pop=2048 · gens=3000 · 4× the §v2.6 Pair 1 baseline budget)

### Question

Does §v2.6 Pair 1's 4/20 BOTH at pop=1024 gens=1500 rise to ≥ 15/20 at 4× compute, mirroring scales-with-compute on simpler 4-token body-invariant pairs?

### Hypothesis (pre-registered)

If the Pair 1 baseline failure is search-landscape-limited (high epistasis around the 6-token `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT` assembly), 4× compute should close the gap. If structural at this BP_TOPK(k=3) decoder, BOTH stays near floor.

### Result

| condition | compute | F_gt_1 | F_gt_3 | **BOTH** | mean train | max\|gap\| |
|---|---|---|---|---|---|---|
| §v2.6 Pair 1 baseline | pop=1024, gens=1500 | 4/20 | 4/20 | **4/20** | 0.88 / 0.88 | 0.074 |
| §v2.6-pair1-scale (this sweep) | pop=2048, gens=3000 | 8/20 | 8/20 | **8/20** | 0.936 / 0.925 | 0.086 |

Flips: 200 total, 75 zero-cost (vs 15/100 at baseline — proportional 3× rise in alternation-stable solutions).

**Matches pre-registered outcome:** `INCONCLUSIVE` (BOTH = 8/20 ∈ [6, 9] per the pre-reg's INCONCLUSIVE row, line 83 of `prereg_v2_6_pair1_scale.md`).

**Statistical test (per prereg-promise, line 127 of prereg):** paired McNemar on shared seeds 0..19, baseline BOTH-solve vs scaled BOTH-solve. Discordants: **b=2, c=6** (2 seeds lost BOTH under scaling; 6 gained it); two-sided exact binomial **p = 0.289**. The +4 net gain is directional but not significant at α=0.05 at this n. This is weaker pairing than ideal — pop_size changes perturb the population-init RNG stream, so "shared seed" controls task data but not evolutionary trajectory.

**Training-set label balance (sanity check):** unchanged from §v2.6 Pair 1 baseline (50/50 per task). No sampler change in this experiment; Gate 20 trivially satisfied.

### Interpretation

The ADI diagnostic (see **Degenerate-success check** below) is the informative part of this result, not the 8/20 headline. At baseline: 6/20 seeds had all required tokens on tape, but only 4/20 chained them — **assembly gap = 2**, ADI = 0.10 (mild assembly barrier). At scaled compute: 8/20 seeds have all required tokens, and **all 8 chained them** — assembly gap = 0, ADI = 0.00.

This decomposes the baseline 4/20 into two additive barriers:

1. **Component-discovery barrier** (6 → 8 seeds, +2 under 4× compute): finding the full {INPUT, CHARS, MAP_EQ_R/SLOT_12, SUM, THRESHOLD_SLOT, GT} token multiset on a 32-cell tape at 6-token density is the dominant bottleneck. Scaling helps modestly but does not close it — 12/20 scaled-sweep seeds still don't carry all required tokens.
2. **Assembly barrier** (2 → 0 seeds): the "components present but not correctly chained" gap **vanishes** at 4× compute. When a scaled-sweep run discovers the token set, it reliably chains it into an executable body.

Per the prereg decision rule for INCONCLUSIVE ("run ADI diagnostic to decide between assembly-limited and mechanism-absent readings"): ADI says **neither**. The observed pattern is a third category the prereg's outcome table did not enumerate: **component-discovery-limited at tape-length / alphabet pressure** — which sits upstream of assembly and would need decoder-arm variation or tape-length extension to probe further. Per methodology principle 2 (pre-register 3-4 outcomes): the outcome table was incomplete; this category deserves a row in future pre-regs on assembly.

**Mechanism rename check (principle 16 + 16b, both directions):**
- *Narrower?* No. `body-invariant route mechanism (constant-slot variant)` is neither extended nor refuted here. The 8/20 scaled solve rate is consistent with the mechanism applying to 6-token bodies when components are discovered; the 12/20 non-solvers are upstream-of-mechanism (component set absent, not route broken).
- *Broader?* No. The result does not widen the scope beyond the NARROWED `findings.md#constant-slot-indirection` claim (one body shape, within-family).

**Pre-registered outcome match is honest INCONCLUSIVE.** The scales bar (≥ 15/20) is not met; the FAIL floor (≤ 5/20) is also not met. The result is a partial-progress signal with a specific mechanism read (component-discovery upstream of assembly) — but **without** a scope change to findings.md per the decision rule.

### Caveats

- **Seed count:** n=20 load-bearing but the McNemar pairing is degraded by pop-size-dependent RNG streams. The +4 lift is directional at p=0.29, not a statistically robust scaling signal.
- **Budget limits:** tested at 4×; no 8× or 16× run. The scaling slope (1× → 4×: +4 BOTH) does not project linearly to scales-bar attainment within a plausible budget ceiling.
- **Overreach check:** this result does NOT say "6-token bodies scale with compute" — it says "at 4× compute on this specific 6-token CHARS-chain body, BOTH rises from 4/20 to 8/20 while the assembly barrier closes and the component-discovery barrier becomes the dominant bottleneck." The decision rule for future scope-change commits to §v2.6-pair1-scale-8x (not run).
- **Open mechanism question:** would a shorter tape (length 24 instead of 32, tightening the per-cell token pressure) close the component-discovery gap? Would Arm A (direct GP, no BP_TOPK filtering) discover the components differently? Both queued as decoder-variation follow-ups under the FAIL-row decision rule in the original prereg; promoted here to "worth running even under INCONCLUSIVE" because the ADI diagnostic identifies the specific upstream bottleneck they'd probe.

### Degenerate-success check (inspection commitment from prereg)

Pre-reg required: *"If a too-clean PASS, run `decode_winner.py v2_6_pair1_scale --all` and classify each winner's body — canonical chain or alternative assembly?"* Not triggered at 8/20 (not too-clean), but the threshold-adjacency trigger per the updated skill (principle 21) applies, so inspection done:

**Winner decode on the 8 scaled-sweep BOTH-solvers (seeds 2, 3, 7, 8, 9, 10, 13, 19):** none of the 8 winners has the *contiguous substring* `INPUT CHARS SLOT_12 SUM THRESHOLD_SLOT GT` on their raw tape. The required tokens are present in each (component-presence check passes), but with interleaved tokens (SEP_A/SEP_B, NOP, DUP, CONST_*, secondary copies of the slot/aggregator) — the **permeable BP_TOPK** decoder extracts a valid executable body by skipping non-contributing cells. This is the same pattern §v2.4-alt seed 2 showed: **multiple tape-level assemblies map to the same behavioral body under BP_TOPK(k=3)**. No novel attractor category emerged; all 8 solvers reach behaviorally-equivalent bodies via tape-level assembly diversity. ADI = 0 is consistent with this: component-presence and behavioral-solve coincide because the decoder tolerates assembly scatter.

This is a subtle mechanism-level observation worth recording: the decoder's permeability (BP's "NOP passes through bonded runs" semantics, extended to top-K in BP_TOPK) **absorbs** tape-level assembly scatter and is part of why "components present ⇒ behavioral solve" holds at scaled compute. Under Arm A (direct GP, no permeability), we would expect a different picture.

### Findings this supports / narrows

- Does **not** upgrade `findings.md#constant-slot-indirection` (still NARROWED/within-family/one-pair). The INCONCLUSIVE outcome per prereg line 159 means no automatic scope upgrade.
- Narrows `findings.md#constant-slot-indirection` **Open external-validity questions** slightly: question (ii) from that entry ("does Pair 1 resolve at 4× compute?") is now answered as "partially — assembly barrier closes but component-discovery remains; scales-bar not met at 4× on a 32-cell tape." The open question reshapes rather than resolves.
- Supports the methodology-level **ADI metric** as a first-class diagnostic (methodology §21): at baseline, ADI=0.10 flagged a small assembly barrier; at scaled compute, ADI=0 shows the barrier closed — a clean decomposition of the failure mode that the aggregate BOTH-solve count alone would have missed.

### Next steps

- Per prereg decision rule (INCONCLUSIVE): report as-is; no automatic follow-up. Queued-but-optional:
  - **§v2.6-pair1-scale-8x** (pop=4096, gens=6000) — if paper needs tightening on the scaling slope.
  - **§v2.6-pair1-scale-A** (Arm A direct GP, same task, pop=1024 gens=1500) — the decoder-variation counterfactual. Would distinguish "BP_TOPK absorbs assembly scatter" from "components present implies solve under any decoder."
  - **§v2.6-pair1-tape24** (same task, tape_length=24) — would the tighter per-cell pressure close the component-discovery barrier?
- No scope change to findings.md pending.

### Prereg-promise ledger (§v2.6-pair1-scale, line-by-line against `Plans/prereg_v2_6_pair1_scale.md`)

| prereg promise | reported in chronicle | status |
|---|---|---|
| Baseline F_pair1_baseline = 4/20 BOTH at commit `0230662` | reported verbatim in Result table | ✓ |
| Threshold calibration: scales bar at ≥ 15/20 (§v2.3 bar) | used as PASS-scales criterion | ✓ |
| Sampler audit (principle 20): no change, class balance 50/50, proxy accuracy recorded | reported in Result / Caveats | ✓ |
| Statistical test: paired McNemar, one-sided α=0.05 | reported in Result (b=2 c=6 p=0.29); pairing caveat recorded | ✓ |
| Diagnostics: fixed-task solve counts, ADI per seed, winner decode on ≥0.999, trajectory plot | all reported | ✓ |
| Degenerate-success inspection on ≥15/20 outcome | not triggered at 8/20; threshold-adjacency trigger applied instead | ✓ |
| Decision rule for INCONCLUSIVE: "run ADI diagnostic" | done; ADI = 0 at scaled compute → component-discovery-limited | ✓ |
| Scope tag if PASS (upgrade to across-family / 2 body shapes) | not triggered; scope unchanged | n/a |

---

## §v2.6-pair1 follow-up sweeps. 2×2×2 of compute × tape × decoder (2026-04-15)

**Status:** three pre-registered follow-ups, each with its own status token · n=20 each · commit `c8af29d` · —

**Pre-regs:**
- [Plans/prereg_v2_6_pair1_scale_A.md](../../Plans/prereg_v2_6_pair1_scale_A.md) — Arm A counterfactual at 1× compute
- [Plans/prereg_v2_6_pair1_tape24.md](../../Plans/prereg_v2_6_pair1_tape24.md) — shorter tape at 1× compute
- [Plans/prereg_v2_6_pair1_scale_8x.md](../../Plans/prereg_v2_6_pair1_scale_8x.md) — 8× compute under BP_TOPK

**Sweeps:** `experiments/chem_tape/sweeps/v2/v2_6_pair1_{scale_A,tape24,scale_8x}.yaml`

**Compute:** scale_A ~8 min at 4-8 workers; tape24 ~45 min at 2 workers; scale_8x ~3 h at 4 workers.

### Question

The §v2.6-pair1-scale chronicle (INCONCLUSIVE, BOTH=8/20, ADI=0.00) identified a third category the original prereg did not enumerate: component-discovery-limited upstream of assembly. These three follow-ups each test a specific rescue axis independently: does Arm A direct GP outperform BP_TOPK at matched compute (decoder hypothesis)? does a tighter 24-cell tape increase canonical-component discovery (representation-pressure hypothesis)? does 8× compute alone eventually clear the scales bar under BP_TOPK on the 32-cell tape (pure-budget hypothesis)?

### Result — comparative table

| config | compute | tape | decoder | **BOTH/20** | COMP/20 | solve/20 | ADI | mean train | mean hold |
|---|---|---|---|---|---|---|---|---|---|
| Pair 1 baseline | 1× | 32 | BP_TOPK(k=3) | 4 | 6 | 4 | **+0.10** | 0.88 | 0.88 |
| tape24 | 1× | **24** | BP_TOPK(k=3) | 6 | 5 | 6 | −0.05 | 0.912 | 0.913 |
| **scale_A** | **1×** | 32 | **Arm A direct** | **7** | 7 | 7 | 0.00 | 0.920 | 0.921 |
| scale (4×) | 4× | 32 | BP_TOPK(k=3) | 8 | 8 | 8 | 0.00 | 0.931 | 0.926 |
| **scale_8x** | **16×** | 32 | BP_TOPK(k=3) | **13** | 12 | 13 | −0.05 | 0.951 | 0.955 |

Seed-overlap signatures (behaviorally-solved seeds per config):

| config | solved seeds | new vs its baseline | lost vs its baseline |
|---|---|---|---|
| Pair 1 baseline | {3, 9, 11, 17} | — | — |
| tape24 (vs baseline) | {0, 1, 2, 4, 7, 18} | {0, 1, 2, 4, 7, 18} | **{3, 9, 11, 17}** |
| scale_A (vs baseline) | {1, 3, 6, 7, 10, 17, 18} | {1, 6, 7, 10, 18} | {9, 11} |
| scale_8x (vs scale 4×) | {2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18} | {4, 11, 12, 15, 16, 17, 18} | {13, 19} |

### Matched pre-registered outcome — per sweep

**§v2.6-pair1-scale-A:** `PASS — partial help from Arm A` (verbatim prereg row: `BOTH_A in [6, 9]`). BOTH_A=7, COMP_A=7, ADI_A=0.00. Lift over baseline BOTH_BP=4 is +3 — directionally positive but below the ≥6 threshold for "PASS — Arm A rescues." Per the prereg decision rule: "record as decoder-arm evidence specific to Pair 1. No findings-level scope change without a second task family."

**§v2.6-pair1-tape24:** `FAIL — tape length is not the main barrier` (verbatim prereg row: `COMP_24 ≤ 6`). COMP_24=5, BOTH_24=6. Per the prereg decision rule: "deprioritize tape length as the main rescue axis; keep decoder and alphabet explanations in front." Directionally, BOTH does rise (4 → 6), but the prereg's decision key was `COMP` — and it dropped. Tighter tape did not materially lift canonical-component discovery.

**§v2.6-pair1-scale-8x:** `PASS — partial, still discovery-limited` — with one noted off-by-one against the prereg's strict `COMP_8x = BOTH_8x` criterion. BOTH_8x=13 (in [10,13] ✓), COMP_8x=12, ADI_8x=−0.05 (≤ 0.05 ✓). The strict equality `COMP = BOTH` is violated by 1 because one scaled-sweep seed solved behaviorally without all canonical component tokens on tape — an **alternative assembly** (permeable BP_TOPK decoder absorbing scatter), not an assembly relapse. The row's intent ("no positive assembly gap") is satisfied. **Methodology lesson noted:** future pre-regs enumerating an "assembly gap" band should use `|ADI| ≤ ε` rather than strict `COMP = BOTH`, because alternative-assembly solvers are a known chem-tape pattern (§v2.4-alt seed 2; §v2.6-pair1-scale precedent). Per the prereg decision rule: "compute helps discovery but does not close the pair. Keeps `tape24` and `scale-A` load-bearing."

### Statistical tests (per prereg-promise)

Paired McNemar, one-sided α=0.05, seeds 0..19, on BOTH-solve:

| comparison | b (lost) | c (gained) | two-sided p | one-sided p (after > before) |
|---|---|---|---|---|
| scale_A vs Pair 1 baseline | 2 {9, 11} | 5 {1, 6, 7, 10, 18} | 0.4531 | **0.2266** |
| tape24 vs Pair 1 baseline | 4 {3, 9, 11, 17} | 6 {0, 1, 2, 4, 7, 18} | 0.7539 | **0.3770** |
| scale_8x vs scale (4×) | 2 {13, 19} | 7 {4, 11, 12, 15, 16, 17, 18} | 0.1797 | **0.0898** |

**None reach α=0.05.** At n=20, BOTH-solve lifts of +3 (scale_A), +2 (tape24), and +5 (scale_8x vs 4×) are directional but statistically indistinguishable from noise under paired McNemar with this many discordants. Taken with the descriptive solved-seed overlap, the scale_8x lift is the strongest candidate (p=0.0898 one-sided, 7 gained vs 2 lost); scale_A and tape24 are noisier.

### Interpretation

Three independent reads, one methodology-level surprise.

**1. Decoder arm is a real but bounded lever.** Arm A at 1× compute (BOTH=7) roughly matches BP_TOPK at 4× compute (BOTH=8) on this task — ~8× compute saved per BOTH-solve at matched result. But the prereg's stronger "Arm A rescues" bar (BOTH ≥ 10 AND lift ≥ 6) did not trigger. **Per prereg row: PASS-partial.** The 5 new seeds unlocked by Arm A ({1, 6, 7, 10, 18}) suggest BP_TOPK has arm-specific idiosyncratic attractors; the 2 lost seeds ({9, 11}) suggest BP_TOPK has arm-specific idiosyncratic rescues. The two decoders explore partially-overlapping solution sets on this body, not a strict subset relation.

**2. Tape shortening is NOT the mechanism read earlier proposals suggested.** The prereg predicted that tighter per-cell token pressure should raise canonical-component discovery (`COMP`). Observed: COMP went **down** (6 → 5) at matched compute. BOTH went up marginally (4 → 6), entirely via **alternative-assembly solvers** — the tape24 solved-seed set {0, 1, 2, 4, 7, 18} has **zero overlap** with the baseline solved-seed set {3, 9, 11, 17}. The baseline-solved seeds all lost their solve under the tighter tape. This is a **representation-shift**, not a representation-pressure effect: shorter tapes change *which* seeds are solvable rather than raising the ceiling. A solve-count lift of +2 that comes entirely from seed-set substitution is weaker evidence than a solve-count lift of +2 that extends the baseline set; tape24's net-positive BOTH is misleading without the overlap diagnostic.

**3. Compute scaling under BP_TOPK(k=3) has positive slope, but bounded.** scale_8x at 16× compute hits 13/20, up from 8/20 at 4× (lift +5) and 4/20 at 1× (lift +9 total). The 4× → 8× McNemar (p=0.0898) is the closest to conventional significance. Gained seeds under 8× {4, 11, 12, 15, 16, 17, 18} are mostly NEW seeds, not "stabilized 4× wins" — 6 of the 8 scale-4× solvers are retained (lost {13, 19}) and 7 new seeds cross the threshold. **Per prereg row: PASS-partial, still discovery-limited.** The scales bar (≥14/20) is not cleared at 16×, so the prereg's stricter "PASS — scales with compute" row does not trigger. Pure compute under BP_TOPK(k=3) at 32-cell tape has **diminishing but positive returns** and does not cleanly close Pair 1 within a plausible budget.

**Mechanism rename check (principles 16 + 16b):** The three results together support a **decoder-aware refinement** of the constant-slot-indirection claim — the mechanism itself is not narrower or broader, but its operational scope now explicitly depends on decoder arm. Under Arm A direct GP, fewer seeds hit the component-discovery bottleneck per unit compute than under BP_TOPK(k=3). Under BP_TOPK, compute helps with diminishing returns. This is a **decoder-pair × body-shape interaction** that neither the original §v2.3 nor the §v2.6 breadth result could surface.

### Caveats

- **Pre-registered but not pre-committed to be combined.** These three were authored as three separate pre-regs (user, at commit `af0a7e5`/`c8af29d`) and run independently. The 2×2×2 comparative table is an ex-post synthesis, not a factorial experiment. The missing cells (tape24 × Arm A, tape24 × 8×, Arm A × 8×) are open.
- **All three McNemar tests fall short of α=0.05** at n=20. The scale_8x vs scale(4×) p=0.09 is the closest; scale_A and tape24 are noisy. The observed lifts are informative as mechanism hypotheses but not as statistical findings on their own.
- **Seed-overlap shifts are not additive.** tape24's solved set and baseline's solved set are disjoint; combining them naively would overstate cumulative progress. A seed-level meta-analysis across the three interventions would need a factorial sweep (or a held-out holdout seed set).
- **Overreach check:** the chronicle's proposed "decoder-aware refinement" to findings.md is a single-pair, single-alphabet, single-compute-budget observation. Scope-tag any promotion explicitly.

### Degenerate-success check

Not triggered (no BOTH ≥ 15/20). Per the prereg-required inspections:

- **scale_8x winners** (all 13 BOTH-solvers decoded via `decode_winner.py v2_6_pair1_scale_8x --all`): 12/13 have all canonical components on tape; 1/13 (the ADI=−0.05 case) is an alternative-assembly solver. No "single winner architecture dominating" signature — the 13 tapes differ substantially in token ordering while all reaching behaviorally-equivalent programs under BP_TOPK(k=3) extraction. Same pattern as §v2.4-alt seed 2 and §v2.6-pair1-scale: the permeable decoder absorbs tape-level scatter.
- **scale_A winners** (7 BOTH-solvers): all 7 have all canonical components on tape (COMP=solve=7). Under Arm A, the whole tape is the program, so token-presence is closer to program-presence. No alternative-assembly pattern here — consistent with the decoder-dependence read.
- **tape24 winners** (6 BOTH-solvers): 5/6 have all canonical components; 1/6 is alternative-assembly. This 1/6 is the seed driving the COMP=5 vs BOTH=6 mismatch. Shorter tape does not suppress the alternative-assembly phenomenon under BP_TOPK.

### Findings this supports / narrows

- **Does not upgrade** `findings.md#constant-slot-indirection` beyond its NARROWED status. The open external-validity question (ii) — "does Pair 1 resolve at higher compute?" — now has a richer partial answer: compute helps with diminishing returns under BP_TOPK(k=3); decoder arm is an additional lever of comparable size at matched compute; tape length is not the dominant axis.
- **Reshapes the open-validity section** of `findings.md#constant-slot-indirection` with a decoder-dependence note (updated inline in the commit).

### Next steps

- Per all three pre-regs' decision rules: record as axis-specific evidence for Pair 1. No automatic findings-level scope change without a second task family or body.
- The natural factorial follow-up (tape24 × Arm A × 8×) is queued but not prioritized pending a separate body-invariant 6-token pair to replicate on — see `findings.md#constant-slot-indirection` Open external-validity (i).
- Prereg formulation lesson for next cycle: use `|ADI| ≤ ε` rather than strict `COMP = BOTH` in outcome rows, to cleanly handle alternative-assembly solvers (observed three times in this session).

### Prereg-promise ledger (combined, line-by-line)

| prereg promise | reported in chronicle | status |
|---|---|---|
| (scale_A) Baseline BOTH_BP=4, COMP_BP=6, ADI_BP=0.10 | in comparative table | ✓ |
| (scale_A) Outcome row matched verbatim | `PASS — partial help from Arm A` | ✓ |
| (scale_A) McNemar one-sided α=0.05, A > BP_TOPK | reported (p=0.23) | ✓ |
| (scale_A) Decode all BOTH-solvers; report COMP_A, ADI_A, overlap | done | ✓ |
| (tape24) Baseline BOTH_32=4, COMP_32=6, ADI_32=0.10 | in comparative table | ✓ |
| (tape24) Outcome row matched verbatim | `FAIL — tape length is not the main barrier` | ✓ |
| (tape24) McNemar one-sided α=0.05, tape24 > tape32 | reported (p=0.38) | ✓ |
| (tape24) Decode all BOTH-solvers; report COMP, ADI, overlap | done | ✓ |
| (tape24) "COMP lift without BOTH lift is not a clean rescue" guard | explicitly applied: COMP went DOWN; BOTH lift came from seed-shift, not extension | ✓ |
| (scale_8x) Baseline BOTH_4x=8, COMP_4x=8, ADI_4x=0.00 | in comparative table | ✓ |
| (scale_8x) Outcome row matched verbatim | `PASS — partial, still discovery-limited` with off-by-one noted | ✓ (with methodology lesson) |
| (scale_8x) McNemar one-sided α=0.05, 8× > 4× | reported (p=0.09) | ✓ |
| (scale_8x) Decode all BOTH-solvers; report solved-seed overlap vs 4× | done | ✓ |
| Across all three: factorial cells NOT tested | noted explicitly as caveat | ✓ |

---

## §v2.7. Pair 1 partial→canonical assembly-transition rates (2026-04-15)

**Status:** `CONTROL-DEGENERATE` · n=20 per task · commit `73086c8` · —

**Pre-reg:** [Plans/prereg_pair1-transitions.md](../../Plans/prereg_pair1-transitions.md)
**Analysis:** `experiments/chem_tape/analyses/milestone_trajectories.py`
**Source data:** existing `experiments/output/2026-04-14/v2_3_fixed_baselines/` (n=40 across `sum_gt_{5,10}_slot`) and `experiments/output/2026-04-15/v2_6_fixed_baselines/` (n=120 across the six §v2.6 tasks). Zero new evolutionary compute.
**Compute:** ~10 s for milestone classification across 160 runs × up to 1500 gens each.

### Question

Is Pair 1's 4/20 failure on `any_char_count_gt_1_slot` driven by a partial→canonical assembly bottleneck — a low per-generation transition rate to canonical, and/or a local mutation-neighbor cliff at near-canonical states — relative to §v2.3's `sum_gt_5_slot` which solves 20/20 at matched compute?

### Hypothesis (pre-registered)

If landscape-level cliff: `R_P1/R_23` ≤ 0.1 AND `M_near_P1/M_near_23` ≤ 0.1 with matching paired tests. If trajectory-level: `R_P1/R_23` ≤ 0.1 only; escape rate comparable. If neither: bottleneck is elsewhere.

### Result

**Primary outcome: CONTROL-DEGENERATE (first-evaluated row, pre-committed in Plans/prereg_pair1-transitions.md line 85).** Both triggers fire on the §v2.3 `sum_gt_5_slot` control:

| trigger | criterion | observed | fires? |
|---|---|---|---|
| first-canonical-set-gen < 20 for ≥ 10/20 seeds | ≥ 10 | **15/20** | ✓ |
| avg gens-below-canonical < 50 | < 50 | **27.2** | ✓ |

**Per-prereg decision rule:** ratio-based rows (`PASS`/`PASS-partial`/`INCONCLUSIVE`) are short-circuited. No mechanism reading. No findings-level claim. Raw per-seed counts are reported for record.

### Raw per-task data (decision-rule-mandated report)

| task | n | reach canonical set | median first-canonical-set gen | median first-solve gen | R_seed mean | R_seed median | #seeds with R_seed=0 | ever reach near-canonical |
|---|---|---|---|---|---|---|---|---|
| `sum_gt_5_slot` (§v2.3 primary) | 20 | 17/20 | **0** | 6 | 0.051 | 0.000 | 12/20 | 11/20 |
| `sum_gt_10_slot` (§v2.3 secondary) | 20 | 18/20 | 3 | 12 | 0.103 | 0.006 | 9/20 | 13/20 |
| `any_char_count_gt_1_slot` (Pair 1 primary) | 20 | 10/20 | **43** | **372** | 0.006 | 0.000 | 13/20 | 11/20 |
| `any_char_count_gt_3_slot` (Pair 1 secondary) | 20 | 11/20 | 80 | 358 | 0.027 | 0.001 | 9/20 | 17/20 |

Raw (not-a-verdict) ratio for reference only: `R_P1_mean / R_23_mean` ≈ 0.006 / 0.051 ≈ **0.12** (this is division-noise under CONTROL-DEGENERATE; reported only to close the numeric loop, explicitly not to satisfy a PASS threshold).

### Interpretation (no mechanism reading under this outcome)

The §v2.3 4-token bodies are too easy: random initialization frequently (15/20 seeds) lands in canonical-set-present state within 20 generations, and the average trajectory spends only 27 generations below canonical. Under this distribution, the denominator of `R_23` is dominated by early-gen dynamics and the ratio `R_P1/R_23` is noise, as the prereg's codex reviewer pre-identified. Because the row-fire gating in the outcome table puts CONTROL-DEGENERATE first, the prereg's PASS/PASS-partial/INCONCLUSIVE rows are explicitly non-applicable.

**What the data *does* show** (reported as raw counts only, not as a mechanism reading):

- Pair 1 takes ~40× longer to first reach its canonical token-set (median 43 gens vs 0 gens on §v2.3).
- Pair 1's token_set → solve delta is 0 gens (median) — when canonical is reached, solve follows immediately. §v2.3 shows a 2-gen delta. Token-set-first-encounter is tightly coupled to behavioral solve on Pair 1 — **the bottleneck is reaching the canonical token-set at all, not chaining it after reached**. This is consistent with §v2.6-pair1-scale's ADI=0 read and §v2.6-pair1 follow-up sweeps' "component-discovery-limited" interpretation. But per the decision rule, this is chronicle observation, **not a promoted mechanism claim**.
- 13/20 Pair-1 primary seeds have `R_seed = 0` (never make a canonical-set transition in trajectory). This is the zero-dominated distribution the prereg's fallback-test protocol anticipated.

**Secondary control (`sum_gt_10_slot`) does not rescue the baseline design:** 15/20 seeds still reach canonical before gen 20 (only avg gens-below-canonical differs: 108.2 vs 27.2). CONTROL-DEGENERATE fires on both §v2.3 tasks.

### Standing diagnostic guards (all four, per prereg line 107-112)

| guard | status |
|---|---|
| **1. Classifier strictness (strict vs permissive `MAP_EQ_R` ∨ `MAP_EQ_E`)** | **Pass** (no change in outcome). Permissive classification for Pair 1 shifts one seed's near-canonical first-gen from 80 to 45 on `gt_3_slot` and the near-canonical-reaching count from 11/20 to 18/20 on `gt_3_slot`, but **does not change any outcome-row trigger** nor any `R_seed` value (R_seed is computed on canonical-set transitions, not near-canonical). Strict classification remains primary. Note: the permissive sensitivity on near-canonical counts (11 → 18) is material enough that if §v2.7' runs on a non-degenerate baseline, the sensitivity should be reported prominently. |
| **2. Stack-order invisibility (token-set → solve delta)** | **Flagged for Pair 1 (coupled)**, **pass for §v2.3 (slight decoupling)**. Pair 1 median delta = 0 gens (token-set reached ≈ solve gen). §v2.3 median delta = 2 gens (token-set reached ~2 gens before solve). The 100-gen prereg threshold for "decoupled" is not crossed by either task; stack-order invisibility is not the limiting factor on either. |
| **3. Control-degenerate (§v2.3 saturates too early)** | **FIRES** — as reported above. Primary outcome. |
| **4. Best-of-pop-trajectory scope caveat** | **Applied.** Whole analysis is best-of-pop only. Population-diversity or second-best-trajectory claims are out of scope. |

### Caveats

- **Seed count:** n=20 load-bearing but the CONTROL-DEGENERATE outcome means no statistical test is computed. Per-seed counts are the chronicle's only output.
- **Overreach check:** "Pair 1 takes ~40× longer to reach canonical set" is a **raw count observation at best-of-pop granularity on one task pair** — not a generalisable mechanism claim. The prereg's decision rule explicitly blocks any mechanism reading under CONTROL-DEGENERATE.
- **What was not done:** the expensive `mutation_neighbor_sampling.py` step (pre-reg-required only if the ratio-based rows applied). Per the decision rule's short-circuit, this saves ~200 s of CPU and ~20k one-step fitness evaluations that would have produced uninterpretable ratios.

### Degenerate-success check

Not triggered at any PASS row (no PASS row fired). The four standing diagnostic guards are reported above regardless of outcome, per the prereg's inspection commitment.

### Findings this supports / narrows

- **Does not support or narrow** `findings.md#constant-slot-indirection`. Per the prereg's downstream-commitment gate (line 169), no §v2.7 outcome promotes a claim in this pass.
- **Methodology lesson (cross-cutting):** the pre-committed CONTROL-DEGENERATE row and pre-identification of the problem from the codex spot-check paid off. The prereg's decision-rule design prevented an hour of mutation-sampling compute that would have produced uninterpretable ratios. This is an example of principle 2 (pre-register 3+ outcomes including the degenerate case) doing real work.

### Next steps

Per the prereg's CONTROL-DEGENERATE decision rule (line 171): redesign the baseline. Two concrete options:

1. **§v2.7'-a:** introduce a harder 4-token integer body where first-canonical-set reliably happens ≥ gen 50 on most seeds. Candidate: a task whose canonical body involves `CONST_1` or `CONST_2` arithmetic (e.g., `INPUT CONST_2 ADD SUM GT` with the constant absent from the baseline alphabet distribution). Requires new task builder + fixed-task sweep.
2. **§v2.7'-b:** introduce a 6-token integer body as baseline (matched body-length to Pair 1, avoiding the body-length × input-domain confound flagged in the prereg). Candidate: `INPUT CONST_5 ADD SUM CONST_5 GT` or similar.

Both options require a new sweep before §v2.7 can re-run with an interpretable baseline. No automatic queueing in this pass — deferred pending paper-scope review on whether the assembly-transition mechanism claim is worth the additional sweep budget.

### Prereg-promise ledger (§v2.7, line-by-line)

| prereg promise | reported in chronicle | status |
|---|---|---|
| Raw per-seed counts on both tasks under CONTROL-DEGENERATE | reported in Raw data table | ✓ |
| First-gen-at-each-milestone per seed | exported to `output/v2_7_milestones/per_seed_summary.json` | ✓ |
| Residence time per milestone per seed | exported | ✓ |
| Missing-token identity at near-canonical (Pair 1) | in milestones.csv via `canonical_count` column | ✓ |
| Token-set → solve delta per seed | reported in Raw data table + guard #2 | ✓ |
| Mutation-neighbor sampling | **NOT RUN** (short-circuited by CONTROL-DEGENERATE, per decision rule) | ✓ (short-circuit) |
| Statistical tests on R and M_near | **NOT RUN** (same reason) | ✓ (short-circuit) |
| All four standing guards reported | reported in Standing diagnostic guards table | ✓ |
| No findings-level claim in this pass | confirmed — no findings update | ✓ |
| Re-prereg as §v2.7' as follow-up | flagged in Next steps | ✓ |

---

## §v2.11. Arm A direct GP on §v2.3's `sum_gt_{5,10}_slot` pair (2026-04-16)

**Status:** `PASS` · n=20 (alternation) + 40 (fixed) · commit `23826da` · —

**Pre-reg:** [Plans/prereg_v2_11_arm_A_on_v2_3.md](../../Plans/prereg_v2_11_arm_A_on_v2_3.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_11_arm_A_{alt,fixed}.yaml`
**Compute:** ~5 min · 10 workers (60 runs: 20 alt + 20 fixed×2)

### Question

On §v2.3's `sum_gt_{5,10}_slot` pair — the only body where `constant-slot-indirection` is demonstrated at precision — does Arm A direct GP reproduce the BOTH-solve, or is the mechanism decoder-specific?

### Hypothesis (pre-registered)

The decoder-arm dependence caveat in `findings.md#constant-slot-indirection` is untested on the §v2.3 body. Three plausible outcomes: (1) Arm A reproduces ≈80/80 → decoder-independence on 4-token bodies, (2) Arm A materially less → §v2.3's 80/80 is partly BP_TOPK's permeability, (3) Arm A materially more → unlikely but possible.

### Result

#### Fixed-task baselines (Arm A)

| task | F (≥0.999) | stuck seeds | max holdout gap |
|------|-----------|-------------|-----------------|
| sum_gt_5_slot | 18/20 | {3, 14} at 0.516 | 0.009 |
| sum_gt_10_slot | 20/20 | — | 0.000 |

Fmin_A = 18. Δ_F vs BP_TOPK = (20+19)/2 − (18+20)/2 = 19.5 − 19.0 = 0.5 (negligible).

#### Alternation (Arm A)

| metric | Arm A (this sweep) | BP_TOPK baseline (§v2.3) |
|--------|-------------------|--------------------------|
| BOTH | **20/20** | 20/20 |
| flip_cost (mean) | **0.000** | 0.000 |
| zero-cost flips | **100/100** transitions | 100/100 |
| max train-holdout gap | **0.000** | 0.000 |
| alt_cost (Fmin − BOTH) | **−2** (alternation outperforms fixed!) | 1 |

#### Counterfactual slot-indirection test (Gate 4)

For each of the 20 BOTH-solvers: re-evaluate with the **wrong** threshold (threshold=10 on gt5 labels; threshold=5 on gt10 labels). If fitness breaks, the solve **causally depends** on THRESHOLD_SLOT.

| seed | ok_gt5 | ok_gt10 | wrong_gt5 | wrong_gt10 | verdict |
|------|--------|---------|-----------|------------|---------|
| 0 | 1.000 | 1.000 | 0.984 | 0.531 | CAUSAL |
| 1 | 1.000 | 1.000 | 0.953 | 0.609 | CAUSAL |
| 2 | 1.000 | 1.000 | 0.969 | 0.562 | CAUSAL |
| 3 | 1.000 | 1.000 | 0.969 | 0.562 | CAUSAL |
| 4 | 1.000 | 1.000 | 0.969 | 0.578 | CAUSAL |
| 5 | 1.000 | 1.000 | 0.953 | 0.562 | CAUSAL |
| 6 | 1.000 | 1.000 | 0.984 | 0.562 | CAUSAL |
| 7 | 1.000 | 1.000 | 0.953 | 0.578 | CAUSAL |
| 8 | 1.000 | 1.000 | 0.969 | 0.547 | CAUSAL |
| 9 | 1.000 | 1.000 | 0.969 | 0.531 | CAUSAL |
| 10 | 1.000 | 1.000 | 0.969 | 0.547 | CAUSAL |
| 11 | 1.000 | 1.000 | 0.953 | 0.547 | CAUSAL |
| 12 | 1.000 | 1.000 | 0.969 | 0.578 | CAUSAL |
| 13 | 1.000 | 1.000 | 0.969 | 0.516 | CAUSAL |
| 14 | 1.000 | 1.000 | 0.984 | 0.578 | CAUSAL |
| 15 | 1.000 | 1.000 | 0.953 | 0.547 | CAUSAL |
| 16 | 1.000 | 1.000 | 0.953 | 0.562 | CAUSAL |
| 17 | 1.000 | 1.000 | 0.953 | 0.562 | CAUSAL |
| 18 | 1.000 | 1.000 | 0.953 | 0.594 | CAUSAL |
| 19 | 1.000 | 1.000 | 0.969 | 0.562 | CAUSAL |

**attractor_PASS_share = 20/20 = 1.00** (prereg threshold: ≥ 0.85)

The asymmetry is mechanistically correct: swapping threshold from 10→5 on gt10 labels drops fitness to ~0.55 (threshold=5 classifies most inputs as positive, breaking gt10's label structure). Swapping 5→10 on gt5 labels drops only to ~0.96 (threshold=10 is more restrictive, so gt5's "sum>5" still mostly holds when checked at "sum>10", except for the 5<sum≤10 band).

#### Solved-seed overlap with BP_TOPK

| | BP_TOPK (§v2.3) | Arm A (this sweep) | overlap |
|---|---|---|---|
| BOTH-solve | 20/20 | 20/20 | 20/20 (perfect) |

**Matches pre-registered outcome:** `PASS — decoder-robust`. All six criteria met: BOTH_A ≥ 18 ✓, F_5_A ≥ 18 ✓, F_10_A ≥ 17 ✓, flip_cost < 0.05 ✓, alt_cost ≤ 1 ✓, attractor_PASS_share ≥ 0.85 ✓.

**Statistical test:** Paired McNemar on BOTH-solve, Arm A vs BP_TOPK, seeds 0..19: b=0, c=0, no discordant pairs. Both at 20/20 on all shared seeds.

### Interpretation

Arm A direct GP reproduces §v2.3's BOTH-solve at 20/20 with zero flip cost and zero overfit — matching BP_TOPK exactly on this 4-token body. The counterfactual test confirms that all 20 BOTH-solvers use the slot-indirection mechanism causally: swapping THRESHOLD_SLOT to the wrong task's value breaks the solve, proving the body routes through THRESHOLD_SLOT for task discrimination.

The constant-slot-indirection mechanism on the `INPUT SUM THRESHOLD_SLOT GT` body is **decoder-robust**: it works under both BP_TOPK (top-K permeable extraction) and Arm A (direct stack execution of the full 32-byte tape). This is consistent with the prereg's reading (1): on 4-token bodies, the search landscape is easy enough that decoder choice does not matter. The mechanism is a property of the body and the fitness landscape, not of the decoder.

The BOTH_A > Fmin_A anomaly (20/20 alternation vs 18/20 fixed on gt5) is worth noting: alternation appears to act as a mild curriculum/regularizer, helping the 2 stuck fixed-task seeds (3, 14) find the body. This is consistent with alternation providing search-path diversity that single-task fixed search lacks — but at n=2 stuck seeds, this is an observation, not a claim.

**Mechanism rename check (principle 16 + 16b):** (a) Is the claimed mechanism narrower than the name "decoder-robust constant-slot-indirection"? No — the counterfactual test confirms it's the same slot-indirection mechanism under both decoders. (b) Is the mechanism broader? Not from this experiment alone — this only tests the easy 4-token body. The name is accurate for this scope.

### Caveats

- **Seed count:** n=20 (load-bearing).
- **Budget limits:** matched to §v2.3 at pop=1024 gens=1500. Decoder-robustness at higher budgets untested but irrelevant — the body is at ceiling.
- **Overreach check:** decoder-robustness is demonstrated on this one body shape only. The §v2.6 Pair 1 6-token body showed decoder-arm IS a real lever (Arm A 7/20 vs BP_TOPK 4/20 at matched compute). This result does NOT extend decoder-robustness to harder bodies — it confirms the prereg's prior that "on 4-token bodies, decoder choice did not matter."
- **Open mechanism questions:** whether the mechanism is decoder-robust on harder bodies (6-token) remains the open question, addressable via Arm A × 4× compute on Pair 1.

### Degenerate-success check

**Triggered** (BOTH_A = 20/20, flip_cost = 0.000 — too-clean guard per prereg line 149).

- **Candidate: parallel per-task bodies.** RULED OUT by counterfactual test — all 20 winners break under wrong-threshold swap, proving the body uses THRESHOLD_SLOT causally (not separate per-task programs).
- **Candidate: token-as-passive-junk.** RULED OUT — same counterfactual evidence. If THRESHOLD_SLOT were in a no-effect position, swapping its value wouldn't change fitness.
- **Candidate: body-irrelevant attractor.** RULED OUT — zero holdout gap (all winners score 1.0 on both train and holdout on both tasks).

**Inspection-tooling note:** The prereg's causal-slot-indirection classifier (lines 166-193) was implemented as an automated counterfactual evaluation rather than manual classification. The counterfactual test is stronger than the prereg's manual classification plan: it directly verifies that THRESHOLD_SLOT's value is causally load-bearing, rather than relying on pattern-matching on the tape. The ~20-30 min manual classification estimate in the prereg is superseded by this ~2-min automated test.

### Findings this supports / narrows

- **Narrows:** `findings.md#constant-slot-indirection` decoder-arm dependence caveat. Per the prereg's PASS-decoder-robust decision rule: rewrite the caveat to scope decoder-dependence to Pair 1's body only. On §v2.3's 4-token body, the mechanism is decoder-robust (Arm A 20/20 with causal slot-indirection confirmed).
- **Does not affect:** `findings.md#op-slot-indirection`, `findings.md#proxy-basin-attractor`.

### Next steps

Per prereg decision rule (PASS-decoder-robust):
1. Rewrite the decoder-arm caveat in `findings.md#constant-slot-indirection` to scope decoder-dependence to Pair 1's body only. This is a caveat-narrowing pass, not a new claim promotion.
2. No new findings entry — the §v2.3 claim remains at its current scope; this just narrows one of its caveats.

### Prereg-promise ledger (§v2.11)

| prereg promise | reported in chronicle | status |
|---|---|---|
| BOTH_A, F_5_A, F_10_A raw counts | BOTH=20/20, F_5=18/20, F_10=20/20 | ✓ |
| Per-seed best-of-run fitness | in summary.json per sub-sweep | ✓ |
| Mean/max train-holdout gap | alternation: 0.000; fixed: max 0.009 | ✓ |
| Mean/max post-flip fitness drop + distribution | all 100/100 transitions zero-cost; mean=0.000 | ✓ |
| Flip-event count + zero-cost count | 100/100 zero-cost | ✓ |
| decode_winner.py on all BOTH-solvers | counterfactual test run on all 20 (stronger than manual decode) | ✓ (superseded by automated counterfactual) |
| Solved-seed overlap with §v2.3 BP_TOPK | 20/20 perfect overlap | ✓ |
| ADI per condition | not computed — uninformative at 20/20 BOTH (swamped) | ✓ (noted as swamped) |
| Paired McNemar | b=0, c=0, no discordant pairs | ✓ |
| attractor_PASS_share (Gate 4) | 20/20 = 1.00 via counterfactual test | ✓ |
| Per-task McNemar (secondary) | F_5: b=0, c=2 (Arm A loses 2 seeds); F_10: b=1, c=0 (Arm A gains 1). Descriptive only | ✓ |

---

## §v2.4-proxy-2. Simultaneous dual-proxy decorrelation on AND-composition (2026-04-16)

**Status:** `FAIL` · n=20 per arm (2 arms, 40 runs total) · commit `92b3325` · —

**Pre-reg:** [Plans/prereg_v2_4_proxy2.md](../../Plans/prereg_v2_4_proxy2.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_4_proxy2_bp_topk.yaml`, `v2_4_proxy2_arm_a.yaml`
**Compute:** ~10 min (both arms ran in parallel, 10 workers each)

### Question

When the top-2 single-predicate proxies (`max > 5` at ~0.92 and `sum > 10` at ~0.91) are simultaneously decorrelated to 0.75 in the training distribution, does evolution find genuine AND-composition, or shift to a third-best proxy?

### Hypothesis (pre-registered)

Three competing readings: (1) proxy cascade — third proxy takes over, (2) AND-composition freed, (3) collapse — sampler too aggressive. See prereg for full outcome table with 5 rows.

### Result

| condition | F_AND (≥0.999) | mean best | max best | overfit (>0.05 gap) | attractor breakdown (non-solvers) |
|-----------|---------------|-----------|----------|---------------------|----------------------------------|
| BP_TOPK single-decorr (§v2.4-proxy) | 3/20 | 0.934 | — | — | 11/17 sum>10, 2/17 max>5 |
| **BP_TOPK dual-decorr** | **0/20** | **0.840** | 0.906 | 6/20 (max 0.141) | 8/20 max_gt, 7/20 sum_gt, 4/20 IF_GT, 1/20 other |
| Arm A single-decorr (§v2.12) | 1/20 | 0.944 | — | 13/20 | 12/19 sum_gt, 4/19 max_gt |
| **Arm A dual-decorr** | **1/20** | **0.871** | 1.000 | 9/20 (max 0.117) | 9/19 sum_gt, 4/19 max_gt, 4/19 IF_GT, 2/19 other |

Proxy accuracies under the dual-decorr sampler (measured at commit `3e19e0f`, seed 0):

| proxy | accuracy |
|-------|----------|
| max > 5 | 0.750 (decorrelated ✓) |
| sum > 10 | 0.750 (decorrelated ✓) |
| sum > 15 | **0.906** (new dominant proxy) |
| any cell > 7 | 0.859 |
| max > 7 | 0.859 |
| any cell > 6 | 0.844 |

Attractor share (fraction of non-solvers in single-predicate proxy basin):
- BP_TOPK: 15/20 = 0.75 (≥ 0.50 ✓)
- Arm A: 13/19 = 0.68 (≥ 0.50 ✓)

**Matches pre-registered outcome:** `FAIL — proxy cascade (third proxy traps)`. All criteria met: F_AND_BP ≤ 3/20 ✓ (0/20), F_AND_A ≤ 3/20 ✓ (1/20), attractor_3rd ≥ 0.50 on both arms ✓.

**Statistical tests:**
- BP_TOPK dual vs single-decorr: McNemar b=0 (dual+,single−), c=3 (single+,dual−), p=0.250 (two-sided). Not significant; dual-decorr is directionally worse.
- Arm A dual vs single-decorr: McNemar b=1, c=1, p=1.000. No change.
- Cross-arm within dual-decorr: b=1 (A+,BP−), c=0. One discordant pair only.

### Interpretation

Weakening both top-2 proxies to 0.75 accuracy did not free evolution for AND-composition. Instead, evolution shifted to third-tier proxies — `sum > 15` at 0.91, `any cell > 7` at 0.86, `max > 7` at 0.86 — and the attractor-basin pattern persisted at 0.68-0.75 of non-solvers in proxy basins. The proxy cascade reading is confirmed: the trapping mechanism is not specific to `max > 5` or `sum > 10`; it operates on whichever single-predicate has the highest accuracy in the current training distribution.

The BP_TOPK arm actually **regressed** from 3/20 to 0/20 under dual-decorrelation. This is consistent with the dual-decorr sampler removing the neg_lo_lo cohort (max≤5 AND sum≤10), which may have provided a gradient signal that occasionally helped seeds reach the AND-composition body under single-decorrelation. The mean fitness dropped from 0.934 to 0.840 — the landscape is flatter, not better.

The attractor breakdown shifted compared to single-decorrelation: under single-decorr, sum>10 dominated (11/17 under BP_TOPK); under dual-decorr, the split is more even (8/20 max_gt + 7/20 sum_gt under BP_TOPK). This is consistent with both former dominant proxies being weakened, allowing a wider spread of third-tier attractors.

**Mechanism rename check (principle 16 + 16b):** (a) Is the mechanism narrower than "single-predicate proxy basin attractor"? No — the cascade from first-best to second-best (§v2.4-proxy) to third-best (this experiment) confirms the basin-shape reading is about **any** sufficiently-accurate single-predicate, not a specific one. (b) Is the mechanism broader? Possibly — the ~0.85-0.91 accuracy range of third-tier proxies is lower than the original ~0.92. The trapping threshold may be lower than the "≥ ~0.90" in the current claim. The data supports broadening to "≥ ~0.85" as the approximate trapping floor, but this is a single data point (one dual-decorr condition); further narrowing would require a sampler that eliminates all ≥0.85 proxies.

### Caveats

- **Seed count:** n=20 per arm (load-bearing).
- **Overfit:** 6/20 BP_TOPK seeds and 9/20 Arm A seeds exceed 0.05 train-holdout gap. The overfit under dual-decorr is moderate but widespread, similar to §v2.12's decorr sub-sweep (13/20). The 1/20 Arm A solver (seed 7, holdout 0.980) is clean.
- **Overreach check:** the "any ≥~0.85 proxy traps" reading is directional, not a precise threshold claim. The third-tier proxies cluster at 0.84-0.91; we cannot distinguish "≥0.85 traps" from "≥0.90 traps on a flatter landscape."
- **Sampler design caveat:** the dual-decorr sampler removes neg_lo_lo examples entirely, which may have collateral effects on the fitness landscape beyond proxy-decorrelation. The BP_TOPK regression (3→0) could partly reflect this collateral rather than pure proxy-cascade.
- **Open mechanism questions:** (i) A sampler that eliminates ALL single-predicates above 0.80 would be the definitive test — but may require a different input domain (length-4 [0,9] may not support such a sampler). (ii) The IF_GT-containing non-solvers (4/20 on each arm) could be proto-compositional bodies that failed to complete AND-assembly — inspection of these would clarify whether the landscape has more compositional structure under dual-decorr than single-decorr.

### Degenerate-success check

Not triggered — result is FAIL direction (0/20 and 1/20 solves).

- **Too-clean FAIL candidate (identical attractor to single-decorr):** NOT observed. Attractor distribution shifted (more spread across max_gt + sum_gt + IF_GT), unlike the concentrated sum>10 dominance under single-decorr. The dual-decorr sampler did change the landscape, just not enough to free AND-composition.
- **Arm A seed 7 solver:** holdout = 0.980 (not 1.0). Verified as close-to-genuine AND. This is the only solver across both arms — too thin to be a degenerate-success concern.

### Findings this supports / narrows

- **Broadens:** `findings.md#proxy-basin-attractor`. Per prereg decision rule (FAIL — proxy cascade → principle 16b): the "≥ ~0.90 accuracy" language in the claim should be relaxed. The proxy-basin trapping persists when the top-2 proxies are weakened to 0.75, as long as third-tier proxies at ~0.85-0.91 remain available. The claim broadens from "whenever a ≥ ~0.90-accurate single-predicate exists" toward "whenever a ≥ ~0.85-accurate single-predicate exists."
- **Adds evidence for decoder-generality:** both BP_TOPK and Arm A show the same cascade pattern, consistent with §v2.12's decoder-general finding.

### Next steps

Per prereg decision rule (FAIL — proxy cascade):
1. **Principle 16b broadening pass on `findings.md#proxy-basin-attractor`:** relax "≥ ~0.90" in claim sentence to "≥ ~0.85" (approximate; single data point). Add this experiment to Supporting experiments. Update scope boundary.
2. **No further proxy-decorrelation experiments auto-queued.** The cascade pattern suggests diminishing returns from sampler-only interventions on this task family. A fundamentally different approach (different input domain, different composition structure, multi-objective) would be needed to test whether proxy basins can be fully eliminated.

### Prereg-promise ledger (§v2.4-proxy-2)

| prereg promise | reported in chronicle | status |
|---|---|---|
| F_AND_BP, F_AND_A at 0.999 and 0.95 | 0.999: reported (0/20, 1/20). 0.95: BP_TOPK 0/20, Arm A 3/20 (from fitness values) | ✓ |
| Per-seed best-of-run fitness | in sweep output per seed | ✓ |
| Mean and max train-holdout gap | BP_TOPK: 6/20 overfit, max 0.141; Arm A: 9/20, max 0.117 | ✓ |
| Attractor breakdown per arm | reported in Result table | ✓ |
| Solved-seed overlap: dual vs single-decorr | BP_TOPK: 0 overlap (dual {}, single {0,11,16}). Arm A: 0 overlap (dual {7}, single {13}) | ✓ |
| Solved-seed overlap: BP_TOPK vs Arm A within dual-decorr | BP_TOPK {}, Arm A {7}. Disjoint (trivially, BP_TOPK has 0 solvers) | ✓ |
| Per non-solver dominant proxy classification | reported as heuristic category breakdown. Per-seed predicate accuracy not computed (deferred — heuristic classifier sufficient for FAIL verdict) | ✓/deferred |
| Class balance verification | 0.500 on all seeds (confirmed by task builder design: 32/64 positives) | ✓ |
| McNemar per arm vs baseline | reported: BP_TOPK p=0.250, Arm A p=1.000 | ✓ |
| McNemar cross-arm | reported: b=1, c=0 | ✓ |

---

## §v2.4-proxy-3. Split-halves AND proxy-basin boundary sweep (2026-04-16)

**Status:** `INCONCLUSIVE` · n=20 per arm per threshold (6 sub-sweeps, 120 runs total) · commit `b5ffbd4` · —

**Pre-reg:** [Plans/prereg_v2_4_proxy3_boundary.md](../../Plans/prereg_v2_4_proxy3_boundary.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_4_proxy3_gt{6,7,8}_{bp_topk,arm_a}.yaml`
**Compute:** ~15 min (6 sweeps in parallel, 5 workers each)

### Question

At what single-predicate proxy accuracy does the proxy-basin attractor stop trapping greedy evolution? Does a split-halves AND task with independent conjuncts and population-level best proxy at ~0.79-0.86 escape the basin?

### Hypothesis (pre-registered)

Three thresholds tested as a gradient: >6 (population best proxy ~0.79), >7 (~0.81), >8 (~0.86). Crossed with BP_TOPK and Arm A. See prereg for 5 combined-gradient outcome rows.

### Result

| threshold | arm | F_AND | mean best | ≥0.95 | overfit (>0.05) |
|-----------|-----|-------|-----------|-------|-----------------|
| >6 | BP_TOPK | **0/20** | 0.502 | 0/20 | 12/20 |
| >6 | Arm A | **0/20** | 0.536 | 0/20 | 11/20 |
| >7 | BP_TOPK | **0/20** | 0.500 | 0/20 | 12/20 |
| >7 | Arm A | **0/20** | 0.520 | 0/20 | 10/20 |
| >8 | BP_TOPK | **0/20** | 0.500 | 0/20 | 12/20 |
| >8 | Arm A | **0/20** | 0.500 | 0/20 | 11/20 |

**0/120 solvers across all 6 conditions.** No seed reaches ≥0.95 fitness. Mean fitness ~0.50 across all conditions (constant-output territory on balanced 50/50 task).

**Matches pre-registered outcome:** All three thresholds match the per-threshold **COLLAPSE** row: "F_AND ≤ 2/20 AND mean best < 0.80." Combined verdict: **All COLLAPSE** — not covered by any explicit combined-gradient row. Closest match: "All TRAP" row from the prereg, but the mechanism is different (collapse, not proxy-basin trapping).

**Statistical tests:** Not computed — all conditions at 0/20; no discordant pairs exist for McNemar.

### Interpretation

This is not proxy-basin trapping. The mean fitness of ~0.50 on a balanced task means evolution is stuck at constant-output programs, not converging to a single-predicate proxy. The signature of proxy-basin trapping is mean fitness ≥0.85 with the best-of-run converging to a recognizable predicate (as in §v2.4 at 0.92 mean, §v2.4-proxy at 0.93, §v2.4-proxy-2 at 0.84-0.87). Here, evolution cannot even discover that the input carries learnable signal.

The root cause is **search-space expansion with novel tokens.** The `v2_split` alphabet has 24 tokens (vs v2_probe's 22). The required compositional body is 9 tokens: `SUM_LEFT2 THRESHOLD_SLOT GT SUM_RIGHT2 THRESHOLD_SLOT GT ADD CONST_1 GT`. Each of `SUM_LEFT2` and `SUM_RIGHT2` appears at only 1/24 ≈ 4.2% frequency per random tape position. The probability of assembling even a partial body with both novel tokens in useful positions is extremely low at pop=1024 × gens=1500.

**Verification that the task IS solvable:** The handcrafted 9-token body scores 1.000 on both train and holdout for all three thresholds. The task is perfectly learnable — evolution just cannot find the body at this budget with this alphabet size.

**Mechanism rename check (principle 16 + 16b):** (a) Is "search-space expansion failure" narrower than this name? No — the description matches. (b) Is it broader? Possibly — the failure could be specific to the 9-token body length and 2-new-token rarity, not general to any novel-token introduction. The name should be scoped: "search-space expansion failure at 9-token body with 2 novel tokens in 24-token alphabet."

### Caveats

- **Seed count:** n=20 per arm per threshold (load-bearing).
- **Budget limits:** pop=1024 × gens=1500 may be insufficient for this body. Higher compute could rescue — but this is the same budget used for all prior experiments, so the comparison is fair.
- **Overreach check:** this result says NOTHING about the proxy-basin trapping threshold. The experiment was designed to probe the ~0.80 proxy boundary, but it failed for reasons unrelated to proxies (novel-token discovery). The proxy-basin claim in findings.md is neither narrowed nor broadened by this result.
- **Design limitation (acknowledged pre-run in prereg):** per-seed proxy variance at n=64 was flagged as a concern, but the actual failure mode was more fundamental — evolution never got far enough to encounter ANY proxy.
- **Open question:** could a seeded-initialization strategy (injecting a few tapes containing SUM_LEFT2/SUM_RIGHT2) bootstrap discovery? Or does the body require too many interdependent tokens for mutation-crossover to assemble at any reasonable budget?

### Degenerate-success check

Not triggered — no solvers exist.

### Findings this supports / narrows

- **Does not affect** `findings.md#proxy-basin-attractor`. The proxy-basin claim stands as-is. This experiment failed to test the boundary because of a search-space confound (novel-token discovery), not because the proxy-basin claim is wrong. The "≥~0.85" trapping threshold remains the best estimate from prior experiments.
- **Methodology lesson:** testing a proxy-accuracy boundary requires holding the search difficulty constant. Introducing new tokens changes the search landscape so dramatically that the proxy question is confounded. Future attempts to test the boundary should use tokens already present in the alphabet (e.g., repurposing existing reducers on a different input domain, or using the existing v2_probe alphabet on longer inputs).

### Next steps

Per prereg decision rule (all COLLAPSE): the split-halves approach at this budget is uninformative for the proxy-threshold question. Two paths forward:

1. **Same task, higher compute:** test split_and_gt6 at 4× or 16× compute to see if the body eventually emerges. This separates "body is undiscoverable" from "body is hard but reachable."
2. **Different approach entirely:** instead of adding new tokens, test the proxy boundary on the **existing** v2_probe alphabet by using a longer input domain ([0,9]^8 or [0,3]^8) where whole-list SUM and REDUCE_MAX still work but the correlation structure is weaker. This avoids the novel-token confound.
3. **Seeded initialization:** inject a few handcrafted tapes containing the target body into the initial population and test whether evolution can maintain/improve them. This would test whether the body is *maintainable* (selection can preserve it once found) even if *discoverable* is hard.

### Prereg-promise ledger (§v2.4-proxy-3)

| prereg promise | reported in chronicle | status |
|---|---|---|
| F_AND per arm per threshold at 0.999 and 0.95 | 0/20 at 0.999 on all 6 conditions; 0/20 at 0.95 on all 6 | ✓ |
| Per-seed best-of-run fitness | in sweep output; mean ~0.50 across all | ✓ |
| Mean and max train-holdout gap | reported as overfit counts (10-12/20 per condition) | ✓ |
| Attractor breakdown per arm per threshold | **NOT COMPUTED** — all seeds at ~0.50 (constant-output); attractor classification is uninformative when no predicate is discovered | ✓ (short-circuited by COLLAPSE) |
| Whether solvers use SUM_LEFT2/SUM_RIGHT2 | N/A — no solvers exist | ✓ (vacuously) |
| Per-seed proxy accuracy on training data | **NOT COMPUTED** — deferred; uninformative when evolution doesn't reach any predicate | deferred |
| McNemar per arm | N/A — all at 0/20; no discordant pairs | ✓ (vacuously) |
| Gradient analysis across thresholds | COLLAPSE across all three — no gradient signal | ✓ |

---

## §v2.13. BP_TOPK(k=5) parameter sweep on §v2.3 and §v2.6 Pair 1 (2026-04-16)

**Status:** `INCONCLUSIVE` · n=20 per sub-sweep (4 sub-sweeps, 80 runs total) · commit `1cfe7d5` · —

**Pre-reg:** [Plans/prereg_v2_13_k5_sweep.md](../../Plans/prereg_v2_13_k5_sweep.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_13_k5_v2_3_{alt,fixed}.yaml`, `v2_13_k5_pair1_{alt,fixed}.yaml`
**Compute:** ~30 min · 10 workers (4 sub-sweeps × 20 seeds)

### Question

Within the BP_TOPK decoder family, does increasing `topk` from 3 to 5 change BOTH-solve rate, ADI, and solved-seed identity on (a) §v2.3's 4-token body and (b) §v2.6 Pair 1's 6-token body?

### Hypothesis (pre-registered)

Three competing readings: (1) wider k absorbs more tape scatter (helps), (2) wider k dilutes selection pressure (hurts), (3) null (k saturated at 3). See prereg for full outcome table.

### Result

#### §v2.3 pair (4-token body: `INPUT SUM THRESHOLD_SLOT GT`)

| condition | BOTH | F_5 | F_10 | flip_cost | overfit seeds | holdout gap (max) |
|-----------|------|-----|------|-----------|---------------|-------------------|
| k=3 baseline (§v2.3) | 20/20 | 20/20 | 19/20 | 0.000 | 0/20 | 0.016 |
| k=5 (this sweep) | 20/20 | 20/20 | 19/20 | 0.000 | 0/20 | 0.016 |

Same stuck seed (5) under both k values. Zero discordant pairs. Seed-level behavior identical.

**Per-pair verdict: NULL — k saturated at 3.** |Δ_BOTH| = 0, |Δ_ADI| = 0.

#### §v2.6 Pair 1 (6-token body: `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT`)

| condition | BOTH | F_gt1 | F_gt3 | ADI | overfit seeds |
|-----------|------|-------|-------|-----|---------------|
| k=3 baseline (§v2.6) | 4/20 | 4/20 | 10/20 | 0.10 | — |
| k=5 alternation | 5/20 | 5/20 | 5/20 | 0.10 | 2/20 (max gap 0.086) |
| k=5 fixed gt_1 | — | 6/20 | — | — | 3/20 (max gap 0.086) |
| k=5 fixed gt_3 | — | — | 5/20 | — | 1/20 (max gap 0.070) |

**Per-pair verdict: INCONCLUSIVE — small directional lift.** Δ_BOTH = +1, |Δ_ADI| = 0.00, McNemar p = 1.000.

#### Seed overlap (Pair 1 BOTH-solvers, shared seeds 0..19)

| | k=3 solves | k=5 solves | overlap | k=3 only | k=5 only |
|---|---|---|---|---|---|
| seeds | {3, 9, 11, 17} | {2, 3, 9, 10, 16} | {3, 9} | {11, 17} | {2, 10, 16} |

60% of the combined solver set is disjoint. k=5 unlocks a different seed subset rather than extending k=3's set — consistent with decoder-parameter × body-shape non-additive interaction (principle 9).

#### ADI (assembly difficulty index)

- k=5 Pair 1: COMP=7, BOTH=5, gap=2, ADI=0.10 (mild assembly barrier)
- k=3 Pair 1 baseline: COMP=6, BOTH=4, ADI=0.10
- Δ_ADI = 0.00

#### Combined verdict

§v2.3 = NULL, Pair 1 = INCONCLUSIVE-small → per prereg combined grid: **DEFAULT INCONCLUSIVE**.

**Matches pre-registered outcome:** `DEFAULT INCONCLUSIVE` (§v2.3 NULL × Pair 1 INCONCLUSIVE-small falls into the catch-all row of the combined-verdict grid).

**Statistical test:** McNemar on §v2.3: no discordant pairs, p=1.000. McNemar on Pair 1: b=3 (k5+,k3−), c=2 (k3+,k5−), p=1.000 (two-sided).

### Interpretation

The §v2.3 4-token body is completely insensitive to k at {3, 5} — identical seed-level outcomes, same stuck seed, same flip-cost signature. This is pure NULL: k is a saturated parameter on this body at this budget.

On Pair 1, the aggregate BOTH barely moves (+1), but the **per-task fixed baselines tell a more interesting story**: F_gt1 rises modestly (+2, from 4 to 6) while F_gt3 collapses sharply (−5, from 10 to 5). Under k=3, 6 seeds solved gt_3 but not gt_1 (the "gt_3-only solver" phenotype); under k=5, this category is completely empty — F_gt1 = F_gt3 = BOTH = 5 on alternation. Wider k appears to have **eliminated the gt_3-only solver phenotype**, consistent with prereg reading (2): wider extraction window dilutes selection pressure for canonical-body assembly, and the harder-to-assemble task (gt_1, requiring the full 6-token chain) is disproportionately affected.

The 60% seed-set disjointness is consistent with k changing which seed-level landscapes are navigable, not uniformly helping or hurting. k is a body-shape-dependent lever, not a global hyperparameter improvement.

### Caveats

- **Seed count:** n=20 per sub-sweep (load-bearing).
- **Budget limits:** matched to baselines at pop=1024 gens=1500. k sensitivity at higher budgets untested.
- **Overreach check:** no claim about k=5 being better or worse — the result is NULL on §v2.3 and INCONCLUSIVE on Pair 1. The F_gt3 collapse is a mechanistic observation, not a verdict.
- **Open mechanism questions:** COMP/ADI computation uses the heuristic token-set classifier; per-seed winner decode for the 5 BOTH-solvers would confirm whether they use the same canonical body as k=3 solvers.
- **Deferred diagnostics:** ADI trajectories (per-generation history) not computed — marked deferred per prereg diagnostics section.

### Findings this supports / narrows

- Does not support or narrow any `findings.md` entry. Per the prereg decision rule, DEFAULT INCONCLUSIVE triggers no findings change.
- **Note for `findings.md#constant-slot-indirection` Open external-validity questions:** k is a body-shape-dependent axis, not a global improvement direction. The §v2.3 body is saturated at k=3; the Pair 1 body shows phenotype-mix changes without BOTH improvement. Future preregs on this body need not test k variation unless body shape changes substantially.

### Next steps

Per prereg decision rule: report as parameter-saturation evidence on §v2.3 and phenotype-mixing evidence on Pair 1. No findings change. The k-axis question is effectively closed for these two body shapes at this budget.

The F_gt3 collapse is interesting enough to warrant a one-paragraph note in the §v2.6 Pair 1 follow-up context but does not merit a standalone follow-up experiment. If a future body design is sensitive to extraction-window width, k could be revisited.

### Prereg-promise ledger (§v2.13)

| prereg promise | reported in chronicle | status |
|---|---|---|
| BOTH_5, F_a_5, F_b_5 per pair | reported in Result tables | ✓ |
| COMP_5, ADI_5 per pair | reported in ADI section (Pair 1: COMP=7, ADI=0.10; §v2.3: swamped) | ✓ |
| Per-seed best-of-run fitness | in summary.json per sub-sweep | ✓ |
| Per-seed train, holdout, gap | in summary.json; overfit seeds reported | ✓ |
| Solved-seed overlap with k=3 | reported in Seed overlap table | ✓ |
| McNemar per pair | reported: §v2.3 p=1.000, Pair 1 p=1.000 | ✓ |
| Mean/max post-flip fitness drop | §v2.3: 0.000; Pair 1: not computed (deferred — low priority given INCONCLUSIVE) | ✓/deferred |
| Per BOTH-solver winner decode + attractor classification | **NOT RUN** — deferred; low priority given DEFAULT INCONCLUSIVE verdict | deferred |
| ADI trajectories per pair | **NOT RUN** — deferred per prereg ("defer if too expensive") | deferred |
| Seeds with COMP=1 AND BOTH=0 | Pair 1: 2 seeds (gap=2) | ✓ |

---

## §v2.12. Arm A direct GP on §v2.4 proxy-basin tasks (2026-04-16)

**Status:** `FAIL` · n=20 per sub-sweep (2 sub-sweeps, 40 runs total) · commit `1cfe7d5` · —

**Pre-reg:** [Plans/prereg_v2_12_arm_A_on_proxy_basin.md](../../Plans/prereg_v2_12_arm_A_on_proxy_basin.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_12_arm_A_v2_4_natural.yaml`, `v2_12_arm_A_v2_4_decorr.yaml`
**Compute:** ~12 min · 10 workers (2 sub-sweeps × 20 seeds)

### Question

Is `findings.md#proxy-basin-attractor` (single-predicate proxy basins dominate greedy search under BP_TOPK whenever a ≥~0.90-accurate single-predicate exists) decoder-specific to BP_TOPK, or is it a general property of greedy search under any chem-tape decoder?

### Hypothesis (pre-registered)

Two competing readings: (1) BP_TOPK-specific — Arm A escapes because proxy basins are stabilized by permeability; predicted F_AND_A ≥ 10/20 on both samplers. (2) Decoder-general — proxy dominance is a property of greedy fitness with cheap proxies, not the decoder; predicted F_AND_A ≤ 3/20 natural, ≤ 5/20 decorr.

### Result

| condition | F_AND (≥0.999) | mean best | max holdout gap | overfit seeds (>0.05) | attractor breakdown (non-solvers) |
|-----------|---------------|-----------|----------------|----------------------|----------------------------------|
| BP_TOPK natural baseline (§v2.4) | 0/20 | 0.921 | — | — | 14/20 max>5, 6/20 partial |
| **Arm A natural** | **0/20** | 0.922 | 0.078 | 3/20 | 10/20 max_gt_5, 6/20 sum_gt, 4/20 other |
| BP_TOPK decorr baseline (§v2.4-proxy) | 3/20 | — | — | — | 2/17 max>5, 11/17 sum>10 |
| **Arm A decorr** | **1/20** | 0.944 | 0.102 | 13/20 | 12/19 sum_gt, 4/19 max_gt_5, 3/19 other |

Δ_natural = 0 (both at 0/20). Δ_decorr = −2 (Arm A worse: 1/20 vs 3/20).

**Attractor share (fraction of non-solvers in single-predicate proxy basin):**
- Natural: 16/20 = 0.80 (prereq: ≥ 0.50 ✓)
- Decorr: 16/19 = 0.84 (prereq: ≥ 0.50 ✓)

**Matches pre-registered outcome:** `FAIL — proxy-basin is decoder-general`. All four criteria met: F_AND_A_natural ≤ 3/20 ✓, F_AND_A_decorr ≤ 5/20 ✓, attractor_share_natural ≥ 0.50 ✓, attractor_share_decorr ≥ 0.50 ✓.

**Statistical test:** Not computed — both conditions have 0 or 1 discordant pairs vs baseline; McNemar is uninformative at this solve count. Descriptive comparison only.

### Interpretation

Arm A direct GP is trapped by the same single-predicate proxy basins as BP_TOPK. On the natural sampler, 0/20 Arm A seeds solve the AND task, matching BP_TOPK exactly. On the decorrelated sampler, 1/20 (vs BP_TOPK's 3/20) — if anything, Arm A is slightly worse, not better.

The attractor breakdown under Arm A mirrors BP_TOPK's pattern: natural-sampler winners converge to `max > 5` (10/20 under Arm A vs 14/20 under BP_TOPK); decorr-sampler winners shift to `sum > 10` variants (12/19 under Arm A vs 11/17 under BP_TOPK). The attractor-switch post-decorrelation — the signature that named the basin mechanism in §v2.4-proxy — reproduces under a completely different decoder.

This means the proxy-basin attractor is not an artifact of BP_TOPK's permeability or extraction logic. It is a property of **greedy fitness search with cheap single-predicate proxies**, period. The decoder determines how the genome encodes the proxy program (tape extraction vs direct execution), but the evolutionary dynamics — convergence to the cheapest ≥0.90-accurate predicate, robustness to compute scaling (§v2.4 4×), attractor-switching under decorrelation — are decoder-invariant.

### Caveats

- **Seed count:** n=20 per sub-sweep (load-bearing).
- **Overfit concern (decorr sub-sweep):** 13/20 seeds (65%) exceed 0.05 train-holdout gap, mean gap 0.052, max 0.102. This is systematic and notably higher than the natural sub-sweep (3/20). At n_examples=64 with holdout_size=256 this is moderate but widespread — most decorr seeds are memorizing slightly. The 1/20 solve on the decorr sub-sweep should be interpreted cautiously (holdout for that seed is 1.0, so the solve itself is clean, but the surrounding non-solver population has noisy fitness).
- **Sampler audit (principle 20) — post-hoc flag:** The prereg triggered principle 20 and required a sampler audit on seeds {0, 1, 2} before the sweep ran. **This audit was not run pre-sweep.** Post-hoc audit results at current commit:
  - Natural sampler: all three seeds pass prereg criteria (class balance 0.500, max proxy ≥ 0.85: seed 0 = 0.922, seed 1 = 0.922, seed 2 = 0.859).
  - Decorr sampler: seed 0 max_proxy = 0.938, marginally exceeding the prereg's ≤ 0.93 threshold (breach = 0.008). Seeds 1 (0.922) and 2 (0.891) pass. The dominant proxy shifted from `max_gt_5` (§v2.4-proxy reference) to `sum_gt_15` — different proxy but same class of single-predicate attractor.
  - **Assessment:** The 0.008 breach on 1/3 seeds does not indicate task-builder semantic change (the prereg's stated HALT concern). The attractor pattern is consistent with the §v2.4 baseline. However, this audit was post-hoc, not pre-sweep as required. Noted as a prereg-fidelity flag; does not block the FAIL verdict (which depends on solve counts and attractor shares, not sampler thresholds) but should be discharged before any findings-level promotion.
- **Overreach check:** this experiment extends the proxy-basin scope tag to "decoder-general" on the tested pair. It does NOT establish decoder-generality for other AND-composition tasks, other proxy types, or other input distributions.
- **Open mechanism questions:** (i) Does simultaneous decorrelation of both `max > 5` and `sum > 10` free either decoder? (§v2.4-proxy-2, not yet pre-registered.) (ii) Does a non-AND composition family (OR, XOR) show the same basin behavior?

### Degenerate-success check

Not triggered — result is FAIL direction (0/20 and 1/20 solves). The too-clean FAIL candidate (identical attractor breakdown to BP_TOPK) is partially observed: natural-sampler shows 10/20 max_gt_5 under Arm A vs 14/20 under BP_TOPK — similar but not identical. The attractor-switching pattern (decorr shifts to sum_gt) does reproduce, which is the mechanistically important signal.

### Findings this supports / narrows

- **Broadens:** `findings.md#proxy-basin-attractor`. Per prereg decision rule (FAIL — decoder-general → principle 16b broadening pass): the current scope caveat "Tested only at BP_TOPK(k=3, bp=0.5); other arms not characterised" updates to "Tested at BP_TOPK(k=3, bp=0.5) and Arm A direct GP; both trap." The claim sentence itself does not change (already decoder-general in form: "evolution under BP_TOPK reliably converges..." → the sentence should be updated to remove the "under BP_TOPK" qualifier). The mechanism name `single-predicate proxy basin attractor` should NOT reference decoder — the basin is a property of greedy fitness search with cheap proxies, not a decoder artifact.
- **Does not affect:** `findings.md#constant-slot-indirection` or `findings.md#op-slot-indirection`.

### Next steps

Per prereg decision rule:
1. **Principle 16b broadening pass on `findings.md#proxy-basin-attractor`:** update the scope tag from "under BP_TOPK greedy search" to "under greedy search at this budget (decoder-general: BP_TOPK and Arm A both trap)." Add this experiment as a row in "Supporting experiments." Update the scope-boundary bullet "Tested only at BP_TOPK" to "Tested at BP_TOPK and Arm A."
2. **Queue:** §v2.4-proxy-2 (simultaneous decorrelation of top-2 proxies, crossed with both decoders) is the highest-value next experiment on the proxy-basin track — per codex review recommendation.
3. **Deferred:** findings-promotion of the broadened scope tag is gated on discharging the principle-20 sampler audit flag above.

### Prereg-promise ledger (§v2.12)

| prereg promise | reported in chronicle | status |
|---|---|---|
| F_AND_A_natural, F_AND_A_decorr at 0.999 AND 0.95 thresholds | 0.999: reported (0/20, 1/20). 0.95 threshold: natural 3/20, decorr 14/20 (from summary.json seeds_ge_0.95) | ✓ |
| Per-seed best-of-run fitness | in summary.json per sub-sweep | ✓ |
| Mean and max train-holdout gap | natural: mean 0.016, max 0.078; decorr: mean 0.052, max 0.102 | ✓ |
| Attractor breakdown per sub-sweep | reported in Result table and Interpretation | ✓ |
| Solved-seed overlap with BP_TOPK | natural: 0/20 vs 0/20 (trivially identical). Decorr: Arm A seed 13 solves; BP_TOPK seeds {2, 3, 8} solved — disjoint | ✓ |
| Single-predicate proxy accuracies on seed=0 | **DEFERRED** — sampler audit run post-hoc, not as a per-run diagnostic. Values reported in Caveats section | deferred (post-hoc) |
| Per non-solver: extracted predicate accuracy | **NOT COMPUTED** — the heuristic classifier in decode_winner.py reports category, not per-seed predicate accuracy. Deferred as infrastructure gap (same as §v2.11 classifier limitation) | deferred |
| Sampler-design audit (principle 20) | **RUN POST-HOC** — not pre-sweep as required. Results reported in Caveats section. Marginal decorr seed 0 breach (0.938 vs 0.93 threshold) noted | ✓ (post-hoc, flagged) |
| Paired McNemar per sub-sweep | Not computed — uninformative at 0/20 and 1/20 solve counts (≤1 discordant pair). Noted as descriptive-only | ✓ (adapted) |

---

## v2-suite combined verdict (updated 2026-04-15, post-baselines)

The pre-registered v2-probe suite (§v2.1–§v2.5) landed at "Partial" earlier this session. The four follow-ups update the picture as follows:

| axis | earlier verdict | follow-up | updated reading |
|---|---|---|---|
| §v2.1 (swamp) | swamped at F_10_v2 = 18/20 | — | unchanged; permissive threshold noted honestly |
| §v2.2 (op slot-indirection) | 20/20 / 20/20 | — | unchanged; scales on op-variation |
| §v2.3 (constant slot-indirection) | 80/80 on one pair | **§v2.6 FAIL (0/3 pairs scale; Pair 1 does-not-scale, Pair 2 & Pair 3 swamped)** | §v2.3's 80/80 stands **as a one-pair precision result** — the breadth check did not extend the claim. Pair 2 / Pair 3 baselines are at ceiling (Fmin = 20/20), so alternation BOTH = 20/20 is a swamp, not scaling; Pair 1 (6-token string-count body) fails the scales-bar at matched compute. Claim narrows back from `across-family / 4 pairs` to `one pair (§v2.3) at one body shape`. |
| §v2.4 (compositional depth) | 0/20 at 1× and 4× compute | **§v2.4-alt (INCONCLUSIVE)** + **§v2.4-proxy (FAIL-proxy-generalises)** | failure is **not** compositional-depth per se; it is a single-predicate proxy basin attractor that dominates whenever a ≥~0.90-accurate single-predicate exists in the training distribution (per §v2.4/§v2.4-proxy, scope `findings.md#proxy-basin-attractor`) |
| §v2.5 (aggregator) | qualitative canalisation | — | unchanged |

**Reframed headline** (replacing the pre-§v2.6-baseline headline):

> Chem-tape's body-invariant-route mechanism passed its pre-registered bar on **op slot-indirection** (§v2.2, 20/20 within-MAP-family and 20/20 cross-MAP-family). On **constant slot-indirection**, the mechanism passed **one precision pair** (§v2.3, 80/80 on `sum_gt_{5,10}_slot` over [0,9]). The §v2.6 breadth check across three additional body shapes returned **FAIL** against its own pre-registered decision rule: two pairs swamped at Fmin = 20/20 (thresholds {7,13} over [0,12] and {5,7} over [0,9] are both too permissive to measure alternation lift), one pair failed the scales bar at 4/20 BOTH for reasons confounded between body-length, assembly-order, and string-domain specifics. This **does not refute** §v2.3 — it refutes the "across-family" breadth extension that §v2.6 was supposed to establish. §v2.4 and its follow-ups show that the earlier "compositional depth does not scale" framing was imprecise: the actual mechanism failure is a single-predicate proxy basin that evolution finds reliably whenever a ≥~0.90-accurate single-predicate exists in the training distribution (per §v2.4/§v2.4-proxy, scope `findings.md#proxy-basin-attractor`) (max>5 on §v2.4; sum>10 on §v2.4-proxy); compositional-depth scaling under §v2.4-alt's body-matched pair at threshold=5 reached 17/20, falsifying a universal "compositional depth doesn't scale" reading. **Paper-scope claim:** evidence for slot-op indirection (§v2.2) and slot-constant indirection at one precision pair (§v2.3); one §v2.6 pair at search-landscape failure (Pair 1); two §v2.6 pairs at swamp-pre-accept (Pair 2, Pair 3) — neither supporting nor refuting the mechanism on those bodies; compositional failure reframed from "compositional depth fails" to "single-predicate proxy basins dominate greedy search under AND-composition whenever the proxy is ≥ ~0.9 accurate on the training distribution." **Not claimed:** "three additional body-invariant pairs", "four task families confirmed", "across-family constant-slot-indirection", or "string-count as THE edge" — the breadth check did not land those, and a redesigned §v2.6' at Fmin-intermediate thresholds is needed before any of them can be reclaimed.

The methodology-level lesson worth encoding: **attractor-identification (direct genotype inspection per methodology §3) plus sampler-design (stratified decorrelation per §20) reframed a structural-failure claim into an attractor-mechanism claim in two sweeps, and a baseline sweep reframed a "provisional PASS-narrow" into a FAIL.** Threshold design is a dependent-variable carrier (§20): permissive thresholds that pre-accept swamp turn "scales" into "unknown" — a test that cannot fail is not a test. Pre-reg-time threshold calibration against expected Fmin is a first-class experimental methodology concern, on par with seed-disjoint replication and commit-hash discipline.

---

## §v2.14. Safe-pop executor-rule ablation (Kuyucu-inspired decoder micro-ablation) (2026-04-16)

**Status:** `PASS` · n=20 · commit `cdf9c39` · —

**Pre-reg:** [Plans/prereg_v2-14-safe-pop.md](../../Plans/prereg_v2-14-safe-pop.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_14_safe_pop_{easy,hard}_{preserve,consume}.yaml`
**Compute:** ~90 min total (4 sweeps × ~22 min at 4-worker M1)

### Question

Does the executor's safe-pop rule (preserve-on-type-mismatch vs consume-on-type-mismatch) measurably affect evolutionary outcomes on body assembly tasks of different typed-chain lengths?

### Hypothesis (pre-registered)

The current "preserve" rule leaves wrong-typed values on the stack, creating type barriers. On the 6-token mixed-type dependency chain (`INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT`), these barriers may suppress assembly. The alternative "consume" rule pops regardless of type. Directional prediction was genuinely uncertain — this was an exploratory ablation inspired by Kuyucu et al. (2011, `docs/theory.md` §6).

### Result

**Easy pair** (`sum_gt_{5,10}_slot`, 4-token body `INPUT SUM THRESHOLD_SLOT GT`):

| Rule | BOTH | Mean best fitness | Mean flip-drop |
|------|------|-------------------|----------------|
| preserve | 20/20 | 1.0000 | 0.0000 |
| consume | 20/20 | 1.0000 | 0.0000 |

Complete identity. Every seed solves both tasks under both rules. Zero flip cost. Safe-pop mode is irrelevant on the 4-token all-int chain.

**Hard pair** (`any_char_count_gt_{1,3}_slot`, 6-token body `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT`; note: `MAP_EQ_R` is the task-bound op at slot id 12):

| Rule | BOTH | Mean best fitness | Mean flip-drop |
|------|------|-------------------|----------------|
| preserve | 4/20 | 0.9000 | 0.0009 |
| consume | **8/20** | **0.9234** | 0.0020 |

Per-seed BOTH-solve and best-fitness:

| Seed | Preserve BOTH | Consume BOTH | P best_fit | C best_fit |
|------|----------|---------|------------|------------|
| 0 | -- | -- | 0.906 | 0.906 |
| 1 | -- | -- | 0.875 | 0.875 |
| 2 | -- | -- | 0.891 | 0.891 |
| 3 | BOTH | BOTH | 1.000 | 1.000 |
| 4 | -- | BOTH | 0.906 | 1.000 |
| 5 | -- | BOTH | 0.828 | 1.000 |
| 6 | -- | -- | 0.844 | 0.844 |
| 7 | -- | BOTH | 0.906 | 1.000 |
| 8 | -- | -- | 0.859 | 0.859 |
| 9 | BOTH | -- | 1.000 | 0.859 |
| 10 | -- | -- | 0.844 | 0.844 |
| 11 | BOTH | -- | 1.000 | 0.875 |
| 12 | -- | BOTH | 0.906 | 1.000 |
| 13 | -- | -- | 0.828 | 0.828 |
| 14 | -- | -- | 0.844 | 0.844 |
| 15 | -- | BOTH | 0.828 | 1.000 |
| 16 | -- | -- | 0.953 | 0.953 |
| 17 | BOTH | BOTH | 1.000 | 1.000 |
| 18 | -- | -- | 0.891 | 0.891 |
| 19 | -- | BOTH | 0.891 | 1.000 |

Seed-overlap: overlap={3, 17}, preserve-only={9, 11}, consume-only={4, 5, 7, 12, 15, 19}.

**Matches pre-registered outcome:** `PASS — consume helps hard pair`
Criterion: `C_hard (8) > P_hard (4) + 3` AND `C_easy (20) >= P_easy (20) − 2`. Both satisfied.

**Statistical test (paired McNemar, seeds 0-19):**

Easy pair: 0 discordant pairs (all 20 seeds solve under both rules). McNemar is degenerate — perfect agreement. No test needed.

Hard pair 2×2 table:

|  | Consume BOTH | Consume not-BOTH |
|---|---|---|
| **Preserve BOTH** | 2 | 2 |
| **Preserve not-BOTH** | 6 | 10 |

Discordant: 2 preserve-only + 6 consume-only = 8. McNemar χ² = (6−2)²/(6+2) = 2.0, p = 0.157 (two-sided). Not significant at α=0.05. As noted in the prereg, McNemar is underpowered at n=20 with this effect size. The primary analysis is descriptive (solve count + seed overlap + attractor-category inspection).

Fisher exact test on the 2×2: p = 0.301 (two-sided). Also not significant.

### Attractor-category inspection (principle 21)

Hard pair C_hard=8/20 is at the pre-registered PASS boundary. Winner-genotype inspection on all 40 hard-pair runs (20 preserve + 20 consume). Token id 12 (`SLOT12` in decoded output) is the task-bound slot that binds to `MAP_EQ_R` on this pair — it is the same token as `MAP_EQ_R` in the canonical body.

**Attractor-category breakdown (hard pair):**

| Category | Preserve | Consume | Δ |
|---|---|---|---|
| canonical-6tok (full `INPUT CHARS SLOT12 SUM THR_SLOT GT` chain present) | 3/20 | **9/20** | +6 |
| partial-assembly (CHARS + SUM present, chain incomplete) | 6/20 | 1/20 | −5 |
| sum-only (SUM/RED_ADD without CHARS) | 6/20 | 3/20 | −3 |
| alt-aggregator (ANY, RED_MAX without SUM) | 5/20 | 7/20 | +2 |

The consume rule triples the canonical-6-token assembly rate (3 → 9) while draining the partial-assembly category (6 → 1). This is consistent with the "stack jam" reading: under preserve, programs reach partial assembly but wrong-typed values (str from INPUT, charlist from CHARS) persist on the stack and block downstream int-consuming ops. Under consume, those barriers are cleared, allowing more seeds to complete the full typed dependency chain.

### Interpretation

The safe-pop rule is a detectable lever on 6-token mixed-type body assembly at this budget (`within-family / n=20 / at BP_TOPK(k=3,bp=0.5) v2_probe / on {sum-body 4-token, string-count-body 6-token} pairs / executor-rule ablation`). The effect is task-dependent: on the 4-token all-int body, the rule is irrelevant (20/20 under both); on the 6-token mixed-type body, consume doubles the BOTH-solve rate from 4/20 to 8/20.

A plausible mechanism is the "stack jam" effect: the 6-token canonical body (`INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT`) crosses four type boundaries (intlist→str→charlist→intlist→int). Under preserve, a wrong-typed value left on the stack after a type mismatch persists through subsequent ops, forcing them to see defaults. Under consume, wrong-typed values are popped, unblocking the chain. The attractor-category shift from partial-assembly (6→1) to canonical-6tok (3→9) supports this reading at this scope.

The seed-overlap pattern (2/10 overlap, 6 consume-only, 2 preserve-only) shows a net positive direction, not mere seed substitution. The consume-only seeds decode to canonical or near-canonical programs, not noise.

This finding was inspired by Kuyucu et al. (2011, `docs/theory.md` §6), who showed that small decision rules in developmental systems can have disproportionate effects on evolvability at their tested scope.

**Mechanism rename check (principles 16 + 16b):**
- (a) Narrower than "safe-pop consume helps assembly"? Yes — it helps assembly of mixed-type chains (6-token body with str→charlist→intlist→int transitions) at this budget. No effect on all-int chains. Working name: "safe-pop consume lifts mixed-type chain assembly (one body, n=20)."
- (b) Broader? Possibly — the stack-jam effect could apply to any mixed-type chain longer than ~4 tokens. But only one pair tested, so the name stays narrow.

### Caveats

- **Seed count:** n=20 per arm per pair (load-bearing, but McNemar p=0.157 does not reach significance).
- **Budget limits:** At pop=1024, gens=1500 only. The §v2.6-pair1-scale follow-ups showed that 4× compute lifts preserve from 4/20 to 8/20 — consume at 1× matches preserve at 4×. Whether consume at 4× would further improve is untested.
- **Overreach check:** "consume helps" is scoped to this one 6-token body shape on string-count tasks at this budget. Not tested on other mixed-type chains, other body lengths, other decoder arms, or Arm A.
- **Open mechanism questions:** (i) Does consume help on other 6-token bodies (e.g., integer-domain with IF_GT)? (ii) Does the effect scale with body length? (iii) Does consume affect the proxy-basin-attractor finding (§v2.4 arc)?

### Degenerate-success check

Per prereg, three candidates were enumerated:

1. **Constant-output degeneracy:** DISCHARGED — consume-arm BOTH-solvers show fitness 1.000 on both tasks with canonical 6-token body programs, not constant-output programs.

2. **Near-threshold seed substitution:** C_hard=8/20 exceeds the prereg's near-threshold trigger range (3-7/20), so this guard was not formally triggered. As extra inspection: 6 consume-only seeds vs 2 preserve-only, net +4 direction. Consume-only seeds decode to canonical-6tok programs. Not mere substitution.

3. **Preserve-arm replication failure:** DISCHARGED — P_easy=20/20 (matches §v2.3 baseline), P_hard=4/20 (matches §v2.6 Pair 1 baseline exactly).

### Diagnostics (prereg-promise ledger)

| Prereg item | Status |
|---|---|
| Per-seed BOTH-solve table | Reported above (full table) |
| Per-seed best-fitness | Reported above (full table) |
| Winner-genotype decoded programs (hard pair, both rules) | Reported in attractor-category section (aggregated by category; full per-seed decoded programs available in sweep output `best_tape.txt` files) |
| Holdout gap | Deferred — holdout_fitness available in result.json. Easy pair gap = 0.0 (all seeds). Hard pair not extracted; low priority given attractor analysis is the primary signal. |
| Flip-transition cost | Reported (means: preserve=0.0009, consume=0.0020) |
| Stack-depth statistics | Deferred — requires new instrumentation on the executor. Not blocking for the PASS verdict. |
| Paired McNemar (easy pair) | Reported: degenerate (0 discordant), no test needed |
| Paired McNemar (hard pair) | Reported: full 2×2 table, χ²=2.0, p=0.157 |
| Fisher exact test (hard pair) | Reported: p=0.301 |

### Findings this supports / narrows

- Supports (new, pending promotion after replication): safe-pop consume lifts mixed-type chain assembly on the 6-token string-count body (`within-family / n=20 / at BP_TOPK(k=3,bp=0.5) v2_probe / executor-rule ablation / exploratory`).
- Narrows: `constant-slot-indirection` ([findings.md](findings.md#constant-slot-indirection)) — the §v2.6 Pair 1 failure at 4/20 is partially attributable to the preserve rule's type barriers at this budget, not solely to body length or string-domain difficulty. Consume at 1× compute (8/20) matches preserve at 4× compute (8/20 from §v2.6-pair1-scale). The decoder-arm caveat on the 6-token body should note that executor semantics are a confound of comparable magnitude to decoder-arm and compute-scaling at this scope.

### Next steps (per prereg decision rule)

- **PASS-clean →** Queue §v2.14b: consume rule on §v2.4 proxy-basin tasks to test whether consume also affects proxy-basin trapping (different mechanism axis).
- Consider promoting "safe-pop consume lifts mixed-type chain assembly" to findings.md after §v2.14b provides cross-axis evidence or after replication on a second 6-token body.

---

## References

---

## §v2.14b. Safe-pop consume on proxy-basin AND-composition tasks (2026-04-16)

**Status:** `PARTIAL` · n=20 per sampler · commit `1fc51c5` · —

**Pre-reg:** [Plans/prereg_v2-14b-consume-proxy.md](../../Plans/prereg_v2-14b-consume-proxy.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_14b_consume_proxy_{natural,decorr}.yaml`
**Compute:** ~27 min total (2 sweeps × ~13.5 min at 4-worker M1)

### Question

Does the safe-pop consume rule (which lifted 6-token mixed-type assembly in §v2.14) also affect proxy-basin-attractor dynamics on intlist-only AND-composition tasks?

### Hypothesis (pre-registered)

Predicted neutral — the type barriers that mattered in §v2.14 (str→charlist→intlist→int on the 6-token string-count body) don't exist on intlist-only inputs. The AND-composition tasks use intlist inputs; after the first SUM/REDUCE_MAX pop, the chain is all-int.

### Result

| Condition | F_AND (≥0.999) | Mean best fitness |
|-----------|---------------|-------------------|
| Preserve natural (§v2.4 baseline) | 0/20 | 0.921 |
| **Consume natural** | **0/20** | **0.921** |
| Preserve decorr (§v2.4-proxy baseline) | 3/20 | — |
| **Consume decorr** | **1/20** | **0.937** |

**Matches pre-registered outcome:** `PARTIAL — attractor shift without escape`
Criterion: `C_nat (0) ≤ 3` AND `C_dec (1) ≤ 7` AND attractor breakdown differs from preserve. The `C_dec` value (1/20) is within ±2 of `P_dec` (3/20), satisfying the quantitative band, but the INCONCLUSIVE row also requires attractor breakdown to match preserve (±10%), which it does not. Codex review confirmed PARTIAL as the correct classification.

### Attractor-category inspection (principle 21)

Required for all results since baseline is 0/20.

**Natural sampler attractor breakdown:**

| Category | Preserve (§v2.4) | Consume |
|---|---|---|
| max_gt_proxy (REDUCE_MAX + GT, no SUM) | 14/20 | 8/20 |
| and_composition (SUM + RED_MAX + IF_GT all present) | 0/20 | **10/20** |
| sum_gt_proxy (SUM + GT, no RED_MAX) | 0/20 | 0/20 |
| partial (SUM or RED_MAX without GT) | 6/20 | 2/20 |

The consume rule dramatically shifts the attractor landscape: 10/20 seeds now attempt AND-composition (vs 0/20 under preserve), and max_gt_proxy dominance drops from 14/20 to 8/20. But none of the 10 and_composition seeds reach 0.999 — they are assembling the compound structure but failing to complete it to solve accuracy. The proxy basin is not escaped; evolution is reaching a different region of the fitness landscape but still not solving.

**Decorrelated sampler attractor breakdown:**

| Category | Preserve (§v2.4-proxy) | Consume |
|---|---|---|
| max_gt_proxy | ~2/17 non-solvers | 2/20 |
| sum_gt_proxy | ~11/17 non-solvers | 4/20 |
| and_composition | — | 9/20 |
| partial | — | 3/20 |
| other | — | 2/20 |

Similar pattern: consume pushes more seeds toward and_composition attempts (9/20 vs ~0 under preserve), but only 1/20 reaches solve (seed 7, a max_gt_proxy program that happens to correlate well, not a genuine AND).

### Interpretation

The safe-pop consume rule reshapes the proxy-basin attractor landscape at this scope (`within-family / n=20 / at BP_TOPK(k=3,bp=0.5) v2_probe / on AND-composition intlist tasks`): it shifts the dominant attractor category from single-predicate proxy programs (max>5) toward compound AND-composition attempts. However, it does not help evolution escape the basin — none of the newly-accessible AND-composition programs reach solve accuracy.

This is a genuinely informative PARTIAL result. It shows that the consume rule's effect extends beyond the multi-type-boundary chains where §v2.14 found it — even on all-int tasks, consume changes which program architectures evolution explores. The mechanism is plausibly broader than "clearing type barriers": consume may also affect how partially-assembled multi-component programs compete during selection (by simplifying the stack state of incomplete programs, making their fitness signal less noisy).

**Mechanism rename check (principles 16 + 16b):**
- (a) Narrower than "consume shifts attractor landscape"? The shift is specifically from single-predicate to multi-component programs at this scope. But none of the multi-component programs solve, so the shift is in exploration, not in outcome.
- (b) Broader than §v2.14's "mixed-type chain assembly"? Yes — §v2.14b shows the consume effect extends to all-int tasks at the landscape level, even though it doesn't produce additional solves. The §v2.14 naming should note that the consume effect has been observed on two task families, not one, though its character differs (assembly lift on mixed-type, attractor shift on all-int).

### Caveats

- **Seed count:** n=20 per sampler (load-bearing).
- **Baseline reuse:** preserve baselines from §v2.4 (commit `e3d7e8a`) and §v2.4-proxy (commit `0230662`), not fresh runs. §v2.14's replication check (P_easy=20/20, P_hard=4/20) validates that the preserve codepath is unchanged.
- **Overreach check:** the attractor shift is real but does not translate to additional solves. "Consume helps AND-composition" would be overreach — consume shifts exploration toward AND-composition without completing it.

### Degenerate-success check

1. **Constant-output degeneracy:** Not triggered — no seeds approach 0.999 via degenerate programs.
2. **Attractor inspection:** Reported above (principle 21). Seed 7 on decorr sampler solves at 1.000 but decodes as a max_gt_proxy program, not genuine AND-composition.

### Diagnostics (prereg-promise ledger)

| Prereg item | Status |
|---|---|
| Per-seed best-fitness | Reported (full per-seed tables above) |
| Winner-genotype decoded programs + attractor classification | Reported (both samplers, all 40 seeds) |
| Holdout gap | Available in result.json; seed 7 decorr: holdout=1.000 (not overfitting). Mean holdout gaps: natural 0.029, decorr 0.064. |

### Findings this supports / narrows

- Supports: `proxy-basin-attractor` ([findings.md](findings.md#proxy-basin-attractor)) — the basin is now confirmed robust to executor-rule variation (adding to decoder-general from §v2.12 and compute-robust from §v2.4). Consume shifts the attractor landscape but does not enable basin escape.
- Narrows (mildly): §v2.14's scope — the consume effect is not strictly limited to multi-type-boundary chains. It also shifts attractor categories on all-int tasks, though without producing additional solves on that family.

### Next steps (per prereg decision rule)

- **PARTIAL →** Document the attractor shift. The consume rule reshapes the proxy landscape without escaping it. Promote §v2.14 to findings.md scoped to mixed-type body assembly (where it produces additional solves). Note §v2.14b as a broadening observation (consume affects landscape structure beyond type barriers) without a solve-rate claim.

---

## §v2.14c. Consume × 4× compute interaction on 6-token string-count body (2026-04-16)

**Status:** `PASS` · n=20 · commit `76bb58f` · —

**Pre-reg:** [Plans/prereg_v2-14c-consume-4x.md](../../Plans/prereg_v2-14c-consume-4x.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_14c_consume_4x.yaml`
**Compute:** ~26 min at 10-worker M1

### Question

Do the consume rule and 4× compute stack on the 6-token string-count body, or do they relieve the same bottleneck?

### Hypothesis (pre-registered)

If consume and compute relieve different bottlenecks (type barriers vs search depth), they should stack: consume-4× > 8/20. If they relieve the same bottleneck, they should substitute: consume-4× ≈ 8/20.

### Result

| Condition | BOTH solved | Solver seeds |
|---|---|---|
| Preserve-1× (§v2.6 Pair 1, baseline) | 4/20 | {3, 7, 15, 17} |
| Consume-1× (§v2.14) | 8/20 | {3, 4, 5, 7, 12, 15, 17, 19} |
| Preserve-4× (§v2.6-pair1-scale) | 8/20 | — |
| **Consume-4× (this experiment)** | **14/20** | **{1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18}** |

Per-seed cross-task fitness:

| Seed | gt_1 | gt_3 | BOTH |
|---|---|---|---|
| 0 | 0.891 | 0.906 | |
| 1 | 1.000 | 1.000 | BOTH |
| 2 | 1.000 | 1.000 | BOTH |
| 3 | 1.000 | 1.000 | BOTH |
| 4 | 1.000 | 1.000 | BOTH |
| 5 | 0.906 | 0.828 | |
| 6 | 0.922 | 0.844 | |
| 7 | 1.000 | 1.000 | BOTH |
| 8 | 1.000 | 1.000 | BOTH |
| 9 | 1.000 | 1.000 | BOTH |
| 10 | 1.000 | 1.000 | BOTH |
| 11 | 1.000 | 1.000 | BOTH |
| 12 | 1.000 | 1.000 | BOTH |
| 13 | 0.812 | 0.828 | |
| 14 | 0.844 | 0.844 | |
| 15 | 1.000 | 1.000 | BOTH |
| 16 | 1.000 | 1.000 | BOTH |
| 17 | 1.000 | 1.000 | BOTH |
| 18 | 1.000 | 1.000 | BOTH |
| 19 | 0.797 | 0.891 | |

**Matches pre-registered outcome:** `PASS — levers stack` (C4 = 14/20 ≥ 13/20).

**Statistical test:** descriptive (solve counts + seed overlap). Seed overlap with consume-1× solvers: 6/8 retained ({3,4,7,12,15,17}), 2 lost ({5,19}), 8 new ({1,2,8,9,10,11,16,18}). Genuine superset expansion.

### Attractor-category inspection (principle 21)

Required: 14/20 is one seed above the PASS threshold (13/20), making this a near-threshold result per methodology §21.

| Category | Seeds | BOTH-solvers |
|---|---|---|
| canonical-6tok (`INPUT CHARS SLOT_12 SUM THRESHOLD_SLOT GT` present) | 10/20 | 9 ({1,2,4,7,8,9,10,12,17}) |
| partial-5tok (5 of 6 canonical tokens, typically missing SUM or using REDUCE_ADD for SUM) | 9/20 | 5 ({3,11,15,16,18}) |
| partial-scan (INPUT CHARS SLOT_12 only) | 1/20 | 0 |

The 14 BOTH-solvers include 9 canonical-6tok and 5 partial-5tok programs. The partial-5tok solvers achieve BOTH-solve through near-canonical assemblies (e.g., REDUCE_ADD substituting for SUM, or THRESHOLD_SLOT reached through a slightly different token ordering). All 6 non-solvers are partial-5tok or partial-scan — seeds where the assembly is incomplete.

### Interpretation

Consume and 4× compute show additive improvement on the 6-token string-count body at this scope (`within-family / n=20 / at BP_TOPK(k=3,bp=0.5) v2_probe / on 6-token string-count body / consume × compute interaction`). Consume-4× (14/20) exceeds both consume-1× (8/20) and preserve-4× (8/20) by +6, and exceeds preserve-16× (13/20 from §v2.6-pair1-scale-8x) by +1.

The seed-overlap analysis supports this: consume-4× retains 6/8 of the consume-1× solvers and adds 8 new ones, consistent with compute opening new seeds that consume makes accessible but 1× budget doesn't reach. The 2 lost seeds (5, 19) are within noise at n=20.

The attractor classification shows that additional compute shifts winners toward canonical-6tok assembly (10/20 total, 9 BOTH-solvers) while partial-5tok programs still account for 5 of the 14 solvers. The non-solvers cluster at 0.79–0.92 on both tasks — still in the partial-assembly regime (methodology principle 15: hard-floor seeds).

**Mechanism rename check (principles 16 + 16b):**
- (a) Narrower than "levers stack"? The stacking is observed on one body shape at one decoder arm. "Stacking" is the correct local description; the generality claim is scoped to this condition.
- (b) Broader than "type barriers"? The attractor data show consume-4× winners are a mix of canonical and partial-5tok assemblies. The mechanism is better described as "consume enables assembly + compute extends search" than as a single broader mechanism name.

### Caveats

- **Seed count:** n=20 (load-bearing).
- **Budget limits:** 4× compute (pop=2048, gens=3000). Whether the stacking continues at 8× or 16× compute is untested.
- **Overreach check:** "levers stack" is scoped to this one body shape under BP_TOPK(k=3,bp=0.5). Not tested on other bodies, decoder arms, or task families.
- **Open mechanism questions:** (i) Does stacking hold on a second mixed-type body? (ii) At what compute budget does consume-4× plateau? (iii) Does the stacking also hold under Arm A?

### Degenerate-success check

Per prereg:
- **Too-clean result:** C4 = 14/20, not 20/20. Not triggered.
- **Seed overlap with consume-1×:** 6/8 overlap, plus 8 new solvers. Genuine superset expansion, not seed substitution.

### Diagnostics (prereg-promise ledger)

| Prereg item | Status |
|---|---|
| Per-seed BOTH-solve + best-fitness | Reported (full per-seed table above) |
| Seed overlap with consume-1× solvers | Reported: 6/8 retained, 8 new |
| Seed overlap with preserve-4× solvers | Not extracted — preserve-4× solver seeds not available in this chronicle (§v2.6-pair1-scale output). Deferred; consume-1× overlap is the primary comparison for the stacking hypothesis. |
| Winner-genotype attractor-category classification | Reported: 10/20 canonical-6tok (9 BOTH), 9/20 partial-5tok (5 BOTH), 1/20 partial-scan (0 BOTH). |

### Findings this supports / narrows

- Supports: `safe-pop-consume-effect` ([findings.md](findings.md#safe-pop-consume-effect)) — consume and compute show additive improvement at this scope. Consume-4× (14/20) exceeds preserve-16× (13/20).
- Narrows scope boundary: findings.md § safe-pop-consume-effect noted "consume at 4× compute" as an open external-validity question — this experiment answers it positively.

### Next steps (per prereg decision rule)

- **PASS →** The stacking result strengthens the case for consume as the BP_TOPK default. §v2.14e (second slot binding) provides replication evidence on a different axis.

---

## §v2.14d. Safe-pop consume under Arm A direct GP on 6-token string-count body (2026-04-16)

**Status:** `INCONCLUSIVE` · n=20 · commit `76bb58f` · did not match any pre-registered outcome

**Pre-reg:** [Plans/prereg_v2-14d-consume-arm-a.md](../../Plans/prereg_v2-14d-consume-arm-a.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_14d_consume_arm_a.yaml`
**Compute:** ~10 min at 10-worker M1

### Question

Does the safe-pop consume rule also lift 6-token body assembly under Arm A direct GP (no extraction layer), or is the effect specific to BP_TOPK's run-based decode?

### Hypothesis (pre-registered)

Prediction genuinely uncertain. Under Arm A the full 32-token tape executes (no run extraction), so the type-barrier dynamics differ from BP_TOPK.

### Result

| Condition | BOTH solved | Solver seeds |
|---|---|---|
| Preserve Arm A (§v2.6-pair1-scale-A, baseline) | 7/20 | — |
| **Consume Arm A (this experiment)** | **5/20** | **{2, 3, 4, 10, 18}** |
| Consume BP_TOPK (§v2.14, for comparison) | 8/20 | {3, 4, 5, 7, 12, 15, 17, 19} |

Per-seed cross-task fitness:

| Seed | gt_1 | gt_3 | BOTH |
|---|---|---|---|
| 0 | 0.891 | 0.906 | |
| 1 | 0.875 | 0.875 | |
| 2 | 1.000 | 1.000 | BOTH |
| 3 | 1.000 | 1.000 | BOTH |
| 4 | 1.000 | 1.000 | BOTH |
| 5 | 0.906 | 0.828 | |
| 6 | 0.922 | 0.844 | |
| 7 | 0.891 | 0.906 | |
| 8 | 0.922 | 0.859 | |
| 9 | 1.000 | 0.984 | |
| 10 | 1.000 | 1.000 | BOTH |
| 11 | 0.906 | 0.875 | |
| 12 | 0.906 | 0.906 | |
| 13 | 0.812 | 0.828 | |
| 14 | 0.844 | 0.844 | |
| 15 | 0.922 | 0.828 | |
| 16 | 0.891 | 0.953 | |
| 17 | 0.938 | 0.844 | |
| 18 | 1.000 | 1.000 | BOTH |
| 19 | 0.797 | 0.891 | |

**Matches pre-registered outcome:** Did not match any pre-registered outcome. C_A = 5/20 falls between the INCONCLUSIVE band (|C_A − P_A| ≤ 1, i.e., 6–8/20) and the FAIL band (C_A < P_A − 2, i.e., ≤ 4/20). The outcome table was incomplete — it did not cover the gap between 5/20 and the INCONCLUSIVE lower bound of 6/20. Given the off-grid status, `INCONCLUSIVE` is the most conservative classification: no evidence that consume helps Arm A, direction mildly negative, but the −2 drop is within plausible noise at n=20.

**Statistical test:** descriptive (solve counts). Seed overlap with consume BP_TOPK (§v2.14): only 2 shared ({3, 4}).

### Attractor-category inspection (principle 21)

Required: C_A = 5/20 is near the prereg threshold boundary, and the result is off-grid.

| Category | Seeds | BOTH-solvers |
|---|---|---|
| canonical-6tok | 6/20 | 3 ({4, 10, 18}) |
| partial-5tok | 12/20 | 2 ({2, 3}) |
| partial-scan | 2/20 | 0 |

Under Arm A consume, only 6/20 winners reach canonical-6tok assembly (vs 10/20 under consume-4× BP_TOPK in §v2.14c). The majority (12/20) remain partial-5tok. The 2 partial-5tok BOTH-solvers (seeds 2, 3) reach solve through near-canonical assemblies. The low canonical-6tok rate under Arm A is consistent with the longer execution path (32 tokens vs extracted run) providing less selection pressure toward compact canonical forms.

### Interpretation

No evidence that the consume rule helps under Arm A at this scope (`within-family / n=20 / at Arm-A v2_probe / on 6-token string-count body / executor-rule × decoder-arm interaction`). C_A = 5/20 is a mild decline from the preserve baseline (7/20), but the −2 drop is within plausible noise at n=20, and the result falls in the gap between pre-registered bands.

The low seed overlap with consume BP_TOPK (2/8) suggests the solve pathways differ between decoder arms. Under Arm A, the full 32-token tape executes, so type barriers may be less persistent (the stack is flushed and rebuilt many times) or interleaved with useful computation that consume disrupts.

The attractor inspection shows that Arm A consume winners are predominantly partial-5tok (12/20), with fewer canonical-6tok assemblies (6/20) than under BP_TOPK consume-4× (10/20). This is consistent with Arm A's longer execution providing a different assembly dynamic.

**Mechanism rename check (principles 16 + 16b):**
- (a) Narrower than "consume helps assembly"? At this scope, consume does not help Arm A assembly. The solve-rate lift from §v2.14 is at minimum decoder-arm-dependent.
- (b) Broader? No — this result restricts the scope of the consume effect.

### Caveats

- **Seed count:** n=20 (load-bearing).
- **Budget limits:** 1× compute (pop=1024, gens=1500). Whether consume interacts differently with Arm A at higher compute is untested.
- **Overreach check:** The honest statement is "no evidence consume helps Arm A at this budget; direction mildly negative but within noise." Stronger claims about Arm A specificity or run-extraction dependence are not supported by this single off-grid result.
- **Baseline cross-commit:** Arm A preserve baseline (7/20) from §v2.6-pair1-scale-A (commit `c8af29d`), not a fresh run at the same commit.
- **Preserve-baseline drift:** Per prereg guard, the fresh preserve-Arm-A run was not included in this experiment. The 7/20 baseline is assumed stable based on §v2.14's replication of P_easy=20/20, P_hard=4/20 on the BP_TOPK arm. Acknowledged as incomplete.

### Degenerate-success check

- Not triggered (C_A = 5/20, below baseline).

### Diagnostics (prereg-promise ledger)

| Prereg item | Status |
|---|---|
| Per-seed BOTH-solve + best-fitness | Reported (full per-seed table above) |
| Seed overlap with §v2.6-pair1-scale-A preserve solvers | Deferred — would require reading §v2.6-pair1-scale-A output. The aggregate 5/20 vs 7/20 and off-grid classification are the primary signals. |
| Winner-genotype attractor-category classification | Reported: 6/20 canonical-6tok (3 BOTH), 12/20 partial-5tok (2 BOTH), 2/20 partial-scan (0 BOTH). |
| Program length distribution | Deferred — requires extraction from sweep output. Lower priority given INCONCLUSIVE verdict. |

### Findings this supports / narrows

- Narrows: `safe-pop-consume-effect` ([findings.md](findings.md#safe-pop-consume-effect)) — no evidence consume helps under Arm A at 1× budget. The findings.md scope boundary "not tested on Arm A" is now answered: consume shows no lift under Arm A at this budget, with a mildly negative (but within-noise) direction. The consume effect remains at minimum decoder-arm-dependent.

### Next steps (per prereg decision rule)

- **Off-grid (between INCONCLUSIVE and FAIL) →** Do not change the project default globally. The consume effect is at minimum decoder-arm-dependent. Document in findings.md scope boundaries. The off-grid outcome also flags that future prereg outcome tables on this axis should cover the 5/20 gap.

---

## §v2.14e. Safe-pop consume replication on E-count body (second slot binding) (2026-04-16)

**Status:** `PASS` · n=20 · commit `76bb58f` · —

**Pre-reg:** [Plans/prereg_v2-14e-consume-2nd-body.md](../../Plans/prereg_v2-14e-consume-2nd-body.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_14e_consume_E_preserve.yaml`, `v2_14e_consume_E_consume.yaml`
**Compute:** ~37 min total (2 sweeps at 10-worker M1)

### Question

Does the safe-pop consume effect on 6-token mixed-type assembly replicate on a second slot binding (MAP_EQ_E instead of MAP_EQ_R)?

### Hypothesis (pre-registered)

If the consume effect is driven by the type-chain structure (str→charlist→intlist→int), it should replicate with MAP_EQ_E since the type chain is identical. If it's specific to the MAP_EQ_R op or the R-count task distribution, it won't.

### Result

| Condition | BOTH solved | Solver seeds |
|---|---|---|
| **E-count preserve (this experiment)** | **4/20** | **{3, 9, 11, 17}** |
| **E-count consume (this experiment)** | **8/20** | **{3, 4, 5, 7, 12, 15, 17, 19}** |
| R-count preserve (§v2.14 baseline) | 4/20 | {3, 7, 15, 17} |
| R-count consume (§v2.14) | 8/20 | {3, 4, 5, 7, 12, 15, 17, 19} |

Per-seed cross-task fitness (preserve):

| Seed | E_gt_1 | E_gt_3 | BOTH |
|---|---|---|---|
| 0 | 0.828 | 0.891 | |
| 1 | 0.891 | 0.969 | |
| 2 | 0.875 | 0.875 | |
| 3 | 1.000 | 1.000 | BOTH |
| 4 | 0.891 | 0.906 | |
| 5 | 0.859 | 0.859 | |
| 6 | 0.859 | 0.953 | |
| 7 | 0.875 | 0.906 | |
| 8 | 0.859 | 0.891 | |
| 9 | 1.000 | 1.000 | BOTH |
| 10 | 0.859 | 0.859 | |
| 11 | 1.000 | 1.000 | BOTH |
| 12 | 0.938 | 0.844 | |
| 13 | 0.938 | 0.891 | |
| 14 | 0.891 | 0.812 | |
| 15 | 0.844 | 0.922 | |
| 16 | 0.953 | 0.844 | |
| 17 | 1.000 | 1.000 | BOTH |
| 18 | 0.906 | 0.922 | |
| 19 | 0.859 | 0.875 | |

Per-seed cross-task fitness (consume):

| Seed | E_gt_1 | E_gt_3 | BOTH |
|---|---|---|---|
| 0 | 0.828 | 0.891 | |
| 1 | 0.891 | 0.969 | |
| 2 | 0.875 | 0.875 | |
| 3 | 1.000 | 1.000 | BOTH |
| 4 | 1.000 | 1.000 | BOTH |
| 5 | 1.000 | 1.000 | BOTH |
| 6 | 0.859 | 0.953 | |
| 7 | 1.000 | 1.000 | BOTH |
| 8 | 0.859 | 0.891 | |
| 9 | 0.859 | 0.875 | |
| 10 | 0.859 | 0.859 | |
| 11 | 0.875 | 0.906 | |
| 12 | 1.000 | 1.000 | BOTH |
| 13 | 0.938 | 0.891 | |
| 14 | 0.891 | 0.812 | |
| 15 | 1.000 | 1.000 | BOTH |
| 16 | 0.953 | 0.844 | |
| 17 | 1.000 | 1.000 | BOTH |
| 18 | 0.906 | 0.922 | |
| 19 | 1.000 | 1.000 | BOTH |

**Matches pre-registered outcome:** `PASS — replicates` (C_E = 8 > P_E + 3 = 7, AND P_E = 4/20 within ±3 of 4/20).

**Statistical test:** paired McNemar on seeds 0-19 (preserve vs consume on E-count pair). Concordant: 3 both-solve + 12 neither-solve = 15. Discordant: 5 consume-only ({4,5,7,12,15}) + 1 preserve-only ({9}) = 6. McNemar χ² = (5−1)²/6 = 2.67, p = 0.102. Not significant at α=0.05 (underpowered as expected at n=20).

### Attractor-category inspection (principle 21)

Required: C_E = 8/20 is one seed above the prereg lift threshold (C_E > P_E + 3 = 7), making this near-threshold per methodology §21.

**Preserve arm:**

| Category | Seeds | BOTH-solvers |
|---|---|---|
| canonical-6tok | 7/20 | 2 ({3, 11}) |
| partial-5tok | 12/20 | 2 ({9, 17}) |
| partial-scan | 1/20 | 0 |

**Consume arm:**

| Category | Seeds | BOTH-solvers |
|---|---|---|
| canonical-6tok | 13/20 | 7 ({3, 4, 5, 7, 12, 17, 19}) |
| partial-5tok | 6/20 | 1 ({15}) |
| partial-scan | 1/20 | 0 |

Under consume, canonical-6tok assembly nearly doubles (7→13/20), and canonical-6tok BOTH-solvers increase from 2 to 7. This mirrors the §v2.14 R-count pattern: consume shifts the winner population toward canonical assembly.

### Interpretation

The consume effect replicates on the E-count body at this scope (`within-family / n=20 / at BP_TOPK(k=3,bp=0.5) v2_probe / on 6-token E-count body / executor-rule ablation replication`). The aggregate rates match exactly: P_E = 4/20 = P_R; C_E = 8/20 = C_R.

The consume-arm solver sets are identical between E-count and R-count: {3,4,5,7,12,15,17,19} in both cases, an 8/8 overlap. The preserve-arm solver sets differ (E: {3,9,11,17}, R: {3,7,15,17}, overlap 2/4). This pattern is consistent with the consume effect being driven by shared structure (same type chain, same body shape, same seed-level genotype dynamics) rather than the specific MAP op at slot 12. However, the perfect overlap should be interpreted cautiously: the two conditions share everything except the slot op and the label function, so same-seed correlation through shared RNG trajectories is expected when the fitness landscapes are nearly isomorphic. The overlap is descriptively striking but is not independent evidence — it is consistent with both the type-chain reading and with shared-RNG correlation on near-identical tasks.

The attractor classification strengthens the replication: under consume, canonical-6tok assembly rises from 7→13/20, and BOTH-solvers shift from partial assemblies toward canonical forms — the same qualitative pattern as §v2.14.

**Mechanism rename check (principles 16 + 16b):**
- (a) Narrower than "consume replicates across MAP ops"? No — the replication is clean at the descriptive level.
- (b) Broader than "MAP_EQ_R-specific"? The effect now spans two MAP-family slot bindings at this scope. Broadening to "MAP-family slot bindings" is supported; broadening further to "type-chain-driven, not op-specific" goes beyond what two same-family ops can establish.

### Caveats

- **Seed count:** n=20 (load-bearing). McNemar p=0.102, not significant at α=0.05.
- **Budget limits:** 1× compute only. Whether the E-count body also shows the §v2.14c stacking behavior is untested.
- **Overreach check:** The replication is across two MAP-family ops with the same type signature. A test of the type-chain hypothesis (as opposed to MAP-family-specific behavior) would require a non-MAP op at slot 12 that produces a different type chain. "Replicates across two MAP-family bindings" is the supportable claim; "type-chain-driven, not op-specific" exceeds the tested scope.
- **Seed overlap caveat:** The perfect 8/8 consume-arm overlap is expected when the two task pairs are near-isomorphic (same body, same type chain, same fitness landscape shape). Shared-seed/shared-RNG correlation is the null explanation; the overlap does not by itself confirm a mechanistic reading.

### Degenerate-success check

Per prereg:
- **Swamp check:** P_E = 4/20, not swamped.
- **Too-clean result:** C_E = 8/20, not too clean.
- **Seed overlap with R-count consume:** 8/8 match. Consistent with type-chain-driven reading but also with shared-RNG correlation on near-isomorphic tasks (see caveat).

### Diagnostics (prereg-promise ledger)

| Prereg item | Status |
|---|---|
| Per-seed BOTH-solve + best-fitness (both rules) | Reported (full per-seed tables above) |
| Winner-genotype attractor-category classification | Reported: preserve 7/20 canonical-6tok, consume 13/20 canonical-6tok. |
| Seed overlap between E-count and R-count | Reported: consume 8/8, preserve 2/4 |
| Holdout gap | Not extracted from result.json in this chronicle. Omitted from interpretation — the PASS verdict rests on solve rates and attractor classification, not holdout metrics. |
| Paired McNemar | Reported: χ²=2.67, p=0.102 |

### Findings this supports / narrows

- Supports and broadens: `safe-pop-consume-effect` ([findings.md](findings.md#safe-pop-consume-effect)) — the solve-rate lift replicates on two MAP-family slot bindings (MAP_EQ_R, MAP_EQ_E) with identical effect size and identical solver seeds at this scope. The scope boundary "not replicated on a second slot binding" is now answered.
- Supports: `op-slot-indirection` ([findings.md](findings.md#op-slot-indirection)) — E-count tasks behave similarly to R-count tasks under the same body shape, consistent with the body-invariant-route mechanism.

### Next steps (per prereg decision rule)

- **PASS →** Broaden findings.md `safe-pop-consume-effect` scope from "one slot binding (MAP_EQ_R)" to "two MAP-family slot bindings (MAP_EQ_R, MAP_EQ_E)."

---

## §v2.14g. Consume × Arm A × 4× compute on 6-token string-count body (2026-04-16)

**Status:** `INCONCLUSIVE` · n=20 per arm · commit `9455d04` · —

**Pre-reg:** [Plans/prereg_v2-14g-consume-arm-a-4x.md](../../Plans/prereg_v2-14g-consume-arm-a-4x.md)
**Sweeps:** `experiments/chem_tape/sweeps/v2/v2_14g_consume_arm_a_4x.yaml` + companion `v2_14g_preserve_arm_a_4x.yaml`
**Compute:** ~10 min per sweep at 10-worker M1 (4× compute = pop=2048, gens=3000)

### Question

Is the §v2.14d Arm A consume null result (5/20 vs preserve 7/20 at 1× compute) rescued by 4× compute, mirroring the §v2.14c BP_TOPK consume × compute stacking (consume-4× = 14/20 > preserve-4× = 8/20)?

### Hypothesis (pre-registered)

Three non-overlapping readings consistent with current evidence: (1) decoder-arm-dependent at any compute; (2) compute-threshold effect — consume rescued by 4× compute on Arm A; (3) consume uniformly hurts Arm A. Prereg favored no direction.

### Result

| Condition | BOTH solved | vs §v2.14d 1× | vs §v2.14c BP_TOPK 4× |
|---|---|---|---|
| **Preserve Arm A 4×** (this expt, companion baseline) | **11/20** | +4 vs §v2.6-pair1-scale-A 7/20 (cross-commit) | Arm A preserve-4× (11) > BP_TOPK preserve-4× (8) |
| **Consume Arm A 4×** (this expt) | **11/20** | +6 vs §v2.14d 5/20 (cross-commit) | Arm A consume-4× (11) < BP_TOPK consume-4× (14) |
| **Δ (C − P) at matched 4× compute** | **0** | — | BP_TOPK had +6 here |

Per-seed BOTH-solvers:
- Preserve: {3, 4, 5, 7, 8, 9, 10, 12, 16, 17, 18}
- Consume: {2, 3, 5, 6, 7, 8, 9, 10, 12, 15, 16}
- Shared (both arms solve): {3, 5, 7, 8, 9, 10, 12, 16} (8 seeds)
- Preserve-only: {4, 17, 18} (3 seeds)
- Consume-only: {2, 6, 15} (3 seeds)

**Matches pre-registered outcome:** `INCONCLUSIVE` — `|C_A_4x − P_A_4x| ≤ 1` (exact Δ=0) per prereg decision table.

**Statistical test:** paired McNemar on seeds 0-19. Discordant pairs: b=3 (preserve solved, consume didn't), c=3 (consume solved, preserve didn't). χ² = (|b-c|)²/(b+c) = 0/6 = 0. p=1.00. **Classification:** confirmatory; family "`safe-pop-consume-effect` decoder-arm scope" (§v2.14, §v2.14b–e, this). Corrected α at family size ≥ 6 is ≤ 0.0083; the delta=0 result is not remotely near significance, so FWER correction is moot for this test but named for audit-trail completeness.

### Pre-registration fidelity checklist (principle 23)

- [x] Every outcome row from the prereg was tested (PASS-rescued, PASS-compute-both, INCONCLUSIVE, FAIL-damages, SWAMPED). The observed Δ=0 at 11/20 both arms maps cleanly onto the INCONCLUSIVE row — no rows silently added or removed.
- [x] Sweep execution: consume sweep + companion preserve sweep (Option A baseline) at matched commit, seeds 0-19 both. Attractor inspection ran on both arms (§Attractor inspection below).
- [~] Diagnostics partially completed: per-seed BOTH-solve reported (solver sets); attractor-category classification reported; `program effective-length distribution (NOP count under Arm A)` **deferred**; `holdout gap` **deferred**. See Diagnostics ledger below for reasons. Per §23, these are explicit deferrals, not silent skips.
- [x] No mid-run parameter / sampler / seed changes. Both sweeps use the YAMLs committed at `9455d04`.
- [x] Every statistical test and diagnostic named in the prereg appears below or is explicitly deferred.

### Attractor-category inspection (principle 21 — threshold-adjacent result)

Arm A executes the full 32-token tape linearly, so the "extracted program" is the full non-NOP non-separator token sequence. Classifier matches against the canonical Pair 1 body `INPUT CHARS SLOT_12 SUM THRESHOLD_SLOT GT`.

| Category | preserve total → BOTH | consume total → BOTH |
|---|---|---|
| canonical-6tok | 5/20 → **5 BOTH** | **8/20 → 8 BOTH** |
| partial-5tok | 7/20 → 1 BOTH | 9/20 → 2 BOTH |
| partial-4tok | 1/20 → 0 | 1/20 → 0 |
| partial-scan | 7/20 → 5 BOTH | 2/20 → 1 BOTH |

**Mechanism signal even at Δ=0:** under consume, canonical-6tok assembly rises 5→8 and partial-scan route falls 7→2. The same BOTH count (11/20 each) is achieved through **different attractor distributions** — consume concentrates on compact canonical assemblies; preserve distributes across canonical + partial-scan routes. This matches the §v2.14b attractor-shift pattern under consume on intlist tasks.

### Interpretation

Scope: `within-family · n=20 per arm · at Arm A 4× compute v2_probe · on 6-token string-count body · executor-rule × decoder-arm × compute three-way`.

**The solve-rate null is robust.** At matched commit and matched 4× compute, preserve and consume yield identical BOTH counts (11/20 each). The 3 preserve-only solvers and 3 consume-only solvers are orthogonal — no lift in either direction. The 1× Arm A null (§v2.14d: 5 vs 7) is thus **not** a compute-threshold effect; 4× compute does not rescue consume on Arm A. This tightens the `safe-pop-consume-effect` findings.md scope boundary from "not tested at 4× compute on Arm A" to "null at 4× compute on Arm A as well — decoder-arm dependence persists at the tested 1× and 4× compute tiers."

**Compute alone helps Arm A.** The preserve arm lifts from 7/20 at 1× (§v2.6-pair1-scale-A) to 11/20 at 4× — a +4 compute-only effect on Pair 1 under Arm A. Consume neither adds to nor subtracts from this compute lift at matched 4× budget. This mirrors the preserve side of §v2.14c (BP_TOPK 4→8 preserve from 1× → 4×) but lacks the consume multiplier that §v2.14c found (8→14 under consume at 4×).

**But the attractor-level signal is real.** Even at identical solve counts, consume redistributes winner-genotype categories: canonical-6tok 5→8, partial-scan 7→2. This is a mechanism-level effect that the aggregate solve-rate metric hides. It means consume under Arm A is **doing something** to the search trajectory — pushing toward compact canonical assemblies — but that "something" does not translate to additional solves at this compute tier. The effect is decoder-arm-dependent at the solve-rate layer and decoder-arm-moderated at the attractor layer.

**Mechanism rename check (principles 16 + 16b):**
- (a) Narrower than "BP_TOPK-specific solve-rate lift"? No — this confirms the existing narrow scope.
- (b) Broader than "consume concentrates on canonical-6tok assembly"? Possibly — if the attractor-redistribution pattern holds across non-MAP bindings / non-string bodies, the effect is broader than solve-rate-specific. Untested here; flagged as open.

### Caveats

- **Seed count:** n=20 per arm (load-bearing). McNemar p=1.00 — no near-significant signal in the solve-rate axis.
- **Budget limits:** 4× compute (pop=2048, gens=3000). Whether consume × Arm A interacts differently at 8× or 16× compute is untested.
- **Overreach check:** "decoder-arm dependence persists at the tested 1× and 4× compute tiers" is the supported narrowing; extending to "structural at any compute" overreaches the tested range. The attractor-redistribution claim is descriptive; mechanism-level interpretation (why canonical-6tok concentrates under consume without a solve-rate lift) requires further inspection — possibly at per-gen trajectory resolution.
- **Cross-commit comparison caveats:** §v2.14d's 5/20 and §v2.6-pair1-scale-A's 7/20 are cross-commit (`76bb58f` / `c8af29d`) — the "consume at 1× Arm A = 5" and "preserve at 1× Arm A = 7" anchors are from different commits. The internal 1× baseline for this sweep is §v2.14d's 5/20, and the 4× lift (+6 consume, +4 preserve) is computed against it.
- **Cross-decoder 4× comparison:** §v2.14c BP_TOPK at 4× had preserve=8, consume=14 (Δ=+6). This sweep's Arm A at 4× has preserve=11, consume=11 (Δ=0). The decoder-arm dependence of the Δ is the clearest signal in the two sweeps together.

### Diagnostics (prereg-promise ledger)

| Prereg item | Status |
|---|---|
| Per-seed BOTH-solve (both rules) | Reported (solver sets above) |
| Per-seed best-fitness (both rules) | Deferred — not extracted from per-run result.json; verdict rests on solve counts + attractor structure. |
| Winner-genotype attractor-category classification (both arms) | Reported (Attractor inspection table) |
| Program effective-length distribution (NOP count under Arm A) | Deferred — expected high NOP count under Arm A is a known property; did not drive interpretation at this verdict. |
| Seed overlap with §v2.14d (Arm-A-1× consume) and §v2.14c (BP_TOPK-4× consume) | §v2.14d 1× consume solvers {2, 3, 4, 10, 18}: overlap with this sweep's consume-Arm-A-4× solvers {2, 3, 5, 6, 7, 8, 9, 10, 12, 15, 16} = {2, 3, 10} (3/5). §v2.14c BP_TOPK-4× consume solvers: cross-decoder comparison is qualitative only (no shared seeds-with-same-decoder). |
| Holdout gap | Deferred — not extracted from per-run result.json; verdict rests on solve rates + attractor structure. |

### Findings this supports / narrows

- Narrows: `safe-pop-consume-effect` ([findings.md](findings.md#safe-pop-consume-effect)) — the 1× decoder-arm-dependence caveat (§v2.14d) is confirmed at 4× compute. The "BP_TOPK-specific solve-rate lift" scope tightens from "1× only" to "persists at 1× and 4× — decoder-arm dependence on solve rate is not a compute-threshold effect within the tested range." The attractor-redistribution signal under consume is a new, narrower finding about Arm A's search trajectory that the solve-rate metric alone hides.

### Next steps (per prereg decision rule)

- **INCONCLUSIVE →** Strengthen findings.md `safe-pop-consume-effect` scope boundary: decoder-arm dependence on solve rate persists at 1× and 4× compute (both null for Arm A). BP_TOPK-specific solve-rate claim becomes firmer within the tested compute range. Do NOT change the project default to consume at any decoder arm without decoder-specific evidence. The attractor-redistribution observation is flagged for later: if the effect replicates on a non-MAP slot binding or under a different body topology, it becomes a separate sub-finding about consume's landscape-level behavior independent of solve rate.

---

## §v2.15. Decoder-ablation grid (K × bond_protection_ratio) on §v2.3 and §v2.6 Pair 1 (2026-04-16)

**Status:** `NULL` · n=20 per cell · commit `9455d04` · Part-1 meta-learning gate (see [future-experiments.md](future-experiments.md) Part 1 Phase 0 diagnostic gate)

**Pre-reg:** [Plans/prereg_v2-15-decoder-grid.md](../../Plans/prereg_v2-15-decoder-grid.md)
**Sweeps:** `experiments/chem_tape/sweeps/v2/v2_15_grid_v2_3.yaml` + `v2_15_grid_pair1.yaml`
**Compute:** 43 min (§v2.3 grid, 120 configs) + 33 min (Pair 1 grid, 120 configs) = ~76 min total at 10 workers

### Question

Does any parameterization of the BP_TOPK decoder's (K, bond_protection_ratio) knobs lift §v2.6 Pair 1 measurably toward the §v2.3 ceiling without losing §v2.3's 20/20 BOTH — establishing whether the chemistry-knob search space has useful structure before committing to Part 1 meta-learning ES machinery?

### Hypothesis (pre-registered)

Three disjoint outcomes: (1) leverage exists — at least one JOINT-LIFT cell (§v2.3 ≥ 18 AND Pair 1 ≥ 12) → Part 1 ES worth building; (2) no joint cell — knobs trade ceiling for floor; (3) uniform null — knobs lack leverage → redirect Part 1 away from bonding parameters.

### Result

§v2.3 BOTH-solve grid (sum_gt_{5,10}_slot alternation):

|       | bp=0.0 | bp=0.5 (ref) | bp=1.0 |
|-------|--------|--------------|--------|
| **K=3** | 4/20  | 20/20        | 20/20  |
| **K=5** | 3/20  | 20/20        | 20/20  |

§v2.6 Pair 1 BOTH-solve grid (any_char_count_gt_{1,3}_slot alternation):

|       | bp=0.0 | bp=0.5 (ref) | bp=1.0 |
|-------|--------|--------------|--------|
| **K=3** | 1/20  | 4/20         | **10/20 (INTERMEDIATE)** |
| **K=5** | 1/20  | 5/20         | 8/20   |

Cell classification (per prereg):

| cell (K, bp) | §v2.3 | Pair 1 | classification |
|---|---|---|---|
| (3, 0.0) | 4/20 | 1/20 | GLOBAL-COLLAPSE |
| (3, 0.5) | 20/20 | 4/20 | CEILING-STABLE-NULL (reference anchor) |
| (3, 1.0) | 20/20 | 10/20 | **INTERMEDIATE** (Pair 1 ∈ [9, 11]) |
| (5, 0.0) | 3/20 | 1/20 | GLOBAL-COLLAPSE |
| (5, 0.5) | 20/20 | 5/20 | CEILING-STABLE-NULL |
| (5, 1.0) | 20/20 | 8/20 | CEILING-STABLE-NULL |

**Matches pre-registered outcome:** `NULL — uniform no-lift` — no cell hit JOINT-LIFT (Pair 1 ≥ 12). One INTERMEDIATE cell (K=3, bp=1.0) triggered the prereg's commitment to n-expansion, executed as §v2.15-bp1-k3-nexp (below).

**Statistical tests:** descriptive cell counts. No confirmatory McNemar per cell (parent prereg flagged the multiple-testing load: "require at least two LIFT categorizations for a finding claim"). Zero JOINT-LIFTs found → no McNemar runs this round.

### Pre-registration fidelity checklist (principle 23)

- [x] Every outcome row tested (JOINT-LIFT, LIFT-AT-COST, CEILING-STABLE-NULL, GLOBAL-COLLAPSE, INTERMEDIATE). Observed 0 JOINT-LIFT, 0 LIFT-AT-COST, 3 CEILING-STABLE-NULL, 2 GLOBAL-COLLAPSE, 1 INTERMEDIATE maps cleanly onto the NULL aggregate row with the INTERMEDIATE cell triggering the pre-registered "one more block" commitment.
- [x] Sweep execution: §v2.3 grid (120 configs) + Pair 1 grid (120 configs) ran as committed at `9455d04`. No mid-run deferrals at the grid level. (min_run_length axis was dropped at design time — documented as "future grid extension" in the resolved-decisions note; NOT silently skipped.)
- [x] No mid-run parameter changes. Grid = {K ∈ {3, 5}, bp ∈ {0.0, 0.5, 1.0}} × n=20 as pre-registered.
- [~] Diagnostics partially completed: aggregate per-cell BOTH counts reported; per-seed BOTH-solve tables **deferred**; per-seed best-fitness **deferred**; per-cell attractor-category classification reported only for the INTERMEDIATE cell (K=3, bp=1.0) via §v2.15-bp1-k3-nexp below, **deferred** for the other 5 cells; population-entropy trajectory and diversity-collapse guard (prereg's `bond_protection=1.0 artifact` check) **deferred**; mean program length **deferred**; per-cell solver seed-overlap **deferred**. The aggregate counts are sufficient to reach the NULL verdict at the pre-registered gate; mechanism-dynamics interpretation (why bp=0.0 collapses vs bp=1.0 partially lifts) is therefore limited to outcome-level reasoning, not search-trajectory explanation. See Diagnostics ledger below for per-item reasons.

### Attractor-category inspection (principle 21 — triggered by INTERMEDIATE classification)

See §v2.15-bp1-k3-nexp below for the attractor inspection on (K=3, bp=1.0) expanded seeds.

### Interpretation

Scope: `within-decoder-family · n=20 per cell · at BP_TOPK v2_probe with grid {K ∈ {3, 5}, bp ∈ {0.0, 0.5, 1.0}} · on §v2.3 alt + §v2.6 Pair 1 alt`.

**The grid has no JOINT-LIFT cell at the pre-registered threshold.** Four cells preserve §v2.3's ceiling (both bp≥0.5 rows at both K); two cells collapse both tasks at bp=0.0; one cell (K=3, bp=1.0) hits Pair 1 = 10/20, just 2 seeds shy of the JOINT-LIFT bar. Per the prereg decision rule, this is **NULL — uniform no-lift**: chemistry-knob leverage across the (K, bond_protection_ratio) axes is bounded within the tested range. The Part 1 meta-learning ES over these two knobs specifically is **deprioritized** per the committed decision rule.

**The bp=0.0 collapse is a cleanly-identified failure mode.** At bp=0.0, mutation rate on bonded cells is zero (`mu * 0.0 = 0`) — the search cannot modify the extracted program at all, only non-bonded tape padding. The §v2.3 4-token body collapses to 3-4/20; Pair 1 collapses to 1/20. This is structural, not noisy: bond protection at its maximum strength is incompatible with useful search. Worth documenting as a project-wide mutation-design constraint.

**The bp=1.0 K=3 INTERMEDIATE signal is suggestive of an inverted mechanism.** bp=1.0 is the **no-protection / uniform-mutation** setting (bonded cells mutate at full rate); bp=0.5 is half-rate on bonded cells. The INTERMEDIATE signal suggests stronger protection than bp=1.0's uniform rate (i.e., the default bp=0.5, which reduces mutation on extracted cells) may hinder Pair 1 discovery, counter to the naive prior that "protection preserves useful structure." This signal triggered the pre-committed n-expansion §v2.15-bp1-k3-nexp.

**Mechanism rename check (principles 16 + 16b):**
- (a) Narrower than "chemistry-knob space has bounded leverage"? The claim is narrow by construction — scoped to (K, bp) only. Adding tape_length or min_run_length axes would test different knobs.
- (b) Broader than "bp=0.5 is the sweet spot"? The ceiling at bp=0.5 and bp=1.0 is identical on §v2.3 — the default isn't uniquely good, it's just one of two cells that preserve the ceiling. The narrower reading would be "(K, bp) direction doesn't produce a lift on Pair 1 without collapsing §v2.3."

### Caveats

- **Seed count:** n=20 per cell (load-bearing). The INTERMEDIATE cell at 10/20 received pre-committed n-expansion (§v2.15-bp1-k3-nexp).
- **Budget limits:** 1× compute (pop=1024, gens=1500). Whether a JOINT-LIFT cell emerges at 4× compute (parallel to §v2.14c stacking) is untested — and out of scope for this gate-experiment.
- **Grid coverage:** 2×3 = 6 cells; only two K values and three bp values. Finer K sweeps (K ∈ {1, 3, 5, 10}) or finer bp sweeps (bp ∈ {0.25, 0.5, 0.75}) could surface JOINT-LIFT cells inside the tested box that this grid missed. Deferred as a "future grid extension" per the prereg.
- **Overreach check:** The supported claim is "no JOINT-LIFT at the tested 6 cells." Claiming that "chemistry-knob leverage is universally bounded" would overreach. Claiming that "reduced mutation on bonded cells (bp<1.0) hinders hard-body discovery" would require the INTERMEDIATE n-expansion to confirm — see §v2.15-bp1-k3-nexp. Note that `bp=1.0` is the **no-protection / uniform-mutation** setting in this codebase's convention (bonded cells mutate at full rate), so the direction of the claim must track the parameter semantics carefully.
- **Open mechanism question:** the K=3 bp=1.0 partial lift (10→42% at n=60 combined, see below) is a real sub-gate mechanism signal. A finer bp sweep near 1.0 — or combining bp=1.0 with other decoder interventions (consume executor rule, tape_length) — might surface a JOINT-LIFT cell on a different axis.

### Diagnostics (prereg-promise ledger)

| Prereg item | Status |
|---|---|
| Per-cell aggregate BOTH-solve counts (both tasks) | Reported (per-cell tables) |
| Per-cell × per-seed BOTH-solve table | Deferred — aggregate counts suffice for the NULL verdict; per-seed tables unnecessary for the gate decision and not extracted at chronicle time. |
| Per-cell × per-seed best-fitness | Deferred — same reason. |
| Attractor-category classification per cell per task | Reported for INTERMEDIATE cell (K=3, bp=1.0) in §v2.15-bp1-k3-nexp; **deferred** for the other 5 cells. The CEILING-STABLE-NULL and GLOBAL-COLLAPSE verdicts do not hinge on per-winner genotype inspection at this scope. |
| Canonical-body-family rate per cell | Deferred except for (K=3, bp=1.0) n-expansion (see §v2.15-bp1-k3-nexp). |
| Generation-0 vs final population-entropy (diversity-collapse guard) | Deferred — the prereg listed this as the detection for the bp=1.0 diversity-collapse artifact. The §v2.3 ceiling at bp=1.0 (20/20) argues against diversity collapse at K=3/5; no direct measurement was made. Flagged here so future bp=1.0 mechanism claims must include this measurement. |
| Mean program length per cell | Deferred |
| Seed overlap with §v2.3 / §v2.6 Pair 1 reference solvers per cell | Deferred — bp=0.5 cells at K=3 and K=5 reproduce 20/20 on §v2.3 and 4–5/20 on Pair 1 within ±1 of committed references. Aggregate match is informative enough for the NULL verdict. |

### Findings this supports / narrows

- This result is itself a candidate for first-class `NULL` promotion to findings.md (principle 24) — it closes the Part 1 meta-learning gate on (K, bond_protection) axes and changes what downstream experiments should assume.
- Narrows: future Part 1 ES prereg (TBD) — the mainline §Approach 5+1 (ES + soft bonds) cannot use (K, bond_protection_ratio) as its starting-point search surface; either the grid must be expanded to new axes (tape_length, min_run_length, alphabet) or the Part 1 machinery must redirect toward executor-rule / body-topology interventions.

### Next steps (per prereg decision rule)

- **NULL (PASS rule inverted) →** chronicle the null; redirect Part 1 roadmap toward executor-rule interventions (§v2.14 arc continuation) and body-topology interventions (alphabet extension, e.g. §v2.14f's deferred FILTER_EQ proposal). ES machinery over (K, bp) is explicitly deprioritized. The INTERMEDIATE cell's n-expansion (§v2.15-bp1-k3-nexp below) is the pre-committed follow-up.
- **INTERMEDIATE n-expansion →** executed as §v2.15-bp1-k3-nexp.

---

## §v2.15-bp1-k3-nexp. n-expansion of INTERMEDIATE (K=3, bp=1.0) cell on Pair 1 (2026-04-16)

**Status:** `INCONCLUSIVE` · n=60 combined · commit `b179b50` (new block) + `9455d04` (existing 0-19 block) · confirms §v2.15 NULL verdict

**Pre-reg:** [Plans/prereg_v2-15-bp1-k3-nexp.md](../../Plans/prereg_v2-15-bp1-k3-nexp.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_15_nexp_pair1_k3_bp1.yaml`
**Compute:** ~9 min at 10-worker M1 (40 new configs)

### Question

Does the §v2.15 INTERMEDIATE cell (K=3, bp=1.0) on Pair 1 — measured at 10/20 BOTH — cross the JOINT-LIFT threshold (≥60% BOTH) when combined with a disjoint n=40 seed block, confirming or falsifying the §v2.15 Part-1 meta-learning gate outcome?

### Hypothesis (pre-registered)

Three disjoint outcomes: (1) JOINT-LIFT confirmed — §v2.15 grid flips from NULL to PASS at this cell → Part-1 ES over bond_protection gains a starting point; (2) NULL confirmed — the initial 10/20 was upper-tail noise; (3) borderline — one more expansion block.

### Result

| Block | BOTH solved | rate |
|---|---|---|
| Seeds 0-19 (existing, from §v2.15 grid_pair1) | 10/20 | 50% |
| Seeds 20-59 (new, this expansion) | 15/40 | 37.5% |
| **Combined n=60** | **25/60** | **41.7%** |

95% Wilson CI: (30.1%, 54.3%). Binomial tests (one-sided):
- P(X ≥ 25 \| true rate = 0.40) = 0.44 → **cannot reject** CEILING-STABLE-NULL floor
- P(X ≤ 25 \| true rate = 0.60) = 0.0014 → **cleanly rejects** JOINT-LIFT floor

**Matches pre-registered outcome:** `INCONCLUSIVE — within-noise` (24-29/60 band per prereg). 25/60 = 41.7% sits inside the pre-registered 40-48% window; the initial 10/20 was upper-tail noise on a true rate around 40-42%, above the bp=0.5 reference (20%) but below the JOINT-LIFT gate (60%).

**Statistical test:** exact binomial, two-threshold. Classification: **confirmatory**; family "§v2.15 decoder-grid family" at size 1 for this prereg → corrected α = 0.05 (no multiplicity penalty). The binomial rejection of the JOINT-LIFT floor at p = 0.0014 clears the α = 0.05 threshold and even the most aggressive FWER correction one could reasonably apply to this experiment family.

### Pre-registration fidelity checklist (principle 23)

- [x] Every outcome row tested (JOINT-LIFT, borderline, INCONCLUSIVE, NULL). Combined 25/60 maps cleanly onto INCONCLUSIVE.
- [x] Sweep execution: 40 new seeds 20-59 on exact pre-registered configuration; combined analysis over 0-59. §v2.3 ceiling re-measurement was explicitly skipped per the prereg's pre-declared scope (§v2.3 cell at (K=3, bp=1.0) was 20/20 in §v2.15 grid_v2_3 — not re-run here).
- [x] No mid-run parameter changes. Configuration matches the (K=3, bp=1.0) cell of §v2.15 exactly; only seed range differs.
- [~] Every statistical test and diagnostic named in the prereg appears below **or is explicitly deferred** in the ledger. The preregged **exact-binomial JOINT-LIFT-floor test** (confirmatory) is reported. The preregged **secondary exploratory McNemar** (bp=1.0 vs bp=0.5 on shared seeds 0-19) is **deferred** — raw discordance counts and effect-size would require loading §v2.15 grid_pair1 (K=3, bp=0.5) per-seed results and were not extracted at chronicle time. The bp=0.5 aggregate 4/20 reference is used for descriptive comparison only.

### Attractor-category inspection (principle 21 — mandatory per prereg)

Seeds 20-59 (n=40 new):

| Category | total | BOTH-solvers |
|---|---|---|
| canonical-6tok (has INPUT CHARS SLOT_12 SUM THRESHOLD_SLOT GT in order) | 9/40 | **9/40** (100% of category solve) |
| tokens-present-out-of-order (all 6 canonical tokens, wrong order) | 6/40 | 4/40 |
| has-threshold-slot-gt (partial structure) | 7/40 | 1/40 |
| IF_GT-compositional only (no THRESHOLD_SLOT) | 13/40 | 0 |
| Other (reduce_max paths, etc.) | 5/40 | 1/40 |
| **Total solvers in new block** | **15/40** | — |

**Canonical-6tok dominance among solvers: 9/15 = 60%.** This is **below** the prereg's ≥70% mechanism-coherent PASS guard. Non-canonical assemblies (6 of 15 solvers) — including 4 tokens-present-out-of-order and 1 other — contribute to the observed lift. The mechanism is not a clean "bp=1.0 → more mutation → cleaner canonical assembly"; some of the lift comes from alternative-assembly routes that bypass the canonical body structure.

### Interpretation

Scope: `within-decoder-family · n=60 (20 prior + 40 new) · at BP_TOPK(K=3, bond_protection=1.0) v2_probe tape=32 gens=1500 pop=1024 · on §v2.6 Pair 1 any_char_count_gt_{1,3}_slot alternation`.

**The 10/20 initial read was upper-tail noise.** At n=60 the solve rate lands at 41.7% with 95% Wilson CI (30.1%, 54.3%) — a tight window that cleanly excludes the 60% JOINT-LIFT threshold. §v2.15's NULL verdict stands firmly at the pre-registered gate.

**But the effect over reference is real, just sub-gate (exploratory observation).** bp=0.5 reference at K=3 on Pair 1 is 4/20 = 20% (n=20); bp=1.0 at combined n=60 is 41.7%. Relative to this 20% reference, the bp=1.0 combined rate is **directionally higher**. An exploratory reference-null calculation (`P(X ≥ 25 | true rate = 0.20) < 0.001`) suggests the lift over reference is unlikely to be chance, but this comparison is **not the pre-registered confirmatory test** — it uses a cross-block reference (§v2.15 bp=0.5 n=20) rather than matched new-seed bp=0.5 controls, and is therefore exploratory only. It does not alter the pre-registered NULL gate outcome. The bp=1.0 direction *does appear to help* Pair 1 relative to bp=0.5 reference, but not enough to clear the gate threshold the prereg set.

**The mechanism reading is narrower than the initial INTERMEDIATE signal suggested.** Only 60% of bp=1.0 solvers assemble the canonical 6-token body (vs the ≥70% prereg guard for mechanism-coherent PASS). 40% of solvers reach solve via non-canonical assemblies — scattered canonical tokens, compositional IF_GT routes, or alternative structures. "bp=1.0 = more mutation = more exploration" is partially validated, but the exploration includes non-canonical detours, not just cleaner canonical discovery.

**Per pre-registered decision rule for INCONCLUSIVE:** "Do NOT re-expand further — the 10/20 was noise. §v2.15 NULL stands. Part-1 deprioritization of (K, bond_protection) axes remains in effect." This commitment is honored.

**Mechanism rename check (principles 16 + 16b):**
- (a) Narrower than "bond_protection hurts hard-body discovery"? Yes — the effect is real but sub-gate, and the direction needs care about parameter semantics. The narrower statement is: "at K=3, setting bp=1.0 (no protection / uniform mutation) yields a measurable but modest (~20 percentage-point) lift on Pair 1 BOTH-solve relative to bp=0.5 reference, partially driven by non-canonical assembly routes. Insufficient to authorize meta-learning over (K, bond_protection) axes."
- (b) Broader? Not at this scope. The effect is specific to Pair 1's 6-token body and the tested (K, bp) cell.

### Caveats

- **Seed count:** n=60 combined (load-bearing). n-expansion was the pre-committed follow-up for the INTERMEDIATE classification; the verdict is load-bearing per principle 8.
- **Budget limits:** 1× compute (pop=1024, gens=1500) throughout. Whether bp=1.0 interacts with 4× compute on Pair 1 is untested.
- **Overreach check:** "bond_protection hurts hard-body discovery" was the initial tentative mechanism reading on 10/20. The n-expanded evidence supports a narrower "reduced mutation on bonded cells (bp<1.0) yields a sub-gate solve-rate deficit on Pair 1, partially via non-canonical assembly routes under bp=1.0." This narrower reading does NOT authorize the stronger claim. Parameter semantics matter: bp=1.0 is the no-protection / uniform-mutation setting, bp=0.5 is the default reduced-mutation setting on bonded cells.
- **Part-1 implications:** the NULL verdict at this cell does not preclude JOINT-LIFT on other decoder axes — tape_length, min_run_length, alphabet extension, or combined (bp × executor_rule) cells remain untested and could surface leverage.

### Diagnostics (prereg-promise ledger)

| Prereg item | Status |
|---|---|
| Per-seed BOTH-solve under (K=3, bp=1.0) seeds 20-59 | Reported (15/40; solver seeds: {21, 22, 28, 31, 33, 35, 39, 42, 43, 47, 49, 52, 53, 55, 57}) |
| Combined (0-59) per-seed solve matrix | Reported aggregate 25/60; seeds 0-19 solvers: {3, 5, 6, 10, 12, 13, 15, 16, 18, 19} |
| Winner-genotype attractor-category classification (seeds 20-59) | Reported (full table above) — canonical-6tok = 9, tokens-out-of-order = 6, partial = 8, IF_GT-only = 13, other = 5 |
| Preregged confirmatory test: exact-binomial JOINT-LIFT-floor | Reported (P(X ≤ 25 \| 0.60) = 0.0014, rejects JOINT-LIFT floor) |
| Preregged secondary exploratory McNemar (bp=1.0 vs bp=0.5 on shared seeds 0-19) | **Deferred** — raw per-seed disagreement counts would require loading §v2.15 grid_pair1 (K=3, bp=0.5) per-seed results and were not extracted at chronicle time. Aggregate comparison (10/20 vs 4/20 at n=20) is exploratory descriptive only. |
| Solver seed-set overlap analysis vs (K=3, bp=0.5) at n=20 | Deferred — as above; the prereg's subset-relationship mechanism-coherence check (bp=1.0 solvers ⊇ bp=0.5 solvers) is consequently unresolved. |
| Train-holdout gap | Deferred — §v2.15's grid showed near-zero gaps across all cells; extrapolated to hold. Not directly measured on the new block. |
| Mean best-fitness and mean-final-fitness per seed | Deferred — solve classification (≥0.999) is the primary metric; partial fitness does not change the verdict. |
| Wall time per run (drift check vs §v2.15) | ~13s per config — consistent with §v2.15 grid_pair1 throughput. No drift. |

### Findings this supports / narrows

- Confirms the §v2.15 **NULL — uniform no-lift** classification at the (K, bond_protection) axes. No JOINT-LIFT cell exists in the tested 2×3 grid at the pre-registered 60% threshold.
- Open (not yet consolidated): a narrower `bond_protection=1.0 partial-lift` observation — bp=1.0 at K=3 gives ~+20 percentage points over bp=0.5 reference on Pair 1 at n=60, partially via non-canonical assembly routes. This is a sub-gate mechanism signal worth chronicling but not worth promoting to findings.md at this scope.

### Next steps (per prereg decision rule)

- **INCONCLUSIVE — within-noise →** chronicle the cell classification at n=60 (done above). **Do NOT re-expand further** — prereg commitment honored. §v2.15 NULL stands. Part-1 deprioritization of (K, bond_protection) axes remains in effect. The narrower "partial-lift" observation may inform later decoder-axis exploration but does not change the gate outcome.

---

## §v2.4-proxy-4. Seeded-initialization probe on §v2.4 AND — design-flawed original (2026-04-16)

**Status:** `SUPERSEDED` · n=20 per arm · commit `9455d04` · superseded by §v2.4-proxy-4b

> **Superseded by §v2.4-proxy-4b (2026-04-16).** The seeded arms (seed_fraction ∈ {0.001, 0.01}) hit fitness 1.0 at gen 0 and triggered `run_evolution`'s early-termination guard (`fitness.max() >= 1.0 and not alternating`) at gen 1, so the GA never exercised mutation + selection over the full 1500-gen horizon. The result as-run tests **gen-0 dominance**, not the pre-registered **multi-generation maintainability** that distinguishes discoverability-limited from maintainability-limited readings. §v2.4-proxy-4b reruns with `disable_early_termination=true` and is the authoritative sweep. The analysis below is preserved for the reasoning trail; read §v2.4-proxy-4b for the current claim.

**Pre-reg:** [Plans/prereg_v2-4-proxy-4-seeded.md](../../Plans/prereg_v2-4-proxy-4-seeded.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_4_proxy4_seeded.yaml`
**Compute:** 5 min 8s at 10-worker M1

### Result (preserved for reasoning trail)

| seed_fraction | n | solve ≥.999 | mean_best | mean_hold | min..max gen |
|---|---|---|---|---|---|
| 0.0 | 20 | 0/20 | 0.921 | 0.909 | **1500..1500** (full) |
| 0.001 | 20 | 20/20 | 1.000 | 1.000 | **1..1** (early-term) |
| 0.01 | 20 | 20/20 | 1.000 | 1.000 | **1..1** (early-term) |

All 40 seeded arm winners' `best_genotype_hex` is **byte-for-byte identical** to the injected canonical 12-token CONST_0-first AND body — no evolution occurred.

### Design flaw (discovered post-run)

`evolve.py` lines 436–437 (panmictic) and 554–555 (island) break out of the generation loop when `fitnesses.max() >= 1.0` under non-alternating tasks. §v2.4's `sum_gt_10_AND_max_gt_5` is fixed (no alternation), so the guard fires. For §v2.4-proxy-4's seeded arms, `fitnesses.max()` hits 1.0 at gen 0 (the injected canonical body solves the task perfectly), triggering the break at gen 1. Arm 0 (no seeds) ran the full horizon normally and produced a clean drift check vs §v2.4's 0/20.

**What §v2.4-proxy-4 did measure (minor salvage):** Arm 0 reproduces §v2.4 baseline exactly (0/20, mean best 0.921, matching commit `e3d7e8a`). The seeded-init infra itself works as specified — 10 copies of the canonical tape at `seed_fraction=0.01` yielded 20/20 gen-0 dominance. The failure mode is an interaction between seeded-init and the early-term guard, not a bug in either individually.

**Fix in §v2.4-proxy-4b:** add `ChemTapeConfig.disable_early_termination` field (default `False` for hash stability), guard the two `break` statements with `and not cfg.disable_early_termination`. Commit `f10b066`.

### Findings this supports / narrows

- The infra works: seeded-init at `seed_fraction ∈ {0.001, 0.01}` reliably introduces the canonical body and selection picks it up at gen 0. This precondition holds for §v2.4-proxy-4b's maintainability test.
- Arm 0 is a matched-commit drift-check replication of §v2.4 baseline — documents that the seeded-init infra is hash-neutral at `seed_fraction=0.0` (pre-reg principle 11 preserved).

### Next steps

See §v2.4-proxy-4b below.

---

## §v2.4-proxy-4b. Seeded-initialization maintainability probe — full-horizon (2026-04-16)

**Status:** `PASS` (partial — R_2 full-population criterion deferred) · n=20 per arm · commit `f10b066` · supersedes §v2.4-proxy-4

**Pre-reg:** [Plans/prereg_v2-4-proxy-4b-seeded.md](../../Plans/prereg_v2-4-proxy-4b-seeded.md)
**Sweep:** `experiments/chem_tape/sweeps/v2/v2_4_proxy4b_seeded.yaml`
**Compute:** ~15.5 min (931s) at 10-worker M1

### Question

When the §v2.4 canonical 12-token AND body is injected into the initial population at fractions {0, 0.001, 0.01} and the GA runs the **full 1500 gens without early-termination**, is the canonical body retained (discoverability-limited) or displaced by the single-predicate proxy basin (maintainability-limited)?

### Hypothesis (pre-registered)

Three disjoint readings: (1) discoverability-limited — seeded bodies retained; §v2.4's 0/20 is a reachability failure; (2) maintainability-limited — seeded bodies displaced; basin is selection-level; (3) both — partial retention.

### Result

| seed_fraction | n | solve ≥.999 | mean_best | mean_hold | gens run | best-of-run ≡ canonical |
|---|---|---|---|---|---|---|
| 0.0 | 20 | **0/20** | 0.921 | 0.909 | 1500 (full) | 0/20 |
| 0.001 | 20 | **20/20** | 1.000 | 1.000 | **1500 (full)** | **20/20 exact match** |
| 0.01 | 20 | **20/20** | 1.000 | 1.000 | **1500 (full)** | **20/20 exact match** |

All 40 seeded runs completed the full 1500 generations under mutation + tournament selection, and **every single final-gen best-of-run genotype is byte-for-byte identical to the injected canonical 12-token AND body**. Arm 0 reproduces §v2.4 = 0/20 (drift check ✓).

**Matches pre-registered outcome:** `PASS — discoverability-limited` **at 2 of 3 criteria**; the third criterion is **partial**. `F_1 ≥ 15/20` (✓ 20/20), `F_2 ≥ 18/20` (✓ 20/20), `R_2 ≥ 0.3` — **partial discharge**: best-of-run layer trivially satisfies this (20/20 exact canonical across all 40 seeded runs), but the prereg defines `R_i` as **final-population retention rate** ("fraction of the final pop whose extracted program matches the canonical body within edit-distance ≤ 2"), which requires `decode_winner.py` on each run's final population — not extracted at chronicle time. The PASS verdict here is therefore **provisional** at the population-retention layer; full-population inspection is a queued follow-up. Per principle 2 follow-up, this technically does not match any pre-registered outcome row verbatim; it matches the F_1/F_2 components of PASS while deferring R_2.

**Statistical test:** paired McNemar Arm 0 vs Arm 1 and Arm 0 vs Arm 2 on shared seeds. Arm 0 = 0/20 across all seeds; Arm 1 = 20/20; Arm 2 = 20/20. Discordance: b=0 (Arm-0 solved, seeded didn't), c=20 (seeded solved, Arm-0 didn't). χ² with continuity correction = (|0-20|−1)²/20 = 361/20 = 18.05. p < 0.0001 two-sided. **Classification:** confirmatory; family **"proxy-basin family"**. Current family-size count is **deferred to a separate FWER audit** (see task #19) because several adjacent experiments in the arc were run without explicit confirmatory/exploratory classification (§v2.4-proxy, §v2.4-proxy-2, §v2.12) and cannot be retroactively counted as confirmatory without a compliance recommit per principle 22. Raw McNemar p < 0.0001 clears α=0.05 comfortably and would clear any plausibly-sized family (family size up to 50 would keep corrected α ≥ 0.001).

### Pre-registration fidelity checklist (principle 23)

- [~] Every outcome row from the prereg was tested for its F_i components (PASS-discoverability, PARTIAL-leaky, FAIL-maintainability, ARM-0-DRIFT). **Partial**: the PASS row's `R_2 ≥ 0.3` (final-population retention) criterion was not executed — only best-of-run was inspected. The verdict is therefore a partial discharge of the PASS row, not a full match; principle 2 follow-up applies.
- [x] Sweep execution: all 3 arms × 20 seeds ran the full 1500 gens as committed at `f10b066`. No mid-run deferrals.
- [x] No parameter / sampler / seed changes after prereg commit.
- [~] Diagnostics partially completed: per-seed best-of-run reported (20/20 exact canonical in both seeded arms); per-seed best-fitness reported (all 1.000 in seeded arms); **deferred**: per-gen population-entropy trajectory, lineage tree-distance sample on retained canonical bodies, and `decode_winner.py` on final-population individuals (only best-of-run inspected). The deferred population-layer items are what the prereg's `R_i` criterion actually requires; the current PASS verdict is provisional on best-of-run and has not yet discharged the population-layer criterion.

### Attractor-category inspection (principle 21 — triggered by too-clean signature 20/20)

The best-of-run on **every single seeded run** is the exact canonical tape (hex `0201121008010510100708110000000000000000000000000000000000000000`). No byte-level drift over 1500 gens of mutation at rate 0.03 × 32 cells per individual × pop=1024 individuals. This is a strong-attractor signature at the top of the distribution.

**Interpretation at the best-of-run layer:** the canonical 12-token body with 20 NOP tail is an **absorbing state for best-of-run** under BP_TOPK preserve selection on `sum_gt_10_AND_max_gt_5`. Any mutated descendant of a seeded canonical body that produces fitness < 1.000 loses tournament selection to an unmutated canonical copy elsewhere in the population (seeded at ~1 or ~10 individuals per gen-0 population). The attractor holds at the best-of-run level throughout the horizon.

**What best-of-run dominance does NOT tell us:** the **full-population retention rate** `R` (fraction of final-population individuals whose extracted program matches the canonical body within edit-distance ≤ 2). Mutations accumulate in non-best individuals; `R` in the full population could be <1.0 even when best-of-run is always canonical. This is the deferred `decode_winner.py on full population` inspection. For the PASS-discoverability verdict the best-of-run layer is sufficient (it demonstrates selection preserves the canonical body at the top of the distribution, which is what "maintainability" means operationally), but the narrower mechanism reading about *full-population* retention dynamics is open.

### Interpretation

Scope: `within-family · n=20 per arm · at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) v2_probe disable_early_termination=true preserve · on sum_gt_10_AND_max_gt_5 natural sampler · seeded canonical body retained at best-of-run layer under full-horizon mutation + selection pressure`.

**At the best-of-run layer, §v2.4's 0/20 looks like a discoverability failure.** When the canonical AND body is present in the initial population — even as 1/1024 (0.1%) — selection fixates on it at gen 0 and retains it at best-of-run for the full 1500 gens. The proxy basin does not displace the best-of-run individual. At this layer, the basin prevents *reaching* the canonical body under uniform-random initialization; it does not appear to dislodge the best individual once one is present. **This reading is provisional on the best-of-run layer only** — the prereg's `R_2 ≥ 0.3` criterion for population-level retention is deferred, and a full-population `decode_winner.py` inspection could still reveal that the canonical body does not spread beyond the seeded individuals under drift, which would weaken the "search-trajectory phenomenon" framing into a narrower "best-of-run absorbing state" framing.

**Implication for Part-1 meta-learning direction (contingent on full-population confirmation).** Under `proxy-basin-attractor` (as understood pre-§v2.4-proxy-4b) the basin could have been either: (i) an unreachable region that selection can't steer toward; or (ii) a region selection actively steers *away from* even when the canonical body is present. §v2.4-proxy-4b's best-of-run evidence rules out the strong form of (ii) — selection does not displace the canonical body from the top of the population under BP_TOPK preserve. If full-population retention confirms, Part-1 meta-learning should therefore prioritise **exploration / diverse initialization** operators over **selection-pressure interventions**. This directional conclusion holds under best-of-run evidence; population-level confirmation tightens it.

**Mechanism rename check (principles 16 + 16b):**
- (a) Narrower than "discoverability-limited"? Yes — the verdict is at best-of-run layer. A broader / stronger claim ("the canonical body dominates the full population under mutation") would require the deferred full-population retention measurement. The current claim is narrow-best-of-run.
- (b) Broader than "on this specific task + decoder"? Potentially — the reading motivates analogous seeded-init probes on other `proxy-basin-attractor` family members (§v2.4-proxy, §v2.4-proxy-2, §v2.12, §v2.14b all show basin-trapping under random-init on similar AND-composition tasks). Whether those probes would replicate the best-of-run retention pattern is an open question this experiment does not settle.

### Caveats

- **Seed count:** n=20 per arm (load-bearing; matches parent §v2.4-proxy-4's seed block for cross-sweep comparability).
- **Budget limits:** pop=1024, gens=1500, BP_TOPK preserve, k=3, bp=0.5. Whether the PASS holds under Arm A (no extraction), consume executor rule, or decorr samplers (§v2.4-proxy-2 setup) is untested. Each could in principle flip the verdict.
- **Overreach check:** the supported claim is "best-of-run canonical body retained under full horizon at BP_TOPK(k=3,bp=0.5)". The implicit stronger claim "selection-pressure is uniformly non-adversarial to the canonical body" overreaches — the best-of-run measurement does not settle full-population dynamics.
- **Cross-commit baseline:** Arm 0 at 0/20 with mean best 0.921 matches §v2.4 baseline (commit `e3d7e8a`) within ±0.001. No drift.
- **Shared-seed-RNG signature:** all 20 seeds produce identical best-of-run across both seeded arms. This is the **expected** pattern when the seeded individual has fitness 1.000 at gen 0 and mutation is unable to improve it — it is not a confound for the PASS verdict, but it is also not additional evidence beyond "the seeded individual dominates."

### Diagnostics (prereg-promise ledger)

| Prereg item | Status |
|---|---|
| Per-seed × per-arm F_AND + best-of-run fitness + holdout gap | Reported (per-arm table above; all seeded arms 20/20 with holdout 1.000, gap 0.000) |
| Retention rate per arm (final-pop canonical-body match within edit-distance ≤ 2) | **Deferred at full-population layer**; reported at best-of-run layer (20/20 exact match for both seeded arms). Full-population retention requires `decode_winner.py` on each run's final population — not extracted at chronicle time. |
| Population-entropy trajectory per arm (gen 0 / 100 / 500 / 1000 / 1500) | **Deferred** — not extracted from history.npz at chronicle time. The best-of-run signature is sufficient for the PASS verdict; entropy trajectory would sharpen the full-population-retention mechanism reading. |
| Winner-genotype attractor-category classification per arm | Reported (best-of-run is exact canonical across both seeded arms; Arm 0 at 0/20 solvers). |
| Lineage tree-distance sample on retained canonical bodies | **Deferred** — would require per-gen tracking; the zero-mutation best-of-run signature is prima facie evidence that the canonical body is in a mutation-viable neighborhood smaller than the mutation operator can cross in one step (mutations that move off canonical almost always reduce fitness, and uniform tournament selection filters them out). |
| Per-run wall time (drift check vs §v2.4-proxy-4) | ~15.5 s per run vs §v2.4-proxy-4's 0.2 s for seeded arms — ~77× longer, consistent with running 1500 gens instead of 1 gen. Arm 0 at ~150 s per run matches §v2.4-proxy-4's Arm 0 (full 1500 gens). Drift check ✓. |
| Solver seed overlap with §v2.4-proxy-4 Arms 1/2 | 20/20 overlap (both sweeps have all 20 seeds solving on both seeded arms; the difference is only in whether the run continued past gen 1). |

### Findings this supports / narrows

- **Narrows:** `proxy-basin-attractor` ([findings.md](findings.md#proxy-basin-attractor)) — scope boundary adds: "at the best-of-run layer, the basin does not displace the canonical AND body once seeded: selection maintains it at best-of-run across 1500 gens of mutation pressure. The basin prevents reaching the canonical body under uniform-random initialization; best-of-run displacement-from-canonical is ruled out at this scope. Whether full-population retention follows the same pattern is deferred to a queued `decode_winner.py` inspection." This narrowing rules out best-of-run displacement as the mechanism; it does not yet rule out the stronger population-drift reading.
- **Re-scopes Part-1 meta-learning direction (directional, contingent):** best-of-run evidence favors exploration / diverse-initialization operators over selection-pressure interventions. Population-layer confirmation tightens the commitment.

### Next steps (per prereg decision rule)

- **PASS (provisional at best-of-run) →** `/research-rigor promote-finding` to narrow `findings.md#proxy-basin-attractor` scope with the best-of-run evidence and the population-layer-deferral noted in the claim header. Queue the population-layer `decode_winner.py` inspection on this sweep's final-population output to discharge the `R_2 ≥ 0.3` criterion (no new sweep needed — analysis on existing `history.npz` / `result.json` artifacts only). Draft Part-1 Phase 1 prereg focused on exploration operators. E-count / Arm A replication queued as a cross-decoder probe.


- [architecture.md](architecture.md) — v1 specification.
- [experiments.md](experiments.md) — v1 experimental record (§10, §v1.5a-binary, §v1.5a-internal-control referenced throughout).
