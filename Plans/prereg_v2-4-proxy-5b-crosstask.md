# Pre-registration: §v2.4-proxy-5b-crosstask — cross-task scope test of BOTH-KINETIC R_fit signal on `sum_gt_5_slot`

**Status:** QUEUED — BLOCKED on canonical-tape identification for `sum_gt_5_slot` (see Engineering Prerequisite below) · target commit TBD · 2026-04-18 · upstream chronicle at [docs/chem-tape/experiments-v2.md §v2.4-proxy-5b-amended](../docs/chem-tape/experiments-v2.md)

## Upstream context

§v2.4-proxy-5b-amended (commit `4aa8b40`, 2026-04-18) returned **BOTH-KINETIC**: both BP_TOPK preserve and Arm A show R_fit_999 kinetic lift under lower mutation rates on `sum_gt_10_AND_max_gt_5` natural sampler. Specifically:
- Arm A: massive R_fit_999 lift (structural → kinetic signal);
- BP_TOPK: modest R_fit_999 lift, with monotone pattern across mr ∈ {0.005, 0.015, 0.03}.

Before any paper-level citation, methodology principle 17 (scope-boundary) requires a cross-task scope test: does this kinetic signal generalise to an independent load-bearing task, or is it confined to the `sum_gt_10_AND_max_gt_5` natural-sampler task? The §v2.4-proxy-5b-amended decision rule explicitly commits: *"Queue cross-task scope test (§v2.4-proxy-5b-crosstask) before paper-level citation."*

## Engineering prerequisite (BLOCKING)

The canonical tape for `sum_gt_5_slot` under BP_TOPK(k=3, bp=0.5) must be identified before `seed_tapes` can be set in the sweep YAML.

**Status of canonical tape identification:**

The most common `best_genotype_hex` for `sum_gt_5_slot` across prior runs is:
```
1100081010040d0b02111213100a1009040511080713130c090f0f010b130d08
```
(12/22 occurrences in prior sweep outputs). However, this is materially less dominant than the `sum_gt_10_AND_max_gt_5` canonical (60/60 occurrences), and its dominance across arms and mutation rates has not been confirmed in a dedicated baseline.

**Two resolution options (Option 1 chosen 2026-04-18):**

1. **[CHOSEN] Run a new baseline sweep** on `sum_gt_5_slot`: unseeded BP_TOPK(k=3, bp=0.5) at pop=1024, gens=1500, mr=0.03, seeds 0–19. Take the best-of-run genotype that occurs in ≥ 15/20 seeds as the canonical. If no genotype meets that bar, the task may lack a stable dominant attractor and this experiment's seeding design requires rethinking.

   **Discharge path (2026-04-18):** Option 2 is unavailable — the §v2.3 fixed-baseline sweep outputs (`2026-04-14/v2_3_fixed_baselines`) are not on disk in the current working tree. Option 1 is executed via the already-queued `v2_3_fixed_baselines` entry in `queue.yaml:63` (runs `experiments/chem_tape/sweeps/v2/v2_3_fixed_baselines.yaml`, which is byte-identical to Option 1's specified parameters — BP_TOPK(k=3, bp=0.5), pop=1024, gens=1500, mr=0.03, seeds 0–19, plus `sum_gt_10_slot` as a free byproduct). Post-sweep analysis script: `experiments/chem_tape/check_canonical.py` on the `sum_gt_5_slot` cells of the sweep output. Decision rule at morning triage:
   - **≥ 15/20 seeds converge to one hex →** update `seed_tapes` field below to that hex; flip this prereg's Status to `RUNNING`; commit; launch the main crosstask sweep on the next queue cycle.
   - **< 15/20 seeds converge to any single hex →** `sum_gt_5_slot` lacks a stable dominant attractor under BP_TOPK at this configuration. Update this prereg with a `SUPERSEDED-DESIGN` block and propose an alternative seeding design (e.g., seed with the full per-seed canonical per-seed rather than a universal canonical; or change cross-task target to `sum_gt_10_slot`).

2. **~~Examine §v2.3 fixed-baseline run outputs~~** — unavailable in this working tree. Rejected 2026-04-18.

**Unblocking commit:** The prereg's `seed_tapes` field below is marked `TBD (BLOCKED)`. The `v2_3_fixed_baselines` queue entry runs tonight (2026-04-18); when the canonical tape is confirmed from that sweep's output, update this field and commit the change. The main crosstask sweep may not run until that commit exists.

---

## Question (one sentence)

Does the BOTH-KINETIC R_fit_999 mutation-rate signal — in which both BP_TOPK preserve and Arm A show monotone R_fit_999 lift at lower mutation rates under seeded initialisation — replicate on `sum_gt_5_slot` (slot-indirection arithmetic task, threshold=5, no AND-conjunction), an independent load-bearing task from §v2.3?

## Hypothesis

The BOTH-KINETIC signal observed in §v2.4-proxy-5b-amended is a property of the variation-layer kinetics (erosion rate scales with mutation pressure regardless of task), not of the specific `sum_gt_10_AND_max_gt_5` task structure. Under this reading, `sum_gt_5_slot` — which shares the arithmetic domain and the slot-indirection structure, but differs in threshold value, absence of AND-conjunction, and uses the simpler INPUT ACCUMULATE ADD_IF_GT 5 HALT body — should show qualitatively similar kinetic lift patterns under the same arm × mr sweep.

Competing reading: the BOTH-KINETIC signal is task-conditioned on `sum_gt_10_AND_max_gt_5`'s specific proxy-basin geometry (the AND task's wider solver neutral network under BP_TOPK; its specific proxy-basin under Arm A). The simpler `sum_gt_5_slot` task — which has a more compact canonical body (4 tokens vs 12 tokens), a stronger fixed-task solve signal (20/20 at baseline vs 20/20 but different attractor geometry), and no proxy-basin — may be structurally rate-insensitive.

