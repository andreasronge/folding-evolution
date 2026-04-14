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

### Proposed alphabet expansion (5 primitives)

| primitive | semantics | role |
|-----------|-----------|------|
| `MAP_EQ_E` | map each char to 1 if 'E' else 0 | enables multi-mapping tasks; pairs with existing MAP_EQ_R and MAP_IS_UPPER |
| `CONST_2` | push literal 2 | direct constant; removes the "build 2 via DUP/ADD" cost |
| `CONST_5` | push literal 5 | same; unblocks the §v1.5a-internal-control scenario cleanly |
| `IF_GT` | pop 3 values (else, then, cond); push `then if cond > 0 else else` | conditional dispatch; enables compositional tasks v1 cannot express |
| `REDUCE_MAX` | array reduce to max element | new aggregator; pairs with REDUCE_ADD for aggregator-variation tests |

Reasons for each:

- **MAP_EQ_E**: existing slot_12 can only bind to MAP_EQ_R or MAP_IS_UPPER. Adding MAP_EQ_E enables tasks like "has R and E both" or "first-char-of-type" that force multi-slot programs.
- **CONST_2, CONST_5**: §v1.5a-internal-control revealed that requiring different constants (10 vs 5) produces canalization even with matched basin and scaffold. Adding direct constants tests whether the framework survives when the "same body" criterion is genuinely achievable — both tasks can use literal constants without needing structurally different programs.
- **IF_GT**: enables compositional tasks (branch on a condition) that v1's pure scan-map-aggregate model cannot express. Lets us test whether the mechanism scales to compositional depth.
- **REDUCE_MAX**: pairs with existing REDUCE_ADD for aggregator-shape variation. Tasks like "max element > threshold" test whether aggregator variation alone breaks body-invariance.

Alphabet size grows from 14 active tokens (0-13) to 19 (0-18). Separator ids 14, 15 become 19, 20. Tape length may need to grow to compensate for the slightly denser alphabet. Detailed tokenization is an implementation decision.

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

2. **Direct-constant threshold tasks** (using CONST_2, CONST_5): `sum_gt_2_v2`, `sum_gt_5_v2`, `sum_gt_10_v2` — same as existing intlist tasks but using literal constants instead of built-up arithmetic. Directly tests §v1.5a-internal-control's framework limit — if different tasks now share the same scaffold token sequence (differing only in which CONST_* is used), do they co-solve?

3. **Conditional tasks** (using IF_GT): "if sum>threshold output count-R else 0" — compositional depth, requires the body to use multiple primitives coordinated by a conditional. Tests mechanism scaling to compositional structure.

4. **Aggregator-variation tasks** (using REDUCE_MAX): `max_gt_threshold` — same input space as sum-based tasks but different reduction. Paired with sum-based tasks, tests whether aggregator shape breaks body-invariance.

Detailed task specifications are in [experiments-v2.md](experiments-v2.md).

## Implementation surface (executor changes)

The v1 executor (`src/folding_evolution/chem_tape/executor.py`) dispatches on token id. Changes required:

- New dispatch entries for MAP_EQ_E, CONST_2, CONST_5, IF_GT, REDUCE_MAX.
- Token-id map updates in `alphabet.py`. Separator ids shift.
- `ACTIVE_MASK` / `NON_SEPARATOR_MASK` update to cover the expanded id range.
- `TaskAlphabet` gains capacity to bind additional slots if needed (but initially slot_12, slot_13 retain their v1 semantics; new primitives are direct-dispatched).
- New task builders in `tasks.py`: `make_has_R_and_E_task`, `make_sum_gt_2_task`, `make_sum_gt_5_v2_task`, etc.

Hash stability: v1 configs continue to hash unchanged (new primitives only exist when v2-probe sweeps enable them via an `alphabet: "v2_probe"` config field, defaulted to `"v1"`).

Estimated implementation effort: 1–2 weeks for a focused push, vs months for full v2.

## Secondary direction: evolvable G→P mapping (exploratory)

Separate from the primary mechanism-scaling question, the v2 probe provides a tractable entry point for the "can the mapping be evolved" question the broader discussion surfaced.

**Level 2 concrete probe:** add a genotype-encoded header field (beyond cell 0 which evolve-K already uses) that determines which subset of a meta-alphabet is active for this individual. Example: 3 header cells × 4 possible primitive-set indices → 64 alphabet configurations. Evolution discovers which primitive set suits the task.

**What this would establish:** whether evolution can discover task-appropriate primitive sets, or whether it collapses to a fixed assignment (analogous to §12's K-collapse). Connects to evolution-of-evolvability literature.

**Why this is level-2 priority, not primary:** the primary mechanism-scaling question must answer first — if the mechanism doesn't scale, evolvable mapping has no lever. If it does scale, evolvable mapping becomes a natural extension with real scientific weight.

## Decision tree

```
v2 probe runs (mechanism tests at intermediate expansion)
│
├── Mechanism scales cleanly
│   → Full v2 engineering push justified
│   → v3 chemistry ablation becomes well-motivated
│   → Evolvable-mapping probe (level 2) becomes natural follow-up
│
├── Mechanism becomes irrelevant (swamped by primitives)
│   → Chem-tape is a minimum-viable-rep story
│   → Paper-level claim narrows to v1 scope
│   → Full v2 not scientifically justified
│   → Consider pivot to different research track
│
└── Mechanism partially survives (scope limits characterizable)
    → Focused experiment to characterize the limit
    → Narrower paper claim than full scaling, but still mechanistic
    → Decide on full v2 based on residual mechanism strength
```

## References

- [architecture.md](architecture.md) — v1 specification (unchanged; supersedes this document's "v2 expressivity parity" item only).
- [experiments.md](experiments.md) — v1 experimental record through §v1.5a-internal-control.
- [experiments-v2.md](experiments-v2.md) — pre-registered v2-probe experiment suite.
- [../folding/findings.md](../folding/findings.md) §4–§5 — original regime-shift mechanism that motivated chem-tape's v1.5 line.
