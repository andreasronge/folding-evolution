# §v2.5-plasticity-2a winner-tape inspection (2026-04-22)

Zero-compute inspection (methodology principle 3) of the 40 top-1 winners from the pooled §v2.5-plasticity-2a (seeds 20..39, budget=5 plastic) + §v2.5-plasticity-2a-nexp-budget5 (seeds 40..59, budget=5 plastic) sweeps. Pre-committed inspection obligation from the §v2.5-plasticity-2a-nexp-budget5 chronicle's Next-steps bullet 1 (addressing codex P2-1 on the 40/40 `top1_winner_hamming = 5` cap+1-sentinel signature).

**Anchor commit:** `c08888a` (§v2.5-plasticity-2a-nexp-budget5 chronicle landed).
**Data sources:** `experiments/output/2026-04-21/v2_5_plasticity_2a/sweep_index.json` (seeds 20..39) and `experiments/output/2026-04-22/v2_5_plasticity_2a_nexp_budget5/sweep_index.json` (seeds 40..59). Winner selection: `best_genotype_hex` field, which is the decoded best-of-run top-1 per the sweep's own selection (per-run best_fitness ranking; deterministic tiebreak per `analyze_plasticity.py:_compute_top1_winner_hamming` verbatim).

## Headline: the cap+1=5 sentinel was information-destroying

The prereg's `top1_winner_hamming` metric with `cap=4` returned **5 on 40/40 winners** — a single-valued histogram that hid the actual distance structure. Uncapped Levenshtein distance from winner active-view to canonical active-view on the same 40 winners:

| uncapped distance | count |
|-------------------|-------|
| 17 | 1 |
| 19 | 3 |
| 20 | 2 |
| 21 | 3 |
| 22 | 9 |
| 23 | 8 |
| 24 | 8 |
| 25 | 2 |
| 26 | 4 |

**Min 17, median 23, max 26.** Winners are not uniformly distant — they span a 9-token range, but all are **far beyond cap=4**. The cap=4 setting was calibrated for a near-canonical regime (§v2.5-plasticity-1a sf=0.01 cells produced winners near canonical); in the §2a sf=0.0 regime, every winner is in the distant-tail regime and the cap destroys the intra-regime structure.

## Active-view length: winners are 2× longer than canonical

Canonical `sum_gt_10_AND_max_gt_5` active-view length: **12 tokens**. Winner active-view length distribution (n=40):

| length | count |
|--------|-------|
| 22 | 1 |
| 23 | 1 |
| 24 | 2 |
| 25 | 3 |
| 26 | 5 |
| 27 | 4 |
| 28 | 11 |
| 29 | 10 |
| 30 | 3 |

**Min 22, median 28, max 30.** Zero winners have canonical-length (12). Winners are roughly 2–2.5× longer than canonical — they are NOT "near-canonical with noise"; they are structurally different programs.

## Canonical-token presence: winners mostly contain canonical operators

Canonical active-view token set: `{CONST_0, INPUT, REDUCE_MAX, CONST_5, GT, SUM, ADD, IF_GT}` (8 distinct tokens). Number of canonical tokens MISSING from each winner's active view:

| missing count | winners |
|---------------|---------|
| 0 | 13/40 |
| 1 | 15/40 |
| 2 | 10/40 |
| 3 | 2/40 |

**28/40 winners have at least 7 of the 8 canonical tokens present.** But they also have **many extra tokens** the canonical doesn't use (DUP, THRESHOLD_SLOT, MAP_EQ_E, CHARS, ANY, REDUCE_ADD, SLOT_12/13, CONST_1/2, SWAP beyond canonical's 2).

This is the decisive structural observation: **winners are not classical-Baldwin near-canonical (zero at canonical-length)**, and they are not single-predicate proxies (see classification below), and they are not noise — they are **compositional AND-attempts with substantial operator overhead**.

## Attractor classification (heuristic, pooled n=40)

Simple heuristic based on which combinations of `{REDUCE_MAX, CONST_5}` (max > 5 predicate building blocks) and `{SUM, GT, IF_GT}` (sum > 10 predicate building blocks) appear in each winner's active view:

