# Pre-registration: §v2.5-plasticity-2a — Arm A sf=0.0 seed-removal probe of P-1 diagnosis falsifiability (branching test for `selection-deception` vs rank-1-structural-mismatch)

**Status:** QUEUED (v3, amended) · target commit `{short-sha, to be pinned when sweep launches}` · 2026-04-19

*This prereg follows from diagnosis `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` (class: `selection-deception` / "deception of learning-to-learn" — Risi & Stanley 2010). Escalation path is pre-committed; scope is restricted to the path identified there. This prereg enacts P-1 from §v2.5-plasticity-1a's Falsifiability block — the cheapest branching test that distinguishes "INVERSE-BALDWIN driven by static-canonical shortcut" (selection-deception, EES next) from "INVERSE-BALDWIN is intrinsic to rank-1 plasticity on this task" (rank-2 first; diagnosis doc amended per §13).*

## Amendment history

**2026-04-19 (v3 — pre-data, pre-engineering).** Codex review of v2 flagged 2 partially-fixed items (P1-2 residual, P1-6 residual), 1 new P1 (diagnosis-doc operationalization mismatch), and 2 new P2s (infra-scope understatement, missing verbatim METRIC_DEFINITIONS). This v3 amendment:

1. **Row 1 renamed from BALDWIN-EMERGES to F-RECOVERY-WITHOUT-INVERSE-SIGNATURE** (P1-2 residual). The row-1 trigger (F high + tail-gap absent + δ_std unrestricted) does not establish Baldwin direction (closer-to-canonical benefits more) — it establishes "plasticity recovers F without reproducing the INVERSE-BALDWIN tail-concentration signature." The label now describes what is actually measured; Baldwin-direction would require per-seed Hamming analysis of top-1 winners beyond the row-match clauses. Routing is unchanged — this outcome still supports the selection-deception diagnosis via the "shortcut removal unlocks plasticity's selection-layer contribution" signal.
2. **Row 3 clause (c) broadened to any h ∈ {2, 3, ≥4}** (NEW-P1). v2's gap-based trigger required `Baldwin_gap_h≥4 CI_lo ≥ 0.10`, which would miss an intrinsic INVERSE-BALDWIN pattern if the positive uplift concentrates in h=2 or h=3 instead. v3: clause (c) is `max(Baldwin_gap_h2, Baldwin_gap_h3, Baldwin_gap_h≥4) CI_lo ≥ 0.10` — any non-h=0,1 bin showing the seed-majority positive signal triggers. Also adds explicit note: row-3 gap clause operationalizes the diagnosis doc's slope-based INVERSE-BALDWIN definition for the sf=0.0 regime where slope is likely undefined; at result time, if Baldwin_slope IS defined, the slope sign is reported alongside the gap-based verdict for consistency.
3. **Row-3 threshold rationale corrected** (P1-6 residual). v2 claimed "CI_lo ≥ 0.10 means ≥ 10 of 20 seeds show gap > 0.10" — statistically wrong (CI_lo is on the cell mean, not on seed-majority). v3: drops the seed-majority equivalence claim; adds an explicit per-seed clause: "AND ≥ 10 of 20 seeds show max-across-bins Baldwin_gap > 0.10" as an additional sub-clause guarding the row-3 trigger. This makes the seed-majority intent explicit rather than implied.
4. **F thresholds reframed as proportion-based dual criterion** (P1-6 residual). v2's `frozen + 12` was flagged as effectively absolute 15/20 because §1a drift frozen happens to be 3/20. v3: row 1 criterion becomes `plastic best-budget F_proportion ≥ 0.75 AND frozen F_proportion ≤ 0.25`; row 3 criterion becomes `plastic best-budget F_proportion ≤ (frozen F_proportion + 0.15)`. Both are dual criteria tied to frozen, not single-number absolutes.
5. **Status-transition checklist infra scope corrected** (NEW-P2). Codex verified that `analyze_plasticity.py:analyze_run` skips frozen-only runs (returns None when no `delta_final` column); the paired R_fit merge is a genuine new code path, not a flag flip. `history.npz` does not currently contain `initial_population_canonical_count`; the gen-0 invariant check requires runner instrumentation in `run.py` or `evolve.py`, not just an assertion. v3: checklist rewritten with realistic effort estimates (~2-2.5 h total, up from ~65 min).
6. **New METRIC_DEFINITIONS block (verbatim) added** (NEW-P2). Per principle 27, the prereg must cite the exact entries that will land in `analyze_plasticity.py:METRIC_DEFINITIONS`. v3 adds a "METRIC_DEFINITIONS extensions" block with the exact wording for `Baldwin_gap_max_cell_boot_ci`, `R_fit_delta_paired_sf0`, and `initial_population_canonical_count`.

