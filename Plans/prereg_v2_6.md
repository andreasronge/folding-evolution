# Pre-registration: §v2.6 — task-diversity breadth check for constant-indirection

**Status:** FAIL · target commit `80d5320` · 2026-04-15 · resolved by [experiments-v2.md §v2.6](../docs/chem-tape/experiments-v2.md) at commit `dbca965` (post-baseline: 0/3 pairs scale, 2 swamped at Fmin=20/20, 1 does-not-scale; matched pre-reg FAIL combined-verdict row)

Derived from [docs/chem-tape/experiments-v2.md §v2.6](../docs/chem-tape/experiments-v2.md).

## Question (one sentence)

Does §v2.3's 80/80 BOTH-solve on `sum_gt_{5,10}_slot` generalise to other
body-invariant constant-indirection pairs, or is it specific to that pair?

## Hypothesis

§v2.3 demonstrated that the slot-indirection mechanism absorbs threshold
variation on one specific body (`INPUT SUM THRESHOLD_SLOT GT`) for thresholds
in {5, 10} on intlists over [0,9]. If the mechanism is generally a
"body-invariant-route absorbs constant variation" phenomenon, then three
structurally distinct body-invariant pairs (string domain, wider integer
range, aggregator variant) should all pass the same bar. If §v2.3's 80/80
was specific to the `sum_gt_{5,10}_slot` pair (e.g., dependent on the [0,9]
distribution or `SUM REDUCE_ADD`-adjacent arithmetic), we should see mixed
or null results.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_6.yaml` (three pairs
  via sub-sweeps, one per pair).
- **Tasks (new):**
  - **Pair 1 (string-domain count):**
    `any_char_count_gt_1_slot` and `any_char_count_gt_3_slot`.
    Body: `INPUT CHARS MAP_EQ_R SUM THRESHOLD_SLOT GT` (slot_12 = MAP_EQ_R).
    Thresholds ∈ {1, 3}. Length-16 strings.
  - **Pair 2 (wider integer range):**
    `sum_gt_7_slot_r12` and `sum_gt_13_slot_r12`.
    Body: `INPUT SUM THRESHOLD_SLOT GT`. Thresholds ∈ {7, 13}.
    Length-4 intlists over [0,12].
  - **Pair 3 (aggregator variant):**
    `reduce_max_gt_5_slot` and `reduce_max_gt_7_slot`.
    Body: `INPUT REDUCE_MAX THRESHOLD_SLOT GT` (slot_13 = REDUCE_MAX,
    bound via the existing `_make_agg_task` factory). Thresholds ∈ {5, 7}
    — tightened from doc draft's {2, 5} to avoid ceiling saturation
    (P(max>2)≈0.999 is a swamp floor; P(max>5)≈0.99, P(max>7)≈0.87 give
    measurable baselines). Length-4 intlists over [0,9].
- **Alphabet:** `v2_probe`.
- **Fixed params:** pop=1024, gens=1500, n_examples=64, holdout=256, arm=BP_TOPK,
  topk=3, bond_protection_ratio=0.5, tape_length=32 — matched to §v2.3.
- **Seeds:** 0..19 (n=20) per pair, task-alternating period=300.
- **Fixed-task baselines:** run all 6 tasks fixed-task at the same config
  first (6 tasks × 20 seeds = ~45 min compute for baselines; alternation
  sweeps are additional ~45 min for three pairs).
- **Est. compute:** ~90 min total at 4 workers.

## Baseline measurement (required)

- **Baseline quantity:** per-task fixed-task solve rate `F_task`.
- **Measurement:** fixed-task sweep above, run first.
- **Prior reference point:** §v2.3 achieved `F_sum_gt_5_slot = 20/20`,
  `F_sum_gt_10_slot = 19/20`, and alternation BOTH = 20/20. That is the
  "scales" shape any §v2.6 pair is being calibrated against.
- **Per-pair alternation threshold (principle 6):** BOTH ≥ max(Fmin − 3, 12)
  where `Fmin = min(F_task_a, F_task_b)` for that pair — same formula §v2.3
  and §v2.4 used.

## Internal-control check (required)

- **Tightest internal contrast:** §v2.3 itself. §v2.6 is the
  across-family breadth test that follows an already-passing internal
  control (consistent with methodology §1). Running §v2.6 **before** §v2.3
  had passed would have been wrong; running after is correct.
- **Are you running it here?** yes (§v2.3 ran; passed 80/80 across 4 seed
  blocks).

## Pre-registered outcomes (required — at least three)

Outcomes are per-pair; combined verdict is below.

### Per-pair scoring

| per-pair outcome | criterion | interpretation |
|---|---|---|
| **scales** | BOTH fixed baselines ≥ 15/20 AND alternation BOTH ≥ max(Fmin − 3, 12) | Mechanism extends to this pair. |
| **partial** | alternation BOTH in [max(Fmin−6, 8), max(Fmin−3, 12)) | Mechanism partially extends. |
| **does-not-scale** | alternation BOTH ≤ 5/20 | Mechanism does not extend here. |
| **swamped** | Fmin ≥ 19/20 AND alternation BOTH in [Fmin−1, Fmin] | Baseline too high to measure alternation lift. Reports baseline only. |
| **baseline-fails** | min(F_task_a, F_task_b) ≤ 5/20 | Task itself is unsolvable at matched compute; alternation result is uninterpretable — re-design the pair (e.g., thresholds too extreme). |

### Combined verdict (across the three pairs)

| combined | criterion | interpretation (updates §v2.3 claim) |
|---|---|---|
| **PASS — broad** | 3/3 pairs "scales" | §v2.3's claim has real breadth across task families. Constant-indirection is a genuine body-invariant-route mechanism. |
| **PASS — narrow-positive** | 2/3 pairs "scales", 1 "partial" or "does-not-scale" | Mechanism is real but has a characterisable edge. The failing pair's structure identifies where the mechanism narrows. |
| **INCONCLUSIVE** | 1/3 pair "scales" | §v2.3's result was likely specific to its pair; headline narrows sharply to "sum_gt_{5,10}_slot precision" rather than "constant-indirection in general." |
| **FAIL** | 0/3 pairs "scales" | §v2.3's result was pair-specific. The "body-invariant-route absorbs constant variation" framing is retracted; the claim narrows to "a single body-invariant pair produces 80/80." |

## Degenerate-success guard (required)

§v2.3's 80/80 with max gap 0.0156 was already flagged as "too clean" and
inspected (direct genotype decode confirmed canonical-body convergence with
threshold-slot as the only task distinguisher — real mechanism). Any §v2.6
pair scoring ≥18/20 BOTH triggers the same inspection protocol:

1. Decode best-of-run genotypes on all 20 seeds, both tasks.
2. Check: do both tasks share a token-identical body? If yes, slot-indirection
   is doing the work (same mechanism as §v2.3). If no — evolution solves both
   tasks with different bodies — then the apparent "BOTH solves" is
   coincidence, not slot-indirection, and the pair's result does **not**
   support the mechanism claim.
3. For Pair 2 (wider range [0,12]): check whether evolution exploits a
   range-limit trick (e.g., a predicate like "any cell > 9" that happens to
   correlate with sum-gt-threshold under this distribution). This would be
   a Pair-2-specific degenerate success.
4. For Pair 3 (aggregator): the thresholds {2, 5} are both very permissive
   on max over [0,9] — `max > 2` is true for ~0.999 of samples, `max > 5`
   for ~0.99. This may **swamp** (high baseline). Pre-accept a swamp
   outcome for Pair 3 if Fmin ≥ 19/20; use the swamped-row reading
   rather than the scales-row reading.

**Inspection commitment:** record the inspection result in the chronicle
entry, distinguishing "slot-indirection mechanism confirmed" from "same
BOTH count, different mechanism."

## Statistical test

- **Test:** paired McNemar on shared seeds (0..19) per pair, comparing
  alternation BOTH vs Fmin. One-sided α=0.05. Reported alongside raw counts.
- **Across-pair comparison:** descriptive only (three data points; no
  meta-analysis test).

## Diagnostics to log

- Per-pair: fixed-baseline solve counts, alternation BOTH, Fmin, holdout gap.
- Flip-transition cost per pair (§v2.3 pattern: zero-cost target).
- Winner-architecture decode for any pair with ≥18/20 BOTH (see guard).
- Training-set label balance sanity check per task (Pair 3 may have class
  imbalance under extreme thresholds; flag if |p_positive − 0.5| > 0.1).

## Scope tag

**If this experiment passes broadly (3/3), the claim enters findings.md
scoped as:**
`across-family / n=20 per pair / at pop=1024 gens=1500 BP_TOPK(k=3,bp=0.5) /
on three body-invariant constant-indirection pairs (string-count, integer-sum
wider-range, integer-max aggregator)`

Explicitly **not** claiming: "universal constant-indirection at all scales,"
"every body-invariant pair works," or "mechanism is budget-free." Breadth
is 3 pairs, not the full task-family space.

## Decision rule

- **PASS-broad (3/3) →** promote §v2.3's claim to findings.md with the
  `across-family` scope tag and the three §v2.6 pairs as supporting
  evidence. Downstream commitment: any future paper-level claim can cite
  "across three body-invariant pairs" rather than "one pair (precision
  only)."
- **PASS-narrow (2/3) →** §v2.3's claim is real but bounded. Characterise
  the failing pair in the chronicle; consider a follow-up that varies the
  specific attribute the failing pair differed on.
- **INCONCLUSIVE (1/3) →** §v2.3 headline narrows sharply. Paper-level claim
  becomes "sum_gt_{5,10}_slot precision" rather than "constant-indirection."
  Run a supersession pass on §v2.3's interpretation.
- **FAIL (0/3) →** full retraction of the generalising reading.
  Supersede §v2.3 interpretation section with "pair-specific result; no
  evidence of broader mechanism."

---

*Audit trail.* Closed gates: degenerate-success candidates enumerated with
per-pair concerns (Gate 3); thresholds anchored to §v2.3's 80/80 reference
(Gate 4); scope tag scoped to three specific pairs, not "constant-indirection
in general" (principle 18); across-family extension gated on §v2.3 having
already passed internal-control (principle 1). Known risk: Pair 3's
permissive thresholds may swamp — pre-accepted in the outcome table.
