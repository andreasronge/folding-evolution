# Pre-registration: §v2.5-plasticity-2c — F_AND_test solve-rate capacity-scaling probe at rank-1 plasticity budget ∈ {5, 10, 20, 40}, Arm A sf=0.0

**Status:** READY-TO-LAUNCH v3 (pre-data, post-engineering, post-sweep-YAML, post-codex-v4-PASS-WITH-P2 all P2s discharged) · target commit `06e8732` (engineering + sweep YAML + queue entry landed at `a3a0cc8` + `06e8732`; will be re-pinned to the pre-sweep-launch commit in a follow-up one-line commit) · 2026-04-22

*This prereg is the §2b (methodology principle 2b) follow-up pre-committed by the §v2.5-plasticity-2a-nexp-budget5 chronicle (docs/chem-tape/experiments-v2.md commit `c08888a`) and motivated (not compelled) by the winner-tape inspection ([Plans/_v2-5-plasticity-2a_winner_inspection_2026-04-22.md](_v2-5-plasticity-2a_winner_inspection_2026-04-22.md), commit `00d00e8`, Sections 1+2+3+4 + codex-corrected §4.6).*

*Inspection observations supporting this prereg (descriptive only; all claim-level mechanism interpretations deferred per codex second-round NEEDS-REVISION):*
- *At budget=5 (pooled n=40), F_AND_test_plastic = 14/40 = 0.35; per-winner Baldwin gap mean +0.364; 0/40 solve under frozen eval of plastic-evolved winners.*
- *At frozen control (n=20, plasticity OFF during evolution), F_AND_test = 0/20 (max frozen fit 0.9688); compositional-AND attractor incidence 80% identical to plastic regime; plasticity-active-token count median 3 (vs plastic median 6).*
- *§28a prose-fit / clause-fail on §v2.5-plasticity-2a row 3 (INVERSE-BALDWIN-REPLICATES): mechanism axes (max_gap_at_budget_5 CI [+0.267, +0.346]; δ_std=2.59; seed_maj 37/40) satisfied; F-lift clause (≤0.15) fails with observed 0.35. Row 4 (AMBIGUOUS/PARTIAL) matched cleanly at n=40; this §2c prereg enumerates the observed cell per §2b.*

## Question (one sentence)

**Does F_AND_test solve rate under rank-1 operator-threshold plasticity at Arm A sf=0.0 on `sum_gt_10_AND_max_gt_5` — observed at 14/40 (pooled §v2.5-plasticity-2a + n-exp at plasticity_budget=5, commit `7361631`) — show directional scaling with plasticity budget across {5, 10, 20, 40}, as measured by a paired-seed bootstrap 97.5% CI on per-seed `F_AND_test_plastic` difference between budget=40 and budget=5 cells on the shared seeds 20..39 excluding 0 on the positive side?**

## Hypothesis

**Primary confirmatory statistic (single; authoritative for all row clauses):** `f_and_test_plastic_paired_boot_ci_budget40_vs_budget5` — seed-bootstrap 97.5% CI on the per-seed paired difference `F_AND_test_plastic[budget=40, seed=s] − F_AND_test_plastic[budget=5, seed=s]` for s ∈ {20..39}, n=20 paired differences. 10 000 resamples via `numpy.random.default_rng(seed=42)`. Budget=5 per-seed indicators are extracted from the pooled §v2.5-plasticity-2a + n-exp data at commit `7361631` (see Setup § "Shared-seed extraction" below for the explicit join/filter procedure). H1 rejection criterion: CI excludes 0 on the positive side (CI_lo > 0).

**Secondary point-estimate trend (used only in row-clause conjunctions; NOT a separate confirmatory test):** monotone non-decreasing point-estimate trend across budget ∈ {5, 10, 20, 40} cells. Defined as `F_AND_test_plastic_count[budget=b_{k+1}] ≥ F_AND_test_plastic_count[budget=b_k]` for every adjacent pair; ties (equal counts) are permitted. This is evaluated on point estimates only; no additional α budget.

