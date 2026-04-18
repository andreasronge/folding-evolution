# Pre-registration: §v2.5-plasticity-1a — Arm A operator-threshold plasticity probe (Baldwin diagnostic on the narrow-plateau decoder)

**Status:** RUNNING · engineering prerequisites 1–6 discharged at commits `d735e5e` (config fields + hash exclusion), `758e175` (rank-1 plastic VM path + evaluate.py gate + evolve.py per-individual dump), `feae431` (analyze_plasticity.py METRIC_DEFINITIONS + pytest) · reviewer audit 2026-04-18 (research-rigor skill): principle 11 passes (`test_plasticity_hash_stability_at_defaults`); principle 23 byte-identity passes via `evaluate.py:104 if cfg.plasticity_enabled:` gate; principle 27 METRIC_DEFINITIONS live in `experiments/chem_tape/analyze_plasticity.py` · sweep YAML `experiments/chem_tape/sweeps/v2/v2_5_plasticity_1a.yaml` (12 cells × 20 seeds = 240 configs, all unique hashes) · launched via overnight queue 2026-04-18

**Historical (pre-2026-04-18):** QUEUED — **BLOCKED on engineering + METRIC_DEFINITIONS additions (see "Engineering prerequisites" below)** · target commit `TBD` · 2026-04-17 evening

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
- `plasticity_delta: float = 1.0` — per-step threshold shift for the sign-gradient rule; δ is a **shared scalar across all GT operations** in the decoded program (rank-1 = one float total; both conjuncts adapt through the same δ). At default excluded from hash.

  **Task-scale justification for δ=1.0.** `sum_gt_10_AND_max_gt_5` uses integer operands: `sum(xs) ∈ [0, 36]` vs threshold 10; `max(xs) ∈ [0, 9]` vs threshold 5. δ=1 shifts either threshold by one integer unit per sign flip — meaningful and non-trivial. Budget grid `{1, 2, 3, 5}` (revised 2026-04-18) keeps max accumulated shift ≤ ±5 and the `max>5` conjunct's threshold in [0, 10] — non-trivial and non-saturated across the full range. The earlier draft's budget=10 cell hit ±10 shift and could saturate the `max>5` conjunct to always-true (threshold → −5) or near-always-false (threshold → 9+), confounding the universal-adapter signal with threshold saturation. Removing budget=10 keeps the Baldwin-slope regression in the useful-capacity range. Pin δ=1 for this sweep; do not sweep δ alongside budget — a 2D search at this stage would be parameter search disguised as mechanism discovery.

### 3. Task split support

The current `sum_gt_10_AND_max_gt_5` task emits 64 examples. For a meaningful train/test split:

- Either (a) modify `task` API to expose a `(train_examples, test_examples)` split deterministically per-seed, or
- (b) Accept an implicit split in the evaluator: first `train_fraction * n_examples` rows are train, remainder are test.

Option (b) is cheaper; option (a) is cleaner. Either is acceptable but must be chosen before the sweep runs. The sweep YAML will commit to one option explicitly.

### 4. `METRIC_DEFINITIONS` additions (principle 27)

The outcome grid below cites the following new entries; these must be added to `analyze_retention.py`'s `METRIC_DEFINITIONS` dict (or a new `analyze_plasticity.py` module, exporting compatibly) before this prereg can be committed as RUNNING:

