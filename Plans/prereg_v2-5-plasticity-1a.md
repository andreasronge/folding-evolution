# Pre-registration: §v2.5-plasticity-1a — Arm A operator-threshold plasticity probe (Baldwin diagnostic on the narrow-plateau decoder)

**Status:** QUEUED — **BLOCKED on engineering + METRIC_DEFINITIONS additions (see "Engineering prerequisites" below)** · target commit `TBD` · 2026-04-17 evening

## Supersession / upstream context

§v2.4-proxy-4d decode-consistent follow-up (commit `cca2323`) confirmed two decoder-specific F/R-dissociation mechanisms. Under **Arm A** the plateau is genuinely narrow: R_fit ≈ 0.004 at `seed_fraction=0.01`, 99.6% of the non-elite population sits in the proxy basin (mean fitness ≈ 0.836), canonical is elite-preserved only. Under **BP_TOPK** a wide solver neutral network already exists structurally (R_fit ≈ 0.72 with R₂_decoded ≈ 0.002 — decoded solvers are structurally distinct from canonical).

Per `docs/chem-tape/runtime-plasticity-direction.md` (revised post-4d): plasticity's strongest test is Arm A, where the plateau is narrow enough that any lifetime-adaptation mechanism has unambiguous work to do. Under BP_TOPK the decoder already does substantial plateau smoothing, so plasticity on top would be redundant and would confound interpretation. This prereg is the Arm A-scoped rank-1 plasticity probe the plasticity-direction doc proposes.

## Engineering prerequisites (MUST land before sweep can run)

Per methodology §25 (measurement infrastructure gate) and §27 (metric definitions in code), this sweep cannot run until the following engineering lands in a separate commit:

### 1. Plastic-operator implementation

