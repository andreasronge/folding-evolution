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

## References

- [architecture-v2.md](architecture-v2.md) — v2 probe architecture and decision tree.
- [architecture.md](architecture.md) — v1 specification.
- [experiments.md](experiments.md) — v1 experimental record (§10, §v1.5a-binary, §v1.5a-internal-control referenced throughout).
