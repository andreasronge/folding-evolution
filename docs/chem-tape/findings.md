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

## constant-slot-indirection. Body-invariant route absorbs slot-bound integer-constant variation on a single body shape at precision (n=80, within-family; §v2.6 breadth check failed).

**Scope tag:** `within-family` · `one body shape` · `n=20 (pre-reg) + 60 (seed expansion) = 80 on one pair` · `at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) v2_probe alphabet` · `on body shape` `INPUT SUM THRESHOLD_SLOT GT` `with thresholds {5, 10} on intlists over [0,9]`

**Status:** `NARROWED` · last revised commit `344e4de` · 2026-04-15 (narrowed from `ACTIVE` at commit `320fc6b` on the same date; §v2.6 baseline completion below)

> **Narrowed by §v2.6 baseline completion (2026-04-15, commit `344e4de`).** The pre-baseline reading (ACTIVE; `across-family / 4 pairs`) cited §v2.6 Pair 2 (`sum_gt_{7,13}_slot_r12`) and Pair 3 (`reduce_max_gt_{5,7}_slot`) as 20/20 BOTH supporting evidence. The fixed-baseline sweep that the prereg required but the initial session skipped shows both pairs at Fmin = 20/20 — prereg-pre-accept swamp outcome (per `Plans/prereg_v2_6.md` outcome-table line 84). Swamped pairs provide **no evidence** for or against the mechanism: the 20/20 alternation BOTH is what two independently-easy tasks produce with or without slot-indirection. The entry narrows to §v2.3's one precision pair only. The pre-baseline claim and scope-tag text are preserved in the "Narrowing-history" block below (methodology §13 reasoning trail).

### Claim

When two binary tasks share the `INPUT SUM THRESHOLD_SLOT GT` body and differ
only in a task-bound integer constant exposed via `THRESHOLD_SLOT`, evolution
discovers the body once and solves both tasks via that body at 80/80 BOTH
across 4 seed blocks at the tested budget. The mechanism is demonstrated at
precision on one pair; the breadth check (§v2.6) across three additional
body-invariant pairs did not extend the claim — two of the three pairs were
swamped at Fmin = 20/20 (baseline too permissive to measure alternation lift)
and one pair (6-token string-count body) failed at 4/20.

### Scope boundaries (what this claim does NOT say)

- Does **not** claim `across-family` — the across-family extension failed
  its pre-registered breadth check (§v2.6 FAIL: 0/3 pairs scaled, two
  swamped, one does-not-scale).
- Does **not** claim the aggregator-variant body (`INPUT REDUCE_MAX
  THRESHOLD_SLOT GT`) supports the mechanism — §v2.6 Pair 3 was swamped at
  Fmin = 20/20 and is therefore uninformative for or against the mechanism
  on that body.
- Does **not** claim constant-indirection works at any wider input range
  — §v2.6 Pair 2 over [0,12] was similarly swamped.
- Does **not** claim the mechanism is budget-free: §v2.6 Pair 1 (6-token
  body) failed at 4/20 at matched compute, possibly resolvable at higher
  pop/gens but untested.
- Tested only on intlist inputs of length 4 over [0,9] with thresholds
  {5, 10}, `INPUT SUM THRESHOLD_SLOT GT` body.