| category | count | criterion |
|----------|-------|-----------|
| **both-predicates-AND-attempt** | **32/40** | has ≥1 of `{REDUCE_MAX, CONST_5}` AND ≥1 of `{SUM}` AND ≥1 of `{GT, IF_GT}` |
| max>5-only-proxy | 4/40 | has `{REDUCE_MAX, CONST_5, GT}` but no `SUM` |
| sum>10-only-proxy | 2/40 | has `{SUM, GT/IF_GT}` but no `REDUCE_MAX` and no `CONST_5` |
| other/unknown | 2/40 | doesn't fit above |

**32/40 winners are attempting the compositional AND structure.** This is dramatically different from §v2.4-proxy's decorrelated-task-sampler result where most winners landed on a single-predicate proxy (e.g., `max > 5`). Under the §2a sf=0.0 regime, selection pressure drives winners toward the compositional structure, not toward single-predicate shortcuts.

F_AND_test_plastic = 14/40 = 0.35 = the fraction of those compositional attempts that actually solve the task on the 16-example test set. The remaining 18 `both-predicates-AND-attempt` winners (32 − 14 = 18, modulo the single-predicate winners that also contribute to F_test solve rate) attempted AND but didn't quite achieve it — wrong operator counts, spurious extra tokens, or semantic composition failures.

## Token frequency in winner active views (per-winner average)

Pooled across n=40 winners:

| token | count (pooled) | per-winner avg | canonical count | canonical per-winner |
|-------|---------------|----------------|-----------------|----------------------|
| GT | 106 | 2.6 | 2 | 2.0 |
| INPUT | 91 | 2.3 | 2 | 2.0 |
| REDUCE_MAX | 90 | 2.2 | 1 | 1.0 |
| DUP | 69 | 1.7 | 0 | 0 (absent) |
| IF_GT | 62 | 1.6 | 1 | 1.0 |
| SLOT_13 | 60 | 1.5 | 0 | 0 (absent) |
| SUM | 60 | 1.5 | 1 | 1.0 |
| THRESHOLD_SLOT | 57 | 1.4 | 0 | 0 (absent) |
| ADD | 56 | 1.4 | 1 | 1.0 |
| CONST_5 | 55 | 1.4 | 3 | 3.0 |
| CONST_1 | 52 | 1.3 | 0 | 0 (absent) |
| SWAP | 51 | 1.3 | 2 | 2.0 |
| CONST_0 | 48 | 1.2 | 1 | 1.0 |
| SLOT_12 | 48 | 1.2 | 0 | 0 (absent) |
| CHARS | 46 | 1.1 | 0 | 0 (absent) |
| ANY | 38 | 0.9 | 0 | 0 (absent) |
| MAP_EQ_E | 37 | 0.9 | 0 | 0 (absent) |
| CONST_2 | 35 | 0.9 | 0 | 0 (absent) |
| REDUCE_ADD | 33 | 0.8 | 0 | 0 (absent) |

**Canonical-absent operators (DUP, SLOT_12/13, THRESHOLD_SLOT, CONST_1/2, CHARS, ANY, MAP_EQ_E, REDUCE_ADD) each average ~0.8–1.7 per winner.** That's substantial operator overhead: the winner has ~12 "extra" tokens beyond the 12 canonical tokens, averaging across these non-canonical operators.

## Sample decoded winners (first 5 per sweep)

**§2a (seeds 20..39):**