Prior data bear on both readings: §v2.11 shows Arm A achieves 18/20 on `sum_gt_5_slot` at mr=0.03 unseeded — the task is solvable under Arm A, but the proxy-basin mechanism may be absent (no complex AND structure for a proxy predicate to exploit). If the kinetic signal in §v2.4-proxy-5b-amended was driven by proxy-basin retention dynamics rather than generic erosion kinetics, it may fail or attenuate on `sum_gt_5_slot`.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_4_proxy5b_crosstask.yaml` (to be written when unblocked)
- **Arms / conditions:** `mutation_rate ∈ {0.005, 0.015, 0.03}` × `arm ∈ {BP_TOPK preserve, A}` × `seed_fraction ∈ {0.0, 0.01}`. 3 × 2 × 2 = 12 cells. **Plus: budget-decoupling cell** (principle 17 scope-boundary for the "kinetic" framing, added 2026-04-18 per review of §v2.4-proxy-5b-amended's budget-vs-rate confound): `mutation_rate=0.005` × `generations=9000` × `arm ∈ {BP_TOPK preserve, A}` × `seed_fraction=0.01`. 2 cells. **Total: 14 cells × 20 seeds = 280 runs.**
  - BP_TOPK cells: `topk=3, bond_protection_ratio=0.5` (matches §v2.4-proxy-5b baseline).
  - Arm A cells: default `topk=1` (ignored for arm=A execution; decoded view is informational only).
  - Budget-decoupling cells match total expected mutation count of the mr=0.03 × gens=1500 baseline (~45 mutations per tape) by using mr=0.005 × gens=9000 (same expected count ~45), holding everything else identical. If R_fit_999 at mr=0.005 × gens=9000 matches the mr=0.005 × gens=1500 cell, the kinetic effect is rate-driven (not budget-driven). If it matches the mr=0.03 × gens=1500 cell, the "kinetic" framing is actually a total-mutation-budget framing and the claim in findings.md#proxy-basin-attractor must be rewritten.
- **Task:** `sum_gt_5_slot` (INPUT ACCUMULATE ADD_IF_GT 5 HALT; threshold slot-bound to 5).
- **Seeds:** 0..19 per cell (same seed range as §v2.4-proxy-5b-amended, enabling cross-task per-seed comparison; budget-decoupling cells reuse seeds 0..19).
- **Fixed params:** `safe_pop_mode=preserve`, `pop_size=1024`, `generations=1500` (except budget-decoupling cells: `generations=9000`), `tournament_size=3`, `elite_count=2`, `crossover_rate=0.7`, `tape_length=32`, `alphabet=v2_probe`, `disable_early_termination=true`, `dump_final_population=true`, `seed_tapes=TBD (BLOCKED — see Engineering Prerequisite)`, `n_examples=64`, `holdout_size=256`, `backend=mlx`. Only `mutation_rate`, `arm`, `seed_fraction`, and (for budget cells) `generations` vary.
- **Est. compute:** main 12 cells ~40–60 min wall at 10 workers; budget-decoupling cells 6× wall per run due to 6× generations — ~4–8 min/run × 40 runs / 10 workers ≈ 20–40 min wall. Total ~60–100 min wall.
- **R_fit_holdout_999 axis (added 2026-04-18 per post-E1 engineering of `analyze_retention.py --include-holdout`):** report `R_fit_holdout_999` and `R_fit_holdout_mean` alongside `R_fit_999` for every cell. The main cross-task question is whether low-mr kinetic lift generalises; the holdout axis tests whether the lift is in generalizing solvers or in train-only proxy-fitters.
- **Related experiments:** §v2.4-proxy-5b-amended (the BOTH-KINETIC upstream result, commit `4aa8b40`); §v2.3 (load-bearing provenance of `sum_gt_5_slot`); §v2.11 (Arm A baseline on `sum_gt_5_slot` at mr=0.03, 18/20).

**Principle 20 audit:** Task identifier changes from `sum_gt_10_AND_max_gt_5` to `sum_gt_5_slot`. The label function changes (single threshold vs AND-conjunction), the input distribution is the same natural sampler (integer inputs), and the sampler range is unchanged. This is a **task change**, not a sampler design change — principle 20 applies insofar as the label function is new, but the degenerate-label guard is already satisfied by prior evidence:
- (i) Class balance: natural sampler over [0,9]×n; `sum > 5` fires on a large fraction of examples — not degenerate.
- (ii) Fixed-task baseline: §v2.3 shows 20/20 at pop=1024, gens=1500, mr=0.03, BP_TOPK(k=3, bp=0.5). Task is learnable.
- (iii) Non-degeneracy: §v2.11 confirms 18/20 Arm A solve rate. Predicting constant-0 does not win.

Principle 20 gate is satisfied by existing measurements. No new sampler audit run required before the sweep.

**Principle 23 audit:** The `mr=0.03 × sf=0.01` cells (both arms) are the internal baseline for this experiment. They must reproduce the fixed-task solve rate (F ≥ 18/20 in both arms) before interpreting any lower-mr cells. The seeded mr=0.03 baseline is the anchor; if it fails to reproduce, investigate before running additional cells.

## Baseline measurement (required)

- **Baseline for this task (principle 6):**
  - `sum_gt_5_slot` fixed-task (unseeded, mr=0.03): BP_TOPK 20/20 (§v2.3 fixed baselines, 2026-04-14). Arm A 18/20 (§v2.11, seeds {3, 14} stuck).
  - `sum_gt_5_slot` seeded (sf=0.01, mr=0.03), both arms: **not yet measured — will be the `mr=0.03 × sf=0.01` cells of this sweep.** These cells form the principle-23 baseline gate.
  - Cross-task comparison anchor (§v2.4-proxy-5b-amended at `mr=0.03 × sf=0.01`):
    - BP_TOPK: R_fit_999 = 0.723; R₂_decoded = 0.0024. (Commit `cca2323`.)
    - Arm A: R_fit_999 = 0.004; R₂_decoded = 0.0046 (informational). (Same commit.)

- **Metric definitions (principle 27, cited verbatim from `experiments/chem_tape/analyze_retention.py` METRIC_DEFINITIONS):**
  - `R_fit_999`: *"Fraction of final-population individuals whose training-task fitness is >= 0.999 (near-canonical fitness proxy, independent of structural distance from canonical)."*
  - `R2_decoded`: *"Fraction of final-population tapes whose BP_TOPK(k=topk) decoded view — the exact token sequence passed to the VM under arm=BP_TOPK, computed as the top-K longest non-separator runs concatenated in tape order via engine.compute_topk_runnable_mask — is within Levenshtein edit distance 2 of canonical's decoded view. For arm=A runs this view is informational (the VM executes the raw tape), not execution-semantic."*
  - `R2_active`: *"Fraction of final-population tapes whose permeable-all active view (non-NOP, non-separator tokens in tape order) is within Levenshtein edit distance 2 of canonical's 12-token active program. This view is a SUPERSET of the BP_TOPK(k) decode; active-view and decoded-view distances can disagree in either direction (Levenshtein is not monotone under the top-K-longest-run subsequence restriction)."*
  - `unique_genotypes`: *"Count of distinct 32-token tapes in the final population, by raw byte equality. Upper-bounds full-population exact-match retention: R_exact <= (pop_size - unique_genotypes) / pop_size."*
  - `bootstrap_ci_spec`: *"Nonparametric bootstrap over per-seed values: 10 000 resamples with replacement via numpy.random.default_rng(seed=42); 95% CI is the [2.5%, 97.5%] empirical quantile of the resampled means."*

## Internal-control check (required)

- **Tightest internal contrast per arm:** `mutation_rate=0.005` vs `mutation_rate=0.03` at the same `sf=0.01`, same seeds, same task, same commit. This is the direct kinetic-vs-structural contrast within `sum_gt_5_slot`.
- **Cross-arm contrast:** at matched `mutation_rate`, compare R_fit_999 lift pattern between BP_TOPK and Arm A. If the two arms diverge on `sum_gt_5_slot` in a way they do not diverge on `sum_gt_10_AND_max_gt_5`, that is task-conditional arm-specific kinetics.
- **Cross-task contrast (the primary question):** compare per-arm R_fit_999 lift magnitudes at mr=0.005 on `sum_gt_5_slot` (this sweep) vs `sum_gt_10_AND_max_gt_5` (§v2.4-proxy-5b-amended, commit `4aa8b40`). Seed sets are matched (0–19), enabling a direct cross-task comparison at the per-arm level.
- **Are you running it here?** Yes — all twelve cells span the internal contrast. The cross-task contrast uses data already on disk from §v2.4-proxy-5b-amended.

## Pre-registered outcomes (required — §26-compliant cross-product grid)

### Grid axes and coarse bins

| axis | arm scope | coarse bins |
|---|---|---|
| `R_fit_999` at mr=0.005 vs mr=0.03 baseline (within this sweep) | both arms | low < 0.1 · mid 0.1–0.7 · high ≥ 0.7 |
| `R_fit_999` lift magnitude vs §v2.4-proxy-5b-amended (cross-task comparison) | both arms | within-2× · >2× difference · opposite-direction |
| `F_slot` at mr=0.005 × sf=0.01 | both arms | 20/20 · partial 15–19/20 · swamped < 15/20 |

**Rationale for primary metric:** R_fit_999 is primary for both arms, as established by §v2.4-proxy-5b-amended's grid repair. R₂_decoded for Arm A is informational only (same degenerate-success guard applies). Cross-task comparison uses within-arm R_fit_999 lift magnitude at mr=0.005 vs mr=0.03.

### Per-arm outcome rows (R_fit_999 kinetic profile on sum_gt_5_slot)

#### Arm A outcome rows

| outcome | R_fit_999 at mr=0.005 vs baseline mr=0.03 | F_slot | interpretation |
|---|---|---|---|
| **A-KINETIC** | high ≥ 0.3 (substantial lift) | 20/20 | Arm A shows kinetic lift on sum_gt_5_slot. |
| **A-MILD** | mid 0.1–0.3 (moderate lift) | 20/20 | Arm A shows attenuated kinetic signal on this simpler task. |
| **A-STRUCTURAL** | low < 0.1 (no lift) | 20/20 | Arm A rate-insensitive on sum_gt_5_slot. |
| **A-SWAMPED** | any | F < 18/20 | mr=0.005 too low to sustain solving from seed on this task. |

#### BP_TOPK outcome rows

| outcome | R_fit_999 at mr=0.005 vs baseline mr=0.03 (≈ 0.723 expected) | R₂_decoded at mr=0.005 | F_slot | interpretation |
|---|---|---|---|---|
| **BP-KINETIC-FULL** | high ≥ 0.85 | high ≥ 0.05 | 20/20 | Full kinetic signal: solver retention and canonical proximity both lift. |
| **BP-KINETIC-RFLT** | high ≥ 0.85 | low < 0.05 | 20/20 | Solver retention lifts; canonical proximity unchanged. Partial kinetic on fitness dimension. |
| **BP-MILD-FULL** | mid 0.1–0.7 | high ≥ 0.05 | 20/20 | Moderate retention lift with canonical proximity lift. |
| **BP-MILD-RFLT** | mid 0.1–0.7 | low < 0.05 | 20/20 | Moderate retention lift only. |
| **BP-STRUCTURAL** | low (within 95% CI of baseline mr=0.03 value in this sweep) | low < 0.05 | 20/20 | Rate-insensitive on sum_gt_5_slot; structural decoder geometry dominates. |
| **BP-STRUCTURAL-SHIFT** | low (within CI) | high ≥ 0.05 | 20/20 | Fitness retention unchanged; canonical proximity shifts. Unusual — note if observed. |
| **BP-SWAMPED** | any | any | F < 18/20 | mr=0.005 too low for BP_TOPK arm on this task. |

**Note on BP baseline at mr=0.03:** The `mr=0.03 × sf=0.01` cell of this sweep (not §v2.4-proxy-5b-amended) is the within-task baseline. R_fit_999 at mr=0.03 on `sum_gt_5_slot` may differ from 0.723 (measured on `sum_gt_10_AND_max_gt_5`). All threshold comparisons use the measured mr=0.03 value from this sweep, not the imported 0.723 figure.

### Cross-task outcome rows (primary experiment question)

| outcome | R_fit pattern on sum_gt_5_slot vs sum_gt_10_AND_max_gt_5 | interpretation |
|---|---|---|
| **REPLICATES** | Both arms show monotone R_fit_999 lift at lower mr; magnitudes within 2× of §v2.4-proxy-5b-amended values | BOTH-KINETIC finding generalises across task families within the arithmetic domain; variation-layer direction is task-general within this family. |
| **PARTIAL** | One arm replicates kinetic lift (A-KINETIC or A-MILD; BP-KINETIC-*); the other is rate-insensitive (A-STRUCTURAL; BP-STRUCTURAL) on sum_gt_5_slot | Task-specific component in the kinetic signal; finding is arm-conditional × task-conditional. |
| **ATTENUATED** | Both arms show kinetic lift on sum_gt_5_slot but magnitudes are >2× smaller than §v2.4-proxy-5b-amended values | Kinetic signal is task-general but task-strength-dependent; simpler task attenuates the erosion rate. |
| **FAILS** | Neither arm shows substantial R_fit_999 lift at lower mr on sum_gt_5_slot (both A-STRUCTURAL + BP-STRUCTURAL) | BOTH-KINETIC is task-specific to sum_gt_10_AND_max_gt_5; findings.md scope must stay single-task. |
| **SWAMPED** | F_slot < 18/20 at mr=0.005 in either arm | Exploration failure on sum_gt_5_slot at low mutation; repeat at mr=0.01 before interpreting. |
| **INCONCLUSIVE** | any other pattern (e.g., non-monotone; opposing arm directions with neither matching a clean cross-task outcome) | Update grid per principle 2b before interpreting. |

### Monotonicity cell (mr=0.015 interpolation)

Both arms: if R_fit_999 shows monotone lift from mr=0.03 → mr=0.015 → mr=0.005 on `sum_gt_5_slot`, the kinetic reading is strengthened. Non-monotonicity is an INCONCLUSIVE qualifier. (Note: the §v2.4-proxy-5a-followup-mid-bp result, 2026-04-18, showed that a 3-point sweep on bond_protection_ratio hid a non-monotone staircase that a 5-point sweep uncovered. A 3-point mr grid on `sum_gt_5_slot` could hide a similar structure. If the Monotonicity-cell criterion is marginally met with only 3 points, add a 4th mr value from {0.008, 0.010, 0.020} to triangulate before committing to monotone.)

### Budget-decoupling outcome rows (principle 17 scope-boundary on the "kinetic" framing)

**Confound acknowledgement (added 2026-04-18 after codex adversarial review).** The §v2.4-proxy-5b-amended "BOTH-KINETIC" framing names a rate effect, but `mr=0.005 × gens=1500` vs `mr=0.03 × gens=1500` confounds four simultaneous process variables: (a) expected per-tape mutation count (7.5 vs 45); (b) total selection opportunities per lineage (1500 gens either way — equal); (c) crossover opportunities per lineage (equal); (d) time-to-fixation for any given beneficial variant. The `mr=0.005 × gens=9000` cell matches (a) to the `mr=0.03 × gens=1500` baseline but changes (b), (c), and (d) by 6×. Therefore **this prereg cannot cleanly decompose "rate" from "total process budget"** — it discriminates "per-tape mutation count" from "rate-plus-time-plus-selection-opportunities" bundle, which is weaker than the earlier draft implied. Outcome row language is tightened below; no outcome supports an unqualified rewrite of `findings.md#proxy-basin-attractor` from "kinetic" to "mutation-budget-driven."

