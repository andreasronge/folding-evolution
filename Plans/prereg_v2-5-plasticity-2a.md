# Pre-registration: §v2.5-plasticity-2a — Arm A sf=0.0 seed-removal probe of P-1 diagnosis falsifiability (branching test for `selection-deception` vs rank-1-structural-mismatch)

**Status:** QUEUED · target commit `{short-sha, to be pinned when sweep launches}` · 2026-04-19

*This prereg follows from diagnosis `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` (class: `selection-deception` / "deception of learning-to-learn" — Risi & Stanley 2010). Escalation path is pre-committed; scope is restricted to the path identified there. This prereg enacts P-1 from §v2.5-plasticity-1a's Falsifiability block — the cheapest branching test that distinguishes "INVERSE-BALDWIN driven by static-canonical shortcut" (selection-deception, EES next) from "INVERSE-BALDWIN is intrinsic to rank-1 plasticity on this task" (rank-2 first; §29 class-4 diagnosis is refuted and a new 'mechanism-mismatched' class may be needed — see Decision rule).*

## Question (one sentence)

Under Arm A direct GP on `sum_gt_10_AND_max_gt_5` natural sampler with `seed_fraction=0.0` (canonical AND body removed from initial population), does rank-1 operator-threshold plasticity at `budget ∈ {1, 2, 3, 5}` reproduce the §v2.5-plasticity-1a INVERSE-BALDWIN pattern (positive slope CI-excluding-0 on positive side, δ_std growing monotone with budget), flip to a Baldwin-direction slope, produce a universal-adapter collapse, or produce a novel pattern the §1a grid does not anticipate?

## Hypothesis

The `selection-deception` diagnosis (§29 class 4) predicts that removing the canonical shortcut will allow plasticity to produce selection-layer uplift that was previously masked by canonical-elite preservation. Three pre-committed readings of the sf=0.0 data:

1. **BALDWIN-EMERGES.** Without the static shortcut, plasticity acquires selection-layer work: `F_AND_test` scales with budget (≥ 15/20 at some budget), OR Baldwin_slope cell-level 95% CI excludes 0 on the **negative** side at ≥ 1 budget if the regression is computable. Selection-deception is **supported**; §v2.5-plasticity-2b (EES) is the next leg.
2. **UNIVERSAL-ADAPTER.** `F_AND_test` ≥ 15/20 at some budget AND `δ_std` at budget=5 collapses to ≤ 1.5. Plasticity discovers canonical-equivalents via a convergent δ regardless of starting genotype; selection-deception is weakly supported but mechanism-name narrows to "canonical-is-recoverable-from-noise-if-shortcut-absent." EES candidate for confirmation.
3. **INVERSE-BALDWIN-REPLICATES.** `F_AND_test` < 5/20 at every budget AND `δ_std` at budget=5 > 2.0 AND (Baldwin_slope CI excl 0 on positive side at ≥ 3/4 budgets OR Baldwin_slope undefined). Selection-deception is **REFUTED**: the INVERSE-BALDWIN pattern is not driven by the canonical shortcut, it is intrinsic to rank-1-plasticity-on-this-task. Methodology consequence: §29's class-4 doesn't fit the §1a data and §29 is missing a class (call it `mechanism-mismatched`: capacity present but directed at the wrong part of the fitness landscape — cannot refine near-canonical because nothing useful to refine, works only in distant tail). Escalation pivots to **rank-2 memory** (§v2.5-plasticity-1b) before EES, because the correct fix is qualitatively different capacity (state history, per-example adaptation) rather than a selection-regime change.
4. **AMBIGUOUS-MARGINAL.** `F_AND_test` 5-14/20 at budget=5 OR (slope still positive but CI_hi at budget=5 < 0.04) — slope magnitude drops substantially vs §1a's [+0.0521, +0.0863] but stays positive. The mechanism is neither clearly selection-deception (insufficient Baldwin lift) nor clearly intrinsic (magnitude dropped). Decision: n-expansion to seeds 40..59 on best-signal budget, OR pivot to EES while rank-2 engineering runs in parallel.