- seed=23, fit=0.8542, active-len=28: `ADD SWAP CHARS CONST_0 CONST_5 INPUT ADD CONST_1 DUP CONST_1 ANY REDUCE_MAX IF_GT CONST_5 INPUT DUP CHARS SLOT_13 SUM DUP THRESHOLD_SLOT INPUT REDUCE_MAX DUP THRESHOLD_SLOT ADD CONST_1 GT`
- seed=30, fit=0.8750, active-len=29: `REDUCE_MAX SUM ANY GT INPUT CONST_5 MAP_EQ_E THRESHOLD_SLOT GT REDUCE_MAX CONST_1 MAP_EQ_E ADD MAP_EQ_E THRESHOLD_SLOT REDUCE_MAX CONST_5 IF_GT CONST_5 SUM CHARS SWAP INPUT DUP INPUT REDUCE_MAX REDUCE_MAX GT SLOT_13`
- seed=21, fit=0.9375, active-len=29: `CONST_1 DUP ANY SWAP ADD INPUT MAP_EQ_E SWAP CONST_0 SLOT_12 SLOT_13 IF_GT DUP DUP REDUCE_MAX MAP_EQ_E CONST_0 MAP_EQ_E REDUCE_MAX SLOT_13 IF_GT DUP INPUT REDUCE_MAX CHARS SLOT_12 SWAP REDUCE_ADD GT`
- seed=20, fit=0.9375, active-len=24: `SLOT_12 CHARS GT CONST_2 DUP CONST_0 SUM REDUCE_MAX INPUT CONST_0 CONST_1 DUP CONST_5 ANY SWAP SWAP CHARS ADD ADD INPUT REDUCE_MAX MAP_EQ_E REDUCE_MAX GT`
- seed=22, fit=0.9167, active-len=26: `THRESHOLD_SLOT ADD GT INPUT REDUCE_ADD SUM DUP IF_GT SWAP CHARS GT SUM IF_GT SLOT_13 INPUT REDUCE_MAX REDUCE_MAX GT DUP SLOT_13 SWAP CONST_2 SLOT_13 SWAP ADD IF_GT`

**n-exp (seeds 40..59):**

- seed=43, fit=0.9167, active-len=30: `REDUCE_MAX REDUCE_ADD CONST_1 SUM REDUCE_MAX THRESHOLD_SLOT ADD IF_GT SLOT_12 ANY SLOT_13 CONST_5 THRESHOLD_SLOT SWAP MAP_EQ_E THRESHOLD_SLOT CHARS CONST_2 REDUCE_ADD IF_GT INPUT DUP SLOT_12 SUM CONST_2 REDUCE_ADD INPUT SUM CONST_5 GT`
- seed=50, fit=0.8958, active-len=28: `CONST_5 SUM INPUT IF_GT CONST_2 CONST_2 SLOT_12 THRESHOLD_SLOT SLOT_12 MAP_EQ_E INPUT IF_GT CONST_5 CHARS CONST_5 IF_GT SUM GT SLOT_13 CONST_2 CONST_0 CONST_5 GT THRESHOLD_SLOT INPUT REDUCE_MAX CONST_2 GT`
- seed=56, fit=0.9583, active-len=23: `INPUT THRESHOLD_SLOT REDUCE_MAX IF_GT CONST_0 CONST_0 THRESHOLD_SLOT MAP_EQ_E CONST_1 SWAP SLOT_13 INPUT REDUCE_MAX THRESHOLD_SLOT SLOT_13 SLOT_13 CONST_1 ADD THRESHOLD_SLOT SLOT_13 IF_GT REDUCE_ADD GT`
- seed=51, fit=1.0000, active-len=25: `CONST_0 GT ADD CONST_0 SLOT_13 SUM CONST_1 SWAP SLOT_12 CHARS MAP_EQ_E CHARS ANY MAP_EQ_E INPUT REDUCE_MAX DUP INPUT REDUCE_ADD SLOT_13 SLOT_13 CONST_5 GT GT GT`
- seed=57, fit=1.0000, active-len=30: `SLOT_12 REDUCE_MAX CHARS CHARS DUP SLOT_13 DUP CHARS CHARS CONST_0 GT CONST_5 CHARS GT INPUT REDUCE_MAX SLOT_13 REDUCE_ADD GT DUP DUP SLOT_12 IF_GT SLOT_12 INPUT SUM CONST_5 GT IF_GT`

Both `fit=1.0000` winners (n-exp seeds 51 and 57) are clearly compositional AND-attempts with substantial operator overhead — not near-canonical.

## Implications for the §2b follow-up prereg