| outcome | R_fit_999 at mr=0.005, gens=9000 (per-tape-mutation-matched, gens increased 6×) vs the two anchors | interpretation |
|---|---|---|
| **PER-TAPE-MUTATION-INVARIANT** | Budget cell matches mr=0.005 × gens=1500 (within 0.1 R_fit) and differs from mr=0.03 × gens=1500 by > 0.15 | The per-tape mutation count is NOT the causal lever (or at least not the dominant one); the 6× extra generations do not erode the low-mr lift. Consistent with "rate-or-time-or-selection-opportunity" being the operative mechanism; the kinetic framing in findings.md is not falsified but is narrowed — the lift survives extended evolution. Do NOT claim rate-driven; claim rate-OR-time-OR-selection-opportunity driven. |
| **PER-TAPE-MUTATION-BUDGET-MATCHED** | Budget cell matches mr=0.03 × gens=1500 (within 0.15 R_fit) and differs from mr=0.005 × gens=1500 by > 0.15 | Per-tape mutation count IS a causal lever; under budget-matched conditions the low-mr lift attenuates. This would narrow the kinetic claim: R_fit_999 responds to per-tape mutation count, not to per-generation rate specifically. **Does not trigger a rewrite of findings.md#proxy-basin-attractor from "kinetic" to "mutation-budget-driven"** — that language would still be overreach because the `gens=9000` cell also changes selection opportunities. Queue a fixed-generation pop-scaled sub-experiment (pop=512 vs pop=2048 at matched gens × mr) to further decouple. |
| **MIXED-RESPONSE** | Budget cell is between the two anchors (neither matches within thresholds) | Both per-tape count and per-generation rate (or time/selection-opportunities) matter, non-decomposable at this scale. Report as such; no finding-layer rename. |
| **BUDGET-INCONCLUSIVE** | Budget cell shows unexpectedly different mechanism (e.g., R_fit_999 drops below mr=0.03 baseline under long runs — suggests selection saturation or long-horizon attractor dynamics) | Inspect final populations before interpreting. Potential selection-saturation or long-horizon artefact. |