- `F_AND_test`: Fraction of the 20 seeded runs that achieve best-of-run fitness ≥ threshold on the held-out test examples (separate from training examples). Unit: count/20. **Binary per-run measure — used for F-recovery claim only, not for Baldwin slope regression.**
- `F_AND_train`: same, on training examples. (Sanity check — should remain near 20/20 under seeded init.)
- `test_fitness_frozen`: Per-individual fraction of held-out test examples correctly classified with δ=0 (frozen, no adaptation). Continuous scalar in [0, 1]; 16-valued given 75/25 split over 64 examples (16 test examples). **This is the continuous test-fitness used in the Baldwin slope regression — not the binary F_AND_test.** Emitted per-individual in `final_population.npz`.
- `test_fitness_plastic`: Per-individual fraction of held-out test examples correctly classified with δ trained on the 48 train examples and then frozen. Continuous scalar in [0, 1]. Emitted per-individual in `final_population.npz`.
- `delta_convergence`: Per-individual final value of δ after train-phase adaptation, stored alongside frozen/plastic fitnesses in `final_population.npz`. Used to diagnose universal-adapter signature: if `std(delta_final)` is small relative to `mean(delta_final)` across diverse genotypes, δ converges to the same value regardless of genotype → universal-adapter flag independent of F recovery.
- `GT_bypass_fraction`: Fraction of final-population individuals whose **decoded program contains no GT token**. These individuals have `test_fitness_plastic - test_fitness_frozen = 0` trivially (plasticity cannot act on a program with no GT operation) and must be **excluded from the Baldwin slope regression and reported separately**. Computed by scanning the decoded token sequence for the GT opcode before any fitness evaluation. Emitted as a per-cell scalar in the analysis CSV.
- `R_fit_frozen_999`: Fraction of the final population whose training fitness ≥ 0.999 under frozen evaluation (plasticity state disabled at test time). This is the analogue of `R_fit_999` under frozen semantics.
- `R_fit_plastic_999`: Same, under plastic evaluation (train-phase adaptation, then test). Captures the within-lifetime adaptation uplift.
- `Baldwin_gap`: For each non-GT-bypass individual in the final population, compute `test_fitness_plastic - test_fitness_frozen` on held-out test examples. Aggregate as mean of that gap binned by Hamming-to-canonical-active-view distance (bins 0, 1, 2, 3, ≥4). Positive gap means plasticity helps; zero gap means plasticity does nothing; negative gap means plasticity hurts. **GT-bypass individuals excluded; reported separately via GT_bypass_fraction.**
- `Baldwin_slope`: Linear regression slope of per-individual `(test_fitness_plastic - test_fitness_frozen)` on `hamming_to_canonical`, computed on non-GT-bypass individuals only. If slope is negative (closer genotypes get more plastic uplift) → Baldwin signature. If slope is zero (uniform uplift regardless of distance) → universal adapter. Bootstrap 95% CI on slope using 10 000 resamples.

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

  **Arm A (direct GP) — primary confirmatory cells, per-tape mutation budget matched:**
  - `arm=A`, `plasticity_enabled=True`, `plasticity_budget ∈ {1, 2, 3, 5}`, `seed_fraction=0.01`, `generations=1500` (seeded with canonical AND body — anchors the Hamming-to-canonical axis; `gens=1500 × mr=0.03 → ~45 expected mutations/tape` matches the §v2.4-proxy-4c Arm A frozen baseline exactly on the per-tape axis that the §v2.4-proxy-5b-amended BOTH-KINETIC finding identified as load-bearing)
  - Control: `arm=A`, `plasticity_enabled=False`, `sf=0.01`, `generations=1500` (the §v2.4-proxy-4c Arm A baseline at reduced pop; per-tape mutation count matched via identical gens × mr)
  - Drift check: `arm=A`, `plasticity_enabled=True`, `plasticity_budget=5`, `sf=0.0`, `generations=1500` (randomly-initialised — universal-adapter signature without canonical seed)

  **BP_TOPK (preserve+consume) — exploratory control arm, budget mismatch acknowledged:**
  - `arm=BP_TOPK`, `plasticity_enabled=True`, `plasticity_budget ∈ {1, 2, 3, 5}`, `seed_fraction=0.01`, `generations=500` (BP_TOPK baseline mutation budget ≠ §v2.4-proxy-4d — mismatch is acknowledged in the exploratory scope tag)
  - Control: `arm=BP_TOPK`, `plasticity_enabled=False`, `sf=0.01`, `generations=500`
  - Drift check: `arm=BP_TOPK`, `plasticity_enabled=True`, `plasticity_budget=5`, `sf=0.0`, `generations=500`

  **Rationale for co-registration.** §v2.4-proxy-4d established per-decoder baselines: Arm A has narrow plateau (R_fit_frozen ≈ 0.004); BP_TOPK has wide solver plateau (R_fit_frozen ≈ 0.72). Running both arms in the same sweep enables the substitute-vs-complement test (does plasticity lift R_fit more under Arm A than BP_TOPK, or equally?) as a single registered design rather than a post-hoc follow-up, which would lose the clean cross-arm comparison baseline.

  **Rationale for asymmetric generations (revised 2026-04-18 after codex review).** The §v2.4-proxy-5b-amended BOTH-KINETIC result identified per-tape mutation count as the load-bearing variable. Principle 23 requires the Arm A frozen-control cell to reproduce the §v2.4-proxy-4c baseline's per-tape mutation budget. §v2.4-proxy-4c: `pop=1024 × gens=1500 × mr=0.03`, per-tape expected mutations = gens × mr = 45. Plasticity Arm A at `pop=512 × gens=1500 × mr=0.03`: per-tape expected = 45 — **matched exactly on the per-tape axis**. Total-population mutation budget is halved by the pop reduction (768,000 vs 1,536,000 tape-generation steps), which is acknowledged as an unavoidable compute-scale decision per the plasticity-direction doc's pop=512 commitment; principle-23 gate is discharged on the per-tape budget only. BP_TOPK arm is exploratory (no claim gate) so the budget mismatch at gens=500 is acknowledged rather than matched — avoids unnecessary compute on the arm that only contributes effect-size.

  **Rationale for budget grid {1, 2, 3, 5} (revised 2026-04-18).** The earlier draft had budget ∈ {3, 10}; at budget=10 with δ=1 the `max>5` conjunct's threshold can saturate (reach −5 or 9+), confounding "universal adapter" signal with "threshold saturation" artefact. The revised range {1, 2, 3, 5} brackets the saturation boundary (budget=5 × δ=1 reaches max shift ±5, keeping `max>5` threshold in [0, 10] — still non-trivial) and gives real gradient coverage for the Baldwin-slope regression across the useful-capacity range.

  **Arm classification for FWER (principle 22).** Arm A cells: **confirmatory** — the Baldwin_slope CI test gates the `plasticity-narrow-plateau` claim (family size 1 → corrected α = 0.05). BP_TOPK cells: **exploratory** — effect-size only; no p-value gates a new findings.md claim in this sweep. The differential magnitude (Arm A lift vs BP_TOPK lift) is logged as a diagnostic for the substitute-vs-complement hypothesis, which would require a separate confirmatory prereg to promote.

  **Total: Arm A (4 budget + 1 control + 1 drift) + BP_TOPK (4 budget + 1 control + 1 drift) = 12 cells × 20 seeds = 240 runs.**