Reading 3 (INVERSE-BALDWIN-REPLICATES) is the pre-committed null that would falsify P-1 and change the escalation ladder. Readings 1-2 support P-1; reading 4 is the designed "insufficient discrimination" bucket that forces replication before routing.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2a.yaml` (to be created)
- **Arms / conditions:** Arm A only (direct GP). BP_TOPK is EXCLUDED from this prereg per the §v2.5-plasticity-1a chronicle's caveat: BP_TOPK's R_fit structural ceiling prevents lift detection, and until a decoder-side probe lowers the ceiling (a §v2.4-proxy-5* sequel, not a plasticity experiment), BP_TOPK plasticity spend is under-informative. Arm A is where the plasticity spend is load-bearing.
  - **Plastic cells (confirmatory):** `arm=A, plasticity_enabled=true, plasticity_budget ∈ {1, 2, 3, 5}, seed_fraction=0.0, generations=1500, pop_size=512, mr=0.03, tournament_size=3, elite_count=2, crossover_rate=0.7, plasticity_mechanism=rank1_op_threshold, plasticity_delta=1.0, plasticity_train_fraction=0.75` × 4 budgets × 20 seeds = 80 runs
  - **Frozen control cell (principle-23 anchor):** `arm=A, plasticity_enabled=false, seed_fraction=0.0, generations=1500, pop_size=512, mr=0.03, tournament_size=3, elite_count=2` × 20 seeds = 20 runs. Establishes sf=0.0 frozen baseline on shared seeds for paired R_fit_999 delta.
  - **Bridging cell (exploratory, Baldwin_slope regression support check):** `arm=A, plasticity_enabled=true, plasticity_budget=5, seed_fraction=0.01, generations=1500` on disjoint seeds (20..39) × 1 cell × 20 seeds = 20 runs. Tests whether §1a's positive-slope CI at budget=5 sf=0.01 **replicates on disjoint seeds**. Not confirmatory (no FWER growth — §v2.5-plasticity-1a's size-1 family is closed); exploratory for internal consistency. Saves downstream "was §1a a seed-block artifact?" concern.
- **Seeds:** 20..39 on all cells — **disjoint from §v2.5-plasticity-1a's seeds 0..19**, per principle 8 independent-seed-confirmation discipline.
- **Fixed params:** pop=512, gens=1500, mutation_rate=0.03, crossover_rate=0.7, tape_length=32, n_examples=64, alphabet=v2_probe, task=sum_gt_10_AND_max_gt_5, disable_early_termination=true, dump_final_population=true, backend=mlx, plasticity_mechanism=rank1_op_threshold, plasticity_delta=1.0, plasticity_train_fraction=0.75, holdout_size=256. Arm A plastic cells: `seed_tapes=None` (no canonical seeding under sf=0.0); frozen control: `seed_tapes=None` ditto; bridging cell: `seed_tapes=canonical 12-token AND body` (identical to §1a).
- **Est. compute (post-evaluate-loop optimization committed `b1eab3c`, 2.18× wall speedup on pop=128×gens=100 profile, extrapolating to ~2.4-2.7× at full scale):** 80 plastic runs × ~2.3 min/run at budget=5 (scaled from §1a's 7 min/run pre-optimization) ≈ 180 min; 20 frozen runs × ~1.5 min/run ≈ 30 min; 20 bridging runs × ~2.3 min/run ≈ 45 min. Parallel at 10 workers: total wall ≈ 30-45 min. Well under the §1a 6-hour first-pass. Full sweep with headroom: 90-min queue timeout is conservative.
- **Related experiments:** §v2.5-plasticity-1a (primary predecessor — the INVERSE-BALDWIN pattern this prereg tests the diagnosis of); `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` (the diagnosis this prereg enacts P-1 for); §v2.4-proxy-4c Arm A baseline (commit `9135345` — per-tape mutation budget reference).

**Principle 17a audit (multi-variable confound disclosure).** The prereg varies `plasticity_budget ∈ {1, 2, 3, 5}` × `seed_fraction ∈ {0.0, 0.01}` (bridging). Derived process variables that change across cells:
- **plasticity_budget axis:** (a) max |δ_accumulated| per tape = budget × 1.0 at budget=5 vs 1.0 at budget=1; (b) adaptation-step count per evaluation = up to budget; (c) per-evaluation Python VM work = linear in budget. All three are co-moving and expected — the budget axis is the mechanism-capacity axis by design.
- **seed_fraction axis:** (d) initial-canonical count = `floor(pop × sf)` = 0 at sf=0.0, 5 at sf=0.01; (e) initial-population Hamming-to-canonical distribution shifts; (f) elite slot's initial capture of canonical is structurally different (no canonical to capture at sf=0.0; canonical always present at sf=0.01). Three variables move on the sf axis. The outcome rows explicitly name the sf=0.0 regime (no canonical in init); no "shortcut strength" continuous claim is made, only the discrete sf=0.0 vs sf=0.01 contrast. Principle-17b tested-set qualifier applied.

**Principle 20 audit (sampler design).** Sampler is unchanged from §v2.5-plasticity-1a: the natural sampler for `sum_gt_10_AND_max_gt_5` (64 inputs, 48 train × 16 test per the 0.75 train_fraction split). No change to the training distribution; principle 20 not triggered.

**Principle 23 audit (execution fidelity, chronicle-time mirror).** Frozen control at sf=0.0 must reproduce the §v2.5-plasticity-1a frozen-Arm-A-sf=0.01 R_fit_999 infrastructure behavior (pop=512, gens=1500, mr=0.03, per-tape mutation budget = 45) — differing ONLY in the sf axis. At sf=0.0 the expected R_fit_999 is close to 0 (no canonical to seed); any substantial R_fit at frozen sf=0.0 would indicate the population discovered canonical-equivalents without seeding, which is informative about the baseline regime and should be logged as a §25 anchor check.

## Baseline measurement (required)

- **Baseline quantity 1 — frozen Arm A sf=0.0 R_fit_999 at pop=512, gens=1500, mr=0.03:** must be measured in-sweep by the frozen control cell on seeds 20..39. Expected close to 0 (§v2.5-plasticity-1a drift cell frozen sf=0.0 best-fitness F_AND_test = 3/20 at pop=512 gens=1500 with no budget; R_fit_frozen_999 was 0.000 in the §1a drift cell summary). Measured value is the paired-seed anchor for plastic ΔR_fit at sf=0.0.
- **Baseline quantity 2 — §v2.5-plasticity-1a drift cell (frozen Arm A sf=0.0 budget=5):** from §1a output `experiments/output/2026-04-19/v2_5_plasticity_1a/plasticity_summary.json`: F_AND_test = 3/20, F_AND_train = 0/20, R_fit_plastic at budget=5 = 0.035 (single data point — no budget sweep in §1a drift). This prereg adds 4 budget points at sf=0.0 on disjoint seeds.
- **Baseline quantity 3 — §1a Arm A budget=5 sf=0.01 cell (for bridging-cell replication):** Baldwin_slope cell-level 95% CI (seed-bootstrap) = `[+0.0521, +0.0863]`; R_fit_plastic_999 mean = 0.088; δ_mean = −2.81, δ_std = 2.67. Bridging cell on seeds 20..39 should reproduce within-CI; a major divergence would flag a §1a seed-block artifact.

**Metric definitions (principle 27).** All metrics cited from `experiments/chem_tape/analyze_plasticity.py:METRIC_DEFINITIONS` (imported verbatim — see §v2.5-plasticity-1a chronicle). The `Baldwin_slope` definition specifically requires a non-GT-bypass subpopulation with variance in Hamming-to-canonical distance; at sf=0.0 this may be degenerate (see measurement-infrastructure gate below).

**Measurement-infrastructure gate (principle 25) — known risk at sf=0.0.** `analyze_plasticity.py:linreg_slope` returns nan when x-variance = 0 (all non-GT-bypass individuals in a single Hamming bin). §v2.5-plasticity-1a's drift cell (Arm A sf=0.0 budget=5) already produced nan slope: every non-GT-bypass individual sat at Hamming ≥ 4 (no h<4 subpopulation emerged under random init + 1500 gens). **It is therefore likely that some or all sf=0.0 plastic cells will produce undefined Baldwin_slope in this prereg.** To keep the prereg's confirmatory test meaningful, the outcome grid below uses a **composite confirmatory axis** (F_AND_test scaling + δ_std scaling + Baldwin_gap-at-h≥4 magnitude) that remains computable when the slope is nan. The Baldwin_slope is reported when defined as a secondary signal; it is NOT load-bearing for row-matching at sf=0.0.

**METRIC_DEFINITIONS extensions for this prereg (added at engineering-commit time):**
- `baldwin_gap_h_ge4_cell_mean`: already emitted by `analyze_plasticity.py` (per-cell mean of `Baldwin_gap_h_ge4` across seeds); proposed as the sf=0.0 confirmatory axis substitute for `Baldwin_slope`. The scaling of this quantity with budget replaces the slope-sign criterion.
- `F_AND_test_count`: count of 20 seeds where best-of-run test fitness ≥ 0.999. Already emitted per-seed in `plasticity.csv` via `best_fitness_test_plastic`; per-cell aggregation added to `summarize` function.
- `paired_R_fit_delta_sf0` (new): paired per-seed `R_fit_plastic_999(bud) − R_fit_frozen_999(frozen_control)` at sf=0.0. Requires the frozen control cell to share seeds 20..39 with the plastic cells. `analyze_plasticity.py` does NOT currently emit this; adding a post-hoc CSV cross-cell merge script is the principle-25 extension needed before the chronicle can land. Effort: ~30 min.

## Internal-control check (required)

- **Tightest internal contrast:** paired plastic(sf=0.0, budget=b) vs frozen(sf=0.0, no plasticity) on shared seeds 20..39 at every budget. Directly tests "does plasticity do work at sf=0.0" without the confound of the canonical-shortcut being present.
- **Secondary internal contrast:** cross-prereg within-family on the bridging cell — plastic(sf=0.01, budget=5) seeds 20..39 vs §v2.5-plasticity-1a's plastic(sf=0.01, budget=5) seeds 0..19. Tests whether §1a's confirmatory signal replicates on a disjoint seed block (exploratory, not a new confirmatory family member).
- **Are you running it here?** Yes — both contrasts are present.

## Pre-registered outcomes (required — at least three; §26 grid across measured axes)

<!--
Per principle 2b + 26: axes measured at per-seed resolution each get a coarse-bin row.
Three measured axes — all load-bearing at sf=0.0:
  - F_AND_test @ budget=5 (primary; plastic discovery from noise): {≥15/20 recovered | 5-14/20 partial | <5/20 not-recovered}
  - δ_std @ budget=5: {collapse ≤0.5 | flat [0.5, 1.5] | grows >2.0}
  - Baldwin_gap_h_ge4 @ budget=5 (secondary; replaces Baldwin_slope when slope is nan): {near-zero ≤0.05 | moderate (0.05, 0.15] | large >0.15 — §1a observed 0.260}

Baldwin_slope (per §1a): reported when defined (non-degenerate x-variance); NOT load-bearing for row-matching — {negative CI excludes 0 | flat CI includes 0 | positive CI excludes 0 | undefined/nan}
-->

**Arm A outcome grid (confirmatory — `plasticity-narrow-plateau` FWER family remains CLOSED at size 1 per §1a; this prereg's test is a SEPARATE confirmatory family `plasticity-inverse-baldwin-replicates` opening at size 1 with corrected α = 0.05, per principle-22a per-sweep counting):**

| # | outcome | F_AND_test@bud=5 | δ_std@bud=5 | Baldwin_gap_h≥4@bud=5 | Baldwin_slope (if defined) | interpretation / routing |
|---|---------|-------------------|--------------|--------------------|-----------------------------|--------------------------|
| 1 | **BALDWIN-EMERGES** | ≥ 15/20 | any | any | negative CI excl 0 ≥ 1 budget (if defined) | Plasticity recovers canonical-equivalents without the static shortcut; selection-deception diagnosis **SUPPORTED**. Next leg: §v2.5-plasticity-2b (EES) as the primary class-4 follow-up; rank-2 deferred. Findings.md `plasticity-narrow-plateau` NULL narrows: the NULL was shortcut-specific, not a universal rank-1 null. |
| 2 | **UNIVERSAL-ADAPTER** | ≥ 15/20 | ≤ 1.5 | any | flat or near-zero | Plastic discovery from noise via convergent δ. Selection-deception diagnosis supported weakly — the mechanism is "δ does the work, genotype irrelevant" rather than "genotype encodes learnable circuit." EES candidate; rank-2 deferred. Findings.md `plasticity-narrow-plateau` narrows to "NULL under seeded canonical; discovers canonical-equivalents under no-shortcut." |
| 3 | **INVERSE-BALDWIN-REPLICATES** (PRE-COMMITTED FALSIFIER for P-1) | < 5/20 | > 2.0 | > 0.15 | positive CI excl 0 at ≥ 3/4 budgets (if defined) OR undefined | Selection-deception diagnosis **REFUTED**. Pattern is intrinsic to rank-1 plasticity on this task, not shortcut-induced. Methodology consequence: (a) §29 class-4 does not fit the §1a data; a new `mechanism-mismatched` class is needed (capacity present but directed at wrong landscape region) — a methodology amendment proposal follows this chronicle. (b) Escalation pivots to **rank-2 memory (§v2.5-plasticity-1b) FIRST**, ahead of EES. (c) Findings.md `plasticity-narrow-plateau` NULL broadens: rank-1 mismatch is task-structural, not selection-structural. |
| 4 | **AMBIGUOUS-MARGINAL** | 5-14/20 OR (F<5/20 AND δ_std>2.0 AND Baldwin_gap_h≥4 < 0.15) OR (slope defined + positive + CI_hi@bud=5 < 0.04) | any | any | any | Neither clear support nor clear refutation. Decision: n-expansion to seeds 40..59 at best-signal budget before routing; OR parallel pursuit of EES AND rank-2 engineering while n-expansion runs. Timeline cost ≈ 2-3 hours compute. |
| 5 | **FAIL — universal-null-at-sf=0.0** | < 5/20 | ≤ 1.5 | < 0.05 | flat or undefined | Rank-1 plasticity does NOT do measurable work at sf=0.0 either. Both selection-deception (didn't help without shortcut) AND rank-1-intrinsic-tail-effect readings are weakened. Rank-1 is likely the wrong mechanism altogether for this task; EES unlikely to help (no capacity to redirect); rank-2 the cleaner candidate but under a different rationale (fill an empty mechanism bag, not fix a directed one). |
| 6 | **SWAMPED — train fails** | F_AND_train < 15/20 at any seeded cell OR frozen control's F_AND diverges from §1a drift baseline (3/20 → any of {0/20, ≥8/20} is suspicious) | any | any | any | Infrastructure or task-baseline bug. Stop and inspect. (Differs from §1a's SWAMPED: seeded canonical is ABSENT here, so F_AND_train depends on discovery — a low value is plausible under class 1/2/3 above. The SWAMPED flag here targets the frozen control specifically; if frozen F behaves unexpectedly, the principle-23 anchor is broken.) |
| 7 | **INCONCLUSIVE — grid-miss catchall** | Any pattern not fitting rows 1-6 | — | — | — | Per principle 2b, update the grid before interpreting. Do NOT route to EES or rank-2 until the new pattern has a formal row in a follow-up prereg. |

**Bridging cell outcome (exploratory — no FWER growth):**

The plastic(sf=0.01, budget=5) seeds 20..39 cell compares to §1a's Baldwin_slope CI = `[+0.0521, +0.0863]`. Report-only states: `REPLICATES` (seeds 20..39 CI overlaps `[+0.0521, +0.0863]`), `WEAKENS` (CI_hi drops below +0.04), `STRENGTHENS` (CI_lo rises above +0.08), `FLIPS` (CI excludes 0 on negative side). No routing change is gated on this cell — it is a read-only internal-consistency check on §1a's confirmatory signal.

**Row-clause fidelity (principle 28a pre-commitment).** Row 3 (INVERSE-BALDWIN-REPLICATES) requires ALL four sub-clauses: F_AND_test < 5/20 AND δ_std > 2.0 AND Baldwin_gap_h≥4 > 0.15 AND (slope positive at ≥ 3/4 budgets if defined, OR undefined). Prose-match with any sub-clause failing = grid-miss (row 7), NOT a row-3 match. This protects against the §1a-precedent "INVERSE-BALDWIN pattern" being read-in from partial evidence.

**Threshold justifications:**
- **F_AND_test ≥ 15/20 (row 1):** same threshold as §1a PASS-Baldwin's F criterion; preserves cross-sweep comparability.
- **F_AND_test < 5/20 (rows 3, 4, 5):** §1a drift cell at sf=0.0 budget=5 F_AND_test = 7/20 plastic (current signal); to claim INVERSE-BALDWIN-REPLICATES we need to be *below* that level (plastic discovery fails to scale with budget removal of elite canonical advantage). 5/20 is a 2× drop from the 10/20 midpoint — a meaningful threshold for "plasticity does not do work."
- **δ_std > 2.0 at budget=5 (row 3):** §1a observed 2.67 at sf=0.01 budget=5 and 2.53 at sf=0.0 budget=5 drift. The 2.0 threshold is the §1a minimum observed — a substantive drop below that signals different mechanism behavior.
- **δ_std ≤ 1.5 at budget=5 (row 2, 5):** §1a never observed δ_std < 1.5 at budget=5; a drop to ≤ 1.5 is a qualitative shift (mechanism capacity saturating differently).
- **Baldwin_gap_h≥4 > 0.15 (row 3):** §1a observed 0.260 at sf=0.01 budget=5 and 0.284 at sf=0.0 budget=5 drift. 0.15 is roughly half that — a substantive-but-not-quite-§1a-level magnitude, deliberately loose to catch replications that are somewhat weaker but still directionally correct.
- **CI_hi@bud=5 < 0.04 (row 4):** the pre-committed "slope magnitude drops substantially" falsifier from the conversation that produced this prereg — below half of §1a's CI lower bound (+0.052 → 0.04).

## Degenerate-success guard (required)

Six guards inherited from §v2.5-plasticity-1a (with sf=0.0-specific adjustments):

1. **Universal-adapter artefact (row 2).** If F_AND_test ≥ 15/20 at every budget with δ_std ≤ 1.5 at every budget, plasticity is acting as a universal canonical-recovery mechanism independent of genotype. Detection: compute per-seed Hamming-to-canonical of the top-1 winner at each budget; if ≥ 75% of winners are at h=0 (exact canonical) regardless of budget, the mechanism is "plasticity-enables-random-search-to-find-canonical" not "plasticity-refines-learnable-circuits." Report as UNIVERSAL-ADAPTER (row 2), not BALDWIN-EMERGES (row 1).
2. **Train-test leakage (universal).** Same as §1a guard 2. Compute `F_AND_test − F_AND_train` per seed; suspicious near-zero gap at high budget combined with high plastic discovery flags leakage. Under sf=0.0 this manifests as "plastic discovery on train but frozen evaluation on test matches exactly" — improbable under correct semantics.
3. **Threshold-saturation artefact (budget=5 cell, population and top-1-winner split — lesson from §1a codex review).** Report **both** population-level and top-1-winner |δ_final| ≥ 5 fractions at budget=5. §1a drift showed 0.738 population + 14/20 top-1 winners at |δ|≥5 under sf=0.0 budget=5 — under this prereg's pre-committed design, if row 3 (INVERSE-BALDWIN-REPLICATES) fires, the threshold-saturation guard is NOT discharged on the top-1-winner axis (winners saturating confirms "plasticity IS doing work in the winners, not just the tail"), which is a **different** signature from §1a's sf=0.01 top-1 = 0/20. Flag this cross-condition asymmetry explicitly.
4. **GT-bypass artefact.** Same as §1a. GT_bypass_fraction ≥ 0.50 at any cell → row 7 (grid-miss with INCONCLUSIVE-GT-bypass-majority sub-tag).
5. **δ-convergence artefact (universal-adapter in δ-space).** Same as §1a guard 5. If δ_std at budget=5 collapses to ≤ 0.5 across seeds (all winners using near-identical δ), the mechanism is convergent-δ-with-any-genotype; report as UNIVERSAL-ADAPTER regardless of F_AND_test.
6. **Adaptation-budget-too-high at budget=5.** Inherits from §1a guard 6. Population-level |δ|≥5 fraction at budget=5 is expected to be substantial (§1a sf=0.0 observed 0.738); the budget-saturation phenomenon itself is not a guard failure, but if budget=3 also shows |δ|=3 saturation in > 50% of population (impossible under δ=1 × 3 steps unless a coding bug allows larger steps), the test is broken. Sanity assertion: max |δ_final| at budget=b is exactly b × δ = b × 1 = b; any value greater than b is an infrastructure bug.

**New guard specific to sf=0.0 (guard 7 — no-canonical-in-init invariant).** Verify via `history.npz:initial_population_canonical_count` OR post-hoc inspection of generation-0 population: the seeded canonical 12-token AND body must NOT appear in the initial population at sf=0.0. If it does (via random-init luck or seed-tape mis-handling), the sf=0.0 condition is compromised for those seeds and they must be excluded from analysis. Expected: 0 canonical in gen-0 across all 80 plastic + 20 frozen runs (random 32-byte tapes × 4-bit encoding has negligible probability of generating canonical 12-token AND body).

## Statistical test (principle 22)

- **Primary confirmatory test:** per-cell **seed-bootstrap 95% CI on `Baldwin_gap_h≥4` per budget** (10 000 resamples via `numpy.random.default_rng(seed=42)` per `bootstrap_ci_spec`). This replaces §1a's Baldwin_slope CI as the confirmatory axis when slope is undefined at sf=0.0. Row 1 (BALDWIN-EMERGES) requires Baldwin_gap_h≥4 CI to include values ≤ 0 OR F_AND_test ≥ 15/20; row 3 (INVERSE-BALDWIN-REPLICATES) requires Baldwin_gap_h≥4 CI strictly > 0.15.
  - **Secondary diagnostic:** per-cell seed-bootstrap 95% CI on `R_fit_plastic_999 − R_fit_frozen_999_control` at each budget, paired on seeds 20..39. Confirmatory-family-adjacent but not promoted to confirmatory (per principle-22a per-sweep counting, adding this as a second family member would mean α = 0.025/test; using it as effect-size-only keeps the family at size 1).
- **Classification:** **confirmatory.** This prereg gates the diagnosis-routing decision for §v2.5-plasticity-1a's INVERSE-BALDWIN pattern — P-1's verdict determines whether EES or rank-2 comes next.
- **Family:** NEW — `plasticity-inverse-baldwin-replicates`. Family size at this prereg = 1 (first confirmatory test in the family). Corrected α = 0.05 / 1 = 0.05. If INVERSE-BALDWIN-REPLICATES (row 3) fires, a follow-up rank-2 sweep entering as a confirmatory test would grow the family to size 2. The §1a family `plasticity-narrow-plateau` is distinct (closed at size 1 with null recorded) and does NOT merge into this family — the two families test different claims (the NULL vs the diagnosis-falsifier).
- **Per-sweep test counting (principle 22a):** 4 plastic budget cells × 1 test-per-cell = 4 test instances for the Baldwin_gap_h≥4 confirmatory axis. However, the OUTCOME GRID aggregates these into row-match verdicts rather than per-cell α-gates (a single grid-match is the confirmatory claim, not four independent claims). Per principle-22a, this prereg **explicitly classifies as 1 confirmatory test** (the grid-match verdict), with the 4 per-cell Baldwin_gap_h≥4 CIs serving as grid-input sub-statistics. If a future audit counts this differently, the per-sweep counting block must be amended before rechronicle.

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_AND_train`, `F_AND_test` (best-of-run, binary), `R_fit_frozen_999`, `R_fit_plastic_999`.
- Per-individual `test_fitness_frozen`, `test_fitness_plastic`, `delta_final`, `has_gt` → `final_population.npz` via existing `evaluate_population_plastic` full-metric path on the final-generation dump.
- Per-cell `GT_bypass_fraction`, `Baldwin_gap` by Hamming bin {0, 1, 2, 3, ≥4}, `Baldwin_slope` (if defined; nan logged transparently if not).
- Per-cell `std(delta_final)` stratified by Hamming bin — universal-adapter diagnostic.
- Per-cell bootstrap 95% CI on `Baldwin_gap_h≥4` (seed-level; the primary confirmatory statistic at sf=0.0).
- Per-cell bootstrap 95% CI on `R_fit_plastic_999 − R_fit_frozen_999` paired on shared seeds.
- Per-cell `|δ_final| ≥ 5` fraction at budget=5 — both population and top-1-winner split (from §1a codex-review lesson).
- Per-cell best-of-run hex for top-1 winner at each seed — attractor inspection input for row-1 / row-2 distinction.
- Per-seed `initial_population_canonical_count` in gen-0 — guard 7 (no-canonical-in-init invariant).
- Per-cell bootstrap 95% CI on `Baldwin_slope` when defined; marked "nan (degenerate-x-variance)" when undefined — the §25 disclosure made explicit.