Thresholds: the 0.15 margin is ~3× the per-cell bootstrap CI half-width observed in §v2.4-proxy-5b-amended (~0.05). Rate-vs-budget discrimination requires a clean signal; within-CI outcomes are BUDGET-INCONCLUSIVE by design.

**No outcome of this cell alone rewrites `findings.md#proxy-basin-attractor` from "kinetic" to "mutation-budget-driven."** Principle 17 overreach guard: a single 2-cell contrast with a 6× confound in selection opportunities cannot support that paper-level rewrite. The PER-TAPE-MUTATION-BUDGET-MATCHED outcome triggers further experiments to disambiguate, not a findings.md rewrite.

**R_fit_holdout_999 annotation:** for every budget-decoupling cell, also report `R_fit_holdout_999` and its difference from the matched within-anchor cell. If budget cells show `R_fit_999` matching but `R_fit_holdout_999` diverging, the budget-vs-rate mechanism differs in generalization — diagnostic; does not enter the outcome grid, but informs the next prereg.

## Degenerate-success guard (required)

1. **Mutation-rate-too-low artefact (SWAMPED rows):** at mr=0.005 × sf=0.01, F_slot must be ≥ 18/20 per arm. `unique_genotypes` per arm must exceed 500/1024. `R₀_decoded` at sf=0.0 must remain 0.000 (no drift solve without seed).

