# Chem-tape Findings — Durable Claims (Scope-Tagged)

This is the consolidated ledger of chem-tape's load-bearing claims. Each entry
is **scope-tagged** (methodology §18) and anchored to the experiments and
commits that produced it. New entries are promoted from
[experiments.md](experiments.md) / [experiments-v2.md](experiments-v2.md)
only when **(a)** at least one n≥20 experiment supports the claim, **(b)**
zero-compute mechanism inspection has surfaced a mechanism reading (not just
an aggregate solve count, methodology §3), and **(c)** the claim is
load-bearing for downstream work.

Status vocabulary: `ACTIVE` (current claim), `NARROWED` (later experiment
narrowed the scope), `FALSIFIED` (later experiment refuted the claim). See
[`docs/_templates/findings_entry.md`](../_templates/findings_entry.md) and
[methodology principles 5, 16, 17, 18, 19](../methodology.md).

---

## op-slot-indirection. Body-invariant route absorbs slot-bound op variation across MAP-family primitives at v2 expressivity (n=20 per pair, across-family).

**Scope tag:** `across-family` · `n=20 per pair × 2 pairs` · `at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) v2_probe alphabet` · `on shared body` `INPUT CHARS slot_12 ANY` `with slot_12 ∈ {MAP_EQ_R, MAP_EQ_E, MAP_IS_UPPER}`

**Status:** `ACTIVE` · last revised commit `320fc6b` · 2026-04-15

### Claim

When two binary tasks share a token-identical body and differ only in the
op bound to a single task slot, evolution discovers the body once and
solves both tasks via that body, with `THRESHOLD_SLOT`/`SLOT_12` absorbing
the task-distinguishing variation.

### Scope boundaries (what this claim does NOT say)

- Does not claim slot-indirection works for **arbitrary** ops or **arbitrary**
  body shapes — only the MAP-family ops on the 4-cell scan-map-aggregate
  body have been tested at v2.
- Does not generalize to op-binding for non-MAP slot positions (`slot_13`
  aggregator-variation is qualitative-only at v2; see
  [experiments-v2.md §v2.5](experiments-v2.md)).
- Tested only on length-16 string inputs over the 53-char alphabet at
  pop=1024 / gens=1500 / BP_TOPK(k=3, bond_protection=0.5).
- Open external-validity question: does the mechanism survive at smaller
  pop/gens budgets, or is the 20/20 a budget-saturation artifact?

### Mechanism reading (current)

**Current name:** `body-invariant-route mechanism (op-slot variant)`

**Naming history:**
- Initial: "decode breadth" (v1 §8 era) — falsified by §11/§v1.5a
- Narrowed: "quarantine via exclusion" (v1 §10 K-alternation reading)
- Narrowed: "body-invariant route" (v1 §v1.5a-binary post-mortem; current
  framing). The mechanism is a **shared body that exposes a task-bound
  slot** — neither decode breadth nor exclusion alone explains the cross-task
  solve pattern.

### Supporting experiments