## Scope tag (required for any summary-level claim)

**If this experiment produces row 1 (BALDWIN-EMERGES) or row 2 (UNIVERSAL-ADAPTER):** the `plasticity-narrow-plateau` findings.md NULL narrows from "rank-1 does NOT narrow the basin at tested regime" to "rank-1 does NOT narrow the basin under seeded canonical AT sf=0.01; DOES narrow / recover under sf=0.0 — selection-deception diagnosis confirmed." The scope tag on the narrowed claim:
`within-task-family · n=20 per cell × 4 confirmatory Arm A sf=0.0 plastic budgets + 1 frozen-sf=0.0 control · at Arm A (direct GP) pop=512 gens=1500 mr=0.03 tournament_size=3 elite_count=2 · on sum_gt_10_AND_max_gt_5 natural sampler with 75/25 train/test split · rank1_op_threshold mechanism δ=1.0 budget ∈ {1,2,3,5} · random initial population (sf=0.0)` plus the existing §1a scope.

**If this experiment produces row 3 (INVERSE-BALDWIN-REPLICATES):** the `plasticity-narrow-plateau` NULL broadens: "rank-1 does NOT narrow the basin at tested regime EVEN UNDER sf=0.0 — pattern is intrinsic to rank-1-on-this-task, not shortcut-induced." The scope tag: same as above but with the selection-deception diagnosis explicitly retracted and a new `mechanism-mismatched` methodology-class-gap flag in the findings.md entry.