1. **The prereg's `top1_winner_hamming` metric needs either cap-raising or replacement.** At cap=4 it returns a single-valued sentinel on 40/40 winners; at uncapped it reveals a 9-token range that distinguishes winners. A reasonable redesign: cap at `L_canonical = 12` (so value `≥ 13` is "structurally distinct from canonical") with the interpretation "≤ 2 = near-canonical, 3–7 = compositional variant, ≥ 8 = distant-tail compositional or alternate structure."
2. **The "CB ACTIVE vs INACTIVE" categorical binning at ≤1 vs ≥2 is too coarse for this regime.** All 40 winners classify as CB INACTIVE under the prereg's rule even though 28/40 contain at least 7 of 8 canonical tokens. The prereg's follow-up must introduce a finer mechanism category that distinguishes:
   - **near-canonical** (structural identity or minor edits; active-view length close to 12; canonical token set present)
   - **compositional AND-attempt** (active-view length 20–30; canonical operators + substantial overhead; attempts AND structure): **32/40 winners**, dominant attractor
   - **single-predicate proxy** (max>5 or sum>10 alone): **6/40 winners**, minority
   - **other**: **2/40 winners**
3. **The "compositional AND-attempt with operator overhead" attractor is what selection finds under rank-1 plasticity at sf=0.0 budget=5.** It is neither classical-Baldwin (winners are far from canonical) nor single-predicate proxy (14/40 actually solve — this is NOT a `max > 5` attractor). The follow-up prereg should pre-register this as a dedicated attractor category with decision rules for how to interpret it (EES? rank-2? novel selection regime?).
4. **F_AND_test_plastic = 14/40 = 0.35** is consistent with "compositional AND-attempt attractor" where some attempts succeed semantically and some don't — roughly a 44% success rate conditional on being in this attractor. The F-lift mid-range (0.35) is therefore the natural outcome of this attractor, not an ambiguity on the F axis.
5. **The `selection-deception` diagnosis (§29 class 4) does NOT cleanly apply.** The diagnosis predicts "selection doesn't need the mechanism" because a static shortcut satisfies fitness. But at sf=0.0 there's no static canonical shortcut, and selection IS finding compositional AND structure — it's just finding it with operator overhead. The rank-1 plasticity may be providing mutation-robustness to the compositional structure (operator-threshold plasticity doesn't force convergence to a single canonical). The P-1 falsifier was framed around "shortcut removal unlocks F-recovery" vs "rank-1-intrinsic INVERSE-BALDWIN" — neither frame precisely captures "compositional AND-attempt with operator overhead."

## Methodology notes

- **Principle 3 (zero-compute inspection):** this inspection used ~5 min of Python on already-on-disk data to reveal mechanism-level structure that the cap=4 metric hid. Standard chem-tape workflow.
- **Principle 21 (attractor-category classification):** 40/40 winners were classified via the heuristic above. The category counts (32 / 4 / 2 / 2) support the §2b follow-up prereg's need to enumerate the compositional-AND-attempt category as a dedicated outcome row.
- **Principle 25/§27 (metric-fidelity drift):** the `top1_winner_hamming ∈ {0,1,2,3,4}` METRIC_DEFINITIONS entry vs the cap+1=5 sentinel is the direct cause of the information loss. The follow-up prereg must address this (cap-raise or metric replacement) before it commits to routing logic.

## Next actions (for §2b follow-up prereg authoring)

1. Determine cap value (or uncapped) for a redesigned `top1_winner_hamming`-like metric that preserves distance-to-canonical structure in the distant-tail regime.
2. Pre-register "compositional AND-attempt with operator overhead" as a dedicated attractor category with its own decision rule — what experiment does it route to?
3. Re-examine whether the `selection-deception` (§29 class 4) diagnosis applies to this attractor, or whether a new §29 class entry is needed.
4. Consider adding a `compositional_and_attempt_fraction` per-cell metric (count of winners whose active view contains the AND-predicate token set) as a diagnostic or routing axis.
5. The prereg should also commit to at-chronicle-time inspection of winner-tape decoded structure (not just per-cell counts) since the mechanism-level read is what distinguishes the attractor categories.

---

**Scratch-doc status:** inspection result only; not a methodology document. May be deleted after the §2b follow-up prereg discharges its engineering-infrastructure commitments (§25b-equivalent metric redesign + attractor-category enumeration).