| experiment | commit | n | what it establishes |
|---|---|---|---|
| [v1 §v1.5a-binary](experiments.md) | `4f9b02e` | 20 | original 20/20 cross-task solves on `{count_r, has_upper}` slot-12 pair |
| [v1 §10 K-alternation](experiments.md) | `8c26115` | 50 | environmental forcing produces cross-regime-compatible bodies (precondition lemma) |
| [§v2.2 Pair A](experiments-v2.md#v22) | `e3d7e8a` | 20 | within-MAP-family pair `{R, E}` 20/20 BOTH train and holdout |
| [§v2.2 Pair B](experiments-v2.md#v22) | `e3d7e8a` | 20 | cross-MAP-family pair `{R, upper_v2}` 20/20 BOTH (v2 replication of §v1.5a-binary) |
| §v2.2 fixed baselines | `e3d7e8a` | 20 × 3 tasks | `{R, E, upper_v2}` all 20/20 train+holdout (swamp-check satisfied) |

### Narrowing / falsifying experiments

None to date. The only adjacent narrowing is from the constant-indirection
finding below (different mechanism axis, not a narrowing of this claim).

### Implications for downstream work

- **Downstream experiments may assume:** task-alternation across MAP-family
  slot bindings will produce body-invariant solutions at this budget.
- **Downstream experiments must still test:** any new op-family extension
  (e.g., a `MAP_*` op outside the eq/is_upper family); any reduction in
  pop/gens budget; any non-string input domain for op-slot indirection.

### Review history

- 2026-04-15 — initial promotion from experiments-v2.md §v2.2 chronicle
  (commit `320fc6b`) after §v2.6 confirmed no narrowing in this axis.

---

## constant-slot-indirection. Body-invariant route absorbs slot-bound integer-constant variation across multiple body shapes (n=20 per pair, across-family with characterised edge).

**Scope tag:** `across-family` · `n=20 per pair × 4 pairs (1 with seed expansion to n=80)` · `at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) v2_probe alphabet` · `on body shapes` `INPUT SUM THRESHOLD_SLOT GT` `(integer)` `and` `INPUT REDUCE_MAX THRESHOLD_SLOT GT` `(aggregator)`

**Status:** `ACTIVE` · last revised commit `320fc6b` · 2026-04-15

### Claim

When two binary tasks share a token-identical body and differ only in a
task-bound integer constant exposed via `THRESHOLD_SLOT`, evolution discovers
the body once and solves both tasks via that body — extending the
op-slot-indirection mechanism from operator variation to constant variation
across at least three structurally distinct body shapes.

### Scope boundaries (what this claim does NOT say)

- Does **not** claim "constant-indirection is universal" — the string-domain
  body (`INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT`, 6 tokens) failed at
  4/20 BOTH despite components being present in 75-94% of evolved tapes.
  See [§v2.6 Pair 1 chronicle](experiments-v2.md#v26).
- Does not claim the mechanism is budget-free: failure on the 6-token body
  may resolve at higher pop/gens, but that is **not** tested.
- Tested only on intlist inputs of length 4 (over [0,9] and [0,12]) and one
  string-domain attempt that failed.
- Open external-validity question: does Pair 1 (string-count) solve at 4×
  compute, the way §v2.4-alt's threshold=5 task did under matched compute?

### Mechanism reading (current)

**Current name:** `body-invariant-route mechanism (constant-slot variant)`

**Naming history:**
- Initial: extension of "body-invariant route" from op-slot to constant-slot,
  proposed pre-§v2.3 (commit `4f0fe94`).
- Confirmed: §v2.3's 80/80 across 4 seed blocks demonstrates constant-slot
  variant works on the canonical sum body.
- Narrowed (Pair 1 edge): the mechanism's **discoverability** depends on
  body-shape topology — the 4-token bodies (Pair 2 sum_r12, Pair 3
  reduce_max) converge at ceiling, the 6-token CHARS-chain body
  (Pair 1) does not. Renaming candidate: "body-invariant route, 4-token
  shapes" — deferred until Pair 1's compute-scaling result decides whether
  the edge is structural or budget-dependent.

### Supporting experiments

| experiment | commit | n | what it establishes |
|---|---|---|---|
| [§v2.3](experiments-v2.md#v23) | `e3d7e8a` | 20 (pre-reg) + 60 (expansion) = 80 | `{sum_gt_5_slot, sum_gt_10_slot}` 80/80 BOTH; max\|gap\| = 0.0156; 399/400 zero-cost flip transitions |
| [§v2.6 Pair 2](experiments-v2.md#v26) | `0230662` | 20 | `{sum_gt_7_slot_r12, sum_gt_13_slot_r12}` 20/20 BOTH on length-4 intlists over [0,12] |
| [§v2.6 Pair 3](experiments-v2.md#v26) | `0230662` | 20 | `{reduce_max_gt_5_slot, reduce_max_gt_7_slot}` 20/20 BOTH (slot_13 aggregator-variant body) |

### Narrowing / falsifying experiments

| experiment | commit | effect |
|---|---|---|
| [§v2.6 Pair 1](experiments-v2.md#v26) | `0230662` | narrowed scope: the 6-token `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT` body solves at only 4/20 BOTH at matched compute, despite 75-94% of failing winners having all required components present. Discoverability depends on body-shape topology, not just on the indirection mechanism. |

### Implications for downstream work

- **Downstream experiments may assume:** any 4-token body of the form
  `INPUT <unary op> THRESHOLD_SLOT GT` will solve cross-threshold at 20/20
  BOTH at this budget.
- **Downstream experiments must still test:** longer body shapes (≥6 tokens
  with strict assembly order); higher search budgets to test whether Pair 1
  is search-limited or structurally limited; non-integer constant types.
- Any future paper-level claim of "constant-indirection" must cite both
  §v2.3+§v2.6 supporting evidence **and** the §v2.6 Pair 1 edge —
  consolidation here is what makes that traceability automatic.

### Review history

- 2026-04-15 — initial promotion (commit `320fc6b`); §v2.6 ran in same
  session, Pair 1 edge folded in as a narrowing entry rather than blocking
  promotion.

---

## proxy-basin-attractor. Greedy search under chem-tape's BP_TOPK decoder is dominated by single-predicate proxy basins whenever a near-perfect single-predicate exists in the training distribution (n=20+ per axis, mechanism-grade).

**Scope tag:** `within-family / cross-axis on AND-composition` · `n=20 each on 4 sweeps × ≥3 attractor reframings` · `at pop=1024 gens=1500 (and 4× scaled to pop=2048 gens=3000) BP_TOPK(k=3,bp=0.5) v2_probe alphabet` · `on integer-list AND-composition labels of the form` `(sum > t1) AND (max > t2)`

**Status:** `ACTIVE` · last revised commit `320fc6b` · 2026-04-15

### Claim

When the training data contains a single-predicate (e.g., `max > 5` or
`sum > 10`) whose accuracy on the training labels is ≥ ~0.90, evolution
under BP_TOPK reliably converges to that predicate alone within the
pre-registered budget — *regardless of whether the underlying label
function requires AND-composition* — and the basin is robust to compute
scaling (4×) and to decorrelation of the original proxy (evolution shifts
to the next-best single-predicate).

### Scope boundaries (what this claim does NOT say)

- Does not claim "compositional depth doesn't scale" — the broader v2.4
  framing is **superseded** by this narrower mechanism reading. Compositional
  bodies (e.g., §v2.4-alt threshold=5 at 17/20) **are** discoverable when no
  near-perfect single-predicate proxy exists.
- Does not claim the basin attractor is universal across all AND-composition
  tasks; tested specifically on `(sum > t1) AND (max > t2)` with t1 ∈ {5, 10}
  and t2 = 5 on length-4 intlists over [0,9].
- Does not claim the basin is the only failure mode — the §v2.6 Pair 1
  failure (different track, body topology issue) is a distinct mechanism.
- Tested only at BP_TOPK(k=3, bp=0.5); other arms not characterised.

### Mechanism reading (current)

**Current name:** `single-predicate proxy basin attractor`

**Naming history:**
- Initial: `refinement bottleneck under 4× compute` (§v2.4 follow-up,
  commit `94da867`) — falsified by direct genotype inspection (§v2.4
  open-question section, commit `cd01d6e`).
- Narrowed: `max > 5 proxy attractor` (§v2.4 inspection result) — narrower
  than the original framing but still too narrow because it implied the
  predicate was specific.
- Broadened (methodology principle 16b applied): `single-predicate proxy
  basin attractor` (§v2.4-proxy result, commit `320fc6b`). Decorrelating
  `max > 5` did not free the search — evolution shifted to `sum > 10`
  (the next-best ≥0.90 predicate). The mechanism is the **basin shape**,
  not the specific predicate.

### Supporting experiments

| experiment | commit | n | what it establishes |
|---|---|---|---|
| [§v2.4 baseline](experiments-v2.md) | `e3d7e8a` | 20 | `sum_gt_10_AND_max_gt_5` F_AND = 0/20 at pre-reg compute; baseline fitness clusters at 0.85–0.97 |
| [§v2.4 compute-scaling](experiments-v2.md) | `94da867` | 20 | F_AND_scaled = 0/20 at 4× compute (pop=2048, gens=3000); attractor robust to budget scaling |
| [§v2.4 inspection](experiments-v2.md) | `cd01d6e` | 20 | direct genotype decode: 14/20 baseline seeds converge to exact `max > 5` predicate; refinement-bottleneck framing falsified |
| [§v2.4-alt](experiments-v2.md#v24-alt) | `0230662` | 20 | threshold=5 task solves at 17/20 with the IF_GT+CONST_0-prefix compositional body — proves "compositional depth doesn't scale" framing was wrong; the basin only blocks when the proxy is high-accuracy |
| [§v2.4-proxy](experiments-v2.md#v24-proxy) | `0230662` | 20 | under decorrelation (P(max>5\|+)=1.0, P(max>5\|−)=0.5), evolution shifts from `max > 5` (2/17 stuck) to `sum > 10` (11/17 stuck); 3/20 found genuine AND |

### Narrowing / falsifying experiments

None yet. Two queued candidates that could narrow further:
- §v2.4-proxy-2 (simultaneous decorrelation of `max > 5` and `sum > 10`): if
  evolution still finds a 0.84-accuracy `any cell > 6` proxy, the basin
  story is fully general; if a novel attractor emerges, the claim narrows.
- Different decoder arms: if BP (k=1) or A (direct GP) escape the basin
  while BP_TOPK does not, the claim narrows from "greedy search" to
  "BP_TOPK-specific."

### Implications for downstream work

- **Downstream experiments may assume:** any AND-composition task with a
  single-predicate-correlation ≥ ~0.90 in training will *fail* the
  compositional body discovery at this budget — and the failure is *not*
  diagnostic of the mechanism's compositional reach.
- **Downstream experiments must still test:** the basin's robustness to
  decoder-arm changes; whether decorrelating the next-best predicate
  also gets shifted-to or yields novel attractors; whether the basin
  exists for OR/XOR/larger-k compositions.
- **Methodology consequence:** sampler design (methodology §20) is now
  load-bearing for any AND-composition follow-up — class-balanced and
  proxy-decorrelation-aware sampling must be specified in the prereg.

### Review history

- 2026-04-15 — initial promotion (commit `320fc6b`) replacing the
  superseded "compositional depth doesn't scale" framing in the §v2.4
  chronicle. This is a **mechanism rename in the broader direction**
  (methodology §16b); the original §v2.4 verdict text remains in the
  chronicle for reasoning-trail purposes (methodology §13).
