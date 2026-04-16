# Pre-registration: §v2.15-bp1-k3-nexp — n-expansion of the INTERMEDIATE (K=3, bp=1.0) cell on Pair 1

**Status:** QUEUED · target commit `TBD` · 2026-04-16

## Question (one sentence)

Does the (K=3, bond_protection=1.0) cell on §v2.6 Pair 1 — measured at 10/20 BOTH in §v2.15 (INTERMEDIATE per prereg) — cross the JOINT-LIFT threshold (≥60% BOTH) when combined with a disjoint n=40 seed block, thereby confirming or falsifying the §v2.15 Part-1 meta-learning gate outcome?

## Hypothesis

§v2.15 (commit `TBD` → logged under prereg_v2-15-decoder-grid.md) produced the following Pair 1 BOTH-solve counts at n=20 per cell:

| | bp=0.0 | bp=0.5 | bp=1.0 |
|---|---|---|---|
| K=3 | 1/20 | 4/20 (reference) | **10/20 (INTERMEDIATE)** |
| K=5 | 1/20 | 5/20 | 8/20 |

The (K=3, bp=1.0) cell at 10/20 is 2 seeds below the pre-registered JOINT-LIFT threshold of 12/20 (60%). The §v2.3 cell at (K=3, bp=1.0) is already 20/20 — the ceiling-preservation condition is trivially satisfied. The §v2.15 prereg's decision rule for INTERMEDIATE cells commits to n-expansion: **"Borderline; expand to larger n for confirmation."**

Three hypotheses about the underlying solve-rate at this cell:

1. **JOINT-LIFT confirmed.** True solve rate ≥ 60%. Expected combined count at n=60 is ≥ 36/60. Part-1 meta-learning gate **flips from NULL to PASS** — chemistry-knob leverage at bp=1.0 direction is real. bond_protection **hurts** Pair 1 discovery when non-zero.
2. **INTERMEDIATE stable.** True solve rate ∈ [50%, 55%]. Expected count 30-33/60. Borderline at larger n too; NULL remains the defensible classification at the pre-registered threshold, but the mechanism signal is real.
3. **NULL confirmed.** Initial 10/20 was an upper-tail sampling noise. True solve rate ≤ 45%. Expected count ≤ 27/60. §v2.15's NULL verdict stands firmly; Part-1 ES deprioritization confirmed.

