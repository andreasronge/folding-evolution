# Pre-registration: §v2.5-plasticity-2a — Arm A sf=0.0 seed-removal probe of P-1 diagnosis falsifiability (branching test for `selection-deception` vs rank-1-structural-mismatch)

**Status:** QUEUED (v2, amended) · target commit `{short-sha, to be pinned when sweep launches}` · 2026-04-19

*This prereg follows from diagnosis `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` (class: `selection-deception` / "deception of learning-to-learn" — Risi & Stanley 2010). Escalation path is pre-committed; scope is restricted to the path identified there. This prereg enacts P-1 from §v2.5-plasticity-1a's Falsifiability block — the cheapest branching test that distinguishes "INVERSE-BALDWIN driven by static-canonical shortcut" (selection-deception, EES next) from "INVERSE-BALDWIN is intrinsic to rank-1 plasticity on this task" (rank-2 first; diagnosis doc amended per §13).*

## Amendment history

**2026-04-19 (v2 — pre-data, pre-engineering).** Original v1 committed at `9ff9bf8`; codex adversarial review of v1 flagged 6 P1 issues + 4 P2 issues. This v2 amendment addresses all of them pre-data (QUEUED status preserved — no sweep data exists yet, so amendments are legitimate per §13's spirit, which protects chronicles not preregs). Summary of changes from v1:

1. **Grid coverage honesty (P1-1).** v1 claimed full cross-product coverage; v2 acknowledges row 7 (grid-miss catchall) explicitly absorbs the F<5/δ_std ∈ (1.5, 2.0] and F<5/δ_std ≤ 1.5/gap ≥ 0.05 intermediate cells. §2b compliance: the grid is not truly exhaustive, and the catchall is load-bearing rather than cosmetic.
2. **Slope removed from row clauses (P1-2).** v1 was internally inconsistent — said slope "NOT load-bearing for row-matching" but rows 3 and 4 still keyed off slope. v2 removes slope from every row clause; slope is reported as descriptive diagnostic when defined. Primary confirmatory axis is `Baldwin_gap_h≥4` only. This sidesteps the sf=0.0 undefined-slope risk entirely.
3. **Confirmatory test collapsed to one statistic at one cell (P1-3).** v1's "1 confirmatory test" bookkeeping was at odds with row 3's "at ≥ 3/4 budgets" per-cell language — §22a bookkeeping slippage. v2 defines the confirmatory test as a single seed-bootstrap CI on `Baldwin_gap_h≥4` at budget=5 (the deepest-capacity cell, where §1a's strongest signatures concentrated). The three lower-budget cells are exploratory effect-size only; monotonicity-with-budget is a descriptive observation, not a confirmatory sub-test.
4. **Class-5 methodology amendment proposal removed (P1-4).** v1's row 3 decision rule pre-committed to a §29 `mechanism-mismatched` class-5 amendment. Codex called it "grid-miss in fancy clothing" and overreach. v2 removes the class-5 proposal; if row 3 fires, the consequence is a §13-style diagnosis-doc amendment (selection-deception retraction/narrowing) and a rank-2 queue entry. Any methodology amendment is deferred to a follow-up once multiple experiments show the same unclassifiable pattern.
5. **Bridging cell dropped (P1-5).** v1's sf=0.01 seeds-20..39 cell had counting-ambiguity under §22b commit-time-membership. v2 drops it entirely; replication of §1a's positive-slope signal on disjoint seeds deserves its own prereg if desired.
6. **Thresholds re-anchored (P1-6).** v1's F<5/20 was "2× drop from 10/20 midpoint" (not baseline-relative); Baldwin_gap > 0.15 was "halved §1a 0.260 point estimate" (not CI-anchored). v2 anchors F to frozen-control ("plastic best-budget F_AND_test within (frozen ± 3 seeds)") and Baldwin_gap to per-seed majority ("≥ 10 of 20 seeds > 0.10 at budget=5").
7. **§17a bundle consolidated (P2-1).** v1 enumerated 3 facets of sf axis as 3 confounds; they are 1 structural bundle. v2: "presence/absence of seeded canonical attractors in gen-0."
8. **Guard 7 moved to §23/§25 checklist (P2-2).** v1 listed "no-canonical-in-init invariant" as a principle-4 degenerate-success guard; it's an infrastructure-fidelity check. v2 relocates.
9. **Pre-allocated mechanism names removed from decision rules (P2-3).** v1 named "rank-1-plasticity-selection-deception-by-canonical-shortcut" etc. in row-1/2/3 routing without §16c falsifiability blocks. v2 defers naming to chronicle-time.
10. **Compute estimate softened (P2-4).** v1 said "~45 min wall"; v2 calls it "projected, extrapolated from pop=128×gens=100 profile."

v1 text is preserved in git history (`9ff9bf8`).

---

## Question (one sentence)

Under Arm A direct GP on `sum_gt_10_AND_max_gt_5` natural sampler with `seed_fraction=0.0` (canonical AND body removed from initial population), does rank-1 operator-threshold plasticity at `budget ∈ {1, 2, 3, 5}` reproduce §v2.5-plasticity-1a's `Baldwin_gap_h≥4` positive-monotone-in-budget pattern, or does the pattern collapse / flip when the static canonical shortcut is absent?

## Hypothesis

The `selection-deception` diagnosis (§29 class 4) predicts that removing the canonical shortcut will allow plasticity to produce selection-layer uplift that was previously masked by canonical-elite preservation. Four pre-committed readings (principle 2):

1. **BALDWIN-EMERGES.** F_AND_test ≥ 15/20 at some budget, AND Baldwin_gap_h≥4 seed-bootstrap CI at budget=5 does NOT satisfy row 3's positive-floor clause (i.e., the INVERSE-BALDWIN signature weakens substantially). Selection-deception **SUPPORTED**; EES next leg.
2. **UNIVERSAL-ADAPTER.** F_AND_test ≥ 15/20 at some budget AND δ_std at budget=5 collapses to ≤ 1.5. Plasticity recovers canonical-equivalents via convergent δ regardless of starting genotype; selection-deception weakly supported; EES candidate for confirmation.
3. **INVERSE-BALDWIN-REPLICATES.** Frozen-anchored F criterion fails (plasticity gives no or trivial F uplift vs frozen-control) AND δ_std at budget=5 > 2.0 AND seed-majority Baldwin_gap criterion fires. Selection-deception **REFUTED**: pattern is intrinsic to rank-1-on-this-task, not shortcut-induced. Consequence: diagnosis doc amended per §13; rank-2 memory queued ahead of EES.
4. **AMBIGUOUS / PARTIAL.** Any intermediate pattern: F_AND_test 5-14/20 at budget=5, OR mixed δ_std/gap signals. Decision: n-expansion on seeds 40..59 at budget=5 before routing, OR parallel rank-2 engineering while n-expansion runs.

Readings 1 and 2 support P-1; reading 3 refutes it; reading 4 forces replication before routing. Reading 3 is the pre-committed null that would falsify P-1.

## Setup

- **Sweep file:** `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2a.yaml` (to be created)
- **Arms / conditions:** Arm A only (direct GP). BP_TOPK is EXCLUDED per the §v2.5-plasticity-1a chronicle's caveat (structural R_fit ceiling → ΔR lift undetectable until a decoder-ceiling-lowering probe lands; §v2.4-proxy-5* sequel, not plasticity).
  - **Plastic cells (confirmatory source):** `arm=A, plasticity_enabled=true, plasticity_budget ∈ {1, 2, 3, 5}, seed_fraction=0.0, generations=1500, pop_size=512, mr=0.03, tournament_size=3, elite_count=2, crossover_rate=0.7, plasticity_mechanism=rank1_op_threshold, plasticity_delta=1.0, plasticity_train_fraction=0.75` × 4 budgets × 20 seeds = 80 runs. **Only budget=5 contributes a confirmatory test** — see Statistical test section. Budgets 1, 2, 3 are exploratory effect-size for monotonicity characterization.
  - **Frozen control cell (principle-23 anchor + row-3 baseline):** `arm=A, plasticity_enabled=false, seed_fraction=0.0, generations=1500, pop_size=512, mr=0.03, tournament_size=3, elite_count=2` × 20 seeds = 20 runs. Establishes sf=0.0 frozen baseline on shared seeds for (a) paired R_fit_999 delta and (b) row-3 F_AND_test anchor.
  - **Total:** 100 runs. Bridging cell from v1 dropped per P1-5.
- **Seeds:** 20..39 on all cells — **disjoint from §v2.5-plasticity-1a's seeds 0..19**, per principle 8 independent-seed-confirmation discipline.
- **Fixed params:** pop=512, gens=1500, mutation_rate=0.03, crossover_rate=0.7, tape_length=32, n_examples=64, alphabet=v2_probe, task=sum_gt_10_AND_max_gt_5, disable_early_termination=true, dump_final_population=true, backend=mlx, plasticity_mechanism=rank1_op_threshold, plasticity_delta=1.0, plasticity_train_fraction=0.75, holdout_size=256, seed_tapes=None (no canonical seeding at sf=0.0).
- **Est. compute (PROJECTED, extrapolated — NOT benchmarked at full scale).** The evaluate-loop optimization committed at `b1eab3c` measured 2.18× wall speedup on a pop=128 × gens=100 profile. Extrapolating to full scale (pop=512 × gens=1500 × budget=5) assumes the hot path scales linearly with `pop × gens × budget` while fixed GA overhead stays constant — plausible but not verified. Projected per-run wall: budget=5 ≈ 2.3 min (half of §1a's ~5 min/run pre-optimization at the same scale), budget=1 ≈ 1 min, frozen ≈ 1.5 min. Parallel at 10 workers, projected wall for 100 runs: 30-60 min. **90-min queue timeout is conservative headroom.** Actual runtime may diverge; true benchmark requires this sweep to land.
- **Related experiments:** §v2.5-plasticity-1a (primary predecessor); `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` (the diagnosis this prereg enacts P-1 for); §v2.4-proxy-4c Arm A baseline (commit `9135345` — per-tape mutation budget reference at matched pop=1024 scale).

**Principle 17a audit (multi-variable confound disclosure — amended).** The prereg varies one axis (`plasticity_budget ∈ {1, 2, 3, 5}`) plus one structural contrast vs §1a (`seed_fraction=0.0` instead of §1a's `seed_fraction=0.01`). Derived variables on the budget axis: (a) max accumulated |δ| per tape, (b) adaptation-step count, (c) per-evaluation VM work — all three co-move with budget by design and do not represent an undisclosed confound (budget IS the capacity axis). The sf contrast against §1a is a **single structural bundle**: *presence/absence of seeded canonical attractors in generation 0*. The three facets the v1 enumeration named (initial-canonical-count, Hamming distribution, elite-slot capture) are restatements of that single bundle, not independent confounds. Principle-17b: tested integer budget values ∈ {1, 2, 3, 5}, not `≤ 5` continuous range.

**Principle 20 audit.** Sampler unchanged from §1a (natural sampler for sum_gt_10_AND_max_gt_5, 64 inputs, 48 train × 16 test at 0.75 split). Principle 20 not triggered.

**Principle 23 audit.** Frozen control at sf=0.0 must reproduce §1a frozen-Arm-A-sf=0.01 infrastructure behavior (pop=512, gens=1500, mr=0.03, per-tape mutation budget = 45), differing ONLY on the sf axis. Expected R_fit_999 at frozen sf=0.0 close to 0 (no canonical to seed; §1a drift cell showed R_fit_frozen_999 = 0.000 at pop=512 gens=1500).

**Infrastructure-fidelity check (moved from v1's principle-4 guard 7 per P2-2).** No-canonical-in-init invariant: verify via `history.npz:initial_population_canonical_count` or post-hoc gen-0 inspection that the canonical 12-token AND body does NOT appear in the initial population at sf=0.0 across all 80 plastic + 20 frozen runs. Expected 0/100; any nonzero count indicates the `seed_fraction=0.0` handling has a bug. Adjunct pytest assertion added to the Status-transition checklist (item 2).

## Baseline measurement (required)

- **Baseline quantity 1 — frozen Arm A sf=0.0 F_AND_test and R_fit_999 at pop=512 × gens=1500 × mr=0.03:** measured in-sweep by the frozen control cell on seeds 20..39. §1a drift precedent: F_AND_test_frozen_best = 3/20; R_fit_frozen_999 = 0.000. The row-3 F criterion below is tied to this frozen control via "plastic best-budget F within (frozen ± 3)" — principle 6 compliant.
- **Baseline quantity 2 — §v2.5-plasticity-1a Arm A budget=5 sf=0.01 signatures (for row-3 threshold motivation):** Baldwin_slope cell-level CI `[+0.0521, +0.0863]`; Baldwin_gap_h≥4 mean = 0.260 (max); δ_std = 2.67; F_AND_test = 20/20 (saturated under seeded canonical). The row-3 Baldwin_gap threshold is seed-majority-anchored rather than point-estimate-halved.
- **Baseline quantity 3 — §v2.5-plasticity-1a Arm A budget=5 sf=0.0 drift signatures:** Baldwin_gap_h≥4 mean = 0.284; δ_std = 2.53; F_AND_test_plastic = 7/20 vs frozen-best = 3/20. Single-budget data; this prereg adds 3 lower-budget points for budget-scaling.

**Metric definitions (principle 27).** All confirmatory metrics cited from `experiments/chem_tape/analyze_plasticity.py:METRIC_DEFINITIONS` verbatim (same as §1a — see §1a chronicle's METRIC_DEFINITIONS block). The cell-level seed-bootstrap CI on `Baldwin_gap_h≥4` at budget=5 is NOT currently emitted by `analyze_plasticity.py` — this is an infra extension, see Status-transition checklist item 1.

**Measurement-infrastructure gate (principle 25).** Three infrastructure facts disclosed:

- **Cell-level seed-bootstrap CI on `Baldwin_gap_h≥4` (primary confirmatory statistic).** `analyze_plasticity.py` currently emits `Baldwin_gap_h_ge4_mean` per-cell (mean across seeds) but no CI. An extension to `analyze_plasticity.py:summarize` adding seed-bootstrap CI (10 000 resamples, rng seed 42, matching `bootstrap_ci_spec`) is REQUIRED before the sweep launches. Effort: ~15 min (mirror the Baldwin_slope seed-bootstrap pattern codex-review-recomputed at §1a chronicle time). Status-transition checklist item 1.
- **Paired per-seed `R_fit_plastic_999 − R_fit_frozen_999_control` at sf=0.0 (secondary diagnostic).** Requires a cross-cell merge between plastic and frozen-control per-run CSVs on shared seeds 20..39. Not emitted by current analysis pipeline. Effort: ~30 min. Status-transition checklist item 1 (same commit as the CI extension).
- **Baldwin_slope definition at sf=0.0.** `analyze_plasticity.py:linreg_slope` returns nan when x-variance = 0 (all non-GT-bypass individuals in a single Hamming bin). §1a drift cell observed this. In v2 the Baldwin_slope is **descriptive-only**; it does NOT appear in any row clause. The undefined-slope risk is therefore not a gate on row-matching; slope is reported for reasoning-trail purposes (e.g., if the h<4 tail DOES emerge unexpectedly, slope becomes informative).

## Internal-control check (required)

- **Tightest internal contrast:** paired plastic(sf=0.0, budget=b) vs frozen(sf=0.0, no plasticity) on shared seeds 20..39 at every budget. Directly tests "does plasticity do work at sf=0.0" without the confound of the canonical shortcut.
- **Are you running it here?** Yes — the frozen control cell is in-sweep on seeds 20..39, giving paired per-seed anchors at matched pop × gens × mr.

## Pre-registered outcomes (required — principle 2 + 2b + 26)

<!--
Axes measured at per-seed resolution at budget=5 (the pre-committed confirmatory cell):
  - F_AND_test (primary; plastic discovery from noise; frozen-control-anchored)
  - δ_std (primary; mechanism-capacity-utilization axis)
  - Baldwin_gap_h≥4 (confirmatory; seed-majority anchored)

Baldwin_slope reported when defined; NEVER appears in row clauses (v2 fix per P1-2).

Honest grid-coverage acknowledgment (§2b compliance, v2 fix per P1-1): the 5 named rows do NOT
exhaustively cover the 3-axis cross-product. Row 7 (grid-miss catchall) explicitly catches
intermediate-δ_std ∈ (1.5, 2.0] states and mixed δ/gap combinations that don't fit rows 1-5.
If row 7 fires, the next prereg on this axis must enumerate the observed pattern per principle 2b.
-->

**Confirmatory axis (single statistic at single cell — v2 per P1-3):**

The **one confirmatory test** is the seed-bootstrap 95% CI on `Baldwin_gap_h≥4` at `budget=5` — 20 seeds, 10 000 resamples, rng seed 42, matching `bootstrap_ci_spec`. Row 3 fires when CI_lo ≥ 0.10 (seed-majority-positive bound). Budgets 1, 2, 3 are exploratory effect-size for monotonicity characterization; their per-cell values are reported but do NOT enter the FWER family.

**Outcome grid:**

| # | outcome | F_AND_test (best across budgets) | δ_std @ budget=5 | Baldwin_gap_h≥4 @ budget=5 (confirmatory axis) | interpretation / routing |
|---|---------|-------------------|--------------|--------------------|--------------------------|
| 1 | **BALDWIN-EMERGES** | ≥ (frozen + 12) seeds (i.e., best-budget plastic F − frozen-control F ≥ 12/20) | any | CI_lo < 0.05 (gap weak/absent — the §1a positive-floor pattern does NOT survive shortcut removal) | Plasticity recovers canonical-equivalents without the static shortcut; selection-deception diagnosis **SUPPORTED**. Next leg: §v2.5-plasticity-2b (EES). Rank-2 deferred. Findings.md `plasticity-narrow-plateau` narrows to "NULL under seeded canonical; DOES narrow/recover under sf=0.0." |
| 2 | **UNIVERSAL-ADAPTER** | ≥ (frozen + 12) seeds | ≤ 1.5 | any | Plastic discovery from noise via convergent δ. Selection-deception weakly supported; mechanism is "δ does the work regardless of genotype." EES candidate. Findings.md narrows to "NULL under seeded; discovers canonical-equivalents under sf=0.0 via universal-δ mechanism." |
| 3 | **INVERSE-BALDWIN-REPLICATES** (pre-committed P-1 falsifier) | ≤ (frozen + 3) seeds (plasticity gives NO substantive F uplift vs frozen-control) | > 2.0 | **CI_lo ≥ 0.10** — the seed-majority-positive criterion | Selection-deception diagnosis **REFUTED**. Pattern is intrinsic to rank-1 on this task. Consequence: (a) `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` amended per §13 — class-4 selection-deception reading narrowed/retracted; (b) §v2.5-plasticity-1b (rank-2 memory) queued ahead of EES; (c) findings.md `plasticity-narrow-plateau` broadens to "pattern is shortcut-independent." No §29 methodology amendment pre-committed — any taxonomy change deferred to a follow-up after multiple experiments show the same unclassifiable pattern. |
| 4 | **AMBIGUOUS / PARTIAL** | (frozen + 4) to (frozen + 11) seeds (mid-range F uplift) | any | any | Neither clean support nor clean refutation. Decision: n-expansion seeds 40..59 at budget=5 (~20 min wall post-optimization) before routing. Parallel rank-2 engineering may start (3-5 day job) but no rank-2 sweep queues until the expanded verdict lands. |
| 5 | **FAIL — universal-null-at-sf=0.0** | ≤ (frozen + 3) seeds | ≤ 1.5 | CI_hi < 0.05 | Rank-1 plasticity does NO measurable work at sf=0.0 across all three axes. Both selection-deception (didn't help without shortcut) AND rank-1-intrinsic-tail-effect (no tail gap either) are weakened. Rank-1 is likely the wrong mechanism altogether; EES unlikely to help; rank-2 enters as "fill an empty mechanism bag" candidate under a weaker rationale. |
| 6 | **SWAMPED** | frozen F_AND_train < 15/20 diverges from §1a drift baseline (3/20) in suspicious directions (0/20 or ≥ 8/20) | any | any | Infrastructure or anchor-baseline bug. Stop and inspect. |
| 7 | **INCONCLUSIVE — grid-miss catchall (§2b; v2 explicit)** | any | any | any pattern not fitting rows 1-6 | §2b: the grid is not exhaustive. v2 explicitly acknowledges row 7 catches intermediate-δ_std ∈ (1.5, 2.0] states, mixed (F low / δ_std high / gap low) states, and any other cell in the F × δ_std × gap cross-product not enumerated in rows 1-5. If row 7 fires, the next prereg on this axis must enumerate the observed pattern pre-data before interpreting. |

**Row-clause fidelity (principle 28a pre-commitment).** Row 3 requires ALL three sub-clauses simultaneously: (a) F_AND_test best-budget ≤ frozen-control-F + 3 seeds; (b) δ_std at budget=5 > 2.0; (c) Baldwin_gap_h≥4 seed-bootstrap CI_lo at budget=5 ≥ 0.10. Prose-match with any sub-clause failing = row 7 (grid-miss), NOT a row-3 match. Row 5 (universal-null) requires its own 3-way conjunction. Row 2 (universal-adapter) requires F recovery + δ_std collapse — gap axis is "any" because universal-adapter's signature is in F + δ_std space regardless of gap.

**Threshold justifications (v2 re-anchored per P1-6):**

- **F_AND_test "frozen + 12" (row 1):** §1a's Baldwin-direction PASS threshold was F ≥ 15/20 absolute. At sf=0.0, absolute 15/20 is unreasonable (frozen-control F ≈ 3/20 per §1a drift; plastic getting to 15/20 requires lifting by 12 seeds). Expressing the threshold as "frozen + 12" makes it baseline-relative — the test is "plastic lifts F by 60% of the 20-seed range above frozen."
- **F_AND_test "frozen + 3" (rows 3, 5):** §1a drift observed plastic F = 7/20 vs frozen-best F = 3/20 at budget=5 sf=0.0 — i.e., plastic already gives a 4-seed lift. The row-3 threshold ≤ frozen + 3 requires plastic to give LESS uplift than the §1a drift observation — i.e., the positive-gap pattern fails to even produce §1a-drift-level F uplift on seeds 20..39. This is a strong falsifier threshold: if P-1 is right (selection-deception), plastic at sf=0.0 should produce MORE F uplift than §1a drift (canonical shortcut removed → plasticity's room to work increases).
- **δ_std > 2.0 (row 3):** §1a observed 2.67 at sf=0.01 budget=5 and 2.53 at sf=0.0 budget=5 drift. The 2.0 floor is the §1a minimum observed across both regimes; a substantial drop below 2.0 would signal different mechanism behavior, not INVERSE-BALDWIN replication.
- **δ_std ≤ 1.5 (rows 2, 5):** §1a never observed δ_std < 1.5 at budget=5; a drop to ≤ 1.5 is a qualitative shift (mechanism-capacity saturating differently).
- **Baldwin_gap_h≥4 CI_lo ≥ 0.10 (row 3 confirmatory clause):** anchored to per-seed majority rather than halved-point-estimate. §1a point-estimate at budget=5 sf=0.0 was 0.284; seed-majority threshold of CI_lo ≥ 0.10 requires at least half the seeds showing gap > 0.10 (bootstrap CI lower bound ≥ 0.10 on the cell mean across seeds). This is a defensible effect-size floor tied to sampling variance, not to a single number.
- **Baldwin_gap_h≥4 CI_hi < 0.05 (row 5 clause):** symmetric upper-bound at budget=5 — plasticity produces no tail-gap at all. Anchored to §1a drift baseline's near-zero frozen gap.

## Degenerate-success guard (principle 4 — amended per P2-2)

Six guards inherited from §v2.5-plasticity-1a (with sf=0.0-specific adjustments). The v1 "guard 7 (no-canonical-in-init invariant)" has been moved to the Infrastructure-fidelity check block above (principle 23/25), because it is an execution-fidelity check, not a degenerate-success risk.

1. **Universal-adapter artefact (row 2).** If F_AND_test ≥ frozen+12 at every budget with δ_std ≤ 1.5 at every budget, plasticity is acting as a universal canonical-recovery mechanism. Detection: compute per-seed Hamming-to-canonical of the top-1 winner at each budget; if ≥ 75% of winners are at h = 0 (exact canonical) regardless of budget, the mechanism is "plasticity-enables-random-search-to-find-canonical." Route as row 2.
2. **Train-test leakage.** Same as §1a guard 2. Suspicious near-zero `F_AND_test − F_AND_train` gap at high budget combined with high plastic discovery flags leakage.
3. **Threshold-saturation artefact (budget=5 cell, population and top-1-winner split).** Report **both** population-level and top-1-winner `|δ_final| ≥ 5` fractions at budget=5. §1a drift showed 0.738 population + 14/20 top-1 at sf=0.0 budget=5 — under this prereg if row 3 fires, expect similar (saturated mechanism-state in winners is consistent with INVERSE-BALDWIN-REPLICATES because the mechanism IS doing work in the winners; it's just not directed where selection rewards it). Report for chronicle transparency.
4. **GT-bypass artefact.** GT_bypass_fraction ≥ 0.50 at any cell → row 7.
5. **δ-convergence artefact (universal-adapter in δ-space).** If δ_std at budget=5 collapses to ≤ 0.5 across seeds, report as row 2 regardless of F_AND_test.
6. **Adaptation-budget-too-high at budget=5.** Sanity: max `|δ_final|` at budget=b = b × δ = b × 1 = b; any value strictly greater indicates an infrastructure bug.

## Statistical test (principle 22 — v2 per P1-3)

- **Primary confirmatory test:** seed-bootstrap 95% CI on `Baldwin_gap_h≥4` at `budget=5` (20 seeds, 10 000 resamples, `numpy.random.default_rng(seed=42)`, per `bootstrap_ci_spec`). Row 3 fires when CI_lo ≥ 0.10; row 5 when CI_hi < 0.05.
- **Secondary diagnostic (effect-size only, no FWER contribution):** per-cell `Baldwin_gap_h≥4` means at budgets 1, 2, 3; paired `R_fit_plastic_999 − R_fit_frozen_999` at sf=0.0 per cell; per-Hamming-bin Baldwin_gap pattern; δ_std scaling with budget. Used to characterize monotonicity / universal-adapter / row-distinguishing signals but NOT to gate α.
- **Classification:** **confirmatory.** Gates the diagnosis-routing decision for §1a's INVERSE-BALDWIN pattern.
- **Family:** NEW — `plasticity-inverse-baldwin-replicates`. Size 1 at this prereg; corrected α = 0.05 / 1 = 0.05. Distinct from the closed `plasticity-narrow-plateau` family (§1a tested the Baldwin-direction NULL; this tests whether the POSITIVE-slope replicates under shortcut removal).
- **Per-sweep test counting (principle 22a, v2):** this prereg runs 4 plastic budget cells × 20 seeds = 80 plastic runs. **One** confirmatory test is gated: the budget=5 cell's seed-bootstrap CI on `Baldwin_gap_h≥4`. The budgets 1/2/3 cells are exploratory effect-size — they inform row routing via descriptive thresholds (e.g., monotonicity of δ_std across budgets as a universal-adapter disambiguator) but do NOT each open a family member. Principle 22a requires this counting to be stated explicitly: if a future audit counts differently, amend this block before rechronicle.

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_AND_train`, `F_AND_test` (best-of-run, binary), `R_fit_frozen_999`, `R_fit_plastic_999`.
- Per-individual `test_fitness_frozen`, `test_fitness_plastic`, `delta_final`, `has_gt` → `final_population.npz`.
- Per-cell `GT_bypass_fraction`, `Baldwin_gap` by Hamming bin {0, 1, 2, 3, ≥4}, `Baldwin_slope` when defined.
- Per-cell `std(delta_final)` stratified by Hamming bin — universal-adapter diagnostic.
- Per-cell seed-bootstrap 95% CI on `Baldwin_gap_h≥4` — the primary confirmatory statistic at budget=5.
- Per-cell paired `R_fit_plastic_999 − R_fit_frozen_999` on shared seeds — secondary diagnostic.
- Per-cell `|δ_final| ≥ 5` fraction at budget=5, split: population-level AND top-1 winner.
- Per-cell best-of-run hex for top-1 winner per seed — attractor inspection input (row-1 / row-2 / row-5 disambiguation).
- Per-seed `initial_population_canonical_count` in gen-0 — infrastructure-fidelity check.
- `Baldwin_slope` reported when defined with "nan (degenerate x-variance)" otherwise — transparent §25 disclosure.

## Scope tag (required for any summary-level claim)

**If row 1 or row 2 fires:** `plasticity-narrow-plateau` NULL narrows — "rank-1 does NOT narrow at sf=0.01, DOES narrow/recover at sf=0.0 — selection-deception supported." Scope:
`within-task-family · n=20 per cell × 4 plastic Arm A sf=0.0 budget cells + 1 frozen sf=0.0 control · at pop=512 gens=1500 mr=0.03 tournament_size=3 elite_count=2 · sum_gt_10_AND_max_gt_5 natural sampler with 75/25 train/test split · rank1_op_threshold δ=1.0 budget ∈ {1,2,3,5} · random initial population sf=0.0` plus existing §1a scope.

**If row 3 fires:** `plasticity-narrow-plateau` NULL broadens — "pattern is shortcut-independent; rank-1-intrinsic on this task." Scope: same parameter set + the explicit selection-deception-retraction flag. No pre-commitment to a §29 taxonomy amendment; diagnosis doc amended per §13 and rank-2 queued as the empirical next step.

Explicitly NOT-broadening in any outcome: other tasks (P-3 open for cross-task); rank-2 or deeper mechanisms (untested); other selection regimes (EES/novelty-search separate legs); other δ values; other train/test splits. Principle 17b: tested integer budget values ∈ {1, 2, 3, 5}.

## Decision rule

- **Row 1 (BALDWIN-EMERGES) →** narrow `plasticity-narrow-plateau` NULL in findings.md; queue §v2.5-plasticity-2b (EES) as confirmatory leg for selection-deception; rank-2 deferred. Mechanism-name: deferred to the chronicle's §16-renaming cycle (no pre-allocation).
- **Row 2 (UNIVERSAL-ADAPTER) →** narrow findings.md; queue §v2.5-plasticity-2b (EES) with an axis testing whether EES preserves the convergent-δ behavior; rank-2 deferred. Mechanism-name: deferred to chronicle.
- **Row 3 (INVERSE-BALDWIN-REPLICATES; P-1 pre-committed falsifier) →** three actions: (a) amend `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` per §13 — class-4 selection-deception reading retracted or narrowed in scope; (b) queue §v2.5-plasticity-1b (rank-2 memory) as the next escalation; (c) broaden findings.md `plasticity-narrow-plateau`. **No §29 methodology amendment pre-committed in this prereg** (P1-4 fix): if rank-2 reveals the same unclassifiable pattern, the methodology amendment is considered at THAT point based on 2+ experiments. Single-experiment taxonomy changes are not pre-committed. Mechanism-name: deferred.
- **Row 4 (AMBIGUOUS / PARTIAL) →** n-expansion seeds 40..59 at budget=5 (~20 min wall projected); re-evaluate against rows 1-5 and re-route. Do NOT queue EES or rank-2 sweeps until the expanded verdict lands. Parallel rank-2 engineering (VM implementation, 3-5 days) may START while n-expansion runs.
- **Row 5 (FAIL — universal-null-at-sf=0.0) →** queue §v2.5-plasticity-1b (rank-2) with weaker-motivation priority; EES unlikely to help. Methodology-backlog item: add a "null-across-selection-regime-AND-mechanism" case to the diagnosis doc's rejected-diagnoses tree. No §29 amendment pre-committed.
- **Row 6 (SWAMPED) →** stop and inspect. Do not chronicle until anchor check passes.
- **Row 7 (INCONCLUSIVE — grid-miss catchall) →** per principle 2b, update outcome grid BEFORE interpreting. Chronicle as INCONCLUSIVE-grid-miss with the observed pattern documented as a pre-commitment for a follow-up prereg.

## Audit trail

- **Principle 1:** plastic-vs-frozen on shared seeds at sf=0.0 is the tightest internal contrast; runs in-sweep.
- **Principle 2 + 2b:** 7 rows enumerated; row 7 explicitly acknowledged as the grid-miss catchall for intermediate δ_std ∈ (1.5, 2.0] and mixed-axis cells not covered by rows 1-5. §2b honest compliance — grid is not exhaustive by construction, catchall carries weight.
- **Principle 4:** 6 guards (universal-adapter, leakage, threshold-saturation, GT-bypass, δ-convergence, budget-saturation-sanity). Guard 7 (no-canonical-in-init) moved to infrastructure-fidelity check per P2-2.
- **Principle 6:** F_AND_test thresholds frozen-control-anchored; δ_std thresholds §1a-observed-anchored; Baldwin_gap threshold CI-anchored (seed-majority).
- **Principle 16c:** no new mechanism name pre-allocated; any renaming deferred to chronicle-time with its own falsifiability block per P2-3.
- **Principle 17a / 17b:** budget axis (one intended capacity variable, 3 co-moving derived variables); sf contrast (one structural bundle, not 3 independent confounds). Tested values discrete.
- **Principle 20:** sampler unchanged; not triggered.
- **Principle 22 + 22a + 22b:** confirmatory, 1 test at budget=5, family `plasticity-inverse-baldwin-replicates` size 1, α = 0.05. Per-sweep counting stated explicitly (not slipped to 4 tests via row-3 per-budget language).
- **Principle 23:** frozen-control-at-sf=0.0 is in-sweep anchor; pop/gens/mr byte-identical to §1a sf=0.01 frozen control except sf axis.
- **Principle 25:** Baldwin_gap_h≥4 seed-bootstrap CI is required confirmatory statistic but NOT currently emitted by `analyze_plasticity.py` — infra extension blocking RUNNING status.
- **Principle 26:** F_AND_test × δ_std × Baldwin_gap_h≥4 cross-product at budget=5 gridded; Baldwin_slope demoted to descriptive-only (never in row clauses) per P1-2.
- **Principle 27:** METRIC_DEFINITIONS inherited verbatim from §1a + new cell-level bootstrap CI entry added as part of infra extension.
- **Principle 28a/b/c:** row clauses are conjunctions of all sub-clauses (28a); guards cover multi-failure-mode cases with explicit bundles (28b); status-line inline qualifier discipline at chronicle time (28c).
- **Principle 29:** this prereg follows the pre-committed diagnosis doc; escalation path restricted to the doc's ladder. No §29 methodology amendment pre-committed (P1-4 fix).

## Status-transition checklist (QUEUED → RUNNING)

Before this prereg can move from QUEUED to RUNNING:

1. **Infra extension to `analyze_plasticity.py`:** add cell-level seed-bootstrap CI for `Baldwin_gap_h≥4` (primary confirmatory statistic; 10 000 resamples, rng seed 42). Add paired `R_fit_plastic_999 − R_fit_frozen_999` cross-cell merge (secondary diagnostic). Add METRIC_DEFINITIONS entries for both. Effort: ~45 min combined.
2. **Pytest assertion:** `sf=0.0 → 0 canonical in gen-0` for all 100 runs (infrastructure-fidelity check moved from v1's guard 7). Effort: ~20 min.
3. **Sweep YAML:** `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2a.yaml` — 4 plastic cells × 20 seeds + 1 frozen control × 20 seeds = 100 runs.
4. **Queue entry:** add to `queue.yaml` with 90-min timeout (conservative headroom over projected 30-60 min).
5. **Pin target commit SHA** in Status line above.
6. Codex adversarial review of this v2 — focused on the re-anchored thresholds, the row-3 confirmatory-test collapse to 1 statistic, and the removed class-5 amendment not silently reappearing elsewhere.

## References

- `Plans/prereg_v2-5-plasticity-1a.md` — primary predecessor prereg.
- `docs/chem-tape/experiments-v2.md#v2.5-plasticity-1a` — INVERSE-BALDWIN chronicle (grid-miss verdict, §29 class-4 diagnosis).
- `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` — diagnosis doc this prereg enacts P-1 for.
- `docs/methodology.md` — §§1, 2, 2b, 4, 6, 16c, 17a, 17b, 20, 22, 22a, 22b, 23, 25, 26, 27, 28a/b/c, 29.
- `experiments/chem_tape/analyze_plasticity.py` — METRIC_DEFINITIONS source.
- `docs/chem-tape/runtime-plasticity-direction.md` — direction doc (rank-1 → rank-2 ladder).
- Risi, S. & Stanley, K. O. (2010). "Evolving Plastic Neural Networks with Novelty Search." *Adaptive Behavior* 18(6), 470-491 — literature anchor for class-4 `selection-deception`.
- Prior commit `9ff9bf8` — v1 of this prereg (superseded by this v2 amendment; reasoning trail preserved in git history per §13 spirit).
