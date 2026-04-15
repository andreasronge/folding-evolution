# Experiments: Chemistry-Tape v2 probe

**Scope:** pre-registered experimental suite for the v2 probe defined in [architecture-v2.md](architecture-v2.md). Each experiment has a sharp pre-registered outcome table before implementation, informed by what §v1.5a-internal-control taught us about overfit framings. v1 experimental record lives in [experiments.md](experiments.md) and is unchanged by this document.

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

All per-seed artefacts under `experiments/output/2026-04-14/<entry_id>/`.

### Per-experiment outcomes

| experiment | headline | verdict (pre-reg) |
|---|---|---|
| **§v2.1 Part A** (fixed baseline `sum_gt_10_v2`) | F_10_v2 = **18/20** train, 18/20 holdout | **Swamp gate tripped** |
| **§v2.1 Part B** (K-alternation {3, 999}) | A_10_v2 = **15/20** = F_10_v2 − 3 | Partial (but measurement-limited by swamp) |
| **§v2.1 tape=48 headroom** | 18/20 train (15/20 holdout) | Comparable to tape=32; alphabet density is not a confound |
| **§v2.2 Pair A** {R, E} within-family | **20/20 BOTH** train, **20/20 BOTH holdout** | **Scales cleanly** |
| **§v2.2 Pair B** {R, upper} cross-family | **20/20 BOTH** (v2 replication of §v1.5a-binary's 20/20) | **Scales cleanly** |
| §v2.2 fixed baselines on string tasks | R / E / upper_v2 all **20/20** train and holdout | Swamp-check joint condition satisfied |
| **§v2.3** constant-slot indirection | **20/20 BOTH** pre-reg; **80/80 BOTH** across 4 seed blocks (0-79); zero-cost transitions at 100/100 flip events; max gap 0.016 | **Scales cleanly — headline result** |
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

However, the Partial label understates what the data shows. The two axes that **directly extend §v1.5a's mechanism claim** — op variation (§v2.2) and constant variation (§v2.3) — both scaled cleanly. The failure is on a different dimension (compositional depth via `IF_GT`) that was a stretch of the mechanism, not a core test of it. The §v2.1 swamp was pre-registered explicitly to trigger when direct primitives (`CONST_5 CONST_5 ADD`) remove selection pressure; tripping it is evidence the pre-reg was well-calibrated, not evidence against the mechanism.

### Headline framing for writeup

> Chem-tape's body-invariant-route mechanism scales cleanly on its two native generalization axes — op slot-indirection (§v2.2, 20/20 within-family + 20/20 cross-family) and **constant slot-indirection (§v2.3, 80/80 BOTH across 4 seed blocks, zero train-holdout gap, 100% instant flip recovery)**. §v2.1's pre-registered swamp check fired at v2 expressivity, moving `sum_gt_10_v2` out of the mechanism-testing range at this primitive set. Compositional depth via `IF_GT` (§v2.4) is open pending layout follow-up; the AND-task asymmetry (F_AND = 0/20 vs F_OR = 9/20 at matched compute) suggests a decode-structure placement constraint rather than a fundamental depth limit, but this distinction has not yet been tested.

The §v2.3 result is the strongest single mechanism claim in the suite. It directly recovers the §v1.5a-internal-control falsification at v2 scale: two tasks with **token-sequence-identical bodies** that differ only in a task-bound integer (`threshold = 5` vs `10`) produce 80/80 BOTH-solve with zero overfitting and zero-cost alternation transitions.

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

Results will be appended here once the sweep completes.

---

## References

- [architecture-v2.md](architecture-v2.md) — v2 probe architecture and decision tree.
- [architecture.md](architecture.md) — v1 specification.
- [experiments.md](experiments.md) — v1 experimental record (§10, §v1.5a-binary, §v1.5a-internal-control referenced throughout).