- Open external-validity questions: (i) does a redesigned §v2.6' with
  Fmin-intermediate thresholds on Pair 2 / Pair 3 bodies support the
  mechanism? (ii) does Pair 1 resolve at higher compute / alternative
  decoder / shorter tape, separating search-landscape-difficulty from
  mechanism-absence? **Answered partially by four follow-ups (commit
  `c8af29d`), see [§v2.6-pair1 follow-up sweeps](experiments-v2.md#v26-pair1-follow-up-sweeps-2×2×2-of-compute-×-tape-×-decoder):**
  - **4× compute** ([§v2.6-pair1-scale](experiments-v2.md#v26-pair1-scale), INCONCLUSIVE at commit `600ef20`): 4/20 → 8/20, assembly barrier closes, component-discovery barrier remains.
  - **16× compute** (§v2.6-pair1-scale-8x, PASS-partial, BOTH=13/20): compute helps with diminishing returns under BP_TOPK(k=3); does not cleanly clear the ≥14/20 scales bar at 16× either.
  - **Arm A direct GP at 1× compute** (§v2.6-pair1-scale-A, PASS-partial, BOTH=7/20): ~matches BP_TOPK at 4× compute — decoder-arm is a real lever of comparable magnitude to 4× compute on this body.
  - **Tape length 24 at 1× compute** (§v2.6-pair1-tape24, FAIL, COMP=5 → lower than baseline): shorter tape is *not* the mechanism it appeared; BOTH lift came entirely from seed-set substitution, not from extending baseline's solved seeds.

  Reformulated open question: **"Is Pair 1's remaining discovery gap a joint function of decoder-arm × compute, with tape length secondary?"** Untested factorial cells (Arm A × 4× compute, Arm A × 16× compute, tape24 × Arm A) would settle this, but require a second 6-token body to avoid single-pair overfitting.
- **Decoder-arm dependence caveat (added 2026-04-15, narrowed 2026-04-16 by §v2.11):** on the **6-token body** (Pair 1) at pop=1024 gens=1500, Arm A direct GP achieves 7/20 BOTH while BP_TOPK(k=3,bp=0.5) achieves 4/20 at matched compute — decoder-arm is a real lever on harder bodies. **On the 4-token body (§v2.3), decoder choice does not matter: §v2.11 confirmed Arm A reproduces 20/20 BOTH with causal slot-indirection (attractor_PASS_share = 20/20 = 1.00 via counterfactual threshold-swap test).** The caveat narrows to: decoder-arm dependence applies to bodies demanding ≥6 tokens in strict dependency order, not to 4-token bodies.

### Mechanism reading (current)

**Current name:** `body-invariant-route mechanism (constant-slot variant, one-pair precision)`

**Naming history:**
- Initial: extension of "body-invariant route" from op-slot to constant-slot,
  proposed pre-§v2.3 (commit `4f0fe94`).
- Confirmed: §v2.3's 80/80 across 4 seed blocks demonstrates constant-slot
  variant works on the `INPUT SUM THRESHOLD_SLOT GT` body at thresholds {5, 10}.
- *Provisionally-broadened (2026-04-15 morning, commit `320fc6b`, superseded):*
  "body-invariant route, 4-token shapes." Reasoning was: §v2.6 Pair 2
  (sum r12) and Pair 3 (reduce_max) hit 20/20 BOTH at alternation, suggesting
  the mechanism extends to a wider input range and to an aggregator-variant
  body. This framing was **narrowed on the same day** (commit `344e4de`)
  when the §v2.6 fixed-baseline sweep showed both pairs swamped at
  Fmin = 20/20 — the alternation 20/20 is indistinguishable from "tasks
  independently easy" and provides no positive evidence for the mechanism.
- Narrowed to one-pair precision (current, 2026-04-15 afternoon, commit
  `344e4de`): the mechanism is demonstrated at precision on `{sum_gt_5_slot,
  sum_gt_10_slot}` only. Whether it extends to other body shapes is
  **open** — the breadth check did not land because of prereg-time
  threshold choices that pre-accepted swamp on two of three target pairs.
  Rename to "body-invariant route, one-pair precision (sum body, thresholds
  {5, 10})" until a redesigned §v2.6' produces Fmin-intermediate breadth
  evidence.

### Supporting experiments

| experiment | commit | n | what it establishes |
|---|---|---|---|
| [§v2.3](experiments-v2.md#v23) | `e3d7e8a` | 20 (pre-reg) + 60 (seed expansion) = 80 | `{sum_gt_5_slot, sum_gt_10_slot}` 80/80 BOTH; max\|gap\| = 0.0156; 399/400 zero-cost flip transitions; direct genotype decode confirms canonical-body convergence with THRESHOLD_SLOT as the only task-distinguishing token |

### Narrowing / falsifying experiments

| experiment | commit | effect |
|---|---|---|
| [§v2.6 Pair 1](experiments-v2.md#v26) | `0230662` / `344e4de` (baseline) | narrowed-and-baseline-confirmed: the 6-token `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT` body solves at only 4/20 BOTH alternation AND fixed-task solo `any_char_count_gt_1_slot` hits Fmin = 4/20 at matched compute. Fails both the scales-bar (4 < 12) and the baseline-fails check (min(F) ≤ 5). Candidate explanations (body-length, assembly-order, string-domain) are confounded by the current design. |
| [§v2.6 Pair 2](experiments-v2.md#v26) | `344e4de` | narrowed: `{sum_gt_7_slot_r12, sum_gt_13_slot_r12}` alternation BOTH = 20/20, **but** fixed-task baselines show Fmin = 20/20 on the same pair — prereg-table row `swamped` (Fmin ≥ 19/20). The 20/20 alternation BOTH was originally read as supporting, but swamp means the result is mechanism-untested on this body. Moved from Supporting to Narrowing. |
| [§v2.6 Pair 3](experiments-v2.md#v26) | `344e4de` | narrowed: `{reduce_max_gt_5_slot, reduce_max_gt_7_slot}` alternation BOTH = 20/20, with Fmin = 20/20 — prereg-table row `swamped` (explicitly pre-accepted in prereg lines 113-117 for aggregator thresholds). Aggregator-variant body therefore provides no evidence for or against the mechanism on this shape. Moved from Supporting to Narrowing. |

### Narrowing-history (preserved per methodology §13)

**Pre-narrowing claim text (2026-04-15 morning, commit `320fc6b`, superseded):**

> "When two binary tasks share a token-identical body and differ only in a
> task-bound integer constant exposed via `THRESHOLD_SLOT`, evolution discovers
> the body once and solves both tasks via that body — extending the
> op-slot-indirection mechanism from operator variation to constant variation
> across at least three structurally distinct body shapes."

**Pre-narrowing scope tag (2026-04-15 morning, commit `320fc6b`, superseded):**

> `across-family · n=20 per pair × 4 pairs (1 with seed expansion to n=80) · at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) v2_probe alphabet · on body shapes INPUT SUM THRESHOLD_SLOT GT (integer) and INPUT REDUCE_MAX THRESHOLD_SLOT GT (aggregator)`

**Why narrowed:** the "three structurally distinct body shapes" and
`across-family` claims rested on §v2.6 Pair 2 / Pair 3 alternation-level
20/20 BOTH results. The prereg-required fixed-baseline sweep (initially
skipped) was run later on commit `344e4de` and showed both pairs at
Fmin = 20/20 — prereg-table `swamped` outcome. Swamped pairs are
mechanism-untested; they cannot be counted as supporting evidence.

### Implications for downstream work

- **Downstream experiments may assume:** `{sum_gt_5_slot, sum_gt_10_slot}`
  on the `INPUT SUM THRESHOLD_SLOT GT` body solves cross-threshold at
  80/80 BOTH at the tested budget.
- **Downstream experiments must still test (open questions):**
  - whether the mechanism extends to any body shape other than
    `INPUT SUM THRESHOLD_SLOT GT` — §v2.6 did not establish this;
    needs a redesigned §v2.6' with Fmin-intermediate thresholds
    (e.g., Pair 2 at thresholds {18, 24} over [0,12], Pair 3 at
    structurally distinct r6 body) to avoid swamp pre-accept
  - whether the mechanism extends to aggregator-variant bodies
    (`INPUT REDUCE_MAX THRESHOLD_SLOT GT`) — §v2.6 Pair 3 was
    uninformative (swamp); needs redesign at non-ceiling thresholds
  - whether Pair 1 resolves at 4× or 8× compute, separating
    search-landscape-difficulty from mechanism-absence on
    6-token bodies
  - non-integer constant types (floats, enumerations, ordinals)
- Any future paper-level claim about constant-slot-indirection must
  cite §v2.3's 80/80 on the one pair **and** §v2.6's FAIL on the
  breadth check — consolidation here is what makes that
  traceability automatic. **Not claimable:** "across-family",
  "across multiple body shapes", "aggregator-variant confirmed",
  "four task families." The breadth check did not land those.

### Review history

- 2026-04-15 morning (commit `320fc6b`) — initial promotion from
  experiments-v2.md §v2.6 chronicle. §v2.6 ran in same session with
  Pair 1 edge folded in; Pair 2 / Pair 3 counted as 20/20 BOTH
  supporting evidence. This promotion was **premature** — the
  prereg-required fixed-baseline sweep had not been run, so the
  scales-vs-swamp row could not yet be picked for Pair 2 / Pair 3.
- 2026-04-15 afternoon (commit `344e4de`) — **narrowed** by the
  §v2.6 baseline-completion chronicle update. Pair 2 / Pair 3
  reclassified from Supporting to Narrowing (swamp, uninformative
  for the mechanism). Claim scope narrowed from `across-family /
  4 pairs` to `within-family / one pair (§v2.3)`. Status flipped
  from `ACTIVE` to `NARROWED`. Pre-narrowing text preserved
  verbatim in Narrowing-history block above (methodology §13).

---

## proxy-basin-attractor. Greedy search is dominated by single-predicate proxy basins whenever a ≥~0.85-accurate single-predicate exists in the training distribution (n=20+ per axis, mechanism-grade; decoder-general across BP_TOPK and Arm A; proxy-cascade confirmed under dual-decorrelation).

**Scope tag:** `within-family / cross-axis on AND-composition` · `n=20 each on 7 sweeps × ≥4 attractor reframings` · `at pop=1024 gens=1500 (and 4× scaled to pop=2048 gens=3000) v2_probe alphabet` · `across decoder arms {BP_TOPK(k=3,bp=0.5), Arm A direct GP}` · `across sampler conditions {natural, single-decorr, dual-decorr}` · `on integer-list AND-composition labels of the form` `(sum > t1) AND (max > t2)`

**Status:** `ACTIVE` · last revised commit `92b3325` · 2026-04-16 (broadened twice: decoder-general by §v2.12, proxy-accuracy threshold relaxed from ≥~0.90 to ≥~0.85 by §v2.4-proxy-2)

### Claim

When the training data contains a single-predicate (e.g., `max > 5`,
`sum > 10`, `sum > 15`, `any cell > 7`) whose accuracy on the training
labels is ≥ ~0.85, greedy evolution reliably converges to that predicate
alone within the pre-registered budget — *regardless of whether the
underlying label function requires AND-composition* — and the basin is
robust to compute scaling (4×), to decorrelation of the top-1 proxy
(evolution shifts to the next-best), to simultaneous decorrelation of
the top-2 proxies (evolution cascades to third-best), and to decoder-arm
variation (BP_TOPK and Arm A direct GP both trap in the same attractor
categories).

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
- ~~Tested only at BP_TOPK(k=3, bp=0.5); other arms not characterised.~~ **Updated 2026-04-16:** §v2.12 tested Arm A direct GP on both samplers; Arm A traps in the same basin categories (attractor_share 0.80 natural, 0.84 decorr). Decoder-arm is no longer an open scope boundary on this task family. (Pending principle-20 audit discharge for paper-grade.)

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
| [§v2.12 Arm A natural](experiments-v2.md#v212-arm-a-direct-gp-on-v24-proxy-basin-tasks-2026-04-16) | `1cfe7d5` | 20 | Arm A direct GP on natural sampler: F_AND_A = 0/20, attractor breakdown 10/20 max_gt_5 + 6/20 sum_gt (attractor_share = 0.80). Basin traps Arm A as thoroughly as BP_TOPK. |
| [§v2.12 Arm A decorr](experiments-v2.md#v212-arm-a-direct-gp-on-v24-proxy-basin-tasks-2026-04-16) | `1cfe7d5` | 20 | Arm A decorr sampler: F_AND_A = 1/20, attractor breakdown 12/19 sum_gt + 4/19 max_gt_5 (attractor_share = 0.84). Attractor-switch post-decorrelation reproduces under different decoder. (Principle-20 audit pending.) |
| [§v2.4-proxy-2 BP_TOPK dual-decorr](experiments-v2.md#v24-proxy-2-simultaneous-dual-proxy-decorrelation-on-and-composition-2026-04-16) | `92b3325` | 20 | BP_TOPK under dual-decorrelation (max>5 AND sum>10 both at 0.75): F_AND = 0/20. Evolution cascades to third-tier proxies (sum>15 at 0.91, max>7/any_cell>7 at ~0.86). attractor_3rd = 0.75. |
| [§v2.4-proxy-2 Arm A dual-decorr](experiments-v2.md#v24-proxy-2-simultaneous-dual-proxy-decorrelation-on-and-composition-2026-04-16) | `92b3325` | 20 | Arm A under dual-decorrelation: F_AND = 1/20. Same cascade pattern (attractor_3rd = 0.68). Decoder-general proxy cascade confirmed. |

### Narrowing / falsifying experiments

None yet. One queued candidate that could narrow further:
- §v2.4-proxy-2 (simultaneous decorrelation of `max > 5` and `sum > 10`): if
  evolution still finds a 0.84-accuracy `any cell > 6` proxy, the basin
  story is fully general; if a novel attractor emerges, the claim narrows.
- ~~Different decoder arms: if BP (k=1) or A (direct GP) escape the basin
  while BP_TOPK does not, the claim narrows from "greedy search" to
  "BP_TOPK-specific."~~ **Resolved by §v2.12 (2026-04-16):** Arm A does
  not escape; basin is decoder-general on this task family.

### Implications for downstream work

- **Downstream experiments may assume:** any AND-composition task with a
  single-predicate-correlation ≥ ~0.90 in training will *fail* the
  compositional body discovery at this budget — and the failure is *not*
  diagnostic of the mechanism's compositional reach.
- **Downstream experiments must still test:** ~~the basin's robustness to
  decoder-arm changes;~~ (resolved by §v2.12: decoder-general)
  ~~whether decorrelating the next-best predicate also gets shifted-to
  or yields novel attractors;~~ (resolved by §v2.4-proxy-2: yes, third-tier
  proxies take over — cascade confirmed) whether the basin exists for
  OR/XOR/larger-k compositions; whether a sampler that eliminates ALL
  single-predicates above ~0.80 frees AND-composition (may require a
  different input domain).
- **Methodology consequence:** sampler design (methodology §20) is now
  load-bearing for any AND-composition follow-up — class-balanced and
  proxy-decorrelation-aware sampling must be specified in the prereg.

### Review history

- 2026-04-15 — initial promotion (commit `320fc6b`) replacing the
  superseded "compositional depth doesn't scale" framing in the §v2.4
  chronicle. This is a **mechanism rename in the broader direction**
  (methodology §16b); the original §v2.4 verdict text remains in the
  chronicle for reasoning-trail purposes (methodology §13).
- 2026-04-16 — **broadened** by §v2.12 (commit `1cfe7d5`). Arm A direct
  GP tested on both samplers; basin traps both decoders. Scope tag updated
  from "BP_TOPK(k=3,bp=0.5)" to "across decoder arms {BP_TOPK, Arm A}."
  Claim sentence updated to remove "under BP_TOPK" qualifier. Headline
  updated. Principle-20 sampler-audit flag noted in status line (post-hoc
  audit was marginal; does not block the broadening but noted for
  paper-grade audit trail).
- 2026-04-16 — **broadened** by §v2.4-proxy-2 (commit `92b3325`).
  Dual-decorrelation (max>5 AND sum>10 simultaneously weakened to 0.75)
  confirms proxy cascade: evolution shifts to third-tier proxies (sum>15
  at 0.91, any_cell>7 at 0.86). Trapping threshold relaxed from "≥ ~0.90"
  to "≥ ~0.85" in claim sentence. Scope tag updated to include
  dual-decorr sampler condition. Headline updated.

---

## safe-pop-consume-effect. Safe-pop consume rule lifts mixed-type chain assembly on the 6-token string-count body across two MAP-family slot bindings under BP_TOPK, stacks with 4x compute on R-count body, shows no lift under Arm A at 1x, and shifts attractor categories on intlist AND-composition tasks (n=20 per comparison, within-family, executor-rule ablation).

**Scope tag:** `within-family` · `n=20 per comparison` · `at BP_TOPK(k=3,bp=0.5) v2_probe alphabet` · `executor-rule ablation` · `1x solve-rate lift on 6-token string-count body with slot_12 in {MAP_EQ_R, MAP_EQ_E} under task alternation` · `4x compute stacking confirmed on R-count body only (MAP_EQ_R)` · `no lift observed under Arm A at 1x compute` · `intlist AND-composition (landscape-shift observation only)`

**Status:** `ACTIVE` · last revised commit `76bb58f` · 2026-04-16

### Claim

Switching the executor's safe-pop rule from "preserve wrong-typed values on stack" to "consume wrong-typed values" doubles the BOTH-solve rate on the 6-token mixed-type string-count body from 4/20 to 8/20 at matched 1x compute under BP_TOPK(k=3,bp=0.5), replicated on two MAP-family slot bindings (MAP_EQ_R and MAP_EQ_E) with identical effect size and identical solver seeds. On the R-count body specifically, the effect stacks with 4x compute: consume-4x reaches 14/20 BOTH, exceeding both consume-1x (8/20) and preserve-4x (8/20). The consume rule shows no lift under Arm A direct GP at 1x compute (5/20 vs 7/20 preserve, off-grid between prereg INCONCLUSIVE and FAIL bands; §v2.14d). On intlist-only AND-composition tasks, consume does not produce additional solves but shifts the dominant attractor category from single-predicate proxies toward compound AND-composition attempts (0→10/20 on natural sampler).

### Scope boundaries (what this claim does NOT say)

- Does not claim the consume rule is universally better — on the 4-token all-int body the rule is irrelevant (20/20 under both).
- Does not claim the consume rule helps escape the proxy-basin-attractor — §v2.14b showed consume shifts the attractor landscape but does not produce additional solves on intlist-only AND-composition tasks.
- Does not claim a causal mechanism — the attractor-category shift is consistent with a "stack jam" / type-barrier reading but the causal chain is not experimentally isolated.
- **Slot-binding scope (updated):** replicated on two MAP-family slot bindings (MAP_EQ_R, MAP_EQ_E) with identical solver sets at 1x compute. Not tested on non-MAP ops or ops producing a different type chain. The identical solver sets under consume are consistent with a type-chain-driven reading but also with shared-RNG correlation on near-isomorphic tasks (§v2.14e caveat). Broadening beyond "MAP-family slot bindings" is not supported.
- **Decoder-arm scope (updated):** the solve-rate lift is BP_TOPK-specific. Under Arm A at 1x compute, consume shows 5/20 vs 7/20 preserve — no evidence of lift, direction mildly negative but within noise (§v2.14d, off-grid between prereg bands). The consume solve-rate lift should not be assumed to extend to Arm A at this budget.
- **Compute stacking scope (updated):** consume and compute show additive improvement under BP_TOPK on the R-count body: consume-4x (14/20) exceeds both consume-1x and preserve-4x (both 8/20) and exceeds preserve-16x (13/20). Whether stacking continues at 8x or 16x compute is untested. Whether stacking holds on the E-count body or under Arm A is untested.
- McNemar p=0.157 (§v2.14 R-count) and p=0.102 (§v2.14e E-count) at n=20 — the solve-rate effect does not reach inferential significance on either pair individually. The evidence is descriptive (solve count + seed overlap + attractor-category inspection), not statistically confirmed.
- Open external-validity questions: (i) effect on other task families beyond string-count and AND-composition; (ii) non-MAP slot bindings with different type chains; (iii) consume x Arm A interaction at higher compute; (iv) whether stacking replicates on the E-count body.

### Mechanism reading (current)

**Current name:** `safe-pop consume executor-rule effect (BP_TOPK-specific solve-rate lift)`

**Naming history:**
- Initial: "safe-pop consume lifts mixed-type chain assembly" (§v2.14 PASS, commit `cdf9c39`). First-pass name based on the solve-rate lift and attractor shift on the string-count body. The "stack jam" hypothesis (Codex independent review) motivated the experiment: wrong-typed values persist on the stack under preserve, blocking downstream typed ops.
- Broadened observation (§v2.14b PARTIAL, commit `1fc51c5`): consume also shifts attractor categories on intlist-only tasks (0→10/20 AND-composition attempts without additional solves). The effect extends beyond multi-type-boundary chains at the landscape level. Name broadened from "type-barrier clearance" to the neutral "executor-rule effect" to cover both manifestations.
- Compute stacking confirmed on R-count body (§v2.14c PASS, commit `76bb58f`): consume-4x reaches 14/20, exceeding both single levers. Attractor classification: 10/20 canonical-6tok (9 BOTH-solvers), 9/20 partial-5tok (5 BOTH-solvers). Consume and compute appear to address different aspects of the assembly problem at this scope.
- Replication on second slot binding at 1x (§v2.14e PASS, commit `76bb58f`): E-count body (MAP_EQ_E) replicates R-count exactly — P_E=4/20, C_E=8/20, identical consume solver sets (8/8 overlap). Effect spans two MAP-family slot bindings at 1x compute. Under consume, canonical-6tok assembly rises from 7→13/20 (same qualitative pattern as R-count).
- No Arm A lift observed at 1x (§v2.14d INCONCLUSIVE/off-grid, commit `76bb58f`): consume shows 5/20 vs 7/20 preserve under Arm A — no evidence of lift, mildly negative direction within noise. The solve-rate lift is at minimum decoder-arm-dependent. Name updated to note "BP_TOPK-specific solve-rate lift."
- Current: `safe-pop consume executor-rule effect (BP_TOPK-specific solve-rate lift)` — three layers: (a) solve-rate lift on mixed-type chains under BP_TOPK, replicated on two MAP-family bindings (§v2.14, §v2.14e), (b) additive improvement with compute under BP_TOPK on R-count body (§v2.14c), (c) landscape-level attractor shift on all-int tasks (§v2.14b). Arm A shows no lift at 1x (§v2.14d).

### Supporting experiments

| experiment | commit | n | what it establishes |
|---|---|---|---|
| [§v2.14](experiments-v2.md#v214-safe-pop-executor-rule-ablation-kuyucu-inspired-decoder-micro-ablation-2026-04-16) | `cdf9c39` | 20 | PASS: consume 8/20 vs preserve 4/20 on R-count hard pair; 20/20 vs 20/20 on easy pair. Attractor shift: canonical-6tok 3→9/20, partial-assembly 6→1/20. McNemar p=0.157. |
| [§v2.14b](experiments-v2.md#v214b-safe-pop-consume-on-proxy-basin-and-composition-tasks-2026-04-16) | `1fc51c5` | 20 per sampler | PARTIAL: consume does not escape proxy basin (F_AND=0/20 natural, 1/20 decorr) but shifts attractor categories (0→10/20 AND-composition attempts on natural sampler). |
| [§v2.14c](experiments-v2.md#v214c-consume--4-compute-interaction-on-6-token-string-count-body-2026-04-16) | `76bb58f` | 20 | PASS: consume-4x 14/20 BOTH on R-count body, exceeding consume-1x (8/20) and preserve-4x (8/20). Attractor: 10/20 canonical-6tok (9 BOTH), 9/20 partial-5tok (5 BOTH). Levers stack on this body. |
| [§v2.14e](experiments-v2.md#v214e-safe-pop-consume-replication-on-e-count-body-second-slot-binding-2026-04-16) | `76bb58f` | 20 | PASS: E-count replicates R-count exactly at 1x (P_E=4/20, C_E=8/20, 8/8 consume solver overlap). Consume canonical-6tok 7→13/20. Broadens 1x lift to two MAP-family slot bindings. |

### Narrowing / falsifying experiments

| experiment | commit | effect |
|---|---|---|
| [§v2.14d](experiments-v2.md#v214d-safe-pop-consume-under-arm-a-direct-gp-on-6-token-string-count-body-2026-04-16) | `76bb58f` | Narrowing: consume shows no lift under Arm A at 1x compute (5/20 vs 7/20 preserve, off-grid between prereg INCONCLUSIVE and FAIL bands). The solve-rate lift is at minimum decoder-arm-dependent. Scope boundary "not tested on Arm A" resolved: no evidence of benefit at this budget. |

### Implications for downstream work

- **Downstream experiments may assume:** on the 6-token string-count body under BP_TOPK(k=3,bp=0.5), the consume rule approximately doubles BOTH-solve rate at 1x compute (replicated on MAP_EQ_R and MAP_EQ_E), and reaches 14/20 at 4x compute on the R-count body.
- **Downstream experiments must still test:**
  - Whether the effect extends to non-MAP slot bindings or ops producing a different type chain (current evidence spans two MAP-family ops with identical type signatures).
  - Whether consume x Arm A interaction changes at higher compute (§v2.14d tested only at 1x).
  - Whether 4x stacking replicates on the E-count body (currently confirmed only on R-count).
  - Whether changing the project default to consume under BP_TOPK causes regressions on any existing task family beyond the three tested (R-count, E-count, AND-composition).
  - Effect on other task families or body shapes entirely.

### Review history

- 2026-04-16 — initial promotion from §v2.14 (PASS, commit `cdf9c39`) + §v2.14b (PARTIAL, commit `1fc51c5`). Codex adversarial review on §v2.14 chronicle addressed all P1 findings (full 2×2 McNemar, per-seed tables, scope tags, mechanism language). Codex confirmed §v2.14b classification as PARTIAL. Codex adversarial review on findings draft addressed 2 P1s (mechanism name too narrow for entry-wide label; "mediated by" overstates causality) and 4 P2s (scope tag detail, downstream non-test, two-layer mechanism split, overreach softening).
- 2026-04-16 — **updated** with §v2.14c (PASS, R-count stacking), §v2.14d (INCONCLUSIVE/off-grid, Arm A no-lift), §v2.14e (PASS, E-count replication at 1x). Scope broadened to two MAP-family slot bindings at 1x and R-count compute stacking at 4x. Scope narrowed by Arm A non-lift. Headline updated. Codex adversarial review on findings diff: 2 P1s addressed (Arm A language softened from "does not help" to "shows no lift at 1x"; 1x replication vs 4x stacking scopes separated in tag and assumption bullet), 4 P2s acknowledged (n tag tightened to "per comparison"; causal language in stacking softened; downstream assumptions narrowed to match scope; no contradictions with neighboring entries).