**H1 (capacity-scaling; routes to narrowing claim):** paired-bootstrap 97.5% CI excludes 0 on the positive side (primary confirmatory statistic rejects null), AND the point-estimate trend across {5, 10, 20, 40} is monotone non-decreasing. Routing: `findings.md#plasticity-narrow-plateau` NARROWS (the scaling observation narrows the FALSIFIED null's scope). Rank-2 (§v2.5-plasticity-1b) and EES (§v2.5-plasticity-2b) deprioritized.

**H0 (no directional evidence; routes to broadening null):** paired-bootstrap CI includes 0 (primary confirmatory statistic fails to reject null), AND the paired point estimate `F_AND_test_plastic_count[40] − F_AND_test_plastic_count[5]` is ≤ 0 (no positive direction). Routing: `findings.md#plasticity-narrow-plateau` BROADENS within the tested regime (rank-1 does not scale with budget on this task at tested budgets ∈ {5, 10, 20, 40}); rank-2 (§v2.5-plasticity-1b) and/or EES (§v2.5-plasticity-2b) queue as the next escalation targets.

**H-partial (directional but CI-inconclusive):** paired-bootstrap CI includes 0 AND the paired point estimate is strictly positive AND the point-estimate trend is monotone non-decreasing. Routing: no `findings.md` change; report effect size + CI. Consider larger-budget follow-up under user judgment; not pre-committed.

**H-non-monotone (grid-miss on point-estimate trend):** the point-estimate trend across {5, 10, 20, 40} is non-monotone (at least one adjacent pair has decrease). Routing: §2b grid-miss; new prereg required to enumerate the observed trend shape before interpreting.

**H-reverse (unexpected direction):** paired-bootstrap 97.5% CI excludes 0 on the NEGATIVE side (budget=40 harms F_AND_test relative to budget=5 at clear statistical significance). Routing: §2b grid-miss on direction; stop and inspect before any routing.

**H-SWAMPED (infrastructure):** `initial_population_canonical_count > 0` on any run OR the frozen-control baseline is independently re-measured (not required by this prereg) and diverges materially from 0/20 OR hash-dedup accidentally re-runs existing budget=5 seeds OR **seed-integrity pre-check fails** (any missing/duplicated/extra seed in either the budget=5 pooled subset or the budget=40 cell per Setup § "Seed-integrity pre-check"). Routing: stop and inspect; no routing until infrastructure check passes.

**Mechanism naming: DEFERRED** (codex-v1 P2-3 correction — "under-capacity," "expressivity ceiling," "rank-1 is not narrow at sufficient capacity" removed from prereg language). No mechanism name is pre-registered in this prereg. Any mechanism-name proposal happens at chronicle time, with a full §16c falsifiability block if named. The corrected framing uses neutral outcome-routing language: narrowing/broadening `findings.md#plasticity-narrow-plateau` based on observed directional scaling, without a mechanism claim.

**Secondary diagnostics (descriptive-only; NO confirmatory-test status; NO α budget; NO routing clauses — explicit §26 demotion):**
- Per-winner Baldwin gap (`test_fitness_plastic − test_fitness_frozen` on same winner genotype) distribution across budgets
- `top1_winner_plasticity_active_count` per winner across budgets
- `top1_winner_overhead` per winner across budgets
- `top1_winner_levenshtein_uncapped` per winner across budgets
- `top1_winner_attractor_category` per winner across budgets
- `top1_winner_canonical_token_set_size` per winner across budgets

**§26 explicit demotion (per codex-v1 P1-4 correction):** the inspection Section 4 observations on these axes are from a single-budget comparison (plastic budget=5 vs frozen budget=0). Single-budget observations cannot support cross-budget scaling predictions on these axes. Per principle 26's escape hatch, the prereg demotes these axes to **pure effect-size-only diagnostics with no outcome-table routing rows**. Chronicle-time: if any secondary axis shows a dramatic pattern not anticipated by Section 4's baselines, the chronicle reports it as a chronicle-time §2b grid-miss discovery and the follow-up prereg enumerates the observed pattern. This is NOT a pre-registered row; it is chronicle-time §26 discipline parallel to §v2.5-plasticity-2a's own row-4 pre-commitment pattern.

**Prediction linkage to prior experiments:**
- §v2.5-plasticity-2a pooled n=40 budget=5 anchor (data commit `7361631`): F_AND_test_plastic = 14/40 = 0.35; seed-bootstrap 97.5% CI on F-fraction computed pre-data on existing data (Status-transition checklist item 2).
- §v2.5-plasticity-2a frozen control n=20 budget=0 (data commit `7361631`): F_AND_test = 0/20.
- §v2.5-plasticity-1a sf=0.01 budget ∈ {1, 2, 3, 5} precedent: INCONCLUSIVE grid-miss at a different regime (seeded canonical sf=0.01 present); `findings.md#plasticity-narrow-plateau` opened as FALSIFIED at size 1 with α=0.05 per §22b commit-time-membership at that chronicle.
- [docs/chem-tape/runtime-plasticity-direction.md](../docs/chem-tape/runtime-plasticity-direction.md) mechanism ladder: rank-1 operator-threshold is the currently-tested rung. Rank-2 memory is the next rung if H0 fires.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2c.yaml` (to be created; see Status-transition checklist below)
- **Arms / conditions:** Arm A only (direct GP). BP_TOPK EXCLUDED per §v2.5-plasticity-1a chronicle's structural R_fit ceiling caveat (same as §v2.5-plasticity-2a). **3 new plastic cells at the capacity axis:**
  - `arm=A, plasticity_enabled=true, plasticity_budget ∈ {10, 20, 40}, seed_fraction=0.0, generations=1500, pop_size=512, mr=0.03, tournament_size=3, elite_count=2, crossover_rate=0.7, plasticity_mechanism=rank1_op_threshold, plasticity_delta=1.0, plasticity_train_fraction=0.75` × 3 budgets × 20 seeds = **60 new runs**.
  - **Budget=5 cell: REUSES pooled §v2.5-plasticity-2a + n-exp n=40 data** at commit `7361631` (no re-run; the 40 per-winner artifacts are on disk in `experiments/output/2026-04-21/v2_5_plasticity_2a/` and `experiments/output/2026-04-22/v2_5_plasticity_2a_nexp_budget5/`).
  - **Frozen control cell: REUSES §v2.5-plasticity-2a n=20 frozen control at seeds 20..39** (`plasticity_enabled=false`, F_AND_test = 0/20; data commit `7361631`). NOT re-expanded. If H-SWAMPED fires, infrastructure-inspection required before routing.
- **Seeds:** **seeds 20..39** on the 3 new budget cells. Same seed block as §v2.5-plasticity-2a's primary cell — the paired-seed structure is the internal-control contrast (principle 1). The n-exp seeds 40..59 are NOT re-used at new budgets here.
- **Fixed params:** pop=512, gens=1500, mr=0.03, crossover_rate=0.7, tournament_size=3, elite_count=2, tape_length=32, n_examples=64, alphabet=v2_probe, task=sum_gt_10_AND_max_gt_5, disable_early_termination=true, dump_final_population=true, backend=mlx, plasticity_mechanism=rank1_op_threshold, plasticity_delta=1.0, plasticity_train_fraction=0.75, holdout_size=256, seed_tapes="" (no canonical seeding at sf=0.0). All params byte-identical to §v2.5-plasticity-2a's primary cell except `plasticity_budget`.

**Shared-seed extraction (codex-v1 P2-1 correction — explicit procedure):** the primary confirmatory statistic compares budget=40 (20 new runs at seeds 20..39) vs budget=5 on the same 20 seeds. The budget=5 per-seed F_AND_test_plastic indicators are extracted by:

1. Load `experiments/output/2026-04-21/v2_5_plasticity_2a/plasticity.csv` (post-§2a data).
2. Filter to rows where `plasticity_enabled == 'True' AND plasticity_budget == '5' AND arm == 'A'`.
3. Retain only rows with `seed ∈ {20, 21, ..., 39}` (the §2a cell's seeds 20..39; excludes the n-exp seeds 40..59).
4. Compute per-seed binary indicator `best_fitness_test_plastic >= 1.0 - 1e-9`.
5. Join to budget=40 per-seed indicators (new runs at seeds 20..39) on the `seed` column; paired n=20 difference vector.

**Seed-integrity pre-check (codex-v2 P2-1 correction — missing/duplicated/failed seed handling):** before forming the paired n=20 vector, verify that **exactly 20 seeds** are present in the filter-retained budget=5 subset (seeds 20..39) AND **exactly 20 seeds** are present in the budget=40 cell AND **every seed ∈ {20..39} appears exactly once** in each subset. Any deviation — missing seed (fewer than 20), duplicated seed (same seed twice), or extra seed (seed outside {20..39}) in either cell — **routes the chronicle verdict to Row 6 (SWAMPED)**. This is an infrastructure failure indicating a sweep-output integrity issue; inspection is required before any routing. The pre-check is implemented in the paired-bootstrap routine (Status-transition checklist item 1(h)) with explicit assertion and an error message naming which cell and which seed anomaly triggered the SWAMPED routing.

The pooled n=40 data from §2a + n-exp is ALSO used for reporting the budget=5 cell's per-cell seed-bootstrap 97.5% CI (Status-transition checklist item 2 — pre-data baseline). The paired-bootstrap confirmatory test uses ONLY the seeds 20..39 subset (n=20 matched pairs).

- **Est. compute:** per-run wall scales roughly linearly with plasticity budget. Projected per-run wall: budget=10 ≈ 12 min, budget=20 ≈ 18 min, budget=40 ≈ 30 min. Parallel wall at 10 workers: budget=10 cell ≈ 24 min, budget=20 cell ≈ 36 min, budget=40 cell ≈ 60 min. **Total projected wall: ~2 hours for 60 new runs.** Queue timeout 10800s (3h, 1.5× headroom). Actual per-run cost requires a pilot seed before the sweep launches; see Status-transition checklist.
- **Related experiments:** §v2.5-plasticity-2a primary (commit `4d331ad`); §v2.5-plasticity-2a-nexp-budget5 (commit `9ad15ea`); §v2.5-plasticity-2a chronicle (commit `2fedf7d`); §v2.5-plasticity-2a-nexp chronicle (commit `c08888a`); inspection scratch (commit `00d00e8`); §v2.5-plasticity-1a at commit `4ceb22b` (sf=0.01 regime); diagnosis doc `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md`; [docs/chem-tape/runtime-plasticity-direction.md](../docs/chem-tape/runtime-plasticity-direction.md) for mechanism-ladder context.

**Principle 17a audit:** varies ONE nominal config field — `plasticity_budget`. Derived process variables co-moving with budget: (a) max `|δ_final|` per tape = budget × δ = budget; (b) adaptation-step count per evaluation = budget; (c) per-evaluation plasticity VM work = O(budget). All three directly derive from budget. Budget IS the capacity axis. Principle 17b: tested integer budget values ∈ {5, 10, 20, 40}; scope qualifiers must use this verbatim tested-set, not continuous-range phrasing.

**Principle 20 audit:** sampler unchanged from §2a; not triggered.

**Principle 23 audit:** all 4 cell params byte-identical to §2a except `plasticity_budget`. Reusing §2a's budget=5 data (n=40 pooled) requires that sweep YAML's hash-dedup NOT re-run existing seeds 20..39 budget=5 (hash includes budget, so different budget configs produce different hashes — no dedup concern; Status-transition checklist item 3 verifies).

## Baseline measurement (required — principle 6 + 25)

**Baseline quantity 1 — F_AND_test_plastic seed-bootstrap 97.5% CI at budget=5 (pooled n=40 from §2a + n-exp):**
- Measurement: seed-bootstrap 97.5% CI on per-cell F_AND_test_plastic fraction using 40 per-seed binary indicators, 10 000 resamples via `numpy.random.default_rng(seed=42)`. Matches `bootstrap_ci_spec`.
- **Value (measured pre-data at commit `38fa033`+1):** point estimate = **14/40 = 0.3500**; 97.5% CI = **[0.2000, 0.5250]** (quantiles [1.25%, 98.75%]). Per-seed breakdown: §2a seeds 20..39 contribute 7/20 solvers; n-exp seeds 40..59 contribute 7/20 solvers; pooled 14/40.
- Rationale: direct baseline for the paired-bootstrap confirmatory test. Principle 6 satisfied — threshold is data-derived, not imported. **Note:** the paired-bootstrap confirmatory test on shared seeds 20..39 uses only the n=20 §2a subset as the budget=5 reference per Setup § "Shared-seed extraction" step 3 (n-exp seeds 40..59 are NOT in the shared-seed set); this n=40 pooled baseline CI is reported as chronicle-time context, not as the confirmatory statistic's reference.

**Baseline quantity 2 — F_AND_test_frozen at frozen-control cell (n=20, seeds 20..39):**
- Existing §2a frozen-control data (commit `7361631`); F_AND_test = 0/20. Serves as infrastructure anchor for the row-6 SWAMPED trigger.

**Baseline quantity 3 — observational context from inspection Section 4 (NOT pre-registered as baseline for routing clauses):**
- Frozen-control (n=20): median active-view length = 27.5, median overhead = 15.5, median plasticity-active-token count = 3, compositional_AND incidence 80%.
- Plastic-evolved budget=5 (n=40): median active-view length = 28, median overhead = 16, median plasticity-active-token count = 6, compositional_AND incidence 80%, per-winner Baldwin gap mean +0.364.
- These are reported for chronicle-time context only; NOT pre-committed as routing thresholds (per codex-v1 P1-4 correction — secondary axes are fully demoted).

**Metric definitions (principle 27 — verbatim):** existing metrics cited from `experiments/chem_tape/analyze_plasticity.py:METRIC_DEFINITIONS` verbatim. New metrics pre-committed verbatim in the METRIC_DEFINITIONS extensions section below.

**Measurement-infrastructure gate (principle 25):** the primary confirmatory statistic and secondary diagnostics require engineering extensions:

1. **Primary confirmatory CI (`f_and_test_plastic_paired_boot_ci_budget40_vs_budget5`):** new cell-level routine on per-run CSV data. Engineering estimate: ~30 min. Status: **pending infra extension** (Status-transition checklist item 1).
2. **Primary per-cell CI (`f_and_test_plastic_seed_boot_ci`):** per-cell seed-bootstrap on F-fraction (descriptive; reports endpoint CIs). Engineering: ~15 min. Pending.
3. **6 new per-run metrics** (all §26-demoted diagnostics): `top1_winner_overhead`, `top1_winner_plasticity_active_count`, `top1_winner_levenshtein_uncapped` (replaces deprecated cap=4 `top1_winner_hamming`), `top1_winner_attractor_category`, `top1_winner_canonical_token_set_size`, `top1_winner_baldwin_gap`. Engineering: ~1.5h total. Pending.
4. **Glue: paired-subset extraction routine, pytest coverage, sweep-YAML, queue entry, hash-dedup pytest, pilot timing, pre-data baseline CI precompute.** Codex-v1 P2-4 correction: engineering estimate bumped from ~2h to **~4-6h total** to include all glue.

Status-transition checklist item 1 covers all engineering; sweep does not launch until items 1-7 pass.

**Grouping-script attribution (principle 25 clarification):** the per-cell seed-bootstrap CI routine lives in `analyze_plasticity.py:summarize` (existing grouping by `(arm, plasticity_enabled, plasticity_budget, seed_fraction)` already matches this prereg's per-cell grid). The paired-bootstrap routine lives in a NEW function `paired_bootstrap_budget40_vs_budget5` (Status-transition checklist item 1(h)) that takes the per-run CSV + budget labels as inputs and outputs a CI tuple. No new grouping wrapper script needed.

## Internal-control check (required — principle 1)

- **Tightest internal contrast:** paired plastic at budget=40 vs plastic at budget=5 on shared seeds 20..39 — holds task, sampler, seeds, pop, gens, mr, tournament_size, elite_count, mechanism, δ, sf, alphabet, train/test split ALL fixed; only `plasticity_budget` varies. This is the primary confirmatory test.
- **Are you running it here?** Yes — budget=40 at seeds 20..39 is the primary new cell; shared-seed paired-bootstrap against budget=5 is the confirmatory test.

## Pre-registered outcomes (required — principle 2 + 2b + 26) — v2 rewrite per codex-v1 P1-1 and P1-2

**Axis structure (codex-v1 P1-4 fully corrected):** the primary routing axis is 1D — the paired-bootstrap 97.5% CI on `F40 − F5` (shared seeds 20..39) combined with the point-estimate trend across budgets. Secondary axes are explicitly §26-demoted (diagnostic-only, no outcome-table rows; chronicle-time discipline only).

**Row precedence (codex-v1 P1-1 correction):** rows are evaluated in precedence order; the FIRST matching row fires. This resolves tie-ambiguity and multi-row collisions.

**Precedence order:** Row 6 (SWAMPED) → Row 4 (NON-MONOTONE) → Row 5 (REVERSE) → Row 1 (PASS) → Row 2 (PARTIAL) → Row 3 (SATURATION) → Row 7 (CATCHALL).

**Outcome grid:**

| # | outcome | Primary-statistic conjunction (paired CI + trend) | Precedence |
|---|---------|---------------------------------------------------|------------|
| 6 | **SWAMPED** (infrastructure) | `initial_population_canonical_count > 0` on any run, OR hash-dedup accidentally re-runs existing budget=5 seeds, OR seed-integrity pre-check fails (missing/duplicated/extra seed in either cell per Setup § "Seed-integrity pre-check"), OR any other infrastructure-fidelity failure | 1st (highest) |
| 4 | **INCONCLUSIVE — NON-MONOTONE** (grid-miss on trend; §2b) | Point-estimate trend across {5, 10, 20, 40} is non-monotone (at least one adjacent pair has `F_AND_test_count[b_{k+1}] < F_AND_test_count[b_k]`) | 2nd |
| 5 | **INCONCLUSIVE — REVERSE** (grid-miss on direction; §2b) | Paired-bootstrap 97.5% CI on `F40 − F5` shared seeds 20..39 EXCLUDES 0 on the NEGATIVE side | 3rd |
| 1 | **PASS-CAPACITY-SCALING** (H1) | Paired CI excludes 0 on POSITIVE side AND point-estimate trend is monotone non-decreasing | 4th |
| 2 | **PARTIAL** (H-partial) | Paired CI includes 0 AND point-estimate trend is monotone non-decreasing AND paired point estimate `F̂40 − F̂5 > 0` | 5th |
| 3 | **INCONCLUSIVE — SATURATION** (H0) | Paired CI includes 0 AND paired point estimate `F̂40 − F̂5 ≤ 0` (including tie `F̂40 = F̂5`) | 6th |
| 7 | **INCONCLUSIVE — catchall** (§2 follow-up) | Any pattern not matched by rows 1-6 above (expected very rare under the well-defined paired-bootstrap + trend predicates) | 7th (lowest) |

**Row-clause fidelity (principle 28a — v2 explicit):** every row fires only when its full conjunction is satisfied AND no higher-precedence row fires first. Tie-breaking on paired point estimate: `F̂40 = F̂5` routes to Row 3 (SATURATION, not Row 2 PARTIAL), since Row 2 requires strict `F̂40 − F̂5 > 0`. Tie-breaking on point-estimate trend: `F_AND_test_count[b_{k+1}] == F_AND_test_count[b_k]` counts as non-decreasing (satisfies monotone clause of rows 1 and 2); strict decrease triggers Row 4.

**Threshold justifications (principle 6 — all baseline-relative):**
- **Paired-bootstrap CI exclusion criterion (rows 1, 5):** derived from the bootstrap distribution on the same 20 paired seeds; no imported threshold.
- **Monotone non-decreasing trend (rows 1, 2, 4):** anchored to the 4 measured cell point estimates themselves; no imported trend magnitude.
- **Paired point-estimate sign (rows 2, 3):** direct data comparison; no imported threshold.
- **Row-6 SWAMPED triggers:** `initial_population_canonical_count > 0` is an infrastructure-fidelity invariant (should always be 0 at sf=0.0; any violation indicates a bug). Hash-dedup mismatch: verified by pytest (checklist item 3).

## Degenerate-success guard (required — principle 4 + principle 28b)

Five guards inherited from §v2.5-plasticity-2a with budget-scaling adaptations. Each individually enumerated.

1. **Universal-adapter artefact.** Single-criterion: `top1_winner_levenshtein_uncapped` at any budget ≤ 4 for ≥ 15/20 seeds. If triggered, top-1 winners converge to near-canonical structure across budgets — a pattern not anticipated by Section 4's observation of distant-tail winners across all 40 inspected. Chronicle-time: flag as §26 secondary-axis grid-miss (no pre-registered row fires from this guard — per codex P1-4 secondary-axis demotion; the chronicle-time discipline handles it).
2. **Train-test leakage.** Single-criterion: `F_AND_test_plastic_count − F_AND_train_plastic_count` near zero at any budget AND `F_AND_test_plastic_count ≥ 15/20` (high solve rate with indistinguishable train/test). Chronicle-time inspection.
3. **Threshold-saturation (population + top-1 winner split).** Conjunction per §28b: per-cell `|δ_final| ≥ budget` fraction on population AND on top-1 winner, BOTH reported per cell. Physical-ceiling violation (`|δ_final| > budget`) indicates a bug; discharge in chronicle.
4. **GT-bypass artefact.** Single-criterion: `GT_bypass_fraction ≥ 0.50` at any cell. Chronicle-time.
5. **δ-convergence artefact.** Single-criterion: `delta_final_std_mean ≤ 0.5` at any budget (δ convergence across genotypes). Chronicle-time; if triggered, §26 secondary-axis grid-miss flag at chronicle time.

**Infrastructure-fidelity check:** `history.npz:initial_population_canonical_count == 0` across every run (row-6 SWAMPED trigger if violated). Covered by existing pytest `tests/test_chem_tape_seeded_init.py`.

**Conjunction-guard check (principle 28b):** guard 3 is the multi-mode case; its population+top-1 conjunction covers both winner-level and population-level saturation. No single-criterion guard misses a known multi-mode failure here.

## Statistical test (principle 22 + 22a + 22b) — v2 rewrite per codex-v1 P1-2 + P1-3

- **Primary confirmatory test (authoritative for all row clauses):** paired-seed bootstrap 97.5% CI on per-seed difference `F_AND_test_plastic[budget=40, seed=s] − F_AND_test_plastic[budget=5, seed=s]` for s ∈ {20..39}, n=20 paired differences. 10 000 resamples, `numpy.random.default_rng(seed=42)`, 97.5% quantile CI on paired-difference mean. H1 rejection criterion: CI_lo > 0 (excludes 0 positive). H-reverse trigger: CI_hi < 0 (excludes 0 negative).
- **Secondary (NOT confirmatory, effect-size only, NO α budget):** per-cell seed-bootstrap 97.5% CI on F_AND_test_plastic fraction at each budget cell (for trend visualization); per-cell descriptive statistics on §26-demoted secondary axes.
- **Classification:** **confirmatory.** Gates the narrowing/broadening decision for `findings.md#plasticity-narrow-plateau`.
- **Family (codex-v1 P1-3 correction — joins existing family, does NOT open new):** **`plasticity-narrow-plateau`** (the same family opened by §v2.5-plasticity-1a at size 1, FALSIFIED; per §22b commit-time-membership, the family member count does not decrease on null — it stays at size 1 after §1a's closure). This prereg's confirmatory test is a second member of the same claim-family (the test routes to narrowing/broadening the same findings-layer claim), growing the family to **size 2**. **Bonferroni-corrected family α = 0.05 / 2 = 0.025.** Operationalization (codex-v2 P1-1 correction): the paired-bootstrap CI is pre-registered at **97.5% two-sided** (quantiles [1.25%, 98.75%]) to match the corrected family α exactly — a two-sided test at α = 0.025 with either-side rejection (H1 PASS on CI_lo > 0; H-reverse on CI_hi < 0) consumes exactly 0.025 total family α. No shorter-CI phrasing appears in the authoritative sections (Hypothesis / Outcome grid / Statistical test / METRIC_DEFINITIONS); 97.5% is the authoritative CI for all row clauses and for the primary confirmatory statistic. Historical references to "95% CI" appear in the Amendment history block only, where they describe the superseded v2 state.
- **Per-sweep test counting (principle 22a):** this prereg produces **one** confirmatory test (the paired-bootstrap CI on budget=40 vs budget=5). Budget=10 and budget=20 cells' F_AND_test values enter the point-estimate trend predicate used in row-clause conjunctions — these are NOT separate confirmatory tests per 22a (they inform trend classification but do not each open an α-budget member).
- **Commit-time family membership (principle 22b):** the confirmatory test counts in the family regardless of rejection outcome. If H0 fires (overlapping CI), the null is recorded under §24 but the family member count remains at 2 and the corrected α stays at 0.025 for any future test.

## Diagnostics to log (beyond primary confirmatory axis)

Per prereg §Diagnostics-to-log discipline (inherited from §v2.5-plasticity-2a):

- Per-seed × per-cell F_AND_train, F_AND_test (plastic eval for plastic cells; frozen eval for reused frozen control).
- R_fit_frozen_999, R_fit_plastic_999 per cell.
- Per-individual test_fitness_frozen, test_fitness_plastic, train_fitness_frozen, train_fitness_plastic, delta_final, has_gt, genotypes → `final_population.npz`.
- Per-cell GT_bypass_fraction.
- Per-cell Baldwin_gap by Hamming bin (h=0..≥4); Baldwin_slope (nan expected at sf=0.0).
- Per-cell std(delta_final) stratified by Hamming bin.
- Per-cell seed-bootstrap 97.5% CI on F_AND_test_plastic fraction (descriptive; secondary).
- **Per-run `top1_winner_baldwin_gap`, `top1_winner_plasticity_active_count`, `top1_winner_overhead`, `top1_winner_levenshtein_uncapped`, `top1_winner_attractor_category`, `top1_winner_canonical_token_set_size`** — all §26-demoted secondary axes; reported per-run per-cell.
- Per-cell paired R_fit_plastic_999 − R_fit_frozen_999 on shared seeds (R_fit_delta_paired_sf0; inherited from §2a).
- Per-cell `|δ_final| ≥ budget` fraction (pop-level + top-1 winner split).
- Per-cell best-of-run hex for top-1 winner per seed.
- Per-seed initial_population_canonical_count in gen-0.

## Scope tag (required — principle 17 + 17b + 18)

**If H1 (row 1 PASS-CAPACITY-SCALING) fires:** `findings.md#plasticity-narrow-plateau` NARROWS with scope:
`within-task-family · per-cell n=20 at budgets ∈ {10, 20, 40} + pooled n=40 at budget=5 · pop=512 gens=1500 mr=0.03 tournament_size=3 elite_count=2 · sum_gt_10_AND_max_gt_5 natural sampler with 75/25 train/test split · rank1_op_threshold mechanism · δ=1.0 · tested integer budgets ∈ {5, 10, 20, 40} · sf=0.0 · Arm A only · seeds 20..39 at new budgets`.

**If H0 (row 3 SATURATION) fires:** `findings.md#plasticity-narrow-plateau` BROADENS with the same scope tag plus explicit "at tested budgets ∈ {5, 10, 20, 40}" qualifier per principle 17b (no extrapolation beyond tested set).

**Explicitly NOT-broadening in any outcome:** other tasks (P-3 from §1a open for cross-task); BP_TOPK arm (EXCLUDED); rank-2 or deeper mechanisms (untested); other selection regimes; other δ values; other train/test splits; budgets beyond 40; seeds beyond 20..39 at new budgets.

## Decision rule

- **Row 1 (PASS-CAPACITY-SCALING) →** narrow `findings.md#plasticity-narrow-plateau`; queue a chronicle-time mechanism-naming round per §16c (naming requires ≥ 3 falsifiable predictions); deprioritize rank-2 (§v2.5-plasticity-1b) and EES (§v2.5-plasticity-2b). Consider budget ≥ 80 follow-up under user judgment (not pre-committed).
- **Row 2 (PARTIAL) →** no findings change; report effect-size + paired-bootstrap CI. Budget ≥ 80 follow-up under user judgment; not pre-committed.
- **Row 3 (SATURATION) →** broaden `findings.md#plasticity-narrow-plateau` (rank-1 does not scale at tested budgets); queue rank-2 (§v2.5-plasticity-1b) ahead of EES (§v2.5-plasticity-2b) as next escalation.
- **Row 4 (NON-MONOTONE grid-miss) →** §2b catchall; new prereg required before interpretation. Rank-2, EES both deferred.
- **Row 5 (REVERSE grid-miss) →** §2b catchall; stop and inspect before routing. Harm-from-budget-scaling is an unexpected direction; investigate for infrastructure issues, data-distribution changes, or novel mechanism.
- **Row 6 (SWAMPED) →** stop and inspect; no routing until infrastructure check passes.
- **Row 7 (CATCHALL) →** §2 follow-up; note outcome table was incomplete; update for future prereg.

## Audit trail

- **Principle 1:** paired-seed internal contrast (budget=40 vs budget=5 on seeds 20..39) is in-sweep; tightest within-family contrast.
- **Principle 2 + 2b + 26:** 7 rows enumerated with explicit precedence order (codex-v1 P1-1 correction). Primary axis is 1D on paired-bootstrap CI + point-estimate trend. Secondary axes fully §26-demoted per codex-v1 P1-4 correction; no routing clauses on them; chronicle-time §26 discipline only. Partial (row 2) and catchall (row 7) both present per principle 2.
- **Principle 4 + 28b:** 5 guards (guard 7 infrastructure moved to row 6 SWAMPED). Guard 3 multi-mode via conjunction.
- **Principle 6:** all thresholds baseline-relative (paired-bootstrap on same dataset; point-estimate trend on 4 measured cells). No imported numeric thresholds.
- **Principle 16c:** mechanism naming DEFERRED; §16c block empty. Codex-v1 P2-3 correction: mechanism-heavy language ("under-capacity," "expressivity ceiling," "rank-1 is not narrow at sufficient capacity") removed from prereg body.
- **Principle 17a + 17b:** budget axis is single-variable with 3 directly-derived co-moving process variables. Tested integer budgets ∈ {5, 10, 20, 40} per 17b; scope qualifiers use verbatim tested-set.
- **Principle 20:** sampler unchanged; not triggered.
- **Principle 22 + 22a + 22b:** confirmatory, **1 test** (paired-bootstrap on seeds 20..39). Joins existing `plasticity-narrow-plateau` family (codex-v1 P1-3 correction), growing from size 1 (§1a null) to **size 2**; corrected α = 0.05/2 = **0.025**. Commit-time membership per 22b.
- **Principle 23:** param-identity to §2a except budget axis. Frozen control reuses §2a. Hash-dedup verified at checklist item 3.
- **Principle 25 + 27:** primary confirmatory statistic + 6 §26-demoted secondary metrics pre-committed verbatim in METRIC_DEFINITIONS extensions. Engineering estimate **~4-6h** (codex-v1 P2-4 correction).
- **Principle 26:** secondary axes EXPLICITLY demoted per escape hatch; cite-the-reason documented in Hypothesis block (single-budget inspection cannot support cross-budget scaling predictions on these axes). No outcome-grid rows on secondary axes; chronicle-time discipline handles dramatic patterns via §2b grid-miss flag.
- **Principle 28a/b/c:** row clauses are explicit conjunctions with precedence (28a); guard 3 multi-mode (28b); status-line inline qualifier at chronicle time (28c).
- **Principle 29:** this prereg does NOT follow from a diagnosis doc — §2a-nexp was row-4 AMBIGUOUS (pre-registered row), not FAIL/grid-miss. §29 not invoked.

## METRIC_DEFINITIONS extensions (principle 27 — verbatim)

The following entries will be added verbatim to `experiments/chem_tape/analyze_plasticity.py:METRIC_DEFINITIONS` by Status-transition checklist item 1 before sweep launches:

```python
"top1_winner_overhead": (
    "Per-run integer: active-view length of the top-1 winner's tape minus 12 "
    "(canonical active-view length for sum_gt_10_AND_max_gt_5). Negative if "
    "winner is shorter than canonical. Winner selection: argmax over "
    "test_fitness_plastic, tiebroken by train_fitness_plastic, then by smallest "
    "genotype index (matches top1_winner_hamming selection verbatim). Active "
    "view = tokens with id in {1..19} (v2_probe; excludes NOP=0 and separators "
    "20/21). Added in §v2.5-plasticity-2c; §26-demoted diagnostic, no routing."
),
"top1_winner_plasticity_active_count": (
    "Per-run integer: count of plasticity-active operators {GT (8), IF_GT (17), "
    "THRESHOLD_SLOT (19)} in the top-1 winner's active-view tokens. Conservative "
    "plasticity-active set under rank1_op_threshold. Canonical has "
    "GT*2+IF_GT*1+THRESHOLD_SLOT*0 = 3. Added in §v2.5-plasticity-2c; §26-"
    "demoted diagnostic, no routing."
),
"top1_winner_levenshtein_uncapped": (
    "Per-run integer: full active-view Levenshtein distance (uncapped) from the "
    "top-1 winner's active-view to the canonical sum_gt_10_AND_max_gt_5 active-"
    "view. Replaces the deprecated top1_winner_hamming with cap=4 (which "
    "returned cap+1=5 sentinel on all §v2.5-plasticity-2a + n-exp winners, "
    "destroying distance information). Preserves full distance structure "
    "(observed range 17-26 on §2a n=40). Winner selection identical to "
    "top1_winner_overhead. Added in §v2.5-plasticity-2c; §26-demoted diagnostic."
),
"top1_winner_attractor_category": (
    "Per-run string in {'compositional_AND', 'max>5-only', 'sum>10-only', "
    "'other'}: heuristic classification of the top-1 winner's active-view "
    "structure. compositional_AND: has >=1 of {REDUCE_MAX, CONST_5} AND >=1 of "
    "{SUM} AND >=1 of {GT, IF_GT}. max>5-only: has {REDUCE_MAX, CONST_5, GT} "
    "but no SUM. sum>10-only: has {SUM, GT or IF_GT} but no REDUCE_MAX and no "
    "CONST_5. other: doesn't fit above. Canonical classifies as compositional_"
    "AND. Added in §v2.5-plasticity-2c; §26-demoted diagnostic."
),
"top1_winner_canonical_token_set_size": (
    "Per-run integer in {0..8}: count of canonical active-view operators "
    "{CONST_0, INPUT, REDUCE_MAX, CONST_5, GT, SUM, ADD, IF_GT} present (set "
    "intersection) in top-1 winner's active-view. Higher = more canonical "
    "operators present; does NOT imply canonical structure. Added in §v2.5-"
    "plasticity-2c; §26-demoted diagnostic."
),
"top1_winner_baldwin_gap": (
    "Per-run float: test_fitness_plastic[winner_idx] minus test_fitness_"
    "frozen[winner_idx] on SAME top-1 winner genotype. Positive = plasticity "
    "helps this winner's test-set fitness; negative = plasticity hurts. "
    "Measured on 16 held-out test examples. §2a pooled n=40 budget=5: mean "
    "+0.364, range [-0.125, +0.688]. Added in §v2.5-plasticity-2c; §26-demoted "
    "diagnostic."
),
"f_and_test_plastic_seed_boot_ci": (
    "Per-cell seed-bootstrap 97.5% CI on F_AND_test_plastic fraction. 10 000 "
    "resamples with replacement over 20 per-seed binary indicators (best_"
    "fitness_test_plastic >= 1.0) via numpy.random.default_rng(seed=42); CI = "
    "[1.25%, 98.75%] empirical quantiles of resampled fractions. Matches "
    "bootstrap_ci_spec. For budget=5 pooled cell uses n=40 indicators. "
    "Descriptive (not confirmatory). Added in §v2.5-plasticity-2c."
),
"f_and_test_plastic_paired_boot_ci_budget40_vs_budget5": (
    "Paired-seed bootstrap 97.5% CI on per-seed difference F_AND_test_plastic"
    "[budget=40, seed=s] minus F_AND_test_plastic[budget=5, seed=s] for s in "
    "{20..39}, n=20 paired differences. 10 000 resamples via numpy.random."
    "default_rng(seed=42); CI = [1.25%, 98.75%] empirical quantiles of resampled "
    "paired-difference means. Budget=5 per-seed indicators extracted from "
    "pooled §v2.5-plasticity-2a data (not n-exp) via seed filter. "
    "**Primary confirmatory test for §v2.5-plasticity-2c family 'plasticity-"
    "narrow-plateau' (family size now 2, corrected alpha = 0.025).** H1 "
    "rejection: CI_lo > 0. H-reverse trigger: CI_hi < 0. Added in §v2.5-"
    "plasticity-2c."
),
```

8 new entries total (6 per-run diagnostics + 2 cell-level CIs).

## Status-transition checklist (must discharge before sweep launch)

Engineering total estimate **~4-6h** (codex-v1 P2-4 correction — includes all glue).

1. **Engineering: extend `analyze_plasticity.py` with 6 new per-run metrics + 2 new cell-level CI routines.** Each sub-item has pytest coverage.
   - (a) `top1_winner_overhead` routine (~15 min)
   - (b) `top1_winner_plasticity_active_count` routine (~10 min)
   - (c) `top1_winner_levenshtein_uncapped` routine + retire cap=4 `top1_winner_hamming` metric (~15 min)
   - (d) `top1_winner_attractor_category` routine (~20 min)
   - (e) `top1_winner_canonical_token_set_size` routine (~10 min)
   - (f) `top1_winner_baldwin_gap` routine (~10 min)
   - (g) `f_and_test_plastic_seed_boot_ci` cell-level CI routine (~15 min)
   - (h) `f_and_test_plastic_paired_boot_ci_budget40_vs_budget5` paired-CI routine with explicit seeds-20..39 extraction from pooled §2a data (~30 min)
   - (i) Glue: per-run + per-cell schema pytest, paired-extraction pytest, CI-reproducibility pytest (~1h)
   - (j) Re-run `analyze_plasticity.py` on existing §2a + n-exp data to validate new columns (~15 min)
   - Sub-total: ~3.5-4h.
2. **Pre-data: compute baseline CIs on pooled n=40 budget=5 F_AND_test.** Run new CI routines on existing data; report point estimate (14/40 = 0.35) and 97.5% CI. Direct comparator for H1/H0/H-partial. (~15 min.)
3. **Pytest: hash-dedup discipline.** Verify dry-run invocation of `sweep.py` on the new sweep YAML does NOT re-compute existing budget=5 cells (different budget → different config hash; dedup should skip nothing inappropriately). Pure sanity check given hash is budget-sensitive. (~15 min.)
4. **Sweep YAML creation.** `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2c.yaml` with 3 new cells × 20 seeds = 60 runs. Params byte-identical to §2a except `plasticity_budget ∈ {10, 20, 40}`. (~30 min.)
5. **Queue.yaml entry.** Timeout 10800s (3h). Reference this prereg path verbatim. (~10 min.)
6. **Pilot timing.** Run 1 seed at budget=40 (~30 min wall projected) to calibrate compute estimate before committing sweep YAML params. (~30-45 min.)
7. **Codex adversarial review of this prereg v2 (mandatory per research-rigor prereg-mode hard gate).** Address every P1; acknowledge/defer P2. Document in Amendment history below. (~15-30 min of review + fix time.)
8. **Target commit SHA pin.** After items 1-7 land, re-pin target commit in this prereg's status line.

Total engineering + review: **~4-6h** depending on codex-v2 finding count.

## Amendment history

**2026-04-22 (v3 — READY-TO-LAUNCH; post-engineering, post-sweep-YAML, post-codex-v4-PASS-WITH-P2 doc-state P2 discharged in-place).**

Codex-v4 final review (pre-sweep-launch): VERDICT **PASS-WITH-P2** (0 P1 + 1 P2). Codex-v4 P2: status line mismatch — said "DRAFT v3, target commit TBD, pre-engineering, pre-sweep-YAML" despite engineering (a3a0cc8) and sweep YAML + queue entry (06e8732) having landed. Discharged in-place: status line updated to READY-TO-LAUNCH + target commit pinned to 06e8732. Codex-v4 confirmed: no residual 95% CI outside amendment history; no mechanism-name language; row precedence + tie-breaking internally consistent; family α=0.025 operationalized with 97.5% CI; seed-integrity pre-check consistent across 4 locations; baseline comparator 14/40=0.35 / 97.5% CI [0.20, 0.525] baked in as pre-data context.

**2026-04-22 (v3 — post-codex-v2-FAIL + codex-v3-PASS-WITH-P2 both P2s discharged in-place; engineering pending at commit).**

Codex-v3 review verdict: **PASS-WITH-P2** (no P1; 2 P2). Both P2s discharged in-place on this v3 working text:
- Codex-v3 P2-1 (residual "95%" language in Amendment history creating self-contradiction with the claim "No 95% phrasing remains"): the corresponding Statistical-test-section sentence was clarified to scope the "no shorter-CI phrasing" claim to the authoritative sections only, with explicit acknowledgement that the Amendment history's historical references to "95% CI" describe the superseded v2 state.
- Codex-v3 P2-2 (H-SWAMPED in Hypothesis block not updated to include seed-integrity failure case): added seed-integrity-pre-check failure to the H-SWAMPED trigger list for consistency with Row 6 SWAMPED and the Setup block's seed-integrity pre-check procedure.

 v2 was reviewed by codex (research-rigor prereg-mode hard-gate item 7, second round) and returned **FAIL** with **1 P1 + 1 P2**. v3 applies the remaining corrections:

- **P1-1 (FWER correction not operationalized in decision rule):** v2 declared family α = 0.025 but every row clause still used a CI width inconsistent with the corrected α. v3 changes ALL CI references to **97.5% two-sided CI** (quantiles [1.25%, 98.75%]). At 97.5% two-sided with either-side rejection (CI_lo > 0 OR CI_hi < 0), the total α consumed equals the Bonferroni-corrected family α = 0.025 exactly. No shorter-CI phrasing remains in the authoritative prereg sections (Hypothesis, Outcome grid, Statistical test, METRIC_DEFINITIONS); the only residual mentions of shorter-CI language are in THIS amendment-history block, where they appear as references to the superseded v2 state.
- **P2-1 (missing/duplicated/failed seed handling unspecified):** v3 adds an explicit **Seed-integrity pre-check** in the Setup block: before forming the paired n=20 vector, verify exactly 20 seeds present in each subset with every seed ∈ {20..39} appearing exactly once. Any deviation → Row 6 SWAMPED. Row 6's SWAMPED triggers are updated accordingly.

v2 preserved in git commit history before this amendment; v3 is the current working state.

**2026-04-22 (v2 — pre-data, pre-engineering, pre-sweep-YAML, post-codex-v1-FAIL).** v1 draft was submitted to codex adversarial review (research-rigor prereg-mode hard-gate item 7) and returned **FAIL** with **4 P1 + 4 P2** findings. v2 applies all corrections:

- **P1-1 (row tie/precedence ambiguity):** v2 adds explicit precedence order (Row 6 → 4 → 5 → 1 → 2 → 3 → 7) and resolves ties: `F̂40 = F̂5` routes to Row 3 (SATURATION); equal-point-estimate trend counts as non-decreasing.
- **P1-2 (primary confirmatory statistic mismatch):** v2 picks the **paired-bootstrap CI** as the SINGLE authoritative primary statistic. All row clauses are rewritten in paired-bootstrap + point-estimate-trend language. Independent-endpoint-CI phrasing removed.
- **P1-3 (wrong FWER family):** v2 **joins the existing `plasticity-narrow-plateau` family** (opened by §v2.5-plasticity-1a at size 1, FALSIFIED). Family grows to size 2 at this prereg's commit. Corrected α = 0.05/2 = **0.025**.
- **P1-4 (§26 demotion not discharged):** v2 **fully demotes secondary axes with NO outcome-grid rows**. The v1 "row 5 — secondary-axis grid-miss" with pre-registered thresholds is REMOVED (it defeated the §26 escape hatch). v2's row 5 is now "REVERSE" (paired CI excludes 0 negative) which is a primary-statistic row, not a secondary-axis row. Chronicle-time §2b grid-miss discipline handles secondary-axis dramatic patterns (parallel to §2a's row-4 pre-commitment pattern).
- **P2-1 (shared-seed extraction underspecified):** v2 adds explicit 5-step extraction procedure in Setup block.
- **P2-3 (mechanism language leaked back in):** v2 removes "under-capacity," "expressivity ceiling," "rank-1 is not narrow at sufficient capacity." Replaced with neutral outcome-routing language.
- **P2-4 (engineering estimate optimistic):** v2 bumps engineering estimate from ~2h to **~4-6h** total; Status-transition checklist item 1 now itemizes all sub-components.

v1 is NOT preserved in git (was never committed). v2 is the first committed draft; target SHA pin deferred to checklist item 8 after codex-v2 review passes.
