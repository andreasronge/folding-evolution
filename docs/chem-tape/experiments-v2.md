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

Three possible regime outcomes define the decision tree in [architecture-v2.md](architecture-v2.md#decision-tree): scales cleanly, becomes irrelevant, partially survives. Each suite experiment below pre-registers which outcome its result would support.

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

Task: `sum_gt_10_AND_has_upper` — binary, returns 1 iff both `sum(input) > 10` AND `input` contains an uppercase char. A solving program computes both sub-predicates, leaves them on the stack, then uses `IF_GT` as an AND-selector. Example body structure (not the only valid program):

```
INPUT CHARS MAP_IS_UPPER ANY     # has_upper result → [hu]
INPUT SUM CONST_5 CONST_5 ADD GT # sum_gt_10 result → [hu, s]
CONST_0                          # else_val = 0       → [hu, s, 0]
SWAP                             # swap then reorder  → [hu, 0, s]
IF_GT                            # pops (else=0, then=hu, cond=s); if s>0 push hu else 0
```

Stack trace uses v1's existing primitives (INPUT, CHARS, MAP_IS_UPPER, ANY, SUM, ADD, GT, CONST_0, SWAP) plus v2's `CONST_5` and `IF_GT`. No unused primitives; `IF_GT`'s (else, then, cond) signature is respected.

Alternation schedule: `{sum_gt_10_AND_has_upper, sum_gt_10_OR_has_upper}` at period 300 × seeds 0-19, K=3 r=0.5 panmictic. The OR variant is the same body with a different last step (e.g., `SWAP CONST_1 SWAP IF_GT`, or a cleaner rewrite; the exact token sequence to swap between AND and OR is an implementation choice — what's pre-registered is that both tasks are binary, compositional, use only v2 primitives, and differ minimally).

**Fixed-task baselines.** Both tasks' fixed-task solve rates measured first (same as §v2.1's baseline-pairing pattern) to establish max-of-fixed per task. Alternation thresholds below are expressed relative to the lower of the two fixed baselines.

**Pre-registered outcomes.**

| BOTH solves | interpretation |
|-------------|----------------|
| ≥ lower fixed − 3 | **Scales:** mechanism survives compositional depth. Cross-regime compatibility isn't limited to single-reduction tasks. |
| 6-11/20 (or lower-fixed-minus-more-than-3) | **Partial:** compositional depth reduces but doesn't eliminate compatibility. |
| 0-5/20 | **Does not scale:** compositional depth breaks the mechanism. Chem-tape's body-invariant-route claim applies only to non-compositional task space. |

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

Combined outcomes from §v2.1-§v2.5 map to one of three regimes (full decision tree in [architecture-v2.md](architecture-v2.md#decision-tree)):

- **All-or-most scale (≥4/5 experiments in the "scales" column):** mechanism generalizes. Commit to full v2 + v3 chemistry ablation. Paper-level claim: chem-tape provides scalable evolvability via body-invariant-route mechanism.
- **Most-or-all fail to scale (≥4/5 in the "does not scale" column):** v1 findings are rep-scale-specific. Full v2 is primarily capability engineering. Paper-level claim narrows to v1 scope. Consider pivoting.
- **Mixed (no clear majority):** partial scaling with characterizable limits. Focused follow-up to nail the specific failure mode; paper-level claim is about mechanism scope rather than existence.

## What this suite does NOT test (explicitly out of scope)

- **Full folding-Lisp expressivity.** Quotation tokens, structured records, field access, higher-order combinators. This is full v2 scope, gated on v2-probe outcome.
- **Evolvable primitive set / alphabet.** The level-2 "can the mapping be evolved" direction. Queued as an exploratory probe contingent on v2-probe mechanism-scaling result.
- **New chemistry mechanisms.** Bond persistence variants, multi-pass bonding, irreversibility. These are v3 ablation territory; v2 probe holds chemistry fixed at v1 best configuration.
- **External validity on genuinely different task structures.** Order-sensitive, memory-requiring, non-threshold-arithmetic tasks. Some of these need further alphabet expansion beyond v2 probe scope; others (order-sensitive) need new executor semantics.

## Secondary direction queued: evolvable-mapping probe (level 2)

Described in [architecture-v2.md §Secondary direction](architecture-v2.md#secondary-direction-evolvable-gp-mapping-exploratory). Waits on v2-probe mechanism-scaling result.

## References

- [architecture-v2.md](architecture-v2.md) — v2 probe architecture and decision tree.
- [architecture.md](architecture.md) — v1 specification.
- [experiments.md](experiments.md) — v1 experimental record (§10, §v1.5a-binary, §v1.5a-internal-control referenced throughout).