- **Seeds:** 0..19 per cell (disjoint-comparable with §v2.4-proxy-4c Arm A baseline).
- **Fixed params:** `pop_size=512` (reduced from §v2.4 default per plasticity-direction doc), `tournament_size=3`, `elite_count=2`, `mutation_rate=0.03`, `crossover_rate=0.7`, `tape_length=32`, `alphabet=v2_probe`, `disable_early_termination=true`, `dump_final_population=true`, `seed_tapes` = canonical AND body (same as 4b/4c/4d), `plasticity_train_fraction=0.75`, `plasticity_mechanism="rank1_op_threshold"`, `plasticity_delta=1.0`, `backend=mlx`. `generations` varies per arm (Arm A: 1500 for per-tape budget match; BP_TOPK: 500 exploratory) as noted above.
- **Est. compute (revised 2026-04-18 after codex review — per-tape budget matched at gens=1500, not gens=2250):**
  - **Arm A cells (gens=1500, per-tape budget matched):** frozen control ≈ 3.5 min/run at pop=512 gens=1500 (≈ half of §v2.4-proxy-4c's pop=1024 gens=1500 baseline of ~7 min/run). Plastic cells at budget ∈ {1,2,3,5} add per-individual per-generation plasticity-simulation cost — the cost scales roughly linearly in `plasticity_budget`: conservatively 3.5 × (1 + 0.2 × budget) min/run, so budget=1 ≈ 4.2 min, budget=5 ≈ 7 min. 6 cells × 20 seeds = 120 runs; at 10 workers with mix of frozen/plastic ≈ 70-90 min wall.
  - **BP_TOPK cells (gens=500, exploratory budget mismatch):** frozen control ≈ 1 min/run; plastic cells 1-2.5 min/run scaling with budget. 6 cells × 20 seeds = 120 runs at 10 workers ≈ 20-30 min wall.
  - **Total sweep wall: ~90-120 min (1.5-2 hours).** Overnight-feasible with headroom. Arm A plastic cells at budget=5 are the longest single-run bound (~7 min each, 20 in parallel).
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

**Note on GT-bypass exclusion (pre-registered).** `Baldwin_slope` and `Baldwin_gap` below are computed on the **non-GT-bypass subset only**. Before scoring any row: check `GT_bypass_fraction`. If ≥ 0.50, that cell is INCONCLUSIVE on the Baldwin axis regardless of slope value — flag it and report the GT-bypass fraction. GT-bypass individuals (decoded program contains no GT token; trivially ΔF=0) are reported separately and do not enter the regression. A GT-bypass majority is itself a finding about what the population converges to.

**Note on continuous vs binary fitness.** `Baldwin_slope` uses `test_fitness_frozen` and `test_fitness_plastic` — continuous per-individual fractions of 16 held-out examples correct (not the binary `F_AND_test`). `F_AND_test` is best-of-run binary, used only for the F-recovery column.

**Arm A outcome grid (confirmatory — `plasticity-narrow-plateau` family, corrected α = 0.05/1 = 0.05):**

| outcome | F_AND_test | Baldwin_slope | R_fit_plastic − R_fit_frozen | GT_bypass_fraction | interpretation |
|---|---|---|---|---|---|
| **PASS — Baldwin** | ≥ 15/20 | negative, 95% CI excludes 0 | > 0.1 | < 0.50 | Reading (1): genotype encodes learnable circuit; closer-to-canonical genotypes adapt better. Selection pressure preserved. Escalate per decision rule: rank-2 memory + check substitute-vs-complement from BP_TOPK grid. |
| **PARTIAL — universal adapter** | ≥ 15/20 | flat, CI includes 0 | > 0.1 | < 0.50 | Reading (2): plasticity works but erases evolutionary signal. Check `delta_convergence`: small std(δ_final) across diverse genotypes → universal-adapter confirmed in δ space. Tighten budget. |
| **PARTIAL — δ-convergence flag** | ≥ 15/20 | any | > 0.1 | < 0.50 | F recovers but δ_final clusters tightly regardless of genotype origin → universal-adapter signature in adaptation dynamics even if slope is non-flat. Inspect δ distribution; do not claim Baldwin without resolving. |
| **FAIL — weak plasticity** | < 5/20 | any | small or negative | < 0.50 | Reading (3): rank-1 too weak for Arm A's narrow plateau. Escalate to rank-2 memory. |
| **INCONCLUSIVE — frozen wins** | any | positive, CI excludes 0 | < -0.1 | any | Plasticity actively harmful. Likely engineering bug in sign-gradient direction. Stop and inspect. |
| **INCONCLUSIVE — mid F_test** | 5–14/20 | any | any | < 0.50 | Marginal recovery. Run n=20 replication (seeds 20–39) at best-performing budget before claiming. |
| **INCONCLUSIVE — GT-bypass majority** | any | any | any | ≥ 0.50 | Regression input is minority subset; slope unreliable. Report GT-bypass fraction and inspect what circuit type dominates. |
| **SWAMPED — train fails** | any | any | any | any + F_AND_train < 15/20 | Infrastructure or task-split bug. Stop. |
| **INCONCLUSIVE** | any pattern not fitting above | any | any | any | Per principle 2b update the grid before interpreting. |

**BP_TOPK outcome grid (exploratory — effect-size only, no p-value gates a new findings.md claim in this sweep):**

Context: §v2.4-proxy-4d R_fit_frozen ≈ 0.72 under BP_TOPK — wide solver plateau already exists. Plasticity is expected to show less R_fit lift than Arm A (substitute hypothesis) or similar lift (complement hypothesis). The cross-arm differential is logged as a diagnostic for a future confirmatory sweep.

| BP_TOPK outcome | R_fit_plastic − R_fit_frozen | vs. Arm A lift | interpretation |
|---|---|---|---|
| **Substitute signal** | < 0.05 | Arm A lift > 0.10 | Plasticity and decoder smoothing are substitutes — they occupy the same layer of landscape smoothing. Little room for plasticity to add on an already-wide plateau. |
| **Complement signal** | comparable magnitude to Arm A | within factor 2 | Plasticity and decoder smoothing are complements — operate on different layers. Both needed. Flag for a future confirmatory cross-arm prereg. |
| **Negative lift** | < −0.05 | any | Plasticity disrupts BP_TOPK's neutral network. Inspect best-of-run winners for mechanism. |
| **Ceiling / SWAMPED** | any + R_fit_frozen ≥ 0.90 | n/a | Metric ceiling; plasticity cannot add measurable lift. Log and move on. |

**Threshold justification:** 15/20 is the §v2.4-alt PASS threshold on a structurally similar task; reuse preserves cross-sweep comparability. 5/20 is the §v2.6 FAIL threshold on the Pair-1 body discovery. Baldwin_slope CI bounds at 0 (two-sided) is the standard null. The R_fit delta bin width 0.1 is a ~10× the bootstrap CI width of the §v2.4-proxy-4d baseline R_fit measurements (0.004-0.72 range, CIs < 0.01), so 0.1 clearly separates "real uplift" from "noise."

## Degenerate-success guard (required)

- **Universal-adapter artefact (PARTIAL row).** Principle 4: is 20/20 F_AND_test under plastic + random-init (sf=0.0) too clean? Detection: if the `plasticity_enabled=True, sf=0.0` drift cell achieves F_AND_test ≥ 15/20, the adaptation rule is expressive enough to discover canonical-equivalent behaviour from noise — selection on genotypes becomes irrelevant. This is the universal-adapter signature; report as PARTIAL (not PASS) and tighten capacity.
- **Train-test leakage artefact.** If the task split exposes test examples to plasticity adaptation (e.g., via a bug in the train/test selector), F_AND_test will trivially match F_AND_train. Detection: compute `F_AND_test - F_AND_train` — should be modestly negative or near zero under honest generalisation; a suspicious near-zero gap at high budget combined with very high plastic R_fit flags leakage. Inspect the train/test split code path before claiming.
- **Threshold-saturation artefact.** If plastic thresholds converge to trivial values (always-true or always-false comparisons) that happen to match the training distribution, the circuit doesn't actually learn — it memorises. Detection: inspect final plastic thresholds on 5 best-of-run winners; reject as degenerate if > 50% of comparison operators have saturated to constants.
- **Adaptation-budget-too-high artefact (revised 2026-04-18 to match budget range {1,2,3,5}).** At `plasticity_budget=5` the adaptation rule has 5 forward passes per evaluation — the highest in the current range. At budget=5 with δ=1 the `max>5` conjunct threshold can reach [0, 10] (5 steps in either direction); threshold=0 means "always true"; threshold=10 means "never true when max∈[0,9]". Not fully saturated but near the edge — inspect final δ values for budget=5 cells; if δ_final ≤ −5 or δ_final ≥ +5 (i.e., at the extreme of the ±5 accumulation range) in > 50% of best-of-run winners, the conjunct has reached the boundary — report as threshold-saturation artefact. Report every budget cell separately; do not average.
- **GT-bypass artefact.** Programs with no GT token in the decoded sequence cannot be made plastic — their `test_fitness_plastic = test_fitness_frozen` regardless of adaptation budget. If the final population converges to predominantly GT-bypass programs (GT_bypass_fraction ≥ 0.50), the Baldwin regression is computed on a minority subset and may be unreliable. Pre-register this as the `INCONCLUSIVE — GT-bypass majority` row. Detection: scan decoded program token sequences for GT opcode before evaluation; tag each individual. A GT-bypass majority in the Arm A plastic cells is itself informative — it means selection under plasticity favors GT-free programs, potentially because GT-free circuits have higher frozen fitness (they're not penalized by plasticity instability).
- **δ-convergence artefact.** Universal adapter in δ space: if δ_final clusters tightly (std(δ_final) ≈ 0) across genotypically diverse individuals (e.g., genotypes with Hamming distance ≥ 4 from canonical), all genotypes are adapting to the same threshold offset regardless of their structure — the adaptation rule, not the genotype, is doing the work. Pre-register: compute per-cell `std(delta_final)` stratified by Hamming-to-canonical bin. If std is near zero in all bins, report as PARTIAL — δ-convergence flag before inspecting the Baldwin slope.

## Statistical test

- **Primary:** bootstrap 95% CI on `Baldwin_slope` (linear regression slope of per-individual (plastic - frozen) fitness on Hamming-to-canonical) per cell. Per §27 METRIC_DEFINITIONS `bootstrap_ci_spec`: 10 000 resamples via `numpy.random.default_rng(seed=42)`.
- **Secondary:** paired McNemar on `F_AND_test` between plastic and frozen cells on shared seeds. Two-sided, raw α=0.05.
- **Classification (principle 22):** **confirmatory.** This prereg gates a new findings.md candidate claim — "rank-1 operator-threshold plasticity lifts solve rate on the narrow Arm A plateau, with Baldwin signature." The confirmatory test is the Baldwin_slope CI being strictly negative (excluding 0). `F_AND_test` is a secondary confirmatory variable (paired McNemar between plastic and frozen must reject null for PASS).
- **Family:** **new findings.md family** — `plasticity-narrow-plateau` (Arm A scoped). Family size at this prereg = 1 (this is the first confirmatory test in a new family). Corrected α = 0.05 / 1 = 0.05. Future plasticity probes (rank-2 memory, BP_TOPK control, other tasks) would grow the family and lower the corrected α.

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_AND_train`, `F_AND_test`, `best-of-run` plastic and frozen fitness (binary per-run)
- Per-individual `test_fitness_frozen`, `test_fitness_plastic` (continuous, fraction of 16 held-out examples correct) — the Baldwin slope regression inputs
- Per-individual `delta_convergence` (δ_final after train-phase adaptation) — emitted alongside fitnesses in `final_population.npz`
- Per-cell `GT_bypass_fraction` — fraction of final population with no GT token in decoded program
- Per-cell `std(delta_final)` stratified by Hamming-to-canonical bin — δ-convergence artefact check
- Per-cell bootstrap 95% CI on `Baldwin_slope`, `R_fit_plastic_999`, `R_fit_frozen_999`, `R_fit_plastic_999 − R_fit_frozen_999`
- Per-cell Hamming-binned Baldwin gap (bins {0, 1, 2, 3, ≥4}) — frozen vs plastic continuous fitness stratified by distance to canonical; GT-bypass individuals excluded from bins, counted separately
- Final δ_final values for 5 best-of-run winners per cell — threshold-saturation guard (especially for budget=5 cells; flag if |δ_final| ≥ 5 in > 50% of winners)
- `unique_genotypes` per cell — population diversity sanity
- Paired-seed `F_AND_test(plastic) − F_AND_test(frozen)` distribution — paired McNemar input (Arm A cells only; BP_TOPK is exploratory)

## Scope tag (required for any summary-level claim)

**If this experiment PASSes (Arm A confirmatory cells), the new findings.md candidate enters scoped as:**
`within-family · n=20 per cell (4 confirmatory Arm A cells at budget ∈ {1, 2, 3, 5}) · at Arm A (direct GP) pop=512 gens=1500 mr=0.03 tournament_size=3 elite_count=2 disable_early_termination=true · on sum_gt_10_AND_max_gt_5 natural sampler with 75/25 train/test split · plasticity_mechanism=rank1_op_threshold, plasticity_delta=1.0, plasticity_budget ∈ {1, 2, 3, 5} · seeded canonical 12-token AND body at sf=0.01 · non-GT-bypass subset of final population · per-tape mutation budget matched (gens × mr = 45) to §v2.4-proxy-4c Arm A frozen baseline; total-population budget is halved by the pop reduction from 1024 → 512 and this mismatch is acknowledged, not corrected`.

Explicitly not-broadening to: BP_TOPK (co-registered as exploratory — substitute-vs-complement finding requires a separate confirmatory prereg); other task families (not tested); rank-2 or deeper plastic mechanisms (not tested); GT-bypass circuits (excluded from scope by design).

## Decision rule

- **PASS — Baldwin (Arm A) →** (1) promote candidate to findings.md as a NEW entry `plasticity-narrow-plateau` with ACTIVE status and the scope tag above; (2) escalate the plasticity direction: queue §v2.5-plasticity-1b (rank-2 memory shortcut); (3) read the BP_TOPK exploratory cells from this same sweep — if BP_TOPK shows small lift (substitute signal), write up the differential as a follow-on confirmatory prereg; if BP_TOPK shows comparable lift (complement signal), that changes the escalation priority. The BP_TOPK data is already in hand from this sweep — no separate follow-up needed to get the differential.
- **PARTIAL — universal adapter →** do NOT promote to findings.md (not a positive mechanism claim). The {1, 2, 3, 5} budget grid already includes the small-capacity cells; if Baldwin signal emerges only at budget=1 or budget=2 and disappears at budget=3 and budget=5, report as a capacity-boundary finding. If no budget yields a Baldwin signature, the rank-1 mechanism is fundamentally too expressive for this task; write up as a negative mechanism-layer finding.
- **FAIL — weak plasticity →** do NOT promote. Try the rank-2 (memory) mechanism per the plasticity-direction doc's fallback ladder before concluding plasticity does not help Arm A.
- **INCONCLUSIVE — frozen wins →** STOP and inspect. Likely an engineering bug in the plastic adaptation rule. Do not run additional plasticity sweeps until the code is validated on a minimal synthetic case.
- **INCONCLUSIVE — mid F_test →** run n=20 independent-seed replication at the best-performing budget (seeds 20-39). Do not claim until the replication lands.
- **SWAMPED — train fails →** engineering bug. Stop and inspect.
- **INCONCLUSIVE (grid-miss) →** update the grid per principle 2b before interpreting.

---

*Audit trail.* Nine Arm A outcome rows + four BP_TOPK exploratory rows (principle 2 + 2b + 26). Baseline F_AND_test measured by the control cell in this sweep at per-tape-matched mutation budget (`gens=1500 × mr=0.03 × pop=512` → per-tape expected = 45, matching §v2.4-proxy-4c's per-tape expected = 45 exactly on the axis §v2.4-proxy-5b-amended identified as load-bearing); §v2.4-proxy-4c Arm A baseline numbers are context, the in-sweep control cell is the principle-6 anchor. Total-population budget is halved (768k vs 1.5M tape-gen steps) due to pop reduction from 1024 → 512; this mismatch is acknowledged, not corrected, per the plasticity-direction doc's pop=512 commitment. Internal control is plastic vs frozen on shared seeds (principle 1). Degenerate-success guard covers universal-adapter, train-test leakage, threshold saturation (revised for budget=5 boundary), GT-bypass artefact, δ-convergence artefact (principle 4). Principle 20 marginally triggered — class balance verified at sweep launch. Principle 22: Arm A Baldwin_slope CI is **confirmatory** founding `plasticity-narrow-plateau` FWER family at size 1 (α=0.05); BP_TOPK cells are **exploratory** (effect-size only). Principle 23 gate preserved — Arm A control cell reproduces §v2.4-proxy-4c baseline's per-tape mutation budget exactly at gens=1500; BP_TOPK control cell does NOT match budget (gens=500) and is acknowledged as exploratory-scope-only. Principle 25 and 27 both **blocked pending engineering**: `METRIC_DEFINITIONS` entries for `test_fitness_frozen`, `test_fitness_plastic`, `delta_convergence`, `GT_bypass_fraction`, `Baldwin_gap`, `Baldwin_slope`, `R_fit_frozen_999`, `R_fit_plastic_999` do not yet exist in code. Principle 26 satisfied — `GT_bypass_fraction` gridded as an explicit column (not silently demoted to diagnostic). 2026-04-18 revisions: budget grid changed from {3, 10} to {1, 2, 3, 5} to remove threshold-saturation confound at budget=10; Arm A gens set to 1500 (per-tape budget matches §v2.4-proxy-4c exactly; codex review caught an earlier gens=2250 draft that overshot per-tape budget to 67.5); BP_TOPK gens=500 exploratory. Decision rule updated: BP_TOPK data co-registered in this sweep, so substitute-vs-complement finding is available immediately (principle 19).

## Status-transition checklist (from QUEUED → RUNNING)

Before this prereg can move from QUEUED to RUNNING, all six engineering prerequisites above must be complete and committed. At that point:

1. Add a supersession note to this prereg's top ("Engineering landed at commit `X`; prereg now RUNNING").
2. Update `target commit` in the status line to the post-engineering commit short-SHA.
3. Re-verify that each METRIC_DEFINITIONS entry cited in "Pre-registered outcomes" matches the code verbatim (principle 27).
4. Run the pytest coverage added in step 6 of the engineering prereqs; attach pass confirmation.
5. Launch the sweep.
