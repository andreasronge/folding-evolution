# Architecture: Chemistry-Tape GP — v2 probe

**Relationship to v1:** v1 is complete and its findings are authoritative. See [architecture.md](architecture.md) for the v1 specification and [experiments.md](experiments.md) for the v1 experimental record (§1 through §v1.5a-internal-control). This document specifies a **v2 probe** — an intermediate expansion *between* v1 and full v2 folding-Lisp parity — designed to answer one sharp scientific question before committing to full v2 engineering.

## North star

> **Does chem-tape's body-invariant-route mechanism (§10 K-alternation + §v1.5a-binary slot-indirection) scale with expressivity, or is it a small-representation artifact?**

Two outcomes, two distinct research directions:

- **Mechanism scales** → chem-tape is a genuinely scalable evolvability representation. Full v2 (folding-Lisp parity + §v3 chemistry ablation) is a justified engineering push with a real mechanism story to tell.
- **Mechanism doesn't scale** → chem-tape's v1 findings are a minimum-viable-representation story. The paper-level claim narrows to v1 scope. Full v2 becomes primarily capability engineering, not mechanism research.

A third outcome — partial scaling with characterizable limits — is also possible and would define a focused follow-up.

This replaces the v1-architecture.md "v2 — expressivity parity" item, which is now deferred pending the v2-probe outcome.

## What v1 established (summary)

The v1 work (full detail in [experiments.md](experiments.md)) converged on a narrow but defensible positive claim:

> Environmental forcing produces cross-regime compatibility when the representation offers a body-invariant route across regimes.
> - Decode route: §10 K-alternation (7/20, zero flip cost)
> - Task-level indirection route: §v1.5a-binary slot-12 indirection (20/20, zero flip cost)
> - Internal-control falsification: §v1.5a-internal-control matched-everything pair → 0/20 (framework limit)

Best fixed baseline on sum_gt_10: **K=3 r=0.5 panmictic at 11/20**. All v2-probe experiments inherit this as the GA baseline.