2. **Task-too-easy artefact:** `sum_gt_5_slot` solves 20/20 at baseline (§v2.3) and is described as CONTROL-DEGENERATE in §v2.7-pair1-transitions (random init frequently lands near canonical). If seeded R_fit_999 at mr=0.03 is already ≥ 0.9 (near-ceiling) in this sweep, the mr=0.005 lift margin is too small to detect kinetic effects. Detection: if `R_fit_999` at mr=0.03 × sf=0.01 exceeds 0.9 in either arm, flag as task-ceiling-limited; the cross-task comparison is then non-informative for that arm (not the same as STRUCTURAL — a null from a ceiling task is uninterpretable).

3. **Canonical-tape instability artefact:** if seed_tapes is set to a genotype that is not the true dominant best-of-run on `sum_gt_5_slot`, seeds may converge to a different canonical and the seeded-fraction × retention metrics will be miscomputed. Detection: per-seed best-of-run hex at sf=0.01 must cluster around the canonical tape (≥ 15/20 seeds converge to canonical at mr=0.03 × sf=0.01). If fewer converge, flag as seed-tape-instability and revisit the canonical tape identification.

4. **Arm A decoded-view artefact:** Arm A R₂_decoded values are informational only (VM executes raw tape); no Arm A mechanism claim rests solely on the decoded column.