v2 is preserved in git history at commit `f6ead25`. v1 at `9ff9bf8`.

---

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

1. **F-RECOVERY-WITHOUT-INVERSE-SIGNATURE** (v3 renamed from BALDWIN-EMERGES; see v3 amendment note). `plastic_F_prop ≥ 0.75 AND frozen_F_prop ≤ 0.25`, AND `max_gap_@5` CI_hi < 0.05 with seed-minority < 10/20 (tail-gap absent; INVERSE-BALDWIN signature does NOT survive shortcut removal). Selection-deception **SUPPORTED** via shortcut-removal-unlocks-F-recovery signal. Baldwin-direction NOT established by row alone — requires post-hoc per-seed Hamming analysis of top-1 winners. EES next leg.
2. **UNIVERSAL-ADAPTER.** F proportions same as row 1 AND δ_std at budget=5 collapses to ≤ 1.5. Plasticity recovers canonical-equivalents via convergent δ regardless of starting genotype; selection-deception weakly supported; EES candidate for confirmation.
3. **INVERSE-BALDWIN-REPLICATES.** Frozen-anchored F criterion fails (`plastic_F_prop ≤ frozen_F_prop + 0.15`) AND δ_std at budget=5 > 2.0 AND `max_gap_@5` (max across h ∈ {2, 3, ≥4}) seed-bootstrap CI_lo ≥ 0.10 AND per-seed majority ≥ 10/20 have max_gap > 0.10. Selection-deception **REFUTED**: pattern is intrinsic to rank-1-on-this-task, not shortcut-induced. Consequence: diagnosis doc amended per §13; rank-2 memory queued ahead of EES.
4. **AMBIGUOUS / PARTIAL.** Any intermediate pattern: `frozen_F_prop + 0.15 < plastic_F_prop < 0.75` OR mixed δ_std/gap signals. Decision: n-expansion on seeds 40..59 at budget=5 before routing, OR parallel rank-2 engineering while n-expansion runs.

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