Open questions explicitly not answered in v1:
- Whether mechanisms survive at richer expressivity (the v2-probe question).
- Whether the G→P mapping itself can be evolved (secondary direction below).
- External validity on order-sensitive, memory-requiring, non-threshold-arithmetic tasks (requires alphabet expansion = this document's scope).

## Scope: intermediate expansion

**Not** full folding-Lisp parity. Not quotation tokens, not structured-record inputs, not higher-order combinators. The v2 probe adds a small, targeted set of primitives chosen to (a) enable mechanism tests at richer expressivity, (b) address the specific internal-control falsification §v1.5a-internal-control identified, (c) keep implementation cost low (~1-2 weeks, not months).

### Inherited from v1 (unchanged)

v1 primitive ids 0-13 (`alphabet.py`): `NOP=0, INPUT=1, CONST_0=2, CONST_1=3, CHARS=4, SUM=5, ANY=6, ADD=7, GT=8, DUP=9, SWAP=10, REDUCE_ADD=11, SLOT_12=12, SLOT_13=13`. Active mask is ids 1-13 (id 0 = NOP is inactive). `SLOT_12, SLOT_13` dispatch via `TaskAlphabet` to op names `OP_NOP, OP_MAP_EQ_R, OP_MAP_IS_UPPER` (v1). v1 also reserves ids 14-15 as separators (execute as NOP). v2 adds 6 primitives at ids 14-19, reassigning the previously-reserved ids, and shifts separators to 20-21. v1 ids 0-13 are semantically unchanged; `TaskAlphabet` extends its op-name vocabulary (see below).

**SUM vs REDUCE_ADD in v1 / v2-probe.** Both primitives exist and have *identical executor implementations* (pop intlist, push its sum — see `executor.py` `_op_sum` and `_op_reduce_add`). `REDUCE_ADD`'s comment marks it as a placeholder for a higher-order reduce introduced in full v2. **Because higher-order combinators are explicitly out of scope for the v2 probe (see "Scope hygiene"), `REDUCE_ADD` remains a semantic alias for `SUM` throughout this document.** Task bodies in [experiments-v2.md](experiments-v2.md) use `SUM` for aggregation; §v2.5's aggregator-variation framing compares `REDUCE_ADD` (≡ `SUM` in v2-probe) against the new `REDUCE_MAX` — the distinction is nominal at v2-probe scale and only becomes semantically real at v2-full.

### Proposed alphabet expansion (5 primitives + 1 for §v2.3)

| id | primitive | semantics (precise) |
|----|-----------|---------------------|
| 14 | `MAP_EQ_E`       | array op: map each char `c` in top-of-stack array to `1 if c == 'E' else 0`. Stack underflow → push 0. |
| 15 | `CONST_2`        | push integer literal `2`. No stack consumption. |
| 16 | `CONST_5`        | push integer literal `5`. No stack consumption. |
| 17 | `IF_GT`          | value-level selector (eager). Pop three integers — `else_val`, `then_val`, `cond` (in that stack order, `cond` on top). Push `then_val if cond > 0 else else_val`. Both branches are already-evaluated values; not a control operator. `cond > 0` is **strictly** positive (0 → else). Any underflow → push 0. |
| 18 | `REDUCE_MAX`     | array op: reduce top-of-stack array to `max(elements)`. Empty array → push `0` (matches `REDUCE_ADD`'s empty-sum convention). Underflow → push 0. |
| 19 | `THRESHOLD_SLOT` | push integer constant whose value is task-bound via `TaskAlphabet.threshold: int`. No stack consumption. Added specifically for §v2.3 (constant-slot indirection). |

Reasons for each:

- **MAP_EQ_E**: v1 slot_12 can only bind to `MAP_EQ_R` or `MAP_IS_UPPER`. Adding `MAP_EQ_E` enables multi-map-binding tasks and richer slot-indirection testing at v2 scale.
- **CONST_2, CONST_5**: direct integer literals. v1's `sum_gt_5` and `sum_gt_10` required ADD-chains to build their constants; direct literals make the body shorter and remove one confound in §v2.3.
- **IF_GT**: enables compositional tasks that v1's scan-map-aggregate model cannot express. Value-level selector (not control flow) — both operands always evaluated before IF_GT executes.
- **REDUCE_MAX**: pairs with existing `REDUCE_ADD` for aggregator-shape variation at matched body settings.
- **THRESHOLD_SLOT**: the direct analogue of v1's slot_12 but binding an integer constant. Makes §v2.3 a clean body-invariant-route test — both sum_gt_5_slot and sum_gt_10_slot share the identical body `INPUT SUM THRESHOLD_SLOT GT`; only the task's bound integer differs.

### Slot-binding generalization (explicit design commitment)

The v2 probe **extends** v1's slot mechanism rather than holding it fixed. `TaskAlphabet` is generalized so existing `slot_12` and `slot_13` can bind to any of the new map/aggregator primitives (MAP_EQ_E, REDUCE_MAX), not just the v1 map ops. `THRESHOLD_SLOT` adds a third slot-binding channel for integer constants.

This is the mechanism under test. v1's §v1.5a-binary demonstrated that slot-indirection absorbs *op* variation across regimes (20/20 BOTH); v2 tests whether this generalizes to (a) a broader op set (§v2.2) and (b) *constant* variation (§v2.3).

### Alphabet / tape dimensions

- Token ids 0-19 are primitives (20 total, up from v1's 14 — counting active ids 1-13 + NOP at 0). Separator ids shift: `SEP_A = 20`, `SEP_B = 21`. Effective alphabet size 22.
- **Tape cell storage:** v1 stores tokens in the low nibble of a `uint8` (per `alphabet.py`'s module docstring — 4-bit tokens, 16-value range). The v2 alphabet's max id is 21, which requires 5 bits and **crosses the 4-bit boundary**. The storage byte remains `uint8` (no packing change), but any v1 code path that assumes "low nibble only" must be audited: the `alphabet.py` module docstring needs updating, and any hash / display / mask logic keyed on the 4-bit assumption (e.g., `& 0x0F`) must be located and widened. Estimated audit effort: a grep for `0x0F`, `nibble`, and `N_TOKENS == 16` across the executor and tape-viz code; small scope but mandatory before v2 runs.
- **Tape length: fixed at 32 (unchanged from v1).** 32 cells was sufficient for v1's 14-token active alphabet. The v2 probe's 20-token active alphabet is denser, but holding tape length constant eliminates one confound when comparing v2-probe solve rates to v1 baselines. If v2 experiments show systematic under-capacity (maximum observed scaffold length saturating at tape bound across all seeds), extending to 48 cells is queued as a separate axis — not rolled into the probe.
- Mask definitions (`ACTIVE_MASK`, `NON_SEPARATOR_MASK`) extend to ids 0-19 active, 20-21 separators.

### Scope hygiene

**Deliberately out of scope for the v2 probe:**
- Full folding-Lisp operator set (quotation, structured records, field access): too big for a probe.
- Evolvable alphabet / slot bindings: separate "can the mapping be evolved" direction (below).
- Higher-order combinators (true map/filter/reduce as first-class): v2-full scope.
- New decode rules or bond mechanisms: these are v3 ablation territory; don't confound with expressivity.

The probe adds capability along one axis (primitive set) while holding everything else (decode, bond rule, protection semantics, island structure) fixed at the v1 best-known configuration.

## New task space enabled by the expansion

The new primitives unlock roughly four new task classes useful for mechanism testing:

1. **Multi-mapping tasks** (using MAP_EQ_R + MAP_EQ_E together): "has_R_and_E" — binary, short-scaffold, requires using two slots coherently. Pairs with existing has_at_least_1_R and has_upper for an extended §v1.5a-binary analogue.

2. **Constant-slot threshold tasks** (using THRESHOLD_SLOT): `sum_gt_5_slot`, `sum_gt_10_slot` — both use the identical body `INPUT SUM THRESHOLD_SLOT GT`; only the task's bound `threshold` value differs. This is the sharpest body-invariance test: two tasks whose required programs are *token-sequence-identical*, differing only in a slot-bound integer. §v2.3 tests whether slot-indirection absorbs constant variation the way §v1.5a-binary showed it absorbs op variation.

3. **Conditional tasks** (using IF_GT): "if sum>threshold output count-R else 0" — compositional depth, requires the body to use multiple primitives coordinated by a conditional. Tests mechanism scaling to compositional structure.

4. **Aggregator-variation tasks** (using REDUCE_MAX): `max_gt_threshold` — same input space as sum-based tasks but different reduction. Paired with sum-based tasks, tests whether aggregator shape breaks body-invariance.

Detailed task specifications are in [experiments-v2.md](experiments-v2.md).

## Implementation surface (executor changes)

The v1 executor (`src/folding_evolution/chem_tape/executor.py`) dispatches on token id. Changes required:

- New dispatch entries for MAP_EQ_E, CONST_2, CONST_5, IF_GT, REDUCE_MAX, THRESHOLD_SLOT with the precise semantics above (stack-underflow convention: push 0; eager branch evaluation for IF_GT).
- Token-id map updates in `alphabet.py`; separator ids shift from v1's (14, 15) to (20, 21).
- `ACTIVE_MASK` / `NON_SEPARATOR_MASK` extend to cover ids 0-19 as active, 20-21 as separators.
- `TaskAlphabet` extended so `slot_12` and `slot_13` can bind any of MAP_EQ_E, REDUCE_MAX (in addition to v1's MAP_EQ_R, MAP_IS_UPPER, NOP). A new `threshold: int` field binds the value pushed by THRESHOLD_SLOT. This is the v2 probe's core mechanism-scaling lever; §v2.2 and §v2.3 depend on it.
- New task builders in `tasks.py`: `make_any_char_is_E_task`, `make_sum_gt_slot_task` (slot-bound threshold), etc. Full task specs in [experiments-v2.md](experiments-v2.md).

**Hash stability:** v1 configs continue to hash unchanged. New primitives only exist when v2-probe sweeps enable them via an `alphabet: "v2_probe"` config field (default `"v1"`). `threshold` is excluded from the hash when `alphabet="v1"`.

**Backend and compute.** v2-probe sweeps use the MLX backend + Rust executor path (`_folding_rust.rust_chem_execute_batch`) — same as current v1 sweeps. Experiment compute estimates in [experiments-v2.md](experiments-v2.md) assume 4-worker parallelism; empirical v1 reference sweep (`sum_gt_10_topk` at pop=1024, gens=1500, 20 seeds × 6 conditions) took ~17.6 min, which pins per-experiment expectations.

**Estimated implementation effort:** 1-2 weeks for a focused push (executor dispatches, alphabet wiring, new task builders, tests). Full v2 would be months.

## Secondary direction: evolvable G→P mapping (exploratory)

Separate from the primary mechanism-scaling question, the v2 probe provides a tractable entry point for the "can the mapping be evolved" question the broader discussion surfaced.

**Level 2 concrete probe:** add three new genotype-encoded header cells (cells 1, 2, 3; cell 0 remains the evolve-K header if active). **Each of the three cells independently selects** from 4 possible slot-binding assignments, yielding 4³ = 64 per-individual alphabet configurations. Independent selection means the three header loci are orthogonal — mutation and crossover combine bindings from different parents, and evolution explores the 64-configuration space via local moves rather than 1-of-64 jumps. (Contrast: a single header cell indexing into 64 pre-designed alphabet sets would be a lookup table, not evolvable. The independent-cell design is the evolvable version.)

**What this would establish:** whether evolution can discover task-appropriate primitive sets, or whether it collapses to a fixed assignment (analogous to §12's K-collapse). Connects to evolution-of-evolvability literature.

**Why this is level-2 priority, not primary:** the primary mechanism-scaling question must answer first — if the mechanism doesn't scale, evolvable mapping has no lever. If it does scale, evolvable mapping becomes a natural extension with real scientific weight.

## Decision tree

Four outcomes, each with an operational signature. The suite has **four graded experiments** (§v2.1, §v2.2, §v2.3, §v2.4) with pre-registered pass/fail columns, plus **one exploratory experiment** (§v2.5) that reports qualitative distributions rather than a hard pass/fail bit. Combined success criterion: **≥3/4 graded experiments land in their pre-registered "scales" column AND §v2.5's qualitative observations are consistent with scaling (no evidence against) → scales cleanly; fixed-baseline check in §v2.1 Part A declares swamped if ceilings are saturated; ≥3/4 graded in "does not scale" → does not scale; anything else → partial.** §v2.5 never flips a "scales" verdict to "does not scale" on its own — it contributes weight-of-evidence, not a veto.

```
v2 probe runs (mechanism tests at intermediate expansion)
│
├── SCALES CLEANLY  (≥3/4 graded experiments in "scales" column + §v2.5 consistent)
│   signatures:
│     - §v2.1 alternation solve rate ≥ fixed − 1 AND mean |Δbest| < 0.05
│     - §v2.2 Pair A AND Pair B both at 15+/20 BOTH
│     - §v2.3 constant-slot indirection at 15+/20 BOTH
│   → Full v2 engineering push justified
│   → v3 chemistry ablation becomes well-motivated
│   → Evolvable-mapping probe (level 2) becomes natural follow-up
│
├── SWAMPED BY EXPRESSIVITY  (mechanism has no headroom to demonstrate)
│   signature: §v2.1 Part A fixed-task baseline F_10_v2 ≥ 18/20 on sum-family
│   AND fixed-task baselines on string-family tasks ≥ 19/20. Alternation cannot
│   improve on ceilings. §v2.1's fixed-baseline gate declares this explicitly.
│   → Chem-tape's v1 mechanism findings may be partly a minimum-viable-rep
│     story; richer primitives make the tasks directly solvable without
│     needing the chemistry layer.
│   → Paper-level claim narrows: mechanism demonstrated at v1-scale,
│     supplanted by direct-primitive solvability at v2 scale.
│   → Full v2 unlikely to teach more about the chemistry layer.
│   → Decision: back to v1-scope paper or pivot research track.
│
├── DOES NOT SCALE  (≥3/4 graded experiments in "does not scale" column)
│   signatures: §v2.1 drop ≥ 0.2 or solve rate collapsed; §v2.2 BOTH ≤ 10/20
│   on both pairs; §v2.3 BOTH ≤ 5/20.
│   → v1 findings are rep-scale-specific.
│   → Paper-level claim confined to v1 scope; v2 full push primarily
│     capability engineering, not mechanism research.
│   → Consider pivoting research direction.
│
└── PARTIAL  (mixed outcomes, or 2/4 graded in any column)
    → Focused experiment to characterize the limit.
    → Narrower paper claim than full scaling, but still mechanistic.
    → Decide on full v2 based on which specific axes survive.
```

"Swamped" is a distinct branch from "does not scale" — both may produce similar alternation numbers, but have different mechanism implications and different follow-up actions. The swamp check is an explicit gating step in [experiments-v2.md §v2.1 Part A](experiments-v2.md) rather than inferred retrospectively.

## References

- [architecture.md](architecture.md) — v1 specification (unchanged; supersedes this document's "v2 expressivity parity" item only).
- [experiments.md](experiments.md) — v1 experimental record through §v1.5a-internal-control.
- [experiments-v2.md](experiments-v2.md) — pre-registered v2-probe experiment suite.
- [../folding/findings.md](../folding/findings.md) §4–§5 — original regime-shift mechanism that motivated chem-tape's v1.5 line.