5. **Non-monotonicity flag:** R_fit_999 that lifts at mr=0.015 but falls at mr=0.005 is flagged as INCONCLUSIVE on the kinetic axis; do not claim kinetic without monotone pattern.

## Statistical test (principle 22)

- **Primary:** per-cell bootstrap 95% CI on R_fit_999, R₂_decoded, R₂_active (via `analyze_retention.py`). Cross-task magnitude comparison uses bootstrap CI overlap between this sweep's mr=0.005 cells and §v2.4-proxy-5b-amended's corresponding cells.
- **Classification (principle 22): exploratory.** Does not gate a new findings.md claim; provides cross-task scope evidence for the BOTH-KINETIC reading in `findings.md#proxy-basin-attractor`.
- **Family (principle 22):** n/a (exploratory). Proxy-basin FWER family size unchanged. No new confirmatory test enters the family.
- **Corrected α:** not applicable (exploratory; no p-value gate).

**Rationale:** This experiment's primary purpose is scope qualification (principle 17), not a new mechanism claim. The result narrows or broadens the geographic scope of the BOTH-KINETIC finding; it does not add an independent positive claim to the proxy-basin FWER family.

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_slot`, best-of-run fitness (expected 20/20 and 1.0 at sf=0.01, mr=0.03)
- Per-cell `R_fit_999`, `R₂_decoded`, `R₂_active`, `R₂_raw`, `unique_genotypes`, `final_generation_mean`
- Per-cell bootstrap 95% CI on all three R₂ views + R_fit_999
- Edit-distance histogram {0, 1, 2, 3, ≥4} active-view per cell
- Per-seed best-of-run hex at sf=0.01 per arm — canonical convergence check (degenerate-success guard item 3)
- **Cross-task magnitude table:** for each arm, tabulate R_fit_999 at mr ∈ {0.005, 0.015, 0.03} in this sweep alongside the matched §v2.4-proxy-5b-amended values. This is the primary cross-task comparison artefact.
- Drift-check: R_fit_999 at sf=0.0 across all mutation rates, both arms (expected ≈ 0.000)

## Measurement-infrastructure gate (principle 25)

- **R_fit_999:** produced directly by `experiments/chem_tape/analyze_retention.py` when `dump_final_population=True` is set in sweep config. Column: `R_fit_999_mean` per cell in the summary CSV. Status: **produced directly**.
- **R₂_decoded, R₂_active:** produced directly by `analyze_retention.py` under the same dump condition. Status: **produced directly**.
- **unique_genotypes:** produced directly by `analyze_retention.py`. Status: **produced directly**.
- **bootstrap_ci_spec:** produced by `analyze_retention.py` bootstrap routine. Status: **produced directly**.
- **Cross-task magnitude table:** post-hoc analysis joining this sweep's output with §v2.4-proxy-5b-amended's stored CSVs. No new infra required — both are standard `analyze_retention.py` outputs. Status: **produced directly by joining existing outputs**.

All committed metrics are in state (i) (produced directly). No proxy substitutions. Principle 25 gate satisfied.

## Scope tag (required for any summary-level claim)

**If REPLICATES:** `across-family (arithmetic sampler) · n=20 per cell (12 cells) · at pop=1024 gens=1500 tournament_size=3 elite_count=2 crossover_rate=0.7 v2_probe disable_early_termination=true · on sum_gt_5_slot + sum_gt_10_AND_max_gt_5 (arithmetic domain, natural sampler) · BP_TOPK(k=3, bp=0.5) preserve + Arm A direct GP · mutation_rate ∈ {0.005, 0.015, 0.03} · seeded canonical body at sf ∈ {0.0, 0.01}`.

**If PARTIAL or FAILS:** `within-family (sum_gt_10_AND_max_gt_5 only) · n=20 per cell · BOTH-KINETIC scope does not extend to sum_gt_5_slot [or is arm-conditional on sum_gt_5_slot]`. findings.md scope tag must be narrowed to single-task before paper-level citation.

**If ATTENUATED:** `across-family (arithmetic sampler, with task-strength qualification) · BOTH-KINETIC generalises but magnitude depends on task complexity`.

## Decision rule

- **REPLICATES →** update `findings.md#proxy-basin-attractor`: add cross-task scope note. Promote BOTH-KINETIC scope from `within-family (sum_gt_10_AND_max_gt_5)` to `across-family (arithmetic sampler) — replicated on sum_gt_5_slot`. Write the scope tag with both tasks and n=20 per cell × 2 tasks. Queue n=20 independent-seed replication block (seeds 20–39, both tasks) before paper-level citation.
- **ATTENUATED →** update `findings.md#proxy-basin-attractor` with cross-task qualifier: "BOTH-KINETIC generalises to arithmetic-domain slot-indirection tasks but magnitude scales with task complexity (compound AND > simple threshold)." Scope stays `across-family (arithmetic sampler)` with the attenuation qualifier. Queue a third task to triangulate the magnitude-vs-complexity relationship.
- **PARTIAL →** interpret per-arm: whichever arm replicates kinetic lift stays at current scope; the non-replicating arm's kinetic claim is narrowed to `task-specific (sum_gt_10_AND_max_gt_5 only)`. findings.md update depends on which arm replicates.
- **FAILS →** `findings.md#proxy-basin-attractor` scope stays single-task. Add explicit scope boundary note: "BOTH-KINETIC does not replicate on sum_gt_5_slot — finding is specific to sum_gt_10_AND_max_gt_5 natural sampler." Paper-level citation requires additional task coverage to claim cross-task generality.
- **SWAMPED (either arm) →** re-run the affected arm at mr=0.01 instead of mr=0.005 before interpreting. Do not claim STRUCTURAL from a swamped cell.
- **TASK-CEILING-LIMITED (degenerate-success guard item 2 fires) →** the cross-task comparison is uninformative for the ceiling arm. Document as unresolvable at this task with this seeding design. Consider a harder arithmetic task (e.g., `sum_gt_10_slot`, `sum_gt_15_slot`) as a replacement cross-task target. Do not claim FAILS — a ceiling is not a null.
- **SEED-TAPE-INSTABILITY (degenerate-success guard item 3 fires) →** halt interpretation; re-identify the canonical tape for sum_gt_5_slot and rerun. The blocked-prerequisite process above applies again.
- **INCONCLUSIVE →** update the outcome grid per principle 2b, then re-interpret.
- **PER-TAPE-MUTATION-INVARIANT (budget-decoupling cell) →** record the result in `findings.md#proxy-basin-attractor`'s supporting-experiments row with the scope-qualifier "per-tape mutation count is not the dominant lever; rate-or-selection-opportunity-or-time driven." **Does not unqualify** the kinetic framing as paper-level; the confound (6× selection opportunities at gens=9000) remains, so the phrase "kinetic" narrows to "per-generation-rate-or-time driven." Queue the fixed-generation pop-scaled sub-experiment (pop ∈ {512, 2048} at mr=0.005 × gens=1500) to further decouple selection opportunities.
- **PER-TAPE-MUTATION-BUDGET-MATCHED (budget-decoupling cell) →** narrow findings.md: the kinetic qualifier becomes "per-tape mutation count driven (confounded with selection opportunities at 6× extended generations — a cleaner decoupling sweep is queued)." **Explicitly not a rewrite** to "mutation-budget-driven" without the follow-up sub-experiment; a single 2-cell contrast with a 6× selection-opportunity change cannot support that level of scope change (principle 17). Queue fixed-generation pop-scaled sub-experiment before any further findings-layer update.
- **MIXED-RESPONSE (budget-decoupling cell) →** `findings.md#proxy-basin-attractor` keeps both per-tape count and rate/time/selection-opportunity bundle as listed levers; scope tag adds "(process variables not decomposable at gens=1500 vs gens=9000)". No rewrite; narrowing qualifier only.
- **BUDGET-INCONCLUSIVE (budget-decoupling cell) →** halt paper-level citation of the kinetic framing; queue a pop-scaled sub-experiment (e.g., pop=512 vs pop=2048 at mr=0.005 gens=1500) to disambiguate before any further kinetic claim.

