# Experiments: Chemistry-Tape v2 probe

**Scope:** pre-registered experimental suite for the v2 probe defined in [architecture-v2.md](architecture-v2.md). Each experiment has a sharp pre-registered outcome table before implementation, informed by what §v1.5a-internal-control taught us about overfit framings. v1 experimental record lives in [experiments.md](experiments.md) and is unchanged by this document.

## North star (restated)

> Does chem-tape's body-invariant-route mechanism (v1 experiments.md §10 + §v1.5a-binary) scale with expressivity, or is it a v1-scale artifact?

Three possible regime outcomes define the decision tree in [architecture-v2.md](architecture-v2.md#decision-tree): scales cleanly, becomes irrelevant, partially survives. Each suite experiment below pre-registers which outcome its result would support.

## Suite at a glance

| # | experiment | target question | gates | ~compute |
|---|-----------|-----------------|-------|----------|
| §v2.1 | K-alternation replication at v2 expressivity | does §10's zero-cost cross-K signature survive? | — | ~15 min |
| §v2.2 | Multi-slot indirection test | does §v1.5a-binary's slot-indirection scale to >1 slot? | §v2.1 clean or partial | ~15 min |
| §v2.3 | Internal control at v2 | does §v1.5a-internal-control falsification persist, or does direct-constant availability resolve it? | §v2.2 clean | ~15 min |
| §v2.4 | Compositional depth probe | does the mechanism survive tasks using IF_GT? | §v2.2 or §v2.3 clean | ~15 min |
| §v2.5 | Aggregator-variation pair | does matched-body with different aggregators co-solve? | exploratory | ~10 min |

Estimated total: 1-1.5 hours of compute across all five, assuming pipelined. Each experiment is pre-registered independently so a clean negative at §v2.1 truncates the rest cleanly.

---

## §v2.1 K-alternation replication at v2 expressivity

**Question.** [experiments.md §10](experiments.md) showed zero-cost K-alternation compatibility (7/20 solve rate, 0.000 post-flip drop) on sum_gt_10 at K ∈ {3, 999}. Does this signature survive at v2 expressivity?

**Setup.**
- Task: sum_gt_10_v2 (same task as v1's sum_gt_10, but available constants include CONST_2 and CONST_5 so "10" is buildable via CONST_5 + CONST_5 + ADD instead of 1+1+1+1+1+1+1+1+1+1).
- K schedule: {3, 999} × period 300 × seeds 0-19.
- Base: K=3 r=0.5 panmictic, pop=1024, gens=1500.

**Pre-registered outcomes.**

| signature | interpretation |
|-----------|----------------|
| solve rate ≥ 7/20 AND mean \|Δbest\| < 0.05 | **Scales:** §10's signature reproduces at v2 expressivity. |
| solve rate > 7/20 AND mean \|Δbest\| < 0.05 | Expressivity amplifies the mechanism — chemistry becomes more valuable with richer primitives. |
| solve rate = 7/20 ± noise AND mean \|Δbest\| ≈ 0.2-0.3 | **Partial:** mechanism present but degraded. Richer alphabet introduces non-trivial flip costs. |
| solve rate drops significantly below 7/20 | **Does not scale:** v2 expressivity changes the reachability landscape in a way that hurts chem-tape's mechanism. |

**Caveat:** sum_gt_10_v2's fixed-task solve rate will likely be higher than v1's 11/20 (direct constants make the task easier). Pre-run a K=3 r=0.5 fixed baseline on sum_gt_10_v2 to establish max-of-fixed before interpreting alternation results. This is the §v1.5a pattern applied here.

## §v2.2 Multi-slot indirection test

**Question.** [experiments.md §v1.5a-binary](experiments.md) showed 20/20 cross-task solves when two tasks differed only in slot_12's op binding. Does this slot-indirection mechanism scale when the variation is across multiple slots?

**Setup.**
- New tasks:
  - `first_char_is_R`: task variant where slot_12 = MAP_EQ_R, REDUCE_MAX checks if first (actually max in this framing) is set.
  - `first_char_is_E`: same structure but slot_12 = MAP_EQ_E (using the new primitive).
  - `first_char_is_upper`: slot_12 = MAP_IS_UPPER.
- Schedule: alternate between pairs from {first_char_is_R, first_char_is_E, first_char_is_upper}. Task-level slot-12 variation is the only difference.
- Pair A: {first_char_is_R, first_char_is_E} — both use MAP_EQ_* variants.
- Pair B: {first_char_is_R, first_char_is_upper} — mixed MAP_EQ vs MAP_IS.
- Same K=3 r=0.5 panmictic baseline.

**Pre-registered outcomes.**

| Pair A result | Pair B result | interpretation |
|---------------|---------------|----------------|
| 18-20/20 BOTH | 18-20/20 BOTH | **Scales cleanly:** slot-indirection mechanism generalizes to any slot-12 variation. §v1.5a-binary was not specific to MAP_EQ_R/MAP_IS_UPPER pairing. |
| 18-20/20 BOTH | 0-10/20 BOTH  | **Partial:** indirection works within similar-family MAP ops but breaks across MAP families. Reveals a within-family vs across-family axis. |
| 0-10/20 BOTH on both | Mechanism does not scale — even direct slot-variation fails at v2 expressivity. Strong negative for the entire mechanism claim. |

**What this tests that §v1.5a-binary did not:** §v1.5a-binary was a single MAP_EQ_R ↔ MAP_IS_UPPER contrast. §v2.2 tests whether the 20/20 result was specific to that contrast or a general property of slot-level indirection.

## §v2.3 Internal control at v2 — does direct-constant availability resolve the falsification?

**Question.** [experiments.md §v1.5a-internal-control](experiments.md) falsified the basin × scaffold framework by showing {sum_gt_5, sum_gt_10} co-solve at 0/20 despite matching everything. Hypothesis: canalization occurred because the tasks required different constant-construction programs (build 5 vs build 10). With CONST_2 and CONST_5 directly available, both tasks can use literal constants with structurally identical programs. Does co-solve recover?

**Setup.**
- Tasks: sum_gt_5_v2 (uses CONST_5 directly), sum_gt_10_v2 (uses CONST_5 CONST_5 ADD).
  - Actually the sharpest test is to construct a program template where *the same token sequence* solves both under different task bindings. This requires either slot indirection for the threshold itself (making the threshold a task-bound constant) OR accepting that the tasks have *slightly* different optimal programs and seeing whether the canalization pattern still holds.
- Schedule: {sum_gt_5_v2, sum_gt_10_v2} × period 300 × seeds 0-19.

**Pre-registered outcomes.**

| BOTH solves | interpretation |
|-------------|----------------|
| 15+/20      | **Framework recoverable:** §v1.5a-internal-control's falsification was specifically about constant-construction cost. Direct constants restore co-solve. Narrower claim: basin × scaffold holds *when body-invariant routes are available*. |
| 0-5/20      | **Framework truly limited:** even direct constants don't resolve the canalization. Body-invariant-route mechanism is genuinely the load-bearing axis. §v1.5a-internal-control's falsification stands. |
| 6-14/20     | Partial recovery. Mixed picture; would need further analysis of which seeds recover. |

**Pre-implementation note:** if tasks can be constructed where the *literal same token sequence* works under both (via slot-binding the threshold constant), that's a cleaner test. The design decision is: do we want to test "direct constants help" or "body-invariant route restored"? Default: the latter, implemented via threshold-slot binding if tractable. Worth 30 minutes of design discussion before implementing.

## §v2.4 Compositional depth probe

**Question.** v1 tasks are all scan-map-aggregate (no compositional depth). IF_GT enables conditional-branching tasks. Does the mechanism survive at compositional depth > 1?

**Setup.**
- Task pair: {"sum_gt_10 AND has_upper", "sum_gt_10 OR has_upper"} — both compositional, both binary, same scaffold shape (SUM CONST_5 CONST_5 ADD GT {has_upper} IF_GT — rough sketch).
- Single schedule: alternation at period 300.

**Pre-registered outcomes.**

| BOTH solves | interpretation |
|-------------|----------------|
| 12+/20      | Mechanism survives compositional depth. Cross-regime compatibility isn't limited to single-reduction tasks. |
| 0-5/20      | Compositional depth breaks the mechanism. Chem-tape's body-invariant-route claim applies only to non-compositional task space. |
| 6-11/20     | Graded result — compositional depth reduces but doesn't eliminate compatibility. |

**Importance:** if §v2.4 fails but §v2.1-§v2.3 pass, the v2 probe ends with "mechanism scales up to compositional depth 1 but not beyond" — a clear, narrower-than-hoped result.

## §v2.5 Aggregator-variation pair

**Question.** Does matched-body differing in aggregator (REDUCE_ADD vs REDUCE_MAX) co-solve?

**Setup.**
- Tasks: "sum_of_chars_gt_10" (REDUCE_ADD on a MAP output), "max_of_chars_gt_5" (REDUCE_MAX on same MAP).
- Schedule: alternation at period 300.

**Pre-registered outcomes.**

| BOTH solves | interpretation |
|-------------|----------------|
| 15+/20      | Aggregator variation is absorbable via body-invariant route (slot-binding the aggregator). |
| 0-5/20      | Aggregator is a genuinely body-differentiating axis. Narrower mechanism claim. |

This is exploratory — primarily characterizes which structural variations are absorbable vs which force canalization.

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