**Metric definitions (principle 27).** Existing metrics cited from `experiments/chem_tape/analyze_plasticity.py:METRIC_DEFINITIONS` verbatim (same as §1a — see §1a chronicle's METRIC_DEFINITIONS block). Five NEW entries (`max_gap_at_budget_5`, `max_gap_at_budget_5_cell_boot_ci`, `max_gap_at_budget_5_seed_majority`, `R_fit_delta_paired_sf0`, `initial_population_canonical_count`) are pre-committed verbatim in the "METRIC_DEFINITIONS extensions" block below (before the Status-transition checklist). The primary confirmatory statistic — cell-level seed-bootstrap CI + per-seed-majority count on `max_gap_at_budget_5` — is NOT currently emitted by `analyze_plasticity.py`; Status-transition checklist item 1 covers the extensions.

**Measurement-infrastructure gate (principle 25).** Three infrastructure facts disclosed:

- **Cell-level seed-bootstrap CI + per-seed-majority on `max_gap_at_budget_5` (primary confirmatory statistic; v3 broadened from v2's h≥4-only).** `analyze_plasticity.py` currently emits `Baldwin_gap_h_ge4_mean` per-cell (mean across seeds at h≥4 only, no CI). v3 requires: (a) a new per-seed metric `max_gap_at_budget_5` = per-seed max across h ∈ {2, 3, ≥4}; (b) cell-level seed-bootstrap CI on the per-cell mean of that metric (10 000 resamples, rng seed 42, matching `bootstrap_ci_spec`); (c) a seed-majority count (seeds > 0.10 threshold). Status-transition checklist item 1.
- **Paired per-seed `R_fit_delta_paired_sf0` at sf=0.0 (secondary diagnostic).** Requires a cross-cell merge between plastic and frozen-control per-run CSVs on shared seeds 20..39. `analyze_plasticity.py:analyze_run` currently skips frozen-only runs entirely — this is a genuine new code path, not a flag flip. Status-transition checklist item 1(a)+(e).
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

**Confirmatory axis (single statistic at single cell — v3 per P1-3 + NEW-P1):**

Let `max_gap_@5` = per-cell max across Hamming bins h ∈ {2, 3, ≥4} of `Baldwin_gap` at `budget=5`. The **one confirmatory test** is the seed-bootstrap 95% CI on `max_gap_@5` — 20 seeds, 10 000 resamples, rng seed 42, matching `bootstrap_ci_spec`. Row 3 fires when the CI's lower bound ≥ 0.10 AND a per-seed majority (≥ 10/20) also shows max-across-bins `Baldwin_gap > 0.10` at budget=5. v3 broadens from h≥4-only to any-of-{h=2,h=3,h≥4} because INVERSE-BALDWIN's positive uplift may concentrate in h=2 or h=3 rather than h≥4 when initial population is random (NEW-P1 fix). Budgets 1, 2, 3 are exploratory effect-size for monotonicity characterization; their per-cell values are reported but do NOT enter the FWER family.

**v3 note (F thresholds — reframed per P1-6 residual).** F criteria are dual-frozen-anchored proportions (plastic vs frozen), not single-number seed-count deltas. `F_prop = F_AND_test / 20`. Rows 1/2: `plastic_F_prop ≥ 0.75 AND frozen_F_prop ≤ 0.25`. Rows 3/5: `plastic_F_prop ≤ frozen_F_prop + 0.15`. Row 4: `frozen_F_prop + 0.15 < plastic_F_prop < 0.75`. If frozen ends up higher than 0.25 (unexpected), row 6 SWAMPED fires.

**v3 note (operationalization-to-diagnosis-doc mapping).** The diagnosis doc defines INVERSE-BALDWIN and Baldwin-direction in slope terms. At sf=0.0 the slope is likely undefined per principle 25. The gap-based row triggers here are the best-effort operationalization of the diagnosis's slope-based branches for the sf=0.0 regime. At result time, if `Baldwin_slope` IS defined (h<4 subpopulation unexpectedly emerges), the slope sign is reported alongside the gap-based verdict; disagreements between the two are flagged as open-mechanism signals for the chronicle.

**Outcome grid:**

| # | outcome | F_AND_test proportion (best across budgets) | δ_std @ budget=5 | `max_gap_@5` (confirmatory axis — max across h ∈ {2, 3, ≥4}) | interpretation / routing |
|---|---------|-------------------|--------------|--------------------|--------------------------|
| 1 | **F-RECOVERY-WITHOUT-INVERSE-SIGNATURE** (v3 renamed from BALDWIN-EMERGES) | plastic ≥ 0.75 AND frozen ≤ 0.25 | any | CI_hi < 0.05 AND < 10/20 seeds have per-seed max_gap > 0.05 (tail-gap absent; §1a INVERSE-BALDWIN signature does NOT survive shortcut removal) | Plasticity recovers canonical-equivalents without the static shortcut; selection-deception diagnosis **SUPPORTED** by the shortcut-removal-unlocks-F-recovery signal. Baldwin-direction NOT established — per-seed Hamming analysis of top-1 winners required at chronicle time to confirm. Next leg: §v2.5-plasticity-2b (EES). Rank-2 deferred. Findings.md `plasticity-narrow-plateau` narrows. |
| 2 | **UNIVERSAL-ADAPTER** | plastic ≥ 0.75 AND frozen ≤ 0.25 | ≤ 1.5 | any | Plastic discovery from noise via convergent δ. Selection-deception weakly supported; mechanism is "δ does the work regardless of genotype." EES candidate. Findings.md narrows. |
| 3 | **INVERSE-BALDWIN-REPLICATES** (pre-committed P-1 falsifier) | plastic ≤ frozen + 0.15 (plasticity gives NO substantive F uplift) | > 2.0 | `max_gap_@5` CI_lo ≥ 0.10 AND ≥ 10/20 seeds have per-seed `max_gap > 0.10` | Selection-deception diagnosis **REFUTED**. Pattern is intrinsic to rank-1 on this task. Consequence: (a) `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` amended per §13 — class-4 narrowed/retracted; (b) §v2.5-plasticity-1b (rank-2 memory) queued ahead of EES; (c) findings.md `plasticity-narrow-plateau` broadens. No §29 methodology amendment pre-committed. Mechanism-name deferred. |
| 4 | **AMBIGUOUS / PARTIAL** | frozen + 0.15 < plastic < 0.75 (mid-range F uplift) | any | any | Neither clean support nor clean refutation. Decision: n-expansion seeds 40..59 at budget=5 (~20 min wall projected); re-evaluate against rows 1-5. Do NOT queue EES or rank-2 sweeps until the expanded verdict lands. Parallel rank-2 engineering (VM implementation, 3-5 days) may START while n-expansion runs. |
| 5 | **FAIL — universal-null-at-sf=0.0** | plastic ≤ frozen + 0.15 | ≤ 1.5 | CI_hi < 0.05 | Rank-1 plasticity does NO measurable work at sf=0.0 across all three axes. Both selection-deception AND rank-1-intrinsic-tail-effect are weakened. Rank-2 enters as "fill an empty mechanism bag" candidate under weaker motivation. |
| 6 | **SWAMPED** | frozen_F_prop outside the plausibility window `[0.10, 0.40]` (§1a drift observed 0.15 = 3/20; suspicious shifts either direction) | any | any | Infrastructure or anchor-baseline bug. Stop and inspect. |
| 7 | **INCONCLUSIVE — grid-miss catchall (§2b explicit)** | any | any | any pattern not fitting rows 1-6 | §2b: grid is not exhaustive. Row 7 catches intermediate-δ_std ∈ (1.5, 2.0] states, mixed (F low / δ_std high / gap low) states, and any other cell in the F × δ_std × gap cross-product not enumerated in rows 1-5. If row 7 fires, the next prereg must enumerate the observed pattern pre-data before interpreting. |

**Row-clause fidelity (principle 28a pre-commitment).** Row 3 requires ALL three sub-clauses simultaneously: (a) `plastic_F_prop ≤ frozen_F_prop + 0.15`; (b) δ_std at budget=5 > 2.0; (c) `max_gap_@5` seed-bootstrap CI_lo ≥ 0.10 AND ≥ 10/20 seeds have per-seed max_gap > 0.10. Prose-match with any sub-clause failing = row 7 (grid-miss), NOT a row-3 match. Row 5 (universal-null) requires its own 3-way conjunction. Row 1 requires F recovery + gap-absence (CI_hi AND per-seed-minority). Row 2 requires F recovery + δ_std collapse.

**Threshold justifications (v3 re-anchored per P1-6 + NEW-P1):**

- **F thresholds (proportion-based dual criterion, v3).** Row 1/2's "plastic ≥ 0.75 AND frozen ≤ 0.25" is explicitly dual — tied to frozen being LOW in addition to plastic being HIGH. If frozen-sf=0.0 ends up higher than 0.25 (e.g., the population discovers canonical-equivalents without any seeding, which §1a drift's 3/20 suggests is possible but rare), row 1 cannot fire — the lift-above-frozen must be substantial, not just plastic reaching a threshold. If frozen is suspiciously high (> 0.40), row 6 SWAMPED fires instead. The 0.75/0.25 numbers correspond to §1a's 15/20 and 5/20 ceiling/floor but are expressed as proportions to handle frozen shifts cleanly.
- **Row-3 F threshold `plastic ≤ frozen + 0.15` (v3).** §1a drift observed plastic_F_prop = 7/20 = 0.35 vs frozen_F_prop = 3/20 = 0.15 at budget=5 sf=0.0 — i.e., §1a drift showed plastic − frozen = 0.20 uplift. The row-3 threshold requires plastic uplift ≤ 0.15 (strictly LESS than §1a drift's observed 0.20 lift). If INVERSE-BALDWIN is truly intrinsic to rank-1 on this task, shortcut removal should not unlock MORE F uplift than §1a drift showed, and plastic should stay close to frozen. This is a strict falsifier.
- **δ_std > 2.0 (row 3).** §1a observed 2.67 at sf=0.01 budget=5 and 2.53 at sf=0.0 budget=5 drift. 2.0 is the §1a minimum observed; substantial drop below 2.0 would signal different mechanism behavior, not INVERSE-BALDWIN replication.
- **δ_std ≤ 1.5 (rows 2, 5).** §1a never observed δ_std < 1.5 at budget=5; drop to ≤ 1.5 is a qualitative shift (mechanism-capacity saturating differently).
- **`max_gap_@5` CI_lo ≥ 0.10 AND per-seed-majority > 0.10 (row 3; v3 explicit dual criterion per P1-6 residual).** Dual criterion: cell-mean-CI floor AND seed-majority. The cell-mean-CI catches "average signal is positive with sampling-variance-bounded precision"; the per-seed-majority catches "signal isn't driven by a small tail of extreme seeds." Requiring BOTH sidesteps v2's statistically incorrect "CI_lo ≥ 0.10 = seed-majority" equivalence. §1a drift point estimate at h≥4 was 0.284; 0.10 is a substantive floor well below that anchor, reasonable for replication on disjoint seeds. Max-across-bins (v3 broadening per NEW-P1) handles the "positive uplift shifts to h=2/3 instead of h≥4" case.
- **`max_gap_@5` CI_hi < 0.05 AND seed-minority > 0.05 (row 5).** Symmetric upper-bound with dual criterion. Plasticity produces no non-trivial tail-gap anywhere.
- **Row 1 gap clause — CI_hi < 0.05 AND < 10/20 seeds > 0.05 (v3 explicit).** Mirror of row 5's gap clause for the "gap absent" signal, but paired with the opposite F criterion.

## Degenerate-success guard (principle 4 — amended per P2-2)

Six guards inherited from §v2.5-plasticity-1a (with sf=0.0-specific adjustments). The v1 "guard 7 (no-canonical-in-init invariant)" has been moved to the Infrastructure-fidelity check block above (principle 23/25), because it is an execution-fidelity check, not a degenerate-success risk.

1. **Universal-adapter artefact (row 2).** If F_AND_test ≥ frozen+12 at every budget with δ_std ≤ 1.5 at every budget, plasticity is acting as a universal canonical-recovery mechanism. Detection: compute per-seed Hamming-to-canonical of the top-1 winner at each budget; if ≥ 75% of winners are at h = 0 (exact canonical) regardless of budget, the mechanism is "plasticity-enables-random-search-to-find-canonical." Route as row 2.
2. **Train-test leakage.** Same as §1a guard 2. Suspicious near-zero `F_AND_test − F_AND_train` gap at high budget combined with high plastic discovery flags leakage.
3. **Threshold-saturation artefact (budget=5 cell, population and top-1-winner split).** Report **both** population-level and top-1-winner `|δ_final| ≥ 5` fractions at budget=5. §1a drift showed 0.738 population + 14/20 top-1 at sf=0.0 budget=5 — under this prereg if row 3 fires, expect similar (saturated mechanism-state in winners is consistent with INVERSE-BALDWIN-REPLICATES because the mechanism IS doing work in the winners; it's just not directed where selection rewards it). Report for chronicle transparency.
4. **GT-bypass artefact.** GT_bypass_fraction ≥ 0.50 at any cell → row 7.
5. **δ-convergence artefact (universal-adapter in δ-space).** If δ_std at budget=5 collapses to ≤ 0.5 across seeds, report as row 2 regardless of F_AND_test.
6. **Adaptation-budget-too-high at budget=5.** Sanity: max `|δ_final|` at budget=b = b × δ = b × 1 = b; any value strictly greater indicates an infrastructure bug.

## Statistical test (principle 22 — v3 per P1-3 + NEW-P1)

- **Primary confirmatory test:** seed-bootstrap 95% CI on `max_gap_@5` at `budget=5` (20 seeds, 10 000 resamples, `numpy.random.default_rng(seed=42)`, per `bootstrap_ci_spec`), where `max_gap_@5` = per-seed max across Hamming bins h ∈ {2, 3, ≥4} of `Baldwin_gap`. Row 3 fires when CI_lo ≥ 0.10 AND per-seed majority (≥ 10/20) have per-seed max_gap > 0.10. Row 5 fires when CI_hi < 0.05 AND per-seed minority (< 10/20) have per-seed max_gap > 0.05. The dual cell-mean-CI + per-seed-majority criterion is v3's explicit fix for P1-6-residual's statistically incorrect "CI_lo ≥ 0.10 = seed-majority" equivalence.
- **Secondary diagnostic (effect-size only, no FWER contribution):** per-cell `Baldwin_gap` by-Hamming-bin pattern at budgets 1, 2, 3; paired `R_fit_plastic_999 − R_fit_frozen_999` at sf=0.0 per cell; δ_std scaling with budget; per-seed Hamming distribution of top-1 winners (for row-1 Baldwin-direction post-hoc check). Used to characterize monotonicity / universal-adapter / row-distinguishing signals but NOT to gate α.
- **Classification:** **confirmatory.** Gates the diagnosis-routing decision for §1a's INVERSE-BALDWIN pattern.
- **Family:** NEW — `plasticity-inverse-baldwin-replicates`. Size 1 at this prereg; corrected α = 0.05 / 1 = 0.05. Distinct from the closed `plasticity-narrow-plateau` family (§1a tested the Baldwin-direction NULL; this tests whether the POSITIVE-gap signature replicates under shortcut removal).
- **Per-sweep test counting (principle 22a, v3):** this prereg runs 4 plastic budget cells × 20 seeds = 80 plastic runs. **One** confirmatory test is gated: the budget=5 cell's dual-criterion bootstrap-CI-plus-per-seed-majority test on `max_gap_@5`. The budgets 1/2/3 cells are exploratory effect-size — they inform row routing via descriptive thresholds (e.g., monotonicity of δ_std across budgets as a universal-adapter disambiguator) but do NOT each open a family member. If a future audit counts differently, amend this block before rechronicle.

## Diagnostics to log (beyond fitness)

- Per-seed × per-cell `F_AND_train`, `F_AND_test` (best-of-run, binary), `R_fit_frozen_999`, `R_fit_plastic_999`.
- Per-individual `test_fitness_frozen`, `test_fitness_plastic`, `delta_final`, `has_gt` → `final_population.npz`.
- Per-cell `GT_bypass_fraction`, `Baldwin_gap` by Hamming bin {0, 1, 2, 3, ≥4}, `Baldwin_slope` when defined.
- Per-cell `std(delta_final)` stratified by Hamming bin — universal-adapter diagnostic.
- Per-cell seed-bootstrap 95% CI on `max_gap_at_budget_5` + `max_gap_at_budget_5_seed_majority` count — the primary confirmatory dual statistic at budget=5 (v3 broadened from v2's h≥4-only).
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

- **Row 1 (F-RECOVERY-WITHOUT-INVERSE-SIGNATURE; v3 renamed) →** narrow `plasticity-narrow-plateau` NULL in findings.md; queue §v2.5-plasticity-2b (EES) as confirmatory leg for selection-deception; rank-2 deferred. Additional chronicle-time work: per-seed Hamming analysis of top-1 winners to test whether Baldwin-direction (closer-to-canonical benefit) is established beyond row-match clauses — this is mechanism-layer follow-up, not routing-gating. Mechanism-name: deferred to the chronicle's §16-renaming cycle.
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
- **Principle 25:** `max_gap_at_budget_5` cell-level seed-bootstrap CI + per-seed-majority is the required confirmatory statistic; frozen-only run processing + cross-cell merge for `R_fit_delta_paired_sf0` is the secondary diagnostic. Neither is currently emitted by `analyze_plasticity.py` — five new METRIC_DEFINITIONS entries pre-committed verbatim in the Metric-definitions-extensions block; Status-transition checklist item 1 covers the code.
- **Principle 26:** F_AND_test × δ_std × Baldwin_gap_h≥4 cross-product at budget=5 gridded; Baldwin_slope demoted to descriptive-only (never in row clauses) per P1-2.
- **Principle 27:** METRIC_DEFINITIONS inherited verbatim from §1a + new cell-level bootstrap CI entry added as part of infra extension.
- **Principle 28a/b/c:** row clauses are conjunctions of all sub-clauses (28a); guards cover multi-failure-mode cases with explicit bundles (28b); status-line inline qualifier discipline at chronicle time (28c).
- **Principle 29:** this prereg follows the pre-committed diagnosis doc; escalation path restricted to the doc's ladder. No §29 methodology amendment pre-committed (P1-4 fix).

## METRIC_DEFINITIONS extensions (principle 27 — verbatim; v3 per NEW-P2)

The following entries will be added verbatim to `experiments/chem_tape/analyze_plasticity.py:METRIC_DEFINITIONS` by Status-transition checklist item 1 before the sweep launches. These are the §27 pre-commitments the v3 confirmatory test depends on:

```python
"max_gap_at_budget_5": (
    "Per-seed maximum of Baldwin_gap across Hamming bins h in {2, 3, >=4} "
    "at plasticity_budget=5. Computed as max(Baldwin_gap_h2, Baldwin_gap_h3, "
    "Baldwin_gap_h_ge4) per seed for non-GT-bypass individuals only. "
    "Broader than §1a's Baldwin_gap_h_ge4 metric to handle the case where "
    "positive plastic uplift concentrates in h=2 or h=3 rather than h>=4 "
    "(expected at sf=0.0 where the Hamming-to-canonical distribution is "
    "shifted relative to sf=0.01)."
),
"max_gap_at_budget_5_cell_boot_ci": (
    "Seed-level nonparametric bootstrap 95% CI on the per-cell mean of "
    "max_gap_at_budget_5: 10 000 resamples with replacement over the "
    "20 per-seed values via numpy.random.default_rng(seed=42); CI is the "
    "[2.5%, 97.5%] empirical quantile of the resampled means. Matches "
    "bootstrap_ci_spec. Distinct from the existing Baldwin_slope_ci95 "
    "columns, which bootstrap intra-population over individuals and cannot "
    "support cell-level row-match clauses."
),
"max_gap_at_budget_5_seed_majority": (
    "Count of seeds (out of 20 in the cell) with per-seed "
    "max_gap_at_budget_5 > 0.10. Part of §v2.5-plasticity-2a's row-3 "
    "dual criterion: cell-bootstrap CI_lo >= 0.10 AND this count >= 10. "
    "Sidesteps v2's incorrect 'CI_lo >= 0.10 implies seed-majority-positive' "
    "equivalence claim — cell-mean CI and per-seed majority are distinct "
    "statistical statements that must both hold for the row."
),
"R_fit_delta_paired_sf0": (
    "Per-seed paired difference R_fit_plastic_999 - R_fit_frozen_999 at "
    "sf=0.0, where R_fit_frozen_999 is taken from the frozen control cell "
    "at the matching seed in the same sweep (NOT from the plastic run's "
    "own final_population frozen evaluation, which would compare plastic "
    "and frozen evaluation on the same evolved population rather than "
    "comparing the plastic cell's final population to the frozen control's "
    "final population). Requires cross-cell merge between the plastic "
    "cells and the frozen control cell on shared seeds 20..39. Used as "
    "§v2.5-plasticity-2a's secondary diagnostic."
),
"initial_population_canonical_count": (
    "Count of individuals in the generation-0 population whose tape "
    "byte-for-byte matches any of the cfg.seed_tapes_hex entries. Emitted "
    "per-run to history.npz as a scalar at generation-0 population build "
    "time. At sf=0.0 with seed_tapes=None, the expected value is 0 for "
    "every seed; any nonzero count flags an infrastructure bug in "
    "build_initial_population."
),
```

## Status-transition checklist (QUEUED → RUNNING — v3 per NEW-P2 infra-scope correction)

Before this prereg can move from QUEUED to RUNNING:

1. **`analyze_plasticity.py` extensions (~90 min total; up from v2's ~45 min after codex-v2 review flagged under-scoping):**
   - (a) Modify `analyze_run` to ALSO process frozen-only runs (currently returns None when `delta_final` column is missing from `final_population.npz`). Frozen runs have `genotypes` + `fitnesses` arrays only; emit `R_fit_frozen_999` and the minimum diagnostic fields needed for the cross-cell merge. ~20 min.
   - (b) Add `max_gap_at_budget_5` per-seed computation in `analyze_run` (max across existing `Baldwin_gap_h{2,3,_ge4}` keys; reported per-run via `plasticity.csv`). ~10 min.
   - (c) Add cell-level seed-bootstrap CI on `max_gap_at_budget_5` in `summarize` (10 000 resamples, rng seed 42). ~15 min.
   - (d) Add `max_gap_at_budget_5_seed_majority` count in `summarize`. ~5 min.
   - (e) Add cross-cell merge for `R_fit_delta_paired_sf0`: join plastic-cell per-seed `R_fit_plastic_999` with frozen-control per-seed `R_fit_frozen_999` on (arm, seed) and emit the paired delta per-cell. Current `analyze_run` emits per-run `R_fit_delta_999` within the same run's population — this is a NEW code path. ~30 min.
   - (f) Add the 5 METRIC_DEFINITIONS entries verbatim from the block above. ~10 min.
2. **`run.py` / `evolve.py` instrumentation (~20 min):** add `initial_population_canonical_count` to `history.npz` as a scalar computed in `build_initial_population` (compare each gen-0 tape byte-for-byte against `cfg.seed_tapes_hex` entries if set, else emit 0). NEW — `history.npz` does not currently track this field; grep-verified at codex-v2 review time.
3. **Pytest assertion (~20 min):** `sf=0.0 AND seed_tapes=None → initial_population_canonical_count == 0` in `tests/test_chem_tape_seeded_init.py` (extend existing sf-related tests).
4. **Sweep YAML:** `experiments/chem_tape/sweeps/v2/v2_5_plasticity_2a.yaml` — 4 plastic cells × 20 seeds (seeds 20..39) + 1 frozen control × 20 seeds = 100 runs. Paired-seed structure required for the secondary R_fit diagnostic.
5. **Queue entry:** add to `queue.yaml` with 90-min timeout (conservative headroom over projected 30-60 min).
6. **Pin target commit SHA** in Status line above.
7. **Codex adversarial review of v3** — focused on whether the broadened `max_gap` metric actually captures INVERSE-BALDWIN signal robustly, whether the dual CI + per-seed-majority criterion is defensible, and whether row 1's F-RECOVERY-WITHOUT-INVERSE-SIGNATURE renaming is clean (not just rhetorical).

**Total engineering effort:** ≈ 2-2.5 h (up from v2's ~65 min); v2's estimate was flagged by codex as understating the frozen-run-handling and `history.npz` instrumentation scope.

## References

- `Plans/prereg_v2-5-plasticity-1a.md` — primary predecessor prereg.
- `docs/chem-tape/experiments-v2.md#v2.5-plasticity-1a` — INVERSE-BALDWIN chronicle (grid-miss verdict, §29 class-4 diagnosis).
- `Plans/diagnosis_v2-5-plasticity-1a_2026-04-19.md` — diagnosis doc this prereg enacts P-1 for.
- `docs/methodology.md` — §§1, 2, 2b, 4, 6, 16c, 17a, 17b, 20, 22, 22a, 22b, 23, 25, 26, 27, 28a/b/c, 29.
- `experiments/chem_tape/analyze_plasticity.py` — METRIC_DEFINITIONS source.
- `docs/chem-tape/runtime-plasticity-direction.md` — direction doc (rank-1 → rank-2 ladder).
- Risi, S. & Stanley, K. O. (2010). "Evolving Plastic Neural Networks with Novelty Search." *Adaptive Behavior* 18(6), 470-491 — literature anchor for class-4 `selection-deception`.
- Prior commits: `9ff9bf8` — v1 of this prereg; `f6ead25` — v2 amendment (superseded by this v3; reasoning trail preserved in git history per §13 spirit).