---

*Audit trail.* Question inherits from §v2.4-proxy-5b-amended (same kinetic mechanism probe, new task + budget-decoupling extension). Principle 1: internal cross-arm, cross-mr, and cross-gens contrasts are within-sweep; cross-task contrast uses §v2.4-proxy-5b-amended data on disk. Principle 2: five cross-task outcome rows (REPLICATES, PARTIAL, ATTENUATED, FAILS, SWAMPED) + four budget-decoupling rows (PER-TAPE-MUTATION-INVARIANT, PER-TAPE-MUTATION-BUDGET-MATCHED, MIXED-RESPONSE, BUDGET-INCONCLUSIVE) plus INCONCLUSIVE. Principle 2b: per-arm grid is the full cross-product of (R_fit_999 bin × R₂_decoded bin × F_slot bin) as in §v2.4-proxy-5b-amended; cross-task grid adds ATTENUATED as a distinct non-paired row; budget-decoupling grid is a three-way anchor comparison (mr=0.005×gens=1500, mr=0.03×gens=1500, mr=0.005×gens=9000). Principle 4: three degenerate-success candidates (swamped, task-ceiling, canonical-tape-instability) plus inherited Arm A decoded-view and non-monotonicity guards. Principle 6: within-sweep mr=0.03 baseline is the threshold anchor — no imported absolute numbers from other tasks. Principle 17: BLOCKED status prevents overreach; cross-task scope tag is not claimed until the sweep runs; budget-decoupling cells added 2026-04-18 after the §v2.4-proxy-5b-amended chronicle acknowledged the rate-vs-budget confound (principle 17 scope-boundary). Principle 18: scope tags written for each outcome. Principle 19: decision rule commits specific findings.md edits per outcome including a rewrite branch (KINETIC-BUDGET-DRIVEN) and a supersession branch referencing methodology §13. Principle 20: task change (not sampler design change); class balance and learnability confirmed by §v2.3 and §v2.11. Principle 22: exploratory; no new FWER family test. Principle 23: mr=0.03 × sf=0.01 cells are the within-sweep baseline gate; mr=0.005 × gens=9000 budget-decoupling cells are a separate gate against the §v2.4-proxy-5b-amended numbers. Principle 25: all metrics produced directly by analyze_retention.py (including the post-E1 `--include-holdout` flag for R_fit_holdout_999); principle 25 gate explicitly discharged. Principle 26: R₂_decoded, F_slot, and R_fit_holdout_999 are gridded per-arm alongside R_fit_999. Principle 27: metric definitions cited verbatim from METRIC_DEFINITIONS dict (including the new R_fit_holdout_999 entry added 2026-04-18).*