- **Mechanism:** rank-1 operator-threshold plasticity. Comparison operators (GT, LT, EQ, and the tape-valent equivalents in `alphabet`) acquire a learnable scalar threshold modifier. During the *train phase* of evaluation, the modifier adapts via a fixed rule (e.g., increment by `+δ` on false-negatives, decrement by `-δ` on false-positives — matching the plasticity-direction doc's "rank-1 shortcut"). During the *test phase* it is frozen.
- **Location:** new module `src/folding_evolution/chem_tape/plasticity.py` OR an extension of `src/folding_evolution/chem_tape/vm.py` (whichever keeps the frozen-path fast-path untouched).
- **Scope:** per the plasticity-direction doc's rank-1 table, "localized (one float per op)." Per-instance plasticity state should NOT affect the config hash when `plasticity_enabled=False`.

### 2. `ChemTapeConfig` fields (hash-excluded at defaults per principle 11)

- `plasticity_enabled: bool = False` — master switch; when False, execution is byte-identical to current Arm A.
- `plasticity_budget: int = 0` — number of train-phase adaptation steps per evaluation; 0 recovers frozen behaviour. At default excluded from hash.
- `plasticity_mechanism: str = "rank1_op_threshold"` — reserved enum; at default-string excluded from hash.
- `plasticity_train_fraction: float = 0.75` — train/test split; 0.75 means 75% of `n_examples` used for adaptation, 25% for held-out evaluation. At default excluded from hash.

### 3. Task split support

The current `sum_gt_10_AND_max_gt_5` task emits 64 examples. For a meaningful train/test split:

- Either (a) modify `task` API to expose a `(train_examples, test_examples)` split deterministically per-seed, or
- (b) Accept an implicit split in the evaluator: first `train_fraction * n_examples` rows are train, remainder are test.

Option (b) is cheaper; option (a) is cleaner. Either is acceptable but must be chosen before the sweep runs. The sweep YAML will commit to one option explicitly.

### 4. `METRIC_DEFINITIONS` additions (principle 27)

The outcome grid below cites the following new entries; these must be added to `analyze_retention.py`'s `METRIC_DEFINITIONS` dict (or a new `analyze_plasticity.py` module, exporting compatibly) before this prereg can be committed as RUNNING:

- `F_AND_test`: Fraction of the 20 seeded runs that achieve best-of-run fitness ≥ threshold on the held-out test examples (separate from training examples). Unit: count/20.
- `F_AND_train`: same, on training examples. (Sanity check — should remain near 20/20 under seeded init.)
- `R_fit_frozen_999`: Fraction of the final population whose training fitness ≥ 0.999 under frozen evaluation (plasticity state disabled at test time). This is the analogue of `R_fit_999` under frozen semantics.
- `R_fit_plastic_999`: Same, under plastic evaluation (train-phase adaptation, then test). Captures the within-lifetime adaptation uplift.
- `Baldwin_gap`: For each individual in the final population, compute `frozen_fitness - plastic_fitness` on held-out test examples. Aggregate as mean of that gap binned by Hamming-to-canonical-active-view distance (bins 0, 1, 2, 3, ≥4). Negative gap means plasticity helps; zero gap means plasticity does nothing; positive gap means plasticity hurts.
- `Baldwin_slope`: Linear regression slope of per-individual `(plastic_fitness - frozen_fitness)` on `hamming_to_canonical`. If slope is negative (closer genotypes get more plastic uplift) → Baldwin signature. If slope is zero (uniform uplift regardless of distance) → universal adapter.

### 5. Analysis pipeline

- New function (or new script `experiments/chem_tape/analyze_plasticity.py`) that reads `final_population.npz` + the new per-individual frozen/plastic fitness columns, computes the Hamming-binned Baldwin gap and the Baldwin slope, and outputs a per-run CSV + per-cell summary.
- Bootstrap 95% CI on `Baldwin_slope` using the same spec as `analyze_retention.py`.

### 6. Pytest coverage

- Round-trip test: `plasticity_enabled=False` at default produces byte-identical final-population dumps to the current Arm A pipeline on a fixed seed.
- Smoke: `plasticity_enabled=True, plasticity_budget=5` on pop=16 gens=10 produces non-zero plasticity state and a non-degenerate Baldwin gap.

**Estimated engineering effort:** ~2-4 hours (plastic VM path + config fields + METRIC_DEFINITIONS + analysis script + tests). Per the plasticity-direction doc the rank-1 mechanism is the cheapest shortcut that tests the hypothesis; this matches that rank.

---

## Question (one sentence)

Under Arm A (direct GP) on `sum_gt_10_AND_max_gt_5` natural sampler with a 75/25 train/test split, does rank-1 operator-threshold plasticity (a) recover solve rate on the held-out examples (`F_AND_test`), (b) exhibit a negative Baldwin slope (closer-to-canonical genotypes get more plastic uplift), or (c) exhibit a flat Baldwin slope (universal-adapter — plasticity works but dissolves evolutionary signal)?

## Hypothesis

Three readings (principle 2), with a fourth principle-26-mandated outcome for the grid:

1. **Baldwin (PASS).** F_AND_test recovers (≥ 15/20 on held-out) AND Baldwin_slope is negative with `p < 0.05` on bootstrap CI. Interpretation: evolved genotypes encode *learnable circuits* — closer-to-canonical genotypes adapt better because the genotype carries real signal that plasticity refines. This is the Hinton & Nowlan 1987 signature; selection pressure is preserved through the adaptation wrapper.
2. **Universal adapter (PARTIAL).** F_AND_test recovers (≥ 15/20) BUT Baldwin_slope is flat (CI contains 0). Interpretation: plasticity works but dissolves evolutionary signal — all genotypes adapt to similar phenotypes regardless of starting structure. Selection on genotypes becomes irrelevant. This is the plasticity-direction doc's cautionary failure mode and is a non-trivial finding per se (a universal-adapter for an arbitrary 2-bit function via a rank-1 mechanism is itself a publishable artefact).
3. **Weak plasticity (FAIL).** F_AND_test does not recover (< 5/20 on held-out). Interpretation: rank-1 plasticity is too weak to cross the cliff under Arm A. Escalation to memory (rank 2) or deeper plastic mechanisms is warranted per the plasticity-direction doc's fallback ladder.
4. **Frozen-wins (INCONCLUSIVE-degenerate).** Plastic evaluation is uniformly worse than frozen evaluation (positive Baldwin gap across Hamming bins). Interpretation: plasticity is actively harmful — the adaptation rule misaligns the thresholds. Engineering error likely; inspect before claiming.

Relative to the §v2.4-proxy-4d decoder-specific split, this probe tests whether **within-lifetime adaptation can do the smoothing that Arm A's decoder doesn't**. If PASS, the plasticity-direction doc's prediction that "plasticity narrows Arm A's proxy basin toward canonical in a way that structural decoder smoothing (BP_TOPK) does not" is supported.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_5_plasticity_1a.yaml` (to be created post-engineering)
- **Arms / conditions:**
  - `arm=A`, `plasticity_enabled=True`, `plasticity_budget ∈ {3, 10}`, `seed_fraction=0.01` (seeded with canonical AND body — anchors the Hamming-to-canonical axis)
  - Control cells: `arm=A`, `plasticity_enabled=False`, matched `sf=0.01` (the §v2.4-proxy-4c Arm A baseline at reduced scale)
  - Drift check: `plasticity_enabled=True`, `sf=0.0` (randomly-initialised plasticity — tests whether adaptation creates canonical-equivalent circuits without prior genotypic signal)
  - Total: 2 (budget) + 1 (control) + 1 (drift) = 4 cells × 20 seeds = 80 runs.
- **Seeds:** 0..19 per cell (disjoint-comparable with §v2.4-proxy-4c Arm A baseline).
- **Fixed params:** `pop_size=512` (reduced from §v2.4 default per plasticity-direction doc), `generations=500` (reduced; the adaptation budget inside each eval adds compute per-individual), `tournament_size=3`, `elite_count=2`, `mutation_rate=0.03`, `crossover_rate=0.7`, `tape_length=32`, `alphabet=v2_probe`, `disable_early_termination=true`, `dump_final_population=true`, `seed_tapes` = canonical AND body (same as 4b/4c/4d), `plasticity_train_fraction=0.75`, `plasticity_mechanism="rank1_op_threshold"`, `backend=mlx`.
- **Est. compute:** 4 cells × 20 seeds. Arm A baseline at pop=1024 gens=1500 took ~7 min/run per 4d; at pop=512 gens=500 ≈ 1/6 of that = ~1.2 min/run frozen. Plastic evaluation adds `plasticity_budget` forward passes per individual per generation, so plastic cells ≈ 1.2 min × (1 + plasticity_budget/n_examples_effective) — conservatively 2-4 min/run. At 10 workers: ~15-30 min wall for the sweep.
- **Related experiments:** §v2.4-proxy-4c Arm A (commit `9135345` — frozen baseline); §v2.4-proxy-4d decode-consistent follow-up (commit `cca2323` — decoder-specific mechanism anchor); `docs/chem-tape/runtime-plasticity-direction.md` (design motivation).

**Principle 20 audit:** task function and sampler unchanged. The 75/25 train/test split is a new analysis-layer partition of the existing `n_examples=64` labelled set, NOT a change to the training distribution. Principle 20 is marginally triggered: verify at prereg time that the train/test split is class-balanced (both AND-true and AND-false examples present in both halves) — a 75/25 random split over 64 examples with the natural sampler's mixed labels should be fine, but the sweep YAML must assert this per-seed.

**Principle 23 audit:** Control cell (frozen, plasticity disabled) must reproduce §v2.4-proxy-4c Arm A baseline on the 20 shared seeds within bootstrap CI at the reduced scale. Validate before interpreting plastic cells.

## Baseline measurement (required)

- **Baseline quantity 1 — frozen F_AND on held-out test at `sf=0.01`, Arm A, pop=512, gens=500:** must be measured by the control cell in this sweep (`plasticity_enabled=False`). The §v2.4-proxy-4c Arm A baseline was at pop=1024 gens=1500 full-data, so it cannot be transferred as-is; the reduced-scale control cell re-establishes the frozen baseline under this prereg's parameters.
- **Baseline quantity 2 — Arm A R_fit_999 at `sf=0.01`, `mr=0.03`:** 0.004 per §v2.4-proxy-4d decode-consistent follow-up (commit `cca2323`). Carried forward as the "plateau is narrow" anchor; the plasticity lift is measured against this (R_fit_plastic_999 vs R_fit_frozen_999).
- **Metric definitions (principle 27):** cite from the new `METRIC_DEFINITIONS` entries the engineering step adds; verbatim quotes to be inserted into this prereg at the RUNNING-commit revision after engineering lands. **This prereg cannot transition from QUEUED to RUNNING until the cited entries exist in code.**

## Internal-control check (required)

- **Tightest internal contrast:** plastic vs frozen on the same seeds, same task, same initialisation (seeded canonical). Directly tests whether lifetime adaptation does work the frozen path cannot.
- **Secondary contrast:** plastic `sf=0.0` (random init) vs plastic `sf=0.01` (canonical-seeded). If plastic cells solve at similar rates regardless of seeding, that is evidence for the universal-adapter reading (2) before looking at the Baldwin slope — plasticity recovers solutions from any starting point, dissolving the canonical-seed information advantage.
- **Are you running it here?** Yes, all four cells are present.

## Pre-registered outcomes (required — §26-compliant outcome grid across two primary axes + F-sanity)

<!--
Per methodology §26: measured axes at per-seed resolution each get a coarse-bin row.
  - F_AND_test (primary; can-plasticity-recover-solve-rate-on-held-out)
  - Baldwin_slope (primary; mechanism axis — genotypic-signal-preserved-or-dissolved)
  - R_fit_plastic_999 - R_fit_frozen_999 (co-primary; population-layer adaptation uplift)
  - F_AND_train (sanity — should stay near 20/20 under seeded init)

F_AND_test coarse bins: {≥15/20 recovered | 5-14/20 partial | <5/20 not-recovered}
Baldwin_slope coarse bins: {negative w/ CI excluding 0 — Baldwin | flat, CI includes 0 — universal | positive w/ CI excluding 0 — degenerate-frozen-wins}
(R_fit_plastic - R_fit_frozen) coarse bins: {> 0.1 large uplift | [-0.1, 0.1] minimal uplift | < -0.1 harm}
-->

| outcome | F_AND_test | Baldwin_slope | R_fit_plastic - R_fit_frozen | interpretation |
|---|---|---|---|---|
| **PASS — Baldwin** | ≥ 15/20 | negative, 95% CI excludes 0 | > 0.1 | Reading (1): genotype encodes learnable circuit; closer-to-canonical genotypes get more plastic uplift. Selection pressure preserved through adaptation wrapper. Escalate per decision rule: (a) rank-2 memory shortcut + (b) BP_TOPK control cell. |
| **PARTIAL — universal adapter** | ≥ 15/20 | flat, CI includes 0 | > 0.1 | Reading (2): plasticity works but erases evolutionary signal. Rank-1 operator-threshold is expressive enough to adapt *any* starting genotype to canonical-equivalent behaviour. Non-trivial finding. Next step: tighten adaptation budget (reduce `plasticity_budget`) until the Baldwin signature re-emerges — if it does, the capacity is the load-bearing variable; if it doesn't, the mechanism is too expressive for this task. |
| **FAIL — weak plasticity** | < 5/20 | any | small or negative | Reading (3): rank-1 plasticity is too weak to cross the narrow plateau under Arm A. Fallback per plasticity-direction doc: try rank-2 (memory) before concluding plasticity doesn't help. |
| **INCONCLUSIVE — frozen wins** | any | positive, CI excludes 0 | < -0.1 | Reading (4): plastic evaluation is actively harmful. Likely an engineering error in the adaptation rule (e.g., threshold updates in the wrong direction). Inspect before interpreting. |
| **INCONCLUSIVE — mid F_test** | 5-14/20 | any | any | Intermediate recovery; either adaptation budget is marginal or task has per-seed variance. Run n=20 independent-seed replication (seeds 20-39) at the best-performing budget before claiming. |
| **SWAMPED — train fails** | any | any | any + F_AND_train < 15/20 | Seeded individuals do not even solve on training examples under the plastic path. Infrastructure or task-split bug. Inspect before running any further plasticity probe. |
| **INCONCLUSIVE** | any pattern not fitting above | any | any | Per principle 2b update the grid before interpreting. |

**Threshold justification:** 15/20 is the §v2.4-alt PASS threshold on a structurally similar task; reuse preserves cross-sweep comparability. 5/20 is the §v2.6 FAIL threshold on the Pair-1 body discovery. Baldwin_slope CI bounds at 0 (two-sided) is the standard null. The R_fit delta bin width 0.1 is a ~10× the bootstrap CI width of the §v2.4-proxy-4d baseline R_fit measurements (0.004-0.72 range, CIs < 0.01), so 0.1 clearly separates "real uplift" from "noise."

## Degenerate-success guard (required)

- **Universal-adapter artefact (PARTIAL row).** Principle 4: is 20/20 F_AND_test under plastic + random-init (sf=0.0) too clean? Detection: if the `plasticity_enabled=True, sf=0.0` drift cell achieves F_AND_test ≥ 15/20, the adaptation rule is expressive enough to discover canonical-equivalent behaviour from noise — selection on genotypes becomes irrelevant. This is the universal-adapter signature; report as PARTIAL (not PASS) and tighten capacity.
- **Train-test leakage artefact.** If the task split exposes test examples to plasticity adaptation (e.g., via a bug in the train/test selector), F_AND_test will trivially match F_AND_train. Detection: compute `F_AND_test - F_AND_train` — should be modestly negative or near zero under honest generalisation; a suspicious near-zero gap at high budget combined with very high plastic R_fit flags leakage. Inspect the train/test split code path before claiming.
- **Threshold-saturation artefact.** If plastic thresholds converge to trivial values (always-true or always-false comparisons) that happen to match the training distribution, the circuit doesn't actually learn — it memorises. Detection: inspect final plastic thresholds on 5 best-of-run winners; reject as degenerate if > 50% of comparison operators have saturated to constants.
- **Adaptation-budget-too-high artefact.** At `plasticity_budget=10` the adaptation rule has 10 forward passes per evaluation. If plasticity absorbs 10× the information that the genotype encodes, the universal-adapter risk is highest here. Report `plasticity_budget=3` and `=10` cells separately in the outcome table; do not average across budgets.

## Statistical test

- **Primary:** bootstrap 95% CI on `Baldwin_slope` (linear regression slope of per-individual (plastic - frozen) fitness on Hamming-to-canonical) per cell. Per §27 METRIC_DEFINITIONS `bootstrap_ci_spec`: 10 000 resamples via `numpy.random.default_rng(seed=42)`.
- **Secondary:** paired McNemar on `F_AND_test` between plastic and frozen cells on shared seeds. Two-sided, raw α=0.05.
- **Classification (principle 22):** **confirmatory.** This prereg gates a new findings.md candidate claim — "rank-1 operator-threshold plasticity lifts solve rate on the narrow Arm A plateau, with Baldwin signature." The confirmatory test is the Baldwin_slope CI being strictly negative (excluding 0). `F_AND_test` is a secondary confirmatory variable (paired McNemar between plastic and frozen must reject null for PASS).
- **Family:** **new findings.md family** — `plasticity-narrow-plateau` (Arm A scoped). Family size at this prereg = 1 (this is the first confirmatory test in a new family). Corrected α = 0.05 / 1 = 0.05. Future plasticity probes (rank-2 memory, BP_TOPK control, other tasks) would grow the family and lower the corrected α.

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_AND_train`, `F_AND_test`, `best-of-run` plastic and frozen fitness
- Per-cell bootstrap 95% CI on `Baldwin_slope`, `R_fit_plastic_999`, `R_fit_frozen_999`, `R_fit_plastic_999 - R_fit_frozen_999`
- Per-cell Hamming-binned Baldwin gap (bins {0, 1, 2, 3, ≥4}) — the diagnostic plot the plasticity-direction doc requires: frozen vs plastic fitness stratified by Hamming-to-canonical
- Final plastic-threshold distribution for 5 best-of-run winners per cell — degenerate-success guard (threshold saturation)
- `unique_genotypes` per cell — sanity that the population has not frozen
- Paired-seed `F_AND_test(plastic) - F_AND_test(frozen)` distribution — the paired McNemar input

## Scope tag (required for any summary-level claim)

**If this experiment PASSes, the new findings.md candidate enters scoped as:**
`within-family · n=20 per cell (4 cells) · at Arm A (direct GP) pop=512 gens=500 mr=0.03 tournament_size=3 elite_count=2 disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler with 75/25 train/test split · plasticity_mechanism=rank1_op_threshold, plasticity_budget ∈ {3, 10} · seeded canonical 12-token AND body at sf=0.01`.

Explicitly not-broadening to: BP_TOPK (not tested here — follow-up experiment per PASS decision rule); other task families (not tested); rank-2 or deeper plastic mechanisms (not tested).

## Decision rule

- **PASS — Baldwin →** (1) promote candidate to findings.md as a NEW entry `plasticity-narrow-plateau` with ACTIVE status and the scope tag above; (2) escalate the plasticity direction per the plasticity-direction doc: queue §v2.5-plasticity-1b (rank-2 memory shortcut); (3) queue a BP_TOPK control cell probe (same design, BP_TOPK arm) — the plasticity-direction doc's prediction is that BP_TOPK will see a much smaller lift because its decoder already does plateau smoothing. Cross-arm magnitude comparison is the test of substitutes-vs-complements.
- **PARTIAL — universal adapter →** do NOT promote to findings.md (not a positive mechanism claim). Queue a capacity-tightening sweep (`plasticity_budget ∈ {1, 2}`) to find the capacity boundary where the Baldwin signature re-emerges. If none exists, the rank-1 mechanism is fundamentally too expressive for this task; write up as a negative mechanism-layer finding.
- **FAIL — weak plasticity →** do NOT promote. Try the rank-2 (memory) mechanism per the plasticity-direction doc's fallback ladder before concluding plasticity does not help Arm A.
- **INCONCLUSIVE — frozen wins →** STOP and inspect. Likely an engineering bug in the plastic adaptation rule. Do not run additional plasticity sweeps until the code is validated on a minimal synthetic case.
- **INCONCLUSIVE — mid F_test →** run n=20 independent-seed replication at the best-performing budget (seeds 20-39). Do not claim until the replication lands.
- **SWAMPED — train fails →** engineering bug. Stop and inspect.
- **INCONCLUSIVE (grid-miss) →** update the grid per principle 2b before interpreting.

---

*Audit trail.* Seven outcome rows (principle 2 + 2b). Baseline F_AND_test must be measured by the control cell in this sweep; §v2.4-proxy-4c Arm A baseline at pop=1024 gens=1500 is cited as context but not transferred (principle 6). Internal control is plastic vs frozen on shared seeds (principle 1). Degenerate-success guard covers universal-adapter, train-test leakage, threshold saturation, adaptation-budget-too-high (principle 4). Principle 20 marginally triggered by the train/test split — class balance must be verified at sweep launch. Principle 22 classified as **confirmatory**, founding a new `plasticity-narrow-plateau` FWER family at size 1. Principle 23 gate preserved — control cell must reproduce the §v2.4-proxy-4c Arm A frozen baseline at this reduced scale. Principle 25 and principle 27 both **blocked pending engineering**: the `METRIC_DEFINITIONS` entries (`F_AND_test`, `R_fit_plastic_999`, `R_fit_frozen_999`, `Baldwin_gap`, `Baldwin_slope`) do not yet exist in code. Principle 26 satisfied at design time — both `F_AND_test` and `Baldwin_slope` are gridded as primary axes; no diagnostic axis is silently demoted. Decision rule commits to specific findings.md / follow-up-experiment actions per outcome (principle 19).

## Status-transition checklist (from QUEUED → RUNNING)

Before this prereg can move from QUEUED to RUNNING, all six engineering prerequisites above must be complete and committed. At that point:

1. Add a supersession note to this prereg's top ("Engineering landed at commit `X`; prereg now RUNNING").
2. Update `target commit` in the status line to the post-engineering commit short-SHA.
3. Re-verify that each METRIC_DEFINITIONS entry cited in "Pre-registered outcomes" matches the code verbatim (principle 27).
4. Run the pytest coverage added in step 6 of the engineering prereqs; attach pass confirmation.
5. Launch the sweep.