Explicitly NOT-broadening to (in all outcome cases): other tasks (cross-task probe §v2.5-plasticity-2c remains open for P-3); rank-2 or deeper mechanisms (still untested); other selection regimes (EES is a separate leg); other δ values; other plasticity_train_fraction values. Principle 17b: tested integer budget values ∈ {1, 2, 3, 5}, not `≤ 5` continuous range.

## Decision rule

The pre-committed routing decision by row:

- **Row 1 (BALDWIN-EMERGES) →** Narrow `plasticity-narrow-plateau` NULL in findings.md as above; queue §v2.5-plasticity-2b (EES) as confirmatory leg for the selection-deception diagnosis. Rank-2 deferred (class-4 supported, so class-2 not invoked). Mechanism-name budget: new name "rank-1-plasticity-selection-deception-by-canonical-shortcut" for the chronicle, subject to §16-cycle renaming.
- **Row 2 (UNIVERSAL-ADAPTER) →** Narrow findings.md as above; queue §v2.5-plasticity-2b (EES) with an additional axis testing whether EES preserves the convergent-δ behavior or unlocks per-genotype δ variation. Rank-2 deferred. Mechanism-name budget: "rank-1-plasticity-canonical-recovery-from-noise-under-convergent-δ."
- **Row 3 (INVERSE-BALDWIN-REPLICATES) →** The pre-committed falsifier for P-1 fires. Three actions: (a) submit a methodology amendment proposal adding `mechanism-mismatched` as §29 class 5 (capacity present but directed at wrong landscape region); (b) update `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` with an amended diagnosis doc citing the new class — the class-4 selection-deception reading is retracted per principle 13; (c) queue §v2.5-plasticity-1b (rank-2 memory) as the next escalation with the new class as the prereg-reference-pattern clause, citing "mechanism-mismatched" rather than "mechanism-weak." EES becomes a secondary leg, not primary — or deferred entirely if rank-2 produces a clean Baldwin signature. Findings.md `plasticity-narrow-plateau` broadens to "rank-1 mismatch is task-structural."
- **Row 4 (AMBIGUOUS-MARGINAL) →** n-expansion on seeds 40..59 at the highest-signal budget (probably budget=5) — 20 additional runs, ~45 min compute. Re-analyze pooled n=40 result; re-evaluate against rows 1-5 and re-route accordingly. Do NOT route to EES or rank-2 until the expanded result lands. Parallel rank-2 engineering may START (it's a 3-5 day job) but no sweep queues until the row-verdict is clear.
- **Row 5 (FAIL — universal-null-at-sf=0.0) →** Both diagnoses refuted: neither class-4 selection-deception (plasticity doesn't help even without shortcut) nor class-2 mechanism-weak (exercised capacity exists in §1a evidence). This is a third methodology gap: rank-1 plasticity is likely the wrong mechanism **and the wrong selection regime is irrelevant**. Queue §v2.5-plasticity-1b (rank-2) with weaker-motivation priority — the hypothesis becomes "rank-2 memory adds the missing capacity that rank-1 lacked, under either selection regime." EES unlikely to help (no directed capacity to redirect). Methodology: add a fourth rejection case to the diagnosis doc.
- **Row 6 (SWAMPED) →** Stop. Inspect the frozen control cell's infrastructure. Do not commit the chronicle until the anchor check passes.
- **Row 7 (INCONCLUSIVE — grid-miss catchall) →** Per principle 2b, update the outcome grid BEFORE interpreting. Propose a new row in a follow-up prereg; the current sweep chronicles as INCONCLUSIVE-grid-miss without routing.

**Mechanism-name rename budget (principle 16).** This prereg's outcome routing allocates one renaming cycle per positive row (1, 2, 3). The new name is committed in the chronicle, subject to §16-cycle renaming after any subsequent experiment. No renaming is pre-emptive; all names are working-hypothesis scoped.

## Audit trail

- **Principle 1 (internal controls first):** plastic-vs-frozen on shared seeds at sf=0.0 is the tightest internal contrast; it runs in-sweep. Cross-task external validity is deferred to §v2.5-plasticity-2c (P-3).
- **Principle 2 + 2b (≥3 outcomes, grid for ≥2 axes):** 7 rows enumerated across F_AND_test × δ_std × Baldwin_gap_h≥4 cross-product; row-3 pre-committed as P-1 falsifier per the conversation that produced this prereg.
- **Principle 4 (degenerate-success):** 7 guards enumerated (six from §1a + guard 7 no-canonical-in-init specific to sf=0.0).
- **Principle 6 (baseline-relative thresholds):** F_AND_test thresholds anchored to §1a drift (3-7/20 reference); δ_std thresholds anchored to §1a observed (2.0 floor / 1.5 qualitative-shift); Baldwin_gap_h≥4 anchored to §1a observed 0.260 (loose 0.15 threshold).
- **Principle 17a (multi-variable confound disclosure):** budget axis (3 derived variables co-moving) and sf axis (3 derived variables co-moving) both enumerated and scoped.
- **Principle 17b (tested-set qualifier discipline):** budget values ∈ {1, 2, 3, 5} tested integer set; sf ∈ {0.0, 0.01} discrete contrast; no continuous-range smuggling.
- **Principle 20 (sampler design):** sampler unchanged from §1a; not triggered.
- **Principle 22 + 22a (FWER + per-sweep counting):** confirmatory; new family `plasticity-inverse-baldwin-replicates` size 1; the 4 per-cell Baldwin_gap CIs classified as grid-input sub-statistics under the single grid-match confirmatory test — pre-committed per 22a.
- **Principle 23 (execution fidelity):** frozen-control-at-sf=0.0 is the sweep-internal anchor; pop/gens/mr byte-identical to §1a sf=0.01 frozen control except for the sf axis.
- **Principle 25 (measurement infrastructure):** disclosed degenerate-x-variance risk for Baldwin_slope at sf=0.0; substituted Baldwin_gap_h≥4 as the confirmatory statistic; flagged one infra extension (paired_R_fit_delta cross-cell merge — ~30 min effort) to complete before sweep launches.
- **Principle 26 (grid every measured axis):** F_AND_test, δ_std, Baldwin_gap_h≥4 all coarse-binned; Baldwin_slope reported when defined but NOT gridded (axis is infrastructure-dependent and graceful-degraded to secondary).
- **Principle 27 (METRIC_DEFINITIONS cited verbatim):** imported from §v2.5-plasticity-1a; new METRIC_DEFINITIONS entry for `paired_R_fit_delta_sf0` must land in `analyze_plasticity.py` before sweep; status: pending.
- **Principle 28a/b/c (row-match / guard / status-line fidelity):** row 3 requires all four sub-clauses satisfied; guard 7 covers the sf=0.0-specific no-canonical-in-init failure mode; status-line qualifier discipline applies at chronicle time.
- **Principle 29 (diagnose-before-escalate):** the diagnosis doc exists (`Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md`); this prereg's Setup section cites it verbatim; escalation-path-pre-committed clause honored.

## Status-transition checklist (QUEUED → RUNNING)

Before this prereg can move from QUEUED to RUNNING:

1. Engineering: add `paired_R_fit_delta_sf0` METRIC_DEFINITIONS entry + cross-cell merge logic to `analyze_plasticity.py`. Effort: ~30 min.
2. Engineering: verify `seed_tapes=None` + `seed_fraction=0.0` behavior in `evolve.py` `build_initial_population` — confirm no canonical is inserted. Pytest coverage already exists for `plasticity_enabled=False` byte-identity; add an assertion that `sf=0.0 → 0 canonical in gen-0` via `tests/test_chem_tape_plasticity.py`. Effort: ~20 min.
3. Write sweep YAML `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2a.yaml` matching Setup section exactly (80 plastic + 20 frozen + 20 bridging = 120 runs).
4. Add to queue.yaml with a 90-min timeout (generous headroom over expected 45-min wall).
5. Pin target commit short-SHA in Status line above.
6. Codex adversarial review of this prereg (the research-rigor prereg-mode step; pre-sweep). Expected foci: row-3 pre-committed falsifier threshold defensibility, methodology-gap proposal for `mechanism-mismatched`, guard 7 coverage, per-sweep test-counting classification under principle 22a.

## References

- `Plans/prereg_v2-5-plasticity-1a.md` — primary predecessor prereg (rank-1 plasticity at sf=0.01).
- `docs/chem-tape/experiments-v2.md#v2.5-plasticity-1a` — the INVERSE-BALDWIN chronicle (grid-miss verdict, §29 class-4 diagnosis).
- `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` — the diagnosis doc this prereg enacts P-1 for.
- `docs/methodology.md` — §§1, 2, 2b, 4, 6, 17a, 17b, 20, 22, 22a, 25, 26, 27, 28a/b/c, 29.
- `experiments/chem_tape/analyze_plasticity.py` — METRIC_DEFINITIONS source (principle 27 verbatim anchor).
- `docs/chem-tape/runtime-plasticity-direction.md` — direction doc (rank-1 → rank-2 ladder, now modified by the §29 class-4 branching).
- Risi, S. & Stanley, K. O. (2010). "Evolving Plastic Neural Networks with Novelty Search." *Adaptive Behavior* 18(6), 470-491 — literature anchor for class-4 `selection-deception`.