**Mechanism reading (tentative, contingent on outcome):** if JOINT-LIFT confirms, the mechanism is *"bond_protection under BP_TOPK slows mutation on cells already extracted, which helps preservation of assembled programs on easy bodies (§v2.3 4-token) but blocks exploration on hard bodies (Pair 1 6-token). At bp=1.0, no protection = full mutation = more exploration = better discovery of the harder assembly."* This would be the first positive finding in the chem-tape suite that treats bond_protection as a **lever that can hurt**, not just help — mechanism-rename territory for `bond_protection_ratio`'s narrative.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_15_nexp_pair1_k3_bp1.yaml`
- **Arms / conditions:** single cell (K=3, bp=1.0) on Pair 1 alternation
- **Tasks:** `{any_char_count_gt_1_slot, any_char_count_gt_3_slot}` alternation, period 300
- **Seeds:** **20-59** (disjoint from §v2.15's seeds 0-19). Combined analysis over seeds 0-59 for final n=60 count.
- **Fixed params:** pop=1024, gens=1500, v2_probe alphabet, tape_length=32, arm=BP_TOPK, topk=3, bond_protection_ratio=1.0, safe_pop_mode=preserve
- **Est. compute:** ~7-8 min wall (40 configs × ~1 min / 10 workers, matching §v2.15 grid throughput)
- **Related experiments:** §v2.15 (parent grid, INTERMEDIATE at this cell), §v2.6 Pair 1 (4/20 reference at bp=0.5), §v2.14c/d/e (all §v2.14 Pair 1 work)

**Principle 20 audit:** label function (Pair 1 = any_char_count_R_gt_{1,3}) and sampler unchanged from §v2.15. Seed block is fresh (20-39 never used on this task pair in chem-tape-v2 track; 40-59 is also disjoint from §v2.3 seed-expansion blocks which use the reference cell). Principle 20 **not triggered** — no sampler or distribution change.

**Principle 23 audit (pre-declared):** this sweep runs only the single n-expansion cell. The other 5 §v2.15 cells are **explicitly not re-expanded** in this prereg — their n=20 counts stand as reported in §v2.15. This is a deliberate narrowing of scope: the INTERMEDIATE cell is the only one whose classification hinges on the n=20/n=60 difference.

## Baseline measurement (required)

- **Baseline quantity (Pair 1, bp=1.0 K=3):** BOTH-solve rate — the quantity being n-expanded.
- **Measurement:** the existing 10/20 at seeds 0-19 (§v2.15 grid_pair1, commit TBD → logged under the §v2.15 chronicle). This sweep measures seeds 20-59. Combined analysis at n=60.
- **Anchors (reference and ceiling):**
  - **Reference** (K=3, bp=0.5): 4/20 BOTH from §v2.15 grid_pair1 — the Pair 1 "hard-body floor" the cell is being compared against.
  - **§v2.3 ceiling check:** (K=3, bp=1.0) on §v2.3 is 20/20 BOTH (from §v2.15 grid_v2_3). Ceiling-preservation condition is already confirmed; we **do not re-measure it here**. If there were any chance that bp=1.0 destabilizes §v2.3 at different seeds, we would re-measure, but §v2.3 is easy enough that 20/20 on one seed block is highly likely to replicate.

## Internal-control check (required)

- **Tightest internal contrast:** the same cell (K=3, bp=1.0) on disjoint seeds 20-59 vs the existing 0-19 result. The n-expansion IS the internal control.
- **Are you running it here?** Yes.
- **Secondary anchor:** the bp=0.5 reference cell at 4/20 from §v2.15 — we are specifically testing whether bp=1.0 lifts **over** this reference. No re-measurement of bp=0.5 needed; the §v2.15 cell stands.
- **Deferred external validity:** whether the bp=1.0 lift generalizes to the E-count body (MAP_EQ_E slot), to Arm A, or to non-6-token bodies is all deferred to follow-ups after this n-expansion resolves the core question.

## Pre-registered outcomes (required — at least three)

Let `F_combined` = Pair 1 BOTH-solve count at the (K=3, bp=1.0) cell, combined over seeds 0-59 (existing 10 + new 40).

| outcome | quantitative criterion | interpretation |
|---------|------------------------|----------------|
| **PASS — JOINT-LIFT confirmed** | `F_combined ≥ 36/60` (60% BOTH) | JOINT-LIFT threshold cleared at the pre-registered scale. §v2.15 grid outcome flips from NULL to **PASS — leverage found** at this single cell. Part-1 meta-learning ES over (K, bond_protection) axes gets a concrete starting point at this cell. Mechanism reading: bond_protection hurts hard-body discovery at non-zero levels. |
| **PASS — borderline / partial** | `F_combined ∈ [30, 35]/60` (50-58% BOTH) | Between the ≥60% JOINT-LIFT threshold and the ≤40% CEILING-STABLE-NULL boundary. At n=60, 95% binomial CI is non-overlapping with the 4/20 reference rate (20%) — the lift is statistically real but below the pre-registered gate. Document the signal; treat as INTERMEDIATE-at-n-60 and queue one additional expansion block (seeds 60-119, n=120 total) before final classification. |
| **INCONCLUSIVE — within-noise** | `F_combined ∈ [24, 29]/60` (40-48%) | The 10/20 initial read was upper-tail noise; cell classification at n=60 is CEILING-STABLE-NULL. The bp=1.0 lift over bp=0.5's 4/20 reference remains directionally positive but the effect is smaller than the original INTERMEDIATE signal suggested. Narrows but does not falsify the "bond_protection hurts" reading. |
| **FAIL — NULL confirmed** | `F_combined < 24/60` (< 40%) | The 10/20 initial read was a sampling anomaly. §v2.15 NULL verdict stands firmly. Part-1 meta-learning redirection confirmed at this axis. |

**Threshold justification:**
- **JOINT-LIFT at ≥36/60 (60%):** matches the parent prereg's 12/20 (60%) threshold exactly — a linear scale preserves the pre-registered decision rule.
- **Borderline at 30-35/60 (50-58%):** matches the parent prereg's INTERMEDIATE band 9-11/20 linearly, with slight upward extension to avoid bucket-ties.
- **CEILING-STABLE-NULL at ≤24/60 (≤40%):** matches parent prereg's ≤8/20 (40%) linearly.

**Binomial reasoning.** Under H0 that the true rate is 50% (the observed 10/20 estimate), exact binomial probability of observing ≥36/60 is ~7% — a clean expansion above 60% would be strong evidence for the JOINT-LIFT reading. Under H0 that the true rate is 60%, probability of observing <30/60 is ~7% — symmetric power. At n=60 we have reasonable separation between "true 50%" and "true 60%" populations.

## Degenerate-success guard (required)

- **Too-clean (`F_combined ≥ 54/60 = 90%`):** would indicate the bp=1.0 cell solves Pair 1 better than §v2.3 solves its own task. Mechanism candidate: at bp=1.0, BP_TOPK + uniform mutation discovers a canonical Pair 1 body trivially — which contradicts the entire §v2.6 Pair 1 difficulty arc (§v2.6-pair1-scale at 4× compute = 8/20, §v2.6-pair1-scale-8x at 16× compute = 13/20). A 54/60 would suggest either (a) a sampler / task bug, (b) a decoder bug where bp=1.0 silently bypasses the executor, or (c) the task is trivially solvable under the specific (K=3, bp=1.0) configuration and the entire Pair 1 arc needs reinspection. Attractor-inspect immediately; treat as STOP-AND-AUDIT before interpretation.
- **Attractor-category inspection (principle 21 — mandatory regardless of outcome):** for the new seeds 20-59, decode winners via `decode_winner.py`. Expected attractor categories per §v2.14c chronicle: `canonical-6tok`, `partial-5tok`, `proxy-based`, `degenerate`. A PASS outcome should show canonical-6tok dominance among solvers (≥70% of solvers). If not, the cell is "solving" via a non-canonical route, and the mechanism reading narrows.
- **Seed-overlap audit:** compare solver seed-set at (K=3, bp=1.0) vs solver seed-set at (K=3, bp=0.5) on the shared seeds 0-19 (already measured). A subset relationship (bp=1.0 solvers ⊇ bp=0.5 solvers) is the expected mechanism-coherent pattern. A disjoint relationship suggests the bp=1.0 cell is finding different seeds' bodies — possibly a different mechanism entirely.
- **Drift check (cross-commit):** the §v2.15 grid ran at commit `b571ccb`. If this n-expansion runs at a later commit and the first 20 seeds' result on the exact same config hash is cached, the hash-stability principle (principle 11) guarantees no recompute. If hashes diverge, investigate before aggregating.

## Statistical test (if comparing conditions)

- **Primary test:** exact binomial test of H0: `true rate ≤ 0.40` vs H1: `true rate ≥ 0.60` on `F_combined / 60`. One-sided α = 0.05, evaluated at the combined n=60.
- **Classification (principle 22):** **confirmatory**. The test p-value gates the JOINT-LIFT claim which would enter findings.md and authorize Part-1 meta-learning ES machinery.
- **Family:** **"§v2.15 decoder-grid family"** (the single family of tests gating the JOINT-LIFT / Part-1 gate claim). Parent §v2.15 prereg did not formally classify its cell-level tests (it predates principle 22), but in retrospect its 6 cell-level classifications on Pair 1 × 2 tasks were each effectively an informal confirmatory test. For this prereg, I count the family as containing **1 confirmatory test** — this n-expansion's binomial — because §v2.15's cell counts are treated as observed data rather than independent inferential tests.
- **Corrected α:** α_FWER = 0.05 / 1 = **0.05** (no multiplicity penalty at family size 1). If the user believes §v2.15's 12 cell counts should each be counted as family members, the corrected α becomes 0.05 / 13 ≈ 0.004, and the JOINT-LIFT threshold tightens accordingly. **USER REVIEW:** confirm family-size interpretation.
- **Secondary test (exploratory):** effect-size contrast of (K=3, bp=1.0) vs (K=3, bp=0.5) via paired McNemar on shared seeds 0-19 only (since seeds 20-59 were not run at bp=0.5 in §v2.15). This is **exploratory only** — reports raw disagreement counts, no p-value gate.

## Diagnostics to log (beyond fitness)

- Per-seed BOTH-solve under (K=3, bp=1.0) for seeds 20-59
- Combined (seeds 0-59) per-seed BOTH-solve matrix
- Winner-genotype attractor-category classification for seeds 20-59 (new), plus seeds 0-19 if not already done for §v2.15
- Solver seed-set overlap analysis vs (K=3, bp=0.5) on shared seeds 0-19
- Train-holdout gap (principle 15-aligned overfit check — §v2.15 grid showed near-zero gaps; should hold here)
- Mean best-fitness and mean-final-fitness per seed (useful for distinguishing "solved" from "nearly solved")
- Wall time per run (drift check vs §v2.15 grid_pair1's per-config time)

## Scope tag (required for any summary-level claim)

**If PASS — JOINT-LIFT confirmed:**
`within-decoder-family · n=60 (20 prior + 40 new) · at BP_TOPK(K=3, bond_protection=1.0) v2_probe tape=32 gens=1500 pop=1024 · on §v2.6 Pair 1 any_char_count_gt_{1,3}_slot alternation · bond_protection=1.0 lifts hard-body BOTH-solve over bp=0.5 reference from 20% to ≥60%; §v2.3 ceiling preserved at n=20`

**If PASS — borderline or INCONCLUSIVE:** scope tag is not promoted to findings.md until further n-expansion confirms.

**If FAIL — NULL confirmed:** no new claim; §v2.15 NULL stands.

## Decision rule

- **PASS — JOINT-LIFT confirmed →** promote the bp=1.0 JOINT-LIFT finding to `findings.md` via research-rigor `promote-finding` mode. Draft Part-1 meta-learning Phase 1 prereg (ES + soft bonds) with (K=3, bp=1.0) as the initial starting point. Queue an E-count replication sweep (`§v2.15-bp1-k3-ecount`) to test whether the lift extends beyond the R-count body — this is the across-family check.
- **PASS — borderline (30-35/60) →** one additional n-expansion block (seeds 60-119, +60 runs, ~8 min). Do NOT promote to findings.md yet. Do NOT start Part-1 Phase 1 planning yet. The signal is real but unresolved at the pre-registered gate.
- **INCONCLUSIVE / CEILING-STABLE-NULL (24-29/60) →** chronicle the cell classification at n=60. Do NOT re-expand further — the 10/20 was noise, and the mechanism reading narrows to "bp=1.0 may help marginally but within-reference-noise, insufficient to support JOINT-LIFT." §v2.15 NULL stands. Part-1 deprioritization of (K, bond_protection) axes remains in effect.
- **FAIL — NULL confirmed (<24/60) →** chronicle the NULL confirmation. Close the §v2.15 INTERMEDIATE thread. Any remaining bond_protection exploration goes through a *different* axis (e.g., within-cell mutation-rate interaction, or body-length × bp interaction) — not this specific (K, bp) grid.

---

*Audit trail.* Four outcome rows (principle 2: PASS-clean, PASS-partial, INCONCLUSIVE, FAIL). Thresholds linear-scaled from parent §v2.15 prereg's 12/20 / 9-11/20 / ≤8/20 gate (principle 6). Internal control is the n=20 → n=60 self-comparison on disjoint seeds (principle 1). Degenerate-success candidates include STOP-AND-AUDIT trigger at ≥54/60 and mandatory attractor inspection regardless of outcome (principle 4). Principle 20 not triggered. Principle 22 classification explicit: confirmatory test, family "§v2.15 decoder-grid family" at size 1 (with user-review note on alternative family-size interpretation). Principle 23 pre-declared — only the INTERMEDIATE cell re-runs, other §v2.15 cells are deliberately not re-expanded. Decision rule commits to exact next-step actions per outcome (principle 19) — including the "one more block" commitment for borderline to prevent post-hoc reroute.

**USER REVIEW CHECKLIST** (before commit):
- [ ] Approve seed block 20-59 (40 new seeds, disjoint from §v2.15's 0-19)
- [ ] Confirm family-size interpretation (1 confirmatory test → α=0.05 uncorrected)
- [ ] Approve the ≥36/60 JOINT-LIFT absolute threshold and the [30, 35] borderline band
- [ ] Confirm decision rule — especially the "one more block" commitment for borderline
- [ ] Confirm commit-hash gating
